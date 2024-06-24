#!/usr/bin/env python3
"""Main entry-point module. This script is used to start the program."""

from __future__ import annotations

import tcod.console
import tcod.context
import tcod.tileset

import g
import game.state_tools
import game.states

CONFIG_FILE = "config.ini"


def main() -> None:
    """Entry point function."""
    tileset = tcod.tileset.load_tilesheet(
        "data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    g.states = [game.states.MainMenu()]
    with tcod.context.new(columns=80, rows=50, tileset=tileset) as g.context:
        game.state_tools.main_loop()


if __name__ == "__main__":
    main()
