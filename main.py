#!/usr/bin/env python3
"""Main entry-point module. This script is used to start the program."""

from __future__ import annotations

import attrs
import tcod.console
import tcod.context
import tcod.event
import tcod.tileset


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
            case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
                self.player_x -= 1
            case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
                self.player_x += 1
            case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
                self.player_y -= 1
            case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
                self.player_y += 1

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw the player with print. Bounds do not need to be checked with this function."""
        console.print(self.player_x, self.player_y, "@")


def main() -> None:
    """Entry point function."""
    tileset = tcod.tileset.load_tilesheet(
        "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    console = tcod.console.Console(80, 50)
    state = ExampleState(player_x=console.width // 2, player_y=console.height // 2)
    with tcod.context.new(console=console, tileset=tileset) as context:
        while True:  # Main loop
            console.clear()  # Clear the console before any drawing
            state.on_draw(console)  # Draw the current state
            context.present(console)  # Render the console to the window and show it
            for event in tcod.event.wait():  # Event loop, blocks until pending events exist
                print(event)
                state.on_event(event)  # Dispatch events to the state


if __name__ == "__main__":
    main()
