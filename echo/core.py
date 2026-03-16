"""
Echo Memory System - Core Implementation (Optimized)

A brain-like memory management system with:
- SQLite-backed storage with transactions and indexing
- Power-law temperature decay with spaced repetition
- Association networks
- Event-triggered recall
- Never-forget storage
"""

import json
import math
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple

import re
from collections import Counter


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SCHEMA_VERSION = "2.0"

_DEFAULT_PRIORITY_DECAY: Dict[str, Tuple[float, float]] = {
    # priority -> (a, b) for power-law T = a * t^(-b)
    "P0": (1.0, 0.05),
    "P1": (1.0, 0.15),
    "P2": (1.0, 0.30),
}

_STOP_WORDS: frozenset = frozenset({
    "the", "and", "for", "with", "this", "that", "are", "was", "were",
    "been", "being", "have", "has", "had", "does", "did", "will",
    "这个", "那个", "可以", "需要", "应该", "就是", "因为",
})

_NON_PROJECTS: frozenset = frozenset({
    "The", "This", "That", "AI", "API", "OK", "HTTP", "JSON",
})

_TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "AI": ["ai", "gpt", "model", "machine learning", "ml"],
    "API": ["api", "token", "endpoint", "interface"],
    "Security": ["security", "vulnerability", "audit"],
    "Optimization": ["optimization", "improve"],
    "Architecture": ["architecture", "design", "system"],
    "Workflow": ["workflow", "process", "pipeline"],
    "Database": ["database", "sql", "query"],
    "Frontend": ["frontend", "ui", "react", "vue"],
}

# ---------------------------------------------------------------------------
# SQL DDL
# ---------------------------------------------------------------------------

_DDL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memories (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    content       TEXT NOT NULL,
    category      TEXT NOT NULL DEFAULT 'learning',
    priority      TEXT NOT NULL DEFAULT 'P1',
    permanent     INTEGER NOT NULL DEFAULT 0,
    confidence    REAL NOT NULL DEFAULT 1.0,
    temperature   REAL NOT NULL DEFAULT 1.0,
    state         TEXT NOT NULL DEFAULT 'active',
    access_count  INTEGER NOT NULL DEFAULT 0,
    consolidation_level INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    last_used     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    tag       TEXT NOT NULL,
    PRIMARY KEY (memory_id, tag)
);

CREATE TABLE IF NOT EXISTS access_history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    accessed_at TEXT NOT NULL,
    trigger   TEXT NOT NULL DEFAULT 'user_query'
);

CREATE TABLE IF NOT EXISTS associations (
    memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    kind      TEXT NOT NULL,  -- 'link', 'trigger', 'project', 'topic'
    value     TEXT NOT NULL,
    PRIMARY KEY (memory_id, kind, value)
);

-- Indexes for hot queries
CREATE INDEX IF NOT EXISTS idx_memories_temperature ON memories(temperature);
CREATE INDEX IF NOT EXISTS idx_memories_state       ON memories(state);
CREATE INDEX IF NOT EXISTS idx_memories_category    ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_created     ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_tags_tag      ON memory_tags(tag);
CREATE INDEX IF NOT EXISTS idx_assoc_kind_value     ON associations(kind, value);
CREATE INDEX IF NOT EXISTS idx_access_history_mem   ON access_history(memory_id);
"""


# ---------------------------------------------------------------------------
# Helper: Spaced-repetition bonus
# ---------------------------------------------------------------------------

def _spaced_repetition_bonus(access_count: int, consolidation_level: int) -> float:
    """
    Calculate temperature bonus from spaced-repetition & consolidation.

    The more a memory has been accessed at well-spaced intervals (approximated
    here by ``consolidation_level``), the slower it decays.  We return a
    multiplicative factor >= 1.0 that is applied *after* the base power-law
    decay, effectively slowing it.
    """
    # Each consolidation level reduces effective decay exponent
    # bonus ∈ [1.0, ~2.0]
    rep_factor = 1.0 + 0.1 * math.log1p(access_count)
    consol_factor = 1.0 + 0.15 * consolidation_level
    return min(rep_factor * consol_factor, 3.0)


def _compute_temperature(
    hours_since_last_access: float,
    priority: str,
    access_count: int,
    consolidation_level: int,
) -> float:
    """
    Power-law decay: T = a × t^(-b) / bonus

    ``t`` is measured in hours since last access (clamped to >= 1).
    """
    a, b = _DEFAULT_PRIORITY_DECAY.get(priority, (1.0, 0.15))
    t = max(hours_since_last_access, 1.0)
    base = a * (t ** (-b))
    bonus = _spaced_repetition_bonus(access_count, consolidation_level)
    return min(base * bonus, 1.0)


def _state_for_temperature(temp: float) -> str:
    if temp < 0.1:
        return "archived"
    if temp < 0.3:
        return "dormant"
    return "active"


# ---------------------------------------------------------------------------
# Storage backend
# ---------------------------------------------------------------------------

class _SQLiteStorage:
    """
    Thin wrapper around a SQLite database that hides all SQL from the
    public ``MemorySystem`` class.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._conn: sqlite3.Connection = sqlite3.connect(
            db_path, check_same_thread=False
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_DDL)
        self._ensure_meta()

    # -- context helpers ----------------------------------------------------

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """Yield a cursor inside an explicit transaction."""
        cur = self._conn.cursor()
        cur.execute("BEGIN")
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        self._conn.close()

    # -- meta ---------------------------------------------------------------

    def _ensure_meta(self) -> None:
        cur = self._conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key='version'")
        row = cur.fetchone()
        if row is None:
            now = datetime.now(timezone.utc).isoformat()
            cur.execute(
                "INSERT INTO meta(key,value) VALUES(?,?)",
                ("version", _SCHEMA_VERSION),
            )
            cur.execute(
                "INSERT INTO meta(key,value) VALUES(?,?)",
                ("created_at", now),
            )
            self._conn.commit()

    # -- CRUD ---------------------------------------------------------------

    def insert_memory(self, mem: Dict[str, Any]) -> None:
        with self.transaction() as cur:
            cur.execute(
                """
                INSERT INTO memories
                    (id, title, content, category, priority, permanent,
                     confidence, temperature, state, access_count,
                     consolidation_level, created_at, last_accessed, last_used)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    mem["id"],
                    mem["title"],
                    mem["content"],
                    mem["category"],
                    mem["priority"],
                    int(mem["permanent"]),
                    mem["confidence"],
                    mem["temperature"],
                    mem["state"],
                    mem["access_count"],
                    mem.get("consolidation_level", 0),
                    mem["created_at"],
                    mem["last_accessed"],
                    mem["last_used"],
                ),
            )
            # tags
            for tag in mem.get("tags", []):
                cur.execute(
                    "INSERT OR IGNORE INTO memory_tags(memory_id, tag) VALUES(?,?)",
                    (mem["id"], tag),
                )
            # associations
            assoc = mem.get("associations", {})
            for kind in ("link", "trigger", "project", "topic"):
                plural = kind + "s"
                for val in assoc.get(plural, []):
                    cur.execute(
                        "INSERT OR IGNORE INTO associations(memory_id, kind, value) VALUES(?,?,?)",
                        (mem["id"], kind, val),
                    )

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM memories WHERE id=?", (memory_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return self._row_to_dict(row)

    def memory_exists(self, memory_id: str) -> bool:
        cur = self._conn.cursor()
        cur.execute("SELECT 1 FROM memories WHERE id=? LIMIT 1", (memory_id,))
        return cur.fetchone() is not None

    def update_memory_fields(self, memory_id: str, fields: Dict[str, Any]) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k}=?" for k in fields)
        vals = list(fields.values()) + [memory_id]
        with self.transaction() as cur:
            cur.execute(f"UPDATE memories SET {cols} WHERE id=?", vals)

    def update_memory(self, memory_id: str, **kwargs: Any) -> bool:
        """Update arbitrary allowed columns on a memory row."""
        forbidden = {"id", "created_at"}
        allowed = {k: v for k, v in kwargs.items() if k not in forbidden}
        # Separate tag / association updates from column updates
        tag_update = allowed.pop("tags", None)
        assoc_update = allowed.pop("associations", None)

        with self.transaction() as cur:
            if allowed:
                cols = ", ".join(f"{k}=?" for k in allowed)
                vals = list(allowed.values()) + [memory_id]
                cur.execute(f"UPDATE memories SET {cols} WHERE id=?", vals)

            if tag_update is not None:
                cur.execute("DELETE FROM memory_tags WHERE memory_id=?", (memory_id,))
                for tag in tag_update:
                    cur.execute(
                        "INSERT OR IGNORE INTO memory_tags(memory_id,tag) VALUES(?,?)",
                        (memory_id, tag),
                    )

            if assoc_update is not None:
                cur.execute("DELETE FROM associations WHERE memory_id=?", (memory_id,))
                for kind in ("link", "trigger", "project", "topic"):
                    plural = kind + "s"
                    for val in assoc_update.get(plural, []):
                        cur.execute(
                            "INSERT OR IGNORE INTO associations(memory_id,kind,value) VALUES(?,?,?)",
                            (memory_id, kind, val),
                        )
        return True

    def record_access(self, memory_id: str, trigger: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self.transaction() as cur:
            cur.execute(
                "INSERT INTO access_history(memory_id, accessed_at, trigger) VALUES(?,?,?)",
                (memory_id, now, trigger),
            )
            cur.execute(
                """UPDATE memories
                   SET temperature=1.0, state='active',
                       last_used=?, last_accessed=?,
                       access_count = access_count + 1
                   WHERE id=?""",
                (now, now, memory_id),
            )
            # Consolidation: if recent accesses are well-spaced, bump level
            cur.execute(
                "SELECT COUNT(*) FROM access_history WHERE memory_id=?",
                (memory_id,),
            )
            total_accesses: int = cur.fetchone()[0]
            # Simple heuristic: every 5 accesses, increase consolidation
            new_level = total_accesses // 5
            cur.execute(
                "UPDATE memories SET consolidation_level=? WHERE id=?",
                (new_level, memory_id),
            )

    def iter_all_memories(self) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM memories")
        return [self._row_to_dict(row) for row in cur.fetchall()]

    def iter_non_permanent(self) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM memories WHERE permanent=0")
        return [self._row_to_dict(row) for row in cur.fetchall()]

    def bulk_update_temperature(self, updates: List[Tuple[float, str, str]]) -> None:
        """updates: list of (temperature, state, memory_id)"""
        with self.transaction() as cur:
            cur.executemany(
                "UPDATE memories SET temperature=?, state=? WHERE id=?",
                updates,
            )

    def get_tags(self, memory_id: str) -> List[str]:
        cur = self._conn.cursor()
        cur.execute("SELECT tag FROM memory_tags WHERE memory_id=?", (memory_id,))
        return [r[0] for r in cur.fetchall()]

    def get_associations(self, memory_id: str) -> Dict[str, List[str]]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT kind, value FROM associations WHERE memory_id=?", (memory_id,)
        )
        assoc: Dict[str, List[str]] = {
            "links": [],
            "triggers": [],
            "projects": [],
            "topics": [],
        }
        for row in cur.fetchall():
            plural = row[0] + "s"
            if plural in assoc:
                assoc[plural].append(row[1])
        return assoc

    def get_access_history(self, memory_id: str) -> List[Dict[str, str]]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT accessed_at, trigger FROM access_history WHERE memory_id=? ORDER BY id",
            (memory_id,),
        )
        return [{"at": r[0], "trigger": r[1]} for r in cur.fetchall()]

    def add_link(self, id1: str, id2: str) -> None:
        with self.transaction() as cur:
            cur.execute(
                "INSERT OR IGNORE INTO associations(memory_id,kind,value) VALUES(?,?,?)",
                (id1, "link", id2),
            )
            cur.execute(
                "INSERT OR IGNORE INTO associations(memory_id,kind,value) VALUES(?,?,?)",
                (id2, "link", id1),
            )

    def find_orphan_links(self) -> List[Dict[str, str]]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT a.memory_id, a.value
            FROM associations a
            LEFT JOIN memories m ON a.value = m.id
            WHERE a.kind='link' AND m.id IS NULL
            """
        )
        return [
            {"type": "orphan_link", "memory_id": r[0], "target": r[1]}
            for r in cur.fetchall()
        ]

    def search_text(
        self,
        query_lower: str,
        categories: Optional[List[str]],
        min_temperature: float,
    ) -> List[Dict[str, Any]]:
        """
        Return candidate memories that pass category / temperature filters.
        Full scoring is done in Python for flexibility.
        """
        sql = "SELECT * FROM memories WHERE temperature >= ?"
        params: list = [min_temperature]
        if categories:
            placeholders = ",".join("?" for _ in categories)
            sql += f" AND category IN ({placeholders})"
            params.extend(categories)
        cur = self._conn.cursor()
        cur.execute(sql, params)
        return [self._row_to_dict(row) for row in cur.fetchall()]

    def get_memories_by_association(
        self, kind: str, value_lower: str
    ) -> List[str]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT memory_id FROM associations WHERE kind=? AND LOWER(value)=?",
            (kind, value_lower),
        )
        return [r[0] for r in cur.fetchall()]

    def count_by_state(self) -> Dict[str, int]:
        cur = self._conn.cursor()
        cur.execute("SELECT state, COUNT(*) FROM memories GROUP BY state")
        return {r[0]: r[1] for r in cur.fetchall()}

    def count_by_category(self) -> Dict[str, int]:
        cur = self._conn.cursor()
        cur.execute("SELECT category, COUNT(*) FROM memories GROUP BY category")
        return {r[0]: r[1] for r in cur.fetchall()}

    def avg_temperature(self) -> float:
        cur = self._conn.cursor()
        cur.execute("SELECT AVG(temperature) FROM memories")
        row = cur.fetchone()
        return float(row[0]) if row[0] is not None else 0.0

    def total_count(self) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM memories")
        return cur.fetchone()[0]

    def archive_memory(self, memory_id: str) -> None:
        with self.transaction() as cur:
            cur.execute(
                "UPDATE memories SET temperature=0.0, state='archived' WHERE id=?",
                (memory_id,),
            )

    def rebuild_associations(self, memory_id: str, assoc: Dict[str, List[str]]) -> None:
        with self.transaction() as cur:
            # preserve manual links
            cur.execute(
                "SELECT value FROM associations WHERE memory_id=? AND kind='link'",
                (memory_id,),
            )
            links = [r[0] for r in cur.fetchall()]

            cur.execute("DELETE FROM associations WHERE memory_id=?", (memory_id,))
            for link_val in links:
                cur.execute(
                    "INSERT OR IGNORE INTO associations(memory_id,kind,value) VALUES(?,?,?)",
                    (memory_id, "link", link_val),
                )
            for kind in ("trigger", "project", "topic"):
                plural = kind + "s"
                for val in assoc.get(plural, []):
                    cur.execute(
                        "INSERT OR IGNORE INTO associations(memory_id,kind,value) VALUES(?,?,?)",
                        (memory_id, kind, val),
                    )

    def export_all(self) -> Dict[str, Any]:
        """Return full data in the legacy JSON-compatible format."""
        memories: Dict[str, Any] = {}
        for mem in self.iter_all_memories():
            mem_id = mem["id"]
            mem["tags"] = self.get_tags(mem_id)
            mem["associations"] = self.get_associations(mem_id)
            mem["access_history"] = self.get_access_history(mem_id)
            memories[mem_id] = mem

        cur = self._conn.cursor()
        cur.execute("SELECT value FROM meta WHERE key='created_at'")
        row = cur.fetchone()
        created_at = row[0] if row else datetime.now(timezone.utc).isoformat()

        return {
            "version": _SCHEMA_VERSION,
            "created_at": created_at,
            "config": {
                "priority_decay_params": {
                    k: {"a": v[0], "b": v[1]}
                    for k, v in _DEFAULT_PRIORITY_DECAY.items()
                },
            },
            "memories": memories,
        }

    # -- internal helpers ---------------------------------------------------

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["permanent"] = bool(d["permanent"])
        return d


# ---------------------------------------------------------------------------
# Migration helper: JSON → SQLite
# ---------------------------------------------------------------------------

def _migrate_json_to_sqlite(json_path: str, storage: _SQLiteStorage) -> None:
    """One-time migration from legacy JSON storage to SQLite."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for mem in data.get("memories", {}).values():
        # Ensure consolidation_level exists for old records
        mem.setdefault("consolidation_level", 0)
        try:
            storage.insert_memory(mem)
        except sqlite3.IntegrityError:
            # Already migrated
            pass

    # Rename old file so migration doesn't re-run
    backup = json_path + ".bak"
    if not os.path.exists(backup):
        os.rename(json_path, backup)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MemorySystem:
    """
    Echo Memory System – A brain-like memory management system.

    Features:
    - SQLite-backed storage with WAL journaling and transactions
    - Power-law temperature decay with spaced-repetition bonuses
    - Automatic association building
    - Event-triggered memory wakeup
    - Vector-based semantic search (optional)
    """

    def __init__(
        self,
        storage_path: str = "~/.echo-memory.db",
        vector_db_enabled: bool = True,
        decay_schedule: str = "daily",
    ) -> None:
        """
        Initialize the Echo Memory System.

        Args:
            storage_path: Path to SQLite database file.
                          If a ``.json`` sibling exists it will be auto-migrated.
            vector_db_enabled: Enable vector database for semantic search.
            decay_schedule: Temperature decay schedule (daily/weekly).
        """
        self.storage_path: str = os.path.expanduser(storage_path)
        self.vector_db_enabled: bool = vector_db_enabled
        self.decay_schedule: str = decay_schedule

        self._storage = _SQLiteStorage(self.storage_path)

        # Auto-migrate legacy JSON if present
        json_candidate = os.path.splitext(self.storage_path)[0] + ".json"
        if os.path.exists(json_candidate):
            _migrate_json_to_sqlite(json_candidate, self._storage)

        # Vector search engine (optional) — untouched per constraints
        self.vector_engine: Any = None
        if vector_db_enabled:
            try:
                from .vector import VectorSearchEngine  # type: ignore[import-untyped]
                self.vector_engine = VectorSearchEngine()
            except ImportError:
                pass

    # -- kept for backward compat (some callers may read .data) -------------

    @property
    def data(self) -> Dict[str, Any]:
        """Legacy property: returns full data dict (expensive)."""
        return self._storage.export_all()

    # -- ID generation ------------------------------------------------------

    @staticmethod
    def _generate_id() -> str:
        return uuid.uuid4().hex[:8]

    # -- NLP helpers --------------------------------------------------------

    @staticmethod
    def _extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        chinese = re.findall(r"[\u4e00-\u9fff]{2,}", text)
        english = re.findall(r"[a-zA-Z]{3,}", text)
        keywords = [w for w in (chinese + english) if w.lower() not in _STOP_WORDS]
        return [kw for kw, _ in Counter(keywords).most_common(max_keywords)]

    @staticmethod
    def _extract_projects(text: str) -> List[str]:
        patterns = [r"[A-Z]{2,}", r"\b[A-Z][a-z]{3,}\b", r"[\u4e00-\u9fff]{2,}"]
        projects: set[str] = set()
        for pat in patterns:
            projects.update(re.findall(pat, text))
        return list(projects - _NON_PROJECTS)

    @staticmethod
    def _extract_topics(text: str) -> List[str]:
        text_lower = text.lower()
        return list({
            topic
            for topic, kws in _TOPIC_KEYWORDS.items()
            if any(kw in text_lower for kw in kws)
        })

    def _build_associations(self, text: str) -> Dict[str, List[str]]:
        return {
            "links": [],
            "triggers": self._extract_keywords(text),
            "projects": self._extract_projects(text),
            "topics": self._extract_topics(text),
        }

    # -- Public CRUD --------------------------------------------------------

    def create(
        self,
        title: str,
        content: str,
        category: str = "learning",
        priority: str = "P1",
        permanent: bool = False,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Create a new memory.

        Returns:
            Memory ID
        """
        mem_id = f"mem_{category}_{self._generate_id()}"
        now = datetime.now(timezone.utc).isoformat()
        associations = self._build_associations(title + " " + content)

        memory: Dict[str, Any] = {
            "id": mem_id,
            "title": title,
            "content": content,
            "category": category,
            "priority": priority,
            "permanent": permanent,
            "confidence": 1.0,
            "tags": tags or [],
            "created_at": now,
            "last_accessed": now,
            "last_used": now,
            "access_count": 0,
            "consolidation_level": 0,
            "temperature": 1.0,
            "state": "active",
            "associations": associations,
        }

        self._storage.insert_memory(memory)

        if self.vector_engine is not None:
            self.vector_engine.add_memory(memory)

        return mem_id

    def access(self, memory_id: str, trigger: str = "user_query") -> Optional[Dict[str, Any]]:
        """
        Access a memory, resetting its temperature to 1.0.

        Returns:
            Full memory dict or ``None`` if not found.
        """
        if not self._storage.memory_exists(memory_id):
            return None

        self._storage.record_access(memory_id, trigger)
        mem = self._storage.get_memory(memory_id)
        if mem is None:
            return None
        mem["tags"] = self._storage.get_tags(memory_id)
        mem["associations"] = self._storage.get_associations(memory_id)
        mem["access_history"] = self._storage.get_access_history(memory_id)
        return mem

    def search(
        self,
        query: str,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        min_temperature: float = 0.0,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search memories by query.

        Returns:
            List of ``(memory_dict, weighted_score)`` tuples.
        """
        query_lower = query.lower()
        candidates = self._storage.search_text(query_lower, categories, min_temperature)

        results: List[Tuple[Dict[str, Any], float]] = []

        for mem in candidates:
            mem_id = mem["id"]
            tags = self._storage.get_tags(mem_id)
            assoc = self._storage.get_associations(mem_id)

            score = 0.0

            if query_lower in mem["title"].lower():
                score += 5
            if query_lower in mem["content"].lower():
                score += 3
            for tag in tags:
                if query_lower in tag.lower():
                    score += 2
            for trigger in assoc.get("triggers", []):
                if query_lower in trigger.lower():
                    score += 2
            for project in assoc.get("projects", []):
                if query_lower in project.lower():
                    score += 3
            for topic in assoc.get("topics", []):
                if query_lower in topic.lower():
                    score += 2

            if score > 0:
                mem["tags"] = tags
                mem["associations"] = assoc
                mem["access_history"] = self._storage.get_access_history(mem_id)
                weighted = score * mem["temperature"]
                results.append((mem, weighted))

        results.sort(key=lambda x: x[1], reverse=True)

        # Association expansion
        final: List[Tuple[Dict[str, Any], float]] = list(results[:limit])
        seen_ids = {r[0]["id"] for r in final}

        for mem, _score in results[:limit]:
            for linked_id in mem["associations"].get("links", []):
                if linked_id not in seen_ids and self._storage.memory_exists(linked_id):
                    linked = self._storage.get_memory(linked_id)
                    if linked is not None:
                        linked["tags"] = self._storage.get_tags(linked_id)
                        linked["associations"] = self._storage.get_associations(linked_id)
                        linked["access_history"] = self._storage.get_access_history(linked_id)
                        final.append((linked, linked["temperature"] * 0.5))
                        seen_ids.add(linked_id)

        return final[:limit]

    # -- Temperature decay --------------------------------------------------

    def decay_temperatures(self) -> Dict[str, Any]:
        """
        Apply power-law temperature decay with spaced-repetition bonuses.

        Returns:
            Statistics about the decay operation.
        """
        stats: Dict[str, Any] = {
            "processed": 0,
            "state_changes": {
                "active_to_dormant": 0,
                "dormant_to_archived": 0,
            },
        }

        now = datetime.now(timezone.utc)
        updates: List[Tuple[float, str, str]] = []

        for mem in self._storage.iter_non_permanent():
            old_state = mem["state"]
            last_used = datetime.fromisoformat(mem["last_used"])
            hours = max((now - last_used).total_seconds() / 3600.0, 0.0)

            new_temp = _compute_temperature(
                hours,
                mem["priority"],
                mem["access_count"],
                mem.get("consolidation_level", 0),
            )
            new_state = _state_for_temperature(new_temp)

            updates.append((new_temp, new_state, mem["id"]))

            if old_state == "active" and new_state == "dormant":
                stats["state_changes"]["active_to_dormant"] += 1
            elif old_state == "dormant" and new_state == "archived":
                stats["state_changes"]["dormant_to_archived"] += 1

            stats["processed"] += 1

        if updates:
            self._storage.bulk_update_temperature(updates)

        return stats

    # -- Events -------------------------------------------------------------

    def on_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process an event to wake relevant memories.

        Returns:
            List of woken memory dicts.
        """
        event_type: Optional[str] = event.get("type")
        woken: List[Dict[str, Any]] = []

        target_ids: set[str] = set()

        if event_type == "project_access":
            project = event.get("project", "")
            target_ids.update(
                self._storage.get_memories_by_association("project", project.lower())
            )
        elif event_type == "keyword":
            keyword = event.get("keyword", "")
            # Search triggers that contain keyword
            for mem in self._storage.iter_all_memories():
                assoc = self._storage.get_associations(mem["id"])
                for trigger in assoc.get("triggers", []):
                    if keyword.lower() in trigger.lower():
                        target_ids.add(mem["id"])
                        break
        elif event_type == "topic":
            topic = event.get("topic", "")
            target_ids.update(
                self._storage.get_memories_by_association("topic", topic.lower())
            )

        if target_ids:
            now = datetime.now(timezone.utc).isoformat()
            updates: List[Tuple[float, str, str]] = []
            for mid in target_ids:
                mem = self._storage.get_memory(mid)
                if mem is None:
                    continue
                new_temp = min(mem["temperature"] + 0.3, 1.0)
                new_state = "active"
                updates.append((new_temp, new_state, mid))
                # Build the returned dict
                mem["temperature"] = new_temp
                mem["state"] = new_state
                mem["tags"] = self._storage.get_tags(mid)
                mem["associations"] = self._storage.get_associations(mid)
                mem["access_history"] = self._storage.get_access_history(mid)
                woken.append(mem)

            if updates:
                self._storage.bulk_update_temperature(updates)

        return woken

    # -- Association management ---------------------------------------------

    def add_link(self, memory_id_1: str, memory_id_2: str, strength: float = 1.0) -> None:
        """Create bidirectional association between two memories."""
        if self._storage.memory_exists(memory_id_1) and self._storage.memory_exists(memory_id_2):
            self._storage.add_link(memory_id_1, memory_id_2)

    def get_associations(self, memory_id: str) -> Optional[Dict[str, List[str]]]:
        """Get all associations for a memory."""
        if not self._storage.memory_exists(memory_id):
            return None
        return self._storage.get_associations(memory_id)

    def rebuild_associations(self) -> None:
        """Rebuild association network for all memories."""
        for mem in self._storage.iter_all_memories():
            assoc = self._build_associations(mem["title"] + " " + mem["content"])
            self._storage.rebuild_associations(mem["id"], assoc)

    # -- Stats / admin ------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        total = self._storage.total_count()
        return {
            "total_memories": total,
            "by_state": self._storage.count_by_state(),
            "by_category": self._storage.count_by_category(),
            "avg_temperature": self._storage.avg_temperature(),
        }

    def export(self, output_path: str, format: str = "json") -> None:
        """Export memories to file."""
        if format == "json":
            data = self._storage.export_all()
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def archive(self, memory_id: str) -> None:
        """Archive a memory to deep storage."""
        if self._storage.memory_exists(memory_id):
            self._storage.archive_memory(memory_id)

    def update(self, memory_id: str, **kwargs: Any) -> bool:
        """Update an existing memory."""
        if not self._storage.memory_exists(memory_id):
            return False
        return self._storage.update_memory(memory_id, **kwargs)

    def verify(self) -> List[Dict[str, str]]:
        """Verify memory system integrity."""
