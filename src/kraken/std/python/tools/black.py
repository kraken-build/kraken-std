from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Union

from kraken.core import Project, Property, TaskResult

from ..settings import EnvironmentAwareDispatchTask


class BlackTask(EnvironmentAwareDispatchTask):
    """A task to run the `black` formatter to either check for necessary changes or apply changes."""

    check_only: Property[bool] = Property.config(default=False)
    config_file: Property[Path]
    source_directories: Property[list[Union[str, Path]]] = Property.config(default_factory=lambda: ["src"])
    additional_args: Property[list[str]] = Property.config(default_factory=list)

    def get_execute_command(self) -> list[str] | TaskResult:
        command = ["black"] + list(map(str, self.source_directories.get()))
        command += self.settings.get_tests_directory_as_args()
        if self.check_only.get():
            command += ["--check"]
        if self.config_file.is_filled():
            command += ["--config", str(self.config_file.get())]
        command += self.additional_args.get()
        return command


@dataclasses.dataclass
class BlackTasks:
    check: BlackTask
    format: BlackTask


def black(project: Project | None = None, **kwargs: Any) -> BlackTasks:
    """Creates two black tasks, one to check and another to format. The check task will be grouped under `"lint"`
    whereas the format task will be grouped under `"fmt"`."""

    project = project or Project.current()
    check_task = project.do("blackCheck", BlackTask, group="lint", **kwargs)
    format_task = project.do("blackFormat", BlackTask, group="fmt", default=False, **kwargs, check_only=True)
    return BlackTasks(check_task, format_task)