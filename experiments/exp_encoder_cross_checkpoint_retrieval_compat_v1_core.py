"""Cross-checkpoint retrieval-compatibility probe (continual-encoder validation).

Spec source: notes/research_drill_brain_grounded_continual_self_improving_encoder_2026-07-04.md
("Cheap decisive test" section). Answers the USER's strategic question: if the
concept encoder is UPDATED (version B) after vectors were already stored by an
earlier version (A), can a query encoded by one version still retrieve the
correct item stored by the other -- or does an encoder update silently break
every stored vector? This is READ-ONLY: no training, reuses the two already-
finished R1 MID checkpoints (data/substrate_concept_encoder_v1b_v3global_mid/
_ckpt_block_{global,in_batch}.pt, both step 1800). Local CPU only. Does NOT
touch the running v3b GPU cell or its dirs (substrate_concept_encoder_v1b_v3b_*)
-- this cell has its own artifact/output dirs.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01): query
"cross-checkpoint retrieval compatibility encoder version backward compatible
embedding drift" -> top hit cosine=0.3916, generic WordNet "compatibility" /
"incompatibility" antonym-pair lexical entries (not a prior arc cell); nearest
substrate-relevant hit "Versioning + backwards compatibility"
(notes/research_drill_production_deployment_architecture_2026-06-07.md,
cosine=0.376) is a DIFFERENT topic (deployment/ops versioning, not encoder
cross-checkpoint retrieval). NONE of the top-5 hits are a prior arc cell
addressing this specific probe. GENUINELY NOVEL instantiation of the
continual-encoder research drill's own "cheap decisive test" recommendation.

CAVEAT ON INSTANTIATION (read before interpreting numbers): the drill's
literal design compares step1200-vs-step1800 checkpoints of ONE lineage
(within-run drift). No intermediate per-step checkpoints were saved for
either R1 MID arm (only the final step-1800 checkpoint exists per arm), and a
retrain to manufacture one was judged out of scope for a "cheap decisive"
probe. Instead this cell instantiates cross-"version" as the two arms that DO
exist: GLOBAL-objective (anchors every training step to a fixed landmark
frame -- the R1 fix) as "version A", and IN_BATCH-objective (the v2 baseline;
no landmark anchor at all) as "version B". Both are derived from the SAME
seed=7 held-out split and the SAME teacher embedding space, so this is a
FAITHFUL "did an encoder UPDATE (objective swap, a realistic real-world
encoder-improvement event) break already-stored vectors" test -- directly
answering the USER's question -- but it is only a PARTIAL test of the
narrower "the landmark anchor IS a BCT mechanism" claim, since only the A
arm references the anchor; B never does. A high cross-arm compatibility
number here is arguably BETTER news than the narrow BCT claim (it would show
two independently-trained objectives sharing only a teacher embedding space,
with NO explicit compatibility loss between them, still preserve retrieval --
a free floor); a low number validates the drill's Part-3 recommendation to
add an explicit compatibility loss before promoting a new encoder version
into production. Either outcome is informative; report both directions
(A-index/B-query and B-index/A-query) and both codes (DENSE, BLOCK) rather
than cherry-picking one.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at run gate (sha256 over the 4 code matrices: A_dense,
  B_dense, A_block, B_block)
- final_metrics_atomicity: tmp_replace (this cell writes its own tmp+os.replace,
  does not rely on _seed_checkpoint.write_metrics's non-atomic write)
- except SystemExit / KeyboardInterrupt: raise BEFORE except Exception (no
  bare except, no except BaseException)
- crlb_floor_computed: n/a -- this is a retrieval-identity ratio, not a
  noise-floor/capacity metric; the closest analytical floor is CHANCE-LEVEL
  top-1 retrieval = 1/n_probe (SMOKE ~1/200=0.005, FULL ~1/4390=0.00023),
  verified empirically via the RANDOM_CONTROL arm rather than a closed-form
  bound (declared crlb_n/a below with rationale)
- baseline_in_band (META_RULE_AG analog): SAME-checkpoint retrieval must be
  >= 0.99 (near-ceiling sanity: if not, the retrieval computation itself is
  broken, not a real result) -- hard-asserted, not just reported
- discriminator-fires: RANDOM_CONTROL (two independent random codebooks) must
  score <= 0.10 -- proves the metric has real floor-vs-ceiling dynamic range,
  is not vacuously saturating to 1.0 regardless of input
- discriminator survives scale: SMOKE runs at n_probe=200 (subsample of the
  4390-item held set) and FULL runs at the full held set (n=4390); the
  qualitative question (is cross-checkpoint retrieval close to the
  same-checkpoint ceiling) is not scale-sensitive here (chance level scales
  as 1/n either way, always far below both HARD_PASS/HARD_FAIL thresholds),
  so smoke-at-reduced-N is a legitimate discriminator preview, not merely a
  machinery check (option A/C hybrid per DISCRIMINATOR-MUST-SURVIVE-SCALE)
- HARD_PASS strictly above floor + 5% band-width (META_RULE_L): thresholds are
  taken directly from the drill's own falsifiable predictions (>=0.90 PASS,
  <0.50 FAIL, 0.50-0.90 MIDDLE_BAND) -- not re-derived here, cited from spec
- HP_SCOPE: HARD_PASS/HARD_FAIL gate applies to the 4 CROSS/SAME ratio units
  only (A_index_B_query x {dense,block}, B_index_A_query x {dense,block});
  SAME_* and RANDOM_CONTROL_* units are integrity-only, exempt from the gate
- cardinality_ok: EXPECTED_N_UNITS = 10 (2 SAME x 2 codes + 2 CROSS-directions
  x 2 codes + 1 RANDOM_CONTROL x 2 codes = 4+4+2=10); verdict counts per_unit
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (identical regime/split/arch
  to the already-validated R1 MID cell; this cell only adds a read-only
  cross-encode + retrieval pass, no new training config)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the
  prereg (preregs/2026-07-04_exp_encoder_cross_checkpoint_retrieval_compat_v1.md)

Prereg: preregs/2026-07-04_exp_encoder_cross_checkpoint_retrieval_compat_v1.md
Reused (import only, NOT edited): experiments/exp_encoder_migration_step1b_v3_
global_objective_landmark_rkd_concept_encoder_v1_core.py

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402
from experiments.exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core import (  # noqa: E402
    N_DIM_DEFAULT, K_BLOCKS_PRIMARY, SEED_DEFAULT, HELD_FRAC, MID_HELD_CAP,
    _resolve_teacher_cache, _load_teacher, _make_student,
    _encode_hard_block, _dense_sign_codes, _random_block_codes,
)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_cross_checkpoint_retrieval_compat_v1"

CKPT_DIR = _REPO / "data" / "substrate_concept_encoder_v1b_v3global_mid"
CKPT_A = CKPT_DIR / "_ckpt_block_global.pt"     # "version A": GLOBAL objective (R1 fix)
CKPT_B = CKPT_DIR / "_ckpt_block_in_batch.pt"   # "version B": IN_BATCH objective (v2 baseline)
EXPECTED_MID_SPLIT = (39515, 4390)              # (n_train, n_held); MEASURED@mid_run.log

SMOKE_N_PROBE = 200
EXPECTED_N_UNITS = 10

# Falsifiable predictions CITED@notes/research_drill_brain_grounded_continual_
# self_improving_encoder_2026-07-04.md ("Cheap decisive test" section) --
# not re-derived here.
HARD_PASS_RATIO = 0.90
HARD_FAIL_RATIO = 0.50

# Discriminator-fires sanity gates (this cell's own correctness self-checks).
SAME_CKPT_SANITY_FLOOR = 0.99
RANDOM_CONTROL_CEILING = 0.10


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / arms-must-differ).
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": int(expected_n_units),
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _arms_must_differ(arms_outputs: Dict[str, torch.Tensor]) -> Dict[str, str]:
    """META_RULE_AF: catches bit-identical arms (e.g. same checkpoint loaded
    twice by mistake). Raises loudly rather than silently continuing."""
    digests: Dict[str, str] = {}
    for name, out in arms_outputs.items():
        arr = out.detach().cpu().contiguous().numpy()
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: arms {a!r} and "
                    f"{b!r} bit-identical (hash={digests[a]}); checkpoint "
                    f"loaded twice by mistake or arm-implementation bug")
    return digests


# ---------------------------------------------------------------------------
# Core retrieval metric.
# ---------------------------------------------------------------------------

@torch.no_grad()
def _top1_retrieval(query_codes: torch.Tensor, index_codes: torch.Tensor) -> float:
    """Top-1 nearest-neighbor retrieval accuracy.

    query_codes[i] and index_codes[i] encode the SAME concept (aligned by
    held-set row order). For each query row i, does argmax_j cos(query_i,
    index_j) == i? Ground truth is row-identity (both code sets are built
    over the identical concept ordering), not a teacher-similarity proxy.
    Chunked over query rows to bound peak memory.
    """
    if query_codes.shape != index_codes.shape:
        raise ValueError(
            f"failure_class=SHAPE_MISMATCH: query {tuple(query_codes.shape)} "
            f"vs index {tuple(index_codes.shape)}")
    n = query_codes.shape[0]
    qn = query_codes / (query_codes.norm(dim=-1, keepdim=True) + 1e-8)
    idxn = index_codes / (index_codes.norm(dim=-1, keepdim=True) + 1e-8)
    correct = 0
    chunk = 1024
    for lo in range(0, n, chunk):
        hi = min(lo + chunk, n)
        sims = qn[lo:hi] @ idxn.T
        pred = sims.argmax(dim=1)
        target = torch.arange(lo, hi)
        correct += int((pred == target).sum())
    return correct / n


# ---------------------------------------------------------------------------
# Self-test (synthetic, no disk artifacts, validates _top1_retrieval itself).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()
    torch.manual_seed(0)
    n, d = 500, 128

    def _rand_codes(seed: int) -> torch.Tensor:
        g = torch.Generator().manual_seed(seed)
        c = torch.sign(torch.randn(n, d, generator=g))
        c[c == 0] = 1.0
        return c

    codes_a = _rand_codes(1)

    # (a) same-codebook retrieval must be exactly 1.0 (self is always the
    # unique cosine-1.0 maximum; no other row can exceed it).
    same = _top1_retrieval(codes_a, codes_a)
    if same != 1.0:
        raise AssertionError(
            f"self-test FAIL: same-codebook retrieval={same} (expected 1.0)")

    # (b) an INDEPENDENT random codebook must be near chance (<<0.5), proving
    # the metric does not vacuously saturate to 1.0 regardless of input.
    codes_b = _rand_codes(2)
    rnd = _top1_retrieval(codes_a, codes_b)
    if rnd >= 0.25:
        raise AssertionError(
            f"self-test FAIL: independent-random retrieval={rnd:.4f} "
            f"(expected near chance ~1/{n}={1.0/n:.4f}, got suspiciously high)")

    # (c) a KNOWN partial-compatibility case: 20% of rows independently
    # replaced ("encoder update corrupted these") -> expect retrieval close
    # to 0.80 (not 1.0, not floor). Validates the metric resolves partial
    # drift, not just the two extremes.
    codes_c = codes_a.clone()
    n_corrupt = int(round(n * 0.20))
    g_corrupt = torch.Generator().manual_seed(3)
    codes_c[:n_corrupt] = torch.sign(torch.randn(n_corrupt, d, generator=g_corrupt))
    codes_c[codes_c == 0] = 1.0
    partial = _top1_retrieval(codes_a, codes_c)
    if abs(partial - 0.80) > 0.05:
        raise AssertionError(
            f"self-test FAIL: 80%-identical/20%-corrupted retrieval={partial:.4f} "
            f"(expected ~0.80 +/- 0.05)")

    # (d) arms-must-differ helper: must raise on identical input, must NOT
    # raise (and return distinct digests) on differing input.
    digests = _arms_must_differ({"a": codes_a, "b": codes_b})
    if digests["a"] == digests["b"]:
        raise AssertionError("self-test FAIL: arms_must_differ digests collided")
    raised = False
    try:
        _arms_must_differ({"a": codes_a, "a_dup": codes_a.clone()})
    except RuntimeError:
        raised = True
    if not raised:
        raise AssertionError(
            "self-test FAIL: arms_must_differ did not raise on identical arms")

    elapsed = time.perf_counter() - t0
    print(f"[selftest] PASS same={same:.4f} random={rnd:.4f} "
          f"partial80={partial:.4f} ({elapsed:.2f}s)", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Real-checkpoint probe.
# ---------------------------------------------------------------------------

@torch.no_grad()
def _encode_checkpoint(ckpt_path: Path, X: torch.Tensor, n_dim: int, kb: int,
                       blk_l: int, device: str, seed: int) -> Dict:
    if not ckpt_path.exists():
        raise FileNotFoundError(
            f"failure_class=CHECKPOINT_MISSING: {ckpt_path}")
    student = _make_student("mlp", X.shape[1], n_dim, device, seed)
    ckpt = torch.load(str(ckpt_path), map_location=device)
    load_result = student.load_state_dict(ckpt["student"])
    if load_result.missing_keys or load_result.unexpected_keys:
        raise RuntimeError(
            f"failure_class=STATE_DICT_MISMATCH: {ckpt_path.name} "
            f"missing={load_result.missing_keys} "
            f"unexpected={load_result.unexpected_keys}")
    student.eval()
    dense = _dense_sign_codes(student, X)
    block = _encode_hard_block(student, X, kb, blk_l)
    return {"dense": dense, "block": block, "ckpt_step": ckpt.get("step")}


def run_probe(run_mode: str, seed: int, out_dir: Path) -> int:
    device = "cpu"
    expected_units = EXPECTED_N_UNITS
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[xckpt] run_mode={run_mode} seed={seed} device={device} "
          f"ckpt_A={CKPT_A} ckpt_B={CKPT_B}", flush=True)

    n_dim = N_DIM_DEFAULT
    kb = K_BLOCKS_PRIMARY
    blk_l = n_dim // kb

    cache_path = _resolve_teacher_cache(None)
    X, ids = _load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[xckpt] teacher {cache_path.name}: {V_cache} concepts x "
          f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * HELD_FRAC)), MID_HELD_CAP)
    n_tr = V_cache - n_he
    he_idx = perm[n_tr:n_tr + n_he]
    split_match = (n_tr, n_he) == EXPECTED_MID_SPLIT
    print(f"[xckpt] split replica: n_tr={n_tr} n_he={n_he} "
          f"match_mid_run={split_match}", flush=True)
    if not split_match:
        raise RuntimeError(
            f"failure_class=SPLIT_MISMATCH: expected {EXPECTED_MID_SPLIT}, "
            f"got ({n_tr}, {n_he}) -- teacher cache selection drifted; the "
            f"two checkpoints were trained against a DIFFERENT held split "
            f"than this replica would produce")

    Xhe_full = X[torch.from_numpy(he_idx.copy())].contiguous()

    if run_mode == "smoke":
        gsub = np.random.default_rng(seed + 999)
        sub_idx = np.sort(gsub.choice(Xhe_full.shape[0], size=SMOKE_N_PROBE,
                                      replace=False))
        Xhe = Xhe_full[torch.from_numpy(sub_idx.copy())].contiguous()
    else:
        Xhe = Xhe_full
    print(f"[xckpt] probe set n={Xhe.shape[0]} (of held {Xhe_full.shape[0]}) "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    codes_a = _encode_checkpoint(CKPT_A, Xhe, n_dim, kb, blk_l, device, seed)
    print(f"[xckpt] encoded A (GLOBAL) ckpt_step={codes_a['ckpt_step']} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)
    codes_b = _encode_checkpoint(CKPT_B, Xhe, n_dim, kb, blk_l, device, seed)
    print(f"[xckpt] encoded B (IN_BATCH) ckpt_step={codes_b['ckpt_step']} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    digests = _arms_must_differ({
        "A_dense": codes_a["dense"], "B_dense": codes_b["dense"],
        "A_block": codes_a["block"], "B_block": codes_b["block"],
    })

    gen_r1 = torch.Generator().manual_seed(seed + 501)
    gen_r2 = torch.Generator().manual_seed(seed + 502)
    rand_dense_1 = torch.sign(torch.randn(Xhe.shape[0], n_dim, generator=gen_r1))
    rand_dense_1[rand_dense_1 == 0] = 1.0
    rand_dense_2 = torch.sign(torch.randn(Xhe.shape[0], n_dim, generator=gen_r2))
    rand_dense_2[rand_dense_2 == 0] = 1.0
    rand_block_1 = _random_block_codes(Xhe.shape[0], kb, blk_l, gen_r1)
    rand_block_2 = _random_block_codes(Xhe.shape[0], kb, blk_l, gen_r2)

    units: List[Dict] = []

    def _unit(name: str, query: torch.Tensor, index: torch.Tensor) -> float:
        acc = _top1_retrieval(query, index)
        units.append({"unit": name, "top1_retrieval": acc, "n": query.shape[0]})
        print(f"[xckpt] unit {name}: top1_retrieval={acc:.4f}", flush=True)
        return acc

    same_a_dense = _unit("SAME_A_DENSE", codes_a["dense"], codes_a["dense"])
    same_a_block = _unit("SAME_A_BLOCK", codes_a["block"], codes_a["block"])
    same_b_dense = _unit("SAME_B_DENSE", codes_b["dense"], codes_b["dense"])
    same_b_block = _unit("SAME_B_BLOCK", codes_b["block"], codes_b["block"])
    # CROSS: index built by one version (frozen "already stored"), query
    # encoded by the OTHER version (the "updated encoder"). Both directions.
    cross_aidx_bq_dense = _unit("CROSS_INDEX_A_QUERY_B_DENSE",
                                codes_b["dense"], codes_a["dense"])
    cross_aidx_bq_block = _unit("CROSS_INDEX_A_QUERY_B_BLOCK",
                                codes_b["block"], codes_a["block"])
    cross_bidx_aq_dense = _unit("CROSS_INDEX_B_QUERY_A_DENSE",
                                codes_a["dense"], codes_b["dense"])
    cross_bidx_aq_block = _unit("CROSS_INDEX_B_QUERY_A_BLOCK",
                                codes_a["block"], codes_b["block"])
    random_dense = _unit("RANDOM_CONTROL_DENSE", rand_dense_1, rand_dense_2)
    random_block = _unit("RANDOM_CONTROL_BLOCK", rand_block_1, rand_block_2)

    # --- discriminator-fires / correctness sanity gates (hard asserts) -----
    for name, v in [("SAME_A_DENSE", same_a_dense), ("SAME_A_BLOCK", same_a_block),
                    ("SAME_B_DENSE", same_b_dense), ("SAME_B_BLOCK", same_b_block)]:
        if v < SAME_CKPT_SANITY_FLOOR:
            raise RuntimeError(
                f"failure_class=SAME_CHECKPOINT_SANITY_FAIL: {name}={v:.4f} "
                f"< {SAME_CKPT_SANITY_FLOOR} (retrieval-computation bug or "
                f"degenerate code collapse; do not trust cross numbers)")
    for name, v in [("RANDOM_CONTROL_DENSE", random_dense),
                    ("RANDOM_CONTROL_BLOCK", random_block)]:
        if v > RANDOM_CONTROL_CEILING:
            raise RuntimeError(
                f"failure_class=RANDOM_CONTROL_TOO_HIGH: {name}={v:.4f} > "
                f"{RANDOM_CONTROL_CEILING} (metric may be vacuously "
                f"saturating; discriminator-fires check failed)")

    ratios = {
        "A_index_B_query_dense": cross_aidx_bq_dense / same_a_dense,
        "A_index_B_query_block": cross_aidx_bq_block / same_a_block,
        "B_index_A_query_dense": cross_bidx_aq_dense / same_b_dense,
        "B_index_A_query_block": cross_bidx_aq_block / same_b_block,
    }
    min_ratio = min(ratios.values())
    tail = "[" + " ".join(f"{k}={v:.4f}" for k, v in ratios.items()) + "]"

    if min_ratio >= HARD_PASS_RATIO:
        verdict = "HARD_PASS"
        verdict_msg = (f"cross-checkpoint retrieval >= {HARD_PASS_RATIO*100:.0f}% "
                       f"of same-checkpoint in ALL 4 direction/code combos "
                       f"(min={min_ratio:.4f}); compatibility-loss work is "
                       f"NEXT-priority, not an urgent blocker {tail}")
    elif min_ratio < HARD_FAIL_RATIO:
        verdict = "HARD_FAIL"
        verdict_msg = (f"cross-checkpoint retrieval < {HARD_FAIL_RATIO*100:.0f}% "
                       f"of same-checkpoint in at least one direction/code "
                       f"combo (min={min_ratio:.4f}); pull the explicit "
                       f"compatibility-loss work FORWARD to NOW, before any "
                       f"periodic re-distillation cadence is adopted {tail}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"cross-checkpoint retrieval between "
                       f"{HARD_FAIL_RATIO*100:.0f}-{HARD_PASS_RATIO*100:.0f}% "
                       f"of same-checkpoint (min={min_ratio:.4f}); real "
                       f"drift-vulnerability but not urgent; proceed with "
                       f"the NEXT-priority compatibility-loss item as scoped "
                       f"in the drill {tail}")

    cardinality_ok = len(units) == expected_units
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                       f"{len(units)} units != expected {expected_units}")

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": seed,
        "n_probe": int(Xhe.shape[0]),
        "n_held_full": int(Xhe_full.shape[0]),
        "ckpt_a_path": str(CKPT_A), "ckpt_a_step": codes_a["ckpt_step"],
        "ckpt_b_path": str(CKPT_B), "ckpt_b_step": codes_b["ckpt_step"],
        "per_unit": units,
        "ratios": ratios,
        "min_ratio": min_ratio,
        "hard_pass_threshold": HARD_PASS_RATIO,
        "hard_fail_threshold": HARD_FAIL_RATIO,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "arms_differ_verified": True,
        "arm_digests": digests,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "instantiation_caveat": (
            "cross-'version' = GLOBAL-objective vs IN_BATCH-objective final "
            "(step 1800) checkpoints of the SAME R1 MID run, not sequential "
            "steps of one lineage; see cell docstring CAVEAT section"),
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    print(f"[xckpt] wrote {out_dir / 'metrics.json'} verdict={verdict} "
          f"({elapsed:.1f}s)", flush=True)
    return 0


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    return p


def _resolve_run_mode(args: argparse.Namespace) -> str:
    if args.self_test:
        return "self_test"
    if args.full:
        return "full"
    if args.smoke:
        return "smoke"
    return args.run_mode


def main() -> int:
    p = build_argparser()
    args = p.parse_args()
    run_mode = _resolve_run_mode(args)
    if run_mode == "self_test":
        return run_self_test()
    anchor = ANCHOR_NAME if run_mode == "full" else f"{ANCHOR_NAME}_{run_mode}"
    out_dir = get_output_dir(anchor)
    try:
        return run_probe(run_mode, args.seed, out_dir)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves the two above
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    sys.exit(main())
