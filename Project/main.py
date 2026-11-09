from pico2d import clear_canvas, close_canvas, delay, get_events, open_canvas, update_canvas
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_SPACE

import game_world
import camera
from background import Background
from building import Building
from mine_entrance import MineEntrance
from mine_merchant import MineMerchant
from player import Player
from hud import Hud


running = True


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(player.x - 1440) <= 100
        ):
            enter_mine()
        else:
            game_world.handle_event(event)


def update_world():
    game_world.update()
    camera.follow(player.x)


def reset_world():
    global background, player

    game_world.clear()
    camera.reset()
    background = Background()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    buildings = [
        Building("assets/buildings/house_exterior.png", 160),
        Building("assets/buildings/farm_exterior.png", 480),
        Building("assets/buildings/ranch_exterior.png", 800),
        Building("assets/buildings/buffet_exterior.png", 1120),
        Building("assets/buildings/mine_exterior.png", 1440),
    ]
    game_world.add_objects(buildings, depth=1)
    player = Player()
    game_world.add_object(player, depth=2)


def enter_mine():
    game_world.clear()
    background.use_mine_map()
    player.x = 64
    player.y = 150
    player.pressed_keys.clear()
    if player.state == "RUN":
        player.stop_running()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    entrances = (
        (486, "assets/ore/ore_stone.png", False),
        (786, "assets/ore/ore_coal.png", True),
        (1086, "assets/ore/ore_iron.png", True),
        (1396, "assets/ore/ore_gold.png", True),
    )
    for x, ore_path, locked in entrances:
        game_world.add_object(
            MineEntrance(x, 180, ore_path, locked),
            depth=1,
        )
    merchant = MineMerchant(300, 150)
    game_world.add_object(merchant, depth=1)
    game_world.add_object(player, depth=2)
    camera.reset()


def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()


if __name__ == "__main__":
    open_canvas()
    reset_world()
    enter_mine()
    try:
        while running:
            handle_events()
            update_world()
            render_world()
            delay(0.01)
    finally:
        close_canvas()