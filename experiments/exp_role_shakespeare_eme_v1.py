"""Push -- register-invariance at the EXTREME + the POS-layer adjacent component, on real Early-Modern-English.

LitBank (19c) has archaic morphology at 0.014% of tokens; tinyshakespeare (EME) at 2.31% -- a 165x denser
regime, exactly where the brain's register-invariance advantage should show. Shakespeare is NOT on the live
reading path (grep), so this is a CAPABILITY test ("if the brain reads Shakespeare, we can once we understand"),
not a live-cost claim.

DEFINITIONAL GOLD (no hand annotation): 'thou' is unambiguously NOMINATIVE -> it is the SUBJECT of its clause;
'thee' is ACCUSATIVE -> it is NOT a subject. So every 'thou' adjacent to a finite verb is that verb's subject.

Measures, per 'thou' instance adjacent to an EME/-est verb:
  POS-LAYER (adjacent component)  : does spaCy tag 'thou' as PRON? (the layer the cue cascade stands on)
  spacy_raw                       : does spaCy make 'thou' the nsubj of the verb? (the floor)
  cue_override_full + morph       : does the brain-faithful cascade (with the archaic-morphology lexicon) pick it?
CONTROL: 'thee' (accusative) must NOT be assigned as a subject by the cascade (a case cue that fired on any
2nd-person pronoun would be wrong -- the fix must respect the case distinction).

spaCy LOCAL only. Deterministic. ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_role_parse_accuracy_probe_v1 as A
import experiments.exp_role_cue_first_subject_v1 as F

ANCHOR = "role_shakespeare_eme_v1"
SHAKESPEARE = os.path.join(_REPO, "data", "corpora", "tinyshakespeare.txt")
EME_VERBS = F.ARCHAIC_VERB | {"art", "wast", "wert", "didst", "hadst", "shouldst", "wouldst", "couldst",
                              "mayst", "mightst", "lovest", "livest", "givest", "takest", "makest",
                              "speakest", "tellest", "callest", "hearest", "seest", "feelest"}


def _is_eme_verb(w):
    w = w.lower().strip(".,'\"!?;:()")
    return w in EME_VERBS or (w.endswith("est") and len(w) > 4 and w not in
                              ("best", "rest", "west", "east", "guest", "honest", "quest", "forest",
                               "request", "interest", "harvest", "nearest", "dearest", "priest", "modest"))


def extract_thou_items(max_lines=None):
    """Lines with 'thou'/'thee' adjacent (within 2 tokens) to an EME finite verb. Definitional gold."""
    thou_items, thee_items = [], []
    with open(SHAKESPEARE, encoding="utf-8") as f:
        for li, line in enumerate(f):
            if max_lines and li >= max_lines:
                break
            line = line.strip()
            toks = line.split()
            if len(toks) < 3 or len(toks) > 40:
                continue
            low = [t.lower().strip(".,'\"!?;:()") for t in toks]
            for i, w in enumerate(low):
                if w not in ("thou", "thee"):
                    continue
                # nearest EME verb within 2 tokens (adjacency => unambiguous clause)
                vj = None
                for j in (i - 1, i + 1, i - 2, i + 2):
                    if 0 <= j < len(toks) and _is_eme_verb(toks[j]):
                        vj = j
                        break
                if vj is None:
                    continue
                text = " ".join(toks)
                item = {"text": text, "subj_tok": i, "verb_tok": vj, "pron": w}
                (thou_items if w == "thou" else thee_items).append(item)
    return thou_items, thee_items


def _score(nlp, items, want_subject=True):
    """Returns dict of rates: pos_pron (spaCy tags the pronoun PRON), raw (spaCy nsubj), cascade (full+morph)."""
    pos_ok, raw_ok, casc_ok = [], [], []
    for it in items:
        text = it["text"]
        subj_span = A._tok_span(text, it["subj_tok"])
        verb_span = A._tok_span(text, it["verb_tok"])
        doc, toks, pos = F._spacy_toks_pos(nlp, text)
        gold_tok = F._tok_at_charspan(doc, subj_span)
        ptok = doc[gold_tok]
        pos_ok.append(int(ptok.pos_ == "PRON"))
        # raw: is the pronoun spaCy's nsubj of the verb
        raw_sp = F.R.repaired_subject_span(doc, verb_span, mode="raw")
        raw_ok.append(int(bool(raw_sp) and A._overlap(raw_sp, subj_span)))
        # cascade + morph lexicon
        use_pos = F._patch_morph(toks, pos)
        v = F._verb_idx(doc, verb_span, use_pos)
        pick = F.full_cue_subject(doc, toks, use_pos, v)
        picked_pron = int(pick is not None and pick == gold_tok)
        casc_ok.append(picked_pron if want_subject else (1 - picked_pron))  # thee: correct = NOT picked
    r = lambda a: round(float(np.mean(a)), 4) if a else 0.0
    return {"n": len(items), "spacy_pos_tags_PRON": r(pos_ok), "spacy_raw_subject": r(raw_ok),
            "cascade_morph": r(casc_ok)}


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR); os.makedirs(d, exist_ok=True); return d


def _atomic_write(m):
    d = _out_dir(); tmp = os.path.join(d, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(d, "metrics.json"))


def main(max_lines=None):
    nlp = A._load_spacy()
    t0 = time.perf_counter()
    thou_items, thee_items = extract_thou_items(max_lines=max_lines)
    thou = _score(nlp, thou_items, want_subject=True)
    thee = _score(nlp, thee_items, want_subject=False)   # accusative: cascade must NOT call it a subject
    metrics = {
        "verdict": "MEASURED", "anchor_name": ANCHOR,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "elapsed_s": round(time.perf_counter() - t0, 1),
        "register": "Early-Modern-English (tinyshakespeare); morphology density 2.31% vs LitBank 0.014% (165x)",
        "live_path": "Shakespeare is NOT on the live reading path (capability test, not a live-cost claim)",
        "thou_subject": thou,
        "thee_object_control": thee,
        "interpretation": ("thou_subject.spacy_pos_tags_PRON = the POS-LAYER degradation on EME (the layer the "
                           "cascade stands on). spacy_raw_subject = the floor; cascade_morph = the brain-faithful "
                           "fix with the stored archaic lexicon. thee control: the cascade must NOT assign the "
                           "ACCUSATIVE 'thee' as a subject (respecting the case distinction the brain uses)."),
    }
    _atomic_write(metrics)
    print(f"[EME thou-as-subject n={thou['n']}] spaCy POS=PRON {thou['spacy_pos_tags_PRON']} | "
          f"spaCy raw subject {thou['spacy_raw_subject']} -> cascade+morph {thou['cascade_morph']}")
    print(f"[EME thee-as-object control n={thee['n']}] cascade correctly does NOT make it subject: {thee['cascade_morph']}")
    print(f"-> {os.path.join(_out_dir(),'metrics.json')} ({metrics['elapsed_s']}s)")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        nlp = A._load_spacy()
        assert _is_eme_verb("knowest") and _is_eme_verb("art") and not _is_eme_verb("honest")
        ti, te = extract_thou_items(max_lines=2000)
        assert len(ti) > 0, "should find some 'thou'+EME-verb items in Shakespeare"
        print(f"[self-test] PASS ({len(ti)} thou items in first 2000 lines)"); sys.exit(0)
    try:
        main(max_lines=(3000 if args.mode == "smoke" else None))
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        _atomic_write({"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                       "traceback": traceback.format_exc()[:4000]})
        raise
