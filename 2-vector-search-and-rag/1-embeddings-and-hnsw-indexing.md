# 1. Embeddings & HNSW Indexing — Xây dựng Vector Database trên Redis

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - Vector Embedding là gì và tại sao nó là "DNA" của AI Agent Memory.
> - Tạo Vector Index bằng `FT.CREATE` với thuật toán **HNSW** (Hierarchical Navigable Small World) — cấu trúc bên trong, tham số `M`, `efConstruction`, `efRuntime` ảnh hưởng đến recall accuracy vs query speed.
> - **FLAT vs HNSW**: FLAT (brute-force, chính xác 100%) cho dataset nhỏ — HNSW (approximate, cực nhanh) cho dataset lớn.
> - Tích hợp với thư viện Embedding: `sentence-transformers`, `text-embedding-3-small` (OpenAI), `textembedding-gecko` (Google).
> - `FT.INFO` — Kiểm tra trạng thái, số lượng vector đã index, dung lượng RAM tiêu thụ.

*← Quay lại: [0-getting-started](../0-getting-started/3-how-to-start.md)*
