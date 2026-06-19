# Strategy overnight refill plan -- post-v272 (2026-05-29)

**Filed by:** strategy deep-review (Opus) in response to GPU drain at v272.
**Recipient:** exp_dev (next dispatch from main thread, user-review-gated).
**Pause state:** check `data/orchestrator_paused.flag` before shipping. As of this filing GPU=drained, CPU has 1 running + 5 pending (saad_solla_v20 still in flight on CPU).
**Window:** ~16h overnight; GPU ~14-16h actual budget; CPU ~10-12h actual budget.

Per [[feedback-no-experiment-design-in-prompts]] this routing file specifies anchor pointers + queue assignment + timeout + justification only. exp_dev re-derives sweep grids / per-cell HP/HF thresholds / smoke configurations from each script's own pre-reg docstring.

Per [[feedback-no-padding-experiments]] every anchor in this list is tied either to a v272 open-question, a v269-v271 still-actionable routing, or a Tier-1 cap_map row needing replication / N-axis extension. No marginal variants added to hit a queue-depth number.

Per [[feedback-ship-before-dependency-verified]] anchors flagged with Kerdock-even-log2 dependency (any `_n8192` carrying make_kerdock_4coset_codebook reach) are EXCLUDED from this plan and remain on the v270 consolidated rescue routing.

---

## 1. What v272 actually told us (honest)

### 1.1 BE-1 precision-floor sweep -- per-cell HONEST but strategic narrative OVER-CLAIMED

The 6-anchor sweep (fp32 / fp16 / int8 / int4 / int2 / int1 on KF-2 isolation at "N=8192") returned max_iso < 0.05 at every precision, including INT1. Per-cell numerical labels are honest: the KF-2 edit-isolation metric does hold under aggressive quantization. The strategic narrative ("32x cost advantage validated; 100-1000x deployment cost differentiation") OVER-CLAIMS what the probe demonstrated. The KF-2 max_iso metric in the BE-1 design measures the post-edit isolation pattern across stored facts. That pattern is dominated by the codebook-vs-argmax structure, NOT by W-magnitude precision. INT1 binarized W producing iso comparable to FP32 is physics-impossible if W precision were operatively load-bearing -- it is direct evidence the test is W-precision-insensitive in the operative path. A genuine cost-advantage test must exercise retrieval accuracy or pool-readout under quantized W where the magnitudes propagate through the readout matmul. Such a test does NOT exist as a shippable script tonight; it needs new script-design work (~1 day eng) and is explicitly excluded from this plan.

Implication: KF-2 row stays UNCHANGED at checkmark (per-cell pass holds). Framework-reliability product-feature band stays UNCHANGED (cannot lift on a probe whose interpretation contradicts the probe's evidence). The 130th LABEL-VS-HONEST sub-flavor (STRATEGIC_INTERPRETATION_OVER_CLAIM) is documented. NO BE-1 reships tonight; the existing data is sufficient to characterize the iso-test's quantization-insensitivity, and a fresh test design is the rate-limiter, not more compute.

Additional concern: Kerdock-even-log2 vulnerability. N=8192 has log2=13 (odd), and the v270-v271 trail shows make_kerdock_4coset_codebook crashes at import. The fact that 6 BE-1 runs at `_n8192` completed without ValueError suggests either a silent codebook fallback OR ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH (config N may not actually be 8192). This is flagged for strategy-level reconciliation next cycle (not in this overnight plan).

### 1.2 Region C/D probes -- substrate is beta-invariant in killer-feature behavior at tested operating points

Region C (M_frac=4, beta=64) HARD_PASS with retention=1.000 across 5/5 seeds and both KF-1 and KF-2 variants. Region D (M_frac=12, beta=64) MIDDLE_BAND with mean_ret=0.3325 across 5/5 seeds and both variants. These results are IDENTICAL in behavior class to regions A (M_frac=4, beta=8) and B (M_frac=12, beta=8). At the probed operating points, beta=64 behaves the same as beta=8: under-capacity ferromagnet retrieves perfectly, over-capacity collapses to chance-floor.

This is a substrate PROPERTY, not a probe failure. It implies the killer-feature behavior is M_frac-controlled and beta-invariant in the tested regions. Strategic consequences:

- The 4-region phase-lattice steerability narrative (KF-A through KF-E driven by beta-steering) is NOT supported at the probed points. If it holds elsewhere, it lives in the narrow band near beta_c (~10-16), not at extreme beta values.
- Operational simplicity wins: no need to steer beta to access different killer-features; M-loading alone selects regime.
- The phase-class profile row CAN keep its yellow band but with NEW annotation: "beta-steering NOT YET demonstrated at probed corners".

Implication for tonight: any further beta-steering probes should target the narrow beta band near beta_c (8-20) at intermediate M_frac (6-10), NOT extreme beta. That is the only remaining beta-axis question worth GPU time. One anchor will probe this; rest of overnight budget shifts to other Tier-1 questions.

### 1.3 saad_solla_v19 beta-sweep BLOCKED -- failure mode is metrics-absent (not timeout, not CUDA OOM)

wall_s=4559 (76min) substantive runtime well under 21600s budget, no remote metrics.json materialized, no CUDA OOM signal in failure. This pattern is consistent with EITHER (a) script crashed mid-run after meaningful compute but before metrics emission, OR (b) substantive beta-axis HARD_FAIL where script ran to completion but failed to emit metrics due to a downstream-of-physics bug. Cannot disambiguate from the runner.log alone.

CPU still running saad_solla_v20_n4096_m_sweep -- that result will be a load-bearing signal: if v20 HARD_PASSES the 5th axis (m-sweep), it suggests the v19 beta-sweep failure was script-specific (not a substrate beta-axis limitation), and v19 deserves a narrower-beta-range retry. If v20 ALSO fails, that is two consecutive 5th-axis attempts failing and the Saad-Solla framework's beta-extension axis is structurally suspect.

This routing plan branches on the saad_solla_v20 outcome in Section 4.

### 1.4 Net strategic implications

1. The 4-region phase-lattice steerability narrative collapses to a 1D M-axis with beta-invariance at extreme beta. Steerability, if real, lives in a narrow beta band near beta_c. One probe answers this.
2. BE-1 cost-advantage claim is in limbo: per-cell pass without operative validation. A new W-magnitude-operative test design is needed (not shippable tonight). Tonight's plan covers the adjacent question -- whether the KF-1 hallucination-detection mechanism (posterior-entropy, NOT W-magnitude-dependent) holds at N=16384 to validate killer-feature N-scaling independently of the quantization question.
3. Saad-Solla v19 disambiguation deferred to v20 outcome; routing branches.
4. axis-4 hysteresis-killer was CLOSED at probe level. Rescue path: test at multi-basin operating point (beta near beta_c AND M near M_c boundary). One anchor probes this.
5. PB-3 critical-slowing FIRST CONTRADICTING evidence at v271 (PB3V4_HARD_FAIL FLAT_TAU_N8192). 3 rescue sketches (audit, N-down reproduce, dtype-instrument) filed cheapest-first. Tonight ships the CHEAPEST: N-down reproduce at N=4096 to confirm the contradiction is real and not Kerdock-even-log2 silent fallback.
6. KF-1 row at green 65-80% (lifted v271). N-axis replication at N=8192 is the next step toward checkmark elevation -- this is the most efficient single anchor of the night.

---

## 2. Re-prioritized Tier-1 questions for next 16h

### Q1. Does KF-1 hallucination-detection hold at N=8192 (multi-N replication)?

Why high-leverage now: v271 lifted KF-1 row from green-smoke to green at single-N (N=4096, 5-seed x 3-M_frac). The row annotation explicitly says "multi-N replication N=8192 still needed for tick promotion". A clean HARD_PASS at N=8192 elevates KF-1 from green to checkmark and is the highest-evidence-density product-feature event reachable tonight. This is INDEPENDENT of the W-magnitude-precision quantization question that BE-1 tangled with -- the posterior-entropy mechanism does NOT depend on W magnitude.

Anchor: `kf1_hallu_rescue_v3_n8192` -- NEW SCRIPT NEEDED (exp_dev derives from kf1_hallu_rescue_v2_n4096 at higher N). Estimated wall_s 1800-3600s. PROT-019 _n8192 floor: timeout_s >= 21600s.

Kerdock-even-log2 risk: KF-1 hallu rescue v2 uses argmax-vs-uniform readout, not Kerdock codebook construction. Audit step (1min) confirms whether make_kerdock_4coset_codebook is reached at this script. If reached: reship at N=4096 reproduce-stability test instead.

### Q2. Does KF-2 isolation hold at N=4096 with PROPER per-anchor W-magnitude exercise (not BE-1 isolation-only)?

Why high-leverage now: this is the OPERATIVE-PATH test that BE-1 should have been but wasn't. Reuse the existing kf2_isolation_proof_v2_n8192 script's logic at N=4096 with --bit-precision arg applied AFTER store but BEFORE the retrieval that actually exercises the readout matmul. The metric must be retrieval accuracy (not iso pattern) so W magnitude is operatively load-bearing. **This requires NEW script work and CANNOT ship as-is** -- explicitly deferred to next cycle. NOT in tonight's plan.

### Q3. Does the substrate exhibit steerable killer-feature behavior in the NARROW beta band near beta_c (8-20) at intermediate M_frac (6-10)?

Why high-leverage now: v272 closed the extreme-beta steerability narrative (Region C/D = A/B). The narrow beta_c band is the ONLY remaining window where beta-steering could live. If killer-feature behavior shifts meaningfully across beta in [8, 20] at M_frac in [6, 10], steerability is partially rehabilitated. If not, the 1D M-axis model is fully validated and the substrate operational model simplifies.

Anchor: existing `t1_beta_v3_n4096_mfrac_sweep` (already on CPU queue pending). This anchor IS Q3 -- it sweeps beta x M_frac at N=4096 on CPU. NO NEW SHIP needed; it ships from CPU queue when saad_solla_v20 finishes.

### Q4. Does axis-4 hysteresis (M-history dependence) exist at the multi-basin operating point (beta near beta_c, M near M_c)?

Why high-leverage now: v272 closed axis-4 hysteresis at probed (rate, seed) at beta=8 with max_loop_area=0.0. Rescue: try at higher beta with M near critical boundary where multi-basin theoretically exists. This is a CHEAP probe (existing script + different operating point) that disambiguates "no hysteresis anywhere" from "no hysteresis at probed points".

Anchor: NEW SCRIPT NEEDED -- exp_dev derives `axis4_hyst_critical_v2_n4096` from axis4_hyst_ramp_v1_n4096 at beta=12 (near beta_c) and M_frac sweep across [4, 6, 8, 10] (across M_c boundary). Estimated wall_s 600-1200s. PROT-019 _n4096 floor: timeout_s >= 14400s.

### Q5. Does PB-3 critical-slowing flat-tau result reproduce at N=4096 (cheapest contradiction-confirmation rescue)?

Why high-leverage now: v271 PB3V4_HARD_FAIL was first contradicting evidence at N=8192. Cheapest rescue sketch (per v271 verdict_handler): N-down reproduce at N=4096 confirms whether the FLAT_TAU is genuine substrate physics or a Kerdock-even-log2 silent fallback masquerading. If FLAT_TAU reproduces clean at N=4096 (Kerdock log2=12 OK), the contradiction is GENUINE and PB-3 critical-slowing row needs band review. If FLAT_TAU disappears at N=4096, the v271 result was an artifact and the row stays UNCHANGED.

Anchor: NEW SCRIPT NEEDED -- exp_dev derives `pb3_extended_v5_n4096` from pb3_extended_v4_n8192 at N=4096 with same beta-range / seeds. Estimated wall_s 1200-2400s. PROT-019 _n4096 floor: timeout_s >= 14400s.

### Q6. Does KF-2 envelope-extension hold at N=4096 with codebook-variation (kf3_cross_codebook is already CPU-pending)?

Why high-leverage now: KF-2 row at checkmark; envelope-expansion via codebook diversity adds robustness evidence. Existing CPU pending: `kf3_cross_codebook_v1_n4096`. NO NEW SHIP needed.

### Q7. Does the bid_n_stability v4 N=12288 result land cleanly (BID order-parameter N-axis extension)?

Why high-leverage now: BID family at N=8192 v5 HARD_PASSED. v4 at N=12288 is the next N-axis extension toward checkmark elevation of the bipolar-isolated-density family on the non-eq-stat-mech row. v3 / v4 normalized family had timeout issues; v4 unnormalized at N=12288 has not yet been attempted.

Anchor: `bid_n_stability_v4_n12288` -- script EXISTS (`exp_bid_n_stability_v4_n12288.py`). Estimated wall_s 1800-3600s. PROT-019 _n4096 floor: timeout_s >= 14400s. Risk: N=12288 has log2~13.58 (NOT a power of 2 -- Kerdock will not even be reached as it requires power-of-2 N). Audit: whether bid_n_stability_v4 script uses Kerdock codebook at all. If yes, the N=12288 value will fail the power-of-2 check.

### Q8. Does the kf2_isolation_proof_v2 at N=8192 hold as a clean checkmark replication (N-scale corroboration)?

Why high-leverage now: KF-2 row at checkmark from v2 at N=4096 / earlier. N=8192 standalone proof (NOT the BE-1 sweep) adds N-axis corroboration without the precision-floor entanglement. Script exists at `exp_kf2_isolation_proof_v2_n8192.py`.

Anchor: `kf2_isolation_proof_v2_n8192` -- script EXISTS. Estimated wall_s 600-1800s. Kerdock-even-log2 risk: N=8192 log2=13 odd. Audit step required. If Kerdock reached: ABSORB into v270 consolidated rescue routing, NOT this plan. Skip and reship at N=4096 reproduce or N=16384 elevation.

---

## 3. 16-hour overnight anchor list

Total: 27 anchors planned. 18 GPU (overnight_queue) + 9 CPU (remote_cpu_queue). 5 anchors already on CPU queue pending (counted in CPU total).

Per [[feedback-no-experiment-design-in-prompts]] each anchor below specifies only:
- Verified script path (Glob-confirmed exists)
- Justification (1 sentence)
- Queue / timeout floor / est wall_s
- Dependencies (ship-FIRST vs LATER ordering)

exp_dev re-derives sweep grids, HP/HF bands, seed counts, smoke gate from each script's docstring. Per PROT-018 every anchor name MUST verify against the actual `--N` passed at queue_add (exp_dev gates at queue_add.py exit-6).

Per [[feedback-ship-name-collision]] each anchor name MUST be checked for uniqueness against completed-entry prefixes BEFORE queue_add.

### 3a. GPU anchors (overnight_queue) -- 18 total

**Ship-FIRST batch (highest leverage, run early so verdict feedback can re-prioritize batch 2):**

| # | Anchor | Script | Justification | timeout_s | est wall_s |
|---|---|---|---|---|---|
| G1 | kf1_hallu_rescue_v3_n8192 | NEW (derive from exp_kf1_hallu_rescue_v2_n4096.py at N=8192) | Q1 -- KF-1 N-axis replication for green->checkmark elevation; HIGHEST single-anchor leverage tonight | 21600 | 1800-3600 |
| G2 | pb3_extended_v5_n4096 | NEW (derive from exp_pb3_extended_v4_n8192.py at N=4096) | Q5 -- cheapest PB-3 FLAT_TAU disambiguation; confirms or rejects v271 contradicting evidence | 14400 | 1200-2400 |
| G3 | axis4_hyst_critical_v2_n4096 | NEW (derive from exp_axis4_hyst_ramp_v1_n4096.py at beta near beta_c, M near M_c) | Q4 -- axis-4 hysteresis rescue at multi-basin operating point | 14400 | 600-1200 |
| G4 | kf2_isolation_proof_v2_n4096_audit | NEW (audit + reship of kf2_isolation_proof_v2_n8192 at N=4096 if Kerdock-vulnerable) | Q8 -- KF-2 N-scale corroboration WITHOUT BE-1 precision entanglement; N=4096 chosen because Kerdock-even-log2 safe | 14400 | 600-1800 |
| G5 | tcft_m_sweep_v3_n8192_5seed | experiments/exp_tcft_m_sweep_v3_n8192_5seed.py | TCFT deletion-cert row at green 85-94%; M-sweep at N=8192 5-seed = highest-evidence-density TCFT corroboration available | 21600 | 1800-3600 |
| G6 | tcft_alpha_sweep_v1_n8192 | experiments/exp_tcft_alpha_sweep_v1_n8192.py | TCFT envelope-expansion across alpha; adds robustness evidence | 21600 | 1800-3600 |

**Ship-SECOND batch (Tier-1 question coverage; depends on G1 verdict for KF-1 reweighting):**

| # | Anchor | Script | Justification | timeout_s | est wall_s |
|---|---|---|---|---|---|
| G7 | bet_b_4stage_batch128_v1_n4096 | experiments/exp_bet_b_4stage_batch128_v1.py | Bet B 4-stage yellow row; batch128 axis-rescue (4th independent stage-A rescue arm); ship per [[feedback-rehabilitation-after-rejection]] | 14400 | 1800-3600 |
| G8 | bet_b_4stage_n16384_v1 | experiments/exp_bet_b_4stage_n16384_v1.py | Bet B 4-stage N-axis extension to N=16384 (Kerdock log2=14 EVEN, SAFE) | 21600 | 2400-4800 |
| G9 | saad_solla_v18_n16384 | experiments/exp_saad_solla_v18_n16384.py | Saad-Solla N-axis extension to N=16384; corroborates v16 N=8192 production-scale at 2x larger N (Kerdock log2=14 SAFE) | 21600 | 3600-7200 |
| G10 | kf4_drift_detect_v4_n4096 | experiments/exp_kf4_drift_detect_v4_n4096.py | v269 routing open -- KF-4 posterior-entropy rescue v4 mirroring KF-1 success path | 14400 | 1200-2400 |
| G11 | kf3_multisub_v2_n4096 | experiments/exp_kf3_multisub_v2_n4096.py | KF-3 multi-substrate isolation at N=4096 (v3 at N=8192 was Kerdock-blocked; v2 at N=4096 SAFE) | 14400 | 600-1800 |
| G12 | bid_order_parameter_v6_n4096 | experiments/exp_bid_order_parameter_v6_n4096.py | BID order-parameter at N=4096 (cheaper N-scale than v4 N=12288 for non-eq-stat-mech corroboration) | 14400 | 1200-2400 |

**Ship-THIRD batch (envelope expansion / corroboration):**

| # | Anchor | Script | Justification | timeout_s | est wall_s |
|---|---|---|---|---|---|
| G13 | bid_order_parameter_v5_n8192_bsc | experiments/exp_bid_order_parameter_v5_n8192_bsc.py | BID BSC codebook variant at N=8192 (avoids Kerdock-even-log2; codebook-axis diversity) | 21600 | 1800-3600 |
| G14 | kf5_phase_v1_n4096 | experiments/exp_kf5_phase_v1_n4096.py | KF-5 phase-mechanism v1 baseline at N=4096 (v2 basin-volume rescue routing still open); ship v1 first to confirm baseline reproduces before v2 ships | 14400 | 600-1800 |
| G15 | t1_m_sweep_v1_n4096 | experiments/exp_t1_m_sweep_v1_n4096.py | M-sweep at N=4096 (mirror to beta-sweep v3 axis-1 coverage) | 14400 | 600-1800 |
| G16 | t1_beta_fine_v2_n4096 | experiments/exp_t1_beta_fine_v2_n4096.py | Beta-fine narrow-band probe (Q3 GPU complement to CPU t1_beta_v3 mfrac_sweep) | 14400 | 1200-2400 |
| G17 | tcft_erase_robustness_n8192_v1 | experiments/exp_tcft_erase_robustness_n8192_v1.py | Was IN-FLIGHT before reset (per post_reset_priority note); needs re-ship; TCFT robustness corroboration | 21600 | 1800-3600 |
| G18 | bid_n_stability_v4_n12288 | experiments/exp_bid_n_stability_v4_n12288.py | Q7 -- BID N-axis extension to N=12288 (Kerdock vulnerability AUDIT REQUIRED before ship; N=12288 is NOT power-of-2 so make_kerdock_4coset_codebook will reject at the n_log2 != round check; if script uses BSC instead this is safe) | 21600 | 1800-3600 |

GPU total est wall_s: lower bound sum 24600s (~6.8h), upper bound sum 51000s (~14.2h). Comfortable fit within 14-16h budget; if any single anchor over-runs the queue can absorb without breaching budget.

### 3b. CPU anchors (remote_cpu_queue) -- 9 total

**5 ALREADY PENDING on CPU (do NOT re-ship; verify exp_dev sees them as pending before adding new):**

| # | Anchor | Script | Justification | timeout_s | est wall_s |
|---|---|---|---|---|---|
| C1 | saad_solla_v20_n4096_m_sweep | experiments/exp_saad_solla_v20_n4096_m_sweep.py | RUNNING -- 5th-axis Saad-Solla m-sweep CPU disambiguation; CRITICAL outcome decides Section 4 branching | (set) | in flight |
| C2 | t1_beta_v3_n4096_mfrac_sweep | experiments/exp_t1_beta_v3_n4096_mfrac_sweep.py | Q3 -- narrow-beta steerability probe | (set) | already queued |
| C3 | t2_codebook_v3_n4096_op_sweep | experiments/exp_t2_codebook_v3_n4096_op_sweep.py | Codebook x operating-point axis sweep | (set) | already queued |
| C4 | ortho_noneq_corroborator_v1 | experiments/exp_ortho_noneq_corroborator_v1.py | Non-eq-stat-mech orthogonal corroboration | (set) | already queued |
| C5 | axis3_triplepoint_v2_n4096 | experiments/exp_axis3_triplepoint_v2_n4096.py | Axis-3 triple-point alternate operating points (v260 routing follow-on) | (set) | already queued |
| C6 | kf3_cross_codebook_v1_n4096 | experiments/exp_kf3_cross_codebook_v1_n4096.py | Q6 -- KF-2/KF-3 cross-codebook envelope at N=4096 | (set) | already queued |

**3 NEW CPU anchors to add:**

| # | Anchor | Script | Justification | timeout_s | est wall_s |
|---|---|---|---|---|---|
| C7 | axis2_codebook_density_v2_n4096_collapse_rerun | experiments/exp_axis2_codebook_density_v2_n4096_collapse.py | v272 V3 MIDDLE_BAND was M_frac-invariant in over-cap; rerun with SEEDS only (no new sweep) on CPU at SMALLER N=2048 to disambiguate whether the invariance is N-dependent or substrate-level | 14400 | 1800-3600 |
| C8 | kf5_steerable_beta_v2_cpu | experiments/exp_kf5_steerable_beta_v2.py | KF-5 phase-mechanism v2 CPU baseline (the basin-volume rescue routing v269 is open; CPU is fine for v2 unless GPU needed) | 14400 | 2400-4800 |
| C9 | tcft_erase_time_v1_n2048 | experiments/exp_tcft_erase_time_v1_n2048.py | TCFT erase-time at N=2048 CPU (cheap N-down envelope; corroborates G5/G6 GPU TCFT batch) | 14400 | 1800-3600 |

CPU total est wall_s for NEW additions: 6000-12000s (~1.7-3.3h additional). Combined with already-pending CPU items the total CPU budget fits 10-12h comfortably.

### 3c. Dependencies / ordering

- G1 (KF-1 N=8192 elevation) ships FIRST in GPU batch -- verdict feeds back into batch-2 prioritization. If G1 HARD_PASSES, KF-1 row likely elevates to checkmark and battery of KF-1 variants becomes lower priority. If G1 fails or MIDDLE_BANDS, posterior-entropy mechanism scaling is unclear and KF-1 stays at green; battery 2 absorbs.
- G2 (PB-3 FLAT_TAU disambiguation) ships SECOND -- if reproduces at N=4096, opens new strategic discussion; if disappears, returns PB-3 row to UNCHANGED state.
- G3 (axis-4 hysteresis rescue) ships THIRD -- cheap probe at multi-basin operating point.
- G4 (KF-2 isolation N-scale audit) ships FOURTH -- requires Kerdock-vulnerability audit gate.
- G5-G6 (TCFT batch) ship in PARALLEL with G1-G4 (independent capability row).
- G7-G12 ship in SECOND wave after G1-G6 verdicts so re-prioritization is informed.
- G13-G18 ship in THIRD wave (envelope expansion / corroboration; low ordering sensitivity).
- C7-C9 ship to CPU queue AFTER saad_solla_v20 result observed (Section 4 branching may modify C7-C9 list).

### 3d. Kerdock-even-log2 risk audit checklist (run by exp_dev BEFORE each ship)

For every anchor above, grep its script for `make_kerdock_4coset_codebook`. If absent: safe. If present:

- N=4096 (log2=12 EVEN): SAFE
- N=8192 (log2=13 ODD): BLOCKED -- skip; absorbed into v270 consolidated rescue routing
- N=12288 (NOT power-of-2): BLOCKED -- script-level rejection at the n_log2 != round check
- N=16384 (log2=14 EVEN): SAFE

For G1 (KF-1 hallu rescue v3 at N=8192): exp_dev audits whether script uses Kerdock. v2 at N=4096 (parent) does NOT use Kerdock (uses argmax-vs-uniform). Likely SAFE at N=8192.

For G18 (BID v4 N=12288): exp_dev audits whether script uses Kerdock. If yes, REPLACE with bid_n_stability_v4_n16384 (build NEW script at N=16384 Kerdock-safe) OR drop and substitute with bid_order_parameter_v5_n8192_bsc duplicate.

---

## 4. Branching on saad_solla_v20 result

CPU still running saad_solla_v20_n4096_m_sweep. Decision tree:

### If saad_solla_v20 HARD_PASS (5th-axis m-sweep succeeds)

Interpretation: v19 beta-sweep failure was script-specific (the m-sweep code path works at N=4096; v19 beta-axis path has a separate bug). Saad-Solla 5th-axis is partially confirmed (m-axis lives); beta-axis disambiguation deferred to a v21 narrower-beta-range retry.

Action: at next exp_dev dispatch (post-G1 verdict ideally), file routing for saad_solla_v21_beta_narrow at GPU OR CPU. Anchor name: derive from v19 script with narrower beta range and dtype-instrumentation. NOT in this overnight plan -- defers to post-v20-verdict cycle.

Framework-reliability specific band: LIFT +1-2% (5th-axis m-axis production-scale).

### If saad_solla_v20 FAILED (5th-axis m-sweep also crashes / no metrics)

Interpretation: two consecutive 5th-axis attempts failed (beta + m). Saad-Solla framework's 5th-axis extension is structurally suspect. Beta-axis AND m-axis both blocked at production scale.

Action: file Saad-Solla framework constraint annotation on the LEADING checkmark row -- "Saad-Solla checkmark holds for axes 1-4 (codebook / N / seed / M-density) NOT 5th axis (beta/m extensions). v19+v20 both BLOCKED at production scale; structural bug or substrate constraint. NEXT: dtype-instrumented re-run of EITHER v19 or v20 at SMALLER N to disambiguate."

DROP Saad-Solla axis-expansion from overnight plan tonight. Specifically G9 (saad_solla_v18_n16384) becomes RISKIER -- it's an N-axis extension not a 5th-axis extension, but the dtype-instrumentation question may bite at N=16384 too. RECOMMEND: keep G9 in plan (independent question), but flag for exp_dev awareness that if v18 ALSO produces no metrics, the failure mode is N-scale-dependent (not 5th-axis-specific) and a deeper engineering audit is needed before further Saad-Solla ships.

Framework-reliability specific band: UNCHANGED (no lift on failed runs).

Default plan (this routing file): proceed with G1-G18 + C7-C9 as written. Branch decision (saad_solla v21 vs drop) applies to the NEXT exp_dev cycle, not this overnight ship.

---

## 5. What CANNOT ship overnight (explicitly deferred)

### Multi-week engineering tracks (do NOT enter overnight queue):
- LLM-1 Phase-2 (ROME baseline + harness wire-up). ~1 week of script-design work.
- LLM-3 retrieval vs vector DB benchmark. ~2 weeks of engineering.
- LLM-6 hallucination benchmarks against TruthfulQA / HaluEval. ~2-3 weeks integration.
- LLM-2 / LLM-4 / LLM-5 explicitly deferred per post_reset_priority note bandwidth section.

### BE-1 v2 with W-magnitude-operative test:
- Requires NEW script that exercises retrieval accuracy under quantized W (NOT iso pattern). exp_dev needs to: (a) take exp_kf2_isolation_proof_v2_n8192 logic, (b) add `--bit-precision` arg using experiments/_bit_precision.py helper, (c) apply quantize_roundtrip AFTER store BEFORE retrieval, (d) measure retrieval accuracy (not max_iso). This is ~1 day of script-design eng. NOT shippable tonight. File at next strategy cycle.

### Kerdock-even-log2 vulnerable anchors at N=8192:
- All 6+ anchors on v270 consolidated rescue routing remain blocked tonight. Do NOT include in overnight queue.
- Specifically: axis1_mb_chunk9_v1_n8192, axis1_mb_chunk10_v1_n8192_fine, t1_beta_sweep_v2_n8192, t2_codebook_boundary_v2_n8192, t3_susceptibility_v2_n8192 (per v270 routing). Wait for the consolidated rescue to be processed by exp_dev (separate dispatch).

### v272 Region C/D extension to other beta values:
- Region C/D at extreme beta=64 already done. Other beta values for these probes are LOW VALUE per Section 1.2 finding. Do NOT add Region E/F probes to overnight queue.

### v272 BE-1 precision-floor re-ship at different N:
- Per Section 1.1, this is a probe-design problem not a compute problem. Do NOT re-ship BE-1 at N=4096 or N=16384 -- it will return the same quantization-insensitive iso pattern. New test design is the rate-limiter.

---

## 6. PROT compliance pre-check (for exp_dev queue_add)

| Constraint | Mechanism |
|---|---|
| ASCII-only verdict_msg + print() | exp_dev `grep` for non-ASCII chars in each shipped script's print/verdict_msg lines |
| PROT-018 _n<N> binding | exp_dev verifies actual --N arg matches name suffix (queue_add.py exit-6 gate) |
| PROT-019 timeout floor | _n4096 >= 14400s; _n8192 >= 21600s; specified in Section 3a/3b tables |
| HDLAB_EXP_NAME env-var honored | exp_dev verifies each script reads HDLAB_EXP_NAME for output dir naming |
| REMOTE VERIFY post-ship | exp_dev SSH read-back after each queue_add |
| Justification per anchor | Section 3a/3b table column |
| Kerdock-even-log2 audit | Section 3d checklist |
| Ship-name-collision check | exp_dev verifies anchor name unique vs completed-entry prefixes BEFORE queue_add |
| HIGH-importance status_log on dispatch | exp_dev writes status_log entry per [[feedback-for-you-tab-primary-channel]] |

---

## 7. Top-3 highest-leverage anchors (rank-ordered)

1. **G1 kf1_hallu_rescue_v3_n8192** -- KF-1 N-axis replication for green->checkmark elevation; highest product-feature reliability move available tonight.
2. **G2 pb3_extended_v5_n4096** -- PB-3 FLAT_TAU disambiguation; either confirms genuine substrate contradiction (opens new strategic discussion) or rejects v271 artifact (restores cap_map row).
3. **G9 saad_solla_v18_n16384** -- Saad-Solla N=16384 extension; corroborates v16 N=8192 production-scale at 2x N (Kerdock log2=14 SAFE) and is independent of the v19/v20 5th-axis question.

---

## 8. NOT exp_dev's scope (defer to next strategy cycle)

- Deciding whether the Kerdock construction is appropriate for the experiments hitting the even-log2 vulnerability (STRATEGY-level question).
- Building experiments/_w_magnitude_operative_test.py for the BE-1 v2 OPERATIVE test (STRATEGY + exp_dev script-design work outside this routing).
- Deciding band lifts on cap_map rows from G1-G18 verdicts (verdict_handler scope).
- Deciding next-cycle research drills based on v272 + this overnight batch (orchestrator scope).
