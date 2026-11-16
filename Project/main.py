from pico2d import clear_canvas, close_canvas, delay, get_events, open_canvas, update_canvas
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_SPACE

import game_world
import game_state
import camera
from background import Background
from building import Building
from mine_entrance import MineEntrance
from mine_merchant import MineMerchant
from mine_exit import MineExit
from tunnel_exit import TunnelExit
from tunnel_ore import TunnelOre
from miner import Miner
from player import Player
from hud import Hud
from shop import Shop
from inventory import Inventory


running = True
in_mine = False
in_tunnel = False
current_tunnel = None

ENTRANCES = (
    (486, "stone"),
    (786, "coal"),
    (1086, "iron"),
    (1396, "gold"),
)
ENTRANCE_X = dict((ore_name, x) for x, ore_name in ENTRANCES)

# purchased miners: fixed slots centered on the tunnel, x grows per purchase
MINER_SLOT_SPACING = 60
MINER_SLOT_CENTER_X = 800
MINER_SLOT_Y = 150


def miner_slot_x(index):
    return MINER_SLOT_CENTER_X + (index - 4.5) * MINER_SLOT_SPACING


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif inventory.open:
            game_world.handle_event(event)
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and in_tunnel
            and abs(player.x - 64) <= 50
            and abs(player.y - 150) <= 80
        ):
            leave_tunnel()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and in_mine
            and not in_tunnel
            and abs(player.x - 64) <= 50
            and abs(player.y - 150) <= 80
        ):
            leave_mine()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and in_mine
            and not in_tunnel
        ):
            for x, ore_name in ENTRANCES:
                if (
                    game_state.open_tunnels[ore_name]
                    and abs(player.x - x) <= 50
                    and abs(player.y - 180) <= 80
                ):
                    enter_tunnel(ore_name)
                    break
            else:
                game_world.handle_event(event)
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and not in_mine
            and abs(player.x - 1440) <= 50
        ):
            enter_mine()
        else:
            game_world.handle_event(event)


def update_world():
    game_state.update_miner_income()
    game_world.update()
    camera.follow(player.x)


def reset_world():
    global background, player, inventory, in_mine, in_tunnel

    in_mine = False
    in_tunnel = False
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
    inventory = Inventory(player)
    game_world.add_object(inventory, depth=8)


def enter_mine():
    global in_mine, in_tunnel

    in_mine = True
    in_tunnel = False
    game_world.clear()
    background.use_mine_map()
    player.x = 64
    player.y = 150
    player.pressed_keys.clear()
    if player.state == "RUN":
        player.stop_running()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    game_world.add_object(MineExit(64, 150), depth=1)
    for x, ore_name in ENTRANCES:
        game_world.add_object(
            MineEntrance(
                x,
                180,
                f"assets/ore/ore_{ore_name}.png",
                ore_name,
            ),
            depth=1,
        )
    merchant = MineMerchant(300, 150)
    game_world.add_object(merchant, depth=1)
    game_world.add_object(player, depth=2)
    game_world.add_object(Shop(player, merchant), depth=8)
    game_world.add_object(Inventory(player), depth=8)
    camera.reset()


def enter_tunnel(ore_name):
    global in_tunnel, current_tunnel

    in_tunnel = True
    current_tunnel = ore_name
    game_world.clear()
    background.use_tunnel_map()
    player.x = 64
    player.y = 150
    player.pressed_keys.clear()
    if player.state == "RUN":
        player.stop_running()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    game_world.add_object(TunnelExit(64, 150), depth=1)
    game_world.add_object(
        TunnelOre(
            800,
            350,
            f"assets/ore/ore_{ore_name}.png",
            player,
            ore_name,
        ),
        depth=1,
    )
    for index in range(game_state.miners[ore_name]):
        game_world.add_object(
            Miner(miner_slot_x(index), MINER_SLOT_Y, ore_name),
            depth=1,
        )
    game_world.add_object(player, depth=2)
    game_world.add_object(Inventory(player), depth=8)
    camera.reset()


def leave_tunnel():
    global current_tunnel

    entrance_x = ENTRANCE_X[current_tunnel]
    current_tunnel = None
    enter_mine()
    player.x = entrance_x
    player.y = 150
    camera.follow(player.x)


def leave_mine():
    reset_world()
    player.x = 1440
    player.y = 300
    camera.follow(player.x)


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