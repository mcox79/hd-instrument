---
problem: the_learned_is_a_taxonomic_identity_channel_is_the_dominant_unbuilt_meaning_lever
status: REFUTED
bar: "Build the LEARNED is-a/taxonomic identity channel (Rogers-McClelland property-SVD + Levy-Goldberg contexts + genus-differentia, NO WordNet at inference), GROW it by reading, and fuse it into the live meaning read; SHOW the sense-assignment decision rises CI-separated over the grounded floor on the live decision (SimLex-held-out), with the info-free twin LOSING, and report the grow-by-reading curve toward the taxonomic ceiling (0.65) -- OR a rigorous LOCATED NEGATIVE naming exactly why the learned is-a channel cannot approach the ceiling without WordNet (with a number; the brain's actual mechanism faithfully built). INVARIANT: recall path byte-identical; NO WordNet / NO external LLM at inference."
result: "LOCATED NEGATIVE (the bar's blessed full-pass clause) that REFUTES the priority-1 PREMISE. The brief's dominant-lever number (taxonomic AUF-MRR 0.650 vs 0.188, +0.488) was measured against grounded-distinctive ALONE (0.188) -- the PRE-SEQ floor. Measured against the CURRENT strongest floor (grounded-distinctive (+) grown-SEQ, the parent's just-landed parser-free lever) on the SAME live anchor-pool decision + SimLex gold: BASE AUF-MRR = 0.505 (n=94 SimLex-high) / 0.391 (n=338 pooled SimLex+SimVerb), because grown-SEQ ALONE already reaches 0.455 (n=94) -- the co-occurrence channel banks the identity signal (Harris). Against that strong floor, EVEN THE CIRCULAR WordNet taxonomic ceiling adds only +0.159 (n=94, CI[-0.001,+0.298], NOT CI-sep) / +0.057 (n=338, CI[-0.019,+0.137], NOT CI-sep); and oracle{grounded+SEQ}=0.744 EXCEEDS the WordNet ceiling 0.650 -- so the taxonomic channel adds NO reachable coverage the grown co-occurrence channel lacks on its own axis. The residual is NOT missing is-a knowledge, but it is NOT cleanly a read-out gap either: decomposed on n=94 it splits ~evenly into (i) a TRIAGE/read-out component +0.238 (recoverable only IN PRINCIPLE -- the confidence margin discriminates correctness only weakly, AUC 0.65 n=94 / 0.60 pooled, which is why the parent's Path-2 confidence sweep was a located negative), (ii) a RANKING/REPRESENTATION component +0.126 (the true partner sits at rank 2-3 'in reach' -- the relation-confusion zone the taxonomic channel targets and demonstrably FAILS to fix), and (iii) a DEEP coverage/knowledge component +0.130 (true partner rank>10, 32% of queries). My learned DIRECTED is-a channel, built faithfully (parser-free/WordNet-free Hearst read-edges -> Roller-Kiela-Nickel PPMI+SVD densification -> Collins-Quillian genus-differentia CO-HYPONYM-PENALTY capture), SEQ-backfilled to 100% is-a coverage on the favorable n=94 population: CAPTURE_vs_BASE = +0.000 (CI[0,0]), additive FUSE_vs_BASE = -0.054 (HURTS), knowledge-shuffled twin NOT beaten -- the learned is-a supplies no net identity-discrimination the strong baseline lacks. So the taxonomic identity channel is NOT the dominant unbuilt lever: it was dominant only over the obsolete pre-SEQ floor; grow-by-reading already captured it."
floor: "STRONGEST floor actually run = grounded-distinctive (+) grown-SEQ (the parent's landed parser-free BF representation), AUF-MRR 0.505 (n=94 SimLex-high, the brief's exact lever population) / 0.391 (n=338 pooled). This SUPERSEDES the brief's grounded-distinctive-alone floor (0.188), which grown-SEQ beats CI-separated (+0.329 CI[+0.201,+0.466], n=94). Info-free / knowledge-shuffled twins: symmetric shared-genus twin (isa_knowledge) and directed-capture twin BOTH not-beaten (twin_loses=False); the earlier SEQ info-free twin loses CI-sep (parent W20)."
controls: "(1) KNOWLEDGE-SHUFFLED TWIN (permute which word owns which is-a edge-row): NOT beaten by the real is-a channel on either the symmetric (isa_knowledge, twin_loses=False) or the directed (capture, twin_loses=False) variant -> the learned is-a carries no net identity signal on this decision (excludes 'a real but small effect'). (2) CIRCULAR WordNet-CM UPPER-BOUND reference (the most an is-a channel could supply): even it is NOT CI-separated over grounded+SEQ (+0.159 n=94 / +0.057 pooled) -> excludes 'a better learned extractor would win'. (3) ORACLE (perfect selective-prediction) + ORACLE-UNION (perfect per-query {BASE,CM} router): oracle_BASE 0.744 > CM 0.650 (no missing reachable coverage from CM's own axis), oracle_union 0.897 > oracle_BASE (taxonomic complementary IN PRINCIPLE but only under a perfect router+confidence -- both parent-located-negatives). (3b) RESIDUAL DECOMPOSITION (rank of true partner + margin per query): the residual splits ~evenly into triage/read-out (+0.238, recoverable only in principle) / ranking-representation (+0.126, rank 2-3 in-reach) / deep coverage (+0.130, rank>10) -> excludes 'the residual is cleanly a read-out gap' AND 'it is missing is-a knowledge'. (4) SEQ-BACKFILL to 100% is-a coverage (Rogers-McClelland inheritance): CAPTURE still +0.000 -> excludes 'coverage-limited'. (5) BASE_vs_GD CI-separated -> the strong floor is genuinely stronger than the brief's, not a measurement fluke. (6) recall path byte-identical (ranking arms only; no hdlab written); NO WordNet / NO parser / NO LLM anywhere in the learned channel."
files_changed: "experiments/exp_meaning_fusion_directed_isa_capture_v1.py (the DIRECTED learned is-a channel: parser-free Hearst read-edges -> Roller PPMI+SVD densification -> genus-differentia co-hyponym-penalty capture + SEQ-backfill generalization; the strongest faithful build), data/exp_meaning_fusion_directed_isa_capture_v1/metrics.json (pooled, no-backfill grow curve), data/exp_meaning_fusion_directed_isa_capture_v1_simlex_bf/metrics.json (n=94 favorable pop + backfill, 100% coverage), experiments/exp_meaning_fusion_isa_headroom_diag_v1.py (the DIAGNOSTIC: taxonomic headroom over the strong grounded+SEQ baseline on SimLex-high vs pooled, + oracle + oracle-union), data/exp_meaning_fusion_isa_headroom_diag_v1/metrics.json, experiments/exp_meaning_fusion_residual_decomposition_v1.py (decomposes the BASE residual into triage/read-out vs ranking/representation vs deep-coverage thirds -- answers 'is read-out the correct rerank?': NO, under-determined), data/exp_meaning_fusion_residual_decomposition_v1/metrics.json, experiments/exp_meaning_fusion_relation_rerank_v1.py (the brain's meaning-competition -- divisive normalization + recurrent lateral inhibition -- + CSLS/MP as one-shot approximations, for wall #2: ALL null over the strong base), data/exp_meaning_fusion_relation_rerank_v1/metrics.json, experiments/exp_meaning_fusion_new_channels_v1.py (symmetric-coordination + mutual-inclusion channels for wall #2: SYM hurts-but-beats-twin, INCL null -- redundant with grown-SEQ), data/exp_meaning_fusion_new_channels_v1/metrics.json, experiments/exp_meaning_fusion_equivalence_channel_v1.py (THE PIVOT: referential-equivalence/renaming channel -- synonym-specific, escapes the co-occurrence theorem; diffuse fusion hurts, precision-gated binding fires on 0 eval queries -> renaming targets entities, ~0 common-word gold-pair coverage), data/exp_meaning_fusion_equivalence_channel_v1/metrics.json, experiments/exp_meaning_fusion_contrast_probe_v1.py (research Probes 1-3: does contrast/coordination/apposition/substitutability separate SYN vs CO-HYP where cosine can't? -- cosine AUC 0.677, contrast signals add nothing, coverage-starved), data/exp_meaning_fusion_contrast_probe_v1/metrics.json, experiments/exp_meaning_fusion_confusion_taxonomy_v1.py (what the residual confusions ARE: 63% taxonomic + 18% antonym + 46% frequency-hub, WordNet analysis-only), data/exp_meaning_fusion_confusion_taxonomy_v1/metrics.json, experiments/exp_meaning_fusion_incontext_probe_v1.py (Probe 5, WiC: context-conditioned vs type-level -- VALIDATES the pivot: type-level AUC 0.485=chance-by-construction, context lifts monotonically to 0.582), data/exp_meaning_fusion_incontext_probe_v1/metrics.json, data/exp_meaning_fusion_isa_knowledge_v1/metrics.json (LANDED the never-run symmetric clean-Hearst-genus baseline -> located negative), verification/test_learned_isa_taxonomic_channel.py (scaffold-free 22-check witness). NO hdlab/ modified (Q111). NO preregs/arm_key touched."
reverify: ".venv/Scripts/python.exe verification/test_learned_isa_taxonomic_channel.py  (18 checks; reads landed metrics + live micro-checks of the mechanism)"
---

# What this is: the taxonomic identity channel is NOT the dominant unbuilt lever -- grow-by-reading already captured it; and the residual is NOT missing is-a knowledge but splits three ways (read-out / ranking / coverage), so there is no single clean next lever

**The brief's premise, stated as priority-1:** the is-a / taxonomic identity channel is "the single dominant
meaning lever" -- taxonomic AUF-MRR **0.650 vs grounded 0.188 (+0.488)**, taking the live sense-assignment
decision "from ~15% to ~65% of achievable." Build it learned-from-reading (no WordNet), grow it, fuse it, and
approach the 0.65 ceiling.

**What the disk says (the number that reframes everything).** That +0.488 was measured against
**grounded-distinctive ALONE (0.188)** -- the floor as it stood *before* the parent solver
(`measure_end_to_end...`, integrated) landed the parser-free **grown-SEQ** channel (direction-typed PPMI over
the raw word stream, grown by reading). On the SAME live anchor-pool decision and SAME SimLex gold, measured
against the **current strongest floor** (grounded-distinctive **(+) grown-SEQ**), the lever collapses:

| arm (rank the true SimLex partner among the live ~556-anchor pool) | AUF-MRR n=94 (SimLex-high, the brief's pop) | AUF-MRR n=338 (pooled) |
|---|---|---|
| grounded-distinctive ALONE (the brief's floor) | 0.188 | 0.150 |
| **grown-SEQ ALONE** (parser-free, read to 500k) | **0.455** | 0.341 |
| **BASE = grounded-distinctive (+) grown-SEQ** (the STRONGEST floor) | **0.505** | **0.391** |
| WordNet-CM taxonomic (CIRCULAR ceiling -- the MOST an is-a channel could supply) | 0.650 | 0.462 |
| oracle{BASE} (perfect confidence ordering) | **0.744** | 0.642 |
| oracle{BASE ∪ CM} (perfect per-query router) | 0.897 | 0.804 |

- **The premise is REFUTED.** Against the strong floor, even the **circular** WordNet taxonomic channel adds
  only **+0.159 (n=94, CI[-0.001,+0.298], NOT CI-separated)** and **+0.057 (n=338, CI[-0.019,+0.137], NOT
  CI-separated)**. The "+0.488 dominant lever" was the distance from the *obsolete* pre-SEQ floor; grow-by-reading
  (SEQ alone 0.455) already banks the bulk of it. This is the Harris distributional hypothesis realized: a
  direction-typed co-occurrence channel, read to strength, *is* a paradigmatic (identity) signal.
- **oracle{BASE} = 0.744 EXCEEDS the WordNet ceiling 0.650.** The grounded+SEQ representation, with perfect
  confidence, reaches HIGHER than the circular taxonomic channel does with its own confidence. So on its own
  axis the taxonomic channel supplies **no reachable coverage the co-occurrence channel lacks**; the entire
  realistic CM advantage (+0.159) is *better native confidence*, and the internal selective-prediction gap of
  BASE itself (0.505 -> 0.744 = **+0.239**) is LARGER than that. So the taxonomic axis supplies no missing
  knowledge -- but the residual is NOT cleanly a read-out gap either (see the decomposition section below): it
  splits ~evenly into a triage/read-out third, a ranking/representation third, and a deep coverage third.
- **The taxonomic channel IS complementary in principle** (oracle{BASE ∪ CM}=0.897 > oracle{BASE}=0.744): a
  *perfect per-query router* between the two would gain reachable coverage. But realizing it needs both a
  perfect router (parent measured per-query {G,SEQ} routing = +0.023, a dead end) AND perfect confidence
  (parent's Path-2 located negative). So the complementary coverage is real but **unrealizable with any learned
  read-out we can build** -- and even the ceiling-defining circular WordNet channel cannot realize it CI-sep.

## The learned DIRECTED is-a channel, built the research note's way -- and why it captures +0.000

The RESEARCH note (`RESEARCH_bf_isa_acquisition.md`) correctly diagnosed that the earlier property-SVD prototype
was missing the **directed, labelled genus EDGE**, and pointed to Roller-Kiela-Nickel 2018 (SVD-densify a
Hearst-pattern PPMI matrix; BLESS AP 0.45->0.76). I built exactly that, parser-free and WordNet-free, and
confronted the true wall (relation confusion) with a mechanism the parent never tried:

1. **Read is-a EDGES** via the self-contained Hearst extractor (copular / "kind of" / "such as"; NO WordNet, NO
   parser, NO POS), cross-occurrence CONFIRMED (>=2) + pattern-reliability weighted (CLS graded accumulation,
   McClelland-McNaughton-O'Reilly; not a hard count). Both directions (w's hypernyms and w's hyponyms).
2. **ISA_dense = Roller-Kiela-Nickel**: PPMI over the [as-hyponym (+) as-hypernym] is-a-pattern matrix,
   truncated-SVD densified (generalizes sparse edges; Saxe-McClelland-Ganguli ordered modes).
3. **The CAPTURE (the crux, and NEW vs the parent's failed symmetric captures): a Collins-Quillian
   genus-differentia CONJUNCTION** -- the co-hyponym penalty `genus_overlap(q,c) * (1 - isa_interchange(q,c))`.
   A co-hyponym (same genus, different differentia) is down-weighted; a synonym (same genus, interchangeable in
   is-a patterns) is kept. This is an explicit AND (coincidence gate), not the additive fusion / coarse-to-fine
   re-rank the parent tried and that failed.
4. **SEQ-backfill** (Rogers-McClelland property inheritance): edge-less words inherit an is-a vector = the
   SEQ-neighbour-weighted average of edge-bearing neighbours' is-a vectors -> raises is-a coverage from 18% to
   **100%** on the eval vocabulary (the research note's OOV backfill).

**Result (n=94 SimLex-high, the favorable population, backfill -> 100% is-a coverage, read to 1.5M lines):**
`CAPTURE_vs_BASE = +0.000 (CI[0,0])`; additive `FUSE_vs_BASE = -0.054` (the is-a channel HURTS the strong
baseline -- it carries relatedness/co-hyponymy, not clean identity); **knowledge-shuffled twin NOT beaten**.
Every faithful lever -- directed edges, Roller densification, the conjunction capture, 100% coverage -- and the
learned is-a channel supplies **nothing net** over grounded+SEQ. On the pooled population without backfill,
read-edge coverage caps at **18%** even at 1.5M lines, and the capture is likewise +0.000.

**Why (mechanism of the negative).** (a) The identity signal the taxonomic channel would supply is *already in*
the grown co-occurrence channel (SEQ 0.455; oracle{BASE} 0.744 > CM 0.650) -- there is almost nothing left to
add. (b) What little the taxonomic axis adds is complementary only under a perfect per-query router+confidence
(unrealizable; parent-located-negatives), not a stand-alone rankable gain. (c) Reading-derived is-a is either sparse (18%) or, once backfilled
via co-occurrence, becomes a *symmetric* co-hyponym-conflating similarity -- the same relatedness signal SEQ
already has -- so it cannot supply the clean DIRECTED discrimination. The WordNet ceiling's only advantage is
**CURATION/completeness** (a complete, sense-resolved graph), and even that advantage is not CI-separable over
grounded+SEQ on this decision.

## The symmetric shared-genus channel (the brief's other route), LANDED -- also a located negative
`exp_meaning_fusion_isa_knowledge_v1.py` (built by the parent solver but **never run to full**; I landed it):
the CLEAN, non-circular, cross-confirmed shared-genus PPMI channel, fused with grounded+SEQ. At 1.5M lines it
covers 15% of query words and **HURTS**: OVERALL genus_adds **-0.020 (CI[-0.039,+0.002], not CI-sep)**, covered
subset **-0.134**, and the knowledge-shuffled twin is NOT beaten. A shared-hypernym bag is a **co-hyponym
detector** (dog and cat both share "animal" -> high) -- it reinforces the relation confusion rather than
resolving it. This is why the directed edge was worth trying; but the directed edge, faithfully built, also
fails (above).

## Is the residual actually a "read-out/confidence" gap? DECOMPOSED (answering the follow-up -- I over-claimed first)
I initially called the residual "a read-out/confidence gap." That ran ahead of the evidence. The oracle gap is a
*selective-prediction* construct by definition (it reorders which queries you ACCEPT; it does not change any
ranking) -- so it is triage-recoverable IN PRINCIPLE, but that says nothing about whether a *realizable*
confidence signal can get it, nor whether the true partner is even rankable. `exp_meaning_fusion_residual_decomposition_v1.py`
decomposes the BASE residual (grown-SEQ fixed), per query: rank of the true partner, top-1 margin, correctness.

| n=94 SimLex-high (realistic AUF 0.506) | value | reading |
|---|---|---|
| rank1 / rank2-3 / rank4-10 / rank>10 | 0.30 / 0.23 / 0.15 / **0.32** | 30% already right; 23% "in reach"; 32% DEEP |
| triage-oracle (perfect abstention, ranking FIXED) | 0.744 | **+0.238** = the read-out/triage component |
| rank-sharpen top-3 (promote in-reach partner + triage) | 0.870 | **+0.126** = the ranking/representation component |
| (deep tail, rank>10) | -> 1.0 | **+0.130** = the coverage/knowledge component |
| AUC(margin -> correct) n=94 / pooled | 0.65 / **0.60** | margin discriminates correctness only WEAKLY |
| Spearman(margin, correct) n=94 / pooled | 0.25 / **0.13** | confidence is poorly calibrated |
| confidently-wrong fraction (margin >= median correct) | 0.30 / **0.38** | a third of errors are CONFIDENT -> unrecoverable by any confidence |

**So we do NOT know read-out/confidence is the correct rerank.** The residual splits ~evenly in THREE:
- **+0.238 triage/read-out** -- recoverable ONLY IN PRINCIPLE. The confidence margin's real discriminative power
  is weak (AUC 0.65 n=94, 0.60 pooled; Spearman 0.25/0.13) and ~a third of errors are confidently-wrong, which is
  exactly why the parent's Path-2 confidence sweep was a LOCATED NEGATIVE. Triage is the frame, not a demonstrated fix.
- **+0.126 ranking/representation** -- the true partner sits at rank 2-3, beaten by a co-hyponym/associate #1. This
  is the relation-confusion zone -- the ONE place the taxonomic channel *should* help -- and my learned is-a channel
  (and even circular WordNet, not-CI-sep) demonstrably does NOT fix it. This is an OPEN representation problem.
- **+0.130 deep coverage** -- true partner rank>10 (32% n=94, 42% pooled); a coverage/knowledge problem neither
  read-out nor a local rerank touches.

**Net:** read-out is at most ONE of two roughly-equal levers, and it is not proven realizable; the other half is
a ranking/representation problem where taxonomy is the natural-but-failed candidate; and a third is coverage. The
honest verdict is that the correct rerank is UNDER-DETERMINED -- what is firmly established is the NEGATIVE
(taxonomic-knowledge is not the dominant capturable lever), not a positive redirect.

## Prototyping fixes for the three walls (owner: "do it all, brain-foundationally, iterate, circle in on the answer") -- they CONVERGE
After the decomposition I built and measured a brain-foundational candidate for each wall, researched the wall
(a literature scan, folded below), and iterated. Everything converges on ONE diagnosis. All on the live decision
(grown-SEQ fixed, BASE = grounded-distinctive (+) grown-SEQ = 0.506 n=94 / 0.392 pooled), twin-controlled.

**WALL #2 (ranking / relation-confusion) -- the brain's OWN meaning-competition, built faithfully, does NOT resolve it.**
`exp_meaning_fusion_relation_rerank_v1.py`. Not a retrieval trick: DIVISIVE NORMALIZATION (Carandini-Heeger, PINNED)
+ recurrent LATERAL-INHIBITION settling weighted by candidate-candidate similarity (Usher-McClelland; a co-hyponym
CLUSTER should self-suppress). Result (n=94 / pooled): LATINHIB -0.003 / +0.005, DIVNORM -0.003 / +0.005, and the
in-reach (rank 2-3) subset -0.015 / +0.006 -- NONE CI-separated, twin not beaten. One-shot engineering
approximations (CSLS -0.018, Mutual-Proximity +0.006) also null. MECHANISM: the co-hyponym and the true synonym are
near-equidistant AND mutually coupled in grounded+SEQ, so lateral inhibition suppresses BOTH equally -- competition
cannot route to a distinction that is not in the geometry. So wall #2 is REPRESENTATION-bound: the signal must be
ADDED, not routed.

**Two NEW reading-learned channels to ADD the signal -- both fail over the strong base.** `exp_meaning_fusion_new_channels_v1.py`.
- SYM (symmetric coordination "X and/or Y", Schwartz-Reichart-Rappoport -- biases toward similarity): over the strong
  grown base it HURTS (-0.051 n=94 / -0.068 pooled) though it beats its shuffled twin -- real similarity signal, but
  REDUNDANT with grown-SEQ (coordinated words already are directional neighbours) so it only dilutes.
- INCL (mutual/bidirectional distributional inclusion, Weeds-Clarke -- synonyms mutually include, co-hyponyms keep
  private features): null-to-negative (-0.029 / -0.052). Co-hyponyms share so many features that mutual inclusion
  stays high for them too.

**WALL #1 (triage) -- cross-channel top-1 AGREEMENT** beats the margin as a confidence ordering on n=94 but NOT on
pooled (agreement>margin = True n=94 / False pooled) -- a weak, non-robust triage signal, consistent with the
parent's Path-2 located negative.

**WALL #3 (deep) -- Binder-2016 experiential richness is UNAVAILABLE at coverage.** The differentia the neuroscience
names (distinctive experiential features; Cree-McRae) would need a RICH feature space; Binder-2016 (65 experiential
dims, an admissible offline foundation asset) covers only 64/521 SimLex-high words -> essentially ZERO covered PAIRS,
so it cannot even be tested as a channel. Lancaster (already used) is high-coverage but coarse (11 dims) and
concreteness-confounded (a prior diagnostic put its synonym/sibling separation at random-init AUC 0.46 after
balancing). So no available feature source is BOTH rich and high-coverage.

**RESEARCH FOLDED IN (the wall, understood).** A literature scan surfaced the decisive citation: **Scheible &
Schulte im Walde (J. Language Modelling), "first-order co-occurrence distributions of the related words tend to be
very similar across the relations" -- antonyms and co-hyponyms "can appear as similar as genuine synonyms under
cosine."** This is a PUBLISHED representational-ceiling theorem, and it EXPLAINS the convergence: grounded, SEQ, SYM,
INCL, is-a are ALL first-order co-occurrence statistics, so they ALL inherit the inability to separate synonym from
co-hyponym. The literature's only separators are the distinctive-feature differentia (needs rich features) and
token-level substitutability (a different instrument). The neuroscience (Rogers-McClelland; Saxe; Cree-McRae;
Patterson-Lambon Ralph hub-and-spoke) agrees: the separator is the DISTINCTIVE-FEATURE differentia = the late
(small-eigenvalue) modes of the property-covariance SVD, which the brain grounds in rich PERCEPTUAL/EXPERIENTIAL
spokes at full coverage.

**THE CONVERGED ANSWER (six mechanisms + a theorem + a coverage analysis).** The +0.126 ranking wall is a
FINE-FEATURE representational/data ceiling, NOT an untried mechanism: (a) the published theorem says first-order
co-occurrence cannot separate the two relations; (b) six brain-foundational mechanisms (is-a, recurrent competition,
divisive-norm, CSLS, mutual-inclusion, symmetric-coordination) all converge to null/negative over the strong base
because they are all first-order co-occurrence; (c) the differentia that DOES separate (raises the oracle) is
unroutable by the brain's own competition AND needs features that are rich AND high-coverage, which no available
source has (reading = high-coverage but can't-separate; Binder = rich but ~0 eval-pair coverage; Lancaster =
high-coverage but coarse/confounded). The brain resolves it via rich experiential grounding at full coverage (the
ATL spokes); our offline norms approximate that only coarsely or sparsely. The one untested axis DIFFERENT in kind
-- token-level / in-context substitutability -- is unlikely to help the COMMON, monosemous SimLex/SimVerb words
(context adds no disambiguation where a word has one sense) and its value for polysemous/rare senses is UNMEASURABLE
on SimLex (a separate problem, for which the WiC gold on disk is the right instrument). This is the fair located
negative: the brain's actual mechanisms, faithfully built, all fail because the distinguishing signal is a fine
experiential feature not available from reading at coverage.

## The PIVOT beyond the wall (owner: "how do we pivot to overcome this in the substrate?")
The wall's cause dictates the pivot: every failed mechanism was a first-order co-occurrence SIMILARITY statistic,
which the theorem forbids from separating synonym/co-hyponym. So the pivot must be a signal DIFFERENT IN KIND. I
built and measured the strongest one -- a REFERENTIAL-EQUIVALENCE channel (`exp_meaning_fusion_equivalence_channel_v1.py`).

**The idea (brain-foundational, reading-derived, escapes the theorem).** The brain knows sofa==couch by
REFERENTIAL IDENTITY (they rename the same thing), and language marks this explicitly: "sofa, also called a
couch", "X (aka Y)", "X, i.e., Y". These fire for SYNONYMS and NOT for co-hyponyms ("dog, i.e., cat" never
occurs) -- the synonymy analog of the Hearst is-a patterns, a targeted CONSTRUCTION rather than a cosine, so it
is not subject to the co-occurrence theorem. It correctly extracts film/movie, sofa/couch, motor/engine,
atom/molecule when present.

**Measured -- it does NOT overcome the wall, for a principled reason (coverage MISMATCH, not a wrong mechanism).**
On the live decision (grown-SEQ base 0.506 n=94), sw_cap=2.8M:
- diffuse fused channel: -0.056 (n=94) / -0.031 (pooled), twin NOT beaten -- it connects a word to WHATEVER it was
  renamed to (usually a non-gold partner), so it dilutes.
- PRECISION-GATED direct binding (confirmed >=2, high-precision patterns only, hard override, no dilution):
  **+0.000 -- the gate fires on ZERO eval queries.** No confirmed high-precision rename connects a SimLex query
  word to its anchor-pool partner, even at 2.8M lines.
- Edge-quality diagnostic (400k): of 13 equivalence edges among SimLex words, 5 are true gold pairs; explicit
  renaming targets ENTITIES / TECHNICAL TERMS (aliases), so it covers ~1.5% of common-word gold pairs and
  connects the rest to wrong partners. Common adjective/verb/noun synonyms are almost never explicitly renamed.

**So the complete, converged answer: no reading-derived channel overcomes this wall for common-word synonymy at
the type level.** Three INDEPENDENT principled limits: (1) the co-occurrence theorem (similarity channels); (2)
the perceptual-feature COVERAGE ceiling (the differentia is perceptual; Binder-2016 is rich but 534 words -> ~0
eval pairs, and it can't be propagated from co-occurrence without reintroducing the theorem); (3) the renaming
COVERAGE mismatch (referential equivalence is correct-when-present but targets entities, ~0 common-word gold
pairs). The distinction is fundamentally PERCEPTUAL + REFERENTIAL, acquired through embodied experience, which
text does not supply at coverage.

**THE SUBSTRATE PIVOT -- three constructive routes, each with its honest cost (ranked):**
1. **CHANGE THE INSTRUMENT to token-level / in-context (RECOMMENDED).** The brain NEVER does context-free type-level
   meaning; it resolves a word IN a sentence, where top-down context disambiguates and the type-level co-hyponym
   confusion is moot. This is where the reader is strong and brain-faithful. The WiC gold is on disk
   (`data/wsd_benchmarks/`, a live board arm). Cost: it is a different (adjacent) problem -- sense-selection, not
   type-level synonym ranking -- so it re-frames rather than "solves" this brief.
2. **ACQUIRE fine PERCEPTUAL/EXPERIENTIAL features at full-vocabulary coverage.** The differentia is the ATL
   spokes; supply it as a static offline FOUNDATION asset richer than the 11-dim Lancaster and broader than the
   534-word Binder (e.g. offline-computed multimodal/visual features, or a larger experiential-norm set). Cost: a
   DATA-ACQUISITION problem, not a mechanism, and it reaches for perception a text-only reader does not have.
3. **ACCEPT coarse type-level meaning as sufficient.** grounded+SEQ (0.505) is already ~76% of the realistic
   ceiling and is the parent's landed BF win; the residual synonym/co-hyponym distinction is a genuine modality
   limit for a text reader, not a fixable mechanism gap. Spend effort elsewhere (the read-out third, or token-level).

**Strategic recommendation:** the type-level synonym-vs-co-hyponym decision on SimLex is the WRONG target for a
text-only reader -- it asks text to supply a perceptual/referential distinction it structurally lacks. Pivot the
substrate to token-level sense-selection (route 1), where the reader operates as the brain does; treat fine
synonymy as an experiential foundation asset (route 2) only if perceptual data can be acquired at coverage.

## Research-driven deepening + probes (owner: "research to understand this, determine probes to nail it down")
A neuroscience/psycholinguistics drill nailed the brain's mechanism and corrected two things I had over-stated.

**How the brain does it (the mechanism, exactly).** A word activates a convergent MULTIMODAL pattern in the ATL
hub over modality SPOKES (vision/sound/action/affect); synonyms (couch/sofa) converge to the SAME spoke pattern
(same referent), co-hyponyms (dog/cat) share COARSE spokes but differ on DISTINCTIVE spokes (bark vs meow) --
the differentia is fine PERCEPTUAL features (Cree-McRae; Patterson-Lambon Ralph). Acquisition is a DIVISION OF
LABOR: perception/cross-situational learning fixes the REFERENT (Yu-Smith); language distribution carries a lot
(blind adults recover "perceptual" structure from language, Kim-Bedny PNAS 2019/2021; Andrews 2009); and
REFERENTIAL-PRAGMATIC CONTRAST (Markman mutual-exclusivity; Clark principle-of-contrast) supplies the DISTINCTNESS
that keeps two words from collapsing to one concept -- but contrast is a COMPETITION constraint, not a similarity
readout (Gandhi-Lake: ME must be an explicit inductive bias, absent by default). Retrieval is TOKEN-LEVEL,
context-gated prediction (N400 = semantic prediction error, Rabovsky-McClelland), NOT a context-free type lookup.

**Two corrections to my earlier claims, from the probes:**
- **Cosine is NOT blind to the distinction.** `exp_meaning_fusion_contrast_probe_v1.py` (WordNet-labeled 400 SYN +
  400 CO-HYP pairs, labels analysis-only): fused grounded+SEQ cosine ranks a synonym above a co-hyponym at AUC
  **0.677** -- the Scheible theorem is about heavy OVERLAP, not zero signal. So the wall is not pairwise
  inseparability; it is the MULTI-CANDIDATE live ranking, where a close sibling / antonym / frequency-HUB sneaks
  above the true synonym.
- **The contrast/mutual-exclusivity lever the research flagged -- tested directly -- does NOT pan out on our
  corpus.** Coordination "X and Y" does NOT behave as a co-hyponym detector here (AUC 0.573, weakly favors
  synonyms; a frequency confound; coverage 22%/7%); explicit contrast ("X not Y", "X versus Y") and apposition
  ("X i.e./aka Y") have ~0 coverage for common words (AUC 0.501/0.501, 0% apposition coverage). Substitutability-
  divergence separates in the right direction (synonyms lower, AUC 0.375) but is weaker than and redundant with
  cosine. The contrast-corrected score does NOT beat cosine (0.677 -> 0.677). Same coverage wall as renaming/is-a:
  contrast constructions exist for entities/technical terms, not everyday synonyms.

**What the confusions ACTUALLY are** (`exp_meaning_fusion_confusion_taxonomy_v1.py`, n=94, 66 wrong; WordNet
analysis-only): IN-REACH (rank 2-3) = 63% TAXONOMIC (co-hyponym 45% + hyper/hypo 18%), 18% ANTONYMS, 9% actually-
valid ALTERNATIVE synonyms (not real errors), 9% associates; and **46% of wrong top-1 picks are higher-FREQUENCY
"hub" words than the true partner.** DEEP (rank>10) = 40% genuine associates/far (a coverage problem) + 40%
taxonomic. So the residual is a multi-candidate ranking problem under THREE named pressures: frequency hubs (46%),
taxonomic siblings (63% of in-reach), antonyms (18%).

**Net understanding (nailed with numbers).** For a TEXT-ONLY reader at the TYPE level, the fine synonym/co-hyponym
ranking is limited by (i) heavy distributional overlap (cosine 0.677, not clean), (ii) frequency-hub intrusion
(46%), (iii) coverage-starved contrast/apposition constructions. The brain's separating signal is fine PERCEPTUAL
differentia + IN-CONTEXT resolution + a COMPETITION/contrast step -- of which only the last is reading-derivable,
and it is coverage-starved here.

**IN-CONTEXT PROBE (Probe 5) -- RUN, and it VALIDATES the pivot** (`exp_meaning_fusion_incontext_probe_v1.py`, WiC
dev, n=568, target coverage 0.92). A context-conditioned representation v(w|C) = alpha*grounded(w) +
(1-alpha)*mean(grounded(sentence context)) -- the simplest predictive-coding contextualization. TYPE-level
(alpha=1, the word's vector alone) is AUC **0.485 = chance BY CONSTRUCTION** (identical vector for the same word
in both sentences -> it structurally cannot do the task). Folding in context lifts it MONOTONICALLY: alpha 1.0 ->
0.7 -> 0.5 -> 0.3 -> 0.0 gives AUC 0.485 -> 0.536 -> 0.542 -> 0.555 -> **0.582** (WiC-acc 0.574), same-vs-different
cosine gap widening throughout. So the substrate CAN resolve meaning IN CONTEXT where the type-level
representation cannot -- the type-level ceiling is a consequence of the FRAMING, not a fundamental inability.
(Modest absolute AUC 0.582 = a directional grounded-only probe -- the discrimination is CONTEXT-carried, since the
same-word target vector is constant across the two sentences. INDEPENDENT CORROBORATION, stronger: the substrate's
already-landed, tuned in-context WiC cells reach WiC accuracy ~0.66-0.68 (`exp_curated_foundation_wic_v1` 0.682,
`exp_wic_optimization_stack_v1` 0.664) -- far above the type-level 0.5 and above this cheap grounded-only probe. So
the pivot is corroborated by existing substrate work, not resting on one probe.)

**So the substrate pivot is now evidence-backed, not just recommended:** resolve meaning TOKEN-LEVEL / in-context
(the brain's actual mode; N400/predictive), NOT as context-free type-level facts. The type-level synonym-ranking
this brief posed is the wrong target for a text reader; the in-context decision is tractable and brain-faithful.
(This is a distinct problem -- context-conditioned sense-selection, partly worked in the WiC cells -- so it is a
re-frame/hand-off, not a within-brief solve.)

## Every component is 100% brain-foundational -- and the negative is NOT an upstream fidelity gap (owner directive #1-4)
The owner's standing mental model: "if a truly brain-foundational component is not working, some upstream
component is not 100% BF." **This is the documented exception, and it matters.** The end component (the learned
is-a channel) is 100% BF: Hearst-family reading evidence (a computation a competent reader performs; NOT a
dictionary lookup) -> graded reliability-weighted CLS accumulation -> Levy-Goldberg PPMI -> Saxe-McClelland
ordered SVD -> Georgopoulos cosine -> Ma-Pouget convergent-cue Bayes; NO WordNet, NO parser, NO POS. The entire
upstream chain (grounded ATL + grown-SEQ) is the parent's audited **100%-BF, parser-free** representation
(`FULL_CHAIN_BF_AUDIT.md`). The is-a channel does not underperform because something upstream is non-BF -- it
underperforms because its **contribution is redundant** with the already-BF co-occurrence channel (Harris), and
the residual that remains is split (read-out / ranking / coverage), not a missing-knowledge slot. A faithful BF
component can be *correct and redundant*; that is a real,
non-obvious outcome, and it is why chasing "more knowledge here" is the wrong move.

## What I did NOT establish (and would withdraw first if wrong)
- I did NOT prove the taxonomic axis is *worthless* -- oracle{BASE ∪ CM}=0.897 shows real complementary reachable
  coverage IN PRINCIPLE. I claim only that it is NOT the dominant lever and NOT realizable by a learned-from-reading
  channel (or even by circular WordNet's own confidence) CI-separated over grounded+SEQ. I would withdraw any
  "taxonomy is useless" reading; the honest claim is "not dominant, not learnable-to-CI-sep here, read-out-bound."
- The eval is the SimLex/SimVerb-covered subset of the live anchor-pool decision (n=94 / n=338), a faithful
  sample of `canonicalize`'s decision, not a whole-corpus census. The genuinely-rare tail the loop also grounds
  is unmeasured by SimLex (parent W27 caveat inherited).
- The co-hyponym-penalty beta was fixed at 1.0 (CAPTURE AUF 0.5054 <= BASE 0.5063 already, so larger beta only
  down-weights a null-to-negative signal further). I did not exhaustively sweep beta; I would test that first if
  challenged, but the additive-FUSE-hurts + twin-not-beaten + CM-not-CI-sep evidence converges.

## KEY REALIZATIONS (the enabling moves)
- **Recompute the floor in-place against the STRONGEST rep, not the number in the brief.** The whole refutation
  turns on one move: the brief's "grounded floor 0.188" was stale (pre-SEQ). Measuring grounded+SEQ (0.505) on
  the SAME population dissolved the +0.488 "dominant lever" into +0.159-not-CI-sep. This is the `flat_store`
  lesson again: an isolation/pre-baseline number that collapses against the strongest floor.
- **oracle > ceiling is the tell that a channel adds no new reachable coverage.** oracle{grounded+SEQ}=0.744 >
  WordNet-CM 0.650 proves the co-occurrence channel already reaches past the taxonomic ceiling on its own axis;
  the taxonomic "advantage" is confidence, not knowledge. Compute the oracle before concluding a knowledge gap.
- **A symmetric shared-genus bag is a co-hyponym DETECTOR, not an identity discriminator** -- it structurally
  reinforces the very relation confusion it was meant to fix (measured: hurts + twin not beaten). Directionality
  is the missing axis; but even the directed edge, at 100% coverage, is redundant with SEQ.
- **A brain-foundational component can be correct AND redundant.** The "not-working -> upstream-not-BF" heuristic
  has an exception: when an earlier BF channel already captures the signal, a new faithful BF channel adds nothing
  -- the diagnosis is redundancy, not a fidelity gap. Test contribution against the strongest existing rep, not
  against a bare floor.
- **When N brain-foundational mechanisms all converge to the same null, look for the THEOREM.** is-a, recurrent
  competition, divisive-norm, CSLS, mutual-inclusion, and symmetric-coordination all landed null/negative over the
  strong base. The unifying reason was a PUBLISHED result (first-order co-occurrence provably cannot separate
  synonym from co-hyponym): they are all first-order co-occurrence statistics. A convergent wall across faithful
  mechanisms is a signal to find WHY they share a limit -- here, they share an input statistic -- not to keep
  trying more of the same kind. The separator (the distinctive-feature differentia) is a DIFFERENT kind of signal,
  and it is coverage-starved, not un-tried.
- **A smoke win over a WEAK base can invert over the STRONG base.** SYM was +0.096 CI-sep over the ungrown-SEQ
  smoke base (0.061) and -0.051 over the grown base (0.506) -- it was adding what grown-SEQ later supplied. Always
  confirm a candidate against the strongest floor before believing it.
- **Check the DIRECTION of a construction signal before using it.** The research named contrast/coordination as
  the key untested lever -- and I had used coordination BACKWARDS (fused "X and Y" as a SIMILARITY boost). "X and
  Y" implies X != Y: coordination is a CO-HYPONYM/distinctness detector, not a similarity signal. (It still did not
  pan out here -- coverage -- but the lesson stands: a construction's implicature sets the sign.)
- **When a decision is stuck at a type-level ceiling, test whether the brain even OPERATES at that level.** The
  brain resolves meaning IN CONTEXT (token-level, N400/predictive), and the type-level frame was AUC 0.5 BY
  CONSTRUCTION on WiC. Folding in context lifted it monotonically (0.485 -> 0.582), and the substrate's tuned WiC
  cells already reach ~0.66-0.68 -- so the "wall" was partly the FRAMING. Question the instrument, not just the
  mechanism.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **Meaning channel / is-a taxonomic identity:** the "is-a is the dominant unbuilt lever" verdict is STALE and
  should be corrected. Against the landed grounded+SEQ representation the taxonomic headroom is +0.159 (n=94, not
  CI-sep) / +0.057 (pooled, not CI-sep); grown-SEQ already supplies the paradigmatic identity signal (SEQ alone
  0.455). Record: the residual over grounded+SEQ (oracle 0.744 vs realistic 0.505) is NOT a missing knowledge
  channel and NOT cleanly a read-out gap -- it decomposes ~evenly into triage/read-out (+0.238, recoverable only
  in principle), ranking/representation (+0.126, rank 2-3 in-reach), and deep coverage (+0.130); the taxonomic
  axis is complementary-in-principle (oracle-union 0.897) but not learnable-to-CI-sep from reading.
- `exp_meaning_fusion_isa_knowledge_v1` (built by the parent, previously un-landed): now LANDED as a located
  negative (symmetric shared-genus HURTS, twin not beaten).

## CROSS_SOLUTION_IMPROVEMENT_MAP inputs (owner 2026-09-09)
- **My wall (flagged UPSTREAM component):** the meaning-decision RANKING/REPRESENTATION for the relation-confusion
  zone (true synonym at rank 2-3, beaten by a co-hyponym/associate) -- NOT a knowledge channel, and NOT cleanly a
  read-out channel. The residual over grounded+SEQ decomposes ~evenly into triage/read-out (+0.238, recoverable only
  in principle; parent Path-2 located-negative), ranking/representation (+0.126, the in-reach zone), and deep
  coverage (+0.130). The correct rerank is UNDER-DETERMINED; what is firm is that taxonomic-knowledge supply is not it.
- **Inputs my (refuted) channel consumed:** the parser-free grown-SEQ store
  (`reading_grounding_loop.track_directional_context_counts` + `directional_context_lemmas`); grounded ATL
  (`grounded_similarity`); the self-contained Hearst read-edge extractor; SimLex-999 + SimVerb-3500 gold.
- **Recommended forward direction (validated):** route the meaning decision TOKEN-LEVEL / in-context (Probe 5:
  type-level AUC 0.485 -> context 0.582; landed WiC cells ~0.66-0.68) -- the brain's N400/predictive mode. This is
  the meaning cluster's real lever, and it is the WiC problem-owner's territory (a hand-off, not this brief).
- **Reopen trigger:** if a brain-exact per-query reliability / metacognition signal is built that closes the
  BASE read-out gap CI-sep, the taxonomic axis's complementary coverage (oracle-union 0.897) becomes worth
  re-testing as a routed channel -- but only then.

## WHAT THIS NEEDS TO IMPROVE IN CAPABILITY (ranked by evidence + leverage)
The capability that would improve the meaning read is NOT more taxonomic/is-a knowledge (refuted). In order:
1. **Route the meaning decision TOKEN-LEVEL / in-context (the #1 lever; VALIDATED).** The live `canonicalize` is a
   context-FREE type-level read; the brain is context-gated (N400/predictive). Type-level is AUC 0.485 (chance by
   construction); context-conditioning lifts it (my probe 0.582; landed WiC cells ~0.66-0.68). Improvement = wire
   the sense-assignment read to condition on the sentence (biased competition / predictive top-down), not a
   context-free type vector. This is the meaning cluster's real lever and the WiC problem-owner's territory.
2. **Supply fine PERCEPTUAL/EXPERIENTIAL features at full-vocabulary coverage.** The synonym/co-hyponym differentia
   is perceptual (dog barks, cat meows -- ATL spokes). Our grounded spoke is coarse (11-dim Lancaster,
   concreteness-confounded on synonym/sibling); Binder-2016 is the right KIND (65 experiential dims) but covers
   ~0 eval PAIRS. Improvement = acquire a rich experiential-feature asset at coverage (larger norm set or offline
   multimodal features), then the differentia (ordered-SVD late modes) has real input. A FOUNDATION-asset problem.
3. **A brain-exact per-query RELIABILITY / metacognition for the read-out third** (0.505 -> oracle 0.744 selective-
   prediction gap). But scalar confidence + dual-process recollection are parent located-negatives, and ~1/3 of
   errors are CONFIDENTLY wrong (representation, not metacognition) -- so this likely rides on (1)/(2), not alone.
4. **Frequency-hub suppression in the read-out** (46% of wrong picks are higher-frequency "hub" words). CSLS /
   Mutual-Proximity tested null at type level, but the hub finding suggests a hubness-aware read-out is worth
   revisiting IN the in-context frame (1), where the candidate field is context-narrowed.
NOT worth redoing (measured dead ends over grounded+SEQ): learned is-a / shared-genus / Roller-densified,
symmetric-coordination, mutual-inclusion, referential-equivalence, recurrent competition / divisive normalization.

## COMPONENT / BF STATUS (what each computes + its mathematical brain-foundational status; owner checklist item 7)
BF legend: PINNED = the brain's exact equation, evidence-locked; BF_SPIRIT = a defensible computational-level model
of a brain operation; OUR-INVENTION = a placeholder we built; NOT_BF = an external/fitted tool. All channels below
use NO WordNet / NO parser / NO LLM at inference.

| component (file) | what it computes | BF status | finding for this problem |
|---|---|---|---|
| grounded spoke (`hdlab/grounded_similarity`) | z-scored Lancaster+Brysbaert sensorimotor vector; whitened = distinctive | **PINNED** (Carandini-Heeger normalization; Patterson-Nestor-Rogers distinctive-feature ATL) | correct + live, but COARSE (11-dim) -> can't carry the fine perceptual differentia; concreteness-confounded on syn/sibling. Data/richness LIMIT, not a computation flaw |
| grown-SEQ (`reading_grounding_loop.track_directional_context_counts` + `directional_context_lemmas`) | direction-typed PPMI over the raw word stream, L2-normed | **PINNED-computation / BF_SPIRIT** (theta-phase order coding, Lisman-Idiart; Levy-Goldberg predictive PPMI; divisive norm) | the dominant meaning signal (AUF 0.455 alone); grow-by-reading is the parent's landed lever. Already banks most of the "taxonomic" signal (Harris) |
| convergent-cue fusion (`convergent_cue_reader` / experiment) | gain-weighted sum of log-posteriors | **BF_SPIRIT** (Ma-Pouget cue integration; Weber-Fechner saturating gain) | correct; parameter-free-ish. Fuses grounded+SEQ into the strong baseline (0.505 n=94) |
| live meaning decision `canonicalize` (`reading_grounding_loop`) | nearest-anchor cosine + SDT accept | **BF_SPIRIT** | the KEY deviation: it is a context-FREE TYPE-level read; the brain is TOKEN-LEVEL, context-gated (N400). This framing is the wall -- see improvement #1 |
| learned is-a / property-SVD differentia (`exp_meaning_fusion_learned_isa_channel`, `..._differentia_channel`) | ordered SVD of a distinctiveness-reweighted property matrix; late modes = differentia | **BF_SPIRIT** (Rogers-McClelland; Saxe-McClelland-Ganguli; Cree-McRae) | the COMPUTATION is BF and RAISES the oracle (+0.044 CI-sep) -- but its INPUT (fine features) is coverage-starved and it is unroutable at this power. BF computation, starved input |
| directed read-is-a edge (Roller Hearst PPMI+SVD) | SVD-densified Hearst-pattern co-occurrence | **BF_SPIRIT** (Hearst-as-reading-evidence; Roller-Kiela-Nickel) | correct-when-present; +0.000 on the live decision (coverage ~18%, redundant with SEQ) |
| referential-equivalence (`exp_meaning_fusion_equivalence_channel`) | renaming/apposition construction edges | **BF_SPIRIT** (referential binding / apposition resolution) | correct-when-present but ~0 common-word coverage (renaming targets entities); diffuse fusion hurts, gated fires 0 |
| contrast/coordination signal (`exp_meaning_fusion_contrast_probe`) | coordination/contrast/apposition construction frequency | **BF_SPIRIT** (Clark principle-of-contrast; Markman mutual-exclusivity -- a COMPETITION constraint) | reading-derivable in principle; ~0 coverage for common words on our corpus; coordination is a co-hyponym detector (I had used it backwards as similarity) |
| recurrent competition (`exp_meaning_fusion_relation_rerank`) | divisive normalization + lateral-inhibition settling | **PINNED-computation** (Carandini-Heeger; Usher-McClelland LCA) | faithful; null here -- co-hyponym+synonym are mutually coupled, so inhibition suppresses both. Confirms the signal must be ADDED not routed |
| WordNet conceptual channel (`hdlab/conceptual_meaning`) | IDF-weighted definitional-feature cosine | **NOT_BF at inference** (an ontology) -- ceiling/analysis reference ONLY, banned at inference | marks headroom (0.650) and separates syn/cohyp, but not learnable-from-reading and circular with SimLex |
| in-context read (Probe 5 + landed WiC cells) | context-conditioned representation (predictive top-down) | **BF_SPIRIT** (N400/predictive, Rabovsky-McClelland; biased competition) | VALIDATED direction: context lifts where type-level cannot. The recommended capability path |

---
## TLDR (plain language)
The system learns what a new word means by matching it to a word it already knows. The brief said the biggest
missing helper is knowing "what kind of thing a word is" (a robin is a bird), and that adding it would take the
system from getting about 15% of these matches right to about 65%. That 65%-vs-15% comparison was made against
an OLD, weak version of the system. In the meantime a different fix already shipped -- letting the system learn
word meanings from the ORDER words appear in as it reads -- and that fix alone already does most of the job. When
I measure the "what kind of thing it is" helper against the CURRENT system instead of the old one, it barely
adds anything: even a perfect dictionary (which we're not allowed to use at read time anyway, and which is
"cheating" on this test) only nudges the score up by an amount too small to be sure it's real, and the
learned-from-reading version I built -- done the careful way the research recommended, and stretched to cover
every test word -- adds exactly nothing and sometimes hurts. The reason is that reading word-order already
teaches the system most of "what kind of thing" a word is. The shortfall that's left is NOT one thing: about a
third of it is the system being bad at knowing when it's right (and, as an earlier study found, we can't fix
that reliably); about a third is cases where the right answer is sitting at 2nd or 3rd place, just behind a
look-alike word (this is the spot the "what kind of thing" helper was meant to fix -- and it doesn't); and about
a third is cases where the right answer is buried deep, which needs genuinely more/better knowledge. So the
headline "this is the dominant missing piece" is wrong against today's system: it was the dominant piece against
last month's system, it's already largely built, and there is no single clean next lever -- the remaining
shortfall is split three ways. The constructive finding: the brain doesn't judge word meaning in the abstract --
it does so IN A SENTENCE, using the surrounding words. When we let the system use the sentence context (instead of
judging the word in isolation), the meaning distinction it could NOT make in isolation becomes makeable -- and the
system's existing in-context tools already do this at ~two-thirds accuracy. So the real improvement is to decide
word meaning in context, the way the brain does, not to keep hunting for a context-free "what kind of thing" cue
that a text-only reader cannot supply.

## QUESTIONS
None blocking. One flag for the strategy session: the priority-1 ranking rested on the +0.488 lever number,
which does not survive the strongest-floor discipline (grounded+SEQ). Do NOT simply re-file it as a
read-out/confidence problem -- the residual decomposition shows that is only ~one-third of it (and not proven
realizable); the meaning-cluster re-rank should reflect the three-way split, not a single successor lever.

## NEXT STEPS
1. **(re-rank, strategy)** The taxonomic-knowledge lever is refuted against grounded+SEQ, and the ranking wall #2 is
   now shown (six mechanisms + a theorem) to be a FINE-FEATURE representational/data ceiling, not an untried
   mechanism. Do NOT re-file this cluster as "supply is-a knowledge" NOR as a single read-out lever. The only two
   directions with any remaining headroom are: (a) a RICH + HIGH-COVERAGE experiential feature space (the differentia
   the brain grounds in perceptual spokes) -- Binder-2016 is the right KIND but covers ~0 eval pairs, so the real
   task is acquiring/deriving fine experiential features at coverage (a FOUNDATION-asset problem, not a reading-channel);
   (b) **the TOKEN-LEVEL / in-context decision -- now VALIDATED, not just recommended** (Probe 5: type-level AUC 0.485
   -> context-conditioned 0.582 monotone; the substrate's landed WiC cells already reach ~0.66-0.68). The
   recommended substrate move is to route the meaning read through context (the brain's N400/predictive mode); it is
   a distinct problem (context-conditioned sense-selection, the WiC cells' territory), so a HAND-OFF, not a within-brief solve.
2. **(do NOT redo -- measured dead ends over grounded+SEQ)** learned is-a / shared-genus / Roller-densified (+0.000);
   symmetric-coordination (hurts); mutual-inclusion (null); CSLS / Mutual-Proximity (null); recurrent competition /
   divisive normalization (null). All are first-order co-occurrence and inherit the Scheible & Schulte im Walde
   ceiling. Even circular WordNet is not CI-sep over grounded+SEQ. Do not re-run these on this decision.
3. **(where the differentia IS real)** The distinctive-feature differentia (late-mode property-SVD) RAISES the oracle
   ceiling (+0.044 CI-sep, parent W24) -- the signal exists; it is unroutable at the available power AND coverage-
   starved. If pursued, the lever is fine EXPERIENTIAL features at scale, not more co-occurrence.
4. **(where is-a MIGHT still pay -- a different task)** is-a's proven wins are on DIRECTIONAL entailment and
   common-noun coref (typed-spoke cells), not synonym-identity ranking. Pursue the taxonomic axis where
   directionality is the task, not where grown co-occurrence already suffices.

---
INTEGRATED_BY_STRATEGY 2026-09-10 (CONT-160). Reverified test_learned_isa_taxonomic_channel.py 36/36
first-hand. REFUTED integration: the located-negative + the validated IN-CONTEXT pivot folded to
BRAIN_FOUNDATIONAL_AUDIT.md §2b; durable negatives recorded (type-level is-a/similarity/contrast/
coordination/equivalence exhausted — grown-SEQ banks the distributional signal + first-order co-occurrence
provably conflates syn/antonym/cohyp, Scheible-Schulte). NO hdlab landed (refuted). This is the key
evidence for the capability-wall response: the text-only type-level meaning frame is exhausted; the way
through is (1) in-context/token-level routing [validated #1 lever] + (2) grounding-coverage foundation
(perceptual differentia beyond text). Memory brain-foundational-is-a-acquisition-blueprint corrected.
