# 4. Security — ACL, TLS & Quản lý Credentials cho Multi-Agent System

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Phần A: Redis ACL (Access Control List)

> - **Vấn đề bảo mật**: Khi nhiều Agent service cùng kết nối Redis, không nên dùng chung 1 credential có full quyền.
> - **ACL Rule**: Giới hạn quyền của từng service:
>   - `Agent Memory Service` → chỉ được `READ/WRITE` trên namespace `agent:*:memory:*`.
>   - `LangCache Service` → chỉ được thao tác `FT.SEARCH`, `HGET`, `HSET` trên namespace `langcache:*`.
>   - `Monitoring Service` → chỉ được `INFO`, `MONITOR`, không được ghi bất kỳ key nào.
> - Lệnh cấu hình: `ACL SETUSER`, `ACL LIST`, `ACL WHOAMI`, `ACL LOG`.
> - Lưu ACL config vào file `aclfile` để persist qua restart.

## Phần B: TLS Encryption

> - Bật TLS trên Redis để mã hóa toàn bộ traffic Agent ↔ Redis (quan trọng khi deploy trên cloud / multi-region).
> - Cấu hình TLS trong `redis.conf`: `tls-port`, `tls-cert-file`, `tls-key-file`, `tls-ca-cert-file`.
> - Tích hợp Redis TLS Client trong Python (`redis-py` với `ssl=True`).

## Phần C: Secrets Management

> - **Không bao giờ hardcode Redis password** trong source code hoặc docker-compose → Dùng `.env` + `Docker Secrets` hoặc `HashiCorp Vault`.
> - Credential rotation: Thay đổi Redis password không downtime với Rolling restart.

*← Quay lại: [3-monitoring-and-observability.md](./3-monitoring-and-observability.md)*
