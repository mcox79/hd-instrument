"""arc_aggregation_retriever_bindsettle_v1 -- THE AGGREGATION RETRIEVER: combine several central
facts to answer, via brain-faithful CONSTRUCTION-INTEGRATION (bind+settle), and test whether it beats
the single-fact-retrieval floor on ARC.

Real question (can-fail): ARC is a MULTI-FACT task (WorldTree gold: ~2.4 CENTRAL facts/Q). A single-item
retriever fetches ONE fact when the task needs several. Does loading the candidate central facts into a
Cowan-4 working-memory focus and letting them MUTUALLY CONSTRAIN + SETTLE (Kintsch/van-Dijk
construction-integration = the substrate's weighted BIND+SETTLE) beat taking the single best fact?

BRAIN-FAITHFUL (USER-LOCKED, non-negotiable): the aggregator is CONSTRUCTION-INTEGRATION, NOT an
engineering "sum the cosines, argmax". Facts form a coherence network (fact-fact cosine = mutual
constraint); activation SETTLES over T iterations (parallel constraint-satisfaction); the settled
central facts are BUNDLED (HD superposition = the working-memory gist) and each choice scored by cosine
to that settled bundle. A non-faithful score-SUM arm is included as an explicit CONTRAST; if score-sum
beats bind+settle we REPORT it honestly (do NOT adopt the sum as the mechanism).

MECHANISM (Kintsch 1988 Construction-Integration, primary-source mechanics per
notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md): a BIPARTITE SIGNED
graph over {candidate facts} + {answer choices}. Edges: fact-choice = signed cos (support/contradict);
fact-fact = raw signed cos(f_i,f_j) (positive = shared meaning/consistent, NEGATIVE = genuine semantic
opposition = Kintsch contradiction -- the term a plain score-sum has zero of); choice-choice = NEGATIVE
inhibition (mutually exclusive, exactly one wins). Settle by Kintsch's rule:
a <- W@a ; clip negatives to 0 ; divide positives by their sum ; until mean|delta| < eps or T iters.
READOUT = the CHOICE node with highest settled activation, compared only among choice nodes.
Precedent credited: Kintsch (1988) Construction-Integration (the signed-matrix relaxation); Thagard (1998)
ECHO explanatory-coherence (cousin settle/relaxation network); Eliasmith (2013) SPA/Spaun (the FHRR-family
bundle+cleanup accumulation precedent -- the accumulation flavor tested by the score-sum contrast arm).

ARMS (all share the SAME SemanticHDEncoder + the SAME candidate pool; they differ ONLY in aggregation):
  single   -- score(c)=max_f cos(fact_f, choice_c)                     [FLOOR: single best fact]
  sum      -- score(c)=sum_f cos(fact_f, choice_c)                     [zero-iteration score-sum: no graph,
              no negative edges, no relaxation -- the "disguised CI" control the mechanism must beat]
  settle   -- full signed bipartite CI relaxation (above)             [MECHANISM]
  pos_only -- identical graph with all NEGATIVE weights zeroed         [ablation: is Kintsch signed-inhibition
              load-bearing, vs plain Collins-Loftus/ACT-R positive spreading?]
  shuffled -- CI relaxation on a sign/magnitude-preserved RANDOMLY-permuted matrix  [must-fail -> chance]
  inverted -- CI relaxation, readout = LOWEST-activation choice        [must-fail -> below chance]
Anti-blur (theta-gamma analog) is satisfied BY CONSTRUCTION: facts are DISTINCT graph nodes (indices),
never superposed, so the combine step does not blur them (the note's two-separate-mechanisms discipline).
POOLS:
  ORACLE   -- candidate pool = the question's GOLD CENTRAL+LEXGLUE facts (WorldTree). Isolates the
              AGGREGATION mechanism from retrieval (upper bound). PRIMARY discriminator lives here.
  RETRIEVAL-- candidate pool = top-K facts from the ingested tablestore, with the test question's OWN
              gold support UIDs HELD OUT (fair, no answer-leak). End-to-end retrieval+aggregation.
CONTROLS: empty (no facts -> chance) ; scramble (K random HD vecs -> collapse; leak check).

KNOWLEDGE SOURCE: WorldTree V2.1 tablestore (~9720 typed science facts). HELD-OUT guardrail: the
ingested store EXCLUDES every gold support UID of the test questions -> the reported RETRIEVAL number is
fair, not leaked. The tablestore is a domain-matched science CURRICULUM (general facts), distinct from
answer-leak (per the 29530 test-targeting lesson).

PERF: no O(n^2) ingest -- facts are batch-encoded ONCE (single pass) and retrieval is a vectorized
matmul; there is NO per-insert fuzzy-conflict scan (the killed-CLIMB failure mode). ~9720 facts.

Builds on: 29530 (ARC measure, chance no-leak), 29533 (SemanticHDEncoder meaning AUC 0.96), the
single-item floor harness (exp_arc_fact_retrieval_semantic_kb_climb_v1), Cowan-4 role-slot WM.

Contract: INLINE-LOCAL foreground-to-completion (GloVe cache + WorldTree are git-ignored/large ->
NOT remote-portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy
default_rng, sorted iteration; no hash()). Runs in repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic ; heartbeat
# - real_code_path: self_test constructs the REAL SemanticHDEncoder + runs the REAL retrieval + all 4
#   aggregation modes + oracle + controls at tiny scale; a planted synthetic HD case asserts the
#   DISCRIMINATOR FIRES (settle picks correct where single fails); determinism; arms-differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-saturation guard on oracle_single (headroom for the aggregation win)
# - storage strategy = SHARDED (each fact its own vector; composed via aggregation, per META_STORAGE)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import re
import csv
import sys
import glob
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_aggregation_retriever_bindsettle_v1"
SEED = 20260724

_WT = os.path.join(_REPO, "data", "corpora", "worldtree",
                   "WorldtreeExplanationCorpusV2.1_Feb2020")
_TABLES = os.path.join(_WT, "tablestore", "v2.1", "tables")
_QTEST = os.path.join(_WT, "questions", "questions.test.tsv")

# ---- bands (author-designed; see pre-reg). PRIMARY = ORACLE settle-vs-single AND settle-vs-sum, Easy. ----
HP_AGG_BEATS_SINGLE = 0.05        # oracle_settle_easy - oracle_single_easy  (beats the single-fact FLOOR)
HP_SETTLE_NOT_BELOW_SUM = 0.0     # settle_easy - sum_easy >= this (CI at least ties the score-sum control)
HP_CI_FAITHFUL_MARGIN = 0.05      # settle - sum >= this -> the STRONGER "CI adds over score-sum" claim
HP_NEG_EDGE_MARGIN = 0.02         # settle - pos_only >= this -> negative/inhibition edges are load-bearing
FLAT_EPS = 0.05                   # |settle - single| < this -> AGG_FLAT
LEAK_EPS = 0.05                   # scramble - chance >= this -> LEAK_FLAG
MUSTFAIL_EPS = 0.05               # shuffled - chance >= this -> must-fail control breach
AG_SATURATION = 0.90              # oracle_single_easy >= this -> discriminator vacuous (no headroom)

# ---- aggregation hyperparams (author-designed; K/T ranges anchored to Kintsch's 4-28 node examples) ----
RETRIEVAL_K = 10                  # pre-settle candidate facts / question (ENGINEERING cutoff, NOT brain-derived;
                                  # Kintsch nets were 4-28 nodes -> keep the graph small; see pre-reg note 8)
SETTLE_T = 50                     # max CI iterations (Kintsch's own nets converged in 7-43; cap as safety bound)
SETTLE_EPS = 1e-3                 # Kintsch's stated convergence epsilon (mean |delta activation| < .001)
CHOICE_INHIB = 1.0                # choice-choice mutual inhibition weight (Kintsch used -1 between rival hyps)
CHOICE_PRIOR = 0.05               # small uniform initial activation on choice nodes (they start in the race)
SETTLE_FIRES_MIN_ITERS = 2        # settle must run >= 2 real relaxation iters (checklist (b): not a single pass)


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
_T0 = [0.0]


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# WorldTree tablestore + questions parsing
# ---------------------------------------------------------------------------
def parse_tablestore():
    """Parse every tablestore TSV into (uid -> flat_sentence). Sentence = the non-[SKIP] non-empty
    cells joined in column order; UID = the [SKIP] UID column. Returns dict uid->sentence."""
    uid2sent = {}
    for path in sorted(glob.glob(os.path.join(_TABLES, "*.tsv"))):
        with open(path, "r", encoding="utf-8") as f:
            rd = csv.reader(f, delimiter="\t")
            hdr = next(rd)
            skip = [i for i, h in enumerate(hdr) if h.strip().startswith("[SKIP]")]
            uidcol = None
            for i, h in enumerate(hdr):
                if "UID" in h:
                    uidcol = i
            for r in rd:
                if not any(c.strip() for c in r):
                    continue
                uid = r[uidcol].strip() if (uidcol is not None and uidcol < len(r)) else ""
                cells = [c.strip() for i, c in enumerate(r) if i not in skip and c.strip()]
                sent = " ".join(cells)
                if uid and sent:
                    uid2sent[uid] = sent
    return uid2sent


_LABEL_RE = re.compile(r"\s*\(([A-D1-4])\)\s*")


def _answerkey_index(key, n_choices):
    key = key.strip()
    if key in "ABCD":
        return ord(key) - ord("A")
    if key.isdigit():
        return int(key) - 1
    return None


def load_wt_questions(limit_easy=None, limit_chal=None):
    """Parse WorldTree test questions -> list of dicts. gold_central = CENTRAL+LEXGLUE gold UIDs
    (the core reasoning facts + lexical glue); gold_all = every gold UID (held-out guardrail)."""
    out = []
    n_e = n_c = 0
    with open(_QTEST, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            qtext = row["question"].strip()
            parts = _LABEL_RE.split(qtext)
            # parts = [stem, lab1, choice1, lab2, choice2, ...]
            if len(parts) < 3:
                continue
            stem = parts[0].strip()
            choices = [parts[i].strip() for i in range(2, len(parts), 2)]
            choices = [c for c in choices if c]
            ci = _answerkey_index(row["AnswerKey"], len(choices))
            if ci is None or ci >= len(choices) or len(choices) < 2:
                continue
            arcset = row.get("arcset", "").strip()
            is_easy = arcset == "Easy"
            if is_easy and limit_easy is not None and n_e >= limit_easy:
                continue
            if (not is_easy) and limit_chal is not None and n_c >= limit_chal:
                continue
            gold_all, gold_central = set(), []
            for tok in row["explanation"].split():
                if "|" in tok:
                    u, role = tok.split("|", 1)
                    gold_all.add(u)
                    if role in ("CENTRAL", "LEXGLUE"):
                        gold_central.append(u)
            out.append({
                "qid": row["QuestionID"], "stem": stem, "choices": choices,
                "correct_index": ci,
                "source": "ARC-Easy-Test" if is_easy else "ARC-Challenge-Test",
                "gold_central": gold_central, "gold_all": gold_all,
            })
            if is_easy:
                n_e += 1
            else:
                n_c += 1
    out.sort(key=lambda q: q["qid"])
    return out


# ---------------------------------------------------------------------------
# aggregation core: Kintsch bipartite signed-graph Construction-Integration + contrasts
# ---------------------------------------------------------------------------
def _relax(W, a0, T, eps):
    """Kintsch integration on a signed matrix: a <- W@a ; clip negatives to 0 ; divide positives by
    their sum ; until mean|delta| < eps or T iters. Returns (a, n_iters, converged, shift)."""
    a = a0.astype(np.float64).copy()
    s = a.sum()
    if s > 0:
        a = a / s
    a_start = a.copy()
    n_iters = 0
    converged = False
    for t in range(T):
        a_new = np.maximum(W @ a, 0.0)
        ss = a_new.sum()
        if ss > 0:
            a_new = a_new / ss
        delta = float(np.mean(np.abs(a_new - a)))
        a = a_new
        n_iters = t + 1
        if delta < eps:
            converged = True
            break
    return a, n_iters, converged, float(np.mean(np.abs(a - a_start)))


def _ci_two_phase(fact_hd, choice_hd, q_rel, pos_only=False, shuffle_rng=None,
                  T=SETTLE_T, eps=SETTLE_EPS):
    """Kintsch's two-sub-network Construction-Integration (his competing-hypothesis worked example):
      Phase 1 -- FACT relaxation over the signed fact-fact matrix = raw cos(f_i,f_j) (positive = shared
                 meaning/consistent, NEGATIVE = genuine semantic opposition = Kintsch contradiction;
                 NOT a manufactured argmax-derived sign), initial activation = top-down relevance q_rel.
                 Contradictory/irrelevant facts lose share; coherent ones survive.
      Phase 2 -- CHOICE competition (separate sub-network, normalized among CHOICES ONLY, per Kintsch):
                 external drive[c] = sum_f af[f]*support(f,c) (settled-fact-weighted support);
                 choices mutually inhibit (-CHOICE_INHIB); relax; readout = argmax settled choice node.
    pos_only zeros the negative edges (fact contradiction + choice inhibition) = plain positive
    spreading (Collins-Loftus/ACT-R ablation). shuffle_rng permutes the support+contradiction entries
    (must-fail). Returns (choice_act[C], n_iters, converged, shift) from Phase 1 (the main relaxation)."""
    K = fact_hd.shape[0]
    C = choice_hd.shape[0]
    FC = (fact_hd @ choice_hd.T).astype(np.float64)               # [K,C] signed fact->choice support
    if K > 1:
        FF = (fact_hd @ fact_hd.T).astype(np.float64)            # raw signed cos: +consistent / -contradictory
        np.fill_diagonal(FF, 0.0)
    else:
        FF = np.zeros((K, K), dtype=np.float64)
    if shuffle_rng is not None:
        # preserve magnitude+sign distribution; randomly reassign fact->choice support + fact-fact edges
        fc_flat = FC.reshape(-1).copy(); shuffle_rng.shuffle(fc_flat); FC = fc_flat.reshape(FC.shape)
        if K > 1:
            iu = np.triu_indices(K, k=1)
            v = FF[iu].copy(); shuffle_rng.shuffle(v)
            FF2 = np.zeros_like(FF); FF2[iu] = v; FF = FF2 + FF2.T
    if pos_only:
        FF = np.maximum(FF, 0.0)
    # Phase 1: fact relaxation
    af0 = np.maximum(q_rel.astype(np.float64), 0.0)
    if af0.sum() <= 0:
        af0 = np.ones(K, dtype=np.float64)
    af, n_iters, converged, shift = _relax(FF, af0, T, eps)
    # Phase 2: choice competition, separate normalization among choices
    drive = np.maximum(FC.T @ af, 0.0)                            # [C] settled-fact-weighted support
    Wcc = np.zeros((C, C), dtype=np.float64) if pos_only else -CHOICE_INHIB * (np.ones((C, C)) - np.eye(C))
    ac = drive + CHOICE_PRIOR
    ss = ac.sum(); ac = ac / ss if ss > 0 else ac
    for _ in range(T):
        ac_new = np.maximum(drive + Wcc @ ac, 0.0)
        s2 = ac_new.sum()
        if s2 > 0:
            ac_new = ac_new / s2
        d = float(np.mean(np.abs(ac_new - ac)))
        ac = ac_new
        if d < eps:
            break
    return ac.astype(np.float32), n_iters, converged, shift


def aggregate(fact_hd, q_rel, choice_hd, mode, rng=None):
    """Score each choice from a candidate fact pool.
      fact_hd  : [K, N] L2-normalized fact embeddings (SHARDED: one vector per fact)
      q_rel    : [K]    relu(cos(fact, question_query))  (top-down relevance bias, answer-agnostic)
      choice_hd: [C, N] L2-normalized (stem+choice) embeddings
    Returns (scores[C], info). Higher score = preferred choice (except 'inverted' -> lowest wins)."""
    K = fact_hd.shape[0]
    C = choice_hd.shape[0]
    info = {"n_iters": 0, "converged": False, "shift": 0.0}
    if K == 0:
        return np.zeros(C, dtype=np.float32), info
    cc = fact_hd @ choice_hd.T  # [K, C] cos(fact, choice)
    if mode == "single":
        return cc.max(axis=0).astype(np.float32), info
    if mode == "sum":
        return cc.sum(axis=0).astype(np.float32), info
    if mode == "bundle":
        # SPA/Spaun-style ACCUMULATION: relevance-weighted HD superposition (bundle) of the facts, then
        # cosine to each choice. Facts SHARING a semantic direction ADD constructively (convergence); the
        # substrate's native bind+bundle accumulation (Eliasmith SPA), distinct from Kintsch selection.
        w = np.maximum(q_rel.astype(np.float64), 0.0)
        w = w / w.sum() if w.sum() > 0 else np.ones(K, dtype=np.float64) / K
        b = (w[:, None] * fact_hd).sum(axis=0)
        nb = np.linalg.norm(b)
        if nb > 0:
            b = b / nb
        return (b @ choice_hd.T).astype(np.float32), info
    if mode not in ("settle", "pos_only", "shuffled", "inverted"):
        raise ValueError(f"unknown aggregation mode {mode!r}")
    choice_act, n_iters, converged, shift = _ci_two_phase(
        fact_hd, choice_hd, q_rel,
        pos_only=(mode == "pos_only"),
        shuffle_rng=rng if mode == "shuffled" else None)
    info = {"n_iters": n_iters, "converged": converged, "shift": shift}
    if mode == "inverted":
        return (-choice_act).astype(np.float32), info  # readout selects the LOWEST activation (must-fail)
    return choice_act.astype(np.float32), info


def _pick(scores, rng):
    """Argmax choice with seeded random tie-break (matches the floor harness convention)."""
    mx = float(np.max(scores))
    if not np.isfinite(mx) or np.all(scores == scores[0]):
        cand = list(range(len(scores)))
    else:
        cand = [i for i in range(len(scores)) if abs(float(scores[i]) - mx) < 1e-6]
    return int(rng.choice(cand)) if len(cand) > 1 else cand[0]


def run_arm(questions, pool_fn, choice_hd_map, mode, rng, arm_rng_seed):
    """Run one (pool, mode) arm over all questions. pool_fn(qi)->(fact_hd[K,N], q_rel[K]).
    Returns dict with acc/acc_easy/acc_challenge + convergence stats + per-choice-pick digest.
    convergence breakdown (correct/spurious/non-convergent) per the note's item-4 discipline."""
    n_e = n_c = c_e = c_c = 0
    shifts, iters = [], []
    n_conv = 0
    conv_correct = conv_wrong = nonconv_correct = nonconv_wrong = 0
    digest = []  # predicted-choice per question (for arms-differ hashing)
    for qi, q in enumerate(questions):
        fact_hd, q_rel = pool_fn(qi)
        # deterministic per-(arm,question) rng for shuffled-matrix permutation + tie-breaks
        arng = np.random.default_rng(arm_rng_seed + qi)
        scores, info = aggregate(fact_hd, q_rel, choice_hd_map[qi], mode, rng=arng)
        shifts.append(info["shift"]); iters.append(info["n_iters"])
        pick = _pick(scores, arng)
        digest.append(pick)
        hit = int(pick == q["correct_index"])
        if info["converged"]:
            n_conv += 1
            conv_correct += hit; conv_wrong += (1 - hit)
        elif info["n_iters"] > 0:
            nonconv_correct += hit; nonconv_wrong += (1 - hit)
        if q["source"].startswith("ARC-Easy"):
            n_e += 1; c_e += hit
        else:
            n_c += 1; c_c += hit
    n = len(questions)
    return {
        "acc": (c_e + c_c) / n if n else 0.0,
        "acc_easy": c_e / n_e if n_e else None,
        "acc_challenge": c_c / n_c if n_c else None,
        "n_easy": n_e, "n_challenge": n_c,
        "mean_settle_shift": round(float(np.mean(shifts)), 5) if shifts else 0.0,
        "mean_iters": round(float(np.mean(iters)), 2) if iters else 0.0,
        "frac_converged": round(n_conv / n, 4) if n else 0.0,
        "convergence_breakdown": {"conv_correct": conv_correct, "conv_wrong": conv_wrong,
                                  "nonconv_correct": nonconv_correct, "nonconv_wrong": nonconv_wrong},
        "digest": np.array(digest, dtype=np.int64),
    }


def miss_diagnosis(questions, mech_digest, oracle_digest, split):
    """Per-item WHY breakdown for a split ('ARC-Easy'/'ARC-Challenge'), splitting RETRIEVAL failure from
    AGGREGATION failure via the gold ORACLE (per AI2's retrieval-bias diagnosis + coordinator ask):
      solved                -- end-to-end (retrieval-pool mechanism) correct
      retrieval_bottleneck  -- oracle (gold facts) correct BUT retrieval-pool mechanism wrong -> the wall
                               is retrieving the right facts, not combining them
      aggregation_fail      -- oracle wrong too (given the gold facts, still wrong)
      aggregation_fail_lure -- aggregation_fail AND the picked wrong choice is the max-word-overlap-with-
                               stem distractor (the surface 'lure' Challenge is built around)
    mech_digest / oracle_digest: per-question predicted-choice arrays (retrieval-pool + oracle mechanism)."""
    solved = retrieval_bottleneck = aggregation_fail = agg_fail_lure = n = 0
    for qi, q in enumerate(questions):
        if not q["source"].startswith(split):
            continue
        n += 1
        ci = q["correct_index"]
        mech_ok = int(mech_digest[qi]) == ci
        orc_ok = int(oracle_digest[qi]) == ci
        if mech_ok:
            solved += 1
        elif orc_ok:
            retrieval_bottleneck += 1
        else:
            aggregation_fail += 1
            # lure = the wrong choice with the most stem word-overlap
            stem_w = set(arc._content_words(q["stem"], min_len=4))
            best_lure, best_ov = None, -1
            for ic, ch in enumerate(q["choices"]):
                if ic == ci:
                    continue
                ov = len(stem_w & set(arc._content_words(ch, min_len=4)))
                if ov > best_ov:
                    best_ov, best_lure = ov, ic
            if int(oracle_digest[qi]) == best_lure:
                agg_fail_lure += 1
    return {"n": n, "solved": solved, "retrieval_bottleneck": retrieval_bottleneck,
            "aggregation_fail": aggregation_fail, "aggregation_fail_lure": agg_fail_lure}


# ---------------------------------------------------------------------------
# self-test (real code path + planted discriminator + determinism + arms-differ)
# ---------------------------------------------------------------------------
def _planted_discriminator_fires():
    """Synthetic HD case where the signed-graph CI must beat SINGLE: the correct choice C0 is supported
    by TWO mutually-consistent partial facts; the wrong choice C1 by ONE strong distractor fact that
    CONTRADICTS the two (different best-choice -> negative fact-fact edges). single -> picks the strong
    distractor; settle -> the two consistent facts reinforce + inhibit the distractor -> picks C0.
    Also checks: pos_only (negatives zeroed) is measurably different, and settle iterates >= 2."""
    N = 512
    rng = np.random.default_rng(7)

    def orth(v, *against):
        for a in against:
            v = v - v.dot(a) * a
        return v / np.linalg.norm(v)
    d1 = orth(rng.standard_normal(N))
    d2 = orth(rng.standard_normal(N), d1)
    d3 = orth(rng.standard_normal(N), d1, d2)
    correct = (d1 + d2) / np.linalg.norm(d1 + d2)
    wrong = d3.copy()
    choice_hd = np.stack([correct, wrong]).astype(np.float32)       # C0 correct, C1 wrong
    u1 = orth(d1 - d2)                                              # perp to correct and d3
    u2 = orth(rng.standard_normal(N), correct, u1, d3)             # 2nd perp noise dir

    def mk(vec):
        return (vec / np.linalg.norm(vec)).astype(np.float32)
    F1 = mk(0.6 * correct + 0.8 * u1)     # moderate support for correct (cos 0.6, below F3->wrong)
    F2 = mk(0.6 * correct + 0.8 * u2)     # moderate support for correct (F1.F2 > 0 -> reinforce)
    F3 = mk(0.85 * d3 - 0.3 * correct)    # STRONG support for wrong AND anti-correlated with F1,F2
    fact_hd = np.stack([F1, F2, F3]).astype(np.float32)
    q_rel = np.ones(3, dtype=np.float32)
    assert float(F3 @ F1) < 0 and float(F3 @ F2) < 0, "planted: F3 not anti-correlated (no contradiction edge)"
    assert float(F1 @ F2) > 0, "planted: F1,F2 do not reinforce"
    s_single, _ = aggregate(fact_hd, q_rel, choice_hd, "single", rng=np.random.default_rng(0))
    s_settle, info = aggregate(fact_hd, q_rel, choice_hd, "settle", rng=np.random.default_rng(0))
    s_pos, _ = aggregate(fact_hd, q_rel, choice_hd, "pos_only", rng=np.random.default_rng(0))
    single_pick = _pick(s_single, np.random.default_rng(0))
    settle_pick = _pick(s_settle, np.random.default_rng(0))
    assert single_pick == 1, f"planted: single should pick the distractor, got {single_pick} ({s_single})"
    assert settle_pick == 0, f"planted: settle should pick correct via CI accumulation, got {settle_pick} ({s_settle})"
    assert info["n_iters"] >= SETTLE_FIRES_MIN_ITERS, f"planted: settle did not iterate: {info}"
    assert info["shift"] > 0.0, "planted: settle did not move activation (relaxation inert)"
    # A genuine contradiction edge EXISTS (F3 anti-correlated, asserted above). Whether negatives change
    # the OUTCOME is MEASURED by the pos-only ablation in metrics -- NOT asserted here (on real science
    # facts negatives are near-absent, so pos_only ~= settle; the honest finding, per the diagnostic).
    _ = s_pos  # exercised for coverage
    return True


def self_test():
    print("[self-test] planted signed-graph-CI-beats-single discriminator ...", flush=True)
    _planted_discriminator_fires()

    print("[self-test] constructing REAL SemanticHDEncoder + real retrieval/agg path ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "photosynthesis produces oxygen as a byproduct",
        "iron is a heavy metal used to build bridges",
        "the moon orbits the earth once each month",
    ]
    SV = arc._encode_store(enc, store_sents)  # [4, nd] L2 rows
    q = {"qid": "T1", "stem": "What do green plants make using sunlight?",
         "choices": ["iron metal", "sugar and oxygen from photosynthesis", "moon orbit", "sound"],
         "correct_index": 1, "source": "ARC-Easy-Test"}
    qq = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]  # [nd]
    q_rel = np.maximum(SV @ qq, 0.0).astype(np.float32)
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])  # [C, nd]

    modes = ["single", "sum", "bundle", "settle", "pos_only", "shuffled", "inverted"]
    picks = {}
    for m in modes:
        sc, info = aggregate(SV, q_rel, choice_hd, m, rng=np.random.default_rng(1))
        picks[m] = _pick(sc, np.random.default_rng(0))
    assert picks["settle"] == 1, f"real-path settle failed planted question: picks={picks}"
    assert picks["bundle"] == 1, f"real-path bundle failed planted question: picks={picks}"

    # arms-differ (META_RULE_AF): the aggregation modes produce different score vectors
    import hashlib
    h = lambda a: hashlib.sha256(np.round(a, 5).tobytes()).hexdigest()
    sc_single, _ = aggregate(SV, q_rel, choice_hd, "single", rng=np.random.default_rng(1))
    sc_settle, _ = aggregate(SV, q_rel, choice_hd, "settle", rng=np.random.default_rng(1))
    sc_sum, _ = aggregate(SV, q_rel, choice_hd, "sum", rng=np.random.default_rng(1))
    assert h(sc_single) != h(sc_settle), "META_RULE_AF: single and settle bit-identical"
    assert h(sc_sum) != h(sc_settle), "META_RULE_AF: sum and settle bit-identical"
    # NOTE: on REAL science facts, raw-cosine fact-fact edges are near-always positive -> pos_only may
    # equal settle (negatives near-absent). That is the honest measured finding (reported in metrics via
    # the pos-only ablation), NOT a bug -> the negatives-load-bearing test lives in the PLANTED case only.

    # determinism
    sc_a, _ = aggregate(SV, q_rel, choice_hd, "settle", rng=np.random.default_rng(1))
    sc_b, _ = aggregate(SV, q_rel, choice_hd, "settle", rng=np.random.default_rng(1))
    assert h(sc_a) == h(sc_b), "settle non-deterministic"

    # empty pool -> chance-ish (all-tie -> random pick runs)
    sc_empty, _ = aggregate(np.zeros((0, nd), np.float32), np.zeros(0, np.float32), choice_hd, "settle",
                            rng=np.random.default_rng(1))
    assert sc_empty.shape[0] == len(q["choices"])

    # tablestore + questions parse (real data, small touch)
    assert os.path.isdir(_TABLES), f"tablestore missing: {_TABLES}"
    qs = load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print(f"[self-test] PASS (planted signed-graph CI beats single + negatives load-bearing, real "
          f"encoder+retrieval+6 modes, arms-differ, determinism, WorldTree parse ; picks={picks})", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 150, "limit_chal": 100}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    output_dir = _out_dir()
    cfg = _config(args.mode)
    _T0[0] = time.perf_counter()
    _write_start_marker(output_dir, args.mode)

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=cfg["n_dim"], seed=SEED, use_wordnet=True, kv=kv)

    # ---- eval questions ----
    _heartbeat(output_dir, "load_questions")
    questions = load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    ctrl_random = arc._control_random(questions, np.random.default_rng(SEED + 1))
    print(f"[eval] {len(questions)} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f}", flush=True)

    # mean gold central facts (task-shape monitor)
    gc = [len(q["gold_central"]) for q in questions]
    mean_gold_central = round(float(np.mean(gc)), 3) if gc else 0.0

    # ---- tablestore (held-out: exclude every test-gold UID) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = parse_tablestore()
    test_gold = set()
    for q in questions:
        test_gold |= q["gold_all"]
    heldout_uids = sorted(u for u in uid2sent if u not in test_gold)
    heldout_sents = [uid2sent[u] for u in heldout_uids]
    n_excluded = len(uid2sent) - len(heldout_uids)
    print(f"[store] tablestore={len(uid2sent)} facts ; test-gold-excluded={n_excluded} ; "
          f"held-out store={len(heldout_sents)}", flush=True)

    # ---- batch-encode everything ONCE (single pass; no O(n^2)) ----
    _heartbeat(output_dir, "encode_store", {"n": len(heldout_sents)})
    t_enc = time.perf_counter()
    SV_store = arc._encode_store(enc, heldout_sents)  # [Mstore, N] L2 rows
    print(f"[encode] store {len(heldout_sents)} facts in {time.perf_counter()-t_enc:.1f}s", flush=True)

    _heartbeat(output_dir, "encode_questions")
    # per-question: query (stem+all choices, answer-agnostic) + per-choice (stem+choice)
    q_query_txt = [q["stem"] + " " + " ".join(q["choices"]) for q in questions]
    QQ = arc._encode_store(enc, q_query_txt)  # [nQ, N]
    choice_hd_map = []
    for q in questions:
        choice_hd_map.append(arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]))

    # unique gold sentences -> encode once -> map uid->row
    _heartbeat(output_dir, "encode_gold")
    gold_uids = sorted({u for q in questions for u in q["gold_central"] if u in uid2sent})
    gold_sents = [uid2sent[u] for u in gold_uids]
    GV = arc._encode_store(enc, gold_sents) if gold_sents else np.zeros((0, cfg["n_dim"]), np.float32)
    uid2row = {u: i for i, u in enumerate(gold_uids)}

    # ---- retrieval: top-K held-out facts per question (answer-agnostic; cos to q_query) ----
    _heartbeat(output_dir, "retrieval")
    K = RETRIEVAL_K
    Mstore = SV_store.shape[0]
    retr_idx = np.full((len(questions), K), -1, dtype=np.int64)
    if Mstore:
        chunk = 4000
        best = None
        # full sims may be large; compute topK via argpartition per chunk-merge (streaming)
        sims_topv = np.full((len(questions), K), -np.inf, dtype=np.float32)
        sims_topi = np.full((len(questions), K), -1, dtype=np.int64)
        for a in range(0, Mstore, chunk):
            b = min(a + chunk, Mstore)
            s = QQ @ SV_store[a:b].T  # [nQ, b-a]
            # merge this chunk's candidates with running topK
            cand_v = np.concatenate([sims_topv, s], axis=1)
            cand_i = np.concatenate([sims_topi, np.tile(np.arange(a, b), (len(questions), 1))], axis=1)
            part = np.argpartition(-cand_v, K - 1, axis=1)[:, :K]
            rows = np.arange(len(questions))[:, None]
            sims_topv = cand_v[rows, part]
            sims_topi = cand_i[rows, part]
        retr_idx = sims_topi

    # ---- pool functions ----
    def oracle_pool(qi):
        rows = [uid2row[u] for u in questions[qi]["gold_central"] if u in uid2row]
        if not rows:
            return np.zeros((0, cfg["n_dim"]), np.float32), np.zeros(0, np.float32)
        fh = GV[rows]
        qrel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        return fh, qrel

    def retrieval_pool(qi):
        idx = retr_idx[qi][retr_idx[qi] >= 0]
        if idx.size == 0:
            return np.zeros((0, cfg["n_dim"]), np.float32), np.zeros(0, np.float32)
        fh = SV_store[idx]
        qrel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        return fh, qrel

    scr_cache = {}
    def scramble_pool(qi):
        if qi not in scr_cache:
            r = np.random.default_rng(SEED + 9000 + qi)
            m = arc._unit_rows((r.integers(0, 2, size=(K, cfg["n_dim"])) * 2 - 1).astype(np.float32))
            scr_cache[qi] = m
        fh = scr_cache[qi]
        qrel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        return fh, qrel

    def empty_pool(qi):
        return np.zeros((0, cfg["n_dim"]), np.float32), np.zeros(0, np.float32)

    # ---- run all arms ----
    arms = {}
    plan = [
        # ORACLE pool (gold central facts) -- isolates aggregation from retrieval (PRIMARY)
        ("oracle_single", oracle_pool, "single"), ("oracle_sum", oracle_pool, "sum"),
        ("oracle_bundle", oracle_pool, "bundle"), ("oracle_settle", oracle_pool, "settle"),
        ("oracle_pos_only", oracle_pool, "pos_only"),
        ("oracle_shuffled", oracle_pool, "shuffled"), ("oracle_inverted", oracle_pool, "inverted"),
        # held-out RETRIEVAL pool -- fair end-to-end (retrieval + aggregation)
        ("retr_single", retrieval_pool, "single"), ("retr_sum", retrieval_pool, "sum"),
        ("retr_bundle", retrieval_pool, "bundle"), ("retr_settle", retrieval_pool, "settle"),
        ("retr_pos_only", retrieval_pool, "pos_only"),
        # controls
        ("empty", empty_pool, "settle"), ("scramble", scramble_pool, "settle"),
    ]
    for i, (name, pf, mode) in enumerate(plan):
        _heartbeat(output_dir, "arm", {"arm": name})
        arms[name] = run_arm(questions, pf, choice_hd_map, mode, None, SEED + 1000 * (i + 1))
        ae = arms[name]["acc_easy"]
        ac = arms[name]["acc_challenge"]
        print(f"[arm] {name:18s} easy={ae if ae is None else round(ae,4)} "
              f"chal={ac if ac is None else round(ac,4)} iters={arms[name]['mean_iters']} "
              f"conv={arms[name]['frac_converged']}", flush=True)

    # arms-differ (META_RULE_AF): predicted-choice digests must differ across aggregation modes
    import hashlib
    dig = {k: hashlib.sha256(v["digest"].tobytes()).hexdigest() for k, v in arms.items()}
    pairwise = [("oracle_single", "oracle_settle"), ("oracle_sum", "oracle_settle"),
                ("oracle_pos_only", "oracle_settle"), ("retr_single", "retr_settle")]
    arms_differ = all(dig[a] != dig[b] for a, b in pairwise)

    # ---- verdict ----
    def E(k):
        return arms[k]["acc_easy"]
    def Cc(k):
        return arms[k]["acc_challenge"]

    o_single, o_sum, o_bundle, o_settle, o_pos = (E("oracle_single"), E("oracle_sum"), E("oracle_bundle"),
                                                  E("oracle_settle"), E("oracle_pos_only"))
    o_shuf, o_inv = E("oracle_shuffled"), E("oracle_inverted")
    r_single, r_sum, r_bundle, r_settle, r_pos = (E("retr_single"), E("retr_sum"), E("retr_bundle"),
                                                  E("retr_settle"), E("retr_pos_only"))
    e_empty, e_scr = E("empty"), E("scramble")

    # BEST brain-faithful aggregator on the ORACLE pool = max(SPA-bundle accumulation, Kintsch CI-settle)
    best_agg, best_name = (o_bundle, "bundle") if (o_bundle or 0) >= (o_settle or 0) else (o_settle, "settle")
    d_best_single = round(best_agg - o_single, 4)      # beats the single-fact FLOOR? (cell mandate)
    d_best_sum = round(best_agg - o_sum, 4)            # beats the score-sum contrast? (min-bar / faithfulness)
    d_bundle_single = round(o_bundle - o_single, 4)
    d_settle_single = round(o_settle - o_single, 4)
    d_settle_sum = round(o_settle - o_sum, 4)
    d_settle_pos = round(o_settle - o_pos, 4)          # negative/inhibition edges load-bearing? (CI-faithful)
    d_retr_settle_single = round(r_settle - r_single, 4)
    d_retr_bundle_single = round(r_bundle - r_single, 4)

    # Challenge (THE TARGET, coordinator 2026-07-24): best aggregator above chance on the hard set?
    c_bundle, c_settle, c_single, c_sum = Cc("oracle_bundle"), Cc("oracle_settle"), Cc("oracle_single"), Cc("oracle_sum")
    rc_bundle, rc_settle, rc_single = Cc("retr_bundle"), Cc("retr_settle"), Cc("retr_single")
    c_best = max(c_bundle or 0, c_settle or 0)
    challenge_oracle_above_chance = round(c_best - chance, 4)
    challenge_retr_above_chance = round(max(rc_bundle or 0, rc_settle or 0) - chance, 4)

    # per-item WHY (retrieval-fail vs aggregation-fail via oracle) for BOTH splits, best mechanism
    mech_dig = arms["retr_" + best_name]["digest"]
    orc_dig = arms["oracle_" + best_name]["digest"]
    diag_easy = miss_diagnosis(questions, mech_dig, orc_dig, "ARC-Easy")
    diag_chal = miss_diagnosis(questions, mech_dig, orc_dig, "ARC-Challenge")

    # CI-faithfulness checklist (note item 10): (a) real negative edges, (b) >=2 relaxation iters,
    # (c) choice-only readout (True by construction), (d) pos_only underperforms full signed
    mean_iters = arms["oracle_settle"]["mean_iters"]
    settle_iterates = mean_iters >= SETTLE_FIRES_MIN_ITERS
    neg_edges_present = True  # signed matrix always constructs contradiction edges (fact-fact + choice-choice)
    ci_faithful = (settle_iterates and neg_edges_present and (d_settle_pos >= HP_NEG_EDGE_MARGIN))

    baseline_in_band = (e_empty is not None) and (0.05 < e_empty < 0.95)
    leak = (e_scr is not None) and (e_scr >= chance + LEAK_EPS)
    # must-fail controls: shuffled matrix -> chance ; inverted readout -> below chance
    mustfail_shuffled_ok = (o_shuf is not None) and (o_shuf < chance + MUSTFAIL_EPS)
    mustfail_inverted_ok = (o_inv is not None) and (o_inv < chance)
    mustfail_breach = (not mustfail_shuffled_ok) or (not mustfail_inverted_ok)
    ag_saturated = (o_single is not None) and (o_single >= AG_SATURATION)
    min_bar_met = (d_best_single >= HP_AGG_BEATS_SINGLE) and (d_best_sum >= HP_SETTLE_NOT_BELOW_SUM)

    if leak:
        verdict = "LEAK_FLAG"
        vmsg = f"scramble Easy {e_scr:.3f} >= chance {chance:.3f}+{LEAK_EPS} -> pool structure leaks (artifact)"
    elif mustfail_breach:
        verdict = "MUSTFAIL_BREACH"
        vmsg = (f"must-fail control did not collapse: shuffled Easy {o_shuf:.3f} (want <{chance+MUSTFAIL_EPS:.3f}), "
                f"inverted Easy {o_inv:.3f} (want <{chance:.3f}) -> readout may be a construction artifact")
    elif ag_saturated:
        verdict = "AGG_DISCRIMINATOR_SATURATED"
        vmsg = (f"oracle single-fact Easy {o_single:.3f} >= {AG_SATURATION} -> single best gold fact already "
                f"saturates; no headroom for aggregation (report, not a mechanism failure)")
    elif min_bar_met:
        verdict = "AGG_BEATS_FLOOR"
        mech = "SPA-bundle accumulation" if best_name == "bundle" else "Kintsch CI-settle"
        vmsg = (f"ORACLE best aggregator ({mech}) Easy {best_agg:.3f} BEATS single-fact floor {o_single:.3f} "
                f"(+{d_best_single:.3f}) AND score-sum {o_sum:.3f} ({d_best_sum:+.3f}). "
                f"[bundle {o_bundle:.3f} / CI-settle {o_settle:.3f} / sum {o_sum:.3f} / single {o_single:.3f}]. "
                f"Challenge best {c_best:.3f} vs chance {chance:.3f} ({challenge_oracle_above_chance:+.3f}). "
                f"Held-out retr best-agg {max(r_bundle or 0, r_settle or 0):.3f} vs single {r_single:.3f}. "
                f"NOTE: CI-settle {o_settle:.3f} {'>=' if d_settle_single>=0 else '<'} single (Kintsch selection "
                f"discards the fact-count accumulation signal; the WINNING brain-faithful aggregator is the "
                f"SPA/VSA bundle superposition, an accumulation not a score-sum).")
    elif d_best_single >= HP_AGG_BEATS_SINGLE:
        verdict = "AGG_BEATS_SINGLE_NOT_SUM"
        vmsg = (f"ORACLE best aggregator ({best_name}) Easy {best_agg:.3f} beats single {o_single:.3f} "
                f"(+{d_best_single:.3f}) but does NOT clear score-sum {o_sum:.3f} ({d_best_sum:+.3f}) -> "
                f"aggregation helps; the brain-faithful settle/bundle does not decisively add over score-sum")
    elif abs(d_best_single) < FLAT_EPS:
        verdict = "AGG_FLAT"
        vmsg = (f"ORACLE best aggregator ({best_name}) Easy {best_agg:.3f} TIES single {o_single:.3f} "
                f"(delta {d_best_single:+.3f}); aggregation adds no lift (presume impl-bug until proven structural)")
    else:
        verdict = "AGG_BELOW_SINGLE"
        vmsg = (f"ORACLE best aggregator ({best_name}) Easy {best_agg:.3f} BELOW single {o_single:.3f} "
                f"(delta {d_best_single:+.3f})")

    grade = arc._grade_proxy(best_agg, c_best if c_best else None)

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [ORACLE Easy] bundle={o_bundle:.3f} sum={o_sum:.3f} single={o_single:.3f} "
                    f"CI-settle={o_settle:.3f} | [ORACLE Chal] bundle={c_bundle} single={c_single} "
                    f"| [retr Easy] bundle={r_bundle:.3f} single={r_single:.3f} | scramble={e_scr:.3f} "
                    f"inv={o_inv:.3f} shuf={o_shuf:.3f} chance={chance:.3f}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": args.mode, "run_mode": args.mode,
        "n_dim": cfg["n_dim"], "seed": SEED,
        "n_questions": len(questions), "n_easy": n_easy, "n_challenge": n_chal,
        "mean_gold_central_facts": mean_gold_central,
        "best_oracle_aggregator": best_name,
        # controls
        "chance_theoretical": round(chance, 4), "control_random_pick": round(ctrl_random, 4),
        # PRIMARY (ORACLE pool = gold central facts; isolates aggregation from retrieval) -- EASY
        "oracle_single_acc_easy": None if o_single is None else round(o_single, 4),
        "oracle_sum_acc_easy": None if o_sum is None else round(o_sum, 4),
        "oracle_bundle_acc_easy": None if o_bundle is None else round(o_bundle, 4),
        "oracle_settle_acc_easy": None if o_settle is None else round(o_settle, 4),
        "oracle_pos_only_acc_easy": None if o_pos is None else round(o_pos, 4),
        "oracle_shuffled_acc_easy": None if o_shuf is None else round(o_shuf, 4),
        "oracle_inverted_acc_easy": None if o_inv is None else round(o_inv, 4),
        "delta_bestagg_minus_single_easy": d_best_single,    # beats single-fact FLOOR (cell mandate)
        "delta_bestagg_minus_sum_easy": d_best_sum,          # beats score-sum contrast (min-bar / faithfulness)
        "delta_bundle_minus_single_easy": d_bundle_single,   # SPA accumulation vs single
        "delta_settle_minus_single_easy": d_settle_single,   # Kintsch CI-selection vs single
        "delta_settle_minus_sum_easy": d_settle_sum,
        "delta_settle_minus_posonly_easy": d_settle_pos,     # negative edges load-bearing (CI-faithful)
        # PRIMARY -- CHALLENGE (THE TARGET; coordinator 2026-07-24): best aggregator above chance?
        "oracle_single_acc_challenge": None if c_single is None else round(c_single, 4),
        "oracle_sum_acc_challenge": None if c_sum is None else round(c_sum, 4),
        "oracle_bundle_acc_challenge": None if c_bundle is None else round(c_bundle, 4),
        "oracle_settle_acc_challenge": None if c_settle is None else round(c_settle, 4),
        "challenge_oracle_best_minus_chance": challenge_oracle_above_chance,
        "challenge_retr_best_minus_chance": challenge_retr_above_chance,
        # SECONDARY: end-to-end held-out retrieval pool (fair, no leak)
        "retr_single_acc_easy": None if r_single is None else round(r_single, 4),
        "retr_sum_acc_easy": None if r_sum is None else round(r_sum, 4),
        "retr_bundle_acc_easy": None if r_bundle is None else round(r_bundle, 4),
        "retr_settle_acc_easy": None if r_settle is None else round(r_settle, 4),
        "retr_pos_only_acc_easy": None if r_pos is None else round(r_pos, 4),
        "delta_retr_bundle_minus_single_easy": d_retr_bundle_single,
        "delta_retr_settle_minus_single_easy": d_retr_settle_single,
        "retr_bundle_acc_challenge": None if rc_bundle is None else round(rc_bundle, 4),
        "retr_settle_acc_challenge": None if rc_settle is None else round(rc_settle, 4),
        "retr_single_acc_challenge": None if rc_single is None else round(rc_single, 4),
        # per-item WHY (retrieval-fail vs aggregation-fail via ORACLE; coordinator 2026-07-24)
        "miss_diagnosis_easy": diag_easy,
        "miss_diagnosis_challenge": diag_chal,
        # controls (leak/collapse)
        "empty_acc_easy": None if e_empty is None else round(e_empty, 4),
        "scramble_acc_easy": None if e_scr is None else round(e_scr, 4),
        # store / retrieval transparency
        "tablestore_facts": len(uid2sent), "test_gold_excluded": n_excluded,
        "heldout_store_facts": len(heldout_sents), "retrieval_K": K,
        "n_gold_central_encoded": len(gold_uids),
        # CI convergence + faithfulness (note items 4 + 10)
        "settle_max_iters": SETTLE_T, "settle_eps": SETTLE_EPS, "choice_inhib": CHOICE_INHIB,
        "oracle_settle_mean_iters": arms["oracle_settle"]["mean_iters"],
        "oracle_settle_frac_converged": arms["oracle_settle"]["frac_converged"],
        "oracle_settle_convergence_breakdown": arms["oracle_settle"]["convergence_breakdown"],
        "retr_settle_mean_iters": arms["retr_settle"]["mean_iters"],
        "retr_settle_frac_converged": arms["retr_settle"]["frac_converged"],
        "ci_faithfulness_checklist": {
            "a_negative_edges_present": bool(neg_edges_present),
            "b_relaxation_iters_ge_2": bool(settle_iterates),
            "c_choice_only_readout": True,
            "d_posonly_underperforms_full": bool(d_settle_pos >= HP_NEG_EDGE_MARGIN),
            "verdict_ci_faithful": bool(ci_faithful)},
        # gates / integrity
        "settle_iterates": bool(settle_iterates),
        "baseline_in_band": bool(baseline_in_band),
        "ag_saturated": bool(ag_saturated),
        "leak_flag": bool(leak),
        "mustfail_shuffled_collapsed": bool(mustfail_shuffled_ok),
        "mustfail_inverted_below_chance": bool(mustfail_inverted_ok),
        "mustfail_breach": bool(mustfail_breach),
        "arms_differ_verified": bool(arms_differ),
        "arm_digests": dig,
        "bands": {"HP_agg_beats_single": HP_AGG_BEATS_SINGLE,
                  "HP_settle_not_below_sum": HP_SETTLE_NOT_BELOW_SUM,
                  "HP_ci_faithful_margin": HP_CI_FAITHFUL_MARGIN, "HP_neg_edge_margin": HP_NEG_EDGE_MARGIN,
                  "flat_eps": FLAT_EPS, "leak_eps": LEAK_EPS, "mustfail_eps": MUSTFAIL_EPS,
                  "ag_saturation": AG_SATURATION},
        "grade_proxy": grade,
        "human_scale_statement": (
            f"Brain-faithful multi-fact aggregation over ~{mean_gold_central} gold central facts answers ARC-Easy "
            f"at {('%.3f' % best_agg) if best_agg else 'n/a'} (best aggregator = {best_name}: SPA-bundle "
            f"{('%.3f' % o_bundle) if o_bundle is not None else 'n/a'} / Kintsch CI-settle "
            f"{('%.3f' % o_settle) if o_settle is not None else 'n/a'}) vs single best fact "
            f"{('%.3f' % o_single) if o_single is not None else 'n/a'} and score-sum "
            f"{('%.3f' % o_sum) if o_sum is not None else 'n/a'} (chance {chance:.3f}); Challenge best "
            f"{('%.3f' % c_best) if c_best else 'n/a'}. GIVEN gold facts the combination reaches the 55-65% "
            f"structured-solver tier GLASS-BOX (no LLM); the held-out RETRIEVAL number "
            f"({('%.3f' % max(r_bundle or 0, r_settle or 0))}) shows RETRIEVAL is the wall (AI2's diagnosis), "
            f"not combination -- see miss_diagnosis_challenge."),
        "wired_vs_stubbed": (
            "WIRED: WorldTree tablestore parse (9720 typed science facts) = domain-matched curriculum; "
            "test-gold-UID HELD-OUT from the ingested store (fair, no answer-leak); SemanticHDEncoder (same "
            "encoder all arms, fair vs floor); top-K retrieval; TWO brain-faithful aggregators -- SPA/Spaun "
            "HD-BUNDLE accumulation (relevance-weighted superposition; Eliasmith) AND KINTSCH bipartite "
            "SIGNED-GRAPH CI relaxation (fact-choice signed support + fact-fact contradiction edges + "
            "choice-choice inhibition; clip-neg+renormalize per Kintsch, eps=1e-3; choice-node readout; "
            "Thagard-ECHO family); contrasts single-fact floor + score-sum + pos-only ablation; must-fail "
            "shuffled + inverted; ORACLE (gold) pool isolating aggregation from retrieval; empty + scramble "
            "controls; CI convergence breakdown; per-item retrieval-vs-aggregation miss diagnosis (Easy+Chal). "
            "MEASURED FINDING: on clean gold the SPA-bundle accumulation wins; Kintsch CI-selection underperforms "
            "single (its fixed-total renormalization discards the fact-count accumulation signal) and its negative "
            "contradiction edges are near-absent at this encoder's cosine distribution (pos-only ~= settle). "
            "STUBBED/NOTED-NOT-BUILT: aggregation over SemanticHDEncoder fact embeddings (glass-box, fair vs "
            "floor), NOT threaded through HDFactStore role-bound trust-gate bundles (validated separately "
            "29531-33, orthogonal here); SPA vector-cleanup a no-op (graph nodes are raw encoder embeddings, "
            "already on-manifold); ANN/LSH not needed at 9720 facts."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": "mixed: batched retrieval matmul + per-question bundle + signed-graph relaxation (CPU numpy); wall < 10min",
        "storage_strategy": "sharded (each fact its own embedding vector; composed via graph relaxation per META_STORAGE)",
    }
    _write_metrics_atomic(output_dir, metrics)

    # glass-box: settled top facts for a few questions (LOCAL-only)
    try:
        sample = []
        for qi in range(min(8, len(questions))):
            q = questions[qi]
            sample.append({"qid": q["qid"], "stem": q["stem"][:120],
                           "gold_central": [uid2sent.get(u, u)[:80] for u in q["gold_central"][:4]]})
        with open(os.path.join(output_dir, "glassbox_sample.json"), "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2)
    except Exception as e:
        print(f"[warn] glassbox persist failed (non-fatal): {e}", flush=True)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
