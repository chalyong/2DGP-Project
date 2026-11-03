from pico2d import close_canvas, delay, get_events, open_canvas
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import game_world


running = True


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def update_world():
    game_world.update()


def render_world():
    # Rendering is intentionally empty during the initial window test.
    pass


if __name__ == "__main__":
    open_canvas()
    try:
        while running:
            handle_events()
            update_world()
            render_world()
            delay(0.01)
    finally:
        close_canvas()