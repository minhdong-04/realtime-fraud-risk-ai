"""
{
    script : 04_kafka_paysim_producer.py
    desc   : Doc PaySim streaming_sample.parquet, publish len Kafka topic hoac
             gui truc tiep qua API Scoring de simulate real-time transaction stream
    input  : data/features/paysim/streaming_sample.parquet
    output : Kafka topic: transaction.created hoac POST http://localhost:8000/internal/v1/score
    loop   : 1 loop — stream tung giao dich
    run    : python scripts/04_kafka_paysim_producer.py --speed 0.5
}
"""

import sys
import os
import json
import time
import uuid
import argparse
import urllib.request
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SAMPLE_PATH = "data/features/paysim/streaming_sample.parquet"
KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "transaction.created"
API_SCORE_URL = "http://localhost:8000/internal/v1/score"
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "development-internal-key")

def row_to_transaction(row: pd.Series) -> dict:
    """
    {
        func   : row_to_transaction
        desc   : Convert PaySim row thanh transaction payload format cua API
        input  : row (pd.Series)
        output : dict
        loop   : 0 loops
    }
    """
    is_fraud = int(row.get("isFraud", 0))
    is_transfer = bool(row.get("is_transfer", 1))
    step = int(row.get("step", 0))

    return {
        "transaction_id": f"PAYSIM-{uuid.uuid4().hex[:8].upper()}",
        "account_id": f"acc-{abs(hash(str(step))) % 1000:04d}",
        "merchant_id": "merch-paysim-vn",
        "device_id": str(uuid.uuid4()) if is_fraud else "device-known-001",
        "amount": float(row.get("amount", 0)),
        "currency": "VND",
        "transaction_type": "TRANSFER" if is_transfer else "CASH_OUT",
        "channel": "MOBILE",
        "is_fraud_label": is_fraud,
        "step": step,
    }

def post_to_backend(payload: dict) -> dict | None:
    """
    {
        func   : post_to_backend
        desc   : Gui giao dich truc tiep vao backend FastAPI qua Internal API Key
        input  : payload (dict)
        output : dict | None
        loop   : 0 loops
    }
    """
    try:
        req_data = json.dumps({
            "transaction_id": payload["transaction_id"],
            "account_id": payload["account_id"],
            "merchant_id": payload["merchant_id"],
            "device_id": payload["device_id"],
            "amount": payload["amount"],
            "currency": payload["currency"],
            "transaction_type": payload["transaction_type"],
            "channel": payload["channel"],
        }).encode("utf-8")

        req = urllib.request.Request(
            API_SCORE_URL,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "X-Internal-API-Key": INTERNAL_API_KEY,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

def main():
    """
    {
        func   : main
        desc   : Dieu phoi stream giao dich tu tap PaySim
        input  : None
        output : None
        loop   : 1 loop — gui tung ban ghi
    }
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--speed", type=float, default=0.5, help="Giay giua 2 messages")
    parser.add_argument("--limit", type=int, default=None, help="So messages toi da")
    args = parser.parse_args()

    if not os.path.exists(SAMPLE_PATH):
        print(f"[WARN] Chua co {SAMPLE_PATH}. Vui long chay python scripts/02c_process_paysim.py truoc.")
        return

    df = pd.read_parquet(SAMPLE_PATH)
    if args.limit:
        df = df.head(args.limit)

    producer = None
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=1000,
        )
    except Exception:
        pass

    mode_str = "Kafka Broker (localhost:9092)" if producer else f"Direct HTTP API Stream ({API_SCORE_URL})"
    print(f"\n[START] Dang phat dong {len(df)} giao dich PaySim -> Mode: {mode_str}")
    sent_count = 0
    fraud_count = 0

    # { loop-1: stream tung row voi delay de simulate real-time }
    for _, row in df.iterrows():
        payload = row_to_transaction(row)
        if producer:
            try:
                producer.send(TOPIC, value=payload)
            except Exception:
                post_to_backend(payload)
        else:
            post_to_backend(payload)

        sent_count += 1
        fraud_count += payload["is_fraud_label"]
        label = "[FRAUD]" if payload["is_fraud_label"] else "[LEGIT]"
        print(f"  [{sent_count:04d}] {label} {payload['transaction_id']} | amount={payload['amount']:>12,.0f} VND | type={payload['transaction_type']}")
        time.sleep(args.speed)

    if producer:
        producer.flush()
    print(f"\n[DONE] Da stream thanh cong: {sent_count} messages | {fraud_count} fraud sent\n")

if __name__ == "__main__":
    main()
