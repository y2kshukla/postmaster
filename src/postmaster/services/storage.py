from __future__ import annotations

import json
import os
import sqlite3
from typing import Optional

from postmaster.models.collection import Collection
from postmaster.models.environment import Environment
from postmaster.models.request import HttpRequest


class StorageService:
    def __init__(self, db_path: str = "") -> None:
        if not db_path:
            app_dir = os.path.join(os.path.expanduser("~"), ".postmaster")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "postmaster.db")
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_tables()

    def close(self) -> None:
        if self._conn:
            self._conn.close()

    def _init_tables(self) -> None:
        cursor = self._conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS environments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT NOT NULL,
                url TEXT NOT NULL,
                status_code INTEGER,
                request_data TEXT NOT NULL,
                response_data TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        self._conn.commit()

    def save_collection(self, collection: Collection) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO collections (id, name, data, updated_at) VALUES (?, ?, ?, datetime('now'))",
            (collection.id, collection.name, collection.model_dump_json()),
        )
        self._conn.commit()

    def load_collections(self) -> list[Collection]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT data FROM collections ORDER BY name")
        rows = cursor.fetchall()
        return [Collection.model_validate_json(row["data"]) for row in rows]

    def delete_collection(self, collection_id: str) -> None:
        self._conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
        self._conn.commit()

    def save_environment(self, env: Environment) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO environments (id, name, data, updated_at) VALUES (?, ?, ?, datetime('now'))",
            (env.id, env.name, env.model_dump_json()),
        )
        self._conn.commit()

    def load_environments(self) -> list[Environment]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT data FROM environments ORDER BY name")
        return [Environment.model_validate_json(row["data"]) for row in cursor.fetchall()]

    def delete_environment(self, env_id: str) -> None:
        self._conn.execute("DELETE FROM environments WHERE id = ?", (env_id,))
        self._conn.commit()

    def add_history(
        self, request: HttpRequest, status_code: int = 0, response_data: str = ""
    ) -> None:
        self._conn.execute(
            "INSERT INTO history (method, url, status_code, request_data, response_data) VALUES (?, ?, ?, ?, ?)",
            (request.method, request.url, status_code, request.model_dump_json(), response_data),
        )
        self._conn.commit()

    def load_history(self, limit: int = 50) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_setting(self, key: str, default: str = "") -> str:
        cursor = self._conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
        )
        self._conn.commit()
