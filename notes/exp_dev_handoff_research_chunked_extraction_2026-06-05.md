# exp_dev hand-off -- research: massive parallel chunked extraction

**Filed-by:** research sub-agent (2026-06-05)
**Trigger:** 2x drill delivery; notes/research_drill_massive_parallel_chunked_extraction_2x_2026-06-05.md
**Per [[feedback-no-experiment-design-in-prompts]]:** This file names WHAT to test and WHY; exp_dev designs the anchor, sweep grid, thresholds, and queue assignment with full autonomy.

---

## Pause state block

This hand-off is eligible for pickup on next exp_dev emergency-refill cycle.
Queue assignment and priority are exp_dev's call. Do NOT encode experiment design here.

---

## Anchor candidates (rank-ordered)

### Candidate 1 -- EXTRACTION QUALITY ABLATION (tier: urgent, binding)

**Anchor pointer:** substrate retrieval accuracy as a function of extraction model size (1B / 7B / 30B / 70B) on a held-out Wikipedia test set.

**Substrate-product reading:** The entire cheap-extraction architecture ($31 for 7.2M articles via CPU fleet + 7B Q4) is ONLY viable if 7B extraction quality does not cause a measurable retrieval accuracy cliff vs. 70B. If there is a sharp quality cliff at 7B (< 70% of 70B baseline accuracy), the $31 path is invalidated and the architecture must use >= 30B GPU workers. This is the single highest-leverage open question from the drill.

**Tier hint:** laptop CPU smoke (extract 10K articles at 1B, 7B; compare to small GPU run at 30B, 70B); result gates the full-scale architecture decision.

**Why now:** Research drill identified this as HARD-FAIL HF-2 threshold -- it must be resolved before any infrastructure investment in the CPU extraction pipeline.

---

### Candidate 2 -- CPU PREFILL THROUGHPUT VALIDATION (tier: cheap decisive test)

**Anchor pointer:** llama.cpp /embedding endpoint throughput on t4g.xlarge (or equivalent ARM CPU) for 7B Q4_K_M model at batch prefill mode on 10K Wikipedia passages (500-1000 tok each).

**Substrate-product reading:** The $31 full-Wikipedia cost estimate depends on 2500 tok/s effective throughput. If actual throughput is < 300 tok/s (HF-1 threshold), the CPU path cost rises to ~$250, no longer competitive with a 4-hour single H100 burst (~$10). This smoke test costs < $0.01 and takes < 15 minutes.

**Tier hint:** laptop CPU or single cloud CPU instance; pure throughput timing with no substrate involvement.

**Why now:** Cheapest decisive test in the entire drill. Should run before any architecture commitment.

---

### Candidate 3 -- APPLE SILICON PREFILL THROUGHPUT (tier: medium, if Candidate 2 passes)

**Anchor pointer:** 70B Q4_K_M prefill throughput on M-series Apple Silicon (M3 Ultra / M4 Max) via MLX or llama.cpp Metal backend, running in server/embedding mode (not generation mode).

**Substrate-product reading:** If Mac prefill throughput >= 1000 tok/s, 100 idle Macs extract full Wikipedia at 70B quality in < 10 hours for ~$1. If < 500 tok/s (HF-3 threshold), wall time increases to 39+ hours -- less attractive but still feasible as a multi-day campaign.

**Tier hint:** local laptop run (if M3/M4 Max available); extract 10K passages, time, extrapolate.

**Why now:** Validates the "volunteer Mac fleet at $1" product story before it gets communicated externally.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_massive_parallel_chunked_extraction_2x_2026-06-05.md
- Algebra scripts: d:/AI/hd-instrument/tools/orchestrator/chunking_algebra.py, chunking_algebra2.py
- Decisions log: d:/AI/hd-instrument/notes/research_decisions_2026-06-05.md
- BOINC reference (task granularity): arxiv.org/pdf/1903.01699

---

## Contract

- Candidates 1-3 are independent. Candidate 2 is the cheapest; do it first.
- If Candidate 2 (HF-1): throughput < 300 tok/s -- escalate to orchestrator before Candidate 1. The architecture recommendation changes.
- If Candidate 1 (HF-2): 7B quality < 70% of 70B -- escalate to orchestrator. Switches from CPU tier to GPU/Mac tier as primary recommendation.
- Pre-reg HARD-PASS/HARD-FAIL thresholds per research note Section 8 before queuing.

## Autonomy declaration

exp_dev owns: anchor naming, sweep parameter selection, threshold formulas, queue assignment (laptop CPU vs remote CPU vs GPU), pre-reg bands, and self-test cells for any formula. Research provides only the WHAT and WHY above.
