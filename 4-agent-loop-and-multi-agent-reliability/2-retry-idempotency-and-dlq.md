# 2. Retry, Idempotency & Dead-Letter Queue — Đảm bảo Độ tin cậy của Agent Loop

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Phần A: Retry & Idempotency

> - **Bài toán**: Agent gọi Tool `send_email(user_id=123)` → Server timeout → Agent retry → Email bị gửi 2 lần.
> - **Idempotency Key**: Tạo unique key cho mỗi Tool call bằng `SET idempotency:{tool}:{request_id} "processing" NX EX 300` — nếu key tồn tại thì không thực thi lại.
> - **Exponential Backoff + Jitter**: Chiến lược tăng dần thời gian chờ retry để tránh làm quá tải API ngoài.
> - `XPENDING` (PEL — Pending Entries List): Monitor các message chưa được ACK, phát hiện Worker bị crash.
> - `XCLAIM`: Tự động cướp lại task bị treo quá thời gian cho phép, giao cho Worker khác.

## Phần B: Dead-Letter Queue (DLQ)

> - **DLQ là gì**: Sau N lần retry thất bại, task được đẩy vào stream `agent:dlq` thay vì bị mất hoàn toàn.
> - Cấu trúc DLQ message: Metadata nguyên nhân lỗi, số lần retry đã thực hiện, timestamp, stack trace.
> - **Circuit Breaker pattern trên Redis**: Đếm số lỗi liên tiếp từ 1 Tool bằng `INCR`; khi vượt ngưỡng → chuyển trạng thái sang `OPEN` (từ chối mọi request tới Tool đó) → tự động thử lại sau khoảng thời gian `half-open`.

*← Quay lại: [1-streams-event-driven-loop.md](./1-streams-event-driven-loop.md)*
