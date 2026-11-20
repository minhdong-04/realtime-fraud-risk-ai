"""
{
    module : alert_service.py
    desc   : Application Service phát cảnh báo tự động khi phát hiện rủi ro cao hoặc trôi đặc trưng.
}
"""

class AlertService:
    """
    {
        class  : AlertService
        desc   : Service phát đi các thông báo cảnh báo qua webhook hoặc log kiểm vết
    }
    """

    def send_alert(self, title: str, message: str, level: str = "WARNING") -> bool:
        """
        {
            func   : send_alert
            desc   : Gửi cảnh báo hệ thống
            input  : title (str), message (str), level (str)
            output : (bool) — True nếu gửi thành công
            loop   : 0 loops
        }
        """
        print(f"[ALERT - {level}] {title}: {message}")
        return True
