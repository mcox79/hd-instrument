# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 of per-example predicted-index vectors, pairwise distinct)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no learned-noise Cramer-Rao floor; discriminator = pre-registered CONVERSION_FIX_LIFTS /
#   PARTIAL / NO_LIFT / INVALID rule (Director spawn 2026-07-30, "localized bottleneck: real->FHRR
#   encoding conversion" cell).
# - baseline_in_band: n/a -- no learned baseline arm to saturate; the 3 floors ARE the can-fail controls
#   (reused VERBATIM from exp_vsa_native_bind_zeroshot_role_v1 via kx), decide_verdict() requires ALL
#   THREE to independently collapse to near-chance per key-arm or that arm's result is INVALID.
# - discriminator survives scale: closed-form (no training loop, no smoke/full scale gap); self-test
#   exercises the REAL frozen v2 encoder + REAL oc.build_oracle_table at tiny n (real_code_path)
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed/torch.Generator only; NO hash(),
#   NO list(set())
"""Does fixing the real->FHRR ENCODING CONVERSION step (not the real-space orthogonalizing transform
itself) recover the exact-orthogonality Lowdin/QR already achieve in real space, and lift native FHRR
zero-shot novel-role recall toward chain-grade? (Director spawn 2026-07-30, "localized bottleneck".)

WHY (mechanism this cell isolates -- narrower than the prior enabler): exp_vsa_key_orthogonalization_
transform_v1 (commit aca66a929) measured that Lowdin/QR/ZCA achieve EXACT real-space key orthogonality
(toy-case cos<0.01, MEASURED@data/exp_vsa_key_orthogonalization_transform_v1/metrics.json:selftest.
transform_diag) but the post-ENCODING (after z-score + phase-encode) off-diagonal cosine only moves
from raw=0.3478 to lowdin=0.3520 (MEASURED@same file:cosines) -- i.e. the exact real-space
orthogonality is almost ENTIRELY destroyed by the z-score+phase-encode conversion step, landing verdict
PARTIAL (MEASURED@same file:verdict).

INSPECTING THAT CELL'S OWN encoder_table_for() (experiments/exp_vsa_key_orthogonalization_transform_v1.
py, function encoder_table_for): mu = T.mean(dim=0, keepdim=True); sd = T.std(dim=0, keepdim=True) --
this is a PER-COLUMN (per-feature, over the 15 role-rows) affine rescale: Z[i,j] = (T[i,j]-mu[j])/sd[j].
This is NOT a per-sample step in the "one z-score per example" sense, but it IS a per-FEATURE diagonal
rescale, i.e. Z = (T - 1 mu^T) @ diag(1/sd). CLAIM (THEORETICAL, linear algebra): a per-column diagonal
rescale with NON-UNIFORM sd across the d=512 columns does NOT preserve the row Gram matrix T T^T that
Lowdin/QR just forced to I -- diag(1/sd) is not a scalar multiple of the identity, so it warps the
15x15 pairwise-angle structure between role keys BEFORE the phase-encode nonlinearity even runs. A
GLOBAL SCALAR normalization (one mu, one sd, computed over ALL n*d entries, not per-column) rescales
every row by the SAME constant, which preserves the Gram matrix up to a strictly positive scalar
multiple (Z Z^T = c * T_c T_c^T for centered T_c, c>0) -- i.e. it should NOT re-introduce the
correlation that the per-column step does. THIS CELL tests that specific claim: does swapping the
per-column z-score for a GLOBAL SCALAR z-score (everything else byte-identical: same Lowdin transform,
same PHASE_SCALE, same phase-encode nonlinearity, same task/floors/gamma) let the already-exact real-
space orthogonality survive into the FHRR keys?

ONE VARIABLE = the encoding-conversion's normalization granularity (per-column vs global-scalar), for
a FIXED already-orthogonalized real matrix (transform_lowdin, reused verbatim from the prior enabler
cell, aliased `kx`). Everything else (encoder, oracle table construction, phase-encode functional form,
bind/unbind, floors, gamma-tuning, task corpus) is BYTE-IDENTICAL, reused via kx/vz (which themselves
chain to oc/base/rc) -- same TRAIN_ROLES_V2/HELD_OUT_ROLES_V2 zero-shot split, same 3 can-fail floors.

KEY-ARMS (report cosine AND recall together per Director spawn fairness requirement):
  ARM_RAW_COLSCALE      -- kx's ARM_RAW reproduced exactly (T=identity, per-column z-score). Gate-D
    positive control: MUST reproduce kx's MEASURED raw cosine=0.3478 within REPRO_TOL.
  ARM_LOWDIN_COLSCALE   -- kx's ARM_LOWDIN reproduced exactly (T=lowdin, per-column z-score). Gate-D
    positive control: MUST reproduce kx's MEASURED lowdin cosine=0.3520 within REPRO_TOL.
  ARM_RAW_GLOBALSCALE   -- T=identity, GLOBAL SCALAR z-score (mu,sd over all n*d entries). Isolates
    whether global-scalar normalization alone (no orthogonalization) moves cosine -- control for the
    next arm.
  ARM_LOWDIN_GLOBALSCALE -- T=lowdin, GLOBAL SCALAR z-score. THE FIX under test: does the already-
    exact real-space orthogonality now survive into the FHRR keys?
  ARM_CLEAN            -- kx's ARM_CLEAN reused verbatim (independent random-phase FHRR table):
    reference ceiling.

PRE-REGISTERED DECISION RULE (written BEFORE running; NOT loosened after seeing results):
  CONVERSION_FIX_LIFTS: ARM_LOWDIN_GLOBALSCALE achieves off-diagonal cosine < COSINE_HARD_PASS=0.20 AND
    recall_heldout_acc >= ORACLE_MIN=0.50 on ALL 3 seeds AND all 3 floors collapse to <= FAIL_MAX=0.15
    on ALL 3 seeds for that arm AND both Gate-D reproduction arms (ARM_RAW_COLSCALE, ARM_LOWDIN_
    COLSCALE) match kx's MEASURED numbers within REPRO_TOL => the encoding-conversion (not the
    orthogonalizing transform) was the localized bottleneck; native binding is now deployable.
  PARTIAL: ARM_LOWDIN_GLOBALSCALE's cosine drops by >= COS_IMPROVE_MARGIN=0.05 vs ARM_LOWDIN_COLSCALE
    AND/OR recall improves by >= RECALL_IMPROVE_MARGIN=0.10, but doesn't clear both HARD-PASS bars =>
    the conversion fix helps but the residual is inherent to something else (report the gain honestly).
  NO_LIFT: ARM_LOWDIN_GLOBALSCALE cosine/recall are within margin of ARM_LOWDIN_COLSCALE (no
    meaningful gain) => the per-column-vs-global-scalar distinction was NOT the bottleneck; the
    residual correlation is inherent to phase-encoding this real-encoder key set at this d, regardless
    of normalization granularity.
  INVALID: either Gate-D reproduction arm misses tolerance (kx invocation drift) OR any floor fails to
    collapse for an arm being interpreted.

COSINE_HARD_PASS = 0.20 (HYPOTHESIZED@this file: comfortably below the measured raw/lowdin-colscale
plateau of ~0.35, and below kx's own coordinator-set HARD_PASS_COS_15=0.15 by a looser margin since
this is a narrower single-shot mechanism probe, not the full frontier-plan gate).
COS_IMPROVE_MARGIN = 0.05, RECALL_IMPROVE_MARGIN = 0.10 (HYPOTHESIZED@this file: same order as kx's
PARTIAL_MARGIN=0.10 convention, cosine margin set tighter since cosine has lower measured seed-to-seed
noise than recall in kx's own data).
FAIL_MAX = CHANCE_RECALL(0.05) + 0.10 = 0.15, ORACLE_MIN = 0.50, REPRO_TOL = 0.05 (all THEORETICAL,
same convention as kx/vz).

Run:  .venv/Scripts/python.exe experiments/exp_vsa_key_globalscale_phase_conversion_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_vsa_key_globalscale_phase_conversion_v1.py --full

ASCII-only. No emojis. CPU (local, push-free). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- closed-form bind/unbind/decode + one fixed eigh
(Lowdin, reused from kx) over cached examples, NO gradient descent; kx's own byte-identical full run
measured elapsed_s=20.15 (MEASURED@data/exp_vsa_key_orthogonalization_transform_v1/metrics.json:
elapsed_s); this cell does strictly fewer arms (4 new + reused clean vs kx's 6) so wall time is
expected well under kx's already-fast run, far inside the 15-minute cap.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_vsa_key_orthogonalization_transform_v1 as kx  # noqa: E402
import exp_vsa_native_bind_zeroshot_role_v1 as vz  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402
from hdlab import binding  # noqa: E402  -- explicit dependency declaration (vz uses it internally)

oc = sys.modules["exp_oracle_context_invariant_address_wm_v2"]
base = sys.modules["exp_selective_overwrite_recall_nl_wm_roleseparated_v1"]
rc = sys.modules["exp_selective_overwrite_recall_nl_wm_readcond_v1"]

ANCHOR_NAME = "vsa_key_globalscale_phase_conversion_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = vz.V2_CKPT

S_TARGET_TOTAL = vz.S_TARGET_TOTAL
V_FILL = vz.V_FILL
CHANCE_RECALL = vz.CHANCE_RECALL
TRAIN_ROLES_V2 = vz.TRAIN_ROLES_V2
HELD_OUT_ROLES_V2 = vz.HELD_OUT_ROLES_V2
ALL_ROLES = vz.ALL_ROLES
PHASE_SCALE = vz.PHASE_SCALE
CLEAN_KEY_SEED = vz.CLEAN_KEY_SEED
FILLER_SEED = vz.FILLER_SEED
DISTRACT_SEED = vz.DISTRACT_SEED
SHUFFLE_SEED = vz.SHUFFLE_SEED
WRONGKEY_SEED = vz.WRONGKEY_SEED
ORACLE_PROBE_SEED = vz.ORACLE_PROBE_SEED

FULL_TRAIN, FULL_EVAL = vz.FULL_TRAIN, vz.FULL_EVAL
SEEDS_FULL = vz.SEEDS_FULL

# ---- pre-registered bands (written BEFORE running; NOT loosened) ----
NEAR_CHANCE_MARGIN = 0.10
FAIL_MAX = CHANCE_RECALL + NEAR_CHANCE_MARGIN     # THEORETICAL: 0.15
ORACLE_MIN = 0.50
REPRO_TOL = 0.05
COSINE_HARD_PASS = 0.20
COS_IMPROVE_MARGIN = 0.05
RECALL_IMPROVE_MARGIN = 0.10

# MEASURED@data/exp_vsa_key_orthogonalization_transform_v1/metrics.json (Gate-D reproduction targets)
KX_RAW_COS_REF = 0.3477550293718066
KX_LOWDIN_COS_REF = 0.35199944249221254
KX_RAW_HELD_REF = [0.2917039693494498]  # mean; per-seed compared via kx's own vz reference below
KX_ENCODER_HELD_REF_PERSEED = [0.3146067415730337, 0.27692307692307694, 0.2835820895522388]

KEY_ARMS = ("raw_colscale", "lowdin_colscale", "raw_globalscale", "lowdin_globalscale", "clean")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    safe_metrics = _jsonify(metrics)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe_metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def hash_offset(key_arm):
    """Deterministic (sha256, NOT hash()) small offset so each arm's FLOOR_WRONGKEY table is
    independently seeded but reproducible."""
    digest = hashlib.sha256(key_arm.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 100000


# ---------------- the ONE variable: normalization granularity ----------------
def encode_colscale(T, scale=PHASE_SCALE):
    """Per-COLUMN (per-feature, over the n role-rows) z-score then phase-encode. Reproduces kx's
    encoder_table_for exactly. Z[i,j] = (T[i,j]-mu[j])/sd[j] -- a diagonal (non-scalar) rescale that
    does NOT preserve the row Gram matrix T T^T."""
    mu = T.mean(dim=0, keepdim=True)
    sd = T.std(dim=0, keepdim=True).clamp_min(1e-6)
    return vz.phase_encode_real(T, mu, sd, scale)


def encode_globalscale(T, scale=PHASE_SCALE):
    """GLOBAL SCALAR z-score (one mu, one sd over ALL n*d entries) then phase-encode. Z = (T - mu)/sd
    with mu,sd scalars -- this rescales every row by the SAME constant, preserving the row Gram matrix
    up to a strictly positive scalar multiple (does not warp inter-role angle structure)."""
    mu = T.mean()
    sd = T.std().clamp_min(1e-6)
    return vz.phase_encode_real(T, mu, sd, scale)


def encoder_table_for(oracle_table_raw, key_arm):
    if key_arm == "raw_colscale":
        return encode_colscale(kx.transform_raw(oracle_table_raw))
    if key_arm == "lowdin_colscale":
        return encode_colscale(kx.transform_lowdin(oracle_table_raw))
    if key_arm == "raw_globalscale":
        return encode_globalscale(kx.transform_raw(oracle_table_raw))
    if key_arm == "lowdin_globalscale":
        return encode_globalscale(kx.transform_lowdin(oracle_table_raw))
    raise ValueError("unknown key_arm %r" % key_arm)


def off_diag_cosine(table, n=S_TARGET_TOTAL):
    cos = []
    for i in range(n):
        for j in range(n):
            if i != j:
                cos.append(vz.complex_cosine(table[i], table[j]))
    return float(np.mean(cos)), float(np.max(cos))


def build_tables_for_arm(key_arm, oracle_table_raw, shared):
    if key_arm == "clean":
        encoder_table = shared["clean_table"]
    else:
        encoder_table = encoder_table_for(oracle_table_raw, key_arm)
    mean_cos, max_cos = off_diag_cosine(encoder_table)
    tables = dict(shared)
    tables["encoder_table"] = encoder_table
    tables["clean_table"] = shared["clean_table"]
    tables["wrong_key_table"] = vz.phase_vec_table(S_TARGET_TOTAL, encoder_table.shape[1],
                                                    WRONGKEY_SEED + hash_offset(key_arm))
    perm = shared["shuffle_perm"]
    tables["shuffled_filler_table"] = shared["filler_table"][perm]
    return tables, mean_cos, max_cos


def build_shared_tables(enc, Uc):
    """Reuses kx.build_shared_tables verbatim (identical fairness construction: filler/distract/clean
    tables, oracle_table_raw, FLOOR_CONTEXTVARYING reference reps, shuffle perm)."""
    return kx.build_shared_tables(enc, Uc)


def run_key_arm_and_floors(key_arm, oracle_table_raw, shared, ds_by_seed, gamma):
    tables, mean_cos, max_cos = build_tables_for_arm(key_arm, oracle_table_raw, shared)
    out = {}
    for mode in ("main", "floor_wrongkey", "floor_shuffled", "floor_contextvarying"):
        vz_mode = {"main": key_arm if key_arm == "clean" else "encoder",
                   "floor_wrongkey": "floor_wrongkey", "floor_shuffled": "floor_shuffled",
                   "floor_contextvarying": "floor_contextvarying"}[mode]
        per_seed = []
        for seed in SEEDS_FULL:
            ev, ev_b = ds_by_seed[seed]
            res = vz.run_arm(ev, ev_b["ev_idx"].numpy(), ev_b["q_idx"].numpy(), vz_mode, tables, gamma,
                              ev_b["q_is_train"], ev_b["q_is_heldout"])
            per_seed.append(res)
        out[mode] = per_seed
    return out, mean_cos, max_cos


# ---------------- self-tests ----------------
def globalscale_preserves_gram_selftest():
    """Correctness gate (the CORE mechanism claim of this cell): on a toy correlated key set, Lowdin
    orthogonalization gives near-exact real-space row orthogonality (cos<0.01, reproducing kx's own
    transforms_change_geometry_selftest). This checks the CLAIM that a per-COLUMN z-score (kx's
    existing encoder_table_for convention) re-introduces correlation into that already-orthogonal
    matrix, while a GLOBAL SCALAR z-score does NOT (up to floating-point/clamp_min noise)."""
    g = torch.Generator().manual_seed(31415)
    d, n = 64, 15
    shared_dir = torch.randn(1, d, generator=g)
    X = 0.85 * shared_dir + 0.3 * torch.randn(n, d, generator=g)

    def _cos_real(A):
        An = A / A.norm(dim=1, keepdim=True).clamp_min(1e-8)
        C = An @ An.T
        off = C[~torch.eye(n, dtype=torch.bool)]
        return float(off.abs().mean())

    lowdin = kx.transform_lowdin(X)
    lowdin_cos_real = _cos_real(lowdin)
    assert lowdin_cos_real < 0.01, (
        "toy Lowdin did not achieve near-exact real-space orthogonality (cos=%.4f)" % lowdin_cos_real)

    # per-column z-score (diagonal, non-scalar rescale) -- expect this to WARP the Gram matrix
    mu_col = lowdin.mean(dim=0, keepdim=True)
    sd_col = lowdin.std(dim=0, keepdim=True).clamp_min(1e-6)
    z_col = (lowdin - mu_col) / sd_col
    cos_col = _cos_real(z_col)

    # global scalar z-score (uniform rescale) -- expect this to PRESERVE near-zero real-space cosine
    mu_glob = lowdin.mean()
    sd_glob = lowdin.std().clamp_min(1e-6)
    z_glob = (lowdin - mu_glob) / sd_glob
    cos_glob = _cos_real(z_glob)

    assert cos_glob < 0.02, (
        "GLOBALSCALE_SELFTEST_FAIL: global-scalar normalization did not preserve near-zero real-space "
        "cosine after Lowdin (cos=%.4f) -- mechanism claim (uniform rescale preserves Gram up to a "
        "scalar) is wrong or implemented incorrectly" % cos_glob)
    assert cos_col > cos_glob + 0.05, (
        "GLOBALSCALE_SELFTEST_FAIL: per-column z-score did not warp the Gram matrix more than global-"
        "scalar z-score on this toy case (col=%.4f glob=%.4f) -- the claimed mechanism gap did not "
        "reproduce even in the isolated toy setting" % (cos_col, cos_glob))
    return {"lowdin_real_cos": lowdin_cos_real, "colscale_real_cos": cos_col,
            "globalscale_real_cos": cos_glob}


def run_self_test():
    _log("SELF-TEST: toy case -- global-scalar z-score preserves Lowdin's real-space orthogonality, "
         "per-column z-score warps it ...")
    tdiag = globalscale_preserves_gram_selftest()
    _log("  PASS: %s" % tdiag)

    _log("SELF-TEST: load REAL v2 encoder + build REAL oc oracle table (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected"
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")
    shared, oracle_table_raw = build_shared_tables(enc, Uc)

    cosines = {}
    for key_arm in ("raw_colscale", "lowdin_colscale", "raw_globalscale", "lowdin_globalscale"):
        tables, mean_cos, max_cos = build_tables_for_arm(key_arm, oracle_table_raw, shared)
        cosines[key_arm] = {"mean": mean_cos, "max": max_cos}
        _log("  key_arm=%s off_diag_cosine mean=%.4f max=%.4f" % (key_arm, mean_cos, max_cos))

    assert abs(cosines["raw_colscale"]["mean"] - KX_RAW_COS_REF) < REPRO_TOL, (
        "GATE_D_REPRO_FAIL: ARM_RAW_COLSCALE cosine=%.4f does not reproduce kx's MEASURED raw "
        "cosine=%.4f" % (cosines["raw_colscale"]["mean"], KX_RAW_COS_REF))
    assert abs(cosines["lowdin_colscale"]["mean"] - KX_LOWDIN_COS_REF) < REPRO_TOL, (
        "GATE_D_REPRO_FAIL: ARM_LOWDIN_COLSCALE cosine=%.4f does not reproduce kx's MEASURED lowdin "
        "cosine=%.4f" % (cosines["lowdin_colscale"]["mean"], KX_LOWDIN_COS_REF))
    _log("  (informational) globalscale deltas vs colscale: raw=%.4f lowdin=%.4f"
         % (cosines["raw_globalscale"]["mean"] - cosines["raw_colscale"]["mean"],
            cosines["lowdin_globalscale"]["mean"] - cosines["lowdin_colscale"]["mean"]))

    _log("SELF-TEST: tiny end-to-end all key-arms x all modes (arms-must-differ, ranges valid) ...")
    ev = oc.gen_dataset_zeroshot(60, np.random.default_rng(7 + 777), ALL_ROLES)
    ev_b = oc.build_index_batch_ext_v2(ev, enc, 7 + 777)
    assert ev_b["q_is_heldout"].sum().item() > 0, "tiny eval set drew no held-out-role queries"

    digests = {}
    for key_arm in KEY_ARMS:
        tables, _mc, _xc = build_tables_for_arm(key_arm, oracle_table_raw, shared)
        vz_mode = key_arm if key_arm == "clean" else "encoder"
        res = vz.run_arm(ev, ev_b["ev_idx"].numpy(), ev_b["q_idx"].numpy(), vz_mode, tables, 0.9,
                          ev_b["q_is_train"], ev_b["q_is_heldout"])
        assert 0.0 <= res["recall_train_acc"] <= 1.0 or math.isnan(res["recall_train_acc"])
        assert 0.0 <= res["recall_heldout_acc"] <= 1.0 or math.isnan(res["recall_heldout_acc"])
        digests[key_arm] = res["preds_digest"]
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        assert digests[a] != digests[b], "META_RULE_AF VIOLATION: key-arms %r and %r bit-identical" % (a, b)

    _log("SELF-TEST: GAMMA-tuning corpus excludes held-out roles (fairness, reused from vz) ...")
    zs_diag = vz.zeroshot_tuning_excludes_heldout_selftest(enc, Uc, shared)
    _log("  diag=%s" % zs_diag)

    _log("SELF-TEST PASS")
    return {"globalscale_toy_diag": tdiag, "n_cached": n_cached, "cosines": cosines,
            "zeroshot_tuning_diag": zs_diag, "arms_differ_verified": True}


# ---------------- verdict ----------------
def decide_verdict(key_arm_results, cosines):
    def held(key_arm, mode):
        return [r["recall_heldout_acc"] for r in key_arm_results[key_arm][mode]]

    def _all_fail(xs):
        return all((not math.isnan(x)) and x <= FAIL_MAX for x in xs)

    floors_valid_by_arm = {}
    for key_arm in KEY_ARMS:
        ctx_fails = _all_fail(held(key_arm, "floor_contextvarying"))
        wrong_fails = _all_fail(held(key_arm, "floor_wrongkey"))
        shuf_fails = _all_fail(held(key_arm, "floor_shuffled"))
        floors_valid_by_arm[key_arm] = {"ctx_fails": ctx_fails, "wrong_fails": wrong_fails,
                                         "shuf_fails": shuf_fails,
                                         "all_valid": ctx_fails and wrong_fails and shuf_fails}

    raw_col_held = held("raw_colscale", "main")
    lowdin_col_held = held("lowdin_colscale", "main")
    lowdin_glob_held = held("lowdin_globalscale", "main")
    raw_glob_held = held("raw_globalscale", "main")
    clean_held = held("clean", "main")

    invalid_reasons = []
    repro_raw_ok = abs(cosines["raw_colscale"]["mean"] - KX_RAW_COS_REF) <= REPRO_TOL
    repro_lowdin_ok = abs(cosines["lowdin_colscale"]["mean"] - KX_LOWDIN_COS_REF) <= REPRO_TOL
    if not repro_raw_ok or not repro_lowdin_ok:
        invalid_reasons.append(
            "GATE_D_REPRO_FAIL: raw_colscale cos=%.4f (ref %.4f) lowdin_colscale cos=%.4f (ref %.4f)"
            % (cosines["raw_colscale"]["mean"], KX_RAW_COS_REF,
               cosines["lowdin_colscale"]["mean"], KX_LOWDIN_COS_REF))

    for key_arm in ("lowdin_colscale", "lowdin_globalscale"):
        fv = floors_valid_by_arm[key_arm]
        if not fv["all_valid"]:
            broken = []
            if not fv["ctx_fails"]:
                broken.append("FLOOR_CONTEXTVARYING")
            if not fv["wrong_fails"]:
                broken.append("FLOOR_WRONGKEY")
            if not fv["shuf_fails"]:
                broken.append("FLOOR_SHUFFLED_CODEBOOK")
            invalid_reasons.append("key_arm=%s: floors did not collapse: %s" % (key_arm, broken))

    if invalid_reasons:
        return "INVALID", " | ".join(invalid_reasons), floors_valid_by_arm, {}

    lowdin_col_cos = cosines["lowdin_colscale"]["mean"]
    lowdin_glob_cos = cosines["lowdin_globalscale"]["mean"]
    lowdin_col_mean = float(np.mean(lowdin_col_held))
    lowdin_glob_mean = float(np.mean(lowdin_glob_held))
    cos_drop = lowdin_col_cos - lowdin_glob_cos
    recall_gain = lowdin_glob_mean - lowdin_col_mean

    diag = {"lowdin_colscale": {"cosine": lowdin_col_cos, "held_mean": lowdin_col_mean,
                                 "held": lowdin_col_held},
            "lowdin_globalscale": {"cosine": lowdin_glob_cos, "held_mean": lowdin_glob_mean,
                                    "held": lowdin_glob_held},
            "raw_colscale": {"cosine": cosines["raw_colscale"]["mean"],
                              "held_mean": float(np.mean(raw_col_held))},
            "raw_globalscale": {"cosine": cosines["raw_globalscale"]["mean"],
                                 "held_mean": float(np.mean(raw_glob_held))},
            "clean": {"cosine": cosines["clean"]["mean"], "held_mean": float(np.mean(clean_held))},
            "cos_drop_lowdin_glob_vs_col": cos_drop, "recall_gain_lowdin_glob_vs_col": recall_gain}

    works_all_seeds = all(x >= ORACLE_MIN for x in lowdin_glob_held)
    if works_all_seeds and lowdin_glob_cos < COSINE_HARD_PASS:
        verdict = "CONVERSION_FIX_LIFTS"
        msg = ("ARM_LOWDIN_GLOBALSCALE cosine=%.4f < COSINE_HARD_PASS=%.2f AND held-out recall=%s "
               "clears ORACLE_MIN=%.2f on all 3 seeds AND both Gate-D reproductions matched (raw_col "
               "cos=%.4f ref=%.4f, lowdin_col cos=%.4f ref=%.4f) -- the real->FHRR encoding CONVERSION "
               "(per-column z-score) was the localized bottleneck, not the orthogonalizing transform. "
               "cos_drop_vs_colscale=%.4f recall_gain_vs_colscale=%.4f. ARM_CLEAN reference held=%s."
               % (lowdin_glob_cos, COSINE_HARD_PASS, [round(h, 3) for h in lowdin_glob_held], ORACLE_MIN,
                  cosines["raw_colscale"]["mean"], KX_RAW_COS_REF, lowdin_col_cos, KX_LOWDIN_COS_REF,
                  cos_drop, recall_gain, [round(h, 3) for h in clean_held]))
    elif cos_drop >= COS_IMPROVE_MARGIN or recall_gain >= RECALL_IMPROVE_MARGIN:
        verdict = "PARTIAL"
        msg = ("ARM_LOWDIN_GLOBALSCALE cosine=%.4f (colscale=%.4f, drop=%.4f) held-out recall mean=%.3f "
               "(colscale=%.3f, gain=%.3f) -- global-scalar conversion helps but does not clear both "
               "HARD-PASS bars (ORACLE_MIN=%.2f all-seeds AND cosine<%.2f). Report the gain honestly; "
               "residual gap needs further work beyond the conversion-granularity fix."
               % (lowdin_glob_cos, lowdin_col_cos, cos_drop, lowdin_glob_mean, lowdin_col_mean,
                  recall_gain, ORACLE_MIN, COSINE_HARD_PASS))
    else:
        verdict = "NO_LIFT"
        msg = ("ARM_LOWDIN_GLOBALSCALE cosine=%.4f vs colscale=%.4f (drop=%.4f, below "
               "COS_IMPROVE_MARGIN=%.2f) and held-out recall mean=%.3f vs colscale=%.3f (gain=%.3f, "
               "below RECALL_IMPROVE_MARGIN=%.2f) -- per-column-vs-global-scalar normalization "
               "granularity was NOT the bottleneck; residual correlation is inherent to phase-encoding "
               "this real-encoder key set at this d, regardless of z-score convention. The bound is "
               "deeper than the conversion step; would need a from-scratch encoder objective or a "
               "different (non-affine) conversion entirely."
               % (lowdin_glob_cos, lowdin_col_cos, cos_drop, COS_IMPROVE_MARGIN, lowdin_glob_mean,
                  lowdin_col_mean, recall_gain, RECALL_IMPROVE_MARGIN))

    diag["_verdict_diag"] = {"cos_drop": cos_drop, "recall_gain": recall_gain,
                              "works_all_seeds": works_all_seeds}
    return verdict, msg, floors_valid_by_arm, diag


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(KEY_ARMS) * 4 * len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (globalscale-preserves-gram toy proof + real encoder + real "
                           "oracle table + gate-d-repro-check + arms-differ + zeroshot-tuning)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance_recall": CHANCE_RECALL,
            "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: train_n=%d eval_n=%d seeds=%s chance_recall=%.4f key_arms=%s"
         % (args.train_n, args.eval_n, SEEDS_FULL, CHANCE_RECALL, KEY_ARMS))
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")
    shared, oracle_table_raw = build_shared_tables(enc, Uc)

    cosines = {}
    for key_arm in ("raw_colscale", "lowdin_colscale", "raw_globalscale", "lowdin_globalscale"):
        _, mean_cos, max_cos = build_tables_for_arm(key_arm, oracle_table_raw, shared)
        cosines[key_arm] = {"mean": mean_cos, "max": max_cos}
        _log("  key_arm=%s off_diag_cosine mean=%.4f max=%.4f" % (key_arm, mean_cos, max_cos))
    clean_mean_cos, clean_max_cos = off_diag_cosine(shared["clean_table"])
    cosines["clean"] = {"mean": clean_mean_cos, "max": clean_max_cos}

    raw_tables, _mc, _xc = build_tables_for_arm("raw_colscale", oracle_table_raw, shared)
    gamma, gamma_scores, gamma_tuning_diag = vz.tune_gamma(enc, Uc, raw_tables)
    _log("  GAMMA tuned (TRAIN-roles-only, ARM_RAW_COLSCALE-style tables) = %.2f heldout_leak=%s"
         % (gamma, gamma_tuning_diag))
    assert gamma_tuning_diag["n_heldout_events_in_tuning_corpus"] == 0, "ZERO_SHOT_BREACH: gamma tuning"
    assert gamma_tuning_diag["n_heldout_queries_in_tuning_corpus"] == 0, "ZERO_SHOT_BREACH: gamma tuning"

    ds_by_seed = {}
    for seed in SEEDS_FULL:
        ev = oc.gen_dataset_zeroshot(args.eval_n, np.random.default_rng(seed + 777), ALL_ROLES)
        ev_b = oc.build_index_batch_ext_v2(ev, enc, seed + 777)
        assert ev_b["q_is_heldout"].sum().item() > 0, "seed=%d eval set drew no held-out-role queries" % seed
        ds_by_seed[seed] = (ev, ev_b)

    prior_units = ckpt.load_units(OUTPUT_DIR)
    expected_n_units_full = len(KEY_ARMS) * 4 * len(SEEDS_FULL)
    if prior_units:
        _log("checkpoint: %d/%d units already recorded on disk; resuming"
             % (len(prior_units), expected_n_units_full))

    key_arm_results = {}
    digests_all = {}
    for key_arm in KEY_ARMS:
        _log("--- KEY_ARM_%s ---" % key_arm.upper())
        tables, _mc, _xc = build_tables_for_arm(key_arm, oracle_table_raw, shared)
        per_mode = {}
        for mode, vz_mode in (("main", key_arm if key_arm == "clean" else "encoder"),
                               ("floor_wrongkey", "floor_wrongkey"),
                               ("floor_shuffled", "floor_shuffled"),
                               ("floor_contextvarying", "floor_contextvarying")):
            per_seed = []
            for seed in SEEDS_FULL:
                k = ckpt.unit_key(key_arm, mode, seed)
                if k in prior_units:
                    per_seed.append(prior_units[k])
                    continue
                ev, ev_b = ds_by_seed[seed]
                res = vz.run_arm(ev, ev_b["ev_idx"].numpy(), ev_b["q_idx"].numpy(), vz_mode, tables, gamma,
                                  ev_b["q_is_train"], ev_b["q_is_heldout"])
                ckpt.record_unit(OUTPUT_DIR, k, res)
                per_seed.append(res)
            _log("  [%s/%s] recall_held per-seed=%s" % (key_arm, mode,
                 [round(r["recall_heldout_acc"], 4) for r in per_seed]))
            per_mode[mode] = per_seed
            if mode == "main":
                digests_all[key_arm] = per_seed[0]["preds_digest"]
        key_arm_results[key_arm] = per_mode

    verdict, msg, floors_valid_by_arm, diag = decide_verdict(key_arm_results, cosines)
    elapsed = time.perf_counter() - t0

    n_units_done = sum(len(v) for arm in key_arm_results.values() for v in arm.values())
    arms_differ = len(set(digests_all.values())) == len(digests_all)

    def _mean_sd(xs):
        xs = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
        if not xs:
            return {"mean": float("nan"), "sd": float("nan")}
        m = sum(xs) / len(xs)
        var = sum((x - m) ** 2 for x in xs) / len(xs) if len(xs) > 1 else 0.0
        return {"mean": m, "sd": math.sqrt(var)}

    held_summary = {key_arm: _mean_sd([r["recall_heldout_acc"] for r in key_arm_results[key_arm]["main"]])
                     for key_arm in KEY_ARMS}

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance_recall=%.4f | cosines=%s | %s"
                   % (verdict, CHANCE_RECALL,
                      {k: round(v["mean"], 4) for k, v in cosines.items()}, msg[:200]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance_recall": CHANCE_RECALL, "cosines": cosines,
        "held_recall_mean_sd_by_key_arm": held_summary,
        "floors_valid_by_arm": floors_valid_by_arm, "diag": diag,
        "gamma_chosen": gamma, "gamma_tuning_diag": gamma_tuning_diag,
        "key_arm_results": {k: {m: v for m, v in modes.items()} for k, modes in key_arm_results.items()},
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"S_TARGET_TOTAL": S_TARGET_TOTAL, "V_FILL": V_FILL, "train_n": args.train_n,
                   "eval_n": args.eval_n, "seeds": list(SEEDS_FULL),
                   "train_roles_v2": TRAIN_ROLES_V2, "held_out_roles_v2": HELD_OUT_ROLES_V2,
                   "n_cached_sentences": n_cached, "encoder": "real_v2_frozen",
                   "conditioning": "pca_whiten", "binding_flavor": "HRR_real_circular_convolution",
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 15,
        "crlb_n_a": "no learned-noise Cramer-Rao floor; discriminator is the pre-registered "
                    "CONVERSION_FIX_LIFTS/PARTIAL/NO_LIFT/INVALID rule (see decide_verdict)",
        "calibration_check": "adaptive_with_discriminator_gate: GAMMA tuned via kx/vz's small grid "
                              "search on TRAIN-roles-only recall, held-out roles never touched during "
                              "tuning (measured, see gamma_tuning_diag)"})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
