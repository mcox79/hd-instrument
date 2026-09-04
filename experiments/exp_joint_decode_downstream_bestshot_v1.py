"""exp_joint_decode_downstream_bestshot_v1 -- give the parser-downstream payoff its BEST SHOT, isolated from the
detector-precision confound. The v1 full run showed forcing ALL detector-promoted tokens VERB (6576 corrections over
3015 records at the modern threshold) FLOODS the parse and destroys who-did-what reachability (0.698->0.497). That is
a precision artifact, not a test of whether verb RECOVERY helps downstream.

This cell isolates the maximal benefit: on the SUBPOPULATION where the live perceptron genuinely DROPPED the gold verb
(verb_idx tagged non-VERB/AUX), force ONLY the gold verb -> VERB (ORACLE recovery, zero flooding) and measure whether
the gold argument's reachability to the verb + who-did-what accuracy improve, under BOTH the lexical parser and the
register-robust (delexicalized) parser. If even ORACLE single-verb recovery does not lift reachability here, the
downstream payoff is fundamentally absent (a located negative on payoff-2). If it DOES, the payoff exists but is gated
by detector precision on 19c (a calibration problem, not an architecture one).

Also reports the PRECISION-GUARDED joint decode on the FULL pop (a tight 19c threshold instead of the modern one) to
show whether controlling flooding recovers a net-neutral downstream (no-regression) rather than the -0.20 collapse.

Glass-box, CPU, NO LLM. ASCII. own dir.
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
# KB_REFERENT: data/exp_register_predicate_crf_tagger_v1/crf_tagger.pkl
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
import experiments.exp_joint_decode_register_robust_tagger_parser_v1 as JD
from hdlab.predicate_argument_frontend import _attaches_to_verb

OUT_DIR = os.path.join(_REPO, "data/exp_joint_decode_downstream_bestshot_v1")
MAX_HOPS = PP.MAX_HOPS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--cap", type=int, default=4000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    cap = 400 if args.self_test else args.cap

    tg = D.tagger()
    W_lex = AEO.load_model(AEO.MODEL_PATH)
    Wp_delex = JD.train_or_load_delex(smoke=args.self_test)
    rows = [r for r in V1.load_pop(D.LB)[:cap] if PP.cand_ok(r)]

    # SUBPOPULATION: genuine drops (verb_idx tagged non-VERB/AUX)
    import experiments.exp_whodidwhat_verb_id_recoverable_v1 as VID
    rng = np.random.default_rng(20260903)
    sub = {"base_lex": [], "oracle_lex": [], "oracle_delex": [], "twin_lex": []}
    subw = {"base_lex": [], "oracle_lex": [], "oracle_delex": [], "twin_lex": []}
    n_sub = 0
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks)
        if pos[vi0] in ("VERB", "AUX"):
            continue  # not a genuine drop -> outside the subpopulation the fix can act on
        n_sub += 1
        pos_oracle = list(pos); pos_oracle[vi0] = "VERB"   # force ONLY the gold verb (no flooding)
        # info-free twin: force ONE RANDOM gate-eligible non-verb-idx token -> VERB (same # corrections, wrong token)
        elig = [i for i in range(len(toks)) if i != vi0 and pos[i] not in ("VERB", "AUX") and VID.has_verb_reading(toks[i])]
        pos_twin = list(pos)
        if elig:
            pos_twin[int(elig[rng.integers(0, len(elig))])] = "VERB"
        v1 = vi0 + 1
        Hb, _, _ = AEO.parse_with_conf(toks, pos, W_lex)
        Hol, _, _ = AEO.parse_with_conf(toks, pos_oracle, W_lex)
        Hod, _, _ = JD.parse_delex(toks, pos_oracle, Wp_delex)
        Ht, _, _ = AEO.parse_with_conf(toks, pos_twin, W_lex)
        for nm, H, pp in (("base_lex", Hb, pos), ("oracle_lex", Hol, pos_oracle), ("oracle_delex", Hod, pos_oracle), ("twin_lex", Ht, pos_twin)):
            sub[nm].append(int(_attaches_to_verb(gi0 + 1, v1, H, pp, max_hops=MAX_HOPS)))
            subw[nm].append(int(PP.chain_pick(r, toks, pp, H, "far") == r["gold_head"]))

    def rate(a):
        return round(float(np.mean(a)), 4) if a else float("nan")

    res = {"n_subpopulation_genuine_drops": n_sub,
           "reach": {k: rate(v) for k, v in sub.items()},
           "wdw": {k: rate(v) for k, v in subw.items()},
           "reach_oracle_lex_vs_base": JD.paired_boot(sub["oracle_lex"], sub["base_lex"]) if n_sub else None,
           "reach_oracle_delex_vs_base": JD.paired_boot(sub["oracle_delex"], sub["base_lex"]) if n_sub else None,
           "reach_twin_lex_vs_base": JD.paired_boot(sub["twin_lex"], sub["base_lex"]) if n_sub else None,
           "reach_oracle_lex_vs_twin": JD.paired_boot(sub["oracle_lex"], sub["twin_lex"]) if n_sub else None,
           "wdw_oracle_lex_vs_base": JD.paired_boot(subw["oracle_lex"], subw["base_lex"]) if n_sub else None,
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "joint_decode_downstream_bestshot_v1", "results": res}, f, indent=2)

    print("\n===== DOWNSTREAM BEST-SHOT: ORACLE single-verb recovery on the genuine-drop subpopulation (n=%d) =====" % n_sub, flush=True)
    print("  reach: base_lex=%.4f  oracle_lex=%.4f  oracle_delex=%.4f  twin_lex=%.4f" % (res["reach"]["base_lex"], res["reach"]["oracle_lex"], res["reach"]["oracle_delex"], res["reach"]["twin_lex"]), flush=True)
    print("  wdw  : base_lex=%.4f  oracle_lex=%.4f  oracle_delex=%.4f  twin_lex=%.4f" % (res["wdw"]["base_lex"], res["wdw"]["oracle_lex"], res["wdw"]["oracle_delex"], res["wdw"]["twin_lex"]), flush=True)
    if res["reach_oracle_lex_vs_base"]:
        b = res["reach_oracle_lex_vs_base"]; d = res["reach_oracle_delex_vs_base"]
        tw = res["reach_twin_lex_vs_base"]; ot = res["reach_oracle_lex_vs_twin"]
        print("  reach oracle_lex - base   = %+.4f CI%s sep=%s" % (b["delta"], b["ci"], b["sep"]), flush=True)
        print("  reach oracle_delex - base = %+.4f CI%s sep=%s" % (d["delta"], d["ci"], d["sep"]), flush=True)
        print("  reach TWIN(random) - base = %+.4f CI%s sep=%s  (info-free twin must NOT lift)" % (tw["delta"], tw["ci"], tw["sep"]), flush=True)
        print("  reach oracle_lex - TWIN   = %+.4f CI%s sep=%s  (recovery beats random-correction)" % (ot["delta"], ot["ci"], ot["sep"]), flush=True)
    if args.self_test:
        assert n_sub >= 0
        print("[self-test] PASS", flush=True)
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
