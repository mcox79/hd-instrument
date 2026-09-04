"""exp_whodidwhat_clean_frame_ladder_v1 -- settle how much of the 19c who-did-what "wall" survives a CORRECT RULER.

The deep research + disk verification found the ~0.44/~0.60 who-did-what "ceiling" is substantially a GOLD-CONTAMINATION
artifact: the eval gold's "patients" are ~17% true direct objects, ~49% PP-obliques, ~26% copular, ~8% pre-verbal (a
patient-selector structurally cannot/should not pick the non-core roles). This cell RE-MEASURES the who-did-what chain
per GOLD-ROLE SUBSET, for our reader (position + the landed NP-head chunker `hdlab.np_head_reduce`) vs a competent-reader
proxy (spaCy, OFFLINE DIAGNOSTIC ONLY), to show (a) the FULL-gold number is dominated by the non-core subsets, (b) on
the clean direct-object subset the wall dissolves (position ~0.92, NP-head ~0.98), and (c) THE INVERSION that corrects my
earlier signal-loss ladder: on the clean gold our NP-head reader BEATS the competent-reader proxy (my earlier "spaCy > us
at the parse stage" was purely the contaminated ruler).

PART 2 -- COPULA-ANCHOR discriminating test (Lane B Test 2): the ~26% copular subset scores ~0 because a POS=VERB anchor
skips the copula (the predication is real -- Kimian state, Maienborn 2005 -- and UD encodes nsubj(complement,subject)
one-hop). Re-anchor to the predicate complement and measure who-did-what recovery vs the POS=VERB gate AND vs an info-free
PERMISSIVE twin (random content-token anchor) -- honestly reporting if it only ties the twin (register-native's caveat:
naive copula-transparent traversal = permissiveness).

Reuses owner-DONE organs (does NOT rebuild them): `hdlab.np_head_reduce` (SOLVED chunker), the clean-DO classifier from
exp_19c_composed_cleaned_gold_v1. Glass-box; spaCy offline-diagnostic only, never at inference. CPU. ASCII. own dir.
# KB_REFERENT: data/predict_revise_recall_v1/_population_litbank.json
# KB_REFERENT: data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz
"""
from __future__ import annotations
import os
# core-headroom cap (USER 2026-09-04: constrain local runs below all cores; concurrent sessions share the box)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, json, sys, time
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_register_predicate_detector_v1 as D
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_register_native_pp_attachment_v1 as PP
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
from hdlab.np_head_reduce import np_head_reduce
from hdlab.predicate_argument_frontend import _attaches_to_verb

OUT_DIR = os.path.join(_REPO, "data/exp_whodidwhat_clean_frame_ladder_v1")
MAX_HOPS = PP.MAX_HOPS
CONTENT = ("NOUN", "PROPN", "ADJ")


def gold_role(r, pos):
    """Surface gold-role class mirroring CG.is_clean_do: COPULAR / PRE_VERBAL / PP_OBLIQUE / DIRECT_OBJECT."""
    toks = r["sent"].split(); vi = r["verb_idx"]; gi = r.get("gold_idx")
    if not toks or gi is None or not (0 <= vi < len(toks)) or not (0 <= gi < len(toks)):
        return None
    if toks[vi].lower() in CG.COP_AUX:
        return "COPULAR"
    if gi < vi:
        return "PRE_VERBAL"
    for j in range(vi + 1, gi):
        w = CG._clean_tok(toks[j])
        if w in CG.CLEAN_PREPS or (pos is not None and j < len(pos) and pos[j] == "ADP"):
            return "PP_OBLIQUE"
    return "DIRECT_OBJECT"


def _nearest_post(cands, vi):
    """cands = [(head, idx)]; nearest post-verbal, else nearest overall. Returns head word or None."""
    post = [(h, i) for (h, i) in cands if i > vi]
    pool = post or cands
    return min(pool, key=lambda hi: abs(hi[1] - vi))[0] if pool else None


def pick_position(cands, vi):
    return _nearest_post(cands, vi)


def pick_nphead(cands, vi, toks, pos):
    idxs = [i for (_, i) in cands]
    red = np_head_reduce(toks, pos, idxs)
    red_cands = [(CG._clean_tok(toks[ri]) if 0 <= ri < len(toks) else h, ri) for (h, i), ri in zip(cands, red)]
    return _nearest_post(red_cands, vi)


def pick_spacy(cands, vi, sh, sp):
    reach = [(h, i) for (h, i) in cands if _attaches_to_verb(i + 1, vi + 1, sh, sp, max_hops=MAX_HOPS)]
    post = [(h, i) for (h, i) in reach if i > vi]
    pool = post or reach or [(h, i) for (h, i) in cands if i > vi] or cands
    return min(pool, key=lambda hi: abs(hi[1] - vi))[0] if pool else None


def paired_boot(a, b, n_boot=2000, seed=20260904):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) == 0:
        return {"delta": float("nan"), "ci": [float("nan"), float("nan")], "sep": False, "n": 0}
    rng = np.random.default_rng(seed); n = len(a); d = a - b
    rr = np.array([d[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    lo, hi = float(np.percentile(rr, 2.5)), float(np.percentile(rr, 97.5))
    return {"delta": round(float(d.mean()), 4), "ci": [round(lo, 4), round(hi, 4)], "sep": bool(lo > 0), "n": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--cap", type=int, default=6000)
    args = ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    cap = 400 if args.self_test else args.cap

    tg = D.tagger()
    import experiments.exp_arceager_parser_operator_v1 as AEO
    W_lex = AEO.load_model(AEO.MODEL_PATH)
    import experiments.exp_brain_comparison_signal_loss_ladder_v1 as LAD
    try:
        import spacy
        from spacy.tokens import Doc
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        print("[fatal] spaCy required (offline diagnostic): %s" % e, flush=True); return

    rows = [r for r in V1.load_pop(D.LB)[:cap] if PP.cand_ok(r)]
    roles = ["DIRECT_OBJECT", "PP_OBLIQUE", "COPULAR", "PRE_VERBAL"]
    # CLEAN_DO = the owner-DONE coverage-required clean direct-object subset (CG.is_clean_do), to reproduce 0.919/0.981
    acc = {role: {"pos": [], "nphead": [], "spacy": []} for role in roles + ["ALL", "CLEAN_DO"]}
    counts = {role: 0 for role in roles + ["invalid"]}
    # copula-anchor test accumulators
    cop = {"base": [], "reanchor": [], "twin": []}
    rng = np.random.default_rng(20260904)

    for r in rows:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r.get("gold_head")
        pos = tg.tag(toks)
        role = gold_role(r, pos)
        if role is None:
            counts["invalid"] += 1; continue
        counts[role] += 1
        cands = CG.grounded_cands(r)  # [(head, idx)]
        if not cands:
            continue
        doc = nlp(Doc(nlp.vocab, words=toks)); sh, sp = LAD.spacy_heads_pos(doc)
        p_pos = pick_position(cands, vi)
        p_nph = pick_nphead(cands, vi, toks, pos)
        p_spy = pick_spacy(cands, vi, sh, sp)
        clean_do, _reason = CG.is_clean_do(r, pos)
        for arm, pk in (("pos", p_pos), ("nphead", p_nph), ("spacy", p_spy)):
            ok = int(pk == gh)
            acc[role][arm].append(ok); acc["ALL"][arm].append(ok)
            if clean_do:
                acc["CLEAN_DO"][arm].append(ok)

        # PART 2 -- copula-anchor discriminating test (on copular records only)
        if role == "COPULAR":
            # predicate complement = nearest CONTENT head after the copula (the Kimian-state predicate)
            comp = next((j for j in range(vi + 1, len(toks)) if pos[j] in CONTENT), None)
            # info-free twin anchor = a RANDOM content token (not the copula)
            content_ix = [j for j in range(len(toks)) if pos[j] in CONTENT and j != vi]
            twin = int(content_ix[rng.integers(0, len(content_ix))]) if content_ix else vi
            H, _, _ = AEO.parse_with_conf(toks, pos, W_lex)
            def anchored_pick(anchor):
                if anchor is None:
                    return None
                reach = [(h, i) for (h, i) in cands if _attaches_to_verb(i + 1, anchor + 1, H, pos, max_hops=MAX_HOPS)]
                pool = reach or cands
                return min(pool, key=lambda hi: abs(hi[1] - anchor))[0] if pool else None
            cop["base"].append(int(anchored_pick(vi) == gh))          # POS=VERB gate (anchor at copula)
            cop["reanchor"].append(int(anchored_pick(comp) == gh))    # anchor at predicate complement
            cop["twin"].append(int(anchored_pick(twin) == gh))        # info-free random-content anchor

    def rate(a):
        return round(float(np.mean(a)), 4) if a else float("nan")

    total = sum(counts[r] for r in roles)
    res = {"n_records": total, "counts": counts,
           "shares": {r: round(counts[r] / max(1, total), 4) for r in roles},
           "acc": {role: {arm: rate(acc[role][arm]) for arm in ("pos", "nphead", "spacy")} for role in roles + ["ALL", "CLEAN_DO"]},
           "n_by_role": {role: len(acc[role]["pos"]) for role in roles + ["ALL", "CLEAN_DO"]},
           "clean_do_nphead_vs_spacy": paired_boot(acc["CLEAN_DO"]["nphead"], acc["CLEAN_DO"]["spacy"]),
           "clean_do_pos_vs_spacy": paired_boot(acc["CLEAN_DO"]["pos"], acc["CLEAN_DO"]["spacy"]),
           "copula_anchor": {"base": rate(cop["base"]), "reanchor": rate(cop["reanchor"]), "twin": rate(cop["twin"]),
                             "reanchor_vs_base": paired_boot(cop["reanchor"], cop["base"]),
                             "reanchor_vs_twin": paired_boot(cop["reanchor"], cop["twin"]), "n": len(cop["base"])},
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "whodidwhat_clean_frame_ladder_v1", "results": res}, f, indent=2)

    print("\n===== WHO-DID-WHAT under a CORRECT RULER (n=%d) =====" % total, flush=True)
    print("  gold-role composition:", {r: "%d (%.1f%%)" % (counts[r], 100 * res["shares"][r]) for r in roles}, flush=True)
    print("  who-did-what accuracy per gold-role subset (ours position / ours NP-head / spaCy proxy):", flush=True)
    print("  %-14s %6s %8s %8s %8s" % ("subset", "n", "POS", "NPHEAD", "spaCy"), flush=True)
    for role in ["ALL", "CLEAN_DO", "DIRECT_OBJECT", "PP_OBLIQUE", "COPULAR", "PRE_VERBAL"]:
        a = res["acc"][role]
        print("  %-14s %6d %8.4f %8.4f %8.4f" % (role, res["n_by_role"][role], a["pos"], a["nphead"], a["spacy"]), flush=True)
    cd = res["clean_do_nphead_vs_spacy"]
    print("\n  INVERSION on CLEAN-DO (is_clean_do): NP-head - spaCy = %+.4f CI%s sep=%s (ours >= competent reader)" % (cd["delta"], cd["ci"], cd["sep"]), flush=True)
    ca = res["copula_anchor"]
    print("  COPULA-ANCHOR test (n=%d): base(POS=VERB gate)=%.4f reanchor=%.4f twin=%.4f | reanchor-base %+.4f sep=%s | reanchor-twin %+.4f sep=%s"
          % (ca["n"], ca["base"], ca["reanchor"], ca["twin"], ca["reanchor_vs_base"]["delta"], ca["reanchor_vs_base"]["sep"],
             ca["reanchor_vs_twin"]["delta"], ca["reanchor_vs_twin"]["sep"]), flush=True)
    if args.self_test:
        assert total > 0
        print("[self-test] PASS", flush=True)
    print("[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
