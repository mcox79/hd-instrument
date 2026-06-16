"""Phase C TIER-2 genuine-novelty test (Skunkworks 3-tier refinement) -- CELL-NOVEL-ASSEMBLY-2. The decisive SUBSTRATE-INTERNAL novelty target: a NOVEL COMPOSITION that (gate a) NO single existing operator closes -- FULL basis incl ghrr -- AND (gate b) is NOT extensionally-equivalent to ANY single existing operator (the equivalence-check gate that CELL-NOVEL-ASSEMBLY-1 was MISSING, which let perm-o-xor == ghrr slip through as fake novelty). Substrate-internal; NO LLM; no held-out (synthetic). CPU/numpy. ASCII; --self-test.

THE GAP (designed so over-distinguishing single ops FAIL via a GENERALIZATION split -- the pitfall that sank ASSEMBLY-1's premise where ghrr just over-distinguished and closed): target = f({a,b}, c) -- SYMMETRIC in a,b (swapping a<->b keeps the target) but SENSITIVE to c's position. TEST on HELD-OUT a-b orderings (train sees (a,b,c); test queries the unseen (b,a,c)).
  - fully-SYMMETRIC single ops (xor3=a*b*c, conv3, bundle3=a+b+c): conflate c with a,b (key(a,b,c)==key(a,c,b)) -> FAIL c-sensitivity.
  - fully-ASYMMETRIC single ops (ghrr3 chained correlation, perm_idx3 positional): distinct key per ordering -> MEMORIZE seen orderings but FAIL to generalize to the held-out swapped ordering (no a-b symmetry) -> FAIL the generalization split.
  - PARTIAL-symmetric COMPOSITION corr(bundle(a,b), c): symmetric in a,b (generalizes across the swap) AND c-sensitive (corr is order-sensitive for c) -> CLOSES on the generalization split. And it is NOT equivalent to any single op (different functional form).
GATES: (a) NO single op closes the generalization split; (b) the closing composition is NOT extensionally-equivalent to any single op (max key-cosine on random triples < EQUIV_TAU); (c) certified by gap-closure (generalization accuracy).
TIER-2 PASS (genuine substrate-internal novel composition): gates a AND b AND c. TIER-1 (rediscovery) if a single op closes OR the composition is equivalent to one (ASSEMBLY-1's failure). TIER-3 (novel primitive) is OUT OF SCOPE (needs external truth).
DISCIPLINE (post-ASSEMBLY-1 retraction): the equivalence-check is FIRST-CLASS; report honestly if a single op closes (gate a fails -> not a novelty gap) or the composition is equivalent (gate b fails -> rediscovery)."""
from __future__ import annotations
import sys, time, math
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

N_DIM = 4096
V_C = 96
N_TRIPLES = 320
REPS = 24
GAP_BAR = 0.80
EQUIV_TAU = 0.50          # composition is "equivalent" to a single op if max key-cosine on random triples >= this
SEEDS = [7, 17, 23]
SELFTEST = "--self-test" in sys.argv


def _bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _nr(K): return K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); assert _bp(4, 32, g).shape == (4, 32); print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    SINGLES = ["xor3", "conv3", "bundle3", "ghrr3", "perm_idx3"]   # full single-operator basis (uniform 3-ary extensions)
    COMPS = ["corr_bundle", "bundle_corr", "xor_corr"]            # candidate non-uniform compositions (combine-search)
    names = SINGLES + COMPS
    accs = {nm: [] for nm in names}; equiv_max = {nm: [] for nm in COMPS}
    for seed in SEEDS:
        g = np.random.default_rng(seed); n = N_DIM
        C = _bp(V_C, n, g) * math.sqrt(n); Cn = C / math.sqrt(n)
        P1 = g.permutation(n); P2 = g.permutation(n)

        def corr(A, B): return _nr(np.fft.irfft(np.conj(np.fft.rfft(A)) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
        def conv(A, B): return _nr(np.fft.irfft(np.fft.rfft(A) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))

        def key(nm, a, b, c):
            A, B, Cc = Cn[a], Cn[b], Cn[c]
            if nm == "xor3": return _nr(A * B * Cc)
            if nm == "conv3": return conv(conv(A, B), Cc)
            if nm == "bundle3": return _nr(A + B + Cc)
            if nm == "ghrr3": return corr(corr(A, B), Cc)
            if nm == "perm_idx3": return _nr(A + B[:, P1] + Cc[:, P2])
            if nm == "corr_bundle": return corr(_nr(A + B), Cc)        # PARTIAL-symmetric: sym(a,b) + c-sensitive
            if nm == "bundle_corr": return _nr(_nr(A + B) + Cc)        # ~fully symmetric (degenerate)
            if nm == "xor_corr": return corr(_nr(A * B), Cc)           # sym(a,b via xor) + c-sensitive (alt partial)
            raise ValueError(nm)

        # dataset: target = f({a,b}, c), SYMMETRIC in a,b + SENSITIVE to c-position. For each 3-set {x,y,z} register ALL
        # THREE c-role assignments with distinct targets (forces c-sensitivity -> full-symmetric ops collide). TRAIN on ONE
        # a-b ordering; TEST on the SWAPPED a-b ordering of the SAME items (target WAS trained; requires a-b symmetry to
        # generalize -> asymmetric ops, whose swapped key is unseen, FAIL).
        tr = []; te = []
        for _ in range(N_TRIPLES):
            x, y, z = (int(v) for v in g.integers(0, V_C, 3))
            if len({x, y, z}) < 3: continue
            t1, t2, t3 = (int(v) for v in g.integers(0, V_C, 3))      # ({x,y},z),({x,z},y),({y,z},x) distinct targets
            # train: one a-b ordering of each c-assignment (a,b = the pair; c = the singleton)
            for (a, b, c, t) in [(x, y, z, t1), (x, z, y, t2), (y, z, x, t3)]:
                for _ in range(REPS): tr.append((a, b, c, t))
            # test: SWAP a<->b (same {a,b}, same c) -> unseen ordering; a-b-symmetric ops generalize
            for (a, b, c, t) in [(y, x, z, t1), (z, x, y, t2), (z, y, x, t3)]:
                te.append((a, b, c, t))
        tr = np.array(tr); te = np.array(te)
        for nm in names:
            ktr = key(nm, tr[:, 0], tr[:, 1], tr[:, 2]); kte = key(nm, te[:, 0], te[:, 1], te[:, 2])
            W = (Cn[tr[:, 3]].T @ ktr).astype(np.float32)
            preds = (kte @ W.T @ C.T).argmax(1)
            accs[nm].append(float(np.mean(preds == te[:, 3])))
        # equivalence-check: composition vs each single op, max key-cosine on random triples
        rt = g.integers(0, V_C, size=(400, 3))
        for cm in COMPS:
            kc = key(cm, rt[:, 0], rt[:, 1], rt[:, 2])
            mx = 0.0
            for s in SINGLES:
                ks = key(s, rt[:, 0], rt[:, 1], rt[:, 2]); mx = max(mx, float(np.mean(np.sum(kc * ks, axis=1))))
            equiv_max[cm].append(mx)

    macc = {nm: float(np.mean(accs[nm])) for nm in names}
    eqv = {cm: float(np.mean(equiv_max[cm])) for cm in COMPS}
    single_closers = [s for s in SINGLES if macc[s] >= GAP_BAR]
    comp_closers = [c for c in COMPS if macc[c] >= GAP_BAR]
    # tier-2: gate a (no single closes) + gate b (a comp closer is NOT equivalent to any single) + gate c (it closes)
    novel_comps = [c for c in comp_closers if eqv[c] < EQUIV_TAU]
    gate_a = len(single_closers) == 0
    gate_b = len(novel_comps) >= 1
    tier2_pass = gate_a and gate_b

    print("  CELL-NOVEL-ASSEMBLY-2 (TIER-2 novel composition; generalization split; equivalence-checked):", flush=True)
    print("  task: target=f({a,b},c) sym in a,b + c-sensitive; TEST on held-out SWAPPED ordering; close bar=%.2f" % GAP_BAR, flush=True)
    for nm in SINGLES:
        print("    SINGLE   %-12s gen-acc=%.3f %s" % (nm, macc[nm], "CLOSES" if macc[nm] >= GAP_BAR else "fails"), flush=True)
    for cm in COMPS:
        print("    COMP     %-12s gen-acc=%.3f equiv-max-to-single=%.3f %s%s" % (
            cm, macc[cm], eqv[cm], "CLOSES" if macc[cm] >= GAP_BAR else "fails",
            " [NOT-equiv->NOVEL]" if (macc[cm] >= GAP_BAR and eqv[cm] < EQUIV_TAU) else (" [equiv->rediscovery]" if macc[cm] >= GAP_BAR else "")), flush=True)
    print("  gate a (NO single closes)=%s | single_closers=%s" % (gate_a, single_closers), flush=True)
    print("  gate b (closing comp NOT equiv to any single)=%s | novel_comps=%s" % (gate_b, novel_comps), flush=True)
    print("  TIER-2 PASS (genuine substrate-internal novel composition)=%s" % tier2_pass, flush=True)
    return {"macc": macc, "equiv_max": eqv, "single_closers": single_closers, "comp_closers": comp_closers,
            "novel_comps": novel_comps, "gate_a": gate_a, "gate_b": gate_b, "tier2_pass": tier2_pass}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("single closers=%s (must be EMPTY for gate a); comp closers=%s; novel (not-equiv) comps=%s; equiv-max=%s." % (
        r["single_closers"], r["comp_closers"], r["novel_comps"], {k: round(v, 3) for k, v in r["equiv_max"].items()}))
    if r["tier2_pass"]:
        return ("HARD_PASS", "TIER-2 GENUINE SUBSTRATE-INTERNAL NOVEL COMPOSITION: on a generalization-split gap that NO single existing operator closes (full basis incl ghrr -- symmetric ops fail c-sensitivity; asymmetric ops fail to generalize across the held-out a-b swap), the loop assembled a composition (%s) that CLOSES it AND is NOT extensionally-equivalent to any single operator (equivalence-check gate b PASSED -- the gate ASSEMBLY-1 was missing). This is real novelty SHORT of novel-primitive: a genuinely-new COMPOSITE capability, no external truth required. " % r["novel_comps"] + s)
    if not r["gate_a"]:
        return ("HARD_FAIL", "Gate a FAILS: a single existing operator closes the generalization split -> not a no-existing-filler gap (the over-distinguishing pitfall, or the symmetry split was insufficient). Not tier-2 novelty. " + s)
    if not r["gate_b"]:
        return ("HARD_FAIL", "Gate b FAILS: the closing composition IS extensionally-equivalent to a single operator (rediscovery, like ASSEMBLY-1's perm-o-xor==ghrr). Not tier-2 novelty. " + s)
    return ("PARTIAL", "No composition closes the gap either -- combine over this vocabulary cannot reach it; widen vocabulary. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_novel_assembly_2_tier2 | N=%d V=%d triples=%d reps=%d EQUIV_TAU=%.2f" % (N_DIM, V_C, N_TRIPLES, REPS, EQUIV_TAU), flush=True)
    out_dir = get_output_dir("substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
