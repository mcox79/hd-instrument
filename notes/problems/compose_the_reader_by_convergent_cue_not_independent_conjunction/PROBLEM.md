---
priority:
review: EXCELLENT
review_text: "Convergent-cue = log-Bayes product of the episodic + meaning posteriors (CA3 completion + reliability-weighted cue combination) beats the STRONGEST floor meaning-solo 0.700->0.744 (+0.044 CI-sep), re-verified 7/7 FIRST-HAND. Every control passes: shuffled-meaning collapses, shuffled-EPISODIC falls below meaning-solo (win needs REAL episodic evidence = genuine convergence), fused-pool loses + kills the dissociation, double dissociation preserved, lift localised. Brain-faithful (PINNED product rule; OUR-INVENTION calibrated w honestly labelled) and it CAUGHT my brief's straw floor (0.119, below either solo) and re-aimed correctly. Rule AT ceiling; residual = dense store -> compounds with p2. Landed hdlab/convergent_cue_reader.py (witness PASS, registered, default-off island)."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-27 (strategy session; grade EXCELLENT)
> **Re-verified FIRST-HAND** (`verification/test_convergent_cue_composed_reader.py`, 7/7 PASS — suspected my own checker, ran it).
> **Result:** convergent-cue read `argmax_c [log softmax(epi/tau_e) + w·log softmax(sem/tau_s)]` = **0.7438**, beating the
> **strongest** floor meaning-solo **0.6998 by +0.044 CI-sep [0.030,0.058]** on the exact STEP-18 population (held-out n=3681).
> **Argument audit (not just arithmetic):** the decisive control holds — the shuffled-EPISODIC twin (0.667) falls *below*
> meaning-solo and the headline beats it +0.077, so the win requires REAL episodic evidence = genuine convergence, not
> meaning-solo relabeled. Fused one-pool loses (+0.384) and destroys the dissociation (lesion 0.134 < separated 0.178);
> the double dissociation is preserved; the lift is localised (rescues 20.5% of meaning-solo-WRONG, keeps 97.6% of RIGHT);
> equal-weight (w=1) falls below meaning-solo → reliability weighting is load-bearing.
> **Brain-fidelity:** the combination rule (product of posteriors = CA3 pattern completion + Ernst-Banks/PPC cue combination)
> is PINNED; the reliability weight `w` being CALIBRATED (not emergent — our two cue codes aren't one PPC population) is
> honestly labelled OUR-INVENTION-UNDER-TEST. The two pools stay SEPARATE (the fidelity gate I set in §7 — passed).
> **To the solver's credit:** it flagged the brief's named baseline (independent-AND 0.119) as a STRAW floor (lower than
> either system alone) and re-aimed at the true strongest floor (meaning-solo 0.700) — upholding the measurement bar better
> than my brief did. The drill shows the RULE is at ceiling (0.744 vs argmax-union oracle 0.750, NOT_SEP) and the residual is
> the dense store, with the gain rising monotonically with episodic reliability → a testable compounding prediction for p2.
> **hdlab LANDED (Q111):** `hdlab/convergent_cue_reader.py` (`convergent_pick`; ports `pick_convergent_rw` + the gold-blind
> tau calibration verbatim; DEFAULT_TAU_E/S + DEFAULT_W=12 baked = the dense-store calibration; graceful degradation into
> either single system). Witness `verification/test_convergent_cue_reader_organ.py` PASS first-hand; registered
> `convergent_cue_reader_v1` (BUILT/ISLAND, default-safe). AUDIT UPDATE folded (§2b). **Honest deflations preserved:** modest
> absolute magnitude (strict convergence on the hardest subset), WordNet-paraphrase circularity in the ABSOLUTE (identical
> across arms → the delta is clean), calibrated-not-emergent weight. NEXT: recalibrate `w` on p2's sparse store when it lands.

# PROBLEM: the composed reader combines its two validated systems (episodic entity binding + ATL conceptual meaning) by an INDEPENDENT post-hoc conjunction, but the brain retrieves by CONVERGENT-CUE pattern completion — build the convergent-cue composition (meaning cue provides top-down support to the entity read), beat the independent-AND baseline, and PRESERVE the double dissociation

**slug:** `compose_the_reader_by_convergent_cue_not_independent_conjunction` — **opened:** 2026-08-27 by the strategy session
(surfaced by the STEP-18 measurement + the STEP-19 brain-foundationality drill in `notes/CONSOLIDATION_PHASE_LOG.md`).
**status:** OPEN — a MECHANISM-DISCOVERY + BUILD problem. You build + validate in `experiments/`; strategy LANDS any
hdlab change (Q111). There is a concrete BASELINE TO BEAT and a can-fail brain-foundational hypothesis.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3`, DOWNSTREAM of p1 (`build_the_composed_scalar_magnitude_meaning_channel`)
> and p2 (`the_entity_store_is_a_dense_bundle_that_fans`) — it composes what those refine (see §2 relationship). Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the system you touch (hippocampal CLS retrieval + ATL
> semantic control); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission for any
> verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE

To answer "what did X **pursue**?" when the story said "X **chased** Y", a reader must do two things at once: know
**which character** X is (track the pronouns), and know that **pursue means chase** (recognise the paraphrase). We have
a brain-faithful organ for each — an ACT-R + Centering salience binder (episodic/entity) and an ATL conceptual channel
(meaning) — and STEP-18 just proved **both are load-bearing** in one reader (removing either collapses the score).

But STEP-18 combined them the LAZY way: it ran the two retrievals **independently** and required both to be right (a
post-hoc AND). The score came out ≈ the *product* of the two solo rates (0.70 × 0.17 ≈ 0.12), i.e. the two systems were
treated as **statistically independent**. The brain does not do this. Episodic memory retrieval is **convergent-cue
pattern completion**: the meaning of the question and the identity of the character are BOTH fed into the same
content-addressable memory at once, and the meaning cue **helps** the character read (top-down semantic support). So the
brain-faithful reader should do BETTER than the independent product — the meaning cue should **rescue** cases where the
entity read alone would have missed. **Build that convergent-cue reader and show it beats the independent-AND baseline,
without collapsing the two systems into one (which the brain's double dissociation forbids).**

## 2. WHY THIS ONE

It is the CONSOLIDATION's composition-fidelity step. STEP-17 wired the front-end; STEP-18 showed entity+meaning compose;
the STEP-19 drill found the *combination rule itself* is the remaining fidelity gap. It is measurement-surfaced, has a
hard baseline (0.119) and a can-fail brain hypothesis, and it is the READ-side counterpart of the two in-flight stores.

**RELATIONSHIP to the in-flight work (do NOT duplicate):**
- **p2 `the_entity_store_is_a_dense_bundle_that_fans`** = the WRITE/STORE side (sparse DG k-WTA + CA3 *how traces are
  held*). THIS problem = the READ side (*how two cues jointly address the store*). They COMPOSE: build convergent-cue
  read to run over whatever store is live; when p2 lands its sparse store, re-measure on it (one swap). Coordinate, don't rebuild p2.
- The already-SOLVED `content_addressable_retrieval_over_a_separated_store` was SINGLE-cue retrieval. This is MULTI-cue
  (meaning ⊗ entity) convergent retrieval with top-down facilitation — a different mechanism. Read it, build beyond it.
- p1 (scalar-magnitude meaning) refines the ADJECTIVE meaning read; here the cue is VERB meaning (conceptual_meaning) — orthogonal.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED where cited; the mechanism to replicate)

- **Complementary Learning Systems (McClelland, O'Reilly, Norman):** the hippocampus retrieves an episode by **pattern
  completion** from a PARTIAL cue — a subset of the bound features reinstates the whole conjunctive trace. Crucially the
  cue can be MULTI-MODAL: a semantic cue and an entity cue **both** partially match the stored (entity, event, meaning)
  conjunction and JOINTLY drive completion. This is ONE content-addressable read over a convergent cue, NOT two reads ANDed.
- **Top-down semantic support to episodic retrieval (predictive coding; ATL→hippocampal / semantic-control LIFG gating):**
  the meaning system biases which episodic trace completes. So a correct paraphrase recognition should FACILITATE the
  entity read, recovering ambiguous/weak-binding cases — the source of the predicted gain over the independent product.
- **The constraint that KEEPS it faithful (do NOT violate):** the two systems must stay DISSOCIABLE — the canonical
  DOUBLE DISSOCIATION (semantic dementia spares episodic binding; hippocampal amnesia spares semantics). A model that
  FUSES meaning and entity into one undifferentiated pool would score by erasing the dissociation — that is a FIDELITY
  REGRESSION, and your controls must REFUTE it (see §7). Convergent-cue ≠ fusion: separate stores, joint addressing.
- Our binding basis is FHRR (see `[[fhrr-is-the-chosen-binding-basis-do-not-replace]]`); convergent-cue completion over an
  FHRR/CLS store is compatible (this is the store-organisation lever, not a binding-algebra change).

## 4. MEASURED vs INFERRED
- **MEASURED (STEP-18, the baseline to beat):** independent-AND composition FULL **0.1190** [0.0976,0.1424] on LitBank
  paraphrased pronoun who-did-what (60 docs, n=3681); entity-solo(ACT-R) 0.167, meaning-solo 0.700; FULL ≈ their product
  (independence). ENTITY_OFF 0.034, MEANING_OFF 0.000, TWIN 0.066 — both axes load-bearing, twin losing. Harness:
  `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py`.
- **INFERRED (your hypothesis to test):** convergent-cue retrieval > 0.119 CI-sep by rescuing entity-solo MISSES via
  top-down meaning support; the gain concentrates on the entity-solo-WRONG subset. UNPROVEN — could be null (the two
  reads may be genuinely independent here), which is a legitimate PASS if the brain's mechanism was faithfully built.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The independent-AND composition (STEP-18) — that IS the baseline; do not re-derive it, beat it.
- The single-axis validations (entity STEP-13 0.184; meaning STEP-14 0.750 paraphrase) — context only, do not redo.
- Do NOT re-open p2's store-sparsity question or the solved single-cue content-addressable retrieval.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py --docs 8` — confirm the baseline reproduces.
- Read `hdlab/situation_model_accumulate.py` (the register: `make_situation_register`, `add_event`, `decode`) — the
  content-addressable store you will read by convergent cue. Read `hdlab/salience_binder.py` + `hdlab/conceptual_meaning.py`.
- Read `notes/CONSOLIDATION_PHASE_LOG.md` STEP-18 + STEP-19 (the drill) and `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## 7. THE BAR
A convergent-cue composition PASSES only with ALL of:
1. **Beats the independent-AND baseline (0.119) CI-separated** on the SAME gold/harness (paraphrased pronoun who-did-what,
   the STEP-18 items), scored identically. Recompute the baseline in-harness — no number crosses harnesses.
2. **Mechanism is convergent-cue, not fusion:** meaning + entity cues JOINTLY address ONE content-addressable read
   (pattern completion / top-down bias), NOT a re-weighted AND of two independent readouts. State the operation explicitly.
3. **The DOUBLE DISSOCIATION is PRESERVED (the fidelity gate):** a FUSED-pool control (meaning and entity in one
   undifferentiated store) must be REFUTED — either it loses to convergent-cue, or it destroys the dissociation
   (lesioning one system no longer degrades gracefully). Report the lesion-each-system test.
4. **Info-free twin LOSES:** a shuffled/irrelevant meaning cue provides NO facilitation (score falls back toward the
   independent baseline). This proves the gain is TOP-DOWN SEMANTIC support, not a free-parameter artifact.
5. **The gain is LOCALISED to the predicted subset:** show the lift concentrates on entity-solo-WRONG cases (where
   top-down support should rescue), not a uniform shift (which would suggest a scoring artifact).
A rigorous NEGATIVE (faithfully-built convergent-cue does NOT beat independence here, root-caused) is a PASS.

## 8. FILES AND ENTRY POINTS
- Baseline harness: `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py` (build your convergent-cue arm beside FULL).
- Store: `hdlab/situation_model_accumulate.py`. Organs: `hdlab/salience_binder.py`, `hdlab/conceptual_meaning.py`.
- Data: LitBank streams via `experiments/exp_litbank_entity_tracking_end_to_end_v1.py::load_cache`.
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (entity/meaning composition). Log: `notes/CONSOLIDATION_PHASE_LOG.md` STEP 18/19.

## DO NOT QUOTE / DO NOT REDO
The STEP-18 independent-AND number (0.119) is the BASELINE, not a result to reproduce as an achievement. Do not restate
the single-axis validations as your own. Strategy owns the hdlab landing — you propose the diff, you do not write `hdlab/`.
