from src.ui import UIElement

main_element: UIElement | None = None
is_running = True


def set_main_element(element: UIElement):
    global main_element
    if main_element is not None:
        main_element.shutdown()
    main_element = element


def close_game():
    global is_running
    is_running = False
    if main_element is not None:
        main_element.shutdown()
