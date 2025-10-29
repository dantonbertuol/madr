import asyncio
import sys

from fastapi import FastAPI

from madr.routers import contas, romancistas

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # pragma: no cover

app = FastAPI()
app.include_router(romancistas.router)
app.include_router(contas.router)
