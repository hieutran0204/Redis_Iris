# 2.2 — Vector Similarity & Hybrid Search — Tìm kiếm Ngữ nghĩa cho RAG Pipeline

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - Ba hàm khoảng cách: **Cosine Similarity** (góc giữa 2 vector — tốt nhất cho text), **Inner Product** (cho embedding đã normalize), **L2 Euclidean** (khoảng cách vật lý — tốt cho ảnh).
> - `FT.SEARCH` với cú pháp `KNN` — truy vấn K Nearest Neighbors.
> - **Hybrid Search**: Kết hợp Vector Search với bộ lọc Metadata (Filter by category, timestamp, user_id) — quan trọng để tránh Agent lấy nhầm memory của user khác.
> - Pre-filter vs Post-filter: Trade-off về recall và performance.
> - Ví dụ thực tế: Chatbot tìm top-5 "ký ức" liên quan nhất của 1 user cụ thể trong long-term memory store.

*← Trước: [2.1 - Embeddings & HNSW Indexing](./1-embeddings-and-hnsw-indexing.md) | Tiếp theo: [2.3 - RAG Pipeline & Reranking](./3-rag-pipeline-and-reranking.md) →*
