"""
A5-gated atomization: CAUSAL-INFERENCE-COLLAPSES-TO-ADJACENCY (McGuffey causal-relation gold fair-test negative).

AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off
data/eval_gold_mention_role_mcguffey_v1/gold_causal_relations_v1.jsonl
(commit f04c6cc4c, miner tools/gen_causal_relations_gold.py), NOT off any
verdict_msg or spawn-prompt summary.

Writes ONE atom (seq 29626) to data/substrate_index/meta/atoms.jsonl and ONE
matching entry to data/substrate_index/meta/cert_ledger.jsonl, atomically
(tmp -> os.replace), then verify-loads both files and runs an integrity check
before declaring success. LOCAL-ONLY: no origin push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ = 29626

RECOMPUTE_NOTE = (
    "Independent .venv recompute off gold_causal_relations_v1.jsonl (n=208, commit f04c6cc4c): "
    "clause_gap distribution {1: 207, 3: 1} -> adjacent (gap=1) = 207/208 = 0.9952, matching the "
    "claimed 99.5%. verbatim substring guard: cause_clause AND effect_clause both found verbatim in "
    "source_paragraph_verbatim for 208/208 rows (0 failures) -> confirms the 100% verbatim claim. "
    "textual_order distribution {cause_before_effect: 78, effect_before_cause: 130} -> reversed frac "
    "130/208 = 0.6250, matching the claimed 62.5%. connective->textual_order mapping: 0/10 distinct "
    "connectives show more than one textual_order value across their instances (fully deterministic) "
    "-> confirms the 'connective identity alone solves direction, no mechanism needed' lookup-table "
    "claim. connective frequency: for_midsentence=97 (46.6% of 208, matches the ~47% caveat), "
    "thus=21 (10.1%, the borderline-tagged connective), in_order_to=14 (6.7%), because=33, so_that=16, "
    "for_sentence_initial=11, so_sentence_initial=10, so_midsentence=3, since_sentence_initial=2, "
    "therefore=1."
)

ATOM = {
    "atom_id": (
        "meta::causal_connective_inference_collapses_to_clause_adjacency_on_mcguffey_"
        "n208_verbatim_100pct_adjacent_207of208_99p5pct_gap1_reversed_order_62p5pct_but_"
        "fully_connective_deterministic_0_of_10_connectives_multivalued_lookup_table_solves_"
        "direction_no_mechanism_needed_trivial_bind_neighbor_baseline_scores_99p5pct_"
        "recency_floor_trap_falsifies_069039afd_build_now_scoping_reframe_needed_"
        "multicandidate_distractor_or_connective_blinding_or_harder_corpus_5th_mcguffey_"
        "too_simple_collapse_this_session_gold_unverified_thus_borderline_"
        "for_midsentence_47pct_LOCAL_ONLY"
    ),
    "seq": SEQ,
    "op": "insert",
    "corpus": "meta",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "FAIR-TEST NEGATIVE that falsifies the 069039afd scoping call (connective-cued causal-link "
        "inference = BUILD-NOW). Mining measurement on real McGuffey (n=208 causal instances, 100% "
        "verbatim substring-guard pass) shows the task COLLAPSES to trivial clause-adjacency: 207/208 "
        "(99.5%) instances have clause_gap=1 (cause and effect clauses immediately adjacent), so a "
        "'bind the neighboring clause' baseline with ZERO causal reasoning already scores ~99.5%. The "
        "reversed-textual-order rate (62.5%, effect_before_cause) looked like it might require real "
        "direction-inference, but connective identity alone is a fully deterministic lookup table for "
        "textual_order (0/10 connectives take more than one order value across all their instances) -- "
        "so a build here would learn 'so_that -> cause_before_effect, because -> effect_before_cause' "
        "etc, not a causal mechanism. Net: the connective-cued causal task on McGuffey is construction-"
        "determined (recency-floor trap), same pattern as coref-recency-floor / situation-model-identity-"
        "demanding / autonomy-content-gated collapses earlier this session (5th instance)."
    ),
    "anchor": "gold_causal_relations_v1",
    "anchor_name": "causal_connective_gold_mining_v1_mcguffey_g5g6",
    "cell": "data/eval_gold_mention_role_mcguffey_v1/gold_causal_relations_v1.jsonl",
    "headline": (
        "Causal-connective inference collapses to clause-adjacency on McGuffey: 207/208 (99.5%) "
        "gap=1, trivial adjacency baseline scores ~99.5%, reversed-order (62.5%) fully determined by "
        "connective identity (0/10 connectives multivalued) -- FALSIFIES 069039afd build-now scoping, "
        "needs reframe (multi-candidate distractors / connective-blinding) or harder corpus."
    ),
    "key_metrics": {
        "n": 208,
        "clause_gap_distribution": {"1": 207, "3": 1},
        "adjacent_frac": 0.9952,
        "verbatim_substring_guard_pass_frac": 1.0,
        "textual_order_distribution": {"cause_before_effect": 78, "effect_before_cause": 130},
        "reversed_order_frac": 0.625,
        "connectives_with_multivalued_textual_order": 0,
        "distinct_connectives": 10,
        "connective_counts": {
            "for_midsentence": 97, "because": 33, "thus": 21, "so_that": 16,
            "in_order_to": 14, "for_sentence_initial": 11, "so_sentence_initial": 10,
            "so_midsentence": 3, "since_sentence_initial": 2, "therefore": 1,
        },
        "for_midsentence_frac": 0.466,
        "thus_frac": 0.101,
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": RECOMPUTE_NOTE,
    "composes_seq": [],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ - 1,
    "honest_scope": (
        "Gold is UNVERIFIED (gold_verified=false on every row; Director has not manually spot-checked "
        "labels) -- per-instance cause/effect clause labels may contain noise, and 'thus' (10.1% of "
        "instances) is flagged borderline (thus can be discourse-continuative not strictly causal in "
        "some McGuffey usages), for_midsentence (46.6% of instances) is the largest and least-constrained "
        "connective class. HOWEVER the adjacency measurement (clause_gap distribution) and the "
        "connective->order determinism check are STRUCTURAL properties of clause position and connective "
        "identity, not of the cause/effect semantic label -- they stand regardless of per-instance label "
        "noise. This atom certifies the STRUCTURAL collapse finding (adjacency + lookup-table direction), "
        "not the semantic correctness of individual gold rows. Composes the session's now-5th McGuffey-"
        "too-simple collapse pattern (coref recency-floor, situation-model identity-demanding, autonomy "
        "content-gated, causal-connective adjacency-collapse) -- all gated on McGuffey's low content "
        "richness/density, not on the underlying comprehension mechanism being unbuildable."
    ),
    "framing_correction": (
        "069039afd scoped connective-cued causal-link inference as BUILD-NOW; this measurement shows "
        "that scoping call under-weighted McGuffey's short-paragraph structure (causal connectives "
        "almost always link immediately adjacent clauses in graded-reader prose). Correct framing: "
        "NOT build-now as scoped -- either (a) reframe as a multi-candidate/distractor-paragraph task "
        "so a model must actually discriminate the correct antecedent/consequent clause among several "
        "candidates (adjacency alone would no longer suffice), (b) blind the connective identity at "
        "train/eval time so direction can't be read off a lookup table, or (c) source from a richer/"
        "longer-form corpus with genuine long-range causal chains. Building the connective-cued task "
        "as originally scoped would produce a false-positive capability claim: a trivial nearest-clause-"
        "binder would pass the fair-test bar without any causal reasoning."
    ),
    "revival_criteria": (
        "Revive as BUILD-NOW once EITHER: (1) a distractor-paragraph variant of the gold set is mined "
        "where the correct cause/effect clause must be picked from >=3 candidate clauses at varying "
        "distances (not just the true pair) so nearest-neighbor adjacency baseline provably underperforms "
        "a real discriminator by a material margin (pre-register the margin bar), or (2) a harder/longer-"
        "form corpus is sourced with a measured non-adjacent-instance rate materially above ~5% (McGuffey's "
        "measured non-adjacent rate here is 0.48%), or (3) connective identity is stripped/blinded and the "
        "reversed-order discrimination task is re-measured to confirm it survives without the lookup-table "
        "shortcut."
    ),
    "primitive_assessment": (
        "No new primitive; this is a fair-test measurement (gold-mining + structural distribution "
        "analysis) that PREVENTS a construction-determined false-positive build. Reusable methodology: "
        "before building a discourse-relation-inference capability, measure the gold's own adjacency/"
        "distance distribution and any lookup-table-solvable confound (here: connective identity -> "
        "order) BEFORE dispatching a build."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM fair-test negative on a scoping call, not a HARD_FAIL cell).",
    "fairness_verdict": (
        "FAIR: independent recompute off the raw gold file (not off any prior summary) reproduces every "
        "cited number exactly (207/208 adjacent, 100% verbatim, 62.5% reversed, 0/10 multivalued "
        "connectives, 46.6% for_midsentence). The verdict does not claim the causal-relation TASK is "
        "unbuildable in general -- only that THIS gold/corpus combination collapses to a trivial baseline, "
        "which is a scoping/corpus finding, not a capability ceiling claim (per the flat-learning-result "
        "discipline: this is a diagnosed corpus-construction issue, not an intrinsic-ceiling claim)."
    ),
    "cross_arc_overlap": (
        "Composes the session's running McGuffey-too-simple pattern (coref recency-floor collapse, "
        "situation-model identity-demanding collapse, autonomy content-gating, this causal-adjacency "
        "collapse = 5th instance). No prior atom in math/meta corpus specifically measures causal-"
        "connective adjacency distributions; this is a novel structural finding, not a rediscovery."
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


def main():
    now = time.time()
    ATOM["ts"] = now
    ATOM["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now))
    ATOM["ts_day"] = time.strftime("%Y-%m-%d", time.gmtime(now))

    ledger_entry = {
        "seq": SEQ,
        "atom_id": ATOM["atom_id"],
        "corpus": "meta",
        "decision": (
            "MEASURED_MECHANISM CERT +0 (fair-test negative; falsifies 069039afd build-now scoping for "
            "connective-cued causal-link inference on McGuffey). Independent recompute off "
            "gold_causal_relations_v1.jsonl (n=208) confirms EXACTLY: clause_gap {1:207, 3:1} -> "
            "adjacent=99.52%; verbatim guard 208/208 pass; textual_order {cause_before_effect:78, "
            "effect_before_cause:130} -> reversed=62.50%; connective->order fully deterministic (0/10 "
            "connectives multivalued); for_midsentence=46.6%, thus=10.1%. Trivial clause-adjacency "
            "baseline would score ~99.5% with zero causal reasoning; reversed-order signal is a "
            "connective-identity lookup table, not inference. 5th McGuffey-too-simple collapse this "
            "session (composes coref-recency-floor / situation-model-identity / autonomy-content-gating "
            "pattern). Honest scope: gold is UNVERIFIED (per-row labels), but the adjacency + lookup-"
            "table-determinism measurements are STRUCTURAL and stand independent of label noise."
        ),
        "note": (
            "AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off "
            "data/eval_gold_mention_role_mcguffey_v1/gold_causal_relations_v1.jsonl (commit f04c6cc4c), "
            "NOT off verdict_msg or spawn-prompt summary. LOCAL-ONLY; no origin push; no remote persist."
        ),
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
        "ts": now,
        "ts_iso": ATOM["ts_iso"],
        "ts_day": ATOM["ts_day"],
    }

    # A5-gate: atomic write both files (tmp -> os.replace)
    atomic_append_jsonl(ATOMS_PATH, ATOM)
    atomic_append_jsonl(LEDGER_PATH, ledger_entry)

    # Verify-load
    atoms_found, atoms_count = verify_load(ATOMS_PATH, expect_seq=SEQ, expect_atom_id=ATOM["atom_id"])
    ledger_found, ledger_count = verify_load(LEDGER_PATH, expect_seq=SEQ, expect_atom_id=ATOM["atom_id"])

    assert atoms_found, "FAIL: atom not found in atoms.jsonl after write"
    assert ledger_found, "FAIL: ledger entry not found in cert_ledger.jsonl after write"

    print(f"OK: atom seq={SEQ} written to {ATOMS_PATH} ({atoms_count} total lines)")
    print(f"OK: ledger entry seq={SEQ} written to {LEDGER_PATH} ({ledger_count} total lines)")
    print(f"atom_id={ATOM['atom_id']}")


if __name__ == "__main__":
    main()
