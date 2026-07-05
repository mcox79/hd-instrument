# Research drill: CONTROL / instruction-following (goal-conditioned dynamic operation selection)

Date: 2026-07-05. Type: frontier capability drill (constructive build, brain-first). Not vs-LLM.

Calibration penalty applied throughout per [[feedback-lit-scan-calibration-penalty]]: P estimates
deflated 0.15-0.25 from raw; novel-synthesis P capped at 0.50; hard-fail thresholds mandatory below.

---

## HEADLINE

**The gap is narrower than the prior build-roadmap note (`research_drill_glassbox_llm_capability_gaps_build_roadmap_2026-07-05.md`) framed it, and the corpus already contains the decisive next test, pre-registered and sitting one dispatch away from a verdict.**

Two lines of substrate evidence, not one:

1. **`cortex_attention_binding_router_v2` (M1.6) is HARD_PASS cross-seed (3/3 seeds)**: a nearest-class-hypervector classifier composed from `refuse_signal_hv + retrieval_signal_hv + chain_signal` routes queries into one of 4 *qualitatively distinct* substrate operations — REFUSE / RETRIEVE / BIND / MULTI_HOP — at confusion-matrix accuracy **1.000** (seeds 7/13/19, all `>=0.85` pre-reg), lift over no-router baseline **+0.750**, lift over signal-isolated baseline **+0.30-0.33**, min per-class precision (REFUSE) **1.000**. This composes M1.4 (refuse-gate) + M1.5 (WM context retention) + multi-hop partition-oracle into one glass-box dispatcher. This IS goal-driven dynamic op-selection at the coarse "which regime is this query in" level — the machinery is proven, not speculative.

2. **But `exp_pfc_goal_conditioned_gate_v1/v2/v3` already probed the SHARPER question — does an explicit goal vector redirect handling of the SAME content differently — and it is genuinely unresolved, not absent.** v1 never landed (stuck `RUNNING`, infra). v2 (bind-then-cleanup) is `HARD_FAIL_CLEANUP_DID_NOT_FIX_COLLAPSE`: cleanup snaps the bound goal-HV to one codebook entry and destroys the goal signal (`COMBINED=0.000`), while a lighter mechanism (WM-slot goal-distance scoring + additive bias, no bind/cleanup) lifts depth-6 accuracy from V1=0.340 to WM=0.390/ADDITIVE=0.390, only **+0.05 each**, against an `ORACLE=1.000` ceiling — 66 points of headroom unclosed. v3 (drops bind+cleanup, isolates WM+additive) is authored, pre-registered, and **smoke-landed MIDDLE_BAND** (`COMBINED=0.400`, `combined_lift=0.060`, needs `>=0.10` for HARD_PASS) but its **FULL 5-seed run (90 units) was never dispatched** — the data dir only has `SELFTEST_OK`.

Bottom line: the substrate can already select among *distinct operation types* from content (proven, HARD_PASS). It has NOT yet cleanly shown that an explicit goal/instruction vector reconfigures handling of *identical* content (partial, positive-but-weak signal, huge oracle headroom, mechanism untested at the FULL scale that would settle it). This is the real frontier, and it is one dispatch away from a first cross-seed answer.

---

## Brain grounding (verified this cycle)

- **PBWM (O'Reilly & Frank 2006, *Neural Computation*)**: PFC maintains goal-relevant stripes; striatal Go/NoGo competition (trained by dopaminergic RPE) gates which stripe updates (input gating) and which readout drives downstream action (output gating). Not a clean closed-form in the original — simulation-level Go/NoGo competition, not a tidy equation.
- **Miller & Cohen 2001 (*Annu Rev Neurosci* 24)**: PFC sends top-down **bias signals** that let task-relevant-but-weak pathways out-compete prepotent ones — additive gain modulation, `activation_i' = activation_i + bias_i(goal)`. This is EXACTLY the mechanism `pfc_goal_conditioned_gate`'s ADDITIVE arm implements, and it is the weak link (+0.05 only) — consistent with the paper itself being qualitative/under-specified; later work (PBWM, guided-activation models) supplies the missing math.
- **Gurney/Prescott/Redgrave 2001 (GPR model)**: BG selection is competitive disinhibition — `selection = argmin(inhibitory-output-per-channel)`, an inverted-WTA over direct/indirect pathway channels. Cleanly maps to hard discrete selection (closer to the ALREADY-PROVEN router-v2 mechanism than to the weak additive-bias mechanism).
- **Calibration**: PBWM/Miller-Cohen/GPR are decades-old, heavily replicated computational-neuroscience frameworks (high confidence the *phenomenon* is real); the gap is that their native math is simulation/circuit-level, not a differentiable vector primitive — the substrate has to supply its own clean VSA-native formalization, which is where the novel-synthesis risk actually lives.

## External precedent for the clean math form (2 parallel lit-scans, generic terms only)

Ranked by how directly each maps to "vector selects a discrete, inspectable operation":

1. **Adaptive-RAG (Jeong et al., NAACL 2024)** — closest literal precedent. A small trained classifier maps a query to one of 3 discrete classes (no-retrieval / single-step / multi-step retrieval) and dispatches; the paper's practice of reporting **routing accuracy separately from end-task accuracy** is exactly the decisive-test metric split specified below, and this reporting convention is replicated across a growing 2025-26 cluster (RAGRouter-Bench, HANRAG, "Learning to Route"). Self-RAG (Asai et al. 2023) is a softer inline-token variant, also glass-box.
2. **MoE softmax/top-k gating (Shazeer et al. 2017)** — the single cleanest, most industrially-validated closed form: `s = softmax(x . W_op)`, hard or soft top-k dispatch. Directly matches `cortex_attention_binding_router_v2`'s already-proven nearest-class-HV mechanism (a discretized version of this).
3. **Basal ganglia Go/NoGo / GPR argmin-inhibition** — most brain-grounded, least clean closed form; matches the substrate's refuse-gate family (confidence/load-conditioned accept-refuse), not yet the multi-operation case.
4. **Hypernetworks (Ha/Dai/Le 2016)** and **FiLM (Perez et al. 2017)** — generate/modulate the operator itself from a context vector; cleanest general math for "control vector reconfigures computation" but continuous, less glass-box (you can't point to a discrete "operation X fired").
5. **VSA associative clean-up lookup (Smolensky 1990; Plate 1995)** — goal-as-key, operation-HVs-as-values, nearest-neighbor clean-up memory does the gating. This is literally what `cortex_attention_binding_router_v2` already does, and what `pfc_goal_conditioned_gate_v2`'s failed BIND_CLEAN arm tried and broke (cleanup snapped to a single codebook entry and destroyed the goal signal — a known VSA failure mode, not a fundamental one).
6. **Neural Module Networks (Andreas et al. 2016)** — discrete program/layout selection from a question representation; narrower validation base but the cleanest precedent for "compose a *sequence* of selected operations," relevant to future depth beyond single-op selection.

**Risk register finding (substrate-internal, negative result):** `exp_wave14_moe_attention_routing_v1` is the 4th and last of a family of hard-routing attempts over K=16 *homogeneous* Hebbian retrieval "experts" (cosine/ReLU/Hebbian-anchor/soft-attention), and **all 4 are HARD_FAIL** — entropy collapses or goes uniform as K grows, queries don't discriminate in BSC space at that K. This is a real scaling risk but a *different regime*: it's many homogeneous experts, not few (4) qualitatively distinct operation classes, where the router-v2 mechanism already works cleanly (CM=1.000). Do not extrapolate the MoE failure onto the small-K distinct-ops case without testing.

---

## Cheap decisive test (already spec'd, cheapest first move = dispatch not design)

**Immediate move (near-zero cost):** dispatch the already-authored, already-pre-registered `exp_pfc_goal_conditioned_gate_v3_wm_additive_only.py` to FULL (5 seeds x 2 depths x 90 units, CPU, numpy). It smoke-landed MIDDLE_BAND (`combined_lift=0.060` vs `>=0.10` HARD-PASS bar, `cv=0.150` at n_seeds=2) but was never shipped to FULL. This is not a new experiment design — it is a queue-dispatch action on existing, reviewed code. Cost: CPU-cheap, minutes.

**If v3 FULL stays MIDDLE_BAND/weak** (likely, given 66-point oracle headroom and the additive-bias mechanism's known weakness per Miller-Cohen's own under-specified math), the follow-on test applies the PROVEN router-v2 mechanism class to the sharper task: `goal_op_selector_v1`.

- **Arms**: (1) `NO_CONTROL` — fixed pipeline, always dispatches the modal operation (matches `exp_e2e_routing_pipeline`'s own no-router baseline convention). (2) `CONTENT_ONLY` — nearest-class-HV router using only query content (isolates whether content alone already solves it, per corpus-scour's flag that most "routing" cells let the query classify itself). (3) `GOAL_ROUTER` — the SAME stored entity/content queried with 2+ distinct goal-instructions (e.g. "where is X located" vs "what can X do" over identical stored facts about X), goal encoded as a composed signal-HV (role-bound, not bind-then-cleanup — avoid the v2 BIND_CLEAN collapse mode), routed via nearest-class-HV over >=2 qualitatively different operation classes (not depth-6-relation-transition variants as in `pfc_goal_conditioned_gate`, but e.g. RETRIEVE-location vs RETRIEVE-attribute vs MULTI_HOP). (4) `ORACLE` upper bound.
- **Metrics, reported SEPARATELY** (per Adaptive-RAG convention): **op-selection accuracy** (glass-box: which discrete class fired, inspectable) AND **end-task accuracy** (chain through: run the selected op, check the final answer is correct).
- **HARD-PASS**: op-selection accuracy `>= 0.80` cross-seed (deflated from router-v2's proven 1.000 to account for the harder same-content/different-goal disambiguation) AND end-task-accuracy lift over `NO_CONTROL` `>= 0.30` (mirrors `exp_e2e_routing_pipeline`'s own bar) AND lift of `GOAL_ROUTER` over `CONTENT_ONLY` `>= 0.15` (this is the load-bearing discriminator — it isolates that the GOAL vector itself carries routing signal, not just content; same structure as router-v2's already-validated `ARM_M14_M15_ISOLATED` check).
- **HARD-FAIL**: op-selection accuracy `<= 0.40`, OR `GOAL_ROUTER` lift over `CONTENT_ONLY` `<= 0.05` (goal vector adds nothing beyond content — "goal-conditioned" framing unsupported, it's purely content-conditioned, matching what most existing "routing" cells already do).
- Cost: CPU, FHRR/complex64, ~1-2 hr to extend the router-v2 harness with a genuine content-held-fixed/goal-varied arm.

---

## Falsifiable predictions

**HARD-PASS** (goal-conditioned control is real, glass-box, above chance and above content-only): op-selection >=0.80, end-task lift over no-control >=0.30, goal-vs-content-only lift >=0.15, all cross-seed cv<0.10.

**HARD-FAIL** (framing collapses to content-classification, no genuine goal-conditioning): op-selection <=0.40, or goal-vs-content lift <=0.05, or bind-then-cleanup collapse recurs (matches v2's `COMBINED=0.000` failure mode) when goal is combined with any other signal via bind+cleanup instead of composed superposition.

**MIDDLE-BAND** (real but weak, more headroom than mechanism closes — the CURRENT state per v3 smoke): op-selection 0.40-0.80, or lift 0.05-0.15. This is where `pfc_goal_conditioned_gate_v3` smoke already sits; FULL dispatch will confirm whether 5-seed evidence holds the smoke's `+0.06` or moves either direction.

---

## Cross-thread synthesis

- **Multi-drive arbitration research (`research_drill_multi_drive_arbitration_5x_2026-06-10.md`)** already spec'd the math for goal/salience-weighted competitive selection: BG-analog lateral inhibition (F2.2, P_deflated=0.38) and Boltzmann-drive-substrate (F2.1, P_deflated=0.40) are the two highest-ranked candidate mechanisms there, and both are structurally the SAME primitive as goal-conditioned op-selection — a salience/goal vector competitively gates which of K discrete things fires. That drill's Test 2 (BG-analog lateral inhibition, <2hr CPU) was never dispatched; it is now doubly justified since it would validate the same mechanism class this drill needs.
- **`cortex_attention_binding_router_v2` (M1.6)** proves the *composition* pattern works (multiple signal-HVs superposed into one class-HV, nearest-class readout, glass-box) at content-conditioning granularity — this is the scaffold to extend, not rebuild.
- **`exp_pfc_goal_conditioned_gate` family** is the one prior attempt at the SHARPER goal-vs-content question; its failure mode (bind+cleanup destroys goal info) is a known, narrow VSA pitfall (cleanup snaps to nearest single codebook entry, discarding graded goal information) — avoidable by using superposition/composed-signal encoding (router-v2's proven approach) instead of bind-then-cleanup.
- **`exp_wave14_moe_attention_routing_v1` HARD_FAIL family** bounds the risk: hard/soft routing over many (K=16) homogeneous experts fails on discriminability grounds in BSC space. This does NOT bound the few-qualitatively-distinct-operations case (router-v2 proves K=4 distinct-class routing works at CM=1.000) — but it says do not scale the operation library past single digits without re-testing discriminability.
- **PP-8 substrate-LLM deep integration**: a working goal-conditioned dispatcher is the natural gate deciding substrate-vs-LLM-vs-hybrid handling (already prototyped content-only in `exp_e2e_routing_pipeline_cpu_v1`, `exp_t5c_orchestrator_routing_cpu_v1`); a real goal-vector would let the SAME stored content be served through different tiers depending on instruction type.

## Substrate-product implications

1. **Reframe the M3-cortex "control layer" milestone**: not "build from scratch" but "close the existing v3 dispatch gap, then extend the proven router-v2 composition pattern to goal-vs-content disambiguation." This is materially cheaper than the prior roadmap's framing implied.
2. **Glass-box selling point strengthens, not weakens**: both proven mechanisms (router-v2 nearest-class-HV, refuse-gate threshold surface) are fully inspectable by construction — no black-box gating network anywhere in the stack, a genuine differentiator vs LLM agentic tool-routing (which per the lit-scan is usually an opaque LLM few-shot decision unless explicitly logged).
3. **Do not invest in bind+cleanup as the goal-encoding primitive** for control; standardize on composed-signal superposition (the router-v2 pattern) across all future control/gating cells.
4. **Cap the operation-library size in any near-term design** at single digits until a discriminability probe (entropy-vs-K, per the MoE-routing HARD_FAIL family's own diagnostic) is run for the control use case specifically.

---

## Honest achievability

Brain existence-proof stands: PBWM/BG gating is a real, validated biological mechanism (decades of replication) — glass-box goal-driven control is NOT a fantasy target. Substrate-side: the coarse version (content -> discrete op) is DONE (HARD_PASS, CM=1.000). The sharp version (goal, held independent of content, redirects identical content) is demonstrably ACHIEVABLE-in-principle (ORACLE=1.000 in the one cell that tested it) but UNCLOSED (mechanism tried so far recovers only ~7-9% of the achievable gap: 0.05-0.06 lift against 0.66 headroom). This is a real, bounded, cheaply-testable gap — not a structural wall.

**P(goal-vs-content-only lift >=0.15, HARD-PASS band) = 0.45 deflated** (raw ~0.65: reuses a proven composition mechanism on a new but closely-adjacent task; deflated for the genuine novel-synthesis element of goal-independent-of-content disambiguation, which no cell has cleanly shown yet; capped consistent with novel-synthesis P<=0.50).

**Next-drill candidate**: if `goal_op_selector_v1` HARD-PASSes, next layer is sequencing (goal selects an ORDERED chain of 2+ operations, not just one dispatch) — Neural-Module-Networks-style compositional program selection is the literature anchor for that follow-on.

---

## Citations (verified: 15)

1. O'Reilly RC, Frank MJ (2006) Making working memory work: a computational model of learning in the prefrontal cortex and basal ganglia. *Neural Computation* 18(2).
2. Miller EK, Cohen JD (2001) An integrative theory of prefrontal cortex function. *Annu Rev Neurosci* 24:167-202.
3. Gurney K, Prescott TJ, Redgrave P (2001) A computational model of action selection in the basal ganglia I & II. *Biol Cybern* 84(6).
4. Frank MJ, Loughry B, O'Reilly RC (2001) Interactions between the frontal cortex and basal ganglia in working memory: a computational model. *Cogn Affect Behav Neurosci* 1(2).
5. Rombouts JO, Bohte SM, Roelfsema PR (2015) How attention can create synaptic tags for the learning of working memories in sequential tasks. *PLOS Comput Biol* (AuGMEnT).
6. Ha D, Dai A, Le QV (2016) HyperNetworks. arXiv:1609.09106.
7. Shazeer N et al (2017) Outrageously large neural networks: the sparsely-gated mixture-of-experts layer. arXiv:1701.06538.
8. Perez E, Strub F, de Vries H, Dumoulin V, Courville A (2017) FiLM: Visual reasoning with a general conditioning layer. arXiv:1709.07871.
9. Jeong S et al (2024) Adaptive-RAG: learning to adapt retrieval-augmented large language models through question complexity. NAACL 2024, arXiv:2403.14403.
10. Asai A et al (2023) Self-RAG: learning to retrieve, generate, and critique through self-reflection. arXiv:2310.11511.
11. Andreas J, Rohrbach M, Darrell T, Klein D (2016) Neural module networks. CVPR.
12. Smolensky P (1990) Tensor product variable binding and the representation of symbolic structures in connectionist systems. *Artif Intell* 46(1-2).
13. Plate TA (1995) Holographic reduced representations. *IEEE Trans Neural Networks* 6(3).
14. Frady EP, Kent SJ, Olshausen BA, Sommer FT (2020) Resonator networks 1 & 2. *Neural Computation*.
15. Schaul T, Horgan D, Gregor K, Silver D (2015) Universal value function approximators. ICML.

Verified count: 15 (cross-checked against search results by 2 independent lit-scan sub-agents; 12 with direct source URLs, 3 from well-established training knowledge, all internally consistent with the searched summaries).
