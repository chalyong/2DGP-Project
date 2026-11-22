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
MOTION_SECONDS = 3.0  # 수확·심기 동작 모션 전체 시간 (스프라이트 4프레임과 동일)

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
            "motion_until": 0.0,
            "action": None,
            "last_update": get_time(),
        }
    )
    return True


def update():
    """무작위 이동 + 발밑 작물 관리 (심기·수확은 모션 후 결과 적용).

    장면 밖에서도 진행된다.
    """
    now = get_time()
    for f in states:
        delta = max(0.0, now - f["last_update"])
        f["last_update"] = now
        if now < f["motion_until"]:
            f["moving"] = False
            continue
        if f["action"] is not None:
            _apply_action(f, now)
            f["action"] = None
            f["moving"] = False
            continue
        index = farm.cell_at(f["crop"], f["x"], f["y"])
        if index is not None and index != farm.SPRINKLER_CELL:
            slot = game_state.crop_slots.get((f["crop"], index))
            if slot is None:
                _start_motion(f, now, ("plant", index))
                continue
            stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
            if farm.crop_stage(slot, now, stage_seconds) == farm.READY_STAGE:
                _start_motion(f, now, ("harvest", index))
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


def _start_motion(f, now, action):
    """동작 모션을 시작한다. 결과는 모션이 끝난 뒤 적용된다."""
    f["action"] = action
    f["motion_until"] = now + MOTION_SECONDS
    f["moving"] = False
    f["frame"] = 0
    f["frame_timer"] = 0.0


def _apply_action(f, now):
    """모션 종료 시점에 심기/수확 결과를 적용한다 (상태 재검증)."""
    kind, index = f["action"]
    key = (f["crop"], index)
    if kind == "harvest":
        slot = game_state.crop_slots.get(key)
        if slot is None:
            return
        stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
        if farm.crop_stage(slot, now, stage_seconds) != farm.READY_STAGE:
            return
        game_state.collected_items[f["crop"]] += game_state.harvest_yield(
            f["crop"]
        )
        slot["harvested_at"] = now
    else:
        if key in game_state.crop_slots:
            return
        game_state.crop_slots[key] = {
            "planted_at": now,
            "harvested_at": None,
        }


def _random_spot(crop):
    left, bottom, right, top = farm.plow_rect(crop)
    while True:
        x = random.uniform(left + 16, right - 16)
        y = random.uniform(bottom + 16, top - 16)
        if farm.cell_at(crop, x, y) != farm.SPRINKLER_CELL:
            return x, y
