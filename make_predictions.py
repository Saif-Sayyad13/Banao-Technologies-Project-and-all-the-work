"""Write predictions.csv for test_unlabelled.csv in the sample_submission format. Needs ./data/."""
import pandas as pd
from kestrel.data import load_test
from kestrel.service import route

te = load_test()
rows = []
for r in te.itertuples():
    o = route(dict(request_text=r.request_text, channel=r.channel, warranty_status=r.warranty_status, product_family=r.product_family))
    rows.append((r.request_id, o["team"], o["confidence"], o["needs_triage"]))
full = pd.DataFrame(rows, columns=["request_id", "team", "confidence", "needs_triage"])
full[["request_id", "team"]].to_csv("predictions.csv", index=False)       # exactly the required shape
full.to_csv("docs/predictions_with_confidence.csv", index=False)           # extra: for the triage desk
print(full.team.value_counts(), "\ntriage share:", full.needs_triage.mean().round(3), "rows:", len(full))
