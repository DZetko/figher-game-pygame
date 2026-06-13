import pygame

from core import FPS, SceneManager, clock, screen
from scenes.loading import LoadingScene


manager = SceneManager()
manager.go_to(LoadingScene)

while manager.running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            manager.quit()
            continue
        manager.current.handle_event(event)
    manager.current.update()
    manager.current.draw(screen)
    pygame.display.flip()

pygame.quit()
