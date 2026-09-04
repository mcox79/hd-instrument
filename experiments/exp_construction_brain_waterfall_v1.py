"""exp_construction_brain_waterfall_v1 -- the MEASURED signal-loss waterfall, ours vs a competent reader, stage by
stage, for who-did-what over the referent-per-NP candidate set.

Answers precisely: (1) how does our performance compare to the brain (competent-reader proxy = spaCy, reference-only)?
(2) WHERE along the chain do we lose signal? (3) at each stage, does the brain lose there too (shared hard) or not
(a fidelity gap we could close)? Decomposes the multiplicative chain per clause:

  S0 ORACLE (gold reachable)            = 1.000
  S1 CANDIDATE PRESENT (source/introduction): is the gold patient in the candidate set?
       ours = referent-per-NP (+ indefinite-pronoun coverage);  brain = spaCy nominal tagging.
  S2 EVENT (verb-ID)                    = 1.000 here (the who-did-what task SUPPLIES the verb index; noted for deployment).
  S3 SELECT | present (role binding): given the gold IS a candidate, is it the pick?
       ours = deployed feature-competition (hybrid_role_patient);  brain = spaCy dependency dobj.
  END = S1 * S3.

Also reports the DEPLOYED end-to-end reality (coref source) so the dominant real-document loss (SOURCE) is visible,
and decomposes OUR S3 (selection) residual into parse-recoverable (the brain gets it) vs genuine (neither does).
Glass-box; spaCy is the REFERENCE-ONLY oracle (never on the inference path). ASCII. own dir. hdlab READ-only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_whodidwhat_ideal_brain_foundational_v1 as IDEAL
from experiments.exp_construction_ideal_composition_v1 import _refnp_plus_indef
from experiments.exp_construction_aware_selector_diagnosis_v1 import live_pick, _boot
from experiments.exp_construction_aware_selector_brain_comparison_v1 import spacy_picks, _nlp
from hdlab.pos_tagger import PosTagger

OUT_DIR = os.path.join(_REPO, "data/exp_construction_brain_waterfall_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")


def _spacy_gold_nominal(toks, gh):
    """Would the competent reader OPEN the gold head as a nominal argument? (spaCy tags it NOUN/PROPN/PRON.)"""
    import spacy
    nlp = _nlp()
    doc = spacy.tokens.Doc(nlp.vocab, words=list(toks))
    for _n, proc in nlp.pipeline:
        doc = proc(doc)
    for t in doc:
        if t.text.lower() == gh:
            return t.pos_ in ("NOUN", "PROPN", "PRON")
    return False


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = PosTagger.load(POS_ASSET)
    rows = [r for r in V1.load_pop(IDEAL.LB) if r.get("gold_head")]
    clean = [r for r in rows if CG.is_clean_do(r, tg.tag(r["sent"].split()))[0]]
    if smoke:
        clean = clean[:100]

    # per-clause booleans
    s1_ours, s1_brain, end_ours, end_brain = [], [], [], []
    ours_pick_when_present, brain_pick_when_present = [], []
    s3_resid_recoverable, s3_resid_genuine = 0, 0
    for r in clean:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r["gold_head"]
        pos = tg.tag(list(toks))
        cand_heads = {h for h, ix in _refnp_plus_indef(toks, pos, True)}
        in_ours = gh in cand_heads
        in_brain = _spacy_gold_nominal(toks, gh)
        o = (live_pick(toks, pos, vi) or "")            # deployed feature-competition (over rnp)
        sp = spacy_picks(toks, vi); b = sp["best"] or ""
        s1_ours.append(int(in_ours)); s1_brain.append(int(in_brain))
        end_ours.append(int(o == gh)); end_brain.append(int(b == gh))
        if in_ours:
            ours_pick_when_present.append(int(o == gh))
            if o != gh:                                 # S3 selection error (gold WAS a candidate)
                if b == gh:
                    s3_resid_recoverable += 1           # the brain's parse gets it -> a fidelity gap
                else:
                    s3_resid_genuine += 1               # neither -> genuine ambiguity / gold noise
        if in_brain:
            brain_pick_when_present.append(int(b == gh))

    def m(x):
        return round(float(np.mean(x)), 4) if len(x) else None
    S1o, S1b = m(s1_ours), m(s1_brain)
    S3o, S3b = m(ours_pick_when_present), m(brain_pick_when_present)
    res = {
        "n": len(clean),
        "waterfall_ours": {"S0_oracle": 1.0, "S1_candidate_present": S1o, "S2_event_verb_supplied": 1.0,
                           "S3_select_given_present": S3o, "END": m(end_ours),
                           "END_check_S1xS3": round(S1o * S3o, 4)},
        "waterfall_brain_competent": {"S0_oracle": 1.0, "S1_candidate_present": S1b, "S2_event": 1.0,
                                      "S3_select_given_present": S3b, "END": m(end_brain),
                                      "END_check_S1xS3": round(S1b * S3b, 4)},
        "per_stage_ours_minus_brain": {"S1_source": round(S1o - S1b, 4), "S3_selection": round(S3o - S3b, 4),
                                       "END": round(m(end_ours) - m(end_brain), 4)},
        "END_ours_vs_brain_boot": _boot(np.array(end_ours), np.array(end_brain)),
        "S3_selection_residual": {"parse_recoverable_brain_gets_it": s3_resid_recoverable,
                                  "genuine_neither": s3_resid_genuine,
                                  "recoverable_frac": round(s3_resid_recoverable / max(1, s3_resid_recoverable + s3_resid_genuine), 4)},
        "DEPLOYED_reality_note": {"deployed_coref_source_end_to_end_CLEAN_DO": 0.4698,
                                  "coref_S1_candidate_present": 0.8183, "rnp_S1_candidate_present": 0.9705,
                                  "source": "parent open_a_discourse_referent... measured; the deployed dominant loss is S1 SOURCE, not S3"},
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_brain_waterfall_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    res = run(smoke=(args.self_test or args.smoke))
    wo = res["waterfall_ours"]; wb = res["waterfall_brain_competent"]; dg = res["per_stage_ours_minus_brain"]
    print("\n===== SIGNAL-LOSS WATERFALL: OURS vs a COMPETENT READER (cleaned-DO n=%d, referent-per-NP source) =====" % res["n"], flush=True)
    print("  stage                         OURS     BRAIN    ours-brain", flush=True)
    print("  S0 oracle                     %.3f    %.3f" % (wo["S0_oracle"], wb["S0_oracle"]), flush=True)
    print("  S1 candidate present (SOURCE) %.3f    %.3f     %+.3f" % (wo["S1_candidate_present"], wb["S1_candidate_present"], dg["S1_source"]), flush=True)
    print("  S2 event (verb supplied)      %.3f    %.3f" % (wo["S2_event_verb_supplied"], wb["S2_event"]), flush=True)
    print("  S3 select | present (BIND)    %.3f    %.3f     %+.3f" % (wo["S3_select_given_present"], wb["S3_select_given_present"], dg["S3_selection"]), flush=True)
    print("  END (= S1 x S3)               %.3f    %.3f     %+.3f" % (wo["END"], wb["END"], dg["END"]), flush=True)
    d = res["END_ours_vs_brain_boot"]
    print("  END ours-brain: d=%+.4f CI[%+.4f,%+.4f] %s" % (d["delta"], d["ci_lo"], d["ci_hi"], "CI-SEP" if d["sep"] else "TIED (n.s.)"), flush=True)
    sr = res["S3_selection_residual"]
    print("  S3 selection residual: %d parse-recoverable (brain gets it) / %d genuine (neither) -> %.0f%% recoverable"
          % (sr["parse_recoverable_brain_gets_it"], sr["genuine_neither"], 100 * sr["recoverable_frac"]), flush=True)
    dn = res["DEPLOYED_reality_note"]
    print("  [DEPLOYED reality] coref-source END %.3f (S1 coverage coref %.3f vs rnp %.3f) -- the deployed dominant loss is the SOURCE"
          % (dn["deployed_coref_source_end_to_end_CLEAN_DO"], dn["coref_S1_candidate_present"], dn["rnp_S1_candidate_present"]), flush=True)
    if args.self_test or args.smoke:
        assert res["n"] >= 80
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
