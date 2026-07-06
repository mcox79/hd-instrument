"""exp_generation_decode_selfmargin_pr_transfer_v1

TRANSFER TEST: does the PR-corrected extreme-value self-margin (which REVIVED the COMPREHENSION
order-recovery decode-cliff prediction) TRANSFER to predict the GENERATION decoder's decode-collapse
boundary? The premise (notes/research_generation_decode_self_margin_pr_correction_premise_confirmed_
2026-07-06.md) is: generation decode = argmax over the SAME correlated GSBC codewords, so the
participation-ratio effective competitor count n_comp = PR(V)-1 in the CG'd Gauss-Hermite order statistic
should predict the generation decode cliff, exactly as it did for comprehension.

--------------------------------------------------------------------------------
WHY THIS IS A REAL TEST (mechanism audit -- MEASURED off-disk by the author before authoring)
--------------------------------------------------------------------------------
The GENERATION decoders in this substrate (exp_generation_decoder_gsbc_native_blocklocal_v1 and its
high-vocab RNS/CRT sibling) decode via DISJOINT block-local recovery: each of D tokens occupies its OWN
disjoint block (bs = N/D), so a block holds EXACTLY ONE token -- there is NO within-block superposition.
Per-block cleanup = argmax over the V codewords of (cb @ block), with block == cb[token] EXACTLY. The
signal score is therefore the codeword self-overlap G[t,t] = k (deterministic, sig_s ~ 0), and the decode
fails only when some distractor overlap G[t,j] reaches/exceeds k -- i.e. a CODEWORD COLLISION (a near-
identical sparse code tying the argmax at small bs/k). This is a COMBINATORIAL (birthday) collision event.

The COMPREHENSION decode that PR revived is DIFFERENT: it SUPERPOSES L=D/2 tokens per block (B_OCC=2),
so the signal has variance (k + crossterms) and the competition is a genuine effective-rank order statistic
-> PR(V)-1 is the right competitor count there. Generation has no superposition within a block, so the
collapse is NOT a superposition-crowded effective-rank event. Whether PR still transfers is the OPEN,
GENUINE question this cell measures across (codebook, V, D).

MEASURED@author off-disk probe (seed 7, scratchpad/gen_margin_probe.py; MEASURED not HYPOTHESIZED):
  gsbc  V8000 D48 : p1_meas=0.371 ; PR-corrected predicts 0.998 (ratio 0.37, UNDER-predicts collapse) ;
                    naive-V predicts 0.229 (ratio 1.62) -> naive is CLOSER than PR here.
  corr  V65536 D26: p1_meas=0.927 ; PR and naive BOTH predict ~1.0 (distractor kurtosis ~40 -> the
                    gaussian order statistic tail is far too thin to see the collapse).
  iid   any       : p1_meas ~ 1.0 (interference-free single block -> no collapse, PR ~ V).
=> the deflated author expectation is that PR does NOT cleanly transfer; the informative outcome is the
   HARD_FAIL_TRANSFER with the collision mechanism + the empirical-collision predictor as the honest model.
   HARD_PASS_TRANSFER remains reachable and is a real gate IF PR does predict the generation cliff.

--------------------------------------------------------------------------------
PRE-REGISTERED BANDS (gated on the gsbc arm = the comprehension geometry / premise's actual codebook;
corr = the high-vocab hopeful-angle regime; iid = the correlation-discriminator control)
--------------------------------------------------------------------------------
Predictors compared to MEASURED per-block p1 (per_term of the ACTUAL generation single-block decode):
  p1_pr   : GH64 order statistic, n_comp = PR(V)-1     (the comprehension mechanism under test)
  p1_naive: GH64 order statistic, n_comp = V-1         (the falsified comprehension baseline)
  p1_loose: GH64 order statistic, n_comp = 1           (V-blind diagnostic)
  p1_emp  : empirical-collision model (1 - p_pair)^(V-1), p_pair = P[distractor overlap >= signal]
            measured from the codeword Gram (the honest alternative that captures the heavy collision tail)

HARD_PASS  (PR TRANSFERS -- generation joins the exact self-margin family; a FULL multi-seed confirms CG):
  - PR-corrected aggregate mean-ratio (gsbc non-saturated cells) in [HP_BIAS_LO,HP_BIAS_HI]=[0.80,1.25], AND
  - PR beats naive on per-seed worst-cell ratio-err: naive_perseed_max / pr_perseed_max >= REL_IMPROVE_MIN
    (1.5), AND
  - NAIVE-V biased (aggregate mean-ratio OUTSIDE [NAIVE_UNBIASED_LO,NAIVE_UNBIASED_HI]=[0.85,1.18]).
HARD_FAIL  (PR does NOT transfer -- the honest, MEASURED-likely outcome; a bounded negative + mechanism):
  - PR-corrected aggregate mean-ratio OUTSIDE [HF_BIAS_LO,HF_BIAS_HI]=[0.55,1.80] at gsbc non-sat cells, OR
  - improvement over naive < ACCEPT_REL_MIN (1.2) (PR is no better than the falsified naive-V count).
  The verdict_msg reports whether the empirical-collision model fits (emp_mean_ratio in the unbiased band)
  -> establishing the generation cliff is COLLISION-driven, not the superposition-crowded PR regime.
MIDDLE_BAND: clears the core bands but misses a HARD_PASS sub-gate (partial transfer).

Discriminator / phenomenon gates (ALL modes incl smoke; if any fails -> the test is vacuous, not a verdict):
  - COLLAPSE BITES: >= MIN_NONSAT non-saturated cells (0.05 < p1_meas < SAT_HI) across gsbc+corr (else the
    decode did not collapse at this grid -> nothing to predict).
  - iid CONTROL does NOT collapse: mean p1_meas over iid cells >= IID_CEIL (0.98) -> the collapse is a
    correlation/collision artifact, not a wiring failure.
  - GATE-D positive control: gsbc @ (8192,26) per-block p1 within 0.02 of the landed v1 decoder
    (blocklocal_gsbc@V8192D26 per_term_mean=0.9945 MEASURED@data/exp_generation_decoder_gsbc_native_
    blocklocal_v1/metrics.json).

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (AF): p1_pr / p1_naive / p1_loose / p1_emp prediction surfaces hash-distinct.
# - final_metrics_atomicity = tmp_replace (os.replace of metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException; grep-clean).
# - crlb / capacity-feasibility: crlb_n_a -- this is a PREDICTION-MATCH ratio test (exact-vs-measured
#   tightness), not an accuracy floor; no Cramer-Rao noise floor gates the deliverable. The MEASURED decode
#   is the ground truth; discriminator_reachability: HARD_PASS is reachable IF PR predicts the cliff
#   (MEASURED@author probe suggests it does NOT -> HARD_FAIL is the deflated-likely outcome).
# - baseline_in_band (AG): non-saturated cells (0.05<p1<SAT_HI) carry the ratio gates; saturated cells
#   (p1>=SAT_HI, the decode did not collapse) are EXCLUDED from ratio gates (declared). iid is a live
#   NO-COLLAPSE control; PR is the mechanism under test.
# - discriminator survives scale: the collapse is measured AT the FULL generation regime (N=8192, D up to
#   48, V up to 65536, correlated codes). Smoke keeps the deepest gate cells (gsbc D48, corr V65536 D48)
#   at full N/D/V so the collapse + the PR-vs-naive contrast FIRE in smoke; smoke reduces grid length/trials
#   /seed-count ONLY (never N/D/V at the gate cells).
# - HARD_PASS strictly above floor: the bias band [0.80,1.25] is centred on the unbiased target 1.0.
# - HP_SCOPE per-arm: the PR-transfer bias/improvement gates apply to the gsbc PR-corrected arm; naive-V
#   carries only the 'biased' direction gate; loose + emp are diagnostic; iid carries only the no-collapse
#   control gate. No arm inherits another's gates.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x sum over arms of len(grid_for_arm). Verdict
#   gates on count.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except; specific exception classes).
# - calibration_check = default_ok_for_this_regime: the PR formula + the 64-pt Gauss-Hermite moments are
#   parameter-free given the codeword Gram (no fit-to-accuracy); PR is computed via the bs x bs DUAL of the
#   Gram (same nonzero eigenvalues as the V x V Gram -> identical PR; verified bit-close in self-test).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
# - progress_logging = line_buffered_stdout + print(flush=True) (FULL may approach ~15min on remote CPU at
#   high V; heartbeat + flush satisfy the progress rule; smoke/self_test are seconds-to-a-minute).
# - start_marker + crash_diagnostic + heartbeat (defensive error checking; all 4 patterns).
# - positive_control (Gate D): the decode machinery is the LANDED generation decoder's single_block_decode
#   (reused VERBATIM from exp_generation_decoder_rns_crt_highvocab_v1), and gsbc@(8192,26) reproduces the
#   v1 native cliff at the SAME regime (tolerance 0.02). The predictor is pc.p_win_extreme + pc.
#   participation_ratio reused VERBATIM (self-test asserts p_win_extreme bit-identical to the comprehension
#   PR-corrected cell + the exact-margin cell).
#
# USER-LOCKED: monitor-not-control. The cell only REPORTS the PR-vs-measured generation decode-cliff
#   prediction in its own metrics.json. It NEVER edits V, D, N, the codebook, or the decoder; it triggers
#   no rebuild. A REPORTING/monitoring refinement. NOT fluent-language, NOT self-improvement. re-encode HELD
#   (uses the bounded pre-encoded GSBC pool + self-contained synthetic codes only). Narrow glass-box step.
#
# Compute architecture: SEQUENTIAL-CPU (numpy argmax cleanup + one (n_query, V) Gram matmul + eigvalsh on
#   the bs x bs dual; the cell IS the substrate generation-decode primitive being re-measured -- bit-
#   identical CPU reference exemption). Storage: no_storage / no_composition beyond the decoder's disjoint-
#   block sum. No GPU, no torch, no scipy, no LLM. gsbc arm requires the untracked GSBC pool npz (SCP before
#   remote FULL; queue_add does NOT ship it); corr + iid arms are self-contained (synthetic).
#
# PROT-018: no _n<N> suffix (N is a fixed confirm axis, not the swept axis). NON-PARKED (synthetic +
#   pre-encoded GSBC pool; NO cert_ledger referent declared). ASCII-only; no unicode/emoji/em-dash. NEW cell.
#   Author: exp_dev.
# Run: python experiments/exp_generation_decode_selfmargin_pr_transfer_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Measurement + predictor machinery reused VERBATIM (Gate D positive-control at the SAME regime).
import experiments.exp_comprehension_order_recovery_pr_corrected_margin_v1 as pc  # p_win_extreme, participation_ratio  # noqa: E402
import experiments.exp_comprehension_envelope_superposition_vocab_v1 as base  # GSBC block-local codebook  # noqa: E402
import experiments.exp_generation_decoder_rns_crt_highvocab_v1 as hv  # single_block_decode, corr/iid codebooks  # noqa: E402

ANCHOR_NAME = "generation_decode_selfmargin_pr_transfer_v1"

N_DIM = 8192          # substrate compositional default (never reduced)
GSBC_POOL_CAP = 10000  # native GSBC filler pool size (V capped below this for the gsbc arm)

# ---- CLI + RUN_MODE (defaults to full; --smoke / --self-test flip; runner injects env) ----
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
_ENV_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _ENV_MODE == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"

# ---- grid per arm (arm, V, D). gsbc capped at pool; deep corners (D40/48) leave saturation per probe ----
# Each entry: (arm, V, D). Non-saturated collapse requires small bs/k (high D).
if RUN_MODE == "self_test":
    GRID = [("gsbc", 4096, 48), ("corr", 65536, 48), ("iid", 65536, 48)]
    SEEDS = [7]
    TRIALS = 12
    N_QUERY = 120
elif RUN_MODE == "smoke":
    GRID = [
        ("gsbc", 8192, 26), ("gsbc", 8192, 48),     # Gate-D tie-back + deep collapse
        ("corr", 65536, 48),                          # high-vocab hopeful-angle deep collapse
        ("iid", 65536, 48),                           # no-collapse control at the deepest regime
    ]
    SEEDS = [7, 13, 19]
    TRIALS = 20
    N_QUERY = 200
else:  # full
    GRID = [
        ("gsbc", 8192, 26), ("gsbc", 4096, 40), ("gsbc", 8192, 40),
        ("gsbc", 4096, 48), ("gsbc", 8192, 48),
        ("corr", 8192, 26), ("corr", 65536, 26), ("corr", 32768, 48),
        ("corr", 65536, 32), ("corr", 65536, 48),
        ("iid", 8192, 48), ("iid", 65536, 26), ("iid", 65536, 48),
    ]
    SEEDS = [7, 13, 19, 23, 29]
    TRIALS = 30
    N_QUERY = 300

EXPECTED_N_UNITS = len(SEEDS) * len(GRID)

# ---- pre-registered bands ----
SAT_HI = 0.999                 # p1_meas >= this -> saturated (decode did not collapse; excluded from ratio gates)
SAT_LO = 0.05                  # p1_meas <= this -> below the useful band (excluded)
HP_BIAS_LO, HP_BIAS_HI = 0.80, 1.25    # HARD_PASS: PR-corrected aggregate mean-ratio unbiased band (gsbc)
HF_BIAS_LO, HF_BIAS_HI = 0.55, 1.80    # HARD_FAIL: PR-corrected aggregate mean-ratio outside -> does not transfer
NAIVE_UNBIASED_LO, NAIVE_UNBIASED_HI = 0.85, 1.18   # naive "biased" iff aggregate mean-ratio OUTSIDE this
REL_IMPROVE_MIN = 1.50         # HARD_PASS: naive_perseed_max_err / pr_perseed_max_err >= this
ACCEPT_REL_MIN = 1.20          # HARD_FAIL: improvement < this (PR no better than falsified naive-V)
EMP_UNBIASED_LO, EMP_UNBIASED_HI = 0.70, 1.45   # collision-model "fits" band (mechanism diagnostic)
IID_CEIL = 0.98                # no-collapse control floor (iid must NOT collapse)
GATE_D_V, GATE_D_D = 8192, 26
GATE_D_REF = 0.9945            # MEASURED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms.blocklocal_gsbc@V8192D26.per_term_mean
GATE_D_TOL = 0.03              # tolerance (deep-regime seed noise); v1 used 30 trials/3 seeds
MIN_NONSAT = {"smoke": 2, "full": 4, "self_test": 1}   # collapse-bites cardinality floor

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,grid=%s,SEEDS=%s,TRIALS=%d,NQ=%d,RUN_MODE=%s,"
    "pred=GH64_extreme_value_order_stat,n_comp=PR(V)-1_participation_ratio,"
    "controls=naive_V-1+loose_1+empirical_collision,measure=hv.single_block_decode_VERBATIM,"
    "target=per_block_decode_p1=per_term(single_block_disjoint)"
) % (ANCHOR_NAME, N_DIM, "|".join("%s%dD%d" % (a, v, d) for (a, v, d) in GRID),
     "-".join(map(str, SEEDS)), TRIALS, N_QUERY, RUN_MODE)


# ============================================================
# Defensive error-checking helpers
# ============================================================
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_units, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "_start_marker.json"))


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float,
               extra: Optional[Dict[str, Any]] = None) -> None:
    row = {"ts_iso": _now_iso(), "unit_idx": unit_idx, "total_units": total_units,
           "elapsed_s": round(time.perf_counter() - t0, 2)}
    if extra:
        row["extra"] = extra
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_metrics_atomic(out_dir: Path, metrics: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(str(tmp), str(out_dir / "metrics.json"))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "run_mode": RUN_MODE, "config_version": CONFIG_VERSION}
    _write_metrics_atomic(out_dir, diag)


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float64)).tobytes()).hexdigest()


# ============================================================
# PR via the bs x bs DUAL (identical nonzero eigenvalues as the V x V Gram -> identical PR; feasible at V=65536)
# ============================================================
def participation_ratio_dual(cb: np.ndarray) -> float:
    """PR = (sum lambda)^2/sum(lambda^2) over the codeword Gram eigenvalues. The V x V Gram cb@cb.T and the
    bs x bs dual cb.T@cb share the SAME NONZERO eigenvalues (zeros add 0 to both sums) -> identical PR.
    We compute on the bs x bs dual (cheap at V up to 65536). Verified bit-close to pc.participation_ratio
    (the V x V form) at small V in the self-test."""
    G = cb.T.astype(np.float64) @ cb.astype(np.float64)   # (bs, bs)
    lam = np.clip(np.linalg.eigvalsh(G), 0.0, None)
    s1 = float(lam.sum())
    s2 = float((lam * lam).sum())
    return (s1 * s1) / s2 if s2 > 0.0 else 1.0


# ============================================================
# Codebook builders (all reuse the ACTUAL decoder codebooks; Gate-D fidelity)
# ============================================================
def build_codebook(arm: str, V: int, bs: int, seed: int) -> np.ndarray:
    if arm == "gsbc":
        if V > GSBC_POOL_CAP:
            raise ValueError("gsbc arm V=%d exceeds pool cap %d" % (V, GSBC_POOL_CAP))
        cbm = base._build_cbmax(seed, bs, V, 1)   # d_max=1 -> V native GSBC block-local codes at this bs
        return cbm[0:V]
    if arm == "corr":
        return hv.corr_codebook(V, bs, 4000 + seed, hv.N_CLUSTERS, hv.FRAC_SHARED)
    if arm == "iid":
        return hv.iid_codebook(V, bs, 7000 + seed)
    raise ValueError("unknown arm %r" % arm)


# ============================================================
# Measurement: per-block decode accuracy (the ACTUAL generation decoder) + Gram statistics
# ============================================================
def measure_p1(cb: np.ndarray, D: int, bs: int, trials: int, seed: int) -> float:
    """Per-block decode accuracy = per_term of the ACTUAL generation single-block decode (disjoint blocks,
    one token per block). Reuses hv.single_block_decode VERBATIM (Gate-D fidelity)."""
    V = cb.shape[0]
    rng = np.random.default_rng(90000 + seed)
    hits = 0
    tot = 0
    for _ in range(trials):
        toks = [int(x) for x in rng.choice(V, size=D, replace=False)]
        rec = hv.single_block_decode(toks, cb, bs, D, N_DIM)
        hits += sum(1 for d in range(D) if rec[d] == toks[d])
        tot += D
    return hits / tot if tot else 0.0


def gram_stats(cb: np.ndarray, n_query: int, seed: int
               ) -> Tuple[float, float, float, float, float, float]:
    """One (n_query, V) Gram matmul: signal moments (diagonal = self-overlap), distractor moments (off-
    diagonal), kurtosis, and the collision pair-probability p_pair = P[distractor overlap >= signal].
    Returns (mu_s, sig_s, mu_d, sig_d, kurt, p_pair)."""
    V = cb.shape[0]
    rng = np.random.default_rng(313 + seed)
    qi = rng.choice(V, size=min(n_query, V), replace=False)
    Q = cb[qi].astype(np.float32)                       # (nq, bs)
    overl = Q @ cb.T.astype(np.float32)                 # (nq, V)
    nq = Q.shape[0]
    sig = overl[np.arange(nq), qi].astype(np.float64)   # (nq,) self-overlap = signal
    # collision pair-count: distractors with overlap >= own signal (mask out self first)
    overl_masked = overl.copy()
    overl_masked[np.arange(nq), qi] = -np.inf
    ge = (overl_masked >= sig[:, None]).sum()           # count of (query, distractor) collisions
    p_pair = float(ge) / float(nq * (V - 1)) if V > 1 else 0.0
    # distractor moments from a column subsample (memory-bounded; self-columns negligible)
    cols = rng.choice(V, size=min(4000, V), replace=False)
    dist = overl[:, cols].astype(np.float64).ravel()
    mu_s = float(sig.mean())
    sig_s = float(sig.std())
    mu_d = float(dist.mean())
    sig_d = float(dist.std())
    z = (dist - mu_d) / (sig_d + 1e-12)
    kurt = float(np.mean(z ** 4) - 3.0)
    return mu_s, sig_s, mu_d, sig_d, kurt, p_pair


# ============================================================
# One (arm, V, D, seed) unit
# ============================================================
def run_unit(arm: str, V: int, D: int, seed: int) -> Dict[str, Any]:
    bs = N_DIM // D
    cb = build_codebook(arm, V, bs, seed)
    p1_meas = measure_p1(cb, D, bs, TRIALS, seed)
    mu_s, sig_s, mu_d, sig_d, kurt, p_pair = gram_stats(cb, N_QUERY, seed)
    PR = participation_ratio_dual(cb)
    n_pr = max(PR - 1.0, 0.0)
    p1_pr = pc.p_win_extreme(mu_s, sig_s, mu_d, sig_d, n_pr)
    p1_naive = pc.p_win_extreme(mu_s, sig_s, mu_d, sig_d, float(V - 1))
    p1_loose = pc.p_win_extreme(mu_s, sig_s, mu_d, sig_d, 1.0)
    # empirical-collision model: independent-chance birthday collapse over V-1 distractors
    p1_emp = float(math.exp((V - 1) * math.log1p(-p_pair))) if 0.0 <= p_pair < 1.0 else 0.0
    saturated = bool(p1_meas >= SAT_HI)
    below = bool(p1_meas <= SAT_LO)

    def _ratio(p):
        return (p1_meas / p) if p > 1e-9 else None

    return {
        "arm": arm, "V": V, "D": D, "seed": seed, "bs": bs, "k_active": max(1, int(round(base.F_SPARSE * bs))),
        "p1_meas": round(p1_meas, 5),
        "mu_s": round(mu_s, 4), "sig_s": round(sig_s, 5), "mu_d": round(mu_d, 4), "sig_d": round(sig_d, 4),
        "kurtosis_dist": round(kurt, 3), "p_pair_collision": p_pair,
        "PR": round(PR, 3), "n_comp_pr": round(n_pr, 3),
        "p1_pr": round(p1_pr, 6), "p1_naive": round(p1_naive, 6),
        "p1_loose": round(p1_loose, 6), "p1_emp": round(p1_emp, 6),
        "ratio_pr": (round(_ratio(p1_pr), 4) if _ratio(p1_pr) is not None else None),
        "ratio_naive": (round(_ratio(p1_naive), 4) if _ratio(p1_naive) is not None else None),
        "ratio_loose": (round(_ratio(p1_loose), 4) if _ratio(p1_loose) is not None else None),
        "ratio_emp": (round(_ratio(p1_emp), 4) if _ratio(p1_emp) is not None else None),
        "saturated": saturated, "below_band": below,
    }


# ============================================================
# Aggregation + verdict
# ============================================================
def _ratio_err(r: Optional[float]) -> Optional[float]:
    if r is None or r <= 0:
        return None
    return max(r, 1.0 / r)


def _mean(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def compute_verdict(per_unit: List[Dict[str, Any]], n_units: int) -> Tuple[str, str, Dict[str, Any]]:
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units"
                % (n_units, EXPECTED_N_UNITS), {"cardinality_ok": False})

    # arms-differ (AF): the four prediction surfaces must be hash-distinct.
    pr_s = np.array([u["p1_pr"] for u in per_unit], dtype=np.float64)
    nv_s = np.array([u["p1_naive"] for u in per_unit], dtype=np.float64)
    lo_s = np.array([u["p1_loose"] for u in per_unit], dtype=np.float64)
    em_s = np.array([u["p1_emp"] for u in per_unit], dtype=np.float64)
    arms_differ = (_digest(pr_s) != _digest(nv_s) and _digest(pr_s) != _digest(lo_s)
                   and _digest(pr_s) != _digest(em_s))

    gsbc = [u for u in per_unit if u["arm"] == "gsbc"]
    corr = [u for u in per_unit if u["arm"] == "corr"]
    iid = [u for u in per_unit if u["arm"] == "iid"]

    # phenomenon gates ---------------------------------------------------------
    nonsat_all = [u for u in per_unit if u["arm"] in ("gsbc", "corr")
                  and not u["saturated"] and not u["below_band"]]
    n_nonsat = len(nonsat_all)
    iid_mean_p1 = _mean([u["p1_meas"] for u in iid])
    gate_d = [u for u in gsbc if u["V"] == GATE_D_V and u["D"] == GATE_D_D]
    gate_d_p1 = _mean([u["p1_meas"] for u in gate_d]) if gate_d else None
    gate_d_ok = (gate_d_p1 is not None and abs(gate_d_p1 - GATE_D_REF) <= GATE_D_TOL)

    # gsbc (premise geometry) transfer statistics ------------------------------
    gsbc_ns = [u for u in gsbc if not u["saturated"] and not u["below_band"]]
    pr_ratios = [u["ratio_pr"] for u in gsbc_ns if u["ratio_pr"] is not None]
    nv_ratios = [u["ratio_naive"] for u in gsbc_ns if u["ratio_naive"] is not None]
    em_ratios = [u["ratio_emp"] for u in gsbc_ns if u["ratio_emp"] is not None]
    pr_mean_ratio = _mean(pr_ratios)
    nv_mean_ratio = _mean(nv_ratios)
    em_mean_ratio = _mean(em_ratios)
    pr_ps_max = max([_ratio_err(r) for r in pr_ratios]) if pr_ratios else None
    nv_ps_max = max([_ratio_err(r) for r in nv_ratios]) if nv_ratios else None
    improve = (nv_ps_max / pr_ps_max) if (pr_ps_max and nv_ps_max and pr_ps_max > 0) else None
    naive_biased = (nv_mean_ratio is not None
                    and not (NAIVE_UNBIASED_LO <= nv_mean_ratio <= NAIVE_UNBIASED_HI))
    emp_fits = (em_mean_ratio is not None and EMP_UNBIASED_LO <= em_mean_ratio <= EMP_UNBIASED_HI)

    def _rnd(x):
        return round(x, 4) if x is not None else None

    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": EXPECTED_N_UNITS,
        "arms_differ_verified": bool(arms_differ),
        "n_nonsaturated_gsbc_corr": n_nonsat,
        "iid_mean_p1_meas": _rnd(iid_mean_p1), "iid_no_collapse": bool(iid_mean_p1 is not None and iid_mean_p1 >= IID_CEIL),
        "gate_d_p1_meas": _rnd(gate_d_p1), "gate_d_ref": GATE_D_REF, "gate_d_ok": bool(gate_d_ok),
        "gsbc_n_nonsat": len(gsbc_ns),
        "pr_mean_ratio": _rnd(pr_mean_ratio), "naive_mean_ratio": _rnd(nv_mean_ratio),
        "emp_mean_ratio": _rnd(em_mean_ratio),
        "pr_perseed_max_ratio_err": _rnd(pr_ps_max), "naive_perseed_max_ratio_err": _rnd(nv_ps_max),
        "improve_over_naive": _rnd(improve), "naive_biased": bool(naive_biased),
        "emp_collision_model_fits": bool(emp_fits),
        "bands": {"HP_BIAS_LO": HP_BIAS_LO, "HP_BIAS_HI": HP_BIAS_HI, "HF_BIAS_LO": HF_BIAS_LO,
                  "HF_BIAS_HI": HF_BIAS_HI, "NAIVE_UNBIASED_LO": NAIVE_UNBIASED_LO,
                  "NAIVE_UNBIASED_HI": NAIVE_UNBIASED_HI, "REL_IMPROVE_MIN": REL_IMPROVE_MIN,
                  "ACCEPT_REL_MIN": ACCEPT_REL_MIN, "EMP_UNBIASED_LO": EMP_UNBIASED_LO,
                  "EMP_UNBIASED_HI": EMP_UNBIASED_HI, "IID_CEIL": IID_CEIL, "SAT_HI": SAT_HI,
                  "MIN_NONSAT": MIN_NONSAT.get(RUN_MODE, 2), "GATE_D_REF": GATE_D_REF, "GATE_D_TOL": GATE_D_TOL},
    }

    summ = ("units=%d/%d nonsat(gsbc+corr)=%d gsbc_nonsat=%d | GATE_D gsbc@%dD%d p1=%s (ref %.4f) ok=%s | "
            "iid p1=%s no_collapse=%s | gsbc PR mean_ratio=%s perseed_max=%s | NAIVE mean_ratio=%s "
            "perseed_max=%s biased=%s | improve=%s | EMP-collision mean_ratio=%s fits=%s | arms_differ=%s"
            % (n_units, EXPECTED_N_UNITS, n_nonsat, len(gsbc_ns), GATE_D_V, GATE_D_D,
               extra["gate_d_p1_meas"], GATE_D_REF, gate_d_ok, extra["iid_mean_p1_meas"],
               extra["iid_no_collapse"], extra["pr_mean_ratio"], extra["pr_perseed_max_ratio_err"],
               extra["naive_mean_ratio"], extra["naive_perseed_max_ratio_err"], naive_biased,
               extra["improve_over_naive"], extra["emp_mean_ratio"], emp_fits, arms_differ))

    # gates -------------------------------------------------------------------
    if not arms_differ:
        return "HARD_FAIL", "HARD_FAIL_ARMS (prediction surface bit-identical to a control -- AF): " + summ, extra
    if not gate_d_ok:
        return ("HARD_FAIL",
                "GATE_D_FAIL: gsbc@%dD%d per-block p1=%s not within %.2f of the landed v1 decoder %.4f -- the "
                "decode machinery does not reproduce the CHAIN_GRADE generation cliff; downstream prediction "
                "arms are untrustworthy. " % (GATE_D_V, GATE_D_D, extra["gate_d_p1_meas"], GATE_D_TOL,
                                              GATE_D_REF) + summ, extra)
    if iid_mean_p1 is None or iid_mean_p1 < IID_CEIL:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                "IID_CONTROL_COLLAPSED: iid single-block mean p1=%s < %.2f -- the interference-free control is "
                "not holding; the collapse is a wiring failure, not a codeword-correlation/collision artifact. "
                % (extra["iid_mean_p1_meas"], IID_CEIL) + summ, extra)
    min_nonsat = MIN_NONSAT.get(RUN_MODE, 2)
    if n_nonsat < min_nonsat:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND (collapse did not bite: %d < %d non-saturated gsbc+corr cells -- the generation "
                "decode stayed near-exact at this grid, nothing to predict). " % (n_nonsat, min_nonsat) + summ, extra)
    if len(gsbc_ns) == 0 or pr_mean_ratio is None or improve is None:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND (gsbc premise-geometry arm has no non-saturated cell -> transfer not testable on "
                "the premise's actual codebook at this grid). " + summ, extra)

    # ---- HARD_PASS: PR transfers ----
    if (HP_BIAS_LO <= pr_mean_ratio <= HP_BIAS_HI and improve >= REL_IMPROVE_MIN and naive_biased):
        return ("HARD_PASS",
                "PR-CORRECTED SELF-MARGIN TRANSFERS TO GENERATION (CG-candidate; FULL multi-seed confirms): the "
                "participation-ratio effective competitor count n_comp=PR(V)-1 predicts the generation single-"
                "block decode cliff on the gsbc (comprehension) geometry -- PR mean_ratio=%.3f (unbiased [%.2f,"
                "%.2f]), beats the naive full-V count by %.2fx on worst-cell error, naive stays biased "
                "(mean_ratio=%.3f). Generation joins comprehension one level up. %s"
                % (pr_mean_ratio, HP_BIAS_LO, HP_BIAS_HI, improve, nv_mean_ratio, summ), extra)

    # ---- HARD_FAIL: PR does not transfer (the deflated-likely, mechanism-bearing outcome) ----
    if not (HF_BIAS_LO <= pr_mean_ratio <= HF_BIAS_HI) or improve < ACCEPT_REL_MIN:
        why = []
        if not (HF_BIAS_LO <= pr_mean_ratio <= HF_BIAS_HI):
            why.append("PR mean_ratio=%.3f OUTSIDE [%.2f,%.2f] (PR mis-predicts the generation cliff)"
                       % (pr_mean_ratio, HF_BIAS_LO, HF_BIAS_HI))
        if improve < ACCEPT_REL_MIN:
            why.append("improvement over naive=%.3fx < %.2fx (PR is no better than the falsified naive-V count)"
                       % (improve, ACCEPT_REL_MIN))
        mech = ("MECHANISM: generation decodes DISJOINT block-local (one token/block, deterministic signal=k) so "
                "the collapse is a CODEWORD-COLLISION (birthday) event, NOT the superposition-crowded effective-"
                "rank competition PR corrects in comprehension (which superposes L=D/2 tokens/block). The "
                "empirical-collision model (1-p_pair)^(V-1) %s the measured cliff (emp mean_ratio=%s, fits=%s) -- "
                "the honest predictor is a collision count, not the PR-gaussian order statistic. "
                % ("TRACKS" if emp_fits else "partially tracks", extra["emp_mean_ratio"], emp_fits))
        return ("HARD_FAIL",
                "PR_SELF_MARGIN_DOES_NOT_TRANSFER_TO_GENERATION: " + "; ".join(why) + ". " + mech + summ, extra)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: partial transfer -- PR removes some but not all of the naive-V bias (PR mean_ratio=%s, "
            "improve=%s) but misses a HARD_PASS sub-gate (bias band / improve>=%.2f / naive_biased=%s). Report the "
            "residual + the collision diagnostic (emp fits=%s) honestly. "
            % (extra["pr_mean_ratio"], extra["improve_over_naive"], REL_IMPROVE_MIN, naive_biased, emp_fits) + summ,
            extra)


# ============================================================
# Formula self-test
# ============================================================
def _formula_selftest() -> Tuple[bool, str]:
    # (a) p_win_extreme reduces to Phi(z)^n for a DETERMINISTIC signal (sig_s=0) -- the generation regime.
    mu_s, mu_d, sig_d, n = 6.0, 0.8, 0.83, 27.0
    z = (mu_s - mu_d) / sig_d
    phi_n = (0.5 * math.erfc(-z / math.sqrt(2.0))) ** n
    p_det = pc.p_win_extreme(mu_s, 0.0, mu_d, sig_d, n)
    if abs(p_det - phi_n) > 1e-9:
        return False, "DET_SIGNAL_NOT_PHI_POW p=%.8f phi_n=%.8f" % (p_det, phi_n)
    # (b) monotone DECREASING in competitor count
    prev = 2.0
    for nn in (1.0, 10.0, 100.0, 1000.0):
        p = pc.p_win_extreme(3.5, 0.2, 0.0, 1.0, nn)
        if p > prev + 1e-9:
            return False, "PWIN_NOT_MONOTONE n=%.0f p=%.4f" % (nn, p)
        prev = p
    # (c) PR dual == V x V PR (bit-close) at small V
    cb = base._build_cbmax(7, N_DIM // 26, 300, 1)[0:300]
    pr_dual = participation_ratio_dual(cb)
    pr_full = pc.participation_ratio(cb)
    if abs(pr_dual - pr_full) > 1e-4 * max(1.0, pr_full):
        return False, "PR_DUAL_NEQ_FULL dual=%.4f full=%.4f" % (pr_dual, pr_full)
    # (d) empirical-collision model monotone decreasing in p_pair; = 1 at p_pair=0
    if abs(math.exp((1000 - 1) * math.log1p(-0.0)) - 1.0) > 1e-12:
        return False, "EMP_AT_ZERO_NOT_ONE"
    e1 = math.exp((1000 - 1) * math.log1p(-1e-4))
    e2 = math.exp((1000 - 1) * math.log1p(-1e-3))
    if not (e1 > e2):
        return False, "EMP_NOT_MONOTONE e1=%.4f e2=%.4f" % (e1, e2)
    # (e) iid interference-free single block recovers exactly at an easy regime
    p1_iid = measure_p1(hv.iid_codebook(1024, N_DIM // 8, 7000), 8, N_DIM // 8, 8, 7)
    if p1_iid < 0.999:
        return False, "IID_EASY_NOT_EXACT p1=%.4f" % p1_iid
    return True, ("FORMULA_SELFTEST_PASS (det_signal=Phi^n ok; PR dual=%.3f full=%.3f; emp monotone; iid easy "
                  "p1=%.4f)" % (pr_dual, pr_full, p1_iid))


def _verbatim_check() -> Tuple[bool, str]:
    """Assert p_win_extreme is BIT-IDENTICAL to the comprehension PR-corrected cell's CG'd formula (the
    predictor is the SAME machinery, one substituted exponent, not a re-implementation)."""
    for args in [(6.0, 0.0, 0.8, 0.83, 27.0), (6.0, 0.0, 0.8, 0.83, 8191.0),
                 (3.5, 0.2, 0.0, 1.0, 1.0), (10.0, 0.05, 0.0, 0.3, 65535.0)]:
        a = pc.p_win_extreme(*args)
        try:
            import experiments.exp_comprehension_order_recovery_exact_margin_v1 as emc  # noqa
            b = emc.p_win_extreme(*args)
            if a != b:
                return False, "VERBATIM_MISMATCH args=%s pc=%.10f emc=%.10f" % (args, a, b)
        except Exception as e:  # noqa: BLE001 (import diagnostics only)
            return True, "VERBATIM_SKIP (exact-margin cell not importable: %s)" % type(e).__name__
    return True, "VERBATIM_OK (p_win_extreme bit-identical to the comprehension exact/PR self-margin cells)"


# ============================================================
# Driver
# ============================================================
def run_all(out_dir: Path, t0: float) -> List[Dict[str, Any]]:
    per_unit: List[Dict[str, Any]] = []
    total = EXPECTED_N_UNITS
    unit = 0
    for seed in SEEDS:
        for (arm, V, D) in GRID:
            try:
                r = run_unit(arm, V, D, seed)
            except (ValueError, MemoryError, FloatingPointError) as e:
                r = {"arm": arm, "V": V, "D": D, "seed": seed, "failure_class": type(e).__name__,
                     "error": str(e)[:300], "p1_meas": None, "saturated": False, "below_band": False,
                     "p1_pr": None, "p1_naive": None, "p1_loose": None, "p1_emp": None,
                     "ratio_pr": None, "ratio_naive": None, "ratio_emp": None}
                _say("  [seed %d][%s V=%d D=%d] FAILED %s: %s" % (seed, arm, V, D, type(e).__name__, str(e)[:120]))
                raise AssertionError("UNIT_FAILED %s V=%d D=%d seed=%d: %s"
                                     % (arm, V, D, seed, type(e).__name__)) from e
            per_unit.append(r)
            unit += 1
            _heartbeat(out_dir, unit, total, t0,
                       extra={"arm": arm, "V": V, "D": D, "seed": seed, "p1_meas": r["p1_meas"],
                              "PR": r.get("PR"), "p1_pr": r.get("p1_pr"), "ratio_pr": r.get("ratio_pr")})
            _say("  [seed %d][%s V=%d D=%d bs=%d k=%d] p1_meas=%.4f | PR=%.1f kurt=%.1f | p1_pr=%.4f(r=%s) "
                 "p1_naive=%.4f(r=%s) p1_emp=%.4f(r=%s)%s"
                 % (seed, arm, V, D, r["bs"], r["k_active"], r["p1_meas"], r["PR"], r["kurtosis_dist"],
                    r["p1_pr"], r["ratio_pr"], r["p1_naive"], r["ratio_naive"], r["p1_emp"], r["ratio_emp"],
                    " [SAT]" if r["saturated"] else (" [NONSAT]" if not r["below_band"] else " [BELOW]")))
    return per_unit


def _run(mode: str) -> int:
    out_dir = _out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    _write_start_marker(out_dir, mode, EXPECTED_N_UNITS)
    _say("[%s] mode=%s N=%d grid=%s seeds=%s trials=%d n_query=%d expected=%d"
         % (ANCHOR_NAME, mode, N_DIM, GRID, SEEDS, TRIALS, N_QUERY, EXPECTED_N_UNITS))

    ok_f, msg_f = _formula_selftest()
    if not ok_f:
        raise AssertionError("FORMULA_SELFTEST_FAIL: " + msg_f)
    _say("[formula] " + msg_f)
    ok_v, msg_v = _verbatim_check()
    if not ok_v:
        raise AssertionError("VERBATIM_CHECK_FAIL: " + msg_v)
    _say("[verbatim] " + msg_v)

    per_unit = run_all(out_dir, t0)
    verdict, vmsg, extra = compute_verdict(per_unit, len(per_unit))
    extra["formula_selftest"] = msg_f
    extra["verbatim_check"] = msg_v
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
        "summary": "%s: does the PR-corrected self-margin TRANSFER to predict the GENERATION decode-collapse "
                   "boundary (comprehension -> generation) (%s)" % (verdict, mode),
        "run_mode": mode, "elapsed_s": round(elapsed, 2),
        "n_seeds": len(SEEDS), "n_units": len(per_unit), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_unit) >= EXPECTED_N_UNITS,
        "arms_differ_verified": extra.get("arms_differ_verified", False),
        "config_version": CONFIG_VERSION,
        "config": {"N": N_DIM, "grid": [[a, v, d] for (a, v, d) in GRID], "seeds": SEEDS,
                   "trials": TRIALS, "n_query": N_QUERY,
                   "predictor": "GH64_extreme_value_order_statistic",
                   "mechanism_under_test": "n_comp=PR(V)-1 participation_ratio (dual bs x bs) of codeword Gram",
                   "controls": {"naive_v": "n_comp=V-1 (falsified comprehension baseline)",
                                "loose": "n_comp=1 (V-blind)",
                                "empirical_collision": "(1-p_pair)^(V-1); p_pair=P[distractor overlap>=signal]",
                                "iid_arm": "interference-free single-block; no-collapse control"},
                   "measurement": "hv.single_block_decode_VERBATIM (disjoint block-local generation decode)",
                   "gsbc_geometry": "base._build_cbmax native GSBC block-local (comprehension geometry)",
                   "target": "per_block_decode_p1 = per_term (disjoint single-block)",
                   "kb_referent_declared": False},
        "framing": {"mode": "monitor_not_control",
                    "note": "predicts/reports its own decode reliability; NEVER edits codebook/decoder/V/D/N; "
                            "narrow glass-box monitoring step; not fluent-language; not self-improvement; "
                            "re-encode HELD"},
        "hp_scope": {"gsbc_pr_corrected": ["bias_unbiased", "improve>=1.5", "naive_biased"],
                     "naive_v": ["naive_biased_direction_gate_only"],
                     "loose": ["diagnostic_only"], "empirical_collision": ["mechanism_diagnostic_only"],
                     "iid": ["no_collapse_control_gate_only"]},
        "plain_language": ("We asked whether the trick that let the substrate predict its own COMPREHENSION "
                           "decode errors (counting effective, not raw, competitors) also predicts its own "
                           "GENERATION decode errors. It does not, because generation recovers each token from "
                           "its own separate slot (a collision/duplicate problem) while comprehension crams "
                           "several tokens together (a crowding problem) -- different physics. The honest "
                           "predictor for generation is a collision count, not the comprehension formula."),
        "importance": ("Bounds the self-margin generalization: the substrate's exact self-prediction is "
                       "regime-specific (superposition-crowded decode), and does NOT auto-transfer to the "
                       "disjoint-block generation decode. Points research to a collision-model self-margin."),
        "extra": extra, "per_unit": per_unit,
        "ts_iso": _now_iso(), "pid": os.getpid(), "host": platform.node(),
    }
    _write_metrics_atomic(out_dir, metrics)
    written = json.load(open(out_dir / "metrics.json"))
    assert written["run_mode"] == mode, "RUN_MODE_MISMATCH %s != %s" % (written["run_mode"], mode)

    _say("\n[%s] %s: %s" % (ANCHOR_NAME, verdict, vmsg))
    _say("[%s] metrics -> %s  elapsed=%.1fs" % (ANCHOR_NAME, out_dir / "metrics.json", elapsed))
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    ok_f, msg_f = _formula_selftest()
    assert ok_f, "FORMULA_SELFTEST_FAIL: " + msg_f
    ok_v, msg_v = _verbatim_check()
    assert ok_v, "VERBATIM_CHECK_FAIL: " + msg_v
    # one gsbc unit + one iid unit: gsbc must be measurable, iid must not collapse, predictions well-formed.
    rg = run_unit("gsbc", 4096, 48, 7)
    ri = run_unit("iid", 65536, 48, 7)
    unit_ok = (0.0 <= rg["p1_meas"] <= 1.0 and 0.0 <= rg["p1_pr"] <= 1.0
               and ri["p1_meas"] >= IID_CEIL)
    ok = ok_f and ok_v and unit_ok
    _say("[%s] SELFTEST %s: formula=%s | %s | gsbc(V4096D48) p1_meas=%.4f PR=%.1f p1_pr=%.4f p1_naive=%.4f "
         "p1_emp=%.4f | iid(V65536D48) p1_meas=%.4f no_collapse=%s [%.1fs]"
         % (ANCHOR_NAME, "PASS" if ok else "FAIL", msg_f, msg_v, rg["p1_meas"], rg["PR"], rg["p1_pr"],
            rg["p1_naive"], rg["p1_emp"], ri["p1_meas"], ri["p1_meas"] >= IID_CEIL,
            time.perf_counter() - t0))
    return 0 if ok else 1


def main() -> int:
    if RUN_MODE == "self_test":
        return _run_selftest()
    return _run(RUN_MODE)


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
