"""
PHASE-B ARM 2 REQUIRED-A: ternary partial-symmetry vs the EXTENDED RUNNABLE single-binder basis (DECISION
181/PATH A). Replaces the 5-op proxy with the ~8 distinct RUNNABLE single-binder 3-ary ops (the implemented
inventory; HONEST SCOPE: the substrate's "38 ops" are SIGNATURES -- ~8 are runnable hypervector functions; the
2026-06-15 38-op vet was signature-level on the synthetic gap). Tests whether corr(bundle(a,b),c) (the confirmed
tier-2 partial-symmetric composition) closes the REAL math-scoped motif families where ALL extended single
binders FAIL -- per effective family, non-DFT-closure gate, difficulty-normalized.

HEAVY (real-motif completion x ~8 binders x families x seeds, N=4096) -> RUNS ON THE REMOTE DESKTOP per USER
compute policy (queue_add -> remote_cpu_queue). Queue-compatible: --self-test, --smoke, full-mode metrics.json.

Honest both directions: this is the EXTENDED-RUNNABLE-BASIS check (path A), NOT a 38-runnable-function sweep
(those don't exist). corr_bundle novel vs the 8 runnable singles + the prior signature-level 38-op vet.
CPU/numpy, ASCII.
"""
import sys, os, time, math, json
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR = "ternary_motif_phase_B_arm2_extended_basis_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELFTEST = "--self-test" in sys.argv
N_DIM = 1024 if RUN_MODE == "smoke" else 4096
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23]
GAP_BAR = 0.80
REPS = 8 if RUN_MODE == "smoke" else 24
FOURIER_META = {"discrete_fourier_transform", "fast_fourier_transform", "circular_convolution",
                "convolution_theorem_synthesis", "fhrr_bind"}


def _bp(M, n, g): X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
def _nr(K): return K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)


def _make_ops(n, g):
    P1, P2, P3 = g.permutation(n), g.permutation(n), g.permutation(n)
    def corr(A, B): return _nr(np.fft.irfft(np.conj(np.fft.rfft(A)) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
    def conv(A, B): return _nr(np.fft.irfft(np.fft.rfft(A) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
    # EXTENDED RUNNABLE single-binder 3-ary ops (the implemented inventory; uniform-op + positional variants)
    SINGLES = {
        "xor3":        lambda a, b, c: _nr(a * b * c),
        "conv3":       lambda a, b, c: conv(conv(a, b), c),
        "bundle3":     lambda a, b, c: _nr(a + b + c),
        "ghrr3":       lambda a, b, c: corr(corr(a, b), c),
        "perm_idx3":   lambda a, b, c: _nr(a + b[:, P1] + c[:, P2]),
        "xorperm3":    lambda a, b, c: _nr((a * b * c)[:, P1]),
        "bundleperm3": lambda a, b, c: _nr(a[:, P1] + b[:, P2] + c[:, P3]),
        "convperm3":   lambda a, b, c: conv(conv(a, b[:, P1]), c[:, P2]),
        "corrperm3":   lambda a, b, c: corr(corr(a, b[:, P1]), c[:, P2]),  # permuted-correlation (REQUIRED-A completeness)
    }
    COMPS = {
        "corr_bundle": lambda a, b, c: corr(_nr(a + b), c),   # THE confirmed tier-2 partial-symmetric closer
        "xor_corr":    lambda a, b, c: corr(_nr(a * b), c),   # alt partial-symmetric composition
    }
    return SINGLES, COMPS


def load_math_motifs():
    import importlib.util as u
    s = u.spec_from_file_location("ext", str(REPO / "experiments" / "exp_ternary_motif_phase_B_extractor_cpu_v1.py"))
    m = u.module_from_spec(s); _argv = sys.argv; sys.argv = ["ext"]; s.loader.exec_module(m); sys.argv = _argv
    sym_pairs, sym_by_rel, dep, rdep, corpus, n_rel = m.load_graph()
    clean = sym_by_rel.get("SHARES_MATH", set()) | sym_by_rel.get("DUAL", set())
    _, cb = m.extract_motifs(clean, dep, rdep)
    ismath = lambda nm: corpus.get(nm, "") == "math"
    motifs = [(a, tuple(sorted(p))) for a, p in cb if ismath(a) and all(ismath(x) for x in p)]
    from collections import defaultdict
    fam = lambda pr: "DFT-META" if all(x in FOURIER_META for x in pr) else pr
    by = defaultdict(list)
    for a, p in motifs: by[fam(p)].append((a, p))
    return by


def run_family(fam_motifs, seed):
    g = np.random.default_rng(seed); n = N_DIM
    sets = [(y, z, x) for (x, (y, z)) in fam_motifs if len({x, y, z}) == 3]
    if not sets: return None
    atoms = sorted({a for t in sets for a in t}); idx = {nm: i for i, nm in enumerate(atoms)}
    V = _bp(len(atoms), n, g); Vn = V
    T = _bp(3 * len(sets), n, g) * math.sqrt(n)
    SINGLES, COMPS = _make_ops(n, g)
    tr, te = [], []
    for si, (y, z, x) in enumerate(sets):
        yi, zi, xi = idx[y], idx[z], idx[x]; t1, t2, t3 = 3 * si, 3 * si + 1, 3 * si + 2
        for (a, b, c, t) in [(yi, zi, xi, t1), (yi, xi, zi, t2), (zi, xi, yi, t3)]:
            for _ in range(REPS): tr.append((a, b, c, t))
        for (a, b, c, t) in [(zi, yi, xi, t1), (xi, yi, zi, t2), (xi, zi, yi, t3)]:
            te.append((a, b, c, t))
    tr, te = np.array(tr), np.array(te)
    accs = {}
    for nm, op in {**SINGLES, **COMPS}.items():
        ktr = op(Vn[tr[:, 0]], Vn[tr[:, 1]], Vn[tr[:, 2]])
        W = ((T / math.sqrt(n))[tr[:, 3]].T @ ktr).astype(np.float32)
        kte = op(Vn[te[:, 0]], Vn[te[:, 1]], Vn[te[:, 2]])
        accs[nm] = float(np.mean((kte @ W.T @ T.T).argmax(1) == te[:, 3]))
    return accs


def run():
    by = load_math_motifs()
    SING = ["xor3", "conv3", "bundle3", "ghrr3", "perm_idx3", "xorperm3", "bundleperm3", "convperm3", "corrperm3"]  # 9 (REQUIRED-A)
    fam_res = {}
    for fam, fm in sorted(by.items(), key=lambda x: -len(x[1])):
        rows = [run_family(fm, s) for s in SEEDS]; rows = [r for r in rows if r]
        if not rows: continue
        macc = {nm: float(np.mean([r[nm] for r in rows])) for nm in rows[0]}
        best_single = max(macc[s] for s in SING)
        cb_acc = macc["corr_bundle"]
        # SEED-VARIANCE (REQUIRED-B; mode-iii): per-seed corr_bundle + best-of-9-single + margin spread
        cb_ps = [r["corr_bundle"] for r in rows]
        bs_ps = [max(r[s] for s in SING) for r in rows]
        cb_std = float(np.std(cb_ps)); margin_ps = [c - b for c, b in zip(cb_ps, bs_ps)]
        drift = cb_std > 0.40
        fam_res[str(fam)] = {"n": len(fm), "corr_bundle": cb_acc, "best_single": best_single,
                             "closes_clean": (cb_acc >= GAP_BAR and best_single < GAP_BAR),
                             "margin": cb_acc - best_single, "is_dft": fam == "DFT-META", "macc": macc,
                             "corr_bundle_per_seed": cb_ps, "corr_bundle_std": cb_std,
                             "margin_per_seed": margin_ps, "min_margin": min(margin_ps), "drift": drift}
        print(f"  [{('DFT-META' if fam=='DFT-META' else str(fam))}] n={len(fm)} corr_bundle={cb_acc:.3f}(std {cb_std:.3f}) best_single(9)={best_single:.3f} margin={cb_acc-best_single:+.3f} min_margin={min(margin_ps):+.3f} {'DRIFT' if drift else 'no-drift'} {'CLOSES-where-9singles-FAIL' if fam_res[str(fam)]['closes_clean'] else ''}", flush=True)
    return fam_res


def verdict(fr):
    closing = [f for f, r in fr.items() if r["closes_clean"]]
    nondft = [f for f in closing if not fr[f]["is_dft"]]
    universal_margin = all(r["margin"] > 0 for r in fr.values())   # corr beats best-of-9 in every family
    no_drift = all(not r["drift"] for r in fr.values())            # REQUIRED-B: mode-iii seed-variance
    n = len(fr)
    if len(closing) >= math.ceil(n / 2) and len(nondft) >= 2 and no_drift:
        return ("HARD_PASS", f"corr(bundle,c) CLOSES where ALL 9 EXTENDED runnable single-binders FAIL on {len(closing)}/{n} families incl {len(nondft)} NON-DFT (majority + >=2 non-DFT); universal-margin={universal_margin}; no-drift={no_drift} (tier-A). Extended-runnable-basis (path A; +corrperm3); 38 are signatures, 9 runnable.")
    if not no_drift:
        return ("MIDDLE_BAND", f"DRIFT detected (mode-iii: some family corr_bundle seed-std>0.40) -> not tier-A robust; closing {len(closing)}/{n}, universal-margin={universal_margin}.")
    if universal_margin:
        return ("MIDDLE_BAND", f"corr beats best-of-9 in ALL families (universal margin, no-drift) but closes-absolute on {len(closing)}/{n} (cardinality-bounded); non-DFT={len(nondft)}.")
    return ("HARD_FAIL", f"corr does not clear the extended-basis bar (closing {len(closing)}/{n}; universal-margin={universal_margin}).")


def _selftest():
    g = np.random.default_rng(0); S, C = _make_ops(64, g)
    a = _bp(3, 64, g); assert C["corr_bundle"](a[:1], a[1:2], a[2:3]).shape == (1, 64)
    print("[selftest] PASS", flush=True)


if __name__ == "__main__":
    if SELFTEST:
        _selftest(); sys.exit(0)
    print(f"[start] {ANCHOR} run_mode={RUN_MODE} N={N_DIM} seeds={SEEDS} (extended runnable single-binder basis = 8)", flush=True)
    _selftest()
    out_dir = get_output_dir(os.environ.get("HDLAB_EXP_NAME", ANCHOR)); t0 = time.time()
    fr = run(); v, vmsg = verdict(fr)
    print(f"\n[VERDICT] {v} -- {vmsg}", flush=True)
    metrics = {"anchor_name": ANCHOR, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
               "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "N": N_DIM, "per_seed": [fr],
               "families": fr, "elapsed_s": time.time() - t0,
               "compute_backend": "cpu", "dtype": "float32"}
    write_metrics(out_dir, metrics, [fr]); print(f"[metrics] written {out_dir}/metrics.json", flush=True)
