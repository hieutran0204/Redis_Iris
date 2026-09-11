# Project 2 — Long-term Memory Agent

> 🚧 **Sắp ra mắt**
>
> **Mục tiêu**: Xây dựng một AI Chatbot có khả năng ghi nhớ thông tin và sở thích của người dùng xuyên suốt nhiều phiên hội thoại (persistent memory), không bị "quên" khi đóng tab hay khởi động lại server.
>
> **Stack**: Python + LangChain / LangGraph + Redis Stack (RedisJSON + RediSearch) + OpenAI / Gemini
>
> **Kiến trúc bộ nhớ** (triển khai từ Chương 3.2):
> - **Working Memory**: `RedisJSON` lưu toàn bộ conversation turns của session hiện tại. TTL = 4 giờ.
> - **Episodic Memory**: Sau mỗi session, LLM tóm tắt các facts quan trọng → Embed → Lưu vào **RediSearch Vector Index** (không TTL).
> - **Memory Retrieval**: Đầu mỗi session mới, embed câu hỏi hiện tại → Vector Search Episodic Memory → Inject top-K memories vào system prompt.
>
> **Demo flow**:
> - Session 1: Người dùng nhắc họ thích cà phê đen không đường và đang học Redis.
> - Session 2 (2 ngày sau): Chatbot chủ động nhắc đến Redis và hỏi về progress học tập.

*← Quay lại: [project-1](../project-1-semantic-cache-proxy/README.md)*
