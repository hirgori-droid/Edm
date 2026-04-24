from __future__ import annotations

import asyncio

from typamud.game.server import GameServer


async def main() -> None:
    server = GameServer()
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("typamud остановлен")
