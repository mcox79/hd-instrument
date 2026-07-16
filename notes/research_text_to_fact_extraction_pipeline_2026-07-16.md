# Research: the text-to-structured-claim pipeline for the foundation-BUILD (how the substrate would "read a book")

Director drill, 2026-07-16. Design/scoping drill, no code, no cell. Three parallel Sonnet lit-scans (extraction
toolchain maturity; fact-operationalization sub-problems; diagram/chart extraction + single-exposure trust-weighted
learning) + director synthesis on the extraction-to-gate handoff and the single-pass/trust-gated design. Generic
NLP/linguistics/psychology terms only in all external queries — no substrate-novel mechanism names, configs, or
numbers went off-platform.

Framing per the PIVOT: extraction is BUILD-TIME (any external tool — LLM/IE/curation — is fair game; it is not the
substrate's novel contribution). The substrate's novel contribution is the glass-box GATE that decides what a
candidate claim becomes (provisional-hold / committed), which is downstream of extraction. This note scopes the
extraction step and draws the extraction/gate line honestly.

## HEADLINE

**Text-to-triple extraction for textbook prose is MOSTLY-MATURE-WITH-KNOWN-GAPS, not a solved black box** — classical
OpenIE (F1 ~0.41-0.49 on clean Wikipedia/news benchmarks) degrades further on scientific/textbook prose (Groth et al.
2018, directly measured), and even 2025-2026 LLM-based extractors still lose to specialized parsers on complex
multi-relation sentences (a 2026 paper found LLMs *underperform* graph-based parsers on this exact case). The
genuinely open sub-problem is NOT extraction mechanics but **"what counts as a fact"** — specifically **filtering
worked-examples/exercises/rhetorical-scaffolding out of the assertion stream**, which has *no dedicated benchmark* in
the literature (ad hoc heuristics only), unlike definitions (DEFT/WCL, fairly mature) and hedge detection (CoNLL-2010,
mature in-domain but brittle: F1 85% biomedical -> 55% Wikipedia, a domain-transfer warning that applies directly to
us since textbook domains will vary as widely). Diagram/chart extraction bifurcates sharply: simple templated
pedagogical diagrams (AI2D-style, textbook-typical) are near-solved (>94%), but realistic scientific charts are not
(CharXiv: GPT-4o 47.1% vs human 80.5%, a measured 33-point gap, brittle to trivial perturbation) — textbook diagrams
sit closer to the solved end but advanced-textbook data plots will hit the harder regime. The extraction/gate line is
legitimate (extraction = perception, gate = the substrate's own transparent reasoning over the resulting proposal) IF
extractor confidence is passed through as a gate input and provenance is logged for audit — the risk to watch is
**correlated LLM-hallucination masquerading as independent corroboration**. Frontier-2 (single-pass exact write) is a
defensible LIMIT case of the well-established continuous Bayesian-source-reliability literature (near-certain source
-> near-complete update from one report), not a free lunch or an unprecedented design — but no paper licenses
skipping the schema-fit/surprise legs of the gate even for trusted sources, because those two legs catch EXTRACTION
error, which is orthogonal to source trustworthiness.

## Cheap decisive test

Pull ~100 sentences stratified across assertion types (fact / definition / hedge / worked-example / exercise /
rhetorical-scaffold) from a single real textbook source already surfaced in the curriculum-dataset survey
(`notes/research_curriculum_prerequisite_datasets_2026-07-16.md` — TQA, real middle-school science textbook prose,
zero access friction). Run two off-the-shelf steps, no substrate involvement yet:

1. An LLM-based triple extractor (any general-purpose LLM, zero/few-shot prompted for open triples + qualifiers) on
   all 100 sentences, self-scored against hand-read ground truth for **triple precision** (does the S-P-O + qualifier
   set correctly paraphrase a true claim actually stated in the sentence).
2. A lightweight assertion-type classifier: hedge-cue lexicon (per CoNLL-2010 cue categories) + position/syntax
   heuristics (imperative mood, "Example:"/"Exercise" markers, interrogative form) + LLM fallback for the residual —
   scored for **recall on the reject class** (definitions/hedges/examples/exercises correctly kept OUT of the
   direct-fact stream).

This is a pure measurement task (no gate, no cell, no substrate compute) — a half-day exercise, doable inline.

### Falsifiable predictions

**HARD-PASS** (extraction pipeline is fit to proceed to gate-integration as designed):
- Triple extraction precision >= 70% on the hand-graded textbook sample (consistent with literature-implied
  textbook-domain penalty of ~10-20 F1 points off the ~85-90% ceiling seen on cleaner RE benchmarks).
- Assertion-type classifier recall on the reject class >= 80% (catches most non-factual sentences before they reach
  the gate as if they were literal claims).

**HARD-FAIL** (extraction/filtering needs a redesign before any gate-integration cell is authored):
- Triple extraction precision < 50% (near-chance garbling; unusable without heavy human correction, contradicts the
  "mature build-time tech" framing this drill set out to confirm).
- Reject-class recall < 60% (>40% of non-factual sentences — worked examples, exercises, hedges — would enter the
  gate's corroboration/schema-fit pipeline as literal claims, poisoning the very frequency/corroboration signal the
  gate depends on, per the correlated-hallucination risk below).

MIDDLE band (50-70% precision, 60-80% reject-recall): usable with a stricter confidence-threshold cutoff on the
extractor's own reported confidence score (drop low-confidence extractions rather than redesign the pipeline).

## Deliverable: the text-to-fact reading pipeline

### 1. Extraction toolchain (text -> candidate triples)

| Approach | Reported quality | Best for | Textbook-prose caveat |
|---|---|---|---|
| Classical OpenIE (Stanford OpenIE, ReVerb, ClausIE, OLLIE, OpenIE6/MinIE) | F1 ~0.41-0.49 on CaRB (Wikipedia/news) | cheap, high-throughput candidate generation | Groth et al. 2018 directly measured degradation on scientific text; tools were tuned on newswire/encyclopedic domain, textbook prose is out-of-distribution |
| Closed-schema neural RE (SpERT, REBEL, TACRED-style) | ~70-90% F1 within a fixed relation schema | precision on a KNOWN relation inventory | zero recall on anything outside the pre-defined schema — wrong tool for open-domain textbook facts |
| LLM-based triple/structured extraction (GPT-4-class, zero/few-shot) | narrowing gap to supervised RE on some benchmarks; a 2026 paper found LLMs still **underperform** graph-based parsers on complex multi-relation sentences; AutoSchemaKG (2025) demonstrates dynamic schema induction at web scale | schema-free, coreference-aware, can recover implicit arguments via commonsense | best available for textbook prose but not a solved problem — dense multi-clause technical sentences are exactly where the 2026 counter-finding bites |

**Verdict: MOSTLY-MATURE-WITH-KNOWN-GAPS, trending FRONTIER for textbook prose specifically.** This is well-established
build-time engineering in the sense that off-the-shelf tools exist and are usable today (confirming the PIVOT framing
that extraction may use any external tool) — but it is not a solved black box for our specific input domain. Expected
quality: roughly a 10-20 F1-point degradation analog vs the clean-domain ceiling (Wikipedia/news), extrapolated (not a
precisely transported number) from the Groth et al. scientific-text gap. Practical design: use classical OpenIE as a
cheap high-recall candidate generator + an LLM pass as arbiter/normalizer/qualifier-extractor over the OpenIE
candidates (cheaper than running the LLM extractor over the raw corpus at full scale, and gives two independent
extraction signals that can itself function as a corroboration feature — see the hallucination-correlation caveat
below).

### 2. What constitutes a fact (the genuinely subtle part)

**Atomicity — PARTIALLY-SOLVED.** The working pattern (FActScore, 2023) is LLM-prompted decomposition of a sentence
into short, self-contained atomic statements — one sentence routinely yields several. The catch: atomic-fact
granularity is METHOD-DEPENDENT — Russellian, event-based (Neo-Davidsonian), and semantic-parse decompositions
disagree on where to cut, and this shifts downstream scoring (confirmed by both FActScore follow-ups and classical
OpenIE's long-standing n-ary-collapsing-to-binary problem). For facts with more than two arguments (qualifiers,
conditions, units) — Text2NKG (NeurIPS 2024) and Wikidata-style reification (fact-as-node, qualifiers as edges off
that node) are the standard representations. **Design implication for a triple-based substrate:** one sentence maps
to a SET of atomic triples, not 1:1; use reification (a claim-node carrying provenance/qualifiers/confidence, with
S-P-O as the base edge off that node) rather than trying to force every qualifier into the primary triple — this
also gives the gate a natural place to attach its own gate-stats (schema-fit score, surprise score, corroboration
count) as claim-node metadata rather than triple metadata.

**Assertion detection — fragmented, uneven maturity, this is the real gap:**
- Definitions: fairly mature (DEFT corpus — 21,303 sentences from open-source textbooks + SEC filings, 11,004
  definition annotations; WCL). Authors themselves note cross-sentence and implicit definitions remain hard, but
  pattern+LLM catches the majority.
- Hedge/speculation: mature IN-DOMAIN but domain-brittle — CoNLL-2010 shared task reports F1 ~85% on biomedical text
  (BioScope) but only ~55% on Wikipedia. **This domain-transfer gap is the single most load-bearing caveat for us** —
  our textbook corpus will span many domains, and a hedge-detector tuned/validated on one domain should not be
  trusted blind on another without a domain-specific spot-check.
- Factuality/veridicality (FactBank, CommitmentBank): mature ANNOTATION schemes, but classifiers are corpus-specific
  and don't transfer cleanly — a 2026 paper is still proposing fresh factuality schemes for a new domain
  (parliamentary proceedings), i.e. this gets RE-SOLVED per domain, not solved once generically.
- **Example/exercise/rhetorical-scaffold filtering: OPEN.** No dedicated benchmark found. This is handled ad hoc
  (cue-phrase lists, position-in-chapter heuristics, LLM-prompted classification) across the literature — genuinely
  the least mature sub-piece, and exactly the piece a textbook-reading pipeline leans on hardest (textbooks are
  saturated with worked examples and end-of-section exercises that must NOT enter the fact stream as literal claims).
  **This is where we build our own heuristic rather than import one**, combining position-in-document cues
  (worked-example/exercise environments are typically visually/structurally demarcated in source textbooks — headers,
  numbering, imperative mood) with an LLM classification fallback for the residual.

**Attribute-value-unit extraction — PARTIALLY-SOLVED**, closest to mature for canonical single-quantity cases
(MatSciBERT reports NER F1 ~87% for material/property/entity extraction at 3.27M-abstract scale; unit normalization
via ontologies like QUDT is standard). Open issues: unit ellipsis ("5 to 10 mg" sharing one unit across a range),
distinguishing true measurements from incidental numbers (figure/table references, chemical-formula subscripts), and
multidimensional/ratio quantities needing bespoke parsing. Good enough to use directly for the common case
("X boils at 100C" -> entity=X, attribute=boiling_point, value=100, unit=Celsius); flag low-confidence extractions
(ranges, unusual units) for the trust-gate to weight down rather than silently trusting them.

### 3. Images/diagrams — PARTIALLY-SOLVED, sharply bifurcated by realism

Simple, templated pedagogical diagrams (AI2D — grade-school science diagrams with label/arrow/region structure) are
near-solved: Claude 3.5 Sonnet ~94.7%, GPT-4o ~94.2% on the AI2D leaderboard. This is the textbook-typical case for
most K-12/intro-level material. Realistic scientific figures are a different regime entirely: CharXiv (2,323 charts
pulled directly from research papers, not templated) shows GPT-4o at only 47.1% on reasoning questions vs 80.5% human
— a 33-point gap — with reported brittleness to trivial perturbation (up to 34.5-point degradation), and consistent
hallucination as a measured failure mode across ChartBench/ChartMuseum/ChartHal/2024-2025 benchmarks. **Caveat: harder
than prose extraction, and the gap is large and now well-measured** (not folklore). Design implication: diagram-
derived facts should enter the pipeline at a LOWER default trust tier than prose-derived facts regardless of source
trust, until per-domain spot-checks establish the local diagram style sits closer to AI2D than CharXiv.

### 4. The extraction -> gate handoff, and the transparency question

The line: the LLM/OpenIE extractor produces a **proposal** — canonical S-P-O (+ qualifiers, via reification) +
provenance (source sentence, source document/trust-tier, extractor identity, extractor's own confidence score). The
glass-box GATE then computes its accept/provisional-hold/reject decision from properties of that proposal AND the
existing graph state ONLY — schema-fit (local reachability/embedding score against the graph neighborhood, per the
now-LANDED finding in `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md` that schema-fit,
not global-rank surprise, carries the discriminating signal), corroboration count, and ingestion-order-dependent
tightening — with ZERO further LLM calls at that stage.

**Is this legitimate, or does it undermine the "transparent reasoning" value?** Legitimate, with two conditions:
1. Extractor confidence must be passed THROUGH as a gate input feature, not discarded at the extraction/gate
   boundary — a shaky extraction should not enter the graph with the same standing as a clean one. If confidence is
   dropped, the gate is reasoning over information it doesn't have, which IS a transparency leak.
2. Raw source text must be logged alongside every claim-node for audit — a human (or the substrate itself, later)
   can reconstruct WHY a claim entered the graph by reading the gate's own stats (schema-fit/corroboration/order) plus
   the disclosed source sentence, without needing to re-run or trust the LLM's internal reasoning. The acceptance
   DECISION is glass-box even though the proposal's ORIGIN (the LLM call) is not — this is analogous to a visual
   system: nobody calls a reasoning architecture opaque because retinal phototransduction isn't symbolic; the
   reasoning starts once a proposal (percept) exists, and that reasoning is what we're claiming is glass-box.

**Where it would genuinely break:** if downstream reasoning ever needed to justify a claim's MEANING by pointing back
into the LLM's internal reasoning trace (rather than to the triple + its gate-stats + its logged source sentence),
opacity would leak into the reasoning layer proper. It does not currently need to — the gate's stats are computed
from graph-structural properties, not from re-querying the extractor.

**The one real risk, flagged honestly: correlated hallucination masquerading as corroboration.** If "corroboration"
is counted as multiple LLM extractions of the same source (or the same LLM re-run on paraphrases of one underlying
claim), that is NOT independent evidence — LLM hallucination patterns are systematic, not i.i.d. noise, so repeated
LLM extraction could inflate a false claim's corroboration count without it ever being true. Mitigation: count
corroboration by DIVERSE independent sources/extractor-tools (e.g., OpenIE-extracted-from-source-A AND
LLM-extracted-from-independent-source-B), not by repeated LLM calls on the same or paraphrased text. This is a
concrete design constraint the gate's corroboration-counting logic needs, not a blocker.

### 5. The single-pass / trust-gated design (Frontier-2)

The lit-scan on single-exposure learning (fast-mapping in children/adults; one-shot ML memory-augmented networks) is
consistent: single-exposure encodings are FAST but FRAGILE in both biological and artificial systems — durability
normally requires repetition or consolidation. Nothing in that literature shows single-pass durable writing is "free."
But the separate, well-developed Bayesian testimony-epistemology literature (Bovens & Hartmann; Olsson) directly
covers this case: an agent updates jointly on a claim AND on the source's reliability from a single report, with
update magnitude CONTINUOUS in prior source reliability — a near-certain-reliability source's single report shifts
belief close to (not exactly to) certainty. No paper packages "trusted source -> skip corroboration entirely" as a
discrete named principle; it's the natural LIMIT of the continuous rule, not a separate, unprecedented mechanism.
Frontier-2 is therefore a **defensible simplification of an established formal principle**, not a claim unsupported
by any prior theory — but also not something the literature shows is risk-free.

**Trust-gated pipeline design (extends the existing gate, does not replace it):**
- Every source gets a continuous trust prior at ingestion time (vetted textbook = high fixed prior; unvetted/unknown
  web text = low prior; this can start as a simple tiered lookup, refined later).
- **Trust conditions the CORROBORATION requirement only**, not the whole gate. For trust above a threshold,
  corroboration-count requirement drops to 1 (single-pass write is permitted) — but schema-fit and surprise checks
  STILL run and can still hold or reject a proposal. For low-trust sources, corroboration N>=2-3 independent
  sources/extractors is required before promotion from provisional-hold to committed.
- **Rationale for keeping schema-fit/surprise mandatory regardless of trust:** source-trust answers "is the claimed
  fact true in the world"; schema-fit/surprise answer "did we extract/parse it correctly, and does it cohere with
  what the graph already knows." These are orthogonal axes. A vetted textbook sentence can still be MIS-extracted
  (garbled OpenIE output, LLM misreading a nested clause) — trusting the SOURCE does not certify the EXTRACTION. This
  is the concrete reason Frontier-2 should be read as "skip the repetition/corroboration requirement for trusted
  sources," not "skip the gate."

This is a small, principled generalization of the already-landed 3-signal gate (schema-fit / surprise / corroboration
/ order) — corroboration threshold becomes a function of source-trust rather than a fixed constant. No new mechanism
is needed; this is a parameterization of the existing architecture.

## Cross-thread synthesis

- Directly builds on `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md` (schema-fit carries
  the fix; global-rank surprise is chance-level) — the extraction/gate line here assumes that landed result, i.e.
  schema-fit is computed against the SAME local-reachability structure the gate already scans, so extraction proposals
  feed a gate whose core discriminating signal is already validated as non-chance.
- Builds on `research_curriculum_prerequisite_datasets_2026-07-16.md` — TQA (real textbook prose, implicit order, zero
  access friction) is the natural corpus for the cheap decisive test above; it is already the recommended pilot
  dataset for the separate ingestion-order thread, so one corpus serves both drills.
- Builds on `research_ingest_gate_frequency_vs_novel_claim_validity_2026-07-16.md` (frequency-based trust for
  familiar claims is brain-consistent; gate advantage concentrates on NOVEL claims) — reinforces that the
  extraction/assertion-filtering step matters MOST for novel/technical textbook content precisely where hedge/
  veridicality detectors are least validated (the CoNLL-2010 85%->55% domain-transfer gap is a direct warning here).
- Adjacent to `research_biology_beyond_neocortex_ingest_gate_2026-07-16.md` and
  `research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md` (brain needs repetition/consolidation) —
  this note's Frontier-2 section is the direct counterpoint: the brain literature on fast-mapping fragility is the
  reason repetition matters biologically, and Bayesian testimony theory is the reason a sufficiently-trusted written
  source can legitimately bypass that requirement for an artificial system without new theory being needed.

## Substrate-product implications

- Extraction is confirmed BUILD-TIME, off-the-shelf-tool territory (per the PIVOT) — no new research needed to START
  building the ingest pipeline; the open piece is a SMALL custom classifier (example/exercise/rhetorical filtering)
  layered on top of mature components (OpenIE for candidates, LLM for arbitration/qualifiers/definitions, hedge-cue
  lexicon + position heuristics for assertion typing).
- The cheap decisive test above is directly actionable as a build-time measurement task (not a substrate cell): grade
  ~100 hand-picked TQA sentences through an off-the-shelf LLM extractor + a simple heuristic classifier, no gate
  involved yet. This is the natural next step before any gate-integration cell is authored — it validates the INPUT
  quality the gate will actually receive, decoupled from gate-mechanism questions already settled by the landed
  schema-fit result.
- Design constraint to carry into any future gate-integration cell: corroboration counting must be keyed on
  independent SOURCES/extractor-tools, not repeated LLM calls, to avoid the correlated-hallucination-as-corroboration
  failure mode identified above.
- Design constraint: trust conditions corroboration-count-required, not the schema-fit/surprise legs of the gate —
  this keeps the already-landed, validated gate mechanism intact while adding the single-pass capability Frontier-2
  wants.
- Diagram/chart-derived facts should default to a lower trust tier than prose-derived facts, independent of source
  trust, until textbook-specific diagram style is spot-checked against the AI2D/CharXiv maturity split.

## Calibration

Per the lit-scan calibration penalty: the extraction-toolchain and fact-operationalization maturity claims are
lit-CONFIRMED (published benchmarks exist for each sub-claim), so those carry P~0.55-0.65 as reported (moderate
literature-grounded confidence, not deflated to novel-synthesis levels). The NOVEL-SYNTHESIS pieces — the
extraction/gate legitimacy argument and the trust-conditions-corroboration-only design — are capped per
[[feedback-lit-scan-calibration-penalty]] at P<=0.50, deflated further by 0.15-0.25 for being uncharted-regime
synthesis specific to this substrate's gate architecture.

**P_deflated (overall pipeline-design confidence, novel-synthesis-capped) = 0.40**

## Citations (verified count: 22)

CaRB; Groth et al. 2018 (Open IE on Scientific Text); Open IE survey (arXiv:2310.11644); SpERT; REBEL; biomedical
zero-shot RE benchmark (arXiv:2504.04083); "LLMs Underperform Graph-Based Parsers..." (arXiv:2604.08752);
AutoSchemaKG (arXiv:2505.23628); OIE rule-to-LLM survey (ACL 2024 findings); FActScore (arXiv:2305.14251);
OpenFActScore (arXiv:2507.05965); Text2NKG (arXiv:2310.05185); hyper-relational KG message passing
(arXiv:2009.10847); CoNLL-2010 shared task; factuality annotation scheme, parliamentary domain (arXiv:2509.26406);
DEFT corpus / SemEval-2020 Task 6 (arXiv:2008.13694); Measurement Extraction with NLP (EMNLP Findings 2022);
Wiki-Quantities/Wiki-Measurements (Nature Sci. Data 2025); MatSciBERT (npj Comp. Materials 2022); AI2D benchmark
leaderboard; ChartQA (arXiv:2203.10244); CharXiv (arXiv:2406.18521); fast-mapping / one-shot learning literature
(Frontiers in Psychology 2012; ASHA JSLHR 2022; PMC12344786; MANN arXiv:1605.06065) and Bayesian source-reliability
theory (Bovens & Hartmann, via Synthese 2020 review) — grouped as one citation cluster for the single-exposure /
trust-weighting sub-topic.
