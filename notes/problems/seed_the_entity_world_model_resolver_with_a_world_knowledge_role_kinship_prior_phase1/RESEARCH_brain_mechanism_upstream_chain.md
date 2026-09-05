# Research: brain mechanism of the reference-resolution upstream chain (2026-09-05)

Dispatched research drill (44 verified citations). Full synthesis captured here (durable — solver may write this folder). **Owner directive: the wall is crossed ONLY if EVERY component — this one AND upstream — is brain-foundational.**

## HEADLINE
The brief's implicit hypothesis (a static role/kinship KB consulted AFTER records are built) is refuted on two fronts: (1) the brain never has a "records built" state — **bonding and resolution are interleaved word-by-word, and resolution's own output IS the record update**; (2) "salience" is not a positional/recency scalar but a composite of local center-tracking + a global discourse-segment stack + situation-model foregrounding.

## RANKED non-brain-foundational bottlenecks
1. **The two-pass "build records → resolve" architecture (dominant, gating).** Every incrementality finding converges: resolution and record-construction are the SAME continuous process; resolution's output IS the record update, and resolution can OVERRIDE the fast bonding proposal AND retroactively repair earlier records. A feed-forward pipeline that finishes building file-cards before consulting them structurally recreates the chicken-and-egg the brain never has. Likely why 0.540 (gold records) collapses to +0.006 (self-built): errors compound with **no retroactive repair**. P≈0.45.
   - PINNED: Garrod & Terras 2000 (JML 42) bonding (fast, cheap, associative) vs resolution (slow, situational, can override); Just & Carpenter 1980 immediacy; Van Berkum et al. 2003 Nref sustained frontal negativity 300-400ms mid-sentence; Van Berkum 2003 N400 150-200ms sub-lexical → resolution computed BEFORE the referring word finishes.
2. **Salience proxy = positional subject-rank + recency + ACT-R (co-dominant #2).** Misses: (a) Grosz-Sidner 1986 discourse-segment FOCUS STACK (segment-reopening restores accessibility regardless of distance — recency-decay cannot model this); (b) Morrow-Greenspan-Bower 1987 / Glenberg-Meyer-Lindem 1987 SITUATION-MODEL foregrounding (accessibility tracks the protagonist's spatial/possessive situation, decays by situation-model distance not token distance); (c) Gernsbacher 1990 active enhancement/SUPPRESSION (state transitions, not passive decay); (d) Centering (Grosz-Joshi-Weinstein 1995; Brennan-Friedman-Pollard 1987 SUBJ>OBJ>OTHER) is real but genre/parameter-fragile (Poesio et al. 2004) and non-universal — should be ONE soft cue, not a hard key. ACT-R base-level decay is legit (Anderson-Reder) but must be AUGMENTED with the 3 missing terms. P≈0.35.
3. **Head-lemma/WordNet matching as FINAL decision vs a bonding PROPOSAL.** Actually a faithful model of the bonding stage; the divergence is only if there's no subsequent resolution stage that checks situational/thematic/script coherence and can override. Fix = add resolution, not change matching.
4. **Gender/number/animacy filter** — lowest priority; well-pinned early categorical stage (Osterhout-Mobley 1995 P600; Barber-Carreiras 2005), should run in PARALLEL with thematic bonding.
5. **Mention detection** — under-addressed; follow-up drill if still bottlenecked after 1-3.

## Breaking the bootstrap (§1 verdict)
Prior knowledge is NECESSARY but NOT SUFFICIENT. Load-bearing = (b) online per-instance BINDING (schema→instance), gated by (c) fast constraints. Sanford-Garrod scenario-mapping: a scenario/role word pre-activates role slots into IMPLICIT FOCUS (high accessibility) BEFORE the filler — but the slot still must be MAPPED to the text instance online (an act, not a lookup). vmPFC holds schema / hippocampus does rapid congruency-gated instance binding (van Kesteren 2012; Gilboa-Marlatte 2017): fast if congruent, slow if not. **A static KB is a resource consulted DURING online binding, never a substitute for it.**

## Prior-knowledge FAILURE MODE (adversarial, important)
Bower-Black-Turner 1979: script-consistent-but-unstated actions get rising false-recognition — world knowledge FILLS GAPS AND MISLEADS when text is sparse. A role/kinship KB will HALLUCINATE confident-wrong bindings on sparse text — matching this failure mode is itself evidence of fidelity; a system that never errs this way is arguably LESS brain-faithful. → track a plausibility weight per binding; flag atypical fills; don't silently over-apply the prior.

## CHEAP DECISIVE TEST (run before any redesign)
Single-pass incremental resolve-and-update (resolve mention i using only cards from 1..i-1, updated immediately, no oracle) vs current two-pass self-built (+0.006) vs gold ceiling (0.540).
- HARD-PASS: single-pass recovers ≥0.20 abs (≥40% of gap) → architecture-order dominant; fix bonding/resolution separation + retroactive repair.
- HARD-FAIL: <0.05 → run the segment-stack + situation-model composite-salience test (still self-built, still incremental); if THAT recovers ≥0.15, salience is the fix.
- NOTE (disk check needed): the existing `world_model_predict` is ALREADY single-pass incremental and gives +0.006 — so the missing piece is likely the OVERRIDE + RETROACTIVE REPAIR (resolution reversing earlier wrong bonds), not merely "be single-pass." VERIFY on disk.

## Cross-thread principle (3rd confirmation)
Same wall as [[wsd-wall-is-contextual-representation-not-grounding]] and rare-sense episodic: **the brain does not pre-compute a stable static representation then consult it — it performs the computation (sense selection / reference binding) as an online per-instance context-gated act; the "representation" is a byproduct, not the input.** Any "build X then query X" two-pass design in the pipeline is a candidate for the identical failure and should be audited.

## IMPLICATION for THIS problem's plan
- THIS component (KB seed) = scenario-mapping prior that pre-activates role/kinship slots into implicit focus — NECESSARY but insufficient alone.
- UPSTREAM component(s) to make brain-foundational: (1) the resolution ARCHITECTURE — bonding→resolution with override + retroactive repair (interleaved, not batch); (2) SALIENCE/foregrounding — composite (centering + segment focus-stack + situation-model distance + suppression), replacing the positional+recency+ACT-R proxy.
- REUSE opportunity: the reader's already-improved brain-foundational AGENT/who-did-what (CM competition, agent arm 0.71→0.80 from the prior solved problem) is a better foregrounding/event-agent signal than the resolver's positional `rr==0` heuristic — a concrete "revisit the consumer to use the newly-optimized upstream" lever.
