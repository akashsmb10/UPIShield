# Model card

## Purpose and intended use

UPIShield demonstrates behavioral transaction risk scoring for education, interviews, and portfolio review. It may support local experiments; it must not approve, decline, accuse, or investigate real customers.

## Data

All 50,000 UPI-like transactions are synthetic (seed 42); no real company, bank, or customer data is present. Fraud scenarios deliberately overlap legitimate behavior. Potential simulator bias means results do not establish real-world performance.

## Models and features

The system uses transparent rules, Isolation Forest, and a validation-selected Random Forest. Inputs cover amount/time, prior user statistics, device/receiver novelty, location change, and rolling velocity. IDs, `is_fraud`, and `fraud_scenario` are excluded. Isolation Forest fitting uses no labels.

## Evaluation

Rows are split chronologically 70/15/15. Preprocessing fits on training only; validation selects algorithms and thresholds; test is final evaluation. Metrics include precision, recall, F1, PR-AUC, ROC-AUC, FPR, and confusion matrices. Current thresholds and executed results are in `reports/metrics.json`.

## Risks, ethics, and limitations

False positives can inconvenience or unfairly burden users; false negatives can miss loss. Synthetic behavioral profiles may underrepresent groups and changing habits. Explanations describe feature triggers, not guilt. A real deployment requires consent, security, calibrated costs, fairness testing, human review, drift monitoring, appeal processes, and approved real data.
