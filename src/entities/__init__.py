from src.core.types import RequiredCost
from src.entities.archer import create_archer
from src.entities.arrow import create_arrow
from src.entities.ballista import create_ballista
from src.entities.bolt import create_bolt
from src.entities.casern import create_casern
from src.entities.farm import create_farm
from src.entities.fortress import create_fortress
from src.entities.warrior import create_warrior
from src.entities.workshop import create_workshop

entity_icons = {
    'fortress': 'assets/building/fortress/{color_name}.png',
    'arrow': 'assets/unit/archer/arrow.png',
    'archer': 'assets/unit/archer/{color_name}.png',
    'warrior': 'assets/unit/warrior/{color_name}.png',
    'casern': 'assets/building/casern/{color_name}.png',
    'farm': 'assets/building/farm/{color_name}.png',
    'workshop': 'assets/building/workshop/{color_name}.png',
    'ballista': 'assets/unit/ballista/{color_name}.png',
}

unit_production_factories = {
    'archer': create_archer,
    'warrior': create_warrior,
    'ballista': create_ballista,
}
building_factories = {
    'casern': create_casern,
    'farm': create_farm,
    'workshop': create_workshop,
}
buildings: dict[str: RequiredCost] = {
    'casern': RequiredCost(money=100, wood=50),
    'farm': RequiredCost(money=25, wood=100),
    'workshop': RequiredCost(money=200, wood=300),
}
projectiles = {
    'arrow': create_arrow,
    'bolt': create_bolt,
}
