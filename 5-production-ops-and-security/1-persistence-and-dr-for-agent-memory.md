# 1. Persistence & Disaster Recovery cho Agent Memory

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Phần A: Chọn chiến lược Persistence phù hợp

| Loại dữ liệu Agent | Khuyến nghị Persistence | Lý do |
| :--- | :--- | :--- |
| **Session State** (Working Memory) | RDB mỗi 60 giây | Mất tối đa 1 phút dữ liệu là chấp nhận được, restart nhanh. |
| **Episodic Memory** (Long-term Vector) | AOF `appendfsync everysec` | Không thể mất ký ức dài hạn đã tích lũy; chấp nhận mất tối đa 1 giây. |
| **LangCache Store** | RDB hoặc không cần | Cache có thể rebuild lại, không cần hy sinh hiệu năng write. |
| **Task Queue** (Streams) | AOF `always` hoặc RDB | Task quan trọng không được mất giữa chừng. |

> - Cơ chế **RDB fork**: Tại sao `BGSAVE` không block Redis, rủi ro khi fork process quá lớn (Copy-on-Write overhead).
> - Cơ chế **AOF Rewrite**: Tại sao file AOF phình to theo thời gian và `BGREWRITEAOF` giải quyết vấn đề đó.
> - **Hybrid RDB + AOF**: Cấu hình tốt nhất cho hệ thống Agent chạy 24/7.

## Phần B: Backup & Disaster Recovery

> - Backup định kỳ file `dump.rdb` và `appendonly.aof` lên S3/GCS.
> - **Point-in-time Recovery**: Khôi phục agent memory về một thời điểm cụ thể trong quá khứ.
> - **RPO (Recovery Point Objective)** và **RTO (Recovery Time Objective)** — xác định SLA cho hệ thống Agent.

*← Quay lại: [4-agent-loop-and-multi-agent-reliability](../4-agent-loop-and-multi-agent-reliability/4-orchestration-with-langgraph-crewai.md)*
