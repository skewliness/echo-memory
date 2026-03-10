"""
Vector Search Engine for Echo Memory System
"""

import os


class VectorSearchEngine:
    """Vector-based semantic search using LanceDB."""
    
    def __init__(self, db_path: str = "~/.echo-memory/vector_db"):
        """
        Initialize vector search engine.
        
        Args:
            db_path: Path to vector database storage
        """
        self.db_path = os.path.expanduser(db_path)
        self.db = None
        self.table = None
        
        try:
            import lancedb
            self.db = lancedb.connect(self.db_path)
            self._init_table()
        except ImportError:
            raise ImportError("lancedb is required for vector search")
    
    def _init_table(self):
        """Initialize or load vector table."""
        import pyarrow as pa
        
        try:
            self.table = self.db.open_table("memories")
        except:
            # Create new table
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), 384)),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("temperature", pa.float32())
            ])
            self.table = self.db.create_table("memories", schema=schema)
    
    def add_memory(self, memory: dict, vector: list = None):
        """
        Add memory to vector database.
        
        Args:
            memory: Memory object
            vector: Pre-computed vector (optional, will compute if not provided)
        """
        if vector is None:
            vector = self._encode_text(memory["title"] + " " + memory["content"])
        
        self.table.add([{
            "id": memory["id"],
            "vector": vector,
            "title": memory["title"],
            "content": memory["content"][:500],
            "temperature": memory["temperature"]
        }])
    
    def _encode_text(self, text: str) -> list:
        """Encode text to vector using sentence transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode(text).tolist()
        except ImportError:
            # Fallback: simple hash-based vectors
            import hashlib
            import numpy as np
            
            # Create 384-dimensional vector from text hash
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Expand to 384 dimensions
            vector = list(float(b) / 255.0 for b in hash_bytes)
            vector.extend([0.0] * (384 - len(vector)))
            
            return vector
    
    def search(self, query: str, limit: int = 10) -> list:
        """
        Search by vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of search results
        """
        query_vector = self._encode_text(query)
        
        results = self.table.search(query_vector).limit(limit).to_pandas()
        
        return results.to_dict("records")
