# OOD and Compositional Generalization in the Substrate — M3 Implications
# Research drill: Sonnet director, 2026-07-02

---

## PRIOR-WORK OVERLAP CHECK (substrate-KB query mandatory discipline)

Ran 8 substrate-KB queries before this write. Relevant prior-work found:

1. **Compositional generalization** — notes/wave14e_hierarchical_composition_research.md:
   composition with cleanup is depth-5-6 reachable; WITHOUT cleanup K=512 dies at N=4096.
   notes/research_BetX_skill_composition_2026-05-21.md: d=25 composition-depth cliff matches
   VSA noise math + transformer CoT bounds; position-indexed binding is the right scheme.

2. **Correlated-key / distributional mismatch** — Löwe α_c(ρ) ≈ 0.138(1-ρ²) is a CG
   substrate-physics-law atom (backup 2026-07-01). notes/exp_dev_to_research_CONTINUAL_REALDATA:
   STATIC/PRECOMPUTED operations survive real correlated data; DYNAMIC/ONLINE operations are
   fragile (frequency-decay collapses at 0.57; neurogenesis over-fragments).
   arXiv:2503.09518, arXiv:2508.01395: STRUCTURED/CORRELATED patterns REDUCE alpha_c.

3. **Cross-domain retrieval failure** — notes/research_drill_cross_domain_analogy_mechanisms:
   KGE cross-domain failure is a structural theorem (entity manifolds M_A, M_B disjoint;
   no shared objective). RotatE cross-domain Hits@1 = 0.244 vs 0.899 within-domain.
   Gentner SMT: humans use relational systematicity, not surface match.

4. **Refuse-gate OOD detection** — HARD_FAIL (substrate_audit_chain_coherence_benchmark
   ARM 3): substrate confidence alone cannot separate known from unknown — no tau gap,
   refuse_095 without in-coverage F1 drop. BGE confidence alone is a categorical failure
   for OOD detection. Conformal calibration research note
   (research_drill_substrate_conformal_calibration_2x_2026-06-11.md) filed but not closed.

5. **Multihop vs compositional depth** — Atom 19 d50/55 CG, multihop d=100 evidence:
   substrate traverses chains. BUT: multihop is SEQUENTIAL retrieval along existing edges;
   compositional SYNTHESIS (inferring new combinations from stored parts) is a different
   operation not yet tested.

6. **Hierarchical composition noise floor** — wave14e: depth-3 with B=8 gives K_total=512,
   DEAD at N=4096. Hierarchical composition requires cleanup at every level (Plate 1995,
   Kanerva 1996 BSC, Eliasmith SPA). Without cleanup: noise multiplies by depth. With
   cleanup: only cleanup error probability compounds (0.95^L per level).

7. **Dense-Hopfield OOD** — Dim H falsification: distributional shape (uniform vs Zipfian)
   was FLAT in underloaded regime. But CLT-washout is the root cause: at low alpha,
   superposition noise averages out. OOD AT CAPACITY EDGE (high alpha) is UNEXPLORED.

NO prior cell directly tests: (a) substrate retrieving A+B from A-only + B-only storage,
(b) queries at distribution edge revealing shape sensitivity, or (c) conformal calibration
closing OOD detection. All three are genuinely new cells.

---

## HEADLINE

**Substrate expected OOD behavior: partially robust, partially blind.**

The substrate's RETRIEVAL is robust to noise (Dim S/T CG; σ cliff at (0.05, 0.10]).
Its CAPACITY degrades gracefully under correlated keys (Löwe physics law; alpha_c(ρ)
suppression is predictable, not catastrophic for ρ < 0.7). Its REFUSE-GATE is a known
failure for OOD detection (ARM 3 HARD_FAIL; no tau gap).

What has NEVER been tested: whether the substrate can answer compositional queries
(A+B retrieval when only A and B are stored separately). This is the "sum of parts" or
"bundle intersection" question — the most load-bearing OOD scenario for M3 conversational
use.

**P_deflated (substrate handles M3-relevant OOD adequately without cortex intervention):
0.30-0.40.** Calibration notes:

- Correlated-key and noise-OOD: probably fine (CG evidence for graceful degradation).
- Compositional-query OOD (A+B from A-only+B-only): UNKNOWN; mechanistic argument
  below suggests PROBABLY FAILS without cleanup; P(succeeds) ~ 0.20-0.35.
- OOD confidence detection for refuse-gate: KNOWN FAIL (ARM 3 HARD_FAIL). Cortex MUST
  own this.
- Domain-shift OOD (entity manifold mismatch): structurally the same as KGE failure;
  P(fails badly) ~ 0.65-0.75 without explicit bridging.

**M3 architecture verdict: cortex MUST own OOD detection and compositional synthesis.
Substrate alone cannot handle it. Refuse-gate is the right M3 primitive but needs a
stronger signal than raw substrate confidence.**

---

## 2x DRILL — TOP OOD SCENARIO: COMPOSITIONAL-QUERY RETRIEVAL

### Scenario: Query for A+B when substrate has only A-alone and B-alone stored.

**Concrete M3 example**: User asks "What do neuroscientist Eric Kandel's papers on long-term
potentiation say?" Substrate has stored: (a) Kandel-paper-LTP (general), (b) LTP-mechanism
facts (independent), but NEVER Kandel+LTP as a joint binding. Does querying
bind(Kandel, LTP, paper) retrieve the stored individual components?

**Pass 1 — Why the substrate SHOULD handle this (optimistic read):**

HDC superposition stores multiple patterns. A bundle B = sum_i p_i means queries with
partial-key overlap can retrieve relevant patterns. In the Hopfield/Hebbian
formulation W = sum_i p_i * p_i^T, energy minimization from a partial cue q that
overlaps BOTH p_A and p_B will flow toward whichever attractor has the highest cosine
with q. If q = (A + B)/2 (average of stored patterns), and A, B are orthogonal
with cos(A, B) ~ 0, then W*q = W*A/2 + W*B/2 ~ A/2 + B/2 — the query effectively
RETRIEVES a superposition of both, not a clean answer.

This is NOT composition; it is a MIXTURE retrieval. The substrate returns "somewhere
between A and B" — not the INTERSECTION of A's bindings with B's bindings. For
factual retrieval ("who wrote it"), this gives hallucination-like behavior: partial
evidence from both A and B competes in the attractor dynamics.

**Pass 2 — Why the substrate SHOULD FAIL this (pessimistic read, more mechanistic):**

The fundamental problem is that HDC/Hopfield stores BUNDLES (superpositions of patterns)
and retrieves the NEAREST STORED PATTERN. Compositional retrieval of A+B from stored
{A, B} requires that the query q = bind(A-key, B-key) intersects BOTH A's attractor
basin and B's attractor basin simultaneously. This is NOT a property of standard
Hopfield dynamics — the energy landscape has basins around A and B separately; a midpoint
query falls in whichever basin it is geometrically closer to.

Three substrate mechanisms that COULD enable partial compositional retrieval:

1. **Bundle intersection via outer product** (FHRR): if patterns are structured as
   role-filler bindings, a query can UNBIND a specific role and check cosine against
   fillers. E.g., bind(AUTHOR_ROLE, Kandel) * bind(TOPIC_ROLE, LTP) stored as a joint
   tuple. Retrieval of bind(TOPIC_ROLE, LTP) query would unbind and match. BUT: this
   requires the JOINT binding to have been stored. If only A = bind(AUTHOR, Kandel) and
   B = bind(TOPIC, LTP) were stored separately WITHOUT a joint tuple, FHRR bundle
   intersection of the query against two separate patterns CANNOT reconstruct the
   joint binding — you get the nearest stored pattern, not their intersection.

2. **Partial overlap threshold retrieval** (conformal calibration): if A and B share
   a common role (e.g., both tagged as "knowledge_type:neuroscience"), a query that
   includes that shared tag would retrieve both A and B separately (two attractor
   basins). But the query ANSWER must then be synthesized from two retrieved patterns —
   and synthesis is NOT a substrate operation; it requires cortex-level combining logic.

3. **Resonator network** (factorization-in-superposition): resonator networks CAN
   recover A from a superposition bundle if the query specifies constraints. But
   resonator ceiling at N=4096 is 3-6 factors (wave14e + BetX CG). Compositional
   retrieval of A+B from A+B jointly would require factorizing a degree-2 product from
   N-dimensional noise — inside the ceiling, but only if the JOINT tuple was stored.

**Synthesis:** The substrate CANNOT perform compositional retrieval (retrieve A+B
independently from stored {A, B}) without either (a) storing the joint binding at write
time, or (b) cortex orchestrating two sequential retrievals and combining answers.
This is a HARD ARCHITECTURAL BOUNDARY, not a tuning failure.

The correct M3 architecture for compositional queries: cortex decomposes the composite
query into sub-queries, executes them sequentially against substrate, and synthesizes
the answer. Substrate handles each sub-query independently. This is Phase 1 LLM router
behavior — it IS the right M3 design, but the substrate itself is not doing composition.

**Root prediction**: P(substrate natively handles compositional queries) = 0.15-0.25.
P(cortex sequential decomposition works) = 0.65-0.75 (inherits from individual
retrieval CG results per sub-query).

---

## TOP-5 RANKED OOD SCENARIOS (informativeness × cheapness)

### Rank 1: Compositional-query retrieval — A+B from stored {A only, B only}
**Why most informative**: Tests the substrate's sum-of-parts claim directly. M3 agents
will constantly receive composite queries. If substrate fails this, cortex must ALWAYS
decompose — major architectural implication.
**Cell cost**: ~20 min CPU. Small N=4096, K=50 patterns, sweep over 4 query modes
(joint-stored, A-only-query, B-only-query, A+B-composite-query). 3 seeds.
**Falsifiable prediction**: HP if composite query retrieves top-K hit with cosine
score indistinguishable from matched-joint-stored pattern (within 10%). HF if composite
query falls to cosine < 0.5 * matched-single pattern (returns wrong attractor).
**Prior overlap**: NO prior cell. NOVEL.

### Rank 2: Correlated-key OOD (Löwe sweep verification + capacity edge)
**Why informative**: Löwe α_c(ρ) ≈ 0.138(1-ρ²) is a SUBSTRATE_PHYSICS_LAW CG atom
but the distribution-EDGE behavior (ρ → 0.8-0.9 AND alpha near alpha_c simultaneously)
is untested. Real OOD queries in M3 often have correlated key structure (user asks
about related concepts written together). If correlated-key + high-load collapses
retrieval, M3 needs explicit load management.
**Cell cost**: ~45 min CPU. Extend existing correlated-key sweep to (ρ, alpha) joint
grid, adding ρ ∈ {0.5, 0.7, 0.85} × alpha ∈ {0.08, 0.11, 0.14}. 3 seeds.
**Prior overlap**: Löwe CG atom confirmed formula but did NOT explore joint (ρ, alpha)
surface. INCREMENTAL (extends existing CG).

### Rank 3: OOD confidence calibration — does substrate confidence signal OOD vs in-dist?
**Why informative**: ARM 3 HARD_FAIL showed BGE confidence alone fails. But that test
used a pre-trained KGE confidence signal. Substrate-native confidence (cosine of query
to nearest attractor, normalized by mean in-distribution cosine) has NOT been tested
for OOD-vs-in-dist discrimination. If substrate cosine has a useful gap (even if weak),
conformal calibration can convert it to a valid p-value, enabling a principled refuse-gate.
**Cell cost**: ~30 min CPU. Store M=200 facts, calibrate conformal p-value distribution
on held-out 20%, query 50 OOD facts (same domain, different entity combinations). Compare
substrate-native cosine gap to ARM 3 (BGE) gap.
**Prior overlap**: conformal calibration research drill exists (2026-06-11) but no cell
was dispatched. NOVEL cell, informed by prior drill.

### Rank 4: Distribution-edge shape sensitivity — Dim H at alpha = 0.12 (near capacity)
**Why informative**: Dim H falsification showed distributional shape (uniform vs Zipfian)
is flat at underloaded alpha. CLT-washout explains this (at low alpha, superposition
noise averages out). But at alpha ≈ 0.12 (near alpha_c = 0.138), CLT-washout weakens
and rare-pattern OOD (low-frequency queries) may degrade relative to common queries —
shape sensitivity REACTIVATES at the capacity edge. Missed this before because we only
tested underloaded regime.
**Cell cost**: ~25 min CPU. Re-run Dim H cell at alpha ∈ {0.05, 0.08, 0.11, 0.13}
with write distribution Zipfian (s=1.0) and uniform. At each alpha: compare retrieval
accuracy for frequent (top-10%) vs rare (bottom-10%) patterns. 3 seeds.
**Prior overlap**: Directly extends Dim H HF with regime condition. INCREMENTAL.

### Rank 5: Novel entity in composite query (domain-shift OOD)
**Why informative**: User mentions an entity NOT stored at write time (e.g., asks about
"Squire" when only "Kandel" is stored). The partial-cue overlap (shared "memory,paper,
neuroscience" context bindings) might retrieve the Kandel attractor — which is WRONG
but may be PLAUSIBLE. This is the hallucination-generator scenario: confident wrong
answer because partial-match cosine is above refuse threshold. Tests whether refuse-gate
threshold (calibrated on known entities) also rejects genuinely unknown entities.
**Cell cost**: ~20 min CPU. Store M=100 entity-topic bindings. Query 50 known entities
(should retrieve, cosine above threshold) + 50 novel entities with SAME topic bindings
(should refuse). Measure false-accept rate. 3 seeds.
**Prior overlap**: Extends ARM 3 design (substrate-audit_chain_coherence) but using
substrate-NATIVE cosine instead of BGE confidence. ARM 3 failed with BGE; this test
isolates whether native-cosine signal is better. INCREMENTAL.

---

## CHEAPEST DECISIVE EXPERIMENT — CELL DESIGN

### Cell: `ood_compositional_query_v1` (Rank 1)

**Anchor**: `ood_cq_v1`
**Scientific question**: Can the substrate retrieve a composite fact (A+B) when it has
stored only component facts (A-alone, B-alone) — vs explicitly stored joint fact (A+B)?

**Pre-reg envelope:**
- HARD_PASS: composite-query cosine within 0.10 of joint-stored cosine for >=70% of
  query pairs. This would mean substrate IS performing some partial compositional retrieval.
- HARD_FAIL: composite-query cosine < 0.50 of joint-stored cosine for >=70% of query
  pairs. Substrate treats composite query as noise; retrieves one component or neither.
- MIDDLE_BAND: otherwise.

**Design:**
```
N = 4096, M_joint = 50, K_components = 2 per joint fact, 3 seeds.

WRITE phase:
  - 50 joint bindings: p_AB = bind(role_A, vec_A) * bind(role_B, vec_B)
    stored as one pattern. (JOINT condition.)
  - 50 "component-only" pairs: p_A = bind(role_A, vec_A) alone,
    p_B = bind(role_B, vec_B) alone, stored as TWO separate patterns.
    (SEPARATED condition.)
  - All patterns stored in same Hebbian W.

QUERY phase (4 arms):
  ARM 1 (JOINT control): query q = p_AB. Expected: high cosine to stored p_AB.
  ARM 2 (A-only): query q = p_A. Expected: retrieves p_A or p_B depending on
    which attractor q falls into.
  ARM 3 (B-only): query q = p_B. As above.
  ARM 4 (COMPOSITE from components): query q = (p_A + p_B) / 2 normalized.
    Question: does this retrieve p_AB, or does it split between p_A and p_B?

DISCRIMINATOR: For each of the 50 joint facts:
  - measure cosine(query_arm4_retrieved, p_AB) — composite query to joint-stored pattern
  - compare to cosine(query_arm1_retrieved, p_AB) — joint query to joint-stored pattern
  - ratio: r = cosine_arm4 / cosine_arm1
  - r > 0.90: composite query is nearly as good as joint query (PARTIAL COMPOSITION)
  - r < 0.50: composite query fails to retrieve joint pattern (NO COMPOSITION)

CONTROL for SEPARATED condition:
  - query q_sep = (p_A_sep + p_B_sep) / 2 against W containing only separated components
  - check which attractor q_sep lands in (p_A or p_B? or intermediate noise?)

CARDINALITY gate: HARD_FAIL if any arm has fewer than 45/50 successful retrievals
  (prevents phantom-pass from silent exceptions — CARDINALITY_OK discipline).
```

**Runtime estimate**: N=4096, M=100 total patterns (50 joint + 50 sep), 4 arms,
3 seeds. Expected ~15 min CPU. Fits local_cpu_queue smoke; FULL on remote_cpu_queue.

**SMOKE gate**: run at N=1024, M=20, 1 seed. Verify all 4 arms execute, no silent
exceptions, CARDINALITY >=18/20.

**FALSIFIABLE predictions:**

HP: Substrate achieves r > 0.90 for composite-query arm. Would mean VSA superposition
DOES support partial compositional retrieval via average-query. P_deflated = 0.20
(mechanistic argument above strongly predicts failure; this outcome would be surprising
and require theoretical explanation — most likely: stored joint pattern was "close
enough" to average of components that it lands in the right basin).

HF: Substrate achieves r < 0.50 for composite-query arm. Mechanistic expectation:
average of two stored components falls between two attractor basins and slides to the
nearer one (p_A or p_B), NOT p_AB. P_deflated = 0.65 (this is the predicted outcome).

MIDDLE_BAND interpretation: r ∈ (0.50, 0.90) — partial composition. Substrate weakly
generalizes; would need conformal threshold to be useful.

---

## M3 ARCHITECTURE IMPLICATIONS

### 1. Compositional queries require cortex decomposition (structural)
The substrate CANNOT compose A+B from stored {A, B} independently (per mechanistic
argument above). M3 Phase 1 cortex (LLM router) MUST decompose composite queries into
sequential sub-queries. This is an ARCHITECTURAL REQUIREMENT, not a capability gap to
close experimentally.

Implementation: cortex parses user query into slot-filler structure (WHO, WHAT, WHEN,
WHERE roles), issues separate substrate retrieval per slot, then synthesizes the joint
answer. This is the Phase 1 LLM router's job description exactly — no new architecture
needed, just an explicit call-out that the router MUST do this for correctness.

### 2. OOD detection cannot rely on substrate confidence alone (CONFIRMED HARD_FAIL)
ARM 3 result is load-bearing: BGE confidence alone fails OOD detection. Substrate-native
cosine (Rank 3 cell above) is an open question, but the prior is bearish. M3 must use
conformal calibration on top of whatever native signal exists, OR use cortex-level
OOD detection (e.g., explicit novelty-detection module fed by the cortex, not substrate).

Specific cortex primitive needed: a lightweight novelty scorer that maintains a running
mean + variance of in-distribution cosine scores and computes a z-score or p-value for
each incoming query. This is a 5-line module sitting above the substrate retrieval call,
not inside the substrate.

### 3. Distribution-edge OOD: refuse-gate tuning must account for load
The refuse-gate V_REL sweep established a physics law: threshold ~ sqrt(2 * log V_REL / N).
But this is an IN-DISTRIBUTION calibration. At capacity edge (alpha → alpha_c), the same
threshold over-refuses because cosine scores compress. M3 must LOWER the refuse threshold
as substrate load increases (i.e., as M/N approaches alpha_c). A load-sensitive refuse
gate: tau(alpha) = tau_0 * sqrt(1 - alpha / alpha_c) is a natural correction.
NOT experimentally verified; file as directional recommendation pending Rank 2 cell.

### 4. Correlated-key OOD: write-time decorrelation is the fix, not query-time
From the CONTINUAL_REALDATA CG atom: "DECORRELATE BEFORE STORAGE" is the unanimous
fix (DG lateral inhibition, spin-glass cluster breaking, sparse-write, decorrelated replay).
For M3, this means the cortex's WRITE PIPELINE must include a decorrelation step before
handing facts to the substrate. Prototype: whiten entity embeddings before Hebbian
storage (linear operation, O(N^2) one-time cost, O(N) per-write cost).

### 5. Domain-shift OOD: M3 must use explicit partition logic
The cross-domain analogy drill established that entity manifolds M_A, M_B are
geometrically disjoint if co-trained against separate objectives. M3 Phase 1 should
partition the substrate by domain (e.g., separate W matrices per domain, or block-
diagonal structure) so that cross-domain queries are routed to the right partition
rather than asking a single W to bridge disjoint manifolds.
This is the PARTITION primitive from the Wave 3 bounded-capacity cell design.

---

## SUMMARY TABLE

| OOD scenario                          | P(substrate handles it) | M3 cortex primitive needed         | Cell priority |
|---------------------------------------|-------------------------|------------------------------------|---------------|
| Compositional A+B from {A,B} stored   | 0.15-0.25               | Sequential sub-query decomposition | RANK 1        |
| Correlated-key high-load              | 0.55-0.65               | Write-time decorrelation           | RANK 2        |
| Novel-entity in familiar-topic query  | 0.25-0.40               | Conformal OOD detect + refuse      | RANK 5        |
| Distribution-edge shape sensitivity   | 0.45-0.60 (regime-dep)  | Load-sensitive refuse threshold    | RANK 4        |
| Native cosine OOD discrimination      | 0.30-0.45               | Conformal calibration wrapper      | RANK 3        |
| Domain-shift (manifold mismatch)      | 0.10-0.20               | Explicit domain partitioning       | NOT RANKED    |

**Bottom line P_deflated** (substrate handles any one M3 OOD scenario without cortex):
**0.30-0.40** (range reflects uncertainty on native-cosine OOD discrimination).

**Recommended dispatch sequence:**
1. Smoke `ood_cq_v1` locally (15 min) — cheapest decisive test, binary outcome.
2. If Rank 1 HARD_FAIL (predicted): immediately closes the compositional-query arch
   question and frees cortex design to assume sequential sub-queries are MANDATORY.
3. Rank 3 (OOD confidence calibration) follows — informs refuse-gate conformal wrapper
   design, which is needed before ANY M3 conversation-layer safety can be validated.
4. Rank 2 (correlated-key + capacity edge joint grid) — confirms write-time decorrelation
   engineering priority.

---

## FALSIFIABLE HYPOTHESIS PAIR (for pre-reg)

**HP (CHAIN_GRADE candidate):** Substrate handles OOD inputs that differ only in NOISE
or LOAD LEVEL (per Dim S/T CGs); the precision cliff at sigma ∈ (0.05, 0.10] and
refuse-gate V_REL physics law adequately characterize the substrate's OOD boundary for
IN-DISTRIBUTION-SHAPE OOD. P_deflated = 0.65.

**HF (HARD_FAIL forcing):** Substrate CATASTROPHICALLY fails OOD inputs that require
COMPOSITIONAL INFERENCE (A+B from {A,B}) or DOMAIN-SHIFT (novel entity in stored-topic
context), and its native confidence signal cannot distinguish these OOD inputs from in-
distribution inputs. M3 REQUIRES cortex-layer OOD detection + sequential decomposition
as architectural primitives, not as optional enhancements. P_deflated = 0.60.

(Both HF and HP are simultaneously partly-true across different OOD sub-categories —
the drill's load-bearing finding is that OOD is NOT a single axis but at least FOUR
structurally distinct failure modes, each requiring a different cortex primitive.)
