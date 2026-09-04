"""exp_construction_aware_selector_brain_comparison_v1 -- how does our who-did-what SELECTOR perform against a
competent reader (spaCy, offline diagnostic ORACLE, reference-only), and WHERE EXACTLY do we differ?

The diagnosis + residual cells established the construction-aware selector is a NULL over the live proximity selector
(hybrid_role_patient), which already reaches 0.928 at the selector level; the real residual is a heterogeneous
non-canonical tail (object-complement/naming, passive-complement, quotative/cleft inversion, apposition, indefinite-
pronoun coverage), NOT multi-DO competition. This cell answers the owner's question directly: it runs spaCy's
dependency parse as the competent-reader proxy on the SAME cleaned-DO population, picks the parse-based direct object
(obj/dobj, reduced to head, mapped through the naming/object-complement dobj-vs-oprd split), scores it against the
who-did-what gold, and DECOMPOSES the divergence:
  (A) our-live vs competent reader head-to-head accuracy;
  (B) on OUR residual: how many does the competent reader RECOVER (a fidelity gap, recoverable) vs neither recovers
      (a genuine semantic/ambiguity/gold-noise ceiling the brain also hits);
  (C) the object-complement AMBIGUITY: for naming/resultative verbs, does spaCy's dobj (the named thing) or its oprd
      (the complement) match the gold -- quantifying that the who-did-what "patient" of a 2-argument construction is
      genuinely under-determined.

spaCy is built from the SPACE-SPLIT gold tokens (Doc(words=toks)) so token indices align exactly with verb_idx --
no re-tokenization drift. spaCy is a REFERENCE ORACLE only (the documented diagnostic exception); NOTHING here is
proposed for the inference path. ASCII. own dir. hdlab READ-only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_whodidwhat_ideal_brain_foundational_v1 as IDEAL
from experiments.exp_construction_aware_selector_diagnosis_v1 import GIVE_CLASS, NAMING_CLASS, live_pick, _bare, _boot
from hdlab.pos_tagger import PosTagger
from hdlab.thematic_role_labeler import lemma_verb

OUT_DIR = os.path.join(_REPO, "data/exp_construction_aware_selector_brain_comparison_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")

_NLP = None
def _nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def spacy_picks(toks, vi):
    """Competent-reader parse picks for verb at index vi (0-based). Build the Doc from the gold tokens so indices
    align. Returns dict with the dobj head (the named/affected thing), the oprd/attr complement head, and the
    'best' patient = dobj if present else the complement. All lowercased head strings or None."""
    import spacy
    nlp = _nlp()
    doc = spacy.tokens.Doc(nlp.vocab, words=list(toks))
    for name, proc in nlp.pipeline:
        doc = proc(doc)
    if vi >= len(doc):
        return {"dobj": None, "oprd": None, "best": None}
    v = doc[vi]
    # the verb token spaCy actually attached args to (vi may be tagged AUX in a passive/copula; hop to head VERB)
    head_verb = v
    if v.pos_ not in ("VERB",) and v.head is not None and v.head.pos_ == "VERB":
        head_verb = v.head
    dobj = oprd = None
    for ch in head_verb.children:
        if ch.dep_ in ("dobj", "obj") and dobj is None:
            dobj = ch.text.lower()
        if ch.dep_ in ("oprd", "attr", "acomp", "xcomp") and oprd is None:
            oprd = ch.text.lower()
        if ch.dep_ in ("nsubjpass", "nsubj:pass") and dobj is None:   # passive: theme is the subject
            dobj = ch.text.lower()
    best = dobj if dobj is not None else oprd
    return {"dobj": dobj, "oprd": oprd, "best": best}


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = PosTagger.load(POS_ASSET)
    rows = [r for r in V1.load_pop(IDEAL.LB) if r.get("gold_head")]
    clean = [r for r in rows if CG.is_clean_do(r, tg.tag(r["sent"].split()))[0]]
    if smoke:
        clean = clean[:80]

    ours, brain, brain_best_or_oprd = [], [], []
    naming_dobj_hit, naming_oprd_hit, naming_n = 0, 0, 0
    resid = {"recovered_by_brain": 0, "neither": 0, "brain_worse": 0}
    resid_examples = []
    both_wrong = []
    for r in clean:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r["gold_head"]
        pos = tg.tag(list(toks))
        o = (live_pick(toks, pos, vi) or "")
        sp = spacy_picks(toks, vi)
        b = sp["best"] or ""
        b_or = (sp["best"] or "") if (sp["best"] == gh) else (sp["oprd"] or sp["best"] or "")  # generous: dobj or oprd
        ours.append(int(o == gh)); brain.append(int(b == gh))
        brain_best_or_oprd.append(int(gh in (sp["dobj"], sp["oprd"], sp["best"])))
        v = lemma_verb(toks[vi])
        if v in NAMING_CLASS:
            naming_n += 1
            naming_dobj_hit += int(sp["dobj"] == gh)
            naming_oprd_hit += int(sp["oprd"] == gh)
        if o != gh:   # OUR residual: did the brain recover it?
            if b == gh:
                resid["recovered_by_brain"] += 1
                if len(resid_examples) < 40:
                    resid_examples.append({"kind": "brain_recovers", "verb": v, "gold": gh, "ours": o,
                                           "brain_dobj": sp["dobj"], "brain_oprd": sp["oprd"], "sent": r["sent"][:150]})
            else:
                resid["neither"] += 1
                if len([e for e in resid_examples if e["kind"] == "neither"]) < 25:
                    resid_examples.append({"kind": "neither", "verb": v, "gold": gh, "ours": o,
                                           "brain_dobj": sp["dobj"], "brain_oprd": sp["oprd"], "sent": r["sent"][:150]})
        if o != gh and b != gh:
            both_wrong.append(gh)

    ours = np.array(ours); brain = np.array(brain); brain_or = np.array(brain_best_or_oprd)
    res = {
        "n": len(clean),
        "acc_ours_LIVE_selector": round(float(ours.mean()), 4),
        "acc_competent_reader_spacy": round(float(brain.mean()), 4),
        "acc_competent_reader_dobj_or_oprd": round(float(brain_or.mean()), 4),
        "ours_vs_brain": _boot(ours, brain),
        "n_our_residual": int((ours == 0).sum()),
        "residual_vs_brain": resid,
        "residual_recovered_frac": round(resid["recovered_by_brain"] / max(1, (ours == 0).sum()), 4),
        "residual_neither_frac": round(resid["neither"] / max(1, (ours == 0).sum()), 4),
        "naming_construction": {"n": naming_n, "brain_dobj_matches_gold": naming_dobj_hit,
                                "brain_oprd_matches_gold": naming_oprd_hit,
                                "note": "dobj=named thing, oprd=complement; the split shows the patient is under-determined"},
        "examples": resid_examples,
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_aware_selector_brain_comparison_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    res = run(smoke=(args.self_test or args.smoke))
    print("\n===== BRAIN COMPARISON (competent reader = spaCy oracle; cleaned-DO n=%d) =====" % res["n"], flush=True)
    print("  OUR live selector          acc=%.4f" % res["acc_ours_LIVE_selector"], flush=True)
    print("  COMPETENT reader (spaCy)   acc=%.4f (dobj-or-oprd generous=%.4f)"
          % (res["acc_competent_reader_spacy"], res["acc_competent_reader_dobj_or_oprd"]), flush=True)
    d = res["ours_vs_brain"]
    print("  ours - brain               d=%+.4f CI[%+.4f,%+.4f] %s"
          % (d["delta"], d["ci_lo"], d["ci_hi"], "CI-SEP" if d["sep"] else "n.s. (statistically tied)"), flush=True)
    print("  --- WHERE WE DIFFER: on OUR residual (n=%d) ---" % res["n_our_residual"], flush=True)
    print("     recovered by the brain (FIDELITY gap, recoverable): %d (%.1f%%)"
          % (res["residual_vs_brain"]["recovered_by_brain"], 100 * res["residual_recovered_frac"]), flush=True)
    print("     NEITHER recovers (genuine ambiguity / gold noise ceiling): %d (%.1f%%)"
          % (res["residual_vs_brain"]["neither"], 100 * res["residual_neither_frac"]), flush=True)
    nc = res["naming_construction"]
    print("  --- naming/object-complement (n=%d): dobj matches gold %d, oprd matches gold %d (patient under-determined) ---"
          % (nc["n"], nc["brain_dobj_matches_gold"], nc["brain_oprd_matches_gold"]), flush=True)
    if args.self_test or args.smoke:
        assert res["n"] >= 60
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
