# PRIOR MULTI-HOP / SUPERCHARGE BODY OF WORK -- WHAT IT ESTABLISHED, AND THE IMPLICATIONS FOR THE GOAL->SUBGOAL HIERARCHY GRAPH

**Filed:** 2026-09-04 by SOLVER (goal_subgoal_hierarchy problem).
**Trigger:** owner -- *"we could DEFINITELY do multihop and found ways to SUPERCHARGE it"* -- pointing at a large prior body I under-weighted when I called my marker-less located-negative "out of scope."
**Method:** read the actual cells + `data/<cell>/metrics.json` + the handoff/synthesis notes in full (not the verdict text alone). Numbers below are read off disk.

> **FIRST, A DISAMBIGUATION THAT MATTERS.** "multi-hop" in this repo spans THREE distinct bodies. The owner's pointer is body (1). Do not conflate them:
> - **(1) VSA/HD SUBSTRATE MULTI-HOP REASONING** -- bind/bundle/unbind over a knowledge graph, no LLM. This is the "supercharge" body. **RELEVANT.**
> - **(2) RAG RETRIEVAL PRECISION (HotpotQA / ColBERT / bge / Qwen)** -- the 06-07 "precision ceiling/closure" notes. External-LLM demo era; a fuzzy-dense retrieval ceiling. **NOT our line** (superseded by the no-LLM pivot), but its closure PRINCIPLE is load-bearing (see Q5).
> - **(3) WORD-PLACEMENT HOP-DISTANCE** -- the `SYNTHESIS_..._2026-08-21` note (cold-placement, frontier-fit, WordNet edge-tiers). Adjacent; its "wins came from EDGE TYPES not depth" lesson transfers directly (see Q6a).

---

## Q1. What multi-hop was DEFINITELY established -- depth, substrate, accuracy

**Substrate (all body-1 cells): VSA/HD, the project's pinned FHRR-adjacent binding algebra.** `hdlab/kg_traversal.py::KGStore` = entity codebook `E`, relation codebook `R`, Hebbian matrix `W`; bind `key = E[s]*R[p]*sqrt(N)`; store `W += outer(E[o], key)`; retrieve `scores = E @ (W @ key)`; **cleanup = argmax over the codebook** (or Modern-Hopfield softmax). A "hop" = one transit-then-cleanup. This is NOT symbolic pointer-chasing and NOT the reader's extraction -- it is vectors over a graph.

| result | substrate | depth | accuracy | verdict (PINNED) |
|---|---|---|---|---|
| `exp_wave14r_multihop_K100` | **synthetic** KG, N=16384, 100 relations, 100 facts | **50 hops** | 1hop 0.993, 5hop 0.967, 10hop 0.920, 25hop 0.773, **50hop 0.767**; per-hop retention 0.9947, decay -0.0056/hop | **MULTIHOP_50HOP_VALIDATED -- but REGIME-CONTINGENT** |
| `exp_wave14r_multihop_K10` / `_K2` | same but **10 / 2** relations | collapses | K10: 5hop **0.48**, 50hop 0.04. K2: 5hop **0.073** | **V2_NOT_REPLICATED** (the depth result does NOT hold when relations are reused) |
| `exp_ccc1_extra_fb15k237_kg_multihop_v1` | **REAL FB15k-237** KG, 5000 triples, 5427 ent, 226 rel | 3 hops | 1hop **0.946** (relbase 0.200), 2hop **0.709**, 3hop **0.643** | **HARD_PASS** (FULL, 3 seeds, 45min) |
| `exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1` | **REAL ConceptNet** (SYNONYM then IS_A) | 2 hops | at V=48000: accB **0.848** (single-shot accA_hard 0.000), oracle 0.930 | **HARD_PASS** (FULL, 5 seeds, glass-box audit == 1.0) |
| `exp_substrate_sq2_multihop_reasoning_v1` | synthetic, N=512, G=2 | 12 hops | K1..K12 all **1.00** | HARD_PASS (**smoke**, tiny) |
| `hdlab/multi_hop.py` (the PROMOTED organ) | KGStore | **K=2 chain-grade**; K=3,4 middle-band | 2hop 0.426 vs frozen-enc 0.012 = 36.5x (CERT 585) | chain-grade **K=2 only**; deeper = MM, not certified |

**PINNED VERDICT Q1:** Multi-hop over a VSA/HD graph is **definitely established, but the honest depth depends entirely on per-hop interference, not on an absolute number.** On **REAL curated symbolic KGs it is solid to 2-3 hops** (ConceptNet 2-hop 0.848 with re-query; FB15k-237 3-hop 0.643). **50 hops is real but only in a synthetic near-orthogonal regime** (100 distinct relations => ~1 fact per relation key => near-zero crosstalk); with reused relations (K10/K2) it dies by 5 hops -- **the promoted, certified claim in `hdlab/` is K=2**.

---

## Q2. The concrete SUPERCHARGE mechanisms (what each does, the lift, PINNED status)

All of them attack ONE quantity: **per-hop candidate fan-out**, because that sets the crosstalk that kills depth (see Q3).

1. **Community routing** (`exp_community_routed_glassbox_reasoning_scale_v1`, **HARD_PASS**, FULL, N=8192, V up to 30000). Route each hop to its community first (gist argmax over ~sqrt(V) pointers), then clean up **within** the ~sqrt(V) members. **Lift: routed relative-degradation 0.000 (stays flat as V grows 580->30000) while FLAT collapses, rel-deg 1.000; route@Vmax 1.000; SNR routed >2 vs flat 0.52 at V=30000.** Routing is a Merkle-logged, causally-editable step (causal_flip 1.000, tamper 1.000). **PINNED-WORKING.** This is the scale-invariance mechanism -- it turns a V-candidate cleanup into a sqrt(V) cleanup.
2. **Gated working-memory re-query micro-loop** (`exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1`, **HARD_PASS**, REAL ConceptNet). When a single shot's confidence is below a gate, re-query for the 2nd hop. **Lift: resolve_lift +0.383 over single-shot at V=48000 (p=0.0000); beats always-requery by 0.383.** Self-audit telemetry-sensitive (gate_sep 0.252, scramble_gap 0.440). **PINNED-WORKING on real substrate** -- the strongest real-data supercharge. Organ: `hdlab/glass_box_loop.py`.
3. **Hierarchical / ensemble** (`exp_substrate_sq2_x_hierarchical_reasoning_v1_n2048_K10`, **HARD_PASS**). K=4 ensemble at 2.0x critical load. **Lift: ensemble sustains depth 24 where a single vector collapses to depth 0.** **PINNED but SMOKE-scale** (N=512, 2 seeds) -- caveat: not run at production N.
4. **Goal-conditioned / partition-oracle candidate restriction** (proposed in the depth-10 REVIVAL handoff, `..._REVIVAL_2026-06-28`). Caller supplies a goal/candidate-set vector; substrate restricts the cleanup cone. Cone-collapse formula predicts top1@d10 in [0.30,0.50]. **Mechanism PINNED as the right lever; specific cell status not certified here** -- but this is exactly the community-routing idea generalized (and the most goal-graph-relevant).
5. **Per-hop lock-in (OFDM-style)** (`..._lock_in_per_hop_composition_2026-06-23`). Give each hop its own coprime frequency carrier so hops don't interfere; LOGICAL_NOT is free under lock-in. **Analytic depth budget K_max ~ sqrt(2*sqrt(N))** (N=8192 => ~10, N=16384 => ~12). Aim: extend 2-hop -> 5-7 hop. **PROPOSED/analytic -- I found the handoff + META atoms, not a landed HARD_PASS metric. Treat as unverified.**
6. **cf-RPE composition** (`exp_substrate_sq2_x_cfrpe_composition_v1_n4096`, HARD_PASS, smoke). A learned/plastic composition layer **preserves** 12-hop reasoning (hebbian_depth 12 == cfrpe_depth 12, acc 1.0). **PINNED (smoke):** adding plasticity doesn't cost depth.
7. **Completeness moat** (`decisive3_multihop_completeness_cpu_v1`, PP-226, HARD_PASS): 0.996 vs 0.753 -- retrieves the *complete* multi-hop neighborhood, not just top-1. **vs kNN-LM** (PP-189/190): substrate 1.000 at hop-3.
8. **K-beam pathsum** (`exp_multihop_kbeam_pathsum_v1`) -- **SANITY_BREACH, do NOT count as a mechanism** (see Q4).
9. **Per-hop schema-Bayes / brain-faithful 4-primitive PFC-WM state tracker** (Drill A/B, 06-28). Drill A **HARD_FAIL** (all 3 adapters top1=0.000 at depth-15; root cause = a hop-0-locked cluster->partition map, a structural bug not a parameter). Drill B redesigned the primitive (per-hop trajectory readout via the sequence-binding S matrix). **This particular brain-faithful composition is a LOCATED NEGATIVE at depth-15**; the working depth levers are 1-4 above, not this.

**PINNED VERDICT Q2:** The supercharges that are actually certified and real-data-bearing are **community-routing (+ scale invariance)** and **gated re-query (+0.383 on real ConceptNet)**, both glass-box-audited. Hierarchical-ensemble and cf-RPE-preserve are real but smoke-scale. Lock-in and partition-oracle are the right analytic levers but I did not find landed HARD_PASS metrics for them. Every one of them works by **shrinking the per-hop candidate set**, not by a cleverer search.

---

## Q3. The precision ceiling -- is there per-hop decay, and how was it "closed"?

**YES, and it is mechanistic, not empirical.** Per-hop cleanup error is set by **crosstalk between the retrieved key and everything else bound to that relation key**:
`crosstalk_std = sqrt((V_C_per_hop - 1) / N)` and the depth budget `K_max ~ sqrt(2*sqrt(N))` (from `..._lock_in..._2026-06-23`; wave14r frames the same thing as per-hop detection margin `sqrt(N/F)`). This is the **"cone-collapse"** wall: as either the per-hop fan-out (candidates per relation key) or the store size V grows, the SNR falls and the chain dies. It fully explains K100 (50 hops) vs K10/K2 (dead by 5): fewer distinct relations => more facts per key => bigger fan-out => shallower.

**How it was "closed": NOT by scaling, and NOT by a better algorithm -- by reducing the fan-out.** Community-routing (V -> sqrt(V)), goal/partition restriction (restrict the cleanup cone), Modern-Hopfield exponential-capacity cleanup (`hdlab/modern_hopfield_readout.py`), meet-in-the-middle (halves effective depth, in `hdlab/reasoner.py`), macro-actions (compress frequent sub-chains). **The word-placement synthesis (2026-08-21) independently reached the same conclusion from the other side: doubling representation capacity (k=32->64) moved h@10 by nothing (plateau 0.594, dense core), while adding EDGE TYPES gave an 11x lift.** Depth-in-practice is bounded by fan-out and by how many edge TYPES you can travel along -- not by dimension and not by search depth.

**PINNED VERDICT Q3:** Real per-hop decay exists, it is `sqrt(fanout/N)`, and it is "closed" by candidate-set restriction (routing / goal-conditioning / Hopfield / meet-in-middle), never by scaling N. Practical depth on clean substrate is ~10-12 at N~8-16k in low-fanout regimes, 2-3 on dense real KGs.

---

## Q4. The SANITY_BREACH on kbeam_pathsum -- what broke (the failure mode to avoid)

`exp_multihop_kbeam_pathsum_v1`: a **positive-control rail** required depth-2 accuracy in **[0.60, 0.70]** (a known-easy case). It came out **baseline 0.1017, beta_2 0.097 -- OUT OF BAND**. Verdict text: *"2026-06-24 beta-sweep regime not reproduced -- setup drifted; **do NOT interpret main arms**."* The main arms (K10_PATHSUM d5=0.012, etc.) are all near-zero and were declared **uninterpretable**, because if the easy case is broken the whole harness is broken.

**PINNED VERDICT Q4 (the discipline for MY cell):** it was not the mechanism that failed -- the **experimental construction drifted** so even the trivial case failed, voiding everything. **My goal-hierarchy battery MUST carry a pre-registered positive-control rail** (e.g., the authored explicit find->unlock->escape chain must score ~1.0). If that rail breaches, I report the breach and do NOT interpret the real-narrative numbers. My current 1.000-on-authored score is exactly such a rail -- keep it wired as a gate, not as the headline.

---

## Q5. Does ANY of it run over the reader's OWN extracted graph, or only clean symbolic KGs?

**ONLY clean/curated substrates.** Enumerated: synthetic KGs (wave14r, sq2, hierarchical, cfrpe), real curated symbolic KGs (ConceptNet, FB15k-237), and WorldTree rule tables. **None runs the multi-hop engine over the reader's own noisy narrative extraction.** `hdlab/reasoner.py` is explicit: its comprehension front-end is a *crude `_content_words()` stand-in, NOT `hdlab/situation_reader.py`*, and its coverage on real tables ran **RED / COVERAGE_BOUND**.

The load-bearing generalization is stated once, in `..._iterative_multihop_where_works_5x_2026-06-08` (32 citations): **"Iterative multi-hop works reliably when each hop is grounded in CLEAN DISCRETE signal (graph edges, explicit text, game state). It FAILS when grounded in cosine similarity over reformulated dense embeddings."** That is also why RAG body-2 capped at recall@2hop ~0.42-0.47 (fuzzy dense) while KGStore hits 0.95 at 1-hop (clean edges).

**PINNED VERDICT Q5:** The proven multi-hop is a **CLEAN-SUBSTRATE result. The limiter for narrative is EXTRACTION (building the clean typed graph from text), not the reasoning engine.** This is *identical* to my own finding: my walk scores 1.000 on the authored/explicit battery and stalls on real 19c narrative only because the explicit chains are sparse (11 across 25 docs). **My wall is coverage/extraction, not traversal** -- exactly where the whole prior body says the wall is.

---

## Q6. Implications for the goal->subgoal hierarchy graph

### (a) Can the proven machinery supercharge goal-hierarchy traversal? -- YES, but it is over-provisioned for depth; the real lever is EDGE COVERAGE.
My goal graph is a tiny multi-relation KG (nodes = goals/actions; edges = motivation M, enablement E, plus `sm.causal_links`). My deterministic walk is essentially `naive_chain`. I *can* fold motivation + causal + discourse-fact edges into ONE `KGStore` and run `iter_cleanup_chain` / the `reasoner.py` meet-in-the-middle search for goal-why chains, and use community-routing / goal-conditioned restriction for deeper/branchier goal networks. **But goal chains are shallow (~2-5 hops); the depth machinery is not the bottleneck.** The transferable lesson from Q3 + the 08-21 synthesis: **wins come from more EDGE TYPES to travel along, not deeper search.** So the highest-value move is to widen the edge inventory (motivation, enablement, causal, discourse-fact, distributional coherence) feeding the walk -- not to make the walk deeper.

### (b) Can the graded PPMI+SVD bridge + proven multi-hop CRACK my located negative? -- YES; this reclassifies "out of scope" as "solvable graded-bridge + 2-hop."
The `situation_model_has_no_discourse_fact_reasoning` SOLVED (files `exp_discfact_store_bridging_graded_v1.py`) is a **direct precedent for a marker-less resolution**: a reference with no surface marker is resolved by (i) a **reading-built fact store** (entity->role) + (ii) a **graded distributional bridge** -- PPMI+SVD (LSA-style, k swept, peaks k~50-100) over `(role, action)` co-occurrence, `bridge = cosine(role_vec, action_vec)` -- fused as a cue into `hdlab.graded_competition`. **On held-out edges (edge removed) the graded bridge recovers 0.700 [0.660,0.740] vs the hard-match's chance 0.492 (+0.208 ABOVE); it recovers knowledge the KG never stored.**

Mapped onto my located negative (link a marker-less action to an earlier superordinate goal): (i) the reading-built **goal register** = the same-agent open-goal stack; (ii) a **graded action->goal thematic-fit bridge** scores "does this action plausibly serve this open goal?" -- **turning planning inference into a graded thematic-fit lookup, not full planning**; (iii) the proven 2-hop chain (`action -> subgoal -> superordinate`) composes the rest. **Two real caveats from the precedent, which bound the scope honestly:** (1) the graded bridge tops out ~0.70 on held-out edges -- ceiling is the co-occurrence base's density, not ~1.0; (2) the discfact **L2 negative** shows the bridge only fires when there IS something on the stack to bridge to -- fact-ABSENT / freshly-introduced intra-sentential items came back NOT_SEP. So the goal-bridge will fire only when an open superordinate goal is actually live; a truly first-mention action has nothing to attach to (same boundary). **VERDICT: my "needs planning inference, out of scope" was over-stated. The brain-faithful, in-repo path is goal-register + graded action->goal bridge + 2-hop compose -- a solvable problem, with a stated ~0.70 ceiling and a fact-present precondition.**

### (c) Reusable multi-hop organs in `hdlab/` to compose with (do not reinvent):
- **`hdlab/multi_hop.py`** -- `naive_chain` / `iter_cleanup_chain` (Modern-Hopfield per-hop cleanup) over `KGStore`. Chain-grade K=2, MM K=3-4.
- **`hdlab/kg_traversal.py::KGStore`** -- the (s,p,o) triple store; the container for a multi-relation goal graph.
- **`hdlab/reasoner.py`** -- **the closest structural match to a goal-why reasoner**: forward/backward **meet-in-the-middle** typed-rule chain + an **inspectable glass-box derivation trace** + must-fail controls (SHUFFLE_DIRECTION, UNTYPED_SIMILARITY_NULL). Caveat: coverage-bound, crude extractor front-end.
- **`hdlab/glass_box_loop.py`** -- the gated re-query micro-loop (4 certified glass-box properties: replay / Merkle / tamper / causal-flip).
- **`hdlab/modern_hopfield_readout.py`** -- exponential-capacity cleanup for branchier neighborhoods.
- **`hdlab/grounded_semantic_graph.py`** -- PPR over WordNet++ (the landed `semantic_control` gate) for graded semantic coherence.
- **`hdlab.graded_competition`** -- the pinned additive-cue combiner the discfact bridge fuses into (where an action->goal coherence cue would plug in).

---

## TLDR

The team long ago showed the reader CAN follow multi-step chains, and found several ways to make them go further. The catch is that all of that was done over CLEAN, tidy fact-graphs -- hand-made ones, or dictionaries like ConceptNet and Freebase -- never over the messy notes the reader itself pulls out of a story. On clean data it reliably does 2-3 real-world steps, and up to fifty steps in an artificially easy setting; the moment facts get crowded, it fails within about five steps. The single most useful trick was NOT taking more steps -- it was narrowing what it has to sift through at each step (grouping related facts and jumping to the right group first), which gave a large, audited improvement. A separate lesson repeated twice: giving it MORE KINDS of connection to follow helps a lot; making the internal representation bigger helps not at all.

This matters for my goal-map in two ways. First, my own wall is the same wall they hit: the reasoning part is fine, it's PULLING the connections out of old-fashioned prose that's thin. Second -- and this is the correction I needed -- I had called one case ("an action with no explicit 'in order to' marker, tie it back to an earlier goal") out of scope as requiring planning. A solved sibling problem already does essentially this for a different task: it links a marker-less reference by asking "how well does this fit?" using a statistical similarity measure, and it works on connections it was never explicitly taught (about 70% where guessing is 49%). So my hard case is very likely solvable the same way -- as a "does this action fit this open goal?" fit-score plus a two-step link -- not as full planning. It only works when there IS an open goal to attach to, and it tops out around 70%, and I should state both.

## QUESTIONS

None.

## NEXT STEPS

1. **Keep the authored 1.000 battery as a pre-registered POSITIVE-CONTROL RAIL** (the kbeam SANITY_BREACH lesson), not as the headline result; report real-narrative coverage separately and honestly.
2. **Reframe the located negative** (marker-less action -> superordinate goal) as a graded action->goal thematic-fit bridge (PPMI+SVD / `grounded_semantic_graph`) fused into `graded_competition`, then a 2-hop compose over the same-agent open-goal stack -- mirroring `exp_discfact_store_bridging_graded_v1`. State the ~0.70 held-out ceiling and the fact-present precondition up front.
3. **Prioritise EDGE COVERAGE over search depth**: fold motivation + enablement + causal + discourse-fact + distributional-coherence edges into one graph the walk traverses; depth is not the bottleneck for shallow goal chains.
4. **Compose, don't reinvent:** build on `hdlab/reasoner.py` (meet-in-the-middle + glass-box trace) + `hdlab/multi_hop.py` over a `KGStore`, with community/goal-conditioned restriction if a goal network ever gets branchy.
