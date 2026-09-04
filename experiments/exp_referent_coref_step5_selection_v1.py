"""STEP-5 (person-selection) prototype + evaluation for the referent->coref frontier.

CONTEXT. Steps 1-4 of pronoun resolution (open the card, feature the card, gate to tracked people,
unify duplicate cards) are near-lossless after the linking pass. The whole remaining gap to a human
(~0.47 vs ~0.9) is STEP 5: picking the right person among several same-gender candidates. This cell
prototypes and BOUNDS the step-5 frontier the brain-foundational way, building on (NOT re-deriving) the
owner-DONE `who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde` PARTIAL, which already:
  - lit-scanned the mechanism (Garrod-Sanford two stages: fast BONDING = agreement+salience/Centering;
    slow RESOLUTION = knowledge-driven, invoked when bonding under-determines);
  - prototyped a LEARNED nonlinear cue-integrator (+0.054 CI-sep on the hardest bucket) and bounded the
    semantic in-text oracle ceiling at 0.857 vs topicality ~0.56 -> the residual needs a rich per-entity
    individuation representation (the priority-1 North Star), NOT a standalone selection tweak.

WHAT THIS ADDS (the unbuilt, buildable piece). The LIVE reader's selection is `EventCentralityReader`
(rolemass + event memory), NOT that integrator. So this cell measures how far the fast BONDING stage --
pure STRUCTURE, no semantics -- can carry step-5 on the general he/she population, by comparing the
brain's structural cues head-to-head over the SAME feature-complete, tracked-people pool, and reads out
the Badecker-Straub / Lewis-Vasishth INTERFERENCE signature (accuracy vs same-gender competitor count).
The point where the best structural selector tops out is exactly where the semantic RESOLUTION stage
(the North Star) becomes load-bearing -- the "what is needed to replicate" answer, measured.

Selectors (all over the identical animacy+gender-gated pool of tracked entities; glass-box, NO LLM):
  RANDOM      info-free twin (pick a compatible person at random)          -- must LOSE.
  RECENCY     nearest compatible entity (Hobbs recency).
  FREQ        most-mentioned compatible entity (global protagonist / topicality).
  CENTERING   Centering Cb: the entity that was SUBJECT most recently (Grosz-Joshi-Weinstein), recency
              tie-break -- the brain's structural bonding pick.
  ORACLE_STRUCT  best of {recency, freq, centering} per item -- the STRUCTURAL ceiling (reachability).

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_step5_selection_v1.py
"""
import json
import math
import os
import random
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, build_pronoun_targets, name_gender_for_span
from hdlab.state_of_mind import infer_nominal_gender, compatible, PRONOUN_SCOPE
from hdlab.animacy_lexicon import lookup_animacy
import experiments.exp_name_entity_clustering_v1 as NC
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

SEED = 20260903


def _docs(n):
    wdw = json.load(open(os.path.join(_REPO, "data/litbank/who_did_what_events.json"), encoding="utf-8"))
    out = []
    for r in wdw:
        p = os.path.join(NC.CONLL_DIR, r["doc"] + ".conll")
        if os.path.exists(p):
            out.append((r["doc"], p))
        if len(out) >= n:
            break
    return out


def _animate(m, gaz):
    g = m.get("gender") or m.get("name_gender")
    if g is None and gaz:
        g = name_gender_for_span(m.get("span_toks", [m["head"]]), gaz)
    if g in ("masc", "fem"):
        return True
    a = lookup_animacy(m["head"], pos_tag=None)
    return bool(a and (a["animacy"] == "animate" or a["category"] == "person"))


def collect(docs, gaz):
    """Replay each doc's mention stream; at each he/she target, snapshot the tracked-entity pool with
    per-entity structural features (recency order, count, last subject sentence) + the gold cluster."""
    items = []
    for _doc, p in docs:
        mentions, n_sents = parse_litbank_conll(p, name_gender_map=gaz)
        targets = build_pronoun_targets(mentions)
        tgt_midx = {t["target"]["midx"] for t in targets}
        ent = {}          # cluster -> dict(count, last_order, last_subj_sent, gender, number)
        order = 0
        for m in mentions:
            if m["is_pronoun"] and m["midx"] in tgt_midx:
                sc = PRONOUN_SCOPE[m["head"]]
                pool = []
                for cl, e in ent.items():
                    if not e["animate"]:
                        continue
                    if not compatible(sc["gender"], sc["number"], e["gender"], e["number"]):
                        continue
                    pool.append((cl, dict(e)))
                if pool:
                    items.append({"gold": m["cluster"], "sent": m["sent_idx"], "order": order,
                                  "pool": pool})
            if not m["is_pronoun"]:
                cl = m["cluster"]
                e = ent.get(cl)
                if e is None:
                    e = {"count": 0, "last_order": -1, "last_subj_sent": -10,
                         "gender": m.get("gender"), "number": m.get("number"),
                         "animate": _animate(m, gaz)}
                    ent[cl] = e
                e["count"] += 1
                e["last_order"] = order
                if e["gender"] is None and m.get("gender") is not None:
                    e["gender"] = m["gender"]
                if m.get("sent_role_rank", 99) == 0:
                    e["last_subj_sent"] = m["sent_idx"]
            order += 1
    return items


def _pick(item, policy, rng):
    pool = item["pool"]
    if policy == "random":
        return rng.choice(pool)[0]
    if policy == "recency":
        return max(pool, key=lambda ce: ce[1]["last_order"])[0]
    if policy == "freq":
        return max(pool, key=lambda ce: (ce[1]["count"], ce[1]["last_order"]))[0]
    if policy == "centering":
        # Centering Cb: most-recently-a-SUBJECT entity; recency of any mention breaks ties.
        return max(pool, key=lambda ce: (ce[1]["last_subj_sent"], ce[1]["last_order"]))[0]
    raise ValueError(policy)


def _oracle_struct(item):
    gold = item["gold"]
    rng = random.Random(0)
    return any(_pick(item, pol, rng) == gold for pol in ("recency", "freq", "centering"))


def _acc(items, policy, seed=SEED):
    rng = random.Random(seed)
    if not items:
        return float("nan"), 0
    return sum(1 for it in items if _pick(it, policy, rng) == it["gold"]) / len(items), len(items)


def _boot(items, policy_a, policy_b, n_boot=1000, seed=SEED):
    rng = random.Random(seed)
    k = len(items)
    ra = random.Random(1); rb = random.Random(2)
    base = (sum(_pick(it, policy_a, ra) == it["gold"] for it in items)
            - sum(_pick(it, policy_b, rb) == it["gold"] for it in items)) / k
    ds = []
    for _ in range(n_boot):
        sel = [rng.randrange(k) for _ in range(k)]
        a = sum(_pick(items[i], policy_a, ra) == items[i]["gold"] for i in sel)
        b = sum(_pick(items[i], policy_b, rb) == items[i]["gold"] for i in sel)
        ds.append((a - b) / k)
    ds.sort()
    lo, hi = ds[int(0.025 * n_boot)], ds[int(0.975 * n_boot)]
    return {"delta": base, "lo": lo, "hi": hi, "ci_sep": (lo > 0 or hi < 0)}


def run(n_docs=100, n_boot=1000):
    gaz = load_given_gazetteer()
    items = collect(_docs(n_docs), gaz)
    hard = [it for it in items if len(it["pool"]) >= 2]      # >=2 same-gender competitors (bonding under-determines)
    print("=" * 84)
    print("STEP-5 SELECTION over the tracked-person pool  (%d docs)" % n_docs)
    print("  all he/she targets with a pool: %d   |   HARD (>=2 same-gender competitors): %d (%.0f%%)"
          % (len(items), len(hard), 100 * len(hard) / max(1, len(items))))
    print("-" * 84)
    for name, subset in (("ALL", items), ("HARD (>=2 competitors)", hard)):
        print("  %s:" % name)
        for pol in ("random", "recency", "freq", "centering"):
            a, n = _acc(subset, pol)
            print("     %-10s %.4f" % (pol, a))
        oc = sum(_oracle_struct(it) for it in subset) / max(1, len(subset))
        print("     %-10s %.4f   <- best structural cue per item (STRUCTURAL CEILING)" % ("oracle*", oc))
    print("-" * 84)
    best = max(("recency", "freq", "centering"), key=lambda p: _acc(hard, p)[0])
    d_tw = _boot(hard, best, "random", n_boot)
    d_rc = _boot(hard, "centering", "recency", n_boot)
    print("  HARD: best structural selector = %s" % best)
    print("  %-22s : %+.4f CI[%+.4f,%+.4f] ci_sep=%s" %
          ("best - random(twin)", d_tw["delta"], d_tw["lo"], d_tw["hi"], d_tw["ci_sep"]))
    print("  %-22s : %+.4f CI[%+.4f,%+.4f] ci_sep=%s" %
          ("centering - recency", d_rc["delta"], d_rc["lo"], d_rc["hi"], d_rc["ci_sep"]))
    print("-" * 84)
    print("  INTERFERENCE signature (Badecker-Straub / Lewis-Vasishth: acc falls as competitors rise):")
    for lo, hi in ((1, 1), (2, 2), (3, 4), (5, 99)):
        sub = [it for it in items if lo <= len(it["pool"]) <= hi]
        if sub:
            ac, _ = _acc(sub, best if best else "centering")
            oc = sum(_oracle_struct(it) for it in sub) / len(sub)
            print("     %d%s competitors: n=%-4d  %s=%.3f  struct-ceiling=%.3f"
                  % (lo, ("" if lo == hi else "-%d" % hi if hi < 99 else "+"), len(sub), best, ac, oc))
    print("=" * 84)
    return {"n": len(items), "n_hard": len(hard),
            "hard_acc": {p: _acc(hard, p)[0] for p in ("random", "recency", "freq", "centering")},
            "hard_struct_ceiling": sum(_oracle_struct(it) for it in hard) / max(1, len(hard))}


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
