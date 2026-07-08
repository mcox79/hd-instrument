"""glass_box_micro_loop_conceptnet_multihop_v1 -- the certified glass-box reasoning micro-loop,
extended from its clean engineered toy regime to REAL ingested ConceptNet knowledge.

WHAT THIS IS (forward-integration cell; CPU/numpy only; does NOT touch GPU or the encoder):
  Takes the CG-certified retrieve->gate(self-audit)->WM-requery->commit loop with per-hop Merkle audit
  (exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1, commit ba552930a) and points it at genuine
  MULTI-HOP relational queries over the real ConceptNet word-graph
  (data/substrate_index/concept/relations.jsonl -- 189,654 edges over 141,511 nodes; densified, median
  degree 6). The reasoning task: resolve B given a real 2-hop chain X -CN_SYNONYM-> A -IS_A-> B (69,292
  such chains exist in the graph). The bridge A is retrieved into working memory, re-bound into the IS_A
  store, and the answer B committed -- every hop logged + Merkle-chained + hand-editable.

  WHY THIS IS A NON-CEILING GENERALIZATION TEST (not a repeat of the toy ceiling):
  The certified base cell ran a fully-engineered synthetic corpus where every (key,val) pair was drawn
  from independent random ids, so accB saturated at ~1.0 (ceiling). That proved "the mechanism works on
  a toy," NOT "multi-hop reasoning in the wild." Here the difficulty is GRADED by REAL graph structure:
    - real node identities carry random bipolar codes (semantics decoupled from store-codes per
      reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08),
    - the SYN and IS_A stores are GLOBAL bundles of real sampled edges (real hubs / real branching /
      real co-typed distractors, not disjoint synthetic pairs), so per-hop retrieval is < 1.0, and
    - the answer compounds TWO real hops (accB ~ hop1 x hop2), landing accB genuinely below the 0.95
      ceiling. accB > 0.95 is treated as SATURATION_TOO_EASY (raise difficulty), NOT a HARD_PASS.
  This measures generalization of the loop to ingested knowledge, not a re-run of the toy.

  Brain grounding (notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md):
    - PFC->hippocampus retrieval-in-service-of-inference: the anchor cue reaches a CA3 attractor; the
      arbitration/match-mismatch margin is the "stop vs re-query" evaluator (thread 1).
    - Working memory holds the retrieved bridge (active slot) and it is re-bound into the second store to
      bias the hop-2 completion (thread 2 active-slot; thread 4 offline re-completion over stored weights).
    - Cortico-BG-thalamic Go/NoGo value-gate decides WHETHER to commit the single shot or re-query
      (thread 3): high arbitration margin => Go (commit); low margin => NoGo (WM-mediated re-query).

  Composed certified parts (REUSED at the mechanism level; the GPU cells are NOT re-run):
    (A) Merkle audit-replay -- exp_reasoning_chain_replay_v1 (HARD_PASS): deterministic replay + per-step
        Merkle commitment + tamper-detect helpers TRANSCRIBED VERBATIM (that cell runs _selftest at import).
    (B) attention-routing arbitration gate -- exp_substrate_gen_lm_combinedgate_recency_content_v8
        (CHAIN_GRADE): the arbitration MARGIN (top1-top2) is the gate's "why-signal".
    (C) basal-ganglia value-gate Go/NoGo -- exp_pfc_bg_composed_attention_value_gate_v1: margin-threshold
        accept/re-query decision.

THE FALSIFIABLE REGIME (weak-first, on REAL chains; "B beats A" is NOT tautological):
  A per-seed corpus MIXES two trial types the loop cannot tell apart a priori:
    EASY  (frac_easy): a real 1-hop edge X -IS_A-> B; X is a DIRECT key in the IS_A store, so a SINGLE shot
          (unbind the anchor from the IS_A store) resolves it with HIGH arbitration margin.
    HARD  (1-frac_easy): a real 2-hop chain X -CN_SYNONYM-> A -IS_A-> B; B is keyed by the BRIDGE A, NOT by
          X, and X has NO IS_A edge in the store, so a single shot from X lands on NOISE (LOW margin, wrong).
          Only a WM-mediated re-query resolves it: retrieve A from the CN_SYNONYM store (WM active-slot),
          BIND it into the IS_A store, unbind B. Two hops.
  Because the two types are mixed, the arbitration-margin gate is LOAD-BEARING in BOTH directions:
    - ARM_A_SINGLE_SHOT (always commit shot)      resolves EASY, fails HARD   -> acc ~ frac_easy
    - ARM_ALWAYS_REQUERY (always re-query)         resolves HARD, BREAKS EASY  -> acc ~ (1-frac_easy)*hop-quality
    - ARM_B_WM_REQUERY (gated: margin>=tau => Go)  resolves BOTH               -> acc ~ non-ceiling (real hops)
  If a single shot could solve HARD trials, ARM_A would already win and resolve_lift ~ 0 (HARD_FAIL). This
  is MEASURED (discriminator-fires gate: accA_on_hard must be near chance), not assumed.

TELEMETRY-SENSITIVITY (MANDATORY guard):
  ARM_B_SCRAMBLE re-queries with a RANDOM bridge code instead of the WM active-slot content. If the
  "resolution" were an artifact of merely re-querying, SCRAMBLE would resolve too; it must collapse toward
  ARM_A (scramble_gap = accB - accB_scramble >= 0.25). scramble_gap < 0.10 => INCONCLUSIVE_TAUTOLOGICAL.
  The gate margin must ALSO separate EASY from HARD (gate_separation >= 0.10).

THE GLASS-BOX HAND-EDIT DEMONSTRATION (on REAL chains):
    (1) TAMPER-DETECT: hand-edit ONE logged retrieval step; recompute the Merkle root; it mismatches the
        committed root => the tamper flag fires (must be 100%).
    (2) CAUSAL-EDIT (monitor-not-control): on a HARD trial the loop got CORRECT, hand-edit the logged bridge
        from the true CN_SYNONYM bridge A to a DISTRACTOR node; RE-RUN the downstream hop-2 recompute => the
        committed answer flips (correct->wrong). Proves the logged step is load-bearing, not decorative.

CONTRACT (pre-registered; preregs/2026-07-08_glass_box_micro_loop_conceptnet_multihop_v1.md):
  HARD_PASS  : resolve_lift(accB-accA) >= 0.25 AND accB-accALWAYS >= 0.15 AND paired sign-test p < 0.05
               AND accB <= 0.95 (NON-CEILING: genuine real-graph difficulty) AND accA_hard <= 0.15
               (discriminator fires: single-shot fails the multi-hop) AND gate_separation >= 0.10 AND
               gate_routing_acc >= 0.85 AND scramble_gap >= 0.25 AND oracle_bridge_acc >= 0.85 AND
               hop1_retrieve_acc >= 0.80 AND deterministic_replay == 1.0 AND merkle_verify == 1.0 AND
               tamper_detect == 1.0 AND causal_edit_flip >= 0.80 AND arms_differ.
  SATURATION_TOO_EASY : accB > 0.95 (regime not graded hard enough -> raise store capacity M; NOT a HARD_PASS).
  MIDDLE_BAND: resolve_lift in [0.10,0.25) OR gate_separation in [0.05,0.10) OR causal_edit_flip in [0.50,0.80)
               OR accB_route_margin in [0.05,0.15).
  HARD_FAIL  : resolve_lift < 0.10 (the loop adds nothing over single-shot on real chains) OR tamper_detect < 1.0
               OR deterministic_replay < 1.0 (audit breaks on real data).
  INCONCLUSIVE_TAUTOLOGICAL_METRIC : scramble_gap < 0.10 OR gate_separation < 0.05.
  INCONCLUSIVE_RETRIEVAL_BROKEN    : oracle_bridge_acc < 0.85 OR hop1_retrieve_acc < 0.80 (the substrate
               retrieval primitive did not reproduce at the real-graph test regime -> downstream untrustworthy).
  INCONCLUSIVE_DISCRIMINATOR_DEAD  : accA_hard > 0.15 (single-shot solves the multi-hop -> not a real 2-hop test).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 of per-arm answer arrays; A/B/SCRAMBLE/ALWAYS diverge)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-gap discriminator; no single closed-form noise floor. Reachability by bundle-SNR
#   feasibility: for a bundle of M edges in N dims cleaned over V nodes, top1 is reliable while
#   M < N/(2 ln V); at N=8192, V~580 => M<~644. The ISA store holds the real edge count M=240 (=n_hard+
#   n_easy), sitting at 37% of the wall (SNR sqrt(N/M)=5.84) -- the SAME SNR the 120-edge SYN store had at
#   N=4096 (which yields hop1=0.997), so oracle reproduces clean (>0.95). accB = hop1 x hop2 is gated by
#   routing quality (~0.88 real-graph cap), landing non-ceiling in [0.82,0.92] (NOT saturated).
# - baseline_in_band (META_RULE_AG): BASELINE is ARM_A; on the MIXED corpus accA ~ frac_easy = 0.5,
#   strictly inside (0.05, 0.95). ARM_B is the mechanism arm (bounded above by 0.95 non-ceiling gate).
# - discriminator survives scale (option A): SMOKE holds N == FULL N (8192) AND n_hard/n_easy == FULL
#   (120/120), so the per-seed corpus and BOTH relation stores (SYN=120, ISA=240 edges) are built bit-
#   identical to FULL; only the seed count differs (3 vs 5). The oracle positive control is thus verified
#   at the REAL 240-edge single-cue store in smoke (the v1.0 smoke under-sized ISA to 150 and escaped).
# - HARD_PASS strictly above floor (META_RULE_L): gates strict (>=0.25 / <=0.95 / <=0.15 / ==1.0 / >=0.80).
# - HP_SCOPE: resolve/scramble/routing/non-ceiling/discriminator gates apply to ARM_B vs {ARM_A, ARM_ALWAYS,
#   ARM_B_SCRAMBLE}. ARM_ORACLE_BRIDGE carries only the >=0.85 retrieval-ceiling rail (positive control).
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS); verdict counts completed seeds.
# - per-unit failure-class instrumentation (no bare except; per-seed fatal-flag recorded to metrics)
# - calibration_check: default_ok_for_this_regime -- TAU_GATE=0.30 sits a-priori between the HARD noise-floor
#   margin (~sqrt(M/N)) and the EASY clean margin; NOT tuned per-seed. Verified telemetry-sensitive by gate_sep.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@:
#     CN 2-hop CN_SYNONYM->IS_A chain count 69292 MEASURED@data/substrate_index/concept/relations.jsonl (enumerated)
#     CN edges 189654 nodes 141511 MEASURED@data/substrate_index/concept/relations.jsonl
#     reasoning_chain_replay HARD_PASS 100pct det/verify/tamper CITED@experiments/exp_reasoning_chain_replay_v1.py
#     bundle top1 reliable while M < N/(2 ln V) THEORETICAL@ bundle-crosstalk gaussian max-order-statistic
#     accB non-ceiling target [0.80,0.92] HYPOTHESIZED@preregs/2026-07-08_glass_box_micro_loop_conceptnet_multihop_v1.md

Compute architecture: (b) sequential-CPU with justification. Genuinely SEQUENTIAL chained retrieval (hop-2
  depends on the hop-1 WM result) and the cell IS validating the substrate-primitive loop; wall time a few
  seconds/seed (V~580 x N=8192 cleanup matvecs). No GPU; no encoder; no torch.
  Storage: mixed -- each RELATION store is a GLOBAL bundled single-hop associative memory (exemption (a):
  single-hop read WITHIN a hop); cross-hop composition is SHARDED via WM re-binding (the bridge is carried
  in WM and re-bound into the second store, never fused into one global chain bundle).
progress_logging: print_flush_true (line-buffered stdout + flush=True per progress line). FULL timeout_s well
  under 1800s; heartbeat + flush retained defensively.

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Extends (CG certified): experiments/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1.py (commit ba552930a)
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_glass_box_micro_loop_conceptnet_multihop_v1.md
Reuses (mechanism-level; not re-run): experiments/exp_reasoning_chain_replay_v1.py (Merkle helpers transcribed),
  experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py (arbitration-margin gate),
  experiments/exp_pfc_bg_composed_attention_value_gate_v1.py (Go/NoGo value-gate decision).
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

from experiments._seed_checkpoint import get_output_dir, write_metrics, record_gate

ANCHOR_NAME = "glass_box_micro_loop_conceptnet_multihop_v1"
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
HP_ORACLE_BRIDGE_MIN = 0.85      # oracle-bridge retrieval ceiling (positive control at real-graph regime)
HP_HOP1_RETRIEVE_MIN = 0.80      # WM active-slot content is correctly retrieved (absorbs real branching)
HP_CAUSAL_FLIP_MIN = 0.80        # hand-editing the logged bridge flips correct->wrong downstream
HF_RESOLVE_LIFT_CEIL = 0.10      # resolve_lift < this => HARD_FAIL (loop adds nothing)
MB_RESOLVE_LIFT_LO = 0.10        # resolve_lift in [0.10,0.25) => MIDDLE_BAND
MB_GATE_SEP_LO = 0.05            # gate_separation in [0.05,0.10) => MIDDLE_BAND
MB_CAUSAL_FLIP_LO = 0.50         # causal_edit_flip in [0.50,0.80) => MIDDLE_BAND
MB_ROUTE_MARGIN_LO = 0.05        # gate_route_margin in [0.05,0.15) => MIDDLE_BAND
TAUT_SCRAMBLE_FLOOR = 0.10       # scramble_gap < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
TAUT_GATE_SEP_FLOOR = 0.05       # gate_separation < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
SIGN_P_MAX = 0.05                # paired sign-test threshold

# gate threshold: a-priori between the HARD-margin distribution and the EASY-margin distribution at the
# chosen real-graph store density (SYN=120,ISA=240 edges,N=8192). Measured margin physics: hard marginA
# mean~0.06 (p90~0.12), easy marginA median~0.39 (low tail to ~0.11). TAU=0.11 sits at hard-p90 / well
# below easy-median => routing ~0.88. A SINGLE fixed value (NOT tuned per-seed); the real easy/hard margin
# distributions genuinely overlap so routing caps ~0.89 (honest real-graph property, not a gate failure).
TAU_GATE = 0.11
FRAC_EASY = 0.5                  # mixed corpus: half easy (1-hop, single-shot resolves), half hard (2-hop)

# --------------------------- config (selftest / smoke / full) --------------------
# M_SYN / M_ISA are ABSOLUTE store capacities (edges bundled per relation store), held CONSTANT across
# smoke/full so per-hop difficulty is identical (discriminator-survives-scale option A). Trial edges are a
# subset of the store; the remainder are real co-typed distractor edges. Sized near M < N/(2 ln V) boundary
# so per-hop lands in [0.85,0.95] and accB = hop1 x hop2 is non-ceiling.
if SELF_TEST_MODE:
    N_DIM = 512
    N_HARD = 6
    N_EASY = 6
    M_SYN = 12
    M_ISA = 14
    SEEDS = [7]
    USE_REAL_GRAPH = False       # selftest uses a tiny SYNTHETIC graph (no data-file dependency)
elif RUN_MODE == "smoke":
    # v1.1 capacity fix (2026-07-08): SMOKE now uses the SAME n_hard/n_easy as FULL so the per-seed corpus
    # construction is BIT-IDENTICAL to FULL (SYN store = 120 edges, ISA store = 240 edges -- the REAL edge
    # count that the FULL run loads). The original smoke used n_hard=n_easy=40 which, with the m_isa=150
    # ceiling, built only a 150-edge ISA store; that UNDER-SIZED store cleared oracle at ~0.97 while FULL's
    # true 240-edge store landed oracle=0.825 (<0.85) -- the discriminator did NOT survive scale. Now smoke
    # exercises the true 240-edge single-cue store; only the seed count (3 vs 5) differs from FULL.
    N_DIM = 8192                 # == FULL N (raised 4096->8192 for store-capacity headroom; option A preview)
    N_HARD = 120                 # == FULL (so ISA store = n_hard+n_easy = 240 edges, real edge count)
    N_EASY = 120                 # == FULL
    M_SYN = 100                  # no-op ceiling: syn_edges = n_hard = 120 > 100 => 0 distractors => 120 edges
    M_ISA = 150                  # no-op ceiling: isa_edges = n_hard+n_easy = 240 > 150 => 0 distractors => 240
    SEEDS = [7, 17, 23]          # multi-seed smoke (>=3 seeds)
    USE_REAL_GRAPH = True
else:  # full
    # v1.1 capacity fix (2026-07-08): N raised 4096->8192. At N=4096 the single-cue ISA store (240 real edges,
    # V~580) sat at 74.6% of the top1 wall M<N/(2 ln V)~322 (SNR sqrt(N/M)=4.13) => oracle positive control
    # degraded to 0.825 (<0.85 floor) => INCONCLUSIVE_RETRIEVAL_BROKEN. Doubling N to 8192 doubles the wall to
    # ~644, dropping the SAME 240-edge store to 37.3% of wall (SNR=5.84) -- the identical SNR the 120-edge SYN
    # store had at N=4096 (which gives hop1=0.997) -- so oracle reproduces clean. This is a pure capacity-
    # headroom lever: the reasoning loop, gate, Merkle audit, discriminators and thresholds are UNCHANGED.
    N_DIM = 8192
    N_HARD = 120
    N_EASY = 120
    M_SYN = 100
    M_ISA = 150
    SEEDS = [7, 17, 23, 31, 41]
    USE_REAL_GRAPH = True

N_TRIALS = N_HARD + N_EASY
EXPECTED_N_UNITS = len(SEEDS)
ARMS = ["ARM_A_SINGLE_SHOT", "ARM_B_WM_REQUERY", "ARM_B_SCRAMBLE",
        "ARM_ALWAYS_REQUERY", "ARM_ORACLE_BRIDGE"]

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,n_hard=%d,n_easy=%d,M_syn=%d,M_isa=%d,frac_easy=%.2f,tau_gate=%.2f,seeds=%s,mode=%s,"
    "real_graph=%s,rel1=%s,rel2=%s,expected_n=%d,HP_resolve>=%.2f,HP_nonceil<=%.2f,HP_discrimAccAhard<=%.2f"
) % (ANCHOR_NAME, N_DIM, N_HARD, N_EASY, M_SYN, M_ISA, FRAC_EASY, TAU_GATE, SEEDS, RUN_MODE,
     USE_REAL_GRAPH, REL_HOP1, REL_HOP2, EXPECTED_N_UNITS, HP_RESOLVE_LIFT_MIN, HP_NONCEILING_MAX,
     HP_DISCRIM_ACCA_HARD_MAX)

_T0 = time.time()


# ============================================================================
# Merkle audit helpers -- TRANSCRIBED VERBATIM from experiments/exp_reasoning_chain_replay_v1.py
# (that cell runs _selftest() at import => NOT import-safe). HARD_PASS 100pct deterministic replay +
# Merkle verify + tamper detect. CITED@experiments/exp_reasoning_chain_replay_v1.py.
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
# ============================================================================
def make_codebook(V: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """(V, N) bipolar +/-1 float32 codebook (sharded; each concept its own random vector)."""
    return (rng.integers(0, 2, size=(V, N)).astype(np.float32) * 2.0 - 1.0)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def cleanup(probe: np.ndarray, E: np.ndarray) -> Tuple[int, float]:
    """Return (best_id, arbitration_margin) where margin = (top1 - top2) / N over the codebook dot scores."""
    scores = E @ probe                       # (V,)
    N = E.shape[1]
    if scores.shape[0] < 2:
        return int(np.argmax(scores)), 1.0
    top2 = np.argpartition(scores, -2)[-2:]
    a, b = top2[np.argsort(scores[top2])[::-1]]
    margin = float((scores[a] - scores[b]) / N)
    return int(a), margin


# ============================================================================
# REAL ConceptNet graph loading (cached) + tiny SYNTHETIC graph for selftest
# ============================================================================
_CN_CACHE: Dict[str, Any] = {}


def load_cn_graph(path: Path) -> Dict[str, Any]:
    """Load the REAL ConceptNet relations into out-adjacency for REL_HOP1 / REL_HOP2. Cached per path.
    Returns dict with syn_out (src->list[tgt]), isa_out (src->list[tgt]), isa_set (src->set[tgt])."""
    key = str(path)
    if key in _CN_CACHE:
        return _CN_CACHE[key]
    if not path.exists():
        raise FileNotFoundError("ConceptNet relations file not found: %s" % path)
    syn_out: Dict[str, List[str]] = {}
    isa_out: Dict[str, List[str]] = {}
    isa_set: Dict[str, set] = {}
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
            if rt == REL_HOP1:
                syn_out.setdefault(s, []).append(t)
            elif rt == REL_HOP2:
                isa_out.setdefault(s, []).append(t)
                isa_set.setdefault(s, set()).add(t)
            n_lines += 1
    g = {"syn_out": syn_out, "isa_out": isa_out, "isa_set": isa_set, "n_edges": n_lines}
    print("[cn_graph] loaded %d edges | syn_src=%d isa_src=%d" % (n_lines, len(syn_out), len(isa_out)),
          flush=True)
    _CN_CACHE[key] = g
    return g


def make_synthetic_graph(rng: np.random.Generator, n_hard: int, n_easy: int,
                         m_syn: int, m_isa: int) -> Dict[str, Any]:
    """Tiny SYNTHETIC 2-hop graph for the import selftest (no data-file dependency).
    Guarantees well-posed chains X-syn->A-isa->B with B NOT in isa[X]."""
    syn_out: Dict[str, List[str]] = {}
    isa_out: Dict[str, List[str]] = {}
    isa_set: Dict[str, set] = {}
    nid = [0]

    def node() -> str:
        nid[0] += 1
        return "S_%d" % nid[0]

    # hard chains
    for _ in range(n_hard + m_syn):
        x, a, b = node(), node(), node()
        syn_out.setdefault(x, []).append(a)
        isa_out.setdefault(a, []).append(b)
        isa_set.setdefault(a, set()).add(b)
    # easy 1-hop edges (fresh anchors)
    for _ in range(n_easy + m_isa):
        x, b = node(), node()
        isa_out.setdefault(x, []).append(b)
        isa_set.setdefault(x, set()).add(b)
    return {"syn_out": syn_out, "isa_out": isa_out, "isa_set": isa_set, "n_edges": nid[0]}


# ============================================================================
# per-seed corpus construction from the (real or synthetic) graph
# ============================================================================
def build_seed_corpus(graph: Dict[str, Any], seed: int, rng: np.random.Generator,
                      n_hard: int, n_easy: int, m_syn: int, m_isa: int, n_dim: int
                      ) -> Optional[Dict[str, Any]]:
    """Sample real 2-hop chains + real 1-hop edges, build GLOBAL bundled relation stores over random
    bipolar codes, and return the codebook + stores + per-trial query specs. Returns None on shortage.
    Difficulty knobs (n_hard/n_easy/m_syn/m_isa/n_dim) are EXPLICIT params so the import-selftest can run a
    clean small regime independent of the mode's dispatch config."""
    syn_out = graph["syn_out"]; isa_out = graph["isa_out"]; isa_set = graph["isa_set"]

    # ---- enumerate HARD candidates: X -syn-> A -isa-> B with B NOT in isa[X] (single-shot must fail) ----
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
        print("[build] seed=%d SHORTAGE hard: got %d/%d" % (seed, len(hard), n_hard), flush=True)
        return None

    hard_anchor_set = {x for (x, _, _) in hard}

    # ---- enumerate EASY 1-hop edges: X -isa-> B, X disjoint from hard anchors ----
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
        print("[build] seed=%d SHORTAGE easy: got %d/%d" % (seed, len(easy), n_easy), flush=True)
        return None

    # ---- distractor edges to fill each store to its absolute capacity M ----
    # SYN store must contain each hard X->A (n_hard edges) + (m_syn - n_hard) distractor syn edges.
    # ISA store must contain each hard A->B + each easy X->B (n_hard+n_easy edges) + distractor isa edges.
    # Distractor isa edges MUST NOT have a hard anchor as src (keeps single-shot-from-X on pure noise).
    def sample_syn_distractors(need: int, exclude_pairs: set) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        keys = list(syn_out.keys())
        guard = 0
        while len(out) < need and guard < need * 200 + 1000:
            guard += 1
            s = keys[int(rng.integers(0, len(keys)))]
            ts = syn_out[s]
            t = ts[int(rng.integers(0, len(ts)))]
            if s == t or (s, t) in exclude_pairs:
                continue
            out.append((s, t)); exclude_pairs.add((s, t))
        return out

    def sample_isa_distractors(need: int, exclude_pairs: set) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        keys = list(isa_out.keys())
        guard = 0
        while len(out) < need and guard < need * 200 + 1000:
            guard += 1
            s = keys[int(rng.integers(0, len(keys)))]
            if s in hard_anchor_set:            # hard anchors must not be ISA-store keys
                continue
            ts = isa_out[s]
            t = ts[int(rng.integers(0, len(ts)))]
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

    # ---- assign random bipolar codes to every distinct node in the corpus ----
    nodes: set = set()
    for (s, t) in syn_edges:
        nodes.add(s); nodes.add(t)
    for (s, t) in isa_edges:
        nodes.add(s); nodes.add(t)
    for (x, a, b) in hard:
        nodes.add(x); nodes.add(a); nodes.add(b)
    for (x, b) in easy:
        nodes.add(x); nodes.add(b)
    node_list = sorted(nodes)
    node2id = {nm: i for i, nm in enumerate(node_list)}
    V = len(node_list)
    E = make_codebook(V, n_dim, rng)

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

    return {"E": E, "SYN": SYN, "ISA": ISA, "trials": trials, "V": V,
            "n_syn_edges": len(syn_edges), "n_isa_edges": len(isa_edges)}


# ============================================================================
# the retrieve->gate->audit->requery loop (global-store variant of the certified loop)
# ============================================================================
def run_loop_trial(E: np.ndarray, SYN: np.ndarray, ISA: np.ndarray, tr: Dict[str, Any]) -> Dict[str, Any]:
    """Run retrieve->gate->audit->requery for one trial; return per-arm answers + Merkle audit log."""
    anchor = E[tr["anchor_id"]]

    # ---- hop-1: retrieve the CN_SYNONYM bridge into WM (active-slot content) ----
    bridge_hat_id, margin1 = cleanup(bind(anchor, SYN), E)

    # ---- single-shot answer attempt: raw anchor into the IS_A store (the gate's "why-signal") ----
    ansA_id, marginA = cleanup(bind(anchor, ISA), E)

    # ---- gate (Go/NoGo value-gate): margin >= tau => Go (commit shot); else NoGo (re-query) ----
    go = marginA >= TAU_GATE

    # ---- re-query (WM-mediated): bind the WM active-slot content (bridge_hat) into the IS_A store ----
    ansB_wm_id, marginB = cleanup(bind(E[bridge_hat_id], ISA), E)
    ansB_scr_id, _ = cleanup(bind(E[tr["rand_bridge_id"]], ISA), E)          # scramble control
    if tr["bridge_id"] >= 0:
        ansOracle_id, _ = cleanup(bind(E[tr["bridge_id"]], ISA), E)          # oracle: TRUE bridge into ISA
    else:
        ansOracle_id = ansA_id                                              # easy: oracle undefined -> shot

    ans_arm_A = ansA_id
    ans_arm_B = ansA_id if go else ansB_wm_id
    ans_arm_scr = ansA_id if go else ansB_scr_id
    ans_arm_always = ansB_wm_id
    ans_arm_oracle = ansOracle_id

    steps = [
        "query(anchor=%d,easy=%d)" % (tr["anchor_id"], int(tr["easy"])),
        "hop1_retrieve(bridge=%d,margin1=%.4f)" % (bridge_hat_id, margin1),
        "gate(marginA=%.4f,tau=%.4f,decision=%s,ansA=%d)" % (marginA, TAU_GATE, "GO" if go else "NOGO", ansA_id),
        "hop2_requery(bridge_used=%d,ansB=%d,marginB=%.4f)" % (bridge_hat_id, ansB_wm_id, marginB),
        "commit(answer=%d)" % ans_arm_B,
    ]
    root = merkle_root(steps)

    return {
        "easy": bool(tr["easy"]), "go": bool(go),
        "bridge_hat_id": bridge_hat_id, "bridge_id": tr["bridge_id"], "ans_id": tr["ans_id"],
        "margin1": float(margin1), "marginA": float(marginA), "marginB": float(marginB),
        "ans_arm": {"ARM_A_SINGLE_SHOT": ans_arm_A, "ARM_B_WM_REQUERY": ans_arm_B,
                    "ARM_B_SCRAMBLE": ans_arm_scr, "ARM_ALWAYS_REQUERY": ans_arm_always,
                    "ARM_ORACLE_BRIDGE": ans_arm_oracle},
        "steps": steps, "root": root,
    }


def causal_hand_edit(E: np.ndarray, ISA: np.ndarray, tr: Dict[str, Any], res: Dict[str, Any]
                     ) -> Dict[str, Any]:
    """Hand-edit the logged hop-1 bridge (true -> a distractor) and re-run the downstream hop-2 recompute.
    Returns (answer_flipped, tamper_flag_fired). Monitor-not-control: the recomputed answer changes AND the
    committed Merkle root breaks."""
    edited_bridge_id = tr["rand_bridge_id"]                    # adversarial swap: true bridge -> distractor
    ans_recompute_id, _ = cleanup(bind(E[edited_bridge_id], ISA), E)
    answer_flipped = bool(ans_recompute_id != res["ans_arm"]["ARM_B_WM_REQUERY"])
    edited_steps = list(res["steps"])
    edited_steps[1] = "hop1_retrieve(bridge=%d,margin1=%.4f)" % (edited_bridge_id, res["margin1"])
    edited_steps[3] = "hop2_requery(bridge_used=%d,ansB=%d,marginB=%.4f)" % (
        edited_bridge_id, ans_recompute_id, res["marginB"])
    tamper_flag_fired = bool(not merkle_verify(edited_steps, res["root"]))
    return {"answer_flipped": answer_flipped, "tamper_flag_fired": tamper_flag_fired,
            "recomputed_answer": int(ans_recompute_id)}


def binom_two_sided_p(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial p-value for k successes in n trials (sign test)."""
    if n == 0:
        return 1.0
    from math import comb
    probs = [comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(n + 1)]
    obs = probs[k]
    return float(min(1.0, sum(pr for pr in probs if pr <= obs + 1e-12)))


# ============================================================================
# per-seed runner
# ============================================================================
def run_one_seed(seed: int, graph: Dict[str, Any], out_dir: Path) -> Optional[Dict[str, Any]]:
    rng = np.random.default_rng(seed)
    corpus = build_seed_corpus(graph, seed, rng, N_HARD, N_EASY, M_SYN, M_ISA, N_DIM)
    if corpus is None:
        return None
    E = corpus["E"]; SYN = corpus["SYN"]; ISA = corpus["ISA"]; trials = corpus["trials"]

    n = len(trials)
    per_arm_correct = {a: np.zeros(n, dtype=bool) for a in ARMS}
    per_arm_ans = {a: np.full(n, -1, dtype=np.int64) for a in ARMS}
    easy_flags = np.array([bool(t["easy"]) for t in trials])
    margins_easy: List[float] = []
    margins_hard: List[float] = []
    route_correct = np.zeros(n, dtype=bool)
    hop1_correct_hard: List[bool] = []
    oracle_correct_hard: List[bool] = []
    accA_hard_correct: List[bool] = []
    det_ok = np.zeros(n, dtype=bool)
    verify_ok = np.zeros(n, dtype=bool)
    tamper_ok = np.zeros(n, dtype=bool)
    causal_flip: List[bool] = []
    causal_tamper: List[bool] = []
    requery_count = 0

    for i, tr in enumerate(trials):
        res = run_loop_trial(E, SYN, ISA, tr)
        res2 = run_loop_trial(E, SYN, ISA, tr)                 # deterministic replay
        det_ok[i] = (res2["root"] == res["root"] and
                     res2["ans_arm"]["ARM_B_WM_REQUERY"] == res["ans_arm"]["ARM_B_WM_REQUERY"])
        verify_ok[i] = merkle_verify(res["steps"], res["root"])
        tampered = list(res["steps"])
        tampered[4] = "commit(answer=%d)" % (res["ans_arm"]["ARM_B_WM_REQUERY"] + 1)
        tamper_ok[i] = (not merkle_verify(tampered, res["root"]))

        for a in ARMS:
            per_arm_correct[a][i] = (res["ans_arm"][a] == tr["ans_id"])
            per_arm_ans[a][i] = res["ans_arm"][a]

        if tr["easy"]:
            margins_easy.append(res["marginA"])
            route_correct[i] = res["go"]                       # easy routed correctly iff GO (accept shot)
        else:
            margins_hard.append(res["marginA"])
            route_correct[i] = (not res["go"])                 # hard routed correctly iff NOGO (re-query)
            hop1_correct_hard.append(res["bridge_hat_id"] == tr["bridge_id"])
            oracle_correct_hard.append(res["ans_arm"]["ARM_ORACLE_BRIDGE"] == tr["ans_id"])
            accA_hard_correct.append(res["ans_arm"]["ARM_A_SINGLE_SHOT"] == tr["ans_id"])
        if not res["go"]:
            requery_count += 1

        # causal hand-edit demonstration (HARD + ARM_B correct)
        if (not tr["easy"]) and per_arm_correct["ARM_B_WM_REQUERY"][i]:
            ce = causal_hand_edit(E, ISA, tr, res)
            causal_flip.append(ce["answer_flipped"])
            causal_tamper.append(ce["tamper_flag_fired"])

    accs = {a: float(per_arm_correct[a].mean()) for a in ARMS}
    accA = accs["ARM_A_SINGLE_SHOT"]; accB = accs["ARM_B_WM_REQUERY"]
    accScr = accs["ARM_B_SCRAMBLE"]; accAlways = accs["ARM_ALWAYS_REQUERY"]
    accOracle = float(np.mean(oracle_correct_hard)) if oracle_correct_hard else 0.0
    accA_hard = float(np.mean(accA_hard_correct)) if accA_hard_correct else 0.0
    hop1_acc = float(np.mean(hop1_correct_hard)) if hop1_correct_hard else 0.0

    b = per_arm_correct["ARM_B_WM_REQUERY"]; a_ = per_arm_correct["ARM_A_SINGLE_SHOT"]
    n_b_only = int((b & (~a_)).sum()); n_a_only = int((a_ & (~b)).sum())
    n_disc = n_b_only + n_a_only
    sign_p = binom_two_sided_p(n_b_only, n_disc, 0.5) if n_disc > 0 else 1.0

    gate_sep = (float(np.mean(margins_easy)) - float(np.mean(margins_hard))) if margins_easy and margins_hard else 0.0
    causal_flip_rate = float(np.mean(causal_flip)) if causal_flip else 0.0
    causal_tamper_rate = float(np.mean(causal_tamper)) if causal_tamper else 0.0

    arm_digests = {a2: hashlib.sha256(per_arm_ans[a2].tobytes()).hexdigest()[:16] for a2 in ARMS}
    core_arms = ["ARM_A_SINGLE_SHOT", "ARM_B_WM_REQUERY", "ARM_B_SCRAMBLE", "ARM_ALWAYS_REQUERY"]
    arms_differ = (len({arm_digests[a2] for a2 in core_arms}) == len(core_arms))

    rec = {
        "seed": int(seed), "N": N_DIM, "V": corpus["V"], "n_trials": n, "n_hard": int((~easy_flags).sum()),
        "n_easy": int(easy_flags.sum()), "n_syn_edges": corpus["n_syn_edges"],
        "n_isa_edges": corpus["n_isa_edges"], "run_mode": RUN_MODE, "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION, "frac_easy": FRAC_EASY, "tau_gate": TAU_GATE,
        "accs": accs, "accA": accA, "accB": accB, "accScramble": accScr,
        "accAlways": accAlways, "accOracle": accOracle, "accA_hard": accA_hard,
        "resolve_lift": float(accB - accA),
        "gate_route_margin": float(accB - accAlways),
        "scramble_gap": float(accB - accScr),
        "gate_separation": float(gate_sep),
        "gate_routing_acc": float(route_correct.mean()),
        "hop1_retrieve_acc": float(hop1_acc),
        "deterministic_replay": float(det_ok.mean()),
        "merkle_verify": float(verify_ok.mean()),
        "tamper_detect": float(tamper_ok.mean()),
        "causal_edit_flip": causal_flip_rate,
        "causal_edit_tamper": causal_tamper_rate,
        "n_causal_trials": len(causal_flip),
        "sign_p": float(sign_p), "n_b_only": n_b_only, "n_a_only": n_a_only,
        "requery_count": int(requery_count),
        "margin_easy_mean": float(np.mean(margins_easy)) if margins_easy else 0.0,
        "margin_hard_mean": float(np.mean(margins_hard)) if margins_hard else 0.0,
        "arm_digests": arm_digests,
        "arms_differ": bool(arms_differ),
        "arms_differ_exempted": [["ARM_ALWAYS_REQUERY", "ARM_ORACLE_BRIDGE"]],
    }
    print("[seed=%d] V=%d accA=%.3f accB=%.3f accAlways=%.3f accScr=%.3f accOracle=%.3f accA_hard=%.3f | "
          "resolve_lift=%.3f route_margin=%.3f scramble_gap=%.3f gate_sep=%.3f routing=%.3f hop1=%.3f | "
          "det=%.3f verify=%.3f tamper=%.3f causal_flip=%.3f(n=%d) sign_p=%.4f"
          % (seed, corpus["V"], accA, accB, accAlways, accScr, accOracle, accA_hard, rec["resolve_lift"],
             rec["gate_route_margin"], rec["scramble_gap"], rec["gate_separation"], rec["gate_routing_acc"],
             rec["hop1_retrieve_acc"], rec["deterministic_replay"], rec["merkle_verify"], rec["tamper_detect"],
             rec["causal_edit_flip"], rec["n_causal_trials"], rec["sign_p"]), flush=True)
    return rec


# ============================================================================
# aggregate + verdict
# ============================================================================
def _selftest() -> None:
    """Formula self-tests (PROT-022): (1) merkle chains + tamper; (2) bind self-inverse; (3) the weak-first
    real-graph-shaped regime fires on a tiny SYNTHETIC graph (single-shot fails HARD, WM re-query resolves,
    causal edit flips)."""
    r = merkle_root(["a", "b", "c"])
    assert merkle_verify(["a", "b", "c"], r), "merkle verify"
    assert not merkle_verify(["a", "b", "X"], r), "tamper detected"
    assert merkle_root(["a"]) != h(b"genesis"), "merkle chains beyond genesis"
    rng = np.random.default_rng(0)
    E = make_codebook(16, 256, rng)
    x = E[3]; k = E[5]
    assert np.array_equal(bind(k, bind(k, x)), x), "bind self-inverse"
    # (3) tiny CLEAN synthetic-graph corpus (fixed small params, mode-independent): HARD single-shot fails,
    #     WM re-query resolves, causal edit flips. Difficulty calibration is a smoke concern, not a formula test.
    st_nh, st_ne, st_ms, st_mi, st_nd = 6, 6, 12, 14, 512
    g = make_synthetic_graph(np.random.default_rng(1), st_nh, st_ne, st_ms, st_mi)
    corpus = build_seed_corpus(g, 2, np.random.default_rng(2), st_nh, st_ne, st_ms, st_mi, st_nd)
    assert corpus is not None, "synthetic corpus built"
    E2 = corpus["E"]; SYN2 = corpus["SYN"]; ISA2 = corpus["ISA"]
    hard_trials = [t for t in corpus["trials"] if not t["easy"]]
    easy_trials = [t for t in corpus["trials"] if t["easy"]]
    assert hard_trials and easy_trials, "both trial types present"
    nb_ok = 0; a_hard_ok = 0; hop1_ok = 0; flip_ok = 0; ce_n = 0
    for tr in hard_trials:
        res = run_loop_trial(E2, SYN2, ISA2, tr)
        nb_ok += int(res["ans_arm"]["ARM_B_WM_REQUERY"] == tr["ans_id"])
        a_hard_ok += int(res["ans_arm"]["ARM_A_SINGLE_SHOT"] == tr["ans_id"])
        hop1_ok += int(res["bridge_hat_id"] == tr["bridge_id"])
        if res["ans_arm"]["ARM_B_WM_REQUERY"] == tr["ans_id"]:
            ce = causal_hand_edit(E2, ISA2, tr, res); ce_n += 1
            flip_ok += int(ce["answer_flipped"]); assert ce["tamper_flag_fired"], "tamper fires"
    nh = len(hard_trials)
    assert nb_ok >= 0.8 * nh, "WM re-query resolves most HARD (%d/%d)" % (nb_ok, nh)
    assert a_hard_ok <= 0.2 * nh, "single-shot fails most HARD (discriminator fires) (%d/%d)" % (a_hard_ok, nh)
    assert hop1_ok >= 0.7 * nh, "hop1 retrieves bridge (%d/%d)" % (hop1_ok, nh)
    assert (ce_n == 0 or flip_ok >= 0.8 * ce_n), "causal edit flips downstream (%d/%d)" % (flip_ok, ce_n)
    ea_ok = 0
    for tr in easy_trials:
        rese = run_loop_trial(E2, SYN2, ISA2, tr)
        ea_ok += int(rese["ans_arm"]["ARM_A_SINGLE_SHOT"] == tr["ans_id"] and rese["go"])
    assert ea_ok >= 0.8 * len(easy_trials), "EASY single-shot resolves with GO (%d/%d)" % (ea_ok, len(easy_trials))
    print("[selftest] PASS: conceptnet multi-hop glass-box loop "
          "(merkle+tamper, bind-inverse, weak-first fires on synthetic graph)", flush=True)


def aggregate_and_verdict(per_seed: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Any]]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed results",
                "summary": "no per-seed results"}, []

    def col(f):
        return [float(r[f]) for r in per_seed]

    m = {f: float(np.mean(col(f))) for f in
         ["accA", "accB", "accScramble", "accAlways", "accOracle", "accA_hard", "resolve_lift",
          "gate_route_margin", "scramble_gap", "gate_separation", "gate_routing_acc", "hop1_retrieve_acc",
          "deterministic_replay", "merkle_verify", "tamper_detect", "causal_edit_flip", "causal_edit_tamper",
          "margin_easy_mean", "margin_hard_mean"]}
    n_b_only = sum(int(r["n_b_only"]) for r in per_seed)
    n_a_only = sum(int(r["n_a_only"]) for r in per_seed)
    n_disc = n_b_only + n_a_only
    sign_p = binom_two_sided_p(n_b_only, n_disc, 0.5) if n_disc > 0 else 1.0
    arms_differ = all(bool(r["arms_differ"]) for r in per_seed)
    completed = len(per_seed)
    cardinality_ok = completed >= EXPECTED_N_UNITS

    retrieval_ok = (m["accOracle"] >= HP_ORACLE_BRIDGE_MIN and m["hop1_retrieve_acc"] >= HP_HOP1_RETRIEVE_MIN)
    audit_ok = (m["deterministic_replay"] >= 0.999 and m["merkle_verify"] >= 0.999 and m["tamper_detect"] >= 0.999)
    telemetry_ok = (m["scramble_gap"] >= TAUT_SCRAMBLE_FLOOR and m["gate_separation"] >= TAUT_GATE_SEP_FLOOR)
    discriminator_fires = (m["accA_hard"] <= HP_DISCRIM_ACCA_HARD_MAX)
    non_ceiling = (m["accB"] <= HP_NONCEILING_MAX)

    s = ("accA=%.3f accB=%.3f accAlways=%.3f accScr=%.3f accOracle=%.3f accA_hard=%.3f | resolve_lift=%.3f "
         "route_margin=%.3f scramble_gap=%.3f gate_sep=%.3f routing=%.3f hop1=%.3f | det=%.3f verify=%.3f "
         "tamper=%.3f causal_flip=%.3f causal_tamper=%.3f sign_p=%.4f (seeds=%d)"
         % (m["accA"], m["accB"], m["accAlways"], m["accScramble"], m["accOracle"], m["accA_hard"],
            m["resolve_lift"], m["gate_route_margin"], m["scramble_gap"], m["gate_separation"],
            m["gate_routing_acc"], m["hop1_retrieve_acc"], m["deterministic_replay"], m["merkle_verify"],
            m["tamper_detect"], m["causal_edit_flip"], m["causal_edit_tamper"], sign_p, completed))

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = "HARD_FAIL: completed %d < expected %d seeds. " % (completed, EXPECTED_N_UNITS) + s
    elif not audit_ok:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL: audit not sound on real data (det/merkle/tamper < 1.0). " + s
    elif not retrieval_ok:
        verdict = "INCONCLUSIVE_RETRIEVAL_BROKEN"
        vmsg = ("INCONCLUSIVE_RETRIEVAL_BROKEN: oracle_bridge=%.3f (>=%.2f) or hop1=%.3f (>=%.2f) failed; "
                "substrate retrieval did not reproduce at the real-graph regime -> downstream untrustworthy. "
                % (m["accOracle"], HP_ORACLE_BRIDGE_MIN, m["hop1_retrieve_acc"], HP_HOP1_RETRIEVE_MIN)) + s
    elif not discriminator_fires:
        verdict = "INCONCLUSIVE_DISCRIMINATOR_DEAD"
        vmsg = ("INCONCLUSIVE_DISCRIMINATOR_DEAD: accA_hard=%.3f > %.2f -- single-shot already solves the "
                "multi-hop chains, so this is not a genuine 2-hop test (raise difficulty). "
                % (m["accA_hard"], HP_DISCRIM_ACCA_HARD_MAX)) + s
    elif not telemetry_ok:
        verdict = "INCONCLUSIVE_TAUTOLOGICAL_METRIC"
        vmsg = ("INCONCLUSIVE_TAUTOLOGICAL_METRIC: scramble_gap=%.3f (>=%.2f) or gate_sep=%.3f (>=%.2f) too low; "
                "resolution not attributable to correct WM binding / self-audit not telemetry-sensitive. "
                % (m["scramble_gap"], TAUT_SCRAMBLE_FLOOR, m["gate_separation"], TAUT_GATE_SEP_FLOOR)) + s
    elif not non_ceiling:
        verdict = "SATURATION_TOO_EASY"
        vmsg = ("SATURATION_TOO_EASY: accB=%.3f > %.2f -- the real-graph regime is ceiling-saturated (like the "
                "toy); raise store capacity M so accB drops into a graded-difficulty band before certifying "
                "generalization. NOT a HARD_PASS. " % (m["accB"], HP_NONCEILING_MAX)) + s
    elif m["resolve_lift"] < HF_RESOLVE_LIFT_CEIL:
        verdict = "HARD_FAIL"
        vmsg = ("HARD_FAIL: resolve_lift=%.3f < %.2f -- the WM re-query loop adds nothing over a single shot on "
                "real chains (mechanism does not generalize past the toy). " % (m["resolve_lift"], HF_RESOLVE_LIFT_CEIL)) + s
    elif (m["resolve_lift"] >= HP_RESOLVE_LIFT_MIN and m["gate_route_margin"] >= HP_GATE_ROUTE_MARGIN
          and sign_p < SIGN_P_MAX and m["gate_separation"] >= HP_GATE_SEP_MIN
          and m["gate_routing_acc"] >= HP_GATE_ROUTING_ACC_MIN and m["scramble_gap"] >= HP_SCRAMBLE_GAP_MIN
          and m["causal_edit_flip"] >= HP_CAUSAL_FLIP_MIN and arms_differ):
        verdict = "HARD_PASS"
        vmsg = ("HARD_PASS: on REAL ConceptNet 2-hop chains (X-CN_SYNONYM->A-IS_A->B), the gated WM-mediated "
                "re-query resolves what a single shot cannot (resolve_lift=%.3f, accB=%.3f NON-CEILING, "
                "single-shot on the multi-hop accA_hard=%.3f), beats always-requery by %.3f (p=%.4f), the "
                "self-audit is telemetry-sensitive (gate_sep=%.3f, scramble_gap=%.3f), and the glass-box "
                "hand-edit changes the downstream recompute on real chains (causal_flip=%.3f) while firing the "
                "tamper flag (tamper=%.3f). Generalizes the certified loop to ingested knowledge. "
                % (m["resolve_lift"], m["accB"], m["accA_hard"], m["gate_route_margin"], sign_p,
                   m["gate_separation"], m["scramble_gap"], m["causal_edit_flip"], m["tamper_detect"])) + s
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("MIDDLE_BAND: audit sound + retrieval reproduced + telemetry-sensitive + non-ceiling + "
                "discriminator fires, but a HARD_PASS gate missed (resolve_lift=%.3f route_margin=%.3f "
                "gate_sep=%.3f scramble_gap=%.3f causal_flip=%.3f routing=%.3f p=%.4f arms_differ=%s). "
                % (m["resolve_lift"], m["gate_route_margin"], m["gate_separation"], m["scramble_gap"],
                   m["causal_edit_flip"], m["gate_routing_acc"], sign_p, arms_differ)) + s

    gate_claims = [
        record_gate("resolve_lift", m["resolve_lift"], HP_RESOLVE_LIFT_MIN, ">=", "accB - accA"),
        record_gate("accB_non_ceiling", m["accB"], HP_NONCEILING_MAX, "<=", "graded real-graph difficulty"),
        record_gate("accA_hard_discriminator", m["accA_hard"], HP_DISCRIM_ACCA_HARD_MAX, "<=", "single-shot fails multihop"),
        record_gate("gate_route_margin", m["gate_route_margin"], HP_GATE_ROUTE_MARGIN, ">=", "accB - accALWAYS"),
        record_gate("gate_separation", m["gate_separation"], HP_GATE_SEP_MIN, ">=", "margin(easy)-margin(hard)"),
        record_gate("gate_routing_acc", m["gate_routing_acc"], HP_GATE_ROUTING_ACC_MIN, ">="),
        record_gate("scramble_gap", m["scramble_gap"], HP_SCRAMBLE_GAP_MIN, ">=", "telemetry-sensitivity"),
        record_gate("oracle_bridge_acc", m["accOracle"], HP_ORACLE_BRIDGE_MIN, ">=", "positive control"),
        record_gate("hop1_retrieve_acc", m["hop1_retrieve_acc"], HP_HOP1_RETRIEVE_MIN, ">="),
        record_gate("deterministic_replay", m["deterministic_replay"], 0.999, ">="),
        record_gate("merkle_verify", m["merkle_verify"], 0.999, ">="),
        record_gate("tamper_detect", m["tamper_detect"], 0.999, ">="),
        record_gate("causal_edit_flip", m["causal_edit_flip"], HP_CAUSAL_FLIP_MIN, ">="),
        record_gate("sign_p", sign_p, SIGN_P_MAX, "<", "paired B vs A"),
    ]
    summary = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg[:300], "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "n_seeds": completed, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": cardinality_ok,
        "arms_differ": arms_differ, "sign_p": sign_p, "means": m, "per_seed": per_seed,
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

    per_seed: List[Dict[str, Any]] = []
    for si, seed in enumerate(SEEDS):
        rec = run_one_seed(int(seed), graph, out_dir)
        if rec is not None:
            per_seed.append(rec)
        _heartbeat(out_dir, si + 1, len(SEEDS), "seed=%d done" % seed)

    summary, gate_claims = aggregate_and_verdict(per_seed)
    print("\n[VERDICT] " + summary["verdict_msg"], flush=True)
    write_metrics(out_dir, summary, per_seed, gate_claims=gate_claims)
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
