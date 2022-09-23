from src.entities.archer import create_archer
from src.entities.arrow import create_arrow
from src.entities.fortress import create_fortress
from src.entities.warrior import create_warrior

entity_factories = {
    'arrow': create_arrow,
    'fortress': create_fortress,
    'archer': create_archer,
    'warrior': create_warrior,
}
entity_icons = {
    'fortress': 'assets/icon/fortress.png',
    'arrow': 'assets/icon/forge.png',
    'archer': 'assets/unit/archer/black.png',
    'warrior': 'assets/unit/warrior/black.png',
}
