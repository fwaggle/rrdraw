from pprint import pprint

import os
import rrdtool
import yaml

class GraphDrawer():
    def __init__(self, config):
        self.height = int(config['global']['height'])
        self.width = int(config['global']['width'])
        self.outdir = config['global']['outdir']

        self.timescales = []
        for ts in config['times']:
            self.timescales.append(ts)

    def draw_all(self, graph):
        for ts in self.timescales:
            self.draw_one(graph, ts)

    def draw_one(self, graph, ts):
        output = os.path.join(self.outdir, graph['prefix'] + '_' + ts['name'] + '.png')
        args = []

        if 'left_axis' in graph:
            args.append('--vertical-label')
            args.append(graph['left_axis'])

        # Figure out the longest legend.
        legend_size = 0
        for line in graph['lines']:
            if len(line['legend']) > legend_size:
                legend_size = len(line['legend'])

        args.append('COMMENT:%s         ' % (' ' * legend_size))
        args.append('COMMENT:Minimum        ')
        args.append('COMMENT:Average        ')
        args.append('COMMENT:Maximum        ')
        args.append('COMMENT:Last\\n')

        # Now generate the graph args for each data point.
        last = None
        for line in graph['lines']:
            last = line

            # Generate the data definition
            args.append("DEF:%s=%s:%s:%s" % (
                line['source_ds'],
                line['source'],
                line['source_ds'],
                line['source_cf'],
            ))

            # And figure out the min/max/last
            args.append("VDEF:%s_min=%s,MINIMUM" % (
                line['source_ds'],
                line['source_ds'],
            ))
            args.append("VDEF:%s_avg=%s,AVERAGE" % (
                line['source_ds'],
                line['source_ds'],
            ))
            args.append("VDEF:%s_max=%s,MAXIMUM" % (
                line['source_ds'],
                line['source_ds'],
            ))
            args.append("VDEF:%s_last=%s,LAST" % (
                line['source_ds'],
                line['source_ds'],
            ))


            padding_len = legend_size - len(line['legend'])
            padding = ' ' * padding_len

            # Generate the actual line.
            args.append("%s:%s%s:%s%s" % (
                line['type'].upper(),
                line['source_ds'],
                line['color'],
                line['legend'],
                padding,
            ))

            args.append("GPRINT:%s_min:%%12.0lf%s" % (
                line['source_ds'],
                line['units'],
            ))
            args.append("GPRINT:%s_avg:%%12.0lf%s" % (
                line['source_ds'],
                line['units'],
            ))
            args.append("GPRINT:%s_max:%%12.0lf%s" % (
                line['source_ds'],
                line['units'],
            ))
            args.append("GPRINT:%s_last:%%12.0lf%s\\n" % (
                line['source_ds'],
                line['units'],
            ))

        args.append("GPRINT:%s_last:                                          Ending at %%H\\:%%M on %%B %%d, %%Y\\r:strftime" % last['source_ds'])

        rrdtool.graph(output,
            "--disable-rrdtool-tag",
            "--start", ts['start'],
            "--width", str(self.width),
            "--height", str(self.height),
            "--border", "0",
            "--title", "%s - %s" % (graph['title'], ts['title']),
            args
            )

def main():
    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    
    draw = GraphDrawer(config)

    for g in config['graphs']:
        draw.draw_all(g)

if __name__ == "__main__":
    main()
