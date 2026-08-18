import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score, PrecisionRecallDisplay, ConfusionMatrixDisplay
from src.config import *
from src.features import build_features, model_matrix, temporal_split
from src.risk_engine import rule_scores, combine_scores
from src.modeling import choose_threshold, metrics
from src.database import prepare_database
from src.utils import save_json
from scripts.generate_dataset import main as generate

def main():
    ensure_dirs(); raw = generate(); feat = build_features(raw); train, val, test = temporal_split(feat)
    Xtr,Xv,Xt = map(model_matrix,(train,val,test)); yt,yv,ytest = train.is_fraud,val.is_fraud,test.is_fraud
    scaler = StandardScaler().fit(Xtr); iso = IsolationForest(n_estimators=120, contamination=.025, random_state=SEED, n_jobs=1).fit(scaler.transform(Xtr))
    raw_v=-iso.score_samples(scaler.transform(Xv)); lo,hi=np.percentile(raw_v,[2,98]); anomaly=lambda x: np.clip((x-lo)/(hi-lo)*100,0,100)
    av=anomaly(raw_v); at=anomaly(-iso.score_samples(scaler.transform(Xt))); ath=choose_threshold(yv,av)
    candidates={"logistic_regression":make_pipeline(StandardScaler(),LogisticRegression(class_weight="balanced",max_iter=500,random_state=SEED)),
                "random_forest":RandomForestClassifier(n_estimators=160,max_depth=12,min_samples_leaf=3,class_weight="balanced",n_jobs=1,random_state=SEED)}
    best_name,best_model,best_ap=None,None,-1
    for name,model in candidates.items():
        model.fit(Xtr,yt); score=model.predict_proba(Xv)[:,1]; ap=average_precision_score(yv,score)
        if ap>best_ap: best_name,best_model,best_ap=name,model,ap
    pv=best_model.predict_proba(Xv)[:,1]; pt=best_model.predict_proba(Xt)[:,1]; sth=choose_threshold(yv,pv)
    rv,rt=rule_scores(val),rule_scores(test); rth=choose_threshold(yv,rv)
    hv=combine_scores(pv,av,rv); ht=combine_scores(pt,at,rt); hth=choose_threshold(yv,hv)
    results={"dataset":{"transactions":len(raw),"users":int(raw.user_id.nunique()),"fraud_count":int(raw.is_fraud.sum()),"fraud_percentage":round(raw.is_fraud.mean()*100,3),"train_size":len(train),"validation_size":len(val),"test_size":len(test)},
      "rule_baseline":metrics(ytest,rt,rth),"isolation_forest":metrics(ytest,at,ath),"selected_supervised_model":best_name,
      "supervised":metrics(ytest,pt,sth),"hybrid":metrics(ytest,ht,hth),"risk_thresholds":{"medium":round(hth*.55,2),"high":round(hth,2)}}
    joblib.dump({"model":best_model,"isolation_forest":iso,"scaler":scaler,"anomaly_low":lo,"anomaly_high":hi,"metadata":results},ARTIFACT_DIR/"risk_bundle.joblib")
    scored=test[["transaction_id","timestamp","user_id","amount","is_fraud"]].copy(); scored["risk_score"]=ht
    prepare_database(raw,scored); save_json(results,REPORT_DIR/"metrics.json")
    PrecisionRecallDisplay.from_predictions(ytest,ht); plt.tight_layout(); plt.savefig(FIGURE_DIR/"hybrid_precision_recall.png"); plt.close()
    ConfusionMatrixDisplay.from_predictions(ytest,ht>=hth); plt.tight_layout(); plt.savefig(FIGURE_DIR/"hybrid_confusion_matrix.png"); plt.close()
    plt.hist(ht[ytest.to_numpy()==0],bins=40,alpha=.6,label="legitimate"); plt.hist(ht[ytest.to_numpy()==1],bins=40,alpha=.6,label="fraud"); plt.legend(); plt.xlabel("Risk score"); plt.tight_layout(); plt.savefig(FIGURE_DIR/"risk_score_distribution.png"); plt.close()
    plt.scatter(test.amount,ht,c=ytest,cmap="coolwarm",s=5,alpha=.35); plt.xscale("log"); plt.xlabel("Amount (log scale)"); plt.ylabel("Risk score"); plt.tight_layout(); plt.savefig(FIGURE_DIR/"amount_vs_risk.png"); plt.close()
    if hasattr(best_model,"feature_importances_"):
        imp=pd.Series(best_model.feature_importances_,index=MODEL_FEATURES).nlargest(12).sort_values(); imp.plot.barh(); plt.tight_layout(); plt.savefig(FIGURE_DIR/"feature_importance.png"); plt.close()
    print(results); return results

if __name__ == "__main__": main()
