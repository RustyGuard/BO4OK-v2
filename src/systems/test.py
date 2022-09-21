from src.components.test import BComponent, CComponent


def test_a_system(entity_id: str, a: int):
    print('test_a_system', entity_id, a)


def test_b_system(entity_id: str, b: BComponent):
    print('test_b_system', entity_id, b.value)


def test_bc_system(entity_id: str, b: BComponent, c: CComponent, a: int):
    print('test_bc_system', entity_id, b.value, c.value, a)
