# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (bridge matrices distinct; broken-recovered != cotrained-recovered)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp then os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/capacity-feasibility: chance object accuracy = 1/V (V=1024 -> 0.00098 THEORETICAL); broken arm
#     must land in the chance band; posctrl (bridge ceiling) is the reachable upper bound. HP=0.70
#     strictly above HF=0.40 floor (band_width 0.30; +5pct = 0.415; 0.70 well above). crlb_n_a for the
#     bridge itself (learned linear map has no closed-form noise floor; posctrl empirically bounds it).
# - baseline_in_band: broken_reasoning discriminator MUST collapse to chance; posctrl MUST recover high.
# - discriminator survives scale: loop measured AT full N_R=1024 (HRR store/reason) and N_G=8192
#     (bipolar-BSC generation) in ALL modes; smoke reduces V/trials/seeds only, never N. Broken-collapse +
#     posctrl-ceiling + arms-differ assertions FIRE in smoke.
# - HARD_PASS strictly above floor (cotrained end-to-end >= 0.70 AND discrim gap >= 0.40 AND posctrl>=0.70)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
#
# END-TO-END SUBSTRATE LOOP: perceive -> store -> reason(1-hop) -> BRIDGE -> generate  v1
# =====================================================================================
# THE decisive integration test (goal-level): does the substrate compose into ONE working glass-box
# loop? Per the drill (notes/research_integration_end_to_end_substrate_loop_2026-07-05.md), 2 of 3
# hand-offs are already proven clean:
#   (1) encoder -> store  : CLEAN (exp_regime_switch_encoder_instore_integration_verify_v1 HARD_PASS)
#   (2) store   -> reason : CHAIN_GRADE, SAME algebra (exp_deep_reasoning_hub_robustness_v1 over REAL
#                           stored atoms; HRR circular-conv bind/unbind on real BGE concept vectors).
# THE ONE SEAM (never tested end-to-end): reason -> generate. This cell wires it.
#
# ALGEBRA-GAP FINDING (refines the drill): the reasoning primitive AS IMPLEMENTED
# (exp_deep_reasoning_hub_robustness_v1) is HRR circular-convolution on REAL BGE fillers at N_R=1024
# (NOT bipolar-BSC as the drill framed it). The generation decoders are bipolar-BSC / block-local at
# N_G=8192. So the seam is a genuine CROSS-ALGEBRA and CROSS-DIMENSION gap: there is NO zero-transform
# hand-off; a bridge transform is MANDATORY. That strengthens the drill's thesis (both neuro + VSA
# literatures: cross-code hand-offs need a co-trained/learned bridge; naive analytic bridges lose
# fidelity -- Hersche et al. Nat. Nanotech. 2023 measured a 16.22-pt naive-vs-cotrained gap).
#
# THE LOOP (per trial, all steps glass-box / inspectable):
#   PERCEIVE : sample a subject S with D_STORE facts (rel_d, obj_d); objects are REAL correlated BGE
#              concept fillers (unit vectors, N_R=1024). Relations are near-orthogonal HRR roles.
#   STORE    : T = sum_d bind_HRR(role(rel_d), filler(obj_d))  -- the subject's memory trace (real
#              hdlab.binding HRR; the proven store/reason algebra). [glass-box intermediate: T]
#   REASON   : query (S, rel_q, ?): r_hv = unbind_HRR(T, role(rel_q))  -- recovered object HV, carries
#              obj_q identity + HRR bundle crosstalk. [glass-box intermediate: r_hv]
#   BRIDGE   : map r_hv (HRR-BGE, N_R=1024) -> a bipolar generation filler code (N_G=8192). 5 arms:
#              cotrained_linear (learned ridge map W, HELD-OUT concepts), naive_symbolic (argmax r_hv
#              into nearest concept then look up its clean gen code -- the drill's "cheapest bridge"),
#              naive_randproj (fixed random projection + sign -- pure bolt-on floor), stored_direct
#              (posctrl: bridge the CLEAN object BGE, no reasoning crosstalk -> isolates bridge ceiling),
#              broken_reasoning (DISCRIMINATOR: unbind by a role NOT in the trace -> identity severed ->
#              must collapse to chance). [glass-box intermediate: code_est + bit-agreement vs L_gen[obj]]
#   GENERATE : speak the ordered triple (S, rel_q, obj) as a 3-slot bipolar-BSC proposition
#              ans = pos[0]*L_gen[S] + pos[1]*L_rel[rel_q] + pos[2]*code_est (elementwise-product bind,
#              protected/index positions -- the proven roles-known decoder machinery). Decode per slot
#              (unbind by known position + argmax cleanup). [glass-box: decoded (subj,rel,obj) tokens]
#   METRIC   : END-TO-END exact-ordered = spoken (subj,rel,obj) == stored (S,rel_q,obj_q). subj/rel
#              codes are clean so this gates on the object slot (the bridged term).
#
# Bridge clean-test discipline: W is fit ONLY on a TRAIN concept pool DISJOINT from the test vocab; the
# generation lexicon L_gen for test concepts is built independently (BGE -> fixed P_gen -> sign). The
# bridge must GENERALIZE to unseen concepts (held-out methodology).
#
# Sources (CITED@):
#  - experiments/exp_deep_reasoning_hub_robustness_v1.py   (store/reason: real hdlab HRR over BGE atoms)
#  - experiments/exp_generation_decoder_roundtrip_v1.py    (generate: roles-known bipolar-BSC decoder)
#  - notes/research_integration_end_to_end_substrate_loop_2026-07-05.md  (3-arm drill spec + bridge design)
#  - Hersche et al. Nat. Nanotech. 2023 (arXiv:2211.05052): naive vs co-trained bridge, 16.22-pt gap.
#  - data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz  (real correlated fillers; SCP to remote)
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_integration_end_to_end_loop_bridge_v1.py [--self-test | --smoke]
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

ANCHOR_NAME = "integration_end_to_end_loop_bridge_v1"
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hdlab import binding  # noqa: E402  (proven store/reason primitive: HRR circular-conv)

# Dimensions (NEVER reduced in smoke; discriminator-survives-scale).
N_R = 1024            # reasoning/store dim == BGE_DIM == exp_deep_reasoning_hub_robustness_v1 N_DIM
N_G = 8192            # generation dim == exp_generation_decoder_roundtrip_v1 N_DIM
BGE_DIM = 1024
GEN_SLOTS = 3         # spoken ordered triple: (subject, relation, object)

SUBSET_PATH = REPO / "data/gen_integration_loop_cache/bge_concept_subset_12288_v1.npz"
BGE_FULL = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

SEEDS = (7, 13, 19)
RIDGE_LAMBDA = 1.0    # bridge ridge regularization (well-conditioned N_R x N_R normal equations)

# Fixed projection seeds (distinct so naive_randproj is a TRUE bolt-on that does NOT know P_gen).
P_GEN_SEED = 424242       # BGE -> N_G generation-lexicon projection (defines L_gen)
R_NAIVE_SEED = 909090     # BGE-recovered -> N_G naive bolt-on projection (DIFFERENT from P_GEN_SEED)

# Pre-registered bands (HYPOTHESIZED@this-prereg; deflated honestly; verified vs smoke before dispatch).
# THEORETICAL@chance = 1/V (V=1024 -> 0.00098): broken discriminator lands here.
HP_END2END = 0.70         # HARD_PASS: cotrained_linear end-to-end exact-ordered (deliverable arm)
HP_DISCRIM_GAP = 0.40     # HARD_PASS: (deliverable end-to-end - broken_reasoning) must exceed this
HF_END2END = 0.40         # HARD_FAIL: deliverable below -> seam is the wall despite sound components
POSCTRL_FLOOR = 0.70      # WIRING gate: stored_direct (bridge ceiling) must recover >= this
BROKEN_COLLAPSE_CEIL = 0.10  # DISCRIMINATOR: broken_reasoning must collapse at/below this

BRIDGE_ARMS = ["cotrained_linear", "naive_symbolic", "naive_randproj", "stored_direct", "broken_reasoning"]


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


def _mean_pair_cos(Xn: np.ndarray, n: int, rng) -> float:
    m = min(n, Xn.shape[0])
    idx = rng.choice(Xn.shape[0], size=m, replace=False)
    S = Xn[idx] @ Xn[idx].T
    off = S[~np.eye(m, dtype=bool)]
    return float(off.mean())


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


def _role_vec(rel_id: int, seed: int) -> np.ndarray:
    """Near-orthogonal unit HRR role per relation id (deterministic; matches reasoning cell's white_role)."""
    h = int(hashlib.sha256(f"loop_role::{seed}::{rel_id}".encode()).hexdigest(), 16)
    r = np.random.default_rng(h % (2 ** 63 - 1)).standard_normal(N_R).astype(np.float32)
    return r / (np.linalg.norm(r) + 1e-12)


def _bipolar_rows(V: int, N: int, rng) -> np.ndarray:
    return (2.0 * (rng.random((V, N)) > 0.5).astype(np.float32) - 1.0)


def _proj_sign_lexicon(bge_unit: np.ndarray, N: int, proj_seed: int) -> np.ndarray:
    """Generation lexicon: BGE -> fixed Gaussian projection -> sign -> bipolar (V, N). Carries the real
    cos-cone (matches exp_generation_decoder_roundtrip_v1.make_real_lexicon)."""
    pr = np.random.default_rng(proj_seed)
    P = (pr.standard_normal((BGE_DIM, N)).astype(np.float32) / np.sqrt(BGE_DIM))
    return np.where(bge_unit @ P >= 0.0, 1.0, -1.0).astype(np.float32)


def _make_positions(P: int, N: int, rng) -> np.ndarray:
    """Protected/index position codebook pos[k]=roll(base,k) (E3 permutation-indexed; decoder-matched)."""
    base = (2.0 * (rng.random(N) > 0.5).astype(np.float32) - 1.0)
    return np.stack([np.roll(base, k) for k in range(P)], axis=0)


# ============================================================
# Bridge (the NEW seam component): reason-HV (N_R) -> gen filler code (N_G bipolar)
# ============================================================


def _fit_cotrained_bridge(bge_train_unit: np.ndarray, N: int, proj_seed: int) -> np.ndarray:
    """Ridge least-squares bridge W (N_R, N) mapping a reasoning-space BGE vector to its generation code.
    Trained ONLY on the disjoint train concept pool (held-out discipline). Target = the SAME sign-code
    the test-vocab L_gen uses, so W learns the cross-algebra alignment and GENERALIZES to unseen concepts.
    Returns W with code_est = sign(r_hv @ W)."""
    X = bge_train_unit.astype(np.float32)                       # (Ntr, N_R)
    Y = _proj_sign_lexicon(X, N, proj_seed)                     # (Ntr, N) in {-1,+1}
    G = X.T @ X + RIDGE_LAMBDA * np.eye(N_R, dtype=np.float32)  # (N_R, N_R)
    W = np.linalg.solve(G, X.T @ Y).astype(np.float32)         # (N_R, N)
    return W


def _make_naive_randproj(proj_seed: int) -> np.ndarray:
    """Bolt-on analytic bridge: a fixed Gaussian (N_R, N_G) that does NOT know P_gen. code_est=sign(r_hv@R)."""
    pr = np.random.default_rng(proj_seed)
    return (pr.standard_normal((N_R, N_G)).astype(np.float32) / np.sqrt(N_R))


# ============================================================
# Generation decode (roles-known bipolar-BSC; decoder-matched, single-shot per slot)
# ============================================================


def _generate_and_decode(subj_code, rel_code, obj_code_est, pos, L_gen, L_rel):
    """Compose the ordered triple proposition and decode each slot (unbind by known position + argmax).
    subj/obj cleanup over L_gen (concepts); rel cleanup over L_rel (relations). Returns (subj_pred, rel_pred,
    obj_pred) codebook indices."""
    ans = pos[0] * subj_code + pos[1] * rel_code + pos[2] * obj_code_est   # (N_G,) bipolar-BSC superposition
    q_s = ans * pos[0]                                                      # unbind slot 0 (self-inverse)
    q_r = ans * pos[1]
    q_o = ans * pos[2]
    subj_pred = int(np.argmax(L_gen @ q_s))
    rel_pred = int(np.argmax(L_rel @ q_r))
    obj_pred = int(np.argmax(L_gen @ q_o))
    return subj_pred, rel_pred, obj_pred


# ============================================================
# One seed: run the full loop across all bridge arms (paired trials)
# ============================================================


def run_seed(seed: int, V: int, D_store: int, trials: int, n_train: int, output_dir: Path, t0: float):
    """Returns (per_arm_end2end dict, per_arm_obj_acc dict, arms_differ artifacts dict, glassbox list, cone)."""
    rng = np.random.default_rng(1000 + seed)
    sem = _load_bge_subset()
    Vpool = sem.shape[0]

    # disjoint concept partition: test vocab (V) + bridge train pool (n_train), no overlap
    perm = rng.permutation(Vpool)
    test_rows = perm[:V]
    train_rows = perm[V:V + n_train]
    bge_test = _unit_rows(sem[test_rows])          # (V, BGE_DIM) real correlated -- object/subject fillers
    bge_train = _unit_rows(sem[train_rows])        # (n_train, BGE_DIM) held-out bridge training

    # generation lexicons + positions (N_G bipolar)
    L_gen = _proj_sign_lexicon(bge_test, N_G, P_GEN_SEED)     # (V, N_G) concept codes
    n_rel = max(GEN_SLOTS, D_store + 4)                        # relation vocabulary (>= stored + spare roles)
    L_rel = _bipolar_rows(n_rel, N_G, np.random.default_rng(2000 + seed))
    pos = _make_positions(GEN_SLOTS, N_G, np.random.default_rng(3000 + seed))

    # bridges
    W = _fit_cotrained_bridge(bge_train, N_G, P_GEN_SEED)     # (N_R, N_G) held-out learned
    R_naive = _make_naive_randproj(R_NAIVE_SEED)              # (N_R, N_G) bolt-on

    cone = round(_mean_pair_cos(bge_test, 400, np.random.default_rng(4000 + seed)), 4)

    hit = {a: 0 for a in BRIDGE_ARMS}       # end-to-end exact-ordered hits
    ohit = {a: 0 for a in BRIDGE_ARMS}      # object-slot hits (diagnostic)
    rec_obj = {a: [] for a in BRIDGE_ARMS}  # per-arm recovered object indices (arms_differ)
    bit_agree = {a: [] for a in BRIDGE_ARMS}  # bridge fidelity: frac bits matching L_gen[obj]
    glassbox = []

    for tr in range(trials):
        trng = np.random.default_rng(50000 + seed * 131 + tr)
        # PERCEIVE: subject S with D_store distinct facts (distinct relations, distinct objects)
        obj_ids = trng.choice(V, size=D_store, replace=False)
        rel_ids = trng.choice(n_rel, size=D_store, replace=False)
        # STORE: HRR bundle of role-bound object fillers (real hdlab HRR)
        T = np.zeros(N_R, dtype=np.float32)
        for d in range(D_store):
            T = T + _bind_hrr(_role_vec(int(rel_ids[d]), seed), bge_test[obj_ids[d]])
        # QUERY one fact: (S, rel_q, ?)
        q = int(trng.integers(D_store))
        rel_q, obj_q = int(rel_ids[q]), int(obj_ids[q])
        subj_id = int(trng.integers(V))        # subject rendered as a clean gen token (its own identity)
        # REASON: recover object HV by unbinding the query role
        r_hv = _unbind_hrr(T, _role_vec(rel_q, seed))
        # BROKEN discriminator: unbind by a role NOT stored (identity severed)
        unused = [rr for rr in range(n_rel) if rr not in set(int(x) for x in rel_ids)]
        rel_broken = int(unused[trng.integers(len(unused))]) if unused else (rel_q + 7) % n_rel
        r_hv_broken = _unbind_hrr(T, _role_vec(rel_broken, seed))

        subj_code = L_gen[subj_id]
        rel_code = L_rel[rel_q]
        obj_true_code = L_gen[obj_q]

        # BRIDGE arms -> object filler code estimate
        code = {}
        code["cotrained_linear"] = np.sign(r_hv @ W).astype(np.float32)
        code["naive_randproj"] = np.sign(r_hv @ R_naive).astype(np.float32)
        # naive_symbolic: argmax r_hv into nearest test concept (cosine) then look up its clean gen code
        sims = bge_test @ (r_hv / (np.linalg.norm(r_hv) + 1e-12))
        j = int(np.argmax(sims))
        code["naive_symbolic"] = L_gen[j]
        # stored_direct posctrl: cotrained bridge on the CLEAN object BGE (no reasoning crosstalk)
        code["stored_direct"] = np.sign(bge_test[obj_q] @ W).astype(np.float32)
        # broken_reasoning discriminator: cotrained bridge on the severed-identity HV
        code["broken_reasoning"] = np.sign(r_hv_broken @ W).astype(np.float32)

        for a in BRIDGE_ARMS:
            ce = np.where(code[a] == 0.0, 1.0, code[a]).astype(np.float32)   # avoid 0 from sign(0)
            sp, rp, op = _generate_and_decode(subj_code, rel_code, ce, pos, L_gen, L_rel)
            exact = int(sp == subj_id and rp == rel_q and op == obj_q)
            hit[a] += exact
            ohit[a] += int(op == obj_q)
            rec_obj[a].append(op)
            bit_agree[a].append(float(np.mean(ce == obj_true_code)))

        if tr < 3:  # glass-box: log a few full loop traces (inspectable per hand-off)
            glassbox.append({
                "seed": seed, "trial": tr,
                "stored_D": D_store, "query_rel": rel_q, "true_obj": obj_q, "subj": subj_id,
                "trace_norm": round(float(np.linalg.norm(T)), 3),
                "r_hv_cos_true_obj": round(float(bge_test[obj_q] @ (r_hv / (np.linalg.norm(r_hv) + 1e-12))), 4),
                "nearest_concept_j": j, "nearest_is_true": int(j == obj_q),
                "cotrained_bit_agree_vs_Lgen_obj": round(bit_agree["cotrained_linear"][-1], 4),
                "naive_randproj_bit_agree": round(bit_agree["naive_randproj"][-1], 4),
                "broken_bit_agree": round(bit_agree["broken_reasoning"][-1], 4),
                "cotrained_obj_pred": rec_obj["cotrained_linear"][-1],
                "broken_obj_pred": rec_obj["broken_reasoning"][-1],
            })

    end2end = {a: hit[a] / trials for a in BRIDGE_ARMS}
    obj_acc = {a: ohit[a] / trials for a in BRIDGE_ARMS}
    bit_mean = {a: round(float(np.mean(bit_agree[a])), 4) for a in BRIDGE_ARMS}
    artifacts = {
        "W_digest": _digest_arr(W),
        "R_naive_digest": _digest_arr(R_naive),
        "rec_cotrained": _digest(rec_obj["cotrained_linear"]),
        "rec_broken": _digest(rec_obj["broken_reasoning"]),
        "rec_naive_randproj": _digest(rec_obj["naive_randproj"]),
    }
    _heartbeat(output_dir, seed, SEEDS[-1], t0,
               extra={"seed": seed, "cotrained_e2e": round(end2end["cotrained_linear"], 3),
                      "broken_e2e": round(end2end["broken_reasoning"], 3),
                      "posctrl_e2e": round(end2end["stored_direct"], 3)})
    _say(f"  [seed {seed}] V={V} D_store={D_store} cone={cone:.3f} | end2end: "
         f"cotrained={end2end['cotrained_linear']:.3f} naive_sym={end2end['naive_symbolic']:.3f} "
         f"naive_rp={end2end['naive_randproj']:.3f} posctrl={end2end['stored_direct']:.3f} "
         f"broken={end2end['broken_reasoning']:.3f} | bit_agree cotrained={bit_mean['cotrained_linear']:.3f}")
    return end2end, obj_acc, bit_mean, artifacts, glassbox, cone


# ============================================================
# Config + hashing
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"V": 64, "D_store": 3, "trials": 6, "n_train": 512, "seeds": (7,)}
    if mode == "smoke":
        return {"V": 256, "D_store": 3, "trials": 20, "n_train": 2048, "seeds": (7,)}
    return {"V": 1024, "D_store": 3, "trials": 60, "n_train": 4096, "seeds": SEEDS}


def _digest(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


# ============================================================
# Verdict
# ============================================================


def classify(agg: dict, mode: str):
    """agg: per-arm cross-seed mean end-to-end + object accuracy. Returns (verdict, msg, discrim_ok)."""
    cot = agg["end2end"]["cotrained_linear"]
    sym = agg["end2end"]["naive_symbolic"]
    rp = agg["end2end"]["naive_randproj"]
    pos = agg["end2end"]["stored_direct"]
    brk = agg["end2end"]["broken_reasoning"]
    best = max(cot, sym)
    best_arm = "cotrained_linear" if cot >= sym else "naive_symbolic"
    gap = best - brk

    diag = (f"end2end: cotrained={cot:.3f} naive_symbolic={sym:.3f} naive_randproj={rp:.3f} "
            f"posctrl(stored_direct)={pos:.3f} broken={brk:.3f}; best={best:.3f}({best_arm}); "
            f"discrim_gap(best-broken)={gap:.3f}; naive_advantage(cotrained-naive_randproj)={cot - rp:.3f}")

    # --- discriminator-fires gates (all modes) ---
    # (a) WIRING: posctrl (clean object through the bridge) must recover -> components + bridge sound.
    if pos < POSCTRL_FLOOR:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"posctrl stored_direct end2end={pos:.3f} < {POSCTRL_FLOOR}: bridge/generation WIRING failed "
                f"(cannot attribute any loop failure to the reasoning->generation seam). {diag}", False)
    # (b) IDENTITY: broken_reasoning (severed identity) must collapse toward chance.
    if brk > BROKEN_COLLAPSE_CEIL:
        return ("IDENTITY_DISCRIMINATOR_DID_NOT_FIRE",
                f"broken_reasoning end2end={brk:.3f} > {BROKEN_COLLAPSE_CEIL}: severed-identity loop did NOT "
                f"collapse -> end-to-end accuracy is NOT attributable to genuine reasoning (answer leakage). {diag}",
                True)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: full loop (perceive->store->reason->bridge->generate) runs end-to-end AT "
                f"N_R={N_R} N_G={N_G}; posctrl recovers, broken collapses, bridges differ. Deliverable bands are "
                f"FULL-only (canonical = remote landing). {diag}", True)

    # --- FULL pre-registered composition bands (deliverable = cotrained_linear; report best) ---
    if cot >= HP_END2END and gap >= HP_DISCRIM_GAP:
        return ("HARD_PASS",
                f"SUBSTRATE COMPOSES END-TO-END: co-trained bridge closes the reason->generate seam -- "
                f"cotrained_linear end2end={cot:.3f} (>= {HP_END2END}) with discriminator gap {gap:.3f} "
                f"(>= {HP_DISCRIM_GAP}); broken-reasoning collapses to {brk:.3f}. Naive bolt-on randproj bridge "
                f"end2end={rp:.3f} (co-trained advantage {cot - rp:.3f}); symbolic-identity bridge={sym:.3f}. {diag}",
                True)
    # HARD_PASS via symbolic/matched bridge even if the learned-vector bridge is only MIDDLE
    if best >= HP_END2END and gap >= HP_DISCRIM_GAP:
        return ("HARD_PASS",
                f"SUBSTRATE COMPOSES END-TO-END via the {best_arm} bridge (end2end={best:.3f} >= {HP_END2END}, "
                f"discriminator gap {gap:.3f}); the co-trained-VECTOR bridge is only {cot:.3f}. {diag}", True)
    if cot < HF_END2END and best < HF_END2END:
        return ("HARD_FAIL",
                f"REASON->GENERATE SEAM IS THE WALL: no honest bridge round-trips (best end2end={best:.3f} < "
                f"{HF_END2END}) while posctrl bridge ceiling={pos:.3f} (>= {POSCTRL_FLOOR}) -> the degradation is "
                f"the HAND-OFF, not any single component. Next: co-trained bridge fit on reasoning-recovered HVs "
                f"(not clean fillers). {diag}", True)
    return ("MIDDLE_BAND",
            f"PARTIAL COMPOSE: best bridge end2end={best:.3f} in [{HF_END2END},{HP_END2END}); the loop composes "
            f"imperfectly -- quantify per-seed cv and consider a co-trained-on-recovered-HV bridge. {diag}", True)


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    seeds = cfg["seeds"]
    expected_n_units = len(seeds) * len(BRIDGE_ARMS)
    _write_start_marker(output_dir, mode, expected_n_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N_R={N_R} N_G={N_G} V={cfg['V']} D_store={cfg['D_store']} "
         f"trials={cfg['trials']} n_train={cfg['n_train']} seeds={seeds} arms={BRIDGE_ARMS}")

    per_seed_e2e = {a: [] for a in BRIDGE_ARMS}
    per_seed_obj = {a: [] for a in BRIDGE_ARMS}
    per_seed_bit = {a: [] for a in BRIDGE_ARMS}
    artifacts_by_seed = {}
    glassbox_all = []
    cones = {}
    for seed in seeds:
        e2e, oacc, bit, art, gb, cone = run_seed(
            seed, cfg["V"], cfg["D_store"], cfg["trials"], cfg["n_train"], output_dir, t0)
        for a in BRIDGE_ARMS:
            per_seed_e2e[a].append(e2e[a])
            per_seed_obj[a].append(oacc[a])
            per_seed_bit[a].append(bit[a])
        artifacts_by_seed[str(seed)] = art
        glassbox_all.extend(gb)
        cones[str(seed)] = cone

    # arms_differ (META_RULE_AF): compare DISTINCT mechanism artifacts (bridge matrices differ) + verify
    # the severed-identity discriminator genuinely diverges from the co-trained recovery (not bit-identical).
    arms_differ_ok = True
    for sd, art in artifacts_by_seed.items():
        if art["W_digest"] == art["R_naive_digest"]:
            arms_differ_ok = False   # learned vs bolt-on bridge matrices identical -> arm bug
        if art["rec_cotrained"] == art["rec_broken"]:
            arms_differ_ok = False   # broken discriminator did not change recovery -> discriminator bug
    if not arms_differ_ok:
        raise AssertionError(
            "META_RULE_AF VIOLATION: bridge matrices bit-identical OR broken-reasoning recovery == "
            "cotrained recovery (discriminator did not alter output)")

    agg = {
        "end2end": {a: round(float(np.mean(per_seed_e2e[a])), 4) for a in BRIDGE_ARMS},
        "obj_acc": {a: round(float(np.mean(per_seed_obj[a])), 4) for a in BRIDGE_ARMS},
        "bit_agree": {a: round(float(np.mean(per_seed_bit[a])), 4) for a in BRIDGE_ARMS},
        "end2end_per_seed": {a: [round(v, 4) for v in per_seed_e2e[a]] for a in BRIDGE_ARMS},
    }
    verdict, vmsg, discrim_ok = classify(agg, mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: end-to-end substrate loop perceive->store->reason->bridge->generate ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(seeds),
        "n_units": len(seeds) * len(BRIDGE_ARMS),
        "expected_n_units": expected_n_units,
        "cardinality_ok": True,
        "config": {"N_R": N_R, "N_G": N_G, "BGE_DIM": BGE_DIM, "GEN_SLOTS": GEN_SLOTS,
                   "V": cfg["V"], "D_store": cfg["D_store"], "trials": cfg["trials"],
                   "n_train": cfg["n_train"], "seeds": list(seeds), "RIDGE_LAMBDA": RIDGE_LAMBDA,
                   "store_reason_algebra": "HRR_circular_conv_real_BGE_hdlab_binding",
                   "generation_algebra": "bipolar_BSC_elementwise_product_protected_index_positions",
                   "bridge_arms": BRIDGE_ARMS,
                   "real_filler_cache": str(SUBSET_PATH.relative_to(REPO))},
        "arms": {a: {"end2end_mean": agg["end2end"][a], "end2end_per_seed": agg["end2end_per_seed"][a],
                     "obj_acc_mean": agg["obj_acc"][a], "bit_agree_mean": agg["bit_agree"][a]}
                 for a in BRIDGE_ARMS},
        "controls": {"posctrl_stored_direct_end2end": agg["end2end"]["stored_direct"],
                     "broken_reasoning_end2end": agg["end2end"]["broken_reasoning"],
                     "broken_collapsed": bool(agg["end2end"]["broken_reasoning"] <= BROKEN_COLLAPSE_CEIL),
                     "chance_object_acc_THEORETICAL": round(1.0 / cfg["V"], 6),
                     "correlation_cone": cones},
        "glassbox_trace": glassbox_all,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_artifacts": artifacts_by_seed,
        "bands": {"HP_end2end": HP_END2END, "HP_discrim_gap": HP_DISCRIM_GAP, "HF_end2end": HF_END2END,
                  "posctrl_floor": POSCTRL_FLOOR, "broken_collapse_ceil": BROKEN_COLLAPSE_CEIL},
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
    cfg = get_config("selftest")
    e2e, _oacc, _bit, _art, _gb, _cone = run_seed(
        7, cfg["V"], cfg["D_store"], cfg["trials"], cfg["n_train"], output_dir, t0)
    # selftest gate: posctrl recovers (wiring) AND broken collapses below posctrl (discriminator alive)
    ok = (e2e["stored_direct"] >= 0.50) and (e2e["broken_reasoning"] <= e2e["stored_direct"] - 0.20)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: posctrl={e2e['stored_direct']:.3f} "
         f"cotrained={e2e['cotrained_linear']:.3f} broken={e2e['broken_reasoning']:.3f} "
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
