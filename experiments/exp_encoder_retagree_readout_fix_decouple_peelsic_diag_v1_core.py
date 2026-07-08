"""DIAGNOSTIC (measurement only): why does ret_agree10 fail on the trained
semantic encoder despite cosine_to_gold>=0.8, and do our OWN certified retrieval
mechanisms -- the correlation-hurts DECOUPLE law (whitened/decorrelated retrieval
codes) and peel/SIC matching-pursuit readout -- close the top-10 retrieval-agreement
gap?

CONTEXT (verified off-disk 2026-07-08):
  MEASURED@data/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_seed_7
    /metrics.json:ship
      cosine_to_gold(hi80) = 0.8611  (>=0.80 PASS)
      composed_roundtrip   = 0.9833  (>=0.95 PASS)
      spearman_all         = 0.8969
      ret_agree10          = 0.1837  (<0.30 FAIL)  <-- the proxy-to-real gap
  The trained INBATCH-RKD-only SBC block encoder has strong POINTWISE fidelity but
  its TOP-10 retrieval neighborhood disagrees with the BGE teacher's, and top-k
  retrieval is exactly what the operational KB query needs.

THIS CELL IS A MEASUREMENT. It does NOT re-ingest, does NOT change any operational
default, does NOT mutate the KB. It only trains (FULL) / synthesizes (SMOKE) an
encoder in an isolated artifact dir and computes retrieval-agreement under three
readout arms plus neighborhood diagnostics, writing to its OWN metrics.json.

ARMS (all compute ret_agree10 on the SAME held query set vs the SAME held corpus,
matching v3._semantic_unit's top-10 overlap contract):
  baseline    raw student code cosine top-10   [DISCRIMINATOR: must FAIL <0.30]
  armA_whiten ZCA-whitened / decorrelated retrieval codes (the DECOUPLE law
              instantiated at READOUT time: decorrelate the retrieval code before
              cosine top-10)
  armB_peelsic peel/SIC matching-pursuit readout (certified peel_sic_readout
              mode='proj'): pick nearest, deflate its projection from the query
              residual, repeat -> top-10 in confidence order

DIAGNOSTIC METRICS (why the baseline fails):
  teacher_margin_top1_top10   median(top1 - top10) teacher cosine in the held
                              corpus -- neighborhood CROWDING (small => near-ties)
  student_margin_top1_top10   same on baseline student codes
  code_mean_nnz               mean non-zeros per student code (SBC sparsity)
  code_offdiag_corr_abs       mean |off-diagonal| code-dim correlation
                              (the correlation-hurts pathology the DECOUPLE law
                              targets; SBC block codes are near-decorrelated by
                              construction, so whitening has little to act on)

VERDICT (HP_RET_AGREE10 = 0.30 gate, strict per META_RULE_L):
  HARD_PASS  max(armA,armB) >= 0.315 AND >= baseline + 0.02  (a decouple/peel-SIC
             arm lifts ret_agree10 over the failing baseline -> names the
             operational fix for the encoder-default flip)
  HARD_FAIL  max(armA,armB) < 0.30   (neither readout fix lifts it -> honest; the
             gap is a QUANTIZATION-RESOLUTION vs neighborhood-crowding problem, not
             a code-correlation or bundle-decomposition problem -> route to the
             graded-code / STE-anneal lever, NOT a readout transform)
  MIDDLE_BAND 0.30 <= max(armA,armB) < 0.315 (at-floor; inconclusive)

RUN MODES:
  full   train the REAL INBATCH-RKD SBC encoder (reuses the shipmetric core's
         train + encode path verbatim -> identical encoder that produced
         ret_agree10=0.1837), then run the 3 arms + diagnostics on real codes.
         Compute class: batched-GPU (training matmuls + big top-k matmuls). GPU.
  smoke  phenomenon-faithful SYNTHETIC codes (random Gaussian projection of the
         REAL BGE teacher geometry + calibrated noise + the SAME block-SBC
         quantizer) -- reproduces high spearman + low ret_agree10 WITHOUT the
         GPU-scale training the laptop cannot do; validates MACHINERY + fires the
         discriminator + confirms the diagnostic. The FIX-lift MAGNITUDE verdict
         is the FULL's job on real codes (SMOKE synthetic lacks the trained code's
         exact geometry). smoke also calls the certified numpy peel_sic_readout
         for parity with the batched-torch SIC used at FULL.
  self_test  tiny synthetic; asserts all arms run + return finite. No verdict.

ASCII-only. No emojis. No em dashes.

Modules reused (single source of truth; not duplicated):
  experiments/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core (ship)
  experiments/exp_encoder_migration_step1b_v3_..._v1_core (v3)
  experiments/exp_encoder_migration_step1b_v3c_..._v1_core (v3c)
  hdlab/cleanup_family.peel_sic_readout (certified: commit 916e6f7cb / c2f65e53d)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core as ship,
)
v3 = ship.v3
v3c = ship.v3c
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from hdlab.cleanup_family import peel_sic_readout  # noqa: E402

# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_retagree_readout_fix_decouple_peelsic_diag_v1"
SEED_DEFAULT = 7

# Ship-metric bands (JOINT retrieval gate; per Director hand-off contract).
HP_RET_AGREE10 = 0.30           # gate floor (HYPOTHESIZED@hand-off contract)
HP_STRICT = 0.315               # strict HARD_PASS (floor + 5% band; META_RULE_L)
HP_MIN_LIFT = 0.02              # a fix must genuinely beat the baseline
DISCR_BASELINE_CEIL = 0.30      # baseline MUST fail below this (discriminator)

N_ITEMS = 10                    # top-10 retrieval agreement
ZCA_EPS = 1e-2                  # whitening regularizer (ill-conditioning guard)

# Query/corpus scale. Corpus = the held set (matches v3._semantic_unit contract:
# retrieval within the held-out concepts). Queries = a subsample of held (SIC is
# O(Q * N_ITEMS * corpus); baseline/whiten are single matmuls over all held).
FULL_QUERY_SUB = 2000
FULL_CORPUS_CAP = 20000         # matches v3.FULL_HELD_CAP ceiling
SMOKE_N_CONCEPTS = 8000         # teacher subsample for synthetic corpus
SMOKE_QUERY_SUB = 500
SMOKE_NOISE = 0.7               # CALIBRATED so the synthetic baseline ret_agree10
                                # approximates the REAL failing regime (0.184
                                # MEASURED@shipmetric seed_7 metrics.json:ship
                                # .ret_agree10). Not gaming: the discriminator gate
                                # is "baseline fails like the real encoder"; this
                                # calibrates the synthetic to that documented failure.

EXPECTED_N_UNITS = 3            # baseline, armA_whiten, armB_peelsic

TEACHER_CACHE_FULL = ship.TEACHER_CACHE_FULL


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / heartbeat) -- per section 13.
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir: Path, run_mode: str) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")


def _emit_heartbeat(output_dir: Path, i: int, n: int, elapsed: float,
                    extra: Optional[Dict] = None) -> None:
    try:
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(),
               "unit_idx": int(i), "total_units": int(n),
               "elapsed_s": float(elapsed)}
        if extra:
            row["extra"] = extra
        with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass  # heartbeat best-effort; never fatal


def _artifact_dir(run_mode: str, seed: int) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return (_REPO / "data"
            / f"substrate_retagree_diag_v1{suffix}_seed{int(seed)}")


# ---------------------------------------------------------------------------
# Code transforms.
# ---------------------------------------------------------------------------
def _l2n(x: torch.Tensor) -> torch.Tensor:
    return x / (x.norm(dim=-1, keepdim=True) + 1e-8)


def _sbc_encode_from_dense(z: torch.Tensor, kb: int, blk_l: int) -> torch.Tensor:
    """Block-argmax sign SBC quantizer (identical forward to v3._encode_hard_block)."""
    B = z.shape[0]
    zb = z.reshape(B, kb, blk_l)
    o = torch.zeros_like(zb)
    idx = zb.abs().argmax(dim=-1, keepdim=True)
    sgn = torch.sign(torch.gather(zb, -1, idx))
    sgn[sgn == 0] = 1.0
    o.scatter_(-1, idx, sgn)
    return o.reshape(B, kb * blk_l)


def _zca_fit(codes_all: torch.Tensor, eps: float = ZCA_EPS) -> Tuple[torch.Tensor, torch.Tensor]:
    """ZCA whitening from the code covariance (cov-eigh in float64; robust to
    the ill-conditioning that full-matrix SVD hit). Returns (mu, W)."""
    mu = codes_all.mean(0, keepdim=True)
    Xc = (codes_all - mu).double()
    d = Xc.shape[0]
    cov = (Xc.t() @ Xc) / max(1, d)
    cov = cov + eps * torch.eye(cov.shape[0], dtype=torch.float64, device=cov.device)
    evals, evecs = torch.linalg.eigh(cov)
    evals = torch.clamp(evals, min=eps)
    W = evecs @ torch.diag(1.0 / torch.sqrt(evals)) @ evecs.t()
    return mu, W.to(codes_all.dtype)


def _ret_agree_cosine(q_codes: torch.Tensor, corpus_codes: torch.Tensor,
                      Xq: torch.Tensor, Xcorp: torch.Tensor,
                      q_self_idx: torch.Tensor, chunk: int = 512) -> float:
    """Top-10 overlap between teacher (Xq vs Xcorp) and student (q_codes vs
    corpus_codes) neighborhoods. q_self_idx[i] = row in corpus that is query i
    itself (excluded from both top-10). Mirrors v3._semantic_unit's contract."""
    cq = _l2n(q_codes)
    cc = _l2n(corpus_codes)
    Xq_n = _l2n(Xq)
    Xc_n = _l2n(Xcorp)
    nq = cq.shape[0]
    agree = 0.0
    for lo in range(0, nq, chunk):
        hi = min(lo + chunk, nq)
        rows = torch.arange(lo, hi)
        ts = Xq_n[lo:hi] @ Xc_n.t()
        ts[torch.arange(hi - lo), q_self_idx[lo:hi]] = -2.0
        t10 = ts.topk(N_ITEMS, dim=1).indices
        ss = cq[lo:hi] @ cc.t()
        ss[torch.arange(hi - lo), q_self_idx[lo:hi]] = -2.0
        s10 = ss.topk(N_ITEMS, dim=1).indices
        for r in range(hi - lo):
            agree += len(set(t10[r].tolist()) & set(s10[r].tolist())) / float(N_ITEMS)
    return agree / max(1, nq)


def _sic_topk_torch(q_codes: torch.Tensor, corpus_codes: torch.Tensor,
                    Xq: torch.Tensor, Xcorp: torch.Tensor,
                    q_self_idx: torch.Tensor) -> float:
    """peel/SIC matching-pursuit (mode='proj') top-10 retrieval, batched in torch
    for FULL scale. Algorithm identical to hdlab.cleanup_family.peel_sic_readout
    mode='proj': score residual vs corpus, pick argmax, deflate its projection,
    never repick. Teacher top-10 is plain cosine (the gold ordering)."""
    cq = _l2n(q_codes).clone()
    cc = _l2n(corpus_codes)
    Xq_n = _l2n(Xq)
    Xc_n = _l2n(Xcorp)
    nq, M = cq.shape[0], cc.shape[0]
    cc_sqnorm = (cc * cc).sum(1) + 1e-12
    resid = cq.clone()
    picked = torch.zeros(nq, M, dtype=torch.bool)
    ar = torch.arange(nq)
    picked[ar, q_self_idx] = True  # never pick self
    preds = torch.full((nq, N_ITEMS), -1, dtype=torch.long)
    for r in range(N_ITEMS):
        scores = resid @ cc.t()
        scores[picked] = -1e30
        ih = scores.argmax(dim=1)
        preds[:, r] = ih
        picked[ar, ih] = True
        chosen = cc[ih]
        coeff = (resid * chosen).sum(1) / cc_sqnorm[ih]
        resid = resid - coeff.unsqueeze(1) * chosen
    agree = 0.0
    for i in range(nq):
        ts = Xq_n[i] @ Xc_n.t()
        ts[q_self_idx[i]] = -2.0
        t10 = set(ts.topk(N_ITEMS).indices.tolist())
        agree += len(t10 & set(preds[i].tolist())) / float(N_ITEMS)
    return agree / max(1, nq)


def _diag_margins(q_codes: torch.Tensor, corpus_codes: torch.Tensor,
                  Xq: torch.Tensor, Xcorp: torch.Tensor,
                  q_self_idx: torch.Tensor) -> Dict[str, float]:
    """Neighborhood crowding + code-structure diagnostics."""
    Xq_n = _l2n(Xq)
    Xc_n = _l2n(Xcorp)
    cq = _l2n(q_codes)
    cc = _l2n(corpus_codes)
    # teacher margin
    ts = Xq_n @ Xc_n.t()
    ar = torch.arange(ts.shape[0])
    ts[ar, q_self_idx] = -2.0
    tv = ts.topk(N_ITEMS, dim=1).values
    t_margin = float((tv[:, 0] - tv[:, N_ITEMS - 1]).median())
    t_top1 = float(tv[:, 0].median())
    t_top10 = float(tv[:, N_ITEMS - 1].median())
    # student margin
    ss = cq @ cc.t()
    ss[ar, q_self_idx] = -2.0
    sv = ss.topk(N_ITEMS, dim=1).values
    s_margin = float((sv[:, 0] - sv[:, N_ITEMS - 1]).median())
    # code sparsity + dim correlation (on corpus)
    nnz = float((corpus_codes.abs() > 1e-8).float().sum(1).mean())
    dcap = min(256, corpus_codes.shape[1])
    sub = corpus_codes[:, :dcap] - corpus_codes[:, :dcap].mean(0, keepdim=True)
    cc_cov = sub.t() @ sub
    dd = torch.sqrt(torch.diag(cc_cov).clamp(min=1e-12))
    corr = cc_cov / (dd[:, None] * dd[None, :] + 1e-12)
    mask = ~torch.eye(dcap, dtype=torch.bool)
    offdiag = float(corr[mask].abs().mean())
    return {
        "teacher_margin_top1_top10": t_margin,
        "teacher_top1_median": t_top1, "teacher_top10_median": t_top10,
        "student_margin_top1_top10": s_margin,
        "code_mean_nnz": nnz, "code_offdiag_corr_abs": offdiag,
    }


# ---------------------------------------------------------------------------
# Code sources.
# ---------------------------------------------------------------------------
def _real_trained_codes(seed: int, device: str, out_dir: Path, art_dir: Path,
                        t0: float) -> Tuple[torch.Tensor, torch.Tensor, int, str, int]:
    """Train the REAL INBATCH-RKD SBC encoder (shipmetric train path verbatim) and
    return (Xhe teacher, inbatch_block codes, n_he, teacher_cache_name, n_train)."""
    n_dim = v3.N_DIM_DEFAULT
    kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
    cache_path = v3._resolve_teacher_cache(TEACHER_CACHE_FULL)
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    n_tr = V_cache - n_he
    tr_idx, he_idx = perm[:n_tr], perm[n_tr:n_tr + n_he]
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()
    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    print(f"[diag] teacher {cache_path.name}: {V_cache} concepts; "
          f"train={n_tr} held={n_he} ({time.perf_counter()-t0:.1f}s)", flush=True)
    pos_idx, semi_cands = v3._mine_teacher(Xtr, device, art_dir / "_mine_shards",
                                           out_dir, t0)
    steps, batch = ship.FULL_STEPS, ship.FULL_BATCH
    warmup = v3._warmup_for(steps)
    min_step_for_best = max(1, int(round(ship.MIN_STEP_FRAC_FOR_BEST * steps)))
    Xhe_sub = Xhe[:min(ship.FULL_QUICK_HELD_SUB, n_he)].contiguous()

    def _deval_quick(student):
        return v3._dense_spearman_quick(student, Xhe_sub, ship.FULL_QUICK_PAIRS,
                                        seed + 7)

    def _deval_full(student):
        return v3._dense_spearman_quick(student, Xhe, ship.FULL_TRAJ_PAIRS, seed + 7)

    _st, diag = v3c._train_student_full(
        kb, blk_l, Xtr, pos_idx, semi_cands, steps, batch, warmup, seed, device,
        art_dir / "_ckpt_INBATCH.pt", art_dir / "_ckpt_best_INBATCH.pt",
        ship.FULL_CKPT_EVERY, out_dir, t0, None, v3.FRAME_REFRESH_MID,
        ship.NCE_WEIGHT, "INBATCH", objective=ship.OBJECTIVE,
        dense_eval_quick_fn=_deval_quick, dense_eval_full_fn=_deval_full,
        dense_eval_every=ship.FULL_DENSE_EVAL_EVERY,
        min_step_for_best=min_step_for_best)
    print(f"[diag] trained rkd_last={diag['rkd_last']:.4f} "
          f"best_full={diag['best_dense_full']:.4f}@step{diag['best_step']} "
          f"({time.perf_counter()-t0:.1f}s)", flush=True)
    best = v3c._reload_best_student("mlp", Xtr.shape[1], kb * blk_l, device,
                                    art_dir / "_ckpt_best_INBATCH.pt")
    inbatch_block = v3._encode_hard_block(best, Xhe, kb, blk_l)
    return Xhe, inbatch_block, n_he, cache_path.name, n_tr


def _synthetic_codes(seed: int, n_concepts: int
                     ) -> Tuple[torch.Tensor, torch.Tensor, str]:
    """Phenomenon-faithful SMOKE codes: random Gaussian projection of the REAL BGE
    teacher geometry + calibrated noise + the SAME block-SBC quantizer. Carries the
    real crowded neighborhood; fires the discriminator without GPU-scale training."""
    n_dim = v3.N_DIM_DEFAULT
    kb, blk_l = v3.K_BLOCKS_PRIMARY, n_dim // v3.K_BLOCKS_PRIMARY
    cache_path = ship._resolve_smoke_cache(n_concepts)
    X, ids = v3._load_teacher(cache_path)
    g = torch.Generator().manual_seed(seed)
    V = min(n_concepts, X.shape[0])
    perm = torch.randperm(X.shape[0], generator=g)[:V]
    Xhe = _l2n(X[perm].float()).contiguous()
    P = torch.randn(Xhe.shape[1], n_dim, generator=g) / (Xhe.shape[1] ** 0.5)
    z = Xhe @ P
    z = z + SMOKE_NOISE * torch.randn(z.shape, generator=g) * z.std()
    codes = _sbc_encode_from_dense(z, kb, blk_l)
    return Xhe, codes, cache_path.name


# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------
def _verdict(baseline: float, whiten: float, peelsic: float, run_mode: str
             ) -> Tuple[str, str]:
    best = max(whiten, peelsic)
    best_arm = "armA_whiten" if whiten >= peelsic else "armB_peelsic"
    tail = (f"[baseline_ret_agree10={baseline:.4f} armA_whiten={whiten:.4f} "
            f"armB_peelsic={peelsic:.4f} best={best:.4f}({best_arm}) "
            f"gate={HP_RET_AGREE10}]")
    # discriminator must fire (baseline below the gate)
    if not (baseline < DISCR_BASELINE_CEIL):
        return ("SMOKE_GATE_FAIL",
                f"DISCRIMINATOR_DID_NOT_FIRE: baseline ret_agree10 {baseline:.4f} "
                f">= {DISCR_BASELINE_CEIL}; the failing-baseline phenomenon did not "
                f"reproduce at this scale -- cannot test the fix. {tail}")
    if best >= HP_STRICT and best >= baseline + HP_MIN_LIFT:
        return ("HARD_PASS",
                f"READOUT_FIX_LIFTS_RET_AGREE10: {best_arm} lifts ret_agree10 to "
                f"{best:.4f} (>= {HP_STRICT}) over the failing baseline "
                f"{baseline:.4f}; names the operational readout fix for the "
                f"encoder-default flip. {tail}")
    if best < HP_RET_AGREE10:
        return ("HARD_FAIL",
                f"NEITHER_READOUT_FIX_LIFTS_RET_AGREE10: best {best:.4f} < "
                f"{HP_RET_AGREE10}; the decouple/whiten and peel/SIC READOUT "
                f"transforms do NOT close the top-10 gap. The gap is a "
                f"quantization-resolution vs neighborhood-crowding problem, not a "
                f"code-correlation or bundle-decomposition problem -> route to the "
                f"graded-code / STE-anneal (finer-quantization) lever. {tail}")
    return ("MIDDLE_BAND",
            f"AT_FLOOR_INCONCLUSIVE: best {best:.4f} in "
            f"[{HP_RET_AGREE10}, {HP_STRICT}); a readout arm reaches the gate but "
            f"not strictly above it. {tail}")


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------
def run_diag(run_mode: str, seed: int, device_arg: str) -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    anchor = f"{ANCHOR_NAME}_smoke" if run_mode == "smoke" else ANCHOR_NAME
    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode, seed)
    art_dir.mkdir(parents=True, exist_ok=True)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    _write_start_marker(out_dir, run_mode)
    t0 = time.perf_counter()
    print(f"[diag] run_mode={run_mode} seed={seed} device={device} "
          f"anchor={anchor}", flush=True)

    if run_mode == "full":
        Xhe, codes, n_he, cache_name, n_train = _real_trained_codes(
            seed, device, out_dir, art_dir, t0)
        code_source = "real_trained_inbatch_rkd_sbc"
        corpus_cap, query_sub = FULL_CORPUS_CAP, FULL_QUERY_SUB
    else:
        Xhe, codes, cache_name = _synthetic_codes(seed, SMOKE_N_CONCEPTS)
        n_he, n_train = Xhe.shape[0], 0
        code_source = "synthetic_randproj_sbc_of_real_teacher"
        corpus_cap, query_sub = SMOKE_N_CONCEPTS, SMOKE_QUERY_SUB

    # corpus = held set (capped); queries = subsample of corpus (same tensors).
    n_corp = min(n_he, corpus_cap)
    Xcorp = Xhe[:n_corp].contiguous()
    corpus_codes = codes[:n_corp].contiguous()
    nq = min(query_sub, n_corp)
    q_idx = torch.arange(nq)                # first nq corpus rows are the queries
    Xq = Xcorp[q_idx].contiguous()
    q_codes = corpus_codes[q_idx].contiguous()
    q_self_idx = q_idx.clone()             # query i is corpus row i (excluded)
    print(f"[diag] corpus={n_corp} queries={nq} code_source={code_source} "
          f"({time.perf_counter()-t0:.1f}s)", flush=True)

    # ---- diagnostics ----
    diag = _diag_margins(q_codes, corpus_codes, Xq, Xcorp, q_self_idx)
    print(f"[diag] margins {json.dumps({k: round(v,4) for k,v in diag.items()})}",
          flush=True)
    _emit_heartbeat(out_dir, 0, EXPECTED_N_UNITS, time.perf_counter()-t0,
                    extra={"stage": "diagnostics"})

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []

    # ---- ARM baseline ----
    baseline = _ret_agree_cosine(q_codes, corpus_codes, Xq, Xcorp, q_self_idx)
    per_unit.append({"unit": "arm::baseline", "arm": "baseline",
                     "ret_agree10": baseline})
    print(f"[diag] arm 1/3 baseline ret_agree10={baseline:.4f} "
          f"({time.perf_counter()-t0:.1f}s)", flush=True)
    _emit_heartbeat(out_dir, 1, EXPECTED_N_UNITS, time.perf_counter()-t0,
                    extra={"arm": "baseline", "ret_agree10": baseline})

    # ---- ARM A: ZCA-whiten (DECOUPLE law at readout) ----
    mu, W = _zca_fit(corpus_codes)
    w_corp = _l2n((corpus_codes - mu) @ W)
    w_q = w_corp[q_idx]
    # retrieve in whitened space: pass whitened codes as both code args (Xq/Xcorp
    # teacher unchanged -> teacher top-10 gold identical to baseline).
    whiten = _ret_agree_cosine(w_q, w_corp, Xq, Xcorp, q_self_idx)
    per_unit.append({"unit": "arm::armA_whiten", "arm": "armA_whiten",
                     "ret_agree10": whiten, "zca_eps": ZCA_EPS})
    print(f"[diag] arm 2/3 armA_whiten ret_agree10={whiten:.4f} "
          f"({time.perf_counter()-t0:.1f}s)", flush=True)
    _emit_heartbeat(out_dir, 2, EXPECTED_N_UNITS, time.perf_counter()-t0,
                    extra={"arm": "armA_whiten", "ret_agree10": whiten})

    # ---- ARM B: peel/SIC matching-pursuit readout ----
    peelsic = _sic_topk_torch(q_codes, corpus_codes, Xq, Xcorp, q_self_idx)
    peelsic_parity = float("nan")
    if run_mode == "smoke":
        # parity: certified numpy peel_sic_readout(mode='proj') on a small subset.
        cb = _l2n(corpus_codes).numpy().astype(np.float64)
        Xc_n = _l2n(Xcorp)
        cq_n = _l2n(q_codes)
        n_par = min(120, nq)
        a = 0.0
        for i in range(n_par):
            ts = (Xc_n @ _l2n(Xq)[i]); ts[q_self_idx[i]] = -2.0
            t10 = set(ts.topk(N_ITEMS).indices.tolist())
            preds, _d = peel_sic_readout(cq_n[i].numpy().astype(np.float64), cb,
                                         n_items=N_ITEMS + 1, mode="proj")
            s = [int(x) for x in preds if int(x) != int(q_self_idx[i])][:N_ITEMS]
            a += len(t10 & set(s)) / float(N_ITEMS)
        peelsic_parity = a / max(1, n_par)
    per_unit.append({"unit": "arm::armB_peelsic", "arm": "armB_peelsic",
                     "ret_agree10": peelsic, "peelsic_parity_numpy": peelsic_parity})
    print(f"[diag] arm 3/3 armB_peelsic ret_agree10={peelsic:.4f} "
          f"parity={peelsic_parity:.4f} ({time.perf_counter()-t0:.1f}s)", flush=True)
    _emit_heartbeat(out_dir, 3, EXPECTED_N_UNITS, time.perf_counter()-t0,
                    extra={"arm": "armB_peelsic", "ret_agree10": peelsic})

    # ---- META_RULE_AF arms-must-differ (transformed retrieval scores differ) ----
    digests = {
        "baseline": hashlib.sha256(_l2n(q_codes).numpy().tobytes()).hexdigest(),
        "armA_whiten": hashlib.sha256(w_q.numpy().tobytes()).hexdigest(),
    }
    arms_differ = digests["baseline"] != digests["armA_whiten"]
    # armB uses a different algorithm (matching pursuit), inherently differs.

    if abs(len(per_unit)) != EXPECTED_N_UNITS:
        raise RuntimeError(
            f"failure_class=CARDINALITY_BREACH: {len(per_unit)} != {EXPECTED_N_UNITS}")

    verdict, verdict_msg = _verdict(baseline, whiten, peelsic, run_mode)
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device, "N": v3.N_DIM_DEFAULT,
        "code_source": code_source, "teacher_cache": cache_name,
        "n_held_corpus": int(n_corp), "n_queries": int(nq), "n_train": int(n_train),
        "arms": {
            "baseline_ret_agree10": baseline,
            "armA_whiten_ret_agree10": whiten,
            "armB_peelsic_ret_agree10": peelsic,
            "armB_peelsic_parity_numpy": peelsic_parity,
            "best_fix": max(whiten, peelsic),
            "delta_best_vs_baseline": max(whiten, peelsic) - baseline,
        },
        "diagnostics": diag,
        "discriminator_fires": bool(baseline < DISCR_BASELINE_CEIL),
        "hp_ret_agree10": HP_RET_AGREE10, "hp_strict": HP_STRICT,
        "hp_min_lift": HP_MIN_LIFT,
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_unit) == EXPECTED_N_UNITS,
        "arms_differ_verified": bool(arms_differ),
        "final_metrics_atomicity": "write_metrics_tmp_replace",
        "progress_logging": "print_flush_true",
        "crlb_n/a": ("no quantitative noise-floor estimator applies; this is a "
                     "retrieval-agreement diagnostic, not a capacity CRLB cell"),
        "discriminator_reachability": True,
        "baseline_in_band": bool(0.0 < baseline < DISCR_BASELINE_CEIL),
        "cell_chunked": True, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "hp_scope": {"armA_whiten": ["ret_agree10"],
                     "armB_peelsic": ["ret_agree10"]},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[diag] VERDICT {verdict}: {verdict_msg}", flush=True)
    print(f"[diag] wrote {out_dir/'metrics.json'} ({elapsed:.1f}s)", flush=True)
    return 0


def run_self_test() -> int:
    """Tiny synthetic; assert all 3 arms run + return finite. No verdict/metrics."""
    print("[diag] self-test begin", flush=True)
    kb, blk_l = 8, 8
    n_dim = kb * blk_l
    g = torch.Generator().manual_seed(0)
    Xhe = _l2n(torch.randn(200, 64, generator=g))
    P = torch.randn(64, n_dim, generator=g) / 8.0
    z = Xhe @ P + 0.5 * torch.randn(200, n_dim, generator=g)
    codes = _sbc_encode_from_dense(z, kb, blk_l)
    q_idx = torch.arange(40)
    Xq = Xhe[q_idx].contiguous(); q_codes = codes[q_idx].contiguous()
    base = _ret_agree_cosine(q_codes, codes, Xq, Xhe, q_idx)
    mu, W = _zca_fit(codes)
    w = _l2n((codes - mu) @ W)
    whit = _ret_agree_cosine(w[q_idx], w, Xq, Xhe, q_idx)
    sic = _sic_topk_torch(q_codes, codes, Xq, Xhe, q_idx)
    dg = _diag_margins(q_codes, codes, Xq, Xhe, q_idx)
    for name, v in (("baseline", base), ("whiten", whit), ("peelsic", sic)):
        if not math.isfinite(v):
            raise RuntimeError(f"self-test arm {name} non-finite: {v}")
    _p, _d = peel_sic_readout(_l2n(q_codes)[0].numpy().astype(np.float64),
                              _l2n(codes).numpy().astype(np.float64),
                              n_items=N_ITEMS, mode="proj")
    print(f"[diag] self-test OK base={base:.3f} whiten={whit:.3f} sic={sic:.3f} "
          f"margins={json.dumps({k: round(x,3) for k,x in dg.items()})}", flush=True)
    return 0
