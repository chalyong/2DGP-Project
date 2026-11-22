from pico2d import get_time


money = 1000000
play_start_time = get_time()
collected_items = {
    "stone": 0,
    "coal": 0,
    "iron": 0,
    "gold": 0,
    "wheat": 0,
    "potato": 0,
    "strawberry": 0,
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
passes = []

# 농사지: 구역 해금 상태와 심은 작물
# crop_slots 키: (작물, 칸 인덱스) -> 심은 시각(get_time())
farm_unlocked = {
    "wheat": True,
    "potato": False,
    "strawberry": False,
}
crop_slots = {}

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


# passive income: every MINER_CYCLE_SECONDS each purchased miner yields 1 ore,
# whether or not the player is inside the tunnel
MINER_CYCLE_SECONDS = 2.0
miner_cycle_count = 0
_miner_cycle_last = get_time()


def update_miner_income():
    global miner_cycle_count, _miner_cycle_last

    current_time = get_time()
    while current_time - _miner_cycle_last >= MINER_CYCLE_SECONDS:
        _miner_cycle_last += MINER_CYCLE_SECONDS
        miner_cycle_count += 1
        for ore_name, count in miners.items():
            if count:
                collected_items[ore_name] += count
