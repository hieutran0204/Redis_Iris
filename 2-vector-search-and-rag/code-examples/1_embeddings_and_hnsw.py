"""
name: 1_embeddings_and_hnsw.py
description: Hands-on tutorial demonstrating HNSW Vector Index creation on RedisJSON, embedding generation, document storage, and FT.INFO health inspection.
"""

import os
import json
import numpy as np
import redis
from redis.commands.search.field import TextField, TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


def get_client() -> redis.Redis:
    pwd = os.getenv("REDIS_PASSWORD", "secret123")
    return redis.Redis(host="localhost", port=6379, password=pwd, db=0, decode_responses=True)


def get_embedding_generator():
    """
    Returns an embedding generator function.
    Tries to use sentence-transformers if installed; otherwise falls back to
    deterministic normalized NumPy vectors so the lab runs instantly without large dependencies.
    """
    try:
        from sentence_transformers import SentenceTransformer
        print("📦 [INFO] Đang tải mô hình SentenceTransformer ('all-MiniLM-L6-v2')...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        def embed_fn(text: str) -> list:
            vec = model.encode(text)
            return vec.tolist()
        
        return embed_fn, 384
    except ImportError:
        print("💡 [INFO] Gợi ý: Chưa cài đặt 'sentence-transformers'.")
        print("   -> Đang sử dụng Deterministic Embedding Generator (NumPy 128 dims) để chạy lab ngay lập tức!")
        print("   -> (Để dùng model thật: pip install sentence-transformers)\n")
        
        def embed_fn(text: str) -> list:
            # Deterministic pseudo-embedding based on hash of text for reproducibility
            np.random.seed(abs(hash(text)) % (2**32))
            vec = np.random.randn(128).astype(np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec.tolist()
            
        return embed_fn, 128


def main():
    try:
        client = get_client()
        client.ping()
    except Exception as e:
        print(f"\n❌ Lỗi kết nối Redis: {e}")
        print("Hãy đảm bảo container Docker 'redis-stack' đang chạy (docker compose up -d)!")
        return

    print("=" * 70)
    print("🎓 LAB 2.1: EMBEDDINGS & HNSW VECTOR INDEXING TRÊN REDIS")
    print("=" * 70)

    embed_fn, vector_dim = get_embedding_generator()
    index_name = "idx:agent_knowledge"
    doc_prefix = "knowledge:doc:"

    # 1. XÓA INDEX CŨ (NẾU CÓ) ĐỂ KHỞI TẠO MỚI
    try:
        client.ft(index_name).info()
        print(f"[*] Index '{index_name}' đã tồn tại từ trước. Đang xóa để khởi tạo lại...")
        client.ft(index_name).dropindex(delete_documents=True)
    except Exception:
        pass

    # 2. ĐỊNH NGHĨA SCHEMA CHO REDISEARCH + REDISJSON
    print(f"\n⚙️  BƯỚC 1: TẠO HNSW VECTOR INDEX ({vector_dim} CHIỀU, COSINE METRIC)...")
    schema = (
        TextField("$.title", as_name="title"),
        TagField("$.category", as_name="category"),
        VectorField(
            "$.embedding",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": vector_dim,
                "DISTANCE_METRIC": "COSINE",
                "M": 16,
                "EF_CONSTRUCTION": 200,
            },
            as_name="vector"
        )
    )

    definition = IndexDefinition(prefix=[doc_prefix], index_type=IndexType.JSON)
    client.ft(index_name).create_index(fields=schema, definition=definition)
    print(f"✅ Đã tạo thành công Vector Index: '{index_name}' trên Redis!")

    # 3. CHUẨN BỊ TÀI LIỆU VÀ TRÍCH XUẤT EMBEDDINGS
    print("\n📚 BƯỚC 2: TẠO TÀI LIỆU VÀ NẠP VECTOR VÀO REDISJSON...")
    knowledge_base = [
        {
            "id": "101",
            "title": "Chính sách bảo mật và xác thực đa yếu tố (2FA)",
            "content": "Tất cả nhân viên và hệ thống AI Agent bắt buộc phải bật 2FA khi truy cập production.",
            "category": "security"
        },
        {
            "id": "102",
            "title": "Quy trình hoàn tiền cho tài khoản khách hàng",
            "content": "Khách hàng có quyền yêu cầu hoàn tiền trong vòng 14 ngày làm việc kể từ ngày thanh toán.",
            "category": "billing"
        },
        {
            "id": "103",
            "title": "Cấu hình Connection Pooling và Retry cho Redis",
            "content": "Khuyến nghị sử dụng ConnectionPool với max_connections=50 và timeout 5 giây để tránh leak socket.",
            "category": "infra"
        }
    ]

    for item in knowledge_base:
        vec = embed_fn(item["content"])
        doc_key = f"{doc_prefix}{item['id']}"
        doc_data = {
            "title": item["title"],
            "content": item["content"],
            "category": item["category"],
            "embedding": vec
        }
        client.json().set(doc_key, "$", doc_data)
        print(f"   -> Đã lưu key: {doc_key} | Chủ đề: {item['title'][:40]}...")

    # 4. KIỂM TRA TRẠNG THÁI INDEX BẰNG FT.INFO
    print("\n🔍 BƯỚC 3: KIỂM TRA TÌNH TRẠNG CHỈ MỤC BẰNG FT.INFO...")
    info = client.ft(index_name).info()

    num_docs = info.get("num_docs", 0)
    indexing = info.get("indexing", "0")
    percent = float(info.get("percent_indexed", 1.0)) * 100

    print("-" * 50)
    print(f"📋 Báo cáo tình trạng Index '{index_name}':")
    print(f"   - Số tài liệu đã index : {num_docs} docs")
    print(f"   - Trạng thái quét ngầm : {'HOÀN TẤT' if indexing == '0' or not indexing else 'ĐANG XỬ LÝ'}")
    print(f"   - Tỉ lệ lập chỉ mục     : {percent:.1f}%")
    print("-" * 50)

    print("\n🎉 Chúc mừng! Bạn đã hoàn thành khởi tạo Vector Database trên Redis.")
    print("👉 Hãy mở Redis Insight (http://localhost:8001), mở tab Workbench hoặc Database")
    print(f"   để kiểm tra các key '{doc_prefix}*' và chỉ mục '{index_name}'!")


if __name__ == "__main__":
    main()
