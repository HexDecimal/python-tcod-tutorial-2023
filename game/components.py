"""Collection of common components."""
from __future__ import annotations

from typing import Final, Self

import attrs
import tcod.ecs.callbacks
from tcod.ecs import Entity


@attrs.define(frozen=True)
class Position:
    """An entities position."""

    x: int
    y: int

    def __add__(self, direction: tuple[int, int]) -> Self:
        """Add a vector to this position."""
        x, y = direction
        return self.__class__(self.x + x, self.y + y)


@tcod.ecs.callbacks.register_component_changed(component=Position)
def on_position_changed(entity: Entity, old: Position | None, new: Position | None) -> None:
    """Mirror position components as a tag."""
    if old == new:
        return
    if old is not None:
        entity.tags.discard(old)
    if new is not None:
        entity.tags.add(new)


@attrs.define(frozen=True)
class Graphic:
    """An entities icon and color."""

    ch: int = ord("!")
    fg: tuple[int, int, int] = (255, 255, 255)


Gold: Final = ("Gold", int)
"""Amount of gold."""
