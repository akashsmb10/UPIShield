import numpy as np
from sklearn.metrics import precision_recall_curve, precision_score, recall_score, f1_score, average_precision_score, roc_auc_score, confusion_matrix

def choose_threshold(y, scores):
    p, r, t = precision_recall_curve(y, scores)
    f = 2*p*r/(p+r+1e-12)
    return float(t[np.argmax(f[:-1])]) if len(t) else .5

def metrics(y, scores, threshold):
    pred = np.asarray(scores) >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {"threshold": round(float(threshold), 5), "precision": round(float(precision_score(y,pred,zero_division=0)),5),
        "recall": round(float(recall_score(y,pred,zero_division=0)),5), "f1": round(float(f1_score(y,pred,zero_division=0)),5),
        "pr_auc": round(float(average_precision_score(y,scores)),5), "roc_auc": round(float(roc_auc_score(y,scores)),5),
        "false_positive_rate": round(float(fp/(fp+tn)),5), "confusion_matrix": [[int(tn),int(fp)],[int(fn),int(tp)]]}
