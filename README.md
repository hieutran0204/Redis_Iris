<!--
name: README.md
description: Master roadmap for Redis for AI Agents — from core primitives to production-grade multi-agent systems and Redis Iris platform.
-->

# Redis for AI Agents — From Primitives to Production

Kho tài liệu thực chiến chuyên sâu về **Redis**, định hướng hoàn toàn vào việc xây dựng và vận hành **AI Agent Systems** hiện đại — từ nền tảng dữ liệu, Vector Search, Redis Iris AI Platform, đến Multi-Agent Reliability và Production Ops.

---

## 🛠️ Khởi động nhanh

```bash
# Khởi động Redis Stack (Server + RediSearch + RedisJSON + Redis Insight Web UI)
docker compose up -d

# Mở Redis Insight tại: http://localhost:8001
# Password: secret123
```

---

## 📚 Lộ trình học tập

### ✅ [Chương 0: Getting Started](./0-getting-started/)
Tổng quan kiến trúc, phân loại hệ sinh thái & thiết lập môi trường chuẩn.

| # | Nội dung | Trạng thái |
|---|-----|-----------|
| 1 | [Overview Redis — Bản chất & 4 vị trí làm việc trong hệ thống](./0-getting-started/1-introduce.md) | ✅ Hoàn thành |
| 2 | [Hệ sinh thái Redis — OSS / Stack / Cloud / Redis Iris AI Platform](./0-getting-started/2-redis-types-overview.md) | ✅ Hoàn thành |
| 3 | [Setup Docker, Redis Stack & Redis Insight trực quan](./0-getting-started/3-how-to-start.md) | ✅ Hoàn thành |

---

### ✅ [Chương 1: Redis Foundations & Memory Management](./1-redis-foundations-and-memory/)
Cấu trúc dữ liệu tối ưu, kiến trúc bộ nhớ Agent, Event Loop và chiến lược vận hành thực tế.

| # | Nội dung | Trạng thái |
|---|-----|-----------|
| 1 | [Hướng dẫn chọn cấu trúc dữ liệu Redis cho AI Agent (Decision Guide)](./1-redis-foundations-and-memory/1-data-structure-decision-guide.md) | ✅ Hoàn thành |
| 2 | [RedisJSON — Lưu Agent State, Context Window & Tool Schema](./1-redis-foundations-and-memory/2-redis-json-state-store.md) | ✅ Hoàn thành |
| 3 | [Redis Streams — Agent Event Loop & Async Tool Queue](./1-redis-foundations-and-memory/3-streams-for-agent-loop.md) | ✅ Hoàn thành |
| 4 | [Quản lý bộ nhớ, Chiến lược TTL & Lưu trữ bền vững (Persistence)](./1-redis-foundations-and-memory/4-memory-eviction-and-ttl-strategy.md) | ✅ Hoàn thành |
| 5 | [Distributed Locks cho Tools & Connection Pooling trong Production](./1-redis-foundations-and-memory/5-distributed-locks-and-pooling.md) | ✅ Hoàn thành |

---

### ✅ [Chương 2: Vector Search & RAG](./2-vector-search-and-rag/)
Xây dựng Vector Database tốc độ cao và tối ưu hóa RAG Pipeline cho Agent.

| # | Nội dung | Trạng thái |
|---|-----|-----------|
| 0 | [Chunking & Preprocessing — Tiền xử lý dữ liệu cho Vector Search](./2-vector-search-and-rag/0-chunking-and-preprocessing.md) | ✅ Hoàn thành |
| 1 | [Embeddings & HNSW Indexing — Xây dựng Vector DB trên Redis](./2-vector-search-and-rag/1-embeddings-and-hnsw-indexing.md) | ✅ Hoàn thành |
| 2 | [Vector Similarity & Hybrid Search — Tìm kiếm ngữ nghĩa cho RAG](./2-vector-search-and-rag/2-vector-similarity-and-hybrid-search.md) | ✅ Hoàn thành |
| 3 | [RAG Pipeline & Reranking — Ráp nối Hệ thống RAG Thực chiến](./2-vector-search-and-rag/3-rag-pipeline-and-reranking.md) | ✅ Hoàn thành |
| 4 | [RAG Benchmarking & Evaluation — Đo lường Recall@K & chất lượng Retrieval](./2-vector-search-and-rag/4-rag-benchmarking-and-evaluation.md) | ✅ Hoàn thành |
| 5 | [Vector Migration Guide — Import Embeddings từ Pinecone / Qdrant / PGVector](./2-vector-search-and-rag/5-vector-migration-guide.md) | ✅ Hoàn thành |

---

### 🔜 [Chương 3: Redis Iris AI Platform](./3-redis-iris-platform/)
Khai thác sâu bộ công cụ Redis Iris — nền tảng chuyên biệt cho kỷ nguyên AI Agents.

| # | Nội dung | Trạng thái |
|---|-----|-----------|
| 0 | [Why Redis Iris? — Động cơ Ngữ cảnh & Bộ nhớ cho AI Agents](./3-redis-iris-platform/0-why-iris-context-engine.md) | ✅ Hoàn thành |
| 1 | [Redis LangCache — Semantic Caching giảm 90% chi phí token LLM](./3-redis-iris-platform/1-redis-langcache-semantic-cache.md) | 🚧 Sắp ra mắt |
| 2 | [Agent Memory Architecture — Phân tầng Working Memory & Long-term Vector Memory](./3-redis-iris-platform/2-agent-memory-architecture.md) | 🚧 Sắp ra mắt |
| 3 | [Context Retriever — Kết nối dữ liệu nghiệp vụ thời gian thực vào Agent qua MCP](./3-redis-iris-platform/3-context-retriever.md) | 🚧 Sắp ra mắt |
| 4 | [Redis Flex — Auto-Tiering RAM + SSD cho Quy mô Lớn](./3-redis-iris-platform/4-redis-flex-tiering-ram-ssd.md) | 🚧 Sắp ra mắt |
| 5 | [Redis Data Integration (RDI) — Real-time CDC từ PostgreSQL/MySQL](./3-redis-iris-platform/5-redis-data-integration-rdi.md) | ✅ Hoàn thành |

---

### 🔜 [Chương 4: Agent Loop & Multi-Agent Reliability](./4-agent-loop-and-multi-agent-reliability/)
Thiết kế vòng lặp Agent đáng tin cậy và điều phối hệ thống đa tác tử.

| # | Nội dung | Trạng thái |
|---|-----|-----------|
| 1 | [Redis Streams — Event-Driven Agent Loop & Consumer Groups](./4-agent-loop-and-multi-agent-reliability/1-streams-event-driven-loop.md) | 🚧 Sắp ra mắt |
| 2 | [Retry, Idempotency & DLQ — Đảm bảo độ tin cậy khi Tool call thất bại](./4-agent-loop-and-multi-agent-reliability/2-retry-idempotency-and-dlq.md) | 🚧 Sắp ra mắt |
| 3 | [Inter-Agent Pub/Sub Bus — Giao tiếp thời gian thực giữa các Agent](./4-agent-loop-and-multi-agent-reliability/3-inter-agent-pubsub-bus.md) | 🚧 Sắp ra mắt |
| 4 | [LangGraph & CrewAI — Redis làm Checkpointer & State Store](./4-agent-loop-and-multi-agent-reliability/4-orchestration-with-langgraph-crewai.md) | 🚧 Sắp ra mắt |

---

### 🔜 [Chương 5: Production Ops & Security](./5-production-ops-and-security/)
Vận hành hệ thống Agent chạy 24/7 với độ sẵn sàng cao và bảo mật toàn diện.

| # | Nội dung | Trạng thái |
|---|-----|-----------|
| 1 | [Persistence & Disaster Recovery — Bảo vệ Agent Memory khỏi mất mát](./5-production-ops-and-security/1-persistence-and-dr-for-agent-memory.md) | 🚧 Sắp ra mắt |
| 2 | [High Availability — Redis Sentinel & Cluster cho Agent Fleet 24/7](./5-production-ops-and-security/2-high-availability-sentinel-cluster.md) | 🚧 Sắp ra mắt |
| 3 | [Monitoring & Observability — Theo dõi Hit-rate, Latency & Memory](./5-production-ops-and-security/3-monitoring-and-observability.md) | 🚧 Sắp ra mắt |
| 4 | [Security — ACL, TLS & Credential Management cho Multi-Agent System](./5-production-ops-and-security/4-security-acl-and-tls.md) | 🚧 Sắp ra mắt |

---

### 🔜 [Chương 6: Hands-on AI Agent Projects](./6-hands-on-ai-agent-projects/)
Source code hoàn chỉnh — từ prototype đến production-grade Agent System.

| # | Project | Stack | Trạng thái |
|---|---------|-------|-----------|
| 1 | [Semantic Cache Proxy cho LLM API](./6-hands-on-ai-agent-projects/project-1-semantic-cache-proxy/) | FastAPI + RediSearch | 🚧 Sắp ra mắt |
| 2 | [Long-term Memory Chatbot](./6-hands-on-ai-agent-projects/project-2-long-term-memory-agent/) | LangChain + RedisJSON + RediSearch | 🚧 Sắp ra mắt |
| 3 | [Reliable Multi-Agent Research System](./6-hands-on-ai-agent-projects/project-3-reliable-multi-agent-system/) | LangGraph + CrewAI + Redis Streams | 🚧 Sắp ra mắt |

---

## 🗺️ Bản đồ kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│                 AI Agent Fleet (Chương 4)                   │
│   Orchestrator ──Streams──► Worker Agents ──ACK──► DLQ      │
│        │ LangGraph Checkpointer (Redis)                      │
└────────┼────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Redis Iris AI Platform (Chương 3)              │
│  ┌────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │ LangCache  │  │  Agent Memory    │  │ Context         │  │
│  │(Semantic   │  │ (Working Buffer  │  │ Retriever       │  │
│  │ Cache LLM) │  │ + Episodic Vec.) │  │ (CDC via RDI)   │  │
│  └────────────┘  └──────────────────┘  └─────────────────┘  │
└────────┼────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│           Redis Stack Core (Chương 1 & 2)                   │
│  RedisJSON (State)  RediSearch (Vector Index, HNSW)         │
│  Distributed Locks  Eviction Policies  TTL Strategy         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│        Production & Security Layer (Chương 5)               │
│  Sentinel (HA)  Cluster  RDB+AOF  ACL  TLS  Grafana         │
└─────────────────────────────────────────────────────────────┘
```
