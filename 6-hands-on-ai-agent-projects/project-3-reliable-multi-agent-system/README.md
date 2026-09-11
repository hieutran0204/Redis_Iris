# Project 3 — Reliable Multi-Agent Research System

> 🚧 **Sắp ra mắt**
>
> **Mục tiêu**: Xây dựng một hệ thống Multi-Agent tự động hoàn thành tác vụ nghiên cứu phức tạp — điều phối qua **LangGraph** + giao tiếp qua **Redis Streams** + chịu lỗi qua **DLQ + Circuit Breaker**.
>
> **Stack**: Python + LangGraph + CrewAI + Redis Stack + `redis-py`
>
> **Kiến trúc các Agent**:
>
> | Agent | Vai trò | Tool |
> | :--- | :--- | :--- |
> | **Orchestrator** | Nhận task, phân rã subtask, phân công cho Worker Agents | ZSet Priority Queue |
> | **Research Agent** (x3) | Tìm kiếm web, đọc tài liệu, tổng hợp thông tin | Web Search, PDF Reader |
> | **Critic Agent** | Đánh giá chất lượng output của Research Agent | LLM Judge |
> | **Writer Agent** | Tổng hợp toàn bộ findings thành báo cáo cuối | LLM |
>
> **Tính năng Reliability**:
> - **Idempotent Task Processing**: Mỗi subtask có unique ID, không bị xử lý 2 lần dù Worker crash.
> - **Dead-Letter Queue**: Task thất bại sau 3 lần retry → DLQ → Alert Slack.
> - **LangGraph Checkpointer (Redis)**: Toàn bộ Graph State được snapshot sau mỗi node → Có thể resume sau khi hệ thống restart.
> - **Human-in-the-loop**: Orchestrator pause ở "Approval Gate" → Người dùng review trên dashboard → Approve/Reject.

*← Quay lại: [project-2](../project-2-long-term-memory-agent/README.md)*
