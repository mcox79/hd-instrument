"""
A5-gated atomization: state-of-mind WSM-coupling REAL-CORPUS v2 -> MEASURED_MECHANISM boundary (2026-07-17).

Director-AUTHORIZED (standing atom policy: bank when ready; this bound is ready + not about-to-be-updated --
the revival is a NEW cell, not an update to this one). SUPERSEDES the v1 wiring-proof (b56e77203).

VET independently off-disk (.venv, Fix #28: recompute off metrics.json per-row records, NOT verdict_msg):
  - WITH dep acc = 10/12 = 0.8333; WITHOUT dep acc = 0/12 = 0.000; delta = 0.8333 (reproduces exactly)
  - control 5/5 = 1.000 both arms; guardrail 1/1 abstain, wrong_rate 0.000; arm hashes differ
  - tier0_bound=12, tier1_bound=0, tier0_fastpath_rate=1.000 -> the declared role-ranked Cf resolver NEVER FIRED
  - 2 errors real + localized (both fig-garden topic-reactivation rows in the Jackal scene), not curated away

TIER: MEASURED_MECHANISM (not HARD_PASS capability). The coupling DELTA is FLOOR-DETERMINED (WITHOUT=0.000 is
DEFINITIONAL -- the no-memory abstain-everything arm; delta === WITH-accuracy, zero info beyond it), and the
sophisticated centering-Cf apparatus collapses in practice to a bare most-recent-subject recency heuristic.
This is a better-instrumented mechanism/construction proof superseding v1's rigged 1.0-vs-0.0 fixture -- NOT
capability-at-scale.

Cross-arc overlap check (USER-locked): substrate_query.sh top hit cosine=0.3555 is a spurious LEXICAL 'state'
match (WordNet 'state of being without clothing'), NOT a mechanism duplicate; grep for wsm_coupling /
discourse-state / centering-Cb in math atoms = 0. The genuinely-related prior arc is the June-28
narrative_q2_coref HF family (2x-drill capability closure) -- but that is MECHANISM-ORTHOGONAL (substrate-HRR /
Lappin-Leass at inference on synthetic-5char narratives) vs this cell's SYMBOLIC glass-box parse on real
fables, and is CONSISTENT-WITH (that closure concluded coref needs a symbolic surface-form readout -- this IS
that path), not a rediscovery. No prior CERT experiment atom at mechanism-level cosine>0.30.

A5: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta + tail-id match, both files.
LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator + needs_orchestrator_store_sync=True; NO origin push.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_discourse_state_of_mind_wsm_coupling_realcorpus_v2_MM_boundary_2026-07-17"
ATOMIZED_DATE = "2026-07-17"
ANCHOR = "read_discourse_state_of_mind_wsm_coupling_realcorpus_v2"
CELL_COMMIT = "19ba0b776"
V1_COMMIT = "b56e77203"
XARC = ("substrate_query.sh top hit cosine=0.3555 = spurious LEXICAL 'state' match (WordNet), not a mechanism "
        "dup; wsm_coupling/discourse-state/centering-Cb grep in math atoms = 0 (novel). Related prior arc = "
        "June-28 narrative_q2_coref HF family, but MECHANISM-ORTHOGONAL (substrate-HRR/Lappin-Leass on "
        "synthetic-5char vs this SYMBOLIC glass-box parse on real fables) and CONSISTENT-WITH (that closure "
        "said coref needs symbolic surface-form readout -- this IS that path), not a rediscovery. No cert "
        "experiment atom at mechanism-level cosine>0.30.")

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

ATOM_ID = ("math::MM_MEASURED_MECHANISM_discourse_state_of_mind_wsm_coupling_realcorpus_v2_recency_Cb_resolver_"
           "binds_real_pronouns_0p833_10of12_tiny_2fable_1author_sample_coupling_DELTA_FLOOR_DETERMINED_WITHOUT_"
           "0p000_DEFINITIONAL_abstain_all_no_memory_arm_delta_equals_WITH_acc_role_ranked_Cf_resolver_NEVER_"
           "FIRED_tier1_0_all_12_via_tier0_recency_measures_most_recent_subject_NOT_centering_Cf_apparatus_"
           "control_5of5_guardrail_clean_SUPERSEDES_v1_wiring_proof_b56e77203_capability_and_rungs12_codevelop_"
           "OPEN_posctrl_gold_subst_parses_selftest_2026-07-17")

CLAIM = (
    "MATH MEASURED_MECHANISM (better-instrumented boundary, SUPERSEDES the v1 wiring-proof b56e77203): a "
    "discourse 'state of mind' (WSM) recency-Cb resolver binds real pronouns at ~0.83 (10/12) on a tiny "
    "2-fable / 1-author real-prose sample (nltk gutenberg bryant-stories), with control 5/5=1.000 both arms "
    "and a clean guardrail abstain. VERBATIM BOUNDARY: recency-Cb resolver binds real pronouns at ~0.83 on a "
    "tiny 2-fable/1-author sample; coupling DELTA is FLOOR-DETERMINED (WITHOUT=0.000 is DEFINITIONAL -- "
    "abstain-everything no-memory arm; delta === WITH-accuracy, zero info beyond it); the DECLARED role-ranked "
    "Cf resolver NEVER FIRED (tier1_bound=0, all 12 resolutions via Tier-0 recency-Cb), so this measures a "
    "most-recent-subject RECENCY heuristic, NOT the centering-Cf apparatus; coupling-CAPABILITY and "
    "rungs-1+2-co-develop remain OPEN. Revival: (1) non-trivial WITHOUT baseline not abstain-all; (2) corpus "
    "where Cf-ranking fires + is load-bearing; (3) multi-author n>=dozens.")

RECOMPUTE = (
    "INDEP recompute (.venv, off metrics.json per-row records, NOT verdict_msg): WITH dependent acc = 10/12 = "
    "0.8333 (Sun/Wind 3/3 + Jackal 7/9; the 2 wrong are BOTH the fig-garden topic-reactivation rows 'He found "
    "a garden of wild figs' + 'He saw the huge pile of figs', emitted alligator vs gold jackal -- real, "
    "localized, predicted by the docstring, not curated away). WITHOUT dependent acc = 0/12 = 0.000 (every row "
    "STATE_OFF_ABSTAIN). delta = 0.8333 reproduces exactly. control 5/5 = 1.000 both arms; guardrail 1/1 "
    "abstain wrong_rate 0.000; arm_hash WITH != WITHOUT = True. MECHANISM TELEMETRY (the load-bearing finding): "
    "tier0_bound=12, tier1_bound=0, tier0_fastpath_rate=1.000 -- ALL 12 resolutions took the Tier-0 Cb-first "
    "path (bind to the single most-recent unique-subject pointer wsm.cb); the declared role-ranked Cf window "
    "resolver (subject>object, Grosz-Joshi-Weinstein) resolved NOTHING. WITHOUT=0.000 is guaranteed by the "
    "cell's own self-test (every dependent row = COREF_UNRESOLVED standalone), so delta is definitionally == "
    "WITH accuracy. construction_artifact_detected=False (WITH=0.833 not exactly 1.0), but that tripwire only "
    "catches the narrow WITH>=0.999 & WITHOUT<=0.001 case and has no teeth against the WITHOUT-is-a-strawman "
    "issue. Positive-control side: self-test verifies each gold-correct antecedent substitution parses to its "
    "declared gold via the UNMODIFIED rung-9 extractor -- the selection rule is genuinely structural.")

SCOPE = (
    "REAL prose (2 Bryant fables, 1918, public domain; ~20 rows, 12 dependent, 1 guardrail), glass-box, "
    "symbolic, NO LLM/VSA. This is a MECHANISM/construction boundary, NOT capability-at-scale. Two load-bearing "
    "limits: (a) the WITH-vs-WITHOUT coupling contrast is structurally uninformative -- WITHOUT is an "
    "abstain-everything no-memory arm pinned at 0.000 BY DEFINITION (a pronoun is unresolvable in isolation on "
    "ANY corpus), so 'delta=0.833' is a redundant restatement of WITH accuracy, NOT a fair-baseline lift; "
    "(b) the elaborate centering 'state of mind' machinery (cf_memory window, role-ranked Cf, Tier-1 fallback) "
    "is entirely DORMANT -- in practice the WSM collapses to a single wsm.cb pointer and the resolver is "
    "'bind He -> most recent grammatical subject', whose 0.833 is exactly the fraction of this corpus's "
    "pronouns pointing at the immediate prior subject. n=12 from a single author is a thin single-sample "
    "(one row flip = +/-0.083). Do NOT bank as settled capability. Supersedes v1's rigged 1.0-vs-0.0 fixture "
    "(the real-corpus move genuinely fixed the candidate-set engineering; the WITHOUT-strawman + trivial-"
    "resolver issues remain). Coupling-CAPABILITY and the rungs-1+2 (parser x discourse) co-develop claim "
    "remain OPEN.")

METRICS = {
    "with_dep_acc": 0.8333, "without_dep_acc": 0.0, "coupling_delta": 0.8333,
    "n_dependent": 12, "n_dep_correct": 10, "n_dep_wrong": 2,
    "control_acc_both": 1.0, "n_control": 5,
    "guardrail_wrong_rate": 0.0, "n_guardrail": 1,
    "tier0_bound": 12, "tier1_bound": 0, "tier0_fastpath_rate": 1.0,
    "construction_artifact_detected": False,
    "hard_case_correct": False, "n_scenes": 2, "n_authors": 1,
    "hp_gate_would_have_read": "HARD_PASS per cell prereg; MM per auditor re-VET (delta floor-determined + Cf dormant)",
}

COMPOSES = [
    "SUPERSEDES v1 wiring-proof exp_read_discourse_state_of_mind_wsm_coupling_v1 (b56e77203) -- the "
    "hand-authored 1.0-vs-0.0 fixture VET-flagged construction-determined; this real-corpus v2 replaces it as "
    "the current, better-instrumented boundary.",
    "rung-9 ie_extract_downstream_all_fixed (the UNMODIFIED real-prose OPEN extractor reused as base parser + "
    "post-substitution reparser)",
    "coref cell _find_subject_pronoun (v1 ANCHOR 3, UNMODIFIED mechanical pronoun detector)",
    "CONSISTENT-WITH (not superseding) the June-28 narrative_q2_coref 2x-drill capability closure: that closure "
    "concluded substrate-internal coref is not implementable and coref needs a symbolic surface-form readout -- "
    "this symbolic glass-box parse IS that readout path, on real prose, at 0.83 via recency-Cb.",
    "roadmap rungs 1 (broad-parser) x 2 (discourse state-of-mind) co-develop -- this cell is the discourse-state "
    "coupling probe; the co-develop capability claim remains OPEN pending revival.",
]

atom = {
    "id": ATOM_ID,
    "name": CLAIM,
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": ("confirmed_measured_mechanism_discourse_wsm_recency_Cb_binds_real_pronouns_0p833_coupling_"
                    "delta_floor_determined_cf_resolver_dormant_supersedes_v1_wiring_proof_capability_open"),
    "cert_class": ("discourse_state_of_mind_wsm_coupling_realcorpus_recency_Cb_resolver_binds_real_pronouns_"
                   "coupling_delta_floor_determined_without_definitional_zero_role_ranked_Cf_never_fired_"
                   "measures_recency_not_centering_apparatus_measured_mechanism_boundary_capability_open"),
    "description": (CLAIM + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + RECOMPUTE
                    + "\n\nHONEST SCOPE: " + SCOPE),
    "aliases": [],
    "ts_iso": _iso,
    "ts": _ts,
    "metadata": {
        "provenance_quality": "recompute_off_disk_per_row_records_and_tier_telemetry_not_verdict_msg",
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "supersedes": "exp_read_discourse_state_of_mind_wsm_coupling_v1 (b56e77203) -- v1 wiring-proof",
        "supersedes_commit": V1_COMMIT,
        "store_head_at_write": "unsynced_needs_orchestrator",
        "metrics_path": "data/exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2/metrics.json",
        "verified_off_data": RECOMPUTE,
        "honest_scope": SCOPE,
        "metrics": METRICS,
        "over_reads_corrected": [
            "exp_dev framed HARD_PASS as 'promotes the coupling BEYOND wiring-proof toward capability'. "
            "OVER-READ, DEMOTED to MEASURED_MECHANISM: (1) the coupling DELTA is FLOOR-DETERMINED -- WITHOUT="
            "0.000 is DEFINITIONAL (the self-test asserts every dependent row = COREF_UNRESOLVED standalone; a "
            "no-memory arm can only abstain on ANY corpus), so delta === WITH accuracy and carries zero info "
            "beyond it; the WITH-vs-WITHOUT contrast is a strawman baseline, the SAME core defect as v1 just "
            "with WITH no longer perfect.",
            "(2) tier1_bound=0 / tier0_fastpath_rate=1.000: the declared, cited role-ranked Cf resolver (the "
            "headline mechanism extension) NEVER FIRED -- all 12 resolutions were Tier-0 Cb-first (bind to the "
            "single most-recent unique subject). The WSM 'state of mind' collapses in practice to one wsm.cb "
            "pointer; this measures a most-recent-subject RECENCY heuristic, NOT the centering-Cf apparatus it "
            "is framed as exercising. WITH=0.833 = exactly the corpus's fraction of pronouns pointing at the "
            "immediate prior subject; the 2 errors are precisely where recency fails.",
            "(3) construction_artifact tripwire has weak teeth: fires only on WITH>=0.999 & WITHOUT<=0.001 "
            "exactly; passes any non-perfect WITH; does not address the WITHOUT-is-definitionally-0 issue.",
            "(4) n=12 dependent from 2 fables / 1 author is a thin single-sample -- not capability-at-scale.",
        ],
        "genuine_positives_symmetric_anti_negativity": (
            "This IS a real, honest improvement over v1: the sentence-selection rule is genuinely STRUCTURAL "
            "(parseability of the gold antecedent substitution, verified live in self-test via the unmodified "
            "rung-9 extractor, decided BEFORE WITH numbers computed); the 2 errors are honest, localized, "
            "predicted, not curated away; control 5/5 + guardrail clean abstain; real uncurated prose. A "
            "legitimate better-instrumented supersession of v1's rigged fixture -- just not capability."),
        "revival_criteria": [
            "non-trivial WITHOUT baseline (e.g. most-frequent-entity or random-recent-noun), NOT the "
            "abstain-everything no-memory arm, so the coupling delta measures something informative",
            "a corpus varied enough that the Tier-1 role-ranked Cf resolver actually FIRES and is LOAD-BEARING "
            "(the fig-garden topic-reactivation class must be RESOLVABLE, not just measured-wrong)",
            "multi-source / multi-author corpus, n>=several dozen dependent rows (current n=12, 1 author)",
        ],
        "cross_arc_overlap_check": XARC,
        "cites": [
            "Fix_28_verify_off_data_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "verify_the_referent_atom_ids_mechanism_metric_regime",
            "cited_number_must_reproduce_from_cell",
            "feedback_construction_proof_is_not_a_capability_win",
            "feedback_synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
            "auditor_positive_control_must_clear_its_own_floor_before_trusting_result_2026-07-01",
        ],
        "composes_with": COMPOSES,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
    },
}

ledger = {
    "op": "cert_ruling",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom["cert_status"],
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "supersedes_commit": V1_COMMIT,
    "store_head_at_write": "unsynced_needs_orchestrator",
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("MEASURED_MECHANISM_recency_Cb_binds_real_pronouns_0p8333_10of12_coupling_delta_floor_determined_"
                "WITHOUT_0p000_definitional_role_ranked_Cf_resolver_never_fired_tier1_0_tier0_fastpath_1p000_"
                "measures_recency_not_centering_apparatus_control_1p000_5of5_guardrail_clean_supersedes_v1_"
                "b56e77203"),
    "cert_increment_delta": 1,
    "decision": (
        "MM (proven-bound / better-instrumented mechanism boundary, SUPERSEDES v1 wiring-proof). Numbers "
        "reproduce EXACTLY off-disk (WITH 10/12=0.8333, WITHOUT 0/12=0.000, delta 0.8333, control 5/5, "
        "guardrail clean). But this is NOT capability-at-scale: (1) coupling delta is FLOOR-DETERMINED -- "
        "WITHOUT=0.000 is DEFINITIONAL (no-memory abstain-all arm; delta === WITH accuracy, zero info beyond "
        "it); (2) the declared role-ranked Cf resolver NEVER FIRED (tier1_bound=0, all 12 via Tier-0 "
        "recency-Cb) -- measures a most-recent-subject RECENCY heuristic, not the centering-Cf apparatus; "
        "(3) n=12 / 1 author is a thin single-sample. Real improvement over v1's rigged 1.0-vs-0.0 fixture "
        "(structural selection rule, honest localized errors), but capability + rungs-1+2-co-develop OPEN."),
    "framing_correction_vs_director": (
        "Director relayed the exp_dev HARD_PASS as promoting the coupling 'beyond wiring-proof toward "
        "capability'. I DEMOTE to MEASURED_MECHANISM (symmetric anti-negativity: honest downward). The delta "
        "framing overstates -- WITHOUT is definitionally 0 (strawman baseline), so delta carries no info "
        "beyond WITH accuracy; and the headline mechanism (role-ranked Cf resolver) is entirely dormant "
        "(tier1_bound=0), so the result measures recency, not centering. Do NOT bank as capability; the "
        "revival is a NEW cell (non-trivial baseline + Cf-firing corpus + multi-author n). Genuine positives "
        "banked symmetrically: structural selection rule + honest localized errors are a real supersession of "
        "v1."),
    "cross_arc_overlap_check": XARC,
    "net_cert_delta": ("+1 MM (measured-mechanism boundary: WSM recency-Cb binds real pronouns ~0.83 on a tiny "
                       "real sample; coupling delta floor-determined, Cf resolver dormant; SUPERSEDES v1 "
                       "wiring-proof; capability OPEN)."),
    "supersedes": "exp_read_discourse_state_of_mind_wsm_coupling_v1 (b56e77203, wiring-proof)",
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
    "ts_iso": _iso,
    "ts": _ts,
    "atom_id": ATOM_ID,
}


def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: discourse state-of-mind WSM-coupling realcorpus v2 -> MM boundary (2026-07-17) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id / id mismatch"

    # id-uniqueness against existing store
    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store"); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing)")

    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    # integrity: reload full math atoms, assert all parse and the new id present
    n_ok = 0
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True) ===")
    print("ATOM_ID:", atom["id"])


if __name__ == "__main__":
    main()
