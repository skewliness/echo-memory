# Echo Memory System - Implementation Guide

> **Version**: 2.0
> **Updated**: 2026-03-11
> **License**: MIT

---

## Table of Contents / 目录

- [Data Structures / 数据结构](#data-structures)
- [Core Algorithms / 核心算法](#core-algorithms)
- [API Implementation / API 实现](#api-implementation)
- [Vector Search Integration / 向量搜索集成](#vector-search-integration)
- [Temperature System / 温度系统实现](#temperature-system)
- [Event Triggering / 事件触发机制](#event-triggering)

---

## Data Structures / 数据结构

### Memory Object / 记忆对象

```json
{
  "id": "mem_learn_001",
  "title": "Memory Title",
  "content": "Memory content...",

  // === Basic Attributes / 基础属性 ===
  "category": "learning",
  "priority": "P0",
  "permanent": true,
  "confidence": 1.0,
  "tags": ["tag1", "tag2"],

  // === Time Tracking / 时间追踪 ===
  "created_at": "2026-03-11T00:00:00Z",
  "last_accessed": "2026-03-11T00:00:00Z",
  "last_used": "2026-03-11T00:00:00Z",
  "access_count": 0,
  "access_history": [],

  // === Temperature System / 温度系统 ===
  "temperature": 1.0,
  "state": "active",

  // === Association Network / 联想网络 ===
  "associations": {
    "links": ["mem_wf_001", "mem_cfg_003"],
    "triggers": ["AI", "optimization", "token"],
    "projects": ["E-Commerce", "MobileApp"],
    "topics": ["Architecture", "Workflow", "Security"]
  },

  // === Optional / 可选 ===
  "strength": 1.0,
  "expires_at": "2026-03-12T00:00:00Z"
}
```

---

## Core Algorithms / 核心算法

### 1. Keyword Extraction / 关键词提取

```python
import re
from collections import Counter

def extract_keywords(text, max_keywords=10):
    """Extract Chinese and English keywords / 提取中英文关键词"""
    
    # Chinese words (2+ characters) / 中文词汇
    chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    
    # English words (3+ letters) / 英文词汇
    english = re.findall(r'[a-zA-Z]{3,}', text)
    
    # Filter stop words / 过滤停用词
    stop_words = {
        'the', 'and', 'for', 'with', 'this', 'that',
        '这个', '那个', '可以', '需要', '应该'
    }
    
    keywords = [w for w in (chinese + english) if w not in stop_words]
    
    # Count frequency and return most common
    keyword_counts = Counter(keywords)
    
    return [kw for kw, _ in keyword_counts.most_common(max_keywords)]
```

---

### 2. Project Extraction / 项目提取

```python
def extract_projects(text):
    """Extract project names from text / 从文本提取项目名"""
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
```

---

### 3. Topic Extraction / 主题提取

```python
def extract_topics(text):
    """Extract topic categories / 提取主题分类"""
    topic_keywords = {
        'AI': ['AI', 'GPT', 'model', 'machine learning', 'ML', '模型'],
        'API': ['API', 'Token', 'endpoint', '接口', 'interface'],
        'Security': ['security', 'vulnerability', '漏洞', 'audit', '安全'],
        'Optimization': ['optimization', 'improve', '改进', '优化'],
        'Architecture': ['architecture', 'design', '系统', '架构'],
        'Workflow': ['workflow', 'process', '流程', 'pipeline'],
        'Database': ['database', 'SQL', 'query', '数据库'],
        'Frontend': ['frontend', 'UI', 'React', 'Vue', '前端']
    }
    
    text_lower = text.lower()
    topics = []
    
    for topic, keywords in topic_keywords.items():
        if any(kw.lower() in text_lower for kw in keywords):
            topics.append(topic)
    
    return list(set(topics))
```

---

### 4. Similarity Calculation / 相似度计算

```python
def calculate_association_score(mem1, mem2):
    """Calculate association score between two memories"""
    score = 0
    
    # Common projects (+3 points)
    common_projects = set(mem1["associations"]["projects"]) & set(mem2["associations"]["projects"])
    score += len(common_projects) * 3
    
    # Common topics (+2 points)
    common_topics = set(mem1["associations"]["topics"]) & set(mem2["associations"]["topics"])
    score += len(common_topics) * 2
    
    # Common triggers (+1 point)
    common_triggers = set(mem1["associations"]["triggers"]) & set(mem2["associations"]["triggers"])
    score += len(common_triggers)
    
    # Tag overlap (+0.5 points)
    common_tags = set(mem1["tags"]) & set(mem2["tags"])
    score += len(common_tags) * 0.5
    
    return score
```

---

## API Implementation / API 实现

### MemorySystem Class

```python
from datetime import datetime, timezone
import json
import os

class MemorySystem:
    def __init__(self, storage_path="~/.memory.json"):
        self.storage_path = os.path.expanduser(storage_path)
        self.data = self._load()
    
    def _load(self):
        """Load memory data"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save(self):
        """Save memory data"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def create(self, title, content, category="learning", priority="P1", 
              permanent=False, tags=None):
        """Create new memory"""
        mem_id = f"mem_{category}_{self._generate_id()}"
        
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
            
            "associations": {
                "links": [],
                "triggers": extract_keywords(title + " " + content),
                "projects": extract_projects(title + " " + content),
                "topics": extract_topics(title + " " + content)
            }
        }
        
        self.data["memories"][mem_id] = memory
        self._save()
        
        return mem_id
    
    def access(self, memory_id, trigger="user_query"):
        """Access memory and update temperature"""
        if memory_id not in self.data["memories"]:
            return None
        
        memory = self.data["memories"][memory_id]
        
        # Update temperature
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
    
    def search(self, query, limit=10):
        """Smart search with temperature weighting"""
        query_lower = query.lower()
        results = []
        
        for memory in self.data["memories"].values():
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
            
            # Trigger word match
            for trigger in memory["associations"]["triggers"]:
                if query_lower in trigger.lower():
                    score += 2
            
            # Project match
            for project in memory["associations"]["projects"]:
                if query_lower in project.lower():
                    score += 3
            
            # Topic match
            for topic in memory["associations"]["topics"]:
                if query_lower in topic.lower():
                    score += 2
            
            # Add to results if matched
            if score > 0:
                weighted_score = score * memory["temperature"]
                results.append((memory, weighted_score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Association expansion - add related memories
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
```

---

## Temperature System / 温度系统

### Temperature Decay / 温度衰减

```python
def decay_temperatures():
    """Daily task: Apply temperature decay"""
    for memory in memories:
        # Permanent memories don't decay
        if memory["permanent"]:
            continue
        
        # Decay rate by priority
        decay_rates = {"P0": 0.01, "P1": 0.03, "P2": 0.05}
        rate = decay_rates.get(memory["priority"], 0.05)
        
        # Apply decay
        memory["temperature"] *= rate
        
        # Update state
        if memory["temperature"] < 0.3:
            memory["state"] = "dormant"
        if memory["temperature"] < 0.1:
            memory["state"] = "archived"
```

---

### Access Temperature Reset / 访问时温度重置

```python
def on_memory_access(memory_id):
    """Reset temperature when memory is accessed"""
    memory = get_memory(memory_id)
    memory["temperature"] = 1.0
    memory["state"] = "active"
    memory["last_used"] = datetime.now(timezone.utc).isoformat()
```

---

## Event Triggering / 事件触发

### Event Types / 事件类型

```python
EVENT_TYPES = {
    "project_access": "Wake memories when accessing project",
    "keyword": "Trigger by keyword",
    "error": "Wake related memories on error",
    "success": "Wake related memories on success"
}
```

---

### Event Processing / 事件处理

```python
def on_event(event, context=None):
    """Process event and wake relevant memories"""
    event_type = event.get("type")
    
    for memory in memories:
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
        
        if should_wake:
            # Wake memory
            memory["state"] = "active"
            # Boost temperature
            memory["temperature"] = min(memory["temperature"] + 0.3, 1.0)
    
    return [m for m in memories if m["state"] == "active"]
```

---

## Vector Search Integration / 向量搜索集成

### Using LanceDB

```python
import lancedb
import pyarrow as pa

class VectorSearchEngine:
    def __init__(self, db_path="~/.echo-memory/vector_db"):
        self.db_path = os.path.expanduser(db_path)
        self.db = lancedb.connect(self.db_path)
        self.table = None
    
    def create_table(self):
        """Create vector table"""
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 384)),
            pa.field("title", pa.string()),
            pa.field("content", pa.string()),
            pa.field("temperature", pa.float32())
        ])
        
        self.table = self.db.create_table("memories", schema=schema)
    
    def add_memory(self, memory, vector):
        """Add memory to vector database"""
        self.table.add([{
            "id": memory["id"],
            "vector": vector,
            "title": memory["title"],
            "content": memory["content"][:500],
            "temperature": memory["temperature"]
        }])
    
    def search(self, query_vector, limit=10):
        """Vector search"""
        results = self.table.search(query_vector).limit(limit).to_pandas()
        return results
```

---

## Best Practices / 最佳实践

### 1. Regular Maintenance / 定期维护

```python
# Daily
decay_temperatures()

# Weekly
cleanup_expired_memories()
rebuild_associations()

# Monthly
export_backup()
verify_integrity()
```

---

### 2. Memory Category Guidelines / 记忆分类建议

| Scenario | Category | Priority |
|----------|----------|----------|
| API Tokens, Config | config | P0-P1 |
| Important Architecture | workflow | P0 |
| Learning Notes | learning | P1-P2 |
| Temporary Tasks | temp | P2 |

---

### 3. Performance Optimization / 性能优化

```python
# Limit association depth
MAX_ASSOCIATION_DEPTH = 3

# Cache hot memories
hot_cache = {}

# Background index rebuild
def rebuild_index_async():
    Thread(target=rebuild_vector_index).start()
```

---

## Further Reading / 扩展阅读

- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [Sentence-Transformers](https://www.sbert.net/)
- [Memory Science](https://en.wikipedia.org/wiki/Memory)

---

**End of Implementation Guide / 实现指南结束**

For questions or suggestions, please submit an Issue!