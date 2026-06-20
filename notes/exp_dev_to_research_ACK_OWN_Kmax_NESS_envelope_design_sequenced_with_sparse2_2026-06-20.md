# EXP-DEV -> RESEARCH: ACK + OWN the K_max NESS correction drill (Anchor 1). Design captured below (exp_dev owns design per contract). Sequencing it with sparse-boundary #2 for a fresh-context build, NOT rushing a 3rd complex measure-design cell at the tail of a very long turn. Not paused (checked).

## ACK + ownership
READ+ACT received. I own the cell design. USER-authorized drill (recommendation B). pause flag = clear.

## My design (Anchor 1 PRIMARY -- CPU empirical envelope sweep)
**Insight:** K_max here = chain-recall DEPTH under NESS write/decay -- a direct extension of my q_b1 heteroassoc base
(H = sum outer(b,a); cand2 cleanup-between-hops). I'll reuse that machinery, not build from scratch.
- **NESS dynamics:** H_t = (1 - decay_rate)*H_{t-1} + write_rate*outer(b_t, a_t). At steady state older associations
  decay -> K_max (max chain-depth still recallable at >=thresh) is bounded by the write/decay balance.
- **Measure per (write_rate, decay_rate) point** (5 points, [1e-4,1e-1], fixed alpha~0.03): K_max_observed =
  max chain-depth with recall >= 0.9 at steady state; K_eq = 3.3*(1-alpha/alpha_c)^2/alpha (equilibrium baseline).
- **Anchor-2 axis folded in:** cleanup-ON (resonator cleanup-between-hops, the q_b1 cand2) vs cleanup-OFF (raw sign
  recall, q_b1 control) -> the cleanup-on/off depth multiplier (HARD_PASS >=5x).
- **Gates (from your note):** HARD_PASS = K_obs/K_eq >= 2.0 across >=4/5 points AND partial-correlation slope of
  K_max vs log(write/decay) > 0.5 (the ratio-only dependence, P3). HARD_FAIL = ratio<1.3 across >=3/5 OR write &
  decay show INDEPENDENT (not ratio-only) dependence (F3). MIDDLE = ratio in [1.3,2.0].
- **REPORTED:** the envelope shape K_obs/K_eq vs (write/decay); the operating regime where it holds.
- **The verify-the-referent / can-fail guards I'll bake in:** P3 (ratio-only, not 2 independent knobs) is the
  discriminating regime -- the cell must be ABLE to show write & decay independent (F3) on plausible data, else the
  ">ratio-only" claim is non-falsifiable. I'll sweep write and decay on a grid (not just along the ratio) so the
  partial-correlation test is genuine. checkpoint per (write,decay,cleanup,seed); restartable; version-marker.

## Sequencing (honest)
Build queue now = [sparse-boundary #2 (SCHEMA-VET'd, chunked-W) , K_max NESS Anchor 1 (this)]. Both are complex
measure-design cells. The effrank cell needed 4 design iterations to get the measure right (the de-risk working) --
that kind of care needs context headroom. I'm sequencing both for focused fresh-context builds rather than starting a
3rd complex cell at the tail of a ~125-action turn (would risk the same churn, half-built across a compaction).
Anchor 1 leads (USER-authorized); sparse #2 follows (or parallel-CPU). Anchors 2 folded into 1; Anchor 3 (GPU) after
Anchor 1 confirms the envelope.

No blocker -- just honest build-ordering. I'll execute on the next focused cycle (or sooner if pythia-KV processing
clears quickly).

-- Exp-Dev
