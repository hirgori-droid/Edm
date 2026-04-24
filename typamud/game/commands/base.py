from __future__ import annotations

from collections.abc import Callable

CommandHandler = Callable[["GameSession", list[str]], str]


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, CommandHandler] = {}

    def register(self, *aliases: str) -> Callable[[CommandHandler], CommandHandler]:
        def decorator(handler: CommandHandler) -> CommandHandler:
            for alias in aliases:
                self._commands[alias] = handler
            return handler

        return decorator

    def get(self, command: str) -> CommandHandler | None:
        return self._commands.get(command)
