"""A collection of game states."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, Self

import attrs
import tcod.console
import tcod.constants
import tcod.event
from tcod.event import KeySym

import g
import game.world_tools
from game.components import Gold, Graphic, Position
from game.constants import CONSOLE_SIZE
from game.message_tools import report
from game.rendering import LogRenderer
from game.state import Pop, Push, Rebase, State, StateResult
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
                    report(g.world, f"Picked up {gold.components[Gold]}g, total: {player.components[Gold]}g")
                    gold.clear()
                return None
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case tcod.event.KeyDown(sym=KeySym.m):
                return Push(LogViewer.from_console_size(*CONSOLE_SIZE))
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

        LogRenderer.init(g.world, console.width, 5).render().blit(dest=console, dest_x=0, dest_y=console.height - 5)


@attrs.define()
class MenuItem:
    """Clickable menu item."""

    label: str
    callback: Callable[[], StateResult]


@attrs.define(eq=False)
class ListMenu(State):
    """Simple list menu state."""

    items: tuple[MenuItem, ...]
    selected: int | None = 0
    x: int = 0
    y: int = 0

    def on_event(self, event: tcod.event.Event) -> StateResult:  # noqa: PLR0911
        """Handle events for menus."""
        match event:
            case tcod.event.Quit():
                raise SystemExit()
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                dx, dy = DIRECTION_KEYS[sym]
                if dx != 0 or dy == 0:
                    return None
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
            case tcod.event.KeyDown(sym=KeySym.RETURN):
                return self.activate_selected()
            case tcod.event.MouseButtonUp(button=tcod.event.MouseButton.LEFT):
                return self.activate_selected()
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return self.on_cancel()
            case tcod.event.MouseButtonUp(button=tcod.event.MouseButton.RIGHT):
                return self.on_cancel()
            case _:
                return None

    def activate_selected(self) -> StateResult:
        """Call the selected menu items callback."""
        if self.selected is not None:
            return self.items[self.selected].callback()
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
            MenuItem("New game", self.new_game),
            MenuItem("Quit", self.quit),
        ]
        if hasattr(g, "world"):
            items.insert(0, MenuItem("Continue", self.continue_))

        super().__init__(
            items=tuple(items),
            selected=0,
            x=5,
            y=5,
        )

    def continue_(self) -> StateResult:
        """Return to the game."""
        return Rebase(InGame())

    def new_game(self) -> StateResult:
        """Begin a new game."""
        g.world = game.world_tools.new_world()
        return Rebase(InGame())

    def quit(self) -> StateResult:
        """Close the program."""
        raise SystemExit()


@attrs.define(eq=False)
class LogViewer(State):
    """Displays the full log of messages."""

    x: int
    y: int
    width: int
    height: int
    log_renderer: LogRenderer

    @classmethod
    def from_console_size(cls, width: int, height: int) -> Self:
        """Return a new instance derived from the provided console size."""
        MARGIN_SIZE = 2
        return cls(
            x=MARGIN_SIZE,
            y=MARGIN_SIZE,
            width=width - MARGIN_SIZE * 2,
            height=height - MARGIN_SIZE * 2,
            log_renderer=LogRenderer.init(g.world, width - MARGIN_SIZE * 2 - 2, height - MARGIN_SIZE * 2 - 2),
        )

    def on_event(self, event: tcod.event.Event) -> StateResult:  # noqa: PLR0911
        """Handle events for menus."""
        match event:
            case tcod.event.Quit():
                raise SystemExit()
            case tcod.event.MouseWheel(y=y):
                self.log_renderer.scroll(-y * 3)
                return None
            case tcod.event.MouseMotion(motion=(_, y), state=tcod.event.MouseButtonMask.LEFT):
                self.log_renderer.scroll(-y)
                return None
            case tcod.event.KeyDown(sym=KeySym.HOME):
                self.log_renderer.y_position = 0
                return None
            case tcod.event.KeyDown(sym=KeySym.END):
                self.log_renderer.y_position = self.log_renderer.get_max_y_pos()
                return None
            case tcod.event.KeyDown(sym=KeySym.PAGEUP):
                self.log_renderer.scroll(-self.log_renderer.height)
                return None
            case tcod.event.KeyDown(sym=KeySym.PAGEDOWN):
                self.log_renderer.scroll(self.log_renderer.height)
                return None
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                dx, dy = DIRECTION_KEYS[sym]
                if dx != 0 or dy == 0:
                    return Pop()
                self.log_renderer.scroll(dy)
                return None
            case tcod.event.KeyDown():
                return Pop()
            case tcod.event.MouseButtonUp(button=tcod.event.MouseButton.RIGHT):
                return Pop()
            case _:
                return None

    def on_draw(self, console: tcod.console.Console) -> None:
        """Render the menu."""
        current_index = g.states.index(self)
        if current_index > 0:
            g.states[current_index - 1].on_draw(console)
        if g.states[-1] is self:
            console.rgb["fg"] //= 4
            console.rgb["bg"] //= 4

        console.draw_frame(
            self.x, self.y, self.width, self.height, fg=(255, 255, 255), bg=(0, 0, 0), decoration="┌─┐│ │└─┘"
        )
        console.print_box(
            self.x,
            self.y,
            self.width,
            self.height,
            " Message Log ",
            fg=(0, 0, 0),
            bg=(255, 255, 255),
            alignment=tcod.constants.CENTER,
        )
        self.log_renderer.render().blit(dest=console, dest_x=self.x + 1, dest_y=self.y + 1)
