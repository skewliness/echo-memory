"""
Vector Search Engine for Echo Memory System (Optimized)

优化内容:
1. 中文支持 (BGE 模型)
2. 可插拔嵌入架构
3. 批量编码支持
4. 错误处理与重试
5. 完整类型注解
"""

import hashlib
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pyarrow as pa
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False

# ---------------------------------------------------------------------------
# Embedding Provider Interface
# ---------------------------------------------------------------------------

class EmbeddingProvider(ABC):
    """嵌入模型提供者抽象接口"""

    @abstractmethod
    def encode(self, texts: List[str]) -> List[List[float]]:
        """编码文本列表为向量列表"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """返回向量维度"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """模型名称"""
        pass


class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformers 嵌入提供者"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-zh-v1.5",  # 中文优化模型
        device: Optional[str] = None
    ):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._dim = 512  # 默认维度
        self._load_model()

    def _load_model(self) -> None:
        """延迟加载模型"""
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(
            self._model_name,
            device=self._device
        )
        # 获取实际维度
        self._dim = self._model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str]) -> List[List[float]]:
        """批量编码文本"""
        if self._model is None:
            self._load_model()
        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """返回实际向量维度"""
        return self._dim

    @property
    def name(self) -> str:
        return self._model_name


class MultilingualProvider(EmbeddingProvider):
    """多语言嵌入提供者（备用）"""

    def __init__(self):
        self._model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(self._model_name)

    def encode(self, texts: List[str]) -> List[List[float]]:
        if self._model is None:
            self._load_model()
        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        return 384

    @property
    def name(self) -> str:
        return self._model_name


class FallbackHashProvider(EmbeddingProvider):
    """基于哈希的降级嵌入提供者（无依赖）"""

    def __init__(self, dimension: int = 512):
        self._dimension = dimension
        self._name = f"hash_{dimension}d"

    def encode(self, texts: List[str]) -> List[List[float]]:
        """使用 SHA256 哈希生成伪向量"""
        vectors = []
        for text in texts:
            hash_obj = hashlib.sha256(text.encode('utf-8'))
            hash_bytes = hash_obj.digest()

            # 扩展到目标维度
            vector = [float(b) / 255.0 for b in hash_bytes]
            vector.extend([0.0] * (self._dimension - len(vector)))
            vectors.append(vector)
        return vectors

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def name(self) -> str:
        return self._name


# ---------------------------------------------------------------------------
# Vector Search Engine
# ---------------------------------------------------------------------------

class VectorSearchEngine:
    """
    向量搜索引擎 - 使用 LanceDB

    特性:
    - 支持中文 (BGE 模型)
    - 可插拔嵌入架构
    - 批量编码优化
    - 错误重试机制
    """

    def __init__(
        self,
        db_path: str = "~/.echo-memory/vector_db",
        provider: Optional[EmbeddingProvider] = None,
        retry_attempts: int = 3
    ):
        """
        初始化向量搜索引擎

        Args:
            db_path: 向量数据库存储路径
            provider: 嵌入模型提供者 (默认使用中文 BGE 模型)
            retry_attempts: 操作失败重试次数
        """
        self.db_path = os.path.expanduser(db_path)
        self.retry_attempts = retry_attempts

        # 初始化嵌入提供者
        if provider is None:
            try:
                self.provider = SentenceTransformerProvider()
            except Exception:
                # 降级到多语言模型
                try:
                    self.provider = MultilingualProvider()
                except Exception:
                    # 最终降级到哈希方案
                    self.provider = FallbackHashProvider()
        else:
            self.provider = provider

        # 初始化 LanceDB
        self.db = None
        self.table = None
        self._init_lancedb()

    def _init_lancedb(self) -> None:
        """初始化 LanceDB 连接和表"""
        try:
            import lancedb
            self.db = lancedb.connect(self.db_path)
            self._init_table()
        except ImportError:
            raise ImportError("lancedb is required for vector search")

    def _init_table(self) -> None:
        """初始化或加载向量表"""
        if not HAS_PYARROW:
            raise ImportError("pyarrow is required")

        try:
            self.table = self.db.open_table("memories")
            # 检查是否需要 schema 迁移
            self._migrate_schema_if_needed()
        except Exception:
            # 创建新表 - 使用当前模型的维度
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), self.provider.dimension)),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("temperature", pa.float32()),
                pa.field("updated_at", pa.string())
            ])
            self.table = self.db.create_table("memories", schema=schema)

    def _migrate_schema_if_needed(self) -> None:
        """检查并迁移旧 schema 到新 schema"""
        if not HAS_PYARROW:
            return

        existing_schema = self.table.schema
        schema_names = {field.name for field in existing_schema}

        # 检查是否缺少 updated_at 字段
        if "updated_at" not in schema_names:
            print("检测到旧 schema，正在迁移...")
            from datetime import datetime, timezone

            # 导出所有数据
            all_data = self.table.search().limit(10000).to_pandas()

            if len(all_data) == 0:
                # 空表，直接重建
                self.db.drop_table("memories")
                schema = pa.schema([
                    pa.field("id", pa.string()),
                    pa.field("vector", pa.list_(pa.float32(), self.provider.dimension)),
                    pa.field("title", pa.string()),
                    pa.field("content", pa.string()),
                    pa.field("temperature", pa.float32()),
                    pa.field("updated_at", pa.string())
                ])
                self.table = self.db.create_table("memories", schema=schema)
                print("  已重建空表 schema")
                return

            # 检查向量维度是否匹配
            vector_field = None
            for field in existing_schema:
                if field.name == "vector":
                    vector_field = field
                    break

            old_dim = None
            if vector_field and hasattr(vector_field.type, 'list_size'):
                old_dim = vector_field.type.list_size

            needs_reencode = (old_dim != self.provider.dimension)

            if needs_reencode:
                print(f"  向量维度不匹配 (旧:{old_dim} → 新:{self.provider.dimension})，重新编码...")

            # 准备迁移数据
            migrated_records = []
            now = datetime.now(timezone.utc).isoformat()

            for idx, (_, row) in enumerate(all_data.iterrows()):
                title = row.get("title", "")
                content = row.get("content", "")

                if needs_reencode:
                    # 使用新模型重新编码
                    text = title + " " + content
                    vector = self.provider.encode([text])[0]
                else:
                    vector = row["vector"]

                record = {
                    "id": row["id"],
                    "vector": vector,
                    "title": title,
                    "content": content,
                    "temperature": float(row.get("temperature", 1.0)),
                    "updated_at": now
                }
                migrated_records.append(record)

                if (idx + 1) % 10 == 0:
                    print(f"  处理进度: {idx + 1}/{len(all_data)}")

            # 删除旧表并创建新表
            self.db.drop_table("memories")
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), self.provider.dimension)),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("temperature", pa.float32()),
                pa.field("updated_at", pa.string())
            ])
            self.table = self.db.create_table("memories", schema=schema)

            # 重新导入数据
            self.table.add(migrated_records)
            print(f"  已迁移 {len(migrated_records)} 条记录到新 schema")

    def _retry_operation(self, operation, *args, **kwargs):
        """带重试的操作执行"""
        last_error = None
        for attempt in range(self.retry_attempts):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.retry_attempts - 1:
                    time.sleep(0.5 * (attempt + 1))  # 指数退避
                continue
        raise last_error

    def add_memory(
        self,
        memory: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> None:
        """
        添加记忆到向量数据库

        Args:
            memory: 记忆对象
            vector: 预计算的向量 (可选，未提供则自动计算)
        """
        if vector is None:
            text = memory["title"] + " " + memory.get("content", "")
            vector = self._retry_operation(
                self.provider.encode,
                [text]
            )[0]

        from datetime import datetime, timezone

        self._retry_operation(
            self.table.add,
            [{
                "id": memory["id"],
                "vector": vector,
                "title": memory["title"],
                "content": memory.get("content", "")[:500],
                "temperature": memory.get("temperature", 1.0),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }]
        )

    def add_memories_batch(
        self,
        memories: List[Dict[str, Any]]
    ) -> None:
        """
        批量添加记忆（性能优化）

        Args:
            memories: 记忆对象列表
        """
        if not memories:
            return

        # 批量编码文本
        texts = [
            m["title"] + " " + m.get("content", "")
            for m in memories
        ]
        vectors = self._retry_operation(self.provider.encode, texts)

        # 批量插入
        from datetime import datetime, timezone

        records = []
        for memory, vector in zip(memories, vectors):
            records.append({
                "id": memory["id"],
                "vector": vector,
                "title": memory["title"],
                "content": memory.get("content", "")[:500],
                "temperature": memory.get("temperature", 1.0),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })

        self._retry_operation(self.table.add, records)

    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            query: 搜索查询
            limit: 最大结果数
            min_score: 最小相似度分数

        Returns:
            搜索结果列表
        """
        query_vector = self._retry_operation(
            self.provider.encode,
            [query]
        )[0]

        results = self.table.search(query_vector).limit(limit).to_pandas()

        # LanceDB 返回的列名格式
        # 过滤低分结果并转换为字典
        filtered = []
        for _, row in results.iterrows():
            # LanceDB 可能使用 'score' 而不是 '_score'
            score = row.get('_score', row.get('score', 0))
            if float(score) >= min_score:
                filtered.append({
                    "id": row['id'],
                    "score": float(score),
                    "title": row.get('title', ''),
                    "temperature": float(row.get('temperature', 0.0))
                })

        return filtered

    def delete_memory(self, memory_id: str) -> None:
        """
        从向量数据库删除记忆

        Args:
            memory_id: 记忆 ID
        """
        # LanceDB 不直接支持删除，需要重建表
        # 这里使用过滤方式实现软删除
        all_results = self.table.search([]).limit(10000).to_pandas()
        to_keep = all_results[all_results['id'] != memory_id]

        if len(to_keep) < len(all_results):
            # 有数据需要删除，重建表
            if not HAS_PYARROW:
                raise ImportError("pyarrow is required")

            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), self.provider.dimension)),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("temperature", pa.float32()),
                pa.field("updated_at", pa.string())
            ])

            # 删除旧表
            self.db.drop_table("memories")
            # 创建新表
            self.table = self.db.create_table("memories", schema=schema)
            # 插入保留的数据
            if len(to_keep) > 0:
                self.table.add(to_keep.to_dict("records"))

    def update_memory(
        self,
        memory: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> None:
        """
        更新记忆向量

        Args:
            memory: 记忆对象
            vector: 新向量 (可选)
        """
        # LanceDB 更新策略: 删除旧记录后添加新的
        # 注意: 这对于大规模更新不够高效，但对于个人使用足够了
        try:
            self.delete_memory(memory["id"])
        except Exception:
            # 如果删除失败（记录不存在），直接添加
            pass

        self.add_memory(memory, vector)

    def get_stats(self) -> Dict[str, Any]:
        """获取向量数据库统计信息"""
        try:
            # LanceDB: 使用空的向量搜索获取所有记录
            # 注意：limit 需要设置得足够大
            count = len(self.table.to_pandas())
        except Exception:
            # 如果上面的方法失败，尝试搜索
            try:
                import numpy as np
                # 创建一个零向量用于搜索（仅为了计数）
                dummy_vector = [0.0] * self.provider.dimension
                count = len(self.table.search(dummy_vector).limit(10000).to_pandas())
            except Exception:
                count = 0

        return {
            "total_vectors": count,
            "vector_dimension": self.provider.dimension,
            "model_name": self.provider.name,
            "db_path": self.db_path
        }

    def rebuild_index(self) -> None:
        """重建向量索引（LanceDB 内建支持，这里占位）"""
        # LanceDB 的 HNSW 索引是自动维护的
        # 这个方法为未来扩展预留
        pass


# ---------------------------------------------------------------------------
# 工厂函数
# ---------------------------------------------------------------------------

def create_vector_engine(
    model: str = "bge-zh",  # "bge-zh", "multilingual", "hash"
    db_path: str = "~/.echo-memory/vector_db"
) -> VectorSearchEngine:
    """
    创建向量搜索引擎的工厂函数

    Args:
        model: 模型类型
            - "bge-zh": 中文 BGE 模型 (默认，推荐)
            - "multilingual": 多语言模型
            - "hash": 哈希降级方案
        db_path: 数据库路径

    Returns:
        VectorSearchEngine 实例
    """
    provider_map = {
        "bge-zh": lambda: SentenceTransformerProvider(),
        "multilingual": lambda: MultilingualProvider(),
        "hash": lambda: FallbackHashProvider()
    }

    provider = provider_map.get(model, provider_map["bge-zh"])()

    return VectorSearchEngine(db_path=db_path, provider=provider)
