<!--
name: 4-redis-flex-tiering-ram-ssd.md
description: In-depth guide to Redis Flex, Auto-Tiering across RAM and NVMe SSD, managing hundred-million-scale vector datasets, and reducing infrastructure costs by up to 80% without sacrificing microsecond query performance.
-->

# 3.4 — Redis Flex — Auto-Tiering RAM & NVMe SSD cho Quy mô Lớn

> 🚧 **Sắp ra mắt** — Bài này sẽ đi sâu vào:
> - **Bài toán Chi phí**: Agent Fleet tích lũy hàng chục triệu vector memories theo thời gian $\to$ hàng trăm GB dữ liệu $\to$ chi phí RAM vật lý tăng vọt không kiểm soát.
> - **Nguyên lý Hoạt động của Redis Flex**: Tự động phân loại dữ liệu "nóng" (Hot Data trên RAM với độ trễ nanosecond) và dữ liệu "lạnh" (Cold Data trên NVMe SSD với độ trễ microsecond) dựa trên tần suất truy cập.
> - **Quy luật 80/20 trong Vector Retrieval**: Tại sao đa phần các truy vấn của Agent chỉ tập trung vào $20\%$ dữ liệu gần nhất, và cách Redis Flex tận dụng đặc điểm này để cắt giảm $80\%$ chi phí phần cứng.
> - **Cấu hình & Triển khai**: Kích hoạt Auto-Tiering qua Redis Enterprise / Redis Cloud console.
> - **Benchmark Thực nghiệm**: So sánh Throughput & Latency giữa Pure RAM vs Redis Flex Tiered Storage.

---

*← Bài trước: [3.3 - Context Retriever](./3-context-retriever.md) | Tiếp theo: [3.5 - Redis Data Integration (RDI)](./5-redis-data-integration-rdi.md) →*
