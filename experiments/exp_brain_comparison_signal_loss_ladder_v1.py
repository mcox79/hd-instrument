"""exp_brain_comparison_signal_loss_ladder_v1 -- WHERE ALONG THE CHAIN we lose signal vs a competent reader, stage by
stage, on the SAME 19c who-did-what population, with the register (19c vs modern) gap isolated per stage.

The who-did-what chain: TOKENIZE -> TAG(verb present?) -> PARSE(attach args) -> REACH(gold arg reaches the verb?) ->
SELECT(pick the right arg = who-did-what). At each stage we report the RETAINED FRACTION for:
  OURS-perceptron   : the live perceptron tagger + arc-eager parser (the deployed floor)
  OURS-CRF-recovered: + the calibrated-posterior verb recovery (this problem's axis-1 win), precision-guarded (oracle
                      single-verb recovery on genuine drops -- the clean upper bound of what recovery buys the chain)
  BRAIN-proxy       : spaCy en_core_web_sm (a competent STATISTICAL reader; OFFLINE DIAGNOSTIC ONLY, never at inference
                      -- the parent's admissible exception). The nearest measurable stand-in for a competent reader.

spaCy is index-aligned to our whitespace tokens via Doc(words=toks) so verb_idx/gold_idx line up. This is a PROXY for
the brain, not the brain: a competent human also brings top-down world-knowledge a statistical reader lacks (that gap is
argued in SOLVED, not measured here). CPU. ASCII. own dir.
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_register_native_pp_attachment_v1 as PP
from hdlab.predicate_argument_frontend import _attaches_to_verb

OUT_DIR = os.path.join(_REPO, "data/exp_brain_comparison_signal_loss_ladder_v1")
MAX_HOPS = PP.MAX_HOPS


def spacy_heads_pos(doc):
    """spaCy Doc -> (heads {child_1idx: head_1idx (0=root)}, pos list) index-aligned to the input words."""
    heads = {}; pos = []
    for t in doc:
        pos.append(t.pos_)
        heads[t.i + 1] = 0 if t.head.i == t.i else (t.head.i + 1)
    return heads, pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--cap", type=int, default=4000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    cap = 300 if args.self_test else args.cap

    tg = D.tagger(); W_lex = AEO.load_model(AEO.MODEL_PATH)
    try:
        import spacy
        from spacy.tokens import Doc
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        print("[fatal] spaCy required for the brain-proxy ladder: %s" % e, flush=True); return

    rows = [r for r in V1.load_pop(D.LB)[:cap] if PP.cand_ok(r)]
    # accumulators: stage retained fractions
    S = {k: {"verb": [], "reach": [], "select": []} for k in ("ours_perc", "ours_crf", "brain")}
    # copula/predication split: is the gold predicate token a copula? (the UD-convention reach trap)
    COPSET = {"be", "is", "am", "are", "was", "were", "been", "being", "'s", "'re", "'m", "s", "re"}
    split = {"cop": {"ours": [], "brain": []}, "open": {"ours": [], "brain": []}}
    n = 0
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        n += 1
        v1 = vi0 + 1
        pos = tg.tag(toks)
        # --- OURS-perceptron ---
        verb_ok_p = int(pos[vi0] in ("VERB", "AUX"))
        Hp, _, _ = AEO.parse_with_conf(toks, pos, W_lex)
        reach_p = int(_attaches_to_verb(gi0 + 1, v1, Hp, pos, max_hops=MAX_HOPS))
        sel_p = int(PP.chain_pick(r, toks, pos, Hp, "far") == r["gold_head"])
        S["ours_perc"]["verb"].append(verb_ok_p); S["ours_perc"]["reach"].append(reach_p); S["ours_perc"]["select"].append(sel_p)
        # --- OURS-CRF-recovered (precision-guarded oracle single-verb recovery) ---
        pos_rec = list(pos)
        if pos[vi0] not in ("VERB", "AUX"):
            pos_rec[vi0] = "VERB"                       # the calibrated-posterior recovery restores the dropped verb
        verb_ok_c = 1                                    # by construction the verb is now present
        Hc, _, _ = AEO.parse_with_conf(toks, pos_rec, W_lex)
        reach_c = int(_attaches_to_verb(gi0 + 1, v1, Hc, pos_rec, max_hops=MAX_HOPS))
        sel_c = int(PP.chain_pick(r, toks, pos_rec, Hc, "far") == r["gold_head"])
        S["ours_crf"]["verb"].append(verb_ok_c); S["ours_crf"]["reach"].append(reach_c); S["ours_crf"]["select"].append(sel_c)
        # --- BRAIN-proxy (spaCy, index-aligned) ---
        doc = nlp(Doc(nlp.vocab, words=toks))
        sh, sp = spacy_heads_pos(doc)
        verb_ok_b = int(sp[vi0] in ("VERB", "AUX"))
        reach_b = int(_attaches_to_verb(gi0 + 1, v1, sh, sp, max_hops=MAX_HOPS))
        sel_b = int(PP.chain_pick(r, toks, sp, sh, "far") == r["gold_head"])
        S["brain"]["verb"].append(verb_ok_b); S["brain"]["reach"].append(reach_b); S["brain"]["select"].append(sel_b)
        # --- copula vs open-verb split on REACH (attribute the ours-vs-brain gap) ---
        is_cop = (toks[vi0].lower() in COPSET) or (pos[vi0] == "AUX") or (sp[vi0] == "AUX")
        grp = "cop" if is_cop else "open"
        split[grp]["ours"].append(reach_p); split[grp]["brain"].append(reach_b)

    def rate(a):
        return round(float(np.mean(a)), 4) if a else float("nan")

    def cond(num_key, cond_key, arm):
        """rate of num_key among records where cond_key==1 (conditional retention at that stage)."""
        v = np.array(S[arm][cond_key]); u = np.array(S[arm][num_key])
        m = v == 1
        return round(float(u[m].mean()), 4) if m.any() else float("nan")

    res = {"n_records": n}
    for arm in ("ours_perc", "ours_crf", "brain"):
        res[arm] = {st: rate(S[arm][st]) for st in ("verb", "reach", "select")}
        res[arm]["reach_given_verb"] = cond("reach", "verb", arm)
        res[arm]["select_given_reach"] = cond("select", "reach", arm)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "brain_comparison_signal_loss_ladder_v1", "results": res, "elapsed_s": round(time.time() - t0, 1)}, f, indent=2)

    print("\n===== SIGNAL-LOSS LADDER, 19c who-did-what (n=%d records) -- retained fraction per stage =====" % n, flush=True)
    print("  %-18s %8s %8s %8s | %10s %12s" % ("arm", "VERB", "REACH", "SELECT", "REACH|verb", "SELECT|reach"), flush=True)
    for arm, lab in (("ours_perc", "OURS-perceptron"), ("ours_crf", "OURS+CRF-recover"), ("brain", "BRAIN-proxy(spaCy)")):
        a = res[arm]
        print("  %-18s %8.4f %8.4f %8.4f | %10.4f %12.4f" % (lab, a["verb"], a["reach"], a["select"], a["reach_given_verb"], a["select_given_reach"]), flush=True)
    print("\n  VERB   = gold verb tagged VERB/AUX (detection)", flush=True)
    print("  REACH  = gold argument reaches the verb through the parse (structure)", flush=True)
    print("  SELECT = who-did-what pick == gold argument (end-to-end tuple)", flush=True)
    # attribute the reach gap: copula-predicate records vs open-verb records
    res["reach_split"] = {}
    print("\n  REACH gap attribution (copula-predicate vs open-verb records):", flush=True)
    for grp in ("cop", "open"):
        o = split[grp]["ours"]; b = split[grp]["brain"]
        res["reach_split"][grp] = {"n": len(o), "ours": rate(o), "brain": rate(b),
                                   "gap": round((np.mean(b) - np.mean(o)) if o else float("nan"), 4)}
        rs = res["reach_split"][grp]
        print("    %-5s n=%-5d ours=%.4f brain=%.4f  gap=%+.4f" % (grp, rs["n"], rs["ours"], rs["brain"], rs["gap"]), flush=True)
    if args.self_test:
        assert n > 0
        print("[self-test] PASS", flush=True)
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
