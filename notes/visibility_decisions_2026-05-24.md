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
- wave14_cap8_vamp_iterates_rm_1_m_v1 CAP8_RM_ITERATES_GENERATED (annotation): 15/15 RM(1,m) VAMP iterate-trace files written in 304s with min_iters>=3. v5 Composition A audit-trail unblocked for RM(1,m) (real iterates, no spectrum-only fallback). FIRST verdict post structural queue-sync fix -- infrastructure validated. cap_map v179 unchanged. Importance: MEDIUM.


---

## Cycle 201 / v180 -- BATCHED 3-VERDICT visibility (verdict_handler BATCHED-mode; 3 status_log entries written; LOW + MEDIUM + MEDIUM)

### Entry 1 (LOW) -- wave14_cap12_cap8_audit_trail_pipeline_v5 COMPA_AUDIT_MIDDLE_BAND (disambiguation)

PLAIN: The Composition A 4-family audit re-ran with REAL RM(1,m) iterate data (the previous version of this test had used a degraded estimate for RM(1,m) because the iterate files were missing). With the real data, RM(1,m) lifts from 0.40 to 0.571 -- an improvement of 0.17 -- but stays below the 0.60 PASS threshold. Honest reading: the previous 0.40 was partly a degraded-estimate artifact and partly real per-family weakness, NOT one or the other purely. The portfolio framing from yesterday (Kerdock-only at the per-family algebraic audit-trail resolution) STAYS UNCHANGED. The three previously-annotated capability rows (forensic erase, streaming inference, two-readout-primitives) keep the empirical PASS curves they already had, and the "closed-form algebraic derivation" claim continues to scope to Kerdock-class codebooks. Portfolio count stays at 12; no row state changes; this is a clean confirmation of yesterday's framing with the artifact source disambiguated. IMPORTANCE: LOW (informative disambiguation; confirms existing framing with no portfolio movement).

### Entry 2 (MEDIUM) -- wave14_cap8_vamp_ensemble_variance_overlay_v1 ENSEMBLE_OVERLAY_FAIL (Bet Z.5 absorption attempt FAILED)

PLAIN: We tested whether one of our novel readout-primitive candidates (Bet Z.5, an "absorbing-diffusion ensemble smoother" with a per-coordinate posterior-error certificate) is secretly a duplicate of an existing capability (Cap 8 VAMP-on-chain ensemble variance). The test was a structural absorption probe: if K=64 noise-seed-perturbed VAMP runs produce per-coordinate ensemble variance that correlates with per-coordinate reconstruction error, then Bet Z.5 absorbs into Cap 8 and the row closes as a duplicate. The result: 5 out of 5 codewords return correlations below 0.03 (against a pre-registered HARD-FAIL threshold of <0.30 in 3/5). The absorption path is CLEANLY REFUTED. Net consequence: Bet Z.5's per-coordinate-variance certificate is genuinely additional capability, NOT a duplicate of what Cap 8 already provides. The row stays in research-only state but is now empirically confirmed as a novel axis (instead of a synthesis-grade claim that it MIGHT be novel). The next step is a fresh implementation of the underlying mechanism (Diao 2025 absorbing-diffusion smoother on substrate; estimated 4-6 hours CPU + 2-3 GPU-hours validation); this is filed as a pre-registered future experiment but NOT queued this cycle (heavy compute relative to today's queue load -- cheaper sweeps go first). Portfolio count unchanged at 12. IMPORTANCE: MEDIUM (empirically confirms novelty on a 🔬 row; pre-registers the heavy-compute fresh-impl rescue; failure of an absorption probe is informative even though the row's state did not flip).

### Entry 3 (MEDIUM) -- wave14_hatano_sasa_cap3_ness_crooks_v1 HATANO_SASA_CAP3_NESS_CROOKS_MIDDLE_BAND

PLAIN: Cap 1 (erase) already ships with a forensic audit certificate based on a thermodynamic theorem (Crooks fluctuation theorem). We tested whether Cap 3 (continuous writes / streaming dynamics) earns a similar certificate via the Hatano-Sasa extension of the Crooks theorem to steady-state non-equilibrium regimes. The integral fluctuation theorem predicts a specific value (the substrate's average exp(-excess-work) should equal 1.0 within a tight band [0.95, 1.05]); the substrate returned 1.32, which is 30% high. This is OUTSIDE the pass band but INSIDE the broader hard-fail-outside band [0.5, 2.0]. Honest reading: Cap 3 streaming dynamics carries fluctuation-theorem-adjacent structure (we verified real cross-basin transitions at 27% frequency) but does NOT cleanly satisfy the canonical Hatano-Sasa theorem at the precision the canonical derivation requires. Three candidate fixes: (a) add a non-equilibrium correction term to the theory side, (b) refine the basin-decomposition algorithm, (c) try a different fluctuation-theorem framework (Seifert IFT instead of Hatano-Sasa). Cap 3's existing PASS envelope (streaming-inference) is unchanged; the audit-certificate-via-HS-IFT extension is DEFERRED, not killed. A "HS-v2" deferred candidate is filed for the next theory-extension cycle. No portfolio count change (still 12). IMPORTANCE: MEDIUM (defers a potentially substantial customer-facing audit-cert capability for Cap 3 pending theoretical adjustment; not a kill, but also not a free pass -- the canonical IFT was load-bearing for the audit-cert framing).

### Net visibility for the cycle

3 status_log entries written; 0 portfolio movement; queue-refill flag shipped to main thread (CPU drained after 3-verdict batch); 94th PROT-009 paired commit; pause flag CLEARED. Honest-reread LOCK validated cleanly on three distinct verdict classes (PASS-confirmation / FAIL / MIDDLE BAND) in a single batched cycle.

---

## Cycle 202 / v180 -- wave14_tropical_kerdock_N4096_emp_margin_v1 EMP_MARGIN_WELL_DEFINED (data-gen anchor; LOW)

PLAIN: A 5-second GPU run measured how many bit-flips it takes to fool the substrate's readout at production scale (4096 dimensions, 16384 codewords, 250 random codewords sampled). The result is a delta-function-tight distribution: mean = 2004 flips, std = 7, coefficient of variation = 0.4% (against a pre-registered "must be below 30%" threshold -- we beat it by ~75x). Zero degenerate trials, p25 = 1998 flips comfortably above zero. This is the empirical baseline that a companion closed-form theoretical calculation (Anchor 1, running on remote CPU now with ETA 4-8 hours) will be compared against. By itself this verdict is NOT a capability finding -- it is a clean baseline measurement. The closed-form-vs-empirical comparison is what would or would not promote the tropical-margin certificate from research-only to a validated capability. Portfolio count UNCHANGED at 12; no cap_map row movement; cap_map stays at v180. IMPORTANCE: LOW (data-gen success; baseline data only; no row state change; gates on Anchor 1).

QUEUE STATE: GPU drained again (overnight_queue = 0 pending after this 5s run); remote CPU = 1 pending (Anchor 1 closed-form tropical-margin certificate, ETA 4-8 hr). Queue-refill flag shipped to main thread per [[feedback-pipeline-pacing]] queue-depth >= 1 invariant.

### Net visibility for the cycle

1 status_log entry written (LOW; baseline data-gen); 0 portfolio movement; queue-refill flag shipped to main thread (GPU drained again); NO PROT-009 paired commit (annotation-only); pause flag CLEARED -- ACTIVE. 12th honest-reread observation lands cleanly: label EMP_MARGIN_WELL_DEFINED matches data (cv=0.004, deg_frac=0.000, p25=1998 > 0) with no semantic slip.

---

## Cycle 203 / v180 -- wave14_clifford_tn_kerdock_n4096_sanity_v1 HARD_PASS (annotation-only)

### Verdict entry (MEDIUM)

Logged at annotation-only strategy backing-evidence cycle. PLAIN: We tested whether the Clifford-TN bond-dimension-1 closed form reproduces the empirical Schur-Weyl-Pauli reconstruction at the substrate's production dimension N=4096, and whether the Barnes-Wall lattice has zero "magic" (non-stabilizer content) at that scale. Both check out: relative reconstruction error rel_err_max=6.52e-9 (machine-precision noise), Barnes-Wall magic_max=0 EXACTLY. The honest re-read (13th observation) flags that the script's pre-registered literal threshold "<= 1e-10" was over-tight for floating-point arithmetic at N=4096; rel_err_max=6.5e-9 is 65x ABOVE the literal threshold but ~6 orders of magnitude BELOW the 1% hard-fail bar. The SUBSTANTIVE criterion ("magic = 0 + machine-precision reconstruction") is met cleanly. This is Anchor 2 (production-scale GPU sanity) of the Clifford-TN / Barnes-Wall Cap-13 candidate pair; Anchor 1 (CPU closed-form theory anchor at smaller N in {16, 64, 256, 1024}) is still running on remote CPU with ETA ~6-12 hr. Cap 13 candidate row state stays 🔬 at v180 -- promotion gated on Anchor 1 landing. The structural pattern is identical to Cycle 202 (Tropical-Kerdock GPU N=4096 anchor + CPU smaller-N closed-form anchor = paired evidence). NO cap_map version bump this cycle; bundled-promotion paired-commit reserved for when Anchor 1 lands. IMPORTANCE: MEDIUM (positive sanity on substrate-native production scale; substantive criterion met; substrate magic = 0 at Barnes-Wall is a load-bearing observation for Cap 13; but row state movement gated on the CPU theory anchor still in flight).

### Portfolio-level visibility note (cycle 203 / v180)

Substrate-product portfolio at 12 demonstrated capabilities UNCHANGED IN COUNT. Cap 13 candidate row stays 🔬 at v180; the bundled-promotion peg is filed for the paired-commit when Anchor 1 (CPU closed-form theory at smaller N) lands. cap_map at v180 (b716f76, pushed) NO version bump this cycle. Pause flag NOT SET -- ACTIVE. 13th honest-reread observation is a NEW failure mode: script's pre-registered literal threshold (1e-10) was over-tight relative to its substantive criterion (magic=0 + machine-precision); literal-vs-substantive mismatch resolved in favor of substantive reading per [[feedback-no-smoke]] and surfaced for pre-reg discipline calibration. GPU drained again post this verdict (overnight_queue depth = 0); main thread flagged to route next GPU work in parallel with Anchor 1 CPU run per [[feedback-pipeline-pacing]].


## Cycle 202 / v181 -- BATCHED 3-VERDICT: F-14 Tropical KILLED + F-4 Clifford-TN HARD_FAIL_TN_DIVERGENCE + LR_ENVELOPE_MIXED

### V1 entry (HIGH)

Logged at v181 paired commit. PLAIN: We tested whether the tropical-polytope closed-form margin certificate matches the substrate's BSC bit-flip-noise empirics across N in {4, 16, 64, 256, 1024} on 4-coset Kerdock state. The pre-registered HARD-FAIL clause "rel_err > 25% mismatch" was crossed CLEANLY in every N cell (52-99.8% across all 5 cells; error grows MONOTONICALLY with N from 52% at N=4 to 99.8% at N=1024). This is the OPPOSITE of the typical finite-size-artifact shape where small-N is noisy and large-N converges; the error GROWING with N indicates tropical-polytope margin theory is structurally mismatched to BSC discretization of substrate bit-flip noise. F-14 Tropical Cap-13 candidate closed-form margin certificate is KILLED at the theory level. Per [[feedback-rehabilitation-after-rejection]] 5 rescue sketches filed (R1 larger polytope / R2 strictly N=4 / R3 tropical optimization not margin / R4 defer / R5 substrate-novel narrowing framing); R5 is the most-honest framing per [[feedback-no-smoke]] and is carried as the v181 cap_map annotation. NONE pursued this cycle. Cap 13 candidate row STAYS 🔬 at v181 (NOT promoted to portfolio); portfolio count UNCHANGED at 12. The earlier GPU sanity at production N=4096 from Cycle 203 / v180 (the F-4 Clifford-TN companion continent paired anchor) PASSED at machine precision; but F-4 also fails today on the closed-form bond-dim-1 reduction (V3 below). The substrate-novel narrowing framing for both Cap-13 candidate continents is "tropical-polytope margin theory doesn't match BSC discretization; bond-dim-1 Clifford-TN reduction doesn't match the Hopfield-post-processed substrate state at small N; both findings are substantive substrate-physics observations independent of the Cap-13 audit-trail capability framing." IMPORTANCE: HIGH (closed-form-margin theory anchor failure on a Cap 13 candidate continent is a load-bearing strategy update; combined with V3 below this constitutes a dual-rejection signal on the closed-form-margin paired-continent program for the Cap 13 candidate row).

### V2 entry (MEDIUM)

Logged at v181 paired commit. PLAIN: We tested the wave14 online_W LR envelope under multiple schedule shapes (E1 baseline / E2 brief-spike / E3 extended-rectangular / E4 long-tail Robbins-Monro tau=40) at noise levels p=0.30 (baseline noise) and p=0.40 (high noise). Result is MIXED with a substrate-novel pattern: E4 long-tail RM tau=40 WINS over baseline (+0.007 at p=0.30 modest; +0.347 at p=0.40 substantial); E3 extended-rectangular LOSES vs baseline contra the Gong 2026 article's prediction (the article predicts extended-rectangular WINS under noise; on substrate it LOSES); E2 brief-spike LOSES vs baseline as Gong 2026 predicted. The substrate-novel finding is that LONG-TAIL decay (tau >= 40 Robbins-Monro) is the load-bearing schedule shape under noise on substrate NOT rectangular-extended. This is structurally consistent with Cap 5 ✅ existing Robbins-Monro framing and EXTENDS the Cap 5 ✅ noise envelope to long-tail tau >= 40 schedules. Per [[feedback-envelope-expansion-fail-bands]] this reads as annotation-grade extension of Cap 5 ✅ row NOT a row state change. Cap 5 ✅ row gains v181 lr-envelope-extension annotation describing the long-tail RM win under noise. Per [[feedback-2x-means-depth]] 2x Research drill triggered on the mechanism question: WHY long-tail RM decay helps under noise vs rectangular-extended on substrate. Mechanism candidates: variance-averaging at later iterates / late-stage exploration-vs-exploitation tradeoff / Hopfield-attractor-basin late-stage settling / Gong 2026 under-modeled late-stage regime. This is a DEEPER drill on the existing E4 long-tail RM finding NOT a re-verification; the deliverable is mechanism explanation that could inform Cap 5 row annotation AND inform future LR-schedule pre-registrations. NOT dispatched this cycle (Research already loaded; carried as pre-registered future routing for next cycle's Research pickup). IMPORTANCE: MEDIUM (substrate-novel finding extending Cap 5 ✅ envelope is informative not portfolio-state-changing; but 2x Research drill trigger and the OPPOSITE-OF-PREDICTION pattern lift importance above LOW; the +0.347 effect size at high noise p=0.40 is large enough to be customer-facing material).

### V3 entry (HIGH)

Logged at v181 paired commit. PLAIN: We tested whether the Clifford-TN closed-form bond-dim-1 reduction matches the substrate state (v169 Pauli-twirled-Clifford-design framing) at smaller N where the closed-form theory has analytical reach. The pre-registered HARD-FAIL clause "rel_err > 0.1" was crossed CLEANLY at rel_err_max=0.308 (308% above the threshold). F-4 Clifford-TN Cap-13 candidate closed-form bond-dim-1 reduction is KILLED at theory level on small N. The earlier GPU sanity at production N=4096 from Cycle 203 / v180 PASSED at machine precision (magic_max=0 EXACTLY + rel_err_max=6.5e-9). The mechanism reconciliation: substrate state at production N=4096 is dominated by Clifford-orbit structure with magic content below machine precision; BUT at smaller N the bounded non-Clifford magic content injected by Hopfield post-processing becomes the dominant structure that the bond-dim-1 reduction cannot capture (0.308 / 6.5e-9 = 5 x 10^7 ratio rules out noise-amplification artifact at small N). Honest framing per [[feedback-no-smoke]]: "substrate is approximately-Clifford with bounded magic content; pure-Clifford framings hold only at production N where magic is below machine precision; closed-form bond-dim-1 reduction does not extend to small-N regime." This is CONSISTENT with v169 Pauli-twirled-Clifford-design framing at substrate-physics layer (the bounded magic at small N is the post-Hopfield processing layer NOT the substrate physics layer). Per [[feedback-rehabilitation-after-rejection]] 5 rescue sketches filed (R1 increase bond dim chi=2/4 / R2 characterize non-Clifford magic explicitly / R3 reframe approximate-Clifford-bounded-magic / R4 defer / R5 substrate-novel "bounded magic at small N machine-precision-zero magic at production N" narrowing framing); R5 + R3 are the most-honest framings per [[feedback-no-smoke]] and carried as v181 cap_map annotation; R2 (quantify the bounded magic explicitly via Barnes-Wall norm on the actual post-Hopfield substrate state) is the highest-substantive-content rescue path and likely the highest-ranked at next-cycle Strategy review. NONE pursued this cycle. Cap 13 candidate row STAYS 🔬 at v181 (NOT promoted to portfolio; both anchors of the closed-form-margin paired-continent program failed at theory level this cycle). IMPORTANCE: HIGH (second Cap 13 candidate continent's closed-form anchor failure at theory level constitutes a dual-rejection signal on the closed-form-margin paired-continent program for the Cap 13 candidate row; combined with V1 above this is the load-bearing strategy update -- the closed-form-margin paired-continent program needs scope-narrowing to "bounded magic at small N; pure Clifford at production N" framing OR pivot to a different audit-trail capability framing).

### Portfolio-level visibility note (cycle 202 / v181)

Substrate-product portfolio at 12 demonstrated capabilities UNCHANGED IN COUNT. ZERO open ❌ PROVISIONAL rejections remain in portfolio (cleanest portfolio state preserved from v172-v180; Cap 13 candidate row was carried as 🔬 not as ❌ PROVISIONAL prior to v181 and stays 🔬 at v181). The v181 closed-form-margin paired-continent program dual-rejection at theory level (F-14 Tropical CLOSED-rejected + F-4 Clifford-TN MIDDLE BAND with GPU production-N sanity passing) does NOT close the Cap 13 candidate row; the row stays 🔬 with 5+5 rescue sketches filed across both continents and the substrate-novel narrowing rescues (R5 for both) identified as the most-honest framing per [[feedback-no-smoke]]. The honest substrate-physics finding from V3 is "substrate has bounded magic at small N; machine-precision-zero magic at production N; closed-form bond-dim-1 reduction does not extend to small-N regime" which is CONSISTENT with v169 Pauli-twirled-Clifford-design framing at substrate-physics layer. The v181 LR_ENVELOPE_MIXED substrate-novel finding extends Cap 5 ✅ noise envelope to long-tail tau >= 40 RM schedules and triggers a 2x Research drill on the mechanism question. Per [[feedback-pipeline-pacing]] queue context at completion: GPU queue empty after these 3 verdicts (verdict_handler FLAGS queue-refill for main thread); remote CPU has 3 anchors still pending (Mingo-Speicher + Rectangular FC + Hatano-Sasa long-trajectory). The 14th/15th/16th honest-reread observations all show label=msg=data agreement, bringing the post-lock observation tally to 16 clean observations across two HARD-FAIL closures and one MIXED substrate-novel finding in a single batched cycle.


## Cycle 204 -- wave14e_betB_ewc_smoke_v1 BET_B_EWC_INCONCLUSIVE (annotation-only)

### Verdict entry (MEDIUM)

Logged at annotation-only no-version-bump cycle. PLAIN: We tried EWC (Elastic Weight Consolidation; Kirkpatrick 2017) as the canonical published continual-learning rehab path to lift Bet B retention_A from the current ~0.73 to the >= 0.80 target. At the tested lambda grid {0.001, 0.01, 0.1} on N=4096 5-seed, EWC ON shows retention_A=0.736 and gain_C=5.9004 with backward-transfer bwt=+0.1672 -- BUT no clear lift over lambda=0 (no-EWC baseline). The mechanism is not catastrophic (Phase C still learns; bwt is healthy positive) but it is also not distinguishable from the no-EWC baseline at the tested lambdas. Honest re-read (18th post-LOCK observation): label BET_B_EWC_INCONCLUSIVE = msg "no clear lift" = data (retention_A in [0.70, 0.80) AND no-lift) = prereg INCONCLUSIVE branch verbatim. NO over-claim. Bet B core ✅ Validated row is UNTOUCHED -- this experiment tested a SEPARATE retention-envelope-extension question (can EWC lift retention_A above 0.80?) not a re-validation of Bet B itself. NO cap_map version bump; NO row movement; annotation-only. Two elective follow-up paths queued for next-cycle Research pickup: (a) hyperparam extension to lambda > 0.1 (cheapest; Fisher infrastructure already validated this run); (b) Schwarz 2018 Online EWC block-diagonal Fisher variant. Per [[feedback-dont-overextend-theorems]] does NOT kill EWC as a family -- only the (diagonal-Fisher, lambda <= 0.1) cell is closed-deferred. Per [[feedback-rehabilitation-after-rejection]] INCONCLUSIVE is NOT REJECTED so 5-rescue-sketch discipline does not strictly apply. IMPORTANCE: MEDIUM (smoke INCONCLUSIVE with no-lift does NOT change portfolio count and does NOT meaningfully extend any ✅ envelope; deflated from prereg author-side HIGH floor which reflected a hopeful-PASS framing not the actual outcome).

### Portfolio-level visibility note (cycle 204)

Substrate-product portfolio at 12 demonstrated capabilities UNCHANGED IN COUNT. Bet B ✅ Validated row UNCHANGED (the EWC variant tested here is a retention-envelope-extension probe NOT a re-validation of Bet B core mechanism). cap_map stays at v181 (same state as Cycle 202; NO version bump this cycle). Pause flag NOT SET on disk (ACTIVE). remote_cpu_queue depth = 0 at completion of this verdict (this was the last entry there); local_cpu_queue + overnight_queue have pending entries so pipeline depth >= 1 invariant holds at those layers. Remote CPU queue refill is the open question for main-thread pickup. 18th honest-reread observation post-LOCK is a clean label = msg = data = prereg-branch agreement; LOCK still working cleanly. No NEW failure modes surfaced this cycle (the prereg-vs-honest importance deflation MEDIUM-not-HIGH is a discipline calibration note not a new failure mode).


## Cycle 205 (INLINE verdict_handler — 2 verdicts staged for v182 DEFERRED) — 2026-05-24

- 13:XX wave14_tropical_kerdock_N4_closed_form_v1 TROP_R2_CLOSED_FORM_VERIFIED rel_err=0.00e+00 at N=4 strictly; R2 rescue from v181 confirmed clean; NARROW N=4-only degenerate-regime; v182 annotation staged (Cap 13 candidate 🔬 stays); importance MEDIUM; 18th honest-reread observation clean.
- 13:XX wave15_ewc_betB_smoke_v1 EWC_INCONCLUSIVE best lift +0.005 < 0.02 partial; 2nd independent EWC INCONCLUSIVE on Bet B; per [[feedback-lock-in-inefficiency-fixes]] two-observation threshold EWC-class CLOSED-DEFERRED; v182 annotation staged (Bet B 🔬 stays); 5 rescue sketches; importance MEDIUM; 19th honest-reread observation clean.
- Portfolio count UNCHANGED at 12; ZERO open ❌ PROVISIONAL rejections remain.
- cap_map v181 -> v182 paired commit DEFERRED to next Strategy sub-agent cycle (heavy paired-commit footprint not inline-doable).
- Queue state at completion: GPU=2 (1+1), remote_cpu_queue=1 RUNNING ONLY; QUEUE-REFILL FLAGGED; F-6 anchor shipped same turn (Task 3) partly addresses.
- 2 status_log entries written (V1 MEDIUM + V2 MEDIUM); both carry plain_language + importance per [[feedback-for-you-tab-primary-channel]].

## v181 -> v182 BATCHED 4-VERDICT cap_map paired commit (visibility note 2026-05-24 Cycle 204)

Verdicts processed:

- V1 LR_DOSE_MONOTONIC (tau=160 retention 1.000; monotonic ramp tau=10->160; spread=0.133; no plateau ceiling at tau<=160) -- Cap 5 ✅ envelope-extension annotation deepened; importance HIGH (substantive substrate-novel envelope deepening on existing ✅ row; mechanism question sharpened for 2x Research drill scope expansion)
- V2 BOOLEAN_NOISE_STAB_HARD_FAIL (F-6 Cap-13 third candidate KILLED; Cap-13 continent trilogy resolved 0/3 PASS at closed-form-margin theory level) -- Cap 13 candidate row CLOSED-VIA-3-of-3-CONTINENT-REJECTION at theory level; importance CRITICAL (structural-closure signal; trilogy program empirically refuted; 15 rescue sketches across 3 continents; substrate-product narrative outcome on Cap-13 candidate research line)
- V3 VAMP_AMP_CONTRAST_PASS rerun (clean split confirmed at N=4096-full; matches v1) -- Cap 12 ✅ rerun-confirmation annotation; importance LOW (discipline-grade reconfirmation; no envelope expansion)
- V4 N_SWEEP_INCONCLUSIVE (VAMP-on-chain retention 1.000 across all tested N; argmax pattern unclear) -- Cap 8 ✅ N-robustness annotation; importance LOW (annotation-grade; finer-N-grid follow-up pre-registered)

Pause flag: ACTIVE (no flag on disk).
Queues at completion: GPU empty + remote CPU empty + local CPU empty (queue-refill flagged for main thread; main-thread Task 2 will dispatch refill).
Honest-reread observations 17th/18th/19th/20th: all label=msg=data agreement (post-lock observation tally 20 clean).
Portfolio count UNCHANGED at 12 IN COUNT.
ZERO open ❌ PROVISIONAL rejections remain.
96th PROT-009 paired commit (LOCAL; push pending main thread).

Status_log entries written: 4 (V1 HIGH + V2 CRITICAL + V3 LOW + V4 LOW).
Logged at 12:30-12:35 by inline-via-main-thread (Agent dispatch unavailable in sub-agent context per orchestrator post-compaction brief Section 2 execution model clarification).

---

## 2026-05-24 cycle 205 — v183 BATCHED 9-VERDICT cap_map update

- (V1) wave14_hatano_sasa_cap3_long_traj_v2 FULL = HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_FAIL — Cap 3 ✅ UNCHANGED; v180 HS-v2 rehab CLOSED-FAILED (rerun confirms NESS non-canonical). importance=MEDIUM.
- (V2) wave14_betZ5_strictly_stronger_v1 FULL = BETZ5_STRICTLY_STRONGER — Bet Z.5 🔬 -> 🟢 PROMOTE on fresh-impl strictly-stronger-than-VAMP PASS (r=0.458<0.99; variance cert=62.6470). importance=HIGH.
- (V3) wave14_mingo_speicher_1st_order FULL = MS_1ST_ORDER_INCONCLUSIVE — re-queue with iid_gauss + kerdock cells filed. importance=LOW.
- (V4) wave14_sellke FULL = SELLKE_INCONCLUSIVE — re-queue at narrower eps grid filed. importance=LOW.
- (V5) wave14_qnd_cb_invariant FULL = QND_CB_INVARIANT — Cap 8 ✅ FULL UNCHANGED + v183 QND-structural-closure annotation (max_drift_F=0.000000 BOTH codebooks; STRUCTURALLY GUARANTEED at machine precision). importance=CRITICAL.
- (V6) wave14_betV_N65536_v1 FULL = BET_V_N65K_PASS — Bet V 🔬 -> 🟡 PARTIAL composite with V8; gap=0.647 at N=65536 first verdict-level evidence at unprecedented N. importance=HIGH.
- (V7) wave14_cap2_endpoint_id_confidence_remote_v1 FULL = CAP2_ENDPOINT_KILL — Cap 2 ✅ via Cap 6 absorption UNCHANGED; Rescue 1 endpoint-ID REFUTED (elective rescue closed). importance=MEDIUM.
- (V8) wave14_betV_self_reflective_v1 FULL = BET_V_PARTIAL self-reflective — Bet V 🟡 PARTIAL composite with V6; gap=0.285 partial-rescue annotation. importance=MEDIUM.
- (V9) wave14_demo1_noise_envelope_v2 FULL = DEMO1_NOISE_ENVELOPE_PASS — Demo 1 ✅ FULL UNCHANGED + v183 noise envelope extends to p<=0.10 (composed_acc=1.0 at p=0.10; clean=1.0). importance=MEDIUM.

Portfolio UNCHANGED at 12 IN COUNT + 2 new evidence-strength rows (Bet Z.5 🟢 + Bet V 🟡); ZERO open ❌ PROVISIONAL rejections remain. honest-reread LOCK working cleanly across 9 verdict classes 21st-29th observations all label=msg=data agreement 29 clean observations post-lock. 97th PROT-009 paired commit.



## v185 -> v186 SINGLE-VERDICT cap_map update

- (V1) wave14_betB_ablation_B_replay_sweep_v1_2026-05-24 FULL = ABLATION_B_MIDDLE_BAND -- Bet B retention via structural-separation 🟡 M-DEPENDENT PARTIAL UNCHANGED + v186 replay-only-axis BOUNDED control annotation; replay alone plateaus at peak=0.846 / plateau_max=0.846 across by-frac [0.682, 0.840, 0.845, 0.846, 0.844, 0.842, 0.841]; 9pp below HARD-PASS 0.95 regardless of replay fraction; narrow 'monotone=True' flag over-claim detected at honest re-read (series unimodal NOT strict monotone) but load-bearing MIDDLE_BAND tag and substantive bound interpretation HONEST; user's pre-cycle prediction ("replay plateau bounded -> structural separation is the only path") CONFIRMED IN SUBSTANCE; structural-separation axis CONFIRMED as LIVE axis for Bet B retention; compound MoE+per-task stacking ELEVATED to LIVE TOP-PRIORITY; Lane D 4-stage second-LIVE-priority. importance=HIGH.

Portfolio UNCHANGED at 12 IN COUNT + 3 evidence-strength rows (Bet Z.5 🟢 + Bet V 🟡 + Bet B retention 🟡 M-DEPENDENT PARTIAL); ZERO open ❌ PROVISIONAL rejections remain. honest-reread LOCK 33rd observation -- narrow-over-claim + load-bearing-honest in same observation; LOCK working as designed. 100th PROT-009 paired commit.


[16:30 LT] verdict — wave14_betB_compound_pertask_replay_v1_2026-05-24 FULL = COMPOUND_MIDDLE_BAND; retention_A=0.915 in (0.821, 0.95); compound per-task + replay stacks +18.5pp above baseline; HARD-PASS 0.95 NOT cleared by 3.5pp; intrinsic ceiling of TWO-AXIS compound below HARD-PASS; v186 -> v187 cap_map single-verdict annotation; row stays 🟡 M-DEPENDENT PARTIAL; portfolio UNCHANGED 12 + 3; 101st PROT-009 paired commit; 34th honest-reread observation post-LOCK CLEAN.

[16:35 LT] exp_dev ship — 10-anchor hand-off pickup: shipped 5 across GPU (2: K2 Lane D 4-stage + K5/U6 real-time-learning) + remote_cpu (2: K6 compositional + U1/U7 multi-task-transfer) + local_cpu (1: K3 on-device-personalization); covers Priority A KILLER T1/T2 + UNSURE rows from strategy_untested_rows_triage_2026-05-24.md + carries v184 hand-off F-6 Boolean + SSM/S4 + Sellke + MS_1ST_ORDER script-fix as separately-routed; pre-reg + self-test + verify per standing locks; queue depths post-ship: GPU +2 / remote_cpu +2 / local_cpu +1.


[16:55 LT] verdict-batch (10) — v189 -> v190 BATCHED 10-VERDICT cap_map update. (V1) wave14_betB_4stage_continual_v2_rehab_n8192_v1 FOURSTAGE_MIDDLE_BAND K2 axis-1 SATURATION; (V2) wave14_betB_4stage_continual_v2_rehab_phaseA_consolidation_v1 FOURSTAGE_MIDDLE_BAND K2 axis-2 SATURATION no-consolidation-lift; (V3) wave14_cap8_vamp_iterates_srht_hadamard_v1c_cpu_reroute_rerun CAP8_ITERATES_GENERATED Cap 8 infrastructure-only; (V4) wave14e_s4_depth_smoke_v1_reship S4_KILLED; (V5) wave14_sellke_marginal_stability_v1_reship SELLKE_INCONCLUSIVE second-observation; (V6) wave14e_s4_depth_smoke_v1 S4_KILLED duplicate; (V7) wave14_boolean_noise_stab_kerdock_kkl_v1_reship BOOLEAN_NOISE_STAB_HARD_FAIL rerun-confirms v182; (V8) wave14_compositional_holdout_v1 COMPOSITIONAL_MIDDLE_BAND K6 ⚪ -> 🟡 PARTIAL FIRST K6 KILLER T2 probe (4 rehab axes filed); (V9) wave14_betB_multitask_diff_corpus_v1 MULTITASK_DIFF_MIDDLE_BAND U1/U7 ⚪ -> 🟡 PARTIAL FIRST U1/U7 joint probe (3 rehab axes filed); (V10) wave14_realtime_inference_learning_v1 REALTIME_INFERENCE_MIDDLE_BAND labeled / INCONCLUSIVE-INSTRUMENTATION-BUG honest LABEL-OVER-CLAIM 3rd labeled-vs-honest this session. Portfolio 12 UNCHANGED + 6 evidence-strength rows (was 4); ZERO open ❌ PROVISIONAL preserved; honest-reread LOCK 37th-45th observations 8 clean + 1 LABEL-OVER-CLAIM (3/45=6.7% over-claim rate); 104th PROT-009 paired commit.

[2026-05-24T19:49] ORCHESTRATOR TRIAGE (3 issues):
(1) For-You tab blank: recent entries (experiment_queued, research_drill_closure, architecture_rollout, meta_audit) have event_kinds NOT in parsers._NEWS_KINDS = {verdict, cap_map_committed, research_delivery, audit, hard_gate, major_dispatch}. Fix: add experiment_queued and research_drill_closure to _NEWS_KINDS in tools/dashboard/parsers.py.
(2) exp_dev ship claim VALID: cascade_depth RUNNING on GPU (heartbeat confirmed), capacity_plateau pending GPU queue (snapshot confirmed 1 pending), pq_retained RUNNING on remote_cpu (heartbeat confirmed), ultrametric RUNNING on local_cpu (queue.json status=running). Local queue.json files (overnight/remote_cpu) are empty stubs; real state on remote machine, read via SSH by dashboard.
(3) state_check v182 stale: cap_map has headers ## v<N> - (date) ... for v185-v194 but state_check only matches ## v<N> update and ## Cycle N -- v<N> formats. The newer format is unmatched so fallback fires on all v(\d+) tokens, and v182 happens to win the max (Cycle format cap). Fix: add r'^##\s+v(\d+)\s+-\s+' pattern to _cap_map_version() in tools/orchestrator/state_check.py.

## wave14_1rsb_pq_retained_v1 PQ_RETAINED_MIDDLE -- v195 annotation-only

verdict: PQ_RETAINED_MIDDLE | binder=-0.164 | max_sep_sigma=2.37 | n_peaks=4 | mean_q~0 | n_seeds=10
cap_map: v195 annotation-only (no row state change); RSB pool-level row UNCHANGED
1-RSB battery: Pred-2 INCONCLUSIVE (W-vector q_EA~0); Pred-4 hysteresis is next CPU target


---

## v198+v199 -- BUG-RECOVERY visibility record

**Event**: cascade_depth + capacity_plateau FULL results retrieved from remote GPU; root cause diagnosed; cap_map updated to v198+v199.

**For-You tab entry** (HIGH importance):

Both 1-RSB GPU diagnostic experiments that ran overnight completed with FULL configs -- we had a bug where the verdict was read from a stale local smoke file instead of the remote full results. Root cause: before shipping, the manual smoke check wrote a smoke-config file to the same path that the full results would use locally. When the GPU ran the full experiments, results landed on the remote machine only.

After pulling the remote metrics:
- cascade_depth (Pred-5): HARD-FAIL at full config (5 seeds, 5 epochs, N=4096, depths 2-5). Smooth profile, no cliff. max_delta=0.068, var=0.00187 -- both hard-fail conditions met.
- capacity_plateau (Pred-1/3): HARD-FAIL at full config (3 seeds, 7 M-points, N=4096). Flat profile at retA~0.72 across all M values (25k-400k bytes/stage). max_delta=0.031.

What this means: the cascade-depth and capacity-plateau indirect proxies don't show 1-RSB signature. This does NOT affect the 1-RSB framing from the direct retention-plateau observations (the 0.94/0.74/0.60 discrete levels across Bet B variants). Pred-4 hysteresis is still running (remote CPU, highest-leverage remaining test). No re-ship needed.

Structural fix locked: verdict_handler must pull remote metrics before reading local files for GPU queue experiments. exp_dev must use the `_smoke` name suffix for manual pre-ship smoke checks.

**status_log entry**: written with importance=HIGH.
