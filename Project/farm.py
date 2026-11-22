# ?띿궗吏 ?덉씠?꾩썐쨌?щ같 援ъ뿭 湲고븯?숆낵 援ъ뿭 ?뚮뜑留?
# 醫뚰몴??pico2d 湲곗?(?먯젏 醫뚯륫 ?섎떒, y ?꾩そ 利앷?), ?ㅼ???40px/m
from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE

import camera
import auto_npc
import game_state


FARMER_FRAME_DURATION = 0.15


SIZE = 880
EXIT = (440, 790)
MERCHANT = (120, 680)
PLAYER_SPAWN = (440, 690)

GRID = 5
PLOW_WIDTH = 240
PLOW_HEIGHT = 258
CELL_WIDTH = PLOW_WIDTH / GRID
CELL_HEIGHT = PLOW_HEIGHT / GRID

# ?묐Ъ -> ?щ같 援ъ뿭 以묒떖 (?곗긽?? 醫뚰븯?? ?고븯??
ZONES = {
    "wheat": (705, 615),
    "potato": (215, 235),
    "strawberry": (665, 235),
}
SPRINKLER_CELL = 12  # 5x5 以묒븰 移?

# ?깆옣쨌?ъ꽦???쒓컙 (媛쒕컻 以?寃곗젙媛? PRD 7??李몄“)
STAGE_SECONDS = 20  # ?④퀎???쒓컙 -> ?⑥븮?먯꽌 ready源뚯? 60珥?
REGROW_SECONDS = 120  # ?섑솗 ???ㅼ떆 ?깆옣?섍린源뚯? 2遺?
READY_STAGE = 3


def plow_rect(crop):
    cx, cy = ZONES[crop]
    return (
        cx - PLOW_WIDTH / 2,
        cy - PLOW_HEIGHT / 2,
        cx + PLOW_WIDTH / 2,
        cy + PLOW_HEIGHT / 2,
    )


def cell_rect(crop, index):
    """移??몃뜳??0~24, ?꾩そ ?쇱そ遺??媛濡?諛⑺뼢)??(x0, y0, x1, y1)."""
    left, bottom, right, top = plow_rect(crop)
    col = index % GRID
    row = index // GRID
    x0 = left + col * CELL_WIDTH
    y1 = top - row * CELL_HEIGHT
    return (x0, y1 - CELL_HEIGHT, x0 + CELL_WIDTH, y1)


def cell_at(crop, x, y):
    """醫뚰몴媛 ?랁븳 移??몃뜳?? 援ъ뿭 諛뽰씠硫?None."""
    left, bottom, right, top = plow_rect(crop)
    if not (left <= x < right and bottom <= y < top):
        return None
    col = int((x - left) // CELL_WIDTH)
    row = int((top - y) // CELL_HEIGHT)
    col = min(col, GRID - 1)
    row = min(row, GRID - 1)
    return row * GRID + col


def sprinkler_rect(crop):
    return cell_rect(crop, SPRINKLER_CELL)


def is_sprinkler_hit(crop, x, y):
    x0, y0, x1, y1 = sprinkler_rect(crop)
    return x0 <= x < x1 and y0 <= y < y1


def crop_stage(slot, now, stage_seconds=None):
    """?묐Ъ ?깆옣 ?④퀎(0=seed ~ 3=ready). ?꾩쭅 ?녿뒗 ?곹깭硫?None.

    slot: {"planted_at": ?쒓컖, "harvested_at": ?쒓컖 or None}
    ?섑솗 ??REGROW_SECONDS媛 吏?섎㈃ ?ㅼ떆 ?⑥븮遺???먮???
    """
    if stage_seconds is None:
        stage_seconds = STAGE_SECONDS
    planted = slot["planted_at"]
    harvested = slot["harvested_at"]
    if harvested is not None:
        if now - harvested < REGROW_SECONDS:
            return None
        planted = harvested + REGROW_SECONDS
    return min(int((now - planted) // stage_seconds), READY_STAGE)


class FarmZone:
    plow_image = None
    locked_image = None
    sprinkler_image = None
    crop_images = {}
    font = None
    farmer_idle = None
    farmer_walk = None
    farmer_harvest = None

    def __init__(self, crop, player):
        self.crop = crop
        self.player = player
        self.pending = None
        self.notification = None
        self.notification_started = 0
        if FarmZone.plow_image is None:
            FarmZone.plow_image = load_image("assets/farm_tile/plow.png")
            FarmZone.locked_image = load_image("assets/farm_tile/locked_plow.png")
            FarmZone.sprinkler_image = load_image("assets/farm_tile/sprinkler.png")
        if FarmZone.font is None:
            FarmZone.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        if FarmZone.farmer_idle is None:
            FarmZone.farmer_idle = load_image("assets/npc/farmer_idle.png")
            FarmZone.farmer_walk = load_image("assets/npc/farmer_walk_right.png")
            FarmZone.farmer_harvest = load_image("assets/npc/farmer_harvest.png")
        if crop not in FarmZone.crop_images:
            FarmZone.crop_images[crop] = load_image(
                f"assets/farm_tile/crop_{crop}.png"
            )
        self.crop_image = FarmZone.crop_images[crop]

    def handle_event(self, event):
        if event.type != SDL_KEYDOWN or event.key != SDLK_SPACE:
            return
        if self.player.movement_locked or self.player.farm_work:
            return
        if not game_state.farm_unlocked[self.crop]:
            return
        index = cell_at(self.crop, self.player.x, self.player.y)
        if index is None or index == SPRINKLER_CELL:
            return
        if self.pending is not None:
            return
        key = (self.crop, index)
        now = get_time()
        slot = game_state.crop_slots.get(key)
        stage_seconds = game_state.crop_stage_seconds(STAGE_SECONDS)
        if slot is None:
            kind = "plant"
        elif crop_stage(slot, now, stage_seconds) == READY_STAGE:
            kind = "harvest"
        else:
            return
        # ?뚮젅?댁뼱???띾?? 媛숈? ?묒뾽 紐⑥뀡??癒쇱? ?ъ깮?쒕떎
        if not self.player.start_farm_work(auto_npc.MOTION_SECONDS):
            return
        self.pending = (kind, index, now + auto_npc.MOTION_SECONDS)

    def update(self):
        if self.pending is None:
            return
        kind, index, done_at = self.pending
        now = get_time()
        if now < done_at:
            return
        self.pending = None
        amount = game_state.harvest_yield(self.crop)
        applied = game_state.apply_farm_work(self.crop, kind, index, now)
        if applied and kind == "harvest":
            self.notification = f"{self.crop.upper()} * {amount}"
            self.notification_started = now

    def draw(self):
        if game_state.farm_unlocked[self.crop]:
            image = FarmZone.plow_image
        else:
            image = FarmZone.locked_image
        # 5x5 媛?移몄뿉 媛쒕퀎 寃쎌옉吏, ?닿툑 ??援ъ뿭? locked_plow
        for index in range(GRID * GRID):
            x0, y0, x1, y1 = cell_rect(self.crop, index)
            image.draw(
                (x0 + x1) / 2 - camera.x,
                (y0 + y1) / 2 - camera.y,
                CELL_WIDTH,
                CELL_HEIGHT,
            )
        self._draw_crops()
        # ?ㅽ봽留곹겢?? 援ъ뿭 以묒븰 移?(?좉릿 援ъ뿭?먮룄 ?쒖꽕? 議댁옱)
        x0, y0, x1, y1 = sprinkler_rect(self.crop)
        FarmZone.sprinkler_image.draw(
            (x0 + x1) / 2 - camera.x,
            (y0 + y1) / 2 - camera.y,
            54,
            70,
        )
        self._draw_farmers()
        self._draw_notification()

    def _draw_farmers(self):
        now = get_time()
        for f in auto_npc.states:
            if f["crop"] != self.crop:
                continue
            delta = max(0.0, now - f.setdefault("anim_time", now))
            f["anim_time"] = now
            in_motion = now < f.get("motion_until", 0.0)
            frame_duration = (
                auto_npc.MOTION_SECONDS / 4 if in_motion else FARMER_FRAME_DURATION
            )
            f["frame_timer"] += delta
            while f["frame_timer"] >= frame_duration:
                f["frame"] = (f["frame"] + 1) % 4
                f["frame_timer"] -= frame_duration
            if in_motion:
                image = FarmZone.farmer_harvest
            elif f["moving"]:
                image = FarmZone.farmer_walk
            else:
                image = FarmZone.farmer_idle
            flip = "h" if f["facing"] == "left" else ""
            image.clip_composite_draw(
                f["frame"] * 64,
                0,
                64,
                64,
                0,
                flip,
                f["x"] - camera.x,
                f["y"] - camera.y,
                56,
                64,
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
        FarmZone.font.draw(
            self.player.x - camera.x - 30,
            self.player.y - camera.y + 45 + rise,
            self.notification,
            color,
        )

    def _draw_crops(self):
        now = get_time()
        stage_seconds = game_state.crop_stage_seconds(STAGE_SECONDS)
        for (crop, index), slot in game_state.crop_slots.items():
            if crop != self.crop:
                continue
            stage = crop_stage(slot, now, stage_seconds)
            if stage is None:
                continue
            x0, y0, x1, y1 = cell_rect(crop, index)
            self.crop_image.clip_composite_draw(
                stage * 48,
                0,
                48,
                48,
                0,
                "",
                (x0 + x1) / 2 - camera.x,
                (y0 + y1) / 2 - camera.y,
                44,
                44,
            )

