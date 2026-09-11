# 2. Agent Memory Architecture — Phân tầng Bộ nhớ của AI Agent

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Tại sao AI Agent cần memory phân tầng**: LLM context window bị giới hạn (128K token) — không thể nhét toàn bộ lịch sử vào prompt.
> - **4 tầng bộ nhớ** và triển khai trên Redis:
>   1. **Sensory Buffer** (in-flight): Dữ liệu input tức thời, chưa xử lý — `RedisJSON` TTL ~30 giây.
>   2. **Working Memory** (Short-term): Context window hiện tại của task đang chạy — `RedisJSON` TTL ~4 giờ.
>   3. **Episodic Memory** (Long-term): Toàn bộ lịch sử cuộc trò chuyện đã xảy ra — Vector Index (`HNSW`), không TTL.
>   4. **Semantic Memory** (Knowledge): Kiến thức tổng hợp (facts extracted từ nhiều episode) — Vector Index, không TTL.
> - **Consolidation process**: Cron job định kỳ tóm tắt Working Memory → Episodic Memory trước khi nó hết TTL.
> - Thiết kế key schema: `agent:{agent_id}:memory:{layer}:{user_id}:{session_id}`.

*← Quay lại: [1-redis-langcache-semantic-cache.md](./1-redis-langcache-semantic-cache.md)*
