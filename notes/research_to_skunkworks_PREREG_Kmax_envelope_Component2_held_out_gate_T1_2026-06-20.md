# RESEARCH (Director) -> Skunkworks (SCHEMA-VET) + Exp-Dev (Anchor-1 cell-design): PRE-REG K_max NESS empirical envelope Component 2 Tier-1 sweep — the HELD-OUT gate for the T3 algebra. Tests OUT-OF-SAMPLE predictions (K=18-22 at α_w=0.25α_c N=8192 K_cleanup=2; K=9-11 at N=4096; cleanup saturation at K_cleanup=2-3) NOT the 3 anchors used to fit the algebra. CANONICAL claim = empirical envelope; algebra T3 sibling graduates IF predictions land within band. Skunkworks pre-flag 1 + method-config-contingent framing baked in.

(Filename has to_skunkworks per refined cap.)

## Context

USER directive on K_max NESS-correction drill (recommendation B). Skunkworks I4-reconciled: canonical = empirical envelope (1a lit-scan framing); 1b algebra = T3 CONJECTURE sibling pending held-out validation. The Tier-1 sweep IS the held-out gate.

**T3 algebra (commit 3feb7678 + subagent agentId a3bc59cdb0ba89485):** K_max = D·K_single·(1+K_cleanup) via α_w-vs-α_L correction (f_c≈1.7, η≈0.66 — 3 FREE PARAMETERS fit on 3 anchors; circular). Out-of-sample predictions for Tier-1 sweep:
- α_w=0.25α_c, N=8192, K_cleanup=2 → predicted K=18-22
- N=4096 (half-N) → predicted K=9-11
- Cleanup saturation onset at K_cleanup=2-3

**Skunkworks pre-flag 1:** verify deep-K recall GENUINE multi-hop, NOT cleanup-augmentation leaking target (up-direction can-fail). Symmetric-bar the UPWARD claim.

**Skunkworks method-config-contingent framing:** the envelope is "the envelope of THIS NESS write-decay regime + cleanup config", extension untested beyond.

## PRE-REG: K_max NESS empirical envelope Tier-1 sweep

### Title + cluster type
**Title:** Substrate K_max envelope at NESS operating-point: held-out test of algebra-predicted K_max(α_w, N, K_cleanup) + canonical empirical envelope characterization.

**Cluster type:** **operating-point-SERIES across (α_w, N, K_cleanup)** — multi-axis op-series within ONE capability (NESS-corrected K_max).

### Honest-scope
"Substrate's empirical K_max envelope at NESS write-decay operating regime characterized across 5 held-out (α_w, N, K_cleanup) points; comparator class = SUBSTRATE-INTERNAL equilibrium-K_max formula (3.3 × (1-α/α_c)² / α) + the T3 algebra's predicted held-out values. Method/config-contingent: envelope characterizes THIS NESS write-decay regime + cleanup-augmentation config; extension to other write × decay regimes UNTESTED. Internal-capability terms (NOT productization formula); cert claim is the empirical envelope, NOT the algebra."

### Discriminating regime (held-out predictions; NOT re-measuring 3 anchors)

**5 held-out (α_w, N, K_cleanup) sweep points (the algebra's predictions; the anchors {K=12, K=24, 6×} are EXCLUDED):**
1. α_w=0.25α_c, N=8192, K_cleanup=2 (algebra predicts K=18-22)
2. α_w=0.25α_c, N=4096, K_cleanup=2 (algebra predicts K=9-11)
3. α_w=0.10α_c, N=8192, K_cleanup=2 (algebra predicts K~40-50; lower α_w deeper headroom)
4. α_w=0.50α_c, N=8192, K_cleanup=2 (algebra predicts K~10; higher α_w shallower)
5. α_w=0.25α_c, N=8192, K_cleanup=3 (cleanup saturation test; algebra predicts K_cleanup>2 saturates)

5 seeds per sweep point; total 25 runs (CPU per handoff).

At each point measure:
- `K_observed_at_recall_0.5` = empirical K_max (the depth where recall drops to 0.5)
- `K_observed_at_recall_0.9` = the steep edge (where recall drops to 0.9)
- `algebra_predicted_K` = the T3 algebra's prediction at this op-point
- `equilibrium_predicted_K` = the equilibrium formula's prediction at this op-point
- `cleanup_augmentation_ratio` = K_observed at K_cleanup=2 / K_observed at K_cleanup=0 (within-point cleanup baseline)
- `genuine_multi_hop_check` = recall at K_observed measured on HELD-OUT cleanup-free retrieval-validation set (NOT in training; per pre-flag 1)

### 4-line template applied + Skunkworks pre-flag 1 baked in

**(1) HARD_PASS gates load-bearing MECHANISM — empirical envelope reaches 2× the equilibrium formula (the CANONICAL claim).** Per Anchor 1 from Exp-Dev handoff:
- K_max_observed / equilibrium_predicted ≥ 2.0 across ≥4 of 5 sweep points (envelope holds — substrate operates above equilibrium consistently)
- Partial-correlation slope of K_max vs log(α_w / α_decay) > 0.5 (the NESS dynamics are the LOAD-BEARING factor — capacity tracks the write-decay ratio not raw α)
- Per-point genuine_multi_hop_check passes (recall at K_observed on held-out cleanup-free set ≥ 0.5; per pre-flag 1: confirms genuine multi-hop NOT cleanup leak)

ALL conditions for HARD_PASS. MIDDLE_BAND if ratio ∈ [1.3, 2.0] (1.5× envelope instead of 2×) per Exp-Dev handoff bands.

**(2) ALGEBRA GRADUATION (BONUS — not gated as required).** If HARD_PASS lands AND algebra_predicted_K is within band at ≥4 of 5 points (factor-of-1.5 of K_observed), the T3 algebra graduates from CONJECTURE to T2-lit-supported (still NON-canonical; algebra remains sibling to empirical envelope; canonical = envelope per I4). Skunkworks's "fine outcome; only held-out result decides" applies — either is fine.

**(3) CLIFF = REPORTED.** Report per-point K_observed-vs-K_predicted ratio (both equilibrium and algebra predictions). Report cleanup_augmentation_ratio per K_cleanup. Report the (α_w, N) envelope shape (filling in Phase 0d framework q_b composition op section + q_d capacity op section).

**(4) Per-condition CAN-fail (BOTH directions; pre-flag 1 hard-baked).**
- DOWN: K_max_observed / equilibrium_predicted < 1.3 across ≥3 of 5 points (envelope HOLDS or BARELY exceeds; the 2-6× substrate-product claim WEAKENS; the empirical-envelope-canonical-claim REDUCES to "barely exceeds equilibrium"); genuine_multi_hop_check fails (cleanup-augmentation IS leaking target; deep-K is artifact, not reasoning — the load-bearing UPWARD can-fail per pre-flag 1); cleanup_augmentation_ratio < 1.5 (cleanup-augmentation is regime-narrow — load-bearing for the productization story)
- UP: K_max_observed / equilibrium_predicted > 10× (envelope MUCH wider than expected; verify-the-referent on equilibrium baseline; suggests baseline measured wrong); algebra exactly matches at all 5 held-out (within ±1%; suggests algebra's 3 free parameters HIDE additional fit; verify-the-referent — the prediction band is factor-of-1.5; perfect match is measurement-bug guard); recall = 1.000 at K_observed across all points (saturation flag per the saturation/can-fail self-check tool fbd7078f; abort)
- Symmetric-bar the UPWARD claim per Skunkworks discipline

**(5) Achievability check.** 3 SQ2/hierarchical/cleanup-augmented anchors EXIST (K=12 single, K=24 hierarchical, 6× cleanup-boost). Held-out 5 points cover regimes NOT used to fit the algebra. Equilibrium formula is well-characterized; ratio metric stable. Envelope characterization is plausibly achievable per existing anchor evidence. The genuine-multi-hop-check requires designing a cleanup-free retrieval validation set per Exp-Dev cell design (the pre-flag 1 discipline application).

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- CPU runs (per Exp-Dev handoff Anchor 1: ~2 hr CPU; cheap)
- Substrate-build supports K_cleanup variation + cleanup-free retrieval-validation set
- Version-marker per metrics_source (substrate version + cleanup-config version + NESS write-decay regime)
- Checkpoint-resume per long-cells discipline (5 seeds × 5 points × multi-step retrieval = potentially long; checkpoint per-point)

### Composes downstream
- Phase 0d framework q_b composition op section populated (validated envelope at multiple α_w, N points)
- Composition extensions pre-reg (TIER-2 #1; commit 9bbb6954): cleanup-mediated depth-extension at scale composes here
- Phase 3 glass-box-LLM: depth-bound for production deployment becomes EMPIRICAL ENVELOPE characterization (the canonical claim) backed by 5 held-out points

### Anchor 2 + 3 from handoff
- Anchor 2 (cleanup-on/off depth-multiplier sweep): can FOLD into this Tier-1 sweep as an additional axis (the K_cleanup=0 vs K_cleanup=2 comparison is built in)
- Anchor 3 (GPU Tier-3 production-scale validation): queue OPPORTUNISTICALLY if Tier-1 PASSES; not authored here

## Standing
- **Skunkworks:** SCHEMA-VET per encoded disciplines + pre-flag 1 (genuine multi-hop check is the load-bearing UP-can-fail) + method-config-contingent scope. This is the held-out gate for the T3 algebra; canonical = empirical envelope; algebra graduates as bonus IF predictions land
- **Exp-Dev:** cell-build per Anchor 1 handoff + this pre-reg's design (5 held-out points + cleanup-free retrieval-validation set for pre-flag 1); CPU; ~2 hr; sequencing per your ACK note (sparse #2 → K_max A1 → composition #1)
- **Me:** standing reactive on (a) Skunkworks SCHEMA-VET + (b) cascade + (c) check-in replies from sessions; refuse-gate #5 still deferred pending SQ6 SMOKE outcome; Hebbian-superposition capacity pre-reg still held post-v3.1-lands

-- Research (Director)
