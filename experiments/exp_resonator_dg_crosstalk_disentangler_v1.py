"""
exp_resonator_dg_crosstalk_disentangler_v1.py -- CPU pre-check gate for the DG-front-end
resonator escape (5x-drill #1 on the K5/K6 basin/capacity wall).

RESEARCH CONTEXT (notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md
secondary checks #1 + #2; gate for exp_resonator_dg_frontend_ksweep_v1):
The vanilla resonator craters at K5/K6 (oracle_any=0). Skunkworks-confirmed genuine, diagnosed
NOT as fundamental basin-multiplicity but as a CONFIG-CONTINGENT CROSSTALK/SNR CAPACITY CLIFF at
N=4096: the wall sits where M^K crosses ~N^2 (Tsodyks-Feigelman crosstalk-noise mechanism). It MOVES
with N. The proposed escape = DIMENSIONAL EXPANSION (raise effective N via r*N) so crosstalk SNR
rises. This CPU cell DISENTANGLES the two candidate readings BEFORE any GPU spend:

  CHECK A (crosstalk-variance, THE load-bearing disentangler): using an ORACLE unbind (unbind factor
    k with the TRUE other factors, so basin DYNAMICS are removed and ONLY codebook crosstalk remains),
    measure the std of wrong-codeword scores + the true-vs-best-wrong margin, at fixed K, for
    dense-N4096 (baseline) vs dense-r*N (expansion) vs sparse-phasor-r*N (expansion+sparsify). If
    expansion LOWERS crosstalk std ~1/sqrt(N) and RAISES the margin, the Tsodyks-Feigelman SNR reading
    is confirmed (expansion is a real lever) independent of whether basin COUNT changes.
  CHECK B (decorrelation-transfer / FHRR port): does DGProjection's real-valued pattern-separation
    gap (code_cos < input_cos - 0.20 on correlated inputs) PORT to complex-phase FHRR codewords under
    the same expansion+sparsify? Relaxed to 0.15 (phase geometry differs).
  CHECK C (sparsify-viability, the RISKY lever): the multiplicative resonator unbind is a K-way
    PRODUCT; a 2%-dense phasor code makes prod_{j!=k} est[j] near-zero support for K>=3. This cell
    directly measures whether the ORACLE-unbind margin SURVIVES sparsification -- if it collapses to
    <0.10 the naive codebook-sparsify is incompatible with multiplicative binding (informative;
    the sparsify arm of the escape cell would then be expected-to-crater, and the rescue rides on
    expansion-ALONE).

This cell is CPU-cheap (numpy, minutes) and is a DECISION GATE, not a capability claim. Its verdict
tells the escape cell (a) whether expansion is a real crosstalk lever and (b) what to expect from the
sparsify ablation arm.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at gate (dense-N4096 vs dense-rN vs sparse-rN crosstalk hashes differ)
# - final_metrics_atomicity: tmp_replace (write_metrics)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: this is a diagnostic disentangler (measures crosstalk std directly; no HP threshold on
#   a substrate capability -- the numbers ARE the deliverable)
# - discriminator: expansion must MOVE crosstalk std across the N axis (else vacuous)
# - THEORETICAL anchors: crosstalk std ~ 1/sqrt(N_eff); dense margin grows with N
# - progress_logging: print_flush_true (short cell)
ASCII-only. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, json, argparse, time, hashlib, traceback, platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "resonator_dg_crosstalk_disentangler_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- config -----------------------------------------------------------------
N_BASE = 4096
R_EXPAND = 4                    # r=4 -> N_exp=16384 (research proposal)
N_EXP = N_BASE * R_EXPAND
M = 30
SPARSITY = 0.02                # DG default active-rate (the risky lever)
K_PROBE = [4, 5]              # K4 = where vanilla partially works; K5 = onset of crater
N_TRIALS = 40 if SMOKE else 200
SEEDS = [3] if SMOKE else [3, 7, 13]

# discriminator / gate bands
EXPANSION_SNR_RATIO_MIN = 1.30  # dense-N4096 crosstalk_std / dense-Nexp crosstalk_std must exceed this
DECORR_GAP_MIN = 0.15          # code_cos < input_cos - this (complex FHRR port of DG separation)
SPARSIFY_VIABLE_MARGIN = 0.30  # sparse oracle-unbind margin >= this => sparsify arm viable
SPARSIFY_COLLAPSE_MARGIN = 0.10  # sparse margin < this => sparsify collapses binding support


# --- codebook generators ----------------------------------------------------
def phasor_dense(m: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """Dense unit-modulus FHRR phasor codebook. [m, d] complex128."""
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang)


def phasor_sparse(m: int, d: int, sparsity: float, rng: np.random.Generator) -> np.ndarray:
    """DG-analog sparse phasor codebook: complex-gaussian -> top-K by |z| -> unit-phase survivors,
    zeros elsewhere (phase-preserved for nonzero entries). [m, d] complex128."""
    z = rng.standard_normal((m, d)) + 1j * rng.standard_normal((m, d))
    mag = np.abs(z)
    k = max(1, int(round(sparsity * d)))
    if k >= d:
        mask = np.ones_like(mag, dtype=bool)
    else:
        thresh = np.partition(mag, d - k, axis=1)[:, d - k][:, None]
        mask = mag >= thresh
    phase = z / (mag + 1e-12)          # unit-phase e^{i arg z}
    return phase * mask.astype(np.float64)


def _oracle_unbind_scores(books: List[np.ndarray], true: Tuple[int, ...], K: int,
                          d: int) -> np.ndarray:
    """ORACLE unbind of factor 0 (basin dynamics removed): form the bound product s, unbind with the
    TRUE other factors, then score every codeword of factor 0. Returns [M] real scores (score[true0]
    should be ~1 for dense; wrong entries are pure codebook crosstalk). Normalized by active support."""
    s = np.ones(d, dtype=np.complex128)
    for k in range(K):
        s = s * books[k][true[k]]
    others = np.ones(d, dtype=np.complex128)
    for j in range(1, K):
        others = others * books[j][true[j]]
    unbound = s * np.conj(others)      # == books[0][true[0]] up to support of the product
    # normalize by the number of dims that actually carry signal (support of the product chain)
    support = np.count_nonzero(np.abs(others) > 1e-9)
    denom = max(support, 1)
    scores = np.real(books[0].conj() @ unbound) / denom
    return scores


def _crosstalk_stats(books: List[np.ndarray], K: int, d: int, trues: List[Tuple[int, ...]]) -> Dict:
    """Over many true tuples: true-score, best-wrong-score, wrong-score std (crosstalk), margin."""
    true_scores, best_wrong, wrong_std, margins = [], [], [], []
    for true in trues:
        sc = _oracle_unbind_scores(books, true, K, d)
        t0 = true[0]
        ts = float(sc[t0])
        wrong = np.delete(sc, t0)
        bw = float(np.max(wrong))
        true_scores.append(ts)
        best_wrong.append(bw)
        wrong_std.append(float(np.std(wrong)))
        margins.append(ts - bw)
    return {
        "true_score_mean": float(np.mean(true_scores)),
        "best_wrong_mean": float(np.mean(best_wrong)),
        "crosstalk_std_mean": float(np.mean(wrong_std)),
        "margin_mean": float(np.mean(margins)),
        "margin_min": float(np.min(margins)),
        "oracle_recover_rate": float(np.mean([m > 0 for m in margins])),
    }


def _complex_cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a)); nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.real(np.vdot(a, b)) / (na * nb))


def _decorr_port(rng: np.random.Generator) -> Dict:
    """CHECK B: does DG pattern-separation port to complex phasors under expansion+sparsify?
    Build a correlated complex pair (input_cos ~ 0.8-0.95 via small phase perturbation), expand+sparsify
    both through the SAME random projection, measure code_cos vs input_cos."""
    base_ang = (rng.random(N_BASE) * 2 - 1) * np.pi
    x1 = np.exp(1j * base_ang)
    # small phase jitter -> correlated but distinct
    x2 = np.exp(1j * (base_ang + 0.30 * rng.standard_normal(N_BASE)))
    input_cos = _complex_cos(x1, x2)
    # random complex expansion projection N_BASE -> N_EXP, then top-K sparsify + unit-phase
    P = (rng.standard_normal((N_EXP, N_BASE)) + 1j * rng.standard_normal((N_EXP, N_BASE)))
    P /= np.sqrt(2.0 * N_BASE)

    def expand_sparsify(x):
        y = P @ x
        mag = np.abs(y)
        k = max(1, int(round(SPARSITY * N_EXP)))
        thresh = np.partition(mag, N_EXP - k)[N_EXP - k]
        mask = mag >= thresh
        phase = y / (mag + 1e-12)
        return phase * mask.astype(np.float64)

    c1 = expand_sparsify(x1); c2 = expand_sparsify(x2)
    code_cos = _complex_cos(c1, c2)
    gap = input_cos - code_cos
    return {"input_cos": input_cos, "code_cos": code_cos, "gap": gap,
            "ports": bool(gap >= DECORR_GAP_MIN)}


def _selftest() -> None:
    rng = np.random.default_rng(0)
    # 1. dense phasor unit modulus
    b = phasor_dense(5, 256, rng)
    assert np.allclose(np.abs(b), 1.0), "dense phasor modulus"
    # 2. sparse phasor sparsity target
    bs = phasor_sparse(5, 4096, 0.02, rng)
    rate = float(np.count_nonzero(bs)) / bs.size
    assert 0.010 <= rate <= 0.030, "sparse rate %.4f outside [0.01,0.03]" % rate
    # 3. oracle unbind recovers truth for DENSE at N=4096, K=4 (margin large)
    K = 4
    books = [phasor_dense(M, 4096, np.random.default_rng(7 + i)) for i in range(K)]
    true = (7, 3, 19, 2)
    sc = _oracle_unbind_scores(books, true, K, 4096)
    assert int(np.argmax(sc)) == true[0], "oracle unbind must recover factor-0 truth (dense)"
    assert sc[true[0]] - np.max(np.delete(sc, true[0])) > 0.5, "dense oracle margin must be large"
    # 4. crosstalk std lower at larger N (THEORETICAL ~1/sqrt(N))
    trues = [(int(x[0]), int(x[1]), int(x[2]), int(x[3]))
             for x in np.random.default_rng(1).integers(0, M, size=(20, K))]
    books_lo = [phasor_dense(M, 2048, np.random.default_rng(100 + i)) for i in range(K)]
    books_hi = [phasor_dense(M, 8192, np.random.default_rng(100 + i)) for i in range(K)]
    st_lo = _crosstalk_stats(books_lo, K, 2048, trues)
    st_hi = _crosstalk_stats(books_hi, K, 8192, trues)
    assert st_hi["crosstalk_std_mean"] < st_lo["crosstalk_std_mean"], \
        "crosstalk std must fall with N (%.4f !< %.4f)" % (st_hi["crosstalk_std_mean"], st_lo["crosstalk_std_mean"])
    ratio = st_lo["crosstalk_std_mean"] / max(st_hi["crosstalk_std_mean"], 1e-9)
    # 2x N -> ~sqrt(4)=2x std drop expected (2048->8192 is 4x N)
    assert 1.5 < ratio < 3.0, "crosstalk std ratio %.3f not ~sqrt(4)=2 for 4x N" % ratio
    print("[selftest] PASS: dg-crosstalk-disentangler (dense margin ok; crosstalk_std ratio 4xN=%.3f)"
          % ratio, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def run_one_config(K: int, seed: int) -> Dict:
    """Crosstalk stats for dense-N4096, dense-Nexp, sparse-Nexp at fixed K + seed. PAIRED true tuples."""
    rng_t = np.random.default_rng(seed * 13 + K)
    trues_base = [tuple(int(x) for x in rng_t.integers(0, M, size=K)) for _ in range(N_TRIALS)]

    # dense-N4096 baseline
    books_b = [phasor_dense(M, N_BASE, np.random.default_rng(seed * 1000 + K * 10 + i)) for i in range(K)]
    st_base = _crosstalk_stats(books_b, K, N_BASE, trues_base)

    # dense-Nexp (expansion-only, the mechanistically-supported lever)
    books_e = [phasor_dense(M, N_EXP, np.random.default_rng(seed * 2000 + K * 10 + i)) for i in range(K)]
    st_exp = _crosstalk_stats(books_e, K, N_EXP, trues_base)

    # sparse-Nexp (expansion+sparsify, the risky lever)
    books_s = [phasor_sparse(M, N_EXP, SPARSITY, np.random.default_rng(seed * 3000 + K * 10 + i)) for i in range(K)]
    st_spr = _crosstalk_stats(books_s, K, N_EXP, trues_base)

    return {"K": K, "seed": seed,
            "dense_N4096": st_base, "dense_Nexp": st_exp, "sparse_Nexp": st_spr}


def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.perf_counter()
    print("[config] anchor=%s mode=%s N_base=%d N_exp=%d(r=%d) M=%d sparsity=%.3f K=%s trials=%d seeds=%s"
          % (ANCHOR_NAME, RUN_MODE, N_BASE, N_EXP, R_EXPAND, M, SPARSITY, K_PROBE, N_TRIALS, SEEDS), flush=True)

    per_config: List[Dict] = []
    for K in K_PROBE:
        for seed in SEEDS:
            cfg = run_one_config(K, seed)
            per_config.append(cfg)
            print("  K=%d seed=%d | dense4096: xstd=%.4f margin=%.3f rec=%.2f | denseExp: xstd=%.4f margin=%.3f rec=%.2f | sparseExp: xstd=%.4f margin=%.3f rec=%.2f"
                  % (K, seed,
                     cfg["dense_N4096"]["crosstalk_std_mean"], cfg["dense_N4096"]["margin_mean"], cfg["dense_N4096"]["oracle_recover_rate"],
                     cfg["dense_Nexp"]["crosstalk_std_mean"], cfg["dense_Nexp"]["margin_mean"], cfg["dense_Nexp"]["oracle_recover_rate"],
                     cfg["sparse_Nexp"]["crosstalk_std_mean"], cfg["sparse_Nexp"]["margin_mean"], cfg["sparse_Nexp"]["oracle_recover_rate"]),
                  flush=True)

    # decorrelation port (CHECK B)
    decorr = _decorr_port(np.random.default_rng(SEEDS[0] * 77 + 1))

    # aggregate across K/seeds
    def agg(field_arm, field):
        return float(np.mean([c[field_arm][field] for c in per_config]))
    xstd_base = agg("dense_N4096", "crosstalk_std_mean")
    xstd_exp = agg("dense_Nexp", "crosstalk_std_mean")
    xstd_spr = agg("sparse_Nexp", "crosstalk_std_mean")
    margin_base = agg("dense_N4096", "margin_mean")
    margin_exp = agg("dense_Nexp", "margin_mean")
    margin_spr = agg("sparse_Nexp", "margin_mean")

    snr_ratio = xstd_base / max(xstd_exp, 1e-12)

    # ARMS-MUST-DIFFER: the three arms' aggregate crosstalk-std signatures must differ
    sig = {"dense_N4096": round(xstd_base, 8), "dense_Nexp": round(xstd_exp, 8), "sparse_Nexp": round(xstd_spr, 8)}
    arms_differ_ok = len(set(sig.values())) == 3

    # gate logic
    expansion_confirmed = bool(snr_ratio >= EXPANSION_SNR_RATIO_MIN and margin_exp > margin_base)
    decorr_ports = bool(decorr["ports"])
    if margin_spr >= SPARSIFY_VIABLE_MARGIN:
        sparsify_state = "VIABLE"
    elif margin_spr < SPARSIFY_COLLAPSE_MARGIN:
        sparsify_state = "COLLAPSE"
    else:
        sparsify_state = "MARGINAL"

    if not arms_differ_ok:
        verdict = "HARD_FAIL"
        vmsg = "META_RULE_AF: three arms produced identical crosstalk-std signatures %s -- implementation bug." % sig
    elif expansion_confirmed:
        verdict = "GATE_CLEAR_EXPANSION"
        vmsg = ("GATE_CLEAR: expansion lowers crosstalk_std %.4f->%.4f (ratio %.2fx >= %.2f) and raises "
                "oracle margin %.3f->%.3f -- Tsodyks-Feigelman SNR reading CONFIRMED; expansion is a real "
                "lever. Sparsify arm=%s (margin %.3f). Decorr port gap=%.3f (%s). PROCEED to escape smoke; "
                "primary rescue arm = expansion-ALONE; sparsify ablation expected=%s."
                % (xstd_base, xstd_exp, snr_ratio, EXPANSION_SNR_RATIO_MIN, margin_base, margin_exp,
                   sparsify_state, margin_spr, decorr["gap"], "ports" if decorr_ports else "NO-port",
                   "informative-crater" if sparsify_state == "COLLAPSE" else sparsify_state))
    else:
        verdict = "GATE_DENY"
        vmsg = ("GATE_DENY: expansion did NOT confirm SNR lever (crosstalk ratio %.2fx < %.2f OR margin "
                "%.3f !> %.3f). Escape cell's expansion arm unlikely to rescue; do NOT spend GPU. "
                "Sparsify arm=%s margin=%.3f." % (snr_ratio, EXPANSION_SNR_RATIO_MIN, margin_exp, margin_base,
                                                  sparsify_state, margin_spr))

    detail = {
        "aggregate": {
            "crosstalk_std": {"dense_N4096": xstd_base, "dense_Nexp": xstd_exp, "sparse_Nexp": xstd_spr},
            "oracle_margin": {"dense_N4096": margin_base, "dense_Nexp": margin_exp, "sparse_Nexp": margin_spr},
            "expansion_snr_ratio": snr_ratio,
        },
        "decorrelation_port": decorr,
        "expansion_confirmed": expansion_confirmed,
        "sparsify_state": sparsify_state,
        "decorr_ports": decorr_ports,
        "arms_differ_verified": arms_differ_ok,
        "bands": {"expansion_snr_ratio_min": EXPANSION_SNR_RATIO_MIN, "decorr_gap_min": DECORR_GAP_MIN,
                  "sparsify_viable_margin": SPARSIFY_VIABLE_MARGIN, "sparsify_collapse_margin": SPARSIFY_COLLAPSE_MARGIN},
        "config": {"N_BASE": N_BASE, "N_EXP": N_EXP, "R_EXPAND": R_EXPAND, "M": M, "SPARSITY": SPARSITY,
                   "K_PROBE": K_PROBE, "N_TRIALS": N_TRIALS, "SEEDS": SEEDS},
    }
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "per_config": per_config,
        "detail": detail,
        "elapsed_s": time.perf_counter() - t0,
    }
    write_metrics(output_dir, metrics, per_config)
    print("[metrics] written -> %s" % (output_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
