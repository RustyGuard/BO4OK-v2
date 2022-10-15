from enum import Enum

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
    POPUP = 7
    SOUND = 8


class SoundCode(Enum):
    SWORD_SLASH = 'assets/music/sword_slash.wav'
    ARROW_THROW = 'assets/music/arrow_throw.wav'
    ARROW_CONTACT = 'assets/music/arrow_contact.wav'
    WOOD_CHOP = 'assets/music/wood_chop.wav'
    PICKAXE_SWIPE = 'assets/music/pickaxe_swipe.wav'
    CONSTRUCTION_COMPLETED = 'assets/music/construction_completed.ogg'


class ServerCommands:
    """Команды, отправляемые серверу"""
    PLACE_UNIT = 1
    SET_TARGET_MOVE = 2
    PRODUCE_UNIT = 3
