# API Reference / API 参考 / API リファレンス

> **Version**: 2.0
> **Last Updated**: 2026-03-11
> **License**: MIT

---

## Table of Contents / 目录 / 目次

- [Core API / 核心 API / コア API](#core-api)
- [Memory Operations / 记忆操作 / 記憶操作)
- [Search Operations / 搜索操作 / 検索操作)
- [Temperature Management / 温度管理 / 温度管理)
- [Association Operations / 联想操作 / 連想操作)
- [Event Handlers / 事件处理 / イベント処理)
- [Utility Functions / 工具函数 / ユーティリティ関数)

---

## Core API / 核心 API

### MemorySystem Class / 记忆系统类 / 記憶システムクラス

```python
from echo import MemorySystem

# Initialize / 初始化
memory = MemorySystem(
    storage_path="~/.memory-tree.json",
    vector_db_enabled=True,
    decay_schedule="daily"
)
```

**Parameters / 参数 / パラメータ:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `storage_path` | str | `~/.memory-tree.json` | Path to memory storage file |
| `vector_db_enabled` | bool | `True` | Enable vector database |
| `decay_schedule` | str | `"daily"` | Temperature decay schedule |

---

## Memory Operations / 记忆操作

### create() / 创建记忆 / 記憶作成

Create a new memory.

新しい記憶を作成します。

创建新记忆。

```python
memory_id = memory.create(
    title="Memory Title",
    content="Memory content...",
    category="learning",
    priority="P1",
    tags=["tag1", "tag2"],
    permanent=False
)
```

**Parameters / 参数 / パラメータ:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | str | ✅ | Memory title |
| `content` | str | ✅ | Memory content |
| `category` | str | ❌ | Category: config/workflow/learning/tool/project/temp |
| `priority` | str | ❌ | Priority: P0/P1/P2 (default: P1) |
| `tags` | list | ❌ | Custom tags |
| `permanent` | bool | ❌ | Never decay (default: False) |

**Returns / 返回 / 戻り値:** `str` - Memory ID

**Example / 示例 / 例:**

```python
# Create a permanent workflow memory
mem_id = memory.create(
    title="API Authentication Flow",
    content="Use JWT tokens with 24h expiration...",
    category="workflow",
    priority="P0",
    permanent=True
)
```

---

### access() / 访问记忆 / 記憶アクセス

Access a memory, updating its temperature.

記憶にアクセスし、温度を更新します。

访问记忆，更新温度。

```python
memory_data = memory.access(
    memory_id="mem_learn_001",
    trigger="user_query"
)
```

**Parameters / 参数 / パラメータ:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memory_id` | str | ✅ | Memory ID to access |
| `trigger` | str | ❌ | What triggered the access |

**Returns / 返回 / 戻り値:** `dict` - Memory object with updated temperature

**Effects / 效果 / 効果:**
- Sets temperature to 1.0
- Sets state to "active"
- Records access in history

---

### update() / 更新记忆 / 記憶更新

Update an existing memory.

既存の記憶を更新します。

更新现有记忆。

```python
memory.update(
    memory_id="mem_learn_001",
    title="New Title",
    content="Updated content...",
    priority="P0"
)
```

**Parameters / 参数 / パラメータ:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memory_id` | str | ✅ | Memory ID to update |
| `title` | str | ❌ | New title |
| `content` | str | ❌ | New content |
| `priority` | str | ❌ | New priority |
| `tags` | list | ❌ | New tags |

**Returns / 返回 / 戻り値:** `bool` - Success status

---

### delete() / 删除记忆 / 記憶削除

**Deprecated**: Memories are never deleted, only archived.

**非推奨**: 記憶は削除されず、アーカイブされます。

**已弃用**: 记忆永不删除，仅归档。

```python
# Use archive instead / 代わりに archive を使用
memory.archive(memory_id="mem_learn_001")
```

---

### archive() / 归档记忆 / 記憶アーカイブ

Archive a memory to deep storage.

記憶をディープストレージにアーカイブします。

将记忆归档到深层存储。

```python
memory.archive(memory_id="mem_learn_001")
```

**Effects / 效果 / 効果:**
- Sets temperature to 0.0
- Sets state to "archived"
- Still accessible via strong associations

---

## Search Operations / 搜索操作

### search() / 搜索 / 検索

Search memories by query.

クエリで記憶を検索します。

通过查询搜索记忆。

```python
results = memory.search(
    query="API authentication",
    limit=10,
    categories=["workflow", "config"],
    min_temperature=0.1
)
```

**Parameters / 参数 / パラメータ:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | - | Search query |
| `limit` | int | 10 | Max results |
| `categories` | list | None | Filter by categories |
| `min_temperature` | float | 0.0 | Minimum temperature |
| `include_associations` | bool | True | Include linked memories |

**Returns / 返回 / 戻り値:** `list` - `[(memory, score), ...]`

**Example / 示例 / 例:**

```python
# Search for active workflow memories
results = memory.search(
    query="deployment process",
    categories=["workflow"],
    min_temperature=0.5,
    limit=5
)

for memory, score in results:
    print(f"{memory['title']} - Score: {score:.2f}")
```

---

### search_by_project() / 按项目搜索 / プロジェクトで検索

Search memories associated with a project.

プロジェクトに関連する記憶を検索します。

按项目搜索记忆。

```python
results = memory.search_by_project(
    project="Project A",
    limit=20
)
```

---

### search_by_topic() / 按主题搜索 / トピックで検索

Search memories by topic.

トピックで記憶を検索します。

按主题搜索记忆。

```python
results = memory.search_by_topic(
    topic="Architecture",
    limit=20
)
```

---

## Temperature Management / 温度管理

### decay_temperatures() / 衰减温度 / 温度減衰

Apply temperature decay to all memories.

すべての記憶に温度減衰を適用します。

对所有记忆应用温度衰减。

```python
stats = memory.decay_temperatures()
```

**Returns / 返回 / 戻り値:** `dict` - Statistics

```python
{
    "processed": 150,
    "state_changes": {
        "active_to_dormant": 12,
        "dormant_to_archived": 5
    }
}
```

---

### get_hot_memories() / 获取热记忆 / ホット記憶取得

Get most recently accessed memories.

最も最近アクセスされた記憶を取得します。

获取最近访问的记忆。

```python
hot = memory.get_hot_memories(limit=20)
```

**Returns / 返回 / 戻り値:** `list` - Memories with temp ≥ 0.5

---

### set_temperature() / 设置温度 / 温度設定

Manually set memory temperature.

記憶の温度を手動で設定します。

手动设置记忆温度。

```python
memory.set_temperature(
    memory_id="mem_learn_001",
    temperature=1.0
)
```

---

## Association Operations / 联想操作

### add_link() / 添加链接 / リンク追加

Create association between memories.

記憶間の連想を作成します。

在记忆之间创建联想。

```python
memory.add_link(
    memory_id_1="mem_001",
    memory_id_2="mem_002",
    strength=1.0
)
```

---

### get_associations() / 获取联想 / 連想取得

Get all associations for a memory.

記憶のすべての連想を取得します。

获取记忆的所有联想。

```python
associations = memory.get_associations(memory_id="mem_001")
```

**Returns / 返回 / 戻り値:**

```python
{
    "links": ["mem_002", "mem_003"],
    "triggers": ["AI", "optimization"],
    "projects": ["Project A"],
    "topics": ["Architecture"]
}
```

---

### rebuild_associations() / 重建联想 / 連想再構築

Rebuild association network.

連想ネットワークを再構築します。

重建联想网络。

```python
memory.rebuild_associations()
```

---

## Event Handlers / 事件处理

### on_event() / 事件处理 / イベント処理

Process an event to wake relevant memories.

イベントを処理して関連記憶を起床させます。

处理事件以唤醒相关记忆。

```python
woken_memories = memory.on_event({
    "type": "project_access",
    "project": "2FA",
    "action": "wakeup_relevant_memories"
})
```

**Event Types / 事件类型 / イベントタイプ:**

| Type | Description | Example |
|------|-------------|---------|
| `project_access` | Accessing a project | `{type: "project_access", project: "Name"}` |
| `keyword` | Keyword trigger | `{type: "keyword", keyword: "term"}` |
| `topic` | Topic trigger | `{type: "topic", topic: "AI"}` |

---

## Utility Functions / 工具函数

### get_stats() / 获取统计 / 統計取得

Get memory system statistics.

記憶システムの統計を取得します。

获取记忆系统统计。

```python
stats = memory.get_stats()
```

**Returns / 返回 / 戻り値:**

```python
{
    "total_memories": 150,
    "by_state": {
        "active": 45,
        "dormant": 78,
        "archived": 27
    },
    "by_category": {
        "config": 20,
        "workflow": 35,
        "learning": 95
    },
    "avg_temperature": 0.42
}
```

---

### export() / 导出 / エクスポート

Export memories to file.

記憶をファイルにエクスポートします。

导出记忆到文件。

```python
memory.export(
    output_path="memories_export.json",
    format="json"
)
```

**Formats / 格式 / フォーマット:** `json`, `csv`, `markdown`

---

### import_memories() / 导入记忆 / 記憶インポート

Import memories from file.

ファイルから記憶をインポートします。

从文件导入记忆。

```python
memory.import_memories(
    input_path="memories_export.json",
    merge_strategy="update"
)
```

**Merge Strategies / 合并策略 / マージ戦略:**

| Strategy | Description |
|----------|-------------|
| `replace` | Replace all memories |
| `update` | Update existing, add new |
| `skip` | Skip existing IDs |

---

### verify() / 验证 / 検証

Verify memory system integrity.

記憶システムの整合性を検証します。

验证记忆系统完整性。

```python
issues = memory.verify()
```

**Returns / 返回 / 戻り値:** `list` - Issues found (empty if OK)

```python
[
    {"type": "orphan_link", "memory_id": "mem_001", "target": "mem_999"},
    {"type": "missing_vector", "memory_id": "mem_002"}
]
```

---

## Complete Example / 完整示例 / 完全な例

```python
from echo import MemorySystem

# Initialize / 初期化
memory = MemorySystem()

# Create memory / 記憶作成
mem_id = memory.create(
    title="API Authentication Pattern",
    content="Use JWT with refresh tokens...",
    category="workflow",
    priority="P0"
)

# Search / 検索
results = memory.search("authentication")

# Access (updates temperature) / アクセス（温度更新）
memory.access(mem_id)

# Project event / プロジェクトイベント
memory.on_event({
    "type": "project_access",
    "project": "AuthSystem"
})

# Get stats / 統計取得
stats = memory.get_stats()
print(f"Total memories: {stats['total_memories']}")
```

---

**End of API Reference / API 参考结束 / API リファレンス終了**

For more information, see:
- [System Design](SYSTEM_DESIGN.md)
- [Implementation Guide](IMPLEMENTATION.md)
- [Best Practices](BEST_PRACTICES.md)