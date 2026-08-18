"""Post-hoc diagnostic on the LANDED exp_typed_role_context_write_rule_dissociation_v1 result.

Question: does U3_ROLE_ONLY (64-dim (relation, direction) count profile, cosine) measure
SUBSTITUTABILITY, or does it only measure "these two words are not complementary parts of the
same construction"?

Method: reconstruct the U1/U3 context profiles from the cell's own persisted arc_events in
data/exp_typed_role_context_write_rule_dissociation_v1/units.jsonl (READ ONLY; no cell is run,
no experiment file is touched), reproduce the landed AUCs as a fidelity check, then add the
control the cell does not have: a third set R of RANDOM same-population noun pairs with zero
co-occurrence, which are neither WordNet synonyms (SET_P) nor high-co-occurrence collocates
(SET_S).

Decisive contrast:
  AUC(P vs S)  -- the landed number (synonyms above collocates)
  AUC(R vs S)  -- random pairs above collocates. If ~= AUC(P vs S), the arm knows nothing
                  about synonymy; it only detects "not a collocate".
  AUC(P vs R)  -- synonyms above random pairs. If ~= 0.5, no substitutability information.

Usage: .venv/Scripts/python.exe tools/diagnose_role_profile_is_category_detector.py
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import math
import random
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPED = os.path.join(REPO, "data", "exp_typed_role_context_write_rule_dissociation_v1", "units.jsonl")
INSTR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1", "units.jsonl")
POP_KEY = "POPULATION|v1.7|full"
SEED = 20260818
N_BOOT = 2000


def load_population():
    with open(INSTR, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["unit_key"] == POP_KEY:
                r = d["result"]
                return r["matchedP"], r["matchedS"]
    raise RuntimeError("population not found")


def load_profiles():
    """word -> (typed Counter over (nbr,rel,dir), role Counter over (rel,dir), bag Counter, n_occ)."""
    typed, role, bag, nocc = {}, {}, {}, {}
    with open(TYPED, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            k = d["unit_key"]
            if not k.startswith("OCC|"):
                continue
            w = k.split("|")[-1]
            t, ro, bg = Counter(), Counter(), Counter()
            occs = d["result"]["occurrences"]
            for o in occs:
                for ev in o.get("arc_events", []):
                    nbr, rel, direction = ev[0], ev[1], ev[2]
                    t[(nbr, rel, direction)] += 1
                    ro[(rel, direction)] += 1
                for c, n in o.get("bag_counts", {}).items():
                    bg[c] += n
            typed[w], role[w], bag[w], nocc[w] = t, ro, bg, len(occs)
    return typed, role, bag, nocc


def cos(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    keys = a.keys() & b.keys()
    num = sum(a[k] * b[k] for k in keys)
    if num == 0:
        return 0.0
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return num / (na * nb)


def auc_and_ci(pos, neg, rng):
    """rank-sum AUC that pos > neg, with a paired bootstrap CI over pairs."""
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)

    def _auc(p, n):
        allv = np.concatenate([p, n])
        order = allv.argsort()
        ranks = np.empty(len(allv), dtype=float)
        ranks[order] = np.arange(1, len(allv) + 1)
        # average ranks for ties
        i = 0
        srt = allv[order]
        while i < len(srt):
            j = i
            while j + 1 < len(srt) and srt[j + 1] == srt[i]:
                j += 1
            if j > i:
                ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
            i = j + 1
        rp = ranks[: len(p)].sum()
        return (rp - len(p) * (len(p) + 1) / 2.0) / (len(p) * len(n))

    point = _auc(pos, neg)
    boots = []
    for _ in range(N_BOOT):
        p = pos[rng.integers(0, len(pos), len(pos))]
        n = neg[rng.integers(0, len(neg), len(neg))]
        boots.append(_auc(p, n))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return round(point, 4), [round(lo, 4), round(hi, 4)]


def score_pairs(pairs, prof):
    out = []
    for a, b in pairs:
        if a in prof and b in prof:
            out.append(cos(prof[a], prof[b]))
    return out


def main():
    rng = np.random.default_rng(SEED)
    pyrng = random.Random(SEED)

    matchedP, matchedS = load_population()
    P = [tuple(p[:2]) if isinstance(p, (list, tuple)) else (p["w1"], p["w2"]) for p in matchedP]
    S = [tuple(p[:2]) if isinstance(p, (list, tuple)) else (p["w1"], p["w2"]) for p in matchedS]
    print(f"population: |P|={len(P)} |S|={len(S)}  example P={P[0]} S={S[0]}")

    typed, role, bag, nocc = load_profiles()
    print(f"profiles: {len(typed)} words; typed vocab={len(set().union(*[set(v) for v in typed.values()]))} "
          f"role vocab={len(set().union(*[set(v) for v in role.values()]))}")

    # ---- fidelity check: reproduce the landed AUCs ----
    for name, prof in (("U1_TYPED_CONTEXT", typed), ("U3_ROLE_ONLY", role)):
        a, ci = auc_and_ci(score_pairs(P, prof), score_pairs(S, prof), rng)
        print(f"FIDELITY {name}: AUC(P>S)={a} ci={ci}")

    # ---- the missing control: SET_R, random same-population pairs, zero co-occurrence ----
    words = sorted({w for p in P for w in p} | {w for p in S for w in p})
    words = [w for w in words if w in role and sum(role[w].values()) > 0]
    banned = {frozenset(p) for p in P} | {frozenset(p) for p in S}

    def cooccur(a, b):
        return bag.get(a, Counter()).get(b, 0) + bag.get(b, Counter()).get(a, 0)

    R = []
    tries = 0
    while len(R) < len(P) and tries < 400000:
        tries += 1
        a, b = pyrng.sample(words, 2)
        if frozenset((a, b)) in banned:
            continue
        if cooccur(a, b) > 0:
            continue
        banned.add(frozenset((a, b)))
        R.append((a, b))
    print(f"SET_R: {len(R)} random zero-co-occurrence non-P non-S pairs (tries={tries})")

    for name, prof in (("U1_TYPED_CONTEXT", typed), ("U3_ROLE_ONLY", role)):
        pS = score_pairs(P, prof)
        sS = score_pairs(S, prof)
        rS = score_pairs(R, prof)
        a1, c1 = auc_and_ci(pS, sS, rng)
        a2, c2 = auc_and_ci(rS, sS, rng)
        a3, c3 = auc_and_ci(pS, rS, rng)
        print(f"\n{name}")
        print(f"  AUC(P > S) = {a1} {c1}   [the landed claim: synonyms above collocates]")
        print(f"  AUC(R > S) = {a2} {c2}   [random pairs above collocates -- if ~= above, no synonymy]")
        print(f"  AUC(P > R) = {a3} {c3}   [synonyms above random pairs -- the substitutability test]")
        print(f"  mean cos: P={np.mean(pS):.4f} S={np.mean(sS):.4f} R={np.mean(rS):.4f}")

    # ---- R2: frequency-matched random control (profile mass drives cosine reliability) ----
    mass = {w: sum(role[w].values()) for w in words}
    by_mass = sorted(words, key=lambda w: mass[w])
    rank = {w: i for i, w in enumerate(by_mass)}
    banned2 = {frozenset(p) for p in P} | {frozenset(p) for p in S}
    R2 = []
    WIN = 40
    for (a, b) in P:
        if a not in rank or b not in rank:
            continue
        got = None
        for _ in range(3000):
            ca = by_mass[max(0, min(len(by_mass) - 1, rank[a] + pyrng.randint(-WIN, WIN)))]
            cb = by_mass[max(0, min(len(by_mass) - 1, rank[b] + pyrng.randint(-WIN, WIN)))]
            if ca == cb or frozenset((ca, cb)) in banned2 or cooccur(ca, cb) > 0:
                continue
            got = (ca, cb)
            break
        if got:
            banned2.add(frozenset(got))
            R2.append(got)
    print(f"\nSET_R2 (mass-rank-matched to P, +/-{WIN} ranks): {len(R2)} pairs")
    pm = np.array([mass[a] + mass[b] for a, b in P if a in mass and b in mass], dtype=float)
    r2m = np.array([mass[a] + mass[b] for a, b in R2], dtype=float)
    rm = np.array([mass[a] + mass[b] for a, b in R], dtype=float)
    print(f"  median pair arc-mass: P={np.median(pm):.0f} R={np.median(rm):.0f} R2={np.median(r2m):.0f}")
    for name, prof in (("U1_TYPED_CONTEXT", typed), ("U3_ROLE_ONLY", role)):
        a4, c4 = auc_and_ci(score_pairs(P, prof), score_pairs(R2, prof), rng)
        print(f"  {name}: AUC(P > R2_freqmatched) = {a4} {c4}")

    # frequency floor on the P-vs-R2 comparison, recomputed on this population
    def freqsim(pairs):
        return [-abs(math.log(mass[a] + 1) - math.log(mass[b] + 1)) for a, b in pairs if a in mass and b in mass]

    def massmin(pairs):
        return [math.log(min(mass[a], mass[b]) + 1) for a, b in pairs if a in mass and b in mass]

    for fname, fn in (("F_FREQ_SIM", freqsim), ("F_FREQ_MIN", massmin)):
        a5, c5 = auc_and_ci(fn(P), fn(R2), rng)
        a6, c6 = auc_and_ci(fn(P), fn(S), rng)
        print(f"  floor {fname}: AUC(P>R2)={a5} {c5}   AUC(P>S)={a6} {c6}")

    # ---- the floor the cell did not run: MIN-ATTESTATION, on BOTH mass definitions ----
    print("\nFLOOR THE CELL DID NOT RUN -- min-attestation of the weaker partner:")
    for label, tbl in (("arc_mass", mass), ("bag_occurrences", nocc)):
        def fmin(pairs, t=tbl):
            return [math.log(min(t.get(a, 0), t.get(b, 0)) + 1) for a, b in pairs if a in t and b in t]

        def fsim(pairs, t=tbl):
            return [-abs(math.log(t.get(a, 0) + 1) - math.log(t.get(b, 0) + 1)) for a, b in pairs if a in t and b in t]

        am, cm = auc_and_ci(fmin(P), fmin(S), rng)
        asi, csi = auc_and_ci(fsim(P), fsim(S), rng)
        print(f"  [{label}] F_MIN_ATTESTATION AUC(P>S) = {am} {cm} ; F_ATTEST_SIM AUC(P>S) = {asi} {csi}")

    # ---- decisive: mass-matched P vs S subsample ----
    def key(w):
        return (math.log(mass.get(w, 0) + 1), math.log(nocc.get(w, 0) + 1))

    used = set()
    mP, mS = [], []
    TOL = 0.35
    for (sa, sb) in S:
        if sa not in mass or sb not in mass:
            continue
        s_lo, s_hi = sorted([key(sa)[0], key(sb)[0]])
        best, bestd = None, 1e9
        for i, (pa, pb) in enumerate(P):
            if i in used or pa not in mass or pb not in mass:
                continue
            p_lo, p_hi = sorted([key(pa)[0], key(pb)[0]])
            d = abs(p_lo - s_lo) + abs(p_hi - s_hi)
            if d < bestd:
                best, bestd = i, d
        if best is not None and bestd <= TOL:
            used.add(best)
            mP.append(P[best])
            mS.append((sa, sb))
    print(f"\nMASS-MATCHED SUBSAMPLE (|log-mass| tolerance {TOL} summed over both ranks): n={len(mP)} pairs each")
    if mP:
        fm = lambda prs: [math.log(min(mass[a], mass[b]) + 1) for a, b in prs]
        a0, c0 = auc_and_ci(fm(mP), fm(mS), rng)
        print(f"  residual F_MIN_ATTESTATION on the matched subsample = {a0} {c0}  (should be ~0.50)")
        for name, prof in (("U1_TYPED_CONTEXT", typed), ("U3_ROLE_ONLY", role), ("T2_UNTYPED", None)):
            pr = prof if prof is not None else bag
            a7, c7 = auc_and_ci(score_pairs(mP, pr), score_pairs(mS, pr), rng)
            print(f"  {name}: AUC(P>S | mass-matched) = {a7} {c7}")

    # ---- which corruption model reproduces the cell's N6 tolerance (0.6669 -> 0.6507 at p=0.50)? ----
    print("\nCORRUPTION MODELS on the reconstructed U1 profile (what does 'corrupt an arc' mean?):")
    raw = {}
    with open(TYPED, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if not d["unit_key"].startswith("OCC|"):
                continue
            w = d["unit_key"].split("|")[-1]
            evs = []
            for o in d["result"]["occurrences"]:
                evs.extend([tuple(e) for e in o.get("arc_events", [])])
            raw[w] = evs
    all_labels = [(rel, dr) for evs in raw.values() for (_, rel, dr) in evs]
    all_nbrs = [n for evs in raw.values() for (n, _, _) in evs]

    for model in ("LABEL_ONLY", "ATTACHMENT_ONLY", "BOTH"):
        for p in (0.25, 0.50):
            rr = random.Random(SEED + 7)
            tprof, rprof = {}, {}
            for w, evs in raw.items():
                t, ro = Counter(), Counter()
                for (nbr, rel, dr) in evs:
                    if rr.random() < p:
                        if model in ("LABEL_ONLY", "BOTH"):
                            rel, dr = rr.choice(all_labels)
                        if model in ("ATTACHMENT_ONLY", "BOTH"):
                            nbr = rr.choice(all_nbrs)
                    t[(nbr, rel, dr)] += 1
                    ro[(rel, dr)] += 1
                tprof[w], rprof[w] = t, ro
            a8, _ = auc_and_ci(score_pairs(P, tprof), score_pairs(S, tprof), rng)
            a9, _ = auc_and_ci(score_pairs(P, rprof), score_pairs(S, rprof), rng)
            print(f"  {model:16s} p={p:.2f}: U1={a8}  U3={a9}   (cell reports U1 p=0.25 -> 0.6603, p=0.50 -> 0.6507)")

    # ---- HOW COARSE? truncate the role profile to its top-k bins ----
    print("\nTRUNCATING THE 64-BIN ROLE PROFILE TO ITS TOP-k BINS (P vs S, and P vs R2):")
    for k in (1, 2, 3, 5, 8, 16, 64):
        trunc = {w: Counter(dict(c.most_common(k))) for w, c in role.items()}
        a10, c10 = auc_and_ci(score_pairs(P, trunc), score_pairs(S, trunc), rng)
        a11, _ = auc_and_ci(score_pairs(P, trunc), score_pairs(R2, trunc), rng)
        print(f"  top-{k:2d}: AUC(P>S)={a10} {c10}   AUC(P>R2)={a11}")
    # binary presence (counts discarded entirely)
    binp = {w: Counter({kk: 1 for kk in c}) for w, c in role.items()}
    a12, c12 = auc_and_ci(score_pairs(P, binp), score_pairs(S, binp), rng)
    a13, _ = auc_and_ci(score_pairs(P, binp), score_pairs(R2, binp), rng)
    print(f"  binary-presence (counts discarded): AUC(P>S)={a12} {c12}  AUC(P>R2)={a13}")

    # ---- what the role profile actually encodes: head-vs-dependent asymmetry ----
    def direction_share(w):
        c = role[w]
        tot = sum(c.values())
        if tot == 0:
            return None
        up = sum(v for (rel, d), v in c.items() if d == "up")
        return up / tot

    def dir_gap(pairs):
        g = []
        for a, b in pairs:
            da, db = direction_share(a) if a in role else None, direction_share(b) if b in role else None
            if da is not None and db is not None:
                g.append(abs(da - db))
        return float(np.mean(g)), len(g)

    print("\nHEAD/DEPENDENT ASYMMETRY (mean |head-share(a) - head-share(b)|):")
    for nm, pr in (("P", P), ("S", S), ("R", R)):
        m, n = dir_gap(pr)
        print(f"  {nm}: {m:.4f}  (n={n})")

    # ---- how concentrated is the role profile? ----
    tots = [sum(role[w].values()) for w in words]
    dis = [len(role[w]) for w in words]
    print(f"\nrole profile: median distinct (rel,dir) per word = {np.median(dis):.0f}; "
          f"median arc count = {np.median(tots):.0f}")


if __name__ == "__main__":
    main()
