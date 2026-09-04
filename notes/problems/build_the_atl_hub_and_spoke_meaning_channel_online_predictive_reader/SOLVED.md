---
problem: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader
status: PARTIAL
bar: "PASS = a glass-box ATL hub-and-spoke sense representation (distributional spoke bound with RICHER grounded spokes, semantic-inheritance-propagated to coverage) re-settled per context by the online predictive reader (NO transformer, NO training, NO external LLM), whose a_s on strict document-disjoint SemCor subordinate senses (through the wired diagnostic-context readout) CROSSES the 0.35 static-distributional ceiling CI-separated over the launch-pad 0.318, with a shuffled-grounding / shuffled-context info-free twin LOSING CI-separated and NO MFS regression. Report CI half-width + null p95; recompute floors on the item's own population. A rigorous located NEGATIVE -- richer grounded spokes at coverage STILL do not separate the superposed senses, with the named cause + number (e.g. the grounded spoke's own coverage/orthogonality ceiling) -- is a FULL PASS. Strategy lands the Q111 wire."
result: "PARTIAL = a LOCATED NEGATIVE on the brief's named mechanism (a FULL PASS by the bar) + a NEW brain-faithful directional POSITIVE, and the ceiling relocated with a number. (1) The RICHER grounded ATL hub-and-spoke does NOT cross: Binder-2016 65-dim + Warriner VAD, ATL distinctive-feature WHITENED, propagated to coverage by WordNet semantic inheritance, bound to the launch-pad distributional atom -- fed to the wired biased-competition readout, concat-hub a_s=0.283, which LOSES to the launch pad 0.313 CI-separated [-0.044,-0.015]; grounded-keys-alone 0.184; and the concat-hub beats its shuffled-grounding twin 0.162 CI-sep, so the grounded signal is REAL but insufficient. (2) THE SURPRISE THAT LOCATES THE CAUSE: the grounded keys DO separate the senses distribution merges -- w2v gloss keys of gold-vs-dominant cos=0.799 (superposed), grounded keys cos=0.222 (separated), and among the 1277 distribution-MERGED pairs grounding 'rescues' 80% (cos<0.5). So the brief's orthogonality premise HOLDS at the key level; grounding still does not help because (a) coverage is only 0.477 of test pairs and (b) the loss is QUERY-side selection, not key separability (the parent proved KEY-unwinnable=0.000). (3) THE REAL LEVER IS QUERY-SIDE AND BRAIN-FAITHFUL: precision-weighting (Friston selective gain -- gamma>1 / top-k on the diagnosticity, the multiplicative gain that lets a high-precision subordinate cue overturn the dominant prior) CROSSES the launch pad: a_s=0.3364 vs 0.3133, delta +0.0232 CI-sep [+0.012,+0.035], ci_hw 0.0112 = null_p95 0.0112, the shuffled-diagnosticity twin LOSES (0.271, delta +0.066 CI-sep), and it does NOT regress the dominant-sense/MFS population (all-items 0.420->0.435, +0.014). (4) BUT no glass-box readout/representation lever reaches the 0.35 ceiling (best 0.336<0.35; candidate-restriction-by-topic HURTS 0.304, distinctive-whitening the w2v keys is ill-conditioned 0.162): the crosser is a broad-coverage SENSE-DISCRIMINATIVE connection matrix W (parent proved oracle-W -> a_s 0.995; coverage-bound at 52%), which is the owner-DONE consolidation sibling's domain, NOT the ATL grounded hub. (5) THE FULL UPSTREAM BRAIN-FOUNDATIONAL CHAIN, BUILT AND MEASURED AS A MONOTONIC FIDELITY LADDER (grounded sense keys -> grounded/bootstrap ENCODING sense-resolver -> Hebbian bind-to-resolved-sense -> cross-situational consolidation -> precision-weighted W readout; every component the brain's actual computation, research-verified): the sense-discriminative-W ARCHITECTURE EXCELS when-and-only-when the encoding resolver is correct -- GOLD-resolved W beats base +0.0301 CI-separated on the gold-attested subset (a_s 0.338 vs 0.308; reproduces the parent's learned-W), while EVERY glass-box encoding resolver FAILS to build a clean W (distributional -0.004, grounded -0.028, grounded+precision -0.016, propose-and-verify bootstrap -0.012 -- none beats base). This LOCALIZES the single remaining non-brain-foundational component: the encoding-time sense-resolver, which is trapped in the FROZEN, non-recomputed sense-conflated w2v context representation (100% of the loss sits there; grounding never touches the context side). An independent literature drill converged on the identical localization. So the wall is a genuine fixed point: to build the W that would disambiguate, you must first disambiguate, and no glass-box cue breaks the circularity because the subordinate sense is inseparable in the frozen representation the brain replaces by contextual re-computation. All a_s: strict document-disjoint SemCor subordinate, subject-weighted, n=2676/2675, through the wired hdlab.diagnostic_context_wsd, glass-box, frozen 200-dim w2v, NO external LLM/transformer/training; gold used only as the diagnostic-context readout oracle at eval and as the idealized-resolver reference arm, never at inference."
floor: "launch-pad RICH-w2v diagnostic a_s = 0.3133 (this session, threads=1 deterministic; the parent's clean-foundation 0.318 reproduced first-hand); gloss-w2v floor = 0.2512 (parent 0.251 reproduced); the info-free twins: shuffled-diagnosticity 0.2707 and shuffled-grounding 0.1615 (both LOSE CI-separated to their arms). Every arm recomputed on its own population."
controls: "shuffled-GROUNDING twin (grounded keys permuted onto WRONG senses -> concat-hub beats it +0.122 CI-sep, so the grounded signal is real -- and yet the hub still loses to the launch pad, so grounding is real-but-insufficient); shuffled-DIAGNOSTICITY twin (precision gain applied to permuted/WRONG context words -> loses -0.066 CI-sep, so the precision win is the CORRECT diagnostic words, not the sharpening shape); SEPARABILITY DECOMPOSITION (grounded cos(gold,dominant)=0.222 vs w2v-gloss 0.799 -> EXCLUDES 'grounding cannot separate superposed senses'; localizes the null to query-side + 0.477 coverage, NOT key separability); MFS no-regression guard (all-items 0.420->0.435 +0.014 -> the precision gain does not hurt the dominant population); distributional candidate-restriction (0.304 < launch pad -> EXCLUDES 'prune-by-topic helps'; it reinforces the dominant sense, exactly the Deco-Rolls biased-competition narrow-working-range prediction); distinctive-whitening of the distributional keys (0.162, ill-conditioned over 200-dim -> EXCLUDES 'decorrelating the w2v atoms helps'); floors reproduced first-hand (gloss 0.251, launch pad 0.313). Paired 5000x bootstrap CI half-width + sign-flip null p95 on every contrast; each control excludes a distinct rival explanation."
files_changed: "experiments/exp_atl_hubspoke_grounded_separability_v1.py (the richer grounded ATL hub + separability decomposition), experiments/exp_atl_hubspoke_query_side_readout_v1.py (the query-side brain-faithful levers: precision-weighting, candidate-restriction, distinctive-whitening), experiments/exp_atl_hubspoke_grounded_disambiguate_then_bind_v1.py (the FULL upstream chain: grounded/bootstrap encoding resolver -> Hebbian W -> consolidation -> precision readout, as a monotonic brain-fidelity ladder), verification/test_atl_hubspoke_meaning_channel.py (8/8), notes/research_grounded_disambiguate_then_bind_2026-09-04.md (research verification), data/exp_atl_hubspoke_grounded_separability_v1/metrics_full.json, data/exp_atl_hubspoke_query_side_readout_v1/metrics_full.json, data/exp_atl_hubspoke_grounded_disambiguate_then_bind_v1/metrics_full.json"
reverify: ".venv/Scripts/python.exe verification/test_atl_hubspoke_meaning_channel.py   # 8/8 (W1-4 grounding-neg + precision-positive; W5-6 the upstream chain: gold-W excels, glass-box resolvers fail)"
---

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
| **GOLD (idealized brain resolver)** | **0.338** | 0.308 | **+0.030** | **YES** |

**The ladder is the proof, in both directions.** When the encoding resolver is CORRECT (gold -- the idealized brain
resolver), the fully-brain-foundational chain EXCELS: +0.030 CI-separated, reproducing the parent's learned-W and
pointing at the oracle-W 0.995 ceiling. When the resolver is any GLASS-BOX approximation, the chain FAILS -- and it
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
