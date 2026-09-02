"""exp_tagger_prototype_19c_v1 -- PROTOTYPE the fix to the WORST upstream brain-foundational component on 19c
(owner: "prototype the improvements to the downstream components to show that when done right they improve --
maybe just do the worst one first"). The 19c root cause was POS verb-ID (-0.10) + parser head-attach (-0.12),
both register gaps; the tagger is UPSTREAM of the parser, so the parser's attach loss is PARTLY caused by bad
POS. This feeds a BETTER tagger (spaCy en_core_web_sm UPOS = a strong-reference proxy for a gold-target-register
tagger; glass-box, NOT an LLM) into the SAME arc-eager parser + the SAME real role organ, and measures how much
of the 19c loss recovers -- disentangling the tagger's contribution from the parser's OWN register gap.

ARMS (per POS source: SUBSTRATE pos_tagger vs REFERENCE spaCy UPOS), on QA modern (reference) + 19c LitBank:
  S1  verb tagged VERB          (the tagger's own fidelity)
  S4  gold patient attaches to verb in the arc-eager parse  (parser, GIVEN this POS)
  WDW who-did-what through hybrid_role_patient (the real organ, GIVEN this POS)
Recovery = REFERENCE - SUBSTRATE. If the better tagger lifts S4/WDW on 19c, the tagger IS a live lever and the
fix ("read the register") is proven in prototype; the residual is the parser's OWN register gap. spaCy = diagnostic
reference only. CPU + spaCy POS (local). ASCII. own dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
from hdlab.graded_role_assigner import hybrid_role_patient

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_tagger_prototype_19c_v1")
NOMINAL = {"NOUN", "PROPN", "PRON"}


def cand_ok(r):
    return len(GD.cands(r)) >= 2 and sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2


def spacy_pos_map(all_tok_lists):
    """pretokenized UPOS via spaCy (reference tagger). returns list-of-pos aligned to each token list."""
    import spacy
    from spacy.tokens import Doc
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    out = []
    for toks in all_tok_lists:
        if not toks:
            out.append([]); continue
        doc = Doc(nlp.vocab, words=toks)
        for name, proc in nlp.pipeline:
            doc = proc(doc)
        out.append([t.pos_ for t in doc])
    return out


def analyze(name, path, W, tg, use_spacy_cache):
    rows = [r for r in V1.load_pop(path) if cand_ok(r)]
    # unique token lists (by sentence) for spaCy batching
    rows2 = []
    for r in rows:
        toks = r["sent"].split()
        gi0 = r.get("gold_idx"); vi0 = r["verb_idx"]
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        rows2.append((r, toks))
    print("[%s] %d items" % (name, len(rows2)), flush=True)
    # spaCy POS per sentence (cache by sent)
    sents = {}
    for r, toks in rows2:
        sents[r["sent"]] = toks
    skeys = list(sents.keys())
    spos = spacy_pos_map([sents[k] for k in skeys])
    sp_by_sent = {k: spos[i] for i, k in enumerate(skeys)}

    res = {}
    for src in ("substrate", "reference_spacy"):
        s1 = s4 = wdw = n = 0
        for r, toks in rows2:
            vi0 = r["verb_idx"]; gi0 = r["gold_idx"]
            pos = tg.tag(toks) if src == "substrate" else sp_by_sent[r["sent"]]
            if len(pos) != len(toks):
                continue
            n += 1
            heads, _, _ = AEO.parse_with_conf(toks, pos, W)
            s1 += int(pos[vi0] == "VERB")
            s4 += int(heads.get(gi0 + 1) == (vi0 + 1))
            v1 = vi0 + 1; cands = [c + 1 for c in r["cand_idx"]]
            try:
                oidx = hybrid_role_patient(toks, pos, v1, cands)
                pick = toks[oidx - 1] if (oidx and 1 <= oidx <= len(toks)) else r.get("pos_pick")
            except Exception:
                pick = r.get("pos_pick")
            wdw += int(pick == r["gold_head"])
        res[src] = {"S1_verb_tagged": round(s1 / n, 4), "S4_attach": round(s4 / n, 4),
                    "WDW_organ": round(wdw / n, 4), "n": n}
    rec = {k: round(res["reference_spacy"][k] - res["substrate"][k], 4) for k in ("S1_verb_tagged", "S4_attach", "WDW_organ")}
    res["recovery_ref_minus_sub"] = rec
    print("  SUBSTRATE tagger : S1=%.4f S4=%.4f WDW=%.4f" % (res["substrate"]["S1_verb_tagged"], res["substrate"]["S4_attach"], res["substrate"]["WDW_organ"]), flush=True)
    print("  REFERENCE tagger : S1=%.4f S4=%.4f WDW=%.4f" % (res["reference_spacy"]["S1_verb_tagged"], res["reference_spacy"]["S4_attach"], res["reference_spacy"]["WDW_organ"]), flush=True)
    print("  RECOVERY (ref-sub): S1=%+.4f S4=%+.4f WDW=%+.4f" % (rec["S1_verb_tagged"], rec["S4_attach"], rec["WDW_organ"]), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    out = {}
    for nm, path in (("qa_modern", V1.QA), ("litbank_19c", V1.LB)):
        print("\n=== %s ===" % nm, flush=True)
        out[nm] = analyze(nm, path, W, tg, None)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "tagger_prototype_19c_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
