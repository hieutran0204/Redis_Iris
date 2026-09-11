# 1. Redis Streams — Event-Driven Agent Loop

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Redis Streams vs Redis List vs Pub/Sub**: Tại sao Streams là lựa chọn duy nhất đúng cho Agent Task Queue (hỗ trợ Consumer Groups, ACK, replay).
> - Anatomy của 1 Agent Loop trên Redis Streams:
>   1. `XADD` — Agent Orchestrator đẩy task vào stream.
>   2. `XREADGROUP` — Worker Agent lấy task và xử lý.
>   3. `XACK` — Worker báo hoàn thành sau khi Tool call thành công.
>   4. `XPENDING` / `XCLAIM` — Giám sát và cướp lại task bị treo.
> - **Consumer Groups**: Cách scale nhiều Worker Agent song song xử lý task từ cùng 1 stream mà không xử lý trùng nhau.
> - **Human-in-the-loop**: Đẩy task cần phê duyệt của người dùng vào 1 stream riêng, Agent đợi `XREAD BLOCK`.

*← Quay lại: [3-redis-iris-platform](../3-redis-iris-platform/4-redis-flex-tiering-ram-ssd.md)*
