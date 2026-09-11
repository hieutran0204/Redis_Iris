"""
name: 3_agent_interactive_sender.py
description: Interactive CLI allowing the user to type tool requests and publish them to Redis Streams in real-time.
"""

import os
import time
import redis

# Kết nối Redis
pwd = os.getenv("REDIS_PASSWORD", "secret123")
client = redis.Redis(host="localhost", port=6379, password=pwd, db=0, decode_responses=True)

STREAM_NAME = "agent:stream:tools"

print("=======================================================")
print("🤖 AGENT INTERACTIVE SENDER (Trình điều khiển Agent)")
print("   Gõ bất kỳ phép tính nào để bắn task sang Worker qua Redis Streams!")
print("   Ví dụ: 125 * 4, 999 / 3, (10 + 20) * 5")
print("   Gõ 'exit' để thoát.")
print("=======================================================\n")

while True:
    try:
        user_input = input("👉 Nhập phép tính cần Tool xử lý: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 Đã thoát.")
            break

        # Bắn sự kiện vào Redis Stream bằng lệnh XADD (kèm MAXLEN ~ 1000 chống tràn RAM)
        msg_id = client.xadd(STREAM_NAME, {
            "tool": "calculator",
            "params": user_input,
            "sender": "InteractiveAgent",
            "timestamp": str(time.time())
        }, maxlen=1000, approximate=True)

        print(f"🚀 Đã bắn task sang Redis Streams!")
        print(f"   -> Message ID: {msg_id}")
        print(f"   (Hãy nhìn sang cửa sổ Worker để thấy nó chộp lấy task và tính toán!)\n")

    except KeyboardInterrupt:
        print("\n👋 Đã thoát.")
        break
    except Exception as e:
        print(f"❌ Lỗi: {e}\n")
