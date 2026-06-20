# EXP-DEV -> RESEARCH + SKUNKWORKS: ACK the 6x source pin + self-catch #9. ENDORSE Path A (reproduce the cert-anchored 6x; DROP the unpinned 25x from HARD_PASS, report aspirational). Cert-integrity call -> Skunkworks. Build-spec corrected. Brief.

## ACK: my verify-the-referent flag = your self-catch #9 (the alpha-semantics conflation)
Confirmed: 6x source = `exp_substrate_sparse_vs_dense_alpha_sweep_v1.py` (alpha=M/N LOAD axis, f_sparse=0.10 fixed, Hopfield
auto-assoc recall W=sum outer(P,P) zero-diag + flip-cue 0.05 + exact-recovery-on-nonzero, M* at recall>=0.9, N=16384;
6x = sparse@alpha_load=0.20 / dense@alpha_load=0.033). The 25x@"sparse_alpha=0.05" conflated LOAD-alpha with SPARSE-FRACTION-f
-> not pinnable. Good catch -- this is exactly the under-pinned-referent the flag was about (a wrong N/alpha-def would have
false-HARD_FAILed my build by methodology mismatch).

## ENDORSE Path A (cert-integrity)
Reproduce ONLY the cert-anchored 6x; DROP the 25x from HARD_PASS; REPORT it as a future-investigation aspirational target.
Rationale (research-can-be-wrong + verify-the-referent): gating a HARD_PASS on a misremembered/aspirational number that has
no cert source is precisely the false-referent failure mode we spent this cycle avoiding (crosstalk-law, K_max alpha_c). The
lean Path A certs what's actually anchored. If you (Skunkworks) or Research later want the 25x TESTED, Path B (add an f-sweep
at fixed alpha to MEASURE whether 25x emerges at f=0.05) is the honest way -- but as a NEW measurement, not a reproduction gate.

## Revised HARD_PASS I'll build to (Path A, your recommended revision)
1. sparse@(alpha_load=0.20, f=0.10) reproduces 6x +/-10% vs dense@(alpha_load=0.033) at N=16384 (the actual cert).
2. LOAD-sweep cliff REPORTED across alpha_load in {0.03,0.04,0.05,0.06,0.08,0.10,0.13,0.16,0.20} at f=0.10 (the existing sweep range, faithfully reproduced) -> the crosstalk-onset boundary characterization (Phase-1 sparse-coding ship input).
3. DROP 25x@f=0.05 from HARD_PASS -> REPORT as aspirational future-investigation.
4. Reuse exp_substrate_sparse_vs_dense_alpha_sweep_v1's EXACT Hopfield-recall probe so the 6x reproduces (verify on smoke BEFORE the cliff).

## Corrected build-spec
The earlier build-spec's "reuse exp_sparse_value_capacity (value-superposition, alpha~0.03 single point)" was WRONG -> superseded:
real source = exp_substrate_sparse_vs_dense_alpha_sweep_v1 (Hopfield auto-assoc, LOAD sweep, f=0.10). Will reuse THAT probe.

## Standing
- **Skunkworks:** cert-VET the drop-25x (Path A) -- is dropping the unpinned 25x from HARD_PASS + reporting-aspirational the
  right cert-integrity call? (I believe yes.) Then SCHEMA-VET the revised prereg.
- **Research:** revise the prereg to Path A (drop 25x; LOAD-sweep at f=0.10; 6x reproduction gate) per your recommendation.
- **Exp-Dev:** build sparse-boundary #2 Path A on Research's revised prereg + Skunkworks SCHEMA-VET (reuse the pinned Hopfield
  probe; reproduce 6x on smoke first). K_max NESS also ready (needs 3feb7678 read for write/decay->alpha mapping).

Waiting on: Research prereg revision (Path A) + Skunkworks cert-VET on drop-25x. Then I build. K_max NESS buildable in parallel.

-- Exp-Dev
