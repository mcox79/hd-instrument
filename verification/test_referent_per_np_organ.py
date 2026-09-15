"""Scaffold-free witness for open_a_discourse_referent_for_every_np_not_just_coref_mentions.

Drives the experiment cells' run() in memory (writes only to their OWN data dirs) and asserts every headline
from source. NO external LLM. Glass-box. Deterministic.

  W1  CAN-FAIL COVERAGE GAP: the gold PATIENT is a candidate under the deployed coref-column source only ~0.82,
      vs ~0.97 under referent-per-NP (the parent's prototype; the lever this problem lands end-to-end).
  W2  END-TO-END (LIVE reader): on the honest CLEAN-DO instrument, referent-per-NP raises effective end-to-end
      who-did-what (abstain=wrong) CI-separated over the coref-column floor.
  W3  INFO-FREE TWIN LOSES: referent-per-NP beats the matched-count random-position-filler twin CI-separated,
      AND the twin ACTIVELY HURTS vs coref (adding random candidates steals picks; adding the RIGHT referents nets +).
  W4  NO-REGRESSION: referent-per-NP reproduces the noun-supplied eval accuracy (the live `supplied` arm) -- the
      paired delta is ~0 (not a regression), on both regimes.
  W5  DESIGN: referent-per-NP as the SOLE source (coref demoted to a linking pass) BEATS the additive union (keep
      coref + add missed nouns) -- REPLACE, do not ADD (the brief's design, measured).
  W6  WHO-HAS-WHAT: referent-per-NP lifts OBJECT/theme candidate coverage (the inanimate "what" coref's entity-typing
      misses); introduction is capped by the 19c POS-tagger noun recall (named adjacent component).
  W7  GENERALIZATION: referent-per-NP INTRODUCTION coverage is register-INVARIANT (modern ~= 19c), where the coref
      linker is OOD on 19c -- the register-sensitivity lives in the linker, not introduction (DRT Q5).
Run: .venv/Scripts/python.exe verification/test_referent_per_np_organ.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_whodidwhat_referent_per_np_prototype_v1 as COV
import experiments.exp_referent_per_np_end_to_end_v1 as E2E
import experiments.exp_referent_per_np_holder_and_generalization_v1 as HG
import experiments.exp_referent_per_np_frame_detection_v1 as FR
import experiments.exp_referent_per_np_ideal_composition_v1 as ID
import experiments.exp_referent_per_np_selection_improvement_v1 as SEL

FAILS = []


def check(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + detail if detail else ""), flush=True)
    if not cond:
        FAILS.append(name)


def main():
    # 2026-09-15 (strategy, pri 125 landing): this harness installs its arms by monkeypatching
    # situation_reader.parse_litbank_conll (the coref-column role source). Since pri 125 the live reader feeds ONE
    # discovered stream (referent_per_np_source with discover_pronouns) to every consumer, so the monkeypatch is
    # INERT: every arm reads identically (rnp - twin = +0.0000, rnp == union, measured 2026-09-15). The claims this
    # witness made (coverage lever, twin loses and hurts, REPLACE > ADD) are re-established on modern text by pri
    # 125's cell (experiments/exp_pronoun_referent_discovery_v1.py --self-test / --repro: the position twin loses
    # CI-sep and costs patients; the A/B switch reproduces the pre-patch organ). This witness therefore EXITS 3 =
    # SUPERSEDED, loudly, instead of passing vacuously or failing as if the organ regressed.
    import inspect as _insp
    from hdlab.situation_reader import SituationReader as _SR
    if "discover_pronouns" in _insp.signature(_SR.__init__).parameters:
        print("[witness] SUPERSEDED (exit 3): the one-stream reader (pri 125) makes this harness's source-swap "
              "monkeypatch inert; run experiments/exp_pronoun_referent_discovery_v1.py --self-test instead")
        return 3
    # W1 -- the can-fail coverage gap (parent prototype; deterministic; ~7s). Recompute via the module's funcs.
    import glob
    from hdlab.pos_tagger import PosTagger
    from hdlab.coref import parse_litbank_conll
    from hdlab.scene_segment import parse_conll_sentences
    tg = PosTagger.load(COV.POS_ASSET)
    docs = sorted(glob.glob(os.path.join(COV.CORPUS, "*.conll")))
    coref_by, rnp_by = {}, {}
    for d in docs:
        mentions, n_sents = parse_litbank_conll(d)
        sents = parse_conll_sentences(d)
        cor = [set() for _ in range(n_sents)]
        for m in mentions:
            if 0 <= m["sent_idx"] < n_sents:
                cor[m["sent_idx"]].add(str(m["head"]).lower())
        for si, toks in enumerate(sents):
            up = tg.tag(list(toks)); key = " ".join(t.lower() for t in toks)
            coref_by[key] = cor[si] if si < len(cor) else set()
            rnp_by[key] = set(toks[i].lower() for i in COV.referent_per_np_mentions(toks, up))
    rows = COV.V1.load_pop(COV.LB); matched = cc = rc = 0
    for r in rows:
        gh = r.get("gold_head")
        key = " ".join(t.lower() for t in r["sent"].split())
        if not gh or key not in coref_by:
            continue
        matched += 1
        cc += int(gh in coref_by[key]); rc += int(gh in rnp_by.get(key, set()))
    cov_coref, cov_rnp = cc / max(1, matched), rc / max(1, matched)
    check("W1 coverage gap: coref-column patient coverage << referent-per-NP",
          cov_coref < 0.86 and cov_rnp > 0.95 and (cov_rnp - cov_coref) > 0.12,
          "coref %.4f -> rnp %.4f (+%.4f) over %d clauses" % (cov_coref, cov_rnp, cov_rnp - cov_coref, matched))

    # W2-W5 -- end-to-end LIVE reader on a doc subset (keeps the witness ~minutes; full 25-doc headline in metrics.json).
    e = E2E.run(n_docs=12, n_boot=600)
    cd = e["CLEAN_DO"]
    check("W2 end-to-end CLEAN-DO: referent-per-NP beats coref-column floor CI-separated",
          cd["rnp_vs_coref"]["ci_separated"] and cd["rnp_vs_coref"]["delta"] > 0.15,
          "coref %.4f -> rnp %.4f  d=%+.4f CI[%+.4f,%+.4f]" %
          (cd["effective_end_to_end"]["coref"], cd["effective_end_to_end"]["rnp"],
           cd["rnp_vs_coref"]["delta"], cd["rnp_vs_coref"]["ci_lo"], cd["rnp_vs_coref"]["ci_hi"]))
    check("W3 info-free twin LOSES (rnp>twin CI-sep) AND twin actively HURTS vs coref",
          cd["rnp_vs_twin"]["ci_separated"] and cd["twin_vs_coref"]["delta"] < 0,
          "rnp-twin d=%+.4f CI-sep; twin-coref d=%+.4f (twin hurts)" %
          (cd["rnp_vs_twin"]["delta"], cd["twin_vs_coref"]["delta"]))
    # no-regression on BOTH regimes: |rnp - supplied(live)| small (paired delta ~ 0, not a regression)
    nr_full = e["FULL"]["rnp_vs_supplied_noregress"]["delta"]
    nr_clean = cd["rnp_vs_supplied_noregress"]["delta"]
    check("W4 no-regression: referent-per-NP reproduces the noun-supplied eval accuracy (rnp ~= supplied)",
          nr_full >= -0.02 and nr_clean >= -0.05,
          "FULL rnp-supplied d=%+.4f ; CLEAN_DO d=%+.4f (both >= ~0)" % (nr_full, nr_clean))
    check("W5 design: referent-per-NP as SOLE source beats the additive union (REPLACE, not ADD)",
          cd["effective_end_to_end"]["rnp"] > cd["effective_end_to_end"]["rnp_union"],
          "rnp %.4f vs union %.4f" % (cd["effective_end_to_end"]["rnp"], cd["effective_end_to_end"]["rnp_union"]))

    # W6-W7 -- who-has-what coverage + generalization (fast).
    hg = HG.run()
    A = hg["who_has_what_holder_coverage"]; obj = A["OBJECT"]; pr = A["_pos_tagger_19c_noun_recall"]
    check("W6 who-has-what: referent-per-NP lifts OBJECT/theme coverage; capped by 19c POS noun recall",
          obj["recovery"] > 0.05 and 0.85 < pr["recall"] < 0.98,
          "OBJECT coref %.4f -> rnp %.4f (+%.4f); 19c POS noun recall %.4f" %
          (obj["coref"], obj["rnp"], obj["recovery"], pr["recall"]))
    B = hg["generalization_intro_coverage"]
    mod, lit = B["modern_qasrl"]["intro_coverage_patient"], B["litbank_19c"]["intro_coverage_patient"]
    check("W7 generalization: referent-per-NP INTRODUCTION coverage is register-invariant (modern ~= 19c)",
          mod > 0.95 and lit > 0.95 and abs(mod - lit) < 0.05,
          "modern %.4f ~= 19c %.4f (coref linker OOD on 19c = %.4f)" % (mod, lit, cov_coref))

    # W8 -- brain-faithful NP-FRAME detection lifts introduction coverage over the static POS tag CI-sep, twin loses.
    fr = FR.run()
    check("W8 brain-faithful NP-frame detection lifts introduction over static POS (twin loses)",
          fr["frame_minus_pos"]["ci_sep"] and fr["frame_minus_twin"]["ci_sep"],
          "POS %.4f -> POS+frame %.4f (+%.4f CI-sep); frame-twin +%.4f CI-sep" %
          (fr["intro_coverage"]["pos_only"], fr["intro_coverage"]["pos_plus_frame"],
           fr["frame_minus_pos"]["delta"], fr["frame_minus_twin"]["delta"]))

    # W9 -- the IDEAL composition (referent-per-NP source + the parent's validated selector) beats the live source fix
    # CI-sep, reaches/exceeds a competent reader, and a shuffled-cue twin loses (subset for witness speed).
    idc = ID.run(n_docs=12)
    L = idc["ladder"]
    check("W9 IDEAL composition (S1 source + S3 selector) reaches >= competent reader; shuffled-CANDIDATE twin loses",
          L["ideal_rnp_source"] >= L["competent_reader_spacy"] - 0.02
          and idc["ideal_vs_twin_candidates"]["ci_lo"] > 0
          and L["ideal_rnp_source"] > L["live_rnp"],
          "ideal %.3f (live-rnp %.3f, competent %.3f); cand-twin %.3f (ideal-twin d=%+.3f CI-sep)" %
          (L["ideal_rnp_source"], L["live_rnp"], L["competent_reader_spacy"],
           L["twin_shuffled_candidates"], idc["ideal_vs_twin_candidates"]["delta"]))

    # W10 -- the SELECTION improvement (Goldberg construction-aware multi-DO selector) beats the ideal pick CI-sep,
    # concentrated on the multi-DO competition subset; the distributional-fit twin loses (fit is real but subsumed).
    sel = SEL.run(n_docs=25)
    ac = sel["acc"]
    check("W10 construction-aware selection beats ideal CI-sep (concentrated on multi-DO); SP-twin loses",
          sel["construction_vs_baseline"]["ci_lo"] > 0 and sel["construction_vs_baseline_MULTI"]["ci_lo"] > 0
          and sel["constr_sp_vs_twin"]["ci_lo"] > 0,
          "ideal %.3f -> +construction %.3f (ALL +%.3f CI-sep; MULTI-DO +%.3f CI-sep); SP real-vs-twin +%.3f CI-sep" %
          (ac["ideal_baseline"], ac["plus_construction"], sel["construction_vs_baseline"]["delta"],
           sel["construction_vs_baseline_MULTI"]["delta"], sel["constr_sp_vs_twin"]["delta"]))

    print("\n==== REFERENT-PER-NP WITNESS: %d/10 ====" % (10 - len(FAILS)), flush=True)
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)


if __name__ == "__main__":
    import sys; sys.exit(main() or 0)
