# Pre-reg: read_grow_knowledge_guided_bootstrap_v1

Date: 2026-07-17. Author: exp_dev (Agent Teams). Status: RAN INLINE to completion (glass-box, no
runtime LLM; ~10s full corpus). CLAIM-VET-pending (not self-declared chain-grade).

## Question (USER "build a foundation from almost nothing, like humans" test)
Prior read->grow cells used a FIXED extractor (same rules every pass, ZERO prior knowledge) and
plateaued at glass-box is-a edge precision ~0.325 strict (isa_growth v1) / ~0.41 honest
(multihop_genus_head v4) -- "the wall". The brain reads well BECAUSE it already knows things:
comprehension USES existing knowledge. Test the missing loop -- does using the GROWING foundation
to GUIDE extraction let RE-READING (Q1) and INTERLEAVING books (Q2) COMPOUND knowledge PAST the
fixed single-pass wall (Q3)?

## Mechanism (glass-box brain analog)
- FIXED arm  = v1 `ie_isa_extract` (Hearst COP + SUCH-AS) verbatim; single knowledge-free pass.
- GUIDED arm = SAME candidate generator + a SELF-BOOTSTRAPPED concept-class set C (a genus is a
  "recognized class" once asserted as genus for >= MIN_SUPPORT distinct terms in read text; 0
  curated seed). C drives a CONSISTENCY FILTER (keep an is-a edge only if its genus is a
  recognized class -- suppresses spurious copulas whose "genus" is an attribute/measure noun).
  Head RESELECTION kept only as a reported ABLATION.
- Re-read (Q1): CAUSAL pass (C-so-far, incomplete) vs FULL-C re-read (whole-book knowledge).
- Interleave (Q2): re-read book1 with book1-only C vs book1+book2 C.

## Design-gate (verified at smoke BEFORE conclusions; all GREEN)
- REAL baseline = FIXED v1 extractor, same gold+candidates. one_variable = consistency-filter ON/OFF.
- CAN-FAIL = HARD_FAIL_NO_LIFT if guided <= fixed (first-class null: curated/LLM foundation needed).
- difficulty_on = held-out sections' prose NEVER read; fixed edge-prec ~0.33 leaves ~0.67 headroom.
- no_leak = concept-class set C + guidance from READ prose only; held-out glossary genus unseen.
- discriminator_fires / arms_differ / baseline_in_band all True at full.

## Primary metric + bands (HYPOTHESIZED@this file -> MEASURED@data/exp_read_grow_knowledge_guided_bootstrap_v1/metrics.json)
PRIMARY = all-gold is-a EDGE precision (v1 basis, ~360-edge signal). Held-out-generalization
precision is SECONDARY (info-ceiling: coverage ~0.10 -> underpowered, flagged in metrics).
Verdict DECOMPOSES the three questions:
- AXIS A (Q3 beats-wall): guided_filter edge-prec - fixed >= 0.05 AND coverage_retain >= 0.5.
- AXIS B (Q1 re-read compounds): full-C re-read - causal >= 0.01.
- AXIS C (Q2 interleave compounds): book1+book2 - book1-only >= 0.01.
- HARD_FAIL_NO_LIFT if guided <= fixed. HARD_PASS if A AND B AND C. MIDDLE_BAND_BEATS_WALL_NO_COMPOUND
  if A but not (B AND C).

## Compute architecture
(b) sequential-CPU. Pure regex/POS/WordNet/dict; no matmul, no substrate vectors. Candidates
POS-extracted ONCE per section + cached; passes re-apply cheap dict filter. no_storage. CRLB n/a.

## Cell-template compliance
start_marker + crash_diagnostic; except SystemExit->raise before except Exception (no bare/Base);
final_metrics_atomicity=tmp_replace; deterministic (sorted(); no hash()/list(set()) seeding);
arms_differ_verified (fixed vs guided bit-differ, self-test + full); self-test exercises REAL
code path (build_candidate_cache/build_fixed/build_guided_full/edge_precision on tiny corpus).
Single unit, wall<15s -> chunk/heartbeat exempted.

## Result (MEASURED, full corpus, 107 sections, 793 gold / 170 held-out, 1246 candidates)
VERDICT = MIDDLE_BAND_BEATS_WALL_NO_COMPOUND.
- Q3 beats-wall YES: fixed 0.325 -> filter 0.390 (+0.065 @ 59% coverage). Frontier ms=2/3/5/10/20:
  0.388@70% / 0.390@59% / 0.375@40% / 0.529@19% / 0.441@9% (real precision-coverage frontier).
- Q1 within-book re-read NO: causal 0.395 -> full-C reread 0.390 (-0.005); class vocab saturates
  in ~one pass.
- Q2 interleave YES (small): book1_only 0.368 -> book1_after_book2 0.402 (+0.035; book2 adds 79 classes).
- ablation: head-reselection 0.329 (delta vs filter -0.060) -> filter-only is the mechanism.
Seed honesty: 0 curated facts; concept-class set entirely self-bootstrapped from reading (only
prior knowledge = NLTK POS tagger; WordNet lenient-EVAL only).
