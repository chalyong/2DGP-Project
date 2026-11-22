# 목장 레이아웃과 동물 구역 (목장_PRD 3.1 / 3.2)
# 좌표는 pico2d 기준(원점 좌측 하단, y 위쪽 증가), 농사지와 동일 스케일 880x880
from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE

import auto_npc
import camera
import game_state

SIZE = 880
EXIT = (440, 790)  # 중앙 상단
MERCHANT = (120, 680)  # 좌측 상단
PLAYER_SPAWN = (440, 690)

ZONE_WIDTH = 240
ZONE_HEIGHT = 258

# 동물 1~3은 티어 순서대로: 닭(우상), 소(좌하), 돼지(우하)
ZONES = {
    "chicken": (705, 615),  # 동물 1 - 우상단
    "cow": (215, 235),  # 동물 2 - 좌하단
    "pig": (665, 235),  # 동물 3 - 우하단
}

ANIMAL_ORDER = ("chicken", "cow", "pig")
ANIMAL_FRAME_DURATION = 0.2
COOLDOWN_SECONDS = 120  # 자원 재획득 쿨다운 (목장_PRD 3.7 확정)

# 동물 -> 획득 자원 (목장_PRD 3.2)
RESOURCE = {
    "chicken": "egg",
    "cow": "milk",
    "pig": "mushroom",
}
# 동물 -> 사냥 시 획득하는 고기 (목장_PRD 3.4)
MEAT = {
    "chicken": "chicken",
    "cow": "beef",
    "pig": "pork",
}


def cooldown_remaining(animal):
    """남은 재획득 시간(초). 준비됐으면 0 이하."""
    last = game_state.animal_cooldowns.get(animal)
    if last is None:
        return 0.0
    return COOLDOWN_SECONDS - (get_time() - last)


def zone_rect(animal):
    cx, cy = ZONES[animal]
    return (
        cx - ZONE_WIDTH / 2,
        cy - ZONE_HEIGHT / 2,
        cx + ZONE_WIDTH / 2,
        cy + ZONE_HEIGHT / 2,
    )


def zone_at(animal, x, y):
    """좌표가 해당 동물 구역 안이면 True."""
    x0, y0, x1, y1 = zone_rect(animal)
    return x0 <= x < x1 and y0 <= y < y1


class RanchZone:
    """동물 구역: 울타리와 게이트 렌더링 (이후 동물·타이머 렌더 확장)."""

    fence_image = None
    gate_image = None
    font = None

    def __init__(self, animal, player):
        self.animal = animal
        self.player = player
        self.sheet = None
        self.pending = None
        self.notification = None
        self.notification_started = 0
        if RanchZone.fence_image is None:
            RanchZone.fence_image = load_image(
                "assets/buildings/fence_tile_length.png"
            )
            RanchZone.gate_image = load_image("assets/buildings/fence_gate.png")
        if RanchZone.font is None:
            RanchZone.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        self.sheet = load_image(f"assets/npc/animal_{animal}.png")

    def handle_event(self, event):
        """구역 안 Space: 2초 작업 모션 후 자원 획득 (목장_PRD 3.3/3.7)."""
        if event.type != SDL_KEYDOWN or event.key != SDLK_SPACE:
            return
        if self.player.movement_locked or self.player.farm_work:
            return
        if not zone_at(self.animal, self.player.x, self.player.y):
            return
        if self.pending is not None:
            return
        if game_state.animal_counts[self.animal] <= 0:
            return  # 동물 0마리 구역은 무응답
        if cooldown_remaining(self.animal) > 0:
            return  # 재획득 전 중복 획득 불가
        now = get_time()
        # 칼 보유 시 사냥(자원+고기), 없으면 자원만 획득
        kind = "hunt" if game_state.hunting_knives > 0 else "collect"
        if not self.player.start_farm_work(auto_npc.MOTION_SECONDS):
            return
        self.pending = (kind, now + auto_npc.MOTION_SECONDS)

    def update(self):
        if self.pending is None:
            return
        kind, done_at = self.pending
        now = get_time()
        if now < done_at:
            return
        self.pending = None
        if kind not in ("collect", "hunt"):
            return
        amount = game_state.animal_counts[self.animal]
        if amount <= 0:
            return
        resource = RESOURCE[self.animal]
        game_state.collected_items[resource] += amount
        game_state.animal_cooldowns[self.animal] = now
        note = f"{resource.upper()} * {amount}"
        # 모션 종료 시점에 칼이 남아있으면 사냥 처리 (칼 1개 + 동물 1마리 감소)
        if kind == "hunt" and game_state.hunting_knives > 0:
            game_state.hunting_knives -= 1
            meat = MEAT[self.animal]
            game_state.collected_items[meat] += 1
            game_state.animal_counts[self.animal] -= 1
            auto_npc.remove_animal(self.animal)
            note += f" + {meat.upper()}"
        self.notification = note
        self.notification_started = now

    def draw(self):
        x0, y0, x1, y1 = zone_rect(self.animal)
        cx, cy = ZONES[self.animal]
        RanchZone.fence_image.draw(
            cx - camera.x,
            cy - camera.y,
            ZONE_WIDTH,
            ZONE_HEIGHT,
        )
        # 게이트: 구역 하단 중앙 (들어오는 방향)
        RanchZone.gate_image.draw(
            (x0 + x1) / 2 - camera.x,
            y0 - camera.y,
            64,
            64,
        )
        self._draw_animals()
        self._draw_cooldown_timer()
        self._draw_notification()

    def _draw_cooldown_timer(self):
        """구역 우측 하단 내측에 남은 재획득 시간(MM:SS) 표시."""
        remaining = cooldown_remaining(self.animal)
        if remaining <= 0:
            return
        minutes, seconds = divmod(int(remaining + 0.999), 60)
        x0, y0, x1, y1 = zone_rect(self.animal)
        RanchZone.font.draw(
            x1 - 55 - camera.x,
            y0 + 8 - camera.y,
            f"{minutes:02d}:{seconds:02d}",
            (170, 170, 170),
        )

    def _draw_notification(self):
        if not self.notification:
            return
        elapsed = get_time() - self.notification_started
        duration = 1.0
        if elapsed >= duration:
            self.notification = None
            return
        progress = elapsed / duration
        rise = 30 * progress
        start_color = (255, 239, 177)
        end_color = (95, 95, 95)
        color = tuple(
            int(start + (end - start) * progress)
            for start, end in zip(start_color, end_color)
        )
        RanchZone.font.draw(
            self.player.x - camera.x - 30,
            self.player.y - camera.y + 45 + rise,
            self.notification,
            color,
        )

    def _draw_animals(self):
        now = get_time()
        for a in auto_npc.animals:
            if a["animal"] != self.animal:
                continue
            delta = max(0.0, now - a.setdefault("anim_time", now))
            a["anim_time"] = now
            a["frame_timer"] += delta
            while a["frame_timer"] >= ANIMAL_FRAME_DURATION:
                a["frame"] = (a["frame"] + 1) % 4
                a["frame_timer"] -= ANIMAL_FRAME_DURATION
            flip = "h" if a["facing"] == "left" else ""
            self.sheet.clip_composite_draw(
                a["frame"] * 64,
                0,
                64,
                64,
                0,
                flip,
                a["x"] - camera.x,
                a["y"] - camera.y,
                56,
                64,
            )
