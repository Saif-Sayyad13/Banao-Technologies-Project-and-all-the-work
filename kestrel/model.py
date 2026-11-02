from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union


def build(C: float = 10.0):
    """TF-IDF (words 1-2 + character 3-5 grams) -> logistic regression.
    Runs on a CPU in milliseconds. No API, no per-request cost."""
    feats = make_union(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=3),
    )
    return make_pipeline(feats, LogisticRegression(C=C, max_iter=3000))
