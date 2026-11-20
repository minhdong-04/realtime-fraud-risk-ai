"""
{
    script : locustfile.py
    desc   : Locust script sinh tải 1000 TPS cho API chấm điểm rủi ro (LOAD-01 đến LOAD-04).
}
"""

import os

from locust import HttpUser, task, between

class FraudScoringUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def submit_transaction(self):
        payload = {
            "transaction_id": "txn_load_test",
            "account_id": "acc_load_001",
            "amount": 150000.0,
            "currency": "VND",
        }
        self.client.post("/internal/v1/score", json=payload, headers={"X-Internal-API-Key": os.environ.get("INTERNAL_API_KEY", "development-internal-key")})
