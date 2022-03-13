import os
import rrdtool
import time

import rrdraw.exceptions

class GraphTimeScale():
	def __init__(self, config={}):
		self.name = '24h'
		self.title = 'Last 24 Hours'
		self.end = 'now'
		self.start = 'now-86400'

		if 'name' in config:
			self.name = config['name']

		if 'title' in config:
			self.title = config['title']

		if 'start' in config:
			self.start = config['start']

		if 'end' in config:
			self.end = config['end']


class GraphDrawer():
	def __init__(self, config={}):
		# Sensible defaults?
		self._height = 100
		self._width = 300
		self._timescales = []
		self._outdir = '/tmp'

		# Suck in the global config
		if 'global' in config:
			g = config['global']

			if 'height' in g:
				self.height = g['height']

			if 'width' in g:
				self.width = g['width']

			if 'outdir' in g:
				self.outdir = g['outdir']

			if 'timezone' in g:
				os.environ['TZ'] = g['timezone']
				time.tzset()

		# Parse the provided timescales, or use our own
		# TODO: Use our own, for now do nothing.
		if 'times' in config:
			for ts in config['times']:
				self._timescales.append(GraphTimeScale(ts))

	@property
	def height(self):
		return self._height
	@height.setter
	def height(self, value):
		self._height = int(value)

	@property
	def width(self):
		return self._width
	@width.setter
	def width(self, value):
		self._width = int(value)

	@property
	def outdir(self):
		return self._outdir
	@outdir.setter
	def outdir(self, value):
		self._outdir = value

	def draw_all(self, graph):
		for ts in self._timescales:
			self.draw_one(graph, ts)

	def draw_one(self, graph, ts):
		if 'prefix' not in graph:
			raise rrdraw.exceptions.InvalidPrefixGraph("There's a `graph` without a `prefix` property.")

		output = os.path.join(self.outdir, graph['prefix'] + '-' + ts.name + '.png')
		args = []

		field_width = 12

		if 'field_width' in graph:
			field_width = graph['field_width']

		if 'left_axis' in graph:
			args.append('--vertical-label')
			args.append(graph['left_axis'])

		if 'right_axis' in graph:
			args.append('--right-axis-label')
			args.append(graph['right_axis'])

		if 'right_axis_scale' in graph:
			args.append('--right-axis')
			args.append(graph['right_axis_scale'])

		if 'lines' not in graph:
			raise rrdraw.exceptions.NoLinesInGraph("You don't appear to have a `lines` entry in `graph` '%s'" % graph['prefix'])

		if type(graph['lines']) is not list:
			raise rrdraw.exceptions.NoLinesInGraph("The `lines` entry for `graph` '%s' is not an array." % graph['prefix'])

		if len(graph['lines']) < 1:
			raise rrdraw.exceptions.NoLinesInGraph("zero")

		# Figure out the longest legend.
		legend_size = 0
		unit_size = 0
		for line in graph['lines']:
			current = 0
			current_units = 0
			if line['legend'] and len(line['legend']) > 0:
				current = len(line['legend'])
			if line['units'] and len(line['units']) > 0:
				current_units += len(line['units'])
				if '%' in line['units']:
					current_units -= 1

			current += current_units

			if current > legend_size:
				legend_size = current

			if current_units > unit_size:
				unit_size = current_units

		args.append('COMMENT:%s  %s' % (' ' * legend_size, ' ' * unit_size))
		args.append('COMMENT:%sMinimum%s' % (' ' * (field_width - len('Minimum')), ' ' * unit_size))
		args.append('COMMENT:%sAverage%s' % (' ' * (field_width - len('Average')), ' ' * unit_size))
		args.append('COMMENT:%sMaximum%s' % (' ' * (field_width - len('Maximum')), ' ' * unit_size))
		args.append('COMMENT:%sLast\\n' % (' ' * (field_width - len('Last'))))

		# Now generate the graph args for each data point.
		last = None
		for line in graph['lines']:
			last = line

			# Figure out what to call it.
			id = line['source_ds']
			if 'id' in line:
				id = line['id']

			# Generate the data definition
			args.append("DEF:%s=%s:%s:%s" % (
				id,
				line['source'],
				line['source_ds'],
				line['source_cf'],
			))

			if 'shift' in line:
				args.append("SHIFT:%s:%s" % (id, line['shift']))

			if 'multiply' in line:
				args.append("CDEF:%s_fixed=%s,%s,*" % (
					id,
					id,
					line['multiply'],
				))
			# And figure out the min/max/last
			args.append("VDEF:%s_min=%s,MINIMUM" % (
				id,
				id,
			))
			args.append("VDEF:%s_avg=%s,AVERAGE" % (
				id,
				id,
			))
			args.append("VDEF:%s_max=%s,MAXIMUM" % (
				id,
				id,
			))
			args.append("VDEF:%s_last=%s,LAST" % (
				id,
				id,
			))

			if not line['legend']:
				padding_len = 0
			else:
				padding_len = legend_size - len(line['legend'])
			padding = ' ' * padding_len

			# Generate the actual line.
			mult = ''
			if 'multiply' in line:
				mult = '_fixed'

			stack = ''
			if 'stack' in line and line['stack']:
				stack += ':STACK'

			if 'skipscale' in line and line['skipscale']:
				stack += ':skipscale'

			if not line['legend']:
				args.append("%s:%s%s%s%s" % (
					line['type'].upper(),
					id,
					mult,
					line['color'],
					stack,
				))

			else:
				args.append("%s:%s%s%s:%s%s%s" % (
					line['type'].upper(),
					id,
					mult,
					line['color'],
					line['legend'],
					padding,
					stack,
				))

				args.append("GPRINT:%s_min:%%%d.0lf%s" % (
					id,
					field_width,
					line['units'],
				))
				args.append("GPRINT:%s_avg:%%%d.0lf%s" % (
					id,
					field_width,
					line['units'],
				))
				args.append("GPRINT:%s_max:%%%d.0lf%s" % (
					id,
					field_width,
					line['units'],
				))
				args.append("GPRINT:%s_last:%%%d.0lf%s\\n" % (
					id,
					field_width,
					line['units'],
				))

		if 'hrules' in graph:
			if type(graph['hrules']) is list:
				for (rule) in graph['hrules']:
					if 'position' not in rule or 'color' not in rule:
						continue
					rule_legend = ''
					if 'legend' in rule:
						rule_legend = ':%s\\n' % rule['legend']
					args.append('HRULE:%s%s%s' % (rule['position'], rule['color'], rule_legend))

		args.append("GPRINT:%s_last:										  Ending at %%H\\:%%M on %%B %%d, %%Y\\r:strftime" % id)

		rrdtool.graph(output,
			"--slope-mode",
			"--disable-rrdtool-tag",
			"--start", ts.start,
			"--end", ts.end,
			"--width", str(self.width),
			"--height", str(self.height),
			"--border", "0",
			"--title", "%s - %s" % (graph['title'], ts.title),
			args
			)
