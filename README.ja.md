# Echo - 人脳のような記憶システム

> **記憶の響き、決して消えない**

[🇨🇳 中文](README.zh-CN.md) | [🇬🇧 English](README.en.md)

---

## 🧠 概要

**Echo** は人間の脳記憶メカニズムをシミュレートしたインテリジェント記憶管理システムです。

### コア機能

- 🌡 **温度システム** - 記憶の熱度は人間の忘却曲線に従って自然に減衰
- 🔗 **連想ネットワーク** - 記憶間の自動的な意味リンク
- 🔄 **イベントトリガー** - プロジェクト、キーワード、トピックで関連記憶を起床
- 💾 **決して忘れない** - 永続保存、記憶は状態のみ変化（アクティブ/休眠/深层）
- 🔍 **スマート検索** - ベクトル、連想、温度を組み合わせた多次元検索

---

## 📖 システムアーキテクチャ

### 記憶のライフサイクル

```
新規 → 最近 → 長期 → 深層
 ↑     ↑     ↑     ↑
アクセス イベント 連想 休眠
```

### 状態管理

| 状態 | 温度 | 検索可能 | 説明 |
|------|------|----------|------|
| **active** | 0.5-1.0 | ✅ | 頻繁にアクセス |
| **dormant** | 0.1-0.5 | 🔍 連想 | 起床可能 |
| **archived** | 0.0-0.1 | ❌ | 強いイベントのみ |

### 温度減衰

```
優先度減衰率:
├── P0 (永続): ×0.99/日 (30日後 → 0.74)
├── P1 (重要): ×0.97/日 (30日後 → 0.40)
└── P2 (通常): ×0.95/日 (30日後 → 0.22)
```

---

## 🚀 クイックスタート

### インストール

```bash
git clone https://github.com/skewliness/echo-memory.git
cd echo-memory
pip install -r requirements.txt
```

### 基本的な使い方

```python
from echo import MemorySystem

# 初期化
memory = MemorySystem()

# 記憶を作成
memory.create(
    title="API 認証フロー",
    content="JWTトークン使用、24時間有効期限...",
    category="workflow",
    priority="P0",
    permanent=True
)

# 記憶を検索
results = memory.search("API 認証")

# 記憶にアクセス（温度更新）
memory.access(memory_id)

# イベントトリガーで起床
memory.on_event({
    "type": "project_access",
    "project": "AuthSystem"
})
```

---

## 📚 ドキュメント

| ドキュメント | 説明 |
|-----------|------|
| [システム設計](docs/SYSTEM_DESIGN.md) | アーキテクチャ、温度システム、連想ネットワーク |
| [APIリファレンス](docs/API.md) | 完全なAPIドキュメント |
| [実装ガイド](docs/IMPLEMENTATION.md) | 実装の詳細とコード例 |
| [ベストプラクティス](docs/BEST_PRACTICES.md) | 使用パターンとメンテナンス推奨事項 |

---

## 🎯 使用シナリオ

### 記憶カテゴリ

| カテゴリ | 用途 | 優先度 |
|---------|------|--------|
| `config` | API、トークン、設定 | P0-P1 |
| `workflow` | ワークフロー、手順、プロトコル | P0 |
| `learning` | 学習、設計、発見 | P1-P2 |
| `tool` | ツール、フレームワーク | P1 |
| `project` | プロジェクト固有の知識 | P1 |
| `temp` | 一時的なタスク | P2 |

### 一般的なパターン

```python
# 1. APIトークン保存
memory.create(
    title=f"APIトークン - {service_name}",
    content=f"エンドポイント: {endpoint}\nトークン: {token}",
    category="config",
    priority="P0",
    permanent=True
)

# 2. ワークフロードキュメント
memory.create(
    title=f"ワークフロー - {process_name}",
    content="## ステップ\n1. xxx\n2. xxx\n## 検証\nxxx",
    category="workflow",
    priority="P0",
    permanent=True
)

# 3. エラーから学ぶ
memory.create(
    title=f"バグ修正 - {error_description}",
    content="## 問題\n## 根本原因\n## 解決策\n## 予防",
    category="learning",
    priority="P1"
)
```

---

## 🔧 メンテナンス

### 毎日のタスク

```python
# 温度減衰
memory.decay_temperatures()

# 期限切れの一時記憶をクリーンアップ
memory.cleanup_expired()
```

### 毎週のタスク

```python
# 連想を再構築
memory.rebuild_associations()

# 整合性を検証
issues = memory.verify()
```

### 毎月のタスク

```python
# バックアップをエクスポート
memory.export(f"backup_{month}.json")

# 統計を確認
stats = memory.get_stats()
```

---

## 📄 ライセンス

MIT License - 詳しくは [LICENSE](LICENSE) を参照してください

---

## 🤝 貢献

Issue と Pull Request を歓迎します！

---

## 🌟 謝辞

すべての貢献者とユーザーに感謝します！

---

**Echo** - 記憶の響き、決して消えない 🌀