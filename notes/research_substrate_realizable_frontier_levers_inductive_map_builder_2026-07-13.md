# Research: next-wave substrate-realizable levers for ANCHOR_COMPOSE (post SIC-peel + hard-neg)

**Filed by:** research sub-agent. **Trigger:** mission directive — first-wave levers (SIC-PEEL sequential consensus
decode + hard-negative scorer refit, both spec'd in `notes/research_inductive_map_builder_best_in_class_magnitude_
levers_2026-07-13.md` as Lever 1/Lever 2) are already implemented and shipping in `experiments/exp_anchor_compose_
magnitude_opt_cskg_v1.py` (verified on disk: `ANCHOR_PEEL`, `ANCHOR_PEEL_HARDNEG`, `PEEL_ROUNDS=3`, `HARD_NEG_FRAC`
param in `experiments/_kge_anchor1_fit.py::fit_kge_anchor1`, smoke-scale metrics present, not yet landed FULL). This
drill identifies the NEXT WAVE of substrate-realizable levers, under the hard constraint that every candidate must be
classified VSA-NATIVE (glass-box bind/bundle/cleanup/resonator/one-shot-Hebbian family, keep) vs LEARNED-NET
(gradient-trained arbitrary weights/MLPs/attention, disqualify) vs BORDERLINE (state the native-realization path or
reject). Method: (1) read the actual `ANCHOR_COMPOSE` construction code (`build_anchor_compose_codes`,
`build_heldout_entity_split_ac` in `experiments/exp_anchor_compose_inductive_entity_cskg_v1.py`) rather than
re-deriving from the prior note's abstraction — this surfaced a concrete, code-verified gap (see HEADLINE 1); (2) read
the landed `anchor_compose_scaling_ladder_cskg_v3` degree-stratified metrics on disk (`anchor_mrr_by_support_degree`)
to ground the cold/degree-1 floor question in measured numbers, not speculation; (3) 3 parallel Sonnet lit-scans on
genuinely new angles (post-composition attractor/resonator cleanup + cold-start floor effects; per-relation operator
calibration + role-factored binding; non-learned confidence-weighted bundling + fixed decorrelation front-ends) — 2 of
3 returned complete, 1 (per-relation/role-binding) got stuck in a nested background sub-spawn and did not return
synthesized findings in time; that section below relies instead on canonical, high-confidence foundational VSA
literature (Plate/Smolensky/Gayler/Kanerva/Kosko) rather than fabricating lit-scan output — flagged honestly, not
hidden.

---

## HEADLINE

1. **Code-verified NEW finding, the single best lever for the cold/degree-1 floor: `ANCHOR_COMPOSE` currently DISCARDS
   half its available information for held-out entities.** Reading `build_heldout_entity_split_ac` line-by-line: for
   a held-out entity `t`, the construction only collects edges where `t` is the TAIL of a known-head triple
   (`held_by_tail[ti]`). Edges where the held-out entity is the HEAD of a triple pointing to a KNOWN tail
   (`h_hold and not t_hold`) are silently dropped — never added to support, train, or query. This matters enormously
   because the shared scorer is ALREADY fit with `reciprocal=True` (`experiments/_kge_anchor1_fit.py`, line 65-69):
   inverse relations occupy `D[n_rel : 2*n_rel]` and are already trained on the full known graph. Bundling the
   held-out-as-HEAD edges via the ALREADY-TRAINED inverse relation (`est_inv = X[known_tail] + D[r_inverse]`) is a
   **zero-new-training, same-primitive, cheap construction-time change** that could materially increase usable
   support-edge count for exactly the degree-starved population the cheap-test asks about.
2. **The measured on-disk degree-stratified data (`exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json`,
   `anchor_mrr_by_support_degree`) shows WHY this matters and WHY it is structurally different from every other lever
   in this drill.** The `cold` bucket (entities whose only usable tail-direction edge is reserved entirely as the
   query target, by construction — 0 support edges reach them) sits at `anchor_mrr=0.000041`, **below its own
   `random_mrr=0.000524`** and far below `oracle_mrr=0.650751` — the single largest oracle-headroom gap of any
   bucket in the table, and the mechanism is currently WORSE than chance there. `d1` (entities with exactly 1
   composed support edge after split) reaches `anchor_mrr=0.0593` vs `oracle_mrr=0.392` — real signal, but using only
   ~15% of available oracle headroom (vs `d8plus` using ~94%). **This is a structural, not a decoding, problem for
   `cold`:** `build_anchor_compose_codes`'s own `mask = cnt > 0` guard means zero-support entities never get touched
   by the bundle step at all — they fall back to the raw untrained-random `Xa` row. **No cleanup, weighting,
   decorrelation, or role-binding lever can move `cold` entities, because there is nothing to aggregate.** Only
   levers that ADD a new usable edge (reciprocal-direction bundling, lever 1; multi-hop reach; textual/side-info
   fallback) can touch this bucket at all — this reclassifies several candidates below from "general quality lever"
   to "cannot help the specific population the mission asked about," which is itself the most decision-relevant
   finding of this drill.
3. **Every top-ranked lever below is VSA-NATIVE** (closed-form, zero gradient training for the held-out arm, reuses
   existing primitives: `peel_sic_readout`/SIC-peel-style consensus, additive TransE-style bind, already-trained
   reciprocal relation table, fixed random-projection decorrelation). **Explicitly DISQUALIFIED as LEARNED-NET:**
   GAT-style trained-attention bundling; the self-attention-augmented resonator-peeling variant (as opposed to the
   plain SIC-peel already shipping); multi-hop GNN message-passing with learned MLPs (NBFNet/RED-GNN/A*Net class);
   KG-Mixup-style gradient-trained synthetic-triple augmentation. **BORDERLINE, with native-realization sketches
   given below:** frozen/pretrained sentence-embedding nearest-neighbor virtual anchors (uses a frozen, not
   task-trained, feature source — arguably acceptable if the substrate already treats frozen text embeddings as fixed
   codebook entries elsewhere, per the standing ETF/MiniLM dimension-expansion work).
4. **A genuine literature gap, flagged honestly rather than papered over:** no paper found in this scan isolates
   "accuracy of an already-fully-composed vector, before vs. after one added attractor/resonator cleanup pass" as a
   clean ablation — the VSA literature always conflates cleanup with the decode/peeling loop itself (which is what
   SIC-peel, already shipping, already captures). One qualitative hit (HyperSpace, arXiv:2604.15113) confirms the
   DIRECTION (cleanup reduces reconstruction error) but gives no extractable magnitude. This means "iterative
   resonator cleanup of the composed code" as its own distinct lever (beyond the already-shipping SIC-peel) has a
   real but currently unquantified expected value — rank it below the reciprocal-bundling lever, not above.
5. **Confidence/degree-weighted bundling via non-learned formulas has real, quantified but SMALL-MAGNITUDE adjacent
   precedent** (APPNP/PPR-propagation: +1.0 to +1.8 percentage points node-classification accuracy over uniform
   aggregation, arXiv:1810.05997) — real but modest, and the domain (transductive node classification) is a real gap
   from our task (inductive entity link-prediction), so deflate further. The more interesting reframe: a
   **PPR/random-walk weighting computed over the union of an entity's visible support edges AND the fully-known 85%
   rest-of-graph** is a cheap way to let a `d2_3`+ entity's bundle implicitly reach 2 hops without paying the
   explicit-2-hop-bind SNR/dimension cost flagged in the prior note's Lever 3 — this is a new synthesis this drill
   adds, not previously identified.

---

## Part A — on-disk diagnostic: where the floor actually is (measured, not speculative)

From `data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json`, rung `r0_base` (k_core=12, support_frac=0.50,
N=25,752, 2 seeds, `HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE`, base anchor_margin=0.1269 matching confirmed v1):

| Bucket | n_mean (support edges) | anchor_mrr | additive_mrr (control) | random_mrr | oracle_mrr | oracle-headroom used |
|---|---|---|---|---|---|---|
| `cold` (0 usable support edges by construction) | 17.5* | **0.000041** | 0.000041 | 0.000524 | 0.650751 | ~0.006% |
| `d1` (1 composed support edge) | 8.0 | 0.059252 | 0.000042 | 0.000148 | 0.391866 | ~15% |
| `d2_3` | 52.5 | 0.078897 | 0.000043 | 0.000138 | 0.123391 | ~64% |
| `d4_7` | 226.0 | 0.151421 | 0.000042 | 0.000215 | 0.114233 | ~133% (exceeds oracle — noise/small-n) |
| `d8plus` | 2696.0 | 0.127724 | 0.000042 | 0.000535 | 0.135649 | ~94% |

*`n_mean` for `cold` reflects total-graph-degree metadata, not usable support-edge count — by code inspection
(`build_heldout_entity_split_ac`: `if d==1: query_lbl.append(edges[0]); n_cold += 1`), `cold` entities have exactly
ONE clean known-head-to-held-out-tail edge, and that edge is reserved entirely as the query target, leaving ZERO
support edges for the composer. `build_anchor_compose_codes`'s `mask = cnt > 0` then skips them entirely — their
`E_derived` is the raw untrained-random `Xa` initialization, which is why `anchor_mrr ~= additive_mrr` (both
uninformed) and both are near the numerical floor (~4e-5, essentially tied with random noise ranking).

**This table is the single most decision-relevant artifact in this drill:** it converts "which levers help
cold/degree-1 entities" from a speculative question into a directly-measured one. `cold` needs a NEW information
source (reciprocal edges, multi-hop, or side-information fallback); `d1`/`d2_3` need BETTER USE of existing scarce
information (weighting, cleanup, decorrelation can help here); `d4_7`/`d8plus` are already using a large fraction of
available oracle headroom and are the LEAST promising target for further lever investment.

---

## Part B — ranked levers, each classified VSA-NATIVE / LEARNED-NET / BORDERLINE

### Lever 1 (TOP RANK, NEW, code-verified) — Reciprocal/inverse-edge support bundling (rescues `cold` specifically)

**Mechanism:** extend `build_heldout_entity_split_ac` to also collect edges where the held-out entity is the HEAD of
a triple to a KNOWN tail (`h_hold and not t_hold`, currently silently dropped), and extend `build_anchor_compose_codes`
to bundle these via the ALREADY-TRAINED inverse relation: `est_inv = X[known_tail] + D[r + n_rel]` (the inverse
relation table already exists inside `Da` because `fit_kge_anchor1` is called with `reciprocal=True`). Average this
into the SAME bundle as the forward-direction estimates (or keep as a separate pooled arm for the cheap test below).
Zero new training — this is a construction-time change only.

**Brain-analog:** bidirectional associative memory — the classic reference is Kosko's BAM (1988): a single associative
matrix trained on pattern pairs `(A,B)` supports recall in EITHER direction (`A->B` and `B->A`) from the same
learned associations, because Hebbian-style outer-product plasticity is inherently symmetric in what it encodes. This
is the direct analog for "the same trained relation embeddings already support inverse-direction estimation; use both
directions of a fact, not just one." Weaker but relevant: hippocampal CA3 recall is not strictly unidirectional either
— partial cues from either "side" of an associated pair can drive completion via the same recurrent collateral
structure.

**Expected magnitude:** the `cold` bucket is currently indistinguishable from noise (`anchor_mrr` 0.000041 vs
`random_mrr` 0.000524) — ANY entity that gains even ONE usable reciprocal support edge moves from "zero information"
to "one composed estimate," which per the `d1` row (0.059 MRR from exactly one support edge) suggests a plausible
**order-of-magnitude rescue for the SUBSET of `cold` entities that have at least one qualifying reciprocal edge**
(not all will — some genuinely have degree-1 total in both directions). Population-weighted overall MRR gain is
likely small in absolute terms (cold is presumably a minority bucket) but the PER-ENTITY lift for the rescued subset
is the largest of any lever in this drill.

**VSA-native classification: NATIVE.** Reuses the existing additive-bind primitive and an inverse-relation table that
is already fit as a byproduct of standard reciprocal-augmented TransE training (a well-established, non-learned-at-
inference-time technique). No new gradient step for the held-out entity.

**Cost:** LOW — a construction-time code change to two existing functions, re-runs on the existing harness.

**Cheap-next-cell-vs-bigger-build:** **CHEAP NEXT CELL — highest-priority dispatch of this drill.**

**Helps cold/d1?** YES, directly and specifically — this is the only lever in this drill that can move the `cold`
bucket at all, because it is the only one that ADDS a new edge rather than better-using existing edges.

**P_deflated: 0.35** (capped under novel-synthesis ceiling — this is a code-verified gap and a well-established
technique (reciprocal relations are standard KGE practice) but the SPECIFIC transfer to "bundle held-out-as-head
edges into the composer" has not been tested in this literature or on this substrate; deflated for that open step,
not for the underlying mechanism's soundness).

---

### Lever 2 (NEW) — PPR/random-walk-weighted bundling over the visible-support-plus-known-graph (soft multi-hop bridge)

**Mechanism:** instead of a flat or SIC-peel-reweighted mean over an entity's DIRECT support edges only, compute a
personalized-PageRank-style random-walk score seeded at the held-out entity, walking through its visible support
edges INTO the fully-known 85% rest-of-graph (no leakage: only uses the entity's own visible edges plus already-known
graph structure), and use the resulting per-neighbor score as a closed-form (non-learned) bundle weight. This lets an
entity whose direct neighbors are themselves well-connected implicitly draw on 2+ hop structure without the entity's
OWN bundle growing in term-count (`d` in the SNR~5log(D/d) law stays the same — the WEIGHTING changes, not the
term-count) — a genuinely different risk profile from the prior note's explicit-2-hop-bind Lever 3.

**Brain-analog:** none direct and strong — flagged honestly, closest is diffusion-style graph propagation in cortical
association areas (weak analogy).

**Expected magnitude (quantified, adjacent domain):** APPNP (Klicpera et al., ICLR 2019, arXiv:1810.05997): switching
uniform-mean-style GCN propagation to closed-form personalized-PageRank propagation gains **+1.8pp (Cora,
81.5%->83.3%), +1.05pp (Pubmed), +0.33pp (Citeseer)** node-classification accuracy — real, but from transductive
node classification, not inductive link-prediction; deflate for domain transfer.

**VSA-native classification: NATIVE.** PPR/random-walk computation is a closed-form, deterministic, non-learned
operation over the graph adjacency; the resulting weights feed the SAME additive-bind-and-average primitive already
in use.

**Cost:** MODERATE — requires computing a random-walk/PPR score over the (potentially large) known-graph neighborhood
for each held-out entity; more expensive than Lever 1 but still CPU-tractable at CSKG's scale (25,752 nodes).

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, second priority after Lever 1 (shares harness, orthogonal
mechanism).

**Helps cold/d1?** Indirectly for `cold` (only if a `cold` entity's single edge or the Lever-1-recovered reciprocal
edge connects into a well-PPR-scored neighbor — this is a secondary rescue path, not primary); more directly useful
for `d2_3`/`d4_7` where there is already more than one candidate edge to differentially weight.

**P_deflated: 0.30** (capped under novel-synthesis ceiling — genuinely new synthesis for this exact application, not
literature-confirmed in the identical setting).

---

### Lever 3 — Iterative attractor/resonator cleanup of the ALREADY-COMPOSED code (distinct from the shipping SIC-peel)

**Mechanism:** after the bundle/consensus step produces `E_derived[v]` (whether via flat mean or the already-shipping
SIC-peel), run a SEPARATE fixed-point attractor-style refinement pass: `E_derived^(t+1) = cleanup(E_derived^(t))`
where `cleanup` is a similarity/energy-based nearest-attractor update against the codebook (reusing `score_all` /
`cleanup_family.py` machinery as the energy function), iterated to convergence. This is conceptually the modern-
Hopfield "one-step-denoise-a-corrupted-pattern" operation applied to the FINAL composite, not to the raw bundle
before aggregation (which is what SIC-peel already does).

**Brain-analog:** CA3 recurrent-collateral attractor dynamics / modern Hopfield energy descent (Ramsauer et al. 2020,
arXiv:2008.02217 — exponential capacity theorem, quantified for standard associative retrieval, NOT for this specific
composite-cleanup scenario).

**Expected magnitude:** **genuine literature gap, flagged honestly** (HEADLINE 4) — no paper isolates this exact
ablation. HyperSpace (arXiv:2604.15113) confirms the qualitative direction (cleanup reduces reconstruction error
after a noisy composite retrieval) but no extractable number. Treat expected lift as UNQUANTIFIED, plausibly small
given SIC-peel already captures much of the "iterative refinement" benefit for THIS construction.

**VSA-native classification: NATIVE.** Reuses `cleanup_family.py` as an outer fixed-point loop; zero trained
parameters.

**Cost:** LOW — reuses existing cleanup primitive, adds an outer convergence loop.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, but LOWER PRIORITY than Levers 1-2 given the unquantified
expected value and likely overlap with SIC-peel's existing benefit.

**Helps cold/d1?** NO for `cold` (nothing to attract toward if `E_derived` never received any real signal — a cleanup
pass on pure noise converges to a plausible-looking but arbitrary nearest attractor, not the correct one). Marginal
possible help for `d1`/`d2_3` (a single or few noisy estimates could be pulled toward a more plausible attractor).

**P_deflated: 0.20** (genuinely uncertain, literature gap is real, deflated further because of likely redundancy with
already-shipping SIC-peel).

---

### Lever 4 — Directional role-permutation binding (fixes a real asymmetry gap in the current construction)

**Mechanism:** the current bind is `est = X[h] + D[r]` (additive, not multiplicative-HRR bind, but structurally
analogous to a role-filler composition where `D[r]` plays the "role" and `X[h]` the "filler"). Classic VSA/HRR
practice (Plate, *Holographic Reduced Representations*, 1995; Smolensky, tensor-product binding, 1990; Gayler,
Multiply-Add-Permute / MAP architecture, 2003; Kanerva, Vector Symbolic Architectures / hyperdimensional computing,
2009) explicitly recommends a PERMUTATION operator to encode asymmetric/positional roles (e.g., distinguishing
"subject slot" from "object slot") rather than relying solely on a per-relation-indexed vector to carry directionality
— this is precisely what the reciprocal-relation table already does structurally (forward vs. inverse relation ids
occupy disjoint index ranges), so this lever is really "make sure Lever 1's reciprocal bundling is done via a
role-consistent operator, not accidentally conflating forward and inverse contributions in the SAME additive slot."
Practically: verify (and if needed enforce via a permutation) that forward and reciprocal contributions to a bundle
are role-distinguishable before averaging, not silently pooled as if equivalent.

**Brain-analog:** none new beyond Lever 1's Kosko-BAM analog — this is more a correctness/hygiene lever on top of
Lever 1 than an independent mechanism.

**Expected magnitude:** small and mostly RISK-MITIGATING (prevents a subtle version of Lever 1 from working worse than
expected due to forward/inverse conflation) rather than a standalone source of lift. Unquantified.

**VSA-native classification: NATIVE.** Canonical VSA operator (permutation for role-binding), zero training.

**Cost:** TRIVIAL — a few lines inside Lever 1's implementation, not a separate cell.

**Cheap-next-cell-vs-bigger-build:** fold into Lever 1's implementation, not a standalone dispatch.

**Helps cold/d1?** Indirectly, by making Lever 1 (the actual cold-rescue lever) more robust.

**P_deflated: 0.25** for "matters at all here" (mostly a correctness safeguard, not an independent lift source; not
independently dispatched as its own cell).

---

### Lever 5 — Count/frequency and norm-based (non-learned) bundle weighting

**Mechanism:** replace flat mean with a closed-form weight per support-edge estimate — e.g. weight by the OBSERVED
frequency of that (head, relation) pattern in the known graph, or by the estimate vector's own norm as a confidence
proxy. Explicitly NOT learned attention (GAT-style) — that is the disqualified category.

**Expected magnitude:** the adjacent literature is genuinely mixed here (per the prior note's Lever 4 finding:
GraphSAGE-mean beats degree-normalized GCN on OGB link-prediction benchmarks in some cases) — norm-based weighting
has one qualitative-adjacent hit (embedding norm correlates with k-NN confidence, arXiv:2502.09252) but no
graph/KG-specific link-prediction delta was found.

**VSA-native classification: NATIVE** (closed-form, zero learned parameters) if implemented via count/frequency or
vector-norm; **LEARNED-NET if implemented as trained attention** (explicitly disqualified).

**Cost:** TRIVIAL.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, bundle as a secondary arm alongside Lever 1/2's dispatch —
low expected value on its own (reaffirms the prior note's Lever 4 finding), worth testing cheaply, not worth a
standalone dispatch.

**Helps cold/d1?** NO for `cold` (zero edges = nothing to weight); NO-OP for `d1` by definition (weighting a single
term does nothing); marginal help for `d2_3`+.

**P_deflated: 0.20** (unchanged from the prior note's Lever 4 assessment; no new evidence moved this up or down).

---

### Lever 6 — Per-relation reliability/precision calibration (closed-form, not gradient-trained)

**Mechanism:** scale each relation's contribution to a bundle by a closed-form per-relation reliability score computed
from the KNOWN graph (e.g., a relation's own measured precision/consistency when used to predict already-known
tails, or its inverse-frequency), rather than treating every relation type as equally trustworthy. This is DISTINCT
from the prior note's Lever 2 (hard-negative refit of the shared scorer `W`) — that lever improves the SCORER;
this lever improves the CONSTRUCTION-TIME weighting of which relations to trust more when composing `E_derived`.

**VSA-native classification: NATIVE** if the calibration score is computed via a closed-form statistic (frequency,
measured precision on known triples) rather than fit via gradient descent as an additional trainable parameter per
relation (which would push this toward LEARNED-NET — the line is precisely whether the per-relation scalar is
computed by a formula or fit by backprop).

**Expected magnitude:** unquantified for this exact construction-time application; the prior note's Lever 2 already
captures the closest quantified adjacent evidence (RotatE self-adversarial, MixKG, InCL-KGC: +0.02-0.04 MRR), but
that is scorer-training, not bundle-weighting — treat this as a smaller, complementary, unquantified lever.

**Cost:** LOW.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, bundle alongside Lever 5.

**Helps cold/d1?** NO for `cold`; marginal for `d1`+ (a single relation-typed edge weighted by relation reliability
could matter if some relation types are systematically noisier for tail-prediction than others).

**P_deflated: 0.20**.

---

### Lever 7 — DG-style fixed random-projection decorrelation front-end (reinforces prior note's Lever 5)

**Mechanism:** unchanged from the prior note — apply a fixed (non-trained) sparse random-expansion or competitive
sparsification transform to anchor/support-edge representations before bundling, analogous to dentate-gyrus pattern
separation.

**New evidence this drill adds:** MESH (Sharma, Chandra, Fiete, arXiv:2202.00159, ICML 2022) — a fixed random
attractor scaffold plus heteroassociation reported to "nearly saturate the information-theoretic capacity bound,"
reinforcing the qualitative case with a stronger, more directly capacity-relevant citation than the prior note had,
though still not an extractable single accuracy-delta number (would require a full-PDF read to pull the specific
figure). Cover's theorem and the Johnson-Lindenstrauss lemma are confirmed as the general mathematical grounding
across multiple foundational sources (Marr 1969, Albus 1971, O'Reilly & McClelland 1994, de Almeida/Idiart/Lisman
2007/2009) — consistently qualitative, not quantified, across all of them.

**VSA-native classification: NATIVE** (fixed random projection is a hallmark VSA/HDC operation).

**Cost:** LOW.

**Cheap-next-cell-vs-bigger-build:** CHEAP NEXT CELL, bundle as tertiary arm.

**Helps cold/d1?** NO for `cold`; marginal for `d2_3`+ (reduces crosstalk among MULTIPLE bundled terms — irrelevant
when there are 0-1 terms to begin with).

**P_deflated: 0.25** (unchanged from prior note — new citation reinforces direction, does not resolve the
quantification gap).

---

### Explicitly DISQUALIFIED as LEARNED-NET (with BORDERLINE native-realization sketches where one exists)

| Candidate | Why disqualified | Native-realization path (if any) |
|---|---|---|
| GAT-style trained-attention bundling | Requires gradient-trained per-edge attention weights — breaks zero-training-for-new-entities | None; use Lever 2 (PPR) or Lever 5 (norm/count) instead |
| Self-attention-augmented resonator decomposition (arXiv:2403.13218) | The specific "attention-augmented" variant requires trained attention parameters | The underlying resonator-PEEL loop itself is already native and already shipping as SIC-peel; do not adopt the attention-augmented variant |
| Multi-hop GNN message-passing with learned MLPs (NBFNet/RED-GNN/A*Net class) | Learned per-layer MLP transforms, not closed-form | The prior note's fixed-BFS 2-hop bind (Lever 3 there) is the native analog; this drill's Lever 2 (PPR-weighted soft multi-hop) is a cheaper native alternative |
| KG-Mixup synthetic-triple augmentation (arXiv:2302.05044) | Realized via standard gradient-trained embedding table on synthetic triples | **BORDERLINE**: a native analog exists — inject synthetic SUPPORT EDGES (not synthetic triples fed to gradient training) directly into the construction-time bundle for degree-starved entities, using patterns borrowed from similar-degree known entities, entirely closed-form; untested, flagged as a possible future lever, not ranked in Part B given AEGIS's cautionary finding below |
| AEGIS synthetic/random edge augmentation (arXiv:2509.22017) | Reports synthetic/random edges as ACTIVELY HARMFUL for sparse-node link-prediction | N/A — this is evidence AGAINST a lever, not a disqualification of a promising one; reinforces that Lever 1 (REAL reciprocal edges, not synthetic) is the right way to add information, not fabricated edges |
| AEGIS semantic-KNN/textual side-information fallback | Uses a pretrained (frozen) text/sentence encoder | **BORDERLINE**: if the substrate already treats a frozen sentence-embedding table as a fixed feature source elsewhere (per the standing ETF/MiniLM dimension-expansion work), a frozen-embedding nearest-neighbor virtual anchor edge for `cold`/`d1` entities is arguably native (no task-specific gradient training), reported as HELPING sparse nodes in AEGIS (semantic-KNN "largest AUC improvement" on a text-rich sparse graph) — worth a follow-up drill specifically on this if Lever 1 does not fully close the `cold` gap |

---

## Cheap decisive test

**Dispatch ONE cell, `anchor_compose_reciprocal_cold_rescue_cskg_v1`, reusing the EXISTING v1/v2/v3 harness verbatim
(same CSKG-12core split machinery, same seeds, same `n_heldout_eval`, same degree-stratification infra already
computing `anchor_mrr_by_support_degree`):**

- **Arm RECIP:** extend `build_heldout_entity_split_ac` to also retain held-out-as-HEAD edges (currently dropped),
  and extend `build_anchor_compose_codes` to bundle them via the already-trained inverse relation
  `D[r + n_rel]`. Report the SAME degree-stratified table as `r0_base`, with `cold`/`d1`/`d2_3`/`d4_7`/`d8plus`
  recomputed under the NEW (larger) support-edge counts this changes bucket membership for some entities too.
- **Arm RECIP_SCRAMBLE (must-fail control):** identical construction but with the inverse-relation ids permuted
  (same discipline as the existing `ANCHOR_SCRAMBLE`/`PEELSCR` controls) — confirms any lift is relational, not an
  artifact of adding more (any) vectors to the bundle.
- **Optional secondary arm (Lever 2, PPR):** if compute budget allows in the same dispatch, add a PPR-weighted
  variant over the RECIP-augmented support set.

**HARD-PASS:** `cold`-bucket `anchor_mrr` rises from `~0.000041` to **`>=0.02`** absolute (roughly a 500x relative
rescue off an effectively-zero floor — a low absolute bar given the current value is indistinguishable from noise),
AND `RECIP_SCRAMBLE`'s `cold`-bucket value stays within noise of the ORIGINAL `~0.000041` (confirms the lift is
relational, not merely "more vectors in the average"). Overall population MRR gain `>=0.005` absolute is a reasonable
secondary bar (small because `cold` is presumably a minority bucket, but the PER-BUCKET rescue is the primary signal).

**HARD-FAIL:** `cold`-bucket `anchor_mrr` stays `<0.0002` (order-of-magnitude unmoved) despite the RECIP construction
firing correctly (self-test confirms nonzero reciprocal-support entities exist) — this would be genuinely
informative: it would mean CSKG-12core's `cold` entities mostly lack usable edges in EITHER direction beyond their
single query edge, redirecting fully to multi-hop-through-neighbors or textual-fallback levers (BORDERLINE table
above) rather than any same-entity edge-recovery trick.

**Middle band (`cold` lift present but `<0.02`):** degree-stratify further by whether the entity gained 1 vs. 2+
reciprocal support edges — if lift scales with reciprocal-edge-count, the lever works but the `cold` population is
simply thin on reciprocal edges too (a graph-sparsity finding, not an architecture failure) and the next move is
Lever 2 (PPR into the known graph) rather than abandoning the direction.

**Must-fail control reuse:** `RANDOM` and `BASELINE_POP` arms carried over unchanged from the landed harness.

---

## Falsifiable predictions summary

| Lever | Mechanism class | Helps `cold`? | Helps `d1`? | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|---|---|---|
| 1. Reciprocal/inverse-edge bundling | NATIVE | **YES (primary)** | YES | cold anchor_mrr >=0.02 abs, scramble control flat | cold anchor_mrr <0.0002 despite firing | **0.35** |
| 2. PPR/random-walk soft multi-hop | NATIVE | secondary | YES | MRR +>=0.01 abs on d2_3+/d1 buckets | MRR +<0.003 abs | 0.30 |
| 3. Post-composition attractor/resonator cleanup | NATIVE | no | marginal | MRR +>=0.01 abs beyond SIC-peel's own gain | MRR +<0.003 abs beyond SIC-peel | 0.20 |
| 4. Directional role-permutation (folds into Lever 1) | NATIVE | indirect | indirect | Lever 1's own gate, cleaner | Lever 1 underperforms due to conflation, fixed by this | 0.25 |
| 5. Count/norm-based bundle weighting | NATIVE (learned-attention variant disqualified) | no | no-op | MRR +>=0.01 abs, stable sign across seeds | no stable sign | 0.20 |
| 6. Per-relation reliability calibration | NATIVE (formula) / LEARNED-NET (if backprop-fit) | no | marginal | MRR +>=0.01 abs | MRR +<0.003 abs | 0.20 |
| 7. DG-style fixed decorrelation front-end | NATIVE | no | marginal (d2_3+) | MRR +>=0.01 abs | MRR +<0.003 abs | 0.25 |

All P values deflated 0.15-0.25 from naive base rate per the standing lit-scan calibration discipline; none exceed
the 0.50 novel-synthesis cap. Lever 1 is the highest-P item in this drill precisely because it is grounded in a
code-verified structural gap (not a literature-transfer bet).

---

## Cross-thread synthesis

- **Directly extends** `notes/research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md` (Levers
  1-6 there = SIC-peel, hard-neg refit, 2-hop, degree-weighted agg, DG-decorrelation, TEM/grid-cell) — this drill's
  Levers 3, 5, 6, 7 are direct continuations/reinforcements of that note's Levers 1, 4, (new), 5 respectively; Levers
  1, 2, 4 here are genuinely NEW (not present in the prior note), surfaced specifically by reading the actual
  construction code rather than working from the prior note's abstraction alone.
- **Sharpens the capacity-tracks-local-degree law's practical implication**, per the same triple-confirmed
  GrapHD/KGE-rank-bottleneck/hippocampal-CA3 law cited in both prior notes: Lever 1 is SAFE with respect to that
  ceiling for the population it targets (`cold` entities move from `d=0` to `d=1`, pure signal gain, no crowding),
  whereas Lever 2 and the prior note's Lever 3 (explicit 2-hop) both risk the SNR-vs-dimension tradeoff for
  higher-degree entities — this drill's on-disk data (Part A) is the first place the ceiling's population-specific
  applicability (safe for `cold`, risky for `d4_7`/`d8plus`) is made explicit rather than treated as one uniform
  caveat.
- **Connects to the standing relational-capability program spine**
  (`project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`): Lever 1's brain-analog
  (Kosko's bidirectional associative memory — one learned association supporting recall in EITHER direction) is a
  genuinely NEW brain-grounded citation for that program's standing question of whether the substrate's binding
  operations can support bidirectional/reciprocal relational inference, not just forward composition — worth
  flagging to that thread directly as a concrete, code-adjacent instance of "relational capability" (using a
  relation in reverse) rather than just entity-generalization.
- **Does not duplicate** `notes/research_anchor_compose_live_store_integration_path_2026-07-13.md` (a separate,
  orthogonal question about wiring the offline experiment into the live `KGStore`) — that note's two-timescale
  fast-write/slow-consolidation proposal is compatible with any of the levers ranked here; none of these levers
  change which integration path (native-bind vs adjunct-structure) that note recommends resolving first.
- **Open item, honestly flagged:** the per-relation-calibration / role-factored-binding lit-scan sub-agent did not
  return synthesized findings in time (got stuck delegating to its own nested background sub-agents rather than
  searching directly) — Levers 4 and 6 above rely on canonical, high-confidence foundational citations (Plate 1995,
  Smolensky 1990, Gayler 2003, Kanerva 2009) rather than a fresh lit-scan confirming CURRENT quantified deltas for
  per-relation calibration specifically; if a follow-up drill re-runs that scan and finds a quantified number, Lever
  6's `P_deflated` should be revisited upward.

---

## Substrate-product implications

- **The honest, defensible product claim if Lever 1 HARD-PASSes:** "our zero-training entity-generalization mechanism
  does not just compose forward relational facts — it can recover a coherent representation of a brand-new concept
  even when it has been seen ONLY as the subject (not the object) of known relationships, using the exact same
  trained relational machinery in reverse." This is a genuine differentiator: most inductive-KGE literature does not
  explicitly test or exploit this reciprocal-direction asymmetry, and it directly targets the worst-served population
  (`cold`, currently indistinguishable from random) rather than incrementally improving an already-working
  population.
- **If Lever 1 HARD-FAILs:** still informative, not a dead end — it would establish that CSKG-12core's `cold`
  population is fundamentally single-edge-in-any-direction (a genuine graph-sparsity floor, not an architecture gap),
  which redirects cleanly to either the BORDERLINE textual-fallback path (AEGIS-style, if the substrate already has a
  frozen sentence-embedding source available) or an honest product statement that some fraction of brand-new
  concepts simply cannot be usefully described from structure alone and require an exogenous information source —
  directly relevant to the standing grounding-is-the-wall thread
  (`project_grounding_needs_active_intervention_exogenous_referent_3source_synthesis_2026-07-09.md`).
- **Scope discipline:** Levers 3, 5, 6, 7 (post-composition cleanup, non-learned weighting, per-relation calibration,
  fixed decorrelation) are real, cheap, VSA-native quality-of-life improvements worth testing opportunistically
  (bundle as secondary arms in the SAME dispatch as Lever 1, since they share the harness), but this drill's clearest
  finding is that NONE of them can move the `cold` population — prioritizing compute toward Lever 1/2 for the
  cold/degree-1 question specifically, and treating 3/5/6/7 as general-magnitude levers for the `d2_3`+ population
  instead, is the correct allocation given the measured (not assumed) floor data in Part A.

---

## Citations (verified count)

**On-disk, read in full this cycle:** `experiments/exp_anchor_compose_inductive_entity_cskg_v1.py` (full
construction code: `build_heldout_entity_split_ac`, `build_anchor_compose_codes`, arm definitions — the code-verified
Lever 1 gap); `experiments/_kge_anchor1_fit.py` (`fit_kge_anchor1`, confirms `reciprocal=True` inverse-relation
training already in place, and confirms `hard_neg_frac` param already exists for the shipping hard-neg lever);
`experiments/exp_anchor_compose_magnitude_opt_cskg_v1.py` (confirms SIC-PEEL + HARDNEG already implemented/shipping,
smoke-scale metrics present); `data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json` (degree-stratified
`anchor_mrr_by_support_degree` table, Part A); `data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json`
(`mechanism_selftest`, `support_deg_hist`, confirms bucket definitions); `notes/research_inductive_map_builder_best_
in_class_magnitude_levers_2026-07-13.md` (prior lever ranking, extended here); `notes/research_anchor_compose_live_
store_integration_path_2026-07-13.md` (orthogonal integration-path note, cross-referenced not duplicated).
**7 on-disk sources.**

**External literature (2 of 3 parallel Sonnet lit-scans completed; generic ML/neuroscience terms only, no
substrate-novel names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*Attractor cleanup + cold-start floor (10):* Frady, Kent, Olshausen, Sommer, Resonator Networks 1, arXiv:1906.11684;
Resonator Networks 2, Neural Computation 32(12):2332 (2020); "A comparative study of nonlinear cleanup rules in
resonator networks," Frontiers in AI, doi:10.3389/frai.2026.1793314; "Self-Attention Based Semantic Decomposition in
VSA," arXiv:2403.13218; "HyperSpace," arXiv:2604.15113; Ramsauer et al., "Hopfield Networks is All You Need,"
arXiv:2008.02217; Shomer et al., "Toward Degree Bias in Embedding-Based KGC" (KG-Mixup), arXiv:2302.05044, WWW 2023;
"ACTC: Active Threshold Calibration," arXiv:2305.06395, ACL 2023; "AEGIS: Authentic Edge Growth In Sparsity,"
arXiv:2509.22017; "Linearithmic Clean-up for VSA Key-Value Memory," arXiv:2506.15793 (flagged unverified — fetch
garbled, numbers not independently confirmed).

*Non-learned weighting + fixed decorrelation (11):* Klicpera, Bojchevski, Gunnemann, APPNP, arXiv:1810.05997;
Bojchevski et al., PPRGo, arXiv:2007.01570; Kipf & Welling, GCN, arXiv:1609.02907; "When Design Rules Break,"
arXiv:2606.10249; Brody, Alon, Yahav, GATv2, arXiv:2105.14259; "On the Importance of Embedding Norms in SSL,"
arXiv:2502.09252; Marr (1969)/Albus (1971), cerebellar expansion-codon theory (foundational); O'Reilly & McClelland,
Hippocampus 1994 (foundational); de Almeida, Idiart, Lisman, Learning & Memory 2007/2009 (foundational); Sharma,
Chandra, Fiete, "MESH," arXiv:2202.00159; "Dentate Gyrus Circuitry Features Improve Sparse Approximation Algorithms,"
PLOS ONE 2015, journal.pone.0117023.

*Per-relation calibration + role-factored binding — lit-scan did not return; relied on canonical foundational
citations instead (4, high-confidence, not independently re-verified via web this session, flagged per HEADLINE 5 /
cross-thread synthesis):* Plate, "Holographic Reduced Representations," 1995; Smolensky, tensor-product variable
binding, 1990; Gayler, Multiply-Add-Permute (MAP) architecture, 2003; Kanerva, "Hyperdimensional Computing," 2009;
Kosko, "Bidirectional Associative Memories," IEEE Trans. Systems, Man, and Cybernetics, 1988 (also foundational,
5th citation in this group).

**Total: 7 on-disk sources + 21 externally-searched sources + 5 canonical-but-not-freshly-verified foundational
citations = 33 verified/flagged checks.**

---

## Intuitive summary

**The question:** we already have two proven, cheap upgrades shipping for our "instantly describe a brand-new
concept" system (check-and-recheck the composed guess a few times; make the underlying scorer pickier). What's the
NEXT wave of upgrades, and — crucially — which of them can actually help the WORST-off new concepts (the ones we've
seen almost nothing about), versus which ones only help concepts we already handle reasonably well?

**What we found, and it's a genuinely useful correction:** we pulled up the actual measured numbers for how the
system does on the sparsest concepts, broken out by how much information was available about them. The results were
stark: concepts we've seen absolutely nothing usable about currently score WORSE than pure guessing — not just low,
but below the floor, because the system has literally nothing to work with for them. That's a fundamentally different
problem than "the concepts we've seen some things about aren't described as sharply as they could be" (which several
of the candidate upgrades genuinely would help). No amount of "read the guess more carefully" or "weight the evidence
better" can fix a case where there is no evidence at all — you can't recheck an empty page.

**The best new idea this drill found:** reading the actual working code (not just describing it from memory) turned
up a concrete, fixable oversight — the system currently only uses "this new concept IS this kind of thing" facts, but
throws away "this OTHER thing IS this new concept" facts, even though it already has a trained mechanism (built for
an unrelated reason) that could read those facts in reverse, for free, with zero additional training. This is exactly
the kind of thing a two-way memory naturally supports (a fact you learned pointing "forward" is often equally usable
pointing "backward"), and it's the one upgrade in this drill's whole list that can plausibly rescue the very worst
concepts specifically, rather than polishing the ones we're already doing okay on.

**The honest caveats:** one of our three research assistants got stuck delegating its own sub-task rather than doing
the search itself and never reported back in time — rather than making up results for it, we relied on
well-established textbook facts for that section and said so plainly. We also found a genuine hole in the outside
literature: nobody seems to have cleanly tested "does re-examining an already-finished guess, on its own, help" as
distinct from "does re-examining WHILE forming the guess help" (which is the trick we already shipped) — so that
particular idea stays a real but currently unmeasured bet rather than a proven one.
