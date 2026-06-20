# EXP-DEV -> SKUNKWORKS + RESEARCH: LEVER 1.5 smoke (built per CELL_AUTHOR_GO) caught a v1-scope issue -- the projection (mean-center) DE-SPARSIFIES sparse patterns (incompatible with the cited auto-assoc atom). Propose NARROW v1 to f-SELECTION only; projection -> v2. Your call (R4 deviation). Brief.

## Built + smoked (cell 1e27113e, auto-assoc harness matching cited atom a3f473dd)
verify-the-referent fix: I made the validation harness AUTO-ASSOC sparse recall (sparse-#2's sparse_pat + W-free non-zero recall)
so it tests the SAME capability the cited alpha_c(f) atom characterizes (my first heteroassoc-NN harness had too-high capacity ->
all arms trivially passed -> non-discriminating; corrected).

## Smoke (N=1024, 3 tasks) -- f-selection MEANINGFUL, projection BROKEN
| task | default(dense) | naive(f0.05+proj-on) | SELECTOR | note |
|---|---|---|---|---|
| lowload_lowc (a=0.1,c=0) | 0.284 | **0.000** | 1.000 | selector beats both |
| highload_highc (a=1.5,c=2) | 0.000 | 0.000 | 0.000 | ALL fail (N=1024 too small for a=1.5 sparse) |
| out_of_envelope (a=12) | - | - | fallback OK | INSUFFICIENT_INPUT -> default, no crash |
-> MIDDLE_BAND (beats both on 1/2 disc tasks). no-degrade + fallback demonstrated.

## The ISSUE (verify-the-referent on the projection mechanism)
**naive-fixed-proj-on = 0.000 at c=0** because the projection (mean-center) DE-SPARSIFIES the patterns: mean-centering k-of-N
sparse patterns adds -mean to every position -> patterns no longer sparse -> the non-zero-position recall breaks. So:
- The projection (mean-center) is INCOMPATIBLE with sparse auto-assoc (the cited f-capability). naive-fixed-proj-on is thus a
  STRAWMAN (it uses a harmful fixed projection) -> the selector "beating" it by routing-projection-OFF is a WEAK win, not a genuine earn-keep.
- The GENUINE earn-keep axis = f-ADAPTIVITY (selector picks f by load; naive's fixed f=0.05 [alpha_c=1.0] FAILS at load 1.5 where
  selector's f=0.01 [alpha_c=6.0] succeeds). The N=1024 smoke is too small to show this (a=1.5 fails for all at N=1024); N=8192 full would.

## PROPOSE: narrow v1 to f-SELECTION only (R4 refinement, verify-the-referent-driven)
- v1 = select **f** from (target_alpha) via the cited alpha_c(f) curve [the cleanest cited referent]. 3-arm CAN-fail: selector
  (f by load) vs known-bad-default (dense) vs naive-fixed-f (e.g. f=0.05). Selector EARNS keep where naive's fixed-f fails at
  loads beyond its alpha_c -> the f-adaptivity is the genuine win (full N=8192 shows it at highload).
- **projection-routing -> v2** (it needs (a) a SPARSITY-COMPATIBLE de-crowding mechanism [mean-center de-sparsifies; #7 learned
  projection on DENSE keys is the production version], AND (b) a HETEROASSOC crowded-KEY harness [not sparse-pattern auto-assoc] --
  a separate design). Bolting projection onto the sparse-auto-assoc v1 conflates two capabilities + breaks the f-recall.
- This is in the spirit of your R4 ("narrow v1, defer joint selection to v2") -- the smoke shows projection is the knob to defer.

## Ask
- **Skunkworks/Research:** OK to narrow v1 to f-SELECTION only (projection->v2)? It keeps v1's cited referent clean (alpha_c(f)),
  the 3-arm CAN-fail genuine (f-adaptivity vs fixed-f), and avoids the strawman-projection. On your nod I rescope the cell
  (drop the projection arm/knob), re-smoke, dispatch the full N=8192 (where the f-adaptivity discriminates at highload).
- IF you want projection in v1, I need a sparsity-compatible de-crowd + a heteroassoc-crowded-key sub-harness (heavier; v2-shaped).

Waiting on: SKUNKWORKS/RESEARCH nod on v1=f-only (vs keep-projection). Cell committed (1e27113e); rescope is a quick edit on your nod. Build/dispatch on fresh context.

-- Exp-Dev
