# Research comprehensive audit -- 2026-05-23 (post-v162)

**Author**: Research-audit sub-agent (single-shot Opus pass)
**Scope**: All `exp_*` scripts (611 in /experiments), all `data/exp_*/metrics.json` + dashboard snapshot, cap_map history v1-v162 (162 versions), all `notes/research_*.md` (~85 deliveries), all `notes/strategy_request_to_*` routings (~50 files), `notes/audit_dropped_and_review_2026-05-23.md`, `notes/buried_treasure_research_directions.md`, all META audit cycles, `notes/strategy_decisions_2026-05-21` + `_05-23`.
**Format**: ASCII only.
**Honesty pass**: per [[feedback-no-smoke]] -- promising list is short and load-bearing; no padding.

---

## (a) HEADLINE

### Top 3 most promising follow-ups

1. **Bet Z.5 vs VAMP-on-chain structural equivalence check** (~30-60 min local CPU + ~1 hr math). 13-cap_map-versions stale; Strategy v158 routed but NOT yet executed. Two-way valuable: either closes a candidate row OR confirms a strictly stronger readout primitive (per-codeword variance certificate vs aggregate accuracy). This is the highest-leverage single action in the queue right now.

2. **Cap 2 Rescue 5 (Gap C conformal subsumption audit)** -- 2 h documentation work, **zero compute**. Cap 2 just structurally closed at v160 (CAP2_MARGIN_KILL HARD FAIL) and Rescue 1 endpoint-ID just KILLED too (`exp_wave14_cap2_endpoint_id_confidence_v1` AUC=0.5 in 4/4 strata; 2/5 rescues now refuted). If Rescue 5 audit shows Gap C already covers the substrate-product spec, closure becomes FINAL and portfolio stays honestly at 11. If it surfaces a gap, escalates to Rescues 2-4 + Trust-Score (Rescue 6). HIGHEST-leverage substrate-product decision item, lowest cost.

3. **`build_initial_W` bf16/chunked refactor** -- engineering, not research, but is the gate on TWO substrate-product items (Bet A N=1M continual-edit + Bet A M_init capacity envelope). 5 OOM events in one day. ~1-2 day eng effort; unlocks an entire ceiling sweep that's blocked.

### Deferred items still worthwhile

**13 deferred items remain worthwhile**, ranked by leverage/cost. Six are CHEAP (CPU-minutes); seven are SUBSTANTIVE. See section (c) inventory.

---

## (b) Top 10 Promising Experiments

Ranked by leverage / signal strength. Filter: real signal, not orphan-noise.

### Rank 1: Bet Z.5 vs VAMP-on-chain structural equivalence check

- **Status**: 🔬 P=0.40 candidate; 13 cap_map versions stale (v144 cycle 160 to v162); Strategy v158 routed to Exp Dev Pick 3; still pending.
- **WHY promising**: Cycle 162 already proved hard-cleanup + VAMP-on-chain produce equivalent accuracy in head-to-head. Bet Z.5 is the THIRD claimed substrate-novel readout primitive (absorbing-diffusion ensemble smoother with posterior-error certificate + per-codeword variance). The question "are Z.5 and VAMP-on-chain the same algorithm in different framings?" is decidable by derivation, not experiment. Two-way valuable.
- **Cheap decisive test**: ~30-60 min CPU + ~1 hr math. Derive both update rules on N=512, K=10, 5-hop toy chain; check whether they are isomorphic up to reparameterization.
- **Cost**: ~60 min CPU + 60 min human math.
- **Route**: `local_cpu_queue`, theory write-up file.

### Rank 2: Cap 2 Rescue 5 Gap C audit (documentation pass)

- **Status**: ❌ PROVISIONAL closure at v160; Rescue 1 endpoint-ID just KILLED (AUC=0.5 in 4/4 strata `exp_wave14_cap2_endpoint_id_confidence_v1`); 2 of 5 rescues refuted (margin + endpoint-ID).
- **WHY promising**: Research P=0.55 (lit-anchored not capped) -- the v158 Cap 1 Sagawa-Ueda precedent strongly suggests Gap C already delivers Cap 2's customer-facing capability (per-query conformal calibrated confidence). If audit confirms, closure becomes FINAL cleanly; if not, escalation to Rescues 2-4 has explicit hard-fail thresholds. Either way decisive.
- **Cheap decisive test**: 2 h documentation read of cycle 100-153 Cap 2 spec + cycle 173 Gap C scope. Pure documentation, no compute.
- **Cost**: 0 GPU, 0 CPU, 2 h human (or Strategy sub-agent).

### Rank 3: Three orphaned Research deliveries -- one-cycle integration pass (D1, D2, D3)

- **Status**: Three Research notes filed 2026-05-23 morning never integrated into cap_map; burn-down note filed at v158 but actions still pending: D1 (`research_strategy_open_questions`), D2 (`research_order_param_2x_drill`), D3 (`research_semiconductor_physics_substrate_analogies`).
- **WHY promising**: D1 Q2 (15-peak P(q) -> 28-endpoint hierarchy) + D2 (P(q) is the OP at FULL: non-self-averaging variance is structural signal, not noise) + D3 (DLTS analog: per-codeword fixed-point energy spectroscopy via K-pulse transient, P=0.50) all contain falsifiable predictions never tested. D3 Finding 2 (per-codeword RTN dwell-time as basin-DEPTH probe orthogonal to P(q) basin-WIDTH) is a substrate-novel observability primitive at zero infrastructure cost.
- **Cheap decisive test**: 30 min CPU re-analysis of existing endpoint data with K-binning at K-resonance boundaries (audit Rank 2); 1-2 hr theory pass for D3 DLTS analog protocol.
- **Cost**: ~1 hr CPU + ~3 hr theory across all three.

### Rank 4: META Gap A spatially-coupled codebook + block-VAMP

- **Status**: 🔬 P=0.45; 6 versions stale; theorem-backed (Kudekar 2013 threshold-saturation theorem).
- **WHY promising**: This is the ONLY remaining substantively novel substrate-product axis with rigorous theorem-anchor that's been parked. Kudekar's threshold-saturation theorem guarantees spatially-coupled LDPC codes hit Shannon capacity under BP decoding; if substrate's W matrix is reframed as a spatially-coupled construction, the same theorem applies. Substrate-product implication: hits the absolute capacity ceiling that AGS class can deliver. Bet A capacity work is currently AGS-class; Gap A would substantively extend.
- **Cheap decisive test**: 1-day theory pass deriving SC-LDPC block-VAMP recursion on substrate's existing codebook. Then small-N (4096) Python prototype, ~1 hr CPU.
- **Cost**: ~1 day theory + ~1 hr CPU. SUBSTANTIVE not cheap.

### Rank 5: P(q) sub-K-region analyzer pass on existing data (per audit Rank 2)

- **Status**: 🔬 multi-component sub-K-region q_overlap STABLE at FULL v150; "which K-region" never explicitly mapped; 5-versions stale.
- **WHY promising**: D1 Question 3 (broad K-band + near-degenerate eigenspectrum at K=1000) + v150 multi-component sub-K-region OP + v162 P(q) 7-outer-basin hierarchy all point at K-DEPENDENT substrate-physics structure. Existing saved P(q) arrays from cycles 168-172 can be re-binned at K-resonance boundaries (K<900, K=900-1500, K>1500) for free. Tests whether the multi-component OP corresponds to the K-resonance band.
- **Cheap decisive test**: ~15-30 min CPU re-analysis of saved P(q) arrays with explicit K-binning. No new experiment.
- **Cost**: ~30 min CPU.

### Rank 6: Coset-census re-analysis for anti-RM(1,16) mechanism (per audit Rank 5)

- **Status**: 🔬 mechanism OPEN; v152 found substrate AVOIDS RM(1,16) with frac=0.000 (Research P=0.40 predicted ~25% within; empirical 0%); v153 found endpoints uniform across 3 nonlinear cosets; mechanism for the bias never probed.
- **WHY promising**: This is a substrate-PHYSICS surprise -- substrate AVOIDS the linear coset that Hopfield Hebbian dynamics ought to prefer. Two clean hypotheses: entropic (linear coset has lower entropy density) vs energetic (linear codewords are saddles of W-dynamics). Re-analyzes existing saved coset-census data to cross-tabulate per-coset energy vs per-coset entropy.
- **Cheap decisive test**: ~10-20 min CPU on saved coset-census data; computes per-coset energy `E_c = <W_endpoint, codeword_c>` and per-coset entropy from endpoint clustering.
- **Cost**: ~20 min CPU.

### Rank 7: Bet T smoke->FULL divergence bootstrap forensic

- **Status**: 🟡 PARTIAL min_acc=0.689 cycle 101; 56 cap_map versions stale; rehab sketches filed v158 in Research; Rescue 2 per-hyp TEMPSCALE (`wave14_betT_per_hyp_tempscale_v1`) FULL just KILLED at min_acc=0.344 (smoke PASS 1.000; classic smoke->FULL divergence anchor 24).
- **WHY promising**: Two rescues now refuted (TEMPSCALE) but Rescue 3 (class-wise Mondrian conformal `wave14_betT_conformal_v1`) was filed and has a metrics.json missing -- check whether it ever ran. If Rescue 3 has the same hard-fail wall, Bet T is structurally dead and should close. If Rescue 3 PASSES, Bet T axis survives via the conformal route. Either way decisive.
- **Cheap decisive test**: Confirm whether `wave14_betT_conformal_v1` ran (queue routing recorded but no data dir found); if not run, ship it. ~5 min CPU per Research note.
- **Cost**: ~5 min CPU (if not yet run).

### Rank 8: D3 DLTS analog -- per-codeword fixed-point energy spectroscopy

- **Status**: 🔬 P=0.50 (Agent CC); orphan Research delivery D3; never routed.
- **WHY promising**: Predicts the 28-element fixed-point set partitions into >=2 distinct "energy" levels (substrate-novel claim). Uses K-pulse transient + first-passage timing. Existing substrate infrastructure (no new architecture). If confirmed, this is a substrate-novel observability primitive that directly addresses the "what does the 28-element partition MEAN?" question that's been open since cycle 137. Maps to cap_map Cap 4 (provenance) upgrade.
- **Cheap decisive test**: ~1 GPU-hr at N=16384; K-pulse + transient analysis; smoke at N=4096 ~10 min.
- **Cost**: ~10 min smoke / ~1 hr GPU FULL.

### Rank 9: pn-junction two-substrate rectifier primitive (D3 Finding 4)

- **Status**: 🔬 P=0.30 (Agent BB); orphan; never routed. NEW architectural primitive.
- **WHY promising**: Two substrate regions with distinct W structures (W_A != W_B) create a "built-in potential" V_bi proportional to their free-energy mismatch. Information flows preferentially from high-F to low-F region (forward bias); blocked in reverse. Substrate-novel architectural primitive -- rectifier capability requiring no spatial structure, only free-energy landscape mismatch. Maps to Cap 2 (editable memory at scale) AND Cap 4 (cognitive composition).
- **Cheap decisive test**: ~30 min CPU: build two W matrices with controlled free-energy mismatch; measure information flow forward vs reverse.
- **Cost**: ~30 min CPU smoke.

### Rank 10: Wave 15 / Bet I free-probability second-application drill

- **Status**: ✅ Bet I R16 free probability promoted v56 with 2/3 envelopes PASS (σ=16 exact, M/N=8 via modern-Hopfield); third application (multi-hop depth cliff d=25) was never closed; Research synthesis exists.
- **WHY promising**: Free probability is the one advanced-math framework that DIDN'T trivialize on substrate's finite-dim/sample-covariance specifics (unlike Tomita-Takesaki Wave 16, Steenrod Wave 17, Drinfeld Wave 13.4 -- all 3 honest negatives). The third application could close out the framework or reveal a new envelope.
- **Cheap decisive test**: ~1 hr theory derivation; numerical check on saved multi-hop chain data from cycle 121-127.
- **Cost**: ~1 hr human + ~10 min CPU.

---

## (c) Deferred Projects Inventory

| # | Name | When deferred | Current status | Why deferred | Still worthwhile? |
|---|------|----------------|-----------------|---------------|---------------------|
| 1 | Bet Z.5 Absorbing Diffusion Ensemble Smoother | v144 cycle 160 | 🔬 13 versions stale; routed v158 Pick 3 still pending | "4-6 hr impl + 2-3 GPU-hr validation"; bandwidth | **YES** (Rank 1 above) |
| 2 | META Gap A spatially-coupled codebook + block-VAMP | v151 cycle 171 | 🔬 6 versions stale; awaiting bandwidth | substantial 1-day theory + impl | **YES conditional** (Rank 4; theorem-anchored; 1-day eng) |
| 3 | Bet T parallel hypothesis tracking | v101 cycle 101 | 🟡 PARTIAL; rehab v158; TEMPSCALE rescue KILLED; conformal rescue queue unclear | 56 versions stale | **CONDITIONAL** (Rank 7; if conformal rescue runs and PASSES) |
| 4 | Bet V self-reflective | v103 cycle 103 | 🟡 PARTIAL gap=0.424; rehab sketches filed v158 | 54 versions stale | YES (rehab sketches just filed; will follow Bet T pattern) |
| 5 | Bet Z.1 SRHT compressive readout | v120 cycle 120 | ✅ but speedup 0.4x | 37 versions stale; mechanism works but compression benefit unrealized | NO (mechanism viable but no engineering path to speedup; honest defer) |
| 6 | P(h) moments observability family | v109 cycle 109 | 🔬 never fired | 45+ versions stale; superseded by chi_4 + Kovacs + avalanche actually running | NO (effectively superseded by Observability V2 fired at cycles 168-170) |
| 7 | K-resonance K=1000 fixed-point mechanism | v144-v145 | 🔬 Arnold-tongue REFUTED; near-degenerate eigvals candidate noted but never tested | 12 versions stale; mechanism candidate exists | YES (Rank 5; cheap re-analysis pass with K-binning) |
| 8 | Anti-RM(1,16) coset bias mechanism | v152 | 🔬 mechanism OPEN; substrate avoids RM(1,16) with frac=0.000 | substrate-physics surprise; energy vs entropy hypothesis | YES (Rank 6; ~20 min CPU re-analysis) |
| 9 | D1 (research_strategy_open_questions Q2 + Q3) | 05-23 morning | orphan; burn-down note v158 | Q1 already refuted (Kerdock 4-coset); Q2/Q3 never followed | YES partial (Rank 3 & Rank 5) |
| 10 | D2 (research_order_param_2x_drill: P(q) is the OP) | 05-23 morning | orphan; burn-down note v158; held for next OP-related cycle | absorbed indirectly via Sagawa-Ueda but specific findings unintegrated | YES partial (Rank 3) |
| 11 | D3 (research_semiconductor_physics: 4 substrate-applicable mappings) | 05-23 morning | orphan; parked low-priority | 3 findings P>=0.45 (DLTS, RTN, pn-junction) never routed | YES (Rank 8 + 9; ~2 GPU-hr Tier 1; substrate-novel observability) |
| 12 | Cap 2 Rescues 2-4 (VAMP variance / chi_4 / Kovacs per-query) | v160 | 🔬 DRAFT; Research deflated P=0.20/0.15/0.12 | per-query single-trajectory chi_4 + Kovacs methodologically fraught per lit | NO (Research already deflated heavily; ELECTIVE only) |
| 13 | Cap 5 Rescues 2-5 (SVRG + BSC redundancy + adaptive SNAP + tiered SLA) | v159+v161 | 🔬 ELECTIVE; Polyak rescue partial closed | structural boundary CONFIRMED at p<=0.30 covers realistic noise | NO (envelope already covers customer use case; pure ELECTIVE) |
| 14 | Cap 1 noise-robust rescue sketches 2-5 (redundant encoding + cryptographic commit + denoising + code-based) | v157 | 🔬 ELECTIVE | v158 Sagawa-Ueda re-axiom widened Cap 1 SLA; rescues now lower urgency | NO (envelope expanded by metric flip; ELECTIVE only) |
| 15 | Wave 15 / Bet I third application (multi-hop depth cliff d=25) | v56 | ✅ 2/3 envelopes PASS; third never closed | bandwidth | YES low-priority (Rank 10) |
| 16 | Modern dense AM (Bet Y V2.D) noise-tolerance re-test | refuted v108 cycle 99-108 | ❌ refuted as capacity-extension | Ramsauer 2020 Theorem 6 says modern AM has noise-tolerance properties never tested | CONDITIONAL (audit R4 re-review; only re-test if Cap 1 needs noise rescue, currently not needed after Sagawa-Ueda flip) |
| 17 | Bet F SSH-BSC topological coset-level grading | refuted v67 cycle 48 | ❌ closed at bit-level chiral class AIII | v152 anti-RM(1,16) coset bias gives a NEW substrate-symmetry handle not present at v67 | LOW priority re-review only (audit R1) |
| 18 | Cross-application probes (substrate as SAT-solver memory, world-model rollout) | ongoing | never routed | flagged as feasible in design space but no concrete experiment filed | YES conditional (see section (d)) |

**Net deferred-and-still-worthwhile count: 13** (rows 1, 2, 3, 4, 7, 8, 9, 10, 11, 15, 18 + Bet T conformal Rescue 3 + a single Cap 2 Rescue 5 audit). Six are CHEAP (CPU minutes / documentation); seven are SUBSTANTIVE.

---

## (d) Cross-application probes never run

These probes test substrate as a memory/inference primitive for an external task. Flagged as feasible in design space + Research substrate-capabilities-not-being-probed; none routed.

### 1. Substrate as SAT-solver hot-cache (combinatorial reasoning)

**Sketch**: feed a CNF clause set into substrate via Hadamard-bound atoms (one per clause); query "is variable X satisfiable given the clause cache?"; iterate via VAMP-on-chain.

- **Decisive test**: 3-SAT at N=4096 with 100 random clauses; measure %satisfied vs ground-truth Glucose oracle. ~30 min CPU smoke.
- **WHY interesting**: substrate's 28-element basin structure + VAMP-on-chain rescue at acc_50hop=1.000 (cycle 127) suggests it might do BP-equivalent satisfiability inference. SAT is the canonical "BP works here" benchmark.
- **Cost**: ~30 min CPU + ~200 LOC adapter.

### 2. Substrate as world-model rollout buffer (RL / planning)

**Sketch**: store (state, action, next_state) triples as Hadamard-bound atoms in continual-edit mode; query "predict next_state given (state, action)"; chain via Cap 5 Online W updates under noise.

- **Decisive test**: gridworld with N=8192 substrate; 1000 rollouts; measure 10-step prediction accuracy. ~1 hr CPU.
- **WHY interesting**: Bet A continual-edit ✅ + Cap 5 Online W noise envelope ✅ + Demo 2 sequential composition ✅ together make substrate look like a viable world-model RAM. Never tested as such.
- **Cost**: ~1 hr CPU + ~300 LOC RL adapter.

### 3. Substrate as KV-cache replacement for transformer

**Sketch**: hook Hadamard-bound (token, position) atoms into a small transformer's attention layer in place of the K matrix; measure perplexity vs baseline.

- **Decisive test**: GPT-nano with substrate K-cache; 1k tokens; measure bpc vs baseline.
- **WHY interesting**: substrate's CPU-only sub-100ms retrieval at K=4 + decompose+edit primitives would give transformers an auditable+editable KV cache. Engineering-heavy but extremely high value if it works.
- **Cost**: ~3-5 day eng. SUBSTANTIVE not cheap.

### 4. Substrate as streaming anomaly detector

**Sketch**: drift-diffusion NESS (Cap 3 streaming inference) + self-monitoring critical slowing down (D1 Q3 marginal stability lit) + phase-detection P(q) shape (Capability 4 from research_substrate_capabilities) = streaming anomaly detector. Substrate emits phase label + reliability score per tick.

- **Decisive test**: synthetic stream with injected anomalies (sudden noise spike at t=500); measure false-positive + detection-lag. ~1 hr CPU.
- **WHY interesting**: theorem-backed three-axis combination of v158 Cap 3 + research_substrate_capabilities Capability 2 + Capability 4. Substrate-product positioning: "self-aware thermodynamic streaming inference engine".
- **Cost**: ~1 hr CPU smoke.

---

## (e) Research with un-tested predictions

Research deliveries with cheap decisive tests filed and explicit hard-fail thresholds, where the test was never shipped.

| Research note | Test name | Cost | Hard-pass/fail threshold |
|---|---|---|---|
| research_substrate_capabilities_not_being_probed (Capability 1) | Crooks-ratio forensic erase audit | already RUN as v153/v157/v158 ✅ | DONE |
| research_substrate_capabilities_not_being_probed (Capability 2) | self-monitoring confidence smoke | NOT RUN | corr(variance, failure-proximity) >= 0.5 |
| research_substrate_capabilities_not_being_probed (Capability 4) | phase-detection introspection smoke | NOT RUN | 3-way phase classification agreement >= 85% with ground truth |
| research_strategy_open_questions Q3 | ED test eigenmode localization at K=1000 vs K=800 | NOT RUN | non-Hermitian skin-effect signature in eigenvectors? |
| research_strategy_open_questions Q3 | N-scaling of K-resonance band width | NOT RUN | band shrinks vs N -> finite-N artifact; stable -> marginal stability |
| research_order_param_2x_drill (D2) Pred 1 | N-scaling of inter-seed P(q) variance | NOT RUN | variance shrinks slower than 1/sqrt(N) -> non-self-averaging confirmed |
| research_order_param_2x_drill (D2) Pred 3 | P(q) supported on ~28 discrete values | partial PQ_OTHER_CARDINALITY v162 60-peaks; NOT cleanly cross-checked vs cycle 137 28-endpoint | matched (N,K,L) head-to-head probe |
| research_semiconductor_physics (D3) Finding 2 DLTS | K-pulse + first-passage timing | NOT RUN | 28 fixed points partition into >=2 energy levels |
| research_semiconductor_physics (D3) Finding 2 RTN | per-codeword dwell-time ratio | NOT RUN | basin DEPTH probe orthogonal to P(q) WIDTH; distribution non-trivial? |
| research_semiconductor_physics (D3) Finding 4 pn-junction | two-substrate rectifier W_A vs W_B | NOT RUN | forward bias > reverse bias info flow |
| research_betV_rescue_sketches Rescue 1 | post-hoc tau-sweep on cycle 102-103 data | NOT RUN | exists tau* in [0.60,0.80] with acc_above_tau* >= 0.85 |
| research_betT_rescue_sketches Rescue 3 (Mondrian conformal) | wave14_betT_conformal_v1 | UNCLEAR (queued; no metrics.json found) | per Research note |
| research_R1_GDPR_erase_candidates | various GDPR-erase candidate constructions | most subsumed by Cap 1; Research delivered v51 | check what's unintegrated |
| research_R20_compositional_generalization_design | hold-out compositional eval | NOT RUN | substrate generalizes to novel combinations |
| research_R22_sleep_consolidation | replay-during-quiescence experiment | NOT RUN | offline replay strengthens important memories |

**Cheapest un-tested predictions**: D3 RTN basin-depth probe (~30 min CPU) + Bet V post-hoc tau-sweep (~10 min CPU on existing data) + research_substrate_capabilities Capability 4 phase-detection smoke (~30 min GPU on saved data) + D3 DLTS K-pulse spectroscopy (~10 min smoke).

---

## (f) Dead pile (confirmed closed; do NOT pursue)

For completeness; don't waste cycles on these.

- **Wave 14 Connes-Kreimer trees**: closed cycle 26 (R13 honest negative); substrate finite-dim trivializes the Hopf-algebra approach. Coproduct-cutting cleanup approach not viable on substrate.
- **Wave 13.4 Drinfeld double D(S_3)**: closed cycle 26 (R13 honest negative; same mechanism as Wave 14).
- **Wave 16 Tomita-Takesaki modular flow**: closed cycle 26 (R14 honest negative); substrate finite-dim -> type I vN -> modular theory trivializes; T-T is WRONG tool for substrate's beta=32 derivation.
- **Wave 17 Steenrod operations**: closed cycle 28 (R15 honest negative); third advanced-math forward-routing closure.
- **Bet R p-body coupling for capacity gain**: REFUTED cycle 108 v108 + cycle 117 v117 FULL; PBODY_NOGAIN at ratio=1.0; classical-Hopfield-class confirmed at 3 mechanism families. (Note: re-opens as NOISE-PROTECTION mechanism axis per audit R2 re-review, NOT as capacity rescue.)
- **Modern dense AM (Bet Y V2.D)** as capacity-extension: REFUTED at smoke + FULL multi-beta cycles 99-108. (Conditional re-test as NOISE-TOLERANCE per audit R4, only if Cap 1 needs hardening, currently not needed.)
- **Bet W counterfactual binding**: KILLED cycle 102 consistency=0.117 random-like. (Possible Gap C subsumption per audit R3 re-review; cheap if pursued, low priority.)
- **R3-Laplace concept-conditioned readout K>=16**: closed cycle 14 (additive-prior-bias floor); R3 effect dies as 1/K^2 × sigmoid(-log K).
- **MIR-style priority replay**: closed wave14b (rank-equivalence math closes 3 rescue variants).
- **Iterative Hopfield as label readout**: closed wave14b (protocol mismatch).
- **Triple compound R3 x R10 x random-replay**: closed wave14b (shared-evidence-base mechanism).
- **Bet F SSH-BSC topological winding (bit-level)**: closed cycle 48 v67; substrate genuinely lacks AIII Z winding. (Coset-level re-review R1 low priority.)
- **Multi-hop chain at N=65536 K=100 hard-cleanup**: KILLED cycle 121; but VAMP-on-chain RESCUED cycle 127 acc_50hop=1.000. (Hard-cleanup form dead; VAMP-on-chain form ✅.)
- **Cap 2 self-monitoring via cosine margin OR tau iteration count**: TWO independent metric framings hard-fail; v153 + v160. Now Rescue 1 endpoint-ID also KILLED v162-post (AUC=0.5 in 4/4 strata). Cap 2 via intrinsic substrate proxy is structurally dead; only Rescue 5 Gap C subsumption + Rescue 6 Trust-Score remain.
- **Bet T per-hypothesis TEMPSCALE Rescue 2**: just KILLED at FULL min_acc=0.344 (smoke PASS classic divergence). Rescue 2 closed.
- **15-peak P(q) substructure**: SUPERSEDED at v162 by 7-outer + 60-total hierarchy at higher resolution.
- **K-resonance Arnold-tongue mechanism**: REFUTED cycle 162 (lambda_1/lambda_2=0.986 NOT rational).
- **Kerdock 4-coset geometry as ~25% mechanism**: REFUTED at v152 (substrate AVOIDS RM(1,16) frac=0.000).

---

## (g) Recommended pipeline order

Given guidance ("keep queue full; CPU for exploration, GPU for depth") and current state (overnight GPU queue empty; cpu_runner_0 just revived; local CPU idle).

### Immediate (next 24 hr) -- 5 cheap items, all CPU or theory

1. **Cap 2 Rescue 5 Gap C audit** (zero compute, 2 h human) -- decides whether Cap 2 closure goes FINAL or escalates to Rescues 2-4. Highest substrate-product decision item.
2. **Bet Z.5 vs VAMP-on-chain equivalence check** (local_cpu_queue + theory, ~90 min total). Closes the most-stale 🔬 candidate row.
3. **D3 DLTS analog smoke** (~10 min GPU smoke at N=4096 + ~1 hr full at N=16384 on overnight_queue). Substrate-novel observability primitive.
4. **D3 pn-junction two-substrate rectifier smoke** (local_cpu_queue, ~30 min). Substrate-novel architectural primitive.
5. **Coset-census re-analysis for anti-RM(1,16) mechanism** (local_cpu_queue, ~20 min CPU on saved data). Closes 1 substrate-physics OPEN row.

### Near-term (next 1 week) -- 4 substantive items

6. **`build_initial_W` bf16/chunked refactor** (eng, ~1-2 day) -- unblocks Bet A N>=16384 continual-edit envelope.
7. **Bet T Rescue 3 Mondrian conformal** (`wave14_betT_conformal_v1` -- verify if queued data exists; if not, ship; ~5 min CPU). Either closes Bet T cleanly or rescues it.
8. **Bet V post-hoc tau-sweep** (Research note has spec; ~10 min CPU on cycle 102-103 saved data). Tests Rescue 1 for Bet V (confidence-conditioned cleanup).
9. **research_substrate_capabilities Capability 4** (phase-detection introspection on saved P(q) data, ~30 min CPU). Substrate-novel runtime phase classifier.

### Substantive (1-2 weeks)

10. **META Gap A spatially-coupled codebook block-VAMP** (~1-day theory + ~1 hr CPU prototype, then GPU FULL). Last substantively novel substrate-product axis with theorem-anchor.

### Cross-application probes (background, when ready for new task scope)

- Substrate-as-SAT-cache (~30 min CPU smoke)
- Substrate-as-world-model-rollout (~1 hr CPU smoke + RL adapter)
- Substrate-as-streaming-anomaly-detector (~1 hr CPU)

### Routing summary

- **local_cpu_queue**: items 2, 4, 5, 7, 8 (5 cheap CPU exploratory)
- **remote_cpu_queue**: bandwidth for parallel CPU sweeps once depth drops
- **overnight_queue (GPU)**: items 3 (D3 DLTS at N=16384), 9 (phase-detection on saved data), 10 (Gap A prototype once theory lands)
- **Engineering track (off-pipeline)**: item 6 (`build_initial_W` refactor)
- **Documentation track (off-pipeline)**: item 1 (Cap 2 Rescue 5 audit)

---

## Surprises from the audit

1. **Cap 2 has now lost 3 of 5 rescues in <12 hours**: margin KILL (v160), TEMPSCALE KILL (Bet T not Cap 2 -- correction: TEMPSCALE was Bet T Rescue 2), endpoint-ID KILL (Cap 2 Rescue 1, just landed). The closure is closing harder than expected. Rescue 5 (Gap C subsumption) is now the load-bearing path; if it fails, Cap 2 goes FINAL bare ❌.

2. **D3 (semiconductor physics) Finding 2 was the highest-leverage orphan**: per-codeword RTN dwell-time as basin DEPTH probe is a substrate-novel observability primitive ORTHOGONAL to P(q) basin WIDTH. Sat unparsed since 07:08 this morning. Maps to Cap 4 provenance upgrade.

3. **Three advanced-math waves (Connes-Kreimer / Tomita-Takesaki / Steenrod) were all honest-closed in a row** at cycles 26-28 (R13/R14/R15). Common mechanism: substrate finite-dim trivializes infinite-dim machinery. Only Wave 15 free probability survives (Bet I ✅) because it explicitly assumes finite-dim sample-covariance. This is meta-intelligence about future research routing -- the M-P / free-probability / replica / spin-glass / coding-theory frameworks are the right priors.

4. **`build_initial_W` refactor blocks the entire upper N envelope** for Bet A. 5 OOM events in one day from the SAME root cause (`values.T @ keys` float32 matmul intermediate). This is the single highest-value engineering ticket in the project.

5. **The audit-anti-orphan loop is partially working**: Strategy v158 + this audit caught D1/D2/D3 orphans + Bet Z.5 + Bet T/V rescue gap. But Cap 2 endpoint-ID Rescue 1 landed AFTER v160 closure was filed and the new verdict (KILL) didn't fold back into cap_map narrative yet. Audit cadence should be tightened: every cap_map cycle that touches a ❌ PROVISIONAL row should re-check rescue status.

6. **15 of ~85 Research deliveries have un-tested falsifiable predictions** with explicit hard-pass thresholds. Burn-down rate has been good (the cap_map shows 12 demonstrated capabilities largely from Research routing) but the long tail of unintegrated predictions is real. Section (e) is the work list.

---

## Appendix: not-promising items I explicitly excluded from section (b)

- All advanced-math Wave 16/17 / Drinfeld / Tomita derivatives -- triple honest-negative pattern
- Bet R as capacity rescue (audit R2 reframes it as noise-protection, but no immediate Cap that needs it)
- Bet Z.1 SRHT speedup chase (mechanism viable, no engineering path)
- Cap 2 Rescues 2-4 (Research deflated to P<=0.20 each; methodologically fraught)
- P(h) moments observability family (effectively superseded by Observability V2 chi_4 + Kovacs + avalanche)
- 15-peak P(q) substructure (superseded by v162 7+60 hierarchy)
- All compound-mechanism stacking (closed across multiple framings)
- Modern dense AM as capacity-extension (closed; conditional re-test only if Cap 1 needs rescue)

**End of audit.**
