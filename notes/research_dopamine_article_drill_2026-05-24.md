# Research drill — Dopamine accelerates learning via signal DURATION (not magnitude)

**Date**: 2026-05-24
**Trigger**: User shared article https://neurosciencenews.com/dopamine-accelerate-learning-reward-30742/
**Sub-agent**: Research
**Wallclock**: ~6 min (1 WebFetch + cap-map lookups)

---

## 1. Article finding

Gong, Martell, Dudman, Coddington (2026, *Science*, DOI 10.1126/science.aeb0813)
report that mice learn three behavioral tasks (hidden-target navigation, reach-
to-pull motor, sensorimotor decision) **orders of magnitude faster** when reward
magnitude is 1-2 orders larger than standard laboratory amounts: mastery in **one
day with <10 large rewards** versus **weeks with thousands of small rewards**.
Subject-to-subject variance also collapses (week-to-month range → few days).

**The core mechanism is the punchline**: large rewards do NOT simply produce a
larger dopamine *spike*. They **extend the temporal duration** of the dopamine
signal in motivation networks. The authors confirm this by **artificially
extending dopamine duration with optogenetics + standard-magnitude rewards** and
recovering the same accelerated learning. Three measured components:

1. Learning rate per trial (more update per repetition)
2. Day-to-day consolidation (carryover between sessions)
3. Sustained task engagement (the single largest individual-variance driver)

In RL-theoretic language: **dopamine duration is an effective eligibility-trace
window**, not a TD-error magnitude. Longer trace → more state-action pairs
credited per reward delivery.

---

## 2. Substrate mapping — partial, NOT orthogonal

The substrate's standing **Cap 5 (Online W writes, ✅ at FULL, v153 + v159
noise envelope p≤0.30)** uses an explicit learning-rate schedule:

```
lr(t) = 1 / (1 + t/10)      # Robbins-Monro
        + SNAP saturation guard at threshold 1.0
```

This is the substrate's only trained-like primitive — and it has **exactly
the structure dopamine modulates in the paper**: a per-step scalar that
controls how much each write updates W. The article's central claim
(duration > magnitude) gives us a **specific, falsifiable mapping**:

| Brain | Substrate analog |
|---|---|
| Dopamine spike magnitude | lr peak value at t=0 |
| Dopamine signal **duration** | lr decay timescale (the `10` in `1+t/10`) |
| Reward prediction error | retention loss / target mismatch on W·q |
| Eligibility trace window | number of recent writes still above SNAP threshold |
| Reward magnitude scaling | scalar gain on lr-schedule envelope |

The non-obvious, structural finding from the paper: **doubling peak lr is NOT
equivalent to doubling lr-window length**. The optogenetic-extension result is
the crucial test that rules out a pure-magnitude account. Substrate translation:
**at fixed total "lr budget" (∫ lr dt = const), is wider-and-shorter equivalent
to taller-and-narrower for online retention under noise/CF?**

This is genuinely 1-edge to Cap 5 — not 2-edge, not vibes. We already have the
mechanism; we have not characterized the **shape** of the lr envelope, only
the Robbins-Monro default.

---

## 3. Honest reading per feedback-no-smoke

**Where this is real**: Substrate HAS a learning-rate primitive (Cap 5).
The article's central claim is a non-trivial empirical fact about lr-envelope
SHAPE (duration vs. magnitude trade-off) that translates directly to a
question we can ask of `wave14_online_W_*` infrastructure. Cap 5 noise
envelope FAILED at p=0.40 — there is real headroom for "what lr schedule
makes online W robust further into the noise regime?"

**Where I would be smoking**: Three places I refused to claim.

a. The article's third component ("sustained engagement") is a behavioral /
   attentional construct without a substrate analog. No mapping. Drop it.

b. The "consolidation across sessions" component maps loosely to substrate
   **replay** (`replay_preshift_K4` shows replay is COST-FREE for Phase A).
   But the paper's consolidation claim is about offline carryover of the
   *behavioral policy*, not weight consolidation per se. This is 2-edge —
   would need its own drill, not bundled here.

c. **The brain-inspired framing does NOT make the result more likely to
   transfer**. The substrate-relevant question is purely structural:
   does ∫-preserving lr-envelope reshaping change CF resistance? That's a
   numerical question, answerable in CPU smoke.

---

## 4. Concrete anchor proposal

**Name**: `wave14_online_W_lr_envelope_duration_v1`

**Hypothesis (one line)**: At fixed ∫ lr dt across t∈[0, T], wider-shorter
envelopes (low peak, long tail — "extended dopamine") yield strictly better
ONLINE_W_RESISTS_CF under noise p∈{0.20, 0.30, 0.40} than taller-narrower
envelopes ("brief spike"), holding seed, M_init, n_writes, SNAP threshold
constant.

**Design** (CPU smoke, then GPU FULL if smoke clears):
- 4 lr envelopes at fixed ∫=10.0:
  - E1 (Robbins-Monro baseline): `1/(1+t/10)`, decay timescale τ=10
  - E2 ("brief spike"): rectangular lr=2.0 for t∈[0,5], 0 after — high-mag short
  - E3 ("extended dopamine"): rectangular lr=0.5 for t∈[0,20], 0 after — low-mag long
  - E4 ("optogenetic-extended"): Robbins-Monro shape but τ=40 (4× wider tail)
- N=4096 bipolar, n_writes=50, n_seeds=3, noise p∈{0.20, 0.30, 0.40}, SNAP=1.0
- Metric: retention accuracy min_acc≥0.95 (same as Cap 5 noise envelope)

**Queue**: CPU smoke first (`queue_add` with `desktop_cpu` tag, ETA ~90s).
GPU FULL only if E3 or E4 ≥ E1 at p=0.30 AND any cell improves at p=0.40.

**HARD PASS**: E3 OR E4 strictly dominates E1 at p∈{0.30, 0.40} (better
retention at equal ∫). Verdict: `LR_DURATION_BEATS_MAGNITUDE` —
substrate analog of dopamine-duration mechanism confirmed; opens Cap 5
envelope expansion into p=0.40 regime.

**HARD FAIL**: All envelopes within ±0.02 retention at p∈{0.30, 0.40}.
Verdict: `LR_ENVELOPE_SHAPE_NEUTRAL` — under ∫-constraint substrate is
insensitive to shape; the dopamine-duration analogy was vibes-only;
file as "interesting but orthogonal at Cap 5 operating point".

**INCONCLUSIVE / mixed**: any non-monotone pattern across τ — trigger 2x
level-2 drill on envelope dose-response.

**ETA**: smoke 90s + 3 seeds × 4 envelopes × 3 noise = 36 cells ≈ 18min wall
on CPU. GPU FULL (if triggered) ~6min.

---

## 5. 2x drill recommendation

**Not yet.** The article finding is one publication; the substrate mapping is
1-edge but the empirical question is well-posed and cheap to test directly. A
2x level-2 drill would be appropriate **after smoke verdict** — specifically
if HARD PASS lands, drill should (a) characterize the τ-vs-noise-resistance
surface (dose-response), (b) check whether SNAP threshold interacts with τ,
(c) lit-scan for "eligibility trace duration + Hopfield online learning"
intersection (Tolman-Eichenbaum-style replay literature is adjacent per
feedback-dont-dismiss-adjacent-methods).

Per feedback-2x-means-depth: 2x is for drilling EXISTING findings deeper, not
verifying article claims we haven't tested yet. Run the anchor first.

---

## 6. Filing

- Cap_map: do NOT update yet — anchor not run. If HARD PASS, propose new
  sub-cap "Cap 5a Online W lr-envelope duration mode" or expand Cap 5
  envelope row.
- Status log: write For-You entry with importance≈medium ("dopamine-duration
  article → Cap 5 lr-envelope shape probe queued").
- Pause flag: `data/orchestrator_paused.flag` — if active, this is a
  Research DELIVERY only; do NOT auto-dispatch to exp_dev without explicit
  user resume per feedback-obey-user-pause-explicitly.
