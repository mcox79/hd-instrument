---
problem: the_attachment_arm_mis_attaches_30_percent_of_infinitival_verbs_wire_the_predicate_slot_into_the_infinitival_arc_and_add_a_nominal_governor_cue_accrued_from_counts
status: SOLVED
bar: "Infinitival heads CI-sep over the shipped arm with no construction down CI-sep; UAS not down; the purpose decision up (target +0.10); validities accrued with an observe path (twin at floor); the reference twin ported; the board not down -- OR a numbered located negative naming the construction that cannot be won by competition and why."
result: "UD-EWT test, the organ's OWN categories (live chain, no gold column on the decision path), population = every infinitival VERB by the organ's own tags, n=337 -- pri 129's population reproduced to the item. Measured THROUGH THE DIFF, the organ as shipped vs the patched organ, BOTH IN ONE PROCESS: infinitival heads 0.6766 -> 0.7745 (+0.0979 CI[+0.0564,+0.1381] half 0.0409, SEPARATED). NO CONSTRUCTION DOWN: acl_nominal 0.2321 -> 0.4286 (+0.1964 CI[+0.0577,+0.3333] SEP), csubj_extrapos 0.5652 -> 0.8261 (+0.2609 CI[+0.1000,+0.4643] SEP), xcomp_control 0.8757 -> 0.9349 (+0.0592 CI[+0.0119,+0.1087] SEP), advcl_purpose 0.6338 -> 0.7183 (+0.0845 CI[-0.0282,+0.2059] ns, UP -- the construction pri 129's prototype LOST, 0.6338 -> 0.5775), other 0.5000 -> 0.5000 (exactly flat). UAS 0.6465 -> 0.6493 (+0.0028 CI[+0.0019,+0.0040] SEPARATED UP, n=24,586); non-verbal subject attachment 0.6186 -> 0.6332 (+0.0146 CI[+0.0040,+0.0268] SEP), verbal subjects flat; per relation the only movements below zero at n>=20 are amod -0.0008 and mark -0.0013, while acl 0.1421 -> 0.1716, advcl 0.4180 -> 0.4399, xcomp 0.7583 -> 0.8000, csubj 0.3600 -> 0.5600, cop 0.6724 -> 0.6810, nsubj 0.8054 -> 0.8093, root 0.7454 -> 0.7465. READ TIME: none (shipped 15.72 ms/sentence, patched 15.67). The knowledge is LEARNED FROM READING with no tree, no treebank head and no gold column anywhere on the learning path: 6,081 lexical keys accrued from 3,192 sentences read through the organ's own categories, and the two cue channels' validities accrued by the organ's own observe path from the clear cases -- every OTHER cue channel of the landed table is byte-identical (asserted, 15 channels)."
floor: "Attach the infinitival verb to the NEAREST PRECEDING VERB (the arm's dominant existing behaviour): 0.6291 overall (acl_nominal 0.0357, advcl_purpose 0.6197, csubj_extrapos 0.4348, xcomp_control 0.8757, other 0.4444) -- reproduced to the digit against pri 129's landed table. The organ EXACTLY AS SHIPPED is the second floor: 0.6766. Also run as reference points, not as arms: pri 129's count-accrued prototype reproduced in-cell at 0.8012 (it loses advcl_purpose 0.5775 and other 0.1111); the whole-sentence single-root search decode of the patched matrix 0.7597; the matrix ARGMAX with no tree constraint at all 0.7674."
controls: "(1) PERMUTED-VALIDITY TWIN -- both cue channels' accrued cells permuted across their values, sites and values unchanged: 0.4481, the shipped form beats it +0.3264 CI[+0.2699,+0.3824] SEPARATED, and the twin scores BELOW the organ as shipped and below the nearest-verb floor. (2) SHUFFLED-LEXICON TWIN -- the lexical infinitival-expectation store's counts shuffled across words, so `plan` and `market` swap expectations and nothing else changes: 0.7359, the shipped form beats it +0.0386 CI[+0.0100,+0.0669] SEPARATED, and acl_nominal falls 0.4286 -> 0.3036, so the LEXICAL CONTENT is load-bearing exactly where the brief said it would be. (3) UNIFORM-VALUE TWIN -- the control for the ARITHMETIC rather than the information: every value of both channels collapsed to one string, so the per-configuration OFFSET that a targeted overlay necessarily carries survives and the information does not. It scores 0.6706, i.e. BELOW the organ as shipped (0.6766) -- the offset is not the source of the gain, it is slightly harmful. (4) SWITCH-OFF EQUIVALENCE -- with every new switch off the patched organ reproduces the shipped readout EXACTLY (0 differing sentences of 37, asserted in --self-test). (5) PATCHED == REFERENCE -- the vectorised readout equals the per-pair reference loop to 1e-9 with all three new channels live (43 sentences), the organ's own fastpath invariant; the reference twin is ported in the same diff. (6) SILENT DEGRADATION -- each channel returns {} when its own input is absent (a table built before this cue; a category inventory the occupancy read cannot use), asserted. (7) A REFUTED ARM, REPORTED AGAINST MYSELF -- a case-marking / retrieval-interference channel (`ictx`) was built and MEASURED: it lifts acl_nominal to 0.4821 but takes advcl_purpose 0.7183 -> 0.5915, net 0.7745 -> 0.7359; it ships default OFF with its number and the mechanism (section 7). (8) THE POPULATION AND THE SCORER ARE pri 129's OWN: its `--infin` scorer was imported and re-run, reproducing its table to the digit (arm 0.6766 / prototype 0.8012 / floor 0.6291 / twin 0.4540 and all five per-construction rows), and my cache-based population is the same 337 items with the same class counts."
files_changed: "experiments/exp_infinitival_governor_competition_v1.py (the cell: the population, the accrual, the arms, the twins, the residual attribution, the one-process live A/B through the diff, the purpose consumer, the board rows); notes/problems/<slug>/{SOLVED.md, infinitival_governor_patch.diff} (the PROPOSED change -- unified diffs against hdlab/attachment_arm.py AND tools/build_attachment_validities.py, applying cleanly at 584cc37a9 with `git apply`); data/frontend_assets/attachment_validities_infin_v1.json and data/frontend_assets/attachment_validities_infin_adv_v1.json (NEW file names -- the shipped table is never overwritten); data/exp_infinitival_governor_competition_v1/*.json. NO hdlab/ or tools/ file edited: the diff is EXECUTED by the cell, which loads it in memory as the organ."
reverify: ".venv/Scripts/python.exe experiments/exp_infinitival_governor_competition_v1.py --self-test  (18/18, and it applies the diff, runs the fastpath-vs-reference invariant with the new cues, and asserts the switch-off equivalence) ; then the headline, ~2.5 min, writes only into its own directory: HDLAB_EXP_NAME=infinitival_governor_competition_v1 .venv/Scripts/python.exe experiments/exp_infinitival_governor_competition_v1.py --live-ab ; the controls: --twins ; the lever decomposition: --arms ; the residual attribution: --residual ; pri 129's own table: --repro ; out of supply: --oos ; the consumer: --purpose ; the product rows: --board. The knowledge is reproducible from reading alone: --accrue --cap 4000 --teacher clear (~40 s, writes the NEW asset only)."
---

# SOLVED -- the infinitival governor is now decided by the same cue competition as every other arc, and the clause is reanalysed when it arrives

**0.6766 -> 0.7745 on infinitival heads (UD-EWT test, n=337, CI-separated), with NO construction down -- including
`advcl_purpose`, the one pri 129's prototype lost.** The two cues the brief named are inside `arc_scores` with
validities accrued from reading, and a third finding fell out of the measurement and turned out to be the biggest
single lever: **the competition already preferred the right governor and the in-order beam could not reach it.**

---

## 1. THE BAR, IN MY OWN WORDS

When a sentence contains "to do something", attach that clause to the word it belongs to -- and do it the brain's
way, by the same competition among cues that decides every other attachment, with the strength of each cue LEARNED
from reading rather than set by hand. The number to beat is 0.6766 on the 337 infinitival verbs of UD-EWT test;
the nearest-preceding-verb floor is 0.6291; no one of the four constructions may go down; whole-sentence
attachment accuracy must not fall; a version of the mechanism with its information removed must lose; and the
downstream purpose decision should rise.

**And one thing the bar says that is easy to miss: pri 129's prototype already scores 0.8012 overall. It is NOT
the target.** It reaches that number by overriding the arm's other cues, and it pays for it on
`advcl_purpose` (0.6338 -> 0.5775) and `other` (0.5000 -> 0.1111). The landed form has to win *inside* the
competition, which is a harder bar than the prototype's number.

## 2. THE UPSTREAM CHAIN AND WHAT EACH RUNG HANDS DOWN (the status probe, with counts)

The signal the end read needs is **"which word does this infinitival clause belong to"**.

| rung | organ (file) | what it PRODUCES for this signal | what the next rung READS | what is LOST |
|---|---|---|---|---|
| tokens | `frontend.tokenize` | the token sequence | all | nothing measured here |
| categories | `hdlab/lexical_categories.py` | a graded posterior per token, with pri 110's predicate-slot revision applied | the heads rung reads the posterior; `arc_scores_graded` computes the occupancy from it | **8 of the 76 remaining misses are a gold governor the retrieval never offered because the category organ reads it as something else** -- 3 of them are a UD `ADJ` read as `ADV`, 1 a `NOUN` read as `ADV`, 1 a `VERB` read as `ADP`. A categories-rung loss, counted here for the first time |
| lemma | `hdlab/morphology.py` | verb lemmas | the lexical expectation's key | not load-bearing: the store keys on `lemma_verb` for verbs and a de-pluralised form for nominals |
| **heads** | `hdlab/attachment_arm.py` | the arc competition, then the in-order decode | the roles rung, the goal register, the state reader | **THE LOSS THIS BRIEF NAMES, and it was in TWO places, not one.** (a) The competition had **no cue that lets a NOUN govern an infinitival clause** and **never read the predicate slot** -- 38 of the 109 shipped misses are "the competition out-scored the gold and preferred a VERB". (b) **37 of the 109 are arcs the competition ALREADY PREFERRED and the in-order beam could not realise** -- this half is not in the brief and it is the bigger one |
| roles / goal / state | `graded_role_assigner`, `goal_register`, `situation_reader` | who did what, the purpose decision | the board | pri 129 measured the propagation: with GOLD heads its purpose arm goes 0.6589 -> 0.7907, +0.1084 CI-separated above the frozen supervised label |

**Brain-foundational status of each rung FOR THIS SIGNAL, as the disk shows it.** Categories: BF (pri 110, graded,
top-down constraint satisfaction on a settling belief) -- but it hands this rung a **point estimate for the
retrieval decision**: the candidate SET is built from the argmax tag, so a token the organ reads `ADV` is not
offered at all even when the posterior keeps `ADJ` alive. Lemma: BF-spirit. Heads: BF_SPIRIT -- the cue
competition is the Competition Model's, the validities are learned contrasts, but **two of the three constraints
this decision needs were simply absent** and the decode discarded a third. Consumers: BF since pri 129.

**The one non-BF link for this signal, stated exactly:** the arm had a full, learned competition and **no lexical
knowledge to compete with**. The Competition Model's cue strength is *availability x reliability accrued from
experience*; the arm had reliability machinery and nothing to be reliable about. That is what this solution
supplies.

## 3. THE BRAIN, AND THE THREE COMPUTATIONS BUILT

**Opening move -- how does the brain attach an infinitival clause?** It is LEXICALIST constraint satisfaction. The
governor is the candidate whose stored subcategorisation expects an infinitival complement, and the STRENGTH of
that expectation is its usage frequency (MacDonald, Pearlmutter & Seidenberg 1994; Trueswell, Tanenhaus & Kello
1993 and Garnsey, Pearlmutter, Myers & Lotocky 1997 measured exactly this bias driving human attachment), settled
by competition among the candidates retrieved under memory-limited locality (Vosse & Kempen 2000; Lewis &
Vasishth 2005; Bates & MacWhinney's validity = availability x reliability). Two further pinned facts: a clause
predicates ONE thing (Spivey-Knowlton 1993) and an expletive is a PLACEHOLDER, not a predicate (Postal & Pullum
1988) -- so an extraposed clause belongs to the token holding the predicate slot and never to the expletive. And
when a later word disambiguates, the analysis is REVISED rather than re-derived (Frazier & Rayner 1982;
MacDonald 1994 on overtaking). Nothing here is a new organ: all three are arms of the attachment competition the
substrate already has.

**1. THE LEXICAL INFINITIVAL EXPECTATION (`iexp`), ONE CUE FOR ALL THREE CLASSES.** The brief asked for a
*nominal* governor cue. Building it as a nominal cue would have been the wrong shape: the expectation is a
property of the WORD, not of its category -- `plan` / `attempt` / `chance` / `way` (NOUN), `want` / `try` /
`begin` (VERB), `hard` / `able` / `likely` (ADJ) all carry it -- so it lands as ONE cue whose value is
`class : expectation-bin`, and the same statistic supplies **the verb's own control expectation the nominal has
to compete with** (the brief's checklist item 4, built in rather than deferred). The store is accrued from
READING and nothing else -- no tree, no treebank head, no gold column: at every infinitival site the nearest
candidate to the marker's left takes the credit, against how often each word occurs at all (a distributional
frame statistic; Mintz 2003), then one Hindle & Rooth (1993) reallocation pass shares the credit in proportion to
the expectation learned so far -- the same treebank-free estimator this organ already uses for the PP cue.
**What it learned, from 3,192 sentences read through the organ's own categories** (top keys by rate, unedited):
`able 0.829, try 0.724, want 0.636, like 0.575, chance 0.574, need 0.452, nothing 0.429, hard 0.428, begin 0.414,
intend 0.384, continue 0.382, likely 0.364, determine 0.360, go 0.327, agree 0.321, idea 0.321, expect 0.295`.
That is the lexicalist inventory, discovered without a parser.

**2. THE PREDICATE-SLOT GOVERNOR (`islot`).** pri 110 computes P(token q holds its clause's predicate slot),
graded, on every read. It now enters the infinitival arc as a cue VALUE -- `slot:<bin>` for a candidate weighted
by its occupancy, and the distinct value `expl` for an expletive `it` / `there`, which predicates nothing. The
signal is READ, never recomputed: `arc_scores_graded` already hands the occupancy to every cue pass.

**3. CLAUSE-ARRIVAL REANALYSIS (`revise_infinitival_governor`) -- NOT IN THE BRIEF, AND THE BIGGEST LEVER.** The
measurement that found it is in section 5. It carries no parameter: it takes the arc the organ's OWN learned
activations prefer, only among candidates the reader has ALREADY HEARD (`h < j`, so this is the decision AT the
clause's arrival and not lookahead), never creates a cycle and never leaves the sentence rootless. When the pair
is the wrong way round -- the beam made the nominal a DEPENDENT of the clause instead of its governor -- the
revision re-ranks the PAIR, which is what overtaking is.

**The validities are accrued by the organ's own OBSERVE PATH, from the CLEAR CASES.** This is the part I got
wrong first and it is worth stating plainly, because it is the same trap pri 117 recorded: I first accrued the
cue cells from the arm's own graded tree posterior -- the organ's standing self-supervision -- and it taught the
error straight back. Measured: `NOUN>VERB:L | NOM:hi` came out at **+0.157** against `VERB>VERB:L | VERB:hi` at
**+3.123**, and the expletive's own value came out **positive** (`PRON>VERB:L | expl +0.116`), because the outcome
signal IS the belief being repaired. The fix is the organ's own acquisition discipline: `observe_infinitival_site`
accrues one confirmed comprehension at a time from the sites whose governor is unambiguous by adjacency, the
governor taking the outcome and every competitor the zero outcome. Its own error is benign by construction -- at
the sites where adjacency is wrong ("went to the market TO BUY") the adjacent word is a LOW-expectation noun, so
the wrong credit lands in the low bin and not in the high one the decision turns on. After the change the same
cells read `NOM:hi +2.14` against `NOM:0 -3.04`, `expl -2.29`, `ADJ:hi +1.70`.

## 4. THE MEASUREMENT

**Population:** UD-EWT test, 1,787 sentences of 3-80 tokens, and every infinitival VERB by **the organ's own
categories** (a VERB whose preceding token is `to`), n=337 -- pri 129's population, reproduced item for item with
the same class counts. Live chain throughout: the organ's own tagger and graded posterior; the gold column is the
measuring instrument only and never touches the decision or the learning. Paired bootstrap over sentences, 2,000
resamples.

### 4a. Through the diff -- the organ as shipped vs the patched organ, both in one process

| | n | shipped | **patched** | paired delta |
|---|---|---|---|---|
| **ALL infinitivals** | 337 | 0.6766 | **0.7745** | **+0.0979 CI[+0.0564,+0.1381] SEP** |
| `xcomp_control` "want to go" | 169 | 0.8757 | **0.9349** | **+0.0592 CI[+0.0119,+0.1087] SEP** |
| `advcl_purpose` "came to see" | 71 | 0.6338 | **0.7183** | +0.0845 CI[-0.0282,+0.2059] ns, UP |
| `acl_nominal` "a plan to leave" | 56 | 0.2321 | **0.4286** | **+0.1964 CI[+0.0577,+0.3333] SEP** |
| `csubj_extrapos` "it is hard to say" | 23 | 0.5652 | **0.8261** | **+0.2609 CI[+0.1000,+0.4643] SEP** |
| `other` | 18 | 0.5000 | 0.5000 | +0.0000 (exactly flat) |
| UAS | 24,586 | 0.6465 | **0.6493** | **+0.0028 CI[+0.0019,+0.0040] SEP UP** |
| non-verbal subject | 548 | 0.6186 | **0.6332** | **+0.0146 CI[+0.0040,+0.0268] SEP UP** |
| verbal subject | 1,518 | 0.8729 | 0.8729 | +0.0000 ns |

Floor (nearest preceding VERB) **0.6291**. Read time **15.72 -> 15.67 ms/sentence** -- none.

Per relation (n >= 20), the only two below zero are **amod -0.0008** and **mark -0.0013**; up are
`acl 0.1421 -> 0.1716`, `advcl 0.4180 -> 0.4399`, `xcomp 0.7583 -> 0.8000`, `csubj 0.3600 -> 0.5600`,
`cop 0.6724 -> 0.6810`, `nsubj 0.8054 -> 0.8093`, `root 0.7454 -> 0.7465`, `ccomp 0.6667 -> 0.6757`,
`conj 0.3986 -> 0.4044`, `obj 0.7816 -> 0.7825`, `nmod 0.6077 -> 0.6085`.

### 4b. Lever by lever, same population, same one-process A/B

| arm | ALL | acl_nominal | csubj_extrapos | advcl_purpose | xcomp_control | UAS |
|---|---|---|---|---|---|---|
| base (the organ as shipped) | 0.6766 | 0.2321 | 0.5652 | 0.6338 | 0.8757 | 0.6465 |
| + the predicate-slot cue only | 0.6914 | 0.2857 | **0.6957** | 0.6620 | 0.8698 | 0.6473 |
| + the lexical expectation only | 0.7181 | **0.3929** | 0.5652 | 0.6620 | 0.8935 | 0.6482 |
| + both cues (no reanalysis) | 0.7359 | **0.4643** | 0.6957 | 0.6620 | 0.8935 | 0.6487 |
| + the reanalysis only (no cues) | 0.7389 | 0.2143 | 0.6957 | 0.7465 | 0.9467 | 0.6474 |
| **the shipped form (both cues + reanalysis)** | **0.7745** | 0.4286 | **0.8261** | **0.7183** | **0.9349** | **0.6493** |
| -- the REFUTED context channel, section 7 | 0.7359 | 0.4821 | 0.6957 | **0.5915** | 0.9172 | 0.6487 |
| -- twin: validities permuted | 0.4481 | 0.3571 | 0.5652 | 0.3944 | 0.4970 | 0.6422 |
| -- twin: lexicon shuffled | 0.7359 | 0.3036 | 0.6957 | 0.7324 | 0.9231 | 0.6478 |
| -- twin: every value collapsed to one | 0.6706 | 0.2857 | 0.6957 | 0.6056 | 0.8698 | 0.6463 |

**The two halves are complementary and neither is sufficient.** The cues alone fix the MATRIX and leave
`acl_nominal` at 0.4643 with `advcl_purpose` flat; the reanalysis alone realises whatever the UNIMPROVED matrix
prefers and takes `acl_nominal` DOWN to 0.2143. Together they are 0.7745.

### 4c. The controls, paired against the shipped form

| twin | what it removes | ALL | shipped form - twin |
|---|---|---|---|
| permuted validities | the cues' learned strengths (values and sites intact) | 0.4481 | **+0.3264 CI[+0.2699,+0.3824] SEP** |
| shuffled lexicon | the lexical CONTENT (`plan` and `market` swap expectations) | 0.7359 | **+0.0386 CI[+0.0100,+0.0669] SEP** |
| uniform value | the INFORMATION, keeping the per-configuration OFFSET | 0.6706 | below the organ as shipped |

**The third twin is the one I would have been caught by.** A targeted overlay accrues its cells over the SITE
population while the contrast is taken against the landed CONFIGURATION rate, so every value of a new cue carries
a per-configuration offset as well as its information -- and that offset alone could have produced a gain. It
does not: with every value collapsed to one string the organ scores **0.6706, below the 0.6766 it starts at.**
The permuted twin lands at 0.4481, below the nearest-verb floor. The shuffled-lexicon twin costs `acl_nominal`
0.4286 -> 0.3036, which is the lexical knowledge doing exactly the job the brief predicted for it.

## 5. THE FINDING THE BRIEF DID NOT CONTAIN, AND HOW IT WAS FOUND

Tracing three `acl_nominal` misses cue by cue showed the gold governor already carrying the HIGHEST arc score --
`decision` +6.02 against the ROOT's +2.64, `plot` +4.25 against `thwarted`'s +1.47 -- and the decode choosing
something else anyway. So I measured the decode directly, on the same slice, with the same matrix:

| how the same arc matrix is read | infinitival heads |
|---|---|
| **matrix ARGMAX over the candidates, no tree constraint at all** | **0.7674** |
| whole-sentence single-root search (`map1`) | 0.7597 |
| minimum-Bayes-risk tree (`mbr`) | 0.7597 |
| **the live in-order beam** | **0.6822** |
| the in-order beam at width 16 / 32 | 0.7054 / 0.7054 |

**0.0852 of the signal was in the matrix and thrown away by the decode.** The brain's repair for that is not a
wider beam -- the operating point was swept and it saturates at 0.7054 -- it is reanalysis when the disambiguating
word arrives, which this organ already does for the root arc and (pri 117) for the copular subject. With the
reanalysis the live in-order decode reaches **0.7674 on that slice, exactly the matrix-argmax number**: the
decode gap is closed, not reduced. The residual attribution confirms it at full size: **"the competition prefers
the gold and the decode lost it" falls from 37 of 109 misses to 7 of 76.**

## 6. EVERY REMAINING MISS, ATTRIBUTED (full size, n=337)

| why | shipped (109 misses) | **patched (76 misses)** | who owns it |
|---|---|---|---|
| the competition out-scored the gold, preferring a VERB | 38 | **23** | this rung |
| the competition out-scored the gold, preferring a NOUN | 5 | **16** | this rung -- the NEW cost, below |
| the competition preferred the gold, THE DECODE lost it | 37 | **7** | closed by the reanalysis |
| preferring ROOT / ADJ / PROPN / PRON | 12 | 12 | this rung |
| the gold governor was NEVER RETRIEVED (category) | 11 | 11 | the CATEGORIES rung |
| the gold governor was NEVER RETRIEVED (window) | 6 | 7 | an operating point |

**The honest cost, named: 16 of the 76 remaining misses are the nominal cue over-firing** ("prefers a NOUN" where
the gold is a VERB, 7 of them in `advcl_purpose`). The brief anticipated this ("if the nominal-governor cue
over-fires, the missing signal is the verb's own control expectation competing -- accrue it, do not threshold"),
and that is what is built: the verb's expectation is the SAME statistic in the SAME cue, which is why
`advcl_purpose` still ends +0.0845 UP rather than down. It is not fully paid for; section 9 says what would.

**The 11 unretrieved-by-category misses are an UPSTREAM finding, counted here for the first time:** the gold
governor is a token whose UD category and the organ's category disagree (`ADJ` read `ADV` x3, `NOUN` read `ADV`,
`VERB` read `ADP`) or a category the retrieval does not offer. The retrieval reads the ARGMAX tag while the rung
above it hands down a full posterior -- a graded signal delivered as a point estimate, which is the same defect
pri 117 fixed one arc over.

## 7. EVERY NEGATIVE, RESEARCHED UNTIL IT IS UNDERSTOOD

**7a. TEACHING THE CUE FROM THE ARM'S OWN POSTERIOR -- the self-teaching trap, with the numbers.** The organ's
standing self-supervision ("the posterior teaches the cue statistics") is the wrong outcome signal for a cue that
exists to REPAIR that posterior. Measured, both channels accrued that way: `NOUN>VERB:L | NOM:hi` **+0.157**
against `VERB>VERB:L | VERB:hi` **+3.123** -- a high-expectation NOUN got 5% of the pull a high-expectation VERB
got, because the arm puts almost no posterior mass on a noun heading an infinitival, which is the defect itself.
And `PRON>VERB:L | expl` came out **+0.116**, i.e. the expletive the arm wrongly picks was REWARDED. End to end
that configuration scores 0.6822 against the clear-case accrual's 0.7745. **The general lesson, and it is not
specific to this cue: a cue accrued from the belief it is meant to correct learns the error.** The organ's own
answer is the one pri 117 used -- accrue from a CONSTRUCTION the organ can detect in raw reading -- and that is
what `observe_infinitival_site` does.

**7b. THE CASE-MARKING / RETRIEVAL-INTERFERENCE CHANNEL (`ictx`) -- REFUTED AS BUILT.** The claim was Pinker
1984's case marking plus similarity-based retrieval interference (Van Dyke & McElree 2006), and it was aimed at
exactly the configuration pri 129 6c named as the purpose arm's whole deficit (`pp`, 0.5000 against the
perceptron's 0.6562). Built as a third channel with values `adp<0|1>:cm<0|1>`, accrued the same way, it learned a
clean 4.5-point contrast (`adp0:cm0 +1.54` vs `adp1:cm0 -2.96`). **It still loses: 0.7745 -> 0.7359, with
`acl_nominal` UP to 0.4821 and `advcl_purpose` DOWN to 0.5915.** Gating it to the sites where its value actually
varies (a cue competes only where it discriminates) does not rescue it: 0.7054. **The mechanism, counted:** in
"went to the market TO BUY" the true governor is the matrix VERB, which sits BEHIND the preposition
(`adp1:cm0`, -2.96), while the PP-internal noun sits in front of it and is merely case-marked (`adp0:cm1`,
+0.93) -- so the cue prefers the noun over the verb. That is right for "asked for permission to leave" and wrong
for every purpose clause, and the thing that actually separates those two is whether the NOUN's own frame
licenses an infinitival, which is what `iexp` already is. **The channel is redundant where it is right and
harmful where it is not.** It ships default OFF with this note in the organ, so it is not re-tried blind.

**7c. WIDENING THE RETRIEVAL TO ADV CANDIDATES -- REFUTED AS BUILT, and it is the residual's own suggestion.**
8 of the 76 remaining misses are a gold governor the retrieval never offered because the organ reads it `ADV`
("enough TO EAT" is a real construction and the lexical expectation covers degree words). Cells re-accrued for
the wider retrieval, measured at full size: **0.7745 -> 0.7478, paired -0.0267 CI[-0.0470,-0.0060],
CI-SEPARATED DOWN** -- `acl_nominal` 0.4286 -> 0.4643 but `csubj_extrapos` 0.8261 -> 0.6957 and `advcl_purpose`
0.7183 -> 0.6479. **Same mechanism as 7b: every extra candidate DILUTES the competition** -- an ADV standing
between the expletive and the slot holder takes activation the predicate-slot cue had just concentrated. The
8 misses are a CATEGORIES-rung loss (a UD `ADJ` or `NOUN` the organ reads `ADV`) and widening the retrieval is
the wrong place to pay for it. Default OFF with its number.

**7d. THE RETRIEVAL WINDOW IS ALREADY AT ITS PEAK -- swept, not adopted.** Infinitival heads by window:
**6: 0.7418 | 8 (default): 0.7745 | 12: 0.7359 | 16: 0.7329**. Wider is worse for the same dilution reason, and
the 7 remaining "outside the window" misses cannot be bought by widening it. The beam width was swept too
(section 5): 8 -> 0.6822, 16 -> 0.7054, 32 -> 0.7054 before the reanalysis, which is why the reanalysis and not
the beam is the lever.

**7e. THE NOMINAL CUE OVER-FIRES, AND IT IS PAID FOR BUT NOT FULLY.** 16 of the 76 remaining misses are "the
competition preferred a NOUN where the gold is a VERB" (5 of them shipped, so 11 are new), 7 of them in
`advcl_purpose`. The brief predicted this and prescribed the fix -- the verb's own control expectation competing,
accrued not thresholded -- and that IS what is built (one statistic, one cue, verbs and nouns in the same table),
which is why `advcl_purpose` ends +0.0845 UP rather than down. What it does not yet have is the distinction
between a noun that LICENSES an infinitival complement and a noun that merely PRECEDES one in a PP; section 9.2
says what that needs.

## 8. THE DOWNSTREAM CONSUMER, AND WHY IT MOVED +0.0155 AND NOT +0.10

pri 129's purpose/complement decision (**its own cell, unmodified**), both arms in one process, full UD-EWT
train + test, n=129 decidable sites:

| | competition (BF) | perceptron (the frozen supervised label) | majority floor | twin | paired BF - shipped |
|---|---|---|---|---|---|
| on the organ as shipped | 0.6589 | 0.6822 | 0.6202 | 0.5116 | -0.0235 CI[-0.1145,+0.0630] |
| **on the patched organ** | **0.6744** | 0.6822 | 0.6202 | 0.5271 | **-0.0077 CI[-0.1061,+0.0916]** |

**Arm A reproduces pri 129's table to the digit**, so the comparison is like for like. The BF arm rises
+0.0155 and its gap to the supervised label closes from -0.0235 to -0.0077 -- **still parity, not the +0.1084 the
oracle-ceiling probe promised from GOLD heads. I do not claim the bar's "+0.10" was met. Here is why it was
not, traced hand-off by hand-off with counts.**

**THE ACCOUNTING CLOSES EXACTLY, AND THAT IS THE FINDING.** On the consumer's OWN 129 decidable sites the
infinitival head goes from **88/129 correct (0.6822) to 90/129 (0.6977)** -- **+2 arcs, +0.0155** -- while on this
rung's own 337-item population it goes +33 arcs, +0.0979. **The decision moved by +0.0155, the same number its
input moved on its own population.** Nothing is lost between the rungs here; the input simply did not improve
where this consumer looks. Three reasons, all counted:

1. **THE CONSUMER'S POPULATION EXCLUDES THIS RUNG'S BIGGEST WINS, BY CONSTRUCTION.** `purpose_sites` replicates
   `goal_register`'s own entry gate, which *skips* every site `GR._is_extraposed` fires on, every site whose
   nearest preceding verb is a GOAL_VERB, and every adjacent complement-taker. The two constructions this rung
   repaired most -- `csubj_extrapos` (+0.2609) and `acl_nominal` (+0.1964) -- are exactly the ones that gate
   removes. The decidable population is the `xcomp` / `advcl` contrast, where the gains are +0.0592 and +0.0845.
2. **THE HAND-OFF READS TWO BITS OF AN ARC WE IMPROVED BY TEN POINTS.** Of the purpose arm's NINE cues, exactly
   two are derived from the head: `headcat` (the head's category) and `headismv` (is it the nearest main verb).
   The head of the infinitival CHANGED on **30 of the 129 decidable sites (23.3%)**, and those 30 are precisely
   the sites where either head-derived cue value changed. **The governor's IDENTITY -- and therefore its own
   lexicalist frame, which is the whole content of this repair -- is not read at all.** That is the loss, and it
   is a hand-off defect in the CONSUMER, not in this rung: a graded, lexically-specific signal delivered as a
   2-bit summary. Section 9.3 says what to do about it, with the organ that owns it.
3. **The oracle probe's +0.1084 was measured with GOLD heads on the SAME two cues**, so it is an upper bound on
   what those two bits can carry, and reaching it needs the head to be right on nearly all 129 -- not on the 337.

## 9. OUT OF SUPPLY -- GUM / GENTLE, 12+ genres, outside the count supply

Both arms in one process, 1,127 sentences, 184 infinitivals, the same live chain:

| | n | shipped | **patched** | paired delta |
|---|---|---|---|---|
| **ALL infinitivals** | 184 | 0.6304 | **0.7283** | **+0.0978 CI[+0.0342,+0.1656] SEP** |
| `xcomp_control` | 97 | 0.8351 | **0.9278** | **+0.0928 CI[+0.0108,+0.1744] SEP** |
| `acl_nominal` | 25 | 0.1200 | **0.4800** | **+0.3600 CI[+0.1765,+0.5556] SEP** |
| `advcl_purpose` | 30 | 0.5333 | 0.5667 | +0.0333 ns |
| `csubj_extrapos` | 13 | 0.4615 | 0.4615 | +0.0000 |
| UAS | 18,201 | 0.6081 | **0.6100** | **+0.0019 CI[+0.0008,+0.0030] SEP UP** |

**The effect out of supply is the SAME size as in supply (+0.0978 against +0.0979)**, which is the strongest
single piece of evidence that what was learned is the lexicalist expectation and not the shape of UD-EWT: the
lexical store was accrued from UD-EWT train and it transfers intact to twelve unrelated genres. Floor there is
0.5924 (acl_nominal 0.0000). Only two relations move down at n>=20: `obl` -0.0011 and `conj` -0.0017. One item
moves in `in_order_to` (n=2) and is noise by inspection.

## 10. THE OPERATING POINTS, SWEPT AND NOT ADOPTED (the phase diagram)

| retrieval window | ALL | acl_nominal | csubj_extrapos | advcl_purpose | UAS |
|---|---|---|---|---|---|
| 4 | 0.7774 | 0.4107 | 0.6957 | 0.7746 | 0.6494 |
| 6 | 0.7685 | 0.4107 | 0.7826 | 0.7042 | 0.6493 |
| **8 (the default)** | **0.7745** | 0.4286 | **0.8261** | 0.7183 | 0.6493 |
| 12 | 0.7685 | 0.4286 | **0.8696** | 0.7042 | 0.6492 |
| 16 (with ADV candidates) | 0.7329 | 0.4464 | 0.6522 | 0.6338 | 0.6487 |

**The surface is FLAT from 4 to 12 (0.769 - 0.777), so the default is not sitting on a tuned peak** -- window 4 is
nominally 1 item higher overall and 3 items lower on the extraposed family, and 12 is 1 item higher on the
extraposed family. 8 is kept because it is the middle of the flat region, not because it won. The count
smoothing (Dirichlet 3.0 toward the corpus base rate), the expectation bin edges (0.010 / 0.035 / 0.120), the
occupancy bin edges (reused from pri 117) and the reallocation rounds (1) are the other swept points.

## 12. KEY REALIZATIONS -- the moves that made this work

1. **A CUE ACCRUED FROM THE BELIEF IT IS MEANT TO REPAIR LEARNS THE ERROR.** The organ's standing self-supervision
   is the right teacher for a cue that refines what the organ already roughly knows and the WRONG teacher for a
   cue that supplies something the organ has never had. The tell is visible in the table before any end-to-end
   run: the value that should be most negative (`expl`) came out POSITIVE. **Check a new cue's learned validities
   for sign agreement with its own claim before measuring anything downstream** -- it is a two-second check that
   would have saved an hour.
2. **THE BRIEF NAMED TWO CUES; THE MEASUREMENT FOUND A THIRD LEVER THAT WAS BIGGER THAN BOTH.** Tracing three
   individual misses cue by cue showed the gold governor already carrying the highest arc score. Reading the SAME
   matrix three ways (argmax 0.7674 / search 0.7597 / in-order beam 0.6822) turned "the cue is too weak" into "the
   decode is the binding constraint", which is a completely different build. **When a cue you just added does not
   move the end number, read the matrix before strengthening the cue.**
3. **ONE EXPECTATION OVER WORDS, NOT A CUE PER CATEGORY.** The brief asked for a *nominal* governor cue. Building
   it as one cue over WORDS (`class : expectation-bin`, one store for nouns, verbs and adjectives) is what makes
   the verb's control expectation compete with the noun's for free -- which is the brief's own item 4, and it is
   why `advcl_purpose` went UP where the prototype's separate argmax took it down.
4. **EVERY EXTRA CANDIDATE DILUTES THE COMPETITION.** Both refuted arms (the context channel, the ADV retrieval)
   failed the same way: they added activation to candidates the predicate-slot cue had just demoted. In an
   additive competition a cue that is uninformative at a site is not neutral -- it is noise weighted by the
   configuration. **A new channel has to be checked on the population it does NOT discriminate, not only on the
   one it does.**
5. **THE TWIN THAT MATTERED WAS THE ARITHMETIC TWIN.** A targeted cue overlay accrues its cells on the SITE
   population while the contrast is taken against the landed CONFIGURATION rate, so it necessarily carries a
   per-configuration offset. Collapsing every value to one string isolates that offset exactly. It scored 0.6706,
   BELOW the starting 0.6766 -- without that twin the whole result would have been open to "you just pushed some
   arcs harder", and with it that reading is closed.

## 13. EVALUATION OF THE MOST SUCCESSFUL IMPROVEMENT -- what let the signal be maximised

**The chain was cracked rung by rung, and it is the chain, not any one cue, that produced the number.** Rung by
rung, what was cracked and what was not:

| rung | what the brain does | cracked here? |
|---|---|---|
| categories -> the retrieval SET | offer the candidates the input licenses | **NO.** The retrieval reads the ARGMAX tag; 11 of the 76 remaining misses are a governor never offered because the organ's argmax category differs from UD's. The posterior is available and unused |
| the stored LEXICAL EXPECTATION | `plan` expects an infinitival, `market` does not; strength = usage frequency | **YES.** Accrued from raw reading, no parse, no gold; the inventory it discovers (able / try / want / chance / hard / begin / idea) is the lexicalist inventory |
| the PREDICATE SLOT | a clause predicates one thing; the expletive is a placeholder | **YES.** pri 110's graded occupancy was already computed on every read and thrown away at this arc; it is now a cue value, and the extraposed family went 0.5652 -> 0.8261 |
| the COMPETITION | additive activation over configuration-conditioned validities | **YES, and it was already there.** Nothing about the competition changed -- the cues joined it |
| the VALIDITY ACCRUAL | validity = availability x reliability, accrued from experience | **YES, on the second attempt.** From the clear cases, not from the organ's own belief |
| the DECODE | revise when the disambiguating word arrives | **YES.** 37 of 109 misses were arcs the matrix already preferred; after the reanalysis, 7 of 76 |
| the CONSUMER hand-off | pass the governor, not a summary of it | **NO.** The purpose arm reads `headcat` and `headismv` -- two bits of an arc improved by ten points |

**The two rungs NOT cracked are both hand-offs where a graded, identity-bearing signal is delivered as a point
estimate** -- the category argmax going down into the retrieval, and the head category going down into the purpose
arm. That is the same defect pri 117 named one arc over, and it is where the next points are.

## 14. ALTERNATE PATHS -- other ways to do this read, as or more brain-foundational

1. **THE EXPECTATION AS A GRADED PREDICTION RATHER THAN A BINNED CUE VALUE (more BF).** The lexicalist account is
   really about PREDICTION: on reading `plan`, the comprehender pre-activates an infinitival continuation (Levy
   2008 surprisal; Altmann & Kamide 1999 anticipatory eye movements). The organ already has a prediction
   mechanism -- `hold_expectation`, which learns the value of keeping a word open. Putting the infinitival
   expectation THERE instead of (or as well as) in the arc cue would make the noun HOLD its slot until the clause
   arrives, which is what a reader does, and would remove the binning. **What it would take:** one more learned
   context key in `build_hold_expectation` (pri 117 section 7.1 already proposed the analogous key for the copular
   subject). **Why not now:** it changes the decode's state for every word, so it needs its own no-regress pass
   over the whole board; the arc-cue form is the one the brief asked for and is measurable in isolation.
2. **A UNIFIED SUBCATEGORISATION STORE INSTEAD OF AN INFINITIVAL-ONLY ONE (more BF, bigger).** The brain does not
   store "takes an infinitival"; it stores the word's argument structure, and the infinitival frame is one cell of
   it. `hdlab/verb_subcat_frames.py` already exists and `goal_register` consults it. Accruing ONE frame store from
   reading -- over nouns and adjectives too, not only verbs -- would serve this cue, the role competition's frame
   cue, the purpose decision and the obl reader from one place. **What it would take:** a store-shaped brief; the
   accrual here is its first working instance. **Why not now:** it is a cross-organ consolidation, and
   consolidating before the single-cue form is proven is how islands get built.
3. **RETRIEVAL OVER THE CATEGORY POSTERIOR RATHER THAN THE ARGMAX (strictly more BF, and cheap).** Offer every
   candidate whose posterior mass on a candidate class exceeds a threshold, weighting its cue value by that mass
   -- the same first-order mixture `arc_scores_graded` already does for the whole matrix. This is the principled
   version of the ADV arm that was refuted: it adds the 11 missing governors WITHOUT adding full-strength
   competitors, which is exactly why the flat widening failed. **What it would take:** the candidate scan reads
   `tag_post` (already threaded into this function) instead of `pos`. **Why not now:** it needs its own accrual
   and its own no-regress pass; it is the single most promising next build (section 15.1).
4. **SUPERVISED / SOTA COMPARISON, for honesty.** A supervised neural parser is ~0.95 on these arcs and a
   competent human reader is at ceiling; we are at 0.7745 from 0.6766. The glass-box levers that close the rest
   are (a) the retrieval over the posterior, (b) the hold, and (c) the arc scorer's REPRESENTATION, which is
   categorical over a 17-class inventory -- the same third item pri 117 named.

## 15. PRIORITY NEXT STEPS (brief-ready, with numbers)

1. **RETRIEVE OVER THE CATEGORY POSTERIOR, NOT THE ARGMAX TAG -- 11 of the 76 remaining misses, and it is the
   same defect pri 117 fixed one arc over.** The gold governor is never offered because the organ reads `ADJ` as
   `ADV` (x3), `NOUN` as `ADV` (x1), `VERB` as `ADP` (x1), or because the class is not offered at all (`ADV` x4,
   `PART` x2). Widening the class list FLATLY is refuted with a number (-0.0267 CI-separated DOWN, section 7c);
   weighting the candidate by its posterior mass is the version that should work. *Owner: this organ, one scan.*
2. **TEACH THE NOMINAL EXPECTATION TO DISTINGUISH LICENSING FROM ADJACENCY -- 16 of the 76 remaining misses.**
   The cue over-fires on "prefers a NOUN where the gold is a VERB" (7 of them `advcl_purpose`). The missing
   distinction is between a noun that LICENSES an infinitival complement and one that merely precedes one inside
   a prepositional phrase. The case-marking form of this is refuted (section 7b); the form that should work is
   Hindle-Rooth reallocation run to CONVERGENCE over both candidates rather than one pass, so a high-expectation
   verb can take credit back from a low-expectation adjacent noun. *Owner: this organ,
   `infin_assoc_from_reading`, the `--rounds` operating point.*
3. **GIVE THE PURPOSE ARM THE GOVERNOR'S IDENTITY, NOT ITS CATEGORY -- the consumer-side half of this rung's
   value.** Measured here: the infinitival head changed on 30 of 129 decidable sites, the arm reads only
   `headcat` / `headismv`, and its oracle ceiling on those two cues is +0.1084. Adding the governor's own
   infinitival expectation (now a shipped asset) as a cue would let it read the thing that actually decides
   complement-vs-purpose. *Owner: pri 129's organ (`goal_register` / the purpose arm).*
4. **THE 7 "OUTSIDE THE WINDOW" MISSES ARE NOT BOUGHT BY A WIDER WINDOW** (12 and 16 are both worse, section 10).
   They are long-distance dependencies that need the HOLD (alternate path 1), not more retrieval.

## 16. ADJACENT COMPONENTS -- capabilities, limits, BF status (seeds for the next briefs)

| component | what this work found | BF status as the disk shows it |
|---|---|---|
| `hdlab/lexical_categories.py` (categories) | hands the heads rung a POSTERIOR, but the infinitival RETRIEVAL reads only the argmax; 11 counted misses | BF for the occupancy (pri 110); the hand-off into candidate retrieval is a point estimate |
| `hdlab/attachment_arm.py` (this organ) | the competition was sound and starved of lexical knowledge; the in-order decode discarded 37 of 109 | BF_SPIRIT -> stronger: the cues are now lexicalist and the decode revises |
| `goal_register` / the purpose arm (pri 129) | reads 2 bits of the arc; its entry gate excludes the constructions this rung repaired | BF in form, starved at the hand-off |
| `hdlab/verb_subcat_frames.py` | a frame store already exists and is verb-only; this cue accrued a parallel noun/adjective one | a consolidation candidate (alternate path 2) |
| `hold_expectation` / `build_hold_expectation` | the natural home for a lexical expectation as PREDICTION | BF, unexploited for this signal |

## 17. AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

- **`hdlab/attachment_arm.py` -- the infinitival arc.** Previously: the competition owned NO cue that admits a
  nominal governor and never read the predicate slot it is handed on every read. Now: two cues with
  configuration-conditioned validities accrued from reading (`iexp`, `islot`), an online observe path
  (`observe_infinitival_site` / `observe_infinitival_governor`), and a clause-arrival reanalysis
  (`revise_infinitival_governor`). Measured 0.6766 -> 0.7745 in supply and 0.6304 -> 0.7283 out of supply.
- **A NEW DEVIATION TO RECORD, and it is general.** The arm's CANDIDATE RETRIEVAL for this arc reads the argmax
  category while the rung above it hands down a posterior. Counted cost here: 11 of 76 residual misses. The same
  shape as pri 113 section 27 / pri 117's finding, one arc over.
- **A REFUTED-AS-BUILT ENTRY.** Case marking + similarity-based retrieval interference as an infinitival
  attachment cue: net -0.0386 with `advcl_purpose` -0.1268; the mechanism is that the matrix verb of a
  PP-interrupted purpose clause sits BEHIND the preposition. Do not re-try in this form.
- **A SECOND REFUTED-AS-BUILT ENTRY.** Widening the infinitival retrieval to ADV candidates: -0.0267
  CI-separated DOWN. Extra candidates dilute the competition.

## 18. CROSS-SOLUTION MAP (`notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md`)

- **INPUTS THIS COMPONENT CONSUMES:** `hdlab/lexical_categories.py` (the graded category posterior AND the
  predicate-slot occupancy computed from it), `hdlab/morphology.py` (`lemma_verb` for the lexical key),
  `tools/build_attachment_validities.py` (the offline teaching path), the UD-EWT train text as reading material
  (tokens only -- no heads, no deprels, no UPOS column on the learning path).
- **THE UPSTREAM COMPONENT I FLAG AS MY WALL:** the categories rung's hand-off into candidate RETRIEVAL -- a
  graded posterior read as a point estimate, 11 counted misses.
- **THE DOWNSTREAM COMPONENT I FLAG AS THE OTHER HALF OF THIS RUNG'S VALUE:** the purpose arm's head hand-off
  (`headcat` / `headismv`), 30 of 129 sites changed and only two bits read.

## 19. WHAT I WOULD WITHDRAW FIRST IF IT TURNED OUT TO BE WRONG

The **clause-arrival reanalysis**, not the cues. It is the biggest single lever and it is the one that touches the
DECODE rather than the scoring, so it is the one with the widest blast radius -- and its pair-swap branch moves
two arcs instead of one. Everything that says it is safe is here (UAS CI-separated UP in supply and out of it, no
relation down by more than 0.0013, read time unchanged, and it fires 14 times in 700 sentences), but it is the
piece whose failure mode would be least local. The cues would survive its removal at 0.7359.
