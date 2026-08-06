"""FRAME-ARITY PATIENT GATE vs INDEPENDENT GOLD (McGuffey Castle-Building, n=34).

QUESTION: does the 2026-08-06 frame-ARITY gate in hdlab/situation_reader.py::_pick_role_mentions
(hdlab.thematic_role_labeler.STRICTLY_INTRANSITIVE_VERBS -- sit/go/come/arrive/fall/rise/die/
sleep/kneel/... never license a PATIENT slot) raise the PRODUCTION reader's SVO precision against
the SAME independent gold used by exp_coherence_gate_extraction_correctness_independent_gold_v1
(data/gold_mcguffey_castle_building_svo_v1.json), with recall UNCHANGED, as pre-registered
(notes/... frame-arity redirect, commit eab3a4cc5 north-star drill)?

THE FIX UNDER TEST: hdlab.situation_reader.SituationReader(gate_intransitive=True) vs the default
(gate_intransitive=False, byte-identical to pre-fix). The PRIMARY, decisive evidence for this fix
is the gold-independent mechanism can-fail suite already shipped in hdlab/situation_reader.py::
_selftest_frame_arity_gate (16/16 structural cases). THIS cell is the SECONDARY, small-n gold
measurement the pre-reg also calls for -- explicitly scoped MIDDLE_BAND on its own (n=34 gold,
single-annotator, single 46-sentence narrative) per the pre-reg.

WHY A SYNTHETIC-COREF CONLL, NOT A REAL LITBANK FILE: no LitBank-style coref-annotated CoNLL
exists for this McGuffey passage (it is not a LitBank book). hdlab.situation_reader.SituationReader
.read() requires a CoNLL doc whose coref brackets are the ONLY source of "nominal mention"
candidates (hdlab.coref.parse_litbank_conll). To exercise the REAL production functions
(_pick_role_mentions / _assign_roles / _read_events, imported unmodified, never reimplemented)
on this text, this cell builds a CoNLL doc that gives EVERY nominal token (NN/NNS/NNP/NNPS/PRP/
PRP$, tagged by the SAME shared tagger experiments._temporal_ordering.default_tagger production
uses) its own UNIQUE SINGLETON coref bracket -- i.e. a superset candidate pool of "every noun/
pronoun is a mention", vs. real LitBank data where only coref-tracked (often only non-singleton)
NPs are annotated. HONEST LIMITATION (disclosed, not hidden): this makes the candidate pool for
_pick_role_mentions a plausible but not identical proxy for a true LitBank-annotated version of
this text -- absolute P/R levels here should NOT be compared to the 0.232/0.278/0.297 F1 numbers
cited in situation_reader.py's docstring (those are scored on REAL LitBank passages with REAL
coref annotation sparsity). What IS faithful: the arity-gate mechanism itself runs completely
unmodified (same _pick_role_mentions call, same STRICTLY_INTRANSITIVE_VERBS lookup), so the GATED
vs UNGATED delta measured here isolates exactly the fix's effect on THIS reader's SVO output,
which is the ONE variable this cell is designed to measure (per envelope-fail-bands: one variable,
same candidate pool, same predicate extraction, same events -- only gate_intransitive flips).

SCORING: reuses (imports, does not reimplement) the independent-gold lemmatizer + matcher +
scorer already vetted for this exact gold file in
experiments/exp_coherence_gate_extraction_correctness_independent_gold_v1.py (lemma_verb,
load_gold, match_primary, score_arm) so the McGuffey-specific irregular-verb lemmatization and
matching convention are IDENTICAL to the existing coherence-gate measurement on this corpus.

PRE-REGISTERED BANDS (envelope-fail-bands; set before running):
  HARD_PASS: mechanism can-fail 16/16 (imported from situation_reader's own self-test, gold-
    independent, decisive) AND gold PRIMARY precision(gated) > precision(ungated) (>0 real
    intransitive-FP relations removed) AND recall(gated) == recall(ungated) EXACTLY (n_gold_covered
    identical -- the gate must never touch a true positive) AND certification 220/3 green.
  HARD_FAIL: can-fail suite fails ANY case, OR gold recall(gated) < recall(ungated) (a true patient
    was wrongly stripped), OR cert regresses.
  MIDDLE_BAND (expected/pre-declared for the GOLD AGGREGATE ONLY, n=34 is small): can-fail passes
    and recall holds and precision is flat-or-up but the delta is small/noisy at this n; the
    mechanism can-fail suite (not this aggregate) is the decisive evidence per the pre-reg. Report
    the intransitive-FP-removed count SEPARATELY from the larger gold-scope-mismatch FP class this
    fix cannot touch (situation_reader.py docstring: ~65/95 gold-scope FPs on the REAL LitBank
    scoring -- not reproduced by this proxy corpus at all, since every noun is a candidate here).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- 46 short sentences, a
handful of POS-tag calls + 2 full SituationReader.read() passes; wall < 15s. Foreground
local-to-completion. NO queue / NO push / NO remote-persist. Storage: no_storage (measurement,
not composition).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement; NOT queue-
dispatched, mirrors exp_coherence_gate_extraction_correctness_independent_gold_v1's declared
subset):
- arms_differ_verified at smoke (gated vs ungated kept-tuple hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- discriminator fires: gated arm drops >0 kept relations vs ungated
- deterministic seeding: fixed sentence order, deterministic singleton cluster ids (running
  counter over a SORTED sentence-id list), no hash()-seeded RNG, no list(set())
- scaffold-free witness: one hand-checked intransitive-FP the gate removes ("went" -> no longer
  claims a patient) + one transitive TP the gate keeps ("build" -> "castle" unchanged)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import re
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "situation_reader_frame_arity_gate_gold_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import _temporal_ordering as T  # noqa: E402  (shared tagger, same as production)
from experiments.exp_coherence_gate_extraction_correctness_independent_gold_v1 import (  # noqa: E402
    lemma_verb as gold_lemma_verb, load_gold, match_primary, score_arm, split_sents,
)
from hdlab.situation_reader import SituationReader, _write_temp_conll  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb as trl_lemma_verb, is_strictly_intransitive  # noqa: E402

GOLD_LESSONS = ["L04", "L05"]
NOMINAL_POS = {"NN", "NNS", "NNP", "NNPS", "PRP", "PRP$"}


# ----------------------------------------------------------------------------------------------
# Build a synthetic singleton-coref CoNLL doc for the L04+L05 raw text (see docstring for why).
# ----------------------------------------------------------------------------------------------
def build_conll(sent_ids, sent_text):
    """rows for _write_temp_conll (reuse, not reimplement): every nominal-tagged token gets its
    own never-repeated singleton coref cluster id (a deterministic running counter over the
    SORTED-by-construction sent_ids order -- no hash()/set() nondeterminism)."""
    rows = []
    cluster_id = 0
    n_nominal_tokens = 0
    for si, sid in enumerate(sent_ids):
        tagged = T.default_tagger(sent_text[sid])
        for wtok, (surf, low, pos) in enumerate(tagged):
            coref = "_"
            if pos in NOMINAL_POS and low:
                coref = f"({cluster_id})"
                cluster_id += 1
                n_nominal_tokens += 1
            rows.append((si, wtok, low, coref))
    return rows, n_nominal_tokens


# ----------------------------------------------------------------------------------------------
# Run the REAL production reader (gated + ungated) and collect per-sentence SVO tuples.
# ----------------------------------------------------------------------------------------------
def run_reader(path, sent_ids, gate_intransitive):
    reader = SituationReader(gate_intransitive=gate_intransitive)
    sm = reader.read(path)
    kept = []       # (sid, (v, a, p)) -- only events with a real (non "?") patient
    all_events = []  # every event, incl. patient=="?" (for event-count / recall-of-extraction audit)
    for ev in sm.events:
        sid = sent_ids[ev.sent_idx]
        v = gold_lemma_verb(ev.predicate)
        all_events.append((sid, ev.predicate, ev.agent, ev.patient))
        if ev.patient == "?":
            continue
        kept.append((sid, (v, ev.agent.lower(), ev.patient.lower())))
    return kept, all_events, sm


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness (hand-checked, independent of the gold-matching machinery).
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness(kept_ungated, kept_gated):
    ungated_set = {(sid, t) for sid, t in kept_ungated}
    gated_set = {(sid, t) for sid, t in kept_gated}
    removed = ungated_set - gated_set
    went_removed = any(t[0] == "go" for _sid, t in removed)
    # rub(cat, castle) at L04_02 is a real gold TP (transitive) -- must survive gating unchanged.
    rub_kept = any(t[0] == "rub" and t[2] == "castle" for _sid, t in gated_set)
    assert went_removed, f"witness: expected a go()-patient relation to be removed by the gate; removed={removed}"
    assert rub_kept, f"witness: expected rub(...,castle) to survive gating; gated_set={gated_set}"
    assert is_strictly_intransitive(trl_lemma_verb("went")), "witness: 'went'->'go' must be gated"
    assert not is_strictly_intransitive(trl_lemma_verb("rubbed")), "witness: 'rubbed'->'rub' must not be gated"
    return {"witness": "PASS", "n_removed_total": len(removed),
            "go_patient_removed_example": [list(x) for x in removed if x[1][0] == "go"][:3],
            "rub_castle_kept": rub_kept}


# ----------------------------------------------------------------------------------------------
# Config + run.
# ----------------------------------------------------------------------------------------------
def run_config():
    sent_ids = [f"{lid}_{j:02d}" for lid in GOLD_LESSONS
                for j in range(len(split_sents(_load_lesson_text(lid))))]
    sent_text = {sid: None for sid in sent_ids}
    for lid in GOLD_LESSONS:
        for j, s in enumerate(split_sents(_load_lesson_text(lid))):
            sent_text[f"{lid}_{j:02d}"] = s

    gold, gold_meta = load_gold(GOLD_LESSONS)

    rows, n_nominal_tokens = build_conll(sent_ids, sent_text)
    path = _write_temp_conll(rows)
    try:
        kept_ungated, events_ungated, sm_ungated = run_reader(path, sent_ids, gate_intransitive=False)
        kept_gated, events_gated, sm_gated = run_reader(path, sent_ids, gate_intransitive=True)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

    m_ungated = score_arm(kept_ungated, gold, match_primary)
    m_gated = score_arm(kept_gated, gold, match_primary)

    # intransitive-FP-removed: relations present ungated, absent gated, whose verb (re-lemmatized
    # via the SAME thematic_role_labeler lemmatizer the gate itself uses) is strictly-intransitive,
    # and were NOT already a gold true-positive (so this only ever counts REMOVED false positives,
    # never a lost true positive -- that would show up as a recall regression instead, checked
    # separately below).
    ungated_set = {(sid, t) for sid, t in kept_ungated}
    gated_set = {(sid, t) for sid, t in kept_gated}
    removed = ungated_set - gated_set
    added = gated_set - ungated_set
    intransitive_fp_removed = []
    other_removed = []
    for sid, (v, a, p) in removed:
        surface_lemma = trl_lemma_verb(v)  # v is already gold_lemma_verb'd; re-lemmatize for the gate's own vocab
        was_gold_tp = match_primary((v, a, p), gold.get(sid, [])) is not None
        rec = {"sid": sid, "v": v, "a": a, "p": p, "was_gold_true_positive": was_gold_tp}
        if is_strictly_intransitive(surface_lemma) or is_strictly_intransitive(v):
            intransitive_fp_removed.append(rec)
        else:
            other_removed.append(rec)

    recall_unchanged = (m_gated["n_gold_covered"] == m_ungated["n_gold_covered"])
    n_events_unchanged = (len(events_ungated) == len(events_gated))
    precision_up = m_gated["precision"] > m_ungated["precision"]
    any_lost_true_positive = any(r["was_gold_true_positive"] for r in intransitive_fp_removed + other_removed)

    return {
        "sent_ids": sent_ids, "gold_meta": gold_meta, "n_gold_relations": sum(len(v) for v in gold.values()),
        "n_nominal_tokens": n_nominal_tokens,
        "kept_ungated": kept_ungated, "kept_gated": kept_gated,
        "m_ungated": m_ungated, "m_gated": m_gated,
        "n_events_ungated": len(events_ungated), "n_events_gated": len(events_gated),
        "n_events_unchanged": n_events_unchanged,
        "intransitive_fp_removed": intransitive_fp_removed,
        "other_removed_non_intransitive_class": other_removed,
        "n_intransitive_fp_removed": len(intransitive_fp_removed),
        "n_other_removed": len(other_removed),
        "n_added_by_gate": len(added),  # must be 0 -- the gate only ever removes, never adds
        "recall_unchanged": recall_unchanged,
        "n_events_unchanged_flag": n_events_unchanged,
        "precision_up": precision_up,
        "any_lost_true_positive": any_lost_true_positive,
    }


_LESSON_TEXT_CACHE = {}


def _load_lesson_text(lid):
    if lid not in _LESSON_TEXT_CACHE:
        from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST
        les = NEST.load_lessons()
        _LESSON_TEXT_CACHE.update(les)
    return _LESSON_TEXT_CACHE[lid]


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def build_verdict(res):
    if res["any_lost_true_positive"] or not res["recall_unchanged"] or res["n_added_by_gate"] > 0:
        return "HARD_FAIL_RECALL_OR_ADD_REGRESSION"
    if not res["precision_up"]:
        return "MIDDLE_BAND_NO_PRECISION_DELTA_AT_THIS_N"
    return "MIDDLE_BAND_PRECISION_UP_SMALL_N_GOLD_SECONDARY_EVIDENCE"


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    res = run_config()
    witness = scaffold_free_witness(res["kept_ungated"], res["kept_gated"])

    h_ungated = kept_hash(res["kept_ungated"])
    h_gated = kept_hash(res["kept_gated"])
    arms_differ_verified = (h_ungated != h_gated)
    discriminator_fires = (res["n_intransitive_fp_removed"] > 0)

    verdict = build_verdict(res)
    elapsed = time.perf_counter() - t0
    mu, mg = res["m_ungated"], res["m_gated"]
    msg = (f"{verdict} | n_sents={len(res['sent_ids'])} gold={res['n_gold_relations']} "
          f"| UNGATED P={mu['precision']:.3f} R={mu['recall']:.3f} F1={mu['f1']:.3f} n_pred={mu['n_pred']} "
          f"| GATED P={mg['precision']:.3f} R={mg['recall']:.3f} F1={mg['f1']:.3f} n_pred={mg['n_pred']} "
          f"| intransitive_fp_removed={res['n_intransitive_fp_removed']} other_removed={res['n_other_removed']} "
          f"added_by_gate={res['n_added_by_gate']} "
          f"| recall_unchanged={res['recall_unchanged']} n_events_unchanged={res['n_events_unchanged']} "
          f"| arms_differ={arms_differ_verified} discrim_fires={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "arm_metrics": {"ungated": mu, "gated": mg},
        "n_events_ungated": res["n_events_ungated"], "n_events_gated": res["n_events_gated"],
        "n_events_unchanged": res["n_events_unchanged"],
        "intransitive_fp_removed": res["intransitive_fp_removed"],
        "other_removed_non_intransitive_class": res["other_removed_non_intransitive_class"],
        "n_intransitive_fp_removed": res["n_intransitive_fp_removed"],
        "n_other_removed": res["n_other_removed"],
        "n_added_by_gate": res["n_added_by_gate"],
        "recall_unchanged": res["recall_unchanged"],
        "any_lost_true_positive": res["any_lost_true_positive"],
        "kept_hashes": {"ungated": h_ungated, "gated": h_gated},
        "arms_differ_verified": arms_differ_verified, "discriminator_fires": discriminator_fires,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "n_nominal_tokens_synthetic_candidate_pool": res["n_nominal_tokens"],
        "independent_gold_source": "data/gold_mcguffey_castle_building_svo_v1.json (same gold as "
                                   "exp_coherence_gate_extraction_correctness_independent_gold_v1)",
        "honest_limitation": ("candidate nominal pool is a SYNTHETIC every-noun-is-a-singleton-mention "
                              "CoNLL (no real LitBank coref annotation exists for this non-LitBank "
                              "McGuffey text) -- absolute P/R here are NOT comparable to the "
                              "0.232/0.278/0.297 F1 numbers in situation_reader.py's docstring (those "
                              "are on real LitBank data); only the GATED-vs-UNGATED delta on this SAME "
                              "candidate pool is the measured quantity."),
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "intransitive_fp_removed", "recall_unchanged",
                            "scaffold_free_witness"],
        "notes": ("SECONDARY, small-n (34 gold relations) gold measurement of the frame-arity patient "
                  "gate. PRIMARY/decisive evidence is hdlab.situation_reader._selftest_frame_arity_gate "
                  "(gold-independent, 16/16 mechanism can-fail). MIDDLE_BAND on the aggregate is the "
                  "PRE-REGISTERED expected outcome at this n; HARD_FAIL only if recall regresses or the "
                  "gate ever ADDS a relation (n_added_by_gate>0, which would indicate a wiring bug)."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"  intransitive_fp_removed examples: {res['intransitive_fp_removed'][:10]}", flush=True)
    print(f"  witness: {witness}", flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        res = run_config()
        w = scaffold_free_witness(res["kept_ungated"], res["kept_gated"])
        print(f"[{ANCHOR_NAME}] self-test: verdict={build_verdict(res)} "
              f"UNGATED_P={res['m_ungated']['precision']:.3f} GATED_P={res['m_gated']['precision']:.3f} "
              f"intransitive_fp_removed={res['n_intransitive_fp_removed']} "
              f"recall_unchanged={res['recall_unchanged']} witness={w['witness']}", flush=True)
        return
    if args.smoke or args.full:
        run_mode("full" if args.full else "smoke")
        return
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
