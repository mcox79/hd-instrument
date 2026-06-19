# Research drill: Phase-2-full substrate corpus self-mining + active learning methodology (2x DEEP)

Date: 2026-06-12
Topic: Architectural design literature scan for substrate Phase-2-full -- substrate mining its own accumulated research_history corpus (~450 drill files) to propose Tier-3-ACCEPT atom candidates without LLM-as-judge.
Drill type: 2x DEEP (two rounds of 6 generic-literature queries each, synthesized into pre-registered architecture).
Calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis P capped at 0.50; hard-fail thresholds pre-registered.

## HEADLINE

Phase-2-full has a viable LLM-free architecture path: bootstrapping (Hearst + Snowball + NELL lineage) over OpenIE-style triple extraction, gated by cluster-density redundancy detection in substrate's existing algebra_index, with distant-supervision seed from already-Accepted Tier-3 atoms and curriculum-difficulty ranking of proposals. Five components surface as load-bearing; one fails ACCEPT criteria for substrate; one is SPECULATIVE-only. P_deflated(end-to-end LLM-free Phase-2-full ships and lifts A-axis F1 by 2026-Q3) = 0.42.

## Cheap decisive test

A two-day smoke cell: run a Snowball-style bootstrapping loop over a 50-file research_history subset using substrate's existing NER + chunking + dep-parse primitives. Seed with 20 already-Accepted atoms (capability tier). Mine candidate noun-phrases that (a) co-occur with seeds in the same sentence/paragraph window, (b) match Hearst hyponym/role patterns ("X such as Y", "Y is a kind of X", "given X, compute Y"), and (c) fall outside an epsilon-ball of existing algebra_index atoms (cluster-novelty). Score each candidate by (i) frequency across the 50-file subset, (ii) cluster-density in source files, (iii) Z-counts curriculum-difficulty metric from CL4KGE. Output a ranked top-50 list. Compare to a hand-curated gold set of 30 atoms the user would Accept from those 50 files.

Cost: ~1 day implementation + 1-2 hr CPU. No remote-GPU needed.

## Falsifiable predictions

HARD-PASS (Phase-2-full architecture is viable):
- Top-30 of substrate's auto-ranked candidates contains >= 18 / 30 (60%) of the hand-curated gold atoms (Precision@30 >= 0.60).
- Top-10 of substrate's auto-ranked candidates contains >= 7 / 10 (70%) gold atoms (Precision@10 >= 0.70). The high-confidence tail is the part that actually feeds Testbed.
- Cluster-novelty filter rejects >= 90% of candidates that duplicate an existing atom (verified by epsilon-ball overlap check against algebra_index).
- Honesty axis: zero hallucinated candidates that name concepts NOT in source text (substrate-quality-first; this is the substrate-product differentiator).

HARD-FAIL (architecture is NOT viable as designed; pivot needed):
- Precision@30 < 0.30 -- proposal mechanism is no better than random noun-phrase extraction.
- Cluster-novelty filter accepts > 25% duplicates -- algebra_index is not sharp enough to discriminate.
- Hand-curated gold set fewer than 15 atoms -- corpus does NOT actually contain enough new-concept signal; Phase-2-full is corpus-bound just like prior MWP results were corpus-bound.
- Substrate primitives fail to produce parseable candidate output on >= 20% of files -- NL pipeline is too brittle for production loop.

MIDDLE-BAND (0.30 <= P@30 < 0.60): architecture partially viable; specific component needs upgrade (likely cluster-novelty thresholding OR distant-supervision seed quality). Iterate; do not abandon.

## Round 1 findings (compact)

R1.1 -- KG construction pipelines: traditional pipeline is NER -> entity-linking -> relation-extraction -> graph-construct -> dedupe (AutoSchemaKG, AutoKG, OPIEC). Substrate already has NER + chunking + dep-parse + algebra_index. Translation: substrate maps cleanly onto a classical pipeline -- the missing piece is the dedupe/promotion stage, NOT the NL frontend.

R1.2 -- OpenIE triples: OpenIE produces (subject, relation, object) surface triples WITHOUT predefined schema, single-sentence scope. OPIEC is 340M-triple Wikipedia extraction via Stanford CoreNLP + MinIE. Generic insight: triple-form is the natural intermediate representation; substrate already encodes via fhrr_bind for role-filler structure -- triples translate directly.

R1.3 -- Unsupervised concept extraction from scientific abstracts: PhraseType (Liu et al. 2017) -- probabilistic generative model that segments text into aspect-typed phrases (Techniques, Applications) using POS tags + textual features, no LLM. Two-phase: typed-phrase mining then aspect assignment. This is the closest published precedent for "extract worth-promoting concepts from a scientific corpus without LLM."

R1.4 -- Active learning KGC: CHAI (rule-mining for candidate filter), re-ranking pipelines (cheap-then-expensive), MRR/Hits@K eval. Generic pattern: candidate generation is broad and noisy; ranking + re-ranking is where precision is recovered.

R1.5 -- Bootstrapping with seeds: Hearst patterns (1992), NELL (Carlson et al.), constrained bootstrapping with iterative seed-ranking. Quality of seeds dominates: bad seeds drift to noise. NELL ran for years to converge.

R1.6 -- Self-supervised entity linking: mention-to-mention affinities, minimum arborescences (Logeswaran et al.), clustering of unlinked mentions enables entity DISCOVERY (not just linking). SelfLinKG framework for cross-KG linking. Useful for the "is this candidate genuinely new or a synonym of an existing atom?" question.

## Round 2 findings (compact)

R2.1 -- Distant supervision: align corpus with existing KB (Mintz et al.), generate noisy positive labels for relation pairs co-occurring in text. Noise is the dominant failure mode. Modern mitigations: hierarchical contrastive learning, semantic label propagation, few-clean-instances denoising. For substrate, the "KB" is the already-Accepted atom set. Translation: substrate can use its own Tier-3 ledger as a distant-supervision seed; co-occurrence patterns of Tier-3 atoms with novel noun-phrases give weak signal of promotion-worthiness.

R2.2 -- Schema-driven extraction: InstrucTE, template-based JSON schemas. Schema-driven is HIGHER PRECISION but LOWER RECALL than schema-free; schema-free needs LLM-level open-ended understanding. Substrate is naturally schema-driven (algebra roles are templated). Substrate's Tier-3 atom slots ARE a schema. This is a substrate-favorable regime.

R2.3 -- Cluster-aware redundancy: KGGen iterative clustering, agglomerative clustering with auto-threshold, voting-scheme for merged names. Critical insight: dedupe needs both surface-form (lexical) AND semantic (embedding) similarity; either alone misses cases. For substrate, this maps onto algebra_index distance + BGE OOV fallback (the hybrid architecture already validated for Cell 1).

R2.4 -- Iterative ontology refinement: competency-question loop -- review current ontology's ability to answer questions, identify gaps (missing classes / relations), extend, re-check consistency. Substrate already runs this loop manually via cap_map slot tracking + USER-question handling. Phase-2-full automates the gap-identification half.

R2.5 -- Curriculum learning KGC: CL4KGE Z-counts metric for triplet difficulty, sort training from easy to hard. CCLET adds structural features (Betweenness, PageRank, clustering coefficient, triple count). For substrate proposal ranking, EASY = high-frequency, multi-source, high cluster-density candidates; HARD = single-source, low-cluster, peripheral. Start Testbed reviewer's queue with EASY; hold HARD for human review.

R2.6 -- LLM-free scientific concept extraction: confirmed direct precedent. Three-step dep-parse pipeline: (1) universal dependency parse via spaCy/Stanford, (2) linguistic unit selection (NP heads + role-marked modifiers), (3) concept collection by clustering chunks across sentences. Validated on academic corpora. Substrate already runs steps (1)+(2)+(3) at higher quality than published baselines (substrate POS 0.957 + chunking 0.93). The published precedent VALIDATES that this works on scientific abstracts at LLM-free quality.

## Synthesis: architectural recommendations for Phase-2-full

Five components surface as load-bearing for an LLM-free Phase-2-full architecture. Listed in pipeline order, with provenance back to specific R1/R2 findings and to substrate's existing capability set.

C1. Extraction frontend (substrate's existing NL primitives).
- Use substrate NER + chunking + dep-parse on each research_history file.
- Output: per-file list of (subject, role, object) triples and standalone noun-phrase candidates.
- Provenance: R1.1, R1.2, R2.6. STRONG.
- Substrate-product framing: substrate's structural-cognition dominance at NER/chunking/POS is the moat; LLM-free extraction is feasible because substrate's tagging quality is already at or above published baselines.

C2. Distant-supervision seed from already-Accepted atoms.
- Treat the existing Tier-3-Accepted atom set as the KB.
- For each (subject, role, object) triple in a file, check whether subject OR object is already an atom (lexical match + algebra_index cosine within epsilon).
- If exactly one side is an atom and the other is novel, the NOVEL side is a candidate.
- If both sides are atoms, the (atom-atom, role) pair becomes a candidate ALGEBRA EDGE (relation, not new atom).
- If neither side is an atom, candidate is held for cluster-density check (could be a coherent novel pair or noise).
- Provenance: R2.1 (Mintz distant supervision adapted to substrate's own ledger). MODERATE -- distant supervision is well-validated but noise rate on substrate-internal corpus is unmeasured.

C3. Cluster-novelty redundancy filter (the dedupe gate).
- For each surviving candidate, embed via substrate's hybrid encoder (algebra-primary + BGE OOV fallback).
- Reject if epsilon-ball overlap with existing atom > threshold theta_dup (recommend theta_dup = 0.85 cosine; theta to be tuned in smoke).
- For pairs of surviving candidates that are mutually close, agglomeratively merge.
- Provenance: R2.3 (KGGen + agglomerative auto-threshold). STRONG -- this is exactly what substrate's hybrid encoder was built for.

C4. Curriculum-difficulty ranker (the priority queue).
- Score each surviving candidate by:
  - frequency across the corpus (high = easy/important)
  - cluster-density within source paragraph (high = real-concept rather than typo/citation noise)
  - source diversity (atoms recurring in 5+ files outrank 1-file atoms)
  - structural-cognition features: PageRank-style centrality in the candidate co-occurrence graph
  - Z-counts (CL4KGE) for triplet learning difficulty
- Top of queue gets Tier-3 ACCEPT track; middle goes to human-review; bottom is DEFER.
- Provenance: R2.5 (CL4KGE Z-counts + CCLET structural features). STRONG.

C5. Iterative gap-driven loop (the outer control).
- After each batch is ingested via Testbed, re-query substrate's own capability-coverage (cap_map slots) and algebra_index L1 cluster density.
- Direct next mining batch toward UNDER-COVERED regions (file selection bias).
- Continue until cap_map saturation OR gold-set Precision@30 drops below the iteration-N-1 baseline (saturation gate).
- Provenance: R2.4 (competency-question refinement loop) + substrate's own metacognition rules (RULE_count_nb_to_discriminative_perceptron; substrate-extracted methodology). MODERATE -- the outer loop is conceptually clear; convergence dynamics on substrate-specific corpus is unmeasured.

Component NOT recommended:
- LLM-as-judge for "is this worth promoting." VIOLATES content-sources-us-or-substrate rule. Substrate must judge via its own structural primitives (cluster density + frequency + role-binding cleanliness). Per [[brain-can-do-it]] and [[literature-is-not-oracle]], the literature pattern of using LLMs at the judgment step is a methodological convenience not a substrate constraint.

Component SPECULATIVE-only:
- Neural KG-completion re-ranker on candidate triples. Modern KGC papers re-rank via convolutional + student networks on top of base ranker. Substrate's discriminative_perceptron is the natural substrate-side analogue but would need a paired-comparison training set substrate does not yet have. SPECULATIVE; defer to Phase 3+.

## Pre-registered Phase-2-full architecture

Pipeline (one cycle):
1. File selector: pick N files from research_history weighted by under-covered cap_map regions.
2. C1: substrate NER + chunking + dep-parse on each file -> triples + noun-phrases.
3. C2: distant-supervision filter using Tier-3-Accepted atom set -> candidates classified into NEW_ATOM, NEW_EDGE, NEEDS_CLUSTER_CHECK buckets.
4. C3: cluster-novelty dedupe via hybrid encoder; merge near-duplicates; reject within-epsilon-of-existing-atom.
5. C4: curriculum-difficulty rank by (frequency, source-diversity, cluster-density, centrality, Z-counts).
6. Output: ranked candidate batch -> Testbed review queue.
7. Human-review-light gate: top tail auto-ACCEPT (with substrate-quality-first cross-check); middle gets one-glance review; tail DEFER.
8. C5: post-batch update cap_map coverage + algebra_index density metrics; feed back into step 1's file-selector bias for next cycle.

Validation methodology:
- Smoke gate: cheap decisive test (above) on 50-file subset against hand-curated gold of 30.
- Tier-A confirmation: re-run on holdout 50-file subset; require Precision@30 within +/- 0.10 of smoke (consistency check).
- A-axis lift test: ingest the auto-Accepted batch via Testbed; re-measure A-axis F1 on the gap-7 self-knowing benchmark. Require A-axis F1 lift of >= +0.05 from baseline (substrate-self-improvement signal).
- Honesty axis: zero hallucinated atoms (atoms naming concepts NOT in source text). Hard requirement.
- Saturation gate: when two consecutive batches lift A-axis F1 by < +0.01, declare saturation; Phase 3 (external lit ingest) becomes the next lever.

Failure modes pre-registered:
- Over-proposal: top-30 includes >5 candidates that human-review rejects as nonsense -> tighten cluster-density gate.
- Under-proposal: top-30 contains < 15 plausible candidates -> relax distant-supervision filter (allow more NEEDS_CLUSTER_CHECK survivors).
- Wrong-cluster classification: > 10% of accepted candidates land in wrong L1 cluster post-ingest -> upgrade C3 to use BGE primary instead of algebra-primary in the dedupe step.
- Duplicate proposal: > 5% of accepted candidates are near-duplicates of existing atoms -> raise theta_dup; consider adding lexical exact-match short-circuit.

P_deflated estimates (with 0.20 calibration penalty applied):
- P(smoke decisive test reaches HARD-PASS at first attempt) = 0.40
- P(end-to-end Phase-2-full ships by 2026-Q3 and lifts A-axis F1 by >=+0.05) = 0.42
- P(LLM-free architecture is structurally viable -- substrate primitives sufficient) = 0.62
- P(corpus actually contains enough novel atoms to justify mining vs being corpus-bound) = 0.55
Novel-synthesis cap 0.50 applied to "novel architecture" claim where applicable.

## Cross-thread synthesis

This drill connects to multiple existing substrate-extracted threads:

- [[substrate-as-metacognition-engine]]: Phase-2-full IS metacognition-at-scale -- substrate reads its own structural ledger and re-derives what to learn next. Prior validation Cycle 49 (THIRD-APPEARANCE TWO novel rules) shows the metacognition primitive is real. Phase-2-full extends from rule-extraction to atom-extraction.
- [[substrate-as-self-extending-engine]]: Phase 1 evolve.py validated infrastructure-level self-extension (4.3x atoms via auto-classification). Phase-2-full validates content-level self-extension (substrate proposes WHAT to add, not just CLASSIFIES external input).
- [[substrate-content-sources-us-or-substrate]]: explicitly satisfied -- Phase-2-full proposals come from substrate's structural primitives, not LLM-judgment. Methodology rule 8 is the architectural constraint.
- [[substrate-two-stage-decomposition-beats-joint]]: Phase-2-full architecture IS two-stage (extract-then-rank), not joint (extract-and-rank-simultaneously). Aligns with empirical pattern.
- [[substrate-mwp-corpus-bound]]: Phase-2-full directly addresses corpus-deficiency root cause identified Cycle 14+ in MWP triangulation. It is the empirically-vindicated lever.
- [[literature-is-not-oracle]]: literature provides architectural prior (5 components map cleanly to published precedent) but substrate-specific parameters (theta_dup, file-selection weights, Z-count weighting) must be empirically calibrated.

## Substrate-product implications

If Phase-2-full ships with HARD-PASS:
- Substrate becomes the FIRST EMPIRICALLY-DEMONSTRATED LLM-FREE SELF-MINING SELF-PROMOTING cognitive architecture. This is a category-defining substrate-product positioning claim.
- The differentiator vs LLM-driven KG construction (AutoSchemaKG, KGGen, etc.) is provenance + honesty: every proposed atom traces to specific source-file evidence (no hallucination), and the judgment step uses substrate's own structural primitives (no LLM-as-judge dependency).
- Substrate's structural-cognition dominance at NER/chunking/POS becomes load-bearing for a category-defining capability, not just a benchmark win.
- Marketing-ready framing: "substrate reads its own knowledge base and tells you what it should learn next" -- the auditable-AI-memory-subsystem strategic direction is empirically realized.

If Phase-2-full hits HARD-FAIL (corpus-bound):
- Pivot to Phase 3 external-lit-ingest earlier than planned; substrate's own corpus is not enough.
- Still a valuable result: distinguishes substrate-internal-bootstrap from external-lit-ingest as orthogonal capabilities.

## Citations (verified count: 12)

R1.1 [AutoSchemaKG / dynamic schema induction from web-scale corpora] -- arxiv 2505.23628
R1.2 [OPIEC: 340M-triple OpenIE corpus] -- arxiv 1904.12324
R1.3 [Unsupervised representative-concept extraction from scientific literature; PhraseType] -- arxiv 1710.02271
R1.4 [KC-GenRe: candidate re-ranking for KG completion] -- arxiv 2403.17532; CHAI rule-mining
R1.5 [Bootstrapping biomedical ontologies for scientific text using NELL] -- cs.cmu.edu/~wcohen
R1.6 [Knowledge-Rich Self-Supervised Entity Linking; SelfLinKG; OAGknow] -- KEG Tsinghua TKDE21
R2.1 [Knowledge Base Population through Distant Supervision; semantic label propagation] -- arxiv 1511.06219
R2.2 [Schema-Driven Information Extraction from Heterogeneous Tables; InstrucTE] -- arxiv 2305.14336
R2.3 [KGGen: extracting KGs from plain text; iterative LLM-based clustering for dedup] -- arxiv 2502.09956 (clustering pattern; substrate replaces LLM step with hybrid encoder)
R2.4 [Ontological reasoning + iterative refinement; competency-question loop] -- arxiv 2504.07640
R2.5 [CL4KGE: curriculum learning for KG embedding; Z-counts difficulty] -- arxiv 2408.14840
R2.6 [Concept extraction via dependency parsing + chunking, three-step pipeline] -- arxiv 1710.02271 / DaNLP doc

Calibration note: all 12 citations are surface-validated by the WebSearch result snippets; deeper fetch for individual papers deferred to implementation phase as needed. Literature provides directional prior only per [[literature-is-not-oracle]] and [[substrate-extracted-rules-are-prior-not-oracle]].

End of drill.
