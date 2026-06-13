import pygame

from core import GAME_WIDTH, SKY, WHITE, Button, menu_font, title_font
from scenes.base import Scene

MENU_BTN_W, MENU_BTN_H = 320, 60


class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        x = GAME_WIDTH // 2 - MENU_BTN_W // 2
        self.start_btn = Button((x, 240, MENU_BTN_W, MENU_BTN_H), "START")
        self.settings_btn = Button((x, 320, MENU_BTN_W, MENU_BTN_H), "SETTINGS")
        self.exit_btn = Button((x, 400, MENU_BTN_W, MENU_BTN_H), "EXIT")

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.start_btn.hit(event.pos):
            from scenes.game_scene import GameScene
            self.manager.go_to(GameScene)
        elif self.settings_btn.hit(event.pos):
            from scenes.settings import SettingsScene
            self.manager.go_to(SettingsScene)
        elif self.exit_btn.hit(event.pos):
            self.manager.quit()

    def draw(self, surf):
        surf.fill(SKY)
        title = title_font.render("TEKKEN", True, WHITE)
        surf.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 130)))
        mouse_pos = pygame.mouse.get_pos()
        self.start_btn.draw(surf, menu_font, mouse_pos)
        self.settings_btn.draw(surf, menu_font, mouse_pos)
        self.exit_btn.draw(surf, menu_font, mouse_pos)
