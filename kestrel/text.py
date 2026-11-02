"""Text clean-up shared by training and serving.

Handles the things the data pack warned about:
  * mojibake from the Zoho migration (e.g. 'Ã©' for 'é', 'â€¦' for '…')
  * accents / odd punctuation
  * request / order numbers (SR12345, KO2601234) that carry no routing signal
"""
import re
import unicodedata

# the two teams renamed on 15 Jan 2026 -> always train and predict on the NEW names
RENAMES = {"Installations": "Installs & Demo", "Consumables": "Filters & Consumables"}
TEAMS = [
    "Billing", "Filters & Consumables", "Installs & Demo", "Product Advice",
    "Repairs", "Returns & Replacement", "Warranty Claims",
]


def clean(text) -> str:
    t = "" if text is None else str(text)
    for _ in range(2):  # undo UTF-8 read as cp1252 (can be double-encoded)
        try:
            t = t.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[\u2026\u2013\u2014]", " ", t)
    t = re.sub(r"\b(sr|ko)\d+\b", " ", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def to_doc(text, channel, warranty_status, product_family) -> str:
    """One string per request: cleaned text + three metadata tokens."""
    pf = str(product_family).replace(" ", "_")
    return f"{clean(text)} __ch_{channel} __wr_{warranty_status} __pf_{pf}"
