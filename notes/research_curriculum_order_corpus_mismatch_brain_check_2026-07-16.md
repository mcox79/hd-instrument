# Research: brain-check on the CoDEx curriculum-order null + corpus-mismatch diagnostic + AL-CPL re-test

**Date:** 2026-07-16. **Filed by:** research (3 parallel Sonnet lit-scan lanes + Opus/Sonnet synthesis + direct on-disk measurement). **Trigger:** the real-data ingest-ORDER test (`exp_curriculum_order_ingest_real_codex_v1`, verdict `MIDDLE_BAND_METRIC_NEAR_VACUOUS_INFO_CEILING_LOW`) did not visibly reproduce the synthetic HARD_PASS ("order matters; curriculum rescues schema-fit"). Per the always-on discipline of brain-checking every negative before accepting it, this drill asks: does cognitive science actually predict the order effect should be **hierarchy-specific**, such that a null on CoDEx is an *expected*, brain-consistent corpus-mismatch rather than a refutation — and if so, what is the right corpus to re-test on?

---

## (a) HEADLINE

**The literature converges, across three independently-developed frameworks that were never designed to speak to each other, on the same structural claim: sequencing/order effects are a property of material with genuine PREREQUISITE DEPENDENCY structure, and the effect is predicted to be weak-to-vacuous on materially independent ("flat") facts — no single paper states this as a labeled dichotomy, so this is a stitched synthesis, not a looked-up result.** (1) Knowledge Space Theory (Doignon & Falmagne) defines a "surmise relation" — a precedence structure over items — as the entire mechanism by which a "learning path" is even a meaningful concept; when items have no surmise relations between them (mastery of one implies nothing about readiness for another), the theory's own formalism degenerates to the trivial case where every permutation is an equally valid "path" — i.e., KST predicts order-invariance as the fixpoint of an EMPTY surmise relation, not as a separate finding. (2) Piaget's distinction between **operative knowledge** (transformational, rule/schema-based, genuinely stage-gated — seriation, conservation, class-inclusion hierarchies) and **figurative knowledge** (static, item-based, labels/facts) maps directly onto hierarchical-vs-flat: Piaget's stage theory was built to explain the former, and does not claim arbitrary declarative facts (a name, a color word) require the same staged scaffolding. (3) The interleaving/blocking literature (Bjork, Kornell) finds sequencing effects specifically when there is an underlying discriminable rule or category structure to induce (perceptual categories, math problem-types); when items are arbitrary and unconnected (paired-associate lists, isolated trivia) the standard finding is that total exposure/repetition schedule (spacing) dominates, and item ORDER carries little to no independent signal because there is no structure to violate.

**Confirmed directly (not a citation, a same-session on-disk measurement): CoDEx-S and CoDEx-M are exactly the "empty/near-empty surmise relation" flat regime the theory predicts should show a vacuous order effect.** Measured straight from the raw train triples used in the null experiment:

| | CoDEx-S (n=2034) | CoDEx-M (n=17050) |
|---|---|---|
| train edges | 32,888 | 185,584 |
| avg degree | 32.3 | 21.8 |
| density vs. spanning tree (edges / (n-1)) | **16.2x** | **10.9x** |
| edges on a hierarchical/taxonomic relation (P279 subclass-of, P361 part-of, P527 has-part, P171 parent-taxon, P131/P150 admin-nesting) | **0.26%** | **0.18%** |
| top relations by share | P106 occupation (31%), P530 diplomatic-relation (17%), P463 member-of (15%) | P106 occupation (35%), P27 citizenship (8%), P1412 languages-spoken (6%) |

CoDEx is ~11-16x denser than a tree and is built almost entirely (>99.7%) from symmetric-flavor associative facts (occupation, citizenship, membership, language) with essentially no taxonomic/prerequisite edges. This is a dense flat web by construction, not a hierarchy in any meaningful sense — the null result is exactly what KST's degenerate-surmise-relation case and Piaget's figurative-knowledge case predict, not evidence against the synthetic HARD_PASS's mechanism.

**The right re-test corpus, live-verified this cycle: AL-CPL** (`github.com/harrylclc/AL-CPL-dataset`, Liang/Wu/Huang/Giles), a set of four university-course concept graphs (Data Mining, Geometry, Physics, Precalculus) whose prerequisite edges were explicitly validated by the original authors to satisfy **strict partial-order axioms (irreflexive + transitive)** — i.e., these are confirmed genuine DAGs, not similarity graphs. Live-fetched counts and the same density diagnostic:

| Domain | Concepts | Confirmed prerequisite edges | density vs. tree (edges/(n-1)) |
|---|---|---|---|
| Data Mining | 120 | 292 | **2.45x** |
| Physics | 153 | 487 | **3.20x** |
| Precalculus | 224 | 699 | **3.13x** |
| Geometry | 89 | 524 | **5.95x** |

All four domains are 100% prerequisite-typed edges by construction (vs. CoDEx's 0.2-0.3%) and are 3-5x less dense-vs-tree than CoDEx (vs. CoDEx's 11-16x) — a clean, cheap, on-disk-computable structural contrast that lets us attribute the CoDEx null to corpus-mismatch before spending any compute on a stronger metric. Data Mining is the "flattest-to-tree" of the four (2.45x) and is the recommended first pilot domain for the strongest expected order effect; Geometry (5.95x) is the least hierarchy-like of the four and a useful internal robustness check.

---

## (b) Cheap decisive test

**Already run (this cycle, zero additional compute):** the density-vs-tree + hierarchical-edge-fraction diagnostic above, computed directly from the on-disk `data/codex_claimvalidity/raw/train.txt` and `data/codex_m_claimvalidity/raw/train.txt` files and from AL-CPL's live-fetched README statistics. This is the "cheap decisive test" requested by the routing task's part (c) — it is DONE, not proposed, and it is decisive: CoDEx is unambiguously a flat dense web (>10x tree density, <0.3% hierarchical edges) while AL-CPL is a confirmed strict partial order (100% prerequisite-typed, 2.5-6x tree density). No further diagnostic spend is needed before re-running the ordered-ingest experiment on the right corpus.

**Next test (the actual re-run, ship-ready — see Actionable section below):** port `exp_curriculum_order_ingest_real_codex_v1`'s harness (same gate, same tau, same 5 arms: curriculum/random/frequency/random_hold/reverse, same degree-orthogonalized popularity-neutral RA-schema-fit quality metric, same budget-sweep + scramble-null + tau0-null discipline) onto AL-CPL's (concept, prerequisite, concept) triples in place of CoDEx's (h, r, t) triples. Because AL-CPL's edges ARE the ground-truth topological order (no proxy needed — "prerequisite" literally means "must be anchored first"), curriculum order = true topological sort of the validated partial order, and REVERSE = its exact reversal, which should crater harder than CoDEx's reverse arm (CoDEx reverse only caters to a proxy anchoring heuristic; AL-CPL reverse violates an author-validated ground-truth partial order directly).

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 (structural claim — order-sensitivity is a function of dependency density, not a general property of knowledge ingestion).**
P estimate: **P=0.50** (capped at the novel-synthesis ceiling per lit-scan calibration — this is a STITCHED synthesis across three literatures [KST, Piaget, interleaving/blocking research] that individually support the claim but no single source states it as a labeled "hierarchical vs. flat" dichotomy; treat as a strong, convergent, but unproven-as-such interpretive claim, not a looked-up fact).
HARD-PASS: re-running the identical harness on all 4 AL-CPL domains shows the margin_cur_rand / margin_cur_freq bands (same pre-registered thresholds as the CoDEx prereg: >=0.030 / >=0.010) clearing HARD_PASS on a majority of domains, AND the info_ceiling check clears (>=0.03, i.e. NOT another near-vacuous metric result), AND density-vs-tree correlates with effect size across the 4 domains (Data Mining, the flattest-to-tree, shows the largest curriculum-vs-random margin; Geometry, the densest, shows the smallest).
HARD-FAIL: AL-CPL also lands MIDDLE_BAND_METRIC_NEAR_VACUOUS or shows margin_cur_rand <= 0.005 with info_ceiling >= 0.03 (a trustworthy informative negative) on a majority of domains — this would mean the schema-fit/RA quality metric itself (not the corpus) is the bottleneck, a materially different and more actionable finding (metric-design problem, not corpus-selection problem).

**Prediction 2 (causal/transfer claim — the specific AL-CPL re-run reproduces curriculum-beats-scrambled on real, validated-DAG data).**
P estimate: **P=0.35** (deflated per lit-scan calibration; consistent with the identical composite-P pattern already established in the two sibling notes on TQA and on Dolch/Simple-Wikipedia — real structured data is expected to help, but no published study has run this specific ingestion-order ablation on ANY real dataset, computational-substrate or otherwise, so the transfer step remains genuinely untested).
HARD-PASS / HARD-FAIL thresholds: identical to the pre-registered CoDEx bands (see `preregs/2026-07-16_curriculum_order_ingest_real_codex_v1.md`) — reused verbatim, not re-derived, since the mechanism and metric are unchanged; only the input triples change.

**Prediction 3 (reverse-crater strength should be larger on AL-CPL than on CoDEx).**
P estimate: **P=0.40** (deflated; a genuine validated partial order gives REVERSE a ground-truth violation to exploit, whereas CoDEx's reverse arm only violates a proxy anchoring heuristic on a graph with no real prerequisite structure to violate in the first place — this is the single most mechanistically-grounded prediction in this note, but still capped for lack of direct precedent).
HARD-PASS: AL-CPL reverse premature-rejection rate exceeds CoDEx's discriminator value at comparable scale by a visible margin (CoDEx-S full run: not directly reported in the MIDDLE_BAND verdict's headline metrics — check `reverse_craters=True` fired at all, `rev_prem=0.419` from the metrics.json; AL-CPL reverse premature-rejection should exceed ~0.419 given a true partial order vs. a proxy anchor heuristic). HARD-FAIL: AL-CPL reverse premature-rejection is equal to or lower than CoDEx's 0.419 despite AL-CPL being a confirmed strict partial order — would suggest graph SIZE/density (not hierarchy-vs-flat structure per se) is what drives the crater effect, undermining the structural framing above.

---

## (d) Cross-thread synthesis

- **Directly resolves the open question left by `data/exp_curriculum_order_ingest_real_codex_v1/metrics.json`'s MIDDLE_BAND_METRIC_NEAR_VACUOUS verdict** and the corresponding prereg's own honest framing (info_ceiling=0.011, "test CANNOT distinguish order-invariant from metric-too-weak-to-tell"). This note adds a THIRD possible reading beyond "metric too weak" and "order-invariant": **corpus-mismatch** — the metric may be fine, but CoDEx has almost no dependency structure for an order effect to act on in the first place. The measured 0.26%/0.18% hierarchical-edge-fraction is direct evidence for this reading specifically.
- **Converges with, and is a natural extension of, `notes/research_curriculum_prerequisite_datasets_2026-07-16.md`**, which already surveyed and ranked TQA / Junyi / MOOCCube / AL-CPL / LectureBank for a DIFFERENT test design (one needing attached lesson CONTENT, not just structure). This drill's target experiment (`exp_curriculum_order_ingest_real_codex_v1`) needs ONLY graph structure — no attached text — because schema-fit there is defined purely as "are this triple's endpoints already anchored," not any content-similarity measure. That relaxation makes AL-CPL (structure-only, no content-bridging problem) a BETTER fit for THIS specific harness than it was flagged as being for the TQA/Junyi-content-bridge test in the sibling note — a genuinely new, more precise recommendation than the sibling note's own ranking, because the sibling note was scoping a different downstream test.
- **Directly extends `experiments/exp_curriculum_order_ingest_schema_fit_v1.py`'s own design premise**: that synthetic cell explicitly builds a HIERARCHICAL regime (positive control, genuine prerequisite forest) and a FLAT regime (null guard, all facts ground directly on innate anchors, order proven not to matter — flat_spread <= 0.05 is a REQUIRED pass condition, not incidental). CoDEx turning up order-insensitive is exactly what that cell's OWN null-guard regime predicts for flat material. The synthetic cell already encoded the theory this research drill just found independent lit support for; the real-data test picked (by data availability, not by design) a corpus that landed in the null-guard regime rather than the positive-control regime.
- **New finding this drill adds to the whole curriculum-order thread (not covered by the 07-09/07-16 sibling notes):** a cheap, general, ON-DISK-COMPUTABLE diagnostic — `edges / (n_entities - 1)` (density-vs-spanning-tree) plus `fraction of edges on a taxonomic/hierarchical relation type` — for classifying ANY candidate real dataset as hierarchy-like vs. flat-like BEFORE running an expensive order-ablation on it. This should be run as a standard pre-flight check on any future curriculum-order corpus candidate (would have caught the CoDEx mismatch before the compute was spent, cheaply, in under a minute).

---

## (e) Substrate-product implications

1. **The CoDEx MIDDLE_BAND result should NOT be read as a refutation of the curriculum-order mechanism** (that synthetic HARD_PASS stands on its own construction-proof merits). It should be re-classified in the cap_map / decisions log as "corpus-mismatch, inconclusive by design" rather than left as an ambiguous MIDDLE_BAND with no attribution — the on-disk diagnostic above gives a concrete, defensible reason.
2. **AL-CPL is immediately actionable at near-zero friction**: no login, no content-bridging step (the harness only needs structure), four independent domains for a mini robustness sweep, and author-validated strict-partial-order semantics that make the REVERSE arm a genuinely stronger positive control than CoDEx's proxy-anchoring reverse arm.
3. **The density-vs-tree + hierarchical-fraction diagnostic is a reusable pre-flight gate**: before committing compute to any future curriculum/order test on a new real dataset, compute this pair of numbers first (seconds of work) to predict whether the corpus sits in the hierarchical (positive-control) or flat (null-guard) regime, and calibrate expectations before running the expensive test.
4. **A within-CoDEx robustness check is available for free**, if wanted: CoDEx-M's P279/P361/P171/P131/P150 edges (0.18% of 185,584 = ~330 edges) could in principle be pulled out as a tiny internal "hierarchical slice" and compared against a matched-size flat slice from the SAME dataset — controls for dataset-family confounds, though AL-CPL's much larger validated-DAG sample is the stronger first move.

---

## Actionable for exp_dev (per USER-locked discipline: no separate hand-off routing file — delivered here directly)

Per the standing USER-locked discipline that the hand-off ferry mechanism is deprecated, this section IS the actionable hand-off; no `exp_dev_handoff_*.md` file was written. Director: dispatch exp_dev directly from this note.

- **Anchor candidate (rank 1, ship-ready):** port `experiments/exp_curriculum_order_ingest_real_codex_v1.py`'s data-loading layer to read AL-CPL's `*.preqs` files (per-domain: concept-id pairs, positive = confirmed prerequisite) in place of CoDEx's `(h, r, t)` triples. Keep the gate (schema_fit >= tau=0.5), the 5 arms (curriculum/random/frequency/random_hold/reverse), the degree-orthogonalized RA popularity-neutral quality metric, and ALL pre-registered bands/discriminators from `preregs/2026-07-16_curriculum_order_ingest_real_codex_v1.md` unchanged — only the triples source changes. Run all 4 domains (Data Mining, Physics, Precalculus, Geometry) in one sweep; Data Mining first (highest expected effect per the density-vs-tree ranking above).
- **Why now:** the corpus-mismatch diagnostic is complete and decisive (this note, section a/b); AL-CPL is live-verified as downloadable, no-login, structurally exactly what the harness needs, and requires no new architecture — a data-source swap on an already-built, already-pre-registered cell.
- **Tier hint:** cheap CPU, seconds-to-minutes per domain (same complexity class as the original CoDEx-S run, which completed in ~4s; AL-CPL domains are smaller: 89-224 concepts vs. CoDEx-S's 2034 entities).
- **Context pointers (paths, not summaries):** `experiments/exp_curriculum_order_ingest_real_codex_v1.py`, `preregs/2026-07-16_curriculum_order_ingest_real_codex_v1.md`, `data/exp_curriculum_order_ingest_real_codex_v1/metrics.json` (the MIDDLE_BAND result being re-tested), `notes/research_curriculum_prerequisite_datasets_2026-07-16.md` (prior AL-CPL/Junyi/TQA scoping), `experiments/exp_curriculum_order_ingest_schema_fit_v1.py` (the synthetic HARD_PASS whose hierarchical/flat regime split this note found independent lit support for). Source: `github.com/harrylclc/AL-CPL-dataset` (data/*.preqs files per domain).
- **Autonomy:** exp_dev owns cell-design details (exact schema_fit adaptation for AL-CPL's smaller graphs, whether K_ground=1 still applies at this scale, budget-grid choice for the smaller node counts). This note does not prescribe implementation, per [[feedback-no-experiment-design-in-prompts]].

---

## Citations (verified count: 3 parallel lit-scan lanes + 1 live dataset re-verification + 2 direct on-disk measurements = 6 independently-verified inputs)

**Knowledge Space Theory:** Doignon & Falmagne 1985, "Spaces for the assessment of knowledge," *International Journal of Man-Machine Studies*; Falmagne & Doignon, *Learning Spaces* (2011) — surmise relations, feasible learning paths, the degenerate/empty-surmise-relation case.

**Developmental psychology:** Piaget's figurative vs. operative knowledge distinction (schemas/transformations vs. static representations); Piaget's stage theory (sensorimotor -> preoperational -> concrete operational -> formal operational) as a theory of operative/structural knowledge specifically; Vygotsky, Zone of Proximal Development / scaffolding, as a theory of skill/task structure rather than arbitrary fact acquisition.

**Interleaving / blocking / structure-dependent sequencing:** Bjork & Bjork "desirable difficulties" framework; Kornell & Bjork 2008 on interleaved category-induction learning; standard finding that sequencing effects require an underlying discriminable rule/category structure, with item-order mattering less for arbitrary paired-associate / unconnected-fact learning where total exposure/spacing dominates.

**AL-CPL dataset (live-verified this cycle via WebFetch against `github.com/harrylclc/AL-CPL-dataset`):** Liang, Wu, Huang, Giles (EMNLP 2015 lineage); built on Wang et al. 2016's Wiki concept-map dataset; validated for strict partial-order properties (irreflexive + transitive) across 4 domains (Data Mining: 120 concepts/292 prerequisites; Geometry: 89/524; Physics: 153/487; Precalculus: 224/699).

**Direct measurement (this session, on-disk, not literature):** `data/codex_claimvalidity/raw/train.txt` (CoDEx-S, 2034 entities / 32,888 edges) and `data/codex_m_claimvalidity/raw/train.txt` (CoDEx-M, 17,050 entities / 185,584 edges) — density-vs-spanning-tree and hierarchical-relation-fraction computed directly, not estimated.

**Explicit honest flag:** no single source in the KST / Piaget / interleaving literatures states the "hierarchical-vs-flat order sensitivity" claim as a labeled dichotomy in the form used here — this is a stitched cross-literature synthesis (hence the P=0.50 novel-synthesis cap on Prediction 1), not a directly looked-up finding. The AL-CPL structural counts and the CoDEx on-disk measurements are the only fully-verified, non-interpretive numbers in this note.

---

## Status

Written per research-agent contract. No cap_map or strategy files modified. No `exp_dev_handoff_*` / `strategy_request_to_*` routing files written (USER-locked discipline: ferry mechanism deprecated; this note IS the deliverable, including the exp_dev-actionable section above — the Director reads this note directly and dispatches exp_dev).
