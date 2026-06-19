"""
PHASE-B ARM 3 -- C3 INTERNAL-ABSTRACTION-DISCOVERY (DECISION 165a/178a; spec 180+182).
The strongest Phase-B claim: does the substrate AUTONOMOUSLY DISCOVER the partial-symmetric composition
corr(bundle(a,b),c) -- the CONFIRMED tier-2 closer -- from a seed library of in-basis primitives that
EXCLUDES the target composite? DreamCoder/Stitch-class library learning, substrate-internal (native ops;
no learned codebook; 11th rule).

Per Skunkworks precondition (DECISION 175/PROACTIVE): ternary C3 is DEFINITIVELY tier-2 (corr+bundle both
in-basis; composition existence-proven) -> a CLEAN pure-DISCOVERABILITY test. A FAIL is SEARCH-LIMITED ONLY
(no tier-3 ambiguity). Discovery != leakage: seed library EXCLUDES corr_bundle (the search must COMPOSE it).

Method (depth-2 composition search):
  - seed primitives (depth-1 binary ops, in-basis): bundle (superposition), corr (correlation), conv
    (convolution), xor (elementwise) -- NOT corr_bundle (the target; excluded per leakage gate)
  - search space: key(a,b,c) = op2(op1(a,b), c) for op1,op2 in primitives (depth-2 compositions)
  - depth-1 controls: uniform single op on all 3 args (the basis null that must FAIL)
  - DISCOVERY: a composition CLOSES the partial-symmetric generalization-split gap (gen-acc>=0.80) where
    all depth-1 controls FAIL
  - REUSABILITY (Drill-1 criterion): a discovered composition must ALSO close a 2nd INDEPENDENT
    partial-symmetric signature (not just the seed gap)
  - AUTONOMOUS-PASS: >=1 discovered composition closes gap-1 AND reuses to gap-2 AND is a COMPOSITION
    (not a seeded primitive)
  - budget: compositions evaluated (<=100; depth-2 over 4 primitives = 16, well under)

Substrate-internal; CPU/numpy. ASCII.
"""
import sys, math
import numpy as np

N_DIM = 4096
V_C = 96
N_TRIPLES = 320
REPS = 24
GAP_BAR = 0.80
SEEDS = [7, 17, 23]
BUDGET = 100


def _bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _nr(K): return K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)


def _make_ops(n):
    def corr(A, B): return _nr(np.fft.irfft(np.conj(np.fft.rfft(A)) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
    def conv(A, B): return _nr(np.fft.irfft(np.fft.rfft(A) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
    def bundle(A, B): return _nr(A + B)
    def xor(A, B): return _nr(A * B)
    return {"bundle": bundle, "corr": corr, "conv": conv, "xor": xor}


def _gap_dataset(g, V_c):
    """assembly_2-style partial-symmetric gap: target=f({a,b},c) sym in a,b + c-sensitive; 3 c-roles
    (distinct targets) + train one a-b ordering, test SWAPPED ordering (held-out)."""
    tr, te = [], []
    for _ in range(N_TRIPLES):
        x, y, z = (int(v) for v in g.integers(0, V_c, 3))
        if len({x, y, z}) < 3: continue
        t1, t2, t3 = (int(v) for v in g.integers(0, V_c, 3))
        for (a, b, c, t) in [(x, y, z, t1), (x, z, y, t2), (y, z, x, t3)]:
            for _ in range(REPS): tr.append((a, b, c, t))
        for (a, b, c, t) in [(y, x, z, t1), (z, x, y, t2), (z, y, x, t3)]:
            te.append((a, b, c, t))
    return np.array(tr), np.array(te)


def _eval_key(keyfn, Cn, C, tr, te):
    ktr = keyfn(Cn[tr[:, 0]], Cn[tr[:, 1]], Cn[tr[:, 2]])
    W = (Cn[tr[:, 3]].T @ ktr).astype(np.float32)
    kte = keyfn(Cn[te[:, 0]], Cn[te[:, 1]], Cn[te[:, 2]])
    preds = (kte @ W.T @ C.T).argmax(1)
    return float(np.mean(preds == te[:, 3]))


def run_one_gap(seed, n):
    """Returns (depth2_accs dict, depth1_accs dict) for one gap instance."""
    g = np.random.default_rng(seed)
    C = _bp(V_C, n, g) * math.sqrt(n); Cn = C / math.sqrt(n)
    ops = _make_ops(n)
    tr, te = _gap_dataset(g, V_C)
    # depth-1 controls: uniform single op on all 3 (op(op(a,b),c)) -- the basis null that must FAIL
    d1 = {}
    for nm, op in ops.items():
        d1[nm] = _eval_key(lambda A, B, Cc, op=op: op(op(A, B), Cc), Cn, C, tr, te)
    # depth-2 search: op2(op1(a,b), c)
    d2 = {}; evals = 0
    for n1, op1 in ops.items():
        for n2, op2 in ops.items():
            if evals >= BUDGET: break
            d2[f"{n2}({n1}(a,b),c)"] = _eval_key(lambda A, B, Cc, o1=op1, o2=op2: o2(o1(A, B), Cc), Cn, C, tr, te)
            evals += 1
    return d2, d1, evals


def run():
    print(f"[start] PHASE-B ARM 3 C3 abstraction-discovery (depth-2 search; seed lib EXCLUDES corr_bundle; N={N_DIM})", flush=True)
    # gap-1 (discovery) + gap-2 (reusability), independent seeds
    d2_1 = {nm: [] for nm in []}; d1_1 = {}; d2_2 = {}
    # average over seeds for stability
    agg_d2_g1, agg_d1_g1, agg_d2_g2 = {}, {}, {}
    total_evals = 0
    for seed in SEEDS:
        d2g1, d1g1, ev = run_one_gap(seed, N_DIM)
        d2g2, _, _ = run_one_gap(seed + 1000, N_DIM)   # independent 2nd signature
        total_evals += ev
        for k, v in d2g1.items(): agg_d2_g1.setdefault(k, []).append(v)
        for k, v in d1g1.items(): agg_d1_g1.setdefault(k, []).append(v)
        for k, v in d2g2.items(): agg_d2_g2.setdefault(k, []).append(v)
    d2_g1 = {k: float(np.mean(v)) for k, v in agg_d2_g1.items()}
    d1_g1 = {k: float(np.mean(v)) for k, v in agg_d1_g1.items()}
    d2_g2 = {k: float(np.mean(v)) for k, v in agg_d2_g2.items()}

    print("  depth-1 controls (basis null; must FAIL):", flush=True)
    for k, v in sorted(d1_g1.items(), key=lambda x: -x[1]):
        print(f"     {k:24s} gen-acc={v:.3f} {'CLOSES(!?)' if v >= GAP_BAR else 'fails'}", flush=True)
    d1_closes = [k for k, v in d1_g1.items() if v >= GAP_BAR]

    print("  depth-2 compositions (discovery search; gap-1):", flush=True)
    discovered = []
    for k, v in sorted(d2_g1.items(), key=lambda x: -x[1]):
        closes = v >= GAP_BAR
        reuse = d2_g2.get(k, 0.0)
        reuses = reuse >= GAP_BAR
        is_comp = "(" in k  # a composition, not a primitive
        flag = ""
        if closes and len(d1_closes) == 0 and is_comp:
            flag = " DISCOVERED" + (f" + REUSES(gap2={reuse:.3f})" if reuses else f" but NOT-reuse(gap2={reuse:.3f})")
            if reuses: discovered.append(k)
        print(f"     {k:24s} gap1={v:.3f} gap2={reuse:.3f} {'closes' if closes else 'fails'}{flag}", flush=True)

    gate_singles_fail = len(d1_closes) == 0
    autonomous_pass = gate_singles_fail and len(discovered) >= 1
    return {"d1": d1_g1, "d2_g1": d2_g1, "d2_g2": d2_g2, "d1_closes": d1_closes,
            "discovered_reusable": discovered, "autonomous_pass": autonomous_pass, "evals": total_evals}


def verdict(r):
    if not r["d1_closes"] == []:
        return ("HARD_FAIL", f"a depth-1 single op closes the gap ({r['d1_closes']}) -> not a partial-symmetry gap (no discovery needed). Not a valid C3 test.")
    if r["autonomous_pass"]:
        return ("HARD_PASS", f"AUTONOMOUS-DISCOVERY: the substrate's composition-search DISCOVERED {r['discovered_reusable']} (compositions of in-basis primitives, corr_bundle EXCLUDED from seed) that CLOSE the partial-symmetric gap where ALL depth-1 singles FAIL, AND REUSE to a 2nd independent signature. FIRST autonomous tier-2 composition-discovery. (budget {r['evals']} evals)")
    # FAIL = search-limited only (definitively tier-2; the composition exists in-basis)
    closers = [k for k, v in r["d2_g1"].items() if v >= GAP_BAR]
    return ("PARTIAL", f"depth-2 search found {len(closers)} gap-1 closers {closers} but none REUSED to gap-2 (reusability unmet) OR none discovered. SEARCH-LIMITED (definitively tier-2; composition is in-basis) -- widen search/budget. NOT a tier-3 signal. (budget {r['evals']})")


if __name__ == "__main__":
    r = run()
    v, msg = verdict(r)
    print(f"\n[VERDICT] {v} -- {msg}", flush=True)
    import json
    from pathlib import Path
    Path("data/phase_B_ARM3_C3_verdict_2026-06-16.json").write_text(json.dumps({"verdict": v, "msg": msg, **{k: r[k] for k in ["d1_closes","discovered_reusable","autonomous_pass","evals"]}}, indent=2))
    print("[metrics] written data/phase_B_ARM3_C3_verdict_2026-06-16.json", flush=True)
