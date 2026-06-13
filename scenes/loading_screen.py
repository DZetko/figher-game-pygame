import os
import pygame


pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Loading Screen")
clock = pygame.time.Clock()

names = [
    "Michael Minarčík",
    "Daniel Zikmund",
    "Jozef Waldhauser",
    "Petr Archonax",
]

# Délka loadingu 
duration_ms = 4000

# Načtení obrázku
current_folder = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_folder, "loadscreen.png")

background = pygame.image.load(image_path).convert()
background = pygame.transform.smoothscale(background, (1280, 720))

name_font = pygame.font.SysFont("arial", 34, bold=True)
loading_font = pygame.font.SysFont("arial", 24, bold=True)

# Loading bar
bar_rect = pygame.Rect(288, 579, 704, 54)

start_time = pygame.time.get_ticks()
running = True

while running:
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time

    progress = elapsed_time / duration_ms
    progress = min(progress, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Pozadí
    screen.blit(background, (0, 0))

    # Vyplnění loading baru
    fill_width = int(bar_rect.width * progress)
    fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)

    pygame.draw.rect(screen, (0, 170, 255), fill_rect)
    pygame.draw.rect(screen, (255, 255, 255), bar_rect, 2)

    # Střídání jmen
    name_index = (elapsed_time // 1100) % len(names)
    current_name = names[name_index]

    # Blikání barvy jména
    if (elapsed_time // 300) % 2 == 0:
        name_color = (255, 255, 255)
    else:
        name_color = (180, 220, 255)

    # Vykreslení jména
    name_surface = name_font.render(current_name, True, name_color)
    name_rect = name_surface.get_rect(center=bar_rect.center)
    screen.blit(name_surface, name_rect)

    # Vykreslení procent
    loading_text = f"LOADING... {int(progress * 100)}%"
    loading_surface = loading_font.render(loading_text, True, (240, 240, 240))
    loading_rect = loading_surface.get_rect(center=(640, bar_rect.bottom + 35))
    screen.blit(loading_surface, loading_rect)

    pygame.display.flip()
    clock.tick(60)

    if progress >= 1:
        running = False

pygame.quit()