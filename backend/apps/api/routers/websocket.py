"""
{
    module : websocket.py
    desc   : Router API WebSocket đẩy thông báo ca rủi ro mới theo thời gian thực tới Analyst Dashboard (US-01 AC-01-06).
}
"""

from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    """
    {
        class  : ConnectionManager
        desc   : Quản lý các kết nối WebSocket đang hoạt động của giao diện Analyst Dashboard
    }
    """

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        {
            func   : broadcast
            desc   : Phát dữ liệu JSON tới tất cả các client frontend đang kết nối
            input  : message (dict)
            output : None
            loop   : 1 loop — phát tin nhắn tới danh sách các kết nối WebSocket
        }
        """
        # { loop-1: phát thông điệp sự kiện tới tất cả kết nối WebSocket }
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()

@router.websocket("/ws/fraud-cases")
async def websocket_fraud_cases(websocket: WebSocket):
    """
    {
        func   : websocket_fraud_cases
        desc   : Endpoint WebSocket đẩy ca rủi ro mới tới Analyst Dashboard
        input  : websocket (WebSocket)
        output : None
        loop   : 1 loop — duy trì lắng nghe ngắt kết nối client
    }
    """
    await ws_manager.connect(websocket)
    try:
        # { loop-1: duy trì luồng kết nối WebSocket }
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
