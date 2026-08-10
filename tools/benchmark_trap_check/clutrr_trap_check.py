"""
Benchmark trap-check sweep: CLUTRR (facebookresearch/clutrr, HF CLUTRR/v1,
split gen_train23_test2to10).

MEASUREMENT ONLY -- not an inference pipeline. Answers the "cheap decisive
test" from notes/research_extraction_foundation_decisive_benchmark_2026-08-10.md:
does CLUTRR's non-triviality-given-structure guarantee survive an empirical
ENDPOINT-ONLY shortcut probe (predict from first+last relation only, drop the
interior chain), and does that shortcut's edge over majority DEGRADE as chain
length k grows (real composition needed) or stay FLAT/grow (a WIQA-style leak)?

Baselines computed (ASCII-only, no unicode):
  1. MAJORITY       -- mode(target_text) on TRAIN, applied everywhere.
  2. CONTENT/BoW     -- TF-IDF(story text) -> multinomial logistic regression,
                        fit on TRAIN, evaluated on VAL/TEST. Tests whether raw
                        surface text (not gold structure) leaks the answer.
  3. BAG-OF-RELATIONS -- lookup table keyed by the UNORDERED multiset of gold
                        edge_types (sorted tuple) -> majority target_text on
                        TRAIN. No chain order, no composition. Tests "does the
                        unordered SET of extracted relations solve it" (the
                        WIQA-style structure-is-the-answer trap).
  4. ENDPOINT-ONLY   -- lookup table keyed by (first_edge_type, last_edge_type)
                        -> majority target_text on TRAIN. Drops every interior
                        link. This is the CLUTRR-analog of WIQA's polarity-echo
                        probe -- the single most important number in this test.
  5. ORACLE-CHAIN    -- lookup table keyed by the FULL ORDERED tuple of gold
                        edge_types -> majority target_text on TRAIN. Ceiling
                        achievable by a perfect symbolic composition table
                        given only as much data as TRAIN provides (not a true
                        1.0 oracle -- data-limited).

Train split (gen_train23_test2to10) contains ONLY k in {2,3}. Test split spans
k in {2..10}. All lookup tables are fit on TRAIN ONLY and evaluated (with
majority-label fallback for unseen keys) on VAL (k=2,3, in-distribution) and
TEST (k=2..10, out-of-distribution generalization) -- this is what makes the
by-k degradation check meaningful: any k>3 test example is, by construction,
outside the lookup tables' direct training keys except via key-collision
(e.g., the SAME (first,last) or SAME relation-multiset also appearing in a
shorter TRAIN chain).

Self-test: run with --self-test for a tiny in-memory smoke (no download).
"""
import argparse
import ast
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "clutrr")
OUT_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "clutrr_results.json")


def _parse_list_field(x):
    """CLUTRR parquet stores nested fields as stringified Python literals."""
    if isinstance(x, str):
        return ast.literal_eval(x)
    return x


def load_split(name):
    path = os.path.join(DATA_DIR, f"{name}.parquet")
    df = pd.read_parquet(path)
    df = df.copy()
    df["edge_types_p"] = df["edge_types"].apply(_parse_list_field)
    df["k"] = df["edge_types_p"].apply(len)
    return df


def fit_majority(train_df):
    counts = Counter(train_df["target_text"])
    return counts.most_common(1)[0][0], counts


def fit_bow_classifier(train_df):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform(train_df["clean_story"].astype(str))
    y = train_df["target_text"].values
    clf = LogisticRegression(max_iter=2000)
    clf.fit(X, y)
    return vec, clf


def fit_lookup(train_df, key_fn):
    table = defaultdict(Counter)
    for edge_types, label in zip(train_df["edge_types_p"], train_df["target_text"]):
        table[key_fn(edge_types)][label] += 1
    resolved = {k: c.most_common(1)[0][0] for k, c in table.items()}
    return resolved, table


def bag_key(edge_types):
    return tuple(sorted(edge_types))


def endpoint_key(edge_types):
    return (edge_types[0], edge_types[-1])


def chain_key(edge_types):
    return tuple(edge_types)


def eval_lookup(df, table, fallback, key_fn):
    preds = []
    hit_seen_key = []
    for edge_types in df["edge_types_p"]:
        k = key_fn(edge_types)
        if k in table:
            preds.append(table[k])
            hit_seen_key.append(True)
        else:
            preds.append(fallback)
            hit_seen_key.append(False)
    preds = np.array(preds)
    gold = df["target_text"].values
    correct = preds == gold
    return {
        "accuracy": float(correct.mean()),
        "n": int(len(df)),
        "frac_key_seen_in_train": float(np.mean(hit_seen_key)),
    }


def eval_bow(df, vec, clf):
    X = vec.transform(df["clean_story"].astype(str))
    preds = clf.predict(X)
    gold = df["target_text"].values
    return {"accuracy": float((preds == gold).mean()), "n": int(len(df))}


def eval_majority(df, majority_label):
    gold = df["target_text"].values
    return {"accuracy": float((gold == majority_label).mean()), "n": int(len(df))}


def by_k_breakdown(df, scorer_fn):
    out = {}
    for k, sub in df.groupby("k"):
        out[int(k)] = scorer_fn(sub)
    return out


def run(self_test=False):
    if self_test:
        return _self_test()

    train = load_split("train")
    val = load_split("validation")
    test = load_split("test")

    n_labels = train["target_text"].nunique()
    print(f"[LOAD] train={len(train)} val={len(val)} test={len(test)} n_labels={n_labels}")
    print(f"[LOAD] train k-dist={train['k'].value_counts().sort_index().to_dict()}")
    print(f"[LOAD] test k-dist={test['k'].value_counts().sort_index().to_dict()}")

    majority_label, majority_counts = fit_majority(train)
    print(f"[FIT] majority_label={majority_label} "
          f"frac={majority_counts[majority_label] / len(train):.4f}")

    vec, bow_clf = fit_bow_classifier(train)
    bag_table, _ = fit_lookup(train, bag_key)
    endpoint_table, _ = fit_lookup(train, endpoint_key)
    chain_table, _ = fit_lookup(train, chain_key)

    results = {"n_labels_train": int(n_labels), "chance_uniform": 1.0 / n_labels}

    for split_name, df in [("validation", val), ("test", test)]:
        results[split_name] = {
            "n": int(len(df)),
            "majority": eval_majority(df, majority_label),
            "content_bow": eval_bow(df, vec, bow_clf),
            "bag_of_relations": eval_lookup(df, bag_table, majority_label, bag_key),
            "endpoint_only": eval_lookup(df, endpoint_table, majority_label, endpoint_key),
            "oracle_chain_lookup": eval_lookup(df, chain_table, majority_label, chain_key),
        }
        results[split_name]["endpoint_only_by_k"] = by_k_breakdown(
            df, lambda sub: eval_lookup(sub, endpoint_table, majority_label, endpoint_key)
        )
        results[split_name]["majority_by_k"] = by_k_breakdown(
            df, lambda sub: eval_majority(sub, majority_label)
        )
        results[split_name]["bag_of_relations_by_k"] = by_k_breakdown(
            df, lambda sub: eval_lookup(sub, bag_table, majority_label, bag_key)
        )

    # degradation signature: endpoint_only edge over majority, by k, on TEST
    edge_by_k = {}
    for k, ep in results["test"]["endpoint_only_by_k"].items():
        maj = results["test"]["majority_by_k"][k]
        edge_by_k[k] = round(ep["accuracy"] - maj["accuracy"], 4)
    results["test"]["endpoint_only_edge_over_majority_by_k"] = edge_by_k

    ks_sorted = sorted(edge_by_k.keys())
    if len(ks_sorted) >= 2:
        k_lo, k_hi = ks_sorted[0], ks_sorted[-1]
        edge_lo, edge_hi = edge_by_k[k_lo], edge_by_k[k_hi]
        results["test"]["degradation_signature"] = {
            "k_lo": k_lo, "edge_at_k_lo": edge_lo,
            "k_hi": k_hi, "edge_at_k_hi": edge_hi,
            "relative_shrink": None if edge_lo <= 0 else round(1.0 - (edge_hi / edge_lo), 4),
        }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    os.replace(tmp, OUT_PATH)
    print(f"[DONE] wrote {OUT_PATH}")
    print(json.dumps({k: v for k, v in results.items() if k in ("validation", "test", "n_labels_train", "chance_uniform")}, indent=2)[:4000])
    return results


def _self_test():
    """Tiny in-memory smoke: synthetic 2-hop examples, no download, no
    network. Verifies the lookup/eval machinery is wired correctly (real
    code path, small scale) before trusting the full run. Exercises BOTH
    the seen-key hit path AND the unseen-key fallback path explicitly."""
    rows = []
    rels = [("sister", "grandfather", "grandfather"), ("father", "mother", "grandmother"),
            ("brother", "father", "father"), ("son", "sister", "aunt")]
    for i, (a, b, tgt) in enumerate(rels):
        rows.append({
            "clean_story": f"person{i} has a {a} and a {b} making a {tgt}",
            "edge_types_p": [a, b],
            "target_text": tgt,
            "k": 2,
        })
    train = pd.DataFrame(rows)
    # val_seen: identical bag/endpoint key to a train row -> must HIT and score correctly.
    val_seen = pd.DataFrame([{
        "clean_story": "another person has a sister and a grandfather",
        "edge_types_p": ["sister", "grandfather"], "target_text": "grandfather", "k": 2,
    }])
    # val_unseen: a bag/endpoint key never present in train -> must FALL BACK to majority.
    val_unseen = pd.DataFrame([{
        "clean_story": "another person has a daughter and a brother",
        "edge_types_p": ["daughter", "brother"], "target_text": "nephew", "k": 2,
    }])

    maj_label, _ = fit_majority(train)
    assert maj_label == "grandfather", f"self-test majority mismatch: {maj_label}"

    bag_table, _ = fit_lookup(train, bag_key)
    r_seen = eval_lookup(val_seen, bag_table, maj_label, bag_key)
    assert r_seen["accuracy"] == 1.0 and r_seen["frac_key_seen_in_train"] == 1.0, \
        f"self-test bag-of-relations (seen-key) expected hit+correct, got {r_seen}"
    r_unseen = eval_lookup(val_unseen, bag_table, maj_label, bag_key)
    assert r_unseen["frac_key_seen_in_train"] == 0.0, \
        f"self-test bag-of-relations (unseen-key) expected fallback, got {r_unseen}"
    assert r_unseen["accuracy"] == 0.0, \
        f"self-test bag-of-relations (unseen-key) fallback=majority='{maj_label}' != gold 'nephew', expected 0.0, got {r_unseen}"

    ep_table, _ = fit_lookup(train, endpoint_key)
    r2 = eval_lookup(val_seen, ep_table, maj_label, endpoint_key)
    assert r2["accuracy"] == 1.0, f"self-test endpoint-only (seen-key) expected 1.0 got {r2}"

    vec, clf = fit_bow_classifier(train)
    r3 = eval_bow(val_seen, vec, clf)
    assert 0.0 <= r3["accuracy"] <= 1.0 and r3["n"] == 1, f"self-test BoW sanity failed: {r3}"

    print("[SELF-TEST] PASS -- lookup/eval machinery verified (hit path + fallback path + BoW)")
    return {"self_test": "PASS"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        run(self_test=args.self_test)
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        raise
