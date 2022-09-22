from src.entities.arrow import create_arrow
from src.entities.fortress import create_fortress

entity_factories = {
    'arrow': create_arrow,
    'fortress': create_fortress
}
entity_icons = {
    'fortress': 'assets/icon/fortress.png',
    'arrow': 'assets/icon/forge.png',
}
