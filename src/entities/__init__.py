from src.core.types import RequiredCost
from src.entities.archer import create_archer
from src.entities.arrow import create_arrow
from src.entities.casern import create_casern
from src.entities.fortress import create_fortress
from src.entities.warrior import create_warrior

entity_icons = {
    'fortress': 'assets/building/fortress/{color_name}.png',
    'arrow': 'assets/unit/archer/arrow.png',
    'archer': 'assets/unit/archer/{color_name}.png',
    'warrior': 'assets/unit/warrior/{color_name}.png',
    'casern': 'assets/building/casern/{color_name}.png'
}

unit_production_factories = {
    'archer': create_archer,
    'warrior': create_warrior,
}
building_factories = {
    'casern': create_casern,
}
buildings = {
    'casern': RequiredCost(money=100, wood=50),
}
