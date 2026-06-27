"""Build substrate-vs-MD v1 ground-truth jsonl.

ASCII-only. No emojis. No em-dashes.

20 queries x 4 buckets per drill design 2026-06-27. Ground-truth text
extracted by exp_dev (cell-author time) from frozen 2026-06-26 BACKUP file
and memory directives. Hashes frozen here; cell re-verifies at run-time
to defeat post-hoc rigging (BIAS-13 contamination defense).

Run once to (re)build ground_truth.jsonl alongside this script.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "substrate_vs_md_v1.jsonl"

# Each entry: id, bucket (A/B/C/D), q, expected_files (list of relative paths),
# ground_truth_text (extracted paragraph(s) or phrase set with key tokens),
# gt_hash (computed below).
ENTRIES = [
    # ---------------- BUCKET A: directive lookup (5) ----------------
    {
        "id": 1,
        "bucket": "A",
        "q": "what did USER directive D6 say about substrate as definitive source",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Directive 6 Substrate is the definitive source for post-compaction. "
            "I want you to focus, btw, on making substrate the definitive source for info "
            "and context, before the next compaction. Substrate-KB ingest and query landed today. "
            "Scheduled task running every 5 min windowless pythonw. Source-class filter shipped "
            "Option A to work around language-ingest swamping Director queries."
        ),
    },
    {
        "id": 2,
        "bucket": "A",
        "q": "what is the no-local experiment directive",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md",
        ],
        "ground_truth_text": (
            "USER NO LOCAL directive 2026-06-27 do not route experiments to local cpu queue "
            "all cell-author smoke and full dispatch must go through remote_cpu_queue or "
            "overnight_queue. Reason laptop matmul opportunity cost and thermal."
        ),
    },
    {
        "id": 3,
        "bucket": "A",
        "q": "what is the stage progression rule 1 2 3 4 dont skip",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md",
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Substrate is MEMORY plus COMPOSITION plus RETRIEVAL plus AUDIT device. "
            "NOT a statistical LM competitor. Brain is the existence proof. "
            "Stages 1 base 2 optimize 3 higher functions 4 LM equivalence. Dont skip. "
            "Stage 4 LM equivalence text8 is deferred until 1-3 mature."
        ),
    },
    {
        "id": 4,
        "bucket": "A",
        "q": "what did USER say about discriminator must survive scale before full dispatch",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Smoke proves cell RUNS smoke-N discriminator may not survive full-N because substrate "
            "tolerance scales with N cell-author must use check A smoke at full-N or check B "
            "analytical scale justification or check C full-N preview arm in smoke reject full "
            "dispatch if baseline >= 0.95 of mechanism at full-N preview."
        ),
    },
    {
        "id": 5,
        "bucket": "A",
        "q": "what is the agent-spawn-only architecture per 2026-06-26",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_agent_spawn_model_only_4session_dead_USER_2026-06-26.md",
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "there is no fucking orchestrator it is all you you call the orchestrator agent when "
            "you need it. The 4-session model separate Claude Code tabs for Skunkworks Exp-Dev "
            "Orchestrator Testbed is DEAD. Heartbeats confirm only research is live. "
            "Spawn hdi_role sub-agents per task. Do NOT file routing notes they go nowhere."
        ),
    },
    # ---------------- BUCKET B: state queries (5) ----------------
    {
        "id": 6,
        "bucket": "B",
        "q": "what cells are in flight right now",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Wave 4 substrate-KB content-chunk rebuild IN FLIGHT agent a38d457eada23b1ae "
            "Skunkworks batch 4 A5-gated atom commit IN FLIGHT agent a2c412ecd864be3ca "
            "ANCHOR 3 coarse-grain FULL pending queued smoke HARD_PASS with adaptive "
            "p5-percentile threshold."
        ),
    },
    {
        "id": 7,
        "bucket": "B",
        "q": "what is the current substrate CERT count",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "CERT 614 as of Skunkworks landed-VET this session plus 2 from 612 cortex E-tensor "
            "v1 honest_negative and Fix B refutation honest_negative. Honest CERT count Skunkworks "
            "batches 3 plus 4 collectively net plus 1 588 to 589 via ultrametric clustering "
            "chain-grade."
        ),
    },
    {
        "id": 8,
        "bucket": "B",
        "q": "what is the cortex E-tensor importance state",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Cortex E-tensor v1 saturation HARD_FAIL regime too easy recall 1.0 on all arms. "
            "Cortex E-tensor harder regime HARD_FAIL wrong-direction E_GATED HURTS rec_old by "
            "21.7pp vs random. Cortex E-tensor RETEST Fix B HARD_FAIL structural cor E "
            "absW 0.984 vs USER 0.30 required META_RULE_F atomized from this."
        ),
    },
    {
        "id": 9,
        "bucket": "B",
        "q": "what HARD_PASS landings happened in last 6 hours",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "ANCHOR 4 time-decay eviction FULL HARD_PASS eviction_frac 0.515 reingest 30 of 30 "
            "USER_DIRECTIVE retention 1.0 AUDIT_ONLY mode chain-grade-eligible. "
            "exp_cortex_ultrametric_clustering_coarse_grain_v1 FULL HARD_PASS cap_drop 0.212 "
            "rec_clustered 1.000 d_ULTRA_vs_RND plus 0.104 cv 0.000."
        ),
    },
    {
        "id": 10,
        "bucket": "B",
        "q": "what is the active program for compositional understanding stage 3",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "USER pivot language-prediction track CLOSED compositional-understanding Stage 3 track "
            "OPENED. 7 first-wave cells filed 3 ran smoke HARD_PASS today cortex E-tensor top-K "
            "composition refuse-gate PC cleanup. Substrate-as-Director-KB dogfood build "
            "ingest plus query both smoke HARD_PASS today."
        ),
    },
    # ---------------- BUCKET C: mechanism / cell history (5) ----------------
    {
        "id": 11,
        "bucket": "C",
        "q": "what is TWO_TIER generational",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "TWO_TIER generational W fast tier plus slow tier brain analog hippocampus plus "
            "cortex NREM replay consolidation during downtime Partition routing M 10M. "
            "Scaffolding WORKS chain-grade."
        ),
    },
    {
        "id": 12,
        "bucket": "C",
        "q": "what was the top-K composition refuse-gate result",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Refuse-gate V_REL 256 chain-grade. Wave 1.5 fulls cortex E-tensor HARDER plus "
            "top-K engineered plus PC cleanup deeper all MEASURED_MECHANISM by-construction-"
            "saturation mechanisms not exercised at full-N validates new "
            "discriminator-must-survive-scale discipline."
        ),
    },
    {
        "id": 13,
        "bucket": "C",
        "q": "what is the lock-in amplifier chain-grade evidence",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/project_session_2026-06-23_strategic_decisions_full_arc.md",
        ],
        "ground_truth_text": (
            "lock-in amp chain-grade-eligible USER intuition validated. Sparse-bipolar 20-300x "
            "bundle lift. HRR involutive. 5-primitive predicate set. Excitability-trace forward-"
            "only. encoder IS load-bearing bottleneck across V1 V2 V3."
        ),
    },
    {
        "id": 14,
        "bucket": "C",
        "q": "what is the multi-hop depth-15 evidence",
        "expected_files": [
            "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
        ],
        "ground_truth_text": (
            "Multi-hop depth-15 chain-grade 0.808 at depth 15 extended to depth-30 today. "
            "multi-hop depth-extension v1 CHAIN_GRADE_DEPTH_CEILING_30 15 0.81 20 0.71 "
            "25 0.67 30 0.64 CERT plus 1."
        ),
    },
    {
        "id": 15,
        "bucket": "C",
        "q": "what is the n1_v3 substrate-vs-unigram result",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/project_session_2026-06-23_FINAL_pickup_state.md",
        ],
        "ground_truth_text": (
            "n1_v3 PROVES substrate top-1 0.445 vs unigram 0.276 60 percent lift near bigram. "
            "fair_harness on GPU Skunkworks cert routing in flight."
        ),
    },
    # ---------------- BUCKET D: gotcha / known-pitfall (5) ----------------
    {
        "id": 16,
        "bucket": "D",
        "q": "what is the bigram-gap test problem",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md",
        ],
        "ground_truth_text": (
            "the substrate doesnt KNOW anything we havent given it any understanding of language "
            "yet why are we testing it against language when it doesnt know shit. "
            "text8 BPC bigram-gap V_C-sweep trigram-context are MEANINGLESS on a substrate "
            "without semantics. Build understanding first language is downstream."
        ),
    },
    {
        "id": 17,
        "bucket": "D",
        "q": "what is the band-floor results are MIDDLE_BAND rule",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_three_smoke_disciplines_no_silent_except_smoke_fires_discriminator_band_floor_inconclusive_2026-06-26.md",
        ],
        "ground_truth_text": (
            "META_RULE_L band-floor results are MIDDLE_BAND not HARD_PASS caught Wave 3 ANCHOR 5. "
            "Three smoke disciplines no silent except blocks smoke must FIRE discriminator not "
            "just verify cell runs band-floor results are MIDDLE_BAND not HARD_PASS."
        ),
    },
    {
        "id": 18,
        "bucket": "D",
        "q": "why is substrate-vs-MD a head-to-head test now",
        "expected_files": [
            "notes/research_drill_substrate_vs_md_head_to_head_proof_gate_design_2026-06-27.md",
        ],
        "ground_truth_text": (
            "we need to first prove that it substrate will do better than a stale md and that "
            "it is updated regularly before we switch. Gates the MEMORY ritual flip from "
            "Read BACKUP file directly to Query substrate-KB FIRST. ALL FOUR axes latency "
            "completeness freshness robustness must pass for ritual flip."
        ),
    },
    {
        "id": 19,
        "bucket": "D",
        "q": "what is the Fix #28 violation pattern",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22.md",
        ],
        "ground_truth_text": (
            "Fix 28 Verify per-arm metrics before cross-cell convergence claims. Read "
            "metrics.json per-arm not verdict_msg. Pattern is over-claiming from verdict_msg "
            "framings concrete remediation read metrics.json BEFORE propagating cross-arm "
            "narratives default to under-claiming let cert-classification come from Skunkworks "
            "not from my framing."
        ),
    },
    {
        "id": 20,
        "bucket": "D",
        "q": "what is the by-construction-saturation discipline",
        "expected_files": [
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_cert_owner_overrides_director_via_by_construction_saturation_2026-06-22.md",
            "C:/Users/marsh/.claude/projects/d--AI/memory/feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23.md",
        ],
        "ground_truth_text": (
            "Skunkworks correctly overrides Director via by-construction-saturation tiering. "
            "novelty_ratio at metric-cap and density below substrate capacity. Default "
            "classification MM not chain-grade let cert-owner tier UP. Cert-owner role-"
            "separation working as designed queue capacity-sweep for chain-grade evidence."
        ),
    },
]


def _compute_hashes(entries: list[dict]) -> list[dict]:
    for e in entries:
        h = hashlib.sha256(e["ground_truth_text"].encode("utf-8")).hexdigest()
        e["gt_hash"] = f"sha256:{h}"
    return entries


def main() -> None:
    entries = _compute_hashes(ENTRIES)
    with OUT.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=True) + "\n")
    print(f"[build] wrote {len(entries)} entries to {OUT}")
    print(f"[build] first hash sample: id=1 hash={entries[0]['gt_hash']}")
    assert len(entries) == 20
    buckets = {b: sum(1 for e in entries if e["bucket"] == b) for b in "ABCD"}
    assert buckets == {"A": 5, "B": 5, "C": 5, "D": 5}, f"bucket count mismatch: {buckets}"
    print(f"[build] bucket counts {buckets} OK")


if __name__ == "__main__":
    main()
