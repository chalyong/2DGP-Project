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

# 요리 레시피 (PRD 6단계 — 뷔페 이전 인벤토리 제작 경로)
# 각 재료 그룹은 "그룹 중 하나"를 1개 소비: (요리명, ((소비그룹1), (소비그룹2), ...))
RECIPES = (
    ("FRENCH FRIES", (("potato",),)),
    ("EGG BREAD", (("wheat",), ("egg",))),
    ("BERRY DESSERT", (("strawberry",), ("milk",))),
    ("MUSHROOM SOUP", (("mushroom",), ("milk",))),
    ("STEAK", (("chicken", "beef", "pork"), ("potato",))),
)


def consume_ingredients(name, count=1):
    """요리 재료 count회분 소비. 전량 검증 후 소비만 하고 요리는 지급하지 않음."""
    if count <= 0:
        return False, "INVALID COUNT"
    for recipe_name, groups in RECIPES:
        if recipe_name != name:
            continue
        for group in groups:
            available = sum(collected_items.get(key, 0) for key in group)
            if available < count:
                return False, f"NEED {group[0].upper()}"
        for group in groups:
            remaining = count
            for key in group:
                take = min(collected_items.get(key, 0), remaining)
                collected_items[key] -= take
                remaining -= take
                if remaining == 0:
                    break
        return True, f"CONSUMED {name} x{count}"
    return False, "UNKNOWN RECIPE"


def award_dish(name, count=1):
    """리듬게임 성공분만큼 완성 요리 지급."""
    cooked_items[name] = cooked_items.get(name, 0) + count


def cook(name, count=1):
    """요리 제작 count회 (임시 COOKING 탭용): 소비 + 지급."""
    ok, message = consume_ingredients(name, count)
    if not ok:
        return False, message
    award_dish(name, count)
    return True, f"COOKED {name} x{count}"
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
# 구역별 마지막 자원 획득 시각 (2분 쿨다운)
animal_cooldowns = {}
# 구역 자동 수확 완료 이벤트 (RanchZone이 꺼내 알림으로 표시)
ranch_events = []
# 보유 사냥용 칼 (1회용 — 목장_PRD 3.4)
hunting_knives = 0
# 구역 동물 상한 (목장_PRD 3.7 확정)
ANIMAL_LIMIT_PER_ZONE = 10
# 교배 전문가 보유 여부 — 구역별 1명 (목장_PRD 3.6/3.7)
breeders = {"chicken": False, "cow": False, "pig": False}

# 뷔페 시설 보유 수량 (뷔페_PRD 3.2 — b5 선행 규칙의 기준)
# 시작 시설: 식탁 1, 의자 2. 식탁=보유 의자 ≥ 식탁×2, 의자=빈자리(의자 < 식탁×2) 존재
BUFFET_FACILITIES_START = {"chair": 2, "table": 1, "decor": 0}
buffet_facilities = dict(BUFFET_FACILITIES_START)

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


# --- 저장/불러오기 (PRD 9단계 최소 구현 — 단축키 F5/F9, 메뉴 UI는 이후 이관) ---
import json
import os

SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
SAVE_VERSION = 1


def _slot_path(slot):
    return os.path.join(SAVE_DIR, f"slot_{slot}.json")


def save_game(slot=1, name=""):
    """현재 상태를 JSON 슬롯에 저장. (성공, 메시지) 반환."""
    if not 1 <= slot <= 5:
        return False, "SLOT ERROR"
    now = get_time()
    state = {
        "version": SAVE_VERSION,
        "name": name[:12],
        "money": money,
        "collected_items": dict(collected_items),
        "cooked_items": dict(cooked_items),
        "tools": list(tools),
        "farm_tools": list(farm_tools),
        "open_tunnels": dict(open_tunnels),
        "miners": dict(miners),
        "passes": list(passes),
        "animal_counts": dict(animal_counts),
        "hunting_knives": hunting_knives,
        "breeders": dict(breeders),
        "buffet_facilities": dict(buffet_facilities),
        "farm_unlocked": dict(farm_unlocked),
        # 상대시각(get_time 프로세스 기준)은 "경과 초"로 저장해 이식성 유지
        "play_elapsed": now - play_start_time,
        "animal_cooldowns": {k: v - now for k, v in animal_cooldowns.items()},
        "crop_slots": [
            [key[0], key[1],
             slot_data["planted_at"] - now,
             None if slot_data["harvested_at"] is None
             else slot_data["harvested_at"] - now]
            for key, slot_data in crop_slots.items()
        ],
        "miner_cycle_count": miner_cycle_count,
    }
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(_slot_path(slot), "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except OSError:
        return False, "SAVE FAILED"
    return True, f"SAVED SLOT {slot}"


def load_game(slot=1):
    """슬롯을 불러와 상태 복원. 실패 시 상태를 건드리지 않음. (성공, 메시지) 반환."""
    path = _slot_path(slot)
    if not os.path.exists(path):
        return False, f"NO SAVE SLOT {slot}"
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False, "SAVE DATA CORRUPT"
    if not isinstance(state, dict) or state.get("version") != SAVE_VERSION:
        return False, "SAVE VERSION MISMATCH"
    required = ("money", "collected_items", "tools", "animal_counts", "crop_slots")
    if any(key not in state for key in required):
        return False, "SAVE DATA INVALID"

    global money, play_start_time, hunting_knives, miner_cycle_count
    now = get_time()
    money = state["money"]
    collected_items.clear()
    collected_items.update(state["collected_items"])
    cooked_items.clear()
    cooked_items.update(state.get("cooked_items", {}))
    tools[:] = state["tools"]
    farm_tools[:] = state.get("farm_tools", [])
    open_tunnels.clear()
    open_tunnels.update(state.get("open_tunnels", open_tunnels))
    miners.clear()
    miners.update(state.get("miners", miners))
    passes[:] = state.get("passes", [])
    animal_counts.clear()
    animal_counts.update(state["animal_counts"])
    hunting_knives = state.get("hunting_knives", 0)
    breeders.clear()
    breeders.update(state.get("breeders", breeders))
    buffet_facilities.clear()
    buffet_facilities.update(
        state.get("buffet_facilities") or BUFFET_FACILITIES_START
    )
    farm_unlocked.clear()
    farm_unlocked.update(state.get("farm_unlocked", farm_unlocked))
    play_start_time = now - state.get("play_elapsed", 0)
    animal_cooldowns.clear()
    animal_cooldowns.update(
        {k: now + v for k, v in state.get("animal_cooldowns", {}).items()}
    )
    crop_slots.clear()
    for crop, index, planted, harvested in state["crop_slots"]:
        crop_slots[(crop, index)] = {
            "planted_at": now + planted,
            "harvested_at": None if harvested is None else now + harvested,
        }
    miner_cycle_count = state.get("miner_cycle_count", 0)
    return True, f"LOADED SLOT {slot}"


def list_saves():
    """슬롯 목록 조회. [(slot, name_or_None), ...] — 5슬롯 전체."""
    result = []
    for slot in range(1, 6):
        path = _slot_path(slot)
        name = None
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("name") or "( unnamed )" if isinstance(data, dict) else None
            except (json.JSONDecodeError, OSError):
                name = "(CORRUPT)"
        result.append((slot, name))
    return result


def delete_save(slot):
    """슬롯 삭제. (성공, 메시지) 반환."""
    path = _slot_path(slot)
    if not os.path.exists(path):
        return False, f"NO SAVE SLOT {slot}"
    try:
        os.remove(path)
    except OSError:
        return False, "DELETE FAILED"
    return True, f"DELETED SLOT {slot}"
