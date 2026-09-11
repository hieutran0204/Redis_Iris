<!--
name: 2-vector-similarity-and-hybrid-search.md
description: In-depth guide to Vector Similarity Metrics (Cosine, IP, L2), FT.SEARCH KNN queries, Vector Range Search, Multi-tenant Hybrid Search, Pre-filtering mechanics, and integration with Redis Iris Context Platform.
-->

# 2.2 — Vector Similarity & Hybrid Search — Tìm kiếm Ngữ nghĩa cho RAG & AI Agent Memory

Trong bài trước, chúng ta đã nắm vững cách số hóa văn bản thành Vector và lập chỉ mục bằng giải thuật đồ thị **HNSW** trên Redis. 

Tuy nhiên, trong các hệ thống AI Agent thực chiến cấp doanh nghiệp, một bài toán sống còn xuất hiện:
> *"Làm thế nào để tìm kiếm chính xác các mảnh ký ức ngữ nghĩa liên quan nhất, nhưng **tuyệt đối không được rò rỉ dữ liệu** giữa các User khác nhau, **không lấy nhầm văn bản đã hết hạn**, và **không tốn kém tài nguyên** quét toàn bộ cơ sở dữ liệu?"*

Nếu chỉ dùng **Pure Vector Search (Tìm kiếm vector thuần túy)**, hệ thống của bạn sẽ nhanh chóng gặp thảm họa vi phạm bảo mật đa người dùng (Multi-tenant data leakage) và hiện tượng "ảo giác dữ liệu cũ".

Chương này sẽ trang bị cho bạn kiến thức chuyên sâu về **3 hàm đo khoảng cách vector**, cú pháp truy vấn **`FT.SEARCH` KNN / Vector Range**, cơ chế **Hybrid Search (Pre-filtering)**, và cách nền tảng **Redis Iris AI Platform** khai thác tầng tìm kiếm này để quản lý ngữ cảnh cho Agent.

---

## 1. Ba hàm đo khoảng cách Vector (Distance Metrics) — Chọn sao cho chuẩn?

Khi khai báo trường `VECTOR` trong RediSearch, tham số `DISTANCE_METRIC` quyết định thuật toán mà Redis dùng để tính mức độ "gần nhau" giữa vector truy vấn ($\vec{q}$) và vector tài liệu ($\vec{d}$).

```
FT.CREATE idx:kb ON JSON SCHEMA $.embedding AS embedding VECTOR HNSW 6 ... DISTANCE_METRIC <COSINE | IP | L2>
```

```mermaid
graph LR
    subgraph DistanceMetrics["Các hàm đo khoảng cách Vector trong RediSearch"]
        COS["COSINE<br/>(Đo góc giữa 2 vector)"]
        IP["IP (Inner Product)<br/>(Tích vô hướng / Dot Product)"]
        L2["L2 (Euclidean Distance)<br/>(Khoảng cách hình học thẳng)"]
    end
    COS --> TextNLP["Phù hợp nhất: Văn bản (Text NLP)<br/>Khi độ dài văn bản không quan trọng"]
    IP --> UnitVec["Phù hợp nhất: Vector đã Chuẩn hóa L2<br/>Tốc độ nhanh nhất (Tiết kiệm CPU)"]
    L2 --> ImageGeo["Phù hợp nhất: Hình ảnh / Âm thanh<br/>Độ lớn vector mang ý nghĩa vật lý"]
```

---

### 1.1. `COSINE` (Cosine Distance)

* **Bản chất hình học**: Đo **góc** giữa hai vector trong không gian đa chiều, hoàn toàn bỏ qua độ dài (độ lớn - magnitude) của chúng.
* **Công thức toán học**:
  $$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2} = \frac{\sum_{i=1}^{D} u_i v_i}{\sqrt{\sum_{i=1}^{D} u_i^2} \sqrt{\sum_{i=1}^{D} v_i^2}}$$
* **Khoảng cách trong Redis (Cosine Distance)**:
  $$D_{\text{Cosine}}(\vec{u}, \vec{v}) = 1 - \text{Cosine Similarity}(\vec{u}, \vec{v})$$
* **Miền giá trị**: Từ $0.0$ đến $2.0$:
  * $D = 0.0$: Hai vector cùng hướng hoàn toàn (đồng nghĩa $100\%$).
  * $D = 1.0$: Hai vector vuông góc ($90^\circ$, không có mối liên hệ ngữ nghĩa).
  * $D = 2.0$: Hai vector ngược hướng hoàn toàn ($180^\circ$).
* **Use-case**: Chuẩn mực cho tìm kiếm tài liệu văn bản khi vector chưa được chuẩn hóa độ dài.

---

### 1.2. `IP` (Inner Product / Dot Product)

* **Bản chất toán học**: Tích vô hướng giữa hai vector:
  $$\langle \vec{u}, \vec{v} \rangle = \sum_{i=1}^{D} u_i v_i$$
* **Khoảng cách trong Redis (IP Distance)**:
  $$D_{\text{IP}}(\vec{u}, \vec{v}) = 1 - \langle \vec{u}, \vec{v} \rangle$$
* **Điểm cốt lõi cực kỳ quan trọng**:
  * Nếu vector đầu vào đã được **chuẩn hóa độ dài đơn vị (Unit Normalized: $\|\vec{u}\|_2 = 1$)**, thì:
    $$\|\vec{u}\|_2 \|\vec{v}\|_2 = 1 \times 1 = 1 \implies \text{Cosine Distance} \equiv \text{IP Distance}$$
  * **Tại sao nên dùng `IP` thay vì `COSINE`?** 
    * Thuật toán `COSINE` phải thực hiện phép chia căn bậc hai ở mẫu số cho mỗi lần so sánh cạnh đồ thị HNSW.
    * `IP` chỉ thực hiện các phép nhân cộng (FMA - Fused Multiply-Add), tận dụng tối đa tập lệnh SIMD (AVX-512 / ARM NEON) của CPU.
    * **Kết quả**: `IP` cho thông lượng truy vấn (Throughput) **nhanh hơn 20% – 40%** so với `COSINE` trên cùng một tập dữ liệu!

> [!TIP]
> Các mô hình Embedding hiện đại như OpenAI `text-embedding-3-small` / `large`, Cohere Embed v3, hay BGE-M3 mặc định **đều đã xuất xưởng dưới dạng vector chuẩn hóa $L_2 = 1$**. Hãy ưu tiên chọn `DISTANCE_METRIC IP` để đạt hiệu năng tối đa trên Redis!

---

### 1.3. `L2` (Euclidean Distance bình phương)

* **Bản chất hình học**: Khoảng cách đường thẳng vật lý (đoạn nối trực tiếp) giữa 2 điểm trong không gian:
  $$D_{\text{L2}}(\vec{u}, \vec{v}) = \|\vec{u} - \vec{v}\|_2^2 = \sum_{i=1}^{D} (u_i - v_i)^2$$
* **Miền giá trị**: $[0, +\infty)$. Hai vector càng gần nhau thì $D_{\text{L2}}$ càng tiến về $0$.
* **Use-case**: Nhận diện khuôn mặt (Face recognition), phân cụm hình ảnh (Computer Vision features như ResNet/VGG), phân tích chuỗi thời gian (Audio/Sensor embeddings), nơi mà khoảng cách hình học tuyệt đối mang ý nghĩa khác biệt.

---

### 1.4. Bảng tổng kết so sánh 3 Metrics

| Tiêu chí | `COSINE` | `IP` (Inner Product) | `L2` (Euclidean) |
| :--- | :--- | :--- | :--- |
| **Công thức Redis Distance** | $1 - \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$ | $1 - (\vec{u} \cdot \vec{v})$ | $\sum (u_i - v_i)^2$ |
| **Miền giá trị khoảng cách** | $[0.0, 2.0]$ | $(-\infty, +\infty)$ (hoặc $[0, 2]$ nếu normalized) | $[0.0, +\infty)$ |
| **Giá trị 0 mang ý nghĩa gì?** | Trùng hướng hoàn toàn | Tích vô hướng bằng 1 | Trùng tọa độ hoàn toàn |
| **Độ phức tạp tính toán** | Trung bình (Cần tính căn mẫu số) | **Siêu nhanh (Chỉ nhân & cộng vector)** | Nhanh |
| **Yêu cầu Vector chuẩn hóa?** | Không bắt buộc | **Bắt buộc chuẩn hóa $L_2 = 1$** | Không |
| **Ứng dụng khuyến nghị** | Text RAG tổng quát | **RAG Production tối ưu latency** | Vision, Audio, Clustering |

---

## 2. Kỹ thuật truy vấn `FT.SEARCH` với Vector KNN

### 2.1. Giải phẫu cú pháp truy vấn KNN (K-Nearest Neighbors)

Truy vấn tìm kiếm $K$ vector gần nhất trên RediSearch có cấu trúc chuẩn như sau:

```sql
FT.SEARCH <index_name> 
  "(*)=>[KNN <k> @<vector_field> $BLOB AS <score_field>]" 
  PARAMS 2 BLOB <binary_bytes> 
  SORTBY <score_field> ASC 
  DIALECT 2
```

Hãy mổ xẻ từng thành phần:

1. `(*)`: **Filter Query**. Dấu `*` đại diện cho wildcard (lấy toàn bộ không gian tài liệu). Chúng ta sẽ thay thế phần này bằng các biểu thức lọc nghiệp vụ trong phần Hybrid Search.
2. `=>[KNN <k> @vector_field $BLOB AS score_field]`: Toán tử KNN Vector.
   * `<k>`: Số lượng láng giềng gần nhất muốn lấy về (ví dụ `5`, `10`).
   * `@vector_field`: Tên trường vector được khai báo trong Schema (ví dụ `@embedding`).
   * `$BLOB`: Tên biến tham số chứa vector truy vấn.
   * `AS score_field`: Đổi tên điểm khoảng cách trả về (thường đặt là `AS score` hoặc `AS vector_distance`).
3. `PARAMS 2 BLOB <binary_bytes>`:
   * RediSearch sử dụng cơ chế Parameterized Query để nạp dữ liệu nhị phân.
   * `2`: Số lượng phần tử trong cặp `[tên_biến, giá_trị]`.
   * `<binary_bytes>`: **Bắt buộc** là mảng byte nhị phân của số thực float (dù index lưu trên JSON hay HASH, khi truyền vector query vào hàm tìm kiếm của RediSearch thì tham số này vẫn phải đóng gói dưới dạng `np.array(vec, dtype=np.float32).tobytes()`).
4. `SORTBY <score_field> ASC`:
   * Vì RediSearch trả về **Khoảng cách (Distance)** chứ không phải độ tương đồng. Điểm càng nhỏ nghĩa là 2 vector càng gần nhau $\to$ **Luôn sắp xếp tăng dần (`ASC`)**.
5. `DIALECT 2` (hoặc `DIALECT 4`):
   * Bắt buộc phải bật `DIALECT 2` trở lên để kích hoạt cú pháp Vector Search hiện đại và bộ phân tích cú pháp chuẩn.

---

### 2.2. Vector Range Query: Tìm kiếm theo Bán kính Ngưỡng

Một nhược điểm lớn của truy vấn KNN thuần túy ($K=5$):
* Nếu user đặt một câu hỏi hoàn toàn vô nghĩa (ví dụ: *"asdjaksjd123"*), mô hình Embedding vẫn sinh ra một vector.
* Thuật toán KNN **vẫn bị ép buộc phải trả về đủ 5 tài liệu**, dù khoảng cách của chúng rất xa ($D > 0.8$ — hoàn toàn không liên quan)!
* Hậu quả: LLM nhận phải thông tin rác và sinh ra ảo giác (Hallucination).

**Giải pháp**: Sử dụng **Vector Range Query** (Chỉ lấy tài liệu nếu khoảng cách nằm trong bán kính $R$ cho phép):

```sql
FT.SEARCH idx:kb 
  "@embedding:[VECTOR_RANGE $radius $BLOB] => {$yield_distance_as: score}" 
  PARAMS 4 radius 0.25 BLOB <binary_bytes> 
  SORTBY score ASC 
  DIALECT 2
```

* `$radius 0.25`: Chỉ giữ lại các tài liệu có $D_{\text{Cosine}} \le 0.25$ (tương đương Cosine Similarity $\ge 75\%$). Nếu không có tài liệu nào đạt chuẩn, Redis sẽ trả về $0$ kết quả!

---

## 3. Hybrid Search: Trái tim của Hệ thống AI Agent Thực chiến

### 3.1. Thảm họa khi thiếu Metadata Filtering

Hãy tưởng tượng một hệ thống SaaS Agent phục vụ 10,000 công ty cùng lưu ký ức vào một Redis Cluster duy nhất:
* Nếu chỉ tìm kiếm bằng Vector, khi nhân viên Công ty A hỏi: *"Doanh thu quý 3 là bao nhiêu?"*, vector này có thể có khoảng cách cực kỳ gần với tài liệu báo cáo của Công ty B!
* Kết quả: **Rò rỉ dữ liệu xuyên người dùng (Cross-tenant Data Breach)** — lỗi bảo mật mức độ nghiêm trọng nhất (P0).

```mermaid
graph TD
    UserQuery["Query của User A: 'Chính sách thưởng 2026'"] --> Embed["Tạo Query Vector"]
    
    subgraph PureVector["❌ Pure Vector Search (Không Filter)"]
        Embed --> VSearch["KNN Search trên toàn bộ Redis RAM"]
        VSearch --> Leak["Lấy nhầm tài liệu của User B (Do góc vector gần)"]
        VSearch --> Expired["Lấy nhầm chính sách cũ hết hạn từ năm 2021"]
    end
    
    subgraph Hybrid["✅ Hybrid Search (Vector + Metadata Pre-filtering)"]
        Embed --> Filter["Áp bộ lọc: tenant_id == 'A' AND status == 'active'"]
        Filter --> MaskedSearch["Chỉ duyệt KNN trong phạm vi tài liệu hợp lệ của User A"]
        MaskedSearch --> SecureDocs["Kết quả chính xác, bảo mật tuyệt đối"]
    end
```

---

### 3.2. Cú pháp kết hợp Multi-Field Filters trong RediSearch

Trong `FT.SEARCH`, phần nằm trước dấu `=>` chính là biểu thức lọc nghiệp vụ (Filter Expression). Bạn có thể kết hợp toán tử logic `AND` (khoảng trắng), `OR` (`|`), `NOT` (`-`), lọc khoảng số (`NUMERIC`), và lọc danh mục (`TAG`):

#### 1. Lọc theo Phân quyền và Người dùng (TAG Filter):
```sql
(@tenant_id:{tenant_99} @user_id:{user_007})=>[KNN 5 @embedding $BLOB AS score]
```

#### 2. Lọc theo Khoảng thời gian (NUMERIC Filter):
Chỉ lấy các ký ức được tạo trong 30 ngày gần nhất (Timestamp $\ge 1725100000$):
```sql
(@created_at:[1725100000 +inf])=>[KNN 5 @embedding $BLOB AS score]
```

#### 3. Lọc kết hợp Phức tạp (Full Hybrid Search):
Tìm kiếm các tài liệu thuộc danh mục `hr_policy` hoặc `security_rule`, có trạng thái `active`, tạo sau mốc thời gian chỉ định, và thuộc quyền truy cập của công ty `acme_corp`:

```sql
(
  @tenant_id:{acme_corp} 
  @category:{hr_policy | security_rule} 
  @status:{active} 
  @created_at:[1704067200 +inf]
)=>[KNN 5 @embedding $BLOB AS score]
```

---

## 4. Bản chất thuật toán: Pre-filtering vs Post-filtering

Có 2 trường phái kỹ thuật khi kết hợp Vector và Bộ lọc:

```mermaid
sequenceDiagram
    autonumber
    participant App as AI Agent App
    participant RediSearch as Redis Query Engine
    participant HNSW as HNSW Graph / Inverted Index

    Note over App, HNSW: Trường phái 1: Post-filtering (Kém hiệu quả)
    App->>HNSW: 1. Tìm Top 100 vector gần nhất trên toàn bộ dữ liệu
    HNSW-->>App: Trả về 100 docs
    App->>App: 2. Lọc bỏ các doc không thuộc tenant_id='A'
    Note over App: Nếu chỉ có 2 doc thuộc tenant A -> Recall sụp đổ!

    Note over App, HNSW: Trường phái 2: Pre-filtering (Cơ chế chuẩn của RediSearch)
    App->>RediSearch: Gửi Hybrid Query (@tenant_id:{A}) => [KNN 5 @embedding $BLOB]
    RediSearch->>HNSW: Tạo Bitmap Filter tập hợp doc thỏa mãn Tenant A
    HNSW->>HNSW: Duyệt đồ thị HNSW chỉ qua các node nằm trong Bitmap
    HNSW-->>App: Trả về chính xác Top 5 vector tốt nhất của riêng Tenant A!
```

### So sánh chi tiết hai cơ chế:

1. **Post-filtering (Hậu lọc - Nguy hiểm)**:
   * Chạy KNN tìm $K$ vector gần nhất trên toàn bộ database trước.
   * Sau đó mới duyệt qua kết quả và loại bỏ các bản ghi không thỏa mãn metadata filter.
   * **Lỗ hổng chết người**: Nếu người dùng chỉ sở hữu $1\%$ tổng dữ liệu hệ thống, khả năng cao toàn bộ Top 10 kết quả trả về đều thuộc về... người khác! Kết quả sau khi lọc là mảng rỗng ($\text{Recall} = 0$).

2. **Pre-filtering trong Redis (Tiền lọc thông minh)**:
   * RediSearch thực thi bộ lọc metadata **ngay trong lúc duyệt đồ thị Vector**:
     * **Batched Pre-filtering**: RediSearch lấy danh sách ID tài liệu thỏa mãn metadata (dưới dạng bitset/bitmap từ Inverted Index). Khi thuật toán HNSW duyệt qua các đỉnh láng giềng, đỉnh nào không nằm trong bitset sẽ bị bỏ qua ngay lập tức.
     * **Linear Scan Fallback**: Nếu bộ lọc metadata quá khắt khe (ví dụ sau khi lọc chỉ còn dưới $1,000$ documents thỏa mãn), Redis sẽ tự động chuyển sang chế độ quét tuyến tính chính xác (Exact FLAT Scan) trên $1,000$ phần tử đó thay vì duyệt HNSW. Cơ chế thông minh này loại bỏ hoàn toàn hiện tượng "đứt gãy đồ thị" (Graph disconnection) mà các vector database khác thường mắc phải!

---

## 5. Tương thích với Nền tảng Redis Iris AI Platform

Trong hệ sinh thái chuyên biệt cho AI Agent vừa được Redis công bố — **Redis Iris**, cơ chế Hybrid Search chính là "động cơ ngầm" kích hoạt các năng lực sau:

```mermaid
graph TD
    Iris["Redis Iris Platform"] --> LangCache["1. Redis LangCache<br/>(Semantic Cache)"]
    Iris --> AgentMem["2. Redis Agent Memory<br/>(Working & Long-term Memory)"]
    Iris --> CtxRetriever["3. Context Retriever<br/>(Real-time Business Context via MCP)"]

    LangCache --> LangCacheAction["Vector Range Query (R <= 0.1)<br/>Bắt trúng câu hỏi tương đồng ngữ nghĩa, trả kết quả cache ngay tức thì"]
    AgentMem --> AgentMemAction["Hybrid Search với Pre-filtering<br/>Cách ly bộ nhớ theo session_id & user_id, ngăn rò rỉ ký ức"]
    CtxRetriever --> CtxRetrieverAction["Tự động chuyển cấu trúc dữ liệu nghiệp vụ<br/>thành các Tool Model Context Protocol (MCP) có Hybrid Search"]
```

1. **Redis Agent Memory**:
   * Tự động quản lý 2 tầng bộ nhớ: **Working Memory** (lưu ngữ cảnh phiên chat hiện tại trên RedisJSON) và **Episodic Long-term Memory** (vector hóa các sự kiện quan trọng).
   * Khi Agent cần hồi tưởng quá khứ, Iris thực thi câu truy vấn Hybrid Search với bộ lọc cứng `@user_id` và `@session_id` để đảm bảo không bao giờ "nhớ nhầm ký ức của người khác".
2. **Redis LangCache (Semantic Caching)**:
   * Sử dụng **Vector Range Query** với khoảng cách Cosine cực nhỏ ($R \le 0.10$). Khi người dùng hỏi một câu có cùng ý nghĩa với câu hỏi 5 phút trước, hệ thống trả về câu trả lời đã lưu trong cache mà không cần tốn tiền gọi API OpenAI/Claude.
3. **Redis Context Retriever**:
   * Tự động đồng bộ dữ liệu từ PostgreSQL/MySQL sang Redis qua Change Data Capture (CDC), sau đó mở ra giao diện tìm kiếm kết hợp (Text + Vector) chuẩn giao thức **Model Context Protocol (MCP)** để các Agent có thể tự do tra cứu.

---

## 6. Thực hành Code mẫu Python: Hybrid Search & Multi-Tenant Memory

Dưới đây là kịch bản thực tế hoàn chỉnh: Xây dựng hệ thống lưu trữ và tìm kiếm ký ức cho AI Agent đa người dùng bằng thư viện `redis-py` (hỗ trợ RediSearch).

### 6.1. Cài đặt thư viện cần thiết

```bash
pip install redis numpy sentence-transformers
```

### 6.2. Source Code hoàn chỉnh

```python
"""
name: test_hybrid_search.py
description: Complete runnable example demonstrating RediSearch HNSW indexing, 
             pure vector search vs multi-tenant hybrid search, and vector range query.
"""

import json
import time
import numpy as np
import redis
from redis.commands.search.field import (
    TextField,
    TagField,
    NumericField,
    VectorField
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

# 1. Kết nối tới Redis Stack
client = redis.Redis(host="localhost", port=6379, decode_responses=False)

INDEX_NAME = "idx:agent_memory"
DOC_PREFIX = "mem:"
VECTOR_DIM = 4  # Dùng 4 chiều để demo trực quan (Trong production: 384 hoặc 1536)

def recreate_index():
    """Tạo mới Index hỗ trợ cả Metadata Fields và Vector Field."""
    try:
        client.ft(INDEX_NAME).dropindex(delete_documents=True)
        print(f"[*] Dropped existing index: {INDEX_NAME}")
    except Exception:
        pass

    schema = (
        TagField("$.user_id", as_name="user_id"),
        TagField("$.category", as_name="category"),
        NumericField("$.created_at", as_name="created_at"),
        TextField("$.content", as_name="content"),
        VectorField(
            "$.embedding",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIM,
                "DISTANCE_METRIC": "COSINE",
                "M": 16,
                "EF_CONSTRUCTION": 200,
            },
            as_name="embedding"
        )
    )

    definition = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.JSON)
    client.ft(INDEX_NAME).create_index(fields=schema, definition=definition)
    print(f"[+] Index '{INDEX_NAME}' created successfully with HNSW COSINE!")

def seed_sample_memories():
    """
    Nạp dữ liệu ký ức của 2 User khác nhau:
    - User A (user_alice): Lưu thông tin thẻ tín dụng & chính sách nghỉ phép.
    - User B (user_bob): Lưu ghi chú mật khẩu server & lịch công tác.
    """
    memories = [
        {
            "id": "1",
            "user_id": "user_alice",
            "category": "finance",
            "created_at": int(time.time()) - 1000,
            "content": "Thẻ tín dụng Visa doanh nghiệp kết thúc bằng số 8899, hạn mức 50 triệu.",
            # Vector giả lập ngữ nghĩa về 'thanh toán / thẻ tín dụng'
            "embedding": [0.85, 0.10, 0.05, 0.02]
        },
        {
            "id": "2",
            "user_id": "user_alice",
            "category": "hr",
            "created_at": int(time.time()) - 500,
            "content": "Alice đã đăng ký nghỉ phép từ ngày 15 đến 18 tháng sau.",
            "embedding": [0.05, 0.90, 0.12, 0.01]
        },
        {
            "id": "3",
            "user_id": "user_bob",
            "category": "devops",
            "created_at": int(time.time()) - 300,
            "content": "Mật khẩu root của cụm Redis Cluster Staging là 'SecretAdmin2026!'.",
            "embedding": [0.10, 0.15, 0.88, 0.05]
        },
        {
            "id": "4",
            "user_id": "user_bob",
            "category": "finance",
            "created_at": int(time.time()) - 100,
            "content": "Bob thanh toán hóa đơn thẻ tín dụng cá nhân 12 triệu tại ngân hàng.",
            # Vector của Bob cũng nói về 'thẻ tín dụng', có góc rất gần với doc 1 của Alice!
            "embedding": [0.82, 0.12, 0.08, 0.01]
        }
    ]

    for item in memories:
        key = f"{DOC_PREFIX}{item['id']}"
        client.json().set(key, "$", item)
    print(f"[+] Seeded {len(memories)} memory records into RedisJSON.")

def run_pure_vector_search(query_vector: list, top_k: int = 2):
    """
    Tìm kiếm Vector thuần túy (Không có bộ lọc).
    Minh họa nguy cơ lộ lọt dữ liệu giữa các User!
    """
    print("\n" + "="*60)
    print("DEMO 1: PURE VECTOR SEARCH (Nguy cơ lộ lọt dữ liệu)")
    print("="*60)

    # Đóng gói vector query thành dạng binary bytes
    query_bytes = np.array(query_vector, dtype=np.float32).tobytes()

    # Cú pháp KNN wildcard (*)
    query_str = f"(*)=>[KNN {top_k} @embedding $BLOB AS score]"
    q = (
        Query(query_str)
        .sort_by("score", asc=True)
        .return_fields("user_id", "category", "content", "score")
        .dialect(2)
    )

    results = client.ft(INDEX_NAME).search(q, query_params={"BLOB": query_bytes})
    print(f"Query: Tìm kiếm thông tin liên quan tới 'thẻ tín dụng'...")
    print(f"Tổng kết quả tìm thấy: {results.total}")
    for doc in results.docs:
        print(f"  -> [User: {doc.user_id}] | Category: {doc.category} | Distance: {float(doc.score):.4f}")
        print(f"     Nội dung: {doc.content}")

def run_hybrid_search(target_user_id: str, query_vector: list, top_k: int = 2):
    """
    Hybrid Search: Kết hợp Pre-filtering cô lập theo User ID.
    Ngăn chặn tuyệt đối việc User này đọc ký ức của User kia.
    """
    print("\n" + "="*60)
    print(f"DEMO 2: HYBRID SEARCH (Bảo mật - Chỉ tìm trong phạm vi '{target_user_id}')")
    print("="*60)

    query_bytes = np.array(query_vector, dtype=np.float32).tobytes()

    # Pre-filter: Bắt buộc trường user_id phải khớp chính xác
    query_str = f"(@user_id:{{{target_user_id}}})=>[KNN {top_k} @embedding $BLOB AS score]"
    q = (
        Query(query_str)
        .sort_by("score", asc=True)
        .return_fields("user_id", "category", "content", "score")
        .dialect(2)
    )

    results = client.ft(INDEX_NAME).search(q, query_params={"BLOB": query_bytes})
    print(f"Kết quả tìm kiếm cho riêng {target_user_id}:")
    for doc in results.docs:
        print(f"  -> [User: {doc.user_id}] | Category: {doc.category} | Distance: {float(doc.score):.4f}")
        print(f"     Nội dung: {doc.content}")

def run_vector_range_search(target_user_id: str, query_vector: list, max_distance: float = 0.20):
    """
    Vector Range Search: Chỉ lấy các ký ức đạt chất lượng tương đồng cao (Distance <= max_distance).
    Loại bỏ tài liệu không liên quan.
    """
    print("\n" + "="*60)
    print(f"DEMO 3: VECTOR RANGE SEARCH (Bán kính khoảng cách <= {max_distance})")
    print("="*60)

    query_bytes = np.array(query_vector, dtype=np.float32).tobytes()

    # Cú pháp Vector Range kết hợp bộ lọc TAG
    query_str = f"(@user_id:{{{target_user_id}}} @embedding:[VECTOR_RANGE $radius $BLOB] => {{$yield_distance_as: score}})"
    q = (
        Query(query_str)
        .sort_by("score", asc=True)
        .return_fields("user_id", "content", "score")
        .dialect(2)
    )

    params = {
        "radius": max_distance,
        "BLOB": query_bytes
    }

    results = client.ft(INDEX_NAME).search(q, query_params=params)
    print(f"Tìm thấy {results.total} ký ức thỏa mãn ngưỡng bán kính <= {max_distance}:")
    for doc in results.docs:
        print(f"  -> Content: {doc.content} | Distance: {float(doc.score):.4f}")

if __name__ == "__main__":
    recreate_index()
    seed_sample_memories()

    # Vector câu hỏi: "Thẻ ngân hàng và tài chính"
    test_query_vector = [0.84, 0.11, 0.06, 0.02]

    # 1. Pure vector search: Lấy nhầm dữ liệu của cả Alice và Bob
    run_pure_vector_search(test_query_vector, top_k=2)

    # 2. Hybrid search: Khi Alice hỏi, chỉ trả về đúng tài liệu của Alice
    run_hybrid_search(target_user_id="user_alice", query_vector=test_query_vector, top_k=2)

    # 3. Range search: Lọc theo ngưỡng tin cậy
    run_vector_range_search(target_user_id="user_alice", query_vector=test_query_vector, max_distance=0.05)
```

---

## 7. Tiếp cận Hiện đại: Sử dụng Redis VL (`redisvl`)

Bên cạnh thư viện gốc `redis-py`, đội ngũ Redis AI đã phát triển thư viện cấp cao chuyên dụng mang tên **Redis Vector Library (`redisvl`)**. 

Thư viện này cung cấp cú pháp hướng đối tượng cực kỳ trong sáng cho Hybrid Search:

```python
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag, Num

# 1. Khởi tạo Index từ file cấu hình YAML hoặc dict
index = SearchIndex.from_yaml("memory_schema.yaml")
index.connect("redis://localhost:6379")

# 2. Tạo biểu thức lọc Hybrid chuẩn Pythonic
filter_expression = (Tag("user_id") == "user_alice") & (Num("created_at") >= 1704067200)

# 3. Tạo Vector Query tích hợp Filter
query = VectorQuery(
    vector=[0.024, -0.158, 0.891, 0.045],
    vector_field_name="embedding",
    num_results=5,
    return_fields=["content", "category"],
    filter_expression=filter_expression
)

# 4. Thực thi truy vấn
results = index.query(query)
for doc in results:
    print(f"Doc: {doc['content']} | Distance: {doc['vector_distance']}")
```

---

## 8. Production Checklist & Best Practices

1. **Luôn bật `DIALECT 2` hoặc `DIALECT 4`**: Nếu quên chỉ định dialect, câu lệnh `FT.SEARCH` sẽ báo lỗi cú pháp hoặc fallback về dialect 1 không hỗ trợ toán tử vector.
2. **Luôn gán nhãn `TAG` cho các trường định danh**: Các trường như `tenant_id`, `user_id`, `org_id`, `status` phải dùng kiểu `TagField` thay vì `TextField` để đảm bảo so khớp chính xác tuyệt đối (exact match), không bị ảnh hưởng bởi cơ chế tách từ (tokenization) hay stemmer của ngôn ngữ.
3. **Sắp xếp `SORTBY score ASC`**: Khoảng cách nhỏ hơn nghĩa là độ tương đồng cao hơn. Sắp xếp `DESC` sẽ trả về những tài liệu... ít liên quan nhất!
4. **Luôn nạp Query Vector dưới dạng `FLOAT32` binary buffer**: Kể cả khi dữ liệu trong Redis lưu dạng JSON, giá trị tham số `$BLOB` truyền vào `PARAMS` vẫn bắt buộc phải là bytes (`np.array(vec, dtype=np.float32).tobytes()`).
5. **Cân nhắc `IP` thay vì `COSINE` khi scale lớn**: Đảm bảo chuẩn hóa vector ở client trước khi nạp (`vec = vec / np.linalg.norm(vec)`), sau đó cấu hình `DISTANCE_METRIC IP` để đạt tốc độ truy vấn cao nhất và tiết kiệm chu kỳ CPU của Redis.

---

*← Bài trước: [2.1 - Embeddings & HNSW Indexing](./1-embeddings-and-hnsw-indexing.md) | Bài tiếp theo: [2.3 - RAG Pipeline & Reranking](./3-rag-pipeline-and-reranking.md) →*
