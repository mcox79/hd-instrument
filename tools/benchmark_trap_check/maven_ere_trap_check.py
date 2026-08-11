"""
Benchmark trap-check sweep: MAVEN-ERE (Wang et al., EMNLP 2022,
THU-KEG/MAVEN-ERE) causal + subevent relation classification.

MEASUREMENT ONLY -- not an inference pipeline, ZERO organ engineering. This
is Step 0 from notes/research_next_benchmark_after_propara_trap_check_2026-08-10.md
(HEADLINE + Section 3 "First-experiment design"): MAVEN-ERE has NO published
majority/naive baseline anywhere -- the same evidentiary hole that hid WIQA's
oracle-structure leak until this program measured it directly. The dominant
risk flagged in that note: causal relations (57,992 event-level edges) are
very likely a small minority of the full candidate event-mention-pair space,
so a naive "predict no-relation" baseline could be deceptively strong under a
naive metric even though it is structurally weak under the DATASET'S OWN
official metric (see maven_ere_official_eval.py's module docstring for why).

Three baselines computed on the causal-relation task, dev split
(valid.jsonl; test.jsonl gold is hidden per the repo README -- CodaLab-only),
fit (where applicable) on train.jsonl, ASCII-only:

  1. MAJORITY       -- predict the single most frequent label over ALL
                        candidate mention-pairs in TRAIN (almost certainly
                        NONE given the skew), applied everywhere in dev.
                        THE single most important number per the pre-reg.
  2. ADJACENT-SENTENCE-HEURISTIC -- predict CAUSE for the earlier-of-the-pair
                        -> later-of-the-pair mention ordering (by sent_id
                        then token offset) whenever the two events sit in the
                        same or an adjacent sentence AND that sentence-window
                        text contains one of a small fixed causal-connective
                        list (because / so / as a result / due to / therefore
                        / thus / hence / consequently). No train fit --
                        pure surface heuristic, the TORQUE/ProLocal-style
                        shortcut this exact task shape is most likely to leak
                        on per the pre-reg.
  3. BAG-OF-EVENT-TYPES -- lookup table (Counter-based, same pattern as
                        clutrr_trap_check.py's bag_of_relations probe) keyed
                        by the ordered (event_type_A, event_type_B) pair
                        ALONE (MAVEN's own 168-way event-type taxonomy,
                        ignoring all surrounding text), majority-vote fit on
                        TRAIN, fallback = train global majority for unseen
                        type-pairs. Tests whether the relation TYPE is
                        over-predictable from static event-type co-occurrence
                        alone -- the MAVEN-ERE analog of WIQA's sign-leak and
                        CLUTRR's bag-of-relations probe.

Metric: the dataset's OWN official evaluator (evaluate.py's `evaluate()`
function, positive-label-only micro P/R/F1 *100 -- ported faithfully in
maven_ere_official_eval.py; see that module's docstring for the load-bearing
structural property that this metric structurally zeroes out an all-NONE
majority baseline even though the SAME baseline would score ~97-98% on plain
accuracy given the measured class skew). Also reported per this cell's
instruction to show "both their headline metric and, if different,
macro-F1": macro-F1 over ALL labels (0/1/2), plus raw accuracy, for every arm.

Subevent task: majority baseline + class skew reported (Section 3 of the
scout note flags subevent, 15,841 event-level edges, as a possible cleaner
fallback if causal doesn't clear).

VERDICT BANDS (pre-registered in the scout note's "Falsifiable predictions"
section, applied here programmatically, not hand-tuned post-hoc):
  HARD-PASS: majority_f1 <= 40.0 AND adjacent_f1 <= majority_f1+10 AND
             bag_f1 <= majority_f1+10 AND (sota_f1 - best_baseline_f1) >= 5.0
  HARD-FAIL: any of the three baselines scores within 5 points of the
             published SOTA F1 (~31.96, ProtoEM 2023).
  MIDDLE_BAND: neither -- a shortcut shows a real-but-partial edge.
Published SOTA + human-agreement numbers are CITED (from the scout note's
Lane C lit-scan), not re-derived here.

Self-test: run with --self-test for a tiny in-memory smoke (no download),
exercising the real candidate-pair/official-eval/majority/adjacent-sentence/
bag-of-event-types/verdict code paths at N~4 mentions across 3 tiny docs.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

from maven_ere_official_eval import (
    accuracy_pct,
    candidate_pairs,
    macro_f1_all_labels,
    official_gold_labels,
    official_prf,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "maven_ere")
OUT_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "maven_ere_results.json")

# CITED (Section 3 / HEADLINE of the scout note, Lane C lit-scan): ProtoEM
# (arXiv:2309.12892, 2023) causal F1 31.96+/-0.24 -- the most recent published
# number and essentially unchanged from the 2022 MAVEN-ERE paper's own joint
# model (~31.5 causal F1), i.e. the field has not closed this gap since 2022.
SOTA_CAUSAL_F1 = 31.96
SOTA_SUBEVENT_F1 = 29.73
HUMAN_KAPPA_CAUSAL = 0.695
HUMAN_KAPPA_SUBEVENT = 0.751

CONNECTIVE_RE = re.compile(
    r"\b(?:because|so|as a result|due to|therefore|thus|hence|consequently)\b",
    re.IGNORECASE,
)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------- majority
def fit_majority(gold_list):
    counts = Counter()
    for gold in gold_list:
        counts.update(gold.values())
    maj = counts.most_common(1)[0][0]
    return maj, counts


def predict_majority(doc, maj_label):
    keys, _ = candidate_pairs(doc)
    return {k: maj_label for k in keys}


# ------------------------------------------------- adjacent-sentence heuristic
def build_mention_meta(doc):
    """mention_id -> {"sent_id": int, "start": int}."""
    meta = {}
    for event in doc["events"]:
        for m in event["mention"]:
            meta[m["id"]] = {"sent_id": m["sent_id"], "start": m["offset"][0]}
    return meta


def predict_adjacent_sentence_heuristic(doc):
    """CAUSE (label 2) for the earlier->later ordered pair whenever the two
    mentions are in the same/adjacent sentence AND that sentence-window text
    contains a causal connective. NONE (0) for every other candidate pair,
    including the reverse direction of a fired pair. Never predicts
    PRECONDITION (1) -- this heuristic has no signal for that class."""
    keys, _ = candidate_pairs(doc)
    pred = {k: 0 for k in keys}
    meta = build_mention_meta(doc)
    sentences = doc["sentences"]
    seen_unordered = set()
    for (m1, m2) in keys:
        pair_u = frozenset((m1, m2))
        if pair_u in seen_unordered:
            continue
        seen_unordered.add(pair_u)
        s1, s2 = meta[m1]["sent_id"], meta[m2]["sent_id"]
        if abs(s1 - s2) > 1:
            continue
        lo, hi = min(s1, s2), max(s1, s2)
        window_text = " ".join(sentences[lo:hi + 1])
        if not CONNECTIVE_RE.search(window_text):
            continue
        if (s1, meta[m1]["start"]) <= (s2, meta[m2]["start"]):
            earlier, later = m1, m2
        else:
            earlier, later = m2, m1
        pred[(earlier, later)] = 2  # CAUSE
    return pred


# ----------------------------------------------------- bag-of-event-types
def build_mention_to_type(doc):
    m2t = {}
    for event in doc["events"]:
        t = event["type"]
        for m in event["mention"]:
            m2t[m["id"]] = t
    return m2t


def fit_bag_of_event_types(docs, gold_list):
    table = defaultdict(Counter)
    global_counts = Counter()
    for doc, gold in zip(docs, gold_list):
        m2t = build_mention_to_type(doc)
        for (m1, m2), label in gold.items():
            key = (m2t[m1], m2t[m2])
            table[key][label] += 1
            global_counts[label] += 1
    resolved = {k: c.most_common(1)[0][0] for k, c in table.items()}
    fallback = global_counts.most_common(1)[0][0] if global_counts else 0
    return resolved, fallback, len(table)


def predict_bag_of_event_types(doc, table, fallback):
    keys, _ = candidate_pairs(doc)
    m2t = build_mention_to_type(doc)
    pred = {}
    for (m1, m2) in keys:
        key = (m2t[m1], m2t[m2])
        pred[(m1, m2)] = table.get(key, fallback)
    return pred


# --------------------------------------------------------------- evaluation
def align(gold: dict, pred: dict):
    g, p = [], []
    for k, v in gold.items():
        g.append(v)
        p.append(pred[k])
    return g, p


def eval_predictor_over_docs(docs, rel_type, predict_fn, gold_cache):
    all_gold, all_pred = [], []
    for doc, gold in zip(docs, gold_cache):
        pred = predict_fn(doc)
        g, p = align(gold, pred)
        all_gold.extend(g)
        all_pred.extend(p)
    n = len(all_gold)
    dist = Counter(all_gold)
    return {
        "official_micro_f1_positive_only": official_prf(all_gold, all_pred, rel_type),
        "macro_f1_all_labels": macro_f1_all_labels(all_gold, all_pred, rel_type),
        "accuracy_pct": accuracy_pct(all_gold, all_pred),
        "n_candidate_pairs": n,
        "gold_label_dist": {str(k): int(v) for k, v in dist.items()},
        "gold_label_frac": {str(k): (v / n if n else 0.0) for k, v in dist.items()},
    }


# ------------------------------------------------------------------ verdict
def verdict_causal(maj_f1, adj_f1, bag_f1, sota_f1):
    scored = [("majority", maj_f1), ("adjacent_sentence_heuristic", adj_f1), ("bag_of_event_types", bag_f1)]
    within_5pts_of_sota = [name for name, f1 in scored if (sota_f1 - f1) < 5.0]
    hard_pass = (
        maj_f1 <= 40.0
        and adj_f1 <= maj_f1 + 10.0
        and bag_f1 <= maj_f1 + 10.0
        and (sota_f1 - max(maj_f1, adj_f1, bag_f1)) >= 5.0
    )
    if within_5pts_of_sota:
        band = "HARD-FAIL"
    elif hard_pass:
        band = "HARD-PASS"
    else:
        band = "MIDDLE_BAND"
    return {
        "band": band,
        "majority_f1": maj_f1,
        "adjacent_sentence_heuristic_f1": adj_f1,
        "bag_of_event_types_f1": bag_f1,
        "published_sota_f1": sota_f1,
        "best_baseline_f1": max(maj_f1, adj_f1, bag_f1),
        "headroom_vs_sota": sota_f1 - max(maj_f1, adj_f1, bag_f1),
        "within_5pts_of_sota": within_5pts_of_sota,
    }


# ---------------------------------------------------------------------- run
def run(self_test=False):
    if self_test:
        return _self_test()

    train_path = os.path.join(DATA_DIR, "train.jsonl")
    dev_path = os.path.join(DATA_DIR, "valid.jsonl")
    if not os.path.exists(train_path) or not os.path.exists(dev_path):
        raise FileNotFoundError(
            f"MAVEN-ERE data not found at {DATA_DIR}. Expected train.jsonl + valid.jsonl "
            f"(fetch per data/benchmark_trap_check/maven_ere/PROVENANCE.md)."
        )

    train = load_jsonl(train_path)
    dev = load_jsonl(dev_path)
    print(f"[LOAD] train_docs={len(train)} dev_docs={len(dev)}")

    results = {
        "dataset": "MAVEN-ERE (Wang et al., EMNLP 2022, arXiv:2211.07342)",
        "source": "https://github.com/THU-KEG/MAVEN-ERE",
        "obtained_via": "Tsinghua Cloud mirror linked from the repo README (data/download_maven.sh URL), fetched 2026-08-10",
        "train_docs": len(train),
        "dev_docs": len(dev),
        "eval_split_used": "valid.jsonl (dev; test.jsonl gold is hidden per the repo README, CodaLab-only)",
    }

    # ---------------------------------------------------------- CAUSAL task
    train_gold_causal = [official_gold_labels(d, "causal") for d in train]
    dev_gold_causal = [official_gold_labels(d, "causal") for d in dev]

    causal_maj_label, causal_maj_train_counts = fit_majority(train_gold_causal)
    print(f"[FIT] causal majority_label={causal_maj_label} train_label_counts={dict(causal_maj_train_counts)}")

    bag_table, bag_fallback, bag_n_keys = fit_bag_of_event_types(train, train_gold_causal)
    print(f"[FIT] causal bag_of_event_types n_type_pair_keys={bag_n_keys} fallback_label={bag_fallback}")

    causal_results = {
        "majority": eval_predictor_over_docs(
            dev, "causal", lambda d: predict_majority(d, causal_maj_label), dev_gold_causal
        ),
        "adjacent_sentence_heuristic": eval_predictor_over_docs(
            dev, "causal", predict_adjacent_sentence_heuristic, dev_gold_causal
        ),
        "bag_of_event_types": eval_predictor_over_docs(
            dev, "causal", lambda d: predict_bag_of_event_types(d, bag_table, bag_fallback), dev_gold_causal
        ),
    }
    results["causal"] = causal_results
    print(json.dumps({k: v["official_micro_f1_positive_only"] for k, v in causal_results.items()}, indent=2))

    # -------------------------------------------------------- SUBEVENT task
    train_gold_sub = [official_gold_labels(d, "subevent") for d in train]
    dev_gold_sub = [official_gold_labels(d, "subevent") for d in dev]
    sub_maj_label, sub_maj_train_counts = fit_majority(train_gold_sub)
    print(f"[FIT] subevent majority_label={sub_maj_label} train_label_counts={dict(sub_maj_train_counts)}")
    results["subevent"] = {
        "majority": eval_predictor_over_docs(
            dev, "subevent", lambda d: predict_majority(d, sub_maj_label), dev_gold_sub
        ),
    }

    # -------------------------------------------- cited published baselines
    results["cited_published_baselines_for_corroboration"] = {
        "source_2022_paper": "Wang et al. 2022 EMNLP (MAVEN-ERE paper), RoBERTa-based joint model",
        "causal_f1_2022": 31.5,
        "subevent_f1_2022": 27.5,
        "source_2023_protoem": "ProtoEM, arXiv:2309.12892 (2023)",
        "causal_f1_2023_protoem": SOTA_CAUSAL_F1,
        "causal_f1_2023_protoem_std": 0.24,
        "subevent_f1_2023_protoem": SOTA_SUBEVENT_F1,
        "subevent_f1_2023_protoem_std": 0.26,
        "human_agreement_causal_kappa": HUMAN_KAPPA_CAUSAL,
        "human_agreement_subevent_kappa": HUMAN_KAPPA_SUBEVENT,
        "note": (
            "CITED from notes/research_next_benchmark_after_propara_trap_check_2026-08-10.md "
            "(Lane C lit-scan sources: MAVEN-ERE paper + ProtoEM arXiv:2309.12892); not re-derived here."
        ),
    }

    # -------------------------------------------------------------- verdict
    maj_f1 = causal_results["majority"]["official_micro_f1_positive_only"]["f1"]
    adj_f1 = causal_results["adjacent_sentence_heuristic"]["official_micro_f1_positive_only"]["f1"]
    bag_f1 = causal_results["bag_of_event_types"]["official_micro_f1_positive_only"]["f1"]
    results["verdict"] = verdict_causal(maj_f1, adj_f1, bag_f1, SOTA_CAUSAL_F1)
    print(f"[VERDICT] {results['verdict']}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    os.replace(tmp, OUT_PATH)
    print(f"[DONE] wrote {OUT_PATH}")
    return results


# ------------------------------------------------------------------- smoke
def _self_test():
    """Tiny in-memory smoke, no download, no network. Exercises the REAL
    code path (candidate_pairs / official_gold_labels / official_prf from
    maven_ere_official_eval.py, plus this module's majority / adjacent-
    sentence-heuristic / bag-of-event-types / verdict logic) at N~4-5
    mentions across 3 tiny synthetic docs."""
    # doc A: connective present, adjacent sentences, heuristic SHOULD fire
    # and land exactly on the one true CAUSE edge (m1 rain -> m2 flood).
    doc_a = {
        "id": "docA",
        "sentences": ["The rain fell.", "The river flooded because of the rain."],
        "events": [
            {"id": "e1", "type": "Rain", "mention": [{"id": "a_m1", "sent_id": 0, "offset": [1, 2]}]},
            {"id": "e2", "type": "Flood", "mention": [{"id": "a_m2", "sent_id": 1, "offset": [1, 2]}]},
        ],
        "causal_relations": {"CAUSE": [["e1", "e2"]], "PRECONDITION": []},
        "subevent_relations": [],
    }
    # doc B: adjacent sentences, NO connective -> heuristic must NOT fire.
    doc_b = {
        "id": "docB",
        "sentences": ["A man ran.", "He was tired.", "Nothing else happened."],
        "events": [
            {"id": "e1", "type": "Motion", "mention": [{"id": "b_m1", "sent_id": 0, "offset": [1, 2]}]},
            {"id": "e2", "type": "Sensation", "mention": [{"id": "b_m2", "sent_id": 1, "offset": [1, 2]}]},
        ],
        "causal_relations": {"CAUSE": [], "PRECONDITION": []},
        "subevent_relations": [],
    }
    # doc C (dev-only, unseen event-type pair "Sound"/"Sound") -> exercises
    # the bag-of-event-types FALLBACK path explicitly.
    doc_c = {
        "id": "docC",
        "sentences": ["A dog barked.", "A cat meowed."],
        "events": [
            {"id": "e1", "type": "Sound", "mention": [{"id": "c_m1", "sent_id": 0, "offset": [1, 2]}]},
            {"id": "e2", "type": "Sound", "mention": [{"id": "c_m2", "sent_id": 1, "offset": [1, 2]}]},
        ],
        "causal_relations": {"CAUSE": [], "PRECONDITION": []},
        "subevent_relations": [],
    }

    train_docs = [doc_a, doc_b]
    dev_docs = [doc_a, doc_c]  # reuse doc_a (exercises "seen" path) + doc_c (exercises fallback path)

    train_gold = [official_gold_labels(d, "causal") for d in train_docs]
    dev_gold = [official_gold_labels(d, "causal") for d in dev_docs]

    # majority: train pairs = docA {(a_m1,a_m2):2, (a_m2,a_m1):0} + docB
    # {(b_m1,b_m2):0, (b_m2,b_m1):0} -> 3x NONE, 1x CAUSE -> majority=NONE(0).
    maj_label, maj_counts = fit_majority(train_gold)
    assert maj_label == 0, f"self-test expected majority label NONE(0), got {maj_label} counts={maj_counts}"
    assert maj_counts == Counter({0: 3, 2: 1}), f"self-test majority train counts mismatch: {maj_counts}"

    # adjacent-sentence heuristic: connective test in isolation.
    assert CONNECTIVE_RE.search("The river flooded because of the rain.") is not None
    assert CONNECTIVE_RE.search("He was tired.") is None
    pred_a = predict_adjacent_sentence_heuristic(doc_a)
    assert pred_a[("a_m1", "a_m2")] == 2, f"self-test heuristic should fire CAUSE on docA: {pred_a}"
    assert pred_a[("a_m2", "a_m1")] == 0, f"self-test heuristic must not fire reverse direction: {pred_a}"
    pred_b = predict_adjacent_sentence_heuristic(doc_b)
    assert pred_b[("b_m1", "b_m2")] == 0 and pred_b[("b_m2", "b_m1")] == 0, (
        f"self-test heuristic must NOT fire without a connective: {pred_b}"
    )

    # bag-of-event-types: fit on train (Rain/Flood + Motion/Sensation type
    # pairs only), evaluate on dev docA (seen key) + docC (unseen -> fallback).
    bag_table, bag_fallback, bag_n_keys = fit_bag_of_event_types(train_docs, train_gold)
    assert bag_n_keys == 4, f"self-test expected 4 distinct type-pair keys in train, got {bag_n_keys}: {bag_table}"
    assert bag_table[("Rain", "Flood")] == 2, f"self-test bag-of-types seen-key mismatch: {bag_table}"
    assert bag_fallback == 0, f"self-test bag-of-types fallback should be NONE(0), got {bag_fallback}"
    pred_bag_c = predict_bag_of_event_types(doc_c, bag_table, bag_fallback)
    assert ("Sound", "Sound") not in bag_table, "self-test setup error: (Sound,Sound) should be UNSEEN in train"
    assert pred_bag_c[("c_m1", "c_m2")] == 0, f"self-test bag-of-types fallback path wrong: {pred_bag_c}"

    # official metric structural check (all-NONE majority on the 2-pair docA
    # dev-slice, where the true label distribution is 1x CAUSE + 1x NONE):
    maj_eval = eval_predictor_over_docs(
        [doc_a], "causal", lambda d: predict_majority(d, maj_label), [official_gold_labels(doc_a, "causal")]
    )
    assert maj_eval["official_micro_f1_positive_only"]["f1"] == 0.0, (
        f"self-test: all-NONE majority must score exactly 0.0 official F1, got {maj_eval}"
    )
    assert maj_eval["accuracy_pct"] == 50.0, f"self-test: majority accuracy on 1 CAUSE + 1 NONE should be 50.0, got {maj_eval}"

    heuristic_eval = eval_predictor_over_docs(
        [doc_a], "causal", predict_adjacent_sentence_heuristic, [official_gold_labels(doc_a, "causal")]
    )
    assert heuristic_eval["official_micro_f1_positive_only"]["f1"] == 100.0, (
        f"self-test: heuristic should PERFECTLY recover docA's one true CAUSE edge, got {heuristic_eval}"
    )

    # verdict logic: pure unit tests against the three pre-registered bands.
    v_pass = verdict_causal(maj_f1=0.0, adj_f1=5.0, bag_f1=3.0, sota_f1=31.96)
    assert v_pass["band"] == "HARD-PASS", f"self-test verdict HARD-PASS case failed: {v_pass}"
    v_fail = verdict_causal(maj_f1=25.0, adj_f1=28.0, bag_f1=10.0, sota_f1=31.96)
    assert v_fail["band"] == "HARD-FAIL", f"self-test verdict HARD-FAIL case failed: {v_fail}"
    v_mid = verdict_causal(maj_f1=0.0, adj_f1=15.0, bag_f1=3.0, sota_f1=31.96)
    assert v_mid["band"] == "MIDDLE_BAND", f"self-test verdict MIDDLE_BAND case failed: {v_mid}"

    print("[SELF-TEST] PASS -- candidate-pairs/official-eval/majority/adjacent-sentence/"
          "bag-of-event-types/verdict machinery verified on 3-doc synthetic smoke")
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
