from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Callable

from kraken.core.action import Action, ActionResult
from kraken.core.task import Task


@dataclasses.dataclass
class RenderFileAction(Action):
    content: str | Callable[[], str]
    file: Path
    encoding: str = "utf-8"

    def is_up_to_date(self) -> bool:
        if callable(self.content):
            self.content = self.content()
        return self.file.is_file() and self.file.read_text() == self.content

    def execute(self) -> ActionResult:
        if callable(self.content):
            self.content = self.content()
        self.file.parent.mkdir(exist_ok=True)
        encoded = self.content.encode(self.encoding)
        print(f"write {self.file} ({len(encoded)} bytes)")
        self.file.write_bytes(encoded)
        return ActionResult.SUCCEEDED


def render_file(
    name: str,
    content: str | Callable[[], str],
    file: Path,
    encoding: str = "utf-8",
) -> Task[RenderFileAction]:
    from kraken.api import project

    return project.do(name, RenderFileAction(content, file, encoding))