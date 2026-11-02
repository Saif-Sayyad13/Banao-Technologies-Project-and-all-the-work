"""Train on ALL labelled history (target = final_team) and save model/model.joblib.
Needs ./data/. Run: python train.py"""
import json
import joblib
from kestrel.data import load_train
from kestrel.model import build

d = load_train()
m = build().fit(d.doc, d.y)
joblib.dump(m, "model/model.joblib", compress=3)
json.dump({"triage_threshold": 0.6, "n_train": len(d), "classes": list(m.classes_)}, open("model/config.json", "w"))
print("saved model on", len(d), "rows; classes:", list(m.classes_))
