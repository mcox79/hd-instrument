"""exp_coref_residual_discourse_specific_v1 -- DRILL THE WALL: why is the coherence/selectional prior DEAD
on the who-did-what binding residual (0.015-0.029, loses to its info-free twin) when the BRAIN resolves
these cases? Hypothesis (from the sibling refutation + the pronoun-event research drill): the residual is
NOT resolved by TYPICALITY (generic verb/selectional bias -- what USUALLY does X) but by DISCOURSE-SPECIFIC
memory -- what THIS text established these SPECIFIC entities do (the situation model; Kintsch
construction-integration; Kehler-Rohde P(referent) as a this-discourse prior, not a world prior).

DECISIVE CONTRAST on the structurally-dominated residual (gold is NOT most-recent / max-subject / most-
frequent -- every typicality cue is anti-predictive by construction):
  GENERIC (typicality)      : does the query verb v typically select this candidate's TYPE? == the sibling's
                              selectional/thematic prior. MEASURED DEAD (0.015 / 0.010).
  DISCOURSE-SPECIFIC (oracle): does THIS candidate, ELSEWHERE in THIS document, participate in the SAME
                              event (same gov_verb) or the SAME object (obj_head)? A within-document
                              entity-event affinity computed via gold coref -- the situation-model signal.
                              This is an ORACLE CEILING (uses gold coref to find the entity's other
                              mentions), like the sibling's oracle ceilings -- it measures whether the
                              discourse-specific signal EXISTS in the text, i.e. whether the brain's
                              mechanism COULD resolve the residual glass-box (no world knowledge, no LLM).

If DISCOURSE-SPECIFIC recovers a real slice where GENERIC is dead -> the wall is a MISSING SITUATION MODEL
(discourse-specific memory), NOT world knowledge -> we CAN do it once we build that memory (phase 1), and we
know exactly what signal to build. If it too is dead -> the residual is genuinely one-shot / world-knowledge
-bound and irreducible even to a situation model.

CONTROLS: info-free TWIN (shuffle the discourse-specific affinity across candidates -> must LOSE); coverage
(fraction of residual with ANY non-zero discourse-specific signal -- the mechanism's reach); the generic
selectional prior recomputed on the SAME residual (the dead baseline).

Run: .venv/Scripts/python.exe experiments/exp_coref_residual_discourse_specific_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_residual_discourse_specific_v1.py --run
GLASS-BOX, remote-safe (reads pre-parsed cache; NO spaCy, NO torch; numpy only).
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, _gn_compat  # noqa: E402
from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import (  # noqa: E402
    load_streams, _entity_gn_gold, _supports, arm_actr, ACTR_D_FLOOR, SEED)


def _residual(streams) -> List[dict]:
    """Structurally-dominated residual: pronoun queries where the ACT-R binder errs AND the gold is NOT
    favored by any structural cue (recency / subjecthood / frequency) -- the anti-typical core."""
    out = []
    for rec in streams:
        stream = rec["stream"]
        egn = _entity_gn_gold(stream)
        prior: Dict[int, list] = defaultdict(list)
        for m in stream:
            ht = m["head_text"]
            gold = m["gold"]
            if ht in PRONOUNS:
                pg, pn = PRONOUNS[ht]
                cand = {}
                for c, pri in prior.items():
                    if not pri:
                        continue
                    eg, en = egn.get(c, (None, None))
                    if _gn_compat(pg, pn, eg, en):
                        cand[c] = list(pri)
                if gold in cand and len(cand) >= 2:
                    inst = {"doc": rec["doc"], "pronoun": ht, "p_sent": m["sent"], "pron_role": m["role"],
                            "gold_cid": gold, "cand_ids": sorted(cand), "prior": {c: cand[c] for c in cand},
                            "gov_verb": m.get("gov_verb"), "obj_head": m.get("obj_head")}
                    ids, sup, gi = _supports(inst)
                    pick = arm_actr(ids, sup, gi, inst, ACTR_D_FLOOR)["pick"]
                    dom = not ((int(np.argmax(sup["recency"])) == gi)
                               or (sup["subject"][gi] == sup["subject"].max())
                               or (sup["freq"][gi] == sup["freq"].max()))
                    if pick != gi and dom:
                        out.append(inst)
            prior[gold].append((m["sent"], m["role"]))
    return out


def _doc_entity_events(streams) -> Dict[str, Dict[int, dict]]:
    """Per doc, per gold entity: the multiset of gov_verbs and obj_heads it participates in (all mentions).
    The situation-model content, indexed by entity -- built from the whole document."""
    out: Dict[str, Dict[int, dict]] = {}
    for rec in streams:
        ev: Dict[int, dict] = defaultdict(lambda: {"verbs": Counter(), "objs": Counter()})
        for m in rec["stream"]:
            g = m["gold"]
            if m.get("gov_verb"):
                ev[g]["verbs"][m["gov_verb"]] += 1
            if m.get("obj_head"):
                ev[g]["objs"][m["obj_head"]] += 1
        out[rec["doc"]] = ev
    return out


def run(docs: Optional[int] = None, seed: int = SEED) -> dict:
    streams = load_streams(docs)
    res = _residual(streams)
    ent_ev = _doc_entity_events(streams)
    rng = np.random.default_rng(seed)

    n = len(res)
    ds_hit = ds_appl = 0            # discourse-specific (within-doc verb/obj affinity) oracle
    twin_hit = twin_appl = 0        # info-free twin (shuffled affinity)
    verb_only_hit = verb_only_appl = 0
    for inst in res:
        doc = inst["doc"]; v = inst.get("gov_verb"); obj = inst.get("obj_head")
        ids = inst["cand_ids"]; gi = ids.index(inst["gold_cid"])
        ev = ent_ev[doc]
        # discourse-specific affinity per candidate: does this entity do the SAME verb or share the SAME
        # object ELSEWHERE in this doc? (exclude 1 count for the query mention itself via -1 clamp)
        aff = np.zeros(len(ids))
        vaff = np.zeros(len(ids))
        for k, c in enumerate(ids):
            ce = ev.get(c, {"verbs": Counter(), "objs": Counter()})
            va = max(ce["verbs"].get(v, 0) - (1 if c == inst["gold_cid"] else 0), 0) if v else 0
            oa = max(ce["objs"].get(obj, 0) - (1 if c == inst["gold_cid"] else 0), 0) if obj else 0
            aff[k] = va + oa
            vaff[k] = va
        if aff.max() > 0:
            ds_appl += 1
            ds_hit += int(int(np.argmax(aff)) == gi)
            perm = rng.permutation(len(ids))
            twin_appl += 1
            twin_hit += int(int(np.argmax(aff[perm])) == gi)
        if vaff.max() > 0:
            verb_only_appl += 1
            verb_only_hit += int(int(np.argmax(vaff)) == gi)

    def rate(h, a):
        return round(h / a, 4) if a else 0.0
    ds_acc = rate(ds_hit, ds_appl)
    twin_acc = rate(twin_hit, twin_appl)
    return {
        "anchor": "coref_residual_discourse_specific_v1",
        "population": "LitBank who-did-what structurally-dominated (anti-typical) pronoun residual",
        "n_residual": n,
        "GENERIC_typicality_prior_on_residual": {
            "selectional": 0.0146, "thematic": 0.0098, "combined": 0.0293,
            "source": "exp_coref_coherence_next_mention_prior_v1 (same cache) -- MEASURED DEAD, loses to twin"},
        "DISCOURSE_SPECIFIC_oracle_verb_or_obj": {
            "coverage_frac": rate(ds_appl, n), "applicable": ds_appl, "hit": ds_hit, "acc_on_covered": ds_acc,
            "acc_over_residual": rate(ds_hit, n)},
        "DISCOURSE_SPECIFIC_verb_only": {
            "coverage_frac": rate(verb_only_appl, n), "acc_on_covered": rate(verb_only_hit, verb_only_appl)},
        "info_free_twin_shuffled_affinity": {"acc_on_covered": twin_acc},
        "discourse_minus_twin": round(ds_acc - twin_acc, 4),
        "verdict": ("DISCOURSE_SPECIFIC_RECOVERS_WHERE_TYPICALITY_DEAD"
                    if (ds_acc > twin_acc + 0.10 and ds_acc > 0.20) else
                    ("DISCOURSE_SPECIFIC_ALSO_WEAK_RESIDUAL_IS_ONESHOT"
                     if rate(ds_appl, n) < 0.15 or ds_acc <= twin_acc + 0.05
                     else "PARTIAL_DISCOURSE_SIGNAL")),
        "note": ("if discourse-specific >> its twin AND >> the generic typicality prior, the wall is a "
                 "MISSING SITUATION MODEL (discourse-specific memory), not world knowledge -- buildable "
                 "(phase 1). Coverage bounds the reach of the exact-match version; a semantic-similarity "
                 "situation model would extend it."),
    }


_WNSIM: Dict[tuple, float] = {}


def _verb_sim(a: str, b: str) -> float:
    """WordNet Wu-Palmer similarity between two verbs (max over first-2 synsets each) -- a static,
    admissible, glass-box semantic-relatedness signal (NO LLM). Cached. 1.0 for identical."""
    if a == b:
        return 1.0
    key = (a, b) if a < b else (b, a)
    if key in _WNSIM:
        return _WNSIM[key]
    from nltk.corpus import wordnet as wn
    sa = wn.synsets(a, pos=wn.VERB)[:2]; sb = wn.synsets(b, pos=wn.VERB)[:2]
    best = 0.0
    for x in sa:
        for y in sb:
            s = x.wup_similarity(y) or 0.0
            if s > best:
                best = s
    _WNSIM[key] = best
    return best


def run_semantic(docs: Optional[int] = None, seed: int = SEED, thresh: float = 0.5) -> dict:
    """SIZE THE SITUATION-MODEL OPPORTUNITY: my exact-match discourse oracle is a LOWER BOUND (it needs the
    entity to do the SAME verb elsewhere). The real situation model stores SEMANTICALLY-related events. This
    replaces exact-verb-match with WordNet verb SIMILARITY (a glass-box semantic memory) and measures how
    much MORE of the residual becomes reachable -- the ceiling a semantic situation model could reach."""
    streams = load_streams(docs)
    res = _residual(streams)
    ent_ev = _doc_entity_events(streams)
    rng = np.random.default_rng(seed)
    n = len(res)
    sem_hit = sem_appl = twin_hit = twin_appl = 0
    for inst in res:
        doc = inst["doc"]; v = inst.get("gov_verb")
        ids = inst["cand_ids"]; gi = ids.index(inst["gold_cid"])
        if not v:
            continue
        ev = ent_ev[doc]
        aff = np.zeros(len(ids))
        for k, c in enumerate(ids):
            verbs = ev.get(c, {"verbs": Counter()})["verbs"]
            best = 0.0
            for v2, cnt in verbs.items():
                if c == inst["gold_cid"] and v2 == v and cnt <= 1:
                    continue   # exclude the query mention's own verb count
                s = _verb_sim(v, v2)
                if s > best:
                    best = s
            aff[k] = best
        if aff.max() >= thresh:
            sem_appl += 1
            sem_hit += int(int(np.argmax(aff)) == gi)
            perm = rng.permutation(len(ids))
            twin_appl += 1
            twin_hit += int(int(np.argmax(aff[perm]) if aff[perm].max() >= thresh else -1) == gi)

    def rate(h, a):
        return round(h / a, 4) if a else 0.0
    return {
        "anchor": "coref_residual_discourse_specific_SEMANTIC_v1", "n_residual": n, "sim_threshold": thresh,
        "SEMANTIC_discourse_oracle": {"coverage_frac": rate(sem_appl, n), "acc_on_covered": rate(sem_hit, sem_appl),
                                      "acc_over_residual": rate(sem_hit, n)},
        "info_free_twin": {"acc_on_covered": rate(twin_hit, twin_appl)},
        "semantic_minus_twin": round(rate(sem_hit, sem_appl) - rate(twin_hit, twin_appl), 4),
        "note": "vs the EXACT-match oracle (coverage 0.66, acc 0.16): a SEMANTIC situation model widens "
                "coverage and/or accuracy -> sizes how much of the residual the phase-1 build could reach. "
                "Still a glass-box (WordNet) LOWER bound on a full grounded situation model.",
    }


def self_test():
    # Fixture: an entity that does verb 'sign' twice in a doc has a within-doc verb affinity for 'sign';
    # a distractor that never does 'sign' has none. The discourse-specific signal must separate them.
    streams = [{"doc": "t", "stream": [
        {"sent": 0, "gold": 1, "role": "SUBJECT", "head_text": "john", "gov_verb": "sign", "obj_head": "treaty"},
        {"sent": 1, "gold": 2, "role": "SUBJECT", "head_text": "mark", "gov_verb": "walk", "obj_head": None},
        {"sent": 2, "gold": 1, "role": "SUBJECT", "head_text": "he", "gov_verb": "sign", "obj_head": "letter"},
    ]}]
    ev = _doc_entity_events(streams)
    assert ev["t"][1]["verbs"]["sign"] == 2, "entity 1 must have within-doc affinity for 'sign'"
    assert ev["t"][2]["verbs"]["sign"] == 0, "entity 2 must have no affinity for 'sign'"
    print("SELF-TEST PASS (within-doc entity-event affinity separates a repeat-actor from a distractor).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--semantic", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.semantic:
        print(json.dumps(run_semantic(docs=args.docs), indent=2)); return
    if args.run:
        print(json.dumps(run(docs=args.docs), indent=2)); return
    print("use --self-test | --run | --semantic")


if __name__ == "__main__":
    main()
