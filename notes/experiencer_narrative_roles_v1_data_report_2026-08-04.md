# Experiencer-Rich Narrative Role Dataset v1 — Data Report (2026-08-04)

**Dataset:** `experiments/data/experiencer_narrative_roles_v1.jsonl` (118 records)
**Builder (reproducible):** `experiments/build_experiencer_narrative_roles_v1.py`
**Miner (candidate extraction):** `experiments/mine_experiencer_sentences_v1.py`
**Raw candidate dump:** `notes/_mined_psych_candidates_raw.json`

## Purpose
Unblock the thematic-role labeler + OOV verb-frame induction (a97adc45) on EXPERIENCER-SUBJECT
and EXPERIENCER-OBJECT psych-verb constructions, which are ~absent in the McGuffey gold
(`data/gold_mcguffey_lccp_argstruct_v1.json` classifies psych/cognition verbs as `nopat` — thin
by construction, not a bug) and thin elsewhere. Real-narrative genre; non-circular, human-verifiable gold.

## Sources on disk (inventory — WIRE-DON'T-ISLAND, nothing re-sourced externally)
- **VerbNet** — available via NLTK local data (`nltk.corpus.verbnet`, 429 classes) incl. psych classes
  `admire-31.2`, `amuse-31.1`, `long-32.2`, `marvel-31.3`, `want-32.1`, `appeal-31.4`, `wish-62`.
  Used as SUPPLIED KNOWLEDGE to seed the subj-exp vs obj-exp verb split.
- **WordNet** — available via NLTK local data (117,659 synsets) — backup emotion/cognition lemmas.
- **litbank** — `data/litbank/original/*.txt`, 100 full public-domain 19th/20th-c. novels
  (Jane Eyre, Middlemarch, Wuthering Heights, Frankenstein, Pride and Prejudice, Dracula, etc.).
  This is the mining corpus (right genre = real narrative prose).
- Existing schema reference: `experiments/data/srl_corpus_thematic_roles_v1.jsonl` (36 lines) — matched.
- **No external download used.** Internet was reachable but on-disk resources sufficed.

## What was built
- **67 distinct psych verbs** — **36 experiencer-SUBJECT** (subj = EXPERIENCER: fear, want, love, hope,
  dread, long, wish, admire, adore, envy, pity, loathe, cherish, crave, yearn, grieve, mourn, regret,
  miss, trust, doubt, marvel, wonder, rejoice, fret, esteem, despise, relish, enjoy, value, abhor,
  resent, covet, revere, pine, desire) and **31 experiencer-OBJECT** (subj = STIMULUS, obj = EXPERIENCER —
  the hard case that breaks the subject=agent positional heuristic: frighten, please, anger, delight,
  amuse, astonish, annoy, terrify, alarm, surprise, disgust, shock/horrify, startle, comfort, console,
  disturb, vex, charm, fascinate, interest, irritate, enrage, offend, perplex, puzzle, distress,
  displease, embarrass, gladden, torment, soothe).
- **118 sentences**: **100 mined verbatim from litbank**, **18 naturalistic supplements**
  (flagged `source="supplement"`), added only to fill rarer constructions (PP-complement `long for`,
  some passives, causative obj-exp with an overt stimulus) where clean in-corpus instances were sparse.

## Construction variety (yes)
transitive 43, exp_obj_active 31, exp_obj_passive 22, clausal_complement 10, pp_complement 7,
infinitival_complement 2, intransitive 2, ditransitive 1. Both experiencer-object *active*
("It frightened me") and *passive-with-stimulus* ("He was amused by her conversation") are represented,
plus clausal ("I fear his wits were touched") and PP ("she longed for...", "marvelled over...").

## Gold-labeling method — NON-CIRCULAR (yes)
Roles: EXPERIENCER, STIMULUS, THEME (propositional/content complement), AGENT, PATIENT, RECIPIENT.
Each argument's role was assigned by the annotator (glass-box agent) READING the sentence and writing
the TRUE thematic role, **independent of any positional heuristic** (subject != agent here — for
experiencer-object verbs the SUBJECT is the STIMULUS and the OBJECT is the EXPERIENCER) and
**independent of the labeler under test** (no labeler output was consulted). VerbNet class membership is
supplied knowledge that seeds the subj/obj split, but every sentence was individually checked to confirm
it actually instantiates the psych construction (not an adjectival / nominal / idiomatic use) and each
head's role was verified against sentence meaning. Held-out gold is thus verifiable from the sentence
alone (e.g. "in *It frightened me*, ME is unambiguously the experiencer"), so induction is tested on
predicting role from CONSTRUCTION against an independent ground truth.

## Human verification (self spot-check, >=25 sample)
Re-read an independent 30-record sample. **Pre-fix: 28/30 = 93.3% correct.** Two errors found and FIXED:
(1) "His evident distress excited all my compassion" — *distress* is a NOUN there (main verb *excited*),
not a psych-verb instance → replaced with a genuine verbal *distress* sentence.
(2) "She fretted him to the bottom of his soul" — *causative* use (him = experiencer, she = stimulus),
mis-tagged as subject-experiencer → replaced with a clean subject-experiencer *fret* ("you begin to fret
about your feeling"). **Post-fix: 30/30 = 100% on the re-checked sample.**

## Lemma-level split (ready — yes; zero train/heldout lemma overlap)
Recommended **held-out lemmas (10, spanning BOTH types)**: subj-exp = cherish, crave, dread, loathe,
yearn; obj-exp = astonish, embarrass, gladden, horrify, terrify. Each held-out lemma has >=2 sentences
(dread 3, loathe 3, astonish 3; others 2). No held-out lemma appears in train. Anti-memorization: surface
forms vary within and across verbs; held-out verbs are entirely distinct lemmas from train, so induction
must generalize the CONSTRUCTION, not memorize a verb.

## Per-corpus provenance (mined records)
Sentences drawn across many novels incl. Jane Eyre, Middlemarch, Wuthering Heights, Frankenstein,
Pride and Prejudice, Dracula, Of Human Bondage, Sister Carrie, Little Women, Vanity Fair, Sons and Lovers,
The Picture of Dorian Gray, Tess of the d'Urbervilles, North and South, King Solomon's Mines, and others
(the `source` field on each record carries the exact `litbank:<novel_id>`).

## Honest caveats
- 18/118 records are hand-authored supplements (clearly flagged); the experiencer-OBJECT *active with an
  overt lexical stimulus subject* ("The roar terrified the horses") and clean PP-complement subj-exp
  ("long for", "yearn for") are the constructions most reliant on supplement — genuinely rarer in-corpus
  as clean short sentences (most in-corpus obj-exp hits are the *-ed passive/adjectival* form). This is a
  real finding: object-experiencer ACTIVE voice with a concrete stimulus subject is less frequent in prose
  than the passive/participial "X was frightened" framing.
- Some sentences were lightly trimmed (leading/trailing clause) from the mined original for a clean
  single-clause item; the psych clause itself is verbatim.
- Counts are 1–3 sentences/verb (breadth over depth) — sufficient for a lemma-level split but the
  build may want to expand sentences-per-held-out-verb before a high-power eval; the miner + raw dump
  make that a cheap extension.
