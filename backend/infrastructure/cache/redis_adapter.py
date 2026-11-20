"""
{
    module : redis_adapter.py
    desc   : Adapter cho Online Feature Store va Cache ket qua cham diem tren Redis.
             Ket noi Redis server that qua create_redis_client().
}
"""

import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


def create_redis_client() -> Any:
    """
    {
        func   : create_redis_client
        desc   : Tao ket noi toi Redis server that, tra ve None neu khong ket noi duoc
        input  : None
        output : redis.Redis hoac None
        loop   : 0 loops
    }
    """
    try:
        import redis
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True,
        )
        client.ping()
        logger.info("Da ket noi Redis tai %s:%s", client.connection_pool.connection_kwargs.get("host"), client.connection_pool.connection_kwargs.get("port"))
        return client
    except ImportError:
        logger.warning("thu vien redis chua cai dat — dung in-memory fallback")
        return None
    except Exception:
        logger.warning("Khong ket noi duoc Redis — dung in-memory fallback")
        return None


class RedisAdapter:
    """
    {
        class  : RedisAdapter
        desc   : Adapter ket noi Redis feature store truc tuyen va bo nho dem cache ket qua
        note   : Tu dong dung dictionary bo nho trong neu dich vu Redis khong ket noi duoc
    }
    """

    def __init__(self, redis_client: Any = None) -> None:
        self._client = redis_client
        self._memory_store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        """
        {
            func   : get
            desc   : Lay gia tri theo khoa tu Redis hoac bo nho dem phu
            input  : key (str) — khoa tim kiem
            output : Any | None
            loop   : 0 loops
        }
        """
        if self._client:
            try:
                val = self._client.get(key)
                return val.decode("utf-8") if isinstance(val, bytes) else val
            except Exception:
                pass
        return self._memory_store.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        {
            func   : set
            desc   : Ghi gia tri vao cache voi thoi gian song TTL tuy chon
            input  : key (str), value (Any), ttl (int) — thoi gian song (giay)
            output : None
            loop   : 0 loops
        }
        """
        if self._client:
            try:
                self._client.set(key, str(value), ex=ttl)
                return
            except Exception:
                pass
        self._memory_store[key] = str(value)

    def set_features(self, account_id: str, features: dict[str, Any], ttl: int = 86400) -> None:
        """
        {
            func   : set_features
            desc   : Luu tap dac trung da tinh toan cua tai khoan vao online feature store
            input  : account_id (str), features (dict), ttl (int)
            output : None
            loop   : 1 loop — luu tung khoa dac trung vao cache
        }
        """
        # { loop-1: luu tung dac trung truc tuyen theo account_id }
        for k, v in features.items():
            self.set(f"feature:{account_id}:{k}", v, ttl=ttl)

    def get_features(self, account_id: str, feature_names: list[str]) -> dict[str, Any]:
        """
        {
            func   : get_features
            desc   : Truy xuat tap dac trung truc tuyen cua tai khoan
            input  : account_id (str), feature_names (list[str])
            output : dict[str, Any]
            loop   : 1 loop — truy van tung dac trung tu cache store
        }
        """
        result = {}
        # { loop-1: lay tung dac trung theo ten cho account_id }
        for name in feature_names:
            val = self.get(f"feature:{account_id}:{name}")
            if val is not None:
                try:
                    result[name] = float(val) if "." in val else int(val)
                except ValueError:
                    result[name] = val
        return result
