import os

import pygame


def getFileAdd(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, file_name)


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

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Tekken")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("monospace", 64, bold=True)
menu_font = pygame.font.SysFont("monospace", 32, bold=True)
label_font = pygame.font.SysFont("monospace", 24, bold=True)
hud_font = pygame.font.SysFont("monospace", 18, bold=True)
result_label_font = pygame.font.SysFont("monospace", 48, bold=True)


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


class GameState:
    def __init__(self):
        self.p1_fighter_skin = 0
        self.p2_fighter_skin = 1


class SceneManager:
    def __init__(self):
        self.current = None
        self.state = GameState()
        self.running = True

    def go_to(self, scene_cls):
        self.current = scene_cls(self)

    def quit(self):
        self.running = False
