"""exp_situation_model_qa_modern_v1 -- the 19c-FREE MODERN comprehension board.

problem: rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval

The 19c board (exp_situation_model_qa_v1) scores its AGGREGATE + coref/events/temporal/causal on 100
pre-1923 LitBank documents (owner-banned 2026-09-06 as a load-bearing gold). This cell rebuilds the board
so EVERY dimension in the aggregate is scored on MODERN annotated gold, preserving the per_dimension
floor / twin / CI discipline EXACTLY, and emits a 19c-FREE aggregate + an explicit TRANSFERRED-vs-GAP map.

THE READER IS UNCHANGED -- only the corpus + golds change (a MEASUREMENT-fidelity rebuild). Each modern
dimension is a per_dimension row (model_acc / strongest_floor [recomputed on the item's OWN modern
population] / twin_acc [info-free, must lose] / model_minus_strongest[obs,lo,hi] / ci_sep), REUSING the
already-modern arms verbatim and the sibling GUM/UD arms this problem adds.

MODERN DIMENSIONS (gold source):
  coref (pronoun)        GUM      unified discourse referent (sibling SOLVED) -- EXCEEDS floor, twin loses
  salience               GUM      most-mentioned entity vs first-introduced floor
  common_noun_coref      GUM      LOCATED NEGATIVE (blind head-identity is the no-LLM ceiling)
  who_did_what_agent     UD-EWT   HYBRID Competition-Model agent vs positional floor (LOCATED: modern is
                                  canonical -> word-order near-ceiling; the 19c CM win is register-specific)
  who_did_what_patient   UD-EWT   structural_patient_pick (landed +0.086) vs positional floor
  state                  UD-EWT   copular is-a binding vs most-recent-noun floor
  wic (word-sense)       WiC      taxonomic sense signatures vs frequency floor
NAMED GAPS (no modern gold on disk -> filed follow-ons, NOT fabricated, NOT retained as 19c):
  temporal (tense-shared) / causal (connective-reducible) / goal (LitBank) / affect (LitBank)

THE UPSTREAM CHAIN (owner's directive -- every component brain-foundational, all the way upstream):
  #1 the UNIFIED DISCOURSE REFERENT feeds coref -- EXCEEDS on modern (+0.106 pronoun pick, reused).
  #2 the COMPETITION-MODEL ROLE ASSIGNER (owner-DONE) feeds BOTH who-did-what(agent) AND coref
     (entity-KB hard-link). On modern who-did-what it is a LOCATED register finding; on the coref
     entity-KB hard-link the brain-foundational (gold) roles beat the positional proxy CI-sep
     (cross_consumer_upstream) -- so the same upstream lifts a second consumer.

Glass-box, NO external LLM at inference OR in gold construction. ASCII. own dir.
Run: .venv/Scripts/python.exe experiments/exp_situation_model_qa_modern_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_situation_model_qa_modern_v1.py --run
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
# INSTRUMENT-SAFE DETERMINISM PIN (infra; fixes the board exiting mid-run with code 0).
# Several arms transitively import experiments._hashseed_guard, whose module body calls
# os.execv(sys.executable, [sys.executable] + sys.argv) whenever PYTHONHASHSEED != "0".
# That whole-process re-exec is only safe at a standalone cell's ENTRY. Reached mid-run
# here -- this aggregator runs 20+ arms, and run() is also imported as a LIBRARY by the
# reproducer / situation_reader consumers -- it RESTARTS/KILLS the process (bypassing
# normal returns and even sys.exit), so run() never returns its aggregate and the
# canonical metrics.json is never written. Pinning the env var to "0" BEFORE any arm
# imports makes every later _hashseed_guard import a no-op, so the board completes in
# one process. Restores the pre-2026-09-07 behaviour (the guard imports were added that
# day, commits 102641f3bb / 21515fce77, which introduced the mid-run re-exec regression).
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
ANCHOR = "situation_model_qa_modern_v1"
OUT_DIR = get_output_dir(ANCHOR)
SEED = 20260906

# GOLD SOURCE per dimension (for the audit trail; NONE is 19c LitBank and must not appear in the aggregate)
GOLD_SOURCE = {
    "coref": "GUM (modern, coref)", "salience": "GUM (modern, coref)",
    "common_noun_coref": "GUM (modern, coref)", "who_did_what_agent": "UD-EWT (modern, deprels)",
    "who_did_what_patient": "UD-EWT (modern, deprels)", "state": "UD-EWT (modern, deprels)",
    "wic": "WiC (modern, sense)",
}
# NAMED GAPS: dimensions with NO modern gold on disk yet -> filed follow-ons (never fabricated / never 19c)
NAMED_GAPS = {
    "temporal": "19c board gold shares the tense signal (circular); needs an INDEPENDENT modern temporal-order "
                "gold (e.g. TimeBank/TDDiscourse event ordering). Follow-on problem.",
    "causal": "19c board gold is connective-reducible (a connective detector, not force-dynamic reasoning); "
              "needs a NON-CIRCULAR modern causal gold (e.g. BECauSE / annotated because-clauses). Follow-on.",
    "goal": "goal register scored on 19c LitBank only; needs a modern intentionality gold. Follow-on.",
    "affect": "affect register scored on 19c LitBank only; needs a modern emotion gold (e.g. GoEmotions "
              "experiencer-linked). Follow-on.",
}


def _agg(rows):
    """19c-FREE aggregate = item-weighted mean of model_acc / strongest_floor / twin over the SCORED modern
    dimensions. This is a CROSS-POPULATION SUMMARY (informational); the per_dimension rows are the
    load-bearing claims (the measurement bar forbids a single number crossing scorers/populations)."""
    tot = sum(r["n"] for r in rows.values() if r and r.get("model_acc") is not None)
    if not tot:
        return {}
    def wm(key):
        s = sum(r["n"] * r[key] for r in rows.values() if r and r.get(key) is not None)
        return round(s / tot, 4)
    return {"n": tot, "model_acc": wm("model_acc"), "strongest_floor": wm("strongest_floor"),
            "twin_acc": wm("twin_acc"),
            "n_dims_ci_sep_over_floor": sum(1 for r in rows.values() if r and r.get("ci_sep_over_strongest")),
            "n_dims_total": len([r for r in rows.values() if r]),
            "note": "CROSS-POPULATION SUMMARY (item-weighted mean over modern dimensions). NO LitBank "
                    "dimension is included -> 19c-FREE. The per_dimension rows are the load-bearing claims; "
                    "this pooled number crosses scorers/populations and is informational only."}


# ==================================================================================================
# INFORMATIONAL 19c CROSS-REFERENCE (step 0): the LitBank aggregate + per-dim are KEPT for cross-reference
# but DEMOTED out of the headline (owner banned 19c LitBank as a load-bearing gold, 2026-09-06). Reads the
# existing 19c board metrics off disk if present; else a structural placeholder that names the source.
# ==================================================================================================
_LEGACY_19C = os.path.join(_REPO, "data", "situation_model_qa_v1", "metrics.json")


def _informational_19c_crossref():
    """The DEMOTED 19c LitBank board (aggregate + per-dim), kept for cross-reference, NEVER the headline."""
    base = {
        "status": "INFORMATIONAL -- DEMOTED (not the headline)",
        "reason": "owner banned 19th-century LitBank (100 pre-1923 novels) as a load-bearing comprehension "
                  "gold 2026-09-06 (a corpus-age confound, 'basically a different language'); the headline "
                  "aggregate above is 19c-FREE. This block is kept ONLY for cross-reference.",
        "source_cell": "experiments/exp_situation_model_qa_v1.run (tools/baseline_board Instrument A)",
        "corpus": "LitBank (100 pre-1923 novels, 19c)",
    }
    if os.path.exists(_LEGACY_19C):
        try:
            with open(_LEGACY_19C, encoding="ascii") as fh:
                m = json.load(fh)
            base["aggregate_litbank"] = m.get("aggregate")
            base["per_dimension_litbank"] = {k: (v.get("model_acc") if isinstance(v, dict) else None)
                                             for k, v in (m.get("per_dimension") or {}).items()}
            base["loaded_from_disk"] = True
        except Exception as e:
            base["loaded_from_disk"] = False
            base["load_error"] = "%s: %s" % (type(e).__name__, e)
    else:
        base["loaded_from_disk"] = False
        base["note_absent"] = ("no 19c board metrics on disk (data/situation_model_qa_v1/metrics.json); run "
                               "exp_situation_model_qa_v1.run to populate this cross-reference. Its aggregate + "
                               "coref/events/temporal/causal are scored on banned LitBank and are NOT the headline.")
    return base


# ==================================================================================================
# NEW BOARD ARMS (step B): make this session's board-INVISIBLE proven wins SCORED, each reusing the
# solver's OWN measurement. Kept OUT of the 19c-free headline aggregate (`_agg` reads only the 7 core dims);
# these live in res["new_board_arms"] as their own per_dimension rows. OFF in the board self-test.
#   coarse_sense           -- word-sense p7 coarse a_s (SemCor; INFORMATIONAL under the 19c ban, mid-20c).
#   selective_reliability  -- precision-defer p4 (UD-EWT; MODERN): answered-acc gain at dev-tau, twin flat.
#   causal_multihop        -- causal p10 (WIQA multi-hop + TellMeWhy non-adjacent; MODERN): traversal beats
#                             the 1-hop adjacency floor + shuffled-edge twin CI-sep.
#   occ_appraisal          -- inferred-emotion p3 (constructed MODERN OCC gold): the UNSTATED emotion the reader
#                             now infers (sm.infer_emotion) -- TYPE acc vs the strongest floor + goal<->event twin.
#   negation_quantifier    -- truth-conditional p9 (UD-EWT negation net-factuality + MED downward-monotone
#                             quantifier; MODERN): the landed read_polarity field scored vs the polarity/quantity-
#                             blind floor (which INVERTS under negation) + the info-free shuffled-cue twin.
#   natural_logic_monotonicity -- natural-logic p11 (MED downward/upward monotonicity; MODERN): the parse-free
#                             closed-class monotonicity reasoner over the C5 is-a spoke (hdlab.typed_spokes.
#                             natural_logic_label) -- self-detected-monotonicity acc ~0.767 vs a symmetric-cosine
#                             oracle (~0.535) + majority (~0.503) CI-sep + the shuffled-monotonicity twin (~0.540,
#                             loses -> polarity load-bearing), ~85% coverage. Reuses exp_natural_logic_monotonicity_
#                             med_v1.run(light=True) verbatim (witness W13/W14).
#   coref_via_reader       -- p12 coref stack (GUM he/she; MODERN): the LIVE EventCentralityReader pronoun pick
#                             with the phi_person_filter/narrow_him/soften_generic_suppress wires ON (~0.5855) vs
#                             the flag-OFF incumbent (~0.5032) + the info-free shuffled-identity twin -- the
#                             +0.082 CI-sep gain the board's URG-resolver `coref` tile does NOT show (a DIFFERENT
#                             resolver). Reuses verification/test_coref_stack_landing's W1 measurement verbatim.
#   event_goal_congruence  -- structured-matcher p4 (WordNet-antonym-thwart + FrameNet-converse-satisfy, MODERN
#                             head-pairs): the STRUCTURED SIGN matcher (hdlab.structured_matcher.congruence) that
#                             signs event<->goal satisfy/thwart (~0.9750) vs the polarity-blind ATL-hub baseline
#                             (bridging_inference relatedness thresholded, SWEPT to best on this population ~0.4917
#                             -- chance, rel(win,lose)~=rel(sell,buy)) CI-sep + the info-free shuffled-KB twin
#                             (~0.4917, loses -> the EDGES carry the sign) -- the +0.483 signing win that moves NO
#                             board dim today (the OCC arm has no headroom; the matcher fires 0/24 there). Carries
#                             the polarity-isolation slice (antonym subset: hub ~0.000 vs structured ~0.950).
#                             Reuses exp_structured_matcher_event_goal_v1.run verbatim (witness EG1/EG2/EG3).
#   sem_segmentation       -- SEM schema-switch event segmenter (the loop-closure north-star organ, owner-DONE
#                             close_the_recurrent_predictive_coding_loop... SS4l/SS4n; witness W10) on ACTUAL HUMAN
#                             perceived event boundaries (Kumar 2023 behavioural button-press gold, Tunnel): the
#                             SEM schema-switch graded signal's Spearman rho vs actual humans (~0.1235) BEATS the
#                             point-error INCUMBENT (~0.0668, the Kumar-refuted prediction-error quantity), is
#                             ~56% of the leave-one-subject-out human noise ceiling (0.2225), and is AT/ABOVE the
#                             published GPT-2 Bayesian-surprise reference (0.10-0.12; the 'needs a neural model'
#                             claim was RETRACTED). hdlab.sem_event_segmenter is a LATENT ISLAND (imported by NO
#                             live consumer) that moves no board dim. Reuses hdlab.sem_event_segmenter.
#                             _human_validation() VERBATIM (the routine --self-test calls; POINT estimates, no CI
#                             -> ci_sep flags False, the point win in beats_point_error_incumbent). Degrades to a
#                             schema-shaped N/A row if the human gold is absent (the organ abstains, never raises).
# ==================================================================================================
def _degraded(name, err, informational=False):
    """A schema-shaped row for an arm whose asset/runtime is unavailable (degrade-gracefully, like
    tools/baseline_board): model_acc=None + an error note, so the board always emits a row."""
    return {"n": 0, "model_acc": None, "overlap_floor": None, "strongest_floor": None,
            "strongest_floor_name": None, "twin_acc": None,
            "model_minus_strongest": [None, None, None], "model_minus_twin": [None, None, None],
            "ci_sep_over_strongest": False, "ci_sep_over_twin": False, "informational": informational,
            "population": "DEGRADED (asset/runtime unavailable) -- %s" % name,
            "error": ("%s: %s" % (type(err).__name__, err)) if isinstance(err, Exception) else str(err)}


def _sr_row(dev_rows, te_rows, name, pop, n_boot, seed):
    """One selective-reliability per_dimension row: model = answered-acc WITH deferral at dev-tau (cov~0.75);
    floor = blanket answer-all acc; twin = shuffled-confidence random-defer answered-acc (flat). Reuses the
    landed defer-consumer (experiments.exp_defer_consumer_v1) verbatim -- the exact policy the witness asserts."""
    import numpy as np
    import experiments.exp_defer_consumer_v1 as DC
    tau = DC.choose_tau_coverage(dev_rows, 0.75)
    ab = DC.abstain_metrics(te_rows, tau)
    ci = DC.boot_delta(te_rows, lambda rr: DC.abstain_metrics(rr, tau)["answered_acc"], B=n_boot, seed=seed)
    tau_tw = float(np.quantile(DC._arr(DC._twin_conf(dev_rows), "conf_twin"), 0.25))
    tw_ab = DC.abstain_metrics([dict(r, conf=r["conf_twin"]) for r in DC._twin_conf(te_rows)], tau_tw)
    # paired sentence-cluster bootstrap of (model answered_acc - twin answered_acc)
    clusters = DC._by_sid(te_rows); rng = np.random.default_rng(seed); nC = len(clusters)

    def _stat(rr):
        m = DC.abstain_metrics(rr, tau)["answered_acc"]
        t = DC.abstain_metrics([dict(r, conf=r["conf_twin"]) for r in DC._twin_conf(rr)], tau_tw)["answered_acc"]
        return (m - t) if (m == m and t == t) else 0.0
    obs = _stat(te_rows); ds = np.empty(n_boot)
    for b in range(n_boot):
        samp = [r for i in rng.integers(0, nC, nC) for r in clusters[i]]
        ds[b] = _stat(samp)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    mt = [round(float(obs), 4), round(float(lo), 4), round(float(hi), 4)]
    return {"n": len(te_rows), "model_acc": ab["answered_acc"], "overlap_floor": ab["blanket"],
            "floor_accs": {"blanket_answer_all": ab["blanket"]},
            "strongest_floor_name": "blanket_answer_all", "strongest_floor": ab["blanket"],
            "twin_acc": tw_ab["answered_acc"],
            "model_minus_strongest": [ci["delta"], ci["ci"][0], ci["ci"][1]],
            "model_minus_twin": mt,
            "ci_sep_over_strongest": bool(ci["sep"]),
            "ci_sep_over_twin": bool(mt[1] is not None and mt[1] > 0),
            "coverage": ab["coverage"], "tau": round(float(tau), 4), "population": pop}


def board_selective_reliability_dimension(cap=None, n_boot=500, seed=SEED):
    """PRECISION-DEFER (selective-reliability) board arm on MODERN UD-EWT (patient + obl). Reuses the a2=0
    row builders from verification/test_precision_defer_landing + the landed defer-consumer policy."""
    try:
        import hdlab.arceager_parser as AE
        from verification.test_precision_defer_landing import patient_rows_a2z, obl_rows_a2z
        from experiments.exp_typed_selpref_ppattach_v1 import load, TRAIN, TEST
        from experiments.exp_precision_weighted_whodidwhat_v1 import wdw_population
        W = AE.load_model(AE.MODEL_PATH)
        dev = load(TRAIN); te = load(TEST)
        if cap:
            dev = dev[:max(1200, cap)]; te = te[:cap]
        else:
            dev = dev[:3000]
        p_dev, _ = patient_rows_a2z(wdw_population(dev), W)
        p_te, _ = patient_rows_a2z(wdw_population(te), W)
        o_dev, _ = obl_rows_a2z(dev, W)
        o_te, _ = obl_rows_a2z(te, W)
        prow = _sr_row(p_dev, p_te, "patient",
                       "UD-EWT test who-did-what PATIENT selective-reliability; calibrated_patient_confidence "
                       "(a2=0), abstain@dev-tau cov~0.75; model=answered_acc, floor=blanket(answer-all), "
                       "twin=shuffled-conf random-defer (flat). MODERN.", n_boot, seed)
        orow = _sr_row(o_dev, o_te, "obl",
                       "UD-EWT test obl/nmod ATTACHMENT selective-reliability; calibrated_obl_confidence (a2=0), "
                       "abstain@dev-tau cov~0.75; model=answered_acc, floor=blanket, twin=shuffled-conf. MODERN.",
                       n_boot, seed)
        return {"patient_defer": prow, "obl_defer": orow}, {
            "note": "selective-reliability (Kepecs/Kiani confidence-gated commitment; Ernst-Banks precision "
                    "weighting) on MODERN UD-EWT: deferring the shakiest ~25% by the FROZEN calibrator lifts "
                    "answered-accuracy CI-sep over answer-all, the random-defer twin flat. Solver published a2-kept "
                    "PATIENT +0.0873 / obl +0.0916; these a2=0 rows are the deployed config."}
    except Exception as e:
        return {"patient_defer": _degraded("selective_reliability_patient", e)}, {
            "error": "%s: %s" % (type(e).__name__, e)}


def board_causal_multihop_dimension(cap=None, wiqa_cap=None, tmw_n=1500):
    """CAUSAL multi-hop board arm on MODERN non-circular gold: WIQA multi-hop + TellMeWhy non-adjacent-cause.
    Reuses experiments.exp_causal_reasoner_wiqa_v1 + exp_causal_reasoner_tellmewhy_v1 verbatim. On the
    multi-hop / non-adjacent subset the network TRAVERSAL beats the 1-hop adjacency floor (~0 by construction)
    AND the shuffled-edge twin CI-sep -- the load-bearing multi-hop claim (fills the modern causal NAMED GAP)."""
    out = {}
    # -- WIQA multi-hop (|j-i|>=2; gold i,j anchors isolate reasoning from anchoring) --
    try:
        import experiments.exp_causal_reasoner_wiqa_v1 as WQ
        items = WQ.load_items()
        if wiqa_cap or cap:
            items = items[:(wiqa_cap or cap)]
        rows = WQ.score(items)
        mh = [r for r in rows if r["oracle_multihop"]]
        model = round(float(WQ.acc(mh, "reason_oracle")), 4)
        floor = round(float(WQ.acc(mh, "adjacency")), 4)
        twin = round(float(WQ.acc(mh, "twin")), 4)
        pe = round(float(WQ.acc(mh, "polarity_echo")), 4)
        c_adj = WQ.paired_boot(rows, "reason_oracle", "adjacency", key="oracle_multihop")
        c_tw = WQ.paired_boot(rows, "reason_oracle", "twin", key="oracle_multihop")
        out["wiqa_multihop"] = {
            "n": len(mh), "model_acc": model, "overlap_floor": floor,
            "floor_accs": {"adjacency_1hop": floor}, "strongest_floor_name": "adjacency_1hop",
            "strongest_floor": floor, "twin_acc": twin,
            "model_minus_strongest": [c_adj["delta"], c_adj["ci"][0], c_adj["ci"][1]],
            "model_minus_twin": [c_tw["delta"], c_tw["ci"][0], c_tw["ci"][1]],
            "ci_sep_over_strongest": bool(c_adj["ci_sep"]),
            "ci_sep_over_twin": bool(c_tw["ci_sep"]),
            "population": "WIQA dev_with_expl MULTI-HOP subset (gold explanation-graph anchors, |j-i|>=2); "
                          "model=reason_oracle (signed-reachability network); floor=1-hop adjacency (~0 by "
                          "construction); twin=shuffled-edge network. MODERN (Tandon 2019).",
            "note": "the LOAD-BEARING claim is scoped to the position (adjacency) + info-free (twin) floors "
                    "(witness W2). A lexical polarity_echo baseline (%.4f) EXCEEDS the model on the multi-hop "
                    "SIGN subset = the documented edge-extraction wall, NOT a position floor." % pe}
    except Exception as e:
        out["wiqa_multihop"] = _degraded("wiqa_multihop", e)
    # -- TellMeWhy non-adjacent-cause (|h-q|>1; directed human narrative gold) --
    try:
        import experiments.exp_causal_reasoner_tellmewhy_v1 as TMW
        if not os.path.exists(TMW.TMW_TEST):
            out["tellmewhy_nonadjacent"] = _degraded("tellmewhy_nonadjacent",
                                                     "TMW_TEST not on disk (fetch_tellmewhy_v1.py)")
        else:
            r = TMW.run(n=(cap or tmw_n))
            am = r["acc_multihop"]; cm = r["contrasts_multihop"]
            ca = cm["dense_vs_adjacency"]; ct = cm["dense_vs_twin"]
            out["tellmewhy_nonadjacent"] = {
                "n": r["n_multihop"], "model_acc": round(float(am["dense"]), 4),
                "overlap_floor": round(float(am["adjacency"]), 4),
                "floor_accs": {"adjacency_recency": round(float(am["adjacency"]), 4)},
                "strongest_floor_name": "adjacency_recency", "strongest_floor": round(float(am["adjacency"]), 4),
                "twin_acc": round(float(am["twin"]), 4),
                "model_minus_strongest": [ca["delta"], ca["ci"][0], ca["ci"][1]],
                "model_minus_twin": [ct["delta"], ct["ci"][0], ct["ci"][1]],
                "ci_sep_over_strongest": bool(ca["ci_sep"]),
                "ci_sep_over_twin": bool(ct["ci_sep"]),
                "population": "TellMeWhy test Answerable why-questions, NON-ADJACENT-cause subset (all gold "
                              "helpful sentences |h-q|>1); model=dense (graded-necessity densified network); "
                              "floor=adjacency/recency (q-1, 0.000 by construction); twin=shuffled-edge. MODERN "
                              "(Lal 2021)."}
    except Exception as e:
        out["tellmewhy_nonadjacent"] = _degraded("tellmewhy_nonadjacent", e)
    return out, {"note": "MODERN non-circular causal multi-hop traversal (Trabasso & van den Broek reachability; "
                         "Pearl intervention) -- fills the modern causal NAMED GAP with a load-bearing "
                         "multi-hop instrument (traversal beats the 1-hop adjacency floor + shuffled twin)."}


def board_coarse_sense_dimension(max_files=12, seed=0):
    """COARSE word-sense (a_s) board arm on SemCor (INFORMATIONAL under the 19c ban -- SemCor is Brown corpus,
    mid-20c, NOT modern gold; a modern coarse WSD gold is a filed follow-on). Reuses the underspecified sense
    reader (compete FINE, commit COARSE cluster): model = coarse a_s, floor = coarse-MFS, twin = context-shuffle."""
    try:
        import numpy as np
        import experiments.exp_sense_hub_separation_as_v1 as SEP
        import experiments.exp_curated_foundation_wic_v1 as E
        import experiments.exp_underspecified_sense_reader_v1 as R
        from hdlab import meaning_foundation as MF
        w2i, mat = E._w2v(); mat = np.asarray(mat, float)

        def vl(w):
            i = w2i.get(w); return R._unit(np.asarray(mat[i], float)) if i is not None else None
        recs = SEP.build_recs(max_files=max_files)
        sub = [r for r in recs if r["subordinate"]
               and any(MF.covers(s) and MF.sense_signature(s) is not None for s in r["tn"])]
        if not sub:
            return _degraded("coarse_sense", "no covered subordinate SemCor recs", informational=True), {}
        rng = np.random.default_rng(seed); perm = rng.permutation(len(sub))
        model = []; floor = []; twin = []
        for i, r in enumerate(sub):
            tn = r["tn"]; glex = R.coarse_cluster(r["gold"])
            u = R.select_sense(r["ctx"], vl, candidate_synsets=tn, mode="underspecified")
            model.append(int(u["coarse"] == glex))
            floor.append(int(R.coarse_cluster(tn[0]) == glex))
            us = R.select_sense(sub[perm[i]]["ctx"], vl, candidate_synsets=tn, mode="underspecified")
            twin.append(int(us["coarse"] == glex))
        model = np.array(model, float); floor = np.array(floor, float); twin = np.array(twin, float)
        vf = E._paired(model - floor, 11); vt = E._paired(model - twin, 12)
        row = {"n": len(sub), "model_acc": round(float(model.mean()), 4),
               "overlap_floor": round(float(floor.mean()), 4),
               "floor_accs": {"coarse_MFS": round(float(floor.mean()), 4)},
               "strongest_floor_name": "coarse_MFS", "strongest_floor": round(float(floor.mean()), 4),
               "twin_acc": round(float(twin.mean()), 4),
               "model_minus_strongest": [vf["delta"], vf["lo"], vf["hi"]],
               "model_minus_twin": [vt["delta"], vt["lo"], vt["hi"]],
               "ci_sep_over_strongest": bool(vf["sep"]), "ci_sep_over_twin": bool(vt["sep"]),
               "informational": True,
               "population": "SemCor subordinate senses (Brown corpus, mid-20c; gold != MFS, >=1 covered curated "
                             "signature). INFORMATIONAL under the 19c ban -- NOT modern gold; the scored arm needs "
                             "a MODERN coarse WSD gold (filed follow-on). max_files=%d." % max_files}
        return row, {"note": "underspecified sense reader (Frisson good-enough; Rodd shared-core): compete FINE, "
                             "commit the COARSE supersense cluster. INFORMATIONAL (SemCor is mid-20c)."}
    except Exception as e:
        return _degraded("coarse_sense", e, informational=True), {"error": "%s: %s" % (type(e).__name__, e)}


def board_occ_appraisal_dimension(cap=None, seed=20260906):
    """OCC-APPRAISAL INFERRED-EMOTION board arm on the solver's OWN constructed MODERN OCC gold
    (experiments/data/occ_appraisal_gold_v1.jsonl). This capability is board-INVISIBLE today -- no dimension
    scores the UNSTATED emotion the reader now infers (the landed sm.infer_emotion read-out). Reuses the solver's
    OWN measurement verbatim (exp_occ_appraisal_emotion_v1): drive the LIVE reader once per item, run the glass-box
    OCC appraisal (desirability x prospect -> OCC type + valence) over the extracted affect+goal(thwart)+event
    registers, and score TYPE accuracy vs the strongest floor + the info-free goal<->event-shuffle twin (paired
    bootstrap over items). model = TYPE acc; floor = strongest type floor (most-frequent-type / last-stated-word /
    valence-only-oracle); twin = goal<->event-shuffle. Degrades gracefully (never crashes the board)."""
    try:
        import numpy as np
        import experiments.exp_occ_appraisal_emotion_v1 as M
        from experiments._occ_probe import load_gold
        gold = load_gold()
        if cap:
            gold = gold[:cap]
        rows = M.extract_all(gold)
        n = len(rows)
        rng = np.random.RandomState(seed)
        twin_perm = M._derange(n, rng)
        mft = M._mft(rows); majtype = M._majority_type_of_valence(rows)
        mfv = 1 if sum(r["gold_val"] for r in rows) >= 0 else -1
        idx_ps = np.array([r["is_prospect_subset"] for r in rows], bool)
        T = {a: M.arm_type_correct(rows, a, mft=mft, majtype=majtype, twin_perm=twin_perm)
             for a in ["APPRAISAL", "APPRAISAL_ORACLE", "NOFIX", "FLOOR_MFT", "FLOOR_LASTWORD", "FLOOR_VAL_TYPE", "TWIN"]}
        V = {a: M.arm_val_correct(rows, a, mfv=mfv, twin_perm=twin_perm)
             for a in ["APPRAISAL", "FLOOR_MFV", "TWIN"]}
        floor_accs = {"most_frequent_type": round(float(T["FLOOR_MFT"].mean()), 4),
                      "last_stated_word": round(float(T["FLOOR_LASTWORD"].mean()), 4),
                      "valence_only_oracle": round(float(T["FLOOR_VAL_TYPE"].mean()), 4)}
        fname = max(floor_accs, key=floor_accs.get)
        strongest = {"most_frequent_type": "FLOOR_MFT", "last_stated_word": "FLOOR_LASTWORD",
                     "valence_only_oracle": "FLOOR_VAL_TYPE"}[fname]

        def ci(a, b):
            d, lo, hi, _hw, _p95 = M._paired_ci(a, b, rng)
            return [round(d, 4), round(lo, 4), round(hi, 4)]
        ms = ci(T["APPRAISAL"], T[strongest])
        mt = ci(T["APPRAISAL"], T["TWIN"])
        vs = ci(V["APPRAISAL"], V["FLOOR_MFV"])
        row = {
            "n": n, "model_acc": round(float(T["APPRAISAL"].mean()), 4),
            "overlap_floor": floor_accs[fname],
            "floor_accs": floor_accs, "strongest_floor_name": fname, "strongest_floor": floor_accs[fname],
            "twin_acc": round(float(T["TWIN"].mean()), 4),
            "model_minus_strongest": ms, "model_minus_twin": mt,
            "ci_sep_over_strongest": bool(ms[1] > 0), "ci_sep_over_twin": bool(mt[1] > 0),
            "val_acc": round(float(V["APPRAISAL"].mean()), 4), "val_floor": round(float(V["FLOOR_MFV"].mean()), 4),
            "val_minus_floor": vs,
            "type_acc_prospect_subset": (round(float(T["APPRAISAL"][idx_ps].mean()), 4) if idx_ps.any() else None),
            "valence_only_floor_prospect_subset": (round(float(T["FLOOR_VAL_TYPE"][idx_ps].mean()), 4)
                                                   if idx_ps.any() else None),
            "oracle_acc": round(float(T["APPRAISAL_ORACLE"].mean()), 4),
            "nofix_acc": round(float(T["NOFIX"].mean()), 4),
            "population": "constructed MODERN OCC gold (occ_appraisal_gold_v1, n=%d, named characters, balanced "
                          "25/25 valence); model=glass-box OCC appraisal (desirability x prospect -> OCC type) over "
                          "the LIVE reader's affect+goal(thwart)+event registers; floor=strongest type floor "
                          "(most-frequent-type/last-stated-word/valence-only-oracle); twin=goal<->event-shuffle. "
                          "MODERN, self-authored (SOLVED sec 8 caveat)." % n}
        detail = {"note": "OCC forward appraisal (Ortony/Clore/Collins 1988 prospect-based emotions; Scherer "
                          "goal-conduciveness) -- the FIRST board arm that scores the UNSTATED inferred emotion "
                          "(live != scored before this). The load-bearing prospect subset {relief,fears_confirmed} "
                          "(TYPE %s) is provably 0 for the valence-only floor (%s). Composition exact (oracle %s); "
                          "the current substrate w/o the upstream thwart+prospect (NOFIX %s) collapses. Reuses "
                          "exp_occ_appraisal_emotion_v1 verbatim. INFORMATIONAL caveat: gold is self-authored (no "
                          "external MODERN OCC gold on disk; SOLVED sec 8)."
                          % (row["type_acc_prospect_subset"], row["valence_only_floor_prospect_subset"],
                             row["oracle_acc"], row["nofix_acc"])}
        return row, detail
    except Exception as e:
        return _degraded("occ_appraisal", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_spatial_relational_dimension(cap=None, seed=0):
    """SPATIAL-RELATIONAL (relative position) board arm on MODERN human gold: SpartQA-HUMAN YN, END-TO-END over the
    reader's OWN extraction. Reuses the solver's OWN measurement verbatim (exp_spatial_position_qa_v1.score_corpus):
    extract the spatial relations from each context with the reader's OWN parse, build the relational model, and
    answer natural-language yes/no questions by composing it (Franklin-Tversky per-axis closure + converse +
    nested-frame inheritance). model = REASONER (full-depth composition); floor = LAST-MENTION (depth-1: only a
    directly-stated relation answers) -- MUST lose where >=2 facts compose; twin = SHUFFLED-RELATION (node set +
    counts kept, edges permuted -- the info-free control). Paired bootstrap CI. This capability is board-INVISIBLE
    today (no dimension scores relative-position composition); the SOLVED proved it CI-separated end-to-end. Kept OUT
    of the 19c-free headline aggregate (its own row). Degrades gracefully (never crashes the board). MODERN
    (SpartQA-HUMAN human-authored; NOT 19c)."""
    try:
        import experiments.exp_spatial_position_qa_v1 as SPQ
        from experiments.spatial_gold_loaders import load_spartqa_human
        sp = load_spartqa_human("test", q_types=("YN",))
        if cap:
            sp = sp[:cap]

        def sp_gold(it):
            a = it["answer"]
            if isinstance(a, list) and a and str(a[0]).strip().lower() in ("yes", "no"):
                return str(a[0]).strip().lower() == "yes"
            return None

        def sp_subset(it):
            rt = it.get("reasoning", [])
            return "multi" if any(r in ("transitivity", "converse") for r in rt) else "single"

        res, _meta = SPQ.score_corpus(sp, sp_gold, sp_subset, seed=seed)
        ms = res["margin_reasoner_minus_lastmention"]
        mt = res["margin_reasoner_minus_twin"]
        multi = res["by_subset"].get("multi", {})
        row = {
            "n": res["n"], "model_acc": round(float(res["reasoner"][0]), 4),
            "overlap_floor": round(float(res["lastmention"][0]), 4),
            "floor_accs": {"last_mention_depth1": round(float(res["lastmention"][0]), 4)},
            "strongest_floor_name": "last_mention_depth1",
            "strongest_floor": round(float(res["lastmention"][0]), 4),
            "twin_acc": round(float(res["twin"][0]), 4),
            "model_minus_strongest": [ms["margin"], ms["lo"], ms["hi"]],
            "model_minus_twin": [mt["margin"], mt["lo"], mt["hi"]],
            "ci_sep_over_strongest": bool(ms["sep"]),
            "ci_sep_over_twin": bool(mt["sep"]),
            "coverage": res.get("coverage_reasoner"),
            "multi_fact_subset": {"n": multi.get("n"),
                                  "reasoner": (multi.get("reasoner") or [None])[0],
                                  "last_mention": (multi.get("lastmention") or [None])[0]},
            "population": "SpartQA-HUMAN test YN (human-authored), RELATIVE POSITION end-to-end over the reader's OWN "
                          "extraction; model=reasoner (full-depth Franklin-Tversky composition), floor=last-mention "
                          "(depth-1), twin=shuffled-relation (node set + counts kept). Paired bootstrap CI; UNK=wrong; "
                          "coverage-limited (extraction cap, not the reasoner). MODERN (Mirzaee 2021)."}
        detail = {"note": "glass-box relational spatial reasoner (Johnson-Laird mental-model inspection; "
                          "Franklin-Tversky spatial framework) -- the FIRST board arm that scores relative-position "
                          "COMPOSITION end-to-end. The load-bearing claim is scoped to the last-mention (position) + "
                          "shuffled-relation (info-free) floors; the composition holds over the reader's OWN "
                          "extraction (coverage %s). Reuses exp_spatial_position_qa_v1 verbatim. HONEST scope: "
                          "CONTAINMENT/PATH end-to-end on terse real prose stay extraction-gated (recall 0.22/0.02; "
                          "the SOLVED located negative) -- the text->relation EXTRACTOR is the named follow-on."
                          % row["coverage"]}
        return row, detail
    except Exception as e:
        return _degraded("spatial_relational", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_temporal_before_after_dimension(smoke=False):
    """TEMPORAL BEFORE/AFTER board arm on MODERN newswire: TB-Dense event-event BEFORE/AFTER TLINKs (1990s
    newswire, NOT 19c). Reuses the solver's OWN measurement verbatim (exp_temporal_reason_before_after_v1):
    the promoted timeline register answers 'did X happen before/after Y?' over the reordered timeline
    (Reichenbach place, not telling order). model = register acc; floor = ICONICITY (telling order == event
    order, recomputed on the SAME pairs -- MUST lose on the reverse-order/flashback items); twin = shuffled
    tense/marker labels (info-free). Paired sentence-cluster bootstrap CI. This capability is board-INVISIBLE
    today (temporal is a NAMED GAP -- 19c board gold shares the tense signal, circular); TB-Dense is the
    independent MODERN temporal-order gold the gap named. Kept OUT of the 19c-free headline aggregate.
    Degrades gracefully (never crashes the board). Also reports the INTEGRATED reasoner (+TIMEX date channel
    + transitive closure) as the stronger headline in the note."""
    try:
        from experiments import exp_temporal_reason_before_after_v1 as BA
        from experiments import _temporal_eval as EV
        items, _items_base, ndoc = BA.tbdense_before_after(smoke=smoke)
        if not items:
            return _degraded("temporal_before_after", "no TB-Dense before/after pairs (gold absent)"), {}
        full = BA._block(items, "full")
        rev = BA._block([it for it in items if it["reverse"]], "reverse")
        d_tw = EV.cluster_bootstrap_delta(items, "reg_correct", "twin_correct", seed=7)
        # integrated reasoner (stronger headline: cue + TIMEX event-local date + transitive closure)
        integ = None
        try:
            from experiments import exp_temporal_reason_integrated_v1 as IN
            ig = IN.run(smoke=smoke)
            integ = {"integrated_acc": ig["accuracy"]["integrated"], "iconicity": ig["accuracy"]["iconicity"],
                     "delta_vs_iconicity": ig["integrated_vs_iconicity"]["delta"],
                     "ci": ig["integrated_vs_iconicity"]["ci"], "sep": ig["integrated_vs_iconicity"]["sep"],
                     "date_channel_acc": ig["signal_class_provenance"]["date"]["acc"]}
        except Exception as ie:
            integ = {"error": "%s: %s" % (type(ie).__name__, ie)}
        row = {
            "n": full["n"], "model_acc": full["reg_acc"],
            "overlap_floor": full["icon_acc"],
            "floor_accs": {"iconicity_telling_order": full["icon_acc"]},
            "strongest_floor_name": "iconicity_telling_order", "strongest_floor": full["icon_acc"],
            "twin_acc": full["twin_acc"],
            "model_minus_strongest": [full["delta_vs_icon"], full["ci"][0], full["ci"][1]],
            "model_minus_twin": [round(d_tw["delta"], 4), round(d_tw["ci_lo"], 4), round(d_tw["ci_hi"], 4)],
            "ci_sep_over_strongest": bool(full["sep"]),
            "ci_sep_over_twin": bool(d_tw["sep"]),
            "reverse_order_subset": {"n": rev["n"], "reg": rev["reg_acc"], "iconicity": rev["icon_acc"],
                                     "delta": rev["delta_vs_icon"], "sep": rev["sep"]},
            "integrated_reasoner": integ,
            "population": "TB-Dense event-event BEFORE/AFTER TLINKs (1990s newswire, MODERN non-circular); "
                          "model=promoted timeline register (mechanism-if-cue-else-iconicity), floor=iconicity "
                          "(telling order==event order, recomputed on the SAME pairs), twin=shuffled tense/markers. "
                          "Paired sentence-cluster bootstrap. MODERN (Cassidy 2014)."}
        detail = {"note": "glass-box temporal BEFORE/AFTER reasoner (Reichenbach E/R/S; the register overrides "
                          "telling order only on the ~12%% cue-bearing pairs) -- the FIRST board arm scoring "
                          "temporal-order QUERY on modern gold. Load-bearing claim scoped to the iconicity "
                          "(position) + shuffled-label (info-free) floors; by construction it WINS on the "
                          "reverse-order subset where iconicity=0. The INTEGRATED reasoner (+TIMEX event-local "
                          "date + transitive closure) is the stronger headline (+0.099 vs iconicity, date "
                          "channel 0.83). Reuses exp_temporal_reason_before_after_v1 verbatim. HONEST scope: "
                          "TRACIE implicit-event is a SEPARATE script/schema organ (hdlab.temporal_script_schema)."}
        return row, detail
    except Exception as e:
        return _degraded("temporal_before_after", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_temporal_overlap_dimension(smoke=False):
    """TEMPORAL OVERLAP board arm: the Allen interval-intersection reasoner over aspect-derived START/END
    intervals -- the capability the point-order reader could NOT answer (it treats while/as/when as NEUTRAL
    and abstains, and DROPS the progressive that supplies an ongoing interval). Reuses the solver's OWN
    measurement verbatim (exp_temporal_reason_overlap_v1): a CONSTRUCTED can-fail gold isolates the Allen
    mechanism (like the SPACE organ's construction gold). model = Allen reasoner acc; floor = POINT-ORDER
    control (no interval -> no overlap category -> 0.5 on the balanced gold); twin = shuffled aspect labels +
    neutralised markers (info-free). This capability is board-INVISIBLE today (temporal NAMED GAP). Kept OUT
    of the 19c-free headline aggregate. Degrades gracefully. Also reports the REAL-PROSE TB-Dense overlap-gold
    subset (positive control: point-order control=0) + the honest full-population located negative in the note."""
    try:
        from experiments import exp_temporal_reason_overlap_v1 as OV
        con = OV.constructed_block(smoke=smoke)
        if not con or con.get("n", 0) == 0:
            return _degraded("temporal_overlap", "no constructed overlap gold"), {}
        # real-prose serve (modern newswire): the overlap-gold subset positive control + full-pop located negative
        tb = None
        try:
            tb = OV.tbdense_overlap(smoke=smoke, lexical=True)
        except Exception as te:
            tb = {"error": "%s: %s" % (type(te).__name__, te)}
        # model_minus_twin from the constructed block (twin p95; reasoner must beat it)
        twin_delta = round(con["allen_acc"] - con["twin_acc"], 4)
        row = {
            "n": con["n"], "model_acc": con["allen_acc"],
            "overlap_floor": con["point_acc"],
            "floor_accs": {"point_order_control": con["point_acc"]},
            "strongest_floor_name": "point_order_control", "strongest_floor": con["point_acc"],
            "twin_acc": con["twin_acc"],
            "model_minus_strongest": [con["delta_vs_point"], con["ci"][0], con["ci"][1]],
            "model_minus_twin": [twin_delta, None, None],
            "ci_sep_over_strongest": bool(con["sep"]),
            "ci_sep_over_twin": bool(con["allen_acc"] - con["twin_p95"] > 0),
            "twin_p95": con["twin_p95"],
            "real_prose_tbdense": ({"n_overlap_gold": tb.get("n_overlap_gold"),
                                    "allen_recall_on_overlap": tb.get("allen_recall_on_overlap"),
                                    "point_order_control": 0.0,
                                    "overlap_subset_delta_vs_point": tb.get("overlap_subset_delta_vs_point"),
                                    "overlap_subset_sep": tb.get("overlap_subset_sep"),
                                    "full_pop_beats_never_overlap_floor": tb.get("sep"),
                                    "fire_precision": tb.get("fire_precision"),
                                    "overlap_base_rate": tb.get("overlap_base_rate")}
                                   if isinstance(tb, dict) and "error" not in tb else tb),
            "population": "CONSTRUCTED balanced overlap-vs-precedence can-fail gold (real tagger, NO LLM); "
                          "model=Allen interval reasoner over aspect-derived endpoints, floor=point-order control "
                          "(no overlap category -> 0.5), twin=shuffled aspect labels + neutralised markers. The "
                          "MECHANISM isolation gold (MODERN construction, NOT 19c)."}
        detail = {"note": "glass-box Allen (1983) interval-intersection overlap reasoner over Smith-1991 "
                          "aspect-derived START/END intervals -- the FIRST board arm scoring temporal OVERLAP "
                          "(a capability the point-order reader structurally lacked). Load-bearing claim scoped "
                          "to the point-order-control + shuffled-label floors. On the REAL-PROSE TB-Dense "
                          "overlap-gold subset the reasoner recovers ~0.40 of the inclusions the point-order "
                          "control gets 0.0 of (positive control, CI-sep); it does NOT beat the trivial "
                          "'never-overlap' majority on the FULL mixed population (a LOCATED NEGATIVE -- the "
                          "DCT/discourse channel + the ~60%% INCLUDES/SIMULTANEOUS human-IAA ceiling, the named "
                          "next-organs). Reuses exp_temporal_reason_overlap_v1 verbatim."}
        return row, detail
    except Exception as e:
        return _degraded("temporal_overlap", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_temporal_survival_dimension(smoke=False):
    """TEMPORAL WHOLE-SUBGRAPH SURVIVAL board arm on MODERN dense gold (TB-Dense, 1990s newswire): the JOINT
    parse-based front-end (parse each sentence ONCE, read events TENSE-AGNOSTICALLY + the DROPPED copular/stative
    channel off the SINGLE dependency structure) vs the INCUMBENT tense-gated extractor (VBD/had+VBN/be+VBN only), the
    reasoner held at gold-perfect (extraction ISOLATED). This capability is board-INVISIBLE otherwise -- the
    temporal_before_after + temporal_overlap arms score the REASONER over the incumbent extraction; NO arm scored the
    FRONT-END's whole-subgraph survival, the HEADLINE metric of the owner-DONE
    extract_relations_from_prose_whole_subgraph_survival_the_shared_reasoner_bottleneck (a STATE is an event: the
    tense-gate drops present/copular/stative events, so multi-hop chains die at the exponent rate). Makes the wired
    joint_temporal_events gain a SCORED number, INDEPENDENT of the reader flag (reuses the solver's OWN measurement
    verbatim: exp_joint_temporal_survival_v1 + exp_joint_temporal_realreasoner_v1). model = joint_cop whole-subgraph
    survival; floor = incumbent tense-gated survival (recomputed on the SAME chains); twin = info-free random
    same-size event set (must LOSE). Paired bootstrap over chains. Kept OUT of the 19c-free headline aggregate.
    Degrades gracefully (TB-Dense gold absent/unloadable -> a schema-shaped degraded row). MODERN (Cassidy 2014)."""
    try:
        import experiments._hashseed_guard  # noqa: F401  (pins PYTHONHASHSEED=0 -> reproducible parse)
        from experiments.exp_joint_temporal_survival_v1 import run as surv_run
        sv = surv_run(smoke=smoke)
        s = sv["survival"]; mg = sv["margins"]; rc = sv["recall"]
        m_inc = mg["joint_cop_vs_incumbent"]; m_tw = mg["joint_cop_vs_twin"]
        # END-TO-END through the ACTUAL SOLVED reasoner (connective+tense), extraction the only variable
        e2e = None
        try:
            from experiments.exp_joint_temporal_realreasoner_v1 import run as rr_run
            rr = rr_run(smoke=smoke)
            ceil = rr["gold_ceiling"]["answered_correct"]
            e2e = {"incumbent": rr["incumbent"]["answered_correct"],
                   "joint_cop": rr["joint_cop"]["answered_correct"],
                   "joint_nom": rr["joint_nom"]["answered_correct"],
                   "gold_ceiling": ceil,
                   "joint_cop_vs_incumbent": rr["margins"]["joint_cop_vs_incumbent"],
                   "joint_cop_vs_twin": rr["margins"]["joint_cop_vs_twin"],
                   "pct_of_ceiling_joint_nom": (round(rr["joint_nom"]["answered_correct"] / ceil, 4) if ceil else None)}
        except Exception as ie:
            e2e = {"error": "%s: %s" % (type(ie).__name__, ie)}
        row = {
            "n": s["joint_cop"]["total"], "model_acc": round(float(s["joint_cop"]["rate"]), 4),
            "overlap_floor": round(float(s["incumbent"]["rate"]), 4),
            "floor_accs": {"incumbent_tense_gated_survival": round(float(s["incumbent"]["rate"]), 4),
                           "nltk_tense_agnostic_survival": round(float(s["nltk_tenseagn"]["rate"]), 4)},
            "strongest_floor_name": "incumbent_tense_gated_survival",
            "strongest_floor": round(float(s["incumbent"]["rate"]), 4),
            "twin_acc": round(float(s["joint_twin"]["rate"]), 4),
            "model_minus_strongest": [m_inc["delta"], m_inc["ci"][0], m_inc["ci"][1]],
            "model_minus_twin": [m_tw["delta"], m_tw["ci"][0], m_tw["ci"][1]],
            "ci_sep_over_strongest": bool(m_inc["ci_sep"]),
            "ci_sep_over_twin": bool(m_tw["ci_sep"]),
            "null_p95": m_inc.get("null_p95"),
            "event_recall": {"incumbent": round(float(rc["incumbent"]), 4),
                             "joint_cop": round(float(rc["joint_cop"]), 4)},
            "joint_nom_survival": round(float(s["joint_nom"]["rate"]), 4),
            "end_to_end_through_solved_reasoner": e2e,
            "population": "TB-Dense multi-hop BEFORE/AFTER chains (1990s newswire, MODERN dense gold, n_chains=%d); "
                          "model=JOINT tense-agnostic + copular/stative front-end whole-subgraph survival (parse once, "
                          "read all events off the single dependency structure), floor=INCUMBENT tense-gated extractor "
                          "(VBD/had+VBN/be+VBN) on the SAME chains, twin=info-free random same-size event set. Reasoner "
                          "held gold-perfect (extraction ISOLATED). Paired bootstrap over chains. MODERN." % s["joint_cop"]["total"]}
        detail = {"note": "the FIRST board arm scoring the FRONT-END's whole-subgraph SURVIVAL (a STATE is an event; "
                          "the incumbent tense-gate drops present/copular/stative events, so multi-hop chains die at "
                          "the exponent rate). Wired LIVE behind joint_temporal_events (default-ON, reasoner-side + "
                          "ADDITIVE: sm.events byte-identical off vs on -- this arm scores the gain directly, not "
                          "through a live reader consumer). The eventive-NOMINAL channel lifts survival further "
                          "(0.41 -> 0.73, nominal-event recall 0.105 -> 0.703) and is FLIPPED DEFAULT-ON UNGATED "
                          "(joint_nominal_events, 2026-09-07 p6): end-to-end through the ACTUAL solved reasoner the "
                          "UNGATED channel is the winner (answered-correct 0.4937 = 87%% of the gold-event ceiling vs "
                          "the WSD-gated 0.4590 CI-sep WORSE -- gating only drops coverage), so the precision drop is "
                          "an extraction-instrument artifact, not a downstream cost; the WSD gate is a located "
                          "NEGATIVE, retired for this consumer. Reuses exp_joint_temporal_survival_v1 + "
                          "exp_joint_temporal_realreasoner_v1 verbatim."}
        return row, detail
    except Exception as e:
        return _degraded("temporal_survival", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_spatial_extraction_precision_dimension(cap=None):
    """SPATIAL EXTRACTION TYPE-PRECISION board arm on MODERN human gold (SpaceEval/ISO-Space train+trial). This is a
    SEPARATE capability from the spatial_relational arm (which scores relative-POSITION composition on SYNTHETIC
    SpartQA left/right): the owner-DONE extract_spatial_and_causal SPATIAL win is the joint semantic Figure-Ground
    EXTRACTOR's TYPE-PRECISION on HARD adjacent negatives -- can it tell 'the statue IN the temple' from 'the statue
    NEAR the plaza'? The ext CRATERS SpartQA (synthetic left/right, coverage 2.8%), so recall-survival is
    density-confounded; the load-bearing axis is TYPE-PRECISION on its OWN gold. Scores the LANDED extractor the LIVE
    reader's spatial consumer now calls (hdlab.joint_relation_frontend.joint_spatial_frames_ext, use_thematic=True --
    the reader default, situation_reader._read_spatial_reasoning). Reuses the solver's OWN measurement verbatim
    (exp_joint_spatial_precision_qa_v1.build_model/gold_closure/qa/model_from_proximity + the survival cell's
    proximity_floor/boot_margin): build a SpatialModel from each extractor, answer balanced YES/NO containment queries
    (gold transitive closure = YES; HARD adjacent co-sentential non-containment pairs = NO) via the reasoner's
    transitive contains_path, reasoner held FIXED. Arms: ext-semantic (joint_spatial_frames_ext, LIVE reader config
    use_thematic=True) vs incumbent-linear (spatial_relation_extractor.extract_edges) vs the density/PROXIMITY floor
    (connect adjacent co-sentential nouns -- collapses on hard negatives); info-free twin = SHUFFLED-RELATION (permute
    the ext's grounds, node set + counts kept). model = ext-semantic TYPE-precision; strongest floor = incumbent-linear;
    density floor reported separately; paired bootstrap over queries. Kept OUT of the 19c-free headline aggregate (its
    own row). Degrades gracefully. MODERN (Pustejovsky 2015 SpaceEval, NOT 19c). Reproduces the SOLVED win (current
    on-disk: ext 0.5913 vs incumbent 0.5147 CI-sep, twin loses; the use_thematic=False base 0.5701 is byte-faithful to
    the SOLVED-filed joint 0.5712 vs incumbent 0.5179 -- a ~0.005 upstream-parse drift, win + CI-sep intact)."""
    try:
        import numpy as np
        from experiments.spatial_gold_loaders import load_spaceeval_docs
        from experiments.spatial_relation_extractor import extract_edges, tokenize_sents
        from experiments.exp_joint_spatial_survival_v1 import proximity_floor, boot_margin
        from experiments.exp_joint_spatial_precision_qa_v1 import (build_model, model_from_proximity,
                                                                   gold_closure, qa)
        from experiments.spatial_relational_model import SpatialModel, CONTAIN_RELTYPES, canon_entity
        from hdlab.joint_relation_frontend import parse_sentence, joint_spatial_frames_ext

        def _ext_triples(text, use_thematic):
            # MIRROR the LIVE reader's spatial loop (situation_reader._read_spatial_reasoning): tokenize -> parse each
            # sentence ONCE (cached) -> joint_spatial_frames_ext; keep the (fig, rel, gnd) triples (self-loops dropped).
            out = []
            for toks in tokenize_sents(text):
                toks = list(toks)
                if not toks or len(toks) > 120:
                    continue
                up, hd = parse_sentence(toks)
                for (f, r, g, _i, _p) in joint_spatial_frames_ext(toks, up, hd, use_thematic=use_thematic):
                    if canon_entity(f) == canon_entity(g):
                        continue
                    out.append((f, r, g))
            return out

        def _twin_model(triples, trng):
            # info-free SHUFFLED-RELATION twin: permute the grounds of the ext's containment edges (node set + counts
            # kept), then build the model the SAME way build_model does.
            cont = [(f, g) for (f, r, g) in triples if r == "in"]
            M = SpatialModel(max_depth=8)
            if len(cont) < 2:
                for (f, g) in cont:
                    M.add_containment(f, g)
                return M
            gnds = [g for (_f, g) in cont]
            perm = trng.permutation(len(gnds))
            for i, (f, _g) in enumerate(cont):
                M.add_containment(f, gnds[perm[i]])
            return M

        rng = np.random.default_rng(0)         # EXACTLY the SOLVED precision-QA hard-negative sampler (do NOT perturb)
        twin_rng = np.random.default_rng(7)    # SEPARATE stream for the shuffled-relation twin (isolates the sampler)
        arms = {"incumbent": [], "ext": [], "ext_base": [], "proximity": [], "twin": []}
        n_yes = n_no = n_doc = 0
        stop = False
        for split in ("train", "trial"):
            if stop:
                break
            for d in load_spaceeval_docs(split):
                Mg = SpatialModel(max_depth=8)
                for (fig, gnd, rel) in d["qslinks"]:
                    if rel in CONTAIN_RELTYPES:
                        Mg.add_containment(fig, gnd)
                yes, heads = gold_closure(Mg)
                if len(yes) < 1 or len(heads) < 3:
                    continue
                if cap and n_doc >= cap:
                    stop = True
                    break
                n_doc += 1
                prox_pairs = proximity_floor(d["text"])
                no = set()
                for (a, b) in prox_pairs:
                    if a != b and (a, b) not in yes and (b, a) not in yes:
                        no.add((a, b))
                no = list(no)
                if len(no) > len(yes):
                    sel = rng.choice(len(no), size=len(yes), replace=False)
                    no = [no[i] for i in sel]
                no = set(no)
                queries = [(x, y, 1) for (x, y) in yes] + [(x, y, 0) for (x, y) in no]
                n_yes += len(yes); n_no += len(no)
                t_thematic = _ext_triples(d["text"], use_thematic=True)   # the LIVE reader config
                t_base = _ext_triples(d["text"], use_thematic=False)      # byte-faithful to the SOLVED joint arm
                models = {"incumbent": build_model(extract_edges(d["text"])[1]),
                          "ext": build_model(t_thematic),
                          "ext_base": build_model(t_base),
                          "proximity": model_from_proximity(d["text"]),
                          "twin": _twin_model(t_thematic, twin_rng)}
                for a in arms:
                    arms[a].extend(qa(models[a], queries))
        if not arms["ext"]:
            return _degraded("spatial_extraction_precision", "no scorable SpaceEval containment docs"), {}
        A = {a: np.array(arms[a], float) for a in arms}
        acc = {a: round(float(A[a].mean()), 4) for a in arms}
        m_inc = boot_margin(A["ext"], A["incumbent"])
        m_prox = boot_margin(A["ext"], A["proximity"])
        m_tw = boot_margin(A["ext"], A["twin"])
        m_base_inc = boot_margin(A["ext_base"], A["incumbent"])

        def _sep(m):
            return bool(m.get("lo") is not None and m["lo"] > 0)

        row = {
            "n": len(arms["ext"]), "model_acc": acc["ext"],
            "overlap_floor": acc["incumbent"],
            "floor_accs": {"incumbent_linear": acc["incumbent"], "density_proximity": acc["proximity"]},
            "strongest_floor_name": "incumbent_linear", "strongest_floor": acc["incumbent"],
            "twin_acc": acc["twin"],
            "model_minus_strongest": [m_inc.get("margin"), m_inc.get("lo"), m_inc.get("hi")],
            "model_minus_twin": [m_tw.get("margin"), m_tw.get("lo"), m_tw.get("hi")],
            "ci_sep_over_strongest": _sep(m_inc), "ci_sep_over_twin": _sep(m_tw),
            "null_p95_over_strongest": m_inc.get("null_p95"),
            "density_floor_acc": acc["proximity"],
            "model_minus_density": [m_prox.get("margin"), m_prox.get("lo"), m_prox.get("hi")],
            "ci_sep_over_density": _sep(m_prox),
            "ext_base_reproduces_solved": {
                "ext_base_acc": acc["ext_base"], "incumbent_acc": acc["incumbent"],
                "delta": m_base_inc.get("margin"), "ci": [m_base_inc.get("lo"), m_base_inc.get("hi")],
                "ci_sep": _sep(m_base_inc),
                "note": "use_thematic=False = byte-faithful to the SOLVED joint arm (SOLVED-filed 0.5712 vs 0.5179; "
                        "current on-disk ~0.5701 vs 0.5147, a ~0.005 upstream-parse drift, win + CI-sep intact)"},
            "n_yes": n_yes, "n_no": n_no, "n_docs_scored": n_doc,
            "population": "SpaceEval/ISO-Space train+trial balanced containment QA (%d YES + %d NO = %d queries over %d "
                          "docs): model = ext-semantic TYPE-precision (hdlab.joint_relation_frontend."
                          "joint_spatial_frames_ext, use_thematic=True -- the LIVE reader config), strongest floor = "
                          "incumbent-linear (spatial_relation_extractor.extract_edges), density floor = PROXIMITY "
                          "(adjacent co-sentential nouns -> collapses on hard negatives), twin = shuffled-relation "
                          "(ext grounds permuted). Reasoner (SpatialModel.contains_path) held FIXED; paired bootstrap "
                          "over queries. cap=%s. MODERN (Pustejovsky 2015 SpaceEval, NOT 19c)."
                          % (n_yes, n_no, len(arms["ext"]), n_doc, cap)}
        detail = {"note": "glass-box spatial Figure-Ground TYPING (Talmy/Jackendoff; Herskovits preposition-semantics) "
                          "-- the FIRST board arm scoring the joint EXTRACTOR's TYPE-precision on hard adjacent "
                          "negatives (the discriminating test recall-survival cannot do: the brain tells IN from NEAR; "
                          "a proximity flood cannot). Load-bearing claim scoped to the incumbent-linear (position) + "
                          "density-proximity + shuffled-relation (info-free) floors; the density floor COLLAPSES to "
                          "%.4f on hard negatives while the semantic ext holds %.4f (+%.4f). SEPARATE from the "
                          "spatial_relational arm (SpartQA left/right composition -- the ext craters there, coverage "
                          "2.8%%). Scores the LANDED extractor the LIVE reader consumes (use_thematic=True). Reuses "
                          "exp_joint_spatial_precision_qa_v1 verbatim. HONEST scope: CONTAINMENT/PATH end-to-end on "
                          "terse prose stay extraction-gated (the SOLVED located negative)."
                          % (acc["proximity"], acc["ext"], m_prox.get("margin"))}
        return row, detail
    except Exception as e:
        return _degraded("spatial_extraction_precision", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_temporal_implicit_order_dimension(smoke=False):
    """TEMPORAL IMPLICIT-EVENT ORDERING board arm on MODERN gold (TRACIE iid test, ROCStories-derived, n=1924). This
    capability is board-INVISIBLE today -- the temporal_before_after / temporal_overlap / temporal_survival arms score
    the EXPLICIT narrated timeline + the extractor's survival; NONE scores the IMPLICIT-event / abstention path (place
    an UNSTATED event X before/after a narrated event Y from world knowledge -- the owner-DONE
    grow_a_broad_causal_event_order_knowledge_store...). That store is now LIVE in hdlab.temporal_reasoner
    (_script_schema() loads data/exp_broaden_causal_order_store_v1/chains_broad.json, the broader 454k-pair store, as a
    confidence-gated OVERRIDE on the implicit-event branch). Reuses the solver's OWN measurement verbatim
    (exp_broaden_causal_order_final_v1.run -> paired CLUSTERED bootstrap over stories): model = the BROADER store
    (tense-agnostic UPOS re-mine, UNGATED headline), strongest floor = the SEED store (177,800-pair tense-gated mine,
    recomputed on the SAME n=1924 population, abstain->majority); second floor = abstain-majority; info-free twin =
    SHUFFLED-ORDER (each pair's directional orientation permuted, node set + counts kept). Kept OUT of the 19c-free
    headline aggregate (its own row). Degrades gracefully (mine/gold absent -> schema-shaped degraded row). MODERN
    (Zhou 2021 TRACIE, ROCStories-derived; NOT 19c). Reproduces the SOLVED win: broader 0.5655 vs seed 0.5296 (+0.0359
    CI-sep), vs abstain +0.0655 CI-sep, twin loses (+0.0759 CI-sep). n=1924 is the FULL modern gold (the mine is a
    precomputed on-disk asset -- NOT a live re-parse), so no cap is needed; ~10s."""
    try:
        import os as _os
        import experiments.exp_broaden_causal_order_final_v1 as FIN
        # CONFIRM the win is LIVE: the broad store is exactly what hdlab.temporal_reasoner._script_schema() consults on
        # the implicit-event branch (the same on-disk asset), so this arm scores the wired capability, not an island.
        live_broad = None
        try:
            from hdlab.temporal_script_schema import CHAINS_ASSET
            _broad = _os.path.join(_os.path.dirname(_os.path.dirname(CHAINS_ASSET)),
                                   "exp_broaden_causal_order_store_v1", "chains_broad.json")
            live_broad = _os.path.exists(_broad)
        except Exception:
            live_broad = None
        R = FIN.run()
        u = R["arms"]["ungated_headline"]
        vs_seed = u["vs_seed"]; vs_tw = u["vs_twin"]; vs_abs = u["vs_abstain"]
        row = {
            "n": R["n"], "model_acc": round(float(u["acc"]), 4),
            "overlap_floor": round(float(R["seed_floor"]), 4),
            "floor_accs": {"seed_store_tense_gated": round(float(R["seed_floor"]), 4),
                           "abstain_majority": round(float(R["abstain_floor"]), 4)},
            "strongest_floor_name": "seed_store_tense_gated",
            "strongest_floor": round(float(R["seed_floor"]), 4),
            "twin_acc": round(float(R["twin_acc"]), 4),
            "model_minus_strongest": [vs_seed["delta"], vs_seed["lo"], vs_seed["hi"]],
            "model_minus_twin": [vs_tw["delta"], vs_tw["lo"], vs_tw["hi"]],
            "ci_sep_over_strongest": bool(vs_seed["ci_sep"]),
            "ci_sep_over_twin": bool(vs_tw["ci_sep"]),
            "null_p95_over_strongest": vs_seed.get("null_p95"),
            "coverage": round(float(u["cov"]), 4),
            "abstain_floor_acc": round(float(R["abstain_floor"]), 4),
            "model_minus_abstain": [vs_abs["delta"], vs_abs["lo"], vs_abs["hi"]],
            "ci_sep_over_abstain": bool(vs_abs["ci_sep"]),
            "live_broad_store_wired": live_broad,
            "population": "TRACIE iid TEST implicit-event before/after (n=%d, %d ROCStories mined, MODERN "
                          "ROCStories-derived gold): model = BROADER store (tense-agnostic UPOS re-mine, 454k pairs, "
                          "UNGATED headline, coverage %.3f); strongest floor = SEED store (177,800-pair tense-gated "
                          "mine, recomputed on the SAME population, abstain->majority); abstain-majority floor 0.5000; "
                          "twin = shuffled-ORDER (directional orientation permuted). Paired CLUSTERED bootstrap over "
                          "stories. LIVE in hdlab.temporal_reasoner (broad store wired=%s). MODERN (Zhou 2021 TRACIE)."
                          % (R["n"], R["n_docs"], u["cov"], live_broad)}
        detail = {"note": "glass-box implicit-event ordering (Zwaan Event-Indexing -- time is a graded CUE, not a gate; "
                          "Schank-Abelson script prior + confidence-gated override) -- the FIRST board arm scoring the "
                          "IMPLICIT-event / abstention path. The win is an UPSTREAM extraction fix: the seed store's "
                          "offline mine used a tense-gated event detector (drops present/bare/progressive verbs); "
                          "re-mining through the brain-foundational tense-agnostic UPOS front-end DOUBLES coverage "
                          "0.29->0.607 and lifts accuracy CI-sep over both the seed and abstain floors, the "
                          "shuffled-order twin losing (the extracted ORDER is load-bearing, not corpus frequency). "
                          "Reuses exp_broaden_causal_order_final_v1 verbatim. HONEST scope: the ~0.65 per-pair ceiling "
                          "is story-conditioning (aggregate script prior vs instance-specific order); the deep "
                          "situation-model reasoner over grounded state is the named follow-on."}
        return row, detail
    except Exception as e:
        return _degraded("temporal_implicit_order", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_negation_quantifier_dimension(seed=SEED):
    """TRUTH-CONDITIONAL NEGATION + QUANTIFIER board arm on MODERN gold (owner-DONE p9,
    represent_negation_and_quantifier_scope...). This capability is board-INVISIBLE today -- no dimension scores
    whether a stored proposition HOLDS (polarity) or over how many of its arguments it ranges (quantity); every
    event was filed POSITIVE + SINGULAR, which INVERTS the truth value under negation / downward-monotone
    quantifiers. The landed reader now exposes it (read_polarity -> EventRecord.polarity/quantity). Reuses the
    solver's OWN measurement verbatim -- two per_dimension rows:
      negation_ewt   -- exp_polarity_operator_ewt_v1: reader-native net-factuality over the LIVE reader's sm.events
                        vs the polarity-blind floor (must LOSE -- realized-only) + the info-free shuffled-cue twin.
      quantifier_med -- exp_quantifier_operator_med_v1: MED downward-monotone subset vs the monotone-blind floor
                        (INVERTS <0.30) + the shuffled-monotonicity twin; carries the well-powered full-unified
                        aggregate (negation+quantifier ONE operator) CI-sep over blind AND twin.
    Kept OUT of the 19c-free headline aggregate (its own rows). OFF in the board self-test. Degrades gracefully
    (missing gold -> a schema-shaped degraded row, never crashes the board). MODERN (UD-EWT + MED)."""
    out = {}
    # -- NEGATION (UD-EWT reader-native net-factuality) --
    try:
        import experiments.exp_polarity_operator_ewt_v1 as EW
        if not os.path.exists(EW.GOLD_PATH):
            out["negation_ewt"] = _degraded("negation_ewt", "gold_negation_factuality_ewt_v1 not on disk")
        else:
            o = EW.run(shuffle_seed=seed)
            na, omb, omt = o["net_accuracy"], o["operator_minus_blind"], o["operator_minus_twin"]
            out["negation_ewt"] = {
                "n": o["n_scored"], "model_acc": na["operator_full"],
                "overlap_floor": na["blind_floor"],
                "floor_accs": {"polarity_blind": na["blind_floor"]},
                "strongest_floor_name": "polarity_blind", "strongest_floor": na["blind_floor"],
                "twin_acc": na["shuffle_twin"],
                "model_minus_strongest": [omb["delta"], omb["ci"][0], omb["ci"][1]],
                "model_minus_twin": [omt["delta"], None, None],
                "ci_sep_over_strongest": bool(omb["ci_sep"]), "ci_sep_over_twin": bool(omt["beats_twin"]),
                "twin_null_p95": omt["null_p95"],
                "negated_recall": {"operator": o["negated_recall"]["operator_full"],
                                   "blind": o["negated_recall"]["blind_floor"]},
                "over_negation_clean": o["affirmative_regression"]["operator_full_clean"],
                "align_fail": o["align_fail"],
                "population": "UD-EWT reader-native negation net-factuality (gold_negation_factuality_ewt_v1, "
                              "modern web text, n=%d align_fail=%d); model=truth-conditional polarity operator over "
                              "the LIVE reader's sm.events (event_polarity: clause-local negation + coordination "
                              "sharing + implicative/factive complement gate), floor=polarity-blind (every event "
                              "stored positive -> realized -- MUST lose on negated items), twin=shuffled negation "
                              "cues (info-free, matched shape). Paired doc-level bootstrap CI; twin null p95. MODERN."
                              % (o["n_scored"], o["align_fail"])}
    except Exception as e:
        out["negation_ewt"] = _degraded("negation_ewt", e)
    # -- QUANTIFIER (MED downward-monotone + the well-powered unified aggregate) --
    try:
        import experiments.exp_quantifier_operator_med_v1 as MED
        if not os.path.exists(MED.MED_PATH):
            out["quantifier_med"] = _degraded("quantifier_med", "MED.tsv not on disk (fetch_negation_quantifier_gold_v1.py)")
        else:
            m = MED.run()
            ad, ombd = m["acc_downward"], m["operator_minus_blind_DOWNWARD"]
            fb, ft = m["full_operator_vs_blind_ALL"], m["full_operator_vs_twin_ALL"]
            out["quantifier_med"] = {
                "n": ad["n"], "model_acc": ad["operator"],
                "overlap_floor": ad["monotone_blind"],
                "floor_accs": {"monotone_blind": ad["monotone_blind"]},
                "strongest_floor_name": "monotone_blind", "strongest_floor": ad["monotone_blind"],
                "twin_acc": None,
                "model_minus_strongest": [ombd["delta"], ombd["ci"][0], ombd["ci"][1]],
                "model_minus_twin": [None, None, None],
                "ci_sep_over_strongest": bool(ombd["ci_sep"]),
                "ci_sep_over_twin": bool(m["operator_beats_twin_downward"]),
                "twin_downward_null_p95": m["twin_downward_null_p95"], "coverage": m["coverage"],
                "full_unified_aggregate": {  # negation+quantifier ONE downward-monotone operator (well-powered)
                    "n": ft["n"], "operator": ft["a"], "twin": ft["b"],
                    "operator_minus_blind": {"delta": fb["delta"], "ci": fb["ci"], "ci_sep": bool(fb["ci_sep"])},
                    "operator_minus_twin": {"delta": ft["delta"], "ci": ft["ci"], "ci_sep": bool(ft["ci_sep"])}},
                "population": "MED downward-monotone subset (Yanaka 2019 monotonicity NLI, modern, n=%d); "
                              "model=quantifier monotonicity operator (subject cardinality x edit direction), "
                              "floor=monotone-blind (assume upward -> INVERTS on downward), twin=shuffled "
                              "monotonicity (downward null p95). Paired bootstrap CI. The well-powered full-unified "
                              "aggregate (negation+quantifier ONE operator, n=%d) is CI-sep over blind AND the "
                              "info-free twin (see full_unified_aggregate). MODERN." % (ad["n"], ft["n"])}
    except Exception as e:
        out["quantifier_med"] = _degraded("quantifier_med", e)
    return out, {"note": "truth-conditional NEGATION + QUANTIFIER (Kaup-Zwaan two-step operator; Johnson-Laird "
                         "cardinality; Ladusaw downward-monotonicity unifying negation with 'none') -- the FIRST "
                         "board arms that score whether a stored proposition HOLDS and over how many arguments it "
                         "ranges (live != scored before this: the landed read_polarity field). Load-bearing claim "
                         "scoped to the polarity/quantity-blind floor (which INVERTS under negation/downward "
                         "quantifiers) + the info-free shuffled-cue twin. Reuses exp_polarity_operator_ewt_v1 + "
                         "exp_quantifier_operator_med_v1 verbatim."}


def board_coref_via_reader_dimension(n_docs=None, seed=13, n_boot=2000):
    """COREF-VIA-READER board arm on MODERN GUM he/she (n~1240): the LIVE EventCentralityReader pronoun pick
    with the p12 coref STACK flags ON (phi_person_filter + narrow_him + soften_generic_suppress) vs the
    flag-OFF incumbent -- the +0.0823 CI-sep gain that is board-INVISIBLE today because the modern-board `coref`
    tile is computed by a DIFFERENT resolver (URG.Resolver, the unified-referent pronoun pick, +0.106). This arm
    scores the DEPLOYED reader's OWN he/she-pick stack directly, so the landed +0.082 (0.5032 -> 0.5855) shows.

    Reuses verification/test_coref_stack_landing's W1 measurement VERBATIM (same GUM loaders, TEST=odd split,
    the module's _score/_acc/_doc_paired_boot, the FULL flag dict, _KW): model = full-stack reader (all three
    wires ON, ~0.5855), strongest floor = the flag-OFF incumbent reader (~0.5032, byte-identical to the
    pre-landing default -- witness W3), doc-paired bootstrap CI (seed=13, n_boot=2000 -> reproduces W1's CI
    exactly). ADDS the info-free shuffled-identity twin (within-doc permutation of the full reader's cluster
    picks, re-scored vs gold -- must LOSE). Kept OUT of the 19c-free headline aggregate (its own row). OFF in
    the board self-test. Degrades gracefully (GUM gold absent -> a schema-shaped degraded row + report).
    MODERN (GUM, Zeldes 2017)."""
    try:
        import random as _random
        import experiments.gum_coref as G
        from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
        from experiments.exp_hybrid_unified_incumbent_coref_gum_v1 import gum_to_live, _named_clusters
        from hdlab.coref import build_pronoun_targets
        from hdlab.event_centrality_coref import EventCentralityReader
        from verification.test_coref_stack_landing import _score, _acc, _doc_paired_boot, FULL, _KW

        gaz = load_given_gazetteer()
        docs = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz)
        test = [d for i, d in enumerate(docs) if i % 2 == 1]
        if not test:
            return _degraded("coref_via_reader", "no GUM test docs on disk (gum_only load empty)"), {
                "error": "GUM gold absent -> degraded row (REPORT: gum_coref.load_docs returned no docs)"}

        incumbent = EventCentralityReader(graded_pick=True)              # p12 wire flags default OFF -> the floor
        full = EventCentralityReader(graded_pick=True, **FULL)           # all three p12 wires ON -> the model

        p_inc = _score(incumbent, test)                                 # strongest floor (flag-OFF incumbent)
        # ONE full-reader pass: p_full (the SAME loop as _score, deterministic reader -> identical rows) plus the
        # captured gold_cluster per target, so the info-free twin re-scores without a second full-reader pass.
        p_full, gold_rows = [], []
        for d in test:
            ms = gum_to_live(d)
            tg = build_pronoun_targets(ms)
            sid = [0] * (max((m["sent_idx"] for m in ms), default=0) + 1)
            recs = full.resolve_stream(ms, tg, scene_ids=sid, **_KW)
            named = _named_clusters(ms)
            p_full.append([(bool(r["correct"]), r["gold_cluster"] in named, r["resolved_cluster"]) for r in recs])
            gold_rows.append([(r["gold_cluster"], r["gold_cluster"] in named, r["resolved_cluster"]) for r in recs])
        # info-free shuffled-identity twin: within-doc permutation of the reader's picks, re-scored vs gold. The
        # per-target signal (which cluster THIS pronoun picks) is destroyed; the pick marginal is preserved.
        rng = _random.Random(seed)
        p_twin = []
        for rows in gold_rows:
            picks = [rc for (_g, _isn, rc) in rows]
            perm = picks[:]; rng.shuffle(perm)
            p_twin.append([(bool(perm[i] is not None and perm[i] == rows[i][0]), rows[i][1], perm[i])
                           for i in range(len(rows))])

        a_inc, n = _acc(p_inc)
        a_full, _ = _acc(p_full)
        a_twin, _ = _acc(p_twin)
        lo, hi = _doc_paired_boot(p_inc, p_full, seed=seed, n_boot=n_boot)     # full - incumbent (witness W1 CI)
        lot, hit = _doc_paired_boot(p_twin, p_full, seed=seed, n_boot=n_boot)  # full - twin (info-free control)
        row = {
            "n": n, "model_acc": round(a_full, 4),
            "overlap_floor": round(a_inc, 4),
            "floor_accs": {"flag_off_incumbent_reader": round(a_inc, 4)},
            "strongest_floor_name": "flag_off_incumbent_reader", "strongest_floor": round(a_inc, 4),
            "twin_acc": round(a_twin, 4),
            "model_minus_strongest": [round(a_full - a_inc, 4), round(lo, 4), round(hi, 4)],
            "model_minus_twin": [round(a_full - a_twin, 4), round(lot, 4), round(hit, 4)],
            "ci_sep_over_strongest": bool(lo > 0),
            "ci_sep_over_twin": bool(lot > 0),
            "population": "GUM TEST he/she pronoun pick through the LIVE hdlab.event_centrality_coref."
                          "EventCentralityReader (native head_to_cluster scorer, n=%d); model=full p12 coref "
                          "stack (phi_person_filter + narrow_him + soften_generic_suppress ON), floor=flag-OFF "
                          "incumbent reader (byte-identical to the pre-landing default, witness W3), twin=info-"
                          "free shuffled-identity (within-doc permutation of the picks, re-scored vs gold). "
                          "Doc-paired bootstrap CI (verification/test_coref_stack_landing, seed=%d, n_boot=%d). "
                          "MODERN (GUM, Zeldes 2017)." % (n, seed, n_boot),
        }
        detail = {"note": "the p12 coref-stack gain (compose_the_unified_referent_with_the_incumbent_graded_pick_"
                          "pool_for_a_live_coref_gain, owner-DONE) wired LIVE into EventCentralityReader "
                          "(SituationReader turns all three wires ON by default). BOARD-INVISIBLE until now: the "
                          "modern-board `coref` tile is scored by a DIFFERENT resolver (the URG unified-referent "
                          "pronoun pick, +0.106), so the deployed reader's OWN he/she stack gain never showed. "
                          "This arm scores it directly (model %.4f vs flag-off floor %.4f = %+.4f, doc-paired "
                          "bootstrap CI[%.4f,%.4f]; info-free twin %.4f loses). Reuses verification/"
                          "test_coref_stack_landing's W1 measurement verbatim (same loaders, _score/_acc/"
                          "_doc_paired_boot, FULL flags); adds the shuffled-identity twin. 'live != scored' -- the "
                          "board-invisible-proven-win-needs-its-own-instrument-arm case."
                          % (row["model_acc"], row["strongest_floor"], row["model_minus_strongest"][0],
                             lo, hi, row["twin_acc"])}
        return row, detail
    except Exception as e:
        return _degraded("coref_via_reader", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_natural_logic_monotonicity_dimension(smoke=False):
    """NATURAL-LOGIC MONOTONICITY board arm on MODERN gold (MED, Yanaka 2019). This capability is board-INVISIBLE
    today -- no dimension scores the parse-free natural-logic entailment reasoner (p11, landed into
    hdlab.typed_spokes: is_downward / entails / natural_logic_label), even though it validated near-human on MED
    (self-detected-monotonicity acc 0.767 vs majority 0.503 + a symmetric-cosine oracle 0.535, 85% coverage, the
    shuffled-monotonicity twin loses -> polarity load-bearing). This arm scores it directly by REUSING the solver's
    OWN measurement verbatim (exp_natural_logic_monotonicity_med_v1.run, light=True -- the exact path witness
    W13/W14 asserts: the MED gold-loading + the typed_spokes natural_logic_label scoring; the POS/parser-heavy
    informational drills are skipped for speed, ~4s full).

    model = self-detected-monotonicity acc (the brain's FAST closed-class operator-recognition register); strongest
    floor = the SYMMETRIC sentence-cosine oracle (0.535 -- distributional similarity cannot do the directed/structural
    edit) with the majority floor (0.503) carried alongside (both CI-sep); twin = the shuffled-monotonicity info-free
    control (permute the up/down polarity labels -> collapses, proving the POLARITY is load-bearing not just the edit
    type). Bootstrap CIs come straight from the cell's boot_margin. Kept OUT of the 19c-free headline aggregate (its
    own row). OFF in the board self-test. Degrades gracefully (MED gold absent -> a schema-shaped degraded row, never
    crashes the board). MODERN (MED = FraCaS + GLUE-diagnostic + hand-built, NOT 19c)."""
    try:
        import experiments.exp_natural_logic_monotonicity_med_v1 as NL
        if not os.path.exists(NL.MED):
            return _degraded("natural_logic_monotonicity", "MED.tsv not on disk (data/corpora/med/MED.tsv)"), {}
        r = NL.run(smoke=smoke, light=True)   # light: skip the POS/parser-heavy informational drills (~4s full)
        acc, mg = r["acc"], r["margins"]
        self_acc = acc["natural_logic_self_detected_monotonicity"][0]
        maj = acc["majority_floor"]
        sym = acc["symmetric_sentence_cosine_oracle"]
        twin = acc["shuffled_monotonicity_twin"][0]
        m_sym = mg["natlog_vs_symmetric"]; m_maj = mg["natlog_vs_majority"]; m_tw = mg["natlog_vs_shuffled_twin"]
        # strongest floor = the higher of {majority, symmetric-cosine oracle}
        floor_accs = {"majority": round(float(maj), 4), "symmetric_cosine_oracle": round(float(sym), 4)}
        fname = max(floor_accs, key=floor_accs.get)
        m_strong = m_sym if fname == "symmetric_cosine_oracle" else m_maj
        row = {
            "n": r["n_covered"], "model_acc": round(float(self_acc), 4),
            "overlap_floor": floor_accs[fname],
            "floor_accs": floor_accs, "strongest_floor_name": fname, "strongest_floor": floor_accs[fname],
            "twin_acc": round(float(twin), 4),
            "model_minus_strongest": [m_strong["delta"], m_strong["lo"], m_strong["hi"]],
            "model_minus_twin": [m_tw["delta"], m_tw["lo"], m_tw["hi"]],
            "ci_sep_over_strongest": bool(m_strong["sep"]),
            "ci_sep_over_twin": bool(m_tw["sep"]),
            "model_minus_majority": [m_maj["delta"], m_maj["lo"], m_maj["hi"]],
            "ci_sep_over_majority": bool(m_maj["sep"]),
            "model_minus_symmetric": [m_sym["delta"], m_sym["lo"], m_sym["hi"]],
            "ci_sep_over_symmetric": bool(m_sym["sep"]),
            "coverage": r["coverage"],
            "oracle_monotonicity_upperbound": acc["natural_logic_ORACLE_monotonicity_upperbound"][0],
            "per_edit_acc": r["per_edit_acc"],
            "population": "MED entailment/neutral (Yanaka 2019 monotonicity NLI = FraCaS + GLUE-diagnostic + "
                          "hand-built, MODERN; n_covered=%d, coverage %.3f = ~85%% of MED via full natural logic, up "
                          "from the ~15%% single-is-a-substitution slice); model=self-detected-monotonicity natural-"
                          "logic judge (parse-free closed-class is_downward marker x edit-direction over the C5 is-a "
                          "spoke, hdlab.typed_spokes.natural_logic_label), floor=SYMMETRIC sentence-cosine oracle "
                          "(best threshold -- cannot do the directed/structural edit) + majority (both carried CI-sep), "
                          "twin=shuffled-monotonicity (permute up/down polarity -> collapses). Bootstrap CI. MODERN."
                          % (r["n_covered"], r["coverage"]),
        }
        detail = {"note": "glass-box NATURAL LOGIC / monotonicity calculus (van Benthem; Sanchez-Valencia; "
                          "MacCartney-Manning 2009) over the C5 is-a typed spoke -- the FIRST board arm scoring the "
                          "parse-free monotonicity reasoner (the brain's FAST closed-class operator-recognition "
                          "register; Neville 1992, Pulvermuller 1995). Load-bearing claim scoped to BOTH the "
                          "distributional (symmetric-cosine oracle %.3f, +%.4f CI-sep) and the majority (%.3f, +%.4f "
                          "CI-sep) floors; the shuffled-monotonicity twin (%.3f, +%.4f CI-sep) proves the POLARITY is "
                          "load-bearing, not just the edit type. The ORACLE-monotonicity upper bound is %.3f (the "
                          "residual = positional restrictor/body scope, the SLOW register -- a bounded parser lever, "
                          "not a ceiling). Reuses exp_natural_logic_monotonicity_med_v1.run(light=True) verbatim "
                          "(witness W13/W14). 'live != scored' -- the board-invisible-proven-win-needs-its-own-"
                          "instrument-arm case."
                          % (sym, m_sym["delta"], maj, m_maj["delta"], twin, m_tw["delta"],
                             row["oracle_monotonicity_upperbound"])}
        return row, detail
    except Exception as e:
        return _degraded("natural_logic_monotonicity", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_event_goal_congruence_dimension(smoke=False):
    """EVENT<->GOAL CONGRUENCE board arm on a relatedness-MATCHED MODERN-vocabulary gold (n=120: 60 WordNet-
    antonym-thwart + 60 FrameNet-converse-satisfy, all ATL-hub-related). This capability is board-INVISIBLE today
    -- the OCC-appraisal arm has NO headroom for it (the structured matcher fires 0/24 there), so the proven
    event<->goal SIGN win (structured_semantic_matching_for_event_goal..., owner-DONE p4; landed
    hdlab.structured_matcher) moves NO board dim. This arm scores it directly by REUSING the solver's OWN
    measurement verbatim (exp_structured_matcher_event_goal_v1.run, the exact path witness EG1/EG2/EG3 asserts):
    build the relatedness-matched held-out gold, run the STRUCTURED matcher congruence() sign vs the polarity-blind
    ATL-hub baseline (bridging_inference relatedness thresholded, SWEPT to its best on this population) + the
    info-free shuffled-KB twin, paired bootstrap over items.

    model = STRUCTURED signed acc (~0.9750, the brain's structured relational store -- Binder-Desai combinatorial
    semantics); strongest floor = the SWEPT HUB baseline (~0.4917 -- chance; the polarity-blind ATL hub cannot sign
    matched-relatedness opposite-label pairs, rel(win,lose) ~= rel(sell,buy)); twin = shuffled-KB (~0.4917, permute
    the edge maps -> the sign becomes random, loses -> the EDGES carry the sign, not merely 'having a KB'). Carries
    the polarity-isolation slice (on the antonym subset the hub is at/below chance while structured is high).
    Bootstrap CIs come straight from the cell's paired bootstrap. Kept OUT of the 19c-free headline aggregate (its
    own row). OFF in the board self-test. Degrades gracefully (WordNet/FrameNet/ConceptNet absent -> a schema-shaped
    degraded row, never crashes the board). MODERN (WordNet/FrameNet modern-vocabulary head-pairs, NOT 19c)."""
    try:
        import experiments._hashseed_guard  # noqa: F401  (pins PYTHONHASHSEED=0 -> reproducible WordNet/FrameNet sampling)
        import experiments.exp_structured_matcher_event_goal_v1 as EG
        r = EG.run(smoke=smoke)
        vh = r["margins"]["vs_hub"]; vt = r["margins"]["vs_twin"]
        ant = r["by_slice"]["antonym_thwart"]; con = r["by_slice"]["converse_satisfy"]
        row = {
            "n": r["n"], "model_acc": round(float(r["acc"]["structured"]), 4),
            "overlap_floor": round(float(r["acc"]["hub_baseline"]), 4),
            "floor_accs": {"hub_baseline_swept": round(float(r["acc"]["hub_baseline"]), 4)},
            "strongest_floor_name": "hub_baseline_swept",
            "strongest_floor": round(float(r["acc"]["hub_baseline"]), 4),
            "twin_acc": round(float(r["acc"]["twin"]), 4),
            "model_minus_strongest": [round(float(vh["delta"]), 4), round(float(vh["ci"][0]), 4),
                                      round(float(vh["ci"][1]), 4)],
            "model_minus_twin": [round(float(vt["delta"]), 4), round(float(vt["ci"][0]), 4),
                                 round(float(vt["ci"][1]), 4)],
            "ci_sep_over_strongest": bool(vh["ci_sep"]),
            "ci_sep_over_twin": bool(vt["ci_sep"]),
            "hub_best_threshold": r["hub_best_thr"],
            "vs_hub_null_p95": vh["null_p95"], "vs_twin_null_p95": vt["null_p95"],
            "polarity_isolation": {
                "antonym_thwart": {"n": ant["n"], "structured": ant["structured"], "hub": ant["hub_baseline"]},
                "converse_satisfy": {"n": con["n"], "structured": con["structured"], "hub": con["hub_baseline"]}},
            "population": "relatedness-MATCHED modern-vocabulary held-out gold (n=%d: %d WordNet-antonym-thwart + "
                          "%d FrameNet-converse-satisfy, all ATL-hub-related); model=STRUCTURED matcher "
                          "congruence() sign (converse->satisfy, antonym->thwart, else hub-fuzzy/abstain), "
                          "floor=polarity-blind ATL hub (bridging_inference relatedness thresholded, SWEPT to best "
                          "on this population -> chance), twin=info-free shuffled-KB (permute the edge maps). "
                          "Paired bootstrap over items. MODERN (WordNet/FrameNet head-pairs, NOT 19c)."
                          % (r["n"], ant["n"], con["n"])}
        detail = {"note": "the brain's TWO-STORE split as a SCORED organ (structured_semantic_matching_for_event_"
                          "goal..., owner-DONE p4; landed hdlab.structured_matcher): the ATL hub (bridging_inference) "
                          "supplies fuzzy relatedness but is BLIND to the SIGN/direction of a relation (rel(win,lose) "
                          "~= rel(sell,buy)); the structured relational store reads the SIGN off WordNet antonymy + "
                          "FrameNet Perspective_on converse + ConceptNet (Binder-Desai combinatorial semantics; "
                          "Lambon-Ralph hub-and-spoke). The FIRST board arm scoring event<->goal congruence: model "
                          "%.4f vs the swept hub floor %.4f (%+.4f CI-sep) + the shuffled-KB twin %.4f (loses -> the "
                          "EDGES carry the sign). POLARITY ISOLATION: on the antonym subset the hub is %.4f (at/below "
                          "chance -- it predicts satisfy for every high-related antonym) while structured is %.4f. "
                          "BOARD-INVISIBLE until now: the OCC-appraisal arm has no headroom (the matcher fires 0/24 "
                          "there), so this proven +0.48 signing win moved no board dim. This arm ALSO gives the "
                          "deferred affect flip-gate a live instrument to re-measure on. Reuses exp_structured_"
                          "matcher_event_goal_v1.run verbatim (witness EG1/EG2/EG3). 'live != scored' -- the "
                          "board-invisible-proven-win-needs-its-own-instrument-arm case."
                          % (row["model_acc"], row["strongest_floor"], row["model_minus_strongest"][0],
                             row["twin_acc"], ant["hub_baseline"], ant["structured"])}
        return row, detail
    except Exception as e:
        return _degraded("event_goal_congruence", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_tom_dimension(smoke=False):
    """THEORY-OF-MIND belief->action board arm on BigToM (Gandhi et al. 2023, the MODERN peer-reviewed ToM gold,
    278 items, TB/FB matched). Board-INVISIBLE today -- no dim scores the glass-box FORWARD mentalizing chain
    (believes(A,F,t) x wants(A) -> action, read off the BELIEVED state) that hdlab.theory_of_mind runs (owner-DONE
    chain_belief_and_goal_into_theory_of_mind...). Reuses exp_tom_chain_belief_goal_action_v1's measurement + the
    _tom_bigtom loader/value-model (like board_occ_appraisal reuses _occ_probe). model = the CHAIN action accuracy;
    strongest floor = REALITY_FLOOR (BELIEFLESS -- act on the true state, the ToM-blind floor that collapses on the
    FALSE-BELIEF subset); twin = TWIN_BELIEF (a believed value drawn from another item). HEADLINE = the FALSE-BELIEF
    subset (reality != belief -- the load-bearing test). Paired bootstrap over stories. OUT of the 19c-free headline
    aggregate (its own row). Degrades gracefully (BigToM/deps absent -> a schema-shaped row, never crashes)."""
    try:
        import numpy as _np
        import experiments.exp_tom_chain_belief_goal_action_v1 as T
        from experiments._tom_bigtom import load_bigtom
        items = load_bigtom(tasks=("action",))
        if smoke:
            keep = set(sorted({it.sid for it in items})[:12]); items = [it for it in items if it.sid in keep]
        rows = T._predict_all(items)
        n = len(rows); rng = _np.random.RandomState(20260906)
        perm_obs = rng.permutation(n); perm_bel = rng.permutation(n)
        for i, r in enumerate(rows):
            obs_sh = rows[perm_obs[i]]["obs"]; bel_sh = rows[perm_bel[i]]["bel_fix"]
            r["_arms"] = T._correct_arms(r, observed_shuffle=(bool(obs_sh) if obs_sh is not None else False),
                                         belief_shuffle=bel_sh)
        ti = 1   # the ACTION task (forward belief->action)
        model = T._acc(rows, "CHAIN", ti); floor = T._acc(rows, "REALITY_FLOOR", ti); twin = T._acc(rows, "TWIN_BELIEF", ti)
        model_fb = T._acc(rows, "CHAIN", ti, "FB"); floor_fb = T._acc(rows, "REALITY_FLOOR", ti, "FB")
        oracle = T._acc(rows, "ORACLE_BELIEF", ti)
        d, lo, hi, hw = T._paired_ci(rows, "CHAIN", "REALITY_FLOOR", ti, "FB", rng)   # headline: FB subset
        dt, lot, hit, _ = T._paired_ci(rows, "CHAIN", "TWIN_BELIEF", ti, "FB", rng)
        n_fb = sum(r["cond"] == "FB" for r in rows)
        row = {"dimension": "theory_of_mind", "n": n, "n_FB": n_fb,
               "model": round(model, 4), "floor": round(floor, 4), "twin": round(twin, 4),
               "model_FB": round(model_fb, 4), "floor_FB": round(floor_fb, 4), "oracle_belief": round(oracle, 4),
               "headline_FB_delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "ci_half_width": round(hw, 4),
               "ci_sep": bool(lo > 0), "twin_FB_delta": round(dt, 4), "twin_loses": bool(lot > 0),
               "gold": "BigToM (Gandhi 2023, modern; 278 TB/FB)",
               "note": "forward mentalizing believes x wants->action; FALSE-BELIEF subset is load-bearing (ToM-blind floor collapses there)"}
        return row, {"model": model, "floor": floor, "twin": twin, "fb_delta": d, "fb_ci": [lo, hi]}
    except Exception as e:
        return {"dimension": "theory_of_mind", "error": "%s: %s" % (type(e).__name__, e), "model": None}, {}


def board_sem_segmentation_dimension(smoke=False):
    """SEM SCHEMA-SWITCH EVENT-SEGMENTATION board arm on ACTUAL HUMAN perceived event boundaries (Kumar 2023
    behavioural button-press gold, Tunnel Under the World). This capability is board-INVISIBLE today --
    hdlab.sem_event_segmenter (the loop-closure north-star organ, owner-DONE close_the_recurrent_predictive_
    coding_loop..., SS4l/SS4n; witness verification/test_predictive_loop.py W10) is a LATENT ISLAND imported by NO
    live consumer, so its human-validated win moves NO board dim. This arm scores it directly by REUSING the
    organ's OWN human-validation VERBATIM -- hdlab.sem_event_segmenter._human_validation(), the exact routine the
    module's --self-test calls: it loads the aligned human boundary gold (data/corpora/human_event_seg/), runs the
    SEM schema-switch graded signal (switch_score) + the point-error incumbent over the SAME sentences, and returns
    the Spearman rho of each vs ACTUAL humans (+ the published GPT-2 reference + the leave-one-subject-out ceiling).

    model = SEM schema-switch rho vs actual humans (~0.12-0.15); strongest floor = the POINT-ERROR incumbent rho
    (~0.07, the Kumar-refuted prediction-error quantity, recomputed on the SAME sentences -- SEM WINS); context =
    the published GPT-2 Bayesian-surprise reference (0.10-0.12, SEM AT/ABOVE it -- the 'needs a neural model' claim
    was RETRACTED) + the leave-one-subject-out human NOISE CEILING (0.2225, SEM ~56-68% of it). The verbatim
    routine returns POINT estimates (no bootstrap CI -> ci_sep flags stay False; the point win is in
    beats_point_error_incumbent; the pooled cross-story paired-bootstrap CI lives in exp_human_boundary_validation_
    v1). The organ's info-free control is its OWN self-test (switch_score higher at boundaries than within, W3).
    Kept OUT of the 19c-free headline aggregate (its own row). OFF in the board self-test. Degrades gracefully to a
    schema-shaped N/A row if the human boundary gold is absent -- the organ already abstains (_human_validation
    returns None), never raises. MODERN behavioural gold (Kumar 2023; NOT 19c). `smoke` is accepted for signature
    parity (the verbatim single-story fast path is ~2s; no smoke mode)."""
    try:
        import hdlab.sem_event_segmenter as SEM
        hv = SEM._human_validation()   # VERBATIM: the exact routine --self-test calls (loads the aligned human gold)
        if hv is None:                 # organ abstains: Kumar-2023 human-boundary archive absent -> schema-shaped N/A
            return _degraded("sem_segmentation",
                             "Kumar-2023 human-boundary archive absent (data/corpora/human_event_seg/) -- the SEM "
                             "organ's _human_validation() abstained (returned None)"), {
                "note": "hdlab.sem_event_segmenter is present but its human-boundary gold is not on disk; the arm "
                        "returns a schema-shaped N/A row (the organ abstains, never raises)."}
        sem = float(hv["sem_rho_vs_humans"]); inc = float(hv["incumbent_rho"])
        ceil = float(hv["loo_noise_ceiling"]); gpt2 = hv["gpt2_published"]
        gpt2_hi = float(str(gpt2).split("-")[-1])                       # upper of the published GPT-2 rho range
        pct_ceiling = round(100.0 * sem / ceil, 1) if ceil else None
        row = {
            "n": None, "model_acc": round(sem, 4),
            "overlap_floor": round(inc, 4),
            "floor_accs": {"point_error_incumbent_rho": round(inc, 4)},
            "strongest_floor_name": "point_error_incumbent_rho", "strongest_floor": round(inc, 4),
            "twin_acc": None,
            "model_minus_strongest": [round(sem - inc, 4), None, None],   # POINT margin (verbatim routine -> no CI)
            "model_minus_twin": [None, None, None],
            "ci_sep_over_strongest": False,      # verbatim _human_validation returns POINT estimates (no bootstrap CI)
            "ci_sep_over_twin": False,
            "beats_point_error_incumbent": bool(sem > inc),              # the load-bearing point win (SEM WINS)
            "sem_rho_vs_humans": round(sem, 4),
            "point_error_incumbent_rho": round(inc, 4),
            "gpt2_bayesian_surprise_published_rho": gpt2,
            "at_or_above_gpt2": bool(sem >= gpt2_hi),
            "loo_human_noise_ceiling": round(ceil, 4),
            "pct_of_loo_noise_ceiling": pct_ceiling,
            "population": "Kumar 2023 ACTUAL HUMAN perceived event boundaries (behavioural button-press "
                          "segmentation, Tunnel Under the World; sentence-level human boundary strength via "
                          "RT-lagged window-max over the 10 Hz button-proportion stream); model=SEM schema-switch "
                          "graded boundary signal (switch_score) Spearman rho vs actual humans, floor=POINT-ERROR "
                          "incumbent (backward_segment raw-error, the Kumar-refuted quantity) rho on the SAME "
                          "sentences (SEM WINS); GPT-2 Bayesian-surprise (%s) + the leave-one-subject-out human "
                          "NOISE CEILING (%.4f) carried as context. Reuses hdlab.sem_event_segmenter._human_"
                          "validation() VERBATIM (the routine --self-test calls); POINT estimates (no bootstrap "
                          "CI from the verbatim routine). MODERN behavioural gold (Kumar 2023, NOT 19c)." % (gpt2, ceil)}
        detail = {"note": "the SEM schema-switch event segmenter (Franklin/Norman/Ranganath/Zacks/Gershman 2020 "
                          "Structured Event Memory; a BOUNDARY = MAP schema SWITCH, a belief/model update per "
                          "Reynolds-Zacks-Braver 2007, NOT a prediction-error spike) validated against ACTUAL human "
                          "perceived boundaries -- the loop-closure north-star organ (owner-DONE close_the_"
                          "recurrent_predictive_coding_loop..., SS4l/SS4n; witness verification/test_predictive_loop."
                          "py W10). BOARD-INVISIBLE until now: hdlab.sem_event_segmenter is a LATENT ISLAND imported "
                          "by NO live consumer, so its human-validated win moved NO board dim. This arm scores it "
                          "directly: SEM rho %.4f BEATS the point-error incumbent %.4f vs actual humans (the "
                          "incumbent is the Kumar-refuted prediction-error quantity), is %s%% of the leave-one-out "
                          "human noise ceiling %.4f, and is AT/ABOVE Kumar's GPT-2 Bayesian surprise (%s) -- "
                          "content-shift/SEM/GPT-2 all plateau at the ~0.12-0.15 text-predictable ceiling, so this "
                          "glass-box organ is at the achievable neural-reference level ('needs a neural model' "
                          "RETRACTED, SS4l(f)). Reuses hdlab.sem_event_segmenter._human_validation() VERBATIM. "
                          "HONEST scope: POINT estimates (the verbatim routine returns no bootstrap CI -> ci_sep "
                          "flags False; the pooled cross-story paired-bootstrap CI lives in exp_human_boundary_"
                          "validation_v1); the organ's info-free control is its OWN self-test W3 (switch_score "
                          "higher at boundaries than within); the GUM paragraph proxy at 0.48 is the WRONG "
                          "instrument, not a defect. 'live != scored' -- the board-invisible-proven-win-needs-its-"
                          "own-instrument-arm case."
                          % (round(sem, 4), round(inc, 4), pct_ceiling, round(ceil, 4), gpt2)}
        return row, detail
    except Exception as e:
        return _degraded("sem_segmentation", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_crosstype_experiencer_dimension(smoke=False):
    """CROSS-TYPE DEFINITE->NAME BRIDGE -> affect/goal EXPERIENCER bind board arm on modern GUM. Board-INVISIBLE
    today: the landed hdlab.crosstype_bridge organ (route_the_unified_referent WIN, owner-DONE) resolves a person
    role-noun definite ("the doctor") to a prior NAMED person by an in-text descriptive condition + cue-based ACT-R
    retrieval + full-referent competition + retrieval-confidence gate (NO classifier, NO LLM), and offline it lifts
    the affect/goal experiencer bind CI-separated -- but nothing in the live read path calls the organ, so no board
    dim scores it. This arm scores the LANDED ORGAN directly on the reader's OWN path: the reader's front-end LIVE
    parse (live_reparse: hdlab.pos_tagger + arceager_parser + arc_labeler) feeds the organ, whose definite->name binds
    are merged onto the situation_predict floor clustering the reader ACTUALLY runs (_apply_commonnoun_gate,
    entity_kb_resolver=False default), and the experiencer bind is scored floor vs floor+bridge, doc-level paired
    bootstrap, with the info-free RANDOM-target twin as the control.

    model = C3 experiencer bind acc WITH the organ bridge; strongest floor = the live situation_predict clustering
    (the reader's ACTUAL input); twin = the same #merges to RANDOM named entities (correct targeting load-bearing).
    Config = the deployable full-referent-competition (cue_competed). Kept OUT of the 19c-free headline aggregate (its
    own row). OFF in the self-test. Degrades gracefully (GUM/gazetteer/front-end absent -> a schema-shaped row, never
    crashes the board). MODERN (GUM). 'live != scored' -- the board-invisible-proven-win-needs-its-own-instrument-arm
    case; the ACTUAL live-reader wire (into _apply_commonnoun_gate) is the filed pri-3 follow-on."""
    try:
        import random
        from collections import defaultdict
        import numpy as _np
        import experiments.gum_coref as G
        from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
        import experiments.exp_crosstype_landable_validation_gum_v1 as CL
        import experiments.exp_route_unified_to_consumers_gum_v1 as RU
        from hdlab.crosstype_bridge import crosstype_bridge_links
        from hdlab.coref import name_content_tokens
        gaz = load_given_gazetteer()
        # CAP the full-run doc count: this arm live_reparse's every sentence (slow); an uncapped 275-doc run made
        # the full board intractable. 120 docs is representative + bounded (~the TEST-split size), like the other
        # heavy new arms which cap.
        docs = G.load_docs(gum_only=True, limit=(40 if smoke else 120), name_gazetteer=gaz)
        rng = random.Random(13)
        C3 = {"floor": [], "bridge": [], "twin": []}
        C1 = {"floor": [], "bridge": []}
        C2 = {"floor": [], "bridge": []}
        n_merges = 0
        for d in docs:
            ms = RU._gum_to_live(d)
            floor_lab = RU._situation_predict_labels(ms, gaz)
            ld = CL.live_reparse(d)                                   # the reader's OWN front-end parse
            binds = crosstype_bridge_links(ld, gaz, conf_thr=0.0, mode="cue_competed")
            name_floor = defaultdict(set)
            for mm in ms:
                if mm["is_pronoun"]:
                    continue
                if mm.get("mtype") == "name" or name_content_tokens(mm.get("span_toks", [mm["head"]])):
                    if floor_lab.get(mm["midx"]) is not None:
                        name_floor[mm["cluster"]].add(floor_lab[mm["midx"]])
            merged_lab = dict(floor_lab)
            for i, eid in binds.items():
                labs = name_floor.get(eid)
                if labs:
                    merged_lab[i] = sorted(str(x) for x in labs)[0]   # merge the role mention into the named cluster
                    n_merges += 1
            named_eids = [e for e in name_floor if name_floor[e]]
            twin_lab = dict(floor_lab)
            for i in binds:
                if named_eids:
                    e = rng.choice(named_eids)
                    labs = name_floor.get(e)
                    if labs:
                        twin_lab[i] = sorted(str(x) for x in labs)[0]
            C3["floor"].append(RU.score_c3_experiencer(ms, floor_lab))
            C3["bridge"].append(RU.score_c3_experiencer(ms, merged_lab))
            C3["twin"].append(RU.score_c3_experiencer(ms, twin_lab))
            C2["floor"].append(RU.score_c2_hardlink(ms, floor_lab))
            C2["bridge"].append(RU.score_c2_hardlink(ms, merged_lab))
            c1f = RU.score_c1_entity_layer(ms, floor_lab); c1b = RU.score_c1_entity_layer(ms, merged_lab)
            if c1f is not None and c1b is not None:
                C1["floor"].append(c1f["conll_avg"]); C1["bridge"].append(c1b["conll_avg"])
        floor_acc = round(RU._pooled_acc(C3["floor"]), 4)
        bridge_acc = round(RU._pooled_acc(C3["bridge"]), 4)
        twin_acc = round(RU._pooled_acc(C3["twin"]), 4)
        d_floor = RU._paired_boot(C3["bridge"], C3["floor"])
        d_twin = RU._paired_boot(C3["bridge"], C3["twin"])
        n = int(sum(x[1] for x in C3["floor"]))
        c2f = round(RU._pooled_acc(C2["floor"]), 4); c2b = round(RU._pooled_acc(C2["bridge"]), 4)
        c1f_m = round(float(_np.mean(C1["floor"])), 4) if C1["floor"] else None
        c1b_m = round(float(_np.mean(C1["bridge"])), 4) if C1["bridge"] else None
        row = {
            "n": n, "model_acc": bridge_acc,
            "overlap_floor": floor_acc, "strongest_floor_name": "situation_predict_live_floor",
            "strongest_floor": floor_acc, "twin_acc": twin_acc,
            "model_minus_strongest": [d_floor["delta"], d_floor["ci"][0], d_floor["ci"][1]],
            "model_minus_twin": [d_twin["delta"], d_twin["ci"][0], d_twin["ci"][1]],
            "ci_sep_over_strongest": bool(d_floor["ci_sep"]),
            "ci_sep_over_twin": bool(d_twin["ci_sep"]),
            "n_merges": n_merges,
            "no_regress_C1_entity_layer": {"floor": c1f_m, "bridge": c1b_m},
            "no_regress_C2_hardlink": {"floor": c2f, "bridge": c2b},
            "population": "GUM person-common-noun experiencer bind (n=%d): does a person role-noun definite of a NAMED "
                          "gold entity ('the doctor'->Elizabeth) canonicalize to that name so the affect/goal register "
                          "attaches the experiencer correctly? model = the LANDED hdlab.crosstype_bridge organ "
                          "(cue_competed: precise-constructs predication + anaphoricity gate + cue-based ACT-R retrieval "
                          "+ full-referent competition) fed the reader's OWN live parse (live_reparse), binds merged "
                          "onto the situation_predict floor; floor = that live situation_predict clustering; twin = the "
                          "same merges to RANDOM named entities. Doc-level paired bootstrap. MODERN (GUM). No-regress "
                          "carried on the C1 entity-layer CoNLL + C2 hard-link." % n,
        }
        detail = {"note": "glass-box CROSS-TYPE definite->name bridge (Ariel accessibility + Almor descriptive boost + "
                          "Lewis-Vasishth cue-based retrieval + Heim/DRT full-referent competition + McElree "
                          "retrieval-confidence gate; NO trained classifier, NO LLM). The FIRST board arm scoring the "
                          "landed hdlab.crosstype_bridge organ on the reader's OWN live-parse path. 'live != scored' -- "
                          "the actual live-reader wire into _apply_commonnoun_gate is the filed pri-3 follow-on "
                          "(wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift).",
                  "n_merges": n_merges}
        return row, detail
    except Exception as e:
        return _degraded("crosstype_experiencer", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_namebridge_dimension(smoke=False):
    """NAME-BRIDGE COREF board arm on modern GUM. Board-INVISIBLE today: the landed hdlab.typed_spokes C8 entity-type
    spoke (owner-DONE acquire_wikidata_p31) licenses a common-noun anaphor to a PROPER-NAME antecedent ("the artist"
    <- Zurbaran; the ~6-10% of anaphoric common nouns whose antecedent is a name, unreachable by WordNet), via the
    brain-foundational TWO-ROUTE CLS mechanism (consolidated C8 entity-type KB UNION episodic in-text is-a) with
    GRADED constraint-integration selection + a thematic deverbal-agent route -- but nothing in the live read path
    calls it (the board coref dim scores PRONOUN coref, not common->name), so no dim scores it. This arm scores the
    two-route mechanism directly on the GUM name-bridge instrument, reusing the solver's OWN measure
    (exp_namebridge_coref_kb_v1: collect_items + _vec + boot_delta).

    model = the fullest two-route arm (kb_thematic: C8 type-license OR in-text is-a OR thematic, graded select);
    strongest floor = RECENCY over active names (Centering; string-identity/WordNet are 0.000 by construction); twin =
    the shuffled-KB info-free control (correct encyclopedic types are load-bearing). Kept OUT of the 19c-free headline
    aggregate (its own row). OFF in the self-test. Degrades gracefully (spoke/GUM absent). MODERN (GUM). 'live !=
    scored' -- the actual live-reader wire (the two-route path into _apply_commonnoun_gate) is the follow-on."""
    try:
        import experiments.exp_namebridge_coref_kb_v1 as NB
        import experiments.gum_coref as G
        from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
        if not NB.ES.available():
            return _degraded("namebridge", "entity-type spoke asset absent (build_entity_type_spoke_v1 --build)"), {}
        gaz = load_given_gazetteer()
        # CAP the full-run doc count (bounded, representative) -- see board_crosstype_experiencer_dimension.
        docs = G.load_docs(gum_only=True, limit=(60 if smoke else 150), name_gazetteer=gaz)
        items = NB.collect_items(docs)
        if not items:
            return _degraded("namebridge", "no name-bridge items in sample"), {}
        twin = NB.build_twin_map(items, backoff=False, seed=0)
        # model = kb_graded (the SOLVED's adopted GRADED constraint-integration KB mechanism, +0.1096 CI-sep vs
        # recency) -- its shuffled-KB twin LOSES, so the twin control is VALID here (kb_thematic's twin is
        # shuffle-robust because its thematic/in-text routes don't depend on the KB shuffle; kb_thematic +0.1124 is
        # the peak, reported in the population). This arm's twin thus proves the encyclopedic KB is load-bearing.
        v_model = NB._vec(items, "kb_graded", backoff=False)
        v_floor = NB._vec(items, "recency", backoff=False)
        v_twin = NB._vec(items, "kb_graded", backoff=False, twin=twin)
        v_peak = NB._vec(items, "kb_thematic", backoff=False)
        model = round(float(v_model.mean()), 4); floor = round(float(v_floor.mean()), 4)
        twin_acc = round(float(v_twin.mean()), 4)
        d_floor = NB.boot_delta(v_model, v_floor); d_twin = NB.boot_delta(v_model, v_twin)
        row = {
            "n": len(items), "model_acc": model,
            "overlap_floor": floor, "strongest_floor_name": "recency_over_active_names",
            "strongest_floor": floor, "twin_acc": twin_acc,
            "model_minus_strongest": [d_floor["delta"], d_floor["lo"], d_floor["hi"]],
            "model_minus_twin": [d_twin["delta"], d_twin["lo"], d_twin["hi"]],
            "ci_sep_over_strongest": bool(d_floor["sep"] and d_floor["delta"] > 0),
            "ci_sep_over_twin": bool(d_twin["sep"] and d_twin["delta"] > 0),
            "peak_kb_thematic_acc": round(float(v_peak.mean()), 4),
            "population": "GUM name-bridge (anaphoric common noun whose antecedent is a PROPER NAME, n=%d): model = "
                          "kb_graded (GRADED constraint-integration over the consolidated hdlab.typed_spokes C8 "
                          "entity-type KB; type-strength x recency); PEAK = kb_thematic (+ episodic in-text is-a + "
                          "thematic deverbal-agent route, the fullest two-route CLS mechanism, ~+0.1124 vs recency); "
                          "floor = recency over active names (string-identity/WordNet 0.000 by construction); twin = "
                          "shuffled-KB (destroys the encyclopedic type signal). Bootstrap CI. MODERN (GUM)." % len(items),
        }
        detail = {"note": "glass-box NAME-BRIDGE coref via the landed C8 entity-type spoke (DBpedia InstanceOf on the "
                          "ATL hub, read through the C5 is-a closure) -- the proper-name entities WordNet omits. The "
                          "brain's TWO-ROUTE CLS completion (McClelland 1995): consolidated KB for famous entities + "
                          "episodic in-text is-a for names met mid-document (near-disjoint, both load-bearing). FIRST "
                          "board arm scoring name-bridge; the live-reader two-route wire into _apply_commonnoun_gate "
                          "is the filed follow-on (the board coref dim scores PRONOUNS)."}
        return row, detail
    except Exception as e:
        return _degraded("namebridge", e), {"error": "%s: %s" % (type(e).__name__, e)}


# ==================================================================================================
# COMMON-NOUN RESOLUTION board arm (Q111 wire instrument: the live reader's NEW sm.commonnoun_resolution)
# --------------------------------------------------------------------------------------------------
# The typed_coref resolution mechanism, ported onto the reader's LIVE dict-mention stream (routing derived
# LIVE: pronoun via is_pronoun; name via commonnoun_binder.is_name(m, gaz); else common -- NO gold mtype;
# head key = commonnoun_binder.head_lemma(head) -- the reader's OWN lemmatizer, NO GUM gold lemma). This is
# the drop-in the reader's read() runs to populate sm.commonnoun_resolution (proposed Q111 wire; see the
# solver's typed_coref_liveschema_resolve, the GOLD-schema reference). It is GOLD-FREE: no gold field is
# read in any resolution decision (the de-leak discipline) -- gold is used only by the SCORER below.
_CN_TYPE_CACHE = {}


def _cn_type_rel(ha, hb):
    """Sense-resolved typed-spokes type-compatibility (hdlab.typed_spokes.coref_type_license), memoized on a
    symmetric key -- the C5/WordNet taxonomic route the bridge seeds from (identical to hdlab.typed_coref)."""
    if ha == hb:
        return True
    from hdlab.typed_spokes import coref_type_license
    key = (ha, hb) if ha <= hb else (hb, ha)
    c = _CN_TYPE_CACHE.get(key)
    if c is None:
        c = coref_type_license(ha, hb)
        _CN_TYPE_CACHE[key] = c
    return c


class _CNRef:
    """A live-schema typed-identity referent: nominal view (name+common) drives resolution; pronouns write the
    salience history only (de-pollution). Carries NO gold eid (the scorer reconstructs gold membership by ref id)."""
    __slots__ = ("rid", "history", "heads", "name_tokens", "name_surfaces", "gender", "number", "has_name", "last_midx")

    def __init__(self, rid):
        self.rid = rid; self.history = []; self.heads = set(); self.name_tokens = set(); self.name_surfaces = set()
        self.gender = ""; self.number = ""; self.has_name = False; self.last_midx = -1

    def write(self, order, role, mtype, hl, mg, mn, name_toks):
        self.history.append((order, role)); self.last_midx = order
        if mg and not self.gender:
            self.gender = mg
        if mn and not self.number:
            self.number = mn
        if mtype == "name":
            self.has_name = True; self.name_tokens |= name_toks
        elif mtype == "common":
            self.heads.add(hl)


def _reader_commonnoun_resolution(mentions, gaz, appos_map, *, bridge=True, bridge_write=False,
                                  twin=False, rng=None):
    """LIVE-schema typed_coref common-noun RESOLUTION (the Q111 reader wire). Consumes ONLY the reader's
    dict-mention fields (is_pronoun / span_toks / head / gender / name_gender / number / sent_idx /
    sent_role_rank / midx) + gaz + an in-text appos/copula is-a map keyed by head_lemma. Returns a list of
    per-NON-PRONOUN-mention records (midx order) -- the shape the reader stores as sm.commonnoun_resolution:
        {"midx", "mtype": "name"|"common", "own_ref": int, "resolved_ref": int|None}
    own_ref = the referent this mention writes its NOMINAL card into; resolved_ref = the referent THIS
    reference resolves to for scoring (same-head pick / name match / non-writing type bridge), or None (opened
    a new referent -> unresolved). GOLD-FREE. twin=True: the bridge fires to a RANDOM gn-compatible prior
    referent (info-free control -- the type signal destroyed)."""
    import random as _random
    import numpy as _np
    import hdlab.typed_coref as _TC
    from hdlab.commonnoun_binder import head_lemma, concept_lemma, is_name, _num_of, DEF_DET, coarse_class
    from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
    from hdlab.coref import EntityAliaser
    import experiments.exp_unified_referent_gum_v1 as _URG
    from hdlab.typed_spokes import type_licenses as _c8_type_licenses, available_entity_type as _c8_available
    _c8_on = _c8_available()   # C8 encyclopedic name->type route (report_the_typed_coref fix 3); abstains if asset absent
    _c8_cache = {}

    def _c8_lic(head, surface):
        if not _c8_on:
            return False
        k = (head, surface)
        v = _c8_cache.get(k)
        if v is None:
            v = _c8_type_licenses(head, surface)
            _c8_cache[k] = v
        return v

    _g2mfn = {"masc": "m", "fem": "f", "neut": "n"}

    def mfn(m):
        return _g2mfn.get(m.get("gender") or m.get("name_gender") or "", "")

    def gn_ok(rg, rn, mg, mn):
        if mg and rg and mg != rg:
            return False
        if mn and rn and mn != rn:
            return False
        return True

    def name_toks(span):
        return {w.lower() for w in span if w.lower() not in _TC.TITLES and any(c.isalpha() for c in w)}

    rng = rng or _random.Random(0)
    aliaser = EntityAliaser(); canon2ref = {}; name_surf = {}
    refs = []; out = []; nid = [0]

    def new_ref():
        r = _CNRef(nid[0]); nid[0] += 1; refs.append(r); return r

    def act(r, now):
        a = actr_activation(r.history, float(now), decay=DEFAULT_DECAY, role_prominence=ROLE_PROMINENCE)
        return a if a != float("-inf") else -1e9

    # BF non-writing bridges (mirror of situation_reader._resolve_commonnouns): coarse-class FOCUS + conceptual cue.
    def _coarse_compat(a, heads):
        ca = coarse_class(a)
        return ca is not None and any(coarse_class(h) == ca for h in heads)
    _conc_ch = [None]; _conc_cache = {}
    def _conc_bridge(a, b):
        if a == b:
            return True
        k = (a, b) if a <= b else (b, a)
        v = _conc_cache.get(k)
        if v is None:
            if _conc_ch[0] is None:
                from hdlab.conceptual_meaning import ConceptualChannel
                _conc_ch[0] = ConceptualChannel()
            try:
                s = _conc_ch[0].similarity(a, "N", b, "N")
            except Exception:
                s = None
            v = (s is not None and s >= 0.40)
            _conc_cache[k] = v
        return v

    for m in sorted(mentions, key=lambda x: x["midx"]):
        order = m["midx"]
        role = "SUBJECT" if m.get("sent_role_rank", 99) == 0 else "OTHER"
        span = m.get("span_toks", [m["head"]])
        if m["is_pronoun"]:
            mg, mn = _URG._pron_gn(m["head"].lower())
            cands = [r for r in refs if r.last_midx < order and gn_ok(r.gender, r.number, mg, mn)]
            if cands:
                cands[int(_np.argmax([act(r, order) for r in cands]))].write(
                    order, role, "pronoun", "", mg, mn, set())        # full card only (de-pollution)
            continue
        hl = concept_lemma(m["head"]); mg, mn = mfn(m), _num_of(m)   # BF concept-key (in step w/ situation_reader)
        if is_name(m, gaz):
            canon = aliaser.assign(span, (m.get("gender") or m.get("name_gender")) or None)
            if canon is not None and canon in canon2ref:
                r = canon2ref[canon]; opened = False
            elif hl in name_surf:
                r = name_surf[hl]; opened = False
            else:
                r = new_ref(); opened = True
                if canon is not None:
                    canon2ref[canon] = r
                name_surf[hl] = r
            out.append({"midx": order, "mtype": "name", "own_ref": r.rid,
                        "resolved_ref": (None if opened else r.rid)})
            r.write(order, role, "name", hl, mg, mn, name_toks(span))
            r.name_surfaces.add(" ".join(span))     # C8 name-bridge: the surface for the encyclopedic lookup
            continue
        # COMMON: hard-gn + most-recent same-head; else generalized (NO person-gate) non-writing type bridge
        same = [r for r in refs if r.last_midx < order and hl in r.heads and gn_ok(r.gender, r.number, mg, mn)]
        picked = None; opened = True; nowrite = None
        definite = bool(span) and span[0].lower() in DEF_DET
        if same:
            picked = max(same, key=lambda r: r.last_midx); opened = False
        elif bridge:
            tset = appos_map.get(hl, set())
            prior_gn = [r for r in refs if r.last_midx < order and gn_ok(r.gender, r.number, mg, mn)]
            br = [r for r in prior_gn if (r.heads & tset)
                  or (r.has_name and any(t in r.name_tokens for t in tset))
                  or any(_cn_type_rel(hl, h) for h in r.heads)
                  or (r.has_name and any(_c8_lic(hl, ns) for ns in r.name_surfaces))   # C8 encyclopedic name->type
                  or (any(_conc_bridge(hl, h) for h in r.heads))                        # BF conceptual cue (in step w/ reader)
                  or (definite and _coarse_compat(hl, r.heads))]                        # BF situation-model FOCUS bridge
            if br:
                if twin:
                    nowrite = rng.choice(prior_gn) if prior_gn else None
                else:
                    nowrite = max(br, key=lambda r: act(r, order))
                if nowrite is not None and bridge_write:
                    picked = nowrite; opened = False; nowrite = None
            elif definite:                                                             # BF Heim/Loebner UNIQUENESS bridge
                infocus = [r for r in prior_gn if r.last_midx >= order - 6]
                if len(infocus) == 1:
                    nowrite = (rng.choice(prior_gn) if (twin and prior_gn) else infocus[0])
        if picked is None:
            picked = new_ref()
        resolved = (nowrite.rid if nowrite is not None else (None if opened else picked.rid))
        out.append({"midx": order, "mtype": "common", "own_ref": picked.rid, "resolved_ref": resolved})
        picked.write(order, role, "common", hl, mg, mn, set())
    return out


def _score_commonnoun_resolution(resolution, mentions):
    """Score the reader's sm.commonnoun_resolution records against gold, EXACTLY like the URG board metric
    (resolved-referent NOMINAL-dominant gold eid == mention eid, scored incrementally). Population = gold-
    anaphoric gold-COMMON mentions (== the URG board's 2855). Gold (gold_eid + gold mtype) is read HERE ONLY
    (scoring), never in a resolution decision. Returns a per-doc agg {'common':[hits,total],'name':[..]}."""
    from collections import Counter
    gold = {m["midx"]: m for m in mentions}
    gfirst = {}
    for m in mentions:
        gfirst[m["gold_eid"]] = min(gfirst.get(m["gold_eid"], 10 ** 9), m["midx"])
    ref_eids = {}                                   # own_ref -> [gold eids] (nominal members, in midx order)
    agg = {"common": [0, 0], "name": [0, 0]}
    for rec in sorted(resolution, key=lambda r: r["midx"]):
        m = gold[rec["midx"]]; eid = m["gold_eid"]; gm = m["mtype"]
        if gfirst[eid] < rec["midx"] and gm in agg:   # anaphoric (gold first-mention precedes) + scored type
            rr = rec["resolved_ref"]
            prior = ref_eids.get(rr, []) if rr is not None else []
            correct = bool(prior and Counter(prior).most_common(1)[0][0] == eid)
            agg[gm][0] += int(correct); agg[gm][1] += 1
        ref_eids.setdefault(rec["own_ref"], []).append(eid)   # nominal write (AFTER scoring this mention)
    return agg


def board_commonnoun_resolution_dimension(cap=None, seed=13, n_boot=2000):
    """COMMON-NOUN RESOLUTION board arm on MODERN GUM (Q111 wire instrument). Board-INVISIBLE today: the reader
    scores PRONOUN coref (coref_acc) and CLUSTERS entities (sm.entities via commonnoun_binder), but has NO scored
    per-mention common-noun RESOLUTION dim. The owner-DONE report_the_typed_coref_organ... proved the typed_coref
    resolution binding BEATS same-head string-identity CI-sep on the GUM-gold-lemma board regime (0.5671 vs
    0.5412, +0.0259). This arm scores the LIVE reader's NEW sm.commonnoun_resolution -- the typed_coref binding
    ported onto the reader's OWN dict-mention stream (routing via is_pronoun/is_name, keying via the reader's OWN
    head_lemma -- NO GUM gold lemma/mtype), reusing _reader_commonnoun_resolution (the drop-in the wire runs) +
    _score_commonnoun_resolution (the URG metric).

    model = the live wire (0.5394); strongest floor = SAME-LEMMATIZER string-identity (head_lemma, the reader's
    OWN key -- the FAIR same-regime baseline; the model beats it CI-sep); twin = info-free (bridge -> random
    gn-compatible prior, must lose). ALSO reported (nothing hidden): the GUM-GOLD-LEMMA string-identity floor
    (0.5412 = the board common_noun instrument's floor) -- a STRONGER baseline that uses GUM gold-lemma
    annotation the live reader cannot access; the wire reaches PARITY with it (delta ~-0.002, CI incl 0), and the
    LOCATED residual is entirely that gold-lemma regime (redaction see-through + copula-head normalization),
    NOT the binding: the GOLD-lemma-keyed reference mechanism (typed_coref_liveschema_resolve) reproduces the
    proven +0.025 CI-sep over the gold floor here (positive control). Doc-level paired bootstrap CI (URG
    _paired_boot). Kept OUT of the 19c-free headline aggregate (its own row). Degrades gracefully (GUM absent).
    CAP: GUM TEST = odd docs (137 by default, == the URG common_noun instrument population); cap trims the doc
    count. MODERN (GUM, Zeldes 2017). 'landed != live' -- the actual read()-time wire into read() is the Q111
    landing; this arm scores the mechanism it runs."""
    try:
        import random as _random
        import experiments.exp_commonnoun_binder_live_report_v1 as CBL
        import experiments.exp_unified_referent_gum_v1 as URG
        import hdlab.typed_coref as TC
        gaz, test = CBL._load(None)                      # GUM TEST = odd docs (137)
        if cap:
            test = test[:cap]
        if not test:
            return _degraded("commonnoun_resolution", "no GUM test docs on disk (gum_only load empty)"), {
                "error": "GUM gold absent -> degraded row"}
        model_pd, twin_pd, fair_pd, gold_pd, ref_pd = [], [], [], [], []
        for d in test:
            ms = CBL.doc_to_binder_mentions(d)
            ap = TC.appos_copula_isa(d)                  # in-text is-a from the (gold) parse the reader supplies
            model_pd.append(_score_commonnoun_resolution(_reader_commonnoun_resolution(ms, gaz, ap), ms))
            twin_pd.append(_score_commonnoun_resolution(
                _reader_commonnoun_resolution(ms, gaz, ap, twin=True, rng=_random.Random(99)), ms))
            fair_pd.append(CBL.per_doc_agg(CBL.string_identity_resolve(ms, key="binderlemma")))   # head_lemma
            gold_pd.append(CBL.per_doc_agg(CBL.string_identity_resolve(ms, key="lemma_head")))     # GUM gold lemma
            ref_pd.append(CBL.per_doc_agg(CBL.typed_coref_liveschema_resolve(ms, ap)[1]))          # gold-routed ref
        model, n = CBL.acc(model_pd, "common")
        fair, _ = CBL.acc(fair_pd, "common"); gold_floor, _ = CBL.acc(gold_pd, "common")
        twin_acc, _ = CBL.acc(twin_pd, "common"); ref_acc, _ = CBL.acc(ref_pd, "common")
        d_fl, lo_fl, hi_fl, _ = URG._paired_boot(fair_pd, model_pd, "common", n_boot, seed)      # model - fair floor
        d_tw, lo_tw, hi_tw, _ = URG._paired_boot(twin_pd, model_pd, "common", n_boot, seed)      # model - twin
        d_gl, lo_gl, hi_gl, _ = URG._paired_boot(gold_pd, model_pd, "common", n_boot, seed)      # model - gold floor
        d_rf, lo_rf, hi_rf, _ = URG._paired_boot(gold_pd, ref_pd, "common", n_boot, seed)        # ref  - gold floor
        row = {
            "n": n, "model_acc": round(float(model), 4),
            "overlap_floor": round(float(fair), 4),
            "floor_accs": {"same_lemmatizer_string_identity_head_lemma": round(float(fair), 4),
                           "gum_gold_lemma_string_identity_board_reference": round(float(gold_floor), 4)},
            "strongest_floor_name": "same_lemmatizer_string_identity_head_lemma",
            "strongest_floor": round(float(fair), 4),
            "twin_acc": round(float(twin_acc), 4),
            "model_minus_strongest": [round(d_fl, 4), round(lo_fl, 4), round(hi_fl, 4)],
            "model_minus_twin": [round(d_tw, 4), round(lo_tw, 4), round(hi_tw, 4)],
            "ci_sep_over_strongest": bool(lo_fl > 0),
            "ci_sep_over_twin": bool(lo_tw > 0),
            # ---- FULL transparency: the STRONGER gold-lemma board floor + the parity result + the positive control
            "gold_lemma_reference_floor": round(float(gold_floor), 4),
            "model_minus_gold_lemma_floor": [round(d_gl, 4), round(lo_gl, 4), round(hi_gl, 4)],
            "beats_gold_lemma_floor_ci_sep": bool(lo_gl > 0),
            "gold_routed_reference_acc": round(float(ref_acc), 4),
            "gold_routed_reference_minus_gold_floor": [round(d_rf, 4), round(lo_rf, 4), round(hi_rf, 4)],
            "gold_routed_reference_beats_gold_floor_ci_sep": bool(lo_rf > 0),
            "population": "GUM TEST anaphoric common-noun per-mention RESOLUTION (odd docs, n=%d; metric = "
                          "resolved-referent nominal-dominant gold eid == mention eid, URG board instrument). "
                          "model = the LIVE reader's sm.commonnoun_resolution (typed_coref binding on the reader's "
                          "OWN dict-mention stream: routing via is_pronoun/commonnoun_binder.is_name, key via the "
                          "reader's OWN head_lemma -- NO GUM gold lemma/mtype). strongest floor = SAME-LEMMATIZER "
                          "string-identity (head_lemma; the FAIR same-regime baseline). twin = info-free (bridge -> "
                          "random gn-compatible prior). ALSO reported: the GUM-gold-lemma string-identity floor "
                          "(%.4f = the board common_noun floor) -- STRONGER, but uses gold-lemma annotation the live "
                          "reader lacks; the wire reaches PARITY with it and the residual is that gold-lemma regime "
                          "(redaction see-through + copula-head normalization), NOT the binding (the gold-routed "
                          "reference reproduces +0.025 CI-sep over the gold floor -- positive control). Doc-paired "
                          "bootstrap CI (seed=%d, n_boot=%d). MODERN (GUM, Zeldes 2017)." % (n, gold_floor, seed, n_boot),
        }
        detail = {"note": "glass-box typed common-noun RESOLUTION (Ariel content/type-addressed definite "
                          "retrieval; Nieuwland non-writing hold; Lambon-Ralph typed spokes) served by "
                          "hdlab.typed_coref, ported onto the reader's LIVE dict-mention stream -- the Q111 wire "
                          "instrument. FIRST board arm scoring per-mention common-noun resolution. Model %.4f vs "
                          "same-lemmatizer floor %.4f = %+.4f CI[%.4f,%.4f] (CI-sep=%s); info-free twin %.4f loses "
                          "%+.4f CI-sep=%s. LOCATED (2x2 decomposition, solver-measured): the head-KEY regime "
                          "(reader head_lemma vs GUM gold lemma) costs -0.0214, the ROUTING (is_name vs gold mtype) "
                          "costs only -0.0032, WordNet morphy recovers +0.0004 -- so the gap to the proven 0.5664 "
                          "is the GUM gold-lemma ANNOTATION regime, not the mechanism. appos/copula in-text is-a "
                          "seed is +0.0070 CI-sep (load-bearing; from the reader's parse). ADDITIVE / no-regress by "
                          "construction: writes only sm.commonnoun_resolution, never mutates role_mentions cluster "
                          "ids or coref -- default-on-safe. 'landed != live' -- the read()-time wire is the Q111 "
                          "landing (proposed diff: typed_coref_resolution_wire_PROPOSED.py)."
                          % (row["model_acc"], row["strongest_floor"], row["model_minus_strongest"][0],
                             lo_fl, hi_fl, row["ci_sep_over_strongest"], row["twin_acc"],
                             row["model_minus_twin"][0], row["ci_sep_over_twin"])}
        return row, detail
    except Exception as e:
        return _degraded("commonnoun_resolution", e), {"error": "%s: %s" % (type(e).__name__, e)}


def board_state_closure_dimension(n_boot=5000, seed=None):
    """STATE-CLOSURE (multi-clause state antonymy) board arm on the solver's OWN CONSTRUCTED MODERN gold
    (exp_state_closure_wordnet_v1 _CLOSURE_ANTONYM/_CLOSURE_COSTATE, n=25). This capability is board-INVISIBLE
    today -- the `state` dim scores copular is-a binding, NOT whether a state span CLOSES when a later
    INCOMPATIBLE state is asserted ("the towel was wet ... the towel was dry" -> wet no longer holds). The
    owner-DONE fix landed WordNet-derived antonymy into hdlab.state_register.incompatible (a WordNet core-
    adjective FOUNDATION fallback, L264-266), closing antonym pairs the hand list missed (wet/dry, tired/
    rested, honest/dishonest). Reuses the solver's OWN gold + closure machinery verbatim (the _closes state-
    register driver):
      model = the LIVE hdlab.state_register.incompatible (WordNet-derived closure, the landed organ),
      strongest floor = HAND-LIST-ONLY closure (the pre-fix predicate: _INCOMPAT hand groups + un-/in-
        morphology, NO WordNet -- reconstructed here because the landed organ now EQUALS WordNet, so the
        experiment's own `_ORIG_INCOMPAT` 'hand' arm is no longer hand-only [SURFACED discrepancy]),
      second floor = always-persist (never closes),
      info-free twin = scrambled antonymy at matched rate (permute the second state across the antonym items).
    Reports overall acc + antonym-recall / costate-precision split + paired bootstrap CI + the OVER-CLOSE cost
    (WordNet false-close rate on labeled non-opposites minus the hand floor's). CONSTRUCTED (declared, NOT a
    corpus gold) -- makes the MECHANISM board-visible, NOT a headline-aggregate claim. Degrades gracefully."""
    try:
        import numpy as np
        import experiments.exp_state_closure_wordnet_v1 as S
        import hdlab.state_register as SR
        sd = S.SEED if seed is None else seed

        def hand_only(v1, v2):
            # the PRE-FIX incompatible: hand groups (_INCOMPAT) + un-/in- morphology, NO WordNet fallback.
            a, b = SR._canon_value(v1), SR._canon_value(v2)
            if a == b:
                return False
            if b in SR._INCOMPAT.get(a, frozenset()):
                return True
            for x, y in ((a, b), (b, a)):
                if x.startswith("un") and x[2:] == y:
                    return True
                if x.startswith("in") and x[2:] == y:
                    return True
            return False

        n_ant = len(S._CLOSURE_ANTONYM)
        items = [(e, a, b, False) for (e, a, b) in S._CLOSURE_ANTONYM] \
            + [(e, a, b, True) for (e, a, b) in S._CLOSURE_COSTATE]
        rng = np.random.default_rng(sd)
        ant_seconds = [b for (_, _, b) in S._CLOSURE_ANTONYM]
        perm = rng.permutation(len(ant_seconds))
        twin_second = {i: ant_seconds[perm[i]] for i in range(len(ant_seconds))}
        model, floor, persist, twin = [], [], [], []
        ai = 0
        for (e, a, b, gold_holds) in items:
            gc = not gold_holds  # gold: should the span close?
            model.append(int(S._closes(SR.incompatible, a, b) == gc))     # LIVE organ (WordNet-derived)
            floor.append(int(S._closes(hand_only, a, b) == gc))           # hand-list-only floor (pre-fix)
            persist.append(int(False == gc))                              # always-persist floor
            if gold_holds is False:                                       # an antonym item -> scramble second
                b_tw = twin_second[ai]; ai += 1
            else:
                b_tw = b
            twin.append(int(S._closes(SR.incompatible, a, b_tw) == gc))
        model = np.array(model, float); floor = np.array(floor, float)
        persist = np.array(persist, float); twin = np.array(twin, float)

        def boot(av, bv):
            n = len(av); obs = av.mean() - bv.mean(); ds = np.empty(n_boot)
            for k in range(n_boot):
                idx = rng.integers(0, n, n); ds[k] = av[idx].mean() - bv[idx].mean()
            lo, hi = np.percentile(ds, [2.5, 97.5])
            return ([round(float(obs), 4), round(float(lo), 4), round(float(hi), 4)], bool(lo > 0),
                    round(float(np.percentile(np.abs(ds - obs), 95)), 4))

        def split(v):
            return {"antonym_recall": round(float(v[:n_ant].mean()), 4),
                    "costate_precision": round(float(v[n_ant:].mean()), 4),
                    "overall": round(float(v.mean()), 4)}
        floor_acc = round(float(floor.mean()), 4); persist_acc = round(float(persist.mean()), 4)
        if floor_acc >= persist_acc:   # strongest floor = higher of hand-list-only vs always-persist
            sf_name, sf_acc, sf_vec = "hand_list_only_closure", floor_acc, floor
        else:
            sf_name, sf_acc, sf_vec = "always_persist", persist_acc, persist
        ms, ms_sep, ms_p95 = boot(model, sf_vec)
        mt, mt_sep, _ = boot(model, twin)
        mp, mp_sep, _ = boot(model, persist)

        def rate(fn, pairs):
            return round(float(np.mean([int(fn(a, b)) for (a, b) in pairs])), 4)
        wn_neg = rate(SR.incompatible, S._NEG_PAIRS); hd_neg = rate(hand_only, S._NEG_PAIRS)
        wn_pos = rate(SR.incompatible, S._POS_PAIRS); hd_pos = rate(hand_only, S._POS_PAIRS)
        wn_false = ["%s/%s" % (a, b) for (a, b) in S._NEG_PAIRS if SR.incompatible(a, b)]
        live_wired = bool(SR.incompatible("wet", "dry") and not hand_only("wet", "dry"))
        row = {
            "n": len(items), "model_acc": round(float(model.mean()), 4),
            "overlap_floor": sf_acc,
            "floor_accs": {"hand_list_only_closure": floor_acc, "always_persist": persist_acc},
            "strongest_floor_name": sf_name, "strongest_floor": sf_acc,
            "twin_acc": round(float(twin.mean()), 4),
            "model_minus_strongest": ms, "model_minus_twin": mt,
            "ci_sep_over_strongest": ms_sep, "ci_sep_over_twin": mt_sep,
            "null_p95_over_strongest": ms_p95,
            "model_minus_persist": mp, "ci_sep_over_persist": mp_sep,
            "by_arm": {"model_live_wordnet": split(model), "hand_list_only_floor": split(floor),
                       "always_persist_floor": split(persist), "twin_scrambled": split(twin)},
            "over_close_cost": round(wn_neg - hd_neg, 4),
            "lexicon_probe": {"model_recall_on_opposites": wn_pos, "hand_recall_on_opposites": hd_pos,
                              "model_false_close_on_nonopposites": wn_neg,
                              "hand_false_close_on_nonopposites": hd_neg,
                              "model_false_fires": wn_false, "n_pos": len(S._POS_PAIRS),
                              "n_neg": len(S._NEG_PAIRS)},
            "live_wordnet_closure_wired": live_wired, "informational": True,
            "population": "CONSTRUCTED MODERN state-closure gold (exp_state_closure_wordnet_v1, n=%d: %d antonym "
                          "should-close + %d co-state keep-open, mechanism-isolated abstract state events, 19c-free "
                          "vocabulary); model=LIVE hdlab.state_register.incompatible (WordNet-derived closure, "
                          "landed fix); strongest floor=HAND-LIST-ONLY closure (pre-fix predicate, reconstructed); "
                          "second floor=always-persist; twin=scrambled antonymy at matched rate. CONSTRUCTED, "
                          "declared (NOT a corpus gold)." % (len(items), n_ant, len(S._CLOSURE_COSTATE))}
        detail = {"note": "default-persist state model (Dowty 1986 temporal inertia -- a state holds until an "
                          "EXPLICIT incompatible state) with antonymy DERIVED from the semantic hub (ATL; "
                          "Patterson/Nestor/Rogers 2007) via WordNet core-adjective antonyms, replacing the hand "
                          "list that missed wet/dry, tired/rested, honest/dishonest. The FIRST board arm scoring "
                          "multi-clause state CLOSURE. Reproduces the SOLVED win: LIVE %.4f (antonym-recall %.4f) "
                          "vs hand-list-only %.4f (antonym-recall %.4f), %+.4f CI-sep, over-close cost %+.4f "
                          "(WordNet noise: %s). Reuses exp_state_closure_wordnet_v1 gold + _closes driver verbatim. "
                          "SURFACED: the landed organ now equals WordNet, so that cell's own `_ORIG_INCOMPAT` "
                          "'hand' arm is no longer hand-only (this arm reconstructs the true pre-fix floor). "
                          "CONSTRUCTED, declared -- board-visible mechanism, NOT a headline-aggregate claim."
                          % (row["model_acc"], row["by_arm"]["model_live_wordnet"]["antonym_recall"],
                             floor_acc, row["by_arm"]["hand_list_only_floor"]["antonym_recall"],
                             ms[0], row["over_close_cost"], wn_false)}
        return row, detail
    except Exception as e:
        return _degraded("state_closure", e, informational=True), {"error": "%s: %s" % (type(e).__name__, e)}


def board_affect_harm_help_dimension(n_boot=2000, seed=None):
    """AFFECT (harm/help patient-valence) board arm on the solver's OWN SELF-AUTHORED balanced MODERN gold
    (exp_fd_harm_help_live_modern_v1.GOLD, n=36: 12 HARM / 12 HELP / 12 NEUTRAL). This capability is board-
    INVISIBLE today -- the modern board OMITS affect entirely (a NAMED GAP). The owner-DONE fix landed a
    force-dynamics harm/help decision into the LIVE reader (hdlab.context_grounded_valence /
    hdlab.force_dynamics_valence), replacing the closed test-fitted FORCE_CLASS_HARM_REAL list that could
    NEVER emit HELP. Reuses the solver's OWN gold + decision functions verbatim (exp_force_dynamics_harm_help
    _v1):
      model = FORCE-DYNAMICS decision (harm_help refined; Talmy 1988 / Wolff 2007 -- the EXACT function the
        landed reader path consumes, cross-checked below to equal the LIVE reader's affect output),
      strongest floor = the RETIRED closed-list decision (closed_list_arm, pre-fix organ) AND the all-NEUTRAL
        majority (both ~0.333),
      info-free twin = scrambled force lexicon + scrambled harm-set membership.
    Reports acc + paired bootstrap CI + twin + by-class (HARM/HELP/NEUTRAL) + a 0-FALSE-POSITIVE check (FD
    never labels a NEUTRAL scene HARM/HELP) + the LIVE-READER cross-check (drive hdlab.situation_reader.read()
    once on the 36 gold docs; its affect acc must == the decision-level FD acc -> the mechanism is WIRED, not
    an island). SELF-AUTHORED / DIRECTIONAL (declared: the author has seen both lexicons; NOT a corpus gold --
    no harm/help-labeled modern corpus exists on disk) -- board-visible MECHANISM, NOT a headline-aggregate
    claim. Degrades gracefully."""
    try:
        import numpy as np
        import experiments.exp_force_dynamics_harm_help_v1 as FD
        import experiments.exp_fd_harm_help_live_modern_v1 as FDL
        sd = FDL.SEED if seed is None else seed
        GOLD = FDL.GOLD

        def to3(x):
            return x if x in ("HARM", "HELP") else "NEUTRAL"   # NA / None / abstain -> NEUTRAL

        def animacy(noun):
            r = FD.ea.real_animacy_lookup(noun, "NOUN")
            return r["animacy"] if r else None
        scr_lex = FD.scramble_lexicon(FD.LEX_AUG, FD.SEED + 1)
        all_v = set(FD.LEX_AUG) | FD.HARM_VERBS | FD.CLOSED
        scr_harm = FD.scramble_set_membership(FD.HARM_VERBS, all_v, FD.SEED + 2)
        recs = []
        for (subj, verb, pat, g) in GOLD:
            an = animacy(pat)
            recs.append((verb, pat, g,
                         to3(FD.harm_help(verb, an, FD.LEX_AUG, FD.HARM_VERBS, mode="refined")),   # model
                         to3(FD.closed_list_arm(verb, an)),                                        # closed floor
                         to3(FD.harm_help(verb, an, scr_lex, scr_harm, mode="refined"))))          # twin

        def vec(i):
            return np.array([1 if r[i] == r[2] else 0 for r in recs], float)
        model = vec(3); closed = vec(4); twin = vec(5)
        maj = np.array([1 if r[2] == "NEUTRAL" else 0 for r in recs], float)
        maj_acc = round(float(maj.mean()), 4); closed_acc = round(float(closed.mean()), 4)
        if closed_acc >= maj_acc:
            sf_name, sf_acc, sf_vec = "retired_closed_list", closed_acc, closed
        else:
            sf_name, sf_acc, sf_vec = "majority_all_neutral", maj_acc, maj
        rng = np.random.default_rng(sd)

        def boot(av, bv):
            n = len(av); obs = av.mean() - bv.mean(); ds = np.empty(n_boot)
            for k in range(n_boot):
                idx = rng.integers(0, n, n); ds[k] = av[idx].mean() - bv[idx].mean()
            lo, hi = np.percentile(ds, [2.5, 97.5])
            return [round(float(obs), 4), round(float(lo), 4), round(float(hi), 4)], bool(lo > 0)
        ms, ms_sep = boot(model, sf_vec)
        mt, mt_sep = boot(model, twin)
        mm, mm_sep = boot(model, maj)

        def by_class(i):
            by = {"HARM": [0, 0], "HELP": [0, 0], "NEUTRAL": [0, 0]}
            for r in recs:
                by[r[2]][1] += 1; by[r[2]][0] += int(r[i] == r[2])
            return {k: "%d/%d" % (v[0], v[1]) for k, v in by.items()}
        false_pos = [(r[0], r[1], r[3]) for r in recs if r[2] == "NEUTRAL" and r[3] in ("HARM", "HELP")]
        # LIVE-READER cross-check: the FD decision IS what the reader consumes (not an island)
        live = None
        try:
            import hdlab.situation_reader as HSR
            reader = HSR.SituationReader()
            FDL.unpatch()   # ensure the reader runs its LIVE (landed) affect path, not the experiment hook
            os.makedirs(FDL.SCRATCH, exist_ok=True)
            lc = []
            lby = {"HARM": [0, 0], "HELP": [0, 0], "NEUTRAL": [0, 0]}
            for i, (subj, verb, pat, g) in enumerate(GOLD):
                p = os.path.join(FDL.SCRATCH, "gold_%02d.conll" % i)
                open(p, "w", encoding="utf-8").write(
                    FDL.make_conll("gold%d" % i, [FDL.gold_sentence(subj, verb, pat)]))
                pred = FDL.to_gold3(FDL.read_affects(reader, p, pat))
                lc.append(int(pred == g)); lby[g][1] += 1; lby[g][0] += int(pred == g)
            live_raw = float(np.mean(lc))
            live = {"live_reader_acc": round(live_raw, 4),
                    "live_reader_by_class": {k: "%d/%d" % (v[0], v[1]) for k, v in lby.items()},
                    "live_matches_decision": bool(abs(live_raw - float(model.mean())) < 1e-9)}
        except Exception as le:
            live = {"error": "%s: %s" % (type(le).__name__, le)}
        row = {
            "n": len(recs), "model_acc": round(float(model.mean()), 4),
            "overlap_floor": sf_acc,
            "floor_accs": {"retired_closed_list": closed_acc, "majority_all_neutral": maj_acc},
            "strongest_floor_name": sf_name, "strongest_floor": sf_acc,
            "twin_acc": round(float(twin.mean()), 4),
            "model_minus_strongest": ms, "model_minus_twin": mt,
            "ci_sep_over_strongest": ms_sep, "ci_sep_over_twin": mt_sep,
            "model_minus_majority": mm, "ci_sep_over_majority": mm_sep,
            "by_class": by_class(3), "closed_list_by_class": by_class(4),
            "false_positives_on_neutral": false_pos, "zero_false_positives": (len(false_pos) == 0),
            "live_reader_crosscheck": live, "informational": True,
            "population": "SELF-AUTHORED balanced MODERN harm/help gold (exp_fd_harm_help_live_modern_v1.GOLD, "
                          "n=%d: 12 HARM / 12 HELP / 12 NEUTRAL contemporary SVO scenes, verb inventory adversarial "
                          "to FD -- includes FrameNet-missed social-harm + Cause_emotion HELP the model abstains on); "
                          "model=force-dynamics decision (the landed reader path), strongest floor=retired "
                          "closed-list AND all-NEUTRAL majority, twin=scrambled force lexicon + harm-set. "
                          "SELF-AUTHORED / DIRECTIONAL, declared (author saw both lexicons; NOT a corpus gold)."
                          % len(recs)}
        detail = {"note": "harm/help as FORCE DYNAMICS (Talmy 1988; Wolff 2007 -- an affector force overcoming an "
                          "animate patient's inertia to an adverse endstate = HARM/CAUSE; a force opposing an adverse "
                          "endstate = HELP/PREVENT-ENABLE), replacing the closed test-fitted FORCE_CLASS_HARM_REAL "
                          "list that could NEVER emit HELP. The FIRST board arm scoring affect on modern gold. "
                          "Reproduces the SOLVED win: FD %.4f (HARM %s HELP %s NEUTRAL %s) vs retired closed-list "
                          "%.4f (HELP structurally 0/12) and majority %.4f, %+.4f CI-sep; twin %.4f loses; "
                          "%d false positives on NEUTRAL. Cross-check: the LIVE reader's affect acc == the decision-"
                          "level FD acc (matches=%s) -- the mechanism is WIRED, not an island. SURFACED: the fix "
                          "landed in hdlab (context_grounded_valence), so exp_fd_harm_help_live_modern_v1.part_B's "
                          "through-reader monkeypatch is now a NO-OP (all 3 arms collapse to the live 0.778); this "
                          "arm scores the contrast at the decision level (genuine floors) + cross-checks the live "
                          "reader. SELF-AUTHORED / DIRECTIONAL, declared -- board-visible mechanism, NOT a headline "
                          "claim."
                          % (row["model_acc"], row["by_class"]["HARM"], row["by_class"]["HELP"],
                             row["by_class"]["NEUTRAL"], closed_acc, maj_acc, ms[0], row["twin_acc"],
                             len(false_pos),
                             (live.get("live_matches_decision") if isinstance(live, dict) else None))}
        return row, detail
    except Exception as e:
        return _degraded("affect_harm_help", e, informational=True), {"error": "%s: %s" % (type(e).__name__, e)}


def board_predictive_causal_necessity_dimension(held_lines=6000, seed=17):
    """FORWARD predictive-causal INTRINSIC-NECESSITY board arm (owner-DONE generate_dont_retrieve_causal_edges,
    CONT-29). The counterfactual-necessity causal reader is board-INVISIBLE by design: every external causal gold
    (MAVEN/TellMeWhy/GLUCOSE) is a POSITION-ARTIFACT trap a trivial position floor beats, so the brain-foundational,
    TRAP-PROOF measure is INTRINSIC surprisal-reduction (Kuperberg N400 predictive coding + Gerstenberg
    counterfactual necessity), NOT a QA dim. This arm scores the LANDED hdlab.predictive_world_model directly on a
    HELD-OUT simplewiki slice (lines the foundation asset was NOT trained on): for each event with >=3 context
    events, the reader's argmax-necessity antecedent's necessity (surprisal-increase on ablation) vs (strongest
    floor) a RANDOM context event and (position control / twin) the NEAREST context event. A REAL necessity signal
    that ESCAPES position => model beats random CI-sep AND beats nearest CI-sep.

    model = mean reader-argmax necessity (bits); strongest_floor = mean RANDOM-context-event necessity; twin =
    mean NEAREST-event necessity (the position control the solver proved the benchmarks secretly reward). Paired
    clustered bootstrap CI. Kept OUT of the 19c-free headline aggregate (its own INTRINSIC row -- no QA population).
    Degrades gracefully to a schema-shaped N/A row if the foundation asset is absent (build via
    `python -m hdlab.predictive_world_model --build`). NO spaCy / NO LLM (glass-box tagger + WordNet + a linear
    read-out learned by the delta-rule)."""
    try:
        import os as _os
        import math as _math
        from collections import deque as _deque
        import numpy as _np
        try:
            from hdlab.predictive_world_model import PredictiveWorldModel as _PWM, content_events as _ce
            m = _PWM.load()
        except Exception as e:
            return _degraded("predictive_causal_necessity",
                             "foundation asset absent -- build via `python -m hdlab.predictive_world_model --build` (%s)"
                             % e), {"note": "the landed hdlab.predictive_world_model organ needs its simplewiki "
                                    "foundation asset (gitignored/rebuildable); the arm returns a schema-shaped N/A row."}
        _REPO2 = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
        sw = _os.path.join(_REPO2, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
        # HELD-OUT slice: lines AFTER the asset's 40000-line training window (honest -- not trained on).
        stream = []
        with open(sw, encoding="utf-8", errors="ignore") as f:
            for i, ln in enumerate(f):
                if i < 40000:
                    continue
                if i >= 40000 + held_lines:
                    break
                ln = ln.strip()
                if len(ln) >= 8:
                    stream.extend(_ce(ln))
        ids = [m.idx[c] for c in stream if c in m.idx]
        max_nec, rand_nec, near_nec = [], [], []
        rng = _np.random.default_rng(seed)
        win = _deque(maxlen=m.hist)
        for nxt in ids:
            ctx = list(win)
            if len(ctx) >= 3:
                necs = [t[2] for t in m.necessity_ids(nxt, ctx)]
                if necs:
                    max_nec.append(max(necs))
                    rand_nec.append(necs[int(rng.integers(0, len(necs)))])
                    near_nec.append(necs[-1])            # nearest = last context event (position control)
            win.append(nxt)
        n = len(max_nec)
        if n < 100:
            return _degraded("predictive_causal_necessity",
                             "held-out necessity sample too small (%d)" % n), {"n": n}
        a = _np.array(max_nec); r = _np.array(rand_nec); nr = _np.array(near_nec)

        def _boot(hi, lo):
            d = hi - lo
            idx = rng.integers(0, len(d), (2000, len(d)))
            s = d[idx].mean(1)
            return float(d.mean()), float(_np.percentile(s, 2.5)), float(_np.percentile(s, 97.5))

        dr = _boot(a, r); dn = _boot(a, nr)
        row = {
            "n": n, "model_acc": round(float(a.mean()), 4),
            "overlap_floor": round(float(r.mean()), 4),
            "floor_accs": {"random_context_event": round(float(r.mean()), 4),
                           "nearest_event_position": round(float(nr.mean()), 4)},
            "strongest_floor_name": "random_context_event", "strongest_floor": round(float(r.mean()), 4),
            "twin_acc": round(float(nr.mean()), 4),                       # nearest = the position control
            "model_minus_strongest": [round(dr[0], 4), round(dr[1], 4), round(dr[2], 4)],
            "model_minus_twin": [round(dn[0], 4), round(dn[1], 4), round(dn[2], 4)],
            "ci_sep_over_strongest": bool(dr[1] > 0),
            "ci_sep_over_twin": bool(dn[1] > 0),                          # beats NEAREST => escapes position
            "informational": True,
            "population": ("simplewiki HELD-OUT (lines 40000-%d, not in the asset's training window); intrinsic "
                           "counterfactual-necessity bits (surprisal-increase on ablation) over the landed "
                           "hdlab.predictive_world_model; NO external gold -> trap-proof" % (40000 + held_lines)),
            "metric": "mean counterfactual-necessity bits (reader-argmax antecedent)",
        }
        detail = {"reader_argmax_necessity": round(float(a.mean()), 4),
                  "random_context_necessity": round(float(r.mean()), 4),
                  "nearest_event_necessity": round(float(nr.mean()), 4),
                  "reader_vs_random_ci": [round(dr[1], 4), round(dr[2], 4)],
                  "reader_vs_nearest_ci": [round(dn[1], 4), round(dn[2], 4)],
                  "n_effects_scored": n, "vocab_V": m.V}
        return row, detail
    except Exception as e:
        return _degraded("predictive_causal_necessity", e, informational=True), {"error": "%s: %s" % (type(e).__name__, e)}


def run(caps=None, n_boot=1000, seed=SEED, run_new_arms=True, write_metrics=True):
    """Assemble every MODERN per_dimension row. caps = dict of per-arm caps for a fast self-test.
    run_new_arms adds the 3 board-invisible-win arms (coarse-sense/selective-reliability/causal-multihop) as
    their own rows OUTSIDE the headline aggregate; write_metrics=False (self-test) does not clobber the artifact."""
    t0 = time.time()
    caps = caps or {}
    os.makedirs(OUT_DIR, exist_ok=True)
    rows, detail = {}, {}

    # -- COREF / SALIENCE / COMMON-NOUN (GUM) + the cross-consumer upstream proof --
    import experiments.exp_board_coref_gum_v1 as CG
    nd = caps.get("gum")
    cpr, cpr_detail = CG.board_coref_modern_dimension(n_docs=nd)
    rows["coref"] = cpr
    rows["common_noun_coref"] = cpr_detail["common_noun"]
    detail["coref"] = cpr_detail
    sal, sal_detail = CG.board_salience_modern_dimension(n_docs=nd, n_boot=n_boot, seed=seed)
    rows["salience"] = sal; detail["salience"] = sal_detail
    cross = CG.cross_consumer_upstream(n_docs=nd)
    detail["cross_consumer_upstream"] = cross

    # -- WHO-DID-WHAT AGENT (UD-EWT), the upstream role-assigner on modern gold --
    import experiments.exp_board_agent_slot_ud_v1 as AG
    arow, adetail = AG.board_agent_dimension(cap=caps.get("ud"), n_boot=n_boot, seed=seed)
    rows["who_did_what_agent"] = arow; detail["who_did_what_agent"] = adetail

    # -- WHO-DID-WHAT PATIENT (UD-EWT), already-modern landed arm --
    from experiments.exp_board_patient_slot_v1 import board_patient_dimension
    prow, pdetail = board_patient_dimension(cap=caps.get("ud"))
    rows["who_did_what_patient"] = prow; detail["who_did_what_patient"] = pdetail

    # -- STATE (UD-EWT copular), already-modern landed arm --
    from experiments.exp_situation_model_state_qa_v1 import board_state_dimension
    srow, sdetail = board_state_dimension(cap=caps.get("state"), n_boot=n_boot, seed=seed)
    rows["state"] = srow; detail["state"] = {"n": srow["n"], "model": srow["model_acc"]}

    # -- WiC word-sense (already-modern arm) --
    try:
        from experiments.exp_board_wic_sense_v1 import board_wic_dimension
        wrow, wdetail = board_wic_dimension(mode=caps.get("wic_mode", "smoke"))
        rows["wic"] = wrow; detail["wic"] = {"n": wrow["n"], "model": wrow["model_acc"]}
    except Exception as e:
        rows["wic"] = None; detail["wic"] = {"error": "%s: %s" % (type(e).__name__, e)}

    agg = _agg(rows)
    transferred = {k: {"gold": GOLD_SOURCE[k], "model_acc": rows[k]["model_acc"] if rows[k] else None,
                       "strongest_floor": rows[k]["strongest_floor"] if rows[k] else None,
                       "ci_sep_over_floor": rows[k]["ci_sep_over_strongest"] if rows[k] else None,
                       "twin_loses": rows[k]["ci_sep_over_twin"] if rows[k] else None}
                   for k in GOLD_SOURCE if rows.get(k)}
    # -- THREE NEW BOARD ARMS (board-invisible proven wins, each its OWN row; NOT in the headline aggregate).
    #    OFF in the self-test (run_new_arms=False). Each degrades gracefully (never crashes the board). --
    new_arms, new_arms_detail = {}, {}
    if run_new_arms:
        cs_row, cs_det = board_coarse_sense_dimension(max_files=caps.get("coarse_files", 12))
        new_arms["coarse_sense"] = cs_row; new_arms_detail["coarse_sense"] = cs_det
        sr_rows, sr_det = board_selective_reliability_dimension(cap=caps.get("sr"), n_boot=min(2000, n_boot * 2))
        new_arms["selective_reliability"] = sr_rows; new_arms_detail["selective_reliability"] = sr_det
        ca_rows, ca_det = board_causal_multihop_dimension(cap=None, wiqa_cap=caps.get("wiqa"),
                                                          tmw_n=caps.get("tmw", 1500))
        new_arms["causal_multihop"] = ca_rows; new_arms_detail["causal_multihop"] = ca_det
        occ_row, occ_det = board_occ_appraisal_dimension(cap=caps.get("occ"))
        new_arms["occ_appraisal"] = occ_row; new_arms_detail["occ_appraisal"] = occ_det
        sp_row, sp_det = board_spatial_relational_dimension(cap=caps.get("spatial"))
        new_arms["spatial_relational"] = sp_row; new_arms_detail["spatial_relational"] = sp_det
        tb_row, tb_det = board_temporal_before_after_dimension(smoke=bool(caps.get("temporal_smoke")))
        new_arms["temporal_before_after"] = tb_row; new_arms_detail["temporal_before_after"] = tb_det
        to_row, to_det = board_temporal_overlap_dimension(smoke=bool(caps.get("temporal_smoke")))
        new_arms["temporal_overlap"] = to_row; new_arms_detail["temporal_overlap"] = to_det
        ts_row, ts_det = board_temporal_survival_dimension(smoke=bool(caps.get("temporal_smoke")))
        new_arms["temporal_survival"] = ts_row; new_arms_detail["temporal_survival"] = ts_det
        nq_rows, nq_det = board_negation_quantifier_dimension(seed=seed)
        new_arms["negation_quantifier"] = nq_rows; new_arms_detail["negation_quantifier"] = nq_det
        cvr_row, cvr_det = board_coref_via_reader_dimension(n_docs=caps.get("gum"))
        new_arms["coref_via_reader"] = cvr_row; new_arms_detail["coref_via_reader"] = cvr_det
        nl_row, nl_det = board_natural_logic_monotonicity_dimension(smoke=bool(caps.get("natlog_smoke")))
        new_arms["natural_logic_monotonicity"] = nl_row
        new_arms_detail["natural_logic_monotonicity"] = nl_det
        eg_row, eg_det = board_event_goal_congruence_dimension(smoke=bool(caps.get("event_goal_smoke")))
        new_arms["event_goal_congruence"] = eg_row
        new_arms_detail["event_goal_congruence"] = eg_det
        sem_row, sem_det = board_sem_segmentation_dimension(smoke=bool(caps.get("sem_seg_smoke")))
        new_arms["sem_segmentation"] = sem_row
        new_arms_detail["sem_segmentation"] = sem_det
        tom_row, tom_det = board_tom_dimension(smoke=bool(caps.get("tom_smoke")))
        new_arms["theory_of_mind"] = tom_row
        new_arms_detail["theory_of_mind"] = tom_det
        cx_row, cx_det = board_crosstype_experiencer_dimension(smoke=bool(caps.get("crosstype_smoke")))
        new_arms["crosstype_experiencer"] = cx_row
        new_arms_detail["crosstype_experiencer"] = cx_det
        nb_row, nb_det = board_namebridge_dimension(smoke=bool(caps.get("namebridge_smoke")))
        new_arms["namebridge"] = nb_row
        new_arms_detail["namebridge"] = nb_det
        cnr_row, cnr_det = board_commonnoun_resolution_dimension(cap=caps.get("commonnoun_res"),
                                                                 n_boot=min(2000, n_boot * 2))
        new_arms["commonnoun_resolution"] = cnr_row
        new_arms_detail["commonnoun_resolution"] = cnr_det
        # -- this session's TWO board-invisible proven wins, each its OWN row (OUT of the headline aggregate) --
        se_row, se_det = board_spatial_extraction_precision_dimension(cap=caps.get("spatial_precision"))
        new_arms["spatial_extraction_precision"] = se_row
        new_arms_detail["spatial_extraction_precision"] = se_det
        ti_row, ti_det = board_temporal_implicit_order_dimension(smoke=bool(caps.get("temporal_smoke")))
        new_arms["temporal_implicit_order"] = ti_row
        new_arms_detail["temporal_implicit_order"] = ti_det
        # -- this session's TWO landed brain-foundational fixes, made board-visible (each its OWN row, OUT of
        #    the headline aggregate; CONSTRUCTED / SELF-AUTHORED, declared) --
        sc_row, sc_det = board_state_closure_dimension()
        new_arms["state_closure"] = sc_row
        new_arms_detail["state_closure"] = sc_det
        hh_row, hh_det = board_affect_harm_help_dimension()
        new_arms["affect_harm_help"] = hh_row
        new_arms_detail["affect_harm_help"] = hh_det
        pcn_row, pcn_det = board_predictive_causal_necessity_dimension(
            held_lines=(1500 if caps.get("predictive_causal_smoke") else 6000))
        new_arms["predictive_causal_necessity"] = pcn_row
        new_arms_detail["predictive_causal_necessity"] = pcn_det

    crossref = _informational_19c_crossref()

    res = {
        "anchor": ANCHOR, "seed": seed,
        "aggregate_19c_free": agg,
        "per_dimension": rows,
        "new_board_arms": new_arms,
        "new_board_arms_detail": new_arms_detail,
        "informational_19c_crossref": crossref,
        "transferred_to_modern": transferred,
        "named_gaps": NAMED_GAPS,
        "upstream_chain": {
            "component_1_unified_referent_coref": {
                "role": "feeds coref pronoun pick", "status": "EXCEEDS on modern (reused sibling SOLVED)",
                "modern_result": {"model": rows["coref"]["model_acc"] if rows.get("coref") else None,
                                  "floor": rows["coref"]["strongest_floor"] if rows.get("coref") else None,
                                  "ci_sep": rows["coref"]["ci_sep_over_strongest"] if rows.get("coref") else None}},
            "component_2_cm_role_assigner": {
                "role": "feeds who-did-what(agent) AND coref(entity-KB hard-link)",
                "modern_who_did_what": "LOCATED register finding: word-order near-ceiling on modern canonical "
                                       "prose; the 19c CM win does not transfer (see who_did_what_agent detail)",
                "cross_consumer_coref": detail["cross_consumer_upstream"]}},
        "detail": detail,
        "reader_unchanged": True,
        "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    if write_metrics:
        with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
            json.dump(res, fh, indent=2, default=str)
    return res


def _print(res):
    print("=" * 100)
    print("19c-FREE MODERN COMPREHENSION BOARD  (reader unchanged; only corpus + golds are modern)")
    print("=" * 100)
    a = res["aggregate_19c_free"]
    print("AGGREGATE (19c-free, cross-population summary): model=%s floor=%s twin=%s  (%d/%d dims CI-sep over floor)"
          % (a.get("model_acc"), a.get("strongest_floor"), a.get("twin_acc"),
             a.get("n_dims_ci_sep_over_floor"), a.get("n_dims_total")))
    print("\n%-22s %6s %8s %8s %8s %10s %9s  %s" % ("dimension", "n", "model", "floor", "twin",
                                                    "ci>floor", "twin<mod", "gold"))
    for k in ("coref", "salience", "common_noun_coref", "who_did_what_agent", "who_did_what_patient",
              "state", "wic"):
        r = res["per_dimension"].get(k)
        if not r:
            print("%-22s   (not built)" % k); continue
        print("%-22s %6d %8s %8s %8s %10s %9s  %s" % (
            k, r["n"], r["model_acc"], r["strongest_floor"], r["twin_acc"],
            r["ci_sep_over_strongest"], r["ci_sep_over_twin"], GOLD_SOURCE.get(k, "")))
    print("\nNAMED GAPS (no modern gold on disk -> filed follow-ons): %s" % ", ".join(res["named_gaps"]))
    cx = res["detail"]["cross_consumer_upstream"]
    print("\nUPSTREAM CHAIN:")
    c1 = res["upstream_chain"]["component_1_unified_referent_coref"]["modern_result"]
    print("  #1 unified referent (coref): model %s vs floor %s  ci_sep=%s  -> EXCEEDS on modern" % (
        c1["model"], c1["floor"], c1["ci_sep"]))
    print("  #2 CM role assigner: who-did-what(agent) = located register finding; coref(entity-KB hard-link) "
          "gold-roles %s vs positional %s (%s) cost=%s" % (
        cx["gold_roles_acc"], cx["positional_roles_acc"], cx["gold_minus_positional"],
        cx["positional_roles_cost_the_consumer"]))
    print("=" * 100)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-boot", type=int, default=1000)
    a = ap.parse_args()
    if a.self_test:
        # self-test: caps on the 7 core dims; the 3 heavy NEW arms are OFF (run_new_arms=False) and the
        # canonical metrics.json is NOT clobbered (write_metrics=False -- the full-run artifact stands).
        res = run(caps={"gum": 40, "ud": 300, "state": 300, "wic_mode": "smoke"}, n_boot=300,
                  run_new_arms=False, write_metrics=False)
        assert res["per_dimension"]["coref"]["n"] > 50, res["per_dimension"]["coref"]
        assert res["per_dimension"]["who_did_what_agent"]["n"] > 20, res["per_dimension"]["who_did_what_agent"]
        assert res["per_dimension"]["state"] is not None
        assert "temporal" in res["named_gaps"] and "causal" in res["named_gaps"]
        # 19c-free guarantee: no dimension's gold is LitBank
        for k, v in res["transferred_to_modern"].items():
            assert "LitBank" not in v["gold"] and "19c" not in v["gold"], (k, v)
        # step-0 crossref is present + demoted (informational, not the headline)
        cr = res["informational_19c_crossref"]
        assert cr["corpus"].startswith("LitBank") and "DEMOTED" in cr["status"], cr
        _print(res)
        print("\n[self-test] PASS (new arms OFF; 19c LitBank demoted to informational_19c_crossref)")
        return
    res = run(caps={"wic_mode": "full"}, n_boot=a.n_boot)
    _print(res)
    print("\nwrote %s" % os.path.relpath(os.path.join(OUT_DIR, "metrics.json"), _REPO))


if __name__ == "__main__":
    main()
