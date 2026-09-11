"""
name: 1_data_structures_for_agents.py
description: Interactive step-by-step tutorial comparing String, Hash, and List for AI Agent memory components with live Redis Insight verification.
"""

import os
import json
import time
from typing import Optional
import redis


def get_client() -> redis.Redis:
    """Connect to Redis using password from environment or docker default."""
    pwd = os.getenv("REDIS_PASSWORD", "secret123")
    return redis.Redis(host="localhost", port=6379, password=pwd, db=0, decode_responses=True)


def step_pause(prompt_msg: str = "👉 Nhấn [Enter] để tiếp tục bước tiếp theo..."):
    """Pauses execution to allow user to inspect state in Redis Insight."""
    print(f"\n{prompt_msg}")
    input()


def main():
    try:
        client = get_client()
        client.ping()
    except Exception as e:
        print(f"\n❌ Không thể kết nối tới Redis: {e}")
        print("   Hãy bật Docker: docker compose up -d")
        return

    print("=" * 70)
    print("🎓 LAB 1.1: TỰ TAY KHÁM PHÁ CÁC CẤU TRÚC DỮ LIỆU REDIS CHO AI AGENT")
    print("=" * 70)
    print("Mục tiêu: Thấy tận mắt String, Hash, List lưu gì trên RAM và tại sao")
    print("không nên dùng RedisJSON cho tất cả mọi thứ.")
    print("💡 Mẹo: Mở sẵn Redis Insight tại http://localhost:8001 để đối chiếu!")
    
    step_pause("👉 Nhấn [Enter] để bắt đầu BƯỚC 1 (STRING)...")

    # -------------------------------------------------------------------------
    # PHẦN 1: STRING - BỘ ĐẾM TOKEN
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("📌 BƯỚC 1: STRING — THEO DÕI TOKEN TIÊU THỤ BẰNG LỆNH INCRBY")
    print("-" * 70)
    print("❓ BÀI TOÁN: Sau mỗi lần gọi LLM (OpenAI/Gemini), bạn cần cộng dồn số token.")
    print("   Nếu dùng JSON: Phải đọc cả JSON -> parse -> cộng -> ghi đè (CỰC CHẬM).")
    print("   Dùng String: Chỉ 1 lệnh INCRBY duy nhất thực thi trong 0.0001 giây!")

    user_key = "agent:usage:user_alex"
    client.delete(user_key)  # Reset sạch trước khi demo

    print(f"\n1. Lần gọi LLM thứ nhất tiêu tốn 150 tokens.")
    print(f"   [Lệnh Redis gửi đi]: INCRBY {user_key} 150")
    val1 = client.incrby(user_key, 150)
    print(f"   => Giá trị trên Redis hiện tại: {val1}")

    print(f"\n2. Lần gọi LLM thứ hai tiêu tốn thêm 220 tokens.")
    print(f"   [Lệnh Redis gửi đi]: INCRBY {user_key} 220")
    val2 = client.incrby(user_key, 220)
    print(f"   => Giá trị trên Redis hiện tại: {val2}")

    print(f"\n👀 HÃY MỞ REDIS INSIGHT:")
    print(f"   - Tìm key: '{user_key}'")
    print(f"   - Bạn sẽ thấy nó là kiểu String, giá trị lưu đúng: '{val2}'")
    step_pause()

    # -------------------------------------------------------------------------
    # PHẦN 2: HASH - CẤU HÌNH & METADATA CỦA SESSION
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("📌 BƯỚC 2: HASH — LƯU METADATA PHIÊN LÀM VIỆC CỦA AGENT")
    print("-" * 70)
    print("❓ BÀI TOÁN: Một session có các thuộc tính: model, user, status, temperature.")
    print("   Hash cho phép đọc/sửa độc lập từng field mà không ảnh hưởng field khác.")

    meta_key = "agent:session:sess_101:meta"
    client.delete(meta_key)

    print(f"\n1. Khởi tạo metadata cho phiên làm việc:")
    print(f"   [Lệnh Redis gửi đi]: HSET {meta_key} model 'gpt-4o' user 'alex' status 'active'")
    client.hset(meta_key, mapping={
        "model": "gpt-4o",
        "user_id": "usr_alex",
        "status": "active",
        "turn_count": "0"
    })

    print(f"\n2. AI hoàn thành xong 1 lượt suy luận, ta chỉ tăng số turn:")
    print(f"   [Lệnh Redis gửi đi]: HINCRBY {meta_key} turn_count 1")
    client.hincrby(meta_key, "turn_count", 1)

    print(f"\n3. Đọc dữ liệu từ Redis:")
    meta_data = client.hgetall(meta_key)
    for k, v in meta_data.items():
        print(f"   • {k:12}: {v}")

    print(f"\n👀 HÃY MỞ REDIS INSIGHT:")
    print(f"   - Tìm key: '{meta_key}'")
    print(f"   - Icon màu đỏ dạng bảng (Hash). Bạn có thể bấm vào sửa trực tiếp từng field!")
    step_pause()

    # -------------------------------------------------------------------------
    # PHẦN 3: LIST - SLIDING WINDOW CONVERSATION BUFFER
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("📌 BƯỚC 3: LIST — SLIDING WINDOW BUFFER (TỰ CẮT TỈA HỘI THOẠI CŨ)")
    print("-" * 70)
    print("❓ BÀI TOÁN: Context Window của LLM có hạn. Ta chỉ muốn giữ 3 câu chat gần nhất.")
    print("   Bí quyết: Dùng LPUSH (đẩy vào đầu) + LTRIM 0 2 (chỉ giữ đúng 3 câu, câu thứ 4 tự rơi!).")
    print("   Không cần thuật toán cắt mảng, không tốn CPU của Backend!")

    buffer_key = "agent:buffer:sess_101"
    client.delete(buffer_key)

    dialogue = [
        "1. User: Chào bạn!",
        "2. AI: Chào Alex, tôi giúp gì được?",
        "3. User: Thời tiết hôm nay thế nào?",
        "4. AI: Trời nhiều mây, 28 độ C.",
        "5. User: Chiều có mưa không bạn?"
    ]

    print(f"\nGiả lập User và AI chat lần lượt 5 câu. Giới hạn buffer = 3 câu:")
    for turn in dialogue:
        time.sleep(0.4)
        print(f"\n   Đẩy vào: '{turn}'")
        print(f"   [Lệnh Redis]: LPUSH {buffer_key} '{turn}'  kèm  LTRIM {buffer_key} 0 2")
        
        pipe = client.pipeline()
        pipe.lpush(buffer_key, turn)
        pipe.ltrim(buffer_key, 0, 2)  # Chỉ giữ index 0, 1, 2 (tổng cộng 3 phần tử)
        pipe.execute()

        current_items = client.lrange(buffer_key, 0, -1)
        print(f"   => Danh sách hiện tại trong RAM ({len(current_items)} phần tử):")
        for item in current_items:
            print(f"      - {item}")

    print(f"\n💡 KẾT QUẢ: 2 câu chat đầu tiên (câu 1 và câu 2) đã TỰ ĐỘNG BỊ XÓA BỎ!")
    print(f"   RAM của Redis luôn sạch, không bao giờ lo phình bộ nhớ vì lịch sử chat dài.")

    print(f"\n👀 HÃY MỞ REDIS INSIGHT:")
    print(f"   - Tìm key: '{buffer_key}' (icon danh sách màu xanh dương)")
    print(f"   - Kiểm tra xem có đúng là chỉ còn 3 phần tử gần nhất không!")

    print("\n" + "=" * 70)
    print("🎉 BẠN ĐÃ HIỂU RÕ BẢN CHẤT CỦA 3 CẤU TRÚC DỮ LIỆU CỐT LÕI!")
    print("   • Đếm token/flags     -> Dùng STRING (INCRBY)")
    print("   • Metadata cấu hình   -> Dùng HASH (HSET/HGET)")
    print("   • Buffer hội thoại    -> Dùng LIST (LPUSH + LTRIM)")
    print("=" * 70)


if __name__ == "__main__":
    main()
