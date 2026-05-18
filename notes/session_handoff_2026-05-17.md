# Session handoff — 2026-05-17

Compact notes to pick up the thread in a fresh session.

## Where we are (FINAL — late-session breakthrough converged)

**Best result: 2.505 bits/char** (combined config, 15 epochs, converged).
Tiny transformer ceiling: 2.39 bits/char.
**Gap: 0.11 bits/char** — down from 0.45 at the start of this session.

Configuration that delivered this:
- N=4096 FHRR substrate, K=4, arousal=0.3, beta=8.0
- Pointer-chain pool M=1024, alpha=0.3, built during epoch 1 then frozen
- Multi-epoch with decay=1e-4 per batch
- 15 epochs (effectively converged; epoch 10→15 improvement only 0.007 bits)
- Argmax accuracy: 60.3% (up from 54.6% baseline)
- No backprop, no gradient descent

Convergence curve:
  epoch 1:  2.847 bpc (54.5% argmax) — matches single-pass combined
  epoch 5:  2.544 bpc (59.6% argmax) — most of the gain
  epoch 10: 2.512 bpc (60.1% argmax) — diminishing returns
  epoch 15: 2.505 bpc (60.3% argmax) — converged

## The mechanism that unlocked it

Vanilla multi-epoch ALONE overfits catastrophically (W norm explodes,
margins collapse, bpc rebounds upward despite argmax climbing). Vanilla
pool alone gives ~0.25 bits at single-pass. Putting them TOGETHER unlocks
something neither does alone: the fixed pool provides stable external
information; W can specialize on what the pool does not cover; decay
keeps W norm bounded. The combination *compounds multiplicatively*.

This is a real architectural insight that wasn't obvious from individual
ablations. Lesson: architectural complexity that provides INDEPENDENT
information sources stabilizes multi-epoch training in a way that pure-W
multi-epoch cannot.

Architecturally this is exactly why transformer attention works — attention
provides external information per token that prevents the FFN from
overfitting via its own iterative updates.

## Pre-breakthrough best (for reference)

Best single-pass result was 2.84 bits/char (gap 0.45):
- N=4096 + pointer-chain (M=1024, alpha=0.3), single epoch

## What we know about the gap (from signal-stage profiling, commit pending)

Profiling decomposed the loss into three stages:

| Stage | Result | Bottleneck? |
|---|---|---|
| A: Bundle recovery (unbind context bytes from bundle) | **100%** | No — bundle is perfect |
| B: W's argmax accuracy (correct byte top of similarity ranking) | **54.6%** | **Yes** — this is the bottleneck |
| C: Softmax cleanup given W's hypervector | reasonable | Mostly fine |

Gap decomposition:
- ~0.18 bits achievable via better cleanup alone (max cleanup-side lift)
- ~0.27 bits requires raising W's argmax accuracy above 54.6%

**Implication: the leverage is on W's accuracy, not on readout tricks.**

## What we tested and what landed (this session)

| Experiment | Result vs baseline 3.16 |
|---|---|
| Pointer-chain (M=1024, alpha=0.3) | **−0.25** ✓ |
| Larger N=4096 | **−0.14** ✓ |
| Combined N=4096 + pointer-chain | **−0.32 → 2.84** ✓✓ best |
| Multi-epoch Hebbian (3 epochs, N=1024) | −0.15 (epoch 3 best) ✓ |
| Multi-epoch (5+ epochs) | overfits — W norm explodes, margins collapse |
| Eligibility traces | null at this corpus scale |
| Homeostatic decay (1e-4) | null on single-pass |
| Surprise-modulated arousal (as implemented) | +1.1 (hurt — wrong formula) |
| Krotov polynomial cleanup (n ∈ {2,3,5,7}) | hurts at every n>1 (magnitude scale issue) |
| Bloch/randomized DFT substrate | −0.02 (noise) |

## Why Krotov and Bloch failed (root causes)

- **Krotov**: FHRR similarities are ~0.05, not ~1. Polynomial of small numbers crushes the gap. Krotov needs saturating similarities to work.
- **Bloch**: Substrate geometry isn't our bottleneck — W learns to compensate for any reasonable substrate. Frady's prediction of "same scaling, smaller constant" was correct; we just don't gain at this scale.

## Top finding from this session

**Multi-epoch Hebbian works (modestly) but breaks Hebbian's anti-overfit property.** W norm grows unboundedly across epochs; margins collapse after epoch 3. Adding weight decay (a stronger version than the 1e-4 we tested on single-pass) should unlock more epochs and capture more of the argmax-accuracy growth (54% → 59% across 20 epochs even without regularization).

## Priority experiments queued for next session

In order of expected payoff:

1. **Multi-epoch + weight decay sweep** — script written: `experiments/exp_multiepoch_decay_charlm.py`. Was about to run when context filled. Just run `python exp_multiepoch_decay_charlm.py`. Expected: 3.005 (epoch 3 no decay) → ~2.80-2.95 with decay at more epochs.

2. **Best combined run**: 3 epochs + N=4096 + pointer-chain + best weight decay. Probably 2.6-2.7 bits/char.

3. **Modern Hopfield over pointer pool (R1 in backlog)** — predicted 0.10-0.20 bits from pass-2 materials research. Cleanup-side, attacks remaining 0.18-bit cleanup ceiling.

4. **Multi-head W matrices (A2 in backlog)** — addresses Stage B (argmax accuracy) directly. Predicted 0.05-0.20.

5. **Multi-layer Hebbian (A1 in backlog)** — biggest potential lift if it works. ~3-4 hours to implement.

Full backlog of 30+ experiments at `notes/experiments_backlog.md`.

## Research findings to remember

**Cross-field research, pass 1+2 + materials science** identified the framework:

- **Our setup IS provably equivalent to random-features kernel ridge regression with softmax link** (Mei-Misiakiewicz-Montanari 2022). The 0.45-bit gap is at least partly the random-features approximation gap to a learned kernel.
- **Top-5 actionable from deeper materials-science dive** (in `data/exp_*` and `notes/experiments_backlog.md` for details):
  1. Modern Hopfield readout over pool (Ramsauer-style)
  2. Stealthy hyperuniform atoms (Torquato 2018)
  3. Cahn-Hilliard conservative Hebbian update
  4. Hierarchical pointer-chain (multi-ring)
  5. Nucleation-threshold gated updates
- **Schlag-Irie-Schmidhuber 2021** is the closest published mathematical sibling — same delta-rule outer-product update on a single fast-weight matrix. Their slow network uses gradient descent; ours doesn't. They lag transformer by ~2 perplexity on WikiText-103. Our differentiators are HDC substrate + local-only learning + ablation traceability + multi-relation + multi-modulator.

## Key strategic facts

- **Track 0 is alive tier** — Bet B (Hebbian-trained VSA-LM from scratch, no backprop) is empirically viable at small scale.
- **The hardware story is real** — IBM PCM 2020 gives 3 orders of magnitude on cleanup; realistic system-level claim 10×-100× on cleanup-heavy workloads. BSC is deployment-friendly; FHRR is research-only until phase-based silicon catches up.
- **The transformer baseline overfits catastrophically at 38KB** — final test bpc 3.61 after 10 min, requires validation-monitored early stopping to get 2.39. Our architecture has built-in regularization from single-pass training (but multi-epoch breaks this).

## Late-session partial: dendritic-NL experiment (stopped early for GPU transition)

Three of six variants completed before stopping for desktop-GPU transition:

| Variant | epoch 5 test_bpc | W_norm | Verdict |
|---|---|---|---|
| baseline_linear (control) | 2.544 | 86 | matches reference |
| magnitude_tanh alpha=1 | 4.14 | 1041 | FAILED, W exploded |
| magnitude_tanh alpha=3 | 4.14 | 1636 | FAILED, W exploded worse |
| magnitude_relu b=0.5 | running at epoch 1 = 2.857, W_norm 46 | — | looked stable so far |
| magnitude_sigmoid alpha=2 | not run | — | not run |
| real_imag_tanh | not run | — | not run |

Reason for stopping: switching to GPU for ~10x speedup. The whole 6-variant
sweep takes ~45 min on CPU, will take ~5 min on a 4090. Re-running on GPU is
cheaper than waiting.

Pattern so far: magnitude-bounding nonlinearities (tanh) destabilize the
delta-rule geometry and cause W norm to explode. The relu variant (zero out
small magnitudes, keep large ones) survives the dynamics — different
geometric operation. Real_imag_tanh and magnitude_sigmoid remain unknown.

## Next session - desktop GPU setup

Setup prompt is in the message I sent the user; basically:
  - C:\dev\hd-instrument as install location
  - python -m venv .venv, install CUDA-PyTorch (cu121)
  - Make experiment scripts device-aware
  - Re-run dendritic NL sweep (will take ~5 min total instead of 45)
  - Then proceed with BR5 (grid-cell positions), BR2 (DG projector),
    BR3 (climbing-fiber error matrix), BR4 (PFC attractor), MX10
    (parallel tempering)

Priority order based on session findings:
  1. BR5 grid-cell positions (FHRR-native, Frady-Kanerva-Sommer 2018) — best
     evidence-backed substrate change
  2. BR2 DG sparse projector — attacks pool collisions
  3. BR3 climbing-fiber error matrix — federated module the brain has and we don't
  4. BR4 PFC working memory attractor — adds new state dimension
  5. MX10 parallel tempering K=8 + RSB diagnosis — the materials top pick;
     also informs whether further work is sampling-side or capacity-side
  6. MX2 two-time aging scan — diagnostic; tells us if we're in trap vs CTRW regime

## What to do first thing next session

1. **Run `experiments/exp_multiepoch_decay_charlm.py`** — pre-written, just execute. Tells us if decay unlocks more epochs.
2. Based on result, decide between: weight-decay + N=4096+pool combined, or pivot to multi-head/multi-layer (Stage-B attack).
3. If still stuck in mid-2.7s, scale corpus is next move.

## Auto mode quirk to remember

The auto-mode classifier denied running a freshly-written script because "the agent is running unverified code under auto mode without user confirmation of this specific experiment." So the user may need to explicitly allow `Bash(.venv/Scripts/python.exe experiments/*)` in settings, or approve the first run manually. After that the pattern should auto-approve.

## Memory state

Memories at `C:\Users\marsh\.claude\projects\d--AI\memory\` are up to date with:
- User profile (research-oriented, brain-inspired intuition, brutal honesty)
- Feedback memories (no smoke, step-back eval, brain-inspired-is-durable, plain-language)
- Project memories (two-bets structure, observability layer shipped)
- Reference memory (repo location, git workaround for safe.directory)

These will carry to the next session via memory recall.
