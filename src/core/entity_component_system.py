import inspect
import time
from typing import Callable, Type, Any, Iterator

from src.core.types import EntityId, Component, StoredSystem
from src.systems.test import test_bc_system
from src.utils.unique_id import UniqueIdGenerator


class EntityComponentSystem:
    SPECIAL_ARGUMENTS = ('entity_id', 'ecs')

    def __init__(self, on_create: Callable[[EntityId, list[Component]], None] = None,
                 on_remove: Callable[[EntityId], None] = None):
        self.systems: dict[Callable, StoredSystem] = {}
        self._components: dict[Type[Component], dict[EntityId, Component]] = {}
        self._entities: list[EntityId] = []
        self._vars = {}
        self.on_create = on_create
        self.on_remove = on_remove

    def _unsafe_get_component(self, entity_id: str, component_class: Type[Component]) -> Component:
        return self._components[component_class][entity_id]

    def init_component(self, component_class: Type[Component]) -> None:
        self._components[component_class] = {}

    def init_system(self, system: Callable):
        stored_system = StoredSystem(
            components={},
            variables={},
            has_entity_id_argument=False,
            has_ecs_argument=False
        )

        system_params = inspect.signature(system).parameters
        for param_name, param in system_params.items():
            if param_name == 'entity_id':
                stored_system.has_entity_id_argument = True

            elif param_name == 'ecs':
                stored_system.has_ecs_argument = True

            elif param.annotation in self._components:
                stored_system.components[param_name] = param.annotation

            elif param_name in self._vars:
                stored_system.variables[param_name] = self._vars[param_name]

            else:
                raise Exception(f'Wrong argument: {param_name}')

        self.systems[system] = stored_system

    def add_variable(self, variable_name: str, variable_value: Any) -> None:
        self._vars[variable_name] = variable_value

    def create_entity(self, components: list[Component], entity_id=None) -> EntityId:
        if entity_id is None:
            entity_id = UniqueIdGenerator.generate_id()
        else:
            assert entity_id not in self._entities, f"Entity with id {entity_id} already exists"

        for component in components:
            self._components[component.__class__][entity_id] = component
        self._entities.append(entity_id)

        if self.on_create:
            self.on_create(entity_id, components)

        return entity_id

    def get_entity_ids_with_components(self, component_classes: tuple[Type[Component], ...]) -> set[EntityId]:
        if not component_classes:
            return set(self._entities)

        entities = set.intersection(
            *[set(self._components[component_class]) for component_class in component_classes])
        return entities

    def get_entities_with_components(self, component_classes: list[Type[Component]]) -> \
            Iterator[tuple[EntityId, list[Component]]]:
        for entity_id in self.get_entity_ids_with_components(component_classes):
            components = tuple(self._components[component_class][entity_id] for component_class in component_classes)
            yield entity_id, components

    def update(self) -> None:
        for system_function, system in self.systems.items():
            for entity_id in self.get_entity_ids_with_components(list(system.components.values())):
                special_args = {}
                if system.has_ecs_argument:
                    special_args['ecs'] = self
                if system.has_entity_id_argument:
                    special_args['entity_id'] = entity_id
                system_function(
                    **{param: self._unsafe_get_component(entity_id, component_name) for param, component_name in
                       system.components.items()} | system.variables | special_args)

    def remove_entity(self, entity_id: EntityId):
        if self.on_remove is not None:
            self.on_remove(entity_id)
        for components in self._components.values():
            components.pop(entity_id, None)
        self._entities.remove(entity_id)

    def get_component(self, entity_id: EntityId, component_class: Type[Component]):
        return self._components[component_class].get(entity_id, None)

    def get_components(self, entity_id: EntityId,
                       component_classes):
        try:
            return tuple(
                self._unsafe_get_component(entity_id, component_class) for component_class in component_classes)
        except KeyError:
            return None


def test():
    from src.components.test import BComponent, CComponent
    from src.systems.test import test_a_system, test_b_system

    ecs = EntityComponentSystem()
    ecs.add_variable('a', 150)

    ecs.init_component(BComponent)
    ecs.init_component(CComponent)

    ecs.init_system(test_a_system)
    ecs.init_system(test_b_system)
    ecs.init_system(test_bc_system)

    ecs.create_entity([])
    ecs.create_entity([])
    ecs.create_entity([BComponent(value=42)])
    ecs.create_entity([BComponent(value=42), CComponent(value=69)])

    ecs.update()

    assert sorted(ecs.get_entities_with_components((BComponent,))) == [('3', (BComponent(value=42),)),
                                                                       ('4', (BComponent(value=42),))]
    assert next(ecs.get_entities_with_components((BComponent, CComponent))) == ('4', (BComponent(value=42), CComponent(value=69)))


if __name__ == '__main__':
    test()
