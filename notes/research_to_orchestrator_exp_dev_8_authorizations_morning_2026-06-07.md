# Research -> Orchestrator + Exp-Dev: 8 authorizations from user morning review

**From:** Research session
**To:** Orchestrator + Exp-Dev
**Date:** 2026-06-07 morning
**Trigger:** User reviewed overnight findings + authorized all 8 recommendations.

---

## Authorizations (all accepted)

1. **Pause customer-facing privacy claim language.** Cycle 150's "23x privacy advantage" and "HIPAA-grade ZKL <= 10%" were measured on synthetic keys. Cycle 151 shows 11x worse on real keys. Do not pitch these absolute numbers until SRHT fix lands.

2. **Run R3 diagnostic.** Encoder correlation analysis. 1 hour CPU, $0. Confirms anisotropy as ZKL root cause and scopes the SRHT engineering work. Gates the 3-5 day fix below.

3. **Queue SRHT engineering work.** 3-5 day engineering effort to apply Subsampled Randomized Hadamard Transform to keys before storage. Mechanism already validated cycle 148 as drop-in for Hadamard codebook. Conditional on R3 confirming anisotropy is the cause.

4. **Add 50-LOC confidence-weighted bundling filter to v1 Component 2 spec.** Required before any v1 distributed-reasoning build commit. Without it, K-hop collapses at K=3-5 in the cross-shard regime per the LSH-Paradox finding.

5. **Run Cell A (distractor coherence measurement).** 2 hours CPU, $0. Determines whether the 50-LOC fix is sufficient or whether v2 needs semantic sharding (3-4 weeks more). Gate before v1 distributed-reasoning build starts.

6. **Rebuild K-hop scaling test with higher ceiling.** Current test methodology hits K_max=60 ceiling and produces no signal on three open questions: N-scaling, sub-ceiling adversarial robustness, annealing schedule effect. Exp-Dev to redesign.

7. **Start benchmark suite definition this week.** Defines what "beats LLMs at relative size" means in measurable terms. Research session is taking this on. Estimated 1-2 weeks of focused work. Gates the pipeline build.

8. **Queue integrated pipeline build for week 3.** Substrate + small LLM (Llama-3.2-1B BASE) for generation. 2-3 weeks engineering. Don't start before benchmark suite is partly defined.

---

## What each session should do

### Exp-Dev

- Authorizations 2, 5, and 6 produce empirical cells: R3 (1 hr CPU), Cell A (2 hr CPU), and the K-hop ceiling-test redesign. Queue these. All local, $0.
- Authorization 3 (SRHT engineering) is conditional on Authorization 2's result. Don't dispatch SRHT cells until R3 confirms anisotropy.
- Authorization 4 is a SPEC CHANGE not a cell: v1 Component 2 needs the confidence filter added before any production build commit. Note this in Exp-Dev's build planning.

### Orchestrator

- Track Authorization 1 in the customer-claim language: any cycle that touches ZKL or privacy needs to use the "uncertain on real keys; SRHT fix in progress" framing until the SRHT cells pass.
- Authorization 7 means Research is starting benchmark-suite definition this week; expect more research drills focused on benchmark design rather than further substrate-internal exploration.
- Authorization 8 means the integrated pipeline build is week-3 work; queue it.

### Research (me)

- Authorization 7 is my work. Starting benchmark-suite definition drills today.
- User asked for 4 deep drills on the multi-hop coordination problem (separate from the 8 authorizations). Dispatched in parallel.

---

## Plain-language rules apply

User flagged 2026-06-07 morning that reporting was too jargony. All drill outputs and cycle synthesis should explain what things mean in plain terms, not just verdict-class shorthand. Reinforces existing plain-language feedback. Memory entry: feedback_plain_language_no_hype.md.

---

**END.**
