"""State handling functions."""
from __future__ import annotations

import tcod.console

import g


def main_draw() -> None:
    """Render and present the active state."""
    if not g.states:
        return
    console = tcod.console.Console(80, 50)
    g.states[-1].on_draw(console)
    g.context.present(console)


def main_loop() -> None:
    """Run the active state forever."""
    while g.states:
        main_draw()
        for event in tcod.event.wait():
            if g.states:
                g.states[-1].on_event(event)
