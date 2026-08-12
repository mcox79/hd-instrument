"""Scaffold-free witness for hdlab.gap_detector (2026-08-11) -- the ONLINE, AUTONOMOUS
gap-detection organ closing architecture-audit finding #3 (notes/architecture_audit_2026-08-11.md
TIER-2 item 3): "gap-detection has no autonomous component (MISLABEL): every 'gap' is an offline
KB set-difference or a hand-picked curriculum."

Exercises the REAL hdlab.hd_fact_store.HDFactStore + hdlab.cleanup_family.iterative_attractor
(no mocks) through hdlab.gap_detector.GapDetector's public API. Four assertions map directly to
the four pre-registered can-fail tests in
experiments/exp_gap_detection_autonomous_confidence_v1.py:

  (a) SIGNAL DETECTION: a stream mixing genuinely-stored facts with verified-absent novel facts
      separates cleanly at the pre-registered floor (0.625) -- zero false alarms, all novel
      flagged.
  (b) NOT-A-LOOKUP: the SAME probes, with the confidence signal ablated (replaced by
      fixed-seed noise uncorrelated with true label), lose almost all separation -- proving the
      decision quality depends on the REAL CA3/CA1 margin, not a hidden shortcut.
  (c) SCRAMBLE / KB-STATE-SENSITIVITY: a fact correctly recognized as known BEFORE a live-KB
      lesion (via HDFactStore's own store()-ingest-vet REPLACE resolution) is detected as a gap
      AFTER -- proving refresh() reads the store's actual live consolidation state, not a frozen
      snapshot.
  (d) EMPTY-KB EDGE CASE: every probe against an empty store is a gap (codebook_size == 0).

Passes with tracing=False (no trace bus configured anywhere in this file).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.gap_detector import GapDetector  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402

FLOOR = 0.625


def _build_kb(seed: int, n_dim: int = 4096, n_known: int = 40):
    cardinality = {"rel_a": "FUNCTIONAL"}
    store = HDFactStore(n_dim=n_dim, seed=seed, relation_cardinality=cardinality)
    known = [(f"subj_{i:03d}", "rel_a", f"obj_{i:03d}") for i in range(n_known)]
    for s, r, o in known:
        res = store.store(s, r, o, "kb_source", "TRUST_HIGH")
        assert res.resolution == "CLEAN_STORE", res
    return store, known


def test_signal_detection_zero_false_alarms_all_novel_flagged() -> None:
    store, known = _build_kb(seed=101)
    novel = [(f"novel_subj_{i:03d}", "rel_a", f"novel_obj_{i:03d}") for i in range(40)]
    det = GapDetector(store, floor=FLOOR)
    det.refresh()
    known_res = det.batch_familiarity(known)
    novel_res = det.batch_familiarity(novel)
    false_alarms = sum(1 for r in known_res if r.is_gap)
    hits = sum(1 for r in novel_res if r.is_gap)
    assert false_alarms == 0, f"known facts incorrectly flagged as gaps: {false_alarms}/{len(known)}"
    assert hits == len(novel), f"novel facts NOT flagged as gaps: {hits}/{len(novel)}"
    known_margins = [r.margin for r in known_res]
    novel_margins = [r.margin for r in novel_res]
    assert min(known_margins) > 0.99, f"known margins should be exact-match ~1.0: {min(known_margins)}"
    assert max(novel_margins) < FLOOR, f"novel margins should stay below floor: {max(novel_margins)}"


def test_not_a_lookup_ablation_collapses_separation() -> None:
    store, known = _build_kb(seed=102)
    novel = [(f"novel_subj_{i:03d}", "rel_a", f"novel_obj_{i:03d}") for i in range(40)]
    det = GapDetector(store, floor=FLOOR, ablation_seed=777)
    det.refresh()
    real_known = [r.margin for r in det.batch_familiarity(known)]
    real_novel = [r.margin for r in det.batch_familiarity(novel)]
    ablated_known = [r.margin for r in det.batch_familiarity(known, use_confidence_signal=False)]
    ablated_novel = [r.margin for r in det.batch_familiarity(novel, use_confidence_signal=False)]
    real_gap = (sum(real_known) / len(real_known)) - (sum(real_novel) / len(real_novel))
    ablated_gap = (sum(ablated_known) / len(ablated_known)) - (sum(ablated_novel) / len(ablated_novel))
    assert real_gap > 0.5, f"real signal must cleanly separate known/novel: {real_gap}"
    assert abs(ablated_gap) < 0.35, f"ablated signal must NOT reliably separate known/novel: {ablated_gap}"
    # arms-must-differ (META_RULE_AF-style): the two margin vectors are not identical.
    assert real_known != ablated_known, "ablation had no effect -- use_confidence_signal is not wired"


def test_scramble_flips_known_fact_to_gap() -> None:
    store, known = _build_kb(seed=103)
    lesion_subject, relation, original_obj = known[7]
    # re-store the lesion target at TRUST_MID so a later TRUST_HIGH conflict can REPLACE it
    # (store() is idempotent-order here: re-storing the same (s,r,o) at MID after HIGH would not
    # downgrade trust, so build a fresh store where the lesion target starts at MID).
    store2 = HDFactStore(n_dim=4096, seed=103, relation_cardinality={"rel_a": "FUNCTIONAL"})
    for i, (s, r, o) in enumerate(known):
        trust = "TRUST_MID" if i == 7 else "TRUST_HIGH"
        res = store2.store(s, r, o, "kb_source", trust)
        assert res.resolution == "CLEAN_STORE", res
    det = GapDetector(store2, floor=FLOOR)
    det.refresh()
    before = det.familiarity(lesion_subject, relation, original_obj)
    assert before.is_gap is False, f"pre-lesion known fact must NOT be a gap: {before}"
    replace_res = store2.store(lesion_subject, relation, "lesion_replacement_obj", "lesion_src", "TRUST_HIGH")
    assert replace_res.resolution == "REPLACE", replace_res
    det.refresh()
    after = det.familiarity(lesion_subject, relation, original_obj)
    assert after.is_gap is True, f"post-lesion the OLD fact must be detected as a gap: {after}"


def test_empty_kb_every_probe_is_a_gap() -> None:
    store = HDFactStore(n_dim=1024, seed=104, relation_cardinality={"rel_a": "FUNCTIONAL"})
    det = GapDetector(store, floor=FLOOR)
    n = det.refresh()
    assert n == 0
    r = det.familiarity("anyone", "rel_a", "anything")
    assert r.is_gap is True
    assert r.codebook_size == 0


def _run_all() -> None:
    test_signal_detection_zero_false_alarms_all_novel_flagged()
    test_not_a_lookup_ablation_collapses_separation()
    test_scramble_flips_known_fact_to_gap()
    test_empty_kb_every_probe_is_a_gap()


if __name__ == "__main__":
    _run_all()
    print("[test_gap_detector] PASS: signal-detection (zero false alarms, all novel flagged) + "
         "not-a-lookup ablation collapse + scramble-flips-known-to-gap + empty-KB edge case, "
         "all against the REAL hdlab.hd_fact_store.HDFactStore + hdlab.cleanup_family."
         "iterative_attractor code path (tracing=False).")
