# Brain-fidelity audit of the 12 subsystems (2026-08-13)

READ-ONLY audit. No code modified, no commits, no process killed, neither detached run
(`data/exp_wire_definitional_v1*`, `data/exp_anchor_pool_expansion_v1/`) touched. Measurement
environment `.venv/Scripts/python.exe`; working tree at `HEAD 48a9900c1`, branch
`dataprep/mcguffey-graded-corpus`, with `hdlab/reading_grounding_loop.py` MODIFIED in the tree
(the uncommitted definitional wire, see S2).

Subsystem partition and module counts are taken from `notes/system_accounting_2026-08-13.md`
(same day, machine-verified: 141 modules, 141 assigned, 35 live-reachable). This note does not
re-audit the census; it asks a different question of the same partition.

**Live-path membership was re-confirmed by runtime trace this pass, not inherited.** Importing
both entry points and inspecting `sys.modules` returns 40 `hdlab.*` entries, matching the census.
Every membership claim this note leans on was checked individually: IN the closure --
`event_bundle`, `hd_fact_store`, `situation_model_accumulate`, `gap_detector`, `learner`,
`goal_typing`, `frame_induction`; OUT -- `hippocampal_encoder`, `predictive_coding`, `continual`,
`three_tier_loop`, `definitional_extraction`. (Runtime over grep, per evidence-discipline §3.)

## Method (the project's own, applied literally)

For each subsystem: deep-brain map -> per-component compare on **SHAPE** (what the representation
and the operation actually are), **POSITION** (where in the processing order it sits, and what
constrains what), **METRIC** (what the thing is judged on) -> name the gap.

Two standing rules are applied as tests, not as decoration:

1. **A similarity-proxy sitting where the brain reasons is an architectural fault, not a tuning
   problem.** Getting the right component is not enough.
2. **For every mechanism ask which brain structure does this, and whether it shares a process an
   existing organ already implements.** The brain reuses circuits; a parallel build is both
   unfaithful and creates an island.

Severity vocabulary: **FAITHFUL** / **DIVERGENT-BUT-COMPATIBLE** (differs in implementation but
occupies the right position and is judged on a defensible metric) / **ARCHITECTURAL-FAULT**
(wrong shape, wrong position, or a proxy standing in for the computation being claimed).

Every number below is quoted with its control floor. A number without its floor is not evidence.

---

## S1. Live reading-to-grounding loop (21 modules)

**1. What it does.** Reads curriculum text sentence by sentence, flags content words it does not
know, accumulates a context trace per word per encounter, and during an offline "sleep" pass
promotes the well-evidenced ones into a fact store.

**2. Brain system.** Not one structure but a loop across four: left occipitotemporal word-form
processing into the perisylvian language network; **hippocampal CA1 comparator** for
novelty/mismatch (Lisman & Grace); **DG/CA3** for one-shot episodic encoding of each encounter;
and **sharp-wave-ripple replay driving systems consolidation into neocortex** during slow-wave
sleep (Buzsaki; Diekelmann & Born) with the **anterior temporal lobe hub** as the destination
semantic store. The module docstrings cite this literature accurately -- the offline pass, the
`intervening_pass_ok` rule (Dumay & Gaskell's sleep-dependent, not merely time-dependent, word
integration) and the schema criterion (Ghosh & Gilboa) are real findings correctly named
(`hdlab/grounding_acquisition_loop.py:448-459`).

**3. SHAPE / POSITION / METRIC.**

| | ours | brain's |
|---|---|---|
| SHAPE (word repr.) | `context_vector`: unordered **bag of content words**, each a sha256-seeded random bipolar draw, summed and sign-quantised (`grounding_acquisition_loop.py:117-134`). No order, no roles, no syntax. | Structured multimodal code: a hub representation in ATL bound to modality-specific spokes, plus syntactic/thematic structure carried separately. |
| SHAPE (meaning assignment) | `canonicalize`: **argmax cosine** of the word's summed contexts against a matrix of anchor words (`reading_grounding_loop.py:656-703`). Meaning of X = the already-known word whose contexts most resemble X's. | Meaning is a bound relational structure over referents, not a nearest neighbour in a co-occurrence space. |
| POSITION | The parser (S10, `pos_tagger`/`arc_parser`/`arc_labeler`) runs **upstream and on the live path**, and `thematic_role_labeler` assigns roles -- then the grounding gate reads the **bag-of-words** vector and discards all of it. The structured encoder exists (`structural_vector_masked`, `reading_grounding_loop.py:398`) and is **default-OFF** (`:1044-1048`, "THE ONE VARIABLE"). | Syntax **constrains** lexical-semantic acquisition rather than being computed alongside and dropped -- syntactic bootstrapping (Gleitman): the frame a word appears in is evidence about its meaning. |
| METRIC | `schema_consistency_split_half`: cosine between two halves of the item's **own** context vectors, threshold 0.10; plus exposure >= 8 and vote margin >= 0.75 (`grounding_acquisition_loop.py:356-401`, `:432-447`). | Whether the acquired representation supports correct inference and generalisation to unseen contexts. |

**4. Divergence and severity: ARCHITECTURAL-FAULT.**

The decisive step -- what a word *means* -- is a cosine argmax over a co-occurrence profile. That is
a similarity proxy occupying the position where the brain performs relational binding. Three
independent lines of evidence, each with its floor:

- **Hand-scored quality of the live path: 8% MEANINGFUL** (4/50), against a v2 distributional
  baseline also at 8% (4/50) and a low-information-filtered control also at 8% (4/50) --
  `notes/director_handscore_b3_def_vs_control_2026-08-12.md`. The unwired definitional path on the
  same rubric, same n=50, same seed-42 sampling, scores **38%**, and at v5 **64%** (32/50) against
  a pre-registered HARD_PASS band of >=52% (`notes/director_handscore_b3_v5_termboundary_2026-08-12.md`).
  Caveat recorded honestly: those scores are single-judge and **not blind**.
- **The one BLIND score of the live path is 2% MEANINGFUL** (1/50 CONTROL arm, blind, shuffle seed
  42, `notes/director_handscore_structured_comparator_2026-08-13.md`). It is consistent with the
  non-blind 8%, and it is the lower, more trustworthy figure.
- **The metric is self-referential.** Split-half cosine asks whether an item's contexts agree with
  *each other*. Internal coherence is not correspondence: a word that reliably appears in similar
  sentences banks a meaning regardless of whether the object is what it means. The brain's schema
  criterion (Ghosh & Gilboa, which the docstring cites) is congruence with a **prior structured
  schema**, not self-consistency of instances. This is the metric fault the audit method exists to
  catch -- and it is a **standing verdict, not a new one**:
  `research_brain_fidelity_architecture_audit_2026-08-09.md` row 4 already ruled that split-half
  cosine "is a test-retest RELIABILITY metric (psychometrics)" and instructed "Do not call the
  current signal 'vmPFC congruency.'" The reconciling detail, which must be stated or the two
  readings look contradictory: `research_context_binding_..._2026-08-11.md` §3e upholds the
  **necessity of a guard at that position** (the Warren 2014 false-memory liability is real); what
  is not upheld is the **identity of the signal** as schema congruence.

This subsystem's own read-out has also been measured directly since. `notes/director_handscore_readout_v1_2026-08-13.md`: **3% MEANINGFUL / 19% RELATED / 78% NOISE at
  n=100**, against the 8% reference floor; and the F1/F3 read-out fixes returned +0.0200 in a
  contest whose **maximum achievable delta was 0.06** given only 3 MEANINGFUL rows -- i.e. that
  experiment could not have produced a non-NULL verdict. Two corollaries worth carrying: the
  argmax-stability fix (-0.168 flip at matched retention) moved stability without moving quality
  ("F1/F3 make the WRONG argmax more repeatable, not more correct"), and admission drift of
  -0.238 voided the retention-matched claim outright. Against that, the one encouraging signal in
  the same note is corpus-shaped: OpenStax biology material scored **M+R 52.94% (9/17) vs news
  16.05% (13/81), Fisher OR 5.88, p=0.0024** -- with the honest caveat that 8 of the 9 are RELATED,
  not MEANINGFUL, and the 95% CI on 9/17 is 0.28-0.77.

Measured on disk this pass (correcting my own first attempt, which used the field name `object`
where the store uses `obj` and so reported 0%):

| store | facts | GROUNDED_MEANING | tautological `(X,GM,X)` |
|---|---|---|---|
| `data/foundation/reading_grounding_v1/store/store_facts.json` (mtime 2026-08-12 09:46) | 7,966 | 3,544 | **2,328 = 65.7%** |
| `data/foundation/reading_grounding_v2_qualityfix/store/store_facts.json` | 2,146 | 634 | **0 = 0.0%** |

This reproduces `notes/landed_vet_foundation_validation_2026-08-12.md` exactly on v1, and adds a
correction the MEMORY banner does not yet carry: **the tautology defect is fixed in the mechanism
at HEAD**. `_make_grounding_gate` refuses to bank a self-referential fact and logs it as
`REFUSAL_TAUTOLOGY` (`reading_grounding_loop.py:1134-1139`), and the v2 store shows 0/634. What
remains true is the *artifact* critique: the 3,544-fact store that the "grounded foundation" claim
rests on is 65.7% tautology. Two caveats: GM yield falls 3,544 -> 634 across those runs, and I did
**not** verify the two runs read the same corpus, so that ratio is not a clean quality/yield
trade-off measurement. Separately, ~10% of v1 subject tokens are over-stemmed (`billionair`),
which `notes/stemmer_corruption_2026-08-13.md` establishes is historical debt from before commit
`01093ac1f`, not a live defect.

The read-out has a second, structural fault, independently traced today: `canonicalize` takes its
argmax over `ConceptSpace` anchors, and a lemma enters `ConceptSpace` at exactly two sites -- seed
vocabulary, and words this same loop already grounded (`reading_grounding_loop.py:1050-1063`,
`:1279`). The expressible range of "meaning" is therefore a **closed set** pinned near the 887-lemma
seed (`notes/downstream_bottleneck_trace_2026-08-13.md`). When no anchor clears threshold the
function returns the lemma itself (`:699-703`) -- which is why the pre-fix store filled with
tautologies. That note also supplies the crucial negative result: switching on the structured
encoder scored **0/50 vs 2/50** (delta -0.02, pre-registered NULL band |delta| < 0.05), and the
null is **floor-limited by the missing candidate set**, not evidence that structure does not help.
So: fix the read-out's candidate set before re-testing the comparator.

**5. Shared process / duplication.** Three, all in the same direction -- the live path implements a
simpler, less faithful version of something a faithful organ already implements elsewhere:

- **Consolidation.** `consolidation_pass` counts exposures and checks split-half cosine. It has no
  replay. `hdlab/continual.py` (NREM replay) and `hdlab/hippocampal_encoder.py`
  (`CLSReplayCycle`, "replay CA3 attractors as inputs to cortex") both implement replay-driven
  consolidation and are **not on the live path**.
- **Novelty.** `gap_detector` decides gap-hood by a cosine margin against a codebook threshold
  (`gap_detector.py:91-118`, floor 0.625). `hdlab/predictive_coding.py` implements
  Rao-Ballard/Friston residual gating -- prediction error, which is what the hippocampal comparator
  actually computes -- and is **not on the live path**.
- **Lemmatisation.** At least five implementations: `thematic_role_labeler.lemma_word` and
  `.lemma_verb`, `reading_grounding_loop.normalize_lemma`, `definitional_extraction._lemmas`,
  `frame_induction._lemma_candidates`, `goal_outcome_relation_grounded._lemma_candidates`. One of
  them (`lemma_verb`, a suffix stripper) corrupted ~10% of the banked store's subject vocabulary.
  This is the concrete cost of a parallel build.

Credit where due: `gap_detector`'s decision to read the **pre-settle** cosine rather than the
attractor's settled state (`gap_detector.py:96-104`) is correct and well-argued -- a post-settle
read would report confidence for novel input too. That reasoning is exactly right; the residual
divergence is that a *comparator against stored patterns* is still not a *prediction error*.

**6. Wire verdict: STAYS WIRED (it is the live path) -- but the read-out is NOT-UNTIL-X.**
The loop's skeleton (flag -> accumulate -> offline consolidate -> gate) is brain-shaped and should
stay. `canonicalize` should be demoted from primary meaning-assignment to fallback. X = (a) the
candidate set is opened beyond seed-union-already-grounded, and (b) a structured signal supplies
the object. Both are in flight: (a) is `exp_anchor_pool_expansion_v1`, (b) is the uncommitted
definitional wire. Neither is judged here.

---

## S2. Definitional extraction + foundation persistence (5 modules)

**1. What it does.** A symbolic pattern extractor that pulls "X is a Y" definitions out of real
text and writes them as facts, plus deterministic save/reload of the foundation.

**2. Brain system.** **Fast declarative encoding of an explicitly-stated relational proposition** --
hippocampal one-shot relational binding (the "fast mapping" route, Carey & Bartlett), with the
sentence parsed by the ordinary language network (LIFG/pSTS) to recover the predication. The
module names this correctly and, unusually, names the CLS pairing right: the definitional path is
the one-shot relational bind, the distributional path is the slow cortical accumulator, and they
are complements rather than competitors (`definitional_extraction.py:28-33`).

**3. SHAPE / POSITION / METRIC.**

| | ours | brain's |
|---|---|---|
| SHAPE | Five regexes (COPULA, APPOSITIVE, GLOSSARY_COLON, CALLED, REFERS_TO, `:86`) plus a right-most-noun-before-a-clause-boundary heuristic for the genus head (`:41-45`, self-described as "deliberately shallow"). | Parse the construction with the same syntactic machinery used for all comprehension; bind term -> genus. |
| POSITION | Correct in principle -- explicit instruction is exactly where fast declarative encoding belongs. **But it is off the live path** and bypasses the repo's own parser, which IS on the live path. | The definitional route shares the parser with everything else; it is not a separate string-matching channel. |
| METRIC | Hand-scored MEANINGFUL/RELATED/NOISE on a random n=50 sample against a rubric about *what the word means*. | Behavioural: does the learner now use the word correctly. |

**4. Divergence and severity: DIVERGENT-BUT-COMPATIBLE.** A regex is not a neural mechanism and
never will be. But it occupies the right position, it supplies the signal the distributional path
structurally cannot ("X means Y" vs "X occurs near Y" -- the module says so itself at `:22-25`),
and **its metric is the best in the repository**: 64% MEANINGFUL (32/50) against an 8% (4/50)
distributional control, both hand-scored on the same rubric with the same sampling. That is the
only place in this audit where the thing being measured is the thing the brain is judged on.

Two real limits. (a) The pattern set is entirely **NP-headed**, which blocks syntactic
bootstrapping (a route that needs verb argument structure). Measured independently this pass on
`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` (2,092 rows;
patterns COPULA 648 / GLOSSARY_COLON 519 / APPOSITIVE 495 / CALLED 422 / REFERS_TO 8):
**0 of 2,092 objects are verb-only in WordNet**, and 5 of 2,092 subjects are (two of those are
surnames). The genus slot is categorically nominal. Crude proxy -- many words are both noun and
verb, so "verb-only in WordNet" undercounts verbs -- but a count of exactly zero across 2,092 rows
is not a sampling artifact; it is the shape of the pattern set. (b) The extractor re-derives NP-head finding rather than reusing S10 -- disclosed
honestly ("none of them expose a bare NP-head API, so the ~20-line local heuristic is the honest
minimum") but still a parallel build of a process an existing organ performs.

**5. Shared process / duplication.** NP-head extraction duplicates the live parser (S10). The
lemma normaliser is a sixth copy (see S1). `random_indexing` overlaps `context_vector`'s
random-indexing encoder and the S8 encoders.

**6. Wire verdict: YES.** This is the clearest wire recommendation in the audit, and it is
justified on fidelity, not convenience: the CLS story requires *both* a fast relational route and
a slow distributional one, and the substrate currently has only the slow one. The 64%-vs-8%
contrast is a fidelity argument (relational binding beats co-occurrence at recovering meaning),
not merely a score. Caveats to carry: single-judge, non-blind; and the wire must **add** a channel
rather than replace the accumulator, exactly as the module's own docstring argues.

---

## S3. Multi-source knowledge lookup / three-tier (5 modules) -- the specific call

**1. What it does.** When a concept is missing, gather candidate facts from knowledge graphs,
reason over them by two-hop traversal, and gate the good ones into either a permanent foundation
or a retain-forever middle tier.

**2. Brain system -- and this is where the subsystem splits in two.**

The three-tier framing is **Complementary Learning Systems** (McClelland, McNaughton & O'Reilly
1995), stated explicitly: MIDDLE = hippocampus (fast, accumulate, always-queried-first),
FOUNDATION = neocortex (consolidated), GATE+SWEEP = systems consolidation
(`three_tier_loop.py:8-11`). That mapping is legitimate and is the best-motivated architecture
claim in the repository.

The two mechanisms underneath it map very differently:

- **GATHER** (`ca3_relevance_gather`, `gather_reason.py:82-113`) is a matching-pursuit peel loop:
  cue with a query vector decoded from a state-of-mind register, take the attractor's best match,
  subtract it from the residual, repeat until the residual collapses or similarity drops below a
  floor. This **is** hippocampal in shape: pattern completion from a partial cue, with
  already-retrieved items suppressed so the next one can surface -- the same structure as
  sequential free recall with retrieved-item suppression (SAM, Raaijmakers & Shiffrin). Cueing
  retrieval from a maintained state rather than scanning everything is exactly what
  hippocampal-neocortical retrieval does.
- **REASON** (`fanout_two_hop`, `:116-145`) chains two lookups in a Hebbian outer-product
  associative matrix (`kg_traversal.KGStore`: `key = E[s] * R[p] * sqrt(d)`, `W += outer(E[o], key)`,
  `scores = E @ (W @ key)`, `kg_traversal.py:70-105`). A heteroassociative matrix memory is a
  defensible model of cortical/CA3 association. The **max-aggregate over top-k** at the join,
  however, is a search procedure, not a settling dynamic.
- **CORROBORATION / VOTE.** This is the part the mission asks about, and it is the part with **no
  brain analogue**.

**3. SHAPE / POSITION / METRIC (the corroboration mechanism).**

| | ours | brain's |
|---|---|---|
| SHAPE | `independence_weighted_trace_score`: tag each trace with a source name, look the tag up in a hand-written `SOURCE_INDEPENDENCE_CLASS` table, weight the first trace from an independent source 1.5 and a correlated/unknown source 0.15, decay repeats geometrically at 0.2, sum, threshold at 2.5 (`exp_three_tier_loop_independence_weighted_confirm_v1.py:191-238`). | There is no source registry in memory. Episodic traces carry contextual detail from which source can sometimes be *recollected* (source monitoring, prefrontal/MTL), but source identity is a retrieved property, not a weight applied at encoding. Nothing counts distinct informants. |
| POSITION | At the consolidation gate: it replaces the raw trace count `MIN_CONFIRM` via the `trace_weight_fn` hook. | Systems consolidation is driven by **repeated, varied reactivation** across episodes and by congruence with existing schema -- accumulation over *encounters in different contexts*, not over *provenance-labelled informants*. |
| METRIC | "Does the score cross 2.5?" The self-test asserts 1 source does not cross, 2 do, 50 repeats of one never do (`:404-423`). | Is the retained proposition true / does it support correct inference? |

**4. Divergence and severity: the subsystem is SPLIT.**

- GATHER: **FAITHFUL** (cued pattern completion with retrieval suppression).
- REASON: **DIVERGENT-BUT-COMPATIBLE** (Hebbian associative chaining is fine; top-k max-aggregate
  is engineering, and two hops is where its certification stops -- `predict_n_hop`'s own docstring
  records chain-grade only at K=2, MIDDLE_BAND at K=3,4).
- CLS three-tier framing: **DIVERGENT-BUT-COMPATIBLE, with one specific missing piece.** The
  defining mechanism of CLS is **replay**: the hippocampal trace is reactivated and interleaved
  into cortex. `three_tier_loop` promotes by *counting and thresholding*; nothing replays. The
  repo owns `hippocampal_encoder.CLSReplayCycle` and `continual.py`'s NREM replay, and
  `three_tier_loop` imports neither (its imports are `gather_reason`,
  `grounding_acquisition_loop`, `hd_fact_store`, `kg_traversal`, `prelim_tier`,
  `script_grain_acquisition_loop`, `:73-78`). Read this pass, `update_prelim_and_generalize`'s
  "CA3/DG sweep" is a trace-count check plus `schema_consistency_split_half` plus a
  `ScriptLibrary.match_or_spawn` cluster-register match (`prelim_tier.py:134-189`) -- nothing is
  reactivated as input to the slow store. A CLS architecture without replay is CLS in name.
  Note also that the middle tier reuses S1's split-half cosine verbatim ("byte-identical to the
  single-item BANK gate", `:151-156`), so **the S1 metric fault propagates into S3 unchanged** --
  faithful reuse of an unfaithful metric.
- CORROBORATION / VOTE: **ARCHITECTURAL-FAULT.**

**Answering the question plainly: "query several knowledge bases and vote" is not how the brain
retrieves anything.** It is an engineering convenience. The honest decomposition:

- What the brain *does* do that this superficially resembles: (i) **accumulate evidence across
  repeated encounters** before committing to long-term storage -- but over episodes in varying
  contexts, not over labelled informants; (ii) **convergence-zone binding**, where a concept is
  stabilised by convergent input from several *modalities* -- but those arrive simultaneously and
  are bound by coincidence detection, not queried serially and counted; (iii) **source
  monitoring**, which recovers where information came from -- a retrieval-time property, not an
  encoding-time weight.
- What the brain has no analogue for: an explicit registry of sources, a hand-set independence
  coefficient per source, and an additive score compared to a threshold. Corroboration in the
  brain is *emergent* -- a fact supported by many overlapping reactivations survives because
  unsupported features fail to reactivate -- not *computed* from a provenance table.

**No prior note in this repository argues that multi-source corroboration is brain-faithful.** The
three closest argue other things: `research_three_tier_knowledge_sourcing_gather_layer_2026-08-11.md`
is a sourcing/licensing drill whose warrant is stated as the user's own thesis and which names no
brain structure in its recommendations; `multisource_lookup_wiring_audit_2026-08-13.md` is a
reachability audit; and `research_context_binding_..._2026-08-11.md` §1d(b) is the standing
**counter**-evidence -- it found strong support for DG/CA3 pattern separation as what keeps
unrelated conjunctions from competing, but "did NOT find support for the brain using distinct
anatomical 'modules for unrelated content' as a SEPARATE mechanism", and therefore rules that
context-sharding "should be understood explicitly as an ENGINEERING approximation". So arguing
multi-source corroboration is brain-faithful would be **a new claim**, and it would have to
discharge that finding. This note declines to make it.

The one genuinely brain-grounded argument in the neighbourhood is about **channel independence,
not source count**: `brain_fidelity_audit_readout_2026-08-13.md` §3 row 6 notes that in the human
propose-but-verify literature "verification is against an independent referent/scene/discourse cue
-- a channel that can disagree with the proposal mechanism and therefore actually correct it."
That is a real warrant, and it is the useful thing to salvage from S3: what the substrate needs is
**one verification channel that is independent in KIND** (a definitional statement, a sensorimotor
norm, a parse-derived relation), not N databases weighted by a provenance table. Note the same
diagnosis already indicts the live path from the other side -- there, propose and verify "are the
*same statistic* computed twice", which is why PBV could not self-correct.

**The strongest evidence for this verdict is the subsystem's own landed data.** In
`exp_state_of_mind_relevance_gather_reasoning_union_v1` (n=121 real gap targets, recovery@5, disk
`metrics.json` re-read this pass):

| arm | recovery@5 | what it is |
|---|---|---|
| arm0 (single-source structural) | 0.0000 | absent by construction |
| arm1 BLIND UNION fan-out | 0.0413 | baseline |
| **arm2 VOTING** | **0.0248** | raw edge-count frequency vote across the wide pool |
| **arm3 STATE-OF-MIND CUED gather** | **0.3802** | the hippocampal-shaped arm |
| arm3 SCRAMBLE control | 0.0496 | floor (pre-registered <= 0.10) |

Pre-registered bands: delta >= 0.20, scramble <= 0.10, ablation delta >= 0.15; observed delta
0.3388. **The voting arm scored below the blind-union baseline.** Stated with the honesty the
cell itself requires: arm2 is declared "a diagnostic-only control, no HP gate of its own" (cell
header line 9) and is deliberately weakened (frequency count with no fate-awareness), so this is
**not** evidence that corroboration in general fails. It is evidence about which mechanism carried
the win: **the cued retrieval did, and the vote did not.** The subsystem's own best result is its
hippocampal component, not its multi-source component.

**5. Two findings the S3 tests do not surface, both found by reading the cells.**

*(a) The headline ablation is confounded.* The gold gap-set is built by crossing reading facts
with CSKG **narrow** (`/r/MadeOf`) edges (`exp_state_of_mind_..._v1.py:200-221`, `:471`). arm3
queries `hop2_cued`, ingested with **narrow_edges** (`:496`); arm1 queries `hop2_blind`, ingested
with **wide_edges**, any relation (`:493`). So the winning arm's hop-2 store contains exactly the
relation type that *defines gold*, and the baseline's is diluted with every other relation. The
reported ablation delta therefore mixes two variables -- the CA3 gather *and* the retrieval
corpus -- which the project's own DESIGN GATE (one-variable) forbids. The scramble control
permutes the narrow edges' attachment and collapses the arm to 0.0496, which proves the narrow
edge *structure* is load-bearing; it does not separate gather from edge set. The missing arm is
cued-gather over `hop2_blind` (or blind fan-out over `hop2_cued`); neither exists in the cell.
Triple-checked per the evidence-discipline rule: right file (the cell whose `metrics.json` I
read), right version (HEAD; `metrics.json` reproduces the docstring's numbers), right corpus
(one run, both arms), right metric (recovery@5 both), right arms (`:538` vs `:558`). I did **not**
re-run the cell; a detached run is live.

*(b) The corroboration tests measure gate-crossing, not truth.* Grepped for a correctness
measure in all three corroboration cells: `exp_three_tier_loop_independence_weighted_confirm_v1`
and `exp_three_tier_loop_concept_coherence_v1` contain **no gold-standard or held-out accuracy
check at all**. Their HARD_PASS verdicts read "genuine cross-source corroboration NOW crosses the
retain-into-middle gate: closed-form audit 2+-source crossing=36/36" and "21/21 of the previously
-blocked real 2+-source gaps NOW retain". Both are statements about **retention**, and the
closed-form audit is a statement about the arithmetic of a weight scheme whose constants
(1.5 / 0.15 / 0.2 / 2.5) were chosen so that two independent sources cross and no number of
repeats can. The self-test asserts exactly what the constants were selected to produce. The
controls are real and clean (single-source repeat refuses, correlated source refuses, scramble
collapses, reference arm reproduces `n_foundation=40` vs cited 40, `no_leak_ok=True`) -- they
establish that the gate *discriminates as designed*. They do not establish that a corroborated
fact is true. **This is the passing-the-wrong-test failure mode.**

The one landed HARD_FAIL is consistent with all of the above:
`exp_three_tier_loop_genuine_cross_source_corroboration_v1` -->
`HARD_FAIL_thin_cross_source_not_mechanism_failure`, `g_full_combined_promotions=0`, max 3 real
distinct sources per gap against `MIN_CONFIRM=4`, coverage over all 121 gaps `{1: 67, 2: 46, 3: 8}`.
The registry's revival criterion is source thinness. Note what that distribution means: on real
data, **55% of gaps have exactly one source**. A corroboration mechanism is being tuned on a
population that mostly cannot corroborate.

**6. Shared process / duplication.** The independence weighting is honest reuse, not a parallel
build -- it enters through `consolidation_pass`'s existing `trace_weight_fn` hook rather than
reimplementing the gate, and `prelim_tier` is a verbatim promotion of a cell's `TierState`. Credit
that. The genuine duplication is at the CLS level: `three_tier_loop` builds a hippocampus-to-cortex
consolidation path while `hippocampal_encoder` (DG expansion + CA3 autoassociation + replay cycle)
and `continual` (NREM replay) already implement the faithful version and go unused. Also
`gap_driven_reader` ranks prerequisites by **co-occurrence consistency** and ranks reading material
by **lexical occurrence count**, self-described as "deliberately the SIMPLEST possible proxy"
(`gap_driven_reader.py:70-72`) -- a frequency proxy standing where the brain uses
prediction-error-driven exploration, and a third re-derivation of a co-occurrence statistic that
`ConceptSpace` and `random_indexing` already compute.

**7. Wire verdict: SPLIT -- and this is the call the audit exists to make.**

- `ca3_relevance_gather` + `fanout_two_hop` (GATHER, and REASON as a cued retrieval narrower):
  **YES.** Cued pattern completion from a maintained state is brain-faithful, it is the component
  that actually produced the win, and it addresses a real gap in the live path (which currently
  scans the whole anchor matrix).
- The **middle tier** (`prelim_tier`, retain-forever + always-queried-first): **YES in principle**,
  because a fast hippocampal store that accumulates sub-threshold evidence is exactly what CLS
  requires and the live path lacks. **NOT-UNTIL** it consolidates by replay rather than by
  counting -- otherwise wiring it installs the CLS *diagram* without the CLS *mechanism*.
- **Multi-source corroboration / independence-weighted voting: NO.** Not because it fails its
  tests -- it passes them, with clean controls -- but because it is an engineering convenience with
  no neural counterpart, its metric measures gate-crossing rather than truth, and its own data show
  the vote losing to the cued-retrieval mechanism it is packaged with. Wiring it would place a
  provenance-arithmetic proxy at precisely the position where the substrate needs to *reason about
  whether a claim is true*. That is the fault class rule 1 names. If cross-source agreement is
  wanted, the brain-faithful route is convergence: let independent evidence converge on the *same
  representation* and let non-converging content fail to reactivate -- not tally informants.

Recorded so the recommendation is not mistaken for a general dismissal: nothing here says the S3
code is bad or its experiments were sloppy. The controls are among the most careful in the repo.
The claim is narrower and firmer -- **passing a well-controlled test of the wrong quantity does not
license a wire.**

---

## S4. Director KB (7 modules)

**1. What it does.** Builds a large searchable index over notes, preregs, metrics and external
ontologies that the *agent* queries; the substrate never consults it while reading.

**2. Brain system: none -- and that is the correct answer, not a gap.** This is the researcher's
filing cabinet, not part of the modelled cognition. A system that exists to let an agent find its
own notes has no business having a brain analogue, and the fact that it is unreachable from the
live path is a feature. Verified this pass: **no `hdlab/` module outside the `director_kb` cluster
imports it** -- not `reading_grounding_loop`, not `hd_fact_store`, not `atom_consultation`; the
importers are its own CLIs and ~20 experiment cells.

**3. But there is a real fidelity finding inside it, because it claims a mechanism it does not
use.** The docstrings present a substrate-native KG: a `KGStore` with entity codebook `E`,
relation codebook `R` and a Hebbian triple matrix `W`, ingested at `director_kb.py:1047-1082`.
Retrieval does not touch any of it. `DirectorKBQuery` computes a single dense cosine over all
1,288,991 entity vectors (`director_kb_query.py:302-316`, chunked at 100k purely to bound memory)
and takes a top-k (`:336-340`). `self.W` appears at lines 146, 152, 154 and **is never read after
being loaded**; the file's own comment concedes it (`:148-150`: "W matrix is loaded but only used
for confidence sanity"). `self.R` likewise. So a 16.8 MB Hebbian relational store is built,
persisted, loaded per query, and ignored -- **the relational machinery is decorative.**

**4. SHAPE / POSITION / METRIC, and the divergence that actually matters.**

| | ours | brain's |
|---|---|---|
| SHAPE | Entity vector = `sign(sum of blake2b-seeded random bipolar vectors, one per character trigram)` (`char_trigram_encoder.py:38-102`). No learning of any kind -- no counts, no PMI, no gradient. Similarity = cosine between two sign-bundled **bags of character trigrams**. | -- |
| METRIC | Orthographic form overlap. | -- |

Here is the sharp version, and it maps onto a real neural distinction. **What this computes is
VWFA-level similarity** -- sub-lexical orthographic form, the left occipitotemporal visual word
form system -- and in the brain that region is emphatically *not* the semantic system; semantic
access requires the ATL hub. The KB is a VWFA with no hub. The encoder's own docstring states the
consequence: "cat/cats/kitten share no trigrams -- would NOT match" (`:18`). **This is the retrieval
quality ceiling of the entire 10.6 GB artifact, and no amount of scale moves it.** (Minor
secondary: `blake2b(digest_size=4)` gives a 32-bit seed space, so trigram-vector collisions become
likely well inside this corpus's trigram count; `token_vocab.py:54-65` deliberately uses
`digest_size=8` and documents the birthday bound, so the repo knows the issue.)

**Severity: DIVERGENT-BUT-COMPATIBLE as a tool** (a tool needs no fidelity), **but the
substrate-native framing in its docstrings is unearned** and should not be cited as evidence that
the substrate does KG retrieval.

**5. Shared process / duplication -- the clearest encoder duplication in the repo.** Four modules
define byte-for-byte identical `_seed_for_*` / `_bipolar_hv` pairs (`char_trigram_encoder.py:38,44`;
`char_positional_encoder.py:49,55`; `vwfa.py:60,65`; `token_vocab.py:54,68`). More than shared
boilerplate: **`vwfa` strictly subsumes `char_trigram_encoder` as a parameter setting**, and says
so itself -- "VWFA(scales=[3], bind_position=False, sign_bundle=True) has THE SAME STRUCTURE as
CharTrigramEncoder" (`vwfa.py:37-43`) -- while also subsuming most of `char_positional_encoder`
(position binding is a flag). So three implementations of one parameterised mechanism, with the
general one SHELVED and the narrowest one carrying a 10.6 GB index. `random_indexing` is genuinely
distinct (it is the only one of the five that *learns* -- a mutable accumulating context vector);
`token_vocab` is a vocabulary manager, not a text encoder.

**6. Operational note, recorded because it bears on the recovery ritual.** The workflow
`CLAUDE.md` prescribes at session start (`--filename-contains POST_COMPACTION_BACKUP`) takes the
**bypass path**: a literal Python substring scan over entity names with a date sort, confidence
hard-coded to 1.0, which "BYPASSES cosine ranking entirely" (`director_kb_query.py:384-387`,
`:418-438`). The load-bearing retrieval is `grep` with extra steps. Meanwhile the index is
rebuilt from scratch on any source mtime change (193 rebuilds so far, ~32 min each), invalidating
a ~5.3 GB fp16 query cache that is not currently on disk. Not a fidelity matter; a cost matter,
and worth someone's attention.

**7. Wire verdict: NO -- by design, and it should stay that way.** Wiring an orthographic
similarity index into the reading path would install exactly the fault this audit names elsewhere:
a form-similarity proxy where meaning is required. Keep it as an agent tool.

---

## S5. Goal / desire narrative organs (11 modules)

**1. What it does.** Decides who wanted what in a story, and whether they got it.

**2. Brain system.** Goal representation and maintenance is **vmPFC/OFC** (subjective value and
outcome expectancy) with **dorsal ACC** monitoring goal-outcome discrepancy, over an **mPFC/TPJ**
mentalising network that attributes desires to agents. The decisive property: goal states are
**maintained top-down and condition interpretation** -- the brain does not extract an outcome and
then compare it to a goal; the goal is already shaping what counts as an outcome.

**3. SHAPE / POSITION / METRIC.**

| | ours | brain's |
|---|---|---|
| SHAPE | A hard-coded precedence cascade: `relation -> valence -> majority`, then a one-directional contrast override, then two opt-in fallback channels (`goal_achievement.py:341-400`). When neither channel fires, the verdict is `MAJORITY_CLASS` -- a **base-rate guess** (`:380`). | Graded value/expectancy comparison against a maintained goal state; no default class. |
| POSITION | **Bottom-up**: extract an outcome event, type it, then compare to the goal. | **Top-down**: the maintained goal conditions the interpretation. `director_brain_fidelity_audit_shape_position_metric_2026-08-09.md` puts it exactly: "there is no goal-free 'outcome event' to extract". |
| METRIC | Verdict-class accuracy / macro-F1 on annotated pairs. | Whether the reader's inference about the agent's satisfaction matches a human's. |

**4. Divergence and severity: ARCHITECTURAL-FAULT on POSITION -- but this is a standing verdict,
already adjudicated, and the adjudication corrected itself in a way this note must preserve.** The
08-09 audit hypothesised that top-down conditioning was the fix; its own same-day synthesis
overturned that: "**The readout, not the conditioning, is the bottleneck -- confirmed EMPIRICALLY**",
with the top-down probe failing its control outright (real **0.613** vs **scrambled 0.704**) and
"pure top-down conditioning alone" explicitly rejected
(`director_brain_fidelity_SYNTHESIS_and_direction_verdict_2026-08-09.md`). So the correct statement
is: the position is unfaithful, *and* fixing the position alone has been tested and does not work.
The missing leg named there -- goal as a **utility/preference function** (Baker/Saxe/Tenenbaum) --
"has NO analog in the current pipeline", and a crude graded-utility probe landed 0.278 against
pre-registered bands HARD-PASS >=0.40 / HARD-FAIL <0.15, i.e. MIDDLE.

Numbers with their floors: the 3-channel organ scores **0.688 accuracy** against a derived **human
ceiling of ~0.77-0.87** (not the 0.66 three-way-unanimity figure, which the synthesis note records
as its own conflation error). The union-OOV channel that is wired by default measured macro-F1
**0.6992 -> 0.7248 (n=80)** and **0.6623 -> 0.6875 (n=160)**, abstain-cohort recovery **5/8 = 0.625
vs M2-alone 3/8 = 0.375**, with pairscramble collapsing (`goal_achievement.py:365-369`). Those are
real, controlled, modest gains.

**5. Scaffold density, measured this pass.** Counting module-level constant tables with >=15 string
literals: `idiom_grounding._RAW_IDIOMS` **117 entries**, `goal_achievement._ENTITY_STOPWORDS` **114**,
`goal_outcome_relation._MWE_WIDTH1_LIGHT_VERB_STOP` **62**, `result_type_induction.POOL_STAGES` **59**,
`goal_achievement._AUX_STOP` **41**, `quality_relation._ENGAGE_NEG` **33**,
`goal_outcome_relation.LIGHT_STOP` **32**; `goal_outcome_relation` alone carries 15 module-level
tables. This is class (B) scaffold in the vocabulary of
`brain_fidelity_audit_comprehension_pipeline_2026-08-02.md` -- brain-compatible in function,
hand-authored rather than learned -- and that note's scaling tell applies: the cue-discovery step
has been hand-authored every time.

**6. The self-test FAILURE is an improvement, not a regression -- and this is worth getting right.**
The census reports `python -m hdlab.goal_achievement` failing with
`AssertionError: channel 'relation:recur' != 'majority'`. Located at HEAD: the pinned fixture is
`("I wanted to meet my friend.", "I met up with my friend.", "Fulfilled", "majority")`
(`goal_achievement.py:409`), and the line above it explains the pin -- "-> majority; verdict still
correct. **Documents the gap honestly** rather than asserting a fire" (`:408`). The pin therefore
records a *known non-detection*. That gap has since closed (`lemma_verb("met")` now returns `meet`,
so the relation channel fires), the verdict `Fulfilled` is unchanged and still correct, and the test
fails because the system got better than its own pinned expectation. Certification is RED on `main`
for this and one derived pytest failure. It is a stale pin, not a broken mechanism -- but it is RED,
and a red suite is a red suite.

**7. Shared process / duplication.** `goal_owner_select.GeneralRecencyEntityResolver` is the seventh
antecedent selector (see D1), and the deliberately-unfixed twin problem documented there lives in
this subsystem. `goal_typing` -- which *is* on the live path -- is the organ this cluster's logic
mostly reaches the substrate through; the other ten are not in the closure. Valence/polarity tables
appear independently in `context_grounded_valence`, `quality_relation` and
`wordnet_polarity_propagation` (S7).

**8. Registry mismatch to carry.** Two rows claim `WIRED_AND_PIPELINE_USED` for `goal_owner_select`
(`goal_owner_select_component5_directed_score`, `goal_owner_full_selector_enumerate_argmax_tiebreak`)
while the module is **not** in the live runtime closure -- two of the three false
`WIRED_AND_PIPELINE_USED` claims the census identified are in this subsystem.

**9. Wire verdict: NOT-UNTIL-X.** The organs work, are controlled, and produce modest real gains,
so this is not a NO. But X is specific and is not "wire more channels": the subsystem's own
adjudicated diagnosis is that the **read-out** is the bottleneck and that adding top-down
conditioning alone has already failed its control. Until there is a graded utility/preference
representation -- the leg identified as absent -- adding more precedence channels to a cascade that
falls back to a base-rate guess buys accuracy without buying fidelity.

---

## S6. Coreference / situation model (10 modules)

**1. What it does.** Tracks which later mentions refer to which earlier entity, and holds a running
model of the described situation.

**2. Brain system.** **Hippocampal relational binding and antecedent retrieval** (the same
episodic-index machinery that supports "which thing was that"), operating over a **PFC working-memory
register** that maintains a small number of discourse entities, updated by **prediction error at
event boundaries** (Zacks' event-segmentation theory; Kurby & Zacks). The prior corpus is emphatic
that the live `coreference_resolver` -- Centering Cb plus Principle B -- is **FAITHFUL at Marr's
algorithmic level** and is the single organ every generation of audits agrees on
(`goal_owner_attribution_pipeline_brain_fidelity_audit.md` Component 2;
`brain_audit_SYNTHESIS_missing_semantic_organ.md`). That verdict stands and this note does not
disturb it.

**3. SHAPE / POSITION / METRIC (the ten shelved modules, not the live organ).**

| | ours | brain's |
|---|---|---|
| SHAPE | One scalar, everywhere: `salience = count + 0.5 * exp(-0.1 * (now - last_mention))` (`state_of_mind.py:245-247`, constants at `:125-127`), then argmax. Centering is approximated by additive hand-set weights `CENTER_SUBJECT_W=2.0`, `CENTER_PARALLEL_BONUS=0.5` (`coref.py:119-120`). | Graded activation over a maintained discourse model, with structural constraints (information status, Cb/Cf transition type) doing real work, not a weight. |
| POSITION | Entity state is **append-only**: `mention_midxs.append(midx)` plus filling a `None` gender (`state_of_mind.py:313-322`; `coreference_resolver.py:265-283`). Nothing is ever revised in light of later evidence. | The discourse representation is *updated* -- reinterpretation on disconfirming evidence is the defining behaviour. |
| METRIC | Hand-built fixtures. `coref_distractor_suppress` asserts `acc_on >= 0.99` on a 3-target toy and `all(h == "anna")` (`:368-370`); `situation_reader` asserts `by_pred["feared"].subj_role == "EXPERIENCER"` on typed-in CoNLL rows (`:731`). | Behavioural accuracy on natural discourse. |

**4. Divergence and severity: ARCHITECTURAL-FAULT**, on two counts.

*(a) Nothing updates.* An append-only counter is not a situation model. The only two modules that
implement a genuine dynamic state-update are `slot_attention_wm` (prediction-error-gated bistable
slot write, `:193-228`, with learned `write_theta` and annealed `tau` -- exactly the right shape)
and `entity_slot_gate` (gated Hebbian write, `:78-92`). The first has **no training loop, no
self-test and no verification witness**; the second **HARD_FAILED its own mandatory control** --
random-init untrained nets matched the trained version (`:132-134`), i.e. structure, not learning.
So the faithful shape exists twice, is untested once and refuted once, and the shipped mechanism is
a counter.

*(b) The whole stack runs on oracle mentions.* `parse_litbank_conll` takes mention spans **and gold
cluster ids** from the gold coref column (`coref.py:175-189`), and "subjecthood" is *linear order
within the sentence* (`:230-234`), not a parse. So every S6 coref number presupposes perfect mention
detection and a positional subject heuristic. That is a scope caveat that must travel with any
figure from this subsystem.

Two further proxies worth naming because they look like mechanisms: scene segmentation is a
**55-entry hand-written list of leading n-grams** ("meanwhile", "the next day",
`scene_segment.py:74-101`), and referentiality is a **39-word quantifier stoplist** plus
"was this head ever mention-rank-0" (`coref_distractor_suppress.py:124-134`). And in
`event_centrality_coref`, the HD layer looks load-bearing but is not: `query_bundle` is a lossless
re-read of a symbol table whose contents were fixed by the positional heuristic, and the decision
is a hand-weighted vote (`AGENT_W=2.0 / PATIENT_W=1.0`, `:135-162`). Its registry row records the
honest negative -- event structure **loses** to plain recency, crux delta **-0.0469**.

**5. Shared process / duplication -- the worst in the repository, and it is not close.**

**At least seven implementations of gender-filtered recency/salience antecedent selection live in
`hdlab/`**: `state_of_mind.WorkingOverlay`, `coref.CorefReader`,
`coref_distractor_suppress.SuppressReader`, `scene_segment.SceneProtagonistReader`,
`event_centrality_coref.EventCentralityReader`, `bundle_focus_coref.BoundedEntityFocus`,
`coreference_resolver`'s five `run_*` variants, and `goal_owner_select.GeneralRecencyEntityResolver`
(`goal_owner_select.py:205-250`, an explicitly byte-copied resolver). Four of them form a
single-inheritance chain in which each subclass **copy-pastes `resolve_stream` and inserts one
branch** (`coref.py:661-679`, `coref_distractor_suppress.py:283-299`, `scene_segment.py:376-389`,
`event_centrality_coref.py:341-355`), and `_centering_pick` appears verbatim in two files
(`coref.py:534-555`, `coref_distractor_suppress.py:173-190`). Separately there are **eight distinct
entity-state stores**. The live `coreference_resolver` imports the very same two constants from
`state_of_mind` and computes the identical salience (`:190-192`) -- so this is one mechanism wearing
seven costumes. The brain reuses one antecedent-retrieval circuit; this is the textbook parallel
build, at scale.

One naming correction to carry: `working_memory.py` **contains no working memory**. It is five
envelope constants plus two guard functions that raise `ValueError` on out-of-range sizes
(`:42-111`). The registry describes it as a "multi-bank K-item capacity primitive (chain-grade
K=4096)"; that primitive is not in this file. And `state_of_mind.py`'s own docstring concedes its
name is a mislabel ("NOT THEORY-OF-MIND ... ZERO belief logic", `:3-8`).

**6. Wire verdict: NO for all ten.** Not on convenience grounds -- on fidelity. Wiring any of them
adds an eighth copy of a mechanism the live path already has in its most faithful form
(`coreference_resolver`, Centering + Principle B, the organ the audits endorse). The single
exception worth a **NOT-UNTIL-X**: `slot_attention_wm` is the only implementation of the update
dynamics the subsystem actually lacks, and X = it gets a training loop, a witness, and the same
random-init control that refuted its sibling. Absent that control it must not be wired, because its
sibling shows exactly how this shape fails.

---

## S7. Word / script acquisition loops (6 modules)

Read personally (this subsystem's investigating agent died mid-run on an API error; I did the
reading rather than leave the section on inference).

**1. What it does.** Learns a new word's meaning from what happens after it in a story, optionally
seeded by a dictionary lookup; and the same idea at the level of multi-step scripts.

**2. Brain system.** Two routes that the brain genuinely does pair: **fast declarative acquisition
from an explicit source** (the dictionary half) and **slow experiential learning from consequence**
(the corpus half) -- again CLS, and `word_learning_tool`'s framing of it is correct. The script half
maps to **DG pattern separation feeding CA3 pattern completion**, and `dg_pattern_separation.py`
cites the causal, not merely correlational, evidence for that division: Leutgeb et al. 2007 (DG
rate-remapping decorrelates similar contexts far more than CA3/CA1) and Guzman et al. 2016
(optogenetic silencing of DG granule cells impairs discrimination of *similar* but not *dissimilar*
contexts). That is the best-sourced brain claim in the whole audit.

**3. The architecture is more faithful here than almost anywhere else, and it is contradicted by
its own results.** `word_acquisition_loop`'s design (`:1-22`) is a genuine multi-channel acquisition
loop: PROPOSE via `predictive_coding.threshold_gate` (a real prediction-error trigger -- note this
is the organ the *live* path lacks), CHANNEL A structural MDL construction induction via
`hdlab.learner`, CHANNEL B affective appraisal through a frozen reward-trained theta, CONSOLIDATE
by confirmation count plus an abstain band, WRITE-BACK into a Tier-3 overlay. Shape, position and
channel independence are all defensible.

**4. And it HARD_FAILED, with the controls making the failure unambiguous.** Off
`data/exp_combined_dictionary_consequence_word_learning_tool_v1/metrics.json` this pass:

| arm | 3-way accuracy |
|---|---|
| dictionary alone | 0.2222 |
| consequence alone | 0.1944 |
| **combined** | **0.1944** |
| pre-registered floor | **0.6389** |
| empty baseline | 0.1667 |
| scrambled dictionary | 0.1722 |
| **scrambled consequence** | **0.2056** |

Read that last row: **the scrambled consequence arm outscored the real one** (0.2056 vs 0.1944), and
every arm sits within a few points of the 0.1667 empty baseline while the floor is 0.6389. Combining
the two channels did not beat either channel alone; it matched the worse one. Dictionary coverage
was **6/33 lemmas (3/16 content)**. This is not a near-miss -- the mechanism is not distinguishable
from its own scramble control.

**5. The most consequential finding: the DG fix was built and never wired into the organ it was
built to fix.** `dg_pattern_separation.py` exists because `script_grain_acquisition_loop`'s keying
step calls `cleanup_family.iterative_attractor` -- CA3 pattern *completion* -- **with no upstream
pattern-separation stage**, so at 195-way scenario cardinality similar registers collapse into
catch-all basins (measured: `n_items_spawned_total=35`, mean item purity ~0.19-0.20, and the
compounding curve *degrades* with exposure: real_final **0.5538 < baseline 0.5859**). The module
diagnoses this precisely and implements the missing stage. **Verified this pass:
`script_grain_acquisition_loop` does not import `dg_pattern_separation`** -- grep over all of
`hdlab/` returns only the module itself and an unrelated self-test in `hippocampal_encoder`. Its
consumers are ten-odd experiment cells.

This is the audit's recurring pattern in its purest form: **the fault was correctly diagnosed, the
brain-canonical fix was correctly built and correctly cited, and the organ with the fault still
does not call it.** It also independently reproduces the standing correction (a) from
`research_context_binding_..._2026-08-11.md` §1b -- that bind must be preceded by DG sparse
expansion -- at a second, unrelated site.

**6. Proxy flags.** `wordnet_polarity_propagation` -- the only live dictionary call in the
repository -- infers polarity by **max `path_similarity` vote against a 52-word hand-curated anchor
set**, with antonym opposition taking precedence and a hand-set neighbour floor and vote margin.
That is a lexical-graph similarity vote standing where word meaning should be, and it returns a
*polarity for an outcome verb*, not a definition. Calling this "looking the word up" overstates it.

**7. Wire verdict: NO for the tool as measured** (its own HARD_FAIL and scramble controls settle
it), **NOT-UNTIL-X for the loop** (X = a channel that is independent in kind rather than a second
statistic over the same lexicon; the dictionary channel at 6/33 coverage is not that channel), and
**YES on fidelity for `dg_pattern_separation` into `script_grain_acquisition_loop`** -- it is the
right component, in the right position, with causal brain evidence, addressing a measured defect in
a named organ. That is as clean a wire case as this audit produces.

---

## S8. Encoders (10 modules)

**1. What it does.** Turns text into hypervectors -- character n-grams, PPMI factorisations,
concept prototypes, and stream combination.

**2. Brain system.** The intended mapping is the reading ventral stream: **VWFA** for sub-lexical
orthographic form, feeding an **ATL semantic hub** that integrates modality spokes, with
`late_combine`/`composed_encoder_v3` framed as the **N400 late-integration** stage. The form end of
that map is honest; the hub end is where it breaks.

**3. The decisive finding: essentially nothing here is learned, and the one module that claims a
learning rule does not implement it.**

`concept_encoder.py` is documented as competitive-Hebbian. Its training loop
(`concept_encoder.py:491-523`) mean-centres the corpus, **sums each label's surface vectors into a
class centroid**, keeps the top-2% coordinates by magnitude, and takes the sign. There is **no
competition** -- no lateral inhibition, no anti-Hebbian term, no winner-take-all update, no
iteration; it is one closed-form pass. And `learning_rate` (default 1.0) **cannot change the output
at all**: it multiplies every accumulator uniformly, so it cancels in both the magnitude ranking and
`np.sign`. A dead parameter is presented as the Hebbian learning rate. Inference then returns the
matched prototype row verbatim (`:567-576`) -- so the "encoder" emits a **nearest-prototype id**,
not a representation of its input. The docstring is honest that concept identity comes from the
supervised integer label (`:12-31`); the *mechanism name* is what misleads.

This matters beyond one module because `concept_encoder` is the module the registry row
`composition` marks `WIRED_AND_PIPELINE_USED` -- one of the three pipeline-status claims the census
measured as false.

The rest, precisely: `vwfa`, `char_positional_encoder`, `char_trigram_encoder` and `token_vocab` are
**fixed hash-seeded random codebooks with no `fit` at all**; `ppmi_sparse_encoder` fits PPMI+SVD but
over **concept labels, not contexts**, so `target_dim = min(n_dim, V, C)` caps the embedding at rank
<= number of labels (~50) zero-padded to 2048 (`:159-160`) -- its own self-test asserts the collapse
(`:324`); `composed_encoder_v3` builds class centroids again and fuses two cosines with hand-set
alpha/beta (`:230`); `late_combine` fits **one scalar** by an 11-point grid search (`:118-179`);
`whitening` is the only classical statistical fit (ZCA over second-order statistics, `:56-85`) and
has **no self-test and no witness**; `gsbc_graded_encoder` requires an **external neural teacher**
and fail-louds without one (`:108-116`); and `encoder_retrain_persist` is a *loader* for the only
genuinely gradient-trained artefact (a 3.15M-parameter top-layer unfreeze, checkpoints on disk,
trained on a **synthetic** situation-model harness, its own self-test asserting only that the
checkpoint loads -- "No accuracy claim here").

**4. Severity: ARCHITECTURAL-FAULT**, and it is the same fault as S9(a) seen from the other side.
The ATL hub's defining property is a **learned, similarity-structured** representation in which
related concepts overlap. What this subsystem supplies is either a random equidistant basis or a
supervised class centroid. A prototype bank keyed by a supervised label cannot be the hub, because
the labels are the thing a hub is supposed to explain. The prior corpus reached the same place by a
different route and with a decisive control: on this representation even a **supervised**
nearest-centroid sense classifier scores **0.5167 against a 0.5625 floor**, so "the failure is
REPRESENTATIONAL (signal absent), not a clustering/induction defect"
(`brain_fidelity_vet_components.md` Part A). Same-vs-different-sense cosine separation: **0.003-0.005**.

**5. Metric flag.** Nearly every S8 self-test measures a *property of the construction* on a
synthetic fixture, not a capability: `concept_encoder`'s headline assert reproduces **a previous run
of itself on its own generated corpus** (`0.492 +/- 0.05`, `:1036`); `composed_encoder_v3` asserts
`correct >= 4` out of 5 on a 5-concept toy (`:387`); `vwfa` asserts that it *cannot* see synonymy
(`:343`) -- honest, but a property assertion on four typed-in strings. No real corpus appears in
any S8 self-test.

**6. Duplication.** See S4: `vwfa` subsumes `char_trigram_encoder` and most of
`char_positional_encoder` as parameter settings, by its own docstring. Class-centroid prototype
construction is implemented independently in `concept_encoder` and `composed_encoder_v3`.

**7. Wire verdict: NO for the cluster as it stands** (registry already SHELVES the
`vwfa`/`ppmi`/`composed_v3` row, and that is the right call for the right reason). **NOT-UNTIL-X for
the one thing this subsystem is actually needed for**: X = an encoder whose similarity structure is
*learned from grounded evidence* rather than from supervised labels -- the sensorimotor norms already
on disk (`notes/sensorimotor_anchoring_scope_2026-08-13.md`) are the nearest available spoke.
`encoder_retrain_persist` keeps its WIRE status but its scope caveat must travel with it: synthetic
harness, naturalistic-text validation pending.

---

## S9. VSA/HDC core primitives, memory and reasoning (44 modules)

**1. What it does.** The algebra the whole substrate is built on -- bind, bundle, cleanup -- plus a
large library of stand-alone brain-analog primitives promoted out of individual experiments.

**2. Brain system.** The algebra claims to model **distributed population coding** with
**conjunctive binding** and **attractor-based cleanup** -- i.e. cortical population codes, the
DG/CA3 conjunctive expansion, and recurrent attractor dynamics.

**3. Is the algebra genuinely brain-shaped, or a convenient formalism? Component by component.**

| primitive | ours | brain | verdict |
|---|---|---|---|
| **bundle** (`bundling.py:11-45`) | sum of vectors, then per-component magnitude renormalisation (FHRR) or L2 (HRR); optional geometric recency decay from modulator state | superposition in a population code is real; **divisive normalisation** is a canonical cortical computation (Carandini & Heeger), and recency weighting is real | **FAITHFUL** in shape |
| **bind, FHRR** (`binding.py:31-40`) | elementwise complex multiply = phase addition; **dimension-preserving** | the best-evidenced brain shape is **dimension-EXPANDING conjunctive coding** (mixed selectivity, Rigotti 2013 / Fusi 2024; item-place conjunctive cells, Komorowski 2009), which is a different algebraic family. Phasor VSA does have a spiking implementation (Frady & Sommer) -- but that is *implementability*, not *occurrence in cortex* | **DIVERGENT**; see standing verdict below |
| **bind, HRR** | circular convolution via FFT | no direct neurophysiological evidence for any convolution-family operator | **convenient formalism** |
| **bind, BSC** | elementwise multiply of bipolar vectors, self-inverse | XOR-class binding; no direct mechanism | **convenient formalism** |
| **factorization** (structure separable from content) | a property of the algebra, not a separate op | genuinely supported -- TEM (Whittington 2020), Baldassano/Hasson/Norman 2018, Bernardi 2020 | **FAITHFUL**; the strongest part of the representation pillar |
| **cleanup** (`cleanup_family.py`) | five primitives incl. classical Hopfield (Hebbian outer product + sign update) and modern Hopfield (softmax, Ramsauer 2020); `iterative_attractor` is softmax-attractor settling (`iterative_attractor.py:1-33`, citing Amari/Wilson-Cowan, Marr, Treves-Rolls, Krotov-Hopfield) | recurrent attractor dynamics in CA3 and in cortical local circuits | **FAITHFUL** in shape -- the citations are accurate and the primitives really do implement them |

So the algebra is **not** merely a convenient formalism, but the defensible part is narrower than
the code's framing suggests: **bundling, cleanup and factorization are genuinely brain-shaped; the
bind operator is not.**

**This conforms to a standing verdict rather than announcing a new one, and I am correcting my own
first draft against it.** `research_brain_fidelity_architecture_audit_2026-08-09.md` row 7 puts
`P(any convolution-family operator, FHRR included, is neurally faithful as the binding SHAPE)
~0.15` against `P(conjunctive/outer-product is better-supported) ~0.75`, on the specific ground
that convolution is dimension-preserving while conjunctive coding is dimension-expanding -- "a
structurally DIFFERENT algebraic family". The same corpus forbids two rescues I was drafting:
binding-by-synchrony is not available as a justification ("do NOT justify our binding via
synchrony", `research_brain_fidelity_broad_audit_synthesis_2026-08-01.md` §2a; largely refuted as
a general cortical mechanism), and spiking implementability (Eliasmith NEF, Frady & Sommer) is an
existence proof, not evidence of occurrence. An earlier note's rescue -- that convolution-bind is
"better modeled as a conjunctive-coding analog" (`brain_fidelity_audit_and_path_to_fully_capable_
comprehension_2026-08-02.md` A4) -- was superseded by the 08-09 audit, which is later, adversarial,
code-and-primary-source checked, and contains its own self-retraction. Standing house style, which
this note follows: never write "the brain uses FHRR".

**The sharpest form of the finding: the repo owns the better-supported shape and does not use it.**
`hippocampal_encoder.DGProjection` is exactly dimension-expanding conjunctive coding -- random
expansion, top-K sparsify, sign (`hippocampal_encoder.py:5-8`). Its only importers are its own
module and a set of 2026-07-03 experiment smokes; no other `hdlab/` module imports it, and it is
not in the live closure.

**4. Where it diverges -- two faults, one of them the deepest in the audit.**

**(a) ARCHITECTURAL-FAULT: the atom basis is random, fixed, and dense; the only learned structure
is first-order co-occurrence.** `atoms.make_atoms` draws i.i.d. uniform phases or Gaussians
(`atoms.py:28-45`); `KGStore` draws bipolar entity codebooks (`kg_traversal.py:62-65`);
`context_vector` draws a sha256-seeded bipolar vector per word. Consequence: **all concepts are
a priori equidistant.** The representation of a word carries no information about what it means;
every scrap of semantic structure must be carried by an association matrix or by overlap in
accumulated context bundles. `ConceptSpace` does learn -- but what it learns is a sum of random
word vectors, i.e. a count-based distributional model (`reading_grounding_loop.py:405-450`).

The brain's semantic representations are learned *and similarity-structured*: related concepts
have overlapping population codes, which is the basis of semantic priming and of graded category
structure, and the ATL hub is organised by that similarity. A random equidistant basis cannot
express it. **This is the same fault as S1's, one level down**: it is *why* the meaning read-out
degenerates to "which known word co-occurred most". The two are not separate problems.

Sparsity is a second-order version of the same divergence: brain codes are sparse (~1-3% active in
DG); these atoms are dense. `hippocampal_encoder`'s `DGProjection` does the faithful thing --
random *expansion* then top-K sparsify then sign -- and is not on the live path.

**(b) The attractor is present in form and absent in function.** The live path calls
`iterative_attractor` and then uses only `diag["final_argmax_idx"]`, discarding the settled state
(`gap_detector.py:111-118`; `gather_reason.py:103-112` does the same). For `gap_detector` this is
deliberate and correctly argued. The net effect at the system level is nonetheless that an
8-step softmax settling procedure is being used as a one-shot argmax.

Worse, one live-path organ does not even run the attractor. `hd_fact_store._cleanup` -- in the
live closure -- is a bare `argmax(cb @ filler_hat)` (`hd_fact_store.py:205-211`). That is precisely
the shape `research_context_binding_conjunctive_coding_and_replay_necessity_2026-08-11.md` §1b
names as "the exact 'two discrete steps' shape the literature flags as the biggest fidelity
mismatch", with the fix already specified (use `cleanup_family.iterative_attractor`) and not
applied. Note the position distinction the standing corpus insists on, which this note honours:
cosine-argmax is a CRITICAL fault at the *meaning-selection* position (S1), a flagged debt at the
*entity-tracking readout* position, and **not** a fault as *cue-dependent retrieval* -- so
`gather_reason`'s use of it inside a cued peel loop is not indicted here.

**(c) The live path spans two algebra families that do not compose.** Verified this pass:
`situation_model_accumulate.unit_phase_vec` returns FHRR `complex64`
(`situation_model_accumulate.py:32-35`), while `event_bundle`, `hd_fact_store` and `gap_detector`
operate on bipolar `{-1,+1}` BSC (`event_bundle.py:36,46-48`). All four are in the live closure.
This corroborates `research_brain_fidelity_architecture_audit_2026-08-09.md` row 7's observation
that "the 'representation pillar' currently spans TWO algebra families that do not compose", and
locates it on the live path rather than in the library.

**5. Shared process / duplication -- the 44 modules are largely a museum.** Only 8 of 44 are
live-reachable (`atoms, binding, bundling, cleanup_family, iterative_attractor, modulators,
ablation, semantic`). The unwired 36 include the most brain-faithful organs in the repository,
each correctly cited: `hippocampal_encoder` (Marr 1971 DG/CA3 + replay), `predictive_coding`
(Rao-Ballard/Friston), `temporal_trace` (Foldiak 1991), `excitability` (CREB / synaptic
tag-and-capture), `continual` (NREM replay), `modern_hopfield_readout` (Ramsauer 2020). Every one
of them duplicates -- more faithfully -- a function the live path performs with a counter or a
cosine. That is the audit's structural finding about S9: **the substrate's fidelity problem is not
that faithful mechanisms were never built; it is that the built ones are not in the path.**

The single sharpest instance, and it is not new -- it has been on the record for over two weeks.
`hippocampal_encoder.cls_discrete_budget_consolidate` implements the faithful consolidation loop
(recency-decayed fast store, fixed per-phase replay budget, SWR-style partial-cue reactivation
`cue = rho*key + sqrt(1-rho^2)*noise`, CA3 completion, Hebbian write into a *separate* slow store).
It is certified HARD_PASS at **gap 0.913 old-retention against a naive-consolidation control**
(`consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md` §0/§3.1, commit `92e01cf3f`), and
that note's verdict on wiring it was "**Cost: wiring, not invention.**" Consumers, verified this
pass: `hdlab/hippocampal_encoder.py` itself, one experiment
(`exp_unified_self_learning_loop_v6_replay_consolidation.py`) and one verification test. **No live
path calls it, sixteen days on.** Every "S3 should be wired / CLS is implemented" claim should be
read against that fact.

A vocabulary trap makes this easy to miss, and it is worth stating once for the whole audit. The
registry row `hippocampal_encoder_dg_ca3_pipeline` reads `integration_status: WIRED` with
`revival_criteria: "n/a -- already wired via real consumers"` -- while its own
`pipeline_status` is `WIRED_BUT_NOT_PIPELINE_REACHABLE` (read verbatim from
`data/capability_registry.jsonl` this pass). **In this registry "WIRED" means "has consumers
somewhere", not "on the live path"**, and the consumers here are experiment cells. A reader
skimming `integration_status` would conclude the CLS pipeline is wired. It is not.

Registry-declared dead ends to leave alone: `reasoner` (`built_2026-07-25_then_abandoned_2026-07-27`,
SHELVE), `k_cliff_scaling` and `profiling` (zero consumers, never demonstrably executed).

**6. Metric flag.** Most S9 primitives are judged on recovery/capacity against random codebooks --
can you retrieve vectors you stored. That is a valid test *of the algebra* and no test at all *of
representation*: it is self-referential in the same way S1's split-half cosine is. Passing says the
storage works, not that anything is meant.

**7. Wire verdict.**
- Core algebra (`atoms/binding/bundling/cleanup_family/iterative_attractor`): **already wired,
  keep.**
- `hippocampal_encoder`, `predictive_coding`, `continual`: **YES on fidelity** -- each is the
  faithful version of something the live path currently fakes, which is the strongest possible
  wire argument. Sequenced behind the S1 read-out fix, because wiring a better novelty signal
  under a broken candidate set will produce another floor-limited null.
- `temporal_trace`, `excitability`, `modern_hopfield_readout`: **NOT-UNTIL** a named consumer
  exists; they are faithful but currently unmotivated by any live deficit.
- The random-atom basis: **not a wire question, an architecture question.** No amount of wiring
  fixes an equidistant basis; a learned similarity-structured encoder (S8) or an external grounding
  spoke (the Lancaster/Brysbaert norms already on disk,
  `notes/sensorimotor_anchoring_scope_2026-08-13.md`) is the structural answer.

---

## S10. Glass-box parser front-end (5 modules)

**1. What it does.** The project's own POS tagger and dependency parser, trained in-repo on real
annotated data, with no spaCy/NLTK parser dependency.

**2. Brain system.** The **left perisylvian syntactic network** -- LIFG/BA44 and posterior STS,
with the dorsal (arcuate) stream carrying hierarchical structure building (Friederici's model).
Timing matters here: syntactic structure building is fast (ELAN/P600) and, critically, it
**feeds forward into and constrains** semantic integration.

**3. SHAPE / POSITION / METRIC.** This is the one subsystem where the metric is right by default.

| | ours | brain's |
|---|---|---|
| SHAPE | `pos_tagger`: averaged structured perceptron (Collins 2002) over a hand-written emission template + first-order transitions, **exact Viterbi** decode (`perceptron.py:66-131`). `arc_parser`: hashed arc-factored averaged perceptron, **greedy per-token argmax + cycle-breaking** (`:135-183`) -- *not* MST, despite `reading_grounding_loop.py:281` saying "Viterbi/MST decoding". `arc_labeler`: 36-way linear argmax per arc, no tree consistency. | Incremental, predictive, cue-integrating structure building; not a per-arc independent scorer. |
| POSITION | Correct and, unusually, actually upstream on the live path (lazily imported at `reading_grounding_loop.py:300-303`). | Correct. |
| METRIC | **Real accuracy on real annotated data.** UD-EWT; measured **UAS 0.7868 base / 0.7925 rich** (dev n=1989, train n=12329, `data/exp_parser_uas_ladder_richfeat_v1/metrics.json`). | Behavioural/neural correlates. |

**4. Severity: DIVERGENT-BUT-COMPATIBLE, and the best-founded subsystem in the audit.** A greedy
arc-factored perceptron is not how the brain parses, but it occupies the right position, it is
trained on real annotated data, and it is judged on held-out accuracy against gold. Of the twelve
subsystems this is the only one whose headline number is an accuracy on real annotations. That
should be said plainly, because most of this audit is critical.

**5. A live-path defect found in the process, verified independently.** The reading loop sets
`_PARSER_ASSET = "arc_parser_richfeat_ud_ewt.npz"` (`reading_grounding_loop.py:246`) and loads it
with `ArcParser.load(...)` -- **the base class** (`:306`), whose `parse()` scores with `_arc_ids`
only. Those weights were trained by `exp_parser_uas_ladder_richfeat_v1` using `_arc_ids_rich`,
which is the base template set **concatenated with 13 extra templates** and self-described as a
"Monotone superset of _arc_ids" (`exp_parser_uas_ladder_richfeat_v1.py:182-187`). The matching
consumer class `RichArcParser` exists **only in that experiment file** (`:204`). Grepped all of
`hdlab/`: `RichArcParser` and `_arc_ids_rich` appear **nowhere**. So the live path scores
rich-trained weights through a truncated feature function -- the 13 rich templates' learned weights
are never summed, and the base templates' weights were learned in their presence.

**The live parser is therefore neither the 0.7868-UAS base model nor the 0.7925-UAS rich model, and
its actual UAS is unmeasured.** Note the base-trained asset `arc_parser_hashed_ud_ewt.npz` is on
disk and is the one *not* loaded. Triple-check statement, per evidence discipline: right file
(`hdlab/reading_grounding_loop.py` at HEAD, not a snapshot copy), right symbol (grep over all of
`hdlab/` returns zero hits for both rich identifiers), right asset (all four assets listed;
only `richfeat` is referenced), right relation (the superset claim is the experiment's own
docstring). I confirmed each of these myself after the finding was reported to me. **Not
verified: the size of the effect** -- neither the reporting agent nor I executed the parser to
quantify the UAS delta, and a hashed-feature model given a subset of its features may degrade
gracefully or sharply. This is a real defect of unmeasured magnitude, not a demonstrated
degradation, and it should be quoted that way.

**6. Two smaller metric notes.** `arc_labeler.label_accuracy` measures labelling **given gold
heads** (`:123-141`) -- a decoupled number, not LAS, so it cannot be read as end-to-end parse
quality. And `completeness_checker` emits **hand-set constants as confidences** (0.90 complete /
0.75 imperative / 0.55 finite-no-subject, `:209-223`); they are not calibrated probabilities and
should not be consumed as such.

**7. Shared process / duplication.** `candidate_generator` deliberately over-generates
`(verb, nominal)` pairs and states that it "cannot tell subject from object; the Step-2 vote selects
among the candidates" (`:9-15`) -- **a downstream vote standing exactly where the labeler's
`nsubj`/`obj` distinction belongs**, and indeed it composes `PosTagger` + `ArcParser` and never
calls `ArcLabeler` (`:141-143`). That is a proxy substituting for a component the subsystem already
owns. Separately, S2's NP-head heuristic re-derives a job this subsystem does.

**8. Wire verdict: YES -- already wired, keep, and fix the loader.** The tagger/parser/labeler are
the right components in the right position judged on the right metric. Two housekeeping items with
fidelity consequences: the feature-function mismatch above, and the fact that **none of
`pos_tagger`, `arc_parser`, `arc_labeler` or `candidate_generator` has a registry row** -- the only
assets in the repository trained on real annotated data, and the capability gate cannot see them.

---

## S11. Infrastructure and measurement (16 modules)

**1. What it does.** Experiment scaffolding: tracing, trace storage, per-item logging, session
event logging, LM-eval baselines, GPU budgeting, attention kernels, reachability statistics.

**2. Brain system: none, correctly.** Measurement apparatus is the experimenter's, not the
organism's. `tracing.py` (the spine, imported by ~15 `hdlab` modules and by `hdlab/__init__.py`)
and `session_log.py` (246 importers, the most-imported module in the repository) are real, small
and correct. No fidelity claim is made or needed. **Severity: N/A. Wire verdict: N/A.**

Three findings worth carrying anyway.

**(a) The attention modules are real attention, and the audit should say so plainly.**
`chunked_attention`, `streaming_attention` and `gpu_generated_streaming_attention` (~980 lines
together) all compute `readout = softmax(beta * cos_sim(Q,K)) @ V` with an online log-sum-exp so
peak memory is O(chunk) -- `chunked_attention.py:60-67` states the equivalence verbatim, default
`beta=13.0` at `:76`. That is transformer-style scaled attention in its Modern/Dense-Hopfield form.
**It does not violate the no-external-LLM-at-inference invariant**, and the distinction matters:
the invariant is about the *provenance of learned weights*, and these have **no learned parameters
at all** -- keys and values are substrate memory items or seeded random bipolar vectors
(`gpu_generated_streaming_attention.py:114-120`). So: attention as a *readout primitive*, used as
the dense-Hopfield arm against the Hebbian outer-product arm in capacity benchmarks. On fidelity
that is the same verdict as `modern_hopfield_readout` in S9 -- a defensible attractor-readout
family. Consumers: `chunked_attention` has exactly one `hdlab` consumer (`cortex.py:63`, called at
`:346`) plus a verification test; the two streaming variants have **zero** `hdlab` consumers,
zero `tools` consumers and no verification test, existing only for a 2026-07 GPU benchmark wave.

**(b) `hdlab/harness.py` is a front door with zero users, and the duplication behind it is
industrial.** The module is a pure re-export shim whose own docstring says so (`:5`), created
2026-07-28 as "one canonical front door going forward". Measured: **`hdlab.harness` has zero
importers in the entire repository** -- the only two matches are inside the file itself. Meanwhile
`def get_output_dir` is independently defined in **939 files** under `experiments/` and
`def write_metrics` in **439**, and the canonical `_seed_checkpoint` implementation still lives in
`experiments/`, not `hdlab/`. The registry row `shared_harness_seed_checkpoint` records
`gate_decision: WIRED` -- which records the shim's *creation*, not any *adoption*. This is the
strongest single illustration of the parallel-build cost this audit keeps finding, and it is
mechanical rather than conceptual, so it is also the cheapest to fix.

**(c) Half of `reachability_audit.py` has never had data to run on.** Its mode (a),
`measured_reachability`, "returns all zeros (mode (a) is inert but wired)" because grounding
metadata is 100% empty (`:139-146`). Mode (b) (k-hop mass, distance-to-hub, degree-controlled
permutation nulls at `:227-249`) is genuinely well built and genuinely reused -- 16 importers,
the most-reused module in S11 after `session_log`/`tracing`. `bigram_gap_measurement.py`, built to
stop every LM cell rebuilding the bigram baseline differently, has **one** consumer.

Registry coverage of this slice is **11 of 29** modules, and the unregistered set includes
`session_log` (246 importers), `tracing` (the spine), the `director_kb` ingest engine that builds
the 10.6 GB index, and all three attention modules -- consistent with the standing
"enumerate from the filesystem, then reconcile" rule.

---

## S12. Dead / stale (1 module)

`_scratch_orig_goal_owner_select.py` (889 lines). **Confirmed a strictly-older snapshot**, zero
importers. Read-only `git diff --no-index` against `hdlab/goal_owner_select.py` (981 lines):
**106 changed lines, 99 insertions / 7 deletions**, in four hunks -- an extra import, an extracted
helper `_first_roster_name_token`, and ~84 lines of 2a path-unification machinery
(`_REPORTING_VERBS`, `_speaker_attributed_goal_holder`, `_unify_owner_via_polarity_path`) that the
scratch copy lacks. The only content unique to the scratch file is the pre-refactor inlining of a
helper whose behaviour is preserved. **Brain analogue: none. Wire verdict: NO -- delete candidate.**

One correction to the registry, which does not change its verdict: the row
`scratch_orig_goal_owner_select_stale_backup` justifies itself with "a near-full-file delta
(113 diff lines out of 121)". The measured diff is 106 changed lines against files of 889 and 981
lines, i.e. **~11%, not near-full-file**. The conclusion (dead backup, zero consumers,
delete-candidate) is right; its stated basis is not. Worth noting only because a wrong number in a
registry row is how a wrong number gets inherited.

---

## S-EXTRA. `hdlab/learner/` -- live, and in none of the twelve subsystems

The 12-subsystem partition covers the 141 top-level `hdlab/*.py`. It does **not** cover
`hdlab/learner/` (8 files) or `hdlab/dashboard/` (4 files). `hdlab.learner` and its four plugins
**are in the live runtime closure** (census S0). Recording it because an audit that only walks the
partition would miss a live component -- the same failure mode CLAUDE.md's evidence-discipline §2
was written about.

**What it is.** A centralised MDL model-selection engine over four glass-box hypothesis-class
plugins -- `estimation`, `ruleind`, `gam`, `proginduction` -- plus an explicit `KEEP_EPISODIC`
outcome (`hdlab/learner/registry.py:1-25`).

**How it reaches the live path.** Not the way the docstrings suggest. Neither
`reading_grounding_loop` nor `grounding_acquisition_loop` imports it -- the only mentions there are
comments (`grounding_acquisition_loop.py:462,470`), which is exactly the grep-vs-runtime trap. It
enters through `goal_typing` and `frame_induction`, both of which are in the closure and both of
which import it directly.

**Brain reading.** The `KEEP_EPISODIC` vs `generalize` choice is a real CLS decision -- keep the
episode or extract the regularity -- and putting it under one explicit selection criterion is
defensible. **DIVERGENT-BUT-COMPATIBLE**: MDL two-part coding is a computational-level account
(Perfors & Tenenbaum), not a mechanism, so per this repo's own Marr-level rule it should not be
counted as SHAPE fidelity. **Wire verdict: already wired, keep** -- but note the specific gap the
census found and I confirmed: the MDL gate hook in `consolidation_pass` is occupied by the
*refusal* gate, so the learner's compression gate is not what runs at the grounding decision.

---

## CROSS-CUTTING FINDING 1: duplicated processes (the brain reuses circuits; this does not)

Ranked by cost, not by count.

| # | process | implementations | evidence |
|---|---|---|---|
| D1 | **antecedent selection by recency+salience** | **>=7** | `state_of_mind.WorkingOverlay`, `coref.CorefReader`, `coref_distractor_suppress.SuppressReader`, `scene_segment.SceneProtagonistReader`, `event_centrality_coref.EventCentralityReader`, `bundle_focus_coref.BoundedEntityFocus`, `coreference_resolver`'s five `run_*`, `goal_owner_select.GeneralRecencyEntityResolver` (`:205-250`). Four form a copy-paste inheritance chain; `_centering_pick` verbatim in two files. All compute the same `count + 0.5*exp(-0.1*dt)`. |
| D2 | **experiment scaffolding** | **939 + 439** | `def get_output_dir` in 939 `experiments/` files, `def write_metrics` in 439, while `hdlab/harness.py` (the designated canonical front door) has **zero importers repo-wide**. |
| D3 | **entity-state stores** | **8** | `EntityState`, `TrackedEntity`, `BoundedEntityFocus`, `EventMemory`, `AccumulateRegister`, `MultiBankAccumulateRegister`, `SlotAttentionWM.slots`, `EntitySlotGate.slots`. |
| D4 | **hashed-bipolar text encoders** | **3 of one mechanism + 2 kernel copies** | `vwfa` subsumes `char_trigram_encoder` and most of `char_positional_encoder` as parameter settings, by its own docstring (`vwfa.py:37-43`); `_seed_for_*`/`_bipolar_hv` byte-identical across four files. |
| D5 | **lemmatisation** | **>=6** | `thematic_role_labeler.lemma_word` / `.lemma_verb`, `reading_grounding_loop.normalize_lemma`, `definitional_extraction._lemmas`, `frame_induction._lemma_candidates`, `goal_outcome_relation_grounded._lemma_candidates`. **This one already cost real damage**: `lemma_verb`, a suffix stripper, corrupted ~10% of the banked store's subject vocabulary (`billionair`). |
| D6 | **consolidation** | **3, and the faithful two are unwired** | live `consolidation_pass` (counting + split-half cosine) vs `hippocampal_encoder.cls_discrete_budget_consolidate` (replay, HARD_PASS gap 0.913 vs naive control) vs `continual` (NREM replay). |
| D7 | **novelty detection** | **2, and the faithful one is unwired** | live `gap_detector` cosine margin threshold vs `predictive_coding` residual gate. Notably `word_acquisition_loop` (S7) *does* use `predictive_coding` -- so the faithful organ is reachable from an unwired loop but not from the live one. |
| D8 | **class-centroid prototype construction** | 2 | `concept_encoder:491-523` and `composed_encoder_v3:176-190`. |
| D9 | **NP-head extraction** | 2 | `definitional_extraction`'s right-most-noun heuristic vs the live `arc_parser`/`arc_labeler`. Self-disclosed. |
| D10 | **cleanup / attractor readout** | 4+ | `cleanup_family`'s five primitives, `iterative_attractor`, `modern_hopfield_readout`, and `hd_fact_store._cleanup`'s bare argmax (`:205-211`) on the live path. |

D1 has produced a consequence worth recording on its own, because it shows what parallel builds
eventually cost. `goal_owner_select.GeneralRecencyEntityResolver`'s docstring states it was
"byte-copied from" `exp_component5_gold_role_isolated_v1.py`, that a subject-position bug was fixed
in the `hdlab/` copy in 2026-08-06, and that **the experiment's copy is deliberately left unfixed**
-- because that copy "gates the 48-item fair instrument's DIVERGENT-item population for the cert
suite", so repairing it "cannot change that population without risking a cert regression"
(`goal_owner_select.py:205-232`). A known bug is now preserved on purpose because a certification is
coupled to the population the bug produces. That is a maintenance state a single shared organ cannot
reach.

**The pattern is directional and that is what makes it a fidelity finding rather than a tidiness
complaint.** In D6, D7 and (in S7) the DG stage, the duplication is not two equal implementations --
it is a *less faithful* mechanism on the live path and a *more faithful* one, already built,
certified, and cited to primary neuroscience, sitting unwired beside it.

---

## CROSS-CUTTING FINDING 2: tests that pass while measuring the wrong quantity

The mission asks for these explicitly. Each item below **passes its test**.

| subsystem | what the test asserts | what it does not measure |
|---|---|---|
| **S3** corroboration | `independence_weighted_trace_score` self-test asserts 1 source does not cross 2.5, 2 do, 50 repeats never do (`:404-423`); FULL verdicts report "2+-source crossing=36/36" and "21/21 now retain" | whether a corroborated fact is **true**. The constants (1.5 / 0.15 / 0.2 / 2.5) were chosen to produce exactly the asserted behaviour. No gold-standard or held-out accuracy check exists in either cell. |
| **S1** grounding gate | `schema_consistency_split_half >= 0.10` -- cosine between two halves of an item's own contexts | correspondence to anything external. Already ruled a "test-retest RELIABILITY metric" by the 08-09 architecture audit. |
| **S9** primitives | recovery/capacity against random codebooks | that the stored vectors mean anything. Self-referential in the same way as S1's. |
| **S8** `concept_encoder` | headline assert reproduces **a previous run of itself** on its own generated corpus (`0.492 +/- 0.05`, `:1036`) | any capability. No real corpus appears in any S8 self-test. |
| **S10** `arc_labeler` | `label_accuracy` given **gold heads** (`:123-141`) | end-to-end parse quality (this is not LAS). |
| **S10** `completeness_checker` | emits 0.90 / 0.75 / 0.55 as "confidence" (`:209-223`) | nothing -- they are hand-set constants, not calibrated probabilities. |
| **S6** coref stack | fixture asserts like `all(h == "anna")`, `acc_on >= 0.99` on 3 targets | performance on natural discourse; and the whole stack consumes **gold mentions and gold cluster ids** (`coref.py:175-189`). |
| **S4** director KB | -- | retrieval is cosine over bags of character trigrams; the `W`/`R` relational store is loaded and never read. |

The healthy contrast, worth stating because it shows the project can do this: **S2's** metric is a
hand-scored MEANINGFUL/RELATED/NOISE judgement about *what a word means*, with a control arm, and
**S10's** is UAS against gold UD-EWT annotations. Those two are measuring the right quantity.

---

## SUMMARY TABLE

| # | subsystem | brain analogue | severity | wire verdict |
|---|---|---|---|---|
| S1 | live reading-to-grounding loop (21) | hippocampal CA1 novelty + DG/CA3 encoding + SWR-replay consolidation into an ATL semantic hub | **ARCHITECTURAL-FAULT** (meaning = cosine argmax over a bag-of-words co-occurrence profile; metric is self-consistency) | already wired, keep the skeleton; **read-out NOT-UNTIL** the candidate set opens and a structured signal supplies the object |
| S2 | definitional extraction (5) | fast declarative/relational encoding of an explicit proposition (hippocampal one-shot bind; "fast mapping") | DIVERGENT-BUT-COMPATIBLE (regex is not a mechanism, but right position, right metric) | **YES** -- the clearest wire case; 64% vs 8% control |
| S3 | multi-source lookup / three-tier (5) | GATHER = CA3 cued pattern completion; three-tier = CLS; **corroboration = nothing** | **SPLIT**: gather FAITHFUL, CLS framing DIVERGENT-BUT-COMPATIBLE (no replay), **corroboration ARCHITECTURAL-FAULT** | gather **YES**; middle tier **NOT-UNTIL** it consolidates by replay; **corroboration NO** |
| S4 | director KB (7) | **none** -- researcher's filing cabinet (its retrieval is VWFA-level orthographic form, with no hub) | DIVERGENT-BUT-COMPATIBLE as a tool; substrate-native framing unearned (W and R never read) | **NO**, by design -- keep it an agent tool |
| S5 | goal / desire organs (11) | vmPFC/OFC value + dACC discrepancy monitoring over mPFC/TPJ mentalising | **ARCHITECTURAL-FAULT** on POSITION (bottom-up extraction; base-rate default class) | **NOT-UNTIL** a graded utility/preference representation exists -- top-down conditioning alone already failed its control |
| S6 | coref / situation model (10) | hippocampal relational antecedent retrieval + PFC discourse register updated at event boundaries | **ARCHITECTURAL-FAULT** (append-only counters, no update; oracle mentions) | **NO** for all ten; `slot_attention_wm` **NOT-UNTIL** it has a training loop, a witness and the random-init control that refuted its sibling |
| S7 | word / script acquisition (6) | CLS pair (explicit source + experiential consequence); DG separation feeding CA3 completion | mixed: architecture faithful, results HARD_FAIL below scramble; `dg_pattern_separation` FAITHFUL | tool **NO** (fails its own controls); loop **NOT-UNTIL** an independent-in-kind channel; **`dg_pattern_separation` -> `script_grain_acquisition_loop` YES** |
| S8 | encoders (10) | VWFA form -> ATL semantic hub -> N400 late integration | **ARCHITECTURAL-FAULT** (nothing learned but one loader; "competitive-Hebbian" is a class centroid with an inert learning rate) | **NO** as it stands; **NOT-UNTIL** similarity structure is learned from grounded evidence |
| S9 | VSA core (44) | population coding + conjunctive binding + attractor cleanup | **MIXED**: bundling/cleanup/factorization FAITHFUL; **bind operator DIVERGENT** (P~0.15); **random equidistant atom basis ARCHITECTURAL-FAULT** | algebra already wired, keep; `hippocampal_encoder`/`predictive_coding`/`continual` **YES on fidelity**, sequenced after the S1 read-out fix; atom basis is an architecture question, not a wire |
| S10 | glass-box parser front-end (5) | left perisylvian syntactic network (LIFG/pSTS, dorsal stream) | DIVERGENT-BUT-COMPATIBLE -- **the best-founded subsystem**; real ML on real annotations | **YES** -- already wired, keep; **fix the loader** (rich weights in the base feature function) |
| S11 | infrastructure (16) | **none** (measurement apparatus) | N/A | N/A; `harness` shim has 0 users against 939/439 hand-rolled copies |
| S12 | dead (1) | none | N/A | **NO** -- delete candidate (strictly older, ~11% divergent, zero consumers) |
| S-extra | `hdlab/learner/` (8, live, unpartitioned) | CLS keep-episode-vs-generalise decision | DIVERGENT-BUT-COMPATIBLE (MDL is computational-level, not a mechanism) | already wired, keep |

**Tally.** ARCHITECTURAL-FAULT: S1, S5, S6, S8, plus S3's corroboration component and S9's atom
basis. FAITHFUL or DIVERGENT-BUT-COMPATIBLE: S2, S3's gather, S9's bundling/cleanup/factorization,
S10, S-extra. No brain analogue by design: S4, S11, S12.

**The single sentence this audit reduces to:** the substrate's fidelity problem is not that faithful
mechanisms were never built -- `hippocampal_encoder`, `predictive_coding`, `continual`,
`dg_pattern_separation`, `cls_discrete_budget_consolidate` are built, certified, and cited to
primary neuroscience -- **it is that on the live path a counter or a cosine stands in each of their
places.**

---

## WHAT I COULD NOT VERIFY

1. **No experiment was re-run.** Two detached runs are live (`exp_wire_definitional_v1`,
   `exp_anchor_pool_expansion_v1`) and were not touched. Every experimental number here is read
   from a `metrics.json` on disk or from a persisted hand-score note; no per-arm recomputation was
   done. In particular I did **not** re-run
   `exp_state_of_mind_relevance_gather_reasoning_union_v1` to test the narrow-vs-wide confound I
   identify in S3(a) -- that confound is established by reading the cell's arm construction
   (`:471`, `:493`, `:496`), not by measuring its effect. **The size of the confound is unknown.**
   It could be most of the 0.3388 delta or a small part of it. The missing arm is cheap
   (cued gather over `hop2_blind`) and would settle it.
2. **The hand-scores are single-judge.** The 64% definitional and 8% distributional figures are one
   scorer, not blind. Only the structured-comparator scores (2% / 0%) were blind. Inter-rater
   reliability is unmeasured anywhere in this arc.
3. **I did not verify that `reading_grounding_v1` and `reading_grounding_v2_qualityfix` read the
   same corpus**, so the 3,544 -> 634 drop in GROUNDED_MEANING yield after the tautology fix is
   *not* a clean quality/yield trade-off measurement and should not be quoted as one.
4. **Brain-side claims are literature-grounded, not re-derived.** Where I assert what the brain
   does, I am relying on the citations in this repo's own prior notes plus standard references.
   I fetched no papers this pass. Every such claim is therefore at the confidence the prior
   corpus assigned it -- and where that corpus assigns an explicit deflated probability
   (e.g. `P ~0.15` that a convolution-family operator is the faithful binding shape), I have
   carried the number rather than rounding it to a verdict.
5. **Whether wiring any unwired subsystem would help the live path is untested by anything.** No
   cell imports both the reading loop and the three-tier loop. My wire verdicts are fidelity
   judgements, as the brief requires; they are not predictions of a score change, and the one
   recent attempt to improve the read-out returned a floor-limited NULL.
6. **`concept_encoder` and `reasoner` self-tests remain unresolved** (both TIMEOUT at 180s per the
   census). I did not run them. Any claim about `concept_encoder`'s training rule rests on reading
   its code, not on observing it run.
7. **A stale claim is still propagating and I did not repair it** (read-only brief). Gap **G5** of
   `director_three_tier_knowledge_architecture_design_audit_2026-08-11.md` ("the MDL conjunctive
   gate was never invoked, `mdl_gate_fn=None` at both call sites") was superseded by
   `system_accounting_2026-08-13.md`, but `multisource_lookup_wiring_audit_2026-08-13.md:284`
   still repeats it in the stale form. None of the three notes CLAUDE.md lists as superseded
   carries a superseded-by line. Flagging rather than editing, since this brief is read-only.
8. **The census partition was taken as given.** I did not re-derive the 141-module assignment or
   the 35-module live closure; both come from `system_accounting_2026-08-13.md`, measured the same
   day by runtime `sys.modules` trace. I did spot-confirm the specific live-path memberships my
   arguments lean on (`hd_fact_store`, `event_bundle`, `situation_model_accumulate`, `gap_detector`).
9. **Division of labour, stated so the evidence chain is auditable.** I read S1, S2, S3, S7, S9 and
   `hdlab/learner` personally. S4/S11/S12 and S6/S8/S10 came from delegated code-reads whose
   file:line citations I spot-checked rather than fully re-derived; I re-verified in person every
   claim this note leans on hardest -- the live parser feature-function mismatch (S10), the
   `hd_fact_store._cleanup` argmax, the two-algebra split, `cls_discrete_budget_consolidate`'s
   consumers, and the `GeneralRecencyEntityResolver` byte-copy. The S5 investigation's first agent
   **died mid-run on an API error**; a second was dispatched, and rather than wait on it I read
   `goal_achievement`'s channel cascade, the failing pin, and the scaffold-table counts myself.
   S5's numbers are therefore mine plus the prior corpus, not a fresh independent code sweep -- the
   thinnest section in this note.
10. **The S10 defect's magnitude is unmeasured.** That the live path feeds rich-trained weights to a
   base feature function is established by reading. What it costs in UAS is not, and a hashed model
   given a feature subset could degrade gracefully or sharply.
11. **One measurement error of my own, recorded because the process matters.** My first tautology
   count returned 0.0% -- I had queried the field `object` where the store uses `obj`, so no row
   ever matched. I nearly reported "the 65.7% figure does not reproduce". The census figure is
   correct; my instrument was wrong. Stated here as the concrete instance of why a negative about
   someone else's landed result gets the same scrutiny as a positive of one's own.
