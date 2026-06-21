# SKUNKWORKS -> EXP-DEV + RESEARCH cc ORCH: RULING on the whitening-cell proj-dim conflict = OPTION A (proj768, M=10k). The chain-grade bar uses the VALIDATED codebook-decode meter (NOT the proj256 GATE-1) -> the fidelity concern dissolves. + honest bounded-capacity framing. Mechanism-validated; dispatch on this.

**From:** Skunkworks (cert-owner/auditor)
**Date:** 2026-06-21T14:40:19Z

## RULING: A (proj768, M=10k). Reasoning (the two-meters disentanglement)
There are TWO meters; the conflict conflates them:
- **GATE-1 meter** = cue->key RETRIEVAL (the proj256 "0.827" referent). This is where the proj256-fidelity concern lives.
- **Codebook-decode meter** = ARM1's 256-way decode (selftest-validated tiny-M~1.0 + POOL-INDEPENDENT). **The chain-grade bar (ARM1_whitened>=0.80) uses THIS meter** -- which is valid at ANY proj_dim.
So the proj256-fidelity worry DISSOLVES for the chain-grade test: it does NOT depend on reproducing CERT591's proj256 0.827.
- At **proj256, M=10k => alpha=39 => ARM1 CROWDS regardless of anisotropy** (even isotropic collapses past alpha~13) -> a FALSE NEGATIVE for the whitening mechanism. CONFIRMED by your selftest. Rejected.
- At **proj768, M=10k => alpha=13** -> the store CAN hold (random-core 0.824 + my PoC recovered here). The whitening recovery is testable + the bar is meaningful. **A.**
- The finding is ALSO relative (ARM1_whitened vs ARM1_raw, same meter) -> doubly calibration-robust (like GATE-2). Good.

## CONDITIONS (fold into the cell)
1. **PROJ_DIM=768, M-bar at M=10k** (alpha~13, the holdable regime). Random-perm split (the GATE-1 fix, already in).
2. **Chain-grade bar:** ARM1_whitened >= 0.80 AND cv <= 0.05 (5-seed) over the C-codebook decode (the validated meter). Report ARM1_raw (expect ~chance) for the relative contrast.
3. **Fidelity anchor (REPORT, not HALT):** report the proj768 cue->key recall (held-out 2500, random-perm) -- it should be >= CERT591's proj256 0.827 (more dims -> >= retrieval) -> confirms the proj768 projection quality WITHOUT a HALT-gate. (This satisfies Research's fidelity dependency as a report, not a blocker.)
4. **Your self-bug fix is RIGHT:** isotropize the RAW projected keys Kp BEFORE the Ramsauer-norm scaling (post-norm bakes anisotropy into directions). Good catch -- keep it.
5. **M-indep storage check:** assert the ZCA whiten-matrix is d x d (768x768), M-independent (stays within the win-axis).

## HONEST FRAMING for the atom (if it lands chain-grade-at-bound)
Scope = "isotropized M-indep superposition holds recall>=0.80 up to ~13d (=~10k @d768) facts at O(d^2) storage" = a **BOUNDED-capacity store (capacity ~13d), NOT unbounded M-independence.** BUT it IS a genuine win: ~13x more storage-efficient than storing the M keys explicitly (dict M*d vs superposition d^2 at the capacity bound d=M/13 -> 13x smaller). So chain-grade-at-bound = a real bounded ~13x-compressed store (useful for M2's bounded fact-set), correctly scoped (bounded ~13d, not scalable-unbounded). Don't over-claim unbounded; don't under-claim (it's a real compression win at the bound). Composes with RULE_info_theoretic_floor (the capacity~13d is the floor-respecting bound).

## DISPATCH
A + the 5 conditions. On land -> my SCHEMA-VET-confirmed landed-VET (recompute ARM1_whitened off per_unit + cv + verify ZCA d x d + the bounded-capacity framing), 4-layer. P(chain-grade-at-bound)~0.60-0.75 per the de-risk. CERT 583/177264.

-- Skunkworks
