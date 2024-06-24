"""A collection of game states."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, Protocol

import attrs
import tcod.console
import tcod.constants
import tcod.event
from tcod.event import KeySym

import g
import game.world_tools
from game.components import Gold, Graphic, Position
from game.state import Pop, Push, Reset, State, StateResult
from game.tags import IsItem, IsPlayer

DIRECTION_KEYS: Final = {
    # Arrow keys
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    # Arrow key diagonals
    KeySym.HOME: (-1, -1),
    KeySym.END: (-1, 1),
    KeySym.PAGEUP: (1, -1),
    KeySym.PAGEDOWN: (1, 1),
    # Keypad
    KeySym.KP_4: (-1, 0),
    KeySym.KP_6: (1, 0),
    KeySym.KP_8: (0, -1),
    KeySym.KP_2: (0, 1),
    KeySym.KP_7: (-1, -1),
    KeySym.KP_1: (-1, 1),
    KeySym.KP_9: (1, -1),
    KeySym.KP_3: (1, 1),
    # VI keys
    KeySym.h: (-1, 0),
    KeySym.l: (1, 0),
    KeySym.k: (0, -1),
    KeySym.j: (0, 1),
    KeySym.y: (-1, -1),
    KeySym.b: (-1, 1),
    KeySym.u: (1, -1),
    KeySym.n: (1, 1),
}


@attrs.define(eq=False)
class InGame(State):
    """Primary in-game state."""

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Handle events for the in-game state."""
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        match event:
            case tcod.event.Quit():
                raise SystemExit()
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                player.components[Position] += DIRECTION_KEYS[sym]
                # Auto pickup gold
                for gold in g.world.Q.all_of(components=[Gold], tags=[player.components[Position], IsItem]):
                    player.components[Gold] += gold.components[Gold]
                    text = f"Picked up {gold.components[Gold]}g, total: {player.components[Gold]}g"
                    g.world[None].components[("Text", str)] = text
                    gold.clear()
                return None
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case _:
                return None

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw the standard screen."""
        for entity in g.world.Q.all_of(components=[Position, Graphic]):
            pos = entity.components[Position]
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = entity.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg

        if text := g.world[None].components.get(("Text", str)):
            console.print(x=0, y=console.height - 1, string=text, fg=(255, 255, 255), bg=(0, 0, 0))


class MenuItem(Protocol):
    """Menu item protocol."""

    __slots__ = ()

    @property
    def label(self) -> str:
        """Label for the menu item."""

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Handle events passed to the menu item."""


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


@attrs.define(eq=False)
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
                raise SystemExit()
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
        current_index = g.states.index(self)
        if current_index > 0:
            g.states[current_index - 1].on_draw(console)
        if g.states[-1] is self:
            console.rgb["fg"] //= 4
            console.rgb["bg"] //= 4
        for i, item in enumerate(self.items):
            is_selected = i == self.selected
            console.print(
                self.x,
                self.y + i,
                item.label,
                fg=(255, 255, 255),
                bg=(64, 64, 64) if is_selected else (0, 0, 0),
            )


class MainMenu(ListMenu):
    """Main/escape menu."""

    __slots__ = ()

    def __init__(self) -> None:
        """Initialize the main menu."""
        items = [
            SelectItem("New game", self.new_game),
            SelectItem("Quit", self.quit),
        ]
        if hasattr(g, "world"):
            items.insert(0, SelectItem("Continue", self.continue_))

        super().__init__(
            items=tuple(items),
            selected=0,
            x=5,
            y=5,
        )

    @staticmethod
    def continue_() -> StateResult:
        """Return to the game."""
        return Reset(InGame())

    @staticmethod
    def new_game() -> StateResult:
        """Begin a new game."""
        g.world = game.world_tools.new_world()
        return Reset(InGame())

    @staticmethod
    def quit() -> StateResult:
        """Close the program."""
        raise SystemExit()
