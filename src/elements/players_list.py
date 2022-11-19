from functools import partial
from typing import Callable

from pygame import Color, Rect
from pygame.font import Font

from src.config import config
from src.core.types import ConnectedPlayer
from src.ui import UIElement
from src.ui.button import UIButton
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class PlayersListElement(UIElement):
    PLAYER_AMOUNT_MASK = 'Подключено игроков: {current_amount}'

    def __init__(self, font: Font, connected_players: list[ConnectedPlayer], kick_player: Callable[[ConnectedPlayer], None] = None):
        super().__init__()
        self.font = font
        self.connected_players = connected_players

        self.kick_player = kick_player

    def update_players(self):
        self.children.clear()

        self.players_count = TextLabel(None, Color('white'), self.font,
                                       self.PLAYER_AMOUNT_MASK.format(current_amount=1),
                                       center=config.screen.rect.move(0, -175).center)
        self.append_child(self.players_count)

        offset_y = -125
        for i, player in enumerate(self.connected_players):
            player_box = UIElement(Rect(0, 0, 500, 30), Color('gray'),
                                   center=config.screen.rect.move(0, offset_y + i * 35).center)
            self.append_child(player_box)
            self.append_child(
                UIElement(Rect((0, 0), (24, 24)), color=player.color, border_width=1,
                          center=player_box.bounds.move(15, 0).midleft))
            self.append_child(
                TextLabel(Rect(0, 0, 400, 25), Color('black'), self.font, player.nick,
                          center=config.screen.rect.move(0, offset_y - 2 + i * 35).center))

            if (self.kick_player is not None) and player.kickable:
                remove_button = UIButton(Rect((0, 0), (24, 24)), None, partial(self.kick_player, player),
                                         center=player_box.bounds.move(-15, 0).midright)
                self.append_child(remove_button)
                self.append_child(UIImage(remove_button.bounds.copy(), 'assets/ui/cross.png'))
                remove_button.on_mouse_hover = partial(remove_button.set_color, Color('darkred'))
                remove_button.on_mouse_exit = partial(remove_button.set_color, None)
