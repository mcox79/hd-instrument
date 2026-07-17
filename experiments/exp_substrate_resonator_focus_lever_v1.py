"""
exp_substrate_resonator_focus_lever_v1 -- does anything raise the resonator's joint-factor
"focus" beyond its ~F=3-4 sweet spot? -- CPU numpy, local inline (local_cpu_queue runner is down).

ROUTING: Director task, source `notes/research_wm_focus_limit_functional_increase_2026-07-17.md`
  (the drill) + `notes/research_working_memory_integration_upper_limit_2026-07-16.md`. Reuses
  `resonate()`/`cleanup()`/`phasor` mechanics verbatim from `exp_resonator_factorization_v1.py`
  (the true iterative alternating-projection joint-factor resonator, NOT R6's block-local
  disjoint-subspace decode which structurally sidesteps interference). Pre-reg:
  `notes/prereg_resonator_focus_lever_v1_2026-07-17.md` (bands + regime-calibration rationale --
  READ FIRST, the numbers below are not arbitrary).

THREE ARMS (core; (iv) paging and (v) orthogonal-subspace decoupling deferred as follow-ups, see
  pre-reg -- (v) is partially pre-answered by prior banked R6 data, cited in the pre-reg):
  (i) FLAT: one joint resonate() call over all F factors at once (must-fail control at F=6/8).
  (ii) HIERARCHICAL: split F into two groups of <=4; resolve group A alone (own codebooks),
       reconstruct s_A_hat from the DECODED (not ground-truth) indices, isolate group B via
       s_B_isolated = S * conj(s_A_hat) (the exact unbind primitive resonate() already uses
       internally), resolve group B alone. Stage-1 errors genuinely propagate (leaky chunk-and-pass).
  (iii) DECORRELATED codebook: same flat decode, but codebook phase-generating matrix is
       QR-orthogonalized before exponentiating to unit-modulus phasors (bind/unbind math untouched
       -- exp(1j*theta) is unit-modulus regardless of how theta was generated). Dense/baseline
       reference reuses FLAT's own numbers (zero extra compute, removes RNG-draw confound).

PRE-REGISTERED bands (let REF = mean FLAT accuracy at F=4, measured live):
  HARD-PASS: hier_F6>=0.70*REF AND hier_F8>=0.40*REF AND flat_F6<=0.30*REF AND flat_F8<=0.15*REF
    AND (hier_F6-flat_F6)>=0.30 AND (hier_F8-flat_F8)>=0.20 AND |decorr_F6-flat_F6|<=0.15 AND
    |decorr_F8-flat_F8|<=0.15.
  HARD-FAIL: |hier_F6-flat_F6|<=0.05 AND |hier_F8-flat_F8|<=0.05 (no rescue), OR
    (decorr_F6-flat_F6)>=0.30 (decorrelation ALSO rescues -- positive surprise, not a cell failure).
  MIDDLE_BAND: anything else (see pre-reg for full rationale incl. why bands are ratio-based, not
    the drill's raw 90%/85%, at this substrate's calibrated regime).

REGIME (measured via dry-run calibration, NOT the literature's assumed default -- see pre-reg):
  N=16384, M=8 per-slot codebook size, MAX_IT=200. At the ORIGINAL cell's own default regime
  (N=2048, M=30) K=4 is ALREADY collapsed (0.047, measured by re-running that cell FULL this
  session) -- would make "F=4 reference" meaningless there.

FORMULA SELF-TESTS (PROT-022 + F.1 real_code_path): 1. bind/unbind inverse. 2. cleanup self.
  3. flat resonate exact at tiny K=2. 4. hierarchical 2-stage exact at tiny ka=kb=1.
  5. QR-decorrelated codebook preserves unit modulus + orthogonal by construction.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, traceback
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._cell_heartbeat import CellHeartbeat

ANCHOR_NAME = "substrate_resonator_focus_lever_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---- regime (same N/M/MAX_IT in smoke and full -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A;
#      only TRIALS differ) ----
N_DIM = 16384
M_FACTOR = 8
MAX_IT = 200
FLAT_K = [3, 4, 6, 8]
HIER_CONFIGS = [(6, 3, 3), (8, 4, 4)]  # (F, ka, kb)
if RUN_MODE == "smoke":
    SEEDS = [7]
    TRIALS = 10
else:
    SEEDS = [7, 17, 23]
    TRIALS = 60

EXPECTED_UNITS_PER_SEED = len(FLAT_K) + len(FLAT_K) + len(HIER_CONFIGS)  # flat + decorr-orth + hier = 4+4+2=10


# ---------------------------------------------------------------------------
# Core primitives -- REUSED VERBATIM from experiments/exp_resonator_factorization_v1.py
# (the true iterative alternating-projection joint-factor resonator). No new bind/unbind/cleanup
# primitive is introduced; the only new function is orthogonalize_theta (codebook construction).
# ---------------------------------------------------------------------------
def make_theta(m, d, g):
    return g.uniform(-np.pi, np.pi, (m, d))


def phasor_from_theta(theta):
    return np.exp(1j * theta).astype(np.complex64)


def orthogonalize_theta(theta):
    """Decorrelate a codebook's phase-generating matrix via QR, rescaled to preserve the
    baseline's typical phase spread, wrapped into [-pi,pi]. exp(1j*theta) stays exactly
    unit-modulus regardless of how theta was generated -- bind/unbind invertibility (which
    requires unit-modulus phasors elementwise) is untouched by this transform."""
    m, n = theta.shape
    assert m <= n, "orthogonalize_theta requires M <= N"
    q, _ = np.linalg.qr(theta.T)  # N x M, orthonormal columns
    qc = q[:, :m].T  # M x N, orthonormal rows (unit L2 norm each)
    scale = np.sqrt(n) * (np.pi / np.sqrt(3))  # match uniform(-pi,pi)'s per-element std
    theta_o = qc * scale
    theta_o = np.mod(theta_o + np.pi, 2 * np.pi) - np.pi
    return theta_o


def cleanup(v, book):
    j = int(np.argmax((book @ np.conj(v)).real))
    return book[j], j


def resonate(s, books, K, max_it=MAX_IT):
    est = [b.mean(0) for b in books]
    est = [e / (np.abs(e) + 1e-8) for e in est]
    prev = None
    for _ in range(max_it):
        idxs = []
        for k in range(K):
            others = np.ones(s.shape, dtype=np.complex64)
            for j in range(K):
                if j != k:
                    others = others * est[j]
            r = s * np.conj(others)
            scores = books[k] @ np.conj(r)
            est[k] = (scores @ books[k])
            est[k] = est[k] / (np.abs(est[k]) + 1e-8)
            idxs.append(int(np.argmax(scores.real)))
        if idxs == prev:
            break
        prev = idxs
    return idxs


def compose(books, idx):
    s = np.ones(books[0].shape[1], dtype=np.complex64)
    for i, b in enumerate(books):
        s = s * b[idx[i]]
    return s


def make_books(K, M, N, g, decorr=False):
    out = []
    for _ in range(K):
        theta = make_theta(M, N, g)
        if decorr:
            theta = orthogonalize_theta(theta)
        out.append(phasor_from_theta(theta))
    return out


# ---------------------------------------------------------------------------
# Self-test (F.1 real_code_path -- exercises the REAL functions above at tiny scale, not a
# synthetic-only branch)
# ---------------------------------------------------------------------------
def _selftest():
    g = np.random.default_rng(0)
    a = phasor_from_theta(make_theta(1, 32, g))[0]
    b = phasor_from_theta(make_theta(1, 32, g))[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-4), "bind/unbind inverse"

    book = phasor_from_theta(make_theta(5, 32, g))
    _, j = cleanup(book[2], book)
    assert j == 2, "cleanup self"

    books2 = make_books(2, 4, 64, g)
    true2 = [1, 2]
    s2 = compose(books2, true2)
    got2 = resonate(s2, books2, 2, max_it=50)
    assert got2 == true2, "flat resonate exact at tiny K2"

    books_a = make_books(1, 4, 64, g)
    books_b = make_books(1, 4, 64, g)
    true_a, true_b = [1], [2]
    s_a = compose(books_a, true_a)
    s_full = s_a * compose(books_b, true_b)
    dec_a = resonate(s_a, books_a, 1, max_it=50)
    s_a_hat = compose(books_a, dec_a)
    s_b_iso = s_full * np.conj(s_a_hat)
    dec_b = resonate(s_b_iso, books_b, 1, max_it=50)
    assert dec_a == true_a and dec_b == true_b, "hierarchical 2-stage exact at tiny ka=kb=1"

    theta_raw = make_theta(4, 64, g)
    theta_o = orthogonalize_theta(theta_raw)
    book_o = phasor_from_theta(theta_o)
    assert book_o.shape == (4, 64), "decorr codebook shape"
    assert np.allclose(np.abs(book_o), 1.0, atol=1e-4), "decorr codebook unit modulus preserved"
    # QR guarantees the GENERATING theta rows are exactly orthogonal (before the [-pi,pi] wrap,
    # which can slightly perturb this for entries near the wrap boundary) -- check the
    # pre-wrap orthogonality directly on the QR output, not the final wrapped/exponentiated book
    # (which has no exact-orthogonality guarantee; the arm-level results test the empirical effect).
    m, n = theta_raw.shape
    q, _ = np.linalg.qr(theta_raw.T)
    qc = q[:, :m].T
    offdiag = np.abs(qc @ qc.T - np.eye(m))
    assert offdiag.max() < 1e-6, "QR-orthogonalized generating vectors exactly orthonormal"

    print("[selftest] PASS: resonator-focus-lever (bind/unbind, cleanup, flat, hierarchical 2-stage, decorr)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Crash diagnostic (per §13-C / §8: except SystemExit/KeyboardInterrupt re-raise; Exception writes
# CELL_CRASHED metrics then re-raises)
# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    import json
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _arms_must_differ(arms_outputs: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests = {}
    for name, out in arms_outputs.items():
        b = np.asarray(out, dtype=np.float64).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, bnm = names[i], names[j]
            if arms_outputs[a].shape == arms_outputs[bnm].shape:
                assert digests[a] != digests[bnm], (
                    "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, bnm, digests[a])
                )
    return digests


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def run_seed(seed: int, hb: CellHeartbeat) -> Dict:
    g = np.random.default_rng(seed)
    out = {"seed": seed}
    unit_count = 0

    # --- Arm (i) FLAT ---
    flat_acc = {}
    for K in FLAT_K:
        books = make_books(K, M_FACTOR, N_DIM, g)
        succ = 0
        for _ in range(TRIALS):
            true = [int(g.integers(0, M_FACTOR)) for _ in range(K)]
            s = compose(books, true)
            got = resonate(s, books, K)
            succ += int(got == true)
        flat_acc[K] = succ / TRIALS
        unit_count += 1
        print("  [seed=%d] FLAT K=%d acc=%.3f" % (seed, K, flat_acc[K]), flush=True)
        hb.tick(unit_count, extra={"arm": "flat", "K": K, "acc": flat_acc[K]})
    out["flat_acc"] = flat_acc

    # --- Arm (iii) DECORRELATED (orthogonalized codebook; dense reference = flat_acc above) ---
    decorr_acc = {}
    for K in FLAT_K:
        books = make_books(K, M_FACTOR, N_DIM, g, decorr=True)
        succ = 0
        for _ in range(TRIALS):
            true = [int(g.integers(0, M_FACTOR)) for _ in range(K)]
            s = compose(books, true)
            got = resonate(s, books, K)
            succ += int(got == true)
        decorr_acc[K] = succ / TRIALS
        unit_count += 1
        print("  [seed=%d] DECORR K=%d acc=%.3f (dense-ref=%.3f)" % (seed, K, decorr_acc[K], flat_acc[K]), flush=True)
        hb.tick(unit_count, extra={"arm": "decorr", "K": K, "acc": decorr_acc[K]})
    out["decorr_acc"] = decorr_acc

    # --- Arm (ii) HIERARCHICAL ---
    hier_acc = {}
    hier_stage1_acc = {}
    for (F, ka, kb) in HIER_CONFIGS:
        books_a = make_books(ka, M_FACTOR, N_DIM, g)
        books_b = make_books(kb, M_FACTOR, N_DIM, g)
        succ = 0
        succ1 = 0
        for _ in range(TRIALS):
            true_a = [int(g.integers(0, M_FACTOR)) for _ in range(ka)]
            true_b = [int(g.integers(0, M_FACTOR)) for _ in range(kb)]
            s_a = compose(books_a, true_a)
            s_full = s_a * compose(books_b, true_b)
            dec_a = resonate(s_a, books_a, ka)
            s_a_hat = compose(books_a, dec_a)
            s_b_iso = s_full * np.conj(s_a_hat)
            dec_b = resonate(s_b_iso, books_b, kb)
            ok = (dec_a == true_a) and (dec_b == true_b)
            succ += int(ok)
            succ1 += int(dec_a == true_a)
        hier_acc[F] = succ / TRIALS
        hier_stage1_acc[F] = succ1 / TRIALS
        unit_count += 1
        print("  [seed=%d] HIER F=%d (ka=%d,kb=%d) acc=%.3f (stage1_acc=%.3f)" % (
            seed, F, ka, kb, hier_acc[F], hier_stage1_acc[F]), flush=True)
        hb.tick(unit_count, extra={"arm": "hier", "F": F, "acc": hier_acc[F]})
    out["hier_acc"] = hier_acc
    out["hier_stage1_acc"] = hier_stage1_acc
    out["unit_count"] = unit_count
    assert unit_count == EXPECTED_UNITS_PER_SEED, (
        "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got %d units, expected %d" % (unit_count, EXPECTED_UNITS_PER_SEED)
    )
    return out


def verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    flat = {K: float(np.mean([p["flat_acc"][K] for p in per_seed])) for K in FLAT_K}
    decorr = {K: float(np.mean([p["decorr_acc"][K] for p in per_seed])) for K in FLAT_K}
    hier = {F: float(np.mean([p["hier_acc"][F] for p in per_seed])) for F, _, _ in HIER_CONFIGS}

    ref = flat[4]
    f6, f8 = flat[6], flat[8]
    h6, h8 = hier[6], hier[8]
    d6, d8 = decorr[6], decorr[8]

    denom = max(ref, 1e-6)
    summary = (
        "REF(flat_F4)=%.3f flat={3:%.3f,4:%.3f,6:%.3f,8:%.3f} hier={6:%.3f,8:%.3f} decorr={6:%.3f,8:%.3f}"
        % (ref, flat[3], flat[4], flat[6], flat[8], hier[6], hier[8], decorr[6], decorr[8])
    )

    hard_pass = (
        h6 >= 0.70 * denom and h8 >= 0.40 * denom
        and f6 <= 0.30 * denom and f8 <= 0.15 * denom
        and (h6 - f6) >= 0.30 and (h8 - f8) >= 0.20
        and abs(d6 - f6) <= 0.15 and abs(d8 - f8) <= 0.15
    )
    hard_fail_no_rescue = abs(h6 - f6) <= 0.05 and abs(h8 - f8) <= 0.05
    hard_fail_decorr_rescues = (d6 - f6) >= 0.30

    if hard_pass:
        return ("HARD_PASS",
                "HARD_PASS: hierarchical staging rescues joint-factor decode at F=6/8 (gap F6=%+.3f F8=%+.3f "
                "vs flat's crater) while decorrelation shows no comparable rescue -- confirms hierarchy, not "
                "decorrelation, is the lever for RESONATOR FOCUS (distinct from the storage/bundle axis). %s"
                % (h6 - f6, h8 - f8, summary), locals_public(flat, decorr, hier, ref))
    if hard_fail_decorr_rescues:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND (positive surprise, Prediction-3 HARD-FAIL per research note): decorrelated codebook "
                "ALSO rescues F=6 (gap=%+.3f) -- decorrelation is NOT confined to the storage axis at this "
                "regime; re-open the two-axis-independence claim rather than treating this as a cell failure. %s"
                % (d6 - f6, summary), locals_public(flat, decorr, hier, ref))
    if hard_fail_no_rescue:
        return ("HARD_FAIL",
                "HARD_FAIL: hierarchical staging provides no measurable rescue at F=6 or F=8 (|hier-flat|<=0.05 "
                "both) -- the drill's #1 lever (hierarchical/sequential factorization) does not raise resonator "
                "focus at this regime; deprioritize in favor of decoupled-channels or paging. %s" % summary,
                locals_public(flat, decorr, hier, ref))
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: partial rescue pattern (not cleanly HARD-PASS or HARD-FAIL -- e.g. hierarchy helps "
            "at one of F=6/F=8 but not both, or decorrelation shows a small 0.05-0.30 partial rescue). %s"
            % summary, locals_public(flat, decorr, hier, ref))


def locals_public(flat, decorr, hier, ref) -> Dict:
    return {"flat_acc_mean": flat, "decorr_acc_mean": decorr, "hier_acc_mean": hier, "ref_flat_F4": ref}


print("[config] anchor=%s mode=%s N=%d M=%d MAX_IT=%d seeds=%s trials=%d flat_K=%s hier=%s" % (
    ANCHOR_NAME, RUN_MODE, N_DIM, M_FACTOR, MAX_IT, SEEDS, TRIALS, FLAT_K, HIER_CONFIGS), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)


def main():
    t0 = time.time()
    marker = {"pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": EXPECTED_UNITS_PER_SEED * len(SEEDS)}
    os.makedirs(out_dir, exist_ok=True)
    import json
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)

    per_seed = []
    total_units = EXPECTED_UNITS_PER_SEED * len(SEEDS)
    with CellHeartbeat(out_dir, total_units=total_units, interval_s=30) as hb:
        for seed in SEEDS:
            per_seed.append(run_seed(seed, hb))

    # ARMS-MUST-DIFFER (META_RULE_AF): flat vs decorr (same K grid, same shape) must not be
    # bit-identical after averaging across seeds.
    flat_vec = np.array([np.mean([p["flat_acc"][K] for p in per_seed]) for K in FLAT_K])
    decorr_vec = np.array([np.mean([p["decorr_acc"][K] for p in per_seed]) for K in FLAT_K])
    hier_vec = np.array([np.mean([p["hier_acc"][F] for p in per_seed]) for F, _, _ in HIER_CONFIGS])
    digests = _arms_must_differ({"flat": flat_vec, "decorr": decorr_vec, "hier": hier_vec})
    arms_differ_verified = True

    v, vmsg, agg = verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "per_seed": per_seed,
        "aggregate": agg,
        "arms_differ_verified": arms_differ_verified,
        "arm_digests": digests,
        "expected_n_units_per_seed": EXPECTED_UNITS_PER_SEED,
        "cardinality_ok": all(p["unit_count"] == EXPECTED_UNITS_PER_SEED for p in per_seed),
        "regime": {"N": N_DIM, "M": M_FACTOR, "MAX_IT": MAX_IT, "trials": TRIALS},
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written", flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(out_dir, ANCHOR_NAME, e)
    raise
