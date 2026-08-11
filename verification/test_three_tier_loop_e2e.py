"""Scaffold-free end-to-end witness for hdlab.three_tier_loop (2026-08-11) -- the FULL
gap -> STATE-OF-MIND -> GATHER -> REASON -> PARSE -> GATE -> FOUNDATION/MIDDLE cycle, composed
entirely of already-validated real hdlab organs (no mocks, no synthetic-only branch, no LLM):

  hdlab.situation_model_accumulate.RelationRegister   (STATE OF MIND)
  hdlab.gather_reason.ca3_relevance_gather/fanout_two_hop (GATHER + REASON, promoted 2026-08-11)
  hdlab.grounding_acquisition_loop.context_vector/Library/consolidation_pass (PARSE + GATE)
  hdlab.prelim_tier.TierState/update_prelim_and_generalize (MIDDLE TIER, promoted 2026-08-11)
  hdlab.hd_fact_store.HDFactStore                      (FOUNDATION)
  hdlab.three_tier_loop.ThreeTierLoop                  (the assembly under test)

Real KG universe: 4 subjects (1 well-corroborated "GAP_A", 3 related sub-threshold "GAP_B"
family members), each with its own REAL two-hop chain (subject -[FATE]-> material
-[BRIDGE]-> whole) ingested into real hdlab.kg_traversal.KGStore instances, and a REAL
hdlab.situation_model_accumulate.RelationRegister binding each subject's own material to a
GOAL role -- the CA3 gather + K=2 fan-out that resolves each gap's candidate answer is the
ACTUAL reasoning mechanism running (deterministic; not a hand-typed placeholder answer).

Three required cycle assertions (can-fail; a wrong-tier answer at any checkpoint below fails
the test, via _resolve_with_priority_sentinel's raw-fallback AssertionError plus explicit
tier-tag assertions at every checkpoint):
  (a) GAP_A: 8 well-corroborated encounters -> the strict GATE promotes it directly ->
      answers FOUNDATION_RESOLVED.
  (b) GAP_B family (3 distinct, related subjects): 5 encounters each (sub-threshold: below the
      exposure=8 promotion floor, but at/above the retain floor) -> the strict GATE never
      promotes any of them (still PENDING, never even reaches "GROUNDED" until re-evaluated) ->
      each is RETAINED in the MIDDLE tier and answered from there, never lost, never promoted.
  (c) RE-ENCOUNTER: 7 more (middle-only) encounters per GAP_B member (12 total each) -> the
      MIDDLE tier's own CA3/DG near-concept SWEEP clusters the 3 related members together and
      their COMBINED evidence (36 traces >= the cluster-grain floor of 32) crosses the SAME
      strict gate -> all 3 promote into FOUNDATION (per ThreeTierLoop's documented ASSEMBLY
      DECISION: combined-evidence promotion is wired to land in the identical foundation store
      the single-item GATE uses) -> answers flip from MIDDLE_RESOLVED to FOUNDATION_RESOLVED.

Passes with tracing=False (no trace bus configured anywhere in this file; hdlab.tracing.emit
is a no-op by default -- nothing here opts in).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch  # noqa: E402

import hdlab.three_tier_loop as ttl  # noqa: E402
from hdlab.gather_reason import build_codebook, real_to_concat  # noqa: E402
from hdlab.grounding_acquisition_loop import context_vector  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.script_grain_acquisition_loop import calibrate_novelty_threshold  # noqa: E402
from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec  # noqa: E402

RELATION = "GAP_FACT"
FATE_REL = "DESTROY"
BRIDGE_REL = "BRIDGE"
GAPB_CLUSTER = "b_family"
GAPA_CLUSTER = "a_solo"


def _build_universe():
    """Real KG + RelationRegister fixture: 1 GAP_A subject + 3 GAP_B-family subjects, each with
    its own genuine 2-hop chain. Returns everything a per-subject gather_and_reason call needs."""
    subjects = {
        "p_a": ("m_a", "w_a"),
        "p_b1": ("m_b1", "w_b1"),
        "p_b2": ("m_b2", "w_b2"),
        "p_b3": ("m_b3", "w_b3"),
    }
    ents: list = []
    for s, (m, w) in sorted(subjects.items()):
        ents.extend([s, m, w])
    ent_idx = {name: i for i, name in enumerate(ents)}
    n_ent = len(ents)

    gen1 = torch.Generator().manual_seed(31337)
    hop1 = KGStore(n_ent=n_ent, n_rel=1, n_dim=1024, generator=gen1)
    hop1_rows = [[ent_idx[s], 0, ent_idx[m]] for s, (m, _w) in subjects.items()]
    hop1.ingest_triples(torch.tensor(hop1_rows, dtype=torch.long))

    gen2 = torch.Generator().manual_seed(31338)
    hop2 = KGStore(n_ent=n_ent, n_rel=1, n_dim=1024, generator=gen2)
    hop2_rows = [[ent_idx[m], 0, ent_idx[w]] for _s, (m, w) in subjects.items()]
    hop2.ingest_triples(torch.tensor(hop2_rows, dtype=torch.long))

    fhrr_d = 512
    mat_gen = torch.Generator().manual_seed(31339)
    materials = sorted(m for m, _w in subjects.values())
    mat_vecs = {m: unit_phase_vec(fhrr_d, mat_gen) for m in materials}
    mat_names, codebook = build_codebook(mat_vecs)

    reg_gen = torch.Generator().manual_seed(31340)
    reg = RelationRegister(d=fhrr_d, generator=reg_gen)
    for s, (m, _w) in subjects.items():
        reg.bind_filler(s, "GOAL", mat_vecs[m])

    return subjects, ent_idx, n_ent, hop1, hop2, mat_names, codebook, reg


def _resolve_candidate(subject: str, subjects, ent_idx, n_ent, hop1, hop2, mat_names, codebook, reg) -> str:
    """Run the REAL GATHER+REASON pass for one subject: decode its state-of-mind query vector,
    CA3-gather the relevant material, K=2 fan-out reason to the candidate whole. Returns the
    candidate's entity NAME (not index) -- the item this gap's evidence will accumulate under."""
    query = real_to_concat(reg.decode_filler(subject, "GOAL"))
    result = ttl.gather_and_reason(query, mat_names, codebook, ent_idx, hop1, hop2,
                                   ent_idx[subject], 0, 0, k1=5, k2=5, n_ent=n_ent)
    idx_to_name = {v: k for k, v in ent_idx.items()}
    top1_idx = result["top1_idx"]
    assert top1_idx is not None, f"REASON produced no candidate for {subject}: {result}"
    return idx_to_name[top1_idx]


def _episode_text(subject: str, candidate: str, day: int) -> str:
    phrasing = ["was affected again", "showed the same downstream effect",
                "was implicated once more", "matched the prior finding"]
    return (f"Reasoning over {subject} nominated {candidate}, which {phrasing[day % len(phrasing)]} "
            f"during independent observation number {day}.")


def _raw_source_sentinel(pk: str) -> None:
    raise AssertionError(
        f"raw external multi-source GATHER reached for {pk!r} despite a live FOUNDATION or "
        f"MIDDLE hit -- priority-order routing violated (wrong tier / no tier answered)")


def _resolve_with_priority_sentinel(loop: "ttl.ThreeTierLoop", pk: str, expected_tag: str) -> str:
    """FOUNDATION -> MIDDLE -> raw-fallback-sentinel (raises if reached). Additionally asserts
    the resolved tag matches expected_tag exactly -- a wrong-tier answer (e.g. MIDDLE resolving
    when FOUNDATION should already have it, or vice versa) fails this assertion directly, not
    just the raw-fallback case."""
    tag, obj = loop.answer(pk)
    if tag == "UNRESOLVED":
        _raw_source_sentinel(pk)
    assert tag == expected_tag, f"{pk}: expected tier {expected_tag!r}, got {tag!r} (object={obj!r})"
    assert obj == "POS", f"{pk}: expected resolved polarity POS, got {obj!r}"
    return tag


def test_full_cycle_gap_to_foundation_or_middle() -> None:
    subjects, ent_idx, n_ent, hop1, hop2, mat_names, codebook, reg = _build_universe()
    candidates = {s: _resolve_candidate(s, subjects, ent_idx, n_ent, hop1, hop2, mat_names, codebook, reg)
                 for s in subjects}
    # sanity: the REAL reasoning mechanism recovered each subject's OWN true whole (not a
    # hand-typed placeholder -- see _resolve_candidate).
    for s, (_m, w) in subjects.items():
        assert candidates[s] == w, f"REASON recovered {candidates[s]!r} for {s}, expected {w!r}"

    store = HDFactStore(n_dim=2048, seed=777, use_index=True)
    loop = ttl.ThreeTierLoop(store, seed_base=555, n_dim=2048, relation=RELATION)

    def cluster_key_fn(pk: str) -> str:
        subject, _relation, _candidate = ttl.parse_gap_item_key(pk)
        return GAPB_CLUSTER if subject in ("p_b1", "p_b2", "p_b3") else GAPA_CLUSTER

    calib = calibrate_novelty_threshold(
        matched_pairs=[(ttl.gap_register_fn(ttl.gap_item_key("p_b1", RELATION, candidates["p_b1"]),
                                            GAPB_CLUSTER, "POS"),
                       ttl.gap_register_fn(ttl.gap_item_key("p_b2", RELATION, candidates["p_b2"]),
                                           GAPB_CLUSTER, "POS"))],
        wrong_pairs=[(ttl.gap_register_fn(ttl.gap_item_key("p_b1", RELATION, candidates["p_b1"]),
                                          GAPB_CLUSTER, "POS"),
                     ttl.gap_register_fn(ttl.gap_item_key("p_a", RELATION, candidates["p_a"]),
                                         GAPA_CLUSTER, "POS"))])
    assert calib["discriminates"], f"calibration setup must discriminate: {calib}"
    novelty_thresh = calib["novelty_thresh"]

    pk_a = ttl.gap_item_key("p_a", RELATION, candidates["p_a"])
    pk_b = {s: ttl.gap_item_key(s, RELATION, candidates[s]) for s in ("p_b1", "p_b2", "p_b3")}

    # ---- pre-encounter: everything UNRESOLVED --------------------------------------------
    assert loop.answer(pk_a) == ("UNRESOLVED", None)
    for pk in pk_b.values():
        assert loop.answer(pk) == ("UNRESOLVED", None)

    # ---- GAP_A: 8 well-corroborated encounters -------------------------------------------
    for i in range(8):
        cvec = context_vector(_episode_text("p_a", candidates["p_a"], i))
        loop.encounter(pk_a, "POS", cvec, f"a_ep{i}", pass_idx=0)

    r1 = loop.consolidate(1, cluster_key_fn, novelty_thresh, gate_kwargs={"register": False})
    assert loop.library.items[pk_a].status == "PENDING", (
        "GAP_A must NOT bank on the very pass it first reaches min_confirm (intervening-pass rule)")
    # (b)-shape checkpoint for GAP_A too: MIDDLE already has it (no intervening-pass rule there).
    tag_mid = _resolve_with_priority_sentinel(loop, pk_a, "MIDDLE_RESOLVED")
    assert tag_mid == "MIDDLE_RESOLVED"

    r2 = loop.consolidate(2, cluster_key_fn, novelty_thresh, gate_kwargs={"register": False})
    assert loop.library.items[pk_a].status == "GROUNDED_POS", (
        f"GAP_A must bank on the intervening pass, got {loop.library.items[pk_a].status}")
    promoted_a = {e["lemma"]: e["promoted"] for e in r2["gate"]["promotion_log"]}
    assert promoted_a.get(pk_a) is True, f"GAP_A must promote (exposure=8>=8, consistency=1.0): {r2['gate']}"

    # ---- ASSERTION (a): a reasoned fact with enough corroboration PASSES the gate ---------
    tag_a = _resolve_with_priority_sentinel(loop, pk_a, "FOUNDATION_RESOLVED")
    assert tag_a == "FOUNDATION_RESOLVED"

    # ---- GAP_B family: 5 sub-threshold encounters each ------------------------------------
    for s in ("p_b1", "p_b2", "p_b3"):
        for i in range(5):
            cvec = context_vector(_episode_text(s, candidates[s], i))
            loop.encounter(pk_b[s], "POS", cvec, f"{s}_ep{i}", pass_idx=0)

    r3 = loop.consolidate(3, cluster_key_fn, novelty_thresh, gate_kwargs={"register": False})
    for s in ("p_b1", "p_b2", "p_b3"):
        promoted_this_pass = {e["lemma"]: e["promoted"] for e in r3["gate"]["promotion_log"]}
        assert pk_b[s] not in promoted_this_pass or not promoted_this_pass[pk_b[s]], (
            f"{s}: must NOT promote via the strict single-item gate at exposure=5<8, log={r3['gate']}")
    assert r3["middle"]["n_combined_promoted_this_pass"] == 0, (
        f"combined-evidence must NOT fire yet (15 traces < cluster floor 32): {r3['middle']}")

    # ---- ASSERTION (b): sub-threshold facts FAIL the gate -> RETAINED in middle, not lost -
    for s in ("p_b1", "p_b2", "p_b3"):
        tag_b = _resolve_with_priority_sentinel(loop, pk_b[s], "MIDDLE_RESOLVED")
        assert tag_b == "MIDDLE_RESOLVED", f"{s} must be answerable from MIDDLE, not lost, not FOUNDATION yet"

    # ---- RE-ENCOUNTER: 7 more middle-only encounters per member (12 total each) -----------
    for s in ("p_b1", "p_b2", "p_b3"):
        for i in range(5, 12):
            cvec = context_vector(_episode_text(s, candidates[s], i))
            loop.encounter(pk_b[s], "POS", cvec, f"{s}_ep{i}", pass_idx=3, also_strict=False)

    r4 = loop.consolidate(4, cluster_key_fn, novelty_thresh, gate_kwargs={"register": False})
    assert r4["middle"]["n_combined_promoted_this_pass"] == 3, (
        f"combined evidence (3 members x 12 traces = 36 >= cluster floor 32) must cross the "
        f"gate and promote all 3 members in this pass, got {r4['middle']}")

    # ---- ASSERTION (c): re-encounter -> middle answered FIRST (already proven above) -> ---
    # ---- accumulated (combined) evidence eventually crosses the gate -> promotes ----------
    for s in ("p_b1", "p_b2", "p_b3"):
        tag_c = _resolve_with_priority_sentinel(loop, pk_b[s], "FOUNDATION_RESOLVED")
        assert tag_c == "FOUNDATION_RESOLVED", (
            f"{s} must now resolve from FOUNDATION after combined-evidence promotion")

    # ---- honest cross-check: FOUNDATION facts are genuinely glass-box recoverable ---------
    for pk in [pk_a] + list(pk_b.values()):
        hit = store.query(*[pk, RELATION])
        assert hit and hit[0]["object"] == "POS" and hit[0]["subject"] == pk, (
            f"foundation store round-trip failed for {pk}: {hit}")


def _run_all() -> None:
    test_full_cycle_gap_to_foundation_or_middle()


if __name__ == "__main__":
    _run_all()
    print("[test_three_tier_loop_e2e] PASS: full gap -> state-of-mind -> gather -> reason -> "
          "parse -> gate -> foundation/middle cycle reproduced end-to-end (tracing=False), "
          "all 3 cycle assertions + priority-order sentinels hold.")
