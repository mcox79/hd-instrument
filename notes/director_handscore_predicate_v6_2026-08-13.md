# Director hand-score: v6 predicate recovery sample (2026-08-13)

**Scorer:** Director, single judge, scored BLIND (arm labels not consulted; the sample ships
`scored: false` with no pre-assigned buckets). Sample:
`data/exp_definitional_predicate_v6/predicate_audit_sample.json` (n=50, seed 42, arm
`DEF_V6_PREDICATE`, arm n=250). Relations in arm: ENABLING_CONDITION 79,
ENABLING_CONDITION_AGENT 76, PROCESS_ACTION 49, PROCESS_PATIENT 46.

## SCOPE -- READ BEFORE THE NUMBER

This is a **NEW measurement on NEW relation types** (PROCESS_ACTION / PROCESS_PATIENT /
ENABLING_CONDITION / ENABLING_CONDITION_AGENT) over a **different corpus slice**. It is
**NOT comparable to the v5 64% figure** (`director_handscore_b3_v5_termboundary_2026-08-12.md`,
GROUNDED_MEANING genus facts) and must NOT be reported as an improvement or a regression against
it. `notes/STATUS.md` DO-NOT-REDO already flags cross-scoring against v5's 64% as an error.

It licenses only: **"predicate recovery on process definitions yields a correct action/condition
fact ~70% of the time on this corpus, single-judge."**
It licenses **NO** claim about the substrate LEARNING anything -- this is a hand-written parser
SUPPLYING facts.

## RESULT

| bucket | n | share |
|---|---|---|
| MEANINGFUL | 35/50 | **70%** |
| RELATED | 7/50 | 14% |
| NOISE | 8/50 | 16% |

- **MEANINGFUL (35):** 01,02,03,04,08,09,10,11,12,14,15,17,18,19,20,22,26,27,28,29,31,32,33,34,35,37,38,39,40,43,46,47,48,49,50
- **RELATED (7):** 05,13,24,30,41,42,44
- **NOISE (8):** 06,07,16,21,23,25,36,45

## WHAT WORKED

The predicate slot recovers the actual verb of the process, not a genus noun:

- [08] `catabolism --PROCESS_ACTION--> break`
- [22] `hemostasis --PROCESS_ACTION--> cease`
- [47] `transcription --PROCESS_ACTION--> copy`
- [48] `translation --PROCESS_ACTION--> synthesize`
- [32] `persuasion --PROCESS_ACTION--> change`
- [18] `encoding --PROCESS_ACTION--> get` + [19] `encoding --PROCESS_PATIENT--> information`
  (action and patient recovered as a pair from one definition)
- [27] `menopause --ENABLING_CONDITION_AGENT--> ovary`
- [39] `pupillary light reflex --ENABLING_CONDITION_AGENT--> light`

## DEFECT CLASSES (ranked)

### 1. TERM TRUNCATION RECURRENCE -- HIGHEST LEVER

Bare or partial heads banked as the term:

- [21] `form` -- should be **polyploidy** (definiendum surface: "other form of polyploidy")
- [36] `process` -- should be the **bone-development process** ("The process begins when
  mesenchymal cells in the embryonic skeleton gather together...")
- [41][42] `second-degree` -- truncated from "a second-degree or **incomplete block**"
- [44][45] `termination` -- where [44] is termination **OF THE SIGNAL** and [45] is termination
  **OF TRANSLATION**. Both bank under the same term string: now indistinguishable in the store.

This is the **SAME defect class as the v5 glossary term-boundary bug**, resurfacing in a
different pattern. The boundary logic should be fixed **ONCE, CENTRALLY**, not per-pattern.

### 2. NEGATION DROPPED -> INVERTED FACT -- MOST DANGEROUS

- [07] source: "The bystander effect is a phenomenon in which a witness or bystander **does not
  volunteer** to help a victim or person in distress." Banked as
  `bystander effect --PROCESS_ACTION--> volunteer`.

The stored fact **asserts the opposite of the source**. Nothing downstream can detect this.
Rare-but-poison: an inverted fact is strictly worse than a missing one.

### 3. WRONG ARGUMENT SELECTED

- [25] `lactation --PROCESS_PATIENT--> nipple` -- should be **milk**; taken from a trailing adjunct
  ("...in response to an infant sucking at the nipple").
- [16] `diffusion --PROCESS_PATIENT--> region` -- should be **material**; took an oblique
  ("material travels from regions of high concentration...").
- [45] `termination --ENABLING_CONDITION_AGENT--> uag` -- took a **parenthetical example**
  ("a nonsense codon (UAA, UAG, or UGA)") instead of the head **codon**.
- [13] `differentiation --PROCESS_PATIENT--> function` -- took the **purpose clause**
  ("to carry out distinct functions"), not the main clause.

### 4. FIRES ON NON-DEFINITIONS

- [23] `high death rate --ENABLING_CONDITION--> increase` -- extracted from a sheep-mortality
  **data description** ("a high death rate occurred when the sheep were between 6 and 12 months
  old, and then increased even more..."). Not a definition at all; and it grabbed a coordinated
  main verb from **outside** the when-clause.
- [06] `biochemical basis --PROCESS_ACTION--> precede` -- the term is wrong (should be
  **epistasis**, or nothing) and the verb came from a **deeply embedded relative clause**
  ("...a gene that precedes or follows it in the pathway").

### 5. MINOR: PASSIVE AGENT/PATIENT SLOT CONFUSION

- [30] `neurodevelopmental disorder --ENABLING_CONDITION_AGENT--> development`, where
  "development" is the **patient** of "is disturbed", not an agent.

## LIMITS

Single judge. Borderline calls:

- [05] `behavioral isolation --ENABLING_CONDITION_AGENT--> presence` -- syntactically correct head,
  but near-contentless.
- [24] `infection --ENABLING_CONDITION--> enter` -- faithful to the sentence, but misleading if
  banked as a general fact about infection (it is about one fluke life-cycle). A **context-scope**
  problem, not a parse error.
- [43] `sensory activation --ENABLING_CONDITION--> process` -- vague value.

Facts remain **UNBANKED** in `data/exp_definitional_predicate_v6/`. Growth is PAUSED and none of
these have entered any canonical foundation (`data/foundation/**` untouched).
