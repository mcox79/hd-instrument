# SUBSTRATE STRATEGY — how this thing gets better, and how we know

**LIVING DOCUMENT. Undated filename on purpose — edit it in place, don't fork a dated copy.**
Companion to `notes/ORGAN_MAP.md` (what we have, organ by organ). That doc is the SNAPSHOT.
This one is the PLAN: what must go up, what we build next, what we stop, and what runs when
nobody is driving.

---

## PART 0 — IN PLAIN LANGUAGE (read this even if you read nothing else)

**What we are building.** A machine that reads and understands, built out of parts that each do
what a specific piece of a brain does — using the brain's actual arithmetic, not something that
merely resembles it. Then, once a part matches the brain, and only then, we allow ourselves to
make it better than the brain.

**Where we actually are.** We have 38 identified organs. **Five** of them do the brain's arithmetic.
**Thirteen** do roughly the right operation but measure the wrong thing. **Seven** are missing
outright. **Sixteen have never been tested against anything they could have failed** — those are
UNTESTED, which is not the same as working, and this document refuses to call them working.

**The one number that gates everything — and it now HAS A FLOOR (2026-08-14).** When our reader
reads text and tries to name what a word means, it gets it right **4.80%** of the time, against a
**0.80%** floor from a scrambled version of itself. That is **six times its floor**, so it is real
and not luck — and it is still **half** of the **10%** we require before growing the knowledge
base. Adding more of a thing that is 95% empty just makes a bigger empty thing.

**The "two thirds are tautologies" claim was WRONG, and this is good news.** It said the machine
mostly writes down "a dog is a dog." It was a **bug in how the answer was looked up**: the word's
own entry was left in the list of possible answers, so of course it picked itself, every time. With
that entry excluded — which is what the live reader actually does — it writes **zero** tautologies.
So of the two conditions on the gate, the tautology one now **passes**; only quality fails.

**What is actually broken, stated precisely (2026-08-14).** Every answer it gets RIGHT is a
**sister** of the target: axon→dendrite, artery→vessel, anaphase→telophase, atrium→ventricle. It
finds the right *neighbourhood* and cannot pick the right *member*. That is not a supply problem
and not a retrieval problem — retrieval scores 0.786 when asked for something it definitely knows.
It is a **separation** problem.

**The trap we already fell into.** Six separate ideas for fixing this were tried and all six failed
*cleanly* — meaning we know they're dead, which is worth something. More facts: no. Better text:
no. More coverage: no. Cleverer weighting: no. Removing the shared component every vector carries
(step 3): no. Un-doing the coarse read-out to recover the brain's forgetting curve (step 2): the
curve was never lost. The problem is not supply, and it is not the two most obvious geometry fixes.

**The honest good news.** The machine is not failing at everything. On coreference — working out
who "he" refers to — we score **0.7193** against trivial baselines of 0.5614 and 0.3860. This
document previously said we were LOSING there. **That was wrong**, and it was wrong because someone
compared a score from one experiment against baselines from a different experiment. Fixed today.

**The discipline that makes this document worth trusting.** Every number below has a floor (the
score you'd get from a stupid method, so you know whether ours is doing anything) and a commit
hash (so you can check it). Where we don't have a floor, it says **NO FLOOR** in capitals. Where
the science doesn't actually pin an answer, it says **UNPINNED** — and that is a fact about
neuroscience, not a gap for us to fill with a guess.

**What to do if you are a cold session with no context.** Read PART 1 (the scoreboard). Pick the
highest step in PART 2 that isn't done. Check PART 3 first to make sure it isn't something we
already killed. That's it.

---

## PART 1 — THE SCOREBOARD

The smallest set of numbers that genuinely tracks "is the substrate getting better." If a number
is not on this list, moving it does not count as progress.

Four CAPABILITY numbers. Three HYGIENE numbers. Nothing else is a headline.

### CAPABILITY

| # | number | now | floor(s) | last moved by | what would move it |
|---|---|---|---|---|---|
| **C1** | **Near-neighbour 2AFC, live reading path** | **0.6980** (was 0.6395) | scrambled-context **0.5095**, frequency **0.48025**, chance 0.50 | `38f7a0d5c` (graded comparator ON) | the PRICED capacity step `d=256→1024`, worth ~**+0.05**, HELD (step 4). ~~rank-1 common-mode removal~~ — TRIED, **no effect** (step 3, `34b94e8bc`) |
| **C2** | **Context-conditioned discrimination GAP** | **+0.1005** (0.6395 with context vs 0.5390 without) | scrambled-context **0.4975**, frequency 0.4800 | `exp_context_conditioned_near_neighbour_v1` | anything that makes the context port carry MORE than "some signal is present". The gap is real; its CONTENT is unproven |
| **C3** | **Reading-grounding read-out quality** | **hit@1 4.80%** open-vocabulary, n=4000, 5491 anchors; **tautology rate 0.0%** | **scramble 0.80%** — a REAL FLOOR, recorded 2026-08-14 (`204eba1a0`). Delta **+4.00pp**, CI [+3.30, +4.70] | `exp_grounding_readout_known_answer_v1` (STEP 1, REPORTED) | **separation between sister terms.** Supply, mass, coverage and reweighting are all separately closed |
| **C4** | **Coreference, identity-demanding accuracy** | **0.7193** (earned 0.6842) | recency **0.5614**, singleton **0.3860**, oracle ceiling **0.9298** | `exp_wire_coref_accumulate_situation_model_v1` | closing earned-vs-oracle (0.6842 → 0.9298). This is a WIDEN-THE-MARGIN target on a WORKING organ |

**C3 is the gate, and it is now HALF PASSED.** Revival criterion: **≥10% MEANINGFUL against a
recorded floor, tautologies <10%.** The **tautology clause PASSES** (0.0%, and the old 65.7% was an
eligibility bug — see PART 3 CORRECTIONS). The **quality clause FAILS by 5.2pp** (4.80% vs 10%).
While it fails, **KNOWLEDGE-BASE GROWTH STAYS PAUSED.** No new corpora ingested for the sake of
size. This is not caution, it is arithmetic: growth multiplies whatever the quality is.

**Two C3 numbers that are NOT the headline and must not be substituted for it.** On the *banked*
2026-08-12 facts (n=319) the read-out is **AT_FLOOR** — GOLD_HIT 2.51% vs scramble 1.25% and
popularity 0.94%, delta CI **[-0.31, +3.13]**, includes zero. And the 2-candidate forced choice is
**MIDDLE_BAND** — 0.5393 with the graded comparator ON, against scramble 0.4738 and frequency
0.4943. With the graded comparator **OFF** it is **0.4720, BELOW CHANCE**: the `38f7a0d5c` flip is
what puts this read-out above chance at all. Positive control SELF_RETRIEVAL **0.786** (floor 0.70)
— that is what licenses reading the nulls as MEANING failures rather than plumbing failures.

### HYGIENE (these are also progress, and they are cheap)

| # | number | now | target | why it's on the headline list |
|---|---|---|---|---|
| **H1** | PASS-flavoured verdicts with **NO FLOOR** | **134** | **0** | A PASS with no floor is not evidence. 134 of them is a standing lie in our own records |
| **H2** | **Biology share of vocabulary** | **63.9%** (54.6 → 63.2 → 63.9 across extractor generations) | **falling** | ⚠️ **ANTI-METRIC — must go DOWN.** Self-reinforcing: improving extraction WITHOUT fixing corpus selection amplifies the skew. Three generations of "improvement" made it worse. **The foraging organ diversifies SOURCES (16 banked-from vs 4; dominant-source-share drop 0.1585) but does NOT yet fix this** — its own dominant domain is `textbook_biology` at 0.6325, and its FROZEN control failed to reproduce the skew, so that cell is not evidence on H2 either way |
| **H3** | Modules on the live path | **44 of 155** | rising, honestly measured | Measured by RUNTIME, never grep. A capability not on the live path is an island, and islands don't count |

### Numbers that are NOT on the scoreboard, and why

- **Definitional extraction 94%** — real (47/50, `exp_definitional_predicate_v62`) but **NO FLOOR
  RECORDED**, so it cannot be a headline. Give it a floor and it can join. Also: it measures what a
  PARSER HANDS the substrate, not what the substrate recovers. **Never place it beside C3.**
- **The hand-scored 64%** — also real (32/50, v5 term-boundary fix, floor 8%), also measures
  parser-handed extraction. **4.80% / 64% / 94% are three different populations, not a
  contradiction.** Cross-scoring them is already logged as a repeated error. Do not repeat it.
- **The old "1-3% MEANINGFUL"** — superseded as the C3 headline by the floored 4.80% above. It came
  from a blind hand-score with **3 MEANINGFUL rows in 100**, i.e. underpowered by floor (STANDING
  DISCIPLINE 1). The two are not comparable: different population, different rubric, and only one
  of them has a floor. Cite 4.80% vs 0.80%.
- **The foraging arms that beat FORAGE** — FROZEN scores **0.0743** held-out coverage against
  FORAGE's 0.0617, and RANDOM scores **0.3864** WordNet agreement against FORAGE's 0.3511. Neither
  breaks the prereg (each check named its own comparator in advance) and neither is a headline, but
  quoting foraging's wins without them overstates the organ.
- **0.7495** — this is the **d=1024** arm, not the live path. Quoting it as shipped is quoting an
  unshipped capacity change. See C1's "priced" note.

---

## PART 2 — SEQUENCED BUILD ORDER

Per step: the organ, the specific fidelity fix, a test that can FAIL, its floor, and whether it can
run alongside others.

### STEP 1 — ✅ **REPORTED 2026-08-14.** `exp_grounding_readout_known_answer_v1`
- **Organ:** B1/B2 — what the context vector actually contains.
- **RESULT: C3 HAS A FLOOR.** Open-vocabulary hit@1 **4.80%** vs scramble **0.80%**, n=4000 over
  5491 anchors, delta **+4.00pp** CI [+3.30, +4.70]. Real, six times its floor, **half** the 10%
  revival gate. Banked-fact arm **AT_FLOOR**; 2AFC arm **MIDDLE_BAND** (0.5393 ON / 0.4720 OFF).
  Prereg `a334501d2`, degenerate-arm fix `1b2022522`, results `204eba1a0`.
- **HOW IT GOT DONE after three deaths:** the blind hand-score gate was replaced by a
  **KNOWN-ANSWER** gate (WordNet gold) with a scramble floor — a discriminator with range by
  construction, per STANDING DISCIPLINE 1. The prior three dispatches were gated on the hand-score
  and could not have resolved.
- **The correction it produced:** the **65.7% tautology rate was an ELIGIBILITY BUG**, not a meaning
  failure — see PART 3.
- **WHAT IT HANDS THE NEXT STEP:** every correct hit is a **SISTER term** (axon→dendrite,
  artery→vessel, anaphase→telophase). The read-out finds the neighbourhood and cannot pick the
  member. **Separation is the target**; supply, mass, coverage and reweighting are closed.
- ⚠️ **Do NOT re-run the F1+F3 stabilisation question off this.** Stability is not quality, and
  F1F3 scored no better than base here (banked-arm 1.98% vs 2.51%).

### STEP 2 — ✅ **CLOSED 2026-08-14, HYPOTHESIS REFUTED.** `exp_forgetting_kernel_signreadout_v1`
- **Organ:** D8-adjacent — forgetting kernel.
- **The hypothesis was:** `ConceptSpace.observe` accumulates unbounded, then `np.sign()`s it one
  line before use, **throwing the brain's `t^-1/2` kernel away**.
- **REFUTED.** graded slope **-0.2939** [-0.3527, -0.2443] vs binarised **-0.3261**
  [-0.3925, -0.2729] — **CIs overlap**, |dslope| never above 0.063 on any of four streams. Power
  law wins on all four (dAIC **+38 to +94**); exponential never competitive. **The `sign()` is not
  the cause and the kernel was never lost.** Prereg+cell `d0c5c906e`, results `41da8e454`.
- **WHY, derived before the run:** Benna-Fusi's bound destroys information at **WRITE** time, which
  is what costs an exponent. Our `sign()` is a **read-out quantiser on an unbounded stored sum**, so
  it costs a constant `sqrt(2/pi)` and no exponent.
- 🔴 **THE CONTROL FIRED, AND IT IS THE BIGGER FINDING.** Shuffling ingest order moves the slope by
  **<0.012**: the accumulator is order-invariant, so **that curve measures INTERFERENCE and
  DILUTION, not CONSOLIDATION.** Do not cite it as a consolidation result anywhere.
- **CONSEQUENCE for D8:** the cascade / Benna-Fusi organ is now ruled out **twice** — already
  PARKED-BY-SCALE (~1e6 synapses vs our d=256..4096) and now **unnecessary**, since the exponent it
  would have supplied is already present. See PART 3.

### STEP 3 — ✅ **CLOSED 2026-08-14, HARD_FAIL_NO_EFFECT.** `exp_rank1_common_mode_removal_v1`
- **Organ:** G3 (neuromodulatory gain). Prereg `32ca72e9c`, cell `917dad83f`, results `34b94e8bc`.
- **The operation WORKED and the task did not care.** Removal verified — shared-direction energy
  **0.1535 → 0.0270**, mean pairwise cosine **0.1427 → -0.0004**. Accuracy **0.6980 → 0.6985**,
  CI **[-0.0043, +0.0053]**, includes zero.
- 🔴 **THE CAN-FAIL CONTROL IS WHAT CLOSES IT:** removing a **RANDOM** rank-1 direction gives
  **+0.0005**, sd 0.0012 over K=20 draws — **identical to the treatment.** The declared reading of
  that outcome ("if random helps equally, the effect is not the common mode") applies. Sister-term
  errors unchanged (0.0220 → 0.0220, **zero converted**); literal mean subtraction HURTS (-0.0213).
- **CORRECTION IT PRODUCED: the 58% common-mode premise does not reproduce.** See PART 3.
- **Scope preserved:** full-covariance whitening stays **PARKED-BY-SAMPLE-SIZE** at `O(d²)` =
  65k-16M samples. This null does **not** close it in either direction.

### STEP 4 — **THE PRICED CAPACITY STEP.** `d = 256 → 1024`
- 🔒 **STATUS: HELD PENDING USER AUTHORISATION.** It rewrites **every persisted anchor store** (a
  migration) and **a concurrent session is live**. Both conditions must clear before it is queued.
- **Worth ~+0.05 on C1.** Recorded here as a PRICED STEP, **not as an achieved result.**
- **Measured:** QUANT `[0.6395, 0.7030, 0.7380]`, GRAD `[0.6980, 0.7495, 0.78225]` at d =
  256/1024/4096. Capacity is the LARGER lever and was deliberately not changed.
- **CAN-FAIL TEST:** C1 at d=1024 post-migration, against the d=256 number and the d=1024 scramble
  floor (0.49025).
- **ORDERING:** step 3 has CLOSED with no effect, so there is no confound left to wait on. The only
  remaining blockers are the two in STATUS above: **USER authorisation and the concurrent session.**
- ⚠️ **A landed VET already refuted the MECHANISM story here** — unmodified `sign()` at d=1024
  (0.7030) BEATS graded at d=256 (0.69975), and the graded-minus-sign delta decays with d
  (0.0602 → 0.047 → 0.041). **The capability stands; the explanation does not.** Do not sell this
  step as "the format fix scaling up."

### STEP 5 — **COREFERENCE: WIDEN THE MARGIN.** Organ E3
- **Reframed today.** This was a rescue target; it is not. We are **above** both trivial floors.
- **Fidelity fix:** competitive retrieval among ≥2 semantically plausible antecedents — never
  tested at scale. Reuse the existing Centering/Cb resolver (the brain reuses circuits; a parallel
  build is both non-faithful and an island).
- **CAN-FAIL TEST:** accuracy at n in the hundreds on real text with ≥2 plausible candidates.
- **FLOOR:** recency **0.5614**, singleton **0.3860**, oracle **0.9298** — all same-corpus,
  same-metric, same-run. **Only this pair may sit beside 0.7193.**
- **ORDERING:** **PARALLEL**, and **IN FLIGHT as of 2026-08-14** — an agent owns
  `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*`. Do not touch those paths.
- **Now the top UNBLOCKED build step**, since 1-3 have all reported and 4 is held.

### THE FORAGING ORGAN — landed and HARD_PASS, not on the scoreboard
`exp_information_foraging_reading_v1` (`3d4761f69`; organ `c97ecbef2`, registry WIRE `625751a8c`).
Marginal-value-theorem patch-leaving over a 28-corpus shelf. **D2 held-out coverage FORAGE 0.0617
vs RANDOM 0.0127** (+3.868 relative, the load-bearing test); **D3 WordNet agreement 0.3511 vs
FROZEN 0.2920**; D1 dominant-source-share drop 0.1585. **D4 FAILED: oracle ratio 0.5344** against
its 0.70-1.00 band — **the organ leaves patches too early**, which is the specific next fix if this
is worked on. It is not a scoreboard number because it moves *what gets read*, not what the read-out
recovers; **read PART 1's "arms that beat FORAGE" note before quoting it.**

### Below the line (real, sequenced, not top-5)
**D4 replay schedule** — needs a corpus stream to be testable at all, and needs the corrected
biology (see PART 4). **D7 successor representation** — MISSING, and it blocks the one normative
replay-selection candidate. **Verb organs** — the foundation is NOUN-ONLY (0 genuine verb
definitions in 2092 facts; all 5 extractor patterns are NP-headed). Syntactic bootstrapping is
blocked on this and is **not ready to build on**.

---

## PART 3 — KILL CRITERIA

A plan that never removes anything is a wish list.

### KILLED — DO NOT RE-QUEUE. Each was refuted cleanly; that is why they are cheap to leave dead.

| route | how it died | do not confuse with |
|---|---|---|
| **More facts** | shuffled **WRONG** definitions scored **IDENTICALLY** to correct ones, to 6 decimal places | — nothing. This is the cleanest negative we own |
| **Better text** | textbook **0%** vs news **4%** MEANINGFUL, matched-N | "textbooks are good sources" — they may be, for a different mechanism |
| **More coverage** | 2.9% → **35.0%** coverage, still at chance | coverage is not the bottleneck; do not buy more of it |
| **Distinctiveness weighting as log-IDF** | null in zero-noise **analytic** arms | ≠ all reweighting. STEP 3 is a DIFFERENT thing (right basis) |
| **Context-conditioned sense selection** | HARD_FAIL on both indexes, **below random floor** | — |
| **PBV (propose-before-verify)** | abandon-on-wrong **0.286** vs 0.60 needed; abandonment was arithmetic on encounter count, not correctness | — |
| **Rank-1 common-mode removal** (STEP 3) | removal VERIFIED (energy 0.1535→0.0270) and accuracy moved **+0.0005**, CI includes 0 — while a **RANDOM** direction moved it **+0.0005** too | ≠ full-covariance whitening, which stays PARKED-BY-SAMPLE-SIZE and is **not** closed by this |
| **`sign()` destroying the forgetting kernel** (STEP 2) | graded **-0.2939** vs binarised **-0.3261**, CIs overlap, power law wins by 38-94 AIC on all four streams | ≠ "the retention curve is meaningless" — it is real, it just measures **interference/dilution**, not consolidation |
| **FORAGE_REFUSAL** (refuse-to-bank harder) | held-out coverage **0.0253** vs FORAGE's 0.0617; grounded 383 vs 604 | ≠ the refusal gate itself, which is what keeps tautologies at 0 |

### CORRECTIONS TO THIS DOCUMENT'S OWN PRIOR CLAIMS (2026-08-14)

- **"Two thirds of what it stores is a tautology" (65.7%) was an ELIGIBILITY BUG.** With the lemma's
  own anchor left eligible, the argmax returns it **100%** of the time — analytically pinned, not a
  measurement. The live loop excludes it and emits **0%** in every arm measured. The legacy
  2328/3544 in `data/foundation/reading_grounding_v1` is that bug. **The tautology half of the C3
  gate now PASSES.** Do not re-quote 65.7% as a live number.
- **"Our code carries a 58% common mode" was ~4x overstated, and mixed two quantities.** Measured on
  the live field (n=2377, d=256): ORGAN_MAP's own `||mean a||/mean||a||` definition gives **0.3650
  GRADED / 0.2997 SIGN** — the sign figure is half the claimed 0.5841 — and **that definition is a
  NORM RATIO, not a variance fraction.** True shared-direction energy is **0.1535**; **PC1 holds
  0.0350** of the centred field's variance. `ORGAN_MAP.md` B3/G3 corrected in place. The
  right-basis *reasoning* for STEP 3 still stands; the *magnitude* that made it look urgent does not.

### PARKED-BY-SCALE — the mechanism is real, our scale is wrong. State the crossover or don't park it.

- **D8 cascade synapse. NOW RULED OUT TWICE, and the second reason is the stronger one.** (i)
  PARKED-BY-SCALE: crossover **~1e6 synapses**; published figures use 2.5e7 and 5.4e9; **we run
  d = 256..4096**, so a negative there is **THE PUBLISHED PREDICTION**, not a ceiling. (ii)
  **UNNECESSARY:** STEP 2 showed the power-law forgetting exponent it would have supplied is
  **already present** in both our read-out arms. **Do not queue it**, as a capacity win or as a
  kernel fix.
- **Full-covariance whitening.** Crossover `O(d²)` samples = **65k-16M**. We don't have them; an
  estimated full covariance would be dominated by its own estimation noise and would ADD variance.

### When an organ is declared UNPINNED-AND-PARKED (rather than drilled forever)

All four must hold. Write them down when you invoke this.

1. The literature does **not** pin the equation — checked in a real drill, not from memory.
2. There is **no can-fail test** that could distinguish candidate forms at our scale.
3. Nothing on the scoreboard is blocked on it.
4. It has already consumed **two** drill cycles without narrowing.

Then: mark it **UNPINNED-AND-PARKED** on the organ map with the date and what would un-park it.
**Saying "the literature does not pin this" is a FINDING about neuroscience, not a hole to fill
with a plausible guess.** The D4 replay SELECTION FUNCTION is the standing example — genuinely
unpinned, and its one normative candidate (Mattar & Daw's `GAIN × NEED`) is blocked on organ D7,
which we don't have.

### Standing kill rules

- **A narrow failure does not prove impossibility.** Before writing "route exhausted", write exactly
  what was tested (data size, quality, mechanism depth) and what the STRONGER version would be, and
  test THAT. We got this wrong once already.
- **A flat result in a LEARNING experiment is a broken experiment, not a ceiling.** Diagnose
  (not-actually-learning / no-new-content / underpowered) before concluding anything.
- **Kill the EXPLANATION separately from the CAPABILITY.** The graded comparator's mechanism story
  is dead while its number stands. Both facts get recorded.

---

## PART 4 — CADENCE THAT RUNS WITHOUT THE DIRECTOR

**Why this section exists.** A 30-minute self-drive loop existed under the old harness and was
**silently lost in migration**. Separately: **11 scheduled tasks were disabled for 12 days** and a
**KB ingest for 6 days** — both unnoticed, because nothing read the gap. The failure class is
always the same: *the check ran, produced a placeholder, and nobody noticed the placeholder.*

**The governing rule: a check that can fail silently is not a check.** Every item below states how
it FAILS LOUDLY.

| what | how often | what it checks | how it FAILS LOUDLY |
|---|---|---|---|
| **Self-drive tick** | **30 min** | is anything moving? if the queue is empty and no run is live, pick the top unblocked step from PART 2 | writes a heartbeat with a UTC timestamp; **if the newest heartbeat is >90 min old, the session-start hook prints an unmissable banner** naming the gap |
| **Scoreboard refresh** | 30 min | re-reads the 7 numbers in PART 1 **off disk** | any number that cannot be found on disk is printed as **`MISSING — DO NOT CITE`**, never silently omitted or carried forward |
| **Scheduled-task liveness** | 30 min | enumerates every `hd_*` task and asserts **Enabled** | any task not Enabled → banner naming the task and its disable date. **This is the specific check whose absence cost 12 days** |
| **KB ingest freshness** | 30 min | `director_kb_freshness_check.py` — newest file on disk vs last-scanned mtime | **exits 1** with a stderr banner if gap >30 min. Already built; keep it wired |
| **Capability registry audit** | session start + weekly | orphans, duplicate versions, unregistered live modules | prints the residue **both ways** (registry-not-on-disk AND disk-not-in-registry) |
| **Floor census** | weekly | recount H1 (PASS-with-no-floor) | if the count ROSE, name the new offenders |
| **Live-path enumeration** | weekly | H3, by **runtime import**, never grep | grep is wrong in both directions in the same file; a grep-based answer is a failure, not a result |

**Three design rules for all of the above, each earned:**

1. **Enumerate from the filesystem, then reconcile to the registry — never the reverse.** A
   registry-first audit is structurally blind to the 62 modules that have no registry row.
2. **A placeholder is a failure, not output.** `(no AS OF line found)` survived undetected inside
   the very hook meant to prevent that failure. Missing input → loud banner, never prose.
3. **The durable anchor is the SESSION-START READ, not the cron.** Crons are a backstop. A rule
   that lives only in a scheduler is one silent disable away from not existing.

**Not yet implemented; the cadence above is a SPECIFICATION.** The self-drive tick, the scoreboard
refresh and the scheduled-task liveness check do not currently exist as running jobs. Building them
is itself a step — and it is deliberately NOT in the top 5, because a cadence that watches a
substrate nobody is improving is theatre. Build it alongside STEP 1, not before.

---

## PART 5 — THE TWO PHASES. DO NOT BLUR THEM.

### PHASE A — BRAIN PARITY, ORGAN BY ORGAN. **← WE ARE ENTIRELY HERE.**

For each organ: identify the brain structure, find its ACTUAL mathematical operation, implement
THAT operation in the right SHAPE, the right POSITION in the pipeline, judged on the BRAIN'S
metric. Right component is not enough — shape, place and metric all have to match.

Everything in PART 2 is Phase A. Every scoreboard number is a Phase-A number.

**Ask of every mechanism, before building it:** (1) which brain structure does this — a neural
system, not a cognitive-theory label? (2) does it share an already-developed process, in which case
**REUSE that organ**? The brain reuses circuits; a parallel build is both unfaithful and an island.

### PHASE B — SUPERCHARGE BEYOND THE BRAIN. **NOTHING IS IN PHASE B. NOTHING.**

Named here **only so they are not started by accident.** If you find yourself working on one of
these, you have left the plan.

| candidate | why it is tempting | why it stays parked |
|---|---|---|
| **Dimensionality far beyond biological sparse codes** (d ≫ 4096) | the capacity curve keeps climbing | we have not matched the brain at d=256. A bigger unfaithful organ is still unfaithful |
| **Exact/lossless binding beyond what neural noise permits** | we CAN be exact; brains can't | the brain's failure modes carry information. Removing them before understanding them removes the thing we're studying |
| **Unbounded perfect memory (no forgetting)** | trivially available to us | **forgetting is a mechanism, not a defect** — the `t^-1/2` kernel in STEP 2 is the point |
| **Full-covariance whitening at scale** | strictly more powerful than rank-1 | PARKED-BY-SAMPLE-SIZE, and it is a Phase-B ambition wearing a Phase-A costume |
| **Parallel replay far beyond ~10-30k events/night** | we have no metabolic budget | the schedule's SHAPE is what's pinned; running it 1000× faster tests nothing about fidelity |
| **Non-biological retrieval indexes** (ANN structures with no cortical analogue) | fast and effective | this is the glass-box invariant's edge. Allowed only if the mechanism stays inspectable |

**The gate from A to B, per organ:** the organ does the brain's operation, in the right shape and
position, judged on the brain's metric, **against a floor it could have failed** — and only then
may it be exceeded. **Phase B is opened per-organ, never globally.**

**The invariant that survives both phases:** runtime reasoning is **glass-box**, with **no external
LLM at inference**. That never relaxes, in A or in B.

---

## PART 6 — HOW TO NOT DRIFT

- **Only held-out or public numbers count.**
- **VET positives exactly as hard as negatives.** An upward surprise gets the same scrutiny.
- **State the SCOPE of every claim.** "Grounding is 1-3%" is a fact about ONE loop, not the system.
- **A floor is only a floor on the SAME corpus, metric, run and arm.** Today's coref correction is
  the whole reason this line exists.
- **Run a KNOWN-ANSWER arm as well as a floor. A floor tells you whether the EFFECT is real; a
  known-answer arm tells you whether the INSTRUMENT is.** They fail independently. Bought twice on
  2026-08-14: the forgetting-kernel estimator returned a confident CI that **excluded the truth**
  (survivorship bias dropped 96 of 1140 synthetic points; pseudo-replication inflated AIC) and only
  the synthetic arm could show it; and the read-out's SELF_RETRIEVAL 0.786 is what licensed reading
  its nulls as MEANING failures rather than plumbing. Full text: `notes/STATUS_LESSONS.md`
  STANDING DISCIPLINE 6.
- **An organ with no floored evidence is UNTESTED, not working.**
- **Prefer UNPINNED and UNTESTED over confident filler.**
- **Re-verify before citing.** Notes go stale within hours; three did in one day.
- **Select by brain-foundational-correctness, not by cheapness.** Difficulty is irrelevant to the
  pick. Cheap probes are fine to RUN for a measurement; they never set DIRECTION.
- **Wire it or shelve it.** A gain left in experimental results is an island. Promote to `hdlab/`,
  register it, or write explicit revival criteria. Nothing stays in limbo.
