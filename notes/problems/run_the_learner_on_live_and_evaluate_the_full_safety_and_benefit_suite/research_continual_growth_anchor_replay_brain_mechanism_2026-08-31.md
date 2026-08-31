# Research drill: how does the brain keep word-meaning stable while it keeps reading? (2026-08-31)

Literature drill (routed to hdi_research) for the live-canary problem. The question that decides the
mechanism: my continual growth loop must not DRIFT as it keeps reading. Is "replay a FIXED original anchor at
constant weight every round" the brain's actual anti-drift mechanism, or something else?

## The five findings (citations verified by the drill)

1. **Interleaved replay is NOT constant-rate per item.** CLS (McClelland, McNaughton & O'Reilly 1995) requires
   interleaving old with new, but never a constant *per-item* rate. Replay is a **biased sampler** (Kumaran,
   Hassabis & McClelland 2016, TiCS): reactivation is weighted by recency/reward/novelty, and replay of a
   given trace **declines as it consolidates** — its protection migrates from replay to intrinsic synaptic
   stability. So a literally frozen-copy-replayed-forever anchor is *not* the mechanism.

2. **Replay is prioritized toward at-risk items.** Mattar & Daw 2018 (Nat Neurosci): reactivate by
   gain x need. Schapiro et al. 2018 (Nat Commun): human rest-replay preferentially reactivates the
   **weakly-learned** items. The faithful "which to replay" rule is *protect the most-at-risk/most-drifting*,
   not a uniform sweep.

3. **The anchor is a consolidated GIST, not a verbatim original — and for word MEANING it keeps changing.**
   Trace-transformation (Winocur & Moscovitch 2011): cortical traces become schematic/semantic, not copies.
   For semantic memory specifically, lexico-semantic representations are **continuously, slowly updated across
   the lifespan** — early word meanings are gradually *replaced* by later usage (diachronic semantic-update
   work 2024/25). **A hard FREEZE is therefore the LEAST faithful anchor for meaning.**

4. **The load-bearing lifelong anti-drift mechanism is SYNAPTIC consolidation**, per-parameter stability that
   grows with confirmation: Grossberg stability-plasticity dilemma (match-based gating); Fusi, Drew & Abbott
   2005 cascade model; its ANN form EWC (Kirkpatrick 2017); the slow-store/mean-teacher EMA (Tarvainen &
   Valpola 2017; Kumaran 2016 slow store). "Keep a fixed anchor + fuse" reproduces the anti-forgetting EFFECT
   via an external slow store, but it is a **computational-level SUBSTITUTE for synaptic consolidation**, not
   the mechanism itself.

## Verdict (acted on)

- **Frozen-original anchor = NEEDS-MODIFICATION, not wrong.** It will cut drift (a sound engineering fix) but
  it is only PARTIAL fidelity: it freezes a trace the brain keeps slowly fluid.
- **The single most brain-faithful variant = a slowly-consolidated EMA anchor:** `anchor <- (1-eta)*anchor +
  eta*grown` at small eta (Procrustes-aligned so the EMA lives in one coordinate frame). High inertia resists
  round-to-round drift; non-zero plasticity still absorbs genuine meaning change.
- **Second-order refinement (named as a follow-on, not built here):** prioritized/at-risk-weighted replay and
  per-dimension stability that grows with confirmation (Fusi cascade / EWC / Mattar-Daw gain x need).

## How this changed the build

The anti-drift lever is recast as ONE parameter: the slow anchor store's **consolidation rate eta**. The
read-out each round = keep-both ensemble(SLOW anchor, FAST grown) via `hdlab.cls_growth` (verbatim). The three
arms differ in exactly one variable:
- **FROZEN** (eta=0): the engineering fix; PARTIAL fidelity.
- **EMA_ANCHOR** (eta small): the brain-faithful primary arm.
- **DECAY_ANCHOR** (eta=0.5): the anti-brain can-fail control; MUST drift.

Falsifiable prediction (the drill's): EMA holds drift as low as FROZEN **while absorbing legitimate new meaning
FROZEN rejects** -> EMA is a strictly-better stability/plasticity operating point. Tested by sweeping eta and
mapping the corruption-vs-gain frontier.

## Sources
McClelland/McNaughton/O'Reilly 1995; Kumaran/Hassabis/McClelland 2016 (TiCS 20:512); Mattar & Daw 2018 (Nat
Neurosci 21:1609); Schapiro et al. 2018 (Nat Commun 9:3920); Winocur & Moscovitch 2011 (JINS); Fusi/Drew/Abbott
2005 (Neuron 45:599); Grossberg 1980 (ART); Kirkpatrick et al. 2017 (PNAS 114:3521); Tarvainen & Valpola 2017
(mean teacher). Full drill transcript in the solver session log.
