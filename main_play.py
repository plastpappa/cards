import pyglet

from card import *
from card.games.sjuan import *
from draw.games.sjuan import *
from draw.draw import *
from draw.manage import *
from draw.vector import Vector


def main(config, window, WINDOW_SIZE):
    cards_grouped = [ [
        Card(suit, value) for value in CardValue
        if ((value.adj_value(aces_lowest = True) - 7) * dir > 0
            or dir == 1 and value == CardValue.SEVEN)
    ] for suit in CardSuit for dir in (1, -1) ]

    sjuan = Sjuan(config['game']['players'], RectangleShape(
        bottom_left = Vector(0, 0), size = WINDOW_SIZE
    ), cards_grouped = cards_grouped)

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

    pyglet.clock.schedule_interval(update, 1 / config['window']['fps'])
    pyglet.app.run()
