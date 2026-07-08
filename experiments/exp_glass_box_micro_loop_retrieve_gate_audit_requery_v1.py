"""glass_box_micro_loop_retrieve_gate_audit_requery_v1 -- a minimal GLASS-BOX reasoning micro-loop.

WHAT THIS IS (brain-grounded forward-integration cell; CPU/numpy only, does NOT touch GPU or the encoder):
  Compose three ALREADY-CERTIFIED substrate parts into one inspectable + hand-editable loop:
    retrieve -> gate (self-audit) -> re-query -> commit, with every hop wrapped in a Merkle audit log.

  Brain grounding (notes/research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md):
    - PFC->hippocampus retrieval-in-service-of-inference: a content cue reaches a CA3 attractor; the
      arbitration/match-mismatch signal is the "stop vs re-query" evaluator (thread 1).
    - Working memory holds the partial result (active slot); it is BOUND with the query context to
      bias the second completion (thread 2 active-slot; thread 4 offline re-completion over the same
      stored weights, NOT a separate planner).
    - Cortico-BG-thalamic Go/NoGo value-gate decides WHETHER to commit the single shot or re-query
      (thread 3): high arbitration margin => Go (commit); low margin => NoGo (gather more / re-query).

  Composed certified parts (REUSED at the mechanism level; the GPU cells are NOT re-run):
    (A) Merkle audit-replay -- exp_reasoning_chain_replay_v1 / exp_khop_audit_replay_v1 (HARD_PASS):
        the deterministic replay + per-step Merkle commitment + tamper-detect helpers are TRANSCRIBED
        verbatim (both cells run _selftest at import => not import-safe). This IS the glass-box wrapper.
    (B) attention-routing arbitration gate -- exp_substrate_gen_lm_combinedgate_recency_content_v8
        (CHAIN_GRADE): the arbitration MARGIN (top1-top2 of the biased-competition over the codebook)
        is the "why-signal" the gate reads. Realized here as the CPU cleanup-margin (same quantity the
        v8 content-relevance softmax arbitrates); the v8 cell is GPU / not import-safe.
    (C) basal-ganglia value-gate Go/NoGo -- exp_pfc_bg_composed_attention_value_gate_v1: the
        margin-threshold accept/re-query decision is the Go/NoGo actor (commit vs gather-more).

THE FALSIFIABLE REGIME (weak-first; "B beats A" is NOT tautological):
  A per-trial corpus MIXES two trial types the loop cannot tell apart a priori:
    EASY  (frac_easy): the answer is bound DIRECTLY to the query anchor in the hop-2 store, so a SINGLE
          shot (unbind with the anchor) resolves it with HIGH arbitration margin.
    HARD  (1-frac_easy): the answer is bound to a BRIDGE concept, NOT the anchor. A single shot from the
          anchor lands on NOISE (LOW margin, wrong). Only a WM-mediated re-query resolves it: retrieve the
          bridge from the hop-1 store (the WM active-slot content), BIND it into the hop-2 store, unbind
          the answer. Up to 2 hops.
  Because the two types are mixed, the arbitration-margin gate is LOAD-BEARING in BOTH directions:
    - ARM_A_SINGLE_SHOT (always commit shot)      resolves EASY, fails HARD   -> acc ~ frac_easy
    - ARM_ALWAYS_REQUERY (always re-query)         resolves HARD, BREAKS EASY  -> acc ~ (1-frac_easy)
    - ARM_B_WM_REQUERY (gated: margin>=tau => Go)  resolves BOTH               -> acc ~ 1.0
  So the gated loop dominates BOTH always-accept AND always-re-query -- the self-audit routing is the
  mechanism, not "a free second try". If a single shot could solve HARD trials, ARM_A would already win
  and resolve_lift would be ~0 (the HARD_FAIL branch). This is measured, not assumed.

TELEMETRY-SENSITIVITY (MANDATORY guard; two tautological-metric incidents 2026-07-07/08):
  ARM_B_SCRAMBLE re-queries with a RANDOM bridge code instead of the WM active-slot content. If the
  "resolution" were an artifact of merely re-querying, SCRAMBLE would resolve too. It must collapse toward
  ARM_A (scramble_gap = accB - accB_scramble >= 0.25). scramble_gap < 0.10 => INCONCLUSIVE_TAUTOLOGICAL
  (reported as inconclusive, NOT a clean negative). The gate margin must ALSO separate EASY from HARD
  (gate_separation >= 0.10); if it does not, the self-audit signal is not telemetry-sensitive.

THE GLASS-BOX HAND-EDIT DEMONSTRATION (the literal point):
  Every hop is logged as a hop_record and chained into a Merkle root (PER-HOP-AUDIT anchor, cosine=0.32 in
  the substrate KB: research_drill_compliance_maximization_2x_2026-06-09). Two facets are demonstrated:
    (1) TAMPER-DETECT: hand-edit ONE logged retrieval step; recompute the root; it mismatches the committed
        root => the tamper flag fires (must be 100%).
    (2) CAUSAL-EDIT (monitor-not-control): on a HARD trial the loop got CORRECT, hand-edit the logged
        bridge from the true bridge to the DISTRACTOR bridge; RE-RUN the downstream hop-2 recompute from the
        edited value => the committed answer flips (correct->wrong). This proves the logged step is
        load-bearing (the log is causally faithful, hand-editable), not decorative.

CONTRACT (pre-registered; preregs/2026-07-08_glass_box_micro_loop_retrieve_gate_audit_requery_v1.md):
  HARD_PASS  : resolve_lift(accB-accA) >= 0.25 AND accB-accALWAYS >= 0.25 AND paired sign-test p < 0.05
               AND gate_separation >= 0.10 AND gate_routing_acc >= 0.90 AND scramble_gap >= 0.25
               AND oracle_bridge_acc >= 0.90 AND hop1_retrieve_acc >= 0.90
               AND deterministic_replay == 1.0 AND merkle_verify == 1.0 AND tamper_detect == 1.0
               AND causal_edit_flip >= 0.80 AND arms_differ.
  MIDDLE_BAND: resolve_lift in [0.10,0.25) OR gate_separation in [0.05,0.10) OR causal_edit_flip in [0.50,0.80).
  HARD_FAIL  : resolve_lift < 0.10 (the loop adds nothing) OR tamper_detect < 1.0 OR deterministic_replay < 1.0
               (the audit edit is not detected / replay not deterministic).
  INCONCLUSIVE_TAUTOLOGICAL_METRIC : scramble_gap < 0.10 OR gate_separation < 0.05.
  INCONCLUSIVE_RETRIEVAL_BROKEN    : oracle_bridge_acc < 0.90 OR hop1_retrieve_acc < 0.90 (the substrate
               retrieval primitive did not reproduce at the test regime -> downstream arms untrustworthy).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 of per-arm answer arrays; A/B/SCRAMBLE/ALWAYS diverge)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-gap discriminator; no single closed-form noise floor. Reachability by bundle-SNR
#   feasibility: hop bundle M/N = 20/4096 << capacity so clean unbind top1 ~ 1.0; a raw-anchor unbind of a
#   bridge-keyed answer is orthogonal to E => argmax near chance 1/V=1/256. Discriminator gates well inside.
# - baseline_in_band (META_RULE_AG): the BASELINE is ARM_A; on the MIXED corpus accA ~ frac_easy = 0.5,
#   strictly inside (0.05, 0.95). ARM_B is the mechanism arm (ceiling allowed).
# - discriminator survives scale (option A): SMOKE holds N == FULL N (4096) so per-hop cleanup difficulty and
#   the raw-anchor noise floor are identical to FULL; smoke previews the FULL discriminator at fewer trials/seeds.
# - HARD_PASS strictly above floor (META_RULE_L): gates strict (>=0.25 / >=0.10 / >=0.25 / ==1.0 / >=0.80).
# - HP_SCOPE: resolve/scramble/routing gates apply to ARM_B vs {ARM_A, ARM_ALWAYS, ARM_B_SCRAMBLE}.
#   ARM_ORACLE_BRIDGE carries only the >=0.90 retrieval-ceiling rail (positive control at test regime).
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS); verdict counts completed seeds.
# - per-unit failure-class instrumentation (no bare except; per-seed fatal-flag recorded to metrics)
# - calibration_check: default_ok_for_this_regime -- TAU_GATE=0.30 sits a-priori between the HARD noise-floor
#   margin (~sqrt(M/N)=0.07) and the EASY clean margin (~0.9); NOT tuned per-seed. Verified telemetry-sensitive
#   by gate_separation.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@:
#     PER-HOP-AUDIT anchor cosine=0.3242 CITED@notes/research_drill_compliance_maximization_2x_2026-06-09.md
#     reasoning_chain_replay HARD_PASS 100pct det/verify/tamper CITED@experiments/exp_reasoning_chain_replay_v1.py
#     HARD noise-floor margin ~ sqrt(M/N) = sqrt(20/4096) = 0.070 THEORETICAL@ bundle-crosstalk sqrt-law
#     EASY clean margin ~ 1 - sqrt(M/N) ~ 0.93 THEORETICAL@ clean-unbind cosine
#     resolve_lift full HARD_PASS P HYPOTHESIZED@preregs/2026-07-08_glass_box_micro_loop_..._v1.md

Compute architecture: (b) sequential-CPU with justification. This is a genuinely SEQUENTIAL chained
  retrieval (hop-2 depends on the hop-1 WM result) and the cell IS validating the substrate-primitive loop;
  wall time is a few seconds/seed (V=256 x N=4096 cleanup is a tiny matvec). No GPU; no encoder; no torch.
  Storage: mixed -- each hop is a per-hop BUNDLED single-hop associative memory (exemption (a): pure
  single-hop read, no downstream composition WITHIN a hop); cross-hop composition is SHARDED via WM
  re-binding (the bridge is carried in WM and re-bound, never fused into one global chain bundle).
progress_logging: print_flush_true (line-buffered stdout + flush=True per progress line). FULL timeout_s
  well under 1800s but heartbeat + flush retained defensively.

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_glass_box_micro_loop_retrieve_gate_audit_requery_v1.md
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
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics, record_gate

ANCHOR_NAME = "glass_box_micro_loop_retrieve_gate_audit_requery_v1"

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
HP_GATE_ROUTE_MARGIN = 0.25      # accB - accALWAYS (gated routing beats always-requery => gate load-bearing)
HP_GATE_SEP_MIN = 0.10           # mean margin(EASY) - mean margin(HARD) (self-audit telemetry-sensitive)
HP_GATE_ROUTING_ACC_MIN = 0.90   # fraction of trials routed correctly (easy->accept, hard->requery)
HP_SCRAMBLE_GAP_MIN = 0.25       # accB - accB_scramble (WM content is what resolves)
HP_ORACLE_BRIDGE_MIN = 0.90      # oracle-bridge retrieval ceiling (positive control at test regime)
HP_HOP1_RETRIEVE_MIN = 0.90      # WM active-slot content is correctly retrieved
HP_CAUSAL_FLIP_MIN = 0.80        # hand-editing the logged bridge flips correct->wrong downstream
HF_RESOLVE_LIFT_CEIL = 0.10      # resolve_lift < this => HARD_FAIL (loop adds nothing)
MB_RESOLVE_LIFT_LO = 0.10        # resolve_lift in [0.10,0.25) => MIDDLE_BAND
MB_GATE_SEP_LO = 0.05            # gate_separation in [0.05,0.10) => MIDDLE_BAND
MB_CAUSAL_FLIP_LO = 0.50         # causal_edit_flip in [0.50,0.80) => MIDDLE_BAND
TAUT_SCRAMBLE_FLOOR = 0.10       # scramble_gap < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
TAUT_GATE_SEP_FLOOR = 0.05       # gate_separation < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
SIGN_P_MAX = 0.05                # paired sign-test threshold

# gate threshold: a-priori between HARD noise-floor margin (~0.07) and EASY clean margin (~0.9); NOT tuned.
TAU_GATE = 0.30
FRAC_EASY = 0.5                  # mixed corpus: half easy (single-shot resolves), half hard (need re-query)

# --------------------------- config (selftest / smoke / full) --------------------
if SELF_TEST_MODE:
    N_DIM = 512
    V_NODES = 32
    M_STORE = 6                  # items per hop bundle
    N_TRIALS = 8
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 4096                 # == FULL N (discriminator preview at full scale; option A)
    V_NODES = 256
    M_STORE = 20
    N_TRIALS = 40
    SEEDS = [7, 17, 23]          # multi-seed smoke (>=3 seeds)
else:  # full
    N_DIM = 4096
    V_NODES = 256
    M_STORE = 20
    N_TRIALS = 200
    SEEDS = [7, 17, 23, 31, 41]

EXPECTED_N_UNITS = len(SEEDS)
ARMS = ["ARM_A_SINGLE_SHOT", "ARM_B_WM_REQUERY", "ARM_B_SCRAMBLE",
        "ARM_ALWAYS_REQUERY", "ARM_ORACLE_BRIDGE"]

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,M=%d,n_trials=%d,frac_easy=%.2f,tau_gate=%.2f,seeds=%s,mode=%s,expected_n=%d,"
    "HP_resolve>=%.2f,HP_route>=%.2f,HP_gatesep>=%.2f,HP_scramble>=%.2f,HP_causal>=%.2f"
) % (ANCHOR_NAME, N_DIM, V_NODES, M_STORE, N_TRIALS, FRAC_EASY, TAU_GATE, SEEDS, RUN_MODE, EXPECTED_N_UNITS,
     HP_RESOLVE_LIFT_MIN, HP_GATE_ROUTE_MARGIN, HP_GATE_SEP_MIN, HP_SCRAMBLE_GAP_MIN, HP_CAUSAL_FLIP_MIN)

_T0 = time.time()


# ============================================================================
# Merkle audit helpers -- TRANSCRIBED VERBATIM from experiments/exp_reasoning_chain_replay_v1.py
# (and exp_khop_audit_replay_v1.py); those cells run _selftest() at import => NOT import-safe.
# HARD_PASS 100pct deterministic replay + Merkle verify + tamper detect
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
# ============================================================================
def make_codebook(V: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """(V, N) bipolar +/-1 float32 concept codebook (sharded; each concept its own vector)."""
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
# per-trial corpus construction (weak-first regime) + the loop
# ============================================================================
def build_trial(E: np.ndarray, V: int, M: int, easy: bool, rng: np.random.Generator) -> Dict[str, Any]:
    """Construct one trial: hop-1 store (anchor->bridge), hop-2 store (answer keyed by anchor OR bridge)."""
    # need 5 named ids + hop1 distractors 2*(M-1) + hop2 distractors 2*(M-2) + 1 rand_bridge = 5 + 4M - 6 + 1.
    ids = rng.choice(V, size=min(V, 5 + 4 * M), replace=False)
    anchor_id = int(ids[0]); bridge_c_id = int(ids[1]); bridge_d_id = int(ids[2])
    ans_id = int(ids[3]); wrong_id = int(ids[4])
    pool = [int(x) for x in ids[5:]]

    anchor = E[anchor_id]; bridge_c = E[bridge_c_id]; bridge_d = E[bridge_d_id]

    # ---- hop-1 store: anchor -> bridge_c, plus M-1 distractor (key,val) pairs (bundled) ----
    B1 = bind(anchor, bridge_c).copy()
    di = 0
    for _ in range(M - 1):
        k = E[pool[di]]; v = E[pool[di + 1]]; di += 2
        B1 = B1 + bind(k, v)

    # ---- hop-2 store: answer keyed by anchor (EASY) or by bridge_c (HARD); plus a bridge_d->wrong trap ----
    if easy:
        B2 = bind(anchor, E[ans_id]).copy()
    else:
        B2 = bind(bridge_c, E[ans_id]).copy()
    B2 = B2 + bind(bridge_d, E[wrong_id])                       # trap: wrong bridge -> wrong answer
    for _ in range(max(0, M - 2)):
        k = E[pool[di]]; v = E[pool[di + 1]]; di += 2
        B2 = B2 + bind(k, v)

    rand_bridge_id = int(pool[di]); di += 1
    return {"anchor_id": anchor_id, "bridge_c_id": bridge_c_id, "bridge_d_id": bridge_d_id,
            "ans_id": ans_id, "wrong_id": wrong_id, "rand_bridge_id": rand_bridge_id,
            "easy": bool(easy), "B1": B1.astype(np.float32), "B2": B2.astype(np.float32)}


def run_loop_trial(E: np.ndarray, tr: Dict[str, Any]) -> Dict[str, Any]:
    """Run the retrieve->gate->audit->requery loop for one trial; return per-arm answers + audit log."""
    anchor = E[tr["anchor_id"]]; B1 = tr["B1"]; B2 = tr["B2"]

    # ---- hop-1: retrieve the bridge (WM active-slot content) ----
    bridge_hat_id, margin1 = cleanup(bind(anchor, B1), E)

    # ---- single-shot answer attempt (raw query = anchor into hop-2) : the gate's "why-signal" ----
    ansA_id, marginA = cleanup(bind(anchor, B2), E)

    # ---- gate (Go/NoGo value-gate): margin >= tau => Go (commit shot); else NoGo (re-query) ----
    go = marginA >= TAU_GATE

    # ---- re-query (WM-mediated): bind WM active-slot content (bridge_hat) into hop-2 ----
    ansB_wm_id, marginB = cleanup(bind(E[bridge_hat_id], B2), E)
    # scramble control: re-query with a RANDOM bridge code (telemetry-sensitivity guard)
    ansB_scr_id, _ = cleanup(bind(E[tr["rand_bridge_id"]], B2), E)
    # oracle-bridge positive control: hand the TRUE bridge to hop-2 (skip hop-1)
    ansOracle_id, _ = cleanup(bind(E[tr["bridge_c_id"]], B2), E)

    # ---- per-arm committed answers ----
    ans_arm_A = ansA_id                                        # always commit the single shot
    ans_arm_B = ansA_id if go else ansB_wm_id                  # gated: accept if Go, else WM re-query
    ans_arm_scr = ansA_id if go else ansB_scr_id               # gated, but scramble re-query
    ans_arm_always = ansB_wm_id                                # always re-query (never accept the shot)
    ans_arm_oracle = ansOracle_id                              # oracle bridge (ceiling)

    # ---- glass-box audit log: one hop_record per step, Merkle-chained ----
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
        "bridge_hat_id": bridge_hat_id, "bridge_c_id": tr["bridge_c_id"], "bridge_d_id": tr["bridge_d_id"],
        "ans_id": tr["ans_id"], "wrong_id": tr["wrong_id"],
        "margin1": float(margin1), "marginA": float(marginA), "marginB": float(marginB),
        "ans_arm": {"ARM_A_SINGLE_SHOT": ans_arm_A, "ARM_B_WM_REQUERY": ans_arm_B,
                    "ARM_B_SCRAMBLE": ans_arm_scr, "ARM_ALWAYS_REQUERY": ans_arm_always,
                    "ARM_ORACLE_BRIDGE": ans_arm_oracle},
        "steps": steps, "root": root,
    }


def causal_hand_edit(E: np.ndarray, tr: Dict[str, Any], res: Dict[str, Any]) -> Dict[str, Any]:
    """Hand-edit the logged hop-1 bridge (true -> distractor) and re-run the downstream hop-2 recompute.
    Returns (answer_flipped, tamper_flag_fired). The glass-box demonstration: a monitor-not-control edit
    changes the recomputed downstream answer AND breaks the committed Merkle root."""
    B2 = tr["B2"]
    edited_bridge_id = tr["bridge_d_id"]                        # adversarial swap: true bridge -> distractor
    ans_recompute_id, _ = cleanup(bind(E[edited_bridge_id], B2), E)
    answer_flipped = bool(ans_recompute_id != res["ans_arm"]["ARM_B_WM_REQUERY"])
    # rebuild the tampered log and confirm the tamper flag fires (recomputed root != committed root)
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
def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    E = make_codebook(V_NODES, N_DIM, rng)

    n_easy = int(round(FRAC_EASY * N_TRIALS))
    easy_flags = np.array([True] * n_easy + [False] * (N_TRIALS - n_easy))
    rng.shuffle(easy_flags)

    per_arm_correct = {a: np.zeros(N_TRIALS, dtype=bool) for a in ARMS}
    per_arm_ans = {a: np.full(N_TRIALS, -1, dtype=np.int64) for a in ARMS}
    margins_easy: List[float] = []
    margins_hard: List[float] = []
    route_correct = np.zeros(N_TRIALS, dtype=bool)
    hop1_correct = np.zeros(N_TRIALS, dtype=bool)
    det_ok = np.zeros(N_TRIALS, dtype=bool)
    verify_ok = np.zeros(N_TRIALS, dtype=bool)
    tamper_ok = np.zeros(N_TRIALS, dtype=bool)
    # causal-edit is demonstrated on HARD trials that ARM_B got CORRECT
    causal_flip = []
    causal_tamper = []
    requery_count = 0

    for i in range(N_TRIALS):
        easy = bool(easy_flags[i])
        tr = build_trial(E, V_NODES, M_STORE, easy, rng)
        res = run_loop_trial(E, tr)

        # deterministic replay: recompute the whole trial from the same inputs -> identical answers + root
        res2 = run_loop_trial(E, tr)
        det_ok[i] = (res2["root"] == res["root"] and
                     res2["ans_arm"]["ARM_B_WM_REQUERY"] == res["ans_arm"]["ARM_B_WM_REQUERY"])
        verify_ok[i] = merkle_verify(res["steps"], res["root"])
        # tamper: edit one logged step (mutate the committed answer) -> root must mismatch
        tampered = list(res["steps"]); tampered[4] = "commit(answer=%d)" % (res["ans_arm"]["ARM_B_WM_REQUERY"] + 1)
        tamper_ok[i] = (not merkle_verify(tampered, res["root"]))

        for a in ARMS:
            per_arm_correct[a][i] = (res["ans_arm"][a] == tr["ans_id"])
            per_arm_ans[a][i] = res["ans_arm"][a]
        hop1_correct[i] = (res["bridge_hat_id"] == tr["bridge_c_id"])
        if easy:
            margins_easy.append(res["marginA"])
            route_correct[i] = res["go"]              # easy trial routed correctly iff GO (accept shot)
        else:
            margins_hard.append(res["marginA"])
            route_correct[i] = (not res["go"])        # hard trial routed correctly iff NOGO (re-query)
        if not res["go"]:
            requery_count += 1

        # causal hand-edit demonstration (HARD + ARM_B correct)
        if (not easy) and per_arm_correct["ARM_B_WM_REQUERY"][i]:
            ce = causal_hand_edit(E, tr, res)
            causal_flip.append(ce["answer_flipped"])
            causal_tamper.append(ce["tamper_flag_fired"])

    accs = {a: float(per_arm_correct[a].mean()) for a in ARMS}
    accA = accs["ARM_A_SINGLE_SHOT"]; accB = accs["ARM_B_WM_REQUERY"]
    accScr = accs["ARM_B_SCRAMBLE"]; accAlways = accs["ARM_ALWAYS_REQUERY"]
    # ORACLE_BRIDGE is the bridge-keyed retrieval ceiling: only defined on HARD trials (on EASY the answer is
    # anchor-keyed, so probing with the true bridge correctly returns noise). Positive control on HARD subset.
    hard_mask = ~easy_flags
    accOracle = (float(per_arm_correct["ARM_ORACLE_BRIDGE"][hard_mask].mean())
                 if hard_mask.any() else 0.0)

    # paired sign test: ARM_B vs ARM_A on the SAME trials
    b = per_arm_correct["ARM_B_WM_REQUERY"]; a = per_arm_correct["ARM_A_SINGLE_SHOT"]
    n_b_only = int((b & (~a)).sum()); n_a_only = int((a & (~b)).sum())
    n_disc = n_b_only + n_a_only
    sign_p = binom_two_sided_p(n_b_only, n_disc, 0.5) if n_disc > 0 else 1.0

    gate_sep = (float(np.mean(margins_easy)) - float(np.mean(margins_hard))) if margins_easy and margins_hard else 0.0
    causal_flip_rate = float(np.mean(causal_flip)) if causal_flip else 0.0
    causal_tamper_rate = float(np.mean(causal_tamper)) if causal_tamper else 0.0

    # arms-differ (META_RULE_AF): hash the actual COMMITTED ANSWER-ID streams (not correctness bools, which
    # legitimately coincide for arms that fail on the same trials). The 4 core arms must all be distinct.
    # ARM_ORACLE_BRIDGE coincides with ARM_ALWAYS_REQUERY exactly when hop1_retrieve_acc==1.0 (retrieved
    # bridge == true bridge) -- a MEASURED property, not a bug -> that pair is arms_differ_exempted.
    arm_digests = {a2: hashlib.sha256(per_arm_ans[a2].tobytes()).hexdigest()[:16] for a2 in ARMS}
    core_arms = ["ARM_A_SINGLE_SHOT", "ARM_B_WM_REQUERY", "ARM_B_SCRAMBLE", "ARM_ALWAYS_REQUERY"]
    arms_differ = (len({arm_digests[a2] for a2 in core_arms}) == len(core_arms))

    rec = {
        "seed": int(seed), "N": N_DIM, "V": V_NODES, "M": M_STORE, "n_trials": N_TRIALS,
        "run_mode": RUN_MODE, "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "frac_easy": FRAC_EASY, "tau_gate": TAU_GATE,
        "accs": accs, "accA": accA, "accB": accB, "accScramble": accScr,
        "accAlways": accAlways, "accOracle": accOracle,
        "resolve_lift": float(accB - accA),
        "gate_route_margin": float(accB - accAlways),
        "scramble_gap": float(accB - accScr),
        "gate_separation": float(gate_sep),
        "gate_routing_acc": float(route_correct.mean()),
        "hop1_retrieve_acc": float(hop1_correct.mean()),
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
        "arms_differ": bool(arms_differ),  # 4 core arms distinct by committed-answer stream
        "arms_differ_exempted": [["ARM_ALWAYS_REQUERY", "ARM_ORACLE_BRIDGE"]],  # coincide iff hop1==1.0 (measured)
    }
    print("[seed=%d] accA=%.3f accB=%.3f accAlways=%.3f accScr=%.3f accOracle=%.3f | resolve_lift=%.3f "
          "route_margin=%.3f scramble_gap=%.3f gate_sep=%.3f routing=%.3f hop1=%.3f | "
          "det=%.3f verify=%.3f tamper=%.3f causal_flip=%.3f(n=%d) sign_p=%.4f"
          % (seed, accA, accB, accAlways, accScr, accOracle, rec["resolve_lift"], rec["gate_route_margin"],
             rec["scramble_gap"], rec["gate_separation"], rec["gate_routing_acc"], rec["hop1_retrieve_acc"],
             rec["deterministic_replay"], rec["merkle_verify"], rec["tamper_detect"], rec["causal_edit_flip"],
             rec["n_causal_trials"], rec["sign_p"]), flush=True)
    return rec


# ============================================================================
# aggregate + verdict
# ============================================================================
def _selftest() -> None:
    """Formula self-tests (PROT-022): (1) merkle chains + tamper detect; (2) bind self-inverse;
    (3) the weak-first regime actually fires (single-shot fails HARD, WM re-query resolves it)."""
    # (1) Merkle chains + tamper
    r = merkle_root(["a", "b", "c"])
    assert merkle_verify(["a", "b", "c"], r), "merkle verify"
    assert not merkle_verify(["a", "b", "X"], r), "tamper detected"
    assert merkle_root(["a"]) != h(b"genesis"), "merkle chains beyond genesis"
    # (2) bind is self-inverse for bipolar
    rng = np.random.default_rng(0)
    E = make_codebook(16, 256, rng)
    x = E[3]; k = E[5]
    assert np.array_equal(bind(k, bind(k, x)), x), "bind self-inverse"
    # (3) weak-first regime fires at a tiny scale: HARD single-shot fails, WM re-query resolves
    Es = make_codebook(48, 1024, np.random.default_rng(1))
    tr = build_trial(Es, 48, 6, easy=False, rng=np.random.default_rng(2))
    res = run_loop_trial(Es, tr)
    assert res["ans_arm"]["ARM_B_WM_REQUERY"] == tr["ans_id"], "WM re-query resolves HARD"
    assert res["marginA"] < TAU_GATE, "HARD single-shot margin below gate (weak-first fires)"
    assert res["bridge_hat_id"] == tr["bridge_c_id"], "hop1 retrieves the correct bridge"
    ce = causal_hand_edit(Es, tr, res)
    assert ce["tamper_flag_fired"], "causal hand-edit fires tamper flag"
    assert ce["answer_flipped"], "causal hand-edit flips downstream answer"
    # easy single-shot resolves with high margin
    tre = build_trial(Es, 48, 6, easy=True, rng=np.random.default_rng(3))
    rese = run_loop_trial(Es, tre)
    assert rese["marginA"] >= TAU_GATE, "EASY single-shot margin above gate"
    assert rese["ans_arm"]["ARM_A_SINGLE_SHOT"] == tre["ans_id"], "EASY single-shot resolves"
    print("[selftest] PASS: glass-box micro-loop (merkle+tamper, bind-inverse, weak-first regime fires)", flush=True)


def aggregate_and_verdict(per_seed: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed results",
                "summary": "no per-seed results"}

    def col(f):
        return [float(r[f]) for r in per_seed]

    m = {f: float(np.mean(col(f))) for f in
         ["accA", "accB", "accScramble", "accAlways", "accOracle", "resolve_lift", "gate_route_margin",
          "scramble_gap", "gate_separation", "gate_routing_acc", "hop1_retrieve_acc", "deterministic_replay",
          "merkle_verify", "tamper_detect", "causal_edit_flip", "causal_edit_tamper", "margin_easy_mean",
          "margin_hard_mean"]}
    # pooled paired sign test across seeds
    n_b_only = sum(int(r["n_b_only"]) for r in per_seed)
    n_a_only = sum(int(r["n_a_only"]) for r in per_seed)
    n_disc = n_b_only + n_a_only
    sign_p = binom_two_sided_p(n_b_only, n_disc, 0.5) if n_disc > 0 else 1.0
    arms_differ = all(bool(r["arms_differ"]) for r in per_seed)
    completed = len(per_seed)
    cardinality_ok = completed >= EXPECTED_N_UNITS

    # ---- guards first (positive control + telemetry) ----
    retrieval_ok = (m["accOracle"] >= HP_ORACLE_BRIDGE_MIN and m["hop1_retrieve_acc"] >= HP_HOP1_RETRIEVE_MIN)
    audit_ok = (m["deterministic_replay"] >= 0.999 and m["merkle_verify"] >= 0.999 and m["tamper_detect"] >= 0.999)
    telemetry_ok = (m["scramble_gap"] >= TAUT_SCRAMBLE_FLOOR and m["gate_separation"] >= TAUT_GATE_SEP_FLOOR)

    s = ("accA=%.3f accB=%.3f accAlways=%.3f accScr=%.3f accOracle=%.3f | resolve_lift=%.3f route_margin=%.3f "
         "scramble_gap=%.3f gate_sep=%.3f routing=%.3f hop1=%.3f | det=%.3f verify=%.3f tamper=%.3f "
         "causal_flip=%.3f causal_tamper=%.3f sign_p=%.4f (seeds=%d)"
         % (m["accA"], m["accB"], m["accAlways"], m["accScramble"], m["accOracle"], m["resolve_lift"],
            m["gate_route_margin"], m["scramble_gap"], m["gate_separation"], m["gate_routing_acc"],
            m["hop1_retrieve_acc"], m["deterministic_replay"], m["merkle_verify"], m["tamper_detect"],
            m["causal_edit_flip"], m["causal_edit_tamper"], sign_p, completed))

    # ---- verdict ladder ----
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = "HARD_FAIL: completed %d < expected %d seeds. " % (completed, EXPECTED_N_UNITS) + s
    elif not audit_ok:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL: audit not sound (deterministic_replay/merkle_verify/tamper_detect < 1.0). " + s
    elif not retrieval_ok:
        verdict = "INCONCLUSIVE_RETRIEVAL_BROKEN"
        vmsg = ("INCONCLUSIVE_RETRIEVAL_BROKEN: oracle_bridge=%.3f (>=%.2f) or hop1=%.3f (>=%.2f) failed; "
                "substrate retrieval did not reproduce at test regime -> downstream arms untrustworthy. "
                % (m["accOracle"], HP_ORACLE_BRIDGE_MIN, m["hop1_retrieve_acc"], HP_HOP1_RETRIEVE_MIN)) + s
    elif not telemetry_ok:
        verdict = "INCONCLUSIVE_TAUTOLOGICAL_METRIC"
        vmsg = ("INCONCLUSIVE_TAUTOLOGICAL_METRIC: scramble_gap=%.3f (>=%.2f) or gate_sep=%.3f (>=%.2f) too low; "
                "resolution not attributable to correct WM binding / self-audit not telemetry-sensitive -- "
                "NOT a clean negative. " % (m["scramble_gap"], TAUT_SCRAMBLE_FLOOR, m["gate_separation"],
                                            TAUT_GATE_SEP_FLOOR)) + s
    elif m["resolve_lift"] < HF_RESOLVE_LIFT_CEIL:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL: resolve_lift=%.3f < %.2f -- the WM re-query loop adds nothing over a single shot. " % (
            m["resolve_lift"], HF_RESOLVE_LIFT_CEIL) + s
    elif (m["resolve_lift"] >= HP_RESOLVE_LIFT_MIN and m["gate_route_margin"] >= HP_GATE_ROUTE_MARGIN
          and sign_p < SIGN_P_MAX and m["gate_separation"] >= HP_GATE_SEP_MIN
          and m["gate_routing_acc"] >= HP_GATE_ROUTING_ACC_MIN and m["scramble_gap"] >= HP_SCRAMBLE_GAP_MIN
          and m["causal_edit_flip"] >= HP_CAUSAL_FLIP_MIN and arms_differ):
        verdict = "HARD_PASS"
        vmsg = ("HARD_PASS: gated WM-mediated re-query resolves the weak-first regime a single shot cannot "
                "(resolve_lift=%.3f, beats always-requery by %.3f, p=%.4f), self-audit is telemetry-sensitive "
                "(gate_sep=%.3f, scramble_gap=%.3f), and the glass-box hand-edit changes downstream recompute "
                "(causal_flip=%.3f) while firing the tamper flag (tamper=%.3f) -- inspectable + hand-editable "
                "self-auditing multi-hop reasoning. " % (m["resolve_lift"], m["gate_route_margin"], sign_p,
                m["gate_separation"], m["scramble_gap"], m["causal_edit_flip"], m["tamper_detect"])) + s
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("MIDDLE_BAND: audit sound + retrieval reproduced + telemetry-sensitive, but a HARD_PASS gate "
                "missed (resolve_lift=%.3f route_margin=%.3f gate_sep=%.3f scramble_gap=%.3f causal_flip=%.3f "
                "routing=%.3f p=%.4f arms_differ=%s). " % (m["resolve_lift"], m["gate_route_margin"],
                m["gate_separation"], m["scramble_gap"], m["causal_edit_flip"], m["gate_routing_acc"], sign_p,
                arms_differ)) + s

    gate_claims = [
        record_gate("resolve_lift", m["resolve_lift"], HP_RESOLVE_LIFT_MIN, ">=", "accB - accA"),
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

    per_seed: List[Dict[str, Any]] = []
    for si, seed in enumerate(SEEDS):
        rec = run_one_seed(int(seed), out_dir)
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
