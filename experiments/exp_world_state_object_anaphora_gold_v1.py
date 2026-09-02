"""exp_world_state_object_anaphora_gold_v1 -- close the one honest gap in the coref-blind-register solution:
give OBJECT ANAPHORA a CI-separated ACCURACY (not just impact/coverage) on REAL GOLD.

CONTEXT: the register's object key needs "it/its/they/them" resolved to the salient object entity (the route the
reader's coref LACKS -- TARGET_PRONOUNS is he/she only). The build-across cell measured object-anaphora IMPACT
(259/374 MCScript2 relocations) but not accuracy, because MCScript2 has no gold coref. DISCOVERY (2026-09-01):
LitBank's coref CoNLL gold-clusters NON-PERSON entities too (facilities/locations/vehicles/groups), so 354
object-pronoun mentions (it/its/they/them/their) carry a GOLD cluster and 270 have a resolvable prior nominal
antecedent. That is real gold for object anaphora.

BRAIN MECHANISM (PINNED): object anaphora uses the SAME Centering salience machinery as person anaphora
(Grosz-Joshi-Weinstein 1995, Cf-ranking is entity-type-agnostic) + a NUMBER-agreement filter (it/its singular;
they/them/their plural) + the pleonastic-'it' filter (Lappin & Leass 1994). The open question this drill answers
empirically: for OBJECTS, does Centering SALIENCE (topical/subject-prominence) beat pure RECENCY, or is object
antecedent-ranking different from person anaphora? Let the gold decide.

ARMS (resolve each object pronoun to a prior nominal MENTION; correct = that mention's gold cluster == the
pronoun's gold cluster):
  recency        : the most-recent prior nominal (number-agreed) -- the simplest floor.
  salience       : Centering Cf pick = subject-prominence (sent_role_rank==0) weighted + recency decay (the
                   brain-faithful arm; number-agreed).
  first_mention  : the earliest nominal in the pronoun's gold-eligible window (a can-fail floor).
  twin (NULL)    : a random prior number-agreed nominal (K permutations -> mean + p95; info-free control).
  gold           : the antecedent exists by construction -> upper bound (sanity).
CONTROLS: reader's OWN coref ABSTAINS on these (0.0, out of scope) -- the organ recovers what the reader cannot;
number-agreement ablation; the twin NULL must lose CI-sep. Glass-box; NO spaCy/LLM. ASCII only.
# KB_REFERENT: data/corpora/litbank_coref_conll
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from collections import Counter

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR = "world_state_object_anaphora_gold_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
LITBANK_DIR = os.path.join(REPO, "data", "corpora", "litbank_coref_conll")

SG_PRON = {"it", "its"}                       # singular object anaphora
PL_PRON = {"they", "them", "their"}           # plural / group anaphora
PERSON_PRON = {"he", "him", "his", "she", "her", "hers", "i", "me", "my", "we", "us", "you", "your"}
RECENCY_WINDOW = 25                           # candidate nominal mentions to look back (mention-stream distance)
W_SUBJECT = 2.0                               # Centering Cf: subject-prominence weight
LAM = 0.08                                    # recency decay


def is_plural_head(h):
    """Crude morphological number: a nominal head ending in 's' (not 'ss'/'us'/'is') is plural-ish."""
    h = h.lower()
    if len(h) >= 3 and h.endswith("s") and not h.endswith(("ss", "us", "is")):
        return True
    return False


def candidates_before(nominals, p_midx, want_plural, number_filter=True):
    """prior nominal mentions within the recency window. number_filter=True applies the PINNED number-agreement
    (it/its -> singular candidate, they/them -> plural); False is the ABLATION (no agreement)."""
    out = [m for m in nominals if m["midx"] < p_midx]
    out = out[-RECENCY_WINDOW:]
    if not number_filter:
        return out
    agreed = [m for m in out if is_plural_head(m["head"]) == want_plural]
    return agreed if agreed else out          # fall back to all if number filter empties the pool


def pick_recency(cands):
    return cands[-1] if cands else None


def pick_first(cands):
    return cands[0] if cands else None


def pick_salience(cands, p_midx):
    """Centering Cf pick: subject-prominence + recency decay (person-anaphora arm)."""
    best, best_s = None, -1e9
    for m in cands:
        s = (W_SUBJECT if m.get("sent_role_rank", 9) == 0 else 1.0)
        s += np.exp(-LAM * (p_midx - m["midx"]))
        if s > best_s:
            best_s, best = s, m
    return best


def pick_recency_object(cands):
    """the binder's actual policy: most-recent NON-SUBJECT nominal (an object/oblique is the salient theme for
    object anaphora -- objects are rarely the discourse Cb, so subject-prominence is the WRONG cue for 'it')."""
    objs = [m for m in cands if m.get("sent_role_rank", 9) != 0]
    return (objs[-1] if objs else (cands[-1] if cands else None))


def run_doc(path):
    from hdlab.coref import parse_litbank_conll, load_name_gender
    gaz = load_name_gender()
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    if not mentions:
        return []
    nominals = [m for m in mentions if not m["is_pronoun"] and m["head"] not in PERSON_PRON]
    rows = []
    for m in mentions:
        h = m["head"]
        if h not in SG_PRON and h not in PL_PRON:
            continue
        want_plural = h in PL_PRON
        c_p = m["cluster"]
        cands = candidates_before(nominals, m["midx"], want_plural)
        if not cands:
            continue
        # resolvable = a prior nominal in the SAME gold cluster exists (else the pronoun's antecedent is a
        # pronoun-only chain / cataphor -> out of an object-anaphora resolver's scope; excluded, counted).
        resolvable = any(cm["cluster"] == c_p for cm in cands)
        if not resolvable:
            continue
        cands_nonum = candidates_before(nominals, m["midx"], want_plural, number_filter=False)
        rec = pick_recency(cands)
        fir = pick_first(cands)
        sal = pick_salience(cands, m["midx"])
        rob = pick_recency_object(cands)
        rec_nn = pick_recency(cands_nonum)                       # ABLATION: recency without number agreement
        rows.append({
            "kind": "sg" if h in SG_PRON else "pl",
            "recency": int(rec["cluster"] == c_p),
            "first": int(fir["cluster"] == c_p),
            "salience": int(sal["cluster"] == c_p),
            "recency_object": int(rob["cluster"] == c_p),
            "recency_nonumber": int(rec_nn["cluster"] == c_p) if rec_nn else 0,
            "gold_cluster": c_p,
            "cand_clusters": [cm["cluster"] for cm in cands],   # for the random-twin NULL
        })
    return rows


def boot(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return {"acc": None, "ci": [None, None], "n": 0, "half": None}
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return {"acc": round(float(vals.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "n": len(vals), "half": round((hi - lo) / 2, 4)}


def twin_null(rows, n_boot, seed):
    """random prior number-agreed nominal (info-free): each row draws a random candidate cluster; K resamples."""
    rng = np.random.default_rng(seed)
    accs = []
    for _ in range(n_boot):
        hits = 0
        for r in rows:
            cc = r["cand_clusters"]
            hits += int(cc[rng.integers(0, len(cc))] == r["gold_cluster"])
        accs.append(hits / len(rows))
    accs = np.asarray(accs, float)
    return {"mean": round(float(accs.mean()), 4), "p95": round(float(np.percentile(accs, 95)), 4)}


def run(mode="full", n_docs=100, n_boot=2000, seed=20260901):
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    if mode == "smoke":
        files = files[:5]
    else:
        files = files[:n_docs]
    rows = []
    for f in files:
        rows.extend(run_doc(f))
    res = {"anchor": ANCHOR, "mode": mode, "n_docs": len(files), "n_items": len(rows)}
    if rows:
        sg = [r for r in rows if r["kind"] == "sg"]
        for name in ("recency", "first", "salience", "recency_object", "recency_nonumber"):
            res[name] = boot([r[name] for r in rows], n_boot, seed + hash(name) % 999)
        # PINNED number-agreement ablation: recency(number-agreed) minus recency(no agreement).
        dnn = np.asarray([r["recency"] - r["recency_nonumber"] for r in rows], float)
        rngn = np.random.default_rng(seed + 17)
        bnn = [dnn[rngn.integers(0, len(dnn), len(dnn))].mean() for _ in range(n_boot)]
        res["number_agreement_gain"] = {"delta": round(float(dnn.mean()), 4),
                                        "ci": [round(float(np.percentile(bnn, 2.5)), 4), round(float(np.percentile(bnn, 97.5)), 4)]}
        res["twin_random_null"] = twin_null(rows, n_boot, seed + 5)
        res["reader_coref_on_it"] = 0.0     # the reader's coref abstains on it/they (TARGET_PRONOUNS = he/she only)
        # paired salience-minus-recency (does person-anaphora Cf subject-prominence beat pure recency for OBJECTS?)
        d = np.asarray([r["salience"] - r["recency"] for r in rows], float)
        rng2 = np.random.default_rng(seed + 9)
        bs = [d[rng2.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
        res["salience_minus_recency"] = {"delta": round(float(d.mean()), 4),
                                         "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}
        res["best_arm"] = max(("recency", "first", "salience", "recency_object"), key=lambda a: res[a]["acc"])
        res["best_beats_twin_p95"] = bool(res[res["best_arm"]]["acc"] > res["twin_random_null"]["p95"])
        res["n_sg"] = len(sg)
        if sg:
            res["salience_sg_only"] = boot([r["salience"] for r in sg], n_boot, seed + 3)
            res["recency_object_sg_only"] = boot([r["recency_object"] for r in sg], n_boot, seed + 4)
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    """salience prefers the subject-prominent object over a more-recent oblique; number filter works."""
    noms = [
        {"midx": 0, "head": "book", "cluster": 7, "sent_role_rank": 0},   # subject-ish, cluster 7
        {"midx": 1, "head": "table", "cluster": 9, "sent_role_rank": 1},  # more recent, oblique
    ]
    sal = pick_salience(noms, 2)
    rec = pick_recency(noms)
    print("[self-test] salience picks subject-prominent 'book'(c7): %s ; recency picks 'table'(c9): %s"
          % (sal["cluster"] == 7, rec["cluster"] == 9), flush=True)
    ok = sal["cluster"] == 7 and rec["cluster"] == 9 and is_plural_head("books") and not is_plural_head("book")
    print("[self-test] number: books=plural, book=singular: %s" % (is_plural_head("books") and not is_plural_head("book")), flush=True)
    print("[self-test] " + ("OK" if ok else "FAIL"), flush=True)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_boot=(400 if mode == "smoke" else args.n_boot))
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    if res["n_items"]:
        print("  n_items=%d (sg it/its=%d) over %d docs" % (res["n_items"], res.get("n_sg", 0), res["n_docs"]), flush=True)
        for a in ("recency", "recency_nonumber", "recency_object", "first", "salience"):
            print("  %-16s %.3f %s" % (a, res[a]["acc"], res[a]["ci"]), flush=True)
        print("  number-agreement gain (recency agreed - no-agreement): %.3f %s"
              % (res["number_agreement_gain"]["delta"], res["number_agreement_gain"]["ci"]), flush=True)
        print("  twin random NULL: mean=%.3f p95=%.3f  | reader coref on 'it' = 0.000 (abstains, out of scope)"
              % (res["twin_random_null"]["mean"], res["twin_random_null"]["p95"]), flush=True)
        print("  salience-minus-recency delta %.3f %s ; best=%s beats twin p95=%s"
              % (res["salience_minus_recency"]["delta"], res["salience_minus_recency"]["ci"],
                 res["best_arm"], res["best_beats_twin_p95"]), flush=True)
    else:
        print("  NO ITEMS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
