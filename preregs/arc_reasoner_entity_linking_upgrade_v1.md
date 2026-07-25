# Pre-reg: ARC reasoner entity-linking upgrade v1

- **Cell:** `experiments/exp_arc_reasoner_entity_linking_upgrade_v1.py`
- **Capability wired:** `hdlab/reasoner.py` DerivationReasoner `link_mode` front-end entity-linker
- **Rules:** `data/rules/arc_science_typed_rules_v1.json` (233 science-precise typed rules, key `rules`)
- **Contract:** INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic; VET-PENDING; no atom banking.
- **Anchor:** `arc_reasoner_entity_linking_upgrade_v1` | seed 20260725

## Question
The composed DerivationReasoner emits correct selective glass-box traces but fires on only ~11% of ARC-Challenge because the question-word -> rule-entity bridge is a strict GloVe cos>=0.85 match (too thin/strict to cross paraphrase). Rules are valid + cover the content; the gap is the LANGUAGE bridge. **Can an entity-linking upgrade raise DEMONSTRATED reasoning-coverage WITHOUT sacrificing selectivity?**

## Design (one variable across arms = the entity-LINK MODE)
Rules / typed graph / meet-in-middle search / decision are IDENTICAL across arms. Only the question-word->node linker changes:
- `glove` (BEFORE baseline): strict GloVe cos>=tau_unify (0.85) only.
- `lemma`: + TIGHT symbolic bridge -- morphy lemma / raw-token EXACT match to node-label lemmas (rocks<->rock). No hypernym spread.
- `lemma_syn`: + WordNet SAME-SYNSET single-token synonyms (rock<->stone). Multi-token / apostrophe / proper-noun lemmas dropped.

**Upgrade-arm selection (GUARDRAIL-FIRST, pre-registered, not tuned):** upgrade arm = higher-coverage of {lemma, lemma_syn} that keeps distractor-derive-rate <= SELECTIVITY_CEIL. If neither keeps selectivity -> that IS the loss-of-selectivity failure.

## Metrics (reported per mode; coverage AND selectivity together)
- `coverage_fraction` = fraction of questions with >=1 derivable candidate.
- **SELECTIVITY** `distractor_derive_rate` = fraction of the 3 wrong choices that become derivable (GUARDRAIL).
- `gold_derive_rate` = fraction of questions whose GOLD choice is derivable.
- `derived_subset_acc` vs `derived_subset_baseline_acc` = reasoner (derivation-mode decisions) vs similarity baseline on the SAME derived subset.

## Pre-registered bands (fixed BEFORE run; reported STRAIGHT)
1. `coverage_rises_ge_0.05` : coverage(upgrade) - coverage(glove) >= 0.05 absolute.
2. `selectivity_preserved_le_0.13` : upgrade distractor-derive-rate <= 0.13 (~2x the 0.063 baseline).
3. `gold_reachability_rises_ge_0.03` : gold-derive(upgrade) - gold-derive(glove) >= 0.03.
4. `derived_acc_ge_baseline_and_gt_chance` : derived-subset acc >= similarity baseline on same subset AND > chance.

## Verdict logic (CAN-FAIL, HONEST-NEG pre-registered)
- **REASONING-COVERAGE-RISES-SELECTIVE (PASS):** selectivity preserved AND bands 1,3,4 all pass.
- **HONEST-NEG-coverage-meaning-bound:** coverage rise < 0.03 (stuck) OR selectivity lost (distractor-derive-rate > 0.13). Isolates the finding: the question-language->rule-entity bridge needs GROUNDED MEANING (the #1 wall); reasoning-coverage is meaning-bound.
- **MIDDLE:** otherwise (e.g. coverage rises selectively but decision-correctness does not clear the bar).

## Held-out / anti-leak
Full ARC-Challenge test (1172 questions). The 233 rules are science facts NOT derived from test labels; `distractor_derive_rate` is the anti-leak selectivity check.

## Discriminator-fires (smoke, n=60)
glove cov 0.150 -> lemma_syn 0.233 (d=+0.083); distractor 0.073 -> 0.107 (<=0.13). Discriminator FIRES + is selective; baseline in-band (not saturated). `lemma` == `glove` at smoke (GloVe already catches morphology) -> the lever is SYNONYM bridging.

## Compute architecture
Sequential-CPU (justified): graph 215 nodes / 209 edges (tiny; not matmul-heavy at scale); GloVe encodings cached across modes on a single shared reasoner; wall < 10 min foreground. No GPU batching warranted. Storage: no_storage / no_composition (rule-graph reasoning, not vector-store composition).

## CELL-TEMPLATE
except SystemExit before except Exception (no BaseException); atomic metrics (tmp+os.replace); start-marker; crash-diag; heartbeat; self-test builds the REAL DerivationReasoner over a hand rule-set (GloVe-free FakeBase) + exercises all 3 link modes + evaluate + the real rules loader (real_code_path). All numbers MEASURED@ this run.
