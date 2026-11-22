from pico2d import get_time

import farm


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
    "egg": 0,
    "milk": 0,
    "mushroom": 0,
    "chicken": 0,
    "beef": 0,
    "pork": 0,
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

# 목장: 구역별 동물 마릿수 (시작 닭 1마리 — 목장_PRD 3.7)
animal_counts = {"chicken": 1, "cow": 0, "pig": 0}

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


# 농사지 도구: 곡괭이 등급(작물별 수확량)과 비료(성장 시간 단축)
farm_tools = []
HOE_LEVELS = ("STONE HOE", "IRON HOE", "GOLD HOE")
# 곡괭이처럼 작물별 차등 (밀 → 감자 → 딸기 순으로 감소)
HOE_YIELDS = {
    "STONE HOE": {"wheat": 2},
    "IRON HOE": {"wheat": 3, "potato": 2},
    "GOLD HOE": {"wheat": 5, "potato": 3, "strawberry": 2},
}


def harvest_yield(crop):
    """기본 1개, 보유한 최고 등급 곡괭이의 해당 작물 수확량."""
    for hoe in reversed(HOE_LEVELS):
        if hoe in farm_tools and crop in HOE_YIELDS[hoe]:
            return HOE_YIELDS[hoe][crop]
    return 1


def crop_stage_seconds(base_seconds):
    """비료 보유 시 성장 단계 시간을 절반으로 단축."""
    if "FERTILIZER" in farm_tools:
        return base_seconds * 0.5
    return base_seconds


def apply_farm_work(crop, kind, index, now):
    """심기·수확 결과 적용 (농부/플레이어 공통). 성공 시 True.

    모션 종료 시점에 호출되므로 상태를 다시 검증한다.
    """
    key = (crop, index)
    stage_seconds = crop_stage_seconds(farm.STAGE_SECONDS)
    if kind == "harvest":
        slot = crop_slots.get(key)
        if slot is None:
            return False
        if farm.crop_stage(slot, now, stage_seconds) != farm.READY_STAGE:
            return False
        collected_items[crop] += harvest_yield(crop)
        slot["harvested_at"] = now
        return True
    slot = crop_slots.get(key)
    if slot is not None and farm.crop_stage(slot, now, stage_seconds) is not None:
        return False
    crop_slots[key] = {
        "planted_at": now,
        "harvested_at": None,
    }
    return True


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
