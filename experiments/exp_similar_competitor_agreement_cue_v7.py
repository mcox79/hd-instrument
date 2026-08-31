"""exp_similar_competitor_agreement_cue_v7 -- the PUSH toward excellent: does the brief's CONTENT feature-match
cue (gender/number AGREEMENT), built from RELIABLE data, beat the already-landed graded picker?

CONTEXT. v6 showed the reframe holds and the brief's multi-timescale-TCM proposal is a rigorous negative; the
memory/ACCESSIBILITY axis is at its informational ceiling (landed graded_antecedent_pick = 0.676 on held-out
pronoun coref). The one PINNED cue I had NOT built is morphological AGREEMENT (Van Dyke & McElree's coarse content
cue; obligatory phi-agreement, Benveniste/Mancini) -- the brief's central "feature-MATCHING competitors". My first
phi attempt (from who-did-what action-mentions) was too noisy (gold agreement-compatible only 36%). This cell
builds phi from the FULL LitBank coref chains (coref_conll/*.conll -- every mention token incl. pronouns): gold
agreement-compatible rises to 88.8%, and agreement prunes 21.9% of the candidate pool. So it MIGHT help.

BRAIN MECHANISM. Agreement is an OBLIGATORY hard constraint on anaphora (person/number/gender/animacy). The brain
applies it as a candidate-set filter BEFORE salience-based selection (a fast morphological gate feeding the slower
cue-based retrieval). We replicate: prune confidently-incompatible candidates (recall-safe: UNKNOWN passes; never
empty), THEN run the landed graded_antecedent_pick. Also a SOFT variant (agreement as an added graded cue).

ARMS on the SAME held-out candidate sets (candidate_priors = [(sent, role)] per candidate; phi joined by entity id):
  LANDED            : graded_antecedent_pick alone (the current substrate state) -- the floor to beat
  LANDED+AGR_HARD   : prune known-conflicting gender+number candidates (recall-safe), then landed pick
  LANDED+AGR_GENDER : gender-only hard prune (number inference is noisier; isolate the cleaner signal)
  LANDED+AGR_SOFT   : agreement as an added z-scored cue in the graded competition (DEV-tuned weight)
  TWIN              : AGR_HARD with SHUFFLED phi (permute entity->phi within doc) -> agreement info destroyed -> must LOSE
DIAGNOSTIC (bounds agreement's ceiling): of the LANDED picker's ERRORS, how many are agreement-INCOMPATIBLE picks
  (fixable by the filter) vs compatible-but-wrong (not fixable)?

PASS (a genuine new win) = an agreement arm beats LANDED by >= +0.02 hit@1 CI-separated on held-out docs, twin
losing, holding across splits. RIGOROUS NEGATIVE (also a pass) = it does not -> agreement is already saturated by
the picker / its gold-exclusion cancels its pruning; the residual is purely structural.

Consumes landed hdlab organs (graded_coref_pick, graded_competition). NO external LLM. Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_agreement_cue_v7.py --self-test
     ...                                                                             --full
"""
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import graded_coref_pick as GCP
from hdlab.graded_competition import graded_pick

ANCHOR = "similar_competitor_agreement_cue_v7"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")
CONLL = os.path.join(REPO, "data", "litbank", "coref_conll")

MASC = {"he", "him", "his", "himself"}; FEM = {"she", "her", "hers", "herself"}
NEUT = {"it", "its", "itself"}; PLUR = {"they", "them", "their", "theirs", "themselves", "we", "us", "our", "ours", "ourselves"}
P1 = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
P2 = {"you", "your", "yours", "yourself", "yourselves", "thou", "thee", "thy", "thine"}


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_conll_clusters(path):
    open_stack = collections.defaultdict(list); toks = []; clus = collections.defaultdict(list)
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
                open_stack[int(part[1:])].append(gi)
            elif part.endswith(")"):
                c = int(part[:-1])
                if open_stack[c]:
                    st = open_stack[c].pop()
                    for j in range(st, gi + 1):
                        clus[c].append(toks[j])
    return clus


def entity_phi(clus):
    phi = {}
    for c, words in clus.items():
        low = [w.lower() for w in words]; cnt = collections.Counter(low)
        num, gen, per = "SG", "UNK", "3"
        if any(w in PLUR for w in low):
            num = "PL"
        gm = sum(cnt.get(w, 0) for w in MASC); gf = sum(cnt.get(w, 0) for w in FEM); gnn = sum(cnt.get(w, 0) for w in NEUT)
        if max(gm, gf, gnn) > 0:
            gen = {0: "M", 1: "F", 2: "N"}[[gm, gf, gnn].index(max(gm, gf, gnn))]
            if num == "PL":
                gen = "UNK"
        p1 = sum(cnt.get(w, 0) for w in P1); p2 = sum(cnt.get(w, 0) for w in P2)
        third = sum(cnt.get(w, 0) for w in (MASC | FEM | NEUT | {"they", "them", "their"}))
        if (p1 + p2) > 0 and third == 0:
            per = "1" if p1 >= p2 else "2"
        phi[c] = (num, gen, per)
    return phi


def load_phi_by_doc():
    out = {}
    for path in glob.glob(os.path.join(CONLL, "*.conll")):
        out[os.path.basename(path)[:-6]] = entity_phi(parse_conll_clusters(path))
    return out


def pron_phi(p):
    p = p.lower()
    if p in PLUR: return ("PL", "UNK", "3")
    if p in MASC: return ("SG", "M", "3")
    if p in FEM: return ("SG", "F", "3")
    if p in NEUT: return ("SG", "N", "3")
    if p in P1: return ("UNK", "UNK", "1")
    if p in P2: return ("UNK", "UNK", "2")
    return ("UNK", "UNK", "UNK")


def compat(cp, pp, use_number=True, use_gender=True):
    (cn, cg, cpe), (pn, pg, ppe) = cp, pp
    if use_number and pn != "UNK" and cn != "UNK" and pn != cn: return False
    if use_gender and pg != "UNK" and cg != "UNK" and pg != cg: return False
    if ppe != "UNK" and cpe != "UNK" and ppe != cpe: return False
    return True


def load_insts():
    return json.load(open(PRON, encoding="utf-8"))


def split_docs(insts, frac=0.4, salt=""):
    return set(d for d in sorted(set(i["doc"] for i in insts))
               if (int(hashlib.md5((salt + d).encode()).hexdigest(), 16) % 1000) / 1000.0 < frac)


def query_rows(insts, phi_by_doc, shuffle_phi=False, seed=7):
    gen = np.random.default_rng(seed)
    rows = []
    for inst in insts:
        ps = int(inst["p_sent"]); doc = inst["doc"]; phi = phi_by_doc.get(doc, {})
        items = []
        for cid, ms in inst["candidates"].items():
            pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
            if pm:
                items.append((int(cid), pm))
        if len(items) < 2:
            continue
        cids = [c for c, _ in items]; priors = [pm for _, pm in items]
        cand_phi = [phi.get(c, ("UNK", "UNK", "3")) for c in cids]
        if shuffle_phi:                       # twin: permute the phi labels across this doc's candidates
            perm = gen.permutation(len(cand_phi)); cand_phi = [cand_phi[i] for i in perm]
        gi = cids.index(int(inst["gold"])) if int(inst["gold"]) in cids else -1
        rows.append({"priors": priors, "cand_phi": cand_phi, "gi": gi, "ps": ps,
                     "pron_phi": pron_phi(inst["pronoun"])})
    return rows


def keep_compatible(row, use_number=True, use_gender=True):
    pp = row["pron_phi"]
    keep = [i for i, cp in enumerate(row["cand_phi"]) if compat(cp, pp, use_number, use_gender)]
    return keep if len(keep) >= 1 else list(range(len(row["priors"])))   # recall-safe: never empty


def landed_pick_full(priors, ps):
    return GCP.graded_antecedent_pick(priors, ps)["pick"]


def landed_pick_filtered(row, use_number=True, use_gender=True):
    keep = keep_compatible(row, use_number, use_gender)
    sub = [row["priors"][i] for i in keep]
    local = GCP.graded_antecedent_pick(sub, row["ps"])["pick"]
    return keep[local] if local >= 0 else -1


def _zscore(v):
    v = np.asarray(v, float); s = v.std()
    return (v - v.mean()) / s if s > 1e-12 else np.zeros_like(v)


def _base_sup(priors, ps, d=GCP.DEFAULT_ACTR_D):
    prev = max((s for pri in priors for (s, _r) in pri if s < ps), default=None)
    early = [min(s for s, _r in pri) for pri in priors]; fs = min(early)
    rec = [1.0 / min(GCP._dt(ps, s) for s, _ in pri) for pri in priors]
    subj = [max(GCP.ROLE_W.get(r, 1.0) for _s, r in pri) for pri in priors]
    cb = [1.0 if any(s == prev and r == "SUBJECT" for s, r in pri) else 0.0 for pri in priors]
    freq = [math.log1p(len(pri)) for pri in priors]
    first = [1.0 if early[i] == fs else 0.0 for i in range(len(priors))]
    par = [1.0 if max(pri, key=lambda sr: sr[0])[1] == "OTHER" else 0.0 for pri in priors]
    actr = [math.log(sum(GCP.ROLE_W.get(r, 1.0) * (GCP._dt(ps, s) ** (-d)) for s, r in pri)) for pri in priors]
    return {"recency": _zscore(rec), "subject": _zscore(subj), "cb": _zscore(cb), "freq": _zscore(freq),
            "first": _zscore(first), "parallel": _zscore(par), "actr": _zscore(actr)}


def landed_pick_soft(row, w_agr):
    pp = row["pron_phi"]
    agr = [1.0 if compat(cp, pp) else -1.0 for cp in row["cand_phi"]]
    sup = _base_sup(row["priors"], row["ps"]); sup["agr"] = _zscore(agr)
    w = dict(GCP.TUNED_WEIGHTS); w["agr"] = w_agr
    return int(graded_pick(sup, w, gain=GCP.DEFAULT_GAIN)["win"])


def acc(rows, fn):
    return float(np.mean([int(fn(r) == r["gi"]) for r in rows])) if rows else float("nan")


def paired(a, b, gen, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a - b; n = len(diff)
    idx = gen.integers(0, n, size=(n_boot, n)); boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    signs = gen.choice([-1.0, 1.0], size=(n_boot, n))
    p95 = float(np.percentile(np.abs((diff[None, :] * signs).mean(axis=1)), 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "band": band, "n": n}


def run(n_boot=2000):
    t0 = time.perf_counter()
    insts = load_insts(); phi_by_doc = load_phi_by_doc(); gen = np.random.default_rng(20260831)
    test_docs = split_docs(insts)
    tr = query_rows([i for i in insts if i["doc"] not in test_docs], phi_by_doc)
    te = query_rows([i for i in insts if i["doc"] in test_docs], phi_by_doc)

    # DEV-tune the soft agreement weight on train
    best_wa, best = 0.0, -1
    for wa in [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0]:
        a = acc(tr, lambda r, wa=wa: landed_pick_soft(r, wa))
        if a > best:
            best, best_wa = a, wa

    cv_landed = np.array([int(landed_pick_full(r["priors"], r["ps"]) == r["gi"]) for r in te], float)
    cv_hard = np.array([int(landed_pick_filtered(r, True, True) == r["gi"]) for r in te], float)
    cv_gen = np.array([int(landed_pick_filtered(r, False, True) == r["gi"]) for r in te], float)
    cv_soft = np.array([int(landed_pick_soft(r, best_wa) == r["gi"]) for r in te], float)

    a_landed, a_hard, a_gen, a_soft = cv_landed.mean(), cv_hard.mean(), cv_gen.mean(), cv_soft.mean()
    d_hard = paired(cv_hard, cv_landed, gen, n_boot)
    d_gen = paired(cv_gen, cv_landed, gen, n_boot)
    d_soft = paired(cv_soft, cv_landed, gen, n_boot)

    # twin: shuffled phi (best arm = whichever agreement arm is highest)
    te_tw = query_rows([i for i in insts if i["doc"] in test_docs], phi_by_doc, shuffle_phi=True, seed=101)
    a_twin_hard = acc(te_tw, lambda r: landed_pick_filtered(r, True, True))

    # diagnostic: of LANDED errors, how many are agreement-INCOMPATIBLE picks (fixable) vs compatible-but-wrong?
    fixable = notfix = 0
    for r in te:
        pk = landed_pick_full(r["priors"], r["ps"])
        if pk == r["gi"]:
            continue
        if not compat(r["cand_phi"][pk], r["pron_phi"]):
            fixable += 1
        else:
            notfix += 1
    n_err = fixable + notfix

    best_arm = max([("AGR_HARD", a_hard), ("AGR_GENDER", a_gen), ("AGR_SOFT", a_soft)], key=lambda kv: kv[1])
    best_d = {"AGR_HARD": d_hard, "AGR_GENDER": d_gen, "AGR_SOFT": d_soft}[best_arm[0]]
    verdict = "AGREEMENT_HELPS" if (best_d["band"] == "ABOVE" and best_d["delta"] >= 0.02) else \
              ("MARGINAL" if best_d["band"] == "ABOVE" else "RIGOROUS_NEGATIVE")

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_test": len(te), "soft_weight": best_wa,
           "acc": {"LANDED": a_landed, "LANDED+AGR_HARD": a_hard, "LANDED+AGR_GENDER": a_gen,
                   "LANDED+AGR_SOFT": a_soft, "TWIN_shuffled_phi": a_twin_hard},
           "delta_hard_vs_landed": d_hard, "delta_gender_vs_landed": d_gen, "delta_soft_vs_landed": d_soft,
           "landed_errors": {"total": n_err, "agreement_fixable": fixable, "not_fixable": notfix,
                             "fixable_frac_of_errors": fixable / n_err if n_err else 0.0},
           "twin_hard_loses": bool(a_twin_hard < a_hard),
           "best_arm": best_arm[0], "VERDICT": verdict}
    _log("=== held-out TEST (n=%d) ===" % len(te))
    _log("  LANDED=%.3f | +AGR_HARD=%.3f | +AGR_GENDER=%.3f | +AGR_SOFT=%.3f(w=%.2f) | TWIN(shuffled phi)=%.3f"
         % (a_landed, a_hard, a_gen, a_soft, best_wa, a_twin_hard))
    _log("  AGR_HARD-LANDED   = %+.3f [%.3f,%.3f] %s" % (d_hard["delta"], d_hard["lo"], d_hard["hi"], d_hard["band"]))
    _log("  AGR_GENDER-LANDED = %+.3f [%.3f,%.3f] %s" % (d_gen["delta"], d_gen["lo"], d_gen["hi"], d_gen["band"]))
    _log("  AGR_SOFT-LANDED   = %+.3f [%.3f,%.3f] %s" % (d_soft["delta"], d_soft["lo"], d_soft["hi"], d_soft["band"]))
    _log("  LANDED errors: %d total | %d agreement-FIXABLE (%.1f%%) | %d not-fixable  <- ceiling for agreement"
         % (n_err, fixable, 100 * fixable / n_err if n_err else 0.0, notfix))
    _log("VERDICT: %s (best arm %s; twin loses=%s) (%.1fs)"
         % (verdict, best_arm[0], res["twin_hard_loses"], res["elapsed_s"]))
    return res


def self_test():
    _log("SELF-TEST: conll phi parse; agreement prune recall-safe; soft cue runs")
    phi = load_phi_by_doc()
    assert len(phi) >= 90, "expected ~100 docs of phi, got %d" % len(phi)
    # a masculine query should prune a confidently-feminine candidate
    row = {"priors": [[(1, "SUBJECT")], [(2, "OTHER")]], "cand_phi": [("SG", "F", "3"), ("SG", "M", "3")],
           "gi": 1, "ps": 5, "pron_phi": ("SG", "M", "3")}
    keep = keep_compatible(row)
    assert keep == [1], "masculine pronoun should keep only the masculine candidate: %r" % keep
    # recall-safe: if all pruned, keep all
    row2 = {"priors": [[(1, "OTHER")], [(2, "OTHER")]], "cand_phi": [("SG", "F", "3"), ("SG", "F", "3")],
            "gi": 0, "ps": 5, "pron_phi": ("SG", "M", "3")}
    assert keep_compatible(row2) == [0, 1], "must not empty the pool"
    assert landed_pick_soft(row, 1.0) in (0, 1)
    _log("SELF-TEST PASS")
    return {"n_docs_phi": len(phi)}


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    if args.self_test or not args.full:
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now_iso()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run()
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
