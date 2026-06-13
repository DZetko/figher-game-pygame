import pygame

import assets
from assets import FIGHTERS
from core import (
    GAME_HEIGHT,
    GAME_WIDTH,
    GRAVITY,
    GROUND_Y,
    HP_BG,
    HP_FG,
    JUMP_V,
    MOVE_SPEED,
    WHITE,
    getFileAdd,
    hud_font,
    result_label_font,
)
from scenes.base import Scene
from scenes.settings import START_TUNE_PATH


class FighterBase:
    def __init__(self, x, facing_right, controls, hp_location, fighter_idx):
        self.is_blocking = False
        self.x = x
        self.y = GROUND_Y
        self.vy = 0
        self.on_ground = True
        self.facing_right = facing_right
        self.controls = controls
        self.hp_location: tuple[int, int] = hp_location
        self.fighter_idx = fighter_idx
        self.frames = FIGHTERS[fighter_idx]["frames"]
        self.hp = 100

        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_delay = 6

        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = 12
        self.has_hit = False

        self.w = self.frames["static_right"][0].get_width()
        self.h = self.frames["static_right"][0].get_height()

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
        self.is_blocking = bool(keys[self.controls["block"]])
        if self.is_blocking:
            return  # locked in place while blocking
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
        self.is_blocking = False
        self.is_punching = True
        self.punch_timer = 0
        self.frame_idx = 0
        self.frame_timer = 0
        self.has_hit = False

    def update(self):
        if not self.on_ground:
            self.vy += GRAVITY
            self.y += self.vy
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.vy = 0
                self.on_ground = True

        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames["static_right"])

        if self.is_punching:
            self.punch_timer += 1
            if self.punch_timer >= self.punch_duration:
                self.is_punching = False
                self.frame_idx = 0

    def try_hit(self, other):
        if not self.is_punching or self.has_hit or other.is_blocking:
            return
        if self.punch_timer < self.punch_duration // 3:
            return
        if self.hit_rect().colliderect(other.rect()):
            other.hp = max(0, other.hp - 8)
            self.has_hit = True

    def draw(self, surf):
        direction = "right" if self.facing_right else "left"
        if self.hp <= 0:
            frames = self.frames[f"dead_{direction}"]
            img = frames[-1]  # freeze on final dead pose
        elif self.is_blocking:
            img = self.frames[f"block_{direction}"][0]
        else:
            state = "motion" if self.is_punching else "static"
            frames = self.frames[f"{state}_{direction}"]
            img = frames[self.frame_idx % len(frames)]
        rect = img.get_rect()
        if self.is_blocking:
            rect.midbottom = (int(self.x), int(self.y + 20))
        else:
            rect.midbottom = (int(self.x), int(self.y))
        surf.blit(img, rect)


class Fighter1(FighterBase):
    controls = {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "punch": pygame.K_f,
        "block": pygame.K_s
    }

    def __init__(self, fighter_idx=0):
        super().__init__(250, True, self.controls, (30, 20), fighter_idx)


class Fighter2(FighterBase):
    controls = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "punch": pygame.K_RSHIFT,
        "block": pygame.K_DOWN
    }

    def __init__(self, fighter_idx=0):
        super().__init__(750, False, self.controls, (GAME_WIDTH - 390, 20), fighter_idx)


def draw_hp_bar(surf, location, hp, label):
    x, y = location
    w, h = 360, 18
    pygame.draw.rect(surf, HP_BG, (x, y, w, h))
    pygame.draw.rect(surf, HP_FG, (x, y, int(w * hp / 100), h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)
    surf.blit(hud_font.render(f"{label}: {hp}", True, WHITE), (x, y + h + 4))


BG_CYCLE_AFTER_MILLISECONDS = 220

class GameScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.winner = None
        self.background_idx = 0
        self.next_background_cycle = pygame.time.get_ticks() + BG_CYCLE_AFTER_MILLISECONDS
        self.reset()

    def reset(self):
        state = self.manager.state
        self.p1 = Fighter1(state.p1_fighter_skin)
        self.p2 = Fighter2(state.p2_fighter_skin)
        self.winner = None
        pygame.mixer.music.load(START_TUNE_PATH)
        pygame.mixer.music.play()

    def cycle_background(self):
        self.background_idx = (self.background_idx + 1) % len(assets.game_backgrounds)
        self.next_background_cycle = pygame.time.get_ticks() + BG_CYCLE_AFTER_MILLISECONDS

    def _back_to_menu(self):
        from scenes.menu import MenuScene
        self.manager.go_to(MenuScene)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self._back_to_menu()
            return
        if self.winner:
            if event.key == pygame.K_r:
                self.reset()
                self.winner = None
            return
        if event.key == Fighter1.controls["punch"]:
            self.p1.start_punch()
        elif event.key == Fighter2.controls["punch"]:
            self.p2.start_punch()

    def update(self):
        if self.winner:
            return
        if pygame.time.get_ticks() >= self.next_background_cycle:
            self.cycle_background()

        keys = pygame.key.get_pressed()
        self.p1.handle_input(keys)
        self.p2.handle_input(keys)
        self.p1.update()
        self.p2.update()
        self.p1.try_hit(self.p2)
        self.p2.try_hit(self.p1)
        if self.p1.hp <= 0:
            self.winner = "Player 2"
        elif self.p2.hp <= 0:
            self.winner = "Player 1"

    def draw(self, surf):
        surf.blit(assets.game_backgrounds[self.background_idx], (0, 0))
        self.p1.draw(surf)
        self.p2.draw(surf)
        draw_hp_bar(surf, self.p1.hp_location, self.p1.hp, "P1")
        draw_hp_bar(surf, self.p2.hp_location, self.p2.hp, "P2")
        if self.winner:
            label = result_label_font.render(f"{self.winner} WINS! press R to restart", True, WHITE)
            surf.blit(label, label.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2)))
