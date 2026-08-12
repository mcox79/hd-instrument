# Pre-reg: foundation_validation_harness_v1

Director task (2026-08-12, spawn to exp_dev): build + smoke a FOUNDATION-QUALITY VALIDATION
harness answering "is the reading-grown foundation TRULY grounded and properly organized" along
3 claims (CORRECTNESS, ORGANIZATION/COHERENCE, CAN-REASON), each with controls. This is the (2)
validation the USER gated further growth on (MEMORY.md ACTIVE MISSION, 2026-08-12). Build + SMOKE
only against a FROZEN snapshot now; the decisive FULL run is deferred until the director hands
off the final foundation path (two in-flight accumulation agents, cycle2-bio aabae9339 +
self-directed-gap-loop a7ace81e, are still writing data/foundation/reading_grounding_v1/ as of
this pre-reg).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "foundation validation grounding correctness coherence multi-hop
reasoning scramble ablation control"` run before any design work. Top-5 hits, all cosine <0.38:
(1) entity='foundation' cosine=0.3721 -- generic word-concept match, not a prior validation
    design.
(2) 'reasoning_scope_correction' cosine=0.3633 -- unrelated skunkworks concurrency note.
(3)/(5) `data/exp_read_grow_foundation_conditioned_comprehension_v1/metrics.json` cosine=0.358/
    0.353 -- the closest genuine prior-work hit (same reading/grounding arc). Inspected:
    verdict=HARD_FAIL_CARRYFWD_RARE, "carry-forward test terms too rare (n=0 < 15); loop
    untestable at this scale" -- tests carry-forward COMPREHENSION on cold vocabulary, NOT
    store-level correctness/coherence/multi-hop-reasoning-with-controls. Different claim
    structure, different mechanism under test.
(4) 'correlation' cosine=0.3545 -- generic math-concept match.
No hit at cosine>0.30 tests this exact harness (3-claim store audit + no-leak/scramble/ablation
controls over HDFactStore). Verdict: NOVEL, not a rediscovery.

## Capability-registry check
`python tools/capability_registry_query.py --serves "grounding validation"` -> 0/107 rows match.
No existing wired capability serves this; building fresh, reusing owned organs per below (not a
parallel mechanism).

## Object under test
`hdlab.hd_fact_store.HDFactStore` loaded via `hdlab.foundation_persistence.load_store()` from a
FROZEN, TIMESTAMPED COPY of `data/foundation/reading_grounding_v1/` (an accumulation agent is
actively writing the live dir; this harness NEVER opens the live dir directly). First frozen
smoke snapshot taken 2026-08-12T13:50:41Z:
`data/foundation_snapshots/reading_grounding_v1_smoke_20260812T135041Z/`
MEASURED@that snapshot's `store/store_meta.json`: n_dim=2048, seed=1001, sr_threshold=0.75,
use_index=True, relation_cardinality={KNOWN_WORD: FUNCTIONAL, GROUNDED_MEANING: FUNCTIONAL}.
MEASURED@store/store_facts.json: 7966 total fact rows, all status=ACTIVE (no SUPERSEDED/DROPPED/
FLAGGED present in this snapshot); relation counts KNOWN_WORD=4422, GROUNDED_MEANING=3544 (of
which 2328 self-grounded [subject==obj, a terminal/root anchor] and 1216 cross-grounded
[subject != obj, a genuine word->concept claim]).

Facts are `(lemma, GROUNDED_MEANING, canonical_obj)` word-sense-grounding assertions (the
lemma's context-bundle nearest-anchor in `ConceptSpace`), NOT a general-relation KG -- this
shapes claim 3's design below (transitive GROUNDED_MEANING chains, not arbitrary multi-relation
hops).

The cell can ALSO take `--freeze-from <live_dir>` to perform the frozen-copy step itself
(`shutil.copytree` into a fresh `data/foundation_snapshots/<tag>_<UTC-ts>/`) so the eventual FULL
dispatch is a single auditable "freeze-then-validate" invocation once the director hands off the
final live path.

## Reused organs (wire-don't-island; no parallel mechanism)
- `hdlab.hd_fact_store.HDFactStore.query()` -- the ONLY read path (glass-box unbind+cleanup);
  claim 3's REASON mechanism is two CHAINED calls to this real method, not a python-dict
  shortcut (the shadow `subject/obj` fields are used only to CONSTRUCT candidate questions and
  grade the final answer, exactly the "SHADOW ledger used ONLY for grading/inspection" role the
  module's own docstring assigns them -- never used as the answer path).
- `hdlab.foundation_persistence.load_store` / `load_concept_space` -- the sanctioned reload API
  (byte-identical round-trip, proven by that module's own self-tests).
- `hdlab.reading_grounding_loop.ConceptSpace.bundle()` -- per-lemma quantized context vector,
  reused read-only for claim 2a's same-rep-at-scale cohesion measurement.
`hdlab.cleanup_family.iterative_attractor` (the pointer-cited "reasoning/cleanup primitive") is
the SAME primitive family `HDFactStore`'s own per-role cleanup already IS (matmul + argmax over
a domain codebook, via `EventBundleCodec`/`RoleSlotSummarizer` bipolar bind/cleanup) -- claim 3's
2-hop chained `store.query()` mechanism exercises that family natively at each hop; a bespoke
second call into `cleanup_family.iterative_attractor` would be a duplicate cleanup pass over the
identical codebook math, not a different mechanism, so it is deliberately NOT re-invoked
separately (documented here per META_RULE_AC so this is a stated design choice, not a silent
gap).

## Claim 1 -- CORRECTNESS
Scope: live (status ACTIVE/COMBINED) GROUNDED_MEANING facts, CROSS-grounded only (subject !=
obj; self-grounded facts are a null claim -- "word means itself" -- reported descriptively as
`self_grounded_rate`, not scored).

Held-out reference: MODERN corpus co-occurrence (USER-LOCKED modern-only: explicitly EXCLUDES
`data/corpora/mcguffey_graded`, `data/corpora/mcguffey_readers`, `data/corpora/graded_readers_*`).
Per-fact sentence pointers are NOT recoverable from the store (facts carry only a segment-level
`source` tag, e.g. `reading:bio_new`; `hdlab/foundation_persistence.py`'s own docstring confirms
terminal-item traces are intentionally not persisted past promotion) -- so "check against the
SOURCE sentence" is implemented as "check against real sentences drawn from the same class of
modern source material", the closest available reconstruction, not literal per-fact backtrace.
Declared explicitly rather than silently substituted.
- SMOKE corpus scope: `data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt`
  (OpenStax Biology, raw text, naive sentence split) + `data/corpora/process_articles_v1/
  process_articles.json` (already sentence-split, `articles[name][section] -> [sentence,...]`).
- FULL corpus scope (not run today): adds `data/corpora/onestop/Texts-SeparatedByReadingLevel/
  {Adv,Ele,Int}-Txt/*.txt` (plain text; verified format 2026-08-12, NOT the bracketed-parse
  `Processed-AllLevels-AllFiles/Parsed/*` variant) + `data/corpora/base_vocabulary/cleaned/*`.
- Match rule: `lemma_match_mode: "prefix_from_word_start"` -- stored lemmas are already stemmed
  by `reading_grounding_loop.normalize_lemma` (a generic suffix-stripper, e.g. "villag" from
  "village"), so exact whole-word regex would systematically MISS real surface forms. Match =
  `re.compile(r'\bLEMMA', re.IGNORECASE)` (word-boundary at the START only). This has a known
  short-stem over-match risk (e.g. "end" prefix-matches "ending"/"endure"); the SAME matcher is
  applied identically to the true `canon_obj` AND the decoy (below), so any systematic
  over-matching bias affects `precision_hat` and `chance_hat` equally and mostly cancels in the
  GAP the gate actually uses -- self-tested directly (see Self-test section).
- Co-occurrence window: same-sentence only (`cooccur_window: "same_sentence"`).

Sampling (deterministic, PROT-023 compliant -- one `random.Random(SEED)` consumed sequentially
over a `sorted()` candidate list, never `hash()`/`list(set())`):
- N_smoke = min(20, n_cross_live); N_full = min(150, n_cross_live).
- `precision_hat` = fraction of sampled facts whose (lemma, canon_obj) co-occur in-scope-corpus.
- `chance_hat` = fraction where lemma co-occurs with a per-fact deterministic DECOY object (drawn
  from the live OBJECT vocabulary, excluding the true canon_obj and lemma itself), same matcher.
- Wilson 95% CI computed for both (formula self-tested, see below; no external stats dependency).
- `gap = precision_hat - chance_hat`.

Bands:
- HARD_PASS: `gap >= 0.20` AND Wilson-lo(precision) > Wilson-hi(chance) (statistically
  separated, not just point-estimate).
- HARD_FAIL: `gap < 0.05` (indistinguishable from chance-level corpus co-occurrence -- the
  store's claimed word-meanings carry no detectable real-text support above noise).
- MIDDLE_BAND: otherwise.
`crlb_n/a`: "precision-vs-chance corpus-co-occurrence estimate, not a Gaussian argmax-noise
capacity metric; no CRLB applies." `discriminator_reachability`: true (a genuinely-grounded
fact's canon_obj is a real associate of lemma in running text; a genuinely-noise-grounded fact's
canon_obj is not, so the corpus either does or does not confirm the pairing -- reachable either
way, that IS the measurement).

## Claim 2 -- ORGANIZATION / COHERENCE
Three components; (a) and (b) are quantitative gates, (c) is a descriptive spot-check (not
gated -- "sensible neighborhoods" requires qualitative judgment, logged to `diag` for
inspection, not a numeric pass/fail).

**(a) same-idea==same-rep AT FOUNDATION SCALE** (extends the small dedup case to the live
foundation): group ALL live GROUNDED_MEANING facts (self+cross) by `canon_obj`; clusters with
>=2 member lemmas qualify. For each qualifying cluster, `intra_cos` = mean pairwise cosine among
members' `ConceptSpace.bundle(lemma)` vectors; `inter_cos` = mean cosine from each member to
`k_neg=5` deterministically-sampled members drawn from OTHER clusters. `cluster_gap = intra_cos -
inter_cos`; `cohesion_gap` = mean over qualifying clusters (cap: smoke 40 clusters, full all).
Requires >=5 qualifying clusters for a valid measurement, else `INCONCLUSIVE_INSUFFICIENT_
CLUSTERS` (not gated as fail).
- HARD_PASS: `cohesion_gap >= 0.10`. HARD_FAIL: `cohesion_gap <= 0.02`. MIDDLE_BAND: otherwise.

**(b) no contradictory facts co-stored**: for each FUNCTIONAL relation (KNOWN_WORD,
GROUNDED_MEANING per the store's own declared `relation_cardinality`), scan `(subject,relation)`
groups for >1 DISTINCT object among status==ACTIVE facts -- that is the genuine invariant breach
(the store's own REPLACE logic should always leave <=1 ACTIVE winner; FLAGGED pairs are
DETECTED-and-parked unresolved conflicts, i.e. the mechanism WORKING, reported separately as
`flagged_pairs_count`, not a coherence failure). Reads `HDFactStore._facts` directly (same
sanctioned precedent as `hdlab/foundation_persistence.py`'s own save/load, which already reads
this same private state to build/restore snapshots) since the aggregate contradiction question
has no public API.
- HARD_PASS: `active_contradiction_count == 0`. HARD_FAIL: `active_contradiction_count > 0`.

**(c) concept neighborhoods (descriptive)**: sample 10 deterministic self-grounded root lemmas,
report their top-5 `ConceptSpace` cosine-neighbors to `diag` for human/agent inspection at smoke
time (not gated).

Overall claim-2 verdict = HARD_PASS iff (a) and (b) both HARD_PASS; HARD_FAIL if either
HARD_FAILs; else MIDDLE_BAND.

## Claim 3 -- CAN-REASON (load-bearing)
Chain construction (deterministic, from the store's own live `subject->obj` GROUNDED_MEANING
map, used ONLY to select+grade questions, never as the answer path -- see "Reused organs"):
for every `A` with `gm_map[A]=B` and `B` itself in `gm_map` with `gm_map[B]=C`, keep iff
`C != B`, `B != A`, `C != A` (non-trivial chain -- a self-grounded hop-2 target degenerates the
2nd hop into a no-op and would let the ablated arm trivially "win", defeating the control), AND
`(A, C)` is NOT itself a live fact (**no-leak**: the 2-hop answer must never be directly stored).
MEASURED@2026-08-12 snapshot: 356 such chains exist (e.g. `sale -> owner -> house`), plenty for
both smoke (N=25) and a future FULL (N=150, capped at available).

Held-out question: "what does A ground to transitively, via its own first-hop meaning?" Gold
answer = C. The question's gold answer is NEVER present as a single stored fact by construction
(no-leak filter above); answering it requires COMBINING >=2 grounded facts (the hop1 fact for A
and the hop2 fact for B) -- neither alone answers it.

**Mechanism (REASON arm)**: `B_hat = query_single(store, A, "GROUNDED_MEANING")` (real
`HDFactStore.query()`, glass-box unbind+cleanup); `C_hat = query_single(store, B_hat,
"GROUNDED_MEANING")` (same real call, chained). `correct = (C_hat == C)`.
`mechanism_accuracy` = mean over N sampled chains.

**CONTROL 1 -- no-leak**: structurally GUARANTEED by the store's own FUNCTIONAL-cardinality
invariant, not an ad-hoc filter -- `gm_map` (subject->object) holds at most ONE object per
subject (built from ACTIVE facts only), so the ONLY direct fact about `A` is `(A,B)`; once the
chain-construction requires `C != B` (the degenerate-exclusion above), a direct `(A,C)` fact is
impossible unless the store's own invariant is violated. `leaked_count` is nonetheless computed
by DEFENSIVELY re-scanning `HDFactStore._facts` at measurement time (not the shadow `gm_map`) for
any live `(A, GROUNDED_MEANING, C)` fact -- this would only ever fire if the store's FUNCTIONAL
invariant were independently broken (the same failure claim 2b's contradiction scanner also
catches), and is self-tested by deliberately corrupting a tiny real store to prove the check
fires (see Self-test item 7). `leaked_count > 0` is still a HARD_FAIL trigger.

**CONTROL 2 -- scramble-foundation**: build a fresh `HDFactStore` (same n_dim/relation_
cardinality/use_index as the original) over the SAME `(subject, GROUNDED_MEANING)` universe but
with `obj` values `random.Random(SEED).shuffle()`'d across subjects (fixed seed, degree-
preserving marginal). Re-run the IDENTICAL mechanism (2 chained real `store.query()` calls)
against the scrambled store, for the SAME sampled A's, graded against the SAME true gold C.
`scrambled_accuracy` = mean. Expectation: collapses toward the empirical chance floor because the
scrambled store's subject->object structure is destroyed (this measured floor IS the "chance
baseline" for this claim -- no separate a-priori 1/V formula is used, since the mechanism's own
argmax-cleanup dynamics under scramble are the honest reference, not a naive uniform-random
assumption).

**CONTROL 3 -- ablation (remove the combination/2nd-hop step)**: guess = `B_hat` only (hop1
result, no chaining). `ablation_accuracy` = fraction where `B_hat == C` -- by chain-construction
`B != C` always, so a correctly-implemented ablation floor should be nearly 0; this proves the
SECOND hop (the combination step) is load-bearing, not decorative.

`arms_differ_verified` (META_RULE_AF): hash mechanism/ablation/scrambled per-question prediction
arrays; assert not all bit-identical.

Bands:
- HARD_PASS: `mechanism_accuracy >= 0.50` AND `mechanism_accuracy - scrambled_accuracy >= 0.20`
  AND `mechanism_accuracy - ablation_accuracy >= 0.20` AND `leaked_count == 0`.
- HARD_FAIL: `leaked_count > 0` OR `mechanism_accuracy - scrambled_accuracy < 0.05` OR
  `mechanism_accuracy - ablation_accuracy < 0.05` OR `mechanism_accuracy < 0.10`.
- MIDDLE_BAND: otherwise.
`crlb_n/a`: "discrete exact-match retrieval accuracy over an enumerated no-leak question set;
the empirical scramble-control accuracy IS the chance floor used, no separate closed-form CRLB."

## Overall verdict
`HARD_PASS_foundation_validated` iff all 3 claims HARD_PASS. `HARD_FAIL_foundation_validation_
failed` if ANY claim HARD_FAILs. Else `MIDDLE_BAND`. SMOKE mode additionally requires
`smoke_controls_discriminate` (claim-3 mechanism_accuracy strictly > BOTH scrambled_accuracy and
ablation_accuracy, directionally, even if the smoke-scale gap does not yet clear the 0.20 FULL
bar) -- if that directional check fails, override to `SMOKE_GATE_FAIL_discriminator_not_firing`
regardless of the other numbers, per exp_dev's DISCRIMINATOR-MUST-SURVIVE-SCALE + "smoke must
fire the discriminator" disciplines.

## SCHEMA-VET gates
- `sweep_alignment_verdict`: N/A -- no swept axis (fixed sample sizes per mode); declared
  `no_sweep_axis`.
- `discriminating_fraction`: N/A, same reason; declared `no_sweep_axis`.
- `composition_edges`: `HDFactStore.query(A) -> HDFactStore.query(B_hat)` SHAPE_MATCH (both
  calls the identical public method on the identical store instance; chained by python, no
  adapter needed).
- `positive_control_arms`: N/A in the SCHEMA-VET "reproduce a prior chain-grade cell" sense --
  this cell is the FIRST test of this exact claim (see prior-work check); its own formula
  self-tests (below) serve the equivalent role (reproduce the mechanism at a tiny, closed-form,
  analytically-known regime before trusting it on noisy real data).
- `functional_requirements`: (1) sample+verify factual precision against an external reference
  -> corpus co-occurrence check (new, this cell). (2) verify representational coherence at scale
  -> `ConceptSpace.bundle` cosine cohesion (existing organ, reused). (3) verify contradiction-
  free storage -> `HDFactStore`'s own status/`relation_cardinality` invariant, audited directly
  (existing organ's own invariant, reused not reinvented). (4) combine >=2 facts to answer an
  unstated question -> chained `HDFactStore.query()` (existing organ's own read path, reused,
  not a new retrieval mechanism).
- `real_code_path_exercised`: [HDFactStore, ConceptSpace] -- self-test constructs REAL
  `HDFactStore` instances (tiny n_dim=512, ~10-20 facts) and a REAL `ConceptSpace`, not a
  synthetic-only branch.
- `substrate_signature_checked`: `HDFactStore(n_dim=int, seed=int, relation_cardinality=dict,
  sr_threshold=float, use_index=bool)` -- all base/stable kwargs (matches the constructor used
  throughout `hd_fact_store.py`'s own self-tests; no version-specific optional kwarg risk).
- `guard_baseline_validated`: N/A -- no control-beats-baseline break-guard in this cell (bands
  are direct threshold/gap gates); declared `n/a`.
- `deterministic_seeding`: true -- one `random.Random(SEED)` per claim, consumed sequentially
  over `sorted()` candidate lists; `HDFactStore`'s own `torch.Generator(seed=...)` for the
  scrambled store construction; no `hash()` or `list(set())` ordering anywhere.
- `baseline_in_band` (META_RULE_AG): N/A -- claim 3's "baseline-ish" arms (scrambled, ablated)
  are INTENTIONALLY-WEAKENED controls, not saturating baselines; declared
  `exempt: scrambled_and_ablated_are_the_can-fail_controls_not_saturating_baselines`.
- `cell_chunked`: false -- single deterministic pass per mode, no seed axis; wall time far under
  the chunking threshold (smoke measured, see below).
- `arms_differ_verified`: MANDATORY at smoke, per claim 3 above.
- `final_metrics_atomicity`: `tmp_replace` (single-shot; `.tmp` + `os.replace`).
- `progress_logging`: N/A -- smoke `timeout_s` far under 1800s (measured below); declared
  `progress_cadence_expected_s: n/a (short cell)`.

## Compute architecture
Sequential-CPU, justified: N<=150-per-claim exact-match lookups + cosine ops over a <=4000-fact,
n_dim=2048 store; dominant cost is corpus text I/O (a few MB) and the scrambled-store rebuild
(~3544 `store.store()` calls, use_index=True, O(1) average). No batched-GPU benefit at this
scale (matmul dimensions are tiny per call; the win would be batching thousands of independent
tiny matmuls, which numpy/torch CPU already handles in microseconds each here). Storage strategy:
`no_storage` -- this cell is READ-ONLY over an existing frozen snapshot; it does not write new
facts to any canonical store (the scrambled-store rebuild is an in-memory throwaway control
object, never persisted).

## Multi-unit checkpoint/resume
Each claim's per-item loop (claim 1: sampled facts; claim 2: qualifying clusters; claim 3:
sampled chain questions) uses `tools/exp_checkpoint.py` (`unit_key`/`completed_units`/
`record_unit`/`load_units`) writing to `<output_dir>/ckpt_claim{1,2,3}/units.jsonl`, per
CLAUDE.md's multi-unit mandate.

## Self-test (formula-level, real-code-path, per F.1)
All tiny, closed-form, analytically-known-answer fixtures using REAL `HDFactStore`/`ConceptSpace`
objects (n_dim=512, ~10-20 facts), run before ANY real foundation data is touched:
1. `wilson_ci` sanity: bounds/monotonicity properties (0<=lo<=phat<=hi<=1; interval narrows as n
   grows; k=0 -> lo=0; k=n -> hi<1 asymptotically).
2. Prefix co-occurrence matcher: "villag" matches "the village council met" (true), does NOT
   match "the pillage was swift" (false, no leading-boundary match), matches "villagers gathered"
   (prefix-extends correctly).
3. `cohesion_gap`: tight synthetic clusters (base vector + small noise, 3 clusters x 3 members)
   give `gap > 0.3`; a degenerate all-random-vectors case gives `gap < 0.15` -- proves the metric
   discriminates structured vs unstructured at the formula level.
4. Contradiction scanner: (a) a clean store + one FLAG-conflict (via `store.store()`'s own logic)
   gives `active_contradiction_count==0`, `flagged_pairs_count==1`; (b) manually forcing both
   conflicting records' status back to ACTIVE (simulating a hypothetical future bug) makes the
   scanner report `active_contradiction_count==1` -- proves the check is can-fail, not vacuous.
5. Chain builder: a clean 2-hop chain is included; a degenerate chain (hop-2 self-grounded,
   B==C) and a cycle (B==A) are both excluded.
6. Leak detection: a clean tiny store reports no leak for its own chain; after deliberately
   injecting a corrupted direct `(A, GROUNDED_MEANING, C)` ACTIVE fact (bypassing `store()`'s own
   conflict logic via direct `FactRecord` append, simulating a hypothetical bug), the same
   measurement-time scan correctly flags the leak -- proves the check is can-fail, not vacuous
   (see CONTROL 1 above for why a leak cannot arise through normal chain construction).
7. REASON mechanism + all 3 controls, on a real tiny store with 3 planted clean chains:
   mechanism_accuracy==1.0 (noiseless); ablation_accuracy==0.0 (B always != C by construction);
   scramble (fixed seed) accuracy drops by >=0.5 absolute on this tiny fixture -- proves the
   mechanism, ablation, and scramble controls all fire correctly BEFORE ever touching noisy real
   foundation data.

## Smoke design
Real pipeline against the frozen snapshot (`data/foundation_snapshots/reading_grounding_v1_
smoke_20260812T135041Z/`), N=20 (claim 1), cluster-cap=40 (claim 2), N=25 (claim 3 chains).
Smoke gate (in addition to the claim bands, which are reported honestly even if not yet
decisive at this N): `smoke_controls_discriminate` as defined in "Overall verdict" above --
non-negotiable before this harness is ever considered ready to point at a FULL run.
Estimated wall time: dominated by corpus load (~1.5MB text + 512KB json, <2s) + scrambled-store
rebuild (~3544 `store()` calls, expect low-single-digit seconds) + O(100) query()/cosine calls
(milliseconds) -- smoke total expected well under 60s (MEASURED value reported in the smoke
`metrics.json`; if wall time exceeds expectation materially, `progress_logging` requirement
above is re-evaluated).

## Dispatch
SMOKE runs on `local_cpu_queue` per the USER-LOCKED 2026-07-01 "smoke only on local" rule (this
harness IS the smoke; there is no separate smoke-then-full dispatch today). NO FULL dispatch --
explicitly deferred until the director hands off the final (post-accumulation) foundation path,
per task contract. No origin push (LOCAL-only commit).
