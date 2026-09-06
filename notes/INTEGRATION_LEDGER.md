# INTEGRATION LEDGER — every recent solution's claimed gain, live-wiring status, and the up/downstream work still needed to REALIZE the full gain

**Why this exists (owner, 2026-09-05):** recent submissions carry sweeping up/ and down/stream improvements that are needed to realize their full gains. Those improvements used to live only as prose inside individual `SOLVED.md` files + scattered follow-on problems, so the *headline wire* got integrated but the *full-gain follow-through* slipped. This ledger is the single authoritative tracker: for **every** recent solution it records (a) the **END-SCORE / GAIN the solution CLAIMED** + the instrument it was measured on, (b) what is **wired LIVE** now, (c) which **board dim actually moved** (or none-yet), and (d) every **up/downstream improvement** still needed to hit the claimed number. It is simultaneously the **ordered work-list for the top-down integration pass**.

**Accountability model:** a solution's claimed number is a *target*. We only "realized" it when a **live board dimension** moves by that much (or a named instrument gap is closed). `full_gain_realized: YES/PARTIAL/NO` is the running scoreboard of that.

**Key recurring pattern:** "landed ≠ live." A component can be promoted to `hdlab/` and even default-ON, yet its claimed gain sits on *its own instrument* while the board doesn't probe it (instrument gap), or it's capped by an unbuilt upstream (coref/parser/meaning-hub), or a downstream consumer isn't updated to *receive* its new signal. Those are the rows that matter for the pass.

**Companion:** `notes/PROVISIONAL_WIRINGS.md` — everything wired in a TEMPORARY/non-final state (scoped workarounds, default-off holds, latent landings, provisional golds, lossy couplings) + what the pass resolves.

**Status vocabulary:** `LIVE` (wired + default-on, reaching a consumer) · `LATENT` (in hdlab, no live read()-time consumer) · `DEFAULT-OFF` (wired, flag off with a reason) · `NO-WIRE` (located negative — a valid pass, nothing to land) · `INSTRUMENT-GAP` (live but no board arm probes it).

> Build status: harvesting the recent SOLVED corpus via 4 read-only agents (2026-09-05). Chunk C (dimensions/state/events) landed first and is below; who-did-what/coref, knowledge/meaning, and perf chunks appending. The at-a-glance SUMMARY TABLE + the ordered TOP-DOWN WORK-LIST are built at the bottom once all chunks are in.

---

## 2026-09-06 (CONT-11) — REASONING-PHASE WIRES INTEGRATED (7 this session, newest-first)

The reasoning phase went live. Each below was reverified first-hand + landing-witnessed + board-self-test-checked, then committed (NOTHING pushed). **Dominant theme = INSTRUMENT-GAP (live ≠ scored): the board still scores 19c LitBank, so most of these modern-gold wins are board-INVISIBLE — the `board_*_dimension()` arms + the modern-comprehension-board (p1) close it.**

- **precision_weight_the_head_driven_readers `110280d52`** — the reasoning phase's RELIABILITY SUBSTRATE. Claimed: patient selective@50 0.8789→0.9745 (+0.0956 CI-sep), QA-SRL 0.2982→0.3414, obl 0.7581→0.8919, random-conf twins flat (UD-EWT/QA-SRL, MODERN). Landed: `hdlab/parse_confidence.py` (frozen glass-box calibrator, raw AUC 0.615→calibrated 0.858, reuses graded_competition) + `EventRecord.patient_conf/patient_defer` behind `precision_weight_roles` **DEFAULT-OFF** (measured reason: no consumer defers yet + ~2 parses/read → landed-but-latent; flip-on = a reasoning consumer defers + board read-cost check). realized_on_board: **NONE** (INSTRUMENT-GAP + DEFAULT-OFF). full_gain: PARTIAL.
- **bridging_inference `4ce5075b1`** — the MEANING CHANNEL'S FIRST LIVE read()-time CONSUMER (it was entirely LATENT). Claimed: referential-part WordNet meronymy 0.4720 / ConceptNet PartOf 0.6087 (curated mfnd 0.6541) / instrument 0.4522, CI-scale over no-inference (0.20) + salience floors, shuffled-meaning twin collapses. Landed: `hdlab/bridging_inference.py` DEFAULT-ON/lazy as `sm.bridge`/`sm.infer_bridges`, reusing the ATL PPMI+SVD hub + meaning_foundation; all 8 dims byte-identical off-vs-on. realized_on_board: **NONE** (INSTRUMENT-GAP — no meaning/bridging board dim). full_gain: PARTIAL. followon: `board_bridging_dimension()` arm; PPR-FUSE/entropy-gate estimator.
- **theory_of_mind `4ce5075b1`** — the reasoning phase's first MENTALIZING system. Claimed: BigToM belief-pred CHAIN 0.849, FALSE-belief +0.871 over a 0% floor, twins lose, oracle 1.000 (BigToM, MODERN). Landed: `hdlab/theory_of_mind.py` (believes×wants→action off the BELIEVED state + inverse) DEFAULT-ON/lazy as `sm.predict_action`/`will_act_on`/`attribute_belief`, reusing belief_timeline + goal_register; byte-identical off-vs-on. realized_on_board: **NONE** (INSTRUMENT-GAP). full_gain: PARTIAL. followon: `board_tom_action_dimension()` arm; goal→fact desired-VALUE binding via the meaning channel (the action ceiling).
- **byhead agent cue (grounded_meaning_role_cue) `4ce5075b1`** — Claimed: non-canonical agent clean-slice 0.2556→0.6889 (+0.433 CI-sep), full 0.5224→0.6866, canonical no-regress, twin loses (QA-SRL, MODERN). Landed: `graded_role_assigner.agent_supports` byhead cue (gated participle+by-PP, weight 10 outvotable) + `situation_reader.cm_agent_byhead` DEFAULT-ON; grounded selfit cue = LOCATED NEGATIVE (not landed); byte-faithful, agent-only additive-safe. realized_on_board: **NONE** (INSTRUMENT-GAP — the board's only agent gold is 19c LitBank syntactic subjects, ~no by-agent Qs; board −0.0016 = gate false-fires on archaic 'by oneself'). full_gain: PARTIAL. followon: a MODERN by-agent board arm.
- **coref pick (strengthen_the_cue_based_pronoun_coref) `14f7f5e83`** — a LIVE BOARD-MOVER. Claimed: live pooled he/she coref_acc 0.4693→0.6019 (+0.1327 CI-sep); named no-regress 0.4883→0.6165; who-has-what 0.4035→0.4735 (+0.070). Landed: `EventCentralityReader.graded_pick=True` → PINNED graded ACT-R retrieval (recency load-bearing), event-centrality forced off; retires the anti-brain-foundational rolemass pick; coref-independent dims byte-identical 12/12. realized_on_board: **YES — the ONE board-mover this batch** (coref dim RISES on its live pooled instrument; who-has-what +0.070). full_gain: YES (register-general recency mechanism; a modern pronoun corpus is the proper home). 19c-measured but a fidelity correction justified independently.
- **space where_is (…lazy_locative_pp_bridging) `1d48cffd8`** — Claimed: MODERN where_is 0.319→0.468 (+0.149); LIVE read() 0.277→0.447 (+0.170); floor + shuffled-ground twin CI-sep. Landed: named-ground binding (Talmy Figure/Ground + VerbNet Goal gate + graded ConceptNet AtLocation) DEFAULT-ON in `_space_reader` prior_ext; additive (who-did-what byte-identical). realized_on_board: **NONE** (INSTRUMENT-GAP — board `location` dim is coarse/at-ceiling 1.0, doesn't score exact-node where_is). full_gain: PARTIAL. followon: a MODERN where_is board arm; Ground-aware goal-PP attachment.
- **parser distributed-selpref (distributed_…_parser) `b07572d2c`** — EXCELLENT located negative. Claimed: REFUTED (object-class selpref for UAS, brain-corroborated); the reframe = precision-weight a good-enough parse (Friston), selective who-did-what 0.871 vs 0.780 demonstrated. Landed: **NO-WIRE** (located negative); the reframe became the precision_weight follow-on (integrated above). realized_on_board: — (nothing to realize; the value is the reframe + substrate). full_gain: N/A (correct located negative).

**BATCH SCOREBOARD: 1 board-mover realized (coref); 5 live-but-INSTRUMENT-GAP (ToM / bridging / byhead / space + precision_weight-also-latent); 1 located-negative-no-wire (parser). The dominant unfinished work = MODERN-gold board arms (p1 + the per-arm follow-ons) to score the 5 board-invisible wins — the recurring "live ≠ scored".**

---

## Already integrated this session (strategy, mid-flight)

### a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround
- one_line: Mental-causation bridge — an event-TYPE representation + a folk-psych bridging selector that crosses the mental-causation wall force dynamics can't represent; the brief's literal route (retire scoping) is a located negative (kept scoping).
- claimed_gain: constructed non-adjacent mixed bridges UNIFIED 1.000 vs force-only 0.500 (+0.500 CI[+0.250,+0.750]); real LitBank coverage 16/16 event-typed (mental 11/16) vs force 3/16; faithful selector +0.875 CI-sep over recency-only.
- instrument: exp_causal_unified_bridge_event_type_v1 (constructed dissociation, n=16) + RC.GOLD real edges; NOT the live board (causal QA gold is connective-only + circular for plausibility).
- verdict: EXCELLENT PARTIAL — located negative on the literal route (full pass) + constructive mental-causation cross.
- landed_live: LIVE default-ON pure-add. hdlab/event_type.py (event-TYPE organ) + `_read_causation` PASS-2 mental-bridge behind `causal_mental_bridge` (connective links first → goal-graph superset).
- realized_on_board: NONE YET (INSTRUMENT-GAP) — mental links are non-connective; the causal board dim (connective-only gold) is byte-identical off-vs-on. +214 mental_bridge links added to the situation model for downstream consumers.
- upstream_needed: contextual WSD via GroundedSemanticGraph (type_ok 0.688→0.750, chain 0.875→0.938) — LATENT organ exists; coref-experiencer (preserved only 0.500 on real prose) — the reader's live coref is the lever.
- downstream_needed: 3 consumers to UPDATE to receive the event-type signal — causation_typing → mental typing (3/16→16/16); affect_register → OCC-appraisal inferred-emotion channel; goal-graph → motivational spine (+47 enablement edges, already additive).
- adjacent_or_optim: mine a real-corpus non-adjacent MENTAL-bridge gold (the missing scored instrument — no live mental-causal metric exists).
- followon_filed: recorded here (this ledger) rather than scattered problem files.
- full_gain_realized: PARTIAL — mechanism + event-type organ live; field accuracy + the 3 downstream signal-updates + a scored mental-causal instrument are the pass work.

### add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost
- one_line: A byte-identical fast scoring path for the arc labeler's 36-label per-arc perceptron (~54% of a long-doc read) + the graded Competition-Model readout the same refactor materializes for free.
- claimed_gain: labeler scoring 8.7–9.8x (~4.2s/read), whole-read ~54% cut on 3 full docs; byte-identical (0/22,921 held-out arcs); graded readout entropy→error AUC 0.930 (twin 0.481).
- instrument: labeler-in-read timing (3 full docs) + byte-identity witness (22,921 held-out arcs, 2 populations); NOT a board dim (byte-identical → no score change).
- verdict: EXCELLENT — byte-identical speedup + a brain-faithful graded readout (positive; the parser exploration D-O = located negatives/research).
- landed_live: LIVE default-ON. `_FastLabelPlan` + `_ensure_fast` in `hdlab/arc_labeler.py`; `label()` routes through it; `_predict_label`/`_score` kept as reference. Opt-in byte-safe `label_graded` publisher (default-off). Witnesses: solver 5/5 + hdlab-landing 4/4.
- realized_on_board: NONE (byte-identical — pure speedup, the single biggest read-cost). The graded readout is default-off (no consumer wired).
- upstream_needed: the PARSER is the dominant leak (obl:agent LAS 0.0588; −21% heads even w/ gold tags) — the parser tier.
- downstream_needed: the entity_states/copular binder + who-did-what readout should consume the graded label posterior + entropy (not hard 1-best) — belongs with `consume_the_graded_pos_posterior` (row 7).
- adjacent_or_optim: per-arc INDEPENDENCE (no joint one-role-per-clause decode) = the deeper fidelity gap (Q113). Parser exploration (D-O) → the rubric.
- followon_filed: recorded here (below) — whiten-the-meaning-channel + self-sup+grounded parser.
- full_gain_realized: YES for the speed (fully live, byte-identical). The graded-readout ACCURACY payoff needs a consumer (row 7 step); the parser fidelity is the parser tier.

**Two tracked follow-ons from this submission (owner may dispatch as solver problems; kept here per "track it all in one place"):**
1. **whiten the meaning-channel embedding** (MEANING TIER / step 4) — root cause of the grounding negatives = near-collinear meaning vectors (cosine 0.92); whiten (subtract global mean + project out top-D PCs) lifts the LIVE WSD channel a_s +0.0176–0.058 (n=2676) AND flips the parser-grounding control +0.020. UNVERIFIED — needs the shuffled-diagnosticity twin + significance + vs-curated-baseline before landing. A concrete near-term testable win; fold into the meaning-stage build.
2. **self-supervised + grounded front-end parser** (PARSER TIER north-star) — the DMV+universal-prior+EM + online never-frozen predictive-coding learner induce real structure with no gold trees (0.38–0.45), grounded meaning deciding ROLE on non-canonical clauses; the gap to supervised 0.84 is grounded-experience SCALE + the missing answer key, not the mechanism. Recorded in `PARSER_JOINT_INTEGRATION_RUBRIC.md` as the true-ideal direction; a multi-week program (owner decision to dispatch).

---

## ✅ TOP-DOWN PASS EXECUTED (2026-09-05) — all 6 owner-DONE integrated; gate EMPTY

Baseline agg **0.6592** → tiers landed in order, each measured + committed:
- **Step 0 (ruler):** 3 arms folded into the board (`patient`/`goal_hierarchy`/`wic`) — realized the previously-INVISIBLE gains: **patient 0.8311 (+0.086 CI-sep)**, **goal_hierarchy 1.000 (+0.318)**, and put the **meaning channel on the board** (`wic` 0.6006→0.6639 = +0.0633). `9da95a0ea`.
- **Parser tier:** double-parse CONSOLIDATION (single arc-eager parse) — board **0.6592 zero-regression**, ~5% faster. `612b0b579`.
- **Goal tier:** advcl PURPOSE FILTER (goal-why lever) + CONTEXTUAL `_link_open_stack` edge (situation-relatedness). `5462341ec`.
- **Coref tier (entity-KB):** landed default-OFF `6b57a04e9`; then **REALIZED via a NEW common-noun coref board arm** (`exp_board_common_noun_coref_v1`, `9b97be24c`): model 0.6889 vs surface-head 0.5965 = **+0.0924 CI-sep**, shuffled-KB twin loses — the +0.0882 was never a located negative, it needed its own arm (the board coref dim scores PRONOUN; this scores COMMON-NOUN; separate brain systems, separate arms). The LIVE reader flag stays default-off pending the two-pass wired into read() (the arm uses the cached two-pass).
- **Meaning tier:** board-visible via the wic arm; the reader-side `select_sense` channel is §2-deferred (islanded). `4cf4ac041`.
- Earlier this session: causal mental-bridge `8cbb1b0ed`, arc-labeler fast path `dad8b7b11`.

**REALIZED board wins:** patient +0.086, goal-hierarchy +0.318, **common-noun coref +0.0924** (new arm), goal-why (purpose-filter), a faster board-neutral parser, and the meaning channel now SCORED (wic +0.0633). **Board-neutral/additive (honestly):** parser (neutral), causal mental-bridge + goal contextual edge (additive, not yet board-scored — need a mental-causal / marker-less gold), meaning-wire reader-side (islanded select_sense, §2-deferred). The pass added FOUR board arms (patient/goal-hierarchy/wic/common-noun) that made previously-invisible proven wins visible.

## PASS FOLLOW-ONS (the deeper realization work surfaced by the pass — owner may dispatch)
1. **The entity-KB TWO-PASS reader_coref + a COMMON-NOUN coref board arm** — the board `coref` dim scores only PRONOUN coref; add a common-noun-clustering arm (like the patient/wic arms) so the entity-KB's +0.0882 becomes visible, and supply the Step-3 reader-coref lever via a two-pass. Then flip `entity_kb_resolver` on if net-positive.
2. **The read()-time MEANING STAGE (§2-gated)** — the reader has no read()-time meaning consumer; `grounded_semantic_graph.select_sense` is islanded. Build the stage that consumes the curated foundation (the wic arm proves the value). Gated by the §2 no-transformer owner decision for the fine half.
3. **The event-TYPE downstream signals** — feed `hdlab/event_type` to the 3 named consumers: causation_typing (mental typing 3/16→16/16), affect_register (OCC inferred-emotion), goal-graph (motivational spine); + a mined MENTAL-causal gold + a marker-less goal gold (the mechanisms landed this session are additive, awaiting these instruments).

## STAGED QUEUE — (all integrated 2026-09-05; retained for the record)

Per the batch discipline: reverify + grade promptly (done), wire in the pass so board-movers are measured in the integrated reader + in tier order. None wired live yet (no `INTEGRATED_BY_STRATEGY`).

| Submission | Reverify (first-hand) | Tier / pass step | Claimed gain (instrument) | Disposition |
|---|---|---|---|---|
| `seed_the_entity_world_model_resolver...` | `test_entitykb_resolver_v2.py` **6/6** | COREF (step 2) | common-noun coref +0.0809 / relational +0.1440 CI-sep (held-out LitBank) | Land the full-chain resolver + KB asset + live `sm.entities` coref coupling into `commonnoun_binder`; NOT the agent head-match. Board-mover (coref dim). |
| `wire_the_curated_meaning_foundation...` | `test_curated_foundation_wic.py` **6/6** | MEANING (step 4) | curated+coarsening beats the LIVE PPR `select_sense` reader **+0.0633 CI-sep** on WiC (n=2038); twins lose | **REROUTED win** — the brief's who-did-what/hub + meaning-readout proposals are located negatives (parse-bound; no live meaning stage). Wire the curated taxonomic signatures + shared-core COARSENING into the live `grounded_semantic_graph.select_sense` (the board's one live meaning metric). Coarsening SCOPED to the same/diff-sense judgment (NOT fine-sense a_s). Residual to human 0.80 = deep contextualization = §2 owner decision. |
| `validate_the_ppmi_svd_means_end_bridge...` | `test_contextual_goal_attachment_modern.py` **4/4** (+5/5,+9/9) | GOAL (post-meaning) | contextual situation-relatedness beats the info-free twin **K1 0.700 vs 0.483 CI-sep** (n=797 modern gold; 19c 0.634 vs 0.537) | **REROUTED** — the brief's context-free ATOMIC bridge is REFUTED (sits in the twin band); the brain's CONTEXTUAL inverse planning (situation→goal relatedness in the live associative store) wins. **NO PARSER WORK** (parser reused unchanged — the parser-touch flag was a false positive). Wire a reliability-gated contextual edge in `build_goal_graph`; uses the meaning store (compose after the meaning tier). |

**Parser-tier note:** so far NO submission carries a parser REPLACEMENT to wire. The arc-labeler's parser sections (D-O) were DIAGNOSIS/exploration (recorded in the rubric, filed as follow-ons); the means-end did NO parser work. If a genuine parser replacement is coming, it is in a not-yet-done submission.

---

## Chunk C — dimensions / state / events (harvested 2026-09-05)

### the_situation_model_has_no_affect_emotion_dimension
- one_line: A glass-box per-character AFFECT/EMOTION register (valence primary + category) bound to the coref-resolved experiencer via a psych-verb linking frame.
- claimed_gain: "how does X feel" category (n=673) 0.788 vs floor 0.312 vs twin 0.394 (CI-sep); valence-sign (n=743) 0.838 vs floor 0.490; multi-character 391 right vs 37 reverse (10.6x).
- instrument: exp_affect_register_qa_v1 on 100 LitBank docs — this arm IS the board `affect` dim.
- verdict: EXCELLENT — positive win (+ sanctioned located negative for inferred/unstated emotion).
- landed_live: LIVE default-ON. hdlab/affect_register.py + psych_verb_frames.py + affect_lexicon.py + assets; `track_affect` default-TRUE; `_read_affect` sets sm.affect_register + feels/valence_of/feels_about.
- realized_on_board: YES — `affect` dim live ~0.79 (category) / ~0.84 (valence) on its own population. BUT capped: coref is 87% of the end-to-end affect loss (83.5% of experiencers are common-noun entities the reader never tracks); extraction+binding near-ceiling (F1 0.945) given gold coref.
- upstream_needed: COMMON-NOUN coref (the dominant loss, +0.43 F1 headroom) — NOT built (6 prototypes each ≤+0.02; needs a faithful coref organ). Filed pri-2.
- downstream_needed: none (additive; other dims byte-identical).
- adjacent_or_optim: OCC-appraisal channel for inferred affect (gated on the meaning channel); goal×affect composition (frustration/satisfaction); arousal dynamics (stored, unused); revisit context_grounded_valence.py to adopt the psych-verb frame.
- followon_filed: form_a_discourse_referent_for_every_entity... (pri 2).
- full_gain_realized: PARTIAL — live + scoring; ceiling capped by the unbuilt common-noun coref organ.

### the_situation_model_has_no_goal_intention_dimension
- one_line: A glass-box per-agent GOAL/INTENTION register (5th Zwaan dim) — desire/intend/try + purpose constructions, coref-bound, status + reinstatement.
- claimed_gain: WANT-explicit (n=234) 0.6068 vs floor 0.137 & twin 0.0171 (CI-sep); goal-why (n=1372) 0.9796 vs physical-cause 0.0408; status 1.000 vs 0.333; reinstatement 1.000 vs recency 0.000.
- instrument: exp_goal_register_qa_v1 on 100 LitBank docs + authored status/reinstatement gold; registered as the board `goal` dim.
- verdict: EXCELLENT (full-chain upgrade) — positive win + sanctioned located negative (bare-purpose parse-gated; Tier-2 abductive).
- landed_live: LIVE default-ON. hdlab/goal_register.py + `track_goals` default-TRUE + `_read_goals`. ALSO landed upstream general primitive hdlab/verb_subcat_frames.py + asset + passive-agent guard.
- realized_on_board: YES — `goal` dim live & CI-sep (WANT-explicit 0.58 over floor 0.28, twin 0.0; WHY 0.97 vs 0.03). Moved from non-existent to scoring.
- upstream_needed: register-native dependency parse for bare-purpose attachment (parse-gated 0.33 vs oracle) — NOT built (parser_arceager wall).
- downstream_needed: none (additive; witnessed 6/6).
- adjacent_or_optim: goal HIERARCHY graph (built, next row); meaning channel for Tier-2 abductive goals (unifies w/ belief inverse-planning); thwart-by-outcome status; goal×belief composition.
- followon_filed: build_the_goal_subgoal_hierarchy_graph...; register-native parser (parser_arceager).
- full_gain_realized: PARTIAL — explicit slice fully live & CI-sep; bare-purpose tail parse-gated; Tier-2 needs the meaning channel (both the sanctioned located negative).

### build_the_goal_subgoal_hierarchy_graph_for_plot_structure_comprehension
- one_line: A goal→subgoal HIERARCHY GRAPH composing the flat goal register + causal network (motivation edges, connectivity salience, open-superordinate reinstatement) for multi-hop plot-structure questions.
- claimed_gain: authored plot battery: goal-why chain (n=88) 1.000 vs flat 0.6818 (+0.3182); superordinate reinstatement (n=15) 1.000 vs recency 0.0667 (+0.9333); connectivity salience 1.000 vs 0.000; distance-invariant K=0..5; means-end bridge PoC 0.9375 on covered verbs.
- instrument: exp_goal_hierarchy_qa_v1 — 30-item AUTHORED plot battery + real-narrative incidence on 25 docs; NOT the live board.
- verdict: EXCELLENT — positive win (located negative cracked via means-end bridge PoC).
- landed_live: LIVE default-ON. hdlab/goal_hierarchy_graph.py verbatim; `_read_goals` sets sm.goal_graph + 4 callables (pure ADD).
- realized_on_board: **NONE YET — INSTRUMENT-GAP.** Only 6/149 (4%) of live board goal-why questions are multi-hop, and the board gold IS the immediate purpose → the board never probes the graph; 169/169 board answers byte-identical. The 0.68→1.00 gains are on the authored battery only. Needs a `goal_hierarchy` board arm (NOT added).
- upstream_needed: register-native dependency parse (past the 0.33 bare-purpose wall) — not built; edge COVERAGE (more edge types) is the real-narrative lever.
- downstream_needed: **a `goal_hierarchy` board arm must be ADDED** for the benefit to be visible (NOT added at integration).
- adjacent_or_optim: PPMI+SVD means-end bridge real-narrative validation (n=16 PoC, filed); inverse-planning organ (shared w/ belief); faithful two-hop enablement; corpus-validated salience arm; goal×belief composition.
- followon_filed: the means-end bridge validation + the inverse-planning organ.
- full_gain_realized: **NO** — mechanism live but LATENT-for-scoring (no board arm probes it); means-end crack is an n=16 authored PoC.

### register_robust_event_detection_turn_on_and_expand_lifts_every_who_did_what_arm
- one_line: Turn ON scoped register-robust predicate recovery + a sort-aware copula readout so who-did-what reaches the copular-state silo.
- claimed_gain: AGENT arm 0.7099→0.8044 (+0.0945 CI[+0.0829,+0.1049]) on 40 held-out; board 0.7251→0.7918 (+0.0667); copula holder 0.09→0.63, property 0.00→0.275; caught+fixed a hidden causal regression (−0.0594) via scoping.
- instrument: who-did-what agent/patient arms on 16 board docs + 40 disjoint held-out — IS the live board `events` who-did-what population.
- verdict: EXCELLENT — positive win on both arms (+ a located negative: density-robust structural causal fix fails → meaning hub).
- landed_live: LIVE. `predicate_recall` default-ON + `_read_causation` SCOPED over base events (causal byte-identical); copula silo-unification via entity_states + copula-aware readout.
- realized_on_board: **YES** — `events` who-did-what board dim moved: agent 0.7251→0.7918 (+0.0667 CI-sep); copula patient/be 0.00→0.259 on the board slice. Coref/temporal/causal byte-identical.
- upstream_needed: joint graded/calibrated-posterior joint-decoded POS+parse (open-class 19c 0.56→~1.0, copula holder 0.63→0.77, attachment 0.83→0.955) — NOT built (filed).
- downstream_needed: `_read_causation` over base events (coupled) — DONE at landing.
- adjacent_or_optim: force-dynamic causal scorer (= the causal problem I just integrated); unified sort-typed eventuality inventory (merge events+states) — filed; per-consumer FP-threshold dial.
- followon_filed: the force-dynamic meaning-hub causal scorer (now integrated); joint-decoder + unified-inventory.
- full_gain_realized: PARTIAL — copula-readout + scoped predicate_recall live on the board events dim; deeper residual (open-class 19c, copula holder attachment, force-dynamic causal) gated on the joint decoder + meaning hub.

### register_robust_event_detection_the_reader_drops_events_when_the_tagger_misses_the_verb
- one_line: A learned noisy-channel predicate detector (logistic over register-invariant cues, static asset, no LLM) recovering tagger-dropped verbs, modern→19c zero-label transfer.
- claimed_gain: recovery @ FP≤0.5: MODERN (n=89) 0.8989 (+0.3329 vs twin); 19c-TRANSFER (n=144, 0 labels) 0.5625 (+0.5386); QA-SRL 0.803; crosses the parent's 0.16 modern wall; CRF axis-1: 19c 0.582→0.806.
- instrument: recovery-of-dropped-verbs on UD-EWT / LitBank / QA-SRL vs a random-verbhood twin — NOT an end-to-end board delta (explicit).
- verdict: EXCELLENT — positive on the recovery instrument, but a LATENT-for-board landing (turn-on measured flat at this problem).
- landed_live: LANDED. hdlab/predicate_detector.py + asset. Was DEFAULT-OFF at this problem; a LATER sibling (turn_on_and_expand) flipped `predicate_recall` DEFAULT-ON (scoped) → default-on NOW.
- realized_on_board: at this problem NONE (turn-on flat 0.2519→0.2530, not CI-sep — the who-did-what eval supplies the clean main-verb slice, hiding recovery). Later realized via the sibling copula routing + scoping.
- upstream_needed: none upstream of the detector.
- downstream_needed: a free-text event-recall consumer that measures dropped-event recovery — none exists live.
- adjacent_or_optim: the CRF calibrated-posterior tagger (+0.224 on 19c — NOT landed inline, needs crfsuite runtime / shared-component swap); joint-decoded POS+parse; glass-box morphological analyzer; meaning hub for the ~33% semantic ceiling.
- followon_filed: upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior.
- full_gain_realized: PARTIAL — detector live/default-on, but no live board instrument measures its recovery gain (clean who-did-what slice hides it); CRF upgrade (+0.224 19c) un-landed.

### wire_the_copular_state_qa_consumer_and_turn_on_bind_entity_states
- one_line: Wire a live STATE-QA consumer ("what/who is X" → entity-state store) + turn ON bind_entity_states + the label-robust robust_cop upstream detection fix.
- claimed_gain: qa_state 0.7116 (378 predicational) vs floor 0.5714 (+0.1402 CI[+0.087,+0.196]) twin losing; base OFF 0/378; ladder →robust_cop 0.8333 →arc-eager 0.8651; qa_aggregate 0.315→0.404.
- instrument: exp_situation_model_state_qa_v1 on UD-EWT copular GOLD (predicational, non-circular) — NOT the 19c board (would be circular; 19c coverage-only 527/530).
- verdict: EXCELLENT — positive win; registered as the board `state` dim.
- landed_live: LIVE default-ON. `bind_entity_states` default-ON; robust_cop → hdlab/copular_binding.py unioned into `_read_entity_states`; state-QA consumer = board `state` arm.
- realized_on_board: `state` dim now live (was off). ~0.71 (→0.826 w/ robust_cop) but on UD-EWT (modern), NOT the 19c board (coverage-only 527/530). qa_aggregate 0.315→0.404; 4 other LitBank dims byte-identical.
- upstream_needed: copular DETECTION recall (residual is upstream: read-back|binding 0.996, routing 1.000); robust_cop (built+live) closes most; arc-eager +0.032 but 19c-NEGATIVE (needs per-register routing).
- downstream_needed: cross-sentence canonical-entity binding — key state_register on the coref entity not the surface token — NOT built (0.43 of predications become answerable once bound).
- adjacent_or_optim: cross-sentence canonical-entity binding (biggest lever, filed); identity→coref-merge for equatives (~16%, filed); a ~200-clause hand-annotated 19c copular gold; arc-eager per-region routing (modern-only).
- followon_filed: cross-sentence canonical-entity binding; identity→coref-merge.
- full_gain_realized: PARTIAL — consumer + turn-on + robust_cop fully live; headline number modern-only (no 19c board floor), arc-eager un-landed (19c-neg), cross-sentence binding unbuilt.

### consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection
- one_line: Tests consuming the graded CRF POS posterior for name/common-noun detection — a multi-level LOCATED NEGATIVE — but a structure-first PATIENT reader was found + landed instead.
- claimed_gain: located negative (referent_per_np soft-recovery +0.0000 to who-did-what; graded animacy validity 0.511 but +0.0000 on who-did-what); SEPARATE WIN structure-first patient +0.088 on clean UD-EWT (0.673→0.760), zero params, no-regress.
- instrument: who-did-what through the live reader on 25 docs + animacy gold + CLEAN UD-EWT structural gold; the LitBank role-balanced/object gold flagged INVALID.
- verdict: EXCELLENT — rigorous located negative (no wire for the posterior) + a landed structure-first win.
- landed_live: (1) graded posterior → NO-WIRE (located negative). (2) structure-first patient LANDED default-ON: structural_patient_pick, `structural_patient` default-ON, AGENT untouched (0/2850 board agent answers changed).
- realized_on_board: structure-first patient +0.088 on CLEAN UD gold, but LitBank board OBJECT gold reads −0.006 (confounded ruler — mislabels obliques as objects; INVALID). So ~flat/slightly-neg on the current board instrument; real gain shows on clean UD only. Posterior contribution: NONE (located negative).
- upstream_needed: parser verb→argument attachment (perfect-parse ceiling 0.912; residual +0.15) — NOT built.
- downstream_needed: none regressing.
- adjacent_or_optim: name→animate animacy_lexicon fidelity fix (byte-safe, role-metric-neutral — land as correctness); **re-base ALL who-did-what eval on clean UD-EWT structural gold** (not the confounded role-balanced gold); the posterior's real axis is VERB→predicate_detector (already landed).
- followon_filed: improve_the_parser_verb_argument_attachment_for_who_did_what (pri 3).
- full_gain_realized: PARTIAL — posterior brief = full-pass located negative (no wire); structure-first patient live +0.088 on clean instrument but board-masked by a confounded ruler; +0.15 to ceiling needs the parser.

---

## Chunk A — knowledge / meaning chain (harvested 2026-09-05)

> **⚑ THE DOMINANT FINDING of this chunk: the entire meaning/knowledge channel is LATENT.** The reader has NO read()-time meaning consumer (no `reader_meaning_channel` stage). So FOUR proven gains all wait on ONE missing wire: curated foundation +0.0755, rare-sense Bayesian readout +0.065, precision-weighting +0.023, clean-foundation lift +0.067 — every one is latent on read(). Building the single meaning stage cashes in the whole cluster. This is the highest-leverage row in the ledger.

### seed_the_entity_world_model_resolver_with_a_world_knowledge_role_kinship_prior_phase1
- one_line: A role/kinship/scenario KB seed for the entity-world-model resolver — the win came from the whole upstream chain (situation-model instance binding + pronoun-into-entity + consuming the reader's REAL per-text coref), not the KB.
- claimed_gain: aggregate common-noun coref (char-cluster CoNLL) +0.0809 CI[+0.0696,+0.0909]; hard-link +0.1793 (0.2537→0.4342, 63% of the gap to 0.540 gold ceiling); downstream relational reference +0.1440 (0.3570→0.5010); named no-regress −0.0034. KB seed alone = located negative (~2%).
- instrument: 100 held-out LitBank docs, deployment self-built records, via exp_entitykb_resolver_v2 (test 6/6). NOT the live board.
- verdict: EXCELLENT — positive win (chain) wrapping a located negative (KB seed). Owner DONE.
- landed_live: NO hdlab wire yet. Proposed: hdlab/entity_world_model_resolver.py (full-chain resolve()), ship curated KB → data/frontend_assets/role_kinship_scenario_kb.json, wire reader sm.entities head-coref into commonnoun_binder.py. NONE on disk. **STAGED by strategy this session (reverified 6/6); HELD for the top-down pass (board-mover, measure in the integrated reader).**
- realized_on_board: NONE YET (own held-out LitBank/CoNLL instrument; not wired to the live coref board dim).
- upstream_needed: a better substrate pronoun/coref resolver (reader's coref only 0.58-accurate, caps hard-link 0.434 vs 0.540) — bidirectional next lever, not built.
- downstream_needed: wire reader sm.entities head-coref into the resolver/commonnoun_binder; DO NOT wire the reader AGENT head-match (regresses named −0.0064). Default-ON justified.
- adjacent_or_optim: push residual rank_miss/abstain (smaller scoring refinement).
- followon_filed: none (this IS the Phase-1 follow-on of form_a_discourse_referent_for_every_entity...).
- full_gain_realized: NO — owner-DONE, no wire on disk yet; +0.0809 coref gain not on the live board until landed.

### build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift
- one_line: Built + froze the clean curated meaning foundation (117,614 WordNet synset sense-signatures, 44MB float16) as a static offline asset + a reading-grown associative store (C1b, 80k) + grow/prune/consult machinery.
- claimed_gain: C1 rare-sense WSD a_s 0.2512→0.3267 (+0.0755 CI-sep); C1b SimLex 0.166→0.264 (+0.098)/WordSim 0.604; composed_hub_predictor AvgSim→MaxSim which-argument +0.065 CI-sep.
- instrument: C1 via LIVE hdlab.diagnostic_context_wsd on doc-disjoint SemCor subordinate (n=2675); C1b on SimLex/WordSim; usage tweak on QA-SRL ambiguous (n=1318). NOT the live board.
- verdict: EXCELLENT — positive win (the +0.067 reproduces + ships frozen). Owner DONE.
- landed_live: hdlab/meaning_foundation.py LANDED (loader) but **LATENT — no live read()-time consumer**. Frozen assets on disk (gitignored). Usage tweak DEFERRED.
- realized_on_board: NONE YET (meaning instrument only; C1's one consumer diagnostic_context_wsd is not called live).
- upstream_needed: meaning-KB resolution residual — additive prior-override closes HALF glass-box (0.33→0.60); 0.60→1.0 needs a contextual reader = §2 owner decision (rec HOLD).
- downstream_needed: **(1) a read()-time WSD stage consuming C1 (`reader_meaning_channel` — does not exist); (2) ship C1b as the reader's default distributional store (15k→80k) replacing hub_ppmi_svd_200d; (3) rebuild composed_hub_predictor on 80k C1b + adopt MaxSim, measure on live who-did-what (the readiest gain, unmeasured combined).**
- adjacent_or_optim: per-consumer prune projections; materials-science coverage gap; step-2 online targeted-acquisition learner (6,753 collapsed sense-pairs).
- followon_filed: step-2 learner = grow_broad_coverage... (slug below); pri-4 wire_the_curated_meaning_foundation_into_a_live_consumer_and_adopt_the_maxsim_usage.
- full_gain_realized: NO — loader latent; +0.0755/+0.098/+0.065 all latent until the reader gains a meaning stage / the store is swapped / the hub is rebuilt-and-wired.

### grow_broad_coverage_correctly_resolved_rare_sense_experience_the_meaning_channel_learner_on
- one_line: Rebuilt the rare-sense meaning channel as the hippocampal-EPISODIC regime; the landable win is a Bayesian log-prior + precision-weighted READOUT, the online coverage-growth half is a located negative.
- claimed_gain: readout rare-sense a_s 0.316→0.387 (+0.065–0.072 CI-sep); coarse 0.49→0.57; frozen-weight generalizes 6/6; all-pop 0.456→0.629. Located negative: online growth deployed +0.011 (CI-sep only at frac 0.40–0.55); coverage 0.14→0.47.
- instrument: subject-weighted a_s on doc-disjoint SemCor subordinate (n=2676) via hdlab/diagnostic_context_wsd (test 26/26). NOT the live board.
- verdict: STRONG — located negative (full pass) containing a real landable readout positive. PARTIAL; owner DONE.
- landed_live: sense_prior/prior_weight Bayesian readout landed into hdlab/diagnostic_context_wsd, DEFAULT byte-identical, **KEPT default-off (only consumer consolidation_gate is off)**. Episodic/coverage store NOT landed (§2-gated).
- realized_on_board: NONE YET (readout live but default-off; no live board dim consumes it).
- upstream_needed: a richer per-occurrence contextual encoder = §2 invariant boundary (rec HOLD). If relaxed, the shelf-ready CLS episodic + coverage machinery activates.
- downstream_needed: a read()-time meaning consumer (the same missing reader_meaning_channel); only current consumer = default-off consolidation_gate.
- adjacent_or_optim: cross-corpus WiC/SemEval generalization (untested axis); coarse/polysemy-merged grain; concrete rare-sense stratum (+0.035) may be independently landable.
- followon_filed: cross-corpus WiC/SemEval generalization.
- full_gain_realized: NO — readout landed but default-off/latent; coverage half is an unwired located negative gated on §2.

### build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader
- one_line: Tested whether a richer grounded ATL hub-and-spoke sense representation crosses the ~0.35 ceiling — it does not (located negative); query-side precision-weighting gives a real CI-sep gain.
- claimed_gain: precision-weighting (gamma>1/top-k) a_s 0.313→0.336 (+0.023 CI-sep), twin loses (does NOT reach 0.35). Located negative: grounded hub 0.283 < 0.313; full chain stalls ~0.34 even with ideal gold-W.
- instrument: subject-weighted a_s on doc-disjoint SemCor subordinate (n=2676) via hdlab/diagnostic_context_wsd (W1–W8). NOT the live board.
- verdict: EXCELLENT — located negative (full pass) + one landable positive. PARTIAL; owner DONE.
- landed_live: gamma/topk precision-weighting params landed on diagnostic_context_wsd, DEFAULT byte-identical, opt-in (witness 4/4). DID NOT land grounded-hub keys / reading-W / trained encoder.
- realized_on_board: NONE YET (param live but default byte-identical; no read()-time meaning consumer).
- upstream_needed: contextual per-occurrence re-representation = §2 boundary (rec HOLD).
- downstream_needed: a read()-time WSD/meaning consumer to feel the +0.023 (missing reader_meaning_channel); consumers opt into gamma/topk.
- adjacent_or_optim: syntactic-argument-restricted precision query (last within-invariant lever, ~+0.01). DO NOT reinvest in grounding/W-coverage/exemplars/discourse (6 converging located negatives).
- followon_filed: grow_broad_coverage... (pri 5).
- full_gain_realized: PARTIAL — precision-weighting landed but default-off/latent; +0.023 realized only when a meaning stage opts in; ceiling-crossing gated on §2.

### break_the_contextual_input_encoding_ceiling_for_specific_sense_selection
- one_line: Tested a self-supervised glass-box contextual encoder — it does not cross the ~0.33 ceiling; the decisive finding: the lever is a broad-coverage, clean, SENSE-DISCRIMINATIVE W (oracle W → a_s 0.995), coverage-limited today.
- claimed_gain: pure located negative + numbered lever. Encoder best 0.293 < wired diagnostic 0.307–0.317; readout saturated (settling 0.312 = one-shot). Oracle sense-discriminative W → a_s 0.995; learned W beats topic on covered senses 0.367 vs 0.308 (+0.059); bottleneck = COVERAGE (52%).
- instrument: subject-weighted a_s on doc-disjoint SemCor subordinate (n~2676) via hdlab/diagnostic_context_wsd (test 10/10, CPU). NOT the live board.
- verdict: EXCELLENT — located negative (valid pass, no wire) + a numbered redirect. PARTIAL; owner DONE.
- landed_live: NO hdlab wire (located negative — nothing beat the wired diagnostic_context_wsd). Transformer fork refuted.
- realized_on_board: NONE (no wire).
- upstream_needed: none within the invariant (bigger encoder rejected).
- downstream_needed: none directly (a REDIRECT).
- adjacent_or_optim: the discourse/situation-model prior (Stage 4, unbuilt) is the one new brain-faithful build that could source a better W.
- followon_filed: REDIRECT into build_the_controlled_knowledge_growth_consolidation_gate (pri 1) + acceptance test exp_sg_lite_sense_discriminative_W_headroom_v1.
- full_gain_realized: NO — pure located negative; value is the numbered redirect into the knowledge-growth program.

### build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner
- one_line: Built the glass-box consolidation gate (extract→consolidate→admit); PASSES when knowledge is clean (curated foundation +0.067) but the reader cannot grow clean knowledge from its own reading (narrow located negative), localizing the ceiling to the frozen sense-superposed w2v.
- claimed_gain: admitting a CONSOLIDATED clean foundation → a_s 0.2512→0.3178 (+0.067 CI-sep), raw-reading twin LOSES (−0.033). Located negative: reading-derived consolidation caps at gloss ~0.251. cls_growth safe (+0.110/6 rounds).
- instrument: subject-weighted a_s on doc-disjoint SemCor subordinate (n=2676) via hdlab/diagnostic_context_wsd (test 14/14). NOT the live board.
- verdict: EXCELLENT — gate positive wrapping a mechanism-complete narrow located negative. PARTIAL; owner DONE.
- landed_live: consolidate + raw_assocs + regression_guard promoted VERBATIM → hdlab/consolidation_gate.py (offline admission GUARD, composes with hdlab/cls_growth). Witness 7/7. NOT wired default-on; diagnostic_context_wsd unchanged.
- realized_on_board: NONE YET (gate is a live offline admission guard; the +0.067 clean-foundation LIFT is latent — needs the read()-time meaning consumer).
- upstream_needed: the clean-foundation wire (relations+SyntagNet+ConceptNet as sense atoms) = the +0.067 PASS — recommended LAND; overlaps LATENT meaning_foundation.py.
- downstream_needed: a read()-time WSD/meaning stage to feel the +0.067; cls_growth as the learner-on safety wrapper (present). Reading-derived growth must NOT be default-on.
- adjacent_or_optim: the ATL hub-and-spoke + online predictive reader named as the ONLY brain-foundational route through the ~0.35 ceiling.
- followon_filed: build_the_atl_hub_and_spoke_meaning_channel (P9).
- full_gain_realized: PARTIAL — gate + guard landed live as an offline wrapper; the +0.067 clean-foundation lift latent (no read()-time meaning consumer).

### validate_the_ppmi_svd_means_end_bridge_on_real_narrative_marker_less_goal_attachment
- one_line: Tested whether the PPMI+SVD means-end bridge validates on real narrative — it does NOT (info-free twin matches it → a goal-frequency artifact); two real walls located (purpose-extraction precision 0.27; context-free means-end knowledge).
- claimed_gain: REFUTED (located negative). Real LitBank purpose_bare: bridge K1 0.559 vs twin p95 0.533 (not sep); clean advcl-only 0.586 vs 0.574 (not sep). n=16 authored PoC 0.9375 was overfit.
- instrument: matched-population means-end discrimination + shuffled-map twin floor, via exp_meansend_realtext_validate_v1 (test 9/9). NOT the live board.
- verdict: STRONG — rigorous located negative. Status REFUTED. **⚠ No OWNER_NOTES.md / no owner_verdict yet — OPEN, do NOT front-run.**
- landed_live: NO hdlab wire. Proposed (verdict-independent) upstream purpose-precision fix in hdlab/goal_register.py; (HOLD) do NOT wire the bridge in build_goal_graph.
- realized_on_board: NONE (bridge refuted; upstream fix only proposed).
- upstream_needed: register-native dependency parser (advcl vs xcomp) for the 0.27-precision wall — filed parser_arceager.
- downstream_needed: goal-register consumers (_read_goals goal arm, goal_hierarchy_graph, affect_register, commonnoun_binder); upstream purpose fix removes 131 wrong vs 24 genuine (5.5:1) on why() — net-positive, NOT landed.
- adjacent_or_optim: CONTEXTUAL inverse planning (goal posterior conditioned on the situation model) + goal/belief unification (highest value); activation-weighted reinstatement prior for wants() (small verdict-independent fidelity upgrade).
- followon_filed: none new; points to parser_arceager + recommends a CONTEXTUAL inverse-planning brief.
- full_gain_realized: NO — bridge refuted + correctly unwired; the one net-positive piece (upstream purpose-precision fix) proposed not landed; owner verdict not yet recorded.

---

## Chunk D — perf / tagger / parser (harvested 2026-09-05)

> Most of these are byte-identical speedups = **fully realized, live**. TWO exceptions carry unrealized value: (1) the **CRF calibrated posterior organ is LATENT** (consumer predicate_detector default-off → +0.041 event recall / +0.31 reachability unrealized); (2) the **arc-labeler fast path is NOT landed yet** (land-ready, ~54% whole-read cut).

### numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever
- claimed_gain: parser 1.61–2.16x (2.6x longest); parse-in-read 1.87–2.13x; byte-identical (434,330 arcs, 0 mismatch); whole-read within noise (parser ~7%).
- landed_live: LANDED VERBATIM into hdlab/arc_parser.py (length-gated n≥16), default-ON. Witness 393,225 arcs bit-identical.
- realized_on_board: NONE (byte-identical). upstream/downstream: none. adjacent: POS-tagger Viterbi (same technique, filed); typed selectional-preference features (closed inventory → same vectorization).
- full_gain_realized: YES — fully live; no accuracy follow-on owed.

### optimize_the_arc_parser_inner_loop_the_dominant_read_cost
- claimed_gain: arc parser 3.53x (parse cost −72%); byte-identical (393,225 arcs, 0/376); warm read 1.13–1.45x. (Corrected brief's "73%"→~26%.)
- landed_live: FeatCache/precompute_token/sentence_flat/sentence_scores/decode_from_scores VERBATIM → hdlab/arc_parser.py, default-ON; stock kept as _parse_reference. Witness 4/4.
- realized_on_board: NONE (byte-identical). adjacent: POS-tagger inner-loop; the numpy-vectorized gather (became the row above); mechanism-label correction (arc-FACTORED graph parser, not shift-reduce); the real accuracy wall = typed lexical-semantic grounding/PP-attachment (0.587→0.639), routed to the meaning channel.
- full_gain_realized: YES — fully live.

### optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost
- claimed_gain: tagger 4.4–5.25x per-call (cost −77–81%); byte-identical emission matrix AND tags (0/694); read-level 1.19x.
- landed_live: _FastEmissionPlan → hdlab/pos_tagger.py + perceptron._viterbi routing (training path untouched), default-ON. Witness 3/3; full-read fingerprint unchanged.
- realized_on_board: NONE (byte-identical). downstream OPPORTUNITY the speed unlocks: hard-1-best consumers (referent_per_np, consequence_learning VERB-gate) could consume the now-affordable GRADED FB/CRF posterior. adjacent: the graded ranked-parallel decode is byte-identical on 1-best AND cheaper — cashes to accuracy only once top-down meaning re-ranks; PROPN↔NOUN = 28% of tag errors (meaning wall).
- followon_filed: graded-posterior consumption family (became consume_the_graded_pos_posterior...).
- full_gain_realized: YES for speed; the graded-decode ACCURACY payoff is a named unrealized follow-on (gated on meaning/grounding).

### upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior
- one_line: A likelihood-trained glass-box dependency-free (pure-numpy) calibrated CRF POS posterior P(VERB) recovering old-prose dropped verbs; the brief's JOINT tagger-parser decode is a located negative.
- claimed_gain: CRF AUROC 0.9409 / recovery 0.8727 @FP≤0.5 (vs perceptron 0.582); DEPLOYED free-text 19c event recall 0.9382→0.9792 (+0.041 CI-sep); downstream who-did-what reachability +0.3091 on genuine-drop subpop; joint decode +0.0017 (located negative); reproduces crfsuite to 7.3e-7.
- instrument: 19c LitBank transfer, spaCy-oracle event gold (n_dropped=538); witnesses 5/5, 3/3, 3/3. NOT a board dim.
- verdict: EXCELLENT — deployable dependency-free win + a located negative on the joint decode.
- landed_live: hdlab/crf_tagger.py (GlassBoxCRF, pure-numpy, no crfsuite/LLM) + asset LANDED; witness 5/5. **BUT LATENT — its consumer predicate_detector is DEFAULT-OFF → no live board consumer.**
- realized_on_board: NONE — organ latent; +0.041 event recall / +0.31 reachability are on deployment/diagnostic instruments.
- upstream_needed: base-model capacity / target-register training data (spaCy oracle recovers 0.82/0.88); the parser's OOD word-order fidelity is the dominant full-pop leak.
- downstream_needed: **predicate_detector must be turned on with a HIGH-PRECISION verb-recovery gate** (the recall-tuned threshold floods the parse: 6576 forced VERBs collapse reachability 0.698→0.497). The category-cue swap verb_margin→logit(CRF vpost) lifts predicate_detector 19c recall 0.582→0.806 — READY when the consumer wires.
- adjacent_or_optim: joint parse-decode (+0.0017 located negative) + delexicalized parser (−8 UAS) retired.
- followon_filed: successor (base-model capacity / register data); selection routed to meaning-hub/NP-head (SOLVED)/copular is-a (filed).
- full_gain_realized: PARTIAL — CRF organ landed + byte-faithful but LATENT; consumer default-off, so +0.041/+0.31 unrealized until wired with precision-guarded gating.

### route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger
- claimed_gain: ~0.37s/read off the affect path (NLTK 195→0 calls); read cut ~11.5%; VALENCED affect byte-identical (0 flips/8947); inert NA↔None ~9% (located-negative sub-finding, 0 consumers branch on it).
- landed_live: _assign_affect tags via the shared UD-EWT tagger (no NLTK); context_grounded_valence.score_item gains need_valence. Live; witness 6/6, landing 0 flips/1124.
- realized_on_board: NONE (byte-identical valenced/affect). adjacent: **the arc-labeler naive per-label loop (~10x the affect tagger, ~0.87s/read, _FastLabelPlan built+witnessed) → the next row**; tag_punct NLTK PENN tagger in temporal = a located negative for a UPOS reroute (needs XPOS or route via EventRecord.tense) — NOT resolved; grounded-valence wire near-dormant (1 valenced firing/8947).
- followon_filed: the arc-labeler fast-path (next row); tag_punct/temporal-tense XPOS (named, filing recommended).
- full_gain_realized: YES — speedup fully live; no accuracy follow-on owed.

### add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost
- one_line: A byte-identical fast scoring path for the arc labeler's 36-label per-arc perceptron + the graded brain-faithful readout it materializes for free.
- claimed_gain: labeler scoring 8.73x in-read (−4.2s/read); **whole-read ~54% cut on 3 full docs (26.56s→13.28s, CI-sep)**; byte-identical (0/22,921 arcs; full SituationModel byte-identical); graded readout argmax byte-identical (0/18,346) + entropy flags labeling errors gold-free AUC 0.930.
- instrument: labeler-in-read timing (3 full docs) + byte-identity witness (22,921 held-out arcs) + graded readout (UD-EWT test n=18,346).
- verdict: EXCELLENT-caliber — byte-identical speedup + a brain-foundational graded readout. **NOT yet integrated (PROBLEM.md still OPEN, no owner verdict).**
- landed_live: **NOT LANDED YET** — proposed Q111 diff only (add _FastLabelPlan + ArcLabeler._ensure_fast to hdlab/arc_labeler.py). Mechanism + witnesses ready in experiments/. Once landed it runs default-on (labeler is live via bind_entity_states).
- realized_on_board: NONE yet (not landed); when landed byte-identical → no board move (pure speedup, but the biggest single read-cost).
- upstream_needed: the PARSER is the dominant leak (~21% heads wrong even w/ gold POS; obl:agent LAS 0.0588); feed the parser DISTRIBUTED contextual reps; flip the dormant arc-eager parser (+0.05 free).
- downstream_needed: entity_states/copular binder + who-did-what readout should consume the graded label posterior + entropy (not hard 1-best) — belongs with consume_the_graded_pos_posterior.
- adjacent_or_optim: per-arc INDEPENDENCE (no joint one-role-per-clause decode — CRF/bipartite, Theta-Criterion), Q113; confidence-gated parser hybrid = located negative.
- followon_filed: none new; maps onto existing Q113 problems.
- full_gain_realized: NO — land-ready but NOT wired (OWNER verdict pending); a ~54% whole-read speedup sitting on the shelf. **⇒ high-value near-term land once owner-DONE.**

---

## Chunk B — who-did-what / coref (harvested 2026-09-05)

> **⚑ FINDING: the who-did-what STACK is largely live (cm_agent, cm_agent_struct, referent_per_np, structural_patient all default-on), but the board UNDER-MEASURES it.** The events QA is AGENT-only, so the +0.086 patient gain is invisible; the LitBank object/patient gold is ~76% oblique-CONFOUNDED (flagged INVALID). Realizing these gains needs a BOARD-INSTRUMENT upgrade (patient-slot QA on clean UD gold), not more mechanism.

### improve_the_parser_verb_argument_attachment_for_who_did_what
- claimed_gain: LIVE arc_parser patient on clean UD-EWT (n=1255) 0.7450→0.8311 (+0.0861 CI-sep, ~52% of the gap to 0.913 gold-parse ceiling); 19c clean-DO (n=669) +0.0972.
- instrument: CLEAN UD-EWT structural gold (LIVE arc_parser heads) — NOT the live board; the LitBank OBJECT gold is barred as confounded.
- verdict: EXCELLENT — positive win that DID land live but is board-invisible + fair located negatives (head lever; precision-weighted re-attach).
- landed_live: WIRED. 3 Q111 diffs in hdlab/predicate_argument_frontend.py (precise_passive + labeled/valency structural_patient_pick, live in route_predicate_arguments) + parser_arceager DEFAULT-ON. Real read()-time consumer.
- realized_on_board: **NONE YET** — +0.0861 on clean UD only. No-regress run: 2718/8049 patient picks changed yet all 6 board dims 0.0-delta (events QA agent-only; LitBank patient gold confounded).
- upstream_needed: a more precise register-invariant CLAUSE SEGMENTER (owned by the agent-tie problem; not a patient lever). For the patient itself: none.
- downstream_needed: **a PATIENT-slot who-did-what QA on clean gold — the live events QA is agent-only, so +0.086 is invisible end-to-end. NOT built (filed).**
- adjacent_or_optim: per-arc parse CONFIDENCE (AUC 0.81, ZERO live consumers, unwired); obl/PP head attachment (0.69→1.0 gold) for SPACE consumers; graded verb_subcat presence gate (built-unwired, WIRING DEBT 2); categorical-backbone register-general parser (built + Jabberwocky-validated, handed to the agent problem).
- followon_filed: add_a_patient_slot_who_did_what_qa_on_clean_gold; clause-segmenter → the_agent_tie_wall...
- full_gain_realized: PARTIAL — readout + arceager live in hdlab; +0.086 invisible on the board (events QA agent-only, LitBank patient gold confounded); needs a patient-slot QA on clean gold before any board move.

### swap_the_positional_role_assigner_for_the_brain_foundational_competition_model
- claimed_gain: LIVE board who-did-what AGENT cm_ON 0.2519 vs pre-referent 0.2257 (+0.0262 CI-sep); recovery over the referent regression 0.0410→ +0.2109; full stack 0.041→0.690 tuned/0.682 held; landing 0.041/0.075→0.6073 (+0.4689 CI-sep).
- instrument: **the LIVE board itself** (build_events_questions → _answer_events(agent), n=1830 agent Qs).
- verdict: EXCELLENT — a POSITIVE live-board WIN (recovers a real board regression, banks the stranded +0.336 patient).
- landed_live: WIRED default-on. hdlab/graded_role_assigner.agent_competition_pick (reusing graded_competition.net_activation) + situation_reader routes the tracked/coref set as AGENT source; cm_agent/include_pron_agents/case_filter/clause_local/cm_agent_struct all default-True.
- realized_on_board: **YES** — who-did-what AGENT (events dim) recovers 0.041/0.075→0.6073. Direct move on the live events dimension.
- upstream_needed: register-general incremental parse cue for the 75%-embedded-clause tie wall — NOW BUILT (cm_agent_struct default-on); a fuller register-general parser is the open frontier.
- downstream_needed: the board's context-cued answer_instanced readout — BUILT/landed with the wire.
- adjacent_or_optim: event/predicate-detection recall (20% of residual); coref coverage (5%); thetic/presentational/unaccusative construction detector (~20% new-agent ceiling, not built); animacy_lexicon coverage; register weight re-sweep for modern; passive PATIENT via precise_voice (still default-off).
- followon_filed: the_agent_tie_wall... (now owner-DONE, structure cue landed).
- full_gain_realized: **YES** — full stack wired default-on, board agent/events arm realizes 0.041/0.075→~0.61–0.69; named further optimizations remain but the assigned gain is realized.

### the_agent_tie_wall_is_embedded_clauses_needs_a_register_general_incremental_parse_cue
- claimed_gain: tie slice tuned 0.6372→0.7098 (+0.0726 CI-sep); held-out 0.6178→0.6739 (+0.0562); canonical no-regress; shuffled-structure twin loses CI-sep.
- instrument: LitBank 19c board who-did-what AGENT, TIE slice only (context-cued readout). NOT a full 9-dim board re-run.
- verdict: EXCELLENT — positive win landing a live wire.
- landed_live: WIRED default-on. cm_agent_struct=True; _cm_agent_for imports incremental_subject_before from hdlab.incremental_parser, feeds subj_before into agent_competition_pick; structure cue in agent_supports (AGENT_VALIDITIES["structure"]=2.5).
- realized_on_board: events (AGENT). Mechanism live + default-on, BUT headline is tie-slice instrument only — **no live board re-run**, so NONE YET as a board-dim delta.
- upstream_needed: register-robust event detection (58.6% of tie residual = predicate not detected) — predicate_recall (BUILT, was default-off, **flipped ON 2026-09-05**); coref recall; collective-human animacy patch (prototyped).
- downstream_needed: none (feeds the already-live graded_competition).
- adjacent_or_optim: gated relcl filler-gap organ (built, not wired for matrix-after-RC); collective-human animacy fold-in; gerund-possessive exception. Closed negatives: recency/prominence-Centering, eADM precision, thematic-fit.
- followon_filed: register_robust_event_detection_turn_on_and_expand (now owner-DONE).
- full_gain_realized: PARTIAL — structure cue fully live/default-on (mechanism realized), but headline is instrument-only (no board re-run); whole-arm levers (predicate_recall now on; coref recall) partly unrealized.

### construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set
- claimed_gain: LOCATED NEGATIVE — construction adds +0.0000 over live hybrid_role_patient (selector n=149 +0.0000; full n=669 −0.0030; multi-DO −0.0123; end-to-end +0.0000; QA-SRL −0.0008). Side win: indef-pronoun source coverage +0.0105 CI-sep.
- instrument: cleaned-DO 19c LitBank selector + end-to-end read() (n=1354) + QA-SRL. NOT the live board.
- verdict: EXCELLENT — rigorous REFUTED located negative (full pass, selector at ceiling).
- landed_live: NO hdlab wire (located negative). The indef-pronoun win DEFERRED to wire_the_referent_to_coref_linking_pass (latent/gated).
- realized_on_board: NONE (located negative, 0.000).
- upstream_needed: turn ON referent-per-NP SOURCE (deployed 0.47/0.21→selector 0.93; +0.336) — gated on the coref linker (now built); register-native POS tagger.
- downstream_needed: none (selector already the live consumer; null = no new signal).
- adjacent_or_optim: filler-gap parser for pseudo-clefts; discourse old/new for locative inversion; small-clause extractor; meaning-fit selector (gated on the meaning channel); indef-pronoun coverage (+0.0105 prototyped). Folded 2 parent corrections into §2b (do NOT adopt ideal_pick).
- followon_filed: none as its own slug (indef-pronoun folded into the linking-pass wire).
- full_gain_realized: NO — located negative, no wire; indef-pronoun win (+0.0105, 19c) latent, deferred to the referent-per-NP source wire.

### form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref
- claimed_gain: deployable former CoNLL 0.6174 vs surface_head 0.6046 (+0.0128 CI-sep); naive former = located negative (+0.0008 n.s.); entity-world-model crosses 0.255→0.540 GIVEN gold records but self-built +0.006.
- instrument: LitBank gold coref, 100 docs, CoNLL char-cluster population (NOT the board) + affect-experiencer subpop.
- verdict: EXCELLENT — located negative (world-knowledge-bound) + reframe + a small landable +0.0128.
- landed_live: WIRED default-on. hdlab/commonnoun_binder.py (situation_predict) via _apply_commonnoun_gate (commonnoun_situation_gate=True) + commonnoun_canonical=True into GR.make_canonicalizer.
- realized_on_board: **NONE YET** — goal/affect QA IDENTICAL on-vs-off (0.4615==0.4615, 0.7288==0.7288); +0.0128 on the CoNLL instrument only; experiencer subpop near-ceiling.
- upstream_needed: **an ENTITY WORLD-MODEL resolver seeded by a world-knowledge PRIOR (curated scenario/role + kinship KB) to break the identifiability wall → realizes the 0.54 ceiling. Resolver BUILT but capped; the KB prior = the STAGED entity-KB resolver (pri 2).**
- downstream_needed: character-bound canonicalizers (affect/goal/world-state) consume common-noun clusters — BUILT (commonnoun_canonical default-on); pair with the pronoun graded resolver — NOT done.
- adjacent_or_optim: reuses event_centrality_coref + graded_coref_pick. Measured-capped: WordNet bridging (7.8%), 2-pass (+0.0045), confidence-gating (+0.0056).
- followon_filed: the Phase-1 world-knowledge-prior entity-world-model resolver (= the STAGED pri-2 slug).
- full_gain_realized: PARTIAL — +0.0128 live/default-on, no board move; the big win (+0.43 headroom / 0.54 resolver ceiling) gated on the Phase-1 KB (staged this session).

### open_a_discourse_referent_for_every_np_not_just_coref_mentions
- claimed_gain: effective who-did-what PATIENT 0.4698→0.8054 (+0.3356 CI-sep) on cleaned-DO; full noisy pop (n=1354) +0.0473; candidate coverage 0.8183→0.9705 (+0.1521); twin LOSES and HURTS.
- instrument: LIVE read() with only the mention source swapped, cleaned 19c DO gold (n=149) — deployment instrument, NOT the board.
- verdict: EXCELLENT — deployment-ceiling recovery through the live reader (twin loses+hurts, REPLACE>ADD).
- landed_live: WIRED, now DEFAULT-ON. hdlab/referent_per_np.py consumed at read() under the referent_per_np flag. Originally default-off (coref collapsed 0.48→0.02); flipped ON after the linking-pass decouple.
- realized_on_board: NONE cleanly attributable — +0.336 on its own cleaned-DO PATIENT instrument; the dense set transiently REGRESSED the board AGENT (0.252→0.075) until cm_agent co-landed; whole-stack aggregate 0.2903→0.3598.
- upstream_needed: none (this IS the mention source; frame detector built-in).
- downstream_needed: (1) referent→coref LINKING pass — BUILT/owner-DONE; (2) Competition-Model AGENT assigner — BUILT/owner-DONE (cm_agent); (3) construction-aware selector — refuted.
- adjacent_or_optim: wire thematic_role_labeler as the SELECTOR (organ exists, +0.264 non-canonical, filed); meaning-fit selector (gated on meaning channel); register-native POS/NER (0.914→~1.0 cap); NP-type tag pass.
- followon_filed: wire_the_referent_to_coref_linking_pass + construction_aware_selector (P4); register-robust detection (P6).
- full_gain_realized: PARTIAL — source live/default-on + both turn-on blockers built; +0.336 patient wired but measured on its own instrument; board agent needed co-landed cm_agent to avoid net regression; the biggest remaining loss (selection→0.913) prototyped/refuted-not-landed.

### wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on
- claimed_gain: coref recovers to NO regression / byte-identical (decouple−OFF −0.069 not sep; recovery over the regression +0.298); who-did-what +0.336 inherited; brief's expand-pool REFUTED −0.106 CI-sep; BONUS entity-key overlay +0.0429 CI-sep ABOVE baseline (NOT required for turn-on).
- instrument: 100 docs 19c LitBank coref, pooled pronoun coref_acc — NOT the board. (Post-integration board: coref_acc 0.5255==0.5255 on/off.)
- verdict: EXCELLENT — turn-on win (decouple unblocks default-on) wrapping a located negative (expand-pool refuted).
- landed_live: LIVE-WIRED. read() builds TWO mention views (role_mentions ← referent_per_np; coref_mentions ← coref for pronoun anaphora); referent_per_np DEFAULT-ON.
- realized_on_board: coref = **NO MOVE** (held byte-identical 0.5255; collapse prevented but no gain; the +0.043 above-baseline bonus NOT landed). events = PATIENT +0.336 live; AGENT transiently regressed until cm_agent landed.
- upstream_needed: the complete referent set IS the upstream (built/live); referent feature typing (_mk_referent opens blank cards) — NOT built; indef-pronoun source coverage (+0.0105) — not built here.
- downstream_needed: positional AGENT assigner → Competition-Model (cm_agent) — BUILT/LIVE.
- adjacent_or_optim: **overlay-by-discourse-entity coref bonus (+0.043–0.054 CI-sep ABOVE baseline) — NOT landed (needs an owner decision: it uses the coref column's provided clustering);** step-5 per-character individuation organ — MEASURED NEGATIVE (converges ~0.55).
- followon_filed: swap_the_positional_role_assigner (owner-DONE + live). Overlay-by-entity bonus flagged as candidate standalone pending owner decision.
- full_gain_realized: PARTIAL — decouple live, referent_per_np default-on, cm_agent fix live; the turn-on claim (coref no-regress + patient +0.336) realized; **the +0.043 above-baseline coref bonus NOT landed (board coref stays at baseline) — a candidate near-term win pending owner decision.**

### the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses
- claimed_gain: effective end-to-end (abstain=wrong) 0.9851; recomputed vs current reader 0.7877→0.9851 (+0.1973 CI-sep); QA-SRL 0.5678→0.9025 (+0.3347); twin loses; no precision regression.
- instrument: 669 clean-19c DO clauses + QA-SRL — NOT the board.
- verdict: EXCELLENT — positive recovery diagnosis, but the one clean wire landed (structural-DO filter) is KEPT DEFAULT-OFF; the verb-ID portion is a located negative (needs a trained joint POS+parse).
- landed_live: hdlab/structural_do.py + structural_do_recover flag **DEFAULT-OFF** (recovery precision 0.385 on ~76%-oblique-confounded 19c gold; unmeasured downstream harm).
- realized_on_board: NONE YET — the only wire (structural_do_recover) is default-off; +0.1973/0.985 on its own 669-clause harness. (The live reader's 0.629→0.7877 came from np_head_reduce + predict_revise, not this wire.)
- upstream_needed: register-robust predicate identification (20 no-event) — predicate_recall BUILT + LIVE (flipped on 2026-09-05); the deeper joint-POS build (beam_decoded_joint_pos_dependency_parser...) — filed, NOT built.
- downstream_needed: **the ~20 role-output organs (world_state/causation/hd_fact_store) must be re-validated to inherit the fix — PENDING; kept default-off precisely because feeding low-confidence recovered patients would assert FALSE facts.** Gate before flip: (a) a CLEAN 19c gold + info-free random-recovery twin LOSING, (b) a downstream-consumer regression check — both NOT built.
- adjacent_or_optim: structural-DO subsumes the verb_subcat_gate hard veto (landed default-off); object-gap → landed relcl_resolver (re-tread); ditransitive recipient-vs-theme (cheapest win, belongs to the non-canonical problem); non-canonical gold must be REBUILT (~96% broken).
- followon_filed: open_a_discourse_referent_for_every_np (P5); register_robust_event_detection (P6, owner-DONE + live); beam_decoded_joint_pos_dependency_parser (scaffold handed, not built).
- full_gain_realized: NO — the one wire (structural_do_recover) DEFAULT-OFF (low/confounded recovery precision + unmeasured downstream harm); +0.1973 on its own harness. Needs a clean 19c gold + random-recovery twin + a downstream regression check before realization.

---

## SUMMARY — the realization scoreboard (claimed gain → is it live on the board?)

Legend: **YES** fully realized · **PARTIAL** mechanism live, full gain pending · **NO** latent/default-off/unwired/located-negative-no-wire.

| Component | Claimed gain (instrument) | Live status | Realized on board? |
|---|---|---|---|
| **causal mental-bridge** (this session) | UNIFIED 1.000 vs force 0.500; +214 mental links | LIVE default-on pure-add | **NO** — instrument gap (no mental-causal board arm); + 3 downstream signal-updates pending |
| **entity-KB resolver** (pri 2, staged) | common-noun coref +0.0809; relational ref +0.1440 | STAGED (reverified 6/6), not wired | **NO** — held for the pass; unlocks the +0.43 coref ceiling |
| swap_positional_role_assigner (cm_agent) | agent 0.041/0.075→0.61–0.69 | LIVE default-on | **YES** — events/agent arm moved |
| improve_parser_verb_arg (patient) | patient +0.0861 (clean UD) | LIVE default-on | **NO** — events QA agent-only + LitBank patient gold confounded (needs patient-slot QA) |
| agent_tie_wall (cm_agent_struct) | tie +0.0726/+0.0562 | LIVE default-on | PARTIAL — tie-slice only, no board re-run |
| register_robust_event (turn_on) | agent +0.0945; board +0.0667 | LIVE (predicate_recall on, scoped) | **YES** — events who-did-what moved |
| copular state-QA (bind_entity_states) | qa_state 0/378→0.826 | LIVE default-on | **YES** (modern UD-EWT) — state dim; 19c coverage-only |
| affect dimension | feel 0.788 / valence 0.838 | LIVE default-on | **YES** — affect dim; capped by unbuilt common-noun coref |
| goal dimension | WANT 0.61 / WHY 0.98 | LIVE default-on | **YES** — goal dim |
| goal-hierarchy graph | plot 0.68→1.00 | LIVE default-on pure-add | **NO** — instrument gap (no goal_hierarchy board arm) |
| referent_per_np + linking-pass | patient +0.336; coref no-regress | LIVE default-on | PARTIAL — patient on own instrument; **+0.043 coref bonus NOT landed** |
| curated meaning foundation | WSD +0.0755; hub MaxSim +0.065 | LATENT (loader only) | **NO** — no read()-time meaning consumer (pri 4) |
| rare-sense Bayesian readout | a_s +0.065 | LANDED default-off | **NO** — no live meaning consumer |
| ATL precision-weighting (gamma/topk) | a_s +0.023 | LANDED opt-in byte-identical | **NO** — no live meaning consumer |
| consolidation gate | clean-foundation +0.067 | LIVE as offline guard | **NO** — the +0.067 lift latent (no read()-time consumer) |
| CRF calibrated posterior | 19c event recall +0.041; reach +0.31 | LATENT organ | **NO** — consumer predicate_detector default-off |
| arc-labeler fast path | ~54% whole-read cut, byte-identical | **NOT LANDED** (owner-DONE pending) | NO — land-ready, high-value |
| structural_do_recover | who-did-what +0.1973 (own harness) | LANDED default-off | **NO** — needs clean gold + downstream regression check |
| arc-parser vectorize / inner-loop / tagger Viterbi / affect reroute / lean profiles | byte-identical speedups | LIVE default-on | YES (perf — no score change; fully realized) |
| break_contextual_ceiling / construction_selector / means-end-bridge | located negatives | NO wire (valid pass) | — (correctly nothing to realize) |

## TOP-DOWN INTEGRATION PASS — the ordered work-list (start upstream, iterate down; measure each step)

**The five cross-cutting levers, most-upstream first. Each: turn on / wire → measure the board off-vs-on → update the downstream consumer to RECEIVE the signal → measure again → lock.**

0. **BOARD INSTRUMENT UPGRADE (do FIRST — several live gains are invisible).** The board under-measures the reader: (a) events QA is AGENT-only → add a **PATIENT-slot who-did-what QA on clean UD gold** (the LitBank patient gold is ~76%-oblique CONFOUNDED = INVALID; re-base who-did-what on clean UD); (b) add a **goal_hierarchy multi-hop board arm** (only 4% of current goal-why is multi-hop). Without this, the patient +0.086 and the plot 0.68→1.00 stay invisible and the pass can't attribute gains.
1. **Event/predicate tier — wire the CRF posterior → predicate_detector** with a HIGH-PRECISION verb-recovery gate (the recall-tuned threshold floods the parse: 6576 forced VERBs collapse reachability 0.698→0.497). Cashes +0.041 19c event recall / +0.31 reachability. Then re-validate the ~20 role-output organs (structural_do_recover's blocker).
2. **Coref/entity tier — land the STAGED entity-KB resolver (pri 2)** into the live reader (sm.entities head-coref coupling; NOT the agent head-match). Unlocks the common-noun coref ceiling (+0.43 headroom / 0.54) that caps affect experiencers (87% of affect loss) and goal/relational binding. Also decide the **+0.043 above-baseline coref bonus** (overlay-by-discourse-entity) — an owner call, near-term.
3. **Who-did-what tier — with the patient-slot QA live (step 0), realize the +0.086 patient**; sweep the remaining named optimizations (thetic/unaccusative construction detector ~20% new-agent ceiling; animacy_lexicon coverage; register weight re-sweep).
4. **Meaning tier (THE big latent cluster) — build the ONE read()-time meaning stage** (`reader_meaning_channel`) that consumes the curated foundation. Within-invariant now: the curated-foundation KEYS + rebuild composed_hub_predictor on the 80k store + MaxSim (pri 4), stacking the landed gamma/topk + sense_prior. Cashes +0.0755 / +0.065 / +0.023 / +0.067 at once. **The FINE rare-sense half is §2-GATED (the contextual-encoder owner decision — rec HOLD).**
5. **Downstream signal-updates — feed the new event-TYPE signal (from the causal landing) to its 3 consumers:** causation_typing → mental typing (3/16→16/16); affect_register → OCC-appraisal inferred-emotion channel; goal-graph → motivational spine. And mine the mental-bridge gold (the missing scored instrument).

**Land-ready now, verdict-permitting:** the arc-labeler fast path (~54% whole-read cut — land the moment it's owner-DONE).

**Then:** a fresh FULL board with everything integrated = the realized aggregate (the number we've never measured end-to-end). Every claimed gain in the scoreboard above should have a board dim that moved by then, or a named reason it can't (invariant / instrument gap / located negative).

**Gating owner decision:** §2/P9 — HOLD the no-transformer invariant (strategy rec) vs relax for one offline contextual encoder. This gates the entire FINE rare-sense / contextual-meaning cluster (steps 4's fine half). The within-invariant work (steps 0–5) proceeds regardless.
