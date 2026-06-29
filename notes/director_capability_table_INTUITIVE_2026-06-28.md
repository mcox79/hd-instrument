# Substrate Capability Table — Plain-English Status Report
**Date:** 2026-06-28 EOD
**Audience:** Director, USER
**Goal:** What the substrate can and can't do today, what would improve each capability, and for each load-bearing gap — what the brain does, what we've tried, why it failed. Stages 1-3 only (Stage 4 = language equivalence, deferred).

The substrate is an **observable memory + composition + retrieval + audit device**. Think of it as a very large, structured filing cabinet with built-in indexing, error-correction, and fuzzy-search — not as a language model.

---

## Stage 1 — Foundational Primitives

These are the building blocks. If Stage 1 doesn't work, nothing else does. Stage 1 is **~88% mature**.

| Capability | How good? | Phase diagram | Improve? |
|---|---|---|---|
| **HRR bind/unbind** (combine two ideas into one vector; pull them back apart) | Excellent | Fully characterized | No — this is the rock-solid core |
| **Cleanup attractor** (fuzzy vector snaps to closest clean memory) | Excellent | Fully characterized; cliff sharp at N-scaled corruption | No — works as theory predicts |
| **Pattern completion** (give a corrupted memory, get back the original) | Excellent | Fully characterized (PC v2.2 GPU 3-seed; cliff at corruption 0.47–0.49) | Done this session; chain-grade ✓ |
| **Sequence binding** (remember items in order, like a phone number) | Excellent | Fully characterized; K_cliff per Kanerva theory | Done this session |
| **Multi-bank working memory** (juggle ~4 simultaneous items per bank) | Excellent | Fully characterized; K_cliff(B) = 256·B (perfect linear scaling) | Done this session |
| **Refuse-gate** (substrate says "I don't know this" instead of guessing) | Excellent | Tested at V_REL=256 | Stable |
| **Knowledge-graph ingest** (load FreebaseKG / ConceptNet / HotpotQA into substrate) | Excellent | 3 corpora characterized | Stable |
| **Partition routing M=10M** (route a query to the right slice of 10M items, 97% accurate) | Excellent | Fully characterized | Workhorse |
| **Continual learning CRISPR** (write new facts without erasing old ones; forget rate 0.006) | Good | Partial coverage | Worth pushing to HIGH via slab-partition variant |
| **Intent classifier n=100** (route input into 100 categories) | Good | Partial coverage | Worth extending to n=1000 |
| **Capacity multi-bank α-K** (how much can fit per bank vs total banks) | Good (v2 just dispatched; +K=128/256 axes) | MID; v2 will fill to HIGH | v2 GPU in flight, ~15 min |
| **Action-at-any-position lever** (apply same operation regardless of where in the sequence) | Good | MID; 2 chain-grade entries from 2026-06-22 | Stable |

**Stage 1 status:** No load-bearing gaps. The foundation is strong. The MID-coverage entries are improvements-in-flight, not capability holes.

---

## Stage 2 — Meta-Primitives + Optimization

These are higher-level mechanisms: consolidation, schema formation, decay, compression. Stage 2 is **~78% mature** but has **one load-bearing gap** at chain-grade scale.

| Capability | How good? | Phase diagram | Improve? |
|---|---|---|---|
| **TWO_TIER generational W** (working memory ages into long-term storage) | Good (proven_bound; not full chain-grade but solid) | HIGH | Stable |
| **NREM replay** (replay-during-sleep consolidates memory) | **Mixed — works at small scale; fails at chain-grade scale** | HIGH at M<256; CLOSED-negative at M=8192 | **See gap below** |
| **Ultrametric clustering** (group items into hierarchical families — like a biological taxonomy) | Excellent | Fully characterized this session; honest-downward (KMeans wins 67% of phase space, ours wins 35-42%) | Stable |
| **ANCHOR 1 partition-by-source** (keep things separate by where they came from) | Excellent | Fully characterized | Stable |
| **Lock-in amplification** (extract weak signals from noise by integrating over time, like a radio's signal-strength meter) | Good (v1 MM; v2 with extended SNR floor dispatched today) | MID → HIGH-eligible after v2 lands | v2 in flight |
| **Order-sensitive sequence binding** (distinguish "A then B" from "B then A") | Decent | PARTIAL | Worth phase-fill |
| **ANCHOR 3 coarse-graining** (compress fine details into coarse categories) | Decent (ANCHOR 3 v1 today: discriminator on density axis not granularity; reframe needed) | MID | v2 should sweep FAMILY_NOISE |
| **ANCHOR 4 time-decay eviction** (forget old items at controlled rate) | Good (today's FULL: 2/3 HP + 1 borderline MB; phase structure HEALTHY / TOO_AGGRESSIVE / TOO_PERMISSIVE all populated) | MID → HIGH-eligible after Skunkworks VET | Just landed |
| **Schema exemplar-Bayes** (Bayesian retrieval over schemas) | Good (v2 MM; v3 5-seed in flight with tighter alpha) | MID | v3 in flight |
| **Compose-freq routing v5** (first Stage 2 architectural DEFINITIVE) | Excellent | MID | Done this session (per audit add) |

### Stage 2 Load-Bearing Gap: NREM Replay at Chain-Grade Scale

**The gap, in plain English:** When you have a small set of memories (say, ~50), replay-during-sleep works fine — the system can consolidate them into long-term storage with high fidelity. When you scale up to thousands of memories (M=8192), the consolidation fails: most of the memories get garbled or lost in transfer. We tried twice (cortex_hippo_handoff v1, then v2 with a replay-bug fix) and both failed at the high-memory regime.

**What the brain does:** During slow-wave sleep, the hippocampus replays the day's experiences in compressed bursts, and the cortex receives these and incorporates them into long-term semantic memory. This is the **Complementary Learning Systems** model: fast hippocampal learning + slow cortical consolidation = lasting memories.

**Analogy:** Imagine you're a librarian with two desks. Your *intake desk* (hippocampus) can hold ~50 books at a time. Each night, you carry handfuls to the *main archive* (cortex). At ~50 books per night, this works. But if 8,000 books arrive on day 1, you can only carry handfuls — most of the day's intake gets lost before you can transfer it.

**Why our substrate fails:** The substrate's associative memory uses a sparse encoding (Willshaw-style). At sparsity 0.1 and N=4096, the math says you can store ~36 items reliably. We've been trying to store 8192 — that's 227× over the theoretical capacity. The failure isn't a bug; it's hitting a fundamental capacity bound.

**Implication:** Either we accept the substrate has a "small consolidation buffer" (use it for the most-recent N items, like a brain's working memory) OR we add an external cortex layer (an LLM) that handles the high-memory consolidation differently. This is **one of the two reasons** the M3 milestone needs an external cortex layer.

**What we'd try next (if pursuing):** Different protocols — pseudo-rehearsal, generative replay, slot-based slab-partition CRISPR. None tested at chain-grade scale yet.

---

## Stage 3 — Capability Primitives

These are the user-facing capabilities the substrate enables. **Stage 3 is mixed** — some chain-grade wins, several capability closures (some negative, some scope-limited). About **55% banked**.

### Stage 3 capabilities that work well

| Capability | How good? | Brain analog | Phase diagram |
|---|---|---|---|
| **Multi-hop reasoning depth-15** | Excellent (chain-grade; +0.47 lift via partition-oracle hint; broke Barrier 1 this session) | PFC context-gated routing (Mante 2013) | HIGH (depth-15 verified 3-seed) |
| **Compositional generation lift** | Good (+0.724 lift) | Cortex hierarchical composition | MID |
| **Schema exemplar-Bayes (ANCHOR 3)** | Good | vmPFC schema retrieval | MID |
| **Cross-modal binding** (visual + auditory event linking) | Excellent (3-seed HP this session) | TPJ multisensory integration | HIGH (just characterized this session) |
| **CF regret comparison (Cell 1, vmPFC)** | Excellent (R²=0.987) | vmPFC counterfactual reasoning | PARTIAL |

### Stage 3 capabilities currently MM (mechanism-characterized but not chain-grade)

These work but aren't fully nailed down. Most are improvable.

| Capability | What's missing |
|---|---|
| TASK_VECTOR HRR ICL K-cliff | v1 MM (metric artifact); v2 with monotonic-decay metric in flight, 3-seed HP at smoke |
| TOM Sally-Anne 2nd-order | Single MM smoke; needs multi-seed FULL |
| CF latency delta-stack (Cell 2) | Single MM smoke; mechanism observed but not nailed |
| Sequence binding for narrative Q3 | Single-seed MM; Stage 1 K-cliff primitive separately solid |
| Hypothesis-gen pipeline composition | Smoke HP +0.56; FULL queued |
| Parietal MOVABLE-rebind | MM PARTIAL; n_obj cliff at 200 |
| Parietal RELATIONAL-spatial | MM PARTIAL; smoke promising |
| Self-explanation richness | MM bounded 0.467 |

### Stage 3 LOAD-BEARING GAPS

Five things the substrate genuinely cannot do (positive characterization closures, not bugs):

---

#### Gap 1 — Long-narrative coreference (Q2)

**The gap:** Given a story like "Alice met Bob. He gave her a book. She read it.", the substrate cannot track that "he" = Bob, "her" / "she" = Alice, "it" = book across the narrative. We tried two completely different mechanisms (recency-tracking, then a linguist's algorithm called Lappin-Leass adapted to substrate); both failed.

**What the brain does:** Multiple regions cooperate. The **hippocampus** pattern-completes the most recent mentions ("who was just mentioned that could be 'she'?"). The **left language network** (STS / IFG / TPJ) uses syntactic cues (subject vs object) and semantic plausibility. The **anterior cingulate** monitors conflicts ("this 'it' is ambiguous — which referent?"). Critically, the brain has access to the **surface form** — the actual words and morphology — to apply gender/number agreement rules.

**Analogy:** Imagine you're listening to a story and you only get the *gist* of each sentence, not the words themselves. Trying to figure out who "she" refers to in "She picked it up" with no words is like trying to identify the singer of a song when you only have the melody, not the lyrics. The substrate stores meaning-content, not the strings, so it can't apply pronoun-agreement rules.

**Why our substrate fails:** Coref is fundamentally a **surface-form** problem. The substrate compresses inputs into vectors that drop the literal words. Without the strings, no pronoun-binding rule can fire. This is not a bug — it's the substrate doing what it was designed to do.

**Resolution:** External cortex layer (LLM router) handles surface-form-aware tasks; substrate handles memory + composition. This is the second reason M3 needs the cortex layer.

---

#### Gap 2 — Barrier 1 hint derivation

**The gap:** Given a multi-hop question like "Where was the author of Hamlet born?", the substrate cannot **derive the intermediate hint** ("first I need to know the author of Hamlet"). It can chain hops if you give it the hint as a routing key, but it can't generate the hint from the question text. We tried 5 different drills (cosine-similarity to known hints, 3 brain-composition models, supervised linear projection); all failed.

**What the brain does:** The **prefrontal cortex** does this through working-memory chunking + semantic priming. PFC reads the question, identifies key entities ("Hamlet", "born where"), and forms an intermediate sub-question. This is the same mechanism as chain-of-thought reasoning in humans — verbal scratchpad operating on intermediate states.

**Analogy:** It's like the difference between a librarian who, given the question "Where was Shakespeare's wife born?", says "I'll first look up Shakespeare's wife — that's Anne Hathaway — then look up Anne Hathaway's birthplace" (= **derives** the chain), vs. a librarian who, if you hand them two index cards ("Shakespeare's wife = Anne Hathaway", "Anne Hathaway born in = Shottery"), can quickly look up the answer. Our substrate is the second librarian.

**Why our substrate fails:** Hint-derivation is a **planning** task: read input, decide what intermediate fact to retrieve, formulate query for it. The substrate is a parallel associative-retrieval device — it doesn't have an inner planner. The drills all tried to bypass the planner with mechanical substitutes; none worked because the question→hint mapping is genuinely non-trivial inference.

**Resolution:** External cortex (LLM) generates the hint; substrate executes the lookup. Same M3 cortex-layer answer.

---

#### Gap 3 — Hierarchical planning (substrate-native)

**The gap:** Substrate cannot generate goal-conditioned action sequences from scratch. We tried two drills (option-critic, block-sparse-encoding); both failed at the FULL test.

**What the brain does:** **PFC + basal ganglia + cerebellum** form a hierarchical reinforcement learning loop. PFC sets high-level goals → basal ganglia selects options → cerebellum tunes motor execution. Each level operates at a different timescale.

**Analogy:** It's the difference between *knowing how* to plan a trip ("first book flights, then hotel, then rental car...") and *having access to a list* of past trip-plans you can copy. The substrate has the lookup table; it doesn't have the planning loop.

**Why our substrate fails:** Hierarchical planning requires **sequential decision-making with reward feedback** — fundamentally a different computation from associative retrieval. The substrate has no value function and no decision policy.

**Resolution:** External planner (could be LLM + chain-of-thought, or a dedicated RL planner). The substrate provides the memory layer beneath the planner.

---

#### Gap 4 — 4-primitive brain-composition (substrate-native)

**The gap:** The brain coordinates 4 primitive systems (hippocampus episodic + cortex semantic + PFC executive + ACC monitoring) for complex tasks. We tried to compose these 4 substrate-native and failed twice (PFC-WM 4-primitive cell + trajectory-schema drill).

**What the brain does:** The **Complementary Learning Systems** architecture is genuinely a 4-way coordination — fast episodic store, slow semantic consolidation, working-memory buffering, error-monitoring/control. They run in parallel and exchange information at specific events (replay, retrieval, choice).

**Analogy:** Imagine running a restaurant where chef, server, host, and dishwasher all need to coordinate without a manager. The substrate is one role at a time — it doesn't have the coordination layer.

**Why our substrate fails:** Same root as Gap 3 — there's no executive layer in the substrate that can sequence calls into the substrate's primitives. The substrate IS the primitives; it needs something above it to compose them.

**Resolution:** Same — external cortex/planner.

---

#### Gap 5 — CLS handoff at chain-grade memory scale (M=8192)

**The gap:** See Stage 2 NREM-replay gap above. At chain-grade memory load (~8000 items), hippocampus→cortex consolidation fails. We tried two cells (v1, then v2 with replay-bug fixed) and both HF.

**What the brain does:** See Stage 2 — slow-wave-sleep replay. Brain handles much larger memory loads in part by using **distributed cortical storage** (millions of cortical neurons, each contributing a tiny bit) and **structured replay timing** (theta-nested gamma during SWRs).

**Analogy:** See Stage 2 — the small intake desk vs. the giant archive.

**Why our substrate fails:** Willshaw associative-memory capacity bound. The math is fundamental, not a parameter choice.

**Resolution:** Today's regime-conditional amendment from Skunkworks: substrate handles consolidation at low-M ("recent N items"); cortex layer handles high-M. The CLOSED-negative claim **stands at the chain-grade regime** but is properly scoped.

---

#### Gap 6 (subtle, not strictly closed) — Higher-order theory of mind (3rd+ order)

**The gap:** "Alice thinks Bob thinks Carol thinks..." — recursive TOM at depth 3+. We tested today with v2_reframed; smoke HARD_FAIL FLAT_DEPTH (depth signal doesn't surface across orders). HOWEVER, Skunkworks just clarified this is a **bound on the test instrument** (4-location cleanup-attractor ceiling), not a proof the substrate lacks depth capability. The capability itself is still uncharacterized.

**What the brain does:** **TPJ + mPFC** recursively. Humans typically handle depth-2 reliably and depth-3+ with effort; the brain uses syntactic / linguistic scaffolding ("the embedded clause about what Bob believes...").

**Analogy:** Like trying to keep track of a Russian doll set when you can only ever hold 4 in your hands. The "ceiling" we hit isn't "depth doesn't matter" — it's "we only had 4 slots to test depth in".

**Why our substrate fails (at this test):** The test ran on 4-location cleanup attractor with shared distractors across levels. With more locations + per-level distractor scaling, the depth signal might surface. We genuinely don't know yet.

**Resolution:** v3 cell with larger N_LOCATIONS and per-level distractor scaling.

---

## Stage 4 — LM equivalence

**Deferred.** Stages 1-3 must mature first. The substrate is a memory/composition/retrieval device; language is downstream. Re-engage when Stage 3 is comprehensively filled.

---

## Summary of "improve" priorities

| Priority | Capability | Action |
|---|---|---|
| HIGH | NREM consolidation at chain-grade scale | Architectural — external cortex layer (M3 Phase 1 LLM router) |
| HIGH | Long-narrative coref + Barrier 1 hint derivation | Same — external cortex layer |
| MED | Capacity multi-bank v2 chain-grade landing | v2 dispatched today; awaiting Skunkworks VET |
| MED | TASK_VECTOR v2 chain-grade landing | v2 with monotonic-decay metric in flight |
| MED | Lock-in v2 chain-grade landing | v2 in flight |
| MED | ANCHOR 4 today's 2/3 HP atomization | Skunkworks VET pending |
| MED | Schema v3 5-seed AGG | In flight |
| MED | Higher-order TOM 3rd+ — true capability characterization | v3 with N_LOCATIONS expanded |
| LOW | Continual CRISPR HIGH-coverage | Slab-partition variant queued |
| LOW | Intent classifier n=1000 | Phase fill |

**Cert count: 494 chain-grade certifications today.**
