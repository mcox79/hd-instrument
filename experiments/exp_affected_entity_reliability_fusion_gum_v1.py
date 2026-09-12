"""SITUATION-MODEL MILESTONE 2 (BF): RELIABILITY-WEIGHTED FUSION of the forward salience prior with the
selectional/type-coherence likelihood, on the affected-ENTITY (who-was-affected) task.

WHY (measured). Milestone 1 showed the FORWARD SALIENCE PRIOR (ACT-R/Centering over discourse referents) beats the
recency floor +0.27 CI-sep on pronoun undergoers. The brain does not use salience alone: it fuses the salience PRIOR
with the coherence LIKELIHOOD (Kehler-Rohde Bayesian pronoun resolution), and it weights each cue by its RELIABILITY,
not a fixed constant (Ernst-Banks 2002 optimal cue integration; Ma-Beck-Latham-Pouget probabilistic population codes
-> inverse-variance weighting). Our prior selectional-organ ceiling was EXACTLY a fixed-weight failure: a strong type
prior swamped the weaker-but-correct discourse cue. THE FIX = reliability-weighted product-of-experts (the substrate's
BF_SPIRIT `convergent_cue_reader.intrinsic_gain_w`), applied per decision.

THE BUILD. For each pronoun undergoer of verb V, over gender/number-compatible candidate discourse ENTITIES
(online, gold-free, head-individuated):
  s_sal(e)  = ACT-R base-level activation ln( sum_k w(role_k) dt_k^-decay )        [forward salience prior]
  s_coh(e)  = Resnik typed selectional association A(V, supersense(head(e)))       [coherence/type likelihood]
  reliability gains g_sal, g_coh = the per-decision MARGIN (top1-top2) of each cue's own softmax distribution
  w = intrinsic_gain_w(g_sal, g_coh)     (log1p(g_coh)/log1p(g_sal); sem up-weighted only when it is the sharper cue)
  fused pick = argmax_e [ log softmax(s_sal) + w * log softmax(s_coh) ]            [reliability-weighted PoE]
Compare FUSED vs SALIENCE-ALONE vs COHERENCE-ALONE, affected-entity accuracy, matched population, paired CI.

CONTROLS: coherence-alone must be WEAK (the ambiguity wall -- guards against the DMV-43 trap that structure/type
needs the prior); fixed-weight PoE (w=const) as an ABLATION -- reliability-weighting must beat or equal it and must
NOT regress salience-alone (the fixed-weight ceiling); info-free twin; no-leak (gold eid only scores).

Reuses BF organs: salience_binder (BF), typed selectional preference organ, convergent_cue_reader (BF_SPIRIT), the
GUM reader + the milestone-1 undergoer JOIN. NO external LLM. Glass-box. ASCII.
"""
from __future__ import annotations

import math
import os
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_typed_selectional_preference_v1 as TSP
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
import hdlab.convergent_cue_reader as CCR

SEED = 20260910
UND = B1.UND_DEPRELS


def _verb_lemma_for_undergoer(doc, tok):
    """The governing verb lemma of an undergoer token (its within-sentence head)."""
    for t in doc.toks:
        if t.sent == tok.sent and t.idx == tok.head:
            return (t.lemma or t.form).lower()
    return None


def _undergoer_verbs(doc):
    """{global_head_idx: verb_lemma} for undergoer tokens -> lets us attach V to the joined mention."""
    out = {}
    for t in doc.toks:
        if t.deprel in UND:
            vl = _verb_lemma_for_undergoer(doc, t)
            if vl:
                out[t.gidx] = vl
    return out


def _softmax(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return x
    e = np.exp(x - x.max())
    return e / (e.sum() + 1e-12)


def _margin(p):
    """top1 - top2 of a distribution = a per-decision reliability/sharpness gain."""
    if len(p) < 2:
        return 1.0
    s = np.sort(p)[::-1]
    return float(s[0] - s[1])


def run(limit=None):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    import hdlab.coref as COREF
    import hdlab.unified_referent as UR
    import random
    rng = random.Random(SEED)
    tsp = TSP.TypedSelectionalPreference().fit()
    docs = B1._load_test(limit)
    times_key = "order"
    rows = []            # per matched pronoun undergoer: {sal, coh, fused, fused_fixed, unified, gold_hit...}
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        uverbs = _undergoer_verbs(doc)
        # the real organ's pick per pronoun target (the milestone-1 deployment salience)
        uni_correct = {}
        try:
            for rec in UR.resolve_unified_stream(mlive, COREF.build_pronoun_targets(mlive)):
                uni_correct[rec["target_midx"]] = int(bool(rec.get("correct")))
        except Exception:
            pass
        for gidx, vl in uverbs.items():
            if gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[gidx]
            u = mlive[u_mi]
            M = doc.mentions[u_mi]
            if M.mtype != "pronoun":
                continue
            gold_eid = M.eid
            # candidate ENTITIES: prior non-pronoun, gn-compatible; grouped online by head
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            ent_hist = defaultdict(list); ent_last = {}
            for x in cands:
                h = x["head"]
                ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                    ent_last[h] = x
            ents = list(ent_hist.keys())
            if len(ents) < 2:
                continue
            now = float(u["order"])
            s_sal = np.array([actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents])
            s_coh = np.array([(tsp.score(vl, h) if tsp.score(vl, h) is not None else 0.0) for h in ents])
            p_sal, p_coh = _softmax(s_sal), _softmax(s_coh * 4.0)
            g_sal, g_coh = _margin(p_sal), _margin(p_coh)
            w = CCR.intrinsic_gain_w(g_sal, g_coh)
            fused = np.log(p_sal + 1e-12) + w * np.log(p_coh + 1e-12)
            fused_fixed = np.log(p_sal + 1e-12) + 1.0 * np.log(p_coh + 1e-12)   # fixed-weight ablation

            def hit(scores):
                return int(ent_last[ents[int(np.argmax(scores))]]["cluster"] == gold_eid)
            rows.append({
                "sal": hit(s_sal), "coh": hit(s_coh), "fused": hit(fused), "fused_fixed": hit(fused_fixed),
                "unified": uni_correct.get(u_mi, None),
                "twin": int(rng.choice([c["cluster"] for c in cands]) == gold_eid),
            })
    n = len(rows)

    def acc(k):
        v = [r[k] for r in rows if r[k] is not None]
        return round(sum(v) / max(1, len(v)), 4)

    def paired_ci(a, b):
        d = np.array([r[a] - r[b] for r in rows])
        rng2 = np.random.default_rng(SEED)
        boots = np.array([d[rng2.integers(0, len(d), len(d))].mean() for _ in range(2000)])
        lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
        return {"delta": round(float(d.mean()), 4), "ci95": [round(lo, 4), round(hi, 4)], "ci_sep": bool(lo > 0 or hi < 0)}
    return {
        "n_pronoun_undergoers_multi_entity": n,
        "affected_entity_accuracy": {"salience_alone": acc("sal"), "coherence_alone": acc("coh"),
                                     "FUSED_reliability_weighted": acc("fused"),
                                     "fused_fixed_weight_ablation": acc("fused_fixed"),
                                     "unified_organ_ref": acc("unified"), "twin": acc("twin")},
        "fused_minus_salience": paired_ci("fused", "sal"),
        "fused_minus_fixedweight": paired_ci("fused", "fused_fixed"),
        "note": "Reliability-weighted fusion (salience prior x selectional coherence) vs salience-alone on the "
                "affected-entity task. coherence-alone should be WEAK (ambiguity wall); reliability-weighting must "
                "NOT regress salience-alone and should beat the fixed-weight ablation. Gold used only to score.",
    }


def self_test():
    """LOCATED NEGATIVE witness: for (phi-filtered) pronoun undergoers, the TYPE-selectional coherence cue does
    NOT discriminate among same-type candidates (all persons), so it cannot add over the forward salience prior;
    the salience prior is the lever. The deeper coherence (entity-STATE / event-world-knowledge) is the untested
    next step."""
    r = run()
    a = r["affected_entity_accuracy"]
    assert r["n_pronoun_undergoers_multi_entity"] > 40, f"too few multi-entity pronoun undergoers: {r}"
    # the finding: coherence-alone is WEAK (ambiguity wall, non-discriminating among phi-filtered candidates)
    assert a["coherence_alone"] < a["salience_alone"] - 0.05, f"coherence unexpectedly strong: {a}"
    # and fusion does NOT beat salience-alone (type-coherence is redundant for phi-filtered pronoun undergoers)
    assert a["FUSED_reliability_weighted"] <= a["salience_alone"] + 0.01, f"fusion unexpectedly beat salience: {a}"
    print(f"[SELFTEST PASS] LOCATED NEGATIVE (n={r['n_pronoun_undergoers_multi_entity']}): salience "
          f"prior={a['salience_alone']} is the lever; TYPE-coherence alone={a['coherence_alone']} (weak, "
          f"non-discriminating among phi-filtered candidates); fusion={a['FUSED_reliability_weighted']} does not "
          f"add (fused-minus-salience {r['fused_minus_salience']['delta']}). Deeper entity-STATE/event coherence "
          f"is the untested next step.")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        pprint.pprint(run(), width=118, sort_dicts=False)
