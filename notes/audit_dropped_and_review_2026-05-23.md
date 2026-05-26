# META audit -- dropped, stale, re-review (2026-05-23)

**Author**: META audit sub-agent (single-shot, per [[feedback-design-space-and-audit-cadence]])
**Scope**: cap_map history v125-v157 (cycles 128-177), strategy_decisions_2026-05-21/23, research_decisions_2026-05-21/23, all `research_*` deliveries 2026-05-22/23, all `strategy_request_to_*` routings 2026-05-21/22/23, `active_priorities.md`, `buried_treasure_research_directions.md`.
**Format**: ASCII-only (runner PYTHONIOENCODING restart pending per v157 note 6).

---

## (a) HEADLINE -- biggest 3 surprises

1. **`active_priorities.md` is 46 cap_map versions stale** (last updated cycle 111 / v111; current cycle 177 / v157). Every session that reads "active_priorities" as a coordination artifact is reading a snapshot from BEFORE the entire v112-v157 arc (Bet S K-ceiling N=65536, Bet R p-body, observability suite, multi-hop VAMP-on-chain, Bet A 5-seed, Demo 2, N=1M, all 4 Caps + 3 Gaps, anti-RM(1,16), exponential universality, Cap 1 noise envelope). This is the **single biggest coordination risk** in the orchestrator right now. PROT-009 catches cap_map commits but does NOT catch this file. Sessions that consult `active_priorities` will be confused about what's done.

2. **Bet Z.5 (Absorbing Diffusion Ensemble Smoother)** was delivered as 🔬 P=0.40 candidate at v144 (cycle 160, 06:58 EDT) -- a NEW substrate-product readout primitive with **posterior-error certificate + per-codeword variance**, structurally distinct from VAMP-smoother (cycle 162 head-to-head only covered VAMP vs hard-cleanup). Strategy v144 explicitly said "Defer Bet Z.5 to substantive routing (4-6 hrs impl + 2-3 GPU-hrs validation)". 13 cap_map versions later it has never been picked up by Exp Dev and Strategy has not re-routed it. This is the most concrete dropped substrate-novel readout candidate in the queue.

3. **Three Research deliveries on 2026-05-23 morning** (`research_strategy_open_questions_2026-05-23.md` 09:41, `research_semiconductor_physics_substrate_analogies_2026-05-23.md` 07:08, `research_order_param_2x_drill_2026-05-23.md` 09:40) appear in no cap_map narrative and no `strategy_decisions_2026-05-23.md` entry. These are 6/22 today's Research deliveries (the count Strategy v156 cycle 176 cited as "saturation"). Strategy treated them as inbox-overflow rather than integrating them. Three deliveries went directly to disk and never got an integration cycle. (`research_META_gaps_closing` and `research_substrate_capabilities_not_being_probed` DID get picked up at v151; `research_fresh_angles_quirky_matsci` and `research_K_resonance` DID get picked up at v144; `research_crooks_noise_robust` is logged in research_decisions_2026-05-23. The three above are the gap.)

---

## (b) Dropped items

Routings filed but no delivery / no action on delivery.

| # | File | Date | Recipient | Status | Evidence |
|---|------|------|-----------|--------|----------|
| D1 | `strategy_request_to_research_strategy_open_questions_2026-05-23.md` | 05-23 09:34 | Research | Delivered as `research_strategy_open_questions_2026-05-23.md` 09:41 (7 min) -- NEVER integrated into cap_map or strategy_decisions | grep cap_map / decisions: 0 hits |
| D2 | `strategy_request_to_research_order_param_2x_drill_2026-05-23.md` | 05-23 09:33 | Research | Delivered as `research_order_param_2x_drill_2026-05-23.md` 09:40 -- never named in subsequent cap_map (v151+ instead picked up Sagawa-Ueda metric-definition insight from a DIFFERENT route) | grep: 0 hits in cap_map/decisions |
| D3 | (no explicit request file) -> `research_semiconductor_physics_substrate_analogies_2026-05-23.md` | 05-23 07:08 | inbound | Never named in cap_map narrative | grep: 0 hits |
| D4 | Bet Z.5 Absorbing Diffusion Ensemble Smoother | first appeared v144 cycle 160 | Strategy noted "Defer" | Never re-routed. 13 cap_map versions later (v144 -> v157) zero follow-up. | grep: only v144 references in cap_map |
| D5 | META Gap A spatially-coupled codebook + block-VAMP | first appeared v151 cycle 171 | Strategy noted "Defer (substantial)" | v153 confirmed "STILL DEFERRED". No subsequent routing. | grep: only original deferral references |
| D6 | Bet T parallel hypothesis tracking PARTIAL (min_acc=0.689) | cycle 101 (v101) | Strategy intended Phase 2 follow-up | Has sat at 🟡 PARTIAL through 56 cap_map versions (v101 -> v157). No rescue attempted, no closure filed. | cap_map line 4569 |
| D7 | Bet V self-reflective PARTIAL (gap=0.285 -> 0.424 with N) | cycle 102-103 (v102-v103) | Strategy noted "scales positively with N; Bet Y V2.D roadmap should extend" | V2.D Bet Y was simplified (cycle 106) DROPPING the modern-dense-AM aspect. No follow-up Bet V experiment at N=65536 was ever filed. | cap_map line 4965-4967 |
| D8 | `strategy_request_to_research_three_backlog_items_2026-05-22.md` Request 2 (substrate-as-QEC theory) | 05-22 07:55 | Research | Delivered as `research_substrate_as_OAQEC_2026-05-22.md` 08:22 -- delivered NEGATIVE (substrate commutative, Harlow theorem rules out OAQEC). Result integrated at v93 cycle 93. NOT DROPPED but close out is clean. | cap_map line 2902 |
| D9 | `wave14_pq_high_resolution_v1` FULL | filed cycle 172 | Exp Dev | Mentioned as "still pending FULL conversion" at v153, v154, v155, v156, v157 (5 consecutive cycles). 5+ cycles of waiting; not yet executed. | cap_map cycles 173-177 follow-up sections |
| D10 | `strategy_request_to_exp_dev_observability_suite_v1_2026-05-22.md` items 4+5 (P(h) moments family + Bet Y V2.D N=65536 5-test battery item 5) | 05-22 | Exp Dev | Observability suite v1 ran and cert RS phase at v112; the "Bet Y V2.D 5-test battery" became simplified-scope at cycle 106 then never completed as a 5-test set | active_priorities lines 47-48 |

**Net dropped surface**: 5 substrate-product candidate rows (Bet Z.5, Gap A, Bet T rescue, Bet V N-scaling extension, P(h) family) that were explicitly named as next-work and then orphaned. 3 same-day Research deliveries that never got an integration cycle. 1 FULL conversion (pq_high_resolution) that has lingered 5 cycles.

---

## (c) Stale candidates

🔬 / 🟡 cap_map rows sitting > 5 cap_map versions without an experiment or rescue.

| Row | Status | Version of last touch | Cycles dormant | Note |
|-----|--------|-----------------------|----------------|------|
| Bet Z.5 Absorbing Diffusion Ensemble | 🔬 P=0.40 | v144 (cycle 160) | 13 versions / ~17 cycles | substrate-product readout primitive with posterior-error cert; defer-and-orphan pattern |
| META Gap A spatially-coupled codebook | 🔬 P=0.45 | v151 (cycle 171) | 6 versions / ~6 cycles | Kudekar 2013 threshold-saturation THEOREM exists; substantive but tractable |
| Bet T parallel hypothesis tracking | 🟡 PARTIAL min_acc=0.689 | v101 (cycle 101) | 56 versions / many cycles | No rescue list filed; smoke->FULL divergence anchor never investigated |
| Bet V self-reflective | 🟡 PARTIAL gap=0.424 at largeN | v103 (cycle 103) | 54 versions | N-scaling positive but never pushed to N=65536; Bet Y V2.D simplification orphaned the rescue path |
| Bet Z.1 SRHT compressive readout | ✅ but speedup 0.4x | v120 (cycle 120) | 37 versions | mechanism viable, compression benefit never realized; no follow-up to fix the speedup |
| K-resonance K=1000 anomaly | 🔬 mechanism OPEN | v144-v145 (cycle 160-162) | 12 versions | Arnold-tongue REFUTED; nearly-degenerate eigenvalue alternative noted in v145 but never tested as a competing mechanism |
| Bet Y V2.D Bet C/Bet A/multi-hop/Bet V 4-test battery (post-simplification) | 🔬 partial | cycle 106 onward | many | cycle 106 simplified-scope battery never completed as a coherent 4-test set; some items ran (multi-hop, Bet A) others never (Bet V at N=65536) |
| P(h) moments observability family | 🔬 proposed | v109-v112 (cycles 109-112) | 45+ versions | 4-family probe stack originally promised; only C_ij + P(q) + chi_4 + Kovacs + avalanche actually fired; P(h) family never |
| 15-peak P(q) sub-structure | 🔬 OPEN | v152-v153 | 5 versions | REFUTED as 15->28 hierarchy but the 15 itself is unexplained |
| Multi-component sub-K-region q_overlap | ✅ at FULL | v150 (cycle 170) | 7 versions | Validated as new OP, but the WHY the K-region matters is never probed (which K range? does it correspond to the K-resonance K=1000 region? unexplored) |

---

## (d) Re-review candidates

Closures / partial-narrowings that newer evidence should re-examine.

### R1. Bet F SSH-BSC topological (❌-arch CONFIRMED cycle 48 v67)

Closed because Plate-HRR substrate genuinely lacks AIII Z winding. **Re-review trigger**: v152's anti-RM(1,16) coset bias is a DIFFERENT kind of substrate symmetry-breaking. The substrate AVOIDS the linear subcode (frac=0.000), a strong structural finding. Question: does the anti-linear-coset bias define a non-trivial Z_2 grading (linear vs nonlinear cosets) that could carry winding-like protection at the COSET level rather than the bit level? Bet F closure was about bit-level chiral class AIII; coset-level grading was not probed.

**Verdict**: Genuinely worth a Research drill (low priority). Probably still ❌ because the algebra is wrong, but the v152 coset finding gives a NEW substrate-symmetry handle that v67 didn't have.

### R2. Bet R p-body coupling FULL CONFIRMED PBODY_NOGAIN (cycle 117 v117)

3rd cleanup mechanism family refuted. **Re-review trigger**: v157's Cap 1 Crooks noise envelope KILL gave 5 rescue sketches; sketch #5 "code-based protected erase via BCH-coded keys + soft-decoding anti-Hebbian step" is structurally a p-body-like mechanism. But the *purpose* changed: not capacity gain (Bet R original) but noise-protection (Cap 1 envelope rescue). The substrate operating regime for "protection during erase trajectory" is different from "more storage at higher M/N".

**Verdict**: Re-open p-body as a NOISE-PROTECTION mechanism axis (different from CAPACITY axis), not as a Bet R rescue. New row, not row demotion.

### R3. Bet W counterfactual binding KILLED (cycle 102 v102; consistency=0.117 random-like)

**Re-review trigger**: cycle 173 v153 Gap C conformal P(q) calibration RESCUED Bet G at N=65536. The conformal-prediction wrapper that fixed calibration is structurally a counterfactual-bound (it gives a "what-if" coverage guarantee for predictions outside the training distribution). Did Bet W's original probe test the same thing the Gap C rescue passed? Bet W's "consistency" measure may have been the wrong metric for counterfactual capability.

**Verdict**: Re-examine the Bet W metric in light of the conformal-coverage success. Possibly the substrate CAN do counterfactuals via P(q)-bootstrap-conformal wrapper, and Bet W just used the wrong probe.

### R4. Modern dense AM (Bet Y V2.D) REFUTED at smoke + FULL multi-beta (cycles 99-108)

Refuted as a capacity-extension mechanism. **Re-review trigger**: cycle 100 measured `c = beta*N = 32768` -- substrate's beta operating regime is empirically known. Modern dense AM was tested at beta=8/32/2 against that regime. But the v157 Cap 1 noise envelope finding means the Crooks-FT bound holds at clean substrate; what's the noise tolerance? Modern dense AM has well-known noise-tolerance properties (Ramsauer 2020 Theorem 6). The original Bet Y V2.D test focused on capacity ratio; noise-tolerance was never the test.

**Verdict**: Re-test Bet Y V2.D as a NOISE-TOLERANCE mechanism (not capacity). May rescue Cap 1 noise envelope at the cost of changed substrate dynamics.

### R5. R3-Laplace concept-conditioned readout (❌ Closed K>=16, cycle 14)

Closed as K=4 product appendix only. **Re-review trigger**: v144 K-resonance K=1000 fixed-point + v145 K_RESONANCE_NONE + nearly-degenerate eigenvalue at K=1000 all point at K-DEPENDENT substrate dynamics being more structured than thought. The K-dependence pattern that killed R3-Laplace at K>=16 (1/K^2 sigmoid decay) deserves re-look under the new K-dependent dynamical-systems framing.

**Verdict**: Low-priority re-review. The closure is probably still right but the *reason* (additive-prior-bias floor) may not be the actual mechanism if K-dependent dynamical-system structure is at play.

### R6. Multi-hop chain at N=65536 K=100 (cycle 117 smoke KILLED 0.100; cycle 121 FULL KILLED 0.217; cycle 127 VAMP-on-chain RESCUED at 1.000)

VAMP-on-chain rescued multi-hop at FULL. **Re-review trigger**: cycle 127 found `VAMP-on-chain` works at acc_50hop=1.000. This is a forward-backward EP single-pass mechanism. Is this the SAME mechanism as the Bet Z.5 absorbing-diffusion ensemble smoother (still 🔬 stale)? Both are posterior-recovery methods with per-codeword variance handling. If they ARE structurally the same, Bet Z.5 is already partially validated through VAMP-on-chain and the orphan promotion should fire.

**Verdict**: HIGH-VALUE re-review. Asking "is Bet Z.5 = VAMP-on-chain in different framing?" before doing a fresh impl would either close Bet Z.5 as duplicate-of-existing OR confirm it as a strictly stronger primitive (per-codeword variance vs aggregate accuracy).

---

## (e) Design-space map

### ✅ Demonstrated capabilities (12 per v153, carrying forward unchanged through v157)

Per cap_map cycle 173 v153 narrative (lines 11936-11949):

| # | Capability | Anchor | Next envelope axis to probe |
|---|------------|--------|------------------------------|
| 1 | Demo 1 Lane D capstone at N=65536 | cycles 130 + 139 | N>=131072 (push toward N=1M scale); 4-primitive composition under noise |
| 2 | Demo 2 Lane C capstone | cycle 139 | longer chain (>5 stage); composition with Demo 1 capstone |
| 3 | N=1M substrate (16x V2.D) | cycle 170 | continual-edit at N=1M (currently HARD-GATED at N>=16384 per v156); N=2M scale |
| 4 | Cap 1 Crooks forensic erase (clean) | cycle 173 v153 + v157 re-confirm | NOISE ENVELOPE NARROWED to clean (v157); rescue sketches #1-5 await Research vetted ranking (filed v157) |
| 5 | Gap B Online W updates (Robbins-Monro+SNAP) | cycle 173 | longer chain (>50 write); cross-task online updates; concurrent with retrieval |
| 6 | Gap C Conformal calibrated confidence (Bet G rescue) | cycle 173 | calibration under distribution shift; calibration at N=131072+; cross-task conformal |
| 7 | Cap 3 Streaming inference | cycle 173 | NOISE envelope (analog to Cap 1; per v157 follow-up); throughput at N=1M |
| 8 | TWO substrate-novel readout primitives equivalent | cycle 162 | THIRD primitive: Bet Z.5 if rescued from orphan state |
| 9 | Multi-target + cross-task at FULL | cycle 139 | more targets (>4); harder cross-task transfer; under noise |
| 10 | Bet A continual-edit at M_init=8192 N=65536 | cycle 172 + re-confirmed via v156 hard-gate | larger N hard-gated until build_initial_W refactored; **engineering blocker** |
| 11 | 240 envelope cells PASS at FULL | cycle 145 | cells with harsher noise, larger K; meta-envelope (envelope of envelopes) |
| 12 | Observability V2 complete (chi_4 + Kovacs + avalanche) | cycles 168-170 | apply observability to other capabilities (chi_4 during continual-edit, Kovacs during erase, etc.); cross-capability observability |

### 🟡 Partial rows

- Bet T parallel hypothesis tracking (PARTIAL min=0.689; cycle 101 v101; STALE 56 versions)
- Bet V self-reflective (PARTIAL gap=0.424 at largeN; cycle 103 v103; STALE 54 versions)
- Cap 1 Crooks noise envelope (rescue sketches 1-5 filed; awaiting Research vetted ranking)
- Bet A M_init capacity ceiling at N=65536 (OOM-DEFERRED HARD-GATED; engineering blocker on build_initial_W)
- Bet Z.1 SRHT readout (mechanism viable but speedup 0.4x; cycle 120; STALE 37 versions)

### 🔬 Candidate rows (substrate-product extensions awaiting experiment)

- Bet Z.5 Absorbing Diffusion Ensemble Smoother (P=0.40; cycle 160 v144; STALE)
- META Gap A spatially-coupled codebook (P=0.45; cycle 171 v151)
- K-resonance K=1000 fixed-point mechanism (Arnold-tongue REFUTED; nearly-degenerate eigvals candidate)
- Bet A M_init capacity at N=8192 envelope datapoint (3 cells M/N>=2 KILL; AGS-class as expected)
- 15-peak P(q) substructure (5 versions stale; mechanism unknown after 15->28 hierarchy refuted)
- Anti-RM(1,16) coset bias mechanism (substrate-physics; 0% within linear subcode; mechanism unknown)
- P(h) moments observability family (proposed v109; never fired)

### 🔴 Hard-gated rows

- Bet A continual-edit at N>=16384 (v156 HARD-GATE; engineering blocker `build_initial_W` matmul intermediate; bf16-cast or chunked allocation refactor required)

---

## (f) Five CHEAP CPU exploratory experiments -- ranked by leverage

All ~minutes wall-clock on either local desktop CPU or remote CPU runner; no GPU needed; produce design-space data that informs which GPU tests are worth queueing.

### Rank 1 (HIGHEST LEVERAGE): Bet Z.5 vs VAMP-on-chain structural equivalence check

**Why**: Closes the highest-leverage stale-candidate row by either eliminating Bet Z.5 as a duplicate (saving 4-6 hr impl) OR confirming it as strictly stronger (justifying the impl with prior).

**Protocol**: numerical CPU comparison of the absorbing-discrete-diffusion ensemble-smoother update equations (arXiv:2507.07586) vs the VAMP-on-chain forward-backward EP single-pass equations (cycle 127). Both are belief-propagation variants for posterior recovery in chained codeword problems. Re-derive both on the same toy chain (N=512, K=10, 5-hop) and check whether the update rules differ structurally or are isomorphic up to reparameterization.

**Cost**: ~30-60 min CPU + ~1 hr of math derivation.
**Output**: structural equivalence verdict; if non-equivalent, the strictly-stronger axis (per-codeword variance vs aggregate accuracy).

### Rank 2: P(q) sub-K-region analyzer pass on EXISTING data

**Why**: v150's multi-component sub-K-region OP is the substrate-physics QUANTITATIVE recovery anchor (cycle 170 RESTORATION). But "sub-K-region" is never operationally defined -- which K range? Does it correspond to K=900-1500 (the K-resonance band)?

**Protocol**: re-analyze existing P(q) outputs from cycles 168-172 with explicit K-binning at K-resonance boundaries (K<900, K=900-1500, K>1500). Compute per-bin order parameter consistency.

**Cost**: ~15-30 min CPU on saved P(q) arrays.
**Output**: which K-region drives the sub-region OP; whether it overlaps the K-resonance K=1000 fixed-point.

### Rank 3: Bet T smoke->FULL divergence forensic re-analysis

**Why**: Bet T has been 🟡 PARTIAL min=0.689 for 56 cap_map versions with no rescue. The smoke PASS -> FULL PARTIAL divergence is the 1st in a chain of cycle-101-102 5-anchored smoke-not-predictive (cap_map line 4812). The recent 24-anchor smoke->FULL divergence pattern (v157) is dominated by OOM and over-capacity-ceiling regimes; Bet T's was different.

**Protocol**: bootstrap-resample existing Bet T FULL trial data at min_acc=0.689 to estimate the seed-variance contribution vs systematic substrate gap. If seed-variance dominates, Bet T is a 5-seed extension away from passing. If systematic, the gap is real and rescue is needed.

**Cost**: ~5 min CPU re-analyzing saved trial-level data.
**Output**: variance decomposition; pass/fail forecast at 5-seed.

### Rank 4: Bet A M_init capacity envelope -- theoretical Marchenko-Pastur prediction

**Why**: Bet A continual-edit is HARD-GATED at N>=16384 due to OOM. But the question "does the substrate fail at M/N >= some threshold X" is theoretically derivable from Marchenko-Pastur + Frady-Sommer interference scaling (cap_map v3 already used SNR ~ 1/(2B-1) with B=2 to give cliff at K/N=0.55). Bet A's M_init capacity should have an analogous closed-form prediction.

**Protocol**: derive the AGS-class capacity prediction for the Bet A `build_initial_W` protocol at N=65536 from M-P spectral bound + cleanup-margin theorem. Compare to the empirical sweep B datapoint (substrate fails at M/N >= 2 at N=8192) and v98 architectural breakpoint at M = 2N (cycle 98).

**Cost**: ~1-2 hr theory + ~5 min numerical evaluation.
**Output**: predicted M_init capacity at N=65536; tells exp_dev which M_init values are worth trying once the engineering fix lands; eliminates wasted GPU.

### Rank 5: Coset-census re-analysis at FULL -- mechanism for anti-RM(1,16)

**Why**: v152 finding "substrate AVOIDS RM(1,16) with frac=0.000" is a substrate-physics surprise (Research P=0.40 predicted ~25% within; empirical 0%). v153 noted endpoints land in 3 nonlinear cosets uniformly. Mechanism OPEN. Question: is the "anti-linear" bias an entropic effect (linear coset has lower entropy density per codeword) or an energetic effect (linear codewords are saddles of the W-dynamics)?

**Protocol**: re-analyze existing coset-census saved data, compute (a) per-coset energy E_c = <W_endpoint, codeword_c> and (b) per-coset entropy from endpoint clustering. Cross-tabulate energetic vs entropic separation between linear and nonlinear cosets.

**Cost**: ~10-20 min CPU.
**Output**: mechanism candidate for anti-linear-coset bias; informs whether to route a follow-up Research drill or close as entropy-driven default.

---

## (g) Top 3 recommendations to Strategy

### Rec 1 (URGENT): Refresh `active_priorities.md` from v111 to v157

This is the highest-impact single coordination act in the orchestrator right now. Every session that consults `active_priorities` is reading a snapshot from cycle 111. The 12-cap substrate-product portfolio at v153, the engineering hard-gate at v156, the Cap 1 noise-fragility caveat at v157, the OOM-DEFERRED rows, the 71 PROT-009 paired commits -- none of these are in active_priorities. Strategy should write a fresh `active_priorities.md` reflecting v157 substrate-product portfolio + the 5 still-running envelope-expansion priorities + the engineering blocker on build_initial_W, and update the top-of-file `Last updated` line per PROT-001.

Per [[feedback-cap-map-update-protocol]] pull-first-atomic-write-rename pattern applies here too.

### Rec 2 (HIGH-LEVERAGE): Run the Rank-1 Bet Z.5 vs VAMP-on-chain equivalence check on the local CPU runner

Cheap (~30-60 min CPU + ~1 hr theory) and closes the most concrete dropped substrate-product candidate (Bet Z.5; 13 versions stale). Two possible outcomes both create value:

- If equivalent: close Bet Z.5 as duplicate-of-existing, freeing the candidate-row slot AND providing a re-framing of VAMP-on-chain (cycle 127) as "absorbing-diffusion ensemble smoother" (publication-grade per existing literature; but per [[feedback-no-papers-product-only]] frame it as substrate-product capability sharpening).
- If non-equivalent: confirm Bet Z.5 as strictly stronger primitive with posterior-error certificate + per-codeword variance, justify the 4-6 hr impl, route to exp_dev with high prior.

### Rec 3 (CADENCE FIX): File a standing-cadence Research drill on Bet T/Bet V rescue + verify the three orphaned same-day Research deliveries (D1, D2, D3) before queueing new Research work

Two STALE 🟡 PARTIAL rows (Bet T 56 versions, Bet V 54 versions) violate [[feedback-rehabilitation-after-rejection]] -- never had axis-combination rescue sketches filed. And three same-day Research deliveries (`research_strategy_open_questions`, `research_order_param_2x_drill`, `research_semiconductor_physics`) went straight to disk without an integration cycle. Per [[feedback-design-space-and-audit-cadence]] the standing-cadence Research drill is the proactive design-space-mapping role; the right next move is NOT another Research drill but **integrating the three orphaned deliveries** + **filing the 5 axis-combination rescue sketches for Bet T and Bet V** (per PROT-004/006). This burns down inventory before adding more.

---

## Appendix: cycle->cap_map version index covered

v125 (cycle 128) ... v157 (cycle 177) -- 33 cap_map versions covering ~50 cycles spanning 2026-05-22 to 2026-05-23.

## Appendix: routing status snapshot

- Strategy -> Research filed today: 5 (K_resonance, post_v152, strategy_open_questions, order_param_2x_drill, crooks_noise_robust)
- Research deliveries today: 8 (META_gaps_closing, substrate_capabilities, K_resonance, strategy_open_questions, order_param_2x_drill, anti_linear_coset, fresh_angles_quirky_matsci, semiconductor_physics, crooks_noise_robust) -- 3 of 8 not integrated into cap_map (D1/D2/D3 above)
- Strategy -> Exp Dev filed today: 8+ (post_v149, post_v152_pipeline, post_v141, post_v144, post_v151, post_v157_envelope, crooks_noise_envelope_v1, betA_M_init_capacity_envelope_v2_followup, betA_continual_edit_hard_gate)
- Exp Dev deliveries to queue today: 7 (betA_5seed_v2/v3, betA_M_init_v2, crooks_forensic_erase, crooks_noise_corrected_bound, crooks_noise_envelope_v1, observability_v2_kovacs_avalanche, post_v149_batch, streaming_noise_envelope_v1) -- pipeline healthy on the Exp Dev side; bottleneck is GPU + N=65536 OOM engineering wall
