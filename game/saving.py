"""Handling saving and loading of the world."""

from __future__ import annotations

import lzma
import pickle
import pickletools
from pathlib import Path
from typing import Final

import tcod.ecs

SAVE_VERSION = 0
"""Current save version."""

SaveVersion: Final = ("SaveVersion", int)
"""Save version component."""


def save_world(file: Path, world: tcod.ecs.Registry) -> None:
    """Save a world to a file."""
    world[None].components[SaveVersion] = SAVE_VERSION
    data = pickle.dumps(world, protocol=4)
    data = pickletools.optimize(data)
    data = lzma.compress(data)
    file.write_bytes(data)


def load_world(file: Path) -> tcod.ecs.Registry:
    """Return a world loaded from a file."""
    data = file.read_bytes()
    data = lzma.decompress(data)
    world: tcod.ecs.World = pickle.loads(data)  # noqa: S301
    return world
