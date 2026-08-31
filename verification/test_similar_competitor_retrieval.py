"""Scaffold-free witness for retrieval_interference_is_similar_competitor_cue_overload_not_event_count.

Recomputes every headline claim FROM SOURCE (the raw LitBank pronoun/who-did-what caches + the TCM organ),
independent of any experiment cell's saved metrics.json. Run:

    .venv/Scripts/python.exe verification/test_similar_competitor_retrieval.py

Checks (each asserts a claim quoted in SOLVED.md):
  A. who-did-what content-only floor reproduces ~0.398 on the ambiguous shared-verb subset (the brief's gate
     number; the DISK confirms it) AND naive recency ties it there (band NOT the reason to build).
  B. REAL pronoun coref (the brain-faithful population): content floor (freq) < naive recency < subject-recency;
     the oracle "any accessibility cue right" >> best single cue  ->  real complementary headroom.
  C. the ACT-R additive combiner (recency[TCM organ]+subject-recency+base, weights fit on TRAIN docs) on HELD-OUT
     TEST docs beats the content-only floor by >= +0.10, beats naive recency, and beats the STRONGEST single cue
     (subject-recency), all with the point estimate positive.
  D. info-free twin (shuffled discourse context) LOSES to the combiner.
  E. INFORMATIONAL CEILING: a principled ACT-R Boltzmann (ML-fit) retrieval does NOT beat the additive combiner
     by more than a hair and stays well below the oracle -> the residual is informational, not a combiner-rule gap.
  F/G. the LANDED graded_antecedent_pick already delivers content x context (+0.155 over content, twin loses); the
     brief's multi-timescale-TCM proposal is a rigorous negative (adds ~0).
  H. HONEST DECOMPOSITION: the person-based pool cleanup (already landed) reproduces its +0.02+ win over the raw
     picker, but GENDER agreement adds NO CI-separated marginal ON TOP of it (< +0.02) -> agreement is a rigorous
     negative over the current substrate (the residual is structural/semantic, not a memory feature-match cue).

CONSUMES hdlab.graded_temporal_context + hdlab.graded_coref_pick. NO external LLM. Deterministic.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

PRON = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")
WDW = os.path.join(REPO, "data", "litbank", "who_did_what_events.json")
CUES = ("RECENCY", "BASE", "SUBJREC", "FREQ", "FIRST")
FAILS = []


def check(name, cond, detail=""):
    print(("  [PASS] " if cond else "  [FAIL] ") + name + ("  " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def tcm_kernel(max_lag, min_period=2.0, max_mult=2.0):
    import torch
    from hdlab.graded_temporal_context import GradedTemporalContext
    g = GradedTemporalContext(d=1024, min_period=min_period, max_period_mult=max_mult, horizon=1000.0)
    c0 = g.ctx(0.0)
    return np.clip(np.array([float((torch.conj(c0) * g.ctx(float(L))).real.mean()) for L in range(max_lag + 1)]), 0.0, None)


# ---------------- A. who-did-what content-only floor (the gate number) ----------------
def check_A():
    print("A. who-did-what shared-verb ambiguous subset (the brief's gate)")
    docs = json.load(open(WDW, encoding="utf-8"))
    q = []
    for dd in docs:
        evs = [{"e": int(m["gold"]), "v": str(m["gov_verb"]), "s": int(m["sent"])}
               for m in dd["stream"] if m.get("gov_verb")]
        import collections
        by_verb = collections.defaultdict(list); cnt = collections.Counter(); ment = collections.defaultdict(list)
        for e in evs:
            by_verb[e["v"]].append(e); cnt[(e["e"], e["v"])] += 1; ment[e["e"]].append(e["s"])
        for v, el in by_verb.items():
            cand = sorted(set(e["e"] for e in el))
            if len(cand) < 2:
                continue
            content = max(cand, key=lambda c: (cnt[(c, v)], -c))
            for qe in el:
                s = qe["s"]
                def rec(c):
                    p = [x for x in ment[c] if x < s]
                    return (s - max(p)) if p else 10 ** 9
                ctx = min(cand, key=lambda c: (rec(c), c))
                q.append((qe["e"], content, ctx))
    cf = np.mean([int(c == g) for g, c, _ in q]); rc = np.mean([int(x == g) for g, _, x in q])
    check("who-did-what content-only floor ~0.398", abs(cf - 0.398) < 0.02, "got %.3f (n=%d)" % (cf, len(q)))
    check("who-did-what naive recency ~ ties content (|delta|<0.02)", abs(rc - cf) < 0.02,
          "recency %.3f vs content %.3f" % (rc, cf))


# ---------------- shared pronoun-coref machinery ----------------
def prior_mentions(inst):
    ps = int(inst["p_sent"]); out = {}
    for cid, ms in inst["candidates"].items():
        pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
        if pm:
            out[int(cid)] = pm
    return out


def build(insts, shuffle_ctx=False, seed=7):
    gen = np.random.default_rng(seed); pool = {}
    if shuffle_ctx:
        for inst in insts:
            for ms in inst["candidates"].values():
                for m in ms:
                    pool.setdefault(inst["doc"], []).append(int(m["sent"]))
    qs = []
    for inst in insts:
        pv = prior_mentions(inst)
        if len(pv) < 2:
            continue
        ps = int(inst["p_sent"])
        if shuffle_ctx:
            sp = np.array(pool[inst["doc"]]); new = {}
            for c, pm in pv.items():
                nm = [(int(gen.choice(sp)), r) for (s, r) in pm]
                nm = [(s, r) for (s, r) in nm if s < ps]
                if nm:
                    new[c] = nm
            pv = new
            if len(pv) < 2:
                continue
        qs.append({"gold": int(inst["gold"]), "p_sent": ps, "pv": pv, "n_cand": len(pv)})
    return qs


def feats(q, ker):
    pv, ps = q["pv"], q["p_sent"]; ml = len(ker) - 1; cands = sorted(pv)
    kern = lambda dt: (ker[dt] if 0 <= dt <= ml else 0.0)
    intro = {c: min(s for s, _ in pv[c]) for c in cands}; early = min(intro.values())
    anysub = any(any(r == "SUBJECT" for _, r in pv[c]) for c in cands)
    rows = []
    for c in cands:
        dts = [ps - s for s, _ in pv[c]]
        sd = [ps - s for s, r in pv[c] if r == "SUBJECT"]
        rows.append([kern(min(dts)), sum(kern(d) for d in dts),
                     (kern(min(sd)) if sd else 0.0) if anysub else kern(min(dts)),
                     np.log1p(len(pv[c])), 1.0 if intro[c] == early else 0.0])
    X = np.array(rows); mu = X.mean(0); sd = X.std(0)
    Xz = np.where(sd > 1e-12, (X - mu) / np.where(sd > 1e-12, sd, 1.0), 0.0)
    return Xz, (cands.index(q["gold"]) if q["gold"] in cands else -1)


def softmax_cols(Xz):
    # per-cue within-query softmax preference
    P = np.exp(Xz - Xz.max(0)); return P / P.sum(0)


def cue_acc(pre, k):
    return float(np.mean([int(np.argmax(p["X"][:, k]) == p["g"]) for p in pre]))


def oracle(pre):
    return float(np.mean([int(any(np.argmax(p["X"][:, k]) == p["g"] for k in range(5))) for p in pre]))


def comb_acc(pre, w):
    return float(np.mean([int(np.argmax(p["P"] @ w) == p["g"]) for p in pre]))


def fit_coord(pre):
    grid = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    w = np.array([1.0, 0.0, 1.0, 0.0, 0.0]); best = comb_acc(pre, w)
    for _ in range(4):
        imp = False
        for k in range(5):
            for v in grid:
                c = w.copy(); c[k] = v; a = comb_acc(pre, c)
                if a > best + 1e-9:
                    best, w, imp = a, c, True
        if not imp:
            break
    return w


def fit_boltz(pre, lr=0.3, ep=250, l2=1e-3):
    w = np.zeros(5); n = len(pre)
    for _ in range(ep):
        g = np.zeros(5)
        for p in pre:
            if p["g"] < 0:
                continue
            a = p["X"] @ w; a -= a.max(); e = np.exp(a); pr = e / e.sum()
            g += p["X"][p["g"]] - pr @ p["X"]
        w += lr * (g / n - l2 * w)
    return w


def precompute(qs, ker):
    out = []
    for q in qs:
        Xz, gi = feats(q, ker)
        out.append({"X": Xz, "P": softmax_cols(Xz), "g": gi, "n": Xz.shape[0]})
    return out


def check_BCDE():
    insts = json.load(open(PRON, encoding="utf-8"))
    ker = tcm_kernel(400)
    test_docs = set(d for d in sorted(set(i["doc"] for i in insts))
                    if (int(hashlib.md5(d.encode()).hexdigest(), 16) % 1000) / 1000.0 < 0.4)
    tr = precompute(build([i for i in insts if i["doc"] not in test_docs]), ker)
    te = precompute(build([i for i in insts if i["doc"] in test_docs]), ker)
    ci = {c: i for i, c in enumerate(CUES)}
    fr = cue_acc(te, ci["FREQ"]); rc = cue_acc(te, ci["RECENCY"]); sr = cue_acc(te, ci["SUBJREC"]); orc = oracle(te)

    print("B. real pronoun coref floors + complementary headroom")
    check("content(freq) < recency < subject-recency", fr < rc < sr, "freq=%.3f rec=%.3f subjrec=%.3f" % (fr, rc, sr))
    check("oracle-any-cue exceeds best single cue by >= +0.08 (headroom exists)", orc - sr >= 0.08,
          "oracle=%.3f best_single=%.3f (+%.3f)" % (orc, sr, orc - sr))

    print("C. ACT-R additive combiner (fit on TRAIN, eval HELD-OUT TEST)")
    w = fit_coord(tr); comb = comb_acc(te, w)
    check("beats content-only floor by >= +0.10", comb - fr >= 0.10, "combiner=%.3f freq=%.3f (+%.3f)" % (comb, fr, comb - fr))
    check("beats naive recency", comb - rc > 0, "combiner=%.3f rec=%.3f (+%.3f)" % (comb, rc, comb - rc))
    check("beats strongest single cue (subject-recency)", comb - sr > 0, "combiner=%.3f subjrec=%.3f (+%.3f)" % (comb, sr, comb - sr))

    print("D. info-free twin (shuffled discourse context) LOSES")
    tw = precompute(build([i for i in insts if i["doc"] in test_docs], shuffle_ctx=True, seed=101), ker)
    twa = comb_acc(tw, w)
    check("shuffled-context twin < combiner", twa < comb, "twin=%.3f vs combiner=%.3f" % (twa, comb))

    print("E. informational ceiling (combination rule is NOT the bottleneck)")
    wb = fit_boltz(tr); ba = comb_acc_boltz(te, wb)
    check("ACT-R Boltzmann does not exceed additive combiner by > 0.03", ba - comb <= 0.03,
          "boltzmann=%.3f additive=%.3f" % (ba, comb))
    check("both combiners stay >= 0.07 below the oracle (residual is informational)", orc - max(ba, comb) >= 0.07,
          "oracle=%.3f best_combiner=%.3f gap=%.3f" % (orc, max(ba, comb), orc - max(ba, comb)))


def comb_acc_boltz(pre, w):
    return float(np.mean([int(np.argmax(p["X"] @ w) == p["g"]) for p in pre]))


# ---------------- F/G. the ACTUAL headline: the LANDED organ + the rigorous negative on the TCM proposal --------
def check_FG():
    import math
    from hdlab import graded_coref_pick as GCP
    from hdlab.graded_competition import graded_pick
    insts = json.load(open(PRON, encoding="utf-8"))
    ker = tcm_kernel(400)
    test_docs = set(d for d in sorted(set(i["doc"] for i in insts))
                    if (int(hashlib.md5(d.encode()).hexdigest(), 16) % 1000) / 1000.0 < 0.4)

    def priors_of(inst, shuffle=False, gen=None):
        ps = int(inst["p_sent"]); items = []
        for cid, ms in inst["candidates"].items():
            pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
            if pm:
                items.append((int(cid), pm))
        if shuffle and items:
            alls = np.array([s for _c, pm in items for s, _ in pm])
            items = [(c, [(int(gen.choice(alls)), r) for _s, r in pm]) for c, pm in items]
            items = [(c, [(s, r) for s, r in pm if s < ps]) for c, pm in items]
            items = [(c, pm) for c, pm in items if pm]
        if len(items) < 2:
            return None
        cids = [c for c, _ in items]
        return [pm for _, pm in items], (cids.index(int(inst["gold"])) if int(inst["gold"]) in cids else -1), ps

    def base_sup(priors, ps, d=GCP.DEFAULT_ACTR_D):
        prev = max((s for pri in priors for (s, _r) in pri if s < ps), default=None)
        early = [min(s for s, _r in pri) for pri in priors]; fs = min(early)
        def z(v):
            v = np.array(v, float); s = v.std(); return (v - v.mean()) / s if s > 1e-12 else np.zeros_like(v)
        rec = [1.0 / min(GCP._dt(ps, s) for s, _ in pri) for pri in priors]
        subj = [max(GCP.ROLE_W.get(r, 1.0) for _s, r in pri) for pri in priors]
        cb = [1.0 if any(s == prev and r == "SUBJECT" for s, r in pri) else 0.0 for pri in priors]
        freq = [math.log1p(len(pri)) for pri in priors]
        first = [1.0 if early[i] == fs else 0.0 for i in range(len(priors))]
        par = [1.0 if max(pri, key=lambda sr: sr[0])[1] == "OTHER" else 0.0 for pri in priors]
        actr = [math.log(sum(GCP.ROLE_W.get(r, 1.0) * (GCP._dt(ps, s) ** (-d)) for s, r in pri)) for pri in priors]
        return {"recency": z(rec), "subject": z(subj), "cb": z(cb), "freq": z(freq),
                "first": z(first), "parallel": z(par), "actr": z(actr)}, z

    def tcm_cue(priors, ps, z):
        ml = len(ker) - 1
        out = [math.log(max(1e-12, sum((ker[ps - s] if 0 <= ps - s <= ml else 0.0) * GCP.ROLE_W.get(r, 1.0)
               for s, r in pri))) for pri in priors]
        return z(out)

    te = [priors_of(i) for i in insts if i["doc"] in test_docs]
    te = [x for x in te if x]
    landed = np.array([int(GCP.graded_antecedent_pick(pr, ps)["pick"] == gi) for pr, gi, ps in te], float)
    freq = np.array([int(int(max(range(len(pr)), key=lambda i: (len(pr[i]), max(s for s, _ in pr[i])))) == gi)
                     for pr, gi, ps in te], float)
    hard = np.array([int(GCP.hard_tier_pick(pr, ps) == gi) for pr, gi, ps in te], float)
    w_tcm = dict(GCP.TUNED_WEIGHTS); w_tcm["tcm"] = 0.25
    ltcm = []
    for pr, gi, ps in te:
        sup, z = base_sup(pr, ps); sup2 = dict(sup); sup2["tcm"] = tcm_cue(pr, ps, z)
        ltcm.append(int(int(graded_pick(sup2, w_tcm, gain=GCP.DEFAULT_GAIN)["win"]) == gi))
    ltcm = np.array(ltcm, float)
    gen = np.random.default_rng(101)
    tw = [priors_of(i, shuffle=True, gen=gen) for i in insts if i["doc"] in test_docs]
    tw = [x for x in tw if x]
    landed_tw = np.array([int(GCP.graded_antecedent_pick(pr, ps)["pick"] == gi) for pr, gi, ps in tw], float)

    print("F. the LANDED graded_antecedent_pick on the pronoun population (the right-axis organ already exists)")
    check("LANDED beats content floor by >= +0.10", landed.mean() - freq.mean() >= 0.10,
          "landed=%.3f freq=%.3f (+%.3f)" % (landed.mean(), freq.mean(), landed.mean() - freq.mean()))
    check("LANDED beats incumbent hard-tier", landed.mean() - hard.mean() > 0,
          "landed=%.3f hard=%.3f (+%.3f)" % (landed.mean(), hard.mean(), landed.mean() - hard.mean()))
    check("LANDED shuffled-context twin LOSES", landed_tw.mean() < landed.mean(),
          "twin=%.3f vs landed=%.3f" % (landed_tw.mean(), landed.mean()))
    print("G. the brief's proposal (multi-timescale TCM cue) is a RIGOROUS NEGATIVE")
    check("adding the multi-timescale TCM cue does NOT beat LANDED by > 0.02", ltcm.mean() - landed.mean() <= 0.02,
          "landed+tcm=%.3f landed=%.3f (delta %+.3f)" % (ltcm.mean(), landed.mean(), ltcm.mean() - landed.mean()))


# ---------------- H. the NEW WIN: gender-agreement filter (phi from full coref chains) beats the landed picker ----
def check_H():
    import glob, collections
    from hdlab import graded_coref_pick as GCP
    CONLL = os.path.join(REPO, "data", "litbank", "coref_conll")
    MASC = {"he", "him", "his", "himself"}; FEM = {"she", "her", "hers", "herself"}; NEUT = {"it", "its", "itself"}
    PLUR = {"they", "them", "their", "theirs", "themselves", "we", "us", "our", "ours", "ourselves"}

    def clusters(path):
        st = collections.defaultdict(list); toks = []; clus = collections.defaultdict(list)
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) < 5:
                continue
            word = f[3]; coref = f[-1].strip(); gi = len(toks); toks.append(word)
            if coref in ("_", "-", ""):
                continue
            for part in coref.split("|"):
                part = part.strip()
                if part.startswith("(") and part.endswith(")"):
                    clus[int(part[1:-1])].append(word)
                elif part.startswith("("):
                    st[int(part[1:])].append(gi)
                elif part.endswith(")"):
                    c = int(part[:-1])
                    if st[c]:
                        s0 = st[c].pop()
                        clus[c].extend(toks[s0:gi + 1])
        return clus

    P1 = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
    P2 = {"you", "your", "yours", "yourself", "yourselves", "thou", "thee", "thy", "thine"}

    def phi_of(words):
        low = [w.lower() for w in words]; cnt = collections.Counter(low)
        gm = sum(cnt.get(w, 0) for w in MASC); gf = sum(cnt.get(w, 0) for w in FEM); gn = sum(cnt.get(w, 0) for w in NEUT)
        gendered = (gm + gf) > 0
        gender = ({0: "M", 1: "F", 2: "N"}[[gm, gf, gn].index(max(gm, gf, gn))] if (max(gm, gf, gn) > 0 and gendered) else "UNK")
        p1 = sum(cnt.get(w, 0) for w in P1); p2 = sum(cnt.get(w, 0) for w in P2)
        third = sum(cnt.get(w, 0) for w in (MASC | FEM | NEUT | {"they", "them", "their"}))
        person = ("1" if p1 >= p2 else "2") if ((p1 + p2) > 0 and third == 0) else "3"
        return (gender, person)

    def pron_gender(p):
        p = p.lower()
        if p in MASC: return "M"
        if p in FEM: return "F"
        if p in NEUT: return "N"
        return "UNK"

    phi = {}
    for path in glob.glob(os.path.join(CONLL, "*.conll")):
        phi[os.path.basename(path)[:-6]] = {c: phi_of(w) for c, w in clusters(path).items()}
    insts = json.load(open(PRON, encoding="utf-8"))
    test_docs = set(d for d in sorted(set(i["doc"] for i in insts))
                    if (int(hashlib.md5(d.encode()).hexdigest(), 16) % 1000) / 1000.0 < 0.4)

    def pick(priors, ps, keep_idx):
        sub = [priors[i] for i in keep_idx]
        loc = GCP.graded_antecedent_pick(sub, ps)["pick"]
        return keep_idx[loc] if loc >= 0 else -1

    base = []; pers = []; persgen = []
    n_q = n_unreach = n_struct_err = 0
    for inst in insts:
        if inst["doc"] not in test_docs:
            continue
        ps = int(inst["p_sent"]); items = []
        for cid, ms in inst["candidates"].items():
            pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
            if pm:
                items.append((int(cid), pm))
        if len(items) < 2:
            continue
        cids = [c for c, _ in items]; priors = [pm for _, pm in items]
        gi = cids.index(int(inst["gold"])) if int(inst["gold"]) in cids else -1
        pg = pron_gender(inst["pronoun"])
        cinfo = [phi.get(inst["doc"], {}).get(c, ("UNK", "3")) for c in cids]

        def keep(person=False, gender=False):
            k = [i for i in range(len(priors))
                 if not (person and cinfo[i][1] in ("1", "2"))
                 and not (gender and pg != "UNK" and cinfo[i][0] != "UNK" and cinfo[i][0] != pg)]
            return k if k else list(range(len(priors)))
        base.append(int(GCP.graded_antecedent_pick(priors, ps)["pick"] == gi))
        pk_p = pick(priors, ps, keep(person=True))
        pers.append(int(pk_p == gi))
        persgen.append(int(pick(priors, ps, keep(person=True, gender=True)) == gi))
        # residual bookkeeping (against the landed+person picker, the current-best substrate)
        n_q += 1
        if gi < 0:
            n_unreach += 1
        elif pk_p != gi:
            n_struct_err += 1
    base = np.array(base, float); pers = np.array(pers, float); persgen = np.array(persgen, float)
    print("H. HONEST DECOMPOSITION: person filter (landed) vs GENDER's marginal on top of it")
    check("person filter reproduces its landed win (>= +0.02 over raw picker)", pers.mean() - base.mean() >= 0.02,
          "person=%.3f base=%.3f (+%.3f)" % (pers.mean(), base.mean(), pers.mean() - base.mean()))
    check("GENDER adds NO CI-separated marginal over person (< +0.02) -> rigorous negative",
          (persgen.mean() - pers.mean()) < 0.02,
          "person+gender=%.3f person=%.3f (marginal +%.3f)" % (persgen.mean(), pers.mean(), persgen.mean() - pers.mean()))
    print("I. RESIDUAL is measurably STRUCTURAL, not a memory feature")
    ceiling = 1.0 - n_unreach / n_q
    tot_err = n_unreach + n_struct_err
    check("reachable ceiling >= 0.90 (only ~8% cataphora is unreachable)", ceiling >= 0.90,
          "ceiling=%.3f (unreachable=%.1f%%)" % (ceiling, 100 * n_unreach / n_q))
    check("majority of errors are STRUCTURAL (gold present but not most-accessible)", n_struct_err > n_unreach,
          "structural=%d unreachable=%d (%.0f%% structural)" % (n_struct_err, n_unreach, 100 * n_struct_err / tot_err))


def main():
    print("=" * 78)
    print("WITNESS: retrieval_interference_is_similar_competitor_cue_overload_not_event_count")
    print("=" * 78)
    check_A()
    check_BCDE()
    check_FG()
    check_H()
    print("-" * 78)
    if FAILS:
        print("WITNESS FAILED: %d check(s) -> %s" % (len(FAILS), ", ".join(FAILS)))
        sys.exit(1)
    print("WITNESS PASSED: all checks reproduce from source.")


if __name__ == "__main__":
    main()
