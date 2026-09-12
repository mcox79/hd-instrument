"""PROBE v4 (strategy, pri-1): ERROR ANATOMY of the grammar resolver's wrong picks -- count, don't narrate.
For each wrong item: gold's rank in the prior ordering; gold's recency rank; pronoun form; sentence distance to gold's
last mention; whether gold was the subject/topic of the previous clause; HEAD-INDIVIDUATION defects (gold cluster split
across several head keys; the pick's head key MERGING several clusters); GUM genre. Accuracy is reported per stratum so
the missing brain mechanism is named by a number, not a story.
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY


def main(predicted_parse=False):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    docs = B1._load_test(None)
    if predicted_parse:
        for doc in docs:
            B4._overlay_predicted(doc)
    rows = []
    for doc in docs:
        name = getattr(doc, "name", "") or getattr(doc, "doc_id", "") or ""
        genre = name.split("_")[1] if "_" in name else name
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        # previous-clause subjects by sentence: sent -> set of head gidx of nsubj tokens
        subj_by_sent = defaultdict(set)
        for t in doc.toks:
            if t.deprel in AER.SUBJ_DEPS:
                subj_by_sent[t.sent].add(t.gidx)
        for t in doc.toks:
            if t.deprel not in B1.UND_DEPRELS or t.gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[t.gidx]; u = mlive[u_mi]; M = doc.mentions[u_mi]
            if M.mtype != "pronoun":
                continue
            gold = M.eid
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            cg = AER.coarg_head_gidx(doc.toks, t)
            coarg = mlive[head_to_mi[cg]]["head"] if (cg is not None and cg in head_to_mi) else None
            ent_hist = defaultdict(list); ent_last = {}; ent_clusters = defaultdict(set); ent_mentions = defaultdict(list)
            for x in cands:
                h = x["head"]
                ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                ent_clusters[h].add(x["cluster"]); ent_mentions[h].append(x)
                if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                    ent_last[h] = x
            ents = list(ent_hist.keys())
            if len(ents) < 2:
                continue
            now = float(u["order"])
            sal = {h: actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents}
            role_of = {h: AER.role_class(gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "")) for h in ents}
            patient_of = {h: (gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "") in AER.PATIENT_DEPS) for h in ents}
            a_role = AER.role_class(t.deprel)
            legal = AER.legal_candidates(ents, coarg)
            sc = {}
            for h in legal:
                s = sal[h]
                if role_of[h] == a_role: s += AER.GAMMA_G
                if patient_of.get(h): s += AER.GAMMA_T
                sc[h] = s
            order = sorted(sc, key=sc.get, reverse=True)
            pick = order[0]
            gold_heads = [h for h in ents if any(x["cluster"] == gold for x in ent_mentions[h])]
            gold_last_heads = [h for h in ents if ent_last[h]["cluster"] == gold]
            hit = int(ent_last[pick]["cluster"] == gold)
            # gold rank by prior (first head whose LAST mention is gold)
            grank = next((i + 1 for i, h in enumerate(order) if ent_last[h]["cluster"] == gold), None)
            # recency rank of gold among ents (by last mention order)
            rec_order = sorted(ents, key=lambda h: -ent_last[h]["order"])
            rrank = next((i + 1 for i, h in enumerate(rec_order) if ent_last[h]["cluster"] == gold), None)
            # sentence distance from pronoun to gold's last mention
            gsent = None
            for h in gold_last_heads:
                hg = mi2headg.get(ent_last[h]["midx"]); tk = gidx2tok.get(hg)
                if tk is not None:
                    gsent = tk.sent if gsent is None else max(gsent, tk.sent)
            dist = (t.sent - gsent) if gsent is not None else None
            # was gold the SUBJECT of the previous sentence (topic continuity)?
            prev_subj_gold = False
            for g in subj_by_sent.get(t.sent - 1, set()):
                mi = head_to_mi.get(g)
                if mi is not None and doc.mentions[mi].eid == gold:
                    prev_subj_gold = True
            # head-individuation defects
            pick_merges = len(ent_clusters[pick]) > 1          # pick's head key mixes clusters
            pick_key_has_gold = gold in ent_clusters[pick]      # the pick's head bucket CONTAINS gold mentions (merge hides gold)
            gold_split = len(gold_heads) > 1                    # gold cluster spread over several head keys
            rows.append({"genre": genre, "form": M.text.lower(), "hit": hit, "grank": grank, "rrank": rrank,
                         "dist": dist, "prev_subj_gold": prev_subj_gold, "pick_merges": pick_merges,
                         "pick_key_has_gold": pick_key_has_gold, "gold_split": gold_split, "n_legal": len(legal),
                         "gold_in_legal": any(ent_last[h]["cluster"] == gold for h in legal),
                         "gold_heads": len(gold_heads), "pick_is_coarg_like": coarg is None})
    n = len(rows); acc = np.mean([r["hit"] for r in rows])
    print(f"items={n} A5={acc:.4f}")
    def strat(key, fn=lambda v: v):
        c = defaultdict(list)
        for r in rows:
            c[fn(r[key])].append(r["hit"])
        out = sorted(((k, len(v), np.mean(v)) for k, v in c.items()), key=lambda x: -x[1])
        print(f"  by {key}: " + " | ".join(f"{k}: n={m} acc={a:.3f}" for k, m, a in out[:12]))
    strat("genre"); strat("form")
    strat("dist", lambda d: ("same-sent" if d == 0 else "prev-sent" if d == 1 else "2-3" if d in (2, 3) else ">=4") if d is not None else "none")
    strat("prev_subj_gold"); strat("pick_key_has_gold"); strat("gold_split"); strat("pick_merges")
    strat("n_legal", lambda k: "2-3" if k <= 3 else "4-8" if k <= 8 else "9-20" if k <= 20 else ">20")
    wrong = [r for r in rows if not r["hit"]]
    print(f"\nWRONG set n={len(wrong)}:")
    print("  gold rank in prior ordering:", Counter(min(r['grank'], 9) if r['grank'] else 'absent' for r in wrong).most_common(10))
    print("  gold recency rank:", Counter(min(r['rrank'], 9) if r['rrank'] else 'absent' for r in wrong).most_common(10))
    print("  pick's head bucket CONTAINS gold mentions (merge hides gold):", sum(r['pick_key_has_gold'] for r in wrong))
    print("  gold cluster split over >1 head key:", sum(r['gold_split'] for r in wrong), " gold absent from legal:", sum(not r['gold_in_legal'] for r in wrong))
    print("  gold was previous-sentence SUBJECT:", sum(r['prev_subj_gold'] for r in wrong), " (right set:", sum(r['prev_subj_gold'] for r in rows if r['hit']), ")")
    print("  forms:", Counter(r['form'] for r in wrong).most_common(8))
    print("  gold last mention distance:", Counter(('same' if r['dist'] == 0 else 'prev' if r['dist'] == 1 else str(r['dist'])) if r['dist'] is not None else 'none' for r in wrong).most_common(8))


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
