all:
	@coverage run --source rrdraw -m pytest tests/
	@coverage report -m
