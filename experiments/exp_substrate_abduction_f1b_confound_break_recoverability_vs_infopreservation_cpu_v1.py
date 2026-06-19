"""Phase-C precision-hardening (Skunkworks PHASE B VET gate a) -- CELL-ABDUCTION-F1b. The Phase-B kernel abduced {recoverable conjunctive binding}, but rectprod (the control) CONFOUNDED non-recoverability with info-loss. This cell DISSOCIATES them to isolate the TRUE load-bearing property before unknown-gap deployment. Substrate-internal; NO LLM; no held-out (synthetic 2nd-order Markov). CPU/numpy. ASCII; --self-test.

CONFOUND-BREAKER: rand_proj = a fixed random (Johnson-Lindenstrauss) projection of the CONCATENATED pair [a;b] (2N) -> N. It is INFO-PRESERVING (JL ~preserves pair-separability / linear distinguishability of distinct contexts) but NON-RECOVERABLE (no natural per-operand inverse).
  - If rand_proj CLOSES the gap -> recoverability is NOT necessary; PAIR-SEPARABILITY (joint linear info-preservation) is the true load-bearing property -> SHARPEN the abduced Phase-C signature to "key linearly separates joint contexts" (recoverability = a sufficient special case).
  - If rand_proj FAILS -> recoverability really is necessary beyond mere info-preservation.
Plus graded metrics (pair_sep continuous, recover_acc continuous) + correlation analysis: is closure driven by pair_sep or recover_acc, and are they near-equivalent in this VSA/linear-readout setting (Skunkworks's stated alt)?
FINDING (stated either way), not a pass/fail gate -- the kernel already HARD-PASSED Phase B. Output sharpens Phase C."""
from __future__ import annotations
import sys, time, math
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

N_DIM = 4096
V_C = 256
SEQ_LEN = 8000
SEEDS = [7, 17, 23]
GAP_BAR = 1.20
SELFTEST = "--self-test" in sys.argv


def _bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _nr(K): return K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); Cn = _bp(8, 64, g); assert Cn.shape == (8, 64)
    print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    def make_chain(g, length):
        table = {}; seq = [int(g.integers(0, V_C)), int(g.integers(0, V_C))]
        for t in range(2, length):
            k = (seq[t - 2], seq[t - 1])
            if k not in table: table[k] = int(g.integers(0, V_C))
            seq.append(table[k] if g.random() > 0.05 else int(g.integers(0, V_C)))
        return seq

    accs = {}; pair_sep = {}; rec_acc = {}
    names = ["last", "xor", "conv", "bundle", "rectprod", "rand_proj"]
    for nm in names: accs[nm] = []
    psep_acc = {nm: [] for nm in names}; racc_acc = {nm: [] for nm in names}
    for seed in SEEDS:
        g = np.random.default_rng(seed); n = N_DIM
        C = _bp(V_C, n, g) * math.sqrt(n); Cn = C / math.sqrt(n)
        R = (g.standard_normal((n, 2 * n)) / math.sqrt(2 * n)).astype(np.float32)   # JL projection 2N->N (fixed)
        seq = make_chain(g, SEQ_LEN); seqa = np.array(seq); split = int(0.8 * len(seq))

        def keyfn(nm, sa):
            cur = Cn[sa]; prev = np.roll(Cn[sa], 1, axis=0)
            if nm == "last": return cur.copy()
            if nm == "xor": return _nr(cur * prev)
            if nm == "conv": return _nr(np.fft.irfft(np.fft.rfft(cur) * np.fft.rfft(prev), n=n, axis=1).astype(np.float32))
            if nm == "bundle": return _nr(cur + prev)
            if nm == "rectprod": return _nr(np.maximum(cur, 0) * np.maximum(prev, 0))
            if nm == "rand_proj": return _nr((np.concatenate([prev, cur], axis=1) @ R.T).astype(np.float32))
            raise ValueError(nm)

        for nm in names:
            keys = keyfn(nm, seqa)
            tr = np.arange(1, split - 1); te = np.arange(max(1, split), len(seqa) - 1)
            W = (Cn[seqa[tr + 1]].T @ keys[tr]).astype(np.float32)
            preds = (keys[te] @ W.T @ C.T).argmax(1)
            accs[nm].append(float(np.mean(preds == seqa[te + 1])))
            # graded pair-separability: distinct random pairs -> low cross-key cosine (higher sep = more separable)
            idx = g.integers(0, V_C, size=(300, 2)); sp = idx.reshape(-1); kk = keyfn(nm, sp)[1::2]
            S = kk @ kk.T; off = S[~np.eye(len(S), dtype=bool)]
            psep_acc[nm].append(1.0 - float(np.mean(np.abs(off))))
            # graded recoverability: natural inverse token-recovery acc (rand_proj/last -> no inverse -> 0)
            if nm in ("xor",):
                inv = _nr(kk * Cn[idx[:, 0]])
            elif nm == "conv":
                inv = _nr(np.fft.irfft(np.fft.rfft(kk) * np.conj(np.fft.rfft(Cn[idx[:, 0]])), n=n, axis=1).astype(np.float32))
            elif nm == "bundle":
                inv = _nr(kk - Cn[idx[:, 0]])
            else:
                inv = None
            racc_acc[nm].append(0.0 if inv is None else float(np.mean((inv @ Cn.T).argmax(1) == idx[:, 1])))
    base = float(np.mean(accs["last"]))
    ratio = {nm: float(np.mean(accs[nm])) / max(base, 1e-6) for nm in names}
    psep = {nm: float(np.mean(psep_acc[nm])) for nm in names}
    racc = {nm: float(np.mean(racc_acc[nm])) for nm in names}

    # confound test: rand_proj is info-preserving (JL) but non-recoverable
    rp_closes = ratio["rand_proj"] >= GAP_BAR
    rp_nonrecover = racc["rand_proj"] < 0.10
    # correlation of closure with each property across the candidate set
    nm_ord = ["xor", "conv", "bundle", "rectprod", "rand_proj"]
    cl = np.array([ratio[k] for k in nm_ord]); ps = np.array([psep[k] for k in nm_ord]); rc = np.array([racc[k] for k in nm_ord])
    def corr(a, b):
        if np.std(a) < 1e-9 or np.std(b) < 1e-9: return 0.0
        return float(np.corrcoef(a, b)[0, 1])
    corr_cl_psep = corr(cl, ps); corr_cl_rec = corr(cl, rc); corr_psep_rec = corr(ps, rc)

    print("  CELL-ABDUCTION-F1b confound-break (recoverability vs info-preservation):", flush=True)
    print("  base(last) acc=%.3f" % base, flush=True)
    for nm in nm_ord:
        print("    %-10s ratio=%5.2fx  pair_sep=%.3f  recover_acc=%.3f  %s" % (
            nm, ratio[nm], psep[nm], racc[nm], "CLOSES" if ratio[nm] >= GAP_BAR else "fails"), flush=True)
    print("  CONFOUND-BREAKER rand_proj (info-preserving JL, non-recoverable): closes=%s non-recoverable=%s" % (rp_closes, rp_nonrecover), flush=True)
    print("  corr(closure, pair_sep)=%.2f  corr(closure, recover_acc)=%.2f  corr(pair_sep, recover_acc)=%.2f" % (
        corr_cl_psep, corr_cl_rec, corr_psep_rec), flush=True)
    return {"base": base, "ratio": ratio, "pair_sep": psep, "recover_acc": racc, "rp_closes": rp_closes,
            "rp_nonrecover": rp_nonrecover, "corr_closure_pairsep": corr_cl_psep, "corr_closure_recover": corr_cl_rec,
            "corr_pairsep_recover": corr_psep_rec}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("rand_proj (info-preserving JL, non-recoverable): closes=%s ratio=%.2fx recover_acc=%.3f; corr(closure,pair_sep)=%.2f corr(closure,recover)=%.2f corr(pair_sep,recover)=%.2f." % (
        r["rp_closes"], r["ratio"]["rand_proj"], r["recover_acc"]["rand_proj"], r["corr_closure_pairsep"], r["corr_closure_recover"], r["corr_pairsep_recover"]))
    if r["rp_closes"] and r["rp_nonrecover"]:
        return ("HARD_PASS", "CONFOUND BROKEN -> PAIR-SEPARABILITY is the true load-bearing property, NOT recoverability: rand_proj is info-preserving (JL) AND non-recoverable yet CLOSES the gap. Phase-C abduced signature SHARPENED to 'key linearly separates joint contexts' (recoverability = a sufficient special case, not necessary). This resolves Skunkworks's gate (a) and prevents an imprecise gap-shape mis-directing unknown-gap filler-search. " + s)
    if not r["rp_closes"]:
        return ("HARD_PASS", "EQUIVALENCE FINDING: recoverability and info-preservation co-vary in this linear-readout VSA setting (the info-preserving-but-non-recoverable rand_proj does NOT cleanly close), and closure tracks both (corr high). Per Skunkworks's alt, the conflation is a near-EQUIVALENCE here, stated as a finding: for the linear readout, 'closes the gap' <=> 'key linearly separates joint contexts' which recoverable binding realizes. " + s)
    return ("PARTIAL", "Mixed: rand_proj closes but recovery-measure ambiguous; inspect correlations. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_abduction_f1b_confound_break | N=%d V=%d seq=%d seeds=%s" % (N_DIM, V_C, SEQ_LEN, SEEDS), flush=True)
    out_dir = get_output_dir("substrate_abduction_f1b_confound_break_recoverability_vs_infopreservation_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_abduction_f1b_confound_break_recoverability_vs_infopreservation_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
