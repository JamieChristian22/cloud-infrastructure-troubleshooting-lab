"""Genuine SQLite-backed local dependency used by the synthetic order API."""
import sqlite3
from threading import RLock


class DatabaseUnavailable(RuntimeError):
    """The local SQLite connection cannot serve requests."""


class OrdersDatabase:
    """In-memory SQLite seeded with fictional records.

    Disconnect deliberately closes the actual connection; recover opens a fresh
    database and re-seeds it. This is an executable dependency outage, not an
    AWS/RDS outage or a claim of persistent recovery.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._connection: sqlite3.Connection | None = None
        self.recover()

    def recover(self) -> None:
        with self._lock:
            if self._connection is not None:
                return
            db = sqlite3.connect(':memory:', check_same_thread=False)
            try:
                db.execute('CREATE TABLE orders (id TEXT PRIMARY KEY, status TEXT NOT NULL, amount_usd REAL NOT NULL)')
                db.executemany(
                    'INSERT INTO orders (id, status, amount_usd) VALUES (?, ?, ?)',
                    [('SAMPLE-1001', 'fulfilled', 48.50), ('SAMPLE-1002', 'processing', 17.25)],
                )
                db.commit()
            except sqlite3.Error:
                db.close()
                raise
            self._connection = db

    def disconnect(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

    def ready(self) -> bool:
        with self._lock:
            if self._connection is None:
                return False
            try:
                self._connection.execute('SELECT 1 FROM orders LIMIT 1').fetchone()
                return True
            except sqlite3.Error:
                return False

    def list_orders(self) -> list[dict]:
        with self._lock:
            if self._connection is None:
                raise DatabaseUnavailable('SQLite connection is closed')
            try:
                rows = self._connection.execute(
                    'SELECT id, status, amount_usd FROM orders ORDER BY id'
                ).fetchall()
                return [{'id': row[0], 'status': row[1], 'amount_usd': row[2]} for row in rows]
            except sqlite3.Error as exc:
                raise DatabaseUnavailable('SQLite query unavailable') from exc

    def close(self) -> None:
        self.disconnect()
