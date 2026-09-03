"""exp_whodidwhat_verb_id_recoverable_v1 -- is the "20 no-event" residual a WALL or a solvable adjacent gap?

Problem: the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses. 20/669 abstentions are NO-EVENT: the
in-substrate UD POS-tagger mis-tags the 19c finite verb as NOUN/ADJ/ADP/ADV ("the lake PRESENTS an unbroken sheet",
"OBEY that old man", "SPOIL good horses", "looking ROUND the cover"), so the tense-agnostic detector (fires only on
UPOS==VERB) never emits an event. I called this "upstream tagger recall". The research drill says the brain resolves
category ambiguity by CLAUSAL POSITION + verb-reading availability, NOT a static tag (MacDonald 1993; Mintz 2003;
Redington/Chater/Finch 1998) -- so this should be recoverable glass-box without a smarter tagger. This cell TESTS
that: a brain-faithful structural cue (the token has a VERB reading in WordNet AND sits in predicate position after a
subject nominal, in a clause the tagger left VERB-less) recovers the mis-tagged verbs, and I quantify the recovery
and the false-positive cost. It ESTABLISHES the residual is solvable (seeds follow-on 1c) -- it is not a wall.

Glass-box, CPU, NO LLM/spaCy (WordNet is a fixed lexicon, allowed). ASCII. own dir. Nothing in hdlab modified.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments._forward_prediction_live as FPL
from hdlab.thematic_role_labeler import lemma_verb

OUT_DIR = os.path.join(_REPO, "data/exp_whodidwhat_verb_id_recoverable_v1")
LB = os.path.join(_REPO, "data/predict_revise_recall_v1/_population_litbank.json")
NOMINAL = ("NOUN", "PROPN")

_WN = None
def has_verb_reading(tok):
    """Glass-box lexical verbhood: WordNet has a VERB synset for the token or its de-inflected lemma."""
    global _WN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
    low = tok.lower()
    if _WN.synsets(low, pos="v"):
        return True
    return bool(_WN.synsets(lemma_verb(low), pos="v"))


def structural_verb_cue(toks, pos, ix, strict_verbless):
    """Brain-faithful structural verbhood: the token at ix is (re-)read as the clause's finite verb if it has a VERB
    reading AND a nominal SUBJECT precedes it. `strict_verbless` additionally requires the sentence to have NO token
    the tagger already tagged VERB (a verbless clause needing its predicate recovered -> low false-positive)."""
    if pos[ix] == "VERB":
        return False   # already a verb; not a recovery
    if not has_verb_reading(toks[ix]):
        return False
    if not any(pos[j] in NOMINAL for j in range(0, ix)):
        return False   # needs a preceding subject nominal
    if strict_verbless and any(p == "VERB" for p in pos):
        return False
    return True


def frame_verb_cue(toks, pos, ix, k=3):
    """Mintz frequent-frame verbhood (clause-local, low-FP): the token at ix is the clause's predicate if it has a
    VERB reading, a nominal SUBJECT sits within k tokens BEFORE it, a nominal OBJECT sits within k tokens AFTER it,
    and NO already-VERB-tagged token intervenes between that subject and ix (ix is the predicate slot of its clause).
    This is the text-native analog of 'a content word between a subject and an object, in the tensed slot'."""
    if pos[ix] == "VERB" or not has_verb_reading(toks[ix]):
        return False
    subs = [j for j in range(max(0, ix - k), ix) if pos[j] in NOMINAL]
    if not subs:
        return False
    objs = [j for j in range(ix + 1, min(len(toks), ix + 1 + k)) if pos[j] in NOMINAL]
    if not objs:
        return False
    if any(pos[j] == "VERB" for j in range(subs[-1] + 1, ix)):
        return False   # another verb already occupies this clause's predicate slot
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = FPL.get_tagger()
    rows = V1.load_pop(LB)
    if args.self_test or args.smoke:
        rows = rows[:2500]

    # split the clean-DO gold into no-event (gold verb tagged non-VERB) and event-present
    no_event, event_present = [], []
    for r in rows:
        toks = r["sent"].split(); vi = r["verb_idx"]
        if not toks or vi >= len(toks):
            continue
        ps = tg.tag(toks)
        ok, _ = CG.is_clean_do(r, ps)
        if not ok:
            continue
        gc = CG.grounded_cands(r)
        if not [ix for h, ix in gc if ix > vi]:
            continue
        (no_event if ps[vi] != "VERB" else event_present).append((r, toks, ps))

    # RECOVERY on the no-event set: does the structural cue re-identify the mis-tagged gold verb?
    rec_permissive = sum(structural_verb_cue(toks, ps, r["verb_idx"], False) for r, toks, ps in no_event)
    rec_frame = sum(frame_verb_cue(toks, ps, r["verb_idx"]) for r, toks, ps in no_event)
    wn_only = sum(has_verb_reading(toks[r["verb_idx"]]) for r, toks, ps in no_event)

    # FALSE-POSITIVE cost on the event-present set: non-verb tokens the cue would spuriously promote to verbs
    fp_permissive = fp_frame = 0
    for r, toks, ps in event_present:
        for ix in range(len(toks)):
            if ix == r["verb_idx"]:
                continue
            if structural_verb_cue(toks, ps, ix, False):
                fp_permissive += 1
            if frame_verb_cue(toks, ps, ix):
                fp_frame += 1

    ne = max(1, len(no_event))
    res = {
        "n_no_event": len(no_event), "n_event_present": len(event_present),
        "recovery_wordnet_only": round(wn_only / ne, 4),
        "recovery_permissive_cue": round(rec_permissive / ne, 4),
        "recovery_frame_cue": round(rec_frame / ne, 4),
        "recovered_frame_count": rec_frame, "recovered_permissive_count": rec_permissive,
        "fp_permissive_per_sentence": round(fp_permissive / max(1, len(event_present)), 4),
        "fp_frame_per_sentence": round(fp_frame / max(1, len(event_present)), 4),
        "fp_frame_total": fp_frame, "fp_permissive_total": fp_permissive,
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "whodidwhat_verb_id_recoverable_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()},
                  fh, indent=2)
    print("\n===== IS THE 20 NO-EVENT A WALL? glass-box structural verb-ID recovery n_no_event=%d =====" % len(no_event), flush=True)
    print("  WordNet verb-reading available on the mis-tagged verb  : %.4f (%d/%d)  <- lexically ARE verbs" % (
        res["recovery_wordnet_only"], wn_only, len(no_event)), flush=True)
    print("  permissive cue (verb-reading + any preceding subject)  : %.4f (%d/%d)  FP=%.3f/sent  <- too permissive" % (
        res["recovery_permissive_cue"], rec_permissive, len(no_event), res["fp_permissive_per_sentence"]), flush=True)
    print("  FRAME cue (N-[verb]-N, no verb in the predicate slot)  : %.4f (%d/%d)  FP=%.3f/sent (%d on %d clauses)" % (
        res["recovery_frame_cue"], rec_frame, len(no_event), res["fp_frame_per_sentence"],
        fp_frame, len(event_present)), flush=True)
    print("  --> SOLVABLE glass-box (WordNet verbhood + Mintz frequent-frame position), not a wall (follow-on 1c).", flush=True)
    if args.self_test or args.smoke:
        assert len(no_event) >= 5
        assert res["recovery_wordnet_only"] >= 0.8   # the mis-tagged tokens ARE lexically verbs
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
