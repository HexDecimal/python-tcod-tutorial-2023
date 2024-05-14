"""Message log types."""

from __future__ import annotations

from typing import TypeAlias

import attrs


@attrs.define()
class Message:
    """A single item of the message log."""

    raw_text: str
    count: int

    @property
    def text(self) -> str:
        """Final text of this message."""
        if self.count > 1:
            return f"{self.raw_text} (x{self.count})"
        return self.raw_text


MessageLog: TypeAlias = list[Message]
"""Message log type and component."""
