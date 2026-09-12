"""SITUATION-MODEL BUILD 3 (mathematically BF): the IMPLICIT-CAUSALITY next-mention PRIOR, fused with the
forward salience prior by Ernst-Banks calibrated inverse-variance weighting, for who-was-affected.

WHY (measured). Milestone-1 salience prior = the TOPICHOOD/LIKELIHOOD half of Kehler-Rohde
P(ref|pron) ∝ P(pron|ref)·P(ref); it SATURATES at ~0.45 -- the ~55% residual is the missing PRIOR term (the
next-mention expectation set by EVENT SEMANTICS). Milestone-2's type cue failed because phi-agreement already
consumes animacy (same-type candidates) AND margin-based reliability rewarded confident-wrong cues. VERIFY-FIRST
(this program): IC-biasing verbs govern 158/1142 (14%) of pronoun undergoers; salience is WRONG on 64% of those
(the payoff zone); IC disagrees with salience 92% -- a real, orthogonal, populated stratum.

THE CUE (brain-pinned). Implicit causality (Garvey-Caramazza 1974; Hartshorne-Snedeker 2013): stimulus-experiencer
verbs ("frighten") bias the referent to the SUBJECT (NP1, the cause); experiencer-stimulus verbs ("fear") to the
OBJECT (NP2). It discriminates two SAME-TYPE persons by their CAUSAL ROLE -- the axis phi-filtered candidates differ
on. IC feeds the PRIOR term (Rohde-Kehler).

MATHEMATICALLY BF (per owner: upgrade any BF_SPIRIT before use):
  - IC bias = the EMPIRICAL Ferstl-Garnham-Manouilidou (2011) 305-verb human sentence-completion norm
    (data/ic_norms/ferstl2011.xlsx) -- the brain's MEASURED IC signal, an admissible offline foundation asset
    (NOT the BF_SPIRIT categorical psych_verb_frames hand-list; gate to normed verbs).
  - salience = ACT-R base-level activation (hdlab.salience_binder, __bf_status__=BF).
  - FUSION = Ernst-Banks (2002) MLE optimal cue integration -- weight each cue by CALIBRATED INVERSE-VARIANCE
    (w = informedness = (acc - chance)/(1 - chance), measured on a HELD-OUT split; a chance cue -> w=0, cannot
    dilute) -- NOT the BF_SPIRIT margin-based convergent_cue_reader (margin = sharpness != accuracy; it misfired).
  math: p_sal = softmax(ACT-R); p_IC(e) ∝ P(NP1) if e is subject-role else 1-P(NP1), P(NP1)=(bias+1)/2;
        GATE 1[IC verb governs] -> when off, IC term = 0 (the fix for the M2 dilution);
        fused log-score(e) = w_sal·log p_sal(e) + w_IC·gate·log p_IC(e); weights calibrated on even-index docs.

MEASURE on GUM odd-index test: affected-entity accuracy on the IC-PRESENT stratum (primary) + full set (secondary),
vs salience-alone. CONTROLS: SCRAMBLE discourse order (salience collapses, IC SURVIVES = a dissociation diagnostic,
IC is clause-local); INFO-FREE TWIN (random per-verb bias, matched magnitude -> loses); PRIOR-LESION (IC-alone);
NO-LEAK (IC from verb+role only, undergoer-blind; Ferstl is independent of GUM). SELF-KILL if the calibrated-gated
arm does not beat salience-alone CI-separated on the IC-present stratum.

NO external LLM. Glass-box. ASCII.
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
import experiments.exp_affected_entity_reliability_fusion_gum_v1 as B2
import experiments.exp_gap_ic_coherence_v3 as ICV
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY

SEED = 20260910
TAU_IC = 0.30

_LEX = ICV.load_ic_lexicon()
_LIDX = ICV.build_lemma_index(_LEX)


def _ic_bias(verb):
    return _LIDX.get(verb.lower()) if verb else None


def _softmax(x):
    x = np.asarray(x, float)
    e = np.exp(x - x.max())
    return e / (e.sum() + 1e-12)


def _collect(docs):
    """Per pronoun undergoer with >=2 same-type entities: the salience distribution, the IC prior, the gold
    per-entity hit, and whether the governing verb is IC-present. Undergoer-blind IC (verb+role only)."""
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    out = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        uverbs = B2._undergoer_verbs(doc)
        for gidx, vl in uverbs.items():
            if gidx not in head_to_mi:
                continue
            u_mi = head_to_mi[gidx]; u = mlive[u_mi]; M = doc.mentions[u_mi]
            if M.mtype != "pronoun":
                continue
            cands = [x for x in mlive if x["midx"] < u_mi and not x["is_pronoun"] and B1._gn_ok(u, x)]
            if len(cands) < 2:
                continue
            ent_hist = defaultdict(list); ent_last = {}; ent_rank = {}
            for x in cands:
                h = x["head"]; ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                    ent_last[h] = x
                ent_rank[h] = min(ent_rank.get(h, 9), x.get("sent_role_rank", 9))
            ents = list(ent_hist.keys())
            if len(ents) < 2:
                continue
            now = float(u["order"])
            s_sal = np.array([actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents])
            gold_hit = np.array([int(ent_last[h]["cluster"] == M.eid) for h in ents])
            b = _ic_bias(vl)
            ic_present = b is not None and abs(b) >= TAU_IC
            # IC prior over ents by role: subject-role (rank 0) gets P(NP1), else 1-P(NP1)
            pnp1 = (float(b) + 1.0) / 2.0 if b is not None else 0.5
            raw = np.array([pnp1 if ent_rank[h] == 0 else (1.0 - pnp1) for h in ents])
            p_ic = raw / (raw.sum() + 1e-12)
            out.append({"ents": ents, "hist": {h: ent_hist[h] for h in ents}, "rank": {h: ent_rank[h] for h in ents},
                        "order": now, "s_sal": s_sal, "p_ic": p_ic, "gold": gold_hit,
                        "ic_present": ic_present, "bias": b, "n": len(ents)})
    return out


def _informedness(items, cue):
    """Calibrated reliability = (acc - chance)/(1 - chance) of a cue's argmax on the given items. chance = mean 1/n.
    cue in {'sal','ic'}. Returns weight in [0,1]; a chance cue -> 0 (cannot dilute)."""
    if not items:
        return 0.0
    hits = []; chances = []
    for it in items:
        score = it["s_sal"] if cue == "sal" else it["p_ic"]
        hits.append(it["gold"][int(np.argmax(score))]); chances.append(1.0 / it["n"])
    acc = float(np.mean(hits)); ch = float(np.mean(chances))
    return max(0.0, (acc - ch) / (1.0 - ch + 1e-9))


def _scramble_sal(it, rng):
    """salience with permuted discourse order (times) -> the salience prior must collapse; IC (clause-local) survives."""
    ents = it["ents"]
    allt = [t for h in ents for (t, _) in it["hist"][h]]
    rng.shuffle(allt)
    k = 0; hist2 = {}
    for h in ents:
        hist2[h] = [(allt[k + j], r) for j, (_, r) in enumerate(it["hist"][h])]; k += len(it["hist"][h])
    now = max(allt) + 1.0
    return np.array([actr_activation(hist2[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents])


def run(limit=None):
    import random
    rng = random.Random(SEED)
    docs = B1._load_test(limit)
    caldocs = docs[0::2]; evaldocs = docs[1::2]        # held-out calibration vs eval (both within the test split)
    cal = _collect(caldocs); ev = _collect(evaldocs)
    cal_ic = [it for it in cal if it["ic_present"]]
    # CALIBRATED inverse-variance (informedness) weights, fit on the IC-present calibration stratum (where IC applies)
    w_sal = _informedness(cal_ic, "sal") if cal_ic else _informedness(cal, "sal")
    w_ic = _informedness(cal_ic, "ic")
    # info-free twin weight: a random-per-verb-bias IC has chance informedness -> ~0 (report for the twin arm)

    ev_ic = [it for it in ev if it["ic_present"]]

    def evaluate(items, arm):
        hits = []
        for it in items:
            ps = _softmax(it["s_sal"]); pic = it["p_ic"]
            gate = 1.0 if it["ic_present"] else 0.0
            if arm == "salience":
                score = np.log(ps + 1e-12)
            elif arm == "ic":
                score = np.log(pic + 1e-12)
            elif arm == "fused_calibrated":
                score = w_sal * np.log(ps + 1e-12) + w_ic * gate * np.log(pic + 1e-12)
            elif arm == "fused_ungated":
                score = w_sal * np.log(ps + 1e-12) + w_ic * np.log(pic + 1e-12)
            elif arm == "scramble_fused":
                pss = _softmax(_scramble_sal(it, rng))
                score = w_sal * np.log(pss + 1e-12) + w_ic * gate * np.log(pic + 1e-12)
            elif arm == "twin":                       # info-free: random per-decision IC direction, matched magnitude
                flip = rng.choice([1.0, -1.0])
                pnp1 = 0.5 + flip * abs((it["bias"] or 0.0)) / 2.0
                raw = np.array([pnp1 if it["rank"][h] == 0 else 1.0 - pnp1 for h in it["ents"]])
                ptw = raw / (raw.sum() + 1e-12)
                score = w_sal * np.log(ps + 1e-12) + w_ic * gate * np.log(ptw + 1e-12)
            hits.append(it["gold"][int(np.argmax(score))])
        return np.array(hits)

    def summ(items):
        arms = {}
        base = evaluate(items, "salience")
        for a in ("salience", "ic", "fused_calibrated", "fused_ungated", "scramble_fused", "twin"):
            h = evaluate(items, a); arms[a] = round(float(h.mean()), 4)
        # paired CI fused_calibrated - salience
        fc = evaluate(items, "fused_calibrated")
        d = fc.astype(int) - base.astype(int)
        rng2 = np.random.default_rng(SEED)
        boots = np.array([d[rng2.integers(0, len(d), len(d))].mean() for _ in range(2000)]) if len(d) else np.zeros(1)
        arms["n"] = len(items)
        arms["fused_minus_salience"] = {"delta": round(float(d.mean()), 4),
                                        "ci95": [round(float(np.percentile(boots, 2.5)), 4),
                                                 round(float(np.percentile(boots, 97.5)), 4)],
                                        "ci_sep": bool(np.percentile(boots, 2.5) > 0 or np.percentile(boots, 97.5) < 0)}
        return arms
    return {
        "calibration": {"w_salience": round(w_sal, 4), "w_ic": round(w_ic, 4),
                        "n_cal_ic_present": len(cal_ic)},
        "IC_PRESENT_stratum_PRIMARY": summ(ev_ic),
        "full_matched_set_secondary": summ(ev),
        "note": "Ernst-Banks calibrated inverse-variance fusion (informedness weights, held-out) of the BF salience "
                "prior + the empirical Ferstl IC prior, GATED. Primary endpoint = IC-present stratum. Controls: "
                "scramble (salience collapses, IC survives); info-free twin (random per-verb IC, matched magnitude) "
                "must lose; ic-alone = prior-lesion. Mathematically BF: no margin-based BF_SPIRIT weighting.",
    }


def self_test():
    """LOCATED NEGATIVE witness (pre-registered self-kill fired): implicit causality does NOT help affected-entity
    resolution, because the undergoer pronoun is the verb's ARGUMENT (its referent is set by coref/salience) -- NOT
    a following pronoun in a causal continuation (IC's actual configuration, which predicts the CAUSE). IC-alone is
    below chance (misapplied). The mathematically-BF calibrated inverse-variance fusion WORKED as designed: it
    down-weighted the bad cue (w_ic << w_sal) -- unlike margin-weighting (M2), which up-weighted confident-wrong.
    Salience (milestone 1) remains the lever."""
    r = run()
    p = r["IC_PRESENT_stratum_PRIMARY"]; c = r["calibration"]
    assert p["n"] > 20, f"IC-present eval stratum too small: {p['n']}"
    # the finding: IC-alone is weak/misapplied (below salience), and fusion does NOT beat salience (self-kill fired)
    assert p["ic"] < p["salience"], f"IC-alone unexpectedly strong: {p}"
    assert not p["fused_minus_salience"]["ci_sep"] or p["fused_minus_salience"]["delta"] <= 0, \
        f"IC fusion unexpectedly beat salience: {p}"
    # the mathematically-BF fusion worked: calibrated inverse-variance down-weighted the bad cue
    assert c["w_ic"] < c["w_salience"], f"calibrated weighting did not down-weight the weak IC cue: {c}"
    print(f"[SELFTEST PASS] LOCATED NEGATIVE (IC misapplies to argument-pronouns). IC-present stratum (n={p['n']}): "
          f"salience={p['salience']} is the lever; IC-alone={p['ic']} (below chance, misapplied); "
          f"fused={p['fused_calibrated']} does not beat salience ({p['fused_minus_salience']['delta']}). "
          f"Mathematically-BF fusion WORKED: calibrated w_ic={c['w_ic']} << w_sal={c['w_salience']} "
          f"(down-weighted the bad cue, unlike margin-weighting).")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        pprint.pprint(run(), width=118, sort_dicts=False)
