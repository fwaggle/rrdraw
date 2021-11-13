from rrdraw import GraphTimeScale

def test_timescale_init():
	ts = GraphTimeScale()

def test_timescale_config():
	ts = GraphTimeScale({
		'name': '1h',
		'title': 'Last Hour',
		'start': 'now-3600',
	})

	assert ts.name == '1h'
	assert ts.title == 'Last Hour'
	assert ts.end == 'now'
	assert ts.start == 'now-3600'
