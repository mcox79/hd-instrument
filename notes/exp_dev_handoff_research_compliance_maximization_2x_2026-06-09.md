# exp_dev hand-off -- research: compliance maximization 2x

**Filed-by:** research sub-agent, 2026-06-09
**Trigger:** research_drill_compliance_maximization_2x_2026-06-09.md
**Research note path:** d:/AI/hd-instrument/notes/research_drill_compliance_maximization_2x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and ranks
them; exp_dev designs the actual experiment cells, preregs, and dispatch independently.

---

## Pause state block

Pause flag: check data/orchestrator_paused.flag before dispatch.
If paused: hold all anchors until resume. Do not dispatch cloud experiments while paused.
Local CPU anchors (GDPR-PATTERN-DELETE, GDPR-RIGHT-TO-PORTABILITY, PER-TOKEN-AUDIT) may
proceed on the local runner while paused IF the user explicitly authorizes local-only work.

---

## Anchor candidates (rank-ordered)

### Rank 1: GDPR-PATTERN-DELETE
Anchor pointer: engineering anchor GDPR-PATTERN-DELETE (Section 1.2 of research note)
Substrate-product reading: validates "delete all facts about person X" as the primary
GDPR Art.17 workflow; proves keystore-partition mechanism at the mechanism level.
Tier hint: local CPU; < 2 hours wall time; no cloud needed.
Why now: this is the cheap decisive test (Section 8 of research note). If this fails,
the broader compliance story needs redesign before any enterprise pitch. Cheapest
possible risk gate for the entire compliance moat.
Pre-reg bands (exp_dev to refine per envelope-fail-bands):
  HARD-PASS: false_retention_rate = 0.0, false_deletion_rate = 0.0, merkle_root_valid = True
  MID-BAND: false_retention_rate <= 0.001 (operational bug, fixable)
  HARD-FAIL: false_retention_rate > 0.001 OR false_deletion_rate > 0

### Rank 2: PER-TOKEN-AUDIT
Anchor pointer: engineering anchor PER-TOKEN-AUDIT (Section 3.1 and 7, Rank 3 of research note)
Substrate-product reading: per-token grounding audit during LLM generation; EU AI Act
Art.12 compliance claim; deadline August 2, 2026 (54 days from today).
Tier hint: local CPU + local LLM inference (Pythia-160M or Llama-1B); 2-4 hours.
Why now: highest regulatory urgency. Art.12 deadline is fixed. First compliant AI
retrieval system claim is available if shipped before August 2.
Pre-reg bands:
  HARD-PASS: audit_overhead_per_token < 5ms, audit_records_match_retrieved_facts = True
  MID-BAND: 5ms < overhead < 50ms (usable for batch, not interactive)
  HARD-FAIL: overhead > 50ms/token OR audit_records_inconsistent

### Rank 3: GDPR-AT-50M
Anchor pointer: engineering anchor GDPR-AT-50M (Section 1.1 and 7, Rank 1 of research note)
Substrate-product reading: Wikidata-scale deletion validation; proves the 50M-fact GDPR
erasure claim for enterprise customers with large fact bases.
Tier hint: local CPU; block downdate is CPU-bound; may need remote CPU queue for full
50M test (check feedback_route_gpu_vs_cpu_by_torch_not_N.md).
Why now: enterprise pitch anchor; needed for healthcare/financial customers with large
fact inventories.
Pre-reg bands:
  HARD-PASS: total_deletion_plus_audit_time < 60s for 50M facts
  MID-BAND: 60s < time < 300s (acceptable for batch compliance job, not real-time)
  HARD-FAIL: time > 300s (block downdate architecture not viable at Wikidata scale)

### Rank 4: MT-AT-1000-TENANTS
Anchor pointer: engineering anchor MT-AT-1000-TENANTS (Section 2.1 and 7, Rank 4 of research note)
Substrate-product reading: proves DBaaS architecture at thousand-tenant scale;
validates structural isolation claim under load.
Tier hint: local CPU or remote CPU; memory-mapped W_t across 1000 tenants; 4-8 hours.
Why now: DBaaS pitch requires this proof point; PP-101 algebra predicts it works but
no empirical confirmation at 1000-tenant scale exists.
Pre-reg bands:
  HARD-PASS: cross_tenant_leakage_rate = 0.00 across 1000 adversarial queries
  MID-BAND: N/A (any leakage is HARD-FAIL by structural claim)
  HARD-FAIL: any cross-tenant leakage detected

### Rank 5: GDPR-RIGHT-TO-PORTABILITY
Anchor pointer: engineering anchor GDPR-RIGHT-TO-PORTABILITY (Section 1.7 and 7, Rank 5 of research note)
Substrate-product reading: validates GDPR Art.20 export-then-erase workflow end-to-end
with Merkle audit record of export hash.
Tier hint: local CPU; < 2 hours.
Why now: CNIL enforcement priorities include portability (2024-2026 programme); needed
for European enterprise customers.
Pre-reg bands:
  HARD-PASS: export_completeness = 1.0, post_erase_retention = 0, merkle_export_hash_valid = True
  HARD-FAIL: any missing fact in export OR any fact surviving erase

### Rank 6: MT-ADVERSARIAL
Anchor pointer: engineering anchor MT-ADVERSARIAL (Section 2.5 and 7, Rank 6 of research note)
Substrate-product reading: adversarial stress test of structural isolation; proves the
categorical isolation claim under active attack.
Tier hint: local CPU + adversarial query generator; < 4 hours.
Why now: enterprise security audits require adversarial proof, not nominal proof.
Pre-reg bands:
  HARD-PASS: adversarial_success_rate = 0.00 across 1000 crafted queries
  HARD-FAIL: any non-zero leakage

### Rank 7: PER-HOP-AUDIT
Anchor pointer: engineering anchor PER-HOP-AUDIT (Section 3.2 and 7, Rank 7 of research note)
Substrate-product reading: per-hop reasoning chain audit for multi-hop retrieval;
EU AI Act Art.12(2); also enables multi-hop revival debugging (project_multihop_revive_priority).
Tier hint: local CPU + multi-hop chain; 2-4 hours.
Why now: dual value -- compliance + multi-hop debugging ground truth.
Pre-reg bands:
  HARD-PASS: hop_records_complete = True for all hops, merkle_root_covers_full_chain = True
  HARD-FAIL: any hop missing from audit OR root inconsistent

### Rank 8: ZKP-PROOF
Anchor pointer: engineering anchor ZKP-PROOF (Section 5.3 and 7, Rank 8 of research note)
Substrate-product reading: ZK-SNARK circuit for Merkle inclusion proof; proves fact
possession without revealing fact; financial compliance deployment pattern (2025-2026).
Tier hint: local CPU; requires snarkjs/circom or arkworks Rust toolchain; 1-2 days
theory + circuit compilation.
Why now: 2-year moat vs neural competitors (who cannot practically build this circuit).
Lower urgency than Art.12 deadline anchors.
Pre-reg bands:
  HARD-PASS: proof_size < 500 bytes, verification_time < 5ms, proof_generation < 5 minutes
  MID-BAND: proof_size < 10MB, generation < 30 minutes (usable but not ideal)
  HARD-FAIL: proof_size > 10MB OR generation > 30 minutes

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_compliance_maximization_2x_2026-06-09.md
- Prior compliance drill: d:/AI/hd-instrument/notes/research_drill_pattern_b_compliance_distributed_3x_2026-06-07.md
- exp_dev brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Orchestrator brief: d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md
- Multi-hop priority: memory/project_multihop_revive_priority.md
- Production arch: memory/production_architecture_locked_2026-06-07.md
- Feedback relevant: memory/feedback_pre_dispatch_speed_harden_progress_discipline.md
- Feedback relevant: memory/feedback_causal_lm_last_token_pool.md (for PER-TOKEN-AUDIT)
- Feedback relevant: memory/feedback_laptop_run_no_nohup_use_timeout.md (local runs)

---

## Contract section

exp_dev owns: anchor cell design, preregistration per envelope-fail-bands, smoke gate,
dispatch via queue_add.sh, post-ship REMOTE VERIFY, self-test per formula-selftests.

research owns: providing this handoff file and the research note. Research does NOT
design experiment cells, does NOT set exact hyperparameters, does NOT dispatch anchors.

Pause gate: check data/orchestrator_paused.flag. If set, hold queue-triggering commits.

---

## Autonomy declaration

exp_dev decides: cell ordering, batching strategy, which anchors to combine on one
instance, exact implementation of keystore partition and block downdate, exact ZKP
toolchain choice, and whether to run MT-ADVERSARIAL before or after MT-AT-1000-TENANTS.

No inline experiment design is provided here per [[feedback-no-experiment-design-in-prompts]].
