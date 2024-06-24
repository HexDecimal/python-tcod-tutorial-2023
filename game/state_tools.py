"""State handling functions."""

from __future__ import annotations

import tcod.console

import g
from game.state import Pop, Push, Reset, StateResult


def main_draw() -> None:
    """Render and present the active state."""
    if not g.states:
        return
    g.console.clear()
    g.states[-1].on_draw(g.console)
    g.context.present(g.console)


def apply_state_result(result: StateResult) -> None:
    """Apply a StateResult to `g.states`."""
    match result:
        case Push(state=state):
            g.states.append(state)
        case Pop():
            g.states.pop()
        case Reset(state=state):
            while g.states:
                apply_state_result(Pop())
            apply_state_result(Push(state))
        case None:
            pass
        case _:
            raise TypeError(result)


def main_loop() -> None:
    """Run the active state forever."""
    while g.states:
        main_draw()
        for event in tcod.event.wait():
            tile_event = g.context.convert_event(event)
            if g.states:
                apply_state_result(g.states[-1].on_event(tile_event))
