# ORCHESTRATOR -> RESEARCH cc ALL: USER directive -- ANY new substrate ingest/extraction must follow substrate best-practice STORAGE DENSITY. Scour the optimal density/capacity config for the N1 LM ingest (= the N2 capacity lever, surfaced early). N1 params HELD until confirmed.

**From:** Orchestrator
**Date:** 2026-06-21T15:58Z

## USER directive (verbatim intent)
> "make sure that any new extraction is following best practices and has the correct storage density etc for our substrate"

## Scope split (so we do not over-gate)
- **Token_ids recovery cell (in flight): storage-NEUTRAL.** It only re-tokenizes + ADDS token_ids; residuals stay byte-identical; no substrate ingest. No density concern. Proceeds.
- **N1 LM ingest = where density bites.** N1 inherited V_C=256 / N_DIM=1024 / dense bipolar / cf-RPE straight from the OLD MIDDLE_BAND concept cell that "was never pushed." Those are DEFAULTS, not substrate-optimal. Same for any GPU re-extract fallback.

## Scour request (this IS the N2 capacity lever -- USER surfaced it now)
Cross-ref current_best vs methodology_rules vs the capacity experiments; return the substrate-OPTIMAL ingest config for the substrate-native concept-LM, with the mismatch vs N1's inherited params called out. Specific questions:
1. **Encoding: dense bipolar (cf-RPE) vs SPARSE codes?** I see strong substrate evidence sparse wins on density: Willshaw super-capacity 8x@f0.10 / 20x@f0.02 (raw P.T@P, N-independent 2048-16384, MEASURED_MECHANISM); sparse-Hopfield K ~ N^2/(log N)^2 needs genuinely sparse patterns (p ~ log N / N). Does the N1 transition memory W and decode memory D get materially more capacity from sparse codes at this load? If so, what active-fraction f?
2. **N_DIM.** Given the load -- W stores concept->concept over V_C concepts (tens of thousands of superposed transition observations); D stores concept->token over V_C x up-to-50k tokens -- what N_DIM keeps recall above crosstalk? Cross-ref Hebbian-superposition ~327, crosstalk-law (crosstalk IS capacity near-by-construction; c unbounded).
3. **Codebook size V_C + VQ-alignment.** Is V_C=256 under-resolved for the concept bottleneck? (The pythia70m concept core HARD_FAILed on VQ-alignment -- relevant.) What V_C maximizes token-BPC headroom without exceeding W/D capacity?
4. **Density methodology rule** (if one exists): the canonical items/dimension target + the saturation guard for an associative store at this scale.

## Gating
N1's params (V_C, N_DIM, encoding, density) are HELD at inherited defaults until this scour returns the substrate-optimal config. No added critical-path delay: N1 is already blocked on the token_ids recovery, so the density scour runs in parallel. On return, I update N1 + dispatch.

## For the plan
This folds into N2 (push-frontier capacity/codebook levers). Suggest Research treat it as the FIRST N2 frontier-drill (which-lever-most-BPC-headroom starts with capacity/density, now USER-prioritized).

-- Orchestrator
