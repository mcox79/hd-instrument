"""exp_similar_competitor_agreement_decomposition_v8 -- HONEST decomposition: what does GENDER agreement add
OVER the already-landed PERSON/animacy pool-cleanup?

WHY. v7 reported a "+0.040 gender" win, but the scaffold-free witness caught that v7's gender arm ALSO applied a
person filter (compat checks person), and person-based pool-cleanup is ALREADY LANDED
(graded_coref_pick.keep_after_pool_cleanup / phi_agreement_keep: drop 1st/2nd-person discourse participants,
+0.022 CI-sep, owner-DONE). So v7 partly re-derived a landed win. The honest question is gender's MARGINAL value
over a person-filtered baseline (the true current substrate state). This cell decomposes it.

ARMS on the SAME held-out candidate sets (phi from the full LitBank coref chains; conservative number = a gendered
he/she forces SINGULAR):
  BASE     : landed graded_antecedent_pick, NO filter
  +P       : + person filter (drop 1st/2nd-person discourse participants) -- the ALREADY-LANDED pool cleanup
  +P+G     : + gender agreement
  +P+G+N   : + gender + conservative number
  G_only   : gender filter WITHOUT person (isolates raw gender)
KEY MARGINALS (the honest new-contribution numbers):
  (+P) - BASE        = the already-landed person win (should reproduce ~+0.02)
  (+P+G) - (+P)      = GENDER's marginal over the landed baseline  <-- the claim that matters
  (+P+G+N) - (+P+G)  = NUMBER's marginal
TWIN: +P+G+N with shuffled phi -> agreement/person info destroyed -> must LOSE.
ROBUSTNESS: the gender-marginal across 6 doc splits.

Consumes landed hdlab organs. NO external LLM. Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_agreement_decomposition_v8.py --self-test
     ...                                                                                       --full
"""
from __future__ import annotations

import argparse, collections, glob, hashlib, json, os, sys, time
from datetime import datetime, timezone
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from hdlab import graded_coref_pick as GCP

ANCHOR = "similar_competitor_agreement_decomposition_v8"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")
CONLL = os.path.join(REPO, "data", "litbank", "coref_conll")

MASC = {"he", "him", "his", "himself"}; FEM = {"she", "her", "hers", "herself"}; NEUT = {"it", "its", "itself"}
PLUR = {"they", "them", "their", "theirs", "themselves", "we", "us", "our", "ours", "ourselves"}
P1 = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
P2 = {"you", "your", "yours", "yourself", "yourselves", "thou", "thee", "thy", "thine"}


def _log(m): print("[%s] %s" % (ANCHOR, m), flush=True)
def _now(): return datetime.now(timezone.utc).isoformat()


def parse_clusters(path):
    st = collections.defaultdict(list); toks = []; clus = collections.defaultdict(list)
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"): continue
        f = line.split("\t")
        if len(f) < 5: continue
        word = f[3]; coref = f[-1].strip(); gi = len(toks); toks.append(word)
        if coref in ("_", "-", ""): continue
        for part in coref.split("|"):
            part = part.strip()
            if part.startswith("(") and part.endswith(")"): clus[int(part[1:-1])].append(word)
            elif part.startswith("("): st[int(part[1:])].append(gi)
            elif part.endswith(")"):
                c = int(part[:-1])
                if st[c]:
                    s0 = st[c].pop(); clus[c].extend(toks[s0:gi + 1])
    return clus


def entity_phi(clus):
    """(number, gender, person). Conservative number: a gendered he/she forces SG (overrides stray plural)."""
    phi = {}
    for c, words in clus.items():
        low = [w.lower() for w in words]; cnt = collections.Counter(low)
        gm = sum(cnt.get(w, 0) for w in MASC); gf = sum(cnt.get(w, 0) for w in FEM); gn = sum(cnt.get(w, 0) for w in NEUT)
        gendered = (gm + gf) > 0
        num = "SG" if gendered else ("PL" if any(w in PLUR for w in low) else "SG")
        gen = ({0: "M", 1: "F", 2: "N"}[[gm, gf, gn].index(max(gm, gf, gn))] if (max(gm, gf, gn) > 0 and num == "SG") else "UNK")
        p1 = sum(cnt.get(w, 0) for w in P1); p2 = sum(cnt.get(w, 0) for w in P2)
        third = sum(cnt.get(w, 0) for w in (MASC | FEM | NEUT | {"they", "them", "their"}))
        per = ("1" if p1 >= p2 else "2") if ((p1 + p2) > 0 and third == 0) else "3"
        phi[c] = (num, gen, per)
    return phi


def load_phi():
    return {os.path.basename(p)[:-6]: entity_phi(parse_clusters(p)) for p in glob.glob(os.path.join(CONLL, "*.conll"))}


def pron_phi(p):
    p = p.lower()
    if p in PLUR: return ("PL", "UNK", "3")
    if p in MASC: return ("SG", "M", "3")
    if p in FEM: return ("SG", "F", "3")
    if p in NEUT: return ("SG", "N", "3")
    if p in P1: return ("UNK", "UNK", "1")
    if p in P2: return ("UNK", "UNK", "2")
    return ("UNK", "UNK", "UNK")


def load_insts(): return json.load(open(PRON, encoding="utf-8"))
def split_docs(insts, frac=0.4, salt=""):
    return set(d for d in sorted(set(i["doc"] for i in insts))
               if (int(hashlib.md5((salt + d).encode()).hexdigest(), 16) % 1000) / 1000.0 < frac)


def rows_of(insts, phi_by_doc, shuffle_phi=False, seed=7):
    gen = np.random.default_rng(seed); out = []
    for inst in insts:
        ps = int(inst["p_sent"]); phi = phi_by_doc.get(inst["doc"], {}); items = []
        for cid, ms in inst["candidates"].items():
            pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
            if pm: items.append((int(cid), pm))
        if len(items) < 2: continue
        cids = [c for c, _ in items]; priors = [pm for _, pm in items]
        cph = [phi.get(c, ("SG", "UNK", "3")) for c in cids]
        if shuffle_phi:
            perm = gen.permutation(len(cph)); cph = [cph[i] for i in perm]
        gi = cids.index(int(inst["gold"])) if int(inst["gold"]) in cids else -1
        out.append({"priors": priors, "cph": cph, "gi": gi, "ps": ps, "pp": pron_phi(inst["pronoun"])})
    return out


def keep(row, person=False, gender=False, number=False):
    pp = row["pp"]; k = []
    for i, (cn, cg, cpe) in enumerate(row["cph"]):
        if person and cpe in ("1", "2"):                      # discourse participant -> not a 3rd-person antecedent
            continue
        if gender and pp[1] != "UNK" and cg != "UNK" and cg != pp[1]:
            continue
        if number and pp[0] != "UNK" and cn != "UNK" and cn != pp[0]:
            continue
        k.append(i)
    return k if k else list(range(len(row["priors"])))        # recall-safe


def pick(row, **flt):
    k = keep(row, **flt); sub = [row["priors"][i] for i in k]
    loc = GCP.graded_antecedent_pick(sub, row["ps"])["pick"]
    return k[loc] if loc >= 0 else -1


def acc(rows, **flt):
    return float(np.mean([int(pick(r, **flt) == r["gi"]) for r in rows])) if rows else float("nan")


def cvec(rows, **flt):
    return np.array([int(pick(r, **flt) == r["gi"]) for r in rows], float)


def paired(a, b, gen, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a - b; n = len(diff)
    idx = gen.integers(0, n, size=(n_boot, n)); boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    signs = gen.choice([-1.0, 1.0], size=(n_boot, n))
    p95 = float(np.percentile(np.abs((diff[None, :] * signs).mean(axis=1)), 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "band": band, "n": n}


def run(n_boot=2000):
    t0 = time.perf_counter(); insts = load_insts(); phi = load_phi(); gen = np.random.default_rng(20260831)
    test = split_docs(insts); te = rows_of([i for i in insts if i["doc"] in test], phi)

    base = cvec(te); P = cvec(te, person=True); PG = cvec(te, person=True, gender=True)
    PGN = cvec(te, person=True, gender=True, number=True); Gonly = cvec(te, gender=True)
    d_P = paired(P, base, gen, n_boot)                 # landed person win (reproduce ~+0.02)
    d_Gmarg = paired(PG, P, gen, n_boot)               # GENDER marginal over person  <-- the claim
    d_Nmarg = paired(PGN, PG, gen, n_boot)             # number marginal
    d_PGN_base = paired(PGN, base, gen, n_boot)        # full stack over raw landed
    tw = rows_of([i for i in insts if i["doc"] in test], phi, shuffle_phi=True, seed=101)
    a_twin = acc(tw, person=True, gender=True, number=True)

    # robustness of the gender marginal across splits
    marg = []
    for salt in ["", "s1", "s2", "s3", "s4", "s5"]:
        ts = split_docs(insts, salt=salt); r = rows_of([i for i in insts if i["doc"] in ts], phi)
        marg.append(acc(r, person=True, gender=True) - acc(r, person=True))
    marg = np.array(marg)

    verdict = "GENDER_ADDS_OVER_LANDED" if (d_Gmarg["band"] == "ABOVE" and d_Gmarg["delta"] >= 0.02) else \
              ("GENDER_MARGINAL_SMALL" if d_Gmarg["band"] == "ABOVE" else "GENDER_NO_MARGINAL")
    res = {"anchor": ANCHOR, "ts_iso": _now(), "elapsed_s": time.perf_counter() - t0, "n_test": len(te),
           "acc": {"BASE": base.mean(), "+P": P.mean(), "+P+G": PG.mean(), "+P+G+N": PGN.mean(),
                   "G_only_no_person": Gonly.mean(), "TWIN_shuffled_phi": a_twin},
           "person_win_over_base": d_P, "GENDER_marginal_over_person": d_Gmarg,
           "number_marginal": d_Nmarg, "full_stack_over_base": d_PGN_base,
           "gender_marginal_across_splits_mean": float(marg.mean()), "gender_marginal_across_splits_std": float(marg.std()),
           "splits_gender_positive": int((marg > 0).sum()), "twin_loses": bool(a_twin < PGN.mean()), "VERDICT": verdict}
    _log("=== held-out TEST (n=%d) ===" % len(te))
    _log("  BASE=%.3f  +P=%.3f  +P+G=%.3f  +P+G+N=%.3f  (G_only_no_person=%.3f)  TWIN=%.3f"
         % (base.mean(), P.mean(), PG.mean(), PGN.mean(), Gonly.mean(), a_twin))
    _log("  person win (+P - BASE)          = %+.3f [%.3f,%.3f] %s  (already-landed pool cleanup)"
         % (d_P["delta"], d_P["lo"], d_P["hi"], d_P["band"]))
    _log("  GENDER marginal (+P+G - +P)     = %+.3f [%.3f,%.3f] %s  <-- the honest new claim"
         % (d_Gmarg["delta"], d_Gmarg["lo"], d_Gmarg["hi"], d_Gmarg["band"]))
    _log("  NUMBER marginal (+P+G+N - +P+G) = %+.3f [%.3f,%.3f] %s"
         % (d_Nmarg["delta"], d_Nmarg["lo"], d_Nmarg["hi"], d_Nmarg["band"]))
    _log("  full stack (+P+G+N - BASE)      = %+.3f [%.3f,%.3f] %s"
         % (d_PGN_base["delta"], d_PGN_base["lo"], d_PGN_base["hi"], d_PGN_base["band"]))
    _log("  GENDER marginal across 6 splits = %+.3f +/- %.3f  (%d/6 positive)"
         % (marg.mean(), marg.std(), int((marg > 0).sum())))
    _log("VERDICT: %s (twin loses=%s) (%.1fs)" % (verdict, res["twin_loses"], res["elapsed_s"]))
    return res


def self_test():
    _log("SELF-TEST: phi parse; person/gender/number filters recall-safe")
    phi = load_phi(); assert len(phi) >= 90
    row = {"priors": [[(1, "SUBJECT")], [(2, "OTHER")]], "cph": [("SG", "F", "3"), ("SG", "M", "3")],
           "gi": 1, "ps": 5, "pp": ("SG", "M", "3")}
    assert keep(row, gender=True) == [1]
    row2 = {"priors": [[(1, "OTHER")], [(2, "OTHER")]], "cph": [("SG", "F", "3"), ("SG", "F", "3")],
            "gi": 0, "ps": 5, "pp": ("SG", "M", "3")}
    assert keep(row2, gender=True) == [0, 1]                    # recall-safe: never empty
    row3 = {"priors": [[(1, "OTHER")], [(2, "OTHER")]], "cph": [("SG", "UNK", "1"), ("SG", "M", "3")],
            "gi": 1, "ps": 5, "pp": ("SG", "M", "3")}
    assert keep(row3, person=True) == [1]                       # drop 1st-person participant
    _log("SELF-TEST PASS")
    return {"n_docs": len(phi)}


def _aw(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--full", action="store_true")
    a = ap.parse_args(); t0 = time.perf_counter()
    if a.self_test or not a.full:
        st = self_test(); _aw(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                              {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0)); return
    res = run(); _aw(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
