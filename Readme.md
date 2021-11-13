# rrdraw - draw lots of rrdtool graphs in a completely silly manner.

I had to draw enough graphs in rrdtool where doing it all with bash was
getting to be a pain, but not so many that warranted setting up cacti or
similar instead.

So we'll use a YAML file (because I don't have enough problems) to
describe a list of graphs (as "time scales"), and then a list of data,
and then we'll draw a graph file for each combination of the two.

The YAML for the most part resembles a more human-readable version of the
rrdtool arguments. They mostly work the same.

## Features

- It can draw graphs.

## Bugs/TODO

- Completely intolerant of missing fields... it should guess.
- Color semi-randomization
- Multi-axis graphs
- The "units" field must be the same length or things will get screwy
  (you can prepend shorter ones with spaces for now).
