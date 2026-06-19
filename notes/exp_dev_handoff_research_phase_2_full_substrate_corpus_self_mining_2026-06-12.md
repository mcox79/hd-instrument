# exp_dev hand-off -- research: Phase-2-full substrate corpus self-mining + active learning methodology

Filed by: research sub-agent (Opus) 2026-06-12
Trigger: 2x DEEP drill delivered notes/research_drill_phase_2_full_substrate_corpus_self_mining_active_learning_methodology_2x_2026-06-12.md with HARD-PASS / HARD-FAIL pre-registration on a cheap decisive smoke test.

Pause state: this hand-off is INFORMATIONAL pickup material; pause flag controls whether exp_dev acts. Smoke cell is small-cost (~1 day impl + 1-2 hr CPU) and can be queued when refill demand surfaces.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides anchor candidates as pointers; experiment design happens in exp_dev's autonomous design step.

## Anchor candidates (rank-ordered)

Rank 1: Snowball-style bootstrapping smoke on 50-file research_history subset.
- Anchor pointer: notes/research_drill_phase_2_full_substrate_corpus_self_mining_active_learning_methodology_2x_2026-06-12.md section "Cheap decisive test"
- Substrate-product reading: validates the EXTRACTION-FRONTEND + DISTANT-SUPERVISION-FILTER halves of Phase-2-full architecture; gates the larger pipeline.
- Tier hint: Tier-4 PIPELINE (substrate-self-improvement at content level; per substrate-tier-3-atoms-insufficient-need-pipeline rule, Phase-2-full is end-to-end pipeline assembly not atom drop-in).
- Why now: prior corpus-deficiency triangulation (5 mechanisms plateau at 0.34-0.39) named corpus ingestion as the empirically-vindicated lever; Phase-2-full IS that lever in its self-mined form before Phase 3 external-ingest.

Rank 2: Cluster-novelty redundancy filter validation.
- Anchor pointer: same drill note, component C3.
- Substrate-product reading: validates substrate hybrid encoder (algebra-primary + BGE OOV fallback) as a DEDUPE primitive, not just a retrieval primitive.
- Tier hint: Tier-3 atom enhancement (hybrid encoder gets a second validated use case).
- Why now: Cell 1 atom-to-atom hybrid clustering already validated PERFECT (within-vs-between 22x-500M+); reusing the same primitive for dedupe is the highest-confidence half of the pipeline.

Rank 3: Curriculum-difficulty ranker on a held-out triplet subset.
- Anchor pointer: same drill note, component C4.
- Substrate-product reading: validates Z-counts + structural-cognition features as a PRIORITY-QUEUE primitive over candidate atoms.
- Tier hint: Tier-3 atom (new primitive: ranker for proposed atoms).
- Why now: discriminative_perceptron is current-best universal lever 11/12 capabilities; curriculum ranker is in the same mechanism class.

## Context pointers

- d:/AI/hd-instrument/notes/research_drill_phase_2_full_substrate_corpus_self_mining_active_learning_methodology_2x_2026-06-12.md (this drill)
- d:/AI/hd-instrument/notes/substrate_capability_map.md (cap_map for under-covered slots feeding C5)
- d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (most recent research_delivery + verdict entries)
- d:/AI/hd-instrument/PROGRESS.md (Phase 1 evolve.py status; Phase 2 LIGHT current state)

## Contract

- LLM-free path is mandatory per [[substrate-content-sources-us-or-substrate]] -- no LLM-as-judge in any component.
- Honesty axis is hard requirement -- zero hallucinated candidates is non-negotiable; substrate-quality-first.
- Pre-registered HARD-PASS / HARD-FAIL thresholds in the drill note are binding; do not move goalposts.
- Substrate primitives (NER + chunking + dep-parse + hybrid encoder + discriminative_perceptron) are the toolkit; do not introduce new dependencies for smoke cell.

## Autonomy declaration

exp_dev autonomously decides:
- Which 50 files to seed the smoke from (recommend: diverse across 6 history partitions, biased toward under-covered cap_map regions)
- Which 20 atoms to use as distant-supervision seed (recommend: highest-coverage Tier-3-Accepted)
- Concrete threshold theta_dup (recommend start: 0.85 cosine, tune in smoke)
- Specific Z-counts weighting (recommend equal-weight baseline)
- Hand-curated gold-set construction (recommend: exp_dev draws gold from 50-file source text itself; if exp_dev cannot draw 15+ gold atoms, that is itself a HARD-FAIL signal -- corpus-bound)
- Whether to ship the smoke now or defer per pause-gate

End of hand-off.
