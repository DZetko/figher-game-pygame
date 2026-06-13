import pygame

from core import GAME_HEIGHT, GAME_WIDTH, Button, getFileAdd, menu_font
from scenes.base import Scene

MENU_BTN_W, MENU_BTN_H = 320, 60


class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        background = pygame.image.load(getFileAdd("assets/mainmenu.png")).convert()
        self.background = pygame.transform.smoothscale(background, (GAME_WIDTH, GAME_HEIGHT))

        x = GAME_WIDTH // 2 - MENU_BTN_W // 2
        self.start_btn = Button((x, 340, MENU_BTN_W, MENU_BTN_H), "START")
        self.settings_btn = Button((x, 420, MENU_BTN_W, MENU_BTN_H), "SETTINGS")
        self.exit_btn = Button((x, 500, MENU_BTN_W, MENU_BTN_H), "EXIT")

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
        surf.blit(self.background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        self.start_btn.draw(surf, menu_font, mouse_pos)
        self.settings_btn.draw(surf, menu_font, mouse_pos)
        self.exit_btn.draw(surf, menu_font, mouse_pos)
