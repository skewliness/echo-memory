"""
Echo Memory System - Core Implementation

A brain-like memory management system with:
- Temperature-based memory decay
- Association networks
- Event-triggered recall
- Never-forget storage
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import re
from collections import Counter


class MemorySystem:
    """
    Echo Memory System - A brain-like memory management system.
    
    Features:
    - Temperature-based natural decay
    - Automatic association building
    - Event-triggered memory wakeup
    - Vector-based semantic search
    """
    
    def __init__(
        self,
        storage_path: str = "~/.echo-memory.json",
        vector_db_enabled: bool = True,
        decay_schedule: str = "daily"
    ):
        """
        Initialize the Echo Memory System.
        
        Args:
            storage_path: Path to memory storage file
            vector_db_enabled: Enable vector database for semantic search
            decay_schedule: Temperature decay schedule (daily/weekly)
        """
        self.storage_path = os.path.expanduser(storage_path)
        self.vector_db_enabled = vector_db_enabled
        self.decay_schedule = decay_schedule
        
        # Initialize data structure
        self.data = self._load_or_create()
        
        # Vector search engine (optional)
        self.vector_engine = None
        if vector_db_enabled:
            try:
                from .vector import VectorSearchEngine
                self.vector_engine = VectorSearchEngine()
            except ImportError:
                print("Warning: Vector search dependencies not installed.")
                print("Install with: pip install lancedb sentence-transformers")
    
    def _load_or_create(self) -> Dict:
        """Load existing data or create new structure."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Create new structure
        return {
            "version": "2.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "config": {
                "vector_db_enabled": self.vector_db_enabled,
                "decay_schedule": self.decay_schedule,
                "priority_decay_rates": {
                    "P0": 0.01,
                    "P1": 0.03,
                    "P2": 0.05
                }
            },
            "memories": {}
        }
    
    def _save(self):
        """Save data to storage."""
        os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self) -> str:
        """Generate unique memory ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def create(
        self,
        title: str,
        content: str,
        category: str = "learning",
        priority: str = "P1",
        permanent: bool = False,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new memory.
        
        Args:
            title: Memory title
            content: Memory content
            category: Category (config/workflow/learning/tool/project/temp)
            priority: Priority level (P0/P1/P2)
            permanent: Never decay if True
            tags: Custom tags
        
        Returns:
            Memory ID
        """
        mem_id = f"mem_{category}_{self._generate_id()}"
        
        # Build associations
        associations = self._build_associations(title + " " + content)
        
        memory = {
            "id": mem_id,
            "title": title,
            "content": content,
            "category": category,
            "priority": priority,
            "permanent": permanent,
            "confidence": 1.0,
            "tags": tags or [],
            
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_accessed": datetime.now(timezone.utc).isoformat(),
            "last_used": datetime.now(timezone.utc).isoformat(),
            "access_count": 0,
            "access_history": [],
            
            "temperature": 1.0,
            "state": "active",
            
            "associations": associations
        }
        
        self.data["memories"][mem_id] = memory
        self._save()
        
        # Add to vector DB if enabled
        if self.vector_engine:
            self.vector_engine.add_memory(memory)
        
        return mem_id
    
    def _build_associations(self, text: str) -> Dict:
        """Build associations from text content."""
        return {
            "links": [],
            "triggers": self._extract_keywords(text),
            "projects": self._extract_projects(text),
            "topics": self._extract_topics(text)
        }
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Chinese words (2+ characters)
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        # English words (3+ letters)
        english = re.findall(r'[a-zA-Z]{3,}', text)
        
        # Filter stop words
        stop_words = {
            'the', 'and', 'for', 'with', 'this', 'that',
            '这个', '那个', '可以', '需要', '应该'
        }
        
        keywords = [w for w in (chinese + english) if w.lower() not in stop_words]
        
        # Count frequency
        keyword_counts = Counter(keywords)
        return [kw for kw, _ in keyword_counts.most_common(max_keywords)]
    
    def _extract_projects(self, text: str) -> List[str]:
        """Extract project names from text."""
        patterns = [
            r'[A-Z]{2,}',           # Uppercase acronyms
            r'\b[A-Z][a-z]{3,}\b',  # CamelCase
            r'[\u4e00-\u9fff]{2,}', # Chinese project names
        ]
        
        projects = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            projects.update(matches)
        
        # Filter known non-project terms
        non_projects = {'The', 'This', 'That', 'AI', 'API', 'OK', 'HTTP', 'JSON'}
        return list(projects - non_projects)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topic categories from text."""
        topic_keywords = {
            'AI': ['AI', 'GPT', 'model', 'machine learning', 'ML'],
            'API': ['API', 'Token', 'endpoint', 'interface'],
            'Security': ['security', 'vulnerability', 'audit'],
            'Optimization': ['optimization', 'improve'],
            'Architecture': ['architecture', 'design', 'system'],
            'Workflow': ['workflow', 'process', 'pipeline'],
            'Database': ['database', 'SQL', 'query'],
            'Frontend': ['frontend', 'UI', 'React', 'Vue']
        }
        
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(kw.lower() in text_lower for kw in keywords):
                topics.append(topic)
        
        return list(set(topics))
    
    def access(self, memory_id: str, trigger: str = "user_query") -> Optional[Dict]:
        """
        Access a memory, updating its temperature.
        
        Args:
            memory_id: Memory ID to access
            trigger: What triggered the access
        
        Returns:
            Memory object or None if not found
        """
        if memory_id not in self.data["memories"]:
            return None
        
        memory = self.data["memories"][memory_id]
        
        # Update temperature to 1.0
        memory["temperature"] = 1.0
        memory["state"] = "active"
        memory["last_used"] = datetime.now(timezone.utc).isoformat()
        memory["access_count"] += 1
        
        # Record access history
        memory["access_history"].append({
            "at": datetime.now(timezone.utc).isoformat(),
            "trigger": trigger
        })
        
        self._save()
        
        return memory
    
    def search(
        self,
        query: str,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        min_temperature: float = 0.0
    ) -> List[Tuple[Dict, float]]:
        """
        Search memories by query.
        
        Args:
            query: Search query
            limit: Maximum results
            categories: Filter by categories
            min_temperature: Minimum temperature threshold
        
        Returns:
            List of (memory, score) tuples
        """
        query_lower = query.lower()
        results = []
        
        for memory in self.data["memories"].values():
            # Category filter
            if categories and memory["category"] not in categories:
                continue
            
            # Temperature filter
            if memory["temperature"] < min_temperature:
                continue
            
            score = 0
            
            # Title match
            if query_lower in memory["title"].lower():
                score += 5
            
            # Content match
            if query_lower in memory["content"].lower():
                score += 3
            
            # Tag match
            for tag in memory["tags"]:
                if query_lower in tag.lower():
                    score += 2
            
            # Association matches
            for trigger in memory["associations"]["triggers"]:
                if query_lower in trigger.lower():
                    score += 2
            
            for project in memory["associations"]["projects"]:
                if query_lower in project.lower():
                    score += 3
            
            for topic in memory["associations"]["topics"]:
                if query_lower in topic.lower():
                    score += 2
            
            if score > 0:
                # Apply temperature weighting
                weighted_score = score * memory["temperature"]
                results.append((memory, weighted_score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Association expansion
        final_results = list(results[:limit])
        seen_ids = {r[0]["id"] for r in final_results}
        
        for memory, score in results[:limit]:
            for linked_id in memory["associations"]["links"]:
                if linked_id not in seen_ids and linked_id in self.data["memories"]:
                    linked = self.data["memories"][linked_id]
                    # Associated memories get half weight
                    final_results.append((linked, linked["temperature"] * 0.5))
                    seen_ids.add(linked_id)
        
        return final_results[:limit]
    
    def decay_temperatures(self) -> Dict:
        """
        Apply temperature decay to all memories.
        
        Returns:
            Statistics about decay operation
        """
        stats = {
            "processed": 0,
            "state_changes": {
                "active_to_dormant": 0,
                "dormant_to_archived": 0
            }
        }
        
        decay_rates = self.data["config"]["priority_decay_rates"]
        
        for memory in self.data["memories"].values():
            # Permanent memories don't decay
            if memory["permanent"]:
                continue
            
            old_state = memory["state"]
            rate = decay_rates.get(memory["priority"], 0.05)
            
            # Apply decay
            memory["temperature"] *= rate
            
            # Update state based on temperature
            if memory["temperature"] < 0.1:
                memory["state"] = "archived"
            elif memory["temperature"] < 0.3:
                memory["state"] = "dormant"
            else:
                memory["state"] = "active"
            
            # Track state changes
            if old_state == "active" and memory["state"] == "dormant":
                stats["state_changes"]["active_to_dormant"] += 1
            elif old_state == "dormant" and memory["state"] == "archived":
                stats["state_changes"]["dormant_to_archived"] += 1
            
            stats["processed"] += 1
        
        self._save()
        return stats
    
    def on_event(self, event: Dict) -> List[Dict]:
        """
        Process an event to wake relevant memories.
        
        Args:
            event: Event dictionary with 'type' key
        
        Returns:
            List of woken memories
        """
        event_type = event.get("type")
        woken_memories = []
        
        for memory in self.data["memories"].values():
            should_wake = False
            
            if event_type == "project_access":
                project = event.get("project", "")
                if project in memory["associations"]["projects"]:
                    should_wake = True
            
            elif event_type == "keyword":
                keyword = event.get("keyword", "")
                for trigger in memory["associations"]["triggers"]:
                    if keyword.lower() in trigger.lower():
                        should_wake = True
                        break
            
            elif event_type == "topic":
                topic = event.get("topic", "")
                if topic in memory["associations"]["topics"]:
                    should_wake = True
            
            if should_wake:
                # Wake memory
                memory["state"] = "active"
                # Boost temperature
                memory["temperature"] = min(memory["temperature"] + 0.3, 1.0)
                woken_memories.append(memory)
        
        self._save()
        return woken_memories
    
    def add_link(self, memory_id_1: str, memory_id_2: str, strength: float = 1.0):
        """Create association between two memories."""
        if memory_id_1 in self.data["memories"] and memory_id_2 in self.data["memories"]:
            # Add bidirectional links
            if memory_id_2 not in self.data["memories"][memory_id_1]["associations"]["links"]:
                self.data["memories"][memory_id_1]["associations"]["links"].append(memory_id_2)
            if memory_id_1 not in self.data["memories"][memory_id_2]["associations"]["links"]:
                self.data["memories"][memory_id_2]["associations"]["links"].append(memory_id_1)
            self._save()
    
    def get_associations(self, memory_id: str) -> Optional[Dict]:
        """Get all associations for a memory."""
        if memory_id in self.data["memories"]:
            return self.data["memories"][memory_id]["associations"]
        return None
    
    def rebuild_associations(self):
        """Rebuild association network for all memories."""
        for mem_id, memory in self.data["memories"].items():
            # Keep manual links, rebuild keywords/projects/topics
            manual_links = memory["associations"]["links"]
            memory["associations"] = self._build_associations(
                memory["title"] + " " + memory["content"]
            )
            memory["associations"]["links"] = manual_links
        self._save()
    
    def get_stats(self) -> Dict:
        """Get memory system statistics."""
        stats = {
            "total_memories": len(self.data["memories"]),
            "by_state": {"active": 0, "dormant": 0, "archived": 0},
            "by_category": {},
            "avg_temperature": 0.0
        }
        
        total_temp = 0.0
        
        for memory in self.data["memories"].values():
            state = memory["state"]
            stats["by_state"][state] = stats["by_state"].get(state, 0) + 1
            
            category = memory["category"]
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            total_temp += memory["temperature"]
        
        if stats["total_memories"] > 0:
            stats["avg_temperature"] = total_temp / stats["total_memories"]
        
        return stats
    
    def export(self, output_path: str, format: str = "json"):
        """Export memories to file."""
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        # Add other formats as needed
    
    def archive(self, memory_id: str):
        """Archive a memory to deep storage."""
        if memory_id in self.data["memories"]:
            memory = self.data["memories"][memory_id]
            memory["temperature"] = 0.0
            memory["state"] = "archived"
            self._save()
    
    def update(self, memory_id: str, **kwargs):
        """Update an existing memory."""
        if memory_id in self.data["memories"]:
            memory = self.data["memories"][memory_id]
            for key, value in kwargs.items():
                if key in memory and key not in ["id", "created_at"]:
                    memory[key] = value
            self._save()
            return True
        return False
    
    def verify(self) -> List[Dict]:
        """Verify memory system integrity."""
        issues = []
        
        for mem_id, memory in self.data["memories"].items():
            # Check for orphan links
            for linked_id in memory["associations"]["links"]:
                if linked_id not in self.data["memories"]:
                    issues.append({
                        "type": "orphan_link",
                        "memory_id": mem_id,
                        "target": linked_id
                    })
        
        return issues
