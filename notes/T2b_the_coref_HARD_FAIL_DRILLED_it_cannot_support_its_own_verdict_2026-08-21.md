# T2b -- THE COREFERENCE `HARD_FAIL` DRILLED: **IT CANNOT SUPPORT A CLAIM ABOUT CUE-BASED RETRIEVAL — n=89, THE ARM DOES NOT BEAT ITS OWN SCRAMBLE, AND TWO OF THREE PARAMETERS WERE HAND-SET WITH THE SWEEP STILL CLIMBING AT ITS EDGE**

**No new run.** Re-reading `data/exp_coref_cue_based_retrieval_actr_activation_v1/metrics.json`.
**Standing rule being applied: a brain-faithful mechanism losing is `presumed impl-bug until proven
structural`. This is that check, and the artifact does not survive it.**

---

## 1. THE FULL ARM TABLE, WHICH THE VERDICT LINE DOES NOT SHOW

**`P_competitive` = pronoun accuracy where >=2 gender/number-compatible candidates exist.**
Denominators recovered from the reported fractions:

| arm | accuracy | n |
|---|---|---|
| **`base_principle_b`** — a **SYNTACTIC** constraint (Binding Principle B) | **0.7191** | 64/89 |
| `base_strict_cb` — Centering, strict Cb | 0.6966 | 89 |
| `actr_base` | 0.6180 | 55/89 |
| **`actr_parallel`** — the headline treatment | **0.5843** | **52/89** |
| ⚠️ **`actr_parallel_scrambled`** — **the SCRAMBLE CONTROL** | **0.5938** | **19/32** |
| `base_salience` — **our invented β=0.5 / λ=0.1 arithmetic** | 0.5618 | 50/89 |
| `floor_most_recent` / `floor_chain_all` | 0.5281 | 47/89 |
| `floor_singleton` | 0.0000 | — |

## 2. 🚨 **THE SCRAMBLE CONTROL SCORES *ABOVE* THE TREATMENT**

**`actr_parallel_scrambled` 0.5938 vs `actr_parallel` 0.5843.** *An arm that does not beat its own
scrambled control is not demonstrably using the structure it claims to use* -- and this one is
**below** it.

**⚠️ HONEST LIMIT, STATED BECAUSE IT MATTERS: THE DENOMINATORS DIFFER — 19/32 vs 52/89.** The
scramble ran on a **different, smaller subset**, so this is **not** a paired comparison and I will
not call it decisive. **What it does establish is the absence of the thing that was needed: there is
NO evidence the treatment beats its own scramble.** *And per the standing rule, a control must be
compared on the same population -- so the cell's own scramble evidence is unusable in either
direction, which is itself the defect.*

## 3. 📉 **n = 89 COMPETITIVE DECISIONS. THE PLAN'S OWN BAR WAS "HUNDREDS, NOT n=10".**

54 passages, 136 pronoun decisions, **89 competitive**. The headline `-0.1348` is **12 items**. The
CI `[-0.2500, -0.0337]` is **0.22 wide** -- *consistent with anything from a trivial difference to a
catastrophic one.* **A width is not an effect.**

## 4. ⚙️ **TWO OF THREE PARAMETERS WERE NOT PINNED — AND THE SWEEP WAS TRUNCATED WHILE STILL RISING**

```
actr_params: { "d_PINNED": 0.5,  "W_not_pinned": 1.0,  "S_not_pinned": 1.5 }
```

The cell's own field names concede it: **`d` is pinned; `W` and `S` are ours.** And its sensitivity
table shows the result is *dominated* by `S`:

| `S` | 1.0 | 1.5 (**chosen**) | 2.0 (**edge of sweep**) |
|---|---|---|---|
| powered | 0.5385 | **0.5769** | **0.6154** |
| g5g6 reviewed | 0.5405 | **0.5946** | **0.6486** |

**➡️ ACCURACY RISES MONOTONICALLY TO THE EDGE OF THE SWEPT RANGE AND THE SWEEP STOPS THERE.** The
value that was reported (`S=1.5`) is **not** the best value inside the cell's own sweep. *This is
the standing discipline verbatim: **copy the COMPUTATION exactly, SWEEP every PARAMETER** -- our
worst result copied a number, our best copied an operation. `S` is a parameter and it was not swept
to its optimum.*
*Note the honest limit in the other direction too: even the sweep's best (0.6486) does **not** reach
`base_principle_b` 0.7191. **The gap does not close by sweeping alone** -- so this is not a claim
that ACT-R would have won.*

## 5. 🔎 **AND IT CORRECTS MY OWN T2 FRAMING**

T2 said the thing to replace is *"our invented β=0.5/λ=0.1 arithmetic."*
**`base_salience` -- that exact arithmetic -- scores 0.5618, barely above the 0.5281 floor.** It is
**not** what is winning. **The best arm is `base_principle_b` at 0.7191: a SYNTACTIC constraint.**
*So "brain-faithful retrieval lost to our hand-rolled salience formula" is wrong twice over -- the
salience formula is near the floor, and what actually wins is a grammar rule.*

## 6. WHAT THE VERDICT SHOULD SAY

**Not `HARD_FAIL` for cue-based retrieval. `UNDERPOWERED / CONTROL-UNUSABLE / PARAMETERS-NOT-SWEPT`.**
The three defects are independent and each alone blocks the inference:
1. **n=89**, CI 0.22 wide;
2. the **scramble control is on a different subset** and does not separate from the treatment;
3. **two of three parameters hand-set**, with the sweep **still climbing at its boundary**.

**THE ORGAN QUESTION IS THEREFORE STILL OPEN, NOT ANSWERED IN THE NEGATIVE.** *And the standing rule
against generalising a narrow failure applies exactly here: a fair test of a weak implementation
proves that setup failed, not that the capability is impossible.*

## TLDR

Earlier tonight I found that the coreference upgrade I was about to propose had already been built a
week ago and scored **13.5 points worse**. That looked like a closed door. **I drilled it, and the
door is not closed — that experiment cannot support its own conclusion, for three separate reasons.**

**It tested itself against a scrambled version of its own input — and lost to it.** When a mechanism
can't beat its own nonsense control, it isn't demonstrably using the structure it claims to use. (Fair
warning: the scramble ran on a smaller sample, so this isn't proof either way — which is itself the
problem, since that control was the whole point.)

**It rests on 89 decisions.** The 13.5-point gap is twelve items, and the uncertainty range spans
everything from "barely different" to "disastrous."

**And two of its three settings were guessed.** The experiment's own field names admit it — one value
comes from the research, two we picked. Its own sensitivity check shows accuracy **climbing steadily
as one of those guesses increases — right up to the edge of what was tried, where it stops.** The
value reported wasn't even the best one it tested.

**It also corrects something I wrote earlier.** I said the brain-faithful method "lost to our
home-made formula." It didn't — our home-made formula is near the bottom too. **The thing actually
winning is a plain grammar rule.**

None of this means the brain-faithful version works. It means **nobody has yet run a test that could
tell us**, and the honest label is "underpowered and uncontrolled," not "failed."

## QUESTIONS

None.

## NEXT STEPS

1. **Re-label the verdict** from `HARD_FAIL` to underpowered/control-unusable. *Filed as a reading of
   the artifact; the landed `metrics.json` is deliberately NOT modified.*
2. **Any re-run needs three fixes:** n in the hundreds; the scramble on the **same** items; and `S`
   and `W` **swept past** the point where the curve stops rising.
3. **The more interesting question is why a SYNTACTIC constraint (0.7191) is beating everything
   else** -- including both brain-motivated arms. *That is where the signal is.*
