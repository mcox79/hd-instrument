# exp_dev hand-off -- research: substrate 3-op compositional extension

Filed-by: research (opus synthesis), 2026-06-11

Trigger: 2x DEEP drill on substrate compositional generation engine 3-op extension.
Research note: d:/AI/hd-instrument/notes/research_drill_substrate_3op_compositional_extension_2x_2026-06-11.md

Pause state: respect data/orchestrator_paused.flag before queuing. Anchor candidates
are READ-ONLY until orchestrator-resume-experiments. Annotation-only filings allowed
under pause; queue-additions are pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchor candidates
with substrate-product reading + cheap-CPU pilot pointer + tier hint + why-now. The
exp_dev role chooses the cell implementation; research does not pre-decide.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- R3OP-PILOT-1 -- 3-op cheap decisive triple-smoke (Tier B target)

Pointer: research note section (b) + Appendix A.

Substrate-product reading: validates substrate-intrinsic 3-op chain reach.
If T-3OP-CEILING PASS + T-3OP-RECURSE >= MIDDLE + T-3OP-VERIFIED HARD-PASS,
the substrate compositional generation engine has structural reach to depth-3
multistep composition without LLM in the inference path. Direct precondition
for the multi-step audit wedge.

Tier hint: B (single-seed CPU smoke at <= 90 min; multi-seed escalation to Tier A
only if HARD-PASS triggers cross-domain transfer pilot).

Why-now: PP-375 2-op composition validated at 0.753 on MultiArith within
LLM-CoT range; ASDiv 0.30 plateau drill (2026-06-11) identified 2-op-and-3-op
composition as the path to 0.55-0.60; the 3-op extension is the next
structural piece. No new substrate-physics required; only the recursion
harness and typed scratchpad.

Pre-reg bands (verbatim from research note section c):
- P1 oracle ceiling >= 0.85 PASS / < 0.65 HARD-FAIL
- P2 recurse end-to-end >= 0.30 HARD-PASS / [0.15, 0.30) MIDDLE / < 0.10 HARD-FAIL
- P3 verifier-lift >= 0.10 abs AND >= 2*SE HARD-PASS / < 0.03 HARD-FAIL
- P5 scratchpad-recall >= 0.85 at <= 5 atoms PASS / < 0.60 HARD-FAIL

### Anchor 2 -- R3OP-PILOT-2 -- code-step composition transfer (Tier C exploratory)

Pointer: research note section (c) P6 + section (e) cross-domain transfer.

Substrate-product reading: same recursive-2op-with-verifier on a small code-step
benchmark (e.g. function-compose at depth 3). Tests unified compositional engine
hypothesis on a second domain.

Tier hint: C (exploratory; only ships if Anchor 1 HARD-PASS T-3OP-VERIFIED).

Why-now: cross-domain transfer is the load-bearing claim for the unified
compositional generation engine. Without P6 evidence the substrate value
proposition is math-MWP-specific, not unified.

Pre-reg: end-to-end accuracy >= 0.20 on at least 2 of 3 transfer domains
(code, sentence-pair entailment, story-event) per P6 HARD-FAIL band.

### Anchor 3 -- R3OP-PILOT-3 -- sentence-pair entailment 3-step chain (Tier C exploratory)

Pointer: same as Anchor 2 but on a small entailment-chain subset.

Substrate-product reading: validates the substrate compositional engine handles
NL-bridge composition, not just numeric. Cross-thread with substrate-classical
NLP methods (memory entry 2026-06-11).

Tier hint: C (exploratory; same gate as Anchor 2).

Why-now: complements Anchor 2 on the NL side; user strategic insight names
sentence-pair as one of the four engine domains.

### Anchor 4 -- R3OP-PILOT-4 -- story-event sequence 3-step chain (Tier C exploratory)

Pointer: same as Anchor 2 but on a small story-event-prediction subset.

Substrate-product reading: validates the substrate compositional engine handles
narrative composition. Cross-thread with substrate static-robust dynamic-fragile
finding (2026-06-10) -- story-event composition is structurally similar to
event-sequence-prediction in the static-robust regime.

Tier hint: C (exploratory; same gate as Anchor 2).

Why-now: completes the four-domain unified compositional engine evidence
required by user strategic insight.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_substrate_3op_compositional_extension_2x_2026-06-11.md
- d:/AI/hd-instrument/notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md
- d:/AI/hd-instrument/notes/research_drill_asdiv_mixed_adversarial_2x_2026-06-11.md
- d:/AI/hd-instrument/notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md
- d:/AI/hd-instrument/notes/research_drill_substrate_llm_interface_compositional_structure_preservation_2x_2026-06-04.md
- d:/AI/hd-instrument/experiments/data/asdiv_validation.json (in-repo, no fetch)
- memory: substrate_v32_engineered_wrapper_2026-06-11
- memory: substrate_classical_NLP_methods_outperform_phasor_2026-06-11

---

## Contract

- exp_dev chooses cell implementation; research does not pre-decide.
- envelope-fail-bands per research note section (c): pre-reg P1, P2, P3, P5 in
  cell prologue.
- formula-selftests per substrate verification discipline.
- smoke gate: 50-item subset T-3OP-CEILING dryrun within 15 min before full pilot.
- ship via queue_add.sh on the local CPU runner queue (data/local_cpu_queue or
  data/cpu_queue per orchestrator routing).
- post-ship REMOTE VERIFY: confirm verdict landed in dashboard recent_verdicts.

## Autonomy declaration

exp_dev is autonomous on:
- exact cell file paths and naming
- substrate 2-op selector primitive call signatures
- scratchpad atom-pool dimensionality and type-tag schema
- per-step verifier feature engineering (within the constraints in note Appendix A)
- top-K beam width (research suggests K=3; exp_dev may sweep K in {1,3,5}
  within the 90 min budget)

exp_dev defers to research on:
- pre-registration band changes (must re-route to research if proposed)
- adding/removing predictions P1-P6 (must re-route to research)
- cross-domain transfer ordering (Anchors 2-4 gating)

---

end of hand-off
