"""exp_commonnoun_linktype_decomposition_v1 -- WHERE EXACTLY is the common-noun coref signal lost, and
which of it is recoverable by a buildable FOUNDATION asset vs a genuine ONLINE world-model dependency?

Drills the located negative (form_a_discourse_referent... : a faithful cue-based former ties surface-head;
head-match recall 0.341). For every GOLD common-noun coreference link (a common-noun non-pronoun mention m
with a nearest prior same-cluster non-pronoun antecedent `ante`), categorize the LINK by the knowledge it
requires, and measure per category whether pure ACCESSIBILITY (most-recent gender/number-compatible person
referent) recovers it and how much AMBIGUITY (competing compatible referents) intervenes:

  head_identical   m and ante share the head lemma            -> surface-head recovers (no knowledge).
  name_antecedent  ante is a proper NAME ("Elizabeth"->"the girl") -> accessibility to a named referent.
  wordnet_bridge   not head-id, both person-denoting, WordNet best-sense hypernym/synonym compatible
                   ("the fellow"->"the man", "the girl"->"the child") -> STATIC lexical-taxonomy asset.
  kinship_role     m or ante is a kinship / social-role noun ("her father", "the Squire", "the servant")
                   -> RELATIONAL/SCHEMA knowledge (whose father? which servant?).
  residual         none of the above -> the situation-model / deep world-knowledge boundary.

The AMBIGUITY column (mean # of DISTINCT other compatible person referents more recent than the true
antecedent) is the precise SITUATION-MODEL dependency: 0 = pure recency/decay recovers it; >0 = only a
world-model of WHO IS ACTIVE disambiguates it -- exactly the over-merge the faithful former could not cross.

Glass-box, NO LLM. WordNet is a static offline foundation asset. hdlab READ-only. ASCII. own dir.
Run: .venv/Scripts/python.exe experiments/exp_commonnoun_linktype_decomposition_v1.py --self-test
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, json, time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK

OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_linktype_decomposition_v1")
head_lemma = DIAG.head_lemma
is_name = DIAG.is_name

# a compact STATIC kinship / social-role person lexicon (a buildable foundation asset; general English +
# 19c prose -- NOT derived from LitBank characters). These are person nouns whose reference is RELATIONAL.
KINSHIP_ROLE = frozenset("""
father mother son daughter brother sister husband wife parent child uncle aunt cousin nephew niece
grandfather grandmother grandson granddaughter widow widower stepfather stepmother
master mistress servant maid maidservant manservant butler footman valet nurse governess housekeeper
cook groom coachman steward tenant landlord landlady
lord lady sir madam gentleman gentlewoman king queen prince princess duke duchess earl countess baron
squire knight parson vicar rector curate priest doctor captain colonel major general sergeant
friend companion lover mistress neighbour neighbor stranger guest visitor
""".split())


def wn_bridge(hl_a, hl_b, thr=0.20):
    """best-sense WordNet person hypernym/synonym compatibility (a static offline lexical asset). Generous
    (oracle ceiling of lexical bridging): ancestor relation OR path_similarity >= thr on the person senses."""
    if hl_a == hl_b:
        return True
    sa, sb = LK.person_synset(hl_a), LK.person_synset(hl_b)
    if sa is None or sb is None:
        return False
    if sa == sb:
        return True
    if sa in sb.closure(lambda x: x.hypernyms()) or sb in sa.closure(lambda x: x.hypernyms()):
        return True
    ps = sa.path_similarity(sb)
    return ps is not None and ps >= thr


def _num(m):
    return LK._num_of(m)


def decompose(docs, gaz, window=8):
    cats = ["head_identical", "name_antecedent", "wordnet_bridge", "kinship_role", "residual"]
    stat = {c: {"n": 0, "access_recovers": 0, "ambiguity_sum": 0, "ambig0": 0} for c in cats}
    n_links = 0
    for doc, ms in docs:
        by_cluster = defaultdict(list)
        for m in ms:
            by_cluster[m["cluster"]].append(m)
        noms = [m for m in ms if not m["is_pronoun"]]
        noms.sort(key=lambda m: m["midx"])
        # active person referents as we stream (for accessibility/ambiguity): list of (last_sent, hl, gender, num, cluster, is_name)
        active = []
        prior_in_cluster = defaultdict(list)
        for m in noms:
            hl = head_lemma(m["head"]); g = m.get("gender") or m.get("name_gender"); num = _num(m)
            person = LK.person_synset(hl) is not None or is_name(m, gaz)
            pri = prior_in_cluster.get(m["cluster"], [])
            # a LINK only exists for a common-noun mention with a prior same-cluster non-pron antecedent
            if (not is_name(m, gaz)) and person and pri:
                ante = pri[-1]
                ahl = head_lemma(ante["head"])
                if ahl == hl:
                    cat = "head_identical"
                elif is_name(ante, gaz):
                    cat = "name_antecedent"
                elif wn_bridge(hl, ahl):
                    cat = "wordnet_bridge"
                elif hl in KINSHIP_ROLE or ahl in KINSHIP_ROLE:
                    cat = "kinship_role"
                else:
                    cat = "residual"
                n_links += 1
                stat[cat]["n"] += 1
                # accessibility: is `ante` the most-recent compatible person referent within window? and
                # how many DISTINCT other compatible person referents are MORE recent than ante (ambiguity)?
                si = m["sent_idx"]
                comp = [a for a in active if (si - a[0]) <= window
                        and LK._gender_ok(g, a[2]) and LK._number_ok(num, a[3])]
                ante_cl = ante["cluster"]
                more_recent_other = {a[4] for a in comp if a[4] != ante_cl and a[0] >= _last_sent(active, ante_cl)}
                amb = len(more_recent_other)
                # accessibility recovers iff no other compatible referent is strictly more recent than ante
                if amb == 0 and any(a[4] == ante_cl for a in comp):
                    stat[cat]["access_recovers"] += 1
                    stat[cat]["ambig0"] += 1
                else:
                    stat[cat]["ambiguity_sum"] += amb
            prior_in_cluster[m["cluster"]].append(m)
            if person:
                active.append((m["sent_idx"], hl, g, num, m["cluster"], is_name(m, gaz)))
    # finalize fractions
    out = {}
    for c in cats:
        s = stat[c]; n = s["n"]
        out[c] = {"n": n, "frac_of_links": round(n / max(1, n_links), 4),
                  "access_recovers": s["access_recovers"],
                  "access_recovery_rate": round(s["access_recovers"] / max(1, n), 4),
                  "mean_ambiguity_when_missed": round(s["ambiguity_sum"] / max(1, n - s["ambig0"]), 3)}
    return {"n_links": n_links, "window": window, "categories": out}


def _last_sent(active, cluster):
    ss = [a[0] for a in active if a[4] == cluster]
    return max(ss) if ss else -1


def run(n=None, window=8):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    docs, gaz = DIAG.load_docs(n)
    res = decompose(docs, gaz, window=window)
    res["n_docs"] = len(docs); res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_linktype_decomposition_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    print("=" * 92)
    print("WHERE THE COMMON-NOUN COREF SIGNAL GOES  (%d docs, %d gold common-noun links, window=%d)"
          % (res["n_docs"], res["n_links"], res["window"]))
    print("  %-16s %7s %8s | %-14s %-24s" % ("category", "n", "frac", "access_recovery", "mean_ambiguity_when_missed"))
    order = ["head_identical", "name_antecedent", "wordnet_bridge", "kinship_role", "residual"]
    for c in order:
        s = res["categories"][c]
        print("  %-16s %7d %8.4f | %-14.4f %-.3f"
              % (c, s["n"], s["frac_of_links"], s["access_recovery_rate"], s["mean_ambiguity_when_missed"]))
    non_head = 1 - res["categories"]["head_identical"]["frac_of_links"]
    print("  " + "-" * 88)
    print("  NON-head-match links = %.3f of all links; of those the buildable STATIC assets tag: "
          "name-antecedent + wordnet_bridge + kinship_role" % non_head)
    print("=" * 92)


def self_test():
    assert wn_bridge("man", "man") is True
    assert wn_bridge("man", "table") is False
    res = run(n=8, window=8)
    assert res["n_links"] > 0 and abs(sum(c["frac_of_links"] for c in res["categories"].values()) - 1.0) < 0.02
    print("[self-test] PASS (%d links over 8 docs)" % res["n_links"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--window", type=int, default=8)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    _print(run(n=a.n, window=a.window))


if __name__ == "__main__":
    main()
