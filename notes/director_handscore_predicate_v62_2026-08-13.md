# Director hand-score: v6.2 predicate recovery sample (2026-08-13)

**Scorer:** Director, single judge, scored BLIND (the sample ships `scored: false`, `note:
"UNSCORED AND UNBANKED ... the v6.1 hand-score (40/2/8) is NOT carried over"`, no pre-assigned
buckets). Sample: `data/exp_definitional_predicate_v62/predicate_audit_sample.json` (n=50,
seed 42, arm `DEF_V62_PREDICATE`, arm n=221). Relations in arm: ENABLING_CONDITION 69,
ENABLING_CONDITION_AGENT 49, PROCESS_ACTION 48, PROCESS_PATIENT 39,
ENABLING_CONDITION_PATIENT 16.

## SCOPE -- READ BEFORE THE NUMBER

New relation types (PROCESS_ACTION / PROCESS_PATIENT / ENABLING_CONDITION /
ENABLING_CONDITION_AGENT / ENABLING_CONDITION_PATIENT) over textbook corpora, produced by a
**HAND-WRITTEN PARSER SUPPLYING facts**. It licenses only: **"predicate/condition recovery
yields a correct fact ~94% of the time on this corpus, single judge."**
It licenses **NO** claim that the substrate LEARNED anything.

**NOT comparable to any read-out hand-score** (those run at 2-3% MEANINGFUL): a read-out score
measures what the substrate can RECOVER from its own representation; this measures what a parser
HANDS IT. The two numbers are about different objects and must not be placed side by side
anywhere. Also **NOT comparable to the v5 64% figure**
(`director_handscore_b3_v5_termboundary_2026-08-12.md`, GROUNDED_MEANING genus facts);
cross-scoring against v5's 64% is already flagged as an error in `notes/STATUS.md` DO-NOT-REDO.

**BANKING STATUS (changed after this score was taken):** on the Director's ruling that this path
has reached firm ground, the 221 facts were banked into the **provenance-tagged** store
`data/foundation_provenance_v1/store` tagged `pipeline=DEFINITIONAL_EXTRACTOR` (7966 -> 8187
rows). The canonical store `data/foundation/reading_grounding_v1/` was **NOT** written -- its
per-file sha256 is identical before and after. The sample file's own `note` ("UNBANKED") predates
that ruling and is stale in that one respect. **No ISA/definitional (GROUNDED_MEANING) facts were
banked**, growth stays PAUSED.

## RESULT

| bucket | n | share |
|---|---|---|
| MEANINGFUL | 47/50 | **94%** |
| RELATED | 2/50 | 4% |
| NOISE | 1/50 | **2%** |

- **RELATED (2):**
  - **[08]** `cellular respiration --PROCESS_PATIENT--> energy` ("Cellular respiration is the
    process of making ATP using the chemical energy in glucose"). The patient of "making" is
    **ATP**; energy is the **instrument**. Topically right, role wrong.
  - **[27]** `irish potato famine --ENABLING_CONDITION--> become` -- the **correct main verb**
    (v6.1 took "grow" from the reduced relative), but semantically thin on its own.
- **NOISE (1):**
  - **[30]** `neurotransmitter release --ENABLING_CONDITION--> alter` ("Neurotransmitter release
    occurs when an action potential **travels** down the motor neuron's axon, **resulting in
    altered permeability** of the synaptic terminal membrane"). The predicate is taken from the
    **RESULT clause**, not the trigger clause. Correct answer: `travel`.
- **MEANINGFUL (47):** the other 47 rows.

**THE SOLE SURVIVING DEFECT CLASS: predicate taken from a result/consequence clause rather than
the trigger clause.** One row in fifty. It is the whole of the remaining NOISE.

## TRAJECTORY -- THREE SAMPLES, NOT A PAIRED DELTA (READ THIS CAVEAT FIRST)

| version | arm n | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|---|
| v6   | 250 | 35/50 = 70% | 7/50 = 14% | 8/50 = 16% |
| v6.1 | 228 | 40/50 = 80% | 2/50 = 4%  | 8/50 = 16% |
| v6.2 | 221 | **47/50 = 94%** | 2/50 = 4% | **1/50 = 2%** |

**These are THREE DIFFERENT SAMPLES drawn from THREE DIFFERENT FACT POPULATIONS (250 / 228 / 221
facts).** Same scorer, same rubric, same seed convention (42), same sampler object, same corpus --
but **NOT a paired re-score of identical rows.** Report each row as "the quality of THAT version's
output", never as a per-row delta and never as "+14 points".

The substantive reading, stated at that strength and no higher:

- **v6 -> v6.1 converted RELATED into MEANINGFUL** (14% -> 4% RELATED) while **NOISE stayed flat
  at 16%.** Those fixes moved borderline rows; they did not touch the error floor.
- **v6.1 -> v6.2 is the FIRST round to move NOISE (16% -> 2%).** That is the qualitatively new
  thing about this version, and it is what the "firm ground" ruling rests on.

## THE FIXES THAT BOUND (v6.2 sheet rows, and the v6.1 rows they answer)

From `defect_recheck.json` (the exact source sentences the earlier hand-scores flagged):

- **[19]/[20] v6.1** `pathway's` / `end` -> now `(feedback inhibition, ENABLING_CONDITION,
  inhibit)` + `(feedback inhibition, ENABLING_CONDITION_AGENT, **product**)`. The possessive
  fragment is gone AND the real predicate "inhibits" is recovered instead of the noun "end".
- **[27] v6.1** `interesting example of ecosystem dynamics` -- **REFUSED**
  (`TERM_DISCOURSE_FRAME_TERM`). A discourse phrase is no longer minted as a concept.
- **[34] v6.1** `photosynthesis --PROCESS_ACTION--> like` -- **REFUSED** (`SLOT_TYPE_MISMATCH`,
  detail `PROCESS_ACTION|like|PREPOSITION_IN_VERB_SLOT|like`).
- **[32] v6.1** `osmotic regulation --PROCESS_ACTION--> salt` -> now `(osmotic regulation,
  PROCESS_ACTION, **keep**)` with `salt` correctly demoted to `PROCESS_PATIENT`.
- **[46] v6.1** `tragic irish potato famine --...--> grow` -> term stripped to **`irish potato
  famine`**, verb corrected to the main verb `become` (v6.2 sheet **[27]**).
- **[08] v6.1** `cellular respiration --PROCESS_PATIENT--> convert` (verb in a noun slot) --
  the PATIENT is now refused (`VERB_FORM_IN_NOUN_SLOT|stored`) and only the correct
  `PROCESS_ACTION convert` is emitted.
- **v6.2 sheet [25]** `incomplete block --ENABLING_CONDITION_AGENT--> impulse` -- term correct
  (v6 banked `second-degree`).
- **v6.2 sheet [44]/[45]** `termination of translation` -- term correct and distinct from
  `termination of signal` (v6 collapsed both to `termination`).

## MEASUREMENT CORRECTION -- THE DIRECTOR'S ARITHMETIC WAS WRONG

The Director extrapolated **~13 corpus-wide slot-type errors** from 3 sample rows. The true
population is **~4**: `metrics.json` reports `refusal_reason_mix.SLOT_TYPE_MISMATCH = 4`
(`VERB_FORM_IN_NOUN_SLOT` 3, `PREPOSITION_IN_VERB_SLOT` 1). The extrapolation over-counted
because `salts` and `like` have **BOTH noun and verb readings in WordNet** and are therefore
**invisible to a type check** -- they were fixed by the **main-verb rule**, not by the slot-type
gate. **The gate is not narrow; the estimate of what it had to catch was wrong.** Deflate the
"slot type is the highest lever" claim accordingly.

## MACHINE-SIDE CHECKS (off disk)

- `defect_recheck.json`: **21/21** tracked defect rows (8 v6.1-NOISE + 13 v6-tracked) --
  `n_still_reproducing_the_prior_fact = 0`; **7 refused outright**.
- **183 refusals** over 180 distinct sentences (`n_refusals_total = 183`). Mix:
  NO_VERB_IN_OWN_CLAUSE 85, TERM_ANAPHORIC_SUBJECT 44, TERM_NOT_NOMINAL 29, D2_NEGATION_IN_SCOPE 4,
  SLOT_TYPE_MISMATCH 4, D1_BARE_CATEGORY_HEAD 3, D3_PATIENT_OBLIQUE 3,
  D3_PATIENT_PURPOSE_ONLY 3, TERM_DISCOURSE_FRAME_TERM 3, D3_PATIENT_NO_NOMINAL 2,
  TERM_EMPTY_CUT 2, D4_NON_DEFINITIONAL_CONTEXT 1.
- **Four non-CALLED ISA pattern hashes UNCHANGED** by this cell (APPOSITIVE, COPULA,
  GLOSSARY_COLON, REFERS_TO -- current digests identical to the same module with this cell's 4
  sentinel-delimited blocks reverted). **CALLED is EXCLUDED from the claim**: a concurrent agent
  owns and is editing that branch, so its digest can move for reasons that are not this cell's.
- Live module sha256 stable at start and end of the run; shared-module self-test PASS.

## LIMITS

Single judge, n=50, one corpus family (OpenStax BIO / ANAT / PSY). 94% is the quality of the
facts this parser EMITS, after 183 refusals -- it says nothing about coverage of the sentences it
declined, and nothing about whether the substrate can use any of it.
