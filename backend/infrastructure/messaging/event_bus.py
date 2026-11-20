"""
{
    module : event_bus.py
    desc   : Bus sự kiện (Event Bus) cho truyền thông bất đồng bộ giữa các module.
}
"""

from typing import Callable, Any
from collections import defaultdict

class EventBus:
    """
    {
        class  : EventBus
        desc   : In-process Event Bus hỗ trợ mô hình Publish-Subscribe bất đồng bộ
        pattern: Observer Pattern
    }
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        """
        {
            func   : subscribe
            desc   : Đăng ký một hàm callback lắng nghe sự kiện trên chủ đề (topic)
            input  : topic (str) — tên chủ đề sự kiện
                     handler (Callable) — hàm xử lý khi sự kiện xảy ra
            output : None
            loop   : 0 loops
        }
        """
        self._subscribers[topic].append(handler)

    def publish(self, topic: str, payload: Any) -> None:
        """
        {
            func   : publish
            desc   : Phát dữ liệu sự kiện tới tất cả các hàm đăng ký lắng nghe trên topic
            input  : topic (str) — tên chủ đề
                     payload (Any) — nội dung dữ liệu sự kiện
            output : None
            loop   : 1 loop — kích hoạt từng hàm xử lý trong danh sách đăng ký
        }
        """
        handlers = self._subscribers.get(topic, [])
        # { loop-1: kích hoạt từng handler lắng nghe sự kiện }
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                print(f"[EventBus Error] Lỗi xử lý sự kiện chủ đề {topic}: {e}")

event_bus = EventBus()
