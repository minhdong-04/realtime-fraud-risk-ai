"""
{
    module : outbox_publisher.py
    desc   : Tien trinh background xuat ban su kien tu Transactional Outbox len Kafka.
             Ket noi AIOKafkaProducer thuc te.
}
"""

import json
import logging
import os
from typing import Any

from sqlalchemy.orm import Session
from backend.infrastructure.db.repositories.postgres_outbox_repository import PostgresOutboxRepository

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


class OutboxPublisher:
    """
    {
        class  : OutboxPublisher
        desc   : Tien trinh Publisher doc su kien outbox chua gui va day len Kafka topic
        pattern: Transactional Outbox Pattern
    }
    """

    def __init__(self, db: Session) -> None:
        self._repo = PostgresOutboxRepository(db)
        self._producer = None

    async def _get_producer(self) -> Any:
        """
        {
            func   : _get_producer
            desc   : Khoi tao AIOKafkaProducer singleton de gui message len Kafka
            input  : None
            output : AIOKafkaProducer hoac None
            loop   : 0 loops
        }
        """
        if self._producer is not None:
            return self._producer
        try:
            from aiokafka import AIOKafkaProducer
            self._producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._producer.start()
            logger.info("OutboxPublisher da ket noi Kafka tai %s", KAFKA_BOOTSTRAP)
        except ImportError:
            logger.warning("aiokafka chua cai dat — su dung in-memory event bus")
        except Exception as exc:
            logger.error("Loi ket noi Kafka Producer: %s", exc)
        return self._producer

    async def publish_pending_events_async(self) -> int:
        """
        {
            func   : publish_pending_events_async
            desc   : Doc va xuat ban bat dong bo cac su kien dang cho len Kafka
            input  : None
            output : (int) — so luong su kien da phat
            loop   : 1 loop — duyet qua danh sach su kien pending
        }
        """
        events = self._repo.fetch_pending(limit=20)
        producer = await self._get_producer()
        published_count = 0
        # { loop-1: phat tung su kien len Kafka topic }
        for evt in events:
            topic = evt.get("event_type", "unknown")
            payload = evt.get("payload", {})
            if producer:
                try:
                    await producer.send_and_wait(topic, payload)
                except Exception as exc:
                    logger.error("Loi gui event len Kafka: %s", exc)
                    continue
            published_count += 1
        return published_count

    def publish_pending_events(self) -> int:
        """
        {
            func   : publish_pending_events
            desc   : Wrapper dong bo cho publish_pending_events_async (tuong thich nguoc)
            input  : None
            output : (int) — so luong su kien da phat
            loop   : 0 loops
        }
        """
        from backend.infrastructure.messaging.event_bus import event_bus
        events = self._repo.fetch_pending(limit=20)
        published_count = 0
        for evt in events:
            event_bus.publish(evt.get("event_type", "unknown"), evt.get("payload", {}))
            published_count += 1
        return published_count
