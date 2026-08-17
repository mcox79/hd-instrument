"""exp_cue_compression_property_diagnosis_v1 -- WHAT PROPERTY of the raw count cue does the 256-dim
random projection destroy?

THE CONTRADICTION THIS CELL EXISTS TO RESOLVE (both numbers verified off disk before this cell was
written -- see the module docstring's REPRODUCTION NOTE below for the exact recompute).
  - data/exp_cue_information_audit_v1/metrics.json: dropping the 256-dim projection ENTIRELY and
    scoring raw sparse count vectors directly raises partial-cue addressing accuracy from
    C0_PROJECTED_256=0.0711 to U0_UNCOMPRESSED=0.0849, margin +0.0138 CI [+0.0083,+0.0195],
    half-width 0.0056, CI-separated ABOVE.
  - data/exp_sparse_address_dense_value_v1/metrics.json: raising the SAME projection from d=256 to
    d=8192 (32x the memory, same dense a_write=1.0/a_read=sym regime) moves addressing accuracy
    0.0711 -> 0.0709 (d=2048 in between reads 0.0711/0.0714 across draws) -- a gap roughly one
    fifteenth of the arm's own CI half-width (0.0078). MORE DIMENSIONS DO NOT RECOVER THE LOSS.
Both cannot be explained by "the projection is too small". This cell separates WHICH PROPERTY of
the raw representation the projection destroys, holding the encoder's inputs (the SAME masked
content-word counts, the SAME store, the SAME 3994-item / 5491-anchor pool) fixed and varying only
the map from those counts to a fixed-width code.

REPRODUCTION NOTE (this cell's own REGRESSION GATE, computed fresh below, not imported): C0 and U0
are recomputed here from the SAME cache/checkpoint the audit cell built, using the SAME formulas
(cos(mat[a], Q_part[i]) for C0; cos(P_a, q_i) over raw sparse counts for U0), and must reproduce
0.0711 / 0.0849 within tol=5e-4 or the cell raises SystemExit before any property arm is scored.

FOUR CANDIDATE PROPERTIES, isolated ONE VARIABLE AT A TIME against the identical raw counts P_a
(store) / q_i (cue), all scored on the identical population as C0/U0 above:
  S1_SPARSE_HASH_PROJ  sparsity-structure / exact-zero preservation. Feature hashing: each distinct
                       word maps to EXACTLY ONE of 256 output dims with a random sign (the standard
                       hashing trick). Unlike the incumbent dense projection (every word's symbol
                       vector touches all 256 dims), two contexts sharing NO words touch NO shared
                       output dim except by hash collision. Output is still 256-dim and still
                       signed -- this isolates sparsity-of-the-map, nothing else.
  N1_NONNEG_PROJ       non-negativity. A DENSE 256-dim projection (every word touches every output
                       dim, same as the incumbent) but built from a {0,1} Bernoulli matrix instead
                       of {-1,+1} -- so no two words' contributions can CANCEL. Isolates
                       non-negativity, holding denseness fixed at the incumbent's own value.
  B1_BINARIZED_RAW     magnitude/frequency. The SAME uncompressed (no projection at all) sparse
                       count representation as U0, with every nonzero count set to 1 -- frequency
                       information deliberately removed, dimensionality and sparsity structure of
                       U0 preserved exactly. If this still beats C0 by close to the full margin,
                       frequency is not the carrier.
  INTERFERENCE          not a fourth arm -- measured directly as a per-item COLLISION statistic
                       (mean |cos| between the incumbent encoder's own symbol vectors for each pair
                       of distinct words in an item's cue) and correlated with the per-item
                       lost-by-projection flag below, not built into an alternative encoder.

VALIDITY ARMS on EVERY encoding space (S1, N1, B1, plus C0/U0 for reference): K1_EXACT_KEY (query =
the anchor's own representation in that space; must sit at/near ceiling or NO quality number is
published for that arm) and N1_RANDOM_KEY (the real cue reassigned to a different item, same
permutation across every space for comparability; must sit at ~chance).

ITEM-LEVEL DECOMPOSITION (the strongest evidence this cell can produce). For every item, define
LOST_BY_PROJECTION = U0 addresses it correctly AND C0 does not. Report: how many items (a
concentrated small subset, or roughly proportional to chance across the whole 3994-item pool), and
whether LOST_BY_PROJECTION items differ, CI-separated, from the rest on: (a) number of distinct
content words in the cue, (b) the incumbent encoder's own pairwise collision statistic among those
words, (c) how many distinct words the target anchor's own store profile contains. A diffuse loss
(no feature separates) and a concentrated loss (one feature CI-separates) imply different fixes and
are reported as different outcomes, not forced into one.

BETWEEN_PROJECTION_DRAW_SD: S1 and N1_NONNEG_PROJ are each built from 3 independent random-matrix
draws (same seeds pattern as exp_sparse_address_dense_value_v1). Reported beside every S1/N1 margin
-- this cell is ABOUT a random projection, so projection-draw noise is load-bearing, not boilerplate.

BRAIN STRUCTURE: none is claimed. This is an information/format audit of our own encoder, exactly
like the sibling exp_cue_information_audit_v1 it extends -- inventing an anatomy here would be
exactly the laundering the project's brain-fidelity gate exists to ban.

STOP-IF (pre-registered here, before any number is read):
  (i)   the C0/U0 REGRESSION GATE fails to reproduce 0.0711/0.0849 within tol -> STOP, report the
        failed reproduction, do not proceed to any property arm. A failed reproduction of a
        load-bearing number outranks everything else in this cell.
  (ii)  exactly one property arm (S1, N1, or B1) is CI-separated ABOVE C0 by a margin that accounts
        for most of the U0-C0 gap -> that property is the encoder design constraint. Stated as a
        constraint on what to build next, NOT as a capability win.
  (iii) no property arm separates from C0 CI-separated, or the per-item decomposition finds no
        feature that CI-separates LOST_BY_PROJECTION from the rest -> the honest null. The
        constraint becomes "do not compress this representation" rather than "compress it
        differently", and that is reported as a real, useful answer.
  (iv)  more than one property arm separates -> report all of them with their individual and (where
        computable) combined contribution; do not force a single winner.

RUNNER: cpu_runner_local. Reuses the ALREADY-BUILT store counts (P_a) and cue counts (q_i) from
data/exp_cue_information_audit_v1's checkpoint (units.jsonl) READ-ONLY -- load_units() only, never
record_unit() into that directory. Any unit missing from that checkpoint (should not happen for
--grid full; expected for --grid reduced's smaller item/anchor subset) is computed fresh and
checkpointed into THIS cell's OWN out_dir instead. No write ever targets another cell's data
directory.

PROGRESS LOGGING: every phase prints a flushed line. Expected wall time for --grid full is a few
minutes (reusing the checkpoint avoids the ~150s raw-count rebuild the audit cell paid), well under
1800s, but progress logging is included regardless per project convention for any multi-phase cell.

ASCII-only. No LLM anywhere in this path. Writes only under
data/exp_cue_compression_property_diagnosis_v1[_smoke]/. Does not write to
data/exp_cue_information_audit_v1/, data/foundation/, hdlab/, tools/floor_battery.py or
tools/exp_checkpoint.py.
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
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.floor_battery import l2n, paired_bootstrap_ci, margin           # noqa: E402
from tools.exp_checkpoint import load_units, record_unit, unit_key         # noqa: E402

import experiments.exp_task_degeneracy_v1 as DEG                            # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3              # noqa: E402
import experiments.exp_cue_information_audit_v1 as AUD                      # noqa: E402
from hdlab.reading_grounding_loop import symbol_vector                      # noqa: E402

ANCHOR_NAME = "exp_cue_compression_property_diagnosis_v1"
AUD_FULL_OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_cue_information_audit_v1")

MASTER_SEED = 20260817200
N_BOOT = 10000
KA_CEILING_MIN = 0.98
D_PROJ = 256
N_PROJ_DRAWS = 3
N_SMOKE_ITEMS = 150
ANCHOR_POOL_SMOKE = 250

# PROVENANCE: data/exp_cue_information_audit_v1/metrics.json, commit eec21487d, verified off disk
# before this cell was authored (Read the file directly; both numbers below match what is on disk).
REGRESSION_C0 = 0.0711
REGRESSION_U0 = 0.0849
REGRESSION_TOL = 5e-4


def _out_dir(grid: str) -> str:
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + ("_smoke" if grid == "reduced" else ""))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# read-only reuse of the audit cell's checkpointed raw counts; fall back to local (own-dir) build
# =================================================================================================
def load_or_build_counts(keys: Sequence[str], prefix: str, buckets: Dict[str, List[int]],
                         sents: List[str], target_of_key,
                         my_out_dir: str, reuse_dir: Optional[str]) -> Tuple[Dict[str, Counter], Dict]:
    """`target_of_key(key)` returns the lemma whose raw-count window is being built (the anchor
    itself for store counts; the item's target lemma for cue counts, with the sentence looked up by
    the caller via `raw_counts_for_window`). Reused strictly READ-ONLY from `reuse_dir`; any miss is
    computed here and recorded into `my_out_dir`, never into `reuse_dir`."""
    reuse_path = os.path.join(reuse_dir, "units.jsonl") if reuse_dir else None
    reuse_units = load_units(reuse_dir) if reuse_path and os.path.exists(reuse_path) else {}
    mine_done = load_units(my_out_dir)
    out: Dict[str, Counter] = {}
    n_reused_external = n_reused_local = n_built = 0
    t0 = time.time()
    for k, key_id in enumerate(keys):
        ck = unit_key(prefix, key_id)
        if ck in mine_done:
            out[key_id] = Counter(mine_done[ck]["counts"])
            n_reused_local += 1
        elif ck in reuse_units:
            out[key_id] = Counter(reuse_units[ck]["counts"])
            n_reused_external += 1
        else:
            out[key_id] = target_of_key(key_id)
            record_unit(my_out_dir, ck, {"counts": dict(out[key_id])})
            n_built += 1
        if (k + 1) % 1000 == 0 or k == len(keys) - 1:
            print("[%s] %d/%d built=%d reused_local=%d reused_external=%d elapsed=%.0fs" % (
                prefix, k + 1, len(keys), n_built, n_reused_local, n_reused_external,
                time.time() - t0), flush=True)
    return out, {"n_built": n_built, "n_reused_local": n_reused_local,
                "n_reused_external": n_reused_external, "elapsed_s": round(time.time() - t0, 1)}


# =================================================================================================
# property projections -- all built from the SAME raw sparse count matrices, differing in ONE thing
# =================================================================================================
def build_hash_projection(vocab_size: int, d: int, seed: int) -> sp.csr_matrix:
    """S1_SPARSE_HASH_PROJ: the standard feature-hashing trick. Exactly one nonzero (+-1) per row
    (per vocabulary word) -- two words touch the same output dim only by hash collision. This is
    the SPARSITY / exact-zero-preservation isolate: unlike the incumbent dense projection, an
    output dim carries signal ONLY from words that hash to it."""
    rng = np.random.default_rng(seed)
    cols = rng.integers(0, d, size=vocab_size)
    signs = (rng.integers(0, 2, size=vocab_size).astype(np.float32) * 2.0 - 1.0)
    rows = np.arange(vocab_size)
    return sp.csr_matrix((signs, (rows, cols)), shape=(vocab_size, d), dtype=np.float32)


def build_nonneg_projection(vocab_size: int, d: int, seed: int) -> np.ndarray:
    """N1_NONNEG_PROJ: a DENSE {0,1} random matrix -- every word touches every output dim (same
    denseness as the incumbent) but no entry is ever negative, so no two words' contributions can
    CANCEL in any output coordinate. This is the NON-NEGATIVITY isolate, holding denseness fixed."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=(vocab_size, d)).astype(np.float32)


def binarize_sparse(X: sp.csr_matrix) -> sp.csr_matrix:
    """B1_BINARIZED_RAW: presence/absence in place of counts. Same sparsity pattern as the raw
    count matrix -- ONLY the magnitude information is removed."""
    Xb = X.copy()
    Xb.data = np.ones_like(Xb.data)
    return Xb


def project_dense(counts_sparse: sp.csr_matrix, R: np.ndarray) -> np.ndarray:
    return np.asarray(counts_sparse @ R, dtype=np.float32)


def project_sparse_hash(counts_sparse: sp.csr_matrix, R: sp.csr_matrix) -> np.ndarray:
    return np.asarray((counts_sparse @ R).todense(), dtype=np.float32)


# =================================================================================================
# scoring -- one space (store_mat, cue_mat, both ALREADY L2-normalised and DENSE) -> hits per arm
# =================================================================================================
def addressing_hits(S: np.ndarray, valid_mask: np.ndarray, target_idx: np.ndarray) -> np.ndarray:
    Sm = np.where(valid_mask[:, None], S, -np.inf)
    amax = np.argmax(Sm, axis=0)
    return (amax == target_idx).astype(np.float64)


def score_space(name: str, store_n: np.ndarray, cue_n: np.ndarray, valid_mask: np.ndarray,
                target: np.ndarray, perm: np.ndarray, chance: float) -> Dict:
    """store_n/cue_n: L2-normalised dense [n_anchors, d] / [n_items, d]. Returns the primary
    accuracy plus its K1/N1 validity arms, all against the SAME permutation for comparability
    across encoding spaces."""
    S = store_n @ cue_n.T
    S_K1 = store_n @ store_n[target].T
    S_N1 = S[:, perm]
    hits = {"MAIN": addressing_hits(S, valid_mask, target),
           "K1_EXACT_KEY": addressing_hits(S_K1, valid_mask, target),
           "N1_RANDOM_KEY": addressing_hits(S_N1, valid_mask, target)}
    n = hits["MAIN"].shape[0]
    mask = np.ones(n, dtype=bool)
    boot = paired_bootstrap_ci(hits, mask, N_BOOT, MASTER_SEED + 707)
    acc = {k: round(v, 4) for k, v in boot["acc"].items()}
    out = {"n_items": int(n), "chance": round(chance, 6), "accuracy": acc,
          "arm_digest_MAIN": _digest(hits["MAIN"]),
          "K1_validity_PASS": bool(acc["K1_EXACT_KEY"] >= KA_CEILING_MIN),
          "N1_validity_near_chance": bool(abs(acc["N1_RANDOM_KEY"] - chance) < 0.01)}
    print("[space:%s] n=%d chance=%.6f MAIN=%.4f K1=%.4f N1=%.4f" % (
        name, n, chance, acc["MAIN"], acc["K1_EXACT_KEY"], acc["N1_RANDOM_KEY"]), flush=True)
    return out, hits["MAIN"], boot


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {}
    rng = np.random.default_rng(5)

    # T0 -- floor_battery's own self-test, the shared ruler.
    from tools import floor_battery
    res["floor_battery_selftest_keys"] = sorted(floor_battery.self_test().keys())

    # T1 -- build_hash_projection: exactly ONE nonzero per row (per word), value in {-1,+1}, and
    # two words hashed to the SAME dim really do interfere (their contributions land on the same
    # output coordinate) while two words hashed to DIFFERENT dims are exactly orthogonal in the
    # projected space (zero-preservation is exact, not approximate, off the hashed dim).
    R = build_hash_projection(6, 4, seed=1)
    nnz_per_row = np.asarray((R != 0).sum(axis=1)).ravel()
    assert np.all(nnz_per_row == 1), "hash projection rows are not exactly one nonzero: %r" % nnz_per_row
    vals = np.asarray(R[R.nonzero()]).ravel()
    assert set(np.unique(vals).tolist()) <= {-1.0, 1.0}, "hash projection values outside {-1,+1}"
    Rd = np.asarray(R.todense())
    for i in range(6):
        for j in range(i + 1, 6):
            if np.argmax(np.abs(Rd[i])) != np.argmax(np.abs(Rd[j])):
                assert float(Rd[i] @ Rd[j]) == 0.0, "distinct-dim word pair is not exactly orthogonal"
    res["T1_hash_projection_one_nonzero_and_zero_preserving"] = True

    # T2 -- build_nonneg_projection: every entry in {0,1}, genuinely dense (not all-zero, not
    # constant), and two different random seeds give different matrices (draws actually vary).
    R2a = build_nonneg_projection(50, 32, seed=11)
    R2b = build_nonneg_projection(50, 32, seed=12)
    assert set(np.unique(R2a).tolist()) <= {0.0, 1.0}, "nonneg projection has values outside {0,1}"
    assert 0.3 < R2a.mean() < 0.7, "nonneg projection is not ~50% dense: mean=%.3f" % R2a.mean()
    assert not np.array_equal(R2a, R2b), "two different seeds produced the identical matrix"
    res["T2_nonneg_projection_zero_one_dense_seeded"] = True

    # T3 -- binarize_sparse: same sparsity PATTERN (same nonzero positions), every nonzero -> 1.0,
    # a count of 7 and a count of 1 become indistinguishable after binarization (that IS the point).
    X = sp.csr_matrix(np.array([[3.0, 0.0, 7.0], [0.0, 1.0, 0.0]], dtype=np.float32))
    Xb = binarize_sparse(X)
    assert (Xb.toarray() == (X.toarray() > 0).astype(np.float32)).all(), "binarize changed the pattern"
    res["T3_binarize_preserves_pattern_removes_magnitude"] = True

    # T4 -- score_space end-to-end: a planted MAIN arm reaches ceiling-ish, K1 (query=own store row)
    # is 1.0, N1 (permuted cue) falls to chance, matching the audit cell's own T5/T6 pattern.
    n_a, d = 40, 16
    M = l2n(rng.standard_normal((n_a, d)).astype(np.float32))
    valid = np.ones(n_a, dtype=bool)
    target = np.arange(n_a)
    perm = rng.permutation(n_a)
    while np.any(perm == np.arange(n_a)):
        perm = rng.permutation(n_a)
    out4, hits4, _ = score_space("T4", M, M, valid, target, perm, 1.0 / n_a)
    assert out4["accuracy"]["MAIN"] == 1.0, "self-cue MAIN accuracy is not 1.0"
    assert out4["accuracy"]["K1_EXACT_KEY"] == 1.0, "K1 did not reach ceiling"
    assert out4["accuracy"]["N1_RANDOM_KEY"] < 0.15, "N1 did not fall near chance"
    res["T4_score_space_end_to_end"] = out4["accuracy"]

    # T5 -- collision statistic: two ORTHOGONAL vectors have |cos|=0; the SAME vector against
    # itself has |cos|=1; a random pair of encoder symbol vectors at d=256 has a small but nonzero
    # expected |cos| (the theoretical noise floor ~1/sqrt(d) approx 0.0625), not exactly 0.
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    assert abs(_abs_cos(v1, v2)) < 1e-9, "orthogonal vectors did not read collision 0"
    assert abs(_abs_cos(v1, v1) - 1.0) < 1e-9, "self collision did not read 1"
    samp = [_abs_cos(symbol_vector("word_%d" % i, 256), symbol_vector("word_%d" % (i + 1), 256))
           for i in range(200)]
    mean_samp = float(np.mean(samp))
    assert 0.0 < mean_samp < 0.25, "encoder collision floor outside a plausible range: %.4f" % mean_samp
    res["T5_collision_statistic"] = {"mean_sampled_abs_cos_d256": round(mean_samp, 4)}

    # T6 -- item-level bucket reconciliation: n_lost - n_gained must equal round((acc_a - acc_b) *
    # n_items) up to rounding, on a small synthetic pair of hit vectors -- the algebraic identity
    # this cell's headline "diffuse vs concentrated" reasoning depends on.
    ha = np.array([1, 1, 0, 0, 1, 0, 1, 0], dtype=np.float64)
    hb = np.array([1, 0, 0, 1, 1, 0, 0, 0], dtype=np.float64)
    n_lost = int(((ha == 1) & (hb == 0)).sum())
    n_gained = int(((ha == 0) & (hb == 1)).sum())
    assert (n_lost - n_gained) == round((ha.mean() - hb.mean()) * len(ha))
    res["T6_bucket_reconciliation"] = True

    # T7 -- the ruler-mode gate is called and this cell never sets --smoke in argv.
    g7 = DEG.ruler_mode_gate()
    assert g7.get("PASS") is True, g7
    assert "--smoke" not in sys.argv, sys.argv
    res["T7_ruler_mode_gate"] = g7

    print("[selftest] PASS " + json.dumps(res, default=str)[:1800], flush=True)
    return res


def _abs_cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return abs(float(a @ b) / (na * nb))


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir = _out_dir(grid)
    os.makedirs(out_dir, exist_ok=True)
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "out_dir": out_dir,
                "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                "RULER_MODE_GATE": DEG.ruler_mode_gate(), "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "progress_logging": True}

    # ---- harness cache (UNMODIFIED, shared with the sibling cells) ---------------------------
    cache_prov = DEG.build_cache_if_missing()
    C = DEG.load_cache()
    rep["cache_provenance"] = cache_prov
    anchors, mat, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    print("[load] n_anchors=%d n_items=%d %.0fs" % (n_anchors, n_items_all, time.time() - t0),
         flush=True)

    # ---- gold + eligibility (byte-identical construction to exp_task_degeneracy_v1 and the audit
    # cell -- copied here rather than imported so this cell's working population is provably the
    # SAME 3994-item pool without depending on either sibling's internal state) -----------------
    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not C["keep"][i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = C["keep"] & GOLD_ALL.any(axis=0)

    # ---- items (target lemma per item, item_id for checkpoint reuse) -- corpus/buckets are the
    # SAME cached artifact the audit cell built (scratch/cue_information_audit_v1/buckets_full.npz)
    sents, buckets, counts, corpus_prov = AUD.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    shim = AUD._ShimSpace(anchors, C["pos"], mat)
    items, item_diag = C3.build_items(shim, buckets, counts, C3.MAX_ITEMS)
    recov = AUD.verify_recoverability(items, C, sents)
    rep["RECOVERABILITY_GATE"] = recov
    print("[recoverability] checked=%d ALL_EXACT=%s %.0fs" % (
        recov["n_checked_full_pop"], recov["ALL_EXACT"], time.time() - t0), flush=True)
    if not recov["ALL_EXACT"]:
        rep["STOP_IF_FIRED"] = ("RECOVERABILITY_DID_NOT_REPRODUCE -- see AUD.verify_recoverability "
                                "output above. No property arm can be built without exact "
                                "reconstruction of the raw cue. Reduced design: report this and stop.")
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        return rep

    L_of = {it["item_id"]: it["L"] for it in items}
    sentidx_of = {it["item_id"]: it["sent_idx"] for it in items}
    item_id_of_idx = [it["item_id"] for it in items]

    # ---- choose the working item/anchor pools per grid -----------------------------------------
    eligible_item_idx = np.flatnonzero(keep_ALL)
    if grid == "full":
        item_idx = eligible_item_idx
        anchor_ids = list(anchors)
        reuse_dir = AUD_FULL_OUT_DIR
    else:
        item_idx = eligible_item_idx[:N_SMOKE_ITEMS]
        own = sorted({L_of[item_id_of_idx[i]] for i in item_idx})
        rngp = np.random.default_rng(MASTER_SEED + 1)
        pad_pool = [a for a in anchors if a not in set(own)]
        pad = rngp.choice(pad_pool, size=max(0, ANCHOR_POOL_SMOKE - len(own)), replace=False).tolist()
        anchor_ids = sorted(set(own) | set(pad))
        reuse_dir = None       # smoke pool differs from the audit cell's own smoke pool; build local
    n_items_w = int(item_idx.size)
    n_anchors_w = len(anchor_ids)
    rep["POOL"] = {"grid": grid, "n_items_working": n_items_w, "n_anchors_working": n_anchors_w,
                   "n_items_eligible_full_pop": int(eligible_item_idx.size), "n_anchors_full_pop": n_anchors,
                   "reuse_dir": reuse_dir}
    print("[pool] grid=%s n_items=%d n_anchors=%d reuse_dir=%s" % (
        grid, n_items_w, n_anchors_w, reuse_dir), flush=True)

    anchor_pos_global = C["pos"]
    anchor_global_idx = np.array([anchor_pos_global[a] for a in anchor_ids], dtype=np.int64)
    mat_w = mat[anchor_global_idx]
    mat_ok_w = mat_ok[anchor_global_idx]
    local_pos = {a: i for i, a in enumerate(anchor_ids)}
    item_ids_w = [item_id_of_idx[i] for i in item_idx]
    L_w = [L_of[iid] for iid in item_ids_w]
    qidx_w = np.array([local_pos[L] for L in L_w], dtype=np.int64)
    Qpart_w = C["Q_part"][item_idx]

    # ---- P (store raw counts) and Qctx (cue raw counts) -- READ-ONLY reuse of the audit cell's
    # checkpoint where available, computed fresh into THIS cell's own out_dir otherwise ----------
    P, p_diag = load_or_build_counts(
        anchor_ids, "Pstore", buckets, sents,
        lambda a: sum((AUD.raw_counts_for_window(sents[i], a)
                      for i in buckets.get(a, [])[:C3._n_profile(len(buckets.get(a, [])))]), Counter()),
        out_dir, reuse_dir)
    rep["STORE_COUNTS_SOURCE"] = p_diag
    Qctx, q_diag = load_or_build_counts(
        item_ids_w, "Qcue_context", buckets, sents,
        lambda iid: AUD.raw_counts_for_window(sents[sentidx_of[iid]], L_of[iid]),
        out_dir, reuse_dir)
    rep["CONTEXT_CUE_SOURCE"] = q_diag

    # ---- shared vocabulary + raw (un-normalised) sparse count matrices -------------------------
    vocab = AUD.build_vocab([P, Qctx])
    rep["VOCAB"] = {"n_distinct_content_words": len(vocab)}
    P_raw = AUD.to_sparse(P, anchor_ids, vocab)
    Q_raw = AUD.to_sparse(Qctx, item_ids_w, vocab)

    target = qidx_w
    perm = np.random.default_rng(MASTER_SEED + 501).permutation(n_items_w)
    tries = 0
    while np.any(perm == np.arange(n_items_w)) and tries < 50:
        perm = np.random.default_rng(MASTER_SEED + 502 + tries).permutation(n_items_w)
        tries += 1
    chance_addr = 1.0 / max(int(mat_ok_w.sum()), 1)

    spaces: Dict[str, Dict] = {}
    hit_vectors: Dict[str, np.ndarray] = {}

    # ---- C0_PROJECTED_256 (reference reproduction) ----------------------------------------------
    out_c0, hits_c0, _ = score_space("C0_PROJECTED_256", l2n(mat_w), l2n(Qpart_w), mat_ok_w, target,
                                     perm, chance_addr)
    spaces["C0_PROJECTED_256"] = out_c0
    hit_vectors["C0_PROJECTED_256"] = hits_c0

    # ---- U0_UNCOMPRESSED (reference reproduction) -------------------------------------------------
    Pm = AUD.l2n_sparse(P_raw)
    Qm = AUD.l2n_sparse(Q_raw)
    U0_store_n = np.asarray(Pm.todense(), dtype=np.float32)
    U0_cue_n = np.asarray(Qm.todense(), dtype=np.float32)
    out_u0, hits_u0, _ = score_space("U0_UNCOMPRESSED", U0_store_n, U0_cue_n, mat_ok_w, target,
                                     perm, chance_addr)
    spaces["U0_UNCOMPRESSED"] = out_u0
    hit_vectors["U0_UNCOMPRESSED"] = hits_u0

    rep["REGRESSION_GATE"] = {
        "what": "C0_PROJECTED_256 / U0_UNCOMPRESSED addressing accuracy, recomputed fresh here, "
                "must reproduce the landed exp_cue_information_audit_v1 numbers. ONLY MEANINGFUL "
                "at --grid full: the landed figures were measured on the full 3994-item/5491-anchor "
                "pool, and a --grid reduced (smoke) population is a different, much smaller pool by "
                "construction, so it is NOT expected to reproduce them and the gate is advisory only "
                "at reduced scale (checked, never enforced, at reduced scale).",
        "grid": grid, "enforced": grid == "full",
        "C0_measured": out_c0["accuracy"]["MAIN"], "C0_expected": REGRESSION_C0,
        "U0_measured": out_u0["accuracy"]["MAIN"], "U0_expected": REGRESSION_U0,
        "tol": REGRESSION_TOL,
        "C0_PASS": bool(abs(out_c0["accuracy"]["MAIN"] - REGRESSION_C0) <= REGRESSION_TOL),
        "U0_PASS": bool(abs(out_u0["accuracy"]["MAIN"] - REGRESSION_U0) <= REGRESSION_TOL)}
    if grid == "full" and not (rep["REGRESSION_GATE"]["C0_PASS"] and rep["REGRESSION_GATE"]["U0_PASS"]):
        rep["STOP_IF_FIRED"] = ("i_REGRESSION_FAILED_TO_REPRODUCE -- %r. STOPPING before any "
                                "property arm; a failed reproduction of a load-bearing number "
                                "outranks the rest of this cell." % rep["REGRESSION_GATE"])
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        print("STOP: " + rep["STOP_IF_FIRED"], flush=True)
        return rep
    print("[regression] grid=%s enforced=%s C0=%.4f (expect %.4f) U0=%.4f (expect %.4f) PASS=%s/%s" % (
        grid, grid == "full", out_c0["accuracy"]["MAIN"], REGRESSION_C0, out_u0["accuracy"]["MAIN"],
        REGRESSION_U0, rep["REGRESSION_GATE"]["C0_PASS"], rep["REGRESSION_GATE"]["U0_PASS"]), flush=True)

    # ---- B1_BINARIZED_RAW (magnitude/frequency isolate; no projection, no draws) -----------------
    Pb = AUD.l2n_sparse(binarize_sparse(P_raw))
    Qb = AUD.l2n_sparse(binarize_sparse(Q_raw))
    out_b1, hits_b1, _ = score_space("B1_BINARIZED_RAW", np.asarray(Pb.todense(), dtype=np.float32),
                                     np.asarray(Qb.todense(), dtype=np.float32), mat_ok_w, target,
                                     perm, chance_addr)
    spaces["B1_BINARIZED_RAW"] = out_b1
    hit_vectors["B1_BINARIZED_RAW"] = hits_b1

    # ---- S1_SPARSE_HASH_PROJ (sparsity/exact-zero isolate; 3 projection draws) -------------------
    s1_draws = []
    for d in range(N_PROJ_DRAWS):
        Rh = build_hash_projection(len(vocab), D_PROJ, seed=MASTER_SEED + 3000 + d)
        Ps1 = l2n(project_sparse_hash(P_raw, Rh))
        Qs1 = l2n(project_sparse_hash(Q_raw, Rh))
        out_d, hits_d, _ = score_space("S1_SPARSE_HASH_PROJ_draw%d" % d, Ps1, Qs1, mat_ok_w, target,
                                       perm, chance_addr)
        s1_draws.append(out_d)
        if d == 0:
            hit_vectors["S1_SPARSE_HASH_PROJ"] = hits_d
    s1_main_vals = [x["accuracy"]["MAIN"] for x in s1_draws]
    rep["S1_SPARSE_HASH_PROJ"] = {"draws": s1_draws,
                                  "BETWEEN_PROJECTION_DRAW_SD": {
                                      "n_draws": N_PROJ_DRAWS, "mean": round(float(np.mean(s1_main_vals)), 4),
                                      "sd": round(float(np.std(s1_main_vals)), 4), "values": s1_main_vals}}
    spaces["S1_SPARSE_HASH_PROJ"] = s1_draws[0]

    # ---- N1_NONNEG_PROJ (non-negativity isolate; 3 projection draws) ------------------------------
    n1_draws = []
    for d in range(N_PROJ_DRAWS):
        Rn = build_nonneg_projection(len(vocab), D_PROJ, seed=MASTER_SEED + 4000 + d)
        Pn1 = l2n(project_dense(P_raw, Rn))
        Qn1 = l2n(project_dense(Q_raw, Rn))
        out_d, hits_d, _ = score_space("N1_NONNEG_PROJ_draw%d" % d, Pn1, Qn1, mat_ok_w, target,
                                       perm, chance_addr)
        n1_draws.append(out_d)
        if d == 0:
            hit_vectors["N1_NONNEG_PROJ"] = hits_d
    n1_main_vals = [x["accuracy"]["MAIN"] for x in n1_draws]
    rep["N1_NONNEG_PROJ"] = {"draws": n1_draws,
                             "BETWEEN_PROJECTION_DRAW_SD": {
                                 "n_draws": N_PROJ_DRAWS, "mean": round(float(np.mean(n1_main_vals)), 4),
                                 "sd": round(float(np.std(n1_main_vals)), 4), "values": n1_main_vals}}
    spaces["N1_NONNEG_PROJ"] = n1_draws[0]

    # ---- ARMS_MUST_DIFFER (schema-vet requirement) -------------------------------------------------
    digests = {k: _digest(v) for k, v in hit_vectors.items()}
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests
    assert len(set(digests.values())) > 1, "all MAIN hit vectors are IDENTICAL -- a construction bug"

    # ---- decisive margins vs C0 and vs U0, ALL arms, paired bootstrap on the SAME item set --------
    hits_boot = {k: v for k, v in hit_vectors.items()}
    mask = np.ones(n_items_w, dtype=bool)
    boot_all = paired_bootstrap_ci(hits_boot, mask, N_BOOT, MASTER_SEED + 909)
    margins = {}
    for arm in ("S1_SPARSE_HASH_PROJ", "N1_NONNEG_PROJ", "B1_BINARIZED_RAW"):
        margins[arm] = {
            "vs_C0_PROJECTED_256": margin(boot_all["boot"], arm, "C0_PROJECTED_256"),
            "vs_U0_UNCOMPRESSED": margin(boot_all["boot"], arm, "U0_UNCOMPRESSED")}
    margins["U0_UNCOMPRESSED"] = {"vs_C0_PROJECTED_256": margin(boot_all["boot"], "U0_UNCOMPRESSED",
                                                               "C0_PROJECTED_256")}
    rep["DECISIVE_MARGINS"] = margins
    gap = out_u0["accuracy"]["MAIN"] - out_c0["accuracy"]["MAIN"]
    for arm, mm in margins.items():
        if arm == "U0_UNCOMPRESSED":
            continue
        pt = mm["vs_C0_PROJECTED_256"]["point"]
        mm["fraction_of_U0_minus_C0_gap_recovered"] = round(pt / gap, 3) if gap != 0 else None
    print("[margins] " + json.dumps(margins, default=str)[:2500], flush=True)

    rep["SPACES"] = spaces

    # ================================ ITEM-LEVEL DECOMPOSITION ====================================
    lost_by_projection = (hit_vectors["U0_UNCOMPRESSED"] == 1.0) & (hit_vectors["C0_PROJECTED_256"] == 0.0)
    gained_by_projection = (hit_vectors["U0_UNCOMPRESSED"] == 0.0) & (hit_vectors["C0_PROJECTED_256"] == 1.0)
    both_hit = (hit_vectors["U0_UNCOMPRESSED"] == 1.0) & (hit_vectors["C0_PROJECTED_256"] == 1.0)
    both_miss = (hit_vectors["U0_UNCOMPRESSED"] == 0.0) & (hit_vectors["C0_PROJECTED_256"] == 0.0)
    n_lost, n_gained = int(lost_by_projection.sum()), int(gained_by_projection.sum())
    rep["BUCKETS"] = {
        "n_items": n_items_w, "n_both_hit": int(both_hit.sum()), "n_both_miss": int(both_miss.sum()),
        "n_lost_by_projection_U0_only": n_lost, "n_gained_by_projection_C0_only": n_gained,
        "net_lost_minus_gained": n_lost - n_gained,
        "net_over_n_items": round((n_lost - n_gained) / n_items_w, 4),
        "reconciles_with_MAIN_margin_point": margins["U0_UNCOMPRESSED"]["vs_C0_PROJECTED_256"]["point"],
        "fraction_of_pool_lost": round(n_lost / n_items_w, 4)}

    # per-item features: cue size, item-own collision statistic, target anchor store breadth
    print("[decomposition] computing per-item features for %d items" % n_items_w, flush=True)
    sym_cache: Dict[str, np.ndarray] = {}

    def sym(w: str) -> np.ndarray:
        v = sym_cache.get(w)
        if v is None:
            v = symbol_vector(w, 256).astype(np.float32)
            v = v / max(float(np.linalg.norm(v)), 1e-12)
            sym_cache[w] = v
        return v

    n_distinct_cue_words = np.zeros(n_items_w, dtype=np.float64)
    cue_collision = np.full(n_items_w, np.nan, dtype=np.float64)
    target_store_breadth = np.zeros(n_items_w, dtype=np.float64)
    for i, iid in enumerate(item_ids_w):
        words = sorted(Qctx.get(iid, {}).keys())
        n_distinct_cue_words[i] = len(words)
        target_store_breadth[i] = len(P.get(L_w[i], {}))
        if len(words) >= 2:
            vecs = np.stack([sym(w) for w in words])
            S = np.abs(vecs @ vecs.T)
            iu = np.triu_indices(len(words), k=1)
            cue_collision[i] = float(S[iu].mean())
        if (i + 1) % 1000 == 0 or i == n_items_w - 1:
            print("[decomposition] %d/%d %.0fs" % (i + 1, n_items_w, time.time() - t0), flush=True)

    encoder_collision_sample = [
        _abs_cos(sym_cache[a], sym_cache[b]) for idx, (a, b) in enumerate(
            [(w1, w2) for w1 in list(sym_cache.keys())[:200] for w2 in list(sym_cache.keys())[:200]
             if w1 < w2][:5000])]
    rep["ENCODER_COLLISION_FLOOR_C0"] = {
        "n_pairs_sampled": len(encoder_collision_sample),
        "mean_abs_cos": round(float(np.mean(encoder_collision_sample)), 4) if encoder_collision_sample else None,
        "theoretical_1_over_sqrt_d": round(1.0 / (D_PROJ ** 0.5), 4)}

    FEATURE_SEED_OFFSET = {"n_distinct_cue_words": 1, "cue_collision": 2, "target_store_breadth": 3}

    def bucket_compare(feature: np.ndarray, name: str) -> Dict:
        a = feature[lost_by_projection]
        b = feature[~lost_by_projection]
        a = a[~np.isnan(a)]
        b = b[~np.isnan(b)]
        if a.size < 5 or b.size < 5:
            return {"VOID": "fewer than 5 non-nan items in one bucket", "n_a": int(a.size), "n_b": int(b.size)}
        rng = np.random.default_rng(MASTER_SEED + 8000 + FEATURE_SEED_OFFSET.get(name, 0))
        n_boot_local = 5000
        boot_a = rng.choice(a, size=(n_boot_local, a.size), replace=True).mean(axis=1)
        boot_b = rng.choice(b, size=(n_boot_local, b.size), replace=True).mean(axis=1)
        d = boot_a - boot_b
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")
        return {"mean_lost_by_projection": round(float(a.mean()), 4),
               "mean_other": round(float(b.mean()), 4),
               "margin": {"point": round(float(np.mean(d)), 4), "ci95": [round(lo, 4), round(hi, 4)],
                          "band": band},
               "n_a": int(a.size), "n_b": int(b.size)}

    rep["ITEM_LEVEL_DECOMPOSITION"] = {
        "n_distinct_cue_words": bucket_compare(n_distinct_cue_words, "n_distinct_cue_words"),
        "cue_collision_mean_abs_cos": bucket_compare(cue_collision, "cue_collision"),
        "target_store_breadth": bucket_compare(target_store_breadth, "target_store_breadth")}
    any_separated = any(v.get("margin", {}).get("band") == "ABOVE"
                        for v in rep["ITEM_LEVEL_DECOMPOSITION"].values() if isinstance(v, dict))
    rep["ITEM_LEVEL_LOSS_IS_CONCENTRATED"] = bool(any_separated)

    # ================================ STOP-IF DECISION =============================================
    separated_props = [arm for arm in ("S1_SPARSE_HASH_PROJ", "N1_NONNEG_PROJ", "B1_BINARIZED_RAW")
                       if margins[arm]["vs_C0_PROJECTED_256"]["band"] == "ABOVE"]
    if len(separated_props) == 0 and not any_separated:
        verdict = "iii_HONEST_NULL_DIFFUSE"
        headline = ("No property arm (S1/N1/B1) separates from C0 CI-separated, and no per-item "
                   "feature CI-separates the lost-by-projection bucket from the rest. The loss "
                   "is DIFFUSE. Design constraint: do not compress this representation, rather "
                   "than compress it differently.")
    elif len(separated_props) == 1:
        verdict = "ii_SINGLE_PROPERTY_ACCOUNTS_FOR_GAP"
        headline = ("%s is CI-separated ABOVE C0 (%r), recovering %r of the U0-C0 gap. This is a "
                   "DESIGN CONSTRAINT for the next encoder, not a capability claim." % (
                       separated_props[0], margins[separated_props[0]]["vs_C0_PROJECTED_256"],
                       margins[separated_props[0]].get("fraction_of_U0_minus_C0_gap_recovered")))
    elif len(separated_props) > 1:
        verdict = "iv_MULTIPLE_PROPERTIES_SEPARATE"
        headline = "More than one property arm separates from C0: %r. Reported individually, not forced to one winner." % separated_props
    else:
        verdict = "iii_HONEST_NULL_NO_ARM_BUT_ITEM_LEVEL_SIGNAL"
        headline = ("No arm-level property separates from C0, but the item-level decomposition "
                   "found a CI-separated feature difference for the lost-by-projection bucket: %r" %
                   {k: v.get("margin") for k, v in rep["ITEM_LEVEL_DECOMPOSITION"].items()})
    rep["STOP_IF_VERDICT"] = {"verdict": verdict, "headline": headline,
                              "separated_property_arms": separated_props,
                              "item_level_loss_is_concentrated": any_separated}
    print("[VERDICT] %s :: %s" % (verdict, headline), flush=True)

    rep["elapsed_s"] = round(time.time() - t0, 1)
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("WROTE " + os.path.join(out_dir, "metrics.json"), flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    out_dir = _out_dir(a.grid)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        run(a.grid)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(out_dir, "_crash_diagnostic.json"),
                    {"error": "%s: %s" % (type(exc).__name__, exc),
                     "traceback": traceback.format_exc(),
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
