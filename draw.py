from rrdraw import GraphDrawer

import yaml

def main():
    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    
    draw = GraphDrawer(config)

    for g in config['graphs']:
        draw.draw_all(g)

if __name__ == "__main__":
    main()
