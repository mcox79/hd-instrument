"""glass_box_micro_loop_conceptnet_multihop_SCALE_v1 -- scale the CERTIFIED glass-box multi-hop
reasoning micro-loop from the toy-real regime (V~580) toward the REAL ingested knowledge base by
growing the ENTITY COUNT (codebook / disambiguation space) 10-80x, holding ALL glass-box properties.

WHAT THIS IS (forward-integration cell; CPU/numpy BLAS-batched; no GPU, no encoder, no torch):
  Takes the CG-certified retrieve->gate(self-audit)->WM-requery->commit loop with per-hop Merkle audit
  (exp_glass_box_micro_loop_conceptnet_multihop_v1, commit 200b66c3f -- itself extending the toy-certified
  ba552930a) and asks the deep-prize question: does NON-CEILING multi-hop reasoning AND the glass-box
  self-audit HOLD when the reasoner must disambiguate the answer among 10-80x more REAL ingested entities?

  THE SCALING AXIS (V = codebook entity count = number of distinct REAL ConceptNet nodes the per-hop
  cleanup must resolve the true answer AMONG). This is the "entity count" of the locked deep prize:
  substrate reasoning OVER ingested knowledge, at scale. Grid:
      V ~ {600, 6000, 24000, 48000}  =  ~{1x, 10x, 40x, 80x}  over the certified base V~580.
  The base V600 tier is an exact-machinery replica (positive control for "same loop, tiny KB").

  WHY V (codebook) IS THE RIGHT SCALING AXIS, AND WHY THE STORE M IS HELD FIXED:
    The single-cue bundle capacity law is  M < N/(2 ln V):  reliable top1 over a bundle of M edges
    requires N to beat the MAX crosstalk over V cleanup candidates -- the ln V term IS the entity count.
    Growing V is therefore the physics-relevant "reason over a bigger KB" stressor: each hop's cleanup
    must beat the true node against ever more real distractors. We hold the STORE at the certified base
    operating point (n_hard=n_easy=120, M_SYN=120, M_ISA=240 edges) so per-hop REASONING difficulty is
    bit-identical across the grid; the SOLE thing that scales is codebook-crosstalk. Any degradation is
    then cleanly attributable to entity-count scale, not to a changed reasoning task.

    HONEST LIMIT (documented, becomes the next drill): CO-scaling the bundled store (M proportional to V)
    would require N ~ M ln V -- QUADRATIC in entity count (codebook memory ~ V*N ~ V^2 ln V) -- infeasible
    past V~5-8k on any single machine. That quadratic wall is the known bundle-bound; the established fix
    is SHARDED storage (reference_sharded_fhrr_cleanup_capacity_beyond_bundle_bound; +13.9x, holds at
    L=20+). This cell tests the codebook-scale axis (feasible to 80x) and NAMES the bundled-store quadratic
    wall as the reason store co-scaling is deferred to a sharded follow-up. Not a hidden assumption.

  N SCHEDULE (keep single-cue OFF the wall while V scales -- the deliberate lever): N is HELD at the
  certified base value 8192 across the ENTIRE V grid. Rationale (MEASURED in smoke 2026-07-08): the
  single-cue bundle wall N/(2 ln V) recedes only LOGARITHMICALLY with entity count, so at V=48000 the
  M=240 ISA store is still at 63% of the wall (N/(2 ln V) = 380 > M = 240) and the oracle positive control
  stays clean (0.929 >= 0.85). RAISING N (e.g. to 16384) would over-provision this fixed small store:
  the non-ceiling difficulty here is set by GATE-ROUTING error on the real hard-margin distribution
  ((top1-top2)/N), and doubling N sharpens that margin so routing -> 0.99 and accB SATURATES > 0.95
  (MEASURED: the N=16384 variant HARD-passes every integrity gate but trips SATURATION_TOO_EASY). Holding
  N=8192 keeps accB non-ceiling (0.87-0.92, gate-routing-limited) and tests whether it HOLDS as V scales
  80x. Co-scaling the store M (which WOULD warrant scaling N) hits the quadratic wall documented above.
  THEORETICAL@ M<N/(2 ln V) bundle-crosstalk gaussian max-order-statistic;
  MEASURED@data/exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1_smoke/metrics.json:per_scale.

  peel/SIC readout: NOT APPLICABLE and deliberately NOT used. Every readout in this loop is a single-cue
  top1 lookup (unbind one relation, cleanup argmax). Established (exp_encoder_peel_sic_readout_realcodes_v1):
  confidence-ordered peel/SIC helps ONLY where the loop bundles MULTIPLE items (multi-candidate/multi-bridge
  readout); it does NOT benefit single-cue top1. This loop bundles no multi-item readout, so peel/SIC is
  correctly absent. (If a future variant adds multi-bridge fan-out, peel/SIC applies there.)

THE FALSIFIABLE REGIME (unchanged from the certified base; "B beats A" is NOT tautological):
  Per-seed corpus MIXES two trial types the loop cannot tell apart a priori:
    EASY (frac_easy=0.5): real 1-hop X -IS_A-> B; X is a DIRECT key in the ISA store -> a SINGLE shot
         resolves it with HIGH arbitration margin.
    HARD (1-frac_easy):   real 2-hop X -CN_SYNONYM-> A -IS_A-> B; B is keyed by the BRIDGE A, X has NO ISA
         edge in the store -> a single shot lands on NOISE (LOW margin, wrong). Only a WM-mediated re-query
         (retrieve A into WM, bind A into ISA, unbind B) resolves it. Two hops.
  The margin gate is load-bearing in BOTH directions: ARM_A (always commit shot) resolves EASY fails HARD;
  ARM_ALWAYS_REQUERY resolves HARD breaks EASY; ARM_B (gated: margin>=tau => Go) resolves BOTH.

DISCRIMINATOR-MUST-FIRE AT EVERY SCALE (the #1 error class this session -- saturation-vacuous smoke):
  At EACH V the MUST-FAIL control (single-shot on HARD, accA_hard) must FAIL at THAT V (<=0.15) -- else the
  smoke tests nothing at that scale. The oracle positive control must CLEAR its floor at THAT V (>=0.85)
  and SCRAMBLE (random-bridge re-query) must COLLAPSE at THAT V (scramble_gap>=0.25). All three are asserted
  per-scale in smoke via assert_discriminator_fires; a green at small V that would HARD_FAIL at large V is
  refused. GENERATOR GUARD: every drawn corpus is verified to be REAL ingested structure (every hard chain
  is a genuine X-syn->A-isa->B with B not in isa[X]; every codebook entry is a real graph node) so a
  degenerate/easy slice cannot masquerade as a scaled KB.

THE GLASS-BOX HAND-EDIT DEMONSTRATION (on REAL chains, at every scale):
  (1) TAMPER-DETECT: hand-edit one logged step; recompute the Merkle root -> mismatch -> flag fires (100%).
  (2) CAUSAL-EDIT (monitor-not-control): on a HARD trial ARM_B got correct, hand-edit the logged bridge
      (true A -> distractor); re-run the downstream hop-2 recompute -> committed answer flips correct->wrong.

CONTRACT (pre-registered; preregs/2026-07-08_glass_box_micro_loop_conceptnet_multihop_SCALE_v1.md):
  Gates are evaluated PER SCALE; HARD_PASS requires the headline gates at the LARGEST scale AND the
  integrity gates (audit / retrieval / discriminator-fires / telemetry / non-ceiling / resolve_lift>=0.25)
  at EVERY scale.
  HARD_PASS  : at the TOP scale resolve_lift(accB-accA)>=0.25 AND accB-accALWAYS>=0.15 AND paired sign-test
               p<0.05 AND accB<=0.95 (NON-CEILING) AND accA_hard<=0.15 (discriminator fires) AND
               gate_separation>=0.10 AND gate_routing_acc>=0.85 AND scramble_gap>=0.25 AND causal_edit_flip
               >=0.80 AND arms_differ; AND at EVERY scale: oracle_bridge_acc>=0.85 AND hop1_retrieve_acc
               >=0.80 AND deterministic_replay==1.0 AND merkle_verify==1.0 AND tamper_detect==1.0 AND
               accA_hard<=0.15 AND accB<=0.95 AND resolve_lift>=0.25.
  SCALE_WALL : the loop + audit HOLD at small V but DEGRADE with scale (some larger-V tier drops resolve_lift
               <0.25, or oracle<0.85, or accB>0.95). HONEST HIGH-VALUE finding -> names the exact wall
               (single-cue capacity / cleanup crosstalk / hop-depth compounding / retrieval fidelity).
  MIDDLE_BAND: integrity holds at all scales but a top-scale headline gate lands in a middle band.
  HARD_FAIL  : any scale resolve_lift<0.10 OR tamper_detect<1.0 OR deterministic_replay<1.0 (audit breaks).
  INCONCLUSIVE_* : per-scale tautology / retrieval-broken / discriminator-dead (same taxonomy as base).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 of per-arm answer arrays; A/B/SCRAMBLE/ALWAYS diverge)
# - final_metrics_atomicity: tmp_replace (os.replace) + per (scale,seed) partial checkpoint (resume-safe)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-gap discriminator; reachability by the bundle-SNR feasibility above (32% of wall,
#   N=8192/M=240, 63% of wall at V48000, SNR sqrt(N/M)=5.84) -- oracle positive control reachable (0.929).
# - baseline_in_band (META_RULE_AG): BASELINE is ARM_A on the MIXED corpus, accA ~ frac_easy = 0.5, strictly
#   inside (0.05, 0.95). ARM_B is the mechanism arm (bounded above by 0.95 non-ceiling gate).
# - discriminator survives scale (option A): SMOKE runs the SAME V grid AND the SAME N schedule as FULL
#   (600/6000/24000/48000 all at N=8192) at n_hard/n_easy/M identical to FULL; only seed count
#   differs (2 vs 5). The must-fail control is asserted to FAIL at EVERY V incl. the top V=48000.
# - HARD_PASS strictly above floor (META_RULE_L): gates strict (>=0.25 / <=0.95 / <=0.15 / ==1.0 / >=0.80).
# - HP_SCOPE: resolve/scramble/routing/non-ceiling/discriminator gates apply to ARM_B vs {ARM_A, ARM_ALWAYS,
#   ARM_B_SCRAMBLE}. ARM_ORACLE_BRIDGE carries only the >=0.85 retrieval-ceiling rail (positive control).
# - cardinality_ok: EXPECTED_N_UNITS = len(SCALES) * len(SEEDS); verdict counts completed (scale,seed) units.
# - per-unit failure-class instrumentation (no bare except; per-unit fatal-flag recorded to metrics)
# - calibration_check: default_ok_for_this_regime -- TAU_GATE=0.11 sits at hard-margin p90 / below easy median
#   (a-priori, NOT tuned per-seed); verified telemetry-sensitive by gate_separation at every scale.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@:
#     CN edges 188852 distinct_nodes 141490 hard_anchors_available 37143 easy_sources 50512
#       MEASURED@data/substrate_index/concept/relations.jsonl (enumerated 2026-07-08)
#     base loop HARD_PASS on real 2-hop chains at V~580 CITED@experiments/exp_glass_box_micro_loop_conceptnet_multihop_v1.py (commit 200b66c3f)
#     bundle top1 reliable while M < N/(2 ln V) THEORETICAL@ bundle-crosstalk gaussian max-order-statistic
#     N held 8192 across V grid (single-cue wall recedes only ~ln V) THEORETICAL@ M<N/(2 ln V)
#     accB non-ceiling target hold [0.80,0.94] across scales HYPOTHESIZED@preregs/2026-07-08_..._SCALE_v1.md

Compute architecture: (c) mixed with justification. The loop is genuinely SEQUENTIAL across hops (hop-2
  depends on the hop-1 WM result) and per-trial Merkle/tamper/causal audit is scalar CPU work; but the
  codebook cleanup matvecs (the cost that scales with V) are STAGE-BATCHED into single BLAS gemms across all
  trials (E @ Probes.T), so V=48000 is CPU-feasible (~few min FULL). No torch/GPU: the certified base is
  numpy-only and total FULL work is ~13 TFLOP (BLAS multi-threaded), well under the hours-scale threshold
  the GPU-batching mandate targets; adding a torch/GPU path would rewrite the certified machinery for no
  material wall-clock win. Peak RAM ~1.6GB (V48000 x N8192 float32 codebook). MEASURED smoke wall 64s
  (2 seeds x 4 scales); FULL est ~160s (5 seeds x 4 scales), well under the 5400s matrix_sweep floor.
  Storage: mixed -- each RELATION store is a GLOBAL bundled single-hop associative memory (exemption (a):
  single-hop read WITHIN a hop); cross-hop composition is SHARDED via WM re-binding (the bridge is carried
  in WM and re-bound into the second store, never fused into one global chain bundle).
progress_logging: print_flush_true (line-buffered stdout + flush=True per progress line) + per-(scale,seed)
  heartbeat. FULL timeout_s 5400 (matrix_sweep floor); each (scale,seed) unit checkpoints so a kill/resume
  never loses more than one unit (PROT-021 safe).

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Extends (CG certified): experiments/exp_glass_box_micro_loop_conceptnet_multihop_v1.py (commit 200b66c3f)
Reuses (mechanism-level; not re-run): experiments/exp_reasoning_chain_replay_v1.py (Merkle helpers transcribed).
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_glass_box_micro_loop_conceptnet_multihop_SCALE_v1.md
ASCII-only. No emojis, no em dashes.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (get_output_dir, write_metrics, record_gate,
                                          write_partial_key, aggregate_partials, resumable_seeds,
                                          assert_discriminator_fires)

ANCHOR_NAME = "glass_box_micro_loop_conceptnet_multihop_SCALE_v1"
RELATIONS_PATH = REPO / "data" / "substrate_index" / "concept" / "relations.jsonl"
REL_HOP1 = "CN_SYNONYM"   # X -CN_SYNONYM-> A  (bridge)
REL_HOP2 = "IS_A"         # A -IS_A-> B        (answer)

# --------------------------- CLI / run-mode ---------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else ("selftest" if _ARGS.self_test
                  else os.environ.get("HDLAB_RUN_MODE", "full").lower()))
SELF_TEST_MODE = bool(_ARGS.self_test)

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
HP_RESOLVE_LIFT_MIN = 0.25       # accB - accA (loop adds real capability over single shot)
HP_GATE_ROUTE_MARGIN = 0.15      # accB - accALWAYS (gated routing beats always-requery)
HP_NONCEILING_MAX = 0.95         # accB <= this (NON-CEILING: genuine real-graph difficulty)
HP_DISCRIM_ACCA_HARD_MAX = 0.15  # accA_hard <= this (single-shot fails the multi-hop => discriminator fires)
HP_GATE_SEP_MIN = 0.10           # mean margin(EASY) - mean margin(HARD) (self-audit telemetry-sensitive)
HP_GATE_ROUTING_ACC_MIN = 0.85   # fraction of trials routed correctly (easy->accept, hard->requery)
HP_SCRAMBLE_GAP_MIN = 0.25       # accB - accB_scramble (WM content is what resolves)
HP_ORACLE_BRIDGE_MIN = 0.85      # oracle-bridge retrieval ceiling (positive control at each scale)
HP_HOP1_RETRIEVE_MIN = 0.80      # WM active-slot content is correctly retrieved (absorbs real branching)
HP_CAUSAL_FLIP_MIN = 0.80        # hand-editing the logged bridge flips correct->wrong downstream
HF_RESOLVE_LIFT_CEIL = 0.10      # resolve_lift < this => HARD_FAIL (loop adds nothing)
MB_RESOLVE_LIFT_LO = 0.10        # resolve_lift in [0.10,0.25) => MIDDLE_BAND
MB_GATE_SEP_LO = 0.05            # gate_separation in [0.05,0.10) => MIDDLE_BAND
MB_CAUSAL_FLIP_LO = 0.50         # causal_edit_flip in [0.50,0.80) => MIDDLE_BAND
TAUT_SCRAMBLE_FLOOR = 0.10       # scramble_gap < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
TAUT_GATE_SEP_FLOOR = 0.05       # gate_separation < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
SIGN_P_MAX = 0.05                # paired sign-test threshold

# gate threshold: a-priori between the HARD-margin distribution and the EASY-margin distribution. Same
# value the certified base uses (0.11); it is scale-robust because the per-hop store density (M) is held
# fixed across the V grid, so the easy/hard margin distributions do not move with V. A SINGLE fixed value
# (NOT tuned per-seed / per-scale). Verified telemetry-sensitive by gate_separation at every scale.
TAU_GATE = 0.11
FRAC_EASY = 0.5                  # mixed corpus: half easy (1-hop, single-shot resolves), half hard (2-hop)

# --------------------------- scale grid + N schedule ---------------------------
# Each scale = (V_TARGET codebook size, N_DIM). Store held FIXED (n_hard/n_easy/M) across the grid so the
# ONLY axis that scales is codebook crosstalk. N held 8192 across the grid (single-cue wall ~ N/(2 ln V)
# recedes only logarithmically, so N=8192 stays off the wall through V=48000; see docstring N SCHEDULE).
N_HARD = 120
N_EASY = 120
M_SYN = 100                      # no-op ceiling: syn_edges = n_hard = 120 > 100 => 0 distractors => 120 edges
M_ISA = 150                      # no-op ceiling: isa_edges = n_hard+n_easy = 240 > 150 => 0 distractors => 240

if SELF_TEST_MODE:
    N_HARD = 10
    N_EASY = 10
    M_SYN = 20
    M_ISA = 24
    SCALES: List[Tuple[int, int]] = [(80, 1024)]    # tiny synthetic scale (no data-file dependency)
    SEEDS = [7]
    USE_REAL_GRAPH = False
elif RUN_MODE == "smoke":
    # v1.0 smoke == FULL V grid + FULL N + FULL store (discriminator-survives-scale option A); only the seed
    # count differs (2 vs 5). The must-fail control is asserted to fail at EVERY V incl. 48000.
    SCALES = [(600, 8192), (6000, 8192), (24000, 8192), (48000, 8192)]
    SEEDS = [7, 17]
    USE_REAL_GRAPH = True
else:  # full
    SCALES = [(600, 8192), (6000, 8192), (24000, 8192), (48000, 8192)]
    SEEDS = [7, 17, 23, 31, 41]
    USE_REAL_GRAPH = True

N_TRIALS = N_HARD + N_EASY
EXPECTED_N_UNITS = len(SCALES) * len(SEEDS)
ARMS = ["ARM_A_SINGLE_SHOT", "ARM_B_WM_REQUERY", "ARM_B_SCRAMBLE",
        "ARM_ALWAYS_REQUERY", "ARM_ORACLE_BRIDGE"]

CONFIG_VERSION = (
    "ANCHOR=%s,scales=%s,n_hard=%d,n_easy=%d,M_syn=%d,M_isa=%d,frac_easy=%.2f,tau_gate=%.2f,seeds=%s,"
    "mode=%s,real_graph=%s,rel1=%s,rel2=%s,expected_n=%d,HP_resolve>=%.2f,HP_nonceil<=%.2f,"
    "HP_discrimAccAhard<=%.2f"
) % (ANCHOR_NAME, SCALES, N_HARD, N_EASY, M_SYN, M_ISA, FRAC_EASY, TAU_GATE, SEEDS, RUN_MODE,
     USE_REAL_GRAPH, REL_HOP1, REL_HOP2, EXPECTED_N_UNITS, HP_RESOLVE_LIFT_MIN, HP_NONCEILING_MAX,
     HP_DISCRIM_ACCA_HARD_MAX)

_T0 = time.time()


# ============================================================================
# Merkle audit helpers -- TRANSCRIBED VERBATIM from experiments/exp_reasoning_chain_replay_v1.py
# (HARD_PASS 100pct deterministic replay + Merkle verify + tamper detect).
# CITED@experiments/exp_reasoning_chain_replay_v1.py.
# ============================================================================
def h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def merkle_root(steps: List[str]) -> bytes:
    """Chain steps into a single Merkle-style root: c=h(genesis); c=h(c+step) for each step."""
    c = h(b"genesis")
    for s in steps:
        c = h(c + s.encode("utf-8"))
    return c


def merkle_verify(steps: List[str], root: bytes) -> bool:
    """Recompute the root from the recorded steps and confirm it matches the committed root."""
    return merkle_root(steps) == root


# ============================================================================
# defensive-error-checking helpers (start marker / crash diag / heartbeat)
# ============================================================================
def _write_start_marker(out_dir: Path) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _atomic_write_metrics(out_dir: Path, payload: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": round(time.time() - _T0, 1), "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "run_mode": RUN_MODE, "config_version": CONFIG_VERSION}
    try:
        _atomic_write_metrics(out_dir, diag)
    except Exception as e:
        print("[_write_crash_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _heartbeat(out_dir: Path, unit_idx: int, total: int, note: str = "") -> None:
    try:
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
               "total_units": total, "elapsed_s": round(time.time() - _T0, 1), "note": note}
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# ============================================================================
# substrate primitives (bipolar HD; CPU numpy). bind = elementwise product; bundle = sum;
# cleanup = argmax over codebook of the dot score. margin = (top1 - top2)/N (arbitration "why-signal").
# BATCHED cleanup: one BLAS gemm resolves all trials in a stage (E @ Probes.T).
# ============================================================================
def make_codebook(V: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """(V, N) bipolar +/-1 float32 codebook (sharded; each concept its own random vector)."""
    return (rng.integers(0, 2, size=(V, N)).astype(np.float32) * 2.0 - 1.0)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def cleanup_batch(P: np.ndarray, E: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Batched cleanup. P: (n, N) probes; E: (V, N) codebook.
    Returns (best_ids (n,), margins (n,)) where margin = (top1 - top2) / N."""
    N = E.shape[1]
    scores = P @ E.T                                 # (n, V) single BLAS gemm
    n, V = scores.shape
    if V < 2:
        best = np.argmax(scores, axis=1)
        return best.astype(np.int64), np.ones(n, dtype=np.float32)
    part = np.argpartition(scores, -2, axis=1)[:, -2:]        # (n, 2) unordered top2 idx
    rows = np.arange(n)[:, None]
    pvals = scores[rows, part]                                # (n, 2)
    order = np.argsort(pvals, axis=1)                         # ascending; col 1 = larger
    best_local = part[rows, order[:, 1:2]].ravel()           # (n,)
    second_local = part[rows, order[:, 0:1]].ravel()         # (n,)
    best_scores = scores[np.arange(n), best_local]
    second_scores = scores[np.arange(n), second_local]
    margins = ((best_scores - second_scores) / N).astype(np.float32)
    return best_local.astype(np.int64), margins


# ============================================================================
# REAL ConceptNet graph loading (cached) + tiny SYNTHETIC graph for selftest
# ============================================================================
_CN_CACHE: Dict[str, Any] = {}


def load_cn_graph(path: Path) -> Dict[str, Any]:
    """Load the REAL ConceptNet relations into out-adjacency for REL_HOP1 / REL_HOP2. Cached per path.
    Returns syn_out (src->list[tgt]), isa_out (src->list[tgt]), isa_set (src->set[tgt]),
    all_nodes (sorted list of every distinct node -- the codebook decoy pool)."""
    key = str(path)
    if key in _CN_CACHE:
        return _CN_CACHE[key]
    if not path.exists():
        raise FileNotFoundError("ConceptNet relations file not found: %s" % path)
    syn_out: Dict[str, List[str]] = {}
    isa_out: Dict[str, List[str]] = {}
    isa_set: Dict[str, set] = {}
    all_nodes: set = set()
    n_lines = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rt = d.get("rel_type")
            s = d.get("src_id"); t = d.get("tgt_id")
            if s is None or t is None or s == t:
                continue
            all_nodes.add(s); all_nodes.add(t)
            if rt == REL_HOP1:
                syn_out.setdefault(s, []).append(t)
            elif rt == REL_HOP2:
                isa_out.setdefault(s, []).append(t)
                isa_set.setdefault(s, set()).add(t)
            n_lines += 1
    g = {"syn_out": syn_out, "isa_out": isa_out, "isa_set": isa_set,
         "all_nodes": sorted(all_nodes), "n_edges": n_lines}
    print("[cn_graph] loaded %d edges | syn_src=%d isa_src=%d distinct_nodes=%d"
          % (n_lines, len(syn_out), len(isa_out), len(all_nodes)), flush=True)
    _CN_CACHE[key] = g
    return g


def make_synthetic_graph(rng: np.random.Generator, n_hard: int, n_easy: int,
                         m_syn: int, m_isa: int) -> Dict[str, Any]:
    """Tiny SYNTHETIC 2-hop graph for the import selftest (no data-file dependency)."""
    syn_out: Dict[str, List[str]] = {}
    isa_out: Dict[str, List[str]] = {}
    isa_set: Dict[str, set] = {}
    all_nodes: set = set()
    nid = [0]

    def node() -> str:
        nid[0] += 1
        nm = "S_%d" % nid[0]
        all_nodes.add(nm)
        return nm

    for _ in range(n_hard + m_syn):
        x, a, b = node(), node(), node()
        syn_out.setdefault(x, []).append(a)
        isa_out.setdefault(a, []).append(b)
        isa_set.setdefault(a, set()).add(b)
    for _ in range(n_easy + m_isa):
        x, b = node(), node()
        isa_out.setdefault(x, []).append(b)
        isa_set.setdefault(x, set()).add(b)
    # extra inert nodes so a small codebook decoy pool exists for the selftest scale
    for _ in range(200):
        node()
    return {"syn_out": syn_out, "isa_out": isa_out, "isa_set": isa_set,
            "all_nodes": sorted(all_nodes), "n_edges": nid[0]}


# ============================================================================
# per-(scale,seed) corpus construction from the (real or synthetic) graph
# ============================================================================
def build_corpus(graph: Dict[str, Any], seed: int, rng: np.random.Generator,
                 n_hard: int, n_easy: int, m_syn: int, m_isa: int, n_dim: int, v_target: int
                 ) -> Optional[Dict[str, Any]]:
    """Sample real 2-hop chains + real 1-hop edges, build GLOBAL bundled relation stores over random
    bipolar codes, PAD the codebook to v_target with real graph decoy nodes, return codebook + stores +
    per-trial specs. Returns None on shortage. GENERATOR GUARD asserts real-structure well-posedness."""
    syn_out = graph["syn_out"]; isa_out = graph["isa_out"]; isa_set = graph["isa_set"]
    all_nodes = graph["all_nodes"]

    # ---- HARD candidates: X -syn-> A -isa-> B with B NOT in isa[X] (single-shot must fail) ----
    syn_keys = list(syn_out.keys())
    rng.shuffle(syn_keys)
    hard: List[Tuple[str, str, str]] = []
    used_anchor: set = set()
    for x in syn_keys:
        if len(hard) >= n_hard:
            break
        if x in used_anchor:
            continue
        x_isa = isa_set.get(x, set())
        picked = None
        a_list = list(syn_out.get(x, []))
        rng.shuffle(a_list)
        for a in a_list:
            if a == x:
                continue
            b_list = list(isa_out.get(a, []))
            rng.shuffle(b_list)
            for b in b_list:
                if b == x or b == a or b in x_isa:
                    continue
                picked = (x, a, b)
                break
            if picked:
                break
        if picked:
            hard.append(picked)
            used_anchor.add(picked[0])
    if len(hard) < n_hard:
        print("[build] seed=%d V=%d SHORTAGE hard: got %d/%d" % (seed, v_target, len(hard), n_hard), flush=True)
        return None

    hard_anchor_set = {x for (x, _, _) in hard}

    # ---- EASY 1-hop edges: X -isa-> B, X disjoint from hard anchors ----
    isa_keys = list(isa_out.keys())
    rng.shuffle(isa_keys)
    easy: List[Tuple[str, str]] = []
    easy_anchor_set: set = set()
    for x in isa_keys:
        if len(easy) >= n_easy:
            break
        if x in hard_anchor_set or x in easy_anchor_set:
            continue
        b_list = [b for b in isa_out.get(x, []) if b != x]
        if not b_list:
            continue
        b = b_list[int(rng.integers(0, len(b_list)))]
        easy.append((x, b))
        easy_anchor_set.add(x)
    if len(easy) < n_easy:
        print("[build] seed=%d V=%d SHORTAGE easy: got %d/%d" % (seed, v_target, len(easy), n_easy), flush=True)
        return None

    # ---- distractor edges to fill each store to its absolute capacity M ----
    def sample_syn_distractors(need: int, exclude_pairs: set) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        keys = list(syn_out.keys()); guard = 0
        while len(out) < need and guard < need * 200 + 1000:
            guard += 1
            s = keys[int(rng.integers(0, len(keys)))]
            ts = syn_out[s]; t = ts[int(rng.integers(0, len(ts)))]
            if s == t or (s, t) in exclude_pairs:
                continue
            out.append((s, t)); exclude_pairs.add((s, t))
        return out

    def sample_isa_distractors(need: int, exclude_pairs: set) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        keys = list(isa_out.keys()); guard = 0
        while len(out) < need and guard < need * 200 + 1000:
            guard += 1
            s = keys[int(rng.integers(0, len(keys)))]
            if s in hard_anchor_set:                 # hard anchors must not be ISA-store keys
                continue
            ts = isa_out[s]; t = ts[int(rng.integers(0, len(ts)))]
            if s == t or (s, t) in exclude_pairs:
                continue
            out.append((s, t)); exclude_pairs.add((s, t))
        return out

    syn_edges = [(x, a) for (x, a, _) in hard]
    syn_excl = set(syn_edges)
    syn_edges += sample_syn_distractors(max(0, m_syn - len(syn_edges)), syn_excl)

    isa_edges = [(a, b) for (_, a, b) in hard] + [(x, b) for (x, b) in easy]
    isa_excl = set(isa_edges)
    isa_edges += sample_isa_distractors(max(0, m_isa - len(isa_edges)), isa_excl)

    # ---- collect the CORPUS nodes (participate in edges / trials) ----
    corpus_nodes: set = set()
    for (s, t) in syn_edges:
        corpus_nodes.add(s); corpus_nodes.add(t)
    for (s, t) in isa_edges:
        corpus_nodes.add(s); corpus_nodes.add(t)
    for (x, a, b) in hard:
        corpus_nodes.add(x); corpus_nodes.add(a); corpus_nodes.add(b)
    for (x, b) in easy:
        corpus_nodes.add(x); corpus_nodes.add(b)

    # ---- PAD the codebook to v_target with REAL graph decoy nodes (confusable cleanup candidates) ----
    node_list = sorted(corpus_nodes)
    n_corpus = len(node_list)
    if v_target < n_corpus:
        v_target = n_corpus                          # never shrink below the corpus itself
    decoy_pool = [nm for nm in all_nodes if nm not in corpus_nodes]
    need_decoy = v_target - n_corpus
    n_decoy_available = len(decoy_pool)
    if need_decoy > n_decoy_available:
        need_decoy = n_decoy_available               # graph-node-limited (logged)
    if need_decoy > 0:
        idx = rng.choice(n_decoy_available, size=need_decoy, replace=False)
        decoys = [decoy_pool[int(i)] for i in idx]
    else:
        decoys = []
    full_node_list = node_list + decoys
    node2id = {nm: i for i, nm in enumerate(full_node_list)}
    V = len(full_node_list)
    E = make_codebook(V, n_dim, rng)

    # ---- GENERATOR GUARD: verify REAL ingested structure, well-posed 2-hop chains, real codebook ----
    real_pool = set(all_nodes)
    for (x, a, b) in hard:
        assert x in real_pool and a in real_pool and b in real_pool, "hard chain node not a real graph node"
        assert a in syn_out.get(x, []), "hop1 X-syn->A not a real edge"
        assert b in isa_out.get(a, []), "hop2 A-isa->B not a real edge"
        assert b not in isa_set.get(x, set()), "HARD ill-posed: B is a direct ISA of X (single-shot could win)"
    for (x, b) in easy:
        assert b in isa_out.get(x, []), "easy X-isa->B not a real edge"
    assert all(nm in real_pool for nm in full_node_list), "codebook contains a non-real node"
    n_hard_distinct_anchors = len(hard_anchor_set)
    assert n_hard_distinct_anchors == len(hard), "hard anchors not distinct (would collide in SYN store)"

    # ---- build GLOBAL bundled relation stores ----
    SYN = np.zeros(n_dim, dtype=np.float32)
    for (s, t) in syn_edges:
        SYN += bind(E[node2id[s]], E[node2id[t]])
    ISA = np.zeros(n_dim, dtype=np.float32)
    for (s, t) in isa_edges:
        ISA += bind(E[node2id[s]], E[node2id[t]])

    # ---- per-trial query specs (mixed corpus) ----
    trials: List[Dict[str, Any]] = []
    for (x, a, b) in hard:
        rb = int(rng.integers(0, V))
        while rb == node2id[a]:
            rb = int(rng.integers(0, V))
        trials.append({"easy": False, "anchor_id": node2id[x], "bridge_id": node2id[a],
                       "ans_id": node2id[b], "rand_bridge_id": rb})
    for (x, b) in easy:
        rb = int(rng.integers(0, V))
        trials.append({"easy": True, "anchor_id": node2id[x], "bridge_id": -1,
                       "ans_id": node2id[b], "rand_bridge_id": rb})
    perm = rng.permutation(len(trials))
    trials = [trials[i] for i in perm]

    return {"E": E, "SYN": SYN, "ISA": ISA, "trials": trials, "V": V, "v_target": v_target,
            "n_corpus_nodes": n_corpus, "n_decoy_nodes": len(decoys),
            "n_syn_edges": len(syn_edges), "n_isa_edges": len(isa_edges),
            "n_hard_distinct_anchors": n_hard_distinct_anchors}


# ============================================================================
# BATCHED retrieve->gate->audit->requery over all trials of a corpus (loop semantics unchanged)
# ============================================================================
def compute_corpus(E: np.ndarray, SYN: np.ndarray, ISA: np.ndarray,
                   trials: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run the loop for ALL trials via stage-batched BLAS gemms. Returns per-trial arrays + roots.
    Sequential dependency preserved: hop-2 uses the hop-1 WM result (bridge_hat) resolved in the prior
    stage. Results are bit-identical to the per-trial certified loop; only the cleanup is vectorized."""
    n = len(trials)
    anchor_ids = np.array([t["anchor_id"] for t in trials], dtype=np.int64)
    rand_ids = np.array([t["rand_bridge_id"] for t in trials], dtype=np.int64)
    bridge_ids = np.array([t["bridge_id"] for t in trials], dtype=np.int64)
    easy = np.array([bool(t["easy"]) for t in trials])

    A_anchor = E[anchor_ids]                                  # (n, N)

    # hop-1: retrieve CN_SYNONYM bridge into WM
    bridge_hat_ids, margin1 = cleanup_batch(A_anchor * SYN, E)
    # single-shot: raw anchor into ISA (the gate's "why-signal")
    ansA_ids, marginA = cleanup_batch(A_anchor * ISA, E)
    go = marginA >= TAU_GATE
    # WM-mediated re-query: bind the WM active-slot content into ISA
    ansB_wm_ids, marginB = cleanup_batch(E[bridge_hat_ids] * ISA, E)
    # scramble control: random bridge into ISA
    ansB_scr_ids, _ = cleanup_batch(E[rand_ids] * ISA, E)
    # oracle: TRUE bridge into ISA (hard); easy oracle undefined -> single shot
    safe_bridge = np.where(bridge_ids >= 0, bridge_ids, anchor_ids)
    ansOracle_hard, _ = cleanup_batch(E[safe_bridge] * ISA, E)
    ansOracle_ids = np.where(bridge_ids >= 0, ansOracle_hard, ansA_ids)

    ans_arm = {
        "ARM_A_SINGLE_SHOT": ansA_ids,
        "ARM_B_WM_REQUERY": np.where(go, ansA_ids, ansB_wm_ids),
        "ARM_B_SCRAMBLE": np.where(go, ansA_ids, ansB_scr_ids),
        "ARM_ALWAYS_REQUERY": ansB_wm_ids,
        "ARM_ORACLE_BRIDGE": ansOracle_ids,
    }

    # per-trial Merkle steps + root (scalar; cheap)
    roots: List[bytes] = []
    steps_all: List[List[str]] = []
    for i in range(n):
        steps = [
            "query(anchor=%d,easy=%d)" % (anchor_ids[i], int(easy[i])),
            "hop1_retrieve(bridge=%d,margin1=%.4f)" % (bridge_hat_ids[i], margin1[i]),
            "gate(marginA=%.4f,tau=%.4f,decision=%s,ansA=%d)"
            % (marginA[i], TAU_GATE, "GO" if go[i] else "NOGO", ansA_ids[i]),
            "hop2_requery(bridge_used=%d,ansB=%d,marginB=%.4f)" % (bridge_hat_ids[i], ansB_wm_ids[i], marginB[i]),
            "commit(answer=%d)" % ans_arm["ARM_B_WM_REQUERY"][i],
        ]
        steps_all.append(steps)
        roots.append(merkle_root(steps))

    return {"ans_arm": ans_arm, "bridge_hat_ids": bridge_hat_ids, "ansB_wm_ids": ansB_wm_ids,
            "ansB_scr_ids": ansB_scr_ids, "margin1": margin1, "marginA": marginA, "marginB": marginB,
            "go": go, "steps_all": steps_all, "roots": roots, "easy": easy, "bridge_ids": bridge_ids}


def binom_two_sided_p(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial p-value for k successes in n trials (sign test)."""
    if n == 0:
        return 1.0
    from math import comb
    probs = [comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(n + 1)]
    obs = probs[k]
    return float(min(1.0, sum(pr for pr in probs if pr <= obs + 1e-12)))


# ============================================================================
# per-(scale,seed) runner
# ============================================================================
def run_unit(seed: int, v_target: int, n_dim: int, graph: Dict[str, Any], out_dir: Path
             ) -> Optional[Dict[str, Any]]:
    rng = np.random.default_rng(seed * 1000003 + v_target)   # seed decorrelated per scale
    corpus = build_corpus(graph, seed, rng, N_HARD, N_EASY, M_SYN, M_ISA, n_dim, v_target)
    if corpus is None:
        return None
    E = corpus["E"]; SYN = corpus["SYN"]; ISA = corpus["ISA"]; trials = corpus["trials"]
    n = len(trials)
    ans_id = np.array([t["ans_id"] for t in trials], dtype=np.int64)
    easy = np.array([bool(t["easy"]) for t in trials])

    r1 = compute_corpus(E, SYN, ISA, trials)
    r2 = compute_corpus(E, SYN, ISA, trials)                  # deterministic replay (full recompute)

    # deterministic replay: every arm answer array AND every Merkle root reproduce exactly
    det_arms = all(np.array_equal(r1["ans_arm"][a], r2["ans_arm"][a]) for a in ARMS)
    det_roots = all(r1["roots"][i] == r2["roots"][i] for i in range(n))
    deterministic_replay = 1.0 if (det_arms and det_roots) else 0.0

    # merkle verify (recompute root from recorded steps) + tamper-detect (mutate commit step)
    verify_ok = np.zeros(n, dtype=bool)
    tamper_ok = np.zeros(n, dtype=bool)
    for i in range(n):
        verify_ok[i] = merkle_verify(r1["steps_all"][i], r1["roots"][i])
        tampered = list(r1["steps_all"][i])
        tampered[4] = "commit(answer=%d)" % (r1["ans_arm"]["ARM_B_WM_REQUERY"][i] + 1)
        tamper_ok[i] = (not merkle_verify(tampered, r1["roots"][i]))

    per_arm_correct = {a: (r1["ans_arm"][a] == ans_id) for a in ARMS}
    accs = {a: float(per_arm_correct[a].mean()) for a in ARMS}
    accA = accs["ARM_A_SINGLE_SHOT"]; accB = accs["ARM_B_WM_REQUERY"]
    accScr = accs["ARM_B_SCRAMBLE"]; accAlways = accs["ARM_ALWAYS_REQUERY"]

    hard = ~easy
    accA_hard = float(per_arm_correct["ARM_A_SINGLE_SHOT"][hard].mean()) if hard.any() else 0.0
    accOracle = float(per_arm_correct["ARM_ORACLE_BRIDGE"][hard].mean()) if hard.any() else 0.0
    hop1_acc = float((r1["bridge_hat_ids"][hard] == r1["bridge_ids"][hard]).mean()) if hard.any() else 0.0

    # routing accuracy: easy correct iff GO; hard correct iff NOGO (re-query)
    route_correct = np.where(easy, r1["go"], ~r1["go"])
    gate_routing_acc = float(route_correct.mean())
    margins_easy = r1["marginA"][easy]
    margins_hard = r1["marginA"][hard]
    gate_sep = (float(margins_easy.mean()) - float(margins_hard.mean())) if (easy.any() and hard.any()) else 0.0

    # causal hand-edit: on HARD + ARM_B-correct trials, swap bridge->distractor (== scramble recompute)
    ce_mask = hard & per_arm_correct["ARM_B_WM_REQUERY"]
    if ce_mask.any():
        causal_flip = (r1["ansB_scr_ids"][ce_mask] != r1["ansB_wm_ids"][ce_mask])
        causal_flip_rate = float(causal_flip.mean())
        # tamper must fire on the edited chain (root recompute differs); demonstrate on the ce trials
        ct_ok = True
        ce_idx = np.where(ce_mask)[0]
        for i in ce_idx:
            edited = list(r1["steps_all"][i])
            edited[1] = "hop1_retrieve(bridge=%d,margin1=%.4f)" % (r1["bridge_ids"][i], r1["margin1"][i])
            edited[3] = "hop2_requery(bridge_used=%d,ansB=%d,marginB=%.4f)" % (
                r1["bridge_ids"][i], r1["ansB_scr_ids"][i], r1["marginB"][i])
            if merkle_verify(edited, r1["roots"][i]):
                ct_ok = False
                break
        causal_tamper_rate = 1.0 if ct_ok else 0.0
        n_causal = int(ce_mask.sum())
    else:
        causal_flip_rate = 0.0; causal_tamper_rate = 0.0; n_causal = 0

    # paired sign test B vs A
    b = per_arm_correct["ARM_B_WM_REQUERY"]; a_ = per_arm_correct["ARM_A_SINGLE_SHOT"]
    n_b_only = int((b & (~a_)).sum()); n_a_only = int((a_ & (~b)).sum())
    n_disc = n_b_only + n_a_only
    sign_p = binom_two_sided_p(n_b_only, n_disc, 0.5) if n_disc > 0 else 1.0

    arm_digests = {a2: hashlib.sha256(r1["ans_arm"][a2].tobytes()).hexdigest()[:16] for a2 in ARMS}
    core_arms = ["ARM_A_SINGLE_SHOT", "ARM_B_WM_REQUERY", "ARM_B_SCRAMBLE", "ARM_ALWAYS_REQUERY"]
    arms_differ = (len({arm_digests[a2] for a2 in core_arms}) == len(core_arms))

    rec = {
        "seed": int(seed), "v_target": int(v_target), "N": int(n_dim), "V": corpus["V"],
        "n_corpus_nodes": corpus["n_corpus_nodes"], "n_decoy_nodes": corpus["n_decoy_nodes"],
        "n_trials": n, "n_hard": int(hard.sum()), "n_easy": int(easy.sum()),
        "n_syn_edges": corpus["n_syn_edges"], "n_isa_edges": corpus["n_isa_edges"],
        "n_hard_distinct_anchors": corpus["n_hard_distinct_anchors"],
        "run_mode": RUN_MODE, "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "frac_easy": FRAC_EASY, "tau_gate": TAU_GATE,
        "accs": accs, "accA": accA, "accB": accB, "accScramble": accScr, "accAlways": accAlways,
        "accOracle": accOracle, "accA_hard": accA_hard,
        "resolve_lift": float(accB - accA), "gate_route_margin": float(accB - accAlways),
        "scramble_gap": float(accB - accScr), "gate_separation": float(gate_sep),
        "gate_routing_acc": gate_routing_acc, "hop1_retrieve_acc": hop1_acc,
        "deterministic_replay": deterministic_replay,
        "merkle_verify": float(verify_ok.mean()), "tamper_detect": float(tamper_ok.mean()),
        "causal_edit_flip": causal_flip_rate, "causal_edit_tamper": causal_tamper_rate,
        "n_causal_trials": n_causal, "sign_p": float(sign_p), "n_b_only": n_b_only, "n_a_only": n_a_only,
        "requery_count": int((~r1["go"]).sum()),
        "margin_easy_mean": float(margins_easy.mean()) if easy.any() else 0.0,
        "margin_hard_mean": float(margins_hard.mean()) if hard.any() else 0.0,
        "arm_digests": arm_digests, "arms_differ": bool(arms_differ),
        "arms_differ_exempted": [["ARM_ALWAYS_REQUERY", "ARM_ORACLE_BRIDGE"]],
    }
    print("[V=%d N=%d seed=%d] Vcode=%d(decoy=%d) accA=%.3f accB=%.3f accAlways=%.3f accScr=%.3f "
          "accOracle=%.3f accA_hard=%.3f | resolve=%.3f route=%.3f scramble=%.3f gate_sep=%.3f "
          "routing=%.3f hop1=%.3f | det=%.1f verify=%.3f tamper=%.3f causal_flip=%.3f(n=%d) p=%.4f"
          % (v_target, n_dim, seed, corpus["V"], corpus["n_decoy_nodes"], accA, accB, accAlways, accScr,
             accOracle, accA_hard, rec["resolve_lift"], rec["gate_route_margin"], rec["scramble_gap"],
             rec["gate_separation"], rec["gate_routing_acc"], rec["hop1_retrieve_acc"],
             rec["deterministic_replay"], rec["merkle_verify"], rec["tamper_detect"],
             rec["causal_edit_flip"], rec["n_causal_trials"], rec["sign_p"]), flush=True)
    return rec


# ============================================================================
# per-scale aggregation
# ============================================================================
def scale_means(recs: List[Dict[str, Any]]) -> Dict[str, Any]:
    fields = ["accA", "accB", "accScramble", "accAlways", "accOracle", "accA_hard", "resolve_lift",
              "gate_route_margin", "scramble_gap", "gate_separation", "gate_routing_acc",
              "hop1_retrieve_acc", "deterministic_replay", "merkle_verify", "tamper_detect",
              "causal_edit_flip", "causal_edit_tamper", "margin_easy_mean", "margin_hard_mean"]
    m = {f: float(np.mean([float(r[f]) for r in recs])) for f in fields}
    n_b_only = sum(int(r["n_b_only"]) for r in recs)
    n_a_only = sum(int(r["n_a_only"]) for r in recs)
    n_disc = n_b_only + n_a_only
    m["sign_p"] = binom_two_sided_p(n_b_only, n_disc, 0.5) if n_disc > 0 else 1.0
    m["arms_differ"] = all(bool(r["arms_differ"]) for r in recs)
    m["n_seeds"] = len(recs)
    m["V"] = int(recs[0]["V"]); m["v_target"] = int(recs[0]["v_target"]); m["N"] = int(recs[0]["N"])
    m["n_decoy_nodes"] = int(recs[0]["n_decoy_nodes"])
    return m


# ============================================================================
# selftest
# ============================================================================
def _selftest() -> None:
    """Formula self-tests: (1) merkle chains + tamper; (2) bind self-inverse; (3) batched cleanup matches a
    scalar reference; (4) the weak-first regime fires on a tiny SYNTHETIC graph (single-shot fails HARD, WM
    re-query resolves, causal edit flips) via the BATCHED path."""
    r = merkle_root(["a", "b", "c"])
    assert merkle_verify(["a", "b", "c"], r), "merkle verify"
    assert not merkle_verify(["a", "b", "X"], r), "tamper detected"
    assert merkle_root(["a"]) != h(b"genesis"), "merkle chains beyond genesis"
    rng = np.random.default_rng(0)
    E = make_codebook(16, 256, rng)
    x = E[3]; k = E[5]
    assert np.array_equal(bind(k, bind(k, x)), x), "bind self-inverse"

    # batched cleanup matches scalar argmax + margin
    P = np.stack([E[3] * E[7], E[1] * E[2]])
    ids, margs = cleanup_batch(P, E)
    for row in range(2):
        scores = E @ P[row]
        top2 = np.argpartition(scores, -2)[-2:]
        a2, b2 = top2[np.argsort(scores[top2])[::-1]]
        assert ids[row] == a2, "batched cleanup id matches scalar"
        assert abs(margs[row] - (scores[a2] - scores[b2]) / E.shape[1]) < 1e-5, "batched margin matches scalar"

    st_nh, st_ne, st_ms, st_mi, st_nd = 10, 10, 20, 24, 1024
    g = make_synthetic_graph(np.random.default_rng(1), st_nh, st_ne, st_ms, st_mi)
    corpus = build_corpus(g, 2, np.random.default_rng(2), st_nh, st_ne, st_ms, st_mi, st_nd, 80)
    assert corpus is not None, "synthetic corpus built"
    E2 = corpus["E"]; SYN2 = corpus["SYN"]; ISA2 = corpus["ISA"]; trials = corpus["trials"]
    r1 = compute_corpus(E2, SYN2, ISA2, trials)
    ans_id = np.array([t["ans_id"] for t in trials])
    easy = np.array([bool(t["easy"]) for t in trials])
    hard = ~easy
    nb_ok = int((r1["ans_arm"]["ARM_B_WM_REQUERY"][hard] == ans_id[hard]).sum())
    a_hard_ok = int((r1["ans_arm"]["ARM_A_SINGLE_SHOT"][hard] == ans_id[hard]).sum())
    hop1_ok = int((r1["bridge_hat_ids"][hard] == r1["bridge_ids"][hard]).sum())
    nh = int(hard.sum())
    assert nb_ok >= 0.8 * nh, "WM re-query resolves most HARD (%d/%d)" % (nb_ok, nh)
    assert a_hard_ok <= 0.2 * nh, "single-shot fails most HARD (discriminator fires) (%d/%d)" % (a_hard_ok, nh)
    assert hop1_ok >= 0.7 * nh, "hop1 retrieves bridge (%d/%d)" % (hop1_ok, nh)
    ce_mask = hard & (r1["ans_arm"]["ARM_B_WM_REQUERY"] == ans_id)
    if ce_mask.any():
        flips = (r1["ansB_scr_ids"][ce_mask] != r1["ansB_wm_ids"][ce_mask])
        assert flips.mean() >= 0.8, "causal edit flips downstream (%.2f)" % flips.mean()
    ea_mask = easy & (r1["ans_arm"]["ARM_A_SINGLE_SHOT"] == ans_id) & r1["go"]
    assert int(ea_mask.sum()) >= 0.8 * int(easy.sum()), "EASY single-shot resolves with GO"
    print("[selftest] PASS: SCALE conceptnet multi-hop glass-box loop "
          "(merkle+tamper, bind-inverse, batched==scalar cleanup, weak-first fires on synthetic graph)",
          flush=True)


# ============================================================================
# verdict (per-scale + top-scale headline + all-scale integrity)
# ============================================================================
def aggregate_and_verdict(per_scale: Dict[int, Dict[str, Any]], completed_units: int
                          ) -> Tuple[Dict[str, Any], List[Any]]:
    if not per_scale:
        return {"verdict": "UNKNOWN", "verdict_msg": "no completed units",
                "summary": "no completed units"}, []

    scale_keys = sorted(per_scale.keys())               # ascending V_target
    top = per_scale[scale_keys[-1]]
    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    def all_scales(pred) -> bool:
        return all(pred(per_scale[k]) for k in scale_keys)

    audit_ok = all_scales(lambda m: m["deterministic_replay"] >= 0.999 and m["merkle_verify"] >= 0.999
                          and m["tamper_detect"] >= 0.999)
    retrieval_ok = all_scales(lambda m: m["accOracle"] >= HP_ORACLE_BRIDGE_MIN
                              and m["hop1_retrieve_acc"] >= HP_HOP1_RETRIEVE_MIN)
    discriminator_fires = all_scales(lambda m: m["accA_hard"] <= HP_DISCRIM_ACCA_HARD_MAX)
    telemetry_ok = all_scales(lambda m: m["scramble_gap"] >= TAUT_SCRAMBLE_FLOOR
                              and m["gate_separation"] >= TAUT_GATE_SEP_FLOOR)
    non_ceiling = all_scales(lambda m: m["accB"] <= HP_NONCEILING_MAX)
    resolve_holds_all = all_scales(lambda m: m["resolve_lift"] >= HP_RESOLVE_LIFT_MIN)
    any_hardfail_resolve = not all_scales(lambda m: m["resolve_lift"] >= HF_RESOLVE_LIFT_CEIL)

    # per-scale one-line table for verdict_msg
    tbl = " || ".join(
        "V=%d(N=%d,decoy=%d): accB=%.3f resolve=%.3f accA_hard=%.3f oracle=%.3f hop1=%.3f scramble=%.3f "
        "gate_sep=%.3f route=%.3f causal=%.3f tamper=%.3f det=%.1f"
        % (per_scale[k]["v_target"], per_scale[k]["N"], per_scale[k]["n_decoy_nodes"], per_scale[k]["accB"],
           per_scale[k]["resolve_lift"], per_scale[k]["accA_hard"], per_scale[k]["accOracle"],
           per_scale[k]["hop1_retrieve_acc"], per_scale[k]["scramble_gap"], per_scale[k]["gate_separation"],
           per_scale[k]["gate_routing_acc"], per_scale[k]["causal_edit_flip"], per_scale[k]["tamper_detect"],
           per_scale[k]["deterministic_replay"])
        for k in scale_keys)
    s = "[per-scale] " + tbl + (" (seeds/scale=%d)" % top["n_seeds"])

    top_headline_ok = (top["resolve_lift"] >= HP_RESOLVE_LIFT_MIN
                       and top["gate_route_margin"] >= HP_GATE_ROUTE_MARGIN
                       and top["sign_p"] < SIGN_P_MAX and top["gate_separation"] >= HP_GATE_SEP_MIN
                       and top["gate_routing_acc"] >= HP_GATE_ROUTING_ACC_MIN
                       and top["scramble_gap"] >= HP_SCRAMBLE_GAP_MIN
                       and top["causal_edit_flip"] >= HP_CAUSAL_FLIP_MIN and top["arms_differ"])

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = "HARD_FAIL: completed %d < expected %d units. " % (completed_units, EXPECTED_N_UNITS) + s
    elif not audit_ok:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL: audit not sound at some scale (det/merkle/tamper < 1.0 on real data). " + s
    elif any_hardfail_resolve:
        verdict = "HARD_FAIL"
        vmsg = ("HARD_FAIL: resolve_lift < %.2f at some scale -- the WM re-query loop adds nothing over a "
                "single shot on real chains at that scale. " % HF_RESOLVE_LIFT_CEIL) + s
    elif not discriminator_fires:
        verdict = "INCONCLUSIVE_DISCRIMINATOR_DEAD"
        vmsg = ("INCONCLUSIVE_DISCRIMINATOR_DEAD: accA_hard > %.2f at some scale -- single-shot already solves "
                "the multi-hop at that V (not a genuine 2-hop test there). " % HP_DISCRIM_ACCA_HARD_MAX) + s
    elif not retrieval_ok:
        verdict = "SCALE_WALL"
        vmsg = ("SCALE_WALL: oracle_bridge < %.2f or hop1 < %.2f at some scale -- the single-cue retrieval "
                "primitive degraded with entity count (cleanup crosstalk / capacity wall). This NAMES the "
                "wall: single-cue cleanup fidelity vs codebook size. Loop holds at small V, degrades at scale. "
                % (HP_ORACLE_BRIDGE_MIN, HP_HOP1_RETRIEVE_MIN)) + s
    elif not telemetry_ok:
        verdict = "INCONCLUSIVE_TAUTOLOGICAL_METRIC"
        vmsg = ("INCONCLUSIVE_TAUTOLOGICAL_METRIC: scramble_gap < %.2f or gate_sep < %.2f at some scale; "
                "resolution not attributable to correct WM binding / self-audit not telemetry-sensitive. "
                % (TAUT_SCRAMBLE_FLOOR, TAUT_GATE_SEP_FLOOR)) + s
    elif not non_ceiling:
        verdict = "SATURATION_TOO_EASY"
        vmsg = ("SATURATION_TOO_EASY: accB > %.2f at some scale -- the regime is ceiling-saturated there; "
                "raise store capacity M before certifying generalization. NOT a HARD_PASS. "
                % HP_NONCEILING_MAX) + s
    elif not resolve_holds_all:
        verdict = "SCALE_WALL"
        vmsg = ("SCALE_WALL: audit + retrieval + discriminator + telemetry all hold at every scale, but "
                "resolve_lift drops below %.2f at some larger V while holding at small V -- the reasoning "
                "LOOP degrades with entity count (hop-depth compounding x codebook crosstalk). HONEST wall. "
                % HP_RESOLVE_LIFT_MIN) + s
    elif top_headline_ok:
        verdict = "HARD_PASS"
        vmsg = ("HARD_PASS: glass-box multi-hop reasoning + self-audit HOLD at scale. On REAL ConceptNet "
                "2-hop chains the gated WM re-query resolves what a single shot cannot at EVERY entity count "
                "up to V=%d (top-scale resolve_lift=%.3f, accB=%.3f NON-CEILING, accA_hard=%.3f), beats "
                "always-requery by %.3f (p=%.4f), the self-audit is telemetry-sensitive (gate_sep=%.3f, "
                "scramble_gap=%.3f) and the glass-box hand-edit flips the downstream recompute "
                "(causal_flip=%.3f) while the tamper flag fires (tamper=%.3f) -- all at the largest scale. "
                "Deterministic replay + Merkle verify == 1.0 at every scale. Directly advances the deep prize: "
                "substrate reasoning over ingested knowledge, glass-box + self-auditing, AT SCALE. "
                % (top["v_target"], top["resolve_lift"], top["accB"], top["accA_hard"],
                   top["gate_route_margin"], top["sign_p"], top["gate_separation"], top["scramble_gap"],
                   top["causal_edit_flip"], top["tamper_detect"])) + s
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("MIDDLE_BAND: integrity (audit/retrieval/discriminator/telemetry/non-ceiling) holds at every "
                "scale and resolve_lift holds at every scale, but a TOP-scale headline gate missed "
                "(resolve_lift=%.3f route_margin=%.3f gate_sep=%.3f scramble_gap=%.3f causal_flip=%.3f "
                "routing=%.3f p=%.4f arms_differ=%s). "
                % (top["resolve_lift"], top["gate_route_margin"], top["gate_separation"], top["scramble_gap"],
                   top["causal_edit_flip"], top["gate_routing_acc"], top["sign_p"], top["arms_differ"])) + s

    gate_claims = [
        record_gate("top_resolve_lift", top["resolve_lift"], HP_RESOLVE_LIFT_MIN, ">=", "accB-accA at top scale"),
        record_gate("top_accB_non_ceiling", top["accB"], HP_NONCEILING_MAX, "<=", "graded difficulty at top scale"),
        record_gate("top_accA_hard_discriminator", top["accA_hard"], HP_DISCRIM_ACCA_HARD_MAX, "<="),
        record_gate("top_gate_route_margin", top["gate_route_margin"], HP_GATE_ROUTE_MARGIN, ">="),
        record_gate("top_gate_separation", top["gate_separation"], HP_GATE_SEP_MIN, ">="),
        record_gate("top_gate_routing_acc", top["gate_routing_acc"], HP_GATE_ROUTING_ACC_MIN, ">="),
        record_gate("top_scramble_gap", top["scramble_gap"], HP_SCRAMBLE_GAP_MIN, ">="),
        record_gate("top_causal_edit_flip", top["causal_edit_flip"], HP_CAUSAL_FLIP_MIN, ">="),
        record_gate("top_sign_p", top["sign_p"], SIGN_P_MAX, "<", "paired B vs A at top scale"),
        record_gate("allscale_oracle_min", min(per_scale[k]["accOracle"] for k in scale_keys),
                    HP_ORACLE_BRIDGE_MIN, ">=", "worst-scale positive control"),
        record_gate("allscale_hop1_min", min(per_scale[k]["hop1_retrieve_acc"] for k in scale_keys),
                    HP_HOP1_RETRIEVE_MIN, ">=", "worst-scale WM retrieval"),
        record_gate("allscale_resolve_min", min(per_scale[k]["resolve_lift"] for k in scale_keys),
                    HP_RESOLVE_LIFT_MIN, ">=", "worst-scale resolve_lift"),
        record_gate("allscale_deterministic_replay", min(per_scale[k]["deterministic_replay"] for k in scale_keys),
                    0.999, ">="),
        record_gate("allscale_tamper_detect", min(per_scale[k]["tamper_detect"] for k in scale_keys),
                    0.999, ">="),
    ]
    summary = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg[:300], "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "n_units": completed_units, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": cardinality_ok,
        "scales": [per_scale[k]["v_target"] for k in scale_keys],
        "per_scale": {str(per_scale[k]["v_target"]): per_scale[k] for k in scale_keys},
        "top_scale_v": top["v_target"], "arms_differ": bool(top["arms_differ"]),
        "elapsed_s": round(time.time() - _T0, 2),
    }
    return summary, gate_claims


# ============================================================================
# main
# ============================================================================
def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print("[config] %s" % CONFIG_VERSION, flush=True)

    graph = (load_cn_graph(RELATIONS_PATH) if USE_REAL_GRAPH
             else make_synthetic_graph(np.random.default_rng(0), N_HARD, N_EASY, M_SYN, M_ISA))

    # per-(scale,seed) unit keys; resume-safe (PROT-021)
    unit_keys = ["V%d_seed%d" % (v, sd) for (v, _n) in SCALES for sd in SEEDS]
    done, remaining = resumable_seeds(unit_keys, out_dir)
    print("[resume] %d/%d units already complete; running %d" % (len(done), len(unit_keys), len(remaining)),
          flush=True)

    key2spec: Dict[str, Tuple[int, int, int]] = {}
    for (v, n) in SCALES:
        for sd in SEEDS:
            key2spec["V%d_seed%d" % (v, sd)] = (v, n, sd)

    total = len(unit_keys)
    for ui, key in enumerate(unit_keys):
        if key in set(done):
            continue
        v, n, sd = key2spec[key]
        fatal = None
        try:
            rec = run_unit(sd, v, n, graph, out_dir)
        except Exception as e:                                # per-unit failure-class instrumentation
            fatal = "%s: %s" % (type(e).__name__, str(e)[:300])
            print("[unit ERROR] key=%s %s" % (key, fatal), file=sys.stderr, flush=True)
            rec = None
        if rec is None:
            payload = {"unit_key": key, "v_target": v, "N": n, "seed": sd, "fatal": fatal or "SHORTAGE"}
        else:
            payload = rec
            payload["unit_key"] = key
        write_partial_key(out_dir, key, payload)
        _heartbeat(out_dir, ui + 1, total, "unit=%s done" % key)

    # aggregate all valid partials into per-scale groups
    parts = aggregate_partials(out_dir, unit_keys)
    per_scale_recs: Dict[int, List[Dict[str, Any]]] = {}
    completed_units = 0
    for key, payload in parts.items():
        if payload.get("fatal") is not None or "accB" not in payload:
            continue
        completed_units += 1
        v = int(payload["v_target"])
        per_scale_recs.setdefault(v, []).append(payload)
    per_scale = {v: scale_means(recs) for v, recs in per_scale_recs.items() if recs}

    # smoke gate: discriminator MUST fire at EVERY scale (must-fail control fails at THAT V)
    if RUN_MODE in ("smoke", "selftest"):
        for v in sorted(per_scale.keys()):
            m = per_scale[v]
            assert_discriminator_fires(
                control_passed_headline_gate=(m["accA_hard"] > HP_DISCRIM_ACCA_HARD_MAX),
                control_name="ARM_A_single_shot@V%d" % v,
                headline_name="multihop_resolve@V%d" % v, run_mode=RUN_MODE,
                extra="accA_hard=%.3f must be <= %.2f at V=%d" % (m["accA_hard"], HP_DISCRIM_ACCA_HARD_MAX, v))
            assert m["accOracle"] >= HP_ORACLE_BRIDGE_MIN, (
                "SMOKE oracle positive control below floor at V=%d: %.3f < %.2f (single-cue capacity wall; "
                "raise N)" % (v, m["accOracle"], HP_ORACLE_BRIDGE_MIN))
            assert m["scramble_gap"] >= HP_SCRAMBLE_GAP_MIN, (
                "SMOKE scramble did not collapse at V=%d: gap=%.3f < %.2f (resolution may be tautological)"
                % (v, m["scramble_gap"], HP_SCRAMBLE_GAP_MIN))
        print("[smoke-gate] discriminator fires + oracle clears + scramble collapses at ALL scales: %s"
              % sorted(per_scale.keys()), flush=True)

    summary, gate_claims = aggregate_and_verdict(per_scale, completed_units)
    print("\n[VERDICT] " + summary["verdict_msg"], flush=True)
    all_recs = [p for p in parts.values() if "accB" in p]
    write_metrics(out_dir, summary, all_recs, gate_claims=gate_claims)
    print("[metrics] written -> %s" % (out_dir / "metrics.json"), flush=True)


# run formula self-tests at import (fast) then dispatch
_selftest()
if SELF_TEST_MODE:
    sys.exit(0)

if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out_dir_for_crash, e)
        raise
