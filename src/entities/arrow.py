from src.components.damage_on_contact import DamageOnContactComponent
from src.components.decay import DecayComponent
from src.components.player_owner import PlayerOwnerComponent
from src.components.position import PositionComponent
from src.components.texture import TextureComponent
from src.components.velocity import VelocityComponent


def create_arrow(x: float, y: float, owner: PlayerOwnerComponent, angle: int, speed: float = 2):
    return [
        PositionComponent(x, y),
        owner,
        VelocityComponent.create_from_polar_coordinates(speed, angle),
        DecayComponent(150),
        TextureComponent.create_from_filepath('assets/unit/archer/arrow.png', rotation_angle=angle),
        DamageOnContactComponent(10)
    ]
