import pygame

from assets import FIGHTERS
from core import GAME_HEIGHT, GAME_WIDTH, WHITE, Button, hud_font, label_font, menu_font, title_font, getFileAdd
from scenes.base import Scene

ARROW_W, ARROW_H = 50, 50
ARROWS_Y = 420
START_TUNE_PATH = getFileAdd("assets/start_tune.mp3")
JUMP_SOUND_PATH = getFileAdd("assets/jump.mp3")
JUMP_SOUND_PROBABILITY = 0.5

class SettingsScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        background = pygame.image.load(getFileAdd("assets/menubackground.png")).convert()
        self.background = pygame.transform.smoothscale(background, (GAME_WIDTH, GAME_HEIGHT))

        self.p1_x = GAME_WIDTH // 4
        self.p2_x = 3 * GAME_WIDTH // 4
        self.p1_left = Button((self.p1_x - 110, ARROWS_Y, ARROW_W, ARROW_H), "<")
        self.p1_right = Button((self.p1_x + 60, ARROWS_Y, ARROW_W, ARROW_H), ">")
        self.p2_left = Button((self.p2_x - 110, ARROWS_Y, ARROW_W, ARROW_H), "<")
        self.p2_right = Button((self.p2_x + 60, ARROWS_Y, ARROW_W, ARROW_H), ">")
        self.back_btn = Button((GAME_WIDTH // 2 - 100, 510, 200, 50), "BACK")

    def _back_to_menu(self):
        from scenes.menu import MenuScene
        self.manager.go_to(MenuScene)

    @staticmethod
    def _wrap(idx, direction):
        return (idx + direction) % len(FIGHTERS)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._back_to_menu()
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        state = self.manager.state
        if self.p1_left.hit(event.pos):
            state.p1_fighter_skin = self._wrap(state.p1_fighter_skin, -1)
        elif self.p1_right.hit(event.pos):
            state.p1_fighter_skin = self._wrap(state.p1_fighter_skin, 1)
        elif self.p2_left.hit(event.pos):
            state.p2_fighter_skin = self._wrap(state.p2_fighter_skin, -1)
        elif self.p2_right.hit(event.pos):
            state.p2_fighter_skin = self._wrap(state.p2_fighter_skin, 1)
        elif self.back_btn.hit(event.pos):
            self._back_to_menu()

    def _draw_player_column(self, surf, label, x, fighter_idx):
        label_img = label_font.render(label, True, WHITE)
        surf.blit(label_img, label_img.get_rect(center=(x, 150)))

        fighter = FIGHTERS[fighter_idx % len(FIGHTERS)]
        preview = fighter["frames"]["static_right"][0]
        surf.blit(preview, preview.get_rect(center=(x, 290)))

        name_img = hud_font.render(fighter["name"], True, WHITE)
        surf.blit(name_img, name_img.get_rect(center=(x, ARROWS_Y + ARROW_H // 2)))

    def draw(self, surf):
        surf.blit(self.background, (0, 0))
        title = title_font.render("SETTINGS", True, WHITE)
        surf.blit(title, title.get_rect(center=(GAME_WIDTH // 2, 50)))

        state = self.manager.state
        self._draw_player_column(surf, "Player 1", self.p1_x, state.p1_fighter_skin)
        self._draw_player_column(surf, "Player 2", self.p2_x, state.p2_fighter_skin)

        mouse_pos = pygame.mouse.get_pos()
        self.p1_left.draw(surf, menu_font, mouse_pos)
        self.p1_right.draw(surf, menu_font, mouse_pos)
        self.p2_left.draw(surf, menu_font, mouse_pos)
        self.p2_right.draw(surf, menu_font, mouse_pos)
        self.back_btn.draw(surf, menu_font, mouse_pos)
