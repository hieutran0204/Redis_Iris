<!--
name: 3-how-to-start.md
description: Comprehensive guide to setting up Redis via Docker and connecting with Redis Insight GUI, with a focus on preparing for AI Agent and Vector workflows.
-->

# 3. Hướng dẫn Setup Redis với Docker & Kết nối Redis Insight trực quan

Để bắt đầu học và thực hành Redis một cách chuẩn chỉnh nhất — đặc biệt là chuẩn bị nền tảng hạ tầng phục vụ nghiên cứu **AI Agents, Vector Search và Redis Iris** — việc chạy Redis trên **Docker** là giải pháp tối ưu số 1 hiện nay.

Không cần cài đặt rườm rà trên máy host (Windows/Mac/Linux), không lo xung đột môi trường, bật/tắt trong 1 giây và sẵn sàng dữ liệu bền vững qua Docker Volumes.

---

## 1. Chọn phiên bản Redis nào để chạy Docker?

Như đã tìm hiểu ở [2-redis-types-overview.md](./2-redis-types-overview.md), chúng ta có 2 lựa chọn chính:

| Lựa chọn | Image Docker | Bao gồm những gì? | Khuyên dùng khi nào? |
| :--- | :--- | :--- | :--- |
| **Lựa chọn 1 (Khuyên Dùng)** | `redis/redis-stack:latest` | • Redis Core Engine<br>• **RediSearch (Vector Search cho AI)**<br>• **RedisJSON**<br>• RedisBloom & RedisTimeSeries<br>• **Redis Insight Web UI tích hợp sẵn** (port 8001) | **Dành cho học tập, làm việc với AI Agents, RAG, Semantic Caching**. |
| **Lựa chọn 2** | `redis:latest` + `redis/redis-insight:latest` | • Redis OSS thuần túy (chỉ có Core Engine)<br>• Tách riêng container Redis Insight | Khi muốn môi trường nhẹ tối đa, chỉ cần các cấu trúc dữ liệu cơ bản. |

> [!TIP]
> **Vì mục tiêu của bạn là đào sâu vào AI Agent & Redis Iris**, hãy sử dụng **Lựa chọn 1 (`redis/redis-stack`)** ngay từ đầu. Image này có sẵn **RediSearch** (hỗ trợ lưu trữ Vector Embedding, Cosine Similarity search) và **RedisJSON** — hai module cốt lõi để làm việc với LLMs.

---

## 2. Cách 1 (Khuyên dùng): Chạy Redis Stack bằng Docker Compose

Cách chuyên nghiệp nhất là dùng `docker-compose.yml`. Bạn chỉ cần quản lý mọi cấu hình trong một file text duy nhất.

### Bước 2.1: Tạo file `docker-compose.yml`

Tạo file `docker-compose.yml` tại thư mục dự án với nội dung sau:

```yaml
services:
  redis-stack:
    image: redis/redis-stack:latest
    container_name: redis-stack-ai
    restart: unless-stopped
    ports:
      - "6379:6379"     # Port giao tiếp Redis Server (cho Backend / Code kết nối)
      - "8001:8001"     # Port giao diện Web UI Redis Insight
    environment:
      - REDIS_ARGS=--requirepass secret123 --save 60 1 --loglevel notice
    volumes:
      - redis-data:/data

volumes:
  redis-data:
    name: redis-stack-ai-data
    driver: local
```

#### Giải thích các tham số quan trọng:
* `image: redis/redis-stack:latest`: Chứa toàn bộ Redis Core + Modules AI/Vector Search + Redis Insight.
* `ports`:
  * `6379`: Cổng mặc định của Redis database. Ứng dụng Backend (NodeJS/Python/Go) sẽ kết nối vào đây.
  * `8001`: Cổng giao diện trực quan Redis Insight.
* `REDIS_ARGS=--requirepass secret123`: Thiết lập mật khẩu xác thực bảo vệ Redis (ở đây ví dụ là `secret123`, bạn có thể đổi theo ý muốn hoặc bỏ đi nếu chỉ test dev cục bộ).
* `--save 60 1`: Cơ chế RDB tự động lưu dữ liệu xuống đĩa nếu có ít nhất 1 thay đổi trong 60 giây.
* `volumes: redis-data:/data`: Ánh xạ dữ liệu trong container vào Docker Volume máy host. Khi bạn tắt máy hoặc xoá container, dữ liệu của bạn không bị mất.

---

### Bước 2.2: Khởi chạy Container

Mở terminal tại thư mục chứa file `docker-compose.yml` và chạy:

```bash
# Khởi động Redis dưới chế độ chạy nền (detached mode)
docker compose up -d
```

Kiểm tra trạng thái container:
```bash
docker compose ps
```

Nếu thấy `State: Up` hoặc trạng thái `running`, Redis Server và Redis Insight đã sẵn sàng!

---

### (Tùy chọn) Chạy nhanh bằng 1 dòng lệnh `docker run`

Nếu không muốn tạo file docker-compose, bạn có thể chạy ngay lệnh này trên terminal:

```bash
docker run -d \
  --name redis-stack-ai \
  -p 6379:6379 \
  -p 8001:8001 \
  -e REDIS_ARGS="--requirepass secret123" \
  -v redis-stack-ai-data:/data \
  redis/redis-stack:latest
```

---

## 3. Cách 2: Setup Redis Core và Redis Insight độc lập (2 Containers)

Nếu bạn chỉ muốn thử nghiệm Redis Core gốc mà không kèm các module mở rộng, bạn có thể cấu hình 2 container tách biệt:

```yaml
services:
  redis-core:
    image: redis:7.4-alpine
    container_name: redis-core
    restart: unless-stopped
    command: redis-server --requirepass secret123 --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis-core-data:/data

  redis-insight:
    image: redis/redis-insight:latest
    container_name: redis-insight
    restart: unless-stopped
    ports:
      - "8001:5540" # Redis Insight standalone lắng nghe trên port 5540 trong container
    depends_on:
      - redis-core
    volumes:
      - redis-insight-data:/data

volumes:
  redis-core-data:
  redis-insight-data:
```

---

## 4. Kết nối và làm chủ giao diện trực quan Redis Insight

Redis Insight là GUI (giao diện đồ họa) chính thức cực mạnh do chính Redis phát triển, giúp bạn xem và tương tác trực quan với dữ liệu trên RAM.

### Bước 4.1: Mở giao diện trên trình duyệt

Mở trình duyệt bất kỳ và truy cập vào đường dẫn:
👉 **`http://localhost:8001`**

Nếu sử dụng image `redis/redis-stack:latest`, Redis Insight sẽ tự động nhận diện và kết nối sẵn đến Redis Server nội bộ (được hiển thị ngay trên Dashboard).

Nếu được yêu cầu nhập thông tin kết nối thủ công (Add Connection):
* **Host**: `localhost` (hoặc `host.docker.internal` nếu container tách biệt)
* **Port**: `6379`
* **Database Name**: `My Redis AI Local` (tùy đặt)
* **Username**: Để trống (hoặc `default`)
* **Password**: `secret123` (mật khẩu đã cấu hình ở bước trên)

![Redis Insight Dashboard](https://redis.io/wp-content/uploads/2022/10/redisinsight-browser.png)

---

### Bước 4.2: Các tính năng "đáng giá" nhất trên Redis Insight

1. **Browser (Key Inspector):**
   * Hiển thị danh sách toàn bộ các Key theo dạng cây thư mục (Tree View phân cách bởi dấu `:`) hoặc dạng bảng.
   * Xem trực tiếp giá trị của từng kiểu dữ liệu: String, Hash, List, Set, ZSet, JSON...
   * Xem thời gian sống còn lại (**TTL**) của từng key trong thời gian thực.
   * Chỉnh sửa, thêm mới hoặc xóa key trực tiếp trên UI mà không cần gõ lệnh.

2. **Workbench (Interactive CLI):**
   * Cung cấp console gõ lệnh trực tiếp ngay trên trình duyệt với tính năng **Auto-complete**, gợi ý cú pháp và mô tả chi tiết của từng lệnh.
   * Hỗ trợ chạy các lệnh phức tạp, JSON Path query và Vector Index query.

3. **Memory Analysis & Profiler:**
   * Thống kê trực quan dung lượng RAM đang sử dụng, số lượng keys theo từng data type.
   * Nhận diện các key "khủng" đang chiếm nhiều bộ nhớ nhất để tối ưu dung lượng RAM.
   * **Real-time Profiler**: Giám sát mọi lệnh đang được client/backend gọi vào Redis theo thời gian thực (rất hữu ích khi debug request).

---

## 5. Thao tác những câu lệnh đầu tiên qua CLI

Bạn có 2 cách để gõ lệnh trực tiếp vào Redis:

### Cách 1: Qua Terminal máy tính (bằng Docker Exec)
```bash
# Truy cập vào redis-cli bên trong container
docker exec -it redis-stack-ai redis-cli

# Nếu có đặt password, nhập lệnh xác thực:
127.0.0.1:6379> AUTH secret123
OK
```

### Cách 2: Qua tab Workbench trên Redis Insight
Bấm vào biểu tượng **Workbench** (hoặc thanh CLI ở góc dưới màn hình) trên `http://localhost:8001`.

---

### Các câu lệnh "chào sân" căn bản:

#### 1. Kiểm tra kết nối
```redis
PING
# Kết quả trả về: PONG
```

#### 2. Thao tác với String & TTL (Time To Live)
```redis
# Lưu key tên người dùng
SET user:1001:name "Nguyen Van A"

# Lấy giá trị ra
GET user:1001:name
# "Nguyen Van A"

# Lưu OTP đăng nhập và tự động hủy sau 60 giây (EX 60)
SET otp:user:1001 "849201" EX 60

# Kiểm tra xem key OTP còn sống bao nhiêu giây nữa
TTL otp:user:1001
# Trả về: ví dụ 54 (giây)
```

#### 3. Thử nghiệm tính năng RedisJSON (Chuẩn bị cho AI Agent)
*Vì dùng `redis-stack`, bạn có thể lưu object JSON phân cấp nguyên bản mà không cần chuỗi hóa (serialize) thành String:*

```redis
# Lưu trạng thái của một Agent hội thoại
JSON.SET agent:session:01 $ '{"agent_id": "support_bot", "model": "gemini-flash", "memory": {"turns": 2, "topic": "redis_course"}}'

# Truy vấn trực tiếp 1 trường con bên trong JSON
JSON.GET agent:session:01 $.memory.topic
# Kết quả: "[\"redis_course\"]"
```

#### 4. Xem thông tin trạng thái server
```redis
INFO server
INFO memory
```

Mở lại tab **Browser** trên Redis Insight, bạn sẽ thấy ngay các key `user:1001:name`, `otp:user:1001`, và `agent:session:01` xuất hiện trực quan, có thể click vào xem và chỉnh sửa dễ dàng!

---

## 6. Các lệnh Docker hữu ích hàng ngày khi làm việc với Redis

| Mục đích | Câu lệnh |
| :--- | :--- |
| **Bật Redis** | `docker compose up -d` |
| **Dừng Redis (giữ lại dữ liệu)** | `docker compose stop` |
| **Khởi động lại** | `docker compose restart` |
| **Xem log thời gian thực** | `docker compose logs -f` |
| **Truy cập trực tiếp redis-cli** | `docker exec -it redis-stack-ai redis-cli -a secret123` |
| **Xóa sạch container và dữ liệu (Reset)** | `docker compose down -v` |

---

## 7. Tổng kết Chương 0 & Bước tiếp theo

Chúc mừng bạn đã hoàn thành **Chương 0 — Getting Started**!
* Đã nắm vững kiến trúc nền tảng và vị trí làm việc của Redis.
* Đã phân biệt toàn bộ hệ sinh thái (từ Redis OSS, Redis Stack đến Redis Iris AI Platform).
* Đã dựng xong hạ tầng chuẩn với **Docker + Redis Stack + Redis Insight**, sẵn sàng cho cả nghiệp vụ Caching truyền thống lẫn **AI Agent & Vector Search**.

### Lộ trình đặc biệt dành riêng cho định hướng AI Agent:
Theo yêu cầu nghiên cứu chuyên sâu về **AI Agent**:
1. Chúng ta sẽ lướt nhanh qua các cấu trúc dữ liệu nền tảng cốt lõi của Redis mà Agent thường dùng (`Hash` cho Context, `List/Stream` cho Task Queue/Event Loop, `ZSet` cho Sliding Window).
2. Sau đó, chúng ta sẽ **tập trung toàn lực đào sâu vào AI Platform & Redis Iris**:
   * **Semantic Caching với Redis LangCache**: Tiết kiệm chi phí token LLM.
   * **Agent Memory Store**: Quản lý short-term memory (working buffer) & long-term memory (vector embeddings).
   * **Redis Vector Search**: Tạo Index vector HNSW/FLAT, tìm kiếm tương đồng ngữ nghĩa phục vụ RAG cho Agent.
   * **Context Retriever & Tool Generation**: Tích hợp Agent với dữ liệu nghiệp vụ thời gian thực.
