"""
name: 2_agent_state_store.py
description: Interactive step-by-step tutorial for Lesson 1.2 demonstrating RedisJSON atomic partial updates, token tracking, and context trimming.
"""

import os
import json
import time
from typing import Any, Dict, List, Optional
import redis


class AgentStateStore:
    """
    Manages complex hierarchical agent state using RedisJSON.
    Supports atomic partial updates without downloading/re-uploading entire documents.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0
    ):
        pwd = password or os.getenv("REDIS_PASSWORD", "secret123")
        self.client = redis.Redis(host=host, port=port, password=pwd, db=db, decode_responses=True)

    def key(self, session_id: str) -> str:
        return f"agent:session:{session_id}"

    def init_session(self, session_id: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize a new agent session state at root node ($)."""
        k = self.key(session_id)
        initial_state = {
            "session_id": session_id,
            "user_id": user_id,
            "status": "active",
            "total_tokens": 0,
            "metadata": metadata or {},
            "messages": []
        }
        return bool(self.client.json().set(k, "$", initial_state))

    def append_message(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict]] = None) -> int:
        """Atomically append a single message to $.messages array via JSON.ARRAPPEND."""
        k = self.key(session_id)
        msg: Dict[str, Any] = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls

        result = self.client.json().arrappend(k, "$.messages", msg)
        return result[0] if result else 0

    def add_tokens(self, session_id: str, tokens: int) -> int:
        """Increment token counter via JSON.NUMINCRBY without reading document."""
        k = self.key(session_id)
        res = self.client.json().numincrby(k, "$.total_tokens", tokens)
        return int(res[0]) if res else 0

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve messages for LLM context, safely slicing in Python."""
        k = self.key(session_id)
        res = self.client.json().get(k, "$.messages")
        msgs = res[0] if (res and isinstance(res, list)) else []
        if limit and limit > 0:
            return msgs[-limit:]
        return msgs

    def pop_oldest_message(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Trim the oldest message at index 0 via JSON.ARRPOP to manage context window."""
        k = self.key(session_id)
        popped = self.client.json().arrpop(k, "$.messages", 0)
        return popped[0] if popped else None

    def set_status(self, session_id: str, status: str) -> bool:
        """Update session status field via JSON.SET."""
        k = self.key(session_id)
        return bool(self.client.json().set(k, "$.status", status))

    def get_full_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the full hierarchical JSON document."""
        return self.client.json().get(self.key(session_id))


def step_pause(msg: str = "👉 Nhấn [Enter] để tiếp tục bước tiếp theo..."):
    print(f"\n{msg}")
    input()


def main():
    try:
        store = AgentStateStore()
        store.client.ping()
    except Exception as e:
        print(f"\n❌ Lỗi kết nối Redis: {e}")
        print("   Hãy bật Docker: docker compose up -d")
        return

    session_id = "agent_lab_02"
    key_name = store.key(session_id)
    store.client.delete(key_name)  # Reset trước khi demo

    print("=" * 70)
    print("🎓 LAB 1.2: TỰ TAY THỰC HÀNH REDISJSON CHO AGENT STATE STORE")
    print("=" * 70)
    print("Mục tiêu: Hiểu cơ chế Atomic Partial Update và JSONPath trên RAM.")
    print("💡 Mở sẵn Redis Insight tại http://localhost:8001 để xem cây JSON biến đổi!")

    # BƯỚC 1: KHỞI TẠO STATE GỐC
    print("\n" + "-" * 70)
    print("📌 BƯỚC 1: KHỞI TẠO ROOT STATE BẰNG LỆNH JSON.SET")
    print("-" * 70)
    print(f"Agent bắt đầu một cuộc trò chuyện mới với User 'dev_alex'.")
    print(f"[Lệnh Redis]: JSON.SET {key_name} $ '{{...}}'")
    
    store.init_session(session_id, user_id="dev_alex", metadata={"channel": "web_chat"})
    print(f"✅ Đã khởi tạo thành công State trên RAM!")

    print(f"\n👀 HÃY MỞ REDIS INSIGHT (http://localhost:8001):")
    print(f"   1. Tìm key: '{key_name}'")
    print(f"   2. Bấm vào key, bạn sẽ thấy nó bung ra một cây thư mục JSON tuyệt đẹp!")
    print(f"   3. Lưu ý: Trường 'messages' hiện tại đang là mảng rỗng `[]` và total_tokens = 0.")
    step_pause()

    # BƯỚC 2: USER NÓI - ARRAPPEND VÀO MẢNG
    print("\n" + "-" * 70)
    print("📌 BƯỚC 2: USER GỬI TIN NHẮN ĐẦU TIÊN — GỌI LỆNH JSON.ARRAPPEND")
    print("-" * 70)
    print("❓ BÀI TOÁN: Thêm 1 câu nói của user vào mảng $.messages.")
    print("   KHÔNG TẢI CẢ FILE VỀ! Chỉ gửi đúng vài byte câu nói qua mạng.")
    user_msg = "Viết giúp tôi 1 hàm kiểm tra số nguyên tố bằng Python."
    print(f"   Nội dung: '{user_msg}'")
    print(f"   [Lệnh Redis]: JSON.ARRAPPEND {key_name} $.messages '{{\"role\":\"user\",\"content\":\"...\"}}'")

    new_len = store.append_message(session_id, role="user", content=user_msg)
    print(f"   => Redis trả về độ dài mới của mảng messages: {new_len}")

    print(f"\n👀 MỞ LẠI REDIS INSIGHT:")
    print(f"   - Nhấn nút Refresh (F5) hoặc bấm lại vào key '{key_name}'.")
    print(f"   - Bạn sẽ thấy mảng 'messages' tự mọc thêm 1 phần tử [0] ngay trên RAM!")
    step_pause()

    # BƯỚC 3: AI TRẢ LỜI & CỘNG TOKEN
    print("\n" + "-" * 70)
    print("📌 BƯỚC 3: AI PHẢN HỒI & TÍNH PHÍ TOKEN TIÊU THỤ")
    print("-" * 70)
    print("1. Đẩy câu trả lời của AI vào mảng:")
    ai_reply = "def is_prime(n): return n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))"
    store.append_message(session_id, role="assistant", content=ai_reply)
    print(f"   [Lệnh Redis]: JSON.ARRAPPEND {key_name} $.messages '{{\"role\":\"assistant\",...}}'")

    print("\n2. LLM vừa tiêu tốn 115 tokens, cộng dồn vào $.total_tokens:")
    print(f"   [Lệnh Redis]: JSON.NUMINCRBY {key_name} $.total_tokens 115")
    total_tokens = store.add_tokens(session_id, 115)
    print(f"   => Tổng token tích lũy hiện tại: {total_tokens}")

    print(f"\n👀 MỞ REDIS INSIGHT XEM THAY ĐỔI:")
    print(f"   - Mảng messages đã có 2 phần tử (User & Assistant).")
    print(f"   - Trường 'total_tokens' đã tự nhảy từ 0 -> 115.")
    step_pause()

    # BƯỚC 4: CẮT TỈA CONTEXT WINDOW (TRIMMING)
    print("\n" + "-" * 70)
    print("📌 BƯỚC 4: CẮT BỚT TIN NHẮN CŨ (CONTEXT TRIMMING) BẰNG JSON.ARRPOP")
    print("-" * 70)
    print("❓ BÀI TOÁN: Nếu cuộc trò chuyện quá dài, ta muốn xóa câu chat đầu tiên (index 0).")
    print(f"   [Lệnh Redis]: JSON.ARRPOP {key_name} $.messages 0")

    popped = store.pop_oldest_message(session_id)
    print(f"   => Đã pop ra tin nhắn cũ nhất: {popped}")

    print(f"\n👀 MỞ REDIS INSIGHT KIỂM CHỨNG:")
    print(f"   - Tin nhắn đầu tiên của User đã biến mất!")
    print(f"   - Chỉ còn lại câu trả lời của Assistant nằm ở index 0.")
    step_pause()

    # BƯỚC 5: ĐỔI TRẠNG THÁI STATUS
    print("\n" + "-" * 70)
    print("📌 BƯỚC 5: HOÀN TẤT PHIÊN LÀM VIỆC — CẬP NHẬT TRƯỜNG STATUS")
    print("-" * 70)
    print(f"   [Lệnh Redis]: JSON.SET {key_name} $.status '\"completed\"'")
    store.set_status(session_id, "completed")

    print("\nToàn bộ State cuối cùng lấy từ Redis:")
    full_state = store.get_full_state(session_id)
    print(json.dumps(full_state, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("🎉 BẠN ĐÃ LÀM CHỦ REDISJSON CHO AI AGENT STATE STORE!")
    print("   • Atomic partial update mảng tin nhắn bằng JSON.ARRAPPEND")
    print("   • Cộng trừ token bằng JSON.NUMINCRBY")
    print("   • Cắt tỉa context bằng JSON.ARRPOP")
    print("=" * 70)


if __name__ == "__main__":
    main()
