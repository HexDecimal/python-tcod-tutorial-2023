"""State handling functions."""

from __future__ import annotations

import tcod.console

import g
from game.constants import CONSOLE_SIZE
from game.state import Pop, Push, Rebase, StateResult


def main_draw() -> None:
    """Render and present the active state."""
    if not g.states:
        return
    console = tcod.console.Console(*CONSOLE_SIZE)
    g.states[-1].on_draw(console)
    g.context.present(console)


def apply_state_result(result: StateResult) -> None:
    """Apply a StateResult to `g.states`."""
    match result:
        case Push(state=state):
            g.states.append(state)
        case Pop():
            g.states.pop()
        case Rebase(state=state):
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
