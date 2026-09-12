"""PROBE v5 (strategy, pri-1): split the slice by PRONOUN CLASS (the brain uses different machines) and measure the
ENTITY-TOKEN INDIVIDUATION prize with a full mention history (the forward half of the coref two-half machine).

Classes: THIRD = third-person personal pronouns (it/he/she/him/her/they/them + possessives) -> discourse-entity
resolution (this problem); DEICTIC = I/me/you/we/us -> speech-situation (speaker/addressee) model; DEMONSTRATIVE =
this/that/these/those -> abstract/event anaphora; OTHER.

Arms (all over the same items; candidate = an ENTITY TOKEN, not a head-lemma bucket):
  A5-heads        the landed resolver as measured (head-lemma buckets, non-pronoun history)          [incumbent]
  A5-files        gold-free online entity files (hdlab.online_entity_cluster.online_cluster: Heim file-change,
                  ACT-R selection) as the tokens; history = the file's non-pronoun mentions
  A5-files+pron   the same files, plus INCREMENTAL pronoun resolution: every earlier pronoun in the document is
                  resolved by the same resolver and its mention is added to the picked file's history (the entity
                  token accrues ALL its mentions -- the brain's file is updated at every reference)
  ORACLE-cluster  gold clusters as tokens with full history (incl. pronouns): the individuation CEILING (a probe
                  control, never a deployment arm)
Reports n/acc per class x arm, paired CIs vs A5-heads, and the in-focus (top-k) ceilings for the THIRD class.
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.state_of_mind import PRONOUN_SCOPE
from hdlab.online_entity_cluster import online_cluster

SEED = 20260912
DEICTIC = {"i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself", "yourselves", "we", "us", "our", "ours", "ourselves"}
DEMONSTR = {"this", "that", "these", "those"}


def pclass(form: str) -> str:
    f = form.lower()
    if f in PRONOUN_SCOPE or f in {"himself", "herself", "itself", "themselves"}:
        return "THIRD"
    if f in DEICTIC:
        return "DEICTIC"
    if f in DEMONSTR:
        return "DEMONSTR"
    return "OTHER"


def gn_ok(ug, un, g, nmb):
    if ug and g and ug != g:
        return False
    if un and nmb and un != nmb:
        return False
    return True


def main(predicted_parse=False):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    try:
        import experiments.exp_name_entity_clustering_v1 as NEC
        gaz = NEC.load_given_gazetteer()
    except Exception:
        gaz = None
    docs = B1._load_test(None)
    if predicted_parse:
        for doc in docs:
            B4._overlay_predicted(doc)
    ARMS = ("A5_heads", "A5_files", "A5_files_pron", "ORACLE_cluster")
    rows = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        labels = online_cluster(mlive, gaz)                      # gold-free entity files over non-pronoun mentions
        # per-file incremental state (built in document order); pronoun histories appended as we go
        file_hist = defaultdict(list); file_last = {}; file_g = {}; file_n = {}
        pron_hist = defaultdict(list)                            # extra history from resolved pronouns (files+pron arm)
        gold_hist = defaultdict(list); gold_last = {}; gold_g = {}; gold_n = {}   # ORACLE tokens
        # walk mentions in order; at each UNDERGOER pronoun target, evaluate all arms with the state so far
        und_targets = {}
        for t in doc.toks:
            if t.deprel in B1.UND_DEPRELS and t.gidx in head_to_mi and doc.mentions[head_to_mi[t.gidx]].mtype == "pronoun":
                und_targets[head_to_mi[t.gidx]] = t
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            role = B1._role(m.get("sent_role_rank", 2))
            dep = gidx2dep.get(mi2headg.get(mi), "")
            if mi in und_targets and M.mtype == "pronoun":
                t = und_targets[mi]
                u = m
                gold = M.eid
                ug, un = u.get("gender"), u.get("number")
                cg = AER.coarg_head_gidx(doc.toks, t)
                cands_m = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
                a_role = AER.role_class(t.deprel)
                rec = {"form": M.text, "cls": pclass(M.text), "gold": gold}
                if len(cands_m) >= 2:
                    # ---- A5-heads (incumbent) ----
                    ent_hist = defaultdict(list); ent_last = {}
                    for x in cands_m:
                        h = x["head"]; ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                        if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                            ent_last[h] = x
                    ents = list(ent_hist)
                    if len(ents) >= 2:
                        now = float(u["order"])
                        sal = {h: actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents}
                        role_of = {h: AER.role_class(gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "")) for h in ents}
                        patient_of = {h: (gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "") in AER.PATIENT_DEPS) for h in ents}
                        coarg = mlive[head_to_mi[cg]]["head"] if (cg is not None and cg in head_to_mi) else None
                        legal = AER.legal_candidates(ents, coarg)
                        sc = {}
                        for h in legal:
                            s = sal[h]
                            if role_of[h] == a_role: s += AER.GAMMA_G
                            if patient_of.get(h): s += AER.GAMMA_T
                            sc[h] = s
                        order_h = sorted(sc, key=sc.get, reverse=True)
                        rec["A5_heads"] = int(ent_last[order_h[0]]["cluster"] == gold)
                        rec["heads_topk"] = [int(any(ent_last[h]["cluster"] == gold for h in order_h[:k])) for k in (1, 2, 3, 4)]
                        # ---- A5-files / A5-files+pron ----
                        def files_arm(extra):
                            fids = [f for f in file_hist if gn_ok(ug, un, file_g.get(f), file_n.get(f))]
                            if len(fids) < 2:
                                return None
                            hist = {f: file_hist[f] + (extra[f] if extra is not None else []) for f in fids}
                            salf = {f: actr_activation(sorted(hist[f]), now, DEFAULT_DECAY, ROLE_PROMINENCE) for f in fids}
                            rolef = {f: AER.role_class(gidx2dep.get(mi2headg.get(file_last[f]["midx"]), "")) for f in fids}
                            patf = {f: (gidx2dep.get(mi2headg.get(file_last[f]["midx"]), "") in AER.PATIENT_DEPS) for f in fids}
                            coargf = labels.get(head_to_mi[cg]) if (cg is not None and cg in head_to_mi) else None
                            legalf = AER.legal_candidates(fids, coargf)
                            scf = {}
                            for f in legalf:
                                s = salf[f]
                                if rolef[f] == a_role: s += AER.GAMMA_G
                                if patf.get(f): s += AER.GAMMA_T
                                scf[f] = s
                            pick = max(scf, key=scf.get)
                            return pick
                        pf = files_arm(None)
                        rec["A5_files"] = int(file_last[pf]["cluster"] == gold) if pf is not None else None
                        pfp = files_arm(pron_hist)
                        rec["A5_files_pron"] = int(file_last[pfp]["cluster"] == gold) if pfp is not None else None
                        # ---- ORACLE cluster tokens with full history ----
                        gids = [g for g in gold_hist if g in gold_last and gn_ok(ug, un, gold_g.get(g), gold_n.get(g))]
                        if len(gids) >= 2:
                            salg = {g: actr_activation(sorted(gold_hist[g]), now, DEFAULT_DECAY, ROLE_PROMINENCE) for g in gids}
                            roleg = {g: AER.role_class(gidx2dep.get(mi2headg.get(gold_last[g]["midx"]), "")) for g in gids}
                            patg = {g: (gidx2dep.get(mi2headg.get(gold_last[g]["midx"]), "") in AER.PATIENT_DEPS) for g in gids}
                            coargg = mlive[head_to_mi[cg]]["cluster"] if (cg is not None and cg in head_to_mi) else None
                            legalg = AER.legal_candidates(gids, coargg)
                            scg = {}
                            for g in legalg:
                                s = salg[g]
                                if roleg[g] == a_role: s += AER.GAMMA_G
                                if patg.get(g): s += AER.GAMMA_T
                                scg[g] = s
                            pg = max(scg, key=scg.get)
                            rec["ORACLE_cluster"] = int(pg == gold)
                        rows.append(rec)
                        # the files+pron arm: this pronoun's own mention accrues to its picked file
                        if pfp is not None:
                            pron_hist[pfp].append((float(m["order"]), role))
            elif m["is_pronoun"] and mi not in und_targets:
                # a non-target pronoun: resolve it with the resolver over files (no gold) and accrue to the file
                ug, un = m.get("gender"), m.get("number"); now = float(m["order"])
                fids = [f for f in file_hist if gn_ok(ug, un, file_g.get(f), file_n.get(f))]
                if fids:
                    hist = {f: file_hist[f] + pron_hist[f] for f in fids}
                    salf = {f: actr_activation(sorted(hist[f]), now, DEFAULT_DECAY, ROLE_PROMINENCE) for f in fids}
                    pick = max(fids, key=lambda f: salf[f])
                    pron_hist[pick].append((now, role))
            # update gold tokens with EVERY mention (oracle)
            g = m["cluster"]
            gold_hist[g].append((float(m["order"]), role))
            if not m["is_pronoun"]:
                gold_last[g] = m
                if m.get("gender") or m.get("name_gender"): gold_g.setdefault(g, m.get("gender") or m.get("name_gender"))
                if m.get("number"): gold_n.setdefault(g, m.get("number"))
            # update files with this non-pronoun mention
            if not m["is_pronoun"] and mi in labels:
                f = labels[mi]
                file_hist[f].append((float(m["order"]), role)); file_last[f] = m
                if m.get("gender") or m.get("name_gender"): file_g.setdefault(f, m.get("gender") or m.get("name_gender"))
                if m.get("number"): file_n.setdefault(f, m.get("number"))

    rng = np.random.default_rng(SEED)
    def report(sub, label):
        n = len(sub)
        if n == 0:
            return
        print(f"\n{label}: n={n}")
        for a in ARMS:
            v = [r[a] for r in sub if r.get(a) is not None]
            print(f"  {a:15s} acc={np.mean(v):.4f} (n={len(v)})")
        base = np.array([r["A5_heads"] for r in sub])
        for a in ARMS[1:]:
            pairs = [(r[a], r["A5_heads"]) for r in sub if r.get(a) is not None]
            d = np.array([x - y for x, y in pairs], dtype=float)
            if len(d) == 0: continue
            boots = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)])
            print(f"  {a} - A5_heads: {d.mean():+.4f} CI95 [{np.percentile(boots,2.5):+.4f}, {np.percentile(boots,97.5):+.4f}] (n={len(d)})")
        tk = np.array([r["heads_topk"] for r in sub])
        print("  A5-heads in-focus ceiling top-1..4:", [round(float(x), 4) for x in tk.mean(axis=0)])
    print(f"items={len(rows)} (all classes) A5_heads={np.mean([r['A5_heads'] for r in rows]):.4f}")
    from collections import Counter
    print("class counts:", Counter(r["cls"] for r in rows))
    for c in ("THIRD", "DEICTIC", "DEMONSTR", "OTHER"):
        report([r for r in rows if r["cls"] == c], c)
    report(rows, "ALL")


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
