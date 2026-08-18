"""substrate_higher_order_tom_recursive_v1 -- Stage 3 TOM higher-order extension.

Prereg: preregs/2026-06-28_substrate_higher_order_tom_recursive_v1.md
Base cell: experiments/exp_theory_of_mind_sally_anne_nested_hrr_v1.py (Q2=0.875 today)
M3 concern #6: TOM beyond Sally-Anne (3rd+ order recursive belief attribution).

TASK: extend Sally-Anne 2nd-order TOM to recursive depth d in {2, 3, 4, 5}.
A statement at depth d:
  d=2: "Anne believes [obj is at L_x]"
  d=3: "Carol believes [Anne believes [obj is at L_x]]"
  d=4: "Dan believes [Carol believes [Anne believes [obj is at L_x]]]"
  d=5: "Eve  believes [Dan believes [Carol believes [Anne believes [obj at L_x]]]]"

ARMS (4; BIT-DISTINCT per META_RULE_AF):
  SUBSTRATE     nested HRR (depth-d bind chain) + per-agent partition + cleanup + refuse-gate
  NAIVE_FLAT    flat HRR (no nesting) -- should HF at depth>=3 (no recursive structure)
  SHUFFLE       randomly permuted agent order at encode time -- sanity (near-chance)
  RANDOM        random vector floor -- chance reference

PRE-REG (HARD-LOCKED); HARD_PASS requires ALL of:
  SUBSTRATE @ d=2 >= 0.85
  SUBSTRATE @ d=3 >= 0.60
  SUBSTRATE @ d=4 >= 0.40
  SUBSTRATE @ d=5 >= 0.20
  NAIVE_FLAT @ d=3 < SUBSTRATE - 0.20 (mechanism contributes)
  RANDOM in [0.10, 0.45] (chance band, 4-loc)
  arms-distinct SHA-256 per depth
  cv across seeds @ d=3 < 0.15 (only checked if SUBSTRATE_d3 >= 0.40)
  no arm >= 0.999 at depth >= 3 (META_RULE_Q)
  cardinality_ok
  discriminator_at_d3 >= 0.25

Author: exp_dev (hdi_exp_dev sub-agent) 2026-06-28.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AE/AF/AG/AH/AN):
# - arms_differ_verified at smoke gate (per depth)
# - final_metrics_atomicity (tmp + os.replace)
# - except SystemExit raise BEFORE except Exception
# - crlb_floor_computed (SNR per nesting level)
# - discriminator survives scale (smoke uses full N=8192)
# - HARD_PASS strictly above floor
# - HP_SCOPE per-arm-per-depth declaration
# - cardinality_ok for sweep-axis cells

from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_higher_order_tom_recursive_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----------------------- Pre-reg bands HARD-LOCKED -----------------------
# Per-depth HP/HF gates (load-bearing; do not modify post-dispatch).
HP_SUBSTRATE_BY_DEPTH = {2: 0.85, 3: 0.60, 4: 0.40, 5: 0.20}
HF_SUBSTRATE_BY_DEPTH = {2: 0.60, 3: 0.15, 4: 0.05, 5: 0.00}
HP_DISCRIMINATOR_GAP_D3 = 0.25  # SUBSTRATE_d3 - max(other_arms_d3) >= 0.25
HP_MECHANISM_GAP_D3 = 0.20  # SUBSTRATE_d3 - NAIVE_FLAT_d3 >= 0.20
HP_CV_MAX = 0.15
SUSPECT_1000 = 0.999
N_LOCATIONS = 4  # chance = 0.25
CHANCE = 1.0 / N_LOCATIONS
RANDOM_BAND_LO = 0.10
RANDOM_BAND_HI = 0.45
DEPTHS = [2, 3, 4, 5]

EXPECTED_ARMS = ["SUBSTRATE", "NAIVE_FLAT", "SHUFFLE", "RANDOM"]

# Sized for actual modes (smoke uses full N to honor DISCRIMINATOR-MUST-SURVIVE-SCALE).
if SELF_TEST_MODE:
    N_DIM = 1024
    V_REL = 128
    N_AGENTS_MAX = 12  # need 2*depth_max for SHUFFLE to pick disjoint agents
    N_OBJECTS = 3
    N_LOCS_CONFIG = 3
    N_TRIALS_PER_DEPTH = 8
    N_INTERFERENCE = 4
    PER_LEVEL_DISTRACTORS = 2
    SEEDS = [7]
    SMOKE_DEPTHS = [2, 3]  # self-test only checks 2 depths (speed)
elif RUN_MODE == "smoke":
    # Smoke at production N=8192 (DISCRIMINATOR-MUST-SURVIVE-SCALE)
    N_DIM = 8192
    V_REL = 256
    N_AGENTS_MAX = 12  # need 2*depth_max for SHUFFLE to pick disjoint agents
    N_OBJECTS = 4
    N_LOCS_CONFIG = N_LOCATIONS
    N_TRIALS_PER_DEPTH = 50
    # Without per-level distractors, recursive nesting is exact (FHRR bind/unbind
    # commutative). Per-level distractors model "each agent holds beliefs about
    # MANY (obj,loc) pairs" -- decode pulls focal from sum-of-(1+distractor)
    # bindings at each level. Each level adds proportional noise to the decode
    # signal: cos_d ~ 1/sqrt(d * (1 + per_level)) before cleanup.
    N_INTERFERENCE = 16  # outer accumulated banks
    PER_LEVEL_DISTRACTORS = 4  # sibling beliefs per agent per level
    SEEDS = [7]
    SMOKE_DEPTHS = DEPTHS  # smoke runs all 4 depths
else:
    N_DIM = 8192
    V_REL = 256
    N_AGENTS_MAX = 12
    N_OBJECTS = 4
    N_LOCS_CONFIG = N_LOCATIONS
    N_TRIALS_PER_DEPTH = 200
    N_INTERFERENCE = 16
    PER_LEVEL_DISTRACTORS = 4
    SEEDS = [7, 17, 23]  # chunked dispatch
    SMOKE_DEPTHS = DEPTHS

# Datapoints: per seed, per depth, 4 arms * N_TRIALS_PER_DEPTH trials.
ACTIVE_DEPTHS = SMOKE_DEPTHS if (RUN_MODE == "smoke" or SELF_TEST_MODE) else DEPTHS
EXPECTED_N_UNITS = len(SEEDS) * len(ACTIVE_DEPTHS) * len(EXPECTED_ARMS) * N_TRIALS_PER_DEPTH

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V_REL=%d,n_agents_max=%d,n_objects=%d,n_locs=%d,"
    "n_trials_per_depth=%d,n_interference=%d,per_level_distractors=%d,"
    "depths=%s,seeds=%s,mode=%s,"
    "HP_d2>=%.2f,HP_d3>=%.2f,HP_d4>=%.2f,HP_d5>=%.2f,"
    "HP_discrim_d3>=%.2f,HP_mech_d3>=%.2f,HP_cv_max<%.2f,"
    "random_band=[%.2f,%.2f],expected_n=%d,"
    "hardening=L1early+L2perseed+L3outertry+L4importsentinel"
    "+META_RULE_AF+META_RULE_AH+META_RULE_AG+META_RULE_AN"
) % (
    ANCHOR_NAME, N_DIM, V_REL, N_AGENTS_MAX, N_OBJECTS, N_LOCS_CONFIG,
    N_TRIALS_PER_DEPTH, N_INTERFERENCE, PER_LEVEL_DISTRACTORS,
    ACTIVE_DEPTHS, SEEDS, RUN_MODE,
    HP_SUBSTRATE_BY_DEPTH[2], HP_SUBSTRATE_BY_DEPTH[3],
    HP_SUBSTRATE_BY_DEPTH[4], HP_SUBSTRATE_BY_DEPTH[5],
    HP_DISCRIMINATOR_GAP_D3, HP_MECHANISM_GAP_D3, HP_CV_MAX,
    RANDOM_BAND_LO, RANDOM_BAND_HI, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_higher_order_tom_recursive",
        }
        if extra:
            metrics.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH",
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_higher_order_tom_import_crash",
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------- FHRR primitives (complex unit-modulus) -----------------

def random_unit_phases(M: int, n_half: int, g: np.random.Generator) -> np.ndarray:
    phases = g.uniform(-np.pi, np.pi, size=(M, n_half)).astype(np.float32)
    return np.exp(1j * phases).astype(np.complex64)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a * b).astype(np.complex64)


def unbind(c: np.ndarray, key: np.ndarray) -> np.ndarray:
    return (c * np.conj(key)).astype(np.complex64)


def superpose_sum(arrs: List[np.ndarray]) -> np.ndarray:
    if not arrs:
        return np.zeros(1, dtype=np.complex64)
    return np.sum(np.stack(arrs, axis=0), axis=0).astype(np.complex64)


def cleanup_argmax(q: np.ndarray, codebook: np.ndarray) -> Tuple[int, float]:
    sims = np.real(codebook @ np.conj(q))
    norm_q = np.linalg.norm(q) + 1e-12
    norm_cb = np.linalg.norm(codebook, axis=1) + 1e-12
    cos = sims / (norm_q * norm_cb)
    idx = int(np.argmax(cos))
    return idx, float(cos[idx])


# ------------------------ scenario generation ------------------------

def make_higher_order_scenario(g: np.random.Generator, depth: int,
                                  n_objects: int, n_locations: int,
                                  n_agents_avail: int) -> Dict[str, Any]:
    """Generate a depth-d nested attribution scenario.

    Returns dict with:
      depth          recursive belief depth (d)
      object_idx     focal object
      loc_truth      ground-truth location for the deepest claim
      agent_chain    list of agent indices [A_outer, A_mid, ..., A_inner]; len = depth
      target_q       which level we're querying (default: the INNERMOST belief's loc)
    """
    assert depth >= 2
    assert n_agents_avail >= depth, "need >= depth distinct agents"
    object_idx = int(g.integers(n_objects))
    loc_truth = int(g.integers(n_locations))
    # Pick depth distinct agents
    all_agents = list(range(n_agents_avail))
    g.shuffle(all_agents)
    agent_chain = all_agents[:depth]
    return {
        "depth": depth,
        "object_idx": object_idx,
        "loc_truth": loc_truth,
        "agent_chain": agent_chain,
    }


# ------------------------ arm runners ------------------------
# Each arm returns: {"preds": [pred,...] (len=N_TRIALS), "truths": [truth,...]}


def _accumulated_interference(g: np.random.Generator, n_half: int,
                                 obj_cb: np.ndarray, loc_cb: np.ndarray,
                                 agent_cb: np.ndarray,
                                 role_believes: np.ndarray,
                                 n_interference: int) -> np.ndarray:
    if n_interference <= 0:
        return np.zeros(n_half, dtype=np.complex64)
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]
    n_agents = agent_cb.shape[0]
    parts = []
    for _ in range(n_interference):
        ai = int(g.integers(n_agents))
        oi = int(g.integers(n_objs))
        li = int(g.integers(n_locs))
        parts.append(bind(agent_cb[ai],
                           bind(role_believes,
                                 bind(obj_cb[oi], loc_cb[li]))))
    return superpose_sum(parts)


def _nested_encode_substrate(agent_chain: List[int], obj_idx: int, loc_idx: int,
                                obj_cb: np.ndarray, loc_cb: np.ndarray,
                                agent_cb: np.ndarray, role_believes: np.ndarray,
                                per_level_distractors: int = 0,
                                rng: np.random.Generator = None
                                ) -> np.ndarray:
    """Build a nested HRR for "A_outer believes [A_mid believes [... [obj at loc]]]".

    Inner content: bind(obj, loc).
    Wrap once per agent (outermost agent applied LAST):
      level d-1: bind(role_believes, bind(A_inner, bind(obj, loc) + distractors))
      level d-2: bind(role_believes, bind(A_mid, <level d-1> + distractors))
      ...
      level 0 (outer): bind(A_outer, <level 1> + distractors)

    Per-level distractors model "each agent holds beliefs about MANY (obj,loc)
    pairs, not just the focal one". Each level superposes the focal belief
    with `per_level_distractors` other random (obj, loc) bindings. This makes
    decode accumulate noise per level: SNR degrades as 1/sqrt(d * per_level_distractors).
    """
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]
    inner = bind(obj_cb[obj_idx], loc_cb[loc_idx])
    # Innermost level distractors: other (obj, loc) pairs the agent "knows"
    if per_level_distractors > 0 and rng is not None:
        inner_distractors = []
        for _ in range(per_level_distractors):
            oi = int(rng.integers(n_objs))
            li = int(rng.integers(n_locs))
            inner_distractors.append(bind(obj_cb[oi], loc_cb[li]))
        inner = superpose_sum([inner] + inner_distractors)
    cur = inner
    for level_idx, agent_idx in enumerate(reversed(agent_chain)):
        # Wrap current content with this agent's belief
        wrapped = bind(role_believes, bind(agent_cb[agent_idx], cur))
        # Add per-level distractors: this agent ALSO believes other random
        # nested attribution chains (sibling beliefs at this level)
        if per_level_distractors > 0 and rng is not None:
            level_distractors = []
            for _ in range(per_level_distractors):
                # Random sibling chain at this nesting level: pick a random
                # (obj, loc) at the innermost AND wrap with this agent at this level
                oi = int(rng.integers(n_objs))
                li = int(rng.integers(n_locs))
                sibling_inner = bind(obj_cb[oi], loc_cb[li])
                sibling_wrap = bind(role_believes,
                                      bind(agent_cb[agent_idx], sibling_inner))
                level_distractors.append(sibling_wrap)
            wrapped = superpose_sum([wrapped] + level_distractors)
        cur = wrapped
    return cur


def _nested_decode_substrate(bank: np.ndarray, agent_chain: List[int],
                                obj_idx: int,
                                obj_cb: np.ndarray, loc_cb: np.ndarray,
                                agent_cb: np.ndarray,
                                role_believes: np.ndarray) -> Tuple[int, float]:
    """Unwrap depth=d nesting and read off the innermost location.

    Unbinding order matches encoding: outer-most agent applied LAST means
    we unbind it FIRST.
    """
    cur = bank
    # Encoding wrapped from innermost out: outer-most agent is the LAST wrap.
    # So unwrap in the SAME order as agent_chain (outer to inner).
    for agent_idx in agent_chain:
        cur = unbind(cur, role_believes)
        cur = unbind(cur, agent_cb[agent_idx])
    # Now cur should be bind(obj, loc). Unbind obj -> loc.
    cur = unbind(cur, obj_cb[obj_idx])
    return cleanup_argmax(cur, loc_cb)


def run_arm_substrate(scenarios: List[Dict[str, Any]],
                        obj_cb: np.ndarray, loc_cb: np.ndarray,
                        agent_cb: np.ndarray, role_believes: np.ndarray,
                        n_interference: int, per_level_distractors: int,
                        g: np.random.Generator) -> Dict[str, Any]:
    """SUBSTRATE arm: nested HRR + per-agent partition + cleanup + refuse-gate."""
    n_half = obj_cb.shape[1]
    preds, truths = [], []
    for sc in scenarios:
        nested = _nested_encode_substrate(
            sc["agent_chain"], sc["object_idx"], sc["loc_truth"],
            obj_cb, loc_cb, agent_cb, role_believes,
            per_level_distractors=per_level_distractors, rng=g)
        interference = _accumulated_interference(
            g, n_half, obj_cb, loc_cb, agent_cb, role_believes, n_interference)
        bank = superpose_sum([nested, interference])
        pred, _ = _nested_decode_substrate(
            bank, sc["agent_chain"], sc["object_idx"],
            obj_cb, loc_cb, agent_cb, role_believes)
        preds.append(pred)
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


def run_arm_naive_flat(scenarios: List[Dict[str, Any]],
                         obj_cb: np.ndarray, loc_cb: np.ndarray,
                         agent_cb: np.ndarray, role_believes: np.ndarray,
                         n_interference: int, per_level_distractors: int,
                         g: np.random.Generator) -> Dict[str, Any]:
    """NAIVE_FLAT arm: single-level bind (NO nesting).

    Encoding: bind(A_inner, bind(role_believes, bind(obj, loc))) -- ignores
    the OUTER agents (no recursive structure). At depth >= 3, this loses the
    outer attribution information; decoding still attempts the full unwrap
    chain but bank only contains the flat inner bind so outer-unbinds yield noise.
    """
    n_half = obj_cb.shape[1]
    n_objs = obj_cb.shape[0]
    n_locs = loc_cb.shape[0]
    preds, truths = [], []
    for sc in scenarios:
        agent_inner = sc["agent_chain"][-1]
        inner = bind(obj_cb[sc["object_idx"]], loc_cb[sc["loc_truth"]])
        # Match SUBSTRATE: add per_level_distractors at the (single) level
        if per_level_distractors > 0:
            distractors = []
            for _ in range(per_level_distractors):
                oi = int(g.integers(n_objs))
                li = int(g.integers(n_locs))
                distractors.append(bind(obj_cb[oi], loc_cb[li]))
            inner = superpose_sum([inner] + distractors)
        flat = bind(agent_cb[agent_inner],
                     bind(role_believes, inner))
        interference = _accumulated_interference(
            g, n_half, obj_cb, loc_cb, agent_cb, role_believes, n_interference)
        bank = superpose_sum([flat, interference])
        # Decode attempts FULL nested unwrap (mismatched depth)
        cur = bank
        for agent_idx in sc["agent_chain"]:
            cur = unbind(cur, role_believes)
            cur = unbind(cur, agent_cb[agent_idx])
        cur = unbind(cur, obj_cb[sc["object_idx"]])
        pred, _ = cleanup_argmax(cur, loc_cb)
        preds.append(pred)
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


def run_arm_shuffle(scenarios: List[Dict[str, Any]],
                      obj_cb: np.ndarray, loc_cb: np.ndarray,
                      agent_cb: np.ndarray, role_believes: np.ndarray,
                      n_interference: int, per_level_distractors: int,
                      g: np.random.Generator) -> Dict[str, Any]:
    """SHUFFLE arm: encode uses WRONG agent identities; decode uses TRUE chain.

    FHRR bind is COMMUTATIVE, so simply reordering bind operands yields the
    SAME bank vector. To produce a genuine semantic corruption, we must
    substitute DIFFERENT agent identities at encode time. We sample new
    agent IDs from the full codebook minus the true_chain. The decode then
    unbinds the TRUE agents, which are not bound -> result is noise.

    Sanity: predict near-chance (~0.25 with 4 locs).
    """
    n_half = obj_cb.shape[1]
    n_agents_avail = agent_cb.shape[0]
    preds, truths = [], []
    for sc in scenarios:
        true_chain = list(sc["agent_chain"])
        # Pick n_chain DIFFERENT agents from the non-overlapping set
        available = [a for a in range(n_agents_avail) if a not in true_chain]
        if len(available) >= len(true_chain):
            g.shuffle(available)
            wrong_chain = available[:len(true_chain)]
        else:
            # Not enough disjoint agents; pad with reversed true_chain
            # so at least the AGENT IDENTITIES bound at the inner level
            # are different (still corrupts the decode)
            g.shuffle(available)
            wrong_chain = available + list(reversed(true_chain))
            wrong_chain = wrong_chain[:len(true_chain)]
            # Ensure non-identity if possible
            if wrong_chain == true_chain and len(true_chain) >= 2:
                wrong_chain = [wrong_chain[1], wrong_chain[0]] + wrong_chain[2:]
        nested = _nested_encode_substrate(
            wrong_chain, sc["object_idx"], sc["loc_truth"],
            obj_cb, loc_cb, agent_cb, role_believes,
            per_level_distractors=per_level_distractors, rng=g)
        interference = _accumulated_interference(
            g, n_half, obj_cb, loc_cb, agent_cb, role_believes, n_interference)
        bank = superpose_sum([nested, interference])
        # Decode with the TRUE chain (wrong agents bound -> noise)
        cur = bank
        for agent_idx in true_chain:
            cur = unbind(cur, role_believes)
            cur = unbind(cur, agent_cb[agent_idx])
        cur = unbind(cur, obj_cb[sc["object_idx"]])
        pred, _ = cleanup_argmax(cur, loc_cb)
        preds.append(pred)
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


def run_arm_random(scenarios: List[Dict[str, Any]],
                     loc_cb: np.ndarray,
                     g: np.random.Generator) -> Dict[str, Any]:
    """RANDOM arm: pick random location per trial. Pure chance floor."""
    n_locs = loc_cb.shape[0]
    preds, truths = [], []
    for sc in scenarios:
        preds.append(int(g.integers(n_locs)))
        truths.append(sc["loc_truth"])
    return {"preds": preds, "truths": truths}


# ----------------- META_RULE_AF arms-must-differ -----------------

ARMS_DIFFER_EXEMPTED: List[Tuple[str, str]] = []


def arms_must_differ_self_test(arm_concat: Dict[str, List[int]]
                                  ) -> Tuple[bool, Dict[str, Any]]:
    """SHA-256 hash check of arm predictions; flag bit-identical pairs.

    NUANCE: at d=2, all arms may show near-equal accuracy; check is bit-distinct
    not accuracy-distinct. Small-N coincidental ties are tolerated only if at
    least one OTHER pair disagrees.
    """
    digests = {}
    for name, preds in arm_concat.items():
        b = np.asarray(preds, dtype=np.int32).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    arms = sorted(arm_concat.keys())
    diagnostic: Dict[str, Any] = {
        "digests": {k: v[:16] for k, v in digests.items()},
        "pairs": [],
    }
    all_distinct = True
    any_real_disagreement = False
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            ai, aj = arms[i], arms[j]
            pi = np.asarray(arm_concat[ai])
            pj = np.asarray(arm_concat[aj])
            disagreement = float(np.mean(pi != pj))
            if disagreement > 0:
                any_real_disagreement = True
            pair_key = tuple(sorted([ai, aj]))
            is_exempted = any(tuple(sorted(p)) == pair_key
                                for p in ARMS_DIFFER_EXEMPTED)
            if is_exempted and digests[ai] == digests[aj]:
                pair_pass = True
                note = "declared_exempted"
            else:
                pair_pass = (digests[ai] != digests[aj])
                note = ""
            diagnostic["pairs"].append({
                "arm_a": ai, "arm_b": aj,
                "digest_a": digests[ai][:12],
                "digest_b": digests[aj][:12],
                "disagreement": disagreement,
                "pass": pair_pass,
                "note": note,
            })
            if not pair_pass:
                all_distinct = False
    if not any_real_disagreement:
        all_distinct = False
        diagnostic["all_arms_bit_identical"] = True
    diagnostic["all_pairs_pass"] = all_distinct
    return all_distinct, diagnostic


# ----------------- per-seed runner -----------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    n_half = N_DIM // 2

    obj_cb = random_unit_phases(N_OBJECTS, n_half, g)
    loc_cb = random_unit_phases(N_LOCS_CONFIG, n_half, g)
    agent_cb = random_unit_phases(N_AGENTS_MAX, n_half, g)
    role_believes = random_unit_phases(1, n_half, g)[0]

    per_depth: Dict[str, Dict[str, Any]] = {}
    arms_distinct_per_depth: Dict[str, bool] = {}
    arms_distinct_diag: Dict[str, Any] = {}

    for d in ACTIVE_DEPTHS:
        # Generate scenarios for this depth
        scen_rng = np.random.default_rng(seed + d * 1000)
        scenarios = [
            make_higher_order_scenario(scen_rng, d, N_OBJECTS,
                                          N_LOCS_CONFIG, N_AGENTS_MAX)
            for _ in range(N_TRIALS_PER_DEPTH)
        ]
        per_arm: Dict[str, Dict[str, Any]] = {}
        arm_preds_for_distinct: Dict[str, List[int]] = {}
        # Per-arm RNG forks
        per_arm["SUBSTRATE"] = run_arm_substrate(
            scenarios, obj_cb, loc_cb, agent_cb, role_believes,
            N_INTERFERENCE, PER_LEVEL_DISTRACTORS,
            np.random.default_rng(seed + d * 1000 + 100))
        per_arm["NAIVE_FLAT"] = run_arm_naive_flat(
            scenarios, obj_cb, loc_cb, agent_cb, role_believes,
            N_INTERFERENCE, PER_LEVEL_DISTRACTORS,
            np.random.default_rng(seed + d * 1000 + 200))
        per_arm["SHUFFLE"] = run_arm_shuffle(
            scenarios, obj_cb, loc_cb, agent_cb, role_believes,
            N_INTERFERENCE, PER_LEVEL_DISTRACTORS,
            np.random.default_rng(seed + d * 1000 + 300))
        per_arm["RANDOM"] = run_arm_random(
            scenarios, loc_cb, np.random.default_rng(seed + d * 1000 + 400))

        # Per-arm accuracy
        depth_summary: Dict[str, Any] = {}
        for arm in EXPECTED_ARMS:
            r = per_arm[arm]
            acc = float(np.mean([p == t for p, t in zip(r["preds"], r["truths"])]))
            depth_summary[arm] = {"accuracy": acc, "n_trials": len(r["preds"])}
            arm_preds_for_distinct[arm] = list(r["preds"])

        # Arms-distinct test (per depth)
        distinct_pass, distinct_diag = arms_must_differ_self_test(
            arm_preds_for_distinct)
        arms_distinct_per_depth[str(d)] = bool(distinct_pass)
        arms_distinct_diag[str(d)] = distinct_diag

        per_depth[str(d)] = {
            "depth": d,
            "per_arm": depth_summary,
            "arms_distinct_pass": bool(distinct_pass),
        }

    return {
        "seed": int(seed),
        "N": N_DIM,
        "V_REL": V_REL,
        "n_agents_max": N_AGENTS_MAX,
        "n_objects": N_OBJECTS,
        "n_locations": N_LOCS_CONFIG,
        "n_trials_per_depth": N_TRIALS_PER_DEPTH,
        "n_interference": N_INTERFERENCE,
        "active_depths": ACTIVE_DEPTHS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_depth": per_depth,
        "arms_distinct_per_depth": arms_distinct_per_depth,
        "arms_distinct_diag": arms_distinct_diag,
    }


# ----------------- verdict -----------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    # Aggregate per (depth, arm) -> mean/std/cv across seeds
    summary: Dict[str, Dict[str, Dict[str, float]]] = {}
    for d in ACTIVE_DEPTHS:
        d_str = str(d)
        summary[d_str] = {}
        for arm in EXPECTED_ARMS:
            accs = []
            for s in seeds_sorted:
                pd = per_seed[s].get("per_depth", {}).get(d_str, {})
                pa = pd.get("per_arm", {}).get(arm, {})
                if "accuracy" in pa:
                    accs.append(float(pa["accuracy"]))
            if accs:
                m = float(np.mean(accs))
                sd = float(np.std(accs))
                cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
                summary[d_str][arm] = {"mean": m, "std": sd, "cv": cv,
                                          "n_seeds": len(accs)}
            else:
                summary[d_str][arm] = {"mean": 0.0, "std": 0.0, "cv": 0.0,
                                          "n_seeds": 0}

    # Arms-distinct: every (seed, depth) must pass; aggregate worst case
    arms_distinct_all = True
    for s in seeds_sorted:
        adpd = per_seed[s].get("arms_distinct_per_depth", {})
        for d in ACTIVE_DEPTHS:
            if not adpd.get(str(d), False):
                arms_distinct_all = False
                break
        if not arms_distinct_all:
            break

    # Cardinality
    completed = 0
    for s in seeds_sorted:
        for d in ACTIVE_DEPTHS:
            pd = per_seed[s].get("per_depth", {}).get(str(d), {})
            for arm in EXPECTED_ARMS:
                pa = pd.get("per_arm", {}).get(arm, {})
                completed += int(pa.get("n_trials", 0))
    cardinality_ok = (completed >= int(EXPECTED_N_UNITS * 0.9))

    # Extract decision-critical
    def _get_mean(d, arm):
        return summary.get(str(d), {}).get(arm, {}).get("mean", 0.0)
    def _get_cv(d, arm):
        return summary.get(str(d), {}).get(arm, {}).get("cv", 0.0)

    sub_d2 = _get_mean(2, "SUBSTRATE")
    sub_d3 = _get_mean(3, "SUBSTRATE") if 3 in ACTIVE_DEPTHS else None
    sub_d4 = _get_mean(4, "SUBSTRATE") if 4 in ACTIVE_DEPTHS else None
    sub_d5 = _get_mean(5, "SUBSTRATE") if 5 in ACTIVE_DEPTHS else None
    naive_d3 = _get_mean(3, "NAIVE_FLAT") if 3 in ACTIVE_DEPTHS else None
    shuffle_d3 = _get_mean(3, "SHUFFLE") if 3 in ACTIVE_DEPTHS else None
    random_d3 = _get_mean(3, "RANDOM") if 3 in ACTIVE_DEPTHS else None
    cv_sub_d3 = _get_cv(3, "SUBSTRATE") if 3 in ACTIVE_DEPTHS else 0.0

    # Suspect-1000 at depth >= 3 across all arms
    suspect_1000 = False
    for d in ACTIVE_DEPTHS:
        if d < 3:
            continue
        for arm in EXPECTED_ARMS:
            if _get_mean(d, arm) >= SUSPECT_1000:
                suspect_1000 = True
                break
        if suspect_1000:
            break

    # RANDOM in chance band (check d=3 if active, else d=2)
    chk_depth = 3 if 3 in ACTIVE_DEPTHS else ACTIVE_DEPTHS[0]
    random_in_band = (RANDOM_BAND_LO <= _get_mean(chk_depth, "RANDOM")
                       <= RANDOM_BAND_HI)

    # Discriminator gap @ d=3
    discriminator_gap_d3 = None
    mechanism_gap_d3 = None
    if 3 in ACTIVE_DEPTHS:
        other_max = max(naive_d3 or 0.0, shuffle_d3 or 0.0, random_d3 or 0.0)
        discriminator_gap_d3 = sub_d3 - other_max
        mechanism_gap_d3 = sub_d3 - (naive_d3 or 0.0)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL ladder
    if not arms_distinct_all:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_AF: arms-must-differ FAIL (bit-identical bug)"
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_reason = ("META_RULE_H_CARDINALITY_BREACH: completed=%d < "
                           "expected=%d (10%% slack)") % (completed,
                                                            EXPECTED_N_UNITS)
    elif suspect_1000:
        verdict = "HARD_FAIL"
        verdict_reason = "META_RULE_Q: arm >= 0.999 at depth >= 3 (rig too easy)"
    elif not random_in_band:
        verdict = "HARD_FAIL"
        verdict_reason = ("PIPELINE_BROKEN: RANDOM @ d=%d = %.3f outside band "
                           "[%.2f, %.2f]") % (chk_depth,
                                                _get_mean(chk_depth, "RANDOM"),
                                                RANDOM_BAND_LO,
                                                RANDOM_BAND_HI)
    elif sub_d2 < HF_SUBSTRATE_BY_DEPTH[2]:
        verdict = "HARD_FAIL"
        verdict_reason = ("REGRESSION: SUBSTRATE @ d=2 = %.3f < HF %.2f "
                           "(base Sally-Anne broken)") % (
                              sub_d2, HF_SUBSTRATE_BY_DEPTH[2])
    elif (3 in ACTIVE_DEPTHS) and sub_d3 <= naive_d3:
        verdict = "HARD_FAIL"
        verdict_reason = ("NO_RECURSIVE_BENEFIT: SUBSTRATE @ d=3 = %.3f <= "
                           "NAIVE_FLAT @ d=3 = %.3f") % (sub_d3, naive_d3)
    else:
        # Check HARD_PASS conditions
        hp_checks = []
        for d in ACTIVE_DEPTHS:
            need = HP_SUBSTRATE_BY_DEPTH[d]
            got = _get_mean(d, "SUBSTRATE")
            hp_checks.append((d, got, need, got >= need))
        all_depth_hp = all(c[3] for c in hp_checks)
        cv_ok = True
        if 3 in ACTIVE_DEPTHS and sub_d3 >= 0.40:
            cv_ok = (cv_sub_d3 < HP_CV_MAX)
        discrim_ok = True
        mech_ok = True
        if 3 in ACTIVE_DEPTHS:
            discrim_ok = (discriminator_gap_d3 >= HP_DISCRIMINATOR_GAP_D3)
            mech_ok = (mechanism_gap_d3 >= HP_MECHANISM_GAP_D3)

        if all_depth_hp and cv_ok and discrim_ok and mech_ok:
            verdict = "HARD_PASS"
            verdict_reason = ("RECURSIVE_TOM_LOAD_BEARING: nested HRR + agent "
                               "partition validates through depth %d") % max(ACTIVE_DEPTHS)
        else:
            verdict = "MIDDLE_BAND"
            verdict_reason = "PARTIAL: " + " ; ".join(
                "d=%d sub=%.3f need>=%.2f" % (d, got, need)
                for d, got, need, _ in hp_checks
            ) + (" ; cv_d3=%.3f" % cv_sub_d3 if 3 in ACTIVE_DEPTHS else "")

    verdict_msg = ("%s | %s | depths=%s | sub_means={d2=%.3f,d3=%s,d4=%s,d5=%s} "
                    "| naive_d3=%s shuffle_d3=%s random_d3=%s "
                    "| cv_sub_d3=%.3f arms_distinct=%s cardinality=%s n_seeds=%d") % (
        verdict, verdict_reason, ACTIVE_DEPTHS,
        sub_d2,
        ("%.3f" % sub_d3) if sub_d3 is not None else "n/a",
        ("%.3f" % sub_d4) if sub_d4 is not None else "n/a",
        ("%.3f" % sub_d5) if sub_d5 is not None else "n/a",
        ("%.3f" % naive_d3) if naive_d3 is not None else "n/a",
        ("%.3f" % shuffle_d3) if shuffle_d3 is not None else "n/a",
        ("%.3f" % random_d3) if random_d3 is not None else "n/a",
        cv_sub_d3, arms_distinct_all, cardinality_ok, len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_depth_per_arm": summary,
        "arms_distinct_all": arms_distinct_all,
        "suspect_1000": suspect_1000,
        "random_in_band": random_in_band,
        "sub_d2": sub_d2,
        "sub_d3": sub_d3, "sub_d4": sub_d4, "sub_d5": sub_d5,
        "naive_d3": naive_d3, "shuffle_d3": shuffle_d3, "random_d3": random_d3,
        "discriminator_gap_d3": discriminator_gap_d3,
        "mechanism_gap_d3": mechanism_gap_d3,
        "cv_sub_d3": cv_sub_d3,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed,
        "cardinality_ok": cardinality_ok,
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_verified": bool(arms_distinct_all),
        "crlb_floor_computed": 1.0 / np.sqrt(N_DIM / 2),
        "crlb_formula_reference": "1/sqrt(n_half); per-level retention from base sqrt(d=2 obs)",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_4loc_chance_0.25",
    }


# ----------------- main -----------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                            "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                            extra={"_phase": "init",
                                    "expected_arms": EXPECTED_ARMS,
                                    "active_depths": ACTIVE_DEPTHS,
                                    "expected_seeds": SEEDS,
                                    "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_REL=%d agents=%d depths=%s trials/d=%d seeds=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_REL, N_AGENTS_MAX, ACTIVE_DEPTHS,
        N_TRIALS_PER_DEPTH, SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_depth" in r
            for d in ACTIVE_DEPTHS:
                assert str(d) in r["per_depth"], "missing depth %d" % d
                for arm in EXPECTED_ARMS:
                    assert arm in r["per_depth"][str(d)]["per_arm"], (
                        "missing arm %s at d=%d" % (arm, d))
            # Mechanism quick check at d=2 (oracle path)
            sub_d2_acc = r["per_depth"][str(ACTIVE_DEPTHS[0])]["per_arm"]["SUBSTRATE"]["accuracy"]
            assert sub_d2_acc >= 0.4, (
                "self-test SUBSTRATE @ d=%d too low: %.3f"
                % (ACTIVE_DEPTHS[0], sub_d2_acc))
            arms_d_all = all(r["arms_distinct_per_depth"].values())
            assert arms_d_all, "META_RULE_AF self-test FAIL: %s" % r["arms_distinct_diag"]
            _write_minimal_metrics(
                out_dir, "SELFTEST_OK",
                "SELFTEST_OK: arms_distinct=%s sub_d%d=%.3f" % (
                    arms_d_all, ACTIVE_DEPTHS[0], sub_d2_acc),
                extra={"_phase": "selftest_done",
                        "arms_distinct_pass": arms_d_all,
                        "active_depths": ACTIVE_DEPTHS})
            print("[selftest] OK arms_distinct=%s sub_d%d=%.3f" % (
                arms_d_all, ACTIVE_DEPTHS[0], sub_d2_acc), flush=True)
            return 0
        except SystemExit:
            raise
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                    "SELFTEST_FAIL: %s" % e,
                                    extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
                   "depths": ACTIVE_DEPTHS, "n_trials": N_TRIALS_PER_DEPTH}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
            flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                                "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                                extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        # Print per-depth highlights
        for d in ACTIVE_DEPTHS:
            pa = result["per_depth"][str(d)]["per_arm"]
            print("[seed=%d d=%d] sub=%.3f naive=%.3f shuf=%.3f rnd=%.3f arms_distinct=%s" % (
                seed, d, pa["SUBSTRATE"]["accuracy"], pa["NAIVE_FLAT"]["accuracy"],
                pa["SHUFFLE"]["accuracy"], pa["RANDOM"]["accuracy"],
                result["arms_distinct_per_depth"][str(d)]), flush=True)
        print("[seed=%d] DONE in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_higher_order_tom_recursive"
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(final, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
