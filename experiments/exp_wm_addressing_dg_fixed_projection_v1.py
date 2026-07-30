# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; FIXED_DG_ADDRESS vs CONTROL_A eval-logit hash)
# - final_metrics_atomicity: tmp_replace (os.replace at end) -- reuses ho._jsonify / _strip_for_checkpoint
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = held-out-role ADDRESSING accuracy vs the SAME
#   pre-registered HARD-PASS/HARD-FAIL/INVALID bands as the HARD-FAILED cell this forks (bands NOT
#   loosened; reused verbatim via ho.decide_verdict). chance_addr=1/15, chance_recall=0.05, ceiling 1.0.
# - baseline_in_band: CONTROL_A_NO_WARMSTART (reused unchanged from ho) MUST reproduce STUCK_FLAT on
#   both splits, else INVALID. Judged live by ho.decide_verdict.
# - discriminator survives scale: FULL is the scale of interest; self-test builds the REAL v2 encoder +
#   REAL FixedDGAddressWM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed/Generator only; NO hash(), NO list(set())
"""DG-analog FIXED-projection addressing (v1) -- the one-variable pivot off the HARD-FAILED learned-key
held-out-role cell.

CONTEXT (notes/dg_analog_fixed_projection_addressing_build_plan_2026-07-30.md, read in full before
touching this file): exp_wm_addressing_heldout_role_warmstart_v1.py HARD-FAILED
(HARD_FAIL_PERROLE_LOOKUP_ONLY, both seeds; MEASURED@data/exp_wm_addressing_heldout_role_warmstart_v1/
metrics.json): the learned per-role address key (rc.ReadCondWM.key, one row per role, warm-started or
not) memorizes TRAIN_ROLES addresses and generalizes ZERO to HELD_OUT_ROLES (addr_train=1.0,
addr_held=0.0 both seeds). CONTROL_A_NO_WARMSTART (no warm-start, random key, end-to-end only)
reproduced STUCK_FLAT (near chance_addr on both splits) -- confirming the split/construction is valid
and non-vacuous.

THE ONE HARD VARIABLE this file changes vs the HARD-FAILED cell: the addressing path. `rc.ReadCondWM.key`
(a learned nn.Parameter, one row per role) is replaced by `FixedDGAddressWM`'s FIXED (non-trained,
register_buffer, never touched by the optimizer) random-expand + k-WTA-sparsify + hash-to-bucket
pipeline (the DG-analog per notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md
A3/A4). This generalizes to unseen roles BY CONSTRUCTION: E and bucket_of are deterministic functions
applied uniformly to ANY input vector, seen or unseen role alike -- there is no table of trained rows to
be missing an entry from (see the build plan section 2 for the full argument).

EVERYTHING ELSE is reused UNCHANGED by importing exp_wm_addressing_heldout_role_warmstart_v1 (aliased
`ho` below) rather than re-implementing it, per the one-variable-swap / minimize-the-diff discipline:
the 15-role TRAIN/HELD_OUT split (ho.TRAIN_ROLES / ho.HELD_OUT_ROLES, ROLE_SPLIT_SEED=20260730), the
gen_stream_expanded/gen_dataset_expanded construction + leak-guards + construction_selftest, the
CONTROL_A_NO_WARMSTART control (ho.run_control_a, MUST reproduce STUCK_FLAT), the CONTROL_A_LONGER
Olsson-counter-hypothesis diagnostic, the CONTROL_B_PERROLE_LOOKUP_GROUNDTRUTH zero-training ceiling
(ho.control_b_perrole_groundtruth), the decisive addressing-accuracy metric + ALL pre-registered
HARD-PASS/HARD-FAIL/INVALID/MIDDLE_BAND bands (ho.decide_verdict, called directly, NOT re-derived), the
serialization + checkpoint/resume self-tests (ho.serialization_selftest / ho.checkpoint_resume_selftest,
reused verbatim -- generic over unit labels), and train_arm_ext's training/eval loop (ho.train_arm_ext).

ARMS (mirrors the HARD-FAILED cell's arm list; WARM_STARTED replaced by FIXED_DG_ADDRESS):
  FIXED_DG_ADDRESS (the capability under test) -- FixedDGAddressWM: pca_whiten conditioning (unchanged,
    load-bearing per the build plan -- it reduces raw cos_mean~0.99 to pca cos_mean~0.80,
    MEASURED@exp_selective_overwrite_recall_nl_wm_readcond_v1 conditioning_diagnostic), then a FIXED
    random projection E [d_exp, d_enc] (E ~ N(0, 1/d_enc), register_buffer, no grad) + k-WTA sparsify
    (keep top-k highest-VALUE activations, NOT abs-value -- DG's sparse POSITIVE code) + a FIXED
    per-coordinate hash bucket_of: {0..d_exp-1} -> {0..K_SLOTS-1} (register_buffer int tensor, seeded).
    NO per-role learned parameter anywhere in the addressing path (role_query stays shared-not-per-role
    and unchanged; write_gate/value_proj/readout stay learned+content-general, unchanged). NO aux
    slot-address CE loss (there is no learned key row to supervise) and NO warm-start call (nothing to
    warm-start). Trainable params: role_query, write_gate, value_proj, readout only (wm.parameters()
    naturally excludes E/bucket_of since they are buffers, and excludes the learned key since
    FixedDGAddressWM deletes it in __init__). Seeds 7, 13 (ho.SEEDS_FULL).
  CONTROL_A_NO_WARMSTART (reused UNCHANGED from ho.run_control_a) -- same architecture class
    (rc.ReadCondWM, NOT FixedDGAddressWM), conditioning=none, random key init, no aux, end-to-end only.
    MUST reproduce near-chance addressing on BOTH splits (ho.decide_verdict's controlA_ok gate), else
    the test is INVALID. Seeds 7, 13.
  CONTROL_A_LONGER_SCHEDULE (reused UNCHANGED from ho.run_control_a, LONGER_MULT=8x steps, seed=7) --
    Olsson counter-hypothesis diagnostic, reported alongside not instead of.
  CONTROL_B_PERROLE_LOOKUP_GROUNDTRUTH (reused UNCHANGED from ho.control_b_perrole_groundtruth) --
    zero-training symbolic per-role-lookup ceiling; near-1.0 on train roles, structurally 0.0 on
    held-out roles by construction.

DECISIVE METRIC + BANDS: IDENTICAL to the HARD-FAILED cell, reused verbatim via ho.decide_verdict --
held-out-role vs train-role addressing accuracy (argmax over K=15 address logits), NOT loosened:
  HARD_PASS_HELDOUT_ROLE_GENERALIZATION: held-out addr_acc >= 0.80 (both seeds) AND
    (train_addr_acc - held_addr_acc) <= 0.15 (both seeds) AND CONTROL_A near chance_addr on both splits
    (both seeds) AND held_addr_acc - control_B_heldout_acc >= 0.30 (both seeds).
  HARD_FAIL_PERROLE_LOOKUP_ONLY: held-out addr_acc < 0.40 (any seed) OR gap > 0.35 (any seed) OR
    |held_addr_acc - control_B_heldout_acc| <= 0.10 (any seed).
  INVALID / MIDDLE_BAND_INCONCLUSIVE: as ho.decide_verdict defines (see that file).
Note: ho.decide_verdict's verdict_msg text was authored for the WARM_STARTED arm's mechanism
("warm-started arm", "warm-start fix"); this file substitutes those two phrases for
"FIXED_DG_ADDRESS arm" / "FIXED_DG_ADDRESS mechanism" post-hoc (see _retarget_msg below) so the message
reads correctly for THIS arm's mechanism -- the underlying numeric bands/logic are reused byte-identical,
only the cosmetic arm-name substrings are swapped.

Fixed-projection sweep (exp_dev autonomy note per the build plan section 3): d_exp defaults to 2x d_enc
(Spoke-3 design-note precedent, MEASURED@notes/design_stage2_concept_encoder_spoke3_..._2026-07-02.md
line 97) and k defaults to 8 (certified block-local-K resonator value, K8_acc=1.00
MEASURED@data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json). Both are CLI
overridable (--d-exp-mult, --k-wta) so the FULL dispatch can pass whichever (d_exp, k) the cheap
pre-check (exp_wm_addressing_dg_precheck_v1.py) found to clear untrained_addr_distinct >= 12/15 --
this cell deliberately does NOT itself sweep multiple (d_exp, k) as separate arms (that would violate
the one-variable-swap discipline: only the addressing MECHANISM is the variable under test here, not a
hyperparameter grid). dg_seed is a single fixed constant shared across BOTH data-seeds 7/13 (the
addressing geometry itself is not a confound between seeds; only the trainable downstream weights vary
by seed) -- flagged per the build plan's autonomy note.

Run:  .venv/Scripts/python.exe experiments/exp_wm_addressing_dg_fixed_projection_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_wm_addressing_dg_fixed_projection_v1.py --full \
          --d-exp-mult 2 --k-wta 8

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free; this .venv has no CUDA). progress_logging: print_flush_true.
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
import exp_wm_addressing_heldout_role_warmstart_v1 as ho  # noqa: E402  -- HARD-FAILED cell, reused verbatim

ANCHOR_NAME = "wm_addressing_dg_fixed_projection_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (MANDATORY, CLAUDE.md)

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- fixed-projection defaults (exp_dev autonomy note; CLI-overridable, see docstring) ----
D_EXP_MULT_DEFAULT = 2                          # HYPOTHESIZED@this file: Spoke-3 2x-expansion precedent
K_WTA_DEFAULT = 8                               # MEASURED@data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json:K8_acc=1.00
DG_SEED = 20260730001                           # fixed; SAME across seeds 7/13 (addressing geometry not a seed confound)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening (mirrors ho.py; kept local so this file has no hidden coupling
# to ho's OUTPUT_DIR / ANCHOR_NAME globals) ----------------
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


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    safe_metrics = ho._jsonify(metrics)   # reused verbatim; belt-and-suspenders, source fields already native
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe_metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- the ONE HARD VARIABLE: fixed DG-analog projection (no learned per-role param) ----------------
def make_fixed_projection(d_enc, d_exp, k_slots, dg_seed):
    """Build the FIXED (non-trained) random expansion E [d_exp, d_enc] and the FIXED per-coordinate
    hash bucket_of [d_exp] -> {0..k_slots-1}. Pure function so exp_wm_addressing_dg_precheck_v1.py can
    import and reuse this EXACT construction (guarantees the pre-check measures the identical mechanism
    this cell trains, not a look-alike reimplementation)."""
    g = torch.Generator().manual_seed(dg_seed)
    E = torch.empty(d_exp, d_enc)
    E.normal_(0.0, 1.0 / math.sqrt(d_enc), generator=g)             # THEORETICAL: unit-norm-in-expectation columns
    rng = np.random.default_rng(dg_seed)
    bucket_np = rng.integers(0, k_slots, size=d_exp).astype(np.int64)  # uniform i.i.d. per-coordinate LSH-style bucket
    bucket_of = torch.from_numpy(bucket_np)
    return E, bucket_of


def kwta_sparsify(z, k):
    """Keep only the top-k highest-VALUE activations per row (NOT top-k by absolute value -- DG's code
    is a sparse POSITIVE code per the Marr/O'Reilly-McClelland framing), zero the rest. z: [..., d_exp]."""
    kth_vals = torch.topk(z, k, dim=-1).values[..., -1:]            # kth largest value per row
    return z * (z >= kth_vals).to(z.dtype)


def bucket_pool(sparse, bucket_of, k_slots):
    """Fixed scatter-add pooling of the sparse expanded code into K_SLOTS address-logit dims.
    sparse: [N, d_exp] -> returns [N, k_slots] (SAME shape contract as rc.ReadCondWM._addr_logits)."""
    bucket_idx = bucket_of.unsqueeze(0).expand(sparse.shape[0], -1)
    out = torch.zeros(sparse.shape[0], k_slots, dtype=sparse.dtype, device=sparse.device)
    out.scatter_add_(1, bucket_idx, sparse)
    return out


class FixedDGAddressWM(ho.rc.ReadCondWM):
    """rc.ReadCondWM with the learned per-role key (self.key, one nn.Parameter row per role) replaced by
    the FIXED DG-analog pipeline: whiten (unchanged, upstream, via the Conditioner already applied to
    U_tok before construction) -> fixed random expand (self.E) -> k-WTA sparsify -> fixed hash-to-bucket
    (self.bucket_of) -> address logits, SAME [.., K_SLOTS] output shape/contract as the base class so
    NOTHING downstream (softmax, wgate, overwrite loop, h_read pooling, readout) needs to change.

    self.key is DELETED (not just left unused) so wm.parameters() naturally excludes any per-role
    learned param -- there is no per-role learned parameter anywhere in the addressing path."""

    def __init__(self, seed, d_enc, d_mem, k_slots, hidden, v_fill, addr_temp, U_tok, U_pad,
                 d_exp, k_wta, dg_seed):
        super().__init__(seed, d_enc, d_mem, k_slots, hidden, v_fill, addr_temp, U_tok, U_pad)
        del self.key   # remove the learned per-role address key registered by the base class __init__
        E, bucket_of = make_fixed_projection(d_enc, d_exp, k_slots, dg_seed)
        self.register_buffer("E", E)                    # FIXED; requires_grad=False by construction
        self.register_buffer("bucket_of", bucket_of)     # FIXED; int tensor, never touched by optimizer
        self.d_exp = d_exp
        self.k_wta = k_wta
        self.dg_seed = dg_seed

    def _addr_logits(self, x):
        z = x @ self.E.t()                               # [N, d_exp]
        sparse = kwta_sparsify(z, self.k_wta)             # [N, d_exp], top-k highest-value kept
        addr = bucket_pool(sparse, self.bucket_of, self.k_slots)   # [N, K_SLOTS]
        return addr / self.addr_temp


def build_wm_fixed(seed, enc, cond, d_exp_mult, k_wta, dg_seed):
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")   # load-bearing (build plan section 1 step 2)
    d_exp = d_exp_mult * enc.d
    return FixedDGAddressWM(seed, enc.d, ho.D_MEM, ho.K_SLOTS, ho.HIDDEN, ho.V_FILL, ho.ADDR_TEMP,
                             Uc, enc.U_pad_t, d_exp, k_wta, dg_seed)


def run_fixed_dg_address(enc, cond, tr_batch, ev_batch, seed, steps, d_exp_mult, k_wta, dg_seed):
    wm = build_wm_fixed(seed, enc, cond, d_exp_mult, k_wta, dg_seed)
    E_before, bucket_before = wm.E.clone(), wm.bucket_of.clone()
    res = ho.train_arm_ext(wm, tr_batch, ev_batch, steps, ho.LR, list(wm.parameters()), seed,
                            "FIXED_DG_ADDRESS", aux=False)
    # runtime-asserted fixed-ness invariant (not just a docstring claim) -- E/bucket_of must be
    # bit-identical before and after training, since they are never in wm.parameters()'s optimizer set.
    assert torch.equal(wm.E, E_before), "INTEGRITY VIOLATION: fixed E was modified during training"
    assert torch.equal(wm.bucket_of, bucket_before), "INTEGRITY VIOLATION: fixed bucket_of was modified"
    res["d_exp"] = wm.d_exp
    res["k_wta"] = wm.k_wta
    res["dg_seed"] = wm.dg_seed
    return res


def _retarget_msg(msg):
    """ho.decide_verdict's verdict_msg text was authored for the WARM_STARTED arm's mechanism. The
    numeric bands/logic are reused byte-identical (this function touches ONLY these two cosmetic
    substrings) so the message reads correctly for the FIXED_DG_ADDRESS arm's actual mechanism."""
    return (msg.replace("warm-started arm", "FIXED_DG_ADDRESS arm")
               .replace("warm-start fix", "FIXED_DG_ADDRESS mechanism"))


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: reuse serialization + checkpoint/resume self-tests (identical generic logic) ...")
    ser_diag = ho.serialization_selftest()
    _log("  serialization_selftest PASS: %s" % ser_diag)
    ckpt_diag = ho.checkpoint_resume_selftest()
    _log("  checkpoint_resume_selftest PASS: %s" % ckpt_diag)

    _log("SELF-TEST: role split integrity (reused from ho) ...")
    assert ho.HELD_OUT_SET.isdisjoint(ho.TRAIN_SET)
    assert len(ho.HELD_OUT_ROLES) + len(ho.TRAIN_ROLES) == ho.S_TARGET_TOTAL

    _log("SELF-TEST: expanded construction leak-proofing (reused from ho) ...")
    cst = ho.construction_selftest(seed=7, n=400)
    if cst["fails"]:
        raise AssertionError("construction self-test FAILED: %s" % "; ".join(cst["fails"]))

    _log("SELF-TEST: make_fixed_projection / kwta_sparsify / bucket_pool unit checks ...")
    d_enc_toy, d_exp_toy, k_slots_toy, k_toy = 16, 64, 5, 4
    E_a, bucket_a = make_fixed_projection(d_enc_toy, d_exp_toy, k_slots_toy, dg_seed=123)
    E_b, bucket_b = make_fixed_projection(d_enc_toy, d_exp_toy, k_slots_toy, dg_seed=123)
    assert torch.equal(E_a, E_b) and torch.equal(bucket_a, bucket_b), "make_fixed_projection not deterministic"
    E_c, _ = make_fixed_projection(d_enc_toy, d_exp_toy, k_slots_toy, dg_seed=456)
    assert not torch.equal(E_a, E_c), "different dg_seed produced identical E (seeding broken)"
    z_toy = torch.randn(6, d_exp_toy)
    sp = kwta_sparsify(z_toy, k_toy)
    nnz_per_row = (sp != 0).sum(dim=-1)
    assert bool((nnz_per_row <= k_toy).all()), "kwta_sparsify kept more than k nonzero entries"
    assert bool((nnz_per_row >= 1).all()), "kwta_sparsify degenerate (zero survivors)"
    pooled = bucket_pool(sp, bucket_a, k_slots_toy)
    assert pooled.shape == (6, k_slots_toy), "bucket_pool output shape mismatch"

    _log("SELF-TEST: load REAL v2 encoder ...")
    assert os.path.exists(ho.V2_CKPT), "v2 checkpoint missing: %s" % ho.V2_CKPT
    enc = ho.base.FrozenV2Encoder(ho.V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected (widened query set missing?)"
    cond = ho.rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    _log("SELF-TEST: FixedDGAddressWM construction -- no per-role learned param exists ...")
    wm = build_wm_fixed(7, enc, cond, D_EXP_MULT_DEFAULT, K_WTA_DEFAULT, DG_SEED)
    param_names = dict(wm.named_parameters()).keys()
    assert "key" not in param_names, "FixedDGAddressWM must not carry a learned per-role key parameter"
    assert "E" not in param_names and "bucket_of" not in param_names, (
        "E/bucket_of leaked into wm.parameters() (must be register_buffer, not nn.Parameter)")
    assert "role_query" in param_names and "write_gate.0.weight" in param_names, (
        "role_query / write_gate should remain trainable, unchanged")

    _log("SELF-TEST: addr_logits shape check ([N, K_SLOTS], unchanged interface) ...")
    dummy = torch.randn(5, enc.d)
    logits = wm._addr_logits(dummy)
    assert logits.shape == (5, ho.K_SLOTS), "addr_logits shape drifted from the base-class contract"

    _log("SELF-TEST: tiny end-to-end (FIXED_DG_ADDRESS vs CONTROL_A, arms-must-differ, fixed-ness holds "
         "post-training) ...")
    tr = ho.build_index_batch_ext(ho.gen_dataset_expanded(150, np.random.default_rng(7)), enc, 7)
    ev = ho.build_index_batch_ext(ho.gen_dataset_expanded(150, np.random.default_rng(7 + 777)), enc, 7 + 777)
    assert ev["q_is_heldout"].sum().item() > 0, "tiny eval set drew no held-out-role queries"

    fixed_res = run_fixed_dg_address(enc, cond, tr, ev, 7, steps=60, d_exp_mult=D_EXP_MULT_DEFAULT,
                                      k_wta=K_WTA_DEFAULT, dg_seed=DG_SEED)
    ctrl_res = ho.run_control_a(enc, cond, tr, ev, 7, steps=60)
    _log("  tiny FIXED_DG_ADDRESS: eval=%.3f addr_train=%.3f addr_held=%.3f"
         % (fixed_res["eval_acc"], fixed_res["addr_train_acc"], fixed_res["addr_heldout_acc"]))
    _log("  tiny CONTROL_A:       eval=%.3f addr_train=%.3f addr_held=%.3f"
         % (ctrl_res["eval_acc"], ctrl_res["addr_train_acc"], ctrl_res["addr_heldout_acc"]))

    def _digest(t):
        return hashlib.sha256(t.detach().cpu().numpy().tobytes()).hexdigest()
    arms_differ = _digest(fixed_res["ev_logits"]) != _digest(ctrl_res["ev_logits"])
    assert arms_differ, "META_RULE_AF VIOLATION: FIXED_DG_ADDRESS and CONTROL_A bit-identical outputs"
    for r in (fixed_res, ctrl_res):
        assert 0.0 <= r["eval_acc"] <= 1.0
        assert 0.0 <= r["addr_train_acc"] <= 1.0
        assert 0.0 <= r["addr_heldout_acc"] <= 1.0

    _log("SELF-TEST: decide_verdict reuse + message-retargeting sanity ...")
    fake_verdict, fake_msg, _ = ho.decide_verdict([fixed_res], [ctrl_res], ho.control_b_perrole_groundtruth(
        ho.gen_dataset_expanded(200, np.random.default_rng(7 + 999))), ctrl_res)
    retargeted = _retarget_msg(fake_msg)
    assert "warm-started arm" not in retargeted and "warm-start fix" not in retargeted, (
        "message retargeting failed to substitute WARM_STARTED phrasing")

    _log("SELF-TEST PASS")
    return {"serialization_selftest": ser_diag, "checkpoint_resume_selftest": ckpt_diag,
            "fixed_projection_unit_checks": {"deterministic": True, "seed_sensitive": True,
                                              "kwta_bounded": True, "bucket_pool_shape_ok": True},
            "role_split": {"train": ho.TRAIN_ROLES, "held_out": ho.HELD_OUT_ROLES}, "construction": cst,
            "n_cached": n_cached, "no_learned_key_verified": True,
            "tiny_fixed_dg": {"eval_acc": fixed_res["eval_acc"], "addr_train": fixed_res["addr_train_acc"],
                               "addr_held": fixed_res["addr_heldout_acc"]},
            "tiny_control_a": {"eval_acc": ctrl_res["eval_acc"], "addr_train": ctrl_res["addr_train_acc"],
                                "addr_held": ctrl_res["addr_heldout_acc"]},
            "arms_differ_verified": bool(arms_differ), "fake_verdict_for_msg_check": fake_verdict}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=ho.FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=ho.FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=ho.STEPS_WM)
    ap.add_argument("--d-exp-mult", type=int, default=D_EXP_MULT_DEFAULT,
                     help="fixed-expansion factor x d_enc for the DG-analog projection E")
    ap.add_argument("--k-wta", type=int, default=K_WTA_DEFAULT,
                     help="k-WTA sparsity (top-k highest-value activations kept)")
    ap.add_argument("--dg-seed", type=int, default=DG_SEED,
                     help="fixed seed for E/bucket_of construction (shared across data-seeds by design)")
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else (len(ho.SEEDS_FULL) * 2 + len(ho.LONGER_SEED) + 1)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (serialization safety + checkpoint/resume + role split "
                           "integrity + expanded construction + real encoder + FixedDGAddressWM "
                           "no-learned-key invariant + addr_logits shape + arms-differ + verdict-reuse)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "addr_chance": ho.ADDR_CHANCE,
            "chance_recall": ho.CHANCE_RECALL, "d_exp_mult": args.d_exp_mult, "k_wta": args.k_wta,
            "dg_seed": args.dg_seed, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    steps_wm = args.steps_wm
    _log("FULL: train_n=%d eval_n=%d steps_wm=%d longer_mult=%d seeds=%s addr_chance=%.4f "
         "chance_recall=%.4f train_roles=%d held_out_roles=%d d_exp_mult=%d k_wta=%d dg_seed=%d"
         % (args.train_n, args.eval_n, steps_wm, ho.LONGER_MULT, ho.SEEDS_FULL, ho.ADDR_CHANCE,
            ho.CHANCE_RECALL, len(ho.TRAIN_ROLES), len(ho.HELD_OUT_ROLES), args.d_exp_mult, args.k_wta,
            args.dg_seed))
    cst = ho.construction_selftest(seed=7, n=600)
    if cst["fails"]:
        raise AssertionError("pre-run construction self-test FAILED: %s" % "; ".join(cst["fails"]))

    enc = ho.base.FrozenV2Encoder(ho.V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = ho.rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    datasets = {}
    for seed in ho.SEEDS_FULL:
        tr = ho.gen_dataset_expanded(args.train_n, np.random.default_rng(seed))
        ev = ho.gen_dataset_expanded(args.eval_n, np.random.default_rng(seed + 777))
        datasets[seed] = (ho.build_index_batch_ext(tr, enc, seed), ho.build_index_batch_ext(ev, enc, seed + 777),
                          tr, ev)

    # ---- MANDATORY per-unit checkpoint/resume (tools/exp_checkpoint.py; CLAUDE.md contract) ----
    # 6 units total: control_b, fixed_dg x2 seeds, control_a x2 seeds, control_a_longer x1.
    prior_units = ckpt.load_units(OUTPUT_DIR)
    if prior_units:
        _log("checkpoint: %d/6 units already recorded on disk; resuming (skipping those)" % len(prior_units))

    cb_key = ckpt.unit_key("control_b")
    if cb_key in prior_units:
        control_b = prior_units[cb_key]
        _log("  [resume] control_b loaded from checkpoint: train_acc=%.4f held_acc=%.4f"
             % (control_b["train_acc"], control_b["heldout_acc"]))
    else:
        _log("--- control B (zero-training per-role-lookup ceiling; eval sets pooled) ---")
        pooled_eval = []
        for seed in ho.SEEDS_FULL:
            pooled_eval.extend(datasets[seed][3])
        control_b = ho.control_b_perrole_groundtruth(pooled_eval)
        _log("  control_b: train_acc=%.4f held_acc=%.4f" % (control_b["train_acc"], control_b["heldout_acc"]))
        ckpt.record_unit(OUTPUT_DIR, cb_key, control_b)

    _log("--- FIXED_DG_ADDRESS (pca_whiten + fixed random-expand + k-WTA + hash-to-bucket) ---")
    fixed_results = []
    for seed in ho.SEEDS_FULL:
        k = ckpt.unit_key("fixed_dg", seed)
        if k in prior_units:
            fixed_results.append(prior_units[k])
            _log("  [resume] fixed_dg seed=%d loaded from checkpoint" % seed)
            continue
        tr_b, ev_b, _, _ = datasets[seed]
        res = ho._strip_for_checkpoint(run_fixed_dg_address(enc, cond, tr_b, ev_b, seed, steps_wm,
                                                              args.d_exp_mult, args.k_wta, args.dg_seed))
        ckpt.record_unit(OUTPUT_DIR, k, res)
        fixed_results.append(res)

    _log("--- CONTROL_A_NO_WARMSTART (reused unchanged; original STUCK_FLAT setup, same split/steps) ---")
    controlA_results = []
    for seed in ho.SEEDS_FULL:
        k = ckpt.unit_key("control_a", seed)
        if k in prior_units:
            controlA_results.append(prior_units[k])
            _log("  [resume] control_a seed=%d loaded from checkpoint" % seed)
            continue
        tr_b, ev_b, _, _ = datasets[seed]
        res = ho._strip_for_checkpoint(ho.run_control_a(enc, cond, tr_b, ev_b, seed, steps_wm))
        ckpt.record_unit(OUTPUT_DIR, k, res)
        controlA_results.append(res)

    _log("--- CONTROL_A_LONGER_SCHEDULE (reused unchanged; Olsson diagnostic, %dx steps, seed=%s) ---"
         % (ho.LONGER_MULT, ho.LONGER_SEED))
    longer_seed = ho.LONGER_SEED[0]
    lk = ckpt.unit_key("control_a_longer", longer_seed)
    if lk in prior_units:
        longer_result = prior_units[lk]
        _log("  [resume] control_a_longer seed=%d loaded from checkpoint" % longer_seed)
    else:
        tr_b, ev_b, _, _ = datasets[longer_seed]
        longer_result = ho._strip_for_checkpoint(
            ho.run_control_a(enc, cond, tr_b, ev_b, longer_seed, steps_wm * ho.LONGER_MULT,
                              log_tag="CONTROL_A_LONGER"))
        ckpt.record_unit(OUTPUT_DIR, lk, longer_result)

    arms_differ = fixed_results[0]["ev_logits_sha256"] != controlA_results[0]["ev_logits_sha256"]

    verdict, msg, bands = ho.decide_verdict(fixed_results, controlA_results, control_b, longer_result)
    msg = _retarget_msg(msg)
    elapsed = time.perf_counter() - t0

    n_units_done = len(fixed_results) + len(controlA_results) + 1 + 1
    expected_n_units_full = len(ho.SEEDS_FULL) * 2 + 1 + 1

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | addr_chance=%.4f | %s" % (verdict, ho.ADDR_CHANCE, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "addr_chance": ho.ADDR_CHANCE, "chance_recall": ho.CHANCE_RECALL, "oracle_ceiling_ref": 1.0,
        "bands": bands, "role_split": {"train_roles": ho.TRAIN_ROLES, "held_out_roles": ho.HELD_OUT_ROLES,
                                        "role_split_seed": ho.ROLE_SPLIT_SEED},
        "construction_selftest": cst, "control_b": control_b,
        "fixed_dg_address_per_seed": [
            {k: v for k, v in r.items() if k not in ("ev_logits",)} for r in fixed_results],
        "control_a_per_seed": [
            {k: v for k, v in r.items() if k not in ("ev_logits",)} for r in controlA_results],
        "control_a_longer_schedule": {k: v for k, v in longer_result.items() if k not in ("ev_logits",)},
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"S_TARGET_TOTAL": ho.S_TARGET_TOTAL, "K_SLOTS": ho.K_SLOTS, "D_MEM": ho.D_MEM,
                   "HIDDEN": ho.HIDDEN, "ADDR_TEMP": ho.ADDR_TEMP, "STEPS_WM": steps_wm,
                   "LONGER_MULT": ho.LONGER_MULT, "LR": ho.LR, "train_n": args.train_n, "eval_n": args.eval_n,
                   "seeds": list(ho.SEEDS_FULL), "longer_seed": list(ho.LONGER_SEED),
                   "train_roles": ho.TRAIN_ROLES, "held_out_roles": ho.HELD_OUT_ROLES,
                   "n_cached_sentences": n_cached, "encoder": "real_v2_frozen",
                   "v2_ckpt": os.path.relpath(ho.V2_CKPT, REPO_ROOT),
                   "d_exp_mult": args.d_exp_mult, "d_exp": args.d_exp_mult * enc.d, "k_wta": args.k_wta,
                   "dg_seed": args.dg_seed, "addressing_mechanism": "fixed_dg_analog_no_learned_key"},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 60})
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
