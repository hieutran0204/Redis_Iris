# Project 1 — Semantic Cache Proxy cho LLM API

> 🚧 **Sắp ra mắt**
>
> **Mục tiêu**: Xây dựng một Proxy Service trong suốt (transparent proxy) đứng giữa ứng dụng và LLM API (OpenAI / Gemini / Claude). Proxy sẽ tự động cache các câu hỏi có ngữ nghĩa tương đương và trả về câu trả lời từ Redis thay vì gọi LLM, giúp tiết kiệm đến 90% chi phí token.
>
> **Stack**: Python (FastAPI) + Redis Stack (LangCache / RediSearch) + `sentence-transformers`
>
> **Tính năng cốt lõi**:
> - Nhận request từ ứng dụng theo đúng format OpenAI API.
> - Embed câu hỏi → Vector Similarity Search trên Redis.
> - Nếu similarity > threshold → Trả về cached response ngay lập tức.
> - Nếu cache miss → Forward đến LLM thật → Lưu kết quả vào cache để phục vụ lần sau.
> - Dashboard metrics: hit rate, tokens saved, latency distribution.

*← Quay lại: [5-production-ops-and-security](../5-production-ops-and-security/4-security-acl-and-tls.md)*
