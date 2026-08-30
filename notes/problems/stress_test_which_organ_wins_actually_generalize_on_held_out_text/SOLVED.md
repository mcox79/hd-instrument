---
problem: stress_test_which_organ_wins_actually_generalize_on_held_out_text
status: SOLVED
bar: "DELIVERABLE = a GENERALIZATION LEDGER (per audited organ: constructed number -> held-out number -> HOLDS/DOES-NOT-HOLD + the population + the floor + the twin). Plus an AUDIT UPDATE to BRAIN_FOUNDATIONAL_AUDIT.md per reclassified organ." AND per organ "HOLDS = the organ's headline metric beats its strongest floor recomputed ON THAT population, CI-separated (bootstrap; report CI half-width + null p95), with the info-free twin LOSING. NO number crosses populations/scorers."
result: "GENERALIZATION LEDGER over all 33 keyword-flagged organs (10 FALSE POSITIVES already held-out-validated at n=995..28,569; 9 ALREADY NEGATIVES; 13 GENUINELY FRAGILE) + TWO rigorous reruns covering SIX organs with CONTRASTING outcomes: (RERUN 2) the CAUSATION-TYPER cluster (T2a/T2b) reran on real MAVEN-ERE (n=9,698 annotated causal relations) DOES NOT HOLD -- the force-dynamic typer fires on only 16.1% of real causal relations and where it fires its force signal is indistinguishable from a shuffled-lexicon twin (+0.018 NOT_SEP), losing to the majority floor by -0.679 (constructed win was 0.929/1.000 on n=42/40 minimal pairs). (RERUN 1) DEEP RERUN of the top load-bearing fragile cluster (store/retrieval/binding) on real LitBank who-did-what (n=28,569 events, 7,779 entities, gold coref; real-frequency-weighted, full run n_sampled=1376, 658s): the content-addressable separated store's synthetic SEP_CA-over-FLAT win of +0.94 (0.990 vs 0.047 @ load=32, harness-reproduced) generalizes DIRECTIONALLY but its MAGNITUDE collapses 15-60x on real text: SEP-FLAT = +0.060 [0.050,0.070] at partial cue p=0.7 / +0.016 [0.011,0.022] at full cue -- CI-separated ABOVE but tiny, concentrated in the ~13% of entities with >=4 events (per-bin SEP-FLAT ~0 at <=3 events where FLAT is already >=0.98, +0.20 at 4-8, +0.92 at 64+). The BROADER capability DOES survive: SEP-COUNTING = +0.156 [0.142,0.170] CI-separated (a register beats pure counting on real text, unlike flat_store) -- but FLAT also beats counting (+0.096..+0.140), so the SEPARATED-store increment is the small +0.06. Verdict: HOLDS-DIRECTIONALLY / MAGNITUDE-DOES-NOT-HOLD -> wire for busy entities only, not the population."
floor: "per-entity verb COUNTING (predict the entity's most-frequent verb, cue-blind -- the flat_store_destroys_the_code lesson), recomputed on real LitBank: 1.000 @1 event, 0.561 @2-3, 0.348 @4-8, 0.169 @17-63, 0.138 @64+; AND the FLAT superposition read-out (the incumbent live register op) recomputed per load bin. SEP_CA beats COUNTING CI-separated wherever an entity has >=2 events, but ties FLAT at <=3 events."
controls: "SYNTHETIC POSITIVE CONTROL: the imported arms reproduce the organ's own win (SEP_CA 0.990 vs FLAT 0.047 @ synthetic load=32,p=0.7) -> a real-data null is a generalization gap, not a broken harness. INFO-FREE TWINS: SHUFFLED_KEYS + RANDOM_ROUTE LOSE CI-separated wherever the mechanism fires (>=2 events). LOAD STRATIFICATION: the SEP-FLAT margin is a monotone function of entity event-count, ~0 at the real median (1 event). DG BUILD-ACROSS DRILL: SEP_CA_DG < SEP_CA (BELOW) on identity-orthogonal real codes -- DG-at-retrieval hurts a task whose codes are already separated by word identity. COUNTING floor recomputed per population."
files_changed: "experiments/exp_generalize_retrieval_real_codes_v1.py, experiments/exp_generalize_retrieval_similar_competitor_gate_v1.py, experiments/exp_generalize_causation_typer_maven_ere_v1.py, experiments/exp_generalize_causation_implicit_covariation_gate_v1.py, verification/test_generalize_retrieval_real_codes.py, notes/problems/stress_test_which_organ_wins_actually_generalize_on_held_out_text/GENERALIZATION_LEDGER.md, notes/problems/stress_test_which_organ_wins_actually_generalize_on_held_out_text/research_retrieval_interference_load_and_dg_boundary_2026-08-30.md, notes/problems/stress_test_which_organ_wins_actually_generalize_on_held_out_text/research_causation_typer_wall_implicit_and_mental_causation_2026-08-30.md, notes/problems/stress_test_which_organ_wins_actually_generalize_on_held_out_text/SOLVED.md"
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

*(smoke pass n=60/bin shown; the full real-frequency-weighted run, n_sampled=1376, confirms: pooled
SEP−FLAT **+0.060** [0.050,0.070] @p=0.7 / **+0.016** [0.011,0.022] @full cue; SEP−COUNTING **+0.156**
[0.142,0.170]; twin loses **+0.144**. Per-bin SEP−FLAT @p=0.7: +0.000 / +0.022 / +0.204 / +0.525 / +0.813 /
+0.924.)*

**Verdict: HOLDS DIRECTIONALLY, MAGNITUDE COLLAPSES 15–60×.** The synthetic **+0.94** (SEP over FLAT) shrinks
to a real-frequency-weighted **+0.060** at a degraded cue (and **+0.016** at a full cue) on LitBank — because
87% of entities have ≤3 events, where FLAT is already ≥0.98 and SEP does not beat it. The separated-store's
advantage is *real* (twin loses; CI-separated) but concentrated in the ~13% of "busy" entities (≥4 events).
**Two honest readings, both true:** (1) the organ's SPECIFIC claim — *separated beats flat superposition* —
survives only as a small, busy-entity-only +0.06; (2) the BROADER claim — *a register read-out beats pure
counting* — survives robustly at **+0.156** (unlike `flat_store`, which LOST to counting), but FLAT already
delivers most of that (+0.10–0.14), so the separated machinery adds little on the population. **Wire the
separated store for busy entities, not for the population.**

## HOW THE BRAIN DOES THIS — and the DG surprise

The PINNED standard here is generalization/systematicity itself: the brain applies a learned computation to
novel instances; a competence that only fires at its training operating point is a lookup, not the operation.
CA3 content-addressable completion is real, and DG pattern-separation (Leutgeb 2007; McHugh 2007; Nakazawa
2002) is what lets CA3 work on similar memories. My brain-foundational hypothesis going in was: *real codes
are correlated, so DG should be NEEDED on real text.* **The data refuted my own hypothesis, precisely — and
the correlated-codes drill sharpened WHY.** DG-at-retrieval **HURTS** at the tail (SEP_CA_DG 0.50–0.64 vs
SEP_CA 0.98) — and it hurts by the *same* −0.35 to −0.48 whether the verb-filler codes are identity-orthogonal
OR deliberately correlated (near-synonyms sharing a base phase). So DG is not "for correlated fillers." The
retrieval MATCH runs over the **addresses** — `bind(entity, event-index)` — and those are **unique by event
index** in a per-entity register, so the match is already near-perfect and DG's expand+sparsify only injects
noise. DG is a fix for confusable **addresses** (the fan / key-overlap `rho>0` regime — which is exactly where
the content_addressable organ's own sweep found DG helps), and the real who-did-what register does not have
that: its addresses are distinct by construction. → **AUDIT UPDATE below.**

## SECOND RERUN — the causation-typer cluster on real MAVEN-ERE → a clean DOES-NOT-HOLD

To make the ledger rest on more than one rerun, I reran the **causation-typer cluster** (`causation_has_no_force_dynamic_typing`, `causation_typing_needs_a_patient_tendency_estimator`) — headlined 0.929 / 1.000 on n=42 / n=40 **minimal pairs** — on **MAVEN-ERE** (Wang et al. 2022), **n=9,698 independently-annotated causal relations**, importing the organ's own FrameNet force-lexicon + Wolff typer verbatim (`experiments/exp_generalize_causation_typer_maven_ere_v1.py`). **Result: DOES NOT HOLD.** The typer FIRES on only **16.1%** of real causal relations (its force-verb input is usually absent), and where it fires its force signal is **statistically indistinguishable from a shuffled-lexicon twin** (+0.018 NOT_SEP) for the real CAUSE-vs-PRECONDITION distinction, losing to the majority floor by **−0.679**. This confirms the sibling organ's LitBank negative (0.158 vs 0.842, n=19) on a **500× larger** corpus. Disclosed caveat: MAVEN's PRECONDITION ≠ Wolff's ENABLE (ontology mismatch), but the two decisive facts — 16% fire-rate and typer≈shuffled-twin — are ontology-independent. Full detail + AUDIT UPDATE in `GENERALIZATION_LEDGER.md`. **The sweep now rests on two rigorous, contrasting reruns (a holds-with-nuance and a clean negative) covering six organs, plus the full 33-organ triage.**

### …then pushed the causation wall the same way (research drill + a decisive gate)

Applying the retrieval-wall discipline ("did I test the right thing?"), a literature drill
(`research_causation_typer_wall_implicit_and_mental_causation_2026-08-30.md`) returned a PINNED verdict:
real narrative causation is a **whole-event causal-GRAPH** property inferred by a **different brain system**
(Trabasso & van den Broek causal-network; Kintsch construction-integration; Graesser causal-antecedent
inference; Zwaan-Radvansky causation dimension; Mason & Just 2004 + Kuperberg 2011 fMRI/ERP — implicit
connective-less causal inference recruits left IFG/MTG + rostral mPFC, an N400-only signature). The
force-dynamic typer is a **word-grain** mechanism meeting a **discourse-grain** problem — the 16% fire-rate
is exactly its footprint. Verdict: **narrowly-valid-but-mis-scoped (keep it for explicit physical-causal
predication), NOT a wrong primitive.** There is even a *verified absence* of any neural study of
force-dynamic causal verbs, while the implicit-inference network is PINNED — so the missing route is the
better-grounded one.

I then ran the empirical **gate** (`exp_generalize_causation_implicit_covariation_gate_v1.py`), symmetric
with the retrieval gate: does a glass-box **event-type covariation** scorer (learn P(label | cause_type,
effect_type) from MAVEN train — the Chambers & Jurafsky / Hu & Walker precedent) carry the causal signal the
force-dynamic route lacks? **Yes, decisively:** covariation **0.889** beats its own shuffled-type-pair twin
by **+0.094 ABOVE** (a real signal, where force-dynamics was +0.018 NOT_SEP), beats the majority floor by
**+0.056** (clearing the research's pre-registered +0.05 HARD-PASS), beats the force-dynamic typer by
**+0.165**, and works precisely on the **83.9% no-fire subset** (+0.058 over majority, +0.099 over twin).
**This empirically names the next problem** (`narrative_causal_graph_missing_implicit_inference_organ`) and
proves the missing mechanism is implicit event-type covariation / world-knowledge, not force-dynamic verbs.

## PUSHED FURTHER — the +0.06 measured the WRONG interference axis (research drill + a decisive gate)

A literature drill (`research_retrieval_interference_load_and_dg_boundary_2026-08-30.md`) on the wall the
rerun hit returned a decisive, PINNED verdict: **event-count-per-entity is not the brain's interference
axis — and is directly falsified as a primitive** (Radvansky & Zacks 1991: equal fact-count → no fan cost
once facts integrate into one situation model). The load-bearing axis is **similarity-based cue-overload** —
how many *other* active entities feature-match the retrieval cue (Van Dyke & McElree 2006, one-variable
causal; McElree SAT dissociation; Autry & Levine 2014 anaphor fan). **The who-did-what per-entity register,
with ~1 verb-event/entity and distinct verbs, structurally has near-zero competitor overlap — so it cannot
reveal the operation's value, and the +0.06 is the honest number for the *wrong axis*.**

So I ran the research's **cheap decisive gate** (`exp_generalize_retrieval_similar_competitor_gate_v1.py`) —
reframing the SAME corpus onto the right axis: "which of several entities did verb V near sentence s?"
Competitors = every entity who did V in the document; when a verb is shared by ≥2 entities, content
(the verb) under-determines. Result (n=**22,123** ambiguous queries, every document has them — this subset
is *pervasive*, unlike the sparse event-count regime):

| | value | reading |
|---|---|---|
| **content-only floor** (frequency affinity, cue-blind) | **0.398** | content genuinely UNDER-DETERMINES (≤0.75 → **GATE = BUILD**) |
| content floor by competitor count | 0.573 (2) → 0.420 (3–4) → 0.286 (5+) | **textbook cue-overload** (Van Dyke & McElree) |
| leak-free temporal-context (prior-recency) | 0.402 | ties content alone (+0.003 NOT_SEP) |
| context vs shuffled-context twin | +0.080 | recency carries **real** information (twin loses) |

**Two honest conclusions.** (1) The reframe is empirically confirmed: on the brain's real interference axis,
content fails (0.398 on 22k real queries) where the who-did-what event-count task had content near-perfect —
so **the +0.06 is an axis artifact, not a ceiling on the operation.** (2) But a *naive* recency signal alone
does not beat the content floor (+0.003 NOT_SEP), though it carries information (+0.080 over its twin) — so
the reframed rerun's value hinges on **cue COMBINATION** (content-addressable store + context reinstatement
together, per CMR), which is genuinely uncertain (the research's calibrated P=0.50). **This is a next
problem** (`resolve_retrieval_interference` reframed onto the similar-competitor axis; pre-registered
P1/P2/P3 in the research note), NOT built here — but the gate proves it is worth building, on the right axis,
which the original event-count rerun could never have shown.

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
  is already near-perfect. Deployed value of the SEPARATED store over flat on real text ≈ **+0.060 hit@1**
  @degraded cue / **+0.016** @full cue (real-frequency-weighted, CI-separated), vs the **+0.94** synthetic
  headline — concentrated in the ≥4-event minority. The register read-out (flat OR separated) DOES beat pure
  COUNTING by **+0.10..+0.16** on real text (a genuine capability, contra `flat_store`). Reclassify these organs
  from "validated separated-store win" to "**validated, but wire the separated machinery for high-fan entities
  only; its population lift over the already-strong flat register is ~+0.06, not the isolation figure.**"
- **`hdlab/dg_pattern_separation.py` at RETRIEVAL:** confirmed a **negative when the register ADDRESSES are
  distinct** (SEP_CA_DG < SEP_CA by −0.35 to −0.48 at the tail, holding for BOTH orthogonal and
  filler-correlated codes). DG's expand+sparsify only helps when the *addresses/keys* are confusable (the
  fan / key-overlap regime); it is NOT a fix for confusable fillers, and it HURTS a per-entity who-did-what
  register whose addresses are unique by event index. Do not wire DG-at-retrieval onto register codes with
  distinct addresses.
- **Generalization method:** the strongest free predictor (test items existed before the mechanism) confirmed
  again — the 10 false-positives all pre-existed their mechanisms; the collapse-prone organs were all
  validated at a synthetic operating point. `tools/generalization_audit.py` should print, next to each FRAGILE
  flag, the held-out n parsed from its SOLVED, so the false-positive rate is visible.

---

## ADJACENT COMPONENTS — brain-foundational status → next problems (owner-directed)

Evaluating what sits next to the store/retrieval cluster, for planning. Each: brain mechanism (PINNED vs
OUR-INVENTION), current status, and the next-problem seed.

| adjacent component | brain mechanism | fidelity | capability / limitation on real text | next-problem seed |
|---|---|---|---|---|
| **Extraction front-end** (event/argument/role reader that FEEDS the store) | language network LIFG/pMTG → thematic-role assignment | PINNED op, **our impl is the weak link** | incremental parser HOLDS (QA-SRL); but end-to-end event/role recall **~0.32**, composed reader BELOW floor on McGuffey. **This is the real bottleneck the whole retrieval cluster hides behind by holding inputs clean.** | **HIGHEST VALUE.** The store is fine; what feeds it is broken. Overlaps the ROLE-dimension wiring debt + McGuffey→modern migration (p1). A retrieval win is worthless until extraction recall rises. |
| **Counting / co-occurrence floor + meaning channel** | distributional statistical learning; anterior-temporal semantic hub (Phase-1 bottleneck) | PINNED | counting is a **strong** real floor (0.84 weighted; beat *addressed* storage in `flat_store`). Content-addressable retrieval adds **+0.156 EPISODIC specificity** over counting (recover THIS event, not the modal one) — but only for busy entities. `reader_meaning_channel` REFUTED (grounded hub ≤ MFS prior). | Characterize *where* the +0.156 episodic signal lives (which cases counting cannot get) — a candidate capability. Standing lesson: **any new organ must clear counting**, and most do not. |
| **Context / TCM store** (`resolve_retrieval_interference`, T1c) | temporal-context binding + reinstatement (Howard-Kahana TCM, Polyn-Norman CMR) | **PINNED**, impl synthetic-only | proven only on **engineered-separable** synthetic context; the solver's own open question — "is the substrate's REAL context separable?" — is untested. | **Rerun on real similar-competitor narrative** (LitBank/OntoNotes) — the deepest untested T1 claim; a research drill is scoping whether real similar competitors exist and how to operationalize "genuinely similar." |
| **Register write path** (`the_register_write_path`, T1d) | PFC working-memory recency gradient | PINNED-ish, synthetic-only | leaky/capacity win is synthetic; the load finding above applies — **the capacity wall it fixes rarely binds at real low load** (median 1 event/entity). | De-prioritize as a *population* lever; like the separated store it matters only for high-fan entities. |
| **DG pattern separation** (`hdlab/dg_pattern_separation.py`) | dentate-gyrus expansion+kWTA decorrelation | PINNED (Leutgeb 2007, McHugh 2007) | correctly scoped by this rerun: a fix for confusable **addresses** (fan / key-overlap), HURTS where addresses are already distinct. | Identify *where in real reading the situation-model addresses actually overlap* (busy scenes, multiple similar entities) — that is the only regime DG belongs on. |
| **Causal reasoning** (force-dynamic typers T2a/b vs the missing implicit-inference route) | force-dynamics = within-event force vectors (Wolff, behavioral-only, **no neural study — verified absence**); implicit event-event = causal-graph inference (left IFG/MTG + rostral mPFC, **PINNED** — Kuperberg 2011, Mason & Just 2004) | the typer is real but **word-grain**; the discourse-grain route is **missing entirely** | RERUN 2 + gate quantified it: typer fires 16%/≈noise; event-type covariation carries the signal (+0.056 over floor on the 84% no-fire subset). | **Gate-cleared next problem** `narrative_causal_graph_missing_implicit_inference_organ` — a glass-box event-type covariation / selectional-preference causal-graph scorer. |

**The through-line for planning:** the store/retrieval/binding cluster is *validated but low-yield at the
real operating point* — real narrative rarely stresses it (few events per entity, distinct addresses). The
value is upstream (extraction recall) and in the one untested lateral (context/TCM for similar competitors).
Wiring the separated machinery population-wide would import complexity for ~+0.06; wiring it *conditionally*
for high-fan entities, and investing in the front-end, is the brain-faithful priority order.

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
pulls ahead for the rare "busy" characters with many actions. A bonus surprise: a brain-inspired
"keep-memories-distinct" step that I expected to help actually hurt here, because the memories were already
distinct. **Then a literature check found the bigger point: we had been measuring the wrong kind of
difficulty.** Memory in reading gets hard not when one character does many things, but when *two similar
characters compete for the same cue* (like a pronoun that could mean either of two people). I re-measured on
that correct kind of difficulty — and it is *everywhere* in real books (22,000 cases), and there the simple
content method genuinely fails (right only 40% of the time). So the smart memory part does have real work to
do — just on a problem the first test couldn't see. That reframed test is the clear next thing to build, and
the ground for it is now laid.

## QUESTIONS

None — the triage is complete for all 33; the rerun is CI-separated with a floor, an info-free twin, and a
positive control; the deployed-value correction is quantified; and the axis-correction is both literature-backed
(PINNED) and empirically gated (content floor 0.398 on 22,123 real ambiguous queries → BUILD the reframed test).

## NEXT STEPS

- **NEW PROBLEM, gate-cleared and ready: reframe `resolve_retrieval_interference` onto the similar-competitor /
  partial-cue axis.** The gate proved content under-determines on a *large* real subset (floor 0.398, n=22,123),
  so the build is warranted — but naive recency alone ties content, so the test is **cue COMBINATION**
  (content-addressable store + temporal-context reinstatement, per CMR) with a **code-correlation-gated DG step**.
  Pre-registered P1/P2/P3 HARD-PASS/HARD-FAIL bands are in the research note; calibrated P(pass)=0.50. Corpora:
  reconstruct the competitor set on LitBank (gold chains discard competitors) or acquire GAP/ARRAU/ECB+
  (competitor-carrying, modern — also relieves the McGuffey age confound).
- **NEW PROBLEM #2, gate-cleared: `narrative_causal_graph_missing_implicit_inference_organ`.** The causation
  reframe's gate PASSED its pre-registered bar (event-type covariation +0.056 over majority, +0.094 over its
  twin, on the 84% subset the force-dynamic typer never touches). Build a glass-box event-type
  co-occurrence / selectional-preference causal-graph scorer (Chambers & Jurafsky narrative chains; Hu &
  Walker 2017's Trabasso-typology extractor), scoped to *implicit* event-event causation; keep the
  force-dynamic typer for explicit physical predication only. Adjacent brain system = the narrative
  causal-network / construction-integration comprehension network (left IFG/MTG + rostral mPFC; Kuperberg
  2011, Mason & Just 2004 — PINNED at the separability level).
- **Rerun the remaining Category-C organs** on the ledger's pre-existing corpora (the N400 segmenter on
  LitBank/GUM; ToM-microworld on LitBank-mined false-belief; the relcl parser on a reversible-rich corpus).
- **Strategy (Q111):** fold the AUDIT UPDATEs into `BRAIN_FOUNDATIONAL_AUDIT.md` (store/retrieval = "validated
  but low-yield at the real operating point; the value is on the similar-competitor axis, not event-count";
  DG = "gate on code correlation, off for distinct addresses"); annotate the store/retrieval organs
  "wire for high-fan entities only (~+0.06 population lift)"; add the held-out-n column to
  `tools/generalization_audit.py` so the false-positive rate is visible on every future scan.
- **No hdlab change is required by this problem** — it is a measurement/audit. The one code-relevant finding
  (do not wire DG-at-retrieval onto register codes with distinct addresses) is a "do-not," not a diff.
