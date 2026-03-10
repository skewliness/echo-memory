# Best Practices / 最佳实践 / ベストプラクティス

> **Version**: 2.0
> **Last Updated**: 2026-03-11
> **License**: MIT

---

## Table of Contents / 目录 / 目次

- [Memory Organization / 记忆组织 / 記憶の整理](#memory-organization)
- [Category Guidelines / 分类指南 / カテゴリガイドライン)
- [Priority Selection / 优先级选择 / 優先度の選択)
- [Permanent Memory / 永久记忆 / 永続記憶)
- [Association Building / 联想构建 / 連想の構築)
- [Search Optimization / 搜索优化 / 検索の最適化)
- [Maintenance / 维护 / メンテナンス)
- [Common Patterns / 常见模式 / 一般的なパターン)

---

## Memory Organization / 记忆组织

### 1. Use Descriptive Titles / 使用描述性标题 / 説明的なタイトル

**❌ Bad / 悪い / 悪い:**

```python
memory.create(
    title="API stuff",
    content="..."
)
```

**✅ Good / 良い / 良い:**

```python
memory.create(
    title="Authentication API - JWT Token Refresh Flow",
    content="..."
)
```

---

### 2. Structure Content Properly / 正确构建内容 / コンテンツを適切に構造化

**Good structure / 良好的结构 / 良い構造:**

```python
content = """
## Overview / 概述 / 概要
Brief description of what this memory covers.

## Details / 详情 / 詳細
Step-by-step explanation...

## Code Example / 代码示例 / コード例
```python
# example code
```

## Notes / 备注 / メモ
Important caveats or warnings.
"""
```

---

## Category Guidelines / 分类指南

### Category Reference / 分类参考 / カテゴリリファレンス

| Category | Purpose / 用途 | Priority / 优先级 | Example / 示例 |
|----------|----------------|------------------|----------------|
| **config** | Configuration, API keys, settings | P0-P1 | API endpoints, tokens |
| **workflow** | Workflows, procedures, protocols | P0 | Deploy process, review flow |
| **learning** | Learnings, designs, discoveries | P1-P2 | Architecture findings |
| **tool** | Tools, frameworks, libraries | P1 | Docker, Git commands |
| **project** | Project-specific knowledge | P1 | Project decisions |
| **temp** | Temporary tasks, notes | P2 | Today's tasks |

---

### When to Use Each Category / 各分类使用时机 / 各カテゴリの使用时机

#### config / 配置 / 設定

**Use for / 用于 / 使用する場合:**
- API endpoints and tokens
- System configuration values
- Environment variables
- Authentication credentials

**Example / 示例 / 例:**

```python
memory.create(
    title="Production API - Service Name",
    content="Endpoint: https://api.example.com\nToken: xyz-123...",
    category="config",
    priority="P0",
    permanent=True
)
```

---

#### workflow / 工作流 / ワークフロー

**Use for / 用于 / 使用する場合:**
- Step-by-step procedures
- Deployment processes
- Code review protocols
- Testing workflows

**Example / 示例 / 例:**

```python
memory.create(
    title="Deployment Workflow - Production",
    content="""
1. Run tests: pytest
2. Build image: docker build
3. Tag version: git tag
4. Push to registry: docker push
5. Update deployment: kubectl apply
    """,
    category="workflow",
    priority="P0",
    permanent=True
)
```

---

#### learning / 学习 / 学習

**Use for / 用于 / 使用する場合:**
- New discoveries
- Architecture insights
- Problem solutions
- Research findings

**Example / 示例 / 例:**

```python
memory.create(
    title="Redis Caching Strategy Discovery",
    content="""
Found that Redis cache invalidation works best with:
- TTL-based expiration
- Write-through pattern
- Cache-aside for read-heavy
    """,
    category="learning",
    priority="P1"
)
```

---

## Priority Selection / 优先级选择

### Priority Guidelines / 优先级指南 / 優先度ガイドライン

| Priority | Use When / 使用时机 / 使用时机 | Decay Rate / 衰减率 |
|----------|---------------------|-------------|
| **P0** | Critical, core business, never forget | ×0.99/day |
| **P1** | Important, frequently needed | ×0.97/day |
| **P2** | Normal, occasional reference | ×0.95/day |

---

### Decision Tree / 决策树 / 決定木

```
Will this be needed in 6 months?
├── Yes → Is it core/critical?
│   ├── Yes → P0, permanent=True
│   └── No → P1
└── No → P2
```

---

## Permanent Memory / 永久记忆

### Mark Permanent When / 永久标记时机 / 永続マークタイミング

**Always set `permanent=True` for / 总是设为永久 / 常に永続として設定:**

- Core workflows and procedures
- Important API credentials
- Architecture design documents
- Security protocols
- Critical bug fixes

```python
memory.create(
    title="Security Audit Protocol",
    content="...",
    permanent=True  # Never decay
)
```

---

## Association Building / 联想构建

### Automatic vs Manual / 自动 vs 手动 / 自動 vs 手動

**System builds automatically / 系统自动构建 / システムが自動的に構築:**
- Keywords from content
- Project names from text
- Topic categories

**Add manually for / 手动添加用于 / 手動で追加:**
- Cross-reference relationships
- Prerequisite dependencies
- Related concepts

```python
# Manual link / 手动链接 / 手動リンク
memory.add_link("mem_auth_001", "mem_security_005")
```

---

## Search Optimization / 搜索优化

### Effective Queries / 有效查询 / 効果的なクエリ

**❌ Too broad / 太宽泛 / 広すぎる:**

```python
memory.search("API")  # Returns everything
```

**✅ Specific / 具体 / 具体的:**

```python
memory.search("JWT token refresh implementation")
```

---

### Use Category Filters / 使用分类过滤 / カテゴリフィルターを使用

```python
# Only search workflows / 仅搜索工作流 / ワークフローのみ検索
results = memory.search(
    "deployment",
    categories=["workflow"],
    min_temperature=0.5
)
```

---

### Temperature Filtering / 温度过滤 / 温度フィルタリング

```python
# Only active memories / 仅活跃记忆 / アクティブな記憶のみ
active_only = memory.search(
    query="important",
    min_temperature=0.5
)

# Include dormant / 包括休眠 / 休眠も含める
all_relevant = memory.search(
    query="important",
    min_temperature=0.1
)
```

---

## Maintenance / 维护

### Daily Tasks / 每日任务 / 毎日のタスク

```python
# Run temperature decay / 运行温度衰减 / 温度減衰を実行
memory.decay_temperatures()

# Check for expired temp memories / 检查过期临时记忆 / 期限切れの一時記憶をチェック
memory.cleanup_expired()
```

---

### Weekly Tasks / 每周任务 / 毎週のタスク

```python
# Rebuild associations / 重建联想 / 連想を再構築
memory.rebuild_associations()

# Verify integrity / 验证完整性 / 整合性を検証
issues = memory.verify()

# Optimize vector index / 优化向量索引 / ベクトルインデックスを最適化
memory.optimize_index()
```

---

### Monthly Tasks / 每月任务 / 毎月のタスク

```python
# Export backup / 导出备份 / バックアップをエクスポート
memory.export(f"backup_{month}.json")

# Review and archive / 审查和归档 / レビューとアーカイブ
stats = memory.get_stats()
for mem_id in stats['low_access']:
    memory.archive(mem_id)
```

---

## Common Patterns / 常见模式

### Pattern 1: API Token Storage / API Token 存储 / APIトークン保存

```python
memory.create(
    title=f"API Token - {service_name}",
    content=f"""
Service: {service_name}
Endpoint: {endpoint}
Token: {token}
Expires: {expiry_date}
    """,
    category="config",
    priority="P0",
    permanent=True,
    tags=["api", "token", service_name.lower()]
)
```

---

### Pattern 2: Learning from Errors / 从错误中学习 / エラーから学ぶ

```python
memory.create(
    title=f"Bug Fix - {error_description}",
    content=f"""
## Problem / 问题 / 問題
{what_went_wrong}

## Root Cause / 根本原因 / 根本原因
{root_cause}

## Solution / 解决方案 / 解決策
{fix_code}

## Prevention / 预防 / 予防
{how_to_prevent}
    """,
    category="learning",
    priority="P1"
)
```

---

### Pattern 3: Workflow Documentation / 工作流文档 / ワークフロードキュメント

```python
memory.create(
    title=f"Workflow - {process_name}",
    content=f"""
## Prerequisites / 前置条件 / 前提条件
- {prereq_1}
- {prereq_2}

## Steps / 步骤 / ステップ
1. {step_1}
2. {step_2}

## Verification / 验证 / 検証
{how_to_verify}
    """,
    category="workflow",
    priority="P0",
    permanent=True
)
```

---

### Pattern 4: Project Decision Log / 项目决策日志 / プロジェクト決定ログ

```python
memory.create(
    title=f"Decision - {project}: {decision_title}",
    content=f"""
## Context / 背景 / 背景
{situation}

## Decision / 决定 / 決定
{what_was_decided}

## Rationale / 理由 / 理由
{why_this_decision}

## Alternatives Considered / 考虑的替代方案 / 検討された代替案
- {alternative_1}
- {alternative_2}
    """,
    category="project",
    priority="P1",
    associations={
        "projects": [project],
        "topics": [topic_area]
    }
)
```

---

### Pattern 5: Event-Triggered Recall / 事件触发回忆 / イベントトリガー想起

```python
# When accessing a project / 访问项目时 / プロジェクトアクセス時
memory.on_event({
    "type": "project_access",
    "project": "MyProject",
    "action": "wakeup_relevant_memories"
})

# All memories related to MyProject become active
# / 所有与该项目相关的记忆变活跃
```

---

## Anti-Patterns / 反模式 / アンチパターン

### ❌ Don't: Vague Titles / 不要：模糊标题 / あいまいなタイトル

```python
# Bad / 悪い / 悪い
memory.create(title="Stuff", content="...")
```

### ❌ Don't: Wrong Categories / 不要：错误分类 / 間違ったカテゴリ

```python
# Bad: API token in learning / 恶劣：API token 放在 learning / 悪い: API tokenをlearningに
memory.create(title="API Key", content="...", category="learning")
```

### ❌ Don't: Ignore Priority / 不要：忽略优先级 / 優先度を無視

```python
# Bad: Core workflow as P2 / 恶劣：核心工作流设为 P2 / 悪い: コアワークフローをP2に
memory.create(title="Deploy Process", content="...", priority="P2")
```

### ❌ Don't: Overuse Permanent / 不要：滥用永久标记 / 永続マークの乱用

```python
# Bad: Temporary task as permanent / 恶劣：临时任务标记为永久 / 悪い: 一時タスクを永続に
memory.create(title="Buy milk", content="...", permanent=True)
```

---

## Performance Tips / 性能提示 / パフォーマンストヒント

### 1. Limit Association Links / 限制关联链接 / 連想リンクを制限

```python
# System automatically limits to 50 links per memory
# / 系统自动限制每条记忆 50 个链接
# / システムは各記憶のリンクを50に自動制限
MAX_LINKS_PER_MEMORY = 50
```

### 2. Use Temperature Filtering / 使用温度过滤 / 温度フィルタリングを使用

```python
# Faster searches by filtering / 通过过滤加速搜索 / フィルタリングで検索を高速化
results = memory.search(query, min_temperature=0.5)
```

### 3. Batch Operations / 批量操作 / バッチ操作

```python
# Batch decay instead of per-access / 批量衰减而非每次访问 / アクセスごとではなくバッチ減衰
# Run daily, not per-query / 每日运行，非每次查询 / 毎日実行、クエリごとに実行しない
```

---

## Monitoring / 监控 / モニタリング

### Track Memory Health / 追踪记忆健康 / 記憶の健全性を追跡

```python
stats = memory.get_stats()

# Check distribution / 检查分布 / 分布を確認
print(f"Active: {stats['by_state']['active']}")
print(f"Dormant: {stats['by_state']['dormant']}")
print(f"Archived: {stats['by_state']['archived']}")

# Monitor average temperature / 监控平均温度 / 平均温度を監視
print(f"Avg temp: {stats['avg_temperature']}")

# Target: 20-30% active, 50-60% dormant, rest archived
# / 目标：20-30% 活跃，50-60% 休眠，其余归档
# / 目標: 20-30% アクティブ、50-60% 休眠、残りアーカイブ
```

---

## Migration Guide / 迁移指南 / 移行ガイド

### From V1 to V2 / 从 V1 迁移到 V2 / V1からV2へ

**Key changes / 主要变化 / 主な変更:**

1. Add temperature field / 添加温度字段 / 温度フィールド追加
2. Add state field / 添加状态字段 / 状態フィールド追加
3. Build associations / 构建联想 / 連想の構築
4. Migrate categories / 迁移分类 / カテゴリの移行

**See / 见 / 参照:** [Implementation Guide](IMPLEMENTATION.md#migration)

---

**End of Best Practices / 最佳实践结束 / ベストプラクティス終了**

For more information, see:
- [System Design](SYSTEM_DESIGN.md)
- [API Reference](API.md)
- [Implementation Guide](IMPLEMENTATION.md)