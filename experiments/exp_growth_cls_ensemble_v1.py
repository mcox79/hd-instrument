"""exp_growth_cls_ensemble_v1 -- CLS-FAITHFUL GROWTH FOLLOW-UP to
notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/PROBLEM.md BAR #4.

QUESTION: exp_learner_safety_gate_v1's FULL run (data/exp_learner_safety_gate_v1/metrics.json, verdict
SAFE_TO_GROW_GATE_A_AND_CLEAN_GATE_B_PASS_CISEP) found that growing the reader's SELPREF meaning from 5M to
15M simplewiki tokens improves LitBank who-did-what paraphrase accuracy CI-separated
(0.0714 -> 0.1494, delta +0.0780 CI [0.0698,0.0866], n=5529) via REAL grammatical structure (not just more
writing -- the info-free FULLSHUF control does not beat baseline). BUT it also CORRUPTS 25.57% CI
[0.2152,0.2987] (n=395) of the items BASELINE_SMALL got RIGHT -- growth is a NAIVE BATCH OVERWRITE: it
throws away the 5M-token representation entirely and replaces it with a from-scratch 15M-token fit.

The brain does not do this. Complementary Learning Systems (McClelland, McNaughton & O'Reilly 1995, "Why
there are complementary learning systems in the hippocampus and neocortex"): the neocortex integrates new
experience SLOWLY, at a rate-limited pace, INTERLEAVED with replay of old experience, and the hippocampal
trace is never simply thrown away and refit from scratch. So 25.57% corruption from a from-scratch overwrite
is evidence of a MISSING MECHANISM (naive batch refit), not evidence of a ceiling on how much a learner can
safely grow. This cell tests whether a CLS-style growth mechanism can recover most of the accuracy gain
while cutting the corruption rate below the naive-overwrite level.

PRIOR-WORK CHECK: substrate_query.sh returns zero bytes per the 2026-08-18 audit; used
tools/experiment_index.py instead. query "complementary learning" / "CLS" / "replay" / "consolidation" /
"corruption" surfaces hdlab/continual.py's replay_cycle (substrate_continual_NREM_replay_v1,
MEASURED_MECHANISM, +0.57 absolute drift_reduction) and exp_coherence_filter_foundation_growth_safety_
precheck_v1 (MIDDLE_BAND, a different mechanism on a different question -- filtering raw-reader triples
before LCCP consolidation, not growing a distributional-similarity learner's token budget). No prior cell
tests a CLS keep-both-stores ensemble OR a graded/rate-limited consolidation blend against the naive-overwrite
corruption number measured by exp_learner_safety_gate_v1. This cell is novel, not a rediscovery.

CHECKED hdlab/continual.py's replay_cycle FOR DIRECT REUSE, NOT USABLE HERE: it operates on an associative
HD-binding weight matrix W[N_DIM,N_DIM] (re-adds a Hebbian outer-product key@value.T for a resampled subset
of stored bindings) -- the substrate's bind/bundle/cleanup memory representation. SELPREF is a completely
different representational format: a sparse verb x (arg-slot,filler) PPMI co-occurrence matrix factorised by
truncated SVD into dense word vectors. There is no W matrix, no key/value HD codes, and no bind operation
here for replay_cycle to act on -- wiring it in would require a nontrivial representational adapter (project
SELPREF into an HD associative memory) that is out of scope for this drill. So this cell implements the
TWO tractable CLS-faithful proxies the coordinator authorized instead (see ARMS), and says so plainly rather
than force-fitting an inapplicable primitive.

REUSED VERBATIM (READ-ONLY imports; nothing below is modified; this cell writes ONLY to its own data dir):
  experiments.exp_learner_safety_gate_v1 (as G): build_paraphrase_items (SAME LitBank who-did-what gold
    items, SAME construction), cache_path (SAME POS-valid-cache resolution/regeneration discipline),
    score_items / argmax_pred (SAME scoring), boot_ci / paired_delta_acc / corruption_rate (SAME bootstrap
    arithmetic), MODE_CFG / SEED (SAME regime + seed as the BASELINE_SMALL / GROWN_LARGE reference numbers
    quoted above, so paired deltas are apples-to-apples).
  experiments.exp_structured_context_learner_v1 (as S): load_parsed, token_sents, build_vocab,
    build_selpref_cooc, ppmi_matrix, svd_vectors, dense_vec_cosine_fn, random_vec_cosine_fn, ARG_SLOTS,
    SVD_K -- the SAME SELPREF construction pipeline BASELINE_SMALL / GROWN_LARGE were built from.

ARMS (all scored on the SAME items -- CORE_COMMON population, see below; all corruption numbers computed
against the SAME base-right item set):
  BASELINE_SMALL     : SELPREF on 5M tokens (identical construction to G.run(), recomputed here so the
                        paired-delta arithmetic below runs on THIS cell's own item/coverage population).
  GROWN_LARGE_naive   : SELPREF on 15M tokens, naive from-scratch batch refit (identical construction to
                        G.run()'s GROWN_LARGE). The corruption-comparison REFERENCE arm.
  ENSEMBLE_MEAN / MAX : CLS "keep-both-stores" mechanism. Never discards the pre-growth (5M) channel: per
                        candidate, z-score BASELINE_SMALL's cosine and GROWN_LARGE's cosine independently
                        (over the full item population, so the two differently-scaled score distributions
                        are commensurable), then combine by MEAN (average evidence) or MAX (best-evidence-
                        wins) of whichever channel(s) are defined for that candidate. If GROWN's channel is
                        OOV for a candidate the pre-growth channel alone still answers -- the corruption a
                        pure overwrite causes by DELETING the old channel cannot happen here.
  BLEND_0.25/0.50/0.75: CLS graded/rate-limited consolidation proxy. The prompt's own framing is followed
                        literally: "5M-counts + new-10M-counts" is mathematically identical to the naive
                        15M batch refit (a from-scratch count over 15M tokens already IS the union of counts
                        over the first 5M and the next 10M), so that construction changes nothing -- the
                        real CLS lever is a RATE-LIMITED update. Implemented as a CONVEX BLEND AT THE RAW
                        CO-OCCURRENCE (COUNT) LEVEL, not at the finished SVD-vector level: build_selpref_
                        union_matrices() builds the SELPREF verb x (arg-slot,filler) matrix for BOTH corpora
                        over a SHARED (union) row/column index (columns kept if the RAW edge count summed
                        across both corpora clears min_count, so the column SET -- vocabulary of what CAN be
                        represented -- is IDENTICAL across every blend weight; only the per-cell VALUE
                        changes), then blended = (1-alpha)*M_5M + alpha*M_15M, ONE PPMI+SVD on the blend.
                        Blending is deliberately done BEFORE the SVD, not after: two independently-
                        factorised truncated SVDs are only unique up to an arbitrary orthogonal rotation of
                        equal singular values (no natural correspondence between vec_small's and vec_large's
                        coordinate axes), so averaging two unaligned SVD bases would not be a meaningful
                        representation; blending the sufficient statistics (counts) and running a SINGLE SVD
                        on the blend sidesteps that entirely and yields one coherent basis. alpha=0 recovers
                        the 5M-only matrix, alpha=1 recovers the 15M-only matrix (verified in self-test);
                        alpha in {0.25,0.5,0.75} is the graded/rate-limited middle ground the prompt asks
                        for -- old evidence is REPLAYED (kept in the count total) at a controllable weight
                        rather than being overwritten wholesale.
  RANDOM_floor        : random dense vectors over the union vocab (info-free; must lose).

COVERAGE / CORE_COMMON: an item enters the gate population iff BASELINE_SMALL, GROWN_LARGE_naive,
ENSEMBLE_MEAN, ENSEMBLE_MAX and all three BLEND weights produce a defined (non-None) argmax prediction --
so literally every accuracy/corruption/paired-delta number below is computed on the SAME item set (no
number crosses populations). RANDOM_floor is scored on its own achievable subset OF that same population
(context only, not part of any comparison).

THE SAFETY-FLIP TEST (per-arm, all against the SAME base-right item set):
  (a) delta_acc_vs_baseline  = paired-bootstrap(arm accuracy - BASELINE_SMALL accuracy); "keeps the gain"
      iff CI-separated above 0 AND retains >=50% of GROWN_LARGE_naive's own gain over baseline (retention
      fraction reported for every arm regardless of the 50% cutoff, so the raw numbers are always visible).
  (b) delta_corruption_vs_grown_naive = paired-bootstrap(arm's right->wrong-among-base-right rate minus
      GROWN_LARGE_naive's own right->wrong rate), over the SAME resampled base-right indices each replicate
      (matched pairs); "cuts corruption" iff this CI is entirely BELOW 0 (the arm's corruption rate is
      significantly LOWER than the naive-overwrite rate).
  An arm satisfying BOTH (a) and (b) is a CLS-faithful safe-growth mechanism -- SAFE_GROWTH_MECHANISM_FOUND,
  and it flips the BAR #4 safety-gate framing from "not safe, naive overwrite corrupts 25.6%" to "safe,
  provided growth uses mechanism X". If NO arm satisfies both, that is ALSO a rigorous, useful finding: it
  means the two tractable CLS proxies tried here do not rescue naive-overwrite growth, and safe growth (if
  it exists) needs a stronger mechanism (e.g. versioned per-word rollback) -- reported plainly, not spun.

Compute architecture: sequential-CPU sparse linear algebra (scipy.sparse + sklearn randomized_svd via
S.svd_vectors), matching the EXACT primitive family the reused baseline/grown arms were built with. Not a
GPU-batching candidate: the matrices here (verb x arg-slot-filler, tens of thousands of rows/cols, sparse)
are the SAME primitive S.svd_vectors already runs on CPU for BASELINE_SMALL/GROWN_LARGE in the reused
G.run(); there is no independent-phase-point loop to batch (this is TWO extra SVD-style builds -- the
ensemble is a pure post-hoc cosine fusion with no extra SVD at all -- not a sweep). Storage strategy:
no_storage / no_composition -- this is a single-hop similarity read-out over pre-built dense vectors,
matching G.run()'s own declaration.

Run:  .venv/Scripts/python.exe experiments/exp_growth_cls_ensemble_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_growth_cls_ensemble_v1.py --mode smoke
      .venv/Scripts/python.exe experiments/exp_growth_cls_ensemble_v1.py --mode full

ASCII only. Writes ONLY to data/exp_growth_cls_ensemble_v1/. Does not modify hdlab/, exp_learner_safety_
gate_v1.py, exp_structured_context_learner_v1.py, or any other file. Deterministic (fixed integer seeds
only; no hash()-derived RNG seeding or list(set()) ordering per META_RULE F.5).
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
import sys
import time
import traceback
from array import array as _arr
from datetime import datetime, timezone

import numpy as np
import scipy.sparse as sp

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if os.path.join(REPO_ROOT, "experiments") not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_structured_context_learner_v1 as S      # noqa: E402  (READ-ONLY reuse)
import experiments.exp_learner_safety_gate_v1 as G             # noqa: E402  (READ-ONLY reuse)

ANCHOR = "growth_cls_ensemble_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR)
BLEND_WEIGHTS = [0.25, 0.5, 0.75]
ARM_SEED_OFFSET = {"ENSEMBLE_MEAN": 60, "ENSEMBLE_MAX": 61,
                    "BLEND_0.25": 62, "BLEND_0.50": 63, "BLEND_0.75": 64}


# --------------------------------------------------------------------------- ENSEMBLE (keep-both-stores)
def zscore_params(sim_fn, items):
    """Mean/std of sim_fn(query, cand) over every DEFINED (item, candidate) pair -- used to make two
    differently-scaled similarity channels (5M-token cosines vs 15M-token cosines) commensurable before
    fusing them. std floored at 1.0 if degenerate (constant channel) to avoid a divide-by-~0 blowup."""
    vals = []
    for it in items:
        for c in it["cand"]:
            s = sim_fn(it["query"], c)
            if s is not None:
                vals.append(s)
    if not vals:
        return 0.0, 1.0
    arr = np.asarray(vals, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std())
    if std < 1e-12:
        std = 1.0
    return mean, std


def make_ensemble_sim(sim_a, mean_a, std_a, sim_b, mean_b, std_b, mode):
    """CLS keep-both-stores fusion: z-score each channel, combine by mean or max of whichever channel(s)
    are defined. NEVER discards a channel that IS defined just because the other is not (that is exactly
    the naive-overwrite failure mode this arm is designed to avoid)."""
    def fused(q, c):
        sa = sim_a(q, c)
        sb = sim_b(q, c)
        za = (sa - mean_a) / std_a if sa is not None else None
        zb = (sb - mean_b) / std_b if sb is not None else None
        if za is None and zb is None:
            return None
        if za is None:
            return zb
        if zb is None:
            return za
        return (za + zb) / 2.0 if mode == "mean" else max(za, zb)
    return fused


# --------------------------------------------------------------------------- BLEND (graded consolidation)
def build_selpref_union_matrices(parsed_small, parsed_large, union_word_index, min_count):
    """CLS graded-consolidation precursor: SELPREF verb x (arg-slot,filler) co-occurrence for BOTH corpora
    over a SHARED (union) row/col index, so they can be linearly blended -- blended = (1-alpha)*M_small +
    alpha*M_large -- before a SINGLE PPMI+SVD. Count-level analogue of hippocampal replay interleaved with
    cortical consolidation: old evidence (M_small) is never discarded, new evidence (M_large) is integrated
    at a controllable RATE (alpha), not a full batch overwrite. Blended at the RAW COUNT level rather than
    the finished SVD-vector level deliberately: truncated SVD is unique only up to an arbitrary orthogonal
    rotation of equal singular values, so two independently-factorised bases have no natural coordinate
    correspondence and averaging their vectors would not be a well-defined representation; blending counts
    and running ONE SVD on the blend avoids that problem and yields a single coherent basis.
    Column SET = union of qualifying (arg-slot,filler) edges from BOTH corpora, kept if the RAW (unweighted)
    edge occurrence count SUMMED ACROSS BOTH CORPORA >= min_count -- so the column set is IDENTICAL across
    every blend weight (only the per-cell VALUE changes with alpha); blend arms differ in exactly the one
    variable the mechanism is about (the mixing rate), not in which columns exist."""
    def qualifying_edges(parsed):
        for sent in parsed:
            for tok, head, rel, _upos in sent:
                base = rel.split(":")[0]
                if base in S.ARG_SLOTS and 0 <= head < len(sent) and sent[head][3] == "VERB":
                    verb = sent[head][0]
                    if verb in union_word_index and tok in union_word_index:
                        yield verb, base, tok

    col_id = {}
    col_count = []

    def collect(parsed):
        rows = _arr("i"); cols = _arr("i")
        for verb, base, tok in qualifying_edges(parsed):
            cn = base + "\t" + tok
            j = col_id.get(cn)
            if j is None:
                j = len(col_id); col_id[cn] = j; col_count.append(0)
            col_count[j] += 1
            rows.append(union_word_index[verb]); cols.append(j)
        return rows, cols

    rows_s, cols_s = collect(parsed_small)
    rows_l, cols_l = collect(parsed_large)
    n_rows = len(union_word_index)
    cc = np.asarray(col_count, dtype=np.int64) if col_count else np.zeros(0, dtype=np.int64)
    keepmask = cc >= min_count
    n_keep = int(keepmask.sum())
    if n_keep == 0:
        z = sp.csr_matrix((n_rows, 1), dtype=np.float64)
        return z, z, 0
    remap = np.full(len(cc), -1, dtype=np.int64)
    remap[keepmask] = np.arange(n_keep)

    def to_csr(rows, cols):
        if not rows:
            return sp.csr_matrix((n_rows, n_keep), dtype=np.float64)
        rows_np = np.frombuffer(rows, dtype=np.int32).astype(np.int64)
        cols_np = np.frombuffer(cols, dtype=np.int32).astype(np.int64)
        nc = remap[cols_np]
        sel = nc >= 0
        M = sp.coo_matrix((np.ones(int(sel.sum())), (rows_np[sel], nc[sel])),
                           shape=(n_rows, n_keep), dtype=np.float64).tocsr()
        M.sum_duplicates()
        return M

    M_small = to_csr(rows_s, cols_s)
    M_large = to_csr(rows_l, cols_l)
    return M_small, M_large, n_keep


def blend_and_svd(M_small, M_large, alpha, union_word_index, seed):
    blended = ((1.0 - alpha) * M_small + alpha * M_large).tocsr()
    ppmi = S.ppmi_matrix(blended)
    vec = S.svd_vectors(ppmi, seed=seed)
    return S.dense_vec_cosine_fn(vec, union_word_index)


# --------------------------------------------------------------------------- corruption comparison
def paired_corruption_delta(base_arr, arm_a_arr, arm_b_arr, seed, n_boot):
    """Paired-bootstrap delta of the RIGHT->WRONG corruption rate (arm_a - arm_b), resampled over the SAME
    base-right item indices each replicate (matched pairs -- same discipline as G.paired_delta_acc).
    separated_below=True means arm_a's corruption rate is CI-separated BELOW arm_b's (arm_a is safer)."""
    base = np.asarray(base_arr, dtype=int)
    a = np.asarray(arm_a_arr, dtype=int)
    b = np.asarray(arm_b_arr, dtype=int)
    right_idx = np.where(base == 1)[0]
    n = right_idx.size
    if n == 0:
        return {"delta": None, "ci": [None, None], "ci_half": None, "n": 0,
                "separated_above": False, "separated_below": False}
    a_r = a[right_idx]; b_r = b[right_idx]
    rng = np.random.default_rng(seed)
    ds = np.array([
        (float((a_r[idx] == 0).mean()) - float((b_r[idx] == 0).mean()))
        for idx in (rng.integers(0, n, n) for _ in range(n_boot))
    ])
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    d0 = float((a_r == 0).mean() - (b_r == 0).mean())
    return {"delta": round(d0, 4), "ci": [round(lo, 4), round(hi, 4)], "ci_half": round((hi - lo) / 2, 4),
            "n": int(n), "separated_above": bool(lo > 0), "separated_below": bool(hi < 0)}


# --------------------------------------------------------------------------- ARMS-MUST-DIFFER (META_RULE_AF)
def _digest_scorearr(arr):
    a = np.asarray([(-1 if x is None else int(x)) for x in arr], dtype=np.int8)
    return hashlib.sha256(a.tobytes()).hexdigest()


def _arms_must_differ(arms_scores):
    digests = {name: _digest_scorearr(arr) for name, arr in arms_scores.items()}
    names = sorted(digests)
    dup = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                dup.append((names[i], names[j]))
    return digests, dup


# --------------------------------------------------------------------------- start marker / crash diagnostic
def _write_start_marker(expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(exc):
    diag = {"anchor_name": ANCHOR, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_metrics(metrics):
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUTPUT_DIR, "metrics.json"), flush=True)


# --------------------------------------------------------------------------- self-test (formula, no corpus)
def self_test():
    ok = True

    # (1) zscore_params + make_ensemble_sim: hand-worked, known channel values, verify mean/max fusion
    # arithmetic AND the never-discard fallback (channel b undefined for one candidate).
    table_a = {("q", "x"): 1.0, ("q", "y"): 3.0, ("q", "z"): 5.0}
    table_b = {("q", "x"): 10.0, ("q", "y"): 10.0}   # ("q","z") intentionally undefined in channel b
    def fake_sim(table):
        return lambda q, c: table.get((q, c))
    sim_a = fake_sim(table_a); sim_b = fake_sim(table_b)
    toy_items = [{"query": "q", "cand": ["x", "y", "z"], "target": "x"}]
    mean_a, std_a = zscore_params(sim_a, toy_items)
    mean_b, std_b = zscore_params(sim_b, toy_items)
    exp_mean_a = float(np.mean([1.0, 3.0, 5.0])); exp_std_a = float(np.std([1.0, 3.0, 5.0]))
    ok_z = (abs(mean_a - exp_mean_a) < 1e-9 and abs(std_a - exp_std_a) < 1e-9
            and abs(mean_b - 10.0) < 1e-9 and std_b == 1.0)
    fused_mean = make_ensemble_sim(sim_a, mean_a, std_a, sim_b, mean_b, std_b, "mean")
    fused_max = make_ensemble_sim(sim_a, mean_a, std_a, sim_b, mean_b, std_b, "max")
    za_x = (1.0 - mean_a) / std_a; zb_x = (10.0 - mean_b) / std_b
    exp_fm_x = (za_x + zb_x) / 2.0; got_fm_x = fused_mean("q", "x")
    exp_fx_x = max(za_x, zb_x); got_fx_x = fused_max("q", "x")
    za_z = (5.0 - mean_a) / std_a
    got_fm_z = fused_mean("q", "z")     # b undefined at z -> must fall back to channel a alone
    ok_f = (abs(got_fm_x - exp_fm_x) < 1e-9 and abs(got_fx_x - exp_fx_x) < 1e-9
            and abs(got_fm_z - za_z) < 1e-9)
    print("[self-test] zscore+ensemble fusion: mean(x)=%.4f(exp %.4f) max(x)=%.4f(exp %.4f) "
          "fallback(z,b undefined)=%.4f(exp %.4f) -> %s"
          % (got_fm_x, exp_fm_x, got_fx_x, exp_fx_x, got_fm_z, za_z, "OK" if (ok_z and ok_f) else "FAIL"),
          flush=True)
    ok = ok and ok_z and ok_f

    # (2) build_selpref_union_matrices: tiny synthetic parse, two DIFFERENT-size corpora. Verify (a) edge
    # mass matches an INDEPENDENT count via S.build_selpref_cooc's own definition, (b) blend at alpha=0/1
    # reduces exactly to M_small/M_large, (c) column SET is IDENTICAL across every alpha.
    one_pair = [
        [("the", 1, "det", "DET"), ("cat", 2, "nsubj", "NOUN"), ("chased", 2, "ROOT", "VERB"),
         ("the", 4, "det", "DET"), ("mouse", 2, "dobj", "NOUN")],
        [("a", 1, "det", "DET"), ("dog", 2, "nsubj", "NOUN"), ("saw", 2, "ROOT", "VERB"),
         ("a", 4, "det", "DET"), ("bird", 2, "dobj", "NOUN")],
    ]
    parsed_small_t = one_pair * 5
    parsed_large_t = one_pair * 30
    words_t = sorted({t for s in (parsed_small_t + parsed_large_t) for (t, _h, _r, _u) in s})
    union_t = {w: i for i, w in enumerate(words_t)}
    M_s, M_l, ncol_t = build_selpref_union_matrices(parsed_small_t, parsed_large_t, union_t, min_count=1)
    ref_small, _ = S.build_selpref_cooc(parsed_small_t, union_t, min_count=1)
    ref_large, _ = S.build_selpref_cooc(parsed_large_t, union_t, min_count=1)
    mass_ok = (abs(float(M_s.sum()) - float(ref_small.sum())) < 1e-9
               and abs(float(M_l.sum()) - float(ref_large.sum())) < 1e-9)
    blend0 = ((1.0 - 0.0) * M_s + 0.0 * M_l).tocsr()
    blend1 = ((1.0 - 1.0) * M_s + 1.0 * M_l).tocsr()
    blend_mid = ((1.0 - 0.5) * M_s + 0.5 * M_l).tocsr()
    endpoint_ok = (abs(float((blend0 - M_s).sum())) < 1e-9 and abs(float((blend1 - M_l).sum())) < 1e-9)
    cols_fixed_ok = blend0.shape[1] == blend_mid.shape[1] == blend1.shape[1] == ncol_t
    ok_u = mass_ok and endpoint_ok and cols_fixed_ok
    print("[self-test] union matrices: mass_small=%.0f(ref %.0f) mass_large=%.0f(ref %.0f) "
          "endpoints_exact=%s cols_fixed_across_alpha=%s -> %s"
          % (float(M_s.sum()), float(ref_small.sum()), float(M_l.sum()), float(ref_large.sum()),
             endpoint_ok, cols_fixed_ok, "OK" if ok_u else "FAIL"), flush=True)
    ok = ok and ok_u

    # (3) paired_corruption_delta: hand-worked. base-right = idx{0,1,2,3} (4 items). arm_a wrong at 1/4,
    # arm_b (naive-GROWN proxy) wrong at 2/4 -> arm_a corrupts LESS -> delta = 0.25 - 0.50 = -0.25.
    base_t = [1, 1, 1, 1, 0]
    arm_a_t = [1, 0, 1, 1, 0]
    arm_b_t = [0, 0, 1, 1, 0]
    d = paired_corruption_delta(base_t, arm_a_t, arm_b_t, seed=9, n_boot=200)
    ok_pcd = abs(d["delta"] - (-0.25)) < 1e-9
    print("[self-test] paired_corruption_delta: delta=%.4f(expect -0.2500) ci=%s -> %s"
          % (d["delta"], d["ci"], "OK" if ok_pcd else "FAIL"), flush=True)
    ok = ok and ok_pcd

    # (4) arms-must-differ (META_RULE_AF): identical arrays flagged as duplicate; distinct arrays are not.
    digests, dup = _arms_must_differ({"A": [1, 0, 1, None], "B": [1, 0, 1, None], "C": [0, 1, 1, None]})
    ok_afd = (("A", "B") in dup or ("B", "A") in dup) and not any(("C" in p) for p in dup)
    print("[self-test] arms_must_differ: dup_pairs=%s -> %s" % (dup, "OK" if ok_afd else "FAIL"), flush=True)
    ok = ok and ok_afd

    # (5) reuse-surface sanity: the exact G attributes run() below depends on all resolve (verbatim-reuse
    # contract -- if the safety-gate cell's API drifts, fail HERE in milliseconds, not mid-FULL-run).
    ok_g = all(hasattr(G, nm) for nm in
               ("build_paraphrase_items", "cache_path", "score_items", "boot_ci", "paired_delta_acc",
                "corruption_rate", "SEED", "MODE_CFG"))
    print("[self-test] G (exp_learner_safety_gate_v1) reuse surface present -> %s" % ("OK" if ok_g else "FAIL"),
          flush=True)
    ok = ok and ok_g

    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


# --------------------------------------------------------------------------- main run
def run(mode):
    cfg = G.MODE_CFG[mode]
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_start_marker(expected_n_units=1)

    print("[items] building paraphrase items (G.build_paraphrase_items, VERBATIM reuse) ...", flush=True)
    items = G.build_paraphrase_items(docs=None)
    force_words = set()
    for it in items:
        force_words.add(it["query"]); force_words.update(it["cand"])
    print("[items] n_items=%d n_force_words=%d" % (len(items), len(force_words)), flush=True)
    if len(items) < 10:
        print("[abort] fewer than 10 paraphrase items constructed; cannot score", flush=True)
        _write_metrics({"anchor_name": ANCHOR, "mode": mode, "verdict": "ABORT_TOO_FEW_ITEMS",
                         "elapsed_s": round(time.time() - t0, 1)})
        return 1

    print("[load] parsed caches (G.cache_path -- SAME POS-valid resolution as the reference run) ...",
          flush=True)
    parsed_small, ntok_small = S.load_parsed(G.cache_path(cfg["small_tok"]), cfg["small_tok"])
    parsed_large, ntok_large = S.load_parsed(G.cache_path(cfg["large_tok"]), cfg["large_tok"])
    print("[load] small: %d sent / %d tok | large: %d sent / %d tok"
          % (len(parsed_small), ntok_small, len(parsed_large), ntok_large), flush=True)

    toks_small = S.token_sents(parsed_small)
    toks_large = S.token_sents(parsed_large)
    index_small = S.build_vocab(toks_small, force_words, cfg["vocab_cap"], cfg["min_count"])
    index_large = S.build_vocab(toks_large, force_words, cfg["vocab_cap"], cfg["min_count"])
    print("[vocab] small=%d words | large=%d words" % (len(index_small), len(index_large)), flush=True)

    print("[build] NAIVE arms (BASELINE_SMALL / GROWN_LARGE_naive) -- identical construction to G.run() ...",
          flush=True)
    selpref_small, ncol_small = S.build_selpref_cooc(parsed_small, index_small, min_count=cfg["ctx_min_count"])
    selpref_large, ncol_large = S.build_selpref_cooc(parsed_large, index_large, min_count=cfg["ctx_min_count"])
    vec_small = S.svd_vectors(S.ppmi_matrix(selpref_small), seed=G.SEED)
    vec_large = S.svd_vectors(S.ppmi_matrix(selpref_large), seed=G.SEED)
    sim_baseline = S.dense_vec_cosine_fn(vec_small, index_small)
    sim_grown = S.dense_vec_cosine_fn(vec_large, index_large)
    print("[build] selpref cols: small=%d large=%d" % (ncol_small, ncol_large), flush=True)

    print("[build] ENSEMBLE_GROWTH: z-scored fusion of BASELINE_SMALL + GROWN_LARGE_naive cosines "
          "(keep-both-stores) ...", flush=True)
    mean_b, std_b = zscore_params(sim_baseline, items)
    mean_g, std_g = zscore_params(sim_grown, items)
    print("  z-score params: baseline mean=%.4f std=%.4f | grown mean=%.4f std=%.4f"
          % (mean_b, std_b, mean_g, std_g), flush=True)
    sim_ens_mean = make_ensemble_sim(sim_baseline, mean_b, std_b, sim_grown, mean_g, std_g, "mean")
    sim_ens_max = make_ensemble_sim(sim_baseline, mean_b, std_b, sim_grown, mean_g, std_g, "max")

    print("[build] REPLAY_INTERLEAVED_GROWTH: union SELPREF matrices for count-level blend ...", flush=True)
    union_words = sorted(set(index_small) | set(index_large))
    union_index = {w: i for i, w in enumerate(union_words)}
    M_small, M_large, ncol_union = build_selpref_union_matrices(parsed_small, parsed_large, union_index,
                                                                  min_count=cfg["ctx_min_count"])
    print("  union vocab=%d union cols=%d (fixed across all blend weights)" % (len(union_index), ncol_union),
          flush=True)
    sim_blend = {}
    for w in BLEND_WEIGHTS:
        tb = time.time()
        sim_blend[w] = blend_and_svd(M_small, M_large, w, union_index, seed=G.SEED)
        print("  [svd] blend alpha=%.2f done (%.1fs)" % (w, time.time() - tb), flush=True)

    sim_random = S.random_vec_cosine_fn(union_index, dim=S.SVD_K, seed=G.SEED + 5)

    print("[score] scoring all arms on all items ...", flush=True)
    r_baseline = G.score_items(items, sim_baseline)
    r_grown = G.score_items(items, sim_grown)
    r_ens_mean = G.score_items(items, sim_ens_mean)
    r_ens_max = G.score_items(items, sim_ens_max)
    r_blend = {w: G.score_items(items, sim_blend[w]) for w in BLEND_WEIGHTS}
    r_random = G.score_items(items, sim_random)

    n_total = len(items)
    core_idx = [i for i in range(n_total)
                if r_baseline[i] is not None and r_grown[i] is not None
                and r_ens_mean[i] is not None and r_ens_max[i] is not None
                and all(r_blend[w][i] is not None for w in BLEND_WEIGHTS)]
    n_core = len(core_idx)
    print("[coverage] n_total=%d baseline=%d grown=%d ens_mean=%d ens_max=%d blend25=%d blend50=%d "
          "blend75=%d random=%d | CORE_COMMON(all growth arms)=%d"
          % (n_total, sum(x is not None for x in r_baseline), sum(x is not None for x in r_grown),
             sum(x is not None for x in r_ens_mean), sum(x is not None for x in r_ens_max),
             sum(x is not None for x in r_blend[0.25]), sum(x is not None for x in r_blend[0.5]),
             sum(x is not None for x in r_blend[0.75]), sum(x is not None for x in r_random), n_core),
          flush=True)

    if n_core < 10:
        print("[abort] CORE_COMMON coverage < 10 items; cannot gate", flush=True)
        _write_metrics({"anchor_name": ANCHOR, "mode": mode, "verdict": "ABORT_INSUFFICIENT_COVERAGE",
                         "n_total_items": n_total, "n_core_common": n_core,
                         "elapsed_s": round(time.time() - t0, 1)})
        return 1

    base_core = [r_baseline[i] for i in core_idx]
    grown_core = [r_grown[i] for i in core_idx]
    ens_mean_core = [r_ens_mean[i] for i in core_idx]
    ens_max_core = [r_ens_max[i] for i in core_idx]
    blend_core = {w: [r_blend[w][i] for i in core_idx] for w in BLEND_WEIGHTS}
    random_core = [r_random[i] for i in core_idx if r_random[i] is not None]

    all_arms = {"ENSEMBLE_MEAN": ens_mean_core, "ENSEMBLE_MAX": ens_max_core,
                "BLEND_0.25": blend_core[0.25], "BLEND_0.50": blend_core[0.5], "BLEND_0.75": blend_core[0.75]}

    digests, dup_pairs = _arms_must_differ(dict(all_arms, BASELINE_SMALL=base_core,
                                                 GROWN_LARGE_naive=grown_core, RANDOM_floor=random_core
                                                 if len(random_core) == n_core else base_core))
    arms_differ_ok = (len(dup_pairs) == 0)
    print("[check] arms_must_differ (META_RULE_AF): dup_pairs=%s -> %s"
          % (dup_pairs, "OK" if arms_differ_ok else "VIOLATION"), flush=True)
    if not arms_differ_ok:
        print("[abort] META_RULE_AF VIOLATION: bit-identical arms detected -- implementation bug, "
              "refusing to report a verdict", flush=True)
        _write_metrics({"anchor_name": ANCHOR, "mode": mode, "verdict": "ABORT_ARMS_MUST_DIFFER_VIOLATION",
                         "dup_pairs": dup_pairs, "elapsed_s": round(time.time() - t0, 1)})
        return 1

    arm_acc = {
        "BASELINE_SMALL": G.boot_ci(base_core, G.SEED + 1, cfg["n_boot"]),
        "GROWN_LARGE_naive": G.boot_ci(grown_core, G.SEED + 2, cfg["n_boot"]),
        "ENSEMBLE_MEAN": G.boot_ci(ens_mean_core, G.SEED + ARM_SEED_OFFSET["ENSEMBLE_MEAN"], cfg["n_boot"]),
        "ENSEMBLE_MAX": G.boot_ci(ens_max_core, G.SEED + ARM_SEED_OFFSET["ENSEMBLE_MAX"], cfg["n_boot"]),
        "BLEND_0.25": G.boot_ci(blend_core[0.25], G.SEED + ARM_SEED_OFFSET["BLEND_0.25"], cfg["n_boot"]),
        "BLEND_0.50": G.boot_ci(blend_core[0.5], G.SEED + ARM_SEED_OFFSET["BLEND_0.50"], cfg["n_boot"]),
        "BLEND_0.75": G.boot_ci(blend_core[0.75], G.SEED + ARM_SEED_OFFSET["BLEND_0.75"], cfg["n_boot"]),
        "RANDOM_floor": G.boot_ci(random_core, G.SEED + 55, cfg["n_boot"]),
    }
    for nm, r in arm_acc.items():
        print("  %-18s acc=%s ci=%s n=%d" % (nm, r["acc"], r["ci"], r["n"]), flush=True)

    d_grown_vs_base = G.paired_delta_acc(grown_core, base_core, G.SEED + 10, cfg["n_boot"])
    gain_grown = d_grown_vs_base["delta"]
    print("  GROWN_LARGE_naive - BASELINE_SMALL accuracy delta (reference gain): %s" % d_grown_vs_base,
          flush=True)
    grown_corr = G.corruption_rate(base_core, grown_core, G.SEED + 20, cfg["n_boot"])
    print("  GROWN_LARGE_naive corruption right->wrong (reference): %s"
          % grown_corr["corruption_right_to_wrong"], flush=True)

    arm_report = {}
    safe_arms = []
    for nm, arr in all_arms.items():
        off = ARM_SEED_OFFSET[nm]
        d_acc_vs_base = G.paired_delta_acc(arr, base_core, G.SEED + 300 + off, cfg["n_boot"])
        d_acc_vs_grown = G.paired_delta_acc(arr, grown_core, G.SEED + 400 + off, cfg["n_boot"])
        arm_corr = G.corruption_rate(base_core, arr, G.SEED + 500 + off, cfg["n_boot"])
        d_corr_vs_grown = paired_corruption_delta(base_core, arr, grown_core, G.SEED + 600 + off, cfg["n_boot"])
        frac_retained = (d_acc_vs_base["delta"] / gain_grown) if gain_grown else None
        retains_gain = bool(d_acc_vs_base["separated_above"])
        keeps_most_gain = bool(retains_gain and frac_retained is not None and frac_retained >= 0.5)
        cuts_corruption = bool(d_corr_vs_grown["separated_below"])
        is_safe = bool(cuts_corruption and keeps_most_gain)
        if is_safe:
            safe_arms.append(nm)
        arm_report[nm] = {
            "accuracy": arm_acc[nm],
            "delta_acc_vs_baseline": d_acc_vs_base,
            "delta_acc_vs_grown_naive": d_acc_vs_grown,
            "fraction_of_grown_gain_retained": round(frac_retained, 4) if frac_retained is not None else None,
            "corruption_right_to_wrong": arm_corr["corruption_right_to_wrong"],
            "recovery_wrong_to_right": arm_corr["recovery_wrong_to_right"],
            "delta_corruption_vs_grown_naive": d_corr_vs_grown,
            "retains_gain_cisep": retains_gain,
            "cuts_corruption_cisep_below_naive": cuts_corruption,
            "keeps_most_gain_and_cuts_corruption": is_safe,
        }
        print("  %-12s acc_delta_vs_base=%s frac_gain_retained=%s corruption=%s corr_delta_vs_grown=%s "
              "SAFE=%s" % (nm, d_acc_vs_base, arm_report[nm]["fraction_of_grown_gain_retained"],
                            arm_corr["corruption_right_to_wrong"], d_corr_vs_grown, is_safe), flush=True)

    if safe_arms:
        verdict = "SAFE_GROWTH_MECHANISM_FOUND__" + "_".join(safe_arms)
    elif any(arm_report[nm]["cuts_corruption_cisep_below_naive"] for nm in arm_report):
        verdict = "PARTIAL_MITIGATION_CORRUPTION_CUT_BUT_GAIN_NOT_RETAINED"
    else:
        verdict = "NO_TESTED_MECHANISM_REDUCES_CORRUPTION_BELOW_NAIVE_CISEP__REPRESENTATION_GENUINELY_REORGANIZES"

    print("[verdict] %s | %.0fs" % (verdict, time.time() - t0), flush=True)

    metrics = {
        "anchor_name": ANCHOR, "mode": mode, "seed": G.SEED,
        "config": dict(cfg, svd_k=S.SVD_K, svd_p=S.SVD_P, ppmi_alpha=S.PPMI_ALPHA),
        "n_tokens": {"small": ntok_small, "large": ntok_large},
        "vocab": {"small": len(index_small), "large": len(index_large), "union": len(union_index)},
        "selpref_cols": {"small": ncol_small, "large": ncol_large, "union_blend": ncol_union},
        "n_total_items": n_total, "n_force_words": len(force_words),
        "coverage": {
            "baseline": sum(x is not None for x in r_baseline),
            "grown": sum(x is not None for x in r_grown),
            "ensemble_mean": sum(x is not None for x in r_ens_mean),
            "ensemble_max": sum(x is not None for x in r_ens_max),
            "blend_0.25": sum(x is not None for x in r_blend[0.25]),
            "blend_0.50": sum(x is not None for x in r_blend[0.5]),
            "blend_0.75": sum(x is not None for x in r_blend[0.75]),
            "random": sum(x is not None for x in r_random),
            "core_common": n_core,
        },
        "arms_differ_verified": arms_differ_ok,
        "arm_accuracy": arm_acc,
        "reference": {"grown_vs_baseline_accuracy_delta": d_grown_vs_base,
                      "grown_naive_corruption_right_to_wrong": grown_corr["corruption_right_to_wrong"],
                      "grown_naive_recovery_wrong_to_right": grown_corr["recovery_wrong_to_right"],
                      "prior_run_reference_numbers_MEASURED_at_data_exp_learner_safety_gate_v1_metrics_json":
                          {"baseline_acc": 0.0714, "grown_acc": 0.1494, "delta": 0.078,
                           "corruption_right_to_wrong": 0.2557, "note":
                               "prior-cell numbers on ITS OWN CORE_COMMON population (n=5529, 5-way "
                               "intersection incl. label/filler/full-shuffle controls this cell does not "
                               "build); this cell's own recomputed BASELINE_SMALL/GROWN_LARGE_naive numbers "
                               "above are the apples-to-apples reference for every delta in arm_report"}},
        "arm_report": arm_report,
        "safe_arms": safe_arms,
        "verdict": verdict,
        "elapsed_s": round(time.time() - t0, 1),
    }
    _write_metrics(metrics)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    try:
        return run(args.mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise


if __name__ == "__main__":
    sys.exit(main())
