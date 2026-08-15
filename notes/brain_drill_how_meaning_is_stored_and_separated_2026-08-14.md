# Brain drill: how meaning is STORED and how near-identical meanings are SEPARATED

**Filed:** 2026-08-14 (late). **Author:** auditor (AUDIT-ONLY role; no cell authored, nothing wired,
no live-path change, no experiment run).
**Answers:** `notes/PLAN_NEXT_12H.md` step **1-4h — DRILL THE BRAIN MECHANISM. BUILD NOTHING.**
**Form required by that step:** per element, the actual operation with a citation, plus **SHAPE /
POSITION / METRIC**, then OUR gap, then what a faithful version changes in our storage.

> **HONESTY RULES OBEYED HERE** (inherited from `notes/ORGAN_MAP.md` §0 and `CLAUDE.md`):
> **UNPINNED is an answer.** Where the literature does not pin the operation, this note says
> UNPINNED and stops. No equation is invented and dressed as biology.
> **Per-claim evidence tags are PRESERVED** (`[ESTABLISHED]` / `[CONTESTED]` / `[SINGLE-STUDY]` /
> `[UNRESOLVED]`) exactly as the underlying scans wrote them, per
> `notes/research_persistence_policy_2026-08-13.md` §1 — a synthesis that drops the tags launders
> a contested claim into settled fact, and that has already happened once.
> **Notes go stale (CLAUDE.md evidence discipline §4):** every load-bearing OUR-SIDE number below
> was re-verified off `metrics.json` today; brain-side claims are cited as "as scanned on
> 2026-08-13" where they were not re-fetched.

---

## 0. HOW I ENUMERATED, AND WHAT I FOUND (an absence claim requires an enumeration)

**Method.** `ls -lt --time-style=+%Y-%m-%dT%H:%M` on the ABSOLUTE path
`D:/AI/hd-instrument/notes/`, full listing sorted by mtime, then the same listing with
`grep -v watchdog_ping` to remove the 10-minute heartbeat files that dominate the head of the list.
Also `ls -lt` on `D:/AI/hd-instrument/data/literature_cache/` and on the transient task directory
`C:/Users/marsh/AppData/Local/Temp/claude/D--AI/139818eb-.../tasks/`.

**Result of the enumeration — a process finding, not a footnote:**

| observation | evidence |
|---|---|
| Newest **non-watchdog** note today: `orthographic_floor_vet_and_rebaseline_2026-08-14.md`, **17:37** | `ls -lt` on `notes/` |
| Watchdog pings continue to **19:59**; local clock at enumeration **20:05** | same listing; `date` |
| `data/literature_cache/index.jsonl` last written **2026-08-13T19:03**, 65 rows | `ls -lt`, `wc -l` |
| So **NO note and NO cache row was written by any agent between 17:37 and 20:05** | the two listings above |

**Conclusion: the three literature drills dispatched this evening produced ZERO artifacts on disk.**
Three agent generations wrote nothing. This is stated as an enumeration (a full mtime-sorted
directory listing over the relevant window), not as a keyword search that failed to hit.

**And they should not have been dispatched at all.** `notes/research_persistence_policy_2026-08-13.md`
§2 created a standing **CHECK-BEFORE-YOU-SCAN** gate one day earlier, for exactly this reason. The
material was already on disk — see §7, "This drill was answerable from disk".

**Queries run, per that gate:**
- `.venv/Scripts/python.exe tools/director_kb_query.py "perirhinal conjunctive coding feature
  ambiguity within-neighbourhood separation"` — returned **no output** within a 100 s timeout.
  Recorded as INCONCLUSIVE, **not** as "nothing indexed": the KB has known freshness and lock
  defects documented in `research_persistence_policy_2026-08-13.md` §6, and an empty result from a
  tool with a known silent-failure mode is not evidence of absence.
- `.venv/Scripts/python.exe tools/literature_cache.py find --keyword perirhinal` -> `NOT CACHED`.
  Same for `--keyword conjunctive`. `--keyword sparse` -> **4 cached rows** (CLS 1995,
  Quian Quiroga 2005 concept cells, and two others). So the cache genuinely has the sparsity
  literature and genuinely lacks the perirhinal literature.
- Content enumeration for the perirhinal thread: `Grep` for
  `Bussey|Saksida|Barense|Cowell|representational.hierarch` across `notes/` — 8 hits in 4 files.

---

## 1. OUR SIDE — WHAT WE ACTUALLY STORE (re-verified off disk today, not taken from a brief)

**The storage object.** `hdlab/reading_grounding_loop.py:447` `class ConceptSpace`, own docstring:

> "Running per-lemma context-vector accumulator (**raw, un-quantized sums**)."

with state `self._sums: Dict[str, np.ndarray]` (`:458`). The experiment that produces the headline
number describes its own construction the same way (`experiments/exp_grounding_readout_known_answer_v1.py:371`):

> "The substrate's OWN anchor construction: hdlab ConceptSpace **accumulating** hdlab
> `context_vector_masked` over each lemma's PROFILE sentences. No new mechanism."

**So the Director's framing is confirmed on disk: one dense vector per word, built by SUMMING the
vectors of co-occurring words.** `d = CTX_D = 256`, n = 5491 anchors.

**Crowding** — `data/exp_codebook_geometry_precheck_v1/metrics.json`, verdict
`NEAR_DUPLICATES_NOT_THE_DEFECT`, live codebook n=5491 d=256:

| variant | median NN cosine |
|---|---|
| `RAW_GRADED` | **0.4637** |
| `SIGNED` | **0.3516** |
| `CENTERED` | 0.4583 |
| `ZCA_WHITEN` | 0.3526 |
| `NULL_RANDOM` | **0.2264** |

`frac(NN >= 0.99) = 0.0000` against a null of `0.0000` — **zero near-duplicates**, so a dedup pass
has nothing to remove. Max pair 0.8567 (`sympathetic`/`parasympathetic`).

> 🔴 **FRAMING CORRECTION (auditor, symmetric-anti-negativity — this one cuts AGAINST the
> alarming reading).** The brief quotes "median nearest-neighbour similarity **0.4637** vs
> random-null 0.2264". That pair is real but it is the **`RAW_GRADED`** variant. **The LIVE
> comparator path is the SIGNED one** (`canonicalize_fast:736` `nb = np.sign(new_raw_sum)`), whose
> median NN is **0.3516** — excess over null **+0.125**, not **+0.237**. Quote whichever you mean,
> but name the variant. Note also `STATUS_LESSONS.md` item 30's own warning: the top pairs are a
> **MIX** of genuine paradigmatic sisters (`sympathetic`/`parasympathetic` 0.857,
> `guanine`/`cytosine` 0.810) **and of junk with no semantic relation at all**
> (`anal`/`notochord` 0.846, `chocolate`/`fraudulent` 0.789). Quoting only the first group makes the
> crowding look purely taxonomic. It is not.

**The floor.** `data/exp_orthographic_floor_vet_v1/metrics.json`, n=4000, 5491 anchors,
`a1_base_reproduces_c3_headline_exactly = True`:

| arm | hit@1 | 95% CI | median rank |
|---|---|---|---|
| `A1_BASE` (ours) | **0.0480** | [0.04125, 0.05475] | 37.0 |
| `A6_TRIGRAM_ONLY` (spelling alone, zero substrate signal) | **0.0870** | [0.07825, 0.09600] | 37.0 |
| `A7_PREFIX_ONLY` | 0.05875 | [0.05150, 0.06600] | 33.5 |
| `A8_MAXORTHO` | 0.06100 | [0.05374, 0.06850] | 43.0 |

`d_A6_minus_BASE = +0.0390`, CI [0.02825, 0.05000], `ci_excludes_zero = True`. **CI-separated:
our `ci_hi` 0.05475 < trigram `ci_lo` 0.07825.** Confirmed as the brief states.

> **One nuance the headline hides, and it matters for the diagnosis.** `median_rank` is **37.0 for
> BOTH** `A1_BASE` and `A6_TRIGRAM_ONLY`. Spelling beats us **at the top-1 decision**, not at
> overall ranking quality. That is consistent with — and independent evidence for — the
> "paradigmatic neighbour" diagnosis: we put the right neighbourhood near the top and then pick the
> wrong member of it. A spelling channel breaks ties differently, not better-in-general.

---

## 2. (a) HUB-AND-SPOKE — modality spokes bound by an anterior-temporal hub

**THE OPERATION IS UNPINNED AS AN EQUATION.** This is the honest headline and it must not be
softened.

`[ESTABLISHED]` The framework: concepts are formed by a bilateral, transmodal **anterior temporal
lobe (ATL)** hub taking input from modality-specific "spoke" regions, producing representations
capturing cross-modal similarity structure not present in any single modality — grouping *dolphin*
with mammals rather than fish, which shape/habitat alone would not do (Lambon Ralph, Jefferies,
Patterson & Rogers, *Nat Rev Neurosci* 2017, 18:42-55).

`[ESTABLISHED, current formulation]` The hub is **not a simple similarity space and not a linear
averaging device**. It performs a deep, multi-step **nonlinear transformation with recurrent
feedback dynamics**, whose core operation is **pattern completion via a compact abstract "label"**
that feeds back onto shallower unimodal features (Jackson, Orban & Tiesinga, *Neurobiology of
Language* 2026, DOI 10.1162/NOL.a.220, synthesising Jackson, Rogers & Lambon Ralph, *Nat Hum Behav*
2021, 5:774+ and Tiesinga et al., *Sci Rep* 2023).

**Measured dynamics exist; a dynamical equation does not.** `[ESTABLISHED]` Decodable ~200 ms;
representational-geometry breakpoint ~473 ms; anterior-posterior electrode position predicts degree
of dynamic change **r²=0.73, p<0.002** (Rogers, Cox, Lu, Shimotake et al., *eLife* 2021,
10:e66276 — direct ECoG, 8 patients, 16-24 electrodes in left vATL, 1000 Hz, picture naming).
`[SINGLE-STUDY, load-bearing]` Flow VL->Tip at ~140 ms then recurrently back, with **backward
connections consistently stronger than forward** (Tiesinga et al., *Sci Rep* 2023; sEEG leads
3.5 mm apart vs ~2 cm in prior ECoG).

- **SHAPE.** A single, amodal, **graded, DENSE distributed** convergence code, **not** a symbolic
  lookup table and **not** sparse. Graded rather than uniform across ATL, with a bilateral
  centre-point in ventrolateral ATL and specialization radiating outward `[ESTABLISHED]` (Rice,
  Lambon Ralph & Hoffman, *Ann NY Acad Sci* 2015, 1359:84-97; Binney, Hoffman & Lambon Ralph,
  *Cereb Cortex* 2016, 26:4227-4241).
- **POSITION.** Downstream of modality-specific spokes; **upstream of and functionally separable
  from** the semantic CONTROL network (IFG + pMTG). The hub supplies the default graded
  representation; control biases retrieval over it.
- **METRIC.** Two concepts are similar in the hub to the degree they **share behavioural
  feature-norm features** — *wolf*/*coyote* close via shared "furry"/"predatory"/"wild". This is
  **directly verified in the target region itself**: Cox, Rogers, Shimotake et al., *Imaging
  Neuroscience* 2024 (PMC12224414), intracranial ECoG from human vATL during picture naming,
  Representational Similarity Learning against feature norms; graded encoding peaks 200-400 ms.
  **This is a CROSS-MODAL FEATURE-CORRELATION metric, and it is NOT linguistic co-occurrence.**

**In what sense does each spoke keep a separate ADDRESS?** Three converging facts, and one honest
limit:
1. `[ESTABLISHED]` **Damage dissociates by address.** Spoke damage -> modality-restricted deficit;
   hub damage -> pan-modality, category-general deficit (Patterson, Nestor & Rogers, *Nat Rev
   Neurosci* 2007, 8:976-987; Pobric, Jefferies & Lambon Ralph, *PNAS* 2007, 104:20137-20141 —
   1 Hz rTMS to left ATL slowed synonym judgment 9.9%, p<0.001, while **number tasks were completely
   unaffected**).
2. `[ESTABLISHED]` **The connection itself is load-bearing**, not the spoke alone: semantic-deficit
   severity correlates with **reduced hub-spoke white-matter connectivity** as well as with ATL
   atrophy (*Brain* 2020, "White matter basis for the hub-and-spoke semantic representation").
3. `[ESTABLISHED, mechanistic]` **The hub reactivates spoke features that were never presented** —
   pattern completion is the whole point of routing through it (Jackson 2021 / T23).
4. **Honest limit:** whether modality-specific information is *retrieved via* the hub (obligatory
   routing) or *accessible in parallel* is `[CONTESTED]` — the sharpest fault line in the field
   (embodied accounts: Meteyard et al., *Cortex* 2012; Pulvermüller, *TiCS* 2013). Also `[CONTESTED]`
   is **which ATL subregion is the true convergence point** — fMRI/ECoG says ventrolateral VL,
   T23's higher-resolution sEEG says the pole tip; the 2026 review flags this as unresolved.
   And Huth/Gallant's continuous semantic-tiling (*Nature* 2016, 532:453-458) and
   Fernandino/Binder's distributed-experiential account (*J Neurosci* 2022, 42:7121-7136) are live
   `[CONTESTED]` challenges, treated by the 2024-2026 consensus as **complementary rather than
   refuting**.

**The only available equations belong to MODELS of the hub, not to the hub.** Jackson 2021 is a
recurrent ANN with **error-driven backprop-style learning**, 3 spokes, two hidden layers, ~1
shortcut per 9 indirect-route connections, trained on all 3x3=9 modality-pair tasks. **Do not
over-read this into "training is the right tool" — and equally do not claim the brain's model is
Hebbian.** `[ESTABLISHED]` One thing the architecture search DID settle: a **single shared
multimodal hub** beats multiple pairwise "demi-hubs", and demi-hubs are actively harmful because
they let the network bypass the hub (Rogers 2004 and Jackson 2021 independently).

**PINNED SUB-FACT worth keeping:** conceptual COMBINATION in left ATL is **approximately ADDITIVE**
(Baron & Osherson, *NeuroImage* 2011). This licenses our `sum` and indicts only what we do after it.

### OUR GAP (a)
`ORGAN_MAP.md` **B1**. Ours is `hdlab/lexical_similarity.py` — a **hand-authored** `CONCEPT_FEATURES`
dict of DOM/ROLE tag frozensets over ~230 concepts, bundled into an FHRR vector. Feedforward,
one-shot, **no recurrence**, and **UNWEIGHTED**: a tag shared by 8 concepts counts as much as a tag
shared by 1. Fidelity **WRONG-OP** — unweighted shared-feature overlap is the *precise inverse* of
the brain's privileging of distinctive features (see §5). It covers ~0.6% of vocabulary; the rest
falls through. **NO FLOOR — UNTESTED as an organ.**

**The deeper gap, and it is the one that matters:** the brain's hub metric is **cross-modal feature
correlation**. Ours is **text co-occurrence**. Per `drill_brain_atl_lexical_semantic_hub_2026-08-06.md`,
a text-only distributional method is honestly **building ONE spoke well, not the transmodal hub**.

### WHAT A FAITHFUL VERSION CHANGES IN OUR STORAGE
Not "add recurrence" — the hub's dynamical equation is UNPINNED and building one would be inventing
biology. The **pinned, actionable** changes are:
1. Store a concept as a **bundle over a FEATURE basis with separate addresses**, not a sum over
   co-occurring word tokens. The METRIC is pinned (feature-norm overlap, Cox 2024); only the
   dynamics are not.
2. **Do not build demi-hubs.** One shared hub; pairwise integrators are measurably worse.
3. Keep combination **additive** (Baron & Osherson) and fix the **normaliser** after it (§B2/§C1).

---

## 3. (b) SPARSE vs DENSE — and the trap in this element

**🚨 THE MOST IMPORTANT SINGLE CORRECTION IN THIS DRILL. The brief's premise — "SPARSE not dense" —
is HALF WRONG, and the half that is wrong is the half about the system we are actually building.**

`[ESTABLISHED]` **There are TWO coding regimes in two different systems and conflating them is a
trap** (`ORGAN_MAP.md` B4 names it as such):

| system | sparsity | source |
|---|---|---|
| **MTL / hippocampal concept cells** | **~0.2%** — fewer than 2x10⁶ of ~10⁹ MTL neurons per percept; each neuron fires to **~50-150** different concepts | Waydo, Kraskov, Quian Quiroga, Fried & Koch, *J Neurosci* 2006, 26:10232-10234 (1,425 units, 34 sessions) `[ESTABLISHED]` |
| **Neocortical semantic / IT object coding** | sparseness index **~0.2-0.3** — substantially **LESS sparse, more distributed** | Rolls/Treves-style lifetime/population sparseness `[ESTABLISHED directional, exact numbers vary by study/metric]` |
| **Temporal pole during semantic processing** | **~two-thirds of electrode populations active per single exemplar** — explicitly *distributed, not sparse* | Tiesinga et al., *Sci Rep* 2023 `[SINGLE-STUDY]` |

`[ESTABLISHED]` The neocortical semantic code is **dense, distributed, low-effective-dimensional** —
the first ~4 group principal components define a semantic space shared across subjects (Huth,
Nishimoto, Vu & Gallant, *Neuron* 2012, 76:1210-1224, 1,705 categories), with much larger nominal
attribute counts (~65 experiential attributes, Binder et al., *Cogn Neuropsychol* 2016, 33:130-174).

**So: the SEMANTIC HUB — the thing our anchor codebook is trying to be — is DENSE. Sparsity is the
EPISODIC/MTL regime.** `ORGAN_MAP.md` B4 states it flatly: *"Explicitly NOT sparse, NOT binary.
Sparse ~0.2% coding is the MTL regime (Waydo 2006) — a different system; conflating them is a trap."*
`[UNRESOLVED, flagged in the source scan]` A claimed "5-dimensional PCA-derived experiential space"
could **not** be confirmed and should not be cited. Separately pinned and **explicitly not to be
imported**: V1's power-law eigenspectrum (Stringer et al., *Nature* 2019, 571:361-365) — that is
early visual cortex, not semantic cortex.

**What sparsity buys, where it IS the right regime** `[ESTABLISHED]`: the sparse-associative capacity
law **p_max ~ C / (a · ln(1/a))**, C = recurrent connections per cell, a = active fraction (Treves &
Rolls, *Network* 1991, 2:371; *Hippocampus* 1994, 4:374). This is **superlinear in sparsity** —
driving `a` toward zero buys far more than proportional capacity, which is the formal reason DG/CA3's
~2-5% activity level is load-bearing rather than incidental. Contrast the DENSE Hopfield result
~0.14N with a **sharp catastrophic collapse** (Amit, Gutfreund & Sompolinsky 1987). Applied to real
CA3 parameters (C_RC ~12,000, a ~0.02-0.05) Rolls 2013 gets **p_max ~ 10⁴** — and the paper itself
flags this as an illustrative estimate under uncorrelated-random-pattern assumptions, **not a
measured biological count**.

Separating similar concepts is what **DG pattern separation** buys, and its causal evidence is
genuinely strong `[ESTABLISHED]`: Leutgeb et al., *Science* 2007, 315:961 (DG rate-remapping
decorrelates for SMALL changes, CA3 recruits non-overlapping assemblies for LARGE ones); Guzman
et al., *Science* 2016 (optogenetic DG silencing impairs discrimination of *similar* but not
*dissimilar* contexts); McHugh et al., *Science* 2007 (DG-specific NMDAR knockout fails separation
while CA3 completion stays intact — a genuine double dissociation). A precise and frequently-missed
point: **separation and completion are in TENSION** — pure Hebbian LTP alone improves completion but
DEGRADES separation; heterosynaptic LTD is required to keep separation high (O'Reilly & McClelland,
*Hippocampus* 1994, 4:661).

- **SHAPE.** Two regimes. Cortical semantic: dense, graded, low-effective-dim. Hippocampal/DG:
  sparse (~0.2% MTL; ~1-4% DG granule cells), expanded, decorrelated.
- **POSITION.** DG separation sits **BEFORE** CA3 storage (EC -> DG -> CA3, perforant path -> mossy
  fiber). It is a **write-time** transform of the KEY, not a retrieval mechanism.
- **METRIC.** Decorrelation / orthogonalization of similar inputs, and downstream
  storage-capacity-before-crosstalk. **`[CONTESTED]`** the precise separation metric —
  orthogonalization vs decorrelation vs spike-distance measures disagree (Yassa & Stark, *Trends
  Neurosci* 2011); and Quian Quiroga, "No Pattern Separation in the Human Hippocampus," *TiCS* 2020
  disputes whether it exists in humans at all, with a published 2021 rebuttal.
- **UNPINNED:** the nonlinearity type, expansion ratio and threshold (`ORGAN_MAP.md` D1).

### OUR GAP (b)
`ORGAN_MAP.md` **B4**: our context path is **256-dim bipolar ±1**, and **2,377-5,491 concepts in a
256-dim space** is under-capacity. Fidelity **WRONG-OP (binary where the brain is graded) AND
under-capacity**. The measured lever is large and was earned against floors:
`data/exp_capacity_ceiling_near_far_v1` **MIDDLE_BAND_CAPACITY_PARTIAL**, n=4000 — NEAR-pair accuracy
at d=256/1024/4096 is QUANT [0.6395, 0.7030, 0.7380], GRADED [0.6980, 0.7495, 0.78225]; crosstalk
falls **exactly as 1/√d (0.0498 / 0.0249 / 0.0125)**. **16x the dimensionality buys +0.0843 — more
than any mechanism change this program has produced.** Floors in-cell 0.49775/0.5095/0.4845 against
chance 0.50, and between-projection-draw sd **0.0090** reported alongside.

### WHAT A FAITHFUL VERSION CHANGES IN OUR STORAGE
**Do NOT sparsify the semantic anchor codebook — that would be copying the wrong organ.** The
faithful changes are: (i) make the code **graded, not signed** (the brain's cortical code is graded;
ours throws the gradation away — see §5); (ii) **raise d**, which is the pinned capacity lever;
(iii) reserve DG-style sparsification for the **episodic/key** path, where it IS the brain's
operation, applied **at write time to the key**.

---

## 4. (c) CONJUNCTIVE CODING in perirhinal cortex — the closest published match to our exact failure

**Honest scoping statement first.** The **representational-hierarchy / feature-ambiguity** account
(Bussey, Saksida, Murray, Cowell, Barense) is **PRESENT ON DISK ONLY AS CITATIONS**, not as a
full-text-verified scan. `tools/literature_cache.py find --keyword perirhinal` returns **NOT
CACHED**. `Grep` across `notes/` for `Bussey|Saksida|Barense|Cowell|representational.hierarch`
returns **8 hits in 4 files**, all citation-level. **This element is therefore the ONE place in this
drill where a genuinely new literature pull would add something** — see §7. What follows is what
disk actually supports, at the confidence disk actually supports.

**What IS on disk and IS verified:**

`[ESTABLISHED]` **Perirhinal/ATL pattern similarity tracks INTEGRATED feature CONJUNCTIONS, distinct
from more posterior regions that code features INDIVIDUALLY** — Clarke & Tyler, *J Neurosci* 2014,
34:4766; Erez, Cusack, Kendall & Barense, *eLife* 2018, 31873. (Cited in
`drill_brain_atl_lexical_semantic_hub_2026-08-06.md:48`; verified via search, **not** full-text
fetched — flagged there and flagged here.)

`[ESTABLISHED, actively maintained line]` **Perirhinal damage specifically disrupts sensitivity to
feature-CORRELATIONAL STATISTICS, not merely individual feature loss** — Taylor & Devereux, "The
perirhinal cortex and conceptual processing: Effects of feature-based statistics following damage to
the anterior temporal lobes," *Neuropsychologia* 2015. This is the sharpest available statement that
perirhinal computes something *over feature combinations* rather than over features.

`[ESTABLISHED]` Perirhinal Hebbian conjunctive coding as the biological evidence for hub-spoke —
Bussey & Saksida, "Memory, perception, and the ventral visual-perirhinal-hippocampal stream:
thinking outside of the boxes," *Hippocampus* 2007, 17(9):898-908
(`research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md:323`).

**Why this is the closest published match to our exact failure.** The feature-ambiguity account, in
the form disk supports, says: when two things **share most of their individual features** and can be
told apart only by the **particular COMBINATION** they occur in, individual-feature codes are
*ambiguous* and a **conjunctive** representation is required to disambiguate them. That is
*precisely* our defect: `sympathetic` and `parasympathetic` occur in nearly identical sentences, so
their **bags of individual co-occurring words are nearly identical**, and no amount of better
weighting over a bag of individuals can separate them, because the discriminating information is not
in any individual feature — **it is in the conjunction.**

- **SHAPE.** A representation of **feature CONJUNCTIONS**, not of features. `[ESTABLISHED]` The
  brain does **not** do a literal dense outer-product over full-width vectors: each DG/CA3 cell
  fires for a **random, low-order conjunction of a HANDFUL of input features** (O'Reilly &
  McClelland 1994). Literal tensor-product binding's dimensionality blowup is explicitly flagged in
  the VSA literature as impractical; **the brain's solution is sparsity, not a bigger tensor.**
- **POSITION.** At the **apex of the ventral visual stream**, at the perirhinal/ATL end —
  i.e. *after* individual features are extracted posteriorly, and adjacent to the hub. Conjunctions
  are formed at the TOP of the hierarchy, not at the input.
- **METRIC.** Disambiguation under **feature ambiguity**: the benefit appears exactly and only when
  individual features are shared and the conjunction is diagnostic.
- **UNPINNED:** the **binding operation itself**. `ORGAN_MAP.md` E1 records it as *"UNPINNED and
  actively CONTESTED three ways"* (see §6). Nothing on disk pins the algebra by which perirhinal
  forms a conjunction. **PINNED adjacent fact:** TEM's hippocampal conjunctive code is a **product**,
  `p = g ⊗ x` (Whittington 2020) — but that is a hippocampal model, not a perirhinal measurement.

`[ESTABLISHED]` **The one CA3/CA1 honesty flag that must travel with this:** the source scan could
**not** find a single decisive experiment showing a CA3/CA1 cell's firing is *literally the algebraic
conjunction* of an item signal and a context signal, as opposed to merely correlating with both.
Treat "CA3/CA1 = conjunction site" as well-supported but **model-inferred**, not a directly-proven
single-cell fact.

### OUR GAP (c)
**We have NO conjunctive stage at all on the live path.** We store a sum of individual co-occurring
word vectors — the **additive** geometry, which is the arm that loses in our own floored result:
`exp_interference_avoidance_conjunctive_vs_additive_v1`, **CONJUNCTIVE 1.000 vs ADDITIVE 0.273** at
M=256, *and STATUS.md notes in terms that the additive arm **IS our bag geometry***.

### WHAT A FAITHFUL VERSION CHANGES IN OUR STORAGE
Store, alongside (not instead of) the bag, a **low-order conjunction code**: a **sparse, random,
low-order** conjunction of a handful of co-occurring features — explicitly **not** a dense
outer-product, which the literature flags as the impractical version the brain does not use. The
capacity argument is exactly why it should help our failure mode: **bundling many SPARSE
near-orthogonal member codes crosstalks far less than bundling many DENSE correlated ones**
(`hdlab/dg_pattern_separation.py` docstring, citing Willshaw 1969; Treves & Rolls 1991).

---

## 5. (d) DISTINCTIVE vs SHARED features — intercorrelation structure and weighting

**This element is the best-pinned in the whole drill, and it says our current weighting is
BACKWARDS.**

`[ESTABLISHED]` **Distinctive features hold a PRIVILEGED status**: features present in few concepts
are computed/verified **faster** and weighted **more diagnostically** than shared features in healthy
processing — the discriminating feature between near-neighbours is normally the *privileged,
fast-access* feature, not a marginal one (Cree, McNorgan & McRae, *J Exp Psychol: LMC* ~2006,
PMC3226832).

`[ESTABLISHED framework, still current]` **Tyler & Moss's Conceptual Structure Account.** Two
statistical properties of a feature determine its fate:
- **DISTINCTIVENESS** — how few concepts share it (exactly the near-neighbour-discriminating
  property);
- **CORRELATIONAL STRENGTH** — how reliably it co-occurs with the concept's *other* features.

**The central claim, and it is the mechanism behind our failure:** for **living things**, distinctive
features tend to be **WEAKLY CORRELATED** with the concept's other features (a zebra's stripes do not
predict its other properties). This makes them **computationally FRAGILE**, because **attractor
settling is driven by correlational structure**, so features with few correlational supports are the
first casualties of any noise or damage. For **artifacts**, distinctive form-features are usually
tightly correlated with function, hence comparatively robust. (Tyler & Moss, *TiCS* 2001; Taylor,
Devereux & Tyler, *Lang Cogn Processes* 2011, 26(9); Devereux, Tyler, Geertzen & Randall, *Behav Res
Methods* 2014 — the CSLB norms.)

`[ESTABLISHED]` The **degradation signature** confirms it from the lesion side: in semantic dementia,
(a) features shared across many category members are **most robust**; (b) **atypical exemplars and
their distinctive features degrade FIRST** because they lack shared-feature support; (c) producing
**simultaneous over- and under-generalization** — "a penguin is like a duck" — i.e. **drift toward
the category PROTOTYPE**, not clean loss (Rogers, Lambon Ralph, Garrard et al., *Psychol Rev* 2004,
111:205-235; Warrington 1975 for the original attribute-first report). A camel's hump is lost before
"four legs".

- **SHAPE.** A **graded synaptic weight distribution** over features, in which the weight is a
  function of the feature's frequency statistics (distinctiveness) and its correlational embedding.
- **POSITION.** Built **across encounters**, by slow replay-driven cortical consolidation — i.e. at
  ACCUMULATION time, not at comparison time (CLS: McClelland, McNaughton & O'Reilly 1995).
- **METRIC.** A feature's fate = **DISTINCTIVENESS × CORRELATIONAL STRENGTH**, both frequency
  statistics.
- **🔴 UNPINNED — and this is a real gap in the neuroscience, not a gap in our reading.** *"The
  distinctiveness WEIGHT FUNCTION is UNPINNED — nothing in the literature says by how MUCH a rare
  feature is up-weighted"* (`ORGAN_MAP.md` B3). The direction is pinned; the function is not. **Our
  one instantiation of a guess (log-IDF) was refuted** — see below.

**Two `[CONTESTED]`/`[UNRESOLVED]` neighbours that must not be laundered:**
- **Whether the cortex separates near-synonyms at all is NOT SETTLED.** *"No direct single-unit or
  fine-grained RSA study of near-synonym separability in cortex was located — this is a genuine
  evidence gap."* The two live hypotheses (graded space -> separable-but-close vs hub-convergence ->
  collapsed) **have not been directly adjudicated**. Best indirect evidence is Pereira et al., *Nat
  Commun* 2018, 9:963, whose decoder distinguishes "even semantically similar sentences"
  `[ESTABLISHED but indirect]`.
- **Hippocampal pattern separation for SEMANTIC near-neighbours** is `[SINGLE-STUDY, actively
  contested]`: "The human hippocampus can pattern separate memories by meaning," *PNAS* 2026, DOI
  10.1073/pnas.2603114123 — high-resolution subfield MRI, adjective-noun phrases re-presented with a
  semantically-similar adjective substituted; reports orthogonalization as a function of **semantic**
  similarity. Most on-target finding in the whole corpus for our question — **and essentially
  unreplicated, sitting atop the unresolved Quian Quiroga 2020 dispute.**

**A strong engineering parallel, worth keeping** `[ESTABLISHED]`: standard word embeddings place
antonyms, synonyms and co-hyponyms all in close proximity **because they share local co-occurrence
frames** ("the water is hot/cold"). *"Distributional similarity is symmetric and context-frame-based,
but the semantic relations that matter are not distinguishable by symmetric co-occurrence statistics
alone."* The standard fix injects curated relation constraints — i.e. **exactly the kind of small-set
discriminating-relation information that CSA says the brain privileges.** **Our defect is the
textbook distributional defect, and the literature says co-occurrence statistics alone CANNOT fix
it.**

### OUR GAP (d) — the one with the sharpest, most specific finding
`ORGAN_MAP.md` **B1**: our hub is **UNWEIGHTED** — a tag shared by 8 concepts counts as much as a tag
shared by 1. Fidelity **WRONG-OP: "the precise inverse of the brain's privileging of DISTINCTIVE
features."**

`ORGAN_MAP.md` **B3** is worse, and it is the single most damning line in the map:
> **OURS:** `ConceptSpace.observe` — `self._sums[lemma] += ctx_vec`, a genuine graded accumulator,
> **correct** — then `anchor_matrix:450` returns `np.sign(...)` and `bundle:460` returns `np.sign(s)`.
> **"The graded quantity is built and thrown away one line before use. A dimension where 36 of 70
> encounters agreed becomes bit-identical to one where 70 of 70 agreed."** `freeze_graded():482`
> exists, **default OFF**. Fidelity: **RIGHT-OP-WRONG-PLACE. The information already exists in
> memory.**

**We compute the exact statistic the brain uses to weight distinctiveness, and then destroy it with
`np.sign` before anyone reads it.**

**And the honest counterweight, which stops this becoming a "just add IDF" story.** Every
per-dimension REWEIGHTING we have tried is null or harmful: **log-IDF null; global-field z-scoring
+0.0018; pool-inverse −0.011; contrast gain −0.0220** (`exp_task_local_normalisation_pool_v1`,
**HARD_FAIL_GAIN_HURTS**, d = −0.0220 CI [−0.0340,−0.0097], floors 0.4953/0.5065 scrambled, 0.4800
frequency). **The only thing that helped was REMOVING a per-dimension DESTRUCTION**
(`exp_graded_divisive_comparator_v1`, **HARD_PASS**, LIVE 0.6395 -> GRADED 0.6997, d=+0.0602 CI
[0.0440,0.0762], scrambled floors 0.4975/0.5065, frequency 0.4800). `ORGAN_MAP.md` C3 names the
mechanism unifying all four nulls: **with ~70 observations per concept in a 256-dim projection, the
dimensions with the largest anchor-difference are disproportionately the WORST-ESTIMATED.** That is
an **estimation-noise** statement, and **it points at capacity (B4), not at the weighting rule.**

### WHAT A FAITHFUL VERSION CHANGES IN OUR STORAGE
1. **STOP DESTROYING THE GRADED COUNT.** Keep `ConceptSpace._sums` graded through to comparison.
   This is not a new mechanism, not a new equation, and not an invented biology — the switch
   (`freeze_graded`, `ReadoutConfig(graded_query=True)`) **already exists and is default-OFF**, and
   turning it on is the only intervention in this family that has ever produced a floored gain.
2. **Do NOT hand-pick a distinctiveness weight function.** It is **UNPINNED** in the literature and
   four of our own attempts to guess it are null-or-harmful. Fix the estimator (capacity) first.
3. Weight distinctiveness **at ACCUMULATION time** (B3, the brain's position) rather than as a
   comparison-time reweighting (C3), which is where all four failures happened.

---

## 6. (e) ROLE BINDING — "the artery carries blood" vs "blood carries the artery"

**UNPINNED. Say it plainly: there is no settled equation in the neuroscience to be faithful to.**

`ORGAN_MAP.md` **E1**, verbatim:
> **BRAIN'S MATH: UNPINNED and actively CONTESTED three ways** — theta-gamma phase coding (Lisman &
> Jensen), conjunctive mixed selectivity (Rigotti & Fusi), tensor-product representations
> (Smolensky). **There is no settled equation to be faithful to.**
> **FIDELITY: UNSCORABLE** (brain math UNPINNED). *Recorded honestly rather than claimed SAME.*

**What IS pinned, and it is only the container, not the operation:** one theta cycle (~125 ms)
contains **~7 gamma sub-cycles (~17 ms each)**, one item per gamma slot, order encoded in theta-phase
progression (Lisman & Idiart, *Science* 1995, 267:1512; Lisman & Jensen, *Neuron* 2013, 77:1002;
Heusser et al., *Nat Neurosci* 2016, 19:1374). **The slot count and timing are pinned; the ENCODING
OPERATION is UNPINNED.** `ORGAN_MAP.md` E5 is explicit that the `Σ perm^k(x_k)` form is
**Kanerva/Plate HDC — OUR math imported as the analogue, not measured biology.**

**Two pinned ADJACENT facts, neither of which is a perirhinal or cortical role-binding measurement:**
- TEM's hippocampal conjunctive code is a **product**, `p = g ⊗ x` (Whittington 2020).
- LATL conceptual **combination** is **ADDITIVE** (Baron & Osherson 2011) — which *licenses our `sum`*
  and indicts only the normaliser after it.

**The theoretical lineage is real but it is COMPUTATIONAL, not measured** `[ESTABLISHED as
theory]`: Smolensky, *AI* 1990, 46:159 (tensor-product variable binding); Plate, *IEEE TNN* 1995,
6:623 and *Holographic Reduced Representation* 2003 (circular convolution + superposition + cleanup).
Rolls & Treves treat CA3 as a Hopfield-type associative memory, and a Hopfield net's stored
associations **are** mathematically a superposition of outer products — structurally the same object
as a rank-limited tensor-product VSA. Current state of the art, directly hippocampal: **Vector-HaSH**
(Chandra, Sharma, Chaudhuri & Fiete, *Nature* 2025) — entorhinal grid modules provide a fixed
low-dimensional **scaffold**, content is bound to scaffold states via plastic associative
projections, retrieval uses error-correcting attractor dynamics, explicitly built to give a
**graceful** capacity/fidelity tradeoff rather than the Hopfield memory cliff.

- **SHAPE.** UNPINNED. Three incompatible candidate shapes (phase code / mixed selectivity /
  tensor product).
- **POSITION.** UNPINNED for cortex. In the hippocampal models the bind precedes storage; in the
  theta-gamma account the slot structure is a working-memory buffer, not a long-term store.
- **METRIC.** UNPINNED. What is scorable is only what our *own* operation costs: the per-component
  complex normaliser costs **20-32% of d′** versus whole-vector L2 (near/random d′ 4.843 -> 6.030;
  near/disjoint-random 6.070 -> 8.959) — and the scope caveat is that those pairs come from the
  hand-authored lexicon, so this describes **what the OPERATION does to whatever structure exists**,
  not a capability.

### OUR GAP (e)
Unusually, **the binding operation is NOT our gap.** `ORGAN_MAP.md` E1: `hdlab/binding.py` — FHRR
bind = elementwise complex multiply; HRR bind = circular convolution via full FFT, unbind by
conjugate. **WIRED: YES. Composition mechanism VET-confirmed 4x — *given roles*. BLOCKS: nothing —
it works.**

**The gap is the INPUT and the ORACLE.** E1: *"The oracle role-key derivation has no mechanistic
analog — the least defensible part of the binding story."* Roles have to come from syntax (F3/F4),
and our own floored comparison says role-filler structure massively beats the flat bag *once roles
exist*: **FACTORED role/filler held-out 1.000 vs FLAT 0.003**
(`exp_role_filler_factorization_compgen_v1`); **PERMUTATION binding 1.0000 vs FHRR 0.0629** on
same-role collision (`exp_substrate_permutation_binding_multiocc_v2_full`).

### WHAT A FAITHFUL VERSION CHANGES IN OUR STORAGE
**Nothing, on fidelity grounds — and this is the finding.** Because the brain's operation is
UNPINNED and three-ways contested, **no change here can be justified as "more brain-faithful."** Any
change must be justified on our own measured terms (the three floored results), and must be labelled
as **our engineering choice, not biology.** Concretely: store a role-indexed code beside the bag, and
**do not claim brain fidelity for the algebra chosen**, only for the *presence* of role-sensitivity —
which the artery/blood asymmetry demands on logical grounds regardless of which circuit implements it.

---

## 7. THIS DRILL WAS ANSWERABLE FROM DISK (a process finding)

**Of the five elements, FOUR were fully answerable from material already on disk, and one was not.**

| element | already on disk? | where |
|---|---|---|
| **(a) hub-and-spoke** | **YES, fully** — incl. the 2026 mechanistic synthesis, the graded-hub dispute, the tiling/embodied challenges, and the model architecture search | `lit_scan_atl_hub_and_spoke_2026-08-13.md` (29 KB, verbatim, tags intact); `drill_brain_atl_lexical_semantic_hub_2026-08-06.md`; `ORGAN_MAP.md` B1/B5 |
| **(b) sparse vs dense** | **YES, fully** — incl. the exact Waydo numbers and, critically, the MTL-vs-neocortex trap | `lit_scan_cortical_learning_rule_and_sparsity_2026-08-13.md` (19 KB); `ORGAN_MAP.md` B4/D1 |
| **(c) perirhinal conjunctive coding** | **PARTIALLY — citations only** | Clarke & Tyler 2014 / Erez & Barense 2018 / Bussey & Saksida 2007 / Taylor & Devereux 2015, all cited but none full-text verified; `literature_cache` returns NOT CACHED |
| **(d) distinctive vs shared** | **YES, fully** — Cree/McNorgan/McRae + Tyler & Moss CSA with the correlational-fragility mechanism | `lit_scan_semantic_control_near_neighbour_2026-08-13.md` §3 (32 KB); `ORGAN_MAP.md` B3/C4 |
| **(e) role binding** | **YES** — and the answer was already recorded as UNPINNED and three-ways contested | `ORGAN_MAP.md` E1/E5; `research_context_binding_conjunctive_coding_and_replay_necessity_2026-08-11.md` §1 (87 KB) |

**So: 4 of 5 elements needed NO new literature. The only genuine new-scan target is the perirhinal
representational-hierarchy / feature-ambiguity literature (Bussey, Saksida, Murray, Cowell, Barense)
— and that is exactly the element the brief calls "the closest published match to our exact
failure."** A single narrow scan on that one question would have been the correct dispatch; three
broad scans were dispatched and returned nothing.

**Cost of not checking:** three agent generations, ~280k tokens by the coordinator's count, zero
artifacts, while ~230 KB of directly-relevant, tag-preserved material sat on disk. The
CHECK-BEFORE-YOU-SCAN gate (`research_persistence_policy_2026-08-13.md` §2) was created **one day
earlier** to prevent precisely this and did not fire.

**Recommendation (recorded, not executed — I am AUDIT-ONLY):** make the check a **precondition
stated in the drill brief itself**, the way the disclosure rule is. A rule that lives only in a
policy note is one un-read note away from not existing — the same durability failure already
recorded for the scheduled tasks and the KB ingest.

**§5 of the task brief (persist any recovered full report verbatim): NOTHING TO PERSIST.** No
literature report was recovered, because none was produced. The five 08-13 reports are already
persisted verbatim with their `RESCUED VERBATIM SUB-AGENT OUTPUT. DO NOT EDIT THE BODY.` headers and
their per-claim tags intact; this note cites them rather than restating them.

---

## 8. REUSE BEFORE BUILD — which organ do we ALREADY own?

**Enumerated from the filesystem first, then reconciled to the registry** (CLAUDE.md evidence
discipline §2). `ls hdlab/` = 155 `.py` files. The registry was queried too and is **useless for this
question**: `capability_registry_query.py --serves` returns **0 of 127 rows** for *"pattern
separation"*, *"sparse coding"*, *"conjunctive binding"*, *"role filler binding"* and *"attractor
cleanup"* — and 1 unrelated row for *"hub"*. That is the known-leaky registry, not an absence of
organs.

| mechanism | brain structure | organ WE ALREADY OWN | wired? |
|---|---|---|---|
| (a) hub convergence | ATL (vATL / temporal pole) | `hdlab/lexical_similarity.py` (hand lexicon, ~230 concepts); `hdlab/ppmi_sparse_encoder.py` (the named "ATL-hub analog", **CLOSED** by a real negative at scale); `hdlab/random_indexing.py` (the genuine distributional spoke, MIDDLE_BAND, **never wired anywhere**) | partial / closed / **NO** |
| (b) sparse separation | dentate gyrus | **`hdlab/dg_pattern_separation.py`** — fixed Gaussian expansion + top-k by magnitude + L2, hashlib-seeded, brain-canonical docstring citing Leutgeb 2007 / Guzman 2016 / McHugh 2007 | **NO — ZERO importers anywhere.** Re-verified today: `Grep` for `dg_pattern_separation|hippocampal_encoder|DGProjection` across all `*.py` returns **2 files** — `hdlab/hippocampal_encoder.py` itself and **one verification test**. `ORGAN_MAP.md` D1: *"Orphan."* |
| (b') sparse ternary recode | DG | `hdlab/hippocampal_encoder.py:113-116` (`mask · sign(dense)`, sparsity ~0.01-0.03) | **NO** (one verification test only) |
| (c) conjunctive coding | perirhinal | **NONE on the live path.** Nearest owned: `hdlab/binding.py` + `hdlab/bundling.py` | n/a |
| (d) distinctiveness weighting | cortical accumulation | **`ConceptSpace._sums`** — *the graded statistic is ALREADY COMPUTED*; `freeze_graded()` and `ReadoutConfig(graded_query=True)` both exist | **built, then destroyed by `np.sign`; the graded switch is DEFAULT-OFF** |
| (e) role binding | UNPINNED | `hdlab/binding.py` (FHRR/HRR/BSC), `hdlab/situation_model_accumulate.py`, `hdlab/situation_focus.py` (theta-gamma-shaped bounded buffer, capacity 4) | binding **YES**; focus buffer **NO** |
| CA3 completion | CA3 | `hdlab/cleanup_family.py`, `hdlab/iterative_attractor.py` | **YES** — but see the warning below |

> **⚠️ THE "REUSE THE OWNED ORGAN" RULE MUST NOT FIRE FOR CA3 COMPLETION, AND `ORGAN_MAP.md` C4 says
> so explicitly (EXPLICIT NEGATIVE RECOMMENDATION — do NOT build).** The reason is *element (d)*:
> distinctive features are **weakly correlated**, and **attractor settling is driven by correlational
> structure** — so adding CA3-style completion to the comparator would make near-neighbour
> discrimination **WORSE**. Both owned implementations also terminate in `np.sign`, which would add a
> **fourth** prototype operator. *"We already have an attractor network's nonlinearity with none of
> its recurrent weights: all of the prototype drift, none of the completion benefit."*
> **Note the live callers import `k_NN_lookup` (the single-shot form), not the iterative one** —
> `role_slot_summarizer.py:60`, `semantic_parser.py:96`, `context_retention.py:56`.

**THE SINGLE LARGEST FIDELITY GAP** (stated once, and it is not the one the brief anticipated):

> **We compute the brain's statistic and then destroy it.** `ConceptSpace.observe` accumulates a
> genuine graded per-dimension count — the exact quantity the brain uses to weight distinctiveness —
> and `anchor_matrix:450` / `bundle:460` / `canonicalize_fast:736` apply **`np.sign` three separate
> times**, collapsing "36 of 70 encounters agreed" and "70 of 70 agreed" to the same bit. The
> decision variable of the entire substrate is then **a Hamming distance between two 256-bit
> majority-vote patterns** (`ORGAN_MAP.md` C1: cosine between two ±1 vectors **equals 1 − 2·Hamming/d**).
> The organ that performs the missing operation is **the one we already have**, and the switch is
> **already written and default-OFF**.

That gap is (i) brain-grounded on the pinned side of the literature (the cortical semantic code is
**graded**, §3), (ii) the only intervention in its family with a floored positive
(**+0.0602 CI [0.0440,0.0762]** against scrambled 0.4975 and frequency 0.4800), and (iii) **requires
building nothing.** Its known ceiling is capacity (B4), not mechanism.

---

## 9. TWO VERDICTS

### VERDICT 1 — DO-NOT-REDO 18, "role-bound structure alone": **UNTESTED WITH A WORKING RULER. NOT REFUTED.**

**The recorded claim** (`STATUS_LESSONS.md:101`): *"Role-bound dependency structure ALONE as a route
to meaning. NULL on quality (0% vs 2% MEANINGFUL, delta −0.02)."*

**Evidence checked on disk (CLAUDE.md §5 six-point check — right file
`data/exp_structured_comparator_v1/metrics.json`; right version at HEAD; right env
`.venv/Scripts/python.exe`; right corpus 34,169 sentences; right metric hand-scored MEANINGFUL;
right arms CONTROL vs STRUCTURED):**

1. **The CELL ITSELF never claimed a quality refutation.** Its `verdict` on disk is
   **`STRUCTURAL_PASS_PENDING_HANDSCORE`**. The negative comes entirely from the Director's
   hand-score, a separate instrument.
2. **That instrument was arithmetically incapable of returning a non-null.**
   `notes/director_handscore_structured_comparator_2026-08-13.md`: **ONE MEANINGFUL row exists in the
   entire 100-row pooled sample.** With a supply of 1, the **maximum attainable |delta| over ANY
   allocation is 1/50 − 0/50 = 0.02**. The prereg's own power section declared a **minimum detectable
   delta of +0.11**. *"0.02 is 5.5x below the cell's own declared minimum detectable delta. The cell
   could not have returned a non-NULL verdict at any allocation of the MEANINGFUL rows it produced."*
3. **`notes/STATUS.md` STANDING DISCIPLINE 1 forbids exactly this gate and NAMES THIS CELL:**
   *"NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% M — cost TWO experiments,
   both UNDERPOWERED BY FLOOR (`exp_grounding_quality_readout_v1`, **`exp_structured_comparator_v1`**,
   the 2nd claiming to have FIXED the 1st). Gate on KNOWN-ANSWER RECALL instead."*
4. **The manipulation was REAL — which is what makes this "untested", not "failed to run".**
   Verified off `metrics.json`: `S1_cardinality.ok = true` (12 units), `S2_integrity.ok = true`
   (0 tautology facts, 0 no-leak violations, both arms), `S3_arms_differ.ok = true` (distinct
   digests), `S4_control_regression` reproduces the reference digest `836571fa99d5765d` and
   `n_facts=384` exactly. `secondary_cooccurrence_agreement`: `cooc_agreement_top5` **0.2552
   (CONTROL) -> 0.0749 (STRUCTURED)**, `binding_check = "DIVERGED"`. **The structure was genuinely
   imposed; only the ruler was broken.**
5. **A pre-declared confound survives unresolved,** in the cell's own `limitations`: *"STRUCTURED
   sees ~4x fewer features per encounter than CONTROL (2.86 vs 11.33). Filtering IS the mechanism, so
   this is not corrected for; it is the leading alternative explanation for a NULL ('structure was
   starved')."* Plus: the UD front-end is out-of-domain, which *"biases AGAINST H1"*.

**VERDICT: UNTESTED WITH A WORKING RULER.** The 0% vs 2% measured the GENERATOR'S floor, not the
structure. Reopening requires a **known-answer-recall** gate (per STANDING DISCIPLINE 1), not a
larger hand-score. Note the strength of the countervailing evidence this entry is currently
suppressing: **FACTORED 1.000 vs FLAT 0.003**, **CONJUNCTIVE 1.000 vs ADDITIVE 0.273**, **PERMUTATION
1.0000 vs FHRR 0.0629**.
**Recommended action (recorded, not executed):** amend `STATUS_LESSONS.md` item 18 with a
`superseded-by` line (CLAUDE.md §4) reclassifying it from a refutation to **UNDERPOWERED-BY-FLOOR,
UNTESTED**. I did not edit it — that entry is Director-owned and I am AUDIT-ONLY.

### VERDICT 2 — DG pattern separation, "already beaten in July": **NOT REFUTED. SCOPE-LIMITED to one task with one keying signal.**

**Both cells read off disk, not from the notes:**

| cell | verdict | numbers (verbatim from `verdict_msg`) |
|---|---|---|
| `exp_dg_pattern_separation_mcscript_purity_v1` | **HARD_FAIL** | *"DG-separation (sparsity=0.05) `mean_purity_multi=0.1013` does not clear meaningfully above the ~0.1999 baseline. This is the honest capacity-ceiling finding: **the substrate cannot discriminate 195-way online WITH THIS KEYING SIGNAL** even with DG-style separation."* |
| `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` | **HARD_PASS** | *"`dg_full=0.942` >= 0.50 AND `lift_over_uniform=0.859` >= 0.20 AND `effrank_lift=10.08x` >= 1.30x AND `std=0.004` <= 0.05 AND `knn_sentinel=1.000` >= 0.90 at M=10000. DG pattern-separation PRE-WRITE rescues anisotropy collapse **on real Pythia keys** (`uniform_no_presep` collapsed to **0.083**); off-diag mass dropped 0.179 -> 0.012."* |

**Reading.** The HARD_FAIL cell **states its own scope boundary in its own verdict string**: the
failure is attributed to **the keying signal**, at **195-way online** discrimination, on
**MCScript**. The HARD_PASS cell runs the *same mechanism* at **write time on real Pythia keys** and
gets **0.942 vs 0.083** — an **11.3x** separation with tight cross-seed spread (std 0.004) and a
clean sentinel (knn 1.000 at M=10000). `STATUS_LESSONS.md` already records the boundary explicitly:
*"this is pre-write separation on real Pythia keys, NOT the MCScript purity task, where the same
mechanism HARD_FAILs."*

**So DO-NOT-REDO 32's own text is right and its HEADLINE is wrong.** The body says *"Do not
re-propose DG as the separation fix **without a different keying signal**"* — a scoped, correct,
revival-criterion-bearing statement. The title, **"ALREADY BEATEN, IN JULY"**, reads as a general
refutation and is the part that gets quoted.

**Two further facts that keep this open** — and both are the kind of thing that makes a demotion
unsafe (STANDING DISCIPLINE 7: *no demotion without a fresh on-disk re-check*):
- `ORGAN_MAP.md` D1 rates `dg_pattern_separation` fidelity **SAME** — *"Random expansion + k-WTA +
  normalise is the brain's operation, in the right order, at roughly the right sparsity"* — one of
  only **5 organs of 38** to earn SAME.
- Its evidence line reads **"NO FLOOR — UNTESTED"** as an organ, and **WIRED: NO — ZERO `hdlab/`
  importers. Orphan.** I re-verified the orphan status today rather than inheriting it.

**VERDICT: NOT REFUTED — UNTESTED WITH A WORKING RULER on the near-neighbour separation question.**
It was tested on a **different task** (195-way online script purity) with an **acknowledged-bad
keying signal**, and it PASSES its own brain-metric at write time. **Caveat that must travel:** DG is
the **hippocampal/episodic** regime, so per §3 it is **not** licensed as a fix to the *cortical
semantic anchor code*; its faithful use is on the **key/index path**, at write time.
**Recommended action (recorded, not executed):** retitle DO-NOT-REDO 32 to match its own body —
*"DG AS THE GROUNDING ROUTE WITH THE MCSCRIPT KEYING SIGNAL — HARD_FAIL"*.

---

## 10. WHAT THIS DRILL DOES NOT LICENSE

- **It does not license wiring spelling in.** Nothing above touches that; the floor is a
  measuring-stick finding (`PLAN_NEXT_12H.md`).
- **It does not license building a hub, an attractor, or a role-binding circuit on fidelity
  grounds.** (a) and (e) are UNPINNED; (c) is pinned only in shape and is the one element needing a
  real scan; **C4 is an explicit do-NOT-build.**
- **It does not license a distinctiveness weight function.** UNPINNED, and four of our own guesses
  are null-or-harmful.
- **The one thing it does support is a switch that already exists and is default-OFF**, whose
  ceiling is capacity, not mechanism.
- **BUILD NOTHING was honoured:** no experiment, no wiring, no live-path change, no `hdlab/` or
  `experiments/` file touched, no `metrics.json` written.

**Superseded-by discipline:** no note was found stale enough to need a `superseded-by` line; two
entries in `STATUS_LESSONS.md` (items 18 and 32) need **retitling**, recorded in §9 as
recommendations for their Director-owner rather than executed here.
