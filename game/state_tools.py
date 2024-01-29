"""State handling functions."""

import tcod.console

import g


def main_draw() -> None:
    """Render and present the active state."""
    if not g.states:
        return
    g.console.clear()
    g.states[-1].on_draw(g.console)
    g.context.present(g.console)


def main_loop() -> None:
    """Run the active state forever."""
    while g.states:
        main_draw()
        for event in tcod.event.wait():
            print(event)
            if g.states:
                g.states[-1].on_event(event)
