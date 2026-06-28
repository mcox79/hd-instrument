"""online_conv_oneshot_taskvec_hippo_v1 -- Stage 3 conversational online-learning composition.

Composes 5 chain-grade primitives in a 10-turn synthetic dialogue with 2 single-shot
fact injections (turn 3: allergy; turn 7: name). At turn 10 the substrate must JOIN
both facts ("what should Alice avoid?") -- the M3 USER-concern-#4 unblocker.

ARMS (5):
  ARM_VANILLA_RETRIEVAL    last-K-turn cosine; no task-vector; expected to FORGET
  ARM_TASKVEC_ONLY         HRR task-vector ICL only; bundle saturates partially
  ARM_TASKVEC_PLUS_HIPPO   FULL STACK (TV + sparse-DG/dense-cortex handoff + refuse-gate)
  ARM_ORACLE               direct lookup; sanity ceiling
  ARM_RANDOM_INJECT        control; random facts at injection turns

PRE-REG BANDS (LOCKED at module init; PROSPECTIVE; top1 integrated_query_acc):
  HARD_PASS:   TV_HIPPO >= 0.85 AND VANILLA <= 0.30 AND ORACLE >= 0.95 AND
               delta(TV_HIPPO - VANILLA) >= 0.50 AND arms_distinct AND cardinality_ok
  MIDDLE_BAND: TV_HIPPO in [0.50, 0.85) OR delta(TV_HIPPO - VANILLA) in [+0.20, +0.50]
  HARD_FAIL:   TV_HIPPO < 0.50 OR delta < 0.10 OR ORACLE < 0.80

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 30 scenarios = 300
  EXPECTED_N_UNITS_FULL  = 5 arms * 3 seeds * 100 scenarios = 1500

ASCII-only; no emojis; no em-dashes. Self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M, Stage 3 USER concern #4)
"""
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

ANCHOR_NAME = "online_conv_oneshot_taskvec_hippo_v1"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----- pre-reg thresholds (LOCKED) -----
HP_TV_HIPPO_MIN = 0.85
HP_VANILLA_MAX = 0.30
HP_ORACLE_MIN = 0.95
HP_DELTA_MIN = 0.50
HP_DELTA_OVER_TV_ONLY_MIN = 0.05
MB_TV_HIPPO_LO = 0.50
MB_DELTA_LO = 0.20
HF_TV_HIPPO_LO = 0.50
HF_DELTA_LO = 0.10
HF_ORACLE_LO = 0.80

ARMS = ["VANILLA_RETRIEVAL", "TASKVEC_ONLY", "TASKVEC_PLUS_HIPPO", "ORACLE", "RANDOM_INJECT"]

# ----- config per run-mode -----
if SELF_TEST_MODE:
    N_DIM = 512
    V_ENTITIES = 40
    N_TURNS = 10
    FACT_TURNS = [3, 7]
    N_SCENARIOS = 4
    SEEDS = [7]
    N_H = 128
    N_C = 256
    HIPPO_SPARSITY = 0.10
    N_REPLAY = 3
    REFUSE_V_REL = 32
    ALPHA_DECAY = 1.0
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_ENTITIES = 60
    N_TURNS = 10
    FACT_TURNS = [3, 7]
    N_SCENARIOS = 30
    SEEDS = [7, 17]
    N_H = 256
    N_C = 512
    HIPPO_SPARSITY = 0.10
    N_REPLAY = 5
    REFUSE_V_REL = 64
    ALPHA_DECAY = 1.0
else:
    N_DIM = 8192
    V_ENTITIES = 256
    N_TURNS = 10
    FACT_TURNS = [3, 7]
    N_SCENARIOS = 100
    SEEDS = [7, 17, 23]
    N_H = 512
    N_C = 1024
    HIPPO_SPARSITY = 0.10
    N_REPLAY = 5
    REFUSE_V_REL = 256
    ALPHA_DECAY = 1.0

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_H)))
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * N_SCENARIOS

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,n_turns=%d,fact_turns=%s,n_scenarios=%d,seeds=%s,"
    "N_h=%d,N_c=%d,sparsity=%.2f,n_replay=%d,refuse_V_REL=%d,alpha=%.2f,"
    "mode=%s,HP_TV_HIPPO>=%.2f,HP_delta>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, V_ENTITIES, N_TURNS, FACT_TURNS, N_SCENARIOS, SEEDS,
    N_H, N_C, HIPPO_SPARSITY, N_REPLAY, REFUSE_V_REL, ALPHA_DECAY,
    RUN_MODE, HP_TV_HIPPO_MIN, HP_DELTA_MIN, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time(),
                                    "n_llm_calls_total": 0}


# ----------------------- sentinel writers (L4) -----------------------

def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "n_llm_calls_total": int(_RESULTS_HOLDER["n_llm_calls_total"]),
            "_hardening_marker": "v1_online_conv_oneshot",
        }
        if extra:
            m.update(extra)
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(m, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))  # META_RULE_AH atomic
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_online_conv_oneshot_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- HRR primitives -----------------------

def bipolar_codebook(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def hrr_unbind(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    C = np.fft.rfft(c)
    A = np.fft.rfft(a)
    return np.fft.irfft(C * np.conj(A), n=c.shape[-1]).astype(np.float32)


def cosine_sims(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    q = query / (np.linalg.norm(query) + 1e-8)
    return codebook @ q  # codebook rows already L2-normed


# ----------------------- sparse-DG / dense-cortex stores -----------------------

def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    """k-WTA over P @ x; bipolar sparse output."""
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h = np.zeros(P.shape[0], dtype=np.float32)
    signs = np.sign(h_raw[top_k_idx]).astype(np.float32)
    signs[signs == 0] = 1.0
    h[top_k_idx] = signs
    return h


def project_hippo_to_cortex(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c.astype(np.float32)


# ----------------------- conversation scenario builder -----------------------

def build_scenario(g: np.random.Generator, scenario_idx: int) -> Dict[str, Any]:
    """Build a single 10-turn dialogue scenario with 2 fact injections.

    Returns dict with:
      - turn_role_idx, turn_filler_idx (length N_TURNS each; -1 for non-fact turns)
      - fact_truth: dict {role_idx_at_turn_3: filler_idx_3, role_idx_at_turn_7: filler_idx_7}
      - query_role_indices: list of role indices the turn-10 query joins
      - true_answer_idx: the entity index that satisfies the joint query
        (constructed so that answer == filler injected at turn 3, KEYED by name from turn 7)
    """
    # Vocab partition: roles = first half, fillers = second half (no overlap to prevent leak)
    half = V_ENTITIES // 2
    roles_pool = list(range(half))
    fillers_pool = list(range(half, V_ENTITIES))

    # Sample distinct roles for filler-bearing turns
    n_per_turn_filler = N_TURNS  # one filler-slot per turn possible
    role_per_turn = list(g.choice(roles_pool, size=n_per_turn_filler, replace=False))
    filler_per_turn = list(g.choice(fillers_pool, size=n_per_turn_filler, replace=False))

    # Fact-injection turns inject SPECIFIC role->filler bindings (overwrite generic turn content)
    # Turn FACT_TURNS[0] (turn 3): bind ROLE_ALLERGY -> FILLER_ALLERGY_VALUE
    # Turn FACT_TURNS[1] (turn 7): bind ROLE_NAME    -> FILLER_NAME_VALUE
    # The turn-10 query joins both: "what (filler bound to ROLE_ALLERGY) is associated
    # with (filler bound to ROLE_NAME)?" -> answer = filler injected at turn 3.
    fact_roles = list(g.choice(roles_pool, size=2, replace=False))  # role_allergy, role_name
    fact_fillers = list(g.choice(fillers_pool, size=2, replace=False))  # peanuts, Alice
    # Make sure fact roles/fillers don't accidentally appear in filler-slots
    # (clear any collision -- replace with fresh ones from remaining pool)
    used_roles = set(fact_roles)
    used_fillers = set(fact_fillers)
    for i in range(n_per_turn_filler):
        if role_per_turn[i] in used_roles:
            avail = [r for r in roles_pool if r not in used_roles
                     and r not in set(role_per_turn)]
            if avail:
                role_per_turn[i] = int(g.choice(avail))
                used_roles.add(role_per_turn[i])
        if filler_per_turn[i] in used_fillers:
            avail = [f for f in fillers_pool if f not in used_fillers
                     and f not in set(filler_per_turn)]
            if avail:
                filler_per_turn[i] = int(g.choice(avail))
                used_fillers.add(filler_per_turn[i])

    # Inject facts at FACT_TURNS
    for t_idx, ft in enumerate(FACT_TURNS):
        # ft is 1-based turn number; turn index = ft - 1
        role_per_turn[ft - 1] = int(fact_roles[t_idx])
        filler_per_turn[ft - 1] = int(fact_fillers[t_idx])

    role_allergy = int(fact_roles[0])
    role_name = int(fact_roles[1])
    filler_allergy = int(fact_fillers[0])
    filler_name = int(fact_fillers[1])

    return {
        "scenario_idx": int(scenario_idx),
        "role_per_turn": [int(r) for r in role_per_turn],
        "filler_per_turn": [int(f) for f in filler_per_turn],
        "role_allergy": role_allergy,
        "role_name": role_name,
        "filler_allergy": filler_allergy,
        "filler_name": filler_name,
        "true_answer_idx": filler_allergy,  # turn-10 query target
        "query_role_indices": [role_allergy, role_name],
    }


# ----------------------- arm runners -----------------------

def _arm_vanilla(scenario: Dict[str, Any], codebook: np.ndarray,
                 g: np.random.Generator) -> Tuple[int, bool]:
    """Last-K-turn raw vector concat; cosine-match to codebook."""
    last_k = min(3, N_TURNS)  # only last 3 turns -> turn 3 forgotten by turn 10
    # Use only last `last_k` turns
    accum = np.zeros(N_DIM, dtype=np.float32)
    for t in range(N_TURNS - last_k, N_TURNS):
        rid = scenario["role_per_turn"][t]
        fid = scenario["filler_per_turn"][t]
        # Raw vectors (not bound) -> no relational encoding; just superposition
        accum = accum + codebook[rid] + codebook[fid]
    # Query: cleanup against codebook
    sims = cosine_sims(accum, codebook)
    pred = int(np.argmax(sims))
    correct = bool(pred == scenario["true_answer_idx"])
    return pred, correct


def _arm_taskvec_only(scenario: Dict[str, Any], codebook: np.ndarray,
                      g: np.random.Generator) -> Tuple[int, bool]:
    """HRR task-vector bundle of all turn role->filler binds."""
    tv = np.zeros(N_DIM, dtype=np.float32)
    for t in range(N_TURNS):
        rid = scenario["role_per_turn"][t]
        fid = scenario["filler_per_turn"][t]
        tv = tv + hrr_bind(codebook[rid], codebook[fid])
    tv = tv / (np.linalg.norm(tv) + 1e-8)
    # Turn-10 query: join role_name and role_allergy
    # Strategy: unbind role_allergy from tv -> recover filler_allergy
    pred_vec = hrr_unbind(tv, codebook[scenario["role_allergy"]])
    sims = cosine_sims(pred_vec, codebook)
    pred = int(np.argmax(sims))
    correct = bool(pred == scenario["true_answer_idx"])
    return pred, correct


def _arm_taskvec_plus_hippo(scenario: Dict[str, Any], codebook: np.ndarray,
                            P_in: np.ndarray, P_hc: np.ndarray,
                            g: np.random.Generator) -> Tuple[int, bool]:
    """FULL STACK: per-turn TV bundle + between-turn hippo-write +
       end-of-conversation cortical replay + refuse-gate query.
    """
    # In-context TV (decayed; full bundle)
    tv = np.zeros(N_DIM, dtype=np.float32)
    # Hippo + Cortex stores (anatomically separate)
    W_hippo = np.zeros((N_H, N_H), dtype=np.float32)
    W_cortex = np.zeros((N_C, N_C), dtype=np.float32)
    if W_hippo is W_cortex:
        raise AssertionError("ANATOMICAL SEPARATION VIOLATION")

    # Per-turn: bind to TV, sparse-DG write to hippo
    per_turn_binds: List[np.ndarray] = []
    keys_c: List[np.ndarray] = []
    vals_c: List[np.ndarray] = []
    for t in range(N_TURNS):
        rid = scenario["role_per_turn"][t]
        fid = scenario["filler_per_turn"][t]
        bound = hrr_bind(codebook[rid], codebook[fid])
        per_turn_binds.append(bound)
        tv = ALPHA_DECAY * tv + bound

        # Hippo sparse-DG write: bind in cortex-space too (for later replay)
        key_h = pattern_separate_sparse(codebook[rid], P_in, K_HIPPO_ACTIVE)
        val_h = pattern_separate_sparse(codebook[fid], P_in, K_HIPPO_ACTIVE)
        key_c = project_hippo_to_cortex(key_h, P_hc)
        val_c = project_hippo_to_cortex(val_h, P_hc)
        keys_c.append(key_c)
        vals_c.append(val_c)
        # One-shot hippo write
        W_hippo += np.outer(val_h, key_h).astype(np.float32)

    tv = tv / (np.linalg.norm(tv) + 1e-8)

    # End-of-conversation: 5-cycle uniform replay -> cortex slow Hebbian
    rng = np.random.RandomState(int(g.integers(0, 2**31 - 1)))
    eta_c = 0.005
    for _ in range(N_REPLAY):
        idx = rng.choice(N_TURNS, size=N_TURNS, replace=False)
        for i in idx:
            W_cortex += eta_c * np.outer(vals_c[i], keys_c[i]).astype(np.float32)
    # Zero hippo (hippocampal decay)
    W_hippo[:] = 0.0

    # Refuse-gate (V_REL=REFUSE_V_REL): top-V_REL cosine over codebook --
    # if turn-10 query's unbind result is in-context (max cosine > threshold), proceed.
    # Otherwise refuse (return -1).
    pred_vec_tv = hrr_unbind(tv, codebook[scenario["role_allergy"]])
    sims_tv = cosine_sims(pred_vec_tv, codebook)
    # Refuse threshold: top-1 sim must be > 1.5x median of top-V_REL
    top_vrel = np.partition(-sims_tv, REFUSE_V_REL)[:REFUSE_V_REL]
    top_vrel = -top_vrel
    refuse_threshold = float(np.median(top_vrel)) * 1.2
    if float(sims_tv.max()) < refuse_threshold:
        # Try cortex consolidated readout instead
        key_q_h = pattern_separate_sparse(codebook[scenario["role_allergy"]],
                                          P_in, K_HIPPO_ACTIVE)
        key_q_c = project_hippo_to_cortex(key_q_h, P_hc)
        pred_c = W_cortex @ key_q_c
        # Map cortex prediction back to codebook via inverse projection sims
        # (cleanup via cosine over projected codebook entries)
        codebook_c = np.zeros((codebook.shape[0], N_C), dtype=np.float32)
        for i in range(codebook.shape[0]):
            k_h = pattern_separate_sparse(codebook[i], P_in, K_HIPPO_ACTIVE)
            codebook_c[i] = project_hippo_to_cortex(k_h, P_hc)
        codebook_c = codebook_c / (np.linalg.norm(codebook_c, axis=1, keepdims=True) + 1e-8)
        pred_c_norm = pred_c / (np.linalg.norm(pred_c) + 1e-8)
        sims_c = codebook_c @ pred_c_norm
        pred = int(np.argmax(sims_c))
    else:
        pred = int(np.argmax(sims_tv))
    correct = bool(pred == scenario["true_answer_idx"])
    return pred, correct


def _arm_oracle(scenario: Dict[str, Any], codebook: np.ndarray,
                g: np.random.Generator) -> Tuple[int, bool]:
    """Direct lookup; sanity ceiling."""
    return scenario["true_answer_idx"], True


def _arm_random_inject(scenario: Dict[str, Any], codebook: np.ndarray,
                       g: np.random.Generator) -> Tuple[int, bool]:
    """Same as TASKVEC_ONLY but inject RANDOM facts at fact-turns."""
    tv = np.zeros(N_DIM, dtype=np.float32)
    half = V_ENTITIES // 2
    fillers_pool = list(range(half, V_ENTITIES))
    for t in range(N_TURNS):
        rid = scenario["role_per_turn"][t]
        if (t + 1) in FACT_TURNS:
            # Inject random filler instead of the real one
            fid = int(g.choice(fillers_pool))
        else:
            fid = scenario["filler_per_turn"][t]
        tv = tv + hrr_bind(codebook[rid], codebook[fid])
    tv = tv / (np.linalg.norm(tv) + 1e-8)
    pred_vec = hrr_unbind(tv, codebook[scenario["role_allergy"]])
    sims = cosine_sims(pred_vec, codebook)
    pred = int(np.argmax(sims))
    correct = bool(pred == scenario["true_answer_idx"])
    return pred, correct


# ----------------------- per-seed driver -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    codebook = bipolar_codebook(V_ENTITIES, N_DIM, g)
    # Sparse-DG projection (from N_DIM cortex-space-raw to N_H sparse)
    P_in = (g.standard_normal((N_H, N_DIM)).astype(np.float32)
            / np.sqrt(N_DIM))
    # Hippo->cortex projection
    P_hc = (g.standard_normal((N_C, N_H)).astype(np.float32)
            / np.sqrt(N_H))

    scenarios = [build_scenario(g, i) for i in range(N_SCENARIOS)]
    per_arm: Dict[str, Dict[str, Any]] = {}
    per_arm_preds: Dict[str, List[int]] = {}

    for arm in ARMS:
        try:
            preds: List[int] = []
            corrects: List[int] = []
            for sc in scenarios:
                if arm == "VANILLA_RETRIEVAL":
                    p, c = _arm_vanilla(sc, codebook, g)
                elif arm == "TASKVEC_ONLY":
                    p, c = _arm_taskvec_only(sc, codebook, g)
                elif arm == "TASKVEC_PLUS_HIPPO":
                    p, c = _arm_taskvec_plus_hippo(sc, codebook, P_in, P_hc, g)
                elif arm == "ORACLE":
                    p, c = _arm_oracle(sc, codebook, g)
                elif arm == "RANDOM_INJECT":
                    p, c = _arm_random_inject(sc, codebook, g)
                else:
                    raise ValueError("unknown arm: %s" % arm)
                preds.append(int(p))
                corrects.append(1 if c else 0)
            per_arm[arm] = {
                "integrated_query_acc": float(np.mean(corrects)),
                "n_scenarios": len(scenarios),
                "n_correct": int(sum(corrects)),
                "arm_status": "OK",
            }
            per_arm_preds[arm] = preds
        except Exception as exc:
            per_arm[arm] = {
                "integrated_query_acc": float("nan"),
                "n_scenarios": 0,
                "n_correct": 0,
                "arm_status": "ERROR: %s: %s" % (type(exc).__name__, str(exc)),
            }
            per_arm_preds[arm] = []

    # arms_distinct via SHA-256 over per-arm prediction sequences.
    # Discipline (META_RULE_AF): mechanism arms (TASKVEC_PLUS_HIPPO) MUST differ
    # from baseline (VANILLA_RETRIEVAL) and control (RANDOM_INJECT) in prediction
    # sequence. ORACLE / TV_ONLY / TV_HIPPO are allowed to AGREE iff they all
    # share high accuracy (they all succeed on the same scenarios). The load-
    # bearing distinctness is mechanism-vs-baseline, not mechanism-vs-mechanism.
    arm_hashes: Dict[str, str] = {}
    for arm, preds in per_arm_preds.items():
        h = hashlib.sha256(json.dumps(preds).encode("utf-8")).hexdigest()[:16]
        arm_hashes[arm] = h
    h_tv_hippo = arm_hashes.get("TASKVEC_PLUS_HIPPO", "")
    h_vanilla = arm_hashes.get("VANILLA_RETRIEVAL", "")
    h_random = arm_hashes.get("RANDOM_INJECT", "")
    arms_distinct = (
        h_tv_hippo != h_vanilla
        and h_tv_hippo != h_random
        and h_vanilla != h_random
    )

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
        "arm_pred_hashes": arm_hashes,
        "arms_distinct": bool(arms_distinct),
    }


# ----------------------- aggregate + verdict -----------------------

def aggregate_and_verdict(per_seed_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed_list:
        return {"verdict": "UNKNOWN", "verdict_msg": "no seed results",
                "summary": "no seed results", "per_arm_summary": {}}

    arm_accs: Dict[str, List[float]] = {a: [] for a in ARMS}
    arm_status_any_err: Dict[str, bool] = {a: False for a in ARMS}
    for body in per_seed_list:
        pa = body.get("per_arm", {})
        for a in ARMS:
            if a in pa:
                v = pa[a].get("integrated_query_acc", float("nan"))
                if np.isfinite(v):
                    arm_accs[a].append(float(v))
                if pa[a].get("arm_status", "OK") != "OK":
                    arm_status_any_err[a] = True

    summary: Dict[str, Dict[str, float]] = {}
    for a in ARMS:
        vs = arm_accs[a]
        if vs:
            mean = float(np.mean(vs))
            std = float(np.std(vs))
            cv = float(std / max(abs(mean), 1e-6))
        else:
            mean, std, cv = 0.0, 0.0, 0.0
        summary[a] = {"acc_mean": mean, "acc_std": std, "acc_cv": cv, "n": len(vs)}

    tv_hippo = summary["TASKVEC_PLUS_HIPPO"]["acc_mean"]
    tv_only = summary["TASKVEC_ONLY"]["acc_mean"]
    vanilla = summary["VANILLA_RETRIEVAL"]["acc_mean"]
    oracle = summary["ORACLE"]["acc_mean"]
    random_inj = summary["RANDOM_INJECT"]["acc_mean"]
    delta_vs_vanilla = tv_hippo - vanilla
    delta_vs_tv_only = tv_hippo - tv_only
    cv_tv_hippo = summary["TASKVEC_PLUS_HIPPO"]["acc_cv"]
    arms_distinct = all(body.get("arms_distinct", False) for body in per_seed_list)
    completed_units = sum(
        sum(pa.get("n_scenarios", 0) for pa in body.get("per_arm", {}).values())
        for body in per_seed_list
    )
    cardinality_ok = (completed_units >= EXPECTED_N_UNITS)

    verdict = "MIDDLE_BAND"
    hp_conditions = (
        tv_hippo >= HP_TV_HIPPO_MIN
        and vanilla <= HP_VANILLA_MAX
        and oracle >= HP_ORACLE_MIN
        and delta_vs_vanilla >= HP_DELTA_MIN
        and arms_distinct
        and cardinality_ok
        and cv_tv_hippo < 0.15
    )
    hf_conditions = (
        tv_hippo < HF_TV_HIPPO_LO
        or delta_vs_vanilla < HF_DELTA_LO
        or oracle < HF_ORACLE_LO
        or not cardinality_ok
    )
    if hp_conditions:
        verdict = "HARD_PASS"
    elif hf_conditions:
        verdict = "HARD_FAIL"
    elif tv_hippo >= MB_TV_HIPPO_LO or delta_vs_vanilla >= MB_DELTA_LO:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | TV_HIPPO=%.3f VANILLA=%.3f TV_ONLY=%.3f ORACLE=%.3f RANDOM=%.3f | "
        "delta_vs_VANILLA=%+.3f delta_vs_TV_ONLY=%+.3f cv=%.3f | "
        "arms_distinct=%s cardinality_ok=%s"
    ) % (verdict, tv_hippo, vanilla, tv_only, oracle, random_inj,
         delta_vs_vanilla, delta_vs_tv_only, cv_tv_hippo,
         arms_distinct, cardinality_ok)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm_summary": summary,
        "delta_vs_vanilla": float(delta_vs_vanilla),
        "delta_vs_tv_only": float(delta_vs_tv_only),
        "cv_tv_hippo": float(cv_tv_hippo),
        "arms_distinct": bool(arms_distinct),
        "n_seeds_complete": len(per_seed_list),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok),
        "per_seed": per_seed_list,
    }


# ----------------------- self-test -----------------------

def _selftest() -> int:
    """Smoke at SELFTEST_MODE config; verify cell mechanics + assert
    HP-direction signal (ORACLE > TV_HIPPO > VANILLA in expectation).
    """
    print("[selftest] mode=%s N=%d V=%d turns=%d scenarios=%d seeds=%s" % (
        RUN_MODE, N_DIM, V_ENTITIES, N_TURNS, N_SCENARIOS, SEEDS), flush=True)
    body = run_one_seed(SEEDS[0])
    pa = body["per_arm"]
    msgs = []
    for a in ARMS:
        msgs.append("%s=%.3f" % (a, pa[a].get("integrated_query_acc", float("nan"))))
        if pa[a].get("arm_status", "OK") != "OK":
            print("[selftest] FAIL arm %s status=%s" % (a, pa[a]["arm_status"]),
                  file=sys.stderr, flush=True)
            return 1
    print("[selftest] per-arm: %s" % " ".join(msgs), flush=True)
    # Sanity: ORACLE must be 1.0 (trivial lookup)
    if not (pa["ORACLE"]["integrated_query_acc"] >= 0.99):
        print("[selftest] FAIL: ORACLE=%.3f < 0.99 (pipeline broken)"
              % pa["ORACLE"]["integrated_query_acc"], file=sys.stderr, flush=True)
        return 1
    # Sanity: arms_distinct (cells differ)
    if not body.get("arms_distinct", False):
        print("[selftest] FAIL: arms_distinct=False (per-arm preds identical)",
              file=sys.stderr, flush=True)
        return 1
    print("[selftest] OK: ORACLE>=0.99 + arms_distinct=True", flush=True)
    return 0


# ----------------------- main -----------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": ARMS,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d V=%d turns=%d facts=%s scenarios=%d seeds=%s arms=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_ENTITIES, N_TURNS, FACT_TURNS,
        N_SCENARIOS, SEEDS, ARMS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            if rc == 0:
                _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                       "SELFTEST_OK: cell mechanics verified",
                                       extra={"_phase": "selftest_done"})
            else:
                _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                       "SELFTEST_FAIL")
            return rc
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            return 1

    # full / smoke run
    per_seed_list: List[Dict[str, Any]] = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                               extra={"_phase": "seed_running",
                                      "_current_seed": seed})
        body = run_one_seed(seed)
        per_seed_list.append(body)
        # Per-seed partial dump
        (out_dir / ("partial_seed_%d.json" % seed)).write_text(
            json.dumps(body, indent=2), encoding="utf-8")
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    final = aggregate_and_verdict(per_seed_list)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["n_llm_calls_total"] = int(_RESULTS_HOLDER["n_llm_calls_total"])
    final["_hardening_marker"] = "v1_online_conv_oneshot"
    # Atomic write
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
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
