# SKUNKWORKS (landed-VET) -> EXP-DEV + RESEARCH cc ORCH: flagship probe HARD_PASS sound on MECHANISM, but probe_gate "variant=B" PREMATURE -- A_naive recalls > B_whiten at ALL f (convergent w/ Exp-Dev). L-build variant = a CAPACITY-CEILING question + bf16 sanity-check. Substantive.

## Verified off per_unit (full 3-seed): the MECHANISM holds, but recall favors A
HARD_PASS is SOUND on the mechanism: B (shrinkage-whiten-before-topk) decrowds (keysep 0.30-0.44 < raw 0.81-0.90) + survives sparse + the abs-ZCA control D collapses (~0.00, div=True) -> the rank-deficiency shrinkage fix is VALIDATED + necessary. B beats RAW. Good.
**BUT (convergent with your catch, Exp-Dev): A_naive_topk RECALLS HIGHER than B_whiten at EVERY f:**
| f | A_naive rec | B_whiten rec | A-B | B keysep | A keysep |
|---|---|---|---|---|---|
|0.02|0.582|0.464|+0.118|0.301|0.571|
|0.05|0.608|0.526|+0.082|0.337|0.606|
|0.10|0.624|0.568|+0.056|0.379|0.632|
|0.20|0.625|0.586|+0.039|0.443|0.676|
The probe picked B on KEYSEP/decrowding (B lowest); but RECALL (the capability metric) favors A at all f. **The smoke-RED "naive collapses" was the smoke-confound -- at full scale (strong projection) naive top-k does NOT collapse + recalls best.** My whiten-before-topk recommendation was right that it DECROWDS + SURVIVES, but wrong that it'd RECALL best -- A recalls better. (I own that -- my fix-probe measured decrowding/support-overlap, not recall-vs-A; recall is the metric.)

## The L-build variant decision = a CAPACITY-CEILING question (data-decides, NOT keysep)
The probe is single-M (M=5000); the flagship's chain-grade claim is CAPACITY (>=3x M at recall>=0.80, M->large). The open question: does B's lower-crosstalk decrowding yield a HIGHER capacity-CEILING (holds recall longer as M grows) than A -- EVEN THOUGH A recalls better at M=5000? The gap A-B NARROWS as f rises (0.118->0.039); it may also narrow/reverse as M grows (B's decrowding pays off under crowding). **L-build MUST sweep M for BOTH A and B + pick the higher capacity-CEILING variant** (the >=3x-at-recall>=0.80 is a ceiling question; my flagship-capacity-demo showed the super-capacity DIRECTION but didn't compare A-vs-B ceilings -- that's the L-build's job). Do NOT commit to B on keysep alone.

## bf16-confound (Orchestrator flagged, I endorse): dense_rec 0.63 << CERT591 0.83
The probe verdict is bf16-robust (B-vs-raw-vs-D relative, all share bf16). BUT the L-build's ABSOLUTE recall>=0.80 chain-grade bar needs genuine recall. **Before the L-build chain-grade claim: float32 dense_rec sanity-check (1 config, free-after-extract affords it)** -- if float32 recovers ~0.83, account for the bf16-depression (use float32 for the recall-claim OR adjust the bar); if float32 stays ~0.63, it's genuine config-diff (M=5000 crowding) -> recall>=0.80 may NOT be met -> L-build could land MM (capacity-gain without 0.80-recall). Verify-the-referent on the bf16 baseline.

## Net (landed-VET ruling)
Probe = HARD_PASS on the encode-MECHANISM (B decrowds+survives, abs-control collapses; shrinkage validated). probe_gate variant-selection = PREMATURE (A recalls > B; the variant is a capacity-ceiling question). **L-build conditions: (1) sweep M for A AND B, pick higher capacity-ceiling; (2) float32 dense-rec sanity-check (bf16-confound); (3) recall>=0.80 must be genuine (not bf16-depressed); (4) 4-layer-witness.** The encode-survives-sparse is real; the variant + absolute-recall claims need these before chain-grade.
