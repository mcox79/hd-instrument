# Pre-reg: read_grow_reread_compounding_kgguided_v1

Phase-2 opener. Answers the USER's explicit question: "read one book, then read it
AGAIN -- do you gain any more knowledge? Is it a foundation you're building?"

## Question / mechanism
Re-reading the SAME text with the SAME deterministic extractor is bit-flat (identical
sentences -> identical edges). Re-reading can only compound if comprehension is
KNOWLEDGE-GUIDED: the foundation built earlier resolves constructions unextractable cold.
Accumulated knowledge = a GENUS VOCABULARY (nouns asserted as genus for >= T distinct
terms, 0 curated seed). Two COVERAGE-ADDITIVE constructions fire ONLY when their genus is
in that vocabulary (so they extract ZERO cold): KG_COREF (pronoun-subject copular resolved
to most-recent mention) and KG_APPOS (apposition "TERM, a GENUS, ...").

## Arms (ONE variable = re-read / knowledge-guidance schedule)
- (a) PASS-1 COLD: base Hearst extractor (COP + SUCH-AS), single pass. [REAL baseline]
- (b) PASS-2 GUIDED: 2nd pass, KG constructions ON (pass-1 vocab feeds back).
- (c) PASS-3 GUIDED: 3rd pass.
- (d) PASS-2 NAIVE: 2nd pass, KG OFF = deterministic-flat control; == pass-1 by construction. [REAL baseline]
- (e) FREQ-ONLY: predict global-majority genus for every held-out term. [REAL baseline / freq guard, per a9787ced]

## Metric
Held-out foundation quality on ~1000 glossary is-a gold pairs: correct-coverage
(fair paraphrase-robust WordNet genus-match, LENIENT = primary) AND extraction precision,
PER PASS. Held-out sections' prose NEVER read (genuine generalization). Reuses the
isa_growth_v1 (3d3e85592) harness: base extractor + `_wn_related` scorer + glossary gold.

## Bands (HYPOTHESIZED@ this file / cell BANDS; primary = held-out cov LENIENT)
- HARD_PASS: best-guided cov - cold >= 0.02 AND - naive >= 0.02 AND - freq >= 0.02
  AND best-guided prec >= cold prec - 0.05 AND KG fired on >= 5 held-out-relevant terms.
- HARD_FAIL_FLAT: best-guided - cold < 0.005 (flat) OR n_kg_edges == 0 (mechanism never fired).
- HARD_FAIL_FREQ_EQUIV: best-guided - freq < 0.005 (frequency-equivalent).
- else MIDDLE_BAND.

## Design-gate (verified at smoke BEFORE full)
1. REAL baselines: cold + naive-reread + freq-only (all present, distinct).
2. CAN-FAIL: HARD_FAIL if flat / freq-equivalent (a valid informative outcome; do NOT torture).
3. DIFFICULTY-ON: 170 held-out gold, prose never read, fair genus-match.
4. ONE variable: the re-read / knowledge-guidance schedule.
5. DISCRIMINATOR-FIRES: n_kg_edges_total > 0 (mechanism has opportunity).

## Prior work (honesty)
Genus-vocabulary-as-learned-category REDISCOVERS the self-bootstrapped concept-class set of
exp_read_grow_knowledge_guided_bootstrap_v1 (a9787ced, frequency-equivalent). NEW here:
coverage-additive KG_COREF/KG_APPOS constructions, explicit naive-reread control, freq-only
arm, compounding curve on the direct is-a foundation coverage of OpenStax Concepts-of-Biology.

## Compute
Sequential-CPU (regex / Perceptron POS / WordNet / dict accumulation; no matmul; tags cached
across passes). Storage = no_storage. Determinism: sorted() / hashlib only. CRLB n/a. Wall < 10s.
Local-runnable, foreground-to-completion, no external LLM. CLAIM-VET-pending.
