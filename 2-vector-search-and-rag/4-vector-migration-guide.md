# 4. Vector Migration Guide — Chuyển dữ liệu Embeddings sang Redis

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Tại sao migrate sang Redis Vector?**: So sánh chi phí thực tế: Pinecone Serverless vs Redis Cloud vs tự host Redis Stack.
> - Migration từ **Pinecone** → Redis: Export namespace, chuyển đổi metadata schema, bulk import bằng `HSET` pipeline.
> - Migration từ **Qdrant** → Redis: Mapping collection config, payload filter → Redis TAG/NUMERIC field.
> - Migration từ **PGVector** (PostgreSQL) → Redis: Export `pgvector` table sang Redis HNSW Index, dùng Redis Data Integration (RDI) để đồng bộ liên tục.
> - **Chiến lược Zero-downtime Migration**: Chạy dual-write → Gradual traffic shift → Cutover.
> - Script Python tự động hóa quá trình migration (~200 dòng, có sẵn trong thư mục `/scripts`).

*← Quay lại: [3-rag-benchmarking-and-evaluation.md](./3-rag-benchmarking-and-evaluation.md)*
