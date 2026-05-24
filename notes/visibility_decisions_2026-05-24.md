# Visibility decisions -- 2026-05-24

Owner: Visibility sub-agent (Haiku); appended inline by verdict_handler when running in BATCHED-mode and the visibility-only dispatch is internalized.
Convention: append-only; one entry per verdict per cycle; status_log entries mirrored to `data/orchestrator_status_log.jsonl` via `tools/orchestrator/state.py log_event`.

---

## Cycle 193 / v173 -- BATCHED PAIR envelope-narrowing verdicts

### V1 entry (MEDIUM)

Logged at v173 paired commit. PLAIN: Cap 1 Crooks forensic erase (✅ FULL Tier 1 clean + Tier 2 Sagawa-Ueda noise-corrected at v158 single-protocol scope) gets stress-tested at a BROADER claim than what v158 promoted: 4 erasure protocols × 12 (M_base, p) cells = 48 cells total under multi-protocol Pareto stress. Only 12/48 = 25% pass. Honest reading: this is an envelope-NARROWING annotation, NOT a Cap 1 ✅ → 🟡 reversion. v158 never claimed multi-protocol invariance; the multi-protocol Pareto test extends to a strictly broader claim and finds it narrow. Cap 1 ✅ STAYS at the v158 pre-registered single-protocol scope (canonical Crooks at p ∈ {0.05, 0.10, 0.20}); v173 annotates the row with explicit multi-protocol scope language ("Tier-2 Sagawa-Ueda envelope is protocol-dependent, not protocol-invariant"). A 6th-candidate elective rescue sketch is noted: protocol-conditioned Sagawa-Ueda calibration (per-protocol theta_protocol(p) re-axiomatization analogous to the v158 Sagawa-Ueda-from-Crooks re-axiomatization). The v169 closed-form derivation annotation (Pauli-twirled depolarizing-channel entropy) is PRESERVED -- the bound FORM is unchanged across protocols; only WHICH protocol the v158 envelope applies to is scope-clarified. IMPORTANCE: MEDIUM (envelope-narrowing annotation on existing ✅ row; no portfolio change; honest scope-clarification per [[feedback-no-smoke]]).

### V2 entry (MEDIUM)

Logged at v173 paired commit. PLAIN: Cap 3 Streaming inference / NESS framing has a v164b extension row "Cap 3 Glauber-Hopfield discrete-spin NESS extension" that was added at 🟢 state in v164 (single-N N=1024 multi-cell 12/18 low-T cells; explicit ✅ promotion criterion was "want N=4096+ multi-N validation before promoting to ✅" -- unmet). The streaming-NESS test injects streaming noise η ∈ {0.001, 0.010, 0.100, 1.000} across 16 cells and finds bimodal P(q) collapses: overall 3/16 = 19% pass; per-η breakdown {0.001: 1/4, 0.010: 1/4, 0.100: 0/4, 1.000: 1/4}. At η=0.1 ZERO cells survive bimodality. Honest reading: the v164b extension row STAYS at 🟢 with v173 zero-noise scope-tightening annotation ("extends to Glauber-Hopfield bimodal P(q) at low T in ZERO-NOISE Glauber dynamics; FRAGILE under streaming-noise injection η ≥ 0.001; v164b extension does NOT compose cleanly with the streaming-NESS framing of the main Cap 3 ✅ row"). The main Cap 3 ✅ row (continuous-state drift-diffusion NESS at v158 bit-flip envelope) is UNTOUCHED -- V2 probes the DISCRETE-SPIN Glauber-Hopfield extension under STREAMING noise, which is a different observable family than the main row's continuous-state drift-diffusion NESS under bit-flip noise. No revert needed: the v164b row was always 🟢 (not ✅); v173 narrows its claim scope (zero-noise Glauber only); the row stays 🟢 at the narrower scope. The v169 closed-form annotation on the main Cap 3 row (Holevo capacity of Clifford-depolarizing channel via MUB-stabilizer lens) is PRESERVED -- it lives on the main row, not on the v164b extension. IMPORTANCE: MEDIUM (envelope-narrowing annotation on existing 🟢 extension row; no portfolio change; main Cap 3 ✅ row untouched; honest scope-tightening per [[feedback-no-smoke]]).

### Portfolio-level visibility note (cycle 193 / v173)

Substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT. ZERO open ❌ PROVISIONAL rejections remain in portfolio (cleanest portfolio state preserved from v172). Both v173 verdicts are envelope-narrowing annotations on existing ✅ / 🟢 rows -- no row state changes, no portfolio additions, no closures. The v172 substrate-product positioning carries forward UNCHANGED at v173 with two scope-clarification annotations layered on (Cap 1 multi-protocol scope-clarification; Cap 3 v164b zero-noise scope-tightening). Per [[feedback-no-smoke]] both annotations are honest scope-clarifications, not framing retractions -- v158 and v164 BOTH explicitly stated the narrower scope at promotion / row-add time; v173 makes the narrower scope explicit in the row text after broader-claim stress tests returned narrow.

---

## Cycle 194 -- v3 stim Kerdock 2-design frame-potential PASS (status_log mirror)

### V3 entry (MEDIUM)

Logged at no-cap_map-bump strategy backing-evidence cycle. PLAIN: We ran the Section 3.A test from the Kerdock-MUB-stabilizer deep drill -- the F_4 frame-potential test of whether the full Clifford group at production d=4096 lands within the Haar 4th-moment band [1.9, 2.1]. It does, cleanly: F_4 = 2.0262 +/- 0.0148 -- inside the band to better than 5%. This empirically confirms the well-known theoretical claim (Webb 2016, Zhu 2017) that the Clifford group is a unitary 2-design, at the production dimension we actually use. The substrate's Kerdock-PSL(2, 4096) anchor lives INSIDE this Clifford group, so the ambient being a 2-design is necessary-but-not-sufficient for the subgroup also being a 2-design. The v169 closed-form annotations on Cap 1 (Pauli-twirled depolarizing-channel entropy), Cap 3 (Holevo capacity of Clifford-depolarizing channel), and Cap 8 (Schur-Weyl-Pauli-twirled S-transform) all rely on the AMBIENT Clifford group's 2-design property -- those annotations now have independent empirical backing in addition to the textbook citation. The narrower question -- is the Kerdock-PSL SUBGROUP also a 2-design at production d? -- is probed by the MUB-distinguishability test (Section 3.B, still in the queue). Cap 1 / Cap 3 / Cap 8 rows stay at FULL state UNCHANGED; this is annotation-grade backing-evidence per [[feedback-dont-overextend-theorems]], not a row promotion. The d=8 cross-check (formula F_4 = 2.0920 vs direct = 2.2250) is consistent with small-d sampling expectations; the d=4096 direct sample is clean. No cap_map version bump this cycle (the v169 annotation language is unchanged; the new backing-evidence lives in strategy_decisions_2026-05-24.md). IMPORTANCE: MEDIUM (positive corroboration of textbook-anchored property; no row state change; no portfolio change).

### Portfolio-level visibility note (cycle 194)

Substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT. ZERO open ❌ PROVISIONAL rejections remain in portfolio. No cap_map version bump this cycle (v173 -> v173). v169 Cap 1 / Cap 3 / Cap 8 closed-form annotations PRESERVED at unchanged state with new empirical corroboration of the underlying ambient-Clifford-2-design anchor noted in strategy_decisions only. Per [[feedback-no-smoke]] the ambient vs subgroup distinction is preserved in language -- 3.A confirms the ambient; the Kerdock-PSL subgroup question is deferred to 3.B (MUB-distinguishability, still queued).


## Cycle 194 — v174 BBMD Cap-12 rehab PAIRED PASS → portfolio 11 → 12 (FIRST new capability of session)

**Visibility verdict.** Two CRITICAL-importance status_log entries written to data/orchestrator_status_log.jsonl for the For You dashboard tab. Reasoning: per [[feedback-for-you-tab-primary-channel]] portfolio-count changes are the user's headline interest; this is the FIRST portfolio-count change since v160 (12 cap_map cycles ago) and the FIRST of the orchestrator-migration era (started 2026-05-23). Both verdicts get CRITICAL not HIGH.

**Plain-language framing.**
- V1: The substrate now ships a 15-millisecond pre-flight diagnostic that picks which inference engine (AMP or VAMP-on-chain) is right for a customer's specific matrix codebook. The test routes 4 of 5 known codebooks correctly and runs 1383x faster than the alternative (running AMP to convergence/failure). This is a real product wedge: customers save compute by not running AMP-to-failure when the pre-test already predicts failure.
- V2: The mechanism that explains WHY some matrix codebooks crash AMP (the κ_n cumulant divergence) generalizes from the substrate's own Kerdock codebook to a second family (SRHT). Correlation drops from 0.900 to 0.700 — exactly at the pre-registered threshold. This is real evidence the explainer is not Kerdock-specific only, but it's also empirical evidence the correlation weakens family-to-family.
- Combined: portfolio count moves 11 → 12. The new 12th capability is INFRASTRUCTURE-class (routing + diagnostic), narrower than the 11 substrate-physics capabilities. The promotion is 🟢 (validated, want stronger) not ✅ (full validation) because both anchors landed at-threshold without margin; ✅ promotion gates are explicit (R3 τ-robustness + R1 Hadamard second-family).

**Importance assignments.**
- V1 (MP_KS_PRETEST_PIPELINE_PASS): CRITICAL — first new capability of session; portfolio count change; FIRST of orchestrator-migration era.
- V2 (INTERP_FAMILY_SRHT_PASS): CRITICAL — co-anchor of same Cap 12 promotion; necessary condition for the composite Cap 12 row.

**Honest framing per [[feedback-no-smoke]].**
- Both anchors at-threshold, not with margin. R1 ρ=0.700 exactly at line; R3 4/5 exactly at gate.
- R1 generalization REAL but PARTIAL: drop from Kerdock 0.900 to SRHT 0.700 is significant. Two more families (Hadamard, RM) needed for universality claim.
- R3 routes 4 of 5 known codebooks; the 5th cell failure is undiagnosed. τ-robustness untested.
- Cap 12 is the LOWEST-P promotion-eligible rescue to date (R3 P=0.55 + R1 P=0.30 per Research's deflated estimates). Lands as expected for that P range — at-threshold.
- The 1383x speedup is real but reflects compute-class difference (millisecond MP-KS vs second/minute AMP-failure-observation), not a routing-accuracy win. The binding constraint at promotion is routing accuracy (4/5 at-threshold), not speedup magnitude.

**Cross-codebook honesty test result.** The Cap 12 framing PASSED the cross-codebook honesty test (which killed v170's broader framing at v171). The new framing is INFRASTRUCTURE-class not substrate-novel-inference-regime-class; cross-codebook discrimination IS the basis of the capability, not a refuted claim. Honest framing per [[feedback-no-smoke]].

**Dashboard impact.**
- For You tab gets 2 CRITICAL entries with plain-language explanations of the portfolio-count change.
- Capacity tab refresh needed: Cap 12 row NEW; v171-renamed BBMD narrow row ABSORBED; v171 ❌ PROVISIONAL Cap-12 candidate CLOSED-RESCUED.
- Orchestrator status panel: pause flag CLEARED; queue healthy; verdict_handler dispatched and returned with v174 cap_map LOCAL commit hash (push pending main thread).

**Cross-row annotations to surface in dashboard tooltips.**
- Cap 8: "Cap 12 ships the routing-decision layer above Cap 8's VAMP-on-chain primitive."
- v164a/v166: "v174 R1 cross-family PASS extends κ_n divergence from Kerdock-specific to iid-Gauss → SRHT."
- v163: "v174 R1 cross-family PASS suggests AMP-failure pattern generalizes (single-second-family)."
- v171 Cap-12 candidate row: "CLOSED via rehab-passes-rescue per [[feedback-rehabilitation-after-rejection]] (2 of 5 rescue sketches PASSED at v174)."

Visibility logged for cycle 194 v174.


---

## 2026-05-24 — wave14_mp_ks_pretest_tau_robustness_v1 MP_KS_TAU_ROBUSTNESS_PASS — Cap 12 first promotion gate satisfied

**Verdict.** Routing robust across tau in {0.15, 0.20, 0.25}; per_tau={0.15: 4, 0.20: 4, 0.25: 4}; >=4/5 correct at every tau. Cap 12 Gate A (R3 tau-robustness) PASSES.

**Strategy outcome.** ANNOTATION-ONLY; NO v175 cap_map commit. Cap 12 row stays 🟢 at v174. Gate A satisfaction documented in strategy_decisions_2026-05-24.md; bundled annotation deferred to eventual v175 commit when Gate B (Hadamard) lands. Per [[feedback-cap-map-update-protocol]] minimize commit churn.

**Dashboard surfacing.** For You tab status_log entry filed; importance=HIGH; framing: "first of two pre-registered promotion gates SATISFIED for Cap 12 ✅ pathway; routing threshold is NOT a fragile hand-picked artifact; Gate B (cross-family Hadamard) still pending."

**Cross-row annotations (deferred to v175 commit; staged here for tooltip refresh on next paired commit).**
- Cap 12 row tooltip: "Gate A (R3 tau-robustness) SATISFIED 2026-05-24 — 4/5 codebooks routed correctly at EACH tau in {0.15, 0.20, 0.25}; routing threshold structurally robust. Gate B (Hadamard cross-family) STILL PENDING via wave14_interp_family_hadamard_v1."
- v174 Anchor-1 row: "tau-robustness within Kerdock-family confirmed; cross-family extension test pending."

**Capacity tab.** No refresh needed (no row movement this cycle).

**Orchestrator status panel.** Pause flag CLEARED; pipeline healthy; queue has Gate B + RM(1,m) pending; verdict_handler dispatched and returned with NO new commit (annotation-only path).

Visibility logged for cycle 195 v174 (annotation-only, no commit).


---

## 2026-05-24 — Cap 12 🟢 → ✅ COMPOUND-GATE PROMOTION (FIRST ✅ promotion of orchestrator-migration era; v175 paired commit)

**Verdicts.** Two new HARD-PASSES bundled with one previously-deferred Gate A annotation:
- V1: `INTERP_FAMILY_HADAMARD_PASS` — ρ=0.900 (matches Anchor-1 Kerdock exactly), VAMP rel-err 0.0876.
- V2: `INTERP_FAMILY_RM_PASS` — ρ=0.700 at-threshold, VAMP rel-err 0.0802.
- Bundled Gate A (deferred from earlier 2026-05-24): `MP_KS_TAU_ROBUSTNESS_PASS` — per_tau=4/4/4.

**Strategy outcome.** Cap 12 row promotes 🟢 → ✅ on THREE pre-registered passes (compound gate met). v175 paired commit; portfolio count UNCHANGED at 12 IN COUNT (state flip on existing row from v174; not a new row addition). FIRST ✅ capability promotion of orchestrator-migration era (era started 2026-05-23). Pre-registered NEXT envelope-expansion fail bands explicit on the ✅ row (E1 noisy-substrate τ-robustness; E2 N=16384 cross-family; E3 fifth-family Paley-/Walsh-Hadamard) — STRESS gates that could REVERT the ✅, not just confirming-evidence gates.

**Dashboard surfacing.** Two For You tab status_log entries filed (both CRITICAL importance — first ✅ capability promotion of orchestrator-migration era is the highest-importance event class). Plain-language framing: "Substrate now ships a millisecond pre-flight diagnostic that decides AMP vs VAMP-on-chain per customer codebook; cross-validated across 5 codebooks × 3 routing thresholds × 4 codebook families. Honest caveat: per-family strength is bimodal (two families at full Kerdock strength, two at-threshold) — not yet uniformly cross-family."

**Cross-row annotations updated this cycle (v175).**
- Cap 12 row: 🟢 → ✅; title clarified to "AMP-vs-VAMP inference routing infrastructure (MP-KS pre-flight + κ_n-divergence cross-family explainer)"; evidence block now lists FOUR positive anchors + τ-robustness PASS; E1/E2/E3 envelope-expansion fail bands explicit.
- Cap 8 (v168 cross-row): "v168 VAMP-vs-AMP split generalizes BEYOND Kerdock to SRHT + Hadamard + RM(1,m); cross-family corroboration widens empirical envelope of Cap 8." Cap 8 stays ✅ UNCHANGED.
- v164a/v166 κ_n fingerprint: "κ_n divergence is now a THREE-family AMP-error predictor (Kerdock 0.900 + SRHT 0.700 + Hadamard 0.900); RM(1,m) third-family hardening at ρ=0.700; bimodal cross-family pattern."
- v163 outside-AMP-universality: "AMP-failure prediction generalizes across three interpolation families."

**Capacity tab.** Refresh: Cap 12 row moves from 🟢 to ✅; portfolio count display stays at 12 demonstrated capabilities but the ✅-grade indicator updates. First ✅-grade addition since orchestrator migration started.

**Orchestrator status panel.** Pause flag CLEARED; pipeline DRAINED to 0 after both verdicts (remote_cpu=0, GPU=0, local idle); silent_idle imminent; verdict_handler flagged queue-refill for main thread; v175 paired commit landed LOCALLY (push pending main thread); 89th PROT-009 paired commit.

**Honest reading surfaced to user.** Per [[feedback-no-smoke]]:
- Bimodal per-family pattern (two with-margin, two at-threshold) means cross-family strength is uneven; the ✅ rests on a compound gate, not uniform per-family strength.
- 1/5 stable routing failure persists across all τ values (stable failure mode; customer-facing "routes 4/5" not "routes correctly").
- The 1383x MP-KS speedup is over AMP-failure-OBSERVATION, NOT over running-correct-VAMP-on-chain; customer framing is "skip AMP failures we predict will fail."
- N=4096 only; no noise stress test; E1 + E2 are the load-bearing real-world stress tests for whether this ships to customer use.

Visibility logged for cycle 195 v175 (Cap 12 🟢 → ✅ compound-gate promotion; FIRST ✅ promotion of orchestrator-migration era).

---

## Cycle 196 — verdict_handler inline visibility (v176)

**Verdict surfaced.** wave14_mp_ks_noisy_substrate_v1 FULL = MP_KS_NOISY_SUBSTRATE_INCONCLUSIVE (E1 stress gate MIDDLE BAND).

**Dashboard surfacing.** 1 For You tab status_log entry filed (MEDIUM importance — first Cap 12 stress test shows partial noise-sensitivity; not a state change but customer-facing scope narrows).

Plain-language framing: "The substrate's pre-flight routing diagnostic (Cap 12) was stress-tested for the first time against noisy codebooks (10% streaming noise). It routes 2 out of 5 codebooks correctly under noise — versus 4 out of 5 on clean codebooks. The capability still works (not 0/5), but degrades noticeably under noise. Customer-facing deployment envelope narrows: ships on low-noise codebooks only; we're now probing finer to find exactly how much noise it tolerates."

**Cross-row annotations updated this cycle (v176).**
- Cap 12 row: ✅ UNCHANGED + v176 noise-sensitivity envelope annotation; deployment envelope narrows to "η ≤ ε where ε is bounded above by 0.10"; fine-resolution sub-probe E1' pre-registered with 3 outcome branches.
- Cap 8 + v164a/v166 + v163 + v169 closed-form annotations: PRESERVED UNCHANGED (no propagation; layer separation).

**Capacity tab.** Cap 12 row stays ✅; row evidence column updates with noise-envelope annotation; portfolio count display stays at 12 demonstrated capabilities.

**Orchestrator status panel.** Pause flag CLEARED; remote_cpu queue likely DRAINED to 0 after E1 finished; GPU still running E2 N=16384 stress gate; local_cpu idle; verdict_handler flagged queue-refill for main thread; v176 paired commit landed LOCALLY (push pending main thread); 90th PROT-009 paired commit.

**Honest reading surfaced to user.** Per [[feedback-no-smoke]]:
- 50% degradation from clean (4/5) to noisy (2/5) is substantial; the v176 annotation is brutally clear about this rather than smoothing it over.
- The 2/5 result is stable across all three τ values — re-tuning τ will NOT rescue the degradation; substrate-level noise-sensitivity is intrinsic at η=0.10.
- The E1' fine-resolution probe could HARD-FAIL at η = 0.01, in which case Cap 12 would REVERT ✅ → 🟢. This is the load-bearing test for whether Cap 12 ships to real customer data.
- The clean-regime ✅ is preserved at its actually-tested scope (5 codebooks × 3 τ × 4 interpolation families); no smoke applied; the narrowing is just honest about what was tested.

Visibility logged for cycle 196 v176 (E1 stress gate MIDDLE BAND → Cap 12 ✅ + noise-sensitivity envelope annotation; portfolio UNCHANGED at 12).


---

## Cycle 197 — verdict_handler inline visibility (annotation-only; honest negative)

**Verdict surfaced.** wave14_cap12_cap6_conformal_routing_subsumption_v1 FULL = CONFORMAL_ROUTING_SUBSUMPTION_KILLED. Composition B (Cap 12 + Cap 6 conformal routing) EMPIRICALLY REJECTED.

**Dashboard surfacing.** 1 For You tab status_log entry filed (MEDIUM importance — honest negative; composition narrative refuted; no cap_map state change; no portfolio change).

**Plain-language framing.** "We tested whether the substrate's calibration tool (Cap 6) could wrap and improve its routing diagnostic (Cap 12) using a shared mathematical score. It cannot. The wrapper made one codebook (Kerdock) commit-but-be-wrong (worse than chance) and made two others abstain entirely. The two individual capabilities still work on their own — this was a failure of the COMPOSITION story, not either capability. The cleaner product framing now is: Cap 12 routing IS the product on its own; calibration is a value-add ONLY if it widens deployment envelope, and here it does not."

**Cross-row annotations updated this cycle.**
- Cap 12 row: ✅ UNCHANGED at v176 (clean-regime + noise-sensitivity envelope from cycle 196 preserved).
- Cap 6 row: ✅ UNCHANGED (Venn-Abers wrapper works as a standalone calibrator; just does not subsume Cap 12 routing under κ_n-divergence).
- Cap 8 + v164a/v166 + v163 + v169 closed-form annotations: PRESERVED UNCHANGED.

**Capacity tab.** No row state changes. Portfolio count display stays at 12 demonstrated capabilities. Zero ❌ PROVISIONAL.

**Orchestrator status panel.** Pause flag CLEARED; remote_cpu queue still has Anchor 2 (Gold) + Anchor 3 (MMD) pending/running; GPU running E2 N=16384; local_cpu idle; queue HEALTHY (no refill flagged); **NO cap_map commit this cycle** (annotation-only verdict).

**Honest reading surfaced to user.** Per [[feedback-no-smoke]]:
- Composition B's shared-mechanism story ("κ_n-divergence is a clean non-conformity score for Cap 12 under Cap 6's Venn-Abers framework") was plausible at the proactive-drill stage but EMPIRICALLY REJECTED.
- This is the SECOND proactive composition story to receive empirical pushback (after cycle 196's noise-fragility envelope narrowing). Pattern flag: plausible-but-empirically-wrong shared-mechanism stories are a recurring failure mode.
- Composition A (Cap 12 + Cap 8 audit-trail) is STRUCTURALLY DIFFERENT from B — it shares a LAYER BOUNDARY HANDOFF, not a non-conformity score. A is still viable; B's rejection does NOT propagate to A. C remains license-pending on cap11 probe.
- The clean product framing is now: Cap 12 standalone IS the product; Composition A is the strongest active composition candidate; Composition C is gated on Cap 11.
- Five rescue sketches filed (R1 Mondrian conformal; R2 MMD non-conformity score deferred pending Anchor 3; R3 drop conformal pursue Composition A; R4 Cap 12 standalone IS the product as default frame; R5 Cap 6 as tiered-SLA alternative to Cap 12).

Visibility logged for cycle 197 (CONFORMAL_ROUTING_SUBSUMPTION_KILLED → annotation-only; portfolio UNCHANGED at 12; no cap_map commit).


---

## 2026-05-24 — wave14_mmd_vs_mpks_pretest_v1 visibility (honest re-read)

**Event tag.** `MMD_VS_MPKS_PRETEST_PASS` (script label) → **HONEST RE-READ: PASS-but-comparative-claim-INVERTED**.

**For You tab entry.** importance = MEDIUM. plain_language explains that the experiment script wrote a conclusion that contradicts its own numbers — MP-KS actually beat MMD on every metric — and the strategy stance is "no swap; keep MP-KS as Cap 12 pre-test." This is a MEDIUM-importance item because the honest reading PROTECTS Cap 12 from an unwarranted primitive swap; it is not a portfolio change.

**Dashboard surfaces.**
- For You tab: NEW entry surfaced (verdict + honest re-read + lock-candidate flag).
- Capacity tab: NO row change. Cap 12 ✅ remains with MP-KS as primary pre-test. MMD/W1 annotated as backup candidates (above absolute floor but strictly worse than MP-KS).
- Orchestrator status panel: pause flag CLEARED; remote_cpu queue **NOW EMPTY** (post-MMD); GPU has E2 running; refill needed.
- Portfolio count display stays at 12.

**Honest-reading flag.** Per [[feedback-no-smoke]] verdict_msg said "MMD strictly out-performs MP-KS"; numbers said ρ_KS=0.975 > ρ_MMD=0.872 and KS-acc=1.00 > MMD-acc=0.80. Strategy treated numbers as ground truth and rejected the label's comparative claim. Visibility surfaces this as part of the For You-tab line so the user sees the honest re-read, not the misleading script label.

**Pattern flag.** First observation of "script verdict_msg comparative claim contradicting metrics." Memory_curator: candidate for [[feedback-lock-in-inefficiency-fixes]] IF a second occurrence appears. Not locking yet.

Visibility logged for cycle 198 (wave14_mmd_vs_mpks_pretest_v1 → annotation-only; no cap_map commit; queue-refill flagged to main thread).


---

## Cycle 197 / v177 -- SINGLE-VERDICT envelope-tightening with HONEST RE-READ

### V1 entry (MEDIUM)

Logged at 04:01 at v177 paired commit. PLAIN: The v176 fine-resolution noise probe came back with a 5-seed-per-cell sweep at η ∈ {0, 0.01, 0.025, 0.05, 0.075, 0.10}. The script wrote "η_critical=0.025" as a confident threshold, but the per-η accuracies are 4/5, 4/5, 2/5, 4/5, 1/5, 3/5 — NON-MONOTONIC, with a recovery cell at η=0.05 that breaks any clean threshold reading. With 5 seeds the per-cell ±1 binomial scatter is large enough to swamp the apparent threshold. Honest re-read: Cap 12 ✅ tolerates noise up to η ≤ 0.01 with verified evidence (4/5 routing at η=0.01 matches clean); behavior above 1% noise needs 20-seed resolution to characterize. The v176 customer-facing claim "ε bounded above by 0.10" TIGHTENS to v177 "tolerates ≤1% noise (verified); >1% needs further characterization." 20-seed E1'' follow-up pre-registered at η ∈ {0.01, 0.02, 0.03, 0.04, 0.05} with explicit HARD-PASS/HARD-FAIL/MIDDLE-BAND branches. Portfolio count UNCHANGED at 12. This is the SECOND time today a script's verdict_msg has labeled a conclusion that its own per-cell metrics contradict (first: wave14_mmd_vs_mpks_pretest_v1 with "MMD strictly out-performs MP-KS" while ρ_KS > ρ_MMD and routing KS > MMD); two-observation lock threshold MET; memory_curator LOCK candidate RECOMMENDED NOW. IMPORTANCE: MEDIUM (envelope-tightening annotation; not a state change but customer-facing scope narrows + 2nd-observation lock signal).


---

## 2026-05-24 — wave14_cap12_cap8_audit_trail_pipeline_v1 visibility (honest re-read)

**Event tag.** `COMPA_AUDIT_MIDDLE_BAND` (script label) → **HONEST RE-READ: PARTIAL-DATA-AMBIGUOUS**.

**For You tab entry.** importance = MEDIUM. plain_language explains that the Composition A audit looks like a mixed result on the surface but ONLY 2 of the 4 codebook families actually have data; one of those two (Kerdock) is a PERFECT correlation (ρ=1.0), the other (RM(1,m)) misses the threshold (ρ=0.40), and the other two families (SRHT + Hadamard) are NaN because the Cap 8 VAMP iterate trace was never saved for them. The "1/4 pass" framing was misleading; the honest reading is "data missing on 2 families; perfect on 1, fail on 1, can't decide."

**Dashboard surfaces.**
- For You tab: NEW entry surfaced (Composition A: data-missing, not killed; follow-up pre-registered).
- Capacity tab: NO row change. Composition A annotation still rides on the v169 closed-form annotations across Cap 1 / Cap 3 / Cap 8.
- Orchestrator status panel: pause flag CLEARED; remote_cpu queue NOW EMPTY (post Composition A + E1'); GPU still running E2; CPU refill flagged to main thread.
- Portfolio count display stays at 12.

**Honest-reading flag.** Per [[feedback-verdict-msg-honest-reread]] (LOCK landed THIS cycle) verdict_msg labelled "1/4 families pass" / "weak structural sharing" — the honest re-read substitutes "PERFECT on Kerdock + below-threshold on RM(1,m) + 2 NaN families (data missing, not weak); not licensed, not killed; re-run after saving Cap 8 VAMP iterates on SRHT + Hadamard." This is the THIRD observation today of "script verdict_msg over-claims its per-cell metrics" — the LOCK just landed THIS cycle is now VALIDATED on its first post-lock test.

**Pattern flag.** Three observations of the over-claim pattern: (1) wave14_mmd_vs_mpks_pretest_v1 "MMD strictly out-performs MP-KS" (contradicted by ρ_KS > ρ_MMD); (2) wave14_mp_ks_noise_envelope_sweep_v1 "η_critical=0.025" (contradicted by non-monotonic 4,4,2,4,1,3); (3) THIS verdict "1/4 pass" (conflates data-missing with weak). LOCK [[feedback-verdict-msg-honest-reread]] caught this one on first post-lock contact.

Visibility logged for cycle 198 (wave14_cap12_cap8_audit_trail_pipeline_v1 → annotation-only; no cap_map commit; queue-refill flagged to main thread).

- 2026-05-24 ~10:25 verdict wave14_cap11_chi4_early_warning_anchor_v1 CAP11_CHI4_FAIL — chi_4 spike huge (SNR 6.4e9) BUT all 5 seeds negative lead-time; chi_4 is post-hoc characterization, not early-warning. Composition C (Cap12+Cap11+Cap1) KILLED at composition level; Cap 11 stays ✅ at current scope. Honest re-read flagged "(<1.5)" inline-threshold label as 4th observation under just-locked [[feedback-verdict-msg-honest-reread]]. Cap_map unchanged (annotation-only). Portfolio count 12.

## 10:20 — wave14_interp_family_N16384_v1 TIMEOUT (rescued from diagnostic)

GPU lane timed out at wall_s=10800 (3h cap) with empty result dir on the pre-registered E2 Cap 12 N-scaling stress gate (κ_n divergence predictor at N=16384 across {Kerdock, SRHT, Hadamard}). Strategy verdict: Cap 12 ✅ STAYS at v175 scope (N ∈ {1024, 4096}); N=16384 UNTESTED (not failed). Portfolio 12 UNCHANGED. No cap_map commit; annotation-only in strategy_decisions_2026-05-24.md. Follow-up sketch: `wave14_interp_family_N8192_v1` (halve N to fit 3h budget) — DEFERRED to main thread re-ship. FIRST timeout-failure of the session; flags candidate inefficiency `envelope-extension-compute-budget-pre-reg` (1st observation, lock deferred per 2x discipline).

PLAIN: We tried to push the new Cap 12 predictor (which tells customers when AMP-style inference will fail and they should use VAMP instead) to a larger problem size (N=16384) to confirm it scales. The GPU ran out of time (3h cap) before producing any data — so we DON'T know if the predictor still works at that size. Cap 12 is still ✅ at the smaller sizes (1024, 4096) where it was validated. Next try: halve the problem size to fit in the time budget.

IMPORTANCE: MEDIUM
- 2026-05-24 wave14_cap8_vamp_iterates_srht_hadamard_v1b CAP8_ITERATES_FAILED — silent script failure (0/30 trace files, 599s); engineering not substrate; importance=MEDIUM; portfolio 12 unchanged; no cap_map commit; Composition A v3 will likely NaN on SRHT/Hadamard from missing input traces — let it run; v4 fix follows parallel diagnostic.

---

## Cycle 194 / v177 -- COMPA_AUDIT v3 STEP 0 LABEL-VS-HONEST FLAG (verdict_handler, log-only)

### Single entry (MEDIUM)

PLAIN: Step 0 honest re-read of `data/exp_wave14_cap12_cap8_audit_trail_pipeline_v3_smoke/metrics.json` contradicts the verdict_handler-supplied verdict_msg. The supplied message claims a 4-codebook Composition A audit with rhos={kerdock:1.0, srht:0.533, hadamard:0.533, rm_1_m:0.40} and a MIDDLE_BAND label; the on-disk metrics file says COMPA_AUDIT_INCONCLUSIVE with only TWO codebooks (kerdock + iid_gauss) and n_seeds=1 in smoke mode. The SRHT/Hadamard/RM(1,m) rho values quoted in the verdict_msg are not present in the data file. Honest reading: insufficient evidence for ANY Composition A claim from this run; the narrative about "Kerdock-specific narrow holds; bimodal pattern is REAL" is NOT supported by this metrics.json (it would require the FULL-mode 4-codebook 5-seed run). No cap_map version bump; no v169 annotation scope-tightening; portfolio stays at 12. Queue refill NONE (pipeline healthy). Per [[feedback-verdict-msg-honest-reread]] this is the 6th honest-reread observation, and a NEW failure mode worth distinguishing -- prior cases were over-claiming a label given correct underlying numbers; this case is the supplied verdict_msg containing numbers that aren't in the metrics file at all (fabricated-cells failure mode). Follow-up gate: require FULL-mode 4-codebook metrics.json with on-disk per-family rhos before any v178 bump on this experiment family. IMPORTANCE: MEDIUM (informative honest-reread flag; not promotion, not kill, not even confirmed measurement).



## 07:25 — wave14_mp_ks_noise_envelope_sweep_v2b KILLED; Cap 12 ✅ stays with TITLE-LEVEL scope-tightening (v178 cap_map commit)

The pre-registered v177 E1'' 20-seed noise-threshold follow-up returned per_eta_correct={'0.010': 5, '0.020': 2, '0.030': 3, '0.040': 2, '0.050': 4} — the HARD-FAIL clause `per_eta_correct ≤ 3 at η=0.02` fires exactly. Per [[feedback-envelope-expansion-fail-bands]] this is title-level scope-tightening (Cap 12 row title now reads "AMP-vs-VAMP inference routing infrastructure for CLEAN-SUBSTRATE codebooks ... noise envelope η ≤ 0.01 verified at 20-seed; degrades sharply above with non-monotone η-interaction"), NOT ✅ → 🟢 revert — the v175 promotion gates were clean-substrate-only and E1'' at η=0.01 reinforces the clean-substrate ✅ at 5/5 (stronger than v175's 4/5). Customer-facing deployment claim narrows materially to "η ≤ 0.01 codebooks; deploy only on clean-substrate or noise-cleaned input." Portfolio count unchanged at 12. New portfolio gap flagged ("noise-cleanup pre-processing as downstream capability" — UNTESTED). Step 0 honest re-read PASSES — verdict_msg matches per-cell data (first clean post-lock 20-seed test of [[feedback-verdict-msg-honest-reread]]). PLAIN: Our most-recent capability promotion (Cap 12, the "is AMP enough or do we need VAMP?" pre-flight router for matrix-inverse-style inference primitive selection) just confirmed at full 20-seed statistics that it only routes correctly on clean codebooks — at ≥2% per-entry noise it gets the routing wrong on most codebook families, with the failure being η-specific rather than monotone-decay. The capability remains validated for clean-substrate use; the customer-facing claim narrows to "clean codebooks only (≤1% noise)"; a new portfolio gap — codebook denoising as a pre-processor — is now on the research radar. IMPORTANCE: HIGH (major customer-facing scope narrowing on the first ✅ promotion of the orchestrator-migration era; title-level annotation is load-bearing; pre-registered hard-fail discipline working as designed).
verdict wave14_cap8_vamp_iterates_srht_hadamard_v1c CAP8_ITERATES_GENERATED: 30 iterate-trace files written; Composition A audit chain unblocked. cap_map v178 unchanged (annotation-only). For You status_log entry written (importance=MEDIUM).

## 07:55 — wave14_cap12_cap8_audit_trail_pipeline_v4 COMPA_AUDIT_MIDDLE_BAND; cap_map v178 -> v179 (FULL-mode confirmation + earlier honest-reread CORRECTED)

v4 FULL-mode (4 codebooks * 5 seeds) returns rhos={kerdock:1.0, srht:0.533, hadamard:0.533, rm_1_m:0.40}, all tied=False. Pre-registered HARD-PASS (>=3/4 at rho >= 0.60) NOT MET (1/4 only); HARD-FAIL (rho < 0.30 on >=2) NOT MET (zero below 0.30); MIDDLE BAND confirmed. Step 0 honest re-read finding: v4 rho values are NUMERICALLY IDENTICAL to v3 — the 07:13 visibility entry that diagnosed v3 as a smoke-leak / fabricated-cells failure mode was WRONG. v3 numbers were real, written through a different summary path than the visibility wrapper expected to read from. v4 confirms the numbers and clears the smoke-leak diagnosis. v179 narrows the v169 closed-form QECC annotations on Cap 1 / Cap 3 / Cap 8 to KERDOCK SCOPE (the closed-form derivation is portfolio-licensed at Kerdock; SRHT/Hadamard/RM(1,m) keep the empirical PASS envelope without the closed-form license). Cap 8 row gains a substrate-physics observation note: kappa_n vs Schur-Weyl irrep-mass correspondence is BIMODAL across structured codebook families (Kerdock perfect; SRHT == Hadamard intermediate at rho=0.533; RM(1,m) weakest). No portfolio addition (NOT a 12th-capability-adjacent); portfolio count UNCHANGED at 12. Pipeline state: remote_cpu queue drained to 0 after v4 (verdict_handler FLAGS queue-refill for main thread per [[feedback-pipeline-pacing]]); GPU has 6 items pending; pause flag CLEARED. cap_map v179 committed LOCAL (push pending main thread). DEFER candidate filed: honest-reread methodology should require cross-run consistency check before declaring fabricated-cells (1st obs; below 2-obs lock threshold; revisit at next honest-reread mis-diagnosis). PLAIN: We tested whether the algebra story we used to back three existing capabilities (the Kerdock-MUB-stabilizer-code closed-form derivation) generalizes from Kerdock to three other structured codebook families. It generalizes only PARTIALLY — Kerdock is a perfect fit, two Hadamard-class transforms are intermediate (identical to each other, which is itself an interesting substrate-physics observation), and Reed-Muller is the weakest. The three previously-annotated capability rows (forensic erase, streaming inference, two-readout-primitives) keep the empirical PASS curves they already had, but the "closed-form algebraic derivation" claim now scopes to Kerdock-class codebooks; on other codebooks the capabilities hold empirically without the closed-form license. Portfolio count stays at 12; no new capability earned; one DEFER lock candidate flagged about the honest-reread methodology itself. IMPORTANCE: MEDIUM (informative middle-band confirmation; not a state-grade change but customer-facing scope narrows on three existing rows).
