from src.core.types import RequiredCost
from src.entities.archer import create_archer
from src.entities.arrow import create_arrow
from src.entities.fortress import create_fortress
from src.entities.warrior import create_warrior

entity_icons = {
    'fortress': 'assets/building/fortress/black.png',
    'arrow': 'assets/unit/archer/arrow.png',
    'archer': 'assets/unit/archer/black.png',
    'warrior': 'assets/unit/warrior/black.png',
}

unit_production_factories = {
    'archer': create_archer,
    'warrior': create_warrior,
}
building_factories = {
    'fortress': create_fortress,
}
buildings = {
    'fortress': RequiredCost(money=300, wood=100),
}
