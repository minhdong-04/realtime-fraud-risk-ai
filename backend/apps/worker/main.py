"""
{
    module : main.py
    desc   : Điểm chạy chính cho các Asynchronous Event Worker Consumers (Worker Engine).
}
"""

import time
from backend.infrastructure.db.session import SessionLocal
from backend.apps.worker.outbox_publisher import OutboxPublisher

def run_worker_loop():
    """
    {
        func   : run_worker_loop
        desc   : Vòng lặp chính thực thi xuất bản Outbox events và lắng nghe các consumers
        input  : None
        output : None
        loop   : 1 loop — vòng lặp vô hạn chạy background worker
    }
    """
    print("[Worker Engine] Đang khởi chạy các tiến trình Event Consumers & Outbox Publisher...")
    db = SessionLocal()
    publisher = OutboxPublisher(db)

    # { loop-1: chạy chu kỳ quet outbox event 5 giay một lan }
    for _ in range(3):
        count = publisher.publish_pending_events()
        if count > 0:
            print(f"[Outbox Publisher] Đã xuất bản {count} sự kiện lên Kafka")
        time.sleep(1)

    db.close()
    print("[Worker Engine] Hoàn tất chu kỳ quét worker.")

if __name__ == "__main__":
    run_worker_loop()
