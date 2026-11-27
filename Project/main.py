import os

# pico2d resolves asset paths relative to the current working directory.
# Keep the game runnable from the repo root, VSCode, or the Project folder.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from pico2d import clear_canvas, close_canvas, delay, get_events, load_music, open_canvas, update_canvas
import pico2d.pico2d as _pico2d_core  # 렌더러·윈도우 전역이 보관된 서브모듈
from sdl2 import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_F5,
    SDLK_F9,
    SDLK_SPACE,
    SDL_RenderClear,
    SDL_RenderSetLogicalSize,
    SDL_SetRenderDrawColor,
    SDL_SetWindowFullscreen,
    SDL_WINDOW_FULLSCREEN_DESKTOP,
)

import game_world
import game_state
import camera
import farm
import ranch
import buffet
import auto_npc
from background import Background
from props import (
    Breeder,
    Building,
    BuffetChef,
    BuffetExit,
    BuffetShopkeeper,
    DiningFurniture,
    FarmExit,
    FarmMerchant,
    KitchenDishes,
    MineExit,
    MineMerchant,
    RanchExit,
    RanchMerchant,
    TunnelExit,
)
from mine_entrance import MineEntrance
from tunnel_ore import TunnelOre
from auto_npc import Miner
from farm import FarmZone
from player import Player
from hud import Hud
from shop import (
    BUFFET_SHOP_PAGES,
    FARM_SELL_PAGES,
    FARM_SHOP_PAGES,
    RANCH_SELL_PAGES,
    RANCH_SHOP_PAGES,
    Shop,
)
from inventory import Inventory
from cook_menu import CookMenu
from save_menu import SaveMenu


running = True
in_mine = False
in_tunnel = False
in_farm = False
in_ranch = False
in_buffet = False
current_tunnel = None
save_menu = SaveMenu()

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


def reload_current_scene():
    """불러오기 후 현재 씬을 재구성한다 (상점·동물·작물 상태 반영)."""
    if in_tunnel:
        enter_tunnel(current_tunnel)
    elif in_mine:
        enter_mine()
    elif in_farm:
        enter_farm()
    elif in_ranch:
        enter_ranch()
    elif in_buffet:
        enter_buffet()
    else:
        reset_world()
    # 동물 카운트를 저장값에 맞춘다 (초과분 제거 + 부족분 배치)
    for animal in game_state.animal_counts:
        while auto_npc.count_animals(animal) > game_state.animal_counts[animal]:
            auto_npc.remove_animal(animal)
    auto_npc.ensure_animal_population()


# 저장 메뉴 로드 성공 시 현재 씬 재구성
save_menu.on_load = reload_current_scene


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            if save_menu.open:
                save_menu.close(player)
            else:
                running = False
        elif save_menu.open:
            save_menu.handle_event(event, player)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F5:
            ok, msg = game_state.save_game(1)
            print(msg)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F9:
            ok, msg = game_state.load_game(1)
            print(msg)
            if ok:
                reload_current_scene()
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
            and in_farm
            and abs(player.x - farm.EXIT[0]) <= 90
            and player.y >= farm.EXIT[1] - 140
        ):
            leave_farm()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and in_ranch
            and abs(player.x - ranch.EXIT[0]) <= 90
            and player.y >= ranch.EXIT[1] - 140
        ):
            leave_ranch()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and in_buffet
            and abs(player.x - buffet.EXIT[0]) <= 90
            and player.y <= buffet.EXIT[1] + 140
        ):
            leave_buffet()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and not in_mine
            and not in_farm
            and not in_ranch
            and not in_buffet
            and not in_tunnel
            and abs(player.x - 160) <= 50
        ):
            # 집 앞: 저장·불러오기 메뉴 (PRD 9단계)
            save_menu.open_menu(player)
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and not in_mine
            and not in_farm
            and not in_ranch
            and not in_buffet
            and abs(player.x - 480) <= 50
        ):
            enter_farm()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and not in_mine
            and not in_farm
            and not in_ranch
            and not in_buffet
            and abs(player.x - 800) <= 50
        ):
            enter_ranch()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and not in_mine
            and not in_buffet
            and abs(player.x - 1440) <= 50
        ):
            enter_mine()
        elif (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and not in_mine
            and not in_farm
            and not in_ranch
            and not in_buffet
            and abs(player.x - 1120) <= 50
        ):
            enter_buffet()
        else:
            game_world.handle_event(event)


def update_world():
    game_state.update_miner_income()
    auto_npc.update()
    previous_position = (player.x, player.y)
    game_world.update()
    if in_farm and _sprinkler_blocked(player.x, player.y):
        player.x, player.y = previous_position
    if in_ranch and ranch.fence_blocked(player.x, player.y):
        # 울타리 통과 불가 (하단 중앙 게이트만 허용)
        player.x, player.y = previous_position
    if in_buffet:
        # 입구가 설치된 y좌표보다 아래로 내려갈 수 없음 (뷔페_PRD 3.1 하단 입구)
        if player.y < buffet.EXIT[1]:
            player.y = buffet.EXIT[1]
        camera.follow_2d(player.x, player.y)
    elif in_farm or in_ranch:
        # 출구가 설치된 y좌표보다 위로 올라갈 수 없음
        exit_y = farm.EXIT[1] if in_farm else ranch.EXIT[1]
        if player.y > exit_y:
            player.y = exit_y
        camera.follow_2d(player.x, player.y)
    else:
        camera.follow(player.x)


def _sprinkler_blocked(x, y):
    return any(farm.is_sprinkler_hit(crop, x, y) for crop in farm.ZONES)


def reset_world():
    global background, player, inventory, in_mine, in_tunnel, in_farm, in_ranch, in_buffet

    in_mine = False
    in_tunnel = False
    in_farm = False
    in_ranch = False
    in_buffet = False
    game_world.clear()
    camera.restore_world()
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
                f"assets/item/ore_{ore_name}.png",
                ore_name,
            ),
            depth=1,
        )
    merchant = MineMerchant(320, 150)
    sell_merchant = MineMerchant(240, 150)
    game_world.add_object(merchant, depth=1)
    game_world.add_object(sell_merchant, depth=1)
    game_world.add_object(player, depth=2)
    game_world.add_object(Shop(player, merchant), depth=8)
    game_world.add_object(Shop(player, sell_merchant, mode="sell"), depth=8)
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
            f"assets/item/ore_{ore_name}.png",
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


def enter_farm():
    global in_farm

    in_farm = True
    game_world.clear()
    camera.reset()
    camera.set_world(farm.SIZE, farm.SIZE)
    background.use_farm_map()
    player.top_view = True
    player.x = farm.PLAYER_SPAWN[0]
    player.y = farm.PLAYER_SPAWN[1]
    player.pressed_keys.clear()
    if player.state == "RUN":
        player.stop_running()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    game_world.add_object(FarmExit(*farm.EXIT), depth=1)
    merchant = FarmMerchant(*farm.MERCHANT)
    game_world.add_object(merchant, depth=1)
    for crop in farm.ZONES:
        game_world.add_object(FarmZone(crop, player), depth=1)
    game_world.add_object(player, depth=2)
    game_world.add_object(
        Shop(player, merchant, pages=FARM_SHOP_PAGES, title="FARM SHOP"),
        depth=8,
    )
    sell_merchant = FarmMerchant(*farm.SELL_MERCHANT)
    game_world.add_object(sell_merchant, depth=1)
    game_world.add_object(
        Shop(
            player,
            sell_merchant,
            mode="sell",
            sell_rows=FARM_SELL_PAGES,
            title="FARM MARKET",
        ),
        depth=8,
    )
    game_world.add_object(Inventory(player), depth=8)


def leave_farm():
    reset_world()
    player.x = 480
    player.y = 300
    camera.follow(player.x)


def enter_ranch():
    global in_ranch

    in_ranch = True
    game_world.clear()
    camera.reset()
    camera.set_world(ranch.SIZE, ranch.SIZE)
    background.use_ranch_map()
    player.top_view = True
    player.x = ranch.PLAYER_SPAWN[0]
    player.y = ranch.PLAYER_SPAWN[1]
    player.pressed_keys.clear()
    if player.state == "RUN":
        player.stop_running()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    game_world.add_object(RanchExit(*ranch.EXIT), depth=1)
    merchant = RanchMerchant(*ranch.MERCHANT)
    game_world.add_object(merchant, depth=1)
    for animal in ranch.ZONES:
        game_world.add_object(ranch.RanchZone(animal, player), depth=1)
        game_world.add_object(
            Breeder(animal, *ranch.breeder_position(animal)), depth=1
        )
    game_world.add_object(player, depth=2)
    game_world.add_object(
        Shop(player, merchant, pages=RANCH_SHOP_PAGES, title="RANCH SHOP"),
        depth=8,
    )
    sell_merchant = RanchMerchant(*ranch.SELL_MERCHANT)
    game_world.add_object(sell_merchant, depth=1)
    game_world.add_object(
        Shop(
            player,
            sell_merchant,
            mode="sell",
            sell_rows=RANCH_SELL_PAGES,
            title="RANCH MARKET",
        ),
        depth=8,
    )
    game_world.add_object(Inventory(player), depth=8)


def leave_ranch():
    reset_world()
    player.x = 800
    player.y = 300
    camera.follow(player.x)


def enter_buffet():
    global in_buffet

    in_buffet = True
    game_world.clear()
    camera.reset()
    camera.set_world(buffet.SIZE, buffet.SIZE)
    background.use_buffet_map()
    player.top_view = True
    player.x = buffet.PLAYER_SPAWN[0]
    player.y = buffet.PLAYER_SPAWN[1]
    player.pressed_keys.clear()
    if player.state == "RUN":
        player.stop_running()
    game_world.add_object(background, depth=0)
    game_world.add_object(Hud(), depth=9)
    game_world.add_object(BuffetExit(*buffet.EXIT), depth=1)
    shopkeeper = BuffetShopkeeper(620, 540)  # 계산대 구역 (뷔페_PRD 3.1)
    game_world.add_object(shopkeeper, depth=1)
    chef = BuffetChef(350, 700)  # 주방 구역 (뷔페_PRD 3.1)
    game_world.add_object(chef, depth=1)
    game_world.add_object(KitchenDishes(), depth=1)
    game_world.add_object(DiningFurniture(), depth=1)
    game_world.add_object(player, depth=2)
    game_world.add_object(
        Shop(player, shopkeeper, pages=BUFFET_SHOP_PAGES, title="BUFFET SHOP"),
        depth=8,
    )
    game_world.add_object(CookMenu(player, chef), depth=8)
    game_world.add_object(Inventory(player), depth=8)


def leave_buffet():
    reset_world()
    player.x = 1120
    player.y = 300
    camera.follow(player.x)


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
    # clear 색 = 검정(0,0,0) — 전체화면 여백(letterbox)과 빈 영역 바탕색
    if _pico2d_core.renderer is not None:
        SDL_SetRenderDrawColor(_pico2d_core.renderer, 0, 0, 0, 255)
        SDL_RenderClear(_pico2d_core.renderer)
    else:
        clear_canvas()
    game_world.render()
    save_menu.draw()
    update_canvas()


# 배경음악 재생 유지용 참조 (참조 없으면 GC가 음악을 해제함)
background_music = None


def setup_logical_scale():
    """논리 좌표 800×600 유지 — 윈도우/전체화면 크기와 무관하게 스케일링.

    렌더러가 화면 크기에 맞춰 알아서 확대/축소하므로 물체 비율이 그대로 유지된다.
    """
    # pico2d의 렌더러는 서브모듈(pico2d.pico2d) 전역에 존재
    if _pico2d_core.renderer is not None:
        SDL_RenderSetLogicalSize(
            _pico2d_core.renderer, camera.SCREEN_WIDTH, camera.SCREEN_HEIGHT
        )


def setup_fullscreen():
    """데스크톱 전체화면으로 전환 (해상도 모드 변경 없음 — 현재 해상도 유지).

    해상도·종횡비와 무관하게 논리 800×600 스케일링이 적용된다.
    """
    if _pico2d_core.window is not None:
        SDL_SetWindowFullscreen(
            _pico2d_core.window, SDL_WINDOW_FULLSCREEN_DESKTOP
        )


def start_background_music():
    """main_music를 배경음악으로 무한 반복 재생 (오디오 불가 환경은 무시)."""
    global background_music
    try:
        background_music = load_music("assets/music/main_music.mp3")
        background_music.set_volume(48)
        background_music.repeat_play()
    except IOError:
        print("background music unavailable")


if __name__ == "__main__":
    open_canvas()
    setup_logical_scale()
    setup_fullscreen()
    start_background_music()
    reset_world()
    enter_buffet()
    try:
        while running:
            handle_events()
            update_world()
            render_world()
            delay(0.01)
    finally:
        close_canvas()
