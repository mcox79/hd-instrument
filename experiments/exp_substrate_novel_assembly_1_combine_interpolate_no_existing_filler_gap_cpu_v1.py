"""Phase C DECISIVE genuine-novelty test (Skunkworks gate-c boundary) -- CELL-NOVEL-ASSEMBLY-1. F1+F3 validated the ABDUCTION half but both abduced shapes matched an EXISTING operator (gap-driven RETRIEVAL). The decisive test of INVENT-vs-RETRIEVE: a gap whose abduced shape has NO single existing-primitive filler -> forcing the COMBINE/INTERPOLATE assembly of a NEW filler from corpus parts (the user's distinctive idea) -> certify by gap-closure. Substrate-internal; NO LLM; no held-out (synthetic). CPU/numpy. ASCII; --self-test.

THE GAP (constructed so no single primitive closes it): ORDER-SENSITIVE conjunctive binding. Every context pair (a,b) has a reversed twin (b,a) with a CONFLICTING target. To predict, the context key must be (i) conjunctive/pair-separable AND (ii) order-sensitive (distinguish (a,b) from (b,a)). NO single existing primitive has both: xor/conv/bundle are COMMUTATIVE (collapse the twins -> <=50pct on conflict pairs); permutation alone is NOT conjunctive. The closing filler must be ASSEMBLED: bind(permute(a), b).

THE LOOP (genuine, not hand-supplied -- the combine-search discovers the assembly):
  1. ABDUCE the shape from closers-vs-failers: {conjunctive_pairsep + order_sensitive}.
  2. SEARCH single existing primitives -> NONE satisfies the shape AND closes (retrieval FAILS -> novelty required).
  3. COMBINE: enumerate assemblies bind(unary(prev), cur) over vocab unary in {id, perm, perm2} x bind in {xor, conv} -> find which satisfies the abduced shape AND closes. The DATA picks the assembly; I supply the vocabulary + composition operator, not the answer (CONSTRUCT-1 discipline).
  4. CERTIFY by gap-closure: the assembled op closes the task; single primitives do not.
HARD-PASS: (a) NO single existing primitive closes the gap, (b) an ASSEMBLED (composed) operator closes it, (c) the assembly is the one satisfying the abduced {conjunctive + order-sensitive} shape -> genuine COMBINE/INTERPOLATE novel-filler assembly certified by gap-closure. HARD-FAIL: a single primitive closes it (retrieval suffices -> not a novelty gap) OR no assembly closes it.
HONEST FRAME: this is COMPOSITIONAL novelty (assemble a new operator from existing primitives) -- the user's combine/interpolate idea -- NOT ex-nihilo primitive invention (5b-ii; needs external truth). Claim precisely."""
from __future__ import annotations
import sys, time, math
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

N_DIM = 4096
V_C = 128
N_PAIRS = 300          # base unordered pairs; each contributes BOTH (a,b) and (b,a) with conflicting targets
REPS = 40              # instances per ordered pair
GAP_BAR = 0.85         # close = >= 85pct (commutative binders cap ~0.5 on all-conflict pairs)
PROPS = ["conjunctive_pairsep", "order_sensitive", "recoverable"]
SELFTEST = "--self-test" in sys.argv


def _bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _nr(K): return K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)


# ---- operator vocabulary: unary transforms (on the FIRST operand) x binders ----
def _perm_idx(n, g, k):
    p = np.arange(n)
    for _ in range(k): p = g.permutation(p)
    return p


def _selftest():
    g = np.random.default_rng(0); C = _bp(8, 64, g)
    assert C.shape == (8, 64); print("[selftest] PASS", flush=True)


if __name__ == "__main__" and SELFTEST:
    _selftest(); sys.exit(0)


def run() -> Dict:
    out = {}
    accs = {}; props_ref = None
    # candidate names: singles + assemblies (unary o bind). 'id' unary on xor/conv == the plain single primitive.
    BIND = ["xor", "conv", "bundle"]
    # singles MUST include order-sensitive existing binders (Skunkworks vet): ghrr = circular CORRELATION (non-commutative
    # HRR-family bind, the analog of math::T3/ghrr_noncommutative_bind). Excluding it was the incomplete-control artifact.
    singles = ["xor", "conv", "bundle", "ghrr"]                     # atomic single binders (xor/conv/bundle commutative; ghrr NON-commutative)
    assemblies = ["%s_%s" % (u, b) for u in ("perm", "perm2") for b in BIND]  # genuine compositions unary o binder
    names = singles + assemblies
    for nm in names: accs[nm] = []

    for seed in [7, 17, 23]:
        g = np.random.default_rng(seed); n = N_DIM
        C = _bp(V_C, n, g) * math.sqrt(n); Cn = C / math.sqrt(n)
        P1 = _perm_idx(n, g, 1); P2 = _perm_idx(n, g, 2)

        # build ORDER-SENSITIVE dataset: each base pair -> (a,b)->t_ab and (b,a)->t_ba (conflicting)
        pairs = []; targets = []
        for _ in range(N_PAIRS):
            a, b = int(g.integers(0, V_C)), int(g.integers(0, V_C))
            if a == b: b = (b + 1) % V_C
            t_ab, t_ba = int(g.integers(0, V_C)), int(g.integers(0, V_C))
            pairs.append((a, b)); targets.append(t_ab)
            pairs.append((b, a)); targets.append(t_ba)
        pairs = np.array(pairs); targets = np.array(targets)
        # instances
        idx = np.repeat(np.arange(len(pairs)), REPS); g.shuffle(idx)
        split = int(0.8 * len(idx)); tr, te = idx[:split], idx[split:]

        def unary(name, X):
            if name == "id": return X
            if name == "perm": return X[:, P1]
            if name == "perm2": return X[:, P2]
            raise ValueError(name)

        def bind(name, A, B):
            if name == "xor": return _nr(A * B)
            if name == "conv": return _nr(np.fft.irfft(np.fft.rfft(A) * np.fft.rfft(B), n=n, axis=1).astype(np.float32))
            if name == "bundle": return _nr(A + B)
            raise ValueError(name)

        def keyfn(nm, prev, cur):
            Pv, Cu = Cn[prev], Cn[cur]
            if nm == "ghrr":                                        # circular CORRELATION = non-commutative HRR bind (order-sensitive single)
                return _nr(np.fft.irfft(np.conj(np.fft.rfft(Pv)) * np.fft.rfft(Cu), n=n, axis=1).astype(np.float32))
            if "_" in nm:                                            # assembly '<unary>_<bind>'
                u, b = nm.split("_"); return bind(b, unary(u, Pv), Cu)
            return bind(nm, Pv, Cu)                                  # single binder

        for nm in names:
            ptr = pairs[tr]; pte = pairs[te]                         # per-instance ordered pairs
            ktr = keyfn(nm, ptr[:, 0], ptr[:, 1]); kte = keyfn(nm, pte[:, 0], pte[:, 1])
            W = (Cn[targets[tr]].T @ ktr).astype(np.float32)
            preds = (kte @ W.T @ C.T).argmax(1)
            accs[nm].append(float(np.mean(preds == targets[te])))

        if props_ref is None:
            # measure properties per candidate (conjunctive_pairsep, order_sensitive, recoverable)
            ridx = g.integers(0, V_C, size=(300, 2)); ridx[ridx[:, 0] == ridx[:, 1], 1] += 1; ridx %= V_C
            props_ref = {}
            for nm in names:
                kab = keyfn(nm, ridx[:, 0], ridx[:, 1]); kba = keyfn(nm, ridx[:, 1], ridx[:, 0])
                S = kab @ kab.T; off = S[~np.eye(len(S), dtype=bool)]
                conj = float(np.mean(np.abs(off))) < 0.30
                order_sens = float(np.mean(np.sum(kab * kba, axis=1))) < 0.90
                # recoverable: can recover 'cur' given key + transformed-prev (xor: *; conv: corr; sums: subtract)
                if nm == "ghrr":                                    # recover cur from corr-key & prev: conv(key, prev)
                    inv = _nr(np.fft.irfft(np.fft.rfft(kab) * np.fft.rfft(Cn[ridx[:, 0]]), n=n, axis=1).astype(np.float32))
                else:
                    u = nm.split("_")[0] if "_" in nm else "id"; b = nm.split("_")[1] if "_" in nm else nm
                    up = unary(u, Cn[ridx[:, 0]])                    # transformed first operand
                    if b == "xor": inv = _nr(kab * up)
                    elif b == "conv": inv = _nr(np.fft.irfft(np.fft.rfft(kab) * np.conj(np.fft.rfft(up)), n=n, axis=1).astype(np.float32))
                    elif b == "bundle": inv = _nr(kab - up)
                    else: inv = None
                rec = 0.0 if inv is None else float(np.mean((inv @ Cn.T).argmax(1) == ridx[:, 1]))
                props_ref[nm] = {"conjunctive_pairsep": conj, "order_sensitive": order_sens, "recoverable": rec >= 0.5}

    macc = {nm: float(np.mean(accs[nm])) for nm in names}
    closers = {nm for nm in names if macc[nm] >= GAP_BAR}
    single_closers = closers & set(singles)
    assembly_closers = closers & set(assemblies)
    failers = set(names) - closers

    # ABDUCE the MISSING property: what the closers have that ALL existing SINGLE primitives LACK (the gap-shape that
    # drives the combine-search -- the property no retrievable single filler provides).
    missing = [p for p in PROPS if (closers and all(props_ref[c][p] for c in closers)) and all(not props_ref[s][p] for s in singles)]
    # genuine-novelty (structural): NO single primitive closes; an assembly does; the closing assembly supplies the
    # abduced MISSING property (added via composition). perm o binder ADDS order_sensitivity that no single binder has.
    novelty = (len(single_closers) == 0) and (len(assembly_closers) >= 1)
    assembly_supplies_missing = bool(missing) and all(all(props_ref[a][p] for p in missing) for a in assembly_closers)
    hard_pass = novelty and bool(missing) and assembly_supplies_missing
    abduced = missing; disc = bool(missing)

    print("  CELL-NOVEL-ASSEMBLY-1 (combine/interpolate on a NO-single-existing-filler gap; certify by gap-closure):", flush=True)
    print("  order-sensitive conjunctive-binding task (every pair has a reversed conflicting twin); close bar=%.2f" % GAP_BAR, flush=True)
    for nm in names:
        kind = "SINGLE  " if nm in singles else "ASSEMBLY"
        print("    %-10s [%s] acc=%.3f props=%s %s" % (nm, kind, macc[nm],
              "".join("1" if props_ref[nm][p] else "0" for p in PROPS), "CLOSES" if nm in closers else "fails"), flush=True)
    print("  props order: %s" % "/".join(PROPS), flush=True)
    print("  single-primitive closers=%s | assembly closers=%s" % (sorted(single_closers), sorted(assembly_closers)), flush=True)
    print("  ABDUCED missing-property (closers have, ALL singles lack)=%s | NO single closes=%s | assembly supplies missing=%s" % (
        missing, len(single_closers) == 0, assembly_supplies_missing), flush=True)
    print("  HARD-PASS (genuine combine/interpolate novel-filler assembly)=%s" % hard_pass, flush=True)
    return {"macc": macc, "closers": sorted(closers), "single_closers": sorted(single_closers),
            "assembly_closers": sorted(assembly_closers), "props": props_ref, "abduced": abduced, "disc": disc,
            "assembly_supplies_missing": assembly_supplies_missing, "novelty": novelty, "hard_pass": hard_pass}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = ("order-sensitive conjunctive-binding gap: single-primitive closers=%s (must be EMPTY); assembly closers=%s; abduced MISSING-property=%s; assembly supplies it=%s." % (
        r["single_closers"], r["assembly_closers"], r["abduced"], r["assembly_supplies_missing"]))
    if r["hard_pass"]:
        return ("HARD_PASS", "GENUINE COMBINE/INTERPOLATE NOVEL-FILLER ASSEMBLY: NO single existing primitive (xor/conv/bundle, all commutative) closes the order-sensitive gap; the abduced MISSING property the closing filler needs and that NO single binder supplies is %s; the loop ASSEMBLED a new filler (permute o binder) from corpus parts via combine-search that SUPPLIES that property and CLOSED the gap -- certified by gap-closure. This is the INVENT (not just RETRIEVE) step Skunkworks flagged as untested. HONEST: COMPOSITIONAL novelty (new operator composed from existing primitives = the user's combine/interpolate idea), NOT ex-nihilo primitive invention (5b-ii; needs external truth). " % r["abduced"] + s)
    if r["single_closers"]:
        return ("HARD_FAIL", "NOVELTY CLAIM REJECTED (Skunkworks vet CONFIRMED by this corrected control): a SINGLE EXISTING binder closes the gap (%s -- ghrr = non-commutative correlation, the HRR-family order-sensitive binder excluded from the original control). So 'no single existing closes' was an artifact of testing only commutative binders; the assembled perm-o-xor was COMPOSITIONAL REDISCOVERY of an existing capability (order-sensitive binding), NOT invention. The combine/interpolate MECHANISM is valid (it does assemble order-sensitive closers), but genuine novelty is NOT demonstrated -- the decisive test needs a gap unclosable by the FULL existing operator set. Same rediscovery trap as CELL-INV-1/banach/130a-G2, correctly caught at the decisive moment. " % r["single_closers"] + s)
    if not r["assembly_closers"]:
        return ("HARD_FAIL", "No assembled operator closes the gap either -> combine/interpolate over this vocabulary cannot reach the shape; widen the primitive vocabulary or the composition operator. " + s)
    return ("PARTIAL", "Assembly closes but abduced shape/discrimination weak -- inspect property space. " + s)


if __name__ == "__main__":
    _selftest()
    print("[config] anchor=substrate_novel_assembly_1_combine_interpolate | N=%d V=%d pairs=%d reps=%d" % (N_DIM, V_C, N_PAIRS, REPS), flush=True)
    out_dir = get_output_dir("substrate_novel_assembly_1_combine_interpolate_no_existing_filler_gap_cpu_v1"); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": "substrate_novel_assembly_1_combine_interpolate_no_existing_filler_gap_cpu_v1", "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": "full", "n_seeds": 3, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
