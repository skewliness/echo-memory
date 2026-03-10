# Echo - Brain-Like Memory System

> **Memory echoes, never fade**

[🇨🇳 中文](README.zh-CN.md) | [🇯🇵 日本語](README.ja.md)

---

## 🧠 Overview

**Echo** is an intelligent memory management system that simulates human brain memory mechanisms.

### Core Features

- 🌡 **Temperature System** - Memory heat naturally decays following human forgetting curve
- 🔗 **Association Network** - Automatic semantic linking between memories
- 🔄 **Event Triggering** - Wake relevant memories via projects, keywords, topics
- 💾 **Never Forget** - Permanent storage, memories only change state (active/dormant/deep)
- 🔍 **Smart Search** - Multi-dimensional search combining vector, associations, temperature

---

## 📖 System Architecture

### Memory Lifecycle

```
New → Recent → Long-term → Deep
 ↑      ↑       ↑        ↑
Access Event Associative Dormant
```

### State Management

| State | Temperature | Searchable | Description |
|-------|-------------|------------|-------------|
| **active** | 0.5-1.0 | ✅ | Frequently accessed |
| **dormant** | 0.1-0.5 | 🔍 Associative | Can be woken up |
| **archived** | 0.0-0.1 | ❌ | Strong events only |

### Temperature Decay

```
Priority Decay Rates:
├── P0 (Permanent): ×0.99/day (30 days → 0.74)
├── P1 (Important): ×0.97/day (30 days → 0.40)
└── P2 (Normal): ×0.95/day (30 days → 0.22)
```

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/skewliness/echo-memory.git
cd echo-memory
pip install -r requirements.txt
```

### Basic Usage

```python
from echo import MemorySystem

# Initialize
memory = MemorySystem()

# Create memory
memory.create(
    title="API Authentication Flow",
    content="Use JWT tokens with 24h expiration...",
    category="workflow",
    priority="P0",
    permanent=True
)

# Search memories
results = memory.search("API authentication")

# Access memory (updates temperature)
memory.access(memory_id)

# Event-triggered wakeup
memory.on_event({
    "type": "project_access",
    "project": "AuthSystem"
})
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [System Design](docs/SYSTEM_DESIGN.md) | Architecture, temperature system, association networks |
| [API Reference](docs/API.md) | Complete API documentation |
| [Implementation Guide](docs/IMPLEMENTATION.md) | Implementation details and code examples |
| [Best Practices](docs/BEST_PRACTICES.md) | Usage patterns and maintenance recommendations |

---

## 🎯 Use Cases

### Memory Categories

| Category | Purpose | Priority |
|----------|---------|----------|
| `config` | APIs, Tokens, Settings | P0-P1 |
| `workflow` | Workflows, Procedures, Protocols | P0 |
| `learning` | Learnings, Designs, Discoveries | P1-P2 |
| `tool` | Tools, Frameworks | P1 |
| `project` | Project-specific knowledge | P1 |
| `temp` | Temporary tasks | P2 |

### Common Patterns

```python
# 1. API Token Storage
memory.create(
    title=f"API Token - {service_name}",
    content=f"Endpoint: {endpoint}\nToken: {token}",
    category="config",
    priority="P0",
    permanent=True
)

# 2. Workflow Documentation
memory.create(
    title=f"Workflow - {process_name}",
    content="## Steps\n1. xxx\n2. xxx\n## Verification\nxxx",
    category="workflow",
    priority="P0",
    permanent=True
)

# 3. Learning from Errors
memory.create(
    title=f"Bug Fix - {error_description}",
    content="## Problem\n## Root Cause\n## Solution\n## Prevention",
    category="learning",
    priority="P1"
)
```

---

## 🔧 Maintenance

### Daily Tasks

```python
# Temperature decay
memory.decay_temperatures()

# Cleanup expired temp memories
memory.cleanup_expired()
```

### Weekly Tasks

```python
# Rebuild associations
memory.rebuild_associations()

# Verify integrity
issues = memory.verify()
```

### Monthly Tasks

```python
# Export backup
memory.export(f"backup_{month}.json")

# Review statistics
stats = memory.get_stats()
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 🌟 Acknowledgments

Thanks to all contributors and users!

---

**Echo** - Memory echoes, never fade 🌀