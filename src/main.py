import pygame
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.time import Clock

from src import main_loop_state
from src.config import config
from src.constants import EVENT_SEC, EVENT_UPDATE
from src.main_loop_state import set_main_element, close_game


def run_main_loop(screen: Surface):
    clock = Clock()

    pygame.time.set_timer(EVENT_UPDATE, 1000 // 60)
    pygame.time.set_timer(EVENT_SEC, 1000 // 1)

    try:
        while main_loop_state.is_running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    close_game()

                main_loop_state.main_element.update(event)

            screen.fill((0, 0, 0))
            main_loop_state.main_element.render(screen)

            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        close_game()


def main():
    from src.menus.main_menu import MainMenu

    pygame.init()
    screen = config.screen.update_display_mode()

    set_main_element(MainMenu())

    run_main_loop(screen)


if __name__ == '__main__':
    main()
