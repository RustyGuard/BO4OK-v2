from typing import Protocol, Type, TypeVar, overload, Callable, Any, Iterator

from src.core.types import EntityId, Component, StoredSystem

Component1 = TypeVar('Component1')
Component2 = TypeVar('Component2')
Component3 = TypeVar('Component3')
Component4 = TypeVar('Component4')


class EntityComponentSystem(Protocol):
    systems: dict[Callable, StoredSystem]
    components: dict[Type[Component], dict[EntityId, Component]]
    entities: list[EntityId]

    vars: dict[str, Any]
    on_create: Callable[[EntityId, list[Component]], None]
    on_remove: Callable[[EntityId], None]

    def __init__(self, on_create: Callable[[EntityId, list[Component]], None] = None,
                 on_remove: Callable[[EntityId], None] = None): ...

    @overload
    def _get_component(self, entity_id: str, component_class: Type[Component1]) -> Component1: ...

    @overload
    def init_component(self, component_class: Type[Component1]) -> None: ...

    @overload
    def init_system(self, system: Callable): ...

    @overload
    def add_variable(self, variable_name: str, variable_value: Any) -> None: ...

    @overload
    def create_entity(self, components: list[Component1], entity_id=None) -> EntityId: ...

    @overload
    def get_entity_ids_with_components(self, component_classes: list[Type[Component1]]) -> set[EntityId]: ...

    @overload
    def get_entities_with_components(self, component_classes: tuple[Type[Component1]]) -> Iterator[tuple[
        EntityId, tuple[Component1]]]: ...

    @overload
    def get_entities_with_components(self, component_classes: tuple[Type[Component1], Type[Component2]]) -> Iterator[
        tuple[
            EntityId, tuple[Component1, Component2]]]: ...

    @overload
    def get_entities_with_components(self,
                                     component_classes: tuple[Type[Component1], Type[Component2], Type[Component3]]) -> \
    Iterator[tuple[
        EntityId, tuple[Component1, Component2, Component3]]]: ...

    @overload
    def get_entities_with_components(self, component_classes: tuple[
        Type[Component1], Type[Component2], Type[Component3], Type[Component4]]) -> Iterator[tuple[
        EntityId, tuple[Component1, Component2, Component3, Component4]]]: ...

    def update(self) -> None: ...

    def remove_entity(self, entity_id: EntityId): ...

    def get_component(self, entity_id: EntityId, component_class: Type[Component1]) -> Component1: ...

    @overload
    def get_components(self, entity_id: EntityId,
                       component_classes: tuple[Type[Component1]]) -> tuple[Component1]: ...

    @overload
    def get_components(self, entity_id: EntityId,
                       component_classes: tuple[Type[Component1], Type[Component2]]) -> tuple[
        Component1, Component2]: ...

    @overload
    def get_components(self, entity_id: EntityId,
                       component_classes: tuple[Type[Component1], Type[Component2], Type[Component3]]) -> tuple[
        Component1, Component2, Component3]: ...
