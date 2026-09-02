"""baseline_board -- a VERSIONED BASELINE BOARD across the reading-comprehension levers.

WHAT THIS IS: an ASSEMBLY of EXISTING, TRACKED evals into ONE durable, re-runnable tool so the team
can see what a future improvement actually yields (diff two snapshots). It is NOT new science and it
does NOT re-implement any scorer -- every number is produced by the existing experiment/organ code,
called through its public entry points. It writes two artifacts every run:
  - data/baseline_board/baseline_<YYYY-MM-DD>.json  : machine-readable snapshot ({meta, records:[...]})
  - notes/BASELINE_BOARD.md                         : the human-readable table of the SAME records

DESIGNED TO BE RE-RUN AND DIFFED: a fixed doc set (--docs, default 16 for the LitBank arms), pinned
seeds, deterministic. Each instrument degrades gracefully -- if it errors it records a row with
model=null + an error note rather than crashing the whole board (the board must always emit artifacts).

PHASE 1 instruments (all TRACKED components):
  A. Reader QA -- 5 live dimensions + aggregate on 19c LitBank  (exp_situation_model_qa_v1.run, capable)
  B. who-did-what role-path arms on 19c LitBank                 (positional / wired / wired_arceager)
  C. WSD on WiC-dev (modern)                                    (grounded_semantic_graph.select_sense vs MFS)
PHASE 2 instruments (GRADUATED 2026-09-02 -- their solver cells are now TRACKED; assembled here):
  D. MODERN who-did-what on QA-SRL: arc/richfeat vs arc-eager parser  (exp_parser_through_real_organs_v1.run_pop)
     -- THE arm that shows the parser's +0.033 lift, invisible on the 19c board (B). Arms: positional /
        richfeat(live) / arc_eager(promoted) / organ_hybrid_role(live wired organ).
  E. who-has-what: LitBank he/she coref-densify (NON-CIRCULAR honest headline, blind->reader +0.148,
        exp_world_state_coref_densify_v1.run) + MCScript2 end-to-end (exp_world_state_endtoend_whohaswhat_v1.run,
        FLAGGED: full==gold==twin==1.0 -> degenerate twin, so LitBank is the headline).

Run:  .venv/Scripts/python.exe tools/baseline_board.py --docs 16
      (be patient: ~10-15 min. WSD graph build ~1-2 min + WiC scoring ~2-3 min; the new D/E parser +
      world-state arms add ~5 min. Every instrument degrades gracefully -- artifacts are ALWAYS written.)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ---- TRACKED reuse surface (public entry points; NOTHING re-implemented) --------------------------
import experiments.exp_situation_model_qa_v1 as SITQA           # A + the who-did-what gold/scorer for B
from hdlab.situation_reader import SituationReader              # B: the three role-path arms
from tools.load_wsd_benchmarks import load_wic                  # C: modern WiC benchmark loader
from hdlab.grounded_semantic_graph import GroundedSemanticGraph  # C: the promoted settling-graph organ

OUT_JSON_DIR = os.path.join(REPO, "data", "baseline_board")
OUT_MD = os.path.join(REPO, "notes", "BASELINE_BOARD.md")

SEED = 20260902


# ==================================================================================================
# record helper -- one row of the board
# ==================================================================================================
def _rec(instrument, metric, corpus, domain, model, floor, twin, n, config, note):
    """One board record. model/floor/twin are ACCURACIES (float in [0,1]) or None (null in JSON)."""
    def _r(x):
        return round(float(x), 4) if isinstance(x, (int, float)) and x is not None else None
    return {"instrument": instrument, "metric": metric, "corpus": corpus, "domain": domain,
            "model": _r(model), "floor": _r(floor), "twin": _r(twin),
            "n": int(n) if n is not None else None, "config": config, "note": note}


# ==================================================================================================
# A. READER QA -- 5 live dimensions + aggregate (19c LitBank), via exp_situation_model_qa_v1.run
# ==================================================================================================
_DIM_NOTE = {
    "coref": "which-entity from accumulated coref_resolutions (LitBank coref gold).",
    "events": "who-did-what agent off the event index (LitBank WDW gold); CAPABLE reader (tense-agnostic detector on).",
    "temporal": "before/after off sm.timeline_order; HONEST CAVEAT: gold shares the tense signal (tests the QA claim, not independent temporal reasoning).",
    "causal": "cause off causal_links vs grammar-direction gold; the reader's causal organ is connective-reducible (a connective detector, not force-dynamics).",
    "location": "ISLAND dim -- organ not wired into the live reader; score = correct-ABSTAIN rate (faithful behavior is to abstain).",
    "belief": "ISLAND dim -- ToM organ not wired into the live reader; score = correct-ABSTAIN rate.",
}


def instrument_reader_qa(docs: List[str]) -> List[dict]:
    rows: List[dict] = []
    try:
        res = SITQA.run(docs, seed=SEED, capable=True)
    except Exception as e:
        return [_rec("reader_qa", "qa_aggregate", "LitBank", "19c", None, None, None, None,
                     "capable_reader", f"ERROR: {type(e).__name__}: {e}")]
    rc = res.get("reader_config", {})
    cfg_flags = rc.get("flags", "capable")
    # per-dimension rows (the 5 live dims coref/events/temporal/causal + the 2 island abstain dims)
    for dim, d in res.get("per_dimension", {}).items():
        note = _DIM_NOTE.get(dim, "")
        cfg = f"capable_reader[{cfg_flags}]; floor={d.get('strongest_floor_name', 'overlap_ok')}"
        rows.append(_rec("reader_qa", f"qa_{dim}", "LitBank", "19c",
                         d.get("model_acc"), d.get("strongest_floor"), d.get("twin_acc"),
                         d.get("n"), cfg, note))
    # aggregate row (over the scored dimensions; island abstain rows excluded from the QA accuracy)
    a = res.get("aggregate", {})
    rows.append(_rec("reader_qa", "qa_aggregate", "LitBank", "19c",
                     a.get("model_acc"), a.get("strongest_floor"), a.get("twin_acc"), a.get("n"),
                     f"capable_reader[{cfg_flags}]; temporal_readout={rc.get('temporal_readout')}",
                     "Aggregate model accuracy over the 4 scored dimensions vs strongest per-dim floors + info-free (deranged-router) twin."))
    return rows


# ==================================================================================================
# B. WHO-DID-WHAT role-path arms (19c LitBank) -- SAME gold + scorer as SITQA.run_wired_events_qa
#    (build_events_questions + SituationQA + _match, gold WDW_GOLD), with the arc-eager arm ADDED.
# !! GOLD CAVEAT (integrated 2026-09-02, problem the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold):
#    the WDW_GOLD who-did-what ARGUMENT annotations are ~76% OBLIQUE-CONTAMINATED (a to/from/at PP object mislabelled
#    as the core argument). This arm scores the AGENT/subject slot, which is LESS affected than the object slot, but the
#    gold is KNOWN-NOISY -- the honest cleaned DIRECT-OBJECT patient number is ~0.92 (nearest-post-verbal position, on
#    a precision-98.5% cleaned n=669 gold), NOT the low aggregate here. Do NOT quote this arm as a clean who-did-what
#    capability number; the clean-gold re-measure is the routed follow-on (the_who_did_what_selection_residual_is_structural...).
# ==================================================================================================
_WDW_ARMS = {
    "positional": dict(role_route="positional"),
    "wired": dict(role_route="wired"),
    "wired_arceager": dict(role_route="wired", parser_arceager=True),
}
_WDW_NOTE = {
    "positional": "roles assigned POSITIONALLY (default reader; no parse).",
    "wired": "roles routed through a real parse -> route_predicate_arguments (+ quotative), positional fallback.",
    "wired_arceager": "wired parse routed through the promoted arc-eager parser. EXPECTED ~flat here: arceager is modern-trained; LitBank is 19c/OOD. The modern lift (+0.033) shows in Phase-2 QA-SRL (pending).",
}


def instrument_who_did_what(docs: List[str]) -> List[dict]:
    rows: List[dict] = []
    try:
        gaz = SITQA.load_given_gazetteer()
        wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    except Exception as e:
        return [_rec("who_did_what", "who_did_what", "LitBank", "19c", None, None, None, None,
                     arm, f"ERROR (setup): {type(e).__name__}: {e}") for arm in _WDW_ARMS]
    docset = [d for d in docs if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]
    for arm, flags in _WDW_ARMS.items():
        try:
            ok = n = 0
            for doc in docset:
                path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
                sm = SituationReader(gaz=gaz, **flags).read(path)
                qa = SITQA.SituationQA(sm)
                for q in SITQA.build_events_questions(sm, wdw[doc]):
                    _d, ans = qa.answer(q["question"], q)
                    ok += int(SITQA._match(ans, q["gold"], "events"))
                    n += 1
            model = (ok / n) if n else None
            rows.append(_rec("who_did_what", "who_did_what", "LitBank", "19c", model, None, None, n,
                             arm, _WDW_NOTE[arm] + " Scores the AGENT slot (subject head) via build_events_questions."
                             + " [GOLD ~76% oblique-contaminated -- known-noisy; honest cleaned direct-object ~0.92; do not quote as clean.]"))
        except Exception as e:
            rows.append(_rec("who_did_what", "who_did_what", "LitBank", "19c", None, None, None, None,
                             arm, f"ERROR: {type(e).__name__}: {e}"))
    return rows


# ==================================================================================================
# C. WSD -- WiC-dev (modern): grounded_semantic_graph.select_sense vs MFS floor + context-shuffle twin
#    Reuses tools.load_wsd_benchmarks.load_wic + exp_sense_wall_breakthrough_wic_v1._content (tokenizer)
#    + the PROMOTED organ's select_sense (ppr_w2w). NO scorer re-implemented.
# ==================================================================================================
def instrument_wsd_wic(seed: int = SEED, wic_max: Optional[int] = None) -> List[dict]:
    try:
        from experiments.exp_sense_wall_breakthrough_wic_v1 import _content
        pairs = [{"lemma": r["lemma"].lower(), "pos": r["pos"], "gold": bool(r["gold"]),
                  "sent1": r["sent1"], "sent2": r["sent2"]}
                 for r in load_wic("dev") if r["gold"] is not None]
        if wic_max:
            pairs = pairs[:wic_max]
        t0 = time.time()
        graph = GroundedSemanticGraph().build()          # HEAVY (~1-2 min): built ONCE, cached for the run
        build_s = time.time() - t0
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(pairs))
        model_ok, mfs_ok, twin_ok = [], [], []
        for i, p in enumerate(pairs):
            lemma, pos = p["lemma"], p["pos"]
            c1 = list(_content(p["sent1"]) - {lemma})
            c2 = list(_content(p["sent2"]) - {lemma})
            s1 = graph.select_sense(lemma, pos, c1)
            s2 = graph.select_sense(lemma, pos, c2)
            model_ok.append(int((s1 == s2) == p["gold"]))
            # MFS / first-synset floor: sense-0 for both sentences -> ALWAYS predicts "same"
            mfs_ok.append(int(True == p["gold"]))
            # context-shuffle twin: disambiguate side-2 from a RANDOM other pair's sentence
            oc2 = list(_content(pairs[perm[i]]["sent2"]) - {lemma})
            s2t = graph.select_sense(lemma, pos, oc2)
            twin_ok.append(int((s1 == s2t) == p["gold"]))
        n = len(pairs)
        model = float(np.mean(model_ok)) if n else None
        mfs = float(np.mean(mfs_ok)) if n else None
        twin = float(np.mean(twin_ok)) if n else None
        note = (f"select_sense (ppr_w2w spreading activation); graph={graph.n_edges} edges built in {build_s:.0f}s. "
                "Predict SAME-sense iff the two independently-disambiguated synsets match. Floor=MFS (predict same always). "
                "Twin=context-shuffle (side-2 from a random sentence); model>twin = the context is used.")
        return [_rec("wsd", "wsd", "WiC-dev", "modern", model, mfs, twin, n,
                     "grounded_semantic_graph(relations_glosses+conceptnet+syntagnet)", note)]
    except Exception as e:
        return [_rec("wsd", "wsd", "WiC-dev", "modern", None, None, None, None,
                     "grounded_semantic_graph", f"ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()[-400:]}")]


# ==================================================================================================
# D. MODERN who-did-what (QA-SRL) -- arc/richfeat (LIVE) vs arc-eager (PROMOTED) parser, via
#    exp_parser_through_real_organs_v1.run_pop (loads the V1 QA-SRL population; scores the who-did-what
#    PATIENT through the real organs + the two parser arms). This is THE arm that shows the parser's
#    measured +0.033 modern lift that the 19c LitBank board (Instrument B) cannot see. NOTHING re-implemented.
# ==================================================================================================
def instrument_who_did_what_qasrl(nboot: int) -> List[dict]:
    metric, corpus, domain = "who_did_what", "QA-SRL", "modern"
    _arms = ("positional", "richfeat (arc-factored, LIVE parser)", "arc_eager (promoted parser)")
    try:
        import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
        import experiments.exp_parser_through_real_organs_v1 as PRO
        import experiments.exp_arceager_parser_operator_v1 as AEO
        from hdlab.pos_tagger import PosTagger
        tg = PosTagger.load(os.path.join(REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
        W = AEO.load_model(AEO.MODEL_PATH)
        res = PRO.run_pop("qa", V1.QA, W, tg, nboot)
    except Exception as e:
        return [_rec(metric, metric, corpus, domain, None, None, None, None, arm,
                     f"ERROR: {type(e).__name__}: {e}") for arm in _arms]
    acc = res.get("acc", {}).get("FULL", {}); n = res.get("n_FULL")
    pos = acc.get("POS"); rich = acc.get("BASE_labeler"); ae = acc.get("AE_LABELFREE(mine)")
    organ = acc.get("ORGAN_hybrid_role"); resolve = acc.get("ORGAN_resolve_patient")
    d = res.get("deltas", {}).get("AE_vs_BASE", {})
    ae_note = ("promoted arc-eager parser (heads + label-free patient rule). arc_eager vs richfeat "
               "delta=%+.4f CI[%+.4f,%+.4f] frac<=0=%.3f -- THE modern lift the 19c board (Instrument B) "
               "cannot see. CAVEAT (strategy to confirm): this pair mixes TWO changes (parser richfeat->"
               "arc-eager AND extraction labeled->label-free); the pure one-variable head-swap through "
               "predicate_argument_frontend is +0.0152 matrix-verb / +0.0265 pp-arg F1 (exp_predarg_frontend_organ_v1)."
               ) % (d.get("delta", float("nan")), d.get("ci_lo", float("nan")),
                    d.get("ci_hi", float("nan")), d.get("frac_le_0", float("nan")))
    organ_note = ("the actual wired who-did-what IDENTITY organ (graded_role_assigner: position+voice, "
                  "head-INDEPENDENT -> a better parser does not move it directly; resolve_patient organ ties "
                  "arc_eager at %s). Position floor = the positional row." %
                  (("%.4f" % resolve) if resolve is not None else "n/a"))
    return [
        _rec(metric, metric, corpus, domain, pos, None, None, n, "positional",
             "linear-position floor on the modern QA-SRL FULL population (non-reversible items)."),
        _rec(metric, metric, corpus, domain, rich, pos, None, n, "richfeat (arc-factored, LIVE parser)",
             "the current LIVE frontend parser (arc_parser_richfeat) + labeler object-extraction -- the baseline "
             "arc-eager improves on. Floor = positional."),
        _rec(metric, metric, corpus, domain, ae, pos, None, n, "arc_eager (promoted parser)", ae_note),
        _rec(metric, metric, corpus, domain, organ, pos, None, n, "organ_hybrid_role (LIVE wired organ)", organ_note),
    ]


# ==================================================================================================
# E. who-has-what -- the coref-densifier's lift. TWO populations:
#    E1 LitBank he/she densify (NON-CIRCULAR -> the HONEST headline; blind->reader +0.148, twin loses),
#       via exp_world_state_coref_densify_v1.run.
#    E2 MCScript2 end-to-end through the full EntityBinder, via exp_world_state_endtoend_whohaswhat_v1.run
#       -- FLAGGED: full==gold==twin==1.0 (degenerate twin; the lift is mostly cheap indexical), so E1 leads.
# ==================================================================================================
def instrument_who_has_what(nboot: int, coref_docs: int, mcscript_stories: int) -> List[dict]:
    metric = "who_has_what"
    rows: List[dict] = []
    # --- E1: LitBank he/she densify (the HONEST, non-circular headline) ---
    try:
        import experiments.exp_world_state_coref_densify_v1 as DEN
        r = DEN.run(mode="full", n_docs=coref_docs, n_boot=nboot, seed=20260901)
        n = r.get("n_queries")
        blind = r["blind"]["acc"]; reader = r["reader"]["acc"]
        gold = r["gold_oracle"]["acc"]; twin = r["twin_shuffled_coref"]["acc"]
        dmb = r["reader_minus_blind"]; dmt = r["reader_minus_twin"]
        rows.append(_rec(metric, metric, "LitBank", "19c", blind, None, None, n,
                         "blind (raw-string keys)",
                         "the coref-BLIND world-state register wired today (holder key = raw surface head)."))
        rows.append(_rec(metric, metric, "LitBank", "19c", reader, blind, twin, n,
                         "reader (coref-densified) = HONEST HEADLINE",
                         "holder keyed through the reader's OWN he/she coref. reader vs blind delta=%+.4f "
                         "CI[%+.4f,%+.4f] (twin[shuffled-coref]=%.4f loses: reader-twin %+.4f CI[%+.4f,%+.4f]); "
                         "gold-cluster oracle ceiling=%.4f. NON-CIRCULAR: object key held constant, scored in "
                         "gold-cluster space, so the ONLY varying thing is he/she holder resolution."
                         % (dmb["delta"], dmb["ci"][0], dmb["ci"][1], twin, dmt["delta"],
                            dmt["ci"][0], dmt["ci"][1], gold)))
        ph = r.get("pronoun_holder_subset")
        if ph:
            rows.append(_rec(metric, metric, "LitBank", "19c", ph["reader"]["acc"], ph["blind"]["acc"],
                             ph["twin_single_draw"]["acc"], ph["n"],
                             "reader he/she-holder SUBSET (where blindness bites)",
                             "decisive subset: holder is a he/she pronoun -> blind=%.4f by construction (a pronoun "
                             "string maps to no entity); reader=coref recall, gold=%.4f; shuffled-coref null "
                             "p95=%.4f (reader beats p95=%s)."
                             % (ph["blind"]["acc"], ph["gold"]["acc"],
                                ph["shuffled_coref_null"]["p95"], ph["shuffled_coref_null"]["reader_beats_null_p95"])))
    except Exception as e:
        rows.append(_rec(metric, metric, "LitBank", "19c", None, None, None, None,
                         "reader (coref-densified)", f"ERROR: {type(e).__name__}: {e}"))
    # --- E2: MCScript2 end-to-end (FLAGGED circular/degenerate twin) ---
    try:
        import experiments.exp_world_state_endtoend_whohaswhat_v1 as E2E
        r = E2E.run(mode="full", n_stories=mcscript_stories, n_boot=nboot, seed=SEED)
        n = r.get("n_questions")
        blind = r["blind"]["acc"]; full = r["full"]["acc"]; twin = r["twin"]["acc"]
        bidx = r["blind_idx"]["acc"]; fmb = r["full_minus_blind"]; fmbi = r["full_minus_blindidx"]
        rows.append(_rec(metric, metric, "MCScript2", "modern", blind, None, None, n,
                         "blind (raw-string keys)",
                         "coref-blind register on MCScript2 first-person narrative (deterministic gold)."))
        rows.append(_rec(metric, metric, "MCScript2", "modern", full, blind, twin, n,
                         "full_binder (EntityBinder) -- CIRCULAR/degenerate twin",
                         "END-TO-END through the full EntityBinder. full=gold=twin=%.4f -> the object-anaphora "
                         "twin does NOT lose (full_beats_twin_CIsep=%s); the +%.4f lift over blind is mostly the "
                         "cheap indexical normalization (blind+idx=%.4f; object-anaphora-only full-blindidx=%+.4f "
                         "CI[%+.4f,%+.4f]). DEGENERATE-TWIN CAVEAT -> the LitBank row is the honest headline."
                         % (twin, r.get("full_beats_twin_CIsep"), fmb["delta"], bidx,
                            fmbi["delta"], fmbi["ci"][0], fmbi["ci"][1])))
    except Exception as e:
        rows.append(_rec(metric, metric, "MCScript2", "modern", None, None, None, None,
                         "full_binder (EntityBinder)", f"ERROR: {type(e).__name__}: {e}"))
    return rows


# ==================================================================================================
# rendering: printed table + notes/BASELINE_BOARD.md (same records) + json snapshot
# ==================================================================================================
_PHASE2_LANDED = [
    ("D. modern who-did-what (QA-SRL)",
     "LANDED 2026-09-02. On the board as instrument `who_did_what` / corpus QA-SRL: arc/richfeat (LIVE) vs "
     "arc-eager (PROMOTED) parser -- the +0.033 modern lift the 19c board (B) cannot see. Assembled from the "
     "now-tracked exp_parser_through_real_organs_v1.run_pop (+ exp_arceager_parser_operator_v1)."),
    ("E. who-has-what (LitBank + MCScript2)",
     "LANDED 2026-09-02. On the board as instrument `who_has_what`: LitBank he/she coref-densify is the honest "
     "non-circular headline (blind->reader +0.148, twin loses); MCScript2 end-to-end is included but FLAGGED "
     "(full==gold==twin==1.0 -> degenerate twin). Assembled from the now-tracked exp_world_state_coref_densify_v1 "
     "+ exp_world_state_endtoend_whohaswhat_v1."),
]


def _fmt(x):
    return f"{x:.4f}" if isinstance(x, (int, float)) and x is not None else "  -   "


def print_table(records: List[dict], meta: dict) -> None:
    print("=" * 120)
    print("BASELINE BOARD -- versioned baseline to diff future improvements against")
    print(f"generated {meta['generated_utc']}  |  docs={meta['docs']}  seed={meta['seed']}  "
          f"elapsed={meta['elapsed_s']:.0f}s")
    print("=" * 120)
    hdr = f"{'instrument':13s} {'metric':14s} {'corpus':9s} {'domain':7s} {'model':>7s} {'floor':>7s} {'twin':>7s} {'n':>5s}  config / note"
    print(hdr)
    print("-" * 120)
    for r in records:
        line = (f"{r['instrument']:13s} {r['metric']:14s} {r['corpus']:9s} {r['domain']:7s} "
                f"{_fmt(r['model']):>7s} {_fmt(r['floor']):>7s} {_fmt(r['twin']):>7s} "
                f"{str(r['n']) if r['n'] is not None else '-':>5s}  {r['config']}")
        print(line)
        if r["note"]:
            note = r["note"].replace("\n", " ")
            print(f"{'':70s}    - {note[:180]}")
    print("-" * 120)


def _md_cell(x):
    if x is None:
        return "—"
    return f"{x:.4f}" if isinstance(x, float) else str(x)


def write_markdown(records: List[dict], meta: dict) -> None:
    L = []
    L.append("# Baseline Board")
    L.append("")
    L.append("**The versioned baseline to diff future improvements against.** Each row is one existing, "
             "tracked eval; re-run this and compare snapshots to see what a change actually yields. "
             "Regenerated on every run (do not hand-edit).")
    L.append("")
    L.append(f"- **generated (UTC):** {meta['generated_utc']}")
    L.append(f"- **docs (LitBank arms):** {meta['docs']}  |  **seed:** {meta['seed']}  |  "
             f"**elapsed:** {meta['elapsed_s']:.0f}s")
    L.append(f"- **snapshot JSON:** `{os.path.relpath(meta['json_path'], REPO).replace(os.sep, '/')}`")
    L.append(f"- **HOW TO RE-RUN:** `.venv/Scripts/python.exe tools/baseline_board.py --docs {meta['docs']}` "
             "(patient: ~10-15 min -- WSD graph build ~1-2 min + the D/E parser & world-state arms ~5 min). "
             "model/floor/twin are accuracies in [0,1]; higher model, and model separated above floor & twin, is the win.")
    caps = meta.get("caps", {})
    if caps:
        L.append(f"- **Phase-2 (D/E) caps:** newarm_nboot={caps.get('newarm_nboot')}, "
                 f"coref_docs={caps.get('coref_docs')} (LitBank he/she densify), "
                 f"mcscript_stories={caps.get('mcscript_stories')} (MCScript2 end-to-end). n recorded per row.")
    L.append("")
    L.append("| instrument | metric | corpus | domain | model | floor | twin | n | config |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in records:
        L.append(f"| {r['instrument']} | {r['metric']} | {r['corpus']} | {r['domain']} | "
                 f"{_md_cell(r['model'])} | {_md_cell(r['floor'])} | {_md_cell(r['twin'])} | "
                 f"{_md_cell(r['n'])} | {r['config']} |")
    L.append("")
    L.append("### Row notes")
    for r in records:
        if r["note"]:
            L.append(f"- **{r['instrument']} / {r['metric']} ({r['config'].split(';')[0]}):** "
                     f"{r['note'].replace(chr(10), ' ')}")
    L.append("")
    L.append("## PHASE 2 (LANDED 2026-09-02)")
    L.append("")
    L.append("Both Phase-2 levers are now ON the board (their solver cells became tracked). Nothing else is "
             "pending. Each carries its own honesty caveat in the row notes above:")
    for name, why in _PHASE2_LANDED:
        L.append(f"- **{name}** — {why}")
    L.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description="Versioned baseline board across the reading-comprehension levers.")
    ap.add_argument("--docs", type=int, default=16, help="LitBank docs for the reader-QA + who-did-what arms (default 16).")
    ap.add_argument("--wic-max", type=int, default=None, help="cap WiC-dev pairs (default: full dev, ~638).")
    ap.add_argument("--newarm-nboot", type=int, default=1000,
                    help="bootstrap resamples for the Phase-2 (D/E) arms (default 1000; deterministic seeds).")
    ap.add_argument("--coref-docs", type=int, default=25,
                    help="LitBank coref docs for the who-has-what densify arm (default 25 -> ~135 queries, the tracked headline).")
    ap.add_argument("--mcscript-stories", type=int, default=800,
                    help="MCScript2 stories for the who-has-what end-to-end arm (default 800 -> ~660 Qs; the full 3000 is ~2437 Qs, same degenerate twin).")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    t0 = time.time()
    docs = SITQA.load_docs(args.docs)
    print(f"[baseline_board] docs={len(docs)}  seed={args.seed}  running 5 instruments (degrade-gracefully)...")

    records: List[dict] = []
    print("[A] reader QA (5 live dims + aggregate, 19c LitBank) ...")
    records += instrument_reader_qa(docs)
    print("[B] who-did-what role-path arms (positional/wired/wired_arceager, 19c LitBank) ...")
    records += instrument_who_did_what(docs)
    print("[C] WSD on WiC-dev (modern) -- building the settling graph (heavy) ...")
    records += instrument_wsd_wic(seed=args.seed, wic_max=args.wic_max)
    print("[D] modern who-did-what (QA-SRL): arc/richfeat (LIVE) vs arc-eager (PROMOTED) parser ...")
    records += instrument_who_did_what_qasrl(nboot=args.newarm_nboot)
    print("[E] who-has-what: LitBank he/she densify (honest) + MCScript2 end-to-end (flagged) ...")
    records += instrument_who_has_what(nboot=args.newarm_nboot, coref_docs=args.coref_docs,
                                       mcscript_stories=args.mcscript_stories)

    elapsed = time.time() - t0
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(OUT_JSON_DIR, exist_ok=True)
    json_path = os.path.join(OUT_JSON_DIR, f"baseline_{date}.json")
    meta = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "docs": args.docs, "seed": args.seed, "elapsed_s": round(elapsed, 1),
            "json_path": json_path, "n_records": len(records),
            "caps": {"newarm_nboot": args.newarm_nboot, "coref_docs": args.coref_docs,
                     "mcscript_stories": args.mcscript_stories, "wic_max": args.wic_max},
            "note": "Versioned baseline board. Top-level is {meta, records}; `records` is the list of rows."}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "records": records}, f, indent=2)
    write_markdown(records, meta)

    print_table(records, meta)
    print(f"\nwrote {os.path.relpath(json_path, REPO)}")
    print(f"wrote {os.path.relpath(OUT_MD, REPO)}")


if __name__ == "__main__":
    main()
