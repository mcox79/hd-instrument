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

**The one number that gates everything.** When our reader reads text and tries to extract meaning
it can later use, only **1-3%** of what it stores is genuinely meaningful. Two thirds of what it
does store is a tautology — the machine writing down "a dog is a dog." Until that number is at
least **10%**, we do not grow the knowledge base. Adding more of a thing that is 97% empty just
makes a bigger empty thing.

**The trap we already fell into.** Four separate ideas for fixing this were tried and all four
failed *cleanly* — meaning we know they're dead, which is worth something. More facts: no. Better
text: no. More coverage: no. Cleverer weighting: no. The lesson is that the problem is not supply.
Something in how the machine READS BACK what it stored is broken, and we have not yet run the one
experiment that would tell us what.

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
| **C1** | **Near-neighbour 2AFC, live reading path** | **0.6980** (was 0.6395) | scrambled-context **0.5095**, frequency **0.48025**, chance 0.50 | `38f7a0d5c` (graded comparator ON) | (a) rank-1 common-mode removal; (b) the PRICED capacity step `d=256→1024`, worth ~**+0.05** and not yet taken |
| **C2** | **Context-conditioned discrimination GAP** | **+0.1005** (0.6395 with context vs 0.5390 without) | scrambled-context **0.4975**, frequency 0.4800 | `exp_context_conditioned_near_neighbour_v1` | anything that makes the context port carry MORE than "some signal is present". The gap is real; its CONTENT is unproven |
| **C3** | **Reading-grounding MEANINGFUL rate (read-out)** | **1-3%**, tautology rate **65.7%** | needs a recorded floor arm — **currently none** | — (stuck) | **UNKNOWN. This is the point.** The read-out quality experiment has been dispatched 3× and never completed. See STEP 1 |
| **C4** | **Coreference, identity-demanding accuracy** | **0.7193** (earned 0.6842) | recency **0.5614**, singleton **0.3860**, oracle ceiling **0.9298** | `exp_wire_coref_accumulate_situation_model_v1` | closing earned-vs-oracle (0.6842 → 0.9298). This is a WIDEN-THE-MARGIN target on a WORKING organ |

**C3 is the gate.** While C3 is under 10% on a blind hand-score with tautologies under 10%,
**KNOWLEDGE-BASE GROWTH STAYS PAUSED.** No new corpora ingested for the sake of size. This is not
caution, it is arithmetic: growth multiplies whatever the quality is.

### HYGIENE (these are also progress, and they are cheap)

| # | number | now | target | why it's on the headline list |
|---|---|---|---|---|
| **H1** | PASS-flavoured verdicts with **NO FLOOR** | **134** | **0** | A PASS with no floor is not evidence. 134 of them is a standing lie in our own records |
| **H2** | **Biology share of vocabulary** | **63.9%** (54.6 → 63.2 → 63.9 across extractor generations) | **falling** | ⚠️ **ANTI-METRIC — must go DOWN.** Self-reinforcing: improving extraction WITHOUT fixing corpus selection amplifies the skew. Three generations of "improvement" made it worse |
| **H3** | Modules on the live path | **44 of 155** | rising, honestly measured | Measured by RUNTIME, never grep. A capability not on the live path is an island, and islands don't count |

### Numbers that are NOT on the scoreboard, and why

- **Definitional extraction 94%** — real (47/50, `exp_definitional_predicate_v62`) but **NO FLOOR
  RECORDED**, so it cannot be a headline. Give it a floor and it can join. Also: it measures what a
  PARSER HANDS the substrate, not what the substrate recovers. **Never place it beside C3.**
- **The hand-scored 64%** — also real (32/50, v5 term-boundary fix, floor 8%), also measures
  parser-handed extraction. **1-3% / 64% / 94% are three different populations, not a
  contradiction.** Cross-scoring them is already logged as a repeated error. Do not repeat it.
- **0.7495** — this is the **d=1024** arm, not the live path. Quoting it as shipped is quoting an
  unshipped capacity change. See C1's "priced" note.

---

## PART 2 — SEQUENCED BUILD ORDER

Per step: the organ, the specific fidelity fix, a test that can FAIL, its floor, and whether it can
run alongside others.

### STEP 1 — **RUN THE READ-OUT QUALITY EXPERIMENT.** `exp_grounding_quality_readout_v1`
- **Organ:** B1/B2 — what the context vector actually contains.
- **Why first:** it is the only experiment that can answer the question gating everything else
  (C3). **It has been dispatched three times and never completed.** A prereg is already filed
  (`192521a7f`), and the F1+F3 read-out fixes are already wired **default-OFF**.
- **Fidelity fix:** the frozen-anchor-space read-out (F3) is already known to stabilise argmax
  (−0.168 at matched retention). **Stability is NOT quality** — read-out stability and meaning
  quality may be fully decoupled. That is the open question.
- **CAN-FAIL TEST:** blind hand-score of MEANINGFUL rate with F1+F3 ON vs OFF, at matched retention.
- **FLOOR:** the live NULL arm (already in the prereg bands) + the current 1-3% + tautology <10%.
- **ORDERING:** **STRICTLY FIRST.** Everything about growth waits on it.
- **Failure mode to watch:** it dying a fourth time. Make it resumable per unit and detached
  (`Start-Process`, separate stdout/stderr, PID file) — the three prior deaths are consistent with
  the launching agent exiting.

### STEP 2 — **THE ONE-FLAG MEASUREMENT.** `ConceptSpace.observe`
- **Organ:** D8-adjacent — forgetting kernel.
- **The finding:** an unbounded accumulator already yields the brain's **`t^-1/2`** forgetting
  kernel. `ConceptSpace.observe` accumulates unbounded, then **`np.sign()`s it one line before
  use** — throwing the kernel away. The graded flag that just landed may already restore a pinned
  prediction.
- **CAN-FAIL TEST:** retention-vs-time curve with the graded flag ON vs the `sign()` path. Pinned
  prediction: **power law `t^-1/2`, not exponential.** A fitted exponential wins → fail.
- **FLOOR:** the `sign()` path; and the analytic exponential.
- **ORDERING:** **PARALLEL with everything.** One flag, one measurement, no build.
- **Why it's cheap and still on the list:** it is a measurement we can take today on an organ whose
  math IS pinned. Cheap probes are fine to RUN; they never set direction.

### STEP 3 — **RANK-1 COMMON-MODE REMOVAL.** Organ G3 (neuromodulatory gain)
- **Fidelity fix:** whitening is per-dimension gain **IN THE RIGHT BASIS.** Our four failed
  reweightings were per-RAW-dimension — the wrong basis — so they are **not** evidence that this
  fails. Our code carries a **58% common mode**: one shared direction holding most of the variance.
- **CAN-FAIL TEST:** C1 (near-neighbour 2AFC) with rank-1 mean removed vs not.
- **FLOOR:** current 0.6980; scrambled 0.5095; frequency 0.48025. **Plus a can-fail control:**
  remove a RANDOM rank-1 direction. If that helps equally, the effect is not the common mode.
- **ORDERING:** **PARALLEL** with steps 1-2.
- **Bounded on purpose:** rank-1 needs `O(d)` samples and is estimable. **Full-covariance whitening
  needs `O(d²)` (65k-16M samples) and is PARKED-BY-SAMPLE-SIZE.** Do not queue it.

### STEP 4 — **THE PRICED CAPACITY STEP.** `d = 256 → 1024`
- **Status: AVAILABLE AND UNCLAIMED, worth ~+0.05 on C1.** Recorded here as a PRICED STEP, **not
  as an achieved result.**
- **Measured:** QUANT `[0.6395, 0.7030, 0.7380]`, GRAD `[0.6980, 0.7495, 0.78225]` at d =
  256/1024/4096. Capacity is the LARGER lever and was deliberately not changed.
- **COST:** rewrites every persisted anchor store (a migration).
- **RISK:** a concurrent session is live. **Do not start this while another session holds the store.**
- **CAN-FAIL TEST:** C1 at d=1024 post-migration, against the d=256 number and the d=1024 scramble
  floor (0.49025).
- **ORDERING:** **STRICTLY AFTER** step 3 (so the common-mode fix isn't confounded with capacity)
  and after the concurrent session clears.
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
- **ORDERING:** **PARALLEL.** Its metric improves if 1-3 land; its build does not depend on them.

### Below the line (real, sequenced, not top-5)
**D4 replay schedule** — needs STEP 1's corpus stream to be testable at all, and needs the corrected
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

### PARKED-BY-SCALE — the mechanism is real, our scale is wrong. State the crossover or don't park it.

- **D8 cascade synapse.** Crossover **~1e6 synapses**; published figures use 2.5e7 and 5.4e9. **We
  run d = 256..4096.** A negative here is **THE PUBLISHED PREDICTION**, not a ceiling. If run at
  all, it is run to confirm the predicted null AND the predicted initial-SNR **cost** (`1/n`,
  `1/√m`) — the only part observable at our scale. **Do not queue it as a capacity win.**
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
- **An organ with no floored evidence is UNTESTED, not working.**
- **Prefer UNPINNED and UNTESTED over confident filler.**
- **Re-verify before citing.** Notes go stale within hours; three did in one day.
- **Select by brain-foundational-correctness, not by cheapness.** Difficulty is irrelevant to the
  pick. Cheap probes are fine to RUN for a measurement; they never set DIRECTION.
- **Wire it or shelve it.** A gain left in experimental results is an island. Promote to `hdlab/`,
  register it, or write explicit revival criteria. Nothing stays in limbo.
