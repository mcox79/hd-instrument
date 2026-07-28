"""Core: apply the PROMOTED hdlab.gated_fusion learned convex gate as the text+grounding
fusion operator, on ALREADY-SAVED reps from exp_scale_meaning_learn_arc_heldout_v3_grounding
(seed_7/seed_13 evalreps_seed_<N>.npz). NOT a retrain -- a lightweight measurement.

CASH-IN of the islanded gated_fusion capability (registry id gated_fusion_relation_inference,
HARD_PASS +0.297 MRR on the mammal-KG relation-inference cell, promoted to hdlab/gated_fusion.py
but never applied to the encoder's own text+grounding fusion, per
notes/prereg_stub_gated_fusion_text_grounding_fusion_QUEUED_2026-07-28.md). MOTIVATION (measured
this session on the grounding cell's own reported arms): ARM_FUSE_ZAVG (fixed 0.5/0.5 z-avg fusion)
helps semantic (RAW_TEXT ~0.583 -> ZAVG ~0.597, +0.014) but HURTS relational (RAW_TEXT ~0.632 ->
ZAVG ~0.611, -0.021) because RAW_GROUNDING is near-chance on relational (~0.560). A LEARNED gate
should be able to down-weight grounding on relational (recover toward text-alone) while still
up-weighting it on semantic (beat z-avg) -- this cell tests exactly that, per-axis.

DIRECTOR DESIGN-VERIFICATION (2026-07-28, addressed here, both closed):
1. TWO INDEPENDENT SCALAR GATES, not one global lambda. hdlab.gated_fusion.learn_lambda fits a
   single scalar; a single global lambda cannot simultaneously down-weight grounding on relational
   AND up-weight it on semantic. This cell fits lambda_semantic and lambda_relational SEPARATELY,
   each via its own score_fn (own metric, own VAL sample) -- two independent calls into the SAME
   promoted mechanism (hdlab.gated_fusion.gated_table / learn_lambda), not a new mechanism.
2. VAL != TEST, runtime-asserted. Both fits use ONLY split["train_eval_idx"] (TRAIN-side) rows as
   the VAL sample; split["held_idx"] (TEST) is NEVER touched during fitting. An explicit
   `assert not (set(val_ids) & set(held_idx))` fires before every fit (LEAK_ASSERT_VAL_TEST_DISJOINT
   in metrics); this is a HARD structural check (raises, not a soft flag) since split["held_idx"] and
   split["train_eval_idx"] are disjoint BY CONSTRUCTION (build_split excludes held from train_eligible)
   but the assertion defends against any future refactor silently breaking that invariant.

MECHANISM MAPPING (this cell's own choice, documented so lambda direction is never ambiguous):
  primary_codes  = GROUNDING channel (per-query/per-concept z-scored cosine vs candidates).
                   Sometimes near-chance (relational) or entirely ABSENT for a concept with zero
                   grounding-norm coverage ("cold": ||ground[i]||==0, i.e. all 20 dims zero after
                   build_grounding_reps' nan-fill+normalize -- verified true zero-norm for
                   no-coverage concepts, not an approximation).
  fallback_codes = TEXT channel (always present -- every eligible concept has an encoder rep).
  gated_table's cold-row contract ("support_deg[row]==0 -> pure fallback") therefore does EXACTLY
  the right thing here: a concept with zero grounding coverage gets pure TEXT regardless of the
  fitted lambda, never a corrupted mix with an all-zero grounding vector.
  lambda=0.0 -> pure GROUNDING (primary). lambda=1.0 -> pure TEXT (fallback). GRID includes BOTH
  endpoints (this cell's OWN broadening of gated_fusion's "grid must include 1.0" discipline to
  ALSO include 0.0 -- symmetric recovery-guarantee: the gate can never do worse than EITHER pure
  endpoint on VAL, whichever channel dominates for that axis). "Recovers toward text-alone" (the
  honest ceiling on relational, since grounding carries ~no relational signal) corresponds to a
  fitted lambda near 1.0 -- NOT lambda->0; this cell's docstrings/fields always state pure-channel
  meaning explicitly (lambda_convention field in metrics) so no reader has to infer direction.

FUSION LEVEL: score-level (per-query z-scored cosine vectors), NOT raw-embedding-level. TEXT reps
(d_model-dim, e.g. 512) and GROUNDING reps (20-dim) live in DIFFERENT-dimensional spaces -- a raw
convex blend of the two embeddings is not well-formed (this is the projection-step gap the
2026-07-28 testbed stub flagged explicitly: "may need a projection step before fusion is
well-formed"). The existing sibling cell's OWN ARM_FUSE_ZAVG already solves this by fusing at the
SCORE level (0.5*(z(cos_text) + z(cos_ground))); this cell applies gated_fusion.gated_table to the
SAME z-scored score vectors (primary=z(cos_ground), fallback=z(cos_text)) instead of the fixed
0.5/0.5 -- a direct, dimensionally-honest generalization of the SAME mechanism z-avg already uses,
now with a LEARNED weight instead of a fixed one. gated_table's per-row API (Xp[s] = (1-lam)*primary
[s] + lam*fallback[s]) is agnostic to what "code" means -- a per-query z-scored candidate-score
vector is a legitimate "code" as much as a per-concept embedding is; this is a genuine, unmodified
call into the promoted module for BOTH axes (semantic: one batched NxN call via learn_lambda;
relational: one gated_table call per query per grid point, since relational candidate sets are
variable-length across queries and gated_table's batched-table API assumes uniform row length,
which the semantic NxN structure satisfies but relational's variable pos+neg count per query does
not -- documented here so the difference in call pattern between the two axes is never mysterious).

CORRECTNESS SELF-CHECK (mandatory, not just self-test): at lambda=0.5, gated_table's formula
reduces EXACTLY to 0.5*(primary+fallback) = 0.5*(z(cos_ground)+z(cos_text)) = the SAME formula the
landed grounding cell's own ARM_FUSE_ZAVG uses. This cell asserts its own lambda=0.5 recompute
matches (within 1e-4) the imported _r._eval_semantic_set / _r.relational_eval FUSE_ZAVG_ARM output
on the IDENTICAL held-out query set -- a strong, cheap, structural proof this cell's gate machinery
is wired correctly (not a reimplementation-drift risk), BEFORE trusting the fitted-lambda numbers.

REUSE DISCIPLINE (mirrors the grounding cell's own convention): imports
exp_scale_meaning_learn_arc_heldout_v3_relobj (alias _r) UNCHANGED -- _load_eval_bundle (the
EXISTING "EVAL-ONLY re-run" npz loader), select_fusion_on_train, semantic_eval, relational_eval,
_cos_matrix, _zscore_rows, _auc_from_scores, RAW_ARM/TEXT_ARM/FUSE_ZAVG_ARM constants. The relobj
module file is NEVER edited (read-only import; a separate OS process may still be training seed_13
on the GPU box -- importing this module here does not touch it). THE NEW CODE (genuinely this
cell's own): the two independent gate fits + applications, the relational per-query gate-eval loop,
the lambda=0.5-reduces-to-zavg cross-check, and the verdict/band logic.

HARD INVARIANTS: LEAK-PROOF (VAL from train_eval_idx only, runtime-asserted disjoint from
held_idx/TEST). CPU-only, lightweight (loads a saved ~64MB npz + numpy/torch ops over a few
thousand concepts; no training). ASCII-only.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: GATE score vectors hash-differ from pure TEXT/GROUNDING at fitted lambda
#   whenever fitted lambda is not itself 0.0 or 1.0 (exempted pair when lambda lands on an endpoint
#   -- honest by-construction identity, declared not hidden)
# - final_metrics_atomicity: tmp_replace (write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base=0.5 exactly; this cell reuses the sibling cell's own validity
#   controls (COLLAPSE/POPULARITY bands, RAW_SIGNAL_MIN) by citation -- see baseline cross-check
# - baseline_in_band: verified via the lambda=0.5 reduces-to-ZAVG cross-check against the landed
#   sibling cell's own already-validated arms (RAW_SIGNAL_MIN / COLLAPSE_BAND enforced there)
# - discriminator survives scale: N/A -- this is a measurement over the FULL npz already at full
#   scale (no smaller "smoke scale" exists for a read-only measurement); self-test proves code-path
#   correctness at N~20 synthetic concepts instead (option per exp_dev.md discriminator-survives-scale
#   gate: real_code_path self-test substitutes for a smoke-at-full-N when there IS no smaller scale)
# - HARD_PASS strictly above floor: margins specified per-axis in the pre-reg (not this file)
# - HP_SCOPE: gates apply to the GATE arm vs ZAVG/TEXT_ONLY on TEST (held_idx); VAL-fit numbers are
#   model-selection diagnostics only, never gated
# - cardinality_ok: EXPECTED_N_UNITS = 1 seed per cell file (chunked, see wrapper); no sweep axis
# - per-unit failure-class instrumentation: specific except classes -> metrics, no bare except
# - calibration_check: default_ok_for_this_regime (AUC base 0.5 analytic; z-score+cross-check
#   validity witnesses it empirically against the already-validated sibling cell's own controls)
# - deterministic seeding: fixed int seeds, sorted() everywhere, no hash()/list(set())
# - real_code_path: --self-test constructs REAL synthetic bundle + calls the REAL gated_table /
#   learn_lambda / _r._cos_matrix / _r._zscore_rows / _r._auc_from_scores functions at N~20
# - progress_logging: print_flush_true (this cell's total wall time is expected << 1800s, so the
#   §17 mandatory heartbeat threshold does not apply, but flush=True is used anyway, cheap defense)
# - device-agnostic: CPU-only by design (no torch.cuda calls anywhere in this file)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    record_gate,
    write_metrics,
)

# Read-only import of the sibling cell's leak-proof eval pipeline + the promoted gate module.
from experiments import exp_scale_meaning_learn_arc_heldout_v3_relobj as _r  # noqa: E402
from hdlab.gated_fusion import gated_table, learn_lambda  # noqa: E402

ANCHOR_BASE = "gated_fusion_text_grounding_encoder"
NPZ_DIR = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_grounding")

# lambda=0.0 -> pure GROUNDING (primary); lambda=1.0 -> pure TEXT (fallback). See docstring.
GRID = [round(0.1 * i, 2) for i in range(0, 11)]
VAL_CAP_SEM = 1500          # mirrors _r.TRAIN_SELECT_CAP (semantic VAL sample cap)
VAL_CAP_REL = 600           # relational VAL pseudo-query cap (own constant; cheaper per-query cost)
MIN_VAL_N_SEM = 10          # floor below which _r._eval_semantic_set itself returns None
MIN_VAL_N_REL = 40          # floor below which relational gate-fit falls back to lambda=1.0 (pure TEXT)
ZAVG_XCHECK_TOL = 1e-4      # lambda=0.5 must reduce to FUSE_ZAVG within this tolerance


def _log(anchor, msg):
    print("[%s] %s" % (anchor, msg), flush=True)


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=anchor_name, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node(),
                  cuda=bool(torch.cuda.is_available()))
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), anchor_name=anchor_name)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Shared helpers (pure; small; safe to define locally rather than re-import
# private nested functions from _r)
# ---------------------------------------------------------------------------
def _z1(x):
    s = x.std()
    return (x - x.mean()) / (s + 1e-8) if s > 1e-12 else x - x.mean()


def _cold_mask(ground, idx):
    """True where a concept has ZERO grounding-norm coverage (all 20 dims zero)."""
    return np.linalg.norm(ground[idx], axis=1) <= 1e-8


def _assert_val_test_disjoint(val_ids, held_idx, tag):
    held_set = set(int(x) for x in np.asarray(held_idx).tolist())
    overlap = set(int(x) for x in val_ids) & held_set
    if overlap:
        raise RuntimeError("LEAK_ASSERT_VAL_TEST_DISJOINT FAILED (%s): %d ids overlap held-out TEST: %s"
                           % (tag, len(overlap), sorted(overlap)[:10]))
    return True


# ---------------------------------------------------------------------------
# SEMANTIC axis: uniform NxN structure -> direct batched gated_fusion.learn_lambda call
# ---------------------------------------------------------------------------
def _semantic_score_mats(ground, text, idx):
    idx = np.array(sorted(int(i) for i in idx), dtype=np.int64)
    cg = _r._cos_matrix(ground, idx, idx)
    ct = _r._cos_matrix(text, idx, idx)
    cg_z = _r._zscore_rows(cg)
    ct_z = _r._zscore_rows(ct)
    return idx, cg_z, ct_z


def _semantic_auc_score_fn(elig, lex_str):
    n = elig.shape[0]

    def score_fn(Xp):
        Xp_np = Xp.numpy() if isinstance(Xp, torch.Tensor) else Xp
        aucs = []
        for qi in range(n):
            same = np.array([lex_str[j] == lex_str[qi] for j in range(n)])
            same[qi] = False
            cand = np.ones(n, dtype=bool)
            cand[qi] = False
            pos = same[cand]
            if pos.sum() == 0 or pos.sum() == pos.shape[0]:
                continue
            au = _r._auc_from_scores(Xp_np[qi][cand], pos)
            if au is not None:
                aucs.append(au)
        return float(np.mean(aucs)) if aucs else 0.0

    return score_fn


def fit_lambda_semantic(ground, text, counts, universe, split, seed):
    """Fit lambda_semantic on a TRAIN-eval VAL sample (leak-proof; runtime-asserted disjoint
    from held_idx/TEST). Mirrors _r.select_fusion_on_train's own VAL-sampling convention."""
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    tr = [int(i) for i in split["train_eval_idx"].tolist()
          if have_text[i] and universe["lexnames"][i] is not None]
    tr = sorted(tr)
    if len(tr) > VAL_CAP_SEM:
        rng = np.random.default_rng(seed + 4001)
        tr = sorted(rng.choice(np.array(tr), size=VAL_CAP_SEM, replace=False).tolist())
    _assert_val_test_disjoint(tr, split["held_idx"], "semantic_fit")
    n = len(tr)
    if n < MIN_VAL_N_SEM:
        return 1.0, float("nan"), {}, True, n   # too few -> pure TEXT (fallback), safest default
    idx, cg_z, ct_z = _semantic_score_mats(ground, text, tr)
    lex_str = [universe["lexnames"][i] for i in idx]
    support = (~_cold_mask(ground, idx)).astype(np.int64)
    Xg = torch.from_numpy(cg_z.astype(np.float32))
    Xt = torch.from_numpy(ct_z.astype(np.float32))
    X0 = torch.zeros_like(Xt)
    held_ids = list(range(n))
    support_deg = {i: int(support[i]) for i in range(n)}
    score_fn = _semantic_auc_score_fn(idx, lex_str)
    lam, score, curve, used_fb = learn_lambda(
        X0, Xg, Xt, held_ids, support_deg, score_fn, GRID, val_n=n, min_val_n=MIN_VAL_N_SEM)
    return lam, score, curve, used_fb, n


def apply_gate_semantic(ground, text, universe, split, lam):
    """Apply the FITTED lambda (no re-fit) to held_idx (TEST). Returns (auc, n_query, n_concepts)."""
    held = split["held_idx"]
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    elig = [int(i) for i in held.tolist() if have_text[i]]
    idx, cg_z, ct_z = _semantic_score_mats(ground, text, elig)
    n = idx.shape[0]
    lex_str = [universe["lexnames"][i] for i in idx]
    support = (~_cold_mask(ground, idx)).astype(np.int64)
    Xg = torch.from_numpy(cg_z.astype(np.float32))
    Xt = torch.from_numpy(ct_z.astype(np.float32))
    Xp = gated_table(torch.zeros_like(Xt), Xg, Xt, list(range(n)),
                     {i: int(support[i]) for i in range(n)}, float(lam))
    Xp_np = Xp.numpy()
    score_fn = _semantic_auc_score_fn(idx, lex_str)
    auc = score_fn(Xp)
    n_cold = int((support == 0).sum())
    return auc, n, n_cold, Xp_np


# ---------------------------------------------------------------------------
# RELATIONAL axis: variable-length per-query candidate sets -> gated_table called
# once PER QUERY PER GRID POINT (documented departure from the batched API; same
# underlying formula/module, not a reimplementation).
# ---------------------------------------------------------------------------
def _build_relational_query_data(ground, text, adj, deg, query_ids, pool_ids, have_text, rng_seed,
                                 burn_shuffle_perm=False):
    """Mirrors _r.relational_eval's query-construction loop exactly (degree-matched negatives,
    same exclude-set / tie-break logic), parameterized over an arbitrary (query_ids, pool_ids) pair
    so it can serve BOTH the TRAIN-side VAL fit and the TEST(held_idx) application with the SAME
    code path (no drift between fit-time and apply-time query construction).

    burn_shuffle_perm: _r.relational_eval draws `rng.permutation(len(elig_q))` UP FRONT (to build
    its ARM_COLLAPSE_SHUFFLE text_sh control) BEFORE the per-query negative-sampling loop -- that
    permutation call advances the shared rng's state even though this function has no use for the
    shuffle arm itself. Pass True (used by apply_gate_relational, which must reproduce the EXACT
    same candidate/negative draws as the baseline arms it is compared against) to burn an
    identically-shaped permutation call first, so the per-query rng.integers() draws that follow
    line up exactly with _r.relational_eval's. False (default; used by the VAL fit, which compares
    against nothing external) skips the burn -- harmless, since VAL fit only needs internally
    self-consistent draws, not parity with a different function's rng consumption."""
    pool_ids = np.asarray(pool_ids, dtype=np.int64)
    train_set = set(int(x) for x in pool_ids.tolist())
    deg_bin = {}
    for t in pool_ids.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[pool_ids].max()) if pool_ids.shape[0] else 0
    rng = np.random.default_rng(rng_seed)
    elig_q = sorted(int(x) for x in query_ids if have_text[int(x)])
    if burn_shuffle_perm:
        _ = rng.permutation(len(elig_q))   # discarded; burns the same draws as _r.relational_eval
    out = []
    n_used = 0
    for h in elig_q:
        pos_neigh = sorted(j for j in adj[h] if j in train_set and have_text[j])
        if not pos_neigh:
            continue
        pos_neigh = pos_neigh[:8]
        exclude = set(adj[h]) | {h}
        negs, used, ok = [], set(), True
        for p in pos_neigh:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                ok = False
                break
            negs.append(picked)
            used.add(picked)
        if not ok or not negs:
            continue
        n_used += 1
        cand = np.array(pos_neigh + negs, dtype=np.int64)
        posm = np.array([True] * len(pos_neigh) + [False] * len(negs))
        cg = ground[h] @ ground[cand].T
        ct = text[h] @ text[cand].T
        cg_z1 = _z1(cg)
        ct_z1 = _z1(ct)
        supp = 0 if np.linalg.norm(ground[h]) <= 1e-8 else 1
        out.append((cg_z1, ct_z1, posm, supp))
    return out, n_used


def _gate_auc_over_queries(query_data, lam):
    aucs = []
    for cg_z1, ct_z1, posm, supp in query_data:
        primary = torch.from_numpy(cg_z1.astype(np.float32)).unsqueeze(0)
        fallback = torch.from_numpy(ct_z1.astype(np.float32)).unsqueeze(0)
        X0 = torch.zeros_like(fallback)
        Xp = gated_table(X0, primary, fallback, [0], {0: int(supp)}, float(lam))
        au = _r._auc_from_scores(Xp[0].numpy(), posm)
        if au is not None:
            aucs.append(au)
    return float(np.mean(aucs)) if aucs else None


def fit_lambda_relational(ground, text, universe, split, adj, deg, seed):
    """Fit lambda_relational on a TRAIN-only pseudo-held split (leak-proof; runtime-asserted
    disjoint from held_idx/TEST): sample VAL query ids from train_eval_idx, use the REMAINING
    train_eval_idx (excluding the VAL sample) as the matched-negative pool."""
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    tr_all = sorted(int(i) for i in split["train_eval_idx"].tolist())
    rng = np.random.default_rng(seed + 5001)
    # Reserve at most half of train_eval as VAL queries so a non-empty matched-negative POOL
    # always remains (a val_size == len(tr_all) split would leave zero pool -> zero queries
    # constructible, a degenerate all-consumed-by-VAL edge case at small scale).
    val_size = min(VAL_CAP_REL, max(1, len(tr_all) // 2))
    val_ids = sorted(rng.choice(np.array(tr_all), size=val_size, replace=False).tolist())
    _assert_val_test_disjoint(val_ids, split["held_idx"], "relational_fit")
    val_set = set(val_ids)
    pool_ids = np.array(sorted(i for i in tr_all if i not in val_set), dtype=np.int64)
    query_data, n_used = _build_relational_query_data(
        ground, text, adj, deg, val_ids, pool_ids, have_text, rng_seed=seed + 5101)
    if n_used < MIN_VAL_N_REL:
        return 1.0, float("nan"), {}, True, n_used   # too few -> pure TEXT (fallback)
    curve = {lam: _gate_auc_over_queries(query_data, lam) for lam in GRID}
    valid = {lam: v for lam, v in curve.items() if v is not None}
    if not valid:
        return 1.0, float("nan"), curve, True, n_used
    best_lam = max(valid, key=valid.get)
    return float(best_lam), float(valid[best_lam]), curve, False, n_used


def apply_gate_relational(ground, text, universe, split, adj, deg, seed, lam):
    """Apply the FITTED lambda (no re-fit) to held_idx (TEST), using the SAME query-construction
    seed (seed+71) as _r.relational_eval so the candidate sets are IDENTICAL to the baseline arms
    it reports -- apples-to-apples AUC comparison, not a re-drawn (and therefore non-comparable)
    negative sample."""
    have_text = np.linalg.norm(text, axis=1) > 1e-8
    held = split["held_idx"]
    train_pool = split["train_eval_idx"]
    query_data, n_used = _build_relational_query_data(
        ground, text, adj, deg, held.tolist(), train_pool, have_text, rng_seed=seed + 71,
        burn_shuffle_perm=True)
    auc = _gate_auc_over_queries(query_data, lam)
    n_cold = sum(1 for _, _, _, s in query_data if s == 0)
    return auc, n_used, n_cold


# ---------------------------------------------------------------------------
# One seed: load bundle, recompute baselines (reused, unmodified functions),
# fit+apply both gates, cross-check vs ZAVG at lambda=0.5.
# ---------------------------------------------------------------------------
def run_one_seed(seed, anchor_name, npz_path, output_dir, run_mode="full"):
    t0 = time.perf_counter()
    if not os.path.exists(npz_path):
        raise FileNotFoundError(
            "NPZ_NOT_LANDED: %s does not exist -- the grounding cell's evalreps for this seed "
            "have not landed yet; do not dispatch this seed until it has." % npz_path)
    _log(anchor_name, "loading eval bundle: %s" % npz_path)
    bundle, _raw = _r._load_eval_bundle(npz_path)
    universe, split = bundle["universe"], bundle["split"]
    ground, text = bundle["ground"], bundle["text_reps"]
    text_rand, counts = bundle["text_rand"], bundle["counts"]
    adj, deg, n_shards = bundle["adj"], bundle["deg"], bundle["n_shards"]
    w_star, selected_arm = bundle["w_star"], bundle["selected_arm"]
    _log(anchor_name, "  K=%d held=%d train_eval=%d w_star=%.3f selected_arm=%s"
        % (universe["K"], split["held_idx"].shape[0], split["train_eval_idx"].shape[0],
           w_star, selected_arm))

    _log(anchor_name, "recomputing baseline arms (reused, UNMODIFIED sibling-cell functions)...")
    sem_baseline = _r.semantic_eval(ground, text, text_rand, counts, universe, split, seed,
                                    w_star, selected_arm)
    rel_baseline = _r.relational_eval(ground, text, counts, universe, split, adj, deg, n_shards,
                                      seed, w_star)
    _log(anchor_name, "  baseline sem: TEXT=%.4f ZAVG=%.4f GROUNDING=%.4f (n_query=%d)"
        % (sem_baseline[_r.TEXT_ARM], sem_baseline[_r.FUSE_ZAVG_ARM], sem_baseline[_r.RAW_ARM],
           sem_baseline["_n_query"]))
    _log(anchor_name, "  baseline rel: TEXT=%.4f ZAVG=%.4f GROUNDING=%.4f (n_query=%d)"
        % (rel_baseline[_r.TEXT_ARM], rel_baseline[_r.FUSE_ZAVG_ARM], rel_baseline[_r.RAW_ARM],
           rel_baseline["_n_query"]))

    # --- Correctness self-check: lambda=0.5 MUST reduce to FUSE_ZAVG (see module docstring) ---
    sem_at_half, n_sem_test, n_sem_cold, _ = apply_gate_semantic(ground, text, universe, split, 0.5)
    rel_at_half, n_rel_test, n_rel_cold = apply_gate_relational(
        ground, text, universe, split, adj, deg, seed, 0.5)
    sem_xcheck_delta = abs(sem_at_half - sem_baseline[_r.FUSE_ZAVG_ARM])
    rel_xcheck_delta = abs(rel_at_half - rel_baseline[_r.FUSE_ZAVG_ARM])
    if sem_xcheck_delta > ZAVG_XCHECK_TOL:
        raise RuntimeError(
            "XCHECK_FAIL_SEMANTIC_LAMBDA_0.5_NOT_ZAVG: gate@0.5=%.6f vs sibling ZAVG=%.6f "
            "(delta=%.6f > tol=%.6f) -- gate machinery does not reduce correctly; do not trust "
            "fitted-lambda numbers until this is fixed" % (
                sem_at_half, sem_baseline[_r.FUSE_ZAVG_ARM], sem_xcheck_delta, ZAVG_XCHECK_TOL))
    if rel_xcheck_delta > ZAVG_XCHECK_TOL:
        raise RuntimeError(
            "XCHECK_FAIL_RELATIONAL_LAMBDA_0.5_NOT_ZAVG: gate@0.5=%.6f vs sibling ZAVG=%.6f "
            "(delta=%.6f > tol=%.6f) -- gate machinery does not reduce correctly; do not trust "
            "fitted-lambda numbers until this is fixed" % (
                rel_at_half, rel_baseline[_r.FUSE_ZAVG_ARM], rel_xcheck_delta, ZAVG_XCHECK_TOL))
    _log(anchor_name, "  XCHECK PASS: gate@lambda=0.5 == sibling FUSE_ZAVG (sem delta=%.6f, rel delta=%.6f)"
        % (sem_xcheck_delta, rel_xcheck_delta))

    # --- Fit + apply, per axis, independently ---
    _log(anchor_name, "fitting lambda_semantic on TRAIN-eval VAL (leak-proof)...")
    lam_sem, val_score_sem, curve_sem, used_fb_sem, n_val_sem = fit_lambda_semantic(
        ground, text, counts, universe, split, seed)
    sem_gate_auc, n_sem_q, n_sem_cold2, sem_Xp = apply_gate_semantic(
        ground, text, universe, split, lam_sem)
    _log(anchor_name, "  lambda_semantic=%.3f (val_score=%.4f, n_val=%d, used_fallback=%s) -> TEST_AUC=%.4f"
        % (lam_sem, val_score_sem, n_val_sem, used_fb_sem, sem_gate_auc))

    _log(anchor_name, "fitting lambda_relational on TRAIN-only pseudo-held VAL (leak-proof)...")
    lam_rel, val_score_rel, curve_rel, used_fb_rel, n_val_rel = fit_lambda_relational(
        ground, text, universe, split, adj, deg, seed)
    rel_gate_auc, n_rel_q, n_rel_cold2 = apply_gate_relational(
        ground, text, universe, split, adj, deg, seed, lam_rel)
    _log(anchor_name, "  lambda_relational=%.3f (val_score=%.4f, n_val=%d, used_fallback=%s) -> TEST_AUC=%.4f"
        % (lam_rel, val_score_rel, n_val_rel, used_fb_rel, rel_gate_auc))

    # --- arms_differ (META_RULE_AF): GATE score vectors vs pure TEXT/GROUNDING at fitted lambda ---
    import hashlib
    def _dig(a):
        return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
    _, _, _, puretext_Xp = apply_gate_semantic(ground, text, universe, split, 1.0)
    _, _, _, puregrd_Xp = apply_gate_semantic(ground, text, universe, split, 0.0)
    arm_digests = {"GATE_SEM": _dig(sem_Xp), "PURE_TEXT": _dig(puretext_Xp), "PURE_GROUNDING": _dig(puregrd_Xp)}
    arms_differ_exempted = []
    if abs(lam_sem - 1.0) < 1e-9:
        arms_differ_exempted.append(("GATE_SEM", "PURE_TEXT"))
    elif abs(lam_sem - 0.0) < 1e-9:
        arms_differ_exempted.append(("GATE_SEM", "PURE_GROUNDING"))
    else:
        assert arm_digests["GATE_SEM"] != arm_digests["PURE_TEXT"], "META_RULE_AF: GATE==PURE_TEXT unexpectedly"
        assert arm_digests["GATE_SEM"] != arm_digests["PURE_GROUNDING"], "META_RULE_AF: GATE==PURE_GROUNDING unexpectedly"

    elapsed = time.perf_counter() - t0
    per_seed = dict(
        seed=seed, run_mode=run_mode, elapsed_s=elapsed,
        npz_path=npz_path, K=int(universe["K"]),
        n_held=int(split["held_idx"].shape[0]), n_train_eval=int(split["train_eval_idx"].shape[0]),
        baseline=dict(
            semantic=dict(TEXT=sem_baseline[_r.TEXT_ARM], ZAVG=sem_baseline[_r.FUSE_ZAVG_ARM],
                         GROUNDING=sem_baseline[_r.RAW_ARM], n_query=sem_baseline["_n_query"]),
            relational=dict(TEXT=rel_baseline[_r.TEXT_ARM], ZAVG=rel_baseline[_r.FUSE_ZAVG_ARM],
                            GROUNDING=rel_baseline[_r.RAW_ARM], n_query=rel_baseline["_n_query"]),
        ),
        xcheck={"sem_gate_at_0.5": sem_at_half, "sem_zavg": sem_baseline[_r.FUSE_ZAVG_ARM],
                "sem_delta": sem_xcheck_delta, "rel_gate_at_0.5": rel_at_half,
                "rel_zavg": rel_baseline[_r.FUSE_ZAVG_ARM], "rel_delta": rel_xcheck_delta,
                "tol": ZAVG_XCHECK_TOL, "pass_": True},
        gate_semantic=dict(lambda_star=lam_sem, val_score=val_score_sem, n_val=n_val_sem,
                          used_fallback=used_fb_sem, curve=curve_sem, test_auc=sem_gate_auc,
                          n_test_query=n_sem_q, n_test_cold=n_sem_cold2),
        gate_relational=dict(lambda_star=lam_rel, val_score=val_score_rel, n_val=n_val_rel,
                            used_fallback=used_fb_rel, curve=curve_rel, test_auc=rel_gate_auc,
                            n_test_query=n_rel_q, n_test_cold=n_rel_cold2),
        arm_digests=arm_digests, arms_differ_exempted=arms_differ_exempted,
        lambda_convention="lambda=0.0 -> pure GROUNDING (primary); lambda=1.0 -> pure TEXT (fallback)",
        val_test_leak_assert="PASS (runtime-asserted disjoint at both fit calls)",
    )
    return per_seed


def _fmt_seed_verdict(per_seed):
    """Per-seed HONEST verdict (this file alone cannot claim BOTH-seeds HARD_PASS -- see pre-reg)."""
    gs, gr = per_seed["gate_semantic"], per_seed["gate_relational"]
    bs, br = per_seed["baseline"]["semantic"], per_seed["baseline"]["relational"]
    sem_margin_vs_zavg = gs["test_auc"] - bs["ZAVG"]
    rel_margin_vs_zavg = gr["test_auc"] - br["ZAVG"]
    rel_dist_to_text = gr["test_auc"] - br["TEXT"]
    sem_dist_to_text = gs["test_auc"] - bs["TEXT"]
    gates = [
        record_gate("sem_gate_beats_zavg", sem_margin_vs_zavg, 0.0, ">", note="semantic axis"),
        record_gate("rel_gate_beats_zavg", rel_margin_vs_zavg, 0.0, ">", note="relational axis"),
        record_gate("rel_gate_within_0.02_of_text", abs(rel_dist_to_text), 0.02, "<=",
                   note="honest relational ceiling = recover TOWARD text, not exceed it"),
    ]
    return dict(sem_margin_vs_zavg=sem_margin_vs_zavg, rel_margin_vs_zavg=rel_margin_vs_zavg,
               rel_dist_to_text=rel_dist_to_text, sem_dist_to_text=sem_dist_to_text, gates=gates)


# ---------------------------------------------------------------------------
# Self-test: tiny synthetic bundle, exercises the REAL functions above at N~20.
# ---------------------------------------------------------------------------
def _make_synthetic_bundle(n=20, seed=0):
    rng = np.random.default_rng(seed)
    d_text = 12
    text = rng.normal(size=(n, d_text)).astype(np.float32)
    text /= (np.linalg.norm(text, axis=1, keepdims=True) + 1e-8)
    text_rand = rng.normal(size=(n, d_text)).astype(np.float32)
    text_rand /= (np.linalg.norm(text_rand, axis=1, keepdims=True) + 1e-8)
    ground = rng.normal(size=(n, 20)).astype(np.float32) * 0.5
    # 3 concepts have ZERO grounding coverage (cold rows) -- exercise the cold-fallback path
    cold_ids = [n - 1, n - 2, n - 3]
    for c in cold_ids:
        ground[c] = 0.0
    nrm = np.linalg.norm(ground, axis=1, keepdims=True)
    ground = np.where(nrm > 1e-8, ground / (nrm + 1e-8), ground)
    # i%4<2 (not i%2) so BOTH lexnames appear within the even-indexed (held) subset AND the
    # odd-indexed (train_eval) subset -- an i%2-correlated split would make every held query's
    # "same lexname" set degenerate (all-same-class), which _eval_semantic_set correctly rejects
    # (pos.sum()==pos.shape[0]) and would return zero usable queries.
    lexnames = [("lexA" if (i % 4) < 2 else "lexB") for i in range(n)]
    counts = rng.integers(1, 20, size=n).astype(np.int64)
    # synthetic adjacency: ring graph + a few chords so degree-matched negatives are constructible
    adj = [set() for _ in range(n)]
    for i in range(n):
        adj[i].add((i + 1) % n)
        adj[(i + 1) % n].add(i)
    for i in range(0, n, 3):
        j = (i + 5) % n
        adj[i].add(j)
        adj[j].add(i)
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    held = np.array(sorted(range(0, n, 2)), dtype=np.int64)           # >=10 held concepts required
    is_held = np.zeros(n, dtype=bool)
    is_held[held] = True
    train_eval = np.array(sorted(i for i in range(n) if i not in set(held.tolist())), dtype=np.int64)
    universe = dict(lexnames=lexnames, K=n, ids=list(range(n)), surfaces=[str(i) for i in range(n)])
    split = dict(held_idx=held, train_eval_idx=train_eval, is_held=is_held,
                split_meta=dict(synthetic=True))
    return dict(ground=ground, text_reps=text, text_rand=text_rand, counts=counts, deg=deg, adj=adj,
               n_shards=1, universe=universe, split=split, w_star=0.5, selected_arm=_r.FUSE_WTUNED_ARM)


def _selftest():
    print("[selftest] gated_fusion_text_grounding_encoder_core", flush=True)
    b = _make_synthetic_bundle(n=40, seed=0)
    seed = 7

    # 1) baseline reuse (unmodified _r functions) must run clean at tiny N
    sem_baseline = _r.semantic_eval(b["ground"], b["text_reps"], b["text_rand"], b["counts"],
                                    b["universe"], b["split"], seed, b["w_star"], b["selected_arm"])
    assert sem_baseline is not None, "semantic_eval returned None at N=24 (regime too small)"
    rel_baseline = _r.relational_eval(b["ground"], b["text_reps"], b["counts"], b["universe"],
                                      b["split"], b["adj"], b["deg"], b["n_shards"], seed, b["w_star"])
    assert rel_baseline["_n_query"] >= 1, "relational_eval produced zero queries at N=24"
    print("[selftest]  baseline reuse OK (sem_n_query=%d rel_n_query=%d)"
         % (sem_baseline["_n_query"], rel_baseline["_n_query"]), flush=True)

    # 2) gate fit + apply, both axes, real gated_table/learn_lambda calls
    lam_sem, vs_sem, curve_sem, used_fb_sem, n_val_sem = fit_lambda_semantic(
        b["ground"], b["text_reps"], b["counts"], b["universe"], b["split"], seed)
    assert 0.0 <= lam_sem <= 1.0, "lambda_semantic out of [0,1]: %s" % lam_sem
    sem_auc, n_sem_q, n_sem_cold, sem_Xp = apply_gate_semantic(
        b["ground"], b["text_reps"], b["universe"], b["split"], lam_sem)
    assert sem_auc is not None

    lam_rel, vs_rel, curve_rel, used_fb_rel, n_val_rel = fit_lambda_relational(
        b["ground"], b["text_reps"], b["universe"], b["split"], b["adj"], b["deg"], seed)
    assert 0.0 <= lam_rel <= 1.0, "lambda_relational out of [0,1]: %s" % lam_rel
    rel_auc, n_rel_q, n_rel_cold = apply_gate_relational(
        b["ground"], b["text_reps"], b["universe"], b["split"], b["adj"], b["deg"], seed, lam_rel)
    print("[selftest]  lambda_sem=%.2f (n_val=%d) lambda_rel=%.2f (n_val=%d) sem_auc=%s rel_auc=%s"
         % (lam_sem, n_val_sem, lam_rel, n_val_rel, sem_auc, rel_auc), flush=True)

    # 3) lambda=0.5 MUST reduce to ZAVG (the correctness cross-check, exercised here too)
    sem_half, _, _, _ = apply_gate_semantic(b["ground"], b["text_reps"], b["universe"], b["split"], 0.5)
    rel_half, _, _ = apply_gate_relational(
        b["ground"], b["text_reps"], b["universe"], b["split"], b["adj"], b["deg"], seed, 0.5)
    sem_delta = abs(sem_half - sem_baseline[_r.FUSE_ZAVG_ARM])
    rel_delta = abs(rel_half - rel_baseline[_r.FUSE_ZAVG_ARM])
    assert sem_delta < ZAVG_XCHECK_TOL, "XCHECK semantic FAIL at selftest scale: delta=%s" % sem_delta
    assert rel_delta < ZAVG_XCHECK_TOL, "XCHECK relational FAIL at selftest scale: delta=%s" % rel_delta
    print("[selftest]  XCHECK PASS (sem_delta=%.6f rel_delta=%.6f)" % (sem_delta, rel_delta), flush=True)

    # 4) cold-row fallback: cold concepts (zero grounding norm) must be forced to PURE TEXT
    #    regardless of lambda -- verify at lambda=0.0 (pure grounding endpoint) the cold rows'
    #    fused score STILL equals their pure-text z-score row (not a zeroed/corrupted mix).
    held = b["split"]["held_idx"]
    cold_in_held = [i for i in held.tolist() if np.linalg.norm(b["ground"][i]) <= 1e-8]
    if cold_in_held:
        idx, cg_z, ct_z = _semantic_score_mats(b["ground"], b["text_reps"], held.tolist())
        pos = {int(v): k for k, v in enumerate(idx)}
        support = (~_cold_mask(b["ground"], idx)).astype(np.int64)
        Xg = torch.from_numpy(cg_z.astype(np.float32))
        Xt = torch.from_numpy(ct_z.astype(np.float32))
        Xp0 = gated_table(torch.zeros_like(Xt), Xg, Xt, list(range(idx.shape[0])),
                          {i: int(support[i]) for i in range(idx.shape[0])}, 0.0)
        for c in cold_in_held:
            r = pos[c]
            assert np.allclose(Xp0[r].numpy(), ct_z[r], atol=1e-6), (
                "cold-row fallback FAILED: concept %d (zero grounding norm) not forced to pure TEXT "
                "at lambda=0.0" % c)
        print("[selftest]  cold-row fallback OK (%d cold concepts forced to pure TEXT)"
             % len(cold_in_held), flush=True)
    else:
        print("[selftest]  (no cold concepts landed in this synthetic held sample; "
             "cold-path exercised indirectly via support_deg=0 branch in gated_table's own self-test)",
             flush=True)

    # 5) LEAK ASSERT positive control: deliberately construct an overlapping val_ids set and
    #    confirm the guard actually RAISES (not just present-but-dead code).
    try:
        _assert_val_test_disjoint([int(held[0])], held, "selftest_positive_control")
        raise AssertionError("LEAK ASSERT positive control FAILED TO RAISE on a deliberately "
                             "overlapping id set")
    except RuntimeError as e:
        assert "LEAK_ASSERT_VAL_TEST_DISJOINT" in str(e)
        print("[selftest]  LEAK ASSERT positive control OK (raises on deliberate overlap)", flush=True)

    print("[selftest] ALL CHECKS PASS", flush=True)


# ---------------------------------------------------------------------------
# Entry point (called by the per-seed wrapper files)
# ---------------------------------------------------------------------------
def main(seed, anchor_name):
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args, _unknown = parser.parse_known_args()

    output_dir = get_output_dir(anchor_name)   # Path
    output_dir_s = str(output_dir)
    run_mode = "self_test" if args.self_test else "full"
    _write_start_marker(output_dir_s, anchor_name, run_mode, expected_n_units=1)
    try:
        if args.self_test:
            _selftest()
            write_metrics(
                output_dir,
                dict(verdict="HARD_PASS", verdict_msg="SELFTEST_PASS (real code path @ N=24 synthetic)",
                    elapsed_s=0.0, run_mode="self_test"))
            return
        npz_path = os.path.join(NPZ_DIR, "evalreps_seed_%d.npz" % seed)
        per_seed = run_one_seed(seed, anchor_name, npz_path, output_dir_s, run_mode="full")
        sv = _fmt_seed_verdict(per_seed)
        all_gates_pass = all(g["gate_verdict"] for g in sv["gates"])
        verdict = ("SINGLE_SEED_MEASURED_GATES_PASS" if all_gates_pass
                  else "SINGLE_SEED_MEASURED_GATES_PARTIAL")
        verdict_msg = (
            "seed=%d single-seed measurement (NOT a final verdict -- combine with the sibling "
            "seed per pre-reg BOTH-seeds bands). sem_gate_auc=%.4f (zavg=%.4f, margin=%+.4f) "
            "rel_gate_auc=%.4f (zavg=%.4f, margin=%+.4f, dist_to_text=%+.4f)"
            % (seed, per_seed["gate_semantic"]["test_auc"], per_seed["baseline"]["semantic"]["ZAVG"],
               sv["sem_margin_vs_zavg"], per_seed["gate_relational"]["test_auc"],
               per_seed["baseline"]["relational"]["ZAVG"], sv["rel_margin_vs_zavg"],
               sv["rel_dist_to_text"]))
        _log(anchor_name, verdict_msg)
        metrics = dict(
            verdict=verdict, verdict_msg=verdict_msg, elapsed_s=per_seed["elapsed_s"],
            summary=verdict_msg, run_mode="full", anchor_name=anchor_name,
            seed=seed, per_seed=per_seed, seed_verdict=sv,
            structured_gate_claims=sv["gates"],
            ts_iso=datetime.now(timezone.utc).isoformat(),
        )
        write_metrics(output_dir, metrics)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir_s, anchor_name, e)
        raise
