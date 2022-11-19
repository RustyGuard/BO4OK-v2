from functools import partial
from typing import Callable

from pygame import Color
from pygame.font import Font

from src.config import config
from src.core.types import ConnectedPlayer
from src.ui import UIAnchor, UIElement, BorderParams
from src.ui.button import UIButton
from src.ui.image import UIImage
from src.ui.text_label import TextLabel


class PlayersListElement(UIElement):
    PLAYER_AMOUNT_MASK = 'Подключено игроков: {current_amount}'

    def __init__(self, font: Font, connected_players: list[ConnectedPlayer],
                 kick_player: Callable[[ConnectedPlayer], None] = None):
        super().__init__()
        self.font = font
        self.connected_players = connected_players

        self.kick_player = kick_player

    def update_players(self):
        self.children.clear()

        self.players_count = TextLabel(text=self.PLAYER_AMOUNT_MASK.format(current_amount=1), text_color=Color('white'),
                                       font=self.font,
                                       position=config.screen.rect.move(0, -175).center,
                                       anchor=UIAnchor.CENTER)
        self.append_child(self.players_count)

        offset_y = -125
        for i, player in enumerate(self.connected_players):
            player_box = UIElement(position=config.screen.rect.move(0, offset_y + i * 35).center, size=(500, 30),
                                   anchor=UIAnchor.CENTER, background_color=Color('gray'))
            self.append_child(player_box)
            self.append_child(
                UIElement(position=player_box.bounds.move(15, 0).midleft, size=(24, 24), anchor=UIAnchor.CENTER,
                          background_color=player.color, border_params=BorderParams(
                        width=1
                    )))
            self.append_child(TextLabel(text=player.nick,
                                        font=self.font,
                                        position=config.screen.rect.move(0, offset_y - 2 + i * 35).center,
                                        size=(400, 25),
                                        anchor=UIAnchor.CENTER))

            if (self.kick_player is not None) and player.kickable:
                remove_button = UIButton(position=player_box.bounds.move(-15, 0).midright, size=(24, 24),
                                         anchor=UIAnchor.CENTER, on_click=partial(self.kick_player, player))
                self.append_child(remove_button)
                self.append_child(UIImage(image='assets/ui/cross.png',
                                          position=remove_button.bounds.topleft,
                                          size=remove_button.bounds.size))
                remove_button.on_mouse_hover = partial(remove_button.set_background_color, Color('darkred'))
                remove_button.on_mouse_exit = partial(remove_button.set_background_color, None)
