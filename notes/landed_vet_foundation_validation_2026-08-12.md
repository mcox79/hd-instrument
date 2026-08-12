# LANDED-VET: exp_foundation_validation_harness_v1 (2026-08-12)

Auditor: Skunkworks. Audit-only. Written incrementally; sections appended as established.

SUBJECT: claimed run_mode=full, verdict=HARD_PASS_foundation_validated,
against frozen snapshot data/foundation/reading_grounding_v1/ (7966 facts / 3544 GROUNDED_MEANING).

STATUS: IN PROGRESS

## 0. Artifacts located
- Cell: experiments/exp_foundation_validation_harness_v1.py (41556 B, mtime Aug 12 10:10 local)
- Full metrics: data/exp_foundation_validation_harness_v1/metrics.json (ts 2026-08-12T14:27:19Z)
- Smoke metrics: data/exp_foundation_validation_harness_v1_smoke/metrics.json (ts 14:12:39Z)
- Single commit: 71a84d86f 2026-08-12 10:13:46 -0400. Working tree CLEAN for this file.

## 1. THE NUMBERS (full run, off disk)
n_facts_loaded=7966; n_live_grounded_meaning=3544 -- both CONFIRMED present in metrics.
Snapshot: data/foundation_snapshots/reading_grounding_v1_full_20260812T142513Z
SEED = single seed 20260812. **ONE SEED. No cross-seed CV is computable for any claim.**
elapsed 125s.

claim1 CORRECTNESS: n_sampled=150, precision_hat=0.98, chance_hat=0.7267, gap=0.2533
  band hard_pass_gap_min=0.20 -> passes by margin 0.0533 (26% over the floor). MARGINAL.
  Wilson precision [0.9429,0.9932], Wilson chance [0.6504,0.7917] (non-overlapping).
  not_found_rate=0.0067, corpus_n_sentences=30889.
claim2a COHERENCE: cohesion_gap=0.4765 vs band 0.10, 605 qualifying clusters, 0 missing vec.
claim2b CONTRADICTIONS: active_contradiction_count=0, flagged_pairs_count=0.
claim3 CAN-REASON: n_available_chains=356, n_sampled=150, mechanism=1.0, scramble=0.0,
  ablation=0.0, leaked_count=0. **Exact 1.000 / 0.000 / 0.000 -- META_RULE_Q suspect-1.000
  fires on all three arms simultaneously.**

### Smoke-vs-full delta (the MIDDLE_BAND question)
Smoke: n_sampled=20, precision=0.25, chance=0.0, gap=0.25, not_found_rate=0.75,
corpus_n_sentences=12157 -> MIDDLE_BAND.
Full:  n_sampled=150, precision=0.98, chance=0.7267, gap=0.2533, not_found_rate=0.0067,
corpus_n_sentences=30889 -> HARD_PASS.
The gap barely moved (0.2500 -> 0.2533). What moved is not_found_rate 0.75 -> 0.0067,
driven by the MEASUREMENT CORPUS more than doubling: CORPUS_SOURCES_FULL =
CORPUS_SOURCES_SMOKE + onestop Adv/Ele/Int globs + base_vocabulary glob (cell lines 90-107).
So the smoke->full promotion is NOT more evidence about the foundation; it is a
run_mode-dependent enlargement of the reference corpus the foundation is scored against.
Both precision AND chance rose together; the smoke MIDDLE_BAND was a
corpus-coverage artifact, and the full HARD_PASS is a different measurement, not a
higher-powered version of the same one.

## 2. PRE-REGISTRATION -- CLEAN (no band-tampering)
- preregs/2026-08-12_foundation_validation_harness_v1.md mtime 2026-08-12 10:10:30 -0400
- cell mtime 10:10:10 -0400; commit 71a84d86f at 10:13:46; working tree CLEAN (no post-run edit)
- smoke ran 10:11-10:12 local; full ran 10:25-10:27 local. Cell/prereg BOTH predate BOTH runs.
- Bands in the prereg (lines 113-118, 138, 208-213) are IDENTICAL to the code's hardcoded
  thresholds (claim1 gap>=0.20 + Wilson-lo(prec)>Wilson-hi(chance); claim2a 0.10/0.02;
  claim3 mech>=0.50, both gaps >=0.20) and identical to the `bands` block in BOTH metrics.json.
- The FULL corpus scope INCLUDING base_vocabulary was declared in the prereg (lines 91-93)
  BEFORE the run. Not a post-hoc corpus swap.
FINDING: bands were fixed before the run. NOT disqualifying. **One scope deviation:** the
prereg and the cell docstring both state "SCOPE OF THIS DISPATCH: SELF-TEST + SMOKE ONLY...
NO FULL dispatch: the decisive run is deferred until the director hands off the final
(post-accumulation) foundation path" and "FULL corpus scope (not run today)". A full run was
executed 12 minutes later against a self-frozen snapshot. Bands were not touched, so this is a
process deviation, not evidence-tampering -- but the run is NOT the pre-registered decisive run.

## 4. BASELINE -- the base_vocabulary blob question, ANSWERED WITH NUMBERS
Corpus composition, independently recomputed (.venv, off disk):
```
bio            n_sent= 10928 max_words_in_one_sent=    695
process        n_sent=  1229 max_words_in_one_sent=     52
onestop_Adv    n_sent=  6517 max_words_in_one_sent=    150
onestop_Ele    n_sent=  5572 max_words_in_one_sent=     92
onestop_Int    n_sent=  6635 max_words_in_one_sent=     69
base_vocab     n_sent=     8 max_words_in_one_sent=  74288   <-- ONE 74,288-WORD "SENTENCE"
TOTAL sentences = 30889   (exactly matches metrics.json corpus_n_sentences)
```
`base_vocabulary/cleaned/*` is NOT prose: it is `base_vocabulary_ordered.csv` (2.4 MB, 74287
rows) plus two .json files, glob-loaded as `raw_text_glob`. The sentence splitter
`(?<=[.!?])\s+` never fires inside the CSV (every period is followed by a digit), so the entire
74k-word vocabulary becomes ONE pseudo-sentence in which essentially ANY two English lemmas
"co-occur". This is a real corpus-loading defect.

DIRECTION OF THE BIAS -- recomputed on the exact 150 checkpointed units
(data/exp_foundation_validation_harness_v1/ckpt_claim1/units.jsonl):
```
FULL (incl base_vocab blob)   prec=0.9800 chance=0.7267 gap=0.2533  -> HARD_PASS  [reproduces cell exactly]
PROSE ONLY (no base_vocab)    prec=0.9200 chance=0.0333 gap=0.8867  -> HARD_PASS
BASE_VOCAB BLOB ONLY          prec=0.7667 chance=0.7200 gap=0.0467  -> HARD_FAIL
```
ANSWER to the stalled question: the blob DOES inflate the chance baseline (0.0333 -> 0.7267),
but the bias runs AGAINST the claim, not for it. Removing the blob widens the gap 0.2533 ->
0.8867. Claim 1's HARD_PASS is NOT an artifact of the vocabulary blob and does not depend on it.
(Symmetric-anti-negativity note: this is a point where the cell is BETTER than the suspicion.)
Cell arithmetic CONFIRMED: my independent recompute reproduces 0.9800 / 0.7267 / 0.2533 exactly.

## 5. LEAKAGE -- FATAL for claim 1 (ground-by-X, grade-by-X)
How canon_obj is produced (hdlab/reading_grounding_loop.py:293-297):
```
raw_sum = np.sum([t.context_vec for t in it.traces], axis=0)
canon_obj, best_cos = canonicalize(lemma, raw_sum, state.space, thresh=SENSE_MATCH_THRESH)
state.store.store(lemma, MEANING_RELATION, canon_obj, ...)
```
`context_vec` is `context_vector_masked(sentence, lemma)` -- the lemma's SAME-SENTENCE
co-occurrence window from the corpus being read. `canon_obj` is therefore selected as the
nearest word in same-sentence-co-occurrence space, drawn from the read text.
Claim 1 then TESTS: "do `lemma` and `canon_obj` co-occur in a sentence of that same corpus?"
That is the SELECTION CRITERION restated as the TEST. precision -> 1 is guaranteed.
NAMED LEAK PATH: foundation grown from OneStop Ele/Int/Adv + textbook_concepts_biology +
process_articles (prereg 2026-08-12_reading_grounding_loop_cycle2_v1.md lines 57-60); the
claim-1 reference corpus is those exact same files (cell lines 90-107). The prereg's phrase
"Held-out reference" (line 80) is FALSE for this run. Zero held-out text.

CONSTRUCT INVALIDITY, shown directly from the checkpointed units (all scored real_hit=TRUE,
i.e. counted as CORRECT groundings):
```
buyer -> also        checklist -> height    whal -> most        india -> year
woken -> pot         fever -> brightly      firework -> take    thursday -> federation
novelty -> take      sewage -> pip          shopkeeper -> cri   sharp -> bob
```
A minority are plausible collocates (metamorphic->sedimentary, gradient->diffusion,
triphosphate->adenosine, sibling->cousin). None of the above are "the meaning of" the lemma.
The metric cannot separate a correct grounding from an arbitrary same-sentence collocate,
so precision_hat=0.98 is NOT a correctness measurement. Claim 1 does not license
"3544 grounded concepts" in any semantic sense.

## 3. CAN THE CONTROLS FAIL?
- **claim3 ABLATION -- CANNOT FAIL.** `ablation_correct = (B_hat == C)`, but
  `build_two_hop_chains` (cell:267) explicitly excludes chains where `C == B`. Given the
  mechanism arm shows B_hat == B for all 150, ablation_correct is identically False. Ablation
  accuracy is forced to 0.0 whenever the mechanism works at all. The cell's docstring even
  concedes this ("must collapse to near-0 since B != C by chain construction") -- yet
  `gap_ablation >= 0.20` is one of the four AND-ed conditions of claim 3's HARD_PASS band.
  A criterion that is logically implied by another criterion is not a control.
- **claim2b NO-CONTRADICTIONS -- CANNOT FAIL.** hd_fact_store.py:314-319: on an equal-trust
  conflicting write to a FUNCTIONAL relation (GROUNDED_MEANING is FUNCTIONAL per store_meta),
  the store sets BOTH facts to FLAGGED. Two ACTIVE objects for one subject is unreachable via
  the write path. `active_contradiction_count == 0` is a store-invariant unit test, not a
  coherence finding. Corroborating tell: `flagged_pairs_count == 0` too, because
  `process_sentence` short-circuits terminal Library items and `is_gap` skips known words, so
  each lemma is grounded exactly ONCE and never revisited -- write-once, not coherent.
- **claim2a COHESION -- NEAR-CANNOT-FAIL (ground-by-X, grade-by-X).** Clusters are lemmas
  sharing a canon_obj; cohesion is ConceptSpace cosine among those lemmas. But lemmas were
  ASSIGNED to that canon_obj *because* their context vectors were nearest it in that same
  cosine space, and `space.seed_from_bundle(lemma, raw_sum)` then writes the lemma's own
  context back into the space. Intra > inter is structurally implied. The descriptive
  neighborhoods in metrics.json corroborate that the space is not semantic:
  university -> significantly/chart/grim; biological -> that/family/charge.
- **claim3 SCRAMBLE -- CAN fail in principle, but is uninformative.** Exact-match against a
  shuffled 3544-object universe has expected accuracy ~1e-4; 0.0 carries almost no bits, and
  it cannot distinguish "reasoning" from "lossless dict lookup", which is the actual question.
- **claim3 NO-LEAK -- near-by-construction.** `build_two_hop_chains` already excludes
  `(A,C) in direct` before the measurement-time re-check. leaked_count=0 is expected.
- **What claim 3 actually measures.** Ground truth (`build_active_relation_map`, cell:226-233)
  is read from `store._facts`; the mechanism arm reads via `store.query()` (HD unbind+cleanup).
  mechanism_accuracy=1.0 therefore proves HD RETRIEVAL IS LOSSLESS at 3544 concepts -- a real
  but already-known result (bit-identical persistence, cycle2). It is NOT 2-hop reasoning:
  the chains were *defined* by the same map the mechanism dereferences, and the example chains
  are semantically empty (blank->daunt->sheet, calorie->skim->soft, trilogy->obscurity->audienc).

## POWER
ONE seed (20260812). No cross-seed CV computable on any claim. All three claims are single-draw.

## VERDICT: OVERSTATED
The run is REAL and REPRODUCES (my recompute matches 0.9800/0.7267/0.2533 exactly; corpus
sentence counts match 30889/12157 exactly; no fabrication, no band-tampering, prereg predates
the run). What is overstated is the INTERPRETATION "HARD_PASS_foundation_validated /
foundation TRULY grounded and properly organized". Of the four band conditions carrying the
verdict, two cannot fail (claim2b, claim3-ablation), one is near-forced by
ground-by-X-grade-by-X (claim2a), and claim1 is measured against the training text using the
same co-occurrence rule that produced the facts, on facts that are demonstrably not meanings
(buyer->also, india->year, all scored "correct").

DISPOSITION: MEASURED_MECHANISM, not chain-grade. What it does prove, and all it licenses:
"On a 7966-fact / 3544-GROUNDED_MEANING store, HDFactStore.query() reproduces the shadow ledger
exactly over 150 two-hop dereferences (retrieval is lossless at this scale), the store's
FUNCTIONAL-cardinality invariant holds, and reading-assigned (lemma, canon_obj) pairs co-occur
in the read corpus far above a random-word decoy (0.92 vs 0.033 on prose) -- i.e. the pipeline
stores and retrieves what it extracted, with integrity."
It licenses NO claim about grounding CORRECTNESS, semantic organization, or reasoning.

## WHAT WOULD MAKE IT DECISIVE (for the author, not a directive)
1. HELD-OUT text for claim 1 (corpus the foundation never read), or an external reference
   (WordNet gloss/synset overlap), replacing corpus co-occurrence.
2. A claim-1 discriminator that can fail: score against a human/reference meaning, not
   co-occurrence. Current design would pass a store of pure same-sentence collocates.
3. Drop `base_vocabulary/cleaned/*` from any co-occurrence corpus, or sentence-split it
   properly -- one 74,288-word pseudo-sentence is a defect regardless of bias direction.
4. Replace the ablation arm with one that is not logically implied (e.g. hop-1 answered from a
   DIFFERENT subject's map), and replace claim2b with a check the write path cannot guarantee.
5. Claim 2a must be graded in a space not used to form the clusters.
6. >=3 seeds.
