# 3. Redis Context Retriever — Kết nối dữ liệu nghiệp vụ thời gian thực vào Agent

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Vấn đề**: AI Agent cần trả lời *"Đơn hàng #12345 của tôi đang ở đâu?"* nhưng dữ liệu đơn hàng nằm trong PostgreSQL, không phải trong prompt.
> - **Context Retriever** = tầng trung gian tự động sinh ra Tools/Functions cho Agent truy vấn dữ liệu nghiệp vụ từ Redis mà không cần kỹ sư code API riêng.
> - **Workflow**: Schema Discovery → Auto-generate Redis Search Index → Agent gọi Tool `search_orders(user_id, status)` → Context Retriever query Redis → Trả kết quả về cho Agent.
> - Kết hợp với **Redis Data Integration (RDI)** để dữ liệu trong Redis luôn sync với DB nguồn (PostgreSQL/MySQL) via CDC (Change Data Capture).
> - Demo hoàn chỉnh: E-commerce Support Agent có thể trả lời câu hỏi về đơn hàng, tồn kho theo thời gian thực.

*← Quay lại: [2-agent-memory-architecture.md](./2-agent-memory-architecture.md)*
