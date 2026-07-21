#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_ud_ewt_semantic_affectedness_independent_scoreboard_v1

INDEPENDENT-ANNOTATOR SEMANTIC SCOREBOARD for the who-is-affected reader. Every prior meaning-module
number (v1 0.912; v2 held-out 0.816) carried a co-defined asterisk (VET ad793d3a / a38fa920): the same
annotator who wrote the gate lexicon also wrote the gold, so the gold shared the gate's own definition.
This cell removes that asterisk. It scores the reader against a SEMANTIC affectedness gold labeled by an
annotator BLIND to the gate lexicon / VerbNet resource, over 52 UD-EWT TEST sentences (56 rows) that are
also HELD-OUT from the front-end (POS/arc parser/labeler were trained on the UD-EWT TRAIN split).

GOLD: data/ud_ewt_semantic_affectedness_gold_v1/gold.json (independent annotator, blind to the lexicon).
  schema {id, sent_id, text, verb, affected(span|null), type(6-way), intuition, ambiguous, note}.
  6-way taxonomy: patient / target_not_affected / none / negated / transfer / effected.

THREE ARMS (one variable = the gate; SAME front-end, SAME gold, recomputed in-cell):
  STRUCTURAL = raw reader, gate OFF: any grammatical object the reader extracts counts as affected. This
               is the real baseline/contrast (the structural-gold view the semantic gold was built to
               expose). It can only get NOT-affected rows right when the reader extracts nothing.
  BASE_GATE  = arm A = the v2 verb-affectedness gate (full_gate baseline: clause-aware negation -> hand
               phrasal/copula/stative overrides -> VerbNet-graded lemma-modal). THIS ARM'S NUMBER IS THE
               HONEST, NON-CO-DEFINED GATE SCORE -- unconditionally valuable.
  WSD_GATE   = arm B = the WSD frame+selectional reader (full_gate frame_sel: parse-frame matched to
               VerbNet per-sense frames + object-animacy selrestr tie-break). Reported as its DELTA vs A.

  All three share the reader's extracted span (base_pick) + the SAME front-end. Arm A vs B differ ONLY in
  the sense-selection step; both differ from STRUCTURAL only in whether the gate fires.

PRIMARY METRIC (headline) = BINARY affected-vs-not. Collapse the 6-way to yes/no:
  gold_yes  = type in {patient, transfer, effected}  (a genuinely-affected patient/theme exists)
  gold_no   = type in {target_not_affected, none, negated}
  pred_yes(arm) = (gate does NOT force-none) AND (reader extracted a span)
  binary_correct = (pred_yes == gold_yes).
  Rationale (task-specified): psych verbs (want/know/enjoy) sit on a defensible-but-fuzzy
  target_not_affected/none line, so the robust signal is affected-vs-not, NOT the fine 6-way.
  The 4 ambiguous-flagged rows (gold 'ambiguous':true = u08,u42,u44,u56) are EXCLUDED from the primary
  metric and reported separately as a sensitivity check (how the number moves if counted).

SECONDARY:
  - per-class (all 6 gold types) binary-correct breakdown per arm (shows WHERE the gate helps: it should
    recover target_not_affected + negated + stative-none, at some over-fire cost on affected classes).
    NOTE (honest): the reader is a BINARY affected/not gate, NOT a native 6-way classifier -- it cannot
    emit patient-vs-transfer-vs-effected. So the substantive secondary is the per-class binary
    stratification, not a fabricated 6-way confusion (which would be capped low by construction).
  - span-match on the affected rows (patient/transfer/effected): of rows an arm correctly calls
    'affected', does the reader's extracted head-token match the normalized gold span.

SPAN NORMALIZATION (required): gold 'affected' spans carry parenthetical clarifications, e.g.
  "it (my laptop)", "the bartender (rel. '...person...met')". normalize_gold_span STRIPS the "(...)"
  parenthetical, THEN reduces to lowercased content head tokens via the v1 span_head_tokens (drops
  determiners/stopwords). The reader's base_pick surf is already lowercased -> head-token membership match.

DESIGN-GATE (pre-registered BEFORE running; see prereg banner below; CAN-FAIL):
  real_baseline = STRUCTURAL (raw reader, every object=affected) -- exposes the structural-vs-semantic gap.
  one_variable  = the gate (STRUCTURAL off; BASE_GATE = lemma-modal; WSD_GATE = +frame+selectional).
  can_fail      = the gate could score no better than structural on INDEPENDENT labels (if the blind
                  annotator's affected-vs-not judgments do not align with the gate's lexicon, gen_margin
                  collapses -> GATE_NO_LIFT_INDEPENDENT -> the co-defined asterisk was load-bearing).
  difficulty_on = real UD-EWT test web-text + an independent (blind) annotator, not the gate's own author.
  BANDS (headline = BASE_GATE binary acc vs STRUCTURAL binary acc, N=52 non-ambiguous):
    gen_margin = base_gate_acc - structural_acc
    GATE_GENERALIZES_INDEPENDENT (PASS): gen_margin >= 0.15 AND base_gate_acc >= 0.70
    GATE_WEAK_LIFT_INDEPENDENT   (MIDDLE): 0.05 < gen_margin < 0.15  (OR PASS-margin but base<0.70)
    GATE_NO_LIFT_INDEPENDENT     (FAIL):  gen_margin <= 0.05         (asterisk load-bearing)
  WSD delta (arm B, secondary, NOT gating the headline): wsd_delta = wsd_acc - base_gate_acc; the WSD
    overlay is Pareto-safe (only changes polysemous verbs with animate objects), so |wsd_delta| is
    EXPECTED small on UD test; report exactly which rows flip. wsd_delta > 0 with no broken affected rows
    = WSD_HELPS; wsd_delta < 0 = WSD_REGRESSES; else WSD_NEUTRAL.

SELF-TEST (non-tautological, formula-selftest): (1) score TRACKS labels -- fully INVERTING gold_yes gives
  inverted_acc == 1 - original_acc EXACTLY (binary_correct = (pred_yes==gold_yes) flips per row); (2)
  gate is GOLD-FREE -- permuting the gold type/affected labels leaves every arm's pred_yes vector
  byte-identical; (3) arms GENUINELY DIFFER -- STRUCTURAL and BASE_GATE pred vectors are not identical
  (the gate fires on >=1 row); (4) span-normalization strips parentheticals ("it (my laptop)" -> {"it"};
  "the bartender (...)" -> contains "bartender").

Compute architecture: sequential-CPU, justified (pure-python glass-box pass over 56 gold rows; persisted
  averaged-perceptron POS + hashed arc-parser/labeler; nltk VerbNet/WordNet cached lookups; wall seconds;
  no matmul inner loop -> not a GPU candidate). Storage: no_storage/no_composition (measurement cell;
  atomic tmp+replace). Determinism: OMP/MKL/OPENBLAS=1; fixed seed in leak probe; no hash()-seeded RNG.
  LOCAL foreground; NO queue, NO push, NO remote-persist, NO git add, NO hdlab mutation, NO atom bank
  (skunkworks owns banking after VET). ASCII-only, no em-dashes.

# CELL-TEMPLATE MANDATORY (measurement cell; single-shot, no seed/sweep axis):
# - arms_differ_verified at smoke gate (structural/base_gate/wsd pred vectors not all identical)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: accuracy on labeled gold, no noise floor
# - baseline_in_band: STRUCTURAL binary acc in (0.05,0.95) verified at run
# - discriminator survives scale: full IS the scale (N=56 fixed independent gold; not a smoke-vs-full-N issue)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - cardinality_ok: n/a (no sweep axis; single deterministic pass)
# - calibration_check: default_ok_for_this_regime (0.35 = v2 builder spot-check 94.4% dec acc)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import copy
import hashlib
import json
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "ud_ewt_semantic_affectedness_independent_scoreboard_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the reader front-end wiring + the v2 gate + the WSD overlay (read-only imports; NO mutation, NO fork)
from experiments.exp_mcguffey_whoaffected_wsd_frame_selectional_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, UD_TEST,
    reader_pass, base_pick,
    find_verb_index, span_head_tokens,
    parse_frame, arg_animacy, _parse_full,
    full_gate, verb_is_negated_clauseaware,
    AFFECTED_TYPES, NONE_TYPES,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402

GOLD_PATH = os.path.join(REPO_ROOT, "data", "ud_ewt_semantic_affectedness_gold_v1", "gold.json")

SIX_TYPES = ["patient", "transfer", "effected", "target_not_affected", "none", "negated"]

# pre-registered headline bands (BASE_GATE binary acc vs STRUCTURAL binary acc, N non-ambiguous)
BAND_PASS_MARGIN = 0.15
BAND_PASS_ABS = 0.70
BAND_MIDDLE_MARGIN = 0.05


def normalize_gold_span(affected):
    """Strip parenthetical clarifications from a gold 'affected' span, then reduce to lowercased content
    head tokens (v1 span_head_tokens: drops determiners/stopwords). Returns a set (empty for null)."""
    if affected is None:
        return set()
    stripped = re.sub(r"\s*\([^)]*\)", "", affected).strip()
    return span_head_tokens(stripped)


def score_row(g, tagger, parser, labeler):
    """Run the reader + all three arms on one gold row. Returns a per-instance dict (gold-labeled)."""
    text, gverb, gaff, gtype = g["text"], g["verb"], g["affected"], g["type"]
    gold_yes = gtype in AFFECTED_TYPES
    assert gtype in (AFFECTED_TYPES | NONE_TYPES), "unexpected gold type: %r" % gtype
    heads_gold = normalize_gold_span(gaff)

    tokens = ud_tokenize(text)
    rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
    pos = rp["pos"]
    vidx, pos_missed = find_verb_index(tokens, pos, gverb)
    pool = rp["pools"].get(vidx, []) if vidx is not None else []
    bp = base_pick(pool)
    pred_surf = bp["surf"] if bp is not None else None
    pred_none = bp is None

    # parse-frame + object-animacy for the WSD arm
    _pos2, heads, labels = _parse_full(tokens, tagger, parser, labeler)
    pframe = parse_frame(tokens, _pos2, heads, labels, vidx)
    obj_aidx = pframe["obj_aidx"]
    obj_anim = arg_animacy(tokens[obj_aidx - 1], _pos2[obj_aidx - 1]) if obj_aidx else None
    neg = verb_is_negated_clauseaware(tokens, vidx)

    # three arms: STRUCTURAL never forces none; BASE_GATE = v2 lemma-modal; WSD = frame+selectional
    struct_fn = False
    base_fn, base_src = full_gate(gverb, pframe, obj_anim, neg, "baseline")
    wsd_fn, wsd_src = full_gate(gverb, pframe, obj_anim, neg, "frame_sel")

    def pred_yes(force_none):
        return bool((not force_none) and pred_surf is not None)

    def binary_correct(force_none):
        return bool(pred_yes(force_none) == gold_yes)

    def span_ok(force_none):
        # only meaningful on rows the arm correctly calls 'affected'
        return bool(gold_yes and pred_yes(force_none) and pred_surf is not None and pred_surf in heads_gold)

    return {
        "id": g["id"], "sent_id": g.get("sent_id"), "text": text, "verb": gverb,
        "type": gtype, "gold_affected": gaff, "gold_yes": gold_yes,
        "ambiguous": bool(g.get("ambiguous", False)),
        "heads_gold": sorted(heads_gold),
        "pred_surf": pred_surf, "pred_none": pred_none, "pos_missed": pos_missed,
        "parse_sig": pframe["sig"], "obj_anim": obj_anim, "neg": neg,
        "struct_force_none": struct_fn, "base_force_none": base_fn, "base_src": base_src,
        "wsd_force_none": wsd_fn, "wsd_src": wsd_src,
        "struct_pred_yes": pred_yes(struct_fn), "base_pred_yes": pred_yes(base_fn),
        "wsd_pred_yes": pred_yes(wsd_fn),
        "struct_correct": binary_correct(struct_fn), "base_correct": binary_correct(base_fn),
        "wsd_correct": binary_correct(wsd_fn),
        "struct_span_ok": span_ok(struct_fn), "base_span_ok": span_ok(base_fn),
        "wsd_span_ok": span_ok(wsd_fn),
    }


def _acc(rows, key):
    if not rows:
        return None, 0, 0
    c = sum(1 for r in rows if r[key])
    return round(c / len(rows), 4), len(rows), c


def run(mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    _tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(_tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(_tmp, os.path.join(out_dir, "_start_marker.json"))
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_doc = json.load(f)
    gold = gold_doc["gold"]
    if mode == "smoke":
        gold = gold[:14]

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded; independent gold N={len(gold)}", flush=True)

    rows = [score_row(g, tagger, parser, labeler) for g in gold]
    n_all = len(rows)

    # PRIMARY: non-ambiguous rows only
    prim = [r for r in rows if not r["ambiguous"]]
    ambig = [r for r in rows if r["ambiguous"]]
    n_prim = len(prim)

    s_struct = _acc(prim, "struct_correct")
    s_base = _acc(prim, "base_correct")
    s_wsd = _acc(prim, "wsd_correct")

    gen_margin = round((s_base[0] or 0.0) - (s_struct[0] or 0.0), 4)
    wsd_delta = round((s_wsd[0] or 0.0) - (s_base[0] or 0.0), 4)

    # SENSITIVITY: include the 4 ambiguous rows
    a_struct = _acc(rows, "struct_correct")
    a_base = _acc(rows, "base_correct")
    a_wsd = _acc(rows, "wsd_correct")

    # SECONDARY: per-class binary-correct breakdown (all 6 gold types), primary (non-amb) rows
    per_type = {}
    for ty in SIX_TYPES:
        items = [r for r in prim if r["type"] == ty]
        per_type[ty] = {
            "n": len(items),
            "struct_correct": _acc(items, "struct_correct")[2],
            "base_correct": _acc(items, "base_correct")[2],
            "wsd_correct": _acc(items, "wsd_correct")[2],
            "struct_acc": _acc(items, "struct_correct")[0],
            "base_acc": _acc(items, "base_correct")[0],
            "wsd_acc": _acc(items, "wsd_correct")[0],
        }

    # SECONDARY: span-match on affected rows (patient/transfer/effected), non-amb
    aff_rows = [r for r in prim if r["gold_yes"]]
    span_struct = _acc(aff_rows, "struct_span_ok")
    span_base = _acc(aff_rows, "base_span_ok")
    span_wsd = _acc(aff_rows, "wsd_span_ok")

    # WSD flip transparency: rows where WSD decision differs from BASE_GATE
    wsd_flips = [{"id": r["id"], "verb": r["verb"], "type": r["type"], "gold_yes": r["gold_yes"],
                 "base_force_none": r["base_force_none"], "wsd_force_none": r["wsd_force_none"],
                 "base_correct": r["base_correct"], "wsd_correct": r["wsd_correct"],
                 "wsd_src": r["wsd_src"], "parse_sig": r["parse_sig"], "obj_anim": r["obj_anim"]}
                 for r in rows if r["base_pred_yes"] != r["wsd_pred_yes"]]

    # BASE_GATE misses (transparency): non-amb rows the base gate gets wrong
    base_misses = [{"id": r["id"], "verb": r["verb"], "type": r["type"], "gold_yes": r["gold_yes"],
                    "base_force_none": r["base_force_none"], "base_src": r["base_src"],
                    "pred_surf": r["pred_surf"], "pred_none": r["pred_none"], "neg": r["neg"]}
                   for r in prim if not r["base_correct"]]

    # ARMS-MUST-DIFFER (pred_yes vectors across the three arms; all-56)
    def _digest(key):
        return hashlib.sha256(bytes([1 if r[key] else 0 for r in rows])).hexdigest()
    arm_digests = {"structural": _digest("struct_pred_yes"), "base_gate": _digest("base_pred_yes"),
                   "wsd_gate": _digest("wsd_pred_yes")}
    arms_differ = len(set(arm_digests.values())) > 1
    struct_vs_base_differ = arm_digests["structural"] != arm_digests["base_gate"]

    struct_in_band = bool(0.05 < (s_struct[0] or 0.0) < 0.95)

    # ---- verdict (headline = BASE_GATE binary generalization over STRUCTURAL on INDEPENDENT labels) ----
    if not struct_vs_base_differ:
        headline = "SCOREBOARD_ARMS_IDENTICAL_BUG"
    elif gen_margin >= BAND_PASS_MARGIN and (s_base[0] or 0.0) >= BAND_PASS_ABS:
        headline = "GATE_GENERALIZES_INDEPENDENT"
    elif gen_margin > BAND_MIDDLE_MARGIN:
        headline = "GATE_WEAK_LIFT_INDEPENDENT"
    else:
        headline = "GATE_NO_LIFT_INDEPENDENT"

    if wsd_delta > 0 and all(f["wsd_correct"] or not f["gold_yes"] for f in wsd_flips):
        wsd_tier = "WSD_HELPS"
    elif wsd_delta < 0:
        wsd_tier = "WSD_REGRESSES"
    else:
        wsd_tier = "WSD_NEUTRAL"

    verdict = headline
    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] INDEPENDENT (blind-annotator) semantic affectedness scoreboard, UD-EWT test, "
        f"N_primary={n_prim} (+{len(ambig)} ambiguous held out) | BINARY affected-vs-not acc: "
        f"STRUCTURAL={s_struct[0]}({s_struct[2]}/{s_struct[1]}) BASE_GATE(armA)={s_base[0]}"
        f"({s_base[2]}/{s_base[1]}) WSD(armB)={s_wsd[0]}({s_wsd[2]}/{s_wsd[1]}) | "
        f"gen_margin(base-struct)={gen_margin} wsd_delta(wsd-base)={wsd_delta} ({wsd_tier}) | "
        f"with-ambiguous(N={n_all}): struct={a_struct[0]} base={a_base[0]} wsd={a_wsd[0]} | "
        f"per_type_base=" + ",".join(f"{ty}:{per_type[ty]['base_correct']}/{per_type[ty]['n']}" for ty in SIX_TYPES)
        + f" | span_match_affected(n={span_base[1]}): struct={span_struct[0]} base={span_base[0]} "
        f"wsd={span_wsd[0]} | wsd_flips={len(wsd_flips)} | arms_differ={arms_differ} "
        f"struct_in_band={struct_in_band}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "wsd_tier": wsd_tier,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "N_all": n_all, "N_primary": n_prim, "N_ambiguous": len(ambig), "is_probe_flag": True,
        "note": ("Independent-annotator (blind to gate lexicon/VerbNet) semantic affectedness gold over 52 "
                 "UD-EWT TEST sentences (held out from the front-end's TRAIN split). Removes the co-defined "
                 "asterisk on every prior meaning-module number (v1 0.912/v2 0.816 were single-annotator "
                 "gold sharing the gate's own definition, VET ad793d3a/a38fa920). PRIMARY = binary "
                 "affected-vs-not; ambiguous rows excluded. STRUCTURAL(raw)=real baseline; BASE_GATE=arm A "
                 "honest gate; WSD=arm B delta. Gate = verb/frame/animacy, gold-independent -> leak-clean. "
                 "LOCAL-only; no push/remote-persist; no hdlab mutation; no atom bank (skunkworks after VET)."),
        "primary_binary": {
            "n": n_prim,
            "structural_acc": s_struct[0], "base_gate_acc": s_base[0], "wsd_gate_acc": s_wsd[0],
            "structural_correct": s_struct[2], "base_gate_correct": s_base[2], "wsd_gate_correct": s_wsd[2],
            "gen_margin_base_minus_struct": gen_margin, "wsd_delta_wsd_minus_base": wsd_delta,
            "struct_in_band": struct_in_band,
        },
        "ambiguous_sensitivity": {
            "n_ambiguous": len(ambig),
            "ambiguous_ids": [r["id"] for r in ambig],
            "with_ambiguous_structural_acc": a_struct[0], "with_ambiguous_base_gate_acc": a_base[0],
            "with_ambiguous_wsd_gate_acc": a_wsd[0],
            "base_gate_shift": round((a_base[0] or 0.0) - (s_base[0] or 0.0), 4),
            "ambiguous_rows": [{"id": r["id"], "verb": r["verb"], "type": r["type"], "gold_yes": r["gold_yes"],
                                "base_correct": r["base_correct"], "wsd_correct": r["wsd_correct"]}
                               for r in ambig],
        },
        "secondary_per_type": per_type,
        "secondary_span_match_affected": {
            "n_affected": span_base[1],
            "structural_span_acc": span_struct[0], "base_gate_span_acc": span_base[0],
            "wsd_gate_span_acc": span_wsd[0],
            "structural_span_correct": span_struct[2], "base_gate_span_correct": span_base[2],
            "wsd_gate_span_correct": span_wsd[2],
            "note": ("span-match = reader head-token in normalized gold span, over rows the arm correctly "
                     "calls 'affected'. reader is a BINARY gate, not a 6-way classifier -> no fabricated "
                     "6-way confusion; per-class binary breakdown above is the substantive secondary."),
        },
        "wsd_flips": wsd_flips,
        "base_gate_misses": base_misses,
        "arms_differ_verified": arms_differ, "struct_vs_base_differ": struct_vs_base_differ,
        "arm_digests": arm_digests,
        "per_instance": rows,
        "design_gate": {
            "real_baseline": "STRUCTURAL raw reader (any extracted object = affected), recomputed in-cell",
            "one_variable": "the gate (STRUCTURAL off; BASE_GATE=lemma-modal; WSD=frame+selectional)",
            "can_fail": ("gen_margin<=0.05 => gate no better than structural on INDEPENDENT labels => the "
                         "co-defined asterisk was load-bearing (GATE_NO_LIFT_INDEPENDENT)"),
            "difficulty_on": "real UD-EWT test web-text + an annotator BLIND to the gate lexicon",
            "leak_clean": ("gate = verb-lemma + parse-frame + argument-animacy, gold-independent; self_test "
                           "permutes gold labels + re-derives -> pred vectors byte-identical; inverting "
                           "gold_yes gives inverted_acc==1-orig exactly"),
            "bands": {"PASS": "gen_margin>=0.15 AND base_gate_acc>=0.70",
                      "MIDDLE": "0.05<gen_margin<0.15 (or PASS-margin but base<0.70)",
                      "FAIL": "gen_margin<=0.05"},
            "span_normalization": "strip '(...)' parenthetical then v1 span_head_tokens (drop dets/stopwords)",
            "final_metrics_atomicity": "tmp_replace", "crlb_n/a": "accuracy on labeled gold, no noise floor",
            "calibration_check": "default_ok_for_this_regime (0.35 = v2 builder spot-check 94.4% dec acc)",
        },
        "credit": ("gold: independent blind annotator. reader/gate: VerbNet (Kipper-Schuler 2005); WordNet "
                   "(Fellbaum 1998); Levin 1993; Dowty 1991 proto-patient; Beavers 2011; Paczynski-Kuperberg "
                   "2012; v1 hand-lexicon + v2 held-out gate + WSD frame_selectional_v1 (commit 9f31de741)."),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    print("[self_test] start", flush=True)
    # --- span normalization: strip parenthetical clarifications ---
    assert normalize_gold_span("it (my laptop)") == {"it"}, normalize_gold_span("it (my laptop)")
    assert "bartender" in normalize_gold_span("the bartender (rel. '...person...met')")
    assert normalize_gold_span("the Americans") == {"americans"}
    assert normalize_gold_span(None) == set()
    assert normalize_gold_span("These") == {"these"}

    # --- gold loads, schema sound ---
    with open(GOLD_PATH, encoding="utf-8") as f:
        gd = json.load(f)
    gold = gd["gold"]
    assert len(gold) == 56, len(gold)
    assert sum(1 for g in gold if g.get("ambiguous")) == 4
    for g in gold:
        assert g["type"] in (AFFECTED_TYPES | NONE_TYPES), "unexpected type %r" % g["type"]

    # --- real code path: construct the REAL front-end + score real rows ---
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    rows = [score_row(g, tagger, parser, labeler) for g in gold]
    assert len(rows) == 56
    assert all("base_correct" in r and "struct_pred_yes" in r for r in rows)

    prim = [r for r in rows if not r["ambiguous"]]
    orig_base_acc = _acc(prim, "base_correct")[0]

    # --- NON-TAUTOLOGICAL #1: score TRACKS labels. Inverting gold_yes => binary_correct flips per row =>
    #     inverted_acc == 1 - orig_acc EXACTLY (pred_yes is fixed; correct = pred_yes==gold_yes). ---
    inv_correct = [r["base_pred_yes"] != r["gold_yes"] for r in prim]   # correctness under flipped gold_yes
    inv_acc = round(sum(inv_correct) / len(prim), 4)
    assert abs(inv_acc - round(1 - orig_base_acc, 4)) < 1e-9, (inv_acc, orig_base_acc)
    assert inv_acc != orig_base_acc, "score does not respond to labels (tautology)"

    # --- NON-TAUTOLOGICAL #2: gate is GOLD-FREE. Permute gold type/affected -> pred_yes vectors identical. ---
    import random
    rng = random.Random(12345)   # FIXED seed (no hash()-derived seeding; PROT-023)
    perm = list(range(len(gold)))
    rng.shuffle(perm)
    mutated = []
    for k, g in enumerate(gold):
        gg = copy.deepcopy(g)
        gg["type"] = gold[perm[k]]["type"]
        gg["affected"] = gold[perm[k]]["affected"]
        mutated.append(gg)
    mut_rows = [score_row(g, tagger, parser, labeler) for g in mutated]
    for key in ("struct_pred_yes", "base_pred_yes", "wsd_pred_yes"):
        base_vec = [r[key] for r in rows]
        mut_vec = [r[key] for r in mut_rows]
        assert base_vec == mut_vec, "LEAK: %s changed when gold labels were permuted" % key

    # --- NON-TAUTOLOGICAL #3: arms GENUINELY DIFFER (structural vs base_gate pred vectors not identical) ---
    struct_vec = [r["struct_pred_yes"] for r in rows]
    base_vec = [r["base_pred_yes"] for r in rows]
    assert struct_vec != base_vec, "gate never fires -> structural == base_gate (arms identical bug)"

    print("[self_test] span-norm OK; gold OK; real-code-path OK; label-inversion tracks (1-acc) OK; "
          "gold-free permutation OK; arms-differ OK", flush=True)
    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run("smoke"); return
    if args.full:
        run("full"); return
    self_test()


if __name__ == "__main__":
    out_dir_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(out_dir_crash, exist_ok=True)
        with open(os.path.join(out_dir_crash, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
