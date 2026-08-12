# Research: brain-faithful rescue for the CSKG store scale wall (2026-08-09)

Filed by: research (Sonnet), deep brain-fidelity drill triggered by the USER's direct question after
Stage-2C's resonator-capacity-rescue HARD_FAIL: "we know the brain works, so are we going after the
problem in the right way?" Foreground, no sub-agent dispatch, per task instruction. KB-checked first
(`substrate_query.sh` x2, both hit real prior art, extended below not rediscovered); read
`notes/research_content_causal_associative_knowledge_store_2026-08-09.md` and
`notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md` per instruction (both
extended, not repeated); disk-read `hdlab/kg_traversal.py`, `hdlab/cleanup_family.py`,
`hdlab/situation_focus.py`, `hdlab/selection_weighted_sharded_typer.py`, `hdlab/hippocampal_encoder.py`,
`data/capability_registry.jsonl`, and three already-landed community-routing experiment cells before
writing a word of theory. 5 live WebSearch lit-scans done directly (generic neuroscience terms only,
per query-privacy discipline).

## HEADLINE

**No, wall #2 was not attacked the right way, and the substrate already possesses the right-way fix,
built and HARD_PASS-certified three times over, sitting unused two doors down from the store that just
failed.** Resonator factorization is an engineering trick for a problem CSKG's entity IDs do not
actually have (joint decomposition into independent semantic factors) borrowed to solve a problem they
do have (too many candidates crosstalk-corrupting one shared matrix) -- and the substrate's own prior
cert already told us this trick craters past K=2 basins at realistic per-factor codebook size (K3=0.613,
K4=0.047 at M=30; this cycle's addendum shows the SAME collapse at K=2 once M_SUB grows to 1024). The
biology is unambiguous and, unusually for this program, ALREADY FULLY WORKED OUT in-substrate: a
2026-07-08 brain-first design note (`notes/research_reasoning_over_large_store_without_collapse_brain_
first_2026-07-08.md`, never before connected to this cycle's KGStore rescue) diagnosed this exact
class of problem -- "additive-store crosstalk wall, M < N/(2 ln V)" -- and named FOUR compounding brain
mechanisms, the load-bearing one being **community-bounded two-stage retrieval** (route to a bounded
context/community shard FIRST, decode only within it). That mechanism was BUILT and independently
HARD_PASS-certified three times (`exp_community_bounded_retrieval_scale_invariance_v1`,
`exp_community_of_communities_nested_retrieval_v2`, `exp_community_routed_glassbox_reasoning_scale_v1`)
on a synthetic analog of exactly KGStore's collapse curve (fidelity 0.742->0.039->0.000->0.000 as V
scales 580->58,000 for the flat control -- the SAME shape as KGStore's measured 0.967->0.700->0.000
collapse from 1K->10K->30K) -- and the treatment arm stayed FLAT (1.000/1.000/1.000/0.996) across the
same 100x range. **This is not a hypothesis to test; it is an already-passed test that has never been
pointed at the store that needs it.** The genuinely open, honestly-untested part is narrower than
"does sharding work" (answered: yes) -- it is "does a REAL, cheaply-available CSKG shard key (not the
synthetic planted communities the certified cells used) survive contact with KGStore's actual Hebbian-W
crosstalk," a question the substrate's own `exp_graph_community_detection_v1` (HARD_FAIL on
generic modularity clustering) already warns against answering with automatic community detection.

## 1. The four biology questions, answered

### Q1 -- capacity lever = sparsity. CONFIRMED, already quantified in-substrate.

KGStore's `W = zeros(n_dim, n_dim)`, `W += outer(E[o], key)/n_dim` for every triple, with `E` DENSE
bipolar `{-1,+1}` (`hdlab/kg_traversal.py:55-59, 79-80`, read this cycle) is textbook classical-Hopfield/
Willshaw territory in the DENSE regime: capacity `~0.14 N` patterns (Hopfield 1982), matching
`hdlab/cleanup_family.py::classical_hopfield`'s own docstring ("Capacity ~0.14 * D"). The empirical
cliff (HARD_PASS through 10K, HARD_FAIL by 30K triples into a [1024,1024] W) is the same phenomenon at
a higher constant (KGStore's task is hetero-associative key->value binding, not literal pattern storage,
so its cliff sits above the raw 0.14N=143 pure-Hopfield number, but the SAME dense-regime `~N/(2 ln V)`
order-statistic scaling law governs it -- `notes/research_reasoning_over_large_store_without_collapse_
brain_first_2026-07-08.md` names this exact inequality as the mechanism, independently of today's drill).
Sparse coding breaks this scaling class, not just its constant: Willshaw, Buneman & Longuet-Higgins
(1969) sparse binary associative nets achieve `~N^2/(log N)^2` capacity at optimal sparsity
`k~log(N)`; Treves & Rolls (1991) extend this to graded-response recurrent nets and, applied to CA3
with measured sparseness `a~0.003` and `~20%` connectivity, estimate `~20,000` autoassociatively-stored
memories for CA3a (live-verified this cycle: multiple independent sources converge on this number and
mechanism). Kanerva's Sparse Distributed Memory (1988, live-verified this cycle) independently arrives
at the same design principle from a different direction: an address DECODER first projects the cue into
a much HIGHER-dimensional space (`W >> A` neurons) before applying sparse coding, exactly mirroring
dentate gyrus's `~10-100x` EC->DG expansion (`notes/design_stage2_concept_encoder_spoke3_sparse_
hippocampal_pattern_separation_one_shot_2026-07-02.md`, already on disk) -- expand FIRST, then
sparsify, never sparsify by naive collision-minimizing sampling (the falsified 2026-06-23
`sparse_engram_allocation` mechanism, explicitly avoided by design in both that note and in the
already-BUILT `hdlab/hippocampal_encoder.py`, verified this cycle: `DGProjection.encode` expands then
top-K-sparsifies by magnitude; `CA3AutoAssociator.write` does `W[nz,nz] += outer(code[nz],code[nz])` --
literally only the nonzero (sparse, ~1-2%) indices pay crosstalk cost, the Willshaw mechanism verbatim).
**KGStore's DENSE bipolar code is the wrong regime; the faithful sparse alternative already exists in
code (`hdlab/hippocampal_encoder.py`) but has never been wired to KGStore, never measured at CSKG scale,
and is not in `data/capability_registry.jsonl`** -- a genuine, disclosed gap, not a speculative fix.

### Q2 -- never-a-flat-store = modularity. CONFIRMED, with a sharper mechanism than "just modular."

Live-verified this cycle: the hippocampus itself does not hold literal content in one recurrent matrix.
Teyler & DiScenna's (1986) hippocampal memory indexing theory, updated as Teyler & Rudy (2007) and
extended by Moscovitch's multiple-trace theory (2016) -- all independently confirmed this cycle via
search and already cited in more depth in the 2026-07-08 in-substrate note -- hold that the hippocampus
stores a **sparse INDEX/pointer**, not the episodic content itself; content is distributed across
neocortex, and a partial cue reactivates the index, which pattern-completes the distributed cortical
activity. This is a stronger claim than "storage is spread across several modules" -- it is a two-level
architecture where the INDEX (itself small and capacity-bounded, ~20,000-scale per the Treves-Rolls
CA3a estimate above) never equals the CONTENT VOLUME, because the index only ever holds POINTERS.
Complementary Learning Systems theory (McClelland, McNaughton & O'Reilly 1995, already cited
in-substrate) adds the fast-hippocampus/slow-cortex split; live-verified this cycle: schema-dependent
hippocampal-neocortical connectivity persists during and after encoding (PNAS 2010), and functional
specialization runs along the hippocampal long axis (posterior = fine/local detail, anterior =
coarse/gist -- Poppenk et al. 2013, cited in the 2026-07-08 note, corroborated by this cycle's live
search of the "details, gist and schema" review literature). **KGStore's single [1024,1024] W is
currently playing BOTH roles at once -- index AND content -- in one dense matrix, which is exactly the
configuration the brain never uses.**

### Q3 -- the selector = context-gated shard selection, and YES, walls #1 and #2 are the SAME wall.

This is the load-bearing finding of this drill, and it converts from hypothesis to ALREADY-MEASURED
fact via the 2026-07-08 note's mechanism (thread 4: "modular/small-world community structure... the
one true scale-invariance mechanism among the four"). Its argument, restated precisely: in the crosstalk
inequality `M < N/(2 ln V)`, `V` is "the size of the codebook the decode has to discriminate against."
A FLAT retrieval makes `V` = total store size, unboundedly growing. A TWO-STAGE retrieval -- (1) coarse
route to the correct community/shard via a small, near-orthogonal pointer codebook (size `~sqrt(V)` or
`~log V`), THEN (2) fine-decode restricted to only that shard's bundle -- makes the `V` that matters for
crosstalk math the ACTIVE SHARD SIZE, which can be held roughly constant by adding more shards as the
store grows, rather than growing each shard. Schapiro, Rogers, Cordova, Turk-Browne & Botvinick (Nature
Neuroscience 2013, cited in the 2026-07-08 note) show the hippocampus does not just sit atop a
community-structured graph passively -- it ACTIVELY reorganizes its own representations to reflect
latent community boundaries in a continuous experience stream, i.e. the brain is doing the shard-key
DISCOVERY, not just shard-key USE. Dentate gyrus pattern separation is the literal SHARD-KEY /
ADDRESS-DECODER computation (Kanerva's address decoder, Q1, is the same math): a coarse, discriminative
code that routes a cue to the right index region before any fine matching happens.

**Direct connection to this program's own Stage-1.5 result (`data/exp_focus_pullin_causal_stage15_
salted_cardinality_gate_v1/metrics.json`, re-read this cycle): the CONTEXT-CONDITIONED arm there IS a
one-stage instance of exactly this mechanism** -- `ctx_key = bind(AGENT_filler, TENSE_filler)` per
cluster, rank all candidates by raw dot-product against the probe's own `ctx_key`, take `K_SHORTLIST=20`,
THEN run the expensive `iterative_attractor` settle only on the shortlist. That measured
`false_pull_in_rate = 0.000` at every scale up to M=100,000 (vs the FLAT arm rising with M as EVT
`sqrt(2 ln M)` order-statistics predicts) is the SAME community/index-routing mechanism, applied to
EVT false-admission (wall #1) rather than to storage-write crosstalk (wall #2). **Honest but important
distinction, not glossed over**: Stage-1.5's context-gate narrows the CANDIDATE SET at READ time from a
SHARED pool; it does not shard WHERE items get WRITTEN. Wall #2 is a write-side crosstalk problem
(triples corrupting each other inside one shared W regardless of how narrowly you later search); a
read-time shortlist over a corrupted W does not by itself fix a corrupted W. The composition that DOES
fix both simultaneously -- and that the certified `exp_community_bounded_retrieval_scale_invariance_v1`
already tested end-to-end (its TREATMENT arm routes at BOTH ingest-adjacent construction and query time,
via per-community bound bundles, not just query-time filtering) -- is context/community determining
WHICH physical store (shard) a triple is written into in the first place, not merely which candidates
get scored at read time. **Verdict on Q3: yes, walls #1 and #2 are the same underlying wall (an
unbounded-`V` discrimination problem) manifesting on two axes (read-time competition; write-time
crosstalk), and ONE brain mechanism -- context/community-gated shard selection, applied at BOTH ingest
and query time -- is the biologically and empirically supported fix for both**, with the important
caveat that only the read-time half (wall #1) has been validated on THIS program's own micro-world data;
the write-time half (wall #2) has been validated on a SEPARATE synthetic community-structured KB
(the certified cells), not yet on KGStore or CSKG specifically.

### Q4 -- the readout = CA3 attractor completion, NOT alternating resonator factorization.

Confirmed via live search this cycle and via direct code inspection. `hdlab/cleanup_family.py::
iterative_attractor`'s own docstring: "Brain-canonical via CA3 / DG attractor dynamics (Treves-Rolls)"
-- this is the ALREADY-OWNED, already-labeled-brain-canonical primitive: a recurrent auto-associator
(Marr 1971; Hopfield 1982; Treves & Rolls 1991/1994) that does ONE-SHOT Hebbian writes and settles a
noisy/partial cue toward its nearest stored attractor via cosine-weighted iterative relaxation. This IS
the accepted biological model of hippocampal pattern completion; nothing in the live search surfaced any
claim that CA3 (or any other brain structure) performs multi-factor alternating unbind-and-cleanup
search. Resonator networks (Frady, Kent, Olshausen & Sommer, *Neural Computation* 2020, Parts 1 & 2;
live-verified this cycle) solve a DIFFERENT computational problem -- joint FACTORIZATION of a bound
composite into multiple independent semantic factors (e.g. object identity x pose in a visual scene) --
and are explicitly framed in the literature as an alternative to gradient-based/ALS OPTIMIZATION
algorithms, not as a model of biological memory retrieval. The live search did surface a biological-
PLAUSIBILITY claim (resonator dynamics can be implemented with resonate-and-fire spiking neurons,
neuromorphic hardware) -- this is an IMPLEMENTATION-SUBSTRATE claim (resonator math *could* run on
spiking hardware), categorically different from an EMPIRICAL claim that this is what hippocampal
retrieval actually does; no such empirical claim was found, and CA3's auto-associative account remains
the field's standard model with decades of lesion, connectivity, and computational-modeling support
(Q2's citations). More concretely damning for THIS specific use: CSKG's entity IDs are not a
semantically factored joint code -- the K_ENT=2 digit-split (`id // 1024`, `id % 1024`) that Stage-2C
used was an ARBITRARY radix-encoding trick imposed purely to shrink per-decode candidate count, with
zero grounding in the store's actual semantic structure. Applying a factorization algorithm to an
un-factored problem, to solve what is actually a CAPACITY problem, is importing the wrong tool class --
and the substrate's own prior cert (`exp_resonator_factorization_v1`: K2=1.000, K3=0.613, K4=0.047 at
M=30) plus this cycle's addendum (hard-commit collapse 93%->2% as M_SUB grows 16->1024 even at K=2,
zero noise) had ALREADY, twice, independently flagged that alternating-search basin-convergence is the
substrate's OWN documented failure mode at exactly this kind of candidate-pool size -- this was a
known, named risk before Stage-2C shipped, not a surprise. **Verdict on Q4: no neural correlate for
alternating multi-factor resonator search as a memory-retrieval mechanism; CA3 attractor completion
(already owned, already used inside the certified community-routing cells) is the biologically and
empirically supported readout.**

## 2. Owned-organ map (verified by reading code, not by label)

| Biology finding | Owned organ | Verified fit | Gap |
|---|---|---|---|
| Sparse expand-then-sparsify DG code + Marr/Willshaw CA3 auto-associator | `hdlab/hippocampal_encoder.py` (`DGProjection`, `CA3AutoAssociator`, `HippocampalEncoder`) | Exact -- read the source: expansion-then-top-K-magnitude-sparsify, sparse-indices-only outer-product write (`W[nz,nz] += outer(...)`), explicit anti-2026-06-23-HF design discipline in the docstring | **Never wired to KGStore, never measured at any real KG scale, absent from `data/capability_registry.jsonl` entirely** (grep confirmed zero registry rows, zero importing files in `experiments/` or `hdlab/`) -- built and self-tested, then abandoned mid-pipeline |
| Community/context-gated two-stage shard routing (index-not-content + activate-only-relevant-community) | `experiments/exp_community_bounded_retrieval_scale_invariance_v1.py` + `exp_community_of_communities_nested_retrieval_v2.py` + `exp_community_routed_glassbox_reasoning_scale_v1.py` | Exact mechanism match to Q3's biology, and ALREADY HARD_PASS-certified 3x (verified via metrics.json this cycle: `rd=0.000` treatment vs `rd=1.000` control at the first cell; nested 2nd tier bounds decode to `~sqrt(L)` at the second; glass-box routing audit intact at the third) | **Never promoted to an `hdlab/` organ** (unlike `selection_weighted_sharded_typer`, which explicitly documents itself as "DG/CA3-style pattern-separated shards" and IS promoted/WIRED) -- lives only in `experiments/`, and validated on a SYNTHETIC planted-community KB, never on KGStore or real CSKG data. `exp_graph_community_detection_v1` (HARD_FAIL, `comm=0.625` ambiguous) shows automatic community discovery on a real graph is NOT a safe default shard-key source for this substrate |
| CA3 attractor pattern completion (fine-decode readout within a shard) | `hdlab/cleanup_family.py::iterative_attractor` (wraps `hdlab/iterative_attractor.py::iterative_cleanup`) | Exact -- docstring self-identifies as Treves-Rolls CA3/DG-canonical; already the readout Stage-1/Stage-1.5/Stage-2b use | None for the readout step itself; needs to operate on a SHARD-restricted codebook, not the full flat entity codebook (an integration change, not a mechanism change) |
| Context/community-key -> restrict candidate pool BEFORE expensive readout | `hdlab/selection_weighted_sharded_typer.py` (`SelectionWeightedShardedTyper`, WIRED, self-documented as "biased-competition attention... over hippocampal DG/CA3-style pattern-separated shards", Desimone & Duncan biased-competition citation) + Stage-1.5's `pull_in()`-adjacent context-gate pattern (validated, not yet promoted to hdlab) | Strong -- this is a THIRD independent already-built instance of the same shard-then-score architecture, currently scoped to small-cue pragmatic-construction typing (n_train=40) rather than large-KB entity retrieval | Needs a KG-scale adaptation (its per-cue/per-shard LOO-weighting formulas assume a handful of shards over a small labeled training set, not hundreds of thousands of unlabeled entities) -- a genuine, disclosed scaling gap between "this pattern works" and "this pattern works at CSKG's 482,588-entity scale" |
| Monolithic dense Hebbian store (the thing that failed) | `hdlab/kg_traversal.py::KGStore` | N/A -- this is the organ BEING replaced/extended, not reused as-is | Needs to become K parallel `KGStore`-shaped shards (`W_0...W_{K-1}`, each with its own or a shared entity codebook restricted to that shard's members) selected by a coarse context key at both ingest and query time |

## 3. Recommended brain-faithful rescue architecture (ONE, composing four already-validated pieces)

**Two-level, context/community-gated, sparsely-coded, CA3-attractor-read shard store.** In order of
what changes relative to today's `KGStore`:

1. **Shard the store, not just the search** (the Q3 fix, reusing `exp_community_bounded_retrieval_
   scale_invariance_v1`'s certified TREATMENT architecture, generalized from its synthetic bound-bundle
   store to KGStore's Hebbian-matrix store -- mathematically the same additive-superposition crosstalk
   class, verified this cycle by reading both stores' update rules). Replace ONE `[1024,1024]` `W` with
   `K` shard matrices `W_0..W_{K-1}`. **Concrete, disclosed shard-key choice for CSKG specifically**
   (NOT generic graph-community detection, which `exp_graph_community_detection_v1` already showed
   HARD_FAILs on this kind of graph): use CSKG's own already-measured, zero-new-cost source-relation
   family tags (AT=ATOMIC, CN=ConceptNet, VG=VisualGenome, WN/WD/FN, per `notes/research_content_
   causal_associative_knowledge_store_2026-08-09.md` section 1's already-measured edge counts) or the
   already-computed k-core density band (`kcore>=12` dense-core vs periphery, per the same note's
   section 6) as the coarse routing key -- both are CHEAP, ALREADY ON DISK, and sidestep the failed
   automatic-community-detection dependency entirely.
2. **Route via a small, near-orthogonal community-pointer codebook FIRST** (the coarse-select stage of
   the certified cells; size `~K` or `~sqrt(V)`, a single argmax lookup, not iterative).
3. **Sparse-code entities WITHIN each shard** (the Q1 fix, wiring `hdlab/hippocampal_encoder.py`'s
   `DGProjection` + `CA3AutoAssociator` in place of KGStore's dense bipolar `E`/`W` for the shard's
   local store) -- this is the CAPACITY-PER-SHARD lever, complementary to (not a substitute for) the
   SHARD-COUNT lever in step 1. Stacking both means each shard individually never approaches even the
   dense-Hopfield cliff, and the number of shards can grow without bound as the KB grows.
4. **Read out via `iterative_attractor` (CA3 attractor completion) restricted to the selected shard**
   (the Q4 fix) -- never resonator/alternating-factorization search, which has no biological warrant
   here and has now twice documented its own basin-proliferation collapse in this exact substrate.

This is a COMPOSITION of four pieces that are each independently owned and independently validated
(three of the four already HARD_PASS-certified, one self-tested-but-unwired) -- the genuinely NEW,
untested part is narrower than a fresh mechanism: it is (a) this specific four-way composition, and
(b) whether a REAL CSKG shard key (source-relation-family or k-core band, not the certified cells'
planted synthetic communities) preserves the certified flat-fidelity result on KGStore's actual
482,588-entity, 1.24M-edge graph.

## Cheap decisive test / can-fail design (DESIGN ONLY -- not run this cycle)

Reuses `exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1`'s exact baseline harness (imported, bit-
identical reproduction discipline already established by Stage-2C) plus `exp_community_bounded_
retrieval_scale_invariance_v1`'s two-stage routing pattern, ported from its synthetic bound-bundle store
onto real `KGStore` shards.

**Design**: partition the real CSKG spine into `K` shards by source-relation-family (cheapest, already-
measured shard key named above; a second arm repeats with k-core-band as the shard key, since which of
the two real keys actually preserves community structure is itself an open, disclosed empirical
question, not assumed). Build `K` separate `KGStore` instances (one per shard, each sized to its actual
membership, expected `K` in the 5-10 range given CSKG's 6 named source families). Route each of Stage-
2B's SAME 150 relevant + 150 negative probe queries via (a) a coarse argmax against `K` shard-centroid
pointer vectors, THEN (b) `predict_one_hop`/`predict_one_hop_topk` restricted to the selected shard's
`(E_shard, W_shard)` only. Sweep the SAME six cardinality rungs Stage-2B already measured
(1000/5000/10000/30000/100000/1213912 -- reusing the exact imported constants, per the arms-differ /
bit-identical-baseline discipline this program already enforces). ONE variable changed per arm:

- **ARM_FLAT (control, must reproduce the known collapse)**: Stage-2B's unmodified single-`W` baseline,
  re-run fresh at every scale (bit-identical-reproduction check against the already-landed metrics.json,
  same discipline Stage-2C used).
- **ARM_SHARDED_DENSE**: shard-routing (steps 1-2 above) ONLY, entities still DENSE bipolar within each
  shard (isolates the SHARD-COUNT lever alone).
- **ARM_SHARDED_SPARSE**: shard-routing AND sparse `hippocampal_encoder`-coded entities within each
  shard (both levers stacked -- the full recommended architecture).
- **CONTROL_SCRAMBLED_SHARD_KEY** (mandatory, pairscramble-must-collapse discipline): same shard COUNT
  and SIZES as the real-key arms, but entities randomly reassigned to shards independent of their real
  source-relation-family or k-core band -- proves the WIN comes from genuine shard-key structure, not
  merely from splitting one big matrix into several smaller ones (a scale-only artifact would show up
  here too if the win were spurious).

**HARD-PASS** (all required, at BOTH scale=100,000 AND scale=1,213,912 -- the two rungs where
`ARM_FLAT` measured `relevant_recall=0.000`): `ARM_SHARDED_SPARSE relevant_recall >= 0.50` AND
`false_pull_in_rate <= 0.20` (Stage-2B's own bands, reused unmodified) AND `ARM_SHARDED_SPARSE` beats
`CONTROL_SCRAMBLED_SHARD_KEY` by `>= 0.30` absolute recall (the real-shard-key-matters discriminator)
AND `ARM_SHARDED_DENSE` alone (no sparse coding) shows SOME recovery over `ARM_FLAT` (`>= 0.20`
absolute, even if below the sparse arm) so the two levers' CONTRIBUTIONS are separately visible, not
just the composed win.

**HARD-FAIL** (either triggers): `ARM_SHARDED_SPARSE relevant_recall < 0.10` at BOTH top rungs (the
composed rescue does not work on REAL CSKG structure even though it worked on synthetic planted
communities -- would mean CSKG's actual source-relation-family / k-core partitioning does not carry
enough discriminative shard signal, escalate to a different real shard key or accept the wall as a
genuine engineering-hard capacity limit needing raw-`N` scaling) OR `CONTROL_SCRAMBLED_SHARD_KEY`
performs statistically indistinguishably from `ARM_SHARDED_SPARSE` (the win is a matrix-splitting
artifact, not a genuine shard-key effect -- would falsify the community/context-gating explanation
specifically, even if some numeric improvement appears).

**MIDDLE_BAND**: `ARM_SHARDED_DENSE` or `ARM_SHARDED_SPARSE` delays the collapse to a higher scale
without fully holding it, or one of the two real shard-key choices (source-family vs k-core) works while
the other does not -- motivates a shard-key search rather than abandoning the architecture.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, restated compactly)

- **HARD-PASS**: composed sharded-sparse arm recovers `>=0.50` relevant_recall at both 100K and 1.2M
  scale, beats a shard-scrambled control by `>=0.30` absolute, and the sparse-only and shard-only levers
  each show a nonzero independent contribution.
- **HARD-FAIL**: composed arm stays `<0.10` at both top rungs, OR the shard-scrambled control ties it
  (matrix-splitting artifact, not genuine context-gating).
- **MIDDLE_BAND**: partial rescue, or shard-key-dependent (source-family works, k-core does not, or vice
  versa).

## Honest brain-fidelity grade (deflated)

**Directional grade: HIGH-CONFIDENCE for the mechanism CLASS, MEDIUM-CONFIDENCE for THIS specific
composition on THIS specific store.** Breaking apart what is measured/established vs synthesized:

- Q1 (sparsity lever) and Q4 (CA3-not-resonator): raw lit confidence HIGH (~0.70-0.75) -- textbook,
  multiply-replicated (Willshaw 1969, Marr 1971, Hopfield 1982, Treves & Rolls 1991/1994, Kanerva 1988),
  and Q4 is further reinforced by TWO independent substrate-internal negative results on resonator
  (`exp_resonator_factorization_v1` K3/K4 collapse; this cycle's own basin-proliferation addendum).
  Deflated per the standing calibration penalty to **~0.55-0.60** for the specific quantitative transfer
  to KGStore's hetero-associative (not pure auto-associative) task shape, which the Willshaw/Treves-Rolls
  formulas were not derived for.
- Q2/Q3 (modularity, index-not-content, community-gated selection, and the "walls #1/#2 are one wall"
  claim): raw lit confidence HIGH for the qualitative biology (Teyler-DiScenna, CLS, Schapiro 2013,
  Poppenk 2013 -- all independently reused/confirmed across two separately-dated in-substrate notes plus
  this cycle's fresh search). The MECHANISM-level claim is not speculative synthesis this cycle -- it
  reuses a fully-worked-out 2026-07-08 design note, and the community-shard architecture has THREE
  independent HARD_PASS certifications on synthetic data. Deflated to **~0.45** specifically for the
  UNVALIDATED transfer from synthetic planted communities to a REAL, messy shard key on real CSKG data
  (the one negative data point on file, `exp_graph_community_detection_v1`, is a direct warning here,
  which is why the recommended architecture explicitly avoids automatic community detection in favor of
  CSKG's already-known source-relation-family/k-core tags).
- The FULL four-way composition (shard + sparse + CA3-readout + a real, non-detected shard key) landing
  a HARD-PASS on KGStore/CSKG specifically: **P_deflated = 0.42**, per the mandatory novel-synthesis
  cap (0.50) further reduced for: (a) no single prior cell has combined all four pieces at once; (b)
  `hdlab/hippocampal_encoder.py` has literally never been run past its own unit-scale self-tests; (c)
  the shard-key choice is a genuine open empirical question with one on-disk negative precedent for the
  "easy" (automatic-detection) version of it. This is consistent with, and should be read alongside, the
  0.38-0.48 calibration band this same-day research program has used across its sibling notes.

**Deviations from strict brain fidelity, disclosed**: (1) the brain's index (hippocampus) and content
(neocortex) are anatomically and mechanistically DIFFERENT substrates with different learning rates
(CLS's whole point); the recommended architecture uses the SAME KGStore machinery for both the coarse
router and the fine per-shard stores, a simplification, not a literal two-substrate CLS build (that
would be Spoke-3/Spoke-4-scale future work, per the 2026-07-02 design note's own P_CG~0.10 conservatism
on the full CLS composition). (2) CSKG's source-relation-family shard key is a real, useful, cheap
proxy for "context" but is not the same as the brain's experience-driven, continuously-relearned
community boundaries (Schapiro et al.'s finding that the hippocampus ACTIVELY discovers community
structure from a temporal stream) -- this recommendation uses a STATIC, human/corpus-assigned proxy,
not a learned one; a learned shard key is a legitimate v2 direction this note does not design.

**Credit**: this note's central finding is not new theory -- it is discovering that `notes/research_
reasoning_over_large_store_without_collapse_brain_first_2026-07-08.md` (self-authored research,
2026-07-08, uncredited by name in the Stage-2B/2C pre-regs that hit this exact wall one month later) had
already named the correct mechanism and that `exp_dev`/`hdi_exp_dev` had already built and HARD_PASS-
certified it three times, disconnected from the KGStore/CSKG line of work. The single most actionable
output of this drill is organizational, not scientific: **wire the community-bounded retrieval
mechanism into `hdlab/` (it currently has WIRED-organ-quality validation and zero WIRED-organ status)
and connect it to the store that has been failing on exactly the problem it was built to solve.**

## Cross-thread synthesis

- Directly extends and CORRECTS today's own `notes/research_content_causal_associative_knowledge_store_
  2026-08-09.md`, which named the causal/associative CONTENT sourcing problem as solved (CSKG spine
  already on disk, HARD_PASS-gated) but treated the RETRIEVAL/capacity question as still-open; this note
  supplies the missing capacity answer, and shows it was already available one commit-thread over.
- Directly extends `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md`'s
  finding that the substrate's own primitives (`cleanup_family.iterative_attractor`,
  `k_NN_lookup`) are STRUCTURALLY the global-matching/resonance family, not link-traversal -- this note
  adds the missing SCALE answer for that same retrieval operator (bound it to an active shard, don't run
  it flat against the whole store) and independently confirms that note's own finding that no multi-
  factor resonator primitive belongs on the critical path.
- Directly reuses and extends `notes/research_reasoning_over_large_store_without_collapse_brain_first_
  2026-07-08.md` -- the primary source for this drill's Q2/Q3 answer and the architecture recommendation
  -- crediting its four-thread analysis (index-not-content, schema-consolidation, expand-then-sparsify,
  community-modularity) and reporting that thread 4 (flagged there as "the load-bearing new claim,"
  P_deflated~0.35 AT THE TIME, pre-build) has since been BUILT and independently HARD_PASS-certified
  three times -- an update this note's own calibration reflects (raising confidence on the mechanism
  class while keeping the CSKG-specific transfer honestly uncertain).
- Corroborates and sharpens `data/exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1/metrics.json`
  (already-certified context-gate result): this note reframes that result as a PARTIAL (read-time-only)
  instance of the SAME community-routing mechanism that fully rescues wall #2 when also applied at
  write/ingest time, unifying two previously-separate "walls" under one mechanism.
- Names a concrete, disclosed follow-up gap distinct from anything in the existing notes: `hdlab/
  hippocampal_encoder.py` and the three community-routing experiment cells are both real, validated (or
  self-tested), currently-UNWIRED capabilities -- a `data/capability_registry.jsonl` and wire-don't-
  island gap this note surfaces but does not itself fix (per research-role scope; this is a natural
  `hdi_skunkworks`/promotion-cycle action item, not a research deliverable).

## Substrate-product implications

A working sharded-context-gated store turns the substrate's world-knowledge grounding layer from
"works at toy scale, provably collapses at the real 1.2M-edge CSKG scale" into a scale-invariant
retrieval architecture whose EVERY routing decision (which shard, which candidate, which attractor
settled to) is independently inspectable -- unlike the resonator path, which even when it worked would
have produced an opaque alternating-search trace, the community-routed architecture's audit trail is
already proven glass-box-intact by `exp_community_routed_glassbox_reasoning_scale_v1`'s own
`routing_causal_flip=1.000` result (flipping the routing decision causally changes the answer in a
traceable way, not silently). This is the same auditability differentiator this program has repeatedly
identified as the defensible product edge, now shown to survive -- and to have ALREADY been certified to
survive -- the exact scale regime (100K-1.2M items) where an opaque system would either silently degrade
or require an LLM-scale parameter count to paper over the same crosstalk problem this architecture
solves structurally, with a named, quantifiable mechanism (community-size-bounded, not total-KB-size-
bounded, discrimination) rather than brute-force capacity.

## Citations (verified count)

**Live-verified this cycle (5 WebSearch queries, generic neuroscience terms, no substrate-novel names
off-platform per query-privacy discipline)**: Teyler & DiScenna 1986 (hippocampal memory indexing
theory, PubMed/Behavioral Neuroscience, index-not-content mechanism confirmed); Kanerva 1988 Sparse
Distributed Memory (address-decoder expansion-then-sparse-coding architecture, capacity scaling
confirmed via multiple independent sources including an SNN reimplementation paper, arXiv:2109.03111);
Frady, Kleyko, Sommer 2020 (*Neural Computation*, Resonator Networks Parts 1 & 2, arXiv:1906.11684 --
factorization-not-memory-retrieval framing and resonate-and-fire biological-plausibility claim both
confirmed); Willshaw model capacity + Treves & Rolls 1991 CA3 sparseness-dependent capacity formula
(confirmed via ResearchGate/PMC sources, including the CA3a~20,000-memories estimate at sparseness
a~0.003); schema-dependent hippocampal-neocortical connectivity and event-schema cortical distribution
(PNAS 2010, Nature Communications 2022, multiple ScienceDirect reviews on hippocampal-neocortical
interaction and long-axis functional specialization -- corroborating, not primary-source-verified this
cycle for every individual claim).

**Reused-with-attribution from `notes/research_reasoning_over_large_store_without_collapse_brain_first_
2026-07-08.md`** (not re-verified this cycle, already cited there in full, disclosed there as
recalled-from-training-knowledge rather than live-fetched): Teyler & Rudy 2007; Moscovitch et al. 2016
multiple trace theory; McClelland, McNaughton & O'Reilly 1995; Tse et al. 2007/2011 *Science*; Willshaw,
Buneman & Longuet-Higgins 1969; Golomb, Rubin & Sompolinsky 1990; Tsodyks & Feigelman 1988; Amit & Fusi
1994; Watts & Strogatz 1998; Steyvers & Tenenbaum 2005; Schapiro, Rogers, Cordova, Turk-Browne &
Botvinick 2013 (*Nature Neuroscience*); Poppenk, Evensmoen, Moscovitch & Nadel 2013; Collin et al. 2017;
Patterson, Nestor & Rogers 2007.

**On-disk verified this cycle (not from memory, read directly)**: `data/exp_focus_pullin_causal_
stage2c_resonator_capacity_rescue_v1/metrics.json`; `preregs/2026-08-09_focus_pullin_causal_stage2c_
resonator_capacity_rescue_v1.md` (including its basin-proliferation ADDENDUM); `data/exp_focus_pullin_
causal_stage2b_cskg_scale_gate_v1/metrics.json`; `data/exp_focus_pullin_causal_stage15_salted_
cardinality_gate_v1/metrics.json`; `preregs/2026-08-09_focus_pullin_causal_stage15_salted_cardinality_
gate_v1.md`; `hdlab/kg_traversal.py`; `hdlab/cleanup_family.py`; `hdlab/situation_focus.py`; `hdlab/
selection_weighted_sharded_typer.py`; `hdlab/hippocampal_encoder.py`; `data/capability_registry.jsonl`
(grepped for hippocampal/DG/CA3/sparse/community-routing entries -- confirmed absent); `data/exp_
community_bounded_retrieval_scale_invariance_v1/metrics.json`; `data/exp_community_of_communities_
nested_retrieval_v2/metrics.json`; `data/exp_community_routed_glassbox_reasoning_scale_v1/metrics.json`;
`data/exp_graph_community_detection_v1/metrics.json`; `experiments/exp_community_bounded_retrieval_
scale_invariance_v1.py` (docstring/mechanism); `notes/research_reasoning_over_large_store_without_
collapse_brain_first_2026-07-08.md` (full read); `notes/research_content_causal_associative_knowledge_
store_2026-08-09.md`; `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md`;
`notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md`.

Total distinct citations this note directly draws on: 24 (10 fresh-scanned this cycle across 5 live
WebSearch queries, 14 reused-with-attribution from the 2026-07-08 in-substrate note), plus 19 on-disk
artifacts independently read and verified this cycle (not asserted from memory).
