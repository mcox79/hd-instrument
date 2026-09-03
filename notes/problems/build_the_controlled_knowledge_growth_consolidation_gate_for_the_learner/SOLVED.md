---
problem: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner
status: REFUTED
bar: "PASS = a glass-box consolidation gate (extract -> consolidate -> admit; persisted as a static asset, NO external LLM) such that admitting the CONSOLIDATED knowledge raises a_s CI-separated over gloss-only on strict document-disjoint SemCor (subordinate senses, the diagnostic-context readout), with the RAW-ungated twin LOSING CI-separated (it must regress, reproducing -0.015) and NO net regression over MFS. Report CI half-width + null p95; strict document-disjoint is MANDATORY. A rigorous located NEGATIVE -- no glass-box consolidation of reading-derived associations reaches curated quality, with the named ceiling + number -- is a FULL PASS."
result: "RIGOROUS LOCATED NEGATIVE (= the FULL PASS the bar names), now proven across EVERY glass-box lever incl. grounding. a_s on strict document-disjoint SemCor subordinate senses, diagnostic-context readout, n=2676. The consolidation gate CLEANS raw co-occurrence (raw-ungated 0.2183 -> gate 0.238-0.246, CI-separated; the RAW twin REGRESSES -0.033 below gloss, reproducing the parent; MFS no-regression guard PASSES 0.695>=0.683) BUT NO glass-box knowledge source beats gloss-only 0.2512: distributional reading co-occurrence climbs monotonically with syntagmatic tightness (sentence 0.238 -> window+discrim 0.246 -> REAL dependency-parse+discrim 0.251 = gloss, never above); perfect gold sense-ATTRIBUTION 0.232 (coverage-starved); top-k readout 0.218; and GROUNDING (the brain's named crosser, 12-dim Lancaster sensorimotor+concreteness via hdlab.grounded_similarity, biased-competition-fused, reliability-gated) 0.251-0.254, NOT CI-sep even on the grounded-SEPARABLE subset (0.246 vs 0.248). ONLY curated SyntagNet crosses (0.3024, +0.051 CI-sep) via non-glass-box manual concept-filtering. Loss LOCALIZED: attribution is NOT the leak (oracle ~= ours); the residual is association DISCRIMINATIVENESS (reading co-occurrence is topical, not sense-substitutable) + rare-sense Zipf-starvation + GROUNDING that our 12-dim asset is too coarse to realize (ideal = Binder 65-dim brain-based, only 535-word coverage). The growth ENGINE (hdlab.cls_growth) is proven safe (+0.110/6 rounds, drift-free); the binding constraint is admission QUALITY at the source, which no glass-box source meets."
floor: "gloss-only (WordNet definition+examples+lemma-names+hypernyms) a_s = 0.2512 (strongest floor actually run; the parent's pure-gloss L0 = 0.239). RAW-ungated reading-growth twin = 0.2183 (regresses -0.0329, CI-separated below gloss). Curated-SyntagNet CEILING = 0.3024 (+0.051 CI-sep over gloss)."
controls: "RAW-ungated twin (regresses -0.033 below gloss AND loses to the gate CI-sep -> raw is noise, gate removes it); shuffled-sense twin (associates to WRONG sense LOSES 0.236); shuffled-GROUNDING twin (grounded vectors permuted onto wrong senses -> fuse does NOT beat it, 0.251 vs 0.254 -> the grounded channel carries ~no net signal on this population); ORACLE gold sense-attribution (0.232, coverage-starved -> EXCLUDES 'our disambiguation is the leak'); curated-SyntagNet (0.302 +0.051 -> EXCLUDES 'knowledge cannot help through this readout'); MFS-quarantine vs plain recurrence (0.242 vs 0.218 -> discriminativeness lever real); top-k vs mean readout (top-k LOSES -> EXCLUDES 'readout is the fix'); syntagmatic-tightness ladder sentence->window->dependency (0.238->0.246->0.251 monotone-to-gloss -> EXCLUDES 'topical-bag is the only problem'); grounded STRATIFICATION by sense-separability (fails on BOTH the separable AND indistinct halves -> EXCLUDES 'grounding would work if we only applied it where senses differ'); MFS no-regression guard (blended overall 0.695>=MFS 0.683). Each control excludes a distinct rival explanation. Paired bootstrap CI half-width + sign-flip null p95 on every contrast."
files_changed: "experiments/exp_consolidation_gate_v1.py, experiments/exp_consolidation_gate_readbind_v1.py (disambiguate-then-bind; +window), experiments/exp_consolidation_signal_loss_trace_v1.py (oracle-attribution trace), experiments/exp_consolidation_discriminative_rescore_v1.py (MFS-quarantine), experiments/exp_consolidation_gate_syntactic_v1.py (dependency-parsed asset), experiments/exp_consolidation_grounded_v1.py (the grounded ceiling-crosser test), verification/test_consolidation_gate.py, data/exp_consolidation_gate_readbind_v1/metrics_s2353551_cap15.json, data/exp_consolidation_signal_loss_trace_v1/metrics_full.json, data/exp_consolidation_discriminative_rescore_v1/metrics_full.json, data/exp_consolidation_gate_syntactic_v1/metrics_p1000000.json, data/exp_consolidation_grounded_v1/metrics_full.json"
reverify: ".venv/Scripts/python.exe verification/test_consolidation_gate.py"
---

## What was asked, and what the disk says

The brief: build a glass-box consolidation gate that extracts syntagmatic associations from the reader's own
reading, CONSOLIDATES them (dedup / confidence-filter / cross-situational verify) to clean high-confidence
associations, and proves that admitting the CONSOLIDATED knowledge RAISES a_s CI-separated over gloss-only while
the RAW-ungated twin LOSES (regresses). The parent (`build_sg_lite...`) located the lever with numbers: through
the winning biased-competition diagnostic readout, gloss->rich = +0.081 CI-sep, but RAW organic growth REGRESSES
(-0.015), only CONSOLIDATED (SyntagNet-quality) helps.

**The disk says: the consolidation gate WORKS as a noise filter (it removes the raw regression), but no glass-box
consolidation of reading-derived co-occurrence reaches curated quality or even beats gloss-only. This is the
rigorous located NEGATIVE the bar explicitly calls a FULL PASS -- with the ceiling named and numbered, and the
loss localized to a specific, brain-grounded cause.** All numbers: strict document-disjoint SemCor (odd docs =
test), subordinate senses, subject-weighted a_s, n=2676, scored through the WIRED `hdlab/diagnostic_context_wsd`,
glass-box, frozen w2v, NO external LLM, gold used ONLY as a diagnostic oracle (never at inference).

## The measured result (strict doc-disjoint, n=2676)

| arm | a_s (mean readout) | what it is |
|---|---|---|
| gloss (WordNet def+hypernyms) | **0.2512** | the floor to beat |
| reading-derived, RAW ungated | 0.2183 | naive growth -> **REGRESSES -0.033** (reproduces the parent) |
| reading-derived + cross-situational recurrence consolidation | 0.2381 | gate cleans raw (**> RAW CI-sep**) |
| reading-derived + MFS-quarantine discrimination | **0.242** | +biased-competition filter, the best glass-box arm |
| ORACLE: perfect gold sense-attribution (even-doc SemCor) | 0.2318 | the ceiling *if disambiguation were perfect* (coverage-starved, 1.03 assoc/sense) |
| **curated SyntagNet** | **0.3024** (+0.051 CI-sep) | the clean ceiling |

The gate does exactly what a consolidation gate should: it turns the -0.033 raw regression into a CI-separated
improvement over raw (0.218 -> 0.242) and the RAW twin loses. But **the consolidated knowledge lands ~0.01 BELOW
gloss and 0.06 below curated** -- it recovers TO roughly gloss level (undoing the damage), not above it.

## How the brain does this, what we replicated, and WHERE we lose signal (two research drills + an oracle trace)

Two independent literature drills (precise neuroscience of lexical-semantic consolidation; the computational WSD
knowledge-source literature) CONVERGE on the same ledger, and an oracle-ablation trace localizes it quantitatively.

**The brain's effective mechanism (replicated operation-for-operation where we could):**
1. **Disambiguate at encoding, THEN bind** -- controlled/contextual retrieval (LIFG->pMTG/ATL; Jefferies 2013;
   Lambon-Ralph 2017) settles the sense BEFORE storage; the co-occurring context is Hebbian-bound to the
   ALREADY-disambiguated sense, never the word form. We replicated this (`exp_consolidation_gate_readbind_v1`:
   read -> disambiguate-in-context via the wired readout -> bind to the SELECTED sense).
2. **Cross-situational consolidation** (CLS; McClelland 1995 / Kumaran 2016; Yu & Smith 2007; propose-but-verify,
   Trueswell 2013) -- keep regularities that recur across situations, discard one-offs. Replicated (recurrence
   gate).
3. **Biased competition / schema-gating** (Tse 2007) -- keep schema-consistent, sense-discriminating associations.
   Replicated (MFS-quarantine: keep an associate only if the rare sense binds it MORE than its dominant competitor).
4. **Exemplar/best-match retrieval** (Nosofsky; Erk & Pado 2010; MaxSim > AvgSim, Reisinger & Mooney 2010) -- tested
   (top-k/exemplar readout) and it LOSES here (the diagnostic query already does the discrimination on the query side).

**The SIGNAL-LOSS LEDGER (quantified; worst first):**
1. **Association DISCRIMINATIVENESS -- the dominant glass-box leak.** Reading co-occurrence is TOPICAL /
   dominant-sense-biased, not sense-substitutable. Curated SyntagNet helps (+0.051) precisely because its edges are
   MANUALLY-resolved concept->concept syntagmatic pairs; ours are topical bags. MFS-quarantine recovers +0.024,
   confirming topicality IS the residual, but cannot manufacture discriminative pairs that co-occurrence lacks.
   *(Maru et al. 2019 SyntagNet; Camacho-Collados & Pilehvar 2018.)*
2. **Rare-sense Zipf-starvation.** Even perfect in-domain gold attribution yields ~1 associate/sense -- the
   discriminating contexts for rare senses are the rarest, so PPMI/recurrence has least evidence exactly where it is
   needed. *(Raganato 2017; Blevins & Zettlemoyer 2020: LFS is where distributional shortcuts fail.)*
3. **Attribution is NOT the leak (the surprising, load-bearing control).** Our imperfect disambiguation (0.242) ~=
   perfect gold attribution (0.232). Disambiguate-then-bind is necessary and correct, but not where signal is lost.
4. **The missing non-distributional ingredient: GROUNDING.** The brain individuates senses with overlapping or
   sparse linguistic context from sensorimotor/affective spokes (ATL hub; Patterson 2007; Binder & Desai 2011) -- a
   text-distributional signature has ZERO such dimensions, so those senses are inseparable IN PRINCIPLE from reading
   alone. This is the ceiling cause and it is not glass-box-distributionally reachable.
5. **Representation.** Under the diagnostic query, mean-pool beats top-k/exemplar here (measured), so the readout is
   not the recoverable lever.

## The syntagmatic-tightness lever, tested TWO ways (the last glass-box crossing)

SyntagNet's edges are syntactically-LINKED pairs; ours were whole-sentence topical bags. I tested the fix the
brain-faithful way -- disambiguate-then-bind, then restrict the BINDING to syntagmatic neighbours, then
cross-situational recurrence, then MFS-quarantine biased-competition (the 4-stage pipeline):
- **Window proxy (+/-3 content-word neighbours) + MFS-quarantine discrimination:** a_s **0.246** (best config
  ratio=2.0, K=3), and the windowed run's own recur+schema consolidation **0.247**. Both still BELOW gloss 0.251
  (sep=False, delta ~-0.005), the RAW-windowed twin regresses (0.236 < gloss), the shuffled twin loses, and the
  **MFS no-regression guard PASSES** (overall blended 0.695 >= MFS 0.683). So syntagmatic tightness inches the
  ceiling up (0.238 -> 0.247) but does not cross gloss.
- **Real dependency-parsed asset (offline spaCy; head + children of the disambiguated target) + MFS-quarantine:**
  `[IN FLIGHT -- exp_consolidation_gate_syntactic_v1.py, parsing 1M target sentences; the truest test. Every arm so
  far converges at 0.235-0.247, so this is the final confirmation, not expected to cross; if it DOES cross gloss
  CI-sep the verdict flips to PASS.]`

**What I did NOT establish, and would withdraw first if wrong:**
- The claim that ATTRIBUTION is not the leak rests on the oracle being coverage-starved (1.03 assoc/sense on
  even-doc SemCor). A large gold-tagged corpus could give perfect-attribution AND coverage; I could not build one
  glass-box. The full-corpus discriminative route (0.242-0.247, ~12 assoc/sense) triangulates the same ceiling from
  the opposite corner, which is why I hold the conclusion.
- The grounded result used a READOUT fusion; a grounded INPUT encoding (replacing the sense-conflated w2v) could
  do better and is the named successor -- I would withdraw "grounding does not help" if that richer integration
  crosses, but the 12-dim asset failing even on the grounded-separable subset makes me doubt the asset, not the fix.

## THE GROUNDED CEILING-CROSSER: TESTED (the located negative's named fix) -- and why it does not cross with the asset we have

The signal-loss trace named GROUNDING as the ceiling cause: reading co-occurrence is topical, and the brain
individuates senses from sensorimotor/affective spokes (ATL hub; Patterson 2007; Binder & Desai 2011). I BUILT and
tested that fix glass-box (`exp_consolidation_grounded_v1.py`) using the WIRED grounding organ
`hdlab/grounded_similarity` (12-dim Lancaster sensorimotor + Brysbaert concreteness, ~30k coverage):
- **Grounding DOES separate senses distribution cannot** -- a river-context grounded vector matches the river-bank
  sense centroid at **0.813** vs the money-bank sense at **-0.096** (the self-test asserts this). The mechanism is real.
- **But fused into the readout (biased competition in the grounded space + reliability-weighted precision gating), it
  does NOT beat gloss, at ANY available richness -- tested three ways:** base 12-dim 0.251; **affect-augmented 15-dim
  (+Warriner valence/arousal/dominance) 0.252 (filter+fuse 0.256);** ATL-whitened distinctive 0.250 -- all vs gloss
  0.251, NONE CI-separated (null p95 ~0.006-0.009). Affect adds a hair of real signal (0.252 > its shuffled twin
  0.246) but nowhere near a CI-separated crossing.
- **Stratifying by grounded-separability does not rescue it:** on the HIGH-separability (concrete-ish) half it is
  0.246 vs gloss 0.248; on the LOW half 0.255 vs 0.255. It fails on BOTH halves.
- **The specific reason (measured, not asserted):** (a) the glass-box grounding asset is too COARSE -- 12 sensorimotor
  dims; the ideal Binder 65-dim brain-based componential set covers only **535 words**; (b) SemCor subordinate senses
  are ABSTRACT/relational/verbal-dominated, where sensorimotor grounding is inherently uninformative; (c) gloss-derived
  sense centroids rarely capture the discriminative perceptual feature. So grounding is the RIGHT mechanism, REPLICATED
  and TESTED, and shown un-realizable WITH THIS ASSET for a specific reason -- the successor is a richer grounded INPUT
  representation, not a 12-dim norm lookup.

## HOW THE LEARNER GROWS THIS CAPABILITY OVER TIME, AND BUILDS THE CORPUS OPTIMALLY (the composed path)

The growth ARCHITECTURE is complete and its ENGINE is proven; the binding constraint is knowledge QUALITY at the source.
- **Growth engine (proven, safe):** `hdlab/cls_growth` -- keep-both ensemble (`make_ensemble_sim`, old store never
  discarded) + `rollback_gate` (accept a grown update only if corruption CI-upper < 0.15 on a frozen known-correct
  probe) + EMA slow-anchor (`align_and_fuse`, eta=0.1 = the consolidation rate). Measured **+0.110 held-out over 6
  reading rounds, corruption 0.116<0.15, drift-free** (`run_the_learner_on_live...`, SOLVED). The learner CAN grow
  knowledge over time without corrupting the old store.
- **"Optimally built up" operationally = the admission pipeline this problem supplies:** read -> DISAMBIGUATE at
  encoding (bind context to the SELECTED sense, never the word form) -> cross-situational RECURRENCE -> DISCRIMINATION
  filter (MFS-quarantine; grounded where the asset is informative) -> **ADMISSION-QUALITY GATE vs the gloss floor with
  the RAW-vs-consolidated regression check baked in** -> cls_growth keep-both + rollback + EMA anchor. Consistency
  cleanup lives on the EPISODIC is-a KB (schema-congruence needs supercritical density, AUC 0.88), NOT on the
  distributional meaning learner (schema-congruence is confirmation-biased there -- `turn_on_the_learner...`).
- **The measured truth:** the gate and engine are ready and safe, but EVERY glass-box knowledge SOURCE (reading
  co-occurrence, 12-dim grounding) fails the admission gate on this task -- the learner would grow safely but not
  beneficially from them. The source that passes (curated SyntagNet) uses non-glass-box manual filtering. So the corpus
  is "optimally built up" by this pipeline, but beneficial growth needs a SOURCE that clears gloss -- which points to
  the grounded-input build below.

## PROPOSED hdlab WIRE (strategy lands it, Q111, default-off, witnessed)

**Do NOT wire a knowledge-growth default-on.** The measured result is that reading-derived consolidated knowledge
does not beat gloss, so admitting it to the live sense signatures would not help (and raw growth HURTS). The
load-bearing wire is a **guard**, not a feature:
- Promote the consolidation gate as a REUSABLE offline asset-builder (`consolidate(reading_cooc) -> per-sense
  clean associates`) with the RAW-vs-consolidated contrast BAKED IN as a regression check, so any future
  learner-growth path is measured against gloss before admission and the raw regression can never silently ship.
- The gate composes with `hdlab/cls_growth` (keep-both + rollback) as the safety wrapper: cls_growth handles
  reversibility; this gate handles admission quality. Neither alone is sufficient; the measured lesson is that
  admission quality is the binding constraint and reading-derived co-occurrence does not meet it.
- Keep the diagnostic-context readout (`hdlab/diagnostic_context_wsd`) as-is; top-k did not help.

## KEY REALIZATIONS

- **The reversed order IS the regression.** The brain disambiguates BEFORE it stores; naive growth counts
  co-occurrence on the ambiguous FORM then never separates senses, so the dominant sense floods the rare one. Fixing
  the order (disambiguate-then-bind) was necessary but revealed the deeper truth below.
- **Attribution was a decoy; the leak is discriminativeness.** The move that unstuck the analysis was the oracle
  arm: giving the pipeline PERFECT gold sense-attribution and watching it STILL fail to beat gloss. That killed the
  "just disambiguate better" hypothesis and pointed at the real residual -- reading co-occurrence is topical, not
  sense-discriminative, and the ingredient that fixes it (SyntagNet's manual concept-pair filtering; the brain's
  grounding) is non-distributional.
- **A ceiling triangulated from two opposite routes is a real wall.** Perfect-attribution/tiny-coverage and
  imperfect-attribution/full-corpus+discrimination both land at ~0.242 -- the reading-derived ceiling, independent of
  the attribution/coverage tradeoff.
- **The brain's remaining mechanism, named not hand-waved:** grounding. Shown un-replicable from text co-occurrence
  with a specific reason (rare-sense discriminative signal is perceptual, not distributional) and a number (0.242 vs
  curated 0.302 vs gloss 0.251) -- which is the standard for claiming a wall rather than a convenience.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)

- Knowledge growth from reading is CONFIRMED as the biggest lever (curated +0.051 CI-sep) but is NEGATIVE if
  uncontrolled (raw -0.033) -- the consolidation gate removes the regression but does NOT reach curated quality
  glass-box. The consolidation organ's fidelity gap is NOT attribution (we replicate disambiguate-then-bind and it
  matches a gold oracle) -- it is (a) sense-DISCRIMINATIVE vs topical association (SyntagNet's manual filter) and
  (b) GROUNDING (non-distributional). Record the reading-derived ceiling a_s ~0.242 vs curated 0.302 vs gloss 0.251.
- diagnostic_context_wsd: top-k/exemplar key readout is a measured NEGATIVE under the diagnostic query (mean-pool
  wins); do not expect a top-k lift when the query is already biased-competition.
- grounded_similarity (12-dim Lancaster+Brysbaert): the grounding MECHANISM is confirmed (separates concrete
  homonyms 0.813 vs -0.096) but the ASSET is too coarse/abstract-blind to lift rare-sense a_s on SemCor (0.251 =
  gloss, fails even on the grounded-separable half). Fidelity gap: the ideal grounded space is Binder 65-dim
  brain-based (535-word coverage) or a grounded contextual encoder -- a richer grounded INPUT, not a norm lookup.
  cls_growth is the proven safe growth engine (+0.110/6 rounds); admission quality (not the engine) is the wall.

## TLDR (plain English)

The biggest way to help a model pick a word's rare meaning is to give it more world knowledge about which words go
with which meaning -- but if it learns that knowledge the naive way from reading, the score gets WORSE, because raw
word-neighbour statistics pile onto the COMMON meaning and drown the rare one. I built the clean-up gate the brain
uses: read, figure out which meaning is in play FIRST, then attach the surrounding words to THAT meaning, and keep
only the associations that recur and that actually distinguish the meaning. The gate WORKS as a clean-up step -- it
removes the damage that raw learning causes. But even cleaned, reading-derived knowledge does not beat the plain
dictionary definition, and stays well below a hand-curated knowledge base. I proved WHY, three ways: giving the
system PERFECT meaning-labels still didn't help (so bad labelling wasn't the problem); the rare meanings barely
appear in any text (so there's little to learn from); and the one thing that separates the hard cases -- what
things look, sound, and feel like (grounding) -- is how the brain does it. I even BUILT the grounding fix and it
cleanly separates clear cases (river-bank vs money-bank), but the ready-made grounding data we have is only 12
coarse "senses/feelings" numbers per word and most rare meanings are abstract, so it doesn't move the average.
So: the clean-up gate is a real, working safety filter and the safe growth-over-time engine is proven, but
"grow the knowledge from reading" is refuted as a glass-box way to beat the dictionary; the only thing that beats
it is hand-curated knowledge, and the real fix is RICHER grounded word-meanings (a build), not more reading.

## WHERE THE SIGNAL IS LOST (ranked, with numbers -- the map for further optimization)

All a_s on strict doc-disjoint SemCor subordinate, n=2676. gloss floor 0.251; curated ceiling 0.302 (+0.051).

| # | loss source | evidence (the number that proves it) | recoverable glass-box? |
|---|---|---|---|
| 1 | **Association DISCRIMINATIVENESS** (reading co-occurrence is topical/dominant-biased, not sense-substitutable) | curated 0.302 vs best reading-derived 0.251; MFS-quarantine recovers only 0.218->0.246 | PARTLY -- residual is SyntagNet's manual concept-filter (barred) |
| 2 | **Rare-sense Zipf-starvation** (discriminating contexts are the rarest; PPMI weakest where needed) | oracle PERFECT attribution yields ~1 assoc/sense, a_s 0.232 | NO -- intrinsic to corpus/sense frequency |
| 3 | **GROUNDING asset too COARSE for this population** (12-dim sensorimotor+concreteness; separates concrete homonyms 0.813 vs -0.096 but the eval is abstract-dominated) | grounded fuse 0.251-0.254 = gloss, fails even on the grounded-separable half (0.246 vs 0.248) | needs a RICHER grounded INPUT (Binder 65-dim brain-based; only 535-word coverage today) -- a build |
| 4 | ~~Attribution~~ (RULED OUT) | our disambiguation 0.242 ~= perfect gold 0.232 -- NOT a leak | n/a |
| 5 | ~~Readout representation~~ (RULED OUT) | top-k/exemplar LOSES under the diagnostic query (-0.03 to -0.06) | n/a |
| 6 | ~~Syntagmatic tightness~~ (RULED OUT, tested to the real dependency parse) | sentence 0.238 -> window 0.246 -> real dependency 0.251 = gloss, never above | inches up, does not cross |

## STEPS FOR FURTHER OPTIMIZATION (ordered, actionable -- what strategy should build next)

1. **THE ceiling-crosser: a RICHER GROUNDED INPUT representation** (attacks loss #1+#3, the shared upstream root).
   The 12-dim sensorimotor+concreteness asset is too coarse and abstract-blind (tested: fails even on the
   grounded-separable half); build/adopt a Binder-class 65-dim brain-based componential space at BROAD coverage
   (or a grounded contextual encoder) and inject it as the sense REPRESENTATION, not a 12-dim readout-fusion. This is
   the meaning-channel north star; a separate, larger problem, but the highest-value next build and the located cause.
2. **The growth ENGINE + admission GATE are ready to compose:** this problem supplies the admission-quality gate
   (disambiguate-then-bind -> recurrence -> discrimination -> raw-vs-consolidated regression check); `hdlab/cls_growth`
   supplies safe reversible growth (+0.110/6 rounds, drift-free). Once a SOURCE that clears gloss exists (step 1), this
   pipeline grows it over time optimally. Consistency cleanup goes on the EPISODIC KB, not the meaning learner.
3. **Contextual input encoder (the parent's fork)** -- crosses to ~0.53 (BEM-class) but is the transformer/invariant
   boundary; an OWNER decision, not a near-term glass-box lever. Loss #2 (coverage) is helped by more reading but is
   secondary (the parent showed knowledge saturates ~40M tokens).
4. **DO NOT wire reading-derived knowledge growth default-on** -- it does not beat gloss and raw growth HURTS. Wire
   the gate as a REGRESSION-GUARD (raw-vs-consolidated contrast baked in) composing with `hdlab/cls_growth`
   (reversibility) -- admission quality is the binding constraint, and no glass-box source (reading OR 12-dim grounding)
   meets it.

## QUESTIONS

None blocking. The verdict is settled: every glass-box lever (distributional to the real dependency parse, oracle
attribution, discrimination, readout, AND 12-dim grounding) lands at/below gloss 0.251; only curated SyntagNet (0.302)
crosses. One judgment for the owner: whether to fund the richer grounded-INPUT build (step 1) as the actual
ceiling-crosser, since the mechanism (grounding) is confirmed right but the available asset is too coarse.

## NEXT STEPS

See STEPS FOR FURTHER OPTIMIZATION above (ordered). Headline: reading-derived knowledge growth is REFUTED as a
glass-box way to beat gloss (located negative PROVEN across every lever incl. grounding; ceiling 0.251 vs gloss 0.251
vs curated 0.302); the gate WORKS as a raw-noise filter and composes with the proven cls_growth engine; the real
ceiling-crosser is a RICHER GROUNDED INPUT (Binder-class, broad coverage), not more reading and not the 12-dim norms.
