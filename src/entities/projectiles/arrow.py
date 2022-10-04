from src.components.base.decay import DecayComponent
from src.components.base.player_owner import PlayerOwnerComponent
from src.components.base.position import PositionComponent
from src.components.base.texture import TextureComponent
from src.components.base.velocity import VelocityComponent
from src.components.fighting.damage_on_contact import DamageOnContactComponent


def create_arrow(x: float, y: float, owner: PlayerOwnerComponent, angle: int, speed: float = 2):
    return [
        PositionComponent(x, y),
        owner,
        VelocityComponent.create_from_polar_coordinates(speed, angle),
        DecayComponent(150),
        TextureComponent.create_from_filepath('assets/unit/archer/arrow.png', rotation_angle=angle),
        DamageOnContactComponent(10)
    ]
