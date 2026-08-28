---
problem: aimed_reading_is_built_and_the_reader_never_calls_it
status: REFUTED
bar: "AIMED READING MUST BEAT THE FIXED SCHEDULE, NOT ONLY RANDOM -- ON THE LIVE PATH, WITH THE REGISTER BIAS CONTROLLED." (a live call site; beat FROZEN CI-separated on held-out coverage; control the register bias and report the probe's register composition per arm; save the scored population; an information-free twin must LOSE)
result: register-controlled held-out coverage (3000-word probe, 2335 reachable / 665 unreachable by FROZEN's own corpora, equal-weighted; grounded-subject coverage; 10,000 sentences/arm; substrate seed 20260814). FROZEN 0.0510; FORAGE surprise 0.0407 (FORAGE-FROZEN CI [-0.0188,-0.0018]); FORAGE_LP learning-progress-target 0.0254 (CI [-0.0340,-0.0170]); FORAGE_LPFULL full-learning-progress 0.0206 (CI [-0.0382,-0.0223]). No aimed variant beats the fixed schedule; all three CI-separated BELOW it.
floor: strongest floor = FROZEN, the incumbent fixed 4-corpus schedule, register-controlled coverage 0.0510 (upper bound cleared by no aimed arm). Info-free twins: RANDOM (uniform random corpus choice) 0.0240; FORAGE_RANDTARGET (random target) 0.0256.
controls: (1) REGISTER bias controlled by stratifying the probe on FROZEN reachability and equal-weighting the two strata -- removes the 80/20 over-representation of FROZEN's register; FROZEN still wins in BOTH strata. (2) INFO-FREE CORPUS twin RANDOM -- v1 FORAGE beats it (+0.017 CI-sep) but v3 FORAGE_LPFULL ties it (the info-free twin does NOT lose for the LP arms). (3) INFO-FREE TARGET twin FORAGE_RANDTARGET -- FORAGE_LP ties it (delta -0.0002, CI includes 0), proving the learning-progress signal carries NO information for corpus choice. (4) RAW micro coverage reproduces the prior FROZEN-wins-raw register artifact. (5) FRESH-SEED replication (2 fresh seeds, folding in the reconstructed original seed for 3 total) confirms the ordering is seed-robust: REPLICATED (tools/replication_gate.py) -- the shipped forager (frequency/surprise) loses to FROZEN on 3/3 seeds, effects [-0.0103, -0.0331, -0.0277] at seeds [20260814, 20260901, 20260902], same sign 3/3, magnitude stable within 3.2x, no info-free control reproduced half the effect (exp_aimed_reading_seed_replication_v4, data/.../metrics_frequency.json). [Separate later finding, NOT part of this REFUTED forager verdict: a DIFFERENT reader -- v6 comprehensible/learnable-input -- BEATS FROZEN on register-controlled coverage on 3/3 seeds, effects [+0.0405, +0.0397, +0.0286], twin loses; a genuine replicated coverage win with a non-forager chooser, recorded in FORWARD_WORK.md. It does not satisfy the brief's literal bar, which is about wiring the FORAGER.] (6) scored population saved for every arm.
files_changed: experiments/exp_aimed_reading_register_controlled_v1.py, experiments/exp_aimed_reading_learning_progress_v2.py, experiments/exp_aimed_reading_lp_currency_v3.py, experiments/exp_aimed_reading_seed_replication_v4.py, verification/test_aimed_reading_register_controlled.py, verification/test_aimed_reading_learning_progress.py, notes/problems/aimed_reading_is_built_and_the_reader_never_calls_it/SOLVED.md
reverify: D:/AI/hd-instrument/.venv/Scripts/python.exe verification/test_aimed_reading_learning_progress.py
---

# REFUTED: aiming beats reading-at-random, but does NOT beat a good fixed curriculum -- and the real bottleneck is grounding DEPTH, not source choice.

## What was asked
The organ that chooses what to read next (`hdlab/information_foraging.py`, Charnov's marginal-value
theorem) is built, pinned and witnessed, but the reading loop never calls it. The one run that had
tested it reported HARD_PASS while actually LOSING to the fixed 4-corpus schedule on held-out
coverage (0.0617 vs 0.0743) -- under a 7.6x register bias nobody had separated. The bar this brief
set: does aimed reading beat the fixed schedule on held-out coverage once the register bias is
controlled, on a live call site, with an information-free twin losing.

## What I built and measured
A principled family of aimed readers, each one variable different from the last, scored on the same
register-controlled instrument against the same fixed-schedule floor and info-free twins. Every arm
saves its scored population.

| arm | what changed | grounded | register-controlled coverage |
|---|---|---|---|
| FROZEN | fixed 4-corpus schedule (incumbent) | 696 | **0.0510** |
| FORAGE (v1) | surprise currency + frequency target (the shipped organ) | 604 | 0.0407 |
| FORAGE_LP (v2) | learning-progress TARGET (rising trace-coherence) | 323 | 0.0254 |
| FORAGE_LPFULL (v3) | learning-progress CURRENCY (leave) + LP target | 353 | 0.0206 |
| RANDOM | info-free uniform corpus choice | 262 | 0.0240 |
| FORAGE_RANDTARGET | surprise currency + random target | 250 | 0.0256 |

**The register bias is real but is NOT the cause of the loss.** The base_vocab 1001-4000 probe is 80%
reachable inside FROZEN's own 4 corpora (`scratch/probe_register_diag.py`); controlling for it
(equal-weighting FROZEN-reachable vs FROZEN-unreachable words) still leaves FROZEN ahead in BOTH
strata. FROZEN's news + graded-biology curriculum simply grounds more general vocabulary; surprise-
driven foraging is dragged into dense biology jargon the general-vocab probe cannot score.

**The information-free controls did the decisive work.**
- FORAGE (surprise) beats info-free RANDOM (+0.017, CI-separated) -- so aiming beats reading at
  random. It just loses to the fixed schedule.
- FORAGE_LP TIES the random-target twin (delta -0.0002, CI [-0.007, +0.007]). The learning-progress
  signal carries NO information for what to read: choosing targets by it is no better than choosing
  them at random. The trace-coherence-derivative proxy is too noisy at the few-traces-per-concept
  scale to discriminate. (LP fired 99% of the time -- it was genuinely LP-driven, not a fallback.)
- FORAGE_LPFULL (the fully learning-progress reader) is the WORST arm and ties info-free RANDOM --
  the more learning-progress machinery, the shallower the reading and the worse the coverage.

## The diagnosis (the finding that redirects the work)
The reader's bottleneck is GROUNDING DEPTH, not source choice. Grounding a word needs ~4 coherent
encounters of it. The fixed schedule wins by reading a few corpora deeply (2,500 sentences each) so
words repeat enough to ground. Every aimed reader spreads across many corpora (FORAGE_LPFULL read 26)
and grounds each word too few times -- it reads broadly but shallowly. On a general-vocabulary
coverage probe, breadth-of-source loses to depth-of-repetition, and the "smarter" the aiming, the
broader and shallower it gets. Aiming and depth are in tension on this task.

## The live call site (stated plainly, as the bar asks)
Today the reading loop does NOT call the organ to choose a corpus, in EITHER live reader:
- `hdlab/substrate.py::read()` builds the ForagingController (L599) and uses it for WHEN to leave
  (`should_leave()`), but opens corpora in a FIXED rotated alphabetical `order` (L584-636). The code
  says so at L592: *"the forager chooses WHEN to leave but not WHAT to open."*
- `experiments/exp_reading_grounding_loop_cycle2_v1.py:132-137` hard-codes a 4-entry corpus dict.

`slot_status.py` calls H2 "FILLED" only because `substrate.py` CONSTRUCTS the controller; its
corpus-choice output is never consumed. My FORAGE arms ARE the loop calling the organ for the WHAT
(gap-ranked corpus choice over the real reading machinery), so the mechanism is demonstrated.

**Proposed hdlab change (NOT landed; the strategy session lands it -- board Q111):** in
`substrate.read()`, at each patch boundary choose `name` via the organ's gap-ranked corpus choice
over the live corpora (`reg.handles` + `peek` + `rank_material`) instead of taking the next entry of
the rotated `order` (~10 lines; the ranker and controller already exist). Keep the pinned Charnov
leave rule exactly. **IMPORTANT CAVEAT from this brief's own measurements: wiring this in is
correct-to-do but is NOT the win it was assumed to be -- it does not improve general-vocabulary
coverage, because the bottleneck (depth) is upstream of source choice.** Do not wire it expecting a
coverage gain.

## What is PINNED vs OURS
- PINNED: Charnov 1976 MVT leave rule (kept exactly); learning progress = g'(t) as the normative
  information-seeking currency (Oudeyer & Kaplan 2007 -- named in the organ's own docstring).
- OURS-UNDER-TEST (and shown wanting): the trace-coherence-derivative proxy for learning progress,
  the per-step error-drop currency, the spoke of what counts as a "patch"/"yield". The refutation is
  of THESE operationalizations on THIS probe -- not of learning progress in principle.

## What I did NOT establish / would withdraw first
- Coverage measures general-vocabulary BREADTH only. It does NOT measure depth of meaning or
  downstream COMPREHENSION, where aimed reading's value may actually live. A win for the fixed
  schedule here is a fact about vocabulary breadth, not about understanding. This is the single
  biggest caveat: aimed reading may be being judged by the wrong yardstick.
- The register control is a 0.5/0.5 reweighting choice; the full stratum breakdown is reported so a
  different weighting can be recomputed from the saved populations.
- The learning-progress refutation is specific to the cheap trace-coherence proxy; a
  prediction-error-derivative computed per concept with more traces could still carry signal.

## TLDR
The piece that decides what to read next is built but unplugged. I plugged it in (in experiments,
not the live substrate) and measured it honestly. Letting the system choose what to read does NOT
beat the old fixed reading list at learning everyday words -- not the version that chases surprising
text, and not the more brain-faithful version that reads toward what it is currently learning, which
actually did worse. A fairness check proved that "read what you're learning" signal was, at this
scale, no better than choosing at random. The real problem is not WHICH source to open: it is that a
chooser reads a little of everything and never reads any one thing enough times to actually learn it,
while the fixed list wins by reading a few things deeply. Aiming beats reading at random; it loses to
a good fixed curriculum, because this test rewards depth and aiming spreads thin.

## QUESTIONS
None.

## NEXT STEPS
1. **Fix DEPTH, not source choice.** Make the reader stay in a source until it grounds, or add
   spaced repetition of not-yet-grounded words (the spacing effect is itself well-pinned). This is
   the mechanism the evidence points at.
2. **Measure COMPREHENSION, not vocabulary coverage.** A general-vocab probe structurally favors a
   general-register fixed schedule. The decisive test of aimed reading is a downstream task, not word
   coverage.
3. **Only then wire the organ into `substrate.read()`.** The wiring is correct to do, but this
   brief's measurements say it will not move general-vocab coverage on its own -- so it should follow
   a depth fix and a comprehension metric, not precede them.

---

## INTEGRATED_BY_STRATEGY 2026-08-24

Re-verified `verification/test_aimed_reading_learning_progress.py`: WITNESS PASSED -- coverage table
(FROZEN 0.0510 > FORAGE 0.0407 > FORAGE_LP 0.0254 > RANDOM 0.0240), the 2335/665 register partition,
99.03% LP-firing, and all four checks' pass-flags reproduce independently from the saved populations.
Accepted **REFUTED**, rating **STRONG** (review at top of PROBLEM.md). No `hdlab/` change.

CLOSURE recorded -- do not re-open on coverage: aimed reading (surprise OR learning-progress currency)
beats reading-at-random but LOSES to the fixed 4-corpus schedule CI-separated on register-controlled
held-out coverage; the learning-progress signal is INERT (ties a random target). The bottleneck is
grounding DEPTH, not source choice.

DOCK from EXCELLENT: the `controls` field carries a literal `<FILL v4 verdict>` -- the fresh-seed
replication arm was never filled in.

REDIRECTED WORK (the gap this points at, NOT re-opening this brief): (1) a DEPTH fix
(stay-until-grounded / spaced repetition, both pinned); (2) a COMPREHENSION metric rather than
vocabulary coverage. Wiring `information_foraging` into `substrate.read()` is correct-to-do but must
FOLLOW those two -- the same "wire an organ into the read loop only after the upstream fix" caution
that applies to today's landed `distributional_meaning_channel` (batch-transductive) organ.
