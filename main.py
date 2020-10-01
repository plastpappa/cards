from itertools import islice

import pyglet
from pyglet import font
from pyglet.window import Window

from international import FONT_DIR
from card import *
from card.games.sjuan import *
from draw.games.sjuan import *
from draw.draw import *
from draw.manage import *
from draw.vector import Vector


game = SjuanGame(num_players = 2)
    
def main():
    font.add_directory(FONT_DIR)
                
    FPS         = 60
    WINDOW_SIZE = Vector(920, 760)
    
    window = Window(WINDOW_SIZE.x, WINDOW_SIZE.y, caption = "Kort!!!")
    
    sjuan = Sjuan(game, RectangleShape(
        bottom_left = Vector(0, 0), size = WINDOW_SIZE
    ))
    
    @window.event
    def on_draw():
        window.clear()
        sjuan._world.draw()
        
    @window.event
    def on_mouse_motion(*args):
        sjuan._world.mouse_at(*args)

    @window.event
    def on_mouse_drag(*args):
        sjuan._world.mouse_at(*args)
    
    @window.event
    def on_mouse_press(*args):
        sjuan._world.mouse_down(*args)

    @window.event
    def on_mouse_release(*args):
        sjuan._world.mouse_up(*args)
        
    @window.event
    def on_mouse_scroll(*args):
        sjuan._world.mouse_scroll(*args)
        
    def update(dt):
        pass

    pyglet.clock.schedule_interval(update, 1 / FPS)
    pyglet.app.run()


if __name__ == '__main__':
    main()
