from mock import Mock
from unittest.mock import patch
import pytest

from rrdraw import GraphDrawer
from rrdraw import GraphTimeScale
from rrdraw.exceptions import *

def test_draw_init():
	gd = GraphDrawer()

	assert gd.height == 100
	assert gd.width == 300

	gd.height = 300
	assert gd.height == 300

	gd.width = 768
	assert gd.width == 768

def test_draw_config():
	gd = GraphDrawer({
		'global': {
			'width': 247,
			'height': 316,
			'outdir': '/path/to/graphs',
			'timezone': 'Australia/Melbourne'
		}
	})

	assert gd.width == 247
	assert gd.height == 316
	assert gd.outdir == '/path/to/graphs'

	gd = GraphDrawer({
		'global': {
			'outdir': '/another/path',
		}
	})
	assert gd.width == 300
	assert gd.height == 100
	assert gd.outdir == '/another/path'

def test_draw_all():
	gd = GraphDrawer({
		'times': [
			{
				'name': '1h',
				'title': 'One Hour',
				'start': 'end-1h',
				'end': 'now',
			}
		]
	})

	gd.draw_one = Mock()
	graph = Mock()

	assert len(gd._timescales) == 1
	ts = gd._timescales[0]
	assert ts.name == '1h'
	assert ts.end == 'now'

	gd.draw_all(graph)

	gd.draw_one.assert_called_with(graph, gd._timescales[0])

@patch('rrdtool.graph')
def test_draw_one(MockRRDGraph):
	gd = GraphDrawer()
	graph = {
		'prefix': 'test_run',
		'title': 'Test graph',
		'lines': [
			{
				'legend': 'Test Line',
				'type': 'line1',
				'color': "#00ff00",
				'source': "/path/to/data.rrd",
				'source_ds': 'test_value',
				'source_cf': 'AVERAGE',
				'units': "%Sbps",
			}
		]
	}
	ts = GraphTimeScale({
		'name': '4h',
		'title': 'Last Four Hours',
		'start': 'now-4h',
	})

	gd.draw_one(graph, ts)
	MockRRDGraph.assert_called()
	assert "'--vertical-label'" not in str(MockRRDGraph.call_args_list[0])
	assert "'--right-axis-label'" not in str(MockRRDGraph.call_args_list[0])
	assert "'--right-axis'" not in str(MockRRDGraph.call_args_list[0])

	# Test the axis options.
	MockRRDGraph.reset_mock()
	graph['left_axis'] = 'This is the left axis.'
	graph['right_axis'] = 'And this be the right one.'
	graph['right_axis_scale'] = '0.00005:0'

	gd.draw_one(graph, ts)
	MockRRDGraph.assert_called()
	assert "'--vertical-label', 'This is the left axis.'" in str(MockRRDGraph.call_args_list[0])
	assert "'--right-axis-label', 'And this be the right one.'" in str(MockRRDGraph.call_args_list[0])
	assert "'--right-axis', '0.00005:0'" in str(MockRRDGraph.call_args_list[0])

def test_draw_one_no_prefix():
	gd = GraphDrawer()
	graph = {
		'title': 'Test graph',
	}

	with pytest.raises(InvalidPrefixGraph) as exc:
		gd.draw_one(graph, None)

	assert '`graph` without a `prefix`' in str(exc)

def test_draw_one_no_lines():
	gd = GraphDrawer()
	ts = GraphTimeScale({
		'name': '4h',
		'title': 'Last Four Hours',
		'start': 'now-4h',
	})

	# Empty line list? That's a paddlin'.
	graph = {
		'prefix': 'test_run',
		'title': 'Test graph',
		'lines': []
	}
	with pytest.raises(NoLinesInGraph) as exc:
		gd.draw_one(graph, ts)

	# Check it fails correctly if there's no lines at all.
	graph = {
		'prefix': 'test_run',
		'title': 'Test graph',
	}

	with pytest.raises(NoLinesInGraph) as exc:
		gd.draw_one(graph, ts)

	assert 'entry in `graph` \'test_run' in str(exc)

	# It's pretty easy in YAML to accidentally a dict when you mean a
	# list, so let's check for that too.
	# Empty line list? That's a paddlin'.
	graph = {
		'prefix': 'test_run',
		'title': 'Test graph',
		'lines': {'hi': 'bye'},
	}
	with pytest.raises(NoLinesInGraph) as exc:
		gd.draw_one(graph, ts)

	assert 'entry for `graph` \'test_run\' is not an array' in str(exc)
