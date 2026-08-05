# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): four prediction-vectors hash-compared --
#   arm_c_local / old_blind_maintained (NULL) / new_grounded_maintained / pertoken_pooling;
#   new_grounded MUST differ from old_blind (that IS the grounding-fix discriminator).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb: n/a -- fixed 10-item eval, no capacity sweep.
# - calibration_check: default_ok_for_this_regime (WINDOW_LINES=400 single fixed constant reused
#   verbatim from the v1 probe; the two-stage grounding lexicons/theta are FROZEN, never tuned here).
# - cell_chunked: false (n=10 items, single deterministic pass; spaCy parse of only entity-mentioning
#   paragraphs -> seconds).
# - deterministic_seeding: no RNG anywhere (arm_c fit is seed-independent; grounding is deterministic).
# - all numbers MEASURED@ tagged in the completion report, not this file.
#
# C-D (part 1): SITUATION-MODEL AFFECT DIMENSION -- a per-entity MAINTAINED affect trajectory across a
# passage, populated by the VALIDATED two-stage grounding (governor class + WordNet-animacy event-
# assembly, exp_bridge1_event_assembly_open_vocab_v1 / exp_bridge1_governor_grounding_v1; certified
# notes/landed_vet_bridge1_foundation.md) instead of resolve_valence_blind, bound to the coref-lite
# protagonist index. This is the affect DIMENSION ONLY. The forward-projection / PREDICTION step is
# C-D PART 2 (a separate follow-up) and is intentionally NOT attempted here.
#
# WHAT IT EXTENDS: the v1 blind-lexicon probe
# (experiments/exp_maintained_affect_narrative_irony_probe_v1.py, verdict NULL_FALSE_POSITIVES:
# narrative_missed_recovered=1/3, sincere_fp=2/5). Its glass-box diagnosis: the coref + wide-window
# maintenance MECHANISM worked, but resolve_valence_blind (bag-of-harm-tokens) was the blocker --
# it missed dread with no HARM token and false-fired on incidental HARM tokens ("missed a trick",
# "studied hard"). This cell keeps the identical maintenance mechanism and swaps ONLY the per-event
# scorer to the certified grounding.
#
# DECLARED SIMPLIFICATION (flagged, not silently substituted -- same as the v1 probe): coref =
# literal entity-name-variant string match per paragraph (Centering-lite most-recent-compatible-
# antecedent backward search over the prior window), NOT the full CorefReader/SituationModel stack
# (SituationModel.read needs a CoNLL mention stream unavailable for raw novel text at this scope).
# The GROUNDED SCORER is the real certified organ; the coref binding is the declared lite proxy.
"""Standalone C-D part-1 probe. Reuses (never re-derives) exp_grounded_appraisal_transfer_to_text_v1's
fitted arm_c hypothesis + resolve_valence_context/blind + get_corpus_context/_corpus_lines + gold, the
v1 probe's paragraph splitter + AGENT_FOR_ITEM/NAME_VARIANTS + subset ids, and the VALIDATED two-stage
grounding (exp_bridge1_event_assembly_open_vocab_v1.event_type_for_item_real + FORCE_CLASS_HARM_REAL +
real_animacy_lookup; exp_bridge1_governor_grounding_v1.GOVERNOR_VERB_CLASS). Adds ONE new mechanism: a
GROUNDED per-event affect scorer (spaCy verb+direct-object extraction -> two-stage grounding) feeding
the SAME wide-window maintained-affect trajectory + incongruity override as v1. Arms: (a) arm_c_local
(no maintenance), (b) old_blind_maintained (= v1's NULL), (c) new_grounded_maintained, (d) per-token
pooling (entity-blind blind-vote over the window; integration must beat it)."""
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "maintained_affect_grounded_narrative_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import exp_grounded_appraisal_transfer_to_text_v1 as armc  # noqa: E402 (REUSED, unchanged)
import exp_maintained_affect_narrative_irony_probe_v1 as v1probe  # noqa: E402 (REUSED harness/items)
# VALIDATED two-stage grounding (certified notes/landed_vet_bridge1_foundation.md) -- the FIX:
import experiments.exp_bridge1_event_assembly_open_vocab_v1 as ea  # noqa: E402
import experiments.exp_bridge1_governor_grounding_v1 as bridge1  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402

EXPECTED_N_ITEMS = 10
WINDOW_LINES = v1probe.WINDOW_LINES     # 400, reused verbatim
LOCAL_EXCLUDE = v1probe.LOCAL_EXCLUDE   # 3
AGENT_FOR_ITEM = v1probe.AGENT_FOR_ITEM
NAME_VARIANTS = v1probe.NAME_VARIANTS
NARRATIVE_MISSED_IDS = v1probe.NARRATIVE_MISSED_IDS   # {irony_002, irony_003, irony_005}
LOCAL_CUE_IDS = v1probe.LOCAL_CUE_IDS                 # {irony_001, irony_004}
SINCERE_IDS = v1probe.SINCERE_IDS

# ---- spaCy tagger (SUPPLIED grammar, same source the situation_reader/litbank path uses; NOT an
# LLM in the reasoning loop -- glass-box POS+dep preprocessing). Loaded once. ----
_NLP = None


def _nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    return _NLP


# ------------------------------------------------------------------- GROUNDED per-event affect scorer
def grounded_paragraph_class(p_text):
    """Run the VALIDATED two-stage grounding over every (verb, direct-object) clause in the paragraph
    and aggregate to a single paragraph affect class in {HARM, HELP, NA}. Glass-box; returns
    (class, witness_list). Priority HARM > HELP > NA (the incongruity-override hypothesis targets
    established NEGATIVE affect exposing a false-positive surface reading)."""
    doc = _nlp()(p_text)
    tokens = [t.text for t in doc]
    pos = [t.pos_ for t in doc]
    saw_harm = False
    saw_help = False
    witness = []
    for tok in doc:
        if tok.pos_ != "VERB":
            continue
        gov_lemma = lemma_verb(tok.text)
        gclass = bridge1.GOVERNOR_VERB_CLASS.get(gov_lemma, "UNK")
        # find a direct object of this verb (spaCy dep) -> event-assembly refinement
        dobj = None
        for ch in tok.children:
            if ch.dep_ == "dobj" and ch.pos_ in ("NOUN", "PROPN", "PRON"):
                dobj = ch
                break
        clause_cls = None
        if dobj is not None:
            obj_word = dobj.text.lower().strip(".,\"'();:")
            a = ea.real_animacy_lookup(obj_word, dobj.pos_)
            amap = {obj_word: a} if a is not None else {}
            item = {"tokens": tokens, "pos": pos, "target_idx": dobj.i, "target_word": obj_word}
            et, _cat, _gw = ea.event_type_for_item_real(
                item, amap, ea.FORCE_CLASS_HARM_REAL, bridge1.GOVERNOR_VERB_CLASS)
            if et == "BLOCK_HIGH":
                clause_cls = "HARM"          # animate patient + force verb -> harm event (open-vocab)
            elif et == "NEUTRAL":
                clause_cls = "NEUTRAL"       # inanimate patient -> goal/artifact, NOT harm (C-C fix)
        if clause_cls is None:
            # governor dominance-default (stage-1 grounding), unchanged
            if gclass == "HARM":
                clause_cls = "HARM"
            elif gclass == "HELP":
                clause_cls = "HELP"
        if clause_cls == "HARM":
            saw_harm = True
            witness.append({"verb": gov_lemma, "dobj": (dobj.text if dobj is not None else None),
                            "cls": "HARM"})
        elif clause_cls == "HELP":
            saw_help = True
            witness.append({"verb": gov_lemma, "dobj": (dobj.text if dobj is not None else None),
                            "cls": "HELP"})
    if saw_harm:
        return "HARM", witness
    if saw_help:
        return "HELP", witness
    return "NA", witness


def grounded_trajectory(novel, agent_name, surf_start):
    """Entity-BOUND maintained trajectory: scan paragraphs strictly BEFORE arm_c's own local window
    that mention an entity-name variant (coref-lite), score EACH with the grounded scorer. Returns
    list of (para_start_line, class, witness)."""
    lo = max(1, surf_start - WINDOW_LINES)
    hi = surf_start - LOCAL_EXCLUDE
    variants = NAME_VARIANTS[agent_name]
    traj = []
    for p_start, _p_end, p_text in v1probe.paragraphs_for(novel):
        if p_start < lo or p_start > hi:
            continue
        if not any(v in p_text for v in variants):
            continue
        cls, witness = grounded_paragraph_class(p_text)
        if cls != "NA":
            traj.append((p_start, cls, witness))
    return traj


def pertoken_pool_class(novel, surf_start):
    """PER-TOKEN POOLING baseline (integration must beat this): entity-BLIND, no coref binding, no
    maintained trajectory -- pool resolve_valence_blind votes over EVERY token/paragraph in the same
    window and majority-vote. Tests whether entity-binding + maintenance beats undifferentiated
    pooling."""
    lo = max(1, surf_start - WINDOW_LINES)
    hi = surf_start - LOCAL_EXCLUDE
    harm = help_ = 0
    for p_start, _p_end, p_text in v1probe.paragraphs_for(novel):
        if p_start < lo or p_start > hi:
            continue
        cls = armc.resolve_valence_blind(p_text)
        if cls == "HARM":
            harm += 1
        elif cls == "HELP":
            help_ += 1
    if harm == 0 and help_ == 0:
        return "NA"
    return "HARM" if harm >= help_ else "HELP"


def class_to_pred(cls):
    return "NEG" if cls == "HARM" else "POS"   # HARM->NEG; HELP/NEUTRAL/NA->POS (v1 convention)


def run_item(item, chosen_name, hypothesis):
    item_id = item["id"]
    novel = item["novel"]
    surface_text = item["surface_span"]["text"]
    surf_start = item["surface_span"]["line_range"][0]
    local_ctx = armc.get_corpus_context(novel, item["surface_span"]["line_range"], window=2)
    arm_c_local_cls = armc.resolve_valence_context(chosen_name, hypothesis, surface_text, local_ctx)
    arm_c_pred = class_to_pred(arm_c_local_cls)

    agent_name, agent_source = AGENT_FOR_ITEM[item_id]
    true_label = "NEG" if item["valence_type"] == "irony" else "POS"

    # (b) OLD BLIND maintained (v1's NULL) -- recomputed live via the v1 probe's own functions.
    blind_traj = v1probe.maintained_affect_trajectory(novel, agent_name, surf_start)
    blind_state = v1probe.maintained_state(blind_traj)
    if arm_c_local_cls != "HARM" and blind_state == "HARM":
        blind_final = "HARM"
    else:
        blind_final = arm_c_local_cls
    blind_pred = class_to_pred(blind_final)

    # (c) NEW GROUNDED maintained (the fix).
    g_traj = grounded_trajectory(novel, agent_name, surf_start)
    g_state = v1probe.maintained_state([(ln, c) for ln, c, _w in g_traj])
    g_override = False
    if arm_c_local_cls != "HARM" and g_state == "HARM":
        g_final = "HARM"
        g_override = True
    else:
        g_final = arm_c_local_cls
    g_pred = class_to_pred(g_final)

    # (d) PER-TOKEN POOLING (entity-blind, no maintenance).
    pool_state = pertoken_pool_class(novel, surf_start)
    if arm_c_local_cls != "HARM" and pool_state == "HARM":
        pool_final = "HARM"
    else:
        pool_final = arm_c_local_cls
    pool_pred = class_to_pred(pool_final)

    return {
        "id": item_id, "valence_type": item["valence_type"], "agent": agent_name,
        "agent_source": agent_source, "true_label": true_label,
        "arm_c_local_cls": arm_c_local_cls, "arm_c_local_pred": arm_c_pred,
        "arm_c_local_correct": arm_c_pred == true_label,
        "old_blind_state": blind_state, "old_blind_pred": blind_pred,
        "old_blind_correct": blind_pred == true_label,
        "grounded_trajectory": [{"para_start_line": ln, "cls": c, "witness": w} for ln, c, w in g_traj],
        "grounded_state": g_state, "grounded_override_fired": g_override,
        "grounded_final_cls": g_final, "grounded_pred": g_pred,
        "grounded_correct": g_pred == true_label,
        "pertoken_pool_state": pool_state, "pertoken_pool_pred": pool_pred,
        "pertoken_pool_correct": pool_pred == true_label,
        "used_contamination": {
            "reads_true_intent_valence_label": False, "reads_supporting_span_field": False,
            "reads_surface_valence_label": False,
            "window_scanned": [max(1, surf_start - WINDOW_LINES), surf_start - LOCAL_EXCLUDE],
        },
    }


def arms_must_differ(rows):
    def vec(key):
        return hashlib.sha256("".join(r[key] for r in rows).encode("ascii")).hexdigest()
    d_local = vec("arm_c_local_pred")
    d_blind = vec("old_blind_pred")
    d_grounded = vec("grounded_pred")
    d_pool = vec("pertoken_pool_pred")
    return {"arm_c_local_digest": d_local, "old_blind_digest": d_blind,
            "grounded_digest": d_grounded, "pertoken_pool_digest": d_pool,
            "grounded_differs_from_blind": d_grounded != d_blind,
            "grounded_differs_from_local": d_grounded != d_local}


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def compute(rows):
    def sub(ids, key):
        s = [r for r in rows if r["id"] in ids]
        return sum(1 for r in s if r[key]) / len(s) if s else None

    grounded_recovered = sorted(r["id"] for r in rows
                                if r["id"] in NARRATIVE_MISSED_IDS and r["grounded_correct"])
    old_blind_recovered = sorted(r["id"] for r in rows
                                 if r["id"] in NARRATIVE_MISSED_IDS and r["old_blind_correct"])
    grounded_fp = sum(1 for r in rows if r["id"] in SINCERE_IDS and r["grounded_pred"] == "NEG")
    old_blind_fp = sum(1 for r in rows if r["id"] in SINCERE_IDS and r["old_blind_pred"] == "NEG")
    pool_recovered = sorted(r["id"] for r in rows
                            if r["id"] in NARRATIVE_MISSED_IDS and r["pertoken_pool_correct"])
    pool_fp = sum(1 for r in rows if r["id"] in SINCERE_IDS and r["pertoken_pool_pred"] == "NEG")

    n_grounded = len(grounded_recovered)
    n_blind = len(old_blind_recovered)
    n_pool = len(pool_recovered)
    beats_pool = (n_grounded > n_pool) or (n_grounded == n_pool and grounded_fp < pool_fp)
    fps_cleared = grounded_fp == 0 and old_blind_fp > 0

    if n_grounded >= 2 and grounded_fp == 0 and beats_pool:
        verdict = "HARD_PASS"
    elif grounded_fp == 0 and (n_grounded > n_blind or fps_cleared):
        # grounding fix cleared the FPs / improved present-state; forward-dread needs C-D part 2
        verdict = "PARTIAL_NEEDS_PREDICTION"
    elif n_grounded <= n_blind and grounded_fp >= old_blind_fp:
        verdict = "HARD_FAIL_NO_BETTER_THAN_NULL"
    else:
        verdict = "MIDDLE_BAND"

    bands = {
        "grounded_narrative_recovered": grounded_recovered, "n_grounded_narrative": n_grounded,
        "old_blind_narrative_recovered": old_blind_recovered, "n_old_blind_narrative": n_blind,
        "pertoken_pool_narrative_recovered": pool_recovered, "n_pertoken_pool_narrative": n_pool,
        "grounded_sincere_fp": grounded_fp, "old_blind_sincere_fp": old_blind_fp,
        "pertoken_pool_sincere_fp": pool_fp,
        "grounded_beats_pooling": beats_pool, "old_2_fps_cleared": fps_cleared,
        "narrative_missed_acc": {"arm_c_local": sub(NARRATIVE_MISSED_IDS, "arm_c_local_correct"),
                                 "old_blind": sub(NARRATIVE_MISSED_IDS, "old_blind_correct"),
                                 "grounded": sub(NARRATIVE_MISSED_IDS, "grounded_correct"),
                                 "pertoken_pool": sub(NARRATIVE_MISSED_IDS, "pertoken_pool_correct")},
        "local_cue_acc": {"arm_c_local": sub(LOCAL_CUE_IDS, "arm_c_local_correct"),
                          "grounded": sub(LOCAL_CUE_IDS, "grounded_correct")},
        "sincere_acc": {"arm_c_local": sub(SINCERE_IDS, "arm_c_local_correct"),
                        "old_blind": sub(SINCERE_IDS, "old_blind_correct"),
                        "grounded": sub(SINCERE_IDS, "grounded_correct")},
    }
    return verdict, bands


def self_test():
    """Real-code-path self-test: fits the real arm_c hypothesis + runs the REAL grounded scorer
    (spaCy + two-stage grounding) on one known item at real scale. Also asserts the grounded scorer
    correctly abstains/refines on a couple of hand cases (open-vocab, not a synthetic branch)."""
    # unit assertions on the certified grounding path (open-vocab):
    h, _w = grounded_paragraph_class("She battered her nephew in the street.")
    assert h == "HARM", f"expected HARM (animate patient + force verb), got {h}"
    n, _w = grounded_paragraph_class("He beat the game after months of practice.")
    assert n != "HARM", f"'beat the game' must NOT be HARM (inanimate/goal patient), got {n}"
    chosen_name, chosen_result, _digest, _all = armc.fit_arm_c_hypothesis()
    gold = armc.load_gold()
    probe_item = next(it for it in gold if it["id"] == "grapp_irony_003")
    row = run_item(probe_item, chosen_name, chosen_result.hypothesis)
    assert row["grounded_pred"] in ("POS", "NEG")
    print(f"[self-test] battered->{h} beat_game->{n} | irony_003 local={row['arm_c_local_pred']} "
          f"grounded={row['grounded_pred']} traj_len={len(row['grounded_trajectory'])}", flush=True)
    return True


def main():
    t0 = time.perf_counter()
    v1probe._write_start_marker(OUTPUT_DIR, "full", EXPECTED_N_ITEMS)
    chosen_name, chosen_result, arm_c_digest, _all = armc.fit_arm_c_hypothesis()
    hypothesis = chosen_result.hypothesis
    gold = armc.load_gold()
    irony_items = [it for it in gold if it["item_type"] == "irony_vs_sincere_valence"]
    assert len(irony_items) == EXPECTED_N_ITEMS, (
        f"CARDINALITY_BREACH: expected {EXPECTED_N_ITEMS}, got {len(irony_items)}")

    rows = [run_item(it, chosen_name, hypothesis) for it in irony_items]
    verdict, bands = compute(rows)
    diff = arms_must_differ(rows)
    if not diff["grounded_differs_from_blind"]:
        raise AssertionError(
            "META_RULE_AF: grounded and old-blind prediction vectors are bit-identical -- the "
            "grounding swap changed nothing; investigate before trusting the verdict.")

    verdict_msg = (
        f"{verdict}: grounded_narrative={bands['n_grounded_narrative']}/3 "
        f"{bands['grounded_narrative_recovered']} vs old_blind_NULL={bands['n_old_blind_narrative']}/3 "
        f"{bands['old_blind_narrative_recovered']} vs pooling={bands['n_pertoken_pool_narrative']}/3 "
        f"| grounded_fp={bands['grounded_sincere_fp']}/5 (old_blind_fp={bands['old_blind_sincere_fp']}/5,"
        f" cleared={bands['old_2_fps_cleared']}) | beats_pooling={bands['grounded_beats_pooling']}")
    print(f"[result] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "run_mode": "full", "elapsed_s": time.perf_counter() - t0,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
        "n_items": len(rows), "arm_c_fitted_plugin": chosen_name,
        "arm_c_hypothesis_digest": arm_c_digest,
        "bands": bands, "arms_differ_verified": diff, "rows": rows,
    }
    _write_metrics(OUTPUT_DIR, metrics)
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        ok = self_test()
        print("SELF_TEST_PASS" if ok else "SELF_TEST_FAIL", flush=True)
        sys.exit(0 if ok else 1)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 (NOT BaseException; preserves SystemExit/KeyboardInterrupt)
        _write_crash(OUTPUT_DIR, e)
        raise
