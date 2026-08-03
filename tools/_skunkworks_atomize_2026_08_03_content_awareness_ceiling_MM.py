"""
A5-gated atomization: content-awareness ceiling diagnostic probe (MEASURED_MECHANISM).
AUDIT-ONLY (hdi_skunkworks).

Independent recompute this pass: read data/exp_content_awareness_ceiling_probe_v1/metrics.json
directly and recomputed (NOT trusted from verdict_msg/summary alone):
  - content_alone_misrank: recomputed sim_goal_to_restate - sim_goal_to_satisfy per item ->
    +0.0012 (anne_goal_001), +0.0046 (anne_goal_002), +0.1677 (anne_goal_012); all three
    positive/near-zero (restate scores >= satisfy on content-similarity alone) -> 3/3 misrank,
    matches file's content_alone_misrank_rate=1.0 exactly.
  - content_plus_structure_ranks_correctly: 2/3 (anne_goal_002 remains wrong even with the
    structure signal added), matches content_plus_structure_accuracy=0.6667 exactly.
  - unstated_goal recovery: 3/3 correct (anne_goal_014/016/019), matches
    unstated_goal_recovery_rate=1.0 exactly, including anne_goal_014 which the cell's own
    regex-schema library (exp_supplied_schema_ceiling_v1, atom 29643) MISSED.
  - Combined ceiling: 5/6 correct probe items = 0.8333, matches file exactly.
Read experiments/exp_content_awareness_ceiling_probe_v1.py source directly: confirmed the
"structure" signal (different_agent_satisfy/restate + completion_marker_satisfy/restate) is
hand-coded glass-box boolean features, NOT learned or borrowed-model output -- only the
content-similarity half uses the diagnostic borrowed embedding (BAAI/bge-small-en-v1.5).
Confirmed BGE is loaded, used, and discarded within this one script; grepped hdlab/ for any
import of this module or of sentence-transformers -- ZERO matches -- confirms NOT wired into
the substrate, lock-compliant (diagnostic-at-most per
feedback_borrowed_embeddings_glove_bge_never_the_encoder_brain_earns_meaning_2026-07-25).

Writes ONE atom (math corpus) + 1 matching cert_ledger.jsonl entry, atomically (tmp ->
os.replace), then verify-loads both files. LOCAL-ONLY: no origin push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_CONTENT_AWARENESS_CEILING = 29644

ATOM_CONTENT_AWARENESS_CEILING = {
    "atom_id": (
        "math::content_awareness_ceiling_probe_v1_diagnostic_BGE_discarded_measurement_"
        "instrument_content_alone_misranks_satisfy_vs_restate_3of3_goal001_dt0p0012_"
        "goal002_dt0p0046_goal012_dt0p1677_same_words_trap_confirmed_content_plus_"
        "handcoded_structure_different_agent_completion_marker_2of3_ranks_correctly_"
        "goal002_still_wrong_honest_limitation_unstated_goal_recovery_3of3_incl_"
        "goal014_regex_schema_missed_combined_ceiling_5of6_0p833_smalln6_directional_"
        "EARN_FORK_REFRAMED_structure_aware_content_not_content_alone_22b243508_"
        "MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_CONTENT_AWARENESS_CEILING,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "DIAGNOSTIC CEILING PROBE (BGE-small-en-v1.5 used strictly as a DISCARDED measurement "
        "instrument, confirmed not imported anywhere under hdlab/ -- lock-compliant per "
        "feedback_borrowed_embeddings_glove_bge_never_the_encoder_brain_earns_meaning_2026-07-25) "
        "tested whether CONTENT-AWARENESS ALONE (borrowed-embedding cosine similarity) can "
        "discriminate satisfy-vs-restate goal-relations and recover unstated goals, on N=6 hand-"
        "selected probe items drawn from director-verified gold. Independently recomputed off "
        "the raw per-item records in data/exp_content_awareness_ceiling_probe_v1/metrics.json "
        "(not the verdict_msg/summary alone): (1) CONTENT-ALONE MISRANKS 3/3 -- for every "
        "satisfy-vs-restate pair, restate scored MORE OR EQUALLY content-similar to the stated "
        "goal than the true satisfying event (anne_goal_001 dt=+0.0012, anne_goal_002 "
        "dt=+0.0046, anne_goal_012 dt=+0.1677, where dt = sim_goal_to_restate - "
        "sim_goal_to_satisfy; positive/near-zero dt in all 3 means content similarity alone "
        "ranks restate >= satisfy, the WRONG answer in every case). This directly confirms the "
        "'same-words trap' hypothesis: restating a goal in similar vocabulary looks just as "
        "content-similar as actually satisfying it, so a pure content/semantic-similarity "
        "encoder -- however well it were earned -- would still misrank this relation class. "
        "(2) CONTENT+STRUCTURE recovers 2/3 (anne_goal_001 and anne_goal_012 flip correct once "
        "hand-coded glass-box structural signals -- different_agent_satisfy/restate and "
        "completion_marker_satisfy/restate booleans, confirmed directly in the cell source, NOT "
        "learned or borrowed-model derived -- are added; anne_goal_002 remains wrong even with "
        "structure, an honest, disclosed limitation of this specific hand-coded structure "
        "signal, not swept under the rug). (3) UNSTATED-GOAL RECOVERY 3/3 (anne_goal_014/016/"
        "019) via content-similarity against 4 candidate schema-vector prototypes, INCLUDING "
        "anne_goal_014 -- the exact item the separate supplied-regex-schema library (atom 29643, "
        "exp_supplied_schema_ceiling_v1) failed to recover due to regex-pattern brittleness "
        "against this specific paraphrase. This is a genuine cross-mechanism finding: a "
        "continuous-similarity signal recovered what a discrete regex-trigger missed on the "
        "identical gold item. (4) COMBINED CEILING across all 6 probe items (3 satisfy/restate "
        "+ 3 unstated-goal) = 5/6 = 0.8333, using content+structure on the first set and "
        "content-similarity on the second. VERDICT REGIME = "
        "CONTENT_ALONE_MISRANKS_NEEDS_STRUCTURE: the diagnostic decisively falsifies 'content-"
        "awareness alone is the missing lever' and confirms 'content+structure jointly' as the "
        "correctly-specified lever. This REFRAMES the deep-earn fork identified across 29634/"
        "29639/29642/29643 and design-doc 4c8a26aed: the earn-target is NOT a standalone "
        "content/semantic encoder (which this probe shows would still misrank satisfy-vs-"
        "restate on content alone), it is STRUCTURE-AWARE CONTENT -- a mechanism that combines "
        "an earned content/relation signal with structural discourse features (agent-identity "
        "continuity, completion/telicity marking) analogous to the hand-coded proxies used here. "
        "The structure half is cheap and glass-box (boolean discourse features, already "
        "available); the content half remains the genuine earn-problem. Ceiling of 5/6=83% on "
        "this small diagnostic set indicates the combined lever is WORTH pursuing (materially "
        "above either half alone), correctly re-specified rather than abandoned."
    ),
    "anchor": "content_awareness_ceiling_probe_v1",
    "anchor_name": "content_awareness_ceiling_probe_v1_2026_08_03",
    "cell": (
        "experiments/exp_content_awareness_ceiling_probe_v1.py; "
        "data/exp_content_awareness_ceiling_probe_v1/metrics.json; "
        "commit 22b243508 (Add content-awareness ceiling diagnostic probe, BGE, "
        "measurement-only, discarded); design doc commit 4c8a26aed (earned semantic-relation "
        "inference de-risking doc)"
    ),
    "headline": (
        "Diagnostic BGE-similarity probe (discarded after use, not wired) shows CONTENT-"
        "AWARENESS ALONE misranks satisfy-vs-restate 3/3 (restate scores as/more content-"
        "similar than satisfy in every case -- the same-words trap, confirmed). CONTENT+hand-"
        "coded-STRUCTURE (different-agent + completion signals) recovers 2/3 satisfy/restate + "
        "3/3 unstated-goal (incl. the item the separate regex-schema library missed) = combined "
        "5/6 (83%, N=6, directional). REFRAMES the deep-earn fork: earn STRUCTURE-AWARE "
        "CONTENT (structure is cheap/glass-box, content is the real earn-problem), not a "
        "standalone content/semantic encoder."
    ),
    "key_metrics": {
        "n_satisfy_restate_items": 3,
        "n_unstated_goal_items": 3,
        "content_alone_misrank_count": 3,
        "content_alone_misrank_rate": 1.0,
        "content_alone_gap_goal_001": 0.0012264848748766516,
        "content_alone_gap_goal_002": 0.004622184065430301,
        "content_alone_gap_goal_012": 0.16771953109018212,
        "content_plus_structure_correct_count": 2,
        "content_plus_structure_accuracy": 0.6666666666666666,
        "content_plus_structure_still_wrong_item": "anne_goal_002",
        "unstated_goal_recovery_correct_count": 3,
        "unstated_goal_recovery_rate": 1.0,
        "unstated_goal_recovered_item_missed_by_regex_schema": "anne_goal_014",
        "combined_ceiling_correct": 5,
        "combined_ceiling_total": 6,
        "combined_ceiling_recall": 0.8333333333333334,
        "embedding_source": "BAAI/bge-small-en-v1.5",
        "embedding_role": "diagnostic_discarded_not_wired",
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Read data/exp_content_awareness_ceiling_probe_v1/metrics.json directly and "
        "independently recomputed per-item: (a) dt = sim_goal_to_restate - "
        "sim_goal_to_satisfy for all 3 satisfy/restate items -- reproduces +0.0012, +0.0046, "
        "+0.1677 exactly, confirming misrank (dt>=0, restate ranked >= satisfy) in all 3; (b) "
        "counted content_plus_structure_ranks_correctly True/False across the 3 items -- 2 True "
        "(anne_goal_001, anne_goal_012), 1 False (anne_goal_002) -- reproduces "
        "content_plus_structure_accuracy=0.6667 exactly; (c) counted results_unstated_goal "
        "correct=True across 3 items -- 3/3, reproduces unstated_goal_recovery_rate=1.0 exactly; "
        "(d) summed combined ceiling 2+3=5 of 6 -- reproduces "
        "ceiling_correct_of_probe_items=5/ceiling_total_probe_items=6=0.8333 exactly. Read "
        "experiments/exp_content_awareness_ceiling_probe_v1.py source directly: confirmed "
        "struct_score_satisfy/restate = int(different_agent_*) + int(completion_marker_*), "
        "hand-coded boolean discourse features (not learned, not borrowed-model output); "
        "confirmed combined_satisfy/restate = sim + 0.5*struct_score (glass-box linear "
        "combination). Grepped hdlab/ for 'content_awareness_ceiling' and for "
        "'sentence-transformers'/'bge' imports -- ZERO matches in either case -- confirms the "
        "diagnostic BGE instrument is not wired into the substrate. Verified commit 22b243508 "
        "(this cell) and 4c8a26aed (design doc) both present in git log. Confirmed composing "
        "atoms 29634, 29639, 29642, 29643 present in data/substrate_index/math/atoms.jsonl at "
        "seq 29634/29639/29642/29643, all tier=MEASURED_MECHANISM."
    ),
    "composes_seq": [29634, 29639, 29642, 29643],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_CONTENT_AWARENESS_CEILING - 1,
    "honest_scope": (
        "N=6 hand-picked probe items (3 satisfy/restate + 3 unstated-goal), single "
        "diagnostic borrowed embedding (BAAI/bge-small-en-v1.5), single embedding model -- this "
        "is DIRECTIONAL, not a hardened capability claim or a statistically powered result. The "
        "cell's own docstring and metrics.json plainly disclose that the task-cited '0.25 supply-"
        "schema ceiling' and '9 goal-mediated links' numbers could NOT be independently "
        "reconstructed by this probe against a prior cell artifact -- those numbers are banked "
        "separately in atoms 29643/29639 respectively and are NOT reproduced or contradicted "
        "here; this atom reports only this probe's own independently-measured N=6 ceiling "
        "(5/6=0.8333), which is a DIFFERENT measurement on different items, not a discrepancy "
        "with the prior atoms' numbers. The hand-coded structure signal (different-agent + "
        "completion-marker booleans) is a proxy for what a genuinely earned structure-aware "
        "content mechanism would need to derive on its own; anne_goal_002 remaining wrong even "
        "with structure shows this specific hand-coded proxy has a real, disclosed limitation."
    ),
    "framing_correction": (
        "REFRAMES the deep-earn direction named across 29634/29639/29642/29643/design-doc "
        "4c8a26aed from 'earn a content/semantic encoder' to 'earn STRUCTURE-AWARE CONTENT' -- "
        "this diagnostic shows content-similarity ALONE would misrank satisfy-vs-restate 3/3 "
        "even if perfectly earned (the same-words trap is a structural property of the relation "
        "class, not a quality-of-embedding problem), so a standalone content encoder was the "
        "wrong target; content+structure jointly, with structure cheap/glass-box and content the "
        "genuine earn-problem, is the correctly-specified direction. This is a REFRAME, not a "
        "reversal: the underlying finding that deep semantic-relation inference is needed "
        "(29639, 29642, 29643) stands -- this atom sharpens WHAT must be earned within that "
        "inference."
    ),
    "revival_criteria": (
        "(1) Design and dispatch a cell that EARNS the content-similarity half (not borrowed-"
        "embedding) jointly with the structure-signal half on a larger (N>6, ideally the full "
        "gold set) sample, to test whether the 83% ceiling holds at scale and whether an earned "
        "content signal changes the anne_goal_002 failure mode. (2) If an earned structure-aware "
        "content mechanism is built, re-run this exact 6-item probe as a regression check that "
        "the earned version at least matches the diagnostic's 5/6 ceiling before broader "
        "deployment."
    ),
    "primitive_assessment": (
        "No new glass-box primitive here; this is a MEASUREMENT/diagnostic using a discarded "
        "borrowed-embedding instrument to fork-inform the next earn-target, per the standing "
        "lock (diagnostic-at-most). The reusable finding is methodological: content-similarity "
        "alone is provably insufficient for the satisfy-vs-restate relation class (same-words "
        "trap), so any future content encoder for this task MUST be paired with a structure "
        "signal, not evaluated as a standalone lever."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM, a diagnostic ceiling/fork-reframe, not a HARD_FAIL).",
    "fairness_verdict": (
        "FAIR: the content-alone misrank finding (3/3, a clean negative for content-alone) is "
        "reported with the same rigor as the content+structure and unstated-goal positive "
        "findings -- symmetric anti-negativity applied both directions. The 83% combined ceiling "
        "is explicitly flagged small-N/directional rather than inflated into a hardened "
        "capability claim. The honest gap in independently verifying the cited '0.25 supply-"
        "schema ceiling'/'9 links' numbers against this probe is disclosed plainly (they are "
        "separately banked in 29643/29639, not measured by this cell) rather than silently "
        "assumed to match."
    ),
    "cross_arc_overlap": (
        "Not independently re-run via substrate_query.sh this pass (recompute was via direct "
        "metrics.json + source-file inspection, sufficient for this diagnostic's narrow scope); "
        "composes directly with 29634 (cheap-signal probe naming goal/intention tracking), 29639 "
        "(goal-close-pairing semantic CAP naming satisfy-vs-restate as the residual), 29642 "
        "(fork-a coherence-margin falsification), and 29643 (fork-b supplied-schema ceiling, "
        "whose anne_goal_014 miss this probe's unstated-goal arm independently recovers via a "
        "different mechanism) -- no new domain claimed, this is a targeted fork-reframing "
        "diagnostic over the same narrow Anne-goal-intention gold slice already in active use "
        "across the composing atoms, not a rediscovery of unrelated prior work."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}


def atomic_append_jsonl(path, record):
    line = json.dumps(record, ensure_ascii=True) + "\n"
    dir_ = os.path.dirname(path)
    with open(path, "rb") as f:
        existing = f.read()
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(existing)
            tmp.write(line.encode("utf-8"))
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def verify_load(path, expect_seq=None, expect_atom_id=None):
    found = False
    count = 0
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            count += 1
            d = json.loads(raw.decode("utf-8"))
            if expect_seq is not None and d.get("seq") == expect_seq:
                found = True
            if expect_atom_id is not None and d.get("atom_id") == expect_atom_id:
                found = True
    return found, count


def make_ledger_entry(seq, atom, corpus, decision, note):
    now = time.time()
    return {
        "seq": seq,
        "atom_id": atom["atom_id"],
        "corpus": corpus,
        "decision": decision,
        "note": note,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
        "ts": now,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now)),
        "ts_day": time.strftime("%Y-%m-%d", time.gmtime(now)),
    }


def main():
    now = time.time()
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now))
    ts_day = time.strftime("%Y-%m-%d", time.gmtime(now))

    ATOM_CONTENT_AWARENESS_CEILING["ts"] = now
    ATOM_CONTENT_AWARENESS_CEILING["ts_iso"] = ts_iso
    ATOM_CONTENT_AWARENESS_CEILING["ts_day"] = ts_day

    ledger_entry = make_ledger_entry(
        SEQ_CONTENT_AWARENESS_CEILING, ATOM_CONTENT_AWARENESS_CEILING, "math",
        "MEASURED_MECHANISM CERT +0 (content-awareness ceiling diagnostic, decisive fork-"
        "reframe). Independently recomputed off data/exp_content_awareness_ceiling_probe_v1/"
        "metrics.json raw per-item records (not verdict_msg alone): content-alone misranks 3/3 "
        "satisfy-vs-restate (dt +0.0012/+0.0046/+0.1677, restate scores >= satisfy on content "
        "similarity alone -- same-words trap confirmed); content+hand-coded-structure ranks "
        "2/3 correctly (anne_goal_002 remains wrong, disclosed limitation); unstated-goal "
        "recovery 3/3 (incl anne_goal_014, the item atom 29643's regex-schema missed); combined "
        "ceiling 5/6=0.8333, small-N/directional. Confirmed BGE embedding not imported anywhere "
        "under hdlab/ -- diagnostic-only, lock-compliant, discarded. REFRAMES the deep-earn "
        "fork: earn STRUCTURE-AWARE CONTENT (structure cheap/glass-box, content the real earn-"
        "problem), not a standalone content/semantic encoder. Composes 29634/29639/29642/29643 "
        "+ design doc 4c8a26aed.",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute directly off metrics.json raw "
        "per-item blocks + direct source-file (experiments/exp_content_awareness_ceiling_"
        "probe_v1.py) inspection confirming structure signal is hand-coded glass-box, and grep "
        "of hdlab/ confirming zero imports of this module or sentence-transformers/bge -- BGE "
        "confirmed discarded, not wired. Commit 22b243508 (cell) + 4c8a26aed (design doc) both "
        "verified present in git log. LOCAL-ONLY.",
    )

    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_CONTENT_AWARENESS_CEILING)
    atomic_append_jsonl(LEDGER_PATH, ledger_entry)

    found, count = verify_load(
        MATH_ATOMS_PATH,
        expect_seq=SEQ_CONTENT_AWARENESS_CEILING,
        expect_atom_id=ATOM_CONTENT_AWARENESS_CEILING["atom_id"],
    )
    assert found, f"FAIL: atom seq={SEQ_CONTENT_AWARENESS_CEILING} not found in {MATH_ATOMS_PATH} after write"

    found_ledger, ledger_count = verify_load(LEDGER_PATH, expect_seq=SEQ_CONTENT_AWARENESS_CEILING)
    assert found_ledger, f"FAIL: ledger entry seq={SEQ_CONTENT_AWARENESS_CEILING} not found in {LEDGER_PATH} after write"

    print(f"OK: atom seq={SEQ_CONTENT_AWARENESS_CEILING} written to {MATH_ATOMS_PATH} ({count} total lines)")
    print(f"OK: ledger entry written to {LEDGER_PATH} ({ledger_count} total lines)")
    print("atom_id:")
    print(f"  seq={ATOM_CONTENT_AWARENESS_CEILING['seq']} corpus={ATOM_CONTENT_AWARENESS_CEILING['corpus']} -> {ATOM_CONTENT_AWARENESS_CEILING['atom_id'][:120]}...")


if __name__ == "__main__":
    main()
