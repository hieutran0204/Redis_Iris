"""
name: 4_memory_ttl_persistence.py
description: Interactive step-by-step tutorial demonstrating Tiered TTL countdown, key auto-expiration, and persistence checks to prevent agent amnesia.
"""

import os
import time
import redis


def get_client() -> redis.Redis:
    pwd = os.getenv("REDIS_PASSWORD", "secret123")
    return redis.Redis(host="localhost", port=6379, password=pwd, db=0, decode_responses=True)


def step_pause(msg: str = "👉 Nhấn [Enter] để tiếp tục bước tiếp theo..."):
    print(f"\n{msg}")
    input()


def main():
    try:
        client = get_client()
        client.ping()
    except Exception as e:
        print(f"\n❌ Lỗi kết nối Redis: {e}")
        return

    print("=" * 70)
    print("🎓 LAB 1.4: CHIẾN LƯỢC TTL & LƯU TRỮ BỀN VỮNG CHỐNG MẤT TRÍ NHỚ")
    print("=" * 70)
    print("Mục tiêu: Tận mắt thấy key tự động đếm ngược và bốc hơi khỏi RAM,")
    print("và cách bảo vệ bộ nhớ dài hạn của Agent.")

    # BƯỚC 1: WORKING MEMORY CÓ ĐỒNG HỒ ĐẾM NGƯỢC
    print("\n" + "-" * 70)
    print("📌 BƯỚC 1: WORKING MEMORY — ĐỒNG HỒ ĐẾM NGƯỢC TTL (TIME-TO-LIVE)")
    print("-" * 70)
    print("❓ BÀI TOÁN: Bộ nhớ phiên tạm chỉ nên tồn tại vài giờ.")
    print("   Ở đây ta thử nghiệm với TTL = 8 giây để bạn thấy nó tự hủy!")

    temp_key = "agent:session:short_term_101"
    client.set(temp_key, "Dữ liệu phiên chat tạm thời...", ex=8)
    print(f"[Lệnh Redis]: SET {temp_key} '...' EX 8")

    print(f"\n👀 MỞ REDIS INSIGHT (http://localhost:8001):")
    print(f"   Tìm key '{temp_key}', bạn sẽ thấy có cột TTL đang đếm ngược!")
    print(f"   Đang theo dõi từng giây trên màn hình console:")

    for remaining in range(8, -1, -1):
        actual_ttl = client.ttl(temp_key)
        if actual_ttl > 0:
            print(f"   ⏱️  TTL còn lại: {actual_ttl} giây...")
        else:
            print(f"   💥 HẾT GIỜ! Key đã tự động bị tiêu hủy khỏi RAM (TTL = {actual_ttl}).")
            break
        time.sleep(1)

    # Kiểm tra key còn tồn tại không
    exists = client.exists(temp_key)
    print(f"\nKiểm tra lại lệnh EXISTS {temp_key}: {exists} (0 nghĩa là không còn vết tích!)")
    step_pause()

    # BƯỚC 2: GIA HẠN TTL KHI USER CHAT TIẾP (SLIDING EXPIRATION)
    print("\n" + "-" * 70)
    print("📌 BƯỚC 2: GIA HẠN TTL MỖI KHI CÓ HOẠT ĐỘNG MỚI (HEARTBEAT REFRESH)")
    print("-" * 70)
    print("Nếu user vẫn đang tích cực trò chuyện, ta gia hạn thêm thời gian sống:")

    active_key = "agent:session:active_user"
    client.set(active_key, "User đang chat dở dang...", ex=10)
    print(f"1. Tạo session sống 10 giây. TTL hiện tại: {client.ttl(active_key)}s")

    time.sleep(3)
    print(f"2. Sau 3 giây trôi qua, TTL giảm còn: {client.ttl(active_key)}s")

    print(f"3. User gửi thêm 1 tin nhắn mới! Ta gia hạn lại thành 15 giây:")
    print(f"   [Lệnh Redis]: EXPIRE {active_key} 15")
    client.expire(active_key, 15)
    print(f"   => TTL mới sau khi gia hạn: {client.ttl(active_key)}s!")
    step_pause()

    # BƯỚC 3: BẢO VỆ SEMANTIC MEMORY (VĨNH VIỄN)
    print("\n" + "-" * 70)
    print("📌 BƯỚC 3: SEMANTIC / LONG-TERM MEMORY (KHÔNG ĐẶT TTL)")
    print("-" * 70)
    print("Hồ sơ tri thức, sở thích người dùng phải được bảo toàn vĩnh viễn:")

    perm_key = "agent:profile:user_alex:preferences"
    client.hset(perm_key, mapping={
        "preferred_language": "Vietnamese",
        "expertise": "Senior Python Developer",
        "tone": "concise"
    })
    # Không set EXPIRE -> TTL sẽ trả về -1 (vĩnh viễn)
    ttl_perm = client.ttl(perm_key)
    print(f"   [Lệnh Redis]: HSET {perm_key} ... (Không gọi EXPIRE)")
    print(f"   => TTL của profile: {ttl_perm} (-1 nghĩa là tồn tại vĩnh viễn!)")
    print(f"   Khi cấu hình 'volatile-lfu', Redis sẽ KHÔNG BAO GIỜ xóa key này khi đầy RAM!")
    step_pause()

    # BƯỚC 4: PERSISTENCE - KIỂM TRA SNAPSHOT
    print("\n" + "-" * 70)
    print("📌 BƯỚC 4: LƯU TRỮ XUỐNG Ổ ĐĨA (PERSISTENCE) ĐỂ TRÁNH MẤT TRÍ NHỚ")
    print("-" * 70)
    print("Để chắc chắn dữ liệu không mất khi reboot server, ta yêu cầu Redis snapshot ra đĩa:")
    print("[Lệnh Redis]: BGSAVE (Lưu ngầm ra file dump.rdb)")
    try:
        client.bgsave()
        print("✅ Redis đang chụp snapshot toàn bộ RAM lưu vào file 'dump.rdb'!")
    except Exception as err:
        print(f"BGSAVE thông báo: {err}")

    last_save = client.lastsave()
    print(f"Thời điểm Snapshot gần nhất (timestamp): {last_save}")

    print("\n" + "=" * 70)
    print("🎉 BẠN ĐÃ HIỂU CƠ CHẾ KIỂM SOÁT RAM VÀ BẢO TOÀN TRÍ NHỚ AGENT!")
    print("=" * 70)


if __name__ == "__main__":
    main()
