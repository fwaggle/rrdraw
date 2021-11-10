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
        for line in graph['lines']:
            args.append("DEF:%s=%s:%s:%s" % (
                line['source_ds'],
                line['source'],
                line['source_ds'],
                line['source_cf'],
            ))
            args.append("%s:%s%s:%s" % (
                line['type'].upper(),
                line['source_ds'],
                line['color'],
                line['legend'],
            ))
        # print(args)
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
