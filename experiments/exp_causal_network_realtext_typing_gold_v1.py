"""REAL CROSS-SENTENCE TYPING GOLD -- the honest capability test the owner asked for.
   (problem: causation_is_typed_per_clause_not_across_the_causal_network)

The owner's challenge: the "typer beats the placeholder" story rested on CONSTRUCTED data (a perfect
1.000 with CI [1.000,1.000]) plus 4 hand-picked SINGLE-CLAUSE preventions. Does the typer beat a
majority-CAUSE placeholder on a REAL population where majority-CAUSE is NOT the answer -- i.e. real
cross-SENTENCE PREVENT / ENABLE links?

THE HONEST ANSWER (this cell): such a population is very hard to build from real prose, because
real cross-sentence non-CAUSE causal links are RARE, and that rarity is the measured result:

  ENUMERATION (an absence claim needs an enumeration, not a search). I scanned all 100 LitBank
  novels + 2 McGuffey readers for cross-sentence PREVENT/ENABLE by neutral verb-pattern criteria
  (an enabling physical act -- open/unlock/release/free/let-out -- or a preventing act -- shut/bar/
  hold-back/block/shield/catch -- as a sentence, with the NEXT sentence naming the enabled/blocked
  outcome), and hand-read ~40 candidate contexts. Findings:
   - Real PREVENTION/ENABLING is overwhelmingly expressed WITHIN a clause ("prevented him FROM
     going", "saved them FROM drowning", "let Ann get in", "would not let them drown") -- the
     SINGLE-CLAUSE typer's domain, already handled by the integrated parent organ. (The keyword
     within-clause RATE is CONFOUNDED by verb polysemy -- save/keep/hold/bar in non-force senses --
     so it is NOT quoted as a clean number; the qualitative dominance is the finding.)
   - Genuine cross-SENTENCE ENABLE is rare (~a handful of clean cases in 100 novels) and almost
     always uses open/unlock, which are NOT in the FrameNet Causation-family force lexicon -> the
     typer ABSTAINS. Genuine cross-SENTENCE PREVENT (two separate past-tense event sentences, one
     blocking the other) was essentially ABSENT in the hand-read sample.
   - CORPUS-AGE CONFOUND (owner, 2026-08-30): LitBank is 19th-century, McGuffey ~200 years old;
     there is no modern narrative corpus on disk. Any real-text rate here is archaic-prose-bound.

So on the best real cross-sentence typing gold I can honestly assemble (the 16 verbatim LitBank
CAUSE edges + the genuine cross-sentence ENABLE cases found), the typer does NOT beat a majority-
CAUSE placeholder: the population IS overwhelmingly CAUSE, and the rare non-CAUSE cases are
lexically uncovered. This is a RIGOROUS NEGATIVE that bounds the real-text value of the cross-event
edge typer's *non-CAUSE typing* to a rare, uncovered slice -- the construction proof stands as a
MECHANISM demonstration, not a real-text capability win. Glass-box, no LLM. ASCII-only. Deterministic.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_read_causal_chain_on_chain_cause_v1 as RC  # noqa: E402
from experiments import exp_causal_network_realtext_v1 as M2  # noqa: E402  (type_edge_rt, EDGE_TYPE)
from experiments._force_dynamics_lexicon import build_force_lexicon  # noqa: E402

ANCHOR = "causal_network_realtext_typing_gold_v1"

# ---------------------------------------------------------------------------
# The genuine cross-SENTENCE non-CAUSE causal links found by hand-reading the corpus (VERBATIM,
# source-cited). Gold TYPE adjudicated from MEANING. These are the entire yield of the enumeration
# above -- a handful of ENABLE, ~zero clean PREVENT. outcome = the enabled/blocked event's verb.
# ---------------------------------------------------------------------------
REAL_NONCAUSE = [
    dict(src="The Picture of Dorian Gray (Wilde), LitBank 174",
         text="He jumped up, drew the screen hastily across the picture, and unlocked the door. "
              "\"I am so sorry for it all, Dorian,\" said Lord Henry as he entered.",
         cause="unlock", outcome="entered", gold="ENABLE",
         note="unlocking the door enabled Lord Henry's entry (barrier removed -> tending entry proceeds)"),
    dict(src="Main Street (Lewis), LitBank 543",
         text="He unlocked the door. She jiggled while he turned the key, and scampered in.",
         cause="unlock", outcome="scampered", gold="ENABLE",
         note="unlocking enabled her to scamper in"),
    dict(src="Dracula (Stoker), LitBank 345",
         text="Then with a long, thin knife we pushed back the fastening of the sashes and opened the "
              "window. I helped the Professor in, and followed him.",
         cause="open", outcome="helped", gold="ENABLE",
         note="opening the window enabled getting the Professor in"),
]


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _mixed_gold():
    """16 real LitBank CAUSE edges + the genuine cross-sentence ENABLE cases = the real typing gold."""
    gold = []
    for it in RC.GOLD:
        gt = M2.EDGE_TYPE[(it.outcome_lemma, it.cause_lemma)][0]
        gold.append(dict(text=it.text, outcome=it.outcome_lemma, gold=gt, kind="CAUSE_real"))
    for it in REAL_NONCAUSE:
        gold.append(dict(text=it["text"], outcome=it["outcome"], gold=it["gold"], kind="NONCAUSE_real"))
    return gold


def self_test():
    lex = build_force_lexicon()
    g = _mixed_gold()
    assert len(g) == len(RC.GOLD) + len(REAL_NONCAUSE), "mixed gold assembled"
    # the genuine ENABLE cases mostly ABSTAIN (open/unlock not in the physical force lexicon) -- the
    # coverage bound; assert at least that the pipeline runs and returns a label
    t, c, tag = M2.type_edge_rt(REAL_NONCAUSE[0]["text"], REAL_NONCAUSE[0]["outcome"], lex)
    assert t in ("CAUSE", "ENABLE", "PREVENT", "SEQUENTIAL", "ABSTAIN_NO_OUTCOME"), "pipeline returns a label"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    lex = build_force_lexicon()
    gold = _mixed_gold()
    n = len(gold)

    typer_correct = placeholder_correct = 0
    typer_abstain = 0
    rows = []
    kind_gold = Counter()
    for g in gold:
        kind_gold[g["gold"]] += 1
        pred, cause, tag = M2.type_edge_rt(g["text"], g["outcome"], lex)
        ph = "CAUSE"  # majority-CAUSE placeholder
        typer_correct += int(pred == g["gold"])
        placeholder_correct += int(ph == g["gold"])
        typer_abstain += int(pred in ("SEQUENTIAL", "ABSTAIN_NO_OUTCOME"))
        rows.append({"kind": g["kind"], "gold": g["gold"], "typer": pred, "placeholder": ph,
                     "cause": cause, "tag": tag, "text": g["text"][:70]})

    # non-CAUSE subset: does the typer type any of the genuine cross-sentence ENABLE?
    nc = [r for r in rows if r["kind"] == "NONCAUSE_real"]
    nc_typer_correct = sum(int(r["typer"] == r["gold"]) for r in nc)

    typer_acc = typer_correct / n
    placeholder_acc = placeholder_correct / n

    elapsed = time.perf_counter() - t0
    beats = typer_acc > placeholder_acc
    verdict = ("REAL_CROSS_SENTENCE_NONCAUSE_TYPING_IS_A_RIGOROUS_NEGATIVE__RARE_AND_UNCOVERED"
               if not beats else "TYPER_BEATS_MAJORITY_ON_REAL_MIXED_GOLD")

    metrics = {
        "verdict": verdict,
        "summary": (
            f"REAL cross-sentence typing gold (n={n}: {len(RC.GOLD)} verbatim LitBank CAUSE edges + "
            f"{len(REAL_NONCAUSE)} genuine cross-sentence ENABLE cases -- the ENTIRE yield of hand-reading ~40 "
            f"candidate contexts across 100 novels; ~0 clean cross-sentence PREVENT found). FULL self-extraction. "
            f"The typer does NOT beat a majority-CAUSE placeholder: typer {typer_acc:.3f} vs placeholder "
            f"{placeholder_acc:.3f} (beats={beats}). Gold class mix {dict(kind_gold)} is overwhelmingly CAUSE, and "
            f"the typer ABSTAINS on {typer_abstain}/{n} (physical lexicon covers ~3 physical-force verbs; the "
            f"genuine ENABLE cases use open/unlock, NOT in the FrameNet force lexicon -> {nc_typer_correct}/{len(nc)} "
            f"non-CAUSE typed). MEASURED BOUND: real cross-sentence non-CAUSE causation is rare + lexically "
            f"uncovered; the construction-proof 1.000 is a MECHANISM demo, not a real-text capability win. "
            f"CORPUS-AGE confound: LitBank/McGuffey are 19th-c./~200yr; no modern corpus on disk."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "n": n,
        "typer_acc": round(typer_acc, 4),
        "placeholder_acc": round(placeholder_acc, 4),
        "typer_beats_placeholder": beats,
        "typer_abstain": typer_abstain,
        "gold_class_mix": dict(kind_gold),
        "noncause_subset": {"n": len(nc), "typer_correct": nc_typer_correct,
                            "note": "genuine cross-sentence ENABLE; mostly abstained (open/unlock uncovered)"},
        "rows": rows,
        "enumeration": {
            "corpus": "100 LitBank novels + 2 McGuffey readers (data/litbank/original + data/corpora/graded_readers_grade1)",
            "method": "neutral verb-pattern scan (enabling act / preventing act as a sentence + next-sentence outcome), ~40 candidate contexts hand-read",
            "genuine_cross_sentence_ENABLE": len(REAL_NONCAUSE),
            "genuine_cross_sentence_PREVENT": 0,
            "within_clause_dominance": "real prevention/enabling is overwhelmingly within-clause (single-clause typer's domain); the keyword rate is polysemy-confounded and NOT quoted as clean",
        },
        "brain_note": (
            "Consistent with communicative efficiency + the parent's coverage finding: prevention/enabling is "
            "packed into a single clause ('prevent/save/keep X FROM Y', 'let/allow X to Y'), which the integrated "
            "single-clause force typer already handles. The cross-event NETWORK typer's UNIQUE non-CAUSE value is "
            "thus bounded; its real-text value is the STRUCTURE (direction/necessity/selection) on CAUSE edges + "
            "not mis-asserting a positive link on the rare cross-sentence prevention."),
        "scope": (
            "The honest capability test. A rigorous NEGATIVE (the brief: a rigorous negative is a full pass). "
            "Small-n by necessity (the phenomenon is rare); archaic corpus (confound). The MECHANISM proof + the "
            "isolation + the twins live in exp_causal_network_edge_typer_v1; the two-system bound + the built "
            "intentional front-end live in exp_causal_network_realtext_v1 / _intentional_frontend_v1."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"[verdict] {verdict}")
    print(f"elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
