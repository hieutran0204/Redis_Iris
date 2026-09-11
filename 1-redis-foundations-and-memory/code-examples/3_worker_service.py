"""
name: 3_worker_service.py
description: Dedicated async tool worker that blocks and continuously listens to Redis Streams for incoming tasks.
"""

import os
import time
import redis

# Kết nối Redis
pwd = os.getenv("REDIS_PASSWORD", "secret123")
client = redis.Redis(host="localhost", port=6379, password=pwd, db=0, decode_responses=True)

STREAM_NAME = "agent:stream:tools"
GROUP_NAME = "workers_group"
WORKER_NAME = "worker_alpha"

# Khởi tạo Group nếu chưa có
try:
    client.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    print(f"[*] Đã khởi tạo Consumer Group '{GROUP_NAME}' trên stream '{STREAM_NAME}'")
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise e

print(f"\n=======================================================")
print(f"🚀 WORKER [{WORKER_NAME}] ĐÃ SẴN SÀNG & ĐANG CHỜ TÁC VỤ...")
print(f"   (Terminal này sẽ đứng chờ. Hãy sang Terminal khác gõ lệnh!)")
print(f"=======================================================\n")

while True:
    try:
        # Chờ tối đa 5 giây (block=5000), nếu không có task thì lặp tiếp
        entries = client.xreadgroup(
            groupname=GROUP_NAME,
            consumername=WORKER_NAME,
            streams={STREAM_NAME: ">"},
            count=1,
            block=5000
        )

        if not entries:
            # Hết 5s mà không có việc, in chấm nhỏ báo hiệu vẫn đang sống
            print(".", end="", flush=True)
            continue

        print("\n")
        _, messages = entries[0]
        msg_id, data = messages[0]

        print(f"🔔 [NHẬN TÁC VỤ] ID: {msg_id}")
        print(f"   - Tool cần chạy : {data.get('tool')}")
        print(f"   - Tham số đầu vào: {data.get('params')}")

        # Giả lập thời gian suy nghĩ / xử lý của tool
        print(f"   ⏳ Đang thực thi...")
        time.sleep(1.5)

        # Tính toán kết quả
        result = ""
        if data.get("tool") == "calculator":
            expr = data.get("params", "0")
            try:
                result = str(eval(expr, {"__builtins__": None}, {}))
            except Exception as err:
                result = f"Lỗi tính toán: {err}"
        else:
            result = f"Đã thực thi thành công tool '{data.get('tool')}' với tham số '{data.get('params')}'"

        print(f"   ✅ KẾT QUẢ: {result}")

        # GỬI XACK ĐỂ BÁO CÁO HOÀN THÀNH
        client.xack(STREAM_NAME, GROUP_NAME, msg_id)
        print(f"   📤 Đã gửi XACK xác nhận xong task {msg_id}!")
        print(f"--- Đang tiếp tục chờ việc tiếp theo... ---\n")

    except KeyboardInterrupt:
        print("\n👋 Worker dừng hoạt động.")
        break
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        time.sleep(2)
