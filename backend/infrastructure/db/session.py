"""
{
    module : session.py
    desc   : Khởi tạo database engine và quản lý phiên kết nối (session management).
}
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.infrastructure.db.models.orm_models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fraud_platform.db",
)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """
    {
        func   : init_db
        desc   : Khởi tạo schema và các bảng database nếu chưa tồn tại
        input  : None
        output : None
        loop   : 0 loops
    }
    """
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    {
        func   : get_db
        desc   : Generator dependency cung cấp database session cho API requests
        input  : None
        output : Session
        loop   : 0 loops
    }
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
