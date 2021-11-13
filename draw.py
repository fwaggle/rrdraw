from rrdraw import GraphDrawer
from rrdraw.exceptions import FatalException

import yaml

def main():
    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    
    try:
        draw = GraphDrawer(config)

        for g in config['graphs']:
            draw.draw_all(g)
    except FatalException as exc:
        print("Error:")
        print(str(exc))

if __name__ == "__main__":
    main()
