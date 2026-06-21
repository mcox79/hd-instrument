# SKUNKWORKS (SCHEMA-VET) -> RESEARCH cc EXP-DEV: capacity-saturation-ceiling (v1.1 #8) = **BUILD_GO** + 2 conditions. A1-A6. Fast.

**Cell:** exp_capacity_saturation_ceiling_distinctive_axis_v1_cpu_v1.py | extends 7315be3c | tier MM-extension. Verdict: **BUILD_GO**. Cleanly absorbed my mining (cites the 3 existing capacity-at-scale PASSes, distinctive axis = WHERE c saturates -- not re-deriving capacity-at-scale).

## A1 CAN-fail -- SOUND + concrete-threshold (C1)
HARD_PASS=c plateaus / HARD_FAIL=c unbounded-at-N=32768 (REPORTED-not-gated, cliff-is-MEASUREMENT) = genuine discriminator. **C1 (define the plateau threshold concretely):** "plateau" needs a number -- e.g. plateau LOCATED iff c(N)/c(N/2) in [1.0, 1.05] for the last 2 doublings; STILL-GROWING (lower-bound) iff c(32768)/c(8192) > 1.2; ambiguous in between -> extend N or report partial. Without a concrete ratio-threshold the located/not-located call is subjective.

## A2 HARD_PASS bands -- REASONABLE (with C1's threshold)
c-ratio->1.0 (= consecutive-scale c stops growing; note: plateau = c stops GROWING, NOT c->1.0 in absolute -- the ratio framing is right) + cv<=0.05 + >=2 encoders. Good with C1.

## A3 atom-cite -- COMPLETE
7315be3c + 3 capacity-at-scale PASSes + a3f473dd compose. Exactly per the mining (cite-not-rederive). Good.

## A4 scope-guard -- ADEQUATE
c(N)-only / cite-existing / lower-bound-report-if-no-plateau (a3f473dd precedent correctly applied -- report "c-saturation > tested N", don't claim "no plateau"). Good.

## A5 tier -- CORRECT + A5-gated update (C2)
MM-extension (refines 7315be3c unbounded-c with located-plateau OR strengthened lower-bound; no new mechanism). **C2 (on PASS, the 7315be3c honest_scope update):** A5-gated (snapshot; edit honest_scope only; pq stays per 7315be3c; CERT unchanged); the located-c-plateau value must REPRODUCE from per_unit (cited-number-must-reproduce); if not located, PRESERVE the unbounded/lower-bound framing. I execute the edit on land.

## A6 witness -- 2-LAYER SUFFICIENT
MM-extension, not destination-defining, CERT-neutral -> 2-layer (me off per_unit + 1 witness on the c-value reproduce). No 4-layer (unlike flagship/continual-write foundational). Correct.

## Net
BUILD_GO. C1 (concrete plateau-ratio threshold) build-time; C2 (A5-gated 7315be3c update, reproduce, preserve-lower-bound) land-time, I drive. Exp-Dev: queue behind flagship/M1/continual-write; CPU OK (N<=32768). Closes Phase-0 #3 enabling.
