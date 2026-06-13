import pygame

from core import (
    FIGHTER_SCALE,
    FIGHTER_SPRITE_HEIGHT,
    FRAME_INDICES,
    MOTION_ROW_Y,
    SHEET_FRAME_WIDTH,
    STATIC_ROW_Y,
    getFileAdd,
)


def load_spritesheet_strip(sheet, row_y):
    frames = []
    for idx in FRAME_INDICES:
        rect = pygame.Rect(idx * SHEET_FRAME_WIDTH, row_y, SHEET_FRAME_WIDTH, FIGHTER_SPRITE_HEIGHT)
        frame = sheet.subsurface(rect).copy()
        new_w = int(SHEET_FRAME_WIDTH * FIGHTER_SCALE)
        new_h = int(FIGHTER_SPRITE_HEIGHT * FIGHTER_SCALE)
        frame = pygame.transform.scale(frame, (new_w, new_h))
        frames.append(frame)
    return frames


def apply_tint(surface, tint):
    if tint == (255, 255, 255):
        return surface.copy()
    tinted = surface.copy()
    tinted.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
    return tinted


spritesheet = pygame.image.load(getFileAdd("fighter.png")).convert_alpha()
base_static_frames = load_spritesheet_strip(spritesheet, STATIC_ROW_Y)
base_motion_frames = load_spritesheet_strip(spritesheet, MOTION_ROW_Y)

game_backgrounds = [pygame.image.load(getFileAdd(f"assets/background{index}.png")).convert() for index in range(1, 4)]

SKINS = [
    {"name": "Original", "tint": (255, 255, 255)},
    {"name": "Azure", "tint": (140, 180, 255)},
    {"name": "Emerald", "tint": (160, 255, 170)},
    {"name": "Shadow", "tint": (170, 150, 200)},
]


def build_skin_frames(skin):
    static_right = [apply_tint(f, skin["tint"]) for f in base_static_frames]
    motion_right = [apply_tint(f, skin["tint"]) for f in base_motion_frames]
    static_left = [pygame.transform.flip(f, True, False) for f in static_right]
    motion_left = [pygame.transform.flip(f, True, False) for f in motion_right]
    return {
        "static_right": static_right,
        "static_left": static_left,
        "motion_right": motion_right,
        "motion_left": motion_left,
    }


SKIN_FRAMES = [build_skin_frames(skin) for skin in SKINS]
