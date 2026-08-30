---
problem: stress_test_which_organ_wins_actually_generalize_on_held_out_text
status: SOLVED
bar: "DELIVERABLE = a GENERALIZATION LEDGER (per audited organ: constructed number -> held-out number -> HOLDS/DOES-NOT-HOLD + the population + the floor + the twin). Plus an AUDIT UPDATE to BRAIN_FOUNDATIONAL_AUDIT.md per reclassified organ." AND per organ "HOLDS = the organ's headline metric beats its strongest floor recomputed ON THAT population, CI-separated (bootstrap; report CI half-width + null p95), with the info-free twin LOSING. NO number crosses populations/scorers."
result: "GENERALIZATION LEDGER over all 33 keyword-flagged organs: 10 FALSE POSITIVES (already held-out-validated at n=995..28,569), 9 ALREADY NEGATIVES (SOLVED is itself a refutation on real data), 13 GENUINELY FRAGILE (constructed/synthetic-only). DEEP RERUN of the top load-bearing fragile cluster (store/retrieval/binding) on real LitBank who-did-what (n=28,569 events, 7,779 entities, gold coref): the content-addressable separated store's synthetic SEP_CA-over-FLAT win of +0.94 (0.990 vs 0.047 @ load=32) generalizes DIRECTIONALLY but its MAGNITUDE collapses ~15x to a real-frequency-weighted ~+0.06 on real text -- CI-separated ABOVE only for entities with >=4 events (12.7% of the population); at <=3 events (87.3%) SEP_CA ties FLAT (NOT_SEP) because FLAT is already >=0.98. Verdict: HOLDS-DIRECTIONALLY / MAGNITUDE-DOES-NOT-HOLD -> wire for busy entities only, not the population."
floor: "per-entity verb COUNTING (predict the entity's most-frequent verb, cue-blind -- the flat_store_destroys_the_code lesson), recomputed on real LitBank: 1.000 @1 event, 0.561 @2-3, 0.348 @4-8, 0.169 @17-63, 0.138 @64+; AND the FLAT superposition read-out (the incumbent live register op) recomputed per load bin. SEP_CA beats COUNTING CI-separated wherever an entity has >=2 events, but ties FLAT at <=3 events."
controls: "SYNTHETIC POSITIVE CONTROL: the imported arms reproduce the organ's own win (SEP_CA 0.990 vs FLAT 0.047 @ synthetic load=32,p=0.7) -> a real-data null is a generalization gap, not a broken harness. INFO-FREE TWINS: SHUFFLED_KEYS + RANDOM_ROUTE LOSE CI-separated wherever the mechanism fires (>=2 events). LOAD STRATIFICATION: the SEP-FLAT margin is a monotone function of entity event-count, ~0 at the real median (1 event). DG BUILD-ACROSS DRILL: SEP_CA_DG < SEP_CA (BELOW) on identity-orthogonal real codes -- DG-at-retrieval hurts a task whose codes are already separated by word identity. COUNTING floor recomputed per population."
files_changed: "experiments/exp_generalize_retrieval_real_codes_v1.py, verification/test_generalize_retrieval_real_codes.py, notes/problems/stress_test_which_organ_wins_actually_generalize_on_held_out_text/GENERALIZATION_LEDGER.md, notes/problems/stress_test_which_organ_wins_actually_generalize_on_held_out_text/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_generalize_retrieval_real_codes.py"
---

# SOLVED — a generalization ledger over 33 organs, plus a rigorous rerun of the store/retrieval cluster on real text

**The stress-test is built and run.** The keyword triage tool (`tools/generalization_audit.py`) flags 33
organs as "constructed-headlined / thin generalization tail." It OVER-FLAGS by design — a keyword scan
cannot separate "constructed win + STRONG held-out" from "constructed win + THIN held-out." I read the
actual `SOLVED.md` of all 33, recorded each one's real held-out n / population / floor / wiring status, and
**reran** the top load-bearing genuinely-fragile cluster on a pre-existing corpus. Full ledger:
`GENERALIZATION_LEDGER.md`.

## What the triage found (the keyword tool over-flags by ~2.5×)

Of the 33 keyword-fragile organs:
- **10 are FALSE POSITIVES** — already validated on pre-existing corpora at n = 995 … 28,569, CI-separated,
  twin losing (QA-SRL 17k/28k, LitBank 4.6k/28.5k, SimLex-999/SimVerb-3500, GAP). `lookup_does_not_lemmatise`,
  `the_argument_parser…`, `the_entity_store…`, `discrete_where_the_brain_is_graded…`, `optimize_and_validate_the_learner…`,
  `the_situation_model_tracks_words_not_entities`, `theory_of_mind_residual…`, `pronoun_to_event_binding…`,
  `the_register_reads_by_argmax…`, `dimensional_phase_diagram…`. **Do NOT re-audit these.**
- **9 are ALREADY NEGATIVES** — the `SOLVED` is itself a rigorous refutation on real/held-out data (exactly
  the outcome this audit exists to produce): `flat_store_destroys_the_code` (addressed 0.14 loses to counting
  0.32 on real SimpleWiki — the archetype), `the_reading_extractor…`, `the_discourse_fact_reasoner…`,
  `the_reader_has_no_coherence_next_mention_prior`, `causation_is_typed_per_clause…`, `the_sign_quantiser…`,
  `reader_meaning_channel`, `teach_the_self_built_space…`, `wire_the_validated_organs…`.
- **13 are GENUINELY FRAGILE** — a constructed/synthetic win with no strong pre-existing validation. Ranked
  by load-bearing × fragility (table in `GENERALIZATION_LEDGER.md`). The top four (T1a–d) are the foundational
  store/retrieval/binding cluster and share ONE claim; I reran it.

## The deep rerun — the store/retrieval/binding cluster on real LitBank

**The shared claim of the top cluster** (`content_addressable_retrieval_over_a_separated_store`,
`the_core_binding_operator_may_not_be_brain_faithful`, `resolve_retrieval_interference…`,
`the_register_write_path…`): *a SEPARATED, content-addressable / CA3 store beats a FLAT superposition
read-out under load / partial cue.* Every one proved it on a **synthetic random codebook at fixed high load
(32–64 items/register)**. The organs themselves flag this ("an isolation win is not a capability"; "is the
substrate's REAL context separable?"). And the one prior real-text test of the family
(`flat_store_destroys_the_code`) **LOST** to counting.

**What I ran** (`experiments/exp_generalize_retrieval_real_codes_v1.py`): the EXACT retrieval arms imported
verbatim from the content_addressable cell — `arm_flat`, `arm_sep_ca` (+DG), `arm_shuffled_keys`,
`arm_random_route` — on the **real LitBank who-did-what population** (n=28,569 events, 7,779 entities, gold
coref) as **per-entity registers at each entity's REAL event count**, real Zipfian verb fillers (same verb →
same code = real confusability), against the strongest real floor (**per-entity verb COUNTING**), the
info-free twin, and a synthetic **positive control**.

**The real operating point IS the finding.** 72.6% of real entities carry **1** event; 87.3% carry ≤3. The
synthetic organs live at load=32 — ~2% of real entities. Per-bin (partial cue p=0.7):

| entity events | % of real | SEP_CA | FLAT | **SEP−FLAT** (the organ's claim) | SEP−COUNTING | twin loses |
|---|---|---|---|---|---|---|
| 1 | 72.6% | 1.000 | 1.000 | +0.000 tie | +0.000 tie | — |
| 2–3 | 14.7% | 1.000 | 0.981 | **+0.019 NOT_SEP** | +0.439 ABOVE | yes |
| 4–8 | 6.5% | 1.000 | 0.742 | +0.258 ABOVE | +0.652 ABOVE | yes |
| 9–16 | 2.6% | 0.999 | 0.456 | +0.543 ABOVE | +0.761 ABOVE | yes |
| 17–63 | 2.4% | 0.990 | 0.178 | +0.811 ABOVE | +0.821 ABOVE | yes |
| 64+ | 1.2% | 0.976 | 0.052 | +0.924 ABOVE | +0.839 ABOVE | yes |

*(smoke pass n=60/bin; the full real-frequency-weighted run confirms the pooled ~+0.06 and the bands — see the metrics.)*

**Verdict: HOLDS DIRECTIONALLY, MAGNITUDE COLLAPSES ~15×.** The synthetic **+0.94** (SEP over FLAT) shrinks
to a real-frequency-weighted **~+0.06** on LitBank — because 87% of entities have ≤3 events, where FLAT is
already ≥0.98 and SEP does not beat it. The mechanism is *real* (twin loses; beats counting wherever an
entity has ≥2 events) but its value is concentrated in the ~10–13% of "busy" entities (≥4 events). **This is
neither the 0.99 the headline implies nor a `flat_store`-style collapse — it is a precise deployed-value
correction: wire the separated store for busy entities, not for the population.**

## HOW THE BRAIN DOES THIS — and the DG surprise

The PINNED standard here is generalization/systematicity itself: the brain applies a learned computation to
novel instances; a competence that only fires at its training operating point is a lookup, not the operation.
CA3 content-addressable completion is real, and DG pattern-separation (Leutgeb 2007; McHugh 2007; Nakazawa
2002) is what lets CA3 work on similar memories. My brain-foundational hypothesis going in was: *real codes
are correlated, so DG should be NEEDED on real text.* **The data refuted my own hypothesis, precisely.** With
real verb codes that are already **identity-orthogonal** (same word → same code, different words → orthogonal),
DG-at-retrieval **HURTS** (SEP_CA_DG 0.49–0.63 vs SEP_CA 0.98 at the tail) — decorrelating an already-clean
code destroys structure. DG earns its keep only where codes are genuinely correlated (near-synonyms); the
who-did-what register's confusability comes from *repetition* ("say"/"be" recur), not code correlation, so DG
is a fix for a problem this task does not have. The correlated-codes drill in the full run tests exactly the
regime where DG should help. → **AUDIT UPDATE below.**

## What I did NOT establish / would withdraw first

1. **The other 12 fragile organs are triaged, not reran.** I reran the top cluster (T1); T1c
   (`resolve_retrieval_interference` context axis), the two causation typers, ToM-microworld, the N400
   segmenter, the relcl parser, etc. are enumerated with their pre-existing rerun corpora in the ledger but
   NOT yet reran. The sweep is valuable partial (brief-sanctioned) but incomplete. **Withdraw first:** any
   implication that a Category-C organ NOT reran is confirmed fragile — the triage says its *headline* is
   constructed, not that it *fails* held-out.
2. **The per-entity register framing is one faithful choice, not the only one.** I follow
   `register_completion_real_litbank` (unit = entity, competitors = its own events). A per-*document* register
   (unit = all events in the discourse) would superpose ~286 items and make FLAT collapse — inflating the
   SEP win. I chose the per-entity framing because the brain does not hold a whole novel in one working
   register (max_event_slots ≈ 8); a reviewer could argue the realistic M is a recent-events window, between
   the two. The ~+0.06 is the conservative (per-entity) estimate.
3. **Fillers = gov_verbs under gold coref.** I test the retrieval architecture on real *content* with clean
   *structure* (gold clusters), deliberately excluding the ~0.32-recall extraction noise — that is the right
   isolation for a retrieval-architecture generalization test, but the end-to-end number under real extraction
   is a separate (already-negative) problem (`wire_the_validated_organs…`).

## KEY REALIZATIONS (the enabling moves)

- **The keyword tool's FRAGILE list is a candidate list, not a verdict — reading the n is the whole job.**
  Two of its "fragile" hits were validated on 17k/28k held-out items. 10 of 33 flags were false. *A
  generalization audit that trusts a keyword scan reproduces the exact failure it is auditing.*
- **A synthetic win's headline number is set by the OPERATING POINT, and the operating point is a fact about
  the corpus, not the mechanism.** The content-addressable win didn't shrink because the mechanism is wrong —
  it shrank because real entities carry ~1 event and the synthetic headline was measured at 32. *The
  generalization question is not "does the mechanism work?" but "does its regime occur in real text?"* — and
  the answer here is "rarely." That reframe is what turned a pass/fail scan into a deployed-value number.
- **A positive control that reproduces the organ's OWN win is what licenses the negative.** Because the
  imported arms give SEP_CA 0.990 vs FLAT 0.047 at load=32, the ~+0.06 on real text cannot be dismissed as a
  broken port — it is the same code, only the population changed.
- **My brain-foundational prior was falsifiable and got falsified in the right direction.** I predicted DG
  would be needed on real (correlated) codes; measuring it showed DG hurts because real word-identity codes
  are already orthogonal. Running the drill instead of asserting the prior is the difference between a
  finding and a story.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b)

- **STORE / RETRIEVAL cluster (content_addressable / core_binding / register_write):** the separated
  content-addressable store's advantage over flat superposition is a **steep function of load** and the real
  LitBank who-did-what operating point (median 1 event/entity) is deep in the regime where flat superposition
  is already near-perfect. Deployed value on real text ≈ **+0.06 hit@1** (real-frequency-weighted), vs the
  **+0.94** synthetic headline — concentrated in the ≥4-event minority. Reclassify these organs from
  "validated separated-store win" to "**validated, but wire for high-fan entities only; population-level lift
  is ~+0.06, not the isolation figure.**"
- **`hdlab/dg_pattern_separation.py` at RETRIEVAL:** confirmed a **negative on identity-orthogonal codes**
  (DG decorrelation destroys already-separated structure; SEP_CA_DG < SEP_CA). DG is a fix for *correlated*
  codes only. Do not wire DG-at-retrieval onto register codes keyed by symbol identity.
- **Generalization method:** the strongest free predictor (test items existed before the mechanism) confirmed
  again — the 10 false-positives all pre-existed their mechanisms; the collapse-prone organs were all
  validated at a synthetic operating point. `tools/generalization_audit.py` should print, next to each FRAGILE
  flag, the held-out n parsed from its SOLVED, so the false-positive rate is visible.

---

## TLDR (plain language)

We often prove a new brain-part works by testing it on examples chosen to make it look good. This job checked
which of those wins survive on real books the part was never tuned for. Reading the records of 33 flagged
parts: about a third were already proven on big real datasets (a false alarm), about a third had already been
honestly shown to fail on real text, and about a third had only ever been tested on made-up examples. For the
most important of the untested group — the "memory retrieval" parts that everything else reads through — I
reran the actual code on a real corpus of 100 novels. The headline said retrieval-by-content beats the simple
method by a huge margin; on real text that margin shrinks about 15-fold, because real characters are usually
involved in just one or two actions, where the simple method is already almost perfect. The fancy method only
pulls ahead for the rare "busy" characters with many actions. So it is worth switching on for those, not for
everyone. A bonus surprise: a brain-inspired "keep-memories-distinct" step that I expected to help actually
hurt here, because the memories were already distinct.

## QUESTIONS

None — the triage is complete for all 33, the rerun is CI-separated with a floor, an info-free twin, and a
positive control that reproduces the original win, and the deployed-value correction is quantified.

## NEXT STEPS

- **Rerun the remaining Category-C organs** on the pre-existing corpora named in the ledger (highest value:
  `resolve_retrieval_interference` on LitBank/OntoNotes similar-competitor coref with the substrate's REAL
  context vector — the solver's own open question; then the two causation typers on MAVEN-ERE/UD-EWT at scale).
- **Strategy (Q111):** fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md`; annotate the store/retrieval
  organs "wire for high-fan entities only (~+0.06 population lift)"; add the held-out-n column to
  `tools/generalization_audit.py` so the false-positive rate is visible on every future scan.
- **No hdlab change is required by this problem** — it is a measurement/audit. The one code-relevant finding
  (do not wire DG-at-retrieval onto identity-orthogonal register codes) is a "do-not," not a diff.
