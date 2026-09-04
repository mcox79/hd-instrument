---
problem: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader
status: PARTIAL
bar: "PASS = a glass-box ATL hub-and-spoke sense representation (distributional spoke bound with RICHER grounded spokes, semantic-inheritance-propagated to coverage) re-settled per context by the online predictive reader (NO transformer, NO training, NO external LLM), whose a_s on strict document-disjoint SemCor subordinate senses (through the wired diagnostic-context readout) CROSSES the 0.35 static-distributional ceiling CI-separated over the launch-pad 0.318, with a shuffled-grounding / shuffled-context info-free twin LOSING CI-separated and NO MFS regression. Report CI half-width + null p95; recompute floors on the item's own population. A rigorous located NEGATIVE -- richer grounded spokes at coverage STILL do not separate the superposed senses, with the named cause + number (e.g. the grounded spoke's own coverage/orthogonality ceiling) -- is a FULL PASS. Strategy lands the Q111 wire."
result: "PARTIAL = a LOCATED NEGATIVE on the brief's named mechanism (a FULL PASS by the bar) + a NEW brain-faithful directional POSITIVE, and the ceiling relocated with a number. (1) The RICHER grounded ATL hub-and-spoke does NOT cross: Binder-2016 65-dim + Warriner VAD, ATL distinctive-feature WHITENED, propagated to coverage by WordNet semantic inheritance, bound to the launch-pad distributional atom -- fed to the wired biased-competition readout, concat-hub a_s=0.283, which LOSES to the launch pad 0.313 CI-separated [-0.044,-0.015]; grounded-keys-alone 0.184; and the concat-hub beats its shuffled-grounding twin 0.162 CI-sep, so the grounded signal is REAL but insufficient. (2) THE SURPRISE THAT LOCATES THE CAUSE: the grounded keys DO separate the senses distribution merges -- w2v gloss keys of gold-vs-dominant cos=0.799 (superposed), grounded keys cos=0.222 (separated), and among the 1277 distribution-MERGED pairs grounding 'rescues' 80% (cos<0.5). So the brief's orthogonality premise HOLDS at the key level; grounding still does not help because (a) coverage is only 0.477 of test pairs and (b) the loss is QUERY-side selection, not key separability (the parent proved KEY-unwinnable=0.000). (3) THE REAL LEVER IS QUERY-SIDE AND BRAIN-FAITHFUL: precision-weighting (Friston selective gain -- gamma>1 / top-k on the diagnosticity, the multiplicative gain that lets a high-precision subordinate cue overturn the dominant prior) CROSSES the launch pad: a_s=0.3364 vs 0.3133, delta +0.0232 CI-sep [+0.012,+0.035], ci_hw 0.0112 = null_p95 0.0112, the shuffled-diagnosticity twin LOSES (0.271, delta +0.066 CI-sep), and it does NOT regress the dominant-sense/MFS population (all-items 0.420->0.435, +0.014). (4) BUT no glass-box readout/representation lever reaches the 0.35 ceiling (best 0.336<0.35; candidate-restriction-by-topic HURTS 0.304, distinctive-whitening the w2v keys is ill-conditioned 0.162): the crosser is a broad-coverage SENSE-DISCRIMINATIVE connection matrix W (parent proved oracle-W -> a_s 0.995; coverage-bound at 52%), which is the owner-DONE consolidation sibling's domain, NOT the ATL grounded hub. (5) THE FULL UPSTREAM BRAIN-FOUNDATIONAL CHAIN, BUILT AND MEASURED AS A MONOTONIC FIDELITY LADDER (grounded sense keys -> grounded/bootstrap ENCODING sense-resolver -> Hebbian bind-to-resolved-sense -> cross-situational consolidation -> precision-weighted W readout; every component the brain's actual computation, research-verified): the sense-discriminative-W ARCHITECTURE helps ONLY when the encoding resolver is correct -- GOLD-resolved W beats base by +0.028 on the gold-attested subset (a_s ~0.335 vs ~0.307; the ONLY positive arm, directionally > every glass-box resolver; borderline, NOT robustly CI-separated -- which sharpens the negative), while EVERY glass-box encoding resolver FAILS to build a clean W (distributional ~0.000, grounded -0.028, grounded+precision -0.016, propose-and-verify bootstrap -0.012 -- none beats base). This LOCALIZES the single remaining non-brain-foundational component: the encoding-time sense-resolver, which is trapped in the FROZEN, non-recomputed sense-conflated w2v context representation (100% of the loss sits there; grounding never touches the context side). An independent literature drill converged on the identical localization. So the wall is a genuine fixed point: to build the W that would disambiguate, you must first disambiguate, and no glass-box cue breaks the circularity because the subordinate sense is inseparable in the frozen representation the brain replaces by contextual re-computation. All a_s: strict document-disjoint SemCor subordinate, subject-weighted, n=2676/2675, through the wired hdlab.diagnostic_context_wsd, glass-box, frozen 200-dim w2v, NO external LLM/transformer/training; gold used only as the diagnostic-context readout oracle at eval and as the idealized-resolver reference arm, never at inference."
floor: "launch-pad RICH-w2v diagnostic a_s = 0.3133 (this session, threads=1 deterministic; the parent's clean-foundation 0.318 reproduced first-hand); gloss-w2v floor = 0.2512 (parent 0.251 reproduced); the info-free twins: shuffled-diagnosticity 0.2707 and shuffled-grounding 0.1615 (both LOSE CI-separated to their arms). Every arm recomputed on its own population."
controls: "shuffled-GROUNDING twin (grounded keys permuted onto WRONG senses -> concat-hub beats it +0.122 CI-sep, so the grounded signal is real -- and yet the hub still loses to the launch pad, so grounding is real-but-insufficient); shuffled-DIAGNOSTICITY twin (precision gain applied to permuted/WRONG context words -> loses -0.066 CI-sep, so the precision win is the CORRECT diagnostic words, not the sharpening shape); SEPARABILITY DECOMPOSITION (grounded cos(gold,dominant)=0.222 vs w2v-gloss 0.799 -> EXCLUDES 'grounding cannot separate superposed senses'; localizes the null to query-side + 0.477 coverage, NOT key separability); MFS no-regression guard (all-items 0.420->0.435 +0.014 -> the precision gain does not hurt the dominant population); distributional candidate-restriction (0.304 < launch pad -> EXCLUDES 'prune-by-topic helps'; it reinforces the dominant sense, exactly the Deco-Rolls biased-competition narrow-working-range prediction); distinctive-whitening of the distributional keys (0.162, ill-conditioned over 200-dim -> EXCLUDES 'decorrelating the w2v atoms helps'); floors reproduced first-hand (gloss 0.251, launch pad 0.313). Paired 5000x bootstrap CI half-width + sign-flip null p95 on every contrast; each control excludes a distinct rival explanation."
files_changed: "experiments/exp_atl_hubspoke_grounded_separability_v1.py (the richer grounded ATL hub + separability decomposition), experiments/exp_atl_hubspoke_query_side_readout_v1.py (the query-side brain-faithful levers: precision-weighting, candidate-restriction, distinctive-whitening), experiments/exp_atl_hubspoke_grounded_disambiguate_then_bind_v1.py (the FULL upstream chain: grounded/bootstrap encoding resolver -> Hebbian W -> consolidation -> precision readout, as a monotonic brain-fidelity ladder), experiments/exp_atl_hubspoke_discourse_situation_prior_v1.py (the discourse/situation-prior arm -- Vu-Kellas domain-of-reference, located negative), experiments/exp_atl_hubspoke_ideal_full_chain_v1.py (the IDEAL max-coverage gold-W chain + leave-one-doc-out + inheritance -- closes the coverage route; the brain-comparison signal-loss ladder), experiments/exp_atl_hubspoke_contextual_recompute_v1.py (the frozen-representation fix: AutoExtend glass-box de-superposition + context re-computation -- located negative, forces the invariant decision), experiments/exp_atl_hubspoke_joint_ppr_recompute_v1.py (the FULLY-JOINT re-computation via the landed hdlab.grounded_semantic_graph PPR organ -- topical, located negative), experiments/exp_atl_hubspoke_ppr_signal_loss_v1.py (drill: degree-bias REFUTED, leak = topical edges), experiments/exp_atl_hubspoke_actr_ideal_chain_v1.py (the ACT-R ideal chain: experience-weighted directional discriminative edges + fan-specificity + amplify-weak = best arm 0.345, still < 0.35, Zipf-bound edges), experiments/exp_atl_hubspoke_multicue_integration_v1.py (reliability-weighted integration of all cues = 0.344, confirms the ceiling; grounded weight->0), experiments/exp_atl_hubspoke_signal_loss_ladder_v1.py (oracle decomposition: ORACLE_single 0.868 / ORACLE_signed 0.627 -- query-side diagnostic-word ID is the largest loss), experiments/exp_atl_hubspoke_controlled_retrieval_v1.py + _gated_v1.py (controlled-retrieval anti-dominant attack: crosses 0.35 ungated 0.382 but fails MFS guard = prior shift; gated preserves MFS but gain vanishes), experiments/exp_atl_hubspoke_knowledge_integration_v1.py (structured-membership knowledge integration: apparent PASS 0.360 was TRANSDUCTIVE LEAKAGE; clean inductive 0.261 < precision -- W_MODE=even|loo documents the delta), experiments/exp_atl_hubspoke_signal_trace_v2.py (chance-controlled re-trace: ORACLE_single was ~72% combinatorics; per-token gold signal +0.047 above chance = thin/representation-thinned; enabler = contextual re-representation not knowledge), experiments/exp_atl_hubspoke_context2vec_aligned_v1.py (traced the encoder space-mismatch bug + scale trend 0.192->0.207, trained encoder abandoned as non-brain-faithful), experiments/exp_atl_hubspoke_full_chain_signal_trace_v1.py (the full brain-faithful chain ladder R0->R6: climbs to 0.340 at controlled retrieval, stalls at consolidation for Zipf-thin rare senses; reader mu adds +0.011), notes/research_lfs_rare_sense_enabler_knowledge_vs_context_2026-09-04.md, verification/test_atl_hubspoke_meaning_channel.py (W1-W8), notes/research_grounded_disambiguate_then_bind_2026-09-04.md + notes/research_exemplar_based_contextual_recomputation_wsd_2026-09-04.md (research verification: exemplar contextualization Zipf-swamps), data/exp_atl_hubspoke_grounded_separability_v1/metrics_full.json, data/exp_atl_hubspoke_query_side_readout_v1/metrics_full.json, data/exp_atl_hubspoke_grounded_disambiguate_then_bind_v1/metrics_full.json"
reverify: ".venv/Scripts/python.exe verification/test_atl_hubspoke_meaning_channel.py   # W1-W8 (grounding-neg; precision-positive +0.02 CI-sep; gold-W helps only where the rare sense is attested + borderline; glass-box resolvers fail; ideal max-coverage W does NOT cross; glass-box de-superposition de-superposes but a_s drops). The JOINT PPR arm is reproduced by its own cell (data/exp_atl_hubspoke_joint_ppr_recompute_v1/metrics_full.json): PPR 0.264 / fuse 0.323 < precision 0.342 -> topical, does not cross"
---

## INTEGRATED_BY_STRATEGY (2026-09-04) — EXCELLENT (a rigorous located-negative + one landable win)
Reverified via `verification/test_atl_hubspoke_meaning_channel.py` (W1–W8, strict document-disjoint SemCor subordinate, n=2676) + a new pure-numpy landing witness `verification/test_diagnostic_context_precision_landing.py` **4/4** (default byte-identity on 200 cases + the param is live + verbatim to the reference).
- **WIRE LANDED (Q111, default byte-identical):** `hdlab/diagnostic_context_wsd` gains `gamma`/`topk` precision-weighting params on `diagnostic_query`/`diagnostic_context_scores`/`pick_sense` (guarded → default gamma=1.0/topk=None is BIT-identical to the pre-P9 readout; consumers opt in). The precision win lifts a_s 0.313→0.336 (+0.023 CI-sep, twin loses, no MFS regression); does NOT reach ~0.35.
- **DID NOT land (measured negatives):** the grounded hub into the keys (0.283<0.313), reading-derived W default-on (regresses rare senses), a trained encoder (scale-bound, not brain-foundational).
- **§2b folded.** The ceiling is relocated to the encoding-time sense-resolver (frozen sense-conflated context) — the crosser is broad-coverage correctly-resolved rare-sense EXPERIENCE.
- **FOLLOW-ON FILED:** `grow_broad_coverage_correctly_resolved_rare_sense_experience_the_meaning_channel_learner_on` (priority 5).
- **⚠️ OPEN OWNER QUESTION (surfaced to the owner):** hold the no-transformer invariant + accept the ~0.34 rare-sense ceiling (the coverage/learner-on route), OR relax it for ONE offline contextual-sense asset to reach ~0.53? Recommendation: HOLD.

## What was asked, and what the disk says

The brief: break the ~0.35 glass-box subordinate-sense ceiling the 100%-brain-foundational way -- represent each sense
as the **ATL HUB-AND-SPOKE** (the distributional spoke BOUND WITH grounded spokes -- perceptual + affect + relational,
orthogonal to distribution), **ENRICH THE SPOKES** beyond the coarse 12-dim norms (Binder-class ~65-dim + affect +
relational), **propagate to coverage by SEMANTIC INHERITANCE**, and **re-settle per context with the ONLINE PREDICTIVE
READER** -- and prove a_s crosses 0.35 CI-separated with an info-free twin losing, OR a located negative naming why
grounding cannot separate the superposed senses at coverage.

**The disk says PARTIAL, and it is a richer answer than either "solved" or a bare "impossible":**

1. **The richer grounded ATL hub-and-spoke is a LOCATED NEGATIVE (a FULL PASS by the bar).** Built faithfully at
   richness (Binder-65 + Warriner VAD, ATL-whitened, WordNet-inheritance-propagated), it does **not** cross the launch
   pad -- concat-hub a_s **0.283 < 0.313**, CI-separated *below* it.
2. **But NOT for the reason the brief guessed.** The brief's premise -- "grounded dimensions are orthogonal to
   distribution, so they separate senses co-occurrence merges" -- **HOLDS at the key level** (grounded cos(gold,
   dominant) = **0.222** where the w2v gloss keys sit at **0.799**; grounding pulls apart **80%** of the pairs
   distribution merges). Grounding still does not help because the bottleneck is **query-side selection + ~0.48
   coverage**, not key separability (the parent already proved the keys are always separable, KEY-unwinnable = 0.000).
3. **The real lever is query-side, and one brain-faithful query-side mechanism gives a genuine CI-separated gain:**
   **precision-weighting** (Friston selective gain) lifts a_s **0.313 -> 0.336** (+0.023 CI-sep, twin loses, no MFS
   regression) -- new, and neither parent found it. It does not reach 0.35; the crosser is a broad-coverage
   **sense-discriminative W** (the owner-DONE consolidation sibling), which this problem re-confirms with numbers.

All a_s: strict document-disjoint SemCor (odd docs = test), subordinate senses, subject-weighted, n=2676, through the
WIRED `hdlab/diagnostic_context_wsd`, glass-box, frozen w2v, NO external LLM / transformer / training.

## >>> THE GAP TO IMPROVE THIS -- STATED PLAINLY (read this first) <<<

The full brain-faithful chain was assembled and traced end-to-end (ladder below). It CLIMBS correctly and the gap is
NOT where the brief guessed. Here is exactly where the signal is and is not lost:

- **NOT the readout.** Controlled-retrieval precision-weighting is the single biggest gain (+0.069) and is near-optimal
  and landable. **Do not look for more here.**
- **NOT the sense keys / knowledge.** Hub-and-spoke keys help (+0.057); grounding separates the senses fine (cos
  0.222); adding curated + corpus knowledge INDUCTIVELY HURTS (0.261 < 0.34) and only "helped" via measured leakage.
- **NOT a static extractor.** Chance-controlled, the per-token diagnostic signal in frozen w2v is real but THIN
  (+0.047 above chance); we already extract near its ceiling.
- **THE GAP, precisely: the CONSOLIDATION-OF-EXPERIENCE stage cannot build a strong representation for RARE senses,
  because rare senses are Zipf-thin (~1-2 instances in any realistic corpus).** On the assembled chain the climb
  stalls exactly here: glass-box consolidation HURTS rare senses (worse than random -- mis-resolution binds the
  dominant sense's associates onto the rare one), and EVEN A PERFECT (gold) RESOLVER does not help rare senses (too
  few instances to consolidate) though it helps well-attested ones (+0.034 all-population). The enabler the whole
  field uses -- contextual re-representation that THICKENS the thin signal -- requires either transformer-scale
  training (the invariant boundary) or lifetime-scale rare-sense EXPERIENCE, and our fixed test set contains neither.

So the ceiling on this rare-sense task is **~0.34** (controlled retrieval), and the ONE thing standing between ~0.34
and the ~0.53 a competent reader reaches is **broad-coverage, correctly-resolved RARE-SENSE experience** -- not a
better encoder algorithm, not more knowledge, not a better readout.

## >>> WHAT THE NEXT PROBLEM SHOULD FOCUS ON <<<

The next problem should attack the ONE localized gap: **grow broad-coverage, correctly-resolved rare-sense
experience over time** (the learner-on / consolidation north star), because that -- and only that -- thickens the
signal for rare senses without crossing the invariant. Concretely, it should:
1. **Target rare-sense COVERAGE, not the readout or the keys** (those are solved / near-ceiling here). The measured
   bottleneck is that ~half of test senses have <=1-2 correctly-resolved instances.
2. **Break the encoding-resolver circularity with GROUNDING-ANCHORED BOOTSTRAPPING (propose-and-verify, Trueswell
   2013):** resolve the CONFIDENT/concrete cases first (where grounding + precision are reliable), bind them, and let
   the growing sense-discriminative store resolve progressively harder cases -- iterated over a LARGE corpus, ONLINE
   (no batch training). This session showed a single-pass glass-box resolver poisons rare-sense W; the untested lever
   is the iterated, confidence-gated bootstrap that only binds when resolution is trustworthy.
3. **Consolidate with the gate that is already owner-DONE** (`consolidation_gate` + `cls_growth`: keep-what-recurs,
   rollback, EMA anchor) so growth is safe and the raw regression can never ship.
4. **Measure on the SAME instrument** (strict doc-disjoint SemCor subordinate a_s + the full-population consumer
   guard), with the acceptance test PROVEN here: recover the rare-sense gain as coverage grows, WITHOUT regressing
   the dominant population, and with a strict INDUCTIVE (train-only) W + shuffled twin (two false PASSes this session
   were caught only by those controls).
The alternative (owner decision, NOT brain-foundational): an offline contextual-sense asset (a scale-trained encoder)
-- crosses to ~0.53 but is the invariant boundary. Recommend the coverage/learner-on route; hold the invariant.

## How the brain does this -- what is PINNED, what we INVENTED, and what we replicated (5 research drills, cited)

Five primary-source drills this session (notes below). The brain-foundational ledger, marked:

| choice | brain mechanism | verdict |
|---|---|---|
| ATL hub + grounded spokes | canonical CSC spokes = **Sound, Praxis, Valence, Vision, Function, Speech** (Lambon-Ralph 2017, NRN) | **PINNED** -- and note there is **NO canonical "relational" spoke**; the brief's "relational spoke into the ATL hub" is a mild mislabel (relational/thematic knowledge is a *separate* system -- AG combinatorial hub, Binder-Desai 2011; or emergent, Rogers 2004; "awaits future work", Lambon-Ralph 2017) |
| Binder-65 perceptual + Warriner VAD as the spoke asset | direct behavioural measurement of the perceptual/affect channels | **PINNED SUBSTITUTE** for lived perception (admissible offline norms) |
| distinctive-feature WHITENING | ATL privileges DISTINCTIVE features == decorrelate the dominant shared axis (Patterson-Nestor-Rogers 2007) | **PINNED** -- applied to the grounded spoke (it is what the landed `hdlab.grounded_similarity` distinctive read-out does) |
| semantic INHERITANCE to coverage | category-based grounding inference down the taxonomy | **PINNED as the coverage mechanism**, but with a PINNED failure mode: regular polysemy is *defined* by two senses sharing taxonomic/qualia structure (Copestake-Briscoe 1995; Apresjan 1974; Pustejovsky 1995), so inheritance under-differentiates exactly those pairs by construction |
| precision-weighting readout | precision = **multiplicative gain on bottom-up error**, "lets a high-precision error for a low-prior cause overturn a strong prior" (Friston 2010; Bastos 2012); plain reweighting has a **narrow working range** and the higher-baseline (dominant) candidate wins below a critical bias (Deco-Rolls) | **PINNED** -- and it is the mechanism that gives our only CI-separated gain |
| candidate-set restriction | strong context evokes a **domain of reference including ONLY the situation-appropriate sense** (Vu-Kellas 2003) -- a binary prune, not reweighting | **PINNED** -- tested; grounded-domain restriction ties, topic-restriction HURTS |
| online predictive settling | Kintsch C-I / Rao-Ballard settling to a coherent fixed point; relevance == connection strength | PINNED, but the parent proved **iterative settling == one-shot** and recurrent settling **over-collapses** to the dominant basin -- so the settling SHAPE is not the lever; the connection matrix W is |

## The evidence chain (each strict document-disjoint, twin-controlled, glass-box, NO LLM, n=2676)

**A. Floors reproduced first-hand.** gloss-w2v a_s **0.2512** (parent 0.251); RICH launch-pad diagnostic **0.3133**
(parent's clean-foundation 0.318 -- the +0.067 this problem builds on). `exp_atl_hubspoke_grounded_separability_v1`.

**B. The richer grounded ATL hub-and-spoke does NOT cross (the located negative).** Binder-65 + Warriner VAD (dim=68,
434 covered words, top-PC 24.5% of variance), ATL-whitened, inheritance-propagated (sense coverage 0.544):
- grounded-keys-alone a_s **0.184**; concat-hub `[w2v (+) 0.25*grounded]` a_s **0.283** -- both BELOW the launch pad
  0.313 (hub vs launch pad -0.030 CI-sep [-0.044,-0.015]).
- the concat-hub BEATS its **shuffled-grounding twin** 0.162 (+0.122 CI-sep) -- the grounded signal is REAL, just insufficient.

**C. The separability decomposition -- the brief's premise holds, but it is not the bottleneck.** For each test item,
gold (subordinate) vs the max-SemCor-prior DOMINANT competitor:
- **grounded whitened cos(gold, dominant) = 0.222** (median 0.102; 80% of pairs separable at cos<0.5) -- vs the
  **w2v gloss keys at cos 0.799**. Grounding DOES pull apart the senses distribution superposes.
- among the 1277 distribution-MERGED pairs (w2v cos >= 0.5), grounding rescues (cos<0.5) **80%**.
- so key-separability is NOT the ceiling; the residual is (a) coverage 0.477 of pairs and (b) the QUERY side
  (the parent's oracle decomposition: 100% of the loss is the context query; grounding the query is redundant with
  the w2v context). Enriching the KEYS solves a problem the gloss keys already solve.

**D. The query-side, brain-faithful levers (`exp_atl_hubspoke_query_side_readout_v1`).** Attacking the side that carries
100% of the loss:
- **PRECISION-WEIGHTING (Friston selective gain: gamma>1 or top-k on the per-word diagnosticity) is the winner:**
  a_s **0.3364** (gamma=2 / top-k=5-8, dev-selected) vs launch pad 0.3133, **+0.0232 CI-sep [+0.012,+0.035]**,
  ci_hw 0.0112 = null_p95; the **shuffled-diagnosticity twin LOSES** 0.271 (+0.066 CI-sep); **MFS no-regression**
  (all-items 0.420->0.435, +0.014). This is the mechanism Deco-Rolls predicts is necessary -- plain reweighting
  cannot overturn the dominant baseline, but a sharpened gain on the few genuinely-diagnostic words can.
- grounded candidate-restriction (Vu-Kellas domain-of-reference in grounded space) ties (0.327); distributional
  restriction HURTS (0.304 -- reinforces the dominant, the narrow-working-range failure); distinctive-whitening the
  200-dim w2v keys is ill-conditioned (0.162). Combining precision + grounded-restriction does NOT stack (0.325 --
  the levers are redundant, exploiting the same diagnostic signal).
- **No lever reaches 0.35.** The 0.313->0.336 gain is real and brain-faithful, but the 0.35->0.85 headroom
  (oracle-context ceiling 0.853; oracle-W 0.995, parent) is **W quality x coverage**, not the readout.

## THE FULL UPSTREAM BRAIN-FOUNDATIONAL CHAIN -- the monotonic fidelity ladder (owner directive: "every component, you and upstream, must be brain-foundational")

The located negative above closes the ATL grounded hub as the crosser but leaves the owner's question: does building the WHOLE upstream chain brain-foundationally let it cross? I built it and measured it as a monotonic
brain-fidelity ladder (`exp_atl_hubspoke_grounded_disambiguate_then_bind_v1`). The chain the parent proved is the
real lever is a SENSE-DISCRIMINATIVE connection matrix W ("which context words signal THIS sense over its dominant
twin"; oracle-W -> a_s 0.995). W is built by DISAMBIGUATE-THEN-BIND: resolve each encounter's sense at ENCODING,
Hebbian-bind context to the RESOLVED sense, cross-situationally consolidate. Every component is the brain's actual
computation, research-verified this session:
- ENCODING-TIME sense resolution then bind-to-resolved-sense: PINNED (encoding specificity, Tulving-Thomson 1973;
  Light-Carter-Sobell 1970 homograph demo; controlled retrieval LIFG/pMTG, Jefferies 2013).
- Hebbian bind + cross-situational CLS consolidation: PINNED (McClelland 1995; Kumaran-Hassabis-McClelland 2016).
- GROUNDING to break the acquisition bootstrap circularity: PINNED for concrete referents (Yu-Smith 2007; Trueswell
  propose-and-verify 2013) -- but NO support for abstract/regular polysemy (Copestake-Briscoe 1995: regular-polysemy
  senses share taxonomic structure by definition).
- Precision-weighted readout over W: PINNED (Friston 2010; this problem's Cell B).

I varied ONLY the ENCODING sense-resolver (the one component whose fidelity is in question) and held everything else
fixed, W built document-disjoint from even-doc SemCor, tested on the gold-attested odd-doc subordinate subset (the
parent's coverage definition, 52%), a_s vs the launch-pad base on the SAME items:

| encoding resolver (rung) | a_s (W) | a_s (base, same items) | W - base | CI-separated? |
|---|---|---|---|---|
| distributional (parent readbind) | 0.368 | 0.370 | **-0.004** | no |
| grounded (Cell A hub) | 0.319 | 0.347 | **-0.028** | no |
| grounded + precision (Cell B) | 0.320 | 0.336 | **-0.016** | no |
| propose-and-verify BOOTSTRAP (Trueswell) | 0.318 | 0.335 | **-0.012** | no |
| **GOLD (idealized brain resolver)** | **~0.335** | ~0.307 | **+0.028** | borderline (not robust) |

**The ladder is the proof, in both directions.** When the encoding resolver is CORRECT (gold -- the idealized brain
resolver), the fully-brain-foundational chain is the ONLY arm that helps at all (+0.028, directionally > every
glass-box resolver, though borderline / not robustly CI-separated -- even the idealized resolver barely clears, which
sharpens the negative), pointing at the oracle-W 0.995 ceiling. When the resolver is any GLASS-BOX approximation, the chain FAILS -- and it
fails MORE, not less, as we add grounding (grounding is WORSE than distribution here: -0.028 vs -0.004), and the
propose-and-verify bootstrap does not rescue it (-0.012). So the architecture is validated and the wall is localized
to exactly ONE component: **the encoding-time sense-resolver.**

**Why that component cannot be made brain-foundational-AND-correct glass-box -- the fixed point.** To build a
sense-discriminative W you must resolve the subordinate sense at encoding; but resolving the subordinate sense IS the
problem we are trying to solve, and every glass-box resolver operates on the FROZEN, sense-conflated w2v where the
subordinate sense is superposed onto its dominant twin (Arora 2018) -- so it systematically mis-resolves the rare
encounters to the DOMINANT sense, contaminating W with the dominant sense's associations. Grounding does not break
the circularity because the grounded hub is too coarse for the abstract regular polysemy that dominates SemCor
(Copestake-Briscoe). Gold "works" precisely because human annotation BYPASSES the frozen representation. **An
independent literature drill converged on the identical localization: the last non-brain-foundational component is
the CONTEXT/word representation the resolver matches against -- a frozen, non-recomputed bag of word statistics,
where 100% of the measured loss sits, and which grounding never touches.** The brain avoids the fixed point by
CONTEXTUALLY RE-COMPUTING each word as it reads (the frozen vector is replaced per context); the only glass-box
route to that re-computation is a scale-trained contextual encoder = the invariant boundary (no transformer, no
training), which is why it is off-limits and why this is a located negative rather than a clean pass.

**Coverage is the second, independent wall.** Even the gold resolver only reaches +0.030 on the 52%-attested subset
and is coverage-dragged BELOW the launch pad on the full population (gated overall gold-W 0.296 < 0.313), because rare
senses are Zipf-starved in any realistic corpus. Broadening the corpus raises coverage but cannot clean a
resolver-contaminated W, so it does not rescue a glass-box resolver.

**The DISCOURSE / SITUATION prior -- the last unbuilt brain-foundational component -- is also a located negative
(`exp_atl_hubspoke_discourse_situation_prior_v1`).** It was the one route that adds information BEYOND the sentence
(so it could in principle exceed the sentence-level oracle-context ceiling 0.853): build the document-level discourse
domain (mean content-word field over the passage, target sentence excluded -- no leak) and BOOST/RESTRICT candidate
senses by it (Vu-Kellas domain-of-reference; Till-Mross-Kintsch 1988 discourse-driven subordinate selection). Result:
discourse-boost 0.334 == local-precision 0.335 (no gain), discourse-RESTRICTION HURTS (0.294 -- it prunes the
subordinate sense), and the foreign-document twin ties the real arm (0.332). Cause: a real (heterogeneous) SemCor
document's discourse domain is TOPICAL, so like grounding / co-occurrence / exemplars it reinforces the DOMINANT
sense; the strong subordinate-favoring situational domain Vu-Kellas constructed in the lab is not present in natural
text. Six brain-foundational routes now converge on the identical wall.

**So the brain's mechanism is IDENTIFIED and shown un-replicable glass-box, with the specific reason** (the bar for
claiming convergence): the subordinate-sense cue is LOCAL and SENSE-DISCRIMINATIVE, and it is inseparable in the
frozen sense-conflated representation; every glass-box signal that is NOT the frozen local vector (grounding,
discourse, exemplars, learned W) is either topical (reinforces the dominant) or trapped in the same frozen space. The
brain's escape -- online contextual RE-COMPUTATION of the word -- is the invariant boundary. This is a
mechanism-complete located negative, not an exhausted-variations one.

## THE IDEAL FULL CHAIN, BUILT -- and it CLOSES the "grow W coverage" route (owner-authorized offline-foundation relaxation)

The owner authorized relaxing the invariant for the one offline foundation asset. The proof said the crosser is a
broad-coverage sense-discriminative W (oracle-W -> 0.995), so I built the IDEAL version of it
(`exp_atl_hubspoke_ideal_full_chain_v1`): W built from the GOLD-resolved sense-tagged foundation (the idealized
encoding resolver, admissible offline asset) at MAXIMAL coverage -- leave-one-DOCUMENT-out over all SemCor + brain-
faithful SEMANTIC INHERITANCE of W to unseen senses -- read by the precision-weighted biased-competition readout.
Strict document-disjoint; gold used only to build the offline W, never as an inference label on the test item.

**The coverage ladder (full-population a_s, n=2676):**

| rung | a_s | W-coverage |
|---|---|---|
| R0 launch-pad (frozen w2v) | 0.316 | -- |
| R1 + precision-weighted readout | **0.333** | -- |
| R2 gold-W, even-doc coverage | 0.301 | 0.52 |
| R3 gold-W, leave-one-doc-out (all SemCor) | 0.306 | 0.62 |
| R4 + semantic inheritance of W | **0.266** | 0.77 |
| REF oracle-W ceiling (parent) / human | 0.995 / ~0.65 | -- |

**Even the ideal offline W foundation does NOT cross -- it lands BELOW the precision readout, and inheritance makes
it worse.** This is a decisive, mechanism-complete negative that CLOSES the coverage route both parents (and my
earlier draft) held open, for a now-airtight reason: raising coverage grows the DOMINANT sense's W faster than the
Zipf-starved subordinate's (median 2 occurrences per test sense even leave-one-doc-out), so a readout that trusts W
picks the dominant; and SEMANTIC INHERITANCE blurs regular-polysemy siblings (Copestake-Briscoe -- measured: R4
-0.067 vs R3). W helps ONLY on the narrow subset where the SUBORDINATE sense itself is well-attested (+0.030), and
that subset cannot be grown -- attesting rare senses is Zipf-impossible at scale and inheritance blurs them. **So the
wall is the REPRESENTATION, not the knowledge: count-based sense-discriminative knowledge is Zipf-bound for rare
senses; only a representation that GENERALIZES the rare sense from its fine-grained contextual pattern (contextual
re-computation) escapes it -- which is exactly why a transformer crosses (0.53) and every count-based/frozen-vector
method here (grounding, W at max coverage, exemplars, discourse) does not.**

## THE FROZEN-REPRESENTATION FIX, PROTOTYPED -- glass-box contextual RE-COMPUTATION is a located negative that FORCES the invariant decision

The one stage left is stage 1 (the frozen word representation itself). I prototyped the ideal glass-box fix
(`exp_atl_hubspoke_contextual_recompute_v1`): AUTOEXTEND-style sense DISENTANGLEMENT (Rothe-Schutze 2015 -- a shallow
linear decomposition, same PCA/ICA family the research ruled admissible; NO transformer, NO gradient-epoch training,
NO external LLM) that solves for a DISTINCT vector per WordNet sense (word = sum of its senses; sense pulled toward
its relational neighbours), then RE-SELECTS the sense by context coherence (predictive settling). Measured:
- **It DOES de-superpose the senses** -- cos(gold, dominant) drops from gloss 0.854 to AutoExtend 0.710 (the
  decomposition genuinely pulls the superposed senses apart -- the brief's premise, at the representation level).
- **...but a_s DROPS: gloss keys 0.323 -> AutoExtend keys 0.213 -> context-recompute 0.211** (twin 0.163); it LOSES
  to the launch pad CI-separated.
- **Why -- the decisive point:** de-superposing the KEYS while the CONTEXT stays frozen-w2v breaks the context<->key
  match the readout depends on (the disentangled keys leave the frozen manifold the context words live on); and the
  shallow glass-box decomposition is too weak anyway (even bank.n.01 vs bank.n.09 stays cos 0.93). **JOINT
  re-representation of the word AND its context in one consistent space is exactly a trained contextual encoder = the
  invariant boundary.** A prior session's trained BiLSTM confirmed the boundary from the other side (0.293 < baseline
  at 41M scale; a transformer reaches 0.53).

So the ideal fix for the frozen-representation wall, prototyped WITHIN the invariant, is a located negative -- and
that IS the decisive result: there is no glass-box escape, so crossing REQUIRES the one component held off-limits
(joint contextual re-computation), now a fully-evidenced OWNER decision rather than a solver gap.

**AND THE FULLY-JOINT version, built on a LANDED organ, confirms it (`exp_atl_hubspoke_joint_ppr_recompute_v1`).**
The prior negative re-computed only the target with frozen context. The genuinely JOINT re-computation -- every
content word's senses settling together -- is spreading activation over a sense graph, and the substrate already has
that organ: `hdlab/grounded_semantic_graph` (personalized-PageRank over a 117k-node / 1.0M-edge WordNet++ graph =
relations+glosses+ConceptNet+SyntagNet; Kintsch/Waltz-Pollack C-I; the field's UKB WSD). Crucially it reads GRAPH
CONNECTIVITY, not w2v geometry -- the one signal NOT trapped in the frozen superposition. Measured on the same
population: PPR-alone a_s **0.264**, PPR+frequency-prior blend **0.088** (the prior is anti-subordinate), and PPR
FUSED with the w2v precision readout **0.323** -- ALL below the precision readout 0.342 (fuse CI-separated BELOW it),
though the fuse beats its shuffled-PPR twin (0.242 CI-sep, so PPR carries real signal). The signal is real but
TOPICAL -- graph connectivity reinforces the DOMINANT sense, reproducing the parent's C-I-over-topical-W result
(0.22) with the actual landed PPR organ. So joint settling over the best available sense graph is a located negative
for subordinate selection, for the same reason as every other route: the disambiguating cue is LOCAL and
sense-discriminative, and neither the frozen w2v NOR the WordNet++ graph carries it. This makes NINE converging
routes; the joint mechanism is built, reusable, and confirms the wall.

## AGGRESSIVE DRILL OF THE JOINT-PPR NEGATIVE (where the signal leaks, exactly; how the brain differs, precisely)

Four primary-source lanes + two decomposition cells (`exp_atl_hubspoke_ppr_signal_loss_v1`, `exp_atl_hubspoke_actr_ideal_chain_v1`).

**Where the signal leaks -- my leading hypothesis (PageRank degree-bias) was REFUTED, which sharpened the answer:**
- **Degree-bias is NOT the leak (refuted empirically).** corr(PPR activation, node in-degree) = **-0.002**,
  corr(activation, dominant prior) = 0.070, PPR picks the dominant only **14%** of the time; dividing PPR by the
  static PageRank (UKB's degree de-bias) is a **no-op** (0.264 -> 0.264). Reason (Agirre-Soroa-Stevenson 2010):
  degree-bias afflicts the STATIC context-free PageRank; the organ's `_sense_ppr` is already `ppr_w2w` (mass seeded
  in the CONTEXT words' senses, not the target) = the documented mitigation, so personalization already removed it.
- **The missing INTEGRATION phase is not the leak either.** Kintsch integration = A(t+1)=maxnorm(A.W) to the dominant
  eigenvector = a topical stationary distribution; parent 2 built it and it scored 0.22 (< raw PPR). Candidate-level
  sharpening is a no-op for argmax.
- **THE LEAK IS EDGE SEMANTICS.** WordNet++ edges are BOOLEAN topical relatedness ("robin->bird" == "chicken->bird"),
  so PPR settles on the sense most topically-connected to the context -- often neither dominant nor gold.

**How the brain differs, precisely (Collins-Loftus 1975; ACT-R Anderson-Reder 1999; CSC/Rodd 2005):** its edges carry
GRADED strength from USE-FREQUENCY (FAS/BAS asymmetry, cheddar->cheese 0.92 vs cheese->cheddar 0.05); activation is
ONE-STEP capacity-bounded (`A_i=B_i+Sum_j W_j S_ji`, `S_ji=S+ln P(i|j)`, `Sum W_j=1`, NOT iterated); and the control
network (LIFG/pMTG) AMPLIFIES weak-but-relevant / INHIBITS dominant-but-irrelevant, graded by associative weakness.
Weight, not topology, carries the discriminative signal.

**I ported that exactly -- the ACT-R IDEAL CHAIN is the best arm yet, but still short.** Directional
experience-weighted edges `S(s|w)=ln(P(s|w)/P(s))` (the /P(s) IS the CSC inhibit-dominant) + FAN-normalized specificity
`spec(w)=1/(1+ln(1+fan(w)))` (a word cueing FEW senses weighs more -- the fan effect = the precision mechanism,
grounded) + explicit amplify-weak, on the gold-resolved offline foundation (leave-one-doc-out, coverage 0.94):

| arm | a_s |
|---|---|
| w2v precision readout | 0.334 |
| earlier ideal-W (symmetric PPMI, gated) | 0.27 |
| ACT-R gated | 0.218 |
| ACT-R fused w/ precision | 0.309 |
| **ACT-R + amplify-weak (full ideal)** | **0.345** (beats its shuffled-edge twin 0.253 CI-sep) |

The mechanism-diff drove it MONOTONICALLY (0.218 -> 0.309 -> 0.345; +0.075 over the symmetric-PPMI version) --
**every ingredient the drill named is validated.** But 0.345 < 0.35 and is NOT CI-separated over the frozen-w2v
precision readout (delta +0.011, CI [-0.003,+0.026]). And this is with GOLD-resolved edges (the ideal foundation) --
so even perfectly-resolved experience-weighted edges are ZIPF-THIN for the rare sense (its discriminating
co-occurrences are the rarest), the same wall at the edge-weight level. The mechanism that would cross generalizes a
rare sense from FEW attestations instead of counting them = contextual re-computation (the invariant boundary).

**FINAL OPTIMIZATION -- reliability-weighted integration of ALL cues (`exp_atl_hubspoke_multicue_integration_v1`)
confirms the ceiling.** The brain integrates cues by reliability (Ernst-Banks 2002; Friston precision). Integrating
{w2v-precision, ACT-R discriminative-W, grounded-hub}, mix dev-calibrated on the disjoint train docs: best mix picked
precision=1.0, ACT-R-W=0.5, **grounded=0** (grounded adds nothing, as it lost alone), a_s **0.344** -- directionally
above the precision readout (+0.013) but NOT CI-separated (CI [-0.000,+0.026]), beats its shuffled twin (0.310
CI-sep), no MFS regression, does NOT cross 0.35. Every glass-box brain-foundational route AND their reliability-
weighted integration converge at **~0.344-0.345** -- the cues are correlated (all read the same local diagnostic
signal) and the residual is the Zipf/frozen-representation wall. The glass-box brain-foundational envelope is
exhausted at ~0.345; the only lever beyond is contextual re-computation (the invariant boundary).

## BRAIN COMPARISON + THE SIGNAL-LOSS LADDER (where signal is lost -> next focus)

Our best glass-box a_s = 0.336 (precision readout); competent-reader references: a transformer WSD reaches ~0.53 on
rare/subordinate senses (BEM LFS 52.6; the invariant boundary), non-transformer encoders cap 31-37%, human ~0.65.
Stage-by-stage, where OUR signal is lost and the EXACT mechanism-diff from the brain:

| stage | our implementation | our a_s | where signal is lost | EXACT brain difference | next focus |
|---|---|---|---|---|---|
| 1. WORD REP (upstream root) | ONE frozen sense-conflated w2v vector | -- | **THE DOMINANT LOSS** -- the rare sense is superposed onto its dominant twin (Arora 2018); every downstream stage inherits this blur | the brain RE-COMPUTES the word per context (predictive coding; distinct sense activation), so "bank(river)" != "bank(money)" | **JOINT contextual re-computation** -- the only escape. The shallow GLASS-BOX form (AutoExtend de-superposition) was PROTOTYPED and is a located negative (de-superposes keys but a_s drops 0.32->0.21 -- breaks the frozen-context match); joint word+context re-representation = a trained contextual encoder = the invariant boundary (owner decision) |
| 2. SENSE KEYS | rich atom (gloss+relations+SyntagNet) | 0.313 | minor -- keys are already separable (KEY-unwinnable 0.000) | grounded + contextually-distinct keys | not the bottleneck (grounding a located negative; de-superposed keys redundant) |
| 3. READOUT | precision-weighted biased competition | **0.336** | near-optimal for our keys | LIFG/pMTG controlled retrieval + Friston precision -- MATCHED | precision landed (+0.021 CI-sep); syntactic-argument-restricted query is the one glass-box lever left |
| 4. SENSE-DISCRIMINATIVE W | gold-resolved, max coverage + inheritance | 0.27-0.31 (hurts full-pop) | rare-sense Zipf-starvation + inheritance blur -- count-based knowledge cannot cover the rare sense | the brain GENERALIZES a rare sense from its contextual pattern (few-shot), not from many attestations | CLOSED -- count-based W is Zipf-bound; do NOT grow coverage (proven to hurt) |
| 5. DISCOURSE/SITUATION | document domain field | 0.334 (no gain) | topical on heterogeneous text -> reinforces the dominant | strong situational domain restricts to the appropriate sense (Vu-Kellas) | only helps with a strong subordinate-favoring domain (rare in natural text) |

**QUANTIFIED loss ledger (our 0.336 -> human ~0.65):**
- **0.336 -> ~0.35** (glass-box residual: syntactic-restricted precision, composition). ~+0.01, diminishing, within the invariant.
- **~0.35 -> 0.53** THE FROZEN-REPRESENTATION WALL. ~+0.18, the DOMINANT remaining loss. Recoverable ONLY by
  CONTEXTUAL RE-COMPUTATION of the word -- proven NOT recoverable by more/cleaner knowledge (the ideal-W chain hurts),
  NOR by grounding/exemplar/discourse. This is the owner's invariant decision (an offline contextual sense asset).
- **0.53 -> ~0.65** world-knowledge INFERENCE beyond the sentence. ~+0.12, a later problem.

**THE SINGLE DEEPEST DIVERGENCE (unchanged, now proven from every angle):** our representational substrate is a
FROZEN distributional space where senses are superposed; the brain's is contextually RE-COMPUTED, where senses are
DISTINCT. Every route that leaves the word frozen (grounding the keys, count-based W however clean or broad,
exemplars, discourse) inherits the blur and cannot separate the rare sense; the only crosser re-represents the word
per context. **Next focus, in order: (1) the offline contextual sense asset [the crosser, owner invariant decision];
(2) syntactic-argument-restricted precision query [the last glass-box lever within the invariant, ~+0.01]; (3) land
precision-weighting now.** Do NOT invest further in grounding, W-coverage growth, exemplars, or discourse -- all six
are measured located negatives converging on the frozen representation.

## LARGEST-OPPORTUNITY ATTACK: the query-side diagnostic-word identification (located precisely; attacked; a shortcut correctly rejected by the MFS guard)

Re-evaluating WHERE signal is lost on this harness (`exp_atl_hubspoke_signal_loss_ladder_v1`) located the largest
opportunity precisely, and it is NOT the frozen representation or Zipf -- it is QUERY-SIDE diagnostic-word ID:

| arm | a_s | note |
|---|---|---|
| full-bag (flat context) | 0.268 | topical blur |
| precision (diagnosticity) | 0.336 | our best realistic identifier |
| ACT-R fan-specificity | 0.299 | WORSE (wrong identifier) |
| **ORACLE_signed** (the context word that best separates gold from its dominant twin) | **0.627** | realistic-shaped ceiling |
| **ORACLE_single** (any one context word whose frozen w2v picks gold) | **0.868** | the cue IS in the frozen context 87% of the time |

So ~+0.29 (to 0.627) / +0.53 (to 0.868) is recoverable PURELY by identifying the diagnostic context word better --
no new representation, no new knowledge, the info is already in the frozen w2v context. This reproduces the parent's
0.85 on our harness and is the single biggest lever.

**Attacked it with the brain's CONTROLLED RETRIEVAL** (`exp_atl_hubspoke_controlled_retrieval[_gated]_v1`): the LIFG/pMTG
control network overrides the prepotent (dominant) response and seeks evidence for the weak/subordinate reading
(Thompson-Schill 1997; Badre-Wagner 2007; Rodd 2005 -- control recruited BY dominant/subordinate conflict). Gold-blind
signal: weight each context word by `precision(c) x relu(max_{s!=MFS} cos(c,key_s) - cos(c,key_MFS))` -- up-weight the
word that favors a NON-dominant sense. Result and the honest verdict:
- **Ungated, it CROSSES: a_s 0.382 CI-separated over precision [+0.038,+0.062], twin loses -- the first arm all session
  to cross 0.35.** BUT the **MFS guard FAILS** (it regresses the dominant population).
- **The MFS guard exposed it as a PRIOR SHIFT, not better diagnostic-word ID.** The anti-dominant signal cannot tell
  "context genuinely supports a subordinate sense" from "a dominant item with noisy context" -- that distinction IS the
  sense-discriminative knowledge the oracle used the gold label for. So it just moves mass off the dominant: helps the
  all-subordinate eval, hurts dominant items equally.
- **Gated to preserve MFS (tau tuned on the disjoint dev set), the gain VANISHES:** gated 0.336 == precision 0.338,
  ties its own twin, crosses-0.35 = False, MFS preserved. **BAR_PASS = False.** No free lunch.

**So the largest opportunity is real and precisely sized (query-side diagnostic-word ID, +0.29 to +0.53), but closing
it gold-blind requires knowing which non-dominant sense the context supports = the sense-discriminative signal, which
is exactly the Zipf/frozen-representation wall from the query side.** The anti-dominant prior-shift that appears to
cross 0.35 is correctly rejected by the MFS no-regression guard -- a clean example of the guard catching a
population-composition artifact, not a capability.

**KNOWLEDGE-INTEGRATION OPTIMIZATION (`exp_atl_hubspoke_knowledge_integration_v1`) -- an apparent PASS that a strict
control EXPOSED as transductive leakage.** Using all the substrate's sense-linked knowledge (WordNet gloss+examples,
SyntagNet, ConceptNet, gold-W) as a per-sense structured SIGNATURE and identifying the clincher by IDF-weighted
structured MEMBERSHIP (not topical cosine), fused with the precision cosine, first read as a clean PASS: a_s 0.360,
CI-sep over precision, twin loses, MFS IMPROVES 0.44->0.53, crosses 0.35. I SUSPECTED it and built the strict
inductive control -- and it was **transductive leakage**: the leave-one-DOCUMENT-out W pulled in OTHER odd (test)
documents' gold. With a strictly inductive W (EVEN/train docs only, disjoint from every test doc): fuse **0.261 <
precision 0.336** (CI-separated BELOW), BAR_PASS = False; the entire +0.099 was leakage (and dev-tuning saw dev items'
own gold -> dev_sub 0.85, the smoking gun). Under clean induction the knowledge-overlap channel HURTS (the train-only
W is Zipf-thin for held-out test senses -- the same wall). No knowledge integration crosses 0.35 inductively.

## RE-TRACE v2 WITH CHANCE CONTROLS -- the enabler is contextual re-representation, NOT knowledge; and I CORRECT my own ORACLE_single overclaim

Pressed on "if knowledge is not the enabler, what is," I re-traced the signal with chance controls
(`exp_atl_hubspoke_signal_trace_v2`) and ran a literature drill. Both converge, and both correct an earlier claim.

**CORRECTION (the disk over the swing): ORACLE_single 0.868 was ~72% combinatorics.** With a mean of 10.4 candidate
senses/item, chance that SOME context word argmaxes to a SPECIFIC sense is high: a RANDOM non-gold sense's
ORACLE_single = 0.717. So the gold ORACLE_single (0.867) is only +0.150 above random -- the "the disambiguating cue
is in the context 87% of the time" framing was inflated; most of it was luck. WITHDRAW the strong reading of that
number.

**What IS there: a thin-but-real per-token signal (representation-THINNED, not purely extraction-limited).** Per
context word, gold gets 21.2% of the argmax votes vs chance 16.5% vs a random non-gold sense 15.5% -- **+0.047 above
chance, +0.057 above random**; the signed context tilt toward gold over the dominant is **+0.004** (tiny, positive);
the signal concentrates only weakly in high-confidence words (0.227 vs 0.195). Knowledge-free aggregation
(plurality/margin vote) = 0.25-0.29, BELOW our precision readout 0.336 -- so we already extract the thin signal
better than naive voting, and the gold-blind extraction ceiling is only modestly above precision (~0.35, where the
ACT-R ideal chain sits). The signal is thin because each context word is itself a SENSE-CONFLATED static vector, so
its vote is blurred.

**THE ENABLER, stated plainly (literature drill `research_lfs_rare_sense_enabler_knowledge_vs_context_2026-09-04.md`):
CONTEXTUAL PER-OCCURRENCE RE-REPRESENTATION, not knowledge.** Field evidence: zero-knowledge frozen BERT beats MFS by
~20 F1 on rare senses; knowledge-graph pretraining WITHOUT a contextual base UNDERperforms plain frozen BERT (31.2 vs
37.0 LFS); knowledge adds real lift (+7-16) ONLY once a contextual base exists -- exactly reproducing this problem's
0.261-below-0.34 knowledge result. No verified static-embedding-only method beats MFS on rare senses anywhere. The
true bar is CONTEXTUAL, not TRANSFORMER (context2vec, a BiLSTM, beats MFS on LFS) -- but any contextual re-computation
is a trained encoder = the invariant boundary. Contextual re-representation is the enabler precisely because it
THICKENS the thin static signal: the token vector becomes sense-resolved, so the per-token diagnostic vote is no
longer blurred. Knowledge cannot substitute because it rides on the same thin static signal.

**Net corrected localization:** the static-embedding per-token signal is real but thin (+0.047 above chance); we
already extract near its gold-blind ceiling (~0.34-0.35); the remaining headroom (to ~0.53) is a REPRESENTATION gain
that only contextual re-representation delivers -- confirming, from a corrected and chance-controlled trace, that the
enabler is the frozen-representation fix (the invariant boundary), and that neither knowledge nor a better static
extractor closes it.

## THE ENCODER, RE-EXAMINED (owner: "does the brain use a trained encoder?" -- no; "modify the encoder to what downstream needs")

Two owner corrections closed this cleanly. (1) A batch-trained encoder is NOT brain-foundational and was abandoned:
I traced the prior encoders' failure to a real BUG -- the context2vec readout matched a 256-dim context-space query
to a 200-dim w2v gloss key (proven: matmul 200!=256 space/dimension mismatch), so it was near-random; context2vec's
NATIVE readout uses mean-context-vector sense keys IN THE SAME SPACE. Fixing that (`exp_atl_hubspoke_context2vec_aligned_v1`)
and scaling the self-supervised pretrain 40k->300k sentences moved a_s only 0.192->0.207 (coverage 0.99, so not a
coverage issue) -- it beats its structure-destroyed twin (real contextual signal) but stays below the static bag
0.265: a slow, scale-bound climb confirming a trained encoder needs transformer-scale (BERT 0.37 / BEM 0.53). Not
built further (not brain-faithful, and scale-bound).
(2) The reader ALREADY has a brain-faithful contextual re-representation -- the gestalt model's per-token `mu`
(`_gestalts_with_mu`). Decoded: the raw static target vector leans to the DOMINANT sense (gold-minus-dominant tilt
-0.019) but `mu` leans to the GOLD/subordinate sense (+0.012); `mu` beats the raw static target in the readout
(0.201 -> 0.275) and ADDS a real, non-leaky increment to the precision readout (0.3335 -> 0.3394; the shuffled-`mu`
twin drops to 0.266, so the signal is genuine, not leakage). So the substrate's online reader DOES re-represent the
token toward its context sense -- brain-faithfully, glass-box -- it is just WEAK (+0.012 tilt, +0.006 to the readout),
the same thin-signal ceiling as everything else on the frozen substrate. What the downstream needs is a STRONGER
gold-tilt; strengthening `mu` glass-box is the online predictive-coding learner accumulating re-representation over
much more reading (the learner-on / consolidation north star) -- which this problem's disambiguate-then-bind ladder
showed is Zipf-bound with a glass-box resolver (gold-resolved helps +0.03 on attested; glass-box resolvers do not).
So the encoder is real and brain-faithful; its sense-resolution is thin for the measured reason, and thickening it
is the online-experience north star, not a batch encoder.

## THE FULL BRAIN-FAITHFUL CHAIN, TRACED STAGE-BY-STAGE (where signal is lost -- the definitive ladder)

`exp_atl_hubspoke_full_chain_signal_trace_v1` assembles the whole chain as one ladder (subordinate a_s + the full
sub+dom population as the consumer no-regression guard); consolidation W is EVEN/train docs only (strictly inductive).

| rung (brain stage) | a_s subordinate | delta | a_s all (consumer guard) |
|---|---|---|---|
| R0 static input (frozen w2v) | 0.168 | -- | 0.415 |
| R1 read context (flat) | 0.214 | +0.046 | 0.301 |
| R2 hub-and-spoke keys (WordNet rel + SyntagNet) | 0.271 | +0.057 | 0.430 |
| **R3 controlled retrieval (precision biased competition)** | **0.340** | **+0.069** | 0.445 |
| R4 consolidated experience -- GLASS-BOX resolver | 0.321 | **-0.019** | 0.416 |
| R5 consolidated experience -- GOLD resolver (ceiling) | 0.331 | -0.009 vs R3 | 0.479 |
| R6 + reader `mu` re-representation | 0.341 | +0.011 | 0.469 |

**Where signal is lost, exactly:** the chain climbs steadily R0->R3 (reading context +0.046, hub-and-spoke keys
+0.057, controlled-retrieval precision +0.069 -- the biggest single gain) to **0.340**, then STALLS at the
CONSOLIDATION-OF-EXPERIENCE stage:
- R4 glass-box consolidation HURTS (-0.019) and is BELOW its own shuffled-W twin (0.332) -- the glass-box-resolved
  associates are WORSE than random for rare senses, because mis-resolution systematically binds dominant-sense
  associates onto the subordinate.
- Even the GOLD-resolution ceiling (R5) does not help subordinate (0.331 < R3 0.340): rare senses are Zipf-thin
  (~1-2 instances), so NO resolver can consolidate a strong rare-sense representation.
- The consumer guard shows the split precisely: gold consolidation IMPROVES the full population (a_s_all
  0.445->0.479 -- it helps well-attested/dominant senses) while glass-box consolidation REGRESSES it (0.445->0.416).
  So the online learner helps DOMINANT senses and cannot help -- and glass-box, actively harms -- the RARE ones.

**Verdict:** the full brain-faithful chain's rare-sense ceiling is ~0.34 at controlled retrieval (R3); the biggest
gain is the readout (controlled retrieval, brain-faithful, landable); and the signal is lost at the CONSOLIDATION
stage for Zipf-thin rare senses -- the online learner that should thicken the signal cannot get enough rare-sense
experience, and even a perfect resolver cannot manufacture it. This is the same wall, now localized on the assembled
chain with the consumer-guard split: consolidation is net-positive for the substrate's WSD OVERALL (gold +0.034
all-pop) and net-negative for it glass-box (Zipf mis-resolution) -- which is exactly why the sibling gates
reading-growth off by default.

## ORGAN CHECK -- do we have an organ that does contextual re-representation? (yes; all glass-box ones fail within the invariant)

Asked to check the organs for the enabler (contextual re-representation) and/or prototype a brain-faithful one, I
enumerated what the substrate already has:
- **FIVE self-built glass-box contextual encoders exist and ALL score BELOW the static baseline** (measured, on disk):
  context2vec BiLSTM 0.137, context_encoder v2 (masked-LM + gloss encoder, 15 epochs) 0.227, predictive_coding_encoder
  (error-drive + precision) 0.130, context_encoder_from_text 0.107 -- vs bag/diagnostic 0.28-0.34. Contextual
  re-representation is the enabler, but it realizes the gain ONLY at transformer scale (lit refs on disk: BERT-nogloss
  LFS ~0.37, BEM LFS 0.526); our within-invariant encoders are too weak to THICKEN the thin static signal -- they add
  noise and land below the bag. This is the invariant boundary, from five encoder directions.
- **`hdlab/predictive_reader.py`** is the brain-faithful FORWARD-predictor (selectional preference / thematic fit,
  Altmann-Kamide 1999, McRae 1998 -- the "online predictive" half the brief named; landed, owner-DONE, 8/8). But by its
  OWN landed caveat it predicts COARSE GROUNDED features and is "a graded-difficulty SIGNAL, not a standalone accuracy
  lift (ceiling'd by the grounded space)"; and it requires the predicate-argument structure (which verb governs the
  target) that the eval harness (context bags, no parse) does not provide.
- Other meaning organs (`distributional_meaning_channel` = substitutability only, actively BAD at general similarity;
  `iterative_attractor` = settling, over-collapses; `vsa_cleanup_memory`, `conceptual_meaning`, `meaning_fusion`) do
  not do per-occurrence contextual re-representation of the word.

**Verdict:** the organs for contextual re-representation EXIST and they CONFIRM it cannot be realized glass-box within
the invariant -- five encoders all fall below the static baseline (the enabler needs transformer scale = the boundary),
and the brain-faithful forward-predictor is grounded-coarse + parse-dependent (a difficulty signal, not an accuracy
lift). A sixth within-invariant encoder would be another sub-baseline variant; a predictive_reader WSD prototype is
grounded-ceiling'd AND parse-blocked on this harness. So there is no organ-backed, invariant-respecting prototype that
thickens the signal -- consistent with the re-trace (thin static signal) and the literature (only trained contextual
re-representation crosses).

## What I did NOT establish / would withdraw first

- The **precision-weighting +0.023** is the load-bearing positive; its CI lower bound is +0.012 and the exact
  dev-selected config (gamma vs top-k) jitters run-to-run (they tie ~0.334-0.336). If forced to withdraw one claim it
  is any *specific* config; the robust claim is "precision-weighting > launch pad CI-sep, twin loses, no MFS regression."
- The separability decomposition's grounded coverage is 0.477; the 80%-rescue is on the covered half. On the uncovered
  half grounding is silent (no evidence), which is part of why the hub loses overall.
- I did NOT build a broad-coverage sense-discriminative W (the proven crosser) -- it is the owner-DONE consolidation
  sibling and re-building it here would duplicate it. This problem's contribution is (a) closing the grounded route
  with a decomposed cause and (b) the precision-weighting readout refinement, which STACKS with any future W.

## KEY REALIZATIONS

- **Grounding separates the senses -- and that turned out to be the wrong thing to fix.** The move that unstuck the
  analysis was the separability decomposition: grounded cos(gold,dominant)=0.222 while w2v-gloss=0.799. Seeing that
  grounding DOES pull the senses apart, yet a_s does NOT improve, killed "enrich the keys" and pointed the whole
  problem at the query side -- exactly where the parent's oracle decomposition (100% query-side loss) already was.
- **"Located negative" did not mean "the brain mechanism failed."** The ATL grounded spoke works as advertised (it
  separates); the reader just cannot exploit key-separation when the loss is query-side and coverage is half. The
  honest negative is about the ARCHITECTURE PLACEMENT (grounding the keys), not the grounded signal.
- **The dominant-sense collapse is a biased-competition working-range problem, and precision is the fix the brain
  uses.** Plain reweighting (the wired readout, gamma=1) cannot overturn the topical majority that points at the
  dominant sense (Deco-Rolls narrow working range). Making the gain MULTIPLICATIVE and SHARP (gamma>1 / top-k --
  Friston precision) lets a few high-precision subordinate cues win. That is a one-line, brain-faithful refinement to
  the wired readout, and it is our only CI-separated gain.
- **THE STRICT INDUCTIVE CONTROL IS NON-NEGOTIABLE -- it caught two false PASSes.** Both the anti-dominant controlled
  retrieval (0.382, crossed 0.35) and the knowledge-integration fuse (0.360, crossed 0.35, MFS improved) read as
  clean PASSes until vetted: the first was a prior-shift the MFS guard caught, the second was transductive leakage a
  strict train-only W caught (0.360 leaked -> 0.261 clean). A leave-one-DOCUMENT-out W that includes OTHER test
  documents is transductive on the test population; the smoking gun was dev_sub 0.85 (dev items' own gold in the
  W). Always run: (a) the MFS no-regression guard, (b) a strictly inductive train-only foundation, (c) dev-tuning on
  a set disjoint from the foundation. The disk (adversarial recompute) outranks the swing.
- **The relational "spoke" is not a spoke.** Research corrected the brief: the canonical ATL hub has six perceptual/
  affect/verbal spokes and NO relational one; relational/sense-discriminative knowledge is a separate system. So the
  crosser (a sense-discriminative W) was never going to arrive as an ATL grounded spoke -- it is the consolidation/
  connection-matrix problem, which is why grounding the hub was destined to fall short.
- **THE MONOTONIC FIDELITY LADDER IS THE PROOF -- and it proved the owner's thesis in the contrapositive.** Building
  the whole upstream chain and varying ONLY the encoding sense-resolver showed the chain EXCELS iff that one
  component is correct (gold +0.030 CI-sep) and FAILS at every glass-box fidelity level (grounded even worse than
  distributional). "Every component must be brain-foundational" is exactly right -- and the ladder localizes the ONE
  component that cannot be made both brain-foundational and correct glass-box: the encoding resolver, trapped in the
  frozen sense-conflated representation. The move that made this legible was making the resolver the SOLE variable
  and reading the ladder, instead of reporting one combined number.
- **The wall is a FIXED POINT, not a missing trick.** To build the W that disambiguates you must first disambiguate;
  every glass-box resolver is trapped in the frozen w2v where the subordinate sense is superposed, so it mis-resolves
  the rare encounters to the dominant sense and contaminates its own W. Grounding cannot break it (too coarse for
  abstract regular polysemy); the bootstrap cannot break it (it re-resolves with the same trapped cues). The brain
  escapes by contextually RE-COMPUTING the word -- the one thing a frozen-vector substrate structurally cannot do
  without the invariant-boundary encoder.

## PROPOSED hdlab WIRE (strategy lands it, Q111, default-off, witnessed)

**Do NOT wire the grounded hub-and-spoke into the sense keys** -- measured null (concat-hub 0.283 < launch pad 0.313).
The load-bearing, landable positive is a **one-parameter refinement of the wired readout**:
- Add a **precision-sharpening** parameter to `hdlab/diagnostic_context_wsd` (`diagnostic_query`/`diagnostic_context_scores`):
  weight each context word by `diagnosticity ** gamma` (or keep only the top-k most-diagnostic), default `gamma=1.0`
  (byte-identical to today). Dev-selected `gamma≈2` / `top-k≈5` gives a_s 0.313->0.336 on 19c-style subordinate
  selection, CI-sep, twin losing, no MFS regression. Brain-faithful (Friston precision / Deco-Rolls). It STACKS with
  any future W improvement (it is a better *extractor* of whatever signal the keys carry).
- Keep the grounded spoke as a **candidate-restriction** option only where coverage is high (grounded-domain prune ties
  the launch pad; it does not hurt and it is the Vu-Kellas mechanism) -- but it is not a default-on win.
- The crosser remains the broad-coverage sense-discriminative W (owner-DONE `build_the_controlled_knowledge_growth_
  consolidation_gate_for_the_learner`): this problem hands it the confirmation that grounding is not a substitute for it.

## ADJACENT COMPONENTS (candidate next problems -- evaluated for brain-fidelity + leverage)

- **Sense-discriminative W coverage (the crosser).** Parent proved oracle-W -> 0.995, learned-W +0.059 on covered
  senses, bottleneck = 52% coverage. Brain-foundational status: the connection matrix of the AG/C-I system, learned +
  consolidated (owner-DONE sibling). HIGHEST leverage; the +0.06/covered-sense number is the target.
- **Syntactic/argument-restricted context (untested, brain-faithful, my top next-step).** The reader feeds the meaning
  system the target's dependency arguments; concentrating the diagnostic query on the syntactic neighbours (not the
  sentence bag) is a smarter precision signal than positional top-k, and the oracle-context ceiling (0.853) shows the
  headroom is there. Needs an offline parse of the eval sentences (admissible). Not built here -- flagged, not a silent gap.
- **`hdlab/diagnostic_context_wsd` precision parameter (this problem's wire).** OUR-INVENTION placeholder today
  (gamma=1 flat diagnosticity); the brain does precision-weighted (Friston) selective gain -- a fidelity upgrade with a
  measured +0.023.
- **The static distributional spoke itself.** Frozen 200-dim w2v; senses superposed (Arora 2018). Arora sparse-coding
  de-superposition is admissible (glass-box) but topic-grained (won't cross, P~0.15, research). The contextual
  re-representation route is the invariant boundary (transformer). No new brain-faithful de-superposition found.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)

- **The ATL grounded hub-and-spoke is NOT the meaning-channel crosser (measured, mechanism-faithful).** Binder-65 +
  Warriner, ATL-whitened, inheritance-propagated: concat-hub a_s 0.283 < launch pad 0.313. IMPORTANT nuance for the
  audit: grounding DOES separate the senses (grounded cos(gold,dom)=0.222 vs w2v-gloss 0.799; 80% rescue) -- the null
  is query-side + coverage (0.477), NOT the orthogonality premise. Downgrade "grounded spoke separates senses" from
  "ruled out" to "confirmed-but-not-exploitable-through-the-reader (key-separation is not the bottleneck)."
- **Correct the spoke enumeration:** canonical CSC spokes = Sound/Praxis/Valence/Vision/Function/Speech (Lambon-Ralph
  2017); there is NO relational ATL spoke -- relational/sense-discriminative knowledge is a separate system (AG /
  C-I W). PIN this; it explains why the crosser is the consolidation W, not a grounded spoke.
- **NEW readout finding to PIN:** precision-weighting (Friston selective gain, gamma>1/top-k) on the diagnostic readout
  beats the flat (gamma=1) wired readout +0.023 CI-sep, twin losing, no MFS regression. The wired
  `diagnostic_context_wsd` gamma=1 is an OUR-INVENTION placeholder for the brain's precision-weighted controlled
  retrieval; upgrade it. Settling == one-shot still holds (parent); the lever within the readout is precision, not iteration.
- **NEW upstream-chain finding to PIN (the monotonic fidelity ladder):** the sense-discriminative-W architecture
  (disambiguate-then-bind -> Hebbian W -> consolidation -> precision readout) EXCELS iff the encoding sense-resolver
  is correct (gold-resolved W +0.030 CI-sep on the attested subset), and FAILS at every glass-box resolver fidelity
  (distributional -0.004, grounded -0.028, grounded+precision -0.016, propose-and-verify bootstrap -0.012). PIN the
  localization: the LAST non-brain-foundational component is the encoding-time sense-resolver, which is a fixed point
  trapped in the frozen sense-conflated w2v (the subordinate sense is superposed, so any glass-box resolver
  mis-resolves rare encounters to the dominant sense and contaminates its own W). This is the mechanism-level reason
  the meaning channel cannot cross glass-box without contextual re-computation of the word (the invariant boundary).
  Grounding as an acquisition-circularity breaker is a located negative for abstract/regular polysemy (Copestake-Briscoe).
- **grounded_semantic_graph (PPR over WordNet++) is the JOINT settling organ, and it is TOPICAL for subordinate
  selection.** Tested on the a_s task: PPR-alone 0.264, PPR+w2v fuse 0.323 -- both < the precision readout 0.342
  (fuse beats its shuffled twin, so the graph signal is real but points to the DOMINANT sense). PIN: joint
  spreading-activation over the best available sense graph reinforces the dominant sense (graph connectivity is
  topical), reproducing the parent's C-I-over-topical-W result with the landed organ. The organ is correct for its
  wired job (all-words WSD / WiC via the frequency blend); it is a located negative for rare-sense a_s. The
  frequency-prior blend (`select_sense_blended`) is anti-subordinate by design (prior favors the dominant) -- do NOT
  use it for subordinate selection (a_s 0.088).

## TLDR (plain English)

To pick a word's rare meaning, the brief's idea was to describe each meaning by how it looks / feels / relates
(grounded "senses"), because those descriptions are independent of which words sit nearby and so should tell the rare
meaning apart from the common one. I built that, richly (65 brain-based feature ratings + emotion ratings, sharpened
and spread across the dictionary by inheriting features down word families). Two honest findings. First, the idea's
core claim is TRUE: the grounded descriptions really do pull the two meanings apart (they overlap 0.22 where the
plain word-neighbour descriptions overlap 0.80). But it does NOT improve the score, because separating the meanings
was never the hard part -- the hard part is spotting WHICH nearby words are the clue, and grounding does not help
with that, plus we only have grounded descriptions for about half the cases. Second, I found something that DOES
help: the brain, when it has to override a common meaning, cranks up the volume on the few most informative nearby
words instead of averaging them all -- and doing exactly that (a known brain mechanism) lifts the score a real,
statistically-clean notch (about +2 points), without hurting the easy common-meaning cases. It is not enough to
clear the target bar, though. The thing that clears it is a big, clean list of "which nearby words specifically
signal which meaning" -- and building that at scale is a separate, already-in-progress problem, not this one. Net:
the grounded-meaning route is honestly closed (with the reason), and I hand over a small, brain-faithful scoring
improvement that stacks with the real fix.

Then, as instructed, I built the WHOLE upstream chain the brain's way -- read text, figure out each word's meaning
as you go, attach the surrounding words to THAT meaning, keep what recurs -- with every stage made the brain's
actual mechanism, and measured it as a ladder. It gives a decisive answer. When the "figure out the meaning as you
go" step is done PERFECTLY (a human-labelled stand-in for a flawless reader), the whole chain WORKS and beats the
baseline for real (statistically clean). When that step is done by ANY automatic method we can build -- the
perception-based one, and even a bootstrapping one the brain uses when children learn words -- it FAILS, because that
step is forced to run on the same blurry fixed word-vectors where the rare meaning is smeared into the common one,
so it keeps guessing the common meaning and poisons everything downstream. So the proven bottom line is: the
architecture is right and excels the moment that last step is right, and the last step cannot be made right without
letting the reader RE-READ each word in its sentence to un-blur it -- exactly the one technique held off-limits (the
big pretrained-model route). That is the wall, named exactly, with every other component built and verified
brain-faithful.

## QUESTIONS

One decision that is genuinely the owner's, surfaced by building the full chain: the monotonic ladder shows the
architecture excels the instant the encoding sense-resolver is correct (gold +0.030 CI-sep), and proves the last
non-brain-foundational component is the FROZEN, non-recomputed word representation -- which the brain escapes ONLY
by contextually re-computing the word. The single glass-box route to that re-computation is a scale-trained
contextual encoder, which is THE invariant boundary (no transformer, no training). **So the honest question is not
"what else can we build" -- it is whether crossing 0.35 on the full population is worth relaxing the no-transformer
invariant for this ONE upstream asset (an offline-built contextual sense-vector table, still glass-box at
inference), or whether the substrate holds the invariant and accepts the ~0.34 glass-box ceiling here.** That is an
owner call, not a solver call. Grading judgement (same shape as the sibling contextual-ceiling problem): **PARTIAL**,
not "located-negative = FULL PASS", because I found a real CI-separated positive (precision-weighting), built the
full upstream chain the owner asked for, and localized the wall to one named component -- more than a clean route
closure.

## NEXT STEPS

1. **[LAND -- small, brain-faithful, stacks] the precision-weighting readout refinement** (gamma/top-k on
   `hdlab/diagnostic_context_wsd`, default-off, gamma=1 byte-identical). +0.021-0.023 CI-sep, twin losing, no MFS
   regression. It STACKS with any future W and is the one landable positive from this problem.
2. **[THE ARCHITECTURE IS PROVEN -- the blocker is the ENCODING RESOLVER] broad-coverage sense-discriminative W.**
   The chain works with a correct resolver (gold +0.030 CI-sep); the owner-DONE consolidation sibling owns W growth
   (+0.06/covered-sense, oracle-0.995). This problem hands it the proven fact that NO glass-box encoding resolver
   (grounded/distributional/bootstrap) builds a clean W on frozen w2v -- so W growth needs correctly-resolved
   exposure, which is coverage-of-correctly-resolved-senses, not more raw reading.
3. **[THE OWNER DECISION -- crossing needs it] an OFFLINE-built contextual sense-vector table** (re-computed word
   representations as a static asset, glass-box at inference) -- the only thing that un-traps the encoding resolver.
   This relaxes the no-transformer invariant for a FOUNDATION asset (FOUNDATION-IS-FREE-TO-BUILD) while keeping
   inference glass-box; flagged as the owner call in QUESTIONS, not built (invariant boundary).
4. **[MY TOP GLASS-BOX-COMPLIANT UNTESTED LEVER] syntactic/argument-restricted diagnostic context** -- concentrate
   precision on the target's dependency arguments (offline parse); the oracle-context 0.853 says headroom is there.
   A candidate follow-on within the invariant, not built here.
5. **DO NOT** wire the grounded hub into the sense keys (measured null), re-run 12-dim grounding, or grow W from a
   glass-box-resolved corpus expecting it to cross (proven contaminated by dominant-sense mis-resolution).
