"""A collection of game states."""

from __future__ import annotations

import attrs
import tcod.console
import tcod.event
from tcod.event import KeySym


@attrs.define(eq=False)
class ExampleState:
    """Example state with a hard-coded player position."""

    player_x: int
    """Player X position, left-most position is zero."""
    player_y: int
    """Player Y position, top-most position is zero."""

    def on_event(self, event: tcod.event.Event) -> None:
        """Move the player on events and handle exiting. Movement is hard-coded."""
        match event:
            case tcod.event.Quit():
                raise SystemExit()
            case tcod.event.KeyDown(sym=KeySym.LEFT):
                self.player_x -= 1
            case tcod.event.KeyDown(sym=KeySym.RIGHT):
                self.player_x += 1
            case tcod.event.KeyDown(sym=KeySym.UP):
                self.player_y -= 1
            case tcod.event.KeyDown(sym=KeySym.DOWN):
                self.player_y += 1

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw the player with print. Bounds do not need to be checked with this function."""
        console.print(self.player_x, self.player_y, "@")
