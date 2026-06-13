import pygame

from core import getFileAdd


game_backgrounds = [pygame.image.load(getFileAdd(f"assets/background{index}.png")).convert() for index in range(1, 4)]


FIGHTER_FRAME_W = 209
FIGHTER_FRAME_H = 313
FIGHTER_DISPLAY_SCALE = 0.6

# state -> (row index - type of movement, column index - segment of movement)
FIGHTER_STATES = {
    "static": (0, [0, 2, 5]),
    "motion": (2, [0, 2, 5]),
    "block": (3, [1]),
    "dead": (3, [3, 4, 5]),
}


def load_fighter_frames(file_path):
    sheet = pygame.image.load(getFileAdd(file_path)).convert_alpha()
    new_w = int(FIGHTER_FRAME_W * FIGHTER_DISPLAY_SCALE)
    new_h = int(FIGHTER_FRAME_H * FIGHTER_DISPLAY_SCALE)
    frames = {}
    for state, (row, cols) in FIGHTER_STATES.items():
        right = []
        for col in cols:
            rect = pygame.Rect(col * FIGHTER_FRAME_W, row * FIGHTER_FRAME_H, FIGHTER_FRAME_W, FIGHTER_FRAME_H)
            frame = pygame.transform.scale(sheet.subsurface(rect).copy(), (new_w, new_h))
            right.append(frame)
        left = [pygame.transform.flip(f, True, False) for f in right]
        frames[f"{state}_right"] = right
        frames[f"{state}_left"] = left
    return frames


FIGHTERS = [
    {"name": "Basic", "frames": load_fighter_frames("assets/basic_fighter_transparent.png")},
    {"name": "Edie", "frames": load_fighter_frames("assets/edie_fighter_transparent.png")},
    {"name": "Kazumi", "frames": load_fighter_frames("assets/kazumi_fighter_transparent.png")},
]
