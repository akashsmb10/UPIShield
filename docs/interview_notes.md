# Interview notes

1. **Problem:** rank a payment's risk relative to that user's earlier behavior.
2. **Why behavioral:** a globally ordinary payment can be unusual for one user.
3. **Anomaly detection:** identify observations unlike learned normal patterns.
4. **Supervised vs unsupervised:** supervised models learn labels; unsupervised models learn structure without them.
5. **Isolation Forest intuition:** random splits isolate rare, unusual points in fewer steps.
6. **Why it works:** anomalies tend to occupy sparse, easier-to-isolate regions.
7. **Velocity:** counts and amounts over recent time windows.
8. **Behavioral features:** amount ratios, novelty, timing, location, and velocity compared with prior history.
9. **Chronological split:** reproduces predicting the future from the past.
10. **Future leakage:** using activity that had not occurred when a prediction was made.
11. **Target leakage:** letting labels or label-derived information enter model inputs.
12. **Accuracy:** misleading when the majority class dominates.
13. **Precision:** fraction of alerts that are truly fraud.
14. **Recall:** fraction of fraud captured.
15. **F1:** harmonic balance of precision and recall.
16. **PR-AUC:** ranking quality focused on the positive class.
17. **FPR:** fraction of legitimate transactions incorrectly flagged.
18. **Imbalance:** fraud is rare, so thresholds and class weighting matter.
19. **Rules:** transparent domain signals provide an explainable baseline.
20. **Hybrid:** rules add transparency, anomaly detection catches novelty, supervised ML learns labeled patterns.
21. **Score:** 50% probability + 30% anomaly + 20% rules, clipped to 0–100.
22. **New users:** neutral numeric history and novelty indicators.
23. **New devices:** prior device count zero triggers a supported reason.
24. **New receivers:** prior user-receiver count zero triggers a supported reason.
25. **API inference:** validate, retrieve earlier history, engineer features, run three scorers, combine, explain.
26. **Dashboard:** sends JSON to the configurable FastAPI URL and renders returned risk.
27. **Render:** two services share one repository; an environment variable connects them.
28. **Limitations:** synthetic data, batch history, simplified rules, no production controls.
29. **Kafka later:** publish transactions to a stream and score consumers near-real-time.
30. **Graphs later:** model user-device-receiver relationships to detect coordinated rings.

## 60-second explanation

UPIShield is a leakage-safe behavioral fraud prototype. I generated 50,000 synthetic UPI-like payments with realistic user profiles and overlapping anomalies. For each transaction I calculate only prior-history features—amount deviation, new devices and receivers, location changes, and transaction velocity. I chronologically split the data, combine rules, an unsupervised Isolation Forest, and a validation-selected Random Forest, and expose a risk score with deterministic reasons through FastAPI and Streamlit. I evaluate with PR-AUC, precision, recall, F1, ROC-AUC, and false-positive rate rather than accuracy.

## 2-minute explanation

The key design decision is point-in-time correctness. Features are created row-by-row before the current transaction is added to history, so future transactions cannot leak backward. The first 70% of time trains models, 15% validates choices and thresholds, and 15% is held for final evaluation. Isolation Forest supplies a label-free novelty view, Random Forest learns known fraud patterns, and rules retain domain transparency. Their fixed weighted score produces LOW/MEDIUM/HIGH risk plus reasons grounded in actual feature values. The deployment is intentionally simple: artifacts, FastAPI, a SQLite demo store, and a Streamlit client configured by `UPISHIELD_API_URL`.

## Ten likely questions

1. **Why not accuracy?** A majority-only classifier would look strong while catching nothing.
2. **How did you prevent leakage?** Prior-only state, shifted semantics, label exclusion, temporal splitting, and tests.
3. **Why Isolation Forest?** It is interpretable at a high level, fast, and needs no fraud labels.
4. **Why Random Forest?** It won validation PR-AUC and captures nonlinear interactions.
5. **How are thresholds chosen?** Maximum validation F1, never test labels.
6. **Why is anomaly recall high but precision low?** Unusual legitimate behavior is common and anomalies are not identical to fraud.
7. **How do cold starts work?** Neutral defaults plus novelty flags.
8. **Are explanations causal?** No; they report triggered behavioral evidence.
9. **What would production require?** Streaming state, security, monitoring, fairness, human review, and approved data.
10. **Biggest limitation?** Synthetic distributions cannot validate real-world fraud performance.
