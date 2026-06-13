import pygame

from core import GAME_HEIGHT, GAME_WIDTH, getFileAdd
from scenes.base import Scene

NAMES = [
    "Michael Minarčík",
    "Daniel Zikmund",
    "Jozef Waldhauser",
    "Peter Ivan",
]

LOADING_DURATION_MS = 3200
NAME_CYCLE_MS = 800
BLINK_MS = 300

# Reference layout from the original 1280x720 mockup — kept here so the
# magic numbers (288, 579, 704, 54) document where the loading bar sits in
# the background art before we scale it to the game resolution.
REF_W, REF_H = 1280, 720
REF_BAR = (288, 579, 704, 54)


def _scale_x(value):
    return round(value / REF_W * GAME_WIDTH)


def _scale_y(value):
    return round(value / REF_H * GAME_HEIGHT)


class LoadingScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        background = pygame.image.load(getFileAdd("assets/loadscreen.png")).convert()
        self.background = pygame.transform.smoothscale(background, (GAME_WIDTH, GAME_HEIGHT))

        self.name_font = pygame.font.SysFont("arial", _scale_y(34), bold=True)
        self.loading_font = pygame.font.SysFont("arial", _scale_y(24), bold=True)

        bx, by, bw, bh = REF_BAR
        self.bar_rect = pygame.Rect(_scale_x(bx), _scale_y(by), _scale_x(bw), _scale_y(bh))
        self.loading_text_y_offset = _scale_y(35)

        self.start_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.start_time >= LOADING_DURATION_MS:
            from scenes.menu import MenuScene
            self.manager.go_to(MenuScene)

    def draw(self, surf):
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(1.0, elapsed / LOADING_DURATION_MS)

        surf.blit(self.background, (0, 0))

        fill_w = int(self.bar_rect.width * progress)
        pygame.draw.rect(
            surf,
            (0, 170, 255),
            (self.bar_rect.x, self.bar_rect.y, fill_w, self.bar_rect.height),
        )
        pygame.draw.rect(surf, (255, 255, 255), self.bar_rect, 2)

        name = NAMES[(elapsed // NAME_CYCLE_MS) % len(NAMES)]
        name_color = (255, 255, 255) if (elapsed // BLINK_MS) % 2 == 0 else (180, 220, 255)
        name_surf = self.name_font.render(name, True, name_color)
        surf.blit(name_surf, name_surf.get_rect(center=self.bar_rect.center))

        text = f"LOADING... {int(progress * 100)}%"
        loading_surf = self.loading_font.render(text, True, (240, 240, 240))
        surf.blit(
            loading_surf,
            loading_surf.get_rect(center=(GAME_WIDTH // 2, self.bar_rect.bottom + self.loading_text_y_offset)),
        )
