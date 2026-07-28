# Research: ARC fact-combination prior art / competitive-landscape scan (build-on + honest positioning)

**Filed:** 2026-07-24 by research (Opus synthesis over 3 parallel Sonnet lit-scan lanes).
**Trigger:** direct Director request — prior-art due diligence for the AGGREGATION RETRIEVER cell
(`notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md`, gated behind the
CLIMB FULL diagnostic) and its underlying settle-dynamics design
(`notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md`). Does the exact
question we are about to test — "does combining multiple retrieved facts beat single-fact retrieval
on ARC?" — already have a published answer? **Yes, largely, and it materially changes what our cell's
falsifiable predictions should say.**
**KB-check performed before dispatch:** read `notes/research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md`
(4-lane scour already covering NELL/PRA, DrKIT, NTP/LNN, NS-CL, Soar/Spaun — TupleInf appears there only
in a summary table, not with numbers) and `notes/research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`
(no ARC/Aristo/WorldTree hits) to avoid re-deriving already-covered ground. Neither prior note had the
AI2/Aristo-specific numbers or the VSA-2025/QAVSA material below — this scan is genuinely additive, not
duplicative.
**Query-privacy:** all 3 lanes searched literal public paper/system names (Aristo, TupleInf, TableILP,
WorldTree, DGEM, Multee, QAVSA, resonator networks, etc.) — these ARE the correct generic public terms
for this scour; no substrate-novel mechanism names, configs, or numbers went off-platform.
**Method:** 3 parallel Sonnet lit-scans (Lane A: Aristo/AI2 ARC-specific fact-combination systems and
numbers; Lane B: general glass-box multi-fact aggregation QA — TableILP/TupleInf mechanics, memory
networks, NMN, settling-style combination; Lane C: VSA/HDC systems that combine facts, incl. the 2025
ARC-AGI VSA paper and resonator networks) + director synthesis. All three lanes fetched and read primary
PDFs directly rather than relying on search snippets — numbers below are source-verified, not
paraphrased, except where explicitly flagged as unconfirmed.

---

## HEADLINE

**Our exact question — "does combining multiple retrieved facts beat single-fact retrieval on ARC" —
already has a published, nuanced, source-verified answer: it depends entirely on knowledge quality, and
on the harder ARC-Challenge split specifically, the answer for every published attempt (2016-2018) was
NO.** TableILP's own ablation (Khashabi et al. IJCAI 2016) is the cleanest same-system single-vs-multi-fact
comparison in the literature: removing multi-row inference drops accuracy from 61.5% to 51.0% on NY
Regents 4th-grade (curated semi-structured tables) — combination clearly helps by +10.5 points when the
underlying facts are curated and dense. But TupleInf (noisy auto-extracted OpenIE tuples) essentially TIES
single-fact IR (51.7% vs 52.0% on the same test) — no gain from combination when facts are noisy. And on
ARC-Challenge specifically, **every published multi-fact/structured solver from this era (TupleInf 23.73%,
TableILP 26.97%, DGEM 27.11%) is statistically indistinguishable from the 25.02% random-guess baseline**
(AI2's own 95% CI is ±2.5 points) — none of them beat chance. AI2's own diagnosis, quoted directly from the
ARC dataset paper (Clark et al. 2018): the bottleneck was **retrieval bias**, not the combination
mechanism — IR favors sentences individually similar to the question and systematically misses the
partially-matching sentences that only jointly (via combination/chaining) explain the answer. This is a
precise, source-verified precedent for exactly the failure mode our own aggregation-retriever cell must
guard against, and it means our HARD-PASS/HARD-FAIL predictions for that cell were previously
under-specified: beating the single-item floor is the easy half of the question; the harder, field-tested
half is whether our retrieval step itself reproduces the 2016-2018 IR-bias trap before the settle dynamic
ever gets a chance to combine anything.

On the VSA/glass-box side: no published system combines VSA/HDC vector-binding with a genuine iterative
settling/relaxation dynamic (CI-style or otherwise) specifically to combine multiple retrieved facts for
QA — this is a **confirmed, actively-searched-for gap**, not an assumption. The closest analog, Thagard's
ECHO (*Coherence as Constraint Satisfaction*, 1998), implements almost exactly the settle-to-coherence
dynamic our design calls for (signed positive/negative constraint network, settles by local relaxation) —
but it is a symbolic/localist connectionist network, not VSA, and was applied to explanatory/legal
coherence, never to QA benchmarks. The closest VSA-QA analog, QAVSA (Laube, Eliasmith et al., RepL4NLP
2024), bundles a retrieved KG subgraph into one VSA vector and concatenates it with a pretrained-LM
encoding for final scoring — genuine multi-fact VSA combination, but single-pass bundling (no iteration)
and NOT LLM-free at inference (the opposite of our no-black-box-LLM invariant). No VSA/HDC paper of any
kind has been applied to AI2-ARC science QA. Both gaps (CI-in-VSA; VSA-on-AI2-ARC) are genuine, confirmed
via active multi-angle search, not premature dismissal of an untried angle.

P_deflated: **0.42** for the honest-positioning claim below (novel-synthesis capped at 0.50 per discipline,
discounted further — see Calibration section).

---

## (1) Aristo / AI2 ARC-specific fact-combination — numbers, verified against primary PDFs

**Aristo full lineage** (Clark et al., "From 'F' to 'A' on the N.Y. Regents Science Exams," arXiv:1909.01958),
Table 2, verbatim:

| Test Set | IR | PMI | ACME | TupleInf | Multee | AristoBERT | AristoRoBERTa | **ARISTO (ensemble)** |
|---|---|---|---|---|---|---|---|---|
| ARC-Easy | 74.48 | 77.76 | 66.60 | 57.73 | 64.69 | 81.78 | 82.88 | **86.99** |
| ARC-Challenge | n/a\* | n/a\* | 20.44 | 23.73 | 37.36 | 57.59 | 64.59 | **64.33** |

\*IR/PMI define ARC-Challenge (questions both get wrong), so near-zero scores there are definitional, not
a fair comparison — the paper's own footnote.

The historical trajectory (Fig. 2, Regents-8th, 2014-2019): 36.4% -> 58.1% -> 63.1% -> 72.2% -> 73.1% ->
90.7%, driven first by "reasoning with tables and tuples," then by transformer LMs — i.e., the multi-fact
ILP-combination era (TableILP/TupleInf) produced real but modest gains over baseline retrieval, and the
*decisive* gains came later from language models, not from further refining fact-combination logic.
**Ensembling mechanism** (Sec 3.5): two-stage calibrated logistic regression over each solver's confidence
— this is solver-level ensembling, not within-chain fact combination.

**IR/PMI single-fact baseline vs. structured multi-fact solvers on ARC** (Clark et al. 2018, arXiv:1803.05457,
Table 6, direct PDF read):

| Solver | ARC-Challenge | ARC-Easy |
|---|---|---|
| IR (released corpus) | 20.26 | 62.55 |
| TupleInference | 23.83 | 60.81 |
| DecompAttn | 24.34 | 58.27 |
| **Guess-all / random** | **25.02** | 25.02 |
| DGEM-OpenIE | 26.41 | 57.45 |
| BiDAF | 26.54 | 50.11 |
| TableILP | 26.97 | 36.15 |
| DGEM | 27.11 | 58.97 |

Quoted directly from the paper: *"none of the algorithms score significantly higher than the random
baseline on the Challenge set... The poor performance of the non-IR solvers is partly explained by their
correlation with the IR solver... the retrieval bias of the underlying IR methods is towards sentences
that are all very similar to the question, and away from sentences that individually only partially match
the question, but together fully explain the correct answer (e.g., through chaining). This suggests the
need for a more advanced retrieval strategy for questions that require combining multiple facts."* This is
AI2's own, source-verified diagnosis that **retrieval, not the combination step, was the bottleneck** on
ARC-Challenge specifically.

**TupleInf** (Khot, Sabharwal, Clark, ACL 2017, arXiv:1704.05572) — ILP over a support graph, explicitly
**parallel-only** ("TUPLEINF only combines parallel evidence... each tuple must individually connect words
in the question to the answer choice," not chained). Table 2/3 (verbatim), NY Regents:

| Comparison | 4th Grade | 8th Grade |
|---|---|---|
| IR(S) alone | 52.0 | 52.8 |
| TupleInf(T+T') alone | 51.7 | 51.6 |
| IR(S) + TupleInf(T+T') ensemble | 55.3 | 55.1 |

TupleInf alone does **not** beat single-fact IR (essentially tied); only the ensemble gains (+3.3/+2.3
points). Documented failure modes: bag-of-words alignment drops negation/qualifier words, lexical-overlap
alignment produces semantic drift (scores "to breathe" high against "breathe out" — opposite meaning), and
multi-hop tuple chaining was explicitly disabled by the authors because it introduced too much noise —
only parallel (not chained) combination survived to the shipped system.

**TableILP** (Khashabi et al., IJCAI 2016, arXiv:1604.06076) — the cleanest same-system multi-fact ablation
found in this literature (Table 6, verbatim, NY Regents 4th grade, 129 test questions):

| Ablation | Score |
|---|---|
| TableILP (full, multi-row) | 61.5% |
| **No Multiple Row Inference** (single-row/table only) | **51.0%** |
| No Relation Matching | 55.6% |
| No Open IE Tables | 52.3% |
| No Lexical Entailment | 50.5% |

"No Multiple Row Inference... drops the performance by 10.5%, highlighting the importance of being able to
combine evidence from multiple rows." Average knowledge use: 2.3 rows, 1.3 tables per question — most gain
comes from parallel-row combination, not long cross-table chains (directly consonant with our own ~2.5
central-facts finding in the aggregation-retriever note). But on ARC-Challenge (harder, noisier knowledge),
TableILP only reaches 26.97% — barely above chance — so **the +10.5-point multi-row win was measured on
curated tables and a much easier test set; it does not clearly transfer to ARC-Challenge's harder,
less-curated regime.**

**DGEM / Multee** (Khot/Sabharwal/Clark AAAI 2018 SciTail; Trivedi et al. NAACL 2019): DGEM adapted to ARC
is single-sentence entailment with max-over-sentences scoring (**not** multi-fact combination — "we use the
maximum supporting sentence score as the answer choice score," verbatim from the ARC paper). Multee is the
one pre-BERT solver that genuinely combines multiple sentences via a learned "multi-layer aggregator" over
weighted evidence — and it is the best pre-transformer reasoning solver on ARC-Challenge (37.36%), a real
(if soft-attention-based, not discrete) multi-fact combination win over the ILP solvers.

**WorldTree / TextGraphs shared tasks** (Jansen et al. LREC 2018; Xie et al. LREC 2020 WorldTree V2): framed
as fact-retrieval/ranking (MAP/NDCG) for explanation regeneration, not QA accuracy — no direct
single-fact-vs-multi-fact QA-accuracy comparison analogous to the tables above was found in the corpus
papers. TextGraphs shared-task MAP/NDCG numbers found via search (TF-IDF baseline ~0.05-0.6 MAP,
2019 systems ~0.56 MAP, 2021 systems ~0.82 NDCG) are **flagged unverified** — not independently confirmed
against primary shared-task PDFs; treat as approximate.

## (2) General glass-box multi-fact aggregation — mechanics, ceilings, and a real gap

**TableILP/TupleInf mechanics** (both ILP): binary decision variables over active tables/rows/columns/
cells/question-terms/answer-options plus pairwise alignment edges; objective = weighted sum of
alignment/entailment scores over active edges; constraints bound chain length (`MaxTablesToChain`,
`MaxRowsPerTable`) and enforce question-to-answer connectivity through active cells. **The support graph is
genuinely inspectable** — a diagram of selected rows and cell-to-cell alignments literally shows the
reasoning chain used, a real discrete glass-box trace, not a post-hoc rationalization.

**Memory Networks (Weston 2015; Sukhbaatar/MemN2N 2015; Miller/Key-Value 2016)** combine multiple memory
slots via softmax attention + weighted sum — soft and differentiable, not discrete. **The field's own
verdict on this style of "glass-box" is negative**: Jain & Wallace ("Attention is not Explanation," 2019)
found attention distributions can be adversarially altered without changing predictions and are often
uncorrelated with gradient-based importance; Serrano & Smith ("Is Attention Interpretable?," 2019) found
erasing/shuffling attention weights often barely changes output. **This is directly load-bearing for our
own design discipline**: it is external, independent confirmation that "point to the highest-weighted
items" is not a reliable explanation mechanism — exactly why the bindsettle-CI note's must-fail checklist
(shuffled-matrix control, inverted-readout control, positive-only ablation) is not optional rigor but the
literal response to a documented failure mode in a closely analogous soft-combination mechanism. A discrete
signed-relaxation trace (our design) is a structurally different, and per this literature, a more
defensible claim than an attention-weight trace.

**Settling/relaxation-style fact combination for QA: not found anywhere.** The closest analog across both
lit-scan lanes is **Thagard & Verbeurgt, "Coherence as Constraint Satisfaction" (Cognitive Science, 1998)**
— ECHO, a symmetric-connectionist network settling to maximize satisfaction of signed positive/negative
constraints among evidence and hypothesis nodes (structurally close in spirit to Kintsch CI, converges in
<200 cycles, only guaranteed a local not global coherence maximum), applied to explanatory coherence in
science/legal reasoning — never to a QA benchmark, and not itself a VSA/vector-binding system. **This is a
genuine, credit-worthy new precedent for the settle-dynamic itself** (independent of the VSA substrate
question below) that neither prior internal note (bindsettle-CI 07-24, neurosymbolic-glassbox 07-18) had
surfaced — worth adding to the build-on list for the aggregation-retriever cell alongside Kintsch.

**Neural Module Networks**: no NMN paper found with an explicit, named "combine k retrieved facts" module
as its own discrete operation (Gupta et al. ICLR 2020 has find/filter/count/compare/arithmetic modules over
paragraphs, not a fact-combination module per se) — a real, if narrower, additional gap.

## (3) VSA/HDC systems combining facts

**QAVSA** (Laube, Eliasmith et al., RepL4NLP 2024, ACL Anthology 2024.repl4nlp-1.14) — the single closest
VSA-QA precedent found: a retrieved KG subgraph is bind/bundled into ONE VSA vector, passed through a small
MLP, concatenated with a pretrained-LM's QA-context encoding for final scoring; matches QA-GNN's accuracy
on 3 MCQA datasets with a simpler architecture and ~37-39% faster convergence. Confirmed genuine multi-fact
VSA combination (many KG triples -> one composite vector) but reads as **single-pass bundling, not
iterative settling** (unconfirmed with full certainty — PDF extraction failed twice, flagged), and **is
NOT LLM-free at inference** — it depends on a PLM encoding concatenated at the final scoring step, which is
exactly the invariant our substrate is built to avoid.

**"Vector Symbolic Algebras for the Abstraction and Reasoning Corpus"** (Joffe & Eliasmith, arXiv:2511.08747,
Nov 2025) — confirmed to target Chollet's ARC-AGI grid-puzzle benchmark (10.8%/3.0% train/eval, beating
GPT-4 at far lower compute), a genuinely different "ARC" from AI2's science-QA ARC, correctly distinguished.
Mechanism confirmed via full-text read: VSA binds colour/centre/shape per grid object as "System 1"
similarity heuristics; a classical "System 2" pipeline (hitting-set solving over a 13-op DSL + small NN
parameter prediction) does the actual reasoning. **Explicitly single-pass VSA feature extraction — no
resonator iteration, no attractor cleanup, no coherence/energy-relaxation dynamic.** Reinforces rather than
closes the CI-in-VSA gap.

**PathHD** (arXiv:2512.09369) — HDC path-retrieval (GHRR order-aware relation-path encoding) + **one LLM
call** for final adjudication on WebQSP/CWQ/GrailQA. One-shot retrieval, reasoning delegated to the LLM —
not glass-box at the combination step, not LLM-free.

**Resonator networks** (Frady, Kent, Olshausen, Sommer, *Neural Computation* 2020, arXiv:2007.03748 /
arXiv:1906.11684, plus follow-ons on integer factorization, in-memory factorization, and visual-scene
factorization) — the canonical iterative VSA relaxation mechanism, but **every confirmed instance factors
a SINGLE composite/bundled code back into its own known factors**; none combine multiple independently-
retrieved facts into a jointly-settled answer to an external question. No evidence found of resonator
machinery repurposed for QA-style fact aggregation.

**AI2-ARC + VSA/HDC: confirmed zero.** No paper found applying any VSA/HDC system to AI2's science-QA ARC
benchmark. **CI-model-in-VSA: confirmed zero** — actively searched across CI+VSA/HRR, CI+spiking/semantic-
pointer, and generic "coherence network"/"signed relaxation network" + bind-bundle substrate terms; nothing
on point beyond the non-VSA Thagard/ECHO precedent above.

---

## Honest positioning — what's genuinely novel, what's not, where to temper claims

**Genuinely novel (no precedent found after active multi-angle search):**
1. A VSA/HDC substrate combined with a genuine *iterative* settle/relaxation dynamic (CI-style or ECHO-style)
   specifically for multi-fact QA combination. QAVSA is single-pass bundling; resonator networks iterate but
   factor one code, not combine several independent facts; ARC-VSA (2025) is single-pass feature extraction.
   This combination — vector-binding substrate + genuine multi-cycle signed relaxation, applied to combining
   several independently-retrieved facts — has not been done, by anyone, for any QA task, VSA or otherwise.
2. Doing this with **zero black-box LLM at inference**. Both of the closest VSA-QA precedents (QAVSA,
   PathHD) still depend on a PLM/LLM at the final scoring step — our no-LLM-at-inference invariant is a
   genuine differentiator versus the field's actual practice, not just versus a hypothetical black box.
3. The trust-vetted fact store (source-trust design) + human-grade-scale measurement layer is
   HD-instrument-specific scaffolding with no analog found in any of the above literatures (they use
   fixed benchmark KBs, not a live trust-vetting mechanism).

**NOT novel — temper these claims:**
1. **"Combining facts beats single-fact retrieval" is not a novel finding to demonstrate — it is a
   already-published 2016 result** (TableILP's +10.5-point ablation) under the SAME condition we're
   counting on (curated, dense, science-table-style facts — our WorldTree tablestore is exactly this
   genre of resource). Our HARD-PASS prediction that bind+settle beats the single-item floor is asking a
   question the field already answered YES to under favorable knowledge conditions. The genuinely open
   question is narrower and harder: does it ALSO work on ARC-Challenge specifically, where every
   published multi-fact solver (TupleInf, TableILP, DGEM) has been stuck at chance for nine years, and
   AI2's own diagnosis says the reason is retrieval bias, not combination-mechanism weakness. **Expect
   real risk that our cell reproduces this exact historical trap if our retrieval step has the same bias
   AI2 diagnosed** (favoring facts individually similar to the question over facts that jointly, only in
   combination, explain the answer) — see the new cheap decisive test below, which did not exist in either
   prior internal note before this scan.
2. **"Glass-box multi-fact combination for QA" per se already exists and is inspectable** (TableILP/TupleInf
   discrete ILP support-graphs, genuinely traceable, not new). What is novel is doing it via VSA-native
   relaxation instead of ILP — a real mechanism-class delta, but a modest structural novelty, not a
   first-of-its-kind capability. Don't claim "first glass-box multi-fact QA system" — claim "first VSA-
   native, settle-dynamic glass-box multi-fact QA system," which is the accurate, defensible claim.
3. **The settle-to-coherence idea itself (independent of VSA) is not new** — credit Thagard's ECHO (1998)
   explicitly alongside Kintsch when describing the mechanism lineage; it is a 27-year-old precedent for
   exactly this class of signed constraint-satisfaction relaxation, just never applied to QA or built on a
   vector-binding substrate.
4. **Attention-weighted "glass-box" claims are contested in the field** (Jain & Wallace 2019; Serrano &
   Smith 2019) — this should sharpen, not weaken, our own claim: emphasize that our combination step is a
   *discrete* signed-relaxation trace (closer to TableILP's inspectable support-graph than to an attention
   weight), and that the must-fail checklist (shuffled/inverted/positive-only controls) is how we
   distinguish a genuine glass-box mechanism from a superficially-inspectable one — a distinction the field
   itself has shown really matters (soft attention looked inspectable and turned out often not to be
   faithful).

---

## Cheap decisive test (NEW — sharpens the already-staged aggregation-retriever cell)

Before or alongside the CI-relaxation vs. score-sum arms already specified in the bindsettle-CI note, add
a **retrieval-bias diagnostic** directly modeled on AI2's own 2018 finding: for a stratified sample of
ARC-Challenge questions (reuse the WorldTree gold central-fact annotations, no new labeling), measure
**recall of gold central facts in the top-k retrieved candidate set BEFORE the CI settle step runs**, split
by whether the gold fact is (a) individually similar to the question (easy for IR to find) or (b) only
partially matches the question, requiring the OTHER co-required facts for its relevance to be apparent
(the exact class AI2 found IR systematically misses). If (b)-class recall is low, no downstream settle
sophistication fixes ARC-Challenge — the honest report is "reproduces the 2018 IR-bias trap," not a
combination-mechanism failure. If (b)-class recall is reasonably high, low final accuracy is genuine
evidence the settle mechanism (not retrieval) is the bottleneck, and CI-relaxation is targeting the right
layer. This costs the same WorldTree-annotation-reuse budget as the multihop-reasoning-layer note's
diagnostic (~1-2 hours, no new labeling infra) and should run BEFORE claiming victory or defeat on the
main CI-vs-score-sum comparison.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, updated for this scan's precedent)

**HARD-PASS (all must hold, pre-registered before results):**
1. Bind+settle CI relaxation beats the single-item floor on **ARC-Easy** by >=5 points (this replicates a
   condition — curated/dense facts, TableILP-style — where the field's own 2016 precedent says combination
   should help; a miss here is a stronger signal of an implementation problem than a miss on Challenge).
2. The retrieval-bias diagnostic (above) shows (b)-class gold-fact recall is NOT catastrophically low
   (i.e., our retrieval step measurably avoids the specific 2018 AI2-diagnosed bias) — this is the
   necessary precondition for the settle mechanism to have anything to combine.
3. The discrete signed-relaxation trace passes the must-fail checklist already specified in the
   bindsettle-CI note (shuffled-matrix collapses to chance, inverted-readout performs below chance,
   positive-only ablation underperforms full signed version) — i.e., it is a genuine discrete glass-box
   trace, not a superficially-inspectable one per the attention-is-not-explanation caution above.

**HARD-FAIL (any one sufficient to require an honest downgrade, though the cell may still be useful):**
1. ARC-Challenge accuracy lands in the same 23-27% chance-band that TupleInf/TableILP/DGEM have all been
   stuck in since 2016-2018, AND the retrieval-bias diagnostic shows low (b)-class recall — this is not a
   fresh negative result, it is a **precise replication of a nine-year-old, already-diagnosed failure
   mode**, and should be reported as such (retrieval bug, not CI-mechanism bug) rather than as evidence
   against Construction-Integration or VSA combination generally.
2. Bind+settle does not beat the single-item floor even on ARC-Easy with curated tablestore facts — since
   the field's own precedent (TableILP ablation) says combination SHOULD help under exactly these
   conditions, this specific failure implicates our combination mechanism itself, not the harder,
   already-partially-excused ARC-Challenge case.
3. The must-fail checklist is not clean (e.g., positive-only ablation ties or beats the full signed
   version) — report honestly as spreading-activation-style aggregation (still a useful, real result, per
   the bindsettle-CI note's own fallback framing), not as CI-faithful or as beating any documented prior
   art on inspectable combination.

## Cross-thread synthesis

- Sharpens `notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md` (P_deflated
  0.38) with an external precedent it didn't have: Thagard's ECHO as a second, independent settle-to-
  coherence lineage alongside Kintsch CI (both signed constraint-satisfaction networks, neither previously
  applied to QA or VSA) — add to that note's citation list as build-on credit.
- Sharpens `notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md`'s cell design
  with a concrete, field-precedented retrieval-bias diagnostic that did not exist in that note — this
  should be added as a guardrail BEFORE the main CI-vs-score-sum comparison is treated as decisive, per
  the "cheap decisive test" section above.
- Extends (does not repeat) `notes/research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md`'s
  4-lane scour: that note's Field Survey table B row for "OpenIE (+TupleInf)" now has real numbers behind
  it (this note supplies them); that note's overall verdict ("no system unifies learned-read + VSA-binding
  + glass-box multi-hop") is reinforced, not contradicted, by this scan's finding that no VSA system does
  genuine multi-fact QA combination via settling either — a second, independent confirmation of the same
  gap from a different search angle (ARC/Aristo-specific rather than general neurosymbolic).
- Extends `notes/research_multihop_reasoning_layer_biology_and_design_sketch_2026-07-24.md`'s framing of
  ARC-Challenge as a possible aggregate-support-set / evaluation-format-artifact problem (not a chaining-
  depth problem) with a THIRD, independent, source-verified line of evidence pointing the same direction:
  AI2's own 2018 diagnosis that ARC-Challenge's wall is a retrieval-bias problem, not a combination-depth
  or combination-mechanism problem. Three independent angles (that note's WorldTree-shape argument, its
  cited evaluation-format-artifact paper, and this note's AI2 retrieval-bias quote) now converge on
  "fix retrieval/coverage before blaming the reasoning mechanism" as the dominant hypothesis for ARC's
  historical wall — directly actionable for how the aggregation-retriever cell's failure modes should be
  triaged when results land.
- Does NOT change `notes/exp_dev_handoff_research_K_fact_combination_2026-06-05.md`'s superposition-
  capacity math (that handoff is about VSA superposition/cleanup capacity bounds, K~sqrt(N)/2, unrelated
  to this scan's QA-benchmark-accuracy question) — no overlap, no correction needed there.

## Substrate-product implications

The honest positioning above gives the product a **precise, defensible claim rather than an inflated
one**: "the first VSA-native system to combine multiple retrieved facts via a genuine iterative settling
dynamic, with zero black-box LLM at inference, for question answering" — each qualifier in that sentence
is load-bearing and independently checked against a real, confirmed gap (VSA+settling: gap confirmed;
LLM-free: QAVSA/PathHD both use one, we don't; multi-fact-not-single-item: TableILP already showed this
helps under curated conditions, we're extending it to a different substrate and a genuinely harder
benchmark). Equally important for product honesty: **if ARC-Challenge caps at the same 23-27% chance-band
every prior structured solver hit, that is not a novel negative result** — it replicates a well-documented,
nine-year-old finding, and the retrieval-bias diagnostic is what distinguishes "we found the same known
wall" from "we found a new one." This reframes how a Challenge-split miss should be reported to the user:
not as evidence against Construction-Integration or the substrate, but as a test of whether our retrieval
step solved a specific, well-characterized 2018 problem — a much more precise and useful framing than a
generic "still hard" verdict.

## Citations (verified count: 31 total — 28 newly verified this scan across 3 lit-scan lanes + 3 KB-credited,
not re-derived)

**Aristo/AI2 ARC lineage (Lane A, primary PDFs read directly):** Clark et al. 2019/2020, "From 'F' to 'A' on
the N.Y. Regents Science Exams" (arXiv:1909.01958); Clark et al. 2018, "Think you have Solved Question
Answering? Try ARC" (arXiv:1803.05457); Khot, Sabharwal, Clark, ACL 2017, "Answering Complex Questions
Using Open Information Extraction" / TupleInf (arXiv:1704.05572); Khashabi et al., IJCAI 2016, "Question
Answering via Integer Programming over Semi-Structured Knowledge" / TableILP (arXiv:1604.06076); Khot,
Sabharwal, Clark, AAAI 2018, SciTail/DGEM; Trivedi et al., NAACL 2019, Multee; Jansen et al., LREC 2018,
WorldTree (ACL Anthology L18-1433); Xie et al., LREC 2020, WorldTree V2 (numbers not independently
PDF-verified, flagged); TextGraphs-13 shared-task repo (secondary source, MAP/NDCG numbers flagged
unverified).

**General glass-box multi-fact QA (Lane B):** Weston et al. 2015, Memory Networks; Sukhbaatar et al. 2015,
End-to-End Memory Networks; Miller et al. 2016, Key-Value Memory Networks (ACL Anthology D16-1147); Jain &
Wallace 2019, "Attention is not Explanation"; Serrano & Smith 2019, "Is Attention Interpretable?"; Gupta et
al., ICLR 2020, Neural Module Networks for Reasoning over Text (arXiv:1912.04971); Thagard & Verbeurgt
1998, "Coherence as Constraint Satisfaction" (ECHO, *Cognitive Science*); Khot et al., AAAI 2020, QASC.

**VSA/HDC (Lane C):** Joffe & Eliasmith 2025, "Vector Symbolic Algebras for the Abstraction and Reasoning
Corpus" (arXiv:2511.08747, targets ARC-AGI not AI2-ARC, correctly distinguished); Laube, Eliasmith et al.,
RepL4NLP 2024, QAVSA (ACL Anthology 2024.repl4nlp-1.14) + UWaterloo MASc thesis; PathHD (arXiv:2512.09369);
LinkHD (SSRN preprint, manufacturing KG link-prediction, not multi-fact QA); Frady, Kent, Olshausen, Sommer,
resonator networks (*Neural Computation* 2020, arXiv:2007.03748 and arXiv:1906.11684); follow-ons: in-memory
factorization (arXiv:2211.05052), visual-scene factorization (arXiv:2404.19126); ARLC (arXiv:2406.19121)
and Rel-SAR (arXiv:2501.11896), both noted as sources but not independently detailed this session (flagged).

**KB-credited, not re-derived:** Eliasmith 2013, *How to Build a Brain* (SPA/Spaun); Hersche et al. 2023,
NVSA (*Nature Machine Intelligence*); Kintsch 1988, Construction-Integration (*Psychological Review*).

**Internal cross-thread:** `notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md`;
`notes/aggregation_retriever_bindsettle_construction_integration_2026-07-24.md`;
`notes/research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md`;
`notes/research_multihop_reasoning_layer_biology_and_design_sketch_2026-07-24.md`;
`notes/exp_dev_handoff_research_K_fact_combination_2026-06-05.md`.

**No live-fetch follow-ups flagged for Director** — all load-bearing numbers (Aristo table, TupleInf
Regents table, TableILP ablation table, ARC dataset Table 6) were read directly from fetched PDFs by the
sub-agents, not inferred from search snippets. The only unverified secondary claims are the WorldTree V2 /
TextGraphs MAP/NDCG numbers (Section 1, flagged inline) and QAVSA's exact 3-dataset identity and single-
pass-vs-iterative status (Section 3, flagged inline) — low-priority to chase further since neither changes
the honest-positioning conclusion above.

## Calibration reasoning (P_deflated = 0.42)

Raw confidence in the FACTUAL/HISTORICAL claims (Aristo/TupleInf/TableILP numbers, AI2's own retrieval-bias
diagnosis, the attention-is-not-explanation findings, the confirmed VSA/CI-settling gaps) is high, ~0.85-0.90
— all load-bearing numbers were read directly from primary PDFs by the sub-agents (not paraphrased search
snippets), and the "gap confirmed" claims (CI-in-VSA, VSA-on-AI2-ARC) were reached via active multi-angle
search across all 3 lanes independently converging on the same absence, not a single lane's failure to
find something. Standard lit-scan deflation (-0.15 to -0.25) brings this to ~0.60-0.70 for the factual
landscape claims. The NOVEL-SYNTHESIS claim — "our specific combination (VSA + CI/ECHO-style settling +
trust-vetted store + LLM-free inference) is the right one to build and is genuinely differentiated" — is
capped at 0.50 per discipline, discounted further to 0.42 because: (i) QAVSA is close enough in spirit
(VSA + multi-fact combination + QA) that a determined search might still surface a closer unpublished or
very-recent 2026 preprint not yet indexed; (ii) the honest-positioning claim depends on our own cell
actually clearing the retrieval-bias diagnostic and the must-fail checklist, neither of which has been
measured yet — this note describes a landscape and a sharpened test design, not a result; (iii) the
strongest single risk this scan surfaces (reproducing the 2016-2018 chance-band trap on ARC-Challenge via
the same retrieval bias AI2 already diagnosed) is a real, field-precedented possibility, not a remote one,
and should weigh on any P(ARC-Challenge HARD-PASS) estimate more heavily than the pre-scan design assumed.
