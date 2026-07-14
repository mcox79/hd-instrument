"""STRUCTURE_DISCOVERY_SHARED_CODE_READOUT: does the shared-code + compositional-similarity-readout architecture
LEARN compositional structure from data (plain cross-entropy, NO hand-designed algebra, NO homomorphism regularizer)
and GENERALIZE to genuinely-novel (A,B) combinations -- and does it do so ACROSS MULTIPLE structure families, not
just modular addition?

WHY THIS CELL (the open problem): the prior conjunction cell
(exp_conjunction_native_bind_vs_homophily_cskg_v1) was a CONSTRUCTION_PROOF -- it HAND-DESIGNED the FPE phasor
algebra (bind(code[a],code[b]) = code[(a+b)%L] BY CONSTRUCTION) and measured that the native bind beats frequency.
It never tested whether the algebra could be DISCOVERED from data for real content. An inline Director prototype
found a strong hint: put A, B, and the ANSWER in a SHARED learnable code table (one complex64 phasor code per value),
read out by comparing bind(E[a],E[b]) to E[answer] via a compositional similarity readout
(logits[r] = Re<bind(E[a],E[b]), E[r]>), train with plain CE. On additive R=(A+B)%L: novel-pair acc = 0.789 (>>chance
0.042) vs 0.11 for a SEPARATE-tables (memorize) architecture; on an ARBITRARY random-table rule: 0.032 (= chance) --
the must-fail that proves GENUINE DISCOVERY not memorization/leak. THIS CELL confirms or refutes that, rigorously, at
scale, across multiple structure families.

WHAT IS MEASURED: the KEY CLAIM = discovery succeeds iff genuine compositional structure exists that is COMPATIBLE
WITH THE BIND'S OWN ALGEBRA (complex elementwise mul = commutative abelian-group convolution in the dual), across
MULTIPLE structure families, and FAILS (to chance) when the composition is arbitrary. The honest expected BOUND
(pre-registered): the elementwise-complex-mul bind is COMMUTATIVE, so the shared-code symmetric readout can only
discover structure isomorphic to a COMMUTATIVE (abelian) group operation. Two DISTINCT abelian families
(cyclic add Z_L and bitwise XOR (Z_2)^k) test not-a-fluke-of-modular-addition. An ASYMMETRIC linear form
(c1*A + c2*B, c1!=c2) is the CLAIM-BOUNDING family (predicted: discovery bounded/fails, because a symmetric readout
cannot represent an asymmetric function). An ARBITRARY random table is the MUST-FAIL control (predicted: chance).

## STRUCTURE FAMILIES (the discriminating axis; all scored PAIRED on the SAME held-out novel (A,B) pairs)
  F1 CYCLIC   : R = (A + B) mod L                 [abelian Z_L; DISCOVERABLE predicted]
  F2 XOR      : R = A xor B  (L a power of 2)      [abelian (Z_2)^k; DISTINCT family; DISCOVERABLE predicted]
  F3 ASYM     : R = (c1*A + c2*B) mod L, c1!=c2    [NON-symmetric; CLAIM-BOUNDING (symmetric bind cannot represent)]
  F4 ARBITRARY: R = T[A,B], T a FIXED RANDOM table [NON-compositional; MUST-FAIL: novel unlearnable -> chance]
  (F1 also run as F1_NOISY: fraction eps of TRAIN labels flipped to random -> label-noise robustness of discovery.)

## ARCHITECTURE ARMS (per family; novel-pair top-1 acc is the headline; chance = 1/L)
  DISCOVERY = SHARED learnable complex64 unit-phasor code table E (one code per value); readout
              logits[r] = Re<bind(E[a],E[b]), E[r]> using the REAL substrate FHRR bind (hdlab.binding.bind); trained
              with plain cross-entropy, NO hand-designed algebra, NO homomorphism regularizer. THE headline mechanism.
  MEMORIZE  = SEPARATE learnable real tables Ea, Eb + concat -> MLP -> logits over R (no shared code, no bind). The
              architecture contrast: memorizes seen pairs, has NO compositional prior. OVER-parameterized vs DISCOVERY
              (params_MEMORIZE >= params_DISCOVERY) so it cannot be dismissed as underpowered.
  FPE       = HAND-DESIGNED fixed matched phasor codes (construction-proof ceiling): F1 additive-FPE, F2 XOR-character
              code (both EXACT homomorphisms under the bind); F3/F4 additive-default (diagnostic, predicted low). NOT
              trained. Shows what the algebra achieves when hand-built -> the DISCOVERY-vs-FPE gap = optimization gap.
  FREQ_NULL = strongest non-learning null: score(y)=count_train(a'==a,y)+count_train(b'==b,y) (conditional frequency).
              MUST fail on compositional novel (no conditional support for unseen combos).
  ORACLE    = learner info-ceiling: deterministic rule -> 1.0 achievable (F1/F2/F3); ARBITRARY held-out is
              information-theoretically independent of train -> ceiling = chance (1/L). Bounds every arm; the verdict
              never celebrates sub-ceiling.

## PRE-REGISTERED BANDS (NOVEL stratum, top-1 accuracy; chance = 1/L; NOT tuned on data)
HARD_PASS (the architecture GENUINELY DISCOVERS compositional structure across families) -- require ALL:
  HP1  DISCOVERY novel-acc >= HP_DISC_ABS (0.50) on F1 CYCLIC AND on F2 XOR   [absolute discovery, >=2 abelian families]
  HP2  DISCOVERY novel-acc - MEMORIZE novel-acc >= HP_ARCH_ADV (0.25) on F1 AND F2   [architecture advantage]
  HP3  F4 ARBITRARY DISCOVERY novel-acc <= chance + MUSTFAIL_TOL (0.05)   [must-fail: no generalization w/o structure]
  HP4  FREQ_NULL novel-acc <= HP_NULL_FAILS (0.20) on F1 AND F2   [null genuinely fails on compositional novel]
HARD_FAIL / REFUTE (the architecture does NOT discover structure -- report STRAIGHT) -- ANY:
  RF1  DISCOVERY novel-acc - MEMORIZE novel-acc <= REFUTE_TOL (0.10) on F1   [no architecture advantage -> refuted]
  RF2  (INTEGRITY, dominates) F4 ARBITRARY DISCOVERY novel-acc >= chance + INTEGRITY_BREACH (0.15)   [it "generalizes"
       on a RANDOM table -> leak/cheat -> the whole benchmark is INVALID]
MIDDLE_BAND: anything else -- e.g. discovery beats memorize but modestly, OR works on F1 (additive) but not F2 (XOR)
  => additive-only, claim bounded; OR F2 works F1 does not; etc. F3 ASYM is NOT a pass/fail gate -- it is the
  CLAIM-BOUNDING diagnostic (predicted bounded: symmetric commutative bind cannot represent an asymmetric linear form;
  if DISCOVERY unexpectedly solves F3 the architecture is MORE general than commutative -> report as a finding).

## Compute architecture
class (c) mixed / sequential-CPU, JUSTIFIED: small full-batch SGD fits (train ~ coverage*L^2 rows ~1200 at FULL;
readout is one batched (B,d) elementwise bind + one (B,d)@(d,L) matmul per step -- BATCHED tensors, NOT a python loop
over pairs, per the GPU-batching rule; matmuls are tiny so GPU launch overhead would dominate -> CPU is correct).
Families x seeds x arms iterate sequentially; each fit is internally vectorized. Total FULL wall < ~10 min CPU.
Storage strategy: no_storage (no bundling; per-value SHARDED codes -- each value its own vector by construction).

## final_metrics_atomicity: tmp_replace (write_metrics uses os.replace; crash-metrics atomic).
## progress_logging: print_flush_true (line-buffered stdout + per-family/per-seed flush prints + heartbeat).
## cell_chunked: false (single-file; seeds run in a per-seed try/except loop with per-seed partials + cardinality gate).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over per-family arm predictions)
# - final_metrics_atomicity: tmp_replace (write_metrics os.replace; crash-metrics atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discrete argmax over L classes; chance=1/L is the only floor; HARD_PASS(0.50) >> chance(0.0156 at L=64)
#   and << oracle(1.0) so reachable; capacity feasibility = FPE hand-design achieves ~1.0 -> the band is attainable.
# - baseline_in_band at smoke (META_RULE_AG; MEMORIZE novel in (chance, 0.95); DISCOVERY not saturated at chance)
# - discriminator survives scale: self-test at tiny L fires the DISCOVERY-vs-MEMORIZE gap AND the arbitrary must-fail;
#   FULL L=64 keeps chance tiny (0.0156) so the >>chance discovery signal cannot be a small-L saturation artifact.
# - HARD_PASS strictly above floor + margin (0.50 abs, 0.25 arch-adv; well above chance and above smoke-observed noise)
# - HP_SCOPE: {DISCOVERY: [HP1,HP2,HP3], MEMORIZE: [HP2 as the contrast baseline, RF1], FREQ_NULL: [HP4],
#   FPE: [ceiling reference only -- no pass/fail gate], ORACLE: [ceiling reference only], F3_ASYM: [diagnostic only]}
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (per-seed cardinality gate; families x arms are inner-fixed per seed)
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded)
# - calibration_check: default_ok_for_this_regime (bands are absolute accuracy vs chance, not primitive-inherited)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - §15-F self-test CONSTRUCTS the REAL substrate bind (hdlab.binding.bind) INSIDE the DISCOVERY gradient loop at
#   tiny scale (real_code_path); substrate_signature binds hd_bind against its live signature
# - §15-F guard_baseline: n/a (no control-beats-baseline break-guard; MEMORIZE is a fair over-parameterized contrast)

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from hdlab.binding import bind as hd_bind  # noqa: E402  # the REAL substrate FHRR bind (complex64 elementwise mul)

ANCHOR_NAME = "structure_discovery_shared_code_readout_v1"

# ---- structure families ----
F_CYCLIC = "F1_CYCLIC"
F_XOR = "F2_XOR"
F_ASYM = "F3_ASYM"
F_ARB = "F4_ARBITRARY"
F_NOISY = "F1_NOISY"
FAMILIES = [F_CYCLIC, F_XOR, F_ASYM, F_ARB, F_NOISY]
ABELIAN_FAMILIES = [F_CYCLIC, F_XOR]      # the two DISTINCT abelian families the HARD_PASS requires

# ---- arms ----
DISC = "DISCOVERY"
MEMO = "MEMORIZE"
FPE = "FPE"
FREQ = "FREQ_NULL"
ORC = "ORACLE"
ARMS = [DISC, MEMO, FPE, FREQ, ORC]

# ---- CITED prototype (the inline Director finding this cell confirms/refutes) ----
CITED_PROTO_DISC_ADD = 0.789   # CITED@Director inline prototype scratchpad/homomorphism_reg.py (additive novel acc)
CITED_PROTO_MEMO_ADD = 0.11    # CITED@ same (separate-tables memorize novel acc)
CITED_PROTO_DISC_ARB = 0.032   # CITED@ same (arbitrary-rule novel acc ~ chance)

# ---- PRE-REGISTERED bands (NOVEL stratum, top-1 acc; chance=1/L; NOT tuned on data) ----
HP_DISC_ABS = 0.50        # HP1: DISCOVERY novel-acc >= this on F1 AND F2
HP_ARCH_ADV = 0.25        # HP2: DISCOVERY - MEMORIZE novel-acc >= this on F1 AND F2
MUSTFAIL_TOL = 0.05       # HP3: F4 DISCOVERY novel-acc <= chance + this
HP_NULL_FAILS = 0.20      # HP4: FREQ_NULL novel-acc <= this on F1 AND F2
REFUTE_TOL = 0.10         # RF1: DISCOVERY - MEMORIZE novel-acc <= this on F1 -> refuted
INTEGRITY_BREACH = 0.15   # RF2: F4 DISCOVERY novel-acc >= chance + this -> leak/invalid

# ---- self-test planted thresholds (calibrated on the tiny synthetic self-test scale; see calibration run) ----
ST_DISC_ABS = 0.35        # DISCOVERY F1 novel-acc >= this at tiny scale (>> chance 1/16=0.0625; conservative)
ST_ARCH_ADV = 0.18        # DISCOVERY - MEMORIZE novel-acc >= this on F1 (discriminator FIRES)
ST_ARB_MUSTFAIL = 0.12    # F4 DISCOVERY novel-acc - chance <= this (must-fail fires)
ST_FPE_ADD = 0.95         # FPE additive homomorphism F1 novel-acc >= this (hand-design is near-exact)

# Config profiles. SELFTEST / MEMSMOKE / FULL exercise the SAME split->train->arms->verdict path.
SELFTEST_CFG = dict(L=16, n_dim=48, coverage=0.60, steps=400, disc_lr=0.05, memo_h=48, memo_lr=0.01,
                    noise_eps=0.15, c1=1, c2=2, seeds=[7], min_novel=20)
MEMSMOKE_CFG = dict(L=32, n_dim=128, coverage=0.40, steps=900, disc_lr=0.05, memo_h=96, memo_lr=0.01,
                    noise_eps=0.15, c1=1, c2=2, seeds=[7], min_novel=80)
FULL_CFG = dict(L=64, n_dim=256, coverage=0.30, steps=1600, disc_lr=0.05, memo_h=160, memo_lr=0.01,
                noise_eps=0.15, c1=1, c2=2, seeds=[7, 13, 17], min_novel=300)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Rules + splits.
# ---------------------------------------------------------------------------

def _is_pow2(n):
    return n > 0 and (n & (n - 1)) == 0


def build_arbitrary_table(L, seed):
    """Fixed random table T (L,L) -> Z_L. Deterministic per seed. NON-compositional (no held-out generalization)."""
    g = np.random.default_rng(seed * 100003 + 991)
    return g.integers(0, L, size=(L, L)).astype(np.int64)


def rule_answer(a, b, family, L, c1, c2, arb_table):
    """Deterministic answer R for a pair (a,b) under the given structure family."""
    if family in (F_CYCLIC, F_NOISY):
        return (a + b) % L
    if family == F_XOR:
        return (a ^ b) % L
    if family == F_ASYM:
        return (c1 * a + c2 * b) % L
    if family == F_ARB:
        return int(arb_table[a, b])
    raise ValueError("unknown family %s" % family)


def make_split(L, coverage, seed, min_novel, family, c1, c2, arb_table, noise_eps):
    """Split all L*L (a,b) pairs into TRAIN (coverage fraction) and NOVEL (held-out, never in train).

    Returns dict with train/novel a,b,y arrays + seen (a subset of train pairs re-used as a positive fit-check
    stratum). Verifies every value 0..L-1 appears in TRAIN as an A, as a B, and as an answer R (so every code gets
    gradient). NOISY family flips a fraction noise_eps of TRAIN labels to a uniform-random class (test labels clean).
    Determinism: seeded rng permutation; NO python-set-hash nondeterminism (indices are sorted arrays)."""
    g = np.random.default_rng(seed * 100003 + 7)
    all_pairs = np.array([(a, b) for a in range(L) for b in range(L)], dtype=np.int64)  # (L*L, 2), row-major stable
    n = all_pairs.shape[0]
    perm = g.permutation(n)
    n_train = int(round(coverage * n))
    n_train = max(n_train, 2 * L)                 # ensure enough coverage for every-value-present
    tr_idx = np.sort(perm[:n_train])
    nv_idx = np.sort(perm[n_train:])
    tr = all_pairs[tr_idx]
    nv = all_pairs[nv_idx]

    a_tr, b_tr = tr[:, 0], tr[:, 1]
    a_nv, b_nv = nv[:, 0], nv[:, 1]
    y_tr = np.array([rule_answer(int(a), int(b), family, L, c1, c2, arb_table) for a, b in zip(a_tr, b_tr)],
                    dtype=np.int64)
    y_nv = np.array([rule_answer(int(a), int(b), family, L, c1, c2, arb_table) for a, b in zip(a_nv, b_nv)],
                    dtype=np.int64)

    # every-value-present audit (codes must be trainable)
    vals_a = set(int(x) for x in a_tr)
    vals_b = set(int(x) for x in b_tr)
    vals_y = set(int(x) for x in y_tr)
    missing_a = sorted(set(range(L)) - vals_a)
    missing_b = sorted(set(range(L)) - vals_b)
    missing_y = sorted(set(range(L)) - vals_y)

    # LEAK CHECK: no novel pair appears in train (by construction of the disjoint index split; assert it)
    tr_set = set((int(a), int(b)) for a, b in tr)
    leaked = [(int(a), int(b)) for a, b in nv if (int(a), int(b)) in tr_set]

    # NOISY: flip fraction of TRAIN labels to a uniform-random class (test/novel labels stay clean)
    y_tr_noisy = y_tr.copy()
    n_flipped = 0
    if family == F_NOISY and noise_eps > 0.0:
        gflip = np.random.default_rng(seed * 100003 + 555)
        flip_mask = gflip.random(y_tr.shape[0]) < noise_eps
        y_tr_noisy[flip_mask] = gflip.integers(0, L, size=int(flip_mask.sum()))
        n_flipped = int(flip_mask.sum())

    # SEEN stratum = a bounded sample of train pairs (fit-check that arms actually fit training)
    n_seen = min(len(a_tr), 500)
    seen_sel = np.sort(g.permutation(len(a_tr))[:n_seen])

    return dict(
        a_tr=a_tr, b_tr=b_tr, y_tr=y_tr, y_tr_train=y_tr_noisy,   # y_tr_train is what arms train on (noisy for F_NOISY)
        a_nv=a_nv, b_nv=b_nv, y_nv=y_nv,
        seen_a=a_tr[seen_sel], seen_b=b_tr[seen_sel], seen_y=y_tr[seen_sel],
        n_train=int(len(a_tr)), n_novel=int(len(a_nv)), n_seen=int(n_seen),
        missing_a=missing_a, missing_b=missing_b, missing_y=missing_y,
        leaked=leaked, n_flipped=n_flipped, min_novel=min_novel,
    )


# ---------------------------------------------------------------------------
# Codebooks (hand-designed FPE ceiling) + the compositional similarity readout.
# ---------------------------------------------------------------------------

def build_matched_fpe(family, L, n_dim, seed):
    """Hand-designed matched phasor codebook (construction-proof ceiling). F1/F1_NOISY: additive FPE
    (code[a]*code[b] = code[(a+b)%L] EXACT). F2 XOR: character code exp(i*pi*<s,bits>) (code[a]*code[b]=code[a xor b]
    EXACT). F3/F4: additive-default (diagnostic; predicted low -- no symmetric hand-design exists)."""
    g = np.random.default_rng(seed * 100003 + 313)
    if family == F_XOR and _is_pow2(L):
        k = int(round(np.log2(L)))
        s = g.integers(0, 2, size=(n_dim, k)).astype(np.int64)          # per-dim random parity mask over k bits
        vbits = ((np.arange(L, dtype=np.int64)[:, None] >> np.arange(k, dtype=np.int64)[None, :]) & 1)  # (L,k)
        parity = (vbits @ s.T) % 2                                       # (L, n_dim) in {0,1}
        code = np.exp(1j * np.pi * parity).astype(np.complex64)         # {+1,-1} phasors
        return torch.from_numpy(code)
    # additive FPE (matched to cyclic; diagnostic for asym/arbitrary)
    m = g.integers(1, max(2, L), size=n_dim).astype(np.float64)
    j = np.arange(L, dtype=np.float64)[:, None]
    phase = (2.0 * np.pi / L) * (j * m[None, :])
    return torch.from_numpy(np.exp(1j * phase).astype(np.complex64))     # (L, n_dim) complex64


def readout_logits(E, a_idx, b_idx):
    """Compositional similarity readout: logits[r] = Re<bind(E[a],E[b]), E[r]> using the REAL substrate FHRR bind.
    E (L,d) complex64 unit phasors; a_idx,b_idx (B,) long. Returns (B,L) real logits."""
    Ea = E[a_idx]                                    # (B,d) complex64
    Eb = E[b_idx]
    bound = hd_bind(Ea, Eb)                           # REAL substrate bind (elementwise complex mul); autograd-through
    return (bound @ E.conj().t()).real               # (B,L) float32; Re<bound, E[r]>


def eval_readout_acc(E, a_idx, b_idx, y):
    """Top-1 novel/seen accuracy for a phasor-code arm (DISCOVERY / FPE) via the compositional readout."""
    with torch.no_grad():
        logits = readout_logits(E, torch.as_tensor(a_idx, dtype=torch.long), torch.as_tensor(b_idx, dtype=torch.long))
        pred = torch.argmax(logits, dim=1).cpu().numpy().astype(np.int64)
    return float((pred == np.asarray(y, dtype=np.int64)).mean()), pred


# ---------------------------------------------------------------------------
# DISCOVERY arm: SHARED learnable phasor code table + compositional readout, plain CE.
# ---------------------------------------------------------------------------

def train_discovery(split, L, n_dim, steps, lr, seed):
    """Learn theta (L,n_dim) real; code E = polar(1, theta) unit phasors (SHARED across A,B,answer). Optimize plain CE
    over R classes through the REAL bind readout. NO hand-designed algebra, NO homomorphism regularizer."""
    torch.manual_seed(seed * 100003 + 71)
    theta = nn.Parameter(torch.empty(L, n_dim).uniform_(-np.pi, np.pi))
    opt = torch.optim.Adam([theta], lr=lr)
    a_tr = torch.as_tensor(split["a_tr"], dtype=torch.long)
    b_tr = torch.as_tensor(split["b_tr"], dtype=torch.long)
    y_tr = torch.as_tensor(split["y_tr_train"], dtype=torch.long)       # noisy labels for F_NOISY, clean otherwise
    lossf = nn.CrossEntropyLoss()
    final_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        E = torch.polar(torch.ones_like(theta), theta)                 # (L,d) complex64 unit modulus
        logits = readout_logits(E, a_tr, b_tr)
        loss = lossf(logits, y_tr)
        loss.backward()
        opt.step()
        final_loss = float(loss.detach().item())
    with torch.no_grad():
        E = torch.polar(torch.ones_like(theta), theta).detach()
    return E, final_loss


class MemoNet(nn.Module):
    """SEPARATE real embedding tables for A and B + concat -> MLP -> logits over R. No shared code, no bind."""

    def __init__(self, L, h):
        super().__init__()
        self.ea = nn.Embedding(L, h)
        self.eb = nn.Embedding(L, h)
        self.net = nn.Sequential(nn.Linear(2 * h, h), nn.ReLU(), nn.Linear(h, L))

    def forward(self, a_idx, b_idx):
        x = torch.cat([self.ea(a_idx), self.eb(b_idx)], dim=1)
        return self.net(x)


def train_memorize(split, L, h, steps, lr, seed):
    """Over-parameterized memorize baseline (fair: params_MEMORIZE >= params_DISCOVERY). Fits seen pairs; no
    compositional prior -> should NOT generalize to novel combos."""
    torch.manual_seed(seed * 100003 + 131)
    model = MemoNet(L, h)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    a_tr = torch.as_tensor(split["a_tr"], dtype=torch.long)
    b_tr = torch.as_tensor(split["b_tr"], dtype=torch.long)
    y_tr = torch.as_tensor(split["y_tr_train"], dtype=torch.long)
    lossf = nn.CrossEntropyLoss()
    n_params = int(sum(p.numel() for p in model.parameters()))
    final_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        logits = model(a_tr, b_tr)
        loss = lossf(logits, y_tr)
        loss.backward()
        opt.step()
        final_loss = float(loss.detach().item())
    return model, final_loss, n_params


def eval_memo_acc(model, a_idx, b_idx, y):
    with torch.no_grad():
        logits = model(torch.as_tensor(a_idx, dtype=torch.long), torch.as_tensor(b_idx, dtype=torch.long))
        pred = torch.argmax(logits, dim=1).cpu().numpy().astype(np.int64)
    return float((pred == np.asarray(y, dtype=np.int64)).mean()), pred


# ---------------------------------------------------------------------------
# FREQ_NULL (conditional-frequency null) + ORACLE (info-ceiling).
# ---------------------------------------------------------------------------

def eval_freq_null(split, L, a_idx, b_idx, y):
    """score(r)=count_train(a'==a,r)+count_train(b'==b,r); backoff to marginal POP when no conditional support."""
    ay = defaultdict(lambda: np.zeros(L, dtype=np.float64))
    by = defaultdict(lambda: np.zeros(L, dtype=np.float64))
    marg = np.zeros(L, dtype=np.float64)
    for a, b, yy in zip(split["a_tr"], split["b_tr"], split["y_tr_train"]):
        ay[int(a)][int(yy)] += 1.0
        by[int(b)][int(yy)] += 1.0
        marg[int(yy)] += 1.0
    preds = np.empty(len(a_idx), dtype=np.int64)
    for i, (a, b) in enumerate(zip(a_idx, b_idx)):
        sc = ay.get(int(a), np.zeros(L)) + by.get(int(b), np.zeros(L))
        if sc.sum() <= 0.0:
            sc = marg
        preds[i] = int(np.argmax(sc))
    return float((preds == np.asarray(y, dtype=np.int64)).mean()), preds


def oracle_novel_acc(family, L):
    """Learner info-ceiling on the NOVEL stratum. Deterministic learnable rule -> 1.0 achievable; ARBITRARY held-out
    entries are information-theoretically independent of train -> ceiling = chance (1/L)."""
    if family == F_ARB:
        return 1.0 / L
    return 1.0


# ---------------------------------------------------------------------------
# One family, one seed: train + eval every arm on SEEN and NOVEL strata.
# ---------------------------------------------------------------------------

def run_family(family, cfg, seed):
    L, d = cfg["L"], cfg["n_dim"]
    arb = build_arbitrary_table(L, seed)
    split = make_split(L, cfg["coverage"], seed, cfg["min_novel"], family, cfg["c1"], cfg["c2"], arb, cfg["noise_eps"])

    # DISCOVERY (shared learnable codes + real bind readout)
    E_disc, disc_loss = train_discovery(split, L, d, cfg["steps"], cfg["disc_lr"], seed)
    disc_seen, disc_seen_pred = eval_readout_acc(E_disc, split["seen_a"], split["seen_b"], split["seen_y"])
    disc_nov, disc_nov_pred = eval_readout_acc(E_disc, split["a_nv"], split["b_nv"], split["y_nv"])

    # MEMORIZE (separate tables + MLP)
    memo, memo_loss, memo_params = train_memorize(split, L, cfg["memo_h"], cfg["steps"], cfg["memo_lr"], seed)
    memo_seen, memo_seen_pred = eval_memo_acc(memo, split["seen_a"], split["seen_b"], split["seen_y"])
    memo_nov, memo_nov_pred = eval_memo_acc(memo, split["a_nv"], split["b_nv"], split["y_nv"])

    # FPE (hand-designed matched ceiling; NOT trained)
    E_fpe = build_matched_fpe(family, L, d, seed)
    fpe_seen, _ = eval_readout_acc(E_fpe, split["seen_a"], split["seen_b"], split["seen_y"])
    fpe_nov, fpe_nov_pred = eval_readout_acc(E_fpe, split["a_nv"], split["b_nv"], split["y_nv"])

    # FREQ_NULL
    freq_seen, _ = eval_freq_null(split, L, split["seen_a"], split["seen_b"], split["seen_y"])
    freq_nov, freq_nov_pred = eval_freq_null(split, L, split["a_nv"], split["b_nv"], split["y_nv"])

    # ORACLE info-ceiling
    orc_nov = oracle_novel_acc(family, L)

    n_params_disc = int(L * d)
    arms = {
        DISC: dict(seen=disc_seen, novel=disc_nov, train_loss=disc_loss, n_params=n_params_disc),
        MEMO: dict(seen=memo_seen, novel=memo_nov, train_loss=memo_loss, n_params=memo_params),
        FPE: dict(seen=fpe_seen, novel=fpe_nov),
        FREQ: dict(seen=freq_seen, novel=freq_nov),
        ORC: dict(novel=orc_nov),
    }
    # ARMS-MUST-DIFFER (META_RULE_AF): novel-stratum prediction vectors must not be bit-identical across arms
    pred_arms = {DISC: disc_nov_pred, MEMO: memo_nov_pred, FPE: fpe_nov_pred, FREQ: freq_nov_pred}
    sigs = {k: hashlib.sha256(np.asarray(v, dtype=np.int64).tobytes()).hexdigest()[:16] for k, v in pred_arms.items()}
    return dict(family=family, L=L, chance=1.0 / L, arms=arms, sigs=sigs,
                n_train=split["n_train"], n_novel=split["n_novel"], n_seen=split["n_seen"],
                missing_a=len(split["missing_a"]), missing_b=len(split["missing_b"]), missing_y=len(split["missing_y"]),
                n_leaked=len(split["leaked"]), n_flipped=split["n_flipped"],
                memo_params=memo_params, disc_params=n_params_disc)


def run_seed(cfg, seed, families=None):
    fams = families if families is not None else FAMILIES
    out = {}
    for fam in fams:
        out[fam] = run_family(fam, cfg, seed)
    n_novel = out[F_CYCLIC]["n_novel"] if F_CYCLIC in out else out[fams[0]]["n_novel"]
    return dict(seed=seed, L=cfg["L"], chance=1.0 / cfg["L"], families=out,
                n_novel=int(n_novel), n_seen=int(out[fams[0]]["n_seen"]))


# ---------------------------------------------------------------------------
# Decisive verdict over per-seed results.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _fam_arm_novel(per_seed, fam, arm):
    return _nm([ps["families"][fam]["arms"][arm]["novel"] for ps in per_seed if fam in ps["families"]])


def decisive_verdict(per_seed):
    L = per_seed[0]["L"]
    chance = 1.0 / L

    disc_f1 = _fam_arm_novel(per_seed, F_CYCLIC, DISC)
    disc_f2 = _fam_arm_novel(per_seed, F_XOR, DISC)
    memo_f1 = _fam_arm_novel(per_seed, F_CYCLIC, MEMO)
    memo_f2 = _fam_arm_novel(per_seed, F_XOR, MEMO)
    freq_f1 = _fam_arm_novel(per_seed, F_CYCLIC, FREQ)
    freq_f2 = _fam_arm_novel(per_seed, F_XOR, FREQ)
    disc_arb = _fam_arm_novel(per_seed, F_ARB, DISC)
    memo_arb = _fam_arm_novel(per_seed, F_ARB, MEMO)
    disc_asym = _fam_arm_novel(per_seed, F_ASYM, DISC)
    memo_asym = _fam_arm_novel(per_seed, F_ASYM, MEMO)
    disc_noisy = _fam_arm_novel(per_seed, F_NOISY, DISC)
    memo_noisy = _fam_arm_novel(per_seed, F_NOISY, MEMO)
    fpe_f1 = _fam_arm_novel(per_seed, F_CYCLIC, FPE)
    fpe_f2 = _fam_arm_novel(per_seed, F_XOR, FPE)

    adv_f1 = disc_f1 - memo_f1
    adv_f2 = disc_f2 - memo_f2
    arb_lift = disc_arb - chance

    # ---- HARD_PASS gates ----
    hp1 = bool(disc_f1 == disc_f1 and disc_f2 == disc_f2 and disc_f1 >= HP_DISC_ABS and disc_f2 >= HP_DISC_ABS)
    hp2 = bool(adv_f1 == adv_f1 and adv_f2 == adv_f2 and adv_f1 >= HP_ARCH_ADV and adv_f2 >= HP_ARCH_ADV)
    hp3 = bool(arb_lift == arb_lift and arb_lift <= MUSTFAIL_TOL)
    hp4 = bool(freq_f1 == freq_f1 and freq_f2 == freq_f2 and freq_f1 <= HP_NULL_FAILS and freq_f2 <= HP_NULL_FAILS)
    hard_pass = bool(hp1 and hp2 and hp3 and hp4)

    # ---- HARD_FAIL / REFUTE gates ----
    rf1 = bool(adv_f1 == adv_f1 and adv_f1 <= REFUTE_TOL)
    rf2 = bool(arb_lift == arb_lift and arb_lift >= INTEGRITY_BREACH)   # integrity: dominates
    hard_fail = bool(rf1 or rf2)

    if rf2:
        verdict = "INVALID_ARBITRARY_GENERALIZES_DISCOVERY_LEAKS"
    elif hard_pass:
        verdict = "ARCHITECTURE_DISCOVERS_COMPOSITIONAL_STRUCTURE_ACROSS_ABELIAN_FAMILIES"
    elif hard_fail:
        verdict = "REFUTED_NO_ARCHITECTURE_ADVANTAGE_OVER_MEMORIZE"
    else:
        # bounded / partial: name the bound honestly
        f1_ok = bool(disc_f1 >= HP_DISC_ABS and adv_f1 >= HP_ARCH_ADV)
        f2_ok = bool(disc_f2 >= HP_DISC_ABS and adv_f2 >= HP_ARCH_ADV)
        if f1_ok and not f2_ok:
            verdict = "MIDDLE_BAND_ADDITIVE_ONLY_XOR_NOT_DISCOVERED"
        elif f2_ok and not f1_ok:
            verdict = "MIDDLE_BAND_XOR_ONLY_ADDITIVE_NOT_DISCOVERED"
        else:
            verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || chance=1/L=%.4f | F1_CYCLIC: DISC=%s MEMO=%s adv=%s FREQ=%s FPE=%s | F2_XOR: DISC=%s MEMO=%s adv=%s "
           "FREQ=%s FPE=%s | F4_ARB(must-fail): DISC=%s lift=%s(<=%.2f=%s breach>=%.2f=%s) MEMO=%s | "
           "F3_ASYM(bound): DISC=%s MEMO=%s | F1_NOISY: DISC=%s MEMO=%s || HP1_abs=%s HP2_adv=%s HP3_arb=%s "
           "HP4_null=%s | RF1_tie=%s RF2_integrity=%s"
           % (verdict, chance, _fmt(disc_f1), _fmt(memo_f1), _fmt(adv_f1), _fmt(freq_f1), _fmt(fpe_f1),
              _fmt(disc_f2), _fmt(memo_f2), _fmt(adv_f2), _fmt(freq_f2), _fmt(fpe_f2),
              _fmt(disc_arb), _fmt(arb_lift), MUSTFAIL_TOL, hp3, INTEGRITY_BREACH, rf2, _fmt(memo_arb),
              _fmt(disc_asym), _fmt(memo_asym), _fmt(disc_noisy), _fmt(memo_noisy),
              hp1, hp2, hp3, hp4, rf1, rf2))

    def _r(x):
        return round(x, 6) if (x == x) else None

    gates = dict(
        verdict=verdict, chance=_r(chance),
        f1_cyclic=dict(discovery=_r(disc_f1), memorize=_r(memo_f1), advantage=_r(adv_f1), freq_null=_r(freq_f1),
                       fpe_ceiling=_r(fpe_f1)),
        f2_xor=dict(discovery=_r(disc_f2), memorize=_r(memo_f2), advantage=_r(adv_f2), freq_null=_r(freq_f2),
                    fpe_ceiling=_r(fpe_f2)),
        f3_asym_bound=dict(discovery=_r(disc_asym), memorize=_r(memo_asym)),
        f4_arbitrary=dict(discovery=_r(disc_arb), lift_over_chance=_r(arb_lift), memorize=_r(memo_arb)),
        f1_noisy=dict(discovery=_r(disc_noisy), memorize=_r(memo_noisy)),
        hard_pass_gates=dict(HP1_disc_abs=hp1, HP2_arch_adv=hp2, HP3_arb_mustfail=hp3, HP4_null_fails=hp4),
        hard_fail_gates=dict(RF1_no_advantage=rf1, RF2_integrity_breach=rf2),
        bands=dict(HP_DISC_ABS=HP_DISC_ABS, HP_ARCH_ADV=HP_ARCH_ADV, MUSTFAIL_TOL=MUSTFAIL_TOL,
                   HP_NULL_FAILS=HP_NULL_FAILS, REFUTE_TOL=REFUTE_TOL, INTEGRITY_BREACH=INTEGRITY_BREACH),
        cited_prototype=dict(disc_add=CITED_PROTO_DISC_ADD, memo_add=CITED_PROTO_MEMO_ADD, disc_arb=CITED_PROTO_DISC_ARB),
    )
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Self-test: apparatus validity on a tiny synthetic arena (REAL bind in the DISCOVERY gradient loop) + preflight.
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    cfg = dict(SELFTEST_CFG)
    L, d = cfg["L"], cfg["n_dim"]
    chance = 1.0 / L

    # F.1/F.2 real-bind homomorphism sanity: hand-designed additive FPE -> bind(code[a],code[b]) == code[(a+b)%L].
    Yc = build_matched_fpe(F_CYCLIC, L, d, 7)
    a_idx = torch.tensor([3, 7, 11], dtype=torch.long)
    b_idx = torch.tensor([5, 2, 9], dtype=torch.long)
    bound = hd_bind(Yc[a_idx], Yc[b_idx])                             # REAL substrate bind
    pred = torch.argmax((bound @ Yc.conj().t()).real, dim=1).tolist()
    expect = [((int(a) + int(b)) % L) for a, b in zip(a_idx.tolist(), b_idx.tolist())]
    homomorphism_ok = bool(pred == expect)

    # Run the tiny discovery experiment on F1 (cyclic) and F4 (arbitrary); the DISCOVERY train loop USES the real bind.
    res = run_seed(cfg, 7, families=[F_CYCLIC, F_ARB])
    f1 = res["families"][F_CYCLIC]
    f4 = res["families"][F_ARB]
    disc_f1 = f1["arms"][DISC]["novel"]
    memo_f1 = f1["arms"][MEMO]["novel"]
    seen_f1 = f1["arms"][DISC]["seen"]
    fpe_f1 = f1["arms"][FPE]["novel"]
    disc_arb = f4["arms"][DISC]["novel"]

    disc_learns = bool(disc_f1 >= ST_DISC_ABS)
    arch_adv = bool((disc_f1 - memo_f1) >= ST_ARCH_ADV)
    fpe_ceiling_ok = bool(fpe_f1 >= ST_FPE_ADD)
    arb_mustfail = bool((disc_arb - chance) <= ST_ARB_MUSTFAIL)
    disc_fits = bool(seen_f1 >= disc_f1 - 1e-6)                       # fits seen at least as well as novel (sanity)
    novel_ok = bool(f1["n_novel"] >= cfg["min_novel"] and f1["n_leaked"] == 0)
    # arms differ on the novel stratum (>= 3 distinct prediction signatures among DISC/MEMO/FPE/FREQ)
    n_sigs = len(set(f1["sigs"].values()))
    arms_differ = bool(n_sigs >= 3)

    # VACUOUS-SMOKE / DISCRIMINATOR-FIRES guard: DISCOVERY MUST separate from MEMORIZE on F1 novel (control fails).
    control_passed = bool((disc_f1 - memo_f1) < ST_ARCH_ADV)
    assert_discriminator_fires(control_passed, control_name="MEMORIZE",
                               headline_name="discovery_beats_memorize_f1_novel", run_mode="self_test",
                               extra="on the tiny additive arena DISCOVERY did NOT separate from the MEMORIZE baseline "
                                     "on the NOVEL stratum -> the architecture-advantage discriminator is frozen at "
                                     "this scale (raise L/d/steps until it fires)")

    v_verdict, _vm, _vg = decisive_verdict([run_seed(cfg, 7)])         # full-family self-test verdict (all 5 families)

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["hdlab.binding.bind", "readout_logits", "train_discovery"],
         "exercised_entrypoints": ["hdlab.binding.bind", "readout_logits", "train_discovery"],
         "extra": "self-test TRAINS the DISCOVERY arm (train_discovery -> readout_logits -> hdlab.binding.bind) on a "
                  "tiny synthetic additive arena -- the EXACT shared-code + real-bind gradient path the FULL run uses; "
                  "no external data dependency (synthetic rules), so the full path is exercised locally"},
        {"kind": "substrate_signature", "callable_obj": hd_bind, "callable_name": "hdlab.binding.bind",
         "kwargs": {"a": Yc[a_idx], "b": Yc[b_idx]}},
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(disc_learns and arch_adv and fpe_ceiling_ok and homomorphism_ok),
         "control_name": "SYNTHETIC_ADDITIVE_DISCOVERY",
         "headline_name": "shared_code_discovery_beats_memorize_on_novel_additive",
         "extra": "apparatus CAN detect discovery-beats-memorize when structure exists: on synthetic additive, the "
                  "learned shared-code arm generalizes to novel combos, the memorize arm does not, and the "
                  "hand-designed FPE ceiling is near-exact"},
        {"kind": "metric_moves", "metric_name": "f1_novel_acc",
         "values": [disc_f1, memo_f1, fpe_f1, disc_arb, f1["arms"][FREQ]["novel"], seen_f1],
         "extra": "arms MOVE: DISC_f1=%.3f MEMO_f1=%.3f FPE_f1=%.3f DISC_arb=%.3f FREQ_f1=%.3f DISC_seen=%.3f"
                  % (disc_f1, memo_f1, fpe_f1, disc_arb, f1["arms"][FREQ]["novel"], seen_f1)},
        {"kind": "negative_control_margin",
         "control_scores": [memo_f1, disc_arb],
         "headline_threshold": disc_f1, "higher_is_pass": True, "margin": ST_ARCH_ADV, "n_repeats_min": 2,
         "control_name": "memorize_and_arbitrary_below_discovery_f1",
         "extra": "the MEMORIZE baseline and the ARBITRARY must-fail sit far below DISCOVERY-F1; both confirm the F1 "
                  "generalization requires genuine compositional structure discovered by the shared-code architecture"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["homomorphism_ok", "disc_learns", "arch_adv", "fpe_ceiling_ok", "arb_mustfail",
                                    "disc_fits", "arms_differ", "novel_ok", "decisive_verdict"],
         "exercised_gates": ["homomorphism_ok", "disc_learns", "arch_adv", "fpe_ceiling_ok", "arb_mustfail",
                             "disc_fits", "arms_differ", "novel_ok", "decisive_verdict"],
         "extra": "decisive_verdict=%s at self-test scale" % v_verdict},
    ], run_mode="self_test")

    out = dict(
        homomorphism_ok=homomorphism_ok, homomorphism_pred=pred, homomorphism_expect=expect,
        f1_discovery_novel=round(disc_f1, 5), f1_memorize_novel=round(memo_f1, 5),
        f1_advantage=round(disc_f1 - memo_f1, 5), f1_fpe_novel=round(fpe_f1, 5), f1_discovery_seen=round(seen_f1, 5),
        arb_discovery_novel=round(disc_arb, 5), arb_lift=round(disc_arb - chance, 5), chance=round(chance, 5),
        n_distinct_sigs=n_sigs, n_novel=f1["n_novel"], n_leaked=f1["n_leaked"],
        disc_learns=disc_learns, arch_adv=arch_adv, fpe_ceiling_ok=fpe_ceiling_ok, arb_mustfail=arb_mustfail,
        disc_fits=disc_fits, arms_differ=arms_differ, novel_ok=novel_ok,
        decisive_selftest_verdict=v_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["real_code_path", "substrate_signature", "positive_control", "metric_moves",
                                     "negative_control_margin", "full_gates_exercised"],
    )
    ok = bool(homomorphism_ok and disc_learns and arch_adv and fpe_ceiling_ok and arb_mustfail and disc_fits
              and arms_differ and novel_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("run_mode=%s seeds=%s L=%s n_dim=%s coverage=%s steps=%s"
         % (run_mode, seeds, cfg["L"], cfg["n_dim"], cfg["coverage"], cfg["steps"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s | f1_disc=%s f1_memo=%s adv=%s fpe=%s arb_lift=%s homo_ok=%s vp_ok=%s"
         % (st_ok, st_res.get("f1_discovery_novel"), st_res.get("f1_memorize_novel"), st_res.get("f1_advantage"),
            st_res.get("f1_fpe_novel"), st_res.get("arb_lift"), st_res.get("homomorphism_ok"),
            st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s"
                        % {kk: st_res.get(kk) for kk in ("homomorphism_ok", "disc_learns", "arch_adv",
                           "fpe_ceiling_ok", "arb_mustfail", "disc_fits", "arms_differ", "novel_ok")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS STRUCTURE_DISCOVERY: the shared-code + real-bind readout arm, trained with plain "
                        "CE (NO hand-designed algebra), DISCOVERS the additive rule and generalizes to NOVEL combos on "
                        "the tiny synthetic arena, beating the over-parameterized MEMORIZE baseline; the ARBITRARY "
                        "must-fail fires (novel ~ chance); FPE hand-design ceiling near-exact; 6 validity-preflight "
                        "checks declared. FULL sweeps L=64 across F1_CYCLIC/F2_XOR (abelian), F3_ASYM (claim-bound) and "
                        "F4_ARBITRARY (must-fail) with 3 seeds to test discovery across DISTINCT structure families.",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed = []
    unit_failures = []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            res = run_seed(cfg, seed)
            f1 = res["families"][F_CYCLIC]
            if int(f1["n_novel"]) < cfg["min_novel"]:
                raise RuntimeError("novel stratum too small (%d < %d)" % (int(f1["n_novel"]), cfg["min_novel"]))
            if int(f1["n_leaked"]) != 0:
                raise RuntimeError("LEAK: %d novel pairs found in train (seed=%d)" % (int(f1["n_leaked"]), seed))
            n_sigs = len(set(f1["sigs"].values()))
            if n_sigs < 3:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d n_sigs=%d" % (seed, n_sigs))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            _log("seed=%d nov=%d seen=%d | F1 DISC=%s MEMO=%s | F2 DISC=%s MEMO=%s | F4 DISC=%s(chance=%.4f) | "
                 "F3 DISC=%s | (%.1fs)"
                 % (seed, f1["n_novel"], f1["n_seen"],
                    _fmt(f1["arms"][DISC]["novel"]), _fmt(f1["arms"][MEMO]["novel"]),
                    _fmt(res["families"][F_XOR]["arms"][DISC]["novel"]),
                    _fmt(res["families"][F_XOR]["arms"][MEMO]["novel"]),
                    _fmt(res["families"][F_ARB]["arms"][DISC]["novel"]), res["chance"],
                    _fmt(res["families"][F_ASYM]["arms"][DISC]["novel"]), time.time() - ts))
            _hb("seed", si + 1)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = decisive_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, unit_failures=unit_failures,
                   per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")  # CPU-only cell (tiny matmuls)
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
        if "memsmoke" in os.environ.get("HDLAB_EXP_NAME", "").lower():
            run_mode = "memsmoke"
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
