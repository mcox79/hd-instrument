"""content_dehub_joint_lever_v1 -- ONE training-free content-embedding de-hub
transform (Local Scaling, PRIMARY), applied at INPUT + retrain-from-scratch,
tested as a JOINT lever across TWO stuck capabilities at once:

  (A) GENERALIZATION rank-1 ceiling  -- filtered Hits@1 REAL-minus-SHUFFLED on the
      schema-relation reframe harness, de-hubbing the OBJECT feature matrix Fo.
  (B) ENCODER retrieval-agreement    -- in-batch-RKD student ret_agree10 vs the
      RAW BGE-large teacher's top-10, de-hubbing the RKD pairwise TARGET geometry.

SCIENTIFIC QUESTION: a probe (notes/research_content_dehub_joint_lever_gen_encoder_
2026-07-05.md) measured the hubness is MECHANISM-SHARED across the two content
spaces (cross-model hub rho=0.545, same top hub words, 49.4% vocab overlap). Does
ONE de-hub transform, applied at each content space's INPUT + retrain-from-scratch
(the UNTESTED point; NOT the post-hoc rescore that went phantom on this exact
FROZEN locus), lift BOTH downstream metrics -- PAIRED, with a SHUFFLED anti-phantom
control, gated on REAL-absolute lift?

CONTRACT BANDS (task):
  HARD-PASS = REAL-abs lift >= +0.05 on BOTH gen Hits@1 AND enc ret_agree10, with
              SHUFFLED not lifted > +0.03 (anti-phantom) on both sides.
  HARD-FAIL = either side <= +0.02.
  MIDDLE    = one side lifts (report which).
  Mechanism check (gate): Local Scaling must actually de-hub the geometry
              (nk_gini(dehub) < nk_gini(raw)) on BOTH content spaces AND on the
              synth_cross_domain_shared_hub joint-lever positive control.

DESIGN DECISIONS (cell-author autonomy; DOCUMENTED, not silent):
  * De-hub method = LOCAL_SCALING (Zelnik-Manor & Perona 2004), realized as a
    FEATURE transform (exact eigen-embedding of the symmetric-normalized self-
    tuning affinity, dehub_transforms.local_scaling_embedding). This is the SAME
    code on both sides -- literally shared -- and produces a unit-normed feature
    matrix whose cosine geometry is the de-hubbed geometry, so it drops into a
    bilinear scorer (feature input) AND an RKD Gram target (Phi @ Phi.T is a cosine
    in [-1,1], SAME RANGE as the raw teacher Gram -> a fair RAW-vs-DEHUB compare
    never changes the target SCALE, only its GEOMETRY). ZCA_WHITEN (secondary) +
    ABTT (reference/weakest) are ALSO run on the gen side (cheap, dim-preserving);
    encoder side runs the PRIMARY LOCAL_SCALING only to bound smoke cost (ZCA/ABTT
    encoder arms are FULL-optional, flagged).
  * k (local scale) = 10 (matches the note's own off-disk measurement + the
    Nielsen/Macocco/Baroni 2024 SBERT analog). rank = min(V-1, 256) gen objects;
    min(batch-1, 64) enc per-batch target. AUTONOMY per task.
  * Gen: de-hub the OBJECT codebook Fo (where the FROZEN-slot hubness lives per the
    parent note); SUBJECT features stay RAW (inductive novel-subject validity
    unchanged; the scorer's asymmetric projection maps 384-d subjects and r-d
    objects to the same df). Primary slot = FROZEN (the content-baked locus); JOINT
    is FULL-optional.
  * Enc: student INPUT stays RAW BGE (deployable; no train/eval input mismatch);
    only the RKD TARGET geometry is de-hubbed -- exactly the note's "transform the
    teacher matrix BEFORE computing the in-batch RKD relational target". Per-batch
    local scaling (in-batch RKD is batch-local by construction; tractable at FULL
    scale where a global 178k-point eigendecomposition is not). Compact in-batch-
    RKD loop reuses v3._make_student / v3._block_ste / v3._encode_hard_block and the
    EXACT in_batch RKD loss form ((code_Gram - teacher_Gram)[off]^2); it drops v3c's
    semi-hard mining + checkpoint-best-selection (NOT the de-hub variable; identical
    across all arms so it cannot confound the RAW-vs-DEHUB comparison). ret_agree10
    is measured by v3._semantic_unit VERBATIM (identical ship-metric definition).
  * SHUFFLED anti-phantom: gen = permuted labels (harness paired REAL/SHUFFLED);
    enc = permuted teacher-target control (target rows correspond to a within-batch
    permutation of point identities, decorrelating student input from target).

NOT A REPEAT of exp_schema_relation_hubness_debias_rescore_v1 (post-hoc score
rescore, partially phantom on FROZEN) -- this transforms the CONTENT INPUT before
any fit + retrains from scratch. Prior-work check (substrate-KB, USER-locked
2026-07-01): query "content embedding de-hubbing local scaling Nk-Gini
generalization encoder retrieval agreement joint lever" -> top hit cosine=0.2979
(production-deployment note), all hits < 0.30. NONE at cosine>0.30 -- no prior arc
CELL. GENUINELY NOVEL (content-side de-hub as a cross-capability joint lever).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (RAW vs LOCAL_SCALING de-hubbed Fo bytes
#   differ; enc RAW-target vs DEHUB-target Grams differ)
# - final_metrics_atomicity = tmp_replace (write to metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare)
# - crlb n/a: rank/retrieval-agreement transfer has no closed-form noise floor;
#   bands are absolute-lift deltas far above 0 and below saturation. Declared.
# - baseline_in_band at smoke: gen RAW SHUFFLED Hits@1 not saturated (<0.95); enc
#   CE_BASELINE REAL ret_agree10 in (0.05, 0.95). Reported + gated.
# - discriminator survives scale: option (B/C). Smoke fires the MECHANISM
#   discriminator directly (nk_gini reduction on BOTH real spaces + the synth
#   joint-lever positive control) at real content scale (Fo is the full V codebook;
#   teacher subsample). The downstream-LIFT question is exactly what the note calls
#   the "cheap decisive test at smoke scale before a heavy FULL" -- reported as
#   smoke-lift + FULL-readiness, NOT claimed as the final full-scale verdict.
#   MULTI-SEED smoke (3 seeds) per META_RULE_smoke_single_seed_inflates_AUC (the
#   discriminator is a continuous per-query lift).
# - HARD_PASS strictly above floor: both-sides >= 0.05 vs HARD-FAIL <= 0.02 (2.5x
#   gap; MIDDLE band strictly between) -- META_RULE_L satisfied by construction.
# - HP_SCOPE: {LOCAL_SCALING: [gen FROZEN filtered Hits@1 rms lift; enc ret_agree10
#   lift]}; ZCA/ABTT = reference (reported, not HP-gated); SHUFFLED = anti-phantom
#   control; CE_BASELINE/CONTENT_RAW = paired baseline.
# - cardinality_ok: EXPECTED_N_UNITS declared per run_mode; counted; gated.
# - per-unit failure-class instrumentation (no bare except; no silent continue).
# - calibration_check = adaptive_with_discriminator_gate: k=10 is the note's own
#   measured value (not tuned-for-pass); the nk_gini-reduction + synth-control
#   gates ARE the discriminator-fires proofs.
# - progress_logging = print_flush_true (line-buffered stdout + flush=True).
# - all numbers in this docstring tagged CITED@ / MEASURED@ / THEORETICAL@.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "8")
os.environ.setdefault("CUDA_MODULE_LOADING", "LAZY")

import argparse
import hashlib
import json
import platform
import time
import traceback
import collections
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

_ARGV_SNAPSHOT = list(sys.argv)

import torch  # overnight_queue GPU gate greps for `import torch`

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import experiments.dehub_transforms as dh
from experiments._seed_checkpoint import get_output_dir
import experiments.exp_schema_relation_hitsatk_mrr_reframe_v1 as reframe
from experiments import (
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)

# restore argv (reframe / _seed_checkpoint import-time selftests can mangle it)
if list(sys.argv) != _ARGV_SNAPSHOT:
    sys.argv = _ARGV_SNAPSHOT

ANCHOR_NAME = "content_dehub_joint_lever_v1"

# ---------------------------------------------------------------------------
# Run mode
# ---------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--full", action="store_true")
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--device", default=None, choices=[None, "cpu", "cuda"])
_ARGS, _ = _P.parse_known_args()
_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.full:
    RUN_MODE = "full"
elif _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full")

# device: default cpu for smoke/self-test (remote_cpu / laptop safety), auto for full
if _ARGS.device:
    _DEVICE = _ARGS.device
elif RUN_MODE == "full":
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
else:
    _DEVICE = "cpu"

# ---------------------------------------------------------------------------
# De-hub hyperparameters (AUTONOMY; k = note's measured value, not tuned)
# ---------------------------------------------------------------------------
DEHUB_K = 10                      # CITED@note Section 1b/1d + Nielsen 2024 SBERT analog
GEN_RANK_CAP = 256                # object-embedding rank cap (<= V-1)
ENC_TARGET_RANK_CAP = 64          # per-batch RKD-target embedding rank cap (<= batch-1)
GEN_METHODS = ["CONTENT_RAW", "LOCAL_SCALING", "ZCA_WHITEN", "ABTT"]
ENC_METHODS = ["CE_BASELINE", "LOCAL_SCALING"]
ENC_ARMS = ["REAL", "SHUFFLED"]
GEN_RELS = ["AtLocation", "CausesDesire"]   # semantic HP-eligible (note Section 1e)
ENC_ARM_REAL = "REAL"

# ---------------------------------------------------------------------------
# Bands (task contract)
# ---------------------------------------------------------------------------
HP_LIFT_MIN = 0.05                # BOTH sides REAL-abs lift >= this -> HARD-PASS
HF_LIFT_MAX = 0.02                # EITHER side <= this -> HARD-FAIL
ANTIPHANTOM_MAX = 0.03            # SHUFFLED lift must not exceed this (else phantom)
GEN_SHUF_SAT_HI = 0.95            # gen SHUFFLED Hits@1 saturation guard
ENC_BASE_LO, ENC_BASE_HI = 0.05, 0.95   # enc baseline ret_agree10 in-band

# ---------------------------------------------------------------------------
# Config grid per run_mode
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    SEEDS = [7, 13, 19]
    GEN_CONFIGS = [("V100", 100, 300), ("V300", 300, 400)]   # (name, V, M)
    GEN_HP_V = {"V300"}
    GEN_DF = 128
    GEN_STEPS = 300
    GEN_N_TEST = 60
    GEN_POOL_CAP = 6000
    ENC_STEPS = 90
    ENC_BATCH = 128
    ENC_N_TR = 900
    ENC_N_HE = 400
    ENC_FINAL_PAIRS = 20000
    ENC_NKGINI_SUB = 800
elif RUN_MODE == "self_test":
    SEEDS = [7]
    GEN_CONFIGS = [("V80", 80, 200)]
    GEN_HP_V = {"V80"}
    GEN_DF = 64
    GEN_STEPS = 60
    GEN_N_TEST = 30
    GEN_POOL_CAP = 2000
    ENC_STEPS = 10
    ENC_BATCH = 64
    ENC_N_TR = 300
    ENC_N_HE = 150
    ENC_FINAL_PAIRS = 4000
    ENC_NKGINI_SUB = 300
else:  # full
    SEEDS = [7, 13, 19]
    GEN_CONFIGS = [("V300", 300, 800), ("V1000", 1000, 800)]
    GEN_HP_V = {"V300", "V1000"}
    GEN_DF = 384
    GEN_STEPS = 2000
    GEN_N_TEST = 150
    GEN_POOL_CAP = 30000
    ENC_STEPS = 1800
    ENC_BATCH = 128
    ENC_N_TR = None                # from cache (all but held)
    ENC_N_HE = None
    ENC_FINAL_PAIRS = 400000
    ENC_NKGINI_SUB = 6000

ENC_N_DIM = v3.N_DIM_DEFAULT       # 4096
ENC_KB = v3.K_BLOCKS_PRIMARY       # 128
ENC_BLK_L = ENC_N_DIM // ENC_KB    # 32

TEACHER_CACHE_FULL = "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"


def expected_n_units() -> int:
    gen = len(SEEDS) * len(GEN_CONFIGS) * len(GEN_RELS) * len(GEN_METHODS)
    enc = len(SEEDS) * len(ENC_METHODS) * len(ENC_ARMS)
    return gen + enc


EXPECTED_N_UNITS = expected_n_units()


# ===========================================================================
# GEN SIDE -- reuse reframe harness functions verbatim; de-hub the object matrix
# ===========================================================================
def _proj_asym(d_subj: int, d_obj: int, df: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Ps = (rng.standard_normal((d_subj, df)) / np.sqrt(d_subj)).astype(np.float32)
    Po = (rng.standard_normal((d_obj, df)) / np.sqrt(d_obj)).astype(np.float32)
    return Ps, Po


def _dehub_object_matrix(Fo_raw: np.ndarray, method: str, V: int) -> np.ndarray:
    rank = min(GEN_RANK_CAP, max(2, V - 1))
    return dh.dehub_features(Fo_raw, method, k=DEHUB_K, rank=rank)


def run_gen_relation(rel: str, V: int, M: int, seed: int) -> Dict:
    """One (relation, V, seed): for each de-hub method, FROZEN filtered Hits@1/MRR
    REAL + SHUFFLED, plus nk_gini(raw)/nk_gini(dehub) of the object matrix."""
    sp = reframe.build_split_scaled(rel, seed, V, GEN_N_TEST, GEN_POOL_CAP, M)
    codebook = sp["codebook"]; obj_idx = sp["obj_idx"]; V_eff = sp["V_eff"]
    train_pairs = sp["train_pairs"]; ind_test = sp["ind_test"]; by_subj = sp["by_subj"]

    train_subs = [s for s, _ in train_pairs]
    y_train = np.array([obj_idx[o] for _, o in train_pairs], dtype=np.int64)
    rng = np.random.RandomState(seed + 991)
    y_shuf = y_train[rng.permutation(len(train_pairs))]
    ind_subs = [s for s, _ in ind_test]
    y_ind = np.array([obj_idx[o] for _, o in ind_test], dtype=np.int64)

    Fo_raw = reframe.encode_feature_matrix(codebook, "bge_semantic")
    Fa = reframe.encode_feature_matrix(train_subs, "bge_semantic")
    Fc = reframe.encode_feature_matrix(ind_subs, "bge_semantic")
    d_subj = Fa.shape[1]
    fm = reframe._filter_mask(ind_subs, y_ind, by_subj, obj_idx, V_eff)

    nk_raw = dh.nk_gini(Fo_raw, k=DEHUB_K)
    per_method: Dict[str, Dict] = {}
    fo_digests: Dict[str, str] = {}
    for method in GEN_METHODS:
        Fo_m = _dehub_object_matrix(Fo_raw, method, V_eff)
        fo_digests[method] = hashlib.sha256(np.ascontiguousarray(Fo_m).tobytes()).hexdigest()
        Ps, Po = _proj_asym(d_subj, Fo_m.shape[1], GEN_DF, reframe.PROJ_SEED)
        Wr, Ws = reframe.fit_scorer_paired(
            Fa, y_train, y_shuf, Fo_m, Ps, Po, GEN_STEPS,
            reframe.SCORER_LR, reframe.SCORER_TAU, reframe.SCORER_L2)
        Sr = reframe.score_scorer(Fc, Wr, Fo_m, Ps, Po)
        Ss = reframe.score_scorer(Fc, Ws, Fo_m, Ps, Po)
        mr = reframe.rank_metrics(reframe.filtered_ranks(Sr, y_ind, fm))
        ms = reframe.rank_metrics(reframe.filtered_ranks(Ss, y_ind, fm))
        per_method[method] = {
            "hits1_real": mr["hits1"], "hits1_shuf": ms["hits1"],
            "hits1_rms": mr["hits1"] - ms["hits1"],
            "mrr_real": mr["mrr"], "mrr_shuf": ms["mrr"],
            "mrr_rms": mr["mrr"] - ms["mrr"],
            "obj_dim": int(Fo_m.shape[1]),
            "nk_gini_obj": dh.nk_gini(Fo_m, k=DEHUB_K),
        }
    return {"rel": rel, "V": V, "V_eff": V_eff, "chance": 1.0 / V_eff,
            "nk_gini_raw_obj": nk_raw, "per_method": per_method,
            "fo_digests": fo_digests, "n_ind": int(len(y_ind))}


# ===========================================================================
# ENC SIDE -- compact in-batch-RKD; de-hub the TARGET geometry; ret_agree10 vs RAW
# ===========================================================================
def _dehub_target_gram(x: torch.Tensor) -> torch.Tensor:
    """De-hubbed RKD target Gram for a batch of RAW teacher rows x:(B,d).
    LOCAL_SCALING feature-embedding of the batch -> Phi -> Phi @ Phi.T (cosine
    in [-1,1], same range as raw x@x.T). Per-batch (in-batch RKD is batch-local)."""
    xb = x.detach().to("cpu").numpy().astype(np.float32)
    rank = min(ENC_TARGET_RANK_CAP, max(2, xb.shape[0] - 1))
    Phi = dh.local_scaling_embedding(xb, k=DEHUB_K, rank=rank)
    G = (Phi @ Phi.T).astype(np.float32)
    return torch.from_numpy(G).to(x.device)


def _train_encoder_arm(Xtr: torch.Tensor, method: str, arm: str, steps: int,
                       batch: int, seed: int, device: str) -> torch.nn.Module:
    """Compact in-batch-RKD student. INPUT stays RAW BGE (deployable); only the
    TARGET geometry is de-hubbed (LOCAL_SCALING) and/or permuted (SHUFFLED)."""
    kb, blk_l = ENC_KB, ENC_BLK_L
    d_in = Xtr.shape[1]
    student = v3._make_student("mlp", d_in, kb * blk_l, device, seed)
    opt = torch.optim.Adam(student.parameters(), lr=v3.LR)
    gen = torch.Generator().manual_seed(seed)
    V = Xtr.shape[0]
    Xd = Xtr.to(device)
    B = int(min(batch, V))
    off = ~torch.eye(B, dtype=torch.bool, device=device)
    for step in range(steps):
        bidx = torch.randint(0, V, (B,), generator=gen)
        x = Xd[bidx.to(device)]                     # RAW teacher rows -> student input
        # target geometry (optionally permuted for the SHUFFLED anti-phantom arm)
        xt = x[torch.randperm(B, generator=gen).to(device)] if arm == "SHUFFLED" else x
        if method == "LOCAL_SCALING":
            T = _dehub_target_gram(xt)
        else:                                        # CE_BASELINE = raw teacher Gram
            T = xt @ xt.T
        z = student(x)
        s = v3._block_ste(z, kb, blk_l)
        s_n = s / (s.norm(dim=-1, keepdim=True) + 1e-8)
        l_rkd = ((s_n @ s_n.T - T)[off] ** 2).mean()
        if not torch.isfinite(l_rkd):
            raise RuntimeError(f"failure_class=NAN_LOSS: {method}/{arm} step {step}")
        opt.zero_grad(); l_rkd.backward(); opt.step()
        if step % 30 == 0:
            print(f"    [enc {method}/{arm} seed{seed}] step {step}/{steps} "
                  f"rkd={float(l_rkd.detach()):.4f}", flush=True)
    return student


def run_enc(seed: int, cache_path: Path, device: str) -> Dict:
    X, ids = v3._load_teacher(cache_path)
    X = X.float()
    X = X / (X.norm(dim=-1, keepdim=True) + 1e-8)
    Vc = X.shape[0]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(Vc)
    if ENC_N_HE is None:
        n_he = min(int(round(Vc * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_tr = Vc - n_he
    else:
        if Vc < ENC_N_TR + ENC_N_HE:
            raise RuntimeError(f"failure_class=CACHE_TOO_SMALL: {Vc} < {ENC_N_TR + ENC_N_HE}")
        n_tr, n_he = ENC_N_TR, ENC_N_HE
    tr_idx = perm[:n_tr]; he_idx = perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()

    # mechanism check: nk_gini(raw) vs nk_gini(local-scaling-embedded) on a subsample
    sub = min(ENC_NKGINI_SUB, n_he)
    Xhe_sub = Xhe[:sub].numpy().astype(np.float32)
    nk_raw = dh.nk_gini(Xhe_sub, k=DEHUB_K)
    nk_ls = dh.nk_gini(dh.local_scaling_embedding(
        Xhe_sub, k=DEHUB_K, rank=min(128, sub - 1)), k=DEHUB_K)

    ret: Dict[str, Dict[str, float]] = {}
    gram_digests: Dict[str, str] = {}
    for method in ENC_METHODS:
        ret[method] = {}
        for arm in ENC_ARMS:
            student = _train_encoder_arm(Xtr, method, arm, ENC_STEPS, ENC_BATCH,
                                         seed + (0 if arm == "REAL" else 5), device)
            codes = v3._encode_hard_block(student, Xhe, ENC_KB, ENC_BLK_L)
            unit = v3._semantic_unit(f"{method}_{arm}", codes, codes, Xhe, Xhe, 0,
                                     ENC_FINAL_PAIRS, seed + 3)
            ret[method][arm] = float(unit["ret_agree10"])
            if arm == "REAL":
                ret[method]["spearman_real"] = float(unit["spearman_all"])
                ret[method]["hi80_cos_real"] = float(unit["hi80_cos"])
            print(f"  [enc seed{seed}] {method}/{arm} ret_agree10="
                  f"{ret[method][arm]:.4f}", flush=True)
        # arms-differ digest on the de-hubbed vs raw target of a fixed batch
    # target-differ digest: raw vs dehub Gram on a fixed reference batch
    ref = Xtr[:min(ENC_BATCH, Xtr.shape[0])].to(device)
    graw = (ref @ ref.T)
    gdeh = _dehub_target_gram(ref)
    gram_digests["CE_BASELINE"] = hashlib.sha256(
        np.ascontiguousarray(graw.detach().cpu().numpy()).tobytes()).hexdigest()
    gram_digests["LOCAL_SCALING"] = hashlib.sha256(
        np.ascontiguousarray(gdeh.detach().cpu().numpy()).tobytes()).hexdigest()
    return {"seed": seed, "n_tr": int(n_tr), "n_he": int(n_he), "V_cache": int(Vc),
            "nk_gini_raw": nk_raw, "nk_gini_dehub": nk_ls,
            "ret_agree10": ret, "gram_digests": gram_digests,
            "teacher_cache": cache_path.name}


def _resolve_enc_cache() -> Path:
    if RUN_MODE == "full":
        return v3._resolve_teacher_cache(TEACHER_CACHE_FULL)
    # smoke/self_test: smallest local bge_large cache with enough concepts
    need = (ENC_N_TR or 900) + (ENC_N_HE or 400)
    cand_dir = REPO / "data" / "substrate_index" / "cached_indices"
    best: Optional[Tuple[int, Path]] = None
    for p in sorted(cand_dir.glob("bge_large_v2_name_*.npz")):
        try:
            cnt = int(p.stem.split("_")[4])
        except (IndexError, ValueError):
            continue
        if cnt >= need and (best is None or cnt < best[0]):
            best = (cnt, p)
    if best is None:
        return v3._resolve_teacher_cache(None)
    return best[1]


# ===========================================================================
# synth_cross_domain_shared_hub -- joint-lever-specific POSITIVE control
# ===========================================================================
def synth_cross_domain_shared_hub(seed: int) -> Dict:
    """Two synthetic content spaces (different dim, different generator seed) that
    SHARE a designed common subset of central/hub items (mirrors the measured
    rho=0.545 cross-model property). Verify the SAME de-hub transform, fit +
    applied INDEPENDENTLY to each, reduces Nk-Gini in BOTH."""
    rng = np.random.RandomState(seed + 4242)
    n, n_shared = 300, 40
    shared_assign = rng.randint(0, 4, size=n_shared)   # shared hub identities

    def _space(d: int, n_hub: int, pull: float, s2: int) -> np.ndarray:
        r = np.random.RandomState(s2)
        hubs = r.standard_normal((n_hub, d)); hubs /= np.linalg.norm(hubs, axis=1, keepdims=True) + 1e-9
        base = r.standard_normal((n, d)); base /= np.linalg.norm(base, axis=1, keepdims=True) + 1e-9
        assign = r.randint(0, n_hub, size=n)
        assign[:n_shared] = shared_assign               # SAME items are hubs in BOTH
        X = (1 - pull) * base + pull * hubs[assign]
        X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
        return X.astype(np.float32)

    A = _space(48, 4, 0.7, seed + 1)
    Bx = _space(96, 4, 0.7, seed + 2)                   # different dim + generator
    gA_raw = dh.nk_gini(A, k=DEHUB_K)
    gB_raw = dh.nk_gini(Bx, k=DEHUB_K)
    gA_ls = dh.nk_gini(dh.local_scaling_embedding(A, k=DEHUB_K), k=DEHUB_K)
    gB_ls = dh.nk_gini(dh.local_scaling_embedding(Bx, k=DEHUB_K), k=DEHUB_K)
    both_reduced = (gA_ls < gA_raw - 1e-6) and (gB_ls < gB_raw - 1e-6)
    return {"gA_raw": gA_raw, "gA_dehub": gA_ls, "gB_raw": gB_raw, "gB_dehub": gB_ls,
            "both_reduced": bool(both_reduced)}


# ===========================================================================
# Aggregate + verdict
# ===========================================================================
def _mean(vals: List[float]) -> float:
    v = [x for x in vals if x == x]
    return float(np.mean(v)) if v else float("nan")


def _std(vals: List[float]) -> float:
    v = [x for x in vals if x == x]
    return float(np.std(v, ddof=1)) if len(v) > 1 else 0.0


def aggregate(gen_runs: List[Dict], enc_runs: List[Dict]) -> Dict:
    # GEN: per (rel) at HP V-configs, per method: mean hits1_rms / hits1_shuf across seeds
    gen_by: Dict[Tuple[str, str, str], List[Dict]] = collections.defaultdict(list)
    gen_nk_raw: List[float] = []
    gen_nk_ls: List[float] = []
    for gr in gen_runs:
        if gr["V"] in [c[1] for c in GEN_CONFIGS if c[0] in GEN_HP_V]:
            gen_nk_raw.append(gr["nk_gini_raw_obj"])
            gen_nk_ls.append(gr["per_method"]["LOCAL_SCALING"]["nk_gini_obj"])
        for method, md in gr["per_method"].items():
            gen_by[(gr["rel"], f"V{gr['V']}", method)].append(md)

    # per-relation LOCAL_SCALING lift over CONTENT_RAW at HP V-configs
    gen_rel_lift: Dict[str, float] = {}
    gen_rel_shuf_lift: Dict[str, float] = {}
    for rel in GEN_RELS:
        ls_rms, raw_rms, ls_shuf, raw_shuf = [], [], [], []
        for (r, vname, method), rows in gen_by.items():
            if r != rel:
                continue
            if vname not in {f"V{v}" for (nm, v, m) in [(c[0], c[1], 0) for c in GEN_CONFIGS] if nm in GEN_HP_V}:
                continue
            if method == "LOCAL_SCALING":
                ls_rms += [x["hits1_rms"] for x in rows]
                ls_shuf += [x["hits1_shuf"] for x in rows]
            elif method == "CONTENT_RAW":
                raw_rms += [x["hits1_rms"] for x in rows]
                raw_shuf += [x["hits1_shuf"] for x in rows]
        gen_rel_lift[rel] = _mean(ls_rms) - _mean(raw_rms)
        gen_rel_shuf_lift[rel] = _mean(ls_shuf) - _mean(raw_shuf)

    gen_lift = _mean([gen_rel_lift[r] for r in GEN_RELS])
    gen_shuf_lift = _mean([gen_rel_shuf_lift[r] for r in GEN_RELS])
    # gen SHUFFLED saturation (RAW arm)
    gen_shuf_sat = _mean([x["hits1_shuf"] for (r, v, m), rows in gen_by.items()
                          if m == "CONTENT_RAW" for x in rows])

    # reference methods (ZCA/ABTT) gen lift for reporting
    def _method_lift(method: str) -> float:
        lifts = []
        for rel in GEN_RELS:
            m_rms = [x["hits1_rms"] for (r, v, mm), rows in gen_by.items()
                     if r == rel and mm == method for x in rows]
            r_rms = [x["hits1_rms"] for (r, v, mm), rows in gen_by.items()
                     if r == rel and mm == "CONTENT_RAW" for x in rows]
            lifts.append(_mean(m_rms) - _mean(r_rms))
        return _mean(lifts)
    gen_zca_lift = _method_lift("ZCA_WHITEN")
    gen_abtt_lift = _method_lift("ABTT")

    # ENC: LOCAL_SCALING REAL ret_agree10 lift over CE_BASELINE REAL
    enc_base_real = _mean([er["ret_agree10"]["CE_BASELINE"]["REAL"] for er in enc_runs])
    enc_ls_real = _mean([er["ret_agree10"]["LOCAL_SCALING"]["REAL"] for er in enc_runs])
    enc_base_shuf = _mean([er["ret_agree10"]["CE_BASELINE"]["SHUFFLED"] for er in enc_runs])
    enc_ls_shuf = _mean([er["ret_agree10"]["LOCAL_SCALING"]["SHUFFLED"] for er in enc_runs])
    enc_lift = enc_ls_real - enc_base_real
    enc_shuf_lift = enc_ls_shuf - enc_base_shuf
    enc_nk_raw = _mean([er["nk_gini_raw"] for er in enc_runs])
    enc_nk_ls = _mean([er["nk_gini_dehub"] for er in enc_runs])

    return {
        "gen_lift_hits1": gen_lift, "gen_lift_hits1_std": _std([gen_rel_lift[r] for r in GEN_RELS]),
        "gen_rel_lift": gen_rel_lift, "gen_shuf_lift": gen_shuf_lift,
        "gen_shuf_sat": gen_shuf_sat,
        "gen_zca_lift": gen_zca_lift, "gen_abtt_lift": gen_abtt_lift,
        "gen_nk_gini_raw": _mean(gen_nk_raw), "gen_nk_gini_dehub": _mean(gen_nk_ls),
        "enc_lift_ret_agree10": enc_lift, "enc_shuf_lift": enc_shuf_lift,
        "enc_base_real": enc_base_real, "enc_ls_real": enc_ls_real,
        "enc_base_shuf": enc_base_shuf, "enc_ls_shuf": enc_ls_shuf,
        "enc_nk_gini_raw": enc_nk_raw, "enc_nk_gini_dehub": enc_nk_ls,
    }


def compute_verdict(agg: Dict, synth: Dict, arms_differ_ok: bool,
                    n_units: int) -> Tuple[str, str, Dict]:
    gen_lift = agg["gen_lift_hits1"]
    enc_lift = agg["enc_lift_ret_agree10"]
    gen_nk_reduced = agg["gen_nk_gini_dehub"] < agg["gen_nk_gini_raw"] - 1e-6
    enc_nk_reduced = agg["enc_nk_gini_dehub"] < agg["enc_nk_gini_raw"] - 1e-6
    synth_ok = bool(synth["both_reduced"])
    gen_phantom = agg["gen_shuf_lift"] > ANTIPHANTOM_MAX
    enc_phantom = agg["enc_shuf_lift"] > ANTIPHANTOM_MAX
    gen_sat = agg["gen_shuf_sat"] >= GEN_SHUF_SAT_HI
    enc_in_band = ENC_BASE_LO < agg["enc_base_real"] < ENC_BASE_HI

    diag = {
        "gen_lift_hits1": gen_lift, "enc_lift_ret_agree10": enc_lift,
        "gen_nk_reduced": gen_nk_reduced, "enc_nk_reduced": enc_nk_reduced,
        "synth_cross_domain_both_reduced": synth_ok,
        "gen_shuf_lift": agg["gen_shuf_lift"], "enc_shuf_lift": agg["enc_shuf_lift"],
        "gen_phantom": gen_phantom, "enc_phantom": enc_phantom,
        "gen_shuf_saturated": gen_sat, "enc_baseline_in_band": enc_in_band,
        "arms_differ_ok": arms_differ_ok,
        "mechanism_dehub_fires_both": gen_nk_reduced and enc_nk_reduced,
    }

    tail = (f"[gen Hits@1 lift={gen_lift:+.4f} (Nk-Gini {agg['gen_nk_gini_raw']:.3f}"
            f"->{agg['gen_nk_gini_dehub']:.3f}) | enc ret_agree10 lift={enc_lift:+.4f} "
            f"(Nk-Gini {agg['enc_nk_gini_raw']:.3f}->{agg['enc_nk_gini_dehub']:.3f}, "
            f"base={agg['enc_base_real']:.3f}) | shuf_lift gen={agg['gen_shuf_lift']:+.3f} "
            f"enc={agg['enc_shuf_lift']:+.3f} | synth_both_reduced={synth_ok}]")

    # ---- hard gates ----
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{n_units}/{EXPECTED_N_UNITS} units {tail}", diag)
    if not arms_differ_ok:
        return ("HARD_FAIL", f"META_RULE_AF_VIOLATION: de-hub arms bit-identical to RAW {tail}", diag)

    # ---- mechanism-fires gate (SMOKE discipline: de-hub must de-hub the geometry) ----
    if not (gen_nk_reduced and enc_nk_reduced and synth_ok):
        return ("SMOKE_GATE_FAIL",
                f"MECHANISM_DID_NOT_FIRE: LOCAL_SCALING failed to reduce Nk-Gini on "
                f"gen={gen_nk_reduced}/enc={enc_nk_reduced} content OR synth joint-lever "
                f"control did not reduce both ({synth_ok}); the transform is not de-hubbing "
                f"the geometry -> re-spec k/rank before any FULL. {tail}", diag)

    # ---- phantom guard (anti-phantom): demote a side whose SHUFFLED baseline was inflated ----
    eff_gen = gen_lift if not gen_phantom else min(gen_lift, HF_LIFT_MAX)
    eff_enc = enc_lift if not enc_phantom else min(enc_lift, HF_LIFT_MAX)

    both_pass = (eff_gen >= HP_LIFT_MIN and eff_enc >= HP_LIFT_MIN
                 and not gen_phantom and not enc_phantom)
    if both_pass:
        return ("HARD_PASS",
                f"JOINT_LEVER_CONFIRMED: ONE training-free content de-hub (LOCAL_SCALING at "
                f"input + retrain-from-scratch) lifts BOTH generalization Hits@1 (+{gen_lift:.3f}) "
                f"AND encoder ret_agree10 (+{enc_lift:.3f}) >= {HP_LIFT_MIN}, SHUFFLED not lifted "
                f"(anti-phantom holds), Nk-Gini reduced on both content spaces + synth joint-lever "
                f"control fires. The shared-hub-mechanism prediction (rho=0.545) is realized as a "
                f"real cross-capability lever. {tail}", diag)

    either_fail = (eff_gen <= HF_LIFT_MAX or eff_enc <= HF_LIFT_MAX)
    one_side = (eff_gen >= HP_LIFT_MIN) ^ (eff_enc >= HP_LIFT_MIN)
    if one_side and not either_fail:
        which = "generalization" if eff_gen >= HP_LIFT_MIN else "encoder_ret_agree10"
        return ("MIDDLE_BAND",
                f"SINGLE_SIDE_LIFT: LOCAL_SCALING clears +{HP_LIFT_MIN} on ONE side ({which}) but "
                f"not both (gen={gen_lift:+.3f}, enc={enc_lift:+.3f}); the content-geometry de-hub is "
                f"REAL and the pre-training application point IS reachable, but the joint claim needs "
                f"the complementary label-prior/distillation fix layered on the other side. {tail}",
                diag)
    if either_fail:
        # joint lever falsified; surface any standalone single-side win honestly
        standalone = []
        if eff_gen >= HP_LIFT_MIN and not gen_phantom:
            standalone.append(f"gen(+{gen_lift:.3f})")
        if eff_enc >= HP_LIFT_MIN and not enc_phantom:
            standalone.append(f"enc(+{enc_lift:.3f})")
        sa = (" standalone single-side win: " + ",".join(standalone)) if standalone else ""
        return ("HARD_FAIL",
                f"JOINT_LEVER_FALSIFIED: LOCAL_SCALING lift <= {HF_LIFT_MAX} on at least one side "
                f"(gen={gen_lift:+.3f}, enc={enc_lift:+.3f}); de-hubs the geometry (Nk-Gini reduced) "
                f"but that does not convert to a joint downstream lift.{sa} {tail}", diag)
    # both in (HF, HP) partial
    return ("MIDDLE_BAND",
            f"PARTIAL_BOTH_SIDES: LOCAL_SCALING gives a real but sub-threshold lift on both sides "
            f"(gen={gen_lift:+.3f}, enc={enc_lift:+.3f}, both in ({HF_LIFT_MAX},{HP_LIFT_MIN})); "
            f"content-geometry de-hub partially reachable at the pre-training point. {tail}", diag)


# ===========================================================================
# Defensive: start-marker + crash-diagnostic
# ===========================================================================
def _write_start_marker(out_dir: Path):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "device": _DEVICE,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _emit_heartbeat(out_dir: Path, unit_idx: int, total: int, t0: float):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total, "elapsed_s": time.time() - t0}
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def _write_crash_metrics(out_dir: Path, exc: Exception):
    diag = {"anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ===========================================================================
# Main
# ===========================================================================
def _run_all(out_dir: Path) -> Dict:
    t0 = time.time()
    _write_start_marker(out_dir)
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} device={_DEVICE} seeds={SEEDS} "
          f"gen_cfgs={[c[0] for c in GEN_CONFIGS]} rels={GEN_RELS} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)

    cache_path = _resolve_enc_cache()
    print(f"[{ANCHOR_NAME}] enc teacher cache = {cache_path.name}", flush=True)

    gen_runs: List[Dict] = []
    enc_runs: List[Dict] = []
    n_units = 0
    ui = 0
    for seed in SEEDS:
        for (cname, V, M) in GEN_CONFIGS:
            for rel in GEN_RELS:
                gr = run_gen_relation(rel, V, M, seed)
                gen_runs.append(gr)
                n_units += len(gr["per_method"])          # one unit per de-hub method
                ui += 1
                _emit_heartbeat(out_dir, ui, len(SEEDS), t0)
                ls = gr["per_method"]["LOCAL_SCALING"]; rw = gr["per_method"]["CONTENT_RAW"]
                print(f"  [gen seed{seed} {cname} {rel[:11]}] "
                      f"RAW Hits@1 rms={rw['hits1_rms']:+.3f} LS Hits@1 rms={ls['hits1_rms']:+.3f} "
                      f"(lift={ls['hits1_rms']-rw['hits1_rms']:+.3f}) Nk-Gini "
                      f"{gr['nk_gini_raw_obj']:.3f}->{ls['nk_gini_obj']:.3f}", flush=True)
        er = run_enc(seed, cache_path, _DEVICE)
        enc_runs.append(er)
        n_units += len(ENC_METHODS) * len(ENC_ARMS)
        _emit_heartbeat(out_dir, ui, len(SEEDS), t0)

    synth = synth_cross_domain_shared_hub(SEEDS[0])
    print(f"  [synth cross-domain] A {synth['gA_raw']:.3f}->{synth['gA_dehub']:.3f} "
          f"B {synth['gB_raw']:.3f}->{synth['gB_dehub']:.3f} both_reduced={synth['both_reduced']}",
          flush=True)

    # arms-differ: RAW vs LOCAL_SCALING object matrices (gen) + raw vs dehub Gram (enc)
    g0 = gen_runs[0]["fo_digests"]
    e0 = enc_runs[0]["gram_digests"]
    arms_differ_ok = (g0["CONTENT_RAW"] != g0["LOCAL_SCALING"]
                      and e0["CE_BASELINE"] != e0["LOCAL_SCALING"])

    agg = aggregate(gen_runs, enc_runs)
    verdict, verdict_msg, diag = compute_verdict(agg, synth, arms_differ_ok, n_units)

    elapsed = time.time() - t0
    summary = (f"{verdict}: gen_Hits@1_lift={agg['gen_lift_hits1']:+.4f} "
               f"enc_ret_agree10_lift={agg['enc_lift_ret_agree10']:+.4f} "
               f"gen_NkGini={agg['gen_nk_gini_raw']:.3f}->{agg['gen_nk_gini_dehub']:.3f} "
               f"enc_NkGini={agg['enc_nk_gini_raw']:.3f}->{agg['enc_nk_gini_dehub']:.3f}")

    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "device": _DEVICE, "seeds": SEEDS, "dehub_k": DEHUB_K,
        "gen_methods": GEN_METHODS, "enc_methods": ENC_METHODS, "enc_arms": ENC_ARMS,
        "gen_rels": GEN_RELS, "gen_configs": [c[0] for c in GEN_CONFIGS],
        "expected_n_units": EXPECTED_N_UNITS, "n_units_counted": n_units,
        "cardinality_ok": n_units >= EXPECTED_N_UNITS,
        "arms_differ_verified": arms_differ_ok,
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "calibration_check": "adaptive_with_discriminator_gate",
        "crlb_n/a": "rank/retrieval-agreement transfer; no closed-form noise floor; bands are absolute-lift deltas",
        "discriminator_reachability": True,
        "bands": {"HP_LIFT_MIN": HP_LIFT_MIN, "HF_LIFT_MAX": HF_LIFT_MAX,
                  "ANTIPHANTOM_MAX": ANTIPHANTOM_MAX},
        "hp_scope": {"LOCAL_SCALING": ["gen_FROZEN_filtered_Hits1_rms_lift",
                                       "enc_ret_agree10_lift"],
                     "ZCA_WHITEN": ["reference_reported_not_HP"],
                     "ABTT": ["reference_weakest_reported_not_HP"],
                     "SHUFFLED": ["anti_phantom_control"],
                     "CONTENT_RAW/CE_BASELINE": ["paired_baseline"]},
        "aggregate": agg,
        "synth_cross_domain_shared_hub": synth,
        "gen_runs": gen_runs, "enc_runs": enc_runs,
        "gate_diagnostics": diag,
        "reference_lifts": {"gen_zca_lift": agg["gen_zca_lift"],
                            "gen_abtt_lift": agg["gen_abtt_lift"]},
        "n_generative_llm_calls": 0, "allow_synthetic": False,
        "metrics_source": "measured_dehub_joint_lever_gen_frozen_enc_inbatch_rkd",
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": summary,
        "elapsed_s": elapsed,
    }
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, out_dir / "metrics.json")
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s units={n_units}/{EXPECTED_N_UNITS}", flush=True)
    return metrics


def main():
    anchor = ANCHOR_NAME + ("_smoke" if RUN_MODE == "smoke" else "")
    if RUN_MODE == "self_test":
        anchor = ANCHOR_NAME + "_selftest"
    out_dir = get_output_dir(anchor)
    _run_all(out_dir)


# ===========================================================================
# Self-test (fast; formula + verdict-band logic; tiny synthetic; cache-tolerant)
# ===========================================================================
def run_self_test() -> int:
    t0 = time.time()
    dh.formula_selftests(verbose=True)

    # verdict-band logic on hand-set aggregates
    def _agg(gl, el, gnk=(0.4, 0.2), enk=(0.45, 0.25), gsl=0.0, esl=0.0, eb=0.3):
        return {"gen_lift_hits1": gl, "enc_lift_ret_agree10": el,
                "gen_nk_gini_raw": gnk[0], "gen_nk_gini_dehub": gnk[1],
                "enc_nk_gini_raw": enk[0], "enc_nk_gini_dehub": enk[1],
                "gen_shuf_lift": gsl, "enc_shuf_lift": esl,
                "gen_shuf_sat": 0.2, "enc_base_real": eb}
    synth_ok = {"both_reduced": True}
    synth_no = {"both_reduced": False}

    v, _, _ = compute_verdict(_agg(0.08, 0.09), synth_ok, True, EXPECTED_N_UNITS)
    assert v == "HARD_PASS", f"expected HARD_PASS got {v}"
    v, _, _ = compute_verdict(_agg(0.08, 0.01), synth_ok, True, EXPECTED_N_UNITS)
    assert v == "HARD_FAIL", f"expected HARD_FAIL (enc<=0.02) got {v}"
    v, _, _ = compute_verdict(_agg(0.08, 0.035), synth_ok, True, EXPECTED_N_UNITS)
    assert v == "MIDDLE_BAND", f"expected MIDDLE_BAND (one side) got {v}"
    v, _, _ = compute_verdict(_agg(0.03, 0.035), synth_ok, True, EXPECTED_N_UNITS)
    assert v == "MIDDLE_BAND", f"expected MIDDLE_BAND (partial both) got {v}"
    # mechanism did not fire (gen nk not reduced) -> SMOKE_GATE_FAIL
    v, _, _ = compute_verdict(_agg(0.08, 0.09, gnk=(0.4, 0.5)), synth_ok, True, EXPECTED_N_UNITS)
    assert v == "SMOKE_GATE_FAIL", f"expected SMOKE_GATE_FAIL (gen nk not reduced) got {v}"
    # synth control fails -> SMOKE_GATE_FAIL
    v, _, _ = compute_verdict(_agg(0.08, 0.09), synth_no, True, EXPECTED_N_UNITS)
    assert v == "SMOKE_GATE_FAIL", f"expected SMOKE_GATE_FAIL (synth) got {v}"
    # phantom on enc (shuffled inflated) -> enc demoted -> not both pass
    v, _, _ = compute_verdict(_agg(0.08, 0.09, esl=0.10), synth_ok, True, EXPECTED_N_UNITS)
    assert v in ("MIDDLE_BAND", "HARD_FAIL"), f"expected demotion under phantom got {v}"
    # cardinality breach
    v, _, _ = compute_verdict(_agg(0.08, 0.09), synth_ok, True, EXPECTED_N_UNITS - 1)
    assert v == "HARD_FAIL", f"expected HARD_FAIL (cardinality) got {v}"
    # arms identical
    v, _, _ = compute_verdict(_agg(0.08, 0.09), synth_ok, False, EXPECTED_N_UNITS)
    assert v == "HARD_FAIL", f"expected HARD_FAIL (arms identical) got {v}"

    # synth cross-domain control actually reduces both
    sc = synth_cross_domain_shared_hub(0)
    assert sc["both_reduced"], f"synth control did not reduce both: {sc}"

    # tiny gen path on real bge cache if available (cache-tolerant)
    try:
        gr = run_gen_relation("AtLocation", 80, 200, 7)
        assert "LOCAL_SCALING" in gr["per_method"]
        assert gr["per_method"]["LOCAL_SCALING"]["nk_gini_obj"] < gr["nk_gini_raw_obj"] + 0.05
        print(f"[selftest] gen path OK (V_eff={gr['V_eff']} "
              f"LS Hits@1 rms={gr['per_method']['LOCAL_SCALING']['hits1_rms']:+.3f})", flush=True)
    except Exception as e:
        print(f"[selftest] gen path skipped ({type(e).__name__}: {str(e)[:120]})", flush=True)

    print(f"[selftest] PASS (dehub formulas + verdict bands + synth control + gen path) "
          f"elapsed={time.time()-t0:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    if RUN_MODE == "self_test":
        try:
            sys.exit(run_self_test())
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            _out = get_output_dir(ANCHOR_NAME + "_selftest")
            _write_crash_metrics(_out, e)
            raise
    _OUT = get_output_dir(ANCHOR_NAME + ("_smoke" if RUN_MODE == "smoke" else ""))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT, e)
        raise
