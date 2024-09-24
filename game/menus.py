"""Menu UI classes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

import attrs
import tcod.console
import tcod.event
from tcod.event import KeySym

import game.state_tools
from game.constants import DIRECTION_KEYS
from game.state import Pop, State, StateResult


class MenuItem(Protocol):
    """Menu item protocol."""

    __slots__ = ()

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Handle events passed to the menu item."""

    def on_draw(self, console: tcod.console.Console, x: int, y: int, *, highlight: bool) -> None:
        """Draw is item at the given position."""


@attrs.define()
class SelectItem(MenuItem):
    """Clickable menu item."""

    label: str
    callback: Callable[[], StateResult]

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Handle events selecting this item."""
        match event:
            case tcod.event.KeyDown(sym=sym) if sym in {KeySym.RETURN, KeySym.RETURN2, KeySym.KP_ENTER}:
                return self.callback()
            case tcod.event.MouseButtonUp(button=tcod.event.MouseButton.LEFT):
                return self.callback()
            case _:
                return None

    def on_draw(self, console: tcod.console.Console, x: int, y: int, *, highlight: bool) -> None:
        """Render this items label."""
        console.print(x, y, self.label, fg=(255, 255, 255), bg=(64, 64, 64) if highlight else (0, 0, 0))


@attrs.define()
class ListMenu(State):
    """Simple list menu state."""

    items: tuple[MenuItem, ...]
    selected: int | None = 0
    x: int = 0
    y: int = 0

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Handle events for menus."""
        match event:
            case tcod.event.Quit():
                raise SystemExit
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                dx, dy = DIRECTION_KEYS[sym]
                if dx != 0 or dy == 0:
                    return self.activate_selected(event)
                if self.selected is not None:
                    self.selected += dy
                    self.selected %= len(self.items)
                else:
                    self.selected = 0 if dy == 1 else len(self.items) - 1
                return None
            case tcod.event.MouseMotion(position=(_, y)):
                y -= self.y
                self.selected = y if 0 <= y < len(self.items) else None
                return None
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return self.on_cancel()
            case tcod.event.MouseButtonUp(button=tcod.event.MouseButton.RIGHT):
                return self.on_cancel()
            case _:
                return self.activate_selected(event)

    def activate_selected(self, event: tcod.event.Event) -> StateResult:
        """Call the selected menu items callback."""
        if self.selected is not None:
            return self.items[self.selected].on_event(event)
        return None

    def on_cancel(self) -> StateResult:
        """Handle escape or right click being pressed on menus."""
        return Pop()

    def on_draw(self, console: tcod.console.Console) -> None:
        """Render the menu."""
        game.state_tools.draw_previous_state(self, console)
        for i, item in enumerate(self.items):
            item.on_draw(console, x=self.x, y=self.y + i, highlight=i == self.selected)
