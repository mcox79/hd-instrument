---
priority: 2
review: EXCELLENT
review_text: "Bounded the whole solution space with oracle ceilings instead of trying rules one at a time: a perfect router scores EXACTLY the channel, so no monotone combination has headroom. Killed the crux I named -- peakedness predicts prior-error at AUC 0.4033, below chance -- and found the correlated-error mechanism I had missed: 95.65 percent of the channel wrong picks are higher-frequency than truth."
---

> # 🥇 **MY REVIEW -- EXCELLENT. IT KILLED THE CRUX I NAMED, WITH A DIRECT MEASUREMENT.**
> *Reviewed 2026-08-24. Re-verify PASSES, 13 substantive checks. Everything below is from that run.*
>
> ## ✅ **IT ANSWERED THE BRIEF BETTER THAN THE BRIEF ASKED, BY BOUNDING THE WHOLE SOLUTION SPACE**
> Instead of trying combination rules one at a time, it ran the ORACLE CEILINGS -- and they settle it:
>
> | ceiling | value | what it forecloses |
> |---|---|---|
> | `ORACLE_ROUTE` (per-item, pick the better cue) | **`0.4811`** = the channel EXACTLY | **routing cannot help** -- the prior is wrong on `100%` of these items, so there is nothing to route TO |
> | `ORACLE_BLEND`, monotone (prior weight `>= 0`) | `0.4748` | **no monotone blend has headroom** |
> | lambda sweep, best | `0.4245` | below the channel |
> | 🔓 **`SIGNED` oracle (prior weight free)** | **`0.7799`** | **headroom EXISTS -- but only via SUPPRESSION** |
>
> ➡️ **SO MY FRAMING WAS WRONG AT THE ORACLE LEVEL, NOT MERELY UNBUILT.** *I asked for
> reliability-weighted combination. A PERFECT reliability weighter, given the answers, cannot beat
> the channel here.* **The only mechanism with room is a NEGATIVE prior weight -- suppressing the
> dominant sense (reordered-access, Duffy/Rayner 1988), which is a different organ entirely.**
>
> ## 🔻 **AND IT KILLED THE CRUX I EXPLICITLY NAMED**
> My brief said the prior's error might be *"PREDICTABLE from a property we can compute (how peaked
> the sense-frequency distribution is). Untested. It is the crux."* **Measured: `AUC(peakedness ->
> prior-wrong) = 0.4033` -- BELOW chance.** *My proposed predictor is worse than useless.* **And no
> other gold-blind detector fires either** (`channel-disfavours-MFS -> subordinate` `AUC 0.5114`;
> `channel-confidence -> channel-right` `0.5396`). 🔑 **Its info-free twin detector scores `0.6572`
> on subordinate -- HIGHER than the real one, so the detector carries no signal at all.**
>
> ## 🧠 **THE MECHANISTIC FINDING I HAD MISSED, AND IT EXPLAINS THE WHOLE FAILURE**
> **`95.65%` of the channel's wrong picks on subordinate items are HIGHER-FREQUENCY than the truth.**
> *The channel fails in the SAME DIRECTION as the prior.* ➡️ **That is CORRELATED ERROR -- precisely
> the regime the landed `exp_attention_salience_reliability_gate_correlated_error_v1` HARD_FAIL says
> INVERTS reliability weighting (`auc 0.3198`, below chance).** **The brief listed that as the
> suspected regime; this confirms it with a direct count rather than an analogy.**
>
> ## ⚖️ **WHAT IT HONESTLY DID NOT ACHIEVE, AND SAYS SO**
> The suppression mechanism WORKS on subordinate (`b=-1.5`: `0.7673` vs channel `0.4811`,
> `+0.2862` CI `[+0.1761,+0.4025]`) **and CRASHES the dominant population** (`0.3103` vs prior
> `0.5855`, `-0.2752` CI `[-0.3385,-0.2137]`). **A pure population trade-off, so the bar's
> do-no-harm clause is not met and it reports REFUTED rather than claiming the win.** *Even a
> split-KNOWING best-case gate reaches only `0.5252` sub / `0.4026` dom.*
> ✅ *And the channel's own signal is confirmed real: info-free twin `0.2979` vs `0.4811`.*
>
> 🎯 **THE REDIRECT: the missing organ is a SUBORDINATE-CONTEXT DETECTOR -- something that recognises
> "this context calls for the rare sense" -- and it is bottlenecked on channel quality.** *Which is
> the same missing piece three other instruments found, arriving on a fourth and sharper: not "weight
> your sources", but "notice when the common answer is the wrong one".*


> # 🥈 **PRIORITY 2 — A MEASURED FAILURE OF *COMBINATION*, WITH A LANDED RECIPE AND TWO LANDED TRAPS ALREADY ON DISK.**
> **This is not "go build reliability weighting."** That mechanism has a **HARD_PASS** and two
> **HARD_FAIL**s in this repo already, and they tell you the exact conditions under which it works.
> **Your job is to determine whether our case is the passing regime or the failing one — and if it
> is the failing one, to solve the underlying problem some other way.**

# PROBLEM: A STRONG PRIOR SWAMPS A WEAKER-BUT-CORRECT CHANNEL, AND OUR MIXING RULE CANNOT EXPRESS "TRUST THIS ONE LESS HERE"

**slug:** `the_prior_swamps_the_channel_instead_of_combining_with_it` · **opened:** 2026-08-23 by the
strategy session · **status:** OPEN

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

When our reader decides which meaning of a word is intended, it has two sources of evidence:

- **how common each meaning is** — a very strong general-purpose guess;
- **what the word feels like** — the grounded sensory/motor channel.

We combine them at **fixed weights**. The result is that the common-meaning guess wins essentially
everywhere, including the cases where it is **guaranteed wrong**.

Measured, on the one population where the question is live (words whose intended meaning is *not*
the most common one — 53 words, subject-weighted, chance = `0.3854`):

| arm | score | |
|---|---|---|
| **the grounded channel ALONE** | **`0.4811`** | ✅ above chance |
| the channel **combined with** the common-meaning prior | `0.1415` | 🔻 far below chance |
| the prior alone | `0.0000` | *zero by construction — it cannot pick a rare meaning* |

**Combining a working cue with a confident-but-wrong one makes the answer worse than either the
working cue alone or random guessing.** That is a defect in the *combination*, not in either cue.

---

## 2. WHY THIS ONE

- 🔑 **IT IS A MISDIAGNOSIS WAITING TO HAPPEN.** The submission that produced this data concluded
  *"the grounded channel adds nothing"*. **"The channel is useless" and "our mixing rule destroys
  the channel" predict the SAME aggregate score and imply OPPOSITE next steps.** One says delete the
  channel; the other says fix the rule.
- **IT GENERALISES PAST THIS ORGAN.** Any place we fuse a strong statistical prior with a weaker
  structured signal has this shape.
- 🧠 **THE BRAIN HAS A PINNED ANSWER AND WE ARE NOT USING IT** (§4).

---

## 3. MEASURED vs INFERRED

### MEASURED — you may build on these

| what | number | where |
|---|---|---|
| channel alone, subordinate senses | `0.4811` (chance `0.3854`) | `data/exp_reader_sense_selection_bayesian_hub_v1/_scored_population.json`, 53 words |
| channel **+** prior, same items | `0.1415` | same |
| prior alone, same items | `0.0000` **by construction** | same |
| the aggregate that hid it | `84%` of trials (`708`/`841`) are items the prior cannot lose on | same |
| **reliability gating WORKS on an independent channel** | `mean_delta_hard_unrel = +0.0634`, shuffled controls all `<= 0.0`, do-no-harm `+0.0130` | `exp_attention_salience_reliability_gate_independent_channel_v1` **HARD_PASS** |
| 🔻 **it is INERT when the reliability estimate is DERIVED** | deltas `-0.0280` / `-0.0720` — **and the derived signal had `auc = 0.8303`** | `exp_attention_salience_reliability_gate_derived_v1` **HARD_FAIL_INERT_OR_HARMFUL** |
| 🔻 **it INVERTS under correlated/systematic error** | `auc_unrel = 0.3198` (**below chance**), delta `-0.1018` | `exp_attention_salience_reliability_gate_correlated_error_v1` **HARD_FAIL_CORRELATED_ERROR_FOOLS_CHANNEL** |
| 🔻 joint reliability weighting was REDUNDANT on a strong base | three cells, all HARD_FAIL | `exp_multipred_argstruct_*reliability*_v1` (2026-07-23) |

### INFERRED — overturning any of this is a RESULT

- 🔻 **That our case is the *failing* regime.** The prior's error here is **perfectly systematic**:
  it is wrong on 100% of subordinate items, by construction. That resembles the
  correlated/systematic condition that produced `auc 0.3198` more than the independent condition
  that produced the HARD_PASS. **But it differs in one way that may matter: our systematic error is
  PREDICTABLE from a property we can compute (how peaked the sense-frequency distribution is).**
  *Untested. It is the crux.*
- 🔻 That `0.4811` on 53 words would survive at scale, or on words the norms do not cover.
  **Coverage is not random — this is NOT evidence the channel works where it cannot score.**
- 🔻 That fixing the combination reaches the aggregate metric at all: `84%` of it is dominated by
  items the prior already wins.

---

## 4. HOW THE BRAIN DOES THIS — **AND WHERE IT IS PINNED vs OUR INVENTION**

**PINNED BY EVIDENCE.** Reliability-weighted cue combination is one of the better-measured
computations in neuroscience: when the nervous system combines two noisy estimates of the same
quantity, it weights each **in inverse proportion to its variance**, and the combined estimate is
measurably more precise than either alone (Ernst & Banks 2002 for visual-haptic; the same form
recurs across multisensory integration). **The key property is that the weights are DYNAMIC —
per-stimulus, per-context — not fixed constants.**

**Our current rule is a fixed-weight sum. It structurally cannot express "trust the prior less on
this item", which is exactly the operation required.** *Copy the COMPUTATION (variance-weighted
combination); SWEEP any PARAMETER (how variance is estimated, the window it is estimated over) —
those derive from constraints we do not share.*

**OUR INVENTION, LABEL IT AS SUCH.** Whatever proxy you choose for "reliability" of the grounded
channel or of the prior is **ours, under test** — the brain's variance estimate is not available to
us. **Say which proxy you used and why, and do not present it as the brain's.**

⚠️ **AND THE PRIOR WORK ABOVE CONSTRAINS THIS HARD:** a reliability signal that is **derived from
the same evidence it gates was INERT even at `auc 0.8303`**. **A reliability estimate that merely
*predicts* errors is not the same thing as one that *improves* decisions** — that is this repo's
standing rule that a statistic the mechanism optimises may DIAGNOSE but never DECIDE, and it has
already cost one HARD_FAIL here. **Estimate reliability from something independent, and prove the
independence.**

---

## 5. THE BAR

**ON THE SUBORDINATE-SENSE POPULATION, A COMBINED ARM MUST BEAT *BOTH* SINGLE CUES, CI-SEPARATED,
WITHOUT LOSING ON THE DOMINANT POPULATION.**

1. **Beat the grounded channel alone** (`0.4811`) on subordinate items — *this is the hard half; the
   trivial "solution" of down-weighting the prior to zero just recovers the channel and is NOT a
   pass.*
2. **Do no harm on dominant items**, where the prior currently scores `0.5508`. A combination that
   wins the rare cases by wrecking the common ones is not a win — report both.
3. **Floors recomputed on each population**, chance on the items actually scored, CI half-widths and
   null p95 reported beside every margin.
4. **An info-free twin of your reliability signal must LOSE.** Given the derived-signal HARD_FAIL,
   also report the AUC of your reliability estimate *and* its gate delta **separately** — a good AUC
   with a bad delta is the documented failure mode, not a partial success.
5. **Report coverage.** The channel scores only `53` of `77` subordinate words.

**REFUTING THIS IS A FULL RESULT — AND THEN KEEP GOING.** If reliability weighting turns out to sit
in the correlated-error regime and cannot work here, **that is worth knowing and you have earned the
right to solve the underlying problem another way**: the underlying problem is *"a confident cue
that is systematically wrong on an identifiable subpopulation destroys a weaker correct cue."*
Routing/gating by that subpopulation, learning when to abstain, or a representation that keeps the
two cues separable are all fair game. **Come back with "refuted" alone only if you have also
established that no route you could test solves the underlying problem, and say which you tried.**

---

## 6. ALREADY TRIED — DO NOT REDO

**FIVE LANDED CELLS ALREADY TESTED THIS MECHANISM. Re-running any of them as-is adds nothing;
what is missing is whether OUR case is the passing or the failing regime.**

- ✅ **`exp_attention_salience_reliability_gate_v1` — HARD_PASS.** A reliability gate works in
  principle here.
- ✅ **`exp_attention_salience_reliability_gate_independent_channel_v1` — HARD_PASS.** *This is the
  recipe:* reliability estimated at **source level, leave-one-item-out**, `auc_unrel 0.6764`,
  `mean_delta_hard_unrel +0.0634`, positive on 5/5 seeds, **shuffled control all `<= 0.0`**, and
  do-no-harm on the reliable subset (`+0.0130`). **Copy this estimation design.**
- 🔻 **`exp_attention_salience_reliability_gate_derived_v1` — HARD_FAIL_INERT_OR_HARMFUL.** A
  reliability signal DERIVED from the same evidence it gates: `auc 0.8303` — **highly diagnostic** —
  and gate deltas `-0.0280` / `-0.0720`. **Do not build a derived estimator and do not report AUC as
  if it were the result.**
- 🔻 **`exp_attention_salience_reliability_gate_correlated_error_v1` — HARD_FAIL_CORRELATED_ERROR_
  FOOLS_CHANNEL.** Under shared systematic errors the channel does not merely fail, it **inverts**:
  `auc 0.3198` (below chance), delta `-0.1018`, and incorrect answers scored *higher* than correct
  ones (`0.7013` vs `0.6688`). ⚠️ **This is the regime our case most resembles.**
- 🔻 **`exp_multipred_argstruct_jointreliability_positional_v1`, `..._measuredreliability_joint_v1`,
  `..._earlyjoint_relweighted_v1` — all HARD_FAIL** (`KNOWLEDGE_STILL_REDUNDANT_ON_STRONG_BASE` /
  `EARLY_STILL_REDUNDANT`). *Joint reliability weighting added nothing over a strong base.*
- ✅ `exp_attention_salience_common_mode_detector_v1` — **HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES.**
  *There is already a built detector for the shared-error case that breaks the mechanism.* **Query
  it before building a new one.**

**ALSO ALREADY DONE ON THE CHANNEL ITSELF, from `reader_meaning_channel`:** the channel **cannot
gate links alone** (`66%` hit / `37%` false alarm, AUC `0.7002`); **sparsity does not rescue
bundling**; **an addressed slot does not either**. *Combine, do not substitute — and do not spend a
week re-deriving those.*

---

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| **the population every §1 number comes from** | `data/exp_reader_sense_selection_bayesian_hub_v1/_scored_population.json` (`841` rows, per-item `correct` per arm, `k`, `dominant_congruent`) |
| the cell that produced it | `experiments/exp_reader_sense_selection_bayesian_hub_v1.py` |
| **my re-analysis, reproduces §1 from that file** | `verification/test_the_prior_swamps_the_grounded_channel_not_replaces_it.py` |
| the reviewed submission | `notes/problems/reader_meaning_channel/SOLVED.md` + the review block atop its `PROBLEM.md` |
| **the landed recipe to copy** | `data/exp_attention_salience_reliability_gate_independent_channel_v1/metrics.json` |
| **the two landed traps** | `data/exp_attention_salience_reliability_gate_derived_v1/`, `..._correlated_error_v1/` |
| the grounded channel itself | `hdlab/grounded_semantics.py` (`grounded_vector`, `grounded_similarity`) — **READ ONLY; do not write `hdlab/`** |
| the sense-frequency prior | built inside the cell above; it is not a separate organ |

**WHAT YOU MAY WRITE:** `experiments/`, `verification/`, and this problem folder. **NOT** `hdlab/`,
**NOT** `preregs/**`, **NOT** any `arm_key*` file. `data/foundation/` is READ-ONLY.

---

## 8. DO NOT QUOTE

- 🚫 **`A5_STRINGCTRL` / `A6_TRIGRAM_ONLY` `0.0870` as "what a spell-checker scores".** ~`78%` of it
  is morphological leakage in the WordNet gold; it is under board question **Q117**. **It is not the
  floor for this problem anyway** — different task, different population. **Recompute your own.**
- 🚫 **`BAYES_HUB 0.0827` as evidence that "coherence helps where the prior fails".** That arm is
  **five times below chance** on that stratum. The submission's own witness makes this error; the
  arm that supports the claim is `COH_HUB`.
- 🚫 **Any number from the `841`-trial aggregate as though it described the subordinate cases.**
  `84%` of it is items the prior cannot lose on. **Numbers do not cross populations.**
- 🚫 **`COH_HUB 0.4811` as "the channel works".** It is `53` words, no CI, and measured only where
  the norms cover the word. **Coverage is not random.**
- 🚫 **My own framing in §4 as settled.** *"The prior swamps the channel" is MY reading of someone
  else's data.* **If the disk disagrees with this brief, the disk wins and you say so.**

---

## 9. VERIFY BEFORE YOU START — THE DISK OUTRANKS THIS BRIEF

1. `python tools/before_you_start.py "combine two cues weighted by reliability"` — **read every row**.
2. `python tools/experiment_index.py query "reliability"` — **24 cells, 23 landed. Read them all;
   five are directly about this mechanism and two are HARD_FAILs.**
3. `python tools/organ_map_cite.py A6_TRIGRAM_ONLY` — the spelling floor is under correction.
4. `.venv/Scripts/python.exe verification/test_the_prior_swamps_the_grounded_channel_not_replaces_it.py`
   — reproduces every number in §1 from the saved population.

⚠️ **THE FLOOR SITUATION IS UNSETTLED.** `A5_STRINGCTRL` / `A6_TRIGRAM_ONLY` `0.0870` is under
board question **Q117** — roughly `78%` of it is morphological leakage. **It is not the floor for
THIS problem** (different task and population), but do not import it as a bar. **Recompute your own.**

🚫 **DO NOT** raise `GROUNDED_CAP`. **DO NOT** edit `preregs/**` or any `arm_key*` file. **DO NOT**
write `hdlab/` — prove it in `experiments/` and `verification/`, then say what would change and why.
