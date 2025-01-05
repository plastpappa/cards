import sys

from pyglet import font
from pyglet.window import Window

from international import FONT_DIR
from draw.vector import Vector

import main_play


def get_default_players(num_players: int):
    return [ { 'name': f"Player {n+1}", 'type': 'human' } for n in range(num_players) ]

if __name__ == '__main__':
    args = sys.argv[1:]
    
    font.add_directory(FONT_DIR)

    WINDOW_SIZE = Vector(920, 640)
    window = Window(WINDOW_SIZE.x, WINDOW_SIZE.y, caption = 'Cards')

    if len(args) > 0:
        try:
            players = get_default_players(num_players = int(args[0]))
        except (IndexError, ValueError):
            players = [ { 'name': name, 'type': 'human' } for name in args ]
    else:
        players = get_default_players(num_players = 4)

    main_play.main(players, window, WINDOW_SIZE)