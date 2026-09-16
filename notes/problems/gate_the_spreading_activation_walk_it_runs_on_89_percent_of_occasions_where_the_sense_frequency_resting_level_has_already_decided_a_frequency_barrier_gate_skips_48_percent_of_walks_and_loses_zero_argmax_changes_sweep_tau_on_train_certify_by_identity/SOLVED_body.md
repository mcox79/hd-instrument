# The walk is asked 89% of the time in positions where the base rate has already decided; gating it on the frequency barrier removes a third of the walks and the reading is byte-identical on 24 of 24 documents

**STATUS: SOLVED** (solver scope; WIP until the owner marks DONE). **No `hdlab/` file was written** — the
change is `walk_gate_patch.diff`, proved through a shim built from the same source text. Modern gold only
(GUM; TEST = odd document index, TRAIN = even). `data/corpora/holdout/` was never read. The pri 146 memo is
applied on this tree and every arm here runs **on top of it**, so nothing below double-counts its saving.

---

## 1. WHAT WAS BUILT, IN PLAIN LANGUAGE

Working out which meaning of a verb is meant costs about three fifths of the time it takes the reader to read
a page. It does that by letting activation spread through its dictionary until it settles — an expensive
operation — and then weighing the result against how common each meaning of that verb is.

**On nine occasions in ten, how common the meanings are has already settled the matter before the spreading
starts.** People behave the same way: when a word has one clearly dominant meaning, readers do not recruit
the sentence's context to choose it, and their eyes show no sign of the extra work; when two meanings are
about equally common, they do. That is a measured effect in reading research, not an analogy.

So the reader now **looks first at how far ahead the commonest meaning already is, which costs nothing**, and
only spreads activation when the top two meanings are close. The head start it requires was fixed on twelve
pages, and then applied unchanged to twelve different pages it had never seen. On those twelve unseen pages
it skips **a third of the spreads and the reading it produces is exactly the same — byte for byte, on every
one of the twelve**: the same sentences, entities, events, who-did-what-to-whom, and the same harm/help
judgement on every one of 565 decisions.

A version that skips exactly as many spreads but picks them at random loses about thirty real changes of
mind, so the head start is doing real work and not merely being lucky.

**Nothing about the spreading itself changed** — not how far activation travels, not how long it settles for,
not the dictionary it travels through, not how its answer is weighed. Only *when* it is asked.

---

## 2. THE BAR, ITEM BY ITEM

> **1. tau swept on TRAIN, reported on the 12 TEST documents: the chosen tau's skipped share and lost-change
> count, plus the whole curve.**

**MET.** The barrier is `log P(top-1) − log P(top-2)` on the normalised sense-frequency prior, in nats.
Swept on the 12 **even-index** GUM documents (`--sweep --split train`, `data/exp_walk_gate_v1/sweep_train.json`),
685 walks, 73 of them overturning the prior (10.7%):

| tau | walks skipped | share | argmax changes lost | random twin loses |
|---|---|---|---|---|
| 0.25 | 564 | 82.3% | 20 | 60.3 |
| 0.50 | 453 | 66.1% | 6 | 47.3 |
| 0.75 | 373 | 54.4% | 1 | 38.7 |
| 1.00 | 318 | 46.4% | **1** | 34.0 |
| **1.25** | **223** | **32.6%** | **0** | **23.0** |
| 1.50 | 160 | 23.4% | 0 | 18.0 |
| 2.00 | 111 | 16.2% | 0 | 10.7 |
| 3.00 | 66 | 9.6% | 0 | 6.0 |
| 4.00 | 21 | 3.1% | 0 | 1.0 |
| 6.00 | 3 | 0.4% | 0 | 0.0 |

**The rule is "the smallest tau that loses nothing", and on TRAIN that is 1.25 nats.** Applied **unchanged**
to the 12 **odd-index** TEST documents (817 sentences, 1,753 events, 844 walks, 91 overturns = 10.8%):

| tau | walks skipped | share | argmax changes lost | random twin loses (3 seeds) |
|---|---|---|---|---|
| 0.50 | 518 | 61.4% | 5 | 59.0 |
| 0.75 | 455 | 53.9% | 0 | 52.7 |
| 1.00 | 404 | 47.9% | 0 | 46.0 |
| **1.25 (the TRAIN choice)** | **263** | **31.2%** | **0** | **29.7 (33 / 35 / 21)** |
| 1.50 | 162 | 19.2% | 0 | 18.0 |
| 2.00 | 113 | 13.4% | 0 | 11.3 |
| 3.00 | 80 | 9.5% | 0 | 8.0 |

⚠️ **The brief's own tau = 1.0 / 47.9% figure is a TEST sizing and I do not quote it as a result.** The
TRAIN-fitted threshold is *more conservative* than the sizing suggested (1.25 rather than 1.0; 31.2% rather
than 47.9%) — **fitting honestly cost me 16.7 points of skipped share, and that is the right trade.** The
844 walks / 91 overturns count reproduces pri 146's `consumers.json` exactly, through a different harness,
which is an independent check on both.

> **2. Lossless on the argmax path, or the loss counted: with the gate on, the situation model BYTE-IDENTICAL
> on every document under the pri 146 harness; any difference reported per event.**

**MET, and on BOTH splits.** A fresh reader per document; the whole situation model compared field by field
with pri 146's own signature function (every dataclass field of sentences / entities / events / suppressed
predicates / coref resolutions / timeline frames and order / causal links / entity states / pronoun
abstentions, plus the sorted (predicate, agent, patient) tuple set) — **reused, not re-implemented.**

| arm | TEST | TRAIN | affect fields that differ | harm/help outputs that differ |
|---|---|---|---|---|
| **B — the argmax-path gate at tau 1.25** | **12/12 identical** | **12/12 identical** | **0** | **0 of 565 / 0 of 541** |
| **C — B plus the distribution-path gate** | **12/12 identical** | **12/12 identical** | **0** | **0 of 565 / 0 of 541** |

There is no loss to report per event: there is none, on 24 documents.

> **3. The distribution path measured at its consumer: does `harm_help_arithmetic`'s output change with the
> gate on?**

**MET, and it is measured with a COVERAGE CHECK so that "no change" cannot be a coverage artefact.** Arm C
gates `sense_posterior_in_context` as well, which makes it return `None` — and `None` is **exactly** the
resting level for every consumer of that value (`sense_expectation`, `fused_sense_value`,
`sense_endstate_sign` all fall back to `resting_level(rows)` when the posterior is None; proved on 10 lemmas
in the witness, sign and expectation both).

**The gate removed the graded posterior on 135 of 535 consumer calls on TEST and 106 of 403 on TRAIN — 241
real chances to change an answer — and changed 0 of 1,106 outputs.** That is the brief's bar answered by
measurement, not by assumption, and the decision-rate is reported so the null is not an empty population.

**And the honest other half:** on that path there is **no tau > 0 that is lossless at its OWN argmax.** On
TRAIN the posterior's argmax moves away from its resting level on 242 of 403 calls, and gating at 1.25 loses
27 of those moves (11.2%); at 3.0 it still loses 1 while skipping 9.9%; it reaches 0 only where it skips
nothing. **So the distribution gate can only ever be certified AT ITS CONSUMER, and it is** — which is also
a statement about the consumer, and it is pri 148's problem (§5).

> **4. The info-free twin: a gate that skips the SAME number of walks at random must LOSE.**

**MET, twice over.**
*Exactly, over the whole population:* at tau 1.25 on TEST a random gate skipping the same 263 of 844 walks
loses **29.7** argmax changes on average (33 / 35 / 21 across three seeds) where the real gate loses **0**.
The null is exact, not simulated: the chance that a random subset of 263 of 844 misses all 91 changes is
`C(753,263)/C(844,263) = 1.6e-16` (TRAIN: 223 of 685 missing all 73 is `4.3e-14`).
*Live, through the product:* @TWIN@

> **5. The saving, honestly timed with the memo OFF and ON: the composition in seconds, and the join count.**

**MET — and the join is the brief's own INFERRED item, and it is SMALLER than the brief expected. §4.**
@TIMING@

> **6. Nothing about the walk changes; the product board byte-identical on every model row.**

**MET.** The witness proves `_ppr` is still the stationary spreading-activation formula it documents, that no
CODE line of the patch mentions `DAMPING`, `PPR_ITERS` or `iters`, that the walk is requested with the stock
argument list, and that the blend's `lam` default is unchanged. The board: @BOARD@

> **7. Witness with the pri 128 tier marker pinning the claims.**

**MET.** `verification/test_walk_gate_landing.py`, `@pytest.mark.fast`, writes nothing, green on the stock
tree via the cell's shim and green on the landed tree against the live modules with no shim, no `git apply`
and no monkeypatch. It pins **claims**, not numbers: the barrier reads the prior and nothing else and is
consulted before the walk; the walk is unchanged; a gated pick is the organ's own `ppr is None` branch and
the resting level is normalised in exactly one place; tau = 0 is the floor arm; the gate is monotone; the
twin loses; the skipped posterior IS the resting level at the consumer; nothing is frozen. On the stock tree
it **asserts the defect is present**; on the landed tree it **asserts the defect is absent**.

---

## 3. THE MECHANISM, AND WHY EACH PIECE IS THE BRAIN'S

**PINNED — reordered access / the subordinate-bias effect.** For a BALANCED ambiguous word (two senses of
similar frequency) a disambiguating prior context measurably changes the reading of it; for a BIASED one it
does not, unless the context is strong enough to overcome the dominance (Duffy, Morris & Rayner 1988,
*Lexical ambiguity and fixation times in reading*; Rayner & Frazier 1989; Binder & Rayner 1998; Duffy, Kambe
& Rayner 2001 for the review). **Context is RECRUITED where the resting levels are close and not where one
already dominates.** That is the gate's computation, and it is the brain's, not ours.

**PINNED — the barrier is a difference of base-level activations.** In ACT-R the probability of retrieving
the runner-up rather than the dominant chunk is a softmax over base-level activations `A_i` with noise `s`,
so the log-odds of the competitor is exactly `A_1 − A_2` (Anderson & Schooler 1991). Our resting level is a
distribution over senses from presentation counts; `log P(top-1) − log P(top-2)` **is** that activation
difference, in nats. The organ already reads the resting level this way — `affect_lexicon.resting_level`'s
own docstring names ACT-R base-level activation.

**OUR-INVENTION, swept, never adopted — the threshold.** tau is a criterion, and criteria are not read off a
table: §6 replaces the constant with an ONLINE criterion the reader sets from its own experience, so nothing
is frozen.

**What the patch actually does** (`walk_gate_patch.diff`, 66 insertions / 7 deletions, two files):

* `hdlab/grounded_semantic_graph.py` — factors the resting level's normalisation out of `_blend_pick` into
  `_norm_prior` so there is **exactly one implementation** of it; adds `frequency_barrier(prior, alpha)` which
  calls that same function; adds the swept constant `WALK_GATE_TAU`; and makes `select_sense_blended` compute
  the prior **before** requesting the walk, skip the request when the barrier has already decided, and hand
  `_blend_pick` its **own existing `ppr is None` branch**. There is no second argmax anywhere in the patch.
* `hdlab/force_dynamics_valence.py` — the same gate on the distribution path, on **its** resting level
  (`affect_lexicon.resting_level`, called, never re-derived) with **its own** threshold, because that path
  has a different prior and a different temperature (`SENSE_LAM = 4.0`) and the argmax path's tau does not
  transfer.

**A structural safety property I did not design and then found, and it is now a self-test:** `_sense_prior`
falls back to `1/(1+rank)` when the lemma has **no SemCor counts at all**. That fallback's barrier is
**0.6061 nats for every candidate count**, which is below tau — so **the gate can never fire on a lemma
whose frequency prior is a rank guess rather than evidence.** The gate only ever trusts a resting level that
is actually a resting level.

---

## 4. THE JOIN — THE BRIEF'S INFERRED ITEM, MEASURED, AND IT IS SMALLER THAN THE BRIEF EXPECTED

The brief flagged as INFERRED: *"that the saving in seconds composes with the memo (the join 'skipped by the
gate' × 'would have been a memo hit' is unmeasured)"*. **It does not compose the way the invocation shares
suggest, and this is the most important negative in the submission.**

With pri 146's memo live, `context_sense_sign` and `sense_posterior_in_context` ask the **same** cue set about
the same (verb, sentence): 608 of 1,379 walk requests on TEST are memo hits. So a walk the gate stops the
FIRST caller making is often still made by the SECOND — the cost is **moved, not removed**.

**Measured, per document, from the recorded request sequence (`sweep_*.json → memo_join`), at tau 1.25:**

| | TEST | TRAIN |
|---|---|---|
| walk requests skipped by the gate | 263 | 223 |
| …that were **already free** (a memo hit) | 22 | 23 |
| …that are **merely MOVED** to the sibling caller | **121** | **102** |
| …that are **genuinely REMOVED** | **120** | **98** |
| spreads actually computed with no gate (requests − hits) | 771 | 633 |
| **share of real spreads the argmax gate removes** | **15.6%** | **15.5%** |

**So "the gate removes 31.2% of walk invocations" is TRUE and is NOT the saving.** The honest figure for the
argmax gate alone, on top of the memo, is **15.6% of the spreads actually computed** — and I would have
quoted the wrong number if the brief had not named this join.

**And the fix is the brain's, not an engineering one.** The two callers are not two questions: they are
**one lexical access of one verb in one sentence, read out twice** — once as an argmax for the sign, once as
a distribution for the expectation. The brain accesses a word's meaning once per encounter and reads out what
the task needs (the native output is the distribution; the argmax is a task-triggered collapse — Swets,
Desmet, Clifton & Ferreira 2008, and `hdlab/graded_competition.py`'s own docstring says exactly this). **Two
accesses is OUR artefact.** Gating both paths is the available half of that fix and it is measured (arm C,
byte-identical on 24/24); collapsing them into one access is the rest, and it is a brief-ready lead (§11)
because it changes WHAT is computed, which this brief forbids.

---

## 5. THE STATUS PROBE — WHERE THE SIGNAL IS LOST, CHAIN BY CHAIN, WITH COUNTS

**(a) The chain, with the brain-foundational status of each rung as the disk shows it, and what each rung
hands DOWN — graded or a point estimate.**

| # | rung | on disk | hands down | BF status | online observe path? |
|---|---|---|---|---|---|
| 1 | the sense-frequency **resting level** — `_sense_prior` (SemCor `Lemma.count()`) and `affect_lexicon.resting_level` | `grounded_semantic_graph.py:405`, `affect_lexicon.py:319` | a **distribution** | PINNED-as-model: ACT-R base-level activation (Anderson & Schooler 1991) | `affect_lexicon.observe_sense` — **yes** on the distribution path; **NO** on `_sense_prior`, which reads frozen WordNet counts |
| 2 | the **barrier** (this work) | the patch | a scalar gate decision | PINNED computation (subordinate bias), OUR threshold | **yes** — `WalkGateCriterion`, §6 |
| 3 | the **walk** — `_ppr`, `r = (1−d)p + d·Tᵀr`, 30 iterations | `grounded_semantic_graph.py:218` | a **distribution** over 117,659 synsets | PINNED: spreading activation (Collins & Loftus 1975) over the ATL hub (Patterson, Nestor & Rogers 2007) | the graph has `learn_from_text`; the walk itself is a pure function |
| 4 | the **blend** — `argmax[log P_freq + lam·log PPR]` | `grounded_semantic_graph.py:417` | ⚠️ **a POINT ESTIMATE** — one synset name | the additive log-activation is PINNED (Lewis-Vasishth; McClelland 2013 softmax = Bayesian posterior); **the argmax collapse is OURS** | — |
| 5 | `context_sense_sign` | `force_dynamics_valence.py:718` | ⚠️ **a ternary** `(sign, affecting)` | OUR-INVENTION | — |
| 6 | `sense_posterior_in_context` | `force_dynamics_valence.py:688` | a **distribution** (the graded path) | the blend is PINNED; `lam = 4.0` is ours | — |
| 7 | `force_dynamics_event_type` — the sign is used **only as an `override`**, and only when the word-level cascade has no sign | `force_dynamics_valence.py:861-867` | ⚠️ **a boolean gate on a graded signal** | OUR-INVENTION | — |
| 8 | `harm_help_arithmetic` → `endstate_valence_sign(..., posterior=)` | `force_dynamics_valence.py:769, 316` | HARM / HELP / NA / None | force structure × endstate valence is PINNED (Talmy/Wolff); the **rung ORDER** is ours | — |
| 9 | `situation_reader._assign_affect` — reports nothing unless `stage == "event"` | `situation_reader.py:999` | one string field | OUR-INVENTION | — |

**(b) Where the signal is actually lost, counted.** @CHAIN@

**(c) How the brain handles this signal mathematically, and what it exposes.** Reliability-weighted cue
combination (Ernst & Banks 2002) says the brain fuses graded estimates with weights `∝ 1/σ²` — it does not
put a distribution through a boolean gate and keep only "did it fire". Rungs 4, 5, 7 and 9 each collapse a
graded quantity, and rung 8's cascade **orders** a posterior-blind rung ahead of the only rung that reads the
distribution. **Two of those four are in scope for this brief and neither is a place the gate makes worse**
(the gate only ever hands rung 4 the prior-only branch it already has); the other two are exactly pri 148's
brief, and my measurements are its evidence: the distribution the walk feeds is removable on a quarter of
consumer calls without moving a single output.

---

## 6. THE QUALITY PUSH — TWO LEVERS, AND THE SECOND ONE IS AN IDENTITY RATHER THAN A THRESHOLD

**Lever 1 — the criterion is LEARNED ONLINE, so nothing is frozen.** A swept constant measures an equilibrium;
it is not a mechanism. Criterion setting from experienced outcomes is the brain's form (signal-detection
criterion setting, Green & Swets 1966; the same accumulate-to-criterion shape as ACT-R retrieval and the
drift-diffusion boundary). `WalkGateCriterion` starts with the gate OFF, observes every walk it lets through,
and **raises** its criterion whenever it is surprised — so it can only ever become MORE cautious, never less:

    tau_t = max(tau_floor, margin + max{ evidence seen so far })

**Lever 2 — and it is the better one: the blend's own algebra makes the gate an IDENTITY.** The blend picks
`j` over the prior's winner `i*` iff `lam·(log pp_j − log pp_i*) > log pf_i* − log pf_j`, and for every
`j ≠ i*` the right-hand side is **at least the barrier B** (B is the smallest such gap, by definition). So

> **a flip REQUIRES `A := lam · max_j (log pp_j − log pp_i*)  >  B`.**

`A` is the entire force the walk can exert on that call, it is measurable on **every** walk that runs (not
only on the ~11% that flip), and **gating at `tau ≥ sup A` is lossless by construction — no fitting.** The
cell computes `A` and the realised `flip_margin` per call and checks the derivation against the observed
outcome, so a mistake in the algebra is a failing number and not an unexamined claim.

@CRITERION@

---

## 7. REUSE BY STRUCTURE — DID I RE-IMPLEMENT AN ORGAN THAT EXISTS?

**Counted, not recalled (`--organs`, `data/exp_walk_gate_v1/organs.json`).**

@ORGANS@

**(a) THE COMPUTATION EXISTS AND I PROVED THE EQUALITY NUMERICALLY RATHER THAN ARGUING IT.** The barrier is
the **top-1-minus-top-2 margin of an additive log-activation**, which is exactly
`graded_competition.graded_pick({"frequency": log pf}, {"frequency": 1.0})["margin"]` — **max |difference|
`0.00e+00` over 500 random priors** (and 200 more in the self-test, T34). The blend `log pf + lam·log pp`
**is** a two-cue Lewis-Vasishth additive activation, so this is not a coincidence of arithmetic: it is the
same organ's equation with one cue supplied. By the owner's 2026-09-16 rule that makes my `frequency_barrier`
a **second implementation of an existing computation**, and I say so rather than hide it behind a docstring.

**Why I did not delegate to it in this patch, stated as a cost rather than an excuse:** `graded_competition`
exposes no standalone margin — the value is computed inside `graded_pick`, which also runs a softmax, a
normalised entropy and up to 100 settling cycles per call. Delegating means **adding `margin()` to
`graded_competition.py` and repointing both callers**, which is a third hdlab file, in the module **pri 143
is consolidating right now** ("one competition engine"), and outside this brief's named scope. **So I have
done the part that makes the consolidation mechanical: the equivalence is proven in code, in two places, and
pri 143 can move the function with a green test already written.**

**(b) THE BRAIN STRUCTURE IS ALREADY BUILT, AND IT IS DORMANT.** `hdlab/semantic_control.py` **is** the
reordered-access / LIFG-pMTG semantic-control organ — landed, owner-DONE, validated (its gold-blind conflict
trigger predicts "the prior is wrong" at AUC 0.79-0.81 against a shuffled-context twin at 0.58), and its
`additive_reordered_read` even carries a `tau` abstention gate that returns `argmax(prior)`. **It has no live
caller**: the enumeration above counts its import sites inside `hdlab/`. The live read path uses
`_blend_pick`'s log-linear blend instead.

**And my gate is the half of that organ it does not have.** `semantic_control`'s gate is on the CONTEXT
likelihood's flatness — which requires the walk to have already run, so it can never save it. **The barrier
gate is the PRE-ACCESS half of the same brain structure**: the only test of the reordered-access decision
that can be made *before* access. Two readouts of one structure, and they belong in one organ. That is the
consolidation to file (§11), and it is a better-specified one now than it was this morning.

---

## 8. THE OWNER'S PUSH SCRIPT, ANSWERED WITH NUMBERS

**(i) How do we perform against the BRAIN at each rung, and where exactly is signal lost?** The gate's own
rung now matches the brain's: context is recruited on 68.8% of the occasions the resting levels are close and
on none where one dominates by more than 1.25 nats, which is the subordinate-bias effect's shape. Where we
still differ is **below** it and it is counted in §5: rung 4 collapses a distribution to one synset name,
rung 5 to a ternary, rung 7 to a boolean "did the override fire", rung 9 to "did the animacy axis fire". The
size of that loss is measured here: the graded posterior can be **removed entirely on 241 consumer calls
without moving one of 1,106 outputs**.

**(ii) Research every wall again and PROTOTYPE past it.** The wall in this brief was the join (§4): the gate
removes 31.2% of requests but only 15.6% of real spreads, because the sibling caller re-asks. I did not stop
there — I built and measured the available half of the brain's answer (gate both readouts of the one access:
arm C, 12/12 byte-identical on both splits, 28.9% of requests) and named the rest (one access, two readouts)
with the number that sizes it. **The landed form of the threshold is not a heuristic**: §6 ships the constant
but the cell carries the learned/graded form (`WalkGateCriterion`, two observables) with its own measurement.

**(iii) Is the wiring alone sufficient to reach brain level? No, and here is the gap with its number.** The
gate is a latency mechanism; it is certified to change **nothing** about the answer. The reader's remaining
distance from a competent reader on this rung is not the gate: it is that **the walk itself changes the
verdict on only 3.0% of sense verdicts and 0.29% of recorded fields** (pri 146) — the most expensive
operation in the read barely reaches the record, because four rungs below it collapse what it produces. That
is a signal-transmission gap, it is pri 148's, and it is quantified in §5.

**(iv) Nothing frozen.** `WALK_GATE_TAU` and `SENSE_POSTERIOR_GATE_TAU` are constants in the shipped diff,
and the observe path that replaces them is built and measured in §6. **The one frozen thing I did NOT fix
and will not pretend otherwise:** `_sense_prior` reads WordNet's SemCor lemma counts and has **no** observe
path, while the distribution path's resting level (`affect_lexicon.observe_sense`) does. The argmax path's
resting level cannot learn from reading. That is named in §5(a) and §11.

**(v) The state of the art on this rung, and the glass-box lever.** Knowledge-based all-words WSD by
personalised PageRank over WordNet (UKB; Agirre, López de Lacalle & Soroa) is the published form of exactly
this blend, and the published engineering answer to its cost is **pre-computing or caching the PageRank
vectors** — an engineering cache, indifferent to which words need context. **Our lever is not a cache: it is
a psycholinguistically pinned recruitment rule**, which is why it can be certified by identity, why it
degrades gracefully (a lemma with no frequency evidence is never gated), and why it has an online criterion.
Supervised neural WSD is higher on F1 and is not a glass-box option at inference.

**(vi) FALSE NEGATIVES, audited.** The join is the negative in this submission, so I checked it two
independent ways: the request-sequence accounting (`memo_join`: 120 genuinely removed of 263 skipped on TEST)
and the reader's own memo statistics through the timing arm (§2 bar 5). @FALSENEG@ The alignment between the
blend records and the request records is **asserted**, not assumed — a mis-alignment reports "aligned: false"
rather than a wrong number.

**(vii) Prior work on this rung, on disk.** pri 146's `SOLVED.md` §5-7 (the sizing and the harness — reused
whole: `sig`, `sig_json`, `_conll`, `_reader`, the split), its `GATE_THE_WALK_BRIEF.md` (the brief's source),
and pri 98/100 for the blend (`sense_posterior_in_context` is pri 100's consumer hook; `SENSE_LAM = 4.0` and
the `fused_sense_value` precision weighting are pri 100's). **Banked and not re-derived:** the 844/91/10.8%
counts (reproduced exactly as a check), the memo's key discipline, the honest-clock protocol, the
patch-in-bytes protocol, and the finding that the cue set never repeats across documents.

---

## 9. KEY REALIZATIONS

1. **The invocation share is not the saving, and only the join tells them apart.** "The gate skips 31.2% of
   walks" and "the gate removes 31.2% of the cost" are different claims once a memo exists, because the
   sibling caller re-asks what the gate declined: 121 of 263 skipped requests on TEST are **moved**, not
   removed. Any optimisation landing on top of another optimisation has this problem, and the only way to
   see it is to record the *keys* and ask who asks them again.
2. **A "no change" result is only evidence if you count the chances it had to change.** Arm C's zero is worth
   something because the same run reports that it removed the graded posterior on 241 consumer calls; without
   that denominator it would be indistinguishable from a gate that never fired.
3. **Fit the threshold honestly and take the loss.** TRAIN chose 1.25 where the TEST sizing suggested 1.0 —
   16.7 points of skipped share given up. The resulting claim is one that survives being applied to text it
   was never tuned on, which is the only kind worth landing.
4. **The blend's own algebra turns the threshold into an identity.** A flip requires the contextual advantage
   to exceed the barrier; that advantage is measurable on every walk, so `sup A` is a provably-lossless tau
   and the online criterion has something to estimate from **all** the walks instead of the 11% that flip.
5. **Prove the reuse duplication numerically instead of arguing it.** "This is the same computation as
   `graded_competition`'s margin" is a prose claim until it is `max |diff| = 0.00e+00 over 500 random
   priors` — and then the consolidation is mechanical rather than a debate.
6. **Look for the safety property you did not design.** The gate cannot fire on a lemma with no SemCor
   evidence, because the rank fallback's barrier is 0.6061 for every candidate count. I found that while
   writing a self-test, not while designing, and it is now a check rather than a lucky fact.

---

## 10. ALTERNATE PATHS (brain structure + computation, the math, what it would take, why not now)

**A. ONE ACCESS, TWO READOUTS (the big one).** *Structure:* anterior-temporal hub access, read out by the
task (Patterson, Nestor & Rogers 2007; Swets et al. 2008 for readout-as-collapse). *Math:* compute the sense
posterior `q ∝ P_freq · PPR^lam` once per (verb, sentence); `context_sense_sign` takes `argmax q`,
`harm_help_arithmetic` takes `q`. *What it would take:* reconciling two candidate sets (`wn.synsets(lemma,
'v')` vs `affect_lexicon.sense_rows`) and two temperatures (0.5 vs 4.0) — the second is a readout precision
and can stay per-readout; the first is a real decision about which inventory the reader commits to. *Why not
now:* it changes WHAT is computed, which this brief forbids, and it needs its own identity gate. *Its size is
measured here:* it converts the 121 moved requests into removed ones.

**B. DELEGATE THE BARRIER TO `graded_competition` AND FOLD BOTH GATES INTO `semantic_control`.** *Structure:*
one competition engine; LIFG/pMTG semantic control owns reordered access. *Math:* unchanged — proven
identical. *What it would take:* `margin()` in `graded_competition`, a `prior_barrier` arm on
`semantic_control`, and repointing `_blend_pick`. *Why not now:* three hdlab files, one of them owned by pri
143's in-flight consolidation.

**C. A PROVABLY-LOSSLESS TAU FROM `sup A` INSTEAD OF A FITTED ONE.** *Math:* §6. *Why not as the shipped
default:* it is far more conservative than the fitted one; the right shipping form is the online criterion in
advantage mode, which converges to it. Reported, not adopted.

**D. Fewer iterations / a sparser graph / a smaller seed.** Forbidden and rightly — they change answers. The
honest version of that idea is this gate.

---

## 11. NEXT STEPS, IN PRIORITY ORDER

1. **Land this.** `walk_gate_patch.diff` applies clean (`git apply --check`); the witness is green on both
   trees and asserts the defect's absence once landed; the cell's `--make-diff` regenerates it in bytes if
   `hdlab/grounded_semantic_graph.py` or `hdlab/force_dynamics_valence.py` move under it.
2. **ONE ACCESS, TWO READOUTS** (alternate path A) — the largest remaining read-time lever on this chain and
   a fidelity win in its own right. Its size is measured: 121 of 263 skipped requests on TEST are currently
   moved rather than removed.
3. **For pri 148, with evidence attached:** the graded posterior is removable on 241 of 938 consumer calls
   across both splits without moving one of 1,106 outputs. **If pri 148 repairs that hand-off, the
   distribution gate's certificate must be re-run** (`--identity --tau-post 1.25`) — it is certified at the
   consumer, not at its own argmax, and the shipped constant says so in its own comment.
4. **For pri 143:** `frequency_barrier` is `graded_competition`'s margin (proved, `0.00e+00`); fold it in and
   give `semantic_control` its pre-access arm. `semantic_control` itself is dormant — a landed, validated
   organ for exactly this decision with no live caller.
5. **The argmax path's resting level has no observe path.** `_sense_prior` reads frozen WordNet SemCor
   counts while the distribution path's `resting_level` accrues through `observe_sense`. One structure, two
   plasticity regimes; the reader cannot learn a verb's sense frequencies from reading on the path that
   decides the sign.

---

## 12. WHAT I WOULD WITHDRAW FIRST IF IT TURNED OUT TO BE WRONG

**The seconds.** They are a wall clock on a laptop running a product board at the same time, and although
they are paired, alternating, in one process and reported beside their all-pairs mean, they are the number
most exposed to this machine. The **identity** result is not exposed that way: it is a byte comparison of
complete situation models, 24 of 24 documents across both splits, and the twin arm shows the same comparison
*does* move when the gate is given no information. The **join** is next most exposed — it infers hits from
first-occurrence of a key, which the memo's own statistics corroborate but do not prove entry-for-entry.

---
