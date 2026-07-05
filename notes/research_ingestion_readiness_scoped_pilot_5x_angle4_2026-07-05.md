# 5x-drill angle 4 of 5: should we ingest more info now? Machinery-readiness + scoped pilot spec

Date: 2026-07-05. Owner: research (Opus synthesis over substrate scour + 2 parallel Sonnet lit-scans:
hippocampal-cortical consolidation neuroscience; KB-ingestion-pilot + multi-hop-eval methodology).
Field-advisor run per discipline: top candidates (free-cumulants, Glauber dynamics, Wigner-edge) are
math/physics-thread material, not adjacent to this USER-directed ingestion question -- explicit
user-initiated angle (Trigger E) overrides the generic field-coverage heuristic this cycle.

## HEADLINE

**Machinery is PARTIAL, further along than the ground-truth anchor implies, and the highest-leverage
next move is NOT a new ingest -- it is verifying an ingest that already happened.** A real, non-synthetic
external KB (ConceptNet, 133,305 nodes / 179,781 edges) has been sitting in the canonical
`PartitionedStore` concept partition since 2026-06-19, committed, Store-load-verified. Separately, the
substrate's core mechanism -- multi-value Hebbian bind + 2-hop composition + fabrication-refusal over a
REAL external KB -- is already CHAIN_GRADE on FB15k-237 (50k triples, U1, CERT 583->584), proven 5000x-7410x
over random floors, not saturation-artifact. But neither of those has been shown to work THROUGH the live
operational query path (`Retriever.semantic()` / cortex / KG-walk) -- only through an isolated numpy
eval harness (U1) or a raw Store-load check (the ConceptNet ingest). This is the exact same gap the
encoder work already named and gated (step-0 integration-verify): offline/isolated proof != in-situ proof.
Applying that same discipline to KNOWLEDGE instead of the ENCODER gives a pilot that needs **zero new
ingest and zero re-encode** -- it only exercises content and code paths that already exist.

## Substrate scour: what "ingest machinery" actually contains today (verified on disk)

| Component | State | Evidence |
|---|---|---|
| Ingest-completeness cap (Space 1, char_trigram KB) | **FIXED** 07-03 | `config/director_kb_schema.json:76` `jsonl_max_lines_per_file: 200000` (was 5000); `director_kb.py` hard_cap 2000000 (was 50000) |
| Placeholder-label bug (Wikidata `name` field) | **FIXED** | commit `e28a4f474`; 4,991 rows backfilled |
| wikipedia-in-math-lane (~17 atoms) | OPEN, deferred, low-priority | not a retrieval-correctness blocker under qualified-id addressing per step-1 doc |
| Qualified-id / dup-id-collision fix (Space 2, the BGE/concept-vector store `Retriever.semantic()` actually reads) | **DESIGNED + PARTIALLY BUILT, NOT VERIFIED-WIRED** | root cause confirmed in code: `PartitionedStore.all_atoms()` flattens on bare local id -> same id can exist in >1 lane -> silent overwrite (measured 1500 submitted -> 1497 stored). Fix = 3-layer defense (qualified-id namespace + pre-write assert + `add_atoms_strict`), documented `notes/step1_reencode_migration_plan_...2026-07-04.md`. Cache files matching a "qualified_*" convention exist on disk (`qualified_bge_large_v2_name_177899.npz`, `..._177872_complete.npz`, built 07-04 21:35/22:19) -- BUT grep of the whole repo finds **zero .py files referencing that filename pattern**; the operational loader (`backend/substrate_index/retrieve_cache.py`) selects caches via a content-hash glob (`bge_large_*.npz`) keyed off `sha256(sorted(id_order))`, which is a DIFFERENT selection mechanism than the "qualified_*" files use. **Unverified whether the live Retriever is loading the collision-safe cache or the original one.** This is a live, concrete, checkable gap -- not a hypothesis. |
| Open relation vocabulary (relations as atoms, not enum; predicate-inclusive dedup) | **PRINCIPLE ADOPTED, partially enforced** | U1/N8's mechanism already treats relations as bound HD role-vectors (`key = E[s] * R[p] * sqrt(N)`), consistent with the design. Neocortical-analog CONSOLIDATION LOOP (auto-promote a new relation after N witnesses) explicitly **NOT YET BUILT**. Historical regression: the 5510-atom Wikidata ingest collapsed all triples to mono-typic `DEPENDS_ON` (closed-enum default-fallthrough bug); root-caused, but no confirmed clean re-ingest since. |
| Real external-KB reasoning mechanism | **PROVEN, isolated harness** | U1 (`exp_u1_fb15k237_ingest_eval_v1`, CHAIN_GRADE, CERT 583->584): set-recall 0.9896 (7410x over 0.0001 random floor, verified not by-construction), refuse-gate OOD/accept 0.974/0.958 (2.44x genuine signal separation, held-split calibrated), 2-hop 0.381 vs zero-by-construction 1-hop 0.0075 (5000x over random argmax). Real, structured, non-synthetic FB15k-237 (Freebase subset). Pure numpy/BLAS, zero LLM calls (audited). |
| Real external-KB content, physically ingested into the canonical live store | **DONE 06-19, verified, committed** | ConceptNet bounded-v1: +133,305 CONCEPT_NODE atoms + 179,781 edges into `data/substrate_index/concept/`; `PartitionedStore.all_atoms()` = 177,217 (independently re-verified, not trusting the cell's self-report); invariant_check TRUE-HARD-PASS; committed `e3b3147e`. Confirmed still present today: `grep -c CONCEPT_NODE concept/atoms.jsonl` = 133,305 (unchanged). 20,219 held-out edges firewalled for a future inference-transfer eval. |
| ConceptNet content reachable via the LIVE operational query path | **NEVER TESTED** | The full BGE index cache covering all 177,899 atoms (`bge_large_v2_name_177899_54f7cf6a.npz`) was only built 07-04 20:58 -- one day old. No cell has queried `Retriever.semantic()`/cortex/KG-walk against ConceptNet content and checked known-item recall. N8 (`exp_n8_conceptnet_ingest_eval_v1`), the natural sibling to U1 that would prove the mechanism generalizes off Freebase's opaque MIDs to readable ConceptNet strings (with a frozen-encoder semantic baseline, OPEN-C unlock), was **pre-registered 2026-06-22 and never dispatched or landed** -- a loose end sitting in `notes/n8_conceptnet_ingest_pre_reg_2026-06-22.md`, ready to run. |
| Curation-vs-volume prior | **Empirically settled, negative for bulk source-push** | TIER_4c assessment (06-16): the 5510-atom Wikidata bulk ingest went 84% stale and moved NO capability needle -- measured net-negative. Consumer-pull (atomize on-demand) beats source-push (bulk-dump) here. Any pilot must stay small/curated, not volume-chasing. |

**Net verdict on machinery readiness: PARTIAL.** The hard mechanism-level questions (can the substrate do
multi-hop reasoning + fabrication-refusal over a real external KB at all?) are answered YES, robustly. The
plumbing questions (is a real KB already-in-the-store actually reachable and correct through the path
cortex/M3 will use?) are UNVERIFIED, and the substrate's own bug history (5000-line cap, placeholder
labels, dup-id collisions, NULL-byte corruption -- four distinct addressability/integrity bugs found in
this exact pipeline in the last three weeks) is a strong base-rate argument that a fifth wrinkle is more
likely than not to be sitting in the unverified path. That argues for a targeted verify-first pilot, not
either "ingest nothing more" or "ingest broadly now."

## Cheap decisive test (spec, no new ingest, no re-encode, CPU-only)

**`exp_ingest_knowledge_integration_verify_v1`** (proposal only -- not dispatched, per task scope):

1. Draw N=200-300 known-fact probes from the ALREADY-INGESTED ConceptNet content (e.g. `dog IsA mammal`,
   `fire CapableOf burn` -- pick facts independently confirmable in `concept/atoms.jsonl`'s CN_* rows).
2. Query through the REAL production path -- `Retriever.semantic()` / `.hybrid()` (whichever cortex/M3
   actually calls) -- NOT a fresh numpy harness. Log which cache file gets resolved (settles the
   qualified-id-fix-wired question as a side effect).
3. Measure known-item recall@10 against the live index; assert `atoms reachable via query == atoms on
   disk` (the same completeness-assert discipline as the ingest-integrity principle).
4. Carve a bounded 2-hop subgraph around ~20-50 seed ConceptNet entities (MetaQA/CLUTRR-style: generate
   1-hop and 2-hop questions from the same seed set) and run the SAME 1-hop-vs-2-hop comparison U1/N8
   already pre-registered, but through the live query/reasoning path this time.
5. Compare against U1's isolated-harness numbers as the reference bar, not as an equivalence assumption.

**HARD-PASS:** live known-item recall@10 >= 0.80 on >=90% of the probe set AND live 2-hop composition
accuracy > live 1-hop baseline + 0.02 AND resolved cache shows zero collision loss (retrieved unique-atom
count == submitted qualified-id count). -> ConceptNet is genuinely live-addressable now; no re-ingest, no
re-encode, no new cell needed to start reasoning over real knowledge -- go straight to dispatching N8 (or
its live-path variant) for the full mechanism-level cert.

**HARD-FAIL:** live known-item recall@10 < 0.40 on the same probe set, OR resolved cache shows collision
loss (retrieved count < submitted count, reproducing the step-0 1500->1497 pattern at full 177k scale). ->
ConceptNet is on-disk but NOT live-addressable -- the qualified-id fix is unverified/unlanded in the
operational path and MUST be completed (and re-verified with this same probe) before any new-content
dogfood ingest, exactly as the 07-04 ordered plan's step-1 gate already requires.

**MIDDLE-BAND:** recall@10 in [0.40, 0.80) or 2-hop only weakly clears baseline -- diagnose which stage is
lossy (raw-atom-presence vs vector-index-inclusion vs retrieval-ranking) before deciding whether to patch
or re-run the cache rebuild.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):** P(HARD-PASS on first try) estimated
0.55-0.65 undeflated (strong mechanism prior from U1 + content already ingested + full cache already
rebuilt post-ingest) -> **P_deflated = 0.35-0.40**, not from a generic lit-scan discount but from this
system's own measured bug-density: four independent addressability/integrity bugs (5000-line cap,
placeholder labels, dup-id collision, NULL-byte partial-write corruption) have each been found in this
exact ingest/query pipeline within the last three weeks. A base-rate argument, not pessimism-for-its-own-sake.

## Falsifiable predictions

- **HARD-PASS path unlocks:** dispatch N8 (already pre-registered, zero design cost) as the mechanism-level
  cert on ConceptNet's readable-entity variant of U1, PLUS confirms the live query path is the SAME
  addressable space -- meaning any future dogfood-ingest (step 2 of the 07-04 ordered plan) can proceed on
  schedule without waiting for the sparse-code re-encode fork to resolve.
- **HARD-FAIL path forces:** land the qualified-id fix in `retrieve_cache.py`'s cache-selection path (make
  it find/prefer the collision-safe cache, or rebuild the content-hash-named cache FROM the qualified-id
  list rather than `all_atoms()`), re-run this same probe as the acceptance gate -- this is a small, scoped,
  Testbed/Exp-Dev fix, not a research question.
- **Either way, this closes within one cheap CPU cell** -- it does not touch the encoder fork, the sparse
  concept-code migration, or any GPU dispatch.

## What to ingest + how (scoped pilot spec, ranked)

**Tier 0 (do first, ~free): the verify-first pilot above.** Not a new ingest. Turns "unknown" into
"known" on content and mechanism that already exist. No re-encode, no new corpus, no dispatch cost beyond
one small CPU cell.

**Tier 1 (next, cheap, reuses existing design): dispatch N8 as pre-registered.** ConceptNet en-100k
(readable entities, 8 relation types, frozen-encoder MiniLM-L6 baseline for the OPEN-C semantic-vs-composition
check U1 deferred). Pre-registered bands already locked (`notes/n8_conceptnet_ingest_pre_reg_2026-06-22.md`):
set-recall>=0.95, refuse-gate>=0.80/0.80, substrate_2hop > 1-hop+0.02, substrate_2hop >= 2.0x frozen-encoder.
Smoke already ran clean (HARD_PASS at M=5k). This is a decision for exp_dev/USER, not a new design task --
the cell and pre-reg already exist, unused for two weeks.

**Tier 2 (if USER wants genuinely NEW content, not just verification of what's there): the dogfood-ingest
pilot** already speced in `notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md`
step 2 -- 50-200 of our own research/notes, chunked -> concept+relation atoms -> encoded with the CURRENTLY
OPERATIONAL encoder (BGE, Space 2 -- NOT the pending sparse concept code, so it lands in the SAME space as
everything else and never needs a re-encode or risks a mixed-encoder store) -> predicate-inclusive dedup ->
A5-gated write. Known-item retrieval probe (query a concept you KNOW is in note X, confirm rank-1) before
scaling. This matches the field's own convention for pilot scale (FB15k-237's ~14.5k/310k and iText2KG's
5-15-document pilots are the standard "shake out the pipeline" scale; ATOMIC-2020's own authors validated on
a 5k sample regardless of the full KB's 1.33M size) -- a 50-200-note pilot is comfortably within that norm.

**Explicitly does NOT need the full re-encode:** both Tier 0/1 (ConceptNet, already in Space 2) and Tier 2
(new content, encoded with the CURRENT operational encoder into the SAME Space 2) sidestep the sparse-code
migration entirely. The mixed-encoder-store collapse risk (measured: cross-retrieval ~1%) only applies if
NEW content is encoded with a DIFFERENT encoder than what's already in the store -- avoided here by
construction, not by timing luck.

## Cross-thread synthesis: brain mechanism + does this unlock the glass-box-LLM frontier?

**Brain mechanism (Complementary Learning Systems, hippocampal fast-encode -> cortical slow-consolidate;
2 parallel lit-scans, generic terms, calibration-penalized):**

- Dentate gyrus performs pattern separation on incoming input; CA3 supports one-shot autoassociative binding
  of arbitrary (role, filler) pairs via a newly-characterized fast synaptic mechanism (Behavioral Timescale
  Synaptic Plasticity, Bittner et al. 2017 / Fan et al. 2023), gated by a novelty/prediction-error signal
  (preferentially engaged in novel contexts, Priestley et al. 2022). This is the "ingest a new fact
  one-shot, isolated, sparse" half -- directly analogous to the substrate's A5-gated single-atom write into
  a pattern-separated (qualified-id-addressed) store.
- Systems consolidation happens offline (slow-wave-sleep ripple-spindle-slow-oscillation coupling,
  Klinzing/Niethard/Born 2019) via **interleaved** replay -- new material is woven into old cortical
  structure on a specific temporal schedule (novel content preferentially replayed at slow-oscillation
  transition points, familiar content dominates the stable middle; Golden et al. 2025 preprint), which is
  the mechanistic solution to catastrophic interference. Interleaving-with-old-material, not raw repetition
  count, is what the evidence credits.
- **Load-bearing for THIS question:** Tse et al. (2007, *Science*) shows a schema takes real, non-trivial
  up-front cost to build (6 paired-associates, ~1 month of repeated training in their paradigm) -- but ONCE
  a schema exists, a brand-new SCHEMA-CONSISTENT item integrates in a single trial and becomes
  hippocampus-independent within 24-48 hours (a lesion at 3h post-learning impairs recall; a lesion at 24h
  does not). Schema-INCONSISTENT items still require the full slow route. This is a genuine, causally-tested
  (lesion-based) asymmetry, not a loose analogy: **build/verify a small curated pilot first (the schema),
  confirm it generalizes, THEN allow faster integration of consistent new content** is exactly what the
  brain does, mechanistically, not merely a convenient engineering staging.
- Hippocampal indexing theory (Teyler & DiScenna 1986; updated 2007, 2020): the hippocampus stores a compact
  POINTER/index to a distributed cortical trace, not the content itself. This directly parallels (and is
  already, by accident, the substrate's architecture): qualified-ids in `PartitionedStore` are the
  pointer/index layer; the BGE npz cache is the distributed content-retrieval layer. A published direct
  translation of this exact analogy exists (HippoRAG, arXiv:2405.14831: KG=hippocampal index,
  dense/parametric store=cortical content, PageRank-style spreading activation=pattern completion) --
  useful validation that the substrate's separation-of-pointer-from-content design is a coherent, precedented
  direction, not a novel risk.
- Calibration: the qualitative two-timescale + schema-gated-fast-path picture is strongly-replicated
  consensus (McClelland/McNaughton/O'Reilly 1995 remains a foundational, heavily-cited framework; Tse et
  al.'s lesion-timing result is causal but from one lab's paradigm, narrower evidence base than the core CLS
  claims). The exact quantitative thresholds (item counts, timescales) are soft -- treat as order-of-magnitude
  intuition (hours-vs-weeks; single-digit curated items vs. dozens), not precise parameters. Whether the
  hippocampus alone can do RAPID statistical learning (Kumaran & McClelland 2012's challenge to the 1995
  model) remains actively contested.

**Does this unlock the glass-box-LLM frontier -- and is it before or after the integration test?**

Angle-3's integration-design drill (delivered today, `notes/research_integration_end_to_end_substrate_loop_2026-07-05.md`)
found: encoder->store CLEAN (smoke-verified), store->reasoning CLEAN (CHAIN_GRADE, reasoning runs directly
over real stored atoms), reasoning->generation THE ONE OPEN SEAM (untested cross-algebra bridge; both brain
and VSA literature say naive/fixed bridges lose real fidelity -- up to 16.2 points measured in a directly
analogous published system -- while co-trained bridges do not).

The knowledge-ingestion pilot proposed here (Tier 0/1) only exercises the TWO ALREADY-PROVEN-CLEAN seams
(encoder->store, store->reasoning). It does NOT require the reasoning->generation bridge, because its
decisive test stops at "retrieve the right fact and compose 2 hops of it" -- it does not require the
substrate to SPEAK the answer. **This means the knowledge-verification pilot does not need to wait for the
integration test to close, and vice versa -- they are two independent prerequisites, not a strict
before/after ordering.** Both are cheap, CPU-only, reuse-existing-primitives cells that can run in the same
cycle without either blocking the other. The FULL "glass-box LLM" claim -- ingest real knowledge, store it,
reason over it, and SAY the answer -- needs BOTH to close: this pilot proves reasoning-over-real-ingested-
knowledge works through the live path; angle 3's arm-A/B/C test proves the reasoning-output can be spoken.
Neither alone completes the loop, and there is no dependency forcing one before the other -- run both.

## Substrate-product implications

Not "should we ingest more" in the abstract -- the substrate already HAS more real, non-synthetic knowledge
than the "knows almost nothing" framing suggests (133k ConceptNet nodes, committed, Store-verified); the gap
is specifically LIVE-PATH ADDRESSABILITY, which is a verification task, not an ingestion task. This
reframes the angle-4 question: the right next action is cheaper than "ingest more" implies, and the answer
to "is now the time" is **yes for verification, not yet for new bulk content** -- consistent with the
TIER_4c curation-over-volume precedent and the CLS schema-first-then-fast-path brain mechanism. If the
verify-first pilot HARD-PASSes, N8 and the dogfood-ingest pilot become low-risk, same-week follow-ons. If it
HARD-FAILs, the fix is a small, already-scoped Testbed/Exp-Dev task (wire the qualified-id cache into
`retrieve_cache.py`'s selection path), not a research-track blocker.

## Citations (verified count: 53 distinct sources across 2 independent Sonnet WebSearch lit-scans;
not independently cross-checked against primary text -- lit-scan tier, calibration penalty applied)

Neuro/CLS scan (28 sources): McClelland, McNaughton & O'Reilly 1995 *Psychol. Rev.*; PMC2829853; PMC3812781;
Bittner et al. 2017; Fan et al. 2023; Priestley et al. 2022; PMC11519319; *Nat. Commun.* 2020 (mnemonic
prediction errors); PNAS 2021/2022 follow-ups; *Nat. Commun.* 2022 (hippocampal reps switch errors->predictions);
Klinzing/Niethard/Born 2019 *Nat. Neurosci.*; 2023 *Neuron* review; Golden/Saxena/Gonzalez/Delanois/Kilianski/
McNaughton/Bazhenov 2025 bioRxiv preprint; PMC9755223; Tse et al. 2007 *Science* 316:76-82; Tse et al. 2011
*Science*; van Kesteren et al. 2012 *TiCS*; Gilboa & Marlatte 2017 *TiCS*; Sharon/Moscovitch/Gilboa 2011 PNAS;
PMC4244253; PMC4556537; PMC4519547; PMC6711760; Kumaran & McClelland 2012; Teyler & DiScenna 1986; Teyler &
Rudy 2007; PMC7486247; HippoRAG arXiv:2405.14831.

KB-pilot/multi-hop-eval scan (25 sources): Toutanova & Chen 2015 (FB15k-237); Dettmers et al. 2018 (WN18RR);
Zhang et al. AAAI 2018 (MetaQA); Speer/Chin/Havasi AAAI 2017 (ConceptNet 5.5); Hwang et al. AAAI 2021
(ATOMIC-2020); Vashishth et al. WWW 2018 (CESI); Gupta/Kenkre/Talukdar EMNLP 2019 (CaRe); Lairgi et al. 2024
(iText2KG, arXiv:2409.03284); Broscheit et al. EMNLP 2020 (OLPBench); Cranfield/TREC known-item-search
paradigm; ANN-Benchmark/VectorDBBench; MDPI 2024 KG-construction survey; Grüninger & Fox competency
questions; GraphMERT arXiv:2510.09580; Gashteovski et al. EMNLP Findings 2021 (BenchIE); Cai/Liang et al.
NeurIPS 2022 (OWA evaluation, arXiv:2209.08858); Yih et al. ACL 2016 (WebQSP); Sun et al. EMNLP 2018
(GraftNet); Yang et al. EMNLP 2018 (HotpotQA); Sinha/Sodhani/Dong/Pineau/Hamilton EMNLP 2019 (CLUTRR); Lao &
Cohen 2010 / Lao/Mitchell/Cohen EMNLP 2011 (PRA); Xiong et al. EMNLP 2017 (DeepPath); Das et al. ICLR 2018
(MINERVA); Akrami et al. ACL 2020; arXiv:2601.09069 (2026 review, symbolic-to-NL relations).

## Prior internal cells / notes flagged (substrate scour, not re-derived)

- `exp_u1_fb15k237_ingest_eval_v1` (CHAIN_GRADE, CERT 583->584) -- mechanism proof, isolated harness.
- `exp_n8_conceptnet_ingest_eval_v1` -- pre-registered 2026-06-22, never dispatched (loose end, cheap to close).
- `orchestrator_to_all_CONCEPTNET_ingest_DONE_...2026-06-19.md` -- real KB physically in canonical store.
- `notes/step1_reencode_migration_plan_bct_safe_unique_id_addressability_gates_2026-07-04.md` -- qualified-id
  fix design + inventory (this note extends it: cache exists, wiring unverified).
- `notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md` -- the ordered
  plan this note narrows (Tier 0/1 shows a slice of "step 2" doesn't need to wait on "step 1").
- `notes/research_integration_end_to_end_substrate_loop_2026-07-05.md` -- angle-3 finding this note
  cross-references for the generation-seam dependency analysis.
- `skunkworks_to_research_TIER_4c_ASSESSMENT_...2026-06-16.md` -- curation-over-volume precedent (5510-atom
  Wikidata 84%-stale failure).
