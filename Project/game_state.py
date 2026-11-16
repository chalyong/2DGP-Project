from pico2d import get_time


money = 1000000
play_start_time = get_time()
collected_items = {
    "stone": 0,
    "coal": 0,
    "iron": 0,
    "gold": 0,
}
cooked_items = {}
tools = []
open_tunnels = {
    "stone": True,
    "coal": False,
    "iron": False,
    "gold": False,
}
miners = {
    "stone": 0,
    "coal": 0,
    "iron": 0,
    "gold": 0,
}

PICKAXE_ORDER = (
    "WOOD PICKAXE",
    "STONE PICKAXE",
    "IRON PICKAXE",
    "GOLD PICKAXE",
)
PICKAXE_YIELDS = {
    "WOOD PICKAXE": {"stone": 2},
    "STONE PICKAXE": {"stone": 3, "coal": 2},
    "IRON PICKAXE": {"stone": 5, "coal": 3, "iron": 2},
    "GOLD PICKAXE": {"stone": 10, "coal": 5, "iron": 3, "gold": 2},
}


def mining_yield(ore_name):
    for pickaxe in reversed(PICKAXE_ORDER):
        if pickaxe in tools:
            return PICKAXE_YIELDS[pickaxe].get(ore_name, 1)
    return 1
