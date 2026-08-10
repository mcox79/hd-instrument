# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; MAJORITY/BOW/BAGSTATES/REASONING/
#   REASONING_SCRAMBLE per-para label-grid hashes must differ)
# - final_metrics_atomicity: tmp_replace (single-shot) + per-seed checkpoint (experiments/
#   _seed_checkpoint.py) for the scramble-seed loop
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: accuracy/F1-comparison ablation over a fixed real corpus (ProPara EMNLP18
#   dev/test); no capacity/noise-floor discriminator threshold to CRLB-check
# - HP_SCOPE: {reasoning_vs_baselines: [official_full_set_no_regression, proxy_focus_subset_win,
#   scramble_collapse], scramble: [scramble_collapse], baselines: [] (reference only, no HP gate)}
# - cardinality_ok: EXPECTED_N_UNITS=len(SEEDS)=1 (smoke) / 3 (full) scramble-permutation seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (bands calibrated from --smoke DEV-set
#   numbers per preregs/2026-08-10_propara_decisive_inference_arm1_oracle_v1.md, applied
#   unchanged to the --full TEST-set run; no test-set peeking)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL substrate objects (AccumulateRegister,
#   propara_official_eval.corpus_evaluation, TfidfVectorizer/LogisticRegression) at tiny
#   scale (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true (elapsed_s << 1800s expected; declared anyway)
# See preregs/2026-08-10_propara_decisive_inference_arm1_oracle_v1.md for the full pre-reg.
"""exp_propara_decisive_inference_arm1_oracle_v1 -- THE DECISIVE INFERENCE TEST, ARM 1
(oracle structure), on ProPara (Dalvi et al. 2018 NAACL). Isolates INFERENCE from
EXTRACTION: given ProPara's GOLD event structure (per-participant event MULTISET --
same oracle grant as the bag-of-states baseline: does participant X get
created/moved/destroyed anywhere in the paragraph, with counts, but NOT which step),
does glass-box REASONING (hdlab.situation_model_accumulate.AccumulateRegister as the
per-paragraph situation-model register + a retrieve-validate-advance greedy assignment
loop, structurally modeled on experiments/exp_focus_pullin_causal_stage2a_multihop_
loop_v1.py's retrieve->validate->advance pattern) correctly LOCALIZE each oracle event
to its true step, beating baselines that lack either the oracle structure (majority,
BoW/single-step) or the cross-step composition ability (bag-of-states), under BOTH (a)
the OFFICIAL ProPara leaderboard metric (Inputs/Outputs/Conversions/Moves, ported
bit-exact in tools/benchmark_trap_check/propara_official_eval.py, validated against the
official evaluator repo's own regression fixtures) on the FULL participant set (full-set
no-regression), and (b) the trap-check harness's own declared 4-way change-label
macro-F1 proxy restricted to the participant-UNMENTIONED subset (the FOCUS metric --
this is where lexical extraction structurally cannot help and cross-step composition is
necessary; propara_trap_check.py's own docstring already declares this proxy is
"not the official leaderboard metric" but CITES the paper's own Cat-3 rule-based-vs-
ProGlobal collapse/recovery finding it corroborates) -- reported alongside the official
axis to show the two AGREE in direction (not asserted, MEASURED).

SCRAMBLE control (load-bearing): a deterministic (hashlib-seeded, no Python hash())
permutation of sentence order breaks (1) the BoW per-step retrieve-signal's alignment
to the true step, and (2) the existence-monotonicity VALIDATE ordering constraint
(CREATE-step < MOVE-steps < DESTROY-step no longer means textual/temporal precedence).
If reasoning's advantage were a fixed artifact (not genuine cross-step composition),
scramble would not move it. HARD-PASS requires scramble to collapse the reasoning arm's
edge toward the no-memory baseline.

Modes:
  --self-test  Tiny 2-paragraph synthetic smoke (real code path: real AccumulateRegister,
               real official_eval port, real sklearn fit) + arms-must-differ + verdict
               logic sanity. No queue dispatch, no file I/O beyond metrics.json.
  --smoke      Runs on the DEV split (43 paragraphs) -- used to CALIBRATE the HARD_PASS/
               HARD_FAIL bands actually shipped in --full (see prereg); 1 scramble seed.
  --full       Runs on the TEST split (54 paragraphs, the EMNLP18 held-out set) -- the
               decisive run. 3 scramble-permutation seeds (7, 17, 29), checkpointed via
               experiments/_seed_checkpoint.py (resumable per seed).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

ANCHOR_NAME = "propara_decisive_inference_arm1_oracle_v1"
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(REPO_ROOT)
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
import propara_official_eval as offeval  # noqa: E402  (tools/benchmark_trap_check)
from propara_trap_check import (  # noqa: E402  (tools/benchmark_trap_check; REUSE, not rebuild)
    load_jsonl,
    build_step_rows,
    build_paragraph_set_rows,
    fit_step_bow,
)
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics as _ckpt_write_metrics,
)

DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara")
LABELS = ["NONE", "CREATE", "MOVE", "DESTROY"]
MAX_STEPS = 16  # MEASURED@this session: true max across train/dev/test = 10; headroom kept
REG_DIM = 512   # AccumulateRegister FHRR dim; MEASURED@this session: decode fidelity 10/10
                # at n_events=10/entity, d=512 (well within the module's validated capacity,
                # docstring cites >=0.999 self-consistency at n_events=256/entity)
SEEDS_SMOKE = [7]
SEEDS_FULL = [7, 17, 29]

# HARD_PASS/HARD_FAIL bands: DEV-CALIBRATED (see prereg "Smoke findings" + "Calibration
# procedure"). MEASURED@data/exp_propara_decisive_inference_arm1_oracle_v1_smoke/metrics.json
# (dev, seed=7): natural_focus_margin=0.175, scramble_retained_frac=0.507, reasoning's OWN
# natural-vs-scramble relative drop=20.7%, official_overall_gap=0.218 -- all comfortably clear
# these bands with real margin, not razor-thin. Pinned here BEFORE --full touches TEST.
#
# Scramble-collapse rationale (NOT naive "must hit baseline exactly"): the oracle event
# MULTISET is paragraph-level and THEREFORE INVARIANT to sentence-order scramble by design
# (see reasoning_label_grids docstring) -- some residual advantage over baselines (which lack
# that oracle grant entirely) is STRUCTURALLY EXPECTED to survive scramble even with zero
# genuine temporal composition. A full collapse to the baseline floor is therefore NOT the
# right bar; two complementary signals are gated instead: (a) baseline-relative retained_frac
# must drop substantially (temporal composition contributes real, not 100%, of the win), AND
# (b) reasoning's OWN score (self, not vs. baseline) must ALSO drop meaningfully under
# scramble (a baseline-independent, oracle-count-confound-free composition-sensitivity check).
FOCUS_WIN_MARGIN_HARD_PASS = 0.03      # reasoning_focus_macro_f1 - max(baseline_focus_macro_f1) >=
FOCUS_WIN_MARGIN_HARD_FAIL = 0.00      # below this: no genuine win over the best baseline
SCRAMBLE_COLLAPSE_HARD_PASS = 0.65     # baseline-relative retained_frac <= this for HARD_PASS
SCRAMBLE_COLLAPSE_HARD_FAIL = 0.90     # baseline-relative retained_frac > this = did NOT collapse
SCRAMBLE_SELF_DROP_HARD_PASS_MIN = 0.10  # reasoning's OWN (natural-scramble)/natural relative drop >=
OFFICIAL_NO_REGRESSION_HARD_FAIL = -0.02  # reasoning official overall F1 - best baseline < this = regression


# ============================================================================ deterministic seeding (F.5: no hash())
def _det_seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 31 - 1)


def _deterministic_perm(key: str, n: int) -> List[int]:
    rng = random.Random(_det_seed(key))
    idx = list(range(n))
    rng.shuffle(idx)
    return idx


# ============================================================================ data prep
def _load_split(split: str):
    return load_jsonl(os.path.join(DATA_DIR, f"grids.v1.{split}.json"))


def _oracle_event_multiset(steps_df: pd.DataFrame) -> Dict[Tuple[str, str], Dict[str, int]]:
    """Per (para_id, participant): count of CREATE/MOVE/DESTROY events anywhere in the gold
    label sequence -- SAME oracle grant as the bag-of-existence baseline (does X ever get
    created/moved/destroyed), generalized from boolean to COUNT (a participant can move more
    than once). This is the "oracle structure" ARM1 input; NOT the per-step localization,
    which the reasoning arm must recover."""
    out: Dict[Tuple[str, str], Dict[str, int]] = {}
    for (para_id, participant), g in steps_df.groupby(["para_id", "participant"]):
        counts = {"CREATE": 0, "MOVE": 0, "DESTROY": 0}
        for lab in g.sort_values("step")["label"]:
            if lab in counts:
                counts[lab] += 1
        out[(para_id, participant)] = counts
    return out


# ============================================================================ arm: MAJORITY
def majority_label_grids(paragraphs: List[Dict]) -> Dict[str, Dict[str, List[str]]]:
    out = {}
    for para in paragraphs:
        n = len(para["sentence_texts"])
        out[para["para_id"]] = {p: ["NONE"] * n for p in para["participants"]}
    return out


# ============================================================================ arm: BoW / single-step (no memory)
def _bow_feature_matrix(vec, rows: List[Tuple[str, bool]]):
    from scipy.sparse import hstack, csr_matrix
    texts = [r[0] for r in rows]
    mentioned = np.array([[float(r[1])] for r in rows])
    X_text = vec.transform(texts)
    return hstack([X_text, csr_matrix(mentioned)]).tocsr()


def bow_label_grids(paragraphs: List[Dict], vec, clf) -> Dict[str, Dict[str, List[str]]]:
    out = {}
    for para in paragraphs:
        sents = para["sentence_texts"]
        grid = {}
        for participant in para["participants"]:
            part_tokens = set(participant.lower().replace(",", " ").split())
            rows = []
            for sent in sents:
                mentioned = bool(part_tokens & set(sent.lower().replace(".", " ").replace(",", " ").split()))
                rows.append((sent, mentioned))
            X = _bow_feature_matrix(vec, rows)
            preds = clf.predict(X)
            grid[participant] = list(preds)
        out[para["para_id"]] = grid
    return out


def _bow_step_probs(vec, clf, sents: List[str], participant: str) -> List[Dict[str, float]]:
    """Per-step predicted class probabilities for one participant (used as the RETRIEVE
    signal by the reasoning arm; reuses the SAME fitted classifier as the BoW baseline, not
    a new model)."""
    part_tokens = set(participant.lower().replace(",", " ").split())
    rows = []
    for sent in sents:
        mentioned = bool(part_tokens & set(sent.lower().replace(".", " ").replace(",", " ").split()))
        rows.append((sent, mentioned))
    X = _bow_feature_matrix(vec, rows)
    proba = clf.predict_proba(X)
    classes = list(clf.classes_)
    out = []
    for row in proba:
        out.append({classes[i]: float(row[i]) for i in range(len(classes))})
    return out


# ============================================================================ arm: BAG-OF-STATES (structure, no composition)
class _ConstantClassifier:
    """Fallback for a target with a single class in the training fold (e.g. a tiny
    self-test corpus where no participant ever MOVEs) -- mirrors propara_trap_check.
    fit_and_eval_bag_of_existence's existing 'skip: single_class_in_train' guard, but as a
    real predict()-able stub (this arm needs to predict on held-out paragraphs, not just
    report a score)."""
    def __init__(self, const: int):
        self.const = int(const)

    def predict(self, X):
        n = X.shape[0]
        return np.full(n, self.const, dtype=int)


def fit_bag_of_states_classifiers(train_set_df: pd.DataFrame) -> Dict[str, Tuple[object, object]]:
    """Genuinely-trained (NOT oracle) paragraph-level set classifiers, same recipe as
    propara_trap_check.fit_and_eval_bag_of_existence but returning the fitted (vec, clf)
    pair per target so this arm can PREDICT on held-out paragraphs, not just report a score.
    Single-class targets (e.g. a corpus where a type never occurs) fall back to
    _ConstantClassifier instead of raising -- LogisticRegression cannot fit one class."""
    out = {}
    for target in ["ever_create", "ever_move", "ever_destroy"]:
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        X = vec.fit_transform(train_set_df["full_text"].astype(str))
        y = train_set_df[target].astype(int).values
        if len(set(y.tolist())) < 2:
            out[target] = (vec, _ConstantClassifier(int(y[0]) if len(y) else 0))
            continue
        clf = LogisticRegression(max_iter=2000)
        clf.fit(X, y)
        out[target] = (vec, clf)
    return out


def bag_of_states_label_grids(paragraphs: List[Dict], bag_clfs: Dict[str, Tuple[object, object]]
                               ) -> Dict[str, Dict[str, List[str]]]:
    """Has STRUCTURE (predicted ever_create/ever_move/ever_destroy from genuinely-trained
    classifiers) but NO cross-step composition ability: places each predicted event at a
    FIXED, content-blind position (CREATE at step 1, DESTROY at the last step, one MOVE at
    the midpoint) -- deliberately incapable of localizing to the TRUE step, per the design
    note's baseline description ("has states, no cross-step composition")."""
    out = {}
    for para in paragraphs:
        n = len(para["sentence_texts"])
        full_text = " ".join(para["sentence_texts"])
        grid = {}
        for participant in para["participants"]:
            labels = ["NONE"] * n
            for target, tok, pos in [
                ("ever_create", "CREATE", 0),
                ("ever_destroy", "DESTROY", n - 1),
                ("ever_move", "MOVE", n // 2),
            ]:
                vec, clf = bag_clfs[target]
                X = vec.transform([full_text])
                pred = bool(clf.predict(X)[0])
                if pred and labels[pos] == "NONE":
                    labels[pos] = tok
            grid[participant] = labels
        out[para["para_id"]] = grid
    return out


# ============================================================================ arm: REASONING (retrieve-validate-advance + situation model)
def _assign_events_for_participant(pending_counts: Dict[str, int], step_probs: List[Dict[str, float]],
                                    n_steps: int) -> Dict[int, str]:
    """retrieve -> validate -> advance greedy assignment of oracle event-type tokens to
    steps, structurally modeled on exp_focus_pullin_causal_stage2a_multihop_loop_v1.run_loop
    (retrieve top candidate; validate against a constraint; advance / retry-exclude) --
    adapted from FHRR-codebook hop-retrieval to discrete oracle-count-constrained step
    assignment (a different embedding, same retrieve-validate-advance CONTROL-FLOW pattern;
    the literal reused ORGAN here is AccumulateRegister, wired in by the caller below).

    Processing order CREATE -> DESTROY -> MOVE(s) is the VALIDATE step: it enforces
    existence-monotonicity (create-step < move-steps < destroy-step) by construction, via a
    shrinking feasible [lo, hi] window, rather than post-hoc rejection -- CREATE pins the
    lower bound, DESTROY (searched next, within [lo, n_steps]) pins the upper bound, then
    MOVE(s) are placed inside the resulting window. Steps are picked (RETRIEVE) by ranking
    the remaining, unused candidate steps by the BoW classifier's predicted probability for
    that event type (descending); ADVANCE = commit the top candidate and shrink the window."""
    assigned: Dict[int, str] = {}
    used: set = set()
    lo, hi = 1, n_steps
    order = (["CREATE"] * min(pending_counts.get("CREATE", 0), 1)
             + ["DESTROY"] * min(pending_counts.get("DESTROY", 0), 1)
             + ["MOVE"] * pending_counts.get("MOVE", 0))
    for tok in order:
        candidates = [s for s in range(lo, hi + 1) if s not in used]
        if not candidates:
            continue
        candidates.sort(key=lambda s: -step_probs[s - 1].get(tok, 0.0))
        chosen = candidates[0]
        assigned[chosen] = tok
        used.add(chosen)
        if tok == "CREATE":
            lo = max(lo, chosen + 1)
        elif tok == "DESTROY":
            hi = min(hi, chosen - 1)
    return assigned


def reasoning_label_grids(paragraphs: List[Dict], vec, clf, oracle_multiset: Dict[Tuple[str, str], Dict[str, int]],
                           scramble: bool = False, scramble_seed: int = 0
                           ) -> Tuple[Dict[str, Dict[str, List[str]]], Dict[str, float]]:
    """The decisive ARM1 mechanism: oracle event MULTISET (structure) + per-step BoW retrieve
    signal + validate-ordering-constrained greedy localization, wired through a per-paragraph
    hdlab.situation_model_accumulate.AccumulateRegister (bind role=predicted_label to
    event_idx=step for EVERY step of EVERY participant; final prediction = FHRR decode, not
    the plain-Python dict directly -- proves the organ is actually load-bearing, not
    decorative). scramble=True permutes sentence order (deterministic, hashlib-seeded) before
    computing the BoW retrieve signal AND before recomputing 'mentioned' -- the oracle
    multiset itself is paragraph-level and therefore UNCHANGED by scramble (only the
    LOCALIZATION signal degrades)."""
    out: Dict[str, Dict[str, List[str]]] = {}
    decode_checks = {"n": 0, "match": 0}
    for para in paragraphs:
        para_id = para["para_id"]
        sents = para["sentence_texts"]
        n = len(sents)
        if scramble:
            perm = _deterministic_perm(f"scramble_{scramble_seed}_{para_id}", n)
            sents_for_signal = [sents[i] for i in perm]
        else:
            sents_for_signal = sents

        gen = torch.Generator()
        gen.manual_seed(_det_seed(f"situation_model_{para_id}"))
        reg = AccumulateRegister(role_vocab=LABELS, d=REG_DIM, generator=gen, max_event_slots=MAX_STEPS)

        grid = {}
        for participant in para["participants"]:
            counts = oracle_multiset.get((para_id, participant), {"CREATE": 0, "MOVE": 0, "DESTROY": 0})
            step_probs = _bow_step_probs(vec, clf, sents_for_signal, participant)
            assigned = _assign_events_for_participant(counts, step_probs, n)
            final_labels = [assigned.get(t, "NONE") for t in range(1, n + 1)]

            for t in range(1, n + 1):
                reg.add_event(participant, final_labels[t - 1], t - 1)
            decoded = []
            for t in range(1, n + 1):
                lab, _scores = reg.decode(participant, t - 1)
                decoded.append(lab)
                decode_checks["n"] += 1
                decode_checks["match"] += int(lab == final_labels[t - 1])
            grid[participant] = decoded
        out[para_id] = grid
    fidelity = decode_checks["match"] / max(decode_checks["n"], 1)
    return out, {"decode_fidelity": fidelity, "n_decoded": decode_checks["n"]}


# ============================================================================ scoring: official metric
def _official_corpus_scores(paragraphs: List[Dict], label_grids: Dict[str, Dict[str, List[str]]]) -> Dict:
    answers, predictions = {}, {}
    for para in paragraphs:
        pid = para["para_id"]
        answers[pid] = offeval.process_summary_from_gold_states(pid, para["participants"], para["states"])
        n_steps = len(para["sentence_texts"])
        predictions[pid] = offeval.process_summary_from_labels(pid, label_grids[pid], n_steps)
    return offeval.corpus_evaluation(answers, predictions)


# ============================================================================ scoring: proxy 4-way macro-F1 (mentioned/unmentioned)
def _proxy_scores(steps_df: pd.DataFrame, label_grids: Dict[str, Dict[str, List[str]]]) -> Dict:
    pred_lookup: Dict[Tuple[str, str, int], str] = {}
    for para_id, grid in label_grids.items():
        for participant, labels in grid.items():
            for i, lab in enumerate(labels):
                pred_lookup[(para_id, participant, i + 1)] = lab
    preds = np.array([pred_lookup[(r.para_id, r.participant, r.step)] for r in steps_df.itertuples()])
    gold = steps_df["label"].values
    mentioned_mask = steps_df["mentioned"].values

    def _blk(mask):
        if mask.sum() == 0:
            return {"n": 0}
        p, g = preds[mask], gold[mask]
        return {"n": int(mask.sum()), "accuracy": float((p == g).mean()),
                "macro_f1": float(f1_score(g, p, labels=LABELS, average="macro", zero_division=0))}

    return {"overall": _blk(np.ones(len(steps_df), dtype=bool)),
            "mentioned": _blk(mentioned_mask), "unmentioned": _blk(~mentioned_mask)}


# ============================================================================ arms-must-differ (META_RULE_AF)
def _arms_must_differ(label_grids_by_arm: Dict[str, Dict[str, Dict[str, List[str]]]]) -> Dict:
    def _digest(grid):
        b = json.dumps(grid, sort_keys=True).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    sigs = {arm: _digest(g) for arm, g in label_grids_by_arm.items()}
    pairs = {f"{a}_vs_{b}": sigs[a] != sigs[b]
             for i, a in enumerate(sigs) for b in list(sigs)[i + 1:]}
    return {"sigs": sigs, "pairs_differ": pairs, "all_differ": all(pairs.values())}


# ============================================================================ one full evaluation pass over a split
def run_split(split: str, train_paragraphs: List[Dict], scramble_seed: int = 7) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    train_set_df = build_paragraph_set_rows(train_paragraphs)

    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)  # oracle over the SPLIT's OWN gold (ARM1 grant)

    grids: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
    grids["majority"] = majority_label_grids(paragraphs)
    grids["bow_singlestep"] = bow_label_grids(paragraphs, vec, clf)
    grids["bagstates"] = bag_of_states_label_grids(paragraphs, bag_clfs)
    grids["reasoning"], reasoning_diag = reasoning_label_grids(paragraphs, vec, clf, oracle_multiset, scramble=False)
    perm_key = f"seed{scramble_seed}"
    grids[f"reasoning_scramble_{perm_key}"], scramble_diag = reasoning_label_grids(
        paragraphs, vec, clf, oracle_multiset, scramble=True, scramble_seed=scramble_seed)

    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    diff = _arms_must_differ({"majority": grids["majority"], "bow_singlestep": grids["bow_singlestep"],
                              "bagstates": grids["bagstates"], "reasoning": grids["reasoning"],
                              "reasoning_scramble": grids[f"reasoning_scramble_{perm_key}"]})

    baseline_focus_f1 = max(proxy[a]["unmentioned"].get("macro_f1", 0.0) for a in ("majority", "bow_singlestep", "bagstates"))
    reasoning_focus_f1 = proxy["reasoning"]["unmentioned"].get("macro_f1", 0.0)
    scramble_focus_f1 = proxy[f"reasoning_scramble_{perm_key}"]["unmentioned"].get("macro_f1", 0.0)
    natural_margin = reasoning_focus_f1 - baseline_focus_f1
    scramble_margin = scramble_focus_f1 - baseline_focus_f1
    scramble_retained_frac = (scramble_margin / natural_margin) if abs(natural_margin) > 1e-9 else None
    # baseline-independent composition-sensitivity check: does reasoning's OWN score drop under
    # scramble (free of the oracle-multiset-is-scramble-invariant confound in retained_frac above)
    scramble_self_drop_frac = ((reasoning_focus_f1 - scramble_focus_f1) / reasoning_focus_f1
                                if abs(reasoning_focus_f1) > 1e-9 else None)

    baseline_official_overall = max(official[a]["overall"]["f1"] for a in ("majority", "bow_singlestep", "bagstates"))
    reasoning_official_overall = official["reasoning"]["overall"]["f1"]

    elapsed = time.time() - t0
    return {
        "split": split, "scramble_seed": scramble_seed, "elapsed_s": round(elapsed, 3),
        "n_paragraphs": len(paragraphs), "n_step_rows": int(len(steps_df)),
        "grids_digest": diff["sigs"], "arms_differ": diff,
        "reasoning_decode_diag": reasoning_diag, "scramble_decode_diag": scramble_diag,
        "official": official, "proxy": proxy,
        "baseline_focus_macro_f1": baseline_focus_f1, "reasoning_focus_macro_f1": reasoning_focus_f1,
        "scramble_focus_macro_f1": scramble_focus_f1,
        "natural_focus_margin": natural_margin, "scramble_focus_margin": scramble_margin,
        "scramble_retained_frac": scramble_retained_frac,
        "scramble_self_drop_frac": scramble_self_drop_frac,
        "baseline_official_overall_f1": baseline_official_overall,
        "reasoning_official_overall_f1": reasoning_official_overall,
        "official_overall_gap": reasoning_official_overall - baseline_official_overall,
    }


# ============================================================================ verdict logic
def seed_verdict(result: Dict) -> Tuple[str, str]:
    focus_margin = result["natural_focus_margin"]
    scramble_frac = result["scramble_retained_frac"]
    self_drop = result.get("scramble_self_drop_frac")
    official_gap = result["official_overall_gap"]
    decode_ok = (result["reasoning_decode_diag"]["decode_fidelity"] >= 0.99
                and result["scramble_decode_diag"]["decode_fidelity"] >= 0.99)
    arms_ok = result["arms_differ"]["all_differ"]

    scramble_collapsed = (scramble_frac is not None and scramble_frac <= SCRAMBLE_COLLAPSE_HARD_PASS
                          and self_drop is not None and self_drop >= SCRAMBLE_SELF_DROP_HARD_PASS_MIN)
    scramble_failed_to_collapse = (scramble_frac is not None and scramble_frac > SCRAMBLE_COLLAPSE_HARD_FAIL)

    hard_fail = ((not arms_ok) or (not decode_ok)
                or (focus_margin < FOCUS_WIN_MARGIN_HARD_FAIL)
                or (official_gap < OFFICIAL_NO_REGRESSION_HARD_FAIL)
                or scramble_failed_to_collapse)
    hard_pass = (arms_ok and decode_ok and focus_margin >= FOCUS_WIN_MARGIN_HARD_PASS
                and official_gap >= 0.0 and scramble_collapsed)

    msg = (f"split={result['split']} seed={result['scramble_seed']} "
          f"focus_margin={focus_margin:.4f}(>= {FOCUS_WIN_MARGIN_HARD_PASS} for HP, "
          f"< {FOCUS_WIN_MARGIN_HARD_FAIL} for HF) "
          f"scramble_retained_frac={scramble_frac} (<= {SCRAMBLE_COLLAPSE_HARD_PASS} for HP collapse, "
          f"> {SCRAMBLE_COLLAPSE_HARD_FAIL} for HF-no-collapse) "
          f"scramble_self_drop_frac={self_drop} (>= {SCRAMBLE_SELF_DROP_HARD_PASS_MIN} for HP collapse) "
          f"official_overall_gap={official_gap:.4f}(>=0 for HP, >= {OFFICIAL_NO_REGRESSION_HARD_FAIL} else HF) "
          f"decode_ok={decode_ok} arms_ok={arms_ok}")

    if hard_fail:
        return "HARD_FAIL", f"HARD_FAIL: {msg}"
    if hard_pass:
        return "HARD_PASS", f"HARD_PASS: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND: {msg}"


def combine_verdicts(per_seed_verdicts: List[str]) -> Tuple[str, str]:
    if any(v == "HARD_FAIL" for v in per_seed_verdicts):
        return "HARD_FAIL", f"OVERALL_HARD_FAIL: >=1 seed HARD_FAIL ({per_seed_verdicts})"
    if all(v == "HARD_PASS" for v in per_seed_verdicts):
        return "HARD_PASS", f"OVERALL_HARD_PASS: all {len(per_seed_verdicts)} seeds HARD_PASS"
    return "MIDDLE_BAND", f"OVERALL_MIDDLE_BAND: mixed seed verdicts ({per_seed_verdicts})"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> Dict:
    """Real-code-path check on a tiny 2-paragraph synthetic corpus: official_eval's OWN
    self_test() (bit-exact official-fixture regression), the full run_split() pipeline
    (real AccumulateRegister, real sklearn fit, real official-metric scoring), arms-must-
    differ, decode fidelity, and verdict-logic sanity."""
    off_result = offeval.self_test()

    synth_paras = [
        {"para_id": "s1", "sentence_texts": [
            "A seed is planted in soil.", "Water is added.", "The seed germinates.",
            "Roots grow into the soil.", "The plant grows tall."],
         "participants": ["seed", "water", "root"],
         "states": [
             ["-", "soil", "soil", "soil", "soil", "-"],   # seed: CREATE,NONE,NONE,NONE,DESTROY
             ["-", "-", "pot", "soil", "soil", "soil"],    # water: NONE,CREATE,MOVE,NONE,NONE
             ["-", "-", "-", "soil", "soil", "soil"],      # root: NONE,NONE,CREATE,NONE,NONE
         ]},
        {"para_id": "s2", "sentence_texts": [
            "Clouds form in the sky.", "Rain falls to earth.", "The rain soaks into ground."],
         "participants": ["cloud"],
         "states": [["-", "sky", "sky", "-"]]},          # cloud: CREATE, NONE, DESTROY
    ]
    train_paras = synth_paras  # tiny self-test: train on itself (real_code_path, not accuracy claim)

    steps_df = build_step_rows(synth_paras)
    train_steps_df = build_step_rows(train_paras)
    train_set_df = build_paragraph_set_rows(train_paras)
    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)

    grids = {}
    grids["majority"] = majority_label_grids(synth_paras)
    grids["bow_singlestep"] = bow_label_grids(synth_paras, vec, clf)
    grids["bagstates"] = bag_of_states_label_grids(synth_paras, bag_clfs)
    grids["reasoning"], reasoning_diag = reasoning_label_grids(synth_paras, vec, clf, oracle_multiset, scramble=False)
    grids["reasoning_scramble"], scramble_diag = reasoning_label_grids(synth_paras, vec, clf, oracle_multiset, scramble=True)

    assert reasoning_diag["decode_fidelity"] == 1.0, f"DECODE_FIDELITY_FAIL: {reasoning_diag}"
    assert scramble_diag["decode_fidelity"] == 1.0, f"SCRAMBLE_DECODE_FIDELITY_FAIL: {scramble_diag}"

    # oracle event multiset sanity: seed has exactly 1 CREATE + 1 DESTROY, 0 MOVE
    assert oracle_multiset[("s1", "seed")] == {"CREATE": 1, "MOVE": 0, "DESTROY": 1}, oracle_multiset[("s1", "seed")]
    # STRUCTURAL invariants the VALIDATE step guarantees regardless of the (noisy, tiny-N-
    # trained) BoW retrieve ranking -- exact step PLACEMENT is a statistical claim tested on
    # real dev/test data at --smoke/--full scale, not something a 2-paragraph self-test
    # corpus can pin deterministically (the fitted classifier at this scale is not reliable
    # enough to hand-predict its exact ranking; asserting a specific step would make the
    # self-test brittle to incidental classifier noise, not a real bug signal).
    seed_labels = grids["reasoning"]["s1"]["seed"]
    assert seed_labels.count("CREATE") == 1 and seed_labels.count("DESTROY") == 1, seed_labels
    assert seed_labels.index("CREATE") < seed_labels.index("DESTROY"), (
        f"VALIDATE_ORDERING_VIOLATION seed: {seed_labels}")
    # water exercises the MOVE branch: oracle gives 1 CREATE + 1 MOVE, 0 DESTROY
    assert oracle_multiset[("s1", "water")] == {"CREATE": 1, "MOVE": 1, "DESTROY": 0}, oracle_multiset[("s1", "water")]
    water_labels = grids["reasoning"]["s1"]["water"]
    assert water_labels.count("CREATE") == 1 and water_labels.count("MOVE") == 1, water_labels
    assert water_labels.index("CREATE") < water_labels.index("MOVE"), (
        f"VALIDATE_ORDERING_VIOLATION water: {water_labels}")

    official = {arm: _official_corpus_scores(synth_paras, g) for arm, g in grids.items()}
    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    diff = _arms_must_differ(grids)
    assert diff["all_differ"], f"ARMS_IDENTICAL: {diff}"

    # verdict-logic unit checks
    hf_result = {"split": "x", "scramble_seed": 0, "natural_focus_margin": -0.10,
                 "scramble_retained_frac": 0.5, "official_overall_gap": 0.0,
                 "reasoning_decode_diag": {"decode_fidelity": 1.0}, "scramble_decode_diag": {"decode_fidelity": 1.0},
                 "arms_differ": {"all_differ": True}}
    hf_v, _ = seed_verdict(hf_result)
    assert hf_v == "HARD_FAIL", hf_v  # negative focus margin forces HARD_FAIL

    hp_result = {"split": "x", "scramble_seed": 0, "natural_focus_margin": 0.15,
                 "scramble_retained_frac": 0.10, "scramble_self_drop_frac": 0.50, "official_overall_gap": 0.02,
                 "reasoning_decode_diag": {"decode_fidelity": 1.0}, "scramble_decode_diag": {"decode_fidelity": 1.0},
                 "arms_differ": {"all_differ": True}}
    hp_v, _ = seed_verdict(hp_result)
    assert hp_v == "HARD_PASS", hp_v

    # a case that retains a LOW baseline-relative fraction but where reasoning's OWN score
    # barely moves (self_drop below the minimum) must NOT be HARD_PASS -- this is exactly the
    # scenario the self-drop gate exists to catch (the oracle-count-confound false collapse).
    mb_result = {"split": "x", "scramble_seed": 0, "natural_focus_margin": 0.15,
                 "scramble_retained_frac": 0.10, "scramble_self_drop_frac": 0.01, "official_overall_gap": 0.02,
                 "reasoning_decode_diag": {"decode_fidelity": 1.0}, "scramble_decode_diag": {"decode_fidelity": 1.0},
                 "arms_differ": {"all_differ": True}}
    mb_v, _ = seed_verdict(mb_result)
    assert mb_v == "MIDDLE_BAND", mb_v

    return {"official_eval_self_test": {"n_fixtures_checked": len(off_result["official_fixtures"]),
                                        "fixtures_ok": True},
            "oracle_multiset_check": oracle_multiset[("s1", "seed")],
            "reasoning_decode_diag": reasoning_diag, "scramble_decode_diag": scramble_diag,
            "arms_differ_check": diff,
            "official_summary": {arm: official[arm]["overall"] for arm in official},
            "proxy_summary": {arm: proxy[arm]["unmentioned"] for arm in proxy},
            "verdict_logic_unit_checks": {"hard_fail_case": hf_v, "hard_pass_case": hp_v,
                                          "self_drop_confound_case": mb_v}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str)[:8000])
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    split = "dev" if args.smoke else "test"
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    expected_units = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    train_paragraphs = _load_split("train")
    run_config = {"run_mode": run_mode, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(seeds, output_dir, run_config=run_config)
    print(f"[{run_mode}] split={split} {len(done)}/{len(seeds)} seeds already complete; running {remaining}",
        flush=True)

    for i, seed in enumerate(remaining):
        print(f"[{run_mode}] seed={seed} running on split={split}...", flush=True)
        result = run_split(split, train_paragraphs, scramble_seed=seed)
        verdict, msg = seed_verdict(result)
        payload = {"seed": seed, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
                  "config_version": f"ANCHOR={ANCHOR_NAME},split={split}",
                  "verdict": verdict, "verdict_msg": msg, "result": result}
        write_partial(output_dir, seed, payload)
        print(f"[{run_mode}] seed={seed} {verdict}: {msg}", flush=True)
        _write_heartbeat(output_dir, len(done) + i + 1, expected_units, time.time() - t0)

    per_seed = aggregate_partials(output_dir, seeds, run_config=run_config)
    per_seed_verdicts = [per_seed[str(s)]["verdict"] for s in seeds]
    overall_verdict, overall_msg = combine_verdicts(per_seed_verdicts)

    elapsed = time.time() - t0
    per_seed_summary = {
        s: {"verdict": per_seed[str(s)]["verdict"],
            "natural_focus_margin": per_seed[str(s)]["result"]["natural_focus_margin"],
            "scramble_retained_frac": per_seed[str(s)]["result"]["scramble_retained_frac"],
            "official_overall_gap": per_seed[str(s)]["result"]["official_overall_gap"],
            "baseline_focus_macro_f1": per_seed[str(s)]["result"]["baseline_focus_macro_f1"],
            "reasoning_focus_macro_f1": per_seed[str(s)]["result"]["reasoning_focus_macro_f1"],
            "scramble_focus_macro_f1": per_seed[str(s)]["result"]["scramble_focus_macro_f1"],
            "official": {arm: per_seed[str(s)]["result"]["official"][arm]["overall"]
                        for arm in per_seed[str(s)]["result"]["official"]}}
        for s in seeds}

    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "seeds": seeds, "per_seed_verdicts": dict(zip([str(s) for s in seeds], per_seed_verdicts)),
        "per_seed_summary": per_seed_summary,
        "per_seed_full": {k: v for k, v in per_seed.items()},
        "cardinality_ok": len(per_seed) == expected_units, "expected_n_units": expected_units,
        "cell_chunked": True, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "accuracy/F1-comparison ablation over a fixed real corpus (ProPara EMNLP18); "
                    "no capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: HARD_PASS/HARD_FAIL bands calibrated from "
                            "--smoke DEV-set numbers (see prereg), applied unchanged to --full TEST; "
                            "no test-set peeking",
        "bands": {"FOCUS_WIN_MARGIN_HARD_PASS": FOCUS_WIN_MARGIN_HARD_PASS,
                  "FOCUS_WIN_MARGIN_HARD_FAIL": FOCUS_WIN_MARGIN_HARD_FAIL,
                  "SCRAMBLE_COLLAPSE_HARD_PASS": SCRAMBLE_COLLAPSE_HARD_PASS,
                  "SCRAMBLE_COLLAPSE_HARD_FAIL": SCRAMBLE_COLLAPSE_HARD_FAIL,
                  "OFFICIAL_NO_REGRESSION_HARD_FAIL": OFFICIAL_NO_REGRESSION_HARD_FAIL},
    }
    _ckpt_write_metrics(
        Path(output_dir), metrics,
        results=[{"elapsed_s": per_seed[str(s)]["result"]["elapsed_s"]} for s in seeds])
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_seed_full",)}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
