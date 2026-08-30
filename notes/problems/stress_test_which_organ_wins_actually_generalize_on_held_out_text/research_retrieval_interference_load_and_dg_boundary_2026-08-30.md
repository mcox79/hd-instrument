# Research drill — retrieval-interference LOAD AXIS, the DG BOUNDARY, and CONTEXT reinstatement for similar competitors

**Filed:** 2026-08-30 by the research sub-agent (solver-scoped; single-file write).
**Trigger:** the store/retrieval/binding rerun (`exp_generalize_retrieval_real_codes_v1.py`) found the synthetic
SEP_CA-over-FLAT win (+0.94 @ load=32) collapses to a real-frequency-weighted **~+0.06** on LitBank who-did-what,
because 72.6% of entities carry exactly 1 verb-event and FLAT is already >=0.98 there; the win survives only for the
~10-13% "busy" (>=4-event) entities. Also: **DG pattern-separation HURTS** identity-orthogonal register codes
(SEP_CA_DG 0.49-0.63 < SEP_CA 0.98 at the tail). SOLVED.md named the open follow-on: rerun
`resolve_retrieval_interference` on LitBank/OntoNotes similar-competitor coref with the substrate's REAL context vector.
This drill adjudicates three brain-foundational walls before that build is committed.

**Method:** three parallel Sonnet cognitive/hippocampal-neuroscience lit-scans (one per wall), generic public terms
only (no substrate-novel names/configs/numbers off-platform). Synthesis + calibration by Opus. Lit-scan calibration
penalty applied: P estimates deflated 0.15-0.25; novel-synthesis P capped at 0.50; hard-fail thresholds pre-registered.

---

## HEADLINE

**The ~+0.06 is an ARTIFACT of measuring the WRONG load axis.** The cognitive-science evidence is convergent and, on
the decisive experiments, PINNED: retrieval interference in comprehension is driven by **similarity-based
cue-overload** — how many *other active entities feature-match the retrieval cue* — **not** by event-count-per-entity.
Event-count is a weak, derived proxy that is *directly falsified as a primitive* (Radvansky & Zacks 1991: equal
fact-count produces no fan cost once facts integrate into one situation model). The who-did-what task, with
same-word->same-code and ~1 unique verb-event per entity at the median, has structurally **near-zero competitor
overlap** — so it cannot reveal the operation's value regardless of how the store is built. The value lives on the
axis the task removed: **partial-cue retrieval among similar competitors** (pronoun / bridging anaphora where several
same-type entities match a coarse cue). There, three brain mechanisms co-fire — content-addressable completion (CA3),
**pattern-separation gated on code correlation** (DG), and **context reinstatement** (TCM/CMR) — and context
reinstatement resolving similar-memory competition is neurally PINNED (Bramao et al. 2022). **Recommendation: the
interference rerun IS worth building, but reframed onto the similar-competitor / partial-cue axis, gated by a cheap
content-floor test first.**

---

## Cheap decisive test (run BEFORE building the full rerun — ~1 CPU-hour)

The rerun only has room if content genuinely under-determines the choice on a real similar-competitor subset. Measure
that directly and cheaply:

1. On a pre-existing coref corpus (**GAP** is purpose-built: 8,908 naturally-occurring Wikipedia snippets each with
   **two same-gender candidate antecedents** — the competitor set is already reconstructed for you; or reconstruct
   the same-type candidate set on LitBank/OntoNotes, since their released gold chains discard competitors), isolate
   the **ambiguous subset**: mentions with >=2 candidate antecedents that share the coarse cue (gender/number/animacy/
   grammatical role) so a **content-only feature matcher** cannot rank them.
2. Compute the **content-only floor** accuracy on that ambiguous subset (features + semantic match, cue-blind to
   temporal/discourse order).
3. **Decision gate:** if the content-only floor on the ambiguous subset is **<= ~0.75** (genuine under-determination),
   there is headroom for a separated store + context reinstatement to add value -> **build the full rerun**. If it is
   **>= ~0.90** (features already separate the competitors), the mechanism has no room and the rerun would replay the
   +0.06 story on a different axis -> **do not build**; report the content floor as the answer.

This is the same discipline that produced the +0.06 correction (measure the operating point before crediting the
mechanism), applied one axis over.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Pre-registered for the reframed **similar-competitor / partial-cue** rerun. All bootstrap-CI, report CI half-width +
null p95, info-free twin must LOSE, floor recomputed on the same population.

- **P1 (load axis).** On the ambiguous same-type-competitor subset, a content-addressable/separated store **plus
  temporal-discourse context reinstatement** beats the content-only floor.
  - **HARD-PASS:** >= **+0.10 hit@1** CI-separated over the content-only floor on the ambiguous subset, twin losing.
  - **HARD-FAIL:** margin CI includes 0, OR the content-only floor is already >= 0.90 on the "ambiguous" subset
    (i.e., the subset was not actually content-under-determined -> the axis is still wrong; stop).
- **P2 (context is the carrier, not the store alone).** Ablating context reinstatement (content-addressable store
  only, no temporal/discourse cue) drops the P1 lift by the majority of its size.
  - **HARD-PASS:** context ablation removes >= 60% of the P1 margin (context is doing the disambiguation, matching
    Bramao 2022 competitor-then-target reinstatement).
  - **HARD-FAIL:** context ablation removes <= 20% of the margin -> the win is content-store fan, not context
    reinstatement; the `resolve_retrieval_interference` context claim does NOT generalize; reclassify.
- **P3 (DG boundary, the corrected version).** DG pattern-separation, gated on **measured code correlation**, HELPS on
  the **correlated-competitor** subset (near-synonym predicates / similar characters) and is neutral-or-off on the
  orthogonal subset.
  - **HARD-PASS:** SEP_CA_DG > SEP_CA CI-separated on the high-code-correlation subset, AND SEP_CA_DG <= SEP_CA on the
    orthogonal subset (reproducing the who-did-what negative, confirming the gate).
  - **HARD-FAIL:** DG fails to help even where codes are genuinely correlated -> the DG-helps-similar half does not
    transfer to this representation; the operation is mis-specified for text, not just mis-gated.

---

## WALL 1 — THE LOAD / INTERFERENCE AXIS — VERDICT: measuring the WRONG axis; +0.06 is an artifact, not a ceiling

**Brain mechanism.** Comprehension retrieval is content-addressable, cue-based retrieval from a working memory of
partially-active chunks (Lewis & Vasishth 2005 activation-based ACT-R sentence model — *modeling choice*). Its
difficulty is governed by **cue-overload / similarity-based interference**: a cue retrieves poorly in proportion to
how many items match it, not how many items exist.

**PINNED evidence (the decisive controlled experiments):**
- **Van Dyke & McElree 2006 (JML 55:157-166)** — held encoding load / list-length constant, manipulated only whether
  an intervening NP matched the retrieval cues; interference tracked **cue-overload** ("cues cannot uniquely
  distinguish among competitors"), not item count. One-variable causal manipulation -> **PINNED**.
- **McElree 2000; McElree, Foraker & Dyer 2003** speed-accuracy-tradeoff studies — retrieval **speed is constant**
  regardless of distance/number of intervening items; retrieval **accuracy** drops specifically with cue-*matching*
  competitors. The cleanest dissociation available: count does not slow retrieval; competitor-match lowers accuracy.
  **PINNED**.
- **Radvansky & Zacks 1991 (JEP:LMC), "Mental models and the fan effect"** + **Radvansky, O'Rear & Fisher 2017 (Mem &
  Cog)** — the fan effect is driven by the **number of distinct situation/event models** a concept is bound into, NOT
  the number of facts; equal fact-count produces **no** fan cost when the facts integrate into one coherent situation
  model. This *directly falsifies event-count as the primitive*. **PINNED** (replicated ~26 yrs apart).
- **Autry & Levine 2014 (Front. Psychol. 5:818)** — a **fan effect in anaphor processing**: 2-5 same-category
  candidate antecedents for a pronoun-like probe; RT slope **15.2 ms/noun (referents) vs 31.3 ms/noun (distractors)**,
  probe-accuracy linear trend p=.003, 2-vs-5 contrast **d=0.24 (95% CI 0.12-0.36)**. Confirms candidate (c)
  partial-cue = candidate (b) cue-overload *with a coarse cue*. **PINNED**.

**Calibration / deflation (mandatory).** **Jager, Engelmann & Vasishth 2017 (JML)** Bayesian meta-analysis of 110
comparisons: similarity-based interference is real but **dependency-type dependent** — inhibitory interference appears
for non-agreement subject-verb full-cue-match, is **absent** for subject-verb agreement and reflexive/reciprocal
antecedents, and partial-match sometimes yields *facilitatory* interference. **Do not treat similarity interference as
a universal law with one constant** — expect a modest, structure-dependent lift. This is the strongest reason to
deflate any large-lift expectation and to pre-register the P1 HARD-FAIL.

**Verdict on the four candidate axes:**
- **(a) event-count per entity — WEAK / falsified as a primitive.** It predicts difficulty only as a proxy, and
  over-predicts load for a busy-but-coherent character (integrates to one model -> no fan cost) while under-predicting
  for two similar minor characters. The who-did-what rerun measured *this* axis; +0.06 is the honest number **for the
  wrong axis**.
- **(b) similarity / cue-overload — DOMINANT.** Every other axis reduces to it. This is where content-addressable
  retrieval is load-bearing in reading.
- **(c) partial-cue (pronoun/bridging) — real, = (b) with a coarse cue** (Autry & Levine).
- **(d) cross-episode fan — = (b) over competing situation-model representations**, not a raw context tally
  (Radvansky & Zacks; Howard & Kahana TCM).

**So:** ~+0.06 is **not a true low ceiling for the operation in reading** — it is the value of a content-addressable
store on an axis (within-entity event count) where the brain's own interference literature says the operation barely
bites. The axis that reveals the real value is **between-entity similar-competitor / partial-cue retrieval**.

---

## WALL 2 — THE DG BOUNDARY — VERDICT: our finding is BRAIN-FAITHFUL in direction; "helps similar" is PINNED; "hurts distinct" is stronger than the neuroscience causally proves, and our own measurement is the missing data point

**PARTIAL CONFIRM, asymmetric evidence quality:**

| Sub-claim | Status | Anchor |
|---|---|---|
| DG **helps** discriminate similar inputs and is *causally required* specifically there | **CONFIRMED — PINNED (causal)** | McHugh et al. 2007 |
| DG's surplus decorrelation is concentrated at the similar end, ->0 as inputs become distinct | **CONFIRMED — PINNED (electrophysiology)** | Leutgeb et al. 2007 |
| DG separation is "pointless" (zero marginal benefit) when input is already orthogonal | **CONFIRMED — MODELING (theory)** | Santoro 2013; Marr 1971 |
| DG **actively HURTS** (net cost / adds noise) on already-distinct inputs | **NOT causally tested in vivo** — inference from over-sparsification info-theory | PLOS Comp Biol 2023 |
| DG is "quiescent/irrelevant" (shuts off) for distinct inputs | **NOT SUPPORTED AS STATED** — DG/CA3 treats distinct lures like *novel* items (non-differential, not off) | Bakker et al. 2008 |

**PINNED evidence:**
- **McHugh, Jones, Quinn ... Tonegawa 2007 (Science 317:94-99)** — DG-granule NR1 (NMDAR) conditional KO mice:
  **normal** acquisition and **normal discrimination of DISTINCT contexts**, but **selectively impaired at
  discriminating two SIMILAR contexts** (over-generalized freezing), with reduced context-specific rate modulation in
  downstream CA3. A true **double dissociation by input similarity**. This **PINS the "helps similar" half causally.**
  It does *not* test whether intact DG is a net cost on distinct inputs (no arm shows WT underperforming KO on
  distinct trials) — so it is **silent on the "hurts distinct" half.**
- **Leutgeb, Leutgeb, Moser & Moser 2007 (Science 315:961-966)** — square<->circle morph continuum: DG population
  vectors decorrelate (rate-remap) even for tiny shape changes while CA3 stays correlated; as environments become
  fully **distinct**, CA3 catches up (global remapping) and DG's **surplus** decorrelation over CA3 shrinks toward
  **zero**. DG's marginal value **vanishes** at the distinct end — it does not go negative in this dataset (DG and CA3
  become redundant there, not antagonistic).
- **Bakker, Kirwan, Miller & Stark 2008 (Science 319:1640-1642)** — human high-res fMRI: CA3/DG bias score **0.15**
  (treats similar lures like novel items = separation) vs CA1 **0.59-0.83** (treats lures like repeats = completion).
  Key nuance: lure activity was **not significantly different from novel** — DG is **non-differentially engaged**, not
  switched off, for distinct inputs.

**Theory (modeling):**
- **Santoro 2013 (Front. Behav. Neurosci. 7:96)**, direct quote: when EC input similarity S_EC(I1,I2)=0, "any further
  separation accomplished by the DG is **pointless** ... there are conditions whereby this separation may be
  **arbitrary, and even unnecessary**." From the Marr 1971 / Rolls / Treves-Rolls sparse-autoassociative framework:
  DG mossy-fiber sparsification only does work when EC patterns overlap. Note the word is **"pointless," i.e., zero
  marginal benefit — not "harmful."**
- **PLOS Comput Biol 2023** ("Robust and consistent measures of pattern separation") — over-sparsification is a genuine
  cost mechanism (destroys mutual information "up to the point where almost all information is lost"), but this is a
  statement about *excess sparsity in general*, not specifically about applying DG to already-orthogonal inputs.

**Verdict.** Our result "DG hurts distinct codes, helps similar ones" is **brain-faithful in its DIRECTION**, and the
**"helps similar" half is PINNED** (McHugh causal + Leutgeb electrophysiology). But the **"HURTS" (net-negative on
orthogonal codes) half is a stronger claim than the causal neuroscience establishes** — the literature supports "zero
marginal benefit / wasted capacity," plus a general over-sparsification cost, but **no in-vivo experiment shows DG
actively degrading already-distinct inputs.** This is precisely the gap **our own measurement fills**: SEP_CA_DG
0.49-0.63 < SEP_CA 0.98 on identity-orthogonal codes is an empirical instance of the predicted-but-untested cost
regime — a *modest AUDIT contribution*, not merely a confirmation. **Design rule (PINNED-supported):** gate the
pattern-separation step on **measured input-population correlation** (Leutgeb morph gate) or **candidate
confusability/false-alarm rate** (Bakker/MST gate) — invest separation where correlation is high; skip it where codes
are already orthogonal. Same-word->same-code register codes are orthogonal-by-identity -> **DG off** (matching the
who-did-what negative). Near-synonym / similar-character codes are correlated -> **DG on** (this is the P3 test).

**Boundary condition, operationalized for reading:** two register memories are "similar enough to recruit DG" when
their **codes are correlated** — near-synonym predicates ("say"/"utter"/"remark"), shared feature bundles, similar
characters — NOT when they differ only by **repetition of an identical symbol** ("say" recurring), which is the
who-did-what register's actual confusability source and is orthogonal-by-identity.

---

## WALL 3 — CONTEXT / TCM FOR SIMILAR COMPETITORS — VERDICT: context reinstatement is a neurally-PINNED disambiguator; similar competitors are double-digit-frequent in real text but HIDDEN by single-chain annotation; the rerun is worth building with a reconstructed competitor set

**Brain mechanism.** A slowly-drifting **temporal context vector** binds each item; retrieval reinstates the context
active at encoding, which then cues *other* items (Howard & Kahana 2002 TCM — *modeling choice*). CMR (Polyn, Norman &
Kahana 2009) extends the vector with **source/semantic context**, so two items with near-identical content but
different source/temporal context get different bound context and become **separable by context, not content**.

**PINNED neural evidence (context reinstatement observed at retrieval):**
- **Bramao, Jiang, Wagner & Johansson 2022 (Cerebral Cortex 32:5020-5035)** — *the most direct hit on the exact
  question.* AB/AC interference: cue A must retrieve target C while a stronger similar competitor B intrudes; EEG MVPA
  showed the **competitor's encoding context is reinstated first, and interference resolution coincides with the
  ensuing reinstatement of the TARGET's context.** Direct quote: "proactive interference was accompanied by an early
  reinstatement of the competitor context and interference resolution was associated with the ensuing reinstatement of
  the target context." Neural evidence that context reinstatement is the mechanism separating two content-overlapping
  memories. **PINNED** = measured during the computation (correlational EEG, not a lesion/causal-necessity test).
- **Manning, Polyn, Baltuch, Litt & Kahana 2011 (PNAS 108:12893)** — ECoG: reinstated context predicts the next item
  recalled, reproducing temporal contiguity at the level of brain activity. **PINNED**.
- **Folkerts, Rutishauser & Howard 2018 (J. Neurosci. 38:4200)** — human single-unit: well-remembered probes reinstate
  the drifted encoding context ("jump back in time"); poorly-remembered probes show anti-contiguity. **PINNED**
  (author order not disk-verified this pass).
- Foundational behavioral base: **Wickens 1970** release-from-proactive-interference; **Underwood 1957** interference
  is a function of the number of *similar* prior lists; **Johnson, Hashtroudi & Lindsay 1993** source-monitoring
  (two content-matching memories told apart by an inferential decision over bound context features).

**Operational definition (falls out of TCM/CMR):** two traces are **genuinely content-similar** when their
item/semantic feature vectors overlap enough that a content-only cue cannot rank one above the other; they are
**context-separable** when their bound context vectors (temporal position, source, discourse-index state) differ
enough that a context-reinstating cue can. Concrete narrative structures where this arises:
- **Repeated near-identical events at different times** ("which time did X happen") — **ECB+** (Cybulska & Vossen
  2014) is built entirely on near-identical news events differing only in time/participant/location; **Bontkes,
  Rubinova & Palombo 2025 (Mem & Cog)** show repeated-life-event memory gradedly collapses toward an undifferentiated
  script as instance similarity rises.
- **Similar minor characters** — Zwaan & Radvansky 1998 event-indexing model tracks **protagonist** as one of five
  situation-model indices separate from event content; predicts exactly this failure mode when two characters share
  properties.
- **Bridging / pronoun resolution with multiple matching antecedents** — Arnold 2010 accessibility: two same-type,
  same-gender salient referents are disambiguated by recency/topicality/grammatical role (context-like features), not
  content.

**Corpus reality (the key operational catch):** these cases are **not rare in the text, but systematically hidden by
annotation.** OntoNotes and vanilla LitBank (Bamman, Popat & Shen 2020) store a **single gold antecedent chain per
entity** — competitor/near-miss candidates are discarded at annotation time, so **you cannot measure competitor
prevalence from their released files** and, worse, a rerun that reads only the gold chain will *reconstruct the
who-did-what problem* (no competitors -> content trivially wins). Purpose-built resources confirm the phenomenon is
common: **GAP (Webster et al. 2018, TACL)** = 8,908 naturally-occurring Wikipedia snippets each with **two same-gender
candidate antecedents**; **ARRAU (Poesio & Artstein 2005)** = genuine ambiguity in ~**42%** of dialogue markables
(~12% in AnCora, genre-dependent — secondary-sourced numbers, treat as directional); **ECB+** for near-identical
events.

**Verdict.** A real similar-competitor retrieval rerun **is worth building**, and context reinstatement is a genuine,
neurally-PINNED brain mechanism for it (Bramao 2022 the anchor). **But the rerun MUST reconstruct the competitor
set** (enumerate same-type candidate antecedents), because the standard corpora throw competitors away — or use
**GAP**, which already ships the two-candidate structure. Test whether adding **temporal/discourse context
reinstatement** resolves the ambiguous subset above a content-only floor (P1/P2).

---

## Cross-thread synthesis

- **This closes the loop the SOLVED.md opened.** SOLVED named the next-step: rerun `resolve_retrieval_interference` on
  LitBank/OntoNotes similar-competitor coref with the substrate's REAL context vector. This drill says: **do it, but
  (i) reframe the load axis from event-count to similar-competitor / partial-cue** (Wall 1, PINNED), **(ii) gate DG on
  measured code correlation** (Wall 2, PINNED-supported), and **(iii) the disambiguator to test is context
  reinstatement, which is neurally PINNED for exactly this** (Wall 3, Bramao 2022) — **and reconstruct the competitor
  set because gold chains hide it.**
- **Convergent with the 08-29 discourse-fact drill**
  (`research_discourse_fact_resolution_brain_mechanism_2026-08-29.md`): that drill found a *freshly-introduced
  intra-sentential* antecedent is resolved by fast structural cues, NOT situation-model retrieval — i.e., the *wrong
  population* for a fact-store build. This drill agrees and sharpens it: the **right** population for a
  content-addressable + context-reinstatement build is the **inter-mention similar-competitor** case (multiple
  same-type antecedents, cross-sentence), where content genuinely under-determines. The two drills partition the coref
  residual: structural-cue cases (fast, no retrieval) vs similar-competitor cases (retrieval + context). Only the
  latter is this cluster's job.
- **Consistent with the owner discipline (08-28):** "score at the regime where the brain's advantage shows, not the
  data-rich regime where counting wins." The who-did-what rerun scored in the counting-wins regime (1 event/entity);
  the brain's advantage shows on the high-interference / low-content-separability subset. This drill relocates the
  measurement to that regime.
- **The DG negative is not a refutation of DG — it is a correctly-located boundary.** Same lesson as the
  who-did-what collapse: the mechanism is real; the operating point in the test removed the regime where it pays.

---

## Substrate-product implications

1. **Do NOT rerun the event-count axis again.** +0.06 is the honest number for that axis; the literature says the axis
   is weak (Radvansky & Zacks PINNED-falsifies count-as-primitive). Wiring the separated store "for busy entities
   only" (the SOLVED recommendation) remains correct for the count axis, but the *larger* value is on a different axis.
2. **Build the reframed rerun** (`resolve_retrieval_interference` on the similar-competitor / partial-cue axis), gated
   by the cheap content-floor test. Deliverable = the same HOLDS/DOES-NOT-HOLD ledger form, on the **ambiguous
   subset**, floor = content-only feature matcher, twin = shuffled-context.
3. **Ship a code-correlation gate for the pattern-separation step** (do NOT wire DG onto identity-orthogonal register
   codes — already a "do-not" in the AUDIT UPDATE; this drill adds the *positive* rule: wire DG **only** on the
   high-code-correlation subset, and P3 tests that it helps there). Gate variable = measured input-population
   correlation or candidate confusability rate.
4. **Context reinstatement is the mechanism to instantiate for the disambiguator** — temporal/discourse recency +
   source, per TCM/CMR, with Bramao's competitor-then-target reinstatement as the falsifiable neural signature
   (P2 ablation).
5. **Corpus note for the migration effort (p1):** GAP / ARRAU / ECB+ are the modern, pre-existing, competitor-carrying
   corpora; they also relieve the McGuffey corpus-age confound. Standard single-chain LitBank/OntoNotes gold **must be
   augmented with a reconstructed competitor set** or the rerun silently reproduces the who-did-what null.

**P estimates (deflated per calibration penalty):**
- P(similarity/cue-overload is the load-bearing axis, not count) = **0.85** (established cog-sci, PINNED experiments —
  not a novel synthesis, so light deflation).
- P(reframed similar-competitor rerun shows a CI-separated lift on the ambiguous subset | cheap test passes) =
  **0.50** (novel-synthesis cap; deflated 0.20 — Jager 2017 says the effect is modest and structure-dependent).
- P(DG helps on the correlated-competitor subset, P3 HARD-PASS) = **0.55** (McHugh/Leutgeb PINNED for the biology, but
  transfer to our code representation is the untested step -> deflated).
- P(context ablation removes the majority of the lift, P2) = **0.45** (Bramao PINNED neurally, but that the substrate's
  context vector carries discourse-time cleanly enough is the OUR-INVENTION risk -> deflated).

---

## Citations (verified count)

**Wall 1 (12):** Van Dyke & McElree 2006 (JML 55:157-166) [primary abstract verified]; McElree 2000 (J
Psycholinguist Res); McElree, Foraker & Dyer 2003 (JML); Lewis & Vasishth 2005 (Cog Sci); Radvansky & Zacks 1991
(JEP:LMC); Radvansky, O'Rear & Fisher 2017 (Mem & Cog); Autry & Levine 2014 (Front Psychol 5:818) [effect sizes
verified]; Jager, Engelmann & Vasishth 2017 (JML) [meta-analytic, verified]; Watkins & Watkins 1975 (cue-overload);
Anderson & Reder 1999 (fan review); Howard & Kahana 2002 (TCM); Schneider & Anderson 2012. *Unverified figure flagged:
"200-300 ms/fan-unit" secondary-source only — not cited above.*

**Wall 2 (7):** McHugh et al. 2007 (Science 317:94-99) [PINNED causal, cross-confirmed]; Leutgeb et al. 2007 (Science
315:961-966) [PINNED ephys, cross-confirmed]; Bakker, Kirwan, Miller & Stark 2008 (Science 319:1640-1642) [PMC full
text, exact quotes]; Santoro 2013 (Front Behav Neurosci 7:96) [PMC full text, exact quotes]; PLOS Comput Biol 2023
robust-measures [snippet]; Marr 1971 [via Santoro]; Yassa & Stark 2011 (Trends Neurosci 34:515-525) [bibliographic
only, not quoted]. *Lacy et al. 2010/2011 parametric lure-bin curve referenced but NOT verified this pass — flagged,
not counted.* Net: 4/7 solid-to-strong, 3/7 bibliographic/snippet.

**Wall 3 (11):** Howard & Kahana 2002 (J Math Psych 46:269-299); Polyn, Norman & Kahana 2009 (Psych Rev 116:129-156);
Manning et al. 2011 (PNAS 108:12893) [PINNED]; Folkerts, Rutishauser & Howard 2018 (J Neurosci 38:4200) [PINNED,
author order unverified]; **Bramao, Jiang, Wagner & Johansson 2022 (Cereb Cortex 32:5020-5035)** [PINNED, full-text
quote — the anchor]; Wickens 1970 (Psych Rev 77:1-15); Underwood 1957 (Psych Rev 64:49-60); Johnson, Hashtroudi &
Lindsay 1993 (Psych Bull 114:3-28); Zwaan & Radvansky 1998 (Psych Bull); Webster et al. 2018 GAP (TACL); Cybulska &
Vossen 2014 ECB+; plus Poesio & Artstein 2005 ARRAU, Bontkes et al. 2025, Arnold 2010, Bamman et al. 2020
(secondary-sourced numbers flagged directional).

**Total verified-primary or strongly-cross-confirmed: ~18 of ~30 cited; the load-bearing anchors (Van Dyke & McElree
2006, Radvansky & Zacks 1991, McHugh 2007, Leutgeb 2007, Bramao 2022) are all verified.**

---

## TLDR (plain language)

We tested a "smart memory" part on 100 real novels and its advantage over a simple method almost vanished — but we
were measuring the wrong kind of difficulty. Real brain research on reading is clear: memory gets hard not when a
character does *many* things, but when *two similar characters or things compete* for the same mental cue (like a
pronoun that could point to either of two people). Our test had no such competition, so of course the smart part had
nothing to prove. The right next test is exactly the competition case, and the brain's trick for it — reinstating
*when/where* something was learned to tell two similar memories apart — is well-documented in real brains. One catch:
the standard reading datasets quietly delete the competitors, so we have to rebuild the competitor list first (or use
a dataset built for it). Two side-findings held up: a brain-inspired "keep-memories-distinct" step correctly should be
switched OFF when memories are already distinct (our data even fills a small gap the neuroscience left open), and it
should help when memories are genuinely similar — which is the case we should now test.

## QUESTIONS

None — the three walls are adjudicated with PINNED-vs-modeling tags, and a cheap gating test de-risks the build/no-build
call.

## NEXT STEPS

- **Run the cheap decisive test** (content-only floor on the reconstructed same-type-competitor / GAP ambiguous subset).
  Build the full reframed rerun only if that floor is <= ~0.75.
- **Reframe `resolve_retrieval_interference` onto the similar-competitor / partial-cue axis** with context
  reinstatement as the disambiguator and a code-correlation gate on the DG step (P1/P2/P3 pre-registered above).
- **Feed the corpus note to the migration effort (p1):** GAP / ARRAU / ECB+ carry competitors and are modern
  (also relieves the McGuffey age confound); single-chain LitBank/OntoNotes must be competitor-augmented first.
