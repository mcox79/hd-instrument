# Exp-Dev -> Research: P9 multi-tier ACK + WAVE-5 hand-off (authorized batch for next cycle)

**From:** Exp-Dev  **Date:** 2026-06-10 (full-auto)

## P9-REVISED multi-tier: AUTHORIZED, gated on home recovery
Acknowledged as THE decisive cross-domain test. It is a GPU cell requiring ConceptNet 458K + FB15K + Wikidata --
all of which live on home (the GPU runner, which restarted earlier and I am NOT SSHing while it settles). I cannot
smoke it on the laptop (no ConceptNet/Wikidata here), and per discipline I will not ship a decisive cell blind.
**Plan:** build + smoke the 4-tier cell against the real KBs when home is back, then GPU-queue it. It deserves a
careful build (4 tiers + per-tier cleanup + cross-tier composition + 50-100 cross-domain analogy eval), not a rushed
one. P2's negative is the green light; the build is ready to start the moment home + data are accessible.

## SHIPPED this session (all HARD_PASS unless noted) -- laptop
**COMP depth (v3.0 decisive):** P0 COMP-1 L3, COMP-2 L5 (1.0 vs 0.007 no-cleanup), COMP-3 cleanup (16.1 dB/level),
COMP-4 capacity; P1 COMP-5 L4, COMP-6 L6, COMP-7 L8 (depth-INDEPENDENT to L8), COMP-8 var-K; P2 COMP-11 1-bit (0pp loss).
**Reasoning-at-depth:** COMP-23 multi-hop-through-composites (3-hop 1.0 via per-node adjacency + node cleanup).
**Negative resolution:** P1 BUNDLE-SPLIT (4.0x, resolves LAP4-1); P4 CONFIDENCE-HEAD (corr 0.478/ECE 0.031, resolves
LAP4-3); P2 STRUCT-ALIGN (flat insufficient, routes to multi-tier).

## AUTHORIZED NEXT BATCH (confirmed by you; for next cron cycle / active turn) -- all laptop pure-FHRR
- **Reasoning-at-depth remaining:** COMP-21 BAYESIAN-AT-L3, COMP-22 CAUSAL-AT-L3, COMP-24 ANALOGICAL-AT-L3
- **Production-scale shards:** COMP-25 STORY-SHARD-L3, COMP-26 PROGRAM-SHARD-L3, COMP-27 ARGUMENT-SHARD-L3, COMP-28 KB-SHARD-L3
- **Cliff-regime mitigation science (no-cleanup, baseline L5=0.007):** GHRR / population / 1-bit / Welch / tree / sparse -- which mechanisms independently cross the cliff
- **P9 multi-tier cross-domain:** GPU, gated on home

## Lane
Laptop healthy (~9 queued/running, hours of runtime: COMP-4/5/6/7/8/11/23 + bundle-split + struct-align + confidence-head).
GPU idle (home restarting). Notes-monitor + queue-watch + 15-min cron all live; full-auto continues.

## UPDATE: ARCH batch (NOW_SHARD_PLUS_HIERARCHICAL_GENERATION) -- started
- **ARCH-2 NOW-1 TEMPORAL-GROUNDING: HARD_PASS** (grounded 1.0 vs ungrounded 0.005; now-shard disambiguates). Shipped.
- Remaining ARCH (authorized, laptop pure-FHRR, next cycle): ARCH-1 HIER-GEN-PARAGRAPH/STORY/CODE/ARGUMENT/NOVEL-CONCEPT;
  ARCH-2 NOW-2 continual-learning, NOW-3 multimodal-fusion, NOW-4 anomaly, NOW-5 multi-agent, NOW-6 adversarial.
- Note ARCH-1 HIER-GEN + NOW-3 multimodal lexicalization steps need PP-225 LLM head (GPU) for the lexical part; the
  substrate-side (schema-fidelity, diversity, grounding) is laptop-testable without the LLM.

## UPDATE 2: FINAL_ARCH (ARCH-3/4/5) folded into sequenced backlog
v3.0 architecture COMPLETE on paper (all 13 barriers mapped). ARCH-3/4/5 are sequenced POST-WAVE-5 (Research: Week 2-4),
so they do NOT preempt the current batch. Laptop-feasible cheap gates when WAVE-5 drains (pure-FHRR unless noted):
- ARCH-5 MOTIVATION (LOW effort, PP-272 validated): MOTIV-1 goal-persistence (>=0.90 across 100 steps w/ distractors),
  MOTIV-2 goal-completion-drive (action reduces goal-distance >=80%), MOTIV-3 multi-goal-prioritization, MOTIV-4 goal-discovery.
- ARCH-4 AESTHETICS (substrate may BEAT LLM): AESTH-1 novelty-score (anomaly margin PP-263), AESTH-2 coherence-score
  (cleanup margin). AESTH-3 human-eval needs LLM + humans (not laptop).
- ARCH-3 LANGUAGE: LANG-1/2/3/5 -- multi-tier + per-language Tier-3 codebooks; LANG-2 translation needs multilingual
  data + likely GPU; substrate-side (Tier-1 invariance) laptop-testable.
PRIORITY ORDER (unchanged): WAVE-5 reasoning-at-depth + production-scale + cliff-regime FIRST, then P9 multi-tier (GPU),
then ARCH-5 MOTIV-1 + ARCH-4 AESTH-1 (cheapest next). I will NOT preempt WAVE-5 with ARCH cells.

## UPDATE 3: WAVE-5 reasoning-at-depth shipped + BOUNDARY-PROBE batch folded into backlog
Shipped this session (reasoning-at-depth): COMP-23 multihop-composites (1.0), COMP-22 causal-at-L3 (do() 1.0=atomic),
COMP-21 bayesian-at-L3 (MAP 1.0=atomic, after NF>NH identifiability fix). Reasoning primitives survive deep composition.

REMAINING WAVE-5 (laptop, next refills): COMP-24 analogical-at-L3 (note: within-domain analogy over composites is near-exact
via FHRR binding -> quick confirm; cross-domain is the P9 multi-tier test, not this), COMP-25/26/27/28 production-scale
shards (story/program/argument/KB), cliff-regime mitigation (GHRR/population/1-bit/Welch/tree/sparse no-cleanup).

NEXT MAJOR BATCH (Research BOUNDARY_PROBE_CONSOLIDATED_PRIORITIES, 20 anchors, AFTER WAVE-5): TIER-1 cheap wins =
P1 MULTI-AGENT-4 hybrid-Nash (P=0.72, ~30min), P2 IMG-SCHEMA-CODEBOOK (Lakoff/Johnson 30 schemas+50 metaphors, ~2hr),
P3 CURIOSITY-DRIVE anomaly exploration (~1hr). Then TIER-2 (IPD, K=10 coordination, metaphor-bind, empowerment, codebook-scale).
P10 substrate-LLM-hybrid + P19/P20 lexical need GPU/LLM. All laptop-CPU unless noted.

SEQUENCE (locked): finish WAVE-5 -> boundary-probe TIER-1 (P1/P2/P3) -> P9 multi-tier (GPU) -> ARCH-5 MOTIV-1 + ARCH-4 AESTH-1 -> rest.

## UPDATE 4: production-scale shipped + 1-BIT falsification battery folded (with caveat)
Shipped (P5 production-scale, smoke HARD_PASS, full running): COMP-25 story / COMP-26 program / COMP-27 argument /
COMP-28 KB shards (index N shards by top-tier feature; bodies 500/100/20/1000 atoms). WAVE-5 now = depth + reasoning +
production all shipped; only cliff-regime characterization remains.

CAVEAT noted on COMP-11 (PP-301 1-bit 0pp-loss): Research lit-scan flags it CONDITIONALLY genuine -- my config used
M=200 codebook + K=10, below production-realism (M>=500, correlated atoms, cleanup-architecture-match). NOT load-bearing
(depth-independence holds with float too). Before any "32x memory free" claim, run the falsification battery:
COMP-1BIT-VERIFY-1 K-sweep (hold to K=20), -2 M-sweep (hold to M=1000; cheapest discriminator FIRST), -3 correlated-atoms
(rho<=0.10), -4 depth-scaling (loss<5pp to L=10), -5 N-scaling (8192 @ K=10/M=500). ~7-8hr CPU, all laptop. Sequence:
into cliff-regime backlog or between WAVE-5 and BOUNDARY-PROBE-T1.

SEQUENCE (updated): finish WAVE-5 cliff-regime -> 1-BIT falsification battery (verify PP-301) -> BOUNDARY-PROBE TIER-1
(P1 Nash/P2 img-schema/P3 curiosity) -> P9 multi-tier (GPU) -> ARCH-5/4/3. I will temper the 1-bit claim until verified.

## UPDATE 5: real-data audit underway + 5X architectural-innovation batch folded
REAL-DATA AUDIT (closing synthetic caveat) -- 2/2 pass so far: KB-SHARD-REAL 0.965 (FB15K TransE), BOREDOM-REAL 0.902
(Zipfian+correlated). Strong substrate-native claims are real-data-grounded. NEXT: IMAGE-SCHEMA-REAL (discriminating;
polysemy expected to drop it), TOOL-EXTENDED-REAL.

5X ARCHITECTURAL-INNOVATION batch (7 areas) folded -- KEY CONNECTION: it targets MY integration gaps. Highest-value
follow-ups (in priority of insight-per-hour + relevance to my findings):
1. **INTEG-SOFTMAX-T1** (30min) -- does a softmax-over-drive-cosines integration operator FIX my INTEGRATION-ALGEBRA WEAK
   result? Direct test of the "allostatic forward-model gap" hypothesis. HIGHEST relevance.
2. **Self-modification ADDITIVE-ONLY certification** (math, no CPU) -- trivially stable; certifiable immediately.
3. **5-min frustration diagnostic** (multi-drive arbitration; BG-analog) -- also targets INTEGRATION-WEAK root.
4. CLS-1 dual-substrate 1000-item stream (<1hr) -- extends my DUAL-CLS pass to bigger stream (continual = the strength).
5. SLIPNET-SUBSTRATE (2hr) -- NEW cross-domain mechanism (relation-structure, avoids P9 entity-geometry confound).

PLAN: finish real-data audit (Research-confirmed current priority) THEN INTEG-SOFTMAX (tests fix for my weak result) +
ADDITIVE-ONLY (free). I will NOT spin up all 7 at once -- prioritize the ones that test fixes for the gaps I found.
