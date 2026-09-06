# -*- coding: utf-8 -*-
"""
SQLite orqali foydalanuvchi tarixini va tanlangan tilini saqlash.
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "bot_database.db"


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'uz',
                created_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT,
                file_type TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def set_user_language(user_id: int, language: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, language, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
            """,
            (user_id, language, datetime.now().isoformat()),
        )
        conn.commit()


def get_user_language(user_id: int) -> str:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT language FROM users WHERE user_id = ?", (user_id,)
        )
        row = cur.fetchone()
        return row[0] if row else "uz"


def add_history(user_id: int, topic: str, file_type: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO history (user_id, topic, file_type, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, topic, file_type, datetime.now().isoformat()),
        )
        conn.commit()


def get_history(user_id: int, limit: int = 10):
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT topic, file_type, created_at FROM history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return cur.fetchall()
