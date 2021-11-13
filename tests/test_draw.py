from rrdraw import GraphDrawer

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

def test_draw_times():
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
