"""
Benchmark trap-check sweep: TRIP (Storks, Gao, Zhang, Chai, EMNLP Findings 2021)
Cloze task -- given a pair of stories (one physically plausible, one made
implausible by swapping a single "breakpoint" sentence), pick the plausible
one.

MEASUREMENT ONLY -- not an inference pipeline. Per
notes/research_extraction_foundation_decisive_benchmark_2026-08-10.md, TRIP's
content ceiling and structure-vs-composition status are "COMPLETELY
UNMEASURED -- no BoW/lexical baseline ever published." This script produces
the first disk-verified numbers.

Data sources (both required; the HF auto-converted parquet drops the nested
per-sentence state annotations during schema flattening -- confirmed by
direct inspection, all state-* arrays empty in ClozeTrain/Dev/Test.parquet):
  - HF sled-umich/TRIP parquet (ClozeTrain/ClozeDev/ClozeTest): gives the
    pair structure (label = which of stories[0]/stories[1] is plausible).
  - GitHub sled-group/Verifiable-Coherent-NLU all_data/www.json: gives the
    dense per-sentence, per-entity, per-attribute (20 attrs) physical-state
    annotations, keyed by example_id, used to build the GOLD-structure
    "bag of states" trap-check.

Baselines computed (ASCII-only):
  1. MAJORITY        -- predict a fixed position (0) for every pair; report
                         both label-distribution and the accuracy of that
                         fixed choice (near-chance if positions are balanced).
  2. CONTENT/BoW      -- TF-IDF(full story text) difference vector (A - B)
                         -> logistic regression -> predict which position is
                         plausible. Tests whether raw surface style/lexical
                         choice (not tracked physical state) leaks the
                         answer -- the MCScript/Story-Cloze-style trap.
  3. LAST-SENTENCE-ONLY (TRIP's endpoint-only analog) -- same as (2) but
                         featurized from ONLY the final sentence of each
                         story (skips all intervening context/history).
                         Tests whether the single anomalous sentence alone,
                         without any accumulated physical-state history,
                         already gives the game away.
  4. BAG-OF-STATES (structure-without-composition, the WIQA-style trap)
                         -- uses TRIP's own dense GOLD per-sentence attribute
                         annotations (www.json), pooled UNORDERED across all
                         sentences in a story: for each (entity, attribute)
                         pair, does its assigned state value change at least
                         once anywhere in the story (order-blind "churn"
                         count)? Predict implausible = higher-churn story
                         (direction fit on TRAIN, not assumed). If this
                         solves the task, plain unordered state-presence
                         solves it and no temporal/precondition composition
                         is required.

Self-test: run with --self-test for a tiny in-memory smoke (no download).
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "trip")
OUT_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "trip_results.json")


def load_cloze_split(name):
    path = os.path.join(DATA_DIR, f"Cloze{name}.parquet")
    return pd.read_parquet(path)


def load_www():
    path = os.path.join(DATA_DIR, "www.json")
    www = json.load(open(path, encoding="utf-8"))
    merged = {}
    for split in www:
        merged.update(www[split])
    return merged


def story_text(story_dict, last_sentence_only=False):
    sents = story_dict["sentences"]
    if last_sentence_only:
        return str(sents[-1]) if len(sents) else ""
    return " ".join(str(s) for s in sents)


def churn_count(www_entry):
    """Order-blind: for each (entity, attribute), does the assigned state
    value change at least once across the story's sentences? Count how many
    (entity, attribute) pairs do."""
    states = www_entry.get("states", [])
    per_key_values = {}
    for sent_states in states:
        for attr, pairs in sent_states.items():
            for ent, val in pairs:
                key = (ent, attr)
                per_key_values.setdefault(key, set()).add(val)
    return sum(1 for v in per_key_values.values() if len(v) >= 2)


def build_pairs_df(cloze_df, www_lookup):
    rows = []
    for _, r in cloze_df.iterrows():
        s0, s1 = r["stories"][0], r["stories"][1]
        label = int(r["label"])  # index (0 or 1) of the plausible story
        rows.append({
            "example_id": r["example_id"],
            "label": label,
            "text0": story_text(s0),
            "text1": story_text(s1),
            "last0": story_text(s0, last_sentence_only=True),
            "last1": story_text(s1, last_sentence_only=True),
            "churn0": churn_count(www_lookup.get(s0["example_id"], {})),
            "churn1": churn_count(www_lookup.get(s1["example_id"], {})),
        })
    return pd.DataFrame(rows)


def eval_majority(df):
    # predict position 0 always plausible
    pred = np.zeros(len(df), dtype=int)
    gold = df["label"].values
    return {
        "accuracy": float((pred == gold).mean()),
        "n": int(len(df)),
        "label_dist": {int(k): int(v) for k, v in df["label"].value_counts().to_dict().items()},
    }


def fit_diff_classifier(train_df, text0_col, text1_col):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    corpus = pd.concat([train_df[text0_col], train_df[text1_col]]).tolist()
    vec.fit(corpus)
    X0 = vec.transform(train_df[text0_col])
    X1 = vec.transform(train_df[text1_col])
    Xd = (X0 - X1).toarray()
    y = (train_df["label"].values == 0).astype(int)  # 1 if position0 plausible
    clf = LogisticRegression(max_iter=2000)
    clf.fit(Xd, y)
    return vec, clf


def eval_diff_classifier(df, vec, clf, text0_col, text1_col):
    X0 = vec.transform(df[text0_col])
    X1 = vec.transform(df[text1_col])
    Xd = (X0 - X1).toarray()
    pred_pos0 = clf.predict(Xd)  # 1 if predicts position0 plausible
    pred_label = np.where(pred_pos0 == 1, 0, 1)
    gold = df["label"].values
    return {"accuracy": float((pred_label == gold).mean()), "n": int(len(df))}


def fit_churn_direction(train_df):
    """Direction: does HIGHER churn correlate with implausible (label picks
    the OTHER position)? Fit on train by majority vote, do not assume."""
    higher_is_implausible_votes = 0
    decidable = 0
    for _, r in train_df.iterrows():
        if r["churn0"] == r["churn1"]:
            continue
        decidable += 1
        higher_idx = 0 if r["churn0"] > r["churn1"] else 1
        implausible_idx = 1 - r["label"]
        if higher_idx == implausible_idx:
            higher_is_implausible_votes += 1
    frac = higher_is_implausible_votes / decidable if decidable else 0.5
    return {
        "higher_churn_is_implausible": frac >= 0.5,
        "frac_support": float(frac),
        "n_decidable_train": int(decidable),
        "n_tied_train": int(len(train_df) - decidable),
    }


def eval_churn_baseline(df, direction):
    higher_is_implausible = direction["higher_churn_is_implausible"]
    correct = 0
    n_tied = 0
    for _, r in df.iterrows():
        if r["churn0"] == r["churn1"]:
            n_tied += 1
            # tie -> coin flip; count as 0.5 expected, but score deterministically as wrong half the time via fixed default (predict position0 plausible)
            pred_label = 0
        else:
            higher_idx = 0 if r["churn0"] > r["churn1"] else 1
            implausible_idx = higher_idx if higher_is_implausible else (1 - higher_idx)
            pred_label = 1 - implausible_idx
        correct += int(pred_label == r["label"])
    return {
        "accuracy": float(correct / len(df)) if len(df) else 0.0,
        "n": int(len(df)),
        "frac_tied_churn": float(n_tied / len(df)) if len(df) else 0.0,
    }


def run(self_test=False):
    if self_test:
        return _self_test()

    www_lookup = load_www()
    print(f"[LOAD] www.json entries: {len(www_lookup)}")

    train_c = load_cloze_split("Train")
    dev_c = load_cloze_split("Dev")
    test_c = load_cloze_split("Test")
    print(f"[LOAD] ClozeTrain={len(train_c)} ClozeDev={len(dev_c)} ClozeTest={len(test_c)}")

    train = build_pairs_df(train_c, www_lookup)
    dev = build_pairs_df(dev_c, www_lookup)
    test = build_pairs_df(test_c, www_lookup)

    vec_full, clf_full = fit_diff_classifier(train, "text0", "text1")
    vec_last, clf_last = fit_diff_classifier(train, "last0", "last1")
    churn_direction = fit_churn_direction(train)
    print(f"[FIT] churn_direction={churn_direction}")

    results = {"churn_direction": churn_direction}
    for split_name, df in [("dev", dev), ("test", test)]:
        results[split_name] = {
            "n": int(len(df)),
            "majority_fixed_position0": eval_majority(df),
            "content_bow_fulltext": eval_diff_classifier(df, vec_full, clf_full, "text0", "text1"),
            "last_sentence_only": eval_diff_classifier(df, vec_last, clf_last, "last0", "last1"),
            "bag_of_states_churn": eval_churn_baseline(df, churn_direction),
        }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    os.replace(tmp, OUT_PATH)
    print(f"[DONE] wrote {OUT_PATH}")
    print(json.dumps(results, indent=2)[:4000])
    return results


def _self_test():
    """Tiny in-memory smoke exercising the REAL code path (churn_count,
    fit_diff_classifier, fit_churn_direction) at N~6 pairs, no download."""
    www_lookup = {
        "0": {"states": [{"loc": [["cup", 0]]}, {"loc": [["cup", 0]]}]},          # no churn
        "0-C0": {"states": [{"loc": [["cup", 0]]}, {"loc": [["cup", 5]]}]},        # churn=1
        "1": {"states": [{"loc": [["pan", 1]]}, {"loc": [["pan", 1]]}]},
        "1-C0": {"states": [{"loc": [["pan", 1]]}, {"loc": [["pan", 9]]}]},
        "2": {"states": [{"loc": [["pot", 1]]}, {"loc": [["pot", 1]]}]},
        "2-C0": {"states": [{"loc": [["pot", 1]]}, {"loc": [["pot", 3]]}]},
    }
    rows = [
        {"example_id": "0-C0", "label": 1,
         "stories": [
             {"example_id": "0-C0", "sentences": ["A cup sat there.", "It stayed still oddly."]},
             {"example_id": "0", "sentences": ["A cup sat there.", "It stayed on the table."]},
         ]},
        {"example_id": "1-C0", "label": 1,
         "stories": [
             {"example_id": "1-C0", "sentences": ["A pan was used.", "It teleported away weirdly."]},
             {"example_id": "1", "sentences": ["A pan was used.", "It was washed after."]},
         ]},
        {"example_id": "2-C0", "label": 0,
         "stories": [
             {"example_id": "2", "sentences": ["A pot was heated.", "It was set on the stove."]},
             {"example_id": "2-C0", "sentences": ["A pot was heated.", "It flew into orbit strangely."]},
         ]},
    ]
    df = pd.DataFrame(rows)
    pairs = build_pairs_df(df, www_lookup)
    assert list(pairs["churn0"]) == [1, 1, 0], f"self-test churn0 expected [1,1,0] got {pairs['churn0'].tolist()}"
    assert list(pairs["churn1"]) == [0, 0, 1], f"self-test churn1 expected [0,0,1] got {pairs['churn1'].tolist()}"

    direction = fit_churn_direction(pairs)
    assert direction["higher_churn_is_implausible"] is True, f"self-test direction fit wrong: {direction}"
    ev = eval_churn_baseline(pairs, direction)
    assert ev["accuracy"] == 1.0, f"self-test churn baseline expected 1.0 got {ev}"

    vec, clf = fit_diff_classifier(pairs, "text0", "text1")
    ev2 = eval_diff_classifier(pairs, vec, clf, "text0", "text1")
    assert 0.0 <= ev2["accuracy"] <= 1.0 and ev2["n"] == 3, f"self-test BoW-diff sanity failed: {ev2}"

    maj = eval_majority(pairs)
    assert maj["n"] == 3 and "label_dist" in maj, f"self-test majority sanity failed: {maj}"

    print("[SELF-TEST] PASS -- churn/diff-classifier/majority machinery verified on 3-pair synthetic smoke")
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
