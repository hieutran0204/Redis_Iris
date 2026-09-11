"""
name: 5_distributed_lock_and_pool.py
description: Interactive step-by-step tutorial demonstrating Connection Pooling and Distributed Locking to prevent socket leaks and tool race conditions.
"""

import os
import time
from typing import Optional
import redis


def get_pool() -> redis.ConnectionPool:
    """Singleton Connection Pool preventing TCP socket exhaustion."""
    pwd = os.getenv("REDIS_PASSWORD", "secret123")
    return redis.ConnectionPool(
        host="localhost",
        port=6379,
        password=pwd,
        db=0,
        max_connections=10,
        decode_responses=True
    )


def step_pause(msg: str = "👉 Nhấn [Enter] để tiếp tục bước tiếp theo..."):
    print(f"\n{msg}")
    input()


def main():
    pool = get_pool()
    client = redis.Redis(connection_pool=pool)

    try:
        client.ping()
    except Exception as e:
        print(f"\n❌ Lỗi kết nối Redis: {e}")
        return

    print("=" * 70)
    print("🎓 LAB 1.5: DISTRIBUTED LOCKS & CONNECTION POOLING")
    print("=" * 70)
    print("Mục tiêu: Hiểu cách chống sập server do leak socket")
    print("và chống tranh chấp (race condition) khi nhiều Sub-Agent cùng gọi 1 Tool.")

    # BƯỚC 1: CONNECTION POOLING
    print("\n" + "-" * 70)
    print("📌 BƯỚC 1: CONNECTION POOLING — NGĂN CHẶN CẠN KIỆT TCP SOCKET")
    print("-" * 70)
    print("❓ BÀI TOÁN: Agent loop gọi Redis hàng ngàn lần. Nếu tạo kết nối mới liên tục,")
    print("   OS sẽ hết cổng mạng (TIME_WAIT leak) và sập ứng dụng.")
    print("   Giải pháp: Connection Pool tạo sẵn tối đa 10 kết nối dùng chung.")

    client_a = redis.Redis(connection_pool=pool)
    client_b = redis.Redis(connection_pool=pool)
    print(f"Mượn Client A từ Pool -> Ping: {client_a.ping()}")
    print(f"Mượn Client B từ Pool -> Ping: {client_b.ping()}")
    print("✅ Cả 2 client đều tái sử dụng chung nhóm socket mà không tốn công tạo mới!")
    step_pause()

    # BƯỚC 2: TỰ TAY CHIẾM KHÓA BẰNG LỆNH REDIS THÔ
    print("\n" + "-" * 70)
    print("📌 BƯỚC 2: TỰ TAY CHIẾM KHÓA (ACQUIRE LOCK) BẰNG 'SET ... NX PX'")
    print("-" * 70)
    print("❓ BÀI TOÁN: Sub-Agent 1 muốn đặt vé máy bay chuyến 'VN123'.")
    print("   Ta tạo khóa với timeout 10 giây (PX 10000) và cờ NX (chỉ tạo nếu chưa ai có).")

    lock_key = "lock:flight:VN123"
    client.delete(lock_key)  # Reset sạch trước khi thử

    token_agent_1 = "token_worker_agent_1"
    print(f"\n[Sub-Agent 1 gửi lệnh]: SET {lock_key} '{token_agent_1}' NX PX 10000")
    result_1 = client.set(lock_key, token_agent_1, nx=True, px=10000)
    print(f"   => Kết quả trả về: {result_1} (OK -> Chiếm khóa THÀNH CÔNG!)")

    print(f"\n👀 MỞ REDIS INSIGHT (http://localhost:8001):")
    print(f"   - Tìm key '{lock_key}'")
    print(f"   - Bạn sẽ thấy key này đang tồn tại và có TTL đếm ngược từ 10 giây!")
    step_pause()

    # BƯỚC 3: SUB-AGENT 2 CỐ TÌNH XÂM PHẠM
    print("\n" + "-" * 70)
    print("📌 BƯỚC 3: SUB-AGENT 2 CỐ TÌNH TRANH CHẤP KHI KHÓA ĐANG BỊ CHIẾM")
    print("-" * 70)
    token_agent_2 = "token_worker_agent_2"
    print(f"[Sub-Agent 2 gửi lệnh]: SET {lock_key} '{token_agent_2}' NX PX 10000")
    result_2 = client.set(lock_key, token_agent_2, nx=True, px=10000)
    print(f"   => Kết quả trả về: {result_2} (None / nil -> BỊ TỪ CHỐI THẲNG THỪNG!)")
    print("\n💡 GIẢI THÍCH: Nhờ cờ NX, Redis từ chối Sub-Agent 2. Tool đặt vé được bảo vệ,")
    print("   tránh hoàn toàn hiện tượng 2 người cùng đặt 1 chỗ ngồi (Double-booking)!")
    step_pause()

    # BƯỚC 4: GIẢI PHÓNG KHÓA AN TOÀN BẰNG LUA SCRIPT
    print("\n" + "-" * 70)
    print("📌 BƯỚC 4: GIẢI PHÓNG KHÓA AN TOÀN (CHỈ CHỦ SỞ HỮU MỚI ĐƯỢC XÓA)")
    print("-" * 70)
    print("Nếu chỉ dùng lệnh DEL lock_key, lỡ khóa đã hết hạn và người khác vừa chiếm,")
    print("bạn sẽ vô tình xóa nhầm khóa của người ta! Vì vậy phải kiểm tra token trước:")

    lua_release = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    print(f"Sub-Agent 1 thực thi xong Tool, gửi script kiểm tra token '{token_agent_1}' để xóa:")
    released = client.eval(lua_release, 1, lock_key, token_agent_1)
    print(f"   => Kết quả giải phóng: {released} (1 = Xóa thành công!)")
    print(f"   Key '{lock_key}' đã biến mất khỏi Redis. Giờ người khác có thể chiếm lại!")
    step_pause()

    # BƯỚC 5: SỬ DỤNG CONTEXT MANAGER TRONG THỰC TẾ
    print("\n" + "-" * 70)
    print("📌 BƯỚC 5: TRONG CODE THỰC TẾ DÙNG 'with client.lock(...)'")
    print("-" * 70)
    print("Thay vì tự viết Lua script, thư viện redis-py đã bọc sẵn cơ chế này:")

    print("Bắt đầu khối code an toàn:")
    with client.lock(lock_key, timeout=5):
        print("   🔒 Đang ở trong vùng khóa an toàn!")
        print("   🤖 Agent đang thực thi Tool...")
        time.sleep(1)
        print("   ✅ Tool chạy xong! Chuẩn bị thoát khối 'with'...")
    print("🔓 Đã tự động nhả khóa khi kết thúc khối 'with'!")

    print("\n" + "=" * 70)
    print("🎉 BẠN ĐÃ LÀM CHỦ DISTRIBUTED LOCKS VÀ CONNECTION POOLING!")
    print("=" * 70)


if __name__ == "__main__":
    main()
