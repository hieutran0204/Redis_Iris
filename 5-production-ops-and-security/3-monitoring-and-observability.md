# 3. Monitoring & Observability — Theo dõi Sức khỏe Hệ thống Agent

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:

## Metrics Cốt lõi cần theo dõi

| Metric | Lệnh Redis / Source | Ngưỡng Cảnh báo |
| :--- | :--- | :--- |
| **Memory usage** | `INFO memory` → `used_memory_rss` | > 80% `maxmemory` |
| **Memory fragmentation ratio** | `mem_fragmentation_ratio` | > 1.5 → cần `MEMORY PURGE` |
| **Hit rate** | `keyspace_hits / (keyspace_hits + keyspace_misses)` | < 85% → Cache strategy cần review |
| **LangCache hit rate** | Custom metric từ `FT.SEARCH` latency log | < 70% → Threshold quá cao hoặc quá thấp |
| **Eviction rate** | `evicted_keys` per second | > 0 nếu dùng `noeviction` → Alert ngay |
| **Connected clients** | `connected_clients` | Gần `maxclients` (mặc định 10000) |
| **Replication lag** | `INFO replication` → `master_repl_offset - slave_repl_offset` | > 1MB → Replica bị tụt hậu |
| **Stream pending messages** | `XPENDING agent:tasks - + 10` | > N messages pending lâu → Worker bị treo |

## Stack Monitoring đề xuất

> - **Redis Exporter + Prometheus + Grafana**: Export toàn bộ metrics Redis sang Grafana dashboard.
> - **Redis Insight Profiler**: Real-time command profiler để phát hiện bottleneck query.
> - **Custom Alert**: Gửi cảnh báo qua Slack/PagerDuty khi hit rate < 80% hoặc eviction rate > 0.
> - **Distributed Tracing**: Tích hợp OpenTelemetry để trace từng bước trong Agent Loop (từ request → queue → tool call → response).

*← Quay lại: [2-high-availability-sentinel-cluster.md](./2-high-availability-sentinel-cluster.md)*
