# How the brain does reference resolution -- the complete theory, all the signals, and a bottom-up BF trace of our chain

**2026-09-10, solver.** Owner: "we do NOT understand what we're working on -- understand deeply how the brain does this,
ALL the signals, then bottom-up trace where those signals are, and how BF they're handled through the entire chain."
This is the theory we had never written down (we had only been testing cues piecemeal). Two deep research drills
(hdi_research: computation+signals; representation+individuation+acquisition) + a file:line audit of the live chain
(Explore over `hdlab/`). Citations are PINNED unless marked INFERENCE/UNSETTLED.

## 0. THE ONE-PARAGRAPH REFRAME (why every cue-tweak we tried failed)
Human reference resolution is a **TWO-HALF machine**. (1) A **forward, generative half**: comprehension builds a
*situation model* by MINTING a token per referent at its INTRODUCTION -- an identity/index that is ontologically prior to
and independent of the words describing it -- and binding that token to a multidimensional **situational address**
(spatial, temporal/ordinal, episodic/event, thematic-role). From that model it continuously *predicts the next referent*
(a **prior**). (2) A **backward, retrieval half**: content-addressable cue-matching (agreement, type, recency, referring-
form) produces a **likelihood** over candidates. The referent is the **Bayesian posterior = prior x likelihood**, with
learned form-conditioned weights, competitors held in parallel with graded activation, an explicit *ambiguity* state (the
Nref signal), and a reanalysis path. **We built ONLY the backward likelihood -- recency x type -- and argmax it.** No token-
independent-of-head individuation, no situational address on the entity, no forward prior, no posterior combination, no
ambiguity state. Adding more backward cues (focus bridge, discourse-entity tracker, accessibility prior, near-identity)
could never fix a machine missing its entire forward half and its individuation substrate. **Our null results were
predicted by the theory, not evidence of a ceiling.**

## 1. THE BRAIN'S ARCHITECTURE (computational level)
- Reference is a **byproduct of building a coherent situation model**, not a standalone module (Hobbs 1979; Hagoort MUC
  2013/2016 -- retrieval=Memory feeds integration=Unification; Kuperberg & Jaeger 2016 -- comprehension = prediction over a
  hierarchical generative model; Ferreira good-enough 2002 -- resolution is graded/task-modulated, not always committed).
- The antecedent is **retrieved by direct-access content-addressable cue-matching** (McElree 2000/03 -- constant speed,
  distance-invariant; Lewis & Vasishth 2005 ACT-R activation; Jager-Engelmann-Vasishth 2017 -- similarity-based interference
  meta-analysis). This is the *mechanism* level -- the half we implemented.
- The **forward prior** is real and applied EARLY: anticipatory reference to semantic type/specific entity (Altmann & Kamide
  1999), implicit-causality next-mention bias at the verb (Garvey-Caramazza 1974; Koornneef & Van Berkum 2006), coherence-
  relation-driven next-mention (Kehler 2002; Rohde-Kehler-Elman 2006/7).
- **Reconciliation (the strategic point):** retrieved-vs-predicted is a false dichotomy -- the brain does *expectation-guided
  retrieval*: `P(referent | expr) ~ P(form/features | referent) x P(referent | context-prior)` (Kehler-Kertz-Rohde-Elman
  2008; the product structure predicts the production/interpretation asymmetry). We built only the likelihood term and
  argmax it.

## 2. THE COMPLETE SIGNAL INVENTORY (what the brain uses; weight; Bayes role)
Weight: HARD (near-filter) / STRONG (dominant soft bias, can override) / MOD / WEAK. Role: Prior (forward) / Likelihood
(form+feature match) / Filter (compatibility gate).

| # | signal | what it computes | weight | role | key evidence |
|---|---|---|---|---|---|
| A | morphosyntactic agreement (gender/number/person/animacy) | feature compatibility | HARD (defeasible) | Filter | Osterhout-Mobley 95; Arnold+00; attraction Wagers+09 |
| B | binding (Principle A/B/C) | structural licensing | HARD-ish, early | Filter | Sturt 03; intrusion Badecker-Straub 02 |
| C | recency / activation decay | temporal accessibility | WEAK-MOD | Likelihood | Lewis-Vasishth 05 |
| D | grammatical prominence / subjecthood / Centering | salience ranking (Cf/Cb) | STRONG (default prior) | Prior | Grosz-Joshi-Weinstein 95; first-mention Gernsbacher-Hargreaves 88; repeated-name Gordon+93 |
| E | grammatical-role parallelism | same-role preference | MOD | Prior | Smyth 94; Chambers-Smyth 98 |
| F | FORM of referring expression | accessibility signaled by form (pron vs def vs name) | STRONG | Likelihood P(form\|ref) | Ariel 90; Gundel+93; Almor 99; Kaiser-Trueswell 08 |
| G | information structure / topic / QUD | topical default, question constraint | STRONG | Prior | Roberts 96/12 |
| H | semantic type / selectional restriction | argument-type fit | STRONG (hard for gross clash) | Filter/Likelihood | Altmann-Kamide 99 |
| I | lexical semantics / is-a / near-synonymy / cohesion | non-morphological lexical link (bridging) | MOD(pron)/DECISIVE(def-desc) | Likelihood | Halliday-Hasan 76; Morris-Hirst 91 |
| J | coherence relations | discourse-relation next-mention | STRONG (can override role) | **Prior** | Hobbs 79; Kehler 02; Asher-Lascarides 03 |
| K | verb implicit-causality / thematic bias | causal next-mention | STRONG, EARLY | **Prior** | Garvey-Caramazza 74; Koornneef-VanBerkum 06 |
| L | situation model / event-indexing | structured salience (protagonist/scene; space/time/cause) | STRONG (structures C) | Prior | Zwaan-Radvansky 98 |
| M | prosody / punctuation | given/new, contrast, speaker shift | WEAK-MOD | Prior/Likelihood | Kaiser; (punct = text proxy) |
| N | world knowledge / plausibility | pragmatic coherence of result | STRONG-DOMINANT | Prior (over model) | Winograd schemas |
| O | segmentation / common ground / abstract (event/prop) referents | boundary resets; shared ground; discourse deixis | MOD | Prior | Clark; Zwaan-Radvansky |

Cue INTEGRATION is a weighted parallel constraint-satisfaction / probabilistic posterior (MacDonald+94; Kehler+08), NOT a
hard-filter pipeline and NOT argmax over one scalar; even "hard" cues (agreement, binding) are extreme-weight cues that LEAK
(attraction), and the weights are LEARNED and FORM-conditioned (Kaiser-Trueswell 08). DYNAMICS: incremental / Now-or-Never
(Christiansen-Chater 16); cue-specific ERP latencies (agreement LAN/P600; type N400; IC early; Nref for ambiguity); graded
parallel maintenance of competitors; commit-under-pressure with reanalysis.

## 3. THE SUBSTRATE (how entities are represented/individuated -- the arena the signals act on)
Convergent across formal semantics, perception, development, and neuroscience -- **identity is a content-free TOKEN minted
at introduction; features are PREDICATIONS of it, not its key:**
- Discourse-referent = a token/variable/file-card with an INDEX assigned at introduction; two men = two indices, both
  carrying `man(.)` (Karttunen 76; Kamp 81 DRT; Heim 82 File Change Semantics -- Novelty opens a new card, Familiarity finds
  an existing one).
- Entities are individuated by their **situational address**: space/time/causation/intentionality/protagonist (Zwaan-
  Radvansky 98 event-indexing). Perceptual homolog: object files & FINSTs individuate by **spatiotemporal trajectory, NOT
  features** -- people track 4-5 *identical* objects (Kahneman-Treisman-Gibbs 92; Pylyshyn 01). Development: infants
  individuate by space/time BEFORE kind/feature (Xu-Carey 96) -- our head-keyed merge reproduces the 10-month-old's failure.
  Neural: dentate-gyrus **pattern separation** orthogonalizes similar traces; without it CA3 **pattern-completes** (merges) --
  greedy head-merge = pattern completion with no separation (Bakker+08; Yassa-Stark 11; CLS McClelland+95).
- Humans ALSO fail to separate feature-identical entities with no distinguishing situational context -- but they **hedge and
  flag** (AmbiCoref, Yuan+23; Nref sustained negativity scaling with #candidates, Nieuwland-VanBerkum 06) where we merge
  silently. So the genuinely-ambiguous residual is a shared information limit; the rest is separable BY THE SITUATIONAL
  ADDRESS, which is not a feature of the mention.
- Wall B ("study"="project") is **referent-level, not lexical**: two descriptions predicate ONE token, licensed by situation
  coherence (Halliday-Hasan 76 -- cohesion REFLECTS the tie, does not create it; Murphy 03 -- relations computed, not stored).
  Our same-chain PMI measured the *shadow* and correctly found it structurally too thin.

## 4. THE BOTTOM-UP TRACE -- each signal through OUR live chain (file:line ground truth; BF verdict)
Live path (`situation_reader.read()`): (1) entity clustering -> `sm.entities` via `online_entity_cluster.online_cluster`
(the `commonnoun_binder` situation-gate runs first but its cluster writes are OVERWRITTEN at `situation_reader.py:4288` ->
shadowed); (2) common-noun resolution -> `sm.commonnoun_resolution` via `_resolve_commonnouns` (`:4082`); (3) pronoun coref ->
`sm.coref_acc` via `graded_antecedent_pick(TUNED_WEIGHTS)` (`graded_coref_pick.py:56`), event-centrality HD memory forced OFF
(`query_memory=False`, `event_centrality_coref.py:286`). `coreference_resolver` (Binding B + strict Centering) is DORMANT
(imported only by `goal_typing`).

| # | signal | in live chain? | how (file:line) | BF verdict |
|---|---|---|---|---|
| A | agreement gn | **LIVE** (gn hard filter) | `state_of_mind.py:152/338`; `graded_coref_pick.py:92`; cn `situation_reader.py:4142` | BF-ish (shallow); the only hard filter that fires. person/animacy filter wired but default OFF |
| B | binding A/B/C | **ABSENT** (dormant) | `coreference_resolver.py:241` run_principle_b -> goal_typing only | gap (would be near-hard) |
| C | recency/ACT-R | **LIVE, dominant** | `graded_coref_pick.py:94` A=ln(Sum w_role.dt^-d), actr weight 1.5; `salience_binder.py:74` | BF (Anderson-Schooler) -- but it is the ONLY live selective cue |
| D | prominence/Centering | **PARTIAL** -- role-prominence baked into ACT-R (SUBJECT=4.0); Cb & first-mention CODED but weight 0.0 | `graded_coref_pick.py:88` subject=0.25, `:89` cb=0.0, `:91` first=0.0 | the STRONG default-prior cue is present-but-zero-weighted -> effectively absent |
| E | role-parallelism | **DORMANT** (coded, weight 0.0) | `graded_coref_pick.py:92` par cue, parallel weight 0.0 | inert (and we measured it HURTS if turned on -- C10) |
| F | referring FORM | **LIVE** (structural) | pronoun writes salience card only; nominal-dominant scoring (`typed_coref.py:172-215`; `situation_reader.py:4166`) | BF_SPIRIT (Ariel de-pollution) -- but NOT used as a graded P(form\|ref) likelihood, only as a write-rule |
| G | topic / QUD | **ABSENT** | no QUD/topic organ in the pick | gap |
| H | semantic type / selectional | **LIVE as binary license seed** (not predicate-arg fit) | `typed_spokes.py:233` coref_type_license at `_resolve_commonnouns:4199`; SRL frontend NOT wired | BF_SPIRIT op; the live semantic signal, but binary + non-writing |
| I | is-a / near-synonymy / cohesion | **LIVE (binary license)** | `typed_spokes.py:233`; in-text is-a `situation_reader.py:4037`; C8 `:4200`; `conceptual_meaning` gloss-cosine (extra bridge) | BF_SPIRIT op; KNOWLEDGE incomplete; near-identity is learner-bound (C10) |
| J | coherence relations | **ABSENT** (organ exists, default OFF) | `coherence_reader.py:15` SDRT-lite; track_coherence default False (`situation_reader.py:931`) | the biggest STRONG-prior gap; built-but-dormant |
| K | verb implicit-causality | **ABSENT from coref** (tested-dead for binding) | `psych_verb_frames.py`/`event_type.py` -> only coherence_reader (OFF); `salience_binder.py:13` "IC does not replicate" | STRONG-prior gap; a prior null exists (see 5c) |
| L | situation model / event-index | **ORGAN EXISTS, FORCED OFF in the live pick** | `event_centrality_coref.py:158` hd_centrality tie-break, but query_memory=False; `situation_model_accumulate.py` not imported by reader | the SUBSTRATE gap (see 5b) -- present in the tree, not on the retrieval path |
| M | prosody / punctuation | **ABSENT** | none in the pick | minor gap |
| N | world knowledge / plausibility | **ABSENT from coref** | lives in coherence_reader (OFF), generalized_event_knowledge (no coref consumer) | gap (unbounded cue) |
| O | segmentation / abstract referents | **PARTIAL**: fixed-window scene segmentation live (`scene_segment`); abstract/proposition anaphora ABSENT | `situation_reader.py:1811` scene_ids=i//WINDOW | scene = crude fixed window (not event-semantic); no event/prop referents |

## 5. THE ARCHITECTURE / SUBSTRATE TRACE (S1-S8) -- where the real divergence is
| # | feature | finding (file:line) | verdict |
|---|---|---|---|
| S1 | token minted independent of head, vs head-keyed | HYBRID: entity IS a minted token (`typed_coref.py:172` TypedRef(rid); `online_entity_cluster.py:74` _File(cid)) BUT re-access is **head-lemma-keyed** (`situation_reader.py:4190` `hl in r.heads`; `online_entity_cluster.py:144`) | **THE central miss**: the token exists but retrieval keys on the HEAD -> two same-head entities cannot be held apart |
| S2 | novelty / introduction detector | PRESENT (definiteness gate `commonnoun_binder.py:94/287` indefinite->mint; open-new fallback) but live `_resolve_commonnouns` does NOT gate on definiteness (uses head-match presence) | partial -- the mint/bind decision is head-driven, not novelty-driven, on the live cn path |
| S3 | multidimensional SITUATIONAL INDEX on the entity | **ABSENT on the entity** -- it carries only `history=[(order,role)]` + gn + head/name bag (`situation_reader.py:4119`; `typed_coref.py:175`). Spatial/temporal/event registers EXIST separately (`location_register`, `temporal_order_register`, `situation_model_accumulate`) but are NOT indexed on the entity for retrieval | **THE load-bearing gap**: the individuating address the brain uses is not joined to the entity, so retrieval can't use it |
| S4 | pattern-separation / anti-interference | ABSENT (`dg_pattern_separation.py` exists, not wired); live = distractor suppress + modifier veto | gap; greedy merge = pattern completion |
| S5 | ambiguity / Nref detector | COMPUTED then DISCARDED: `graded_coref_pick.py:102` returns entropy+margin; `_graded_pool_pick` uses only `res["pick"]` (argmax) | the ambiguity signal EXISTS and is thrown away -- a cheap, high-value wire |
| S6 | graded parallel maintenance + reanalysis | single argmax commit (`event_centrality_coref.py:490`); `salience_binder.py:105` graded_write softmax exists but dormant; no reanalysis | gap |
| S7 | Bayesian posterior / weighted multi-cue vs single argmax | weighted softmax competition EXISTS (`graded_coref_pick.py:97` z-scored cues -> `graded_competition`) but default weights collapse to ACT-R-dominant (actr 1.5, subject 0.25, ALL ELSE 0) | the machinery is there; it is starved to one cue |
| S8 | forward next-mention PREDICTION | **ABSENT; tested-DEAD** for coherence next-mention (`graded_coref_pick.py:125` note: `the_reader_has_no_coherence_next_mention_prior` = rigorous negative). Forward EVENT prediction exists (`generalized_event_knowledge.predict_next_event`) but predicts event CONTENT, not the referent, no coref consumer | the whole forward half is missing; one prior form was measured null (see 5c) |

### 5a. The diagnosis -- WHY every cue-tweak failed, in one line
We have been adding backward LIKELIHOOD cues (S7 weights) to a machine that (i) RETRIEVES BY HEAD, not by token+situational
address (S1+S3), and (ii) has NO forward prior (S8) and NO posterior combination beyond ACT-R-dominant argmax. The dominant
walls are substrate walls, not cue walls: **Wall A (same-head separation)** is S1+S3 -- the discriminator lives on the
entity's situational address, which we neither store nor retrieve on, so *no mention-feature cue can ever move it* (exactly
what we measured: an exact no-op even with gold syntax). **Wall B (near-identity)** is the same substrate at the referent
level -- two descriptions of one token, licensed by situation coherence, not a lexical table (why the PMI shadow was thin).

### 5b. The load-bearing gap, named: S3 (situational index on the entity), then S1 (token-addressed retrieval)
The raw materials EXIST in the tree but are not joined to the retrieval path: scene/episode (`scene_segment`), temporal order
(`temporal_order_register`), location (`location_register`), thematic role (already in `history`), event bundles
(`situation_model_accumulate`, `event_centrality_coref.hd_centrality`). The brain-foundational build is to **make the
discourse entity a token carrying a {temporal-ordinal, episodic/scene, spatial, role} address, and retrieve/individuate on
that address** -- so two same-head entities in different scenes/events/roles get DIFFERENT addresses and stop merging. This
is the precondition for everything downstream (a forward prior has individuated candidates to rank; coherence can license a
second description of one token).

### 5c. Honest reconciliation -- "the forward prior was tested DEAD" (S8/K/J)
A prior null exists: `the_reader_has_no_coherence_next_mention_prior` measured a coherence next-mention prior as DEAD, and the
event-transition world-model was a located negative for coref (grain mismatch, C3). Two readings, and the theory favors the
second: (1) the prior genuinely doesn't transfer on GUM (common-noun-dominated; coherence/IC are largely PRONOUN phenomena);
(2) [INFERENCE, theory-backed] the prior was tested as an ADDED backward cue over a substrate with NO token individuation and
NO situation-model address -- you cannot predict "which entity next" when entities are head-keyed feature bags that have
already merged. The substrate drill is explicit: the prior ranks *among individuated candidates*; without S1+S3 there are no
properly individuated candidates to rank. **So the correct order is substrate FIRST (S3+S1), then re-test the forward prior on
top of it** -- not prior-as-a-cue over the broken substrate. This also means the earlier null is NOT a refutation of the
forward half; it is a test in the wrong architecture (flag: hypothesis-pending-VET).

### 5d. What the current SOLVED result is, in this frame
The concept-key fix + focus bridge + Heim/Loebner uniqueness bridge (cumulative 0.5818, beats the honest de-leaked floor
+0.0564 CI-sep) are all correct, brain-foundational IMPROVEMENTS TO THE BACKWARD LIKELIHOOD -- the half we have. They are
real and worth keeping. They are near the ceiling of that half; the remaining loss is the forward half + the substrate.

## 6. THE BRAIN-FOUNDATIONAL BUILD DIRECTION (implied by the trace, not yet built)
Ordered by the trace's load-bearing analysis:
1. **SUBSTRATE FIRST -- give the discourse entity a situational ADDRESS and individuate/retrieve on it (S3+S1).** Join the
   existing scene/temporal/role registers to the entity; separate same-head tokens by distinct addresses. Can-fail test
   (per the substrate drill): construct/identify same-head pairs in DISTINCT scene/event/role coordinates and show a
   token+address store keeps them apart where the feature bag merged -- on the honest de-leaked instrument, twin-controlled.
2. **WIRE THE AMBIGUITY FLAG (S5) -- it already exists (entropy/margin), it is discarded.** Make the resolver hedge/abstain on
   near-ties instead of silently argmax'ing (Nref analog). Cheap; a fidelity win and a board-visible instrument.
3. **UN-STARVE THE POSTERIOR (S7).** The weighted-softmax competition exists; the weights collapse to ACT-R. Re-fit/allow the
   structured-salience cues (D: Centering Cb/first-mention) once the substrate gives them a real address to rank over.
4. **THEN re-test the FORWARD PRIOR (S8/J/K) on the fixed substrate** -- coherence relation + implicit causality as a prior in
   the posterior, over individuated candidates. Only after 1-3; the earlier null was in the wrong architecture.
5. Reclassify Wall B off the lexical track: "second description predicates one active token when coherence licenses it,"
   gated by referent-level type compatibility, PMI only a weak tiebreaker -- feeds the learner/knowledge program.

## 7. THE SUBSTRATE BUILD -- RESULT (2026-09-10, owner: "do it, brain-foundationally, right not cheap")
Built the substrate fix (S3+S1) in `resolve_param(sep_mode=True)` + `exp_cn_situational_index_v1.py`: each discourse entity
carries a situational address {episodic scene, temporal, event/role}; greedy head-keyed merge is replaced by the CORRECT Heim
novelty/familiarity decision -- a DEFINITE re-accesses (address-SELECTS the right same-head token, never mints); an INDEFINITE
("a man"/"another man") MINTS a new same-type token unless situationally identical (Zwaan-Radvansky continuity + DG
pattern-separation vs CA3 completion). Full controls: info-free twin (scene-scramble), per-bucket, activity probe, ablation
over the address dimensions, theta/scene-window sweep. All runs 4-core-capped.

**FIRST BUILD WAS WRONG (documented, not hidden):** I initially minted on LOW continuity for ANY same-head mention -> it
fragmented single entities re-mentioned after a gap and CRASHED same-head-unambiguous 0.955->0.51. Root cause: I inverted
Heim -- a definite signals FAMILIARITY (re-access), so only an indefinite introduction is the mint/novelty signal. Fixed.

**RESULT (GUM modern TEST n=2855, vs the backward-half floor 0.5818):**
- SAFE (Heim-correct): same-head-unambiguous 0.9492 -> 0.9446 (~-9 lost); the mechanism FIRES (56 novelty mints, 413
  resolutions changed) and it DOES separate ambiguous entities: same-head-AMBIGUOUS 0.4168 -> 0.4454 best (~+17 correct).
- BUT NOT CI-SEPARATED at the board: best config (theta 0.5, scene-window 2, weights episodic+temporal) = **0.5846, d=+0.0028
  CI[-0.0013,+0.0074]** -- every one of ~20 swept configs is a small positive (+0.0007..+0.0028), NONE clears CI-separation
  (the ~+17 ambiguous gain is offset by the ~-9 unambiguous fragmentation).
- ABLATION of the address: episodic > temporal > event/role, matching the theory -- BUT the episodic/event arms are
  TWIN-EQUIVALENT (scrambling the scene costs nothing detectable). So the small gain is essentially the indefinite-NOVELTY-mint
  (a temporal "don't-merge-indefinites" effect), NOT the situational address discriminating. At available granularity (crude
  sent-window scene; gov-verb event) the situational ADDRESS does not carry CI-separable board signal.

**HONEST VERDICT -- a LOCATED result, mechanism validated, board gain sub-CI-sep:**
1. The substrate DIAGNOSIS is confirmed and the ARCHITECTURE is correct: the head-keyed merge IS the structural block, and a
   token-mint on the novelty signal DOES individuate same-head entities safely (no unambiguous destruction once Heim is right).
   This is a real, brain-foundational capability the backward matcher structurally lacked.
2. The board HEADROOM via situational individuation is SMALL and non-CI-separated, for a diagnosable reason: the residual
   same-head-ambiguous cases in GUM are largely NOT separated by a clean novelty/episodic signal at available granularity --
   they are interleaved same-context entities, i.e. the genuine INFORMATION LIMIT humans also hit (AmbiCoref/Nref). The
   mechanism helps exactly the subset that HAS a novelty signal (~56 indefinite re-introductions) and cannot help the rest.
3. The situational-ADDRESS signal (episodic/event) is twin-equivalent at the CRUDE index I wired (`sent//W` scene; gov-verb
   event). The one "right, not cheap" lever left UNTESTED is a REAL episodic index -- the SEM schema-switch event segmenter
   (`hdlab.sem_event_segmenter`, human-boundary-validated) as the scene coordinate. Deferred, NOT done, with an honest caveat:
   its own docstring reports it is WORSE on GUM paragraph structure (rho 0.48, validated on movie narrative), and the crude
   index is already twin-equivalent, so the expected board gain is small -- a named follow-on, not a hidden win.

**What is banked:** nothing new CI-separated from the substrate build (it is not a board win). The prior backward-half wins
(concept-key + focus + Heim/Loebner uniqueness = 0.5818) stand. The substrate MECHANISM (sep_mode, Heim-correct) is validated
and default-OFF (faithfulness preserved); it is the right architecture for when a real episodic index or the forward prior is
added, but on its own it is a sub-CI-sep located result on this instrument.

## 8. STEPS 2 & 3 -- RESEARCH-DIRECTED, BOTH INFORMATIVE NEGATIVES (2026-09-10)
Two follow-up research drills (hdi_research) chose the builds; both executed 4-core-capped, on the honest instrument, with
scramble-twin controls; slice-level doc-paired CIs.

**STEP 2 -- DISCOURSE PROMINENCE as the address (research picked this OVER the forward prior and OVER spatial: the forward
prior is mis-signed for full definites [Ariel/Almor: definites mark LOW accessibility] and blind to same-context ambiguity;
spatial is weakly monitored in text [Zwaan et al. 1998]).** `exp_cn_prominence_select_v1.py`: over the individuating
substrate, select among same-head tokens for a definite by a recency<->prominence blend (prominence = first-mention +
subjecthood + topic-frequency; Gernsbacher 1988 / Grosz-Joshi-Weinstein 1995 / von Heusinger). Measured on the same-head-
ambiguous slice's own population (n=595, baseline sep+recency 0.4370):
- lambda=1.0 (prominence-only): slice d=**-0.0218 CI[-0.0391,-0.0088]** -- CI-separated WORSE than recency (recency is the
  dominant selector, confirming the descriptive 0.78 vs 0.20-0.37 first-hand).
- lambda=0.5 (recency+prominence): slice d=-0.0050, and the PROMINENCE-SCRAMBLE twin is IDENTICAL (-0.0050) -> prominence is
  TWIN-EQUIVALENT; it carries NO marginal selection signal over recency.
- **Verdict: INFORMATIVE NEGATIVE.** Prominence does not separate the same-head-ambiguous residual beyond recency. With the
  earlier episodic/event twin-equivalence (S7), this is the SECOND controlled line of evidence that this slice is a genuine
  INFORMATION LIMIT (recency near-optimal; no address/prominence cue discriminates; humans also fail -- AmbiCoref/Nref). Per
  the research's own decision rule, deprioritize all further address dimensions for this slice; the ~10-15% under-determined
  floor is real.

**STEP 3 -- LEARNED NEAR-IDENTITY as a GRADED license (research: reuse the is-a organ's functional-similarity space + a
coordinate-relatedness READ = symmetric functional-overlap MINUS is-a subsumption, x an online MINERVA coref-echo; NOT a flat
lexical table).** `exp_cn_nearid_graded_v1.py` (learned from GUM TRAIN even docs; TEST odd; no leak): measured on the
different-head residual (n=899, floor 0.1991):
- +nearid tau=0.20: diff d=**-0.0044 CI[-0.0093,-0.0010]** (slightly HURTS); board -0.0014.
- SCRAMBLE-twin (permute the learned vocabulary): diff d=**+0.0011** -- the twin is NOT worse than the real license (it is
  marginally better, within noise). **The primary gate FAILS: the real learned pairs carry no net-positive bridge signal.**
- **Verdict: INFORMATIVE NEGATIVE.** A learned functional-overlap near-identity, fed as a bridge license, is not net-positive
  on the residual: the over-bridge cost cancels/exceeds the correct binds, and scrambling the pairs does not hurt. This
  confirms the theory -- near-identity is REFERENT-LEVEL (two descriptions of one token, licensed by situation coherence) +
  noise-bounded (Recasens: near-identity is the inter-annotator-disagreement zone), NOT recoverable as a lexical/functional
  bridge license at this corpus scale. Its real home is the generative/coherence + learner program, not a coref license.

**JOINT CONCLUSION (three controlled measurements this session, plus C8/C10 earlier):** the coref board's remaining residual is
now triangulated as dominated by (i) genuine SAME-CONTEXT ambiguity for same-head (an information limit humans share -- no
address/prominence/cue separates it beyond recency), and (ii) REFERENT-LEVEL/coherence-bound + annotation-noise near-identity
for different-head (not a lexical license). Neither is addressable by more coref mechanism/cues on this instrument. The
validated architecture (backward likelihood + Heim individuation substrate) stands; the genuine remaining levers are the
GENERATIVE world-model (coherence at read time) and the LEARNER (near-identity acquired online for the generative program) --
both LARGE, separate programs with honest small expected coref payoff. The disciplined call: stop iterating coref cues/address
on this board; the residual is understood.

## 9. PROBE 1 -- the GOLD-SEPARATION ORACLE CEILING CORRECTS the "information limit" claim (2026-09-10)
Adversarial research (hdi_research) flagged two uncontrolled confounds in the "information limit" verdict (genre-pooling +
per-mention instrument) and named the decisive probe: a per-genre gold-separation ORACLE ceiling on the same-head-ambiguous
slice (`exp_cn_oracle_ceiling_probe_v1.py`, 4-core-capped). Result (n_amb=595, 137 docs):

| genre | ACHIEVED | ORACLE (perfect separation + recency) | HEADROOM | same-head pair-acc |
|---|---|---|---|---|
| NARRATIVE | 0.329 | 0.882 | +0.553 CI[+0.45,+0.66] SEP | 0.72 |
| DIALOGUE | 0.393 | 0.775 | +0.382 CI[+0.18,+0.56] SEP | 0.54 |
| EXPOSITORY | 0.455 | 0.808 | +0.354 CI[+0.17,+0.56] SEP | 0.51 |
| ALL | 0.417 | 0.780 | **+0.363 CI[+0.28,+0.46] SEP** | 0.53 |

**CORRECTION TO C9/C10/§8's "information limit" read (own it):** the same-head-ambiguous slice is NOT unresolvable. If entities
were separated, plain RECENCY resolves them at ~0.78 pooled / 0.88 narrative -- vs 0.42 achieved. The +0.36 slice prize
(~+0.075 board) is CI-separated in EVERY genre. The limit is on the SEPARATION SIGNAL (the partition), NOT on resolvability;
the resolver's same-head pair-discrimination is near-chance (0.53). So the earlier "stop, information limit" lean was wrong in
its MAGNITUDE claim: there is a large, measured prize behind entity separation.
- The prize is CROSS-GENRE (largest in narrative +0.55, but +0.35 in expository/dialogue too) -> NOT a genre-dilution
  artifact to be captured by genre-targeting; a GENERAL separation gap, largest where protagonist structure is strongest.
- The prize is an ORACLE ceiling -- "perfect separation" IS solving same-head coref. Our achievable separation signals
  (novelty-mint, address, prominence) captured only ~+0.03 of the +0.36. The gap = the value of a REAL separation mechanism.

**REVISED DIRECTION VERDICT:** the entity-grain GENERATIVE SITUATION MODEL (token minting + strong individuation + forward
prior) -- which is exactly the separation mechanism -- is now justified by a measured COREF prize (~+0.075 board potential),
not only by downstream comprehension. Build it (right, not easy = a strong individuation signal + the forward prior, not the
exhausted cues). Honest caveats: (a) achievable fraction of the +0.36 is unknown (simple signals captured little; the bet is
the full model captures materially more); (b) NO gold coherence-relation layer to validate the forward-prior half -- the one
instrument gap; (c) large integration + one genuinely-new component (entity-grain forward referent-prediction). The probe was
the right call: it flipped a load-bearing conclusion.

## 10. BUILD BLUEPRINT + CRITICAL-PATH CALL (2026-09-10, owner authorized the build)
Research mapped the build (hdi_research). DURABLE STRATEGIC CALL (do not re-litigate): the +0.36 oracle prize (§9) was
measured with the oracle resolver = plain RECENCY, so **the prize is captured by ENTITY SEPARATION ALONE. The individuation
substrate is the CRITICAL PATH; the forward prior is a SECOND, gated, off-critical-path phase** (it can only add above the
0.78 recency-oracle ceiling -- narrative-bounded, instrument-gap-blocked, once-tested-null). Do NOT build all 22 components
for a prize that ~7 capture. Build order: leaves (L1 scene-vector, L2 SEM episodic index, L3 DG pattern-separation, L4 recency,
L5 role, L6 Heim mint, L7 ambiguity flag) -> Aggregate 1 (individuation substrate) -> [gated] Aggregate 2 (forward prior) ->
Aggregate 3 (posterior+ambiguity) -> final assembly into read(). Each component isolation-authenticated (can-fail + info-free
twin) before wiring; each aggregate gated (beat floor + twin loses + no-regress + per-genre convergent validity, largest in
narrative). **DECISIVE FIRST GATE = Phase 0a:** does the REAL SEM episodic index (`hdlab.sem_event_segmenter`) carry same-head
separation signal (pair-discrimination > 0.53 CI-sep, scene-scramble twin loses, per genre) where the crude sent-window index
was TWIN-EQUIVALENT (§7)? If it too is twin-equivalent -> the prize is not capturable with our computable coordinates -> a hard
located negative (the info exists per the oracle but not where we can read it). sigma2 MUST match scene magnitude (SEM silently
stops switching on mismatch). Full blueprint in the hdi_research return (this session).

## 11. PHASE 0a GATE -- the coordinate-based individuation substrate CANNOT capture the prize (2026-09-10, build stop)
Executed the blueprint's decisive first gate (`exp_cn_sem_episodic_pairdisc_v1.py` proxy + `exp_cn_sem_wired_v1.py` authentic).
The REAL SEM episodic schema-id (`hdlab.sem_event_segmenter`, human-validated), and a STRONGER finer-sigma2 variant, wired as
the resolver's episodic address on the same-head-ambiguous slice (n=595), per genre:

| genre | floor | crude(sent//W) | SEM | SEM-fine | twin(random) |
|---|---|---|---|---|---|
| NARRATIVE | 0.329 | 0.355 | 0.329 | 0.329 | 0.368 |
| DIALOGUE | 0.393 | 0.438 | 0.404 | 0.416 | 0.483 |
| EXPOSITORY | 0.455 | 0.480 | 0.460 | 0.460 | 0.510 |
| ALL | 0.417 | 0.437 | 0.417 | 0.422 | 0.457 |

**SEM ≡ floor (does nothing) and is BELOW crude and BELOW the random twin, in EVERY genre incl narrative; the finer-sigma2
stronger version also fails.** Pair-proxy corroborates: SEM separated only 34.5% of gold-different same-head pairs (SEP=0.345)
-- most sit in the SAME SEM episode. **Root cause = GRAIN MISMATCH:** SEM segments EVENTS/scenes, but two same-type entities
in one scene share the event -> event boundaries cannot separate them; across scenes recency already separates. So the
episodic/event coordinate carries NO same-head separation signal. Triangulated with sec7 (crude episodic twin-equivalent),
the prominence null (sec8), and this (real+fine SEM). DG pattern-separation (L3) cannot rescue it -- it orthogonalizes an
address that does not differ for same-scene different entities.

**BUILD STOP + the synthesis (both prior reads reconciled):** the sec9 oracle prize (+0.36) is REAL, but Phase 0a proves the
separating information is NOT in any COMPUTABLE situational coordinate we have (episodic real/fine, temporal, role, prominence;
spatial unavailable + low-prior). The oracle achieves it with GOLD coref = COMPREHENSION ("which specific entity, from
understanding the text"), not a coordinate. **=> Do NOT build the coordinate-based individuation substrate (Phases 1-4) for
coref: its critical component (the episodic address) provably cannot capture the prize.** The prize is reachable only by the
full GENERATIVE COMPREHENSION world-model (which entity is meant), justified by comprehension breadth with coref as a
DOWNSTREAM beneficiary -- not a coref-specific build. Phase 0a did its fail-fast job: it stopped the large build on a
coordinate that cannot carry the signal. Cells: `exp_cn_sem_episodic_pairdisc_v1.py`, `exp_cn_sem_wired_v1.py` (resolve_param
gained a default-off `scene_map` injection; faithfulness unaffected).

## 12. BUILT THE PER-ENTITY SITUATION MODEL RIGHT (research-prescribed) -- EARNED located negative (2026-09-10)
Owner: "research the absolutely correct way, then do it right not easy." Definitive-method research (hdi_research) corrected a
DESIGN-LEVEL error in sec11: the individuator must be PER-ENTITY (each referent accumulates its own bound situational
signature; mint iff no active signature matches -- Heim file-change / object-files / dentate pattern-separation), NOT per-scene
(two same-type entities in one scene SHARE the scene, so a per-scene vector cannot separate them by construction -- that was
the sec11 error). And the 12-d filler was a two-order-of-magnitude VSA CAPACITY floor (role atoms in 12-d have ~0.29 cosine ->
roles inert). Built bottom-up on the authenticated substrate, each component isolation-tested:
- **D-1 FILLER** = JL random projection (D=2048) of the grounded meaning vector: graded similarity preserved (cos dog/cat 0.93,
  man/woman 0.92, man/rock 0.52; JL-corr 0.99+). PASS. (`exp_cn_vsa_capacity_gate_v1.py`)
- **D-2 ROLE-BINDING load-bearing** (FHRR circular convolution, hdlab.binding): unbind-recovery 0.96->1.00 at D 512->2048,
  scramble 0.001 (chance 0.0004). PASS at D>=512 -- the research's ~512-2048 floor confirmed; the 12-d failure explained+fixed.
- **D-3 HANDLE**: fresh random atoms orthogonal (0.03), reuse identical (1.0). PASS.
- **D-4 INTEGRATION (the decisive gate)** (`exp_cn_entity_signature_v1.py`, n_same=1554/n_diff=1157): does the per-entity
  situational signature separate same-head DIFFERENT entities? **situational content (handle-lesioned) AUC=0.539 ~ chance;
  SCRAMBLE twin AUC=0.539 IDENTICAL -> the situational STRUCTURE carries NO separation signal** (even with gold co-participant
  identity fed in). Only the gold-keyed random HANDLE separates (AUC 0.966) -- circular (assigned from the answer; not an
  achievable online signal, since online you can only mint the right handle AFTER separating, which needs the signature to
  differ -- and it doesn't).

**EARNED VERDICT (fair-test + brain-exact BOTH pass, the discipline's bar):** the representation is CORRECT and AUTHENTICATED
(D-1/D-2/D-3 pass at D=2048; the sec7/sec11 non-BF-input confounds are removed), and on that correct substrate the situational
per-entity signature does NOT separate same-head entities (D-4 AUC 0.539 = scramble = chance). So the sec9 +0.36 oracle prize
is REAL but NOT capturable by ANY situational-binding representation, however brain-foundational -- separating two same-type
entities is a COMPREHENSION act (which specific referent, from the whole text + world knowledge), which the gold handle only
stands in for by using the answer. This is the AmbiCoref/Nref information limit, now proven at the representation-correct level
with scramble + handle-lesion controls -- an EARNED located negative, unlike the sec11 premature stop. The entity-grain
situation model built FOR coref does not pay; the prize belongs to the full comprehension/world-model program (coref a
downstream witness). Robustness: the predication (role-filler) binding was scramble-invariant-null, so richer (fused
distributional) fillers cannot rescue D-4 -- the non-distinctiveness is in the entity's situational PARTICIPATION (roles not
conserved across mentions; co-participants/positions overlap), not the filler quality. Cells: exp_cn_vsa_capacity_gate_v1.py,
exp_cn_entity_signature_v1.py (+ resolve_param scene_map injection, default-off).

## 13. BOTH comprehension signals tested on the correct substrate -- EXHAUSTIVE earned ceiling (2026-09-10)
After D-4 (situational signature null), tested the other comprehension signal the oracle used -- each entity's DESCRIPTIVE
IDENTITY (accumulated modifiers + appositive/copular type-refinements; Kintsch entity semantics), on the same authenticated
D=2048 FHRR substrate (`exp_cn_descriptive_identity_v1.py`, n=1175 same-head-ambiguous pairs):
- **DISTINGUISHABILITY ORACLE: only 44.5% of pairs are descriptively DISTINCT; 55.5% are descriptively IDENTICAL** (both bare
  "the man", no distinguishing modifier) -> genuinely IRREDUCIBLE (AmbiCoref/Nref human-parity tail).
- **DESCRIPTIVE signature does NOT beat scramble even on the distinguishable slice: real AUC 0.588 vs scramble 0.606** (ALL
  0.569, all-scramble 0.539). An entity's own mentions describe it INCONSISTENTLY (one "tall man", next bare "man"), so
  same-entity signatures cohere no better than random -> the signature cannot use the descriptive difference.

**EXHAUSTIVE EARNED CEILING (fair-test + brain-exact BOTH pass; representation authenticated D-1/D-2/D-3; both candidate
comprehension signals tested with scramble controls):** on the correct high-dim FHRR representation, NEITHER text-extractable
per-entity signal separates same-head entities better than scramble -- SITUATIONAL participation (roles/co-participants/
position: AUC 0.539=chance=scramble, sec12) NOR DESCRIPTIVE identity (modifiers/appositions: 0.588~scramble, 55% identical).
The only separator is the gold-keyed random handle (0.966, circular). So the sec9 +0.36 prize is NOT capturable by any
per-entity textual signature: separation requires the ANSWER (world-knowledge/inference about the specific referent, or is
irreducibly undetermined for the 55% descriptively-identical majority). The coref separation lever is EXHAUSTED for
text-extractable signals; the residual is (a) 55% irreducible (human parity) + (b) a world-knowledge/inference remainder that
belongs to the comprehension/world-model program, NOT a coref-extractable signature. Banked: the correct, reusable D=2048 FHRR
substrate (filler=JL-projected meaning, role-binding, handle) as validated default-off components. Coref deliverable stays the
backward-half wins (0.5818). Cells: exp_cn_descriptive_identity_v1.py.

## TLDR (plain English)
We finally wrote down how the brain actually does this, and it explains why nothing we tried worked. The brain uses two
halves: it gives every new thing a blank name-tag the instant it's first mentioned and stamps it with where/when/which-scene
it appeared, and it constantly guesses who the next sentence is about. Only THEN does it do the backward "which earlier thing
matches?" step we built. We built just that last step, and only its two weakest clues (how recently something was mentioned,
and rough type), and we file everything under the describing word -- so two different things called "the man" get filed
together and can never be pulled apart, and "the study"/"the project" can never be linked. That's not a tuning problem; the
machine is missing its front half and its filing system. The good news: the parts we need (scene/time/role stamps, an
"I'm not sure which one" signal, the multi-clue combiner) already exist in our codebase -- they're just not connected to the
part that looks things up. The fix is to connect the filing system first (tag each thing by where/when/which-scene, not by
its word), then the rest can finally work. The small wins we already have are real and worth keeping -- they're improvements
to the backward half; they're just near the ceiling of that half.

## QUESTIONS
None -- the theory + trace are decisive on direction. Two items flagged hypothesis-pending-VET: (a) whether the forward-prior
null re-tests positive on a fixed substrate (5c); (b) whether GUM's genre mix carries enough scene/event structure for the
situational address to separate same-head entities in practice (6.1's can-fail test settles it).

## NEXT STEPS
1. This document is the shared theory (was never written down). Fold its signal table + trace into the substrate's coref
   audit; treat "no mention-feature cue separates same-head entities" as a DURABLE negative WITH mechanism (the discriminator
   is the entity's situational address), not a ceiling.
2. Build direction is section 6, substrate-first (S3+S1), can-fail on the honest de-leaked instrument, twin-controlled.
   Recommend confirming this re-scoping before the build (it is an architecture change, not a cue).
3. Keep the banked backward-half wins (concept key + focus bridge + uniqueness bridge, 0.5818); they are correct and near the
   ceiling of the half we have.

### Sources
Hobbs 1979; Kehler 2002; Kehler-Kertz-Rohde-Elman 2008; Kuperberg-Jaeger 2016; Hagoort 2013/16; Ferreira+02; McElree 2000/03;
Lewis-Vasishth 2005; Jager-Engelmann-Vasishth 2017; Altmann-Kamide 1999; Garvey-Caramazza 1974; Koornneef-VanBerkum 2006;
Rohde-Kehler-Elman 2006/7; Grosz-Joshi-Weinstein 1995; Gernsbacher-Hargreaves 1988; Gordon+1993; Smyth 1994; Chambers-Smyth
1998; Ariel 1990; Gundel-Hedberg-Zacharski 1993; Almor 1999; Kaiser-Trueswell 2008; Roberts 1996/2012; Halliday-Hasan 1976;
Morris-Hirst 1991; Asher-Lascarides 2003; Zwaan-Radvansky 1998; Christiansen-Chater 2016; Karttunen 1976; Kamp 1981; Heim
1982; Johnson-Laird 1983; Kahneman-Treisman-Gibbs 1992; Pylyshyn 2001; Treisman 1996; Spelke 1990; Xu-Carey 1996; Bakker+2008;
Yassa-Stark 2011; McClelland-McNaughton-O'Reilly 1995; Nieuwland-VanBerkum 2006; Yuan+2023 (AmbiCoref); Markman-Wachtel 1988;
Murphy 2003; Cruse 1986.
