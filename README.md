# Echo - 类人脑记忆系统 / Brain-Like Memory System / 人脳のような記憶システム

> 记忆的回响，永不消散 / Memory echoes, never fade / 記憶の響き、決して消えない

---

## 🧠 概述 / Overview / 概要

**Echo** 是一个模拟人类大脑记忆机制的智能记忆管理系统。

**Echo** is an intelligent memory management system that simulates human brain memory mechanisms.

**Echo** は人間の脳記憶メカニズムをシミュレートしたインテリジェント記憶管理システムです。

### 核心特性 / Core Features / コア機能

- 🌡 **温度系统 / Temperature System / 温度システム** - 记忆热度自然衰减 / Memory heat naturally decays / 記憶の熱が自然に減衰
- 🔗 **联想网络 / Association Network / 連想ネットワーク** - 记忆自动关联 / Auto-linking memories / 記憶が自動的にリンク
- 🔄 **事件触发 / Event Triggering / イベントトリガー** - 通过事件唤醒记忆 / Wake memories by events / イベントで記憶を呼び覚ます
- 💾 **永不遗忘 / Never Forget / 決して忘れない** - 记忆永久保存 / Permanent storage / 記憶を永久保存
- 🔍 **智能搜索 / Smart Search / スマート検索** - 多维度搜索 / Multi-dimensional search / 多次元検索

---

## 📖 系统架构 / System Architecture / システム構造

### 记忆生命周期 / Memory Lifecycle / 記憶のライフサイクル

```
新记忆 → 近期记忆 → 长期记忆 → 深层记忆
New → Recent → Long-term → Deep
新規 → 最近 → 長期 → 深層
  ↑         ↑         ↑         ↑
  │         │         │         │
访问触发   事件唤醒   联想唤醒   沉睡
Access  Event     Associative  Dormant
アクセス  イベント   連想      休眠
```

### 状态管理 / State Management / 状態管理

| 状态 State | 温度 Temp | 搜索 Search | 搜索可见 Visible |
|-----------|-----------|-----------------|-----------------|
| **active** アクティブ | 0.5-1.0 | ✅ | 活跃 Frequently accessed 頻繁にアクセス |
| **dormant** 休眠 | 0.1-0.5 | 🔍 联想 Associative | 可唤醒 Can wake up 呼び覚せ可能 |
| **archived** アーカイブド | 0.0-0.1 | ❌ | 深层 Deep deep 深層 |

---

## 🚀 快速开始 / Quick Start / クイックスタート

### 安装 Installation / インストール

```bash
# Clone the repository
git clone https://github.com/yourname/echo-memory.git
cd echo-memory

# Install dependencies / 依赖をインストール
pip install -r requirements.txt
```

### 基本使用 Basic Usage / 基本的な使い方

```python
from echo import MemorySystem

# Initialize / 初期化
memory = MemorySystem()

# Create memory / 記憶を作成
memory.create(
    title="My First Memory",  # 我的第一个记忆 / 私の最初の記憶
    content="Important learning notes",  # 重要的学习笔记 / 重要な学習ノート
    category="learning",
    priority="P1"
)

# Search memories / 検索記憶
results = memory.search("learning notes")

# Access memory (updates temperature) / 記憶にアクセス（温度更新）
memory.access(memory_id)
```

---

## 🎯 核心概念 / Core Concepts / コアコンセプト

### 温度系统 Temperature System / 温度システム

记忆热度表示活跃程度 / Memory heat indicates activity / 記憶の熱度は活力度を表します

```
Just accessed: temperature = 1.0 (boiling) / 剛アクセス: 温度 = 1.0 (沸騰)
Daily decay / 毎日減衰:
  P0: ×0.99/day (30 days → 0.74) / 30日後 → 0.74
  P1: ×0.97/day (30 days → 0.40) / 30日後 → 0.40
  P2: ×0.95/day (30 days → 0.22) / 30日後 → 0.22
```

### 联想网络 Association Network / 連想ネットワーク

每条记忆包含联想信息 / Each memory contains association info / 各記憶は連想情報を含みます

```json
{
  "associations": {
    "links": ["mem_002", "mem_003"],      // Related memories / 関連記憶 / 関連する記憶
    "triggers": ["AI", "optimization"],   // Trigger words / トリガー語 / トリガーワード
    "projects": ["Project A"],           // Projects / プロジェクト / プロジェクト
    "topics": ["Architecture", "AI"]    // Topics / トピック / トピック
  }
}
```

### 事件触发 Event Triggering / イベントトリガーリング

```python
# Auto-wake relevant memories when accessing a project / プロジェクトアクセス時に関連記憶を自動で起床させる
memory.on_event({
    "type": "project_access",
    "project": "2FA",
    "action": "wakeup_relevant_memories"
})
```

---

## 📚 文档 / Documentation / ドキュメント

- [系统设计 / System Design / システム設計](docs/SYSTEM_DESIGN.md)
- [API 参考 / API Reference / APIリファレンス](docs/API.md)
- [实现指南 / Implementation Guide / 実装ガイド](docs/IMPLEMENTATION.md)
- [最佳实践 / Best Practices / ベストプラクティス](docs/BEST_PRACTICES.md)

---

## 🤝 贡献 / Contributing / コントリビュート

欢迎贡献 / Welcome to contribute / コントリビュート歓迎！

---

## 📄 许可证 / License / ライセンス

MIT License - 详见 [LICENSE](LICENSE) / 詳しくは [LICENSE](LICENSE) ファイルを参照してください

---

## 🌟 致谢 / Acknowledgments / 感謝

感谢所有贡献者和使用者！/ 感谢 all contributors and users! / 全ての貢献者とユーザーに感謝します！

---

**Echo** - 记忆的回响，永不消散 / Memory echoes, never fade / 記憶の響き、決して消えない
