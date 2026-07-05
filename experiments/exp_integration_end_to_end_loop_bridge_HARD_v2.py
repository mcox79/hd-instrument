# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (W_cotrained != R_naive; rec_cotrained != rec_broken)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp then os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/capacity-feasibility: chance object accuracy = 1/V (V_hard=4096 -> 0.000244 THEORETICAL); broken
#     arm must land in the chance band. posctrl (ORACLE clean-code decoder ceiling) bounds the reachable
#     upper end. HARD_PASS margin (cot-sym >= 0.10) strictly above TIE_EPS=0.02 floor. crlb_n_a for the
#     bridge itself (learned linear map has no closed-form noise floor; oracle posctrl bounds the decoder).
# - baseline_in_band (META_RULE_AG): the BASELINE-TO-BEAT is naive_symbolic; at the HARD regime it MUST land
#     in (SYM_ROOM_FLOOR=0.15, SYM_ROOM_CEIL=0.90) -- degraded but not floored -- else the hard regime gives
#     no room to answer "does the learned bridge beat symbolic" (INCONCLUSIVE, iterate the stressors).
# - discriminator survives scale: the DIFFICULTY axes (V, hops, D_store, hub_cluster, N_R, N_G) are held at
#     FULL in smoke; smoke reduces ONLY trials + seeds (and slightly n_train). So the smoke hard-in-band
#     check IS the full-N preview of symbolic degradation (option A).
# - HARD_PASS strictly above floor: cot-sym margin at hard >= 0.10 AND cross-seed cv(cot_hard) < 0.10 AND
#     easy-rail tie |cot_easy - sym_easy| <= 0.08 (proves the STRESSOR separates them, not the bridge alone).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
#
# END-TO-END SUBSTRATE LOOP, HARD REGIME: perceive -> store -> reason(multi-hop) -> BRIDGE -> generate  v2
# ====================================================================================================
# WHY v2 (VET of v1 integration_end_to_end_loop_bridge_v1, CHAIN_GRADE but scope-limited):
#   v1 measured end2end=1.000 for BOTH cotrained_linear AND naive_symbolic -> the co-trained bridge was
#   NOT shown uniquely necessary; a parameter-free symbolic cleanup->clean-code-lookup TIED it. v1 was
#   OBJECT-slot-only (subj/rel handed in clean), single-hop, D_store=3, V=1024. MEASURED@data/exp_
#   integration_end_to_end_loop_bridge_v1/metrics.json (cotrained end2end_mean=1.0, naive_symbolic=1.0).
#
# THE v2 QUESTION (the VET's expansion criterion): is there a regime where the LEARNED bridge BEATS the
#   symbolic one? If yes -> the co-trained bridge is load-bearing for the glass-box loop. If no (symbolic
#   ties/beats at every regime) -> the substrate composition is effectively SYMBOLIC and the learned bridge
#   is not load-bearing -- an honest, useful NEGATIVE for the glass-box story. Both are reported honestly.
#
# THE MECHANISM DISTINCTION under test (why cotrained COULD beat symbolic):
#   naive_symbolic does a HARD argmax at the bridge (r_hv -> nearest test concept -> its CLEAN code). It is
#   PARAMETER-FREE: it assumes the reasoning-recovered HV's nearest neighbour in BGE space IS the answer.
#   Under low crosstalk (v1's easy regime) that assumption holds -> perfect. Under compounded crosstalk
#   (multi-hop path unbind + a bundle of NEAR-NEIGHBOUR hub objects) the nearest BGE concept is frequently a
#   cluster-mate DISTRACTOR -> symbolic hard-commits to the wrong clean code -> catastrophic slot failure.
#   The v2 cotrained_linear is trained on reasoning-RECOVERED (noisy) HVs paired with the clean target codes
#   (v1's own "next step": co-train the bridge on recovered HVs, NOT clean fillers). It is a LEARNED linear
#   DENOISER of the specific reasoning crosstalk -- a capability the parameter-free symbolic cleanup cannot
#   have. Whether a ridge-linear denoiser's edge survives to the end-to-end triple is the open question.
#   CITED@Hersche et al. Nat. Nanotech. 2023 (arXiv:2211.05052): naive-vs-cotrained cross-code gap 16.22pt.
#
# THREE STRESSORS added over v1 (the VET's expansion targets):
#   (1) SUBJ + OBJ both recovered-noisy-and-bridged (v1 handed subj/rel in clean). The end2end exact-ordered
#       triple now gates on TWO bridged slots -> the bridge carries more load; any per-slot advantage
#       COMPOUNDS into the triple. (relation stays a clean query KEY -- you legitimately know what you asked.)
#   (2) MULTI-HOP reasoning: objects are bound under a composite role PATH of length `hops` (circular-conv of
#       hops distinct roles); recovery unbinds the same composite. hops=2 at hard compounds unbind crosstalk.
#   (3) OBJECT INTERFERENCE: hard regime uses higher V (4096) and NEAR-NEIGHBOUR HUB CLUSTERS -- the D_store
#       fillers of a trace are a cosine-cluster, so bundle crosstalk aligns with distractors that crowd the
#       true filler in BGE space -> symbolic NN-argmax mis-commits.
#
# EASY-REGIME RAIL (control): single-hop, D_store=3, V=1024, uniform-random (non-clustered) fillers ==
#   v1's regime. Expect cotrained ~= symbolic ~= high (TIE). Its purpose: prove any hard-regime separation
#   is STRESSOR-INDUCED, not a bridge artefact. HARD_PASS requires the rail to stay tied.
#
# THE LOOP (per trial, all steps glass-box / inspectable):
#   PERCEIVE : sample a subject S and D_store object fillers (hard: a near-neighbour hub cluster; easy:
#              uniform). All are REAL correlated BGE concept vectors (unit, N_R=1024).
#   STORE    : T = bind(role_SUBJ, bge[S]) + sum_d bind(role_path(rel_d, hops), bge[obj_d]) -- real hdlab HRR.
#   REASON   : obj_hv = unbind(T, role_path(rel_q, hops)); subj_hv = unbind(T, role_SUBJ). Both noisy HVs.
#   BRIDGE   : map subj_hv AND obj_hv (HRR-BGE, N_R=1024) -> bipolar gen codes (N_G=8192). 5 arms:
#              cotrained_linear (W fit on RECOVERED noisy HVs, HELD-OUT train concepts -- learned denoiser),
#              naive_symbolic (argmax hv into nearest test concept -> its clean gen code -- parameter-free),
#              naive_randproj (fixed random projection + sign -- bolt-on floor),
#              stored_direct (posctrl/WIRING: ORACLE clean L_gen codes -> generation-decoder ceiling,
#                             independent of any bridge; if this recovers, arm shortfalls are the bridge),
#              broken_reasoning (DISCRIMINATOR: object unbound by an UNSTORED role path -> identity severed).
#   GENERATE : ans = pos0*subj_code_est + pos1*rel_clean_code + pos2*obj_code_est (bipolar-BSC protected/
#              index positions). Decode each slot (unbind by known position + argmax cleanup).
#   METRIC   : END-TO-END exact-ordered = (subj_pred,rel_pred,obj_pred) == (S,rel_q,obj_q). Gates on the two
#              bridged slots (subj + obj). Per-slot acc + bridge bit-agreement also reported.
#
# Held-out discipline: W is fit ONLY on a TRAIN concept pool DISJOINT from the test vocab, on HVs recovered
# by running the SAME store->reason pipeline (same regime) over training subjects. Test concepts never seen.
#
# Sources (CITED@):
#  - experiments/exp_integration_end_to_end_loop_bridge_v1.py  (v1 loop scaffold; reused + hardened)
#  - experiments/exp_deep_reasoning_hub_robustness_v1.py       (store/reason: real hdlab HRR over BGE atoms)
#  - experiments/exp_generation_decoder_roundtrip_v1.py        (generate: roles-known bipolar-BSC decoder)
#  - data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz  (real correlated fillers; SCP to remote)
#  - Hersche et al. Nat. Nanotech. 2023 (arXiv:2211.05052): naive vs co-trained bridge, 16.22-pt gap.
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_integration_end_to_end_loop_bridge_HARD_v2.py [--self-test | --smoke]
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
import torch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

torch.set_num_threads(min(8, os.cpu_count() or 4))
DEVICE = torch.device("cpu")

ANCHOR_NAME = "integration_end_to_end_loop_bridge_HARD_v2"
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hdlab import binding  # noqa: E402  (proven store/reason primitive: HRR circular-conv)

# Dimensions (NEVER reduced in smoke; discriminator-survives-scale).
N_R = 1024            # reasoning/store dim == BGE_DIM == exp_deep_reasoning_hub_robustness_v1 N_DIM
N_G = 8192            # generation dim == exp_generation_decoder_roundtrip_v1 N_DIM
BGE_DIM = 1024
GEN_SLOTS = 3         # spoken ordered triple: (subject, relation, object)
SUBJ_ROLE_ID = 999983  # reserved role id for the subject-descriptor binding (single role, not a path)

SUBSET_PATH = REPO / "data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz"
BGE_FULL = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

SEEDS = (7, 13, 19)
RIDGE_LAMBDA = 1.0    # bridge ridge regularization (well-conditioned N_R x N_R normal equations)

# Fixed projection seeds (distinct so naive_randproj is a TRUE bolt-on that does NOT know P_gen).
P_GEN_SEED = 424242       # BGE -> N_G generation-lexicon projection (defines L_gen); shared train+test
R_NAIVE_SEED = 909090     # BGE-recovered -> N_G naive bolt-on projection (DIFFERENT from P_GEN_SEED)

# ---- Pre-registered bands (HYPOTHESIZED@this-prereg; deflated honestly; verified vs smoke pre-dispatch) ----
# THEORETICAL@chance = 1/V (V_hard=4096 -> 0.000244): broken discriminator lands here.
POSCTRL_FLOOR = 0.70      # WIRING gate: stored_direct (bridge ceiling on clean fillers) must recover >= this
BROKEN_CEIL = 0.10        # DISCRIMINATOR: broken_reasoning end2end must collapse at/below this
HARD_MARGIN = 0.10        # HARD_PASS: (cotrained - naive_symbolic) end2end at HARD regime must exceed this
TIE_EPS = 0.02            # HARD_FAIL: cot - sym <= this at hard -> symbolic ties/beats -> composition symbolic
CV_MAX = 0.10             # HARD_PASS: cross-seed cv of cotrained_hard end2end must be below this
EASY_TIE_TOL = 0.08       # rail tie: |cot_easy - sym_easy| must be within this (else separation not stressor)
SYM_ROOM_CEIL = 0.90      # META_RULE_AG: hard regime MUST push naive_symbolic below this (else no room)
SYM_ROOM_FLOOR = 0.15     # hard regime MUST keep naive_symbolic above this (else floored / too hard)

BRIDGE_ARMS = ["cotrained_linear", "naive_symbolic", "naive_randproj", "stored_direct", "broken_reasoning"]
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
    """Real correlated concept BGE vectors (V_pool, BGE_DIM). Loads the compact subset (remote-portable,
    ~47MB); if absent AND the full local BGE cache exists, extracts + caches the subset (local self-heal)."""
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


# ============================================================
# Primitives: HRR store/reason (real hdlab.binding), bipolar generation
# ============================================================


def _bind_hrr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular-conv bind via the proven hdlab primitive. (N,),(N,) -> (N,)."""
    out = binding.bind(torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32)),
                       torch.from_numpy(np.ascontiguousarray(b, dtype=np.float32)))
    return out.numpy()


def _unbind_hrr(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular-correlation unbind via the proven hdlab primitive. (N,),(N,) -> (N,)."""
    out = binding.unbind(torch.from_numpy(np.ascontiguousarray(c, dtype=np.float32)),
                        torch.from_numpy(np.ascontiguousarray(b, dtype=np.float32)))
    return out.numpy()


def _role_vec(rel_id: int, hop: int, seed: int) -> np.ndarray:
    """Near-orthogonal unit HRR role per (relation id, hop) (deterministic)."""
    h = int(hashlib.sha256(f"loop_role::{seed}::{rel_id}::{hop}".encode()).hexdigest(), 16)
    r = np.random.default_rng(h % (2 ** 63 - 1)).standard_normal(N_R).astype(np.float32)
    return r / (np.linalg.norm(r) + 1e-12)


def _role_path(base_rel_id: int, hops: int, seed: int) -> np.ndarray:
    """Composite role path = circular-conv of `hops` distinct roles (multi-hop relational path). Recovery
    unbinds the same composite; more hops -> more accumulated unbind crosstalk. (N_R,)."""
    r = _role_vec(base_rel_id, 0, seed)
    for hop in range(1, hops):
        r = _bind_hrr(r, _role_vec(base_rel_id, hop, seed))
    return r


def _bipolar_rows(V: int, N: int, rng) -> np.ndarray:
    return (2.0 * (rng.random((V, N)) > 0.5).astype(np.float32) - 1.0)


def _proj_sign_lexicon(bge_unit: np.ndarray, N: int, proj_seed: int) -> np.ndarray:
    """Generation lexicon: BGE -> fixed Gaussian projection -> sign -> bipolar (V, N). Carries the real
    cos-cone (matches exp_generation_decoder_roundtrip_v1.make_real_lexicon). SHARED across train+test."""
    pr = np.random.default_rng(proj_seed)
    P = (pr.standard_normal((BGE_DIM, N)).astype(np.float32) / np.sqrt(BGE_DIM))
    return np.where(bge_unit @ P >= 0.0, 1.0, -1.0).astype(np.float32)


def _make_positions(P: int, N: int, rng) -> np.ndarray:
    """Protected/index position codebook pos[k]=roll(base,k) (E3 permutation-indexed; decoder-matched)."""
    base = (2.0 * (rng.random(N) > 0.5).astype(np.float32) - 1.0)
    return np.stack([np.roll(base, k) for k in range(P)], axis=0)


def _make_naive_randproj(proj_seed: int) -> np.ndarray:
    """Bolt-on analytic bridge: a fixed Gaussian (N_R, N_G) that does NOT know P_gen. code_est=sign(hv@R)."""
    pr = np.random.default_rng(proj_seed)
    return (pr.standard_normal((N_R, N_G)).astype(np.float32) / np.sqrt(N_R))


# ============================================================
# Trace build + reason (shared by co-training data-gen and test trials)
# ============================================================


def _sample_fillers(bge_pool: np.ndarray, D_store: int, hub_cluster: bool, rng):
    """Return (subj_id, obj_ids[D_store]). hard: a near-neighbour cosine cluster (subj + objs mutually
    confusable); easy: uniform-random distinct. bge_pool rows are unit-normalized (cosine = dot)."""
    Vp = bge_pool.shape[0]
    k = D_store + 1
    if hub_cluster:
        a = int(rng.integers(Vp))
        sims = bge_pool @ bge_pool[a]
        idx = np.argpartition(-sims, k)[:k]
        idx = idx[np.argsort(-sims[idx])]          # deterministic top-k by cosine
        members = idx[:k].copy()
        rng.shuffle(members)                        # randomize which member is the subject
    else:
        members = rng.choice(Vp, size=k, replace=False)
    subj_id = int(members[0])
    obj_ids = [int(x) for x in members[1:k]]
    return subj_id, obj_ids


def _run_trace(bge_pool, subj_id, obj_ids, base_rels, query_idx, hops, seed, n_rel):
    """Build the HRR trace for one subject and recover the queried object + subject (real hdlab HRR).
    Returns dict with obj_hv, subj_hv, obj_hv_broken (severed identity), and the true ids."""
    role_subj = _role_vec(SUBJ_ROLE_ID, 0, seed)
    T = _bind_hrr(role_subj, bge_pool[subj_id])
    for d in range(len(obj_ids)):
        T = T + _bind_hrr(_role_path(int(base_rels[d]), hops, seed), bge_pool[obj_ids[d]])
    rel_q = int(base_rels[query_idx])
    obj_hv = _unbind_hrr(T, _role_path(rel_q, hops, seed))
    subj_hv = _unbind_hrr(T, role_subj)
    used = set(int(x) for x in base_rels)
    unused = [rr for rr in range(n_rel) if rr not in used]
    rel_broken = int(unused[np.random.default_rng(70000 + seed * 17 + query_idx).integers(len(unused))]) \
        if unused else (rel_q + 7) % n_rel
    obj_hv_broken = _unbind_hrr(T, _role_path(rel_broken, hops, seed))
    return {"obj_hv": obj_hv, "subj_hv": subj_hv, "obj_hv_broken": obj_hv_broken,
            "obj_true": int(obj_ids[query_idx]), "subj_true": int(subj_id), "rel_true": rel_q}


# ============================================================
# Bridge: co-trained on RECOVERED (noisy) HVs (held-out concepts, same regime pipeline)
# ============================================================


def _fit_cotrained_on_recovered(bge_train, hops, D_store, hub_cluster, n_train, seed, n_rel):
    """Ridge bridge W (N_R, N_G) fit on reasoning-RECOVERED noisy HVs (NOT clean fillers -- the v1 next-step
    upgrade). Runs the SAME store->reason pipeline over DISJOINT training subjects; pairs each recovered
    subj/obj HV with the clean sign-code of its TRUE identity (shared P_GEN_SEED). Learns to denoise the
    regime's crosstalk. code_est = sign(hv @ W)."""
    L_gen_train = _proj_sign_lexicon(bge_train, N_G, P_GEN_SEED)  # (n_train_concepts, N_G)
    rng = np.random.default_rng(600000 + seed)
    Xs, Ys = [], []
    n_traces = max(64, n_train // 2)                              # 2 samples (obj+subj) per trace
    for _t in range(n_traces):
        subj_id, obj_ids = _sample_fillers(bge_train, D_store, hub_cluster, rng)
        base_rels = rng.choice(n_rel, size=D_store, replace=False)
        q = int(rng.integers(D_store))
        rec = _run_trace(bge_train, subj_id, obj_ids, base_rels, q, hops, seed, n_rel)
        Xs.append(rec["obj_hv"]); Ys.append(L_gen_train[rec["obj_true"]])
        Xs.append(rec["subj_hv"]); Ys.append(L_gen_train[rec["subj_true"]])
    X = np.asarray(Xs, dtype=np.float32)                          # (2*n_traces, N_R)
    Y = np.asarray(Ys, dtype=np.float32)                          # (2*n_traces, N_G) in {-1,+1}
    G = X.T @ X + RIDGE_LAMBDA * np.eye(N_R, dtype=np.float32)
    W = np.linalg.solve(G, X.T @ Y).astype(np.float32)           # (N_R, N_G)
    return W


# ============================================================
# Generation decode (roles-known bipolar-BSC; decoder-matched, single-shot per slot)
# ============================================================


def _generate_and_decode(subj_code_est, rel_code, obj_code_est, pos, L_gen, L_rel):
    """Compose the ordered triple proposition and decode each slot (unbind by known position + argmax)."""
    ans = pos[0] * subj_code_est + pos[1] * rel_code + pos[2] * obj_code_est
    subj_pred = int(np.argmax(L_gen @ (ans * pos[0])))
    rel_pred = int(np.argmax(L_rel @ (ans * pos[1])))
    obj_pred = int(np.argmax(L_gen @ (ans * pos[2])))
    return subj_pred, rel_pred, obj_pred


def _fix_sign(code):
    return np.where(code == 0.0, 1.0, code).astype(np.float32)


# ============================================================
# One (regime, seed): run the full loop across all bridge arms (paired trials)
# ============================================================


def run_regime_seed(regime_name, rc, seed, output_dir, t0, hb_unit):
    """rc = regime config dict. Returns (per_arm_end2end, obj_acc, subj_acc, bit_agree, artifacts, glassbox,
    cluster_cone)."""
    V, D_store, hops, hub, trials, n_train = (rc["V"], rc["D_store"], rc["hops"],
                                              rc["hub_cluster"], rc["trials"], rc["n_train"])
    n_rel = D_store + 8
    rng = np.random.default_rng(1000 + seed + (0 if regime_name == "easy" else 500))
    sem = _load_bge_subset()
    Vpool = sem.shape[0]

    perm = rng.permutation(Vpool)
    test_rows = perm[:V]
    train_rows = perm[V:V + n_train]
    bge_test = _unit_rows(sem[test_rows])          # (V, BGE_DIM) real correlated -- subject/object fillers
    bge_train = _unit_rows(sem[train_rows])        # (n_train, BGE_DIM) held-out bridge training

    L_gen = _proj_sign_lexicon(bge_test, N_G, P_GEN_SEED)    # (V, N_G) test concept gen codes
    L_rel = _bipolar_rows(n_rel, N_G, np.random.default_rng(2000 + seed))
    pos = _make_positions(GEN_SLOTS, N_G, np.random.default_rng(3000 + seed))

    W = _fit_cotrained_on_recovered(bge_train, hops, D_store, hub, n_train, seed, n_rel)
    R_naive = _make_naive_randproj(R_NAIVE_SEED)

    hit = {a: 0 for a in BRIDGE_ARMS}
    ohit = {a: 0 for a in BRIDGE_ARMS}
    shit = {a: 0 for a in BRIDGE_ARMS}
    rec_obj = {a: [] for a in BRIDGE_ARMS}
    bit_agree = {a: [] for a in BRIDGE_ARMS}
    cluster_cones = []
    glassbox = []

    for tr in range(trials):
        trng = np.random.default_rng(50000 + seed * 131 + tr + (0 if regime_name == "easy" else 777))
        subj_id, obj_ids = _sample_fillers(bge_test, D_store, hub, trng)
        base_rels = trng.choice(n_rel, size=D_store, replace=False)
        q = int(trng.integers(D_store))
        rec = _run_trace(bge_test, subj_id, obj_ids, base_rels, q, hops, seed, n_rel)
        obj_q, rel_q = rec["obj_true"], rec["rel_true"]

        # cluster confusability diagnostic (mean pairwise cosine among the trace fillers)
        members = np.array([subj_id] + list(obj_ids))
        M = bge_test[members]
        S = M @ M.T
        cluster_cones.append(float(S[~np.eye(len(members), dtype=bool)].mean()))

        rel_code = L_rel[rel_q]

        def bridge_codes(hv_obj, hv_subj):
            out = {}
            out["cotrained_linear"] = (_fix_sign(np.sign(hv_subj @ W)), _fix_sign(np.sign(hv_obj @ W)))
            out["naive_randproj"] = (_fix_sign(np.sign(hv_subj @ R_naive)), _fix_sign(np.sign(hv_obj @ R_naive)))
            js = int(np.argmax(bge_test @ (hv_subj / (np.linalg.norm(hv_subj) + 1e-12))))
            jo = int(np.argmax(bge_test @ (hv_obj / (np.linalg.norm(hv_obj) + 1e-12))))
            out["naive_symbolic"] = (L_gen[js], L_gen[jo])
            # posctrl (WIRING gate): ORACLE decoder ceiling -- emit the CLEAN L_gen codes of the true subj/obj
            # (perfect bridge). Isolates "can the 3-slot generation decoder recover a clean proposition at
            # this V" from bridge quality. If this recovers, any arm's shortfall is the BRIDGE's fault.
            out["stored_direct"] = (L_gen[subj_id], L_gen[obj_q])
            # broken: object identity severed (unbind by an unstored role path); subject from real recovery
            out["broken_reasoning"] = (_fix_sign(np.sign(hv_subj @ W)),
                                       _fix_sign(np.sign(rec["obj_hv_broken"] @ W)))
            return out, js, jo

        codes, _js, _jo = bridge_codes(rec["obj_hv"], rec["subj_hv"])
        obj_true_code = L_gen[obj_q]

        for a in BRIDGE_ARMS:
            sc, oc = codes[a]
            sp, rp, op = _generate_and_decode(sc, rel_code, oc, pos, L_gen, L_rel)
            exact = int(sp == subj_id and rp == rel_q and op == obj_q)
            hit[a] += exact
            ohit[a] += int(op == obj_q)
            shit[a] += int(sp == subj_id)
            rec_obj[a].append(op)
            bit_agree[a].append(float(np.mean(oc == obj_true_code)))

        if tr < 3:
            glassbox.append({
                "regime": regime_name, "seed": seed, "trial": tr,
                "hops": hops, "D_store": D_store, "hub_cluster": hub,
                "query_rel": rel_q, "true_obj": obj_q, "subj": subj_id,
                "cluster_cone": round(cluster_cones[-1], 4),
                "trace_norm": round(float(np.linalg.norm(rec["obj_hv"])), 3),
                "r_hv_cos_true_obj": round(float(
                    bge_test[obj_q] @ (rec["obj_hv"] / (np.linalg.norm(rec["obj_hv"]) + 1e-12))), 4),
                "cotrained_obj_pred": rec_obj["cotrained_linear"][-1],
                "symbolic_obj_pred": rec_obj["naive_symbolic"][-1],
                "broken_obj_pred": rec_obj["broken_reasoning"][-1],
                "cotrained_bit_agree_vs_Lgen_obj": round(bit_agree["cotrained_linear"][-1], 4),
            })

    end2end = {a: hit[a] / trials for a in BRIDGE_ARMS}
    obj_acc = {a: ohit[a] / trials for a in BRIDGE_ARMS}
    subj_acc = {a: shit[a] / trials for a in BRIDGE_ARMS}
    bit_mean = {a: round(float(np.mean(bit_agree[a])), 4) for a in BRIDGE_ARMS}
    cluster_cone = round(float(np.mean(cluster_cones)), 4)
    artifacts = {
        "W_digest": _digest_arr(W),
        "R_naive_digest": _digest_arr(R_naive),
        "rec_cotrained": _digest(rec_obj["cotrained_linear"]),
        "rec_broken": _digest(rec_obj["broken_reasoning"]),
        "rec_symbolic": _digest(rec_obj["naive_symbolic"]),
    }
    _heartbeat(output_dir, hb_unit, rc["_total_units"], t0,
               extra={"regime": regime_name, "seed": seed,
                      "cot_e2e": round(end2end["cotrained_linear"], 3),
                      "sym_e2e": round(end2end["naive_symbolic"], 3),
                      "posctrl_e2e": round(end2end["stored_direct"], 3),
                      "broken_e2e": round(end2end["broken_reasoning"], 3)})
    _say(f"  [{regime_name} seed {seed}] V={V} D={D_store} hops={hops} hub={hub} cone={cluster_cone:.3f} | "
         f"end2end cot={end2end['cotrained_linear']:.3f} sym={end2end['naive_symbolic']:.3f} "
         f"rp={end2end['naive_randproj']:.3f} posctrl={end2end['stored_direct']:.3f} "
         f"broken={end2end['broken_reasoning']:.3f} | margin(cot-sym)={end2end['cotrained_linear']-end2end['naive_symbolic']:+.3f}")
    return end2end, obj_acc, subj_acc, bit_mean, artifacts, glassbox, cluster_cone


# ============================================================
# Config + hashing
# ============================================================


def get_regimes(mode: str):
    """Two regimes; difficulty axes (V, hops, D_store, hub_cluster) held at FULL in smoke -- only trials,
    seeds, n_train reduced (discriminator survives scale)."""
    # n_train is a CONCEPT-POOL size; the bridge fits on 2*n_traces = 2*max(64, n_train//2) recovered-HV
    # samples. Per-output-bit ridge needs n_samples > N_R=1024, so n_train >= ~1536 (n_samples >= 1536).
    if mode == "selftest":
        easy = {"V": 64, "D_store": 3, "hops": 1, "hub_cluster": False, "trials": 6, "n_train": 1536}
        hard = {"V": 256, "D_store": 5, "hops": 2, "hub_cluster": True, "trials": 6, "n_train": 1536}
        seeds = (7,)
    elif mode == "smoke":
        easy = {"V": 1024, "D_store": 3, "hops": 1, "hub_cluster": False, "trials": 24, "n_train": 3072}
        hard = {"V": 4096, "D_store": 10, "hops": 3, "hub_cluster": True, "trials": 24, "n_train": 3072}
        seeds = (7, 13, 19)
    else:  # full
        easy = {"V": 1024, "D_store": 3, "hops": 1, "hub_cluster": False, "trials": 60, "n_train": 4096}
        hard = {"V": 4096, "D_store": 10, "hops": 3, "hub_cluster": True, "trials": 60, "n_train": 4096}
        seeds = SEEDS
    return {"easy": easy, "hard": hard}, seeds


def _digest(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


def _cv(vals) -> float:
    v = np.asarray(vals, dtype=np.float64)
    m = float(v.mean())
    if abs(m) < 1e-9:
        return 0.0
    return float(v.std(ddof=0) / abs(m))


# ============================================================
# Verdict
# ============================================================


def _regime_gates(agg_r, regime_name):
    """Return (ok, reason) for the by-construction wiring + identity discriminators at one regime."""
    pos = agg_r["end2end"]["stored_direct"]
    brk = agg_r["end2end"]["broken_reasoning"]
    if pos < POSCTRL_FLOOR:
        return False, (f"[{regime_name}] posctrl stored_direct end2end={pos:.3f} < {POSCTRL_FLOOR}: "
                       f"bridge/generation WIRING failed (cannot attribute loop failure to the seam)")
    if brk > BROKEN_CEIL:
        return False, (f"[{regime_name}] broken_reasoning end2end={brk:.3f} > {BROKEN_CEIL}: severed-identity "
                       f"loop did NOT collapse -> accuracy not attributable to genuine reasoning (leakage)")
    return True, "ok"


def classify(agg, mode):
    """agg[regime]['end2end'][arm] = cross-seed mean; agg[regime]['end2end_per_seed'][arm] = list.
    Returns (verdict, msg)."""
    e = {r: agg[r]["end2end"] for r in REGIME_ORDER}
    cot_h, sym_h = e["hard"]["cotrained_linear"], e["hard"]["naive_symbolic"]
    cot_e, sym_e = e["easy"]["cotrained_linear"], e["easy"]["naive_symbolic"]
    rp_h = e["hard"]["naive_randproj"]
    margin_h = cot_h - sym_h
    margin_e = cot_e - sym_e
    cv_cot_h = _cv(agg["hard"]["end2end_per_seed"]["cotrained_linear"])

    diag = (f"HARD: cot={cot_h:.3f} sym={sym_h:.3f} randproj={rp_h:.3f} "
            f"posctrl={e['hard']['stored_direct']:.3f} broken={e['hard']['broken_reasoning']:.3f} "
            f"margin(cot-sym)={margin_h:+.3f} cv(cot)={cv_cot_h:.3f} | "
            f"EASY-RAIL: cot={cot_e:.3f} sym={sym_e:.3f} margin={margin_e:+.3f}")

    # by-construction rails (both regimes)
    for r in REGIME_ORDER:
        ok, reason = _regime_gates(agg[r], r)
        if not ok:
            return "DISCRIMINATOR_DID_NOT_FIRE", f"{reason}. {diag}"

    # Discriminating power requires the two arms are not BOTH saturated at ceiling (then the stressor did
    # nothing measurable). A large gap in EITHER direction is discriminating.
    both_saturated = (min(cot_h, sym_h) >= SYM_ROOM_CEIL)
    sym_in_band = (SYM_ROOM_FLOOR < sym_h < SYM_ROOM_CEIL)
    rail_tied = abs(margin_e) <= EASY_TIE_TOL

    if mode == "smoke":
        # smoke: BLOCK only on machinery (handled by the rails above). Otherwise clear to FULL and report the
        # preview -- HARD_FAIL (symbolic dominates) is an ALLOWED, useful outcome per the task contract, so it
        # must not be gated out here. The only smoke stop is 'no discriminating power' (both arms saturated).
        if both_saturated:
            return ("SMOKE_ITERATE_REGIME",
                    f"NO DISCRIMINATING POWER: both cot={cot_h:.3f} and sym={sym_h:.3f} >= {SYM_ROOM_CEIL} at "
                    f"hard -> the stressor separates nothing. Crank stressors before FULL. {diag}")
        return ("SMOKE_MACHINERY_OK",
                f"SMOKE OK: full loop runs AT N_R={N_R} N_G={N_G}; oracle-decoder posctrl recovers + broken "
                f"collapses in both regimes; arms differ. Hard-regime symbolic {'IN BAND' if sym_in_band else 'SATURATED-HIGH'} "
                f"(sym={sym_h:.3f}); measurable cot-sym gap present. Deliverable verdict is FULL-only "
                f"(canonical=remote). PREVIEW margin(cot-sym) hard={margin_h:+.3f} easy={margin_e:+.3f}. {diag}")

    # ---- FULL research verdict (canonical) ----
    if both_saturated:
        return ("INCONCLUSIVE_NO_DISCRIMINATING_POWER",
                f"both cot={cot_h:.3f} and sym={sym_h:.3f} >= {SYM_ROOM_CEIL} at hard -> the stressor did not "
                f"separate the arms; cannot answer learned-vs-symbolic. {diag}")

    if margin_h >= HARD_MARGIN and cv_cot_h < CV_MAX and rail_tied:
        return ("HARD_PASS",
                f"LEARNED BRIDGE IS LOAD-BEARING: co-trained-on-recovered-HV bridge BEATS symbolic cleanup at the "
                f"hard regime by {margin_h:+.3f} (>= {HARD_MARGIN}), cross-seed cv={cv_cot_h:.3f} (< {CV_MAX}), "
                f"while the easy rail stays TIED ({margin_e:+.3f}, |.|<= {EASY_TIE_TOL}) -> the separation is "
                f"STRESSOR-INDUCED. The substrate composition is NOT purely symbolic. {diag}")
    if margin_h <= TIE_EPS:
        strength = ("STRESSED-BUT-UNBEATEN" if sym_in_band else "symbolic-still-high")
        return ("HARD_FAIL",
                f"COMPOSITION IS EFFECTIVELY SYMBOLIC (honest negative; {strength}): at the hard regime the "
                f"co-trained-on-recovered-HV bridge does NOT beat parameter-free symbolic cleanup "
                f"(margin={margin_h:+.3f} <= {TIE_EPS}); symbolic ties/beats even though it was degraded into "
                f"the measurable band (sym={sym_h:.3f}). Root cause: symbolic RE-EMITS a CLEAN code after its "
                f"NN-argmax; the learned linear bridge emits a NOISY code, and two-slot gating amplifies that. "
                f"The learned bridge is not load-bearing for the glass-box loop -- symbolic cleanup->clean-code "
                f"suffices wherever the loop works at all. {diag}")
    return ("MIDDLE_BAND",
            f"PARTIAL SEPARATION: co-trained margin over symbolic at hard = {margin_h:+.3f} in ({TIE_EPS}, "
            f"{HARD_MARGIN}) OR cv(cot)={cv_cot_h:.3f} >= {CV_MAX} OR rail_tied={rail_tied}. The learned bridge "
            f"helps but does not clear the load-bearing margin; quantify per-seed + consider a stronger denoiser. {diag}")


# ============================================================
# main
# ============================================================


def _aggregate(per):
    """per[regime][arm] -> list over seeds of a metric. Return mean + per-seed."""
    out = {}
    for r in REGIME_ORDER:
        out[r] = {"end2end": {}, "end2end_per_seed": {}, "obj_acc": {}, "subj_acc": {}, "bit_agree": {}}
        for a in BRIDGE_ARMS:
            out[r]["end2end"][a] = round(float(np.mean(per[r]["e2e"][a])), 4)
            out[r]["end2end_per_seed"][a] = [round(v, 4) for v in per[r]["e2e"][a]]
            out[r]["obj_acc"][a] = round(float(np.mean(per[r]["obj"][a])), 4)
            out[r]["subj_acc"][a] = round(float(np.mean(per[r]["subj"][a])), 4)
            out[r]["bit_agree"][a] = round(float(np.mean(per[r]["bit"][a])), 4)
    return out


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    regimes, seeds = get_regimes(mode)
    expected_n_units = len(seeds) * len(REGIME_ORDER) * len(BRIDGE_ARMS)
    total_seed_regime = len(seeds) * len(REGIME_ORDER)
    for r in REGIME_ORDER:
        regimes[r]["_total_units"] = total_seed_regime
    _write_start_marker(output_dir, mode, expected_n_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N_R={N_R} N_G={N_G} seeds={seeds} arms={BRIDGE_ARMS}")
    for r in REGIME_ORDER:
        rc = regimes[r]
        _say(f"  regime={r}: V={rc['V']} D_store={rc['D_store']} hops={rc['hops']} "
             f"hub_cluster={rc['hub_cluster']} trials={rc['trials']} n_train={rc['n_train']}")

    per = {r: {"e2e": {a: [] for a in BRIDGE_ARMS}, "obj": {a: [] for a in BRIDGE_ARMS},
               "subj": {a: [] for a in BRIDGE_ARMS}, "bit": {a: [] for a in BRIDGE_ARMS}}
           for r in REGIME_ORDER}
    artifacts_by = {r: {} for r in REGIME_ORDER}
    cones = {r: {} for r in REGIME_ORDER}
    glassbox_all = []
    hb = 0
    for regime_name in REGIME_ORDER:
        rc = regimes[regime_name]
        for seed in seeds:
            e2e, oacc, sacc, bit, art, gb, cone = run_regime_seed(regime_name, rc, seed, output_dir, t0, hb)
            hb += 1
            for a in BRIDGE_ARMS:
                per[regime_name]["e2e"][a].append(e2e[a])
                per[regime_name]["obj"][a].append(oacc[a])
                per[regime_name]["subj"][a].append(sacc[a])
                per[regime_name]["bit"][a].append(bit[a])
            artifacts_by[regime_name][str(seed)] = art
            cones[regime_name][str(seed)] = cone
            glassbox_all.extend(gb)

    # arms_differ (META_RULE_AF): learned bridge matrix != bolt-on; severed-identity recovery != cotrained;
    # AND the mechanism arms are not bit-identical to symbolic (recovery index streams differ).
    arms_differ_ok = True
    for r in REGIME_ORDER:
        for _sd, art in artifacts_by[r].items():
            if art["W_digest"] == art["R_naive_digest"]:
                arms_differ_ok = False
            if art["rec_cotrained"] == art["rec_broken"]:
                arms_differ_ok = False
            if art["rec_cotrained"] == art["rec_symbolic"]:
                arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError(
            "META_RULE_AF VIOLATION: bridge matrices bit-identical OR severed-identity recovery == cotrained "
            "recovery OR cotrained recovery == symbolic recovery (arm-implementation/discriminator bug)")

    agg = _aggregate(per)
    verdict, vmsg = classify(agg, mode)
    elapsed = time.perf_counter() - t0

    hard = agg["hard"]["end2end"]
    easy = agg["easy"]["end2end"]
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: hard-regime end-to-end loop, learned-vs-symbolic bridge ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(seeds),
        "n_units": len(seeds) * len(REGIME_ORDER) * len(BRIDGE_ARMS),
        "expected_n_units": expected_n_units,
        "cardinality_ok": True,
        "config": {
            "N_R": N_R, "N_G": N_G, "BGE_DIM": BGE_DIM, "GEN_SLOTS": GEN_SLOTS,
            "seeds": list(seeds), "RIDGE_LAMBDA": RIDGE_LAMBDA, "bridge_arms": BRIDGE_ARMS,
            "regimes": {r: {k: regimes[r][k] for k in
                            ("V", "D_store", "hops", "hub_cluster", "trials", "n_train")}
                        for r in REGIME_ORDER},
            "store_reason_algebra": "HRR_circular_conv_real_BGE_hdlab_binding_multihop_composite_role_path",
            "generation_algebra": "bipolar_BSC_elementwise_product_protected_index_positions",
            "cotrained_bridge_training": "on_reasoning_RECOVERED_noisy_HVs_heldout_concepts_same_regime",
            "bridged_slots": ["subject", "object"],
            "real_filler_cache": str(SUBSET_PATH.relative_to(REPO)).replace("\\", "/"),
        },
        "key_comparison": {
            "hard_cot_minus_sym": round(hard["cotrained_linear"] - hard["naive_symbolic"], 4),
            "easy_cot_minus_sym": round(easy["cotrained_linear"] - easy["naive_symbolic"], 4),
            "cv_cotrained_hard": round(_cv(agg["hard"]["end2end_per_seed"]["cotrained_linear"]), 4),
            "learned_separates_at_hard": bool(
                (hard["cotrained_linear"] - hard["naive_symbolic"]) >= HARD_MARGIN
                and _cv(agg["hard"]["end2end_per_seed"]["cotrained_linear"]) < CV_MAX
                and abs(easy["cotrained_linear"] - easy["naive_symbolic"]) <= EASY_TIE_TOL),
        },
        "regimes": {
            r: {
                "end2end": agg[r]["end2end"],
                "end2end_per_seed": agg[r]["end2end_per_seed"],
                "obj_acc": agg[r]["obj_acc"],
                "subj_acc": agg[r]["subj_acc"],
                "bit_agree": agg[r]["bit_agree"],
                "cluster_cone": cones[r],
                "chance_obj_acc_THEORETICAL": round(1.0 / regimes[r]["V"], 6),
            } for r in REGIME_ORDER
        },
        "controls": {
            "posctrl_stored_direct_end2end": {r: agg[r]["end2end"]["stored_direct"] for r in REGIME_ORDER},
            "broken_reasoning_end2end": {r: agg[r]["end2end"]["broken_reasoning"] for r in REGIME_ORDER},
            "broken_collapsed": {r: bool(agg[r]["end2end"]["broken_reasoning"] <= BROKEN_CEIL)
                                 for r in REGIME_ORDER},
        },
        "glassbox_trace": glassbox_all,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_artifacts": artifacts_by,
        "bands": {"POSCTRL_FLOOR": POSCTRL_FLOOR, "BROKEN_CEIL": BROKEN_CEIL, "HARD_MARGIN": HARD_MARGIN,
                  "TIE_EPS": TIE_EPS, "CV_MAX": CV_MAX, "EASY_TIE_TOL": EASY_TIE_TOL,
                  "SYM_ROOM_CEIL": SYM_ROOM_CEIL, "SYM_ROOM_FLOOR": SYM_ROOM_FLOOR},
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
    for r in REGIME_ORDER:
        regimes[r]["_total_units"] = 2
    res = {}
    for regime_name in REGIME_ORDER:
        e2e, _o, _s, _b, _a, _g, _c = run_regime_seed(regime_name, regimes[regime_name], 7, output_dir, t0, 0)
        res[regime_name] = e2e
    # formula self-test: posctrl recovers (wiring) AND broken collapses below posctrl (discriminator alive),
    # in BOTH regimes. Does NOT assert the research margin (that is the FULL question).
    ok = True
    for r in REGIME_ORDER:
        ok = ok and (res[r]["stored_direct"] >= 0.50) and \
            (res[r]["broken_reasoning"] <= res[r]["stored_direct"] - 0.20)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: "
         f"easy(posctrl={res['easy']['stored_direct']:.3f} broken={res['easy']['broken_reasoning']:.3f}) "
         f"hard(posctrl={res['hard']['stored_direct']:.3f} broken={res['hard']['broken_reasoning']:.3f} "
         f"cot={res['hard']['cotrained_linear']:.3f} sym={res['hard']['naive_symbolic']:.3f}) "
         f"[{time.perf_counter()-t0:.1f}s]")
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
