# UPIShield — Behavioral Transaction Anomaly Detection & Risk Scoring

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_Cloud-FF4B4B?logo=streamlit&logoColor=white)](https://upishield-oejrj772uqp5hvmwbjsmhv.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

### [🚀 Open the live UPIShield dashboard](https://upishield-oejrj772uqp5hvmwbjsmhv.streamlit.app/)

Try an explainable transaction-risk assessment directly in the Streamlit Community Cloud application.

> **Deployment note:** The public demo runs independently of the optional EC2 deployment. Streamlit Community Cloud may briefly wake the app after a period of inactivity.

## Overview

UPIShield is an educational fintech ML system that asks: “How unusual is this transaction compared with the user's prior behavior?” It combines transparent rules, an unsupervised Isolation Forest, and a supervised Random Forest into an explainable 0–100 risk score.

### Why this project stands out

- **Behavior-aware:** compares each payment with the sender's prior devices, locations, receivers, timing, and spending patterns
- **Leakage-conscious:** builds historical features from earlier transactions only and evaluates on a chronological holdout
- **Explainable:** combines model probability, anomaly detection, and transparent rules into a reasoned 0–100 score
- **Deployment-ready:** includes a FastAPI scoring service, Streamlit dashboard, packaged model artifact, tests, and cloud configuration

> **Dataset disclaimer:** This project uses synthetic UPI-like transaction data generated solely for educational and portfolio purposes. It contains no real NPCI, PhonePe, Google Pay, Paytm, bank, or customer transaction data.

## Key features

- Reproducible 50,000-row simulator (seed 42), behavioral profiles, overlapping fraud/legitimate behavior
- Prior-only user, device, receiver, location, and transaction-velocity features
- Chronological 70/15/15 train/validation/test split; training-only preprocessing
- Rule baseline, Isolation Forest, Logistic Regression/Random Forest comparison, hybrid scoring
- Deterministic explanations, FastAPI, SQLite demo store, Streamlit, PyTest, Render-ready paths

## Architecture

```mermaid
flowchart LR
  A[UPI-like transaction] --> B[Validation] --> C[Prior-only behavioral features]
  C --> D[Rule engine]
  C --> E[Isolation Forest]
  C --> F[Fraud model]
  D --> G[Hybrid risk score]
  E --> G
  F --> G
  G --> H[FastAPI] --> I[Streamlit dashboard]
```

## Data and feature engineering

The simulator creates users with typical amounts, hours, cities, devices, receivers, and categories, then injects probabilistic anomaly scenarios with legitimate overlap. Historical averages, entity novelty, location changes, time gaps, and rolling 10-minute/1-hour/24-hour velocity use only earlier rows. Labels and scenario names are explicitly excluded from model inputs. Cold-start values use neutral defaults.

## Models and temporal strategy

The earliest 70% trains models, the next 15% selects models and thresholds, and the final 15% is evaluated once. Random splitting would let later behavior inform earlier predictions. Isolation Forest is fitted without labels. Logistic Regression and Random Forest are compared by validation PR-AUC; Random Forest was selected. The hybrid weights are 50% supervised probability, 30% anomaly score, and 20% rule score.

Accuracy is misleading at a 2.17% fraud rate because predicting every row as legitimate looks accurate. Precision measures alert quality, recall measures fraud captured, F1 balances them, PR-AUC assesses ranking under imbalance, ROC-AUC assesses overall ranking, and false-positive rate measures legitimate transactions incorrectly flagged.

## Test-set results

| System | Precision | Recall | F1 | PR-AUC | ROC-AUC | FPR |
|---|---:|---:|---:|---:|---:|---:|
| Rule baseline | 0.1000 | 0.1757 | 0.1275 | 0.1146 | 0.7985 | 0.0318 |
| Isolation Forest | 0.0397 | 0.4595 | 0.0731 | 0.0325 | 0.6633 | 0.2238 |
| Random Forest | 0.2231 | 0.3649 | 0.2769 | 0.2267 | 0.7874 | 0.0256 |
| Hybrid engine | 0.2738 | 0.3108 | 0.2911 | 0.2150 | 0.7763 | 0.0166 |

These values come from `python scripts/run_pipeline.py` with seed 42. Full confusion matrices and thresholds are in `reports/metrics.json`.

## Project structure

`src/` contains generation, validation, features, risk logic, modeling, and SQLite code; `scripts/` contains executable workflows; `api/` and `dashboard/` serve the demo; `tests/` verifies correctness; `docs/`, `notebooks/`, `reports/`, and `artifacts/` contain supporting material and outputs.

## Installation and use (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_pipeline.py
pytest -q
```

Run the API with `uvicorn api.main:app --reload` and open `http://127.0.0.1:8000/docs`. Run the dashboard from the repository root with:

```powershell
$env:PYTHONPATH = "."
streamlit run dashboard/app.py
```

On Linux/macOS, use `PYTHONPATH=. streamlit run dashboard/app.py`.

## Optional AWS EC2 deployment

The dashboard can also be self-hosted on an Ubuntu EC2 instance. Use Python 3.12 because the pinned scientific-Python dependencies are not compatible with Ubuntu 26.04's default Python 3.14.

```bash
git clone https://github.com/akashsmb10/UPIShield.git
cd UPIShield

# Install/use Python 3.12, then create the environment.
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt

PYTHONPATH=. streamlit run dashboard/app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true
```

Allow inbound TCP port `8501` in the instance security group. For a production-style deployment, place Nginx in front of Streamlit on ports 80/443, configure TLS, run Streamlit with `systemd`, and associate an Elastic IP or domain.

### Streamlit Community Cloud (standalone)

The [public dashboard](https://upishield-oejrj772uqp5hvmwbjsmhv.streamlit.app/) loads the packaged model and committed sample history directly, so it does not require a separately hosted API. To redeploy it, select repository `akashsmb10/UPIShield`, branch `main`, and entrypoint `dashboard/app.py`. No secrets or environment variables are required.

## Render deployment

Create two Web Services from the same repository:

- API build: `pip install -r requirements.txt`; start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Dashboard build: `pip install -r requirements.txt`; start: `streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port $PORT`
- Set dashboard environment variable `UPISHIELD_API_URL=<deployed FastAPI URL>`.

Alternatively, deploy the included `render.yaml` Blueprint and set `UPISHIELD_API_URL` to the created API service URL.

Artifacts required for inference are committed/deployed with the repository. SQLite is a local/demo read source, not durable cloud storage.

## Limitations and future work

This is an educational system trained on synthetic data, not production fraud infrastructure. Rules and population defaults are simplified; there is no real financial integration, streaming, drift monitoring, or durable Render SQLite. Future work could add approved real data, Kafka, an online feature store, drift monitoring, graph fraud analysis, and GNN research; none is currently implemented.
