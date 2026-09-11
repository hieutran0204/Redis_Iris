"""
name: 3_agent_stream_loop.py
description: Event-driven AI Agent task loop and async tool worker implementation using Redis Streams and Consumer Groups.
"""

import os
import time
from typing import Dict, Optional
import redis


class AgentStreamLoop:
    """
    Manages event-driven communication between AI Agent Planner and Tool Workers
    using Redis Streams, Consumer Groups, and Acknowledgments (ACK).
    """

    def __init__(
        self,
        stream_name: str = "agent:stream:events",
        group_name: str = "tool_workers_group",
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0
    ):
        pwd = password or os.getenv("REDIS_PASSWORD", "secret123")
        self.client = redis.Redis(host=host, port=port, password=pwd, db=db, decode_responses=True)
        self.stream_name = stream_name
        self.group_name = group_name

        # Khởi tạo Consumer Group nếu chưa tồn tại
        self._ensure_consumer_group()

    def _ensure_consumer_group(self) -> None:
        """Create stream consumer group if it does not exist already."""
        try:
            # ID '0' để đọc từ đầu stream, mkstream=True để tự động tạo stream nếu chưa có
            self.client.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                pass  # Nhóm đã tồn tại từ trước, bỏ qua
            else:
                raise e

    def publish_tool_request(self, session_id: str, tool_name: str, parameters: str) -> str:
        """
        Agent Brain publishes a tool execution request to the Stream.
        Returns the unique generated message ID.
        """
        event_data = {
            "session_id": session_id,
            "event_type": "tool_call",
            "tool_name": tool_name,
            "params": parameters,
            "timestamp": str(time.time())
        }
        msg_id = self.client.xadd(self.stream_name, event_data)
        return msg_id

    def worker_poll_and_execute(self, worker_name: str, block_ms: int = 2000) -> Optional[Dict]:
        """
        Tool Worker polls for a pending task from the Consumer Group, executes it, and sends ACK.
        """
        # Đọc 1 tin nhắn mới (kí hiệu '>')
        entries = self.client.xreadgroup(
            groupname=self.group_name,
            consumername=worker_name,
            streams={self.stream_name: ">"},
            count=1,
            block=block_ms
        )

        if not entries:
            return None

        # entries format: [[stream_name, [(msg_id, data_dict)]]]
        _, messages = entries[0]
        msg_id, data = messages[0]

        print(f"[{worker_name}] Nhận được sự kiện ID={msg_id}: {data['event_type']} -> {data['tool_name']}")

        # Giả lập thực thi công cụ
        result_output = ""
        if data.get("tool_name") == "calculator":
            expr = data.get("params", "0")
            try:
                # Phép tính đơn giản an toàn
                result_output = str(eval(expr, {"__builtins__": None}, {}))
            except Exception as err:
                result_output = f"Error: {err}"
        else:
            result_output = f"Executed {data.get('tool_name')} successfully."

        # BƯỚC CỰC KỲ QUAN TRỌNG: Gửi XACK để báo cáo đã hoàn thành
        self.client.xack(self.stream_name, self.group_name, msg_id)

        # Trả về kết quả và đẩy lại 1 sự kiện tool_result vào stream
        result_event_id = self.client.xadd(self.stream_name, {
            "session_id": data["session_id"],
            "event_type": "tool_result",
            "source_msg_id": msg_id,
            "result": result_output
        })

        return {"task_id": msg_id, "result_id": result_event_id, "output": result_output}


# --- DEMO CHẠY THỰC HÀNH ---
if __name__ == "__main__":
    try:
        loop = AgentStreamLoop()
        session_id = "agent_run_999"

        print("=== BẮT ĐẦU LAB 1.3: EVENT-DRIVEN AGENT LOOP VỚI REDIS STREAMS ===")

        print("\n1. [Agent Brain] Lên kế hoạch và gửi yêu cầu tính toán vào Stream...")
        task_id = loop.publish_tool_request(
            session_id=session_id,
            tool_name="calculator",
            parameters="1250 * 8 + 450"
        )
        print(f"   -> Đã bắn sự kiện lên Redis Stream với Message ID: {task_id}")

        print("\n2. [Tool Worker] Lắng nghe Stream qua Consumer Group và thực thi...")
        execution = loop.worker_poll_and_execute(worker_name="worker_python_1")

        if execution:
            print(f"   -> Worker đã tính xong và gửi XACK!")
            print(f"   -> Kết quả: {execution['output']}")
            print(f"   -> Đã đẩy kết quả lại Stream với ID: {execution['result_id']}")

        print("\n🎉 Hoàn thành Lab 1.3! Bạn đã nắm vững cơ chế Redis Streams + Consumer Group + ACK.")

    except Exception as e:
        print(f"\n❌ Lỗi kết nối: {type(e).__name__} - {e}")
        print("   Hãy chắc chắn bạn đã bật Docker: docker compose up -d")
