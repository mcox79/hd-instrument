# LONG-TERM PLAN — how this substrate gets to real comprehension

**Written 2026-08-16 by the Director.** Living document; edit in place.
Companions: `notes/STATUS.md` (where we are, injected every session) -> `notes/PLAN.md` (the near-term
backlog) -> THIS FILE (why the backlog is shaped the way it is) -> `notes/ORGAN_MAP.md` (per-organ detail).

Written to be read by a session with no memory of the night that produced it, and by a non-specialist
owner. Plain language first, numbers second.

---

## 1. THE GOAL, UNCHANGED

A glass-box substrate that learns what words mean by reading, and reasons over that knowledge **with no
external language model at inference**. An LLM may build a static seed offline. Nothing calls one at
runtime. That is THE invariant; a design that violates it is disqualified regardless of its score.

The brain is the existence proof. It learns word meanings from far less text than we have, so a shortfall
is never a ceiling until both gates pass: the test was fair, AND we did it the way the brain does.

---

## 2. WHAT WE ACTUALLY KNOW (2026-08-16, all measured, all floored)

This section is the foundation of everything below. Re-verify before quoting; every one of these was
wrong at least once.

| # | component | state | evidence |
|---|---|---|---|
| 1 | word encoding | live encoder is a **spelling hash** -- the structure-axis null BY CONSTRUCTION | `542e1fc0d` |
| 2 | meaning assets | built, unwired, and **do not clear the floor** CI-separated | `84b8f00d5` |
| 3 | storage | shipped store applies **no key at all** (`acc += symbol_vector(w)`) | runtime reconstruction |
| 4 | retrieval | **FINE** -- ties a spell-checker, CIs not separable | 55.65% vs 54.55% |
| 5 | selection | **FAILS** -- 1.85x worse than spelling, CI-separated | 8.63% vs 15.95% |
| 6 | instruments | encoding instrument VALIDATED 21/21; storage instrument blocked on a falsified premise | `542e1fc0d` |

**THE FLOOR THAT GOVERNS EVERYTHING -- AND IT IS NOT SPELLING. [ADDED 2026-08-16; this supersedes the
framing every earlier section of this plan was written under.]**

A **CONSTANT RANKING THAT USES ZERO INFORMATION ABOUT THE QUERY** -- cosine to the mean anchor
direction, i.e. the same answer for every question -- scores **hit@1 0.1390 / 0.1518**. It beats the
spelling channel by **+0.0523 [+0.0391,+0.0658]** and **+0.0627 [+0.0475,+0.0778]**, CI-separated
(`sparsify-right-object.json`).

**Consequence: every arm tested to date, our dense read-out, AND the spelling floor itself are all
CI-separated BELOW a baseline that knows nothing at all.** The long-quoted "spelling 8.70% beats us
4.80%" is a comparison between two channels that BOTH lose to a constant. Nobody had ever run it.

**Two readings, and they need different responses. Do not collapse them.**
1. **OUR FLOORS WERE TOO WEAK.** The standing bar's `max(orthographic, frequency, scramble)` never
   included a prototype/popularity-shaped floor, so it under-set the bar everywhere. Fix: add the
   CONSTANT/PROTOTYPE arm as a required fourth floor and re-run the bar over the corpus.
2. **THE TASK MAY BE DEGENERATE.** If a constant answer wins, hit@1 on this pool may be dominated by
   prototypicality rather than by comprehension -- in which case the metric cannot show comprehension no
   matter what we build, and the read-out task itself needs redesigning. Corroborating: pure corpus
   popularity alone reaches top-50 **0.5235 [0.5078,0.5388]** against our 0.5566.
   **These are distinguishable by measurement and that measurement is the top priority.**

**THE ONE SURVIVOR, and it is the only encouraging number in this section:** the grounded asset adds
information a spell-checker does not -- **+0.0168 to +0.0274 above fuse(context, spelling)**, replicated
in all four blocks and under a calibration-invariant rank fusion. Small, real, and still below the
constant guess.

**THE STATISTIC THAT DEFINES WHAT OUR STORE ACTUALLY IS (2026-08-16, `b84417941`):**
**Only 0.46% of a word's top-20 neighbours in our store are its synonyms.** Our store is a
co-occurrence bag, and co-occurrence neighbours are not meaning neighbours. This single number explains
a long run of nulls: any mechanism that reinforces, re-weights, completes from, or replays the store's
own neighbourhoods is operating on a set that is 99.5% wrong.

Proof that the defect is the NEIGHBOURHOODS and not the clumping: Hebbian replay of the store's own
geometry reaches the owner's clumping target (synonym cosine 0.1214 -> **0.4705**) and buys **NOTHING** --
channel NOT_SEPARATED at every dose, reading cue CI-separated BELOW, ratio to frequency-matched
non-synonyms falling monotonically 1.239 -> 1.118, participation ratio collapsing 171 -> 31, and an
isotropic control reaching cosine 0.99 with the channel going DOWN. **Free clumping is worth less than
nothing.**

**What DID work, and it is the template:** consolidating against the THEMATIC RELATION GRAPH (our own
simplewiki extraction -- no WordNet, no LLM, no pretrained table) raises replay-partner synonym purity
**4.4x**, lifts the channel 0.2417 -> 0.2795 and **more than doubles the open-vocabulary read-out
0.0462 -> 0.1069**, clearing all four matched controls (shuffled profiles, frequency-matched partners,
first-order, random store neighbours) CI-separated on both instruments -- and confirming a PRE-WRITTEN
prediction that the pull would be second-order. **Still short:** the constant/prototype floor is 0.2070
against our 0.1069, CI-separated ABOVE us; the reading cue falls -0.0083; spelling is a tie only under
the honest tie convention. A second channel of the RIGHT KIND is the lever. More stirring is not.

**Superseded but retained for the record:** at 20% cue overlap spelling gets recall 0.6536 / rank 24
against our best addressed arm's 0.2380 / rank 330. Also note the REGIME effect, which is the real
retrieval damage: top-50 falls 0.5566 (exact key) -> **0.3758 (partial cue)**, CI-separated below both
spelling and pure popularity. And the tie convention runs the OTHER way from an earlier draft of this
file: under the conservative convention WE are above spelling +0.0641 [+0.0456,+0.0829], because the
15.27% tie mass is the FLOOR's and ours is 0.0%.

**Three architectural facts earned tonight, each expensive:**
- **Role-keys survive a partial cue; conjunctive keys collapse.** At 20% overlap conjunctive addressing is
  CI-separated BELOW the flat bag (-0.0247); per-spoke role addressing is not separated (-0.0007). The
  hub-and-spoke shape is viable. It does not yet WIN.
- **Adding an address to the real read-out made it worse** (`STRUCTURE_HURTS`, -0.01125 CI
  [-0.01950,-0.00300], both known-answer arms clearing 0.70). Structure is not an unconnected fix waiting
  to be plugged in. It was connected, and it lost.
- **The norms are the only meaning asset that GENERALISES.** Off the frequent vocabulary they hold
  (0.2701 -> 0.2289, drop not separated) while every learned encoder collapses CI-separated. A pretrained
  table clears the floor easily (+0.3511, p=0.0005), which proves the RULER works and our ASSETS are weak.

---

## 3. THE DIAGNOSIS — why every architectural fix has measured null

Six months of interventions on retrieval, selection, re-weighting, re-scoring, coherence and capacity all
measured null or negative. That is not six months of bad luck; it is a signature.

**You cannot route meaning that was never supplied.** Retrieval already finds the right neighbourhood as
well as spelling does. Selection then fails -- but selection is being asked to choose between candidates
whose codes carry no meaning to choose ON. Every downstream fix is a better filing system for empty
folders.

**Corollary, and it sets the whole plan's order:** SUPPLY BEFORE ARCHITECTURE. Until a word's code
carries meaning that clears the strongest floor, no storage, completion or selection change can be
evaluated -- a null there is uninterpretable, because it is what you would see either way.

**The counter-argument, kept honest:** it is possible meaning is present but destroyed downstream. We
tested that tonight and it is not the current bottleneck -- bundling 2-3 spokes costs ~nothing, and the
arms that survive bundling best are precisely the ones with no structure signal. The loss is not the
issue while there is nothing to lose.

---

## 4. HOW THE BRAIN DOES IT — the architecture we are copying

Stated per structure, with each claim marked PINNED (evidence) or OURS (invention under test). Per the
standing gate (`3e70c3ba4`), presenting invention as pinned is barred.

**Word form and word meaning are SEPARATE systems.** [PINNED] A spelling-derived code is a FORM code. We
called ours a meaning code for months. Our hub-and-spoke word keeps them in separate addressed slots,
which is the fix.

**Meaning is distributed across modality spokes, bound by an anterior-temporal hub.** [PINNED] Damage the
hub and meaning fails across the board; damage a spoke and one facet is lost. Each spoke keeps its OWN
address. Our single flat sum was a hub with no spokes.

**Coding is SPARSE, and conjunctive rather than featural.** [PINNED for cortex/MTL] Perirhinal cortex
exists to separate items that SHARE features. **[OURS]** The specific conjunction operator is unpinned --
the literature does not fix an algebraic form, and feature-ambiguity has real failed replications. Ours
is invention under test, and the version we tried lost.

**Retrieval is COMPLETION FROM A PARTIAL CUE, never exact-key lookup.** [PINNED] CA3 is a recurrent
auto-associative network; dentate-gyrus separation and CA3 completion are a matched pair. We built
separators with no completer -- which is exactly why orthogonalising keys destroyed the partial-overlap
channel that carried all our signal. **[OURS]** Our completer implementation is refuted at smoke, with a
handicap we introduced (one spoke had 1,476 distinct codes for 4,096 words) and a fair re-test pending.

**Meaning is grounded AND distributional. Both are real brain mechanisms.**
**[CORRECTED 2026-08-16 -- an earlier draft of this file had this wrong, and the error was load-bearing.]**
The earlier claim was "the brain does not learn meaning from co-occurrence statistics", marked PINNED. That
is FALSE as stated. **Congenitally blind adults acquire the STRUCTURE of colour -- which colours are
similar, how they relate -- from language alone, having never seen any.** [PINNED] So distributional
learning is a genuine mechanism the brain uses, not a shortcut we refuse on principle. Sensorimotor
grounding [PINNED] and distributional structure [PINNED] are complementary, not rivals.

**THE OWNER HAS OVERRULED THE "CEILING REFERENCE ONLY" RECOMMENDATION (Q3, 2026-08-16). The bar on
pretrained tables AS FOUNDATION IS LIFTED.** Their reasoning, verbatim:

> "We can build a foundation in whatever way is most efficient. the brain began with hundreds of
> millions of years of evolution instilling a foundation. we can build that foundation however we want,
> as long as it is a strong foundation, and the operation is not llm"

**This is the stronger brain argument and it corrects mine.** I had reasoned that adopting a pretrained
table was reaching for a convenient tool instead of replicating the brain. But the brain did NOT derive
its foundation from scratch either -- EVOLUTION INSTALLED IT over hundreds of millions of years. A human
infant starts with an enormous pre-built prior it did no work to earn. Insisting our substrate derive
everything from its own reading was holding it to a standard the brain itself does not meet.

**THE INVARIANT IS UNCHANGED AND IS THE ONLY BAR: NO LLM IN THE OPERATIONAL FLOW.** A static table built
offline is the analogue of an evolutionary prior. An LLM called at inference is not, and remains
disqualifying regardless of score.

**What this unblocks immediately:** GloVe-300 scores 0.3462 on the identical 322 SimLex pairs against our
best grounded asset's 0.2701, margin +0.3511 [+0.2012,+0.4957] over the floor, p=0.0005. That is no
longer merely a ceiling reference -- it is an admissible foundation ingredient. **What does NOT change:**
it must still be VETTED, still be inspectable, and must still clear the standing bar on the real task,
where nothing yet does. Adopting it is a foundation decision, not a result.

See `notes/drill_brain_word_meaning_acquisition_from_grounded_core_bridging_2026-08-16.md` and BOARD Q3.

**There are TWO relational hubs, not one, and we had only built one.**
**[PINNED -- added 2026-08-16, and it was the single largest fidelity gap in the substrate.]**
TAXONOMIC relations ("a dog is an animal") are carried by the anterior temporal lobe. THEMATIC relations
("dogs go with leashes, spoons go with soup") are carried by a SEPARATE temporo-parietal system. Lesion
studies dissociate them cleanly [Schwartz 2011 PNAS; Mirman 2017 dual-hub], and thematic organisation is
DEVELOPMENTALLY PRIOR -- children group by what-goes-together before what-kind-of-thing
[Nelson/Lucariello slot-filler].

**Every relation we extracted was taxonomic** (COPULA 2006 / APPOSITIVE 1521 / CALLED 1303 /
GLOSSARY_COLON 944 / REFERS_TO 25). We had built one hub and not the other. Our own thematic organ
`extract_predicates` already existed with 221 facts banked, **called by nobody**.

**Turning it on, from the SAME 64MB corpus budget the frequency floor uses** (`relation-supply.json`):
mean in-CORE bridge degree **1.216 -> 3.573** (median 1 -> 3); primary held-out stratum **47 -> 394**;
both-endpoints **4 -> 138**; verbs **0 -> 86**, which makes the noun-vs-verb falsifier constructible for
the first time.

**RETRACTED 2026-08-16, same day: the "+0.2285 [+0.1861,+0.2717] margin over the spelling floor" was
reported here as "the first CI-separated margin over that floor this programme has produced". IT IS NOT A
RESULT ON THE INSTRUMENT THAT MATTERS.** It is the supply scan's NEIGHBOUR-CHOICE DIAGNOSTIC, computed on
a different scorer. On the bridging cell's own instrument the margin over spelling is **-0.0142
[-0.1636,+0.1397]**. This is the same class of error as quoting a 2AFC gain onto an open-vocabulary pool
(DO-NOT-REDO 35) and as the retracted lift gap above: A NUMBER MAY NOT BE CARRIED BETWEEN SCORERS. What
DOES survive: morphology-blocked edge deletion removes 0.48% of edges and the score goes UP, so the
thematic channel is genuinely NOT a spelling channel.

It also explains the pretrained table: its advantage over us is
itself measurably THEMATIC in composition (AtLocation 3907 / UsedFor 1286 vs IsA 1331). It was beating us
with the relation type we had not built.

**Carried forward as a new confound, measured by the same agent that produced the win:** enrichment
raises the bridged-partner shared-neighbour rate to 2.34% against 0.09% at random, CI-separated. Control
C6 is specified and must be run before the margin is quoted as final.

**New meaning is acquired by BRIDGING FROM THE ALREADY-GROUNDED.** **[OURS, the central bet]** A child
does not get norms for every word. They ground a small core through the senses, then extend outward: each
new word is understood by its relation to words already grounded. Our own framing: a gap IS the shortest
missing relational bridge between a new concept and the grounded frontier -- so naming the gap tells you
what to read next, and crossing it IS the grounding. One act, not two.

**Fast binding and slow consolidation are separate systems.** [PINNED, complementary learning systems]
Hippocampus binds an episode in one shot; cortex consolidates the statistics slowly, in sleep. We have
one store doing both jobs.

---

## 5. THE PLAN — five phases, each with a gate and a kill condition

**The standing bar, every phase, no exceptions:** a CI-SEPARATED margin over
`max(orthographic, frequency, scramble)` on the IDENTICAL scorer / n / pool / gold. Never a bare number.
Plus a KNOWN-ANSWER arm proving the instrument and a NULL arm proving the effect -- they fail
independently. **0 of 30 recently-audited cells met this bar.** Everything below is written to.

---

### PHASE 0 — TRUSTWORTHY INSTRUMENTS *(substantially done 2026-08-15/16)*

You cannot improve what you cannot measure, and our rulers were bent. Done: the encoding-quality
instrument (21/21 gates); the checkpoint-collision fix (`ee7c42c0f`) that ended ~128 silently-skipped
runs; the brain-fidelity gate (`3e70c3ba4`); the brain-canonical-defaults tripwire (`0495d5fa8`).

**Remaining, and it blocks Phase 3:**
- **The storage instrument must be redesigned.** Its discriminator assumed the store keeps a smeared key;
  the store keeps no key. Rebuild against what actually runs.
- **Verdict strings are not trustworthy.** Twice tonight a cell reported a passing label whose claim did
  not survive the standing bar. Build a checker that recomputes every banked verdict against the bar and
  reports the disagreements. This is cheap and it protects everything else.

**Kill condition:** none. This phase is permanent overhead, not a bet.

---

### PHASE 1 — MEANING SUPPLY *(the current bottleneck; start here)*

> ## 🔴 **REDIRECTED 2026-08-24 — THE LEVER IS PROJECTING THE NORMS WE HAVE, NOT BUYING MORE. READ THIS BEFORE THE WORK ITEMS BELOW.**
> **Work item 1 says "widen the grounded core to ~90% token coverage: +14,704 words". On tonight's
> evidence that is probably the wrong purchase**, and this phase's own kill condition already
> suspected it (*"hand-rated norms are not a scalable meaning source"*).
>
> `exp_crossmodal_distillation_substitutability_v1` (SOLVED, re-verified, reviewed EXCELLENT):
> **letting the grounded hub TEACH a direction over the distributional model scores `0.8388` CI
> `[0.8031,0.8720]` on the 242-pair substitutability instrument** -- beating its info-free twin's
> MAXIMUM over 200 draws, with no gold anywhere.
>
> 🔑 **AND THE COVERAGE NUMBERS ARE THE POINT FOR THIS PHASE:**
>
> | arm | pairs it can score |
> |---|---|
> | `GROUNDED_ALONE` -- the hand-rated hub itself | **`348` of `484`** (`191` P + `157` S) |
> | **the DISTILLED direction** | **`484` of `484`** |
>
> ➡️ **The distilled direction scores pairs the hub CANNOT, because it is applied to distributional
> features -- which exist for every word in the corpus.** *That is precisely the coverage problem
> this phase was created to solve, addressed without adding a single hand-rated word.*
>
> ⚠️ **WHAT IS NOT YET MEASURED, AND IT DECIDES THE REDIRECT: whether the distilled arm is as
> ACCURATE on the `136` pairs the hub does not cover as on the `348` it does.** The `0.8388` is the
> aggregate; it could be carried by the covered subset. **Split it and report both.** *Until that
> is done, treat "widening is unnecessary" as the leading hypothesis, not a finding.*
> 🚫 **AND THE TEACHER IS STILL A SUPPLIED TABLE.** Distillation makes the existing norms go
> further; it does not make the system independent of them. *Label-free, not resource-free.*

**Brain structure:** sensorimotor spokes feeding the anterior-temporal hub. [PINNED]

**The problem in one line:** our only generalising meaning asset covers 60.4% of running text but just
10.3% of distinct words, and coverage falls to 4% beyond rank 64,000.

**The work:**
1. **Widen the grounded core to ~90% token coverage: +14,704 words** in frequency order (+40,160 -> 95%,
   +103,558 -> 98%). The ~15k option is the knee of the curve and the one to do.
2. **Re-score the widened set on ITS OWN NEW WORDS** against the same floors. Non-negotiable: the
   existing evidence that norms generalise is about rare words that ALREADY HAVE norms. Until new words
   are scored, the coverage number is arithmetic, not capability.
3. ~~**Reduce the lift cost.**~~ **RETRACTED 2026-08-16 -- this item was wrong and it was mine.** The
   claim was that lifting the norms into vector codes costs ~0.073 rho ("a quarter of the signal") and
   was the cheapest win in the plan. Measured like-for-like
   (`data/exp_meaning_lift_population_code_v1/metrics.json`, full, all six validity gates PASS): SimHash
   scores **0.2667** against the **0.2701** direct-read ceiling. **The gap is 0.0034, not 0.073.** The
   larger figure came from comparing numbers computed on DIFFERENT POPULATIONS -- the same class of error
   as quoting a 2AFC gain onto an open-vocabulary pool. There is no quarter to recover.

   **What the cell found instead, and it is worth more than the thing it went looking for:**
   `C1_KCAP_GRD_f005_BOOST@d1024` -- a SPARSE, GRADED population code -- carries meaning at **0.2801,
   CI-separated above all three floors**, AND retains **3.5264 of 7 bits through bundling**: 4.0x the
   incumbent and 7x the pre-registered 0.5-bit criterion. **Meaning that survives superposition is the
   combination this programme needs and had never achieved.** The contrast makes the trade-off concrete:
   `C4_PHASOR` wins on meaning outright (0.3345) and dies in bundling at 0.0097 bits. Meaning you cannot
   superpose is meaning you cannot store.

   **Honest caveat:** the CELL fails the standing bar (`verdict_bar_check` -> `FAILS_BAR`; G0/G4 failed
   on a degenerate denominator, not on the candidates), so the base rate stays 0 of 7,769. The ARM is
   promising; the cell is not a pass. Sparsity is now the live Phase 1 lever -- it is also the largest
   named fidelity gap in section 4 (the brain is sparse, we are dense).

**Gate:** the widened, lifted meaning code clears `max(orthographic, frequency, scramble)` CI-separated on
NEW words it was not built from.

**Kill condition:** if a 15k-word widening does not move the margin on new words, hand-rated norms are not
a scalable meaning source and Phase 2 becomes the only route -- go there directly rather than widening
further. **Do not** buy the number by adopting a pretrained co-occurrence table; that is the failure mode
the owner has named repeatedly.

---

### PHASE 2 — GROUNDING GROWTH *(the central scientific bet)*

**Brain structure:** hub-mediated inference over grounded spokes. **[OURS -- invention under test, and the
part nobody has pinned.]**

Hand-rating words does not scale and is not how humans do it past early childhood. The bet is that a
small grounded core plus reading is enough to ground the rest, one bridge at a time.

**Biology, from the 2026-08-16 drill** (`notes/drill_brain_word_meaning_acquisition_from_grounded_core_bridging_2026-08-16.md`):
the brain bridges new meaning from a grounded core of order 10^3 words, combining relations through the
anterior-temporal hub and angular gyrus. The combination is **ADDITIVE** [PINNED, Baron & Osherson]; the
exact transformation is **UNPINNED and therefore ours to choose and test**. Nearest-frontier ordering is
positively predicted by one-trial schema consolidation [Tse 2007] and by the "lure of the associates"
result [Hills 2009] -- **with a built-in falsifier: that effect is NOUN-SPECIFIC**, so if our bridging
works equally well on verbs we are not seeing the mechanism we think we are. Note our foundation is
already noun-only (0 verb definitions in 2,092 facts), so this must be checked deliberately.

**CORRECTION to an earlier draft of this section:** it said to "unify three things we already own onto a
single distance-to-frontier metric". Runtime inspection found **none of `gap_detector`,
`gap_driven_reader` or the grounding evaluation computes any distance at all.** There is nothing to
unify. The distance-to-frontier metric must be BUILT.

**Also found, and it invalidates a scorer:** `grounded_similarity()` saturates 76.2% of SimLex pairs onto
just two values. It must NEVER be used as a scorer, and anything that used it needs re-checking.

**The work:** `exp_bridged_grounding_from_core_v1` -- hide the norms for a held-out set; rebuild each
word's code ONLY by additive d=1 bridge from a core of words with age-of-acquisition <= 6.0 (2,838
available); score Spearman rho on the bridged-endpoint stratum (n=392 measured; the both-endpoints
stratum at n=66 is underpowered BY CONSTRUCTION and must be reported as such, not quietly dropped).

**Gate:** a word grounded ONLY by bridging -- never hand-rated -- clears
`max(orthographic, hardened-frequency, scramble)` CI-separated, recomputed ON THAT SAME STRATUM. Arms:
`K1_OWN_NORMS` and `K2_ORACLE_BRIDGE` as known-answer arms; a degree-and-frequency-matched EDGE SHUFFLE as
the null; **morphology-blocked edge deletion as the decisive spelling-leakage control** -- required
because a pure spelling channel already beats our whole system 8.70% to 4.80%, so an uncontrolled bridge
score proves nothing.

**Kill condition:** if bridged words never clear the floor while hand-rated words do, then grounding does
not propagate through our relations, and the substrate needs a genuinely different acquisition mechanism.
This is the most important negative result available to this project; report it loudly if it happens.

---

### >>> THIS KILL CONDITION FIRED, 2026-08-17. TWO INDEPENDENT MECHANISMS, BOTH NULL, BOTH GATED. <<<

**1. ADDITIVE BRIDGING FROM THE GROUNDED CORE** (`exp_thematic_relation_supply_bridged_grounding_v2`,
full, 5.1 h). All five additive transformations NOT_SEPARATED on every large stratum (B1 rho 0.0270,
B5 0.0406, permutation p 0.30). Identity is PRESERVED (96.12% distinct codes) and MEANING IS LOST
(8.19% retention vs the hand-rated original). G0 passes on all 8 large strata (K1 +0.2168 to +0.2728),
so the null is READABLE, not an instrument failure.

**2. SELECTIONAL-CONSTRAINT BRIDGING** (`exp_selectional_constraint_bridge_v1`, complete FULL) -- the
owner's own Q5 mechanism: infer the word from the VERB'S CONSTRAINTS on its argument rather than by
copying a lexical neighbour. **CI-separated BELOW the neighbour-copy incumbent (-0.1049) and
NOT_SEPARATED from a RANDOM TARGET**, with its known-answer arm alive.

**So the second mechanism is not merely no better than copying a neighbour -- it is WORSE than
copying, and indistinguishable from pointing at a random word.** These are different mechanisms over
different relation types (thematic co-participation; verb-argument selectional restriction) drawing on
different assets. Both null. The common factor is not the mechanism.

**WHAT THIS DOES AND DOES NOT LICENSE.**
- It DOES establish that **grounding does not propagate through OUR relations, as built**, and that
  more bridging variants are not the answer. Do not build a third one without a new reason.
- It DOES NOT establish that relational bootstrapping is impossible -- **the owner's standing
  directive holds: the brain does this, so the capability is DEMONSTRATED, and a miss is a fact about
  OUR IMPLEMENTATION.** A child does acquire most of its vocabulary this way.
- **Read it alongside the partial-cue result, because they may be one finding.** A cheating oracle
  reads 0.0365 under partial cue against 0.8787 at exact key, and purity predicts exact-key retrieval
  at rho 0.961 while predicting the partial cue at rho -0.0167. **If the cue does not carry the
  identity, then no bridge built ON that cue could ever have worked**, and both nulls have a single
  upstream cause. **DIAGNOSE THAT BEFORE BUILDING ANY REPLACEMENT ACQUISITION MECHANISM.** That
  diagnosis is item 1 of `notes/PLAN_NEXT_24H.md`.

**A POWER CAVEAT, because this project has read an underpowered null as a capability statement three
times in one session:** the verb and adjective strata in mechanism 1 were UNDER-POWERED -- at n=86 a
Spearman CI half-width is ~0.215 and the stratum floor (0.1814) was itself ~the null-distribution
width. Those strata are POWER_INSUFFICIENT, not failures. **The kill fires on the LARGE strata, where
G0 passes and the arms are readable** -- not on the underpowered ones.

---

### PHASE 3 — ADDRESSED STORAGE *(blocked until Phase 1 clears)*

**Brain structure:** perirhinal conjunctive coding + hub-and-spoke addressing. Organ PINNED; operator
**OURS**.

**Where it stands:** the hub-and-spoke word is built and survives partial cue where conjunction collapses.
It does not beat the flat bag. Registered WIRE_CANDIDATE, correctly, not WIRE.

**The work:** re-run the flat-vs-addressed comparison once codes carry real meaning. Sparsify -- the brain
is sparse and we are dense, and this is the largest unexplored fidelity gap we have. Fix the codebook
collision found tonight (1,476 codes for 4,096 words).

**Gate:** addressed beats flat CI-separated on the REAL reading task, not in isolation. An isolation win
is a construction proof; this project has repeatedly mistaken one for a capability.

**Kill condition:** if addressing still does not beat flat with meaningful codes and no collision, then
addressing is not our lever and the plan reorganises around selection.

---

### PHASE 4 — COMPLETION AND SELECTION *(blocked until Phase 3 clears)*

**Brain structure:** DG separation + CA3 completion, a matched pair. [PINNED as a pair; our
implementation OURS.]

**Where it stands:** refuted at smoke -- completion hurts at every partial overlap -- with a self-flagged
handicap in our setup. The fair re-test is filed.

**The work:** fair re-test without the collision handicap; then selection, which is the component that
measurably fails today, using meaning that by then actually exists.

**Gate:** hit@1 on the open-vocabulary read-out clears the SPELLING floor CI-separated. That is the first
moment this system does something a spell-checker cannot.

**Kill condition:** if completion cannot be made to help under partial cue after the handicap is removed,
record that separation and completion do not compose in our geometry -- a real finding about VSA, not
just about us.

---

### PHASE 5 — CONSOLIDATION *(long horizon)*

**Brain structure:** complementary learning systems -- fast hippocampal binding, slow cortical
consolidation. [PINNED]

We have one store doing both jobs, which is why capacity and interference fight each other. A fast
episodic store plus slow statistical consolidation is the brain's answer and we already own pieces of
both. This is deliberately last: it is an optimisation of a system that must first work at all.

---

## 6. WHAT WE STOP DOING

- **Stop tuning selection.** It is not the defect; it is the symptom. Two of tonight's floored negatives
  were selection interventions.
- **Stop quoting the headline 4.80%.** Every claim is per-component with its own floor beside it.
- **Stop trusting verdict strings.** Twice tonight a passing label sat on a dead claim.
- **Stop treating an isolation win as a capability.** Three banked isolation wins did not survive contact
  with the real task; one actively hurt.
- **Stop reaching for the convenient tool.** GloVe would raise our number tomorrow and teach us nothing.
  Ceiling reference only.

---

## 7. HOW WE WILL KNOW IT IS WORKING

In order, each a CI-separated margin over the strongest floor:
1. A widened grounded core clears the floor on words it was not built from. *(Phase 1)*
2. A word grounded only by bridging clears the same floor. *(Phase 2 -- the thesis)*
3. Addressed storage beats the flat bag on the real reading task. *(Phase 3)*
4. The read-out beats the SPELLING floor at hit@1. *(Phase 4 -- the first real capability)*
5. Comprehension competencies accumulate rather than saturating: passive, relative, coreference,
   negation each get their own learned capacity, and adding one does not cost another.

**The honest position on timing:** we are before step 1. Step 4 is the first point at which this system
does something a trivial baseline cannot. Everything before that is building the conditions for it.

---

## 8. THE STANDING FRAME — there is no question of whether this works

**Owner directive, 2026-08-16, and it governs how every result in this plan is read:**

> "we are building a brain foundational ai here - we know it works, and we can replicate it... There is
> no chance of failure here - we KNOW it can work, because the brain does. so keep working, component by
> component, drilling brain function for each function that we're trying to reconstruct."

**This is not optimism, it is the correct inference, and an earlier draft of this file got it wrong by
calling Phase 2 a bet that might fail.** The brain grounds new word meanings from a small sensory core
plus experience, at a fraction of our text budget. So the capability is DEMONSTRATED. The only open
question is ever whether OUR reconstruction of a given organ is faithful enough yet.

**What that changes in practice — the reading of every negative result:**
- A miss is a fact about OUR IMPLEMENTATION, never about the capability. `PAIRING_HYPOTHESIS_REFUTED`
  does not mean completion cannot help; it means our completer, with a codebook collision we introduced,
  did not help in the setup we tried.
- Before any direction is called exhausted, write down what was actually tested and what the STRONGER,
  more brain-faithful version would be -- then test THAT. A fair test of a weak implementation proves
  only that the weak implementation failed.
- "Intrinsic ceiling" is never the first hypothesis. The order is: is a needed COMPONENT missing? Is a
  needed LEARNING mechanism missing? Is the operator a convenient substitute rather than the brain's?
  Only after those, and after a fidelity audit of every element's shape, position and metric, does a
  ceiling claim get made -- and even then the brain's way is the fix.
- Deflate CLAIMS, never AMBITION. Reporting a null honestly and continuing is the job; concluding
  impossibility from a null is a category error.

**The method, per component, in this order every time:**
1. **DRILL THE BIOLOGY FIRST.** Which neural structure performs this function? Not a cognitive-theory
   label -- a structure. What is its input, its output, its coding scheme, its failure mode?
2. **COMPARE OURS TO IT** element by element: shape, position in the pipeline, and the metric it is
   judged on. Name the divergence.
3. **THE DIVERGENCE IS THE BUILD TARGET.** Reuse the organ we own if we own one; the brain reuses
   circuits and a parallel build is both unfaithful and islanding.
4. **TEST IT CAN FAIL**, against the standing bar, with a known-answer arm and a null arm.
5. **ITERATE ON FIDELITY, NOT ON THE NUMBER.** If it loses, the next question is which element still
   diverges from the biology -- not which threshold to move.

Where the literature does not pin an operation, propose the highest-probability brain-motivated candidate
and TEST it, and keep testing candidates until one matches. Invention is authorised and expected. What is
barred is reaching for a convenient available tool INSTEAD of asking how the brain does it, and
presenting our invention as though the biology pinned it.
