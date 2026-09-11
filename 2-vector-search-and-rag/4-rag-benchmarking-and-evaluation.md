# 2.4 — RAG Benchmarking & Evaluation — Đo lường Chất lượng Retrieval

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - Tại sao cần đánh giá RAG: "Cảm giác tốt" không bằng số liệu — Agent trả lời đúng nhưng vì lý do sai.
> - **Recall@K**: Trong K kết quả trả về, bao nhiêu % là thực sự liên quan? Phương pháp tạo Golden Dataset để đo.
> - **Latency Percentile**: p50, p95, p99 của Vector Query — khi nào cần giảm `efRuntime` để đánh đổi recall lấy tốc độ.
> - **A/B Testing HNSW Parameters**: So sánh 2 cấu hình index khác nhau trên cùng query set.
> - **LangCache Hit-Rate Dashboard**: Đo % câu hỏi được phục vụ từ cache vs gọi LLM thật.
> - Tích hợp với `ragas` (framework đánh giá RAG open-source) + export metrics sang Grafana.

*← Trước: [2.3 - RAG Pipeline & Reranking](./3-rag-pipeline-and-reranking.md) | Tiếp theo: [2.5 - Vector Migration Guide](./5-vector-migration-guide.md) →*
