# 2. High Availability — Redis Sentinel & Redis Cluster cho Agent Fleet 24/7

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Phần A: Redis Sentinel — High Availability cho Agent State

> - **Kiến trúc**: 1 Master + N Replica + 3 Sentinel nodes → Tự động failover khi Master sập.
> - **Cơ chế bầu chọn (Election)**: Sentinels đạt quorum → Bầu chọn Replica mới nhất lên làm Master → Cập nhật DNS/config cho ứng dụng.
> - **Độ trễ Failover**: Thường 15–30 giây → Agent bị ngắt kết nối trong khoảng thời gian này → Tại sao cần **Retry + Circuit Breaker** (xem Chương 4.2) để xử lý.
> - Cấu hình trong `docker-compose.yml` cụm 3 Sentinel.

## Phần B: Redis Cluster — Sharding cho Vector Index quy mô lớn

> - **Khi nào cần Cluster**: Khi tổng dữ liệu (vector index + memory) vượt quá RAM của 1 máy đơn lẻ.
> - **Hash Slot**: Redis Cluster phân chia 16384 slots, mỗi Master sở hữu 1 phần — dữ liệu tự động route theo `CRC16(key) % 16384`.
> - **Thách thức với Vector Index trên Cluster**: Hiện tại RediSearch chạy trên 1 shard (không tự động distributed) → Chiến lược workaround bằng application-level routing.

## Phần C: Cấu hình Docker Compose môi trường dev HA

> - Setup cụm 3 Master + 3 Replica (tối thiểu cho Redis Cluster) ngay trên máy local để thực hành.

*← Quay lại: [1-persistence-and-dr-for-agent-memory.md](./1-persistence-and-dr-for-agent-memory.md)*
