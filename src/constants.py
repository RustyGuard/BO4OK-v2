from pygame import Color

EVENT_UPDATE = 27
EVENT_SEC = 28

color_name_to_pygame_color = {
    'aqua': Color('aquamarine'),
    'blue': Color('blue'),
    'green': Color('green'),
    'light_green': Color('green2'),
    'orange': Color('orange'),
    'pink': Color('pink'),
    'purple': Color('purple'),
    'red': Color('red'),
    'yellow': Color('yellow'),
    'black': Color('black')
}


class ClientCommands:
    """Команды, отправляемые клиенту"""
    CREATE = 1
    UPDATE = 2
    TARGET_CHANGE = 3
    RESOURCE_INFO = 4
    COMPONENT_INFO = 5
    DEAD = 6
    DAMAGE = 7


class ServerCommands:
    """Команды, отправляемые серверу"""
    PLACE_UNIT = 1
    SET_TARGET_MOVE = 2
    PRODUCE_UNIT = 3
