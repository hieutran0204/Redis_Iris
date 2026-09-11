# 4. Redis Flex & RDI — Quản lý Dữ liệu Quy mô Lớn cho Agent Fleet

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Phần A: Redis Flex — Auto-Tiering RAM + SSD

> - **Bài toán**: Agent Fleet tích lũy hàng triệu vector memories theo thời gian → 100GB+ dữ liệu → RAM đắt tiền.
> - **Redis Flex hoạt động thế nào**: Tự động phân loại hot data (RAM, nanosecond) và cold data (NVMe SSD, microsecond) dựa trên access frequency.
> - **Khi nào cần Redis Flex**: Khi vector index > 10GB và đa số query chỉ tập trung vào ~20% data gần nhất (80/20 rule).
> - Cấu hình `crdb-cli` / Redis Cloud console để bật Tiering.
> - Đánh giá hiệu năng: Benchmark throughput & latency khi có và không có Flex.

## Phần B: Redis Data Integration (RDI) — Change Data Capture

> - **CDC là gì**: Cơ chế lắng nghe transaction log của DB nguồn (PostgreSQL WAL, MySQL binlog) và propagate thay đổi sang Redis gần như realtime (~vài giây độ trễ).
> - Cài đặt RDI pipeline: `source connector` (Debezium) → `transformation` → `target Redis stream`.
> - Đảm bảo Agent luôn làm việc trên dữ liệu mới nhất, không phải snapshot cũ trong cache.

*← Quay lại: [3-context-retriever.md](./3-context-retriever.md)*
