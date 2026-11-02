import glob
import os
import pandas as pd
from .text import RENAMES, to_doc

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _find(name):
    hits = glob.glob(os.path.join(DATA, f"*{name}*"))
    if not hits:
        raise SystemExit(f"Put the client files in ./data/ (missing: {name}). See README.")
    return hits[0]


def load_train():
    tr = pd.read_csv(_find("train.csv"))
    rl = pd.read_csv(_find("resolution_log"))
    d = tr.merge(rl, on="request_id", validate="1:1")
    d["bot"] = d.team_label.replace(RENAMES)            # what the old bot said
    d["y"] = d.final_team.replace(RENAMES)              # where it was actually resolved
    d["doc"] = [to_doc(*r) for r in zip(d.request_text, d.channel, d.warranty_status, d.product_family)]
    return d


def load_test():
    te = pd.read_csv(_find("test_unlabelled"))
    te["doc"] = [to_doc(*r) for r in zip(te.request_text, te.channel, te.warranty_status, te.product_family)]
    return te
