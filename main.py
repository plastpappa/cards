import sys
from yaml import load, Loader

from pyglet import font
from pyglet.window import Window

from international import FONT_DIR
from draw.vector import Vector

import main_play
import main_train


def main(type):
    config = load(open('config.yaml', 'r'), Loader = Loader)
    font.add_directory(FONT_DIR)

    WINDOW_SIZE = Vector(*(config['window']['size']))
    window = Window(WINDOW_SIZE.x, WINDOW_SIZE.y, caption = config['window']['title'])

    if type == 'play':
        main_play.main(config, window, WINDOW_SIZE)
    elif type == 'train':
        main_train.main(config, window, WINDOW_SIZE)
    else:
        raise ValueError(f'Invalid argument "type": should be "play" or "train", got "{type}"')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError('Please provide a command-line argument specifying whether to play or train')
    main(sys.argv[1])
