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
# THREE NEW BOARD ARMS (step B): make this session's board-INVISIBLE proven wins SCORED, each reusing the
# solver's OWN measurement. Kept OUT of the 19c-free headline aggregate (`_agg` reads only the 7 core dims);
# these live in res["new_board_arms"] as their own per_dimension rows. OFF in the board self-test.
#   coarse_sense           -- word-sense p7 coarse a_s (SemCor; INFORMATIONAL under the 19c ban, mid-20c).
#   selective_reliability  -- precision-defer p4 (UD-EWT; MODERN): answered-acc gain at dev-tau, twin flat.
#   causal_multihop        -- causal p10 (WIQA multi-hop + TellMeWhy non-adjacent; MODERN): traversal beats
#                             the 1-hop adjacency floor + shuffled-edge twin CI-sep.
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
