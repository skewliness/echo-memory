# System Design / 系统设计 / システム設計

> **Version**: 2.0
> **Last Updated**: 2026-03-11
> **License**: MIT

---

## Table of Contents / 目录 / 目次

- [Design Philosophy / 设计理念 / 設計理念](#design-philosophy)
- [Architecture Overview / 架构概览 / アーキテクチャ概要)
- [Memory Model / 记忆模型 / 記憶モデル)
- [Temperature System / 温度系统 / 温度システム)
- [Association Network / 联想网络 / 連想ネットワーク)
- [State Management / 状态管理 / 状態管理)
- [Search Architecture / 搜索架构 / 検索アーキテクチャ)
- [Event System / 事件系统 / イベントシステム)

---

## Design Philosophy / 设计理念

### Core Principles / 核心原则 / コア原則

**Echo** is designed to simulate human brain memory mechanisms. The system follows these fundamental principles:

**Echo** は人間の脳記憶メカニズムをシミュレートするように設計されています。以下の基本原則に従います：

**Echo** 模拟人类大脑记忆机制，遵循以下核心原则：

1. **Never Forget / 永不遗忘 / 決して忘れない**
   - Memories are never deleted, only their state changes
   - All knowledge is preserved permanently
   - 记忆永不删除，只改变状态
   - 全ての知識は永続的に保存されます

2. **Natural Decay / 自然衰减 / 自然な減衰**
   - Memory temperature decays over time
   - Mimics human forgetting curve
   - 记忆热度随时间自然衰减
   - 人間の忘却曲線を模倣します

3. **Association-Based / 基于联想 / 連想ベース**
   - Memories link through semantic associations
   - Contextual recall through triggers
   - 记忆通过语义联想自动关联
   - トリガーを通じた文脈的な想起

4. **Event-Triggered / 事件触发 / イベントトリガー**
   - Specific events wake relevant memories
   - Project access, keywords, topics
   - 通过特定事件唤醒相关记忆
   - プロジェクトアクセス、キーワード、トピック

---

## Architecture Overview / 架构概览

### System Layers / 系统分层 / システム階層

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                   (Memory Operations API)                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Search Layer                           │
│          (Vector Search + Keyword Matching)                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Association Layer                        │
│            (Links, Triggers, Projects, Topics)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Temperature Layer                         │
│              (Decay, State Transitions)                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                            │
│              (JSON + Vector Database)                       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow / 数据流 / データフロー

```
Create Memory → Extract Features → Build Associations → Store
       │              │                   │               │
       │              ↓                   ↓               ↓
       │         Keywords            Semantic Links    Persist
       │         Projects            Trigger Words     Index
       │         Topics
       ↓
Search Query → Vector Match → Association Expand → Rank by Temp
                    │                 │                    │
                    ↓                 ↓                    ↓
              Semantic Similarity   Related Memories   Return Results
```

---

## Memory Model / 记忆模型

### Memory Lifecycle / 记忆生命周期 / 記憶のライフサイクル

```
┌──────────┐     Access      ┌──────────┐     Time      ┌──────────┐
│  Active  │ ←───────────────│ Recent   │ ←────────────│   Long   │
│  1.0°C   │    / Events     │  0.5°C   │    Decays    │  0.1°C   │
└──────────┘                  └──────────┘               └──────────┘
     │                                                         │
     │ Time Decays                                              │ Deep
     ↓                                                          ↓
┌──────────┐                                            ┌──────────┐
│ Archived │ ←──────────────────────────────────────────│  Deep    │
│  0.0°C   │    Association Wakeup Only                  │  0.0°C   │
└──────────┘                                            └──────────┘
```

### Memory States / 记忆状态 / 記憶の状態

| State | Temperature | Searchable | Wake Method |
|-------|-------------|------------|-------------|
| **active** | 0.5 - 1.0 | ✅ Direct | Access, Events |
| **dormant** | 0.1 - 0.5 | 🔍 Associative | Linked memories |
| **archived** | 0.0 - 0.1 | ❌ Deep only | Strong events |

| 状态 | 温度 | 可搜索 | 唤醒方式 |
|------|------|--------|----------|
| **active** | 0.5 - 1.0 | ✅ 直接 | 访问、事件 |
| **dormant** | 0.1 - 0.5 | 🔍 联想 | 关联记忆 |
| **archived** | 0.0 - 0.1 | ❌ 仅深层 | 强事件 |

---

## Temperature System / 温度系统

### Temperature Scale / 温度刻度 / 温度目盛

```
1.0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0.0
     │           │           │           │           │
  Boiling      Warm      Cooling      Cold      Frozen
   活跃        温和        冷却        寒冷        沉睡
```

### Decay Formula / 衰减公式 / 減衰公式

```
T(t) = T₀ × e^(-λ × t)

Where:
  T(t) = temperature at time t
  T₀   = initial temperature (1.0)
  λ    = decay rate based on priority
  t    = time since last access (days)
```

**Priority Decay Rates / 优先级衰减率 / 優先度減衰率:**

| Priority | Daily Rate | After 30 Days | Description |
|----------|------------|---------------|-------------|
| **P0** | ×0.99 | 0.74 | Permanent / 核心 |
| **P1** | ×0.97 | 0.40 | Important / 重要 |
| **P2** | ×0.95 | 0.22 | Normal / 普通 |

---

## Association Network / 联想网络

### Association Types / 联想类型 / 連想タイプ

```json
{
  "associations": {
    "links": ["mem_001", "mem_002"],      // Direct memory links
    "triggers": ["AI", "optimization"],   // Keyword triggers
    "projects": ["Project A"],            // Project context
    "topics": ["Architecture", "AI"]      // Topic categorization
  }
}
```

### Similarity Scoring / 相似度评分 / 類似度スコア

```
Similarity Score Calculation:

  Common Projects  → +3 points per match
  Common Topics    → +2 points per match  
  Common Triggers  → +1 points per match

  Threshold: ≥3 points creates automatic link
```

---

## State Management / 状态管理

### State Transition Rules / 状态转换规则 / 状態遷移ルール

```python
def determine_state(temperature):
    if temperature >= 0.5:
        return "active"
    elif temperature >= 0.1:
        return "dormant"
    else:
        return "archived"
```

### Transition Triggers / 转换触发器 / 遷移トリガー

| Trigger | Effect | From → To |
|---------|--------|-----------|
| Memory Access | temp = 1.0 | Any → active |
| Event Trigger | temp += 0.3 | dormant → active |
| Daily Decay | temp × rate | active → dormant → archived |
| Link Traversal | temp × 0.5 | archived → dormant |

---

## Search Architecture / 搜索架构

### Multi-Stage Search / 多阶段搜索 / マルチステージ検索

```
┌─────────────────────────────────────────────────────────────┐
│                    Search Query                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Stage 1: Vector Search                         │
│         Semantic similarity matching (weight: 1.0)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           Stage 2: Association Expansion                    │
│         Follow links, include related (weight: 0.5)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│             Stage 3: Temperature Ranking                    │
│         Sort by combined score × temperature                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Return Results                         │
│                  (deduplicated, ranked)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Event System / 事件系统

### Event Types / 事件类型 / イベントタイプ

```python
# Project Access Event
{
    "type": "project_access",
    "project": "Project Name",
    "action": "wakeup_relevant_memories"
}

# Keyword Trigger Event  
{
    "type": "keyword",
    "keyword": "search term",
    "action": "wakeup_matching_memories"
}

# Topic Event
{
    "type": "topic",
    "topic": "AI",
    "action": "wakeup_topic_memories"
}
```

### Event Processing / 事件处理 / イベント処理

```python
def process_event(event):
    results = []
    
    for memory in all_memories:
        if matches_event(memory, event):
            memory.state = "active"
            memory.temperature = min(memory.temperature + 0.3, 1.0)
            results.append(memory)
    
    return results
```

---

## Performance Considerations / 性能考虑

### Optimization Strategies / 优化策略 / 最適化戦略

1. **Vector Index Caching / 向量索引缓存**
   - Rebuild only when memories change
   - 记忆变化时才重建

2. **Association Limit / 联想限制**
   - Max links per memory: 50
   - Maximum depth traversal: 3
   - 每条记忆最多链接数和遍历深度

3. **Temperature Decay Batch / 温度衰减批处理**
   - Run once daily, not per-access
   - 每日运行一次，非每次访问

4. **Hot Memory Cache / 热记忆缓存**
   - Keep top 100 active in memory
   - 前100条活跃记忆常驻内存

---

## Security & Privacy / 安全与隐私

### Data Protection / 数据保护 / データ保護

- **Local Storage**: All data stored locally
- **No External APIs**: Privacy-first design
- **本地存储**: 所有数据本地保存
- **无外部 API**: 隐私优先设计

### Access Control / 访问控制 / アクセス制御

```python
def can_access_memory(memory, user_context):
    # Check category restrictions
    # Check confidence threshold
    # Verify project permissions
    return True
```

---

## Future Enhancements / 未来增强

### Planned Features / 计划功能 / 計画された機能

- [ ] Distributed memory synchronization
- [ ] Memory export/import formats
- [ ] Visualization tools for association graphs
- [ ] Machine learning-based decay optimization
- [ ] 分布式记忆同步
- [ ] 记忆导出/导入格式
- [ ] 联想图可视化工具
- [ ] 基于机器学习的衰减优化

---

**End of System Design Document / 系统设计文档结束 / システム設計ドキュメント終了**

For more information, see:
- [API Reference](API.md)
- [Implementation Guide](IMPLEMENTATION.md)
- [Best Practices](BEST_PRACTICES.md)