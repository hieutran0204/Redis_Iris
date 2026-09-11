# 2. Hệ sinh thái Redis — Có bao nhiêu "loại Redis" và chúng khác nhau thế nào?

Khi bắt đầu tìm hiểu Redis, rất dễ bị bối rối vì bạn sẽ thấy vô số cái tên: *Redis OSS, Redis Stack, Redis Cloud, Redis Sentinel, Redis Cluster, Redis Iris, Redis Flex...* Chúng có quan hệ gì với nhau?

Bài này sẽ giúp bạn nhìn thấy toàn bộ bức tranh hệ sinh thái Redis trong 5 phút và biết mình đang học phần nào.

---

## Tư duy phân loại: 2 trục chính

Để không nhầm lẫn, hãy hiểu rằng "loại Redis" được nói đến theo **2 trục hoàn toàn khác nhau**:

| Trục | Phân loại theo | Ví dụ |
| :--- | :--- | :--- |
| **Trục 1: Phiên bản / Tính năng phần mềm** | Redis cung cấp những tính năng gì? | Redis OSS, Redis Stack, Redis Cloud |
| **Trục 2: Mô hình triển khai kiến trúc** | Redis được dựng lên như thế nào trong hệ thống? | Standalone, Master-Replica, Sentinel, Cluster |

Repo này tập trung vào **Trục 1** để hiểu bản chất tính năng, và đề cập **Trục 2** ở góc độ vận hành thực tế.

---

## Trục 1 — Phiên bản / Tính năng: Redis có mấy "dạng"?

### 1.1. Redis OSS (Open-Source Software) — Redis "thuần" / Redis Core

**Đây là thứ chúng ta sẽ học toàn bộ trong repo này.**

Redis OSS là phiên bản mã nguồn mở gốc, viết bằng C, được cộng đồng phát triển và có thể cài đặt miễn phí trên bất kỳ máy chủ nào. Đây là trái tim của toàn bộ hệ sinh thái Redis.

Redis OSS bao gồm các tính năng:
* **9 kiểu cấu trúc dữ liệu cốt lõi**: String, Hash, List, Set, Sorted Set, Bitmap, HyperLogLog, Geospatial, Streams.
* **Cơ chế bảo toàn dữ liệu**: RDB Snapshot & AOF Log.
* **Cơ chế truyền tin & Hàng đợi**: Pub/Sub, Redis Streams với Consumer Groups.
* **Giao dịch nguyên tử**: MULTI/EXEC, Lua Scripting, WATCH (Optimistic Locking).
* **Lệnh nâng cao**: Expire/TTL, Scan, Pipeline, Transactions.

> [!NOTE]
> Redis OSS thay đổi giấy phép từ phiên bản 7.4 trở đi (chuyển sang RSALv2 và SSPLv1). Phiên bản ≤ 7.2 vẫn là BSD License thuần mã nguồn mở. Cộng đồng đã fork ra **Valkey** (Linux Foundation) và **Redict** để tiếp tục duy trì phiên bản 100% OSS.

---

### 1.2. Redis Stack — OSS + Các Module Mở Rộng

Redis Stack = Redis OSS + một bộ module mở rộng được đóng gói sẵn, giải quyết các bài toán phức tạp hơn mà Redis thuần không có:

| Module | Tính năng bổ sung |
| :--- | :--- |
| **RedisJSON** | Lưu trữ và truy vấn JSON natively (không cần serialize thành string) |
| **RedisSearch** | Full-text Search và Vector Search (tìm kiếm ngữ nghĩa / Semantic Search) |
| **RedisBloom** | Bloom Filter, Cuckoo Filter — xác suất kiểm tra phần tử tồn tại với bộ nhớ cực nhỏ |
| **RedisTimeSeries** | Chuỗi dữ liệu thời gian (Time-Series) cho IoT, metrics hệ thống, monitoring |
| **RedisGraph** *(deprecated)* | Lưu trữ và truy vấn đồ thị (Graph Database) theo mô hình Property Graph |

**Khi nào dùng Redis Stack?** Khi bạn cần tìm kiếm văn bản, tìm kiếm ngữ nghĩa theo vector (cho AI/ML), lưu JSON trực tiếp, hoặc lưu dữ liệu cảm biến theo thời gian — mà không muốn cài thêm Elasticsearch hay InfluxDB riêng.

---

### 1.3. Redis Cloud — Dịch vụ Redis được quản lý hoàn toàn (Fully Managed)

Redis Cloud là nền tảng **DBaaS (Database as a Service)** do công ty Redis Ltd. cung cấp. Thay vì tự dựng server, cài đặt, cấu hình Sentinel/Cluster, vá lỗi bảo mật... bạn chỉ cần đăng ký tài khoản, bấm tạo database, dùng ngay.

* **Có sẵn trên các cloud lớn**: AWS, GCP, Azure.
* **Tự động xử lý**: Backup định kỳ, Failover, Scaling, Monitoring.
* **Tích hợp AI Platform**: Đây là nơi ra đời của **Redis Iris**, **Redis Flex**, **Redis LangCache**...

---

### 1.4. Redis AI Stack / Redis Iris Platform — Thế hệ mới cho AI Agents (2026)

Đây là bộ sản phẩm mới nhất của Redis, ra mắt năm 2026, được thiết kế chuyên biệt cho kỷ nguyên **AI Agents** và **LLM (Large Language Models)**. Không phải là thay thế Redis Core, mà là **tầng chuyên biệt bổ sung bên trên Redis Core/Stack**.

```
┌─────────────────────────────────────────────────────────┐
│               Redis AI Platform (Redis Iris)             │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Redis        │  │ Redis Context│  │ Redis Agent   │  │
│  │ LangCache   │  │ Retriever    │  │ Memory        │  │
│  │             │  │              │  │               │  │
│  │ Cache kết   │  │ Truy vấn dữ  │  │ Bộ nhớ dài   │  │
│  │ quả LLM,    │  │ liệu nghiệp  │  │ hạn cho AI   │  │
│  │ tiết kiệm   │  │ vụ cho AI    │  │ Agent qua    │  │
│  │ token API   │  │ Agent        │  │ nhiều session │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  ┌─────────────────────────┐  ┌───────────────────────┐ │
│  │ Redis Data Integration  │  │ Redis Flex            │ │
│  │                         │  │                       │ │
│  │ CDC: đồng bộ data từ    │  │ Lưu trữ RAM + SSD     │ │
│  │ PostgreSQL/MySQL vào    │  │ hybrid — nhiều data   │ │
│  │ Redis gần như realtime  │  │ hơn, chi phí thấp hơn │ │
│  └─────────────────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
         Redis Core / Redis Stack (nền tảng bên dưới)
```

Giải thích từng sản phẩm:

**① Redis Iris** — *"Bộ não ngữ cảnh" cho AI Agent Fleet*
* Là tên gọi chung cho toàn bộ AI Platform, đóng vai trò như một **"Context Engine"** — tầng trung gian cung cấp ngữ cảnh cho các AI Agent tự động.
* Giải quyết bài toán: AI Agent cần biết *"Đơn hàng của khách hàng X hiện đang ở đâu?"* hay *"Khách hàng Y đã từng phàn nàn về vấn đề gì?"* — mà không cần kỹ sư viết tích hợp riêng cho từng nguồn dữ liệu.

**② Redis LangCache** — *Caching thông minh cho LLM*
* Khi người dùng hỏi AI chatbot một câu tương tự câu đã hỏi trước (ví dụ: *"Giờ mở cửa của cửa hàng?"* và *"Shop mở cửa lúc mấy giờ?"*), thay vì gửi cả hai câu lên OpenAI/Gemini tốn tiền, **LangCache** sẽ nhận ra chúng có nghĩa tương đương và trả về kết quả từ cache ngay lập tức.
* **Lợi ích thực tế**: Giảm đến 90% chi phí token API, giảm độ trễ từ vài giây xuống còn vài mili-giây.

**③ Redis Context Retriever** — *"Mắt nhìn dữ liệu" cho AI Agent*
* Cho phép AI Agent truy vấn trực tiếp vào dữ liệu nghiệp vụ thực tế (bảng khách hàng, đơn hàng, sản phẩm trong PostgreSQL/MySQL) mà không cần kỹ sư viết API riêng.
* Tự động sinh ra các công cụ (tools) dựa trên mô hình dữ liệu hiện có.

**④ Redis Agent Memory** — *"Ký ức dài hạn" cho AI Agent*
* Giải quyết vấn đề cốt tử của AI Agent: **Mất ngữ cảnh khi kết thúc session**.
* Lưu trữ cả bộ nhớ ngắn hạn (working memory — những gì đang xảy ra trong task hiện tại) và bộ nhớ dài hạn (long-term memory — tìm kiếm ngữ nghĩa bằng vector qua nhiều session và kênh giao tiếp).

**⑤ Redis Data Integration (RDI)** — *Cầu nối dữ liệu realtime*
* Dùng cơ chế **CDC (Change Data Capture)** để tự động đồng bộ dữ liệu từ các database quan hệ (PostgreSQL, MySQL, Oracle) vào Redis gần như realtime (độ trễ ~vài giây).
* Đảm bảo AI Agent luôn hành động trên dữ liệu mới nhất, không phải dữ liệu cũ trong cache.

**⑥ Redis Flex** — *Lưu trữ thông minh RAM + SSD*
* Thay vì bắt buộc phải để 100% dữ liệu trên RAM (rất đắt tiền khi cần lưu hàng trăm GB bộ nhớ Agent), **Redis Flex** cho phép Redis tự động phân loại:
  * **Hot data** (truy cập thường xuyên) → Giữ trên RAM (truy cập nanosecond).
  * **Cold data** (ít truy cập) → Đẩy xuống SSD (vẫn nhanh hơn database thông thường).
* Kết quả: Giảm tới 80% chi phí hạ tầng mà vẫn duy trì hiệu năng sub-millisecond cho dữ liệu quan trọng.

---

## Trục 2 — Mô hình triển khai kiến trúc: 4 cách dựng Redis trong hệ thống

Bất kể bạn dùng Redis OSS, Redis Stack hay Redis Cloud, khi triển khai thực tế bạn đều phải chọn một trong 4 mô hình kiến trúc sau. Chúng giải quyết bài toán về **tính sẵn sàng cao (HA)** và **khả năng mở rộng (Scalability)**:

```
Tăng dần độ phức tạp & khả năng chịu tải
─────────────────────────────────────────────────────────►

[Standalone] ──► [Master-Replica] ──► [Sentinel] ──► [Cluster]
  Dev/Test         Read Scaling      High Availability   Sharding
  Đơn giản nhất    Tăng tải đọc     Auto Failover     Vô hạn mở rộng
```

| Mô hình | Số Node | Tự Phục Hồi | Scale Ghi | Scale Đọc | Dùng Khi Nào |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Standalone** | 1 | ❌ | ❌ | ❌ | Development, testing, pet project |
| **Master - Replica** | 1M + nR | ❌ (Thủ công) | ❌ | ✅ | Ứng dụng đọc nhiều hơn ghi, chấp nhận xử lý tay khi sập |
| **Sentinel** | 1M + nR + 3S | ✅ (Tự động) | ❌ | ✅ | Production cần HA, dữ liệu vừa RAM 1 máy |
| **Cluster** | 3M+ + Replica | ✅ (Tự động) | ✅ | ✅ | Production siêu lớn, dữ liệu vượt RAM 1 máy |

*(M = Master, R = Replica, S = Sentinel Node)*

> [!TIP]
> 99% ứng dụng vừa và nhỏ (startup, doanh nghiệp SME) dùng **Redis Sentinel** là đủ và chuẩn cho Production. Redis Cluster chỉ cần thiết khi bạn đang ở quy mô của Shopee, Grab, hay Netflix.

---

## Tóm tắt: Repo này học gì?

```
Hệ sinh thái Redis
│
├── ✅ [ĐANG HỌC] Redis Core / OSS                ← Chương 1 → 5
│     Cấu trúc dữ liệu, Persistence, Caching,
│     Pub/Sub, Streams, Transactions, Locks
│
├── ✅ [ĐANG HỌC] 4 Mô hình Triển khai (Conceptual)  ← Bài này
│     Standalone, Master-Replica, Sentinel, Cluster
│
├── 🔜 [SẮP TỚI] Redis Stack & Modules              ← Chương nâng cao
│     RedisJSON, RedisSearch (Vector Search),
│     RedisBloom, RedisTimeSeries
│
└── 🔜 [SẮP TỚI] Redis AI Platform (Redis Iris)     ← Chương AI
      LangCache, Agent Memory, Context Retriever,
      RDI, Redis Flex
```

---

*Tiếp tục sang bài tiếp theo: [3-how-to-start.md](./3-how-to-start.md) để cài đặt Redis bằng Docker và bắt tay thực hành những lệnh đầu tiên.*
