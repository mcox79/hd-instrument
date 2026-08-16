# DRILL: is a 12-dimensional sensorimotor rating space capable of holding word meaning at all?

**2026-08-16, Director (research role). BIOLOGY DRILL + ASSET ENUMERATION + EXPERIMENT DESIGN.
No experiment cell authored. No experiment run. No `hdlab/` or `experiments/` file modified.
No `metrics.json` touched. No subagent spawned. No commit to `data/foundation/**`,
`data/capability_registry.jsonl`, `preregs/`, `notes/PLAN.md` or `notes/LONG_TERM_PLAN.md`.
The live FULL run (`scratch/them_v2_full.pid`) was not polled, touched, or inspected.**

Machine-readable companion: `.claude/scan-out/target-space-drill.json`.

Governing frame: `notes/LONG_TERM_PLAN.md` section 8. The brain does this, so the capability is
DEMONSTRATED. Nothing below concludes that bridging or grounding is intrinsically limited. Every
negative here is a fact about OUR implementation.

**No tool call was denied during this drill.** One tool ERROR is disclosed rather than worked
around: a repo-relative `grep -ril` across `experiments/ preregs/ notes/ hdlab/ tools/`
(5,842 + 3,808 + 11,521 + 160 + 7,408 files) exceeded the 2-minute Bash timeout and returned exit
143 before printing any hits. It was replaced by scoped `Grep` calls on `hdlab/`, which completed.
The enumeration COUNTS above are real (they printed before the timeout); the keyword sweep across
`experiments/` and `preregs/` did NOT complete, so **my dedup coverage is `hdlab/` + the capability
registry + the substrate KB, and NOT a full sweep of `experiments/` or `preregs/`.** Stated because
an absence claim requires an enumeration and mine is partial.

---

## 0. THE QUESTION AND THE SHORT ANSWER

The central bridging experiment came back flat and readable: bridged codes keep the word's
IDENTITY (96.1% distinct) and lose its MEANING (8.2% retention). The falsifier implicated the
target space rather than the mechanism, because the same noun-over-verb profile appears in
`K2_ORACLE` (no graph) and in `K1` (hand-rated, no bridging).

**The answer: the 12-dim space CAN hold meaning, and it is ALSO demonstrably a cap -- because it
is a CONCRETE-SPOKE-ONLY subset of the brain's experiential attribute set, covering two of the
brain's seven semantic blocks. The single missing block we already own on disk (AFFECT) raises the
hand-rated SimLex ceiling by +0.10 to +0.13 overall, paired, CI-separated, on an identical
977-pair stratum, under both raw and z-scored construction. And the POS profile of the GAIN is the
mirror image of the POS profile of the FAILURE.**

**Why that reinterprets the falsifier.** Affective experience is the grounding channel for
abstract and evaluative meaning [PINNED], abstract words carry higher affective ratings than
concrete words [PINNED], and our space has no affective channel. Nouns depend on it least, verbs
and adjectives most. So the noun-over-verb asymmetry is a SHAPE MISMATCH between the words and the
landing space -- which is exactly why it reproduces with the graph removed and with the bridging
removed. Both of those arms land in the same deficient space.

---

# PART A -- THE BIOLOGY

Every claim marked **[PINNED]** (evidence fixes it) or **[UNPINNED]** (ours to choose and test).
Neural structures named, not cognitive-theory labels. Where the field is in dispute the dispute is
reported rather than adjudicated.

## A1. THE DIMENSIONALITY OF SEMANTIC REPRESENTATION IN CORTEX

**There is no single number, and the number you get is a property of the METHOD.** Reported as a
range with the method beside each figure, as the brief requires.

| dims | method | source | status |
|---|---|---|---|
| **3-4** | PCA over voxelwise model weights AVERAGED ACROSS SUBJECTS, keeping only components that survive a subject-consistency bootstrap | Huth, de Heer, Griffiths, Theunissen & Gallant 2016 *Nature* 532:453. A 985-dimensional co-occurrence feature space was fit to voxels; **4** PCs explained significant variance (p<0.001, Bonferroni-corrected bootstrap) in all but one subject, **3** in the last; **3** were used for the published cortical map | [PINNED] |
| **49** (66 in the extension) | SPoSE sparse-positive embedding fit to 1.46M (later 4.70M) triplet odd-one-out judgements over 1,854 natural objects | Hebart, Zheng, Pereira & Baker 2020 *Nat Hum Behav*; THINGS initiative | [PINNED] |
| **65** | meta-analysis of functional divisions in human brain, then human salience ratings per word | Binder, Conant, Humphries et al. 2016 *Cognitive Neuropsychology* 33:130 (PMID 27310469) | [PINNED as a proposal] |
| **unbounded / ill-defined** | cross-validated SVD + hyperalignment, human cortex; and 2-photon population recording, mouse V1 | arXiv 2409.06843 (human, scale-free); Stringer, Pachitariu, Steinmetz et al. 2019 *Nature* 571:361 (nth PC variance ~ 1/n) | [PINNED] |

The scale-free human result is quotable and blunt: *"the scale-free nature of the spectrum
suggests that its dimensionality is ill-defined and likely unbounded (up to the number of
neurons)"*; conventional variance-weighted methods such as RSA detect only **~10** dimensions; and
*"any low-rank truncation of these representations would lead to a non-negligible loss of
stimulus-related information."*

**HONEST CAVEAT, and it matters.** The scale-free human measurement is on **VISUAL** cortex, and
the Stringer power law is **mouse V1**. I did **not** find a semantic-cortex equivalent and I am
**not** claiming one. The generalisation from visual population geometry to semantic population
geometry is **[UNPINNED]**.

**THE SYNTHESIS.** ~4 is what survives anatomical averaging across subjects, i.e. what is SHARED.
~50-65 is what an attribute decomposition recovers. Unbounded-with-a-heavy-tail is what the
population appears to carry. **Our 12 sits in the low-rank shoulder.** So 12 is not absurd -- it is
roughly the size of what a variance-weighted method can see -- **but it is a TRUNCATION, and the
literature says truncation costs real information.**

## A2. WHAT THE DIMENSIONS ARE ACTUALLY ABOUT, AND WHICH ARE SEPARABLE

Binder's brain-derived set has **seven blocks**: sensory, motor, spatial, temporal, **affective**,
**social**, cognitive. Per block, with its substrate and its separability:

- **Sensory + motor** -- modality-specific perceptual and motor cortices = the SPOKES, converging
  on anterior temporal lobe = the HUB. Separable: spoke lesion loses one facet, hub lesion loses
  meaning across the board. **[PINNED]** *This is 11 of our 12 dimensions.*
- **Affect (valence / arousal / dominance)** -- amygdala (population coding of valence), orbito-
  frontal and ventromedial prefrontal cortex. Separable: **[PINNED]**. Load-bearing sub-fact:
  *affective experience is crucial in the grounding of ABSTRACT concepts, and abstract words
  receive higher ratings for both valence and arousal than concrete words* (Vigliocco et al., "The
  neural representation of abstract words: the role of emotion", PMID 23408565). **We do not have
  this block.**
- **Social relevance** -- a SEPARATE SOCIAL SEMANTIC NETWORK: bilateral ATL (superior ATL for
  social concepts, Zahn et al. 2007 *PNAS*), TPJ / angular gyrus, dorsomedial PFC, posterior
  cingulate / precuneus. The literature states that sensory-motor and social semantic information
  are *"the most salient information types that constrain the organization of the semantic system
  in brain"*, *"supported by two SEPARATE semantic subsystems"*. **[PINNED]** **We do not have this
  block.**
- **Taxonomic category** -- anterior temporal lobe. Double-dissociated from thematic by lesion
  (Schwartz et al. 2011 *PNAS* VLSM; Mirman, Landrigan & Britt 2017 dual-hub). **[PINNED]** *We
  carry this as a relation graph, never as dimensions of the landing space.*
- **Thematic / event role** -- posterior middle temporal gyrus + angular gyrus. **[PINNED]** *We
  carry this as a relation graph since 2026-08-16, never as dimensions of the landing space.*
- **Action affordance** -- dorsal stream, parietal and premotor; pMTG exerts causal influence on
  premotor/M1 for action verbs (Granger causality, S0361923012000779). Partly separable: left
  lateral temporal cortex holds representations of VERBS that are INDEPENDENT of representations
  of the ACTIONS they denote (JOCN `jocn_a_00257`). **[PINNED]** *Partially ours, via the 5
  Lancaster effector dimensions.*
- **Spatial / temporal / causal** -- Binder blocks; temporal and causal structure IS event
  structure. Asserted by Binder, less strongly dissociated. **[PINNED as a proposal, UNPINNED as
  separate systems]** **We do not have these.**

**THE COUNT: our 12 dimensions cover TWO of the SEVEN blocks, plus one scalar (concreteness).**

## A3. VERBS -- THE MOST DECISION-RELEVANT PART OF THE DRILL

**The answer splits cleanly, and the split is the whole finding.**

**The EXPERIENTIAL part of verb meaning IS representable in a rating space -- and, once affect is
included, our measured verb ceiling (0.4501) is HIGHER than our noun ceiling (0.3590) on the same
stratum.** So "verbs need a fundamentally different substrate" is FALSE as a blanket claim, and
"our rating space cannot do verbs" is false too. What is true is that the CURRENT space cannot,
because it lacks the block verbs lean on.

**The RELATIONAL part of verb meaning is NOT representable in ANY per-word vector, at any width.**

- Left pMTG extending into angular gyrus scales with verb ARGUMENT VALENCY: three-argument verbs
  (*put*) > two-argument (*chase*) > one-argument (*sleep*). **[PINNED]** (Thompson et al.,
  PMC2632636 / PMC2490697.)
- Thematic-role ASSIGNMENT -- deciding which argument is the agent -- recruits posterior parietal
  cortex; TMS to posterior intraparietal sulcus changes agent-decision accuracy on passive
  sentences. **[PINNED]** (PMC10158617; S002839321530141X.)
- Action verbs show a causal pMTG -> premotor/M1 influence, and bidirectional pMTG <-> premotor.
  **[PINNED]**
- Left lateral temporal cortex represents VERBS independently of the ACTIONS they denote, so verb
  meaning does not reduce to motor simulation. **[PINNED]**
- Gentner's relational-relativity line: verbs are less stable across translation, more readily
  altered in meaning under semantic conflict, more visually variable, and later-acquired; verb
  meanings package only PART of the available relational information and which part is
  language-specific. **[PINNED]**

**"Takes an agent and a patient and causes a change of state in the patient" is a TYPED
STRUCTURE, not a magnitude. No scalar rating on any dimension can express it.**

**Three separate divergences in our system all point at verbs, and none is a ceiling:** our
foundation is noun-only (0 verb definitions in 2,092 facts); our target space has no affect
channel; our relation graph is UNTYPED co-participation. The affect fix is measured and cheap. The
role-typing fix is the one the sibling cell already pre-registered (`extract_predicates_v62`,
`hdlab/thematic_role_labeler.py` -- both owned, both never fed into a bridging graph at scale).
The argument-slot fix is a structural change to what a code IS, and it is the genuinely hard one.

## A4. IS A SMALL, HAND-RATED, PER-WORD ATTRIBUTE VECTOR THE RIGHT SHAPE AT ALL?

**Partly right in kind, wrong in three specific ways. The honest answer is not uniformly damning,
and I am going to separate the parts that ARE the "convenient tool" failure from the parts that
are not.**

**What is DEFENSIBLE about it.** Interpretable, low-rank, per-item attribute dimensions are not
merely a human-readable convenience. Hebart 2020 recovered 49 sparse positive INTERPRETABLE
dimensions from pure behaviour, and they predicted categorisation behaviour and typicality
judgements. Binder derived 65 from brain functional divisions. **The brain-modelling literature
itself uses attribute vectors and they work.** Choosing an interpretable attribute basis is not the
same act as adopting a fitted external embedding: an attribute basis is inspectable, is ours to
reason about, and has direct brain-derived precedent. The glass-box charter is served by it.

**WRONG 1 -- TRUNCATION.** 12 is far below the 49-65 an attribute decomposition recovers, and far
below the heavy power-law tail. [PINNED, with the visual-cortex caveat of A1.]

**WRONG 2 -- THE WRONG BLOCKS, and this is the load-bearing one.** The defect is not mainly WIDTH,
it is WHICH CHANNELS. Measured (Part C): adding 11 more columns of Lancaster **rater-SD** buys
nothing; adding 6 nonlinear summaries of the same 11 dims buys nothing; adding **three** columns of
a **missing channel** buys +0.1013 CI-separated. **This is a missing-spoke defect, not a
dimensionality defect.**

**WRONG 3 -- SENSE AVERAGING.** A per-word rating is an average over that word's senses. Trott &
Bergen (arXiv 2203.05648) show same-sense uses have more similar sensorimotor profiles than
different-sense uses, and that contextual ratings carry information beyond the per-word norms.
**The brain does not store a sense-average; it settles on a sense in context.** [PINNED]

**WHERE THE "CONVENIENT TOOL" CRITICISM DOES LAND, plainly.** Hand-rated norms are a HUMAN
INTROSPECTIVE PROXY, and the authors of our own scorer say so: the norms *"rely on participant
introspection rather than direct neural recordings, which cannot fully satisfy concerns about
word-concept dereferencing"*. And, decisively for us, the same authors state the measure *"would
not generally capture all forms of semantic similarity, such as those based on **thematic
relationships** between concepts"* (Wingfield & Connell, PMC10615916).

**We spent the 2026-08-16 cycle building a THEMATIC relation channel and pouring it into a space
its own authors document as not representing thematic structure.** That is a shape mismatch
between the bridge and the landing space, and it is an INDEPENDENT candidate cause of the 8.2%
retention, additional to the missing-affect one. Both should be on the table.

**Where the criticism does NOT land:** an attribute basis is not a pretrained table. The failure
the owner has warned about is adopting a fitted external artefact because it raises the number.
Choosing which brain-derived blocks to represent is the opposite act.

---

# PART B -- WHAT WE COULD LAND IN (disk first, registry second, runtime always)

**Method.** `os.walk` / `stat` on disk FIRST; then every candidate OPENED AND PARSED under
`D:/AI/hd-instrument/.venv/Scripts/python.exe`. Column names and row counts below are what the
FILES CONTAIN, not what their names claim. `data/capability_registry.jsonl` opened READ-ONLY
afterwards and NOT written. The registry has **200 rows keyed on `id`**, not on module, so there is
no 1:1 module-to-row mapping in either direction -- a registry-first audit of this question would
have been structurally blind. Probe: `tools/target_space_assets_probe.py`.

**Ground truth.** `data/encoder_eval_benchmarks/simlex999.txt` -- 999 pairs, 1,028 words;
words per POS N 751 / V 170 / A 107; pairs per POS N 666 / V 222 / A 111.

| id | space | dims | vocab | SimLex coverage | verbs? | ours? |
|---|---|---|---|---|---|---|
| **T1_CURRENT** | Lancaster 11 means + `Conc.M` | 12 | **36,810** | 1028/1028, incl 170/170 verbs | by coverage yes | external |
| **T2_PLUS_AFFECT** | T1 + Warriner V/A/D | 15 | **13,374** (intersection) | 1012/1028 words, 977/999 pairs, 167/170 verbs | yes | external |
| **T3_AFFECT_ONLY** | Warriner V/A/D | 3 | 13,905 | -- | yes | external |
| **T4_WIDER_UNINFORMATIVE** | T1 + 11 rater-SD cols / + 6 derived | 23 / 18 | 39,705 | full | -- | external |
| **T5_BINDER_65** | Binder brain-based componential | 65 | **535 (434 N / 62 V / 39 A)** | **unmeasurable, not on disk** | 62 verbs only | external |
| **T6_OUR_VERB_ORGAN** | `hdlab/verb_lexical_similarity.py` | 8,192 (FHRR) | **~172 hand-authored words** | -- | yes but tiny | **OURS** |
| **T7_RELATIONS** | `thematic_edges_v1.pkl`, CSKG, ATOMIC v4 | n/a -- a graph, not a vector space | 21,652 normed lemmas | -- | yes | thematic is OURS; CSKG/ATOMIC external |
| **T8_AOA** | Kuperman AoA | 1 | 51,715 | -- | -- | external |

**Runtime confirmations, and one correction.**

- `hdlab.grounded_similarity.coverage_stats()` returns `{n_words: 36810, n_dim: 12,
  grounded_cap: 0.45}`; `_table()['a']` has length 12. **CONFIRMED LIVE.**
- `thematic_edges_v1.pkl` is 28,724,302 B; its `extraction_report_v1.json` records 748,103
  sentences seen, 483,631 with a finite main verb, 420,910 event pairs at count>=2, 160,500
  verb-argument pairs at count>=2, 21,652 distinct normed lemmas, from a 63,999,974-byte simplewiki
  budget. **CONFIRMED.**
- **CORRECTION -- `hdlab/verb_lexical_similarity.py` is far narrower than its name.** Runtime
  inspection: `N_DIM = 8192` FHRR codes built from HAND-AUTHORED CLOSED LEXICONS --
  `GOAL_VERB_FEATURES` 73 entries, `OUTCOME_VERB_FEATURES` 99, `CAUSAL_MARKER_FEATURES` 12,
  `RELATION_MARKER_FEATURES` 16 -- across four narrow domains, and `concept_vector(word, domain)`
  **requires a `domain` argument**. It is a ~172-word verb-CLASS classifier, **not** a general verb
  meaning space. **It cannot be a target space.**
- **ATOMIC v4 is on disk and unused** (`v4_atomic_trn.csv` 31,430,641 B + `all_agg` 19,341,556 +
  dev 3,517,258 + tst 3,871,655). It is EVENT-CENTRED if-then knowledge and therefore the most
  VERB-RELEVANT asset we hold. CEILING-REFERENCE class (external), same rule as CSKG and GloVe --
  never a meaning source.
- **DEDUP HIT.** Registry `id = binder_direct_supply_grounding` is already `SHELVE` /
  `closed_correctly_data_bound`, provenance: *"Binder-65 not even on disk"*. **My independent
  finding reproduces that ruling.** Binder-65 is the most brain-faithful rating space in the
  literature and is unusable as our primary landing space at 535 words. Worth acquiring as a 65-dim
  ORACLE arm on its own small stratum; never as the target space.
- **NOT a dedup hit:** `hdlab/context_grounded_valence.py` (registry `WIRE`, `WIRED_BUT_NOT_
  PIPELINE_REACHABLE`) is an EVENT-valence scoring organ -- governor sense-select plus a WordNet
  animacy-axis patient override. It does not use Warriner's table as a semantic dimension.
  **Affect-as-target-space-dimensions has not been tried.**
- The substrate KB (`tools/director_kb_query.py`) returned only generic WordNet nodes for this
  concept class (`dimension` 0.3877, `dimensionality` 0.3799) plus one unrelated 2026-05-23
  prereg. **The KB found nothing; the disk enumeration and the registry did.** Same conclusion as
  the 08-16 bridging drill: for this concept class the filesystem is the stronger instrument.

## B1. THE PRIOR DECISION THIS DRILL OVERTURNS

`hdlab/grounded_similarity.py`, lines 51-56, verbatim:

> VAD (Warriner) + AoA (Kuperman) norms also live in data/grounding_testbed/ but are NOT used
> here: both are affect/acquisition-trajectory signals, not identity-content signals, and folding
> them in would not address the sibling\synonym confound above (also verified: mixing an
> incomplete-coverage source, ~13,915 Warriner words vs ~39,707 Lancaster words, forces an
> asymmetric zero-fill for the majority of words, which is its own artifact). Left as a documented,
> available extension point, not used in this v1.

**Clause 1 is REFUTED.** "Affect is not an identity-content signal" is a cognitive-theory
assertion, was never measured on the meaning axis, and is false as stated. Measured, paired, on an
identical stratum, CI-separated: affect adds **+0.1228 [+0.0150, +0.2314]** on verbs and
**+0.3399 [+0.1919, +0.4978]** on adjectives. The brain agrees -- affect is one of Binder's seven
blocks with its own substrate.

**Clause 2 STANDS and is the real constraint.** The zero-fill artefact is real and the warning is
correct. The fix is INTERSECTION-STRATUM evaluation, which is what Part C did and what the design
in Part D mandates. **ZERO-FILL REMAINS BARRED.**

**Why this matters beyond the number.** An unmeasured assumption written into a source comment has
been capping the target space since the module was authored. This is the shelve-on-a-non-brain-
framed-criterion failure mode: the exclusion reason was a cognitive-theory label rather than a
brain structure, and it closed a live direction.

---

# PART C -- THE CEILING DIAGNOSTIC

> **SCOPE WARNING, READ BEFORE QUOTING ANY NUMBER IN THIS SECTION.** Every figure below is a
> CEILING measurement using the word's OWN hand-rated code -- the K1 condition, no graph, no
> bridging. **NO FLOORS were computed. NO null arm. This is NOT a cell, NOT a verdict, and NOTHING
> here clears the standing bar.** It exists solely to decide which target spaces are worth putting
> into a can-fail cell. Scripts (promoted out of `scratch/` per the CLAUDE.md scratch corollary,
> because this note cites them as the provenance of numbers):
> `tools/target_space_ceiling_diagnostic.py`, `tools/target_space_paired_diagnostic.py`,
> `tools/target_space_assets_probe.py`. They write
> `data/_target_space_ceiling_diagnostic.json` and `data/_target_space_paired_diagnostic.json`.

**Stratum.** 977 SimLex-999 pairs / 1,008 words where BOTH endpoints are defined in EVERY space
compared. Per POS: N 655, V 215, A 107. **Scorer:** plain cosine on the concatenated rating vector,
L2-normalised; Spearman rho vs SimLex gold; 4,000 bootstrap draws with a **SHARED resample index
across arms** (properly paired); seed 20260816.

### RAW concatenation

| POS | n | S1 current 12-dim | S4 15-dim (+VAD) | paired delta | 95% CI | separated |
|---|---|---|---|---|---|---|
| ALL | 977 | 0.3130 | **0.4143** | **+0.1013** | [+0.0615, +0.1419] | **YES** |
| N | 655 | 0.3338 | 0.3590 | +0.0253 | [-0.0115, +0.0615] | no |
| V | 215 | 0.3273 | **0.4501** | **+0.1228** | [+0.0150, +0.2314] | **YES** |
| A | 107 | 0.2377 | **0.5776** | **+0.3399** | [+0.1919, +0.4978] | **YES** |

### Z-SCORED per dimension (rules out a scale artefact)

| POS | S1 | S4 | paired delta | 95% CI | separated |
|---|---|---|---|---|---|
| ALL | 0.2696 | 0.4040 | +0.1344 | [+0.1021, +0.1687] | YES |
| N | 0.2997 | 0.3691 | +0.0694 | [+0.0389, +0.1032] | YES |
| V | 0.2358 | 0.3968 | +0.1610 | [+0.0874, +0.2405] | YES |
| A | 0.1845 | 0.5577 | +0.3731 | [+0.2322, +0.5189] | YES |

**The effect survives both constructions**, so it is not an artefact of VAD's 1-9 scale sitting
beside Lancaster's 0-5.

### THE NEGATIVE CONTROL, and it fired

| space | dims | rho ALL (raw) | vs S1 = 0.3130 |
|---|---|---|---|
| S5 = T1 + 11 Lancaster **rater-SD** columns | 23 | 0.3035 | **no gain** |
| S6 = T1 + 6 **derived nonlinear summaries** of the same 11 dims | 18 | 0.3025 | **no gain** |

**Widening with columns that carry no new CHANNEL buys nothing. Therefore the VAD gain is not
"more dimensions help".** This is the single most important control in the diagnostic.

### THE DISSOCIATION

VAD **alone** (3 dims): ALL 0.1676, **N 0.0374** (CI-separated WORSE than S1, delta -0.2964),
V 0.3014, **A 0.5593**. **Sensorimotor and affect are complementary spokes -- neither replaces the
other, and the union beats both.** That is what hub-and-spoke predicts.

### DEGENERATE ARM, DISCLOSED

`S9_VALENCE_ONLY_1` returns NaN under RAW because a 1-dimensional vector L2-normalised is always
+/-1, so every cosine is +/-1 and Spearman is undefined; under z-scoring it degenerates to
sign-agreement (0.1716). A construction artefact, reported rather than hidden.

### EXTERNAL CORROBORATION -- our scorer is not broken

Wingfield & Connell (*Behav Res Methods*, PMC10615916) report the same 11-dim Lancaster space at
**r = -0.32 on SimLex-999** (993 pairs), -0.28 WordSim-353, -0.34 MEN. Our `S2_lanc11_only`
measures **0.3186** on 999 pairs. **We reproduce the published value.**

**The consequence is the one sentence in this drill most worth carrying forward: our
`K1_OWN_NORMS` = 0.3301 IS the published ceiling of this space, not a shortfall against it. The
bridge is being asked to recover a fraction of a signal that is itself capped near 0.33.**

---

# PART D -- THE DECIDING EXPERIMENT

**Working anchor: `exp_target_space_vs_bridge_mechanism_v1`. DESIGN ONLY. No cell authored, no
pre-registration written, nothing dispatched.**

## D0. ONE SENTENCE

Hold the bridging mechanism, the graph, the core, the held-out set and the stratum COMPLETELY
FIXED, and vary ONLY the vector each word carries. If bridged RETENTION rises when the target
space gains a channel the brain has and we lack, the target space was the limit. If retention is
flat across all four spaces while each space's own known-answer arm passes, the mechanism is the
limit and the target space is exonerated.

**The one variable is the TARGET SPACE.** Edge set, core membership, held-out membership, stratum,
scorer form (L2-normalise then plain cosine), bootstrap seeds and permutation counts are
byte-identical across arms.

## D1. STRATUM DISCIPLINE -- the hardest constraint, and it changed the design

**Rule.** The entire experiment runs on the INTERSECTION stratum where EVERY space is defined for
BOTH SimLex endpoints AND for every bridge neighbour used. **Zero-fill is BARRED.**

**Measured consequence.** The 15-dim intersection shrinks the AoA<=6.0 core from **2,838 to 1,711**
words (60.3% retained) and the SimLex both-endpoint pool from 999 to 977 pairs.

```
|Lancaster| 39,707   |Concreteness| 39,954   |Warriner| 13,905
S12 (12-dim vocab) = 39,705      S15 (15-dim vocab) = 13,374   shrink 0.337
AoA<=4.0  core_12=  523  core_15=  296  retained 0.566
AoA<=5.0  core_12= 1486  core_15=  858  retained 0.577
AoA<=6.0  core_12= 2838  core_15= 1711  retained 0.603
AoA<=8.0  core_12= 6728  core_15= 4222  retained 0.628
```

**A SMALLER CORE MEANS FEWER BRIDGE NEIGHBOURS, WHICH HURTS THE BRIDGE INDEPENDENTLY OF SPACE
QUALITY.** Therefore **every arm, including the 12-dim incumbent, must run on the intersected core
of 1,711** -- not on its own 2,838.

**And therefore, stated in the prereg in advance: the 8.2% retention figure MAY NOT BE IMPORTED.**
It was computed on a different stratum with a different core. TS1 must RE-EARN its own baseline
inside this cell. Importing 8.2% across strata is exactly the cross-population error that produced
the retracted +0.2285 and the retracted 0.073 lift cost.

1,711 is still O(10^3) and therefore still the right order of magnitude for the biological early
grounded core. The shrink is a cost, not a disqualification.

**DESIGN GATE BEFORE DISPATCH.** Measure the actual bridged stratum n on the intersected core and
graph. The sibling got n=394 on the 12-dim core. **If the intersected n falls below ~250, the
primary is UNDERPOWERED BY CONSTRUCTION and must be reported as such rather than run and banked as
a null** -- a Spearman CI half-width is ~1.96/sqrt(n-3), so 0.099 at n=392, 0.124 at n=250, and
0.176 at n=125. An underpowered primary is how a real effect gets banked as a null.

## D2. THE ARMS

**Target-space arms -- the only thing that varies:**

| arm | space | role |
|---|---|---|
| **TS1_CURRENT_12** | Lancaster11 + `Conc.M` | INCUMBENT; re-earns its own retention baseline on this stratum |
| **TS2_PLUS_AFFECT_15** | TS1 + Warriner V/A/D | **PRIMARY TREATMENT.** Adds the AFFECTIVE block (Binder), a separable subsystem with its own substrate. **The CHANNEL is PINNED as a semantic block; the CHOICE of VAD as its 3-dim operationalisation is OURS-INVENTION-UNDER-TEST.** |
| **TS3_AFFECT_ONLY_3** | Warriner V/A/D alone | DISSOCIATION. If bridged TS3 matches bridged TS2, sensorimotor contributes nothing under bridging -- a different and important finding |
| **TS4_WIDER_UNINFORMATIVE_23** | TS1 + 11 Lancaster rater-SD columns | **THE DECISIVE NEGATIVE CONTROL.** Same magnitude of widening, same source file, no new channel, measured ceiling gain ~0. **If TS4 raises bridged retention as much as TS2, "more dimensions" is the mechanism, the affect story is REFUTED, and the direction dies.** An unwary design omits this arm; without it the experiment cannot fail in the direction that matters. |

**Per-space arms -- every target space gets all five:**

- **K1_OWN_NORMS** -- KNOWN-ANSWER. The word's own hand-rated code in that space. Establishes that
  space's ceiling on this stratum and licenses the instrument. **G0 gate: if K1 does not clear THAT
  SPACE's floors CI-separated on a given stratum or POS sub-stratum, every arm on that
  space/sub-stratum is POWER_INSUFFICIENT, NEVER FAIL.** Applied per space AND per POS. This is the
  rule that made the sibling's verb and adjective numbers unreadable and it must not be relaxed.
- **K2_ORACLE_BRIDGE** -- SECOND KNOWN-ANSWER, **uses NO graph**. Held-out word takes the code of
  the CORE word with the highest GOLD similarity (self, spelling variants, and its own SimLex
  partner all excluded). Separates "the arithmetic of bridging in this geometry" from "our
  relations".
- **B1_BRIDGE_MEAN** -- THE FIXED TREATMENT. Unweighted mean of the codes of the held-out word's
  d=1 in-CORE neighbours, identical edge set across arms. Additive per Baron & Osherson 2011
  [additivity PINNED]; the specific transformation is OURS.
- **N1_MATCHED_REWIRE** -- NULL. Degree-preserving AND log-corpus-frequency-band-matched edge
  shuffle (configuration model), 5 seeds, floor = **MAX DRAW, never the mean**.
- **N2_RANDOM_TARGET** -- SECOND NULL. Bridge to a uniformly random CORE word, 5 seeds, max draw.

**They fail independently.** K1 fails if the SPACE cannot hold meaning on this stratum. K2 fails if
the GEOMETRY cannot carry a bridge even with a perfect neighbour. N1/N2 fail if any bridge to any
core word scores, i.e. if the effect is topical clustering. **B1 failing while K1 and K2 pass and
N1/N2 sit at zero isolates OUR EDGE RULE.** Four different causes, four different detectors.

## D3. THE FLOORS

**A gate is a CI-separated margin over `max(orthographic, frequency, scramble)` on the identical
scorer / n / pool / gold. Never a bare number.**

- **F_ORTHOGRAPHIC** -- character-trigram cosine between the two SimLex spellings.
  **SPACE-INDEPENDENT** -- it never touches the codes, so on a fixed stratum it is **ONE number
  shared by all four target-space arms.** State that explicitly, so nobody computes it four times
  and reports four bootstrap-noise variants as four different floors.
- **F_FREQUENCY_HARDENED** -- max over **all four** channels (`FREQ_NEG_ABS_DIFF`, `FREQ_SUM`,
  `FREQ_MIN`, `FREQ_MIN_OVER_MAX`) on the same 64MB simplewiki budget. Also **space-independent**.
  All four are required: the auditor's finding that two of three "clearing" arms in
  `calibrated_floor_verdict_v1` were not CI-separated from a frequency channel is why this is not
  optional.
- **F_SCRAMBLE_PERM_P95** -- **SPACE-DEPENDENT, MUST BE RECOMPUTED PER SPACE.** Permute the
  assignment of codes to words within that space, recompute rho, take the p95 of the permutation
  distribution; take the HIGHER of row-permutation p95 and gold-permutation p95. `N_PERM >= 2000`
  at full. **Permutation-calibrated, NOT a max over a handful of seed draws.** A 15-dim space has a
  different scramble distribution than a 12-dim one, and reusing the 12-dim floor for the 15-dim
  arm would hand it a free pass.

**The bar per arm:** paired-bootstrap margin over `max(the three)` on the identical stratum; PASS
only if the 95% CI of the margin excludes zero. **Report the per-floor decomposition too, because
the highest POINT floor is not always the hardest to separate from.**

## D4. THE DECIDING QUANTITY

**PRIMARY: RETENTION = rho(B1 in space S) / rho(K1 in space S), and the PAIRED bootstrap CI on the
DIFFERENCE IN RETENTION BETWEEN SPACES, using a shared resample index.**

Why retention and not raw rho: a wider space may raise the ceiling AND the bridged score together.
Raw bridged rho cannot distinguish "the bridge transmits more" from "everything went up". Retention
normalises by that space's own ceiling.

**But report BOTH.** The raw margin over the floors answers the Phase-2 GATE ("does a bridged word
carry meaning at all"). Retention answers the DIAGNOSTIC question ("is the space or the mechanism
the limit"). Different questions; both numbers appear whatever the verdict.

**Report separately, never averaged in:** the IDENTITY axis per space (distinct-code fraction, mean
pairwise cosine, recoverability). The sibling found identity SURVIVES at 96.1% while structure does
not -- a real dissociation that must not be averaged away.

## D5. HOW IT DECIDES -- both outcomes informative

| outcome | reading |
|---|---|
| retention RISES in TS2 vs TS1, paired CI-separated, **and TS4 does NOT rise** | **THE TARGET SPACE WAS THE LIMIT.** The bridge transmits meaning; it had nowhere to put the part of meaning verbs and adjectives live in. Next fidelity step is MORE SPOKES (social, event/temporal), not a different operator. |
| retention FLAT at ~8% in ALL FOUR spaces while K1 clears in each | **THE MECHANISM IS THE LIMIT and the target space is EXONERATED.** Next step is the EDGE RULE -- untyped co-participation replaced by ROLE-TYPED relations via `extract_predicates_v62` and `hdlab/thematic_role_labeler.py`, both owned, both never fed into a bridging graph. This is the move the sibling cell already pre-registered. |
| **TS4 rises as much as TS2** | **DIMENSIONALITY PER SE is doing the work.** The affect story is REFUTED and the direction is dead. |
| retention rises but the raw margin still does not clear the floors | MIDDLE_BAND, not a pass. The space helps and is not yet sufficient. |
| K1 fails its own floors in a space or on a POS sub-stratum | every arm on that space/sub-stratum is **POWER_INSUFFICIENT, NEVER FAIL**. |

## D6. THE POS FALSIFIER, AND ITS HONEST POWER PROBLEM

**Pre-registered prediction.** From the ceiling diagnostic, the affect gain must be CONCENTRATED in
V and A and near-zero in N (raw N delta was +0.0253, not separated). **If the bridged retention
gain is UNIFORM across POS, the affect channel is not doing what the biology says, and the result
is a topical artefact -- report it as a MECHANISM FAILURE even if the headline rises.**

**The problem, stated in advance rather than discovered afterwards.** The sibling's bridged stratum
had V=86 and A=49 and **both failed their own G0**. The intersected stratum will be smaller. So the
POS falsifier is likely to be POWER_INSUFFICIENT again, and pretending otherwise would bank a null
on an undecidable comparison.

**The fix, and it is cheap.** SimVerb-3500 is 3,500 VERB pairs with human similarity ratings. It is
**not on disk** -- `data/encoder_eval_benchmarks/` holds only `simlex999.txt` and
`wordsim353_combined.csv`. **A GOLD SET IS A RULER, NOT A MEANING SOURCE**; acquiring it does not
touch the no-external-model-in-the-runtime-path invariant in any way, and it is the difference
between a decidable verb falsifier and another POWER_INSUFFICIENT. **Recommend acquiring it before
this cell runs.** If it is not acquired, state in the prereg in advance that the verb sub-stratum is
expected to be undecidable, and do not report its number as a FAIL.

## D7. PRE-REGISTERED PROBABILITIES

Standing lit-scan calibration penalty applied: deflated 0.15-0.25, novel synthesis capped at 0.50.

| claim | P |
|---|---|
| `K1` clears its floors in TS1 on the bridged stratum | 0.80 |
| `K1` clears its floors in TS2 on the bridged stratum | 0.75 |
| **TS2 bridged RETENTION exceeds TS1 bridged retention, paired CI-separated** | **0.35** |
| TS4 (uninformative widening) shows NO retention gain -- the control behaves | 0.70 |
| **ANY space's B1 clears `max(floors)` CI-separated (the Phase-2 gate itself)** | **0.20** |
| the POS falsifier is DECIDABLE at all (verb sub-stratum passes its own G0) | 0.30 without SimVerb / 0.60 with |

**Basis for the low primary:** the sibling's B1 sat at **-0.0615 BELOW** the scramble floor. A
+0.10 ceiling gain does not obviously close a -0.06 deficit, and the nearest prior art
(`grounding_snowball`) HALVED between smoke and full. 0.20 is what the priors support, not
pessimism.

## D8. WHAT THIS DESIGN DELIBERATELY DOES NOT DO

- No **zero-fill** of missing norms -- barred; a documented artefact; intersection is the honest
  route.
- No **import of the 8.2% baseline** across strata.
- No use of **`grounded_similarity()`** as the scorer -- it saturates 76.2% of SimLex pairs onto
  two values. Use the raw vector, L2-normalise, plain cosine.
- No **wiring decision.** This cell answers a diagnostic question; WIRE-or-SHELVE is a separate act
  at land time.
- No **pretrained co-occurrence table** in any arm except an explicitly labelled CEILING REFERENCE
  with no verdict weight.
- No change to the **bridging operator, the graph, or the core cut** -- held fixed by construction,
  which is the entire point.

## D9. COSTS -- state these before anyone reads this as "wire VAD in"

1. **VAD is another EXTERNAL HAND-RATED norm set.** It changes the target space; it does **not**
   solve the scaling problem that motivates Phase 2 in the first place. Hand-rating still does not
   scale. **This drill does not rescue Phase 1; it re-scopes Phase 2's landing space.**
2. It costs a **2.97x vocabulary shrink** (39,705 -> 13,374) and a **40% core shrink**
   (2,838 -> 1,711).
3. The **adjective** result (+0.34) is partly a SimLex-sample property: SimLex adjectives are
   heavily valenced (*happy/sad*, *good/bad*), so valence has an unusually easy job there. **The
   VERB result (+0.12 raw, +0.16 z-scored) is the more trustworthy and the decision-relevant one.**
4. **NO FLOORS were computed in the diagnostic.** The floors may rise too. Nothing in Part C has
   cleared the standing bar and nothing in Part C is a result.

---

# PART E -- WHAT I COULD NOT VERIFY

- **The actual bridged stratum n on the intersected core.** Not measured -- it needs the graph
  build and I was scoped to drill and design only. **It is the design gate and must be measured
  before dispatch.**
- **Whether the affect channel is BRIDGEABLE at all.** A word's thematic neighbours may predict its
  sensorimotor profile but not its valence, or the reverse. That is precisely what the cell
  measures and it cannot be known in advance. **A ceiling gain is not a retention gain.**
- **Binder-65 SimLex overlap** -- unmeasurable, the file is not on disk.
- **ATOMIC v4 and CSKG coverage of the SimLex vocabulary** -- files present, not decompressed or
  indexed this pass.
- **A full `experiments/` and `preregs/` keyword sweep** -- the repo-wide `grep` timed out at 2
  minutes (exit 143). Dedup coverage is `hdlab/` + the capability registry + the substrate KB.
- **Generalisation of the power-law dimensionality result to SEMANTIC cortex.** The human
  scale-free measurement is on VISUAL cortex; Stringer is mouse V1. I found no semantic-cortex
  equivalent and am not claiming one. **[UNPINNED]**
- **The citations in Part A were retrieved this pass and are POINTERS TO CHECK before any becomes
  load-bearing**, not a replication audit. Two areas are actively contested and flagged in the
  text: the exact dimensionality figure (method-dependent by construction), and the visual-to-
  semantic generalisation above.

---

# PART F -- THE READING, PER THE STANDING FRAME

The brain grounds new word meanings from a small sensory core plus experience. **The capability is
DEMONSTRATED.** Everything above is a fact about OUR implementation:

- our LANDING SPACE covers **two of the brain's seven semantic blocks**;
- the block it is missing is the one **verbs and adjectives lean on**, which is exactly where our
  numbers fail;
- our EDGE RULE is untyped co-participation where the brain's thematic relations are **role-
  structured**;
- and our target space's own authors document it as **not representing thematic structure**, which
  is the channel we just spent a cycle building.

Four named divergences, each with a build target, **none of them a ceiling.** The next fidelity
step is not a different operator and not a threshold move -- it is **more spokes and typed edges**,
and the experiment in Part D is designed to tell us, in one run, which of those two to do first.
