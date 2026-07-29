# Pre-reg: stateful-core MES fit probe v1 (training-stability diagnostic)

Cell: `experiments/exp_stateful_core_mes_fit_probe_v1.py`
Date: 2026-07-29
Author: exp_dev

## Question (measurement-first, NOT a mechanism/generalization claim)
Under what training configuration does the gap-B stateful-core mechanism (per-slot PBWM gating +
role-query addressing, hdlab/slot_attention_wm.py) RELIABLY FIT a 256-item MES Arm-A train set
(train_loss < 0.15) on BOTH seeds 7 & 13? Plus: does per-slot-only (ee714c31) fit where gap-B does
not (isolate the culprit)?

## Established context (cited, not re-derived)
- MES data-sufficient gate returned OPTIMIZATION_UNSTABLE @256: gap-B MES-A train_loss seed7=0.6989,
  seed13=0.6863 (~ln2=chance, fit=False).
- OLD mean-pool path DID fit @256 (diag_stateful_core_gen_curve_v1 train_loss=0.127).
- => the richer mechanism made the loss surface harder to optimize; training reliability is THE
  blocker before any mechanism/GPU-full decision.

## Design (one thing at a time; mechanism math UNCHANGED)
- Arm A, MES (distE4/distEv6, LOCKED_CONSTRUCTION), 256 balanced items, fixed data rng (20260729).
- Fit = train_loss (final = mean of last 10 steps). Eval NOT scored (this is a fit probe).
- Levers swept (init/temp-anneal set EXTERNALLY on the WM instance, NOT edits to the module):
  LR {1e-4, 3e-4, 1e-3}; linear warmup {0, 0.15, 0.2} + cosine decay; steps {320, 640};
  role_query init std {default 0.02, gentle 0.005}; addr_temp anneal {fixed 0.5, soft->sharp 1.0->0.5}.
- ISOLATION: per-slot-only uses the module's OWN byte-identical ee714c31 fallback
  (wm.step(tok_reps=None) == pooled-clause key, per-slot PBWM); gap-B = wm.step(tok_reps=...). No
  git-checkout of the old file needed.
- Instrumentation: per-step loss + grad-norm PRE-clip AND POST-clip; shape classifier
  (STUCK_FLAT / OSCILLATING / SLOW_DESCENDING / FIT), raw stats logged for auditability.

## Config grid (Arm A, MES, 256, seeds [7,13])
C0 gate-baseline gapb (lr3e-4, no warmup, 320)   -- reproduce UNSTABLE + read shape
C1 lowLR gapb (1e-4, no warmup, 640)             -- oscillation => lower LR + more steps
C2 highLR gapb (1e-3, no warmup, 320)            -- slow => higher LR
C3 warmup+cosine gapb (3e-4, wu0.15, 640)        -- joint-unfrozen warmup
C4 warmup+highLR+cosine gapb (1e-3, wu0.15, 640) -- warmup lets higher peak LR be safe
C5 warmup+cosine+tempanneal gapb (3e-4, wu0.2, 640, temp 1.0->0.5)
C6 gentleinit+tempanneal gapb (3e-4, wu0.2, 640, temp 1.0->0.5, rq_std 0.005)
C7 per-slot gate-baseline (3e-4, no warmup, 320, gap_b=False)  -- ISOLATION
C8 per-slot warmup+cosine (3e-4, wu0.15, 640, gap_b=False)     -- ISOLATION better recipe

## PASS / FAIL bands (envelope)
- PASS  = at least one config reaches train_loss < 0.15 on BOTH seeds. Report the leanest such
  config (fewest steps, prefer gap_b=True = mechanism under test). verdict_tag=FIT_CONFIG_FOUND.
- FAIL  = no config fits both seeds. Report per-config final loss + failure SHAPE as evidence.
  verdict_tag=NO_FIT_CONFIG_FOUND. (An honest "no config found + evidence" is a valid deliverable.)
- Isolation verdict: ROLE_QUERY_IS_CULPRIT (per-slot fits, no gap-B fits) / GAP_B_FITS /
  GENERAL_INSTABILITY (neither fits) / MIXED.

## Compute architecture
Sequential-CPU-per-config on the ENCODER RECURRENCE (each item is an ~11-clause recurrence with a
step-N-depends-on-step-N-1 WM update -> genuine sequential dependency inside a batch), but batched
across the 8 items per step and run on --device cuda. This is the SAME forward path as the gate /
FULL; no new batching opportunity vs that path. Remote GPU (RTX 4060 Ti). Est wall ~1h detached
(HYPOTHESIZED@ ~0.3s/step x ~9600 steps + ~18 ckpt reloads).

## Discriminator-fires
The C0 gate-baseline arm is expected to REPRODUCE the unstable ~ln2 result (that IS the phenomenon
under study); the discriminator here is train_loss<0.15, an explicit numeric gate, not a saturated
accuracy metric. Shape classifier + grad-norm curves make the failure mode observable.

## Downstream (NOT in this probe)
Do NOT run the full generalization gate here (next step once fit is reliable). Do NOT dispatch GPU
FULL. Once a fitting config is found, the gate/FULL train configs adopt it.
