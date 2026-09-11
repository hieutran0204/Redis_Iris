# 3. Inter-Agent Communication — Pub/Sub Bus cho Multi-Agent Fleet

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Pub/Sub vs Streams** cho inter-agent messaging: Pub/Sub (fire-and-forget, realtime broadcast) vs Streams (persistent, guaranteed delivery).
> - Khi nào dùng Pub/Sub giữa Agent: Thông báo trạng thái tức thì (Agent A báo cho Agent B "tôi đã xong subtask X"), không cần lưu lại lịch sử.
> - **Channel naming convention**: `agent:broadcast` (toàn fleet), `agent:{role}` (theo vai trò), `agent:{id}` (unicast tới 1 agent cụ thể).
> - Kết hợp Pub/Sub + Streams: Pub/Sub để signaling (trigger nhanh), Streams để truyền payload lớn (kết quả research, files).
> - Shared Workspace: Dùng `Hash` làm bảng trạng thái chung (blackboard pattern) — mọi Agent cùng đọc/ghi trạng thái global task.

*← Quay lại: [2-retry-idempotency-and-dlq.md](./2-retry-idempotency-and-dlq.md)*
