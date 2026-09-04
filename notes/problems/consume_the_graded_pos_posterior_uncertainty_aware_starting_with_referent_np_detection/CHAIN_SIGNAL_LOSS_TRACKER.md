# Who-did-what chain: signal-loss TRACKER (build the dorsal triad brain-foundationally, track loss until optimized)

Owner directive (2026-09-04): "do it now - all of them truly brain foundational and track where we lose signal
along the entire chain until this is optimized." This is the living tracker. Instrument = the role-balanced
non-canonical gold (`aligned_gold.jsonl`), PATIENT span, **cleaned of gold noise first** (mislabeled intransitive-
subject / cross-clause -- otherwise the ruler dominates). Harness: `experiments/exp_whodidwhat_brain_chain_v1.py`.
Stage 4 is REUSED verbatim (`hdlab.graded_role_assigner`, already brain-faithful); Stages 6+7 prototyped here.

## ITERATION 1 (2026-09-04) -- the ladder, cleaned pre-verbal (non-canonical) n=3483, 561 gold-noise removed

| rung | brain stage | patient acc (non-canon) | recovery | canonical (net-pos) |
|---|---|---|---|---|
| FLOOR | Stage 1 positional (nearest post-verbal) | 0.6365 | -- | 0.8995 |
| +S4 | Stage 4 algorithmic OVERRIDE (voice/word-order; Competition Model) | **0.6612** | **+0.0247 CI-sep** | 0.8991 (neutral) |
| +S6 | Stage 6 clause segmentation (marker-based WM window) | 0.6595 | -0.0017 n.s. | 0.8998 |
| +S7 | Stage 7 reanalysis (P600 cross-clause re-bind) | 0.6629 | +0.0034 CI-sep on non-canon BUT | 0.894 (**-0.0055**) |
| ceiling | Stage 3 candidate coverage (patient IS a candidate) | **0.9842** | residual **+0.32** | 0.944 |

**Reading:** candidate coverage is near-perfect (0.98) -- the loss is SELECTION. The built dorsal override
(Stage 4) recovers +0.0247 CI-separated and is CANONICAL-SAFE -- this is the deployable win (and it is DEFAULT-OFF
in the live reader; wiring it is the single highest-value live action). Stage 6 (marker clause-seg) is neutral
because the HARD cases -- reduced relatives -- have NO clause marker to segment on. Stage 7 (reanalysis) recovers
real non-canonical signal but at a precision cost on canonical -> **net-negative overall**: surface-cue revision
cannot reach the precision the brain's P600 revision needs -- this is the brain's own IMPERFECT/lingering revision
(Christianson 2001), and a clean Stage 7 needs a real conflict-detector (parse/meaning), not surface heuristics.

## WHERE SIGNAL IS STILL LOST after the built chain (residual miss attribution, n_miss on cleaned non-canon)

| bucket | n | brain stage it needs | note |
|---|---|---|---|
| **S5_thematic_fit_or_metric** | **482** | **Stage 5 (MEANING / grounding) or the ruler** | a post-verbal nominal exists but gold patient is pre -> needs world-knowledge to override word order, OR is a metric artifact. THE BIGGEST residual. |
| S4_voice_missed | 424 | Stage 4 refinement | voice/passive cue present but the override still mis-picks -> improve the Competition Model's voice precision |
| S6_clause_or_gap | 220 | Stage 6 (real clause structure) | object-gap/clause cases the marker segmenter misses (reduced relatives) |
| S4_unaccusative | 34 | Stage 4 (unaccusative cue) | sole-theme change-of-state verbs |
| S7_reduced_relative | 9 | Stage 7 (reanalysis) | genuine garden-paths -- small count |

## THE TRACKED CONCLUSION (iteration 1)

1. **On canonical prose we are at the human ceiling (0.90-0.98) and POS/parse recover nothing** -- faithful.
2. **The one clean, net-safe, brain-faithful WIN is Stage 4 (the algorithmic override), +0.0247 CI-sep, and it
   is DEFAULT-OFF.** Wiring the Competition Model live is the highest-value action. (Overlaps the concurrent
   non-canonical / graded-parsing briefs -- hand-off, not a drop-in.)
3. **The largest REMAINING signal loss is Stage 5 -- MEANING / thematic-fit (the grounding wall)** (482 of the
   residual) -- the same wall every prior finding on this substrate hit. Structural dorsal fixes (4/6/7) plateau
   at ~+0.03 on non-canonical; the rest is world-knowledge re-ranking, which is the project's central unsolved
   problem (typed grounding).
4. **A faithful reanalysis (Stage 7) needs a real conflict-detector, not surface cues** -- the brain's revision
   is precise and still imperfect; ours is net-negative until it can consult structure/meaning.

**Next rungs (to keep tracking until optimized):** (a) wire Stage 4 live + measure on the live reader;
(b) Stage 5 = the typed-grounding meaning organ (the wall -- consult event/world knowledge to re-rank when word
order and voice are silent); (c) Stage 6 real (non-marker) clause structure for reduced relatives; (d) fix the
ruler so gains are visible. Signal is NOT lost in POS/parse/candidates -- it is lost in SELECTION, and after the
dorsal override the residual is MEANING.

## ITERATION 2 (2026-09-04) -- BUILD Stage 5 (meaning / thematic fit) and track it

Stage 5 = generalized event knowledge / verb selectional preference (McRae role-filler distributions; Elman 2009;
eADM), REUSING the landed brain-faithful organ `hdlab.verb_role_exemplar_selector` (nearest-grounded-exemplar over
a verb's attested OBJ fillers -- an INSTANCE distribution, glass-box offline store, NO LLM). Integrated the
brain-faithful way: as a COMPETING CUE with a LEARNED validity in the Competition Model (cue-competition down-weights
it where noisy), not a hard override -- because a probe showed the pure thematic-fit selector picks 0.42 < floor 0.60
on this SCIENCE gold. Harness: `experiments/exp_whodidwhat_stage5_thematic_fit_v1.py`.

| variant | non-canonical (pre_clean, n=1681) | canonical (post, n=2093) |
|---|---|---|
| base (Competition-Model cues) | 0.6669 | 0.8782 |
| + Stage 5 thematic-fit cue | **0.6669 (+0.0000)** | 0.8743 (-0.0038) |
| + Stage 5 VERB-SHUFFLED twin | **0.6669** | -- |

**Stage 5 is a COMPLETE NO-OP on this gold, AND ties its verb-shuffled twin EXACTLY (fit-twin = +0.0000).** The
logistic still WANTS the cue (learned validity ~0.97-1.92) but its VALUES carry no signal -- a RANDOM verb's fillers
do as well. This is the organ's own documented caveat, reproduced at scale: **who-did-what thematic fit is bounded
by DOMAIN MATCH of the event-knowledge store.** The store is modern web text; the gold is science/expository = OUT OF
DOMAIN. IN-domain (modern prose) the same organ recovers **+0.102 CI-sep with the twin LOSING** (landed
`the_plausibility_prior_is_a_coarse_centroid...`, p5). So the MECHANISM is right and built; the WALL is a
domain-matched (register-native) event-knowledge store -- a FOUNDATION/corpus problem, not a role-mechanism defect.

## THE TRACKED ENDPOINT (iterations 1+2) -- where the signal is lost, along the ENTIRE chain

1. **POS / parse / candidate coverage: NOT the loss** (we match the brain; gold-POS/parse recover nothing; candidate ceiling 0.98).
2. **Stage 4 (algorithmic override): the one clean built WIN, +0.0247 CI-sep, canonical-safe, DEFAULT-OFF -> wire it.**
3. **Stage 6 (clause seg): neutral** (reduced relatives have no marker). **Stage 7 (reanalysis): net-negative** (surface cues can't hit the brain's revision precision -- the imperfect-revision reality).
4. **Stage 5 (MEANING): the right mechanism, BUILT, but DOMAIN-BOUND -- null on OOD (ties its twin), +0.102 in-domain.**
   The residual meaning loss is a **DOMAIN-MATCHED EVENT-KNOWLEDGE FOUNDATION** problem (register-native selectional
   preferences) + the metric -- i.e. the project's central `clean foundation / domain-match` wall, reached again from
   the who-did-what side. **The chain is optimized as far as the structural stages + available event knowledge allow;
   the remaining loss is a FOUNDATION problem (a register-native selectional store), not another dorsal heuristic.**
