---
problem: store_survives_a_partial_cue
status: REFUTED
bar: "BEAT F_COUNT1 = 0.3242 ON HELD-OUT TEXT, CI-SEPARATED, ON THE LIVE READING PATH." -- the floor is the strongest one actually run, gated on its UPPER bound (0.3366); the information-free twin must LOSE; report exact-key and held-out side by side; report tie density.
result: NO arm beats the floor. Strongest brain-faithful store arm CONF_GATED (confidence-gated dual-process) = 0.2461 hit@1, CI [0.2348, 0.2576]; every other store arm lower (calibrated familiarity NB_LOGODDS 0.0022 / NB_MULT 0.0486, explicit recollection REC_EXPLICIT 0.1619, linear CLS FAM_REC 0.2066). Scorer = lemma-weighted hit@1, one held-out query per lemma, n = 5,490 anchor lemmas, live reading path (context_vector_masked cues, 80/20 profile/held-out split).
floor: F_COUNT1 (first-order PPMI co-occurrence counting) = 0.3242, CI [0.3115, 0.3366] -- REPRODUCED EXACTLY from the refuted cell, so the instrument matches. Gate on the upper bound 0.3366. Also measured: an ORACLE_UNION ceiling (an oracle picking the right arm per item) = 0.4082, +0.0840 CI [+0.0769, +0.0914] above the floor.
controls: INFO_FREE_NB (familiarity profiles randomly re-assigned to lemma identities, shape kept) = 0.0000 held-out -- EXCLUDES that the machinery rather than the lemma-context content carries the score. SCRAMBLE-CONTENT (cue taken from a deranged donor lemma, gold stays L) = 0.0002 (NB) / 0.0000 (FAM_REC) -- EXCLUDES that the read-out ignores cue content (collapses to chance 1/5490 = 0.00018). SELF-RETRIEVAL 2AFC positive control = 0.9767 (>= 0.70) -- EXCLUDES void plumbing. EXACT-KEY regime beside held-out: REC_EXPLICIT recites 0.9122 but recognises 0.1619 -- the recite/recognise gap reproduced in the best explicit store. Tie density reported per arm/regime.
files_changed: experiments/exp_recognition_store_calibrated_familiarity_recollection_v1.py, experiments/exp_flat_vs_addressed_identity_recovery_livepath_v1.py (imported unchanged), verification/test_recognition_store_calibrated_familiarity_recollection.py, notes/problems/store_survives_a_partial_cue/SOLVED.md
reverify: .venv/Scripts/python.exe verification/test_recognition_store_calibrated_familiarity_recollection.py
---

# OUR STORE CAN RECITE BUT NOT RECOGNISE -- REFUTED AS A STORE-FORMAT PROBLEM

**Plain-language TLDR.** Our memory answers almost perfectly when you ask it with the exact words it
stored, but falls apart when you ask with only *some* of those words -- which is all real reading
ever gives. The brief asked: design a better *store* that survives the partial words. I built the
strongest brain-faithful stores I could and **none of them beats plain word-counting**. The reason
turns out to matter: **plain word-counting, done the way we do it, already IS the brain's own
"this feels familiar" signal** -- there is no better version of it to build. So a better store is
not the fix. But the story is not "the words just don't carry enough information", because a cheat
that always picks the best of three methods per word *does* beat counting by a clear margin. The
missing piece is not more information and not a better store -- it is a **decision-maker that knows
*when* to trust the specific-memory method over the familiarity method.** We don't have that
decision-maker, and nothing I could build *without* training one closed the gap.

## What I built (brain foundation stated as PINNED vs OUR-INVENTION)

The task is the refuted cell's exact live-path instrument -- open-vocabulary **identity recovery**:
mask a word, hand the read-out the bag of remaining content words from one held-out sentence, and
ask it to pick the masked word out of all 5,490 candidates. I imported the refuted cell's store and
representation verbatim, so **F_COUNT1 reproduces at 0.3242 by construction** (the reverify).

Recognition memory in the brain is **dual-process** (Yonelinas; Diana/Yonelinas/Ranganath):
a graded **cortical familiarity** signal plus episodic **hippocampal recollection**. I gave the
store the strongest brain-faithful version of each, on the identical instrument:

- **Calibrated cortical familiarity as a posterior** (predictive-coding view: cortex computes a
  calibrated posterior, not a raw tally). `NB_LOGODDS` (Bernoulli log-odds) and `NB_MULT`
  (multinomial likelihood). *Both collapse* (0.0022 / 0.0486). The reason is the finding:
  **PMI = log[P(w|L)/P(w)] already IS the calibrated familiarity weight** -- it subtracts the corpus
  baseline `log P(w)`, which is exactly the informativeness weighting the posterior needs. The NB
  variants that *drop* that baseline term (log-odds has baseline 0.5; multinomial has none) lose
  precisely because they drop it. So `F_COUNT1` is not a naive counter to be beaten -- it is the
  brain-faithful familiarity read-out, and no first-order weight beats it.
- **Hippocampal recollection in the explicit / segregated format** the strategy session's own result
  pins (segregation beats superposition at equal budget). `REC_EXPLICIT` keeps every episode as its
  explicit content-word set and scores idf-weighted max overlap -- the high-fidelity counterpart of
  the *dense, lossy* addressed store that already failed. It **recites at 0.9122 exact-key but
  recognises at only 0.1619 held-out**: the recite/recognise collapse reproduces even in the *best*
  explicit episodic store, which is the cleanest statement that the gap is not a format artifact.
- **CLS dual-process combination**, both **linear** (`FAM_REC` = z(familiarity)+z(recollection) =
  0.2066) and **selective / confidence-gated** (`CONF_GATED` = recruit recollection only where
  familiarity is low-confidence, the actual dual-process control = 0.2461). Both below the floor.

**OUR-INVENTION-UNDER-TEST (labelled, not hidden):** that a naive-Bayes posterior is the right
functional form here (it is not -- PMI already is); that the confidence gate's peakedness signal
predicts when recollection is right (it does not, unsupervised). **PINNED:** dual-process
architecture, segregation of the representation, the uniform prior (the test set is balanced -- one
query per lemma -- so a training-frequency prior would be *miscalibrated*, the opposite of the WSD
reader task; stated so it is not read as an oversight).

## What I measured -- the decisive numbers

| arm (held-out hit@1, n=5,490) | value | vs floor |
|---|---|---|
| **F_COUNT1 -- the floor (PMI familiarity), reproduced** | **0.3242** [0.3115, 0.3366] | -- |
| NB_LOGODDS (Bernoulli posterior) | 0.0022 | far below |
| NB_MULT (multinomial likelihood) | 0.0486 | far below |
| REC_EXPLICIT (explicit hippocampal recollection) | 0.1619 | below |
| FAM_REC (linear CLS dual-process) | 0.2066 | below |
| **CONF_GATED (selective dual-process control -- best store arm)** | **0.2461** [0.2348, 0.2576] | **below** |
| INFO_FREE_NB (control) | 0.0000 | must-lose satisfied |
| SCRAMBLE-content (control) | 0.0000 / 0.0002 | at chance |
| **ORACLE_UNION (fam OR rec OR mult, per item) -- the ceiling** | **0.4082** | **+0.0840 CI [+0.077, +0.091]** |

Exact-key beside held-out: F_COUNT1 0.4106, REC_EXPLICIT 0.9122, FAM_REC 0.5310. Self-retrieval 2AFC
0.9767. All controls bind; the info-free twin reads 0.0000 as the previous solver's did.

## Why this is REFUTED and not PARTIAL

The bar was **not met by any arm** -- the best brain-faithful store (0.2461) does not merely fail to
CI-clear the floor, it is *below* the floor point estimate. There is no partial progress toward the
bar to report. What there IS: a clean demonstration that the **premise is the wrong one**. The
premise (inherited from the refuted `flat_store` brief) is "the store FORMAT loses the information,
so a better-format store will survive the partial cue." That is false three ways over now:
superposition, addressing, and -- here -- calibrated familiarity, explicit recollection, and both
CLS combiners. **A better store format is not the lever.** Showing a problem is the wrong problem is
the first-class REFUTED the brief asks for.

## What I did NOT establish (the honest boundary, and where I differ from the disk's first read)

**I did NOT show the collapse is a pure information cap.** My own ORACLE_UNION refutes the strongest
"it's forced" reading: an oracle that picks the right method per item reaches **0.4082, +0.084
CI-separated above the floor**. So ~8 held-out points carry *genuinely complementary episodic
signal* -- recollection is right on a real subset where familiarity fails. The information to beat
counting **is in the store.** What is missing is a **control** that knows *when* to trust
recollection: the best *unsupervised* gate I built (CONF_GATED) deploys recollection at the wrong
moments and lands *below* the floor. I did not build a *learned* gate, so I have **not** shown the
reserve is unreachable -- only that no unfitted read-out reaches it. This is the same shape as the
`reader_meaning_channel` finding: the gap is a missing **control network**, not missing information
and not a bad store.

## What would have to change in hdlab/ (a proposed change, not a landed one -- Q111)

**Do NOT swap the store format.** The incumbent flat sum in `reading_grounding_loop`
(`_sums[lemma] += ctx_vec`) should not be replaced by any dense/addressed/superposed store to fix
recognition -- none beats counting. If a recognition read-out is wired at all, it should compute the
**explicit PMI familiarity** (what `F_COUNT1` is), which is the best single read-out. The real
missing organ is a **recollection-gating control** (a learned "when to recollect" decision over
familiarity-confidence + recollection-confidence + cue-length features), plus an explicit episodic
recollection store (slot D2 `ca3_completer` is NEEDS_ADAPTER, but the completion regime the brief
notes never occurs; `REC_EXPLICIT` here is the better-suited explicit recollector). This is a
control organ, not a store swap.

## What I would withdraw first if it turned out to be wrong

The claim most exposed is **"PMI is the ceiling of first-order familiarity."** It rests on the NB
variants losing; a cleverer calibrated estimator I did not try could in principle edge F_COUNT1
(though the oracle-union says the real headroom is in recollection, not in a better familiarity
weight). Second most exposed: **the ORACLE_UNION as evidence of *reachable* signal** -- it is an
upper bound a real combiner cannot attain, so "a learned control could beat the floor" is a
hypothesis the union makes plausible, not a result. I withdraw the familiarity-ceiling claim before
the missing-control diagnosis.

## QUESTIONS

None. The instrument reproduced the floor exactly, controls bind, and the verdict is unambiguous
against the bar.

## NEXT STEPS

1. **The store direction is closed.** Do not open a fourth store-format brief; the format is not the
   lever (superposition, addressing, familiarity, recollection all measured losing).
2. **Open a CONTROL brief, not a store brief:** a *learned* recollection-gating control, tested for
   no-leak (train the gate on the profile split or the exact-key regime, apply to held-out; the
   info-free twin must still lose). The bar it must clear is the same 0.3366; its ceiling is the
   0.4082 oracle union. If it clears, the recite/recognise gap is a solved control problem; if it
   does not even with a learned gate, the reserve is genuinely unreachable and the info-cap reading
   becomes airtight.
3. This converges with `reader_meaning_channel`: two independent problems now point at the same
   missing piece -- a control network that decides *when* to use the second channel/store -- which is
   worth more as a shared redirect than either finding alone.
