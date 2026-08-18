"""DEMONSTRABLY-FINISHED MULTI-SENTENCE SITUATION-MODEL READER -- DEMONSTRATION (v1).

ONE runnable that reads REAL multi-sentence LitBank passages and outputs the SituationModel
(entities / events / timeline / causal links, all held in a Cowan-4 focus), with HONEST
per-dimension accuracy + glass-box traces + a cross-sentence CAN-FAIL validity gate. This is
the MULTI-SENTENCE analog of the single-sentence "demonstrably finished" deliverable (29502):
ONE reader, real text in, structured situation-model out, honest accuracy, glass-box.

CONSOLIDATION, NOT a new capability. The reader = hdlab/situation_reader.py, which COMPOSES the
already-banked modules (no new mechanism): coref backbone (EventCentralityReader 29516 recency-
centrality, decision-driving memory; inherits scene-locality 29514 + never-a-subject 29513 +
WorkingOverlay 29506; deixis-person hygiene 29517), event role-slot BUNDLES (event_bundle 29511)
in a bounded Cowan-4 focus (situation_focus 29512 no-runaway), TIME chronology (temporal
multiframe 29510), CAUSATION (causal-network 29515). The win = it RUNS end-to-end on real text +
honest accuracy + glass-box + the cross-sentence validity gate fires; NOT a capability claim
beyond the banked components. Composed accuracy is modest (coref ~0.45 propagates) -- reported
DEFLATED per the no-smoke discipline.

DIMENSIONS + HOW EACH IS SCORED (each on ITS proper gold -- honest):
  ENTITIES/COREF : REAL, scored vs LitBank coref gold on ALL demo books. Overall accuracy +
                   cross-sentence subset accuracy. CAN-FAIL VALIDITY GATE = the single-sentence
                   baseline is STRUCTURALLY BLIND cross-sentence (== 0.0 on the xsent subset),
                   the established gate (29506): these pronouns GENUINELY need cross-sentence state.
  EVENTS/ROLES   : predicate+agent+patient extracted glass-box on the passages (shown qualitatively).
                   The calibrated single-sentence role reader F1 is CITED (roles vs gold where
                   available); NOT re-scored on LitBank (no LitBank role gold). Honest.
  TIME           : MECH (tense+connective chronology) vs TEXT-order baseline on the banked REAL
                   LitBank flashback gold (29510). Validity gate = TEXT low on flashbacks.
  CAUSATION      : CAUSAL_NET vs MOST_RECENT (locality) baseline on the banked REAL LitBank causal
                   gold (29515). Validity gate = MOST_RECENT fails on non-adjacent causes (inverse
                   of coref). HONEST CAVEAT (carried from the 29515 VET, re-derived here): the
                   mechanism is REDUCIBLE to connective-else-most-recent; causal-plausibility
                   reasoning is UNPROVEN. Reported, not hidden.
  MEMORY         : recent (direct) event role-query round-trip in the Cowan-4 focus (glass-box
                   unbind + cleanup). Capacity-limited (Cowan-4 graceful forgetting, 29511) --
                   reported honestly, not as perfect recall.

PRE-REGISTERED BANDS (set BEFORE this run; a DEMONSTRATION/consolidation cell -- "PASS" = it
  composes, runs on real text, honest accuracy, and the validity gate fires; it is NOT a new
  capability claim):
  DEMO_COMPOSES        : every demo book read end-to-end with NO crash; each SituationModel has
                         entities > 0 AND events > 0 AND (n_targets > 0 for books with pronouns).
  COREF_REAL_IN_BAND   : 0.30 <= overall coref acc <= 0.60 (consistent w/ banked ~0.45; NOT
                         saturated >0.95, NOT floor <0.05).
  VALIDITY_GATE_FIRES  : single-sentence baseline acc on the xsent subset == 0.0 (structurally
                         blind) AND TEXT-order timeline acc on flashback gold < MECH acc.
  TIMELINE_REAL        : MECH acc - TEXT acc on HARD_GOLD >= 0.15 (reproduces 29510).
  CAUSATION_REAL       : CAUSAL_NET acc - MOST_RECENT acc on the hard subset >= 0.15 (reproduces
                         29515) AND the reducibility flag is REPORTED.
  MEMORY_GLASSBOX      : recent-event round-trip rate >= 0.5 (well above chance; Cowan-4).
  FAIL bands           : any read() crash; coref acc >0.95 (saturated) or <0.05 (floor); single-
                         sentence xsent acc > 0.05 (validity gate did not fire); TIMELINE or
                         CAUSATION margin <= 0 (mechanism did not beat baseline).
  VERDICT: DEMONSTRATED iff ALL of {DEMO_COMPOSES, COREF_REAL_IN_BAND, VALIDITY_GATE_FIRES,
    TIMELINE_REAL, CAUSATION_REAL, MEMORY_GLASSBOX}. Else PARTIAL (report which hold) or FAIL.

FAIRNESS: coref scored on held-out LitBank gold (reader never sees gold coref linking; 29506
  anti-circular). TIME/CAUSATION on the banked REAL LitBank gold (source-cited, non-circular).
  Baselines are GENUINE can-fail baselines (single-sentence = structurally blind; TEXT-order =
  no tense; MOST_RECENT = locality). ONE variable per dimension.

BRAIN-CHECK: Kintsch/van-Dijk construction-integration + Zwaan event-indexing -- a persistent
  situation model over PROTAGONIST/TIME/CAUSATION updated incrementally per sentence, entities as
  the reference backbone. Each dimension's baseline is the corresponding null (linear order / text
  order / adjacency); the reader uses discourse structure, as the human reader does.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- per-book symbolic coref +
  small HD event-memory unbind/cleanup (n_dim=4096, Cowan-4); NO SGD/training/GPU-batchable
  primitive; ~1s/book after torch warmup, wall < 2 min for all 25 books + the two gold-scored
  dimensions. Storage: sharded event codevectors in a bounded ChunkedFocus (no bundled-composition
  collapse; 29512). Determinism: OMP/MKL/OPENBLAS=1, fixed seeds, no hash()-seeded RNG.
  LOCAL-ONLY, foreground-to-completion. NO push / NO remote-persist / NO queue_add (routing task
  contract: inline-local FULL, not banked -- skunkworks VETs + banks separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground demonstration cell):
  - arms_differ_verified at smoke (hash over MECH vs TEXT timeline signatures + CAUSAL_NET vs
    MOST_RECENT cause picks; single-sentence vs cross-sentence coref decisions)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band: coref not saturated/floor; TEXT/MOST_RECENT can fail (validity gate)
  - discriminator fires: single-sentence == 0 on xsent; MECH > TEXT; CAUSAL_NET > MOST_RECENT
  - glass-box: full SituationModel printed for 2 books (entities w/ cross-sentence mentions,
    events w/ roles, timeline reorderings, causal links, memory round-trip)
  - deterministic seeding (fixed int seeds; sorted book order)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (roles F1 0.64 from 29502; component
    banked accuracies) in this docstring / at print time
  - N/A CRLB (discrete count/accuracy, no HD noise floor on the discrete decisions); N/A multi-seed
    (deterministic given fixed seeds; the coref/HD decisions are deterministic)
  - progress_logging: print_flush_true (stdout line-buffered)

CITED anchors:
  - roles single-sentence F1 ~0.64  CITED@notes/multi_sentence_situation_model_plan_2026-07-24.md
    (29502 consolidated reader; F1 0.5738 base -> 0.6423 do/have; McGuffey LCCP gold)
  - coref recency-centrality plateau ~0.45  CITED@29516 (event_centrality; same-gender subset 0.4523)
  - TIME MECH beats TEXT/PP_DEMOTE on real flashbacks  CITED@29510
  - CAUSATION locality-fails-on-non-adjacent + REDUCIBLE-to-connective-else-recency  CITED@29515
  - Cowan-4 recent round-trip + graceful forgetting  CITED@29511 / 29512
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader  # noqa: E402
from experiments import _causal_network as C  # noqa: E402
from experiments import exp_read_temporal_multiframe_chronology_v1 as TMF  # noqa: E402
from experiments import exp_read_causal_chain_on_chain_cause_v1 as CAU  # noqa: E402

ANCHOR_NAME = "situation_reader_multisent_demo_v1"
CORPUS_DIR = os.path.join(_REPO, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 3
ROLE_F1_CITED = 0.6423  # CITED@29502 do/have consolidated single-sentence reader (McGuffey LCCP)


def _p(msg):
    print(msg, flush=True)


def _out_dir(mode):
    d = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# DIMENSION SCORERS (each on ITS proper banked gold)
# ---------------------------------------------------------------------------
def score_timeline():
    """TIME: MECH (tense+connective chronology) vs TEXT-order on banked REAL flashback gold."""
    flash = [g for g in TMF.HARD_GOLD if g.get("type") == "C" and g.get("risk") == "real"]
    mech = TMF._score_subset("MECH", TMF.HARD_GOLD)
    text = TMF._score_subset("TEXT", TMF.HARD_GOLD)
    mech_flash = TMF._score_subset("MECH", flash)
    text_flash = TMF._score_subset("TEXT", flash)
    sig_mech = hashlib.sha256(TMF._arm_signature("MECH", TMF.HARD_GOLD)).hexdigest()
    sig_text = hashlib.sha256(TMF._arm_signature("TEXT", TMF.HARD_GOLD)).hexdigest()
    return {
        "mech_acc": round(mech["acc"], 4), "text_acc": round(text["acc"], 4),
        "margin": round(mech["acc"] - text["acc"], 4),
        "mech_flashback_acc": round(mech_flash["acc"], 4),
        "text_flashback_acc": round(text_flash["acc"], 4),
        "n_hard_pairs": mech["n_scored"], "n_flashback_items": len(flash),
        "arms_differ": sig_mech != sig_text,
    }


def score_causation():
    """CAUSATION: CAUSAL_NET vs MOST_RECENT on banked REAL causal gold + reducibility check."""
    gold = CAU.GOLD
    hard = [g for g in gold if g.subset in ("NONADJ", "BRIDGE")]

    def arm_acc(arm, items):
        ok = 0
        for it in items:
            events, low = C.extract(it.text)
            outcome = C._find_event(events, it.outcome_lemma)
            if outcome is None:
                continue
            pred = C.predict_cause(arm, events, low, outcome)
            ok += int(pred is not None and pred.lemma == it.cause_lemma)
        return ok / len(items) if items else 0.0

    net = arm_acc("CAUSAL_NET", hard)
    mr = arm_acc("MOST_RECENT", hard)
    net_nonadj = arm_acc("CAUSAL_NET", [g for g in gold if g.subset == "NONADJ"])
    mr_nonadj = arm_acc("MOST_RECENT", [g for g in gold if g.subset == "NONADJ"])
    # REDUCIBILITY (29515 crux): does connective-else-most-recent match CAUSAL_NET exactly?
    mism = 0
    for it in gold:
        events, low = C.extract(it.text)
        outcome = C._find_event(events, it.outcome_lemma)
        if outcome is None:
            continue
        net_pred = C.predict_cause("CAUSAL_NET", events, low, outcome)
        conn = C.connective_cause(events, low, outcome)
        disj = conn if conn is not None else C.most_recent_prior(events, outcome)
        a = net_pred.lemma if net_pred is not None else None
        b = disj.lemma if disj is not None else None
        mism += int(a != b)
    return {
        "causal_net_hard_acc": round(net, 4), "most_recent_hard_acc": round(mr, 4),
        "margin": round(net - mr, 4),
        "most_recent_nonadj_acc": round(mr_nonadj, 4),
        "causal_net_nonadj_acc": round(net_nonadj, 4),
        "n_hard": len(hard),
        "reducible_to_connective_else_recency": (mism == 0),
        "reducibility_mismatches": mism,
        "arms_differ": net != mr,
    }


# ---------------------------------------------------------------------------
# glass-box SituationModel pretty-print
# ---------------------------------------------------------------------------
def print_situation_model(sm, max_entities=8, max_events=12, max_timeline=4, max_causal=4):
    _p("=" * 78)
    _p(f"SITUATION MODEL  |  passage={sm.passage_id}  |  sentences={sm.n_sentences}")
    _p("-" * 78)
    _p(f"[COREF/entities] acc={_f(sm.coref_acc)}  xsent_acc={_f(sm.coref_xsent_acc)}  "
       f"single_sentence_xsent={_f(sm.single_sentence_xsent_acc)} (validity baseline)  "
       f"n_targets={sm.n_targets}  n_xsent={sm.n_xsent_targets}")
    persons = [e for e in sm.entities if e.is_person][:max_entities]
    for e in persons:
        _p(f"    ENTITY c{e.cluster:<3d} PERSON  heads={e.heads[:4]}  "
           f"sents={e.sent_indices[:8]}  n_mentions={e.n_mentions}")
    # a few resolved cross-sentence pronouns (glass-box coref decision)
    xs = [r for r in sm.coref_resolutions if r.sent_dist >= 1][:5]
    for r in xs:
        _p(f"    COREF  '{r.pronoun}'@S{r.sent_idx} -> cluster c{r.resolved_cluster} "
           f"(gold c{r.gold_cluster}, dist={r.sent_dist}) {'OK' if r.correct else 'MISS'}")
    _p(f"[EVENTS] n_events={len(sm.events)} (predicate+agent+patient per clause; glass-box)")
    for ev in sm.events[:max_events]:
        _p(f"    EVENT g{ev.global_idx:<3d} S{ev.sent_idx:<2d} "
           f"{ev.agent} --[{ev.predicate}/{ev.tense}]--> {ev.patient}")
    _p(f"[TIME] n_flashback_frames={len(sm.timeline_frames)} (past-perfect / connective; "
       f"chrono reconstruction)")
    for tf in sm.timeline_frames[:max_timeline]:
        tag = "REORDERED" if tf.reordered else "linear"
        _p(f"    S{tf.sent_idx:<2d} [{tag}] text_order={tf.text_order}  chrono={tf.chrono_order}")
    _p(f"[CAUSATION] n_links={len(sm.causal_links)} (connective/adjacency-derived; "
       f"plausibility NOT isolated -- 29515 caveat)")
    for cl in sm.causal_links[:max_causal]:
        _p(f"    S{cl.sent_idx:<2d} CAUSE '{cl.cause}' -> OUTCOME '{cl.outcome}' [{cl.method}]")
    rt = sm.memory_roundtrip
    _p(f"[MEMORY] Cowan-4 focus round-trip: recent(direct) events={rt['n_direct_events']} "
       f"probes={rt['n_probes']} recovered={rt['n_ok']} rate={rt['roundtrip_rate']:.3f} "
       f"(glass-box unbind+cleanup; capacity-limited forgetting)")
    _p("=" * 78)


def _f(x):
    return "n/a" if x is None else f"{x:.3f}"


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def run(mode):
    out_dir = _out_dir(mode)
    _write_start_marker(out_dir, mode)
    books = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.conll")))
    books = [b for b in books if os.path.getsize(b) > 1000]
    if mode == "smoke":
        books = books[:SMOKE_N]
    _p(f"[run] mode={mode}  n_books={len(books)}")

    reader = SituationReader()
    models = []
    n_correct = n_tgt = n_xs_correct = n_xs = ss_xs_correct = 0
    n_events_total = n_entities_total = 0
    rt_ok = rt_probes = 0
    crashed = []
    t0 = time.time()
    for i, path in enumerate(books):
        try:
            sm = reader.read(path)
        except Exception as e:  # per-book failure-class instrumentation (no silent continue)
            crashed.append({"book": os.path.basename(path), "err": f"{type(e).__name__}: {e}"})
            _p(f"[BOOK-CRASH] {os.path.basename(path)}: {type(e).__name__}: {e}")
            continue
        models.append(sm)
        n_entities_total += len(sm.entities)
        n_events_total += len(sm.events)
        for r in sm.coref_resolutions:
            n_tgt += 1
            n_correct += int(r.correct)
            if r.sent_dist >= 1:
                n_xs += 1
                n_xs_correct += int(r.correct)
        # single-sentence baseline on xsent (validity gate) recomputed from per-book acc
        if sm.n_xsent_targets and sm.single_sentence_xsent_acc is not None:
            ss_xs_correct += round(sm.single_sentence_xsent_acc * sm.n_xsent_targets)
        rt = sm.memory_roundtrip
        rt_ok += rt["n_ok"]
        rt_probes += rt["n_probes"]
        _p(f"  [{i+1:2d}/{len(books)}] {sm.passage_id[:34]:36s} "
           f"ent={len(sm.entities):3d} ev={len(sm.events):3d} tgt={sm.n_targets:3d} "
           f"coref={_f(sm.coref_acc)} ss_xsent={_f(sm.single_sentence_xsent_acc)} "
           f"tl={len(sm.timeline_frames):2d} cz={len(sm.causal_links):2d}")
    elapsed = time.time() - t0

    if crashed:
        raise RuntimeError(f"DEMO_COMPOSES FAIL: {len(crashed)} book(s) crashed: {crashed}")

    coref_acc = n_correct / n_tgt if n_tgt else 0.0
    coref_xsent_acc = n_xs_correct / n_xs if n_xs else 0.0
    ss_xsent_acc = ss_xs_correct / n_xs if n_xs else 0.0
    rt_rate = rt_ok / rt_probes if rt_probes else 0.0

    # per-dimension gold scoring (banked)
    tl = score_timeline()
    cz = score_causation()

    # ---- glass-box: print 2 full situation models (richest coverage) ----
    rich = sorted(models, key=lambda s: -(s.n_targets + len(s.timeline_frames) + len(s.causal_links)))
    _p("")
    _p("################ GLASS-BOX SITUATION-MODEL OUTPUTS (2 real passages) ################")
    for sm in rich[:2]:
        print_situation_model(sm)

    # ---- verdict ----
    demo_composes = (len(crashed) == 0 and n_entities_total > 0 and n_events_total > 0
                     and n_tgt > 0)
    coref_in_band = 0.30 <= coref_acc <= 0.60
    validity_gate = (ss_xsent_acc == 0.0 and n_xs > 0
                     and tl["text_flashback_acc"] < tl["mech_flashback_acc"])
    timeline_real = tl["margin"] >= 0.15
    causation_real = cz["margin"] >= 0.15
    memory_glassbox = rt_rate >= 0.5

    gates = {
        "DEMO_COMPOSES": demo_composes,
        "COREF_REAL_IN_BAND": coref_in_band,
        "VALIDITY_GATE_FIRES": validity_gate,
        "TIMELINE_REAL": timeline_real,
        "CAUSATION_REAL": causation_real,
        "MEMORY_GLASSBOX": memory_glassbox,
    }
    all_pass = all(gates.values())
    verdict = "DEMONSTRATED" if all_pass else "PARTIAL"
    verdict_msg = (
        f"multi-sentence situation reader {verdict}: composes={demo_composes} "
        f"coref={coref_acc:.3f}(band[.30,.60]={coref_in_band}) "
        f"validity_gate(ss_xsent={ss_xsent_acc:.3f}==0)={validity_gate} "
        f"TIME margin={tl['margin']:+.3f}(MECH {tl['mech_acc']:.3f} vs TEXT {tl['text_acc']:.3f}) "
        f"CAUSE margin={cz['margin']:+.3f}(NET {cz['causal_net_hard_acc']:.3f} vs "
        f"MR {cz['most_recent_hard_acc']:.3f}; reducible={cz['reducible_to_connective_else_recency']}) "
        f"memory_rt={rt_rate:.3f}")

    # arms_differ self-test (MECH vs TEXT timeline; CAUSAL_NET vs MOST_RECENT; ss vs xsent)
    arms_differ_verified = tl["arms_differ"] and cz["arms_differ"] and (ss_xsent_acc != coref_xsent_acc)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {sum(gates.values())}/{len(gates)} gates",
        "elapsed_s": round(elapsed, 2),
        "anchor_name": ANCHOR_NAME,
        "mode": mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_books": len(books),
        "gates": gates,
        "arms_differ_verified": bool(arms_differ_verified),
        "coref": {
            "overall_acc": round(coref_acc, 4), "n_targets": n_tgt,
            "xsent_acc": round(coref_xsent_acc, 4), "n_xsent": n_xs,
            "single_sentence_xsent_acc": round(ss_xsent_acc, 4),
            "validity_gate_fires": validity_gate,
            "note": "single-sentence baseline structurally blind cross-sentence (29506 gate)",
        },
        "roles": {
            "single_sentence_f1_CITED": ROLE_F1_CITED,
            "source": "29502 do/have consolidated reader, McGuffey LCCP gold",
            "note": "extracted+shown glass-box on LitBank; NOT re-scored (no LitBank role gold)",
        },
        "timeline": tl,
        "causation": cz,
        "memory": {
            "roundtrip_rate": round(rt_rate, 4), "n_ok": rt_ok, "n_probes": rt_probes,
            "note": "Cowan-4 focus recent-event round-trip; capacity-limited forgetting (29511)",
        },
        "totals": {"n_entities": n_entities_total, "n_events": n_events_total,
                   "n_situation_models": len(models)},
        "honest_frame": ("CONSOLIDATION + DEMONSTRATION of banked modules, NOT a new capability. "
                         "Composed accuracy modest (coref ~0.45 propagates). Causation REDUCIBLE "
                         "to connective-else-recency (plausibility NOT isolated, 29515)."),
    }
    _write_metrics(out_dir, metrics)
    _p("")
    _p("################ VERDICT ################")
    for g, v in gates.items():
        _p(f"  {'PASS' if v else 'FAIL'}  {g}")
    _p(verdict_msg)
    _p(f"[metrics] {os.path.join(out_dir, 'metrics.json')}")
    return metrics


# ---------------------------------------------------------------------------
# infra (start-marker, atomic metrics, crash diagnostic)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def self_test():
    """Real code path: run the demo on the smoke slice + assert the composed dimensions fire."""
    _p("[self-test] running smoke demo (real code path: read() on real LitBank books) ...")
    m = run("smoke")
    assert m["totals"]["n_situation_models"] >= 1, m
    assert m["coref"]["n_targets"] > 0, "no coref targets"
    assert m["coref"]["single_sentence_xsent_acc"] == 0.0, \
        f"validity gate broken: ss_xsent={m['coref']['single_sentence_xsent_acc']}"
    assert m["timeline"]["margin"] >= 0.15, f"TIME margin: {m['timeline']}"
    assert m["causation"]["margin"] >= 0.15, f"CAUSE margin: {m['causation']}"
    assert m["timeline"]["arms_differ"] and m["causation"]["arms_differ"], "arms identical"
    _p("[self-test] PASSED: dimensions compose; validity gate fires; mechanisms beat baselines.")
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, e)
        raise
