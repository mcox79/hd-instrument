"""DIAGNOSIS for wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on.

Reproduces the measured regression (coref_acc 0.48 OFF -> 0.02 ON with referent_per_np) FIRST-HAND on
real LitBank docs, then DECISIVELY separates the two candidate causes so the fix targets the real one:

  EFFECT A  SCORING POLLUTION -- the pronoun still resolves to a gold-co-referent nominal, but
            head_to_cluster[head] (keyed by SURFACE STRING, last-write-wins) was overwritten by a
            later FRESH-SINGLETON referent, so resolved_cluster != gold_cluster.
  EFFECT B  RESOLUTION DERAILMENT -- the flood of NP-head referents (every content noun, not just the
            ~9% coref column) derails the pool pick, so the pronoun binds a NON-co-referent entity.

METHOD: re-score each ON resolution by whether resolved_head is GOLD-co-referent with the pronoun's
gold cluster (the coref-column parse is the reference). If the ORACLE-rescored ON acc ~= OFF, the
resolution is fine and the loss is A (a clustering/keying fix). If it stays low, the loss is B (the
pool is genuinely derailed and the linker must canonicalize the entities, not just the cluster ids).

Glass-box, NO external LLM. Reference-only use of the gold coref column for the diagnostic rescore.
Run: .venv/Scripts/python.exe experiments/exp_referent_coref_linking_diagnosis_v1.py
"""
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, SUP_KW, LOCAL_WINDOW
from hdlab.coref import parse_litbank_conll, build_pronoun_targets
from hdlab.referent_per_np import referent_per_np_source
import experiments.exp_name_entity_clustering_v1 as NC
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer


def _docs(n):
    """Real LitBank docs that have a coref CoNLL on disk (order = who_did_what gold order)."""
    wdw = json.load(open(os.path.join(_REPO, "data/litbank/who_did_what_events.json"), encoding="utf-8"))
    out = []
    for r in wdw:
        p = os.path.join(NC.CONLL_DIR, r["doc"] + ".conll")
        if os.path.exists(p):
            out.append((r["doc"], p))
        if len(out) >= n:
            break
    return out


def _gold_head_clusters(conll_path, gaz):
    """head(lower) -> set(gold clusters it appears in), from the coref column (reference for the rescore)."""
    mentions, _ = parse_litbank_conll(conll_path, name_gender_map=gaz)
    hc = {}
    for m in mentions:
        hc.setdefault(m["head"].lower(), set()).add(m["cluster"])
    return hc


def _resolve_records(reader, conll_path, gaz, rnp):
    """Reproduce the reader's _read_entities resolve call exactly, returning the per-target records
    (which carry resolved_head -- CorefResolution drops it, so we call resolve_stream directly)."""
    if rnp:
        if reader._rnp_tagger is None:
            from hdlab.pos_tagger import PosTagger
            from hdlab.situation_reader import _FRONTEND_POS_ASSET
            reader._rnp_tagger = PosTagger.load(_FRONTEND_POS_ASSET)
        mentions, n_sents = referent_per_np_source(conll_path, reader._rnp_tagger, name_gender_map=gaz)
    else:
        mentions, n_sents = parse_litbank_conll(conll_path, name_gender_map=gaz)
    targets = build_pronoun_targets(mentions)
    if not targets:
        return [], mentions, n_sents
    sid = [i // LOCAL_WINDOW for i in range(n_sents)]
    recs = reader.reader_ec.resolve_stream(
        mentions, targets, scene_ids=sid, topical_mode="rolemass",
        query_memory=True, centrality_mode="event_role", **SUP_KW)
    return recs, mentions, n_sents


def run(n_docs=8):
    gaz = load_given_gazetteer()
    reader = SituationReader(gaz=gaz)            # one reader; reader_ec is stateless across resolve_stream calls
    docs = _docs(n_docs)

    off_correct = off_att = off_n = 0
    on_correct = on_att = on_n = 0
    # diagnosis counters (ON)
    on_right_entity = 0        # resolved_head is gold-co-referent with the pronoun (right entity found)
    on_scored_correct = 0      # actually scored correct
    wrong_but_right_entity = 0 # scored WRONG yet resolved a gold-co-referent head  -> EFFECT A (pollution)
    wrong_and_wrong_entity = 0 # scored WRONG and resolved a non-co-referent head    -> EFFECT B (derailment)
    n_singleton_ratio = []     # per doc: fraction of nominal referents that are fresh singletons

    per_doc = []
    for doc, p in docs:
        # OFF (coref-column source) -- the deployment floor
        recs_off, _, _ = _resolve_records(reader, p, gaz, rnp=False)
        oc = sum(r["correct"] for r in recs_off); oa = sum(r["attempted"] for r in recs_off)
        off_correct += oc; off_att += oa; off_n += len(recs_off)

        # ON (referent-per-NP source) -- the regression
        recs_on, mentions_on, n_sents = _resolve_records(reader, p, gaz, rnp=True)
        nc = sum(r["correct"] for r in recs_on)
        on_correct += nc; on_att += sum(r["attempted"] for r in recs_on); on_n += len(recs_on)

        # singleton ratio: nominal referents whose cluster is a fresh singleton (appears once, non-pron)
        clcount = {}
        for m in mentions_on:
            if not m["is_pronoun"]:
                clcount[m["cluster"]] = clcount.get(m["cluster"], 0) + 1
        nom = [m for m in mentions_on if not m["is_pronoun"]]
        sing = sum(1 for m in nom if clcount[m["cluster"]] == 1)
        n_singleton_ratio.append(sing / max(1, len(nom)))

        # DIAGNOSIS rescore
        hc = _gold_head_clusters(p, gaz)
        for r in recs_on:
            g = r["gold_cluster"]
            rh = (r.get("resolved_head") or "").lower()
            right_entity = bool(rh) and (g in hc.get(rh, set()))
            if right_entity:
                on_right_entity += 1
            if r["correct"]:
                on_scored_correct += 1
            else:
                if right_entity:
                    wrong_but_right_entity += 1
                else:
                    wrong_and_wrong_entity += 1
        per_doc.append((doc, len(recs_off), oc, len(recs_on), nc))

    def acc(c, n):
        return (c / n) if n else float("nan")

    print("=" * 90)
    print("REPRODUCE THE REGRESSION (pooled over %d docs)" % len(docs))
    print("  OFF  coref-column source : coref_acc = %.4f  (correct %d / targets %d ; attempted %d)"
          % (acc(off_correct, off_n), off_correct, off_n, off_att))
    print("  ON   referent-per-NP     : coref_acc = %.4f  (correct %d / targets %d ; attempted %d)"
          % (acc(on_correct, on_n), on_correct, on_n, on_att))
    print("  singleton-cluster ratio of ON nominal referents: mean %.3f" %
          (sum(n_singleton_ratio) / len(n_singleton_ratio)))
    print("-" * 90)
    print("DECISIVE DIAGNOSIS (ON targets, n=%d)" % on_n)
    print("  resolved the RIGHT entity (gold-co-referent head) : %d  (%.4f)"
          % (on_right_entity, acc(on_right_entity, on_n)))
    print("  ...of which actually SCORED correct               : %d  (%.4f)"
          % (on_scored_correct, acc(on_scored_correct, on_n)))
    print("  WRONG score but RIGHT entity  -> EFFECT A pollution: %d" % wrong_but_right_entity)
    print("  WRONG score and WRONG entity  -> EFFECT B derail   : %d" % wrong_and_wrong_entity)
    print("  ORACLE-rescored ON acc (right-entity credit)       : %.4f" % acc(on_right_entity, on_n))
    print("-" * 90)
    print("READING:")
    print("  If ORACLE-rescored ON ~= OFF -> the RESOLUTION is intact; loss is A (clustering/keying).")
    print("  If ORACLE-rescored ON stays low -> the pool is DERAILED; loss is B (need canonical entities).")
    print("=" * 90)
    return {
        "off_acc": acc(off_correct, off_n), "on_acc": acc(on_correct, on_n),
        "on_oracle_acc": acc(on_right_entity, on_n),
        "effect_A_pollution": wrong_but_right_entity, "effect_B_derail": wrong_and_wrong_entity,
        "off_n": off_n, "on_n": on_n,
    }


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    run(n)
