# 농부 고용 데이터와 배치
# 이동 속도는 플레이어 속도 기반 (농장_PRD 4절: 자동 NPC = 플레이어, 동물 = 그 절반)
import math
import random

from pico2d import get_time

import farm
import game_state
from player import WALK_SPEED_PIXELS_PER_SECOND

MAX_PER_ZONE = 3
SPEED_RATIO = 0.5  # 플레이어 속도의 절반 (동물도 동일 배율)
HARVEST_POSE_SECONDS = 5.0  # 수확 동작 전체 시간 (스프라이트 4프레임과 동일)

states = []


def speed():
    return WALK_SPEED_PIXELS_PER_SECOND * SPEED_RATIO


def count(crop):
    return sum(1 for f in states if f["crop"] == crop)


def at_limit(crop):
    return count(crop) >= MAX_PER_ZONE


def hire(crop):
    """농부 고용. 제한 초과 시 False."""
    if at_limit(crop):
        return False
    x, y = _random_spot(crop)
    states.append(
        {
            "crop": crop,
            "x": x,
            "y": y,
            "tx": x,
            "ty": y,
            "facing": "right",
            "moving": False,
            "frame": 0,
            "frame_timer": 0.0,
            "harvest_until": 0.0,
            "last_update": get_time(),
        }
    )
    return True


def update():
    """무작위 이동 + 발밑의 성숙 작물 자동 수확 (장면 밖에서도 진행)."""
    now = get_time()
    for f in states:
        delta = max(0.0, now - f["last_update"])
        f["last_update"] = now
        if now < f["harvest_until"]:
            f["moving"] = False
            continue
        _try_harvest(f, now)
        if now < f["harvest_until"]:
            f["moving"] = False
            continue
        dx = f["tx"] - f["x"]
        dy = f["ty"] - f["y"]
        distance = math.hypot(dx, dy)
        step = speed() * delta
        if distance <= step:
            f["x"], f["y"] = f["tx"], f["ty"]
            f["moving"] = False
            f["tx"], f["ty"] = _random_spot(f["crop"])
        else:
            f["x"] += dx / distance * step
            f["y"] += dy / distance * step
            f["moving"] = True
            f["facing"] = "left" if dx < 0 else "right"
        _plant_at(f, now)


def _plant_at(f, now):
    """발밑의 빈 칸에 씨앗을 심는다."""
    index = farm.cell_at(f["crop"], f["x"], f["y"])
    if index is None or index == farm.SPRINKLER_CELL:
        return
    key = (f["crop"], index)
    if key in game_state.crop_slots:
        return
    game_state.crop_slots[key] = {
        "planted_at": now,
        "harvested_at": None,
    }


def _try_harvest(f, now):
    index = farm.cell_at(f["crop"], f["x"], f["y"])
    if index is None or index == farm.SPRINKLER_CELL:
        return
    slot = game_state.crop_slots.get((f["crop"], index))
    if slot is None:
        return
    stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
    if farm.crop_stage(slot, now, stage_seconds) != farm.READY_STAGE:
        return
    game_state.collected_items[f["crop"]] += game_state.harvest_yield(f["crop"])
    slot["harvested_at"] = now
    f["harvest_until"] = now + HARVEST_POSE_SECONDS
    # 수확 스프라이트를 프레임 0부터 재생
    f["frame"] = 0
    f["frame_timer"] = 0.0


def _random_spot(crop):
    left, bottom, right, top = farm.plow_rect(crop)
    while True:
        x = random.uniform(left + 16, right - 16)
        y = random.uniform(bottom + 16, top - 16)
        if farm.cell_at(crop, x, y) != farm.SPRINKLER_CELL:
            return x, y
