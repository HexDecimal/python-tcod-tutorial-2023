"""Base classes for states."""
from __future__ import annotations

from typing import Protocol

import tcod.console
import tcod.event


class State(Protocol):
    """An abstract game state."""

    def on_event(self, event: tcod.event.Event) -> None:
        """Called on events."""

    def on_draw(self, console: tcod.console.Console) -> None:
        """Called when the state is being drawn."""
