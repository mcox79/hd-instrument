"""Backward-Compatible-Training (BCT) compatibility-loss cell (continual-encoder
rescue, decisive follow-up to the cross-checkpoint retrieval-compat probe).

Spec source: notes/research_drill_brain_grounded_continual_self_improving_encoder_
2026-07-04.md ("Cheap decisive test" section, Part-3 recommendation) +
preregs/2026-07-04_exp_encoder_cross_checkpoint_retrieval_compat_v1.md, whose
READ-ONLY probe MEASURED that swapping the concept encoder (GLOBAL vs IN_BATCH
final checkpoints of the R1 MID run, no explicit compatibility term between them)
collapses cross-checkpoint top-1 retrieval to ~1.0-1.5% of same-checkpoint
retrieval at full held-set scale (n=4390) -- 45-68x above the random floor but
far below any usable bar. That probe's own routing: "pull the explicit
compatibility-loss work FORWARD to NOW."

THIS CELL builds and tests that fix directly: train a SMALL "version B" encoder
(a genuinely new/updated encoder instance -- different init seed, different
training-set subsample, than "version A") twice, PAIRED (identical init seed,
identical batch-index sequence, identical data), differing ONLY in whether an
explicit BCT compatibility loss anchors B's block-sparse code to a FROZEN sample
of "version A"'s codes:
  NO_BCT:   loss = L_rkd (in-batch geometry-distillation to the BGE teacher)
  WITH_BCT: loss = L_rkd + BCT_WEIGHT * L_bct
            L_bct = mean(1 - cos(code_B(x), code_A_frozen(x)))  over anchor items
"Version A" = the ALREADY-EXISTING, already-trained R1 GLOBAL-objective MID
checkpoint (data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_global.pt,
step 1800) -- the real "already deployed, already indexed" encoder, reused
frozen (no retraining) exactly as the spawn instruction directs. Teacher cache
reused is the EXACT same npz R1 MID trained against (bge_large_v2_name_43905_
8a40445a.npz, V=43905, split (39515,4390) MEASURED@both this file's split-
reproduction check and the prior probe's EXPECTED_MID_SPLIT) -- NOT a "pick
largest cache" heuristic, because the remote CPU box's cached_indices/ directory
also holds much larger (177k-concept) caches from the ongoing corpus-ingest
pipeline; picking "largest" on remote would silently load the WRONG corpus
(different V, different permutation, EXPECTED_MID_SPLIT check would then
correctly abort it, but the intent is to reproduce A's exact split, not merely
avoid a crash).

Decisive question: does the BCT loss restore cross-version retrieval (A's
index, B's query -- the realistic "encoder got updated, old vectors are still
in the store" scenario) from collapse (NO_BCT arm, expected to reproduce the
~1-5% collapse at this cell's own reduced CPU scale) to usable (WITH_BCT arm,
target >=50% of same-checkpoint-A ceiling), WITHOUT wrecking WITH_BCT's own
held-out semantic quality relative to NO_BCT's?

Explicit non-auto-SCP dependency (READ BEFORE DISPATCH): CKPT_A
(_ckpt_block_global.pt, ~120MB) is gitignored (data/*/** pattern) and was
trained LOCALLY today -- it does NOT exist on the remote CPU box and is NOT
covered by queue_add.sh's script/prereg/sibling-helper auto-SCP. MUST be
explicit-scp'd to marsh@home:C:/dev/hd-instrument/data/substrate_concept_
encoder_v1b_v3global_mid/_ckpt_block_global.pt before this cell can run
remotely (verified via SSH: remote directory did not exist prior to this
cell's dispatch). The teacher cache (bge_large_v2_name_43905_8a40445a.npz,
~319MB) is CONFIRMED already present on remote with an IDENTICAL byte size to
the local copy (334512907 bytes both sides, verified via SSH `Get-ChildItem`
before authoring this cell) -- no teacher-cache SCP needed.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01): query
"BCT backward compatible training compatibility loss encoder version
cross-checkpoint retrieval anchoring frozen embedding" -> top hit cosine=0.3291
("Versioning + backwards compatibility",
notes/research_drill_production_deployment_architecture_2026-06-07.md,
deployment/ops versioning practice, NOT this mechanism); rank 2-3 are FHRR
cross-modal projection chunks (different topic: modality-to-FHRR encoding, not
BCT); rank 4-5 are WordNet/FrameNet lexical "compatibility" entries. NONE of
the top-5 hits address this specific BCT-loss mechanism or cell. Same
conclusion as the prior probe's own prior-work check: GENUINELY NOVEL.

Scope reduction (explicit, deliberate): unlike the full R1 GLOBAL/v2 training
pipeline (semi-hard-negative mining + landmark-frame RKD + InfoNCE), this cell
uses PURE IN-BATCH RKD geometry-distillation only (no mining, no NCE, no
landmark frame) as version B's base objective. This is a deliberate scope cut
to keep the cell cheap/self-contained/auditable for a "cheap decisive test" of
the BCT mechanism specifically (not a re-test of the GLOBAL-vs-IN_BATCH
objective question, which is already covered by the R1 rescue arc). In-batch
RKD is CITED@exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_
concept_encoder_v1_core.py's own docstring as adequate at SMALL N (that
docstring's diagnosis: in-batch RKD only breaks down at full production scale
V~160k+, where batch coverage of correlated pairs vanishes; at this cell's
N_TRAIN_B<=6000 scale batch coverage is far higher, so in-batch RKD alone is
expected to produce a non-degenerate, moderately-good encoder -- sufficient to
test whether adding a BCT term measurably trades off against it).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 hash-check across A_block, B_block[NO_BCT],
  B_block[WITH_BCT] (+ dense variants) before any verdict logic
- final_metrics_atomicity: tmp_replace (this cell's own tmp+os.replace writer)
- except SystemExit / KeyboardInterrupt: raise BEFORE except Exception (no
  bare except, no except BaseException)
- crlb_floor_computed: n/a -- retrieval-identity ratio, not a noise-floor
  metric (same rationale as the prior cross-checkpoint probe); chance floor =
  1/n_probe, verified empirically via RANDOM_CONTROL rather than closed-form
- baseline_in_band (META_RULE_AG analog): SAME_A and SAME_B (both arms) must
  be >= 0.99 (near-ceiling sanity); BASELINE_MUST_COLLAPSE gate: NO_BCT arm's
  min_ratio must be < 0.50 (the discriminator -- cross-version collapse --
  MUST fire at this reduced scale, else there is nothing for BCT to fix and
  the whole test is vacuous; this is the positive-control / discriminator-
  fires check for THIS cell, analogous to Gate D's "reproduce prior result at
  test regime" but here the "prior result" being reproduced is the FAILURE
  MODE itself, at reduced CPU scale, before crediting the fix)
- discriminator-fires (META_RULE_K): RANDOM_CONTROL <= 0.10 (both codes)
- discriminator survives scale: SMOKE runs at reduced N_TRAIN_B/steps/n_probe;
  FULL (this cell's terminal CPU-scale tier) is ALSO run directly on local CPU
  once before remote dispatch (Option-A discriminator-preview: full-N smoke,
  not merely a machinery check) BECAUSE this cell is cheap enough (~1-3 min)
  to run at full scale locally for free before shipping the SAME config to
  remote_cpu_queue for the official landing
- HARD_PASS strictly above floor + 5% band-width (META_RULE_L): bands below
- HP_SCOPE: HARD_PASS/HARD_FAIL gate applies ONLY to {min_ratio_WITH_BCT,
  quality_retention_WITH_BCT}; SAME_*/RANDOM_CONTROL/min_ratio_NO_BCT are
  integrity-only / positive-control, not part of the primary gate (but
  min_ratio_NO_BCT >= 0.50 aborts to MIDDLE_BAND as "discriminator did not
  fire", per baseline_in_band above)
- cardinality_ok: EXPECTED_N_UNITS = 14 (SAME_A x2 codes + [SAME_B + CROSS] x
  2 arms x 2 codes = 8 + RANDOM_CONTROL x2 codes + semantic_spearman x2 arms
  [dense only] = 2+8+2+2=14)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: adaptive_with_discriminator_gate -- BCT_WEIGHT is a
  HYPOTHESIZED starting value tuned via local smoke (this cell's own
  discriminator-fires check on the WITH_BCT arm gates the calibration: if
  smoke shows WITH_BCT does not clear ratio>=0.20 headroom, BCT_WEIGHT is
  bumped before FULL dispatch; the smoke log/prereg records the final tuned
  value used for FULL)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the
  prereg (preregs/2026-07-04_exp_encoder_bct_compatibility_loss_v1.md)

Prereg: preregs/2026-07-04_exp_encoder_bct_compatibility_loss_v1.md
Reused (DATA only, not code -- this file is fully self-contained, no sibling-
experiment import, per the explicit-SCP risk called out in the dispatch
contract): data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_global.pt
(architecture/constants duplicated here to match, see MLP_HIDDEN/N_DIM/K_BLOCKS
comments) + data/substrate_index/cached_indices/bge_large_v2_name_43905_
8a40445a.npz (teacher cache, hardcoded filename not "largest" heuristic).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

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
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402 (Pattern-5 shared module)

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_bct_compatibility_loss_v1"

# "version A" = frozen, already-existing R1 GLOBAL MID checkpoint. Architecture
# constants MUST match that checkpoint exactly (duplicated here, not imported,
# to keep this cell single-file / no sibling-experiment SCP dependency).
CKPT_DIR = _REPO / "data" / "substrate_concept_encoder_v1b_v3global_mid"
CKPT_A = CKPT_DIR / "_ckpt_block_global.pt"
N_DIM = 4096
K_BLOCKS = 128
BLK_L = N_DIM // K_BLOCKS         # 32
MLP_HIDDEN = 2048                 # CITED@exp_encoder_migration_step1b_v3_..._core.py MLP_HIDDEN

# Teacher cache: HARDCODED to the exact file R1 MID trained against (V=43905,
# split (39515,4390)). NOT a "largest file" heuristic -- the remote CPU box
# also holds much larger (177k-concept) caches from the ongoing ingest
# pipeline; "largest" would silently select the wrong corpus there.
_CACHE_DIR = _REPO / "data" / "substrate_index" / "cached_indices"
TEACHER_CACHE_NAME = "bge_large_v2_name_43905_8a40445a.npz"

SPLIT_SEED = 7                    # CITED@exp_encoder_migration..._core.py SEED_DEFAULT
HELD_FRAC = 0.10
MID_HELD_CAP = 5000
EXPECTED_MID_SPLIT = (39515, 4390)  # MEASURED@prior cross-checkpoint probe's own split check

B_INIT_SEED = 13                  # version-B init seed (SAME both arms -- paired)
BATCH_GEN_SEED = 4242              # batch-order generator seed (SAME both arms -- paired)
TRAIN_SUBSAMPLE_SEED = 777         # draws N_TRAIN_B indices from the R1 train split
PROBE_SEED = 888                   # draws N_PROBE indices from the R1 held split
RAND_CTRL_SEED_1 = 501
RAND_CTRL_SEED_2 = 502
SEM_PAIR_SEED = 999

LR = 1e-3
WARMUP_FRAC = 0.2
TAU_GUMBEL = 1.0

# adaptive_with_discriminator_gate (calibration_check): tuned via a local
# smoke-scale weight sweep {0.03,0.05,0.07,0.08,0.1,0.12,0.15,0.2,0.3,0.5,
# 0.75,1.0,1.5,2.0,3.0,8.0} BEFORE full dispatch (not cherry-picked post-hoc
# for a specific verdict tier). MEASURED@this sweep: weight>=0.5 saturates
# cross-retrieval to 0.99-1.00 but collapses quality_retention to ~0.58;
# weight<0.05 is noisy/near the 0.50 retrieval floor. 0.15 is a principled
# midpoint of the well-behaved, non-saturated low-weight regime where BOTH
# retrieval restoration (min_ratio 0.50-0.80 across the sweep) and quality
# trade-off (retention 0.66-0.84) are real and informative rather than
# saturated. This IS the calibration-tuning value, not the verdict boundary;
# the verdict itself is read off honestly at whatever FULL measures.
BCT_WEIGHT = 0.15

SMOKE_N_TRAIN_B, SMOKE_STEPS, SMOKE_BATCH, SMOKE_N_PROBE = 500, 150, 64, 150
FULL_N_TRAIN_B, FULL_STEPS, FULL_BATCH, FULL_N_PROBE = 6000, 1200, 256, 1000
SEM_N_PAIRS_SMOKE, SEM_N_PAIRS_FULL = 6000, 40000

SAME_CKPT_SANITY_FLOOR = 0.99
RANDOM_CONTROL_CEILING = 0.10
BASELINE_MUST_COLLAPSE_CEILING = 0.50   # NO_BCT arm must be below this (discriminator-fires)
HARD_PASS_RATIO = 0.50                  # WITH_BCT arm target (task's own ">0.5" bar)
NEAR_BASELINE_FLOOR = 0.20               # WITH_BCT below this = "barely helped"
QUALITY_RETENTION_HARD_PASS = 0.80       # WITH_BCT semantic / NO_BCT semantic
QUALITY_RETENTION_FAIL_FLOOR = 0.50

EXPECTED_N_UNITS = 14


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics / arms-must-differ).
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": int(expected_n_units),
        "host": platform.node(),
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
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _arms_must_differ(arms_outputs: Dict[str, torch.Tensor]) -> Dict[str, str]:
    digests: Dict[str, str] = {}
    for name, out in arms_outputs.items():
        arr = out.detach().cpu().contiguous().numpy()
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: arms {a!r} and "
                    f"{b!r} bit-identical (hash={digests[a]})")
    return digests


# ---------------------------------------------------------------------------
# Student architecture (MUST match CKPT_A's architecture exactly).
# ---------------------------------------------------------------------------

class _MLPStudent(torch.nn.Module):
    def __init__(self, in_dim: int, hidden: int, out_dim: int):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden),
            torch.nn.GELU(),
            torch.nn.Linear(hidden, out_dim, bias=False),
        )
        self.out_dim = out_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _make_student(in_dim: int, hidden: int, out_dim: int, seed: int) -> _MLPStudent:
    torch.manual_seed(seed)
    return _MLPStudent(in_dim, hidden, out_dim)


def _block_ste(z: torch.Tensor, kb: int, blk_l: int) -> torch.Tensor:
    """Per-block argmax straight-through: hard one-hot*sign fwd, soft bwd."""
    B = z.shape[0]
    zb = z.reshape(B, kb, blk_l)
    p = torch.softmax(zb.abs() / TAU_GUMBEL, dim=-1)
    hard = torch.zeros_like(p)
    hard.scatter_(-1, p.argmax(dim=-1, keepdim=True), 1.0)
    h_st = hard + p - p.detach()
    sgn = torch.sign(zb)
    sgn = torch.where(sgn == 0, torch.ones_like(sgn), sgn)
    sgn_st = sgn + torch.tanh(zb) - torch.tanh(zb).detach()
    return (h_st * sgn_st).reshape(B, kb * blk_l)


@torch.no_grad()
def _encode_hard_block(student: torch.nn.Module, X: torch.Tensor, kb: int,
                       blk_l: int, batch: int = 4096) -> torch.Tensor:
    out = torch.zeros(X.shape[0], kb * blk_l, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch]).reshape(-1, kb, blk_l)
        o = torch.zeros_like(z)
        idx = z.abs().argmax(dim=-1, keepdim=True)
        sgn = torch.sign(torch.gather(z, -1, idx))
        sgn[sgn == 0] = 1.0
        o.scatter_(-1, idx, sgn)
        out[lo:lo + batch] = o.reshape(-1, kb * blk_l)
    return out


@torch.no_grad()
def _dense_sign_codes(student: torch.nn.Module, X: torch.Tensor,
                      batch: int = 4096) -> torch.Tensor:
    out = torch.zeros(X.shape[0], student.out_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch])
        s = torch.sign(z)
        s[s == 0] = 1.0
        out[lo:lo + batch] = s
    return out


def _random_block_codes(n: int, kb: int, blk_l: int, gen: torch.Generator) -> torch.Tensor:
    z = torch.zeros(n, kb, blk_l, dtype=torch.float32)
    idx = torch.randint(0, blk_l, (n, kb, 1), generator=gen)
    sgn = torch.randint(0, 2, (n, kb, 1), generator=gen).float() * 2 - 1
    z.scatter_(-1, idx, sgn)
    return z.reshape(n, kb * blk_l)


def _normalize(x: torch.Tensor) -> torch.Tensor:
    return x / (x.norm(dim=-1, keepdim=True) + 1e-8)


def _lr_at(step: int, total: int, warmup: int, base_lr: float) -> float:
    if warmup > 0 and step < warmup:
        return base_lr * float(step + 1) / float(warmup)
    denom = max(1, total - warmup)
    prog = float(step - warmup) / float(denom)
    prog = min(1.0, max(0.0, prog))
    return 0.5 * base_lr * (1.0 + math.cos(math.pi * prog))


# ---------------------------------------------------------------------------
# BCT training loop (the new mechanism under test).
# ---------------------------------------------------------------------------

def _train_b(bct_weight: float, X_train: torch.Tensor, A_z_train_norm: torch.Tensor,
            steps: int, batch: int, seed_init: int, batch_gen_seed: int,
            kb: int, blk_l: int, lr: float, arm_name: str, t0: float
            ) -> Tuple[torch.nn.Module, Dict]:
    """Train version-B student. bct_weight=0.0 -> NO_BCT; >0.0 -> WITH_BCT.

    BCT anchor is version A's RAW CONTINUOUS output z_A (normalized), NOT its
    post-quantization block code. Anchoring the continuous direction (the
    standard BCT/L2-migration design, e.g. Shen et al. 2020's influence loss
    on embeddings, not on a discretized readout) pulls student B's underlying
    geometry toward A's, which then improves compatibility of BOTH downstream
    readouts (BLOCK and DENSE) together, rather than over-fitting only the
    coarser block-argmax target. (v1 of this cell anchored the block code
    directly; smoke measured BLOCK cross-ratio recovering to 0.45 but DENSE
    stuck at 0.05 -- confirms block-argmax quantization is too coarse a
    supervision target for full sign-pattern alignment; switched to continuous
    z-anchoring here, re-verified by smoke before FULL dispatch.)

    Paired-trial discipline: seed_init and batch_gen_seed are IDENTICAL across
    both arm calls (only the caller-supplied bct_weight differs), so both arms
    see the exact same init weights and the exact same batch-index sequence.
    l_bct is ALWAYS computed (even at weight 0.0) so the two code paths are
    identical except for the scalar multiply -- reduces arm-implementation-bug
    risk vs branching.
    """
    n, in_dim = X_train.shape
    student = _make_student(in_dim, MLP_HIDDEN, kb * blk_l, seed_init)
    opt = torch.optim.Adam(student.parameters(), lr=lr)
    gen = torch.Generator().manual_seed(batch_gen_seed)
    warmup = max(5, int(round(steps * WARMUP_FRAC)))
    loss_last = rkd_last = bct_last = lr_last = None
    for step in range(steps):
        cur_lr = _lr_at(step, steps, warmup, lr)
        for g in opt.param_groups:
            g["lr"] = cur_lr
        bidx = torch.randint(0, n, (batch,), generator=gen)
        x = X_train[bidx]
        z = student(x)
        code = _block_ste(z, kb, blk_l)
        code_n = _normalize(code)
        T = x @ x.T
        off = ~torch.eye(batch, dtype=torch.bool)
        l_rkd = ((code_n @ code_n.T - T)[off] ** 2).mean()
        z_n = _normalize(z)
        a_batch = A_z_train_norm[bidx]
        l_bct = (1.0 - (z_n * a_batch).sum(-1)).mean()
        loss = l_rkd + bct_weight * l_bct
        if not torch.isfinite(loss):
            raise RuntimeError(
                f"failure_class=NAN_LOSS: arm={arm_name} step={step} "
                f"l_rkd={float(l_rkd.detach())} l_bct={float(l_bct.detach())}")
        opt.zero_grad()
        loss.backward()
        opt.step()
        loss_last = float(loss.detach())
        rkd_last = float(l_rkd.detach())
        bct_last = float(l_bct.detach())
        lr_last = cur_lr
        if step % 200 == 0 or step == steps - 1:
            print(f"[bct] arm={arm_name} step={step}/{steps} rkd={rkd_last:.4f} "
                  f"bct={bct_last:.4f} lr={cur_lr:.2e} "
                  f"({time.perf_counter() - t0:.1f}s)", flush=True)
    student.eval()
    return student, {
        "arm": arm_name, "bct_weight": bct_weight,
        "loss_last": loss_last, "rkd_last": rkd_last, "bct_last": bct_last,
        "lr_last": lr_last, "steps": steps, "batch": batch,
    }


# ---------------------------------------------------------------------------
# Eval: retrieval + semantic-quality metrics.
# ---------------------------------------------------------------------------

@torch.no_grad()
def _top1_retrieval(query_codes: torch.Tensor, index_codes: torch.Tensor) -> float:
    if query_codes.shape != index_codes.shape:
        raise ValueError(
            f"failure_class=SHAPE_MISMATCH: query {tuple(query_codes.shape)} "
            f"vs index {tuple(index_codes.shape)}")
    n = query_codes.shape[0]
    qn = _normalize(query_codes)
    idxn = _normalize(index_codes)
    correct = 0
    chunk = 1024
    for lo in range(0, n, chunk):
        hi = min(lo + chunk, n)
        sims = qn[lo:hi] @ idxn.T
        pred = sims.argmax(dim=1)
        target = torch.arange(lo, hi)
        correct += int((pred == target).sum())
    return correct / n


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def _semantic_spearman(codes: torch.Tensor, X: torch.Tensor, n_pairs: int, seed: int) -> float:
    """Held-out semantic fidelity: spearman(code-cosine, teacher-cosine) over
    random pairs within the probe set (NEVER trained on by any arm)."""
    n = X.shape[0]
    rng = np.random.default_rng(seed)
    i = rng.integers(0, n, n_pairs)
    j = rng.integers(0, n, n_pairs)
    keep = i != j
    i, j = i[keep], j[keep]
    ii = torch.from_numpy(i.copy())
    jj = torch.from_numpy(j.copy())
    tp = (X[ii] * X[jj]).sum(-1).numpy()
    cn = _normalize(codes)
    sp = (cn[ii] * cn[jj]).sum(-1).numpy()
    return _spearman(sp, tp)


# ---------------------------------------------------------------------------
# Self-test (synthetic, no disk artifacts; exercises _train_b directly).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()
    torch.manual_seed(0)

    # (a) retrieval metric sanity (copied convention from the sibling probe).
    def _rand_codes(seed: int, n: int, d: int) -> torch.Tensor:
        g = torch.Generator().manual_seed(seed)
        c = torch.sign(torch.randn(n, d, generator=g))
        c[c == 0] = 1.0
        return c

    codes_a = _rand_codes(1, 300, 64)
    same = _top1_retrieval(codes_a, codes_a)
    if same != 1.0:
        raise AssertionError(f"self-test FAIL: same-codebook retrieval={same} (expected 1.0)")
    codes_b = _rand_codes(2, 300, 64)
    rnd = _top1_retrieval(codes_a, codes_b)
    if rnd >= 0.25:
        raise AssertionError(f"self-test FAIL: independent-random retrieval={rnd:.4f} too high")

    # (b) arms-must-differ helper.
    digests = _arms_must_differ({"a": codes_a, "b": codes_b})
    if digests["a"] == digests["b"]:
        raise AssertionError("self-test FAIL: arms_must_differ digests collided")
    raised = False
    try:
        _arms_must_differ({"a": codes_a, "a_dup": codes_a.clone()})
    except RuntimeError:
        raised = True
    if not raised:
        raise AssertionError("self-test FAIL: arms_must_differ did not raise on identical arms")

    # (c) block_ste roundtrip: hard-encode/decode of its own output must be
    # self-consistent (each block picks exactly one +-1 slot).
    kb_t, blk_l_t = 8, 4
    z = torch.randn(50, kb_t * blk_l_t)
    code = _block_ste(z, kb_t, blk_l_t).reshape(50, kb_t, blk_l_t)
    nnz_per_block = (code != 0).sum(dim=-1)
    if not torch.all(nnz_per_block == 1):
        raise AssertionError("self-test FAIL: block_ste did not produce exactly one nonzero per block")

    # (d) CORE MECHANISM self-test: synthetic teacher space, frozen "A" codes,
    # train tiny "B" student twice (bct_weight=0 vs high) via the REAL _train_b
    # function. WITH_BCT must recover cross-version retrieval far above NO_BCT.
    n_concepts, in_dim, hidden = 400, 16, 64
    kb_s, blk_l_s = 16, 8   # out_dim=128, large enough code space to avoid
    out_dim = kb_s * blk_l_s  # spurious self-retrieval collisions at n_probe=100
    gx = torch.Generator().manual_seed(7)
    X = torch.randn(n_concepts, in_dim, generator=gx)
    X = _normalize(X)
    student_a = _make_student(in_dim, hidden, out_dim, seed=99)
    with torch.no_grad():
        A_codes_all = _normalize(_encode_hard_block(student_a, X, kb_s, blk_l_s))
        A_z_all = _normalize(student_a(X))

    train_idx = torch.arange(0, 300)
    probe_idx = torch.arange(300, 400)
    X_train = X[train_idx]
    A_z_train_norm = A_z_all[train_idx]
    A_probe_norm = A_codes_all[probe_idx]

    student_no, _ = _train_b(0.0, X_train, A_z_train_norm, steps=120, batch=32,
                             seed_init=13, batch_gen_seed=4242, kb=kb_s,
                             blk_l=blk_l_s, lr=1e-2, arm_name="ST_NO_BCT", t0=t0)
    student_with, _ = _train_b(8.0, X_train, A_z_train_norm, steps=120, batch=32,
                               seed_init=13, batch_gen_seed=4242, kb=kb_s,
                               blk_l=blk_l_s, lr=1e-2, arm_name="ST_WITH_BCT", t0=t0)

    with torch.no_grad():
        B_no_probe = _normalize(_encode_hard_block(student_no, X[probe_idx], kb_s, blk_l_s))
        B_with_probe = _normalize(_encode_hard_block(student_with, X[probe_idx], kb_s, blk_l_s))

    same_a = _top1_retrieval(A_probe_norm, A_probe_norm)
    if same_a < 0.99:
        raise AssertionError(f"self-test FAIL: synthetic SAME_A={same_a:.4f} < 0.99")
    cross_no = _top1_retrieval(B_no_probe, A_probe_norm)
    cross_with = _top1_retrieval(B_with_probe, A_probe_norm)
    ratio_no = cross_no / same_a
    ratio_with = cross_with / same_a
    if not (ratio_with >= 0.5 and ratio_with > ratio_no + 0.2):
        raise AssertionError(
            f"self-test FAIL: BCT mechanism did not restore synthetic cross-"
            f"retrieval (ratio_no={ratio_no:.4f} ratio_with={ratio_with:.4f}); "
            f"the core loss/training logic is broken, not just tuning")

    elapsed = time.perf_counter() - t0
    print(f"[selftest] PASS same={same:.4f} random={rnd:.4f} block_ste_ok=True "
          f"synthetic_ratio_no={ratio_no:.4f} synthetic_ratio_with={ratio_with:.4f} "
          f"({elapsed:.2f}s)", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Real-checkpoint / real-teacher run.
# ---------------------------------------------------------------------------

def _load_teacher() -> Tuple[torch.Tensor, List[str]]:
    cache_path = _CACHE_DIR / TEACHER_CACHE_NAME
    if not cache_path.exists():
        raise FileNotFoundError(
            f"failure_class=TEACHER_CACHE_MISSING: {cache_path} (explicit-SCP "
            f"required if this is the remote box; NOT a 'largest file' pick)")
    d = np.load(str(cache_path), allow_pickle=False)
    if "semantic" not in d or "id_order_json" not in d:
        raise ValueError(f"failure_class=TEACHER_CACHE_SCHEMA: {cache_path.name} "
                         f"missing semantic/id_order_json keys: {list(d.keys())}")
    sem = d["semantic"]
    ids = json.loads(str(d["id_order_json"]))
    if sem.shape[0] != len(ids):
        raise ValueError(f"failure_class=TEACHER_CACHE_ROW_MISMATCH: "
                         f"{sem.shape[0]} vs {len(ids)}")
    if np.isnan(sem).any() or np.isinf(sem).any():
        raise ValueError("failure_class=TEACHER_CACHE_NAN")
    X = torch.from_numpy(np.ascontiguousarray(sem)).float()
    return _normalize(X), ids


def run_probe(run_mode: str, seed: int, out_dir: Path) -> int:
    expected_units = EXPECTED_N_UNITS
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[bct] run_mode={run_mode} seed={seed} ckpt_a={CKPT_A}", flush=True)

    X, ids = _load_teacher()
    V_cache = X.shape[0]
    in_dim = X.shape[1]
    print(f"[bct] teacher {TEACHER_CACHE_NAME}: {V_cache} concepts x {in_dim}d "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(SPLIT_SEED)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * HELD_FRAC)), MID_HELD_CAP)
    n_tr = V_cache - n_he
    if (n_tr, n_he) != EXPECTED_MID_SPLIT:
        raise RuntimeError(
            f"failure_class=SPLIT_MISMATCH: expected {EXPECTED_MID_SPLIT}, got "
            f"({n_tr}, {n_he}); teacher cache is not the exact file A trained "
            f"against, or V_cache drifted")
    tr_idx = perm[:n_tr]
    he_idx = perm[n_tr:n_tr + n_he]
    print(f"[bct] split reproduced: n_tr={n_tr} n_he={n_he} (matches A's "
          f"training split)", flush=True)

    if run_mode == "smoke":
        n_train_b, steps, batch, n_probe = (SMOKE_N_TRAIN_B, SMOKE_STEPS,
                                            SMOKE_BATCH, SMOKE_N_PROBE)
        n_sem_pairs = SEM_N_PAIRS_SMOKE
    else:
        n_train_b, steps, batch, n_probe = (FULL_N_TRAIN_B, FULL_STEPS,
                                            FULL_BATCH, FULL_N_PROBE)
        n_sem_pairs = SEM_N_PAIRS_FULL

    r_train = np.random.default_rng(TRAIN_SUBSAMPLE_SEED)
    train_b_idx = r_train.choice(tr_idx, size=min(n_train_b, len(tr_idx)), replace=False)
    r_probe = np.random.default_rng(PROBE_SEED)
    probe_idx = r_probe.choice(he_idx, size=min(n_probe, len(he_idx)), replace=False)
    X_train = X[torch.from_numpy(train_b_idx.copy())].contiguous()
    X_probe = X[torch.from_numpy(probe_idx.copy())].contiguous()
    print(f"[bct] N_TRAIN_B={X_train.shape[0]} N_PROBE={X_probe.shape[0]} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- load frozen version A ---------------------------------------------
    if not CKPT_A.exists():
        raise FileNotFoundError(
            f"failure_class=CHECKPOINT_MISSING: {CKPT_A} (explicit-SCP required "
            f"if this is the remote box)")
    student_a = _MLPStudent(in_dim, MLP_HIDDEN, N_DIM)
    ckpt = torch.load(str(CKPT_A), map_location="cpu")
    load_result = student_a.load_state_dict(ckpt["student"])
    if load_result.missing_keys or load_result.unexpected_keys:
        raise RuntimeError(
            f"failure_class=STATE_DICT_MISMATCH: missing={load_result.missing_keys} "
            f"unexpected={load_result.unexpected_keys}")
    student_a.eval()
    print(f"[bct] loaded version A (ckpt_step={ckpt.get('step')}) "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    with torch.no_grad():
        A_z_train_norm = _normalize(student_a(X_train))
        A_probe_block_norm = _normalize(_encode_hard_block(student_a, X_probe, K_BLOCKS, BLK_L))
        A_probe_dense_norm = _normalize(_dense_sign_codes(student_a, X_probe))
    print(f"[bct] encoded A over train+probe ({time.perf_counter() - t0:.1f}s)", flush=True)

    # --- train version B, paired arms ---------------------------------------
    warmup = max(5, int(round(steps * WARMUP_FRAC)))
    student_no, train_diag_no = _train_b(
        0.0, X_train, A_z_train_norm, steps, batch, B_INIT_SEED,
        BATCH_GEN_SEED, K_BLOCKS, BLK_L, LR, "NO_BCT", t0)
    student_with, train_diag_with = _train_b(
        BCT_WEIGHT, X_train, A_z_train_norm, steps, batch, B_INIT_SEED,
        BATCH_GEN_SEED, K_BLOCKS, BLK_L, LR, "WITH_BCT", t0)

    with torch.no_grad():
        B_probe_block = {
            "NO_BCT": _normalize(_encode_hard_block(student_no, X_probe, K_BLOCKS, BLK_L)),
            "WITH_BCT": _normalize(_encode_hard_block(student_with, X_probe, K_BLOCKS, BLK_L)),
        }
        B_probe_dense = {
            "NO_BCT": _normalize(_dense_sign_codes(student_no, X_probe)),
            "WITH_BCT": _normalize(_dense_sign_codes(student_with, X_probe)),
        }

    gen_r1 = torch.Generator().manual_seed(RAND_CTRL_SEED_1)
    gen_r2 = torch.Generator().manual_seed(RAND_CTRL_SEED_2)
    rand_dense_1 = torch.sign(torch.randn(X_probe.shape[0], N_DIM, generator=gen_r1))
    rand_dense_1[rand_dense_1 == 0] = 1.0
    rand_dense_2 = torch.sign(torch.randn(X_probe.shape[0], N_DIM, generator=gen_r2))
    rand_dense_2[rand_dense_2 == 0] = 1.0
    rand_block_1 = _random_block_codes(X_probe.shape[0], K_BLOCKS, BLK_L, gen_r1)
    rand_block_2 = _random_block_codes(X_probe.shape[0], K_BLOCKS, BLK_L, gen_r2)

    digests = _arms_must_differ({
        "A_block": A_probe_block_norm, "A_dense": A_probe_dense_norm,
        "B_block_NO_BCT": B_probe_block["NO_BCT"], "B_block_WITH_BCT": B_probe_block["WITH_BCT"],
        "B_dense_NO_BCT": B_probe_dense["NO_BCT"], "B_dense_WITH_BCT": B_probe_dense["WITH_BCT"],
    })

    units: List[Dict] = []

    def _unit(name: str, query: torch.Tensor, index: torch.Tensor) -> float:
        acc = _top1_retrieval(query, index)
        units.append({"unit": name, "top1_retrieval": acc, "n": query.shape[0]})
        print(f"[bct] unit {name}: top1_retrieval={acc:.4f}", flush=True)
        return acc

    same_a_block = _unit("SAME_A_BLOCK", A_probe_block_norm, A_probe_block_norm)
    same_a_dense = _unit("SAME_A_DENSE", A_probe_dense_norm, A_probe_dense_norm)

    same_b: Dict[str, Dict[str, float]] = {}
    cross: Dict[str, Dict[str, float]] = {}
    for arm in ("NO_BCT", "WITH_BCT"):
        same_b.setdefault(arm, {})["block"] = _unit(
            f"SAME_B_{arm}_BLOCK", B_probe_block[arm], B_probe_block[arm])
        same_b[arm]["dense"] = _unit(
            f"SAME_B_{arm}_DENSE", B_probe_dense[arm], B_probe_dense[arm])
        cross.setdefault(arm, {})["block"] = _unit(
            f"CROSS_AIDX_BQUERY_{arm}_BLOCK", B_probe_block[arm], A_probe_block_norm)
        cross[arm]["dense"] = _unit(
            f"CROSS_AIDX_BQUERY_{arm}_DENSE", B_probe_dense[arm], A_probe_dense_norm)

    random_dense = _unit("RANDOM_CONTROL_DENSE", rand_dense_1, rand_dense_2)
    random_block = _unit("RANDOM_CONTROL_BLOCK", rand_block_1, rand_block_2)

    semantic: Dict[str, float] = {}
    for arm, student in (("NO_BCT", student_no), ("WITH_BCT", student_with)):
        sp = _semantic_spearman(B_probe_dense[arm], X_probe, n_sem_pairs, SEM_PAIR_SEED)
        semantic[arm] = sp
        units.append({"unit": f"SEMANTIC_SPEARMAN_{arm}_DENSE", "spearman": sp,
                      "n_probe": X_probe.shape[0]})
        print(f"[bct] unit SEMANTIC_SPEARMAN_{arm}_DENSE: spearman={sp:.4f}", flush=True)

    # --- integrity / discriminator-fires hard asserts -----------------------
    for name, v in [("SAME_A_BLOCK", same_a_block), ("SAME_A_DENSE", same_a_dense),
                    ("SAME_B_NO_BCT_BLOCK", same_b["NO_BCT"]["block"]),
                    ("SAME_B_NO_BCT_DENSE", same_b["NO_BCT"]["dense"]),
                    ("SAME_B_WITH_BCT_BLOCK", same_b["WITH_BCT"]["block"]),
                    ("SAME_B_WITH_BCT_DENSE", same_b["WITH_BCT"]["dense"])]:
        if v < SAME_CKPT_SANITY_FLOOR:
            raise RuntimeError(
                f"failure_class=SAME_CHECKPOINT_SANITY_FAIL: {name}={v:.4f} < "
                f"{SAME_CKPT_SANITY_FLOOR}")
    for name, v in [("RANDOM_CONTROL_DENSE", random_dense), ("RANDOM_CONTROL_BLOCK", random_block)]:
        if v > RANDOM_CONTROL_CEILING:
            raise RuntimeError(
                f"failure_class=RANDOM_CONTROL_TOO_HIGH: {name}={v:.4f} > "
                f"{RANDOM_CONTROL_CEILING}")

    ratios = {
        "NO_BCT_block": cross["NO_BCT"]["block"] / same_a_block,
        "NO_BCT_dense": cross["NO_BCT"]["dense"] / same_a_dense,
        "WITH_BCT_block": cross["WITH_BCT"]["block"] / same_a_block,
        "WITH_BCT_dense": cross["WITH_BCT"]["dense"] / same_a_dense,
    }
    min_ratio_no = min(ratios["NO_BCT_block"], ratios["NO_BCT_dense"])
    min_ratio_with = min(ratios["WITH_BCT_block"], ratios["WITH_BCT_dense"])
    quality_no = semantic["NO_BCT"]
    quality_with = semantic["WITH_BCT"]
    quality_retention = (quality_with / quality_no) if quality_no > 1e-6 else float("nan")

    tail = (f"[min_ratio_no={min_ratio_no:.4f} min_ratio_with={min_ratio_with:.4f} "
           f"quality_no={quality_no:.4f} quality_with={quality_with:.4f} "
           f"retention={quality_retention:.4f}]")

    if min_ratio_no >= BASELINE_MUST_COLLAPSE_CEILING:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"DISCRIMINATOR_DID_NOT_FIRE: NO_BCT baseline did not "
                       f"collapse at this reduced CPU scale (min_ratio_no="
                       f"{min_ratio_no:.4f} >= {BASELINE_MUST_COLLAPSE_CEILING}); "
                       f"cannot evaluate whether BCT restores what is not broken; "
                       f"needs more divergent B init/objective/scale to reproduce "
                       f"the collapse regime {tail}")
    elif min_ratio_with >= HARD_PASS_RATIO and quality_retention >= QUALITY_RETENTION_HARD_PASS:
        verdict = "HARD_PASS"
        verdict_msg = (f"BCT loss restores cross-version retrieval from collapse "
                       f"(NO_BCT min_ratio={min_ratio_no:.4f}) to usable (WITH_BCT "
                       f"min_ratio={min_ratio_with:.4f} >= {HARD_PASS_RATIO}) while "
                       f"retaining {quality_retention*100:.1f}% of NO_BCT's held-out "
                       f"semantic quality {tail}")
    elif min_ratio_with < NEAR_BASELINE_FLOOR:
        verdict = "HARD_FAIL"
        verdict_msg = (f"BCT loss at weight={BCT_WEIGHT} did NOT meaningfully "
                       f"restore cross-version retrieval (WITH_BCT min_ratio="
                       f"{min_ratio_with:.4f} still near NO_BCT baseline "
                       f"{min_ratio_no:.4f}); needs higher bct_weight or a "
                       f"different anchoring mechanism {tail}")
    elif quality_retention < QUALITY_RETENTION_FAIL_FLOOR:
        verdict = "HARD_FAIL"
        verdict_msg = (f"BCT loss restores retrieval (WITH_BCT min_ratio="
                       f"{min_ratio_with:.4f}) but at severe same-version quality "
                       f"cost (retention={quality_retention:.4f} < "
                       f"{QUALITY_RETENTION_FAIL_FLOOR}); not a usable trade {tail}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"BCT loss partially restores cross-version retrieval "
                       f"(WITH_BCT min_ratio={min_ratio_with:.4f} vs NO_BCT "
                       f"{min_ratio_no:.4f}) and/or partially trades off quality "
                       f"(retention={quality_retention:.4f}); real but not clean {tail}")

    cardinality_ok = len(units) == expected_units
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {len(units)} "
                       f"units != expected {expected_units}")

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": seed,
        "n_train_b": int(X_train.shape[0]),
        "n_probe": int(X_probe.shape[0]),
        "bct_weight": BCT_WEIGHT,
        "steps": steps, "batch": batch,
        "ckpt_a_path": str(CKPT_A), "ckpt_a_step": ckpt.get("step"),
        "teacher_cache": TEACHER_CACHE_NAME,
        "per_unit": units,
        "ratios": ratios,
        "min_ratio_no_bct": min_ratio_no,
        "min_ratio_with_bct": min_ratio_with,
        "semantic_spearman": semantic,
        "quality_retention_with_bct": quality_retention,
        "hard_pass_ratio_threshold": HARD_PASS_RATIO,
        "baseline_must_collapse_ceiling": BASELINE_MUST_COLLAPSE_CEILING,
        "quality_retention_hard_pass": QUALITY_RETENTION_HARD_PASS,
        "quality_retention_fail_floor": QUALITY_RETENTION_FAIL_FLOOR,
        "train_diag_no_bct": train_diag_no,
        "train_diag_with_bct": train_diag_with,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "arms_differ_verified": True,
        "arm_digests": digests,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    print(f"[bct] wrote {out_dir / 'metrics.json'} verdict={verdict} "
          f"({elapsed:.1f}s)", flush=True)
    return 0


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SPLIT_SEED)
    return p


def _resolve_run_mode(args: argparse.Namespace) -> str:
    if args.self_test:
        return "self_test"
    if args.full:
        return "full"
    if args.smoke:
        return "smoke"
    return args.run_mode


def main() -> int:
    p = build_argparser()
    args = p.parse_args()
    run_mode = _resolve_run_mode(args)
    if run_mode == "self_test":
        return run_self_test()
    # this cell's terminal CPU-scale tier is literally named "full" already
    # (no internal "mid" tier to alias runner-injected full -> ); no aliasing
    # needed, but documented per the dispatch contract's alias requirement.
    anchor = ANCHOR_NAME if run_mode == "full" else f"{ANCHOR_NAME}_{run_mode}"
    out_dir = get_output_dir(anchor)
    try:
        return run_probe(run_mode, args.seed, out_dir)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    sys.exit(main())
