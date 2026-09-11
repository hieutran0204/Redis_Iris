# 4. Orchestration với LangGraph & CrewAI — Redis làm Trái tim của Multi-Agent Graph

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Phần A: LangGraph + Redis

> - **LangGraph Checkpointer**: LangGraph lưu toàn bộ graph state (nodes, edges, intermediate results) sau mỗi step → Redis làm backend Checkpointer để hỗ trợ **pause-and-resume** (Agent bị interrupt có thể tiếp tục đúng chỗ đã dừng).
> - Tích hợp `RedisSaver` từ `langgraph-checkpoint-redis` package.
> - Pattern: **Interrupt → Human Review → Resume**: Agent pause tại node "Approval Required" → Người dùng xem xét trên UI → Approve → Agent tiếp tục từ điểm interrupt.

## Phần B: CrewAI + Redis

> - **Task State Management**: CrewAI Agent state lưu trên Redis Hash, task assignment qua Redis Streams.
> - **Shared Knowledge Base**: Toàn bộ crew chia sẻ 1 Vector Index trên Redis — khi Agent A research xong, Agent B có thể query ngay mà không cần truyền dữ liệu trực tiếp.
> - Monitoring crew performance: Queue depth, task completion rate, per-agent throughput.

## Phần C: Kiến trúc Graph-based Orchestration với Redis

> - **Blackboard Architecture**: Redis Hash làm "bảng đen" trung tâm, mọi Agent đọc/ghi trạng thái task.
> - **Priority Queue**: Redis ZSet làm priority queue cho Orchestrator phân công task theo urgency score.

*← Quay lại: [3-inter-agent-pubsub-bus.md](./3-inter-agent-pubsub-bus.md)*
