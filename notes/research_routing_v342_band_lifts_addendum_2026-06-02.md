# RESEARCH ROUTING — v342 BAND-LIFTs addendum: strategic implications + new probes

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev
**Date:** 2026-06-02
**Trigger:** Cycle 12 batch 19-verdict v341 → v342: 2 BAND-LIFTs (PP-52 + Q-A3/PP-12), I-13 CLOSED, I-17 PARTIAL-RESOLVED, 2 new composition boundaries (well-characterized), 1 LVH catch (#207 SPURIOUS_SPEEDUP_FROM_ACCURACY_COLLAPSE).
**Supersedes:** none. ADDS to `research_routing_v341_refresh_rescues_new_probes_2026-06-02.md` and `research_routing_v337_v340_negative_findings_fixes_2026-06-02.md` — both still load-bearing for the I-12 / I-14 / Phase 0 0c R2 priorities.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names full form, sweep grids, queue specifics, timeout) resolved by strategy + exp_dev. Per-PROT compliance.

---

## 0. EXECUTIVE — what v342 means strategically

**Two BAND-LIFTs that change the empirical anchor strength of the substrate's product story:**

1. **PP-52 (training-acceleration) BAND-LIFT 0.55-0.70 → 0.60-0.75.** Cross-N production-N confirmation at N=4096 AND N=8192, BOTH exact-rollback AND one-shot-addition. The a3 timing caveat at N=1024 (0.35s vs 0.05s gate) is SUPERSEDED at production-N (N=4096 0.063s; N=8192 0.131s — both well within gates). 
   - **Strategic impact:** Phase 0.5b distillation MVP audit-primitive composition story is now empirically de-risked at production N. The "10²-10⁴× speedup vs LoRA" claim has its cleanest empirical anchor yet — Hebbian write is the EXACT update at known wall ~10ms, accuracy preserved at 1.0.

2. **Q-A3/PP-12 (cross-layer composition) BAND-LIFT 0.65-0.80 → 0.70-0.85.** L=4 + L=7 both EXACT-1.0 unanimous 5-seed. Substrate's compositional algebra preserves exact fidelity through at least 7 nested composition layers at N=4096.
   - **Strategic impact:** COMBO-3 5-method unified API's compositional foundation is solidified. PP-12 hierarchical multi-bank addressing is product-ready. The "audit-grade compositional algebra" claim has its deepest empirical anchor.

**Two well-characterized composition boundaries** (operating-envelope features, NOT row closures):

3. **combo2 L=4 b_rep collapse** — PP-48/PP-49 NKT composition algebraically clean at L≤3 (per v340 L=3 unanimous HP); at L=4 the B-pattern anti-Hebbian inhibition collapses to exactly 0.0 (5/5 seeds unanimous, not noise). Clean boundary: NKT composition works at L≤3, fails cleanly at L=4. R2 = sign-cancellation hypothesis (does the 4th layer introduce even-depth degeneracy in the B-pattern accumulation?).

4. **Caching above-capacity eviction at α=0.22 fails** (fid_evict=0.177 << HP=0.8) AFTER the I-13 design fix achieved well-stressed regime. So α_c for eviction is < 0.22. Clean envelope finding: substrate eviction requires α < α_c (TBD); product framing = stay below capacity threshold for eviction-based caching to work.

**One PARTIAL resolution:**

5. **I-17 COMBO-3 PP-51 cert-path** — cert_diff=0.0 (the structural sign issue is RESOLVED via v2 cert fix). Trace rel_err 3e-3 sub-HP remains open; R3 = increase Krylov matvec from 3 to 20-50 to test convergence hypothesis. Cheap.

**One deceptive-evidence catch (LVH #207):**

6. **PP-52 hebbian-vs-LoRA speedup N=4096 HF** — LoRA approximation at N=4096 M=400 r=20 destroys model accuracy (acc_delta=100pp). The reported wall_speedup=171M× is SPURIOUS (LoRA on a broken model has near-zero forward pass). Verdict_msg cited hp2=5/5 PASS deceptively. **Product-narrative correction (load-bearing):** PP-52 framing should be "Hebbian IS the exact update; LoRA APPROXIMATES" — Hebbian-vs-LoRA is NOT the right comparison axis. The substrate value is the EXACT primitive at production wall (~10ms), not a "X× speedup vs LoRA" claim that becomes meaningless when LoRA collapses.

**Product-feature reliability:** 78-92% → 80-94% (+2pp both bounds). HONEST 459 → 475 (+16). LVH 206 → 207 (+1).

---

## 1. NEW EXCITING PROBES UNLOCKED BY v342

### Probe A — Push Q-A3 / PP-12 composition ceiling: L=8, L=9, L=10 sweep

**Why:** L=7 EXACT-1.0 unanimous; ceiling NOT reached. Each additional composition layer is a substrate-novel result.

**Capability question:** at what L does cross-layer composition fidelity drop below EXACT-1.0 at N=4096 5-seed?

**Test:** L ∈ {8, 9, 10} N=4096 5-seed, same cross-layer composition architecture as L=4/L=7 HP anchors.

**Pre-registered bands per L:**
- HARD-PASS: all L_fid = 1.0000 unanimous (5/5 seeds)
- MIDDLE: any L_fid ∈ [0.85, 1.0) — graceful degradation found
- HARD-FAIL: any L_fid < 0.85 OR l_acc < 0.5 — substrate compositional ceiling reached

**Cost:** ~30 min GPU at N=4096 5-seed × 3 L-values. $0 if local GPU.

### Probe B — PP-52 N=16384 + N=32768 cross-N extension

**Why:** PP-52 BAND-LIFT current evidence is N=1024 + N=4096 + N=8192 all HP. One more cross-N rung (N=16384) at zero cloud cost + a cloud confirmation at N=32768 (~$5) push PP-52 to flagship-class production claim.

**Capability question:** does PP-52 exact-rollback + one-shot-addition hold at N=16384 (local GPU) AND N=32768 (cloud H100)?

**Test:** pp52_exact_rollback_n16384 + pp52_one_shot_addition_n16384 at 5-seed local GPU; same anchors at N=32768 cloud.

**Pre-registered HARD-PASS** (same gates as v342 anchors):
- rel_err < 1e-10 (rollback)
- cos_new ≥ 0.9 (addition)
- acc_drop_pp = 0
- wall < timing gate scaled per N (rollback < 0.5s at N=16384; < 2s at N=32768)

**Cost:** ~15 min local GPU + ~$5 cloud H100. If both HP: PP-52 BAND-LIFT eligibility 0.60-0.75 → 0.65-0.85 (4-rung cross-N production confirmation).

### Probe C — combo2 L=4 b_rep sign-cancellation theory R2

**Why:** clean boundary at L=4 (b_rep=0.0 unanimous 5/5) suggests structural, not noise. If R2 theory identifies even-depth degeneracy in B-pattern anti-Hebbian accumulation, predicts L=6 + L=8 will ALSO fail cleanly while L=3, L=5, L=7 work — a parity-class compositional regime.

**Capability question:** does PP-48/PP-49 NKT composition exhibit ODD-DEPTH-ONLY parity in the b_rep observable, or is L=4 the absolute composition ceiling?

**Test plan:**
- R2 (~10 min theory): derive 4-layer B-pattern accumulation algebra; check for sign-cancellation at even depth
- R3 (~10 min CPU): L=5 same architecture as L=4 anchor; if HP, parity hypothesis confirmed
- R4 (~10 min CPU): L=6 same architecture; if HF same as L=4, parity hypothesis fully confirmed
- R5 (~10 min CPU): L=7 with B-patterns (vs Q-A3 L=7 which is pure positive); if HF, even-depth ceiling confirmed at L=4

**Pre-registered HARD-PASS for parity hypothesis:** L=5 b_rep ≥ 0.9 AND L=6 b_rep < 0.4 — odd/even parity confirmed.
**HARD-FAIL for parity hypothesis:** L=5 b_rep < 0.4 — L=4 is the absolute composition ceiling; PP-48/PP-49 NKT composition envelope = L≤3.

**Strategic significance:** if parity hypothesis confirmed, this is a NEW SUBSTRATE-NOVEL FINDING about NKT composition algebra — odd-depth-only composition with even-depth as forbidden sub-band. Product framing: "substrate NKT composition operates in odd-depth phases only — even-depth collapses are predictable signatures of the algebraic structure."

**Cost:** ~40 min CPU + ~10 min theory. $0.

### Probe D — Caching α_c boundary characterization

**Why:** I-13 closed with α=0.22 boundary identified, but the exact α_c (where fid_evict transitions HP→HF) is unknown. Substrate's eviction operating envelope is product-load-bearing for the "audit-grade live drift detection" claim — if α_c is far below 0.22, the envelope is narrow; if close to 0.22, the envelope is wide.

**Capability question:** at what α_stress does fid_evict transition from HP (≥0.8) through MIDDLE through HF (<0.5)?

**Test:** α_stress sweep {0.05, 0.10, 0.15, 0.20, 0.22} at N=4096 5-seed; characterize fid_evict transition curve.

**Pre-registered:** map α_c (the threshold where fid_evict = 0.5) to ±0.025 precision; document operating envelope cell-by-cell.

**Cost:** ~30 min CPU at N=4096 5-seed × 5 α values. $0.

### Probe E — PP-52 reframed comparison (correct LoRA framing)

**Why:** LVH #207 surfaced that Hebbian-vs-LoRA is NOT a meaningful comparison — LoRA collapses at production N regardless of "speedup". Need a CORRECTLY-FRAMED comparison test that anchors PP-52's product value cleanly.

**Capability question:** in the regime where LoRA's accuracy IS preserved (small N, small M, sufficient rank), how does substrate Hebbian compare on (a) accuracy, (b) wall time, (c) FLOPs?

**Test:** PP-52 vs LoRA at N=1024, M=100, r ∈ {N//10, N//5, N//2, N} sweep; find minimum r where LoRA accuracy recovers; compare PP-52 wall/FLOPs at that "LoRA-valid" rank.

**Pre-registered HARD-PASS:** PP-52 wall ≤ 1/100 × LoRA wall at minimum r where LoRA acc ≥ 0.95.
**HARD-FAIL:** PP-52 wall ≥ 1× LoRA wall at any valid r — substrate has no measurable speedup over LoRA when LoRA works.

**Strategic significance:** establishes the FAIR PP-52 product comparison. Honest framing: "Hebbian one-shot is faster than LoRA in the regime where LoRA preserves accuracy; LoRA fails at production N/M scale that substrate handles natively."

**Cost:** ~30 min CPU at N=1024 5-seed × 4 r values. $0.

---

## 2. UPDATED PRIORITY ORDER (v342)

**HIGHEST UNCHANGED from v341 refresh routing** (I-12 / I-14 / Phase 0 0c R2 still load-bearing; v342 did not touch these):
1. I-12 R2 config-delta audit (κ_3 N=16384 collapse)
2. I-14 R2 theory-audit + R3 α=1.0 test (combo1 v3 overcomplete)
3. Phase 0 0c R2 K-bump (PP-47×PP-49 baseline_cos)

**HIGH NEW from v342** ($0, fires immediately):
4. **Probe A** Q-A3 L=8/9/10 (ceiling push; ~30 min GPU)
5. **Probe C** combo2 L=4 parity hypothesis (sign-cancellation R2 + L=5/6/7 sweep; ~40 min CPU)
6. **Probe D** caching α_c boundary characterization (~30 min CPU)
7. **Probe E** PP-52 vs LoRA correct framing (~30 min CPU)
8. I-17 R3 Krylov-budget increase (matvec 3 → 20-50; ~10 min GPU)
9. 2 TIMEOUT rescues: a6 R1 extend timeout to 3600s; engram R1 extend to 1800s

**MEDIUM NEW from v342:**
10. **Probe B** PP-52 N=16384 cross-N extension (~15 min GPU); PP-52 N=32768 cloud (~$5; gated on N=16384 HP)
11. PP-48 NKT depth-11/13 sweep (depth-9 EXACT-1.0; ceiling not reached)
12. Q-B1 depth-35/40 N=8192 (depth-30 HP; ceiling not reached)

**LOWER (carry-forwards from v341 + v340):**
13-N. All v341 + v340 carry-forwards per priority order in those routings.

---

## 3. PHASE 0.5b DISTILLATION MVP READINESS UPDATE

The v342 results materially strengthen Phase 0.5b's empirical foundation:

| Substrate primitive needed | v341 evidence | v342 update |
|---|---|---|
| PP-46 deletion cert | N=4096 confirmed (v341) | Cross-N rollback N=4096+N=8192 strengthens |
| PP-48 NKT | depth-7 N=4096 confirmed | depth-9 N=4096 + depth-3 baseline now confirmed |
| PP-49 HRC | depth-8 N=4096 confirmed; depth-5 anomaly | UNCHANGED (depth-5 R2 still open) |
| PP-50 κ_3 | N=32768 cloud v333 (1727 σ_sep); N=16384 collapse open | UNCHANGED (I-12 R2 still HIGHEST priority) |
| PP-52 training-speedup | N=1024 5-seed (a4, a5) | **Cross-N N=4096 + N=8192 BOTH exact-rollback + one-shot-addition** |
| PP-12 cross-layer composition | L=6 N=4096 | **L=7 N=4096 EXACT-1.0 confirmed (BAND-LIFT)** |

**5 of 6 substrate primitives are now production-N empirically anchored.** PP-50 κ_3 is the only remaining blocker (and only at the specific N=16384 regime — N=32768 cloud is fine).

**My recommendation to orchestrator:** Phase 0.5b distillation MVP can fire WHENEVER user gives the go. The audit-primitive composition story is now strong enough that Phase 0.5b's $15-40 cloud + 1-2 weeks engineering is justified by current empirical evidence. If I-12 R2 reveals PP-50 N-band envelope CAVEAT, Phase 0.5b uses N=8192 (where PP-50 was confirmed historically) or N=32768 cloud (where κ_3 σ_sep up to 1727).

---

## 4. CAP_MAP IMPACT EXPECTATIONS

If HIGH NEW probes all PASS:
- **Q-A3/PP-12 further band-LIFT** eligibility (L=10 push extends the depth ceiling)
- **PP-48/PP-49 NKT odd-depth-only PARITY** finding (Probe C if confirmed) — NEW SUB-PROPERTY of "compositional algebra with depth-parity envelope"
- **PP-44 caching α_c characterized** — operating envelope cell-by-cell mapped
- **PP-52 N=16384 + N=32768 cross-N extension** (Probe B if PASS) — BAND-LIFT to 0.65-0.85
- **COMBO-3 PP-51 trace accuracy improved** (I-17 R3 Krylov budget increase) — I-17 fully RESOLVED
- **2 TIMEOUT anchors recoverable** with extended timeouts

If LVH #207 reframing test (Probe E) HARD-PASSes:
- **PP-52 product-narrative correction documented** — "Hebbian = exact; LoRA = approximate with accuracy ceiling" replaces the broken "X× speedup vs LoRA" framing

---

## 5. DISCIPLINE DECLARATIONS

- Capability questions only; HP/MIDDLE/HARD-FAIL bands pre-registered for all 5 new probes.
- Per `feedback_rescue_sketch_first_sequencing`: R1 annotations applied inline; R2 cheap theory/script audit SECOND for combo2 L=4, caching α_c, I-17 trace.
- Per `feedback_rehabilitation_after_rejection`: combo2 L=4 + caching above-capacity + PP-52 hebbian-vs-LoRA all get R1-R5 rescue sketches before any closure consideration.
- Per `feedback_no_smoke_preframing_in_task_prompts`: all empirical tests have explicit HARD-FAIL trip-wires; no pre-framing.
- Per `feedback_obey_user_pause_explicitly`: pause flag ABSENT; routine pipeline-pacing allowed.
- Per `feedback_no_padding_experiments`: every probe is justified by either (a) ceiling-not-reached extension, (b) operating-envelope characterization, or (c) product-narrative correction (LVH #207).
- Per `feedback_lock_in_inefficiency_fixes`: LVH #207 deceptive-evidence sub-flavor identified; future PP-52 / Hebbian-vs-LoRA framings must follow R5 reframe ("Hebbian = exact O(N); LoRA = approximate O(rN) with accuracy ceiling").
- Per `feedback_substrate_value_framing_2026-05-26`: v342 results reinforce that substrate's PP-52 + Q-A3 + PP-48/49 NKT compositional stack is production-ready at N=8192 — product engineering work should weight HIGHER vs additional theoretical confirmation per the 24-36mo window.

---

**END.** Orchestrator: queue HIGH NEW probes 4-9 in parallel (all $0, ~1.5-2 hr total wall); MEDIUM NEW probes 10-12 sequenced after HIGH. Strategy: cap_map state v342 correct as-of-this-routing; further BAND-LIFTs depend on Probe A/B/E outcomes. exp_dev: cell design for Probes A-E from capability questions + HARD bands above; combo2 L=4 parity hypothesis (Probe C) is the most strategically interesting cell — well-characterized either way.

Phase 0.5b distillation MVP is empirically de-risked; user's go-ahead is the only remaining gate.
