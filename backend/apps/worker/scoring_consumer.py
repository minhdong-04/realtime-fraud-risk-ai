"""
{
    module : scoring_consumer.py
    desc   : Worker Consumer lang nghe topic transaction.featured de cham diem rui ro qua RiskEngine.
             Ket noi Kafka KRaft mode thuc su voi aiokafka.
}
"""

import json
import logging
import os
from typing import Any

from backend.ml.inference.risk_engine import RiskEngine

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_SCORING_TOPIC", "transaction.featured")
KAFKA_GROUP = os.getenv("KAFKA_SCORING_GROUP", "scoring-workers")


class ScoringConsumer:
    """
    {
        class  : ScoringConsumer
        desc   : Worker goi RiskEngine cham diem giao dich real-time qua Kafka event
        pattern: Event-Driven Consumer (CQRS)
    }
    """

    def __init__(self) -> None:
        self._engine = RiskEngine()

    async def start(self) -> None:
        """
        {
            func   : start
            desc   : Khoi dong Kafka consumer bat dong bo, lang nghe va xu ly tung message
            input  : None
            output : None
            loop   : 1 loop — lang nghe lien tuc tung message tu Kafka topic
        }
        """
        try:
            from aiokafka import AIOKafkaConsumer
        except ImportError:
            logger.warning("aiokafka chua cai dat — chay offline mode")
            return

        consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=KAFKA_GROUP,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
        )
        await consumer.start()
        logger.info("ScoringConsumer da ket noi Kafka tai %s", KAFKA_BOOTSTRAP)
        try:
            # { loop-1: xu ly tung message tu Kafka topic }
            async for msg in consumer:
                try:
                    if isinstance(msg.value, dict):
                        result = self.process_event(msg.value)
                        logger.info("Da cham diem: score=%.4f", result["score"])
                except Exception as exc:
                    logger.error("Loi xu ly event: %s", exc)
        finally:
            await consumer.stop()

    def process_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """
        {
            func   : process_event
            desc   : Thuc thi cham diem rui ro cho vector dac trung
            input  : event_data (dict)
            output : dict — ket qua score, risk_level, triggers
            loop   : 0 loops
        }
        """
        fraud_proba, anomaly_score, risk_score = self._engine.evaluate(event_data)
        return {
            "fraud_probability": fraud_proba,
            "anomaly_score": anomaly_score,
            "score": risk_score.value,
            "risk_level": risk_score.level.value,
        }
