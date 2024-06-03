"""Configuration settings."""

import configparser
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import Self

import attrs
import cattrs

converter = cattrs.Converter()


@attrs.define()
class ConsoleConfig:
    """Console config settings."""

    columns: int = 80
    rows: int = 50

    @property
    def size(self) -> tuple[int, int]:
        """Return a (width, height) tuple."""
        return (self.columns, self.rows)


@attrs.define()
class Config:
    """Config attributes."""

    console: ConsoleConfig = attrs.field(factory=lambda: ConsoleConfig())

    @classmethod
    def load(cls, file: str | PathLike[str] | Iterable[str | PathLike[str]]) -> Self:
        """Return a new config loaded from a file."""
        parser = configparser.ConfigParser()
        parser.read(file)
        return converter.structure(parser, cls)

    def save(self, file: str | PathLike[str]) -> None:
        """Write current config to a file."""
        file = Path(file)
        parser = configparser.ConfigParser()
        parser.update(converter.unstructure(self))
        with file.open("w") as f:
            parser.write(f)
