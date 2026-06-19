# RESEARCH ROUTING — v341 refresh: rescue re-prioritization + new exciting probes

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev
**Date:** 2026-06-02
**Trigger:** User explicit re-evaluation ask post-compaction. v341 added Cycle 12 (8 verdicts: 4 HP + 3 HF + 1 MIDDLE), changing rescue priorities since v337-v340 fixes routing.
**Supersedes:** rescue priority order in `research_routing_v337_v340_negative_findings_fixes_2026-06-02.md` (Section 6). All v337-v340 specific drills and fixes STAND; only the priority order shifts.
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names full form, sweep grids, queue specifics, timeout) resolved by strategy + exp_dev. Per-PROT compliance.

---

## 0. EXECUTIVE — what v341 changed

**Three new negatives:**
1. **PP-47×PP-49 counterfactual abduction HF** (Phase 0 0c) — HP1 baseline_cos 0.66-0.72 < HP=0.85; PP-47 alpha=0.012 too sparse; **R2 fix = bump K to 100-150** (~10 min CPU).
2. **I-12 κ_3 N=16384 v2 seed-diversity ALSO HF** (0.33) — 2 independent corroborations; **seed diversity ruled out**. Config-delta vs v335 audit is the ONLY remaining cheap path. **NOW LOAD-BEARING** for PP-50 product claim.
3. **I-14 combo1 v3 N=8192 VRAM-friendly ALSO FAILS** (MMD=0.95, k3=11.02) — **math failure at overcomplete α=2.0**, not VRAM. R2 theory-audit cheapest; R3 = re-run at α≤1.0 (M≤N) to localize alpha upper bound.

**Four new positives:**
1. **A5 cert-grade-training-with-rollback HP** — PP-52 3-cap integrated pipeline (audit+rollback+retention) unanimous N=1024 5-seed.
2. **A4 audit-during-training_v2 HP** — PP-52 audit-during-training FULL confirmed N=1024 5-seed.
3. **PP-47×PP-9 deletion-cert composition v2 HP** — Phase 0 0a confirmed (alpha+K=50 with reduced-K). **De-risks Phase 0.5b distillation MVP's audit-primitive composition story.**
4. **PP-49 HRC depth-8 HP** (cf_cos=1.0, all 4 HP unanimous EXACT) — BUT depth-5 HF (cf_cos=0.03). **Non-monotonicity in depth is a novel finding to chase.**

**Strategic shift:**
- **Phase 0.5b distillation MVP** is empirically de-risked by Phase 0 0a HP. Audit-primitive composition at the most product-load-bearing pair (place-field + deletion cert) WORKS. Authorization can fire whenever user gives the go.
- **PP-52 Tier-4 training-speedup row** is gaining 2 confirmed sub-properties (A4 + A5) without empirical Cluster A1/A2/A3 fired yet. **A1/A2/A3 should fire IMMEDIATELY** on next CPU refill — Cluster A framework is empirically working.
- **PP-50 κ_3 product claim is at MORE RISK** than v340 indicated. I-12 v2 corroboration means it's not seed noise. Cloud N=32768 verification (v333 σ_sep up to 1727) and N=16384 collapse (σ_sep 0.32-0.33) must be reconciled before any product positioning.

---

## 1. UPDATED RESCUE PRIORITY ORDER (supersedes v337-v340 routing Section 6)

**HIGHEST — fire NOW, $0, all under 15 min wall:**

1. **I-12 R2 config-delta audit** (v341 ELEVATED) — script-vs-script side-by-side of `exp_kappa3_sensitivity_sweep_n16384_v2` vs v335 Wave 5 Cell 2 Part B. **MANDATORY before any further κ_3 GPU spend.** Outcome routes to (a) trivial config fix + R3 N=16384 re-run, OR (b) PP-50 N-band envelope CAVEAT.

2. **I-14 R2 theory-audit + R3 α=1.0 test** (v341 ELEVATED) — audit implicit-Gram formula scaling at M>N (does Tr(G^3)/M diverge under overcompleteness?). R3: re-run N=8192 M=N=8192 (α=1.0) to confirm hypothesis. If R3 recovers k3_resc≈1, PP-51 production-N envelope = α≤1.0 documented.

3. **Phase 0 0c R2: PP-47×PP-49 with K=100-150** — 10 min CPU; baseline_cos recovery rules in/out the alpha-sparsity hypothesis.

**HIGH — fire as engineering bandwidth allows, $0:**

4. **I-17 COMBO-3 PP-51 cert-path R2 theory audit** (v340 carry; M-side Gram cert formula sign vs N-side Krylov cert).
5. **I-16 PP-49 HRC counterfactual depth-5 R2 script audit** — depth-8 HP + depth-5 HF non-monotonicity is the load-bearing puzzle; R2 first to rule out script bug, then R3 = depth-3/4/6/7 sweep at N=4096 to characterize the depth-band exactly (~30 min CPU).
6. **combo1 α^(p-1) slope rescue R2** (v339 carry; my prior routing's Drill 2 actually says slope=α^1 was correct, HP band was research over-prediction; this is now just a band-adjustment annotation, no GPU needed).
7. **COMBO-4 μ_aging rescue R5** (v338 carry; drill 1 fit-range bug — R1a refit with ratio≥4 predicts μ→0.85; zero-GPU annotation).

**MEDIUM — substrate-product validation pipeline (CPU, fires after A4/A5 confirmation):**

8. **Cluster A1 Hebbian-vs-GD identity** at N=1024 M=100 (~30 min CPU). A4+A5 HP empirically support the framework; A1 is the cleanest substrate-novel "1000× speedup" claim test.
9. **Cluster A2 deletion cert at training scale** K∈{10, 50, 100, 500} M=1000 (~30 min CPU). Extends A5 sub-property to K-sweep.
10. **Cluster A3 counterfactual training diagnostic** via PP-49 (~1 hr CPU). PP-49 depth-8 HP suggests the counterfactual primitive operates correctly; A3 tests at training scope.

**MEDIUM — composition expansions (cheap GPU, fires after MEDIUM CPU passes):**

11. **PP-52 production-N cross-N {4096, 8192, 16384} 5-seed** — band-LIFT eligibility for PP-52 row given A4+A5 sub-property growth.
12. **Q-A3 L=7 N=4096** (L=6 ceiling not reached).
13. **PP-48 NKT depth-9/depth-10** (depth-7 ceiling not reached).
14. **Q-B1 depth-25/depth-30** (depth-20 ceiling not reached).

**LOWER — gated on HIGHEST resolutions:**

15. **Wave 5 Cell 5 CLOUD N=32768** — DOWNGRADE: hold until I-12 R2 resolves. If I-12 reveals config-delta, cloud dispatch fires with verified-good config. If I-12 reveals N-regime envelope, cloud N=32768 spend is the wrong test.
16. **PP-48 + PP-49 cloud combo2-direct N=32768** (carry-forward; not gated on I-12).
17. **I-13 / I-15 / A3-timing / I-7 / PP-47 cross-N N=16384** — carry-forwards; lower priority than the I-12 + I-14 + A1-3 cluster.

---

## 2. NEW EXCITING PROBES (per `feedback_periodic_scope_expansion` + `feedback_aggressive_cross_domain_research`)

### Probe 1 — PP-49 HRC depth-band characterization (CPU, ~30 min, $0)

**Substrate-novel finding worth chasing:** depth-5 HF (cf_cos=0.03) but depth-8 HP (cf_cos=1.0). Same architecture (HRC), same N=4096, same SHIFT. The non-monotonicity is either (a) a depth-5-specific script/config bug, or (b) a real substrate-compositional regime — "compositional valley" where rank-1 substitution fails at intermediate depth but recovers at higher depth.

**Capability question:** at what depth does rank-1 W substitution recover counterfactual retrieval (cf_cos ≥ 0.85), and is the recovery monotone in depth or band-shaped?

**Test:** sweep depth ∈ {3, 4, 5, 6, 7} at N=4096, 5 seeds, same HRC architecture as depth-8 HP anchor. Plot cf_cos vs depth.

**Pre-registered bands per depth:**
- **HARD-PASS:** cf_cos ≥ 0.85 (3/5 seeds minimum at each depth point) — depth-5 was a configuration anomaly
- **MIDDLE:** cf_cos ∈ [0.3, 0.85] for 1-2 depth points adjacent to depth-5 — a transition band exists
- **HARD-FAIL (substrate-novel):** cf_cos ∈ [0, 0.2] across depth∈{4,5,6} bounded by HP at depth≤3 AND depth≥7 — a genuine compositional valley exists, which is itself a publishable substrate finding (depth-dependent rank-1 substitution regime)

**Why this matters:** if HARD-FAIL band confirms, this is a NEW substrate-novel finding about compositional algebra at HRC depth — informs PP-49 product positioning and possibly opens a new cap_map row about depth-dependent counterfactual regimes.

**Cost:** ~30 min CPU at N=4096, 5 seeds × 5 depths. $0.

### Probe 2 — Cluster A1 Hebbian-vs-GD identity at training scale (CPU, ~30 min, $0)

**Already specified** in `research_routing_tier4_training_speedup_small_scale_battery_2026-06-02.md` Section 1.A1. **FIRES NOW** per A4+A5 confirmation. Tests the cleanest substrate-novel "Hebbian write = optimal MSE encoding at 1000× speedup vs GD" claim.

**P_deflated:** 0.70+ (confirmed primitives at known-good regime per the battery's calibration).

### Probe 3 — Reservoir computing cross-framework drill (Research, sonnet, $0)

**Per `feedback_periodic_scope_expansion`:** no cross-framework drill in last 48h. Reservoir computing (echo-state networks, ESN) is the closest cousin to substrate's "passive read-side companion" Tier-7 architecture. ESNs are non-trained dynamic systems with linear readout — substrate at Tier-7 is structurally similar (substrate as read-side, hyperprobe as fixed encoder, LLM as the "reservoir").

**Capability question:** what does the ESN / reservoir computing literature say about (a) audit primitives for dynamic memory traces, (b) compositional algebra on reservoir state, (c) one-shot writes via linear readout, and how does substrate's COMBO-3 unified API map onto reservoir-computing standard primitives?

**Expected outcome:** either (a) substrate is the missing "audit-grade reservoir" the ESN community didn't build, OR (b) prior art in reservoir computing already covers audit primitives and substrate's positioning narrows. Either outcome is product-load-bearing.

**Cost:** ~20 min sonnet research drill, $0.

### Probe 4 — Memristor / neuromorphic-hardware physical realization scan (Research, sonnet, $0)

**Per `feedback_brain_inspired` + `feedback_aggressive_cross_domain_research`:** substrate's bipolar {±1}^N + outer-product Hebbian writes is structurally aligned with crossbar memristor arrays and RRAM physical computing. If substrate's algorithmic primitives map cleanly onto a physical realization, it's a HARDWARE-acceleration angle that no software-only competitor can match.

**Capability question:** which of substrate's primitives (Hebbian write, deletion cert, κ_3 fingerprint, COMBO-3 5-method API) have a documented or feasible memristor/RRAM realization, and what's the projected throughput vs current GPU implementation?

**Expected outcome:** physical-realization angle that adds 10-100× hardware acceleration to substrate's existing 10²-10⁴× algorithmic acceleration claim. Even a partial mapping is product-narrative differentiation.

**Cost:** ~20 min sonnet research drill, $0.

### Probe 5 — Federated unlearning + cryptographic provenance angle (Research, sonnet, $0)

**Substrate's PP-46 deletion cert** + **PP-49 counterfactual abduction** + **PP-48 negative-knowledge tree** compose into a unique "verifiable user-data-removal protocol" for federated learning. GDPR Article 17 (right to erasure) and proposed AI regulations require provable data removal. Substrate may be the first system with algebraic verification primitives.

**Capability question:** what is the federated-unlearning literature state (mid-2025), what cert formats do regulators accept, and where does substrate's algebraic erasure cert sit relative to (a) machine unlearning (Bourtoule 2021), (b) certified removal (Guo 2020), (c) SISA training (recursive removal)?

**Expected outcome:** identifies whether substrate's deletion cert is novel in the regulatory / federated context, OR if it's been beaten by recent SISA / DP-SGD variants. Informs whether substrate's audit-moat positioning extends naturally to federated unlearning.

**Cost:** ~20 min sonnet research drill, $0.

### Probe 6 — Mech-interp tooling angle (Research, sonnet, $0)

**Substrate's κ_3 + PP-49 counterfactual + PP-48 NKT** could serve as a probe-of-probe for interpretability researchers. Tier-7 passive read-side companion is essentially "spectral activation monitoring + counterfactual ablation" — both standard mech-interp tools but typically separately implemented.

**Capability question:** what tools do current mech-interp researchers use (Neel Nanda's TransformerLens, Anthropic's Sparse Autoencoders, Apollo Research's interp-bench), and where does substrate fit as a unified algebraic API for activation monitoring + counterfactual ablation + drift detection?

**Expected outcome:** identifies whether substrate as Tier-7 audit companion has direct user-pull from the mech-interp research community independent of LLM-product positioning. Could be a SECONDARY positioning anchor: "the algebraic substrate for mech-interp research."

**Cost:** ~20 min sonnet research drill, $0.

---

## 3. SEQUENCING (immediate actions)

```
NOW (parallel, $0):
├── I-12 R2 config-delta audit (READ-only main thread or Research)
├── I-14 R2 theory-audit (Research, ~10 min)
├── Phase 0 0c R2 K-bump (~10 min CPU; exp_dev or queue refill)
├── Probe 3 reservoir computing (Research sonnet, ~20 min)
├── Probe 4 memristor/RRAM (Research sonnet, ~20 min)
├── Probe 5 federated unlearning (Research sonnet, ~20 min)
└── Probe 6 mech-interp tooling (Research sonnet, ~20 min)

NEXT (gated on I-12 + I-14 R2 outcomes):
├── If I-12 config-fix: R3 N=16384 re-run with verified config (~5 min GPU)
├── If I-12 substrate-finding: PP-50 N-band envelope CAVEAT + cap_map update
├── If I-14 α=2.0 confirmed math failure: R3 N=8192 α=1.0 (~5 min GPU)
└── Probe 1 PP-49 HRC depth-band sweep (~30 min CPU)

NEXT+1 (gated on the above + standing user authorizations):
├── Cluster A1 Hebbian-vs-GD identity (~30 min CPU)
├── Cluster A2 deletion cert at training scale K-sweep (~30 min CPU)
├── Cluster A3 counterfactual training diagnostic (~1 hr CPU)
└── Phase 0.5 + 0.5b combined cloud bundle (USER AUTHORIZED; ~$70-140)
```

**Total NOW-step cost:** $0 cloud + ~1.5-2 hr engineering across parallel dispatches.

---

## 4. WHAT CHANGED IN MY PRIOR RESPONSES (re-evaluation honest summary)

**Still load-bearing from v337-v340 routing:**
- All 4 research drills landed; findings stand (μ_aging fit-range, slope=α^1 was correct, cert sign formula audit, κ_3 observable mismatch). Drill 4's "observable mismatch" hypothesis is now WEAKENED by I-12 v2 corroboration — config-delta is the more likely culprit, NOT just an observable-definition difference. R2 will distinguish.
- 5 engineering fixes (I-13/I-14/I-15/A3/I-16) all stand; I-14 escalates per v341.
- Composition boundary annotations (COMBO-1 PP-48 audit-on-NKT; possibly I-16 if R2 confirms) stand.
- Systemic pre-framing fix recommendation stands (v341 had 0 catches — encouraging early sign).

**Re-prioritized:**
- I-12 was MEDIUM in v337-v340 routing; **now HIGHEST** (2 HF confirmations).
- I-14 was MEDIUM (R2 SSH OOM); **now HIGHEST** + scope changed (math failure not VRAM).
- Wave 5 Cell 5 cloud + PP-48/49 cloud combo2-direct: were MEDIUM; **DOWNGRADED to gated on I-12 R2** (don't spend $$$ on N=32768 GPU until N=16384 collapse is resolved).
- Cluster A1/A2/A3: were "fires immediately on next CPU refill" (per Cluster A/B/C battery routing); **now MORE URGENT** because A4+A5 just HP'd, framework empirically validated.

**Net assessment:** my v337-v340 fixes routing was correct at the time but understimated I-12 + I-14 severity. v341 corroborations elevate both to HIGHEST. The Phase 0 0a HP de-risks Phase 0.5b distillation MVP significantly — that's the strongest positive of v341. The PP-49 HRC depth-5 vs depth-8 non-monotonicity is an unexpected new finding worth dedicated characterization (Probe 1).

---

## 5. DISCIPLINE DECLARATIONS

- Capability questions only; HP/MIDDLE/FAIL bands pre-registered (Probe 1 explicit; Cluster A1/A2/A3 already specified; cross-domain drills are research drills not empirical tests).
- Per `feedback_rescue_sketch_first_sequencing`: R1 annotations applied inline above; R2 cheap theory/script audit SECOND for all 3 v341 negatives.
- Per `feedback_negative_results_2x_research`: I-12 v2 corroboration triggers 2x research drill (R2 config-delta audit is the first; if it returns "no config delta", dispatch a 2x deep research drill on κ_3 N-scaling theory at N=16384 specifically).
- Per `feedback_periodic_scope_expansion`: 4 cross-domain drills (Probes 3-6) dispatched concurrently for breadth.
- Per `feedback_aggressive_cross_domain_research`: cross-domain probes are $0; dispatched even when no specific trigger because free capacity exists.
- Per `feedback_no_smoke_preframing_in_task_prompts`: all empirical tests have HARD-PASS/MIDDLE/HARD-FAIL pre-registered; no pre-framing.
- Per `feedback_obey_user_pause_explicitly`: pause flag ABSENT (verified); routine pipeline-pacing allowed.
- Per `feedback_lit_scan_calibration_penalty`: cross-domain drill outputs deflated 0.15-0.25; novel-synthesis cap 0.50 unless lit-scan reveals direct precedent.
- Per `feedback_no_papers_product_only`: cross-domain drills frame as product-capability scoping (not publication-grade).

---

## 6. CAP_MAP IMPACT EXPECTATIONS

If HIGHEST + HIGH all fire and resolve:
- **PP-50 N-band envelope decision** (CAVEAT vs config-fix) — load-bearing for product positioning
- **PP-51 alpha upper bound documented** at N=8192 (α≤1.0 implicit-Gram cleanly works)
- **Phase 0 0c HP** (post K-bump) — composition algebra confirmed for PP-47×PP-49
- **PP-49 HRC depth-band characterization** — new sub-property "depth-monotone" OR new finding "compositional valley at depth-band"
- **I-16/I-17 R2 outcomes** — composition boundary annotations
- **No row closures** — all findings get R1-R5 before closure consideration

If MEDIUM all PASS:
- **PP-52 row band-LIFT** eligibility (3+ confirmed sub-properties: A4, A5, A1, A2, A3)
- **Q-A3 L=7 + PP-48 depth-9/10 + Q-B1 depth-25/30** push composition ceilings outward

---

**END.** Orchestrator: queue HIGHEST 3 actions IMMEDIATELY (parallel; $0; ~1.5 hr total wall). Dispatch 4 cross-domain Research probes (Probes 3-6, parallel sonnet, $0). Hold cloud spend gated on I-12 + I-14 R2 outcomes. Strategy: hold cap_map updates pending HIGHEST resolutions; v341 state correct as-of-this-routing. exp_dev: cell design for Probe 1 + Cluster A1/A2/A3 + I-12/I-14/0c R3 from capability questions above.

Drill outputs from Probes 3-6 will land within ~20 min from dispatch; research will surface to orchestrator at landing.
