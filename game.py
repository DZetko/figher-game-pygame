import os

import pygame


def getFileAdd(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, file_name)


# konstanty
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (40, 30, 60)
GROUND_TOP = (110, 70, 40)
GROUND_MID = (70, 45, 25)
GROUND_DARK = (40, 25, 15)
HP_BG = (60, 0, 0)
HP_FG = (220, 40, 40)
BTN_BG = (50, 50, 80)
BTN_BG_HOVER = (90, 90, 130)

GAME_WIDTH = 1000
GAME_HEIGHT = 600
FPS = 30

GRAVITY = 1.2
JUMP_V = -18
MOVE_SPEED = 5

GROUND_Y = GAME_HEIGHT - 90
FIGHTER_SCALE = 0.7

# Fighter sprite sheet
SHEET_FRAME_WIDTH = 192
STATIC_ROW_Y = 60
MOTION_ROW_Y = 420
FIGHTER_SPRITE_HEIGHT = 280
FRAME_INDICES = [0, 3, 7]  # we are only using state 1, 4, 8 from the generated sprite sheet

# Game states
STATE_LOADING = "loading"
STATE_MENU = "menu"
STATE_SETTINGS = "settings"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

LOADING_DURATION_MS = 3000

# start pygame
pygame.init()

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Tekken")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("monospace", 64, bold=True)
menu_font = pygame.font.SysFont("monospace", 32, bold=True)
label_font = pygame.font.SysFont("monospace", 24, bold=True)
hud_font = pygame.font.SysFont("monospace", 18, bold=True)
result_label_font = pygame.font.SysFont("monospace", 48, bold=True)


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


class FighterBase:
    def __init__(self, x, facing_right, controls, hp_location, skin_idx):
        self.x = x
        self.y = GROUND_Y
        self.vy = 0
        self.on_ground = True
        self.facing_right = facing_right
        self.controls = controls
        self.hp_location: tuple[int, int] = hp_location
        self.skin_idx = skin_idx
        self.hp = 100

        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 6

        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = 12
        self.has_hit = False

        self.w = base_static_frames[0].get_width()
        self.h = base_static_frames[0].get_height()

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h, self.w, self.h)

    def hit_rect(self):
        reach = 60
        if self.facing_right:
            return pygame.Rect(self.x + 10, self.y - self.h * 0.7, reach, self.h * 0.4)
        return pygame.Rect(self.x - 10 - reach, self.y - self.h * 0.7, reach, self.h * 0.4)

    def handle_input(self, keys):
        if self.is_punching:
            return
        moved = False
        if keys[self.controls["left"]]:
            self.x -= MOVE_SPEED
            self.facing_right = False
            moved = True
        if keys[self.controls["right"]]:
            self.x += MOVE_SPEED
            self.facing_right = True
            moved = True
        if keys[self.controls["jump"]] and self.on_ground:
            self.vy = JUMP_V
            self.on_ground = False
        self.x = max(self.w // 2, min(GAME_WIDTH - self.w // 2, self.x))
        return moved

    def start_punch(self):
        if self.is_punching or not self.on_ground:
            return
        self.is_punching = True
        self.punch_timer = 0
        self.frame_idx = 0
        self.frame_timer = 0
        self.has_hit = False

    def update(self):
        # gravitace
        if not self.on_ground:
            self.vy += GRAVITY
            self.y += self.vy
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.vy = 0
                self.on_ground = True

        # animace
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(FRAME_INDICES)

        # punch state
        if self.is_punching:
            self.punch_timer += 1
            if self.punch_timer >= self.punch_duration:
                self.is_punching = False
                self.frame_idx = 0

    def try_hit(self, other):
        if not self.is_punching or self.has_hit:
            return
        # úder zasáhne někde uprostřed animace
        if self.punch_timer < self.punch_duration // 3:
            return
        if self.hit_rect().colliderect(other.rect()):
            other.hp = max(0, other.hp - 8)
            self.has_hit = True

    def draw(self, surf):
        frames_set = SKIN_FRAMES[self.skin_idx]
        if self.is_punching:
            frames = frames_set["motion_right"] if self.facing_right else frames_set["motion_left"]
        else:
            frames = frames_set["static_right"] if self.facing_right else frames_set["static_left"]
        img = frames[self.frame_idx]
        rect = img.get_rect()
        rect.midbottom = (int(self.x), int(self.y))
        surf.blit(img, rect)


class Fighter1(FighterBase):
    controls = {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "punch": pygame.K_f,
    }

    def __init__(self, skin_idx=0):
        super().__init__(250, True, self.controls, (30, 20), skin_idx)


class Fighter2(FighterBase):
    controls = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "punch": pygame.K_RSHIFT,
    }

    def __init__(self, skin_idx=0):
        super().__init__(750, True, self.controls, (GAME_WIDTH - 390, 20), skin_idx)


def draw_hp_bar(surf, location, hp, label):
    x, y = location
    w, h = 360, 18
    pygame.draw.rect(surf, HP_BG, (x, y, w, h))
    pygame.draw.rect(surf, HP_FG, (x, y, int(w * hp / 100), h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)
    surf.blit(hud_font.render(f"{label}: {hp}", True, WHITE), (x, y + h + 4))


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def draw(self, surf, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(surf, BTN_BG_HOVER if hovered else BTN_BG, self.rect, border_radius=6)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=6)
        text = font.render(self.label, True, WHITE)
        surf.blit(text, text.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# Menu buttons
MENU_BTN_W, MENU_BTN_H = 320, 60
menu_x = GAME_WIDTH // 2 - MENU_BTN_W // 2
start_btn = Button((menu_x, 240, MENU_BTN_W, MENU_BTN_H), "START")
settings_btn = Button((menu_x, 320, MENU_BTN_W, MENU_BTN_H), "SETTINGS")
exit_btn = Button((menu_x, 400, MENU_BTN_W, MENU_BTN_H), "EXIT")

# Settings buttons
ARROW_W, ARROW_H = 50, 50
P1_COL_X = GAME_WIDTH // 4
P2_COL_X = 3 * GAME_WIDTH // 4
ARROWS_Y = 420

p1_left_btn = Button((P1_COL_X - 110, ARROWS_Y, ARROW_W, ARROW_H), "<")
p1_right_btn = Button((P1_COL_X + 60, ARROWS_Y, ARROW_W, ARROW_H), ">")
p2_left_btn = Button((P2_COL_X - 110, ARROWS_Y, ARROW_W, ARROW_H), "<")
p2_right_btn = Button((P2_COL_X + 60, ARROWS_Y, ARROW_W, ARROW_H), ">")
back_btn = Button((GAME_WIDTH // 2 - 100, 510, 200, 50), "BACK")


state = STATE_LOADING
loading_started_at = pygame.time.get_ticks()
p1_skin_idx = 0
p2_skin_idx = 0
p1 = None
p2 = None
winner = None
running = True


def start_new_game():
    global state, p1, p2, winner
    p1 = Fighter1(p1_skin_idx)
    p2 = Fighter2(p2_skin_idx)
    winner = None
    state = STATE_PLAYING


def draw_loading(surf, elapsed_ms):
    surf.fill(BLACK)
    title = title_font.render("TEKKEN", True, WHITE)
    surf.blit(title, title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 30)))

    bar_w, bar_h = 360, 16
    bar_x = GAME_WIDTH // 2 - bar_w // 2
    bar_y = GAME_HEIGHT // 2 + 40
    progress = min(1.0, elapsed_ms / LOADING_DURATION_MS)
    pygame.draw.rect(surf, BTN_BG, (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(surf, HP_FG, (bar_x, bar_y, int(bar_w * progress), bar_h))
    pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)

    loading_label = label_font.render("Loading...", True, WHITE)
    surf.blit(loading_label, loading_label.get_rect(center=(GAME_WIDTH // 2, bar_y + 50)))


def draw_menu(surf, mouse_pos):
    surf.fill(SKY)
    title = title_font.render("TEKKEN", True, WHITE)
    surf.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 130)))
    start_btn.draw(surf, menu_font, mouse_pos)
    settings_btn.draw(surf, menu_font, mouse_pos)
    exit_btn.draw(surf, menu_font, mouse_pos)


def draw_player_column(surf, label, x, skin_idx):
    label_img = label_font.render(label, True, WHITE)
    surf.blit(label_img, label_img.get_rect(center=(x, 150)))

    preview = SKIN_FRAMES[skin_idx]["static_right"][0]
    surf.blit(preview, preview.get_rect(center=(x, 290)))

    name_img = hud_font.render(SKINS[skin_idx]["name"], True, WHITE)
    surf.blit(name_img, name_img.get_rect(center=(x, ARROWS_Y + ARROW_H // 2)))


def draw_settings(surf, mouse_pos):
    surf.fill(SKY)
    title = title_font.render("SETTINGS", True, WHITE)
    surf.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 50)))

    draw_player_column(surf, "Player 1", P1_COL_X, p1_skin_idx)
    draw_player_column(surf, "Player 2", P2_COL_X, p2_skin_idx)

    p1_left_btn.draw(surf, menu_font, mouse_pos)
    p1_right_btn.draw(surf, menu_font, mouse_pos)
    p2_left_btn.draw(surf, menu_font, mouse_pos)
    p2_right_btn.draw(surf, menu_font, mouse_pos)
    back_btn.draw(surf, menu_font, mouse_pos)


def cycle_skin(idx, direction):
    return (idx + direction) % len(SKINS)


def handle_menu_click(pos):
    global state, running
    if start_btn.hit(pos):
        start_new_game()
    elif settings_btn.hit(pos):
        state = STATE_SETTINGS
    elif exit_btn.hit(pos):
        running = False


def handle_settings_click(pos):
    global state, p1_skin_idx, p2_skin_idx
    if p1_left_btn.hit(pos):
        p1_skin_idx = cycle_skin(p1_skin_idx, -1)
    elif p1_right_btn.hit(pos):
        p1_skin_idx = cycle_skin(p1_skin_idx, 1)
    elif p2_left_btn.hit(pos):
        p2_skin_idx = cycle_skin(p2_skin_idx, -1)
    elif p2_right_btn.hit(pos):
        p2_skin_idx = cycle_skin(p2_skin_idx, 1)
    elif back_btn.hit(pos):
        state = STATE_MENU


while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        if state == STATE_LOADING:
            pass  # ignore input during loading
        elif state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_menu_click(event.pos)
        elif state == STATE_SETTINGS:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_settings_click(event.pos)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_MENU
        elif state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = STATE_MENU
                elif event.key == Fighter1.controls["punch"]:
                    p1.start_punch()
                elif event.key == Fighter2.controls["punch"]:
                    p2.start_punch()
        elif state == STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    start_new_game()
                elif event.key == pygame.K_ESCAPE:
                    state = STATE_MENU

    # render
    if state == STATE_LOADING:
        elapsed_ms = pygame.time.get_ticks() - loading_started_at
        draw_loading(screen, elapsed_ms)
        if elapsed_ms >= LOADING_DURATION_MS:
            state = STATE_MENU
    elif state == STATE_MENU:
        draw_menu(screen, mouse_pos)
    elif state == STATE_SETTINGS:
        draw_settings(screen, mouse_pos)
    else:
        if state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            p1.handle_input(keys)
            p2.handle_input(keys)
            p1.update()
            p2.update()
            p1.try_hit(p2)
            p2.try_hit(p1)
            if p1.hp <= 0:
                winner = "Player 2"
                state = STATE_GAME_OVER
            elif p2.hp <= 0:
                winner = "Player 1"
                state = STATE_GAME_OVER

        screen.fill(SKY)
        p1.draw(screen)
        p2.draw(screen)
        draw_hp_bar(screen, p1.hp_location, p1.hp, "P1")
        draw_hp_bar(screen, p2.hp_location, p2.hp, "P2")

        if state == STATE_GAME_OVER:
            result_label = result_label_font.render(f"{winner} WINS! press R to restart", True, WHITE)
            screen.blit(result_label, result_label.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2)))

    pygame.display.flip()

pygame.quit()
