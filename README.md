# Real-Time Fraud & Transaction Risk Detection Platform

> **Version**: v2.0  
> **Backend**: Python 3.11+ / FastAPI / XGBoost / Isolation Forest / SHAP  
> **Frontend**: Next.js 16+ (App Router) / TypeScript / Tailwind CSS / Recharts  
> **Architecture**: Clean Layered Architecture & SOLID Principles

---

## 📌 Executive Summary

The **Real-Time Fraud & Transaction Risk Detection Platform** is a Machine Learning powered risk engine delivering sub-100ms real-time scoring, Explainable AI (SHAP), and a Human-in-the-Loop (HITL) review workspace for financial institutions, fintechs, and e-commerce platforms.

### Core Capabilities
- **ML Hybrid Risk Scoring Engine**: Combines XGBoost supervised classification + Isolation Forest anomaly detection + Business Rules policy overrides (BR-01..BR-12).
- **Explainable AI (SHAP)**: Top 10 feature contribution force plots for every transaction prediction.
- **Analyst Review Queue**: Prioritized fraud cases by risk score DESC with 30-day account transaction history timeline.
- **Manager Analytics Dashboard**: Executive KPIs (Fraud Rate, FP Rate, Cases Reviewed Today), 14-day trend charts, and CSV report exporter.
- **MLOps Model Registry**: Model version comparison, candidate promotion, and shadow deployment control.
- **Immutable Audit Trail**: Compliance-ready logging for all mutating analyst decisions and model releases.

---

## 🛠 Project Structure

```
.
├── backend/
│   ├── apps/api/                               # FastAPI Routers, Schemas, Dependencies & Middleware
│   ├── domain/                                 # Zero-dependency Core Domain Entities, Value Objects, Policies & Interfaces
│   ├── ml/                                     # Feature Definitions, Models (Strategy Pattern), Risk Engine, SHAP
│   ├── infrastructure/                         # SQLAlchemy ORM, Postgres Repositories, Redis Feature Store, EventBus
│   ├── services/                               # Application Services (Transaction, Scoring, FraudCase, Analytics)
│   └── scripts/seed_and_train.py               # Database Seed & Initial Model Training Script
├── frontend/                                   # Next.js 16 App Router UI Workspace
│   ├── src/app/analyst/                        # Analyst Fraud Review Queue & Detail Page
│   ├── src/app/manager/                        # Risk Manager Dashboard Page
│   └── src/app/ml-engineer/                    # MLOps Model Registry Page
├── tests/                                      # PyTest Suite (Unit, ML Data Leakage, Integration)
└── docker-compose.yml
```

---

## 🚀 Quick Start Guide

### 0. Configuration (required)

```bash
cp .env.example .env     # fill JWT_SECRET, INTERNAL_API_KEY, DEMO_PASSWORD, ...
python -c "import secrets; print(secrets.token_hex(32))"   # generate secrets
```

Datasets (IEEE-CIS, PaySim, ULB CreditCard) are **not** in the repo: download them from Kaggle into `data/raw/<name>/` and run `scripts/run_full_pipeline.py`. Small trained artifacts live in `backend/ml/artifacts/`.

### 1. Backend Setup & Run

```bash
# Initialize DB and seed 3 demo accounts (password = $DEMO_PASSWORD)
python backend/scripts/seed_and_train.py

# Run FastAPI Server
uvicorn backend.apps.api.main:app --reload --port 8000
```

FastAPI Documentation available at `http://localhost:8000/docs`.

### 2. Frontend Setup & Run

```bash
cd frontend
npm install
npm run dev
```

Next.js Application available at `http://localhost:3000`.

### 3. Run Automated Tests

```bash
python -m pytest tests/ -v
```

### Security notes
- Login verifies bcrypt hashes; no auto-provisioning. RBAC: only `ANALYST` can assign/review cases, only `ML_ENGINEER` can promote/rollback/shadow models.
- `NEXT_PUBLIC_DEMO_MODE=true` enables one-click role login for local demos only; never enable it on a public deployment.
- `staging`/`production` refuse to start without explicit `JWT_SECRET` and `INTERNAL_API_KEY`.

---

## 🛡 Business Rules Enforced
- **BR-01**: AI does NOT perform automated account locks; all legal actions require Analyst confirmation.
- **BR-02**: Risk Score Thresholds — LOW (< 30), MEDIUM (30-69), HIGH (≥ 70).
- **BR-03**: Override Policy — Amount > 10,000,000 VND AND new device flag = True forces HIGH risk level.
- **BR-04**: Fraud cases automatically generated for HIGH risk transactions only.
- **BR-05**: Strict Idempotency — Duplicate `transaction_id` requests return HTTP 409 Conflict.
- **BR-10**: Immutable Audit Logs — Audit trail entries cannot be updated or deleted.
