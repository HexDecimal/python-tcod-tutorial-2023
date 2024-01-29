"""This module stores globally mutable variables used by this program."""

from __future__ import annotations

import tcod.console
import tcod.context

import game.state

console: tcod.console.Console
"""The main console."""

context: tcod.context.Context
"""The window managed by tcod."""

states: list[game.state.State] = []
"""A stack of states with the last item being the active state."""
