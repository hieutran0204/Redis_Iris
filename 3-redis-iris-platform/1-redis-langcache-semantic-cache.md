# 1. Redis LangCache — Semantic Caching cho LLM

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Vấn đề cốt lõi**: Người dùng hỏi *"Giờ mở cửa?"* và *"Shop mở lúc mấy giờ?"* → 2 câu khác nhau nhưng ý nghĩa như nhau → gọi LLM 2 lần = lãng phí tiền.
> - Kiến trúc Semantic Cache: Embed câu hỏi → So sánh Vector Similarity với cache store → Nếu Cosine > threshold thì trả về cached response.
> - Tích hợp với **LangChain `RedisSemanticCache`** và **LlamaIndex `RedisCache`**: 5 dòng code để bật lên.
> - Cấu hình Similarity Threshold — tìm điểm "golden" giữa cache hit rate và độ chính xác.
> - **Chiến lược invalidation**: Khi thông tin nguồn thay đổi (sản phẩm hết hàng, giá đổi), làm sao "xả" cache ngữ nghĩa đúng cách.
> - Đo lường hiệu quả: Dashboard theo dõi hit-rate, p99 latency saved, token cost saved.

*← Quay lại: [2-vector-search-and-rag](../2-vector-search-and-rag/4-vector-migration-guide.md)*
