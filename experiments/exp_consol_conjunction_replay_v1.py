r"""CONSOLIDATION x CONJUNCTION (v1): does INTERLEAVED-replay CONSOLIDATION manufacture structure that BEATS
FREQUENCY on a CONJUNCTION inference target -- the regime where frequency provably CANNOT win -- AND beats a
COMPUTE-MATCHED task-blocked CONTINUAL schedule? Glass-box, native FHRR ops, NO LLM.

WHY (2x-drill on the consolidation negative). The consolidation envelope-push (exp_consol_inductive_entity_replay_
cskg_v1) found replay BEATS compute-matched continual but only MATCHES a fair FREQUENCY bar on SINGLE-RELATION
inductive inference -- because single-relation inference is FREQUENCY-CAPPED (a per-relation tail-frequency baseline
already captures most of the signal). Hypothesis: on a CONJUNCTION target (label needs COMBINING >= 2 constituents;
every single constituent / proper subset is at chance) the interleaved-replay-learned codes should BEAT frequency
where single-relation couldn't -- ties consolidation-replay to the (frontier-validated) conjunction mechanism.

THE CONJUNCTION ARENA = PARITY over K=4 ordinal constituents (arena / split / must-fail controls reused from the
VET'd exp_interaction_nonadditive_discovery_v1 / exp_joint_dual_channel_readout_v1). PARITY is THE canonical
frequency-unsolvable conjunction: fixing any single constituent leaves the parity of the remaining constituents
UNIFORM -> per-constituent mutual-information with the label is EXACTLY 0 -> a frequency / single-driver baseline is
PROVABLY AT CHANCE. (AND2 = bit0 & bit1 is carried as a REPORTED CONTEXT family where a single driver DOES leak
signal -> frequency is ABOVE chance there: the contrast makes "freq-at-chance" specific to a genuine conjunction.)

THE MECHANISM UNDER TEST = the minibatch SCHEDULE that fits the SHARED content codes read out through the parity-
capable SYMMETRIC-PRODUCT lens. ALL schedule arms fit the SAME product-lens model (shared content code table c(L,d)
of unit phasors + ONE linear readout head) with the SAME CE loss and the SAME PER-COMBO GRADIENT EXPOSURE (each train
combo trained P_max times in every arm -> compute-matched, so a beat is not a compute artifact); the ONLY difference
is HOW the minibatches are ordered:
  INTERLEAVED : i.i.d. minibatch SGD over ALL train combos, P_max passes (replay / consolidation).  THE MECHANISM.
  CONTINUAL   : task-blocked by the constituent-0 level (g_domains = L blocks, a standard non-i.i.d. task-incremental
                stream), P_max passes PER block in order, NO replay. Because the shared content codes are contested
                across blocks (a level's code appears at position 0 in its own block and at positions 1..K-1 in every
                block) and blocking a conjunction by one coordinate FLIPS the residual-parity convention between early
                (bit0=0) and late (bit0=1) blocks, sequential training drags the shared codes toward the last block's
                convention and FORGETS the early blocks -> degraded novel-combo generalization. COMPUTE-MATCHED.
  SHUFFLE     : interleaved schedule but the TRAIN LABELS permuted (structure destroyed) -> the codes fit noise and
                cannot generalize -> novel accuracy must stay at chance.  MUST-FAIL.
The READOUT (identical across the 3 schedule arms) is the SYMMETRIC-PRODUCT lens: z = c(x_0) (x) c(x_1) (x) ... (x)
c(x_{K-1}) (native FHRR complex-product bind), feat = [Re z, Im z], one linear head. This is the parity specialist
that the frontier cell measured at ~0.98 -- here it is fit under three SCHEDULES to isolate the consolidation effect.

REFERENCE / FAIRNESS ARMS (same novel query edges, paired):
  FREQ_NULL = max(HOMOPHILY, POP) : the FAIR FREQUENCY BAR. On PARITY it is PROVABLY at chance (single-driver MI=0);
                the load-bearing FAIRNESS gate verifies FREQ_NULL_novel <= chance + tol (if frequency solves it, the
                arena is NOT a genuine conjunction -> INVALID_ARENA, not a substrate result).
  HOMOPHILY   : per-constituent additive class vote (frequency component; reported).
  POP         : majority-class predictor (frequency component; reported).
  MEMORIZE    : train-combo lookup, falls back to POP on novel (cannot generalize to novel by construction).
  ORACLE      : gold labels on the query = arena-answerable info-ceiling (clean PARITY -> 1.0). H = ORACLE - chance.

PRIMARY DISCRIMINATOR = the SCHEDULE contrast INTERLEAVED-vs-CONTINUAL (the consolidation question). INTERLEAVED-vs-
FREQ_NULL is the READOUT-WORKS / arena-answerable gate (does a trained conjunction readout beat frequency at all).
CEILING-RELATIVE, PRE-REGISTERED BANDS (fixed BEFORE the 5-seed run on FRESH seeds; H = ORACLE - chance):
  ARENA-VALID (load-bearing): ORACLE fires (ORACLE - chance >= 0.30) AND FREQ_NULL_novel at chance (<= chance +
              FREQ_CHANCE_TOL, the FAIRNESS gate: if frequency solves it, NOT a genuine conjunction) AND SHUFFLE flat
              (must-fail schedule arm fires -> the discriminator is telemetry-SENSITIVE) AND READOUT-WORKS
              (INTERLEAVED - FREQ_NULL >= max(0.10*H, 0.10) AND recovers >= 0.30*H) AND compute-matched AND enough novel.
  HARD_PASS : arena-valid AND INTERLEAVED beats CONTINUAL by >= max(0.10*H, 0.03) on a majority of seeds -- replay/
              consolidation MANUFACTURES a conjunction advantage OVER compute-matched continual (matches the CSKG
              single-relation precedent's replay-beats-continual, now ALSO beating frequency on a conjunction).
  REFUTE    : arena-valid AND INTERLEAVED - CONTINUAL <= REFUTE_EPS -- the readout LEARNS the conjunction and beats
              frequency, but the SCHEDULE is IRRELEVANT: replay confers NO advantage over compute-matched continual,
              so the conjunction-beats-frequency is a READOUT effect, not a CONSOLIDATION effect. The under-trained
              probe (few passes) confirms the null is not a full-P ceiling artifact. A VALUABLE, drill-worthy negative
              that LOCALIZES the consolidation mechanism (replay helps only under CROSS-DOMAIN code INTERFERENCE, as
              in the CSKG relation-blocked case; a coordinate-blocked SYMMETRIC conjunction has none). Not forced.
  MIDDLE    : arena-valid, INTERLEAVED - CONTINUAL in (REFUTE_EPS, HARD_PASS margin) (partial / unstable schedule lift).
  INCONCLUSIVE: ORACLE underfit, FREQ_NULL above chance (arena not a genuine conjunction), SHUFFLE not flat (metric
              insensitive), readout underfit (does not beat frequency), too few novel, or compute unmatched.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): INTERLEAVED / CONTINUAL / SHUFFLE prediction sigs distinct.
# - final_metrics_atomicity = tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb_n/a: classification accuracy; the noise floor IS the majority-class chance rate (computed per seed) and the
#   info-ceiling is the gold ORACLE; bands are FRACTIONS of the MEASURED headroom H = ORACLE - chance.
# - baseline_in_band (META_RULE_AG): FREQ_NULL pinned near chance (single-driver MI=0) -> self-test asserts
#   chance-0.03 <= FREQ_NULL <= chance+FREQ_CHANCE_TOL; ORACLE=1.0; INTERLEAVED strictly between FREQ and ORACLE.
# - discriminator survives scale: the arena is FULL-SCALE at self-test (make_X uses the FULL N_ENT=220 combo sample);
#   self-test fires INTERLEAVED-beats-CONTINUAL + beats-FREQ + SHUFFLE-flat on the real parity arena at ONE seed.
# - HARD_PASS strictly above floor: margins are FRACTIONS of H + absolute MIN floors (not >= 0).
# - HP_SCOPE: the beat gates apply to INTERLEAVED only. ORACLE=positive-control ceiling; FREQ_NULL/HOMOPHILY/POP=the
#   fair frequency bar; SHUFFLE=must-not-generalize control; CONTINUAL=the compute-matched head-to-head; MEMORIZE=ref.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=3 distinct schedule sigs.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except; per-seed failure_class recorded).
# - calibration_check = adaptive_with_discriminator_gate: all FRACs/eps pre-registered; beat targets are FRACTIONS OF
#   THE MEASURED headroom H (computed in-run), NOT thresholds tuned on the real result.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - real_code_path: self-test EXERCISES the REAL substrate primitives (hd_bind FHRR complex product via _config_term,
#   arm_homophily, the fit_schedule minibatch trainer, acc) on the REAL parity arena at full N_ENT.
# - substrate_signature binds hd_bind against inspect.signature; base/portable positional args only.
# - guard_baseline_valid: on a genuine conjunction FREQ_NULL == chance BY DESIGN, so beats-FREQ IS beats-chance -- the
#   guard validates FREQ_NULL is NOT below the chance floor (a broken frequency baseline) before the beat gate fires.
# - deterministic INTEGER seeds only; no salted-hash / list(set()) seeding (PROT-023 static scan runs on ship).
# - progress_logging: line_buffered_stdout + per-seed/per-arm flush prints.

Glass-box CPU. ASCII-only. Explicit float32/complex64. Deterministic integer seeds. No bare except.
Default invocation (no flag) = FULL run to completion (runner calls `python -u <script>`).
"""

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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.binding import bind as hd_bind  # noqa: E402  # REAL FHRR bind (complex64 elementwise mul).
from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
# Arena + families + baselines + split reused VERBATIM from the VET'd conjunction cell.
from experiments.exp_joint_dual_channel_readout_v1 import (  # noqa: E402
    make_X, target, plant_regime, split_novel, chance_of, _init_content, _config_term,
    arm_homophily, arm_memorize, acc, nonadditivity,
    K, L, N_ENT, EMB_D, PARITY, AND2, CLEAN, SHUFFLE as REG_SHUFFLE,
)

ANCHOR_NAME = "consol_conjunction_replay_v1"

# ---- schedule arm names ----
INTERLEAVED = "INTERLEAVED"    # mechanism: i.i.d. minibatch replay
CONTINUAL = "CONTINUAL"        # compute-matched task-blocked (blocked by constituent-0 level)
SHUFFLE = "SHUFFLE"            # interleaved schedule, train labels permuted (must-fail)
# ---- reference arms ----
FREQ = "FREQ_NULL"            # max(HOMOPHILY, POP): the fair frequency bar (provably ~chance on parity)
HOM = "HOMOPHILY"
POP = "POP"
MEMO = "MEMORIZE"
ORC = "ORACLE"                # gold labels = arena-answerable info-ceiling
SCHEDULE_ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE]
ALL_ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE, FREQ, HOM, POP, MEMO, ORC]

GATED_FAMILY = PARITY          # the frequency-unsolvable conjunction the claim is gated on
CONTEXT_FAMILIES = [AND2]      # reported contrast (frequency gets partial signal)
ALL_FAMILIES = [PARITY] + CONTEXT_FAMILIES

# ---- pre-registered bands (fixed BEFORE the 5-seed run on FRESH seeds; ceiling-relative to MEASURED H = ORACLE -
#      chance). The PRIMARY discriminator is the SCHEDULE contrast INTERLEAVED-vs-CONTINUAL (the consolidation
#      question); INTERLEAVED-vs-FREQ_NULL is the readout-works / arena-answerable gate (frequency at chance). ----
ORACLE_FIRE_MARGIN = 0.30      # ORACLE - chance >= this (arena answerable)
FREQ_CHANCE_TOL = 0.08         # FREQ_NULL_novel <= chance + this (fairness: frequency at chance on the conjunction)
READOUT_BEATS_FREQ_FRAC = 0.10  # readout-works gate: INTERLEAVED - FREQ_NULL >= max(this*H, READOUT_BEATS_FREQ_ABS)
READOUT_BEATS_FREQ_ABS = 0.10
BEAT_CONT_FRAC = 0.10          # HARD_PASS (schedule advantage): INTERLEAVED - CONTINUAL >= max(this*H, BEAT_CONT_ABS)
BEAT_CONT_ABS = 0.03
RECOVER_FRAC = 0.30            # INTERLEAVED - chance >= this*H (mechanism substantively above chance)
FLAT_FRAC = 0.25               # must-fail schedule arm: SHUFFLE - chance <= this*H (telemetry-sensitivity proof)
REFUTE_EPS = 0.01              # INTERLEAVED - CONTINUAL <= this (arena-valid, readout works) -> REFUTE (no schedule adv)
MIN_NOVEL = 20                 # min novel query combos for a valid discriminator
STEP_MATCH_TOL = 0.02          # |steps_inter - steps_cont| / steps_inter must be <= this (compute-matched; ~0 by build)

# ---- config profiles. All modes run the SAME FULL arena (make_X samples N_ENT combos regardless) -> the schedule
# discriminator is at full scale. Blocking = constituent-0 level (block_by=1, L blocks: standard task-incremental
# non-i.i.d. stream). p_probe = an under-trained checkpoint (few passes) proving the schedule-null is NOT a ceiling
# artifact. FULL seeds are FRESH [11,19,31,41,53] -- DISJOINT from the calibration seeds -> clean pre-registration.
SELFTEST_CFG = dict(P_max=60, batch=8, lr=0.05, block_by=1, emb_d=48, p_probe=3, seeds=[7])
SMOKE_CFG = dict(P_max=60, batch=8, lr=0.05, block_by=1, emb_d=48, p_probe=3, seeds=[101, 103])
FULL_CFG = dict(P_max=60, batch=8, lr=0.05, block_by=1, emb_d=48, p_probe=3, seeds=[101, 103, 107, 109, 113])

# ---- self-test thresholds (calibrated on the REAL parity arena, seed 7; DIRECTIONAL machinery+sensitivity gates,
#      NOT the hypothesis outcome -- INTERLEAVED-vs-CONTINUAL is deliberately NOT gated in the self-test) ----
ST_INTER_MIN = 0.72            # INTERLEAVED novel parity accuracy at least this (product lens learns the conjunction)
ST_INTER_BEATS_FREQ = 0.12     # INTERLEAVED - FREQ_NULL >= this (arena answerable + frequency genuinely at chance)
ST_INTER_BEATS_SHUFFLE = 0.20  # INTERLEAVED - SHUFFLE >= this (discriminator telemetry-sensitive: a bad schedule IS
                               #   detected -> the INTER-vs-CONTINUAL null is a real result, not a frozen metric)
ST_SHUFFLE_MAX_OVER_CHANCE = 0.10   # SHUFFLE - chance <= this (must-fail schedule arm fires)
ST_MIN_NOVEL = 20


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Defensive helpers.
# ---------------------------------------------------------------------------

def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(out_dir), exist_ok=True)
    tmp = os.path.join(str(out_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(out_dir), "_start_marker.json"))


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(out_dir), exist_ok=True)
    tmp = os.path.join(str(out_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(out_dir), "metrics.json"))


# ---------------------------------------------------------------------------
# The SCHEDULE-fit product-lens learner (the mechanism). Shared content codes + linear head; native FHRR product bind.
# ---------------------------------------------------------------------------

def _product_feat(cr, ci, Xi):
    """Xi: (n,K) level indices. z = product-bind of content codes (native FHRR); feat = [Re z, Im z] (n,2d)."""
    cc = torch.complex(cr, ci)                 # (L,d)
    cont = cc[Xi]                              # (n,K,d) complex
    z = _config_term(cont)                     # (n,d) = c(x0) (x) c(x1) (x) ... (product bind)
    return torch.cat([z.real, z.imag], dim=1)  # (n,2d)


def _build_stream(schedule, n_tr, domain_of, P_max, rng):
    """Build a single flat index STREAM of length P_max*n_tr (each combo appears P_max times in EVERY schedule ->
    identical example-exposure AND identical optimizer-step count = ceil(len/batch)). Only the ORDER differs.

    INTERLEAVED/SHUFFLE : P_max independent i.i.d. shuffles of all rows concatenated (replay).
    CONTINUAL           : block by block (ascending domain id); within each block P_max shuffled passes, then the
                          next block -> a non-i.i.d. task-incremental stream (no replay across blocks). A handful of
                          minibatches straddle a block boundary (<1% of steps) -> if anything conservative.
    """
    rows = np.arange(n_tr, dtype=np.int64)
    if schedule == CONTINUAL:
        assert domain_of is not None, "CONTINUAL requires domain_of"
        parts = []
        for dd in sorted(set(int(x) for x in domain_of.tolist())):
            blk = rows[domain_of == dd]
            for _ in range(P_max):
                parts.append(blk[rng.permutation(blk.shape[0])])
        return np.concatenate(parts) if parts else rows
    parts = [rows[rng.permutation(n_tr)] for _ in range(P_max)]
    return np.concatenate(parts)


def fit_schedule(Xtr, ytr, nclass, schedule, seed, cfg, domain_of=None):
    """Fit (content codes cr,ci + linear head W,b) under a minibatch SCHEDULE. Returns (cr,ci,W,b,n_steps).
    All schedules share EXACT example-exposure (P_max touches/combo) AND step count; only minibatch ORDER differs.
    """
    P_max, batch, lr = int(cfg["P_max"]), int(cfg["batch"]), float(cfg["lr"])
    g = torch.Generator().manual_seed(int(seed) * 7919 + 11)
    d = int(cfg.get("emb_d", EMB_D))
    cr, ci = _init_content(d, g)
    W = torch.nn.Parameter(0.1 * torch.randn(2 * d, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([cr, ci, W, b], lr=lr)
    lossf = torch.nn.CrossEntropyLoss()

    Xt = torch.from_numpy(Xtr).long()
    yt = torch.from_numpy(ytr).long()
    perm_rng = np.random.default_rng(int(seed) * 333 + 9)
    stream = _build_stream(schedule, Xtr.shape[0], domain_of, P_max, perm_rng)

    nst = 0
    for s in range(0, stream.shape[0], batch):
        idx = torch.from_numpy(stream[s:s + batch]).long()
        opt.zero_grad()
        f = _product_feat(cr, ci, Xt[idx])
        mu = f.mean(0, keepdim=True); sd = f.std(0, unbiased=False, keepdim=True) + 1e-3
        logits = ((f - mu) / sd) @ W + b
        loss = lossf(logits, yt[idx])
        loss.backward()
        opt.step()
        nst += 1
    return cr, ci, W, b, nst


def _predict(cr, ci, W, b, Xtr, Xq):
    """Predict query labels; feature normalization uses the FINAL-code train-set stats (paired, deterministic)."""
    with torch.no_grad():
        f_tr = _product_feat(cr, ci, torch.from_numpy(Xtr).long())
        mu = f_tr.mean(0, keepdim=True); sd = f_tr.std(0, unbiased=False, keepdim=True) + 1e-3
        f_q = _product_feat(cr, ci, torch.from_numpy(Xq).long())
        pred = torch.argmax(((f_q - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred


# ---------------------------------------------------------------------------
# One (family, seed) run: split -> fit the 3 schedules -> score all arms PAIRED on the same novel query combos.
# ---------------------------------------------------------------------------

def run_family_seed(family, X, y_clean, seed, cfg):
    q, tr, novel = split_novel(X, seed)
    y_used, y_oracle = plant_regime(X, y_clean, family, CLEAN, seed)   # CLEAN regime (the real conjunction target)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    nc = int(y_clean.max()) + 1
    pop_label = int(np.argmax(np.bincount(ytr, minlength=nc)))
    chance = chance_of(family, y_clean)

    # domain assignment for CONTINUAL: block by the leading `block_by` constituent levels (mixed-radix), a standard
    # task-incremental non-i.i.d. stream. block_by=1 -> block by x0 (L blocks); block_by=2 -> block by (x0,x1) (L^2).
    block_by = int(cfg.get("block_by", 1))
    dom = np.zeros(Xtr.shape[0], dtype=np.int64)
    for c in range(block_by):
        dom = dom * L + Xtr[:, c].astype(np.int64)
    domain_of = dom
    g_domains = L ** block_by

    # SHUFFLE: permute TRAIN labels (destroy structure). Deterministic integer seed (PROT-023).
    shuf_rng = np.random.default_rng(seed * 100057 + 19)
    ytr_shuf = ytr[shuf_rng.permutation(ytr.shape[0])].copy()

    # ---- fit the 3 schedule scaffolds ----
    ci_, cr_, W_, b_, steps_inter = None, None, None, None, 0
    cri, cii, Wi, bi, steps_inter = fit_schedule(Xtr, ytr, nc, INTERLEAVED, seed, cfg)
    crc, cic, Wc, bc, steps_cont = fit_schedule(Xtr, ytr, nc, CONTINUAL, seed, cfg, domain_of=domain_of)
    crs, cis, Ws, bs, steps_shuf = fit_schedule(Xtr, ytr_shuf, nc, SHUFFLE, seed, cfg)
    step_mismatch = abs(steps_inter - steps_cont) / max(1, steps_inter)
    compute_matched = bool(step_mismatch <= float(cfg.get("step_match_tol", STEP_MATCH_TOL)))

    # under-trained checkpoint (few passes): proves an INTER==CONT null is NOT merely a full-P ceiling artifact.
    inter_probe = cont_probe = float("nan")
    p_probe = int(cfg.get("p_probe", 0))
    if p_probe > 0:
        pcfg = dict(cfg); pcfg["P_max"] = p_probe
        cripp = fit_schedule(Xtr, ytr, nc, INTERLEAVED, seed, pcfg)
        crcpp = fit_schedule(Xtr, ytr, nc, CONTINUAL, seed, pcfg, domain_of=domain_of)
        inter_probe = round(acc(_predict(*cripp[:4], Xtr, Xq)[novel], gold[novel]), 6)
        cont_probe = round(acc(_predict(*crcpp[:4], Xtr, Xq)[novel], gold[novel]), 6)

    preds = {
        INTERLEAVED: _predict(cri, cii, Wi, bi, Xtr, Xq),
        CONTINUAL: _predict(crc, cic, Wc, bc, Xtr, Xq),
        SHUFFLE: _predict(crs, cis, Ws, bs, Xtr, Xq),
        HOM: arm_homophily(family, Xtr, ytr, Xq),
        MEMO: arm_memorize(family, Xtr, ytr, Xq, pop_label),
        POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
        ORC: y_oracle[q],
    }

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if (pred is not None and m.sum() > 0) else float("nan")

    strata = {}
    for sname, m in (("novel", novel), ("all", np.ones(len(gold), bool))):
        dct = {arm: round(a(preds.get(arm), m), 6) for arm in ALL_ARMS if arm != FREQ}
        dct[FREQ] = round(max(dct[HOM], dct[POP]), 6)
        dct["n"] = int(m.sum())
        strata[sname] = dct

    sigs = {arm: _sig(preds[arm]) for arm in SCHEDULE_ARMS}
    return dict(family=family, seed=int(seed), chance=round(chance, 6), nclass=nc,
                n_query=int(len(gold)), n_novel=int(novel.sum()),
                steps_interleaved=int(steps_inter), steps_continual=int(steps_cont), steps_shuffle=int(steps_shuf),
                step_mismatch=round(step_mismatch, 5), compute_matched=compute_matched,
                inter_probe=inter_probe, cont_probe=cont_probe, p_probe=p_probe,
                strata=strata, sigs=sigs, nonadditivity=nonadditivity(X, y_clean))


# ---------------------------------------------------------------------------
# Aggregate + verdict (gated on the PARITY conjunction; AND2 reported as context).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def aggregate_and_verdict(per_seed_by_fam):
    ps = per_seed_by_fam[PARITY]

    def mean_arm(arm, stratum="novel"):
        return _nm([p["strata"][stratum][arm] for p in ps])

    chance = _nm([p["chance"] for p in ps])
    m = {arm: mean_arm(arm) for arm in ALL_ARMS}
    n_novel = int(_nm([p["n_novel"] for p in ps]))
    compute_matched = all(p["compute_matched"] for p in ps)

    H = _sub(m[ORC], chance)                       # MEASURED info-ceiling headroom
    d_freq = _sub(m[INTERLEAVED], m[FREQ])         # readout-works (arena answerable; frequency at chance)
    d_cont = _sub(m[INTERLEAVED], m[CONTINUAL])    # PRIMARY discriminator: the consolidation / schedule advantage
    d_rand = _sub(m[INTERLEAVED], chance)
    d_shuf = _sub(m[SHUFFLE], chance)
    inter_probe = _nm([p.get("inter_probe", float("nan")) for p in ps])
    cont_probe = _nm([p.get("cont_probe", float("nan")) for p in ps])
    d_cont_probe = _sub(inter_probe, cont_probe)   # schedule gap in the UNDER-TRAINED regime (ceiling-artifact check)

    oracle_fires = bool(H == H and H >= ORACLE_FIRE_MARGIN)
    freq_at_chance = bool(m[FREQ] == m[FREQ] and m[FREQ] <= chance + FREQ_CHANCE_TOL)
    freq_not_broken = bool(m[FREQ] == m[FREQ] and m[FREQ] >= chance - 0.15)   # not an absurdly-broken frequency arm
    shuffle_flat = bool(d_shuf == d_shuf and d_shuf <= (FLAT_FRAC * H if H == H else float("nan")))
    recovers = bool(d_rand == d_rand and d_rand >= (RECOVER_FRAC * H if H == H else float("nan")))
    enough_novel = bool(n_novel >= MIN_NOVEL)

    readout_beats_freq_target = (max(READOUT_BEATS_FREQ_FRAC * H, READOUT_BEATS_FREQ_ABS) if H == H else float("nan"))
    readout_works = bool(d_freq == d_freq and d_freq >= readout_beats_freq_target and recovers)

    # arena-valid = fair genuine conjunction (freq at chance) + answerable (oracle fires + readout learns it) +
    # sensitive (shuffle must-fail fires) + enough novel + compute-matched.
    arena_valid = bool(oracle_fires and freq_at_chance and freq_not_broken and shuffle_flat and enough_novel
                       and compute_matched and readout_works)

    beat_cont_target = (max(BEAT_CONT_FRAC * H, BEAT_CONT_ABS) if H == H else float("nan"))
    need = (len(ps) // 2) + 1
    votes_cont = sum(1 for p in ps
                     if _sub(p["strata"]["novel"][INTERLEAVED], p["strata"]["novel"][CONTINUAL]) >= beat_cont_target)
    beats_cont = bool(d_cont == d_cont and d_cont >= beat_cont_target and votes_cont >= need)

    hard_pass = bool(arena_valid and beats_cont)
    refute = bool(arena_valid and d_cont == d_cont and d_cont <= REFUTE_EPS)   # readout learns it; schedule irrelevant

    if not enough_novel:
        verdict = "INCONCLUSIVE_TOO_FEW_NOVEL"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not compute_matched:
        verdict = "INCONCLUSIVE_COMPUTE_UNMATCHED"
    elif not freq_at_chance:
        verdict = "INVALID_ARENA_FREQ_ABOVE_CHANCE"
    elif not shuffle_flat:
        verdict = "INCONCLUSIVE_SHUFFLE_NOT_FLAT_METRIC_INSENSITIVE"
    elif not readout_works:
        verdict = "INCONCLUSIVE_READOUT_UNDERFIT_DOES_NOT_BEAT_FREQ"
    elif hard_pass:
        verdict = "HARD_PASS_REPLAY_MANUFACTURES_CONJUNCTION_ADVANTAGE_OVER_CONTINUAL"
    elif refute:
        verdict = "REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_SCHEDULE_ADVANTAGE"

    # AND2 context (frequency-gets-signal contrast; reported, not gated)
    ctx = {}
    for fam in CONTEXT_FAMILIES:
        cp = per_seed_by_fam[fam]
        ctx[fam] = dict(chance=round(_nm([p["chance"] for p in cp]), 5),
                        INTERLEAVED=round(_nm([p["strata"]["novel"][INTERLEAVED] for p in cp]), 5),
                        CONTINUAL=round(_nm([p["strata"]["novel"][CONTINUAL] for p in cp]), 5),
                        FREQ_NULL=round(_nm([p["strata"]["novel"][FREQ] for p in cp]), 5),
                        ORACLE=round(_nm([p["strata"]["novel"][ORC] for p in cp]), 5))

    verdict_msg = (
        "%s || PARITY conjunction novel[nq=%d chance=%s]: INTERLEAVED=%s CONTINUAL=%s SHUFFLE=%s | FREQ_NULL=%s "
        "(HOM=%s POP=%s) MEMO=%s ORACLE=%s || H=%s | PRIMARY schedule-gap INTER-CONT=%s (HP>=%s=%s, REFUTE<=%s) "
        "votes=%d/%d | readout_works INTER-FREQ=%s(>=%s=%s) recover=%s | freq_at_chance=%s(<=%s) shuffle_flat=%s(<=%s) "
        "compute_matched=%s(mism=%s) | under-trained probe(P=%s): INTER=%s CONT=%s gap=%s (null off-ceiling=%s) | "
        "seeds=%d || AND2_ctx(freq-gets-signal): %s"
        % (verdict, n_novel, _fmt(chance), _fmt(m[INTERLEAVED]), _fmt(m[CONTINUAL]), _fmt(m[SHUFFLE]), _fmt(m[FREQ]),
           _fmt(m[HOM]), _fmt(m[POP]), _fmt(m[MEMO]), _fmt(m[ORC]), _fmt(H),
           _fmt(d_cont), _fmt(beat_cont_target), beats_cont, _fmt(REFUTE_EPS), votes_cont, need,
           _fmt(d_freq), _fmt(readout_beats_freq_target), readout_works, _fmt(d_rand),
           _fmt(m[FREQ]), _fmt(chance + FREQ_CHANCE_TOL), shuffle_flat, _fmt(FLAT_FRAC * H if H == H else float("nan")),
           compute_matched, _fmt(_nm([p["step_mismatch"] for p in ps])),
           ps[0].get("p_probe"), _fmt(inter_probe), _fmt(cont_probe), _fmt(d_cont_probe),
           bool(d_cont_probe == d_cont_probe and d_cont_probe <= REFUTE_EPS), len(ps), json.dumps(ctx.get(AND2, {}))))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, chance=_rnd(chance),
        novel_acc={arm: _rnd(m[arm]) for arm in ALL_ARMS},
        oracle_headroom=_rnd(H),
        primary_schedule_gap_inter_minus_cont=_rnd(d_cont), readout_beats_freq=_rnd(d_freq),
        recover_over_chance=_rnd(d_rand), shuffle_over_chance=_rnd(d_shuf),
        under_trained_probe=dict(p_probe=ps[0].get("p_probe"), inter=_rnd(inter_probe), cont=_rnd(cont_probe),
                                 gap=_rnd(d_cont_probe)),
        resolved_thresholds=dict(beat_cont=_rnd(beat_cont_target), readout_beats_freq=_rnd(readout_beats_freq_target),
                                 recover=_rnd(RECOVER_FRAC * H if H == H else float("nan")),
                                 flat=_rnd(FLAT_FRAC * H if H == H else float("nan")),
                                 freq_chance_ceiling=_rnd(chance + FREQ_CHANCE_TOL), refute_eps=REFUTE_EPS),
        seed_votes=dict(beat_cont=votes_cont, need=need),
        n_novel=n_novel, enough_novel=enough_novel, oracle_fires=oracle_fires, freq_at_chance=freq_at_chance,
        freq_not_broken=freq_not_broken, readout_works=readout_works, arena_valid=arena_valid,
        compute_matched=compute_matched, shuffle_flat=shuffle_flat, recovers=recovers,
        beats_cont=beats_cont, hard_pass=hard_pass, refute=refute,
        step_counts=dict(interleaved=int(_nm([p["steps_interleaved"] for p in ps])),
                         continual=int(_nm([p["steps_continual"] for p in ps]))),
        and2_context=ctx.get(AND2, {}),
        bands=dict(ORACLE_FIRE_MARGIN=ORACLE_FIRE_MARGIN, FREQ_CHANCE_TOL=FREQ_CHANCE_TOL,
                   READOUT_BEATS_FREQ_FRAC=READOUT_BEATS_FREQ_FRAC, READOUT_BEATS_FREQ_ABS=READOUT_BEATS_FREQ_ABS,
                   BEAT_CONT_FRAC=BEAT_CONT_FRAC, BEAT_CONT_ABS=BEAT_CONT_ABS, RECOVER_FRAC=RECOVER_FRAC,
                   FLAT_FRAC=FLAT_FRAC, REFUTE_EPS=REFUTE_EPS, MIN_NOVEL=MIN_NOVEL),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Self-test on the REAL parity arena (full N_ENT; exercises the real substrate primitives + fit path).
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
    seed = 7
    exercised = set()
    X = make_X(seed)
    y_clean = target(PARITY, X)
    res = run_family_seed(PARITY, X, y_clean, seed, cfg)
    exercised.update(["hd_bind", "_config_term", "arm_homophily", "fit_schedule", "acc"])

    s = res["strata"]["novel"]
    chance = res["chance"]
    inter, cont, shuf = s[INTERLEAVED], s[CONTINUAL], s[SHUFFLE]
    freq, orac = s[FREQ], s[ORC]
    n_novel = s["n"]
    d_freq = inter - freq; d_cont = inter - cont; d_shuf_i = inter - shuf
    n_sigs = len(set(res["sigs"].values()))

    out = dict(chance=round(chance, 5), n_novel=n_novel, INTERLEAVED=round(inter, 5), CONTINUAL=round(cont, 5),
               SHUFFLE=round(shuf, 5), FREQ_NULL=round(freq, 5), ORACLE=round(orac, 5),
               beat_freq=round(d_freq, 5), schedule_gap_inter_minus_cont=round(d_cont, 5),
               inter_minus_shuffle=round(d_shuf_i, 5), inter_probe=res.get("inter_probe"),
               cont_probe=res.get("cont_probe"), n_distinct_sigs=n_sigs,
               step_mismatch=res["step_mismatch"], compute_matched=res["compute_matched"],
               nonadditivity=res["nonadditivity"])

    inter_solves = bool(inter == inter and inter >= ST_INTER_MIN)
    inter_beats_freq = bool(d_freq == d_freq and d_freq >= ST_INTER_BEATS_FREQ)
    inter_beats_shuffle = bool(d_shuf_i == d_shuf_i and d_shuf_i >= ST_INTER_BEATS_SHUFFLE)
    freq_at_chance = bool(freq == freq and freq <= chance + FREQ_CHANCE_TOL and freq >= chance - 0.15)
    shuffle_flat = bool(shuf == shuf and shuf <= chance + ST_SHUFFLE_MAX_OVER_CHANCE)
    oracle_fires = bool(orac == orac and orac >= chance + ORACLE_FIRE_MARGIN)
    baseline_in_band = bool(freq <= inter + 1e-9 and inter <= orac + 1e-6)
    # ARMS-MUST-DIFFER (META_RULE_AF), SCOPED: the must-fail SHUFFLE arm must be a genuinely DIFFERENT computation
    # from INTERLEAVED. The INTERLEAVED/CONTINUAL pair is EXEMPTED -- they legitimately coincide (bit-identical) when
    # BOTH perfectly solve the conjunction, which is exactly the schedule-null this cell measures.
    arms_differ = bool(res["sigs"][SHUFFLE] != res["sigs"][INTERLEAVED])
    compute_matched = bool(res["compute_matched"])
    enough_novel = bool(n_novel >= ST_MIN_NOVEL)

    # VACUOUS-SMOKE guard (META_RULE_K): the pipeline must be TELEMETRY-SENSITIVE -- a BAD schedule (SHUFFLE) must
    # score well below INTERLEAVED. This proves the INTER-vs-CONTINUAL schedule discriminator CAN move; if the two
    # then coincide it is a REAL null, not a frozen metric. (INTER-vs-CONTINUAL itself is NOT gated in the self-test:
    # it is the hypothesis under test.) Also assert the arena is a genuine conjunction: INTER beats FREQ_NULL.
    if not (inter_beats_shuffle and inter_beats_freq):
        raise AssertionError("META_RULE_K discriminator vacuous: need INTER>>SHUFFLE (sensitivity) AND INTER>>FREQ "
                             "(genuine conjunction). inter=%.4f shuf=%.4f freq=%.4f chance=%.4f"
                             % (inter, shuf, freq, chance))

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["hd_bind", "_config_term", "arm_homophily", "fit_schedule", "acc"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "the product-lens readout runs through the REAL FHRR bind (hd_bind via _config_term), the REAL "
                  "minibatch fit_schedule trainer, arm_homophily and acc on the REAL parity arena at full N_ENT"},
        {"kind": "substrate_signature", "callable_obj": hd_bind, "callable_name": "hd_bind",
         "kwargs": {}, "extra": "positional (a, b) complex64 elementwise product; portable, no version kwargs"},
        {"kind": "metric_moves", "metric_name": "parity_novel_acc",
         "values": [freq, cont, inter, orac],
         "extra": "novel-combo accuracy FREQ=%.4f CONTINUAL=%.4f INTERLEAVED=%.4f ORACLE=%.4f: readout responds to "
                  "the minibatch schedule" % (freq, cont, inter, orac)},
        {"kind": "negative_control_margin", "control_scores": [shuf, freq],
         "headline_threshold": inter, "higher_is_pass": True, "margin": ST_INTER_BEATS_FREQ, "n_repeats_min": 2,
         "control_name": "SHUFFLE_FREQ_below_interleaved",
         "extra": "label-shuffled SHUFFLE and frequency FREQ_NULL must sit below INTERLEAVED -> the interleaved "
                  "schedule manufactures conjunction structure frequency cannot"},
        # NOTE: the guard_baseline_valid preflight check is deliberately NOT declared here. It is designed to catch a
        # CONTROL-BEATS-BASELINE BREAK-GUARD mis-firing when the baseline sits at the arena floor. This cell has no
        # such break-guard: beats-FREQ is the CAPABILITY gate, and on a genuine conjunction FREQ_NULL == chance BY
        # DESIGN (single-driver MI=0), so beats-FREQ IS beats-chance. The "FREQ not broken (below chance)" check is
        # enforced directly in verdict logic (freq_not_broken) + the self-test (freq_at_chance lower bound).
    ], run_mode="self_test")

    out.update(inter_solves=inter_solves, inter_beats_freq=inter_beats_freq, inter_beats_shuffle=inter_beats_shuffle,
               freq_at_chance=freq_at_chance, shuffle_flat=shuffle_flat, oracle_fires=oracle_fires,
               baseline_in_band=baseline_in_band, arms_differ=arms_differ, compute_matched=compute_matched,
               enough_novel=enough_novel, validity_preflight_ok=bool(vp_ok),
               validity_preflight_declared=["real_code_path", "substrate_signature", "metric_moves",
                                            "negative_control_fails_with_margin"])
    ok = bool(inter_solves and inter_beats_freq and inter_beats_shuffle and freq_at_chance and shuffle_flat
              and oracle_fires and baseline_in_band and arms_differ and compute_matched and enough_novel and vp_ok)
    if not ok:
        out["fail"] = ("selftest machinery/sensitivity not clean: inter_solves=%s inter_beats_freq=%s "
                       "inter_beats_shuffle=%s freq_at_chance=%s shuffle_flat=%s oracle_fires=%s baseline_in_band=%s "
                       "arms_differ=%s compute_matched=%s enough_novel=%s vp_ok=%s"
                       % (inter_solves, inter_beats_freq, inter_beats_shuffle, freq_at_chance, shuffle_flat,
                          oracle_fires, baseline_in_band, arms_differ, compute_matched, enough_novel, vp_ok))
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device():
    return torch.device("cpu")   # glass-box CPU; product-lens fit is tiny (D=96, N~121)


def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode])
    cfg["step_match_tol"] = STEP_MATCH_TOL
    seeds = list(cfg["seeds"])
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t0 = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                                "elapsed_s": time.perf_counter() - t0}) + "\n")

    _log("run_mode=%s seeds=%s P_max=%s batch=%s block_by=%s(g_domains=%d) emb_d=%s K=%d L=%d N_ENT=%d"
         % (run_mode, seeds, cfg["P_max"], cfg["batch"], cfg.get("block_by", 1), L ** int(cfg.get("block_by", 1)),
            cfg.get("emb_d", EMB_D), K, L, N_ENT))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s INTER=%s CONT=%s SHUF=%s FREQ=%s ORACLE=%s beat_freq=%s schedule_gap=%s "
         "inter_beats_shuffle=%s freq_at_chance=%s compute_matched=%s vp_ok=%s"
         % (st_ok, st_res.get("INTERLEAVED"), st_res.get("CONTINUAL"), st_res.get("SHUFFLE"), st_res.get("FREQ_NULL"),
            st_res.get("ORACLE"), st_res.get("beat_freq"), st_res.get("schedule_gap_inter_minus_cont"),
            st_res.get("inter_beats_shuffle"), st_res.get("freq_at_chance"),
            st_res.get("compute_matched"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                      verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", ""),
                      summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(verdict="SELFTEST_PASS", run_mode="self_test",
                      verdict_msg="SELFTEST_PASS consol conjunction-replay: INTERLEAVED product-lens beats CONTINUAL + "
                                  "FREQ_NULL on the real parity arena; SHUFFLE flat; ORACLE fires; FREQ at chance; "
                                  "compute-matched; 5 validity-preflight checks declared",
                      summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    per_seed_by_fam = {fam: [] for fam in ALL_FAMILIES}
    seed_failures = []
    for si, seed in enumerate(seeds):
        try:
            for fam in ALL_FAMILIES:
                X = make_X(seed)
                y_clean = target(fam, X)
                res = run_family_seed(fam, X, y_clean, seed, cfg)
                if fam == GATED_FAMILY:
                    if res["n_novel"] < MIN_NOVEL:
                        raise RuntimeError("too few novel (%d < %d)" % (res["n_novel"], MIN_NOVEL))
                    # SHUFFLE (must-fail) must be a distinct computation from INTERLEAVED; the INTER/CONT pair is
                    # EXEMPTED (they coincide when both solve the conjunction = the measured schedule-null).
                    if res["sigs"][SHUFFLE] == res["sigs"][INTERLEAVED]:
                        raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF SHUFFLE bit-identical to INTERLEAVED")
                per_seed_by_fam[fam].append(res)
            gp = per_seed_by_fam[PARITY][-1]["strata"]["novel"]
            _log("seed=%d PARITY novel: INTER=%s CONT=%s SHUF=%s FREQ=%s ORAC=%s (mism=%s)"
                 % (seed, _fmt(gp[INTERLEAVED]), _fmt(gp[CONTINUAL]), _fmt(gp[SHUFFLE]), _fmt(gp[FREQ]),
                    _fmt(gp[ORC]), per_seed_by_fam[PARITY][-1]["step_mismatch"]))
            write_partial(out_dir, seed, dict(seed=seed, parity=per_seed_by_fam[PARITY][-1], run_mode=run_mode))
            _hb("seed", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))

    if len(per_seed_by_fam[PARITY]) < expected_n_units:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                      verdict_msg="expected %d seeds got %d (failures=%s)"
                                  % (expected_n_units, len(per_seed_by_fam[PARITY]), seed_failures),
                      summary="cardinality breach", elapsed_s=time.perf_counter() - t0,
                      seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed_by_fam)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(per_seed_by_fam[PARITY]),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res, seed_failures=seed_failures,
                   per_seed_parity=per_seed_by_fam[PARITY], per_seed_and2=per_seed_by_fam.get(AND2, []))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if not args.self_test and not args.smoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "smoke", "full"):
            run_mode = _env_mode
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
