# Echo Memory Skill

> **名称**: echo-memory
> **版本**: 1.0.0
> **类型**: 记忆增强

---

## 描述

为主人提供持久化、类脑记忆存储。自动记录重要信息，支持语义搜索和温度衰减。

**特性**：
- 持久化存储（SQLite + 向量数据库）
- 中文语义搜索（BGE 模型）
- 温度衰减 + 记忆巩固
- 联想网络

---

## 何时使用

**主动触发**（无需主人请求）：
- 主人分享技术方案、架构设计
- 主人记录项目决策、配置信息
- 主人提到错误解决、调试经验
- 主人分享代码片段、命令用法
- 主人讨论偏好、工作习惯

**被动触发**（主人明确请求）：
- "记住..." / "记录..."
- "搜索记忆..." / "回忆..."
- "我之前说过..." / "我写过..."

---

## 使用指南

### 创建记忆

```python
from echo.core import MemorySystem

ms = MemorySystem()
mem_id = ms.create(
    title="简短标题",
    content="详细内容",
    category="技术",  # config/project/workflow/error/preference
    priority="P1"     # P0(永久)/P1(重要)/P2(普通)
)
```

### 搜索记忆

```python
# 关键词搜索
results = ms.search("数据库优化", limit=5)

# 向量语义搜索
from echo.vector import VectorSearchEngine
ve = VectorSearchEngine()
results = ve.search("database performance", limit=5)
```

### 获取统计

```python
stats = ms.get_stats()
# {"total_memories": 10, "by_state": {...}, ...}
```

---

## 分类规范

| 分类 | 用途 | 示例 |
|------|------|------|
| `config` | 配置信息 | API 密钥、环境变量、系统设置 |
| `project` | 项目相关 | 架构决策、技术选型、代码位置 |
| `workflow` | 工作流程 | 部署步骤、调试流程、操作规范 |
| `error` | 错误解决 | Bug 修复、错误信息、解决方案 |
| `preference` | 用户偏好 | 习惯设置、工具选择、格式要求 |

---

## 优先级规范

| 级别 | 衰减速度 | 用途 |
|------|----------|------|
| `P0` | 不衰减 | 永久记忆（核心配置、重要决策） |
| `P1` | 慢衰减 | 重要信息（项目决策、错误方案） |
| `P2` | 快衰减 | 临时信息（会话上下文） |

---

## 注意事项

- 敏感信息不要记录（密钥、密码等）
- 记录前先检查是否已存在相似记忆
- 标题要简洁，内容要详细
- 定期清理低价值记忆
