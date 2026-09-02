"""exp_world_state_grouping_optimize_v1 -- OPTIMIZATION lever A (the biggest structural one): how much of the
he/she densification's grouping headroom (reader overlay 0.38 -> gold grouping 0.72) can a GLASS-BOX entity
grouping recover? Isolates ENTITY GROUPING (which mentions are the same entity) from the PICK (graded retrieval),
by running the SAME graded pick over three grouping schemes:
  surface : each distinct lowercased nominal HEAD is an entity (the reader's base overlay -- fragments name variants
            'Miss Bennet'/'Elizabeth'/'Bennet' into 3).
  aliaser : hdlab.coref.build_merge_map (the LANDED glass-box EntityAliaser) unifies proper-name variants into ONE
            canonical entity; non-name nominals by head. NO gold.
  gold     : gold coref clusters (the upper bound).
Graded (hdlab.graded_coref_pick) picks the antecedent entity; scored anti-circularly (the picked entity -> its gold
cluster via a head->majority-cluster side-map; correct = target's gold cluster). PINNED reuse; NO spaCy/LLM.
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
from collections import defaultdict, Counter

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_world_state_he_she_ceiling_v1 import role_of, MASC, FEM

ANCHOR = "world_state_grouping_optimize_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
LITBANK_DIR = os.path.join(REPO, "data", "corpora", "litbank_coref_conll")


def _gender_of(m):
    return m.get("gender") or m.get("name_gender")


def _entity_maps(mentions):
    """Return, per scheme, a dict: entity_key -> ordered list of member mentions (each a mention dict). Pronouns
    are NOT entity-creating in any scheme (they advance the stream but do not anchor an entity)."""
    from hdlab.coref import build_merge_map
    surface, aliaser, gold, gold_nom = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    midx_to_canon, _c2m, _st = build_merge_map(mentions, use_gazetteer=True)
    for m in mentions:
        gold[m["cluster"]].append(m)                       # gold: by cluster (incl. pronoun mentions = pronoun-chaining)
        if m["is_pronoun"]:
            continue
        gold_nom[m["cluster"]].append(m)                   # gold grouping but NOMINAL-only history (no pronoun chains)
        surface[m["head"]].append(m)
        canon = midx_to_canon.get(m["midx"])
        aliaser[canon if canon is not None else ("H::" + m["head"])].append(m)
    return {"surface": surface, "aliaser": aliaser, "gold_nom": gold_nom, "gold": gold}


def _entity_gender(members):
    gs = [_gender_of(m) for m in members]
    gs = [g for g in gs if g in ("masc", "fem")]
    return (max(set(gs), key=gs.count) if gs else None)


def build_head2cluster(mentions):
    c = defaultdict(Counter)
    for m in mentions:
        if not m["is_pronoun"]:
            c[m["head"]][m["cluster"]] += 1
    return {h: cc.most_common(1)[0][0] for h, cc in c.items()}


def entity_gold_cluster(members, head2cl):
    """majority gold cluster of an entity's member mentions (anti-circular scoring side-map)."""
    cc = Counter(m["cluster"] for m in members)
    return cc.most_common(1)[0][0]


def run_doc(path, scheme_acc):
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets, load_name_gender
    from hdlab.graded_coref_pick import graded_antecedent_pick, keep_after_pool_cleanup
    gaz = load_name_gender()
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    if not mentions:
        return
    ent_maps = _entity_maps(mentions)
    head2cl = build_head2cluster(mentions)
    for tgt in build_pronoun_targets(mentions):
        P = tgt["target"]
        g_p = "masc" if P["head"] in MASC else ("fem" if P["head"] in FEM else None)
        if g_p is None:
            continue
        m_p = P["midx"]
        gold = P["cluster"]
        for scheme, emap in ent_maps.items():
            cand_priors, cand_goldcl, cand_heads = [], [], []
            for ekey, members in emap.items():
                priors = [(mm["sent_idx"], role_of(mm)) for mm in members if mm["midx"] < m_p]
                if not priors:
                    continue
                if _entity_gender(members) not in (g_p, None):
                    continue
                cand_priors.append(priors)
                cand_goldcl.append(entity_gold_cluster([mm for mm in members if mm["midx"] < m_p], head2cl))
                cand_heads.append([mm["head"] for mm in members if mm["midx"] < m_p])
            if not cand_priors:
                continue
            keep = keep_after_pool_cleanup(cand_heads)
            kp = [cand_priors[i] for i in keep] or cand_priors
            kg = [cand_goldcl[i] for i in keep] or cand_goldcl
            g = graded_antecedent_pick(kp, p_sent=P["sent_idx"], pron_role=role_of(P))
            pick_cluster = kg[g["pick"]] if g["pick"] >= 0 else None
            scheme_acc[scheme].append(int(pick_cluster == gold))


def boot(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return {"acc": None, "ci": [None, None], "n": 0}
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    return {"acc": round(float(vals.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": len(vals)}


def run(mode="full", n_boot=2000, seed=20260902):
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    if mode == "smoke":
        files = files[:6]
    scheme_acc = {"surface": [], "aliaser": [], "gold_nom": [], "gold": []}
    for f in files:
        run_doc(f, scheme_acc)
    res = {"anchor": ANCHOR, "mode": mode, "n_docs": len(files)}
    for s in ("surface", "aliaser", "gold_nom", "gold"):
        res[s] = boot(scheme_acc[s], n_boot, seed + hash(s) % 500)
    # paired aliaser-minus-surface (does the glass-box aliaser recover grouping headroom?)
    if scheme_acc["surface"]:
        a = np.asarray(scheme_acc["aliaser"], float); su = np.asarray(scheme_acc["surface"], float)
        n = min(len(a), len(su))
        d = a[:n] - su[:n]
        rng = np.random.default_rng(seed + 9)
        bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
        res["aliaser_minus_surface"] = {"delta": round(float(d.mean()), 4),
                                        "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}
        gap = res["gold"]["acc"] - res["surface"]["acc"]
        recov = (res["aliaser"]["acc"] - res["surface"]["acc"]) / gap if gap else None
        res["grouping_headroom_gold_minus_surface"] = round(gap, 4)
        res["aliaser_fraction_of_headroom_recovered"] = round(recov, 3) if recov is not None else None
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    # aliaser unifies a name variant it CAN (shared token): full name 'Elizabeth Bennet' then 'Elizabeth' -> ONE
    # entity (surface grouping would keep 'elizabeth bennet' head 'bennet' vs 'elizabeth' as two).
    from hdlab.coref import build_merge_map
    ms = [{"midx": 0, "is_pronoun": False, "head": "bennet", "span_toks": ["Elizabeth", "Bennet"], "gender": None, "name_gender": "fem", "cluster": 1},
          {"midx": 1, "is_pronoun": False, "head": "elizabeth", "span_toks": ["Elizabeth"], "gender": None, "name_gender": "fem", "cluster": 1}]
    m2c, _c, _s = build_merge_map(ms, use_gazetteer=True)
    unified = len(set(m2c.values())) == 1 and len(m2c) == 2
    print("[self-test] aliaser unifies 'Elizabeth Bennet' + 'Elizabeth' -> one entity: %s (%s)" % (unified, m2c), flush=True)
    return 0 if unified else 1


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
    print("\n  GROUPING optimization (graded pick over each grouping; LitBank he/she, %d docs):" % res["n_docs"], flush=True)
    for s in ("surface", "aliaser", "gold_nom", "gold"):
        print("  %-9s %.3f %s (n=%d)" % (s, res[s]["acc"], res[s]["ci"], res[s]["n"]), flush=True)
    if res.get("gold") and res.get("gold_nom"):
        print("  decomposition: name-unification(aliaser-surface)=%.3f | perfect-nominal(gold_nom-aliaser)=%.3f | pronoun-chaining(gold-gold_nom)=%.3f"
              % (res["aliaser"]["acc"] - res["surface"]["acc"], res["gold_nom"]["acc"] - res["aliaser"]["acc"],
                 res["gold"]["acc"] - res["gold_nom"]["acc"]), flush=True)
    if "aliaser_minus_surface" in res:
        print("  aliaser-surface %.3f %s | headroom(gold-surface)=%.3f | aliaser recovers %.0f%% of it"
              % (res["aliaser_minus_surface"]["delta"], res["aliaser_minus_surface"]["ci"],
                 res["grouping_headroom_gold_minus_surface"], 100 * (res["aliaser_fraction_of_headroom_recovered"] or 0)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
