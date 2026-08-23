# WE PROPAGATE VALENCE ALONG AN AXIS MEASURED TO CARRY NONE OF IT

**2026-08-23, strategy session.** The `78`-point question from the abstention split: *why do a
verb's nearest WordNet neighbours disagree about good-and-bad?* **Because WordNet distance does not
encode good-and-bad at all** -- and the propagator's workhorse stage votes by exactly that distance.

---

## 1. THE MEASUREMENT

**HYPOTHESIS STATED BEFORE MEASURING:** WordNet's verb hierarchy is organised by ACTION TYPE
(troponymy -- "a manner of doing X"), not by the OUTCOME an action produces. `kill` and `cure` are
both things done to a living body. If so, `path_similarity` neighbours are ACTION KIN and valence is
orthogonal to the axis the propagator traverses.

**6,000 random verb pairs, 4,651 human-rated verbs:**

| | |
|---|---|
| Spearman(path_similarity, `abs(valence difference)`) | **`-0.0023`** |
| shuffled-null `abs(rho)` p95 | `0.0231` |
| verdict | 🔻 **INSIDE THE NULL -- no detectable relation** |

**AND THE BANDED VIEW IS BLUNTER THAN THE CORRELATION**, because a correlation can hide a threshold
effect and this one does not:

| path_similarity band | n | mean `abs(dV)` |
|---|---|---|
| `[0.00, 0.10)` | 252 | `1.406` |
| **`[0.10, 0.20)`** | 3,537 | `1.387` |
| 🔻 **`[0.20, 0.34)` -- WHERE THE PROPAGATOR ACTUALLY OPERATES** | **2,191** | **`1.410`** |
| **ALL PAIRS (the random baseline)** | 6,000 | **`1.393`** |

**FLAT. In the exact band the organ works in (`NEIGHBOR_FLOOR = 0.20`), two verbs agree about
valence no better than two verbs picked at random.**

---

## 2. THE INSTRUMENT CAN SEE VALENCE STRUCTURE -- IT JUST IS NOT ON THAT AXIS

**A null from an instrument that never showed it can detect the signal is not evidence of absence.**
Two positive controls, both required before the null above means anything:

| control | n | mean `abs(dV)` | vs random `1.393` | verdict |
|---|---|---|---|---|
| **ANTONYM pairs** -- must be LARGER | 648 | **`2.031`** | `+0.638` | ✅ instrument works |
| **SAME-SYNSET (synonym) pairs** -- must be SMALLER | 8,602 | **`1.063`** | `-0.330` | ✅ instrument works |

🔑 **SO VALENCE LIVES ON WORDNET'S *LEXICAL RELATIONS* -- SYNONYMY AND ANTONYMY -- AND NOT ON ITS
*TAXONOMIC DISTANCE*.** The gold is fine, the pairing is fine, and the structure does carry
good-and-bad. **Just not where we are reading it.**

---

## 3. WHY THIS MATTERS: THE WORKHORSE STAGE READS THE WRONG AXIS

The organ has two stages, and this splits them cleanly:

| stage | what it traverses | commits | accuracy |
|---|---|---|---|
| **A: antonym opposition** | a LEXICAL relation -- **measured to carry valence** | `19` | `0.8421` |
| 🔻 **B: sim-weighted neighbour vote** | **path distance -- measured to carry NONE** | **`307`** | `0.6482` |

**`307` of `326` commits -- 94% of everything the organ says -- come from the stage reading the
axis with no measured valence signal.** *The two stage accuracies were measured days apart from this
and independently; they line up in the direction this predicts.*

**AND THIS EXPLAINS THE `78` POINTS DIRECTLY.** Neighbours disagree because there is no reason for
them to agree: they are selected for being the same KIND OF ACTION, and the quantity being voted on
is not a property of action kind.

---

## 4. THE TENSION I CANNOT RESOLVE, STATED RATHER THAN EXPLAINED AWAY

⚠️ **Stage B still CLEARS its floor (`0.6482` on 307, and the whole-organ margin excludes zero at
every operating point).** If path distance carries no valence, where does that come from?

**I do not know, and I am not inventing a reason** -- the last time I explained an anomaly here, my
explanation predicted something checkable, failed, and had to be withdrawn.

**Candidates worth testing, none tested:** near-synonyms leaking into the high-similarity tail (the
one relation that DOES carry valence); an unbalanced anchor injecting a class prior; or valence
correlating with something that correlates with path position. *The `abs(dV)` measure is symmetric
magnitude, so it would also miss a relation that carries SIGN without carrying magnitude agreement
-- though the flat bands argue against that too.*

---

## 4b. RESOLVED THE SAME DAY -- AND IT QUALIFIES THIS NOTE'S OWN HEADLINE

I said I did not know why Stage B clears its floor and would not invent a reason. **It is none of
the three candidates, and the answer changes what the title above should say.**

**ALL THREE CANDIDATES ARE DEAD:**

| candidate | test | verdict |
|---|---|---|
| global class prior | the anchor is **26 POS / 26 NEG** | 🔻 dead at the source, one command |
| local imbalance | POS fraction of the IN-RANGE anchor set: mean `0.511`, median `0.512` | 🔻 dead -- no local skew |
| lexical leakage | only `114` of `1,971` items share a synset/antonym with an anchor; drop them ALL and the margin holds at `+0.0825`, CI `[+0.0034, +0.1684]`, n=291 | 🔻 dead |

**THE DECIDING CONTRAST -- STRIP THE SIMILARITY WEIGHTING AND KEEP ONLY MEMBERSHIP:**

| arm | committed | organ | floor | margin | CI95 |
|---|---|---|---|---|---|
| **REAL** (sim-weighted) | `309` | `0.6505` | `0.5469` | `+0.1036` | `[+0.0259, +0.1812]` |
| **BINARY** (every in-range anchor votes 1) | `241` | `0.6266` | `0.5602` | `+0.0664` | `[-0.0166, +0.1535]` |

🔑 **ON THE 234 ITEMS BOTH ARMS ANSWER, THEY AGREE 100% OF THE TIME.** The weighting **never changes
an answer.** What it changes is **which items get answered** -- and that is where the whole effect
lives:

| the 75 items REAL commits on and BINARY skips | |
|---|---|
| REAL accuracy on them | **`0.7200`** (54/75) |
| majority floor on them | `0.5067` |
| REAL accuracy on the overlap | `0.6282` |

🧠 **SO THE GRADED SIMILARITY IS NOT CARRYING VALENCE. IT IS CARRYING *ANSWERABILITY*.** It does not
tell you what the answer is; it tells you whether the anchor set is in a position to decide -- and
the words it picks out are genuinely easier ones (`0.72` against a near-chance `0.51` floor, the
strongest margin anywhere in this thread).

⚠️ **THAT QUALIFIES THIS NOTE'S HEADLINE AND I AM NOT LEAVING IT UNQUALIFIED.** "An axis that does
not carry it" is correct about **the answer** -- proximity does not predict WHICH pole, measured
flat across every band. It is **incomplete** about the mechanism: the same axis predicts **where a
confident answer is available.** Both statements are true and the second is the one that explains
Stage B.

*Reproduction note: my Stage-B reimplementation commits `309` where the shipped organ's Stage B
commits `307`. I did not chase the two-item difference; it does not move any conclusion here, and
saying so is better than implying an exact reproduction I did not verify.*

---

## 5. WHAT THIS ESTABLISHES, AND WHAT IT DOES NOT

- ✅ **ESTABLISHED:** WordNet path proximity between verbs carries **no detectable information**
  about valence agreement, inside the band the organ uses, with two working positive controls.
- ✅ **ESTABLISHED:** synonymy and antonymy DO carry it.
- ✅ **ESTABLISHED (section 4b, same day):** Stage B's residual signal is the similarity weighting
  acting as a SELECTOR, not a discriminator -- it never changes an answer (100% agreement with an
  unweighted vote on the 234 items both answer) but picks out 75 further items it answers at
  `0.7200` against a `0.5067` floor. **Proximity carries ANSWERABILITY, not valence.**
- 🚫 **NOT established:** that switching to lexical relations would work better. **That is the
  obvious next build and it is untested.** Antonymy reaches few words (Stage A commits `19` times).
- 🚫 **NOT** a claim about the ANCHOR+PROPAGATE hypothesis itself. *The idea that valence must be
  anchored and propagated is untouched; this is about WHICH STRUCTURE we propagate through.*
- 🚫 **NOT a landed cell** -- inline, `scratch/`, no `metrics.json`.

---

## TLDR

Last stretch I found the system stays silent mostly because the words it knows **disagree** about
whether a new word is good or bad. This asks why they disagree.

**They disagree because the map we are reading does not have that information on it.** WordNet
arranges verbs by what kind of action they are — `kill` and `cure` sit close together because both
are things you do to a living body — and being the same kind of action tells you nothing about
whether the outcome is good. Measured directly: two verbs that are close on that map agree about
good-and-bad **no better than two verbs picked at random**.

The map does hold the information, just somewhere else. Words listed as opposites are far apart in
good-and-bad, and words listed as meaning the same thing are close. Both checks came out right,
which is what makes the main finding trustworthy rather than a broken measurement.

The part that looked uncomfortable is now explained. 94 of every 100 answers come from the part
reading the uninformative axis, and it still beats guessing — because closeness on that map turns
out to tell you not *which* answer is right, but **whether a confident answer is available at all**.
Where it says it can decide, it is right 72 times in 100 against a coin flip; strip that judgement
out and keep everything else, and the answers never change — only which words get answered.

## QUESTIONS

None.

## NEXT STEPS

1. **The obvious build is to propagate along the relations that DO carry valence** rather than along
   distance. Untested, and its known weakness is reach: opposition links fire on 19 of 326.
2. **Explain Stage B's residual signal before building on it.** A mechanism that works for an
   unknown reason is not a foundation.
3. This does not touch the anchor+propagate idea itself -- only the structure chosen to propagate
   through.
