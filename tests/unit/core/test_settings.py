"""
{
    module : test_settings.py
    desc   : Kiểm thử cấu hình môi trường ứng dụng và URL cơ sở dữ liệu.
}
"""

import os
from backend.infrastructure.db.session import DATABASE_URL

def test_database_url_configured():
    # Kiểm thử URL database được định nghĩa hợp lệ
    assert DATABASE_URL is not None
    assert isinstance(DATABASE_URL, str)
