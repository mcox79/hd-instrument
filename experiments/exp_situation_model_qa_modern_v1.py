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
#   coref_via_reader       -- p12 coref stack (GUM he/she; MODERN): the LIVE EventCentralityReader pronoun pick
#                             with the phi_person_filter/narrow_him/soften_generic_suppress wires ON (~0.5855) vs
#                             the flag-OFF incumbent (~0.5032) + the info-free shuffled-identity twin -- the
#                             +0.082 CI-sep gain the board's URG-resolver `coref` tile does NOT show (a DIFFERENT
#                             resolver). Reuses verification/test_coref_stack_landing's W1 measurement verbatim.
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
                          "(0.41 -> 0.73) but is DEFAULT-OFF (joint_nominal_events) pending a WSD precision gate "
                          "(the meaning-channel follow-on). Reuses exp_joint_temporal_survival_v1 + "
                          "exp_joint_temporal_realreasoner_v1 verbatim."}
        return row, detail
    except Exception as e:
        return _degraded("temporal_survival", e), {"error": "%s: %s" % (type(e).__name__, e)}


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
