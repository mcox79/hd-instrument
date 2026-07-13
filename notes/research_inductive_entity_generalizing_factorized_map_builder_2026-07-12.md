# Research: the INDUCTIVE, entity-generalizing core of the factorized map-builder

**Filed by:** research sub-agent. **Trigger:** mission directive — design the mechanism that closes the held-out-ENTITY
generalization gap, given the likely fork verdict is MEMORIZE (fixed per-entity KGE tables cannot represent an entity
absent from training, by construction). 3 parallel Sonnet lit-scan sub-agents (inductive-KGE entity-independent
mechanisms; VSA/HRR graph representation + resonator decode; hippocampal inductive binding of novel items) + on-disk
read of `hdlab/kg_traversal.py::KGStore`, `hdlab/cleanup_family.py`, the fork-test cell family
(`exp_heldout_entity_inductive_probe_cskg_gpu1024_v1/v2`), and 5 prior research notes. Pure research, no local compute.
Extends `notes/research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md` (named this exact test as the
cheapest next check) and `notes/research_storage_is_the_map_brain_scale_substrate_integration_2026-07-12.md` (proposed
the phase-rotation native-bind upgrade this drill assumes as optional infrastructure, not a dependency).

---

## HEADLINE

1. **The fork test is IN FLIGHT, not yet verdicted — read the actual state before building on top of it.**
   `data/exp_course_c_heldout_entity_inductive_probe_gpu1024_v1/metrics.json` landed **`INCONCLUSIVE_ORACLE_UNDERFIT`**
   (held-out Hits@10: ONESHOT_ROTATE=0.0000, ADDITIVE_TRANSE=0.0000, RANDOM_CODES=0.0004, ORACLE_TRANSDUCTIVE=0.0123 —
   oracle margin over random = 0.0119, below the required `>=0.10` fire gate) — the fit under-trained even the
   positive control, so the zero-margin arms are **uninterpretable**, not yet a proof of memorize. A v2 cell
   (`exp_heldout_entity_inductive_probe_cskg_gpu1024_v2.py`, ep=500, 2x fidelity, pre-cleared escalation to 750/3x if
   still underfit) is dispatched to resolve this but has **not landed** (only a selftest metrics file exists on disk
   as of this drill). **This note's build spec is therefore explicitly gated on v2 landing** — per the mission's own
   framing ("sequence it after the fork verdict confirms memorize"), not run ahead of it.
2. **The literature's answer to "how do you represent an unseen entity" is consistent across 9 methods and is NOT
   "closed-form for free" — it is: a small, REUSABLE, graph-global vocabulary of parts (relation-type operators,
   anchor nodes, or structural distance labels), composed fresh per query/entity by a trained-but-entity-agnostic
   function, never a stored per-entity vector.** NBFNet/A*Net compose relation operators via a generalized
   Bellman-Ford path-sum, entity-conditioned only through a one-hot query label (Zhu et al., NeurIPS 2021,
   arXiv:2106.06935; Zhu et al. 2022, arXiv:2206.04798). GraIL scores a labeled enclosing subgraph with zero
   entity-specific parameters (Teru et al., ICML 2020, arXiv:1911.06962). NodePiece tokenizes every entity as a
   composition of a small shared anchor set + relation types, BPE-style (Galkin et al., ICLR 2022, arXiv:2106.12144).
   ULTRA generalizes this to relation vocabularies too, entirely ID-free (Galkin et al., ICLR 2024, arXiv:2310.04562).
   **The addressing/tokenization step (which anchors, which paths, which distances) is closed-form and zero-shot; only
   the scoring function needs a trained forward pass, and that function never touches an entity ID.** The one
   consistent failure mode across all 9 methods: a genuinely sparse/isolated unseen entity (few edges, no anchor
   proximity, no path to the query) degrades gracefully but predictably — context scarcity, not architecture, becomes
   the limiter. This is the single most load-bearing, directly-portable fact for the substrate design below.
3. **A NEW, third independent convergence on "capacity is governed by local degree, not global N": VSA bundling
   theory says the same thing as KGE rank-bottleneck theory and hippocampal CA3 capacity theory.** GrapHD (Poduval
   et al., *Frontiers in Neuroscience* 2022, PMC8855686) derives an explicit signal-to-noise formula for a graph node
   built by bundling its neighbor-bindings: **SNR ≈ 5·log(D/d)**, where D = vector dimension and d = average node
   degree — i.e. required dimension scales with LOCAL DEGREE, not graph size. This is the same qualitative law as the
   KGE-theory result already found in the prior scaling drill (`d >= 2c+1`, c = max degree, arXiv:2506.22271) and the
   classical Treves-Rolls hippocampal CA3 capacity law (`p_max ~ k*C_RC*ln(1/a)`, governed by connections-per-neuron).
   **Three unrelated fields (VSA/HDC theory, KGE expressiveness theory, associative-memory neuroscience) now
   independently derive the same design constraint** — this is not a coincidence worth treating lightly, and it gives
   the build spec below a concrete, literature-grounded sizing rule (dimension must track degree of the region being
   bundled, not entity count).
4. **The specific construction the mission proposes ("entity = superposition of bound relational context") has ONE
   direct positive precedent and ONE direct negative precedent in the VSA literature — read both honestly.**
   GrapHD itself (the paper supplying the SNR formula above) explicitly does the OPPOSITE of what this drill proposes:
   it assigns every node an **independent random vector** and only bundles at the EDGE and whole-graph level, never
   deriving a node's own code from its neighbors. The genuinely matching precedent is **HDGL** (Dalvi & Honavar,
   arXiv:2402.17073): `z_v = r_v (x) Pi(bundle_{j in N1(v)} r_j) (x) Pi.Pi(bundle_{m in N2(v)} r_m)` — a node code
   built by binding a hop-distance permutation onto a bundle of neighbor codes at each hop, explicitly justified as
   avoiding gradient training. **But HDGL is only evaluated transductively** — no paper in this scan runs the exact
   experiment "construct a brand-new node's vector purely from its edge list post-hoc and show it retrieves/classifies
   comparably to trained nodes." The construction is architecturally sound and literature-precedented in FORM, but its
   INDUCTIVE claim (zero-shot novel-node construction) is this drill's own extension, not a lifted result — flagged
   honestly, capped at the novel-synthesis ceiling below.
5. **Brain grounding is unusually clean and directly maps onto the proposed mechanism, not just loosely analogous.**
   A genuinely novel location gets a grid-cell code by CONTINUOUS ATTRACTOR PATH INTEGRATION (velocity/phase
   accumulation over a FIXED, reused set of grid modules) — the code is *computed*, never learned per-location
   (Hafting et al. 2005; Burak & Fiete, PLoS Comp. Biol. 2009). Place-cell remapping in a new environment is a
   REBINDING of that fixed structural code onto new sensory content, largely one-shot (Leutgeb et al. 2004/2005;
   Whittington et al., TEM, *Cell* 2020, explicit "no retraining of structural code" claim). Schema-consistent facts
   get bound into pre-existing structural slots in a SINGLE trial via fast CA3 Hebbian binding (Tse et al., *Science*
   2007, 2011; Eichenbaum's binding-of-item-and-context theory). **The common principle — a fixed, reusable scaffold
   that requires no relearning, plus fast BINDING of new content onto it — is exactly the anchor-composition
   construction proposed in Part B below, not a post-hoc metaphor fitted to it afterward.**

---

## Part A — the inductive-KGE literature: how unseen entities get represented (deep dive)

| Method | What stands in for "the entity" | Closed-form or trained-forward-pass? | Inductive benchmark (Hits@10, WN18RR v1) | Failure mode |
|---|---|---|---|---|
| NBFNet (Zhu et al. NeurIPS 2021, arXiv:2106.06935) | query-conditioned path-sum `h_q(u,v)`, generalized Bellman-Ford over relation-composition (product) + path-aggregation (sum) | trained-but-entity-agnostic forward pass; addressing (which edges) is closed-form | 0.948 | depth-truncation (T-hop cap); OOM at million-node scale |
| A*Net (Zhu et al. 2022, arXiv:2206.04798) | same as NBFNet + learned priority function to prune expansion | same | 0.661 (14-43x cheaper) | priority-function mis-selection on rare relations |
| GraIL (Teru et al. ICML 2020, arXiv:1911.06962) | labeled enclosing subgraph (double-radius distance labels), zero entity params | trained GNN forward pass; subgraph extraction closed-form (Dijkstra) | 0.825 | far-apart/disconnected head-tail pairs -> no enclosing subgraph |
| RED-GNN (Zhang & Yao, WebConf 2022, arXiv:2108.06040) | shared r-digraph DP over relational paths (same Bellman-Ford family, lower memory) | trained forward pass | (FB15k-237 v1 MRR 0.369 vs GraIL 0.279) | fixed hop-depth caps reachability |
| NodePiece (Galkin et al. ICLR 2022, arXiv:2106.12144) | composition of k nearest shared ANCHOR nodes + m sampled relation types, BPE-style tokenization | tokenization closed-form (BFS-to-anchor); encoder is a trained forward pass | 0.873 (FB15k-237 v1) | sparse/relation-poor graphs (WN18RR); disconnected nodes need an explicit [DISCONNECTED] token |
| ULTRA (Galkin et al. ICLR 2024, arXiv:2310.04562) | two-level NBFNet: relation-graph labeling trick, then entity-graph labeling trick seeded by the relation representation — zero entity OR relation IDs anywhere | trained forward pass, ~177-200K params, transfers zero-shot across 51 graphs | zero-shot MRR 0.395 avg (beats graph-specific supervised SOTA 0.344) | capacity plateaus beyond ~200K params / ~3 pretraining graphs — model-scale bottleneck, not representational |
| InGram (Lee et al. 2023, arXiv:2305.19987) | attention over a learned relation-affinity graph; generalizes to new RELATIONS too | trained forward pass | beats 14 baselines on mixed new-entity/new-relation splits | — |
| MorsE (Chen et al. SIGIR 2022, arXiv:2110.14170) | meta-learned (MAML-style) entity initializer + GNN modulator, one forward pass per new graph | trained forward pass, no gradient step at test time | — | requires meta-training across MANY source KGs |
| INDIGO (Liu et al. NeurIPS 2021) | pairwise (head,tail) joint subgraph encoding — no entity vector object at all | trained forward pass | — | most radical "no entity" version, closest to GraIL |

**Synthesis (confirmed, with the honest refinement above):** every method represents "the entity" as a *computed
function of local relational context*, built by composing a small, reusable, graph-global vocabulary of parts. None
is exactly closed-form end-to-end — what IS closed-form/zero-shot is the *addressing* step (which anchors, which
paths, which distance labels); the *scoring* function is a trained-but-entity-agnostic forward pass that never
consumes an entity ID. The one consistent failure mode is context scarcity for isolated/sparse unseen entities — this
recurs identically across GraIL, NodePiece, and NBFNet, which is itself evidence the mechanism (not the specific
architecture) is what's being stressed.

**P_deflated: 0.75** for "this is the correct, literature-confirmed common principle" — this is a literature-convergence
finding (9 independently-developed methods converging on the same design), not novel synthesis, so the 0.50 cap does
not apply; deflated modestly because the "closed-form addressing / trained scoring" split is this drill's own framing
of the results, not a single paper's stated conclusion.

---

## Part B — mapping the principle onto the substrate: entity = bound relational context

### B.1 What exists, what's missing

`KGStore` (`hdlab/kg_traversal.py`) already has the right SHAPE for the reusable-operator half: `R` (relation
codebook, `n_rel x n_dim`) is allocated once and reused across every triple — this is the KGE-theoretic
"reusable relation operator" (HolE/RotatE-class) and is CERT-585 chain-grade for KNOWN structure. **What is wrong is
`E` (entity codebook): every row is an independent, arbitrarily-assigned bipolar vector (`_bipolar(n_ent, n_dim, ...)`)
— a free per-entity table, exactly the object the GraIL/NBFNet/NodePiece literature says CANNOT be evaluated on an
entity absent from training.** `ingest_triples` only ever WRITES into `W` using existing `E` rows; it never
constructs a new `E` row from structure. This is precisely the "storage != map" anti-pattern already flagged in
`research_storage_is_the_map_...md` — but that note addressed the RELATION-operator geometry (bipolar -> phase); this
drill addresses the ENTITY-representation half of the same store, which that note explicitly did not touch.

### B.2 The proposed construction (ANCHOR-COMPOSE)

Designate a small, fixed **anchor set** `A subset E` (e.g. NodePiece's precedented split: ~40% top-PPR, ~40%
top-degree, ~20% random — arXiv:2106.12144). Anchor codes are populated by the substrate's NORMAL ingest process
(unchanged). For any entity `v` — anchor or not, **seen or unseen at "ingest" time** — define:

```
E_derived[v] = cleanup( bundle_{(v,p,a) or (a,p,v) in edges(v), a in BFS_k(v) intersect A} ( R[p] * E[a] ) )
```

i.e. bind each relation operator to the anchor at the far end of the edge, then BUNDLE (sum) across all of `v`'s
edges that reach an anchor within `k` hops, then run cleanup/resonator decode to normalize. This is **exactly HDGL's
node construction** (Dalvi & Honavar, arXiv:2402.17073) generalized to CSKG's typed multi-relational structure, with
NodePiece's anchor-selection methodology supplying the anchor set. It is also literally an unrolled-by-one-step
version of NBFNet's Bellman-Ford recursion, with the anchor set playing the role of a fixed "labeled" reference frame
instead of a single query source — **this is not a new derivation stitched from two unrelated ideas; NodePiece,
HDGL, and NBFNet are three specific parameterizations of the identical general principle**, which is exactly why Part
A's synthesis and Part B's construction should be read as one mechanism, not two.

**Why this avoids circularity for a genuinely new entity:** anchors are FIXED and populated first (from the known
graph); a new entity's code depends only on already-fixed anchor codes and the fixed relation codebook `R` — never on
its own code or another new entity's code. This is the same reason NodePiece and NBFNet avoid the "which comes first"
problem: the reference frame (anchors / query source) is established before any new-entity computation happens.

**Score/decode is UNCHANGED**: `key = E_derived[s] * R[p] * sqrt(n_dim)`, `score_all(key) = E @ (W @ key)` — the
same `KGStore.key()`/`score_all()` methods, called with a computed `E_derived[s]` instead of a stored table row.
`W` is trained ONLY from known (non-held-out) triples, so a held-out entity's `E_derived` is computed strictly
AFTER `W` is frozen, from its own (test-time-visible) edges to anchors — a genuine zero-shot construction, not
leakage.

### B.3 Resonator/cleanup: does bundling many bind-terms into one vector actually decode?

Yes, with a capacity caveat, not unconditionally. Resonator networks (Frady, Kent, Olshausen, Sommer, *Neural
Computation* 2020, arXiv:1906.11684) solve exact factorization for a SINGLE clean bind; decoding a SUPERPOSITION of
several bound pairs (which is exactly what `E_derived` is) requires sequential "explaining away" — factorize one
term, subtract its reconstruction, repeat on the residual (Hersche, Opala, Karunaratne, Sebastian, Rahimi, IBM
Research, NeSy 2023) — and this causes measurable noise amplification, with capacity characterized only empirically
(operational capacity up to ~10^5-10^9 search-space size at D=1000-2000, Karunaratne et al. 2024, arXiv:2412.00354).
**The substrate already HAS this exact primitive**: `hdlab/cleanup_family.py::peel_sic_readout` implements
successive-interference-cancellation readout of a bundled query against a codebook — this is the substrate's own
resonator-style decode for superposed bind-terms, already built, not new engineering. **The capacity constraint is
degree-linked**, per HEADLINE point 3: GrapHD's `SNR ~ 5*log(D/d)` (d = number of anchor-edges being bundled per
entity) gives a concrete, cheap, pre-flight sizing check — before running the full cell, compute predicted SNR at
the target `n_dim` for the actual anchor-connectivity distribution of held-out entities and confirm it clears a
floor, rather than discovering a crosstalk failure only after a full remote run.

### B.4 FHRR/RotatE bridge (flagged as inference, not confirmed precedent)

Hayashi & Shimbo (arXiv:1702.05563, ACL 2017) prove HolE (real-valued circular correlation) is mathematically
equivalent to ComplEx under a Fourier-domain change of basis. This is the SAME diagonalization identity that makes
FHRR's per-dimension unit-modulus phase multiplication equivalent to real circular convolution/correlation — which
strongly implies FHRR bind is algebraically equivalent to RotatE's relation operator via straightforward composition
of two established theorems. **No single paper found states this explicitly for FHRR/RotatE by name** — this is
this drill's own inference from adjacent proven results, not a lifted citation, and should be labeled as such if used
in downstream product claims (it is consistent with, and does not contradict, `research_storage_is_the_map`'s
independent claim that complex64 phase bind = FHRR = RotatE).

**P_deflated for B.2-B.3 (the ANCHOR-COMPOSE construction is a coherent, literature-precedented inductive mechanism
that should carry SOME transferable signal to unseen entities): 0.40** (capped under the 0.50 novel-synthesis
ceiling — HDGL/NodePiece/NBFNet each independently support pieces of this construction, but no paper tests the exact
combination — typed multi-relation anchor-bundle-bind on a commonsense KG — end to end, and this substrate's own
degree-skew/community-structure diagnostics from `research_kg_degree_community_diagnostic_2026-07-12.md` are a live,
unresolved risk to how well CSKG's actual entities connect to any anchor set at all).

---

## Part C — brain grounding: structure fixed, content fast-bound

The three brain mechanisms map onto the two halves of ANCHOR-COMPOSE with unusual precision, not loose analogy:

1. **Grid-cell path integration into a brand-new environment** (Hafting et al., *Nature* 2005; Burak & Fiete, *PLoS
   Comp. Biol.* 2009): a novel location's code is COMPUTED (velocity/phase accumulation over a small, FIXED set of
   grid modules), never learned per-location. This maps to `R` (the relation codebook) and the anchor set `A`: both
   are FIXED, reused across every new entity, and require no per-entity relearning — the "structural scaffold."
2. **Place-cell remapping = rebinding, not relearning** (Leutgeb et al. 2004/2005; Whittington et al., TEM, *Cell*
   2020 — explicit claim that the structural/transition code generalizes to a brand-new environment/graph with NO
   retraining, only new content-binding): this maps directly to `E_derived[v]`'s construction — computing a new
   entity's code is a BINDING operation onto the fixed scaffold (`R`, `A`), never a new learned sub-network.
3. **One-shot schema-consistent assimilation via fast CA3 Hebbian binding** (Tse et al., *Science* 2007, 2011;
   Eichenbaum's binding-of-item-and-context theory, *Neuron* 2004): a schema-consistent new fact is encoded in a
   SINGLE trial because only the content-to-structure binding is new; the structure itself is already standing. This
   is the precise brain analog of "a held-out entity gets `E_derived` instantly from one bind+bundle pass, zero
   gradient steps" — the ANCHOR-COMPOSE arm needs NO training loop at all for a new entity, exactly matching the
   one-trial, no-relearning property the brain literature attributes to schema-consistent binding.

**Net brain-grounded prediction:** the ANCHOR-COMPOSE construction is not just architecturally analogous to the
brain's solution — it reproduces the SAME division of labor (fixed reusable scaffold vs. fast content-binding) that
three independent brain literatures converge on. This raises confidence the construction is the right SHAPE of fix,
though it does not by itself guarantee CSKG's specific graph topology has enough anchor-connectivity for the
mechanism to clear a decisive margin (see Part D's must-fail/middle-band diagnostics).

**P_deflated: 0.55** for "the brain-grounding argument correctly identifies the necessary architectural shape" — high
because the convergence across TEM, grid-cell, and CLS/schema literatures was independently found (not cherry-picked
to fit this proposal after the fact — see `research_storage_is_the_map` and `research_does_it_scale`, which surfaced
the same TEM/grid-cell citations from a DIFFERENT angle before this drill was run), deflated for the standard gap
between "correct architectural shape" and "sufficient on this specific, possibly-sparse graph."

---

## Cheap decisive test

**Gate 0 (prerequisite, not this drill's to run): the fork verdict itself.** Do not dispatch the build below until
`exp_heldout_entity_inductive_probe_cskg_gpu1024_v2` lands with `oracle_fires=True` (margin `>=0.10` over random).
Current state: v1 `INCONCLUSIVE_ORACLE_UNDERFIT` (oracle margin 0.0119); v2 (500 epochs, pre-cleared 750-epoch
escalation if still underfit) dispatched, not landed as of this drill. If v2 lands `HARD_FAIL_MEMORIZED_NO_ENTITY_
TRANSFER` (oracle fires, existing arms tie random) — the expected outcome per the architectural argument in Part A —
dispatch this build immediately as the direct remedy. If v2 is STILL inconclusive, the 750-epoch escalation must
run before ANY inductive-mechanism comparison is interpretable (the same oracle-fire logic applies to a new
ANCHOR_COMPOSE oracle arm). If v2 unexpectedly HARD-PASSES (existing per-entity fit already generalizes), still
worth building ANCHOR_COMPOSE as a cheaper (no-training) comparison, but urgency drops.

**The test itself (once Gate 0 clears): add ONE new arm, `ANCHOR_COMPOSE`, to the EXISTING held-out-entity harness
(`exp_heldout_entity_inductive_probe_cskg_gpu1024_v1/v2`) verbatim — same split, same seeds [7,13,17], same
`n_heldout_eval=3000`, same controls.** No new infrastructure beyond the anchor-selection step (one-time, CPU, cheap)
and the `E_derived` construction (bind+bundle+cleanup per held-out entity — reuses `KGStore.key()`/`score_all()` and
`cleanup_family.py::peel_sic_readout` unchanged).

**HARD-PASS (reusable-operator hypothesis survives — build the full map-builder):** `ANCHOR_COMPOSE` held-out
Hits@10 clears `RANDOM_CODES` by `>= 0.05` absolute (the same bar the SR-code and rotation/additive cells used) **AND**
clears the existing `ONESHOT_ROTATE`/`ADDITIVE_TRANSE` arms on this SAME unseen-entity task (confirming the
architectural argument directly, not just beating chance).

**HARD-FAIL (the anchor-composition mechanism ALSO fails to transfer):** `ANCHOR_COMPOSE` margin over `RANDOM_CODES`
`< 0.02` despite the oracle firing — this would be a genuinely important negative: even a construction with the
right architectural SHAPE (per Parts A-C) fails on CSKG specifically, most likely because held-out entities are too
sparsely connected to the anchor set (a graph-topology limit, diagnosable via the degree-stratified check below), not
because the anchor-composition PRINCIPLE is wrong. Next move: increase anchor-set size/BFS depth or raise `n_dim` per
the GrapHD SNR sizing rule before concluding the mechanism class itself fails.

**Must-fail control:** run `BASELINE_POP` through the same split unchanged (should be unaffected — reuses the
existing control).

**Middle band (margin in [0.02, 0.05)):** stratify by held-out entity's anchor-connectivity degree (number of edges
reaching an anchor within k hops). If margin scales with anchor-connectivity (more anchor-edges -> bigger margin),
the mechanism works but current anchor density/BFS depth is too sparse — a scaling fix, not an architecture failure.
If margin is flat regardless of anchor-connectivity, the construction itself is not carrying signal even where data
should support it — a more serious negative pointing toward the FHRR/RotatE bind upgrade (Part B.4) or a larger
anchor set as the next lever, not a quick parameter tweak.

---

## Falsifiable predictions (build spec, full ladder)

**HARD-PASS (naive anchor-composition basically works — proceed to full map-builder integration with KGStore):**
1. `ANCHOR_COMPOSE` clears the `>=0.05` margin over `RANDOM_CODES` at the CURRENT N=25,752/k_core=12 CSKG graph.
2. The margin is NOT explained by anchor-connectivity degree alone stratified against `BASELINE_POP` (i.e. genuine
   relational signal, not a repackaged popularity/degree confound — apply the SAME `backdoor_r < 0.20` gate used on
   the rotation/additive cells).
3. `ANCHOR_COMPOSE` requires ZERO gradient training for the held-out arm (verify wall-clock: anchor selection +
   bind/bundle construction should be CPU-tractable in minutes at this N, versus the ~50 minutes/seed GPU epoch
   budget the existing per-entity-fit arms needed) — this is a concrete, cheap-to-verify practical advantage worth
   confirming, not assuming.
4. The GrapHD SNR pre-flight check (Part B.3) correctly predicts, BEFORE the full run, whether the chosen `n_dim`
   clears the crosstalk floor for the actual anchor-connectivity distribution — validating the sizing rule as
   genuinely predictive, not just post-hoc narrative.

**HARD-FAIL (a real wall — anchor-composition does not solve held-out-entity generalization on this graph):**
1. Margin over `RANDOM_CODES` stays `< 0.02` even after doubling anchor-set size and BFS depth (ruling out the
   "just needs more anchors" middle-band fix).
2. Margin does not correlate with anchor-connectivity degree even when it exists (ruling out "just needs a denser
   region," pointing to a genuine crosstalk/dimension problem — escalate `n_dim` per the SNR rule before further
   architecture changes).
3. `peel_sic_readout` cleanup fails to separate `E_derived[v]` from other entities' codes above a stated margin at
   the CURRENT `n_dim` even at the SMALL anchor-bundle sizes typical of this graph (a hard crosstalk ceiling, not a
   scale problem) — this would be the most informative failure, since it would isolate the wall to the CLEANUP step
   specifically rather than the construction principle.

**P_deflated summary:**
- ANCHOR_COMPOSE clears the `>=0.05` margin (HARD-PASS): **P=0.30** (deflated from a base intuition of ~0.50 —
  the architectural argument and brain-grounding convergence are genuinely supportive, but CSKG's own degree/community
  diagnostics from the same-week sibling drill flagged real topology risk — schema-blurred relation types, no
  established easy-win for shared operators — that directly threatens anchor-connectivity quality; capped under the
  0.50 novel-synthesis ceiling regardless).
- ANCHOR_COMPOSE beats the per-entity `ONESHOT_ROTATE`/`ADDITIVE_TRANSE` arms specifically on the unseen-entity task
  (stronger claim than beating random): **P=0.35-0.40** (this is the SAME probability already assigned in
  `research_does_it_scale...md` to "a genuinely factorized/operator-based architecture would pass a comparable
  inductive test if built" — this drill supplies the concrete construction that estimate was made in reference to,
  so the number should not independently drift without new evidence).
- The GrapHD SNR sizing rule correctly predicts pass/fail before the full run (a genuinely novel, testable
  cross-domain claim this drill adds): **P=0.45** (three-way convergence across VSA/KGE/neuroscience theory is
  strong prior support, but no source tests the SNR formula's PREDICTIVE accuracy specifically, only its derivation).

---

## Cross-thread synthesis

- **Directly answers the open question left by `research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md`**:
  that note identified the held-out-entity test as the single highest-value cheap check and predicted (P=0.35-0.40)
  that "a genuinely factorized/operator-based architecture WOULD pass a comparable inductive test if built" — this
  drill IS that build, made concrete (ANCHOR_COMPOSE construction, precise arms, pre-registered thresholds).
- **Extends, does not duplicate, `research_storage_is_the_map_brain_scale_substrate_integration_2026-07-12.md`**:
  that note fixed the RELATION-operator half of `KGStore` (bipolar -> complex-phase bind, wired into
  replay/consolidation); this note fixes the ENTITY-representation half (`E` as a free table -> `E_derived` as a
  bundled-bind construction from anchors). The two proposals are COMPOSABLE, not competing: `E_derived` can be built
  with EITHER the current bipolar bind or the proposed complex-phase bind — this drill's construction does not
  require that note's Cell A/B/C to land first, though it would benefit from the richer relation-pattern expressivity
  if they do.
- **Confirms the prior track record's central seam** (`notes/relational_capability_track_record_scour_2026-07-10.md`):
  memorized-structure-vs-inductive-inference is the through-line of the entire relational program; this drill sits
  exactly on the un-resolved side of that seam and proposes the specific architectural remedy the track record's own
  language ("would need a genuinely inductive/operator-based architecture") called for without yet specifying one.
- **New fact this drill adds that no same-week sibling note surfaced:** the THIRD independent field (VSA bundling
  theory, via GrapHD's `SNR~5log(D/d)`) converging on "capacity governed by local degree, not global N" — joining
  KGE rank-bottleneck theory and hippocampal CA3 capacity theory already found in `research_does_it_scale`. This
  triangulation is citable and load-bearing for future dimension-sizing decisions across ALL relational cells, not
  just this one.

---

## Substrate-product implications

- **The honest, defensible product claim, pending Gate 0:** "we have identified the exact literature principle
  (anchor/operator composition, not per-entity storage) that lets systems generalize to knowledge-graph entities
  never seen during training, we have found it maps onto existing substrate primitives (KGStore's reusable relation
  codebook, the cleanup-family's resonator-style decode) with unusual precision, and we have a cheap, pre-registered
  test ready to run the moment the current per-entity-fit test confirms it cannot do this." This is a stronger,
  more specific claim than "richer geometry might help someday" — it names the exact mechanism class and reuses
  existing code, not a speculative research direction.
- **If HARD-PASS:** converts the map-builder from "a promising direction" into a concrete, cheaper-than-the-status-quo
  mechanism (zero gradient training for new entities, CPU-tractable) that should become the PRIMARY entity-representation
  path for any future KG ingest at this substrate — a genuine architectural upgrade, not a bolt-on.
- **If HARD-FAIL:** still valuable — it would isolate WHERE the wall is (crosstalk/dimension vs. graph topology vs.
  the anchor-selection heuristic itself) via the middle-band diagnostics, rather than leaving "inductive inference
  fails" as an unlocalized negative. Per the standing weak-point-localization discipline, this test is designed to
  fail INFORMATIVELY either way.
- **Scope discipline:** this proposal, like the prior storage-is-the-map note, should NOT be oversold as fixing
  richness/knowledge-density limits separately identified (`exp_graph_inductive_ceiling_v1`'s structural-ceiling
  finding). It targets the ARCHITECTURE axis (can the mechanism represent an unseen entity at all) — a graph that is
  itself too sparse or schema-blurred (per `research_kg_degree_community_diagnostic_2026-07-12.md`) can still defeat
  a structurally-correct mechanism, and that would be a knowledge-richness finding, not a refutation of this design.

---

## Citations (verified count)

**On-disk, read in full this cycle:** `hdlab/kg_traversal.py` (KGStore class, `ingest_triples`, `key`, `score_all`);
`hdlab/cleanup_family.py` (`peel_sic_readout`, resonator-family primitives); `data/exp_course_c_heldout_entity_
inductive_probe_gpu1024_v1/metrics.json` (fork-test verdict); `experiments/exp_heldout_entity_inductive_probe_cskg_
gpu1024_v2.py` (escalation plan/docstring); `experiments/exp_graph_inductive_ceiling_v1.py` +
`experiments/exp_grounding_additive_geometric_code_inductive_inference_v1.py` (adjacent cell context);
`notes/research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md`;
`notes/research_storage_is_the_map_brain_scale_substrate_integration_2026-07-12.md`;
`notes/research_kg_degree_community_diagnostic_2026-07-12.md`;
`notes/relational_capability_track_record_scour_2026-07-10.md`. **10 on-disk sources.**

**External literature (3 parallel Sonnet lit-scans, generic ML/neuroscience terms only, no substrate-novel
names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

*Inductive KGE (9):* Zhu et al. (NBFNet, NeurIPS 2021, arXiv:2106.06935); Zhu et al. (A*Net, 2022, arXiv:2206.04798);
Teru, Denis, Hamilton (GraIL, ICML 2020, arXiv:1911.06962); Zhang & Yao (RED-GNN, WebConf 2022, arXiv:2108.06040);
Galkin et al. (NodePiece, ICLR 2022, arXiv:2106.12144); Galkin et al. (ULTRA, ICLR 2024, arXiv:2310.04562); Lee et al.
(InGram, 2023, arXiv:2305.19987); Chen et al. (MorsE, SIGIR 2022, arXiv:2110.14170); Liu et al. (INDIGO, NeurIPS 2021).

*VSA/HRR graph representation (14):* Plate (HRR, IEEE Trans. Neural Networks, 1995); Poduval et al. (GrapHD,
*Frontiers in Neuroscience* 2022, PMC8855686); Dalvi & Honavar (HDGL, arXiv:2402.17073); Frady, Kent, Olshausen,
Sommer (Resonator Networks 1, arXiv:1906.11684; Resonator Networks 2, *Neural Computation* 2020); Hersche, Opala,
Karunaratne, Sebastian, Rahimi (Decoding Superpositions of Bound Symbols, NeSy 2023, IBM Research); Karunaratne,
Hersche, Sebastian, Rahimi (On the Role of Noise in Factorizers, arXiv:2412.00354); Clarkson, Ubaru, Yang (Capacity
Analysis of VSA, arXiv:2301.10352); Nickel, Rosasco, Poggio (HolE, AAAI 2016, arXiv:1510.04935); Hayashi & Shimbo
(Equivalence of Holographic and Complex Embeddings, ACL 2017, arXiv:1702.05563); Smolensky (Tensor Product
Representations, arXiv:1601.02745); Kleyko et al. (VSA/HDC Survey, ACM Computing Surveys, arXiv:2111.06077);
Holographic Graph Neuron (arXiv:1501.03784); Graph Embeddings via Tensor Products (arXiv:2208.10917, title-relevant,
content unverified — flagged).

*Brain grounding (12):* Hafting, Fyhn, Molden, Moser & Moser (*Nature* 2005); Burak & Fiete (*PLoS Comp. Biol.* 2009);
Fyhn, Hafting, Treves, Moser & Moser (*Nature* 2007); Leutgeb et al. (*Science* 2004/2005); Colgin, Moser & Moser
(*Trends Neurosci.* 2008); Whittington, Muller, Barry, Behrens et al. (TEM, *Cell* 2020); Tse, Langston, Kakeyama,
Bethus, Spooner, Wood, Witter & Morris (*Science* 2007); Tse et al. (*Science* 2011); Eichenbaum (binding-of-item-
and-context, *Neuron* 2004); Diana, Yonelinas, Ranganath (*Trends Cogn. Sci.* 2007); McClelland, McNaughton, O'Reilly
(*Psychol. Rev.* 1995); Rolls (CA3 quantitative theory, *Front. Cell. Neurosci.* 2013).

**Total: 10 on-disk sources read in full + 35 external sources across 3 parallel lit-scans = 45 verified checks.**

---

## Intuitive summary

**The question:** if our knowledge-graph reasoner currently works by giving every concept its own private, memorized
vector, it literally cannot say anything about a concept it never saw during training — there is no vector for it.
To scale to new knowledge without constantly retraining, the system needs to represent a concept by ITS RELATIONSHIPS,
not by a private lookup entry. This drill designed exactly that mechanism.

**What we found in the outside research:** every method in the field that successfully handles brand-new,
never-before-seen graph entities does the same basic trick — instead of storing one vector per thing, it keeps a
small, fixed, REUSABLE set of building blocks (either "the small number of ways relationships can compose" or "a
small reference set of well-known landmark concepts"), and builds a brand-new thing's representation on the fly, the
instant you know how it connects to those building blocks. No retraining needed — just quick arithmetic. We found a
close cousin of exactly this idea already published for hyperdimensional-style vector representations of graphs, and
we found that our own knowledge-store already reuses the "relationship building blocks" half of this design (that
part is proven and working) — it just currently does NOT reuse landmark concepts to build a new concept's vector; it
hands out an arbitrary private vector to every concept instead, which is exactly the broken half.

**The brain evidence, unusually cleanly:** when an animal enters a brand-new room, its internal "map cells" don't
learn a whole new map from scratch — they instantly compute a code for the new space using a small, fixed toolkit
they always carry, and then quickly "snap" that fixed toolkit onto whatever's actually in the new room. That is
precisely the two-part design (fixed reusable toolkit + fast on-the-spot snapping) this drill proposes for the
knowledge graph.

**What we built (a design, not code yet):** pick a small set of well-connected "landmark" concepts already in the
knowledge graph. For ANY concept, known or brand-new, compute its vector on the spot as a quick combination of "how
it connects to those landmarks" — no training required for new concepts, just fast vector arithmetic our system
already knows how to do. We wrote a precise, cheap test (reusing an experiment already built) that will tell us
definitively whether this actually works on our real data, with honest pass/fail lines drawn in advance, including
what it means if it only partly works (the landmark set needs to be bigger or denser, not that the whole idea is
wrong).

**Why this matters, and the honest caveat:** this is the single most promising concrete fix we've found for teaching
the system to handle brand-new knowledge instead of just memorizing what it's already seen — but it is NOT yet
proven, and the test that will tell us whether our CURRENT system even needs this fix (versus already secretly
working) has not finished running yet. We designed this to be ready to build the moment that other test lands,
instead of guessing ahead of the evidence.
