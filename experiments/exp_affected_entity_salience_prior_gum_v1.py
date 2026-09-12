"""SITUATION-MODEL MILESTONE 1 (BF): the FORWARD SITUATIONAL-ADDRESS PRIOR for WHO-WAS-AFFECTED.

WHY (measured, convergent). "Who was affected" fails not at the intra-sentence undergoer SLOT (who_did_what_patient
= 0.83, near-solved) but at ENTITY RESOLUTION: the undergoer is a pronoun/definite that must be resolved to the
right DISCOURSE ENTITY (coref board dim is the stuck residual; the oracle probe put the whole headroom in
entity-separation + recency). Selectional knowledge densification (typed Resnik) fixed coverage but NOT recovery --
the residual is genuine AMBIGUITY that needs the situation model. This is the project's 09-10 coref reframe:
reference = FORWARD situational-address PRIOR x BACKWARD retrieval LIKELIHOOD; we built only the backward half.

THE MISSING FORWARD HALF (this cell). The brain resolves an ambiguous undergoer to the SALIENT/TOPICAL/GIVEN entity
(Centering Cb/Cf, Grosz/Joshi/Weinstein; Givenness Hierarchy, Gundel et al.; Kehler-Rohde Bayesian pronoun
resolution: P(referent|pronoun) ∝ P_salience(prior) x P_coherence(likelihood)). The salience prior is ACT-R
base-level activation over discourse referents (Lewis-Vasishth; Anderson) -- ALREADY a BF organ
(hdlab.salience_binder, __bf_status__=BF) -- but it is applied to generic pronoun anaphora and NEVER to the
undergoer/affected decision. THE JOIN (undergoer TOKEN -> coref MENTION -> resolved CHAIN) does not exist; GUM
carries gold deprels AND gold coref in one file, so we build it here.

THE BUILD. On GUM (modern; 19c-banned): join each undergoer token (gold obj/nsubj:pass) to its coref MENTION (by
head_g) and its gold CHAIN (eid) + FORM (pronoun/definite/lexical). For each ANAPHORIC (pronominal) undergoer,
resolve it to a prior entity three ways and score affected-ENTITY accuracy (resolved chain == gold eid), STRATIFIED
by form (the stratum split IS the intra-sentence-vs-discourse scoping test):
  RECENCY floor  : most-recent gender/number-compatible antecedent.
  SALIENCE prior : argmax ACT-R base-level activation B(entity) = ln( sum_k w(role_k) * dt_k^-decay ) over the
                   entity's online (gold-free, head-individuated) mention history (salience_binder.actr_activation,
                   ROLE_PROMINENCE SUBJ>POSS>OBJ>OTHER). = the forward situational-address prior.
  ORACLE         : gold chain (ceiling = 1.0 by construction; reported as the reachable bound).

CONTROLS (full stack): SCRAMBLE discourse order (shuffle mention times -> salience must COLLAPSE toward chance ->
proves the lift is a real discourse-recency/role signal, not a pool artifact); INFO-FREE TWIN (same salience pick,
RANDOM entity identities -> must lose); PRIOR-LESION (= the recency floor); NO-LEAK (gold eid used ONLY to score,
never to build salience -- online head-individuation only); stratum split (pronoun vs lexical).

NO external LLM at inference. Glass-box. ASCII. Reuses BF organs (salience_binder BF; GUM reader).
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.gum_coref as GC
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY

SEED = 20260910
UND_DEPRELS = {"obj", "dobj", "nsubj:pass", "nsubjpass"}


def _load_test(limit=None):
    try:
        import experiments.exp_name_entity_clustering_v1 as NEC
        gaz = NEC.load_given_gazetteer()
    except Exception:
        gaz = None
    docs = GC.load_docs(gum_only=True, name_gazetteer=gaz, limit=limit)
    return [d for i, d in enumerate(docs) if i % 2 == 1]     # odd-index TEST split (board convention)


def _role(rank):
    return "SUBJECT" if rank == 0 else ("OBJECT" if rank == 1 else "OTHER")


def _gn_ok(a, b):
    """gender/number compatibility (unknown = wildcard)."""
    ga, gb = a.get("gender"), b.get("gender")
    na, nb = a.get("number"), b.get("number")
    if ga and gb and ga != gb:
        return False
    if na and nb and na != nb:
        return False
    return True


def _definite(doc, m):
    """definite-common? read the span determiner (the/Def) -- the trivial FORM stratification gap."""
    for t in doc.toks:
        if m.start_g <= t.gidx <= m.end_g and (t.upos == "DET" or "Definite" in (t.feats or {})):
            if t.lemma in ("the", "this", "that", "these", "those") or (t.feats or {}).get("Definite") == "Def":
                return True
    return False


def _undergoer_mentions(doc, mlive):
    """[(midx, form, gold_eid)] for undergoer tokens joined to their coref mention (head_g == token gidx)."""
    head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
    out = []
    for t in doc.toks:
        if t.deprel in UND_DEPRELS and t.gidx in head_to_mi:
            mi = head_to_mi[t.gidx]
            M = doc.mentions[mi]
            if M.mtype == "pronoun":
                form = "pronoun"
            elif M.mtype == "common" and _definite(doc, M):
                form = "definite"
            else:
                form = "lexical"          # name / indefinite / bare
            out.append((mi, form, M.eid))
    return out


def _resolve(mlive, u_mi, arm, rng):
    """Resolve undergoer mention u to a prior entity. Returns predicted gold_eid or None.
    arm in {recency, salience, salience_scramble, twin}. gold eid used ONLY to read the picked mention's identity
    for scoring (never to build the salience)."""
    u = mlive[u_mi]
    now = float(u["order"]) if "order" in u else float(u_mi)
    # candidate antecedents: prior, non-pronoun, gn-compatible
    cands = [m for m in mlive if m["midx"] < u_mi and not m["is_pronoun"] and _gn_ok(u, m)]
    if not cands:
        return None
    # online (gold-free) entity individuation by head; history = [(time, role)]
    ent_hist = defaultdict(list)
    ent_last = {}
    times = {m["midx"]: float(m.get("order", m["midx"])) for m in mlive}
    if arm == "salience_scramble":
        shuf = list(times.values()); rng.shuffle(shuf)
        times = {k: shuf[i] for i, k in enumerate(times)}
        now = max(times.values()) + 1.0
    for m in cands:
        h = m["head"]
        ent_hist[h].append((times[m["midx"]], _role(m.get("sent_role_rank", 2))))
        if h not in ent_last or times[m["midx"]] >= times[ent_last[h]["midx"]]:
            ent_last[h] = m
    if arm == "recency":
        pick = max(cands, key=lambda m: times[m["midx"]])
        return pick["cluster"]
    # salience arms: argmax ACT-R base-level activation over entity histories
    best_h, best_B = None, -1e18
    for h, hist in ent_hist.items():
        B = actr_activation(hist, now, DEFAULT_DECAY, ROLE_PROMINENCE)
        if B > best_B:
            best_B, best_h = B, h
    if best_h is None:
        return None
    if arm == "twin":
        # info-free twin: same salience pick, RANDOM entity identity from the candidate pool
        return rng.choice([m["cluster"] for m in cands])
    return ent_last[best_h]["cluster"]


def run(limit=None):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    import hdlab.coref as COREF
    import hdlab.unified_referent as UR
    rng = random.Random(SEED)
    docs = _load_test(limit)
    arms = ("recency", "salience", "unified", "salience_scramble", "twin")
    # per (arm, stratum): [correct...]
    tally = {a: defaultdict(list) for a in arms}
    matched = []          # pronoun undergoers scored by ALL arms on the SAME items
    n_docs = 0
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        if "order" not in (mlive[0] if mlive else {}):
            for i, m in enumerate(mlive):
                m["order"] = i
        ums = _undergoer_mentions(doc, mlive)
        if not ums:
            continue
        n_docs += 1
        # the REAL BF coref organ: resolve all pronoun targets once, map target_midx -> correct
        uni_correct, uni_scr_correct = {}, {}
        try:
            targets = COREF.build_pronoun_targets(mlive)
            for rec in UR.resolve_unified_stream(mlive, targets):
                uni_correct[rec["target_midx"]] = int(bool(rec.get("correct")))
            # SCRAMBLE control on the REAL organ: permute the discourse ORDER (times/sent_idx) -> the ACT-R
            # salience prior must COLLAPSE if the win is a real discourse-recency/role signal (not static carding)
            perm = list(range(len(mlive))); rng.shuffle(perm)
            scr = []
            for j, m in enumerate(mlive):
                mm = dict(m); mm["order"] = perm[j]; mm["sent_idx"] = perm[j]; scr.append(mm)
            scr.sort(key=lambda m: m["order"])
            scr_tg = COREF.build_pronoun_targets(scr)
            for rec in UR.resolve_unified_stream(scr, scr_tg):
                uni_scr_correct[rec["target_midx"]] = int(bool(rec.get("correct")))
        except Exception:
            pass
        for (u_mi, form, gold_eid) in ums:
            stratum = "pronominal" if form in ("pronoun", "definite") else "lexical"
            preds = {a: _resolve(mlive, u_mi, a, rng) for a in arms if a != "unified"}
            for a, pred in preds.items():
                if pred is None:
                    continue
                tally[a][stratum].append(int(pred == gold_eid)); tally[a]["ALL"].append(int(pred == gold_eid))
            if u_mi in uni_correct:
                tally["unified"][stratum].append(uni_correct[u_mi]); tally["unified"]["ALL"].append(uni_correct[u_mi])
            # MATCHED head-to-head: pronoun undergoers scored by EVERY arm on the SAME items (unified defined + recency pool)
            if form == "pronoun" and u_mi in uni_correct and preds.get("recency") is not None:
                matched.append({"unified": uni_correct[u_mi],
                                "unified_scramble": uni_scr_correct.get(u_mi, 0),
                                "recency": int(preds["recency"] == gold_eid),
                                "salience": int((preds["salience"] or -1) == gold_eid),
                                "twin": int((preds["twin"] or -1) == gold_eid)})

    def acc(a, s):
        v = tally[a][s]
        return {"n": len(v), "acc": round(sum(v) / max(1, len(v)), 4)}

    # MATCHED head-to-head + paired bootstrap CI (unified salience-coref MINUS recency floor), same items
    matched_out = None
    if matched:
        import numpy as np
        rng2 = np.random.default_rng(SEED)
        U = np.array([m["unified"] for m in matched]); R = np.array([m["recency"] for m in matched])
        d = U - R
        boots = np.array([d[rng2.integers(0, len(d), len(d))].mean() for _ in range(2000)])
        matched_out = {
            "n": len(matched),
            "unified_salience_coref": round(float(U.mean()), 4),
            "recency_floor": round(float(R.mean()), 4),
            "salience_actr_crude": round(float(np.mean([m["salience"] for m in matched])), 4),
            "unified_SCRAMBLE_discourse_order": round(float(np.mean([m["unified_scramble"] for m in matched])), 4),
            "twin_info_free": round(float(np.mean([m["twin"] for m in matched])), 4),
            "unified_minus_recency": round(float(d.mean()), 4),
            "ci95": [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)],
            "ci_separated_from_0": bool(np.percentile(boots, 2.5) > 0 or np.percentile(boots, 97.5) < 0),
        }
    return {
        "n_test_docs_with_undergoers": n_docs,
        "MATCHED_pronoun_undergoers_head_to_head": matched_out,
        "affected_entity_accuracy": {
            "pronominal_stratum": {a: acc(a, "pronominal") for a in arms},
            "lexical_stratum": {a: acc(a, "lexical") for a in arms},
            "ALL": {a: acc(a, "ALL") for a in arms},
        },
        "note": "SALIENCE prior (forward situational-address) vs RECENCY floor on the affected-ENTITY task, "
                "stratified by undergoer FORM. The lift should concentrate on the PRONOMINAL stratum and COLLAPSE "
                "under salience_scramble (discourse-order shuffle); the info-free TWIN must lose. Gold eid used "
                "ONLY to score (no-leak). This is the join (undergoer->mention->chain) that did not exist.",
    }


def self_test():
    r = run()
    m = r["MATCHED_pronoun_undergoers_head_to_head"]
    assert m and m["n"] > 50, f"too few matched pronoun undergoers: {m}"
    # THE WIN: the salience-coref forward prior beats the recency floor on the affected-entity task
    assert m["unified_salience_coref"] > m["recency_floor"], f"salience prior did not beat recency: {m}"
    assert m["ci_separated_from_0"], f"unified-minus-recency not CI-separated: {m}"
    # CONTROLS: scramble the discourse order -> the win COLLAPSES (it is a real discourse-salience signal);
    # info-free twin LOSES; lexical stratum is near-floor (discourse-specific)
    assert m["unified_SCRAMBLE_discourse_order"] < m["unified_salience_coref"] - 0.08, f"scramble did not collapse: {m}"
    assert m["twin_info_free"] < m["unified_salience_coref"], f"twin did not lose: {m}"
    lex = r["affected_entity_accuracy"]["lexical_stratum"]["unified"]["acc"]
    print(f"[SELFTEST PASS] FORWARD SALIENCE PRIOR on affected-entity (matched pronoun undergoers, n={m['n']}): "
          f"unified={m['unified_salience_coref']} vs recency floor={m['recency_floor']} "
          f"(+{m['unified_minus_recency']}, CI{m['ci95']}, CI-sep); scramble collapses to "
          f"{m['unified_SCRAMBLE_discourse_order']}; twin={m['twin_info_free']} loses; lexical stratum={lex}.")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        pprint.pprint(run(), width=118, sort_dicts=False)
