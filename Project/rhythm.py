# 4노트 리듬게임 판 (뷔페_PRD 3.3)
# b9: 판 표시와 노트 낙하 — 판정·보상은 b10에서 추가
import random

from pico2d import get_time, load_font, load_image

import shop

PANEL_CENTER_X = 400
PANEL_WIDTH = 340
PANEL_HEIGHT = 530
LANE_COUNT = 4
SPAWN_MIN_SECONDS = 0.5
SPAWN_MAX_SECONDS = 1.0
MAX_ACTIVE_NOTES = 2
FALL_SECONDS = 2.0  # 패널 상단 -> 히트라인 낙하 시간
NOTE_LINGER_SECONDS = 0.35  # 히트라인 통과 후 제거 대기
NOTE_SIZE = 44
FRAME_SIZE = 66
HIT_RATIO = 0.16  # 패널 하단 기준 히트라인 높이


class RhythmGame:
    panel = None
    hitline = None
    frame = None
    error_font = None

    def __init__(self, requests, errors=()):
        if RhythmGame.panel is None:
            RhythmGame.panel = load_image("assets/ui/buffet_rhythm_panel.png")
            RhythmGame.hitline = load_image("assets/ui/buffet_rhythm_hitline.png")
            RhythmGame.frame = load_image("assets/ui/buffet_rhythm_frame.png")
            RhythmGame.error_font = load_font(
                r"C:\Windows\Fonts\consolab.ttf", 16
            )
        queue = []
        for name, quantity in requests:
            queue.extend([name] * quantity)
        random.shuffle(queue)
        self.queue = queue
        self.active = []  # {"name", "lane", "spawned_at"}
        self.errors = list(errors)
        self.next_spawn_at = get_time() + SPAWN_MIN_SECONDS

    @property
    def done(self):
        return not self.queue and not self.active

    @property
    def panel_left(self):
        return PANEL_CENTER_X - PANEL_WIDTH // 2

    @property
    def panel_bottom(self):
        return 300 - PANEL_HEIGHT // 2

    @property
    def hit_y(self):
        return self.panel_bottom + int(PANEL_HEIGHT * HIT_RATIO)

    def lane_x(self, lane):
        lane_width = PANEL_WIDTH / LANE_COUNT
        return self.panel_left + lane_width * (lane + 0.5)

    def update(self):
        now = get_time()
        if (
            self.queue
            and len(self.active) < MAX_ACTIVE_NOTES
            and now >= self.next_spawn_at
        ):
            name = self.queue.pop(0)
            self.active.append(
                {
                    "name": name,
                    "lane": random.randrange(LANE_COUNT),
                    "spawned_at": now,
                }
            )
            self.next_spawn_at = now + random.uniform(
                SPAWN_MIN_SECONDS, SPAWN_MAX_SECONDS
            )
        self.active = [
            note
            for note in self.active
            if now - note["spawned_at"] <= FALL_SECONDS + NOTE_LINGER_SECONDS
        ]

    def draw(self):
        top = self.panel_bottom + PANEL_HEIGHT
        hit_y = self.hit_y
        RhythmGame.panel.draw(
            PANEL_CENTER_X,
            self.panel_bottom + PANEL_HEIGHT // 2,
            PANEL_WIDTH,
            PANEL_HEIGHT,
        )
        # 히트라인: 노랑 선은 이미지 수직 중앙
        hit_height = int(230 * PANEL_WIDTH / 381)
        RhythmGame.hitline.draw(
            PANEL_CENTER_X, hit_y, PANEL_WIDTH, hit_height
        )
        # 레인별 타깃 카드
        for lane in range(LANE_COUNT):
            RhythmGame.frame.draw(
                int(self.lane_x(lane)), hit_y, FRAME_SIZE, FRAME_SIZE
            )
        # 낙하 노트 (요리 아이콘)
        now = get_time()
        for note in self.active:
            ratio = min((now - note["spawned_at"]) / FALL_SECONDS, 1.0)
            y = top - (top - hit_y) * ratio
            shop.draw_item_icon(
                note["name"],
                int(self.lane_x(note["lane"])),
                int(y),
                size=NOTE_SIZE,
                prefer_item=True,
            )
        if self.errors:
            RhythmGame.error_font.draw(
                400, 578, " / ".join(self.errors), (255, 150, 120)
            )
