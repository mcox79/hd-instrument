# Research: scouting a real-data test target for TRANSITION_OP without the frequency-cap trap

Filed by: research (Opus synthesis of 4 parallel Sonnet lit-scans + 1 sub-spawned single-agent lit-scan + internal
data audit). Trigger: `TRANSITION_OP` (sequential non-commutative matrix-chain operator) is VET'd CHAIN_GRADE on the
synthetic dominance arena (`exp_interaction_bilinear_wall_break_v1` follow-on cell, per
`notes/research_brain_asymmetric_directed_relation_operators_2026-07-15.md`) — a construction-proof only. Task: find
where a real directed/asymmetric-relation test could show genuine value, distinct from the program's known
frequency-cap wall (single-relation real-data prediction is usually dominated by node degree/marginals, per the
Costanzo/paralog/Hetionet/CoDEx findings already on file this session). Research-only; no code, no compute, no cell
dispatched, per task instruction.

---

## HEADLINE

**The frequency-cap trap is real and independently reconfirmed across every domain scanned this cycle (KG, biology,
citation networks) — but there is one structurally frequency-immune test class: multi-hop compositional queries
filtered to their irreducible subset, held out by composition PATTERN/ORDER rather than by triple.** This is not a
hedge — it is the literature's own diagnosed fix (Gregucci et al. 2025 found up to 98% of standard multi-hop KG
benchmarks are secretly one-hop-reducible and therefore just as frequency-capped as plain link prediction; their
fix is exactly "filter to the irreducible subset"). The substrate already has a ready-to-use, ingested substrate for
this test: **CSKG's typed/asymmetric relation subset (IsA, PartOf, Causes, HasPrerequisite, HasSubevent — verified
419,927 rows, 7.3% of CSKG, this session)**, and a **same-day sibling drill already did the hard diagnostic work**
showing the *current* CSKG arena (as used by `additive_map`/KGStore) is 80.5% homophily-dominated because the
induced subgraph over-represents the near-symmetric `RelatedTo`/`Synonym` relations (68.6% of CSKG rows, verified
this session) — and already proposed the exact "relation-diversity re-slice" (v3) that filters toward the typed
subset. That re-slice, extended one hop further into a 2-hop order-reversal split, IS the fair test this task was
asked to find. It did not need to be invented from scratch; it needed to be recognized as the natural extension of
work already in flight.

A second, independent structural argument (not just an empirical design choice) makes this the right target:
**`additive_map`'s relation code `D_r` is a translation VECTOR, and vector addition is commutative** — `X_h + D_r1 +
D_r2 = X_h + D_r2 + D_r1` for ANY trained values of `D_r1`, `D_r2`. This is the *exact same* order-blind-by-
construction flaw that `TRANSITION_OP` was built to fix in the synthetic arena (there: `a⊙b⊙c⊙d` Hadamard-fold;
here: vector-sum composition), now identified in the substrate's own live reasoning architecture. If real 2-hop
CSKG chains exist where order genuinely matters (e.g., a PartOf-then-IsA chain resolves to a different, correct
answer than an IsA-then-PartOf chain over the same two edges), `additive_map` is PROVABLY unable to distinguish
them regardless of how well `X`/`D` are trained — a construction-level bound, not an empirical guess. This gives
`TRANSITION_OP` a concrete, already-in-production target where its mechanism class (not just its synthetic score)
is the thing being tested.

---

## Ranked real-data directed-relation test targets

### 1. CSKG typed-relation 2-hop order-reversal split (BEST — ready-to-build, extends in-flight work)

**What it is:** restrict CSKG to the typed/asymmetric relation subset already verified this session — `/r/IsA`
(107,027 rows), `/r/PartOf` (11,375), `/r/HasSubevent`+`/r/HasFirstSubevent`+`/r/HasLastSubevent` (~15,500 combined),
`/r/HasPrerequisite` (10,696), `/r/Causes` (7,832), `/r/MotivatedByGoal`/`/r/CausesDesire` (~6,700 combined) —
**419,927 rows total, 7.3% of CSKG**, EXCLUDING the near-symmetric/lexical relations (`RelatedTo`, `Synonym`,
`SimilarTo`, `Antonym`, `DistinctFrom`, `EtymologicallyRelatedTo`, `FormOf`, `DerivedFrom` — **68.6% of CSKG**, the
relation family the sibling reachability-audit drill already identified as the homophily-driving culprit, citing Li
et al. 2019 arXiv:1905.05538 on ConceptNet's `RelatedTo` dominance). Build 2-hop and 3-hop composed queries over
this typed subset (e.g. `IsA . PartOf`, `PartOf . HasPrerequisite`) following the standard PathQuery/2p-3p taxonomy
(Hamilton et al. 2018 GQE; Ren et al. 2020 Query2Box, arXiv:2002.05969; Ren & Leskovec 2020 BetaE).

**Fair-test design (the load-bearing part):**
1. **Irreducibility filter (Gregucci et al. 2025, ICML, arXiv:2410.12537 — the single most load-bearing external
   citation this cycle):** they found up to 98% of standard CQA-benchmark multi-hop queries are secretly reducible
   to one 1-hop shortcut, meaning SOTA multi-hop models are silently riding the same frequency signal as plain link
   prediction. Filter the CSKG 2/3-hop query set down to the **irreducible subset only** (no single-hop shortcut
   edge exists; answer set is not just the top-degree entities of the target type) before evaluating anything.
2. **Order-reversal held-out split** (this session's own synthesis of the fair-eval lit-scan's split-design
   recommendation): train on `A∘B` compositions (e.g. all `IsA`-then-`PartOf` chains), TEST on `B∘A` (`PartOf`-
   then-`IsA`) chains over the SAME entity pool — this is the split that makes `TRANSITION_OP`'s actual claim
   (composition order matters) load-bearing rather than incidental, extending CLUTRR's relation-composition-pattern
   split (Sinha et al. 2019) with an explicit order axis.
3. **Frequency/degree floor (must-beat, pre-registered, not a token control):** (a) a per-hop marginal-frequency
   composition baseline (compose the per-relation most-frequent-tail distributions, the natural multi-hop analog of
   CoDEx's single-hop relation-frequency baseline that already matches embeddings on ~40% of FB15k-237, Safavi &
   Koutra 2020 arXiv:2009.07810 — already on file from the same-day reachability-audit note); (b) a degree-product/
   Katz-centrality baseline (Akrami et al. 2020, arXiv:2003.08001, which found this beats embeddings outright on
   WN18RR/YAGO3-10 but NOT on FB15k-237, i.e. CSKG's flatter-degree typed subset is the more favorable regime, by
   direct analogy).
4. **Reuse the SCRAMBLE_REFIT gate already built for the sibling v3 re-slice** (relation-label shuffle + refit; if
   post-shuffle performance stays close to pre-shuffle, the arena is still homophily-carried) as an arena-sanity
   check BEFORE running `TRANSITION_OP` itself — this is infrastructure that already exists in-flight, not net-new
   build.
5. **TRANSITION_OP_SHUFFLED_ORDER diagnostic** (already designed and pre-registered in the synthetic-arena cell,
   `notes/research_brain_asymmetric_directed_relation_operators_2026-07-15.md`) transfers directly: apply the same
   learned per-relation matrices but in a randomly permuted hop-processing order at test time only — if performance
   does not degrade, the "order" signal is coming from somewhere else and the attribution claim is void even if raw
   accuracy looks good.

**Frequency-cap risk: LOW-MODERATE, and explicitly mitigated by design** — the irreducibility filter and
order-reversal split are specifically constructed so a frequency/degree baseline CANNOT solve the task by
construction (per Gregucci et al.'s own diagnosis of why the naive version of this task class fails to discriminate).
Residual risk: CSKG's typed subset may still be too degree-entangled even after filtering (the reachability-audit
note's own brain-grounding section found path-length and degree are never cleanly dissociated in real semantic
networks, Steyvers & Tenenbaum 2005) — report degree-stratified results as a matter of course, not just an aggregate
number.

**Readiness:** data already ingested (`data/grounding_testbed/cskg.tsv.gz`), no new acquisition needed. Directly
extends the v3 relation-diversity re-slice already scoped in
`notes/research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md` (same day, same underlying
data) — this is a follow-up drill on an ALREADY-FLAGGED adjacency (Trigger C, adjacency-cascade), not a fresh probe.

---

### 2. FB15k-237 relation-composition subset via the DihEdral non-abelian framing (SECOND — external validation, name-brand precedent)

**What it is:** Xu & Li 2019 (ACL, "DihEdral: Modeling relation type via non-abelian group representation") built a
KG embedding EXPLICITLY because plain abelian rotation (RotatE, which is what the substrate's FHRR complex bind is
mathematically closest to) cannot capture all relation compositions — this is the closest existing published paper
to `TRANSITION_OP`'s exact hypothesis (composition needs non-commutativity), and it reports per-relation-category
ablations (symmetric/antisymmetric/inversion/composition subsets) on FB15k-237/WN18RR that isolate the
asymmetry-specific gain from aggregate MRR — i.e. the analysis methodology to imitate is already published and
citable.

**Fair-test design:** same recipe as candidate #1 (irreducibility filter + composition-pattern/order-reversal split
+ degree-product floor), applied to FB15k-237's compositional-relation subset instead of CSKG's. Akrami et al. 2020
found FB15k-237 is comparatively LESS degree-capped than WN18RR/YAGO3-10 (a pure degree/Katz baseline beats
embeddings on the latter two, but not FB15k-237) — making it the safer of the two "name-brand" benchmarks if this
route is chosen.

**Frequency-cap risk: MODERATE** — FB15k-237 was specifically constructed (Toutanova & Chen 2015) to remove the
original WN18/FB15k inverse-relation leakage (a trivial "look up the inverse triple in training" rule scored MRR
.963/.660 pre-fix, per Dettmers et al. 2018 ConvE paper, arXiv:1707.01476), but Akrami et al. 2020 showed this fix is
INCOMPLETE — residual near-duplicate and "Cartesian product" relations still let simple rules/degree baselines
dominate parts of the "fixed" dataset. Must run the degree-product baseline explicitly, not assume the 237-relation
filtering already solved it.

**Readiness: LOWER than #1** — not yet ingested in this substrate; would require new data acquisition (public,
small, well-documented download, low acquisition risk, but a real extra step vs. candidate #1's zero-acquisition
readiness).

---

### 3. SIGNOR signed/directed causal-chain data + XSwap-style directed permutation (THIRD — real biology, genuine open gap, higher risk)

**What it is:** SIGNOR 3.0 (Nucleic Acids Research 2023, PMC9825604) is public signed+directed causal-chain
biological data (~8,400 entities, activates/represses edges with path-tracing), surfaced by this cycle's dedicated
bio lit-scan (`notes/research_directed_bio_network_operator_fair_test_2026-07-15.md`, filed independently this same
session). **No published benchmark yet isolates genuine multi-hop order-sensitive chain composition on SIGNOR** —
this is a real, named literature gap (not a dismissed dead end, per the dont-dismiss-adjacent-methods discipline),
but also means there is no existing fair-test infrastructure to reuse; it would need to be built from the XSwap/
edge-prior methodology (Zietz et al., PMC9881952) extended to directed multi-hop chains, which is a bigger design
lift than candidates #1/#2 which reuse existing taxonomies verbatim.

**Frequency-cap risk: HIGH for the single-hop version, UNKNOWN (genuinely open) for the multi-hop version.**
ComHub (Studený & Sonnhammer, BMC Bioinformatics 2021, PMC7871572) directly confirms the degree-dominance trap is
severe for single-hop GRN regulator/target direction — a pure hub/out-degree ranking rivals most sophisticated
DREAM5 inference methods. The dedicated bio lit-scan's own P_deflated for this candidate is 0.30, assessed BEFORE
running the cheap XSwap decisive test it specifies (compute the degree-only edge-prior baseline first, cheapest
possible check). Treat as the highest-upside, highest-uncertainty candidate — genuinely undetermined rather than
pre-judged as closed, but the honest prior (per ComHub) leans toward HARD-FAIL for anything short of the
untested multi-hop chain angle.

**Readiness:** data public and downloadable; XSwap tool is pip-installable; but the multi-hop fair-test methodology
itself is unbuilt (this is the gap, not the data).

---

### 4. Real animal transitive-inference paradigms (naturalistic dominance hierarchies) — BRAIN-GROUNDING ONLY, not a substrate benchmark

Not a candidate for a substrate cell (no digital dataset to ingest), but load-bearing for calibrating whether the
synthetic result should be expected to transfer at all. See Brain-grounding section below.

---

## Candidates explicitly RULED OUT or DEPRIORITIZED as frequency-capped traps (flagged per task instruction)

- **Hypernymy direction detection (WordNet/HyperLex-style "which word is the hypernym")**: the MOST frequency-capped
  candidate found this cycle. Bott, Schlechtweg & Schulte im Walde (ACL Findings 2021, "More than just Frequency?")
  found unsupervised directionality measures (WeedsPrec, invCL, SLQS Row) are highly correlated with raw corpus
  frequency and add little beyond it; classic distributional measures hit ~71% on WordNet pairs, not significantly
  above a frequency-only baseline. Would need a hand-built frequency-matched control split to be usable at all — not
  off-the-shelf. DEPRIORITIZED.
- **Plain single-hop KG link prediction on WN18RR/YAGO3-10**: Akrami et al. 2020 found a pure-degree/Katz-centrality
  baseline BEATS learned embeddings outright on these two benchmarks specifically. DEPRIORITIZED as the primary
  target (FB15k-237's typed-relation subset, candidate #2, is the safer name-brand alternative).
- **Standard multi-hop complex-query-answering (CQA) benchmarks used AS-IS** (BetaE/Query2Box 2p/3p/2i/3i/pi/ip
  splits, no irreducibility filter): Gregucci et al. 2025 showed up to 98% of these queries are secretly one-hop-
  reducible, meaning the naive/published version of this task class is JUST as frequency-capped as plain link
  prediction despite looking multi-hop on paper. This is exactly why candidate #1/#2 specify the irreducibility
  filter as a MANDATORY pre-processing step, not an optional refinement.
- **Citation/patent direction prediction**: genuinely unresolved, not confirmed either way. Zhai, Ozmen & Markovich
  (WWW'25 Companion, arXiv:2502.15008) found asymmetric decoders beat symmetric ones by wide margins on directed
  citation-like graphs, but did NOT ablate against an age/popularity-only baseline — so the apparent win cannot yet
  be attributed to genuine directional signal vs. a confound (older/more-cited papers are systematically the cited
  ones). Flagged as an open gap in the literature itself, not usable as a ready fair-test target without first
  building the missing baseline.
- **Metabolic reaction-direction prediction**: deprioritized not because it's degree-capped but because it's a poor
  mathematical match — reaction directionality is thermodynamics/structure-driven, not a chain-composition-order
  problem; doesn't test the thing `TRANSITION_OP` is for.

---

## Fair-test design (generalized recipe, applies across candidates #1-#3)

Synthesized from the fair-eval methodology lit-scan this cycle:

1. **Existence vs. direction vs. composition are three DIFFERENT tasks with different frequency-cap profiles** —
   don't conflate them. (a) Existence (does an edge exist) is the most degree-dominated; report degree-stratified
   metrics and a degree-preserving-negative-sampling (XSwap/configuration-model) control. (b) Direction (given an
   edge is known to exist, which way does it go) has a built-in control most people miss: a PAIR-frequency baseline
   is at chance (50%) by construction, because both directions of the same pair share identical pair co-occurrence —
   the real confound is PER-ENTITY marginal frequency (e.g. "the more frequent node is always the source"), which
   must be reported as its own explicit floor (per Nguyen et al. hypernymy-directionality baseline methodology,
   arXiv:1707.07273, ~0.70-0.75 direction accuracy from frequency alone). (c) Composition (multi-hop chained query)
   is only genuinely frequency-immune AFTER the irreducibility filter (Gregucci et al. 2025) is applied — the
   un-filtered version is not immune at all, matching the trap in the task's own framing.
2. **Split by pattern/order, not by triple**: CLUTRR-style (Sinha et al. 2019) relation-composition-pattern splits,
   extended here with the order-reversal axis (train `A∘B`, test `B∘A`) specific to testing whether non-commutativity
   was genuinely learned rather than memorized in one direction.
3. **The must-beat floor is the ACTUAL empirical bar, not a formality** — per this session's own repeated finding
   (Costanzo yeast epistasis refute, Hetionet/Zietz AUROC>=0.95, ComHub hub-ranking rivaling DREAM5 methods, CoDEx
   frequency baseline matching ~40% of FB15k-237): across every domain scanned this program has touched, the
   frequency/degree floor is usually STRONG, not a token control. Pre-register it as a first-class gated arm, exactly
   as the same-day `dense_recurrence_gi_detection_cell_design` note already did for the biological case.

---

## Does `additive_map` have a directed-relation target, or is it structurally frequency-capped?

**Answer: it has a genuine target (typed CSKG relations), but the arena it currently trains on is frequency-capped
by construction — and there is a construction-level (not just empirical) reason `TRANSITION_OP`'s mechanism class
could add value there that `additive_map`'s own architecture cannot, regardless of training.**

- `additive_map` (`hdlab/additive_map.py`, MRR 0.128 CHAIN_GRADE per
  `notes/research_additive_map_builder_integration_endgame_2026-07-13.md`) scores via `score(t) = -||X_h + D_r -
  X_t||` — a TransE-style translation model. `D_r` is a learned VECTOR per relation; composing two relations is
  `X_h + D_r1 + D_r2`, which is commutative in `D_r1`/`D_r2` by the algebra of vector addition, full stop, no matter
  how `D_r1`/`D_r2` are trained. This is architecturally incapable of representing "order matters" for ANY two-hop
  chain, which is the SAME diagnosed flaw class as the bilinear-op negative that motivated `TRANSITION_OP` in the
  first place (there: commutative Hadamard fold; here: commutative vector sum).
- The arena `additive_map` was fit and VET-confirmed on is CSKG's induced dense-k-core subgraph — and the SAME-DAY
  sibling drill (`notes/research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md`) found this
  specific arena is 80.5% homophily-carried (SCRAMBLE_REFIT retains 19.5% of the beyond-random margin after a
  relation-label shuffle-and-refit), root-caused to over-representation of the near-symmetric `RelatedTo` relation.
  This means the CURRENT `additive_map` training arena is itself close to the frequency-cap trap this task warns
  against — reinforcing (not just coincidentally matching) why a naive "just run TRANSITION_OP on the existing
  additive_map arena" plan would risk nulling out for the wrong reason.
- **The fix is the same fix**: candidate #1 above (typed-relation-only re-slice + irreducibility filter + order-
  reversal split) is simultaneously (a) the fair test for `TRANSITION_OP`, and (b) the already-proposed v3 fix for
  `additive_map`'s own homophily-dominance diagnosis. One re-sliced arena serves both purposes — build it once.

**Is this task frequency-capped?** Not if built per the design above (typed subset + irreducibility filter + order-
reversal split). It WOULD be frequency-capped if run on the current, unfiltered, dense-k-core CSKG arena as-is
(exactly the trap already diagnosed by the sibling note) — this is the single most important operational warning
this note carries forward.

---

## Brain-grounding: does the brain use successor/transition structure for REAL directed relational inference beyond frequency?

**Two separable claims, and they diverge in an important, honestly-reported way.**

1. **Naturalistic transitive inference (real animal dominance hierarchies) genuinely uses order beyond frequency —
   an existence proof, not a transfer precedent.** Real-world (not lab-abstract-stimulus) transitive-inference
   studies exist: cichlid fish, pinyon jays, and domestic chicks solve rank inference from live social dominance
   contests, correctly inferring relative rank of individuals observed only indirectly/via eavesdropping (Frontiers
   Ecol Evol 2015; Nature Comms Biology 2021) — this is NOT solvable by pure frequency-of-appearance since rank must
   be inferred transitively from indirect pairwise observations. Classical primate TI work (rhesus monkeys, Science
   Advances) is specifically designed to strip frequency/reward-magnitude confounds because the field recognizes
   this as "a nearly ubiquitous confound," and properly-controlled single-neuron recordings do show an abstract
   order representation independent of item-specific value (J. Neurosci 2016). **Important counter-voice, honestly
   reported**: the Betasort model (PLOS Comp Biol 2015) shows implicit value/reinforcement-updating (a
   frequency-like mechanism) can reproduce MUCH of transitive-inference behavior without an explicit order
   representation — the field itself has an active, unresolved value-vs-order debate. This tempers, but does not
   refute, the existence-proof claim: order-beyond-frequency inference is real in naturalistic biological settings,
   but is not cleanly dissociated from frequency/value-learning in every account.
2. **TEM/successor-representation-style non-commutative transition operators have NEVER been tested on real-world or
   naturalistic relational data — this is an explicit, acknowledged gap in the primary literature itself, not
   something this lit-scan failed to find.** The most recent TEM-lineage paper found this cycle (arXiv:2605.15733,
   "Structure Abstraction and Generalization in a Hippocampal-Entorhinal Inspired World Model") explicitly states
   current work "lacks the critical step of inferring shared abstract structure from sequences in continuous and
   real-world environments." Human successor-representation studies (2024 biorxiv) also stay within controlled lab
   graph-learning tasks. **This means the synthetic arena's `TRANSITION_OP` win is grounded in real, well-replicated
   biology (TEM's `W_a` matrices, the grid-cell path-integration group-representation theorem) but that biology
   itself has never been shown to transfer to real-world/naturalistic relational graphs** — the real-data test
   proposed in this note is therefore a genuinely NOVEL transfer test, not a literature-confirmed one. This is the
   single most important calibration fact for the P_deflated figure below: it justifies treating the real-data
   extension as full novel-synthesis (capped at 0.50), not a lit-precedented transfer with a higher ceiling.

**Net read:** the brain literature supports "genuine order-beyond-frequency relational inference exists in real
biological settings" (candidate #4, existence proof) but does NOT supply a validated bridge from TEM-style
non-commutative operators to real-world relational data (an open gap the field names itself) — so expect the
CSKG/FB15k-237 real-data test to be informative regardless of outcome (closes or opens that literature gap in this
substrate's own domain), rather than a high-confidence expected replication of the synthetic win.

---

## Falsifiable predictions

**HARD-PASS (candidate #1, CSKG typed-relation 2-hop order-reversal split):** on the irreducibility-filtered,
order-reversal-held-out split, `TRANSITION_OP` beats BOTH (a) the per-hop marginal-frequency-composition baseline
and (b) the degree-product/Katz baseline by a pre-registered margin (recommend >=15-20%, matching the module-registry
standard margin used elsewhere this session, e.g. `dense_recurrence_gi_detection_cell_design`'s 25-30% bar,
deflated somewhat here for a first cross-domain transfer), AND `TRANSITION_OP_SHUFFLED_ORDER` degrades performance
by >=0.20 relative to `TRANSITION_OP` (confirming order-sensitivity is genuinely load-bearing, not decorative), AND
the SCRAMBLE_REFIT arena-sanity gate confirms the re-sliced arena itself is not homophily-dominated
(`rel_specific_frac >= 0.30`, reusing the sibling v3 threshold verbatim).

**HARD-FAIL:** `TRANSITION_OP`'s margin over the degree-product/frequency-composition floor is `<=0.05` (ties within
noise), OR the `TRANSITION_OP_SHUFFLED_ORDER` ablation shows NO meaningful degradation (order-sensitivity claim
void even if raw numbers look fine), OR the SCRAMBLE_REFIT gate fails on the re-sliced arena itself (meaning even the
typed-relation subset remains homophily-carried, and no fair test was actually run). Any of these three would be a
clean, informative negative — matching this program's own repeated real-data pattern (Costanzo refute, Hetionet
AUROC>=0.95, CoDEx ~40% frequency-explained) rather than an anomaly.

**MIDDLE_BAND (most likely per the honest calibration below):** `TRANSITION_OP` beats the frequency/degree floor
by a modest, sub-threshold margin (consistent with Safavi & Koutra's finding that even "clean" real KG benchmarks
carry substantial-but-not-total frequency-explainable signal), OR clears the margin on 2-hop but not 3-hop
compositions, OR clears the accuracy bar but the SHUFFLED_ORDER diagnostic shows only partial degradation. Report
per-sub-condition, do not average into one global verdict, per the same discipline already applied in the synthetic
arena's design.

---

## Cheap decisive test (pre-build, before any full cell)

Before building the 2-hop composition cell: compute the degree-product/frequency-composition floor's AUPRC/accuracy
ALONE on the irreducibility-filtered, order-reversal split first — no `TRANSITION_OP` or `additive_map` training
needed yet. If this floor alone already clears most of the achievable ceiling (analogous to the Zietz/Hetionet
precedent), that immediately calibrates how hard `TRANSITION_OP`'s bar really is, cheaper than discovering it after
a full multi-arm build. This mirrors the identical cheap-test discipline already applied in
`research_dense_recurrence_gi_detection_cell_design_2026-07-15.md` for the biological case.

---

## Cross-thread synthesis

- Directly extends (Trigger C, adjacency-cascade) `notes/research_reachability_audit_arena_selection_vs_fundamental_null_2026-07-15.md`
  — that note diagnosed CSKG's current dense-k-core arena as 80.5% homophily-carried and proposed a v3
  relation-diversity re-slice; this note identifies that SAME re-slice, extended one hop into an order-reversal
  split, as the fair test for `TRANSITION_OP`. One build serves both open threads.
- Directly extends `notes/research_brain_asymmetric_directed_relation_operators_2026-07-15.md` — that note designed
  and VET-pending `TRANSITION_OP` on the synthetic dominance arena; this note is the "next-drill candidate" it
  itself named (multi-hop composition connecting to `hdlab/additive_map.py`), now made concrete with a specific
  dataset, split, and baseline.
- Reuses the fair-test/degree-baseline discipline established this same day in
  `notes/research_dense_recurrence_gi_detection_cell_design_2026-07-15.md` (Zietz XSwap floor as a first-class,
  not token, arm) and generalizes it to the KG/citation domains via this cycle's own external lit-scans.
- Independently corroborated by a fifth (self-dispatched) lit-scan agent this cycle,
  `notes/research_directed_bio_network_operator_fair_test_2026-07-15.md`, which reached the same qualitative
  conclusion for biological GRN data specifically (degree/hub dominance is real and severe for single-hop direction;
  multi-hop signed-chain composition on SIGNOR is the one untested, genuinely open angle) — convergent evidence
  across two independently-dispatched cycles that single-hop real-data direction prediction is frequency-capped
  almost everywhere checked, and multi-hop/compositional structure is the only class that structurally escapes it.
- Extends the June 2026 GHRR non-commutative-bind pilot and the July 14 "unifies symmetric/asymmetric binding"
  drill's still-open unification question — a real-data `TRANSITION_OP` result (either direction) feeds directly
  back into whether one operator can cover both parity-preserving and order-sensitive relational tasks.

---

## Substrate-product implications

- If candidate #1 clears HARD-PASS: this would be the program's FIRST real-data confirmation that a brain-grounded,
  order-sensitive-by-construction operator adds value beyond both a frequency floor AND the substrate's own existing
  reasoning architecture (`additive_map`) on data already in production use — directly de-risking the "is this just
  synthetic-arena theater" question for the entire non-commutative-bind research thread, and giving `additive_map`
  a concrete, construction-level-motivated upgrade path (order-sensitive multi-hop composition) rather than a vague
  "improve it" mandate.
- If HARD-FAIL: this closes the "TRANSITION_OP transfers directly to real KG multi-hop composition" question
  cleanly and for a specific, literature-grounded reason (either residual degree-entanglement even in the
  typed-relation subset, or the order-sensitivity mechanism not mattering once irreducibility is enforced) — the
  substrate-product framing would then correctly narrow `TRANSITION_OP`'s validated scope to "a working synthetic
  construction-proof for order-sensitive composition, not yet shown to transfer to this program's real ingested
  data," which is itself a useful, honest scoping result (same value class as this session's other real-data
  refutes).
- Either way, this note converts "real-data test for TRANSITION_OP" from an open, potentially-frequency-cap-trapped
  question into a SPECIFIC, pre-registered, ready-to-build cell design that reuses data, infrastructure (SCRAMBLE_REFIT
  gate, TRANSITION_OP_SHUFFLED_ORDER diagnostic), and split methodology already proven or in-flight elsewhere in the
  program this same week — the cheapest possible path to a real-data answer.

---

## Citations (verified count: ~30 across 5 lit-scan sub-agents + internal data audit this cycle)

**KG asymmetric-relation angle (this cycle, ~9):** Hamilton et al. 2018 (GQE, NeurIPS); Ren, Hu & Leskovec 2020
(Query2Box, arXiv:2002.05969); Ren & Leskovec 2020 (BetaE); Gregucci et al. 2025 ("Is Complex Query Answering Really
Complex?", ICML, arXiv:2410.12537 — the most load-bearing new citation this cycle); Xu & Li 2019 (DihEdral, ACL);
Sun, Deng, Nie & Tang 2019 (RotatE, ICLR, arXiv:1902.10197); Akrami, Saeef, Zhang, Hu & Li 2020 (SIGMOD,
arXiv:2003.08001); Toutanova & Chen 2015 (FB15k-237, ACL workshop); Dettmers, Minervini, Stenetorp & Riedel 2018
(ConvE/WN18RR, AAAI, arXiv:1707.01476).

**Fair-eval / degree-bias methodology (this cycle, ~8):** Sun et al. 2020 (re-evaluation of KGC methods, ACL,
arXiv:1911.03903); Akrami et al. 2020 SIGMOD (realistic re-evaluation); ICML 2025 implicit-degree-bias paper
(arXiv:2405.14985); edge-existence-degree baseline paper (PMC); Zietz, Himmelstein, Kloster et al. 2024 (XSwap,
GigaScience, PMC9881952/9); BMC Biology 2025 negative-sampling paper (PMC12080959); Nguyen et al. hypernymy
directionality (arXiv:1707.07273); Sinha et al. 2019 (CLUTRR).

**Biological directed-network angle (independently filed sub-agent this cycle, ~8):** Zietz et al. (XSwap/edge-prior,
PMC9881952); `hetio/xswap` tool; Studený & Sonnhammer, ComHub (BMC Bioinformatics 2021, PMC7871572); Bayesian Copula
Directional Dependence on DREAM5 (arXiv:2606.29402, flagged unverified); Chevalley et al., CausalBench (Comm. Biology
2025); SIGNOR 3.0 (NAR 2023, PMC9825604); DREAM5 challenge data; dGPredictor/metabolic-direction literature
(deprioritized as poor match).

**Temporal/citation/narrative ordering angle (this cycle, ~7):** Zhai, Ozmen & Markovich (WWW'25 Companion,
arXiv:2502.15008); PTNS patent-citation (Sci Reports 2024); Chambers & Jurafsky 2008 (narrative chains); Narrative
Event Evolutionary Graph (arXiv:1805.05081); temporal-relation-extraction baseline paper (arXiv:1909.00429);
Order-Based Pre-training for procedural text (arXiv:2404.04676).

**Brain-grounding, naturalistic transitive inference + TEM real-world-transfer gap (this cycle, ~6, plus carried
citations from the earlier same-week TEM/GHRR drill not re-counted here): Whittington et al. 2020 (TEM, Cell,
carried); "Structure Abstraction and Generalization..." (arXiv:2605.15733 — the load-bearing new citation, explicit
real-world-transfer gap statement); "Trial-by-trial learning of successor representations..." (2024 biorxiv); Reward
associations do not explain TI in monkeys (Science Advances); Betasort model (PLOS Comp Biol 2015); naturalistic TI
in social animals (Frontiers Ecol Evol 2015; Nature Comms Biology 2021).

**Internal data audit (this session, verified directly off disk):** `data/grounding_testbed/cskg.tsv.gz` relation
distribution — total 5,748,411 rows; typed/asymmetric subset (`IsA`, `PartOf`, `Causes`, `HasPrerequisite`,
`HasSubevent`+variants, `MotivatedByGoal`, `CausesDesire`) = 419,927 rows (7.31%); near-symmetric/lexical subset
(`RelatedTo`, `Synonym`, `SimilarTo`, `Antonym`, `DistinctFrom`, `EtymologicallyRelatedTo`, `FormOf`, `DerivedFrom`) =
3,940,530 rows (68.55%) — corroborates the sibling reachability-audit note's ConceptNet-`RelatedTo`-dominance
diagnosis with an exact count. `hdlab/additive_map.py` and
`notes/research_additive_map_builder_integration_endgame_2026-07-13.md` read directly for the TransE-style
`score(t) = -||X_h + D_r - X_t||` construction and its commutative-composition property.

---

## P_deflated

**Per-candidate (lit-scan calibration penalty applied, 0.15-0.25 deflation, novel-synthesis capped at 0.50 — applied
more aggressively here than the synthetic-arena note because, per the brain-grounding section, there is NO literature
precedent for TEM-style operators transferring to real-world relational data; this is a genuinely novel transfer,
not a lit-confirmed one):**

- Candidate #1 (CSKG typed-relation order-reversal split) clears HARD-PASS: base intuition ~0.45 (strongest
  readiness — data already ingested, infrastructure partially built via the v3 sibling drill, a real
  construction-level argument for why `additive_map` cannot already solve this) — deflated to **0.30** (below the
  0.50 cap; no real-data precedent exists yet for this exact transfer, and the brain-grounding section's honest
  finding that TEM-style operators have never been tested on real-world data pulls this down further than the
  synthetic-arena note's own 0.48 for `TRANSITION_OP` in-arena).
- Candidate #2 (FB15k-237 DihEdral-style subset) clears HARD-PASS: base intuition ~0.35 (good external precedent via
  DihEdral's own published composition ablations, but requires new data acquisition and does not benefit from the
  in-flight v3-arena synergy) — deflated to **0.22**.
- Candidate #3 (SIGNOR multi-hop signed chain) clears HARD-PASS: **0.20** (carried from the independently-filed bio
  sub-note's own P_deflated=0.30, further discounted here because the multi-hop fair-test methodology itself is
  unbuilt, a genuinely open gap rather than a ready-to-run design).

**Overall (candidate #1, the recommended primary target, clears HARD-PASS): P_deflated = 0.30.**

**MIDDLE_BAND is the single most likely outcome across all three candidates**, consistent with this program's
repeated real-data finding this week (Safavi & Koutra's ~40%-frequency-explained even in "clean" FB15k-237; Zietz's
AUROC>=0.95 degree floor in comparable networks; the yeast-epistasis additive-capturable refute) — a modest,
sub-threshold beyond-frequency margin is the honest expected outcome, not a disappointment relative to HARD-PASS.

## Next-drill candidate

If candidate #1 is built and clears MIDDLE_BAND or better: the natural follow-up is whether the SAME order-reversal-
split methodology, applied to `additive_map`'s live production arena (not just a held-out research cell), motivates
a genuine architecture change (replacing the commutative vector-sum composition with a `TRANSITION_OP`-style
sequential non-commutative chain) — this would move the result from "a research cell shows a possible improvement"
to "the live reasoning architecture's composition operator should change," which is the natural bridge back to the
currently-active AdditiveKGMap improvement thread. Per the field advisor, this also sits on the
`network-science-graph-theory` Tier-1b adjacency for a graph-scale follow-up (spectral/expander bounds on how much
relation-type diversity a subgraph needs before `rel_specific_frac` reliably clears 0.30 without per-arena Monte
Carlo, replacing empirical re-slicing with a predictive design rule).
