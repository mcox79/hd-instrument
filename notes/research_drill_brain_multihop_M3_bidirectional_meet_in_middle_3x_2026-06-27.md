# RESEARCH 3x DRILL: brain mechanism #3 — bidirectional meet-in-the-middle for multi-hop reasoning

**Date:** 2026-06-27
**Slot:** M3 brain-mechanism drill slot 3 (companion to slots 1/2)
**Trigger:** USER directive — 3-angle drill (math/search-algorithms, brain/neuroscience, cross-domain) with substrate-native-path + cell-spec stub + audit of prior "Cell C bidirectional" attempt
**Discipline:** 0.20 calibration deflation; novel-synthesis P cap 0.50; brain-existence +0.10 prior; generic terms in any web query (none needed — internal evidence sufficient); META_M7 rail mandatory for any dispatch
**Plain-English headline:** brain halves multi-hop search depth by running it from BOTH ends and matching in the middle; substrate has tried this twice (v1 + v2_META_M7) and the result is consistent and chain-grade as a TOP-1 RANKER (0.62 lift over forward-only 0.32) — BUT it has NEVER worked as a ROUTING signal (mean_midpoint_cosine=0.000) and was NEVER tested at depth >5 where the BFS sqrt(N) advantage compounds.

---

## 0. HEADLINE — what the substrate already showed, and the un-tested adjacency

**Existing landed evidence (production, V_C=200, depth=5, 3 seeds, N=8192, META_M7 rail PASS):**

| Cell | Arm | top1 | Verdict family |
|------|-----|------|---------------|
| `substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail` | BIDIR_MEET_MID | **0.620** (cv=0.064) | HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL |
| same | SINGLE_FWD_v1regime (1000-binding W) | 0.323 | (rail) |
| same | REPRODUCE_PV2 (2000-binding W) | 0.122 | (META_M7 rail ok) |
| same | BIDIR_MEET_HOP2 mean_midpoint_cosine | **0.000** | (state-cosine probe — NO routing signal) |
| `gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7` | PART_BIDIR_COLLIDE | 0.658 | MIDDLE_BAND_ROUTING_PARTIAL |
| same | PART_NAIVE_CENTROID | 0.662 | (BIDIR did NOT beat naive centroid as router) |
| same | PART_FLY_LSH | 0.602 | (alternative router) |
| same | PART_ORACLE (ceiling) | 0.955 | (oracle bound) |
| `gap1_multihop_ldpc_rts_bidirectional_v2_meta_m6_rail` | LDPC_BIDIR | 0.213 (cv=0.014) | SANITY_BREACH (baseline out-of-band, mechanism still useful) |
| same | RTS_SMOOTHER | 0.213 (cv=0.014) | SANITY_BREACH |
| same | BACKWARD_ONLY | 0.128 | (5-seed reverse-replay alone) |
| same | SOFT_FWD | 0.213 | (forward-soft) |

**Two crucial facts the existing data already settles:**

1. **Bidirectional MEET as a TOP-1 RANKER on full V_C is CHAIN-GRADE at depth-5.** v2 META_M7 rail PASS, cv=0.064, lift over single-fwd-v1regime = +0.297 (0.620 vs 0.323). The METHOD WORKS. (Caveat: the rail compares against the v1 1000-binding regime not the 2000-binding pointer-v2 0.122 regime; honest framing = "bidirectional revives chain-grade ranking; the depth-5 absolute lift over the saturated regime is +0.498 if compared against pointer-v2-0.122 but +0.297 against the matched-binding rail. The matched-binding rail is the honest number per META_M7.")

2. **Bidirectional MEET as a ROUTER (partition selection) is NOT a routing signal.** PART_BIDIR_COLLIDE 0.658 is statistically indistinguishable from PART_NAIVE_CENTROID 0.662; BIAS_P (anisotropy / bias plate from Mu-Viswanath META rules) stands; verdict explicit: "Bidirectional state IS NOT a substrate-native routing signal at HP threshold." The state-cosine probe `mean_midpoint_cosine=0.000` was the leading indicator and the routing cell falsified the steelman.

**What has NEVER been tested (the proposed cell's true contribution):**
- depth >5 (depth 7 / 9 / 11) — where bidirectional's BFS sqrt(N) advantage compounds; today we only have depth=5
- explicit FORWARD_2HOP_ONLY control to PROVE the meeting helps and not just the shorter chain
- compound-error scaling check: if forward-only per-hop=0.69, then forward-2hop accuracy SHOULD be ~0.476 (=0.69^2); we should measure this directly to discriminate "meeting helps" from "shorter chain helps"
- RANDOM_MEET_BASELINE control to discriminate "true meet at correct midpoint" from "meet at any midpoint"
- non-bipolar (FHRR phase / sparse-bipolar) substrate variants
- learned reverse-W instead of W.T (substrate has sequence-binding primitive for reverse atoms; CERT 586)

**Decision:** the proposed cell is NOT a duplicate of v1/v2. It is the **DEPTH-SCALING + CONTROL-DISCRIMINATION** extension. Dispatch warranted, but framed as "scaling-law cell" not "does bidirectional help" (already answered yes). The depth axis is where the brain mechanism's analytical advantage actually IS — at depth-5 the substrate gain is 0.50/0.32 = 1.55x; at depth-9 the analytical prediction is closer to (0.69^4)/(0.69^9) = 1/0.69^5 = ~6.5x.

---

## 1. ANGLE 1 — MATHEMATICAL / SEARCH ALGORITHMS

### 1.1 Bidirectional BFS, Dijkstra, A* (Pohl 1971)

Classical bidirectional search: run BFS simultaneously from source S and target T; expand frontier on both sides; terminate when frontiers intersect. **Branching factor b, depth d: unidirectional cost O(b^d); bidirectional cost O(b^(d/2)) + O(b^(d/2)) = O(2 * b^(d/2)).** Exponential reduction in d/2 — the "halving" is in the EXPONENT, not just the depth. Memory cost scales similarly (must store both frontiers).

Pohl 1971's bidirectional A* generalizes this to weighted graphs; admissibility requires the two searches' heuristics be CONSISTENT, i.e., both estimate the SAME meeting cost. Goldberg-Harrelson 2005 "Computing point-to-point shortest paths" formalized the meeting-criterion for correctness — naive bidirectional Dijkstra terminates when ANY node is settled in both, but the FIRST shared-settled node is NOT necessarily on the optimal path. Correct termination: terminate when sum-of-settled-distances >= shortest-path-found-so-far.

**Substrate mapping:** the substrate's "branching factor" is V_C (200 atoms per position) and the "depth" is the chain hop count. Forward-only depth-5 explores V_C^5 = 3.2e11 nominal candidates (collapsed by per-hop cleanup to top-1 = depth-5 = 0.122). Bidirectional 2.5+2.5 hops on each side explores V_C^2.5 = ~5660 per side; if both sides cleanly converge to the true midpoint, the meeting test is O(V_C) cosine evaluations. **The substrate's existing 0.620 top1 at depth-5 / midhop=2 is consistent with this — both sides converge enough that argmax over V_C=200 candidate-Z's recovers ground truth 62% of the time, vs 32% forward-only.**

**Key prediction from classical theory:** at depth-7 (mid=3), bidirectional should compound forward and backward each over 3-4 hops while forward-only compounds 7. Predicted scaling: forward-only-depth-7 = 0.69^7 = 0.074; bidirectional-meet-at-3 = something like sqrt(0.69^7) ≈ 0.272 (very rough — the actual scaling depends on whether the meeting test itself loses accuracy with deeper backward paths). **Discriminating prediction: at depth-7, bidirectional should be roughly 0.20-0.35 while forward-only is 0.05-0.10 — a 3-7x relative lift, which is much stronger evidence than depth-5's 2x.**

### 1.2 Meet-in-the-middle attacks in cryptography (Diffie-Hellman, 2DES)

Diffie-Hellman 1977 introduced meet-in-the-middle for 2DES key search: brute-force on 2 * 56-bit keys is 2^112; MITM reduces to **2 * 2^56 in time + 2^56 in memory** by computing all 2^56 forward encryptions of the known plaintext, all 2^56 backward decryptions of the known ciphertext, and finding matches. **Time-memory tradeoff is fundamental: trading O(2^d) time for O(2^(d/2)) time + O(2^(d/2)) memory.**

**Substrate insight:** the v1/v2 cell's bidirectional rank arm spends O(V_C) memory (V_C backward-states per query). For the proposed cell at deeper depths (7, 9), we could PRECOMPUTE all backward states from each candidate Z ONCE per query (storing V_C * (depth-mid) state vectors = V_C * 4 * N = 200 * 4 * 8192 * 4 bytes = 26 MB) — same time/memory tradeoff as MITM. This is what the current arm does and is fine; bypass storage by streaming if depth grows too far.

**MITM "salting" insight:** crypto MITM is defeated if the two halves are computed with different keys (3DES vs 2DES). Substrate analogue: if the W matrix changes between forward and backward (which would happen with relation-specific W), the meeting test loses calibration. The current cell uses ONE W for both directions; relation-specific W (candidate P3 in the 5x drill — composed-W functor) would BREAK this MITM, so they're alternative-architectures NOT compose-able.

### 1.3 Birthday paradox / random-walk hitting time

Random walk on N-node graph: expected forward-only hitting time from S to T = O(N) for random graphs. **Bidirectional random walk: expected meeting time = O(sqrt(N))**, by birthday-paradox argument: when both walks have each visited sqrt(N) nodes, the expected overlap is 1 by Birthday inequality. **Square-root improvement is the structural floor.**

**Substrate implication:** if the "hitting time" analogue for substrate is the expected number of cleanup-cycles before finding the true answer with margin > tau, bidirectional cuts this from O(V_C) to O(sqrt(V_C)) = sqrt(200) ≈ 14. At V_C=10000 the saving would be 10000 / 100 = 100x. **Recommendation: include a V_C-scaling arm in the next-cell-up to MEASURE this scaling; today V_C=200 is too small to see the asymptotic.**

### 1.4 Other math angles

- **Lower bound proofs:** Aaronson-Ambainis-Iwama show quantum bidirectional search has no further speedup beyond classical sqrt(N) for unstructured search. Substrate isn't quantum but the message is: sqrt-improvement is the limit; don't expect linear-in-depth scaling from bidirectional alone.
- **Bidirectional BFS for shortest path is OPTIMAL among comparison-based algorithms** (Goldberg 2005). For SUBSTRATE the cleanup primitive is the "comparison" so this applies.

---

## 2. ANGLE 2 — BRAIN / NEUROSCIENCE

### 2.1 Goal-directed navigation: forward + backward planning

**Pfeiffer-Foster 2013 (Nature 497):** rats run a maze; preplay-replay sequences in CA3/CA1 show **forward sequences from current position AND backward sequences from goal location during pauses**. The animal's brain literally runs the trajectory in both directions during decision-making. The forward and backward sweeps converge on intermediate decision points.

**Diba-Buzsaki 2007 (Nat Neurosci 10):** "Forward and reverse hippocampal place-cell sequences during ripples." Same neurons that fired forward during running fire REVERSE during sharp-wave ripples — explicitly bidirectional replay.

**Wikenheiser-Redish 2015 (Nat Neurosci 18):** "Hippocampal theta sequences reflect current goals." Goal-directed forward sweeps in theta cycles; the brain plans forward AND retroactively backward from the goal during the same theta cycle.

**Substrate mapping:** the substrate's CERT 586 sequence-binding primitive supports forward sequence storage. The current v1/v2 cell uses W.T (matrix transpose) as a backward-walk proxy — this is CORRECT for the Hebbian-built W where each (s, p, o) triple writes a rank-1 outer product `E[o] x (E[s] * R[p] * sq)^T`, so `W.T @ E[o]` recovers `E[s] * R[p] * sq` up to crosstalk. **The brain's "reverse-replay" is biologically a SEPARATE network event (not literal W.T retrieval) — there are specialized reverse-replay-eligible cells in CA3. Substrate could test a learned-reverse-W variant (separately ingested) but W.T is the cheap analytical baseline and works.**

### 2.2 Hippocampal reverse-replay during sharp-wave ripples (Buzsaki)

**Foster-Wilson 2006 (Nature 440):** original reverse-replay discovery. After running a track, hippocampal place cells fire in REVERSE ORDER during awake SWRs (sharp-wave ripples). **Reverse-replay is hypothesized to support REWARD CREDIT ASSIGNMENT — propagating the reward at the goal back to intermediate states.**

**Mechanism: TD learning analog.** The brain's reverse sweep IS the gradient backflow for credit assignment. **Substrate analogue:** RTS smoother (already drilled 5x as N1) is the closed-form forward-backward smoother that incorporates future measurements to refine each state estimate — same math as Kalman smoother in SLAM. Reverse-replay = backward Kalman pass.

**Why the substrate's reverse-replay drill (2026-06-22) got 0.128 alone:** backward-only without forward anchor inherits all the per-hop cleanup noise from the OTHER direction; backward-alone is the analytical mirror of forward-alone. It's the PRODUCT of forward and backward (RTS smoother / bidirectional meet-in-middle) that beats either alone.

### 2.3 PFC bidirectional reasoning in problem-solving

**Tanji-Hoshi 2008 (Physiol Rev 88):** PFC supports backward chaining from goals during reasoning tasks. Patients with PFC damage cannot do means-end analysis (working backward from goal). **The brain's bidirectional reasoning is implemented in PFC, with hippocampus providing the memory substrate.**

**Substrate implication:** the v1/v2 cell's bidirectional argmax IS a PFC-style means-end analysis applied to KG chains. The substrate has no PFC primitive but doesn't need one — the closed-form forward+backward+meet IS the analytical limit that PFC presumably approximates with neural dynamics.

### 2.4 Place cells fire prospectively (forward) AND retrospectively (backward)

**Skaggs-McNaughton 1996 (J Neurosci 16):** "Replay of neuronal firing sequences in rat hippocampus during sleep." Place cells encode not just the current position but also recently-traversed AND upcoming positions — phase-precession encodes both PROSPECTIVE and RETROSPECTIVE information within a single theta cycle.

**O'Keefe-Recce 1993 / Lisman-Jensen 2013:** the theta phase code embeds prospective firing in EARLY theta phase and retrospective firing in LATE theta phase — explicit bidirectional encoding within ~125ms.

**Substrate analogue:** the substrate's working-memory primitive (multi-bank K=4096) and sequence-binding (CERT 586) could implement theta-gamma-style bidirectional embedding in ONE compound vector: chain_compound = forward_position + perm(intermediate) + perm^2(backward_target_remembered). The midpoint state then naturally encodes "I am at position-k coming from S, heading to T" — implicit bidirectional context. **NEW substrate cell candidate** that hasn't been tested.

### 2.5 Why these brain findings matter for the 0.50 prior estimate

Direct count: 4 independent brain mechanisms (Pfeiffer-Foster, Foster-Wilson, Tanji-Hoshi, O'Keefe-Recce) all empirically show the brain doing forward+backward simultaneously for navigation/reasoning. Brain-existence prior: this is established biology, not speculation. **+0.10 bump to substrate prior per [[feedback-brain-is-existence-proof]].** Combined with v1/v2 already-landed evidence (chain-grade in production), the prior on "deeper depths show stronger relative lift" is HIGH: P_deflated = 0.55.

---

## 3. ANGLE 3 — CROSS-DOMAIN

### 3.1 Robot motion planning: RRT-Connect (Kuffner-LaValle 2000)

**Bidirectional Rapidly-exploring Random Tree (RRT-Connect):** for high-dim robot motion planning, build two trees rooted at start configuration q_start and goal q_goal; each tree extends toward random samples and tries to connect with the OTHER tree. **Empirically 2-10x faster than single-tree RRT for the same task** in 6+ DoF problems.

**Substrate parallel:** RRT samples random configurations because the state space is too big for systematic BFS. Substrate has V_C=200 — small enough for systematic; bidirectional substrate is closer to bidirectional BFS than RRT-Connect. **But at V_C >> 1000 (when ingesting KGs like ConceptNet 585), RRT-style RANDOM-PROBED bidirectional could be the right primitive.** New angle for future.

### 3.2 Theorem proving: forward + backward chaining

**Classical AI (Russell-Norvig ch 9):** forward chaining = data-driven inference (facts + rules → conclusions); backward chaining = goal-driven inference (goal → rules → required facts). **Production systems (OPS5, SOAR) routinely combine BOTH** because forward alone explodes (too many facts to instantiate) and backward alone loops (without anchoring in known facts).

**Substrate parallel:** the v1/v2 cell is exactly forward-chaining-from-S meeting backward-chaining-from-T. **The current cell uses argmax over V_C candidate Z's — i.e., backward chaining is EXHAUSTIVE over V_C. A "proof-search" variant would prune Z's that have no path-to-S in the W matrix support — substrate-native filter via W^(depth-mid).T @ E[Z] cosine threshold.** New cell candidate.

### 3.3 Compiler dependency resolution

**LLVM, Bazel, Ninja:** build systems compute the dependency DAG and resolve in topological order — but for INCREMENTAL builds they work BOTH directions: from changed-file forward (what depends on this?) and from build-target backward (what are this target's dependencies?). Bidirectional resolution converges in O(changed-files + targets-needed) instead of O(full-graph).

**Substrate parallel:** for SR-closure cells (precomputed M = sum gamma^k W^k from 2026-06-22 drill), the SR is a FORWARD closure. A BACKWARD-SR would be sum gamma^k (W.T)^k. **Bidirectional SR closure: M_bidir = M_forward @ M_backward, which is a single dense matrix computed once at setup. Multi-hop query at depth-d becomes ONE matrix-vector product against the bidir-SR.** This is a NEW substrate primitive — never tested. P_deflated = 0.35 (capped novel-synthesis; depends on whether the bidir-SR composes cleanly without crosstalk amplification).

### 3.4 LDPC turbo codes (already drilled, results known)

The LDPC bidirectional drill from 2026-06-26 (`gap1_multihop_ldpc_rts_bidirectional_v2`) tested LDPC and RTS as bidirectional refinements with 3 forward-backward sweeps. **Both LDPC and RTS landed at 0.213 top1** — better than backward-only 0.128 and better than forward-only baseline 0.110 (5-seed REPRODUCE_PV2 mean), but FAR below the meet-in-middle ranker's 0.620. **Why? LDPC and RTS preserve per-position uncertainty as Gaussian-mixture or LLR distributions, then argmax at the end — they're SOFT message-passing schemes. The meet-in-middle ranker uses the FULL state (not just per-hop distribution) and matches it geometrically in vector-space. Geometry trumps per-position LLR at this regime.**

This is a meaningful negative result for "more sophisticated forward-backward = more accuracy": it doesn't. **The crucial property is whether the algorithm uses the SUBSTRATE'S GEOMETRIC primitive (vector-space cosine) or a SCALAR primitive (per-position LLR).** Substrate's bind/unbind operate in continuous vector space; meet-in-middle is geometric; LDPC/RTS reduce to scalars and lose information. Lesson for substrate-product-pitching.

### 3.5 Other cross-domain instances (briefer)

- **Game-tree search:** minimax with alpha-beta uses depth-limited bidirectional probing in some contexts (proof-number search); not closely parallel.
- **Distributed consensus (Paxos / Raft):** acceptors confirm both sides of agreement; bidirectional commit but not really a search.
- **Database query optimization:** bidirectional join-tree (left-deep + right-deep) is standard. Less of a structural analogue.
- **Bidirectional language models (BERT):** masked-LM trains by predicting tokens from both left + right context. Substrate analogue: ingest chains in BOTH directions during training. Already partially done (sequence-binding CERT 586 stores reverse atoms implicitly via the sequence permutation). **New cell candidate:** explicitly ingest each chain twice (S→T forward, T→S backward) as separate atoms, then test if downstream bidirectional retrieval has lower variance. Adjacent to v1/v2 — not a duplicate.

---

## 4. SUBSTRATE-NATIVE PATH (synthesis across angles)

The substrate has **3 substrate-native primitives** that compose into bidirectional meet-in-middle:

1. **Forward chain:** `state = W @ (state * R[p] * sq)` per hop. Already in v1/v2.
2. **Backward chain via HRR involution:** `state = (W.T @ state) * R[p] * sq` per hop in reverse order. Already in v1/v2 — substrate-native via the involutive property R*R=1 elementwise for bipolar HRR.
3. **Meet via cosine in vector space:** `cosine(state_fwd, state_bwd)` is the canonical substrate similarity primitive. Either as a state-cosine probe (no ranking) OR as argmax over V_C candidate Z's.

**Three NEW substrate primitives that have NOT been composed:**

A. **Learned reverse-W:** instead of W.T, ingest each triple BOTH as (s, p, o) writing `E[o] x (E[s]*R[p]*sq)^T` AND as (o, p, s) writing `E[s] x (E[o]*R_reverse[p]*sq)^T` with a SEPARATE reverse-R codebook. Substrate sequence-binding (CERT 586) already supports reverse atoms. Trade-off: 2x W storage, possibly cleaner reverse retrieval (no W.T crosstalk amplification).

B. **Bidirectional SR closure:** precompute M_forward = sum gamma^k W^k AND M_backward = sum gamma^k (W.T)^k, then form M_bidir = M_forward @ M_backward for one-shot multi-hop. NEW primitive — never tested in any cell to date. Adjacent to SR-closure (P1 from gap1 5x drill).

C. **Compound-vector bidirectional embedding:** bundle `chain_compound = E[S] + perm(intermediate1) + perm^2(intermediate2) + ... + perm^d(E[T])` — encodes both endpoints + intermediate positions in one vector. Substrate-native via permutation-binding (Kanerva 2009 HDC primitive). Probably what the brain's theta-gamma multi-item code is doing (Lisman-Jensen 2013).

---

## 5. CELL SPEC STUB

**File:** `experiments/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v1_META_M7.py`

(Renamed from user's proposed `exp_multihop_bidirectional_meet_in_middle_v1.py` to make explicit this is the DEPTH-SCALING extension of v1/v2, not a duplicate.)

**Anchor:** `multihop_bidirectional_meet_in_middle_depth_scaling_v1_META_M7`

**Goal:** measure how bidirectional's lift scales with depth (depth ∈ {3, 5, 7, 9}); confirm the meeting helps, not just the shorter chain; produce a depth-vs-lift scaling curve.

**ARMS (7):**

| Arm | Mechanism | Purpose | Predicted top1 at d=5 / d=7 / d=9 |
|---|---|---|---|
| ARM_BASELINE_HRR_2HOP_BETASWEEP | beta-sweep [0.62, 0.68] | sacred sanity rail | 0.65 at d=2 |
| ARM_REPRODUCE_POINTER_CHAIN_V2 | 2000-binding pointer-v2 W | META_M7 rail [0.08, 0.25] mandatory | 0.122 at d=5 (rail) |
| ARM_BASELINE_FORWARD_FULL_DEPTH | forward-only at depth d | the unidirectional ceiling at this depth | 0.32 / 0.05 / 0.01 |
| ARM_FORWARD_HALF_DEPTH | forward-only at depth = floor(d/2) | THE CRITICAL CONTROL: tests if just-shorter helps | 0.476 (=0.69^2) / 0.328 / 0.226 |
| ARM_BIDIRECTIONAL_MEET_MID | argmax over V_C of cosine(fwd_state(mid), bwd_state(d-mid, Z)) | THE MECHANISM | 0.62 / **0.40-0.55 predicted** / **0.15-0.30 predicted** |
| ARM_RANDOM_MEET_BASELINE | meet at randomly-chosen midpoint hop index (not floor(d/2)) | THE CONTROL: tests if true midpoint matters | <0.10 |
| ARM_BIDIR_MEET_MULTISCALE | average meet-cosine across mid ∈ {1, floor(d/2), d-1} | scale-invariant variant | TBD |

**HARD_PASS_CHAIN_GRADE_DEPTH_SCALING:**
- ARM_BIDIRECTIONAL_MEET_MID at depth-5 >= 0.55 (reproduces v2 within noise)
- AND ARM_BIDIRECTIONAL_MEET_MID at depth-9 >= 0.20
- AND ARM_BIDIRECTIONAL_MEET_MID > ARM_FORWARD_HALF_DEPTH + 0.10 at EVERY tested depth (proves meeting > shorter)
- AND ARM_BIDIRECTIONAL_MEET_MID > ARM_RANDOM_MEET_BASELINE + 0.20 at every tested depth (proves true midpoint matters)
- AND META_M7 rail PASS (REPRODUCE_PV2 in [0.08, 0.25])
- AND cv <= 0.07 across 5 seeds

**HARD_PASS_PARTIAL_DEPTH_SCALING:** any 2 of 4 sub-conditions above hold.

**HARD_FAIL_NO_DEPTH_SCALING:**
- ARM_BIDIRECTIONAL_MEET_MID at depth-9 < 0.05 OR
- ARM_BIDIRECTIONAL_MEET_MID at depth-9 <= ARM_FORWARD_HALF_DEPTH at depth-9 (no separation between mechanism and "just-shorter" control)

**MIDDLE_BAND_REVIVAL_AT_DEPTH_5_ONLY:** chain-grade at d=5 (reproduces v2) but not at d>5.

**PRE-REG fields (META_M7 / CARDINALITY_OK / verify-the-referent):**
```python
EXPECTED_N_ARMS = 7
EXPECTED_N_DEPTHS = 4   # {3, 5, 7, 9}
EXPECTED_N_SEEDS = 5
HARD_FAIL_CARDINALITY_BREACH = "expected 7 arms x 4 depths x 5 seeds = 140 records"
META_M7_RAIL = (0.08, 0.25)  # REPRODUCE_PV2
SACRED_SANITY = (0.62, 0.68)  # ARM_BASELINE_HRR_2HOP_BETASWEEP
BIAS_Q_GUARD = "if any arm hits 1.000 at V_C=200, flag in verdict_msg"
BIAS_R_GUARD = "no shared codebook between forward and backward W; both built from same triples"
DISCRIMINATOR_AT_FULL_N_SMOKE = True  # smoke runs depth=5 + V_C=200 to prove signal survives full-N
NO_SILENT_EXCEPT = True  # all except blocks halt or record
```

**Compute:** ~3-4 hr CPU at depth=9, V_C=200, N=8192, 5 seeds (depth-9 bidir is the cost driver; backward-walk per candidate Z over 4 hops). Routable via hdi_orchestrator if GPU available; tensor structure is matmul-bound so GPU lifts meaningfully.

**Smoke discipline (per Fix-23 family + discriminator-must-survive-scale USER 2026-06-26):**
- smoke runs depth=5 at V_C=200, N=8192, 1 seed; verifies bidir-meet-mid >= 0.50 BEFORE full dispatch (proves signal survives at full-N)
- smoke verifies CARDINALITY_OK with 7 arms x 1 depth x 1 seed = 7 records

**Brain-grounded prior:** P_deflated = 0.50 (cap honored). Specifically: P(at-least-MIDDLE_BAND on depth-scaling) = 0.65; P(HARD_PASS_CHAIN_GRADE) = 0.50.

**Substrate-product implication if HARD_PASS:**
- depth-scaling cert gives a SUBSTRATE-NATIVE depth-K reasoning capability that LM scaffolds can't easily match (LMs don't have analytical sqrt-scaling for chain-of-thought; their compound error at K steps is k * single-step error)
- audit-chain capability deepens: each hop has per-hop confidence; bidirectional gives MEETING confidence as additional refuse-gate signal
- this becomes a Stage-3 compositional-understanding building block

---

## 6. CROSS-REFERENCE: PRIOR "Cell C bidirectional" attempt

The prior cell was `exp_substrate_multihop_bidirectional_meet_middle_v1` + the v2 META_M7 rail variant. **Both ran in PRODUCTION at V_C=200, N=8192, 3 seeds, depth=5 only.** v2's verdict: `HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL` at BIDIR_MEET_MID=0.620 (cv=0.064), lift_over_fwd=+0.297 over the matched-binding regime, META_M7 rail PASS at REPRODUCE_PV2=0.122.

**Was it properly tested?** YES at depth=5. NOT at depth>5. NOT with FORWARD_HALF_DEPTH control. NOT with RANDOM_MEET control. The 2 missing controls are exactly what discriminate "meeting helps" from "shorter chain helps" and "true midpoint matters" — the user's intuition that the prior test was incomplete on the structural-claim front is CORRECT. The cell proved bidirectional WORKS as a chain-grade ranker; it did not prove WHY it works.

**Differences vs the user's proposed cell:**
- user's proposed: 4 arms (BASELINE_FORWARD_5HOP / BIDIRECTIONAL_2HOP_FROM_EACH / FORWARD_2HOP_ONLY / RANDOM_MEET); ours: 7 arms with depth-scaling axis
- user's proposed: HARD_PASS = bidirectional >= 0.65 AND >> forward_2hop; ours: HARD_PASS_CHAIN_GRADE_DEPTH_SCALING with 4 sub-conditions including depth-9 floor of 0.20
- user's proposed: P=0.50; ours: P_deflated=0.50 (same cap; brain-existence-prior bumped raw P up before capping)

**Why the user's proposed cell is a STRICT SUBSET:** ours adds depth-scaling (3 extra depths) + MULTISCALE arm + 5 seeds vs 3. Recommend dispatch of the LARGER cell which subsumes the user's proposed cell as a special case (depth=5 only is the first column of our depth-scan).

**Earlier non-v1 mentions of "bidirectional" in substrate:**
- `exp_wave14_multihop_bidirectional_N65536_v1` (May 2026) — old wave-14 cell at N=65536, predates the META_M7 / META_M6 rail discipline; results not load-bearing for current substrate state
- `exp_r2d_bidirectional_W_iterative_cleanup_v1` (Jun-22) — used bidirectional iterative cleanup (forward W then backward W as DENOISER, not as separate forward+backward search); different mechanism, not a meet-in-middle test
- `exp_gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7` (Jun-26) — bidirectional-as-router (the falsified USER hypothesis); proved bidir is NOT a routing signal
- `exp_gap1_multihop_ldpc_rts_bidirectional_v2_meta_m6_rail` (Jun-26) — LDPC + RTS as soft bidirectional refinements; scored LDPC=RTS=0.213 (much worse than meet-in-middle's 0.620 — geometry-vs-LLR lesson above)

The user's recollection of "Cell C bidirectional" is the v1/v2 substrate_multihop_bidirectional_meet_middle. It IS the right reference. The proposed v1 cell as user-spec'd is a CONTROL-EXTENDED variant of it; our depth-scaling cell SUBSUMES the user's variant.

---

## 7. CALIBRATION + FALSIFIABLE PREDICTIONS

**Calibration penalties applied:**
- 0.20 lit-scan deflation
- novel-synthesis cap 0.50 (depth-scaling claim is a meaningful extrapolation beyond v2 results — counted as novel-synthesis)
- +0.10 brain-existence prior bump
- net: raw P = 0.65 - 0.20 + 0.10 = 0.55; capped to 0.50 per novel-synthesis cap

**Predictions (5-seed, V_C=200, N=8192, META_M7 rail mandatory):**

1. **At depth-5:** BIDIR_MEET_MID reproduces v2 within [0.55, 0.70] (95% confidence; based on v2's 0.620 with cv=0.064)
2. **At depth-7:** BIDIR_MEET_MID in [0.30, 0.55] (predicted 0.42 from sqrt(0.69^7) heuristic with ~30% noise)
3. **At depth-9:** BIDIR_MEET_MID in [0.10, 0.30] (predicted 0.18 from sqrt(0.69^9))
4. **FORWARD_HALF_DEPTH at depth-9 = forward-only at d=4** ≈ 0.69^4 = 0.226 — uncomfortably CLOSE to predicted BIDIR_MEET_MID. **Discriminating prediction:** BIDIR > FORWARD_HALF by at least +0.05 at d=9, otherwise the "meeting helps" claim is falsified
5. **RANDOM_MEET_BASELINE at any depth:** <0.10 (random midpoint cosine match)
6. **Scaling slope:** log(BIDIR) / log(depth) should be ~-0.7 (sqrt-style); log(FORWARD) / log(depth) should be ~-1.5 (linear-style). The slope difference IS the substrate-product claim.

**HARD-FAIL paths:**
- BIDIR scaling is INDISTINGUISHABLE from FORWARD_HALF_DEPTH at every depth → "bidirectional is just shorter chains" (would falsify the brain-mechanism claim)
- BIDIR drops below 0.05 at d=9 → "bidirectional has compounding-error floor too; no asymptotic advantage"
- RANDOM_MEET hits >0.20 → measurement artifact (V_C too small to discriminate midpoint choice)

---

## 8. SYNTHESIS — substrate-product positioning

Bidirectional meet-in-middle is the **strongest-evidence brain mechanism in the substrate's multihop portfolio** after this drill:

1. **Already chain-grade in production** at depth-5 (v2 META_M7 rail PASS; 0.620 lift over 0.323)
2. **Brain-canonical** (4 independent neural-evidence anchors)
3. **Math-grounded** (Pohl 1971 BFS, MITM crypto, birthday-paradox sqrt-scaling)
4. **Cross-domain** (RRT-Connect robotics, forward+backward chaining theorem provers, compiler dep resolution)
5. **Substrate-native primitives all in place** (W.T involution, cosine meet, no external libraries)
6. **Gap is DEPTH-SCALING + CONTROL-DISCRIMINATION** — exactly what the proposed cell measures
7. **NOT a routing signal** (separate finding; partition-router cell falsified this cleanly)

Product story if depth-scaling cell HARD_PASSes:
- "substrate does k-hop reasoning with sqrt(k)-style scaling, not linear-k compounding error" — a structural advantage over scaffold-LLM chain-of-thought (whose error compounds linearly per token)
- audit-chain becomes: forward chain confidence + backward chain confidence + meeting confidence = 3-signal per-hop provenance
- competing offerings (vector DBs, knowledge-graph QA scaffolds, RAG) don't expose meeting confidence at all

**Recommended dispatch:** depth-scaling cell as standalone. If HARD_PASS at d=9, follow up with bidirectional SR closure (primitive B from §4) as the closed-form one-shot version. If only MIDDLE_BAND at d=9, queue learned-reverse-W variant (primitive A) which probably gets cleaner backward retrieval than W.T.

**Sequence:**
1. AUTHOR cell with smoke at d=5 / V_C=200 / 1 seed verifying BIDIR >= 0.50 (proves discriminator survives at full-N, per USER 2026-06-26 discipline)
2. SPAWN hdi_skunkworks for SCHEMA-VET on pre-reg fields (META_M7, CARDINALITY_OK, bias guards)
3. SPAWN hdi_orchestrator for dispatch to remote_cpu_queue or GPU (matmul-bound at deeper depths)
4. CERT-PASS atomization same-cycle per results-to-application cadence (USER 2026-06-22)

---

## 9. CITATIONS (lit anchors used in this drill)

1. Pohl 1971 "Bi-directional search" Machine Intelligence 6 — classical BFS halving
2. Diffie-Hellman 1977 "Exhaustive cryptanalysis of NBS DES" — MITM 2DES attack
3. Goldberg-Harrelson 2005 "Computing point-to-point shortest paths" SODA — bidirectional Dijkstra correctness
4. Kuffner-LaValle 2000 "RRT-Connect: An efficient approach to single-query path planning" ICRA
5. Russell-Norvig "AIMA" 3e ch9 — forward/backward chaining in production systems
6. Pfeiffer-Foster 2013 Nature 497 — bidirectional preplay-replay
7. Diba-Buzsaki 2007 Nat Neurosci 10 — reverse hippocampal place-cell sequences during ripples
8. Foster-Wilson 2006 Nature 440 — reverse-replay credit assignment
9. Wikenheiser-Redish 2015 Nat Neurosci 18 — theta sequences and goals
10. Tanji-Hoshi 2008 Physiol Rev 88 — PFC backward chaining
11. Skaggs-McNaughton 1996 J Neurosci 16 — sleep replay of awake sequences
12. O'Keefe-Recce 1993 / Lisman-Jensen 2013 — theta phase code prospective+retrospective
13. Aaronson-Ambainis-Iwama — quantum bidirectional search no further speedup beyond sqrt

Plus internal substrate cert anchors: CERT 586 (sequence-binding chain-grade), CERT 587 (FHRR sequence), CERT 585 (n1 Hebbian core), pointer-chain v2 anchor [0.69, 0.485, 0.31, 0.205, 0.145] per-hop floor sequence.

---

## 10. DELIVERY DISCIPLINE

- All 7 arms carry pre-registered HARD-PASS + HARD-PASS-PARTIAL + HARD-FAIL bands.
- Novel-synthesis P cap at 0.50 honored.
- 0.20 calibration deflation applied.
- ASCII only.
- META_M7 rail mandatory (REPRODUCE_PV2 in [0.08, 0.25]).
- Sacred-sanity rail mandatory (BASELINE_HRR_2HOP in [0.62, 0.68]).
- CARDINALITY_OK declared (140 records expected = 7 arms x 4 depths x 5 seeds).
- DISCRIMINATOR-MUST-SURVIVE-SCALE check: smoke at full V_C=200, N=8192 before full dispatch.
- BIAS-Q guard for 1.000 anomalies, BIAS-R guard for codebook-sharing artifacts.
- No silent except blocks.
- All field-advisor cross-references included.

Honest framing: the v1/v2 cell already PROVES bidirectional meet-in-middle WORKS at depth-5 (CHAIN_GRADE). This proposed cell measures HOW WELL it scales with depth AND whether the meeting-vs-just-shorter-chain claim survives controls. Both questions matter for the substrate-product story; neither is settled by existing data.
