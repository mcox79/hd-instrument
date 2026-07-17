# litbank_ic_derived_v1 -- provenance

## Source
- LitBank coreference layer: https://github.com/dbamman/litbank, `coref/conll/*.conll`
- Pinned commit: `3e50db0ffc033d7ccbb94f4d88f6b99210328ed8`
- License: CC BY 4.0 (see LICENSE.txt)
- LitBank annotates the coreference/entity/event layers on (per the LitBank paper)
  roughly the opening portion of each of 100 public-domain English-language novels
  (mostly pre-1923 Project Gutenberg texts) -- NOT the full novel text. This is a
  real, load-bearing scale constraint for anything mined from this corpus (see below).

## Books scanned (all 100 currently published in coref/conll at the pinned commit)
See `mining_rule_version` + `books` field inside `litbank_ic_disagreement_derived_v1.json`
for the exact list (multi-author: Austen, Dickens, the Brontes, Twain, Melville, Conrad,
Stoker, Shelley, Hardy, Eliot, Wells, James, Montgomery, Haggard, Joyce, and more).

## Mining rule (declared, structural, run BEFORE any disagreement/agreement split was
inspected for outcome -- see `tools/derive_litbank_ic_disagreement_v1.py`, version
`v1_because_he_she_2candidate`):
1. Per sentence, find the first causal connective in {"because", "for"} ("since"/"as"
   excluded -- too often temporal, would dilute the causal-explanation frame this
   phenomenon requires per Kehler/Rohde's coherence-relation-dependent IC literature).
2. The token immediately after the connective must be "he" or "she" (subject-position
   3rd-person-singular pronoun -- the classic implicit-causality test frame).
3. NP1 = the coreference mention (from LitBank's own human annotation) nearest to,
   and wholly before, the causal-verb token (nearest-preceding-mention heuristic,
   a structural proxy for "the local subject NP", not outcome-tuned).
4. NP2 = the nearest mention wholly between the verb and the connective (structural
   proxy for "the local object NP").
5. NP1 and NP2 must be DIFFERENT coreference clusters (a genuine 2-candidate case).
6. The pronoun itself must be an annotated coreference mention (real gold -- LitBank's
   own human-verified antecedent, not a norm or an assumption), and its gold cluster
   must equal EITHER NP1's or NP2's cluster (gold-determinable against exactly these
   two candidates -- the canonical implicit-causality test frame).
7. The verb spanning NP1..connective is classified EO (Experiencer-Object,
   "frighten"-class, NP1/subject-bias) / ES (Experiencer-Subject, "love"-class,
   NP2/object-bias) / NEUTRAL (no established IC bias -- a guardrail/negative-control
   class) via the glass-box lexicon declared in the same script (~65 verbs total),
   CITED from: Garvey & Caramazza 1974 (Linguistic Inquiry); Brown & Fish 1983
   (Cognition); Rudolph & Foersterling 1997 (Psychological Bulletin meta-analysis);
   Kehler, Kertz, Rohde & Elman 2008 (J. Semantics). Categorical bias direction only
   (no invented per-verb percentages).

## MEASURED YIELD (disclosed, not hidden -- this is a real, load-bearing finding, not
a mining bug): scanning ALL 100 books' LitBank-annotated openings (~200K tokens total)
for this exact frame found 5 candidate items TOTAL, and ALL 5 landed in the NEUTRAL
(no-established-IC-bias) verb class -- ZERO EO or ES (i.e. zero genuine
verb-bias-vs-recency DISAGREEMENT or agreement) hits. A supplementary cross-sentence
relaxation (IC/neutral-verb clause followed by its OWN sentence starting "For he/she",
a common 19th-century full-sentence causal connective) was also checked and found only
2 more hits, both NEUTRAL-class. CONCLUSION (disclosed in the experiment cell's
pre-reg, not papered over): the exact "IC-verb + causal-connective + immediately-
adjacent subject-pronoun + clean 2-candidate-mention" frame this phenomenon requires
is GENUINELY RARE within LitBank's ~200K-token annotated sample -- consistent with why
the psycholinguistics literature studies implicit causality via elicited completion-
norming experiments rather than corpus frequency counts. This real-corpus arm is
therefore used in the experiment cell as a DISCLOSED, HONEST NEGATIVE/SCARCITY check
(real_data_sufficient gate) and as a genuine zero-hallucination guardrail measurement
(the 5 real NEUTRAL-class hits, scored for whether the verb-semantic mechanism
correctly ABSTAINS rather than guesses) -- NOT as the sole vehicle for the disagreement-
subset capability claim (that rests on the constructed IC minimal-pairs arm, explicitly
flagged as construction-validated / not independent capability evidence, per the
project's construction-artifact-disclosure convention).
