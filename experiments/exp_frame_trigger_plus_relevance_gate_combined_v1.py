"""COMPOSE frame-trigger RECALL fix + relevance-gate PRECISION filter; measure the NET result
(2026-08-05).

QUESTION: exp_frame_trigger_predicate_recall_fix_v1 raised RECALL on the independent McGuffey
extraction gold (0.324->0.529) by scanning EVERY frame-lookup predicate site per sentence
(multi_pred=True), but fired many SPURIOUS secondary-predicate events (primary precision
0.180->0.159, n_pred 61->113, tp 18). exp_event_boundary_relevance_gate_v1 raises PRECISION
(+10-35pts on its own 17-event Zwaan-dimension proxy corpus, HARD-PASS scramble-controlled) by
keeping only events that are a genuine situation-model BOUNDARY (protagonist/tense/causation
discontinuity vs the immediately preceding event) -- a post-hoc FILTER, no change to extraction.
Does running the frame-trigger's expanded (high-recall, low-precision) event set THROUGH the
relevance-gate's boundary filter give a NET improvement over BOTH the frozen baseline AND the
frame-trigger-alone arm, on the SAME independent gold?

WHY THIS COMPOSITION IS NON-TRIVIAL (glass-box, no reimplementation): the relevance-gate's
is_boundary_gate(sm) operates on a hdlab.situation_reader.SituationModel (sm.events with
.agent/.tense/.sent_idx, sm.entities with coref .heads/.cluster, sm.causal_links with .sent_idx)
-- built by a DIFFERENT pipeline (LitBank-CoNLL SituationReader) than the plain-text SVO reader
this recall fix uses (NEST.read_corpus per-sentence). To compose the two REAL mechanisms without
reimplementing either, this cell builds a duck-typed adapter (FakeEvent/FakeEntity/
FakeCausalLink/FakeSM) that supplies is_boundary_gate() with REAL per-event signals computed by
the SAME owned readers the gate's own docstring names as its 3 available Zwaan dimensions:
  PROTAGONIST : the SVO tuple's own agent string (already produced by the frame-trigger reader;
                identity-mapped entities, since this pipeline does no cross-sentence coref
                clustering -- a real, honestly-noted difference from the gate's own richer coref
                lookup, but the SAME comparison primitive: does the agent head differ from the
                immediately preceding event's agent head).
  TIME        : experiments._temporal_ordering.extract_events(sentence_text) -- REAL tense
                extraction (SIMPLE_PAST/PAST_PERFECT/PASSIVE/MODAL_SUBORDINATE/PARTICIPIAL),
                matched to the SVO tuple's verb lemma; falls back to the sentence's first
                extracted event's tense when the frame-trigger's own lemma (TRL-normalized for
                secondary predicates) doesn't exact-match extract_events' own lemma form.
  CAUSATION   : experiments._causal_network.CAUSAL_CONNECTIVES membership test over the SAME
                tokenizer _causal_network.extract() uses -- REAL connective detection, not a
                hand-rolled word list copy.
is_boundary_gate() ITSELF is imported and called unmodified from exp_event_boundary_relevance_gate_v1.
extract_events / CAUSAL_CONNECTIVES are imported and called unmodified from their owning modules.
Only the adapter glue (mapping SVO tuples -> duck-typed sm objects) is new code.

THE FILTER: is_boundary_gate assigns True/False per event in READING ORDER across the WHOLE
corpus stream (mirrors the gate's own passage-level design: prev=None only at position 0, then
discontinuity vs the immediately preceding event in the SAME flat stream the frame-trigger
scores). Two predicates from the SAME sentence (a primary + a spurious secondary) that share
agent+tense+no-causal-shift score as NON-boundary (dropped) -- exactly the SPURIOUS-secondary-
predicate failure mode this cell targets composing away.

PRE-REGISTRATION (fixed before this cell ran; from the task spec):
  HARD-PASS : combined primary F1 > baseline F1 (0.2316) AND combined precision materially
    > frame-trigger-alone precision (0.159) [material := >=+0.05 absolute] AND combined recall
    stays >= ~0.45 (does not collapse back toward the 0.324 baseline).
  PARTIAL   : precision recovers (>=+0.05 vs frame-alone) but recall drops toward baseline
    (< 0.45) -- gate too aggressive, still report as a real but bounded gain if combined F1 still
    beats baseline F1.
  HARD-FAIL : combined F1 <= baseline F1 (0.2316) -- the two mechanisms do not compose; drill
    WHY (does the gate remove TRUE positives too? is its boundary signal, ported to this
    pipeline's weaker protagonist-identity + sentence-level tense/causal proxies, misaligned
    with per-event validity here?).
Also reported (not gating, per task step 4): TRIPLE (predicate+agent+patient) F1 for all 3 arms
-- the frame-trigger's OWN triple F1 got WORSE (0.211->0.177, secondary-predicate role errors,
a SEPARATE component) -- if combined PRIMARY improves but TRIPLE stays bad, that residual is
named explicitly, not folded into this cell's verdict.

DESIGN-GATE (verified at run time, both smoke and full):
  G1 baseline reproduction: multi_pred=False primary P/R/F1 must reproduce the frozen values
     (0.1803/0.3235/0.2316) used elsewhere in this arc, via the SAME G.score_arm/match_primary.
  G2 no-regression: exp_frame_trigger_predicate_recall_fix_v1.py --self-test and
     exp_event_boundary_relevance_gate_v1.py --self-test both pass (neither touched).
  G3 arms differ: combined kept set != frame-trigger flat set (gate actually drops >0 events);
     combined kept set != baseline flat set.
  G4 can-fail-both-ways: the gate could remove 0 spurious events (no precision gain, HARD-FAIL)
     or could remove true positives along with spurious ones (recall collapse, HARD-FAIL) -- both
     reachable; not assumed.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, <=91 short sentences (L04+L05), a trained
averaged-perceptron classifier fit on ~100 hand examples (reused, not retrained) + a handful of
POS-tag + lexical-connective passes; wall < 30s (no GloVe load needed -- this cell never scores
Score-1 content coherence, only structural/dimension discontinuity + exact gold matching).
Foreground, local, NO queue, NO push, NO remote-persist, NO network installs. Determinism:
OMP/MKL/OPENBLAS=1; no randomness anywhere in this cell's own code path.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import subprocess
import sys
import time
import traceback
from collections import namedtuple
from datetime import datetime, timezone

ANCHOR_NAME = "frame_trigger_plus_relevance_gate_combined_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_coherence_gate_extraction_correctness_independent_gold_v1 as G  # noqa: E402
from experiments import exp_frame_trigger_predicate_recall_fix_v1 as FT  # noqa: E402
from experiments import exp_event_boundary_relevance_gate_v1 as GATE  # noqa: E402
from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST  # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2  # noqa: E402
from experiments import _temporal_ordering as TORD  # noqa: E402
from experiments import _causal_network as CNET  # noqa: E402

# Frozen prior-cell numbers (independent gold, primary metric), reproduced byte-exact by G1.
FROZEN_BASELINE_P = 0.18032786885245902
FROZEN_BASELINE_R = 0.3235294117647059
FROZEN_BASELINE_F1 = 0.23157894736842105
# Frame-trigger-alone frozen numbers (from data/exp_frame_trigger_predicate_recall_fix_v1/metrics.json),
# reproduced (not byte-gated, since this cell recomputes them fresh as its own "frame_trigger" arm).
FROZEN_FRAME_P = 0.1592920353982301
FROZEN_FRAME_R = 0.5294117647058824
FROZEN_FRAME_F1 = 0.24489795918367346

FakeEvent = namedtuple("FakeEvent", ["agent", "tense", "sent_idx"])
FakeEntity = namedtuple("FakeEntity", ["heads", "cluster"])
FakeCausalLink = namedtuple("FakeCausalLink", ["sent_idx"])
FakeSM = namedtuple("FakeSM", ["events", "entities", "causal_links"])


def load_slice(slice_lessons):
    """Same corpus-slicing primitive FT.run_reader / G.load_slice_and_reader use, parametrized
    by slice (FT.run_reader hardcodes G.cfg_full(); this cell needs a smoke-vs-full slice)."""
    les = NEST.load_lessons()
    sent_text = {}
    order = []
    for lid in slice_lessons:
        for j, s in enumerate(G.split_sents(les[lid])):
            sid = f"{lid}_{j:02d}"
            sent_text[sid] = s
            order.append(sid)
    return order, sent_text


def run_reader(order, sent_text, multi_pred):
    clf = V2._fit_clf()
    passages = {sid: sent_text[sid] for sid in order}
    store = NEST.read_corpus(clf, passages, nest=True, multi_pred=multi_pred)["store"]
    reader_svo = {}
    for sid in order:
        tups = [(r[1], r[2], r[3]) for r in store.get(sid, []) if r[0] == "svo" and r[1] != "kind"]
        reader_svo[sid] = [(str(v).lower(), str(a).lower(), str(p).lower()) for (v, a, p) in tups]
    return reader_svo


def build_dimension_signals(order, sent_text):
    """Per-sentence REAL tense (via _temporal_ordering.extract_events) and causal-connective
    (via _causal_network CAUSAL_CONNECTIVES + its own tokenizer) signals, keyed by sid."""
    tense_by_lemma_per_sid = {}
    default_tense_per_sid = {}
    causal_flag_per_sid = {}
    for sid in order:
        text = sent_text[sid]
        events, toks = CNET.extract(text)  # events via TORD.extract_events under the hood
        tbl = {}
        for e in events:
            lv = G.lemma_verb(e.lemma)
            tbl.setdefault(lv, e.tense)
        tense_by_lemma_per_sid[sid] = tbl
        default_tense_per_sid[sid] = events[0].tense if events else TORD.TENSE_OTHER
        causal_flag_per_sid[sid] = any(t in CNET.CAUSAL_CONNECTIVES for t in toks)
    return tense_by_lemma_per_sid, default_tense_per_sid, causal_flag_per_sid


def apply_relevance_gate(order, sent_text, svo_frame):
    """Adapt the frame-trigger's flat (sid,tup) SVO stream into a duck-typed SituationModel and
    run the REAL exp_event_boundary_relevance_gate_v1.is_boundary_gate() over it, unmodified."""
    tense_by_lemma, default_tense, causal_flag = build_dimension_signals(order, sent_text)
    sent_idx_of = {sid: i for i, sid in enumerate(order)}

    flat = [(sid, tup) for sid in order for tup in svo_frame[sid]]
    fake_events = []
    for sid, (v, a, p) in flat:
        lv = G.lemma_verb(v)
        tense = tense_by_lemma[sid].get(lv, default_tense[sid])
        fake_events.append(FakeEvent(agent=(a if a else "?"), tense=tense, sent_idx=sent_idx_of[sid]))

    distinct_agents = sorted(set(ev.agent for ev in fake_events if ev.agent != "?"))
    fake_entities = [FakeEntity(heads=[ag], cluster=ag) for ag in distinct_agents]

    causal_sent_idxs = sorted(i for sid, i in sent_idx_of.items() if causal_flag[sid])
    fake_causal_links = [FakeCausalLink(sent_idx=i) for i in causal_sent_idxs]

    fake_sm = FakeSM(events=fake_events, entities=fake_entities, causal_links=fake_causal_links)
    preds, triggers = GATE.is_boundary_gate(fake_sm)
    assert len(preds) == len(flat)
    combined_flat = [item for item, keep in zip(flat, preds) if keep]
    dropped_flat = [(item, trig) for item, keep, trig in zip(flat, preds, triggers) if not keep]
    return flat, combined_flat, dropped_flat, preds, triggers


def run_selftest_subprocess(pyfile, extra_args):
    py = sys.executable
    try:
        cp = subprocess.run([py, pyfile] + extra_args, cwd=REPO_ROOT,
                            capture_output=True, text=True, timeout=180)
        ok = cp.returncode == 0
        msg = (cp.stdout[-400:] + cp.stderr[-400:]).strip()
        return ok, msg
    except Exception as e:  # pragma: no cover
        return False, f"{type(e).__name__}: {e}"


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def cfg_smoke():
    return {"slice_lessons": ["L04"]}


def cfg_full():
    return {"slice_lessons": ["L04", "L05"]}


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    order, sent_text = load_slice(cfg["slice_lessons"])
    gold, gold_meta = G.load_gold(cfg["slice_lessons"])

    svo_baseline = run_reader(order, sent_text, multi_pred=False)
    svo_frame = run_reader(order, sent_text, multi_pred=True)

    flat_baseline = [(sid, tup) for sid in order for tup in svo_baseline[sid]]
    prim_baseline = G.score_arm(flat_baseline, gold, G.match_primary)
    trip_baseline = G.score_arm(flat_baseline, gold, G.match_triple)

    flat_frame, flat_combined, dropped, preds, triggers = apply_relevance_gate(order, sent_text, svo_frame)
    prim_frame = G.score_arm(flat_frame, gold, G.match_primary)
    trip_frame = G.score_arm(flat_frame, gold, G.match_triple)
    prim_combined = G.score_arm(flat_combined, gold, G.match_primary)
    trip_combined = G.score_arm(flat_combined, gold, G.match_triple)

    # G1: baseline reproduction (only meaningful/asserted on the full slice, which matches the
    # frozen cell's own slice_lessons=["L04","L05"]; smoke uses L04-only so is NOT compared to
    # the frozen full-corpus numbers).
    if mode == "full":
        g1_ok = (abs(prim_baseline["precision"] - FROZEN_BASELINE_P) < 1e-9
                 and abs(prim_baseline["recall"] - FROZEN_BASELINE_R) < 1e-9
                 and abs(prim_baseline["f1"] - FROZEN_BASELINE_F1) < 1e-9)
    else:
        g1_ok = True  # not applicable on the smoke (L04-only) slice

    ok_ft, msg_ft = run_selftest_subprocess(
        os.path.join(REPO_ROOT, "experiments", "exp_frame_trigger_predicate_recall_fix_v1.py"),
        ["--self-test"])
    ok_gate, msg_gate = run_selftest_subprocess(
        os.path.join(REPO_ROOT, "experiments", "exp_event_boundary_relevance_gate_v1.py"),
        ["--self-test"])
    g2_ok = ok_ft and ok_gate

    def kept_set(flat_list):
        return set((sid, tup) for sid, tup in flat_list)

    g3_gate_drops_something = len(flat_combined) < len(flat_frame)
    g3_combined_differs_from_baseline = kept_set(flat_combined) != kept_set(flat_baseline)
    g3_ok = g3_gate_drops_something and g3_combined_differs_from_baseline

    delta_p_vs_frame = prim_combined["precision"] - prim_frame["precision"]
    beats_baseline_f1 = prim_combined["f1"] > prim_baseline["f1"]
    beats_frame_f1 = prim_combined["f1"] > prim_frame["f1"]
    precision_material_gain = delta_p_vs_frame >= 0.05
    recall_kept = prim_combined["recall"] >= 0.45

    if not (g1_ok and g2_ok and g3_ok):
        verdict = "HARD_FAIL_DESIGN_GATE_VIOLATION"
    elif prim_combined["f1"] <= prim_baseline["f1"]:
        verdict = "HARD_FAIL_NO_NET_COMPOSITION_GAIN"
    elif precision_material_gain and recall_kept and beats_baseline_f1 and beats_frame_f1:
        verdict = "HARD_PASS_COMPOSITION_NET_GAIN"
    elif precision_material_gain and beats_baseline_f1:
        verdict = "PARTIAL_PRECISION_RECOVERED_RECALL_ERODED"
    else:
        verdict = "PARTIAL_BOUNDED_COMPOSITION"

    secondary_pred_role_residual = {
        "baseline_triple_f1": trip_baseline["f1"],
        "frame_trigger_triple_f1": trip_frame["f1"],
        "combined_triple_f1": trip_combined["f1"],
        "triple_still_worse_than_baseline_after_combine": trip_combined["f1"] < trip_baseline["f1"],
        "note": ("Secondary-predicate role-assignment errors (assign_roles_learned_at mis-picking "
                 "agent/patient head for a secondary predicate in coordination/relative-clause "
                 "contexts) are a SEPARATE component from event/predicate detection (this cell's "
                 "scope) and from situation-boundary filtering (the relevance-gate's scope). The "
                 "relevance gate filters WHICH events survive, not WHAT role each surviving event's "
                 "arguments get -- it cannot fix a wrong (agent,patient) pairing that primary-metric "
                 "matching (verb+patient only) does not surface. If combined TRIPLE F1 is still below "
                 "baseline, that residual routes to the role-assignment fix, not to this composition."),
    }

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} "
           f"| BASELINE P={prim_baseline['precision']:.4f} R={prim_baseline['recall']:.4f} "
           f"F1={prim_baseline['f1']:.4f} n_pred={prim_baseline['n_pred']} "
           f"| FRAME_TRIGGER P={prim_frame['precision']:.4f} R={prim_frame['recall']:.4f} "
           f"F1={prim_frame['f1']:.4f} n_pred={prim_frame['n_pred']} "
           f"| COMBINED P={prim_combined['precision']:.4f} R={prim_combined['recall']:.4f} "
           f"F1={prim_combined['f1']:.4f} n_pred={prim_combined['n_pred']} "
           f"| dP(combined-frame)={delta_p_vs_frame:+.4f} "
           f"| TRIPLE base={trip_baseline['f1']:.4f} frame={trip_frame['f1']:.4f} "
           f"combined={trip_combined['f1']:.4f} "
           f"| gate_dropped={len(dropped)}/{len(flat_frame)} "
           f"| G1={g1_ok} G2={g2_ok}(ft={ok_ft} gate={ok_gate}) G3={g3_ok} "
           f"| beats_baseline_f1={beats_baseline_f1} beats_frame_f1={beats_frame_f1} "
           f"precision_material_gain={precision_material_gain} recall_kept={recall_kept}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg,
        "arms": {
            "baseline": {"primary": prim_baseline, "triple": trip_baseline},
            "frame_trigger": {"primary": prim_frame, "triple": trip_frame},
            "combined": {"primary": prim_combined, "triple": trip_combined},
        },
        "frozen_reference": {
            "baseline": {"precision": FROZEN_BASELINE_P, "recall": FROZEN_BASELINE_R, "f1": FROZEN_BASELINE_F1},
            "frame_trigger": {"precision": FROZEN_FRAME_P, "recall": FROZEN_FRAME_R, "f1": FROZEN_FRAME_F1},
        },
        "design_gate": {
            "G1_baseline_reproduction": g1_ok, "G1_checked": (mode == "full"),
            "G2_no_regression": g2_ok,
            "G2_frame_trigger_selftest": {"ok": ok_ft, "tail": msg_ft},
            "G2_relevance_gate_selftest": {"ok": ok_gate, "tail": msg_gate},
            "G3_arms_differ": g3_ok,
            "G3_gate_drops_something": g3_gate_drops_something,
            "G3_combined_differs_from_baseline": g3_combined_differs_from_baseline,
        },
        "delta_precision_combined_vs_frame": delta_p_vs_frame,
        "beats_baseline_f1": beats_baseline_f1,
        "beats_frame_f1": beats_frame_f1,
        "precision_material_gain_ge_0.05": precision_material_gain,
        "recall_kept_ge_0.45": recall_kept,
        "gate_dropped_examples": [[sid, list(tup), trig] for (sid, tup), trig in dropped[:20]],
        "n_gate_dropped": len(dropped), "n_frame_flat": len(flat_frame),
        "secondary_pred_role_residual": secondary_pred_role_residual,
        "REQUIRED_FIELDS": ["verdict", "arms", "design_gate", "secondary_pred_role_residual",
                            "delta_precision_combined_vs_frame", "beats_baseline_f1", "beats_frame_f1"],
        "notes": ("Composes exp_frame_trigger_predicate_recall_fix_v1 (recall via multi-predicate "
                  "frame-lookup trigger) with exp_event_boundary_relevance_gate_v1 (precision via "
                  "Zwaan-dimension situation-boundary filter), reusing both mechanisms unmodified "
                  "through a duck-typed adapter (real tense via _temporal_ordering.extract_events, "
                  "real causal-connective detection via _causal_network.CAUSAL_CONNECTIVES). See "
                  "module docstring for the full pre-registration and the adapter's honest "
                  "limitations (identity-mapped protagonist entities, sentence-level tense/causal "
                  "granularity -- this pipeline has no cross-sentence coref clustering like the "
                  "gate's native SituationReader path)."),
    }
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        # cheap wiring self-test: 3 synthetic events, hand-verified expected boundary pattern.
        # ev0 Herbert/SIMPLE_PAST/sent0 (segment_start, always True)
        # ev1 Herbert/SIMPLE_PAST/sent0 (SAME agent+tense+no-causal as ev0 -> non-boundary, dropped)
        # ev2 Mary/SIMPLE_PAST/sent1 (agent shift -> boundary, kept)
        fake_events = [
            FakeEvent(agent="herbert", tense="SIMPLE_PAST", sent_idx=0),
            FakeEvent(agent="herbert", tense="SIMPLE_PAST", sent_idx=0),
            FakeEvent(agent="mary", tense="SIMPLE_PAST", sent_idx=1),
        ]
        fake_entities = [FakeEntity(heads=["herbert"], cluster="herbert"),
                          FakeEntity(heads=["mary"], cluster="mary")]
        fake_sm = FakeSM(events=fake_events, entities=fake_entities, causal_links=[])
        preds, triggers = GATE.is_boundary_gate(fake_sm)
        assert preds == [True, False, True], f"self-test: expected [T,F,T], got {preds}"
        assert triggers[1] == [], f"self-test: expected no dims fired for the repeat, got {triggers[1]}"
        assert "protagonist" in triggers[2], f"self-test: expected protagonist trigger, got {triggers[2]}"
        # real-tense/causal-signal wiring smoke: a real sentence must round-trip through CNET/TORD.
        events, toks = CNET.extract("Herbert took the block and threw it because he was angry.")
        assert any(e.tense == "SIMPLE_PAST" for e in events)
        assert "because" in toks and "because" in CNET.CAUSAL_CONNECTIVES
        print(f"[{ANCHOR_NAME}] self-test PASS: adapter preds={preds} triggers={triggers}", flush=True)
        return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
