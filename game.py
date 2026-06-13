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

GAME_WIDTH = 1000
GAME_HEIGHT = 600
FPS = 30

GRAVITY = 1.2
JUMP_V = -18
MOVE_SPEED = 5

GROUND_Y = GAME_HEIGHT - 90
FIGHTER_SCALE = 0.7

# Fighter prit sheet
SHEET_FRAME_WIDTH = 192
STATIC_ROW_Y = 60
MOTION_ROW_Y = 420
FIGHTER_SPRITE_HEIGHT = 280
FRAME_INDICES = [0, 3, 7]  # we are only using state 1, 4, 8 from the generated sprite sheet

# start pygame
pygame.init()

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Tekken")
clock = pygame.time.Clock()

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


spritesheet = pygame.image.load(getFileAdd("fighter.png"))
static_frames_p1 = load_spritesheet_strip(spritesheet, STATIC_ROW_Y)
motion_frames_p1 = load_spritesheet_strip(spritesheet, MOTION_ROW_Y)
static_frames_p2 = [pygame.transform.flip(f, True, False) for f in static_frames_p1]
motion_frames_p2 = [pygame.transform.flip(f, True, False) for f in motion_frames_p1]


def build_platform_surface():
    surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT - GROUND_Y), pygame.SRCALPHA)
    surf.fill(GROUND_MID)
    pygame.draw.rect(surf, GROUND_TOP, (0, 0, GAME_WIDTH, 8))
    pygame.draw.rect(surf, GROUND_DARK, (0, surf.get_height() - 10, GAME_WIDTH, 10))
    for x in range(0, GAME_WIDTH, 40):
        pygame.draw.line(surf, GROUND_DARK, (x, 8), (x, surf.get_height() - 10), 2)
    return surf


platform_surf = build_platform_surface()

class FighterBase():
    def __init__(self, x, facing_right, controls):
        self.x = x
        self.y = GROUND_Y
        self.vy = 0
        self.on_ground = True
        self.facing_right = facing_right
        self.controls = controls
        self.hp = 100

        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 6

        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = 12
        self.has_hit = False

        self.w = static_frames_p1[0].get_width()
        self.h = static_frames_p1[0].get_height()

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
        if self.is_punching:
            frames = motion_frames_p1 if self.facing_right else motion_frames_p2
        else:
            frames = static_frames_p1 if self.facing_right else static_frames_p2
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
    def __init__(self):
        super().__init__(250, True, self.controls)

class Fighter2(FighterBase):
    controls = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "punch": pygame.K_RSHIFT,
    }

    def __init__(self):
        super().__init__(750, True, self.controls)

p1 = Fighter1()
p2 = Fighter2()

hud_font = pygame.font.SysFont("monospace", 18, bold=True)


def draw_hp_bar(surf, x, y, hp, label):
    w, h = 360, 18
    pygame.draw.rect(surf, HP_BG, (x, y, w, h))
    pygame.draw.rect(surf, HP_FG, (x, y, int(w * hp / 100), h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)
    surf.blit(hud_font.render(f"{label}: {hp}", True, WHITE), (x, y + h + 4))


running = True
winner = None

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == Fighter1.controls["punch"]:
                p1.start_punch()
            if event.key == Fighter2.controls["punch"]:
                p2.start_punch()
            if winner and event.key == pygame.K_r:
                p1 = Fighter1()
                p2 = Fighter2()
                winner = None

    if not winner:
        keys = pygame.key.get_pressed()
        p1.handle_input(keys)
        p2.handle_input(keys)

        p1.update()
        p2.update()
        p1.try_hit(p2)
        p2.try_hit(p1)

        if p1.hp <= 0:
            winner = "Player 2"
        elif p2.hp <= 0:
            winner = "Player 1"

    # render
    screen.fill(SKY)
    # vzdálené hory / pozadí
    pygame.draw.polygon(screen, (60, 40, 80), [(0, GROUND_Y), (200, 300), (400, GROUND_Y)])
    pygame.draw.polygon(screen, (50, 30, 70), [(300, GROUND_Y), (550, 250), (800, GROUND_Y)])
    pygame.draw.polygon(screen, (60, 40, 80), [(600, GROUND_Y), (850, 320), (GAME_WIDTH, GROUND_Y)])

    screen.blit(platform_surf, (0, GROUND_Y))

    p1.draw(screen)
    p2.draw(screen)

    draw_hp_bar(screen, 30, 20, p1.hp, "P1")
    draw_hp_bar(screen, GAME_WIDTH - 390, 20, p2.hp, "P2")

    if winner:
        result_label_font = pygame.font.SysFont("monospace", 48, bold=True)
        result_label = result_label_font.render(f"{winner} WINS! press R to restart game", True, WHITE)
        result_label.get_rect().center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
        screen.blit(result_label, result_label.get_rect())

    pygame.display.flip()

pygame.quit()
