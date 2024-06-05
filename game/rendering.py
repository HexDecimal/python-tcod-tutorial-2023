"""Rendering tools and helpers."""

from __future__ import annotations

from typing import Self

import attrs
import tcod.console
import tcod.ecs

import g
from game.message_tools import get_log
from game.state import State


@attrs.define()
class LogRenderer:
    """Log rendering helper."""

    world: tcod.ecs.Registry
    width: int
    height: int
    y_position: int

    @classmethod
    def init(cls, world: tcod.ecs.Registry, width: int, height: int) -> Self:
        """Return a new instance with a derived y_position."""
        self = cls(world, width, height, 0)
        self.y_position = self.get_max_y_pos()
        return self

    def scroll(self, y_dir: int, wrap: bool = False) -> None:
        """Scroll the log by the amount provided by y_dir."""
        self.y_position = max(0, min(self.y_position + y_dir, self.get_max_y_pos()))

    def get_log_height(self) -> int:
        """Total height of the log."""
        return sum(tcod.console.get_height_rect(self.width, msg.text) for msg in get_log(self.world))

    def get_max_y_pos(self) -> int:
        """Maximum value of y_position."""
        return max(0, self.get_log_height() - self.height)

    def render(self) -> tcod.console.Console:
        """Return a console with the log rendered into it."""
        console = tcod.console.Console(self.width, self.height)
        y = -self.y_position
        for msg in get_log(self.world):
            if y >= self.height:
                break
            y += console.print_box(x=0, y=y, width=self.width, height=0, string=msg.text, fg=(255, 255, 255))
        return console


def draw_previous_state(console: tcod.console.Console, state: State) -> None:
    """Draw the state before this state."""
    current_index = g.states.index(state)
    if current_index > 0:
        g.states[current_index - 1].on_draw(console)
    if g.states[-1] is state:  # Darken the screen before drawing the last state.
        console.rgb["fg"] //= 4
        console.rgb["bg"] //= 4
