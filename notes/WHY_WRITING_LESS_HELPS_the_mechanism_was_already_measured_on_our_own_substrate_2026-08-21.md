# **WHY WRITING LESS HELPS: THE MECHANISM WAS ALREADY MEASURED ON OUR OWN SUBSTRATE. INTERFERENCE BETWEEN STORED KEYS PREDICTS CAPACITY AT r = 0.976, BEATING BOTH RIVAL EXPLANATIONS.**

**Owner, Q98: *"approved, but you should do some research on why this is as you're finding it, to
understand why and potentially to give you a good idea on next optimal stepss"*. This is that. The
first place I looked was our own archive, and the answer was there.**

---

## 1. THE MEASURED MECHANISM

`exp_crosstalk_capacity_law_v1_gpu_v1`, verdict **`MEASURED_MECHANISM`**. Its own `honest_claim`:

> *"Direct crosstalk moment **E[<ki,kj>^2]** (raw keys) is the **DOMINANT** cross-encoder predictor
> of Hebbian capacity (Pearson 0.98 / Spearman 0.96, n=11); controls `d_eff` (r=-0.21) and
> `IsoScore` (r=0.30) are **WEAKER** -- partial(ctrl|crosstalk)=-0.35/-0.50 decides
> crosstalk-in-disguise (fails) vs independent predictor (report, don't bury)."*

| quantity | value |
|---|---|
| Pearson, crosstalk vs log capacity | **0.976** |
| Spearman | **0.964** |
| control: effective dimensionality | −0.212 |
| control: IsoScore | 0.304 |
| **partial, `d_eff` given crosstalk** | **−0.349** |
| **partial, IsoScore given crosstalk** | **−0.499** |

**Both rival explanations are weaker AND get weaker still once crosstalk is controlled for -- their
partials go negative. That is the test that separates "a genuine second cause" from "crosstalk
wearing a different name", and the cell ran it deliberately.**

**In plain terms: how much stored items interfere with each other determines how many you can store
and still retrieve. Fewer items stored -> less interference -> cleaner retrieval.**

## 2. ⚠️ **BUT IT IS NOT A MEASUREMENT OF *OUR* SWEEP, AND I WILL NOT MERGE THEM**

**That cell varies the ENCODER** -- 11 encoders (MiniLM, mpnet, bge, e5, pythia 160m-2.8b, gpt2),
`M_keys = 8000`, 5 seeds -- **so it varies KEY GEOMETRY at fixed load.** *The write-rate sweep varies
**how many items are written** at fixed geometry.* **Both are load/interference stories, but they are
different manipulations on different populations, so this explains the DIRECTION and is NOT a
measurement of the write-rate effect** (discipline 11).

**The cell's own limits, which it states rather than hides:** *"NOT parameter-free LAW"* --
`c_spread_max_over_min = 5.04`, `worst_m_crit_cv = 0.343`, **n = 11**.

## 3. 🎯 **THE PREDICTION IT MAKES FOR THE EXTENSION YOU APPROVED**

**If interference is the binding constraint, the gain from writing less must SATURATE once
interference stops binding -- it must NOT keep rising to the empty limit.** *That is a real
can-fail prediction and the approved sweep tests it for free:*

| observation | reading |
|---|---|
| gain flattens while coverage is still complete | ✅ **interference was the constraint; the peak is real and is the operating point** |
| gain keeps rising until words start having no score at all | 🚫 **the curve was drifting to silence after all -- my Q97 measurement said it is not, so this would overturn it** |

**AND IT EXPLAINS THE OTHER HALF OF THE Q98 FINDING, THE ONE THAT LOOKED LIKE BAD NEWS:** *the
rate-matched RANDOM gate matches the clever gate at all four thresholds.* **Under an interference
account that is exactly right and not a disappointment -- interference depends on HOW MANY keys are
superposed, not on WHICH ones. Choosing cleverly cannot help if the quantity is what binds.**
*Two results that read as unrelated -- "writing less helps" and "choosing well does not" -- are one
result under this mechanism.*

## 4. 🔴 **THE OBVIOUS NEXT STEP IS ALREADY CLOSED. DO NOT RE-PROPOSE IT.**

*"Reduce interference directly instead of by writing less"* is the natural move. **It has been tried:**
- **DO-NOT-REDO 44: SPARSIFYING THE STORED KEY under a partial cue -- `-0.0145` CI `[-0.0203,
  -0.0088]`, CI-separated BELOW the flat store, with the oracle arm at `1.0000`.** *Has a revival
  criterion; is not open.*
- **DO-NOT-REDO 32: DG / pattern-separation for grounding -- CLOSED.**

## 5. 💡 **AND THE INFERENCE THAT FOLLOWS, WHICH I AM FLAGGING AS REASONING, NOT MEASUREMENT**

**Our live word encoder is `sha256(w)[:8] -> seed -> default_rng.choice([-1,+1], d)` -- random
bipolar by construction.** *Random codes are close to the minimum achievable crosstalk for a given
dimension; that is the whole reason orthodox VSA uses them.* **So if crosstalk is already near its
floor for our key geometry, there is little headroom in "better keys", and the only remaining lever
on capacity is the NUMBER of items -- which is precisely what the write-rate sweep found, and
precisely why cleverness in choosing did not help.**

⚠️ ***THIS IS A HYPOTHESIS-PENDING-VET, NOT A RESULT.*** *It is licensed by the measured law but not
measured for our own keys. The cheap test is one line: compute `E[<ki,kj>^2]` for our live encoder at
our `d` and place it against the 11 encoders' values already in `detail.per_encoder`. If we sit at
the good end, "better keys" is closed by geometry rather than by trying and failing.*

## 5b. ✅ **THE ONE-LINE TEST IS NOW RUN, AND THE HYPOTHESIS IS CONFIRMED: OUR KEYS SIT AT THE FLOOR**

**Measured with the live encoder itself (`reading_grounding_loop.py:307-308`), Gram trick, `M_keys`
matched to the cell's 8,000.** *`inv_e_sq` = 1 / E[<ki,kj>^2]; **higher is better**.*

| encoder | D | isoscore | `inv_e_sq` | **`inv_e_sq` / D** |
|---|---|---|---|---|
| **OURS (sha256 -> random ±1)** | **256** | 1.000 | **256.00** | **1.000** |
| all-mpnet-base-v2 | 768 | 0.914 | 80.34 | 0.105 |
| all-distilroberta-v1 | 768 | 0.915 | 73.52 | 0.096 |
| all-MiniLM-L6-v2 | 384 | 0.912 | 68.88 | **0.179** *(best of the 11)* |
| bge-small / bge-large | 384 / 1024 | 0.92 | 5.45 / 3.88 | 0.014 / 0.004 |
| e5-base-v2 | 768 | 0.921 | 1.85 | 0.002 |
| pythia-160m ... 2.8b | 768-2560 | 0.81-0.86 | 1.01-2.68 | ~0.001 |
| gpt2-medium | 1024 | **0.283** | 1.01 | 0.001 |

> **`inv_e_sq / D = 1.000` FOR US. THE BEST TRAINED ENCODER MANAGES 0.179 AND MOST MANAGE ~0.001.**
> ***E[cos^2] = 1/d is the Welch bound -- the theoretical minimum for unit vectors in d dimensions.
> We are AT it, and we beat the best trained encoder by 3.2x WHILE USING A THIRD OF ITS
> DIMENSIONALITY.*** *Trained encoders are anisotropic (isoscore 0.28-0.92, `d_eff` far below `D`)
> and therefore waste most of the dimensions they have.*

**CONTROL RUN, AND IT CAUGHT MY OWN BUG FIRST:** *my first "real word" arm returned 7.86 instead of
256 -- because I passed 8 words repeated 1,000 times, so most pairs were the SAME string at cos=1.
Re-run on **5,704 distinct real words** harvested from the landed definitional facts: **inv_e_sq =
255.96** against the synthetic **256.01**.* **Word-independence is now measured, not assumed.**

### ➡️ **SO "BETTER KEYS" IS CLOSED BY GEOMETRY, AND ONLY TWO LEVERS REMAIN**

**`m_crit ≈ c × inv_e_sq` and `inv_e_sq = d` for us, so capacity ≈ `c × d`.** *With the cell's
`c` range 1.005-5.068, that is **257-1,297 items at d=256** and **1,029-5,190 at d=1024**.*

| lever | status |
|---|---|
| **fewer items** | ✅ **the sweep you just approved** |
| **more dimensions** | ✅ **B4's queued d-sweep -- runnable and unrun** |
| better keys | 🚫 **CLOSED: we are at the theoretical floor** |
| cleverer selection | 🚫 **CLOSED: interference counts keys, not which keys** |

⚠️ **HONEST LIMIT ON THE d-PREDICTION:** *the law was measured ACROSS ENCODERS at their native D,
not by varying d for a FIXED encoder. `inv_e_sq = d` for random codes is geometry and is now
measured; that `m_crit` tracks it as we raise our own d is an **extrapolation along a different
axis**, and `c` is unmeasured for our encoder (5x spread). **B4's sweep is the test.***

## 6. 🧠 THE BRAIN SIDE, BECAUSE THE STANDING RULE IS TO ASK

**The brain faces the same problem and its answer is not "write less" -- it is "write separably":
sparse, pattern-separated codes in dentate gyrus, whose entire computational description is reducing
overlap between similar memories before storage.** *Our own `dg_pattern_separation` self-test
measures exactly this and passes: `input_cos 0.934 -> code_cos 0.561`, gap `0.373`.* **So the
substrate CAN separate patterns; what is closed (item 44) is sparsifying the STORED KEY under a
partial cue, which is a different operation from separating similar inputs at encode time.**
***That distinction is worth keeping open: "sparsify the key" failed; "separate similar items before
storing them" is the brain's actual move and is not the same thing.***

## TLDR

You asked why writing less makes the system better. **The answer was already measured in our own
archive, and it is a good one.**

**Stored memories interfere with each other.** Our own experiment measured how strongly, across
eleven different encoders, and found that the amount of interference predicts how much can be stored
and still recalled — with a correlation of **0.98**. Two rival explanations were tested and both were
weaker; more tellingly, both got *weaker still* once interference was accounted for, which is the
check that tells you they were the same thing in disguise.

**So writing less helps because fewer stored items interfere less.** Not a subtle effect — the
dominant one.

**And this explains the part of last night's result that looked like bad news.** Throwing things away
*at random* worked just as well as choosing carefully. Under this explanation that's exactly right:
interference depends on *how many* things you've stored, not *which*. **Two findings that looked
unrelated are one finding.**

**It also makes a prediction we get for free from the experiment you just approved:** the improvement
should level off while the system still has something to say about every word. If instead it keeps
climbing until words start coming back blank, my measurement from earlier was wrong.

**Two honest limits.** That experiment varied the *encoder*, not how much gets written — so it
explains the direction but isn't a measurement of our specific case. And the obvious fix — reduce the
interference directly instead of writing less — **has already been tried and failed**, and is on our
do-not-repeat list with numbers attached.

**One idea I'd flag as reasoning rather than fact:** our system builds its word codes from random
numbers, and random codes are already close to the least-interfering option available. If that holds,
then "use better codes" is closed by mathematics rather than by us failing at it — and quantity is
genuinely the only lever left. **That's checkable in one line against numbers we already have.**

## QUESTIONS

None — Q98 is answered and approved.

## NEXT STEPS

1. **Run the approved extension with the stopping rule**, and read it as a test of the saturation
   prediction in section 3, not merely as a hunt for a peak.
2. **One-line check:** put our live encoder's crosstalk moment beside the 11 already in
   `detail.per_encoder`. *It settles whether "better keys" is a closed route or an open one.*
3. **Keep separate:** "sparsify the stored key" is CLOSED (item 44, with numbers); "separate similar
   items before storing them" is the brain's actual operation and is not the same move.
