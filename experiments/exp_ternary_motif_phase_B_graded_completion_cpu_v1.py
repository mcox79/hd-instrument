"""
PHASE-B TERNARY graded completion (DECISION 165a ARM 2). The CONFIRMED tier-2 partial-symmetric
composition corr(bundle(a,b),c) tested on the REAL mined math-scoped MOTIF-B motifs (not synthetic),
PER EFFECTIVE FAMILY, with the non-DFT-closure gate (Skunkworks meta-cluster: DFT-family 45% dominant
must not carry the whole claim).

Task (same generalization-split as the confirmed tier-2 novel_assembly_2, on REAL pairs): each motif is
(X; {Y,Z}) with {Y,Z} a SHARES_MATH/DUAL symmetric pair (math-corpus) and X the distinguished arg that
DEPENDS_ON both. Train a readout key(Y,Z)->X on ONE a-b ordering; TEST recovery of X on the SWAPPED
ordering key(Z,Y). Partial-symmetric corr(bundle(Y,Z),X) is symmetric in the pair -> generalizes the swap;
fully-asymmetric single binders memorize one ordering -> FAIL the swap; fully-symmetric singles conflate.
Candidate set = all distinct distinguished-args X (pooled); chance ~ 1/|candidates|.

Configs: C1 = 38-op single-binder basis (proxy: 5 uniform 3-ary singles xor3/conv3/bundle3/ghrr3/perm_idx3);
C2 = corr(bundle(a,b),c) partial-symmetric composition (+ alt compositions). HARD claim requires C2 to
CLOSE where all C1 fail, ACROSS a MAJORITY of the 5 effective families AND >=2 NON-DFT families.

Substrate-internal (random hypervectors as atom vectors; no LLM; vector-native bundle+corr; no graph-walk).
CPU/numpy, N=4096, full-mode multi-seed. ASCII.
"""
import sys, math, json
from pathlib import Path
from collections import defaultdict
import numpy as np

REPO = Path(__file__).resolve().parent.parent
DATA_ROOT = REPO / "data" / "substrate_index"
N_DIM = 4096
SEEDS = [7, 17, 23]
GAP_BAR = 0.80
EQUIV_TAU = 0.50
REPS = 24
FOURIER_META = {"discrete_fourier_transform", "fast_fourier_transform", "circular_convolution",
                "convolution_theorem_synthesis", "fhrr_bind"}


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def load_math_motifs():
    """Reuse the extractor's mining -> the 20 math-scoped MOTIF-B motifs (X, frozenset{Y,Z}), per effective family."""
    import importlib.util as u
    s = u.spec_from_file_location("ext", str(REPO / "experiments" / "exp_ternary_motif_phase_B_extractor_cpu_v1.py"))
    m = u.module_from_spec(s); sys.argv = ["ext"]; s.loader.exec_module(m)
    sym_pairs, sym_by_rel, dep, rdep, corpus, n_rel = m.load_graph()
    clean = sym_by_rel.get("SHARES_MATH", set()) | sym_by_rel.get("DUAL", set())
    _, cb = m.extract_motifs(clean, dep, rdep)
    ismath = lambda n: corpus.get(n, "") == "math"
    motifs = [(a, tuple(sorted(p))) for a, p in cb if ismath(a) and all(ismath(x) for x in p)]
    def fam(pair): return "DFT-META" if all(x in FOURIER_META for x in pair) else pair
    by_fam = defaultdict(list)
    for a, p in motifs:
        by_fam[fam(p)].append((a, p))
    return motifs, by_fam


def _bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _nr(K): return K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)


def run_family(fam_motifs, seed):
    """Faithful assembly_2 test on this family's REAL-motif 3-sets {Y,Z,X}: c-sensitivity (3 distinct
    target LABELS per 3-set, one per c-role -- no target-in-key leak) + a-b swap generalization.
    corr(bundle(a,b),c) is sym in a,b (generalizes swap) + c-sensitive (distinguishes c-role) -> closes;
    fully-symmetric singles conflate c-roles -> FAIL; asymmetric singles fail the swap -> FAIL."""
    g = np.random.default_rng(seed); n = N_DIM
    sets = []
    for (x, (y, z)) in fam_motifs:
        s = list({y, z, x})
        if len(s) == 3: sets.append((y, z, x))
    if not sets: return None
    atoms = sorted(set([a for t in sets for a in t]))
    idx = {nm: i for i, nm in enumerate(atoms)}
    V = _bp(len(atoms), n, g); Vn = V
    n_tgt = 3 * len(sets)
    T = _bp(n_tgt, n, g) * math.sqrt(n)            # SEPARATE target-label codebook (no leak: t not in {a,b,c})

    def corr(A, B): return _nr(np.fft.irfft(np.conj(np.fft.rfft(A)) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
    def conv(A, B): return _nr(np.fft.irfft(np.fft.rfft(A) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
    P1 = g.permutation(n); P2 = g.permutation(n)

    def key(nm, a, b, c):
        A, B, Cc = Vn[a], Vn[b], Vn[c]
        if nm == "xor3": return _nr(A * B * Cc)
        if nm == "conv3": return conv(conv(A, B), Cc)
        if nm == "bundle3": return _nr(A + B + Cc)
        if nm == "ghrr3": return corr(corr(A, B), Cc)
        if nm == "perm_idx3": return _nr(A + B[:, P1] + Cc[:, P2])
        if nm == "corr_bundle": return corr(_nr(A + B), Cc)
        if nm == "xor_corr": return corr(_nr(A * B), Cc)
        raise ValueError(nm)

    SINGLES = ["xor3", "conv3", "bundle3", "ghrr3", "perm_idx3"]; COMPS = ["corr_bundle", "xor_corr"]
    names = SINGLES + COMPS
    tr, te = [], []
    for si, (y, z, x) in enumerate(sets):
        yi, zi, xi = idx[y], idx[z], idx[x]
        t1, t2, t3 = 3 * si, 3 * si + 1, 3 * si + 2     # 3 distinct target labels = 3 c-roles (c-sensitivity)
        # train one a-b ordering of each c-role; test SWAPPED a-b ordering (same target)
        for (a, b, c, t) in [(yi, zi, xi, t1), (yi, xi, zi, t2), (zi, xi, yi, t3)]:
            for _ in range(REPS): tr.append((a, b, c, t))
        for (a, b, c, t) in [(zi, yi, xi, t1), (xi, yi, zi, t2), (xi, zi, yi, t3)]:
            te.append((a, b, c, t))
    tr = np.array(tr); te = np.array(te)
    accs = {}
    for nm in names:
        ktr = key(nm, tr[:, 0], tr[:, 1], tr[:, 2])
        W = ((T / math.sqrt(n))[tr[:, 3]].T @ ktr).astype(np.float32)
        kte = key(nm, te[:, 0], te[:, 1], te[:, 2])
        preds = (kte @ W.T @ T.T).argmax(1)
        accs[nm] = float(np.mean(preds == te[:, 3]))
    return accs


def run():
    motifs, by_fam = load_math_motifs()
    all_X = [a for a, _ in motifs]
    fam_order = sorted(by_fam.keys(), key=lambda k: -len(by_fam[k]))
    print(f"[config] math-scoped MOTIF-B motifs={len(motifs)} | effective families={len(by_fam)} | candidates(distinct X)={len(set(all_X))}", flush=True)
    SINGLES = ["xor3", "conv3", "bundle3", "ghrr3", "perm_idx3"]
    COMPS = ["corr_bundle", "xor_corr"]
    fam_results = {}
    for fam in fam_order:
        fm = by_fam[fam]
        per_seed = [run_family(fm, s) for s in SEEDS]
        per_seed = [r for r in per_seed if r]
        if not per_seed: continue
        macc = {nm: float(np.mean([r[nm] for r in per_seed])) for nm in (SINGLES + COMPS)}
        single_close = [s for s in SINGLES if macc[s] >= GAP_BAR]
        c2_close = macc["corr_bundle"] >= GAP_BAR
        closes_where_singles_fail = c2_close and len(single_close) == 0
        is_dft = (fam == "DFT-META")
        fam_results[str(fam)] = {"n": len(fm), "macc": macc, "single_closers": single_close,
                                 "c2_corr_bundle": macc["corr_bundle"], "closes_clean": closes_where_singles_fail,
                                 "is_dft": is_dft}
        label = "DFT-META" if is_dft else f"{fam[0]}+{fam[1]}"
        print(f"  [{label}] n={len(fm)} corr_bundle={macc['corr_bundle']:.3f} "
              f"best_single={max(macc[s] for s in SINGLES):.3f} "
              f"{'C2-CLOSES-where-singles-FAIL' if closes_where_singles_fail else ('C2-closes-but-single-also' if c2_close else 'C2-fails')}", flush=True)
    return fam_results


def verdict(fam_results):
    closing = [f for f, r in fam_results.items() if r["closes_clean"]]
    nondft_closing = [f for f in closing if not fam_results[f]["is_dft"]]
    n_fam = len(fam_results)
    majority = len(closing) >= math.ceil(n_fam / 2)
    nondft_ok = len(nondft_closing) >= 2
    if majority and nondft_ok:
        return ("HARD_PASS", f"corr(bundle,c) CLOSES (where all single binders fail) on {len(closing)}/{n_fam} effective families "
                f"incl {len(nondft_closing)} NON-DFT -> GENERAL partial-symmetry on real mined motifs (majority + >=2 non-DFT). closing={closing}")
    if closing and not nondft_ok:
        return ("MIDDLE_BAND", f"corr(bundle,c) closes {len(closing)}/{n_fam} families but <2 NON-DFT ({nondft_closing}) "
                f"-> Fourier-family-specific, NOT general partial-symmetry. closing={closing}")
    if not closing:
        return ("HARD_FAIL", f"corr(bundle,c) closes 0 families where singles fail -> no partial-symmetry advantage on real motifs.")
    return ("MIDDLE_BAND", f"corr(bundle,c) closes {len(closing)}/{n_fam} families (not majority). closing={closing}")


if __name__ == "__main__":
    print("[start] PHASE-B TERNARY graded completion (ARM 2; real math-scoped motifs; per effective family; non-DFT closure gate)", flush=True)
    fr = run()
    v, msg = verdict(fr)
    print(f"\n[VERDICT] {v} -- {msg}", flush=True)
    out = REPO / "data" / "phase_B_ternary_graded_verdict_2026-06-16.json"
    out.write_text(json.dumps({"verdict": v, "msg": msg, "families": fr}, indent=2))
    print(f"[metrics] written {out}", flush=True)
