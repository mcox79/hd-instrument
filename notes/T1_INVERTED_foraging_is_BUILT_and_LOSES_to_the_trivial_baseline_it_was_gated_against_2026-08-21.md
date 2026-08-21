# T1 INVERTED -- **"DECIDE WHAT TO READ NEXT" IS NOT MISSING. IT IS BUILT, IT LANDED HARD_PASS, AND THE TRIVIAL BASELINE BEATS IT ON EVERY LEARNING OUTCOME.**

**Found ~20 minutes after writing tonight's plan, by the mandatory prior-work check** --
`tools/experiment_index.py query "information foraging"` -> **scanned 8,836 cells, 2 matching, 2
landed.** *The plan proposed BUILDING this organ. It was built a week ago.*

**Cell:** `exp_information_foraging_reading_v1`, **HARD_PASS**, 2026-08-14, 4,144 s, 5 arms,
10,000 sentences each.

---

## 1. THE NUMBERS, ALL FIVE ARMS, ONE RUN, SAME CORPUS AND SCORER

| arm | grounded | **held-out coverage** | held-out precision | **dominant-domain share** | corpora read |
|---|---|---|---|---|---|
| **FROZEN** *(the trivial 4-corpus schedule)* | **696** | **0.0743** | **0.3204** | 0.8822 | 4 |
| **FORAGE** *(the organ)* | 604 | 0.0617 | 0.3063 | 0.6325 | 19 |
| FIXED_LEAVE | 440 | 0.0520 | -- | -- | -- |
| FORAGE_REFUSAL | 383 | 0.0253 | -- | -- | -- |
| **RANDOM** | 157 | 0.0127 | 0.2420 | **0.3057** | 28 |

*(lower dominant-domain share = more varied reading)*

## 2. 🚨 **THE FINDING: FORAGE IS DOMINATED ON BOTH AXES, EACH BY A DIFFERENT TRIVIAL BASELINE**

| what you might want | who wins | FORAGE |
|---|---|---|
| **LEARN MORE** (grounded, held-out coverage, precision) | **FROZEN** -- 696 vs 604, 0.0743 vs 0.0617, 0.3204 vs 0.3063 | **2nd** |
| **READ MORE WIDELY** (dominant-domain share) | **RANDOM** -- 0.3057 vs 0.6325 | **2nd** |

**➡️ THE ORGAN IS SECOND AT BOTH JOBS, AND IT LOSES EACH ONE TO A BASELINE THAT COSTS NOTHING.**
*Reading the same four documents forever grounds MORE words and answers MORE held-out probes than
choosing cleverly. Picking corpora at random reads more widely.*

## 3. **HOW A HARD_PASS SURVIVED THAT -- AND THE CELL DID NOT HIDE IT**

**The cell RECORDED the losing comparison in its own metrics** -- `D2` carries
`frozen: 0.074333` beside `forage: 0.061667`. **Nothing was concealed. The GATE was the defect.**

| gate | comparator chosen | outcome |
|---|---|---|
| **D1** dominant-source-share drop | **vs FROZEN** | PASS 0.1585 -- *a DIVERSITY statistic* |
| **D2** held-out coverage | **vs RANDOM** (the WEAKEST arm) | PASS 3.87x -- *and FROZEN, in the same run, BEAT it* |
| D3 WordNet agreement | vs FROZEN, non-inferiority | PASS -- *though RANDOM scored highest at 0.3864* |
| **D4 oracle ratio** | -- | **FAIL** 0.5343 (band 0.70-1.00) |

**Each gate picked whichever baseline that gate could beat.** The organ map's STEP 1 is explicit --
***"FLOOR -- two arms, BOTH must be beaten: (i) RANDOM ... (ii) the FROZEN 4-entry schedule"***.
**On the learning outcome FORAGE beats only one of the two.**

**AND THIS IS THE REPO'S OWN NAMED FAILURE MODE, VERBATIM: *"A STATISTIC THE MECHANISM OPTIMISES IS
NOT AN OUTCOME."*** D1 measures source diversity; **choosing varied sources is precisely what the
foraging controller does.** It is the anchor-margin error in a new costume -- *measuring the thing
you selected on.*

## 4. ⚠️ **AND IT IS ONE SEED**

`units.jsonl` holds **5 units -- one per arm -- and no `seed` field on any of them.**
**`tools/replication_gate.py` returns `SINGLE_SEED_HYPOTHESIS`.**
*So the HARD_PASS is a single-seed result, which is the shape of four claims already withdrawn this
week. **The inversion in §2 inherits the same limit and is stated as a hypothesis, not a finding.***

## 5. WHAT THIS CHANGES TONIGHT

1. **T1 IS NOT A BUILD.** The organ exists and is wired enough to run 10,000 sentences and choose
   among 19 corpora (`mechanism_fired`: ranked choice, multiple patches, multiple corpora -- all
   true). **Building it again would have re-derived a landed result.**
2. **ORGAN_MAP §1 CALLS H2 *"MISSING"*. IT IS NOT.** That row needs correcting -- and the
   single-sentence summary built on it (*"the organ that decides what to read next ... is why the
   system cannot notice what it does not know"*) is **rhetorically strong and factually stale.**
3. **THE REAL QUESTION IS NOW SHARPER AND CHEAPER:** not *"can we build corpus selection"* but
   ***"why does reading the same four documents forever beat choosing what to read?"*** *That is a
   far more interesting question, and it is a NEGATIVE TO DRILL rather than an organ to build.*
4. **DOES NOT UNBLOCK SLEEP AS ADVERTISED.** Tonight's plan justified T1 partly as the unblocker for
   step 5 (*"nothing new to forget otherwise"*). **FORAGE already reads 19 corpora, so the stream of
   new material exists** -- the blocker on sleep may be smaller than the plan assumed. *To be checked,
   not assumed.*

## 6. THE HONEST COUNTER-CASE -- **RAISED, CHECKED, AND REFUTED IN ONE QUERY**

**MY COUNTER-CASE WAS: FROZEN's win is a domain-match artifact.** It reads 4 biology-adjacent
corpora at a dominant-domain share of **0.8822**; if the held-out probe were biology-weighted,
FROZEN would be tested on what it had just read -- a leak-shaped result. *That was the first thing
to check and it decides the whole finding.*

**IT IS WRONG. THE PROBE IS NOT A CORPUS SAMPLE AT ALL.**
`heldout = load_base_vocab(1000, 4000)` -- **frequency ranks 1001-4000 of
`base_vocabulary_ordered.csv` (74,287 rows), held out of EVERY arm, identical for all five.**
Positive control on what those words actually are, rather than an absence check:

> `grab, fighting, art, favor, upstairs, wall, force, seconds, jail, push, prove, normal, machine`
> ... `castle, delicious, value, circle, miserable, glory, squad, manage`
> ... `pillow, talented, teachers, roommate, stones, bears, safer, approve`

**Ordinary everyday English. No biology bias whatsoever.**

**➡️ SO THE FINDING GETS STRONGER, NOT WEAKER: FROZEN READS FOUR BIOLOGY-HEAVY DOCUMENTS AND STILL
GROUNDS MORE ORDINARY ENGLISH VOCABULARY THAN FORAGE READING NINETEEN CORPORA.** *The one
explanation that would have excused the result is ruled out by construction.*

### WHAT STILL LIMITS IT
- **One seed** -- `SINGLE_SEED_HYPOTHESIS`. No CIs, no tie handling.
- **So the correct statement is NOT "foraging failed."** It is: **the HARD_PASS does not establish
  that foraging beats doing nothing clever, because the arm that beat it was in the same run and was
  not the gate** -- and the obvious excuse for the winner has been checked and does not hold.

## 7. 🔬 **THE DRILL: *WHY* FROZEN WINS -- AND IT PARTLY REHABILITATES THE ORGAN**

All five arms read **exactly 10,000 sentences**. Splitting the outcome into *how many extraction
attempts each arm generated* and *what fraction of those succeeded* -- both already in the metrics,
no new run -- gives the mechanism:

| arm | banked | refused | **attempts** | **HIT RATE** | held-out |
|---|---|---|---|---|---|
| **FROZEN** | 696 | 3,872 | **4,568** | **15.2%** | 0.0743 |
| **FORAGE** | 604 | 1,633 | 2,237 | **🥇 27.0%** | 0.0617 |
| FIXED_LEAVE | 440 | 1,464 | 1,904 | 23.1% | 0.0520 |
| FORAGE_REFUSAL | 383 | 1,419 | 1,802 | 21.3% | 0.0253 |
| **RANDOM** | 157 | 1,177 | 1,334 | **11.8%** | 0.0127 |

**➡️ FORAGE HAS THE BEST HIT RATE OF ANY ARM -- 27.0% vs FROZEN's 15.2%. IT LOSES ON VOLUME:
FROZEN GENERATES 2.04x THE ATTEMPTS FROM THE SAME 10,000 SENTENCES.**

**AND THE ORGAN IS DEMONSTRABLY DOING ITS JOB, WHICH THE HEADLINE ALONE HIDES.** Against **RANDOM**
-- the arm that isolates *choosing* from *not choosing* -- FORAGE more than **doubles** the hit rate
(27.0% vs 11.8%) while reading fewer corpora (19 vs 28). *Gap-driven selection genuinely picks better
material. That is a real capability and it is not what failed.*

**WHAT FAILED IS THE OBJECTIVE.** FORAGE maximises **yield per attempt**; the outcome scores **total
banked**. The four frozen corpora are dense textbook prose that offers far more extractable structure
per sentence, so **volume beats precision at this foundation size** -- *and nothing in the foraging
controller's value function knows that.*

**➡️ THE CONCRETE, TESTABLE FIX THIS POINTS AT:** the ranker weights expected *gap coverage* and is
blind to expected *attempt density*. **A patch that yields 4 candidate structures per sentence is
worth more than one that yields 1, even at a lower hit rate** -- which is ordinary marginal-value
arithmetic and exactly what the foraging controller already exists to compute. *Stated as a
hypothesis: it predicts FORAGE overtakes FROZEN once density enters the gain term.*

## TLDR

Tonight's plan said the top job was to build the part that decides what to read next, because the
organ map lists it as missing and calls it the reason the system can't notice what it doesn't know.

**It isn't missing. It was built a week ago and passed.** I found that in the first check I ran, which
is the check that exists for exactly this.

**But reading the passing result properly, it's worse than that.** The system was compared against
two dumb baselines: reading the same four documents forever, and picking documents at random. **It
lost to one of them at each of the two things it's supposed to be good at.** Reading the same four
things forever actually taught it *more* words and answered *more* test questions. Picking at random
read *more widely*. Clever selection came second at both.

It passed because each individual checkpoint was scored against whichever of the two baselines it
could beat — diversity measured against the narrow one, learning measured against the random one —
while the arm that actually beat it sat in the same results file. **Nothing was hidden; the cell
wrote the losing number down. The scoring rule just never looked at it.**

**I then tried to explain the result away, and failed.** My objection was that the winner might be
cheating without meaning to — the four frozen documents are mostly biology, so if the test words were
also mostly biology it was being tested on what it had just read. **That turned out to be wrong.** The
test is a fixed list of ordinary English words — *grab, upstairs, jail, castle, delicious, pillow,
roommate* — kept away from every version equally. So reading four biology documents forever teaches
the system **more ordinary English** than choosing among nineteen sources. **The one excuse available
to the winner doesn't hold, which makes the result stronger rather than weaker.**

One caveat stands: **it's a single run, not repeated.**

**Then I dug into why — and it's much more interesting than "the clever thing lost."**

Every version read exactly the same number of sentences. Split the result into *how many times each
one tried to learn something* and *how often trying worked*, and the picture flips: **the clever
selector has the best success rate of anything tested — 27%, against 15% for reading the same four
documents.** It's genuinely good at picking promising material. Compared against picking at random,
which is the fair test of whether choosing helps at all, **it more than doubles the success rate.**

**It loses because it doesn't try often enough.** The four frozen documents are dense textbooks that
offer roughly twice as many chances to learn something per sentence. So the selector wins every
attempt and still loses the match.

**That means the machinery works and the goal is wrong.** It's built to maximise how often it
succeeds, while what actually matters is how much it learns in total — and nothing in it currently
knows that a page offering four chances beats a page offering one. **That's a small, specific fix
rather than a rebuild**, and it predicts the selector overtakes the frozen schedule once it counts
opportunities as well as quality.

## QUESTIONS

None.

## NEXT STEPS

1. ✅ **DONE -- the leak explanation is refuted.** The probe is a fixed general-English frequency band,
   identical across arms. **The inversion stands** (single-seed).
2. **Correct `ORGAN_MAP` §1's "MISSING" row for H2** and the summary sentence built on it.
3. **Drill the real question: why does the frozen 4-corpus schedule ground more everyday vocabulary?**
   *First hypothesis worth testing: FROZEN refuses far more (3,872 vs 1,633) yet banks more -- so it
   may simply be getting more ATTEMPTS per useful sentence, i.e. depth beats breadth at this
   foundation size.* Re-run with seeds before claiming it in either direction.
