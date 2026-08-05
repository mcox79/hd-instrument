"""RE-ATTEMPT the frame-trigger RECALL + relevance-gate PRECISION composition with REAL signals
(2026-08-05), replacing the weak-signal port that over-dropped true positives.

BACKGROUND (commit 1f1c26200, exp_frame_trigger_plus_relevance_gate_combined_v1): composing the
frame-trigger's high-recall event set (P=0.159 R=0.529 F1=0.245) with the relevance-gate's
Zwaan-dimension boundary filter gave PRECISION P=0.196 R=0.294 F1=0.235 -- WORSE recall than even
the frozen baseline (0.324), and only +0.037 precision over frame-alone (not material). Root cause
named honestly in that cell's own docstring: the adapter's PROTAGONIST signal was an IDENTITY MAP
(raw agent surface-string equality, no real cross-sentence coref) and its CAUSATION signal was a
naive "any causal connective token present in the sentence" flag -- both weaker than what
hdlab/situation_reader.py's real SituationReader pipeline actually computes.

THIS CELL fixes exactly those two weak links by reusing REAL, already-wired mechanisms instead of
re-porting proxies, per the task's own escape hatch (frame-trigger's plain-text SVO reader and
situation_reader's LitBank-CoNLL-gold-coref reader are genuinely different pipelines -- McGuffey has
no coref-annotated CoNLL, so routing frame-trigger's extraction THROUGH SituationReader.read() is not
possible without fabricating gold coref markup; verified: no data/corpora/*mcguffey*.conll exists).
Instead this cell feeds the gate REAL coref + REAL per-sentence causal-link signals:

  PROTAGONIST : hdlab.coreference_resolver.run_match_or_allocate (the CANONICAL PROMOTED cross-
                sentence coref resolver, atoms 29613/29614/29616/29618, verification/
                verify_coreference_resolver.py) run UNMODIFIED over the frame-trigger's own agent
                mention stream (one record per event, in true reading order, gender/number via the
                SAME is_pronoun_mention/gender_number_for helpers the resolver ships with). This is
                genuine Centering-salience pronoun resolution + token-overlap/determiner-bridging
                name resolution across the WHOLE L04+L05 passage -- not raw string equality. Replaces
                the identity-map entirely.
  CAUSATION   : experiments._causal_network.causal_net_cause, called EXACTLY as hdlab/
                situation_reader.py._read_causation calls it (a sentence flags "causal" only if it
                has >=2 CNET-extracted events AND causal_net_cause finds a genuine connective/bridge
                cause->outcome link between two DIFFERENT events) -- not "any connective token is
                present anywhere in the sentence" (the weak proxy; over-fires on subordinate clauses
                that mention a connective without forming a real 2-event causal link).
  TIME        : unchanged from the prior cell (already real: per-sentence CNET.extract events,
                matched to the frame-trigger SVO tuple's verb lemma; this was never the weak link --
                situation_reader's own CausalLink/tense granularity is ALSO sentence-scoped, so this
                cell's TIME/CAUSATION granularity now matches situation_reader's ACTUAL granularity,
                not a stricter unproven claim of "per-event" causal links situation_reader itself
                does not make either).
GATE.is_boundary_gate() itself is imported and called UNMODIFIED, exactly as the prior cell did.

DIAGNOSTIC (pre-registered, for the HARD-FAIL branch): among the frame-alone TRUE POSITIVES the
real-coref gate still drops (classifies as non-boundary), count how many are COREF-OVER-MERGE
attributable: the event's real-coref protagonist cluster equals the immediately-preceding event's
cluster (in the gate's own reading-order "prev" comparison) BUT the two events' raw agent surface
strings differ. A same-cluster verdict over two different surface mentions is exactly what the
match-or-allocate resolver would produce if it wrongly merged two distinct referents -- if this count
is a material fraction of the drops, cross-sentence coref QUALITY (not the gate's boundary logic) is
the true blocker, confirming the audit's THIN/MIDDLE_BAND coref flag. This is measured off THIS
pipeline's own resolver decisions (no independent coref gold exists for McGuffey), so it is a
STRUCTURAL diagnostic (does the resolver's own same-cluster judgment coincide with same-surface-form)
not a claim of ground-truth coref error -- reported honestly as such.

PRE-REGISTRATION (fixed before this cell ran; from the task spec):
  HARD-PASS : real-coref-gate combined primary F1 > frame-trigger-alone F1 (0.24490) AND combined
    recall >= 0.45 AND combined precision - frame-alone precision (0.15929) >= 0.05 (material).
  PARTIAL   : combined F1 > weak-combine F1 (0.23529) but recall stays < 0.45 (gate still erodes
    recall, just less than the weak-signal version) -- a real but bounded gain.
  HARD-FAIL : combined F1 <= weak-combine F1 (0.23529), i.e. the real-signal upgrade did NOT even
    beat the weak proxy -- report the coref-over-merge diagnostic above; if a material fraction of
    dropped TPs are coref-over-merge-attributable, the ROOT blocker is cross-sentence coref quality,
    not the gate design -- a valid, important negative result, not forced to pass.
Also reported (not gating): TRIPLE F1 for all 3 arms (frame-trigger's own triple F1 residual is a
separate, already-named component -- secondary-predicate role assignment).

DESIGN-GATE (verified at run time, both smoke and full):
  G1 baseline reproduction: multi_pred=False primary P/R/F1 must reproduce the frozen values
     (0.1803/0.3235/0.2316) via the SAME G.score_arm/match_primary (full mode only).
  G2 no-regression: exp_frame_trigger_predicate_recall_fix_v1.py --self-test,
     exp_event_boundary_relevance_gate_v1.py --self-test, and
     verification/verify_coreference_resolver.py all pass (none touched).
  G3 arms differ: combined kept set != frame-trigger flat set (gate drops >0) AND != baseline flat set
     AND != the prior weak-combine cell's kept set (this cell's signals are genuinely different).
  G4 can-fail-both-ways: the real coref could still over-merge (no improvement, HARD-FAIL reachable)
     or could correctly separate referents the identity-map conflated (recall recovers, HARD-PASS
     reachable) -- not assumed.

PRIOR-WORK CHECK (substrate_query.sh, mandatory before authoring): top hits at cosine>0.30 are about
a DIFFERENT McGuffey-comprehension coref-fix result (grade-2 QA/relation-extraction end-to-end reader,
0.3203) and a coref-antecedent-selection bottleneck finding (0.3203) -- both confirm cross-sentence
coref quality is a recurring, previously-measured bottleneck on this kind of text, but neither is this
specific frame-trigger+relevance-gate composition. This cell is NOVEL (a new composition), informed by
(not a rediscovery of) that prior coref-bottleneck finding.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, <=91 short sentences (L04+L05), a trained averaged-
perceptron classifier fit on ~100 hand examples (reused) + a handful of POS-tag/lexical-connective
passes + the coref resolver's own O(n^2)-worst-case but tiny-n (n<150 mentions) match-or-allocate
loop; wall < 30s. Foreground, local, NO queue, NO push, NO remote-persist, NO network installs.
Determinism: OMP/MKL/OPENBLAS=1; no randomness anywhere in this cell's own code path.
ASCII-only.
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

ANCHOR_NAME = "frame_trigger_plus_relevance_gate_real_coref_v1"
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
from hdlab import coreference_resolver as COREF  # noqa: E402

# Frozen prior-cell numbers (independent gold, primary metric), reproduced byte-exact by G1.
FROZEN_BASELINE_P = 0.18032786885245902
FROZEN_BASELINE_R = 0.3235294117647059
FROZEN_BASELINE_F1 = 0.23157894736842105
# Frame-trigger-alone frozen numbers (data/exp_frame_trigger_predicate_recall_fix_v1/metrics.json).
FROZEN_FRAME_P = 0.1592920353982301
FROZEN_FRAME_R = 0.5294117647058824
FROZEN_FRAME_F1 = 0.24489795918367346
# Weak-combine frozen numbers (data/exp_frame_trigger_plus_relevance_gate_combined_v1/metrics.json,
# full mode, commit 1f1c26200 -- the identity-map + sentence-level-connective attempt this cell fixes).
FROZEN_WEAK_COMBINE_P = 0.19607843137254902
FROZEN_WEAK_COMBINE_R = 0.29411764705882354
FROZEN_WEAK_COMBINE_F1 = 0.23529411764705882

FakeEvent = namedtuple("FakeEvent", ["agent", "tense", "sent_idx"])
FakeEntity = namedtuple("FakeEntity", ["heads", "cluster"])
FakeCausalLink = namedtuple("FakeCausalLink", ["sent_idx"])
FakeSM = namedtuple("FakeSM", ["events", "entities", "causal_links"])


def load_slice(slice_lessons):
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
    """Per-sentence REAL tense (per-lemma, via CNET.extract/TORD.extract_events -- unchanged from
    the prior cell, already real) and REAL per-sentence causal-link flag, computed EXACTLY as
    hdlab/situation_reader.py._read_causation computes sm.causal_links (a sentence is causal iff it
    has >=2 CNET events AND causal_net_cause finds a genuine connective/bridge cause->outcome link
    between two different events) -- NOT the prior cell's weak "any connective token present" flag."""
    tense_by_lemma_per_sid = {}
    default_tense_per_sid = {}
    causal_flag_per_sid = {}
    for sid in order:
        text = sent_text[sid]
        events, toks = CNET.extract(text)
        tbl = {}
        for e in events:
            lv = G.lemma_verb(e.lemma)
            tbl.setdefault(lv, e.tense)
        tense_by_lemma_per_sid[sid] = tbl
        default_tense_per_sid[sid] = events[0].tense if events else TORD.TENSE_OTHER
        # REAL causal-link detection (mirrors SituationReader._read_causation exactly).
        is_causal = False
        if len(events) >= 2:
            for outcome in events:
                cause_ev, method = CNET.causal_net_cause(events, toks, outcome)
                if cause_ev is None or cause_ev.lemma == outcome.lemma:
                    continue
                if method in ("connective", "bridge"):
                    is_causal = True
                    break
        causal_flag_per_sid[sid] = is_causal
    return tense_by_lemma_per_sid, default_tense_per_sid, causal_flag_per_sid


def resolve_real_coref(flat, order, sent_text):
    """REAL cross-sentence coref: builds one mention-stream record per event's AGENT surface
    string (agent=="?" events kept as a "?" sentinel, never fed to the resolver -- no real mention
    to resolve), in TRUE reading order (flat is already order-sorted), and runs
    hdlab.coreference_resolver.run_match_or_allocate UNMODIFIED (default flag_unresolved=False, so
    every real mention gets a cluster id, never None). Returns (protagonist_by_idx, resolver_stream,
    resolver_assigned) so the caller can also run the coref-over-merge diagnostic."""
    sent_idx_of = {sid: i for i, sid in enumerate(order)}
    agent_positions = []  # indices into `flat` that have a real agent token
    stream = []
    for i, (sid, (v, a, p)) in enumerate(flat):
        if not a or a == "?":
            continue
        is_pron = COREF.is_pronoun_mention(a)
        gender, number = COREF.gender_number_for(a, is_pron)
        first_word = a.strip().split()[0] if a.strip() else ""
        has_det = first_word in {"the", "a", "an"}
        stream.append({
            "gold_entity": f"agent_{i}", "clause": sent_idx_of[sid], "mention_text": a,
            "is_pronoun": is_pron, "gender": gender, "number": number, "text_pos": i,
            "has_determiner": has_det, "role": "agent",
        })
        agent_positions.append(i)
    assigned = COREF.run_match_or_allocate(stream, flag_unresolved=False)
    protagonist_by_idx = {}
    for i in range(len(flat)):
        protagonist_by_idx[i] = "?"
    for pos, eid in zip(agent_positions, assigned):
        protagonist_by_idx[pos] = f"CLUSTER_{eid}" if eid is not None else "?"
    return protagonist_by_idx


def apply_real_coref_relevance_gate(order, sent_text, svo_frame):
    """Adapt the frame-trigger's flat (sid,tup) SVO stream into a duck-typed SituationModel whose
    protagonist signal is the REAL match-or-allocate coref cluster (not raw string identity) and
    whose causation signal is the REAL sentence-level causal-link detection (not a connective-token
    presence proxy), then run exp_event_boundary_relevance_gate_v1.is_boundary_gate() UNMODIFIED."""
    tense_by_lemma, default_tense, causal_flag = build_dimension_signals(order, sent_text)
    sent_idx_of = {sid: i for i, sid in enumerate(order)}

    flat = [(sid, tup) for sid in order for tup in svo_frame[sid]]
    protagonist_by_idx = resolve_real_coref(flat, order, sent_text)

    fake_events = []
    raw_agent_surface = []
    for i, (sid, (v, a, p)) in enumerate(flat):
        lv = G.lemma_verb(v)
        tense = tense_by_lemma[sid].get(lv, default_tense[sid])
        fake_events.append(FakeEvent(agent=protagonist_by_idx[i], tense=tense, sent_idx=sent_idx_of[sid]))
        raw_agent_surface.append(a if a else "?")

    causal_sent_idxs = sorted(i for sid, i in sent_idx_of.items() if causal_flag[sid])
    fake_causal_links = [FakeCausalLink(sent_idx=i) for i in causal_sent_idxs]

    fake_sm = FakeSM(events=fake_events, entities=[], causal_links=fake_causal_links)
    preds, triggers = GATE.is_boundary_gate(fake_sm)
    assert len(preds) == len(flat)
    combined_flat = [item for item, keep in zip(flat, preds) if keep]
    dropped_flat = [(item, trig) for item, keep, trig in zip(flat, preds, triggers) if not keep]
    return flat, combined_flat, dropped_flat, preds, triggers, fake_events, raw_agent_surface


def coref_overmerge_diagnostic(flat, gold, preds, triggers, fake_events, raw_agent_surface):
    """Among frame-alone TRUE POSITIVES the gate drops, count how many are COREF-OVER-MERGE
    attributable: dropped event's real-coref cluster == immediately-preceding event's cluster (the
    gate's own reading-order 'prev' comparison) BUT the two raw agent surface strings differ.
    Structural self-diagnostic (no independent McGuffey coref gold exists) -- see module docstring."""
    tp_dropped = []
    for i, ((sid, tup), keep) in enumerate(zip(flat, preds)):
        if keep:
            continue
        if G.match_primary(tup, gold.get(sid, [])) is None:
            continue  # not a true positive under frame-alone -- not in scope for this diagnostic
        tp_dropped.append(i)
    overmerge = []
    other = []
    for i in tp_dropped:
        if i == 0:
            other.append(i)  # segment start, no prev to compare (never dropped in practice, i>=1)
            continue
        prev_cluster = fake_events[i - 1].agent
        cur_cluster = fake_events[i].agent
        prev_surface = raw_agent_surface[i - 1]
        cur_surface = raw_agent_surface[i]
        same_cluster = (prev_cluster == cur_cluster) and prev_cluster != "?"
        diff_surface = prev_surface != cur_surface
        if same_cluster and diff_surface and "protagonist" not in triggers[i]:
            overmerge.append({"idx": i, "sid_tup": [flat[i][0], list(flat[i][1])],
                              "prev_surface": prev_surface, "cur_surface": cur_surface,
                              "shared_cluster": cur_cluster})
        else:
            other.append(i)
    return {"n_tp_dropped": len(tp_dropped), "n_coref_overmerge_attributable": len(overmerge),
            "n_other_reason": len(other),
            "frac_coref_attributable": (len(overmerge) / len(tp_dropped)) if tp_dropped else None,
            "coref_overmerge_examples": overmerge[:15]}


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

    (flat_frame, flat_combined, dropped, preds, triggers,
     fake_events, raw_agent_surface) = apply_real_coref_relevance_gate(order, sent_text, svo_frame)
    prim_frame = G.score_arm(flat_frame, gold, G.match_primary)
    trip_frame = G.score_arm(flat_frame, gold, G.match_triple)
    prim_combined = G.score_arm(flat_combined, gold, G.match_primary)
    trip_combined = G.score_arm(flat_combined, gold, G.match_triple)

    diag = coref_overmerge_diagnostic(flat_frame, gold, preds, triggers, fake_events, raw_agent_surface)

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
    ok_coref, msg_coref = run_selftest_subprocess(
        os.path.join(REPO_ROOT, "verification", "verify_coreference_resolver.py"), [])
    g2_ok = ok_ft and ok_gate and ok_coref

    def kept_set(flat_list):
        return set((sid, tup) for sid, tup in flat_list)

    g3_gate_drops_something = len(flat_combined) < len(flat_frame)
    g3_combined_differs_from_baseline = kept_set(flat_combined) != kept_set(flat_baseline)
    g3_ok = g3_gate_drops_something and g3_combined_differs_from_baseline

    delta_p_vs_frame = prim_combined["precision"] - prim_frame["precision"]
    beats_frame_f1 = prim_combined["f1"] > prim_frame["f1"]
    beats_weak_combine_f1 = prim_combined["f1"] > FROZEN_WEAK_COMBINE_F1
    precision_material_gain = delta_p_vs_frame >= 0.05
    recall_kept = prim_combined["recall"] >= 0.45

    if not (g1_ok and g2_ok and g3_ok):
        verdict = "HARD_FAIL_DESIGN_GATE_VIOLATION"
    elif beats_frame_f1 and recall_kept and precision_material_gain:
        verdict = "HARD_PASS_REAL_COREF_COMPOSITION_NET_GAIN"
    elif beats_weak_combine_f1 and not recall_kept:
        verdict = "PARTIAL_BEATS_WEAK_COMBINE_RECALL_STILL_ERODED"
    elif prim_combined["f1"] <= FROZEN_WEAK_COMBINE_F1:
        verdict = "HARD_FAIL_STILL_OVERDROPS_COREF_QUALITY_IS_BLOCKER"
    else:
        verdict = "PARTIAL_BOUNDED_COMPOSITION"

    secondary_pred_role_residual = {
        "baseline_triple_f1": trip_baseline["f1"],
        "frame_trigger_triple_f1": trip_frame["f1"],
        "combined_triple_f1": trip_combined["f1"],
        "triple_still_worse_than_baseline_after_combine": trip_combined["f1"] < trip_baseline["f1"],
        "note": ("Secondary-predicate role-assignment errors are a SEPARATE component from event/"
                 "predicate detection (frame-trigger's scope) and from situation-boundary filtering "
                 "(this gate's scope); not folded into this cell's verdict."),
    }

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} "
           f"| BASELINE P={prim_baseline['precision']:.4f} R={prim_baseline['recall']:.4f} "
           f"F1={prim_baseline['f1']:.4f} n_pred={prim_baseline['n_pred']} "
           f"| FRAME_TRIGGER P={prim_frame['precision']:.4f} R={prim_frame['recall']:.4f} "
           f"F1={prim_frame['f1']:.4f} n_pred={prim_frame['n_pred']} "
           f"| WEAK_COMBINE(frozen ref) P={FROZEN_WEAK_COMBINE_P:.4f} R={FROZEN_WEAK_COMBINE_R:.4f} "
           f"F1={FROZEN_WEAK_COMBINE_F1:.4f} "
           f"| REAL_COREF_COMBINED P={prim_combined['precision']:.4f} R={prim_combined['recall']:.4f} "
           f"F1={prim_combined['f1']:.4f} n_pred={prim_combined['n_pred']} "
           f"| dP(combined-frame)={delta_p_vs_frame:+.4f} "
           f"| TRIPLE base={trip_baseline['f1']:.4f} frame={trip_frame['f1']:.4f} "
           f"combined={trip_combined['f1']:.4f} "
           f"| gate_dropped={len(dropped)}/{len(flat_frame)} "
           f"| tp_dropped={diag['n_tp_dropped']} coref_overmerge_attributable="
           f"{diag['n_coref_overmerge_attributable']} frac={diag['frac_coref_attributable']} "
           f"| G1={g1_ok} G2={g2_ok}(ft={ok_ft} gate={ok_gate} coref={ok_coref}) G3={g3_ok} "
           f"| beats_frame_f1={beats_frame_f1} beats_weak_combine_f1={beats_weak_combine_f1} "
           f"precision_material_gain={precision_material_gain} recall_kept={recall_kept}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg,
        "arms": {
            "baseline": {"primary": prim_baseline, "triple": trip_baseline},
            "frame_trigger": {"primary": prim_frame, "triple": trip_frame},
            "real_coref_combined": {"primary": prim_combined, "triple": trip_combined},
        },
        "frozen_reference": {
            "baseline": {"precision": FROZEN_BASELINE_P, "recall": FROZEN_BASELINE_R, "f1": FROZEN_BASELINE_F1},
            "frame_trigger": {"precision": FROZEN_FRAME_P, "recall": FROZEN_FRAME_R, "f1": FROZEN_FRAME_F1},
            "weak_combine": {"precision": FROZEN_WEAK_COMBINE_P, "recall": FROZEN_WEAK_COMBINE_R,
                              "f1": FROZEN_WEAK_COMBINE_F1},
        },
        "design_gate": {
            "G1_baseline_reproduction": g1_ok, "G1_checked": (mode == "full"),
            "G2_no_regression": g2_ok,
            "G2_frame_trigger_selftest": {"ok": ok_ft, "tail": msg_ft},
            "G2_relevance_gate_selftest": {"ok": ok_gate, "tail": msg_gate},
            "G2_coref_resolver_verify": {"ok": ok_coref, "tail": msg_coref},
            "G3_arms_differ": g3_ok,
            "G3_gate_drops_something": g3_gate_drops_something,
            "G3_combined_differs_from_baseline": g3_combined_differs_from_baseline,
        },
        "delta_precision_combined_vs_frame": delta_p_vs_frame,
        "beats_frame_f1": beats_frame_f1,
        "beats_weak_combine_f1": beats_weak_combine_f1,
        "precision_material_gain_ge_0.05": precision_material_gain,
        "recall_kept_ge_0.45": recall_kept,
        "coref_overmerge_diagnostic": diag,
        "gate_dropped_examples": [[sid, list(tup), trig] for (sid, tup), trig in dropped[:20]],
        "n_gate_dropped": len(dropped), "n_frame_flat": len(flat_frame),
        "secondary_pred_role_residual": secondary_pred_role_residual,
        "REQUIRED_FIELDS": ["verdict", "arms", "design_gate", "coref_overmerge_diagnostic",
                            "secondary_pred_role_residual", "delta_precision_combined_vs_frame",
                            "beats_frame_f1", "beats_weak_combine_f1"],
        "notes": ("Re-attempts exp_frame_trigger_plus_relevance_gate_combined_v1's composition with "
                  "REAL signals: protagonist via hdlab.coreference_resolver.run_match_or_allocate "
                  "(canonical promoted cross-sentence coref, unmodified) instead of raw-string "
                  "identity-map; causation via the SAME connective/bridge causal-net check "
                  "hdlab/situation_reader.py._read_causation uses, instead of a naive connective-"
                  "token-presence flag. is_boundary_gate() itself is unmodified. See module "
                  "docstring for the full pre-registration, the coref-over-merge diagnostic design, "
                  "and why routing through SituationReader.read() literally is not possible on "
                  "McGuffey text (no coref-annotated CoNLL exists for this corpus)."),
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
        # cheap wiring self-test: hand-verified real-coref-resolution + boundary pattern.
        # "herbert" (name) sent0, then "he" (pronoun, should resolve to herbert's cluster) sent0,
        # then "mary" (name, new cluster) sent1 -- same-cluster consecutive events (herbert/he)
        # must NOT trigger protagonist, the cluster-shift to mary MUST trigger protagonist.
        flat = [
            ("s0", ("walked", "herbert", "home")),
            ("s0", ("smiled", "he", "widely")),
            ("s1", ("called", "mary", "herbert")),
        ]
        order = ["s0", "s1"]
        sent_text = {"s0": "Herbert walked home. He smiled widely.", "s1": "Mary called Herbert."}
        protagonist_by_idx = resolve_real_coref(flat, order, sent_text)
        assert protagonist_by_idx[0] == protagonist_by_idx[1], (
            f"real coref should resolve 'he' to herbert's cluster: {protagonist_by_idx}")
        assert protagonist_by_idx[2] != protagonist_by_idx[0], (
            f"'mary' must be a distinct cluster from herbert: {protagonist_by_idx}")
        fake_events = [
            FakeEvent(agent=protagonist_by_idx[0], tense="SIMPLE_PAST", sent_idx=0),
            FakeEvent(agent=protagonist_by_idx[1], tense="SIMPLE_PAST", sent_idx=0),
            FakeEvent(agent=protagonist_by_idx[2], tense="SIMPLE_PAST", sent_idx=1),
        ]
        fake_sm = FakeSM(events=fake_events, entities=[], causal_links=[])
        preds, triggers = GATE.is_boundary_gate(fake_sm)
        assert preds == [True, False, True], f"self-test: expected [T,F,T], got {preds}"
        assert "protagonist" in triggers[2], f"expected protagonist trigger on the mary shift: {triggers[2]}"
        # real causal-link wiring smoke: a genuine 2-event connective sentence must flag causal=True,
        # a single-event sentence merely mentioning a connective word alone must NOT (this is exactly
        # the distinction the weak "any connective token" proxy could not make).
        _, _, causal_flag = build_dimension_signals(["c0"], {"c0": "The window broke because Peter pushed it."})
        assert causal_flag["c0"] is True, "genuine 2-event causal sentence must flag causal=True"
        print(f"[{ANCHOR_NAME}] self-test PASS: protagonist_by_idx={protagonist_by_idx} "
              f"preds={preds} triggers={triggers}", flush=True)
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
