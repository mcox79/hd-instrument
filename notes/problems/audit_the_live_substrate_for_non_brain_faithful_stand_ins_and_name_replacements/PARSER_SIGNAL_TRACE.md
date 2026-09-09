# PARSER SIGNAL TRACE — what every downstream consumer needs from the parser, the score it passes on, and whether it generalizes

**Solver session, 2026-09-08/09.** Companion to `CATALOG.md` (the C3 parser-cluster entry). Every number is quoted
from an on-disk `metrics.json` or `SOLVED.md` with its path + population; the spine (Part A) was re-verified first-hand.
Denominator = the LIVE `situation_reader.read()` path. **19c numbers are informational only (banned as load-bearing);
MODERN gold is the number that counts.** Populations differ across rows — do NOT cross-quote.

---

## PART A — the signals the parser EMITS, and the accuracy it passes on (the throughput ladder)

The front-end emits **four signal tiers**, each consumed downstream. The single internally-consistent source for the
first three (same population, same run) is `data/exp_frontend_chain_signal_loss_v1/metrics.json` (MODERN UD-EWT test,
n=2061 sents / 24,120 tokens) — **verified first-hand this session**:

| tier | signal | producer | ACCURACY it passes on | source |
|------|--------|----------|-----------------------|--------|
| 1 | **UPOS tags** | `pos_tagger.py` (perceptron Viterbi) | **0.9443** | frontend_chain |
| 2 | **unlabeled HEADS (attachment/UAS)** | `arc_parser.py` (batch) / `arceager_parser.py` (live) | batch **0.791** gold-POS / **0.761** pred-POS; arc-eager (live head source) **0.842** gold-POS | frontend_chain; `arceager_parser.py:8` |
| 3 | **labeled deprels (LAS)** | `arc_labeler.py` | **LAS live 0.7175** (head+label both right) | frontend_chain |
| 4 | **attachment RELIABILITY / confidence** | `graded_parser.py` (Matrix-Tree marginals) / `parse_confidence.py` (logistic) | median edge-marginal **AUC 0.825** over 29 labels; patient-arc calibrated **AUC 0.858** | `replace_the_greedy_arc_eager.../SOLVED.md`; `precision_weight.../SOLVED.md` |

**The ladder (why downstream slumps): each consumer inherits the PRODUCT of the stages it needs.**
```
UPOS 0.944  →  heads(UAS) 0.79 gold-POS / 0.76 pred-POS  →  LAS 0.72  →  and specific roles collapse:
    label acc GIVEN gold head+POS   0.9422   (the labeler alone is strong)
    label acc pred head + gold POS  0.8439   (WRONG HEADS cost the labeler ~0.10)
    label acc gold head + pred POS  0.9082   (tagger noise costs ~0.03)
    label acc LIVE (pred head+POS)  0.8210
  per-role LIVE LAS:  obj 0.819  nsubj 0.788  iobj 0.721  |  nsubj:pass 0.402  obl:agent 0.059  ← passive/oblique COLLAPSE
```
**Tier 0 — before any of this, the tagger must EMIT the verb at all.** The reader was dropping **2/3 of events**
because the tense-gated detector missed present-tense verbs: event-detection recall **0.333 → 0.954** (UD-EWT) with the
tense-agnostic UPOS fix; downstream who-did-what tuple recall 0.269 → 0.655 (`the_extraction_front_end_recovers_only_a_third.../SOLVED.md`).
This DETECTION-recall signal (a POS-tier consequence, not attachment) gates every consumer and was the single largest
front-end lever — larger than any attachment gain.

**The dominant ACCURACY loss (given the event is detected) is ATTACHMENT (heads), not tagging or labeling** — and it is
concentrated on the non-canonical roles (passive subject, by-agent, oblique). Two more measured facts about the
reliability tier (Part A tier 4):
- The **gold head is in the marginal's support 1.000** of the time (vs the greedy small-beam decode 0.40–0.49) — so the
  parser's *search* is not the failure; its *commit* is (`replace_the_greedy_arc_eager.../SOLVED.md` §3).
- **PP-attachment** specifically: locality floor 0.587 → grounded-lexicon 0.639 → vs human ~0.88 (a knowledge gap, not a
  decode gap; shuffled-prep twin collapses to 0.512). `data/exp_grow_grounding_pp_attachment_v1/metrics.json`.

---

## PART B — per consumer: the signal it needs, and the PARSE-ATTRIBUTABLE share of its residual

Ordered by how parse-bound the consumer is. "Given correct parse → X" means: with a gold/oracle parse the consumer
scores X, so the (X − live) gap is the parse-attributable residual.

| consumer | parser signal it needs | live accuracy | parse-attributable residual | source |
|----------|------------------------|---------------|-----------------------------|--------|
| **who-did-what / role assign** (`graded_role_assigner`, `predicate_argument_frontend`) | **heads + nsubj/obj labels** | patient live 0.745→0.831; agent 0.14→0.607 | **NUANCED — the head parser is NOT the lever.** gold-parse ceiling 0.961 (residual labeled "head attachment"), BUT a better HEAD parser buys only **+0.025–0.09** (arceager UAS 0.79→0.842 gives the same lift either way) — the **READOUT (voice + labeled obj/nsubj:pass slot + valency) dominates: +0.086 recoverable**; NP-head chunking recovers **+0.20** on the structural slice. On **19c the arc parse TIES gold** (residual is 100% coref/binding, 0% parse) | `improve_the_parser_verb_argument_attachment.../SOLVED.md`; `wire_the_predarg_binder_litbank.../metrics.json`; `the_who_did_what_selection_residual.../SOLVED.md` |
| **spatial** (`spatial_relational_model`, `location_register`) | **obl/nmod attachment + preposition** | reasoner 1.000 on GOLD; end-to-end 0.22–0.28 | **LOW — NOT the wall (corrected).** obl marginal AUC 0.76, but attachment is only **9.7%** of the ground-extraction loss; the wall is **construction coverage 35% + place-typing 14% + entity recognition** (containment edge-miss: 40% NEITHER endpoint extracted, only 10% both-extracted-not-linked). Reasoner near-perfect on gold → the cap is EXTRACTION coverage, not attachment | `build_the_obl_spatial_defer.../SOLVED.md`; `reason_over_the_spatial_relational_model.../SOLVED.md`; `extract_spatial_and_causal_relations.../SOLVED.md` |
| **world-state / who-has-what** (`world_state_register`) | **transfer verb + iobj(recipient)/obj(theme) + coref** | recipient-on-GIVE **0.33**, agent 0.51 | **HIGH (split).** recipient extraction (iobj LAS 0.72) + coref (81% agents are pronouns); **GOLD-coref oracle → 1.000** | `situation_model_has_no_mutable_world_state_register/SOLVED.md`; `..._coref_blind.../SOLVED.md` |
| **copular / state** (`state_register` + `robust_cop`) | **cop label + nsubj + predicate head** | qa_state 0.826 | **MODERATE.** read-back GIVEN binding **0.996** → residual is `cop`-label DETECTION recall (robust_cop lifted 0.701→0.826) | `wire_the_copular_state_qa.../SOLVED.md` |
| **goals** (`goal_register`, `goal_hierarchy_graph`) | **verb + purpose clause (advcl vs xcomp)** | WANT-explicit 0.607 | **MODERATE.** advcl/xcomp split **0.929 gold-heads → 0.72 end-to-end**; explicit slice AT oracle ceiling (0.857), **bare-purpose tail is attachment-gated** | `the_situation_model_has_no_goal_intention.../SOLVED.md`; `validate_the_ppmi_svd_means_end.../SOLVED.md` |
| **referent_per_np** (candidate/entity source) | **NP heads + POS noun-recall** | who-did-what 0.470→0.805 | **MODERATE (POS + coverage).** introduction capped at **0.9142 by POS noun-recall**; event-detect loses 3.4% to POS mistag; **127/669 clauses dropped by the parse-dependent mention builder** (the coverage cap) | `open_a_discourse_referent_for_every_np.../SOLVED.md` §2b waterfall |
| **belief / ToM** (`belief_timeline`, `perceptual_access_ledger`) | **clause + complement + perception-verb extraction** | ToM chain 0.849; live belief 0.90 | **INDIRECT.** inference is EXACT given oracle (100% of residual is extraction); location-perception extraction = **parser recall (0.75→0.92 with a better parse)** | `chain_belief_and_goal.../SOLVED.md`; `theory_of_mind_residual_is_the_observation_cue.../SOLVED.md` |
| **polarity** (`polarity_operator`) | **c-command SCOPE (deprels)** | surface 0.9318 | **INVERTED.** the parse-aware resolver (0.9091) LOSES to the surface scan until attachment improves; given a fully-repaired parse it EQUALS surface (0.9318). Parser noise is the whole gap | `represent_negation_and_quantifier_scope.../SOLVED.md` |
| **relcl / filler-gap** (`relcl_resolver`) | **(rejects the general parse)** | 0.953 | **NEGATIVE.** routed through the general arc parse → **0.198 (below the info-free twin)**; the specialised circuit that IGNORES the parser gets 0.953. The general parser is HARMFUL here | `the_relcl_parser_is_too_weak.../SOLVED.md` |
| **pronoun coref** (`event_centrality_coref` graded ACT-R) | **subject/role cue (weak)** | he/she 0.60 live / 0.775 competitive | **NOT parse.** recency dominates; residual is a missing coherence/next-mention PRIOR (Kehler-Rohde) + world knowledge | `coreference_is_capped_at_065.../SOLVED.md` |
| **common-noun coref** (`commonnoun_binder`/`typed_coref`) | **NP head lemma** | 0.49–0.57 (GUM) | **NOT parse.** on GUM the parse is gold → not the limiter; residual is the world-knowledge **type comparator** (oracle 0.749 vs live 0.567 = ~88% world knowledge) | `report_the_typed_coref.../SOLVED.md` |
| **causal** (`causal_reasoner`; `causation_typing` dormant) | **clause structure + verb-args + coref** | connective QA 0.90 | **MIXED.** connective causation IS positional/structural (0.9010, parse-light); non-connective mental causation is coref-bound (**participant coref lifts the simulator 3.29×**) | `a_force_dynamic_meaning_hub.../SOLVED.md` (§2b CONT) |
| **temporal** (`temporal_reasoner`) | **verb-EVENT detection + clause order** | implicit-order 0.566 | **NOT attachment.** the cap is event-detection (tense-agnostic UPOS) + the context-free script prior, not parse-attachment | `grow_a_broad_causal_event_order_store/SOLVED.md` |
| **bridging** (`bridging_inference`) | **NP heads + clean entities** | 0.47–0.53 | **MINOR.** extraction/salience cost only ~0.007–0.05; the dominant loss (−0.505 of ceiling) is the relatedness ESTIMATOR, not parse | `bridging_inference.../SOLVED.md` §4b ladder |

---

## PART C — DOES IT GENERALIZE? (per signal; the answer differs by tier)

Generalization is itself a signal every consumer inherits. Three distinct behaviors:

**Tier 1–3 (POS / heads / labels) — MODERN-solid, 19c-brittle, but 19c is banned as load-bearing.**
- POS 0.944 modern; on 19c the apparent drop is largely **convention** (copula-as-AUX), not error — genuine archaic
  open-class mistag is ~2.2% (`register_native_parse.../SOLVED.md`). A delexicalized register-robust parser exists but
  costs **−8 UAS in-domain** (0.842→0.762) — robustness is not free.
- Heads: arc-eager 0.842 modern; wins long-range dependencies (+0.15 at distance 6–10) but LOSES on `obl:agent`
  (−0.147) and `appos` (−0.035) vs the batch parser — **generalization across dependency TYPES is uneven**, and the
  oracle-union of both parsers is 0.854 (neither dominates).

**Tier 4 (reliability / confidence) — GENERALIZES POORLY out-of-domain. This is the sharpest generalization finding.**
- The edge-marginal reliability that reads AUC **0.825 median in-domain (UD-EWT) collapses to AUC 0.548 OOD (QA-SRL)** —
  near chance (`replace_the_greedy_arc_eager.../SOLVED.md` §4c(F)).
- Calibrated patient confidence **0.858 UD → 0.620 QA-SRL**; the parse-features-only ablation is 0.777 in-domain
  (`precision_weight.../SOLVED.md`). So the *confidence a consumer trusts to defer/weight* is itself register-bound —
  a downstream consumer that gates on parser confidence inherits an OOD-brittle gate.
- The one confidence signal that DOES hold: parse-**entropy** as a difficulty flag, Spearman(entropy, error) 0.70.

**Structural / specialized signals — GENERALIZE WELL, because they are not parser-accuracy-bound.**
- NP-head chunking: modern lift **+0.1277 > the 19c lift** — generalizes better than the register it was built on.
- The filler-gap circuit and the connective-causal positional rule generalize because they BYPASS the general parse.
- referent_per_np introduction coverage is register-INVARIANT (modern 0.983 ≈ 19c 0.978).

**Verdict on generalization:** the parser's *structure* (POS + heads + labels) generalizes to modern text at a known,
measured level and is deliberately not trusted on 19c; its *confidence/reliability* signal does NOT generalize OOD
(0.82→0.55) and is the weakest link for any consumer that gates on it; and the *structural rules built on top* generalize
best precisely because they don't depend on parser accuracy holding.

---

## PART D — SYNTHESIS: where the parser is the binding constraint (and where it is NOT)

**The parser passes on four signals (plus a tier-0 detection-recall gate). The single most-inherited loss is not one
thing — it decomposes into three levers, only one of which is "a better parser":**
1. **DETECTION recall (tier 0) — the biggest, and it is a POS/tense signal, not attachment:** the reader saw only 1/3
   of events until the tense-agnostic fix (0.333→0.954). Everything downstream is gated by whether the verb is emitted.
2. **READOUT off the existing parse — the dominant *recoverable* accuracy lever, also NOT a better parser:** on
   who-did-what, voice-remap + labeled obj/nsubj:pass slot + valency gives +0.086, and NP-head chunking +0.20, while
   swapping to a better HEAD parser gives only +0.025–0.09. The parse we already have is under-READ.
3. **Genuine HEAD attachment — the residual a better parser *would* fix — is concentrated on the non-canonical roles**
   (`obl:agent` 0.059, `nsubj:pass` 0.402 live LAS) and is NOT glass-box recoverable by selection; it needs the
   top-down loop. On 19c it is not even the wall (arc parse ties gold; the residual there is coref/binding).

Sorting the consumers by WHICH of the three levers binds them (corrected with the full spatial/causal/temporal data):
- **ATTACHMENT-bound (a better head parser + the top-down loop moves them):** who-did-what argument structure
  (the two-valid/gold-not-attached residual), goal bare-purpose (advcl attachment), polarity scope (c-command). Heads.
- **DETECTION/COVERAGE-bound (upstream tier-0/labeler recall moves them, NOT head attachment):** copular (29% loss =
  arc-labeler `cop`-recall), spatial (attachment only ~10%; the wall is construction coverage 35% + entity recognition),
  temporal (event-detection + the ungated nominal channel), world-state recipient (iobj-label recall + coref). These
  wait on whether the right token/relation is EMITTED, not on where the head attaches.
- **NOT parse-bound at all (fixing the parser will not move them):** pronoun coref (coherence prior + world knowledge),
  common-noun coref (world-knowledge type comparator), bridging (relatedness estimator), belief inference
  (observation-cue extraction — the inference is exact given oracle). Parser already at/above the achievable ceiling.
- **Parser actively HARMFUL:** filler-gap role assignment (0.198 through the general parse vs 0.953 specialised) —
  the monolithic bottom-up parse is the wrong abstraction there.

**Refined bottom line:** ATTACHMENT (the classic "parser accuracy" signal) is the binding constraint for a NARROWER
set than it first appears — mainly argument-structure/who-did-what. For the situation-model dimensions
(spatial/causal/temporal/copular) the wall is upstream DETECTION/COVERAGE (does the reader emit the event, the cop, the
place, the entity) and downstream WORLD KNOWLEDGE — not head attachment. This is why "make the head parser more accurate"
buys little across the board, and why the high-value levers are (1) detection recall, (2) fuller readout of the parse we
have, (3) the top-down loop for the genuine attachment residual, and (4) coverage/entity-recognition for the reasoners.

**This is exactly the C3 catalog finding, quantified.** The lever is NOT a better bottom-up scorer:
1. the gold head is already in the marginal support 1.000 of the time (search is not the failure);
2. the median edge-marginal AUC is 0.825 (the graded posterior is informative);
3. so the fix is **COMMIT on the globally-normalized posterior** (Matrix-Tree marginals, built + dormant) instead of the
   greedy arc-eager decode + inert logistic/defer, and **close the recurrent top-down loop (pri-1)** so a
   situation-model expectation resolves the 35% two-valid/gold-not-attached residual bottom-up scoring cannot;
4. and for the consumers where the general parse is harmful (filler-gap), keep the specialised constraint-satisfaction
   circuit rather than routing through the monolithic parser.

**The reliability tier's OOD collapse (0.82→0.55) is NOT a readout problem — DRILLED + MEASURED (2026-09-09,
`experiments/exp_parse_confidence_shape_vs_magnitude_ood_v1.py`).** I hypothesized (Hale precision) that the posterior's
SHAPE (entropy) would be register-robust where its absolute MAGNITUDE is not, so a consumer could gate on entropy
instead of the OOD-brittle logistic. It is **REFUTED at power** (QA-SRL n=8173): in-domain MAGNITUDE AUC 0.775 >
SHAPE-entropy 0.62 (the peak is the *stronger* in-domain signal, not the shape); **OOD BOTH collapse — MAGNITUDE
0.548 [0.534,0.563], SHAPE 0.536 [0.522,0.549], twin 0.502.** So the whole posterior (peak AND shape) is miscalibrated
off-register — the wall is the **frozen, register-specific parser weights**, not the readout. The brain-faithful fix is
therefore **continuous/adaptive parsing** (online Rescorla-Wagner update — the project's own "learning is online, never
frozen" invariant) **+ top-down constraints from the situation model (pri-1)** — NOT a cleverer static confidence
signal. This converges with C3 (unfreeze + close the loop) and the prior unfrozen-parser prototype. A rigorous located
negative that names the mechanism, correcting my own earlier "re-derive from the register-robust posterior" line.
