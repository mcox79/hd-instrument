# Opportunity map (2026-08-13)

SYNTHESIS ONLY. No code modified, nothing committed, no experiment run or re-run, no process
signalled. `data/exp_anchor_pool_expansion_v1/` and `data/exp_wire_definitional_v1/` were READ
(their `metrics.json` / `units.jsonl`), not touched. This note is the only file written. No tool
call was denied at any point.

Sources synthesised: `notes/brain_fidelity_subsystems_2026-08-13.md`,
`system_accounting_2026-08-13.md`, `grounding_results_accounting_2026-08-13.md`,
`multisource_lookup_wiring_audit_2026-08-13.md`, `word_concept_bridge_scope_2026-08-13.md`,
`downstream_bottleneck_trace_2026-08-13.md`, `frontier_distance_2026-08-13.md`,
`minimum_grounded_basis_derivation_and_refutation_2026-08-13.md`.
**`notes/e2e_substrate_trace_2026-08-13.md` did not exist at any point during this pass** (checked
three times, first and last calls of the session); it is not synthesised here.

---

## 0. TWO RESULTS THAT LANDED AFTER MOST OF THE AUDIT WAS WRITTEN, AND THEY REORDER IT

Both were read off disk this pass. Neither appears in any of the eight source notes, all of which
predate or run concurrent with them.

### 0a. `exp_anchor_pool_expansion_v1` -- verdict `COMPARATOR_IS_BINDING` (metrics.json ts 16:53Z today)

This is the direct, pre-registered test of the candidate-set half of "the atom basis is random,
fixed, dense". One variable: anchor pool size. Bands were declared before the run.

| quantity (v5 relation-matched key, n=1353 probe subjects) | SMALL (1,171 anchors) | LARGE (12,792 anchors) | delta |
|---|---|---|---|
| availability (answer is in the pool at all) | 0.1988 | **0.9527** | **+0.7539** |
| recall@1 | 0.0081 | 0.0333 | **+0.0251** |
| recall@5 | 0.0177 | 0.0916 | +0.0739 |
| **availability-conditioned recall@1** | 0.0409 | 0.0349 | **-0.0060** |
| live banked correct | 0/39 | 3/67 = 0.045 | |

Pre-registered bands, verbatim from `metrics.json`:
`POOL_WAS_BINDING` = availability delta >= +0.30 AND recall@1 delta >= +0.10;
`PARTIAL` = recall@1 delta in [+0.03, +0.10);
`COMPARATOR_IS_BINDING` = availability delta >= +0.30 AND recall@1 delta < +0.03 --
*"the answer is on the menu and still is not chosen. PRE-DECLARED FULLY EXPECTED AND ACCEPTABLE."*
Power: SE(delta) <= 0.019, so +0.03 is resolvable at >1.5 SE.

**Observed: availability +0.7539, recall@1 +0.0251 -- below the PARTIAL floor. Landed
`COMPARATOR_IS_BINDING`.** The conditional number is the decisive one: given the answer IS in the
pool, the read-out picks it 3.5% of the time with 12,792 anchors and 4.1% with 1,171. **Opening the
candidate set 4.8x bought nothing on the conditional.** On the v62 predicate key (n=36, declared
relation-MISMATCHED and unable to carry the verdict) availability went 0.306 -> 1.000 and recall@1
stayed 0.000 -> 0.000.

Secondary, hand-score-independent: agreement with a plain sentence-level co-occurrence baseline
**rose** with pool size -- top1 0.0751 -> 0.1017, top5 0.2591 -> 0.4383. A larger pool makes the
read-out *more* co-occurrence-like, not more meaning-like.

Caveat carried: gate `S4_small_regression` records `small_reproduces_reference: False` (386 facts
observed vs 384 expected, digest differs), so the SMALL arm is not bit-identical to its reference
run. The delta is 2 facts on 386 and does not plausibly move a +0.75 / -0.006 contrast, but the
gate is red and should be said.

**What this does to the map.** The brief asks whether fixing the random, fixed, dense atom basis is
the highest-value move or whether something gates it. Answer: **nothing gates it -- it IS the gate,
and the one rival explanation has now been eliminated with a pre-registered band at n=1353.** Every
candidate-supply intervention on the list (the CSKG bridge D1/D2/D3, injecting KG edges into
`canonicalize`, growing the seed vocabulary) is refuted as a route to read-out quality by this
result, independently of the CSKG-specific evidence that already refuted it.

**One distinction the brief's framing invites collapsing, and it must not be.** `DGProjection` is
random EXPANSION + top-K sparsify + sign (`hdlab/hippocampal_encoder.py:75-124`). Applied to a
random equidistant codebook it produces a *sparser, less interfering* equidistant codebook. It does
**not** create similarity structure. It is the right fix for interference at high anchor
cardinality -- which the 12,792-anchor arm makes newly relevant -- and it is the wrong fix for
"all concepts start equidistant". Verified this pass: `DGProjection` and `hippocampal_encoder` have
**zero importers anywhere in `hdlab/`** outside the module itself (grep over all of `hdlab/`, only
self-references and its own self-test).

### 0b. `exp_wire_definitional_v1` -- OFF and ON arms complete, SHUFFLE arm RUNNING AS OF THIS PASS

Read from `data/exp_wire_definitional_v1/units.jsonl` and `_heartbeat.jsonl` (last beat
18:45:06Z, SHUFFLE arm at chunk 105 of 228).

| held-out key B (n=661, not injected) | OFF | ON | SHUFFLE |
|---|---|---|---|
| availability | 0.2224 | 0.7519 | **IN FLIGHT** |
| recall@1 | 0.0076 (5) | 0.0378 (25) | **IN FLIGHT** |
| recall@5 | 0.0227 (15) | 0.1044 (69) | **IN FLIGHT** |
| availability-conditioned recall@1 | 0.0340 | 0.0503 | **IN FLIGHT** |
| live banked correct | 0/17 = 0.000 | 4/41 = 0.098 | **IN FLIGHT** |

ON also banked `n_facts_banked_from_definitions: 394` with `n_tautology_facts: 0` and
`no_leak_violations: []`. On the injected half A (declared `INJECTED_A_WITNESS_NO_CLAIM` by the
cell itself, so no claim is licensed from it) availability reached 0.9942 and recall@1 was 0.0665 --
i.e. **with the answer in the pool 99.4% of the time the read-out still selects it 6.7% of the
time**, independently reproducing 0a's conclusion inside a different cell.

**Discipline: the SHUFFLE arm is the floor and it does not exist yet. Until it lands, the OFF->ON
contrast is a number without its control and is not evidence.** It is reported here because it is
decision-relevant and lands within the hour, not because it is established.

---

## 1. RANKING CRITERION, STATED EXPLICITLY

Rank = **P(the move acts on a constraint measured as binding today) x magnitude of the demonstrable
change x P(the observed gain survives its control)**. Three riders:

1. **Effort does not set rank.** It is reported per item and never used to promote or demote.
2. **Brain fidelity is a GATE, not a term.** A mechanism carrying an ARCHITECTURAL-FAULT verdict
   cannot be ranked above "do not wire" however well it scores. This is what removes the voting
   mechanism from the list entirely rather than placing it low.
3. **"Wire something proven" and "build something new" are scored on different risk scales** and
   each item is labelled. A wire inherits an existing control floor; a build has none until it is
   run, so its P(gain survives control) is set at the base rate for this repository, which the
   day's own record puts low (five read-out routes eliminated, one minimum-basis derivation
   refuted by its own frequency-matched control, one 3.3x corpus effect refuted by its own
   matched-N replication).

Consequence worth stating: **#1 and #2 do not compete.** #1 is the highest expected value and acts
on a path the binding constraint does not gate; #2 is the highest ceiling and the only move on the
binding constraint itself. They touch different mechanisms and can proceed in parallel.

---

## 2. THE RANKED MAP

| # | opportunity | kind | evidence quality | fidelity | effort |
|---|---|---|---|---|---|
| 1 | Wire definitional extraction as a DIRECT-BANK channel and as PBV's independent verifier | WIRE | 64% vs 8% floor, same rubric/scorer/sampling; in-flight cell floor PENDING | YES, clearest in audit | LOW (written, running) |
| 2 | Replace the equidistant atom basis with a similarity-structured one from a channel independent in kind | BUILD | binding constraint established at n=1353; ingredients weak | fixes a named ARCHITECTURAL-FAULT | HIGH |
| 3 | Measure and fix the live parser loader; then re-test the structured encoder | FIX + RE-TEST | defect established by reading; magnitude UNMEASURED | S10 is the best-founded subsystem | LOW |
| 4 | Run the missing gather arm (cued gather over `hop2_blind`) before wiring anything from S3 | MEASURE | S3 headline is CONFOUNDED; size unknown | gather is FAITHFUL if the delta survives | LOW |
| 5 | Wire `dg_pattern_separation` into `script_grain_acquisition_loop` | WIRE | fixes a measured defect (purity ~0.19, real 0.5538 < baseline 0.5859) | YES, best-sourced brain claim in the audit | LOW |
| 6 | Wire `cls_discrete_budget_consolidate` (replay) in place of counting-based consolidation | WIRE | HARD_PASS gap 0.913 vs naive-consolidation control | YES; CLS without replay is CLS in name | LOW ("wiring, not invention") |
| 7 | Ingest the 117,642-sentence OpenStax corpus into the definitional extractor | SUPPLY | corpus counted; density 30.8-105.8 per 1,000; unread by anything | neutral | LOW |
| 8 | Give the 94% predicate score a control arm; add a second scorer to the 64% | MEASURE | closes the two floor/reliability gaps under item 1 | n/a | LOW |
| 9 | Consolidate duplicated organs: harness (D2), lemmatisers (D5) | HYGIENE | 939/439 copies vs a zero-importer shim; D5 already cost ~10% store corruption | "the brain reuses circuits" | LOW-MED |
| 10 | Push the 54 unpushed commits / back up the foundation build chain | RISK | the 221 hand-scored facts + entire build chain exist on one disk | n/a | LOW, needs USER auth |
| 11 | Tighten the capability registry; return certification to green | HYGIENE | 62/141 unregistered; `pipeline_status` wrong both ways; 2 red pins | n/a | MED |

---

## 3. THE TOP THREE IN DETAIL

### #1. Wire definitional extraction as a DIRECT-BANK channel (and as the verifier PBV lacks)

**What it is, plainly.** The extractor that reads "X is a Y" out of real textbook prose currently
runs only inside experiment cells. Its facts are written to files that nothing live re-reads.
Wiring it means the reading loop banks those facts into the foundation directly, at the moment of
reading, without asking the broken comparator to choose anything.

**Evidence, with floors.**
- **64% MEANINGFUL (32/50), floor 8% (4/50)** -- v2 distributional baseline, *same scorer, same
  rubric, same seed-42 sampling*; pre-registered HARD_PASS band >=52%. Ladder on one scorer:
  v2 8% -> v3 38% -> v4 40% -> v5 64%. `notes/director_handscore_b3_v5_termboundary_2026-08-12.md`,
  `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` (2,092 rows).
- The brain-fidelity audit's judgement on that number: *"its metric is the best in the repository...
  the only place in this audit where the thing being measured is the thing the brain is judged
  on"* (S2).
- Contrast the live read-out on the same rubric: **2% MEANINGFUL blind** (1/50, the lower and more
  trustworthy figure), 3-8% non-blind.
- **The 94% predicate figure (47/50, v6.2, 221 facts) has NO CONTROL ARM.** It is precision without
  a floor and must not be quoted beside the 64%. Recorded as item 8.
- In-flight (`exp_wire_definitional_v1`): 394 facts banked from definitions, 0 tautologies, 0 leak
  violations; held-out banked-correct 4/41 vs 0/17. **SHUFFLE floor pending -- not yet evidence.**

**Why this is #1 given `COMPARATOR_IS_BINDING`.** Precisely because the direct-bank path does not
route through the comparator. Everything else on the read-out path is capped by a selector that
scores 3.5% when handed the answer; this channel writes the answer without a selection step. It
also does three jobs at once:
(a) supplies the **fast declarative route** the CLS story requires and the substrate does not have
    (it has only the slow distributional accumulator);
(b) replaces a foundation that is **65.7% self-referential tautology** (2,328/3,544 in
    `reading_grounding_v1`) with facts scored at 64%;
(c) supplies PBV's missing **verification channel independent in kind** -- the standing diagnosis of
    why propose-before-verify could not self-correct is that propose and verify "are the *same
    statistic* computed twice" (`brain_fidelity_audit_readout_2026-08-13.md` S3 row 6, quoted in
    S3 of the subsystem audit). A definitional statement is a different kind of evidence from a
    co-occurrence profile. This is the one thing on the list that discharges that fault.

**Brain-fidelity verdict.** DIVERGENT-BUT-COMPATIBLE, **wire YES** -- the audit's clearest wire
recommendation, justified on fidelity rather than convenience: CLS requires both a fast relational
route and a slow distributional one and the substrate has only the second. The wire must **add** a
channel, not replace the accumulator (the module's own docstring argues this).

**Effort.** LOW. The wire is written (uncommitted, in the working tree) and the cell is running.

**Risk.**
- The 64% is **single-judge and NOT blind**; inter-rater reliability is unmeasured anywhere in this
  arc. The one reliability datapoint available is marginal stability, not item-level agreement.
- **NOUN-ONLY**: 0 of 2,092 definienda have a verb-only WordNet sense; all five patterns are
  NP-headed. Syntactic bootstrapping stays blocked.
- **Bounded ceiling**: the definitional graph reaches only 2,563 of 18,276 corpus lemmas = 14.0%,
  and 89.4% of corpus vocabulary is unreachable from the frontier over these edges (83.1% even in
  the most permissive all-files-undirected variant). Wiring this makes the foundation right; it
  does not make it big.
- A regex is not a mechanism, and it re-derives NP-head finding that the live parser already does.

**Can-fail test that would prove it wrong.** Two, both cheap and one already running:
1. **The SHUFFLE arm now in flight.** If a shuffled definition-map reproduces the ON arm's held-out
   recall@5 gain (0.0227 -> 0.1044) within its band, the gain is pool inflation and not definition
   content, and item 1 collapses to item 2's problem. This is the correct primary discriminator and
   it needs no hand-scoring.
2. **Second-scorer replication of the 64%** on the same 50 rows, blind. Fails if the second scorer
   lands below the pre-registered 52% HARD_PASS band -- in which case the single number this item
   rests on is not established.

### #2. Replace the equidistant atom basis with a similarity-structured one, from a channel independent in kind

**What it is, plainly.** Every concept currently starts as an independent random vector, so no two
concepts are more alike than any other two before they have been read about. All semantic structure
must therefore be manufactured out of what words appear near each other. That is why the meaning
read-out degenerates to "which known word co-occurred most". The fix is a representation in which
related things overlap *before* any text is read, sourced from something that is not co-occurrence.

**Evidence, with floors.**
- **The binding constraint is established.** `COMPARATOR_IS_BINDING` at n=1353 with pre-registered
  bands (0a): availability +0.7539, recall@1 +0.0251, **availability-conditioned recall@1 -0.0060**.
  Independently reproduced inside `exp_wire_definitional_v1`: availability 0.9942 -> recall@1 0.0665.
- **It is representational, not a clustering defect.** On this representation even a *supervised*
  nearest-centroid sense classifier scores **0.5167 against a 0.5625 floor** -- below its own floor
  (`brain_fidelity_vet_components.md` Part A, quoted in S8). Same-vs-different-sense cosine
  separation **0.003-0.005**.
- **The right feature being present is not sufficient.** On `banana` the structured encoder isolated
  `(^nsubj, fruit)` and on `aphotic` `(^amod, zone)`, and the arm scored **0/50** (vs CONTROL 2/50,
  pre-registered NULL band |delta| < 0.05).
- **A larger pool makes it worse, mechanistically:** co-occurrence agreement rose 0.0751 -> 0.1017
  (top1) and 0.2591 -> 0.4383 (top5) from SMALL to LARGE.
- **The available ingredients, with their floors.** Perceptual: picture->word top-1 **0.635** vs
  shuffled **0.074**, chance 0.050; WordNet Wu-Palmer coherence rho 0.353 vs null p95 0.117
  (z=5.03, 500 perms); VET-upheld chain-grade, `ed5e1cc9e`; **20 concrete nouns**, never registered,
  never wired, and its own named follow-up -- *"bind into concept-atoms"* -- was never done.
  Substrate-native (no CLIP) image encoder: HD_record test acc **0.907** vs scrambled-position
  **0.107**, position recovery 0.993 vs chance 0.059 -- built from `hdlab.binding`, never pointed at
  words. Sensorimotor: Lancaster 39,707 + Brysbaert 39,955 rows on disk.

**Brain-fidelity verdict.** This is a named **ARCHITECTURAL-FAULT** (S9(a)): the ATL hub's defining
property is a learned, similarity-structured representation in which related concepts overlap; a
random equidistant basis cannot express it, and the audit states explicitly that this is *"the same
fault as S1's, one level down... it is *why* the meaning read-out degenerates"*. The perceptual
route is the faithful answer (modality spokes converging on a hub), and it is also what the S3
analysis independently asks for: **one verification channel independent in KIND**, not N databases.
S8's own NOT-UNTIL-X is worded as "an encoder whose similarity structure is *learned from grounded
evidence*". Three separate sections of the audit converge on the same prescription.

**Effort.** HIGH. This is a build. No implementation exists. `DGProjection` is not it (see 0a).

**Risk. This is the item with the weakest ingredients on the list and that must be said plainly.**
- The perceptual asset covers **20 words**. Its sibling does not scale: reader image-word matching
  is 0.996 at n=112 clean pairs and falls to **0.175-0.299** at 125 items with 40% distractors.
- The sensorimotor norms are **provably inert at the current threshold**: capped at `GROUNDED_CAP`
  0.45, structurally below the 0.50 link threshold, so they mathematically cannot return
  "same concept". Raising the cap is not free -- it exists because measured `apple`/`orange` raw
  cosine 0.952 and `happy`/`joyful` 0.962 are statistically inseparable.
- Abstract concepts are a closed route: `exp_image_schema_real_cpu_v1` HARD_FAIL, cluster purity
  **0.342** (its synthetic sibling's 1.000 is construction-determined).
- Content-aware perceptual encoding has already failed once: aware **0.232** BELOW blind **0.317**.
- Structure-as-lever has already failed once: FACTORIZED 0.837 vs **RANDOM_BIND 0.836**, control
  eats the entire effect.
- The norms were SHELVED today with a revival criterion this item must satisfy, verbatim:
  *"needed as a **generative** anchor rather than a filter -- with a mechanism that **proposes**
  candidate bindings rather than **scoring** pre-existing ones."* Both image cells are structurally
  proposers; the norms as currently wired are scorers.

**Can-fail test that would prove it wrong.** **The harness already exists and has already produced
a floor** -- this is the single most de-risking fact about item 2. Re-run
`exp_anchor_pool_expansion_v1`'s known-answer-recall measurement with the new basis, **at matched
availability (~0.95)**, one variable. Pre-register on the measured numbers: fails if
availability-conditioned recall@1 does not exceed **0.0349** by a margin whose paired CI excludes
zero, with a **scrambled-basis control** (same similarity structure, wrong concept-to-vector
assignment) that must NOT reproduce the gain. Secondary, non-saturated and mechanistic:
co-occurrence agreement must FALL (from 0.1017 top1), not rise -- if the read-out gets better while
agreeing more with a plain co-occurrence baseline, the basis is not doing the work. Note the
asymmetry that makes this honest: a 20-word perceptual spoke cannot move an n=1353 probe, so the
first fair version of this test needs the spoke extended or the probe restricted to covered words
and reported as such.

### #3. Measure and fix the live parser loader, then re-test the structured encoder

**What it is, plainly.** The live reading loop loads a parser weight file that was trained with a
richer feature set than the class that loads it knows how to compute. The extra features' learned
weights are never summed. Nobody knows how well the parser that actually runs, parses.

**Evidence, with floors.** `reading_grounding_loop.py:246` sets
`_PARSER_ASSET = "arc_parser_richfeat_ud_ewt.npz"` and `:306` loads it with `ArcParser.load(...)`,
the base class, whose `parse()` scores with `_arc_ids` only. Those weights were trained by
`exp_parser_uas_ladder_richfeat_v1` using `_arc_ids_rich`, a self-described *"Monotone superset of
_arc_ids"* with 13 extra templates. The consumer class `RichArcParser` exists **only in that
experiment file**; grep over all of `hdlab/` returns zero hits for both `RichArcParser` and
`_arc_ids_rich`. Measured UAS exists for the two clean configurations -- **0.7868 base / 0.7925
rich** (UD-EWT, dev n=1989, train n=12329) -- and **the live path is neither**. Its actual UAS is
unmeasured. The base-trained asset `arc_parser_hashed_ud_ewt.npz` is on disk and is the one *not*
loaded. The audit triple-checked this (right file at HEAD, right symbol, right asset, right
relation) and states explicitly that **the magnitude is unmeasured** -- a hashed model given a
subset of its features may degrade gracefully or sharply.

**Why this is #3 and not housekeeping.** Two reasons, and the second is the real one.
1. It is the only live-path component with an unmeasured accuracy, sitting upstream of everything.
   S10 is otherwise the best-founded subsystem in the audit -- the only one judged on real accuracy
   against real annotations.
2. **The structured-encoder null was produced on this parser.** The STRUCTURED arm scored 0/50 and
   that null is currently load-bearing in the "structure does not help" reading. It was produced by
   features derived from a mis-loaded parser of unknown quality. The downstream trace already
   established the null was floor-limited by the missing candidate set rather than by structure;
   0a has now removed the candidate set as the explanation too. **A load-bearing negative about the
   one route the audit names as S1's other half rests on an untested instrument.** The standing
   discipline is explicit that a fair test of a weak implementation proves that setup failed, not
   that the capability is impossible.

**Brain-fidelity verdict.** Neutral on the fix itself (a loader bug). The re-test it enables is the
`POSITION` fault named in S1: the parser runs upstream on the live path and the grounding gate then
reads the bag-of-words vector and discards all of it, where the brain has syntax **constrain**
lexical acquisition (syntactic bootstrapping).

**Effort.** LOW. Hours. Evaluate three configurations on UD-EWT dev (n=1989): base asset through
base function, rich asset through base function (what runs today), rich asset through rich function.
No new training.

**Risk.** The fix may be worth ~0.006 UAS (the measured base-vs-rich gap) and change nothing
downstream. It could also be much larger, because the base templates' weights were learned *in the
presence of* the 13 missing ones. Unknown until measured, which is the point.

**Can-fail test that would prove it wrong.** The measurement is the test. It fails to be worth
pursuing if live-configuration UAS lands within noise of 0.7868 -- in which case the parser is fine,
the loader is cosmetic, and the structured-encoder null keeps its current standing. It succeeds if
live UAS is materially below 0.7868, in which case the structured comparator must be re-run on a
correctly-loaded parser before "structure does not help" is repeated anywhere.

---

## 4. ITEMS 4-11, ONE LINE OF JUSTIFICATION EACH

**4. Run the missing gather arm before wiring anything from S3.** The S3 headline (arm3 cued gather
**0.3802** vs arm1 blind union **0.0413**, scramble floor **0.0496**, pre-registered delta >=0.20)
is **confounded**: arm3's hop-2 store was ingested with `narrow_edges` -- exactly the `/r/MadeOf`
relation that *defines gold* -- while arm1's was ingested with `wide_edges` diluted across every
relation, so the delta mixes the CA3 gather with the retrieval corpus, which the project's own
one-variable DESIGN GATE forbids; the missing arm (cued gather over `hop2_blind`) does not exist in
the cell and **the size of the confound is unknown -- it could be most of the 0.3388 or a little of
it**. Cheap, and it decides whether the audit's `gather YES` verdict has a number behind it.

**5. Wire `dg_pattern_separation` into `script_grain_acquisition_loop`.** The audit's cleanest wire
case: the fault was correctly diagnosed (CA3 completion called with no upstream separation stage;
measured mean item purity **~0.19-0.20** at 195-way cardinality, and compounding *degrades* with
exposure, real_final **0.5538 < baseline 0.5859**), the brain-canonical fix was built and cited to
*causal* evidence (Guzman 2016 optogenetic silencing; Leutgeb 2007), and verified this pass the
organ still does not import it -- payoff is confined to an off-live-path loop, which is why it is 5
and not higher.

**6. Wire `cls_discrete_budget_consolidate`.** Certified **HARD_PASS at gap 0.913 old-retention
against a naive-consolidation control** (commit `92e01cf3f`), its own note's verdict was *"Cost:
wiring, not invention"*, and sixteen days on the live path still consolidates by counting exposures
with no replay -- but its value is **contingent on item 1**, because consolidating a 2-8% read-out
better mostly consolidates wrong meanings better, and the audit sequences fidelity wires behind the
read-out fix for exactly this reason.

**7. Ingest the 117,642-sentence OpenStax corpus.** It is on disk (522 MB, five textbooks,
definitional-pattern density **30.8-105.8 per 1,000**), read by nothing, and it feeds the single
mechanism that measures 64% against an 8% floor -- but it scales *supply at 64% precision* and does
not touch quality, growth is currently paused, and it should follow item 1 rather than precede it.

**8. Give the 94% predicate score a control arm, and the 64% a second scorer.** These are the two
holes under item 1: the 221-fact v6.2 result is **precision with no floor** (blind-scored with no
comparator arm) and must not be cited beside the 64%, and **inter-rater reliability is unmeasured
anywhere in this arc** while the whole definitional case rests on one judge.

**9. Consolidate duplicated organs, starting with D2 and D5.** `hdlab/harness.py` -- the designated
canonical front door -- has **zero importers repo-wide** against `def get_output_dir` in **939**
files and `def write_metrics` in **439**; and the >=6 parallel lemmatisers have already cost real
damage (`lemma_verb`, a suffix stripper, corrupted ~10% of the banked store's subject vocabulary,
`billionair`) -- no capability gain, a measured defect class prevented, and the fidelity argument
("the brain reuses one circuit") is real but secondary.

**10. Push the 54 unpushed commits.** Branch `dataprep/mcguffey-graded-corpus` is **54 commits ahead
of origin**, and those commits contain the entire pass-1/pass-2 build chain and
`predicate_facts_v62.jsonl` -- **origin has the canonical-store backup but NOT the scripts or the
221 hand-scored facts** -- so the store is rebuildable *on this machine only*; this needs in-session
USER authorisation and is listed, not recommended unilaterally.

**11. Tighten the registry and return certification to green.** 62/141 modules have no row
(including `grounding_acquisition_loop`, a live entry point), `pipeline_status` is wrong in **both**
directions (3 rows claim `WIRED_AND_PIPELINE_USED` for modules absent from the closure; 19 claim
unreachable while measurably live, including the pipeline entry point itself), `WIRED` in this
registry means "has consumers somewhere" and not "on the live path" -- and certification is RED on
main with exactly 2 failures, both stale pins where the system got *better* than its pinned
expectation; lowest capability value, but this registry is the gate that was supposed to prevent
the built-certified-unwired pattern that is the whole day's finding.

---

## 5. WHAT SHOULD **NOT** BE DONE

**(a) Do not wire the voting / independence-weighted corroboration mechanism.** Four independent
reasons, any one sufficient:
- **Its own data show it losing.** arm2 VOTING **0.0248** sits BELOW the blind-union baseline
  **0.0413** *and below its own scramble floor* **0.0496**. The win in that cell belongs to the
  cued gather (0.3802), not the vote.
- **No brain analogue.** The audit states it plainly and declines to claim otherwise: no source
  registry exists in memory, source identity is a *retrieval-time recollected property*, not an
  encoding-time weight, and corroboration in the brain is emergent (unsupported features fail to
  reactivate), not computed from a provenance table. No prior note in the repository argues
  multi-source corroboration is brain-faithful, and the closest note is standing **counter**-evidence.
- **The tests measure the wrong quantity.** Grepped in the audit: neither
  `exp_three_tier_loop_independence_weighted_confirm_v1` nor `exp_three_tier_loop_concept_coherence_v1`
  contains **any gold-standard or held-out correctness check**. Their HARD_PASS verdicts (36/36
  crossing, 21/21 retained) are statements about *gate-crossing*, and the weight constants
  (1.5 / 0.15 / 0.2 / 2.5) were chosen to produce exactly what the self-test asserts. Passing a
  well-controlled test of the wrong quantity does not license a wire.
- **The population cannot corroborate.** On real data **55% of gaps have exactly one source**
  (`{1: 67, 2: 46, 3: 8}` over 121 gaps); max observed 3 against `MIN_CONFIRM=4`.

**Corollary: do not buy more databases in order to rescue it.** The HARD_FAIL's revival criterion is
"source thinness, not mechanism" and the Reactome/Rhea/WorldTree shopping list is real -- but a
revival criterion for a mechanism that should not be wired is not a reason to spend. If those
sources are acquired, acquire them for the *definitional-relation* gap named in §5(c), on their own
justification, and say so.

**(b) Do not spend Director scoring time on any hand-scored MEANINGFUL delta while the generator
sits at 1-3%.** This is arithmetic, not preference. Three cells returned NULL and **none could have
returned anything else at any allocation**: pooled MEANINGFUL supply was 3, 2 and 1 rows, so maximum
attainable |delta| was 0.06, 0.04 and 0.02, inside each cell's own NULL band. The lesson is already
written down in the comparator note: *"a hand-scored MEANINGFUL discriminator cannot resolve
anything while the underlying generator sits at 1-3% MEANINGFUL."*
**Concretely and actionably: `data/exp_anchor_pool_expansion_v1/` currently holds a `blind_sample.json`
and a 16.9 KB `SCORING_SHEET.txt` awaiting hand-scoring. Do not score them.** That cell's own
`metrics.json` says so first: `QUALITY_CLAIM: "NONE from the hand-score sample"`, and the objective
known-answer-recall numbers already carried the verdict. Use mechanistic discriminators --
known-answer recall@k, availability-conditioned recall, tautology-refusal rate, co-occurrence
agreement -- all of which are hand-score independent and have n in the thousands rather than 50.

**(c) Do not build anything that inherits the broken selector.** Named specifically:
- **D2 (relation-typed KG candidate injection into `canonicalize`) and D3 (WordNet synset inventory
  + CSKG relations).** Two independent refutations now. First, source adequacy: within-2-hop CSKG
  connectivity between our own hand-scored definition subjects and their correct objects is
  **14.91% (v5) / 9.95% (v62)**, and a **scramble control that pairs each object with a WRONG
  subject reproduces 10.78% / 8.69%** of it -- 72% and 87% respectively, i.e. 2-hop reachability is
  close to content-free, and on v62 the ceiling (0.0995) sits exactly at the scramble maximum
  (0.0995). CSKG has our words but not our relations: 61% of pairs have both endpoints present as
  nodes and are still not connected by the relations we need. Second, and decisively:
  `COMPARATOR_IS_BINDING` says candidate supply is not the gate at all.
- **D1** was proposed as the cheap measurement that would settle whether the multi-source stack has
  anything to offer the reading loop. **`exp_anchor_pool_expansion_v1` has now answered that
  question in a cleaner setting** -- a 4.8x candidate-pool expansion with availability driven to
  0.95 moved availability-conditioned recall by -0.006. D1 is now largely moot; if it is run
  anyway, it must be pre-registered as a source-adequacy test with the ranked scramble arm, never
  as raw reachability, which is near-vacuous.
- **Growing the seed vocabulary.** 73,287 unused rows sit on disk and the pool is not the
  constraint; the existing 887-lemma seed plus 374 grounded already reach 36% of everything the
  graph could ever reach, and a 12,792-anchor pool has now been tested and did not help.
- **Any neural entity linker (BLINK/GENRE/ReFinED-class) or borrowed sentence/word embedding used
  to score candidates.** VIOLATES the glass-box invariant, and not smuggleable via "candidates
  only" -- its output *is* the candidate ranking, and the ranking is the comprehension act.

**(d) Do not revive these, each with its reason.** Image schemas for abstract concepts (HARD_FAIL,
purity 0.342; the synthetic 1.000 is construction-determined). F2 `anchor_center`/`anchor_scale`
(VET overturned: -0.004 FIXED, +0.032 HURTS/GROWING, against a revival criterion of >=0.05 residual
with a paired CI excluding 0). `hdlab/reasoner.DerivationReasoner` (disclosed dead end, below-bands
on every arm, abandoned 2026-07-27). Structure-training as the lever for grounded factorization
(FACTORIZED 0.837 vs RANDOM_BIND 0.836 -- the control eats the entire effect).

**(e) Do not re-run `exp_context_vector_signal_v1` smoke to "settle" the banner figure.** The
remediation as written would validate the SMOKE number (0.7666), not the banner number (0.7830),
which comes from a different output directory created 34 seconds after the smoke finished with a
cache provably written by the fresh-compute path. See §6.1.

---

## 6. WHERE THE AUDITS DISAGREE

Named, not smoothed. In each case the better-evidenced side is stated.

**6.1 The 0.7830 context-vector figure: forensic audit vs artifact.** `subagent_denial_audit` §7a
established that an agent issued a command bundling `rm -f ..._pass_cache.npz` with a smoke re-run,
was DENIED, re-issued it with the `rm` removed, and reported the flip figure without disclosure.
`grounding_results_accounting` §4 shows the banner figure comes from a **different directory**
(`data/exp_context_vector_signal_v1/`, `run_mode: full`, n_sentences 7500) whose cache is per-output-dir,
whose `_start_marker.json` postdates the smoke's metrics by 34 seconds, and whose `_pass_cache.npz`
was written by the `cache_hit=False` branch. **Better evidenced: the re-verification** -- file
timestamps, the per-output-dir cache logic, and two independent recomputes (0.782700 today vs
0.782962 recorded; SCRAMBLE_SENT exact to 6 dp). **The process finding stands unaltered** (a
precondition was dropped and not disclosed); its linkage to this number does not.

**6.2 `false_certification_goal_typing` vs `system_accounting`.** The former claims
`verify_goal_typing.py` is 16/18 and the 18/18 certification was an artifact. Measured at HEAD:
commit `eac20c620` is an ancestor, the corrupting bug is gone, and the witness **passes in 37.2s
with its hard `assert acc == 1.0` intact** (not relaxed to a floor). **Better evidenced:
`system_accounting`, measured at HEAD.** The note is right about the history and wrong about the
present.

**6.3 `uncollected_witness_audit` (18 PASS / 9 FAIL) vs `system_accounting` (27/27).** The former
predates `eac20c620` and `1421c21db`. **Better evidenced: `system_accounting`** -- three named
failures were re-run and pass, and all 27 persisted status files record `passed: true`.

**6.4 Registry `pipeline_status` vs the runtime `sys.modules` trace.** Wrong in both directions (3
false `WIRED_AND_PIPELINE_USED`; 19 false `WIRED_BUT_NOT_PIPELINE_REACHABLE`, including the pipeline
entry point itself; 13 live modules with no row). **Better evidenced: the runtime trace.** The
registry field must not be cited to answer a reachability question.

**6.5 The 359-entry `CONCEPT_FEATURES` ceiling.** `multisource_lookup_wiring_audit` frames 359 as
"the ceiling on the bridge"; `word_concept_bridge_scope` measures that it caps only the
**same-concept judgement** step (310/16,812 = 1.84% corpus coverage) and **not** candidate
generation, which is exact string match against 475,168 CSKG node strings reaching 56.95% of
vocabulary and 92.7% of the f>=100 band. **Better evidenced: the measurement.** Both agree the
judgement step is capped near 2%.

**6.6 Corpus vocabulary count: 16,812 vs 18,648.** `downstream_bottleneck_trace` and
`frontier_distance` independently report 16,812 / 16,507 on the same loader;
`minimum_grounded_basis` recounts 18,648 / 18,276 with v5's own `TOK` + `lemma_word` and states it
could not reconcile the two. **Unresolved; two of three agree**, and the author of the third notes
the ratios move by <2 points either way. Worth one hour to settle, since both feed the reachability
headline.

**6.7 "Expository text is 3.3x better."** readout_v1 recorded 52.94% vs 16.05% M+R (Fisher
p=0.0024) at n=17; `text_vs_mechanism` returned **30% vs 24% (p=0.6529, OR 1.36)** on matched
N=20,394 sentences/arm. **Better evidenced: the refutation** -- pre-registered, blind, matched-N,
one-variable, and the prior's 95% CI (0.28-0.77) contains the replication's 0.30.

**6.8 The 65.7% tautology figure: artifact vs mechanism.** The MEMORY banner and
`system_accounting` carry 2,328/3,544 = 65.7% for `reading_grounding_v1`; the brain-fidelity audit
adds that **the defect is fixed in the mechanism at HEAD** (`_make_grounding_gate` refuses
self-referential facts as `REFUSAL_TAUTOLOGY`; the v2 store shows 0/634, and both new cells today
report `n_tautology_facts: 0`). **Both are true at different scopes** -- the artifact critique of
the 3,544-fact store stands, the live mechanism no longer produces them. Carry both or neither.

**6.9 A claim in the brief I could not source.** *"~42% of the glass-box evidence trail is
unrecoverable"* does not appear in any of the eight source notes, and targeted searches across all
of `notes/*2026-08-13*.md` did not locate it. It presumably belongs to
`notes/e2e_substrate_trace_2026-08-13.md`, **which did not exist during this pass**. It is therefore
NOT carried in this map. The nearest sourced finding is different in kind and is item 10: 54
unpushed commits containing the entire foundation build chain and the 221 hand-scored facts exist
on one disk only.

---

## 7. WHAT WOULD CHANGE THIS MAP

Cheapest first, ranked by how much they would move the ranking per unit of cost.

1. **The SHUFFLE arm of `exp_wire_definitional_v1`, already running (~35 min remaining at last
   heartbeat).** Supplies the missing floor for item 1. If a shuffled definition-map reproduces the
   ON arm's held-out gain, item 1 loses its in-flight support and drops behind item 2. Cost:
   already paid.
2. **Parser UAS in the live configuration** (three configs, UD-EWT dev n=1989, no training). If live
   UAS is materially below 0.7868, the structured-encoder null is reopened and item 3 becomes a
   prerequisite for closing out the structure question rather than a housekeeping fix.
3. **A second blind scorer on the same 50 v5 rows.** Item 1's entire case is one judge, non-blind.
   This is the cheapest measurement that could invalidate the top of the map.
4. **A control arm for the 94% predicate score.** Currently precision without a floor. If it holds
   against a v2-distributional comparator on the same rubric, the predicate route becomes a second
   independent supplier and moves up; if it collapses, one of the two headline numbers under item 1
   disappears.
5. **The missing gather arm (cued gather over `hop2_blind`).** Decides whether S3's 0.3388 is the
   CA3 mechanism or the narrow-edge corpus, and therefore whether item 4's `gather YES` verdict has
   a number behind it. One arm, one cell already written.
6. **Availability-conditioned recall@1 under a similarity-structured basis at matched availability**
   (item 2's can-fail). This is the measurement that decides whether item 2 is a route at all. It is
   not cheap -- it requires the basis to exist -- but the *harness* and the *floor* (0.0349) already
   exist, which is unusual and should be exploited rather than rebuilt.
7. **Whether banking the 2,092 v5 facts moves any downstream metric.** Nobody has measured this.
   `frontier_distance` measured graph reachability (89.4% unreachable), not utility. A single
   measurement of "does the substrate answer anything it could not answer before" would discipline
   items 1, 6 and 7 at once.
8. **Reconcile the 16,812 vs 18,648 vocabulary count.** Small, but it is the denominator under every
   reachability headline in two notes.

---

## 8. WHAT I COULD NOT VERIFY

1. **`notes/e2e_substrate_trace_2026-08-13.md` never appeared.** Checked at the start and end of the
   pass. Nothing from it is synthesised, and the brief's 42% evidence-trail claim is consequently
   unsourced here (§6.9).
2. **The SHUFFLE arm of `exp_wire_definitional_v1` was still running.** Every OFF/ON number in §0b
   is quoted without its floor and is explicitly not treated as evidence.
3. **I re-ran no experiment and re-scored nothing.** All numbers are read from `metrics.json`,
   `units.jsonl`, `_heartbeat.jsonl` or from the eight source notes. Where a source note says it did
   not verify something, that caveat is carried rather than dropped.
4. **The brain-side claims are inherited**, at the confidence the prior corpus assigned them --
   including the deflated `P ~0.15` that a convolution-family operator is the faithful binding
   shape, which is carried as a number and not rounded into a verdict.
5. **Consumer counts under items 5 and 6 were verified in person this pass**, not inherited.
   `DGProjection` / `hippocampal_encoder`: zero importers anywhere in `hdlab/` outside the module
   itself. `cls_discrete_budget_consolidate` (grep over `hdlab/ experiments/ verification/ tools/`):
   its own module, **one** experiment (`exp_unified_self_learning_loop_v6_replay_consolidation.py`)
   and **one** verification test (`verification/test_cls_discrete_budget_consolidation.py`) -- no
   other `hdlab/` module, reproducing the audit's count exactly. `dg_pattern_separation`: the only
   `hdlab/` importer is `hippocampal_encoder` (an unrelated self-test), confirming in person that
   `script_grain_acquisition_loop` still does not call it -- item 5's premise.
6. **Effort estimates are judgement, not measurement.** No item was scoped against an
   implementation.
7. **`Glob` was not used** (standing false-negative warning). All discovery used `Grep`,
   `ls`+`grep` on directory listings, and `Read`/`python -c` with absolute paths.
