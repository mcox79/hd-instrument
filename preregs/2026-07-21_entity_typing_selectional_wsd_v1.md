# Pre-reg: entity_typing_selectional_wsd_v1

Filed: 2026-07-21 (exp_dev). LOCAL-ONLY, foreground-to-completion, no push.

## Question (DIRECTIONAL GATE, properly powered)
Does enriching verb-sense disambiguation with the ARGUMENT NOUN's semantic TYPE
(WordNet supersense/lexname of the object) yield a STATISTICALLY SIGNIFICANT
improvement in correct verb-sense assignment over a type-level MFS baseline that
ignores the argument -- the significance the N=31 hand-gold WSD gate (atom 29434)
could NOT establish (aggregate lift statistically NULL, McNemar p~0.6)?

## Build-on
- atom 29434 (WSD frame+selectional gate): frame-matching ALONE nets ZERO;
  selectional restriction (filler noun's semantic type) supplies the lift; but
  N=31, aggregate NULL. THIS cell fixes the power problem.
- atom 29420 (WordNet-noun-type KB): supersense/animacy typing of noun heads.
- Eval corpus: NLTK SemCor (WordNet-sense-tagged, LOCAL). MEASURED coverage below.

## Design (ONE VARIABLE)
- Population: polysemous verb instances (>=2 WordNet senses, gold reachable) from
  SemCor. Deterministic 80/20 split by sentence index (test = idx % 5 == 0).
- Feature: object noun = nearest following gold-tagged noun within window 6; its
  supersense (lexname) is the entity TYPE.
- Model (count-based, learned from TRAIN, glass-box, no external LLM):
  - baseline (entity-typing OFF): argmax_s log P(sense | word)         [MFS prior]
  - mechanism (entity-typing ON): argmax_s log P(sense|word) + log P(obj_lex | s)
  - ONLY difference = the selectional term log P(obj_lex | s). Shared prior, shared
    candidate pool, shared parse. lambda=1 (principled Bayes weight, NOT tuned).
- Primary population = TEST items WITH an object noun (mechanism is active there).
  Secondary = all polysemous test (diluted by no-object items where mech==baseline).
- Primary metric = fine-grained WordNet sense accuracy. Secondary = verb lexname
  accuracy (coarse "who-is-affected"-adjacent).

## Must-fail control
Scramble the object-noun -> supersense map at TEST-lookup only (global random
permutation of noun lexnames; trained table left TRUE), so the type is
decorrelated from the sense. Multi-seed (20 full / 5 smoke) -> sigma-over-scramble.
Applied at test-lookup (NOT a consistent relabeling, which would be a
model-preserving bijection). PROT-023: fixed int seeds, sorted() lexname order.

## MEASURED feasibility (pre-build probe, off SemCor)
- 88,084 verb instances; 83,621 polysemous with gold reachable.
  MEASURED@probe 2026-07-21.
- Object-noun supersense coverage = 0.395 (nearest-following-noun w/in window 6).
  NOT a blocker: WordNet lexname covers 100% of in-WordNet nouns; 39.5% of verb
  instances HAVE an in-window object at all. MEASURED@probe.
- TEST split: 16,642 polysemous test instances; **6,616 with an object** (primary
  population; N in the thousands -> properly powered). MEASURED@probe.
- MFS baseline accuracy = 0.595 (in-band, real headroom). MEASURED@probe.

## Bands (declared BEFORE run)
- baseline_in_band (META_RULE_AG): 0.05 < baseline_sense_acc < 0.95. Expect ~0.6.
- discriminator_fires (META_RULE_K): n_flips > 0 AND n_discordant (McNemar b+c) > 0.
- **HARD_PASS** (all of): real_gain > 0.01 AND McNemar exact p < 0.01 AND
  sigma_over_scramble >= 2.0 AND scramble_gain <= 0.30 * real_gain.
  (= a real, powered, scramble-confirmed entity-typing lift; strictly above the
  gain=0 floor per META_RULE_L.) Tier = MEASURED_MECHANISM.
- **HARD_FAIL** (any of): real_gain <= 0 (entity-typing does not beat MFS; residual
  is world-knowledge not type) OR McNemar p >= 0.05 (not significant) OR scramble
  does NOT kill the lift (map not load-bearing).
- **MIDDLE_BAND**: significant (0.01<=p<0.05) but small, or gain positive but
  marginal, or baseline out of band, or discriminator did not fire.

## Honest framing
MEASURED_MECHANISM territory: meaning = better sense ASSIGNMENT via entity
semantics, NOT compositional generalization / chain-grade. Do NOT inflate. An
honest NEGATIVE (entity-typing does not significantly beat MFS, OR the residual is
world-knowledge type-lookup can't fix) is a valid, valuable outcome. MFS is a
famously strong WSD baseline -> genuine can-fail.

## Compute
Class (b) sequential-CPU justified: symbolic count-model + WordNet lookups, no
matmul/GPU/substrate primitive. Full wall ~1-2 min (SemCor tree deserialization,
cached once). final_metrics_atomicity = tmp_replace. crlb_n/a (symbolic accuracy
over sense-tagged corpus; no matmul noise floor).
