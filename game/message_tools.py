"""Message log functions."""

from __future__ import annotations

import tcod.ecs

from game.message import Message, MessageLog


def get_log(world: tcod.ecs.Registry) -> MessageLog:
    """Return the worlds global log, creating it if it does not exist."""
    return world[None].components.setdefault(MessageLog, [])


def report(world: tcod.ecs.Registry, text: str) -> None:
    """Append text to the global message log."""
    log = get_log(world)
    if log and log[-1].text == text:
        log[-1].count += 1
    else:
        log.append(Message(raw_text=text, count=1))
