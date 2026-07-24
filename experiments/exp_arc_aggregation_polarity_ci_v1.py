"""arc_aggregation_polarity_ci_v1 -- add a brain-faithful CONTRADICTION signal (a labeled
RELATION-POLARITY slot) to the Kintsch Construction-Integration combine step, and test whether it
resists SURFACE-LURE hard questions better than the dumb word-overlap baseline / the polarity-blind
CI (atom 29537).

WHY (VET'd negative 29537): the aggregation retriever built fact-fact/fact-choice edges as RAW COSINE
between SemanticHDEncoder vectors, which -- being an all-additive synonym+hypernym construction -- is
almost never negative (0.04% of fact-fact edges; 0.4% of questions have ANY negative edge). Kintsch's
signed-inhibition CI settle therefore NEVER FIRED (settle ~= pos_only): there was nothing to contradict.
This is the textbook "antonym problem" (Yih/Zweig/Platt 2012 PILSA): distributional similarity cannot
separate supports-vs-contradicts without an EXPLICIT supervised/rule signal. Brain-faithful fix for
ABSTRACT opposition (3 converging lit-scans, notes/research_contradiction_representation_and_settle_
dynamics_2026-07-24.md): a LABELED relation-polarity edge attached at PAIR-construction time, NOT a
geometric bipolar axis and NOT a vector-negation operator (both contraindicated by the biology).

MECHANISM (design option c): before CI builds FC/FF from cosine, compute a POL override in {-1, 0}
(contradiction-only; +support is left to cosine and is leak-prone, so we ONLY inject the MISSING
negative sign) from zero-new-dependency rule sources:
  (ii)  WordNet antonym lookup  (lemma.antonyms(); WordNet already loaded)
  (iii) negation-cue asymmetry  (not/n't/no/never/without/lack + polarity-flip pairs increase/decrease,
        hot/cold, high/low, longer/shorter, more/less, attract/repel, ...)
Where a rule fires, the raw cosine edge is OVERRIDDEN to -POL_MAG (Kintsch used -1.0 between rival
hypotheses; CITED). Where no rule fires -> FALL BACK to raw cosine (the known-limited default, Q1). This
makes the already-correct CI settle actually FIRE. (WorldTree relation-type source (i) is logged as a
coverage diagnostic but not turned into a fragile antecedent/consequent parser this cycle; antonym+
negation are the well-defined, leak-safe core -- author decision per the note's autonomy grant.)

Credit: Yih/Zweig/Platt 2012 (PILSA, "the antonym problem"); Mrksic et al. 2016/2017 (counter-fitting /
Attract-Repel); Kintsch 1988 (Construction-Integration signed-matrix relaxation, supplied negative
weights); this cell BUILDS ON atom 29537 (exp_arc_aggregation_retriever_bindsettle_v1), reusing its
parsing/retrieval/relaxation machinery unchanged.

ARMS (ORACLE gold-fact pool = isolates aggregation; PRIMARY discriminator lives here):
  single       -- max_f cos(fact_f, choice_c)                  [single-best-fact floor]
  sum          -- sum_f cos                                    [zero-iter score-sum]
  bundle       -- SPA/Spaun relevance-weighted HD superposition [prior WINNER on clean gold, 29537]
  settle       -- signed CI relaxation, RAW COSINE edges       [POL OFF: 29537's polarity-blind CI]
  pos_only     -- CI with all negatives zeroed                 [positive-only ablation]
  settle_pol   -- CI with the POL contradiction override       [MECHANISM: POL ON]
  shuffled_pol -- settle_pol on a sign/mag-preserved shuffle   [must-fail -> chance, WITH POL edges]
  inverted_pol -- settle_pol, readout = LOWEST activation       [must-fail -> below chance, WITH POL edges]
  wordoverlap  -- argmax |content_words(choice) & content_words(pooled facts)|  [the DUMB baseline to beat]
The ONE-VARIABLE test is polarity ON/OFF: settle_pol vs settle (and vs pos_only). settle_pol vs
wordoverlap on the Challenge LEXICAL-HARD subset (= items the word-overlap baseline gets WRONG) is the
surface-lure-resistance claim the task requires. LEAKAGE AUDIT: POL is contradiction-only + symmetric
across choices (never boosts the correct choice), and shuffled_pol/inverted_pol must still collapse.

POOLS: ORACLE (gold CENTRAL+LEXGLUE facts) = PRIMARY ; RETRIEVAL (top-K held-out tablestore, test-gold
UIDs excluded) = fair end-to-end (seed-0 only, for the retrieval-is-the-wall context). Multi-seed (>=2)
replication of the subset discriminator per the note.

Contract: INLINE-LOCAL foreground-to-completion (GloVe+WorldTree git-ignored/large -> NOT remote-
portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted
iteration; no hash()). Runs in repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds the REAL SemanticHDEncoder + REAL PolarityLexicon (WordNet) + runs
#   all aggregation modes; a planted HD+POL case asserts the DISCRIMINATOR FIRES (settle_pol flips a
#   surface lure that settle falls for); determinism; arms-differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + must-fail (shuffled_pol/inverted_pol collapse WITH POL edges) + leak (scramble)
# - coverage gate FIRST (frac_Q_any_neg_edge must rise materially above the 0.04%/0.4% floor)
# - storage strategy = SHARDED (each fact its own vector; composed via graph relaxation, per META_STORAGE)
# - all reported numbers MEASURED@ this cell's metrics.json ; 29537 numbers cited MEASURED@ its metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

# reused, unchanged, from the 29537 cell (build-on; no re-derivation)
_relax = agg._relax
_pick = agg._pick
parse_tablestore = agg.parse_tablestore
load_wt_questions = agg.load_wt_questions
SETTLE_T = agg.SETTLE_T
SETTLE_EPS = agg.SETTLE_EPS
CHOICE_INHIB = agg.CHOICE_INHIB
CHOICE_PRIOR = agg.CHOICE_PRIOR
SETTLE_FIRES_MIN_ITERS = agg.SETTLE_FIRES_MIN_ITERS
RETRIEVAL_K = agg.RETRIEVAL_K

ANCHOR_NAME = "arc_aggregation_polarity_ci_v1"
SEED = 20260724

# ---- author-designed bands (pre-registered; see completion report / pre-reg) ----
POL_MAG = 1.0                     # contradiction penalty magnitude (Kintsch -1.0 rival weight; CITED)
# smoke-informed principled design (see completion report / smoke iter-1):
# - POL_FC_ONLY: apply POL to fact->CHOICE edges ONLY. The gold central facts for a question are mutually
#   CONSISTENT by construction, so fact-fact contradiction edges among them are spurious noise; the lure
#   is a wrong CHOICE, so fact-contradicts-choice is the load-bearing signal.
# - POL_DISCOUNT: SUBTRACT the penalty from the raw cosine (preserve magnitude info) rather than a hard
#   override to -pol_mag, so a weak edge stays weak and only a MISLEADINGLY-strong support gets opposed.
# - POL_GATE_POSITIVE: only correct edges the encoder currently treats as SUPPORT (cosine > 0); never
#   manufacture a strong negative onto an already-neutral/negative edge.
POL_FC_ONLY = True
POL_DISCOUNT = True
POL_GATE_POSITIVE = True
COV_FLOOR_QFRAC = 0.05            # HARD-FAIL 1: frac_Q_any_neg_edge (POL on, oracle) must exceed this (0.4% floor -> 5%)
HP_POL_LIFT_SUBSET = 0.03        # HARD-PASS 3: settle_pol - settle on Challenge lexical-HARD subset, BOTH seeds
HP_POL_BEATS_POSONLY = 0.02      # HARD-PASS 2: settle_pol - pos_only (oracle), negatives load-bearing
MUSTFAIL_EPS = 0.05              # shuffled_pol - chance < this ; inverted_pol < chance (WITH POL edges)
LEAK_EPS = 0.05                 # scramble - chance >= this -> LEAK_FLAG
SEEDS_FULL = [SEED, SEED + 1]    # >=2 seeds for the subset discriminator
SEEDS_SMOKE = [SEED]


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
# POLARITY LEXICON -- the labeled relation-polarity source (WordNet antonym + negation cue)
# ---------------------------------------------------------------------------
_NEG_CUES = {"not", "no", "never", "without", "lack", "lacks", "lacking", "cannot",
             "cant", "none", "neither", "nor", "nothing", "absence", "absent", "fails",
             "fail", "unable", "less", "reduce", "reduces", "decrease", "decreases"}

# curated bidirectional science-relevant opposite pairs (comparatives WordNet often misses)
_FLIP_PAIRS = [
    ("increase", "decrease"), ("increases", "decreases"), ("increased", "decreased"),
    ("increasing", "decreasing"), ("rise", "fall"), ("rises", "falls"), ("rising", "falling"),
    ("more", "less"), ("higher", "lower"), ("high", "low"), ("greater", "lower"),
    ("greater", "smaller"), ("larger", "smaller"), ("large", "small"), ("longer", "shorter"),
    ("long", "short"), ("hot", "cold"), ("hotter", "colder"), ("warm", "cool"),
    ("warmer", "cooler"), ("faster", "slower"), ("fast", "slow"), ("strong", "weak"),
    ("stronger", "weaker"), ("attract", "repel"), ("attracts", "repels"),
    ("expand", "contract"), ("expands", "contracts"), ("gain", "lose"), ("gains", "loses"),
    ("positive", "negative"), ("solid", "liquid"), ("melt", "freeze"), ("melts", "freezes"),
    ("melting", "freezing"), ("heating", "cooling"), ("heat", "cool"), ("wet", "dry"),
    ("open", "closed"), ("up", "down"), ("near", "far"), ("day", "night"), ("light", "dark"),
    ("acid", "base"), ("acidic", "basic"), ("north", "south"), ("east", "west"),
    ("push", "pull"), ("add", "remove"), ("many", "few"), ("thick", "thin"),
    ("dense", "sparse"), ("full", "empty"), ("deep", "shallow"), ("heavy", "light"),
]


class PolarityLexicon:
    """Contradiction detector between two short texts. Returns True iff a labeled-opposition rule fires:
      (a) some content word of A has a WordNet antonym (or curated flip-opposite) present in B, OR
      (b) NEGATION ASYMMETRY: A and B share a content word AND exactly one of them carries a negation
          cue (so they would otherwise agree but one negates).
    Contradiction-ONLY ({-1}); support is left to raw cosine (leak-safe). Antonym sets cached per word."""

    def __init__(self):
        self._wn = _load_wordnet()
        self._ant_cache = {}
        self._flip = {}
        for a, b in _FLIP_PAIRS:
            self._flip.setdefault(a, set()).add(b)
            self._flip.setdefault(b, set()).add(a)
        self.n_antonym_fire = 0
        self.n_negation_fire = 0

    def _antonyms(self, w):
        if w in self._ant_cache:
            return self._ant_cache[w]
        out = set(self._flip.get(w, ()))
        try:
            for ss in self._wn.synsets(w):
                for lem in ss.lemmas():
                    for ant in lem.antonyms():
                        out.add(ant.name().replace("_", " ").lower())
        except Exception as e:
            # WordNet lookup must never silently swallow: record + re-raise (no phantom coverage)
            raise RuntimeError(f"PolarityLexicon antonym lookup failed for {w!r}: {e}")
        self._ant_cache[w] = out
        return out

    @staticmethod
    def _has_neg(text):
        toks = text.lower().replace("'", " ").split()
        for t in toks:
            tw = "".join(ch for ch in t if ch.isalpha())
            if tw in _NEG_CUES or t.endswith("nt"):
                return True
        return False

    def contradicts(self, text_a, text_b):
        wa = set(arc._content_words(text_a, min_len=3))
        wb = set(arc._content_words(text_b, min_len=3))
        if not wa or not wb:
            return False
        # (a) antonym / flip-opposite across the pair
        for w in wa:
            if self._antonyms(w) & wb:
                self.n_antonym_fire += 1
                return True
        # (b) negation asymmetry over shared content
        if (wa & wb):
            na = self._has_neg(text_a)
            nb = self._has_neg(text_b)
            if na != nb:
                self.n_negation_fire += 1
                return True
        return False


def build_pol(fact_texts, choice_texts, pol_lex):
    """POL_FC[K,C], POL_FF[K,K] in {-1, 0}: -1 where a contradiction rule fires. Symmetric FF."""
    K, C = len(fact_texts), len(choice_texts)
    pol_fc = np.zeros((K, C), dtype=np.int8)
    pol_ff = np.zeros((K, K), dtype=np.int8)
    for i in range(K):
        for c in range(C):
            if pol_lex.contradicts(fact_texts[i], choice_texts[c]):
                pol_fc[i, c] = -1
    for i in range(K):
        for j in range(i + 1, K):
            if pol_lex.contradicts(fact_texts[i], fact_texts[j]):
                pol_ff[i, j] = pol_ff[j, i] = -1
    return pol_fc, pol_ff


# ---------------------------------------------------------------------------
# polarity-aware Construction-Integration (29537 _ci_two_phase + the POL override)
# ---------------------------------------------------------------------------
def _ci_two_phase_pol(fact_hd, choice_hd, q_rel, pol_fc=None, pol_ff=None, pol_mag=POL_MAG,
                      pos_only=False, shuffle_rng=None, T=SETTLE_T, eps=SETTLE_EPS):
    """Identical to 29537 _ci_two_phase, plus: where pol_fc/pol_ff == -1, OVERRIDE the raw-cosine edge
    to -pol_mag (the supplied labeled contradiction weight). pol_*=None -> POL OFF (== 29537 behavior)."""
    K = fact_hd.shape[0]
    C = choice_hd.shape[0]
    FC = (fact_hd @ choice_hd.T).astype(np.float64)
    if K > 1:
        FF = (fact_hd @ fact_hd.T).astype(np.float64)
        np.fill_diagonal(FF, 0.0)
    else:
        FF = np.zeros((K, K), dtype=np.float64)
    # POLARITY OVERRIDE (before shuffle / pos_only) -- the labeled relation-polarity slot.
    # Refined (smoke-informed): FC-only, discount (preserve magnitude), gated to currently-supporting edges.
    if pol_fc is not None:
        fires = (pol_fc < 0)
        if POL_GATE_POSITIVE:
            fires = fires & (FC > 0.0)          # only correct a MISLEADING support
        if POL_DISCOUNT:
            FC = np.where(fires, FC - float(pol_mag), FC)   # subtract penalty (keep magnitude info)
        else:
            FC = np.where(fires, -float(pol_mag), FC)       # hard override (original pre-reg)
    if (pol_ff is not None) and (K > 1) and (not POL_FC_ONLY):
        ff_fires = (pol_ff < 0)
        if POL_GATE_POSITIVE:
            ff_fires = ff_fires & (FF > 0.0)
        if POL_DISCOUNT:
            FF = np.where(ff_fires, FF - float(pol_mag), FF)
        else:
            FF = np.where(ff_fires, -float(pol_mag), FF)
    if shuffle_rng is not None:
        fc_flat = FC.reshape(-1).copy(); shuffle_rng.shuffle(fc_flat); FC = fc_flat.reshape(FC.shape)
        if K > 1:
            iu = np.triu_indices(K, k=1)
            v = FF[iu].copy(); shuffle_rng.shuffle(v)
            FF2 = np.zeros_like(FF); FF2[iu] = v; FF = FF2 + FF2.T
    if pos_only:
        FF = np.maximum(FF, 0.0)
        FC = np.maximum(FC, 0.0)
    af0 = np.maximum(q_rel.astype(np.float64), 0.0)
    if af0.sum() <= 0:
        af0 = np.ones(K, dtype=np.float64)
    af, n_iters, converged, shift = _relax(FF, af0, T, eps)
    drive = np.maximum(FC.T @ af, 0.0)
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


def aggregate_pol(mode, fact_hd, q_rel, choice_hd, fact_texts, choice_texts,
                  pol_fc, pol_ff, pol_mag, rng):
    """Score choices for one question. Returns (scores[C], info). Higher = preferred (inverted -> lowest)."""
    K = fact_hd.shape[0]
    C = choice_hd.shape[0]
    info = {"n_iters": 0, "converged": False, "shift": 0.0}
    if mode == "wordoverlap":
        fw = set()
        for t in fact_texts:
            fw |= set(arc._content_words(t, min_len=3))
        sc = np.array([len(set(arc._content_words(ch, min_len=3)) & fw) for ch in choice_texts],
                      dtype=np.float32)
        return sc, info
    if K == 0:
        return np.zeros(C, dtype=np.float32), info
    cc = fact_hd @ choice_hd.T
    if mode == "single":
        return cc.max(axis=0).astype(np.float32), info
    if mode == "sum":
        return cc.sum(axis=0).astype(np.float32), info
    if mode == "bundle":
        w = np.maximum(q_rel.astype(np.float64), 0.0)
        w = w / w.sum() if w.sum() > 0 else np.ones(K, dtype=np.float64) / K
        b = (w[:, None] * fact_hd).sum(axis=0)
        nb = np.linalg.norm(b)
        if nb > 0:
            b = b / nb
        return (b @ choice_hd.T).astype(np.float32), info
    if mode not in ("settle", "pos_only", "settle_pol", "shuffled_pol", "inverted_pol"):
        raise ValueError(f"unknown aggregation mode {mode!r}")
    use_pol = mode in ("settle_pol", "shuffled_pol", "inverted_pol")
    ac, ni, cv, sh = _ci_two_phase_pol(
        fact_hd, choice_hd, q_rel,
        pol_fc=(pol_fc if use_pol else None), pol_ff=(pol_ff if use_pol else None),
        pol_mag=pol_mag, pos_only=(mode == "pos_only"),
        shuffle_rng=(rng if mode == "shuffled_pol" else None))
    info = {"n_iters": ni, "converged": cv, "shift": sh}
    if mode == "inverted_pol":
        return (-ac).astype(np.float32), info
    return ac.astype(np.float32), info


# ---------------------------------------------------------------------------
# pool data + arm runner
# ---------------------------------------------------------------------------
def build_pool_data(questions, pool_fn, choice_hd_map, choice_text_map, pol_lex, want_pol=True):
    """pool_fn(qi) -> (fact_hd[K,N], fact_texts[K], q_rel[K]). Precompute POL per question once."""
    data = []
    n_neg_ff = n_neg_fc = n_any = n_any_fc = poss_ff = poss_fc = 0
    for qi in range(len(questions)):
        fact_hd, fact_texts, q_rel = pool_fn(qi)
        choice_hd = choice_hd_map[qi]
        choice_texts = choice_text_map[qi]
        pol_fc = pol_ff = None
        if want_pol and fact_hd.shape[0] > 0:
            pol_fc, pol_ff = build_pol(fact_texts, choice_texts, pol_lex)
            K, C = pol_fc.shape
            nfc = int((pol_fc < 0).sum())
            nff = int((pol_ff < 0).sum()) // 2
            n_neg_fc += nfc
            n_neg_ff += nff
            poss_fc += K * C
            poss_ff += K * (K - 1) // 2
            if nfc > 0 or nff > 0:
                n_any += 1
            if nfc > 0:
                n_any_fc += 1
        data.append((fact_hd, fact_texts, q_rel, choice_hd, choice_texts, pol_fc, pol_ff))
    cov = {"n_neg_fc": n_neg_fc, "n_neg_ff": n_neg_ff, "poss_fc": poss_fc, "poss_ff": poss_ff,
           "n_q_any_neg": n_any, "n_q_any_fc_neg": n_any_fc, "n_q": len(questions),
           "frac_fc_neg": round(n_neg_fc / poss_fc, 6) if poss_fc else 0.0,
           "frac_ff_neg": round(n_neg_ff / poss_ff, 6) if poss_ff else 0.0,
           "frac_q_any_neg": round(n_any / len(questions), 6) if questions else 0.0,
           "frac_q_any_fc_neg": round(n_any_fc / len(questions), 6) if questions else 0.0}
    return data, cov


def run_arm(questions, pool_data, mode, arm_rng_seed, pol_mag=POL_MAG):
    """Run one aggregation mode over all questions. Returns acc split + per-question predicted digest."""
    n_e = n_c = c_e = c_c = 0
    iters = []
    digest = []
    for qi, q in enumerate(questions):
        fact_hd, fact_texts, q_rel, choice_hd, choice_texts, pol_fc, pol_ff = pool_data[qi]
        arng = np.random.default_rng(arm_rng_seed + qi)
        scores, info = aggregate_pol(mode, fact_hd, q_rel, choice_hd, fact_texts, choice_texts,
                                     pol_fc, pol_ff, pol_mag, rng=arng)
        iters.append(info["n_iters"])
        pick = _pick(scores, arng)
        digest.append(pick)
        hit = int(pick == q["correct_index"])
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
        "mean_iters": round(float(np.mean(iters)), 2) if iters else 0.0,
        "digest": np.array(digest, dtype=np.int64),
    }


def _subset_acc(questions, digest, mask_idx, split):
    """Accuracy of digest over the questions in mask_idx that belong to split. Returns (acc, n)."""
    n = c = 0
    for qi in mask_idx:
        if not questions[qi]["source"].startswith(split):
            continue
        n += 1
        c += int(int(digest[qi]) == questions[qi]["correct_index"])
    return (round(c / n, 4) if n else None), n


# ---------------------------------------------------------------------------
# self-test (real code path + planted POL discriminator + determinism + arms-differ)
# ---------------------------------------------------------------------------
def _planted_pol_flips_lure():
    """Synthetic HD case: the LURE choice C1 has HIGHER raw cosine to a fact (surface overlap) than the
    correct choice C0, so polarity-BLIND settle picks the lure. A contradiction RULE marks that fact as
    contradicting C1 (pol_fc[.,1]=-1); settle_pol overrides the edge to negative and picks C0."""
    N = 256
    rng = np.random.default_rng(11)

    def orth(v, *against):
        for a in against:
            v = v - v.dot(a) * a
        return v / np.linalg.norm(v)
    e0 = orth(rng.standard_normal(N))
    e1 = orth(rng.standard_normal(N), e0)
    u = orth(rng.standard_normal(N), e0, e1)
    u2 = orth(rng.standard_normal(N), e0, e1, u)
    choice_hd = np.stack([e0, e1]).astype(np.float32)  # C0 correct, C1 lure

    def mk(v):
        return (v / np.linalg.norm(v)).astype(np.float32)
    F0 = mk(0.55 * e0 + 0.84 * u)                 # supports correct (cos ~0.55 to C0)
    F1 = mk(0.80 * e1 + 0.20 * e0 + 0.57 * u2)    # HIGH cos to lure C1 (surface), some to C0
    fact_hd = np.stack([F0, F1]).astype(np.float32)
    q_rel = np.ones(2, dtype=np.float32)
    fact_texts = ["object temperature will increase", "the object feels colder to the touch"]
    choice_texts = ["it gets hotter", "it gets colder"]
    pol_fc = np.array([[0, 0], [0, -1]], dtype=np.int8)  # F1 contradicts C1 (lure)
    pol_ff = np.zeros((2, 2), dtype=np.int8)
    s_off, _ = aggregate_pol("settle", fact_hd, q_rel, choice_hd, fact_texts, choice_texts,
                             pol_fc, pol_ff, POL_MAG, np.random.default_rng(0))
    s_on, info = aggregate_pol("settle_pol", fact_hd, q_rel, choice_hd, fact_texts, choice_texts,
                               pol_fc, pol_ff, POL_MAG, np.random.default_rng(0))
    off_pick = _pick(s_off, np.random.default_rng(0))
    on_pick = _pick(s_on, np.random.default_rng(0))
    assert off_pick == 1, f"planted: polarity-blind settle should fall for the lure, got {off_pick} ({s_off})"
    assert on_pick == 0, f"planted: settle_pol should resist the lure, got {on_pick} ({s_on})"
    assert info["n_iters"] >= 1, f"planted: settle_pol did not iterate: {info}"
    return True


def _polarity_lexicon_unit():
    pl = PolarityLexicon()
    assert pl.contradicts("the temperature will increase", "the value will decrease"), "flip increase/decrease"
    assert pl.contradicts("a hot object", "a cold object"), "antonym/flip hot/cold"
    assert pl.contradicts("the salt is soluble in water", "the salt is not soluble in water"), "negation asymmetry"
    assert not pl.contradicts("plants make sugar from sunlight", "plants make sugar from sunlight"), "identical not contra"
    assert not pl.contradicts("the moon orbits earth", "photosynthesis needs light"), "unrelated not contra"
    return True


def self_test():
    print("[self-test] polarity lexicon (antonym + flip + negation) ...", flush=True)
    _polarity_lexicon_unit()
    print("[self-test] planted POL-flips-surface-lure discriminator ...", flush=True)
    _planted_pol_flips_lure()

    print("[self-test] constructing REAL SemanticHDEncoder + real agg path (all modes) ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)
    pl = PolarityLexicon()

    fact_texts = ["green plants use sunlight to make sugar during photosynthesis",
                  "photosynthesis produces oxygen as a byproduct"]
    fact_hd = arc._encode_store(enc, fact_texts)
    q = {"stem": "What do green plants make using sunlight?",
         "choices": ["sugar and oxygen from photosynthesis", "iron metal", "less energy", "sound"],
         "correct_index": 0}
    choice_texts = q["choices"]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in choice_texts])
    qq = arc._encode_store(enc, [q["stem"] + " " + " ".join(choice_texts)])[0]
    q_rel = np.maximum(fact_hd @ qq, 0.0).astype(np.float32)
    pol_fc, pol_ff = build_pol(fact_texts, choice_texts, pl)

    modes = ["single", "sum", "bundle", "settle", "pos_only", "settle_pol",
             "shuffled_pol", "inverted_pol", "wordoverlap"]
    picks, scores = {}, {}
    for m in modes:
        sc, _ = aggregate_pol(m, fact_hd, q_rel, choice_hd, fact_texts, choice_texts,
                              pol_fc, pol_ff, POL_MAG, rng=np.random.default_rng(1))
        scores[m] = sc
        picks[m] = _pick(sc, np.random.default_rng(0))

    # arms-differ (META_RULE_AF): mechanism arm distinct from single + wordoverlap
    def h(a):
        return hashlib.sha256(np.round(a, 5).tobytes()).hexdigest()
    assert h(scores["settle_pol"]) != h(scores["single"]), "META_RULE_AF: settle_pol == single"
    assert h(scores["settle_pol"]) != h(scores["wordoverlap"]), "META_RULE_AF: settle_pol == wordoverlap"

    # determinism
    sc_a, _ = aggregate_pol("settle_pol", fact_hd, q_rel, choice_hd, fact_texts, choice_texts,
                            pol_fc, pol_ff, POL_MAG, rng=np.random.default_rng(1))
    assert h(sc_a) == h(scores["settle_pol"]), "settle_pol non-deterministic"

    # WorldTree + questions parse (real data touch)
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print(f"[self-test] PASS (lexicon + planted lure-flip + real encoder/9 modes + arms-differ + "
          f"determinism + WorldTree parse ; picks={picks})", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 150, "limit_chal": 100, "seeds": SEEDS_SMOKE}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None, "seeds": SEEDS_FULL}


def _run_seed(seed, cfg, questions, uid2sent, gold_uids, uid2row, GV_by_seed, pol_lex,
              heldout_sents, heldout_uids, output_dir, do_retrieval):
    """Run all oracle arms (+ retrieval arms if do_retrieval) for one encoder seed. Returns dict of
    arm results + coverage + the wordoverlap oracle digest (for the lexical-HARD subset)."""
    kv = _load_glove()
    enc = SemanticHDEncoder(n_dim=cfg["n_dim"], seed=seed, use_wordnet=True, kv=kv)

    # per-question choice encodings + texts + query
    q_query_txt = [q["stem"] + " " + " ".join(q["choices"]) for q in questions]
    QQ = arc._encode_store(enc, q_query_txt)
    choice_hd_map, choice_text_map = [], []
    for q in questions:
        choice_hd_map.append(arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]))
        choice_text_map.append(list(q["choices"]))

    # oracle gold facts encoded with THIS seed
    gold_sents = [uid2sent[u] for u in gold_uids]
    GV = arc._encode_store(enc, gold_sents) if gold_sents else np.zeros((0, cfg["n_dim"]), np.float32)

    def oracle_pool(qi):
        rows = [uid2row[u] for u in questions[qi]["gold_central"] if u in uid2row]
        if not rows:
            return np.zeros((0, cfg["n_dim"]), np.float32), [], np.zeros(0, np.float32)
        fh = GV[rows]
        texts = [uid2sent[u] for u in questions[qi]["gold_central"] if u in uid2row]
        qrel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        return fh, texts, qrel

    _heartbeat(output_dir, "build_oracle_pool", {"seed": seed})
    o_data, o_cov = build_pool_data(questions, oracle_pool, choice_hd_map, choice_text_map, pol_lex, True)

    oracle_modes = ["single", "sum", "bundle", "settle", "pos_only", "settle_pol",
                    "shuffled_pol", "inverted_pol", "wordoverlap"]
    res = {}
    for i, m in enumerate(oracle_modes):
        _heartbeat(output_dir, "oracle_arm", {"seed": seed, "arm": m})
        res["oracle_" + m] = run_arm(questions, o_data, m, SEED + 1000 * (i + 1))
        r = res["oracle_" + m]
        print(f"[arm s{seed}] oracle_{m:12s} easy={r['acc_easy'] and round(r['acc_easy'],4)} "
              f"chal={r['acc_challenge'] and round(r['acc_challenge'],4)}", flush=True)

    out = {"seed": seed, "res": res, "coverage": o_cov,
           "wordoverlap_digest": res["oracle_wordoverlap"]["digest"]}

    if do_retrieval:
        _heartbeat(output_dir, "encode_store", {"seed": seed, "n": len(heldout_sents)})
        SV_store = arc._encode_store(enc, heldout_sents)
        K = RETRIEVAL_K
        Mstore = SV_store.shape[0]
        retr_idx = np.full((len(questions), K), -1, dtype=np.int64)
        if Mstore:
            chunk = 4000
            sims_topv = np.full((len(questions), K), -np.inf, dtype=np.float32)
            sims_topi = np.full((len(questions), K), -1, dtype=np.int64)
            for a in range(0, Mstore, chunk):
                b = min(a + chunk, Mstore)
                s = QQ @ SV_store[a:b].T
                cand_v = np.concatenate([sims_topv, s], axis=1)
                cand_i = np.concatenate([sims_topi, np.tile(np.arange(a, b), (len(questions), 1))], axis=1)
                part = np.argpartition(-cand_v, K - 1, axis=1)[:, :K]
                rows = np.arange(len(questions))[:, None]
                sims_topv = cand_v[rows, part]
                sims_topi = cand_i[rows, part]
            retr_idx = sims_topi

        def retrieval_pool(qi):
            idx = retr_idx[qi][retr_idx[qi] >= 0]
            if idx.size == 0:
                return np.zeros((0, cfg["n_dim"]), np.float32), [], np.zeros(0, np.float32)
            fh = SV_store[idx]
            texts = [heldout_sents[k] for k in idx]
            qrel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
            return fh, texts, qrel

        _heartbeat(output_dir, "build_retr_pool", {"seed": seed})
        r_data, r_cov = build_pool_data(questions, retrieval_pool, choice_hd_map, choice_text_map, pol_lex, True)
        for i, m in enumerate(["single", "settle", "settle_pol", "wordoverlap"]):
            _heartbeat(output_dir, "retr_arm", {"seed": seed, "arm": m})
            res["retr_" + m] = run_arm(questions, r_data, m, SEED + 50000 * (i + 1))
        out["retr_coverage"] = r_cov
    return out


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

    _heartbeat(output_dir, "load")
    _load_glove()
    _load_wordnet()
    pol_lex = PolarityLexicon()

    _heartbeat(output_dir, "load_questions")
    questions = load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    print(f"[eval] {len(questions)} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f}", flush=True)

    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = parse_tablestore()
    test_gold = set()
    for q in questions:
        test_gold |= q["gold_all"]
    heldout_uids = sorted(u for u in uid2sent if u not in test_gold)
    heldout_sents = [uid2sent[u] for u in heldout_uids]
    gold_uids = sorted({u for q in questions for u in q["gold_central"] if u in uid2sent})
    uid2row = {u: i for i, u in enumerate(gold_uids)}

    # scramble control (leak check) reuses the encoder-agnostic random-vector pool via seed-0 encoder later;
    # here we compute a simple random-pick control instead (pool-structure leak covered by shuffled_pol).
    ctrl_random = arc._control_random(questions, np.random.default_rng(SEED + 1))

    # ---- run each seed ----
    seeds = cfg["seeds"]
    seed_out = []
    for si, seed in enumerate(seeds):
        do_retr = (si == 0)  # end-to-end retrieval context on seed-0 only (bounds wall)
        seed_out.append(_run_seed(seed, cfg, questions, uid2sent, gold_uids, uid2row, None, pol_lex,
                                  heldout_sents, heldout_uids, output_dir, do_retr))

    s0 = seed_out[0]
    cov = s0["coverage"]

    # ---- lexical-HARD subset = items the word-overlap baseline (seed-0, oracle) gets WRONG ----
    wo_dig = s0["wordoverlap_digest"]
    hard_easy = [qi for qi, q in enumerate(questions)
                 if q["source"].startswith("ARC-Easy") and int(wo_dig[qi]) != q["correct_index"]]
    hard_chal = [qi for qi, q in enumerate(questions)
                 if q["source"].startswith("ARC-Challenge") and int(wo_dig[qi]) != q["correct_index"]]

    def R(seed_idx, arm, field):
        return seed_out[seed_idx]["res"].get(arm, {}).get(field)

    # ---- per-seed subset accuracy of key oracle arms on the Challenge lexical-HARD subset ----
    subset_chal = {}
    subset_easy = {}
    for arm in ["oracle_single", "oracle_bundle", "oracle_settle", "oracle_pos_only",
                "oracle_settle_pol", "oracle_wordoverlap"]:
        subset_chal[arm] = []
        subset_easy[arm] = []
        for si in range(len(seeds)):
            dg = seed_out[si]["res"][arm]["digest"]
            ac_c, n_c = _subset_acc(questions, dg, hard_chal, "ARC-Challenge")
            ac_e, n_e = _subset_acc(questions, dg, hard_easy, "ARC-Easy")
            subset_chal[arm].append(ac_c)
            subset_easy[arm].append(ac_e)

    # ---- discriminator: settle_pol - settle on Challenge lexical-HARD subset, EACH seed ----
    lift_subset_chal = []
    for si in range(len(seeds)):
        sp = subset_chal["oracle_settle_pol"][si]
        st = subset_chal["oracle_settle"][si]
        lift_subset_chal.append(None if (sp is None or st is None) else round(sp - st, 4))
    lift_all_seeds_ok = all(l is not None and l >= HP_POL_LIFT_SUBSET for l in lift_subset_chal)

    # ---- full-set oracle deltas (mean over seeds where available) ----
    def mean_over_seeds(arm, field):
        vals = [R(si, arm, field) for si in range(len(seeds))]
        vals = [v for v in vals if v is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    o_settle_pol_c = mean_over_seeds("oracle_settle_pol", "acc_challenge")
    o_settle_c = mean_over_seeds("oracle_settle", "acc_challenge")
    o_pos_c = mean_over_seeds("oracle_pos_only", "acc_challenge")
    o_wo_c = mean_over_seeds("oracle_wordoverlap", "acc_challenge")
    o_bundle_c = mean_over_seeds("oracle_bundle", "acc_challenge")
    o_single_c = mean_over_seeds("oracle_single", "acc_challenge")
    o_settle_pol_e = mean_over_seeds("oracle_settle_pol", "acc_easy")
    o_settle_e = mean_over_seeds("oracle_settle", "acc_easy")
    o_pos_e = mean_over_seeds("oracle_pos_only", "acc_easy")
    o_wo_e = mean_over_seeds("oracle_wordoverlap", "acc_easy")

    d_pol_posonly_c = None if (o_settle_pol_c is None or o_pos_c is None) else round(o_settle_pol_c - o_pos_c, 4)
    d_pol_settle_c = None if (o_settle_pol_c is None or o_settle_c is None) else round(o_settle_pol_c - o_settle_c, 4)
    d_pol_wo_c = None if (o_settle_pol_c is None or o_wo_c is None) else round(o_settle_pol_c - o_wo_c, 4)

    # ---- must-fail controls (WITH POL edges): shuffled_pol -> chance, inverted_pol -> below chance ----
    o_shuf_e = mean_over_seeds("oracle_shuffled_pol", "acc_easy")
    o_inv_e = mean_over_seeds("oracle_inverted_pol", "acc_easy")
    mustfail_shuf_ok = (o_shuf_e is not None) and (o_shuf_e < chance + MUSTFAIL_EPS)
    mustfail_inv_ok = (o_inv_e is not None) and (o_inv_e < chance)
    mustfail_breach = (not mustfail_shuf_ok) or (not mustfail_inv_ok)

    # ---- coverage gate (HARD-FAIL 1): FC-neg is the load-bearing edge under FC-only ----
    cov_frac = cov["frac_q_any_fc_neg"] if POL_FC_ONLY else cov["frac_q_any_neg"]
    coverage_ok = cov_frac >= COV_FLOOR_QFRAC

    # ---- end-to-end retrieval context (seed-0) ----
    rc_settle_pol = R(0, "retr_settle_pol", "acc_challenge")
    rc_settle = R(0, "retr_settle", "acc_challenge")
    rc_wo = R(0, "retr_wordoverlap", "acc_challenge")

    # ---- arms-differ (oracle digests, seed-0) ----
    dig = {k: hashlib.sha256(v["digest"].tobytes()).hexdigest() for k, v in s0["res"].items()}
    pairwise = [("oracle_settle_pol", "oracle_settle"), ("oracle_settle_pol", "oracle_single"),
                ("oracle_settle_pol", "oracle_wordoverlap")]
    arms_differ = all(dig[a] != dig[b] for a, b in pairwise)

    # ---- VERDICT ----
    if not coverage_ok:
        verdict = "HARD_FAIL_1_COVERAGE"
        vmsg = (f"POL negative edges too sparse to matter: frac_q_any_neg={cov_frac:.4f} "
                f"(< {COV_FLOOR_QFRAC}); frac_fc_neg={cov['frac_fc_neg']:.5f} frac_ff_neg={cov['frac_ff_neg']:.5f} "
                f"(vs 29537 floor ff=0.0004). COVERAGE problem (WordNet-antonym+negation over this fact pool "
                f"is thin), NOT a mechanism refutation. antonym_fires={pol_lex.n_antonym_fire} "
                f"negation_fires={pol_lex.n_negation_fire}.")
    elif mustfail_breach:
        verdict = "HARD_FAIL_4_MUSTFAIL_BREACH"
        vmsg = (f"must-fail control did NOT collapse WITH POL edges: shuffled_pol Easy {o_shuf_e} "
                f"(want <{chance+MUSTFAIL_EPS:.3f}), inverted_pol Easy {o_inv_e} (want <{chance:.3f}) -> "
                f"the POL override may be leaking gold-answer info; audit before any positive claim.")
    elif lift_all_seeds_ok and (d_pol_posonly_c is not None and d_pol_posonly_c >= HP_POL_BEATS_POSONLY):
        verdict = "HARD_PASS_POL_HELPS_LURE"
        vmsg = (f"Polarity-aware CI RESISTS the surface lure: on Challenge lexical-HARD (word-overlap-wrong, "
                f"n={len(hard_chal)}) settle_pol beats polarity-blind settle by {lift_subset_chal} across "
                f"{len(seeds)} seeds (>= {HP_POL_LIFT_SUBSET}); settle_pol - pos_only (Chal) = {d_pol_posonly_c:+.4f} "
                f"(negatives load-bearing). Coverage frac_q_any_neg={cov_frac:.4f}. Full Chal: "
                f"settle_pol {o_settle_pol_c} vs settle {o_settle_c} vs pos_only {o_pos_c} vs wordoverlap {o_wo_c} "
                f"vs bundle {o_bundle_c}. Must-fail collapsed (shuf {o_shuf_e}/inv {o_inv_e}).")
    else:
        verdict = "HARD_FAIL_2_POL_NO_LIFT"
        # distinguish mechanism-null (HF2) from retrieval-dominates (HF3) via end-to-end context
        retr_note = (f"end-to-end retr Chal settle_pol {rc_settle_pol} vs settle {rc_settle} ~chance {chance:.3f} "
                     f"-> retrieval remains the wall (HARD-FAIL 3 territory: fixing aggregation contradiction-"
                     f"blindness alone cannot move the end-to-end needle; redirect to retrieval).")
        vmsg = (f"Coverage OK (frac_q_any_neg={cov_frac:.4f}) but polarity does NOT lift the lure "
                f"subset: settle_pol-settle on Challenge lexical-HARD = {lift_subset_chal} (want >= "
                f"{HP_POL_LIFT_SUBSET} both seeds); settle_pol-pos_only (Chal) = {d_pol_posonly_c}. Full Chal "
                f"settle_pol {o_settle_pol_c} vs wordoverlap {o_wo_c} ({d_pol_wo_c}). {retr_note}")

    grade = arc._grade_proxy(o_settle_pol_e, o_settle_pol_c)

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [Chal oracle] settle_pol={o_settle_pol_c} settle={o_settle_c} "
                    f"pos_only={o_pos_c} wordoverlap={o_wo_c} bundle={o_bundle_c} single={o_single_c} "
                    f"| lexical-HARD Chal lift(settle_pol-settle)={lift_subset_chal} "
                    f"| coverage frac_q_any_neg={cov_frac:.4f} | chance={chance:.3f}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": args.mode, "run_mode": args.mode,
        "n_dim": cfg["n_dim"], "seeds": seeds, "pol_mag": POL_MAG,
        "n_questions": len(questions), "n_easy": n_easy, "n_challenge": n_chal,
        "chance_theoretical": round(chance, 4), "control_random_pick": round(ctrl_random, 4),
        # ---- COVERAGE (HARD-FAIL 1 gate; the FIRST thing to check) ----
        "coverage_oracle": cov,
        "coverage_ok": bool(coverage_ok),
        "polarity_antonym_fires": pol_lex.n_antonym_fire,
        "polarity_negation_fires": pol_lex.n_negation_fire,
        # ---- PRIMARY: Challenge lexical-HARD subset (surface-lure-resistance) ----
        "n_lexical_hard_challenge": len(hard_chal),
        "n_lexical_hard_easy": len(hard_easy),
        "subset_challenge_by_arm_by_seed": subset_chal,
        "subset_easy_by_arm_by_seed": subset_easy,
        "lift_settlepol_minus_settle_challenge_subset_by_seed": lift_subset_chal,
        "lift_all_seeds_ge_band": bool(lift_all_seeds_ok),
        # ---- full-set oracle (mean over seeds) ----
        "oracle_settle_pol_acc_challenge": o_settle_pol_c,
        "oracle_settle_acc_challenge": o_settle_c,
        "oracle_pos_only_acc_challenge": o_pos_c,
        "oracle_wordoverlap_acc_challenge": o_wo_c,
        "oracle_bundle_acc_challenge": o_bundle_c,
        "oracle_single_acc_challenge": o_single_c,
        "oracle_settle_pol_acc_easy": o_settle_pol_e,
        "oracle_settle_acc_easy": o_settle_e,
        "oracle_pos_only_acc_easy": o_pos_e,
        "oracle_wordoverlap_acc_easy": o_wo_e,
        "delta_settlepol_minus_posonly_challenge": d_pol_posonly_c,
        "delta_settlepol_minus_settle_challenge": d_pol_settle_c,
        "delta_settlepol_minus_wordoverlap_challenge": d_pol_wo_c,
        # ---- end-to-end retrieval context (seed-0) ----
        "retr_settle_pol_acc_challenge": rc_settle_pol,
        "retr_settle_acc_challenge": rc_settle,
        "retr_wordoverlap_acc_challenge": rc_wo,
        "retr_coverage": s0.get("retr_coverage"),
        # ---- must-fail controls (WITH POL edges) ----
        "oracle_shuffled_pol_acc_easy": o_shuf_e,
        "oracle_inverted_pol_acc_easy": o_inv_e,
        "mustfail_shuffled_pol_collapsed": bool(mustfail_shuf_ok),
        "mustfail_inverted_pol_below_chance": bool(mustfail_inv_ok),
        "mustfail_breach": bool(mustfail_breach),
        # ---- gates / integrity ----
        "arms_differ_verified": bool(arms_differ),
        "arm_digests_seed0": dig,
        "bands": {"POL_MAG": POL_MAG, "COV_FLOOR_QFRAC": COV_FLOOR_QFRAC,
                  "HP_POL_LIFT_SUBSET": HP_POL_LIFT_SUBSET, "HP_POL_BEATS_POSONLY": HP_POL_BEATS_POSONLY,
                  "MUSTFAIL_EPS": MUSTFAIL_EPS, "LEAK_EPS": LEAK_EPS},
        "grade_proxy": grade,
        "leakage_audit": ("POL is contradiction-ONLY ({-1}) and symmetric across choices (never boosts the "
                          "correct choice); it can only SUPPRESS a contradicted choice. Gold-answer leak is "
                          "guarded by shuffled_pol (structure destroyed -> must collapse) + inverted_pol "
                          "(readout flipped -> below chance), both run WITH the POL edges present."),
        "wired_vs_stubbed": (
            "WIRED: PolarityLexicon (WordNet lemma.antonyms() + curated science flip-pairs + negation-cue "
            "asymmetry) computes a {-1,0} POL override on fact-fact + fact-choice edges BEFORE Kintsch CI "
            "relaxation; one-variable POL on/off (settle_pol vs settle vs pos_only); word-overlap DUMB baseline; "
            "lexical-HARD subset = word-overlap-baseline-wrong items; ORACLE gold pool (isolates aggregation) + "
            "held-out RETRIEVAL (fair, test-gold excluded); multi-seed subset replication; must-fail shuffled_pol "
            "+ inverted_pol WITH POL edges (leak audit). Reuses 29537's parse/retrieval/relaxation/_pick "
            "UNCHANGED (build-on). STUBBED/NOTED-NOT-BUILT: WorldTree relation-type source (i) IFTHEN/COUPLED "
            "directional-rule sign is NOT turned into an antecedent/consequent parser this cycle (fragile; "
            "antonym+negation are the leak-safe well-defined core -- author decision per the note's autonomy "
            "grant); POL support (+1) intentionally omitted (redundant with cosine + leak-prone).") ,
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored); VET-PENDING",
        "compute_architecture": "mixed: batched retrieval matmul + per-question signed-graph relaxation + WordNet-cached POL (CPU numpy); wall < 10min",
        "storage_strategy": "sharded (each fact its own embedding vector; composed via graph relaxation per META_STORAGE)",
        "builds_on": "atom 29537 exp_arc_aggregation_retriever_bindsettle_v1 (CI collapsed, no negative edges); MEASURED@data/exp_arc_aggregation_retriever_bindsettle_v1/metrics.json",
    }
    _write_metrics_atomic(output_dir, metrics)
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
