"""PROBE v7 (strategy, pri-1): the FORWARD HALF as one incremental engine, THIRD-person items only.
Entity TOKENS (gold-free Heim files, hdlab.online_entity_cluster) accrue EVERY mention: each pronoun in the document is
resolved by the full grammar resolver (Principle B + parallelism + ACT-R) and its mention is written to the picked token
(KTG reviewing+impletion). Sweeps the operating point we do not share with the brain's lab constants (ACT-R clock,
decay) and the FOREGROUND window (Glenberg availability). Oracle (gold tokens, full history) shown for reference only.
Paired CIs vs the incumbent head-bucket resolver on the SAME items.
"""
from __future__ import annotations

import os
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
from hdlab.online_entity_cluster import online_cluster
from experiments.probe_entity_state_residual_gum_v5 import pclass, gn_ok

SEED = 20260912
ROLE_OF_RANK = {0: "SUBJECT", 1: "OBJECT"}


def load(predicted_parse=False):
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
    out = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        out.append((doc, mlive, gaz))
    return out


class Token:
    __slots__ = ("hist", "last", "gender", "number", "cluster_votes", "mentions", "last_np")

    def __init__(self):
        self.hist = []          # (t_order, t_tok, t_sent, role)
        self.last = None        # last mention dict (any)
        self.gender = None; self.number = None
        self.cluster_votes = defaultdict(int)   # gold clusters of NON-pronoun mentions (scoring only)
        self.mentions = []      # (order, role, t_tok, t_sent, gender, number, mention)
        self.last_np = None

    def add(self, m, t_tok, t_sent, role, is_pron):
        self.hist.append((float(m["order"]), float(t_tok), float(t_sent), role))
        self.last = m
        if not is_pron:
            self.mentions.append((float(m["order"]), role, float(t_tok), float(t_sent), m.get("gender") or m.get("name_gender"), m.get("number"), m))
            self.last_np = m
            g = m.get("gender") or m.get("name_gender")
            if g and self.gender is None: self.gender = g
            if m.get("number") and self.number is None: self.number = m.get("number")
            self.cluster_votes[m["cluster"]] += 1

    def cluster(self):
        return max(self.cluster_votes, key=self.cluster_votes.get) if self.cluster_votes else None


def run_engine(data, *, clock="order", decay=DEFAULT_DECAY, window=None, centering=False, hold=None,
               accrue_pronouns=True, oracle=False, tokens_by="files"):
    """Returns list of (hit, form) for THIRD-person undergoer pronoun targets under one configuration."""
    CI = {"order": 0, "tokpos": 1, "sent": 2}[clock]
    results = []
    for doc, mlive, gaz in data:
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        und = {}
        for t in doc.toks:
            if t.deprel in B1.UND_DEPRELS and t.gidx in head_to_mi and doc.mentions[head_to_mi[t.gidx]].mtype == "pronoun":
                und[head_to_mi[t.gidx]] = t
        labels = {} if oracle else online_cluster(mlive, gaz, centering=centering, hold=hold)
        tokens = {}
        def tok_key(m):
            if oracle:
                return ("g", m["cluster"])
            if tokens_by == "heads":
                return ("h", m["head"])
            return ("f", labels.get(m["midx"]))
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            hg = mi2headg.get(mi); tk = gidx2tok.get(hg)
            t_tok = float(hg if hg is not None else m["order"]); t_sent = float(tk.sent if tk is not None else 0)
            role = ROLE_OF_RANK.get(m.get("sent_role_rank", 99), "OTHER")
            dep = gidx2dep.get(hg, "")
            is_pron = m["is_pronoun"] or (M.mtype == "pronoun" and pclass(M.text) == "THIRD")
            if is_pron:
                ug, un = m.get("gender"), m.get("number")
                now = (float(m["order"]), t_tok, t_sent)[CI]
                def _compat(tk_):
                    return [mm for mm in tk_.mentions if gn_ok(ug, un, mm[4], mm[5])]
                cands = [k for k, tk_ in tokens.items() if _compat(tk_)]
                pick = None
                if cands:
                    # Principle B: exclude the co-argument token
                    coarg = None
                    if mi in und:
                        cg = AER.coarg_head_gidx(doc.toks, und[mi])
                        if cg is not None and cg in head_to_mi:
                            cm = mlive[head_to_mi[cg]]
                            coarg = tok_key(cm) if not cm["is_pronoun"] else None
                    legal = [k for k in cands if k != coarg] or cands
                    if window is not None:
                        inwin = [k for k in legal if t_sent - tokens[k].hist[-1][2] <= window]
                        legal = inwin or legal
                    a_role = AER.role_class(dep) if dep else "OBJ"
                    sc = {}
                    for k in legal:
                        T = tokens[k]
                        cm_ = _compat(T)
                        hist = [((mm[0], mm[2], mm[3])[CI], mm[1]) for mm in cm_] + [(h[CI], h[3]) for h in T.hist if h[3] == "PRON"]
                        lastc = max(cm_, key=lambda mm: mm[0])[6]
                        s = actr_activation(hist, now, decay, ROLE_PROMINENCE)
                        s = s if s != float("-inf") else -1e9
                        ldep = gidx2dep.get(mi2headg.get(lastc["midx"]), "")
                        if AER.role_class(ldep) == a_role: s += AER.GAMMA_G
                        if ldep in AER.PATIENT_DEPS: s += AER.GAMMA_T
                        sc[k] = s
                    pick = max(sc, key=sc.get)
                if mi in und and pclass(M.text) == "THIRD":
                    # evaluate only where the incumbent harness would (>=2 gn-compatible prior non-pronoun mentions, >=2 entities)
                    cm = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(m, x)]
                    if len(cm) >= 2 and len(set(x["head"] for x in cm)) >= 2:
                        hit = int(pick is not None and max(_compat(tokens[pick]), key=lambda mm: mm[0])[6]["cluster"] == M.eid)
                        results.append((hit, M.text.lower(), len(cands)))
                if pick is not None and accrue_pronouns:
                    tokens[pick].hist.append((float(m["order"]), float(t_tok), float(t_sent), "PRON"))
                    tokens[pick].last = m
            else:
                k = tok_key(m)
                if k[1] is None:
                    continue
                tokens.setdefault(k, Token()).add(m, t_tok, t_sent, role, False)
    return results


def incumbent(data):
    """The A5 head-bucket resolver on the same THIRD targets (v5 logic), for paired comparison."""
    res = []
    for doc, mlive, gaz in data:
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        for t in doc.toks:
            if t.deprel not in B1.UND_DEPRELS or t.gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[t.gidx]; u = mlive[u_mi]; M = doc.mentions[u_mi]
            if M.mtype != "pronoun" or pclass(M.text) != "THIRD":
                continue
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            ent_hist = defaultdict(list); ent_last = {}
            for x in cands:
                h = x["head"]; ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                if h not in ent_last or x["order"] >= ent_last[h]["order"]: ent_last[h] = x
            ents = list(ent_hist)
            if len(ents) < 2:
                continue
            cg = AER.coarg_head_gidx(doc.toks, t)
            coarg = mlive[head_to_mi[cg]]["head"] if (cg is not None and cg in head_to_mi) else None
            now = float(u["order"])
            sal = {h: actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents}
            role_of = {h: AER.role_class(gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "")) for h in ents}
            patient_of = {h: (gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "") in AER.PATIENT_DEPS) for h in ents}
            pick = AER.resolve(ents, sal, role_of, patient_of, AER.role_class(t.deprel), coarg_key=coarg)
            res.append((int(ent_last[pick]["cluster"] == M.eid), M.text.lower(), len(ents)))
    return res


def main(predicted_parse=False):
    data = load(predicted_parse)
    inc = incumbent(data)
    base = np.array([h for h, _, _ in inc])
    n = len(base)
    rng = np.random.default_rng(SEED)
    print(f"THIRD items={n}  incumbent A5-heads={base.mean():.4f}")

    def ci(res):
        v = np.array([h for h, _, _ in res])
        assert len(v) == n, (len(v), n)
        d = v.astype(float) - base
        boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(2000)])
        lo, hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5)
        flag = "*" if lo > 0 else ("-" if hi < 0 else " ")
        return f"{v.mean():.4f}{flag}[{lo:+.3f},{hi:+.3f}]"

    print("ORACLE tokens (gold clusters, full history):", ci(run_engine(data, oracle=True)),
          "| oracle, no pronoun accrual:", ci(run_engine(data, oracle=True, accrue_pronouns=False)))
    print("\nGold-free tokens (online_cluster), full resolver for every pronoun, accrual on:")
    for centering in (False,):
        for hold in (None, 0.0):
            for clock in ("order", "tokpos", "sent"):
                row = []
                for decay in (1.0, 2.0, 3.0):
                    row.append(f"d={decay}: {ci(run_engine(data, clock=clock, decay=decay, centering=centering, hold=hold))}")
                print(f"  centering={centering} hold={hold} clock={clock:6s} " + " | ".join(row))
    print("\nFOREGROUND window on the best-looking token config (centering=False hold=None):")
    for clock in ("order",):
        row = []
        for w in (None, 1, 2, 3):
            row.append(f"w={w}: {ci(run_engine(data, clock=clock, decay=2.0, window=w))}")
        print(f"  clock={clock:6s} " + " | ".join(row))
    print("\nno pronoun accrual (tokens only):", ci(run_engine(data, accrue_pronouns=False)))
    print("HEAD-BUCKET tokens inside the engine: accrue off", ci(run_engine(data, tokens_by="heads", accrue_pronouns=False)), "| accrue on", ci(run_engine(data, tokens_by="heads")))
    print("HEAD-BUCKET + foreground w=2 sent clock:", ci(run_engine(data, tokens_by="heads", clock="sent", window=2)), "| w=3:", ci(run_engine(data, tokens_by="heads", clock="sent", window=3)), "| order w=2:", ci(run_engine(data, tokens_by="heads", window=2)))


if __name__ == "__main__":
    main(predicted_parse="--predicted" in sys.argv)
