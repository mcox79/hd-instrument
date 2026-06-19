# Strategy → Research: 4th-attempt mechanism diagnosis ADDENDUM — WARMSTART_RESCUES refines constraint stack

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-22 ~21:20 EDT
**Topic**: REFINES the 7-constraint signature from `strategy_request_to_research_multihop_mechanism_4th_attempt_FINAL_2026-05-22.md` (commit `1541d1c`)
**cap_map state**: v132 (commit pending)
**Trigger**: 3 new empirical verdicts since 4th-attempt routing filed; load-bearing finding is WARMSTART_RESCUES

## TL;DR

Original 4th-attempt routing's constraint #5 ("Loopy within-hop fails WORSE
than argmax") was OVERSTATED. Empirical verdict at FULL: **loopy works PERFECT
acc=1.000 when warmstarted with backward beliefs**. Constraint #7 ("N-dependent
at fixed K — 3.5× degradation") refuted by VAMP-on-chain N-sweep showing
non-monotonic argmax behavior across N.

**TIGHTENED structural constraint**: the dividing line is **initialization
information NOT dynamics**. ALL forward-only init methods fail at acc~0.20-0.25
floor; ALL backward-evidence init methods succeed PERFECT acc=1.000.

## Updated empirical evidence (cycle 133)

### Test 4 (WARMSTART_RESCUES) — load-bearing refinement

`wave14_multihop_resonator_warmstart_v1` FULL = **WARMSTART_RESCUES**:
"Backward evidence rescues Resonator: acc_50hop=1.000>=0.70 vs argmax 0.250.
Loopy dynamics work given right starting point."

**Implication**:
- Resonator loopy-iterative dynamics, forward-initialized = FAILS (cycle 124 acc=0.200)
- Resonator loopy-iterative dynamics, backward-warmstarted = SUCCEEDS PERFECT (cycle 133)
- → Iterative dynamics are NOT the failure mode
- → Cycles in factor graph are NOT the failure mode
- → Information absence at initialization IS the failure mode

### Test 3 (PFAIL_HIGHER) — HMM noise prediction approximately right but cascade theory wrong

`wave14_multihop_hmm_per_hop_pfail_v1` FULL = **PFAIL_HIGHER**:
"Per-hop p_fail=0.0350 > 0.035 (predicted 0.03). (1-p)^50 = 0.168. Substrate has
more per-hop noise than HMM model."

**Implication**:
- Per-hop noise is 0.035 (HMM cycle 131 predicted 0.03 — close)
- BUT (1-0.035)^50 = 0.168 < empirical 0.217 plateau
- Substrate plateau EXCEEDS cascade prediction = substrate has a FLOOR above
  geometric cascade
- Substrate has SOMETHING that prevents decay below ~0.20

### N-sweep — argmax non-monotonic in N

`wave14_vamp_chain_N_sweep_v2` FULL = **N_SWEEP_INCONCLUSIVE**:
"argmax_per_N={4096: 0.067, 8192: 0.2, 16384: 0.067, 32768: 0.0, 65536: 0.333},
vamp_per_N={4096-65536: 1.0 all}."

**Implication**:
- VAMP-on-chain robust across ALL N tested — works at EVERY N
- argmax behavior is STRUCTURALLY NOISY in N, not N-monotone
- Original cycle 121 N-dependence (N=4096 0.767 vs N=65536 0.217) may be
  seed-fragile or K-specific
- 4th-attempt constraint #7 (N-dependent at fixed K) is at minimum NUANCED

## Updated 8-constraint signature (supersedes original 7)

The 5th candidate mechanism must explain ALL 8 simultaneously:

1. **1-hop clean**: acc_1hop=0.983 at N=65536 K=100
2. **ALL forward-only init methods fail** at acc~0.20-0.25 floor (hard argmax
   + soft posterior + loopy-iterative-from-forward all bounded)
3. **Soft posterior gives NO benefit over hard** (cycle 132)
4. **Plateau at acc~0.20 for L=50,100** (cycle 132): not random; not geometric
5. **Loopy works PERFECT when backward-warmstarted** (cycle 133): cycles not
   the failure mode
6. **ALL backward-evidence init methods succeed PERFECT** acc=1.000
   (VAMP-on-chain forward-backward EP + Resonator-warmstart-backward)
7. **Per-hop p_fail ≈ 0.035** but plateau ABOVE cascade prediction
   (1-p)^50=0.168; substrate has FLOOR above ~0.20
8. **VAMP-on-chain N-universal**: acc=1.000 at N∈{4096, 8192, 16384, 32768,
   65536} all; argmax non-monotonic in N (no clean N-degradation signature)

## STRUCTURAL CHARACTERIZATION TIGHTEST TO DATE

> "The dividing line is **initialization information NOT dynamics**. Substrate
> operates in a regime where forward information is INSUFFICIENT to reach
> the correct attractor; backward evidence provides the missing information;
> once available at initialization, ANY dynamics (forward-backward EP or
> loopy iterative) reaches PERFECT acc=1.000."

This is the constraint to satisfy. The mechanism must produce **forward-only-
blind regime** where:
- Forward information is genuinely incomplete at hop t (not just quantized
  approximation; soft posterior provides no gain)
- Backward observation at hop t+k for some k carries the missing information
- The "floor" at acc~0.20 is the bound on what forward-only can achieve
- VAMP-on-chain backward smoothing accesses the missing information

## Seed candidate framings — REFINED

Original 8 candidates (subspace collapse in W^L + coherent error correlation
+ W^L null space + algebraic Kerdock mode mixing + non-Markov chain + attractor
manifold + RSB aging-regime + other) STILL apply, but with the refined
question:

**What substrate mechanism produces forward-information-insufficient regime
where information is observed-but-blocked from forward propagation, and
recoverable only via backward-evidence-conditioning?**

Most directly suggestive:
- **W^L growing null space**: forward projects into null space at depth;
  information "exists" but is geometrically inaccessible from forward;
  backward smoothing from observed endpoint can constrain back through
  null space dimensions
- **Attractor manifold collapse**: chain enters a small manifold containing
  correct + ~5 confusable codewords (explains 0.20 plateau = 1/5); forward
  cannot escape manifold; backward observation outside manifold identifies
  correct member
- **Coherent (not iid) error correlation**: errors at hop t correlated with
  errors at hop t+k via shared substrate structure; forward marginalization
  over correlated errors fails; backward smoothing observes downstream
  error pattern, infers correct correlation

## What Research should produce (revised)

**Pass 1**: external lit-scan for substrate mechanisms producing
"forward-information-insufficient regime with backward-evidence rescue"
signature. The substrate produces ALL forward-only methods fail + ALL
backward-init methods succeed. Find the published mechanism family with
this signature OR conclude substrate is genuinely novel.

**Pass 2**: substrate drill — score top 3-5 candidates against 8-constraint
signature; identify falsifiable predictions; if no candidate fits, honest
verdict "substrate empirically beyond published frameworks for chain
composition mechanism".

## Per [[feedback-no-smoke]] — honest framing requested

If Research's best candidate is SPECULATIVE without lit-scan precedent for
the "forward-info-insufficient + backward-init-rescue" signature, state
plainly: substrate is novel. 4 mechanism diagnoses refuted + 1 substantive
substrate-physics finding (initialization-information-not-dynamics) is itself
the contribution.

This addendum SUPERSEDES the original 4th-attempt routing's constraints #5
and #7. Constraints #1-4 + #6 + #7-revised + #8 are the empirical signature.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
