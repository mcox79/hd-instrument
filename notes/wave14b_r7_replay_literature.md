# R7 negative finding — literature-grounded synthesis

Unbiased research agent, 2026-05-19, after R7 found concept-tagged replay
loses to random replay by 0.53 bpc on BWT-on-A.

## TL;DR

The result is **strongly aligned with the empirical CL literature** and the
**opposite** of what naive CLS theory suggests. Priority signals win only
when (a) tied to current model state (interference, gradient direction,
TD-error), not static structural tags; (b) the buffer is large enough that
coverage isn't the binding constraint. A "concept-activates-yes/no" filter
is a static tag that drops 87.6% of coverage. Textbook recipe for losing
to uniform.

## What the canonical literature says

The classic prioritization papers (Schaul 2015 PER, Mattar-Daw 2018,
Andrychowicz 2017 HER, Aljundi 2019 GSS/MIR, Riemer 2019 MER) all converge
on: **the priority signal that wins is always closed-loop, tied to the
current model state**, never a static descriptor of the sample.

- PER: priority = |TD error|, recomputed each replay.
- MIR: priority = the change in loss the sample would suffer under the
  proposed parameter update. Closed-loop on the present batch.
- GSS: sample selection maximizes *gradient diversity* — explicit coverage
  objective in gradient space.
- MER: prioritization arises through meta-learning, again function of
  current gradient alignment.

## Mattar-Daw was misapplied

Mattar-Daw 2018 (Nature Neurosci) is **explicit**: the objective is expected
future reward improvement at the next decision, not retention of past
performance. The `need × gain` framework presumes (1) a current decision
whose value depends on backed-up information, (2) replay is the bottleneck
channel for that backup. Neither holds in continual pretraining.

This is exactly the failure mode the `feedback-verify-implementations`
memory rule warns about: the mechanism R7 implements (static structural
tagging) doesn't match the mechanism Mattar-Daw analyzes (state-value
dependent dynamic priority).

## Hippocampal biology disfavors static prioritization

- Foster & Wilson 2006, Joo & Frank reviews: SWR replay is biased by
  **recency** and **reward valence**, both dynamic.
- Schapiro 2018: human SWR prioritizes *weakly learned* items —
  inverse to a concept-strength filter.
- Schapiro 2017: statistical regularity extraction lives on a different
  anatomical pathway (EC→CA1) than episodic replay (DG/CA3). They
  cooperate, not "concepts gate episodic replay."

## Why the 12.4% filter hurts

Chaudhry 2019 ([arXiv 1902.10486](https://arxiv.org/abs/1902.10486)):
"in tiny-memory CL, simple uniform-random ER over the full buffer
significantly outperforms specifically designed CL approaches."

Buzzega 2021 ("Rethinking ER", [arXiv 2010.05595](https://arxiv.org/abs/2010.05595)):
the 5 tricks that fix ER are bias-balancing, augmentation, and loss
balancing — not relevance filtering.

Our setup: pool=1024, concept-tagged subset ~127, batch B=64, replay 50%
→ cycling through 127 contexts hundreds of times. Random sees ~1024.
8x effective buffer compression — exactly the regime where literature
says uniform wins.

## What does beat random in supervised CL

| Method | Wins | Why |
|---|---|---|
| GEM/A-GEM (2017-19) | Mixed | Gradient-projection. Memory itself is reservoir-random. |
| **MIR** (2019) | Yes, modestly | Priority = loss under proposed update. Closed-loop. |
| GSS (2019) | Yes, modestly | Diversity in gradient space — coverage in disguise. |
| MER (2019) | Yes, small buffer | Meta-learns gradient alignment. |
| DER/DER++ (2020) | Yes, large effect | Reservoir sampling + logit distillation. |
| van de Ven GR (2020) | Yes vs no-replay | Generative model substitutes for buffer. |
| **Static concept tagging** (R7) | **No** | Not a winning method in any major benchmark. |

## Five preregistered follow-ups (each <1h GPU)

- **F1 — Coverage-varied concept replay.** Sweep filter strictness:
  top-K ∈ {10, 50, 200, 1000} + Hamming neighbors. Prediction: BWT
  recovers monotonically as coverage grows. If even K=10 doesn't beat
  random, the concept signal genuinely has no value.

- **F2 — Loss-magnitude priority (MIR-lite).** Score each pool entry by
  current prediction loss under W_start, sample ∝ loss. *Literature's
  strongest analogue*. Falsifies if beats random by ≥0.10 bpc; doors
  close on prioritization entirely if it loses to random.

- **F3 — Residual concept role at high coverage.** Random replay + small
  λ·loss on the concept-tagged subset's *retrieval* accuracy. Tests if
  concepts have any soft role once they stop being a hard gate.

- **F4 — Pool-size scaling.** POOL ∈ {256, 1024, 4096, 16384}. Random's
  advantage should shrink as concept-tagged subset count exceeds buffer
  effective size. Decides "small-buffer artifact" vs "concepts
  uninformative."

- **F5 — Recency + reward (biology-faithful).** Recency-decay × loss
  magnitude. Closest analogue to actual SWR replay. Should be the best
  non-random baseline; if even this loses, prioritization is dead.

Recommended order: **F1 + F2 first** — jointly settle coverage vs
relevance in one ~90-min GPU session.

## Honest bottom line

**Concept-prioritized replay is closed as a BWT mechanism for this
substrate.**

What is not closed: concepts may still have a role as
- soft auxiliary loss on random-sampled replay (F3)
- structure for the codebook (separate from selection)
- post-replay distillation target (DER++-style)

If we want "concept" in the M2 story, those three are the
literature-grounded escape hatches. If not, the strongest single forward
bet is MIR-style interference-based sampling (F2) — the one route in
modern CL that consistently beats random in supervised CL with small
buffers.

## Cleanest narrative for the writeup

> We tested whether concepts identify the schema-relevant memories worth
> rehearsing. They don't, in the way CLS suggested. The result rehabilitates
> the unbiased version of the consolidation-replay literature: coverage
> dominates relevance in the small-buffer regime, and dynamic interference
> dominates static structure when prioritization helps at all.
