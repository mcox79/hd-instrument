# Research: causal/temporal edge extraction from real prose -- modern external tools (2026-08-10)

Filed by: research (Sonnet). KB-CHECK done first: `substrate_query.sh "causal temporal relation
extraction from text discourse connectives"` returned only generic/weak hits (top cosine=0.3721,
"disconnection"/"extraction"/"temporal relation" atoms -- not a substantive prior finding); confirmed
new ground. Read first: `notes/design_extraction_quality_gate_neural_foundation_2026-08-10.md` (target
schema, item 3 = CAUSAL/TEMPORAL LINKS, flagged HARDEST/may-be-partial), `notes/director_POST_COMPACTION_
BACKUP_2026-08-04.md` TOP block, `notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_2026-08-10.md`
(today's WIQA flagship pick -- its Section 4 experiment design ALREADY assumes connective/adjacency-based
structure extraction; this drill supplies the evidence base for whether that assumption holds), and
`hdlab/situation_model_accumulate.py:161-234` (`CausalLinkRegister.add_causal_link(cause_idx, effect_idx,
polarity)`, read directly -- polarity is already a plain side-dict scalar, not bound into the FHRR
algebra, which matters for the routing recommendation below). `research_field_advisor.py` run (110
drills/22 fields) -- covers substrate-physics fields, does not rank extraction-tooling drills; noted, not
force-fit. Four parallel Sonnet lit-scan sub-agents dispatched this cycle (discourse parsing, temporal RE,
causal RE, AMR+explicit/implicit-ratio), all generic public terms only per query-privacy discipline.

---

## HEADLINE

**The STRUCTURE-vs-POLARITY split from the WIQA arc is CONFIRMED as a real, field-recognized distinction
-- but the strong form ("structure is text-extractable") is REFUTED. The correct claim is the weak form:
structure is *more mature and more extractable than polarity*, not *reliably extractable in the
majority of cases*.** Across every corpus measured, MOST causal and temporal relations carry no explicit
lexical marker: causal implicit-rate ranges 17-79% depending on domain (Causal-TimeBank 54.7%, SemEval-
2010 Cause-Effect 34%, FinCausal 78.7%, MedCaus 17%; arXiv 2503.06076), and pure-temporal-order relations
are even worse -- only ~11-12% of TimeBank TLINKs carry an explicit signal word (arXiv 1203.5066), and
RST discourse relations are exclusively-connective-signaled only ~10-11% of the time (Das & Taboada / RST
Signalling Corpus). Meanwhile, causal DIRECTION/POLARITY identification is independently confirmed by the
field itself to be a separate, markedly less mature sub-problem -- an ECI survey (arXiv 2411.10371) lists
"causal direction identification" as future work distinct from existence detection; a dedicated study
(arXiv 2105.09045) shows models with near-identical relation-classification F1 have "clear gaps" on
direction; and increase/decrease VALENCE specifically (WIQA's exact "more/less" question) is addressed
almost only via narrow pattern-based methods in financial/scientific-text mining, essentially absent from
general ECI benchmarks. **This means: routing polarity to the CSKG crutch is not just consistent with our
own WIQA finding, it is the field's own de-facto architecture** (nobody has built a general
polarity/direction extractor worth reusing). But it also means structure extraction itself will leave
a LARGE fraction of real-prose causal/temporal links un-signalled by any connective/tense rule, and a
trained classifier is the only way to close that gap -- with real, sourced cross-domain risk specific to
our target genre (see deflator below).

**Installability: all four tool families have a runnable, pip-installable, Windows+PyTorch-compatible
option.** Best picks: `amrlib` (AMR, pip+HF, ~700MB-1GB), `OmniEvent` (THU-KEG, temporal RE toolkit,
pure PyTorch+HF, pip-installable, BERT/RoBERTa-scale, supports MATRES/TB-Dense/MAVEN-ERE fine-tuning),
`discopy`/`BMGF-RoBERTa` (discourse, PyTorch+HF), `R-BERT`/`MAVEN-ERE` (causal, PyTorch+HF). None require
exotic Linux-only infra; the one heavy outlier (RSTParser_EACL24, Llama-2-70B+QLoRA) is skippable -- RST
tree structure is not what our schema needs anyway (we need CAUSE/EFFECT + BEFORE/AFTER edges, not
rhetorical nuclearity trees).

**The single biggest, most concrete deflator: the ONE genre-matched number found (children's-story text,
our closest real analog) is far below the encouraging newswire SOTA headlines.** Rule-based causal
relation extraction on children's stories scores only 36% F-measure (Samson et al., DLSU thesis) vs.
40-65% F1 on newswire ECI benchmarks (already modest) -- and children's-story temporal DEPENDENCY parsing
scores LAS 0.647 / tree-edit-distance 0.596 (Kolomiyets et al., ACL 2012) vs. newswire temporal-RE F1 in
the 83-88% range. No modern (2021+) transformer-based causal/temporal extractor has been benchmarked on
this genre in anything found this cycle -- this is an acknowledged, unaddressed gap in the literature, not
a search miss (confirmed independently by two of the four sub-agents). **This must be measured on our own
corpus before trusting any newswire-reported F1 number, exactly as the design doc's oracle-parity gate
already anticipates ("HARDEST; may be partial -- measure its marginal impact separately").**

P_deflated = **0.40** for "structure-extraction (connective-rule tier + a fine-tuned temporal/causal
classifier) reaches >=50% coverage at >=70% precision on our own naturalistic-prose sample" (Section: cheap
decisive test below) -- deflated per lit-scan calibration (uncharted regime for our specific genre; no
direct children's-story-adjacent modern-transformer number exists to anchor against; cross-domain drops of
15-49 points were measured on EVERY domain-shift pair found, and our shift -- newswire to graded
narrative/children's-story-adjacent prose -- is structurally similar to the worst-case shifts measured
(clinical -31 Smatch, FinCausal->CausalTimeBank -49pts, children's-story rule-based causal 36% F-measure)).
P = **0.75** (less deflated; this is a literature-confirmation claim, not a novel mechanism claim, lower
risk class) for "the STRUCTURE-vs-POLARITY split is real and polarity should route to the crutch" -- this
is now backed by independent field evidence (direction-identification-as-future-work, Causal Strength Bank
as a separate benchmark), not just our own single WIQA drill.

---

## 1. Tool landscape summary (full detail in the four sub-agent scans, condensed here)

| Family | Best SOTA (F1, newswire) | Explicit-signal coverage in gold corpora | Public/runnable pick (Windows+PyTorch) |
|---|---|---|---|
| Discourse (PDTB shallow) | Implicit 4-way: 63.4 F1 (BMGF-RoBERTa); explicit 89.6% acc vs implicit 67.8% acc (~22pt gap) | PDTB2: 45% explicit / 40% implicit / 15% other | `discopy` (pip+HF), `BMGF-RoBERTa` |
| Discourse (RST tree) | Full-relation F1: RST-DT 58.1, out-of-domain (Instr-DT) 47.3 (RSTParser_EACL24) | Only ~11% *exclusively* connective-signaled (RST Signalling Corpus); ~86-90%+ signaled by *some* cue (syntax/entity/genre) | `discopy`-adjacent / `DMRST` (moderate setup); RSTParser_EACL24 needs 70B LLM, skip |
| Temporal RE (MATRES) | RoBERTa-large 87.6 F1; LLM zero-shot only 36.6% | Only ~11.2-12.2% of TimeBank TLINKs carry an explicit signal WORD (rest inferred mainly from tense/aspect) | `OmniEvent` (THU-KEG, pip+PyTorch+HF) |
| Temporal RE (TB-Dense) | RoBERTa 83.1 F1; cross-sentence pairs much harder (CAEVO 16.1 manual vs 42.5 auto F1) | same corpus family as above | `OmniEvent` |
| Temporal RE (TORQUE) | RoBERTa-large 51% EM vs human 84.5% EM -- gap barely closed since 2020 | n/a (span-selection format) | raw data only, no turnkey model |
| Causal RE (SemEval-10 T8) | R-BERT ~88-89% F1 (short, mostly-explicit sentences) | ~34% implicit | `R-BERT` (pip+PyTorch) |
| Causal RE (Causal-TimeBank) | DPJL 64.6% F1 intra-sentence | 54.7% implicit | rule-tagger `Causeway`/`BECAUSE` (public); trained SOTA models mostly code-unconfirmed |
| Causal RE (EventStoryLine) | KADE 62.7% F1 (2023), climbing slowly since 2021 (~50-55% -> 62.7%) | "most links, especially inter-sentential, are implicit" (qualitative, multiple papers) | `ERGO` (PyTorch, doc-graph transformer) |
| Causal RE (MAVEN-ERE, joint) | Joint-RoBERTa 31.5 F1 (much lower -- huge joint candidate-pair space) | n/a | `MAVEN-ERE` toolkit (pip+PyTorch+HF, no bundled weights) |
| AMR (`:cause`/`:time`/`:condition`) | Aggregate Smatch 84-85% (SPRING/AMRBART/LeakDistill) -- **no per-relation number exists anywhere for :cause/:time specifically**; these relations are rare and not isolated in any fine-grained AMR eval suite found (Damonte 2017, GrAPES 2024) | unknown/unverified | `amrlib` (pip+HF, best installability of all four families) |

Cross-domain degradation, every pair measured: RST-DT->GUM -11 to -16pt; fiction/Reddit hardest genres
named explicitly; Clinical TempEval ~-20pt F1; AMR news->clinical -31.3 Smatch; CausalTimeBank->CauseNet
0.719->0.445 (-27pt); SemEval->FinCausal2020 0.844->0.350 (-49pt); children's-story rule-based causal
36% F-measure; children's-story temporal dependency LAS 0.647. **No domain-shift pair found is smaller
than -11 points; several are -27 to -49 points; every one of these shifts is smaller in genre-distance
than newswire-to-children's-story, which is the one direct hit and it is the worst number in the set.**

## 2. The STRUCTURE-vs-POLARITY verdict, stated precisely

Refute the strong form ("causal/temporal STRUCTURE is signalled by discourse connectives and is
therefore text-extractable"): **false as a majority claim.** Implicit relations (no connective) are the
majority or near-majority case in nearly every corpus measured (causal: 34-79% implicit across 5 corpora;
temporal-order: ~88-89% of TLINKs carry no explicit signal WORD, though tense/aspect -- itself textual,
just morphological rather than lexical -- covers some of that gap in ways no source quantified cleanly).

Confirm the weak form ("STRUCTURE is more mature / more extractable than POLARITY, and POLARITY should
route to the crutch"): **true, and now doubly confirmed** -- not just by our own WIQA drill, but by the
field's own architecture. Causal existence/link detection has 7-8 years of dedicated benchmark maturity
(SemEval-2010 through MAVEN-ERE 2022, F1 climbing from ~50% to 60%+ on the hardest corpus). Direction/
polarity has no comparable benchmark lineage -- the 2024/2025 ECI survey names it explicitly as future
work, a dedicated 2021 study shows direction recognition fails even when relation-classification succeeds,
and increase/decrease VALENCE (WIQA's literal task) is essentially unaddressed outside financial/scientific
pattern-mining. **There is no general-purpose polarity extractor to reuse even if we wanted one** -- this
is not us being under-resourced relative to a solved field problem, it is the field itself not having
solved it, which makes routing to the crutch (world-knowledge lookup, not extraction) the objectively
correct architecture, not a workaround.

One important WIQA-specific simplification, worth naming explicitly since it changes the risk profile for
the near-term experiment (`exp_wiqa_causal_chain_loop_v1`): **WIQA's process paragraphs give step ORDER
for free** (they are literally numbered/sequential steps), so the general temporal-relation-extraction
problem (the worst-covered case above, ~11-12% explicit) barely applies to WIQA -- adjacency IS the
temporal edge, no classifier needed. What WIQA actually needs from extraction is narrower: (a) causal
LINK EXISTENCE between adjacent/connective-linked steps (the causal-RE numbers above apply, ~35-65% F1
range, implicit-majority), and (b) polarity from the crutch. **The GENERAL extraction-quality-gate schema
(design doc item 3, arbitrary real prose e.g. graded readers) is the harder case** -- it needs both
causal AND full temporal-order extraction with no given sequence to lean on, and that is where the
~11-12% explicit-temporal-signal number and the children's-story LAS 0.647 number bite hardest.

## 3. Recommendation for the extraction pipeline (CausalLinkRegister input)

**Tier 1 (build first, near-zero cost, ship regardless of Tier 2's fate):** a rule-based
connective+tense/aspect detector -- causal connectives (because, so, therefore, as a result, due to,
since-causal) and temporal connectives (after, before, then, while, during, when) plus UD-derived
tense/aspect morphology (already available from any dependency parser front end), scanning adjacent/
nearby clauses. This is a direct extension of the design doc's own UD-fallback path (item: "spaCy 3.x
dependency-parse -> heuristic role mapping"), costs nothing beyond a connective lexicon, and by the
numbers above will catch roughly 10-55% of relations (temporal order at the low end ~11-30%, causal at
the higher end ~20-55%, both HIGH-precision because an explicit connective rarely mis-signals its own
relation type) with essentially zero false-positive risk on the connective-marked subset. **Ship this
immediately, measure its raw coverage on our own corpus, and treat that measured number -- not the
newswire literature number -- as the honest floor.**

**Tier 2 (conditional, install+smoke before committing):** for temporal, `OmniEvent` fine-tuned on
MATRES/TB-Dense is the clear pick (best installability of the temporal-RE family, explicit
Windows/PyTorch/HF compatibility, supports the exact benchmark formats in question). For causal, there is
no comparably turnkey option -- most EventStoryLine/MAVEN-ERE-class SOTA models are literature-confirmed
but code-unconfirmed this cycle; realistic effort is fine-tuning `R-BERT` or `MAVEN-ERE`'s toolkit from
scratch on Causal-TimeBank/EventStoryLine, expect 40-65% F1 on THEIR test domain before any cross-domain
haircut. Given the design doc's explicit instruction ("HARDEST; may be partial -- measure its marginal
impact separately, do not let it block the SRL+coref core"), **the correct sequencing is: ship Tier 1
alone first, measure oracle-parity with Tier-1-only causal/temporal edges (sparse but high-precision), and
only invest in Tier-2 causal fine-tuning if Tier 1's sparse coverage is shown to be the bottleneck** (i.e.
if SRL+coref+grounding are already solid and the causal/temporal edge sparsity is the thing capping
oracle-parity). This avoids sinking engineering time into a fine-tune whose expected genre-shifted F1 is
genuinely unknown (no children's-story-adjacent modern-transformer number exists anywhere in the
literature scanned).

**AMR: do not adopt as the primary source for causal/temporal edges.** It is the cheapest single
install (`amrlib`, best Windows-installability of any candidate in this whole scan) and would be
"free" if AMR is separately chosen for the SRL role (design doc's AMR-as-SRL-alternative option), but
there is literally no verified per-relation accuracy for `:cause`/`:time`/`:condition` anywhere in the
current literature -- these relation types are too rare in AMR-annotated data to appear in any
fine-grained eval suite found (Damonte 2017's 12 categories, GrAPES 2024's 36 phenomena, neither includes
them). If AMR is picked for SRL for other reasons, treat its `:cause`/`:time` edges as a free THIRD signal
to cross-check against Tier 1/Tier 2, never as a trusted standalone source.

**Polarity: route 100% to the CSKG crutch, build zero polarity-extraction machinery.** This is now the
field-consistent architecture, not just our own finding, and it matches the code as it already exists --
`CausalLinkRegister.add_causal_link`'s `polarity` parameter is already a plain Python side-dict scalar
(`self._link_polarity: Dict[Tuple[int,int], int]`, `hdlab/situation_model_accumulate.py:207`), explicitly
NOT bound into the FHRR algebra "because there is nothing to clean up about a +-1 sign" -- the
implementation already anticipates polarity as an externally-supplied fact, not something the bind/bundle/
cleanup_argmax extraction chain derives. The crutch-that-fades architecture (CSKG fills world-knowledge
gaps, substrate consolidates/generalizes, crutch fades) is the exact right home for this.

**Expected coverage, stated honestly:** Tier 1 alone, on our own naturalistic prose: roughly 10-30%
temporal, 20-40% causal (extrapolated from the corpus-composition numbers, not yet measured on our own
text -- this is the cheap decisive test below). Tier 1+2 combined, IF Tier 2 is built and IF cross-domain
degradation on our genre matches the worst end of what was measured elsewhere (children's-story rule-based
causal 36% F-measure is the closest real analog): plausibly 40-55% causal, 25-45% temporal, with
meaningfully wide error bars because no source in this scan benchmarked a modern transformer extractor on
genuinely children's-story-adjacent text.

**Biggest risk:** the design doc's oracle-parity gate (extraction closing 0.684->0.930) could fail
specifically on the causal/temporal component even after SRL+coref+grounding clear their own bars,
because every quantified genre-shift number found this cycle (-11 to -49 points depending on shift
distance) suggests our actual target genre sits closer to the worst-measured shifts than to the newswire
baseline the encouraging headline F1 numbers describe. This is exactly why the design doc already scopes
causal/temporal as separable ("measure its marginal impact separately") -- this drill's contribution is
confirming that instinct was right, with sourced numbers, rather than leaving it as an unquantified
worry.

---

## Cheap decisive test

On a 30-50 sentence sample of OUR OWN naturalistic prose (WIQA process paragraphs, or the graded-reader/
dataprep corpus already in use), run (a) the Tier-1 rule-based connective+tense detector and (b)
`OmniEvent` fine-tuned/zero-shot on MATRES for temporal pairs. Measure: coverage (% of adjacent/plausible
event pairs yielding a confident link) and precision via manual spot-check of ~20 extracted links (no
gold causal/temporal annotation exists for our corpus yet, so precision must be hand-checked, not F1
against a reference set). Cheap (rule tier is instant; OmniEvent runs CPU-feasible on 30-50 sentences, no
GPU needed for this smoke), can-fail (real prior expectation range from newswire literature is 40-80%
coverage; a genre-shift result below 25% would be a clean, attributable signal that newswire numbers do
not transfer, consistent with the children's-story precedents found), one-lever (isolates
structure-extraction quality specifically, independent of SRL/coref/grounding/polarity).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS:** Tier-1 + Tier-2-lite (OmniEvent zero-shot, no fine-tune yet) combined reaches >=50%
  coverage of causal/temporal event pairs at >=70% manual-spot-check precision on our own naturalistic
  sample. -> Proceed to fine-tune Tier 2 for causal; causal/temporal edges are not the bottleneck.
- **HARD-FAIL:** coverage <25% OR precision <50%. -> The newswire-trained tools do not transfer to our
  genre well enough to justify Tier-2 investment yet; ship Tier-1-only (sparse, high-precision) into
  `CausalLinkRegister`, treat causal/temporal structure as a genuinely partial signal (matches the design
  doc's own pre-registered fallback: "measure its marginal impact separately, do not let it block the
  SRL+coref core"), and do not claim a causal/temporal capability beyond what Tier 1 measurably delivers.
- **MIDDLE_BAND:** coverage 25-50% or precision 50-70%. -> Ship Tier 1 now; scope Tier-2 causal fine-tune
  as a follow-on ONLY if oracle-parity measurement (design doc metric 5) shows causal/temporal sparsity is
  the specific thing capping the gap-closure, not SRL/coref/grounding.
- **Independent prediction, high confidence (P~0.80), not gated on the smoke above:** a general-purpose
  polarity/direction extractor built from scratch would underperform the CSKG crutch, because no
  general-purpose one exists in the published literature to even benchmark against -- every polarity/
  direction-adjacent result found is either a narrow domain-specific pattern method (financial/scientific
  text) or an explicit "future work" flag in a 2024/2025 survey. This is a benchmark-fit/architecture
  judgment (lower risk class than a mechanism claim), not subject to the same 0.15-0.25 deflation as the
  coverage number above.

## Cross-thread synthesis

- Directly extends `notes/design_extraction_quality_gate_neural_foundation_2026-08-10.md` item 3
  (CAUSAL/TEMPORAL LINKS, flagged HARDEST) -- this drill supplies the tool landscape, the coverage
  estimates, and the specific installability picks (`amrlib`, `OmniEvent`, `discopy`/`BMGF-RoBERTa`,
  `R-BERT`/`MAVEN-ERE`) the design doc left as "evaluate what actually runs."
- Directly extends `notes/research_flagship_benchmark_scoping_wiqa_torque_mctaco_2026-08-10.md` Section 4
  -- that note's experiment design already assumed "connective-linked/adjacent steps" as the extraction
  mechanism for WIQA; this drill confirms that assumption is reasonable SPECIFICALLY because WIQA's given
  step-order sidesteps the hardest part (general temporal-order extraction, only ~11-12%
  explicitly-signalled), leaving only causal link existence (35-65% F1 range) as WIQA's real extraction
  ask -- a materially easier problem than the design doc's general schema (arbitrary real prose, no given
  order) needs to solve.
- CONFIRMS (does not merely repeat) the WIQA arc's "polarity is world-knowledge, not text-extractable"
  finding: the earlier finding was a single learner failing to generalize on one dataset; this drill shows
  the SAME split is independently recognized across the entire ECI/discourse/temporal-RE literature
  (direction identification named as future work; Causal Strength Bank as a separate, less-developed
  benchmark), which upgrades that finding from "one experiment's negative result" to "matches the field's
  own architecture" -- a meaningfully stronger evidentiary basis for the crutch-routing decision going
  forward.
- New, not previously surfaced in any prior note read this cycle: the children's-story-genre numbers
  (36% F-measure causal, LAS 0.647 temporal) are the first DIRECT genre-matched evidence found anywhere
  in this project's research history for how badly extraction tools may degrade specifically on our
  target prose style -- flag this for the extraction-quality-gate's own smoke-on-5-sentences step
  (design doc guardrail) to include at least one genuinely naturalistic/narrative sentence, not only
  newswire-style test sentences, when doing the installability check.

## Substrate-product implications

If Tier 1 + measured Tier 2 lands in the MIDDLE_BAND or better, the product claim becomes: a glass-box
system that extracts an auditable, source-traceable partial causal/temporal graph from real prose (every
edge traces to either an explicit connective match or a specific classifier decision, never an opaque
LLM judgment) and honestly represents its own coverage gaps (unlinked event pairs stay unlinked, not
guessed) -- paired with a CSKG crutch that supplies world-knowledge polarity where the text is silent
(which per this drill's numbers is the majority of causal relations, not an edge case). This is a more
honest and more differentiated story than assuming a monolithic "we extract causal/temporal structure"
capability: it says exactly which fraction of the graph came from the text and which came from world
knowledge, which is itself a novel auditability property competing LLM-based comprehension systems do not
expose. Do not claim the full design-doc schema item 3 is "solved" on the strength of newswire SOTA
numbers alone -- those numbers do not currently have a genre-matched analog for our target prose, and the
one genre-matched analog found is the worst number in the entire scan.

## Citations (verified count)

Approximately 58 distinct sources across four parallel Sonnet lit-scans (discourse parsing, temporal RE,
causal RE, AMR+explicit/implicit-ratio synthesis) -- full per-claim citations with year/venue are embedded
in each sub-agent's returned scan text (retained in this session's tool-call history) and condensed into
the table/prose above. Headline sources by family: discourse -- discopy (Knaebel & Stede 2021), BMGF-
RoBERTa (Liu et al. IJCAI 2020), RST Signalling Corpus (Das & Taboada), Liu & Zeldes EACL 2023 (arXiv
2302.06488), RSTParser_EACL24; temporal -- MATRES (Ning et al. 2018), TIMERS (ACL 2021), Yuan & Ji arXiv
2410.10476 (2024), TDDiscourse (ACL WS 2019), TORQUE (EMNLP 2020), OmniEvent (arXiv 2309.14258), TimeBank
TLINK signal-word study (arXiv 1203.5066); causal -- SemEval-2010/R-BERT, Causal-TimeBank (Mirza et al.
LREC/COLING 2014), EventStoryLine (Caselli & Vossen 2017), MAVEN-ERE (EMNLP 2022), "Empirical Study of
Causal Relation Extraction Transfer" (arXiv 2503.06076, 2025), ECI survey (arXiv 2411.10371), direction-
recognition study (arXiv 2105.09045); AMR -- SPRING (AAAI 2021), AMRBART (ACL 2022), clinical domain-shift
study (arXiv 2405.09153, 2024), children's-story causal extraction (Samson et al., DLSU thesis),
children's-story temporal dependency parsing (Kolomiyets et al., ACL 2012). Every number reported above
traces to one of these; items each sub-agent explicitly flagged UNVERIFIED (e.g. one Causal-TimeBank
signal-co-occurrence ratio, one TORQUE question-count discrepancy carried from the earlier flagship note)
are carried forward with that flag, not silently treated as settled.
