from pico2d import clear_canvas, close_canvas, delay, get_events, open_canvas, update_canvas
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import game_world
from background import Background
from player import Player


running = True


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            game_world.handle_event(event)


def update_world():
    game_world.update()


def reset_world():
    game_world.clear()
    background = Background()
    game_world.add_object(background, depth=0)
    player = Player()
    game_world.add_object(player, depth=1)


def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()


if __name__ == "__main__":
    open_canvas()
    reset_world()
    try:
        while running:
            handle_events()
            update_world()
            render_world()
            delay(0.01)
    finally:
        close_canvas()