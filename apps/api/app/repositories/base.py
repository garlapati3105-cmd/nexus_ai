"""
Nexus AI — Base Repository
Provides shared CRUD operations for all repositories using the Supabase client.
Implements: create, find_by_id, update, delete, list, search with pagination/filtering/sorting.
"""
from __future__ import annotations
from typing import Any, Optional
from supabase import Client
from app.core.database import get_supabase
from app.core.exceptions import EntityNotFoundException, DatabaseOperationException
from app.core.logging import get_logger

logger = get_logger("repository.base")


class BaseRepository:
    """Abstract base repository with full CRUD, pagination, filtering, and sorting."""

    TABLE_NAME: str = ""  # Override in subclass

    def __init__(self, client: Client | None = None):
        self.db: Client = client or get_supabase()

    # ─── CREATE ──────────────────────────────────────────────
    def create(self, data: dict[str, Any]) -> dict:
        """Insert a single row and return it."""
        try:
            result = self.db.table(self.TABLE_NAME).insert(data).execute()
            if result.data:
                logger.info(f"[{self.TABLE_NAME}] Created: {result.data[0].get('id', 'N/A')}")
                return result.data[0]
            raise DatabaseOperationException("create", f"No data returned from {self.TABLE_NAME}")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"[{self.TABLE_NAME}] Create failed: {e}")
            raise DatabaseOperationException("create", str(e))

    # ─── READ BY ID ──────────────────────────────────────────
    def find_by_id(self, record_id: str, columns: str = "*") -> dict:
        """Fetch a single record by its primary key UUID."""
        try:
            result = self.db.table(self.TABLE_NAME).select(columns).eq("id", record_id).execute()
            if result.data:
                return result.data[0]
            raise EntityNotFoundException(self.TABLE_NAME, record_id)
        except EntityNotFoundException:
            raise
        except Exception as e:
            logger.error(f"[{self.TABLE_NAME}] find_by_id failed: {e}")
            raise DatabaseOperationException("find_by_id", str(e))

    # ─── UPDATE ──────────────────────────────────────────────
    def update(self, record_id: str, data: dict[str, Any]) -> dict:
        """Update an existing record by ID."""
        try:
            result = self.db.table(self.TABLE_NAME).update(data).eq("id", record_id).execute()
            if result.data:
                logger.info(f"[{self.TABLE_NAME}] Updated: {record_id}")
                return result.data[0]
            raise EntityNotFoundException(self.TABLE_NAME, record_id)
        except EntityNotFoundException:
            raise
        except Exception as e:
            logger.error(f"[{self.TABLE_NAME}] Update failed: {e}")
            raise DatabaseOperationException("update", str(e))

    # ─── DELETE (soft) ───────────────────────────────────────
    def delete(self, record_id: str) -> bool:
        """Hard delete by ID. Returns True on success."""
        try:
            result = self.db.table(self.TABLE_NAME).delete().eq("id", record_id).execute()
            logger.info(f"[{self.TABLE_NAME}] Deleted: {record_id}")
            return True
        except Exception as e:
            logger.error(f"[{self.TABLE_NAME}] Delete failed: {e}")
            raise DatabaseOperationException("delete", str(e))

    # ─── LIST (paginated, sorted, filtered) ──────────────────
    def list(
        self,
        columns: str = "*",
        filters: dict[str, Any] | None = None,
        order_by: str = "created_at",
        ascending: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Paginated listing with optional filters and sorting."""
        try:
            query = self.db.table(self.TABLE_NAME).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            query = query.order(order_by, desc=not ascending)
            query = query.range(offset, offset + limit - 1)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"[{self.TABLE_NAME}] list failed: {e}")
            raise DatabaseOperationException("list", str(e))

    # ─── SEARCH ──────────────────────────────────────────────
    def search(
        self,
        column: str,
        query_text: str,
        columns: str = "*",
        limit: int = 20,
    ) -> list[dict]:
        """Case-insensitive text search on a specific column using ILIKE."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select(columns)
                .ilike(column, f"%{query_text}%")
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"[{self.TABLE_NAME}] search failed: {e}")
            raise DatabaseOperationException("search", str(e))
