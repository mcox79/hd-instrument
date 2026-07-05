# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (REGEN vs ANALOG vs ORACLE_CHAIN vs BROKEN inter-stage id streams
#     are hash-distinct per (regime,seed) unit; enforced in _run before verdict).
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb / capacity-feasibility: chance object accuracy = 1/V_obj (V_hard=4096 -> 0.000244 THEORETICAL);
#     BROKEN arm (identity severed at the reason hop) must land in the chance band (<= BROKEN_CEIL=0.05).
#     ORACLE_CHAIN (every stage fed ground truth) bounds the reachable machinery ceiling (WIRING gate).
#     crlb_n_a for the composition itself: no closed-form noise floor for a 4-stage cleanup chain; the
#     compounding_ratio diagnostic (end2end / product_of_isolated_stages) IS the capacity-feasibility test.
# - baseline_in_band (META_RULE_AG): the 4 ISOLATED stage accuracies (comprehend/reason/gate/generate,
#     each fed ground-truth input) MUST each land in (STAGE_LO=0.05, STAGE_HI=0.98) at the hard regime --
#     a stage that is floored or saturated in isolation cannot contribute a measurable factor to the
#     compounding product, and would make the compounding_ratio uninterpretable. Verified in smoke.
# - discriminator survives scale: the DIFFICULTY axes (V, D_store, hops, hub_cluster, N_R, N_G, gate WTA
#     distractor count) are held at FULL in smoke; smoke reduces ONLY trials + seeds + gate-train pool. So the
#     smoke isolated-stage-in-band + REGEN>>ANALOG preview IS the full-N preview of compounding (option A).
# - HARD_PASS strictly above floor: full_chain_end2end[REGEN] >= 0.35 AND compounding_ratio[REGEN] >= 0.70
#     AND (REGEN - ANALOG) >= 0.20 AND cross-seed cv(REGEN) < 0.15 (all strict, above the MIDDLE band).
# - HP_SCOPE: the compounding HP gates apply ONLY to the REGEN arm vs the ANALOG arm; WIRING gate applies to
#     ORACLE_CHAIN; the collapse gate applies to BROKEN. Isolated-stage in-band gates apply to the 4 STAGE
#     oracles.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# INTEGRATION FULL STACK, HARD REGIME: comprehend(role-type) -> store+reason(multi-hop) -> control-gate(goal)
#   -> generate, chained end-to-end for the FIRST time, with REGENERATIVE cleanup vs ANALOG pass-through as
#   the primary experimental axis.  v1
# ====================================================================================================
# WHY (USER direct 5x-drill angle 3: "are the brain components fully baked AND integrated?"):
#   8 capabilities are each individually proven; the only end-to-end loop that passed was EASY-regime
#   (integration_end_to_end_loop_bridge_v1, single-hop object-slot-only symbolic, end2end=1.0). The one
#   HARD-regime seam tested (integration_end_to_end_loop_bridge_HARD_v2) is ONE seam (reason->generate, 2
#   slots). This cell chains 4 REAL subsystems at a HARD regime and asks: does error COMPOUND across stages,
#   or stay near-INDEPENDENT?
#
# THE MECHANISM HYPOTHESIS under test (the digital-repeater-vs-analog distinction):
#   At the one hard seam already tested, per-slot errors stayed NEAR-INDEPENDENT when a REGENERATIVE relay
#   (snap the noisy inter-stage signal to its nearest KNOWN codeword, then emit that codeword's clean code)
#   was used, while raw ANALOG pass-through COMPOUNDED:
#     MEASURED@data/exp_integration_end_to_end_loop_bridge_HARD_v2/metrics.json:
#       naive_symbolic (REGEN):  subj_acc=0.939 obj_acc=0.861 end2end=0.806  (0.939*0.861=0.808 ~= observed)
#       cotrained_linear (ANALOG): subj_acc=0.467 obj_acc=0.228 end2end=0.10 (0.467*0.228=0.106 ~= observed)
#   Near-perfect per-slot independence at n=1 seam. The OPEN question (2/3 lit-scans found NO published
#   benchmark of chaining 3+ cleanup stages in series): does regenerative cleanup keep errors near-independent
#   across a genuine 4-STAGE chain, or does a confident-wrong-attractor cascade appear only once >=4 real
#   subsystems are composed?  CITED@notes/research_integration_full_stack_hard_regime_compose_2026-07-05.md.
#
# THE 4 SUBSYSTEMS (each reuses its proven mechanism at its proven operating point; NO new mechanism):
#   (1) COMPREHEND (role-typing / selectional restriction). Reuses the content-conditioned matched-filter
#       role-typing of exp_comprehension_envelope_superposition_vocab_v1. Each concept lives in exactly ONE
#       role's DISJOINT vocab partition (subject-role vs object-role); a filler's identity constrains its
#       role. From a superposed 2-constituent perceptual bundle (subject code + object code, real correlated
#       codes), recover subj id (argmax over subj partition) + obj id (argmax over obj partition). Error =
#       content-typing confusion under vocab scale + hub-cluster near-neighbours (proven envelope holds at
#       D6/V500: MEASURED@..._comprehension...:grid.D6_V500.order_content_perrole_mean=1.0, parse_holds=True).
#   (2) STORE+REASON (multi-hop, hub-crowded). Reuses the HARD_v2 hard regime: HRR circular-conv bind/unbind
#       (hdlab.binding) over real BGE, V=4096, hops=3, D_store=10, near-neighbour hub cluster. STORES the
#       COMPREHENDED subject/object (not ground-truth), among D_store-1 distractor facts; multi-hop unbind
#       recovers the queried object HV + subject HV. Error = HRR unbind crosstalk.
#   (3) CONTROL-GATE (goal-conditioned Go/NoGo, WTA + abstain). Reuses the goal-transport reach mechanism of
#       exp_pfc_gate_cfrpe_trained_v2: reach(cand;goal)=cos(cand @ M_hat, goal) where M_hat is a ridge-fit of
#       the goal relation on a HELD-OUT train pool, goal = transform of the true object. Winner-take-all over
#       {recovered candidate} U {hub distractors}; Go iff max reach > tau, else abstain (scored as a miss).
#       REDUCED-FIDELITY note (declared SHAPE_DRIFT, prereg Gate C/D): the proven gate trains M by SR-TD over
#       an operator graph; here M is ridge-fit on (concept, goal-transform) pairs -- the reach WTA + abstain
#       ACTOR is faithful, the transport TRAINING is lighter. Positive-control arm STAGE_ORACLE.gate verifies
#       gate Go-accuracy lands in the proven FAIR band (~0.5-0.75; MEASURED@..._pfc_gate...:V1200_d4
#       gonogo=0.653). The gate's contribution to compounding = a stage factor < 1 + candidate-cleanliness
#       sensitivity (a NOISY analog candidate reaches worse -> more false-NoGo).
#   (4) GENERATE (bipolar-BSC block-local decode). Reuses the HARD_v2 / generation-decoder roundtrip decoder:
#       compose the ordered triple (subj,rel,obj) in bipolar-BSC protected/index positions; decode each slot
#       by unbind-position + partition-restricted argmax (role-typing decode benefit). Error = decode crosstalk.
#
# ARMS (the anti-compounding axis, orthogonal to the stage chain):
#   REGEN  (regenerative-relay): at EVERY seam, snap the noisy inter-stage estimate to its nearest KNOWN
#           codeword (argmax -> clean concept code) before the next stage consumes it (comprehend->store,
#           reason->gate, gate->generate). The "digital repeater".
#   ANALOG (no-relay): pass the raw continuous/noisy inter-stage estimate at every seam (softmax-blended
#           comprehension estimate; raw noisy HV into the gate; sign(noisy_HV @ R_naive) code into generate).
#           The "analog repeater" -- mirrors HARD_v2's cotrained_linear collapse.
#   ORACLE_CHAIN (WIRING gate): every stage fed GROUND-TRUTH clean input at every seam -> the machinery
#           ceiling (bridge/gate/decoder wiring). If this recovers, arm shortfalls are the COMPOSITION.
#   BROKEN (discriminator): sever object identity at the reason hop (unbind by an UNSTORED role path) ->
#           must collapse to chance (identity destroyed).
#
# STAGE-ORACLE ISOLATION (diagnostic, not a pass/fail arm): run EACH stage in isolation fed ground-truth input
#   -> comprehend_acc, reason_acc, gate_acc, generate_acc.  product_of_stages = their product = the naive
#   INDEPENDENCE prediction for the full chain. compounding_ratio[arm] = full_chain_end2end[arm] /
#   product_of_stages: ~1.0 => chain behaves as independent multiplicative stages (the good outcome); << 1 =>
#   a NEW emergent compounding penalty appears only when subsystems are genuinely chained (the negative the
#   USER is worried about; no pairwise seam test could reveal it).
#
# GLASS-BOX METRIC wrong_attractor_rate[REGEN]: fraction of REGEN cleanup steps (comprehension argmax +
#   reasoning snap) that commit to a WRONG codeword with HIGH margin (top1_cos - top2_cos > WRONG_ATTR_MARGIN
#   yet top1 != true). Operationalizes the confident-wrong-attractor-no-backtrack failure mode the literature
#   flags as the sharp edge of hard-decision relays; a trust/auditability metric, not just a curiosity.
#
# Sources (CITED@):
#  - experiments/exp_integration_end_to_end_loop_bridge_HARD_v2.py  (store/reason/generate scaffold + real BGE)
#  - experiments/exp_comprehension_envelope_superposition_vocab_v1.py (role-typing selectional restriction)
#  - experiments/exp_pfc_gate_cfrpe_trained_v2.py                   (goal-transport reach Go/NoGo actor)
#  - data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz (real correlated fillers; SCP to remote)
#  - notes/research_integration_full_stack_hard_regime_compose_2026-07-05.md (spec + bands + 3 lit-scans)
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_integration_full_stack_hard_regime_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

import torch  # noqa: E402

torch.set_num_threads(min(8, os.cpu_count() or 4))

ANCHOR_NAME = "integration_full_stack_hard_regime_v1"
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hdlab import binding  # noqa: E402  (proven store/reason primitive: HRR circular-conv)

# ---- Dimensions (NEVER reduced in smoke; discriminator-survives-scale) ----
N_R = 1024            # reasoning/store dim == BGE_DIM (HARD_v2 regime)
N_G = 8192            # comprehension + generation code dim (HARD_v2 / comprehension regime)
BGE_DIM = 1024
GEN_SLOTS = 3         # spoken ordered triple: (subject, relation, object)
SUBJ_ROLE_ID = 999983

SUBSET_PATH = REPO / "data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz"
BGE_FULL = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

SEEDS = (7, 13, 19)
RIDGE_LAMBDA = 1.0

# Fixed projection seeds (distinct so ANALOG's bolt-on does NOT know the clean gen lexicon).
COMP_SEED = 131313        # BGE -> N_G comprehension-lexicon projection
P_GEN_SEED = 424242       # BGE -> N_G generation-lexicon projection
R_NAIVE_SEED = 909090     # BGE-recovered -> N_G analog bolt-on projection (DIFFERENT from P_GEN_SEED)
M_GOAL_SEED = 515151      # gate goal-relation transport (true relation)

# ---- Pre-registered bands (HYPOTHESIZED@this-prereg; deflated per research note; verified vs smoke) ----
# THEORETICAL@chance obj acc = 1/V_obj (hard V=4096 -> 0.000244): BROKEN lands here.
WIRING_FLOOR = 0.80       # WIRING gate: ORACLE_CHAIN end2end must recover >= this (else machinery broken)
BROKEN_CEIL = 0.05        # DISCRIMINATOR: BROKEN end2end must collapse at/below this
HP_END2END = 0.35         # HARD_PASS: full_chain_end2end[REGEN] must exceed this
HP_COMPOUND = 0.70        # HARD_PASS: compounding_ratio[REGEN] must exceed this
HP_MARGIN = 0.20          # HARD_PASS: (REGEN - ANALOG) end2end margin must exceed this
HP_CV_MAX = 0.15          # HARD_PASS: cross-seed cv of REGEN end2end must be below this
HF_END2END = 0.25         # HARD_FAIL: full_chain_end2end[REGEN] below this ...
HF_COMPOUND = 0.50        # ... AND compounding_ratio[REGEN] below this (relay itself compounds)
STAGE_LO, STAGE_HI = 0.05, 0.98   # META_RULE_AG: each ISOLATED stage acc must land in this band (hard regime)
GATE_FAIR_LO, GATE_FAIR_HI = 0.35, 0.90  # gate isolated Go-acc fair band; genuine error source, not saturated
                                         # (this single-hop goal-selection is milder than the proven multi-hop
                                         #  operator gate @0.65, MEASURED@..._pfc_gate...:V1200_d4=0.653)
WRONG_ATTR_MARGIN = 0.10  # glass-box: confident-commit margin threshold (top1_cos - top2_cos)

ARMS = ["regen", "analog", "oracle_chain", "broken"]
REGIME_ORDER = ["easy", "hard"]


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# Real correlated concept fillers (BGE subset; remote-portable)
# ============================================================


_SUB = {"sem": None}


def _load_bge_subset() -> np.ndarray:
    if _SUB["sem"] is not None:
        return _SUB["sem"]
    if SUBSET_PATH.exists():
        _SUB["sem"] = np.load(SUBSET_PATH)["semantic"].astype(np.float32)
        return _SUB["sem"]
    if not BGE_FULL.exists():
        raise FileNotFoundError(
            f"neither subset ({SUBSET_PATH}) nor full BGE cache ({BGE_FULL}) present. "
            f"SCP the subset npz to the remote (queue_add does NOT auto-ship untracked npz).")
    sem = np.load(BGE_FULL)["semantic"]
    rng = np.random.default_rng(20260705)
    rows = np.sort(rng.choice(sem.shape[0], size=12288, replace=False))
    sub = sem[rows].astype(np.float32)
    SUBSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(SUBSET_PATH, semantic=sub, source_rows=rows.astype(np.int64))
    _SUB["sem"] = sub
    return sub


def _unit_rows(X: np.ndarray) -> np.ndarray:
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)).astype(np.float32)


def _unit(v: np.ndarray) -> np.ndarray:
    return (v / (np.linalg.norm(v) + 1e-12)).astype(np.float32)


# ============================================================
# Primitives: HRR store/reason (real hdlab.binding), bipolar codes
# ============================================================


def _bind_hrr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = binding.bind(torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32)),
                       torch.from_numpy(np.ascontiguousarray(b, dtype=np.float32)))
    return out.numpy()


def _unbind_hrr(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = binding.unbind(torch.from_numpy(np.ascontiguousarray(c, dtype=np.float32)),
                         torch.from_numpy(np.ascontiguousarray(b, dtype=np.float32)))
    return out.numpy()


def _role_vec(rel_id: int, hop: int, seed: int) -> np.ndarray:
    h = int(hashlib.sha256(f"fs_role::{seed}::{rel_id}::{hop}".encode()).hexdigest(), 16)
    r = np.random.default_rng(h % (2 ** 63 - 1)).standard_normal(N_R).astype(np.float32)
    return r / (np.linalg.norm(r) + 1e-12)


def _role_path(base_rel_id: int, hops: int, seed: int) -> np.ndarray:
    r = _role_vec(base_rel_id, 0, seed)
    for hop in range(1, hops):
        r = _bind_hrr(r, _role_vec(base_rel_id, hop, seed))
    return r


def _bipolar_rows(V: int, N: int, rng) -> np.ndarray:
    return (2.0 * (rng.random((V, N)) > 0.5).astype(np.float32) - 1.0)


def _gen_projection(proj_seed: int) -> np.ndarray:
    """Fixed Gaussian generation codec basis (BGE_DIM, N_G). The clean gen lexicon is sign(bge @ P); the
    ANALOG arm feeds a NOISY HV through the SAME codec (sign(hv @ P)) WITHOUT snapping to a clean codeword
    first -- the analog-repeater. REGEN snaps to a clean concept then emits its clean code -- the digital
    repeater. Both use the same codec basis; the ONLY difference is the regenerative snap."""
    pr = np.random.default_rng(proj_seed)
    return (pr.standard_normal((BGE_DIM, N_G)).astype(np.float32) / np.sqrt(BGE_DIM))


def _sign_codes(bge_unit: np.ndarray, P: np.ndarray) -> np.ndarray:
    """BGE -> codec -> sign -> bipolar (V, N_G). Carries the real cos-cone."""
    return np.where(bge_unit @ P >= 0.0, 1.0, -1.0).astype(np.float32)


def _make_positions(P: int, N: int, rng) -> np.ndarray:
    base = (2.0 * (rng.random(N) > 0.5).astype(np.float32) - 1.0)
    return np.stack([np.roll(base, k) for k in range(P)], axis=0)


def _fix_sign(code):
    return np.where(code == 0.0, 1.0, code).astype(np.float32)


def _digest(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _cv(vals) -> float:
    v = np.asarray(vals, dtype=np.float64)
    m = float(v.mean())
    if abs(m) < 1e-9:
        return 0.0
    return float(v.std(ddof=0) / abs(m))


# ============================================================
# Stage-1 COMPREHEND: content-typed matched filter over disjoint role partitions
# ============================================================


def _comprehend(P_in, rC_subj, rC_obj, bge_subj, bge_obj):
    """P_in (N_R) = bind(rC_subj, bge[S]) + bind(rC_obj, bge[O]) + sum_c bind(rC_ctx_c, bge[ctx_c]) --
    a role-bound perceptual scene under CONTEXT-LOAD superposition. Comprehension = unbind the subject-role
    and object-role (who-did-what parsing), then TYPE each noisy filler by selectional-restriction matched
    filter over its DISJOINT vocab partition (the content-typing cleanup). Error grows with context load +
    vocab scale (matches the proven comprehension envelope). Returns REGEN (typed->clean id + clean BGE) and
    ANALOG (raw noisy unbound estimate, NO typing cleanup) + margins (top1-top2 cos; glass-box)."""
    u_s = _unbind_hrr(P_in, rC_subj)
    u_o = _unbind_hrr(P_in, rC_obj)
    rs = bge_subj @ _unit(u_s)                    # (V_subj,) selectional-restriction typing over subj partition
    ro = bge_obj @ _unit(u_o)                     # (V,)      typing over obj partition
    si = int(np.argmax(rs))
    oi = int(np.argmax(ro))
    s_sorted = np.sort(rs)[::-1]
    o_sorted = np.sort(ro)[::-1]
    s_margin = float(s_sorted[0] - s_sorted[1]) if len(s_sorted) > 1 else 1.0
    o_margin = float(o_sorted[0] - o_sorted[1]) if len(o_sorted) > 1 else 1.0
    return {
        "subj_id": si, "obj_id": oi,
        "subj_clean": _unit(bge_subj[si]), "obj_clean": _unit(bge_obj[oi]),
        "subj_analog": _unit(u_s), "obj_analog": _unit(u_o),   # raw noisy unbound estimates (no typing)
        "s_margin": s_margin, "o_margin": o_margin,
    }


# ============================================================
# Stage-2 STORE + REASON (multi-hop HRR over real BGE)
# ============================================================


def _store_and_reason(subj_vec, obj_vec, distractor_vecs, base_rels, q_rel, hops, seed,
                      broken_rel):
    """Store T = bind(role_subj, subj_vec) + bind(role_path(q_rel), obj_vec)
                 + sum_d bind(role_path(rel_d), distractor_vecs[d]).  Multi-hop unbind recovers obj + subj.
    broken_rel: an UNSTORED role path for the BROKEN discriminator. Returns noisy HVs."""
    T = _bind_hrr(_role_vec(SUBJ_ROLE_ID, 0, seed), subj_vec)
    T = T + _bind_hrr(_role_path(int(q_rel), hops, seed), obj_vec)
    for d in range(len(distractor_vecs)):
        T = T + _bind_hrr(_role_path(int(base_rels[d]), hops, seed), distractor_vecs[d])
    obj_hv = _unbind_hrr(T, _role_path(int(q_rel), hops, seed))
    subj_hv = _unbind_hrr(T, _role_vec(SUBJ_ROLE_ID, 0, seed))
    obj_hv_broken = _unbind_hrr(T, _role_path(int(broken_rel), hops, seed))
    return obj_hv, subj_hv, obj_hv_broken


def _snap_to_partition(hv, bge_part):
    """Regenerative cleanup: snap noisy HV to nearest concept in a partition. Returns (id, clean BGE, margin)."""
    sims = bge_part @ _unit(hv)
    i = int(np.argmax(sims))
    ss = np.sort(sims)[::-1]
    margin = float(ss[0] - ss[1]) if len(ss) > 1 else 1.0
    return i, _unit(bge_part[i]), margin


# ============================================================
# Stage-3 CONTROL-GATE: goal-transport reach WTA + abstain (ridge-fit transport)
# ============================================================


def _fit_goal_transport(bge_train, M_goal):
    """Ridge-fit M_hat (N_R,N_R) of the goal relation on a HELD-OUT train pool: X=bge_train,
    Y=normalize(X @ M_goal). reach(cand)=cos(cand @ M_hat, goal). Reduced-fidelity vs SR-TD (declared)."""
    X = bge_train.astype(np.float32)
    Y = _unit_rows(X @ M_goal)
    G = X.T @ X + RIDGE_LAMBDA * np.eye(N_R, dtype=np.float32)
    return np.linalg.solve(G, X.T @ Y).astype(np.float32)


def _gate_decide(cand_vec, distractor_vecs, goal_vec, M_hat, tau):
    """WTA over {cand} U distractors by reach=cos(v @ M_hat, goal); Go iff max reach > tau else abstain.
    Returns (go: bool, selected_is_cand: bool). cand is index 0."""
    vs = [cand_vec] + list(distractor_vecs)
    reaches = np.array([float(_unit(v @ M_hat) @ goal_vec) for v in vs], dtype=np.float32)
    j = int(np.argmax(reaches))
    go = bool(reaches[j] > tau)
    return go, (j == 0), float(reaches[0])


# ============================================================
# Stage-4 GENERATE: bipolar-BSC ordered-triple decode (partition-restricted)
# ============================================================


def _generate_and_decode(subj_code, rel_code, obj_code, pos, L_subj, L_obj, L_rel):
    """Compose ordered triple + decode each slot (unbind position + partition-restricted argmax).
    Returns partition-LOCAL ids: subj_pred in [0,V_subj), obj_pred in [0,V), rel_pred in [0,n_rel)."""
    ans = pos[0] * subj_code + pos[1] * rel_code + pos[2] * obj_code
    subj_pred = int(np.argmax(L_subj @ (ans * pos[0])))
    rel_pred = int(np.argmax(L_rel @ (ans * pos[1])))
    obj_pred = int(np.argmax(L_obj @ (ans * pos[2])))
    return subj_pred, rel_pred, obj_pred


# ============================================================
# One (regime, seed): full 4-stage chain across all arms + stage-oracle isolation (paired trials)
# ============================================================


def run_regime_seed(regime_name, rc, seed, output_dir, t0, hb_unit, total_units):
    V = rc["V"]                       # object-role partition size
    V_subj = rc["V_subj"]             # subject-role partition size
    D_store, hops, hub = rc["D_store"], rc["hops"], rc["hub_cluster"]
    trials, n_train = rc["trials"], rc["n_train"]
    gate_goal_noise = rc["gate_goal_noise"]
    n_rel = D_store + 8

    rng = np.random.default_rng(1000 + seed + (0 if regime_name == "easy" else 500))
    sem = _load_bge_subset()
    Vpool = sem.shape[0]
    perm = rng.permutation(Vpool)
    subj_rows = perm[:V_subj]
    obj_rows = perm[V_subj:V_subj + V]
    train_rows = perm[V_subj + V:V_subj + V + n_train]
    bge_subj = _unit_rows(sem[subj_rows])          # (V_subj, BGE_DIM)
    bge_obj = _unit_rows(sem[obj_rows])            # (V, BGE_DIM)
    bge_train = _unit_rows(sem[train_rows])        # (n_train, BGE_DIM) held-out gate-transport training

    # comprehension roles (perceptual scene = role-bound superposition; typed by selectional restriction)
    rC_subj = _role_vec(SUBJ_ROLE_ID + 1, 0, seed)
    rC_obj = _role_vec(SUBJ_ROLE_ID + 2, 0, seed)
    rC_ctx = [_role_vec(SUBJ_ROLE_ID + 100 + c, 0, seed) for c in range(rc["L_ctx"])]
    # generation codec + lexicons (partition-restricted decode) + relation codebook + positions
    P_gen = _gen_projection(P_GEN_SEED)                       # shared codec basis (REGEN + ANALOG both use it)
    L_subj = _sign_codes(bge_subj, P_gen)                     # (V_subj, N_G)
    L_obj = _sign_codes(bge_obj, P_gen)                       # (V, N_G)
    L_rel = _bipolar_rows(n_rel, N_G, np.random.default_rng(2000 + seed))
    pos = _make_positions(GEN_SLOTS, N_G, np.random.default_rng(3000 + seed))

    # gate goal transport (true relation) + ridge-fit estimate on a SMALL held-out pool (n_gate_train <
    # N_R -> underdetermined ridge -> imperfect learned dynamics -> gate lands in the proven FAIR band ~0.65,
    # MEASURED@..._pfc_gate...:V1200_d4 gonogo=0.653; NOT a saturated by-construction gate).
    mg = np.random.default_rng(M_GOAL_SEED + seed)
    M_goal = (mg.standard_normal((N_R, N_R)).astype(np.float32) / np.sqrt(N_R))
    n_gt = min(rc["n_gate_train"], n_train)
    M_hat = _fit_goal_transport(bge_train[:n_gt], M_goal)
    # gate Go threshold tau: LOW null-reach percentile so Go-rate is high and the gate's error is a genuine
    # goal-conditioned WTA SELECTION error among confusable candidates (matches the proven gate's error mode:
    # picking the right target 65% of the time), NOT a bimodal abstain cliff.
    tg = np.random.default_rng(4000 + seed)
    n_null = min(256, n_train)
    null_c = bge_train[tg.integers(0, n_train, size=n_null)]
    null_g = _unit_rows(bge_train[tg.integers(0, n_train, size=n_null)] @ M_goal)
    null_reach = np.array([float(_unit(null_c[i] @ M_hat) @ null_g[i]) for i in range(n_null)], dtype=np.float32)
    tau = float(np.percentile(null_reach, 20))
    gate_n_tight = rc["gate_n_tight"]

    hit = {a: 0 for a in ARMS}
    rec_stream = {a: [] for a in ARMS}
    # stage-oracle isolation counters
    st_comp = 0    # comprehend: argmax recovers TRUE (subj,obj) from the bundle
    st_reason = 0  # reason: snap of unbind recovers TRUE obj (given clean stored fact + distractors)
    st_gate = 0    # gate: Go AND selects TRUE clean candidate (given clean cand + distractors)
    st_gen = 0     # generate: decode recovers TRUE triple (given clean codes)
    wa_c_margins = []  # top1-top2 margins of CORRECT REGEN cleanup commits (comprehension + reason snap)
    wa_w_margins = []  # top1-top2 margins of WRONG REGEN cleanup commits (the confident-wrong candidates)
    glassbox = []
    cluster_cones = []

    for tr in range(trials):
        trng = np.random.default_rng(50000 + seed * 131 + tr + (0 if regime_name == "easy" else 777))
        S = int(trng.integers(V_subj))
        # queried object O + hub-cluster distractor objects
        if hub:
            a = int(trng.integers(V))
            sims = bge_obj @ bge_obj[a]
            k = D_store
            idx = np.argpartition(-sims, k)[:k]
            idx = idx[np.argsort(-sims[idx])]
            members = list(int(x) for x in idx[:k])
            trng.shuffle(members)
        else:
            members = [int(x) for x in trng.choice(V, size=D_store, replace=False)]
        O = members[0]
        distractor_ids = members[1:]                          # D_store-1 other stored objects (memory crowd)
        base_rels = list(int(x) for x in trng.choice(n_rel, size=D_store - 1, replace=False))
        q_rel = int(trng.choice([r for r in range(n_rel) if r not in base_rels]))
        used = set(base_rels + [q_rel])
        unused = [r for r in range(n_rel) if r not in used]
        broken_rel = int(unused[trng.integers(len(unused))]) if unused else (q_rel + 3) % n_rel

        # cluster confusability diagnostic
        mem = np.array([O] + distractor_ids)
        Msub = bge_obj[mem]
        Sc = Msub @ Msub.T
        cluster_cones.append(float(Sc[~np.eye(len(mem), dtype=bool)].mean()))

        # goal for the gate: transform of TRUE object, IMPERFECTLY SPECIFIED. gate_goal_noise=w in [0,1] mixes
        # the true-object transform with a random direction (signal-relative): a partial/ambiguous goal makes
        # the goal-conditioned WTA genuinely ambiguous among the hub-neighbour candidates -> gate lands in its
        # proven FAIR band ~0.65 (else goal==O's exact transform is trivially separable, gate saturates at 1).
        w = gate_goal_noise
        gnoise = trng.standard_normal(N_R).astype(np.float32)
        goal_vec = _unit((1.0 - w) * _unit(bge_obj[O] @ M_goal) + w * _unit(gnoise))
        distractor_vecs = [_unit(bge_obj[d]) for d in distractor_ids]
        # gate WTA competitors = O's TIGHTEST cosine neighbours (small reach margins -> genuine selection
        # error); a separate tight set from the reasoning hub so gate difficulty is its own lever.
        go2 = bge_obj @ bge_obj[O]
        gnn = np.argpartition(-go2, gate_n_tight + 1)[:gate_n_tight + 2]
        gnn = [int(x) for x in gnn[np.argsort(-go2[gnn])] if int(x) != O][:gate_n_tight]
        gate_distractor_vecs = [_unit(bge_obj[i]) for i in gnn]
        rel_code = L_rel[q_rel]

        # ---------- STAGE-1 COMPREHEND (role-bound perceptual scene under context load) ----------
        # context-load fillers = near-neighbours of O (real selectional-restriction typing confusion): the
        # object-role typing argmax must pick O out of a crowd of its own cosine-cluster neighbours.
        oo = bge_obj @ bge_obj[O]
        kk = len(rC_ctx) + 2
        nn = np.argpartition(-oo, kk)[:kk + 1]
        nn = [int(x) for x in nn[np.argsort(-oo[nn])] if int(x) != O]
        ctx_ids = nn[:len(rC_ctx)]
        P_in = _bind_hrr(rC_subj, _unit(bge_subj[S])) + _bind_hrr(rC_obj, _unit(bge_obj[O]))
        for c, cid in enumerate(ctx_ids):
            P_in = P_in + _bind_hrr(rC_ctx[c], _unit(bge_obj[cid]))
        comp = _comprehend(P_in, rC_subj, rC_obj, bge_subj, bge_obj)
        # glass-box wrong_attractor: REGEN comprehension commits (2 steps: subj + obj) -- record margins by
        # correctness; confidence threshold is self-calibrated post-loop (median CORRECT-commit margin).
        for (pred, true, margin) in [(comp["subj_id"], S, comp["s_margin"]),
                                     (comp["obj_id"], O, comp["o_margin"])]:
            (wa_c_margins if pred == true else wa_w_margins).append(margin)

        # ---------- STAGE-ORACLE ISOLATION (ground-truth input per stage) ----------
        # comprehend isolated: argmax recovers true subj AND true obj
        st_comp += int(comp["subj_id"] == S and comp["obj_id"] == O)
        # reason isolated: store the TRUE clean fact + distractors; snap recovers TRUE obj
        o_hv_iso, s_hv_iso, _ = _store_and_reason(
            _unit(bge_subj[S]), _unit(bge_obj[O]), distractor_vecs, base_rels, q_rel, hops, seed, broken_rel)
        r_obj_iso, _, r_margin_iso = _snap_to_partition(o_hv_iso, bge_obj)
        r_subj_iso, _, _ = _snap_to_partition(s_hv_iso, bge_subj)
        st_reason += int(r_obj_iso == O and r_subj_iso == S)
        # gate isolated: TRUE clean candidate + distractors; Go AND selects candidate
        go_iso, selc_iso, _ = _gate_decide(_unit(bge_obj[O]), gate_distractor_vecs, goal_vec, M_hat, tau)
        st_gate += int(go_iso and selc_iso)
        # generate isolated: TRUE clean codes decode the true triple
        sp_iso, rp_iso, op_iso = _generate_and_decode(
            L_subj[S], rel_code, L_obj[O], pos, L_subj, L_obj, L_rel)
        st_gen += int(sp_iso == S and rp_iso == q_rel and op_iso == O)

        # ---------- FULL CHAIN per arm ----------
        for arm in ARMS:
            if arm == "oracle_chain":
                # every seam fed ground truth
                subj_in, obj_in = _unit(bge_subj[S]), _unit(bge_obj[O])
                o_hv, s_hv, o_hv_brk = _store_and_reason(
                    subj_in, obj_in, distractor_vecs, base_rels, q_rel, hops, seed, broken_rel)
                cand_id, cand_vec, cand_code_obj = O, _unit(bge_obj[O]), L_obj[O]
                subj_id_gen, subj_code = S, L_subj[S]
            elif arm == "regen":
                # snap at every seam
                subj_in, obj_in = comp["subj_clean"], comp["obj_clean"]
                o_hv, s_hv, o_hv_brk = _store_and_reason(
                    subj_in, obj_in, distractor_vecs, base_rels, q_rel, hops, seed, broken_rel)
                r_obj, r_obj_vec, r_marg = _snap_to_partition(o_hv, bge_obj)
                r_subj, r_subj_vec, _ = _snap_to_partition(s_hv, bge_subj)
                (wa_c_margins if r_obj == O else wa_w_margins).append(r_marg)
                cand_id, cand_vec, cand_code_obj = r_obj, r_obj_vec, L_obj[r_obj]
                subj_id_gen, subj_code = r_subj, L_subj[r_subj]
            elif arm == "analog":
                # pass noisy estimates at every seam (no snap)
                subj_in, obj_in = comp["subj_analog"], comp["obj_analog"]
                o_hv, s_hv, o_hv_brk = _store_and_reason(
                    subj_in, obj_in, distractor_vecs, base_rels, q_rel, hops, seed, broken_rel)
                cand_id, cand_vec = -1, _unit(o_hv)   # raw noisy HV candidate (no snap)
                cand_code_obj = _fix_sign(np.sign(o_hv @ P_gen))   # noisy HV thru the SAME codec (analog)
                subj_id_gen, subj_code = -1, _fix_sign(np.sign(s_hv @ P_gen))
            else:  # broken
                subj_in, obj_in = comp["subj_clean"], comp["obj_clean"]
                o_hv, s_hv, o_hv_brk = _store_and_reason(
                    subj_in, obj_in, distractor_vecs, base_rels, q_rel, hops, seed, broken_rel)
                r_obj, r_obj_vec, _ = _snap_to_partition(o_hv_brk, bge_obj)   # severed-identity object
                r_subj, r_subj_vec, _ = _snap_to_partition(s_hv, bge_subj)
                cand_id, cand_vec, cand_code_obj = r_obj, r_obj_vec, L_obj[r_obj]
                subj_id_gen, subj_code = r_subj, L_subj[r_subj]

            # ---------- STAGE-3 GATE ----------
            if arm == "oracle_chain":
                go, sel_cand = True, True     # WIRING ceiling: bypass gate abstention (decoder-only wiring)
            else:
                go, sel_cand, _reach = _gate_decide(cand_vec, gate_distractor_vecs, goal_vec, M_hat, tau)

            # ---------- STAGE-4 GENERATE + score ----------
            sp, rp, op = _generate_and_decode(
                subj_code, rel_code, cand_code_obj, pos, L_subj, L_obj, L_rel)
            exact = int(go and sel_cand and sp == S and rp == q_rel and op == O)
            hit[arm] += exact
            rec_stream[arm].append(int(op))

        if tr < 3:
            glassbox.append({
                "regime": regime_name, "seed": seed, "trial": tr,
                "S": S, "O": O, "q_rel": q_rel, "hops": hops, "D_store": D_store, "hub": hub,
                "cluster_cone": round(cluster_cones[-1], 4),
                "comp_subj_pred": comp["subj_id"], "comp_obj_pred": comp["obj_id"],
                "comp_subj_margin": round(comp["s_margin"], 4), "comp_obj_margin": round(comp["o_margin"], 4),
                "reason_iso_obj_pred": r_obj_iso, "reason_iso_margin": round(r_margin_iso, 4),
                "tau": round(tau, 4),
            })

    n = float(trials)
    end2end = {a: hit[a] / n for a in ARMS}
    stage_acc = {
        "comprehend": st_comp / n,
        "reason": st_reason / n,
        "gate": st_gate / n,
        "generate": st_gen / n,
    }
    product_of_stages = float(np.prod([stage_acc[k] for k in ("comprehend", "reason", "gate", "generate")]))
    compounding = {a: (end2end[a] / product_of_stages if product_of_stages > 1e-9 else 0.0) for a in ARMS}
    # self-calibrated wrong_attractor: a WRONG REGEN cleanup commit is "confident" iff its top1-top2 margin
    # is >= the median margin of CORRECT commits (i.e. as confident as a typical correct one). wrong_attractor
    # _rate = fraction of ALL cleanup steps that are confident-wrong; confident_wrong_frac = of the ERRORS,
    # what fraction look confident (the research note's "confident-wrong dominates" claim, P=0.40).
    wa_total = len(wa_c_margins) + len(wa_w_margins)
    wa_thr = float(np.median(wa_c_margins)) if wa_c_margins else 0.0
    n_conf_wrong = int(sum(1 for mg in wa_w_margins if mg >= wa_thr))
    wrong_attractor_rate = (n_conf_wrong / wa_total) if wa_total else 0.0
    cleanup_error_rate = (len(wa_w_margins) / wa_total) if wa_total else 0.0
    confident_wrong_frac = (n_conf_wrong / len(wa_w_margins)) if wa_w_margins else 0.0
    cluster_cone = round(float(np.mean(cluster_cones)), 4)
    artifacts = {a: _digest(rec_stream[a]) for a in ARMS}

    _heartbeat(output_dir, hb_unit, total_units, t0, extra={
        "regime": regime_name, "seed": seed,
        "regen": round(end2end["regen"], 3), "analog": round(end2end["analog"], 3),
        "oracle_chain": round(end2end["oracle_chain"], 3), "broken": round(end2end["broken"], 3),
        "product": round(product_of_stages, 3), "compound_regen": round(compounding["regen"], 3)})
    _say(f"  [{regime_name} seed {seed}] V={V} Vsubj={V_subj} D={D_store} hops={hops} hub={hub} "
         f"cone={cluster_cone:.3f} | end2end regen={end2end['regen']:.3f} analog={end2end['analog']:.3f} "
         f"oracle={end2end['oracle_chain']:.3f} broken={end2end['broken']:.3f} | "
         f"stages(C={stage_acc['comprehend']:.2f} R={stage_acc['reason']:.2f} G={stage_acc['gate']:.2f} "
         f"Gen={stage_acc['generate']:.2f}) product={product_of_stages:.3f} "
         f"compound(regen)={compounding['regen']:.3f} wa_rate={wrong_attractor_rate:.3f}")
    return {
        "end2end": end2end, "stage_acc": stage_acc, "product_of_stages": product_of_stages,
        "compounding": compounding, "wrong_attractor_rate": wrong_attractor_rate,
        "cleanup_error_rate": cleanup_error_rate, "confident_wrong_frac": confident_wrong_frac,
        "wa_confidence_thr": round(wa_thr, 4),
        "cluster_cone": cluster_cone, "artifacts": artifacts, "tau": tau, "glassbox": glassbox,
    }


# ============================================================
# Config
# ============================================================


def get_regimes(mode: str):
    """Difficulty axes (V, V_subj, D_store, hops, hub) held at FULL in smoke; smoke reduces trials/seeds/train."""
    if mode == "selftest":
        easy = {"V": 128, "V_subj": 64, "D_store": 3, "hops": 1, "hub_cluster": False,
                "trials": 8, "n_train": 1536, "L_ctx": 1, "n_gate_train": 512, "gate_n_tight": 4,
                "gate_goal_noise": 0.0}
        hard = {"V": 256, "V_subj": 128, "D_store": 5, "hops": 2, "hub_cluster": True,
                "trials": 8, "n_train": 1536, "L_ctx": 4, "n_gate_train": 512, "gate_n_tight": 6,
                "gate_goal_noise": 0.0}
        seeds = (7,)
    elif mode == "smoke":
        easy = {"V": 1024, "V_subj": 512, "D_store": 3, "hops": 1, "hub_cluster": False,
                "trials": 24, "n_train": 2048, "L_ctx": 2, "n_gate_train": 700, "gate_n_tight": 6,
                "gate_goal_noise": 0.0}
        hard = {"V": 4096, "V_subj": 1024, "D_store": 10, "hops": 3, "hub_cluster": True,
                "trials": 24, "n_train": 2048, "L_ctx": 15, "n_gate_train": 40, "gate_n_tight": 16,
                "gate_goal_noise": 0.3}
        seeds = (7, 13, 19)
    else:  # full
        easy = {"V": 1024, "V_subj": 512, "D_store": 3, "hops": 1, "hub_cluster": False,
                "trials": 60, "n_train": 2048, "L_ctx": 2, "n_gate_train": 700, "gate_n_tight": 6,
                "gate_goal_noise": 0.0}
        hard = {"V": 4096, "V_subj": 1024, "D_store": 10, "hops": 3, "hub_cluster": True,
                "trials": 60, "n_train": 2048, "L_ctx": 15, "n_gate_train": 40, "gate_n_tight": 16,
                "gate_goal_noise": 0.3}
        seeds = SEEDS
    return {"easy": easy, "hard": hard}, seeds


# ============================================================
# Verdict
# ============================================================


def _agg(per):
    """per[regime][field] -> list over seeds. Return means + per-seed."""
    out = {}
    for r in REGIME_ORDER:
        e = {a: [d["end2end"][a] for d in per[r]] for a in ARMS}
        comp = {a: [d["compounding"][a] for d in per[r]] for a in ARMS}
        stg = {k: [d["stage_acc"][k] for d in per[r]] for k in ("comprehend", "reason", "gate", "generate")}
        out[r] = {
            "end2end": {a: round(float(np.mean(e[a])), 4) for a in ARMS},
            "end2end_per_seed": {a: [round(v, 4) for v in e[a]] for a in ARMS},
            "compounding": {a: round(float(np.mean(comp[a])), 4) for a in ARMS},
            "compounding_per_seed": {a: [round(v, 4) for v in comp[a]] for a in ARMS},
            "stage_acc": {k: round(float(np.mean(stg[k])), 4) for k in stg},
            "product_of_stages": round(float(np.mean([d["product_of_stages"] for d in per[r]])), 4),
            "wrong_attractor_rate": round(float(np.mean([d["wrong_attractor_rate"] for d in per[r]])), 4),
            "cleanup_error_rate": round(float(np.mean([d["cleanup_error_rate"] for d in per[r]])), 4),
            "confident_wrong_frac": round(float(np.mean([d["confident_wrong_frac"] for d in per[r]])), 4),
            "cluster_cone": round(float(np.mean([d["cluster_cone"] for d in per[r]])), 4),
        }
    return out


def _wiring_gates(agg_r, regime_name):
    """WIRING + identity discriminators at one regime."""
    oc = agg_r["end2end"]["oracle_chain"]
    brk = agg_r["end2end"]["broken"]
    if oc < WIRING_FLOOR:
        return False, (f"[{regime_name}] ORACLE_CHAIN end2end={oc:.3f} < {WIRING_FLOOR}: 4-stage machinery "
                       f"WIRING failed (cannot attribute chain failure to composition)")
    if brk > BROKEN_CEIL:
        return False, (f"[{regime_name}] BROKEN end2end={brk:.3f} > {BROKEN_CEIL}: severed-identity chain did "
                       f"NOT collapse -> accuracy not attributable to genuine reasoning (leakage)")
    return True, "ok"


def _stages_in_band(agg_hard):
    """META_RULE_AG: the LOSSY subsystems (comprehend, reason) must each be genuine error sources in band;
    the gate must be in its proven FAIR band; generate is the decoder-WIRING ceiling (near-saturation is
    EXPECTED and REQUIRED -- it is what ORACLE_CHAIN measures) so it carries only a wiring floor."""
    s = agg_hard["stage_acc"]
    for k in ("comprehend", "reason"):
        if not (STAGE_LO < s[k] < STAGE_HI):
            return False, (f"isolated lossy stage '{k}' acc={s[k]:.3f} out of band ({STAGE_LO},{STAGE_HI}) at "
                           f"hard: stage floored/saturated -> not a genuine error source, compounding "
                           f"uninterpretable")
    if not (GATE_FAIR_LO <= s["gate"] <= GATE_FAIR_HI):
        return False, (f"isolated gate acc={s['gate']:.3f} outside FAIR band [{GATE_FAIR_LO},{GATE_FAIR_HI}] "
                       f"(proven ~0.65): re-tune gate difficulty before trusting composition")
    if s["generate"] < WIRING_FLOOR:
        return False, (f"isolated generate (decoder wiring) acc={s['generate']:.3f} < {WIRING_FLOOR}: the "
                       f"machinery cannot decode a clean proposition -> composition question unanswerable")
    return True, "ok"


def classify(agg, mode):
    e_h = agg["hard"]["end2end"]
    comp_h = agg["hard"]["compounding"]
    regen, analog = e_h["regen"], e_h["analog"]
    cr_regen = comp_h["regen"]
    margin = regen - analog
    cv_regen = _cv(agg["hard"]["end2end_per_seed"]["regen"])
    prod = agg["hard"]["product_of_stages"]
    s = agg["hard"]["stage_acc"]
    wa = agg["hard"]["wrong_attractor_rate"]

    diag = (f"HARD: regen_e2e={regen:.3f} analog_e2e={analog:.3f} oracle={e_h['oracle_chain']:.3f} "
            f"broken={e_h['broken']:.3f} | product_of_stages={prod:.3f} "
            f"(C={s['comprehend']:.2f} R={s['reason']:.2f} G={s['gate']:.2f} Gen={s['generate']:.2f}) | "
            f"compounding_ratio regen={cr_regen:.3f} analog={comp_h['analog']:.3f} | "
            f"margin(regen-analog)={margin:+.3f} cv(regen)={cv_regen:.3f} wrong_attractor_rate={wa:.3f}")

    # by-construction WIRING + identity rails (both regimes)
    for r in REGIME_ORDER:
        ok, reason = _wiring_gates(agg[r], r)
        if not ok:
            return "DISCRIMINATOR_DID_NOT_FIRE", f"{reason}. {diag}"
    # isolated stages in band (hard)
    sb_ok, sb_reason = _stages_in_band(agg["hard"])

    if mode == "smoke":
        if not sb_ok:
            return ("SMOKE_ITERATE_REGIME",
                    f"STAGE NOT IN BAND: {sb_reason}. Re-spec before FULL. {diag}")
        # smoke clears on machinery + stages-in-band + measurable REGEN>>ANALOG preview; the deliverable
        # verdict is FULL-only (canonical=remote). HARD_FAIL (relay compounds) is an ALLOWED outcome.
        return ("SMOKE_MACHINERY_OK",
                f"SMOKE OK: 4-stage chain runs AT N_R={N_R} N_G={N_G}; ORACLE_CHAIN wiring recovers + BROKEN "
                f"collapses in both regimes; 4 isolated stages in band + gate FAIR; arms differ. PREVIEW: "
                f"REGEN keeps compounding_ratio={cr_regen:.3f}, beats ANALOG by {margin:+.3f}. Deliverable "
                f"verdict is FULL-only. {diag}")

    # ---- FULL research verdict (canonical) ----
    if not sb_ok:
        return ("INCONCLUSIVE_STAGE_OUT_OF_BAND", f"{sb_reason}. {diag}")

    if (regen >= HP_END2END and cr_regen >= HP_COMPOUND and margin >= HP_MARGIN and cv_regen < HP_CV_MAX):
        return ("HARD_PASS",
                f"COMPONENTS INTEGRATE AT 4-STAGE HARD REGIME: regenerative cleanup keeps the full stack "
                f"COMPOSING -- end2end[REGEN]={regen:.3f} (>= {HP_END2END}) at compounding_ratio={cr_regen:.3f} "
                f"(>= {HP_COMPOUND}: near-independent multiplicative stages, NOT an emergent compounding tax), "
                f"beating ANALOG pass-through by {margin:+.3f} (>= {HP_MARGIN}), cross-seed cv={cv_regen:.3f} "
                f"(< {HP_CV_MAX}). The digital-repeater mechanism survives being chained across 4 real "
                f"subsystems. Each subsystem's OWN accuracy is the lever, not an un-attackable integration "
                f"tax. wrong_attractor_rate={wa:.3f} (standing auditability quantity). {diag}")
    if (regen < HF_END2END and cr_regen < HF_COMPOUND):
        return ("HARD_FAIL",
                f"COMPONENTS DO NOT INTEGRATE AT 4-STAGE DEPTH EVEN WITH CLEANUP (decisive negative): "
                f"end2end[REGEN]={regen:.3f} (< {HF_END2END}) DESPITE compounding_ratio={cr_regen:.3f} "
                f"(< {HF_COMPOUND}) -- even with regenerative cleanup at every seam the real chain "
                f"underperforms what independent per-stage multiplication predicts. Pairwise relay is "
                f"NECESSARY-BUT-NOT-SUFFICIENT; a sustained cross-stage working-memory / thalamic buffer "
                f"(not point-to-point cleanup) is the next brain-component lever. {diag}")
    return ("MIDDLE_BAND",
            f"PARTIAL INTEGRATION: end2end[REGEN]={regen:.3f}, compounding_ratio={cr_regen:.3f}, "
            f"margin(regen-analog)={margin:+.3f}, cv={cv_regen:.3f} -- REGEN composes better than ANALOG but "
            f"does not clear the full HARD_PASS bar (need end2end>={HP_END2END} AND compound>={HP_COMPOUND} AND "
            f"margin>={HP_MARGIN} AND cv<{HP_CV_MAX}). Quantify which stage dominates the shortfall. {diag}")


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    regimes, seeds = get_regimes(mode)
    expected_n_units = len(seeds) * len(REGIME_ORDER) * len(ARMS)
    total_seed_regime = len(seeds) * len(REGIME_ORDER)
    _write_start_marker(output_dir, mode, expected_n_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N_R={N_R} N_G={N_G} seeds={seeds} arms={ARMS}")
    for r in REGIME_ORDER:
        rc = regimes[r]
        _say(f"  regime={r}: V={rc['V']} V_subj={rc['V_subj']} D_store={rc['D_store']} hops={rc['hops']} "
             f"hub={rc['hub_cluster']} trials={rc['trials']} n_train={rc['n_train']}")

    per = {r: [] for r in REGIME_ORDER}
    artifacts_by = {r: {} for r in REGIME_ORDER}
    glassbox_all = []
    hb = 0
    for regime_name in REGIME_ORDER:
        rc = regimes[regime_name]
        for seed in seeds:
            res = run_regime_seed(regime_name, rc, seed, output_dir, t0, hb, total_seed_regime)
            hb += 1
            per[regime_name].append(res)
            artifacts_by[regime_name][str(seed)] = res["artifacts"]
            glassbox_all.extend(res["glassbox"])

    # arms_differ (META_RULE_AF): the 3 MECHANISM arms (regen/analog/broken) must produce hash-distinct
    # inter-stage id streams per unit. oracle_chain is EXEMPTED (declared): it is the decoder-WIRING control
    # and coincides EXACTLY with regen's decoded-id stream on trials where regen recovers ground truth (the
    # machinery ceiling), so bit-identity between regen and oracle_chain is the INTENDED wiring behaviour,
    # not an arm-implementation bug. At the hard regime they diverge (regen < oracle_chain), and that
    # divergence IS measured.
    _AF_ARMS = ["regen", "analog", "broken"]
    _AF_EXEMPT = [("regen", "oracle_chain")]
    arms_differ_ok = True
    for r in REGIME_ORDER:
        for _sd, art in artifacts_by[r].items():
            for i in range(len(_AF_ARMS)):
                for j in range(i + 1, len(_AF_ARMS)):
                    if art[_AF_ARMS[i]] == art[_AF_ARMS[j]]:
                        arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError(
            "META_RULE_AF VIOLATION: two MECHANISM arms (regen/analog/broken) produced bit-identical "
            "inter-stage id streams (arm-implementation bug)")

    agg = _agg(per)
    verdict, vmsg = classify(agg, mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: 4-stage integration chain (comprehend->reason->gate->generate), "
                   f"regenerative-vs-analog, hard regime ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(seeds),
        "n_units": len(seeds) * len(REGIME_ORDER) * len(ARMS),
        "expected_n_units": expected_n_units,
        "cardinality_ok": True,
        "config": {
            "N_R": N_R, "N_G": N_G, "BGE_DIM": BGE_DIM, "GEN_SLOTS": GEN_SLOTS,
            "seeds": list(seeds), "RIDGE_LAMBDA": RIDGE_LAMBDA, "arms": ARMS,
            "regimes": {r: {k: regimes[r][k] for k in
                            ("V", "V_subj", "D_store", "hops", "hub_cluster", "trials", "n_train", "L_ctx",
                             "n_gate_train", "gate_n_tight", "gate_goal_noise")}
                        for r in REGIME_ORDER},
            "stages": ["comprehend_role_typing_selectional_restriction",
                       "store_reason_HRR_multihop_hubcrowd_real_BGE_hdlab_binding",
                       "control_gate_goal_transport_reach_WTA_abstain_ridge_fit",
                       "generate_bipolar_BSC_partition_restricted_decode"],
            "regen_seam": "argmax_to_nearest_known_codeword_at_every_seam",
            "analog_seam": "softmax_blend_estimate_plus_raw_noisy_HV_plus_randproj_code_no_snap",
            "gate_transport_fidelity": "ridge_fit_on_heldout_pool_REDUCED_vs_SR_TD_declared_SHAPE_DRIFT",
            "real_filler_cache": str(SUBSET_PATH.relative_to(REPO)).replace("\\", "/"),
        },
        "regimes": {
            r: {
                "end2end": agg[r]["end2end"],
                "end2end_per_seed": agg[r]["end2end_per_seed"],
                "compounding_ratio": agg[r]["compounding"],
                "compounding_ratio_per_seed": agg[r]["compounding_per_seed"],
                "stage_acc_isolated": agg[r]["stage_acc"],
                "product_of_stages": agg[r]["product_of_stages"],
                "wrong_attractor_rate": agg[r]["wrong_attractor_rate"],
                "cleanup_error_rate": agg[r]["cleanup_error_rate"],
                "confident_wrong_frac": agg[r]["confident_wrong_frac"],
                "cluster_cone": agg[r]["cluster_cone"],
                "chance_obj_acc_THEORETICAL": round(1.0 / regimes[r]["V"], 6),
            } for r in REGIME_ORDER
        },
        "key_comparison": {
            "hard_regen_end2end": agg["hard"]["end2end"]["regen"],
            "hard_analog_end2end": agg["hard"]["end2end"]["analog"],
            "hard_regen_minus_analog": round(agg["hard"]["end2end"]["regen"]
                                             - agg["hard"]["end2end"]["analog"], 4),
            "hard_compounding_ratio_regen": agg["hard"]["compounding"]["regen"],
            "hard_compounding_ratio_analog": agg["hard"]["compounding"]["analog"],
            "hard_product_of_stages": agg["hard"]["product_of_stages"],
            "hard_wrong_attractor_rate": agg["hard"]["wrong_attractor_rate"],
            "cv_regen_hard": round(_cv(agg["hard"]["end2end_per_seed"]["regen"]), 4),
            "components_integrate_at_4stage_hard": bool(
                agg["hard"]["end2end"]["regen"] >= HP_END2END
                and agg["hard"]["compounding"]["regen"] >= HP_COMPOUND
                and (agg["hard"]["end2end"]["regen"] - agg["hard"]["end2end"]["analog"]) >= HP_MARGIN
                and _cv(agg["hard"]["end2end_per_seed"]["regen"]) < HP_CV_MAX),
        },
        "controls": {
            "oracle_chain_end2end": {r: agg[r]["end2end"]["oracle_chain"] for r in REGIME_ORDER},
            "broken_end2end": {r: agg[r]["end2end"]["broken"] for r in REGIME_ORDER},
            "wiring_ok": {r: bool(agg[r]["end2end"]["oracle_chain"] >= WIRING_FLOOR) for r in REGIME_ORDER},
            "broken_collapsed": {r: bool(agg[r]["end2end"]["broken"] <= BROKEN_CEIL) for r in REGIME_ORDER},
        },
        "glassbox_trace": glassbox_all,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_artifacts": artifacts_by,
        "bands": {"WIRING_FLOOR": WIRING_FLOOR, "BROKEN_CEIL": BROKEN_CEIL, "HP_END2END": HP_END2END,
                  "HP_COMPOUND": HP_COMPOUND, "HP_MARGIN": HP_MARGIN, "HP_CV_MAX": HP_CV_MAX,
                  "HF_END2END": HF_END2END, "HF_COMPOUND": HF_COMPOUND, "STAGE_LO": STAGE_LO,
                  "STAGE_HI": STAGE_HI, "GATE_FAIR_LO": GATE_FAIR_LO, "GATE_FAIR_HI": GATE_FAIR_HI,
                  "WRONG_ATTR_MARGIN": WRONG_ATTR_MARGIN},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    regimes, _seeds = get_regimes("selftest")
    res = {}
    for regime_name in REGIME_ORDER:
        res[regime_name] = run_regime_seed(regime_name, regimes[regime_name], 7, output_dir, t0, 0, 2)
    # formula self-test: WIRING (oracle_chain recovers) AND identity discriminator alive (broken collapses
    # below oracle) in BOTH regimes; REGEN >= ANALOG directionally at hard; product+compounding computable.
    ok = True
    for r in REGIME_ORDER:
        e = res[r]["end2end"]
        ok = ok and (e["oracle_chain"] >= 0.50) and (e["broken"] <= e["oracle_chain"] - 0.20)
    eh = res["hard"]["end2end"]
    ok = ok and (eh["regen"] >= eh["analog"])
    ok = ok and (res["hard"]["product_of_stages"] > 0.0)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: "
         f"easy(oracle={res['easy']['end2end']['oracle_chain']:.3f} broken={res['easy']['end2end']['broken']:.3f}) "
         f"hard(oracle={eh['oracle_chain']:.3f} broken={eh['broken']:.3f} regen={eh['regen']:.3f} "
         f"analog={eh['analog']:.3f} product={res['hard']['product_of_stages']:.3f} "
         f"compound_regen={res['hard']['compounding']['regen']:.3f}) [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
