"""Honest evaluation. Run: python evaluate.py   (needs ./data/, writes docs/metrics.json)

Validation is by TIME, never random: train on the past, score on the next quarter,
because the real job is routing requests that arrive after the training data ends.
Target = team that actually closed the request (final_team), NOT the bot's label.
"""
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from kestrel.data import load_train
from kestrel.model import build
from kestrel.text import TEAMS

warnings.filterwarnings("ignore")
d = load_train()
d["t"] = pd.to_datetime(d.created_at_ist)
out = {}

# ---- 1. is the bot label a good target? ------------------------------------
out["bot_vs_final_agreement_all_train"] = float((d.bot == d.y).mean())
out["bot_vs_final_by_quarter"] = {str(k): round(float(v), 4) for k, v in
    d.groupby(d.t.dt.to_period("Q")).apply(lambda x: (x.bot == x.y).mean()).items()}
out["bot_first_team_equals_label"] = float((d.first_team.replace({"Installations": "Installs & Demo", "Consumables": "Filters & Consumables"}) == d.bot).mean())

# ---- 2. rolling-origin validation (3 quarters, always train on everything earlier)
folds = [("2025-10-01", "2026-01-01"), ("2026-01-01", "2026-04-01"), ("2026-04-01", "2026-07-01")]
res, rows = [], []
for lo, hi in folds:
    a, b = d[d.t < lo], d[(d.t >= lo) & (d.t < hi)]
    m = build().fit(a.doc, a.y)
    pr = m.predict_proba(b.doc)
    p = m.classes_[pr.argmax(1)]
    r = dict(test_from=lo, n_train=len(a), n_test=len(b),
             acc=accuracy_score(b.y, p), macro_f1=f1_score(b.y, p, average="macro"),
             bot_acc=accuracy_score(b.y, b.bot))
    res.append(r)
    rows.append(pd.DataFrame(dict(y=b.y.values, p=p, conf=pr.max(1), bot=b.bot.values, transfers=b.transfers.values,
                                  text=b.request_text.values, first=b.first_team.values)))
cv = pd.DataFrame(res).round(4)
out["rolling_folds"] = cv.to_dict("records")
P = pd.concat(rows)
out["pooled"] = dict(n=len(P), acc=float((P.y == P.p).mean()), macro_f1=float(f1_score(P.y, P.p, average="macro")),
                     bot_acc=float((P.y == P.bot).mean()))
# binomial 95% interval on pooled accuracy
n, a_ = len(P), (P.y == P.p).mean()
out["pooled"]["acc_ci95"] = [float(a_ - 1.96 * np.sqrt(a_ * (1 - a_) / n)), float(a_ + 1.96 * np.sqrt(a_ * (1 - a_) / n))]
out["per_team_f1"] = {t: round(float(f1_score(P.y == t, P.p == t)), 3) for t in TEAMS}
out["confusion"] = pd.DataFrame(confusion_matrix(P.y, P.p, labels=TEAMS), index=TEAMS, columns=TEAMS).to_dict()

# ---- 3. confidence -> how much can be automated -----------------------------
tbl = []
for th in [0.0, 0.4, 0.5, 0.6, 0.7, 0.8]:
    s = P.conf >= th
    tbl.append(dict(threshold=th, automated_share=round(float(s.mean()), 3), accuracy_on_automated=round(float((P.y[s] == P.p[s]).mean()), 4),
                    bot_accuracy_same_rows=round(float((P.y[s] == P.bot[s]).mean()), 4)))
out["confidence_table"] = tbl

# ---- 4. what kind of request does it get wrong? ------------------------------
P["vague"] = P.conf < 0.5
out["low_confidence_share"] = float(P.vague.mean())
out["acc_when_low_conf"] = float((P.y[P.vague] == P.p[P.vague]).mean())
out["acc_when_high_conf"] = float((P.y[~P.vague] == P.p[~P.vague]).mean())
out["share_of_all_errors_from_low_conf"] = float(((P.y != P.p) & P.vague).sum() / (P.y != P.p).sum())
# is anything but the text useful for vague requests? (answer: no)
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import cross_val_predict
a_all = d[d.t < "2026-04-01"]
mm = build().fit(a_all.doc, a_all.y)
oof = cross_val_predict(build(), d.doc, d.y, cv=5, method="predict_proba")
low = oof.max(1) < 0.5
X = pd.get_dummies(d.loc[low, ["channel", "warranty_status", "product_family"]]).astype(int)
X["hour"] = d.t[low].dt.hour.values
meta = cross_val_predict(HistGradientBoostingClassifier(max_depth=3, max_iter=80), X, d.y[low], cv=5)
out["vague_rows_in_train"] = int(low.sum())
out["vague_meta_only_acc"] = float((meta == d.y[low]).mean())
out["vague_chance_acc"] = 1 / 7
out["bot_acc_on_vague_rows"] = float((d.bot[low] == d.y[low]).mean())

# ---- 5. experiments (what I tried; scored on the newest quarter) --------------
a, b = d[d.t < "2026-04-01"], d[d.t >= "2026-04-01"]
ex = {}
def sc(name, m, ytr, Xtr=None, Xte=None):
    m.fit(a.doc if Xtr is None else Xtr, ytr); p = m.predict(b.doc if Xte is None else Xte)
    ex[name] = dict(acc_vs_final=round(float(accuracy_score(b.y, p)), 4), macro_f1=round(float(f1_score(b.y, p, average="macro")), 4))
sc("A. train on BOT LABELS (what the client asked), score vs where it was actually resolved", build(), a.bot)
sc("B. train on final_team (chosen), TF-IDF words+chars + logistic regression", build(), a.y)
sc("C. same as B, words only", make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2), LogisticRegression(C=10, max_iter=3000)), a.y)
sc("D. linear SVM", make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2), LinearSVC(C=1)), a.y)
sc("E. Complement Naive Bayes", make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2), ComplementNB(alpha=0.3)), a.y)
ex["F. the old bot itself, scored vs where it was actually resolved"] = dict(acc_vs_final=round(float(accuracy_score(b.y, b.bot)), 4), macro_f1=round(float(f1_score(b.y, b.bot, average="macro")), 4))
# model A scored the way the client asked (against the bot's own labels)
mA = build().fit(a.doc, a.bot); pA = mA.predict(b.doc)
ex["A (scored the way Ritu asked: match bot labels)"] = dict(acc_vs_bot_label=round(float(accuracy_score(b.bot, pA)), 4))
out["experiments"] = ex

# ---- 6. rupees ---------------------------------------------------------------
mis = d[d.first_team.replace({"Installations": "Installs & Demo", "Consumables": "Filters & Consumables"}) != d.y]
tr_per_mis = float(mis.transfers.mean())
months = (d.t.max() - d.t.min()).days / 30.4
vol_year = len(d) / months * 12
bot_mis_rate = float(len(mis) / len(d))
def cost(mis_rate): return vol_year * mis_rate * (tr_per_mis * 305 + 260)
th = 0.6
s = P.conf >= th
mod_mis_auto = float((P.y[s] != P.p[s]).mean())
auto = float(s.mean())
# model: confident share automated; the rest goes to a one-person triage desk (no transfer cost, assumed 1 touch)
m_cost_all = cost(float((P.y != P.p).mean()))
m_cost_auto = cost(mod_mis_auto * auto)
out["money"] = dict(requests_per_year=round(vol_year), bot_misroute_rate=round(bot_mis_rate, 4), transfers_per_misroute=round(tr_per_mis, 2),
    cost_per_misroute_rs=round(tr_per_mis * 305 + 260), bot_misroute_cost_per_year=round(cost(bot_mis_rate)),
    model_misroute_rate_all=round(float((P.y != P.p).mean()), 4), model_cost_per_year_route_everything=round(m_cost_all),
    triage_threshold=th, automated_share=round(auto, 3), model_misroute_rate_on_automated=round(mod_mis_auto, 4),
    model_cost_per_year_with_triage=round(m_cost_auto), triage_requests_per_year=round(vol_year * (1 - auto)),
    triage_cost_assumption_rs_per_request=260,
    triage_desk_cost_per_year=round(vol_year * (1 - auto) * 260),
    bot_licence_rs=320000)
mo = out["money"]
mo["bot_total_per_year"] = mo["bot_misroute_cost_per_year"] + mo["bot_licence_rs"]
mo["option_A_route_everything_total"] = mo["model_cost_per_year_route_everything"]
mo["option_A_saving_per_year"] = mo["bot_total_per_year"] - mo["option_A_route_everything_total"]
mo["option_B_triage_total"] = mo["model_cost_per_year_with_triage"] + mo["triage_desk_cost_per_year"]
mo["option_B_saving_per_year"] = mo["bot_total_per_year"] - mo["option_B_triage_total"]
mo["triage_break_even_rs_per_request"] = round((mo["model_cost_per_year_route_everything"] - mo["model_cost_per_year_with_triage"]) / mo["triage_requests_per_year"])
# ---- 7. busiest teams (use real resolution, not bot label) -------------------
tc = d.y.value_counts(normalize=True).round(3)
bc = d.bot.value_counts(normalize=True).round(3)
out["team_share_actual_vs_bot"] = {t: dict(actual=float(tc.get(t, 0)), bot=float(bc.get(t, 0))) for t in TEAMS}
out["data_quality"] = dict(mojibake_rows=int(d.request_text.str.contains("Ã|â€").sum()), legacy_zoho_rows=int((d.source == "legacy_zoho").sum()),
    dup_text_rows=int(d.request_text.duplicated().sum()), n_train=len(d))
json.dump(out, open("docs/metrics.json", "w"), indent=1, default=float)
P.to_pickle("/tmp/P.pkl")
print(json.dumps(out, indent=1, default=float))
