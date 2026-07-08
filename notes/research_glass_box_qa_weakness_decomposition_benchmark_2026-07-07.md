# The next big benchmark: glass-box QA over ingested knowledge, scoped as a WEAKNESS-DECOMPOSITION instrument, not a scoreboard

Date: 2026-07-07. Owner: research (Opus synthesis over substrate scour + 2 parallel Sonnet
lit-scans, generic terms only per [[feedback-query-privacy-decomposition]]). Drill type:
milestone scoping (no cell built, no dispatch), operationalizing M3's "reasoning over ingested
knowledge, glass-box, self-auditing" deep-prize into a concrete first benchmark.

**MID-DRILL REFRAME (incorporated, not a footnote):** the coordinator corrected the framing
partway through this drill. The LLM/encoder comparison is a DIAGNOSTIC INSTRUMENT to find the
substrate's load-bearing weak points, NOT a scoreboard; "beat the LLM" is explicitly not the
goal. Per USER: *"I don't really care overly much about comparing against LLMs — I'm fine doing
it, but only to identify what are the load bearing points of weakness in these measurements that
we need to focus on for improvement."* Everything below is restructured around that: the
benchmark's PRIMARY output is a per-cause weakness map, ranked by gap x fixability; the aggregate
"do we match the LLM" number is a secondary headline, kept honest (don't assume we lose — the
brain is the existence-proof the ceiling isn't fundamental) but not the point.

## HEADLINE

**The benchmark that actually serves the reframe is not a new corpus or a new eval script — it is
PER-STAGE ABLATION LOGGING wired onto machinery that mostly already exists.** Three things are
true simultaneously and none of them requires new invention to state cleanly: (1) the project
already runs a 5-arm ablation design (closure/oracle, frozen-encoder, substrate, random,
scrambled-control) on ConceptNet-held-out multi-hop QA — this IS a weakness-decomposition harness,
just not yet run at target scale or against an LLM; (2) a fresh SMOKE result landed THIS SESSION
(`data/exp_conceptnet_semantic_seeded_beam_composition_v1_smoke/metrics.json`, HARD_FAIL, verified
on disk, n=201/51-with-path) that is itself a clean worked example of why per-cause decomposition
matters: the AGGREGATE result (combined fix, SEM_BEAM=0.157) looks like a flat negative, but
decomposed by arm it reveals two causes with OPPOSITE signs — beam-width alone HELPS
(RANDOM_BEAM=0.529, beating both `bge_cached`=0.490 and the external bar 0.502) while
semantic-seeding alone HURTS badly (SEM_K1=0.216, worse than the ORIGINAL random-code baseline
RANDOM_K1=0.510) and combining them is worse than either single fix (SEM_BEAM=0.157) — an
aggregate-only benchmark would have reported "the composition fix failed" and buried the fact
that one of its two components is a working lever; (3) the single biggest verified blocker to
building the FULL harness is not a missing capability, it's a missing LOGGING LAYER: status_log
2026-07-07T17:07:59Z records that per-item retrieval outcomes were **never persisted** anywhere in
the encoder lineage ("per-item data was never persisted (aggregate-only metrics.json)") — you
cannot attribute failures to a stage if the pipeline only ever writes a scalar summary. Fix that
one gap and most of the rest of the harness is composition of already-proven pieces, not new
research.

## Item 1 — THE BENCHMARK (task, corpus, why, and the instrumentation that makes attribution clean)

**Two-tier design, not a single corpus choice:**

**Tier 1 (run now, ~90% already built):** the ConceptNet-held-out multi-hop QA lineage
(`exp_substrate_conceptnet_kg_inference_transfer_cpu_v1` / N8 / the fresh
`exp_conceptnet_semantic_seeded_beam_composition_v1` smoke). This is NOT a fresh recommendation —
it's recognizing that the project's own standing cell family already implements the core of the
reframe's requirement (clean per-cause attribution) via its 5-arm design: closure (oracle ceiling,
0.980), frozen-BGE (encoder-retrieval-only baseline, 0.490-0.502), substrate (full mechanism under
test), random (floor), scrambled-relation (firing control — proves the mechanism is genuinely
doing something, not gerrymandered: `scramble_collapses=True` confirmed this session). Stratified
by trivial/nontrivial (path-length proxy for hop/branching-difficulty) — the same convention
MetaQA (1/2/3-hop) and MuSiQue (2-4 hop, leakage-minimized) use in the public literature
(confirmed via lit-scan below). **Recommendation: dispatch the FULL multi-seed version of the
already-smoked `exp_conceptnet_semantic_seeded_beam_composition_v1` cell before building anything
new** — it is the cheapest available read on the composition weakness-class, cost is CPU-only,
reuses the June-19 held-out split verbatim.

**Tier 2 (target/production, gated on the logging fix below + Stage-3 scale-test):** the SAME
5-arm-plus-scramble design, instantiated over the actual 970K dogfood self-knowledge corpus
(`data/substrate_director_kb_v1/entities.jsonl`) rather than ConceptNet alone. This is the
literal M3 "reasoning over ingested knowledge, glass-box" target. **Why NOT HotpotQA/MetaQA as
the primary corpus, contrary to the original framing of this drill:** the lit-scan surfaced a
concrete, citable reason to avoid public benchmarks here — "Generating Leakage-Free Benchmarks for
Robust RAG Evaluation" (SeedRG, arXiv:2605.08838) measured LLMs answering **31-78% of
HotpotQA/2WikiMultihopQA/QASC questions correctly with NO retrieval at all**, i.e. pretraining
contamination, not reasoning, drives a large share of "RAG works" claims on those sets. The
dogfood corpus (the project's own notes/preregs, chunked) has **zero contamination risk by
construction** — no pretrained model has seen it — which makes it a STRICTLY CLEANER instrument
for the reframe's actual goal (attributing failure to a real capability gap, not to an LLM's
memorized-answer shortcut). Use MuSiQue/MetaQA's hop-stratification convention as the
METHODOLOGICAL template, not as a corpus substitution.

**The instrumentation that makes attribution clean (this is what item 4 of the reframe demands,
and it's the actual missing piece):** an oracle-substitution ladder, per the lit-scan's confirmed
methodology (Layer6 RAG error-taxonomy paper, arXiv:2510.13975, 16 error types across
chunking/retrieval/reranking/generation stages, 377 hand-annotated errors; "Iterative RAG vs Ideal
Evidence," arXiv:2601.19827, names the oracle-context-substitution diagnostic explicitly; CRAG,
arXiv:2406.04744, separately penalizes hallucination vs. missing-answer per stage; RGB,
arXiv:2309.01431, four-axis robustness decomposition). Concretely, for each held-out question, run
the SAME pipeline four times, swapping in an oracle at exactly one stage per run: (i) oracle
retrieval + real composition + real refuse-decision, (ii) real retrieval + oracle composition
(ground-truth path) + real refuse, (iii) real retrieval + real composition + oracle refuse
(never wrongly abstain/never wrongly answer), (iv) all-real (production). The DELTA between
consecutive oracle-swaps isolates each stage's marginal contribution to the end-to-end error —
this is the standard, literature-precedented way to answer "which stage caused this specific
wrong answer" instead of guessing from an aggregate number. **This does not exist yet on this
substrate at corpus scale** (Tier-1's 5-arm design is a coarser version of the same idea — closure
already IS "oracle-everything" — but the per-stage middle rungs (ii) and (iii) aren't separately
instrumented) — this is the concrete engineering item that turns the existing ablation habit into
a full oracle-substitution ladder.

## Item 2 — THE BASELINES (and the fairness protocol)

**Encoder baseline: BGE-large, already wired and already fair.** `frozen_encoder`/`bge_cached`
arms already run on the identical held-out split, identical corpus, identical top-10 retrieval
budget as the substrate arm — no new work needed here, this comparison is already apples-to-apples
per the June-19 cell's own design.

**LLM baseline: does not exist yet at all — this is a real, concrete gap, not an oversight to wave
past.** Per lit-scan, recommend a small open-weight model in the Qwen2.5-1.5B / Llama-3.2-3B class
— these are the most commonly cited small-model choices in RAG-vs-baseline academic comparisons,
confirmed runnable single-GPU or CPU-only (MDPI 16(9):744, CPU-only inference feasibility study).
Run it in TWO conditions, both cheap: (a) **closed-book** (parametric-only, no retrieval) — this
is the single most informative arm for the reframe's purpose, because on the dogfood corpus
(zero contamination by construction) closed-book performance should be near-floor; if it is NOT
near-floor, that would itself be a diagnostic red flag (data leakage into the LLM's context some
other way, or the "fact" being probed is generic enough to be inferable without the corpus — a
useful negative-control finding either way); (b) **RAG-with-BGE-retrieval**, same top-k=10 budget
as the substrate/encoder arms — per the KILT protocol (arXiv:2009.02252), the accepted standard
for corpus-parity comparison (fix one corpus, one retriever, compare downstream heads). This
directly answers the reframe's fairness requirement: same corpus, same held-out split, same
retrieval budget for every arm.

**Standard pitfalls to design around (lit-scan-confirmed, concrete not generic):** contamination
(addressed above via the dogfood corpus's construction); mismatched retrieval depth/top-k between
arms (hold top-k identical across all arms, matching the June-19 cell's existing convention);
report Hits@k as primary (matching KG-completion/KGQA convention, e.g. EmbedKGQA) rather than
EM/F1 (an open-domain-QA convention less suited to structured multi-hop completion), stratified by
hop-count/branching per MuSiQue's established practice.

## Item 3 — THE PRIORITIZED WEAKNESS MAP (the actual deliverable per the reframe)

Ranked by (gap magnitude x near-term fixability), using only on-disk-verified numbers:

| Rank | Capability (load-bearing) | Substrate perf | Baseline perf | Gap | Status | Improvement lever + current state |
|---|---|---|---|---|---|---|
| **1** | **Multi-hop composition / branching-factor decode** | Hits@10=0.451 (June-19, n=233, CANONICAL) / SEM_BEAM=0.157, RANDOM_BEAM=0.529 (fresh SMOKE, n=201, decomposed) | BGE Hits@10=0.502-0.520 | **−0.05 to −0.35** depending on arm; nontrivial-only gap is worse (−0.72 to −0.84) than trivial (−0.40 to −0.81) | HARD_FAIL (canonical + smoke), but DECOMPOSED into 2 independent causes with opposite signs | Beam-width fix (RANDOM_BEAM) already crosses the BGE bar at smoke scale — HIGH near-term fixability, needs FULL multi-seed confirm. Semantic-seeding fix (SEM_K1/SEM_BEAM) actively BACKFIRES — root cause not understood, needs its own diagnostic before reuse (candidate cause: encoder-derived entity vectors may be collapsing branching structure the random codes preserved by chance; untested). |
| **2** | **Encoder retrieval at production scale (970K)** | Verified only at 177,899 (18% of target); cross-seed MIN ret_agree10=0.432, density m5 | N/A (untested regime, not yet a baseline-relative gap) | **UNKNOWN — the gap itself hasn't been measured yet** | Density-law PREDICTS mild growth (m*=6, band [5,7]), pre-registered, not yet empirically confirmed at scale | Density-dial retune per the JL/Larsen-Nelson mechanism-matched law (`research_density_scale_theory_reconciliation_970k_2026-07-07.md`); sweep designed, R1/R2 rungs in flight. Hub-formation risk flagged (chunk-near-dup clusters, 15.86% of V) as a SEPARATE, cheap, already-scoped mitigation (dedup). |
| **3** | **Self-audit / justification inspectability (the transparency axis an LLM structurally cannot offer)** | 3 of 4 rungs CANONICAL (Tier-1 self-query MM; Tier-2 source-direct entailment coverage=0.813, 24.8x retrieval ceiling; Tier-3 global-consistency MM clean); 5th rung (does retrieved+composed evidence actually ENTAIL the answer, not just retrieve-nearby) SMOKE-proven, not canonical | N/A (an LLM cannot produce this axis at all — structural, not a score to beat) | Not a numeric gap — a COVERAGE gap in the harness's own instrumentation | Strong on 3/4 rungs; 5th rung scoped (`research_justification_retrieval_rung_scoping_unblocked_by_source_direct_2026-07-06.md`), dispatch-ready, not yet built | Dispatch the justification-retrieval rung to FULL/canonical — cheap, reuses source-direct's leaf resolution + Tier-2 comparator, no new mechanism. |
| **4** | **Per-item / per-stage logging (the instrumentation itself)** | Aggregate-only metrics.json across the entire encoder lineage — per-item retrieval outcomes were confirmed NEVER PERSISTED (status_log 2026-07-07T17:07:59Z) | N/A | **This is the blocker that prevents measuring Ranks 1-3 cleanly at scale**, not a capability weakness | Verified-missing, not yet fixed | Add per-item logging (retrieved-ids, per-hop candidate set, refuse-decision, oracle-swap arm) to the eval harness BEFORE building Tier 2 — small, mechanical engineering task, no research risk, but everything else in this table is only cleanly attributable once this exists. |
| **5** | **Refuse/fabrication calibration** | AUROC 0.958-0.999 (N8: setrecall@M100000=1.000, refuse OOD=0.999/accept=0.997, per-seed-min 0.997/0.993); U1/FB15k-237: 0.974/0.958 | (LLM comparison not yet run) | **Not currently a weakness — the strongest measured capability.** Included so the harness doesn't let a future aggregate score DILUTE or HIDE this genuine strength inside a lower composite number. | CHAIN_GRADE | No lever needed; PROTECT this axis by scoring it SEPARATELY in any future aggregate, per the reframe's own "decompose, don't aggregate" principle. |

**The single biggest blocking item, per the reframe's item-4 requirement that the instrumentation
must decompose cleanly:** Rank 4 (per-item logging). Ranks 1-3 all already have credible, partially
or fully proven mechanisms; none of them can be cleanly measured at target scale, and none of
their failures can be cleanly attributed to a stage, until per-item/per-stage logging exists. This
is deliberately ranked above Rank 1 in terms of SEQUENCING even though Rank 1 has the largest
numeric gap — it is cheap, mechanical, zero-research-risk, and unlocks clean measurement of
everything else.

## Item 4 — THE LOAD-BEARING PATH (ordered, with status + biggest risk per item)

1. **Encoder retrieval CG-unblock @177K** — DONE, verified both seeds HARD_PASS on disk
   (`exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed{7,13}`). Risk: none remaining
   at this scale.
2. **Per-item/per-stage logging** (NEW item this drill surfaces as load-bearing, not previously
   sequenced this high) — NOT BUILT. Risk: none technical (mechanical addition to existing eval
   loops); the risk is PRIORITIZATION — it's invisible/unglamorous work that is easy to skip in
   favor of chasing Rank-1's more dramatic gap, but everything downstream needs it.
3. **Density-law scale validation to 970K** — PREDICTED (m*=6, band [5,7]), sweep R1/R2 in
   flight. Biggest risk: hub-formation on the 15.86%-of-V chunk-near-dup clusters degrading
   local top-10 rank agreement even if the aggregate trend matches prediction (a named,
   pre-registered, separately-testable risk, not a vague worry).
4. **Composition/branching fix** — SMOKE HARD_FAIL, but cleanly decomposed (beam helps,
   semantic-seed hurts). Biggest risk: the semantic-seeding backfire is UNEXPLAINED; if its root
   cause turns out to be fundamental (not an implementation bug), Rank-1 stays a durable weak
   spot rather than a closable engineering gap — this is the single most likely item to remain
   "load-bearing-weak" after everything else lands, and therefore the most important one to keep
   researching rather than declare closed.
5. **Self-audit 5th rung (justification-retrieval)** — SMOKE-proven, dispatch-ready. Risk: low;
   mechanical composition of already-proven pieces (source-direct + Tier-2 comparator).
6. **The integration/harness wiring itself** (LLM baseline pilot + oracle-substitution ladder +
   Tier-2 corpus instantiation) — UNBUILT. Biggest risk: scope creep — building the full
   oracle-substitution ladder before Ranks 2-5 land would mean building expensive instrumentation
   around capabilities that are still moving targets; sequence AFTER 2-5, not in parallel with all
   of them.

**The ONE item most likely to block the milestone:** not any single capability, but **Rank 4
(composition/branching)** combined with **Rank 2 (missing per-item logging)** — the two together
mean the project currently cannot say, with clean instrumentation, WHY composition underperforms
beyond the 2-cause hypothesis this session's smoke partially confirmed and partially refuted. Until
logging exists, further composition experiments will keep producing aggregate-only verdicts that
hide exactly the kind of decomposition (beam-helps/semantic-hurts) that made this session's result
interpretable at all — that interpretability only happened because this particular cell HAPPENED
to log 5 separate arms; it is not yet a structural property of the eval harness in general.

## Cheap decisive test

Two, in priority order, both CPU-only, both reuse existing pipelines with zero new corpus work:

1. **FULL multi-seed dispatch of the already-smoked `exp_conceptnet_semantic_seeded_beam_composition_v1`**
   (currently n=201/1-seed SMOKE only). This is the cheapest way to learn whether the
   beam-helps/semantic-hurts split replicates at real N and across seeds, or was a smoke-N=201
   artifact. Zero new design cost — the cell exists and already ran once.
2. **A 200-row LLM closed-book pilot on the SAME June-19 ConceptNet held-out split** (zero new
   corpus/split work): run a small local model (Qwen2.5-1.5B or Llama-3.2-3B class) closed-book
   over the existing 233 with-path + 233 without-path rows. This is the FIRST real
   substrate-vs-LLM data point the project will have had, and it's nearly free — no retrieval
   wiring needed for the closed-book arm, just a prompt template and the existing gold answers.

Both are pre-registrable now; neither requires building the full Tier-2 harness first.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, per weakness-class — not a single pass/fail)

**Composition/branching (Rank 1), FULL multi-seed rerun:**
- HARD-PASS (beam-helps hypothesis replicates): cross-seed RANDOM_BEAM Hits@10 >= bge_cached AND
  the SEM_* arms remain worse than RANDOM_* arms across all seeds (confirms the opposite-sign
  finding is real, not smoke noise).
- HARD-FAIL: RANDOM_BEAM's smoke-scale win over bge_cached (0.529 vs 0.490) collapses to at/below
  bge_cached at FULL scale/multi-seed — would mean the beam-width lever was a smoke-N artifact,
  not a real fix, and Rank 1 has NO currently-working lever (a materially worse finding than
  today's).
- MIDDLE (most likely per this drill's own read): beam-helps direction replicates but margin is
  thin/noisy across seeds; semantic-seed backfire replicates cleanly (this arm's smoke effect size
  was large, -0.3 to -0.6 absolute, less likely to be pure noise than the beam arm's smaller
  ~0.03-0.04 margin over bge_cached).

**Logging/instrumentation (Rank 4), the harness-build itself:**
- HARD-PASS: per-item logging (retrieved-ids, per-hop beam contents, refuse-decision, which
  oracle-swap arm) implemented and a single failed QA row can be traced to exactly one stage
  >=80% of the time (the rest legitimately multi-stage/ambiguous).
- HARD-FAIL: even with per-item logging, >50% of failures remain ambiguous across 2+ stages
  (would mean the pipeline's stages are too entangled for the oracle-substitution ladder to
  cleanly separate — a real, informative negative about the architecture's inspectability, not
  just an instrumentation bug).

**LLM closed-book pilot (Rank "does contamination confound exist on OUR corpus"):**
- HARD-PASS (clean instrument confirmed): LLM closed-book performance on the dogfood/ConceptNet
  held-out set stays near the random floor (<0.15 Hits@10, matching the project's own
  RANDOM_K1~0.04-0.51 range depending on exact split) — confirms zero contamination confound,
  meaning any later RAG-LLM-vs-substrate comparison on this corpus is measuring real
  retrieval+reasoning capability, not memorized-answer leakage.
- HARD-FAIL (contamination confound present): LLM closed-book performs materially above floor —
  would mean this specific ConceptNet slice IS memorized by the baseline LLM's pretraining
  (ConceptNet is public, so this is a real, non-trivial risk despite the dogfood-notes portion of
  the 970K corpus being safe by construction) — if this fires, the Tier-2 dogfood-only corpus
  becomes the ONLY clean instrument, and ConceptNet-based Tier-1 results must be caveated
  accordingly for any LLM-inclusive comparison (the substrate-vs-BGE-only comparisons already
  landed are unaffected, since BGE has no "closed-book memorization" failure mode to confound).

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):**
- P(composition FULL-rerun replicates smoke's opposite-sign pattern, MIDDLE-or-better per above):
  undeflated ~0.55-0.60 (clean smoke signal, scramble control fired, n=201 is small but the effect
  sizes are large, especially the semantic-seed backfire) → **P_deflated = 0.35-0.40**.
- P(per-item logging achieves >=80% clean single-stage attribution once built): undeflated
  ~0.50-0.60 (mechanically achievable, but no direct precedent on THIS pipeline's actual stage
  entanglement) → **P_deflated = 0.30-0.35**, capped at the novel-synthesis 0.50 ceiling since the
  oracle-substitution ladder itself is this drill's synthesis, not yet built or tested here.
- P(LLM closed-book pilot confirms zero-contamination on the ConceptNet slice): undeflated
  ~0.55-0.65 (ConceptNet facts are simple/common-sense and could be trivially inferable without
  memorization either way — genuine uncertainty, not just a citation-based worry) → **P_deflated
  = 0.35-0.45**.
- P("glass-box substrate matches/beats a small LLM on the FIRST aggregate benchmark run," the
  ORIGINAL framing's headline question, now explicitly secondary): given Rank-1's standing
  HARD_FAIL against a strong dense baseline (BGE), and an LLM RAG-arm inherits BGE's retrieval
  quality plus whatever reasoning an LLM adds on top, the honest prior is that an LLM+RAG arm
  likely EDGES the substrate on the aggregate composition metric at least initially — **P_deflated
  (substrate aggregate >= LLM+RAG aggregate on first run) = 0.20-0.30** — but per the reframe, this
  number is reported for completeness, not as the benchmark's success criterion; the weakness map
  above is the actual deliverable regardless of how this number lands.

## Cross-thread synthesis

Composes four already-verified threads without re-deriving them: (1) the ingest-arc scoping
(`research_ingest_arc_scoping_staged_plan_2026-07-07.md`)'s staged Tier 0-4 plan, whose Stage 0-2
(near-term, BGE-space, real-content-already-in-store) maps directly onto this drill's Tier 1, and
whose Stage 3 (encoder production-scale) maps onto Rank 2 of the weakness map; (2) the
multihop-composition-gap scoping (`research_multihop_composition_gap_closure_scoping_2026-07-07.md`),
whose two-cause hypothesis (branching-factor decode brittleness + representational semantic gap)
this drill's fresh on-disk smoke result partially tests — confirming cause (c) (branching, fixed
by beam) shows a promising early signal while cause (d) (semantic-seed) shows an unexpected,
undocumented-until-now BACKFIRE, a genuinely new finding this drill surfaces by reading the smoke's
metrics.json directly rather than assuming the scoping note's untested prediction held; (3) the
self-audit ladder threads (source-direct entailment, justification-retrieval scoping), which
supply the "inspectability" axis an LLM structurally cannot offer and which this drill folds into
Rank 3 of the weakness map rather than treating as a separate program; (4) the density-scale
theory reconciliation, whose m*(970K) prediction is the concrete falsifiable claim behind Rank 2.
The one genuinely NEW finding this drill contributes (not inherited from any prior note): reading
`exp_conceptnet_semantic_seeded_beam_composition_v1_smoke`'s per-arm breakdown directly off disk
(the scoping note that proposed this cell was written BEFORE the smoke ran, so no prior note has
synthesized this result) — the semantic-seeding cause backfires rather than helps, an outcome the
scoping note's own P_deflated=0.15-0.20 for full closure did not specifically anticipate (it
expected semantic-seeding to at least roughly track BGE-parity "almost by construction" — the
smoke's SEM_K1=0.216 is far below that expectation, a genuine surprise worth flagging up, not
smoothing over).

## Substrate-product implications

For Director: the practical next action is NOT "build the 970K QA benchmark" — it's the three
cheap, sequenced items in "Cheap decisive test" above, followed by the per-item logging fix
(Rank 4/Item 4 in the load-bearing path), in that order. The full Tier-2 harness (LLM baseline +
oracle-substitution ladder + dogfood-scale corpus) is real, valuable work, but building it before
the logging gap is closed would mean building an expensive instrument that still can't cleanly
decompose its own findings — the same trap the aggregate-only composition metrics fell into this
session (a HARD_FAIL verdict that would have obscured the beam-helps signal if this particular
cell hadn't happened to log 5 arms). The most consequential product-positioning point: the
self-audit/justification axis (Rank 3) is the one dimension an LLM baseline cannot be scored on at
all, no matter how the accuracy comparison lands — this is the durable, structural differentiator
the reframe's "not a scoreboard" framing is actually pointing at, and the benchmark should report
it prominently as its own axis rather than folding it into a single number.

## Citations (verified count)

**Internal (on-disk, freshly re-verified this cycle, not carried from memory):**
`data/exp_conceptnet_semantic_seeded_beam_composition_v1_smoke/metrics.json` (fresh, full per-arm
breakdown pulled directly — the load-bearing new finding this drill contributes);
`data/exp_n8_conceptnet_ingest_eval_canon_v1/metrics.json` (refuse-gate/setrecall numbers);
`data/exp_encoder_migration_step1b_v4_joint_reverify_relock_v1_seed{7,13}/metrics.json` (encoder
joint-solution verification, cited via the ingest-arc scoping note, cross-checked);
`data/orchestrator_status_log.jsonl` (2026-07-07T17:07:59Z per-item-logging-missing entry — the
single most consequential citation in this note); `notes/research_ingest_arc_scoping_staged_plan_2026-07-07.md`;
`notes/research_multihop_composition_gap_closure_scoping_2026-07-07.md`;
`notes/research_density_scale_theory_reconciliation_970k_2026-07-07.md`;
`notes/research_justification_retrieval_rung_scoping_unblocked_by_source_direct_2026-07-06.md`;
`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-07.md`.

**External (2 parallel Sonnet lit-scans this cycle, generic terms only, zero substrate-novel
mechanism names sent off-platform):**
RAGAS; ARES (arXiv:2311.09476); RGB (arXiv:2309.01431); CRAG (arXiv:2406.04744); Layer6 RAG
error-taxonomy (arXiv:2510.13975, github.com/layer6ai-labs/rag-error-classification); TrustNLP
2026 failure-mode taxonomy (aclanthology.org/2026.trustnlp-main.27); HotpotQA (Yang et al., EMNLP
2018); MetaQA (Zhang et al., AAAI 2018); ComplexWebQuestions (Talmor & Berant, NAACL 2018);
2WikiMultiHopQA (Ho et al., COLING 2020); Selective QA under Domain Shift (Kamath, Jia, Liang, ACL
2020); Roberts/Raffel/Shazeer closed-book QA (arXiv:2002.08910); Lewis et al. RAG (arXiv:2005.11401);
KILT (Petroni et al., arXiv:2009.02252); MuSiQue (Trivedi et al., arXiv:2108.00573); EmbedKGQA
(ACL 2020); SeedRG leakage-free benchmark generation (arXiv:2605.08838, the contamination-risk
finding motivating this drill's corpus recommendation); YuLan-Mini small-LLM baseline conventions
(arXiv:2412.17743); MDPI 16(9):744 CPU-only LLM inference feasibility.

**Flagged low-confidence / not independently cross-checked (per no-hallucinated-numbers
discipline, carried through honestly from the sub-agents' own flags rather than silently dropped):**
"Iterative RAG vs Ideal Evidence" (arXiv:2601.19827) and "RAG-X" (arXiv:2603.03541) — single-source
only, very recent, plausible but unverified against a second citation; "TRACe" as a named framework
— could NOT be confirmed real, likely conflated with TruLens's "RAG Triad," excluded from the
methodology recommendations above; a Pythia-family RAG-baseline citation — could not be found,
Qwen2.5/Llama-3.2 recommended instead on stronger citation support.

**Total: 24 distinct external sources found across 2 parallel lit-scans this cycle (3 explicitly
flagged low-confidence/unconfirmed and excluded from load-bearing claims), plus 9 internal
artifacts freshly re-read off-disk. Zero fabricated citations.**
