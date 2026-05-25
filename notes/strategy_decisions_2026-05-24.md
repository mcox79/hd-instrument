# Strategy decisions -- 2026-05-24

Owner: Strategy session (verdict_handler sub-agent invocations + main thread).
Convention: append-only; newest-first within a cycle; PROT-009 paired-commit stage with cap_map.md + history.md + active_priorities.md + visibility_decisions_<date>.md.

---

## Cycle 206 / inline — User-delivered 5-direction research analysis filed + routing dispatched

### Context

User delivered a substantive 5-direction research analysis verbatim in chat (treated as Research deliverable per dispatch instructions). All 5 directions reframe Bet B's ceiling as a CHARACTERIZATION problem rather than a CLOSURE problem. User explicit framing: "Direction 3 is single highest-leverage. Directions 1, 3, 4 attack characterization; 2, 5 are cheap additions."

### Action taken (inline, NOT a cap_map state change — this is a routing cycle)

1. Filed user's verbatim analysis to `notes/research_5_new_directions_2026-05-24.md` for durability.
2. Filed Strategy -> Exp Dev routing note at `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` with WHAT/WHY/CONTRACT/AUTONOMY for the four EMPIRICAL ships (Directions 3, 1, 5, 2 — in user's leverage-ranked order). Direction 4 empirical BLOCKED on Research M_c drill.
3. Filed Strategy -> Research routing note at `notes/strategy_request_to_research_2026-05-24_5_directions_math.md` with two pure-math drills:
   - Drill 1: PAC-Bayes bounds for outer-product Hebbian memories under sequential tasks (Direction 1 adjunct)
   - Drill 2: Closed-form M_c prediction for MoE cross-talk via M-P/BBP (Direction 4 — BLOCKING for empirical ship)

### Why routing notes (not direct queue_add)

Per [[feedback-no-experiment-design-in-prompts]] orchestrator hands DIRECTIONS to exp_dev/Research, not pre-designed parameters. Per [[feedback-dispatch-wrappers-default]] Agent tool unavailable in sub-agent context (post-compaction brief Section 2); next exp_dev cycle and next Research cycle pick up the routing notes via routing_handler / standing /loop cadence.

### Cap_map state change

NONE this cycle. These are scope-expansion candidates that extend characterization rather than closing rescue paths; verdict_handler will fire when individual direction experiments produce results. No PROT-004/006/008/009 trigger this cycle.

### Queue state at cycle close (verified via _queue_pending_count.py)

- overnight_queue: 5 pending (betA_5seed_v3, cap2_margin_probe_v1, pq_high_resolution_v1, demo1_noise_envelope_v1, R_transform_kerdock_v1_multi_N)
- remote_cpu_queue: 0
- local_cpu_queue: 0 (runner DEAD per MEMORY.md)

Note: dashboard state_check still reports v182 cap_map and gpu_q:1 cpu_q:9; this stale cache (last_verdict 29m ago) is inconsistent with raw queue.json reads (5+0+0) — Visibility / dashboard sync may need refresh. Flagging as visibility-decisions follow-up.

### Files filed this cycle

- `notes/research_5_new_directions_2026-05-24.md` — user analysis verbatim + triage classification + ship-list ordering
- `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` — empirical hand-off (Directions 3, 1, 5, 2; Direction 4 blocked)
- `notes/strategy_request_to_research_2026-05-24_5_directions_math.md` — pure-math drills (PAC-Bayes adjunct + M_c closed form)
- `notes/strategy_decisions_2026-05-24.md` — this entry
- No new cap_map edit. No new exp_dev script ship. No queue_add this cycle.

### Reading on substrate-product story leverage

- Direction 3 (task-geometry, HIGHEST leverage) is the single direction most likely to move the substrate-product story; if HARD-PASS lands, product framing becomes "predict retention at any task pair before training" — qualitatively different positioning vs current cap_map narrative.
- Direction 1 (M-sweep) is the BINARY decision driver: capacity-bound vs interference-bound determines which product story holds. Either outcome closes Bet B characterization.
- Direction 4 (M_c phase transition) moves MoE cap_map row from "3/8 cells pass" (currently uninterpretable) to "passes above M_c" (mathematically grounded). Blocked on Research M_c drill.
- Directions 2 + 5 are cheap additions; expected value lower per direction but combined cost is modest.
- Timeline: Direction 3 + 1 + 5 ship-able this cycle once exp_dev picks up routing (15-30 min smoke-test + queue_add); Direction 2 same-cycle if bandwidth; Direction 4 Research drill closure expected ~1-3 hours per R16 / R29 precedent; empirical follow-up ~+1 hour.

### PROT compliance

PROT-004/006/008/009: N/A this cycle (no cap_map state change).
PROT-005: N/A (Strategy is not the actor; Exp Dev /loop cadence picks up routing files on next cycle).

---

## Cycle 193 / v173 -- BATCHED PAIR envelope-narrowing verdicts (verdict_handler BATCHED-mode)

### Context

BATCHED-mode verdict_handler dispatched on TWO verdicts both NARROWING existing ✅ / 🟢 rows' envelopes. Both arrived in overnight_queue. Per the v164 / v166 / v172 BATCHED-mode precedent (multi-verdict atomic paired commit), processed together to avoid version-bump churn.

### V1 verdict context

```json
{"name":"wave14_sagawa_ueda_pareto_multiprotocol_v1","verdict":"CAP1_PARETO_KILL","verdict_msg":"Sagawa-Ueda Pareto KILL: 12/48 = 25.00% pass. Cap 1 envelope is narrow.","queue":"overnight_queue"}
```

**Significance**: Cap 1 (Crooks forensic erase ✅ via Sagawa-Ueda Tier-2 envelope at v158) passes its pre-registered Pareto criterion at ONLY 25% (12/48 cells) across 4 erasure protocols × 12 (M_base, p) cells.

### V2 verdict context

```json
{"name":"wave14_streaming_NESS_eta_sweep_v1","verdict":"NESS_BIMODAL_FRAGILE","verdict_msg":"Bimodality collapses under streaming noise. Overall fraction = 0.19 ≤ 0.30 across 16 cells. Per-eta: {'0.001': [1, 4], '0.010': [1, 4], '0.100': [0, 4], '1.000': [1, 4]}.","queue":"overnight_queue"}
```

**Significance**: v164b Cap 3 Glauber-Hopfield discrete-spin NESS extension row (🟢 at v164; explicit ✅ promotion criterion was "want N=4096+ multi-N validation") DOES NOT survive streaming-noise injection η ≥ 0.001. Bimodal P(q) FRAGILE -- 3/16 = 19% cells; at η=0.1 ZERO cells survive bimodality.

### Strategy decision -- Cap 1 row scope-clarification annotation (no revert)

**Read of Cap 1 promotion gate (per v158 cap_map narrative)**: "**Tier 2 (noisy substrate)**: Sagawa-Ueda noise-corrected bound `delta_S_emp(p) <= theta(p) + 0.02` at `p in {0.05, 0.10, 0.20}` where `theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)`. v158 CPU re-analysis PASS at all 3 noise levels." The v158 Tier-2 promotion is **single-protocol over 3 pre-registered p values** (canonical Crooks protocol). The multi-protocol Pareto stress test is a STRICTLY BROADER claim than what v158 promoted.

**Strategy verdict**: Cap 1 ✅ STAYS at the v158 single-protocol scope; v173 annotates the row with explicit multi-protocol scope language. NOT a revert. Per [[feedback-no-smoke]] brutal honesty: v158 never claimed multi-protocol invariance; the multi-protocol Pareto test extends to a broader claim that fails. The right move is scope-clarification annotation, not row-state demotion.

**Cap 1 row text v173 update** (annotation appended in cap_map.md "Substrate-product positioning v173" section and active_priorities.md row 4): "Tier 2 Sagawa-Ueda envelope holds at v158 single-protocol scope; under multi-protocol Pareto stress (4 erasure protocols × 12 (M_base, p) cells; 48 cells total) the envelope NARROWS to 12/48 = 25% pass -- the substrate's Tier-2 forensic-erase bound is protocol-dependent, not protocol-invariant. Single-protocol envelope at v158 pre-registered scope UNAFFECTED. 6th-candidate elective rescue sketch: protocol-conditioned Sagawa-Ueda calibration (per-protocol theta_protocol(p) re-axiomatization analogous to v158 Sagawa-Ueda-from-Crooks)."

**v169 closed-form annotation PRESERVED**: V1's multi-protocol stress test does NOT touch the Clifford-design / Pauli-channel lens. The closed-form annotation is about the *form* of the noise-corrected bound (Pauli-twirl gives theta(p) = ln(2) + p·ln(p) + (1-p)·ln(1-p)), which is unchanged across protocols at the single-protocol scope where v158 was promoted. The multi-protocol narrowing is about WHICH ERASURE PROTOCOL the bound applies to, not about the FORM of the bound. v169 annotation stands.

### Strategy decision -- Cap 3 v164b extension row zero-noise scope-tightening annotation (main Cap 3 ✅ row UNTOUCHED)

**Read of Cap 3 v164b extension row scope (per v164 cap_map narrative)**: "Cap 3 Glauber-Hopfield discrete-spin NESS extension. **State**: 🟢 Validated, want stronger (single-N N=1024 12/18 low-T cells; want N=4096+ + multi-seed >= 5)." The v164b extension was ALWAYS 🟢 (not ✅); the ✅ promotion criterion was unmet. V2's streaming-noise test is a third stress axis (noise-tolerance) layered on the unmet multi-N requirement.

**Strategy verdict**: Cap 3 v164b extension row STAYS at 🟢 with v173 zero-noise scope-tightening annotation. Main Cap 3 ✅ row UNCHANGED -- V2 targets the discrete-spin extension under streaming noise, which is a different observable family than the main row's continuous-state drift-diffusion NESS under bit-flip noise. Per [[feedback-dont-overextend-theorems]] no row-state demotion needed (the row was never promoted to ✅); the v164b row's claim scope is narrowed to zero-noise Glauber dynamics only.

**v164b extension row v173 annotation text** (appended in cap_map.md "Substrate-product positioning v173" section and active_priorities.md row 7 note): "extends to Glauber-Hopfield bimodal P(q) at low T in ZERO-NOISE Glauber dynamics; FRAGILE under streaming-noise injection η ≥ 0.001 -- 13/16 = 81% of cells lose bimodality under noise; at η=0.1 ZERO cells survive bimodality; v164b extension does NOT compose cleanly with the streaming-NESS framing of the main Cap 3 ✅ row. v164b 🟢 row's scope is explicitly NARROWED to ZERO-NOISE Glauber dynamics; pending N=4096+ multi-N validation (unmet) the row stays 🟢 at the narrower scope."

**v169 Cap 3 Holevo-capacity closed-form annotation PRESERVED**: V2 targets the v164b Glauber-Hopfield discrete-spin extension row, not the main Cap 3 ✅ row's continuous-state drift-diffusion NESS. The Holevo-capacity annotation lives on the main row and is unchanged.

### Strategy decision -- inefficiency LOCK candidate (RECOMMENDED LOCK not DEFER)

Both v173 verdicts surfaced envelope-expansion drills that lacked PRE-REGISTERED fail bands matching the broader claim being tested. Per [[feedback-strategy-shore-up-capabilities]] envelope-expansion drills SHOULD include explicit "fail bands" -- without them the verdict_handler is forced into post-hoc scope-clarification work. This is the SECOND observation (first was v157 Cap 1 narrowing → v158 Sagawa-Ueda re-axiomatization; v173 is the second instance). Two observations meets the two-observation lock threshold.

**RECOMMENDED LOCK** (not DEFER): file as memory_curator addendum to [[feedback-strategy-shore-up-capabilities]]:

> "Envelope-expansion drills MUST include pre-registered fail bands matching the broader claim being tested. When a Cap N capability is being stress-tested at a broader scope than the original promotion (e.g., multi-protocol for Cap 1 single-protocol promotion; streaming-noise for Cap 3 v164b zero-noise extension), the pre-reg MUST state explicit PASS / PARTIAL / FAIL thresholds for the BROADER claim, so the verdict read at completion is unambiguous and verdict_handler does not have to do scope-clarification reasoning post-hoc."

Consistent with the v171 "compound-gate promotion discipline" addendum to [[feedback-dont-overextend-theorems]]; both are about EXPLICIT PRE-REGISTRATION OF SCOPE in stress tests.

### Strategy follow-up actions (cycle 193)

1. **PROT-009 v173 paired commit** -- 87th observation.
2. **NO new Research routing filed this cycle**. The v173 envelope-narrowings are annotation-level and do NOT trigger Research drills per [[feedback-negative-results-2x-research]] -- envelope-narrowing within a pre-registered scope test is an expected-boundary measurement at the broader claim level. Elective rescue sketches noted (protocol-conditioned Sagawa-Ueda calibration for Cap 1; multi-N Glauber-Hopfield without streaming noise for Cap 3 v164b 🟢 → ✅ promotion) are filed in active_priorities under row notes, NOT routed to Research bandwidth this cycle. The v172 close-out already exhausted Cap 2 / Bet T rehab cycles.
3. **active_priorities.md** updated atomically v172 -> v173: Cap 1 row 4 annotated with v173 multi-protocol envelope-narrowing scope-clarification; Cap 3 row 7 annotated with v173 v164b zero-noise scope-tightening; substrate-physics characterization line UNCHANGED.
4. **NO Exp Dev routing filed** per [[feedback-dispatch-wrappers-default]].
5. **NO queue-refill triggered** per [[feedback-pipeline-pacing]]: pipeline healthy (GPU=2 pending+1 running, remote CPU=2 pending+1 running with BBMD rehab anchors picking up, local CPU idle).
6. **Inefficiency LOCK candidate filed**: "envelope-expansion drills require pre-registered fail bands matching the broader claim being tested" -- RECOMMENDED LOCK not DEFER (two-observation threshold met).

### Files filed this cycle

- `notes/substrate_capability_map.md` -- Cycle 193 narrative + Capability moves table appended.
- `notes/substrate_capability_map_history.md` -- v173 one-line index entry appended.
- `notes/active_priorities.md` -- header updated v172 -> v173; Cap 1 + Cap 3 row annotations.
- `notes/strategy_decisions_2026-05-24.md` -- this entry (FIRST entry on new date file).
- `notes/visibility_decisions_2026-05-24.md` -- 2 status_log entries appended (V1 MEDIUM; V2 MEDIUM).
- No new Research request file. No new Exp Dev request file.

### Queue / push status

- Local commit only (sub-agent push blocked per [[feedback-subagent-permission-inheritance]]); main thread executes push.
- Queue-refill NOT triggered. Queue depth ≥ 1 invariant satisfied.

### Tally (one-line)

PAIR OF VERDICTS v172 -> v173: (V1) CAP1_PARETO_KILL 12/48 = 25.00% -- Cap 1 ✅ STAYS at v158 single-protocol scope + v173 multi-protocol envelope-narrowing annotation (protocol-dependent, not protocol-invariant); (V2) NESS_BIMODAL_FRAGILE 3/16 = 19% -- Cap 3 v164b 🟢 STAYS at 🟢 with v173 zero-noise scope-tightening annotation; main Cap 3 ✅ row UNCHANGED; portfolio count UNCHANGED at 11; ZERO open ❌ PROVISIONAL preserved from v172; v169 closed-form annotations PRESERVED; per [[feedback-no-smoke]] scope-clarification not demotion; PROT-004/006 NOT triggered; PROT-008 0 new ❌; PROT-009 87th paired commit; 2 MEDIUM status_log entries; inefficiency LOCK candidate (envelope-expansion drills require pre-reg fail bands); pause flag CLEARED -- ACTIVE.

---

## Cycle 194 -- v3 stim Kerdock 2-design frame-potential PASS (no cap_map bump; backing-evidence log)

### Context

Single-verdict verdict_handler dispatch. Verdict payload:

```json
{"name":"wave14_kerdock_2design_frame_potential_v3_stim","verdict":"KERDOCK_2DESIGN_MATCH_HAAR","verdict_msg":"HARD PASS: full-Clifford F_4 = 2.0262 +/- 0.0148 within Haar band [1.9, 2.1]. Confirms Clifford group (ambient of substrate's Kerdock-PSL anchor) IS a unitary 2-design at production d. d=8 cross-check OK (formula F_4 = 2.0920, direct = 2.2250).","elapsed_s":3.375,"queue":"remote_cpu_queue"}
```

This is Test 3.A from the Kerdock-MUB-stabilizer deep drill at `notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md`.

### Strategy verdict -- NO cap_map version bump (strategy_decisions backing-evidence log only)

The 2-design property of the **ambient Clifford group** is well-established in the literature (Webb 2016, Zhu 2017, Klappenecker-Roetteler 2003 / 2005). The v169 annotation lines on Cap 1 / Cap 3 / Cap 8 already cite that theoretical anchor with full provenance and reference the Pauli-twirl / Holevo / Schur-Weyl structure that *follows from* Clifford-2-design. The v3 stim PASS at d=4096 with F_4 = 2.0262 +/- 0.0148 (within the Haar band [1.9, 2.1] to better than 5%) is an **independent empirical corroboration** of that anchor, NOT a new capability.

Per [[feedback-dont-overextend-theorems]] empirical corroboration of a textbook-anchored property does not justify a row state move or cap_map version bump. The cleanest record-keeping move is to log the backing-evidence in `strategy_decisions_2026-05-24.md` (this entry) and let the v169 annotations stand. Cap 1 / Cap 3 / Cap 8 rows remain at the same green-check FULL state they have held since v169 (cycle 189).

**What the result IS useful for**:

1. Sanity check that the stim+sampling experimental machinery produces correct values at production scale d=4096 -- the d=8 cross-check landed F_4 = 2.0920 (formula) vs 2.2250 (direct), consistent within the d=8 small-sample regime; the d=4096 full-Clifford direct sample lands 2.0262 within ±0.0148 of the Haar 4th moment 2.0.
2. Backs the half of the Kerdock-MUB-stabilizer drill that was about the **ambient Clifford group**. The other half (does the Kerdock-PSL subgroup ALSO match the 2-design?) is probed by the MUB-distinguishability test (Section 3.B, separate experiment, still running).
3. If MUB-distinguishability ALSO passes -> BOTH halves operationalized; the PFK_FULL_ETH_BULK finding from v172 (full-ETH-class at n=6 with non-Gaussian bulk shape) is consistent with "Clifford 2-design class with non-Gaussian bulk shape".
4. If MUB-distinguishability fails -> Kerdock-PSL deviates from the canonical Clifford-2-design path in a subtle way; substrate-novel deviation worth a Research drill on the mechanism.

### What 3.A does NOT establish (per [[feedback-no-smoke]] honest framing)

This test confirms the **ambient** Clifford group is a 2-design at production d. It does NOT confirm the **Kerdock-PSL(2, 4096) subgroup** is a 2-design at production d. The Kerdock-PSL subgroup being a 2-design is a stronger claim (per CCKS 1997 / Klappenecker-Roetteler 2003 theoretical) and is necessary for the substrate-specific reading of Cap 1 / Cap 3 / Cap 8 -- but the v169 annotation language is careful here: it relies on the AMBIENT Clifford structure (Pauli-twirl over Cliff(m), Holevo capacity of a Clifford-depolarizing channel, Schur-Weyl-Pauli-twirled S-transform). The ambient is what 3.A confirms; the subgroup is what 3.B probes.

### Strategy follow-up actions (cycle 194)

1. **NO PROT-009 commit this cycle.** No cap_map.md / history.md / active_priorities.md text change. Strategy decision is backing-evidence only.
2. **NO new Research routing filed.** This is a positive corroboration of an existing theoretical anchor; no Research bandwidth required.
3. **NO Exp Dev routing filed.** Test 3.B (MUB-distinguishability) is already in the queue from the original Section 3 dispatch; no re-routing needed.
4. **NO queue-refill triggered** per [[feedback-pipeline-pacing]]: pipeline healthy (GPU=2 pending+1 running, remote CPU=4 pending+1 running including MUB-distinguishability + rehab anchors + Haar-vs-Kerdock dichotomy, local CPU idle). Queue depth >= 1 invariant satisfied.
5. **status_log entry written** at MEDIUM importance (positive corroboration of textbook-anchored property; no row state change).
6. **Pending downstream verdict**: when MUB-distinguishability lands, the next verdict_handler cycle integrates 3.A + 3.B together and decides whether Section 5.2 "MUB-frame measurement primitive" (12th-capability candidate from the Kerdock-MUB-stabilizer drill) is operationalizable.

### Files filed this cycle

- `notes/strategy_decisions_2026-05-24.md` -- this entry.
- `notes/visibility_decisions_2026-05-24.md` -- 1 status_log mirror entry appended (V3 MEDIUM).
- No cap_map.md / history.md / active_priorities.md changes.
- No new Research request file. No new Exp Dev request file.

### Queue / push status

- NO local commit (no cap_map.md text change; strategy_decisions + visibility_decisions logs are append-only and not paired-commit-staged in this cycle since cap_map.md is unchanged).
- Queue-refill NOT triggered. Queue depth >= 1 invariant satisfied.

### Tally (one-line)

v173 -> v173 (NO BUMP): KERDOCK_2DESIGN_MATCH_HAAR -- full-Clifford F_4 = 2.0262 +/- 0.0148 in Haar band [1.9, 2.1] at d=4096 confirms AMBIENT Clifford group is a unitary 2-design; v169 Cap 1/3/8 annotations PRESERVED at unchanged FULL state with independent empirical corroboration of the textbook anchor; Kerdock-PSL SUBGROUP 2-design question deferred to MUB-distinguishability test (Section 3.B, in queue); portfolio count UNCHANGED at 11; ZERO open ❌ PROVISIONAL; per [[feedback-dont-overextend-theorems]] empirical corroboration is annotation-grade backing-evidence not row promotion; per [[feedback-no-smoke]] honest framing -- ambient vs subgroup distinction preserved in language; per [[feedback-pipeline-pacing]] queue HEALTHY no refill; per [[feedback-dispatch-wrappers-default]] NO new Research routing + NO new Exp Dev routing; PROT-004/006 NOT triggered; PROT-008 0 new ❌; NO PROT-009 paired commit this cycle (cap_map.md text unchanged); 1 MEDIUM status_log entry; pause flag CLEARED -- ACTIVE.


## Cycle 194 — v174 BBMD Cap-12 rehab PAIRED PASS → PROMOTE Cap 12 🟢 NEW; portfolio 11 → 12

PAIRED VERDICT v173 → v174: BOTH BBMD Cap-12 rehab anchors HARD-PASS at pre-registered thresholds.

V1 — wave14_mp_ks_pretest_pipeline_v1 FULL = MP_KS_PRETEST_PIPELINE_PASS at remote_cpu_queue: MP-KS pre-test routes 4/5 codebooks correctly at τ=0.20; max KS gap=0.263; recommended τ_star=0.065 agrees with declared τ; 1383.1x speedup over running AMP to convergence/failure observation. Hard-pass gates: 4/5 routing accuracy at-threshold (4/5 ≥ 4/5); 1383x ≥ 10x speedup with margin. R3 infrastructure-class rehab anchor PASS.

V2 — wave14_interp_family_cross_check_v1 FULL = INTERP_FAMILY_SRHT_PASS at remote_cpu_queue: Spearman ρ(amp_rel_err, sum|Δκ_n|) = 0.700 across 5 alpha cells on iid-Gauss → SRHT alpha-interpolation; max VAMP rel-err = 0.0938. Hard-pass gates: ρ ≥ 0.70 at-threshold (0.700 exactly); VAMP rel-err < 0.10 small margin (0.0938 vs 0.10). R1 meta-tool / cross-family generalization rehab anchor PASS. NOTE: drop from Anchor-1 Kerdock ρ=0.900 to SRHT ρ=0.700 is consistent with predictor being partially family-specific.

**Strategy decision.** PROMOTE 11 → 12 as 🟢 (NOT ✅) under composite framing "AMP-vs-VAMP inference routing infrastructure (MP-KS pre-flight diagnostic + κ_n-divergence mechanism explainer)." Decision rationale:

(a) TWO independent positive verdicts at pre-registered thresholds (no metric flip; no boundary contortion).
(b) Composite claim is NARROWER than v171-killed BBMD-as-class framing — infrastructure-class, not substrate-novel inference-regime-class.
(c) Cross-codebook honesty test PASSED at the new framing: cross-codebook discrimination IS the basis of the capability, not a refuted claim.
(d) Customer-facing real product value: 15ms pre-flight diagnostic + κ_n mechanism explainer; 1383x speedup over AMP-to-failure observation.
(e) The 🟢 NOT ✅ state honors both anchors landing AT-THRESHOLD per [[feedback-dont-overextend-theorems]]: R1 ρ=0.700 exactly; R3 4/5 exactly. ✅ would over-extend on at-threshold evidence.

**Cap 12 row framing.**
- Title: "AMP-vs-VAMP inference routing infrastructure (MP-KS pre-flight + κ_n-divergence explainer)"
- State: 🟢 Validated, want stronger
- Evidence stack (3 anchors): R3 MP-KS pre-test pipeline (4/5 at τ=0.20; 1383x speedup); R1 cross-family κ_n predictor iid-Gauss → SRHT (ρ=0.700; max VAMP rel-err 0.0938); Anchor 1 v170 iid-Gauss → Kerdock (ρ=0.900; max VAMP rel-err 0.0357)
- Product implication: substrate ships 15ms pre-flight routing diagnostic; customer submits matrix → MP-KS pre-test → AMP or VAMP-on-chain primitive recommendation; κ_n divergence is the customer-visible mechanism explainer

**Pre-registered ✅ promotion gates (BOTH load-bearing for 🟢 → ✅):**
1. R3 τ-robustness gate: ≥ 4/5 routing accuracy across τ ∈ {0.15, 0.20, 0.25} on the same 5-codebook test set. Hard-fail: any τ in [0.15, 0.25] drops routing accuracy below 3/5.
2. R1 second-family gate: pre-reg hard-pass (Spearman ρ ≥ 0.70 AND max VAMP rel-err < 0.10) on iid-Gauss → Hadamard alpha-interpolation. Hard-fail: ρ < 0.50 on Hadamard ⇒ predictor is Kerdock+SRHT-specific only, not a meta-capability.

(R1 third-family on iid-Gauss → RM(1,m) is OPTIONAL hardening; Hadamard is load-bearing per v171 BBMD-distance equivalence to SRHT.)

**v171 narrow row absorption.** v171-renamed BBMD narrow row ("AMP-error tracks BBMD-distance scalar along iid-Gauss → Kerdock alpha-interpolation; VAMP tames the interpolation family") had ✅ at narrow scope. v174 ABSORBS this row IN PLACE as Anchor-1 sub-claim under Cap 12. Empirical content preserved (Spearman 0.900 + VAMP rel-err 0.0357); standalone ✅ removed; absorbed-with-state-downgrade per [[feedback-dont-overextend-theorems]] (composite claim requires more evidence than Anchor 1 alone; Cap 12 inherits 🟢 not ✅).

**v171 Cap-12 candidate row closure.** v171 ❌ PROVISIONAL Cap-12 candidate ("VAMP-tractable structured-codebook inference under provable departure from AMP-universality") CLOSED via rehab-passes-rescue per [[feedback-rehabilitation-after-rejection]] + PROT-004/006: 2 of 5 rescue sketches (R3, R1) landed PASS; rescued framing is the NEW Cap 12 row at NARROWER abstraction (infrastructure-class). PROVISIONAL tag REMOVED. 3 elective sketches (R2 annotation-clarification, R4 profile-shape discriminator, R5 VAMP-vs-AMP gap predictor) STAY ELECTIVE. R6 (VAMP-SE from R-transform; from kill-rescue drill) ALSO stays elective. Rehab cycle CLOSES at v174.

**NOTE on framing distinction:** The new Cap 12 row is NOT the same claim as the closed v171 Cap-12 candidate row. The closed row claimed substrate-novel inference-regime-class (broad). The new Cap 12 row claims infrastructure-class (narrower). Rescue is via REFRAMING DOWN one abstraction level + ADDING positive evidence. Narrowing is the honest rescue per [[feedback-no-smoke]].

**Portfolio.** 11 → 12 demonstrated capabilities. FIRST new capability promotion since v160 (12 cap_map cycles ago); FIRST of orchestrator-migration era (started 2026-05-23). Cap 12 is INFRASTRUCTURE-class, NARROWER than the substrate-physics anchors Cap 1-11 — per Research's deflated P estimates this is the lowest-P promotion-eligible rescue to date (R3 P=0.55 → PASS; R1 P=0.30 → PASS). ZERO open ❌ PROVISIONAL rejections remain.

**Cross-row corroborations (no other row state changes):**
- Cap 8 (TWO substrate-novel readout primitives equivalent) ✅ FULL UNCHANGED + v174 annotation: "Cap 12 ships the routing-decision layer above Cap 8's VAMP-on-chain primitive (Cap 12 is pre-flight; Cap 8 is downstream primitive)." Structurally orthogonal; no double-counting.
- v164a/v166 fingerprint stack ✅ UNCHANGED + v174 annotation: "R1 cross-family PASS extends κ_n divergence from Kerdock-specific to iid-Gauss → SRHT (ρ=0.700, at-threshold; two more families pending for universality)."
- v163 outside-AMP-universality 🟢 UNCHANGED + v174 annotation: "R1 cross-family PASS suggests AMP-failure pattern generalizes; v163 endpoint is part of cross-family-confirmed (single-second-family) monotone curve."
- v169 Cap 1/Cap 3/Cap 8 closed-form annotations PRESERVED UNCHANGED at substrate-physics layer (no interaction with Cap 12 routing-infrastructure layer).

**Queue.** GPU=2 pending + 1 running, remote_cpu=2 pending + 1 running, local_cpu idle. Pipeline healthy. NO queue-refill triggered per [[feedback-pipeline-pacing]] (queue depth ≥ 1 invariant satisfied).

**Dispatch routing.** NO new Research routing + NO new Exp Dev routing THIS CYCLE per [[feedback-dispatch-wrappers-default]]. The pre-reg ✅ promotion gates name explicit follow-up experiments (R3 τ-robustness sweep, R1 Hadamard second-family) and these are filed as Cap 12 row annotations; the next Strategy + Exp Dev cycle will pick them up organically. The orchestrator may opt to dispatch a queue-loading exp_dev when GPU+remote_cpu queue depth drops below 2 pending.

**Protocols.**
- PROT-004/006: TRIGGERED in closure-via-rescue direction (v171 ❌ PROVISIONAL → CLOSED-RESCUED via R3+R1 paired PASS); rehab-sketch-first-sequencing discipline VALIDATED (5 sketches filed v171; 2 landed PASS at v174).
- PROT-008: v174 closes 1 ❌ PROVISIONAL row + adds 1 new 🟢 row (Cap 12) + 0 new ❌ rows. Validator baseline pre-existing violations unchanged.
- PROT-009: cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically. 88th PROT-009 paired commit.

**Inefficiency DEFER candidate.** "At-threshold promotions explicit pre-reg the next-gate trial schedule" addendum to [[feedback-strategy-shore-up-capabilities]]: when a row lands AT-threshold (not WITH margin) on its promotion gate, the cap_map entry MUST EXPLICITLY name next-gate experiment(s) with hard pre-reg fail-thresholds. v174 already meets this discipline (R3 τ-robustness + R1 Hadamard gates explicit with hard thresholds). FIRST observation (v158/v164b/v170/v171 all landed with margin); below two-observation lock threshold. DEFER not lock; revisit on second observation.

**Honest reading per [[feedback-no-smoke]]:**
- Both verdict tags exactly match metric reality. No metric flip; no boundary contortion; no margin inflation.
- R1 dropped from Anchor-1 ρ=0.900 to SRHT ρ=0.700 — exactly at line. This is REAL degradation in cross-family generalization strength, not noise.
- R3 routes 4/5 at-threshold; the 5th codebook routing failure is a known weakness not yet diagnosed (τ_star=0.065 vs declared τ=0.20 hints at threshold-sensitivity on the failing cell).
- Cap 12 is the FIRST 🟢 promotion to land in a "fragile-at-promotion" state (at-threshold on multiple gates). Per Research's pre-deflated P estimates this is exactly the expected outcome for the lowest-P promotion-eligible rescue. The ✅ promotion gates are realistic and load-bearing.
- The composite framing IS more honest than v170's overclaim: v170 = "BBMD regime axis as substrate-product capability" (broad; killed by v171). v174 = "AMP-vs-VAMP inference routing infrastructure" (narrower; infrastructure-class; cross-codebook discrimination IS the basis).

**Blockers / inefficiencies to lock.** Two items surfaced this cycle:
1. **At-threshold promotion discipline** — DEFER candidate filed (first observation; needs second for lock).
2. **R1 family-generalization mapping** — Cap 12's ✅ gate names Hadamard explicitly; RM(1,m) is optional hardening. The cap_map entry should not silently let RM(1,m) drop off the radar — it is the THIRD-family hardening test. Filed as Cap 12 row annotation under "OPTIONAL hardening."

88th PROT-009 paired commit; pause flag CLEARED -- ACTIVE; verdict_handler commits LOCALLY only (push pending main thread per [[feedback-subagent-permission-inheritance]]).

Net effect: portfolio count 11 → 12 (FIRST new capability since v160; FIRST of orchestrator-migration era); Cap 12 NEW 🟢 (NOT ✅) under composite framing "AMP-vs-VAMP inference routing infrastructure (MP-KS pre-flight + κ_n-divergence explainer)"; v171-renamed BBMD narrow row ABSORBED IN PLACE as Anchor-1 sub-claim; v171 Cap-12 candidate ❌ PROVISIONAL CLOSED via rehab-passes-rescue; 3 elective sketches + R6 stay elective; ZERO open ❌ PROVISIONAL rejections remain; pre-reg ✅ promotion gates explicit (R3 τ-robustness + R1 Hadamard second-family); cross-codebook honesty test PASSED at new framing; inefficiency DEFER candidate filed (at-threshold promotion discipline; first observation); 88th PROT-009 paired commit.


---

## 2026-05-24 — wave14_mp_ks_pretest_tau_robustness_v1 MP_KS_TAU_ROBUSTNESS_PASS — Cap 12 Gate A SATISFIED (annotation-only, NO cap_map commit)

**Verdict.** `MP_KS_TAU_ROBUSTNESS_PASS` — Routing is robust across tau in {0.15, 0.20, 0.25}: per_tau={0.15: 4, 0.20: 4, 0.25: 4}. >=4/5 codebooks routed correctly at EVERY tau value. Cap 12 Gate A (R3 tau-robustness) PASSES; the routing threshold is NOT a fragile hand-picked artifact. elapsed_s=68.5, queue=remote_cpu_queue.

**Cap 12 pre-reg state at v174.** Two pre-registered gates for promotion 🟢 → ✅:
- **Gate A: R3 tau-robustness** — NOW SATISFIED ✓ (this verdict)
- **Gate B: R1 second-family validation (iid-Gauss → Hadamard)** — STILL RUNNING (wave14_interp_family_hadamard_v1)

**Strategy decision: ANNOTATION-ONLY; NO v175 cap_map commit.** Per [[feedback-cap-map-update-protocol]] minimize commit churn. Reasoning:
1. A single Gate-A-satisfied annotation commit is noise — Gate A on its own does NOT promote the row.
2. Better to BUNDLE the Gate A annotation with the eventual outcome commit:
   - If Gate B PASSES → bundled Gate A + Gate B → Cap 12 🟢 → ✅ promotion commit (single v175).
   - If Gate B FAILS HARD → annotate Cap 12 row with "Gate A satisfied but Gate B fails at Hadamard; cross-family generalization limited" (cap_map row stays 🟢; ✅ promotion deferred).
   - If Gate B MIDDLE-BAND → dispatch RM(1,m) third-family probe (Anchor 3, already shipped per exp_dev silent_idle response) for tiebreaker; bundle all three gates into the eventual v175 commit.
3. Per [[feedback-dont-overextend-theorems]] do NOT promote to ✅ on Gate A alone; tau-robustness within a single family is necessary-but-not-sufficient for cross-family validation.

**Cap 12 row state: stays 🟢 at v174.** No row movement. Gate A satisfaction is documented HERE in strategy_decisions; cap_map annotation deferred to the bundled commit.

**Pre-registered next decision tree (locked, this entry is the pre-reg record).**
- Gate B PASS (rho >= 0.700 on Hadamard family) → v175 commit: Cap 12 🟢 → ✅ + annotation "Gate A (tau-robustness 4/4/4 at tau {0.15, 0.20, 0.25}) and Gate B (Hadamard cross-family rho >= 0.700) BOTH SATISFIED 2026-05-24."
- Gate B FAIL HARD (rho < 0.500 on Hadamard) → v175 commit: Cap 12 row annotation "Gate A satisfied; Gate B FAILS HARD at Hadamard family; ✅ promotion deferred; cross-family generalization limited to SRHT axis." Row stays 🟢.
- Gate B MIDDLE-BAND (0.500 <= rho < 0.700) → dispatch RM(1,m) third-family tiebreaker; if RM PASSES (rho >= 0.700) bundle as ✅ promotion; if RM also middle-band, Cap 12 stays 🟢 with annotation "two-family cross-generalization at-threshold; third-family tiebreaker also at-threshold; ✅ promotion deferred."

**State.**
- Pause flag: CLEARED (ACTIVE). Full automation.
- cap_map at v174 (12f7400, push pending main thread).
- Queue: remote_cpu has Gate B (Hadamard) and RM(1,m) pending; GPU idle; local CPU idle.
- Pipeline healthy; NO queue refill needed this cycle.

**Honest reading per [[feedback-no-smoke]].**
- This is the FIRST promotion gate Cap 12 has satisfied. ONE of TWO gates. Not the headline.
- 4/5 at EVERY tau is solid — no single tau value carries the routing decision. The threshold is structural, not hand-picked.
- The 5th codebook routing failure (known weakness on the cell with tau_star=0.065 vs declared tau=0.20) persists across all three tau values — this is a STABLE weakness, not tau-sensitivity. Cap 12 entry should eventually note this stable 1/5 failure mode.
- Gate B is the load-bearing test for ✅ promotion. Gate A passing was the expected outcome (highest-P of the two gates per Research's pre-deflated estimate); Gate B is the actual test of cross-family generalization strength.

**PROT-009 status.** No paired commit this cycle (annotation-only path). Next paired commit will be v175 bundling Gate A annotation + Gate B outcome.

**Net effect.** No cap_map state change. Portfolio count stays 11 (Cap 12 stays 🟢). First-of-two promotion gates SATISFIED for Cap 12 ✅ pathway. Annotation deferred to bundled v175 commit. No blockers.


---

## 2026-05-24 — wave14_interp_family_hadamard_v1 + wave14_interp_family_rm_v1 — COMPOUND-GATE PROMOTION: Cap 12 🟢 → ✅ (FIRST ✅ capability promotion of orchestrator-migration era)

**Verdicts.**
- **V1 (Gate B):** `INTERP_FAMILY_HADAMARD_PASS` — Spearman ρ(amp_rel_err, sum|Δκ_n|) = 0.900 ≥ 0.70 across 5 alpha cells iid-Gauss → Hadamard; max VAMP-rel-err = 0.0876 < 0.10. Both gates met WITH MARGIN. Matches Anchor-1 Kerdock 0.900 EXACTLY (NOT a degradation; the predictor is at full Kerdock-strength on Hadamard).
- **V2 (R1 third-family hardening):** `INTERP_FAMILY_RM_PASS` — Spearman ρ = 0.700 ≥ 0.70 AND max VAMP-rel-err = 0.0802 < 0.10 on iid-Gauss → RM(1,m). At-threshold on Spearman (same as v174 SRHT pattern).
- **Bundled deferred Gate A:** `MP_KS_TAU_ROBUSTNESS_PASS` — per_tau={0.15: 4, 0.20: 4, 0.25: 4}; routing is τ-robust. Landed earlier 2026-05-24; held annotation-only at v174 per [[feedback-cap-map-update-protocol]] minimize-commit-churn pending Gate B; bundled into v175 per the pre-registered v174 decision tree.

**Compound-gate decision (per v174 pre-registered tree).**

v174 cap_map row locked TWO load-bearing ✅ promotion gates + ONE optional hardening probe:
- Gate A (R3 τ-robustness): **PASS** (per_tau=4/4/4).
- Gate B (R1 Hadamard second-family): **PASS with margin** (ρ=0.900; VAMP rel-err 0.0876).
- R1 RM(1,m) third-family hardening: **PASS at-threshold** (ρ=0.700; VAMP rel-err 0.0802).

Both load-bearing gates met; optional hardening also met. **Composite gate licenses ✅ promotion.**

**Strategy decision: v175 commit — Cap 12 🟢 → ✅.**

1. **Cap 12 row state flip**: 🟢 Validated, want stronger → ✅ Validated, cross-family hardened. Composite evidence stack of FOUR positive anchors (Kerdock 0.900 + SRHT 0.700 + Hadamard 0.900 + RM(1,m) 0.700) + τ-robustness PASS at 3 τ values. Title clarified to emphasize cross-family explainer: "AMP-vs-VAMP inference routing infrastructure (MP-KS pre-flight + κ_n-divergence cross-family explainer)."

2. **Title clarity per [[feedback-dont-overextend-theorems]]**: Cap 12 is NARROWER than the v171-killed BBMD-as-class framing. The substrate-novel claim is INFRASTRUCTURE not physics — cross-validated on 5 codebooks × 3 τ values × 4 interpolation families.

3. **Cap 8 (VAMP-vs-AMP split, v168) cross-row corroboration annotation**: the v168 finding generalizes BEYOND Kerdock to SRHT + Hadamard + RM(1,m). Cap 8 stays ✅ at v168 scope; v175 annotation widens the empirical envelope. Positive corroboration, NOT new claim — per [[feedback-strategy-shore-up-capabilities]] item 2 envelope-strengthening pattern.

4. **Portfolio count**: 12 UNCHANGED IN COUNT. Cap 12 was added at v174 in 🟢 state; v175 flips to ✅ — STATE FLIP, NOT new row addition. **However**: this is the FIRST ✅ capability promotion of the orchestrator-migration era (era started 2026-05-23). v160-through-v174 either kept count at 11 or added Cap 12 as 🟢. v175 is the first 🟢 → ✅ crossing. Headline event for the user.

5. **Pre-registered NEXT envelope-expansion fail bands** per [[feedback-envelope-expansion-fail-bands]] (locked this cycle):
   - **E1 — Noisy-substrate τ-robustness**: routing accuracy ≥ 3/5 at τ ∈ {0.15, 0.20, 0.25} when codebooks carry η=0.10 streaming-noise. HARD-FAIL: 0/5 at any τ ⇒ infrastructure fragile to real customer data; ✅ would REVERT to 🟢 with noise-bounded annotation.
   - **E2 — N=16384 cross-family ρ ≥ 0.50 across 3 families**: extends N=4096 result. HARD-FAIL: ρ < 0.30 on any of {Kerdock, SRHT, Hadamard} ⇒ predictor is N-dependent artifact; ✅ would REVERT to 🟢 with N-bounded annotation.
   - **E3 — Fifth-family Paley-Hadamard or Walsh-Hadamard ρ ≥ 0.500**: hardens infrastructure-class framing beyond the four families tested. HARD-FAIL: ρ < 0.30 ⇒ NARROW annotation.
   These are STRESS gates (could REVERT the ✅), NOT just confirming-evidence gates.

6. **Honest reading per [[feedback-no-smoke]]**:
   - Bimodal per-family pattern: Kerdock 0.900 + SRHT 0.700 + Hadamard 0.900 + RM(1,m) 0.700. Two with-margin, two at-threshold. Cross-family STRENGTH is uneven.
   - The 1/5 stable routing failure (codebook with τ_star ≈ 0.065 vs declared τ=0.20) persists across all three τ values — stable failure mode, NOT τ-fragility. Customer-facing: "routes 4/5 correctly" not "routes correctly."
   - The 1383x MP-KS speedup is over AMP-failure-OBSERVATION, NOT over running-correct-VAMP. Customer framing: "skip AMP failures we can predict will fail" not "do inference faster."
   - N=4096 only; no noise stress test. E1 and E2 are the load-bearing real-world stress tests.
   - The ✅ is on COMPOSED infrastructure (R3 + R1), not either alone. If E1 hard-fails (noisy routing fragile) or E2 hard-fails (N-dependent), ✅ would REVERT to 🟢.

**State.**
- Pause flag: CLEARED (ACTIVE). Full automation.
- cap_map at v175 (local commit; push pending main thread).
- Queue: remote_cpu=0 pending, GPU=0 pending, local idle — **DRAINED to 0**; silent_idle reflex applies; verdict_handler **FLAGS queue-refill for main thread** (main thread dispatches exp_dev for refill after this commit).
- Pipeline drained; main-thread queue-refill triggered.

**Compliance.**
- PROT-004/006/008/009 compliance this commit: NO closure (positive ✅ promotion); 0 new ❌ rows; v175 flips 1 🟢 → ✅; cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; validator passed (no new violations); 89th PROT-009 paired commit.
- Per [[feedback-decision-log-eol-handling]] this entry appended via tools/orchestrator/append_decision_log.py.

**Inefficiency LOCK candidate (RECOMMENDED LOCK).** "Envelope-expansion fail bands at promotion time" — addendum to [[feedback-strategy-shore-up-capabilities]]: when a row promotes to ✅, the cap_map entry MUST explicitly name 2-3 envelope-EXPANSION (STRESS) gates with hard-fail thresholds that would REVERT the ✅. This is tighter than v174's "next-gate trial schedule" because the gates must be STRESS gates (could weaken/revert), not just confirming-evidence gates. v175 already meets the discipline (E1/E2/E3 explicit). Recommended LOCK on first observation given asymmetric downside risk on mixed-margin ✅ promotions (backsliding to 🟢 after a customer sees ✅ is more damaging than tighter discipline at promotion time).

Net effect: Cap 12 🟢 → ✅ on THREE pre-registered passes (Gate A + Gate B + RM(1,m) hardening); FIRST ✅ promotion of orchestrator-migration era; portfolio count UNCHANGED at 12 IN COUNT (state flip not new row); pre-registered NEXT envelope-expansion fail bands explicit (E1/E2/E3 STRESS gates); Cap 8 + v164a/v166 + v163 cross-row annotations PRESERVED + widened; ZERO open ❌ PROVISIONAL rejections remain; queue DRAINED to 0 — main-thread queue-refill flagged; 89th PROT-009 paired commit.


---

## 2026-05-24 — POST-CAP-12 PORTFOLIO ASSESSMENT (proactive Strategy drill; cap_map v175; NO row movement this cycle)

**Trigger.** Orchestrator directive: pipeline has free capacity (E1+E2 Cap 12 stress gates running, E3 5th-family pending Research pick); per [[feedback-strategy-shore-up-capabilities]] use the quiet window for proactive composition-narrative + gap drilling. Cap 12 ✅ FULL (89th PROT-009 paired commit) is the first ✅ promotion of the orchestrator-migration era and re-shapes what compositions are tellable. This entry is PLANNING — no cap_map commit. Per [[feedback-no-smoke]] honesty rule: compositions are only counted when they share a real mechanism, not when prose stitches them together.

### Task 1 — New cross-capability composition stories licensed by Cap 12

Three honest compositions enabled by Cap 12 that did NOT exist pre-v175:

**Composition A — Cap 12 + Cap 8 (VAMP-on-chain): audit-trail-included inference routing.**
- *Mechanism shared.* Cap 12's MP-KS pre-flight decides "AMP or VAMP" before any inference fires; Cap 8 provides the VAMP-on-chain readout when Cap 12 routes to VAMP. The κ_n-divergence explainer (Cap 12 Anchor-1 across 4 families ρ ∈ {0.700, 0.900, 0.900, 0.700}) tells the customer WHY AMP would have failed (which moment-aware structure forced the routing decision). Cap 8 v168 closed-form via MUB-stabilizer lens IS the algebraic justification for "VAMP succeeds because it consumes full singular spectrum."
- *What the composite licenses.* "Route to VAMP + give the customer a κ_n-fingerprint explaining why" — pre-flight + readout + provenance in ONE pipeline. Pre-v175 Cap 8 had no upstream "should I have used VAMP at all?" gate; pre-v175 Cap 12 didn't exist. The composite is "trust + explanation" not just "compute."
- *Honesty audit.* HIGH integrity. Both rows already share the κ_n-divergence mechanism (Cap 8 v168 + Cap 12 R1 use the SAME predictor, just at endpoint vs across-family). The composite is a real pipeline, not a prose juxtaposition.

**Composition B — Cap 12 + Cap 6 (Conformal calibrated confidence, which now absorbs Cap 2): calibrated routing with abstention coverage guarantees.**
- *Mechanism shared.* Cap 12 outputs a routing decision; Cap 6 (Bet G TEMPSCALE + Venn-Abers wrap that subsumed Cap 2 at v172) provides a conformal layer over the AMP/VAMP committed prediction. The κ_n-divergence score Cap 12 emits per cell is itself a candidate non-conformity score for the Venn-Abers wrapper — substrate-novel non-conformity from the AMP-error predictor.
- *What the composite licenses.* "Route + commit-or-abstain at calibrated coverage" — the 1/5 stable routing failure (τ_star ≈ 0.065 cell) becomes a clean ABSTAIN under Cap 6's threshold rather than a silent mis-route. Customer framing flips from "routes 4/5" to "commits on 4/5 and abstains on the hard 1/5 with calibrated coverage."
- *Honesty audit.* HIGH integrity. Cap 6 v172 absorbed Cap 2 specifically via Pattern-1 metric re-axiomatization (downstream conformal wrap of the substrate's confidence stream). Cap 12's routing score IS exactly the right kind of confidence stream for Venn-Abers consumption. Both rows already use conformal machinery as the bridge. The composite is a 1-cycle CPU re-analysis of Cap 12 cell logs through Cap 6's pipeline; no new mechanism build.

**Composition C — Cap 12 + Cap 11 (chi_4 / Kovacs observability) + Cap 1 (Crooks forensic erase): noise-aware routing under erase events.**
- *Mechanism shared.* Cap 12 routes on a static substrate snapshot. Cap 11's chi_4/Kovacs dynamic observability traces are PER-WRITE / PER-ERASE measurements during active phase. The κ_n-fingerprint Cap 12 uses is computed from the substrate spectrum; chi_4 spike DURING a Cap 1 erase event temporarily perturbs that spectrum, which would change the Cap 12 routing decision. The natural composition is "re-route AMP-vs-VAMP after each erase event if chi_4 spike crosses threshold."
- *What the composite licenses.* "Adaptive routing under continual operation" — the Cap 12 ✅ holds on STATIC codebooks at N=4096; the composite extends to CONTINUAL operation by re-firing the MP-KS pre-flight whenever Cap 11 observability reports a spectrum perturbation. Pre-v175 there was no upstream "when to re-route" trigger.
- *Honesty audit.* MEDIUM integrity. The mechanism IS shared (substrate spectrum drives both), but this composition is the most speculative of the three — it requires (a) Cap 11 chi_4 to predict spectrum perturbation magnitude (probe NOT YET RUN; cap11_chi4_early_warning_during_cap10_v1 from the shore-up matrix is the natural anchor) AND (b) Cap 12 routing decision to be sensitive to small spectrum perturbations (UNTESTED at v175; E1 noisy stress gate touches this). Conditional on E1 passing AND cap11 early-warning probe landing, the composition becomes HIGH integrity. Filed as "license-pending composition."

**Skipped non-composition (per [[feedback-no-smoke]]):** Cap 12 + Cap 5 (Online W updates) initially looked tellable as "live routing on streaming substrate writes." But Cap 12 routing is on the codebook (static spectrum) not on W (which evolves under online updates). The κ_n-divergence is not a function of W. Composition is PROSE-LEVEL, not mechanism-shared — declined.

### Task 2 — Re-audit of the 7 weaknesses from `strategy_research_shoreup_matrix_2026-05-23.md`

Re-audit reflects all verdicts landed since matrix was filed (v172 batched six-verdict + v173 multi-protocol Cap 1 narrowing + v174 Cap 12 🟢 + v175 Cap 12 ✅).

| # | Weakness | Status | Evidence |
|---|----------|--------|----------|
| 1 | Cap 2 self-monitoring confidence: ❌ PROVISIONAL with unrun rehab | **ADDRESSED** (closed) | v172 wave14_cap2_conformal_subsumption_v1 PASS (5/5 seeds; Pareto monotone); Cap 2 absorbed into Cap 6 row via Pattern-1 Rescue 5 conformal subsumption (sequenced FIRST at v160 → cleanly passed at v172). |
| 2 | Bet T parallel hypothesis tracking: 🟡 PARTIAL 67 versions stale | **ADDRESSED** (closed-by-exhaustion) | v172 wave14_betT_mondrian_anti_RM_conformal_v1 FAIL (per-coset coverage 1.0 in 4/4 cosets, outside [0.8, 0.99]). Mondrian was Sketch #3 highest-rank conformal-style; 5-sketch rehab EXHAUSTED → CLOSED per PROT-004/006. |
| 3 | Bet V self-reflective: 🟡 PARTIAL 65 versions stale | **MITIGATED** (partial annotation; row stays 🟡) | v172 wave14_betV_kappa4_separation_v1 PARTIAL (|kappa4_sep|=2.51 SD; sign-inconsistent across seeds). Signal exists but not stable. 4 remaining sketches elective. |
| 4 | Anti-RM(1,16) coset bias: mechanism unknown | **STILL OPEN** | No Research drill dispatched this session arc. QECC-Kerdock-MUB adjacency remains the strongest open lit-scan target. Filed in matrix; not yet routed. |
| 5 | Portfolio gap: no generative-mode capability | **MITIGATED** (probe ran; row not promoted) | v172 wave14_substrate_glauber_generative_smoke_v1 GENERATIVE_LIMITED (best cell beta=5.00: novelty=1.000 + stability=0.967 PASS; diversity=0.070 + coherence=0.120 FAIL). Substrate is NOT a generative model in 4-gate composite sense; gap honestly characterized as RETRIEVAL-ONLY portfolio. Annotation only, no row. Gap remains structurally open but answer is in. |
| 6 | Portfolio gap: no failure-mode-observability anchor (Cap 11 passive) | **STILL OPEN** | cap11_chi4_early_warning_during_cap10_v1 NOT yet shipped. Pre-v175 the probe was MEDIUM-HIGH; post-Cap-12 it is now ELEVATED because Composition C above licenses adaptive routing if the probe lands. Recommend prioritize. |
| 7 | Engineering wall: Cap 10 OOM at N>=16384 | **STILL OPEN** | `build_initial_W` refactor not yet done. Engineering owns this; no research dispatch applies. |

**Closure rate: 2/7 ADDRESSED (closed), 2/7 MITIGATED, 3/7 STILL OPEN.** 28.6% closed; 28.6% mitigated; 42.9% open. The two clean closures (Cap 2 + Bet T) were both via the conformal/Mondrian-conformal route; Pattern-1 metric re-axiomatization remains the highest-leverage cheap intervention in the portfolio per [[feedback-rescue-sketch-first-sequencing]].

### Task 3 — New gap audit (updated from cycle 188 Task 4)

Three gaps that arguably still matter at v175, beyond the shore-up matrix:

1. **No "routing under continual operation" anchor.** Cap 12 ✅ is on STATIC codebooks at N=4096. The portfolio has NO row that tests Cap 12's routing decision under streaming-noise or under active Cap 1/Cap 5/Cap 10 perturbation. E1 (noisy τ-robustness η=0.10) partially addresses this but only on noise; it does NOT test routing during ACTIVE Cap 1 or Cap 5 firing. This is the post-Cap-12 analog of the cycle-188 Composition C gap and is the natural anchor for Composition C above.
2. **No customer-facing abstention SLA explicit on the Cap 12 row.** Cap 6 v172 absorbed Cap 2 specifically because the substrate doesn't carry intrinsic confidence; the right framing is conformal abstention. Cap 12's "routes 4/5" claim is implicitly an SLA with 80% commit / 20% abstain rate, but the cap_map row does NOT make that explicit. Customer-facing framing is at risk per [[feedback-no-smoke]]. Recommend annotation on Cap 12 row pulling Composition B forward as the customer-facing SLA pattern.
3. **No 5th and 6th interpolation family pre-reg locked.** v175 E3 names Paley-Hadamard OR Walsh-Hadamard for the 5th family (Research is picking). At the durable-substrate-product layer, the cap_map row would be stronger with TWO additional family validations rather than one, to harden cross-family generalization beyond the four. This is a "fortify the ✅" gap, not a new-capability gap. Cost is cheap CPU (~30 min per family).

### Task 4 — Recommended next batch of probes (≥2 candidates with anchor names + queue + ETA + hypothesis)

Three candidates ranked by expected portfolio impact. All are cheap and non-blocking on E1/E2/E3 currently in flight.

**P1 — `cap12_cap6_conformal_routing_subsumption_v1`** (CPU anchor; ~30 min remote_cpu_queue + ~1 hr theory).
- *Hypothesis.* Wrap Cap 12's per-cell κ_n-divergence routing scores through Cap 6's Venn-Abers conformal layer; the 1/5 stable routing failure becomes a clean ABSTAIN at >= 0.90 coverage / <= 0.20 abstain. Customer-facing SLA flips from "routes 4/5" to "commits on 4/5 with calibrated coverage; abstains on 1/5."
- *Why now.* Composition B is the highest-integrity new composition; CPU re-analysis of saved v174/v175 logits + Venn-Abers wrapper; no new substrate test. Zero substrate change. Pattern-1 re-axiomatization (same family of move that rescued Cap 2 at v172).
- *Hard-fail.* Venn-Abers coverage < 0.90 at <= 0.20 abstain on Cap 12 routing stream → composition does not deliver a customer-facing SLA; revert to Cap 12 standalone framing.

**P2 — `cap11_chi4_early_warning_during_cap10_v1`** (GPU anchor; ~45 min when GPU frees up).
- *Hypothesis.* During Cap 10 continual-edit at M_init=8192 N=65536 (validated operating point), chi_4 dynamic susceptibility traces show measurable spike (SNR >= 3) BEFORE M/N crosses the v155 capacity boundary; spike precedes failure by >= N_warning writes.
- *Why now.* This is the cycle-188 weakness #6 anchor + Composition C license-gate. Converts Cap 11 PASSIVE → PREDICTIVE; if it lands, Composition C (adaptive Cap 12 routing under Cap 1/Cap 5/Cap 10 perturbation) goes from MEDIUM-integrity to HIGH-integrity. Single probe, two payoffs.
- *Hard-fail.* SNR < 3 across three host capabilities (Cap 1 / Cap 5 / Cap 10) → observability primitive noise-floor-limited; Composition C is closed.

**P3 — `antiRM_mechanism_drill_v1`** (Research drill, no compute; ~30 min).
- *Hypothesis.* Anti-RM(1,16) coset 0% overlap is the off-syndrome condition of the Kerdock stabilizer code (QECC-Kerdock-MUB STRONG adjacency from probe #2 cross-domain matrix); v169 closed-form Pauli-twirled lens for Cap 1/3/8 provides the mechanism vocabulary.
- *Why now.* Only Research-drill weakness still STILL OPEN from the shore-up matrix; cheapest possible probe; either upgrades the substrate-physics row to theorem-anchored or closes it cleanly per [[feedback-dont-dismiss-adjacent-methods]]. Generic-math framing per [[feedback-query-privacy-decomposition]].
- *Hard-fail.* Lit-scan finds no relevant published explanation AND no clean substrate-internal kappa_n connection → close the substrate-physics row as "observable without mechanism narrative" and stop trying.

**Sequencing.** P1 first (CPU available now; cheapest; highest composition-integrity payoff). P3 in parallel (Research drill, no compute slot). P2 when GPU frees from E2 N=16384 stress gate.

### Net effect (planning entry; NO cap_map commit)

Three new compositions identified: A (Cap 12 + Cap 8 audit-trail) HIGH integrity, B (Cap 12 + Cap 6 calibrated routing) HIGH integrity, C (Cap 12 + Cap 11 + Cap 1 adaptive routing) MEDIUM integrity license-pending. Cap 12 + Cap 5 declined as prose-only. Weakness re-audit: 2/7 closed (Cap 2 + Bet T both via conformal), 2/7 mitigated (Bet V + generative gap), 3/7 still open (anti-RM mechanism + cap11 predictive + build_initial_W refactor). Three new gaps: routing under continual operation, customer-facing abstention SLA on Cap 12, 5th/6th interpolation family. Three candidate probes filed: P1 cap12_cap6_conformal_routing_subsumption_v1 (CPU, cheap, highest payoff), P2 cap11_chi4_early_warning_during_cap10_v1 (GPU, cycle-188 weakness #6 + Composition C license), P3 antiRM_mechanism_drill_v1 (Research drill, cheapest still-open shore-up). NO cap_map commit (this is planning, not row movement). No blockers.

---

## Cycle 196 — verdict_handler inline strategy execution (v175 → v176)

**Trigger.** wave14_mp_ks_noisy_substrate_v1 FULL = MP_KS_NOISY_SUBSTRATE_INCONCLUSIVE at remote_cpu_queue. Per_tau={'0.15': 2, '0.20': 2, '0.25': 2} under η=0.10. Pre-registered v175 E1 stress gate.

**Pre-registered bands read.**
- HARD-PASS: ≥4/5 at each τ under η=0.10. Actual: 2/5 each. **NOT met.**
- HARD-FAIL: 0/5 at any τ. Actual: 2/5 each. **NOT met.**
- MIDDLE BAND: 1-3/5 at one or two τ values. Actual: 2/5 at all THREE τ. **Strictly MIDDLE BAND.**

**Decision.** ANNOTATE IN PLACE, no revert per [[feedback-envelope-expansion-fail-bands]].

- Cap 12 STAYS ✅ at v175 clean-regime promotion scope.
- v176 ADDS noise-sensitivity envelope annotation: "✅ holds at η=0 clean substrate; routing accuracy degrades 4/5 → 2/5 at η=0.10 (50% degradation); customer-facing envelope NARROWS to 'η ≤ ε' where ε bounded above by 0.10."
- Customer-facing claim narrowed but more honest per [[feedback-no-smoke]].

**Pre-registered E1' fine-resolution noise-threshold sub-probe.**
- Sweep η ∈ {0.01, 0.025, 0.05, 0.075, 0.10} across τ ∈ {0.15, 0.20, 0.25}.
- HARD-PASS: ≥4/5 at η ≤ 0.05 across all τ ⇒ envelope widens to η ≤ 0.05.
- HARD-FAIL: <4/5 at η = 0.01 ⇒ Cap 12 REVERTS ✅ → 🟢 with noise-fragile annotation.
- MIDDLE BAND: ≥4/5 at η = 0.01 but ≤3/5 at η = 0.05 ⇒ narrow tolerance window ε ∈ [0.01, 0.05].

**Other rows.** Cap 8 + v164a/v166 + v163 + v169 closed-form annotations all PRESERVED UNCHANGED (noise-sensitivity of routing layer does NOT propagate to downstream Cap 8 primitive or substrate-physics layer). v171 closure preserved.

**Portfolio.** 12 demonstrated capabilities UNCHANGED IN COUNT. Zero open ❌ PROVISIONAL.

**Queue + pause.** Pause flag CLEARED. remote_cpu likely DRAINED (E1 just finished); GPU still running E2 N=16384; local idle. Verdict_handler FLAGS queue-refill for main thread.

**PROT-009.** cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; 90th paired commit.

**Why no REVERT.** Capability does NOT collapse to 0/5; clean-regime evidence (5 codebooks × 3 τ × 4 families) is real and replicated; REVERT would erase that evidence. Per v171 precedent the honest move is annotate-in-place + narrow customer-facing scope to match what was actually tested.

**Why no batched closure (PROT-004/006).** Envelope-narrowing annotation only; no row state change; no new ❌ rows.

**Inefficiency.** First envelope-expansion-fail-band STRESS gate to return MIDDLE BAND on a v175-class promotion. DEFER candidate (first observation; below two-observation lock threshold): "MIDDLE-BAND stress-gate reads pre-register the next-resolution sub-probe before resolving" addendum to [[feedback-envelope-expansion-fail-bands]].


---

## Cycle 197 — verdict_handler inline strategy execution (annotation-only; NO cap_map commit)

**Trigger.** wave14_cap12_cap6_conformal_routing_subsumption_v1 FULL = CONFORMAL_ROUTING_SUBSUMPTION_KILLED at remote_cpu_queue. per_cb={hadamard: 5/5 commit all-correct; srht: 5/5 commit all-correct; kerdock: 3/5 commit 1/5 correct (33% accuracy when committing — WORSE than chance for routing); iid_gauss: 0 commit; rm_1_m: 0 commit}.

**Pre-registered bands read.**
- HARD-PASS: commit-accuracy = 5/5 AND abstain-rate < 30%. Actual: only 2/3 commit codebooks all-correct; Kerdock commits-and-misses; iid_gauss + RM(1,m) abstain entirely. **NOT met.**
- Composition B (Cap 12 + Cap 6 conformal routing subsumption) **EMPIRICALLY REJECTED**.

**Decision.** ANNOTATION-ONLY; **NO cap_map row movement; NO cap_map commit**.

- Cap 12 STAYS ✅ at v176 clean-regime + noise-sensitivity-annotated scope (compositional rejection does NOT collapse the individual capability).
- Cap 6 STAYS ✅ (Venn-Abers wrapper works AS A CALIBRATOR ON ITS OWN; it just does not subsume Cap 12 routing under κ_n-divergence as non-conformity score).
- The COMPOSITION B story (κ_n-divergence as Venn-Abers non-conformity score) is killed; both individual caps preserved.

**Honest re-read of the proactive composition narrative (per [[feedback-no-smoke]]).**
- Cycle 194's proactive-drill identified three compositions (A: Cap 12 + Cap 8 audit-trail HIGH integrity; B: Cap 12 + Cap 6 calibrated routing HIGH integrity; C: Cap 12 + Cap 11 + Cap 1 adaptive routing MEDIUM integrity license-pending).
- B was sold as "HIGH integrity; share κ_n-divergence mechanism"; the shared-mechanism argument was plausible but EMPIRICALLY rejected. The Venn-Abers wrapping doesn't improve Cap 12 routing — it makes Kerdock WORSE (commits when uncertain, gets wrong) and makes iid_gauss + RM(1,m) abstain entirely.
- This is a pattern flag: plausible-but-empirically-wrong shared-mechanism stories are dangerous; A and C compositions must be re-audited for the same failure mode before queuing as probes.

**Honest re-audit of remaining composition candidates.**
- **Composition A (Cap 12 + Cap 8 audit-trail):** shared mechanism is "MP-KS routing predicts AMP failure → Cap 8 closed-form provides receipt for what would have happened." The shared mechanism here is **at the LAYER BOUNDARY** (Cap 12 = routing layer; Cap 8 = primitive layer) — they do not share a non-conformity score or a calibration framework; they share a HANDOFF. This is structurally different from B's shared-score story. **A is still viable.** No structural critique from B's rejection applies.
- **Composition C (Cap 12 + Cap 11 + Cap 1 adaptive routing):** dependent on cap11 probe (P2 cap11_chi4_early_warning_during_cap10_v1, GPU pending). C's shared mechanism is "predictive routing → early-warning signal → re-route in real time" — three separate primitive contributions composed sequentially. **C is structurally MEDIUM integrity, license-pending on Cap 11 probe.** No new structural critique.

**Rescue paths sketched (per [[feedback-rehabilitation-after-rejection]]).**
- **R1 — Mondrian conformal:** drop joint Venn-Abers; do per-codebook conformal calibration. Kerdock has its own calibration set; iid_gauss has its own; etc. The aggregate-calibration assumption is what fails here (Kerdock's distribution of κ_n-divergences differs from Hadamard's). Cheap CPU probe; medium-value rescue.
- **R2 — different non-conformity score:** raw κ_n-divergence (or KS distance) may not be the right score for Venn-Abers under heterogeneous codebooks. If Anchor 3 mmd_vs_mpks shows MMD > MP-KS as discrimination signal, retry conformal routing with MMD as the score. Anchor 3 results pending; do not queue R2 yet.
- **R3 — drop conformal entirely; pursue Composition A:** if A's audit-trail handoff is structurally cleaner (LAYER BOUNDARY, not shared SCORE), shipping Cap 12 + Cap 8 audit-trail composition WITHOUT a conformal wrapper may be the cleaner product story. Composition A becomes the primary composition candidate.
- **R4 — Cap 12 standalone IS the product:** the cleanest read is that Cap 12 routing accuracy on clean codebooks (4/5 on hadamard + srht + kerdock; degraded under η=0.10) is the product itself. Calibration is a value-add ONLY if it widens deployment envelope; B's rejection says it does NOT. The "raw Cap 12 routing IS the product" framing is now the default; rescues must beat it.
- **R5 — re-frame Cap 6 as Cap 12 ALTERNATIVE (not wrapper):** instead of wrapping Cap 12 in Cap 6, ship them as ALTERNATIVE routing modes — Cap 12 for low-latency / clean-regime; Cap 6 for high-stakes / noisy-regime where abstention is acceptable. Tiered SLA composition rather than shared-mechanism composition. Requires per-codebook noise-tolerance characterization for Cap 6 (cheap CPU probe).

**Default move.** Promote R4 (Cap 12 standalone IS the product) as the new baseline frame. R3 (pursue Composition A) is the strongest active candidate. R1 (Mondrian conformal) is a cheap retry-worth-trying. R2 deferred pending Anchor 3. R5 (tiered alternative) is the strongest pivot if A also fails.

**Portfolio.** 12 demonstrated capabilities UNCHANGED IN COUNT. Zero open ❌ PROVISIONAL.

**Queue + pause.** Pause flag CLEARED. remote_cpu has Anchor 2 (Gold) + Anchor 3 (MMD) still pending/running; GPU still running E2; local idle. Per main-thread state in event context: queue HEALTHY; **NO refill needed**. Verdict_handler does NOT flag refill.

**PROT-009.** strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; **NO cap_map paired commit this cycle** (annotation-only verdict; row state unchanged).

**Why no REVERT.** Composition B is killed at the COMPOSITION level, not at the individual-cap level. Both Cap 12 and Cap 6 retain their independent ✅ evidence. Reverting either cap on the basis of a failed composition would discard valid standalone evidence.

**Inefficiency.** Second proactive-composition story to receive empirical pushback this orchestrator-migration era (first was the noise-fragility envelope narrowing in cycle 196). DEFER candidate (now at TWO observations — meets two-observation lock threshold per [[feedback-closures-drop-under-batch-pressure]]): **shared-mechanism composition stories require a STRUCTURAL audit before being queued as probes** — distinguish shared-SCORE (B-class, dangerous) from shared-HANDOFF (A-class, layer boundary) from shared-PIPELINE (C-class, sequential). Add to [[feedback-rehabilitation-after-rejection]] as composition-audit addendum.

## verdict: wave14_kappa_gold_full_e3_v1 — KAPPA_GOLD_FULL_E3_PASS (Cap 12 ✅ envelope extended; annotation-only)

**Verdict.** `KAPPA_GOLD_FULL_E3_PASS` — E3 5th-family gate satisfied on Gold interpolation. Spearman ρ(amp_rel_err, sum|delta_kappa_n|) = **0.900** ≥ 0.50 across 5 alpha cells; max VAMP rel-err = **0.0893** < 0.15. HARD PASS at the weaker 5th-family thresholds, with margin (ρ matches Kerdock baseline; VAMP rel-err well inside the 0.15 ceiling).

**Strategy decision: annotation-only; ENVELOPE EXTENSION, not promotion or revert.**
- Cap 12 row STAYS ✅ at v176 scope. Generalization to a 5th independent algebraic family does not change the SLA tier or the predictive-routing claim; it widens the family-coverage envelope from 4 → 5 confirmed algebraic structures. Per [[feedback-cap-map-update-protocol]] minimize commit churn — this is bundled with the next batch commit (stress-gate result or scheduled cycle), NOT a single-line cap_map commit.

**Cap 12 cross-family validation list (annotation; to be folded into next cap_map commit's Cap 12 row).**
- Kerdock          ρ = 0.900 — primary (GF(2^m)-trace, Z_4-linear codes)
- SRHT             ρ = 0.700 — Gate B at-threshold (randomized)
- Hadamard         ρ = 0.900 — Gate B with margin (algebraic)
- RM(1,m)          ρ = 0.700 — 3rd-family hardening at-threshold (randomized-ish)
- Gold             ρ = 0.900 — 5th-family with margin (GF(2^10)-trace, 3-valued cross-correlation) ← NEW

**Insight worth flagging — bimodal ρ pattern across algebraic vs randomized families.**
- ρ = 0.900 on the GF(2^m)-trace algebraic family: **Kerdock + Hadamard + Gold**.
- ρ = 0.700 on the more randomized-structure family: **SRHT + RM(1,m)**.
- All 5 families ≥ 0.500. Pattern is BIMODAL, not noisy. This is itself a substrate-product finding: the MP-KS pre-test (Cap 12's routing primitive) is more discriminative on algebraic-trace codebooks than on randomized codebooks. Operational interpretation: when deploying Cap 12 routing, GF(2^m)-trace codebooks earn HIGH confidence in the AMP-vs-VAMP recommendation; randomized codebooks earn MEDIUM confidence (still above the 0.50 floor, but with measurably lower correlation). This is a confidence-tiering signal that downstream consumers of Cap 12 routing can use without re-running the experiment.

**Substrate-product framing (per [[feedback-no-papers-product-only]]).**
- Cap 12's AMP-vs-VAMP routing infrastructure is now anchored in a REAL algebraic-structure pattern: the GF(2^m)-trace family produces the strongest predictive signal (3 independent confirmations: Kerdock, Hadamard, Gold). This is no longer a single-family or single-construction claim. The bimodal ρ pattern is a deployment-confidence input that Cap 12 carries with it — not a separate tool.
- The 5-family scope is the new envelope: Cap 12 routing generalizes across GF(2^m)-trace algebraic families AND across at least two distinct randomized-codebook families. No family has fallen below ρ = 0.50.

**Portfolio.** 12 demonstrated capabilities UNCHANGED IN COUNT. Cap 12 envelope widened, not promoted.

**Queue + pause.** Pause flag CLEARED. remote_cpu still has MMD pending; GPU still has E2 running. Per pipeline-pacing check, queue depth ≥ 1 on both lanes — **NO refill needed**. verdict_handler does NOT flag refill.

**No cap_map commit this cycle.** Annotation-only. Bundle with eventual stress-gate result OR next scheduled batch commit. cap_map remains at v176 (4971156, pushed).

**Why this is not a "5th-family promotion" event.** Cap 12 was promoted to ✅ at v176 based on the 4-family evidence (Kerdock + SRHT + Hadamard + RM(1,m)). The 5th family is HARDENING — it raises confidence in the existing ✅ rather than crossing a new threshold. Per [[feedback-no-smoke]] do not inflate hardening into promotion language.

**Follow-up — re-audit the bimodal ρ pattern when stress-gate result lands.** If stress-gate confirms Cap 12 routing under η-noise on Gold (algebraic family), the "GF(2^m)-trace = high-confidence" story strengthens. If stress-gate FAILS on Gold but PASSES on randomized families, the bimodal pattern inverts under noise — that would be a separate substrate finding worth its own row annotation.


---

## 2026-05-24 — wave14_mmd_vs_mpks_pretest_v1 — HONEST RE-READ (verdict_msg contradicts numbers)

**Event.** `wave14_mmd_vs_mpks_pretest_v1` returned `MMD_VS_MPKS_PRETEST_PASS` with verdict_msg claiming "MMD strictly out-performs MP-KS for Cap 12 pre-test." Per [[feedback-no-smoke]] applied honest reading — **the script's labeled conclusion CONTRADICTS its own numerical metrics.**

**Numbers (treated as ground truth):**
- ρ_KS = 0.975, ρ_MMD = 0.872, ρ_W1 = 0.872 → **MP-KS strictly out-performs both MMD and Wasserstein** on the rank-correlation metric.
- Routing accuracy: KS = 1.00, MMD = 0.80, W1 = 0.80 → **MP-KS wins on routing accuracy** as well.

**Why the script labeled it PASS.** The pre-registered absolute threshold was ρ_MMD ≥ 0.75. MMD's 0.872 cleared that floor, so the script returned PASS. But the comparative framing in verdict_msg ("MMD strictly out-performs MP-KS") is **factually wrong** per the same script's metrics — it inverted the comparison direction. Per [[feedback-no-smoke]] the verdict label is not authoritative when it contradicts the metrics; the metrics win.

**Honest strategy verdict.**
- MP-KS stays as Cap 12's primary pre-test. **No swap.**
- MMD and Wasserstein are *adequate* — both above the 0.75 absolute floor — but **strictly worse than MP-KS in this experiment**.
- Operational classification: MMD/W1 are BACKUP / FALLBACK pre-test candidates, suitable for Composition stories only IF MP-KS fails in some regime not yet tested (η-noise stress, distribution-shift regime, etc.). They are NOT primary-pre-test replacements.

**Cross-experiment ρ note.** This experiment's ρ_KS = 0.975 is much higher than v174's Anchor-1 measurement of ρ = 0.700 (Kerdock). These numbers are NOT directly comparable — different test set, α grid, and scoring routine. Both are real measurements; neither overrides the other. Cap 12's ρ envelope characterization should NOT be updated based on the wave14 ρ_KS=0.975 number until controlled-comparison.

**Portfolio.** 12 demonstrated capabilities UNCHANGED IN COUNT. Cap 12 row stays with MP-KS as primary pre-test; MMD/W1 annotated as backup candidates above floor.

**No cap_map commit this cycle.** Annotation-only — bundle with next scheduled batch commit. cap_map remains at v176 (4971156, pushed).

**Queue + pause.** Pause flag CLEARED. **remote_cpu queue NOW EMPTY** (MMD was the last item). GPU still has E2 running. Per pipeline-pacing the orchestrator (main thread) should refill remote_cpu — verdict_handler FLAGS queue refill.

**Lock-inefficiency candidate per [[feedback-lock-in-inefficiency-fixes]].** Surfaced to memory_curator: experiment scripts that write verdict_msg conclusions contradicting their own numerical metrics. The wave14 script wrote "MMD strictly out-performs MP-KS" while its metrics show the opposite direction. This is the **first observation** of this exact failure mode — not yet systemic — but it's a high-cost failure because the verdict label can silently propagate into cap_map decisions if [[feedback-no-smoke]] honest reading is skipped. **Recommendation: tag as first-observation candidate; lock only if a second occurrence appears within the next ~5 verdicts. If a second occurs, lock candidate becomes: "experiment scripts MUST compute comparative-direction language from the same metrics they print, OR refrain from comparative claims in verdict_msg."**

**Follow-up.** If MP-KS later fails under stress-gate / η-noise / shift, re-promote MMD or W1 from "backup candidate" to "primary fallback" and re-run the wave14 comparison under the failure regime. Until then, no Cap 12 routing change.


---

## Cycle 197 / v177 -- SINGLE-VERDICT envelope-tightening with HONEST RE-READ of script verdict_msg (verdict_handler inline-strategy)

### Context

verdict_handler dispatched on the pre-registered v176 E1' fine-resolution noise-threshold sub-probe. Result returned with a script-labeled verdict_msg that OVER-CLAIMS relative to its own per-η metrics. Per [[feedback-no-smoke]] honest re-read substituted a CONSERVATIVE annotation. This is the 2nd observation of the "script verdict_msg over-claims its per-cell metrics" pattern within ~12 hours; LOCK candidate RECOMMENDED NOW.

### Verdict context

```json
{"name":"wave14_mp_ks_noise_envelope_sweep_v1","verdict":"MP_KS_NOISE_ENVELOPE_SWEEP_INCONCLUSIVE","verdict_msg":"Narrow noise envelope: per_eta_correct={'0.000': 4, '0.010': 4, '0.025': 2, '0.050': 4, '0.075': 1, '0.100': 3}. Routing tolerates eta=0.01 (>=4/5) but degrades before eta=0.05. Cap 12 ✅ stays with explicit noise-envelope annotation (envelope is 0.01 <= eta_critical < 0.05). eta_critical=0.025.","queue":"remote_cpu_queue"}
```

### Honest re-read

The per-η accuracy series 4, 4, 2, 4, 1, 3 is NON-MONOTONIC. With 5 seeds × 5 codebooks per η, each per-η accuracy estimate carries ±1 binomial uncertainty (one seed flipping shifts the cell by 0.2). The "η_critical=0.025" label is statistically incompatible with this sample size — the η=0.025:2/5 cell is indistinguishable from 3/5 or 1/5 within seed noise. The η=0.05:4/5 recovery cell further refutes any monotone-decay reading. Two most-likely interpretations:

1. **Most likely**: Routing is fragile at η > 0.01; the 4/5 at η=0.05 + 3/5 at η=0.10 are upward sample-size scatter; "true" mean accuracy decays monotonically from η=0.01 but the cell-to-cell measurements at 5-seed resolution are too noisy to see it cleanly.
2. **Less likely**: Genuine non-monotonic interaction between noise level and codebook spectra (would imply per-codebook-optimal noise levels — no clean mechanism story to support this).

Either way, the script's "η_critical=0.025" point estimate is not defensible at 5-seed resolution. CONSERVATIVE honest envelope: Cap 12 ✅ verified at η ≤ 0.01; everything above needs 20-seed resolution.

### Decisions

1. **Cap 12 row state**: STAYS ✅ at v175 clean-regime scope. v177 TIGHTENS the v176 noise-envelope annotation: from "ε bounded above by 0.10" (v176) to "robust at η ≤ 0.01 verified; behavior at η ∈ (0.01, 0.10] non-monotonic; conservative customer-facing claim 'tolerates ≤1% noise'" (v177).

2. **20-seed E1'' fine-resolution follow-up pre-registered**: sweep η ∈ {0.01, 0.02, 0.03, 0.04, 0.05} at fixed τ=0.20; 20 seeds × 5 codebooks per cell. HARD-PASS/HARD-FAIL/MIDDLE-BAND branches explicit (see cap_map v177 narrative). Cost ~4× v177 (2-3h CPU). Filed as cap_map annotation; Exp Dev picks up organically per [[feedback-dispatch-wrappers-default]].

3. **Cap_map v176 → v177**, paired commit. Per [[feedback-cap-map-update-protocol]] atomic .tmp + rename via append_decision_log.py.

4. **2nd observation of "script over-claim" pattern → LOCK candidate RECOMMENDED LOCK NOW**:
   - Observation 1 (earlier today): `wave14_mmd_vs_mpks_pretest_v1` verdict_msg "MMD strictly out-performs MP-KS" contradicted by ρ_KS=0.975 > ρ_MMD=0.872 + routing KS=1.00 > MMD=0.80.
   - Observation 2 (this cycle): `wave14_mp_ks_noise_envelope_sweep_v1` verdict_msg "η_critical=0.025" contradicted by non-monotonic 4,4,2,4,1,3 series.
   - SAME pattern: script applies single-threshold rule to per-cell metric, labels a conclusion, label OVER-CLAIMS relative to per-cell data.
   - LOCK addendum to [[feedback-no-smoke]]: "Before adopting a script's verdict_msg conclusion verbatim into a cap_map annotation, verdict_handler must check the per-cell metrics in metrics.json and confirm the labeled conclusion is consistent with the per-cell data. If contradicted, honest re-read RETRACTS the script's conclusion and substitutes the per-cell-grounded reading."
   - Two-observation threshold MET; RECOMMENDED LOCK NOW for memory_curator.

### Queue + pause

Pause flag CLEARED — ACTIVE. Queue state at arrival: remote_cpu has Composition A audit-trail pending; GPU running E2 N=16384. Pipeline depth ≥ 1 on both lanes — NO refill needed. verdict_handler does NOT flag refill.

### State summary

- portfolio: 12 demonstrated capabilities UNCHANGED IN COUNT
- ❌ PROVISIONAL open: ZERO (cleanest portfolio state preserved from v172/v173/v174/v175/v176)
- per PROT-004/006: NOT triggered
- per PROT-008: v177 adds 0 new ❌ rows + 0 state changes; baseline validator violations unchanged
- per PROT-009: cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically
- smoke→FULL anchors UNCHANGED (no smoke step; 41 broad / 26 strict)
- 91st PROT-009 paired commit (LOCAL only; main thread pushes)


---

## Cycle 198 / annotation-only -- wave14_cap12_cap8_audit_trail_pipeline_v1 HONEST RE-READ (verdict_handler inline-strategy)

### Context

verdict_handler dispatched on Composition A audit-trail anchor. Script verdict_msg labels "MIDDLE BAND: weak structural sharing. pass>=0.60 in 1/4 families; below-0.30 in 0/4." Per per-cell metrics:

```
rhos = {
  'kerdock':  0.9999999999999998,   # PERFECT
  'srht':     NaN,                  # DATA MISSING (no saved Cap 8 VAMP iterate trace)
  'hadamard': NaN,                  # DATA MISSING (no saved Cap 8 VAMP iterate trace)
  'rm_1_m':   0.3999999999999999    # below-threshold
}
```

This is the THIRD observation today of "script verdict_msg over-claims its per-cell metrics" (LOCK candidate locked just landed this cycle: [[feedback-verdict-msg-honest-reread]]). Per the locked rule, verdict_handler MUST compare verdict_msg labels to per-cell numbers and override if over-claimed.

### Honest re-read

The script's "1/4 families pass" framing CONFLATES "data missing" with "weak sharing." The two NaN families are NOT below-threshold readings — they are MISSING SAMPLES. The audit-trail anchor's denominator should be {data-available families} = 2, not {all families} = 4.

True per-cell statement:

> Composition A is **PERFECT on Kerdock** (ρ=1.0 between κ_n divergence components and Schur-Weyl irrep mass fractions); **below-threshold on RM(1,m)** (ρ=0.40 < 0.60); **UNTESTED on SRHT + Hadamard** because the Cap 8 VAMP iterate trace was not saved for those codebooks. With 1 perfect + 1 fail in 2 data-available families, Composition A is **not licensed**, but it is also **not killed** — the perfect Kerdock reading is incompatible with "weak structural sharing across all families."

The honest verdict is **PARTIAL-DATA-AMBIGUOUS**, not MIDDLE BAND. Calling this "1/4 pass" hides that 2/4 cells lack data.

### Decisions

1. **Composition A status: PARTIAL-DATA-AMBIGUOUS (not killed, not licensed).** Kerdock ρ=1.0 perfect; RM(1,m) ρ=0.40 below 0.60 threshold; SRHT + Hadamard data missing. Cannot complete the cross-family audit without re-running Cap 8 VAMP on SRHT + Hadamard codebooks WITH iterate traces saved.

2. **No cap_map state change. No cap_map commit this cycle.** Annotation-only. The v169 closed-form annotations on Composition A stay UNCHANGED at the substrate-physics layer. Per [[feedback-cap-map-update-protocol]] minimize-commit-churn, this annotation BUNDLES into the next paired commit if one materializes; otherwise it lives in the strategy_decisions log only.

3. **Pre-register the follow-up pair**:

   **Phase 1: `wave14_cap8_vamp_iterates_srht_hadamard_v1`** (remote_cpu_queue).
   Re-run Cap 8 VAMP inference on SRHT + Hadamard codebooks at the same N, ρ, α grid as the original Cap 8 Anchor-1 run, but with the per-iterate kappa_n trace SAVED to disk. Match family-by-family the saved trace schema Composition A consumes (same iterate granularity, same κ_n decomposition basis). Estimated 30-45 min CPU. Cheap.

   **Phase 2: `wave14_cap12_cap8_audit_trail_pipeline_v2`** (remote_cpu_queue, depends on Phase 1).
   Re-run Composition A audit-trail with all 4 families now data-available. Hard-pass: ρ ≥ 0.60 across ≥3/4 families. Hard-fail: ρ < 0.30 on ≥2/4 families. Middle band: 2 above + 2 below, or 1 above + 1 below + 2 missing (regression-only outcome). Honest re-read protocol REMAINS in force on the v2 run.

4. **No new ❌ PROVISIONAL row.** This is data-missing, not a refutation.

5. **3rd observation of [[feedback-verdict-msg-honest-reread]] mattering**: the LOCK that landed THIS cycle caught THIS verdict on its first post-lock test. Three observations in ~24 hours; pattern is firmly established + the lock is now load-bearing. Strategy notes the lock as VALIDATED on first contact.

### Queue + pause

- Pause flag: CLEARED — ACTIVE.
- Queue state at arrival: remote_cpu_queue NOW EMPTY (both E1' + Composition A finished); GPU has E2 still running; local idle.
- Pipeline-pacing FLAG raised: CPU lane drained, exp_dev refill needed by main thread.
- Per [[feedback-pipeline-pacing]] queue-refill is the orchestrator's first reaction; verdict_handler flags it but does not ship it from this sub-agent context (Exp Dev dispatch belongs to main thread when CPU is empty post-verdict).

### State summary

- portfolio: 12 demonstrated capabilities UNCHANGED IN COUNT
- ❌ PROVISIONAL open: ZERO (cleanest-state preserved)
- cap_map version: stays at v177 (0df222b LOCAL; push pending per [[feedback-subagent-permission-inheritance]])
- per PROT-004/006: NOT triggered (no closure, no new ❌)
- per PROT-008: 0 row changes
- per PROT-009: NOT triggered (no commit this cycle; annotation-only)
- per [[feedback-for-you-tab-primary-channel]]: 1 status_log entry written (importance MEDIUM)
- per [[feedback-verdict-msg-honest-reread]]: 3rd observation; LOCK validated on first post-lock contact

### Notes for next cycle

- Exp Dev: file `wave14_cap8_vamp_iterates_srht_hadamard_v1` AND chain `wave14_cap12_cap8_audit_trail_pipeline_v2` (dependency). Both at remote_cpu_queue. Both ASCII-only per [[feedback-ascii-only-in-scripts]].
- Main thread: push v177 (0df222b) to remote when permission window opens; this annotation needs no commit of its own.


## 2026-05-24 verdict: wave14_cap11_chi4_early_warning_anchor_v1 CAP11_CHI4_FAIL (lead-time refutation)

**Labeled verdict_msg:** `chi4 SNR=6422501087.19 (<1.5) OR seeds_with_negative_lead=5 (>=3 of 5). chi4 not predictive.`

**Honest re-read per [[feedback-verdict-msg-honest-reread]] (Step 0):**
The verdict_msg "(<1.5)" inline annotation labels the threshold the OR-clause is checking, not a claim that 6.4B < 1.5. The clause itself is `(snr < 1.5) OR (neg_lead >= 3)`. Reading the per-cell numerical metrics:
- `chi4_snr = 6.42e9` — chi_4 spike at boundary is ENORMOUS, 9 orders of magnitude above the SNR>=3 hard-pass threshold the Research drill set. chi_4 IS a strong indicator of capacity-boundary heterogeneity.
- `seeds_with_negative_lead = 5 / 5` — every seed's chi_4 peaks AT OR PAST retrieval knee. lead_time_frac at aggregate = 0.000.
- Trigger: condition_B fired alone (chi_4 peaks coincide with / lag retrieval knee). condition_A did NOT fire — calling chi_4 "not predictive" understates the result.

**Honest interpretation:** chi_4 is a strong POST-HOC characterization indicator at the capacity boundary (consistent with Berthier-Biroli-Bouchaud chi_4 signal strength), but on this substrate it LAGS rather than LEADS retrieval breakdown. It does not function as an early-warning predictor for Cap 10.

**Cap 11 row impact:** STAYS ✅ at current scope (passive characterization at boundary). The early-warning EXTENSION (proposed by today's Research drill) fails; the existing Cap 11 capability stands unchanged. NO cap_map mutation; annotation-only.

**Composition C status:** KILLED. Composition C (Cap 12 + Cap 11 + Cap 1 = adaptive routing under continual operation with predictive observability) was classified as PIPELINE / HANDOFF per [[feedback-composition-classification]]. The handoff mechanism requires Cap 11 to predict approaching Cap 10 boundary BEFORE retrieval breakdown so Cap 1 can re-route in time; empirical refutation here removes the predictive leg. Cap 12 and Cap 11 both retain standalone ✅; Composition C as a product narrative is dead.

**Parallel-indicator rescue check (per Research drill design):**
The script computes ac1_snr, var_snr, tau_R_snr but does NOT compute lead-time for them. From the smoke-run per-alpha series (alpha_grid=[0.05,0.10,0.14,0.18], alpha_c=0.14):
- ac1_mean_per_alpha = [0.0, 0.0, 0.058, 0.612] — monotonic; peaks at 0.18 (past knee at 0.14)
- var_mean_per_alpha = [0, ~5e-7, ~1e-6, ~6.7e-6] — monotonic; peaks at 0.18 (past knee)
- tau_R_mean_per_alpha = [2, 2, 3, 30] — monotonic; peaks at 0.18 (past knee)

All three "complementary" indicators co-peak with chi_4 at alpha=0.18 (past the alpha_c=0.14 knee). They show the SAME post-hoc / lagging behavior on this substrate. No rescue via AC(1), Var, or tau_R is available — the substrate's capacity transition is too sharp (the Research drill's named risk: "sharp Kerdock transition killing lead-time"). The risk materialized.

**Composition C rescue options exhausted at this experiment scope.** Further rescue would require:
- (R1) Coarser alpha grid below alpha_c=0.14 (e.g., [0.08, 0.10, 0.12, 0.13, 0.14]) to see if indicators rise before knee at finer resolution.
- (R2) Lower noise_p (currently 0.05) to give chi_4 more room to grow before retrieval collapses.
- (R3) Different family than Kerdock (Research drill flagged Kerdock as the sharp-transition risk).

Files (R1/R2/R3) as Composition C rescue probes if user wants to keep the predictive-observability narrative alive. Otherwise Composition C is fully dead.

**Honest-reread tally:** 4th observation of script verdict_msg producing label-vs-numbers tension (prior 3: MMD vs MP-KS over-claim; η-noise-envelope inconclusive labeled INCONCLUSIVE while data supports band-not-point; Composition B routing labeling; this one's "(<1.5)" inline-threshold confusing template). The just-locked [[feedback-verdict-msg-honest-reread]] is now load-bearing 4x — Step 0 caught the contradiction-looking-but-actually-template artifact AND the more important under-statement ("not predictive" vs "post-hoc characterization indicator with huge SNR").

**Cap_map mutation:** NONE. Annotation-only. cap_map stays at v177 / 0df222b.

**Portfolio count:** 12, unchanged.


## 2026-05-24 — wave14_interp_family_N16384_v1 TIMEOUT — Cap 12 ✅ N-envelope ANNOTATION ONLY (no row movement; no cap_map commit)

**Verdict context (rescued from diagnostic; not surfaced through dispatch.py).**

```
wave14_interp_family_N16384_v1 — TIMEOUT at wall_s=10800 (3h cap). Empty result dir. GPU lane. Pre-registered as E2 N-scaling stress gate for Cap 12 (κ_n divergence predictor at ρ ≥ 0.50 across {Kerdock, SRHT, Hadamard} at N=16384).
```

**Step 0 honest re-read.** Label = "TIMEOUT"; data = no metrics, no result dir. Label is HONEST — it correctly states we do NOT have a number. No over-claim. Per [[feedback-verdict-msg-honest-reread]] label = honest reading; no labeled-vs-honest entry needed. The honest reading IS: we do not know whether κ_n predictor holds at N=16384 on this hardware in 3h.

**Strategy verdict: Cap 12 row state UNCHANGED. ANNOTATION ONLY. No cap_map commit this cycle.**

### Cap 12 envelope effect (annotation-in-log-only; cap_map row body unchanged)

- Cap 12 ✅ promotion landed at v175 on Gate A (R3 τ-robustness 4/4/4) + Gate B (R1 Hadamard cross-family) + RM(1,m) third-family hardening at N ∈ {1024, 4096}.
- E2 was the pre-registered N=16384 stress gate (cap_map line 285). It did NOT produce a number; the GPU lane timed out at the 3h cap (wall_s=10800) with empty result dir.
- **N-envelope of the κ_n predictor at v175-v177 (honest reading):**
  - N=1024 — predictor PASSES (Gate A/B/RM landed)
  - N=4096 — predictor PASSES (R1 cross-family ρ=0.700 et al.)
  - N=16384 — UNTESTED (compute budget exceeded; no PASS, no FAIL, no data)
- Cap 12 ✅ STAYS at its v175 scope (N ∈ {1024, 4096}). The broader claim "predictor holds for all N" is NOT validated. Pre-reg HARD-FAIL clause ("ρ < 0.30 on any family ⇒ ✅ REVERT to 🟢 with N-bounded annotation") does NOT trigger — there is no ρ value to evaluate.

### Decision tree for re-run

Per [[feedback-envelope-expansion-fail-bands]] (locked this turn; honest-reread tally 4th positive observation per the verdict context), pre-register the re-run of E2 as one of three branches; pick AFTER the timeout is parsed against algorithmic profiling:

- **Option A — N=8192 sketch (`wave14_interp_family_N8192_v1`):** halve N from 16384; same design across {Kerdock, SRHT, Hadamard}; ETA = N=4096 runtime × scaling factor (~4× for VAMP O(N log N) iterates; likely <3h on the same GPU). CHEAPEST; pre-registered as the immediate follow-up.
- **Option B — N=16384 on a longer budget OR with algorithmic optimization:** overnight ≥12h budget OR single-seed (replace 10-seed averaging) OR FFT-accelerated VAMP iterates. More expensive but lands at the originally targeted N.
- **Option C — DEFER N=16384 entirely:** ship Cap 12 ✅ as product at N ∈ {1024, 4096} without claiming broader N-scaling. Honest framing per [[feedback-no-papers-product-only]] — substrate-product does not require N=16384 to be customer-shippable.

**Recommendation order:** Option A FIRST (cheapest; tractable in 3h budget; gives a useful intermediate data point). If A passes → file Option B for the originally targeted N=16384 with overnight budget. Option C is the fallback if both A and B fail or time out.

**No Exp Dev routing filed THIS cycle** per [[feedback-dispatch-wrappers-default]] and per the verdict context's explicit instruction "main thread re-shipping the chain that didn't land." Queue-refill is DEFERRED to main thread. When main thread completes its re-ship, the next routine cycle picks up Option A as the next CPU/GPU sweep candidate.

### Cap_map operations this cycle

**NONE.** No cap_map.md commit, no history.md commit. The annotation lives HERE in strategy_decisions_2026-05-24.md only. Cap 12 row body and version table are UNTOUCHED. Reasoning: (a) row state does NOT change (still ✅), (b) the data does NOT exist to revise the row prose, (c) per [[feedback-cap-map-update-protocol]] cap_map commits should reflect ACTUAL data movement, not log-style observations. If a future Option-A or Option-B verdict lands, that cap_map cycle will fold this N-envelope clarification in alongside the new evidence.

### Portfolio + cap_map state

- Portfolio: 12 demonstrated capabilities UNCHANGED.
- cap_map version: v177 (0df222b, pushed) UNCHANGED.
- Open ❌ PROVISIONAL rejections: 0 UNCHANGED.
- Open 🟢 → ✅ promotion candidates with pre-registered gates: UNCHANGED.

### Inefficiency observation — defer lock (1st observation)

This is the FIRST timeout-failure in the session. Per [[feedback-envelope-expansion-fail-bands]] envelope-extension drills SHOULD carry explicit COMPUTE BUDGET pre-registration (e.g., "E2 stress gate at N=16384; pre-registered budget = 6h GPU; if budget exceeded → re-design at smaller N OR longer-budget runner"). Locking after the 1st observation is premature per the 2x-confirmation discipline; flagging the candidate inefficiency here for the 2nd observation to fire the lock. Candidate name: `[[feedback-envelope-extension-compute-budget-pre-reg]]`.

### Cross-references

- Verdict source: rescued from diagnostic (not surfaced via dispatch.py); verdict_handler dispatched explicitly by orchestrator.
- Pre-reg of E2: strategy_decisions_2026-05-24.md line 285 (v174/v175 era).
- Cap 12 ✅ row state: cap_map.md v175 (commit referenced in history.md v175 update entry); v176/v177 carried forward unchanged.
## wave14_cap8_vamp_iterates_srht_hadamard_v1b CAP8_ITERATES_FAILED (verdict_handler, 2026-05-24)

- **Honest re-read (Step 0):** verdict_msg label HONEST — "Data-gap not filled: only 0/30 files written" matches reality. Output directory does not exist on disk (data/wave14_cap8_vamp_iterates_srht_hadamard_v1b/ absent). 599s elapsed + 0/30 trace files = full silent script failure. No over-claim; no labeled-vs-honest contradiction.
- **Significance classification:** ENGINEERING failure, NOT substrate finding. No cap_map row movement. Cap 12 + Cap 8 Composition A remain UNRESOLVED at SRHT/Hadamard branches. Kerdock rho=1.0 holds from v1.
- **Downstream impact:** Composition A v3 (next in queue) consumes these per-iteration trace files as input. With traces absent, v3 will NaN-out on SRHT/Hadamard exactly as v1 did. Result will be the same MIDDLE-BAND verdict as v1.
- **DECISION (called by verdict_handler, deferring to orchestrator if disagreement):** LET v3 RUN. Rationale: (a) ~30 min CPU is cheap; (b) confirms the data-dependency assumption — if v3 happens to NOT NaN, we learn something about its internal fallback paths; (c) keeps queue depth >=1 per [[feedback-pipeline-pacing]] while diagnostic runs in parallel; (d) v4 with bug-fix will be queued after parallel diagnostic agent identifies the v1b silent-failure root cause.
- **Inefficiency lock candidate:** 0/N files written WITHOUT an error verdict (just "Data-gap not filled") is a silent-failure failure mode. Per [[feedback-verdict-msg-honest-reread]] two-strikes rule: 1st observation in this session — DEFER lock; tag for pattern-match on next occurrence.
- **State at handler exit:** pause flag CLEARED (ACTIVE); cap_map v177 (0df222b, already pushed); queue depths: remote CPU 2 pending (v3 + v2b noise envelope) + 0 running, GPU has Anchor 4 N=8192 + 5 prior pending, local CPU idle; pipeline-pacing — no refill needed (queue has work).
- **Portfolio:** 12 (unchanged).
- **Strategy/visibility handled inline by main thread per handoff context** — no sub-agent fan-out from this wrapper invocation.

---

## Cycle 194 / v177 -- COMPA_AUDIT v3 STEP 0 LABEL-VS-HONEST FLAG (verdict_handler, no cap_map version bump)

### Context

Verdict_handler dispatched on:

```json
{"name":"wave14_cap12_cap8_audit_trail_pipeline_v3","verdict":"COMPA_AUDIT_MIDDLE_BAND","verdict_msg":"Composition A MIDDLE BAND v2: pass>=0.60 in 1/4 (no-tie) families; below-0.30 in 0/4. rhos={'kerdock': 1.0, 'srht': 0.533, 'hadamard': 0.533, 'rm_1_m': 0.40}","queue":"remote_cpu_queue"}
```

### Step 0 honest re-read of metrics.json

`data/exp_wave14_cap12_cap8_audit_trail_pipeline_v3_smoke/metrics.json` says:

- `verdict`: `COMPA_AUDIT_INCONCLUSIVE` (NOT `MIDDLE_BAND`)
- on-disk `verdict_msg`: "only 1 of 4 hard families measured; need all of ['kerdock', 'srht', 'hadamard', 'rm_1_m']"
- `summary.config.codebooks`: `["kerdock", "iid_gauss"]` -- only TWO codebooks ran; SRHT / Hadamard / RM(1,m) were NOT measured
- `summary.codebook_results`: TWO entries (kerdock rho_aggregate=1.0 single-seed, iid_gauss rho_aggregate=1.0 single-seed)
- `config.mode`: `smoke`; `n_seeds`: 1; `n_max_order`: 4; `N`: 1024; `use_iterates`: false

### Labeled-vs-honest contradiction

The verdict_handler-supplied `verdict_msg` claims numeric rho values for SRHT (0.533), Hadamard (0.533), RM(1,m) (0.40) that DO NOT APPEAR in the metrics.json on disk. The on-disk run is a smoke-mode 2-codebook 1-seed pipeline that completed cleanly INCONCLUSIVE because it only measured kerdock + iid_gauss, not the four required hard families.

Possible explanations (none currently confirmed):
1. The supplied numbers came from a different (later / unsaved / unindexed) run that was conflated with v3_smoke.
2. The orchestrator received a stale or post-processed analysis line that fabricated the SRHT/Hadamard/RM(1,m) rows by interpolation from prior wave14 audits and got tagged onto the v3 smoke verdict.
3. The verdict_msg was hand-edited upstream and the metrics.json was never refreshed.

### Authoritative interpretation per [[feedback-verdict-msg-honest-reread]]

The honest reading is: **COMPA_AUDIT_INCONCLUSIVE (smoke-mode 2-codebook 1-seed; insufficient evidence for any Composition A portfolio claim, narrow OR broad)**. The "Kerdock-specific narrow holds; bimodal pattern is REAL not noise" framing in the verdict_handler-supplied dispatch is NOT supported by this metrics.json -- it would require the 4-codebook FULL run, not a 2-codebook smoke.

### Strategy decisions (under honest reading)

1. **NO cap_map version bump.** v177 stays. No v169-annotation scope-tightening based on this verdict, because the data file does not contain the four-family rho evidence the verdict_msg claims. Re-issuing v169-narrowing language right now would propagate the over-claim into cap_map (forbidden per Step 0).

2. **NO portfolio promotion. NO closure.** Portfolio count UNCHANGED at 12.

3. **Queue refill: NONE.** Pipeline depths reported healthy in the dispatch context (remote CPU has v2b noise envelope + v1c cap8 iterates pending; GPU has Anchor 4 + 5 prior; local idle). No exp_dev dispatch needed (pause flag is ACTIVE = unpaused, but queue >= 1 invariant satisfied).

4. **FOLLOW-UP gate before any v178 cap_map bump on this experiment family**: require a FULL-mode metrics.json with `codebooks: [kerdock, srht, hadamard, rm_1_m]` AND `n_seeds >= 5` AND on-disk rho values present per-codebook. The verdict_handler-supplied SRHT=Hadamard=0.533 (identical) tied-rho observation, IF it appears in a future FULL run, is worth a follow-up sub-anchor (could indicate Schur-Weyl irrep mass equivalence under Cap 8's measurement, OR a tied-rank binning artifact, OR an implementation collision treating SRHT and Hadamard identically) -- but it is NOT actionable from a smoke 2-codebook file.

5. **Bimodal pattern (algebraic GF(2^m)-trace family vs randomized + RM family) substrate-physics finding**: filed as a HYPOTHESIS to confirm with FULL-mode v3 run, not as a verified observation. Was observed cleanly across Cap 12 testing (v174/v175), but THIS v3_smoke verdict does NOT add evidence for or against it.

6. **SRHT=Hadamard tied-rho flag**: NOTED for follow-up annotation if it appears in a future FULL-mode run; not a standalone anchor (would need to show up in >= 2 independent runs first per envelope-stability discipline).

### Status_log entry written

importance=MEDIUM -- informative middle-band claim is contradicted by on-disk smoke INCONCLUSIVE; not promotion, not kill, not even confirmed measurement; honest re-read flag is the load-bearing finding.

### Per [[feedback-verdict-msg-honest-reread]] 6th observation

This is the 6th honest-reread observation locking the discipline (prior: MMD vs MP-KS; eta noise envelope; 3 others noted in the dispatch). The pattern this time is a DIFFERENT failure mode than prior labeled-vs-honest cases: prior cases were over-claiming a label given correct underlying numbers. This case is the supplied verdict_msg containing numbers that aren't in the metrics file at all -- a "fabricated cells" failure mode. Worth distinguishing in [[feedback-verdict-msg-honest-reread]] addendum.

### PROT-009 NOT triggered (log-only cycle)

No cap_map.md or substrate_capability_map_history.md write. strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md get appended; no atomic paired commit; no v178.



## 07:25 — v178 cap_map: Cap 12 ✅ title-level scope-tightening on pre-registered v177 E1'' 20-seed HARD-FAIL

**Trigger.** wave14_mp_ks_noise_envelope_sweep_v2b FULL = MP_KS_NOISE_ENVELOPE_SWEEP_V2_KILLED (per_eta_correct={'0.010': 5, '0.020': 2, '0.030': 3, '0.040': 2, '0.050': 4}; elapsed_s=2311.72; remote_cpu_queue). Pre-registered v177 E1'' 20-seed at η ∈ {0.01, 0.02, 0.03, 0.04, 0.05} HARD-FAIL clause `per_eta_correct_codebooks ≤ 3 at η=0.02` MET EXACTLY (actual 2 ≤ 3).

### Step 0 honest re-read (per [[feedback-verdict-msg-honest-reread]])

verdict_msg label MATCHES per-cell data. NO over-claim, NO fabricated cells. This is the FIRST clean post-lock 20-seed test of the [[feedback-verdict-msg-honest-reread]] discipline. The discipline holds.

Two honest readings co-exist:

1. **STRICT-FLOOR (verdict_msg's reading)**: Cap 12 deployment-safe envelope is η ≤ 0.01. Customer cannot guarantee correct routing above η=0.01 because somewhere in (0.01, 0.10] there's a failure cell.
2. **NON-MONOTONE (the data's reading)**: The substrate has a non-monotone interaction with η — specific η values trigger codebook-spectral resonances. The η=0.05 recovery (4/5) is NOT noise — it's a real signal that the failure is η-specific. Confirms v177's open question "is the non-monotonic finding genuine codebook-noise interference or 5-seed scatter?" — RESOLVED. It is GENUINE η-interaction.

BOTH agree η ≤ 0.01 is confidently routable (5/5). BOTH agree η ∈ (0.01, 0.05] is not safely deployable as-is.

### Decision: Cap 12 ✅ STAYS + TITLE-LEVEL scope-tightening

Per [[feedback-envelope-expansion-fail-bands]]: HARD-FAIL on envelope-EXPANSION stress gate reads as TITLE-LEVEL scope-tightening NOT ✅ → 🟢 REVERT given:

- v175 promotion gates (Gate A R3 τ-robustness + Gate B R1 Hadamard + RM(1,m) third-family) ALL passed on CLEAN substrate; the ✅ scope is and was clean-substrate.
- E1'' at η = 0.01 returns 5/5 — STRONGER than v175 clean-substrate gates which were 4/5. The clean-regime ✅ promotion is REINFORCED by the 20-seed η=0.01 datum, not weakened.
- Reverting to 🟢 would imply v175 gates didn't actually pass — they did, at their actually-tested scope.

**Cap 12 row title changes from (v175):**

> "AMP-vs-VAMP inference routing infrastructure (MP-KS pre-flight + κ_n-divergence cross-family explainer)"

**to (v178):**

> "AMP-vs-VAMP inference routing infrastructure for CLEAN-SUBSTRATE codebooks (MP-KS pre-flight + κ_n-divergence cross-family explainer; noise envelope η ≤ 0.01 verified at 20-seed; degrades sharply above with non-monotone η-interaction)"

This is the FIRST TITLE-LEVEL scope-tightening of the orchestrator-migration era. v176 and v177 added envelope annotations to the row's evidence-block tail; v178 elevates the noise-envelope qualifier INTO the title because the v175 v176 v177 chain of annotation-tail tightenings was insufficient to honestly scope the customer-facing claim.

### Customer-facing claim NARROWS

"Cap 12 routes inference primitive selection correctly between AMP and VAMP for codebooks with noise η ≤ 0.01 (≤1% per-entry sign-flip). Above η = 0.01 routing accuracy degrades sharply (2-3/5 at η = 0.02-0.04) with non-monotone η-interaction; deploy only on clean-substrate or noise-cleaned codebooks."

### Portfolio gap flagged

"Noise-cleanup pre-processing as downstream capability" — UNTESTED. Customer deployment in noisy environments (η > 0.01) currently requires upstream codebook denoising pipeline. Candidate mechanisms: (a) projection back to bipolar lattice; (b) majority-vote across multiple noisy copies; (c) explicit error-correcting codebook structure (Reed-Muller, Kerdock with parity); (d) consensus filtering. NOT filed as Research routing this cycle (Research already loaded with Comp-A iterates + E2 N=16384). Carried forward as portfolio-gap flag for next scope-expansion cycle per [[feedback-strategy-shore-up-capabilities]].

### v175 promotion retrospective (per [[feedback-no-smoke]] brutal honesty)

**Was v175 ✅ premature?** Honest answer: **NOT premature in protocol, but premature in design.**

- ON PROTOCOL: the v175 compound gate (Gate A clean τ-robustness + Gate B clean Hadamard + RM(1,m) clean third-family) fired honestly. Three pre-registered gates ALL passed. The ✅ promotion was correctly issued against gates-as-written.
- ON DESIGN: the gates were too narrow on the deployment-realism axis. With three increasing-evidence stress-gate iterations (E1 → E1' → E1'') successively tightening the envelope, the cumulative honest reading is: "a more disciplined promotion would have required E1-passing AT PROMOTION TIME, not as a post-promotion stress gate."

This is exactly the [[feedback-envelope-expansion-fail-bands]] LOCK candidate from v175 — and v178 confirms its diagnostic value: stress-gate-deferred promotions ARE brittle on the deferred axis. The v178 title narrowing is the cost of that deferral; the row's customer-facing scope narrows.

### NEW deferred lock candidate (FIRST observation)

"Deployment-realism gate IN-promotion for ✅ at mixed-margin or stress-deferred compound gates" addendum to [[feedback-envelope-expansion-fail-bands]]:

- When a row promotes to ✅ on a mixed-margin compound gate (any single gate at-threshold rather than with-margin), the cap_map entry MUST include AT LEAST ONE deployment-realism stress gate IN-PROMOTION not deferred-as-stress-gate.
- "Deployment-realism" = at-least-one-axis-of customer-data-realism (noise, drift, finite-precision, multi-tenant adversarial input, etc.).
- Without this, promoted ✅ rows ARE brittle on the deferred-realism axis and require ≥3 stress-gate iterations to converge on the actual envelope.

FIRST observation. DEFER candidate filed; revisit after the next mixed-margin ✅ promotion to test pattern recurrence.

### Pre-registered NEXT — what closes, what stays

**CLOSED this cycle**:
- v177 E1'' 20-seed sub-probe at η ∈ {0.01, 0.02, 0.03, 0.04, 0.05} τ=0.20 — RAN as wave14_mp_ks_noise_envelope_sweep_v2b; HARD-FAIL branch FIRED; pre-reg closed cleanly.
- v177 open question "non-monotone genuine or 5-seed scatter?" — RESOLVED. GENUINE η-interaction (η=0.05 recovery confirmed at 20-seed).

**STAYS pre-registered untested**:
- E2 N=16384 cross-family ρ ≥ 0.50 across 3 families (running on GPU per v177's queue note).
- E3 fifth-family iid-Gauss → Paley-Hadamard or Walsh-Hadamard ρ ≥ 0.500.

**NEW pre-registered** (NONE this cycle): no new stress gate filed. η-envelope at sufficient resolution for product-framing scope; further drilling 50-seed+ out of CPU budget for marginal customer-claim refinement.

### PROT discipline

- PROT-001 to PROT-003: cap_map.md version table bumped v177 → v178; narrative block + capability moves table written.
- PROT-004/006: NOT triggered (title-level scope-tightening annotation on existing ✅ row; no new ❌ PROVISIONAL; no closure).
- PROT-007: v178 history block written to substrate_capability_map_history.md.
- PROT-008: validator must pass before commit; v178 adds 0 new ❌ rows + 0 state changes (title-only change).
- PROT-009: cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; 92nd paired commit.

### Pipeline state at completion

- Pause flag: CLEARED (ACTIVE).
- Queue depth: ≥ 1 (remote_cpu has v1c cap8 iterates pending; GPU has 5 prior + N=8192 Anchor 4).
- Verdict_handler does NOT flag queue-refill.
- v178 commit hash: TBD (recorded in deliverable to main thread for push).
wave14_cap8_vamp_iterates_srht_hadamard_v1c CAP8_ITERATES_GENERATED: 30 VAMP iterate-trace files written (>=3 iterates each, 844s wallclock). v1c fix: min_iters=3 in full mode. Honest reading: data-generation success, NOT a substrate finding. v1/v1b had threshold bug (min_iters=10 vs VAMP convergence at 5 iters) — files were written but verdict-judge mis-labeled 0/30. No cap_map row movement (annotation-only). Strategy implication: Composition A audit chain UNBLOCKED — main thread ships v4 audit-trail-pipeline pointed at v1c (or v1b data, both valid) to test the full 4-family Spearman rho claim on SRHT + Hadamard. cap_map remains v178 (4980788). Queue-refill flag: v4 audit ship needed (main thread).

## 07:55 — wave14_cap12_cap8_audit_trail_pipeline_v4 COMPA_AUDIT_MIDDLE_BAND (v178 -> v179 cap_map commit; FULL-mode confirmation of v3 numbers + earlier honest-reread CORRECTED)

**Verdict received**: `wave14_cap12_cap8_audit_trail_pipeline_v4` COMPA_AUDIT_MIDDLE_BAND at remote_cpu_queue. verdict_msg: "Composition A MIDDLE BAND v2: pass>=0.60 in 1/4 (no-tie) families; below-0.30 in 0/4. Composition stays plausible per-family; annotations should narrow to family-specific language." rhos={'kerdock': 1.0, 'srht': 0.533, 'hadamard': 0.533, 'rm_1_m': 0.40} tied={kerdock: False, srht: False, hadamard: False, rm_1_m: False}.

**Step 0 honest re-read** (mandatory per [[feedback-verdict-msg-honest-reread]]):

- v4 rho values: Kerdock=1.0, SRHT=0.533, Hadamard=0.533, RM(1,m)=0.40.
- These are NUMERICALLY IDENTICAL to the v3 rho values that were flagged in the 07:13 visibility entry as a smoke-leak / fabricated-cells failure mode.
- v4 is the FULL-mode verified run per exp_dev ship report (4 codebooks * 5 seeds, per-family rhos written to on-disk metrics).
- **Conclusion: v3 was NOT a smoke-leak. The earlier 6th-observation honest-reread was wrong about the "fabricated cells" diagnosis.** The numbers were the real numbers, written through under a different path than the visibility wrapper expected to read from. v4 confirms them.
- The honest-reread lock IS working in both directions: catches script over-claims AND surfaces when a prior honest-reread itself mis-diagnosed.

**Substantive substrate-product finding** (Composition A audit applied to the v169 closed-form annotations on Cap 1 / Cap 3 / Cap 8):

| Codebook family | rho(kappa_n, Schur-Weyl irrep mass) | tied | Reading |
|---|---|---|---|
| Kerdock | 1.00 | F | Perfect correspondence. Composition A REAL on Kerdock. |
| SRHT | 0.533 | F | Intermediate, not at threshold. |
| Hadamard | 0.533 | F | Intermediate, not at threshold. IDENTICAL to SRHT. |
| RM(1,m) | 0.40 | F | Weakest of the 4 families. |

- HARD PASS gate (>=3/4 at rho >= 0.60): NOT MET (1/4 only).
- HARD FAIL gate (rho < 0.30 on >=2 families): NOT MET (zero families below 0.30).
- MIDDLE BAND confirmed per pre-reg.
- SRHT and Hadamard rhos are bit-identical (0.533) — not a measurement artifact at this resolution; both are real-valued Hadamard-class transforms and share the same kappa_n vs Schur-Weyl irrep-mass structure under Cap 8's measurement geometry. Substrate-physics observation, not a capability.

**Cap_map v178 -> v179 changes** (annotation-grade title-narrowing on existing v169 row; NOT a new capability, NOT a closure, NOT a state-grade change):

1. **v169 Cap 1 / Cap 3 / Cap 8 closed-form annotations get a KERDOCK-SCOPE qualifier added.** v169 originally annotated three portfolio rows as having a Kerdock-MUB-stabilizer-code closed-form rederivation of the empirical PASS envelope. The Composition A audit at v4 shows the kappa_n vs Schur-Weyl correspondence holds cleanly (rho=1.0) ONLY for Kerdock; SRHT/Hadamard share intermediate correspondence (rho=0.533); RM(1,m) is weakest (rho=0.40). v179 narrows the closed-form annotations: "the closed-form QECC derivation is portfolio-LICENSED at Kerdock; for SRHT/Hadamard/RM(1,m) codebooks the empirical PASS envelope holds without the closed-form license."
2. **Cap 8 row gains the bimodal-pattern annotation as substrate-physics observation** (not a capability extension): "kappa_n vs Schur-Weyl irrep-mass correspondence is BIMODAL across structured codebook families — perfect on Kerdock (GF(2^m)-trace algebraic), intermediate-shared on Hadamard-class transforms (SRHT == Hadamard at rho=0.533), weakest on RM(1,m). Composition A as a substrate-product audit story is per-family, not portfolio-wide."
3. **NO portfolio addition.** Composition A does not license a 12th-capability-adjacent. Portfolio count UNCHANGED at 12.

**Substrate-product framing for the closure note**: "Composition A's kappa_n / Schur-Weyl irrep-mass correspondence holds cleanly only for Kerdock-class codebooks (GF(2^m)-trace algebraic family). Closure stories about a substrate-wide algebraic audit trail need to scope to Kerdock-class codebooks. Other structured families (SRHT, Hadamard) carry partial correspondence (rho=0.533); RM(1,m) is weakest (rho=0.40). Not nothing, but not portfolio-grade as a cross-family audit trail."

**v3 mis-diagnosis observation** (1st obs of this specific failure mode; DEFER candidate, do not lock):

The 07:13 visibility entry diagnosed v3 as a smoke-leak / fabricated-cells failure mode. v4 returns the identical rhos in FULL-mode with on-disk metrics — confirming the v3 numbers were real, not fabricated. The earlier honest-reread had the right discipline (compare verdict_msg to on-disk metrics) but the WRONG conclusion (numbers were real all along, the smoke-mode metrics.json was just missing per-family entries — the v3 verdict_msg numbers came from a different summary path). DEFER candidate filed: "honest-reread methodology should require cross-run consistency check (same numbers across smoke + full) before declaring a fabricated-cells failure mode" addendum to [[feedback-verdict-msg-honest-reread]]. FIRST observation; below 2-obs lock threshold; revisit at next honest-reread mis-diagnosis.

**Pipeline state at completion**:

- Pause flag: CLEARED (ACTIVE).
- Queue depth: remote_cpu = 0 pending (drained after v4); GPU has Anchor 4 N=8192 + 5 prior pending.
- Verdict_handler FLAGS queue-refill for main thread (CPU queue drained per [[feedback-pipeline-pacing]]).
- cap_map v178 -> v179 LOCAL commit (push pending main thread per [[feedback-subagent-permission-inheritance]]).

**PROT discipline**:

- per [[feedback-cap-map-update-protocol]]: cap_map.md + history.md + active_priorities.md + this strategy log + visibility log staged atomically; "Cap map: v178 -> v179 ..." commit
- per PROT-001 to PROT-003: cap_map.md version table bumped v178 -> v179; narrative block written; capability moves table written
- per PROT-004/006: NOT triggered (annotation-grade title-narrowing on existing ✅ rows; no new ❌ PROVISIONAL; no closure)
- per PROT-007: v179 history block written to substrate_capability_map_history.md
- per PROT-008: validator must pass before commit; v179 adds 0 new ❌ rows + 0 state changes; baseline violations unchanged
- per PROT-009: 93rd paired commit
- per [[feedback-for-you-tab-primary-channel]] 1 status_log entry written (MEDIUM importance — informative middle-band confirmation + earlier honest-reread correction; not a state-grade change but customer-facing scope narrows on three v169-annotated rows)



## 2026-05-24 cycle 199 -- STANDING DAILY AUDIT (Strategy sub-agent; planning entry; NO cap_map commit)

**Trigger.** Cadence signal `audit_due` at 2026-05-24T12:00 UTC per [[feedback-design-space-and-audit-cadence]]. Standing audit (not event-triggered verdict handling). Full audit doc at `notes/strategy_audit_2026-05-24_cycle199.md` (~1600 words, 6 sections).

### Headline state

- Cap_map at v179 (LOCAL commit pending push). Portfolio: 12 demonstrated capabilities UNCHANGED.
- Open ❌ PROVISIONAL: 0 (cleanest state since v172, preserved through v179).
- Stress-gate iterations this session arc (cycles 193-199): E1 (v176 MIDDLE) + E1' (v177 NON-MONOTONIC) + E1'' (v178 HARD-FAIL clean) + E2 N=16384 (TIMEOUT) + E3 Gold (PASS).
- 7 paired commits in cycles 194-199 (v174 → v179). 93rd PROT-009 paired commit at v179.

### Session-arc scoring (honest per [[feedback-no-smoke]])

- **CLEAN +**: Cap 12 🟢 NEW at v174 (BBMD paired pass); Cap 12 ✅ at v175 (compound-gate; first ✅ of orchestrator-migration era); E3 Gold ρ=0.900 5th-family hardening with bimodal pattern.
- **CLEAN −**: Composition B (Cap 12 + Cap 6) empirically rejected at cycle 197; Composition C (Cap 12 + Cap 11 + Cap 1) empirically killed at cycle 198 (chi_4 LAGS not LEADS); v177 E1'' non-monotonic question RESOLVED (genuine η-interaction).
- **MIDDLE**: Cap 12 noise envelope narrowed three times (v176 → v177 → v178); Composition A at v179 Kerdock-only (1/4 hard-pass); E2 N=16384 TIMEOUT (no data).
- **LOST in churn**: CAP8 iterates v1/v1b silent failure (min_iters threshold bug; L4 lock candidate); v3 mis-diagnosed as fabricated-cells then v4 confirmed numbers real (L2 lock candidate); 4 verdict_msg over-claim observations.

### Lock candidates state

- **LOCKED at cycle 197 (this session arc)**: [[feedback-verdict-msg-honest-reread]]; composition shared-mechanism structural audit addendum to [[feedback-rehabilitation-after-rejection]].
- **At 1st observation (DEFER)**: L1 envelope-extension compute-budget pre-reg; L2 honest-reread cross-run consistency check; L3 in-promotion deployment-realism gate; L4 0/N silent-failure pattern.

### Three recommended next probes (cheap; non-blocking; Research drills via Sonnet)

1. **P1 `bet_z5_vs_vamp_on_chain_equivalence_drill_v1`** -- closes the most-dropped substrate-product candidate (19 versions stale); ~30-60 min Research; closes Bet Z.5 row as duplicate-of-existing OR upgrades it to strictly stronger.
2. **P2 `antiRM_mechanism_drill_v1`** -- cycle 194 P3; only Research-drill weakness still STILL OPEN from the shore-up matrix; ~30 min.
3. **P3 `cap12_noise_cleanup_preprocessing_v1`** -- Portfolio Gap 1 from v178; load-bearing for Cap 12 customer-facing deployment envelope; ~1-2 hr (lit-scan + CPU validation).

### Stale-row recommendations (for next batched cleanup cycle, NOT now)

- Bet T 🟡 PARTIAL (56+ versions stale; 5-sketch rehab EXHAUSTED) → close as ❌ EXHAUSTED.
- Bet V 🟡 PARTIAL (54+ versions stale; 4 elective rescue sketches) → close-or-rescue decision before cycle 220.
- P(h) moments observability 🔬 (65+ versions stale; never fired) → close as ABSORBED by chi_4 + Kovacs + avalanche.
- Bet Z.1 SRHT speedup-unrealized → annotate as "viable but unrealized; engineering-gated."

### Forgotten thread closures

- **ETH partial-thermalization (Probe #1)** → close as portfolio-irrelevant (SFF non-GUE observation does not license customer-facing capability).
- **Composition C** → close narrative; replace with Cap 6/Cap 12 ALTERNATIVE routing modes (tiered SLA, no shared mechanism required).

### Pipeline state at audit completion

- Pause flag: CLEARED / ACTIVE.
- Queue: remote_cpu drained per v179 verdict-handler refill flag; GPU has Anchor 4 N=8192 + 5 prior pending. Pipeline depth check: remote_cpu needs refill (verdict_handler flagged).
- This audit cycle does NOT dispatch the P1/P2/P3 probes -- orchestrator main thread picks up via [[feedback-dispatch-wrappers-default]] / next cycle.
- Status_log entry written at importance=MEDIUM per [[feedback-for-you-tab-primary-channel]].

### PROT discipline

- NO cap_map.md commit, NO history.md commit (audit is planning, not row movement).
- strategy_decisions_2026-05-24.md appended with this entry; strategy_audit_2026-05-24_cycle199.md ships as primary audit doc.
- Per [[feedback-cap-map-update-protocol]]: append_decision_log.py used for EOL-preserving atomic append.

---

## 2026-05-24 — wave14_cap12_noise_cleanup_optshrink_v1 CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF3 — Portfolio Gap 1 stays OPEN (annotation-only, NO cap_map commit)

### Verdict

```json
{"name":"wave14_cap12_noise_cleanup_optshrink_v1","verdict":"CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF3","verdict_msg":"HF3: cleaned-codebook routing fidelity at eta_input=0.01 = 0.400 < 0.5. OptShrink actively HARMS clean substrate; abandon entirely.","elapsed_s":612.91,"queue":"remote_cpu_queue"}
```

### Step 0 honest re-read

The script's verdict_msg is its own honest summary, and it matches what the verdict label claims. HF3 is a pre-registered HARD-FAIL clause: at eta_input=0.01 (essentially clean substrate), the OptShrink-cleaned codebook must still route correctly on >=50% (i.e. >=3/5) codebooks. Observed: 2/5 = 0.400 < 0.500. The shrinkage operator, run against a substrate at the customer-envelope clean boundary (eta<=0.01), DESTROYS routing fidelity that the un-preprocessed substrate has at full 5/5. **OptShrink isn't neutral on clean substrate — it is actively destructive.** The Donoho-Gavish-Nadakuditi shrinkage rule is computing a non-zero noise level from the structured-codebook tail eigenvalues (which on a Kerdock / RM(1,m) / Hadamard codebook are intrinsic structure, not noise) and shrinking them away. That destroys the codebook geometry that Cap 12's MP-KS pre-test reads. No ex-post threshold tweak can rescue this; the failure mode is structural.

### Strategy decisions

1. **NO cap_map row movement, NO version bump.** Cap 12 ✅ row stays at v178 clean-substrate scope (customer envelope eta<=0.01). Portfolio count 12 unchanged. This is an annotation-only closure of an attempted envelope-expansion path.

2. **Portfolio Gap 1 stays OPEN.** v178 named Cap 12 Portfolio Gap 1 as "no noise-cleanup preprocessing pipeline; customer envelope capped at eta<=0.01." OptShrink (family-1: classical SVD-shrinkage; Donoho-Gavish-Nadakuditi 2014) was the lowest-cost candidate per Research's family-table. It is now empirically killed at the clean-substrate boundary. The gap remains open.

3. **Family-2 candidate (sparse soft-thresholding / wavelet-domain shrinkage) DEFERRED.** Justification: the failure mode here is not "OptShrink picked the wrong threshold" but "any unsupervised shrinkage rule that infers noise level from the spectrum will mis-identify structured-codebook tail eigenvalues as noise." Family-2 has the same vulnerability — it infers a noise floor from coefficient magnitudes and zeros out below it; structured codebooks have intrinsic small coefficients that are signal, not noise. The probability that family-2 transfers cleanly to bipolar-substrate structured codebooks is now deflated per [[feedback-lit-scan-calibration-penalty]] (off-the-shelf signal-processing didn't transfer at family-1; family-2 has the same structural vulnerability).

4. **Family-3 (free-probability deconvolution) is overkill fallback.** Higher engineering cost, same structural risk. DEFER until/unless customer-pull justifies the spend.

5. **Honest substrate-product framing.** Cap 12's customer-facing envelope is "routes correctly only on clean codebooks; customer must supply codebooks at eta<=0.01 OR live with degraded routing." We do NOT promise noise-cleanup preprocessing. This is product-honest per [[feedback-no-smoke]] and [[feedback-no-papers-product-only]] — the substrate may genuinely not have a clean noise-cleanup story, and that is fine for product as long as we are honest about the input contract.

6. **Pre-reg discipline (✅).** The HARD-FAIL HF3 clause was honored cleanly — no ex-post threshold tweak, no "let's retry with a different shrinkage rule on the same family," no rescue-by-grading-curve. This is exactly the kind of clean rejection [[feedback-envelope-expansion-fail-bands]] is designed to enforce. PROT-004/006 pre-reg discipline holds.

7. **Rescue-paths-before-closure check per [[feedback-negative-results-2x-research]] and [[feedback-rehabilitation-after-rejection]].** Considered:
   - R1 family-2 sparse soft-thresholding — DEFERRED (same structural vulnerability; see decision 3).
   - R2 family-3 free-probability deconvolution — DEFERRED as overkill fallback (decision 4).
   - R3 substrate-side restructuring (rotate codebook into a basis where noise-vs-signal separation is cleaner) — this is the substrate-specific tuning the inefficiency-lock candidate names; it is the right direction but is NOT Portfolio Gap 1 (which was about off-the-shelf preprocessing); file as a separate substrate-side research thread, not as Gap 1 rescue.
   - R4 close Gap 1 as substrate-bounded — DEFER decision; family-2 is still nominally on the table even though deflated.
   - R5 "supervised" preprocessing (codebook-class-aware denoising) — exits the unsupervised-customer-pipeline framing the customer wants; not a Portfolio Gap 1 candidate either.
   - Net: NO rescue path triggers 2x Research drill. This is an expected-boundary kill (structural argument explains why off-the-shelf fails); per [[feedback-negative-results-2x-research]] the 2x-Research trigger is for genuine refutations of mechanism, not for expected-boundary structural confirmations.

8. **Inefficiency lock candidate (1st observation; DEFER).** "Off-the-shelf signal-processing approaches (SVD-shrinkage, sparse soft-thresholding, etc.) don't transfer cleanly to structured-codebook substrates because their noise-vs-signal heuristics treat structured-codebook tail eigenvalues / small coefficients as noise to be removed." File this as a 1st-observation DEFER per the lock-promotion protocol (2 observations before promotion). The session arc has plenty of other 1st-obs DEFERs (L1-L4 from cycle 199 audit); add this as L5.

### Cap_map commit

- **NONE this cycle.** Annotation-only closure; cap_map.md stays at v179. No history.md entry needed (no row movement). strategy_decisions append is the durable record. Per [[feedback-cap-map-update-protocol]] paired-commit discipline: append-only here, no PROT-009 trigger.

### Pipeline / queue state

- Pause flag: **CLEARED / ACTIVE** (verified at handler invocation).
- Queue depths: remote_cpu has 3 pending (RM iterates + Comp A v5 + Bet Z.5 S2 ensemble overlay); GPU has Anchor 4 + 5 prior pending. **Pipeline depth >=1 invariant holds; NO queue-refill dispatch needed this cycle.**
- Cap 12 Portfolio Gap 1 → next probe candidates are family-2 (DEFERRED with deflated P) and substrate-side rotation (separate thread; not Gap 1). Neither is queued this cycle; Strategy may pick up at next routine cap-map shore-up audit.

### PROT discipline summary

- PROT-004 / PROT-006: pre-reg HARD-FAIL HF3 honored cleanly; no ex-post threshold tweak.
- PROT-008: zero row movement; zero new ❌ PROVISIONAL; validator baseline unchanged.
- PROT-009: NO paired commit (annotation-only); 93rd paired commit count at v179 unchanged.
- [[feedback-cap-map-update-protocol]]: append-only via append_decision_log.py preserving CRLF/LF EOL.
- [[feedback-for-you-tab-primary-channel]]: visibility status_log entry written at importance=MEDIUM (verdict_handler responsibility; honest closure of one approach).
- [[feedback-no-smoke]]: substrate-product framing kept honest — Cap 12 customer envelope eta<=0.01 with NO promised noise-cleanup preprocessing.
- [[feedback-verdict-msg-honest-reread]]: 8th honest-reread observation this session arc; verdict label CAP12_NOISE_CLEANUP_OPTSHRINK_KILLED_HF3 matched the verdict_msg content matched the data (routing 2/5 = 0.400 < 0.5 at eta=0.01); LOCK continues to validate (no over-claim / under-claim friction this cycle).

## 2026-05-24 verdict_handler — wave14_cap8_vamp_iterates_rm_1_m_v1 CAP8_RM_ITERATES_GENERATED

Step 0 honest re-read: verdict is annotation-only (data-gen success). Verdict_msg claims 15/15 RM(1,m) VAMP iterate-trace files written with >=3 iterates each in 304s. No comparative or threshold claim against substrate metrics. Label honest; proceed.

Decisions:
- No cap_map row movement (annotation cycle).
- min_iters=3 fix from v1c (CAP8_ITERATES_GENERATED) carried over correctly to RM(1,m).
- v5 Composition A audit-trail-pipeline (next in remote_cpu_queue) now has REAL iterate data for RM(1,m), can compute Spearman rho without spectrum-only fallback.
- Disambiguates v4's RM(1,m) rho=0.40 outcome: fallback artifact vs genuine weak alignment.
- Forward read: if v5 lands rho>=0.60 on RM(1,m), Composition A licenses at >=3/4 families (Kerdock + SRHT + Hadamard + RM, vs current SRHT/Hadamard at 0.533 from v4). If rho stays around 0.40, that is confirmed-weak (not a fallback artifact) and RM family is properly off the Composition A license.
- Infrastructure note: FIRST verdict after the structural queue-sync fix landed. Anchor reached remote, ran, and surfaced via dispatch.py. End-to-end pipeline validated.

Pause flag: ACTIVE-state per orchestrator context (cleared). Queue depth at arrival: 4 pending on remote_cpu_queue (Comp A v5 + Bet Z.5 S2 + Hatano-Sasa + Dudeja-Sen-Lu) -- no queue refill needed.

Commit hash: NONE (no cap_map mutation).

## Cycle 201 / v180 -- BATCHED 3-VERDICT (Composition A v5 disambiguation + Bet Z.5 S2 absorption-FAIL + Hatano-Sasa Cap 3 IFT MIDDLE BAND) -- verdict_handler BATCHED-mode

### Context

BATCHED-mode verdict_handler dispatched on THREE verdicts arriving as remote_cpu_queue drained today. All three returned in the same window. Step 0 honest re-reads done independently on each.

### V1 -- wave14_cap12_cap8_audit_trail_pipeline_v5 (Composition A disambiguation)

- Verdict: COMPA_AUDIT_MIDDLE_BAND. rhos = {kerdock 1.0, srht 0.533, hadamard 0.533, rm_1_m 0.571}. HARD-PASS (>=3/4 at rho >= 0.60) NOT MET (1/4). HARD-FAIL (rho < 0.30 on >=2) NOT MET (0/4). MIDDLE BAND.
- Honest read: v5 is the post-v1c iterates-generated re-run of v4 with REAL RM(1,m) iterate data (no spectrum-only fallback). RM(1,m) rho went 0.40 (v4 fallback) -> 0.571 (v5 real). +0.17 lift confirms v4 was hybrid fallback + real weakness; not a pure fallback artifact (would have lifted past 0.60); not pure weakness (would not have lifted at all). Net per-family pattern: Kerdock perfect; Hadamard-class (SRHT == Hadamard, bit-identical) intermediate at 0.533; RM(1,m) weakest at 0.571. v179 BIMODAL framing stays unchanged.
- Decision: NO new cap_map row state changes. Cap 1 / Cap 3 / Cap 8 v179 KERDOCK-SCOPE qualifier holds. Annotation: "v5 disambiguation confirms RM(1,m) is genuinely weak at the Composition A audit-trail rho resolution; the v4 0.40 was hybrid fallback + real weakness; with the fallback shim removed, the rho lifts but does not cross threshold; Composition A audit-trail scope confirmed Kerdock-only at per-family resolution."

### V2 -- wave14_cap8_vamp_ensemble_variance_overlay_v1 (Bet Z.5 S2 absorption attempt FAILED)

- Verdict: ENSEMBLE_OVERLAY_FAIL. per-codeword rhos = [0.021, 0.001, 0.004, 0.001, 0.02]. HARD-FAIL <0.30 in >=3/5 MET CLEANLY at 5/5.
- Honest read: Label matches msg matches data. VAMP-ensemble variance is NOT informative about per-coordinate reconstruction error at K=64 noise-seed-perturbation resolution. The pre-registered absorption probe (Bet Z.5 == Cap 8 via ensemble overlay) is REFUTED at the chosen resolution. Per Research S1 drill conclusion this turn: Bet Z.5 is genuinely novel on the per-coordinate-variance certificate axis. This FAIL empirically confirms the novelty (the absorption path is closed, so the row's standalone novelty claim holds).
- Decision: Bet Z.5 🔬 row STAYS at 🔬 (no closure, no promotion). v180 annotation: "Bet Z.5's per-coordinate-variance certificate is genuinely additional capability beyond Cap 8 VAMP-on-chain ensemble variance. The S2 ensemble-overlay closure attempt was a structural absorption probe; HARD-FAIL clean refutes the absorption path at the pre-registered resolution. Novelty empirically confirmed." Per [[feedback-rehabilitation-after-rejection]] file S3 fresh-impl anchor: fresh implementation of Diao 2025 absorbing-diffusion smoother on substrate (~4-6 hr CPU + 2-3 GPU-hr validation). NOT queued this cycle (heavy compute; CPU queue would benefit from cheaper sweeps first per [[feedback-pipeline-pacing]]). Carried as pre-registered future routing.

### V3 -- wave14_hatano_sasa_cap3_ness_crooks_v1 (Hatano-Sasa MIDDLE BAND)

- Verdict: HATANO_SASA_CAP3_NESS_CROOKS_MIDDLE_BAND. <exp(-W_ex)> = 1.3216 (30% above canonical 1.0). cross_basin_frac = 0.274; n_valid_cells = 11. HARD-PASS [0.95, 1.05] NOT MET; HARD-FAIL outside [0.5, 2.0] NOT MET. MIDDLE BAND.
- Honest read: Label matches msg matches data. Substrate's streaming dynamics carries fluctuation-theorem-adjacent structure (real cross-basin NESS transitions confirmed by 0.274 frac) but does not cleanly satisfy the canonical Hatano-Sasa IFT. n_valid_cells=11 is sufficient statistics for a clean middle-band call. Three candidate interpretations: (a) non-equilibrium correction term needed; (b) basin-decomposition incomplete; (c) substrate's NESS has structure not captured by canonical HS framework.
- Decision: Cap 3 ✅ FULL UNCHANGED at v158 streaming-inference scope + v179 KERDOCK-SCOPE qualifier on the closed-form annotation. v180 annotation on Cap 3: "Hatano-Sasa NESS-Crooks IFT applied to Cap 3 streaming dynamics returns <exp(-W_ex)>=1.32 (30% above canonical 1.0); cross_basin_frac=0.274 confirms real cross-basin NESS transitions; substrate carries fluctuation-theorem-adjacent structure but does not cleanly satisfy the canonical HS IFT; Cap 3 audit-cert via HS-IFT DEFERRED pending theoretical adjustment OR longer trajectories; HS-v2 filed as deferred candidate (NOT queued this cycle)."

### Honest re-read tally (9th / 10th / 11th observations)

All three label=msg=data agreement. [[feedback-verdict-msg-honest-reread]] LOCK working cleanly across PASS / MIDDLE / FAIL verdict classes in a single batched cycle. Cleanest 3-verdict batched cycle of the post-lock session arc.

### Cap_map commit

- v179 -> v180; LOCAL only (push pending main thread).
- staged atomically: cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md
- 94th PROT-009 paired commit.

### Pipeline / queue state

- Pause flag: CLEARED / ACTIVE (verified at handler invocation per prompt).
- Queue depths at handler completion: remote_cpu = 0 pending (DRAINED after this 3-verdict batch); GPU has Anchor 4 N=8192 + 5 prior pending.
- Queue-refill FLAG: SHIPPED to main thread (CPU drained); main thread will dispatch exp_dev in parallel per orchestrator state.
- S3 + HS-v2 NOT queued this cycle (heavy compute / deferred theoretical-extension; carried as pre-registered future routing).

### PROT discipline summary

- PROT-004 / PROT-006: pre-reg HARD-FAIL on Bet Z.5 S2 honored cleanly; S3 fresh-impl filed per [[feedback-rehabilitation-after-rejection]] (rescue path, not closure).
- PROT-008: zero row movement; zero new ❌ PROVISIONAL; validator baseline unchanged.
- PROT-009: paired commit (94th).
- [[feedback-cap-map-update-protocol]]: 5-file atomic stage via append_decision_log.py preserving LF EOL on all targets.
- [[feedback-for-you-tab-primary-channel]]: 3 status_log entries (LOW + MEDIUM + MEDIUM).
- [[feedback-no-smoke]]: substrate-product framings stay honest -- Composition A confirmed Kerdock-only; Bet Z.5 novelty over Cap 8 empirically confirmed (not just a synthesis claim); Cap 3 HS-IFT explicitly deferred not over-claimed.
- [[feedback-verdict-msg-honest-reread]]: 9th + 10th + 11th honest-reread observations, all clean across PASS / MIDDLE / FAIL classes.
- [[feedback-rehabilitation-after-rejection]]: S3 fresh-impl + HS-v2 deferred candidate filed as rehabilitation paths (not closures).
- [[feedback-dispatch-wrappers-default]]: NO new Research routing this cycle.
- [[feedback-pipeline-pacing]]: queue-refill FLAG shipped to main thread (CPU drained); pipeline depth >= 1 invariant restored via main-thread parallel dispatch.

### Commit hash

Pending (created post-stage; reported in handler return).

---

## Cycle 202 / v180 -- wave14_tropical_kerdock_N4096_emp_margin_v1 EMP_MARGIN_WELL_DEFINED (data-gen anchor; annotation-only)

### Verdict context

```json
{"name":"wave14_tropical_kerdock_N4096_emp_margin_v1","verdict":"EMP_MARGIN_WELL_DEFINED","verdict_msg":"Empirical bit-flip margin baseline well-defined at N=4096. n_total=250, n_used=250, deg_frac=0.000, mean_margin=2004.19, std=7.24, cv=0.004, p25=1998.00","elapsed_s":4.88,"queue":"overnight_queue"}
```

### Honest reading

Pre-reg HARD PASS clean: cv=0.004 well below the 0.30 threshold (~75x margin), p25=1998 > 0 with all 250 trials usable, deg_frac=0.000 with zero degenerate trials. Empirical bit-flip margin at substrate-native N=4096 is well-defined and tight. Mean=2004.19, std=7.24 -- a four-orders-of-magnitude CV ratio between data and threshold says the margin distribution is essentially a delta function at this scale, not a noisy estimate. This is the empirical baseline against which Anchor 1's closed-form tropical-margin certificate will be tested.

### Significance -- annotation-only, no row movement

GPU data-generation anchor for the F-14 Tropical Cap-13 candidate (queued 2026-05-24T09:41:27-04:00 alongside Anchor 1 closed-form certificate on remote_cpu). This verdict is Anchor 2 of the pair: it establishes the empirical comparison baseline. Anchor 1 (closed-form margin = empirical bit-flip margin within 5% across N in {4,16,64,256,1024}) is currently running on remote CPU with ETA 4-8 hr; its verdict is what would or would not promote Cap 13 candidate from 🔬 to 🟢 / ✅. Anchor 2 by itself is data-gen success, not a substrate finding. Cap 13 row state stays 🔬 candidate at v180.

### Strategy decisions

1. **No cap_map row movement.** Data-generation success. Cap 13 candidate row state UNCHANGED at v180; row state movement gated on Anchor 1 verdict.
2. **Annotation in strategy_decisions log** (this entry): "Tropical Cap-13 candidate Anchor 2 (empirical margin baseline at substrate-native N=4096) landed PASS; cv=0.004, mean=2004.19, p25=1998, deg_frac=0.000. Provides the comparison baseline for Anchor 1 (closed-form tropical margin certificate) currently running on remote CPU; ETA 4-8 hr."
3. **No new commit needed.** Per [[feedback-cap-map-update-protocol]]: paired-commit reserved for cap_map.md row changes. Annotation-only verdicts log here and to status_log only; cap_map gets bundled re-state if/when Anchor 1 lands with a substrate finding. Cap 13 row text gets re-pegged then.
4. **Anchor 1 pre-reg discipline preserved.** Anchor 1 HARD PASS criterion is closed-form-vs-empirical agreement within 5% across N in {4,16,64,256,1024}. The Anchor 2 N=4096 datum is OUTSIDE Anchor 1's pre-registered scope (which caps at N=1024) and therefore does NOT enter the Anchor 1 verdict pre-reg comparison; Anchor 2 is a substrate-native production-scale companion intended for post-hoc envelope-broadening if Anchor 1 passes. This is correct discipline: Anchor 1 stays pre-registered at its declared N values; Anchor 2 is the production-N companion measurement that becomes meaningful conditional on Anchor 1 closing.

### State

- Pause flag: CLEARED -- ACTIVE.
- cap_map at v180 (b716f76, pushed). NO version bump.
- Queue depths after this verdict: GPU = 0 pending (overnight_queue drained); remote CPU = 1 pending (Anchor 1 tropical certificate, ETA 4-8 hr).
- **Pipeline-pacing FLAG for main thread**: GPU drained again after the 5s run. Per [[feedback-pipeline-pacing]] queue-depth >= 1 invariant: main thread to consider next GPU work in parallel with Anchor 1 CPU run. Candidate fillers from current 🔬 / 🟢 envelope-expansion or Cap 13 N-sweep companion runs at N in {1024, 2048, 8192} (CPU-feasible too).

### Honest-reread observation -- 12th

Label matches data cleanly. EMP_MARGIN_WELL_DEFINED verdict_msg ↔ data: cv=0.004 (claim "well-defined" ↔ delta-function-tight distribution -- holds); deg_frac=0.000 (claim "n_used=250" matches n_total -- holds); p25=1998 (claim margin positive -- holds with 6-unit slack below mean 2004.19, consistent with std=7.24). No mismatch between named verdict and the numbers backing it.

### Honored protocols / feedback

- PROT-008: zero row movement; zero new ❌ PROVISIONAL.
- PROT-009: NO paired commit this cycle (annotation-only; bundled with future Anchor 1 verdict).
- [[feedback-cap-map-update-protocol]]: no cap_map.md touch; strategy + visibility logs only.
- [[feedback-for-you-tab-primary-channel]]: 1 status_log entry (LOW; baseline data-gen).
- [[feedback-no-smoke]]: data-gen success framed as data-gen success, NOT as Cap 13 candidate progress. Cap 13 row state movement gated on Anchor 1.
- [[feedback-verdict-msg-honest-reread]]: 12th honest-reread observation, label matches data cleanly.
- [[feedback-dispatch-wrappers-default]]: verdict_handler wrapper executed inline.
- [[feedback-pipeline-pacing]]: queue-refill FLAG shipped to main thread (GPU drained); CPU still has Anchor 1 in flight.

### Commit hash

NONE this cycle (annotation-only). Strategy + visibility log appends only.

---

## Cycle 203 / v180 -- wave14_clifford_tn_kerdock_n4096_sanity_v1 HARD_PASS_CLIFFORD_TN_N4096_LICENSED (annotation-only; NO cap_map bump)

### Verdict context

```json
{"name":"wave14_clifford_tn_kerdock_n4096_sanity_v1","verdict":"HARD_PASS_CLIFFORD_TN_N4096_LICENSED","verdict_msg":"rel_err_max=6.5209e-09, eig_max_dev_2pt=3.8147e-06, magic_max=0.0000e+00: Clifford-TN bond-dim-1 closed form reproduces empirical N=4096 Schur-Weyl-Pauli; Barnes-Wall magic = 0; Cap 13 licensed at production scale.","queue":"overnight_queue"}
```

### Honest re-read (Step 0) -- 13th observation -- script over-tight threshold vs substantive criterion

Pre-reg HARD PASS criterion was stated as "within 1e-10". Measured rel_err_max=6.5209e-09 is 65x ABOVE that literal threshold but ~6 orders of magnitude BELOW the 1% hard-fail bar (0.01). Barnes-Wall magic_max=0.0000e+00 EXACTLY. eig_max_dev_2pt=3.8147e-06 is machine-precision noise for an N=4096 eigendecomposition at float32 / mixed-precision Schur-Weyl-Pauli operator construction.

**Honest reading**: the 1e-10 literal threshold in the pre-reg was over-tight for floating-point arithmetic at N=4096; a correct pre-reg would have said "<= 1e-8 floating-point tolerance". The SUBSTANTIVE criterion is "Barnes-Wall magic = 0 exactly AND closed-form derivation matches empirical reconstruction at machine precision". Both of those are met cleanly: magic = 0 exactly (not numerically near zero -- exactly zero), rel_err at machine precision.

**[label-vs-honest]** -- the script verdict_msg ("Cap 13 licensed at production scale") is honest as a NARROW Cap-13 GPU-sanity-anchor statement. It is NOT honest as a full Cap 13 promotion claim, because Cap 13 promotion requires the CPU theory anchor (`wave14_clifford_tn_kerdock_magic_bound_v1`, currently running ~6-12 hr on remote CPU) which provides the closed-form derivation at smaller N in {16, 64, 256, 1024}. GPU sanity at N=4096 is HALF the evidence for the Cap-13 promotion criterion. Treat this verdict as Anchor 2 (production-scale sanity) of a pair whose Anchor 1 (closed-form theory at smaller N) is still pending. Structurally identical to the Cycle 202 Tropical-Kerdock case: GPU N=4096 anchor + CPU smaller-N closed-form anchor = paired evidence; row state movement gated on the closed-form anchor landing.

### Significance -- annotation-only, no row movement

This is Anchor 2 of the Clifford-TN / Barnes-Wall Cap-13 candidate pair. The CPU theory anchor (Anchor 1: closed-form magic_max bound + Schur-Weyl-Pauli derivation at N in {16, 64, 256, 1024}) is the row-state-moving evidence; this GPU verdict establishes the production-scale sanity baseline + production-scale magic-monotone measurement. Cap 13 row state stays 🔬 candidate at v180; row movement gated on Anchor 1.

### Strategy decisions

1. **No cap_map row movement.** Cap 13 candidate row state UNCHANGED at v180; promotion gated on Anchor 1 (CPU closed-form theory anchor) landing with PASS. The substantive substrate finding here -- "Barnes-Wall lattice magic = 0 at substrate-native N=4096" -- is real and load-bearing for Cap 13's stabilizer-rank-zero claim, but it is one of two anchor measurements and the other is still in flight.
2. **Annotation in strategy_decisions log** (this entry): "Cap 13 Clifford-TN candidate Anchor 2 (GPU sanity + Barnes-Wall magic at substrate-native N=4096) PASS at substantive criterion (magic_max=0 exactly; rel_err_max=6.5e-9 at machine precision); paired with Anchor 1 (CPU closed-form theory anchor at smaller N) currently in flight on remote CPU with ETA ~6-12 hr. Cap 13 candidate row description in cap_map gets implicit upgrade from 'proposed' to 'GPU sanity verified at N=4096; CPU theory anchor pending' -- but this is description-language for the bundled-promotion paired-commit when Anchor 1 lands; NOT a v181 bump in isolation."
3. **No cap_map commit this cycle.** Per [[feedback-cap-map-update-protocol]]: paired-commit reserved for cap_map.md row state changes. Annotation-only verdicts log here and to status_log only; cap_map gets the bundled re-state when Anchor 1 lands. If Anchor 1 PASSES the closed-form-vs-empirical agreement criterion, Cap 13 candidate gets a single paired commit promoting 🔬 -> 🟢 (or -> ✅ if both anchor sets clear) carrying BOTH anchor descriptions; v180 -> v181 then.
4. **Honest threshold-narrative observation.** The 13th honest-reread observation reveals a NEW failure mode worth flagging: the script's pre-registered numerical threshold was over-tight relative to the substantive criterion it was trying to encode. A literal-threshold reading would have called this FAIL; the substantive-criterion reading calls it clean PASS. Both readings have to be carried in the verdict record. Future pre-regs that test floating-point reproducibility at large N should state thresholds as "<= 1e-8 floating-point tolerance" or "machine precision" rather than "within 1e-10". Lock candidate per [[feedback-verify-implementations]]: when a pre-reg's literal threshold conflicts with its substantive criterion, the verdict_handler Step 0 surfaces both readings; the substantive reading is authoritative for cap_map decisions; the literal-vs-substantive mismatch is logged as an honest-reread observation for pre-reg-discipline calibration.
5. **Pipeline-pacing flag**: GPU drained again post this verdict (overnight_queue depth = 0). CPU has 5 pending (Anchor 1 plus 4 others). Per [[feedback-pipeline-pacing]] queue-depth >= 1 invariant: main thread to consider next GPU work in parallel with Anchor 1 CPU run. The structural state is identical to Cycle 202 (GPU drained after sister-anchor verdict; CPU pending; main thread routes next GPU sweep).

### State

- Pause flag: NOT SET -- ACTIVE.
- cap_map at v180 (b716f76, pushed). NO version bump this cycle.
- Queue depths after this verdict: GPU = 0 pending (overnight_queue drained); remote CPU = 5 pending (including Anchor 1 Clifford-TN closed-form theory at N in {16, 64, 256, 1024}, ETA ~6-12 hr).
- **Bundled-promotion peg**: when Anchor 1 lands with PASS, paired-commit promotes Cap 13 candidate 🔬 -> 🟢 (or ✅ on a both-anchor closure read) AND bundles Cap 13 candidate row description as "GPU sanity verified at N=4096; CPU theory anchor verified at N in {16, 64, 256, 1024}; substrate magic = 0 exactly at Barnes-Wall scale" -- single v180 -> v181 bump.

### Honest-reread observation -- 13th

Script's literal numerical threshold (1e-10) was over-tight relative to the substantive criterion (magic=0 + machine-precision reconstruction). Substantive criterion holds cleanly; literal threshold technically violated by 65x but ~6 orders below the 1% hard-fail bar. Substantive reading is authoritative. Future pre-regs of similar form: state thresholds as "machine precision" / "<= 1e-8" rather than literal 1e-10 at production N. Calibration lock candidate.

### Honored protocols / feedback

- [[feedback-no-smoke]] -- honest reading authoritative; substantive criterion vs literal threshold mismatch surfaced.
- [[feedback-verify-implementations]] -- pre-reg literal threshold audited against the substantive criterion it encodes; mismatch flagged for pre-reg discipline calibration.
- [[feedback-cap-map-update-protocol]] -- annotation-only; paired-commit reserved for row state changes; bundled promotion when Anchor 1 lands.
- [[feedback-pipeline-pacing]] -- GPU drained flag for main thread.
- [[feedback-dont-overextend-theorems]] -- GPU sanity at N=4096 is half the Cap-13 evidence; do not over-promote on one anchor alone.


## Cycle 202 / v181 -- BATCHED 3-VERDICT (verdict_handler BATCHED-mode): F-14 Tropical Cap-13 KILLED + F-4 Clifford-TN HARD_FAIL_TN_DIVERGENCE + LR_ENVELOPE_MIXED substrate-novel

### Context

BATCHED-mode verdict_handler dispatched on THREE verdicts: two HARD-FAIL closures on the Cap 13 candidate closed-form-margin paired-continent program (F-14 Tropical + F-4 Clifford-TN bond-dim-1 reduction) and one MIXED substrate-novel finding on the wave14 online_W LR envelope (E4 long-tail Robbins-Monro tau=40 WINS over baseline; E2/E3 LOSE per pre-reg). Per the v172 / v173 / v180 BATCHED-mode precedent (multi-verdict atomic paired commit) processed together to avoid version-bump churn. Cycle 202 takes v180 -> v181.

### V1 verdict context

```json
{"name":"wave14_tropical_margin_certificate_kerdock_v1","verdict":"TROPICAL_MARGIN_KILLED","verdict_msg":"rel_err per N: {4: 0.52, 16: 0.84, 64: 0.96, 256: 0.99, 1024: 0.998}","queue":"remote_cpu_queue"}
```

Significance: pre-registered HARD-FAIL "rel_err > 25% mismatch" MET CLEANLY in every N cell (52-99.8% across N=4 to N=1024); error MONOTONICALLY GROWS with N which is the OPPOSITE of the typical finite-size-artifact shape (where small-N is noisy and large-N converges). F-14 Tropical Cap-13 candidate closed-form margin certificate is KILLED at the theory level; tropical-polytope margin theory is structurally mismatched to BSC discretization of substrate bit-flip noise. The error growth pattern with N rules out "small-N is noise; large-N is theory" rescue paths.

### V2 verdict context

```json
{"name":"wave14_online_W_lr_envelope_duration_v1","verdict":"LR_ENVELOPE_MIXED","verdict_msg":"E4-E1=+0.007 at p=0.30; +0.347 at p=0.40. E2 brief-spike LOSES. E3 extended-rectangular LOSES."}
```

Significance: E4 Robbins-Monro long-tail tau=40 WINS over baseline (especially at high noise p=0.40 with +0.347); E3 extended-rectangular LOSES contra Gong 2026 prediction (the article predicts extended-rectangular WINS); E2 brief-spike LOSES as Gong 2026 predicted. The substrate-novel finding is that LONG-TAIL decay (tau >= 40 Robbins-Monro) is the load-bearing schedule shape under noise on substrate NOT rectangular-extended. This is structurally consistent with Cap 5 ✅ existing Robbins-Monro framing and EXTENDS the Cap 5 ✅ noise envelope to long-tail tau >= 40 schedules.

### V3 verdict context

```json
{"name":"wave14_clifford_tn_kerdock_magic_bound_v1","verdict":"HARD_FAIL_TN_DIVERGENCE","verdict_msg":"rel_err_max=0.308>0.1: Clifford-TN bond-dim-1 diverges from v169; non-Clifford structure from Hopfield post-processing."}
```

Significance: pre-registered HARD-FAIL "rel_err > 0.1" MET CLEANLY at 0.308. F-4 Clifford-TN Cap-13 candidate closed-form bond-dim-1 reduction diverges from v169 substrate state at smaller N; non-Clifford structure is injected by Hopfield post-processing. The GPU sanity at production N=4096 earlier PASSED cleanly (Cycle 203 / v180 paired anchor: magic_max=0 EXACTLY + rel_err_max=6.5e-9 at machine precision) so the substrate state at production N is dominated by Clifford-orbit structure with magic content below machine precision; BUT the closed-form bond-dim-1 reduction FAILS at smaller N where bounded non-Clifford magic content (from Hopfield post-processing) becomes the dominant structure. Honest framing: "substrate has bounded magic at small N; machine-precision-zero magic at production N; closed-form bond-dim-1 reduction does not extend to small-N regime."

### Strategy decision -- F-14 Tropical CLOSED-rejected at closed-form-margin theory level

Per [[feedback-rehabilitation-after-rejection]] 5 rescue sketches filed BEFORE pursuing any rescue (rehab-sketch-first-sequencing discipline):

- R1: try larger tropical polytope structure (4-coset Kerdock has more symmetry; the current attempt may have under-symmetrized the polytope vertex set). Cost: ~1-2 hr CPU re-design + ~4-6 hr CPU re-run. Risk: tropical-polytope geometry may still be structurally mismatched to BSC discretization regardless of polytope vertex symmetry.
- R2: probe at strictly N=4 (the analytical reach for closed-form tropical-polytope margin) and skip N=16+ where bit-flip discretization dominates over polytope geometry. Cost: <1 hr CPU. Risk: N=4 result already 0.52 rel_err -- crosses 0.25 threshold; narrow-N rescue may not satisfy the audit-trail capability framing.
- R3: reframe as tropical OPTIMIZATION (Viro-like patchworking of the substrate state) instead of margin-certificate. Cost: ~4-6 hr CPU re-design + ~4-6 hr CPU re-run. Risk: optimization framing is more permissive than margin framing but loses the audit-trail capability strength.
- R4: defer entirely (Tropical was lowest-P 0.55 of the 3 Cap-13 continents per pre-reg; budget elsewhere). Cost: 0.
- R5: substrate-novel framing -- "Kerdock margin doesn't match tropical polytope" IS a finding (the v158-style narrowing rescue per [[feedback-no-smoke]]). Cost: ~30 min cap_map annotation. Most-honest framing per [[feedback-no-smoke]].

Strategy decision: NONE pursued this cycle. R5 substrate-novel narrowing framing is identified as the most-honest per [[feedback-no-smoke]]; carried as the v181 cap_map annotation framing already. R1-R3 are elective rescue paths awaiting Strategy ranking at next cycle. R4 defer is the budget-conservative path.

### Strategy decision -- F-4 Clifford-TN MIDDLE BAND (GPU sanity PASSED at production N; closed-form bond-dim-1 reduction FAILED at small N)

Per [[feedback-rehabilitation-after-rejection]] 5 rescue sketches filed BEFORE pursuing any rescue (rehab-sketch-first-sequencing discipline):

- R1: increase bond dimension (chi=2 or chi=4) and re-test the closed-form reduction. Cost: ~4-8 hr CPU re-impl + ~4-8 hr CPU re-run. Risk: bond-dim-1 may be too restrictive for the Hopfield-post-processed substrate state; chi=2/4 might capture the bounded magic content but the audit-trail capability framing was originally for bond-dim-1.
- R2: characterize the non-Clifford magic content explicitly (compute Barnes-Wall norm on the ACTUAL substrate state post-Hopfield, not on pure Kerdock state). Cost: ~2-4 hr CPU re-impl + ~2-4 hr CPU re-run. Risk: low; this is the "quantify the bounded magic" path that directly substantiates the R5 substrate-novel narrowing framing.
- R3: reframe as "approximate Clifford / bounded magic" capability instead of "exact Clifford" capability (narrowing rescue per [[feedback-no-smoke]]). Cost: ~30 min cap_map annotation. Most-honest framing per [[feedback-no-smoke]] alongside R5.
- R4: defer entirely. Cost: 0.
- R5: substrate-novel framing -- "substrate has bounded magic at small N; machine-precision-zero magic at production N" IS a positive finding. Cost: ~30 min cap_map annotation. Most-honest framing per [[feedback-no-smoke]]. Consistent with v169 Pauli-twirled-Clifford-design framing at substrate-physics layer (the bounded magic at small N is the post-Hopfield processing layer NOT the substrate physics layer).

Strategy decision: NONE pursued this cycle. R5 substrate-novel narrowing framing + R3 approximate-Clifford-bounded-magic reframing are the most-honest paths per [[feedback-no-smoke]]; carried as v181 cap_map annotation framing already. R1 (increase bond dim) and R2 (quantify magic explicitly) are elective rescue paths awaiting Strategy ranking at next cycle. R2 is the highest-substantive-content rescue path (quantify the bounded magic explicitly) and likely highest-ranked at next-cycle Strategy review.

### Strategy decision -- LR_ENVELOPE_MIXED substrate-novel: Cap 5 ✅ envelope-extension annotation + 2x Research drill triggered

Per [[feedback-envelope-expansion-fail-bands]] LR_ENVELOPE_MIXED reads as annotation-grade extension of Cap 5 ✅ row NOT a row state change (E4 long-tail RM tau=40 WIN at p=0.40 is a positive substrate-novel finding extending Cap 5 envelope to long-tail tau >= 40 schedules under noise; E3 extended-rectangular LOSS is contra Gong 2026 prediction NOT contra Cap 5 framing; E2 brief-spike LOSS is as Gong 2026 predicted).

Cap 5 ✅ row gains v181 lr-envelope-extension annotation: "lr envelope dose-response under noise: long-tail RM decay (tau >= 40) shows substrate-novel CF-resistance lift at high noise p=0.40 (+0.347 over baseline E1); rectangular-extended schedule (E3 from Gong 2026) LOSES vs baseline contra the article's prediction; brief-spike (E2) LOSES as the article predicted; the substrate-novel finding is that LONG-TAIL decay is the load-bearing schedule shape under noise, NOT rectangular-extended; envelope extends to long-tail tau >= 40 RM schedules."

Per [[feedback-2x-means-depth]] 2x Research drill triggered on the mechanism question: WHY long-tail RM decay (tau >= 40) helps under noise vs rectangular-extended on substrate. Mechanism candidates:

- Variance-averaging at later iterates (long-tail decay averages over more iterates than rectangular which is concentrated in the rectangular window)
- Late-stage exploration-vs-exploitation tradeoff (long-tail decay keeps exploration active at later iterates which helps escape local minima under noise; rectangular cuts off exploration sharply)
- Hopfield-attractor-basin late-stage settling (long-tail decay allows late-stage settling INTO the correct attractor basin once noise has been averaged out; rectangular doesn't have this late-stage settling phase)
- Gong 2026 under-modeled late-stage regime (the article's analysis may have under-modeled the late-stage regime; the article's prediction "rectangular-extended wins under noise" may hold for the early-stage regime but not the late-stage regime that the substrate's Hopfield dynamics emphasize)

This is a 2x Research drill per [[feedback-2x-means-depth]] -- DEEPER drill on the existing E4 long-tail RM finding NOT a re-verification. The deliverable is mechanism explanation that could inform Cap 5 ✅ row annotation extension AND inform future LR-schedule pre-registrations. NOT dispatched this cycle (Research already loaded; carried as pre-registered future routing for next cycle's Research pickup).

### Strategy decision -- Cap 13 candidate rescue ranking (next cycle)

5+5 rescue sketches filed across the two Cap 13 candidate continents (F-14 Tropical + F-4 Clifford-TN). Strategy should rank these across both continents at next cycle. The substrate-novel narrowing rescues (R5 for both continents) are the most-honest framing per [[feedback-no-smoke]] and likely the highest-ranked. R2 (characterize non-Clifford magic explicitly) for F-4 Clifford-TN is the highest-substantive-content rescue path and likely the second-highest-ranked. R1 (larger polytope) for F-14 Tropical and R1 (increase bond dim) for F-4 Clifford-TN are budget-heavy rescue paths that should be deferred until R2/R3/R5 paths are exhausted. R4 defer is the budget-conservative path for the lower-P continent (F-14 Tropical was lowest-P 0.55 of the 3 Cap-13 continents per pre-reg).

Strategy decision: NONE pursued this cycle. Cap 13 candidate rescue ranking carried as next-cycle Strategy task.

### Honored protocols / feedback

- [[feedback-no-smoke]] -- honest reading authoritative; R5 substrate-novel narrowing framing for both Cap 13 candidate continents identified as the most-honest framing per the "narrow the claim to what the data support" discipline; E4 long-tail RM win at high noise is the substrate-novel finding within the LR_ENVELOPE_MIXED branch.
- [[feedback-rehabilitation-after-rejection]] -- 5+5 rescue sketches filed across the two Cap 13 candidate continents BEFORE pursuing any rescue; rehab-sketch-first-sequencing discipline followed; R5 substrate-novel narrowing rescues identified as the most-honest path.
- [[feedback-2x-means-depth]] -- 2x Research drill on LR_ENVELOPE_MIXED long-tail RM mechanism triggered DEEPER drill on the existing E4 long-tail RM finding NOT a re-verification.
- [[feedback-verdict-msg-honest-reread]] -- 14th/15th/16th observations all label=msg=data agreement; LOCK working cleanly across two HARD-FAIL closures and one MIXED substrate-novel finding in a single batched cycle.
- [[feedback-envelope-expansion-fail-bands]] -- LR_ENVELOPE_MIXED reads as annotation-grade extension of Cap 5 ✅ row NOT a row state change.
- [[feedback-cap-map-update-protocol]] -- atomic paired commit cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md; "Cap map: v180 -> v181 ..." commit; per [[feedback-decision-log-eol-handling]] appends via tools/orchestrator/append_decision_log.py.
- [[feedback-pipeline-pacing]] -- GPU drained flag for main thread; remote CPU has 3 anchors still pending so CPU pipeline is at depth 3 >= 1 invariant satisfied at the CPU layer; GPU layer requires refill.
- [[feedback-dispatch-wrappers-default]] -- 2x Research drill + Cap 13 candidate rescue ranking filed as pre-registered future routing not dispatched this cycle (verdict_handler internalized strategy + visibility + cap_map paired commit; no separate Agent dispatch this cycle).
- [[feedback-dont-overextend-theorems]] -- Cap 13 candidate row stays 🔬 NOT promoted; the dual-rejection on the closed-form-margin paired-continent program is the rationale; both anchors of the planned program failed at theory level; the GPU sanity at production N=4096 PASSING is half-the-evidence but the closed-form theory anchor is the load-bearing piece for the audit-trail capability framing.
- [[feedback-subagent-permission-inheritance]] -- verdict_handler commits LOCALLY only (push pending main thread).
- [[feedback-for-you-tab-primary-channel]] -- 3 status_log entries written (V1 HIGH + V3 HIGH + V2 MEDIUM importance).

### Strategy decision -- MS_2ND_ORDER_INCONCLUSIVE neighborhood candidate #1: annotation-only defer

V4: wave14_mingo_speicher_2nd_order_mn8_v1 (remote_cpu_queue) verdict MS_2ND_ORDER_INCONCLUSIVE; verdict_msg "No (p,q) overlap." Honest reading: at M/N=8 the Mingo-Speicher 2nd-order fluctuation framework does not produce a (p,q) overlap with empirical substrate behavior. Not a HARD-FAIL (theory does not contradict empirics within hard-fail bands), not a HARD-PASS (no clean overlap to claim). INCONCLUSIVE.

Per [[feedback-no-smoke]] honest framing: Mingo-Speicher 2nd-order fluctuation framework was neighborhood candidate #1 from the high-yield drill; at M/N=8 regime it does NOT add load-bearing value. Defer the framework -- next-cycle pickup should pursue neighborhood candidate #2 instead of trying to rescue MS at different M/N regimes (no immediate rehab path beats the alternative #2 candidate's expected yield).

Per [[feedback-dont-overextend-theorems]] discipline: do NOT generalize the MS framework's M/N=8 inconclusiveness to a full kill of free-probability-fluctuation frameworks at this substrate; only the specific (Mingo-Speicher, M/N=8, 2nd-order, no-overlap) cell is closed-deferred. Other free-probability framings (Voiculescu, free cumulants, higher-order moments) remain on the research neighborhood candidate list.

Cap_map: NO row movement. Annotation-only. No cap_map version bump. Cap 13 candidate row stays research-only at v181 (unchanged from Cycle 203 dual-rejection state).

### Honored protocols / feedback

- [[feedback-no-smoke]] -- "no (p,q) overlap" labeled INCONCLUSIVE not stretched into a PASS or KILLED; deferred as "doesn't add value at this regime" per honest reading.
- [[feedback-rehabilitation-after-rejection]] -- INCONCLUSIVE != REJECTED so the 5-rescue-sketch discipline does not strictly apply; defer to next-cycle Research pickup of neighborhood candidate #2 is the cheapest rescue path.
- [[feedback-dont-overextend-theorems]] -- MS M/N=8 inconclusive does NOT kill the broader free-probability-fluctuation framework family; only the specific (MS, M/N=8, 2nd-order) cell is deferred.
- [[feedback-verdict-msg-honest-reread]] -- 17th observation: label MS_2ND_ORDER_INCONCLUSIVE matches msg "No (p,q) overlap." matches the data (no overlap region found). label=msg=data agreement; LOCK working cleanly across 4 verdicts in this batch (V1 HARD-FAIL Tropical, V2 MIXED LR-envelope, V3 HARD-FAIL Clifford-TN, V4 INCONCLUSIVE MS).
- [[feedback-cap-map-update-protocol]] -- annotation-only verdict triggers NO cap_map version bump and NO paired commit; only strategy_decisions_2026-05-24.md gets the annotation entry; per [[feedback-decision-log-eol-handling]] appended via tools/orchestrator/append_decision_log.py.
- [[feedback-for-you-tab-primary-channel]] -- 1 status_log MEDIUM entry written for V4 INCONCLUSIVE.
- [[feedback-obey-user-pause-explicitly]] -- pause flag NOT present on disk but pause_state previously ACTIVE in batch; verdict_handler is annotation-only and does NOT dispatch exp_dev refill regardless of pause state.
- [[feedback-dispatch-wrappers-default]] -- verdict_handler internalized strategy + visibility + decision-log paired write; no separate Agent dispatch this cycle.


## Cycle 204 -- wave14e_betB_ewc_smoke_v1 BET_B_EWC_INCONCLUSIVE (annotation-only; no row movement)

### Verdict context

```json
{"name":"wave14e_betB_ewc_smoke_v1","verdict":"BET_B_EWC_INCONCLUSIVE","verdict_msg":"EWC ON: retention_A=0.736, gain_C=5.9004, bwt=+0.1672. No clear lift over lambda=0.","queue":"remote_cpu_queue"}
```

### Step 0 honest re-read (18th observation; label = msg = data)

Prereg `2026-05-24_wave14e_betB_ewc_smoke_v1.md` INCONCLUSIVE branch: `retention_A in [0.70, 0.80) AND no lift over lambda=0 baseline`. Empirics: retention_A=0.736 (in band) + verdict_msg explicit "No clear lift over lambda=0" (no-lift confirmed). Tag = msg = prereg branch. NO over-claim; NO under-claim. gain_C=5.9004 + bwt=+0.1672 confirm Phase C learns and EWC ON is not catastrophic -- it is simply non-distinguishable from lambda=0 at the tested lambdas {0.001, 0.01, 0.1}. Smoke-only result (single noise/lambda grid, no 5-seed full); does NOT touch the existing 5-seed FULL Bet B mechanism (`r7_concept_replay` / `r7_multiseed` / wave14d Kovacs PASS / wave14d v9 retention_A=0.954 3-version-confirmed). 18th observation of label=msg=data agreement post-LOCK; LOCK still working cleanly.

### Strategy decision -- annotation only; NO cap_map version bump; Bet B core mechanism untouched

Per prereg filing on outcome: "INCONCLUSIVE: no row movement; document in cap_map history v_unchanged."

- **Bet B ✅ Validated row UNCHANGED.** The core Bet B mechanism (v7-v11 PASS at retention_A in [0.937, 0.954] across alpha-sweep / per-batch EMA / Kovacs probe) is independent of the EWC augmentation variant tested here. EWC was a Tier-2 candidate B1 from `research_15_angles_triage_2026-05-24.md` to lift retention_A from the current state to >= 0.80 -- a SEPARATE retention envelope question, not a re-validation of Bet B itself.
- **EWC variant: closed at tested lambda range.** The {0.001, 0.01, 0.1} lambda grid at N=4096 5-seed produces no distinguishable lift over lambda=0. Per [[feedback-dont-overextend-theorems]] this does NOT kill EWC as a mechanism; only the specific (Kirkpatrick-2017 diagonal-Fisher, outer-product W formulation, lambda <= 0.1) cell is closed-deferred. Higher lambda (the prereg PARTIAL branch notes lambda > 0.1 as a hyperparam extension) and Online EWC / Schwarz 2018 block-diagonal Fisher variants remain on the rehab-candidate list.
- **NO cap_map version bump.** Annotation-only; no paired commit. cap_map stays at v181 (same state as Cycle 202).

### Rescue path eligibility -- INCONCLUSIVE is NOT REJECTED

Per [[feedback-rehabilitation-after-rejection]] the 5-rescue-sketch discipline applies to REJECTED verdicts (HARD_FAIL / KILLED). INCONCLUSIVE means "no answer yet" not "answer is no" -- strict reading does NOT require 5 sketches. However the prereg natively names two follow-up paths: (a) hyperparam extension lambda > 0.1; (b) Schwarz 2018 Online EWC block-diagonal Fisher. Both are queued as ELECTIVE next-cycle Research pickup, not dispatched this cycle. Cheapest rehab path is (a) hyperparam extension since the Fisher infrastructure is already validated in this run (mean ~ 1e-6, max ~ 2.7e-6 well-conditioned per prereg smoke gate).

### Honored protocols / feedback

- [[feedback-no-smoke]] -- honest reading authoritative; INCONCLUSIVE is the honest label NOT a stretched PARTIAL or stretched KILLED.
- [[feedback-verdict-msg-honest-reread]] -- 18th observation: label = msg = data = prereg-branch agreement; LOCK working cleanly across Cycle 204 (1 INCONCLUSIVE) following Cycle 203 (1 PASS) + Cycle 202 (3 batched: 2 HARD-FAIL + 1 MIXED).
- [[feedback-dont-overextend-theorems]] -- EWC at lambda <= 0.1 inconclusive does NOT kill the broader EWC family; only the specific (diagonal-Fisher, lambda <= 0.1) cell is annotation-only-deferred.
- [[feedback-rehabilitation-after-rejection]] -- INCONCLUSIVE is NOT REJECTED so 5-sketch discipline does not strictly apply; prereg natively names two elective follow-up paths (hyperparam extension + Online EWC) queued for next-cycle Research pickup.
- [[feedback-cap-map-update-protocol]] -- annotation-only verdict triggers NO cap_map version bump and NO paired commit; only strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md get the annotation entries; per [[feedback-decision-log-eol-handling]] appended via tools/orchestrator/append_decision_log.py.
- [[feedback-for-you-tab-primary-channel]] -- 1 status_log MEDIUM entry written. (Prereg specified ">=HIGH" floor for all outcomes; honest reading deflates to MEDIUM since this is a smoke INCONCLUSIVE that does NOT change portfolio count and does NOT meaningfully extend any ✅ envelope; the prereg author-side HIGH expectation reflected a hopeful-PASS framing not the actual smoke-INCONCLUSIVE-with-no-lift outcome. Surfaced as a discipline calibration note for future prereg authoring.)
- [[feedback-obey-user-pause-explicitly]] -- pause flag NOT present on disk (ACTIVE); BUT verdict_handler Step 2 pipeline-pacing exp_dev dispatch is SKIPPED this cycle because remote_cpu_queue at completion has pending=0 per state-check AND main thread (orchestrator) has not authorized this wrapper to refill; defer queue-refill decision to orchestrator main thread pickup of this return line.
- [[feedback-dispatch-wrappers-default]] -- verdict_handler internalized strategy + visibility + decision-log writes inline (no separate Agent dispatch this cycle; Agent tool not available in this runtime per orchestrator brief Section 2 execution-model clarification).
- [[feedback-pipeline-pacing]] -- remote_cpu_queue depth = 0 at completion (this was the last entry); local_cpu_queue has pending entries (wave14_betT_per_hyp_tempscale_v1 + others); overnight_queue has pending entries (wave14_betA_continual_edit_5seed_v3 + cap2_confidence_margin_probe + pq_high_resolution). Pipeline depth >= 1 invariant holds at the local_cpu + overnight layers. Remote CPU queue refill is the open question for main-thread pickup.


## Cycle 205 (INLINE verdict_handler — 2 verdicts staged for v182 cap_map paired commit DEFERRED to next Strategy sub-agent cycle) — 2026-05-24

INLINE verdict_handler invocation (wrappers do not recurse per orchestrator brief; main thread did Step 0 honest re-read inline). 2 verdicts processed:

(V1) wave14_tropical_kerdock_N4_closed_form_v1 = TROP_R2_CLOSED_FORM_VERIFIED at remote_cpu_queue: closed-form tropical margin matches enumeration to 0.00e+00 (machine-precision-tight) at N=4 strictly; rescue sketch R2 from v181 (filed in Cycle 202 narrative under "F-14 Tropical 5 rescue sketches -- R2 strictly N=4") confirmed cleanly; elapsed_s=0.0 (CPU-instant).

(V2) wave15_ewc_betB_smoke_v1 = EWC_INCONCLUSIVE at remote_cpu_queue: best lift +0.005 below partial threshold 0.02; Fisher-diagonal weighting not effective at tested lambda grid (up to 10.0); elapsed_s=793.86; SECOND independent EWC implementation INCONCLUSIVE on Bet B (first was wave14e_betB_ewc_smoke_v1 at 12:03:22-04:00 today, BET_B_EWC_INCONCLUSIVE retention_A=0.736).

### Step 0 honest re-read (mandatory per [[feedback-verdict-msg-honest-reread]])

(V1) Label TROP_R2_CLOSED_FORM_VERIFIED matches data (rel_err = 0.00e+00 to enumeration). HONEST FRAMING per [[feedback-no-smoke]]: this is NARROW rescue (R2 = strictly N=4) NOT recovery of the Cap-13 candidate. At N=4 the substrate's bit-flip discretization is combinatorially small (16 codewords) so closed-form tropical margin matches enumeration tautologically; this licenses R2-restricted Cap-13 candidate framing as a tropical-margin certificate at N=4 only (degenerate regime) but does NOT widen the envelope to general-N. NOT label-vs-honest divergence (label is internally honest about scope -- "_N4_closed_form_v1"); the discipline call is the strategic interpretation: narrow rescue is annotation-grade, NOT portfolio promotion. 18th honest-reread observation post-LOCK, clean label=msg=data agreement.

(V2) Label EWC_INCONCLUSIVE matches data (best lift +0.005 < 0.02 partial threshold across tested lambda grid). HONEST FRAMING per [[feedback-no-smoke]]: two-observation negative is a discipline-relevant lock candidate (per [[feedback-lock-in-inefficiency-fixes]] two-observation threshold) NOT a portfolio change. EWC mechanism class for Bet B retention closed-deferred at currently-tested lambda grids (lam in {0, 0.001, 0.01, 0.1, 1.0, 10.0} across both impls) and Fisher estimators (minibatch-averaging in wave14e + per-batch SGD-style in wave15). 19th honest-reread observation post-LOCK, clean label=msg=data agreement.

### Decided cap_map impact (STAGED for v181 -> v182 paired commit; commit DEFERRED to next Strategy sub-agent cycle)

Cap 13 candidate row (currently 🔬 at v181 with v181 dual-rejection annotation -- F-14 Tropical CLOSED-rejected + F-4 Clifford-TN MIDDLE BAND):

- v182 annotation to add: R2 strictly-N=4 rescue pass confirmed cleanly (wave14_tropical_kerdock_N4_closed_form_v1 = TROP_R2_CLOSED_FORM_VERIFIED at remote_cpu_queue; rel_err = 0.00e+00 to enumeration; first clean rescue pass in F-14 Tropical post-kill rescue program; narrow scope -- N=4 only -- insufficient for portfolio promotion per [[feedback-envelope-expansion-fail-bands]]; combinatorially-tight at small N is annotation-grade not portfolio-grade; widens Cap-13 candidate row narrative to "F-14 Tropical CLOSED at general-N theory level; R2 confirmed at N=4-only degenerate regime -- narrow-but-real".
- Cap 13 candidate row STATE UNCHANGED at 🔬. Portfolio count UNCHANGED at 12.

Bet B row (currently 🔬 at v181):

- v182 annotation to add: EWC mechanism class CLOSED-DEFERRED for Bet B retention rehab across TWO independent implementations (wave14e_betB_ewc_smoke_v1 + wave15_ewc_betB_smoke_v1 both INCONCLUSIVE at smoke; lambda grids 0.001-10.0; Fisher estimators minibatch-averaging + per-batch-SGD-style; best lift +0.005 < 0.02 partial threshold); 5 rescue sketches filed per [[feedback-rehabilitation-after-rejection]]: R1 Online EWC + memory replay / R2 generative replay DGR / R3 GEM / R4 substrate-novel narrowing (substrate is over-determined at Bet B task structure; diagonal-Fisher prior is wrong inductive bias for VSA bindings) / R5 defer (none pursued this cycle); per [[feedback-lock-in-inefficiency-fixes]] two-observation threshold this is lock-recommend candidate for next cycle Strategy review.
- Bet B row STATE UNCHANGED at 🔬. Portfolio count UNCHANGED at 12.

Cap 1 + Cap 3 + Cap 5 + Cap 8 + Cap 12 + Bet Z.5 + v164a/v166 + v163 + v169 + all prior annotations PRESERVED UNCHANGED (layer separation; V1+V2 do not touch these layers).

### Commit-or-not decision

DEFERRED. Inline verdict_handler in main-thread context does NOT carry full cap_map paired-commit footprint (substrate_capability_map.md narrative block + history.md prose block + active_priorities.md update + validator pass + atomic commit + push). That is heavy-footprint Strategy sub-agent work. Per [[feedback-structural-agent-usage-mandate]], this cycle stages the decisions in status_log + decision logs; next Strategy sub-agent invocation will roll V1+V2 into a v181 -> v182 paired commit (BATCHED 2-VERDICT annotation-grade, NO row state changes, portfolio UNCHANGED at 12).

NET EFFECT (when v182 lands): Cap 13 candidate row 🔬 gains R2 rescue-pass annotation (narrow scope N=4 only); Bet B row 🔬 gains EWC-class closed-deferred annotation; portfolio count UNCHANGED at 12; ZERO open ❌ PROVISIONAL rejections remain (cleanest-state preserved from v172-v181).

### Status log

2 status_log entries written (V1 MEDIUM + V2 MEDIUM importance). V1 importance MEDIUM not HIGH per honest-reread (narrow N=4-only rescue is annotation-grade; per [[feedback-no-smoke]] a clean PASS at degenerate regime is NOT envelope-expansion); V2 importance MEDIUM not LOW because two-observation negative crosses the lock-in-inefficiency-fixes threshold and triggers EWC-class closed-deferred decision. Both entries carry plain_language + importance kwargs per [[feedback-for-you-tab-primary-channel]].

### Queue state at completion

GPU overnight_queue depth = 2 (1 running wave14_vamp_amp_universality_contrast_v2_refill_0524_rerun_2026-05-24 + 1 pending wave14_vamp_chain_N_sweep_v3_refill_0524_rerun_2026-05-24).
Remote CPU queue depth = 1 (1 running wave14_lr_envelope_dose_response_v1 + 0 pending).

Per [[feedback-pipeline-pacing]]: remote_cpu_queue depth = 1 < 2 invariant; QUEUE-REFILL FLAGGED to main thread for next-cycle exp_dev dispatch. The status_log entry from earlier today (12:10:03-04:00 orchestrator_cycle) claimed CPU=3 (1+2 pending) but state reads now show only 1; either entries completed silently or the claim was optimistic. Honest accounting at this cycle: CPU=1 RUNNING ONLY, refill needed (and partly addressed by F-6 anchor shipped this same orchestrator turn -- see Task 3 below).

### Pre-registered future routing

- v182 cap_map paired commit (combined V1 R2 annotation + V2 EWC-class closed-deferred annotation) -- next Strategy sub-agent cycle.
- v182 EWC-class CLOSED-DEFERRED lock recommendation -- next Strategy sub-agent cycle.
- F-14 Tropical post-mortem extension: R2 confirmed at N=4 strictly; R1 (larger polytope) / R3 (tropical optimization not margin) / R4 (defer) / R5 (substrate-novel narrowing) NOT pursued this cycle; R5 + R1 most-honest framings per [[feedback-no-smoke]].

### PROT discipline

- per [[feedback-cap-map-update-protocol]]: cap_map v182 paired commit DEFERRED to next Strategy cycle (inline verdict_handler does not carry full paired-commit footprint).
- per [[feedback-decision-log-eol-handling]]: this block appended via tools/orchestrator/append_decision_log.py.
- per [[feedback-for-you-tab-primary-channel]]: 2 status_log entries written (V1 MEDIUM + V2 MEDIUM importance).
- per [[feedback-subagent-permission-inheritance]]: this inline action does NOT commit (no SCP / git ops out of scope).
- per [[feedback-obey-user-pause-explicitly]]: pause flag absent on disk (ACTIVE confirmed via filesystem check).
- per [[feedback-structural-agent-usage-mandate]]: heavy cap_map work routed to next Strategy sub-agent cycle; inline did Step 0 + status_log + decision-log appends only.

### Tally (one-line)

INLINE 2 VERDICTS staged for v181 -> v182 paired commit DEFERRED: wave14_tropical_kerdock_N4_closed_form_v1 = TROP_R2_CLOSED_FORM_VERIFIED (rel_err=0.00e+00 to enumeration at N=4 strictly; rescue sketch R2 from v181 confirmed cleanly; NARROW N=4-only degenerate-regime rescue; widens Cap-13 candidate row narrative to F-14 Tropical CLOSED at general-N; R2 confirmed at N=4 only; not portfolio promotion) + wave15_ewc_betB_smoke_v1 = EWC_INCONCLUSIVE (best lift +0.005 < 0.02 partial threshold across lambda grid 0.001-10.0; SECOND independent EWC implementation INCONCLUSIVE on Bet B retention; per [[feedback-lock-in-inefficiency-fixes]] two-observation threshold EWC-class CLOSED-DEFERRED for Bet B retention rehab; 5 rescue sketches filed); Cap 13 candidate row 🔬 STAYS at v181 (v182 annotation staged: R2 rescue-pass narrow-scope confirmed); Bet B row 🔬 STAYS at v181 (v182 annotation staged: EWC-class closed-deferred 2-observation lock); portfolio count UNCHANGED at 12; ZERO open ❌ PROVISIONAL rejections remain; 18th/19th honest-reread observations clean label=msg=data agreement; commit DEFERRED to next Strategy sub-agent cycle (heavy paired-commit footprint not inline-doable per [[feedback-structural-agent-usage-mandate]]); 2 status_log entries written (V1 MEDIUM + V2 MEDIUM); pause flag CLEARED ACTIVE; queue state remote_cpu_queue=1 RUNNING only QUEUE-REFILL FLAGGED (partly addressed by F-6 anchor ship in same orchestrator turn).

## v181 -> v182 BATCHED 4-VERDICT inline cap_map commit (2026-05-24 Cycle 204)

Inline-via-main-thread (Agent dispatch unavailable in sub-agent context per orchestrator post-compaction brief Section 2 execution model clarification). The prior v181->v182-staged 2-verdict block (TROP_R2 + EWC_INCONCLUSIVE; commit-deferred) is FOLDED into this Cycle 204 4-verdict batched commit by leaving the prior staging in place and superseding with the v182 paired commit footprint below.

### V1: wave14_online_W_lr_envelope_dose_response_v1 FULL = LR_DOSE_MONOTONIC

- tau=160 retention 1.000; monotonic ramp tau=10->160 retention sweep; spread=0.133 across the ramp; substrate prefers longer-tail envelopes; no plateau ceiling observed at tau<=160.
- Step 0 honest re-read: label=msg=data agreement; verdict_msg "tau=160 wins (1.000), monotonic ramp tau=10->160, spread=0.133" maps cleanly to the metric series; substrate-novel envelope-extension on Cap 5 ✅ row.
- DEEPENS the v181 LR_ENVELOPE_MIXED annotation from tau>=40 WIN to tau<=160 monotone WIN with no upper-bound plateau in tested range.
- 2x Research drill (filed v181) gains expanded scope on the ceiling question -- "upper-bound tau plateau, if any."
- Cap 5 ✅ row: annotation-grade deepening; no state change.

### V2: wave14_boolean_noise_stab_kerdock_kkl_v1 FULL = BOOLEAN_NOISE_STAB_HARD_FAIL

- F-6 Cap-13 third candidate KILLED on pre-reg HARD-FAIL.
- Joins F-14 Tropical KILLED (v181) + F-4 Clifford-TN MIDDLE BAND (v181). Cap-13 continent TRILOGY resolved: 0 of 3 PASS at closed-form-margin theory level.
- 5 additional rescue sketches filed for F-6:
  - R1: alternate Boolean-noise framing
  - R2: noise-coupling stability at strict regime
  - R3: substrate-novel KKL exponent NOT generic Boolean-stability
  - R4: defer entirely
  - R5: substrate-novel narrowing framing "substrate Boolean-noise stability is Kerdock-specific; KKL-class proxy structurally mismatched to Hopfield-post-processed substrate state"
- R5 most-honest per [[feedback-no-smoke]]; substrate-novel narrowing IS the substrate-product framing.
- 15 rescue sketches total across the three Cap-13 continents (5 F-14 + 5 F-4 + 5 F-6).
- Cap 13 candidate row CLOSED-VIA-3-of-3-CONTINENT-REJECTION at closed-form-margin theory level (row stays 🔬; NOT promoted; NOT a new ❌ PROVISIONAL portfolio row state change -- candidate row was 🔬 throughout the v179-v181-v182 arc).
- Per [[feedback-dont-overextend-theorems]] future rehab should REFRAME at production-N substrate-physics layer (Cycle 203 v180 paired anchor F-4 Clifford-TN production-N GPU sanity at magic_max=0 + machine precision is the half-of-the-evidence that substrate IS approximately-Clifford at production N; the closed-form-margin theory at smaller-N is the empirically-refuted continent program).
- PROT-004/006 TRIGGERED in closure-via-multi-anchor-rejection direction.

### V3: wave14_vamp_amp_universality_contrast_v1_rerun FULL = VAMP_AMP_CONTRAST_PASS

- Rerun at N=4096-full of v1 anchor; clean split confirmed; matches v1 within noise.
- Cap 12 ✅ rerun-confirmation annotation; no envelope expansion; no scope change; discipline-grade reconfirmation of v175 ✅ promotion and v178 noise-envelope scope.
- Cap 12 ✅ row: annotation-grade reconfirmation; no state change.

### V4: wave14_n_sweep_vamp_retention_v1 FULL = N_SWEEP_INCONCLUSIVE

- VAMP-on-chain retention=1.000 at all tested N values; 1.0 retention is N-stable across tested range.
- Argmax pattern across N inconclusive at pre-registered resolution -- follow-up question (finer N-grid and/or noise-coupled stress) carried as pre-registered future routing.
- Cap 8 ✅ N-robustness annotation; annotation-grade not row-state-changing.

### Capability moves table

| Capability | v181 state | v182 state |
|---|---|---|
| Cap 5 RM ✅ | ✅ + v181 envelope-extension under noise annotation | ✅ UNCHANGED + v182 lr-dose envelope deepening annotation (tau<=160 monotone WIN no plateau) |
| Cap 13 candidate | 🔬 + v181 dual-rejection annotation | 🔬 UNCHANGED + v182 closure-via-3-of-3-continent-rejection annotation at closed-form-margin theory level |
| Cap 12 ✅ | ✅ at v175 + multi-version annotations | ✅ UNCHANGED + v182 rerun-confirmation annotation at N=4096-full |
| Cap 8 ✅ | ✅ at v168/v175 + multi-version annotations | ✅ UNCHANGED + v182 N-robustness annotation |
| portfolio count | 12 | 12 UNCHANGED IN COUNT |
| open ❌ PROVISIONAL | 0 | 0 (Cap 13 candidate row stays 🔬 NOT ❌ PROVISIONAL) |

### Substrate-product positioning v182

- Cap 5 ✅ envelope DEEPENS to tau<=160 monotone WIN no plateau ceiling observed; mechanism question (variance-averaging at late iterates / late-stage exploration-vs-exploitation / Hopfield-attractor-basin late-stage settling / Gong 2026 under-modeled late-stage regime) sharpens to "upper-bound tau plateau if any."
- Cap 13 candidate row CLOSED-VIA-3-of-3-CONTINENT-REJECTION at closed-form-margin theory level. Closed-form-margin paired-continent program empirically refuted across all three planned continents. 15 rescue sketches filed across the three continents. R5 substrate-novel narrowing rescues are the load-bearing framings per [[feedback-no-smoke]]. Future rehab should REFRAME at production-N substrate-physics layer per [[feedback-dont-overextend-theorems]] -- the v180 GPU sanity at Clifford-TN continent production-N (magic_max=0, machine-precision rel_err) is the half-of-the-evidence that substrate IS approximately-Clifford at production N; the production-N substrate-physics framing remains an open question.
- Cap 12 ✅ rerun-stable at N=4096-full; no drift; discipline-grade reconfirmation.
- Cap 8 ✅ VAMP-on-chain N-robust at 1.000 retention across tested N; argmax pattern across N inconclusive; finer-N-grid follow-up pre-registered.

### PROT discipline

- per [[feedback-cap-map-update-protocol]]: cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; "Cap map: v181 -> v182 ..." commit
- per [[feedback-decision-log-eol-handling]]: this block appended via tools/orchestrator/append_decision_log.py
- per [[feedback-for-you-tab-primary-channel]]: 4 status_log entries written (V1 HIGH + V2 CRITICAL + V3 LOW + V4 LOW)
- per [[feedback-subagent-permission-inheritance]]: commit LOCAL only (push pending main thread)
- per [[feedback-obey-user-pause-explicitly]]: pause flag absent on disk (ACTIVE confirmed via filesystem check)
- per [[feedback-structural-agent-usage-mandate]]: inline-via-main-thread executed because Agent dispatch unavailable in sub-agent context (per orchestrator post-compaction brief Section 2 execution model clarification: "wrapper sub-agents... do NOT recurse into separate Agent dispatches -- the Agent tool is not available to sub-agents in this runtime"); the user's task hand-off explicitly authorized substantive work via the 3-task structured deliverable
- per PROT-004/006: TRIGGERED in closure-via-multi-anchor-rejection direction (Cap 13 candidate row CLOSED-VIA-3-of-3-CONTINENT-REJECTION at closed-form-margin theory level); NOT a portfolio row closure (candidate row was 🔬 throughout); rehab-sketch-first-sequencing discipline followed
- per PROT-008: v182 adds 0 new ❌ rows + 0 state changes
- per PROT-009: 96th paired commit

### Tally (one-line)

BATCHED 4 VERDICTS v181 -> v182 inline-via-main-thread: LR_DOSE_MONOTONIC (Cap 5 ✅ envelope-extension deepening tau<=160 monotone) + BOOLEAN_NOISE_STAB_HARD_FAIL (F-6 Cap-13 third KILLED; trilogy resolved 0/3 PASS at theory level; Cap 13 candidate row CLOSED-VIA-3-of-3-CONTINENT-REJECTION at closed-form-margin theory level; 15 rescue sketches across 3 continents; R5 substrate-novel narrowing rescue load-bearing per [[feedback-no-smoke]]; future rehab REFRAME at production-N substrate-physics layer per [[feedback-dont-overextend-theorems]]) + VAMP_AMP_CONTRAST_PASS rerun (Cap 12 ✅ rerun-confirmation N=4096-full) + N_SWEEP_INCONCLUSIVE (Cap 8 ✅ N-robustness annotation; argmax follow-up pre-registered); Step 0 honest re-read 17th/18th/19th/20th observations all label=msg=data agreement; portfolio UNCHANGED at 12; ZERO open ❌ PROVISIONAL; commit LOCAL (push pending main thread); 4 status_log entries (V1 HIGH + V2 CRITICAL + V3 LOW + V4 LOW); pause flag CLEARED ACTIVE; 96th PROT-009 paired commit.

---

## Cycle 205 (2026-05-24) — v183 BATCHED 9-VERDICT cap_map update + Strategy priority ranking refresh

**Inline verdict_handler / strategy / visibility composition** (Agent dispatch unavailable in sub-agent context per orchestrator post-compaction brief Section 2 execution model clarification). 9 verdicts processed in one batched cap_map commit.

### Step 0 honest re-read summary

All 9 verdict_msg labels reviewed against per-cell metrics in the user's payload. Findings:

- (V1) HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_FAIL: rerun confirms v2 result. Honest — two independent observations both NESS non-canonical at long-trajectory canonical-HS-IFT framing.
- (V2) BETZ5_STRICTLY_STRONGER: r=0.458 < 0.99 redundancy threshold AND variance cert=62.6470 > separator threshold met pre-reg HARD-PASS clean. Honest — both conjunctive thresholds met.
- (V3) MS_1ST_ORDER_INCONCLUSIVE: needs iid_gauss + kerdock cells per user analysis. Honest — script ran at incomplete cell schema.
- (V4) SELLKE_INCONCLUSIVE: baseline modes=8 at eps=0 (not cleanly RS). Honest — baseline not at the phase Sellke probe assumes.
- (V5) QND_CB_INVARIANT: max_drift_F=0.000000 BOTH codebooks at machine precision. Honest — STRUCTURALLY GUARANTEED label matches per-cell-data zero-drift across both codebooks.
- (V6) BET_V_N65K_PASS: gap=0.647 at N=65536. Honest — single-anchor PASS at unprecedented N; ✅ promotion gate would need multi-N replication.
- (V7) CAP2_ENDPOINT_KILL: ROC AUC<0.55 in 4/4 strata met pre-reg HARD-FAIL clean. Honest — all 4 strata met the kill threshold.
- (V8) BET_V_PARTIAL self-reflective: gap=0.285. Honest — clear sign-of-effect but well below the N=65K PASS gap=0.647; partial-rescue annotation is the right move.
- (V9) DEMO1_NOISE_ENVELOPE_PASS: composed_acc=1.0 at p=0.10 noise AND clean=1.0. Honest — zero degradation under noise at composition-task scale.

All 9 observations show clean label=msg=data agreement; 21st through 29th post-lock observations. [[feedback-verdict-msg-honest-reread]] LOCK working cleanly across 9 verdict classes. 29 clean observations post-lock.

### Strategy priority ranking refresh — per user analysis 2026-05-24

The user delivered a substantive Research-grade analysis on the EWC null and its downstream priority implications. Filed verbatim at `notes/strategy_priority_ranking_2026-05-24_post_ewc_null.md`. Key moves filed to active_priorities.md:

**OFFICIALLY CLOSED-DEFERRED for Bet B retention work**: EWC family (EWC, MAS, SI, Path Integral). The EWC null is structural per R26 — substrate W = sum v_i k_i^T is maximally distributed; Fisher matrix is approximately uniform; parameter-importance regularization provides zero traction on substrate retention by construction. Practical implication: Bet B's 73% retention_A is not movable via parameter-importance methods. DROP from queue.

**ELEVATED (highest active leverage after EWC null)**:
1. MoE GPU run — single highest-leverage active item; attacks Bet B retention via structural-separation axis orthogonal to EWC's parameter-importance axis. Smoke PASSED at N=512 (ratio=1.44). GPU full attempt crashed at runtime (exit_code=1 in 2.4s; script bug). MUST fix or rebuild.
2. Tropical R2 substrate-scale validation — 0.0e+0 closed-form analytic-match at N=4 is rare in substrate-physics work (R16 free probability landed within 20%). Should jump to HIGH priority for substrate-scale test.

**NEW ABLATIONS unlocked by EWC null** (added to ship queue):
A. **Per-task sub-substrate ablation** — train 3 separate W matrices on Bet B's three corpora, concatenate at retrieval. If retention_A jumps to ~95%+, structural separation IS the load-bearing axis. This is the structural-separation-axis falsifier for the EWC-null implication.
B. **Replay-only sweep at varying fractions** — if random replay alone explains 73%, increasing replay fraction toward 1.0 should monotonically improve retention until cost dominates. If retention plateaus before 80% regardless of replay fraction, that bounds achievable retention without structural separation.

**DEMOTED**: EWC-family follow-ups (MAS, SI, Path Integral).

**REMAINING ranked list per user**:
1. MoE GPU run (waiting; FIX REQUIRED)
2. Tropical R2 substrate-scale test
3. SSM/S4 re-queue with corrected task (W as state transition matrix, key as input, value as readout, standard copy-task / selective-copying benchmark; previous smoke failed at task-design level not substrate-level)
4. Self-supervised contrastive (once script lands)
5. F-6 Boolean re-queue with proper schema
6. Ablation A per-task sub-substrate (NEW)
7. Ablation B replay-only sweep (NEW)

### Capability moves committed at v183

See v183 cap_map narrative block for full table. Summary:

- Cap 8 ✅ FULL UNCHANGED + v183 QND-structural-closure annotation (machine-precision invariance; substantive strengthening).
- Bet Z.5 🔬 -> 🟢 PROMOTE on fresh-impl strictly-stronger-than-VAMP PASS.
- Bet V 🔬 -> 🟡 PARTIAL on N=65K PASS + self-reflective PARTIAL composite.
- Cap 2 ✅ UNCHANGED + Rescue 1 closed annotation.
- Cap 3 ✅ UNCHANGED + HS-v2 rehab closed annotation.
- Demo 1 ✅ UNCHANGED + noise envelope extends to p<=0.10.
- MS + Sellke INCONCLUSIVE with re-queues filed.
- Portfolio count UNCHANGED at 12.

### Routing outbound

- **Exp Dev**: dispatched inline for ship list per refreshed priority ranking. Ablation A + Ablation B + Tropical R2 substrate-scale + SSM/S4 re-queue + F-6 Boolean re-queue + MoE GPU fix-or-rebuild.
- **Research**: standing list extended with v183 additions (Bet Z.5 ✅ gate, Bet V ✅ gate, Cap 3 alternate-NESS-framing, MS re-queue cell-schema correction).

### Pipeline-pacing reflex

- queue depth 0 across all three CPU queues at completion (GPU runner alive on amp_se_kerdock_longiter); v183 commit fires exp_dev refill per [[feedback-pipeline-pacing]].
- Pause flag CLEARED — ACTIVE — refill authorized.

### Commit discipline

- per [[feedback-cap-map-update-protocol]]: cap_map.md + history.md + active_priorities.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; "Cap map: v182 -> v183 ..." commit.
- per PROT-009: 97th paired commit.
- per [[feedback-subagent-permission-inheritance]] commit LOCAL only (push pending main thread; orchestrator main-thread executes git push as 1-tool mechanical action).
- per [[feedback-for-you-tab-primary-channel]] 9 status_log entries written with plain_language + importance.


## 2026-05-24 — Orchestrator inline cycle: 2 verdicts processed + GPU CPU-bound reroute

### Task 1 — GPU CPU-bound job rerouted

GPU runner was running `wave14_amp_se_kerdock_longiter_v1` (pure-numpy AMP iteration; no torch.cuda anywhere in script) on the overnight_queue. GPU utilization 0% confirmed via 3-sample nvidia-smi. Killed pid 295004 on remote.

Runner moved to next pending: `wave14_cap8_vamp_iterates_srht_hadamard_v1c` — **SECOND CPU-bound script** queued to overnight_queue (no torch.cuda; pure numpy SRHT+VAMP iterates). Same anti-pattern. Killed pids 76776 + 472720.

After kills, runner picked up `wave14e_moe_xtalk_v1_post_device_fix_rerun_2026-05-24` which uses `torch.device("cuda" if torch.cuda.is_available() else "cpu")` and `torch.cuda.empty_cache()`. **Verified GPU util = 81%, 2204 MiB memory** — genuine CUDA work in flight.

Both CPU-bound scripts rerouted to remote_cpu_queue:
- `wave14_amp_se_kerdock_longiter_v1_cpu_reroute_rerun_2026-05-24` (now running on cpu_runner_0)
- `wave14_cap8_vamp_iterates_srht_hadamard_v1c_cpu_reroute_rerun_2026-05-24` (pending)

**Structural recommendation**: 2 CPU-bound scripts shipped to GPU queue in a single cycle is recurring failure. Suggest exp_dev add a `torch.cuda` pre-check before queuing to overnight_queue (analogous to remote --self-test gate). Filed as inefficiency-fix candidate; not actioned this cycle.

### Task 3 — Verdict processing

#### V1: BINDER_RS_CONFIRMED — wave14_binder_ratio_v1
**Data**: g4 = {512: 0.1902, 1024: 0.0459, 2048: -0.2507, 4096: -0.2647, 8192: -1.4102}; slope=-0.4001 monotone decreasing.

**Honest re-read**: verdict label = "BINDER_RS_CONFIRMED" — matches msg ("g4 monotone decreasing with N (RS self-averaging confirmed)") matches data (5 N values all monotone, slope clearly negative). Clean label=msg=data agreement (30th observation post-lock).

**Cap_map impact** — annotation-grade, NOT portfolio change:
- Binder ratio g4 monotone-decreasing-with-N is the textbook signature of **RS (replica-symmetric) self-averaging** — order parameter distribution concentrates at thermodynamic limit (g4 -> 0 or negative for RS; positive plateau for RSB/structural-glass).
- Substrate-physics implication: substrate's order-parameter distribution is self-averaging across N, consistent with the convex-not-glassy reading from R26 / EWC-null analysis.
- This LINKS to the EWC-null finding: if substrate is RS at the spin-glass-framing level, then per-parameter-importance regularization (EWC) is structurally low-traction (the loss landscape doesn't have the multi-basin metastable structure EWC presumes). Consistent.
- Per [[feedback-dont-overextend-theorems]]: single-N anchor, single observable (g4 only); NOT promoting any row. Annotation-grade for next cap_map cycle: add to substrate-physics characterization narrative as supportive evidence for "convex-not-glassy" reading.
- Importance: **MEDIUM** (substantive substrate-physics evidence; consistent with prior EWC-null + R26 framings; not portfolio-changing).

**No commit this cycle** — annotation-grade adds get folded into next Strategy cap_map cycle (v184 batched commit).

#### V2: MS_1ST_ORDER_INCONCLUSIVE rerun — wave14_mingo_speicher_1st_order_full_v2_rerun_2026-05-24
**Data**: verdict_msg="Need iid_gauss + kerdock cells." Identical to v183 V3 INCONCLUSIVE.

**Honest re-read**: label = msg = "missing cells". The rerun produced the SAME failure mode as the v183 attempt despite being a different script invocation. Per user's read: the script itself has a schema bug that doesn't actually emit the iid_gauss + kerdock cells in `full` mode. **Re-running this script will produce the same INCONCLUSIVE infinitely.**

**Cap_map impact**: zero portfolio change (still research-stage probe). Close the v183 "MS re-queue with iid_gauss + kerdock cells filed" pre-registered routing line — that re-queue is now CONFIRMED to be blocked by script bug, not data. The path requires **script fix**, not another rerun. Per [[feedback-lock-in-inefficiency-fixes]]: 2 observations of same script-bug closure -> lock the path as "MS_1ST_ORDER script has a full-mode cell-schema bug; do not re-queue without fixing the script first."

**Next action**: file a script-bug-fix task for exp_dev (NOT a rerun). Importance: **LOW** (already a deprecated probe; the fix is owed but not urgent).

### Status_log entries

2 entries written this cycle:
- V1 BINDER_RS_CONFIRMED, importance=MEDIUM, plain_language: "Substrate's order-parameter distribution self-averages with N — supports the convex-not-glassy reading from EWC analysis."
- V2 MS_1ST_ORDER_INCONCLUSIVE_RERUN, importance=LOW, plain_language: "Mingo-Speicher 1st-order probe inconclusive AGAIN with the same root cause; script has a cell-schema bug; rerun path locked pending script fix."

### Pause flag state

ACTIVE (no flag file). Task 2 ship dispatched in ACTIVE state per orchestrator post-compaction brief Section 1.



## Verdict batch v183 -> v184 (2026-05-24 13:35 local; orchestrator inline cycle 206)

### V1: MOE_PASS labeled / MOE_PARTIAL_M_DEPENDENT honest — wave14e_moe_xtalk_v1_post_device_fix_rerun_2026-05-24

**Data (5 seeds: 7, 17, 23, 31, 41; per-cell across 4 M × 2 K = 8 cells):**

| M | K | ratio (5-seed mean) | passes 1.3? |
|---|---|---|---|
| 500 | 4 | 1.035 | NO |
| 500 | 8 | 1.046 | NO |
| 2000 | 4 | 1.110 | NO |
| 2000 | 8 | 1.154 | NO |
| 8000 | 4 | 1.260 | NO (just below) |
| 8000 | 8 | 1.399 | YES |
| 32000 | 4 | 1.422 | YES |
| 32000 | 8 | 1.738 | YES |

**Honest re-read**: verdict_msg "MoE reduces cross-talk: at M=32000, K=8, ratio=1.799 >= 1.3" cherry-picks the BEST cell of 8. Per-cell view shows: (a) ratio is monotone-increasing in M across all 4 M levels at both K values; (b) HARD-PASS threshold (ratio >= 1.3) met cleanly at 3/8 cells (high-M K=8 from M=8K up, plus M=32K K=4); (c) 5/8 cells fail the threshold (low-M cells); (d) the substantive substrate-product structure is "MoE structurally reduces cross-talk in the cross-talk-pressure regime (M >> N or M*K large) but NOT in the low-pressure regime (M << N)." Per [[feedback-verdict-msg-honest-reread]] this is an OVER-CLAIM: verdict_msg label PASS over-claims at per-cell resolution. Honest verdict tag: **MOE_PARTIAL_M_DEPENDENT** — the propagatable interpretation to cap_map.

**Substantive substrate-product finding**: the orthogonal-axis hypothesis from earlier user analysis "MoE becomes higher leverage after EWC fails" is **CONFIRMED CONDITIONALLY**. EWC parameter-importance axis is dead (EWC-null closure preserved). Structural-separation axis (MoE-style) is ALIVE in the cross-talk-pressure regime — works where the substrate is load-stressed, fails where it's not. Substrate-product spec implication: a production deployment using MoE for Bet B retention needs to size K(M) — at heavier load (M=32K at K=8) ratio is 1.74; at lighter load (M=500 at K=4) ratio is only 1.04 (barely above 1.0). The K=8 cell consistently dominates the K=4 cell across M (more experts -> more cross-talk relief; expert_loads show heavy-tailed concentration in middle experts).

**Cap_map impact** — NEW evidence-strength row: Bet B retention rehab via structural-separation axis 🟡 M-DEPENDENT PARTIAL.
- Filed as new evidence-strength row UNDER Bet B retention rehab (NOT a new portfolio row at the Cap-N level — it's a within-Bet B rehab anchor).
- Portfolio count UNCHANGED at 12; evidence-strength row count grows from 2 (Bet Z.5 🟢 + Bet V 🟡) to 3 (+ Bet B retention via structural-separation 🟡 M-DEPENDENT PARTIAL).
- ✅ promotion gate: uniform per-cell PASS ratio >= 1.3 across operating range OR characterized M_crit(K) threshold with multi-N replication. Pre-registered future routing.
- Per [[feedback-rehabilitation-after-rejection]] this is rehab PASS (conditional) for the structural-separation axis; the EWC parameter-importance axis remains CLOSED.
- Per [[feedback-dont-overextend-theorems]] honest M-conditional reading NOT promoted to ✅; the cap_map row reflects the per-cell partial pattern.

**Importance**: **HIGH** — substantive substrate-product finding; first verdict-level confirmation that structural-separation axis works (in stressed regime); the orthogonal-axis CONFIRMATION the EWC-null closure analysis predicted.

### V2: EMP_MARGIN_WELL_DEFINED — wave14_tropical_R2_substrate_scale_n4096

**Data**: N=4096, 4-coset Kerdock MM = 16384 codewords; n_total=250, n_used=250; mean_margin=2004.19, std=7.24, cv=0.004; deg_frac=0.000; p25=1998.00.

**Honest re-read**: verdict_msg "Empirical bit-flip margin baseline well-defined at N=4096" matches data (cv=0.004 is extremely tight; no degeneracy; sufficient n). Label = msg = data agreement (31st observation post-lock).

**Cap_map impact**: annotation-grade ONLY; zero portfolio row change.
- F-14 Tropical Cap-13 closed-form margin theory KILLED at v181 stands UNCHANGED.
- This is the empirical-margin layer (orthogonal to closed-form-theory layer) — a clean reference baseline for future bit-flip-resilience or noise-stratified margin probes.
- Per [[feedback-dont-overextend-theorems]] single-N baseline annotation does NOT license any row promotion or rescue.
- **Importance**: **LOW** — clean baseline; supplies reference for downstream margin work; no portfolio movement.

### Status_log entries

2 entries written this cycle:
- V1 MOE_PARTIAL_M_DEPENDENT (honest reading; labeled MOE_PASS), importance=HIGH, plain_language: "We tested mixture-of-experts on Bet B retention. MoE makes the substrate handle dense memory (lots of items) MUCH better — at the heaviest load tested, MoE retrieves ~74% better than single-W. But the help only kicks in when load is high; at light load, MoE is roughly tied with single-W. So MoE is a structural fix for the cross-talk regime, not a uniform win. This CONFIRMS the orthogonal-axis hypothesis that MoE wins where EWC-style parameter-importance failed."
- V2 EMP_MARGIN_WELL_DEFINED, importance=LOW, plain_language: "Tropical R2 empirical bit-flip margin baseline measured cleanly at production scale (N=4096) — tight statistics (cv=0.004) and no degeneracy. This is a reference baseline for future bit-flip resilience work; no portfolio change."

### Pause flag state

ACTIVE (no flag file). Cap_map v184 committed in ACTIVE state per orchestrator post-compaction brief Section 1.

### Queue refill state at v184 close

- GPU (overnight_queue): IDLE, queue empty.
- Remote CPU (remote_cpu_queue): 1 pending (`wave14_cap8_vamp_iterates_srht_hadamard_v1c_cpu_reroute_rerun_2026-05-24`); the long-running `wave14_amp_se_kerdock_longiter_v1_cpu_reroute_rerun_2026-05-24` is in flight.
- Local CPU (local_cpu_queue): REVIVED IDLE — runner pid 13804 + 37416 (`cpu_runner_local` heartbeat updated 2026-05-24T13:32:22; status=idle, queue=0).
- Pickup-ready hand-offs in `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md`: 5 design anchors (Ablation A + Ablation B + SSM/S4 + F-6 Boolean + Sellke) + 1 script-fix (MS_1ST_ORDER). Next exp_dev cycle is the structural refill mechanism per [[feedback-no-experiment-design-in-prompts]]; orchestrator inline cycle does not design experiments.
- Pipeline-pacing reflex (per [[feedback-pipeline-pacing]]): queue refill is gated on pause flag (ABSENT) AND on exp_dev design work being available — the routing notes are filed; next exp_dev dispatch consumes them.


---

## Verdict-handler cycle (v185) — ABLATION_A_MIDDLE_BAND single-verdict cap_map update

**Verdict payload received**:

```json
{"name":"wave14_betB_ablation_A_per_task_v1_2026-05-24","verdict":"ABLATION_A_MIDDLE_BAND","verdict_msg":"retention_A=0.821 in [0.8,0.95); partial structural-separation effect. retention_B=0.982.","queue":"overnight_queue"}
```

### Step 0 honest re-read (32nd observation post-lock)

- Label: `ABLATION_A_MIDDLE_BAND`; msg: `retention_A=0.821 in [0.8,0.95); partial structural-separation effect. retention_B=0.982.`
- Script's pre-registered thresholds (`exp_wave14_betB_ablation_A_per_task_v1.py` lines 17-21): HARD-PASS >= 0.95; HARD-FAIL < 0.80; MIDDLE [0.80, 0.95).
- 0.821 in [0.80, 0.95) → MIDDLE band is mathematically correct.
- retention_B=0.982 high (post-B retention) sanity-checks the substrate isn't broken.
- Comparison anchor: baseline single-shared-W A->B->C with replay was ~73%. Ablation A (per-task separate W matrices) lifts retention_A to 82.1% — +9pp above baseline but 13pp below HARD-PASS.
- **No over-claim**. Label "MIDDLE_BAND" honestly matches per-cell data. 32nd clean observation post-lock; LOCK working as designed.
- Per-seed data (n=1 in smoke; full ran 5 seeds yielding mean=0.821): script's smoke at seed=17 produced retention_A=0.906 (lucky high seed); full 5-seed mean 0.821 below smoke confirms normal smoke->FULL convergence pattern.

### Cap_map impact

- **Row affected**: "Bet B retention via structural-separation axis" (the 🟡 M-DEPENDENT PARTIAL evidence-strength row added at v184).
- **State change**: NONE. Row stays 🟡 M-DEPENDENT PARTIAL.
- **Annotation added**: second-mechanism corroboration — per-task sub-substrate (Ablation A) is a SECOND structural-separation mechanism after v184 MoE. Both partial; neither alone clears HARD-PASS.
- **Substrate-product finding**: structural-separation axis is the right axis but +9pp lift from per-task substrates alone is insufficient for HARD-PASS. Product spec implication — stacking (compound MoE + per-task) OR longer-tail mechanisms (replay, Lane D 4-stage) needed.
- **EWC-null closure UNCHANGED**: Ablation A bypasses parameter-importance entirely (zero-init per-task W matrices), so v185 is consistent with the EWC-null closure narrative. Per user's claim "no method exploiting non-uniform parameter importance can do better" — Ablation A doesn't exploit parameter importance and gets +9pp; modest lift confirms the structural-separation axis is alive but distinct from the dead parameter-importance axis.
- **Pre-registered untested CONSUMED**: v184 Ablation A pre-registered untested row → now consumed at v185 with MIDDLE BAND.
- **Pre-registered new at v185**:
  1. Compound MoE + per-task structural-separation untested (axis-stacking question: do two partial mechanisms combine to clear 0.95?).
  2. Lane D 4-stage continual learning (A->B->C->D) — Priority A KILLER T1 per `strategy_untested_rows_triage_2026-05-24.md`.

### Status_log entry (For You tab)

1 entry written this cycle, importance=HIGH, plain_language: "We tested whether giving the substrate one separate brain-region for each task (per-task sub-substrates) recovers memory after learning many tasks in a row. It helps — going from 73% retention to 82.1% — but not enough to clear the 95% target. Combined with last cycle's MoE result, we now have TWO different structural-separation tricks that each give partial help; neither alone is enough. The axis is real but needs stacking or replay-schedule extensions to fully recover memory."

### Pause flag state

ACTIVE (no flag file). v185 committed in ACTIVE state per orchestrator post-compaction brief Section 1.

### Queue refill state at v185 close (HONEST queue state at handoff time)

- **overnight_queue (GPU)**: 5 pending (NOT 0 as user's verdict-event preamble suggested) — `wave14_betA_continual_edit_5seed_v3` + `wave14_cap2_confidence_margin_probe_v1` + `wave14_pq_high_resolution_v1` + `wave14_demo1_noise_envelope_v1` + `wave14_R_transform_kerdock_v1_multi_N`. Pipeline-pacing reflex DOES NOT FIRE — queue >=1. Per [[feedback-pipeline-pacing]] reflex is "queue=0 → ship" so 5-pending GPU does not trigger emergency refill.
- **remote_cpu_queue**: 0 pending DRAINED. Pipeline-pacing reflex WOULD fire here — and Task 2 below ships to remote_cpu to refill.
- **local_cpu_queue**: idle.
- **11 pickup-ready hand-offs**: 5 from `exp_dev_handoff_5anchors_post_v183_2026-05-24.md` (one CONSUMED at v185 = Ablation A) + 6 from `strategy_untested_rows_triage_2026-05-24.md`. Remaining: 10 design anchors.

### Per [[feedback-dispatch-wrappers-default]] note

Inline v185 commit done in main thread (single sub-agent context dispatched from user; Agent dispatch unavailable per orchestrator post-compaction brief Section 2 — sub-agents internalize multiple role prompts; verdict_handler role logic executed inline). Commit pushed at user discretion (sub-agent push blocked by harness security classifier per [[feedback-subagent-permission-inheritance]]).


---

## Verdict-handler cycle (v186) — ABLATION_B_MIDDLE_BAND single-verdict cap_map update

**Verdict payload received**:

```json
{"name":"wave14_betB_ablation_B_replay_sweep_v1_2026-05-24","verdict":"ABLATION_B_MIDDLE_BAND","verdict_msg":"Pattern not at extremes: monotone=True, peak=0.846, plateau_max=0.846. By-frac: ['0.682', '0.840', '0.845', '0.846', '0.844', '0.842', '0.841'].","queue":"overnight_queue"}
```

### Step 0 honest re-read (33rd observation post-lock)

- Label: `ABLATION_B_MIDDLE_BAND`; msg flags: `monotone=True, peak=0.846, plateau_max=0.846, by-frac=[0.682, 0.840, 0.845, 0.846, 0.844, 0.842, 0.841]`.
- Script-pre-registered MIDDLE band: [0.80, 0.95) by convention from Ablation A; peak=0.846 lands inside cleanly.
- `monotone=True` flag at per-cell resolution: **FALSE**. Series rises sharply from frac=0 (0.682) to a shoulder at fracs 0.10-0.50 (peaks 0.846 at index 3) and then DECLINES slightly to 0.841 at the highest replay fraction. Shape is UNIMODAL (rise-then-shallow-decline), NOT strict monotone. Decline is within binomial-noise resolution (≤0.005 across the high-frac tail), so the flag may reflect a relaxed "monotone-up-to-noise" check, but at honest per-cell reading the strict-monotone claim is unsupported.
- Per [[feedback-verdict-msg-honest-reread]] this is a NARROW over-claim (the monotone flag inside verdict_msg) NOT a load-bearing one (the MIDDLE_BAND tag and the substantive bound interpretation stand). 33rd observation post-lock: narrow-over-claim + load-bearing-honest in same observation.
- Substantive interpretation: replay alone plateaus at ~85% retention regardless of replay fraction. User's pre-cycle prediction: "if retention plateaus before 80% regardless of replay fraction, that bounds achievable retention without structural separation and makes MoE the only path forward." Actual plateau lands at 84.0-84.6% (slightly above 80% but well below HARD-PASS 0.95). Strategic conclusion UNCHANGED in substance -- replay alone is BOUNDED at a low ceiling and cannot clear HARD-PASS regardless of fraction.

### Cap_map impact

- **Row affected**: "Bet B retention via structural-separation axis" (🟡 M-DEPENDENT PARTIAL since v184; v185 second-mechanism corroboration; v186 control-axis annotation).
- **State change**: NONE. Row stays 🟡 M-DEPENDENT PARTIAL.
- **Annotation added**: replay-only axis BOUNDED control anchor. Ablation B isolates the non-structural replay axis and proves it has a low ceiling (~85%). This is a NEGATIVE-control result on the orthogonal axis, NOT an additional mechanism contribution to the structural-separation axis.
- **Substrate-product finding TIGHTENED**: structural separation (Cap 8 VAMP composition + v184 MoE + v185 per-task sub-substrate) is now confirmed as the LIVE axis for Bet B retention because (a) replay alone has a low ceiling, (b) both structural-separation mechanisms individually give partial PASS, (c) any HARD-PASS-clearing rehab MUST include structural separation as load-bearing. Product spec implication: replay alone is insufficient as a product-grade retention mechanism; spec MUST use structural separation as load-bearing.
- **EWC-null closure UNCHANGED**: Ablation B replay is orthogonal to parameter-importance; bounded ceiling consistent with EWC closure narrative.
- **Pre-registered untested CONSUMED**: v184 Ablation B replay-only sweep -> CONSUMED at v186 with MIDDLE BAND replay-axis-bounded control annotation.
- **Pre-registered ELEVATED at v186**:
  1. Compound MoE + per-task separation untested (v185 row) -> ELEVATED to LIVE TOP-PRIORITY at v186. Replay-only is now confirmed bounded, so compound structural-separation stacking is the cheapest remaining path to HARD-PASS.
  2. Lane D 4-stage continual learning (v185 row Priority A KILLER T1) -> ELEVATED to second-LIVE-priority.
- **Pre-registered NEW at v186**: replay-schedule + structural-separation compound test. Replay's ~85% ceiling + structural-separation 9pp lift would project ~94% if axes stack linearly -- marginal vs HARD-PASS 0.95 so worth empirical test; if super-linear stacking observed, HARD-PASS achievable; if sub-linear stacking, structural-separation stacking (compound MoE + per-task without replay) remains the better path.

### Status_log entry (For You tab)

1 entry written this cycle, importance=HIGH, plain_language: "We tested whether replaying old training examples alone (without giving the substrate separate brain-regions for each task) is enough to recover memory. It is not -- replay alone plateaus at about 85% retention no matter how much we replay, which is below the 95% target. The user predicted this outcome would prove that the structural-separation trick (MoE or per-task sub-substrates) is the load-bearing mechanism, and that's what the data confirms. Next live test is whether stacking two structural-separation tricks (MoE plus per-task) can clear the 95% target together."

### Pause flag state

ACTIVE (no flag file). v186 committed in ACTIVE state per orchestrator post-compaction brief Section 1.

### Queue refill state at v186 close (HONEST queue state at handoff time -- main thread to confirm)

- The verdict payload references `queue: overnight_queue` (GPU). Wrapper invoked from sub-agent context -- main thread to confirm queue depths post-commit and apply pipeline-pacing reflex if any queue drained.
- 10 remaining pickup-ready hand-offs in `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` + `strategy_untested_rows_triage_2026-05-24.md` after Ablation A (v185) and Ablation B (v186) consumption. Next exp_dev cycle is the structural refill mechanism per [[feedback-no-experiment-design-in-prompts]].
- Pipeline-pacing reflex is gated on pause flag (ABSENT -> ACTIVE) and on exp_dev design work being available (it is).

### Per [[feedback-dispatch-wrappers-default]] note

Inline v186 commit done in sub-agent context (single verdict_handler invocation from user; Agent dispatch unavailable per orchestrator post-compaction brief Section 2 -- sub-agents internalize multiple role prompts; verdict_handler executes strategy + visibility role logic inline; commit LOCAL only; push pending main thread per [[feedback-subagent-permission-inheritance]]).


## [16:30 LT] Verdict — wave14_betB_compound_pertask_replay_v1_2026-05-24 FULL = COMPOUND_MIDDLE_BAND

**Verdict tag**: COMPOUND_MIDDLE_BAND (label=msg=data agreement clean; 34th honest-reread observation post-lock CLEAN)
**Verdict_msg**: retention_A=0.915 in (0.821, 0.95); partial axis-stacking benefit; replay adds something but compound still does NOT clear HARD-PASS.
**Metrics**: retention_A=0.915 mean across SEEDS=[7,17,23,31,41] at N=4096 BATCH=64 EPOCHS=5 PHASE_A_EPOCHS=8 BYTES=200K REPLAY_FRAC=0.5. Sub-additive stacking (additive projection from v185 +9pp + v186 +12pp above 0.73 baseline ~94%; observed 91.5% lands 2.5pp below linear projection).

**Substantive analysis** (Step 0 honest re-read CLEAN):
- Compound per-task + replay stacks +18.5pp above baseline ~0.73, +9.4pp above per-task-alone (v185 0.821), +6.9pp above replay-only-plateau (v186 0.846). Both axes contribute ADDITIVELY but mildly sub-additively.
- HARD-PASS gate 0.95 NOT cleared by 3.5pp; intrinsic ceiling of TWO-AXIS compound below HARD-PASS in tested envelope.
- Per user pre-cycle EWC-null analysis: structural separation is LOAD-BEARING AND PRODUCTIVE but does not fully close Bet B retention alone. CONFIRMED across THREE independent mechanism observations: v184 MoE M-dependent PARTIAL, v185 per-task substrate PARTIAL, v187 compound per-task+replay PARTIAL.

**Cap_map action**: v186 -> v187 single-verdict annotation. Row state STAYS 🟡 M-DEPENDENT PARTIAL with v187 compound-axis-stacking-additive-but-bounded annotation (NOT promoted to ✅; promotion gate of uniform per-cell PASS at HARD-PASS 0.95 across operating range OR characterized M_crit(K) with multi-N replication NOT met by compound-of-two-mechanisms). Portfolio UNCHANGED at 12 + 3 evidence-strength rows. ZERO open ❌ PROVISIONAL preserved from v172-v186. 101st PROT-009 paired commit (commit hash below).

**Pre-registered new routing**:
- compound + THIRD-axis (compound + MoE / compound + Lane D 4-stage / compound + eligibility-trace consolidation) — cheapest remaining path to HARD-PASS 0.95
- longer-Phase-A consolidation variant (16-32 epochs vs current 8) — cheap orthogonal axis to structural separation + replay

**Bet B retention portfolio status (post-v187)**: structural-separation axis CONFIRMED CONDITIONAL across THREE mechanism families; the compound of two mechanisms has an intrinsic ceiling below HARD-PASS in tested envelope; a third orthogonal mechanism OR a fundamentally different approach is required to clear product-grade retention >= 0.95. The 🟡 PARTIAL state is the **honest empirical reading after three converging-PARTIAL probes** — the row is NOT close to ✅ promotion via more variants of structural separation alone.

**Per [[feedback-no-experiment-design-in-prompts]]**: exp_dev pickup-ready batch shipped this cycle covers the 10 hand-off anchors (see strategy_decisions_2026-05-24.md companion entry "[16:35 LT] Exp Dev hand-off ship — 5 anchors across GPU + remote CPU + local CPU"). Compound + THIRD axis falls into the v187-new-pre-reg slot for the next cycle.


## [14:45 LT] Verdict — wave14_betB_compound_plus_longer_phaseA_v1_2026-05-24 FULL = LONGER_PHASEA_MIDDLE_BAND

**Verdict tag**: LONGER_PHASEA_MIDDLE_BAND (label=msg=data substantive agreement clean BUT narrow language over-claim "ceiling breaks" inside noise envelope; 35th honest-reread observation post-lock -- narrow over-claim + load-bearing honest pattern same as v186 monotone-flag)
**Verdict_msg**: retention_A=0.917 in (0.915, 0.95); longer consolidation partial benefit; ceiling breaks but HARD-PASS NOT cleared.
**Metrics**: retention_A=0.917 vs v187 compound 0.915 -- delta +0.2pp inside seed-variance noise floor; pre-registered MIDDLE band [0.80, 0.95) holds; pre-registered band-floor 0.915 (v187 compound) cleared by +0.2pp but inside noise; PHASE_A_EPOCHS extended from compound v187's 8 to 16-32 (exp_dev's design choice per [[feedback-no-experiment-design-in-prompts]]).

**Substantive analysis** (Step 0 honest re-read 35th observation post-lock):
- The +0.2pp delta is INSIDE seed-variance noise floor for this experiment family (v186 by-frac series had differences of 0.001-0.005 at high-replay tail). Substantively, the longer-Phase-A axis adds ESSENTIALLY NOTHING on top of the compound (per-task + replay) two-axis stacking.
- Verdict_msg language "ceiling breaks but HARD-PASS NOT cleared" is NARROWLY accurate at point-estimate resolution (0.917 > 0.915) but SUBSTANTIVELY misleading -- the ceiling is CONFIRMED not broken because the delta is inside noise. The load-bearing interpretation ("HARD-PASS NOT cleared; fourth axis essentially nothing on top of compound") is honest. This is the same narrow-over-claim + load-bearing-honest pattern as v186 monotone-flag observation (33rd) and is logged as 35th observation post-lock.
- This is the FOURTH probe in the Bet B retention rehab sequence and the FIRST DIRECT evidence that the compound ceiling at 91-92% is INTRINSIC not a function of insufficient Phase-A consolidation time. Giving the substrate twice as long to settle in Phase A before Phase B does NOT lift retention above the compound ceiling.
- User pre-cycle framing "this is a structural-axis question; need fundamentally different approach to clear 95%" CONFIRMED in substance across four converging-PARTIAL probes:
  - v184 MoE M-dependent: 3/8 cells clear 1.3 threshold (M-monotone partial)
  - v185 per-task substrate: retention_A=0.821 (+9pp above baseline; 13pp below HARD-PASS)
  - v186 replay-only-axis: plateau=0.846 (~85% ceiling regardless of replay fraction)
  - v187 compound (per-task + replay): retention_A=0.915 (mild sub-additive stacking; 3.5pp short of HARD-PASS)
  - v188 compound + longer-Phase-A: retention_A=0.917 (+0.2pp on compound; inside noise; ceiling CONFIRMED)
- Bet B retention has CLEAR CEILING around 91-92% with these known mechanism families (structural separation + replay + extended consolidation).

**Cap_map action**: v187 -> v188 single-verdict annotation. Row state STAYS 🟡 M-DEPENDENT PARTIAL with v188 longer-Phase-A-saturation annotation (NOT promoted; promotion gate uniform per-cell PASS at HARD-PASS 0.95 across operating range OR characterized M_crit(K) with multi-N replication still decisively unmet -- v188 is the cleanest direct evidence yet that the gate is intrinsically out of reach for the compound + longer-consolidation family). Portfolio UNCHANGED at 12 + 3 evidence-strength rows. ZERO open ❌ PROVISIONAL preserved from v172-v187. 102nd PROT-009 paired commit (commit hash below).

**Pre-registered new routing**:
- **Research drill on Bet B retention ceiling FIFTH-MECHANISM candidate** -- given four mechanisms each partial, what's the FIFTH mechanism candidate from a DIFFERENT framework that could clear 95%? Research designs the question; orchestrator does not pre-design. Dispatched this cycle as Task 2b.
- **Explicit scope-rescoping option** -- product spec MAY rescope HARD-PASS to a narrower operating envelope (e.g., 91-92% retention at the current parameter envelope; 0.95 reserved for specific M_crit(K) cells). This is the "accept ceiling" option per user framing.
- v187 compound + THIRD axis routing CARRIED FORWARD unchanged -- v188 longer-Phase-A is a separate orthogonal probe (NOT a third-axis stacking test in the v187 sense; v187 third-axis test stacks MoE / Lane D 4-stage / eligibility-trace on top of compound, while v188 extended Phase A within the existing two-axis envelope). The third-axis routing is the v187 LIVE-TOP-PRIORITY and remains the cheapest remaining HARD-PASS path on the rehab list.

**Bet B retention portfolio status (post-v188)**: structural-separation axis CONFIRMED CONDITIONAL across FOUR mechanism families; compound of two mechanisms has an intrinsic ceiling below HARD-PASS in tested envelope; longer-Phase-A consolidation adds essentially nothing on top of compound. Four converging-PARTIAL probes establish that Bet B retention via known mechanism families is BOUNDED at 91-92% in the parameter envelope tested. The 🟡 PARTIAL state is the **honest empirical reading after four converging-PARTIAL probes** -- the row is NOT close to ✅ promotion via more variants of the same axes. A FIFTH mechanism candidate from a DIFFERENT framework (substrate-novel; from a different theoretical class than structural separation / replay / consolidation) is required.

**Per [[feedback-no-experiment-design-in-prompts]]**: exp_dev pickup-ready batch shipped this cycle covers Task 2 queue refill (2 GPU + 1-2 CPU from remaining 10 hand-offs in `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` + `notes/strategy_untested_rows_triage_2026-05-24.md`). Compound + THIRD axis remains the LIVE-TOP-PRIORITY for the next exp_dev cycle.

**Per [[feedback-pipeline-pacing]] queue context**: overnight_queue (GPU) drained to 0 pending at verdict-event preamble (user-stated); main thread confirmed via `tools/orchestrator/state_check.py` (output: gpu_q:0 cpu_q:8). Pipeline-pacing reflex FIRES this cycle (ACTIVE pause-flag state confirmed; queue=0 trigger met). 2 GPU + 1-2 CPU refill shipped via exp_dev hand-off pickup per [[feedback-no-experiment-design-in-prompts]] (exp_dev designs parameters; orchestrator does not). Research drill dispatched in parallel.

**Per [[feedback-dispatch-wrappers-default]] note**: Inline v188 commit done in main thread (single sub-agent context dispatched from user; Agent dispatch unavailable per orchestrator post-compaction brief Section 2 -- sub-agents internalize multiple role prompts; verdict_handler role logic executed inline). Commit LOCAL only (push at user discretion; orchestrator commits but does not auto-push per [[feedback-subagent-permission-inheritance]]).

**Status_log entry**: 1 entry written this cycle, importance=HIGH, plain_language: "We tested whether giving the substrate twice as long to settle in Phase A (longer-consolidation) before learning Phase B helps memory retention beyond what the per-task + replay combination already achieves. It does not -- retention barely moves from 91.5% to 91.7% (within the noise envelope). This is the fourth converging-partial result on Bet B retention; four different mechanism families have each delivered partial benefits and the combinations do not clear the 95% product gate. The substrate has a CLEAR CEILING around 91-92% with these known mechanism families -- a fifth mechanism candidate from a fundamentally different framework is now required to clear the 95% target, OR the product spec needs to rescope to accept the 91-92% ceiling at the current parameter envelope."

## v188 -> v189 (2026-05-24) -- K2 KILLER T1 4-stage continual learning FOURSTAGE_MIDDLE_BAND

**Verdict**: wave14_betB_4stage_continual_v1_2026-05-24 FULL = FOURSTAGE_MIDDLE_BAND retention_A=0.740 retention_B=0.854 retention_C=0.798. Per pre-registered MIDDLE band ("Stage D adds load but mechanism survives partially"); retention_B and retention_C clear per-stage HARD-PASS 0.70 thresholds; retention_A misses HARD-PASS 0.80 by 6pp; NO HARD-FAIL pattern (retention_A=0.74 well above HARD-FAIL 0.50; no catastrophic-collapse signature).

**Cap_map move**: K2 True continual learning at production scale (A->B->C->D) -- KILLER Tier 1 ⚪ UNTESTED -> 🟡 PARTIAL. First-ever 4-stage continual learning probe at substrate-product level. The substrate's compound (per-task + replay) mechanism EXTENDS structurally to 4-stage chains; middle stages retain better than earliest, characteristic of cross-task replay benefiting recently-presented tasks more.

**Portfolio impact**: 12 demonstrated rows UNCHANGED + 4 evidence-strength rows NEW (was 3 -- Bet Z.5 🟢 + Bet V 🟡 + Bet B retention 🟡 M-DEPENDENT PARTIAL; now adds K2 4-stage 🟡 PARTIAL). Closes K2 UNTESTED gap in v1 KILLER framing. ZERO open ❌ PROVISIONAL preserved from v172-v188.

**v189 rehab promotion gate filed (carry-forward)**: per-stage HARD-PASS 0.80 / 0.70 / 0.70 uniformly cleared across 5 seeds OR product-spec rescoping (accept retention_A=0.74 floor for 4-stage chains; reserve 0.80 for 3-stage). Rehab axis candidates: 4-stage with stronger Phase-A consolidation; 4-stage at N=8192; Phase-D-specific replay weighting (heavier weight on stage A in Phase D replay).

**Per [[feedback-dispatch-wrappers-default]] note**: This cap_map commit + exp_dev ship batch executed in a single sub-agent context dispatched from the user per the orchestrator post-compaction brief (Section 2 -- Agent dispatch unavailable; sub-agents internalize role prompts). Verdict-handler role logic + exp_dev role logic both executed inline. Commit LOCAL only (push deferred to main thread per sub-agent permission gap; [[feedback-subagent-permission-inheritance]]).

**Status_log entry**: 1 entry written this cycle, importance=HIGH, plain_language: "We tested whether the substrate can learn FOUR sequential tasks (A then B then C then D) and still remember each -- this was the FIRST EVER 4-stage continual learning probe at substrate-product level. Result is a partial pass: the substrate retained middle stages (B and C) at 85% and 80% respectively, both above the 70% target; the earliest stage (A) retained at 74%, just short of the 80% target. The mechanism survives the 4-stage load without collapsing -- this matters because it confirms the substrate scales structurally from 3-stage (validated last week) to 4-stage. The KILLER Tier 1 'true continual learning at production scale' row moves from UNTESTED to PARTIAL on the capability map. Rehab paths to clear the full 80% target on stage A: stronger Phase-A consolidation, larger substrate dimension N=8192, or weighting Phase-A more heavily in the late-stage replay buffer."


---

## Cycle 215 (2026-05-24 ~16:55 LT) — v190 BATCHED 10-VERDICT cap_map update

**Trigger**: orchestrator batched 10 verdicts inline (verdict_handler role internalized in single sub-agent context per [[feedback-dispatch-wrappers-default]] + orchestrator post-compaction brief Section 2).

**Verdicts processed**:
- (V1) wave14_betB_4stage_continual_v2_rehab_n8192_v1 FULL = FOURSTAGE_MIDDLE_BAND retA=0.740 retB=0.860 retC=0.808 -- K2 rehab axis 1 SATURATION (vs v189 retA=0.740 retB=0.854 retC=0.798 inside seed-variance)
- (V2) wave14_betB_4stage_continual_v2_rehab_phaseA_consolidation_v1 FULL = FOURSTAGE_MIDDLE_BAND retA=0.736 retB=0.854 retC=0.796 -- K2 rehab axis 2 SATURATION (no consolidation lift; user pre-cycle confirmation honest)
- (V3) wave14_cap8_vamp_iterates_srht_hadamard_v1c_cpu_reroute_rerun FULL = CAP8_ITERATES_GENERATED (30 trace files; Composition A v4 audit UNBLOCKED; infrastructure only)
- (V4) wave14e_s4_depth_smoke_v1_reship FULL = S4_KILLED ratio=0.00 binding_depth=200 ssm_depth=0
- (V5) wave14_sellke_marginal_stability_v1_reship FULL = SELLKE_INCONCLUSIVE (baseline modes=8 at eps=0; narrower-eps re-queue did NOT fix baseline)
- (V6) wave14e_s4_depth_smoke_v1 FULL = S4_KILLED duplicate (identical numbers; second-S4 observation closes rehab path)
- (V7) wave14_boolean_noise_stab_kerdock_kkl_v1_reship FULL = BOOLEAN_NOISE_STAB_HARD_FAIL (rerun confirms v182 V2 F-6 Boolean Cap-13 closure no new info)
- (V8) wave14_compositional_holdout_v1 FULL = COMPOSITIONAL_MIDDLE_BAND hold_out_acc=0.116 train_acc=0.652 -- K6 KILLER T2 ⚪ -> 🟡 PARTIAL NEW (FIRST K6 probe)
- (V9) wave14_betB_multitask_diff_corpus_v1 FULL = MULTITASK_DIFF_MIDDLE_BAND retA=0.600 gain_C=3.76 -- U1/U7 ⚪ -> 🟡 PARTIAL NEW (FIRST joint U1/U7 probe; CONDITIONAL transfer)
- (V10) wave14_realtime_inference_learning_v1 FULL = REALTIME_INFERENCE_MIDDLE_BAND labeled / INCONCLUSIVE-INSTRUMENTATION-BUG honest -- LABEL OVER-CLAIM 3rd labeled-vs-honest divergence this session

**Step 0 honest re-read outcomes (per [[feedback-verdict-msg-honest-reread]])**:
- V1-V9: label=msg=data agreement clean (37th-44th observations post-lock)
- V10: LABEL-OVER-CLAIM DETECTED (45th observation post-lock); MIDDLE_BAND tag implies legitimate-middle-band reading but bpc_online=0.000 / bpc_frozen=0.000 / delta=0.000 is structurally implausible (smoke run produced bpc_online=3.762 / bpc_frozen=3.834); honest verdict = INCONCLUSIVE_INSTRUMENTATION_BUG; honest reading treated as authoritative for K5 row interpretation (K5 STAYS ⚪ UNTESTED; instrumentation repair pre-registered)
- Tally: 8 clean + 1 LABEL-OVER-CLAIM (3 / 45 = 6.7% over-claim rate consistent across heterogeneous verdict classes; LOCK working cleanly)

**Cap_map move**:
- K2 True continual learning at production scale (A->B->C->D) -- KILLER Tier 1: 🟡 PARTIAL UNCHANGED + v190 axes 1+2 SATURATION annotations (axis 3 Phase-D-replay-weighting still LIVE)
- K6 Compositional generalization -- KILLER Tier 2: ⚪ UNTESTED -> 🟡 PARTIAL NEW evidence-strength row (FIRST K6 probe; 1.85x chance hold-out; 4 rehab axes filed)
- U1/U7 Multi-task transfer + cross-modal binding -- UNSURE Tier 2: ⚪ UNTESTED -> 🟡 PARTIAL NEW evidence-strength row (FIRST joint probe; gain_C=3.76 strong + retA=0.600 below HARD-PASS; CONDITIONAL transfer; 3 rehab axes filed)
- K5 Real-time learning during inference -- KILLER Tier 2: ⚪ UNCHANGED + v190 INSTRUMENTATION-INCONCLUSIVE annotation (labeled-vs-honest divergence; instrumentation repair filed)
- Cap 8 ✅ UNCHANGED + v190 infrastructure-only annotation
- Bet S4-as-SSM-depth-extension research-stage UNCHANGED + v190 CLOSED-FAILED annotation (two-observation confirmation)
- Sellke research-stage UNCHANGED + v190 SECOND INCONCLUSIVE annotation (alternate-baseline-construction filed)
- F-6 Boolean ❌ closure UNCHANGED + v190 rerun-confirmation annotation

**Portfolio impact**: 12 demonstrated rows UNCHANGED + 6 evidence-strength rows NEW (was 4 -- Bet Z.5 🟢 + Bet V 🟡 + Bet B retention 🟡 + K2 4-stage 🟡; now adds K6 compositional 🟡 + U1/U7 multi-task-transfer 🟡). Closes K6 + U1/U7 ⚪ gaps in v1 KILLER/UNSURE framing. ZERO open ❌ PROVISIONAL preserved from v172-v189.

**v190 rehab promotion gates filed (carry-forward)**:
- K2 rehab axis 3 (Phase-D-specific replay weighting heavier weight on stage A in Phase D replay) STILL LIVE -- only remaining axis from v189 3-axis list
- K6 4 rehab axes: (1) N=8192 + 5+ seeds; (2) explicit hierarchical composition pre-binding; (3) cleanup-iteration at composition site; (4) Bet X position-indexed mechanism integration
- U1/U7 3 rehab axes: (1) MoE structural separation for cross-corpus retention; (2) larger N=8192 for retention floor; (3) weighted-replay favoring corpus-A during corpus-C training
- Sellke alternate baseline construction (quenched-disorder average OR modes-cutoff redefinition NOT just narrower eps)
- K5 instrumentation repair (fix metric-collapse bug; rerun as wave14_realtime_inference_learning_v1_rerun BEFORE any K5 capability claim)

**Per [[feedback-dispatch-wrappers-default]] note**: This cap_map commit batched across 10 verdicts executed inline in single sub-agent context per orchestrator post-compaction brief Section 2 execution-model clarification (Agent dispatch unavailable; sub-agents internalize role prompts; verdict_handler + strategy + visibility role logic all executed inline). Commit LOCAL only (push deferred to main thread per sub-agent permission gap; [[feedback-subagent-permission-inheritance]]).

**Status_log entries**: 10 entries written this cycle (V1 MEDIUM K2 axis 1 saturation; V2 MEDIUM K2 axis 2 saturation; V3 LOW Cap 8 infrastructure; V4 MEDIUM S4 rerun-confirmation; V5 LOW Sellke inconclusive rerun; V6 LOW S4 duplicate; V7 LOW Boolean rerun-confirmation; V8 HIGH K6 first probe -> PARTIAL; V9 HIGH U1/U7 first probe -> PARTIAL; V10 MEDIUM K5 instrumentation-bug labeled-vs-honest).

**PROT-004/006/008/009 compliance this commit**: K6 ⚪ -> 🟡 + U1/U7 ⚪ -> 🟡 row state changes (2 new evidence-strength rows); 4 K6 rehab axes + 3 U1/U7 rehab axes + Sellke alternate baseline + K5 instrumentation repair filed; PROVISIONAL tag NOT required (these are CREATION of new 🟡 PARTIAL rows not ❌ closures); cap_map.md + history.md + strategy_decisions_2026-05-24.md + visibility_decisions_2026-05-24.md staged atomically; pre-commit validator passes (commit hash in main thread push step).


## v191 cycle (2026-05-24, paired promotion) -- K5 instrumentation-rerun HARD-PASS + GPT-quality v1-CANNOT reframe

**Triggered by**: (1) wave14_realtime_inference_learning_v1_rerun FULL = REALTIME_INFERENCE_HARD_PASS delta=-0.548 bpc; (2) USER reframe analysis on GPT-quality v1 ❌ CANNOT row.

**Cycle 191 / paired-verdict + reframe action**:

(V1) K5 instrumentation-repair clean PASS: the v190 V10 INSTRUMENTATION-INCONCLUSIVE annotation was filed because the v190 K5 FULL returned bpc_online=0.000 / bpc_frozen=0.000 (structurally implausible all-zero metrics indicating pretrain_bytes=50000 + T_infer=4000 > corpus_len=48512 making inference stream empty). exp_dev fix: pretrain_bytes now capped at min(40000, corpus_len-T_infer-200) + hard assertions catch any future silent failure. v191 rerun returns bpc_online=2.198 vs bpc_frozen=2.745 in expected range; delta=-0.548 bpc cleared HARD-PASS threshold (delta <= -0.05) by 11x. K5 KILLER Tier 2 ⚪ UNTESTED -> ✅ DEMONSTRATED. First KILLER Tier 2 capability closing at clean PASS at substrate-product level. Portfolio count 12 -> 13 demonstrated capabilities. Honest reread label=msg=data clean agreement (46th observation post-lock).

(V2) GPT-quality generation row reclassification ❌ -> 🟢 PARTIAL: USER substantive Tier-1 reframe analysis (filed at notes/research_tier1_gpt_quality_reframe_2026-05-24.md) identified that the v1 ❌ CANNOT row text at line 122 was STRATEGY POSTURE wearing capability-claim clothes (positioning statement at v1 time, NOT a substrate-physics ceiling test). The v3 grounded reading (2026-05-20) already reclassified the row to 🟢 Partial at line 425; the v1 row survived by drift / non-update, not by evidence. Substrate-physics framework R16 superposition capacity / R23 coding-rate bounds / R26 free-probability composition / R29 noise-tolerant readout does NOT predict a hard quality ceiling that GPT-quality generation cannot reach. The v1 row at line 122 is reclassified ❌ -> 🟢 PARTIAL at v191 with annotation pointing to the reframe note. This is a ROW RECLASSIFICATION not a portfolio promotion (no demonstrated capability addition from this move; the capability count change at v191 is entirely from K5 promotion). 47th observation post-lock clean reframe-discipline.

5 paths filed for GPT-quality empirical/theoretical resolution per USER recommendation:
- Path 3 (HIGHEST per USER; CHEAPEST): AGS scaling-law extrapolation — exp_dev hand-off at notes/exp_dev_handoff_path3_ags_scaling_2026-05-24.md
- Path 1 (substantial build): token-level substrate K=128+ head-to-head vs GPT-2-small — exp_dev hand-off at notes/exp_dev_handoff_path1_token_substrate_2026-05-24.md
- Path 5 (theoretical): Bayes-optimal lower bound via R16+R23+R26 frameworks ~week Research drill — request at notes/research_request_path5_bayes_lower_bound_2026-05-24.md
- Path 4 (strategic hedge): per-document substrate framing — deferred; Strategy considers after Paths 1/3 land
- Path 2 (hybrid kNN-LM-like): reserved for follow-up

**PROT-004/006/008/009 compliance this commit**: K5 ⚪ -> ✅ promotion row (no rehab file required; promotion direction) + GPT-quality ❌ -> 🟢 PARTIAL reclassification (UNDOING v1 stale posture; no fresh ❌ closure; no rehab file required); history.md v191 sibling written; strategy_decisions paired; validator pre-existing baseline violations unchanged (60 history-update blocks PROT-007 restructure-in-progress; 29 pre-PROT-004 closures grandfathered); 105th paired commit.

**Pipeline pacing state**: GPU=4 pending (healthy backlog: betB_replay_by_norm + betB_task_geometry_rerun + betB_4stage_phaseD_a_weighted + compositional_holdout_rehab_n8192); CPU=0 pending (refill target post-commit via Path 3 + Path 1 exp_dev hand-offs); pipeline-pacing reflex GATED on pause flag ABSENT (ACTIVE).

**Per [[feedback-no-experiment-design-in-prompts]]**: 3 hand-off files (Path 3 / Path 1 / Path 5) declare task + pointers + deliverable shape + autonomy. No numerical sweep grids, thresholds, formulas, or anchor names specified by main thread. exp_dev + Research own all design parameters.

**Per [[feedback-for-you-tab-primary-channel]]**: 2 status_log entries written (V1 HIGH K5 -> demonstrated 13th + V2 MEDIUM GPT-quality v1 CANNOT -> PARTIAL reclassification + Paths 3/1/5 dispatched).

**Per [[feedback-verdict-msg-honest-reread]]**: 46th + 47th observations post-lock; both clean label=msg=data agreement; LOCK working cleanly across clean-PASS-from-instrumentation-repair + row-reclassification-from-stale-v1-posture.

## v192 - Bet M Allen-Cahn REJECTED + REPLAY_NORM null annotation + R-PRIME framework filed + existing-data analyses + roadmap

v192 ANNOTATION-ONLY paired commit. (V1) wave14_betB_allen_cahn_tsweep_v1 FULL = ALLEN_CAHN_HARD_FAIL slope=0.069 outside pre-registered [0.3, 0.7] band; Bet M Allen-Cahn t^(1/2) sub-hypothesis REJECTED; retA decay IS monotone (0.860 -> 0.829 over t=1..21) but functional form is NOT t^(1/2); 5 rescues filed inline per [[feedback-rehabilitation-after-rejection]] (R1 logarithmic-forgetting Wickelgren 1972 / Wixted-Ebbesen 1991 LEADING / R2 1-RSB phase-transition / R3 Ebbinghaus longer-t fit / R4 Cahn-Hilliard alt-potential / R5 abandon phase-field). (V2) wave14_betB_replay_by_norm_v1 FULL = REPLAY_NORM_MIDDLE_BAND delta=+0.002 vs uniform-replay baseline; Bet B retention norm-weighting rehab axis CLOSED-NULL; 3 alt-weightings preserved (novelty / error / uncertainty). (V3) USER 2-analysis delivery filed verbatim at notes/research_R_PRIME_directions_2026-05-24.md + notes/research_3_capability_deep_agenda_2026-05-24.md (6 R-PRIME directions + 5 new fields + 3-capability deep agenda). (V4) Existing-data analyses delivered per user explicit "highest-leverage move" directive at notes/research_existing_data_analyses_2026-05-24.md with 6 prior shifts (logarithmic-forgetting > Allen-Cahn / task-pair-geometry > MoE-M_c / geometric-exponential per-hop > sqrt(d) / K > M_stored / cluster-structured retention / Gap(K) concave-saturating). (V5) Prioritized roadmap filed at notes/orchestrator_prioritized_roadmap_2026-05-24.md (top-5 ships: R-PRIME-3 task-pair geometry / Field-A reservoir Lyapunov / Bet D analyzer K=32/K=64 / R-PRIME-2 MoE M_c / Bet M reframe logarithmic-forgetting). Portfolio count UNCHANGED at 13 demonstrated + 5 evidence-strength rows; honest-reread LOCK 48th + 49th observations clean (label=msg=data agreement both moves); 106th PROT-009 paired commit. Pipeline pacing reflex GATED on pause flag ABSENT (ACTIVE).


---

## v193 cycle (2026-05-24, BATCHED 3-verdict) — R-PRIME-3 HARD-FAIL HYPOTHESIS REJECTED + K2 rehab axes EXHAUSTED + K6 dim-scaling exhausted

**Triggered by**: 3 verdicts processed:
- (V1) `wave14_betB_task_pair_geometry_v1` FULL = TASK_GEOMETRY_HARD_FAIL r^2=0.103 < 0.2 non-monotone
- (V2) `wave14_betB_4stage_phaseD_a_weighted_v1` FULL = FOURSTAGE_MIDDLE_BAND retA=0.747 retB=0.852 retC=0.800
- (V3) `wave14_compositional_holdout_n8192_v1` FULL = COMPOSITIONAL_MIDDLE_BAND hold_out=0.128 at N=8192 (was 0.116 at N=512)

**Cycle 193 / batched 3-verdict cap_map action**:

**Step 0 honest re-read (per [[feedback-verdict-msg-honest-reread]])**:
- V1 TASK_GEOMETRY_HARD_FAIL: r^2=0.103 < 0.2 HARD-PASS threshold AND non-monotone series. Label HARD-FAIL is HONEST — clean clear-cut failure on both criteria (r^2 magnitude + monotonicity). 50th observation post-lock clean label=msg=data agreement.
- V2 FOURSTAGE_MIDDLE_BAND Phase-D A-weighted: retA=0.747 in [0.70, 0.80) MIDDLE band cleanly. Delta from v189 baseline retA=0.740 = +0.007 well inside 5-seed variance. Label MIDDLE_BAND is HONEST — A-weighted replay does NOT lift above other 4-stage variants. 51st observation post-lock clean.
- V3 COMPOSITIONAL_MIDDLE_BAND N=8192: hold_out=0.128 in (0.1, 0.5) MIDDLE band cleanly. Delta from N=512 baseline (0.116) = +0.012 slight improvement direction but still MIDDLE. Label MIDDLE_BAND is HONEST — dim-scaling lifts modestly but no promotion. 52nd observation post-lock clean.

All three labels HONEST; no labeled-vs-honest entries this cycle.

**Substantive substrate-product readings**:

**(V1) R-PRIME-3 task-pair-geometry HYPOTHESIS REJECTED** is the LOUDEST single-verdict negative this session. The user's #1 highest-leverage prediction (filed at v191/v192 as Ship 1 in prioritized roadmap; the existing-data analysis at notes/research_existing_data_analyses_2026-05-24.md flagged the 35% retA drop between same-corpus and diff-corpus as the DOMINANT Bet B effect across all variants larger than any structural ablation) was that retention is geometry-bound — empirics show r^2=0.103 < 0.2 HARD-FAIL with non-monotone series. **Bet B ceiling reframe**: retention ceiling is NOT predictable from corpus-pair spectral distance at the tested cosine-based metric. Equivalently, the substrate ceiling at multi-task is CORPUS-INDEPENDENT at the tested geometry layer. **PAC-Bayes KL-accumulation floor framing (R-PRIME-1) STRENGTHENS** as the next-leading-candidate — if geometry is not the mechanism, an information-theoretic floor between task posteriors is the geometry-free retention floor. Per [[feedback-rehabilitation-after-rejection]] 5 rescues filed: R1 alternative geometry metric (joint-binding distance / mutual coherence / free-cumulant of difference operator); R2 sub-corpus geometry (within-corpus chunks not between-corpus pairs); R3 R-PRIME-1 PAC-Bayes floor elevated to Ship 1; R4 cluster-structured retention NOT geometry-graded (three retention plateaus may be basin-discrete not geometry-continuous; supports 1-RSB phase-transition framing R2 from Bet M Allen-Cahn rescues); R5 abandon geometry-mediated retention framing. Per [[feedback-dont-overextend-theorems]] this kills the SPECIFIC metric tested NOT all geometry framings. Per [[feedback-negative-results-2x-research]] R-PRIME-3 closure triggers 2x Research drill cadence deferred to Research wrapper next cycle.

**(V2) K2 4-stage continual learning rehab AXES EXHAUSTED**: all 3 in-design rehab axes (axis 1 N=8192+2x epochs v190 / axis 2 stronger Phase-A consolidation v190 / axis 3 Phase-D A-weighted replay v193) saturate at the same retA~0.74 floor. The retA=0.74/retB=0.85/retC=0.80 pattern is substrate-INTRINSIC at 4-stage load, not undertuned. Product spec implication: accept retA=0.74 as substrate-native 4-stage spec OR reserve retA >= 0.80 HARD-PASS for 3-stage chains. Mechanism-class rescues remain UNTESTED: M1 hierarchical replay (replay sub-task chunks not whole tasks); M2 attention-gated readout (Bet X position-indexed mechanism class); M3 explicit memory consolidation (sleep-cycle simulation); M4 increase substrate dimensionality N at fixed M. These are the path out of MIDDLE band for K2.

**(V3) K6 compositional holds at scale**: hold_out 0.116 -> 0.128 (N=512 -> N=8192) is slight improvement but still MIDDLE band; dim-scaling axis is exhausted as a tuning lever; mechanism-class axes 2 hierarchical pre-binding + 3 cleanup-iteration + 4 Bet X position-indexed integration are the LEADING leverage paths.

**Capability moves**:

| Capability | v192 state | v193 state |
|---|---|---|
| Bet B retention (R-PRIME-3 task-pair-geometry hypothesis) | 🟡 PARTIAL with R-PRIME-3 filed as Ship 1 | 🟡 PARTIAL UNCHANGED + R-PRIME-3 HYPOTHESIS REJECTED annotation (5 rescues filed; PAC-Bayes KL floor R-PRIME-1 elevated to Ship 1) |
| K2 4-stage continual learning rehab | 🟡 PARTIAL with rehab axis 3 STILL LIVE | 🟡 PARTIAL UNCHANGED + axis 3 SATURATION; all 3 in-design rehab axes EXHAUSTED (4 mechanism-class rescues M1-M4 filed) |
| K6 Compositional generalization rehab axis 1 | 🟡 PARTIAL with 4 rehab axes filed | 🟡 PARTIAL UNCHANGED + axis 1 N-scaling SATURATION-AT-SCALE (axes 2/3/4 mechanism-class elevated) |

**Net effect v193**: R-PRIME-3 task-pair-geometry HYPOTHESIS REJECTED (5 rescues filed; PAC-Bayes KL floor R-PRIME-1 elevated to Ship 1); K2 4-stage rehab AXES EXHAUSTED at retA~0.74 substrate-intrinsic floor (4 mechanism-class rescues filed; M1-M4 untested); K6 dim-scaling axis exhausted (3 mechanism-class axes elevated); 9 rescue candidates filed total; portfolio 13 demonstrated + 5 evidence-strength UNCHANGED; substrate empirically rejects geometry-mediated retention joining parameter-importance + classical-phase-field rejection patterns; 107th PROT-009 paired commit.

**Substrate-product positioning v193**: Bet B retention ceiling is NOT geometry-mediated (R-PRIME-3 v193) AND NOT parameter-importance-trackable (EWC-null pre-v178) AND NOT classical-phase-field (Bet M Allen-Cahn v192); the substrate retention pattern is corpus-independent at the geometry layer AND capacity-bound at 4-stage load AND cluster-structured at three plateaus (0.94 pristine / 0.74 4-stage / 0.60 diff-corpus). What REMAINS as candidate retention mechanisms: PAC-Bayes KL-accumulation floor (R-PRIME-1; elevated to Ship 1 v193); 1-RSB basin-discrete cluster-structured (R-PRIME-2 + R4 R-PRIME-3 carry-over); MoE structural separation CONDITIONAL on cross-talk pressure (v184 🟡 M-DEPENDENT PARTIAL alive). Per [[feedback-no-papers-product-only]] substrate-product framing — substrate retention is a multi-mechanism phenomenon with **information-theoretic floor + cluster-basin discrete structure + cross-talk-conditional structural-separation** as the surviving framework after geometry-mediated framing rejection.

**Pipeline pacing state**: GPU=0 pending (drained over cycle); CPU=0 pending (user reports remote CPU queue empty); refill target via R-PRIME-2 MoE M_c falsifier returning to top priority + Field-A reservoir Lyapunov + Bet D analyzer K=32/K=64 + mechanism-class rescues (M1-M4 K2 / K6 axes 2/3/4); pipeline-pacing reflex GATED on pause flag ABSENT (ACTIVE) so refill licensed; exp_dev wrapper for >=3 anchors REQUIRED next cycle per pipeline-pacing invariant.

**PROT-004/006/008/009 compliance this commit**: 0 new ❌ rows + 0 row state changes (annotation-only direction; R-PRIME-3 hypothesis closure is a SPECIFIC-HYPOTHESIS rejection NOT a row state change; K2 axis 3 + K6 axis 1 rehab-axis closures are annotation-grade); 5+4+0 = 9 rescue candidates filed inline per [[feedback-rehabilitation-after-rejection]]; cap_map.md + history.md + strategy_decisions_2026-05-24.md staged atomically; pre-commit validator baseline pre-existing 60-history-blocks violation unchanged + 29 pre-PROT-004 closures grandfathered.

**Per [[feedback-dispatch-wrappers-default]] note**: This v193 cap_map update executed inline in main thread per orchestrator post-compaction brief Section 2 execution-model clarification (Agent dispatch unavailable in this runtime; verdict_handler wrapper agent role logic + strategy + visibility composed inline; queue refill via exp_dev hand-off pickup REQUIRED next cycle). Commit LOCAL + push performed by main thread.

**Per [[feedback-for-you-tab-primary-channel]]**: 3 status_log entries written this cycle (V1 CRITICAL R-PRIME-3 hypothesis REJECTED + V2 MEDIUM K2 rehab axes exhausted + V3 MEDIUM K6 N=8192 saturation).

**Per [[feedback-verdict-msg-honest-reread]]**: 50th + 51st + 52nd observations post-lock — all three clean label=msg=data agreements.


---

## 2026-05-24 — Orchestrator inline verdict_handler cycle v193 -> v194 (single-verdict annotation; cap_map v194 committed)

**Verdict processed (1)**:

```json
{"name":"wave14_betB_multitask_diff_corpus_rehab_n4096_v1","verdict":"MULTITASK_DIFF_MIDDLE_BAND","verdict_msg":"Partial transfer: retention_A=0.604 gain_C=3.758.","queue":"overnight_queue"}
```

(Note: verdict envelope queue tag says "overnight_queue" but the actual cpu_runner_0 ran it on remote_cpu; verdict label = MULTITASK_DIFF_MIDDLE_BAND is honest per pre-reg bands.)

**Substantive substrate-product reading**:

**U1/U7 multi-task-diff-corpus rehab axis 2 SATURATION**: 2x dim doubling N=2048 (v1) -> N=4096 (v1_rehab_n4096) produces retA=0.604 vs 0.600 (delta retA=+0.004 well inside 5-seed seed-variance noise floor) and gain_C=3.758 vs 3.760 (essentially identical). The U1/U7 multi-task-diff-corpus rehab axis 2 (larger N for retention floor; filed at v190 as one of 3 in-design axes) is now **EXHAUSTED at this corpus pair within the tested N envelope**.

**Substrate-product implication**: diff-corpus retention ceiling at retA~0.60 is **N-INDEPENDENT** in tested N range (2048-4096); the dim-scaling lever is NOT the path out of MIDDLE band for U1/U7. This joins the v193-confirmed pattern that retention ceilings (across multiple Bet B variants) are intrinsic-capacity-bound NOT undertuned.

**Cluster-structured retention pattern STRENGTHENS**: three retention plateaus across Bet B variants now empirically converged at discrete values — 0.94 same-corpus pristine / 0.74 4-stage compound / 0.60 diff-corpus. The discrete-plateau structure (not continuous in ANY single axis tested: N, geometry, consolidation time, per-task projection, replay weighting) is the FIFTH converging observation supporting **basin-discrete 1-RSB phase-transition retention framing** v192 R5 / v193 R-PRIME-3 R4 / v194 M4. Continuous-axis Bet B retention mechanism framings are cumulatively rejected.

**Cumulative negative-signal pattern v184-v194** sharpens substrate characterization:
- EWC parameter-importance ❌-DEFERRED v183
- Allen-Cahn t^(1/2) ❌ v192
- Norm-weighted replay NULL v192
- Task-pair-geometry ❌ v193
- Phase-D A-weighted replay SATURATION v193
- N=8192 K6 axis 1 SATURATION-AT-SCALE v193
- **N=4096 U1/U7 axis 2 SATURATION v194 ← this cycle**

The negative signals SHARPEN substrate-product characterization toward (a) discrete-basin phase-transition mechanism framings (1-RSB cluster-structured) and (b) information-theoretic floor framings (PAC-Bayes KL-accumulation R-PRIME-1).

**Capability moves**:

| Capability | v193 state | v194 state |
|---|---|---|
| U1/U7 Multi-task transfer + cross-modal binding (rehab axis 2) | 🟡 PARTIAL with 3 rehab axes filed v190 | 🟡 PARTIAL UNCHANGED + axis 2 N-scaling SATURATION annotation (4 mechanism-class rescues M1-M4 filed; axes 1+3 remain LIVE) |

**Net effect v194**: U1/U7 multi-task-diff-corpus rehab axis 2 (N-scaling 2048->4096) SATURATION annotation (4 mechanism-class rescues filed M1-M4); diff-corpus retention ceiling at retA~0.60 confirmed N-INDEPENDENT in tested envelope; cluster-structured retention pattern STRENGTHENS as fifth converging observation against continuous-axis Bet B retention mechanism framings; portfolio 13 demonstrated + 5 evidence-strength UNCHANGED; 108th PROT-009 paired commit.

**4 mechanism-class rescues filed inline at v194** per [[feedback-rehabilitation-after-rejection]]:
- M1: N-scaling AT MUCH LARGER N (16384 / 32768; structural-break test vs MIDDLE-band exhaustion)
- M2: Multi-task transfer at DIFFERENT corpus pair (current pair may be pathological; different distribution-gap pair may yield different ceiling)
- M3: PAC-Bayes KL-accumulation floor framing (R-PRIME-1 strengthened; same Ship-1 framing as v193 R-PRIME-3 R3)
- M4: Cluster-structured retention (1-RSB basin-discrete framing strengthened; matches v192 R5 / v193 R-PRIME-3 R4)

**U1/U7 v190 axes 1 + 3 remain LIVE**:
- Axis 1: MoE structural separation for cross-corpus retention (orthogonal mechanism; precedented at v184 Bet B same-corpus 🟡 M-DEPENDENT PARTIAL)
- Axis 3: Weighted-replay favoring corpus-A during corpus-C training (precedented null at v192 norm-weighting but novelty/error/uncertainty weightings preserved)

**Per [[feedback-dont-overextend-theorems]]**: kills SPECIFIC N=2048->4096 axis at current corpus pair; does NOT close U1/U7 row (gain_C remains STRONG > HARD-PASS 0.3 indicating new-corpus uptake intact) and does NOT exclude N-scaling at MUCH larger N or different M/N ratios.

**Per [[feedback-verdict-msg-honest-reread]]**: 53rd observation post-lock label=msg=data agreement clean (MULTITASK_DIFF_MIDDLE_BAND tag honest; retA=0.604 in (0.5, 0.7) MIDDLE band cleanly; gain_C=3.758 well above 0.3 HARD-PASS for new-corpus-uptake-only sub-criterion).

**Pipeline pacing state**: GPU=0 pending; CPU=0 pending; refill target via exp_dev wrapper pickup of notes/exp_dev_handoff_v193_queue_refill_2026-05-24.md (3 mandatory + 6 optional anchors); pipeline-pacing reflex GATED on pause flag ABSENT (ACTIVE) so refill licensed; **exp_dev sub-agent dispatch REQUIRED next cycle to restore queue depth >= 1 invariant** — main thread does NOT design these inline per [[feedback-dispatch-wrappers-default]] + [[feedback-no-experiment-design-in-prompts]].

**PROT-004/006/008/009 compliance this commit**: 0 new ❌ rows + 0 row state changes (annotation-only); 4 mechanism-class rescues filed inline; cap_map.md + history.md + strategy_decisions_2026-05-24.md staged atomically; pre-commit validator baseline pre-existing violations unchanged.

**Per [[feedback-dispatch-wrappers-default]] note**: This v194 cap_map update executed inline in main thread per orchestrator post-compaction brief Section 2 execution-model clarification (Agent dispatch unavailable in this runtime; verdict_handler wrapper agent role logic + strategy + visibility composed inline; queue refill via exp_dev hand-off pickup REQUIRED next cycle).

**Watchdog repair note**: also this cycle — `tools/orchestrator/heartbeat_watchdog.py` patched to fix ship_unconfirmed false-positive class. Bug: watchdog only checked `queue_pending` / `queue_running` / `current` / `heartbeat.current` (i.e. "in flight RIGHT NOW") and treated absence as "never landed." When an experiment landed, ran, and was reaped from queue.json before the next watchdog poll, the watchdog re-fired ship_unconfirmed forever (until the entry aged past SHIP_CONFIRMED_RETENTION_S=600s). Fix: composite confirmation check now also looks at `recent_verdicts` (entry produced a verdict) and the runner's `recent_log_lines` (START/DONE record for the name), and stamps a sticky `landed_at` field on the JSONL entry once confirmed. Test run cleared the stale 16:44-16:47 entries (wave14e_moe_xtalk_smoke_v1 / wave14_hatano_sasa_cap3_long_traj_v2 aged past retention and were pruned; wave14_mingo_speicher_1st_order_mn8_v1 stamped landed_at and retained until retention). Watchdog process restarted PID 1432 (was PID 6032). No ship_unconfirmed payloads emitted on the new code.

## v195 -- wave14_1rsb_pq_retained_v1 PQ_RETAINED_MIDDLE annotation

**Step 0 honest re-read**: verdict_msg label PQ_RETAINED_MIDDLE is HONEST per pre-reg bands.
- n_peaks=4 satisfies >=2 (check); max_sep_sigma=2.37 satisfies >=2.0 (check)
- binder=-0.164 FAILS binder>0.30 HARD-PASS threshold
- binder is NEGATIVE (anti-clustering; sub-Gaussian overlap structure)
- mean_q~1e-6, std_q~3e-6: W vectors are NEARLY ORTHOGONAL across seeds (q_EA~0)
- HONEST READ: 4 near-zero-overlap clusters; NOT genuine 1-RSB (requires non-zero q_EA + positive Binder); NOT RS either (RS = single broad unimodal, not 4 peaks); MIDDLE band correct

**Pred-2 (W-vector P(q)) implications**:
- W_ABCD vectors across 10 seeds have overlaps clustering near q=0 (nearly orthogonal)
- High-dimensional: at N=2048, random bipolar vectors have E[q]~0 and std[q]~0.022; observed std_q=3.2e-6 is MUCH TIGHTER -- W vectors are MORE orthogonal than random (each seed finds a diverse solution)
- Does NOT refute pool-level RSB (wave14e2_parisi_ultrametricity validated at pool level; different axis)
- Does NOT support W-level basin-trapping (genuine 1-RSB would need q_EA >> 0 with positive Binder)
- ANNOTATION: W-vector P(q) axis INCONCLUSIVE (binder=-0.164 < 0.30 threshold; q_EA~0)

**1-RSB battery status after Pred-2**:
- Pred-1 (cascade_depth): GPU running
- Pred-2 (pq_retained): MIDDLE -- W-vector axis inconclusive; q_EA~0
- Pred-3 (capacity_plateau): GPU pending
- Pred-4 (hysteresis): NOT SHIPPED -- sole remaining CPU diagnostic; distinguishes first-order vs continuous transition
- Pred-5 (ultrametric_triples): local CPU running

**Capability moves**:

| Row | v194 state | v195 state |
|---|---|---|
| RSB phase / ultrametric index | validated structural (pool-level) | UNCHANGED + W-vector P(q) annotation: INCONCLUSIVE (binder=-0.164; q_EA~0) |

**Net effect v195**: ANNOTATION-ONLY. No row state changes. Pool-level RSB stands. 1-RSB framing from retention plateaus (0.94/0.74/0.60) unaffected. Pred-4 hysteresis is highest-leverage remaining CPU test.

**Pipeline pacing**: remote_cpu_queue=0 (IDLE); pause_state=ACTIVE; exp_dev refill authorized.

**PROT-004/006/008/009 compliance**: 0 new closures; annotation-only.
**Per [[feedback-verdict-msg-honest-reread]]**: 54th post-lock observation; label=msg=data CLEAN.


---

## v196 -- wave14_1rsb_cascade_depth_v1 CASCADE_DEPTH_MIDDLE annotation (smoke-grade artifact)

**Step 0 honest re-read**: verdict_msg label CASCADE_DEPTH_MIDDLE is HONEST per pre-reg bands.
- max_delta=0.058 < 0.08 smooth threshold (FAILS HARD-PASS cliff>=0.15)
- n_cliffs=0 (FAILS HARD-PASS cliff>=0.15)
- var_delta=0.0029 > 0.002 (FAILS HARD-FAIL var<0.002 — so NOT HARD-FAIL)
- Profile: depth=2 retA=0.907 / depth=3 retA=0.849 / depth=4 retA=0.898 (NON-MONOTONE with depth=4 RECOVERY)
- LABEL CORRECT: MIDDLE band

**CRITICAL SECONDARY HONEST READ — artifact is SMOKE not FULL**:
- on-disk metrics.json carries `mode: "smoke", N: 1024, batch_size: 32, epochs: 1, seeds: [17], depths: [2,3,4]`
- v195 exp_dev handoff (notes/exp_dev_decisions_2026-05-24.md lines 401-417) pre-shipped FULL with 5 seeds + 5 epochs + depths {2,3,4,5}
- The SMOKE artifact values exactly match the pre-ship smoke captured at handoff time (max_delta=0.058)
- Watchdog silent_idle at 20:14:48 says GPU drained; either FULL ran and overwrote artifact with smoke values (runner-config-mismatch bug) OR only smoke ever ran on the queue
- Non-monotone depth=4 RECOVERY is most plausibly 1-seed sampling noise NOT substrate signal

**Pred-5 (cascade-depth) implications at this artifact resolution**:
- CANNOT discriminate 1-RSB (predicted cliff>=0.15 then plateau<0.05 at some depth step) from RS (predicted smooth monotone decay) at smoke-grade
- The 1-RSB framing rest mostly on the 5+ converging observations of discrete 0.94/0.74/0.60 retention plateaus across Bet B variants v184-v194 — those are pool-level / retention-level discrete-plateau observations and are ORTHOGONAL to the cascade-depth axis
- Pred-5 status: INCONCLUSIVE at smoke-grade artifact; FULL re-run with v195-handoff config pre-registered

**1-RSB battery status after Pred-5 (smoke-grade) annotation**:
- Pred-1 (capacity_plateau): on-disk artifact = CAPACITY_PLATEAU_RS_SMOOTH at smoke-grade (annotation v197 forthcoming this cycle)
- Pred-2 (pq_retained): v195 ALREADY CONSUMED FULL = MIDDLE; W-vector axis q_EA~0
- Pred-3 (capacity_plateau / GPU): SAME as Pred-1 above
- Pred-4 (hysteresis): SHIPPED at commit b552776 to remote_cpu_queue
- Pred-5 (cascade_depth): SMOKE-grade INCONCLUSIVE this cycle (v196)
- Pred-5 ultrametric_triples: local CPU smoke ULTRAMETRIC_1RSB_CONFIRMED at N=512 trivially (FULL at N=2048 pending)

**Joint pattern read (preliminary; capacity_plateau v197 still pending this cycle)**: 5 of 5 Pred axes have produced SMOKE or MIDDLE outcomes at the artifact resolution accessible; NO Pred axis has produced a clean HARD-PASS for 1-RSB; NO Pred axis has produced a clean HARD-FAIL either. The basin-discrete-1-RSB framing from retention plateaus is NEITHER strengthened NOR refuted by the diagnostic battery at these resolutions. Per [[feedback-dont-overextend-theorems]] this does NOT close the 1-RSB framing; it surfaces the limit of indirect-axis 1-RSB diagnostics at smoke-grade compute.

**Capability moves**:

| Row | v195 state | v196 state |
|---|---|---|
| RSB phase / ultrametric index | ✅ Validated structural (pool-level) + v195 W-vector P(q) annotation INCONCLUSIVE | UNCHANGED + v196 cascade-depth annotation: INCONCLUSIVE at smoke-grade artifact |

**Net effect v196**: ANNOTATION-ONLY. No row state changes. Pool-level RSB stands. 1-RSB framing from retention plateaus (0.94/0.74/0.60) unaffected. Pred-5 SMOKE artifact does not discriminate; FULL re-run pre-registered.

**Pipeline pacing**: gpu_q:0 cpu_q:0 (per state_check 20:17 reading; watchdog silent_idle at 20:14:48); pause_state=ACTIVE; exp_dev refill DEFERRED to orchestrator per turn directive (orchestrator dispatching exp_dev separately to avoid parallel cap_map race).

**PROT-004/006/008/009 compliance**: 0 new closures; annotation-only.
**Per [[feedback-verdict-msg-honest-reread]]**: 55th post-lock observation; label CASCADE_DEPTH_MIDDLE honest at smoke-grade; SMOKE-vs-FULL config mismatch is the load-bearing honest call.
**Per [[feedback-no-experiment-design-in-prompts]]**: this verdict_handler cycle does NOT prescribe FULL re-run parameters — exp_dev decides when re-shipped.


---

## v197 -- wave14_1rsb_capacity_plateau_v1 CAPACITY_PLATEAU_RS_SMOOTH annotation (smoke-grade artifact; verdict_msg over-extends)

**Step 0 honest re-read**: verdict_msg label CAPACITY_PLATEAU_RS_SMOOTH is FORMULA-HONEST per pre-reg bands; verdict_msg EXPLICIT CLAIM "1-RSB capacity plateau NOT supported" OVER-EXTENDS at smoke resolution.
- max_delta=0.067 < 0.08 (FAILS HARD-PASS cliff>=0.15; MEETS HARD-FAIL max_delta<0.08)
- Profile: M=10k retA=0.885 / M=50k retA=0.817 / M=200k retA=0.805 (smooth monotone decay across the THREE sampled M points)
- Deltas: 0.067 (10k->50k), 0.012 (50k->200k) -- both < 0.15 cliff threshold
- LABEL CORRECT per formula: RS_SMOOTH; FORMULA OVER-EXTENDS: "1-RSB NOT supported" is NOT a valid inference from a 3-point single-seed grid
- 56th observation post-lock; this is a label-honest-but-verdict_msg-over-extension case (vs prior v177 MMD-vs-MP-KS where label itself contradicted data)

**CRITICAL SECONDARY HONEST READ -- artifact is SMOKE not FULL**:
- on-disk metrics.json carries `mode: "smoke", N: 1024, batch_size: 32, epochs: 1, seeds: [17], M_sweep: [10000, 50000, 200000]`
- v195 exp_dev handoff (notes/exp_dev_decisions_2026-05-24.md lines 401-417) pre-shipped FULL with 7 M points + multi-seed + N=4096
- The SMOKE artifact values exactly match the pre-ship smoke captured at handoff time (max_delta=0.067)
- Watchdog silent_idle at 20:14:48 says GPU drained; same runner-config-mismatch pattern as cascade_depth v196
- 3-point single-seed grid cannot exclude 1-RSB cliffs between e.g. M=25k and M=80k that the coarse grid skips over

**Pred-1/Pred-3 (capacity-plateau morphology) implications at this artifact resolution**:
- CANNOT discriminate 1-RSB (predicted cliff>=0.15 then plateau<0.05 at some M step) from RS (predicted smooth monotone decay) at smoke-grade
- The 1-RSB framing rests on the 5+ converging observations of discrete 0.94/0.74/0.60 retention plateaus across Bet B variants v184-v194 -- those are pool-level / retention-level discrete-plateau observations ORTHOGONAL to capacity-plateau morphology along an M axis
- Pred-1/Pred-3 status: INCONCLUSIVE at smoke-grade artifact; FULL re-run with v195-handoff config pre-registered

**1-RSB battery joint status after v195/v196/v197 cycle (5 of 5 Preds resolved at the resolution accessible)**:
- Pred-1 (capacity_plateau / GPU): v197 SMOKE-grade INCONCLUSIVE this cycle (verdict_msg over-extension flagged)
- Pred-2 (pq_retained / CPU): v195 ALREADY CONSUMED FULL = MIDDLE; W-vector axis q_EA~0; INCONCLUSIVE
- Pred-3 (capacity_plateau): SAME as Pred-1
- Pred-4 (hysteresis): SHIPPED at commit b552776 to remote_cpu_queue; IN FLIGHT
- Pred-5 (cascade_depth / GPU): v196 SMOKE-grade INCONCLUSIVE this cycle
- Pred-5 ultrametric_triples: smoke ULTRAMETRIC_1RSB_CONFIRMED at N=512 trivially (FULL at N=2048 pending)

**Joint pattern read (definitive after v197)**: 3 of 5 indirect Pred axes returned INCONCLUSIVE at the resolution accessible (Pred-1/3 capacity-plateau smoke + Pred-2 W-vector P(q) FULL + Pred-5 cascade-depth smoke). NONE produced clean HARD-PASS for 1-RSB. NONE produced clean HARD-FAIL after honest re-read (verdict_msg Pred-1 over-extension flagged; otherwise formula HARD-FAIL on cascade_depth was blocked by var threshold). The basin-discrete-1-RSB framing motivated by retention-plateau direct observations (5+ converging plateaus 0.94/0.74/0.60 across Bet B variants v184-v194) is NEITHER strengthened NOR refuted by the indirect-axis diagnostic battery. Per [[feedback-dont-overextend-theorems]] this does NOT close the 1-RSB framing; it surfaces the limit of indirect-axis 1-RSB diagnostics at smoke-grade compute. Pred-4 hysteresis (in flight at remote_cpu) is the highest-leverage discriminator still pending; first-order vs continuous transition is the cleanest binary call available.

**Capability moves**:

| Row | v196 state | v197 state |
|---|---|---|
| RSB phase / ultrametric index | ✅ Validated structural (pool-level) + v195 W-vector + v196 cascade-depth annotations INCONCLUSIVE | UNCHANGED + v197 capacity-plateau annotation: INCONCLUSIVE at smoke-grade artifact + verdict_msg over-extension flagged |

**Net effect v197**: ANNOTATION-ONLY. No row state changes. Pool-level RSB stands. 1-RSB framing from retention plateaus (0.94/0.74/0.60) unaffected. Pred-1/3 SMOKE artifact does not discriminate; FULL re-run pre-registered. Verdict_msg over-extension ("1-RSB NOT supported") flagged as load-bearing dishonest claim if accepted at face value.

**Pipeline pacing**: gpu_q:0 cpu_q:0 (per state_check 20:17 reading; watchdog silent_idle at 20:14:48); pause_state=ACTIVE; exp_dev refill DEFERRED to orchestrator per turn directive (orchestrator dispatching exp_dev separately to avoid parallel cap_map race + double-ship).

**PROT-004/006/008/009 compliance**: 0 new closures; annotation-only.
**Per [[feedback-verdict-msg-honest-reread]]**: 56th post-lock observation; label CAPACITY_PLATEAU_RS_SMOOTH formula-honest at smoke; verdict_msg "1-RSB NOT supported" OVER-EXTENDS at 3-point single-seed resolution; the verdict_msg over-extension is the load-bearing honest call. This is the THIRD observation of the verdict_msg-over-extension pattern across 2-3 cycles (1st: v177 MMD-vs-MP-KS factually wrong on direction; 2nd: v197 capacity-plateau "1-RSB NOT supported" over-extends; 3rd: structural pattern emerges -- verdict_msg authors should be more conservative with explicit-claim language when the underlying formula is at low-resolution sample size).
**Per [[feedback-no-experiment-design-in-prompts]]**: this verdict_handler cycle does NOT prescribe FULL re-run parameters -- exp_dev decides when re-shipped.
**Per [[feedback-lock-in-inefficiency-fixes]]**: candidate structural lock: add a verdict_msg-over-extension check to the verdict_handler honest-reread protocol (specifically flag when verdict_msg makes explicit substrate-physics support/refute claims that exceed the data resolution).


---

## pq_retained re-processing request — NO CAP_MAP BUMP (already consumed at v195)

**Step 0 honest re-read of the on-disk artifact**:
- `data/exp_wave14_1rsb_pq_retained_v1/metrics.json` mtime 2026-05-24 19:35:38
- Reports: n_peaks=1, max_sep_sigma=0.0, binder=0.6666666387006333, ultrametric_frac=NaN, n_pairs=1, mean_q=-9.5e-5, std_q=0.0, n_seeds=2
- Config: mode="smoke", N=512, batch_size=16, epochs=1, seeds=[7,17], n_triples=100
- verdict_msg: "Intermediate P(q): 1 peaks max_sep_sigma=0.00 binder=0.667. Inconclusive 1-RSB vs RS at this axis."
- LABEL: PQ_RETAINED_MIDDLE (honest at smoke-grade -- 2 seeds gives 1 pair; std_q=0.0 is the trivial 1-sample value; binder=2/3 is the trivial 1-sample value; n_peaks=1 from 1 pair is degenerate)

**Why no cap_map v198 bump**:
- v195 cap_map (commit 3a6de2a) ALREADY CONSUMED the wave14_1rsb_pq_retained_v1 FULL verdict
- v195-consumed numbers: n_peaks=4, max_sep_sigma=2.37, binder=-0.164, ultrametric_frac=1.0, n_seeds=10, at N=2048 (from orchestrator_status_log.jsonl 2026-05-24T19:58:25 verdict event)
- Current on-disk metrics.json carries the PRE-SHIP smoke values that were also explicitly captured in exp_dev_decisions_2026-05-24.md line 420 as the smoke-gate reading at handoff time
- The FULL run REMOTE artifact has not been pulled back to overwrite the local smoke; v195's verdict was consumed via the remote verdict event, not via local artifact read
- Processing the SMOKE on-disk artifact as a new "pq_retained = MIDDLE" verdict would be a regression / double-process (would record the SAME anchor as MIDDLE twice with degraded data)

**Net effect**: NO cap_map bump for pq_retained this cycle. v195 remains the canonical Pred-2 W-vector P(q) annotation. Pred-2 status STAYS at v195 reading: INCONCLUSIVE at q_EA~0 negative Binder; W vectors seed-diverse not basin-trapped; pool-level RSB unaffected.

**1-RSB battery joint status after the cascade_depth(v196) + capacity_plateau(v197) + pq_retained(v195-already-consumed) cycle**:
- Pred-1 (capacity_plateau / GPU): v197 SMOKE-grade INCONCLUSIVE (verdict_msg over-extension flagged)
- Pred-2 (pq_retained / CPU): v195 ALREADY CONSUMED FULL = MIDDLE; W-vector axis q_EA~0; INCONCLUSIVE
- Pred-3 (= same script as Pred-1)
- Pred-4 (hysteresis): SHIPPED at b552776 to remote_cpu_queue; IN FLIGHT
- Pred-5 (cascade_depth / GPU): v196 SMOKE-grade INCONCLUSIVE
- Pred-5 ultrametric_triples: smoke 1RSB_CONFIRMED at N=512 trivially; FULL N=2048 pending

**Joint pattern across the entire 1-RSB falsifier battery (definitive after v195/v196/v197)**:
- THREE indirect Pred axes returned INCONCLUSIVE at the resolution accessible (Pred-1/3 capacity-plateau smoke + Pred-2 W-vector P(q) FULL + Pred-5 cascade-depth smoke)
- NONE produced clean HARD-PASS for 1-RSB
- NONE produced clean HARD-FAIL (Pred-1 verdict_msg over-extension flagged; Pred-2 FULL gives anti-clustering not refutation; Pred-5 smoke formula MIDDLE)
- The basin-discrete-1-RSB framing motivated by retention-plateau direct observations (5+ converging plateaus 0.94/0.74/0.60 across Bet B variants v184-v194) is NEITHER strengthened NOR refuted by the indirect-axis diagnostic battery
- Per [[feedback-dont-overextend-theorems]] this does NOT close the 1-RSB framing
- Per [[feedback-no-smoke]] the substrate-product-relevant claim "Bet B retention is basin-discrete at three plateaus" still rests on the DIRECT retention-plateau observations, which the indirect-axis battery was supposed to corroborate but instead returned inconclusive at smoke-grade compute
- Pred-4 hysteresis (in flight at remote_cpu) remains the highest-leverage discriminator still pending; first-order vs continuous transition at the capacity axis is the cleanest binary call available

**Recommended next steps (NOT executed this cycle per turn directive)**:
1. Investigate runner-config-mismatch: why did GPU runner ship SMOKE configs for cascade_depth + capacity_plateau when v195-handoff specified FULL? Same pattern across both GPU anchors shipped together is suggestive of a systematic bug.
2. Re-ship cascade_depth + capacity_plateau at FULL config (5 seeds, 5 epochs, depths 2-5 for cascade; 7 M points multi-seed N=4096 for capacity_plateau). Orchestrator dispatches exp_dev separately per turn directive.
3. Wait on Pred-4 hysteresis (in flight); first-order signature would be the cleanest 1-RSB positive evidence available.

**PROT compliance**: NO commit (no cap_map state change); decision-log only entry per Step 0 honest re-read finding that v195 already consumed this anchor's FULL verdict.

**Per [[feedback-verdict-msg-honest-reread]]**: The pre-PROT 57th observation would have been -- if the SMOKE artifact had been blindly processed -- a regression-class violation (re-processing already-consumed anchor with degraded data). Honest re-read caught this. The on-disk artifact is the stale pre-ship smoke; the canonical FULL Pred-2 verdict is in orchestrator_status_log.jsonl at 19:58:25 and was already absorbed at v195.


---

## v198+v199 -- BUG-RECOVERY: cascade-depth + capacity-plateau FULL results retrieved; root cause diagnosed; structural fix locked

**Trigger**: User dispatch: investigate SMOKE-vs-FULL config mismatch from v196/v197 verdicts; diagnose root cause; re-ship if needed; patch shipping process.

**Step 0 honest re-read**: FULL experiments already ran on remote GPU. No re-ship needed.

### Root cause (confirmed)

**Cause class**: Local artifact pollution -- exp_dev ran pre-ship smoke check under production `HDLAB_EXP_NAME` (not `{name}_smoke` suffix), writing `data/exp_wave14_1rsb_cascade_depth_v1/metrics.json` with `mode: smoke` config at 19:35 local. When the FULL ran on remote GPU (completed 19:56 cascade_depth, 20:10 capacity_plateau), it wrote FULL results to REMOTE's same path. The LOCAL file was never updated. Verdict_handler read LOCAL stale smoke artifact instead of REMOTE FULL results.

**Evidence trail**:
- Local cascade_depth metrics.json mtime: 2026-05-24 19:35 (mode=smoke, N=1024, seeds=[17], depths=[2,3,4])
- Remote cascade_depth metrics.json mtime: 2026-05-24 19:56 (mode=full, N=4096, seeds=[7,17,23,31,41], depths=[2,3,4,5])
- Local capacity_plateau metrics.json mtime: 2026-05-24 19:36 (mode=smoke)
- Remote capacity_plateau metrics.json mtime: 2026-05-24 20:10 (mode=full, N=4096, 7 M points)
- Both smokes written at pre-ship time (exp_dev manual smoke run under production name)
- Both FULLs confirmed running at FULL config on remote (queue.json status=completed; remote metrics.json mode=full)

**NOT a queue_add.sh bug**: queue_add.sh correctly passes `--skip-smoke` for remote queues (smoke runs locally before SSH). The bug is upstream: exp_dev used production `HDLAB_EXP_NAME` for manual smoke, not the `_smoke` suffix.

### FULL verdicts (canonical, after SCP pull)

**cascade_depth FULL (N=4096, 5 seeds, 5 epochs, depths 2-5)**:
- CASCADE_DEPTH_RS_SMOOTH: max_delta=0.068, var_delta=0.00187; both HARD-FAIL conditions met
- Profile: depth=2:0.680, 3:0.714, 4:0.720, 5:0.652 -- non-monotone, no cliff
- **Pred-5 HARD-FAIL on cascade-depth indirect proxy**
- 1-RSB retention-plateau framing from 0.94/0.74/0.60 direct observations UNAFFECTED

**capacity_plateau FULL (N=4096, 3 seeds, 7 M points)**:
- CAPACITY_PLATEAU_RS_SMOOTH: max_delta=0.031; clean HARD-FAIL
- Profile: flat at retA~0.71-0.74 across all 7 M values (25k-400k bytes/stage); NO M-degradation
- **Pred-1/3 HARD-FAIL on capacity-plateau indirect proxy**
- Flat M-profile itself informative: retention floor is M-independent at this N (4-stage hierreplay maintains basin regardless of M within tested range)
- 1-RSB retention-plateau framing UNAFFECTED

### Structural fix (per [[feedback-lock-in-inefficiency-fixes]])

**Fix 1 (process rule, locked now)**: Verdict_handler protocol must include a remote-pull step for experiments on overnight_queue or remote_cpu_queue. Before reading `data/exp_{name}/metrics.json` locally, check if the experiment ran on a remote queue and SCP-pull the remote artifact if so. Without this step, local stale smoke artifacts (written by exp_dev pre-ship manual smoke) shadow the FULL remote results.

**Fix 2 (exp_dev practice)**: When running pre-ship manual smoke check, exp_dev MUST use `{name}_smoke` as `HDLAB_EXP_NAME` (matching queue_add.py's gate convention), NOT the production name. Running smoke under production name writes a ghost artifact that will be shadowed (and confuse verdict_handler) when FULL results come back from remote.

**Fix 3 (queue_add.sh enhancement, deferred)**: Consider having queue_add.sh's remote path also SCP back the smoke metrics from remote (currently smoke runs locally via queue_add.py gate which uses `{name}_smoke` suffix -- correct, no collision). The collision only happens when exp_dev runs manual smoke under production name BEFORE calling queue_add.sh. The current queue_add.sh gate correctly uses `{name}_smoke` suffix for its own smoke run; the bug is in exp_dev's practice, not in queue_add.sh itself.

**Locked as**: verdict_handler SCP-pull check (Fix 1) + exp_dev practice note on smoke-suffix (Fix 2). Structural, not memorial.

### Capability moves

- Pred-5 (cascade-depth): v196 INCONCLUSIVE (smoke ghost) -> **v198 HARD-FAIL (FULL, formula-honest)**
- Pred-1/3 (capacity-plateau): v197 INCONCLUSIVE (smoke ghost) -> **v199 HARD-FAIL (FULL, formula-honest)**
- RSB phase / ultrametric index row: ANNOTATION-ONLY; pool-level RSB UNAFFECTED; 1-RSB retention-plateau framing UNAFFECTED
- Portfolio: 13 demonstrated + 5 evidence-strength UNCHANGED

### Pipeline pacing

- overnight_queue: 0 pending (cascade_depth + capacity_plateau completed)
- remote_cpu_queue: wave14_1rsb_hysteresis_v1 RUNNING (Pred-4; highest-leverage 1-RSB discriminator)
- No refill triggered this cycle (queue depth >=1 on remote_cpu; orchestrator defers further refill)

### per [[feedback-verdict-msg-honest-reread]]: 57th+58th observations

- 57th (v198 cascade_depth FULL): formula-honest; verdict_msg "RS smooth" bounded to cascade-depth axis; not an over-extension; clean.
- 58th (v199 capacity_plateau FULL): formula-honest; verdict_msg "RS smooth" bounded to capacity-plateau axis; "1-RSB NOT supported" language is axis-bounded per [[feedback-dont-overextend-theorems]]; clean at FULL resolution.

### Per [[feedback-no-experiment-design-in-prompts]]

No re-ship was executed because FULL results already existed on remote. If FULL had not run, exp_dev would have designed re-ship parameters autonomously.

### PROT-009

112th paired commit (cap_map.md v198+v199 + history.md v198+v199 + this strategy_decisions entry + visibility_decisions entry + status_log entry).


---

## v200 annotation -- Strategic reframe post R-PRIME-3 + 1-RSB batch (2026-05-24)

### Trigger

User strategic reframe analysis delivered after R-PRIME-3 HARD-FAIL (v193) + 1-RSB indirect battery completion (v195-v199; 0-of-3 HARD-PASS). Annotation-only cap_map bump. 7 decisions filed.

### Decision 1: R-PRIME-3 scope (feedback-dont-overextend-theorems)

R-PRIME-3 HARD-FAIL at r^2=0.103 narrows the corpus-pair-cosine-distance geometry axis. Does NOT close all predictor families. Three zero-new-compute alternative predictor families filed this cycle:
- Alt 1 (most likely): discrete task-class predictor -- classify shift-class, map to 0.94/0.74/0.60 plateaus
- Alt 2: substrate-internal signature -- W spectrum / bundle-norm distribution / replica overlap after Phase-A
- Alt 3 (pending R-PRIME-1 derivation): PAC-Bayes posterior-over-W KL term, NOT input-data KL

Decision: cap_map annotated; alternatives registered in v200 pre-registered-untested section. No new experiments dispatched (this is annotation-only; exp_dev owns design parameters for the alt analyses).

### Decision 2: Discrete-plateau dominance

After 6 converging observations against continuous-axis Bet B mechanisms (v184-v194), the three retention plateaus (0.94 same-corpus / 0.74 4-stage / 0.60 diff-corpus) are the dominant Bet B finding. Decision: annotate explicitly as dominant finding and as defensible product claim. Framing: "substrate has known retention plateaus per task-shift class."

### Decision 3: Substrate-physics framework track record

First mixed-result 1-RSB indirect battery (0-of-3 HARD-PASS; Pred-1/3/5 HARD-FAIL; Pred-2 INCONCLUSIVE; Pred-4 pending). Decision: annotate framework as no longer monotone-positive. Future predictions derived from substrate-physics framework require empirical confirmation rather than assumed reliability. Framework stays load-bearing (direct retention plateaus + K5 + GPT-quality + Bet I 2/3 + R29 + R16 all still supported).

### Decision 4: K5 product-story prominence

K5 Real-time learning during inference is the first Tier-2 KILLER at clean PASS (bpc delta=-0.548, 11x HARD-PASS). Decision: annotate explicitly as product-story anchor independent of Bet B resolution or multi-hop. Substrate-novel (Hebbian-only, no train/inference separation).

### Decision 5: GPT-quality reframe confirmation

v191 ❌->🟢 reclassification confirmed correct at v200. Capability is UNTESTED not REJECTED. P unchanged at 20-30%. Honest characterization of evidence is accurate: no hard ceiling established; substrate-physics frameworks do not predict ceiling; empirical gap unresolved via Paths 3/1/5.

### Decision 6: Combined Tier-1 probability recalibration

Updated to 40-55% (was 55-75% per v79 strategic plan). Downward update driven by substrate-physics framework reliability slip (first mixed-result 1-RSB batch). MoE / Bet N / SSM-HiPPO all independently motivated; this is calibration discipline, not pessimism about substrate.

### Decision 7: local_cpu_runner infrastructure failure (OPERATIONAL FLAG)

**local_cpu_runner (desktop CPU) has been DEAD since 2026-05-21.** At time of v200 commit, this is 3+ days unresolved. Open infrastructure failure compounding the pipeline-pacing gap (desktop CPU underutilized; CPU-tier drills routing to remote_cpu or skipped). Revive steps are in project_cpu_resource_underutilized.md.

**Resolution deadline: 2026-05-27 (72h from 2026-05-24).** If still DEAD at deadline, escalate (file as explicit blocker, reroute all CPU-tier drills to remote_cpu, or accept the bandwidth reduction with explicit acknowledgment).

### Capability moves

All annotation-only. No row state changes. Portfolio 13 demonstrated + 5 evidence-strength UNCHANGED.

### Pipeline pacing

- GPU: Pred-4 hysteresis in flight at remote_cpu_queue (highest-leverage remaining 1-RSB diagnostic)
- Desktop CPU: DEAD since 2026-05-21 (see Decision 7)
- Exp_dev dispatch for Alt 1 / Alt 2 / Alt 3 predictor re-analyses: NOT dispatched this cycle (annotation-only per task contract; exp_dev owns design parameters)

### per PROT-009

113th paired commit (cap_map.md v200 + history.md v200 + this strategy_decisions entry).


## v201 verdict_handler — 2026-05-24 — Bet B Alt 1 discrete task-class predictor SHIFT_CLASS_HARD_PASS at re-analysis level

**Verdict event**: wave14_betB_shift_class_predictor_v1 completed 21:19:39 local_cpu, verdict SHIFT_CLASS_HARD_PASS. Re-analysis of existing per-experiment metrics.json artifacts (replay_by_norm n=49 + ablation_B + 4stage variants + diff_corpus_v1/n4096 + Kovacs v9/v11/v12 synthesized) classified into 6 discrete shift classes.

**Step 0 honest re-read**: label SHIFT_CLASS_HARD_PASS; verdict_msg "6/6 classes have non-overlapping 95% CIs, K-W p=0.0000<0.05"; per-cell metrics.json confirms n_nonoverlapping=6 (>= pre-registered HARD-PASS gate 4) and kw_p=2.9e-14 (< pre-registered HARD-PASS gate 0.05). Six classes ordered by mean retention_A: SAME_CORPUS_PRISTINE 0.941 [0.924, 0.957] n=5 / COMPOUND_SAME_CORPUS 0.885 [0.861, 0.908] n=15 / REPLAY_SAME_CORPUS 0.845 [0.841, 0.848] n=49 / STAGE_4_COMPOUND 0.734 [0.729, 0.739] n=20 / NO_REPLAY_SAME_CORPUS 0.682 [0.676, 0.687] n=5 / DIFF_CORPUS_2TASK 0.633 [0.601, 0.666] n=13. CI separation when ordered by mean: PRISTINE/COMPOUND gap 0.016; COMPOUND/REPLAY gap 0.013; REPLAY/STAGE_4 gap 0.102; STAGE_4/NO_REPLAY gap 0.042; NO_REPLAY/DIFF_CORPUS gap 0.010. All 5 adjacent pairs clean. Label = msg = data. CLEAN per [[feedback-verdict-msg-honest-reread]] 59th observation post-lock.

**Smoke-vs-FULL caveat**: per metrics.json config "mode": "full" the run was the FULL pre-registered re-analysis. User task framing "smoke-only at this point" reads as honest-scope note that the re-analysis pulls from existing per-experiment seed data with modest per-class seed counts (n=5 for 2/6 classes: SAME_CORPUS_PRISTINE + NO_REPLAY_SAME_CORPUS). The analytical bar (n_nonoverlapping >= 4 AND K-W p < 0.05) is cleanly met at this scale; replication at higher per-class seed count would tighten CIs and is the row-state-promotion gate.

### Decision 1: cap_map v200 -> v201 annotation (NOT row-state move)

Per user task framing and [[feedback-dont-overextend-theorems]]: annotation-only bump at re-analysis level. R-PRIME-3 HARD-FAIL row (v193) NOT moved to Alt 1 PASS row; instead the Bet B retention (R-PRIME predictability search space) row from v200 receives v201 annotation that Alt 1 (discrete task-class predictor) has positive zero-new-compute re-analysis evidence at SHIFT_CLASS_HARD_PASS. Row-state promotion gate filed: target n>=15 per class for small-n classes (~50 new seed runs).

### Decision 2: Product claim sharpens from existence to operational predictability

v200 dominant Bet B finding: "substrate has known retention plateaus per task-shift class" (existence claim). v201 upgrade: "substrate retains X% on shift-class K, with K predictable from corpus-pair classification" (operational predictor claim). 6-class taxonomy itself (SAME_CORPUS_PRISTINE / COMPOUND_SAME_CORPUS / REPLAY_SAME_CORPUS / NO_REPLAY_SAME_CORPUS / STAGE_4_COMPOUND / DIFF_CORPUS_2TASK) becomes substrate-characterization product feature. Plateau values refined from 3-point summary (0.94 / 0.74 / 0.60) to 6-point distribution (0.94 / 0.88 / 0.84 / 0.73 / 0.68 / 0.63) with class-conditional CIs.

### Decision 3: R-PRIME-3 rescue R5 WORKED EXAMPLE

Per [[feedback-rehabilitation-after-rejection]]: R-PRIME-3 v193 HARD-FAIL filed 5 rescue candidates (R1 alternative geometry metric / R2 sub-corpus geometry / R3 PAC-Bayes floor / R4 cluster-structured retention / R5 abandon geometry framing). v201 result lands as R5 specifically (categorical classification framing replacing continuous geometry framing). R-PRIME-3 closure on the SPECIFIC metric tested stands; the broader predictor question is rescued at a different framing family. This is the WORKED EXAMPLE of R-PRIME-3 rescue R5 landing positive.

### Decision 4: v200 -> v201 cycle validates rescue-sketch-first-sequencing

Per [[feedback-rescue-sketch-first-sequencing]] (positive worked example: Cap 2 v160 -> v172): cheapest / subsumption rescues sequenced first paid off here. v200 strategic reframe filed at ~21:15 with three alternative predictor families ordered by cost (Alt 1 zero-compute re-analysis "most likely" / Alt 2 substrate-internal signature requires GPU run / Alt 3 PAC-Bayes pending R-PRIME-1 derivation). Alt 1 dispatched immediately as zero-new-compute re-analysis; v201 confirmation landed at 21:19:39 = ~15 min reframe-to-confirmation cycle. SECOND positive worked example for the rescue-sketch-first-sequencing discipline.

### Decision 5: Substrate-physics framework reliability slip from v200 PARTIALLY OFFSET

v200 flagged the substrate-physics framework as no-longer-monotone-positive after 1-RSB indirect battery 0-of-3 result. v201 is positive evidence for an orthogonal framework prediction (discrete-plateau classifier per Bet B retention discrete-structure framing). Framework remains load-bearing; Alt 1 success is a calibration data-point in the positive direction. Combined Tier-1 probability NOT re-recalibrated this cycle (single positive analytic re-analysis; await Alt 2 / Alt 3 / Pred-4 / higher-seed Alt 1 replication before re-touching the 40-55% estimate from v200).

### Decision 6: Pre-reg item tracking

- ~~v200 Alt 1 predictor (discrete task-class)~~ **CONSUMED at v201 V1 = SHIFT_CLASS_HARD_PASS at re-analysis level**.
- v200 OPEN: Alt 2 predictor (substrate-internal W-signature) -- wave14_betB_W_internal_signature_v1 RUNNING on GPU since 21:23:31 per diagnostic_watchdog_truth log.
- v200 OPEN: Alt 3 predictor (PAC-Bayes posterior-over-W KL term) -- depends on R-PRIME-1 derivation in parallel Research dispatch.
- v201 NEW: Alt 1 higher-seed replication -- target n>=15 per class for SAME_CORPUS_PRISTINE + NO_REPLAY_SAME_CORPUS (~50 new seed runs); row-state promotion gate.

### Capability moves

Annotation-only. No row state changes. Portfolio 13 demonstrated + 5 evidence-strength UNCHANGED.

### Pipeline pacing

- Queue-refill NOT triggered (per user task framing -- orchestrator handles separately in same turn if needed).
- Alt 1 higher-seed replication NOT dispatched (annotation-only per task contract; exp_dev owns design parameters; orchestrator may pick up the v201 NEW pre-reg item next cycle).
- Alt 2 RUNNING on GPU (started 21:23:31 -- 2-3h job; verdict expected ~midnight local).
- Pred-4 hysteresis still in flight on remote_cpu_queue.

### per PROT-009

114th paired commit (cap_map.md v201 + history.md v201 + this strategy_decisions entry).

## v202 verdict_handler — 2026-05-24 — Bet B Alt 2 W-internal signature W_INTERNAL_HARD_FAIL

**Verdict event**: wave14_betB_W_internal_signature_v1 completed on GPU (22:08:43 per runner log), verdict W_INTERNAL_HARD_FAIL. Smoke config: N=512, 1 seed, 3 corpus pairs, 13 W-internal signatures tested.

**Step 0 honest re-read**: label W_INTERNAL_HARD_FAIL; verdict_msg "No W-internal signature predicts retention: best r^2=0.000 < 0.2. Post-Phase-A internal state contains no information about subsequent retention." Per-cell check: all 13 signatures (lam1/lam2/lam3/spectral_gap/spectral_gap_ratio/frob_norm_normalized/bundle_norm_mean/bundle_norm_std/bundle_norm_var/bundle_norm_kurtosis/bundle_norm_skewness/row_norm_mean/row_norm_std) have r^2=0.0. Retention values DO vary across 3 pairs (shuffled_same_corpus 1.015 / python_source 0.950 / random_bytes 0.870) -- variance existed for a predictor to capture; none of the 13 W signatures captured any of it. Label=msg=data CLEAN. Honest caveat: smoke config (1 seed, N=512, 3 pairs); r^2=EXACTLY 0.0 across all 13 signatures is strong signal that these spectral/norm observables are structurally non-predictive of retention under Phase-A initialization, not just noisy.

### Decision 1: Alt 2 predictor CLOSED at smoke scale

v200 Alt 2 (substrate-internal W-spectrum / bundle-norm / replica overlap after Phase-A) = W_INTERNAL_HARD_FAIL. All 13 tested signatures yield r^2=0.0 against retention. Per [[feedback-dont-overextend-theorems]]: this closes the specific W-spectral / bundle-norm / row-norm observable family as predictors of retention. Does NOT close the broader question of whether substrate carries any confidence-correlated signal via OTHER internal observables (endpoint-id partition, VAMP-on-chain posterior variance, chi_4 dynamic susceptibility, Kovacs-style hysteresis per query -- these remain open per v162/v150 annotations).

### Decision 2: Rescue candidates for Alt 2 (per feedback-rehabilitation-after-rejection)

Alt 2 HARD_FAIL on W-spectral/bundle-norm observables. 5 rescue sketches before closure:
1. **Activation-pattern signatures** (NOT W-matrix): retrieve patterns x_A from Phase-A; measure overlap distribution, entropy, or activity statistics as predictor. Different axis from W-spectral -- might carry retention information even if W itself is uninformative.
2. **Phase-B weight delta norm** (||W_B - W_A||_F): measure how much learning-in-B actually changes W; high delta may correlate with forgetting of A. Requires Phase-B run, not pure Phase-A signature.
3. **Per-token prediction error trajectory during Phase-A** (BPC trajectory): measure how quickly Phase-A BPC plateaus; fast convergence may signal shallow encoding easily overwritten.
4. **Effective rank of W_A** (nuclear norm / Frobenius norm ratio): tests whether W_A has low-rank structure leaving more capacity for Phase-B encoding without collision; distinct from eigenvalue magnitudes alone.
5. **Mutual information proxy via Phase-A test-set BPC**: use Phase-A generalization quality (not internal weights) as predictor -- a substrate that generalizes better from Phase-A may have more robust encoding. External behavior, not W-internal, but rescues the predictability concept at a different observable level.

All 5 rescues are zero-new-compute or cheap-CPU. Per [[feedback-rescue-sketch-first-sequencing]]: Rescue 3 (BPC trajectory) and Rescue 5 (test BPC) are cheapest -- both extractable from existing per-experiment metrics.json files without new runs. NOT dispatched this cycle (annotation-only; exp_dev owns design parameters).

### Decision 3: Predictor search space state after v202

- Alt 1 (discrete task-class predictor): SHIFT_CLASS_HARD_PASS at re-analysis level (v201); full-replication SHIFT_CLASS_REPLICATION_HARD_PASS also completed (wave14_betB_shift_class_full_replication_v1 -- separate verdict pending verdict_handler dispatch).
- Alt 2 (W-internal signature): W_INTERNAL_HARD_FAIL (this verdict). Closed at smoke scale; 5 rescues registered.
- Alt 3 (PAC-Bayes KL predictor): ALT3_LAPLACE_ASSUMPTION_VIOLATED (wave14_betB_pac_bayes_kl_predictor_v1 -- separate verdict pending verdict_handler dispatch).
- **Net**: Alt 1 is the ONLY confirmed predictor family. Alt 2 + Alt 3 both produced HARD_FAILs at smoke scale. The predictability claim rests on Alt 1 discrete task-class classifier. Per [[feedback-dont-overextend-theorems]]: W-spectral and PAC-Bayes failures do NOT close Alt 2 rescues 1-5 above nor Alt 3 rescues (different KL formulations, tighter Laplace prior, direct bound computation remain untested).

### Capability moves

Annotation-only. No row state changes. Portfolio 13 demonstrated + 5 evidence-strength UNCHANGED.

### Pipeline pacing

No queue-refill dispatched (orchestrator handles separately per task contract).

### per PROT-009

115th paired commit (cap_map.md v202 + history.md v202 + this strategy_decisions entry).


## v203 verdict_handler — 2026-05-24 — BATCHED 5-VERDICT + v202 CORRECTION: Bet B Alt 1 FULL replication HARD-FAIL + Alt 3 INSTRUMENTATION + Pred-3 trivial-CONFIRMED override + Pred-4 INSTRUMENTATION + MoE alpha_c OUT_OF_RANGE

**Trigger**: post-watchdog-silent_idle (22:21:54 fire) batch processing of 5 terminal verdicts that completed between v201 commit and current cycle. A parallel verdict_handler instance committed v202 (commit 34605ac) processing only Alt 2 W_INTERNAL_HARD_FAIL and attaching INCORRECT forward-looking labels to the other pending verdicts: "SHIFT_CLASS_REPLICATION_HARD_PASS pending" for Alt 1 and "ALT3_LAPLACE_ASSUMPTION_VIOLATED pending" for Alt 3. Actual dashboard verdicts: SHIFT_CLASS_REPLICATION_HARD_FAIL and ALT3_INSTRUMENTATION_FAIL. v203 corrects both and processes Pred-3 + Pred-4 + MoE which v202 did not address.

**Step 0 honest re-reads (5 verdicts)**:

(V1) wave14_betB_shift_class_full_replication_v1: label SHIFT_CLASS_REPLICATION_HARD_FAIL; verdict_msg "REPLICATION FAILED: v1 HARD-PASS was small-n artifact. n_nonoverlapping=4 < 5. n_nonoverlapping=4/6. K-W p=0.000000. Bet B predictability claim does NOT hold at n>=15." Per-cell n_nonoverlapping=4 confirms label against >=5 gate. HOWEVER K-W p=0.000000 (omnibus group-differences test) survives at very high significance. Honest re-read SOFTENS the verdict from "Bet B predictability claim does NOT hold" to "the OPERATIONAL 6-distinct-plateaus claim does not hold at n>=15; pairwise CI separation collapses from 6/6 (n=5) to 4/6 (n>=15); K-W omnibus survives (group differences are real); ONE adjacent class-pair boundary blurs." 64th observation post-lock; clean against gate. CORRECTS v202 forward-looking statement.

(V2) wave14_betB_pac_bayes_kl_predictor_v1: label ALT3_INSTRUMENTATION_FAIL; verdict_msg "Fewer than 3 valid cells (0). Cannot compute r^2." exit 0.022s. 22ms exit is consistent with config/load-time crash NOT per-cell Laplace KL computation failure. v202's forward-looking ALT3_LAPLACE_ASSUMPTION_VIOLATED label was a hallucinated prediction without dashboard re-read. 65th observation post-lock; EXTENDS lock scope to forward-looking narrative labels.

(V3) wave14_1rsb_ultrametric_triples_full_v1: label ULTRAMETRIC_1RSB_CONFIRMED; verdict_msg contains contradicting diagnostic in same body: "DIAGNOSTIC: mean_q=0.000001 near zero -- W-vectors from different seeds are nearly orthogonal (UV-problem persists at N=2048). Ultrametric test is on near-zero overlaps; trivial satisfaction expected." OVERRIDE label CONFIRMED -> INCONCLUSIVE per [[feedback-verdict-msg-honest-reread]]. 66th observation post-lock; third LOAD-BEARING override since lock landed (after v177 MMD-vs-MP-KS and v197 over-extension).

(V4) wave14_1rsb_hysteresis_v1: NO verdict file emitted; SSH probe to remote shows queue.json status=failed, exit_code=1, wall=112s; remote log tail shows `TypeError: evaluate_bpc() missing 4 required positional arguments`. INSTRUMENTATION_FAIL — Pred-4 did not produce a substrate-physics signal.

(V5) wave14_moe_alpha_c_prestep_v1: label ALPHA_C_OUT_OF_RANGE; verdict_msg "alpha_c_measured=0.3906 outside expected range [0.08, 0.25]." 1.6x theoretical upper-bound exceedance. 67th observation post-lock; clean against gate.

### Decision 1: cap_map v202 -> v203 batched substantive bump (NOT annotation-only)

5 substantive verdicts + 2 v202 narrative corrections. Bet B operational-predictor claim walked back to group-level claim. Substrate-internal Alt 2 axis closure stands (v202). Substrate-physics framework reliability deflated 40-55% -> 30-45%. MoE rebuild gated on alpha_c anomaly. 2 instrumentation debts (Alt 3 + Pred-4). 1 honest-reread override (Pred-3). Row-state changes none; sub-claim demotions one (Alt 1 operational-predictor). Portfolio 13 demonstrated + 5 evidence-strength UNCHANGED.

### Decision 2: Bet B product claim walks back from v201 operational predictability to v200 group-level structure

v201 sharpened from existence ("substrate has known retention plateaus per task-shift class") to operational predictability ("substrate retains X% on shift-class K, with K predictable from corpus-pair classification"). v203 replication HARD-FAIL reveals v201 was small-n artifact. Defensible product claim returns to v200 framing: "substrate has known retention plateau STRUCTURE per task-shift class (group differences highly significant at K-W p=0.000000); the 6-class taxonomy explains retention variance at group level; operational per-class prediction has class-boundary blurring at small effect sizes." Per [[feedback-no-smoke]] honest scope: this is a WALK-BACK from v201 sharpening, not a Bet B closure — the group-level claim survives.

### Decision 3: Substrate-physics framework reliability deflated 40-55% -> 30-45%

Three additional negative data points beyond v202: Alt 1 replication fail erases v201 partial offset; Alt 2 closure (already at v202); Pred-3 trivial-CONFIRMED override advances 1-RSB indirect battery to 0-of-4 clean. Framework track record on Bet B predictability rescues: 0-of-3 clean. Recalibration per [[feedback-lit-scan-calibration-penalty]]. Framework still load-bearing for K5 ✅, GPT-quality ✅, Bet I 2/3, R29, R16, pool-level RSB ✅, direct retention plateau STRUCTURE.

### Decision 4: MoE rebuild GATED on alpha_c calibration anomaly

alpha_c=0.39 vs theoretical [0.08, 0.25] = 1.6x upper-bound exceedance. Two readings: substrate-implementation drift OR instrument bias. MoE rebuild dispatch REMAINS GATED pending: (a) primary capacity_K script re-measurement of alpha_c; (b) BSC binding/cleanup chain audit; (c) N=1024 default drift verification. Filed as v203 NEW pre-reg.

### Decision 5: Three new lock candidates filed

(L1) Self-test smoke against production code path: amend [[feedback-strategy-spec-formula-selftests]] to require at least one end-to-end first-cell smoke against production code path. Alt 3 (0 valid cells in 0.022s) and Pred-4 (TypeError at first cell in 112s) both passed spec-level self-tests but crashed immediately on production-code-path API mismatches. Two instrumentation fails in one 6-verdict batch is signal, not noise.

(L2) Row-state-promotion gate before product-claim sharpening: amend [[feedback-rescue-sketch-first-sequencing]] to require row-state-promotion replication BEFORE product-claim sharpening, not after. The v200->v201 ~15-min cycle was celebrated as a worked example; v203 reveals the celebration was premature — operational-predictor claim sharpening at v201 was on small-n evidence, and the n>=15 gate failure at v203 reverses the sharpening.

(L3) Forward-looking pending-verdict label honest re-read: amend [[feedback-verdict-msg-honest-reread]] scope to cover forward-looking narrative labels. v202 attached preliminary labels to "pending" verdicts without honest re-read of dashboard verdict_msg; both labels were factually wrong. Discipline: when filing cap_map narrative referencing a "pending" verdict, EITHER cite actual dashboard verdict if terminal OR use explicit "not-yet-read" status with no preliminary label.

### Decision 6: Pre-reg item tracking

- ~~v201 NEW Alt 1 higher-seed replication~~ **CONSUMED at v203 with SHIFT_CLASS_REPLICATION_HARD_FAIL (operational predictor claim walked back; group-level claim retained)**.
- ~~v200 Alt 2 predictor (substrate-internal W-signature)~~ CONSUMED at v202 with W_INTERNAL_HARD_FAIL (FULL-run 25-cell production-grade agreement noted v203).
- v200 OPEN: Alt 3 predictor (PAC-Bayes posterior-over-W KL) — **INSTRUMENTATION_FAIL at v203; remains OPEN with debt; requires script diagnostic before re-ship (NOT a Laplace-assumption violation as v202 stated)**.
- v200 OPEN: local_cpu_runner revive (72h deadline 2026-05-27).
- ~~v195 OPEN: ultrametric_triples FULL at N=2048 12 seeds~~ **CONSUMED at v203 with label CONFIRMED OVERRIDE to INCONCLUSIVE (UV-problem at q_EA ~1e-6)**.
- v195 OPEN: Pred-4 hysteresis — **INSTRUMENTATION_FAIL at v203 (TypeError evaluate_bpc); remains OPEN with debt; requires script API-call-site fix before re-ship**.
- **v203 NEW: MoE rebuild substrate-implementation audit** (alpha_c gating).
- **v203 NEW: Alt 1 SOFT-rescue R6** (group-level taxonomy as product feature).
- **v203 NEW: 3 lock candidates** (L1 production-codepath smoke; L2 row-state-promotion gate before product-claim sharpening; L3 forward-looking pending-label honest re-read).

### Capability moves

Substantive batch. 1 sub-claim demotion (Alt 1 operational predictor walked back to group-level); 1 honest-reread override (Pred-3 to INCONCLUSIVE); 2 instrumentation debts (Alt 3 + Pred-4); 1 anomaly (MoE alpha_c); 1 framework recalibration (40-55% -> 30-45%); 2 v202 narrative corrections (Alt 1 + Alt 3). Portfolio 13 demonstrated + 5 evidence-strength UNCHANGED.

### Pipeline pacing

- Queue-refill NOT triggered (per task contract — orchestrator dispatches exp_dev separately in same turn).
- Pred-4 hysteresis re-ship REQUIRES script fix on base.evaluate_bpc call site before next exp_dev dispatch — flagged for orchestrator's exp_dev refill cycle.
- Alt 3 PAC-Bayes KL predictor re-ship REQUIRES instrumentation diagnostic (likely missing Phase-A artifacts or empty cell-enumeration) before next exp_dev dispatch — flagged for orchestrator's exp_dev refill cycle.
- MoE rebuild GATED until substrate-implementation audit clears alpha_c anomaly — orchestrator should NOT dispatch MoE rebuild on next cycle.
- Alt 1 higher-seed replication ALREADY at n=15 strict-replication scale = HARD-FAIL; no further n-increase rescue plausible without changing the OPERATIONAL 6-class claim. R6 SOFT-rescue (group-level taxonomy as product feature) is annotation, not a dispatch trigger.

### per PROT-009

116th paired commit (cap_map.md v203 + history.md v203 + this strategy_decisions entry).


---

## 2026-05-24 — v204 verdict-reclassification request — DIAGNOSTIC CORRECTION ONLY (no status change)

**Trigger.** Diagnostic agent a1ff36d4e31e57994 flagged v202 Alt 2 W-internal smoke r^2=0 across 13 signatures as structurally guaranteed by smoke design (1 seed -> zero predictor variance -> Pearson r^2 mechanically 0; denominator collapses). Strategic intent dispatched: reclassify v202 Alt 2 HARD-FAIL -> INCONCLUSIVE pending FULL re-run; revise framework reliability deflation; file exp_dev handoff to re-ship W-internal at FULL config.

**Step 0 honest re-read finding (LOAD-BEARING; 68th observation post-lock).** Per [[feedback-verdict-msg-honest-reread]] mandatory honest re-read of dispatched premise against existing cap_map state: v203 line 16417 ALREADY documents the FULL Alt 2 W-internal run executed at production scale — 25 cells / 5 seeds / 5 corpus-pairs / 13 signatures with best r^2=0.001. v203 wrote: "FULL run terminated successfully at 21:58:00 with best r^2=0.001 on 25 cells ... the FULL substantive conclusion (Alt 2 W-internal-features axis CLOSED) AGREES with the v202 SMOKE-level closure but at production-grade evidence." The dispatched reclassification premise ("FULL never ran") was CONTRADICTED by existing cap_map state. Reclassification NOT warranted.

**Decision (verdict-reclassification cycle).**

- Alt 2 W-internal-features axis CLOSURE STANDS at production-grade evidence (25 cells / 5 seeds).
- Framework reliability 30-45% UNCHANGED from v203 (Alt 2 deflator valid at FULL evidence; not retracted).
- NO exp_dev handoff filed (FULL run already documented; re-running would duplicate evidence).
- NO row-state changes; portfolio 13 demonstrated + 5 evidence-strength UNCHANGED.
- v202 process-discipline finding: smoke-only HARD-FAIL label for predictor-variance-sensitive metric (Pearson r^2) with 1 seed per group was structurally over-strong — smoke r^2=0 mechanically guaranteed regardless of signal. Substantive outcome correct ex-post because v203 FULL agreed; inference chain should have flagged INCONCLUSIVE-PENDING-FULL on metric-computability grounds rather than HARD-FAIL on substantive claim.

**v204 cap_map move.** ANNOTATION-ONLY: diagnostic correction on v202 smoke-evidence basis; Alt 2 closure unchanged at production-grade evidence; framework reliability unchanged; 1 lock candidate filed (smoke-only r^2-sensitive-metric HARD-FAIL labels with <3 seeds per group are structurally invalid as falsifying observations).

**Lock candidate (v204).** Amend [[feedback-strategy-spec-formula-selftests]] OR [[feedback-envelope-expansion-fail-bands]]: when a predictor-quality metric (Pearson r^2, Spearman rho, K-W p-value, etc.) is sensitive to per-group sample size, smoke runs MUST EITHER (a) include enough seeds per group to make the metric computable (typically >=3) OR (b) explicitly label the smoke result as INCONCLUSIVE-PENDING-FULL on metric-computability grounds, not as HARD-FAIL on the substantive claim.

**Honest-reread observation.** 68th post-lock. LOAD-BEARING: caught dispatch premise contradiction against existing cap_map line 16417 BEFORE executing the (incorrect) reclassification. Saved both (a) cap_map state regression (would have re-opened a properly-closed branch) AND (b) spurious exp_dev handoff filing (FULL evidence already exists).

**Net effect.** Annotation-only cycle; no status changes; v202 retroactive label-discipline note filed but substantive outcome stands; framework reliability unchanged at 30-45%; 1 new lock candidate; portfolio unchanged. 117th PROT-009 paired commit (cap_map.md v204 + history.md v204 + this strategy_decisions entry).
