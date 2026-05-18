# Pre-registration: Track 0.1c — eligibility traces for temporal credit assignment

**Date pre-registered:** 2026-05-17 (before running)
**Experiment file:** `experiments/exp_eligibility_charlm.py` (not yet written)
**Decision gate this feeds:** Track 0.1 follow-up; informs whether biologically-grounded eligibility traces fix temporal credit assignment in the delta-rule update.

## Question

Track 0.1's three-factor delta rule has a fundamental limitation we share with most simple Hebbian schemes: **the modulator signal at step t only consolidates the connection that was active at step t.** If the model produces a wrong prediction at step t whose true cause was an error in encoding at step t-5, the rule cannot reach back to fix the earlier connection. This is the classical temporal credit assignment problem.

Biology solves this with **synaptic tag-and-capture** (Frey & Morris 1997, *Nature*; Redondo & Morris 2011, *Nat. Rev. Neurosci.*): recent (pre, post) co-activity sets a short-lived molecular tag at the synapse (CaMKII, transient PKA, actin remodeling), and modulator signals that arrive within a ~0.3–2 second window consolidate the tagged synapses. Computationally this is the eligibility trace (Sutton & Barto 1981; Florian 2007 *Neural Comp.*; Bellec et al. 2020 *Nat. Commun.* (e-prop)). Schlag-Irie-Schmidhuber 2021 do *not* use eligibility traces — their delta-rule update is single-step. This is a real differentiator we can add cleanly.

Hypothesis: adding per-connection eligibility traces with a decay time-constant of a few tokens will allow the modulator (surprise / reward) at step t to consolidate connections active in steps [t−τ, t], improving prediction on sequences with multi-step dependencies.

## Architecture under test

Same Track 0.1 setup (FHRR substrate, K=4 bundle, three-factor delta rule), plus:

- **Per-connection eligibility trace E** (shape N×N, complex): updated each step as
  `E ← γ·E + outer(target − expected, context.conj()) / N`
  This is the *short-term* memory of recent pre×post co-activity. Decay rate γ ∈ {0.5, 0.7, 0.9, 0.95}.
- **Weight update** now consumes the trace:
  `W ← W + arousal · E`
  rather than the single-step outer product directly. The trace accumulates across recent steps; the modulator (arousal, here flat for this probe) determines how much of the trace gets written.
- **Modulator scheduling:** for this probe, arousal stays constant. The biological story would have arousal depend on surprise (consolidate more when wrong), but that interaction is a separate variable; isolating the trace effect is the point of this experiment.

## Variations to test

- Trace decay γ ∈ {0.5, 0.7, 0.9, 0.95}. γ=0 reduces to Track 0.1 exactly.
- Best K, beta from Track 0.1 (frozen at winning values).
- Arousal swept ∈ {0.1, 0.3} (lower than Track 0.1 because the trace is now accumulating multi-step contributions).

8 configs × 1 seed. Each run ≈ 4 minutes.

## Pre-registered decision criteria

| Outcome (best test bpc on full corpus) | Verdict |
|---|---|
| Eligibility-trace best beats single-step delta-rule best by > 0.3 bits/char | **Traces help.** Add to default architecture for Bet B. This is biologically grounded; it should help. |
| Within 0.3 bits/char | **Marginal at this scale.** The corpus may not have strong multi-step dependencies. Re-test on a corpus with known long-distance structure (English with multi-sentence consistency requirements). |
| Eligibility-trace best is *worse* | **Surprising.** Either γ is in the wrong range, or trace accumulation introduces noise that outweighs the credit-assignment benefit at this short corpus. Investigate before discarding. |

## Why this matters for the strategic picture

Eligibility traces are the cleanest single addition that turns our architecture from "shallow associative memory" into "temporal credit-assignment learner." Without them, we cannot scale to corpora with multi-token dependencies — and any natural language has multi-token dependencies. With them, we share the credit-assignment story with the most biologically-grounded scalable three-factor framework in the literature (Bellec et al. e-prop).

This experiment is also a low-cost way to test whether our modulator framework has *room to grow*: adding a trace adds one new state per connection. If this small addition produces a measurable lift, we have evidence the modulator-rich design is buying us something. If it doesn't, we know the modulator architecture is over-parameterized for this scale.

## What this is NOT testing

- Whether traces should be sparse rather than dense (every connection vs only recently active ones).
- Whether γ should be learned rather than fixed. Schlag-style learning of γ via a tiny slow network is interesting but adds gradient descent back into the loop, which violates our "local-only" framing.
- Whether traces interact constructively with pointer-chain memory (Track 0.1b). That's a 0.1d combination experiment if both come out alive.
- Whether traces help on long-range dependencies specifically. The 38KB markdown corpus has limited long-range structure; this probe tests if traces help at all, not whether they shine on the hard cases.

## Combined-experiment note

If Track 0.1b (pointer-chain) and Track 0.1c (eligibility traces) both come out alive, the natural follow-up is **Track 0.1d**: both together. Pre-registering 0.1d here in skeletal form so we don't lose it: same as 0.1c but with the pointer-chain mechanism from 0.1b active, and the trace also applied to retrieval-driven updates. This is the configuration most architecturally similar to a biological hippocampus + cortical memory loop.
