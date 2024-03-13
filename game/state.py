"""Base classes for states."""

from __future__ import annotations

from typing import Protocol, TypeAlias

import attrs
import tcod.console
import tcod.event


class State(Protocol):
    """An abstract game state."""

    __slots__ = ()

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Called on events."""

    def on_draw(self, console: tcod.console.Console) -> None:
        """Called when the state is being drawn."""


@attrs.define()
class Push:
    """Push a new state on top of the stack."""

    state: State


@attrs.define()
class Pop:
    """Remove the current state from the stack."""


@attrs.define()
class Rebase:
    """Replace the stack with a new state."""

    state: State


StateResult: TypeAlias = "Push | Pop | Rebase | None"
