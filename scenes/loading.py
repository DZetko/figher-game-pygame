import pygame

from core import BLACK, BTN_BG, GAME_HEIGHT, GAME_WIDTH, HP_FG, WHITE, label_font, title_font
from scenes.base import Scene

LOADING_DURATION_MS = 3000


class LoadingScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.started_at = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.started_at >= LOADING_DURATION_MS:
            from scenes.menu import MenuScene
            self.manager.go_to(MenuScene)

    def draw(self, surf):
        surf.fill(BLACK)
        title = title_font.render("TEKKEN", True, WHITE)
        surf.blit(title, title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 30)))

        elapsed = pygame.time.get_ticks() - self.started_at
        progress = min(1.0, elapsed / LOADING_DURATION_MS)
        bar_w, bar_h = 360, 16
        bar_x = GAME_WIDTH // 2 - bar_w // 2
        bar_y = GAME_HEIGHT // 2 + 40
        pygame.draw.rect(surf, BTN_BG, (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, HP_FG, (bar_x, bar_y, int(bar_w * progress), bar_h))
        pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)

        loading_label = label_font.render("Loading...", True, WHITE)
        surf.blit(loading_label, loading_label.get_rect(center=(GAME_WIDTH // 2, bar_y + 50)))
