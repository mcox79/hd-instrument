# Test 0 -- empirical near-duplicate / lexical-collision density in the real 970K production KB

Date: 2026-07-07. Owner: research (Sonnet). Trigger: USER-directed Test-0 de-risk drill, CPU-only,
no GPU, no cell dispatch, read-only measurement against the COMMITTED KB. Follows the Test-0
definition named in `notes/research_encoder_970k_marchenko_pastur_codebook_collision_forecast_2026-07-07.md`
Item 5, extended per this drill's own tighter design (the source note called for a similarity-sampled
comparison; this drill instead measures the full population where cheap and stratifies by KB-source
category, which turned out to be the decisive axis -- see HEADLINE).

## HEADLINE

**The 970K file is NOT the ConceptNet-like corpus the prior forecast assumed -- it is a
heterogeneous dogfood ingest, and its near-duplicate risk is concentrated, structural, and
diagnosable, not diffuse.** On-disk verification (`manifest.json`, `wc -l`): `data/substrate_director_kb_v1/entities.jsonl`
= 970,069 rows exactly matches the target V the encoder forecast was written against, but its
`per_class` breakdown shows it is a union of true lexical/biological vocabulary (WordNet synsets,
GO terms, KEGG, FrameNet, VerbNet, NeuroLex) **and self-referential document-chunk fragments from
the project's own operational history** (13,359 `notes/` files and 3,024 `preregs/` files, chunked
into 134,026 + 19,747 = 153,773 rows, 15.86% of V) -- this is a materially different composition
than "today's ConceptNet-based 177,899" scaled up 5.5x, which is what the prior forecast's language
implied. **Exact-duplicate rate is low (0.66% of rows, n_distinct/V=0.9966) -- reassuring on its
own -- but exact-string dedup understates the real risk.** Two structural near-duplicate mechanisms,
both measured directly (not assumed): (1) 99.0-99.7% of note/prereg chunk rows have a same-document
sibling with measured char-4-gram Jaccard similarity averaging 0.96-0.97 (vs. 0.16-0.30 for random
cross-document pairs) -- i.e., consecutive chunks of the same source document are near-identical by
construction; (2) WordNet's 121,274 synset rows collapse to only 89,395 distinct surface-form
lemma roots (73.7% effective-distinct), because 39.6% of WordNet rows share a lemma with >=1 other
row (polysemous senses like `bank.n.01`/`bank.n.02` -- same surface form, different meaning, which
is exactly a lexical-collision risk for a name-keyed codebook even though semantically legitimate).
**Net effect on the discrete-algebra collision-count model: negligible.** Re-deriving the birthday
margin with the measured effective-distinct count (~771K-804K instead of raw 970,069) moves the
combinatorial margin from ~180.4 orders of magnitude to ~180.6 -- a change of 0.2 orders against an
astronomical margin. **The prior forecast's "combinatorial margin is not a close call" conclusion is
CONFIRMED, quantitatively, not just qualitatively -- GREEN.** But the prior forecast's characterization
of structured collision as "occasional... concentrated among disambiguation stubs / near-identical
geographic entries" is REVISED: the measured at-risk population is much more identifiable and
larger than that framing suggested -- **15.78% of V (153,114 rows) sit in tight, near-identical
document-chunk clusters (mean cluster size 8.6-10.1 rows) that are a direct artifact of the KB
ingest pipeline's chunking, not of "real world" entity duplication** -- **YELLOW, not RED**: real,
non-trivial, but narrow to two named, mechanically-understood, cheaply-dedupable sources
(chunking + WordNet polysemy), not diffuse across the corpus.

## Cheap decisive test

This measurement (near-dup density stratified by KB-source category, using exact chunk-cluster
grouping + WordNet lemma-collapse + char-4-gram-Jaccard blocking for the remaining categories) **was**
the cheap decisive test the prior forecast called for. It took ~15 seconds of streaming I/O plus a
few seconds of sampled Jaccard computation on a laptop CPU, no GPU, no training, no cell dispatch.
The one thing it could NOT test (out of this drill's scope): whether the encoder's actual K=128-block
codeword assignment is skewed for these identified near-dup clusters -- that requires running the
distillation MLP forward pass on the flagged cluster rows (CPU-feasible, no GPU needed, since it's
inference-only on an already-trained checkpoint) and is the natural next cheap step, not yet done here.

## Falsifiable predictions

**HARD-PASS (discrete-algebra channel, random-birthday component):** using the measured
effective-distinct count (771,036-803,689, see Item 2 below) instead of raw V=970,069 in the
`N^2/(2M)` birthday-collision formula with `M=32^128`, the combinatorial margin remains >=170 orders
of magnitude. **CONFIRMED this cycle** (measured: 180.55-180.58 orders, vs. 180.38 for raw V) --
this prediction is resolved, not merely forecast.

**HARD-FAIL (discrete-algebra channel, structured-collision component):** if a post-hoc stratified
re-check of `keyed@J5`/`shuffled_key` metrics (once available at scale, or re-sliced from any
existing 177,899-scale run that logs per-item results) shows the note/prereg chunk-derived subset
(15.86% of items) has a shuffled-key leak rate that is >2x the leak rate of the non-chunk subset,
that would CONFIRM this drill's structural-collision hypothesis is load-bearing (not just a
theoretical concern). **HARD-PASS** for that same check: chunk-subset leak rate within 1.5x of the
non-chunk subset's leak rate -- would mean the encoder is already robust to this specific structural
near-dup pattern, contrary to this drill's expectation. This is a NEW, concrete, falsifiable
follow-up test this drill contributes, not present in the prior forecast.

**HARD-FAIL (WordNet polysemy channel):** if per-item leak data ever becomes available and shows
polysemous-lemma rows (39.6% of the WordNet subset, 48,045 rows) have a keyed-retrieval confusion
rate (retrieving the wrong sense of the same surface form) meaningfully above chance among
same-lemma alternatives -- this would indicate the encoder is relying on surface form over context
for these rows, a genuine (if narrow, ~5% of V) lexical-leak-adjacent risk. **HARD-PASS**: confusion
rate at or near chance among same-lemma alternatives (i.e., correct sense is retrieved reliably from
context, not surface form).

**Calibration (per [[feedback-lit-scan-calibration-penalty]], applied to this drill's one genuinely
forward-looking claim -- whether the *structured* collision risk actually manifests in the
encoder's real codeword assignments, which this drill did not directly measure):**
- P(structured near-dup clusters produce measurable extra codeword collisions vs. a random-baseline
  control, when tested): undeflated ~0.55-0.65 (mechanistically plausible -- char-trigram-adjacent
  encoding of near-identical text should produce near-identical codes -- but untested) ->
  P_deflated ~0.35-0.45, capped at 0.50 per the novel-synthesis ceiling (no direct precedent for
  this specific KB's chunk-derived near-dup structure).
- P(the aggregate `keyed@J5`/`shuffled_key` HARD-PASS bars from the prior forecast still hold at
  970K, unchanged): **not deflated further by this drill** -- this drill's own quantitative
  recomputation (margin analysis above) is a closed-form derivation, not a literature-calibrated
  estimate, so the 0.60-0.65 P_deflated already assigned by the prior forecast stands, now with
  additional confirmatory evidence (the effective-distinct recompute) rather than being revised
  downward or upward.

## Cross-thread synthesis

Composes and extends, without re-deriving: (1) the Marchenko-Pastur/codebook-collision forecast's
Item 2 collision-count model and its named caveat about structured (non-random) collision -- this
drill supplies the actual measured structure the forecast could only speculate about, and the
speculation ("disambiguation stubs / near-identical geographic entries," borrowed from general
Wikidata-quality literature) turns out to be the WRONG mechanism for THIS specific KB -- the real
mechanism is ingest-pipeline document chunking plus WordNet's inherent polysemy enumeration, both
internal/structural rather than "real world" entity-quality issues; (2) the ingest-arc scoping
note's Item 1 gap (177,899 vs. 970,069 scale, CRLB not re-derived) -- this drill adds the fact that
those two numbers are not merely different SIZES of the same kind of corpus: 177,899 is
ConceptNet + math/science atoms (curated, external, `PartitionedStore.all_atoms()`-verified) while
970,069 is the full dogfood self-knowledge ingest (external KBs + the project's own notes/preregs/
memory/metrics) -- meaning the 970K scale-test is not purely "5.5x more of the same," it changes the
CHARACTER of a meaningful fraction (15.86%+ ) of the corpus; (3) the self-margin taxonomy's
collision-count family classification -- this drill's effective-distinct recompute is a direct,
concrete instantiation of that family's `p1 = n_distinct/V` formula, now measured (0.9966 naive,
0.79-0.83 effective) rather than assumed uniform.

## Substrate-product implications

For Director: (1) the discrete/algebra channel's HARD-PASS forecast at 970K is now on FIRMER
ground -- the combinatorial margin claim survives a real, on-disk recompute with the measured
effective-distinct count, not just the raw V assumption; no change to the recommended light-touch
confirmatory approach for that channel. (2) A concrete, near-zero-cost mitigation is now
actionable BEFORE the GPU scale-test: deduplicating near-identical sibling chunks in the note/prereg
categories (e.g., keep one representative chunk per source document, or merge highly-overlapping
consecutive chunks above a Jaccard threshold) would shrink the ingest corpus from 153,773 raw
chunk-rows to roughly 15,626 effective units (the number of distinct source documents) with
plausibly small information loss -- this alone reduces V by up to ~14% and removes the single
largest identified structural near-dup risk pool before it ever reaches the encoder. (3) The GSBC
density-dial retune (flagged by the prior forecast as the one Donoho-Tanner-class cliff risk) should
be tuned against an EFFECTIVE V of approximately 800,000-830,000 if a dedup pass is applied first,
or the raw 970,069 as a safe (slightly over-provisioned, not catastrophic) fallback if no dedup
pass is applied -- a concrete number to retune against, where none existed before. (4) The single
highest-value next action this drill identifies (cheaper than the >=400K GPU ladder test, still
CPU-only): re-slice any existing keyed@J5/shuffled_key per-item results (if logged) by chunk-vs-
non-chunk membership, to test this drill's new falsifiable prediction (chunk-subset leak rate vs.
non-chunk subset) before spending GPU budget on the full ladder.

## Honest bounds -- what this measurement can and cannot conclude

**Solid (measured, not inferred):** the KB's category composition (per manifest.json, cross-checked
against a fresh regex classification of all 970,069 rows); the exact-duplicate rate (0.66%, exact
computation over all rows via normalized-string hashing, no sampling); the note/prereg chunk
cluster-membership fractions (99.0-99.7% of chunk rows have >=1 sibling -- exact, computed over the
FULL population of chunk rows via doc-prefix grouping, not sampled); the within-doc vs. cross-doc
Jaccard comparison (sampled: 475-589 documents with >=2 sampled chunks per category, 2,509-3,241
within-doc pairs, compared against 1,000 cross-doc random-pair baselines per category); the WordNet
lemma-collapse ratio (121,274 rows, exact computation over the full WordNet subset, not sampled);
the birthday-margin recompute (closed-form, exact arithmetic, not an estimate).

**Approximate, sampled, and should NOT be over-read:** the blocked near-dup fractions for the
`natural_sentence_or_go_name`, `other_short`, `single_token`, `wordnet_synset` (Jaccard-blocking
cross-check), and `path_whole_doc` categories are computed on a capped sample (up to 4,000 items per
category, reservoir-sampled from the full stream) and use first-token blocking, which systematically
UNDER-counts near-duplicates that don't share a first token (e.g., reordered phrases, synonym
substitution) -- these numbers (6.95%-43.18% depending on category) should be read as lower bounds
on true near-dup density for those categories, not precise rates. The `path_whole_doc` category's
high flagged rate (43.18%) is the least examined of these -- this drill did not cluster those rows
by their underlying source-path template (e.g. `data/exp_<name>_v<N>/metrics.json`), so the
translation from "flagged fraction" to an effective-distinct count for that category (2.26% of V)
was deliberately NOT computed, to avoid overclaiming precision the sampling method does not support.

**Not measured at all (out of this drill's CPU-data-only scope, flagged as the natural next step):**
whether the encoder's actual trained codeword assignment is skewed for the identified near-dup
clusters -- this requires running the (already-trained) distillation MLP forward pass, which is
CPU-feasible (inference only, no GPU needed) but was not done in this drill, which was scoped
strictly to data-file measurement, not model inference. Also not measured: the referenced "gate-D
lexical-leak (~0.148, name-shortcut)" figure named in this drill's dispatch could NOT be located
anywhere in `notes/*.md` after a targeted search (`0.148`, `gate.?D`, `lexical.?leak`,
`name.?shortcut` all returned zero matches) -- this drill treats that figure as an unverified
pointer from the dispatching context, not a confirmed on-disk number, per filesystem-verify
discipline (do not propagate unverified figures).

## Citations (verified count: 0 external -- this was an internal filesystem measurement per Test 0's
own design, not a literature scan)

No external web search was performed this cycle; per the role contract, external queries are used
for literature scans, and this drill's task was an on-disk empirical measurement. The prior
forecast note (`notes/research_encoder_970k_marchenko_pastur_codebook_collision_forecast_2026-07-07.md`)
already carries 33 verified external citations for the theoretical framing this drill's numbers are
checked against (birthday-collision scaling, collision-entropy, entity-resolution blocking survey);
this drill reuses that framing without re-citing it.
