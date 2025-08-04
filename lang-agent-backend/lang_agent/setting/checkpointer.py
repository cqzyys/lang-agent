import asyncio
import sqlite3
from typing import Optional

import aiosqlite
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

__all__ = ["async_checkpointer", "async_checkpointer_shutdown"]

CHECKPOINT_PATH = "lang_agent/db/checkpoint.db"


class CheckpointerManager:
    _aiosqlite_conn: Optional[aiosqlite.Connection] = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_async_checkpointer(cls):
        async with cls._lock:
            if cls._aiosqlite_conn is None:
                cls._aiosqlite_conn = await aiosqlite.connect(
                    CHECKPOINT_PATH, check_same_thread=False
                )
            return AsyncSqliteSaver(cls._aiosqlite_conn)

    @classmethod
    async def close_connection(cls):
        if cls._aiosqlite_conn is not None:
            await cls._aiosqlite_conn.close()
            cls._aiosqlite_conn = None

    @classmethod
    def get_sync_checkpointer(cls):
        connection = sqlite3.connect(CHECKPOINT_PATH, check_same_thread=False)
        return SqliteSaver(connection)


async def async_checkpointer():
    return await CheckpointerManager.get_async_checkpointer()


async def async_checkpointer_shutdown():
    await CheckpointerManager.close_connection()


def sync_checkpointer():
    return CheckpointerManager.get_sync_checkpointer()
