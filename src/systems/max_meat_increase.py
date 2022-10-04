from src.components.base.player_owner import PlayerOwnerComponent
from src.components.meat import MaxMeatIncreaseComponent
from src.core.types import PlayerInfo
from src.server.action_sender import ServerActionSender


def max_meat_increase_system(meat_increase: MaxMeatIncreaseComponent, owner: PlayerOwnerComponent,
                             action_sender: ServerActionSender,
                             players: dict[int, PlayerInfo]):
    if meat_increase.increased:
        return

    owner_info = players[owner.socket_id]

    owner_info.resources.max_meat += meat_increase.meat_amount
    meat_increase.increased = True

    action_sender.update_resource_info(owner_info)
