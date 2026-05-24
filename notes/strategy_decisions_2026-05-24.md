# Strategy decisions -- 2026-05-24

Owner: Strategy session (verdict_handler sub-agent invocations + main thread).
Convention: append-only; newest-first within a cycle; PROT-009 paired-commit stage with cap_map.md + history.md + active_priorities.md + visibility_decisions_<date>.md.

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
