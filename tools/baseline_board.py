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
PHASE 2 (NOT built here -- listed as pending in the .md): modern who-did-what (QA-SRL) + who-has-what
  (MCScript2), both blocked on persisting the parser/world-state solver cells (untracked, HARD-FAIL Q115).

Run:  .venv/Scripts/python.exe tools/baseline_board.py --docs 16
      (be patient: the WSD graph build is ~1-2 min, then ~2-3 min to score WiC-dev with the twin.)
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
                             arm, _WDW_NOTE[arm] + " Scores the AGENT slot (subject head) via build_events_questions."))
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
# rendering: printed table + notes/BASELINE_BOARD.md (same records) + json snapshot
# ==================================================================================================
_PHASE2 = [
    ("modern who-did-what (QA-SRL)",
     "The arm that shows the parser's measured +0.033 lift. Its gold/scorer live in the parser solver's "
     "UNTRACKED cells (exp_arceager_parser_operator_v1 / exp_predarg_frontend_organ_v1 / QA-SRL pop) which "
     "HARD-FAIL the Q115 repro hook -> blocked on persisting those cells."),
    ("who-has-what (MCScript2)",
     "The coref-densifier's arm. Its gold/scorer live in the untracked exp_world_state_* cells -> blocked on "
     "persisting those cells."),
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
             "(patient: WSD graph build ~1-2 min). model/floor/twin are accuracies in [0,1]; higher model, "
             "and model separated above floor & twin, is the win.")
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
    L.append("## PHASE 2 (pending cell persistence)")
    L.append("")
    L.append("These levers are NOT on the board yet -- honest about what it does not cover. Both are blocked "
             "on persisting untracked solver cells (they HARD-FAIL the Q115 repro hook), not on the science:")
    for name, why in _PHASE2:
        L.append(f"- **{name}** — {why}")
    L.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description="Versioned baseline board across the reading-comprehension levers.")
    ap.add_argument("--docs", type=int, default=16, help="LitBank docs for the reader-QA + who-did-what arms (default 16).")
    ap.add_argument("--wic-max", type=int, default=None, help="cap WiC-dev pairs (default: full dev, ~638).")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    t0 = time.time()
    docs = SITQA.load_docs(args.docs)
    print(f"[baseline_board] docs={len(docs)}  seed={args.seed}  running 3 instruments (degrade-gracefully)...")

    records: List[dict] = []
    print("[A] reader QA (5 live dims + aggregate, 19c LitBank) ...")
    records += instrument_reader_qa(docs)
    print("[B] who-did-what role-path arms (positional/wired/wired_arceager, 19c LitBank) ...")
    records += instrument_who_did_what(docs)
    print("[C] WSD on WiC-dev (modern) -- building the settling graph (heavy) ...")
    records += instrument_wsd_wic(seed=args.seed, wic_max=args.wic_max)

    elapsed = time.time() - t0
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(OUT_JSON_DIR, exist_ok=True)
    json_path = os.path.join(OUT_JSON_DIR, f"baseline_{date}.json")
    meta = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "docs": args.docs, "seed": args.seed, "elapsed_s": round(elapsed, 1),
            "json_path": json_path, "n_records": len(records),
            "note": "Versioned baseline board. Top-level is {meta, records}; `records` is the list of rows."}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "records": records}, f, indent=2)
    write_markdown(records, meta)

    print_table(records, meta)
    print(f"\nwrote {os.path.relpath(json_path, REPO)}")
    print(f"wrote {os.path.relpath(OUT_MD, REPO)}")


if __name__ == "__main__":
    main()
