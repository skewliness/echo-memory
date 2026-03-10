# Echo Memory System - Implementation Guide

> **版本**: 2.0
> **更新**: 2026-03-11

---

## 📋 目录

- [数据结构](#数据结构)
- [核心算法](#核心算法)
- [API 实现](#api-实现)
- [向量搜索集成](#向量搜索集成)
- [温度系统实现](#温度系统实现)
- [事件触发机制](#事件触发机制)

---

## 数据结构

### 记忆对象 (Memory Object)

```json
{
  "id": "mem_learn_001",
  "title": "记忆标题",
  "content": "记忆内容...",

  // === 基础属性 ===
  "category": "learning",
  "priority": "P0",
  "permanent": true,
  "confidence": 1.0,
  "tags": ["tag1", "tag2"],

  // === 时间追踪 ===
  "created_at": "2026-03-11T00:00:00Z",
  "last_accessed": "2026-03-11T00:00:00Z",
  "last_used": "2026-03-11T00:00:00Z",
  "access_count": 0,
  "access_history": [],

  // === 温度系统 ===
  "temperature": 1.0,
  "state": "active",

  // === 联想网络 ===
  "associations": {
    "links": ["mem_wf_001", "mem_cfg_003"],
    "triggers": ["双模型", "Opus"],
    "projects": ["2FA", "AI"],
    "topics": ["Architecture", "Workflow"]
  },

  // === 可选 ===
  "strength": 1.0,
  "expires_at": "2026-03-12T00:00:00Z"
}
```

---

## 核心算法

### 1. 关键词提取 (Keyword Extraction)

```python
import re

def extract_keywords(text, max_keywords=10):
    """提取中英文关键词"""
    # 中文词汇 (2个以上汉字)
    chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    # 英文词汇 (3个以上字母)
    english = re.findall(r'[a-zA-Z]{3,}', text)
    
    # 过滤停用词
    stop_words = {
        '这个', '那个', '可以', '需要', '应该',
        'the', 'and', 'for', 'with', 'this', 'that'
    }
    
    keywords = [w for w in (chinese + english) if w not in stop_words]
    
    # 统计词频，返回最常见的关键词
    from collections import Counter
    keyword_counts = Counter(keywords)
    
    return [kw for kw, _ in keyword_counts.most_common(max_keywords)]
```

### 2. 项目提取 (Project Extraction)

```python
def extract_projects(text):
    """提取项目名称"""
    patterns = [
        r'[A-Z]{2,}',  # 大写缩写
        r'\b[A-Z][a-z]{3,}\b',  # 大写开头的驼峰命名
        r'[\u4e00-\u9fff]{2,}',  # 中文项目名
    ]
    
    projects = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        projects.update(matches)
    
    # 过滤已知非项目词汇
    non_projects = {'The', 'This', 'That', 'AI', 'API', 'OK'}
    return list(projects - non_projects)
```

### 3. 主题提取 (Topic Extraction)

```python
def extract_topics(text):
    """提取主题分类"""
    topic_keywords = {
        'AI': ['AI', 'GPT', 'Claude', '模型', 'model', 'machine learning', 'ML'],
        'API': ['API', 'Token', 'endpoint', '接口', 'interface'],
        'Security': ['安全', 'security', 'vulnerability', '漏洞', 'audit', '审计'],
        'Optimization': ['优化', 'optimization', 'improve', '改进', 'enhance'],
        'Architecture': ['架构', 'architecture', 'design', '设计', 'system', '系统'],
        'Workflow': ['工作流', 'workflow', 'process', '流程', 'pipeline'],
        'Memory': ['记忆', 'memory', 'vector', '向量', 'storage', '存储']
    }
    
    text_lower = text.lower()
    topics = []
    
    for topic, keywords in topic_keywords.items():
        if any(kw.lower() in text_lower for kw in keywords):
            topics.append(topic)
    
    return list(set(topics))
```

### 4. 相似度计算 (Similarity Calculation)

```python
def calculate_association_score(mem1, mem2):
    """计算两段记忆的关联分数"""
    score = 0
    
    # 共同项目 (+3分)
    common_projects = set(mem1["associations"]["projects"]) & set(mem2["associations"]["projects"])
    score += len(common_projects) * 3
    
    # 共同主题 (+2分)
    common_topics = set(mem1["associations"]["topics"]) & set(mem2["associations"]["topics"])
    score += len(common_topics) * 2
    
    # 共同触发词 (+1分)
    common_triggers = set(mem1["associations"]["triggers"]) & set(mem2["associations"]["triggers"])
    score += len(common_triggers)
    
    # 标签重叠 (+1分)
    common_tags = set(mem1["tags"]) & set(mem2["tags"])
    score += len(common_tags) * 0.5
    
    return score
```

---

## API 实现

### MemorySystem 类

```python
from datetime import datetime, timezone
import json

class MemorySystem:
    def __init__(self, storage_path="~/.memory-tree.json"):
        self.storage_path = os.path.expanduser(storage_path)
        self.data = self._load()
    
    def _load(self):
        """加载记忆树"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save(self):
        """保存记忆树"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def create(self, title, content, category="learning", priority="P1", 
              permanent=False, tags=None):
        """创建新记忆"""
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
        """访问记忆，更新温度"""
        if memory_id not in self.data["memories"]:
            return None
        
        memory = self.data["memories"][memory_id]
        
        # 更新温度
        memory["temperature"] = 1.0
        memory["state"] = "active"
        memory["last_used"] = datetime.now(timezone.utc).isoformat()
        memory["access_count"] += 1
        
        # 记录访问历史
        memory["access_history"].append({
            "at": datetime.now(timezone.utc).isoformat(),
            "trigger": trigger
        })
        
        self._save()
        
        return memory
    
    def search(self, query, limit=10):
        """智能搜索"""
        query_lower = query.lower()
        results = []
        
        for memory in self.data["memories"].values():
            score = 0
            
            # 标题匹配
            if query_lower in memory["title"].lower():
                score += 5
            
            # 内容匹配
            if query_lower in memory["content"].lower():
                score += 3
            
            # 标签匹配
            for tag in memory["tags"]:
                if query_lower in tag.lower():
                    score += 2
            
            # 触发词匹配
            for trigger in memory["associations"]["triggers"]:
                if query_lower in trigger.lower():
                    score += 2
            
            # 项目匹配
            for project in memory["associations"]["projects"]:
                if query_lower in project.lower():
                    score += 3
            
            # 主题匹配
            for topic in memory["associations"]["topics"]:
                if query_lower in topic.lower():
                    score += 2
            
            # 如果有匹配，添加到结果
            if score > 0:
                # 考虑温度权重
                weighted_score = score * memory["temperature"]
                results.append((memory, weighted_score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 联想唤醒 - 添加相关记忆
        final_results = list(results[:limit])
        seen_ids = {r[0]["id"] for r in final_results}
        
        for memory, score in results[:limit]:
            for linked_id in memory["associations"]["links"]:
                if linked_id not in seen_ids and linked_id in self.data["memories"]:
                    linked = self.data["memories"][linked_id]
                    # 关联记忆权重减半
                    final_results.append((linked, linked["temperature"] * 0.5))
                    seen_ids.add(linked_id)
        
        return final_results[:limit]
```

---

## 温度系统实现

### 温度衰减

```python
def decay_temperatures():
    """每日执行：衰减温度"""
    for memory in memories:
        # 永久记忆不衰减
        if memory["permanent"]:
            continue
        
        # 根据优先级计算衰减率
        decay_rates = {"P0": 0.01, "P1": 0.03, "P2": 0.05}
        rate = decay_rates.get(memory["priority"], 0.05)
        
        # 应用衰减
        memory["temperature"] *= rate
        
        # 更新状态
        if memory["temperature"] < 0.3:
            memory["state"] = "dormant"
        if memory["temperature"] < 0.1:
            memory["state"] = "archived"
```

### 访问时温度重置

```python
def on_memory_access(memory_id):
    """访问记忆时重置温度"""
    memory["temperature"] = 1.0
    memory["state"] = "active"
    memory["last_used"] = now()
```

---

## 事件触发机制

### 事件类型

```python
EVENT_TYPES = {
    "project_access": "访问项目时唤醒相关记忆",
    "keyword": "关键词触发",
    "error": "错误发生时唤醒相关记忆",
    "success": "成功时唤醒相关记忆"
}
```

### 事件处理

```python
def on_event(event, context=None):
    """处理事件并唤醒相关记忆"""
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
            # 唤醒记忆
            memory["state"] = "active"
            # 提升温度
            memory["temperature"] = min(memory["temperature"] + 0.3, 1.0)
```

---

## 向量搜索集成

### 使用 LanceDB

```python
import lancedb
import pyarrow as pa

class VectorSearchEngine:
    def __init__(self, db_path="~/.agent-memory/vector_db"):
        self.db_path = os.path.expanduser(db_path)
        self.db = lancedb.connect(self.db_path)
        self.table = None
    
    def create_table(self):
        """创建向量表"""
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 384)),
            pa.field("title", pa.string()),
            pa.field("content", pa.string()),
            pa.field("temperature", pa.float32())
        ])
        
        self.table = self.db.create_table("memories", schema=schema)
    
    def add_memory(self, memory, vector):
        """添加记忆到向量库"""
        self.table.add([{
            "id": memory["id"],
            "vector": vector,
            "title": memory["title"],
            "content": memory["content"][:500],
            "temperature": memory["temperature"]
        }])
    
    def search(self, query_vector, limit=10):
        """向量搜索"""
        results = self.table.search(query_vector).limit(limit).to_pandas()
        return results
```

---

## 最佳实践

### 1. 定期维护

```python
# 每日执行
decay_temperatures()

# 每周执行
cleanup_expired_memories()
rebuild_associations()
```

### 2. 记忆分类建议

| 场景 | 分类 | 优先级 |
|------|------|--------|
| API Token、配置 | config | P0-P1 |
| 重要架构设计 | workflow | P0 |
| 学习笔记 | learning | P1 |
| 临时任务 | temp | P2 |

### 3. 性能优化

```python
# 限制联想深度
MAX_ASSOCIATION_DEPTH = 3

# 缓存热记忆
cache = {}

# 后台重建索引
def rebuild_index_async():
    Thread(target=rebuild_vector_index).start()
```

---

## 扩展阅读

- [LanceDB 文档](https://lancedb.github.io/lancedb/)
- [Sentence-Transformers](https://www.sbert.net/)
- [记忆科学](https://en.wikipedia.org/wiki/Memory)

---

**文档结束**

如有问题或建议，欢迎提交 Issue！