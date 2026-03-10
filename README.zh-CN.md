# Echo - 类人脑记忆系统

> **记忆的回响，永不消散**

[🇬🇧 English](README.en.md) | [🇯🇵 日本語](README.ja.md)

---

## 🧠 概述

**Echo** 是一个模拟人类大脑记忆机制的智能记忆管理系统。

### 核心特性

- 🌡 **温度系统** - 记忆热度自然衰减，模拟人类遗忘曲线
- 🔗 **联想网络** - 记忆之间自动建立语义关联
- 🔄 **事件触发** - 通过项目、关键词、主题唤醒相关记忆
- 💾 **永不遗忘** - 记忆永久保存，只改变状态（活跃/休眠/深层）
- 🔍 **智能搜索** - 结合向量搜索、联想网络、温度权重的多维搜索

---

## 📖 系统架构

### 记忆生命周期

```
新记忆 → 近期记忆 → 长期记忆 → 深层记忆
  ↑         ↑         ↑         ↑
访问触发   事件唤醒   联想唤醒   沉睡
```

### 状态管理

| 状态 | 温度范围 | 搜索可见 | 说明 |
|------|----------|----------|------|
| **active** 活跃 | 0.5-1.0 | ✅ | 频繁访问 |
| **dormant** 休眠 | 0.1-0.5 | 🔍 联想 | 可被唤醒 |
| **archived** 深层 | 0.0-0.1 | ❌ | 强关联触发 |

### 温度衰减

```
优先级衰减率:
├── P0 (永久): ×0.99/天 (30天 → 0.74)
├── P1 (重要): ×0.97/天 (30天 → 0.40)
└── P2 (普通): ×0.95/天 (30天 → 0.22)
```

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/skewliness/echo-memory.git
cd echo-memory
pip install -r requirements.txt
```

### 基本使用

```python
from echo import MemorySystem

# 初始化
memory = MemorySystem()

# 创建记忆
memory.create(
    title="API 认证流程",
    content="使用 JWT Token，24小时过期...",
    category="workflow",
    priority="P0",
    permanent=True
)

# 搜索记忆
results = memory.search("API 认证")

# 访问记忆（更新温度）
memory.access(memory_id)

# 事件触发唤醒
memory.on_event({
    "type": "project_access",
    "project": "认证系统"
})
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [系统设计](docs/SYSTEM_DESIGN.md) | 架构设计、温度系统、联想网络 |
| [API 参考](docs/API.md) | 完整 API 函数文档 |
| [实现指南](docs/IMPLEMENTATION.md) | 实现细节与代码示例 |
| [最佳实践](docs/BEST_PRACTICES.md) | 使用模式与维护建议 |

---

## 🎯 使用场景

### 记忆分类

| 分类 | 用途 | 优先级建议 |
|------|------|------------|
| `config` | API、Token、配置 | P0-P1 |
| `workflow` | 工作流、规范、协议 | P0 |
| `learning` | 学习、设计、发现 | P1-P2 |
| `tool` | 工具、框架 | P1 |
| `project` | 项目、优化记录 | P1 |
| `temp` | 临时任务 | P2 |

### 典型模式

```python
# 1. API Token 存储
memory.create(
    title=f"API Token - {service_name}",
    content=f"Endpoint: {endpoint}\nToken: {token}",
    category="config",
    priority="P0",
    permanent=True
)

# 2. 工作流文档
memory.create(
    title=f"工作流 - {process_name}",
    content="## 步骤\n1. xxx\n2. xxx\n## 验证\nxxx",
    category="workflow",
    priority="P0",
    permanent=True
)

# 3. 从错误中学习
memory.create(
    title=f"Bug 修复 - {error_description}",
    content="## 问题\n## 根本原因\n## 解决方案\n## 预防措施",
    category="learning",
    priority="P1"
)
```

---

## 🔧 维护

### 每日任务

```python
# 温度衰减
memory.decay_temperatures()

# 清理过期临时记忆
memory.cleanup_expired()
```

### 每周任务

```python
# 重建联想网络
memory.rebuild_associations()

# 验证完整性
issues = memory.verify()
```

### 每月任务

```python
# 导出备份
memory.export(f"backup_{month}.json")

# 审查统计
stats = memory.get_stats()
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 🌟 致谢

感谢所有贡献者和使用者！

---

**Echo** - 记忆的回响，永不消散 🌀