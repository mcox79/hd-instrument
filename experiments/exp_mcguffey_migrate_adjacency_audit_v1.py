"""exp_mcguffey_migrate_adjacency_audit_v1 -- EVALUATE the reader components ADJACENT to role assignment
for brain fidelity + GENERALIZATION, with numbers (owner 2026-08-30: evaluate adjacencies, don't just name).

Two measurable adjacencies my role/situation-model migration leans on:

A. THE ANIMACY CUE (`animacy_lexicon` / `_is_animate_head`: a hard-coded ~40-word McGuffey-flavoured list +
   an NNP heuristic). It is a load-bearing proto-agent cue (Dowty). QUESTION: does the animacy->agent cue
   GENERALIZE from McGuffey to modern text, or is its validity a McGuffey artefact? We measure the cue's
   fire-rate and its role-predictive validity (P(agent|animate) vs P(agent|inanimate); animacy-as-role
   accuracy vs floor) on BOTH populations. A cue whose validity collapses on modern text is not
   brain-foundational (the brain's animacy is grounded/learned, not a word list).

B. ENTITY-TRACKING / COREF COVERAGE. My modern UD-EWT gold tracks entities by string identity over PROPN/NOUN
   heads -- UD ships no coref, so PRONOUN mentions are excluded. QUESTION: how much of the real entity-tracking
   challenge does string-identity MISS on modern text? We count what fraction of core-argument mentions are
   PRONOUNS (invisible to string identity) -- the size of the coref dimension the modern eval cannot test
   (and why a both-gold modern narrative corpus is the named next gold).

Writes only to data/exp_mcguffey_migrate_adjacency_audit_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_wire_organs_endtoend_v1 import _pos, _is_animate_head, IN_SCOPE_ROLES, load_gold  # noqa: E402
from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu, UD_TRAIN, UD_TEST  # noqa: E402

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_adjacency_audit_v1")
# KB_REFERENT: data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu


def mention_head_animate(mention):
    toks = _pos(mention)
    if not toks:
        return None
    # head = last token
    w, t = toks[-1]
    return _is_animate_head(w, t)


def animacy_audit(passages, label):
    """Fire-rate + role-predictive validity of the animacy cue on in-scope role mentions."""
    n = 0; animate = 0
    agent_given_animate = [0, 0]      # [agent, total]
    agent_given_inanimate = [0, 0]
    correct = 0                        # animacy-as-role: predict agent if animate else patient
    for p in passages:
        ment = {(nm, m["clause"]): m["mention"] for nm, ch in p["entities"].items() for m in ch}
        for q in p.get("target_queries", []):
            if q["gold_role"] not in IN_SCOPE_ROLES:
                continue
            m = ment.get((q["entity"], q["query_clause"]))
            if m is None:
                continue
            a = mention_head_animate(m)
            if a is None:
                continue
            n += 1
            is_agent = (q["gold_role"] == "agent")
            if a:
                animate += 1
                agent_given_animate[1] += 1
                agent_given_animate[0] += int(is_agent)
            else:
                agent_given_inanimate[1] += 1
                agent_given_inanimate[0] += int(is_agent)
            pred_agent = a
            correct += int(pred_agent == is_agent)
    def rate(x):
        return round(x[0] / x[1], 4) if x[1] else None
    return {
        "population": label, "n": n,
        "animacy_fire_rate": round(animate / n, 4) if n else None,
        "P_agent_given_animate": rate(agent_given_animate),
        "P_agent_given_inanimate": rate(agent_given_inanimate),
        "animacy_as_role_accuracy": round(correct / n, 4) if n else None,
        "cue_validity_gap": (round(rate(agent_given_animate) - rate(agent_given_inanimate), 4)
                             if agent_given_animate[1] and agent_given_inanimate[1] else None),
    }


def coref_coverage_audit():
    """In UD-EWT, what fraction of core-argument mentions are PRONOUNS (invisible to string-identity coref)?"""
    docs = parse_conllu(UD_TRAIN) + parse_conllu(UD_TEST)
    core = Counter()      # upos of the core-arg dependent
    for doc in docs:
        for sent in doc:
            byid = {t["id"]: t for t in sent["toks"]}
            for t in sent["toks"]:
                depfull = t["deprel"]; dep = depfull.split(":")[0]
                head = byid.get(t["head"])
                if head is None or head["upos"] != "VERB":
                    continue
                if dep in ("nsubj", "obj") or depfull == "nsubj:pass":
                    core[t["upos"]] += 1
    total = sum(core.values())
    pron = core.get("PRON", 0)
    tracked = core.get("PROPN", 0) + core.get("NOUN", 0)
    return {"total_core_args": total, "by_upos": dict(core.most_common()),
            "pronoun_fraction": round(pron / total, 4) if total else None,
            "string_identity_trackable_fraction": round(tracked / total, 4) if total else None,
            "note": "PRONOUN core-args are invisible to string-identity coref -> the modern eval cannot test "
                    "the pronoun entity-tracking dimension (which is LitBank's gold + the named both-gold gap)."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    modern = [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]
    mcg = load_gold()
    if args.self_test:
        modern = modern[:60]; mcg = mcg[:30]

    anim_mcg = animacy_audit(mcg, "MCGUFFEY_1830s")
    anim_mod = animacy_audit(modern, "MODERN_UD_EWT")
    coref = None if args.self_test else coref_coverage_audit()

    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(),
               "animacy_cue": {"MCGUFFEY_1830s": anim_mcg, "MODERN_UD_EWT": anim_mod},
               "coref_coverage": coref,
               "verdict": {
                   "animacy_cue_validity_collapses_on_modern":
                       (anim_mcg["cue_validity_gap"] or 0) - (anim_mod["cue_validity_gap"] or 0) > 0.15,
                   "animacy_fire_rate_mcg_vs_modern": [anim_mcg["animacy_fire_rate"], anim_mod["animacy_fire_rate"]],
               }}

    if args.self_test:
        assert anim_mcg["n"] > 0 and anim_mod["n"] > 0
        print("self-test PASS", json.dumps({"mcg_gap": anim_mcg["cue_validity_gap"],
                                            "mod_gap": anim_mod["cue_validity_gap"]}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 88)
    print("ADJACENCY AUDIT -- brain fidelity + generalization of reader components next to role assignment")
    print("=" * 88)
    print("\n[A] ANIMACY CUE (animacy_lexicon / _is_animate_head) -- does animacy->agent generalize?")
    for r in (anim_mcg, anim_mod):
        print(f"  {r['population']:16s} n={r['n']:4d}  fire {r['animacy_fire_rate']}  "
              f"P(agent|animate) {r['P_agent_given_animate']}  P(agent|inanimate) {r['P_agent_given_inanimate']}  "
              f"validity_gap {r['cue_validity_gap']}  role_acc {r['animacy_as_role_accuracy']}")
    print("\n[B] COREF / ENTITY-TRACKING COVERAGE (string-identity misses pronouns)")
    print(f"  core args={coref['total_core_args']}  by_upos={coref['by_upos']}")
    print(f"  PRONOUN fraction (invisible to string-identity) = {coref['pronoun_fraction']}  "
          f"string-id trackable = {coref['string_identity_trackable_fraction']}")
    print(f"\nVERDICT: {json.dumps(metrics['verdict'])}")
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
