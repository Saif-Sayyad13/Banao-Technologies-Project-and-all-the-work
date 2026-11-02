"""Loads the saved model and explains each routing decision in plain words."""
import json
import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from .text import to_doc, TEAMS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = joblib.load(os.path.join(HERE, "model", "model.joblib"))
CFG = json.load(open(os.path.join(HERE, "model", "config.json")))
THRESHOLD = CFG["triage_threshold"]

_union = MODEL.steps[0][1]
_clf = MODEL.steps[-1][1]
_names = _union.get_feature_names_out()
_is_word = np.array([n.startswith("tfidfvectorizer-1__") for n in _names])
_pretty = np.array([n.split("__", 1)[1] if "__" in n else n for n in _names], dtype=object)

_STOP = set(ENGLISH_STOP_WORDS) | {"hi", "hello", "pls", "please", "sir", "team", "thanks", "asap", "help", "namaste", "good", "morning", "urgent", "kindly", "resolve", "call", "back"}


def _meaningful(p: str) -> bool:
    toks = p.split()
    return "__" not in p and any(t not in _STOP for t in toks) and not (toks[0] in _STOP and toks[-1] in _STOP)


def route(record: dict) -> dict:
    for k in ("request_text",):
        if not str(record.get(k, "")).strip():
            raise ValueError("request_text is required")
    doc = to_doc(record.get("request_text", ""), record.get("channel", "chat"),
                 record.get("warranty_status", "in_warranty"), record.get("product_family", ""))
    X = _union.transform([doc])
    proba = _clf.predict_proba(X)[0]
    order = np.argsort(-proba)
    k = order[0]
    team = str(_clf.classes_[k])
    conf = float(proba[k])

    # reasons: words/phrases in THIS request that pushed hardest towards the chosen team
    contrib = X.multiply(_clf.coef_[k]).tocoo()
    items = sorted(((v, c) for c, v in zip(contrib.col, contrib.data) if v > 0 and _is_word[c]), reverse=True)
    phrases, seen = [], set()
    for v, c in items:
        p = str(_pretty[c])
        toks = set(p.split())
        if not _meaningful(p) or any(toks & s_ for s_ in seen):
            continue
        seen.add(frozenset(toks))
        phrases.append(p)
        if len(phrases) == 3:
            break

    needs_triage = conf < THRESHOLD
    if needs_triage:
        reasons = ["The message does not say clearly what the problem is (e.g. 'please call me about my product'), so the data cannot tell which team handles it.",
                   "Send to the triage desk / call the customer back to ask one question, instead of guessing."]
        if phrases:
            reasons.append("Weak hints only: " + ", ".join(f'"{p}"' for p in phrases) + ".")
    else:
        reasons = [f'Wording points to {team}: ' + ", ".join(f'"{p}"' for p in phrases) + "." if phrases else f"Wording matches past {team} requests."]
        reasons.append(f"Similar past requests were most often closed by {team} (model confidence {conf:.0%}).")
    return {
        "team": team,
        "confidence": round(conf, 3),
        "needs_triage": needs_triage,
        "action": "Send to triage desk (ask the customer one question)" if needs_triage else f"Auto-route to {team}",
        "second_choice": str(_clf.classes_[order[1]]),
        "reasons": reasons,
        "model": "tfidf+logreg v1 (no external API)",
    }
