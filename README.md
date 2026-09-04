# LedgerOps

LedgerOps is an institutional digital-asset operations console for reconciling synthetic positions across an internal ledger, exchanges, custodians, and on-chain wallets. It surfaces explainable operational breaks and provides an auditable analyst workflow.

> All data is synthetic. This project uses no real client, trading, exchange, custodian, or wallet data and is not affiliated with any exchange, custodian, Ripple, or financial institution.

## Why deterministic reconciliation

Financial correctness cannot depend on probabilistic output. LedgerOps normalizes source feeds into a canonical model, compares them with explicit tolerances, and stores the records used as evidence. Severity and concentration warnings are transparent rules. AI is deliberately limited to an optional, templated explanation layer and never changes balances, matching, calculations, or severity.

## Architecture

```
Next.js + TypeScript dashboard  ->  FastAPI JSON API  -> SQLite / SQLAlchemy
                                      |-- source adapters
                                      |-- deterministic reconciliation engine
                                      |-- seeded synthetic data generator
```

The SQLAlchemy data layer uses ordinary relational models, so moving from SQLite to Postgres only requires a connection-string change and migration tooling.

## Quick start

Open two terminals from the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m backend.seed
.venv/bin/uvicorn backend.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The UI proxies `/api/*` to FastAPI on port 8000.

## 90-second demo

1. Open **Overview** to see NAV, reconciliation health, and concentration alerts.
2. Open **Exceptions**, select the critical USDC settlement break, and inspect deterministic evidence.
3. Assign the exception, change its status, or add a comment.
4. Open **Activity** to see the append-only audit events created by the workflow.
5. Review **Settings** to see the tolerances and risk thresholds that drive matching and alerts.

## Screenshots

Add screenshots here after running the local demo:

- `docs/overview.png`
- `docs/exception-detail.png`
- `docs/activity.png`

## Testing

```bash
.venv/bin/pytest backend/tests -q
cd frontend && npm run build
```

## Intentional demo breaks

The seed contains a missing USDC settlement, BTC quantity mismatch, duplicate transaction, stale wallet snapshot, price mismatch, timing difference, missing exchange withdrawal, and a high Exchange A concentration warning. It also includes hundreds of matched synthetic records and a within-tolerance match.
