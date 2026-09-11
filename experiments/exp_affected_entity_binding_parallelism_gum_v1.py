"""SITUATION-MODEL BUILD 4 (mathematically BF): the LIKELIHOOD half of pronoun-undergoer resolution --
BINDING PRINCIPLE B (hard co-argument filter) + grammatical/thematic-role PARALLELISM (soft likelihood bonus),
over the ACT-R salience prior. The correct lever we skipped.

WHY (diagnosed). Pronoun reference is a cascade: phi -> BINDING -> salience -> semantics. We built only the
salience PRIOR P(referent) (saturates 0.45) and added level-4 SEMANTIC cues (type, IC) that were redundant
(phi already same-type) / mis-configured (IC is a next-mention prior for a FOLLOWING pronoun, not the verb's
own argument). The discriminating action for an ARGUMENT pronoun is the LIKELIHOOD P(pronoun|referent):
  - PRINCIPLE B [PINNED universal; Chomsky 1981, Reinhart] = a HARD ZERO: a co-argument would be a REFLEXIVE, not
    a plain pronoun -> "John hit HIM" => him != John. P(plain pronoun | co-argument) = 0.
  - ROLE PARALLELISM [PINNED; Smyth 1994, Stevenson 1995] = a SOFT bias: OBJECT pronouns take OBJECT antecedents;
    our subject-biased ROLE_PROMINENCE is BACKWARDS for object anaphors -- its #1 pick is often the illegal
    clause-mate subject that Principle B forbids. (Thematic parallelism: undergoer=PATIENT -> prior PATIENTs.)

MATHEMATICALLY BF (per owner: verify each component; upgrade any BF_SPIRIT before use):
  - Principle B: the PINNED categorical constraint, implemented FRESH from the parse (co-argument = the clause-mate
    SUBJECT of the pronoun's verb; for nsubj:pass, the by-agent) -- NOT the BF-unregistered gold-mention organ.
  - Parallelism: the PINNED Bayesian LIKELIHOOD form exp(gamma*1[role-match]) -- NOT the BF_SPIRIT "invented
    arithmetic" fixed bonus (coref.CENTER_PARALLEL_BONUS, flagged RIGHT-OP-WRONG-METRIC). gamma SWEPT, not adopted.
  - Salience prior: ACT-R base-level activation (hdlab.salience_binder, __bf_status__=BF).
  math: score(c|a) = ln p_sal(c) + gamma_g*1[gram-role(c)=gram-role(a)] + gamma_t*1[c is PATIENT], over
        candidates c NOT excluded by Principle B. Bayesian: P(c|a) ∝ 1[c not co-arg]*exp(parallelism)*softmax(ACT-R).

MEASURE on GUM (gold UD roles = oracle-parse setting, isolating the LEVER): affected-entity accuracy on matched
pronoun undergoers, arms A0 floor / A1 salience(0.4545) / A2 +PrinB / A3 +gram-parallel / A4 +thematic-parallel /
A5 full. KEY DIAGNOSTIC: how often the current A1 top pick IS the illegal co-argument. CONTROLS: ablations (A2-A4),
SCRAMBLE role labels (parallelism collapses), info-free twin (uniform over PrinB survivors). SELF-KILL if A5 not
CI-sep over A1.

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
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
# The LOAD-BEARING resolver math is now the promoted organ hdlab.affected_entity_resolver (owner-DONE
# integration): the constants, the Principle-B co-argument exclusion, the grammatical/thematic role
# classes, and the salience x parallelism scoring live there. Routing through it makes THIS cell's 4/4
# witness the proof that the organ reproduces the win exactly (no divergence between measured + landed).
import hdlab.affected_entity_resolver as AER

SEED = 20260910
SUBJ_DEPS = AER.SUBJ_DEPS
OBJ_DEPS = AER.OBJ_DEPS
PATIENT_DEPS = AER.PATIENT_DEPS
GAMMA_G = AER.GAMMA_G
GAMMA_T = AER.GAMMA_T

_role_class = AER.role_class


def _coarg_head(doc, t, gidx2mi):
    """Principle B/C co-argument to EXCLUDE for an undergoer token t (organ passthrough -- kept as a thin
    wrapper so the run() call site is unchanged; the math lives in hdlab.affected_entity_resolver)."""
    return AER.coarg_head_gidx(doc.toks, t)


_FRONTEND = None


def _overlay_predicted(doc):
    """DEPLOYMENT setting: replace the GUM gold UD deprels/heads with the SUPERVISED PARSER's PREDICTED ones
    (pos_tagger + arc_parser + arc_labeler), so the binding/role lever is measured on the real parse, not gold
    roles. Mutates doc.toks in place (fresh per run)."""
    global _FRONTEND
    if _FRONTEND is None:
        import hdlab.causation_typing as CT
        _FRONTEND = CT._frontend()
    tg, pp, lb = _FRONTEND
    by_sent = defaultdict(list)
    for tok in doc.toks:
        by_sent[tok.sent].append(tok)
    for sent, toks in by_sent.items():
        toks = sorted(toks, key=lambda x: x.idx)
        forms = [x.form for x in toks]
        pos = list(tg.tag(forms))
        heads = dict(pp.parse(forms, pos).heads)
        labels = dict(lb.label(forms, pos, heads))
        for j, x in enumerate(toks):
            i1 = j + 1
            x.deprel = labels.get(i1, "dep").split(":")[0] if labels.get(i1) else x.deprel
            # keep passive/agent subtypes the labeler emits
            x.deprel = labels.get(i1, x.deprel)
            x.head = heads.get(i1, x.head)


def run(limit=None, gamma_g=GAMMA_G, gamma_t=GAMMA_T, predicted_parse=False):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    import random
    rng = random.Random(SEED)
    docs = B1._load_test(limit)
    if predicted_parse:
        for doc in docs:
            _overlay_predicted(doc)
    arms = ("recency", "A1_salience", "A2_prinB", "A3_gram_par", "A4_thematic_par", "A5_full",
            "A5_scramble_roles", "A5_twin_uniform")
    tally = {a: [] for a in arms}
    n = 0; n_coarg_in_pool = 0; a1_picks_coarg = 0; n_prinb_pruned = 0
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        # undergoer tokens
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
            # co-argument entity to exclude (Principle B/C)
            cg = _coarg_head(doc, t, head_to_mi)
            coarg_head_lemma = mlive[head_to_mi[cg]]["head"] if (cg is not None and cg in head_to_mi) else None
            # entities (online, head-individuated) with history + role of most-recent mention
            ent_hist = defaultdict(list); ent_last = {}
            for x in cands:
                h = x["head"]; ent_hist[h].append((float(x["order"]), B1._role(x.get("sent_role_rank", 2))))
                if h not in ent_last or x["order"] >= ent_last[h]["order"]:
                    ent_last[h] = x
            ents = list(ent_hist.keys())
            if len(ents) < 2:
                continue
            n += 1
            now = float(u["order"])
            sal = {h: actr_activation(ent_hist[h], now, DEFAULT_DECAY, ROLE_PROMINENCE) for h in ents}
            role_of = {h: _role_class(gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "")) for h in ents}
            patient_of = {h: (gidx2dep.get(mi2headg.get(ent_last[h]["midx"]), "") in PATIENT_DEPS) for h in ents}
            a_role = _role_class(t.deprel)
            legal = [h for h in ents if h != coarg_head_lemma]
            if coarg_head_lemma in ents:
                n_coarg_in_pool += 1
            if legal and len(legal) < len(ents):
                n_prinb_pruned += 1

            def pick(cand_set, use_par_g=False, use_par_t=False, scramble=False, uniform=False):
                if not cand_set:
                    cand_set = ents
                if uniform:
                    return rng.choice(cand_set)
                ro = role_of
                if scramble:
                    vals = list(role_of.values()); rng.shuffle(vals); ro = {h: vals[i] for i, h in enumerate(ents)}
                # the LOAD-BEARING salience x parallelism argmax = the promoted organ (byte-identical math)
                return AER.score_and_pick(cand_set, sal, ro, patient_of, a_role,
                                          use_par_g=use_par_g, use_par_t=use_par_t,
                                          gamma_g=gamma_g, gamma_t=gamma_t)

            def hit(h):
                return int(ent_last[h]["cluster"] == gold)
            a1 = pick(ents)
            if a1 == coarg_head_lemma:
                a1_picks_coarg += 1
            tally["recency"].append(hit(max(ents, key=lambda h: ent_last[h]["order"])))
            tally["A1_salience"].append(hit(a1))
            tally["A2_prinB"].append(hit(pick(legal)))
            tally["A3_gram_par"].append(hit(pick(ents, use_par_g=True)))
            tally["A4_thematic_par"].append(hit(pick(ents, use_par_t=True)))
            tally["A5_full"].append(hit(pick(legal, use_par_g=True, use_par_t=True)))
            tally["A5_scramble_roles"].append(hit(pick(legal, use_par_g=True, use_par_t=True, scramble=True)))
            tally["A5_twin_uniform"].append(hit(pick(legal, uniform=True)))

    def acc(a):
        v = tally[a]
        return round(sum(v) / max(1, len(v)), 4)

    def paired(a, b):
        d = np.array(tally[a]) - np.array(tally[b])
        rng2 = np.random.default_rng(SEED)
        boots = np.array([d[rng2.integers(0, len(d), len(d))].mean() for _ in range(2000)]) if len(d) else np.zeros(1)
        return {"delta": round(float(d.mean()), 4),
                "ci95": [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)],
                "ci_sep": bool(np.percentile(boots, 2.5) > 0 or np.percentile(boots, 97.5) < 0)}
    return {
        "n_matched_pronoun_undergoers": n, "gamma_g": gamma_g, "gamma_t": gamma_t,
        "DIAGNOSTIC": {"coarg_in_candidate_pool": n_coarg_in_pool,
                       "A1_top_pick_IS_the_illegal_coargument": a1_picks_coarg,
                       "rate": round(a1_picks_coarg / max(1, n), 4),
                       "prinB_pruned_a_candidate": n_prinb_pruned},
        "accuracy": {a: acc(a) for a in arms},
        "A2_prinB_minus_A1": paired("A2_prinB", "A1_salience"),
        "A5_full_minus_A1": paired("A5_full", "A1_salience"),
        "note": "Mathematically-BF likelihood half: Principle-B co-argument filter (PINNED) + role/thematic "
                "parallelism (PINNED likelihood bonus, gamma swept) over the BF ACT-R salience prior. DIAGNOSTIC = "
                "how often the current subject-biased pick is the ILLEGAL co-argument. Controls: A2-A4 ablations; "
                "A5_scramble_roles (parallelism collapses); A5_twin_uniform (PrinB prune value alone).",
    }


def self_test():
    r = run()
    d = r["DIAGNOSTIC"]; a = r["accuracy"]
    assert r["n_matched_pronoun_undergoers"] > 100, f"too few undergoers: {r['n_matched_pronoun_undergoers']}"
    p5 = r["A5_full_minus_A1"]; p2 = r["A2_prinB_minus_A1"]
    # THE WIN (grammatical likelihood): A5 (Principle-B + parallelism) beats A1 salience-alone CI-separated
    assert p5["ci_sep"] and p5["delta"] > 0, f"corrected lever did not beat salience CI-sep: A5={a['A5_full']} A1={a['A1_salience']} {p5}"
    print(f"[SELFTEST PASS] CORRECTED LEVER (mathematically BF grammar likelihood). n={r['n_matched_pronoun_undergoers']}. "
          f"DIAGNOSTIC: A1's top pick is the ILLEGAL co-argument {d['rate']*100:.0f}% of the time "
          f"({d['A1_top_pick_IS_the_illegal_coargument']}/{r['n_matched_pronoun_undergoers']}). "
          f"A1 salience={a['A1_salience']} -> A2 +PrinB={a['A2_prinB']} (+{p2['delta']}, CI{p2['ci95']}) -> "
          f"A5 full={a['A5_full']} (+{p5['delta']}, CI{p5['ci95']}, CI-sep). "
          f"scramble-roles={a['A5_scramble_roles']} (parallelism collapses); twin-uniform={a['A5_twin_uniform']}.")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        pprint.pprint(run(), width=118, sort_dicts=False)
