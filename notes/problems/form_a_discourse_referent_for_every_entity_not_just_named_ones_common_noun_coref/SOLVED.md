---
problem: form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref
status: PARTIAL
bar: "PASS = a glass-box common-noun discourse-referent former (a referent for every entity + bridging + cue-based retrieval + own-NP detection; NO external LLM) such that the coref chain-F1 rises CI-separated toward the +0.43 gold-coref headroom AND at least one downstream character-bound dimension (affect experiencer-binding first) rises CI-separated, with an info-free twin LOSING and no-regress on named-entity coref. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE - a faithful common-noun referent former cannot recover the coref gap glass-box (with the named cause + number, e.g. the retrieval cue is genuinely insufficient without world knowledge), decisively beyond the six partial prototypes - is a FULL PASS."
result: "LOCATED NEGATIVE + a premise-correcting REFRAME + a small LANDABLE WIN (LitBank gold coref, 100 docs, CoNLL avg of MUC/B3/CEAFe; character-cluster population). (a) THE NEGATIVE: the naive cue-based former (ACT-R retrieval extended from pronouns to definite descriptions, reusing hdlab.graded_coref_pick) = CoNLL 0.6050 vs the reader's surface-head floor 0.6046 -> +0.0008 CI[-0.008,+0.009] NOT sep, and no glass-box variant approaches the +0.43 headroom (WordNet bridging tags only 7.8% of links; 82% of common-noun links have 2-3 competing active persons that only a situation model disambiguates). (b) THE REFRAME: forming a referent for EVERY common noun beats the proper-name-centric baseline name_only 0.3386 by +0.2660 CI-sep -- already in the reader's surface-head clustering. (c) THE LANDABLE WIN: the DEPLOYABLE recipe (head-match-gated linking + modifier-split + wide recency window + the event-centrality SITUATION gate, reusing hdlab.event_centrality_coref) = CoNLL 0.6174 -> BEATS surface_head +0.0128 CI[+0.0061,+0.0197] CI-sep (CEAFe 0.469->0.510), info-free twin LOSES (+0.258 CI-sep), no-regress on named coref (+0.0000). DOWNSTREAM affect-experiencer subpopulation (160 mentions, 64 docs): name_only 0.9008 ~ surface_head 0.9080 ~ former 0.9084 (NOT sep) -- already near-ceiling clustered, so no downstream dimension rises CI-separated; the downstream loss is label-consistency + pronoun resolution, not common-noun clustering."
floor: "Strongest floor = the reader's surface-head entity grouping: character-cluster CoNLL 0.6046 (all-non-pronoun 0.6868). Weaker floors recomputed on the same population: name_only (proper-name-centric, forms NO common-noun link) char 0.3386 / all 0.4906; singleton all 0.3511; info-free within-doc label-permuted twin char 0.3583. HEAD-MATCH CEILING: only 0.341 of gold common-noun coreference links share a head lemma; recency+head-match over-merge precision 0.611 with 91% of over-merges content-IDENTICAL."
controls: "info-free within-doc LABEL-PERMUTED twin (same cluster-size distribution, link structure destroyed -> LOSES, former-twin +0.247 CI-sep, excludes 'cluster-size prior did it'); ABLATIONS (full-accessibility former vs head-match-gated vs WordNet-person-bridge -- none beats surface_head CI-sep at the untuned window; accessibility-only HURTS all-nonpron -0.041, excludes 'we just did not build it right'); recency-window PARAMETER SWEEP W in {2,4,6,10,16} (excludes window mis-tuning: no window clears the headroom; wide-window win is modifier-splitting, +0.013); NO-REGRESS on NAMED coref (name-mention subpopulation, former-name_only delta +0.0000 -- names go through the same landed EntityAliaser, excludes 'we broke named coref'); DOWNSTREAM experiencer subpopulation (excludes 'clustering was the affect bottleneck' -- it is already near-ceiling there); name_only/singleton floors recomputed on the same population."
files_changed: "experiments/exp_commonnoun_coref_diagnostic_v1.py, experiments/exp_commonnoun_referent_linker_v1.py, experiments/exp_commonnoun_downstream_binding_v1.py, experiments/exp_commonnoun_linktype_decomposition_v1.py, experiments/exp_commonnoun_situation_gated_binder_v1.py, verification/test_commonnoun_referent_former.py, data/exp_commonnoun_coref_diagnostic_v1/metrics.json, data/exp_commonnoun_referent_linker_v1/{metrics.json,window_sweep.json}, data/exp_commonnoun_downstream_binding_v1/metrics.json, data/exp_commonnoun_linktype_decomposition_v1/metrics.json, data/exp_commonnoun_situation_gated_binder_v1/metrics.json, experiments/exp_commonnoun_scene_presence_ceiling_v1.py, data/exp_commonnoun_scene_presence_ceiling_v1/metrics.json, experiments/exp_commonnoun_prototype_signal_trace_v1.py, data/exp_commonnoun_prototype_signal_trace_v1/metrics.json, experiments/exp_commonnoun_entity_world_model_v1.py, data/exp_commonnoun_entity_world_model_v1/{metrics.json,ideal_margin_sweep.json}, notes/problems/form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref/signal_loss_decomposition_2026-09-04.md"
reverify: ".venv/Scripts/python.exe verification/test_commonnoun_referent_former.py"
---

# Common-noun discourse-referent formation: a located negative, and where the leverage actually is

The brief's premise -- that the reader forms NO discourse referent for common-noun-only entities, and a
glass-box descriptive-content former will recover the +0.43 gold-coref headroom -- is **partly wrong on
disk, and the recoverable part is a WIRING problem, not a clustering-algorithm problem.** I built the
brain's actual mechanism faithfully (content-addressable cue-based retrieval, reusing the landed
`graded_coref_pick` op), swept it, and measured it against the reader's existing clustering with proper
CoNLL coref metrics + an info-free twin + a downstream test. The faithful former does **not** beat the
reader's existing surface-head grouping CI-separated, and lifts no downstream dimension. But forming a
referent for every common noun **does** beat the proper-name-centric baseline by +0.27 CoNLL -- and the
reader **already does that**; the character-bound registers just do not consume it. This is the sanctioned
located NEGATIVE (with the named, quantified cause) plus a premise-correcting reframe.

## 0. Which brain structure, replicate or substitute? (the opening move)
PINNED: comprehension opens a DISCOURSE REFERENT for every entity at first mention (Gernsbacher 1990
Structure Building; Kamp/Heim DRT/FCS introduction) and re-identifies later mentions by CONTENT-ADDRESSABLE
CUE-BASED RETRIEVAL over the active referents (Lewis-Vasishth 2005 ACT-R; McElree direct access), gated by
the GIVENNESS hierarchy (indefinite = discourse-new; definite = link; Gundel-Hedberg-Zacharski 1993) and
ACCESSIBILITY (recency/salience; Ariel 1990; Centering, Grosz-Joshi-Weinstein 1995). A discourse referent
is a FILE CARD that ACCUMULATES features across mentions; the reader re-identifies an ENTITY, not a word.

REUSE (matching organ found, not reinvented): the substrate ALREADY implements the brain's retrieval op --
`hdlab/graded_coref_pick.graded_antecedent_pick` (the PINNED ACT-R base-level activation A = ln(sum_k
w_role * dt^-d), recency x frequency x grammatical role; landed from `coreference_is_capped_at_065...`), but
it is applied ONLY to pronouns. The E3 audit itself flags the reader's coref as RIGHT-OP-WRONG-METRIC.
So the brain-faithful move is to EXTEND that op from pronouns to definite common-noun descriptions -- with
the head lemma as one ADDITIVE cue, not a gate. I copied the ACT-R activation verbatim.

## 1. Ask whether it could succeed FIRST (the diagnostic)
`experiments/exp_commonnoun_coref_diagnostic_v1.py` (100 LitBank docs; 29,103 mentions: 9,136 pronoun /
3,915 name / 16,052 common-noun = 80.4% of non-pronoun mentions). The research mechanism-diff flagged the
HARD-FAIL risk; the disk confirms it, quantified:
- **HEAD-MATCH RECALL = 0.341.** Of common-noun mentions with a prior same-cluster non-pronoun antecedent,
  only 34% share the head lemma with the nearest one. **66% of gold common-noun coreference links do NOT
  head-match** -- 19c literary narrative re-refers by shifting epithet ("the old man" -> "the poor fellow"
  -> "her father" -> "the Squire"), which head-identity and lexical similarity cannot recover. (Poesio-Vieira's
  "head-match is the cheap high-yield case" holds for NEWS, not literary prose -- a genre effect.)
- **OVER-MERGE = content-bound.** Linking each common-noun mention to the most-recent same-head mention is
  correct only 0.611 of the time; of the over-merge errors, **91% are content-IDENTICAL** ("the man" vs a
  DIFFERENT "the man") -- 2 gender-separable, 339 modifier-separable, 3,551 identical. No surface cue
  separates them; only global discourse structure / world knowledge (which man is the current topic) does.
- **The floor is already high.** Non-pronoun coref chain-F1: name_only (no common-noun link) CoNLL 0.4906;
  **surface_head (the reader's overlay: group same-head) 0.6868** -- already the strongest glass-box floor.
- A recency-window sweep showed correct/over-merge sentence-gap distributions overlap heavily (median 2 vs
  4): windowing only trades recall for precision, it does not separate them.

Conclusion BEFORE building: descriptive-content matching is capped -- the recall barrier (0.341) and the
content-identical over-merge are both world-knowledge-bound. The build had to be the brain's actual
mechanism (accessibility retrieval), not head-match, to have any chance at the 66%.

## 2. The faithful former, built and measured
`experiments/exp_commonnoun_referent_linker_v1.py` -- incremental discourse-referent former: read
non-pronoun mentions in order; a PERSON-denoting common-noun mention (WordNet person-typing) is
re-identified by ACT-R cue-based retrieval over the active gender/number-compatible person referents within
a recency window (head lemma an additive cue, NOT a gate -> can bind "the girl" to the active female
referent 'Elizabeth', the recall lever head-identity lacks); indefinite ('a man') OPENS a new referent
(Givenness); names alias via the landed `EntityAliaser`; non-person nouns keep exact-head grouping.
Scored with proper CoNLL (MUC/B3/CEAFe), doc-level bootstrap, on the CHARACTER-cluster population (the
entities the affect/who-did-what/goals dimensions bind to).

| arm (character clusters, 100 docs) | MUC | B3 | CEAFe | CoNLL |
|---|---|---|---|---|
| name_only (proper-name-centric: NO common-noun link) | 0.339 | 0.403 | 0.274 | 0.3386 |
| **surface_head (the reader's existing grouping) = FLOOR** | 0.807 | 0.538 | 0.469 | **0.6046** |
| LINKER (full accessibility, head-lemma a bonus) | 0.790 | 0.518 | 0.508 | 0.6054 |
| LINKER + WordNet person-bridge | 0.794 | 0.529 | 0.498 | 0.6071 |
| info-free label-permuted TWIN | 0.487 | 0.325 | 0.262 | 0.3583 |

- **LOCATED NEGATIVE: LINKER - surface_head = +0.0008, CI[-0.008,+0.009], NOT separated.** The faithful
  cue-based former is CAPPED at the reader's crude surface-head grouping. On the all-non-pronoun population
  the full-accessibility variant HURTS (-0.041) -- it over-merges same-gender persons at the same rate it
  recovers name->epithet links, a net wash. WordNet lexical bridging is a wash (+0.003, not sep) and
  sense-fragile ('girl.n.01' = "young woman", not "child").
- **THE REFRAME (positive, CI-separated): surface_head - name_only = +0.2660, CI[+0.228,+0.303].** Forming a
  referent for common nouns AT ALL recovers +0.27 CoNLL over proper-name-centric -- but the reader ALREADY
  computes surface_head; the character-bound registers just do not consume common-noun clusters.
- **Info-free twin LOSES: LINKER - twin +0.2471, CI-sep** (the machinery is meaningful; the residual is not
  a cluster-size artifact).
- **Recency-window PARAMETER SWEEP** (data/.../window_sweep.json): the only positive is a head-match-gated
  variant at WIDE windows -- W=10 +0.0083, W=16 +0.0126 (CI-sep) -- driven by MODIFIER-SPLITTING ("the old
  man" != "the young man") + ACT-R chaining vs surface_head's blind transitive merge, NOT by descriptive
  bridging. +0.013 is ~5% of the +0.27 recovery and nowhere near the headroom.
- **NO-REGRESS on named coref:** name-mention subpopulation, LINKER - name_only = +0.0000 (names route
  through the same landed EntityAliaser; the former only touches common nouns).

## 3. The downstream (affect experiencer-binding) does not recover either
`experiments/exp_commonnoun_downstream_binding_v1.py` -- runs the landed affect extractor over LitBank,
maps each emotion EXPERIENCER surface to its gold coref mention, and scores coref quality on that exact
subpopulation with a REFERENT-IDENTITY metric (fixing the label-string confound in the affect study's
`coref_binding_vs_gold`, which unfairly penalized common-noun clusters whose glass-box label != gold's
longest-head label). Result (160 experiencer mentions, 64 docs): **name_only 0.9008 ~ surface_head 0.9080 ~
LINKER 0.9084** (LINKER - surface_head +0.0004, NOT sep; twin loses +0.124 CI-sep). The non-pronoun
experiencer mentions are ALREADY near-ceiling clustered -- so a better common-noun clusterer lifts NO
downstream dimension. link-recall rises name_only 0.66 -> former 0.93, but link-precision falls 1.00 ->
0.75 (over-merge), netting zero.

**This exposes a methodological correction the brief inherited:** the affect study's "+0.43 recovered by
GOLD coref" is measured against a REFERENCE built FROM gold coref labels (its all-oracle rung uses the gold
canonicalizer). So the +0.43 partly reflects LABEL-SPACE MATCH, not recoverable CLUSTERING signal -- a
glass-box clusterer with different-but-valid labels scores low even when the clustering is equally good.
The near-ceiling experiencer-subpopulation clustering confirms it: the affect loss is dominated by
label-consistency + PRONOUN-experiencer resolution (the ~10% named-pronoun slice + naming), not by failure
to CLUSTER common-noun entities.

## 3b. WHERE EXACTLY the signal is lost (the aggressive drill -- `signal_loss_decomposition_2026-09-04.md`)
`experiments/exp_commonnoun_linktype_decomposition_v1.py` categorizes every gold PERSON common-noun link
(n=1,936) by the knowledge it requires + measures accessibility-recoverability and the competing-referent
ambiguity:

| category | frac of links | accessibility recovers | mean COMPETING compatible referents |
|---|---|---|---|
| head_identical | 0.287 | 0.222 | 3.03 |
| name_antecedent ("Elizabeth"->"the girl") | 0.188 | 0.215 | 2.63 |
| wordnet_bridge ("the fellow"->"the man") | 0.078 | 0.230 | 2.21 |
| kinship_role ("her father", "the servant") | 0.219 | 0.135 | 2.86 |
| residual (deep world knowledge) | 0.229 | 0.126 | 3.02 |

Two precise findings: **(a) a buildable STATIC lexical asset (WordNet person hypernymy) tags only 7.8% of
links** -- the +0.43 headroom is NOT behind a missing lexicon (name-antecedent 18.8% + kinship 21.9% +
residual 22.9% = 63.5% are not lexical-taxonomy problems). **(b) Only 349/1,936 = 18% of person common-noun
links have a SINGLE unambiguous compatible active referent; 82% occur with 2-3 same-gender persons
simultaneously active**, so accessibility recovers just 0.13-0.23 per category. The correct referent is
fixed by WHICH entity the current SCENE is about -- the online situation model -- not by any recency,
gender, or lexical cue. This is the content-identical over-merge (91%) localized to its cause.

## 4. Performance vs the brain, and precisely where we differ (the mechanism-diff)
- THE PRECISE DIVERGENCE FROM 100% BRAIN-FOUNDATIONAL (drill 3b): the brain resolves a definite description
  by binding it to the currently-FOREGROUNDED entity of that description-type in an ONLINE SITUATION MODEL
  (Zwaan-Radvansky event-indexing; Sanford-Garrod scenario-mapping; Kintsch construction-integration),
  continuously updated by the EVENT structure (who did what to whom). The dominant retrieval cue for "the
  man"/"her father"/"the girl" is SCENE MEMBERSHIP, gated by role-relational + lexical-type compatibility.
  WE HAVE the retrieval op (ACT-R, `graded_coref_pick`) and lexical typing (WordNet/gender); WE LACK the
  online situation model that supplies the dominant cue -- so on the 82% multi-person links we retrieve by
  recency/role and pick wrong as often as right (the measured wash). The gap is NOT a missing lexicon or a
  weaker formula; it is the absence of the situation-model-gated binder -- a Phase-1 meaning-channel/
  world-model capability, a fidelity gap to BUILD across, gated on the reader having a queryable event/scene
  model. (`event_centrality_coref` is the closest existing piece -- event-bundle memory for pronoun ties --
  but it is pronoun-wired and cannot supply role-relational knowledge.)
- DETECTION/INTRODUCTION: the reader (via `referent_per_np`) already opens a referent per content-noun head
  -- introduction is NOT the gap (matches the brain's open-broad DRT step).
- RE-IDENTIFICATION: the brain retrieves the ENTITY by content-addressable cue-based retrieval over file
  cards that accumulate features + the SITUATION MODEL (who is where, doing what). We now retrieve by
  ACT-R activation (recency x frequency x role) + gender/number/modifier compatibility. **Where the brain
  still wins:** (a) the 66% non-head-match links are role-relational ("her father") and synonym epithets
  that need RELATIONAL/WORLD knowledge, not surface cues; (b) the content-identical over-merge (two "the
  man"s) is disambiguated by the brain's world-model of WHICH specific entity is meant -- our recency/role
  activation cannot cross this, and neither can lexical typing. This is the SAME world-knowledge boundary as
  the affect problem's located negative (inferred emotion) and the Phase-1 meaning-channel bottleneck.
- The reader's surface-head grouping is NOT brain-faithful (a static string merge, no file card, no
  accessibility) yet scores 0.6046 -- because on this metric the head-match-recoverable signal is what is
  available glass-box, and surface_head already captures it. The brain-faithful op ties it; it does not beat
  it, because the gains (accessibility-based name->epithet recall) and losses (accessibility over-merge)
  cancel exactly at the world-knowledge boundary.

## 4b. Can we BUILD across it? The situation-model gate, prototyped on the landed organ (measured)
"Is the gap buildable, and similar to an existing organ?" YES to both, and I measured it.
`experiments/exp_commonnoun_situation_gated_binder_v1.py` extends the LANDED `hdlab/event_centrality_coref`
(the HD Cowan-4 event-bundle memory that breaks same-gender PRONOUN ties by which entity is most CENTRAL in
recent events) from pronouns to definite common-noun descriptions -- exactly the situation-model cue the
drill named. Character clusters, 100 docs:
- surface_head 0.6046 | LINKER (ACT-R, no situation model) 0.6050 | **SITUATION (ACT-R + event-centrality
  gate) 0.6092** | twin 0.3593.
- **SITUATION beats the pure-ACT-R former CI-separated: +0.0042, CI[+0.0006,+0.0078]** -- the scene
  protagonist IS a better cue than recency; the mechanism direction is confirmed CORRECT and buildable by
  reusing the landed organ.
- SITUATION alone does not beat surface_head (+0.0046, CI includes 0), but the DEPLOYABLE recipe does:
- **BEST_deploy = head-match-gated linking + modifier-split + wide recency window (W=16) + the
  event-centrality situation gate = CoNLL 0.6174 -> BEATS surface_head +0.0128, CI[+0.0061,+0.0197]
  CI-SEPARATED** (CEAFe 0.469->0.510 = better ENTITY-level clusters: it splits over-merged same-head blobs
  and picks the scene-central antecedent for multi-person ties), info-free twin LOSES (+0.258 CI-sep),
  NO-REGRESS on named coref (+0.0000). This is a small, real, landable optimization over the reader's
  current clustering -- witnessed (`verification/test_commonnoun_referent_former.py` check 6).
- **RELATIONAL situation model PROTOTYPED** (`situation_predict(relational=True)`): the brain's
  same-relation+same-relatum rule (resolve the possessive-pronoun possessor -> key the role-referent by
  (role, possessor) so "her father"..."her father" co-refer). Built + measured: it WORKS (kinship-slice link
  recall 0.357->0.366, BEST+RELATIONAL - BEST +0.0006 CI-sep) but recovers ~1% of the kinship slice --
  NEGLIGIBLE, confirming the ceiling (most role-relational reference needs the relation established by world
  knowledge: 52% are bare roles, and possessive cases rarely recur with a resolvable possessor).
- **So BEST + RELATIONAL = +0.0134 over surface_head, and the kinship-relational + deep-residual ~45% remain**
  -- those need role-relational + world knowledge the event structure + in-text relations do not supply.
  This reproduces, with the actual organ, why the prior situation-structure-for-coref attempts (focus-stack,
  next-mention-prior) were REFUTED on this task. VERDICT: buildable, a small real CI-separated win worth
  landing, but it does NOT cross toward the +0.43 headroom; that is gated on the Phase-1 relational/world
  knowledge (a fidelity gap to build across, not a coref heuristic).

## 4c. THE IDEAL FULL SOLUTION built + the exact remaining wall (`exp_commonnoun_entity_world_model_v1.py`)
A `research` drill (19 verified sources) PINNED the proper brain mechanism: definite reference is resolved by
QUERYING an accumulated ENTITY WORLD-MODEL (a file card per entity: type, social ROLE, RELATIONS accumulated
across the text, recent-EVENT participation, presence, salience), restricted to the FOREGROUNDED set
(bonding), scored by descriptive match (resolution) -- NOT by weighting surface cues (Kintsch CI; Zwaan
event-indexing; Sanford-Garrod bonding->resolution; Morrow-Bower/Glenberg foregrounding; Heim FCS/Kamp DRT;
EntNet/EntityNLM). I BUILT the full ideal architecture = entity world-model + bonding->resolution query +
CONFIDENCE-GATED accumulation (commit high-margin, DEFER uncertain -- reusing graded_coref_pick's abstain,
Nieuwland Nref) + name anchors.

- **The MECHANISM CROSSES with correct records: ambiguous-link resolution 0.255 (surface recency) -> 0.540
  (entity world-model), union-oracle 0.615.** My earlier "capped" conclusion was premature AT THE MECHANISM
  LEVEL -- it was capped for a SURFACE-CUE resolver, not for the world-model query. The facts ARE in the
  narrative (union oracle 0.615).
- **But DEPLOYMENT hits a BOOTSTRAPPING / IDENTIFIABILITY wall.** The 0.540 uses records built from the GOLD
  clustering (the answer). Self-built records -> char-cluster CoNLL 0.6046 -> 0.6097 (+0.0051, CI incl 0;
  CEAFe 0.469->0.501 better entity boundaries, MUC -0.010). Neither 2-pass CONSOLIDATION (0.6091) nor the
  CONFIDENCE GATE (best margin 0.6102, +0.0056 CI incl 0) crosses it -- you cannot build correct-enough
  records without already resolving the reference. The brain breaks this chicken-and-egg with a PRIOR WORLD
  KNOWLEDGE (it knows a priori who "the master" is, who Elizabeth's father is) -- the external prior the
  no-LLM invariant bars, and exactly what SOTA imports from a pretrained LM.
- **GENERALIZES (held-out, ZERO fitted params -- reasoned brain-faithful priors):** disjoint even/odd halves
  both show resolution ~doubling (recency 0.24 -> world-model 0.50 / 0.58) and deployable ~+0.005 wash. The
  mechanism is register-general by construction; the specific numbers are 19c-literary (modern text has fewer
  co-present characters -> likely EASIER, untested); the bootstrap WALL is structural, not a corpus artifact.

## 5. Proposed hdlab change (Q111 -- strategy lands; solver does not write hdlab/)
The measured lever is NOT a smarter clustering algorithm for the +0.43 headroom (world-knowledge-bound). It
is (a) a small WITNESSED optimization and (b) a WIRING change:
1. **(WITNESSED, CI-separated, no-regress -- LAND THIS) The deployable common-noun referent former.** Replace
   the reader's blind transitive same-head merge with the incremental former: per-mention head-match-gated
   link (net-safe recall) with (i) MODIFIER-SPLIT ("the old man" != "the young man"), (ii) a wide recency
   window, and (iii) the EVENT-CENTRALITY SITUATION gate for >=2 head-match candidates (reuse the LANDED
   `hdlab.event_centrality_coref` HD event-memory: the scene-central antecedent wins the tie, extended from
   pronouns to definite descriptions). +0.0128 CoNLL on character clusters (CI[+0.006,+0.020]), CEAFe
   0.469->0.510, twin loses, +0.0000 named-coref regression. Body verbatim:
   `exp_commonnoun_situation_gated_binder_v1.situation_predict(headmatch_gate=True, window=16)`. Default-safe
   (net-positive on clean gold, byte-stable named coref; witness is the gate). Per no-more-default-off:
   impact-analyse the live reader and turn on if net-positive.
2. **(the reframe lever) WIRE the reader's common-noun referents into the character-bound canonicalizers.**
   The reader's entity overlay already clusters common nouns (+0.27 CoNLL over proper-name-centric), but
   `make_canonicalizer` / the affect+goal+world-state registers only NAME proper-name clusters and ABSTAIN
   on common-noun ones. Expose every common-noun cluster with a stable head-lemma label so "the man felt
   afraid" binds to the tracked man. DISK CAVEAT (measured): on the experiencer subpopulation this recovers
   little (already near-ceiling, 0.90); the residual downstream loss is pronoun-experiencer resolution +
   label-consistency -- pair this with the pronoun graded resolver, not with more common-noun clustering.

## 6. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md section 2b)
COREF / common-noun referent formation: the reader DOES form common-noun referents (surface-head grouping,
CoNLL 0.605 on character clusters, +0.27 over proper-name-centric) -- the brief's "forms NO referent for
common-noun entities" is inaccurate at the CLUSTERING level; it is accurate at the CONSUMER level (the
character-bound canonicalizers are proper-name-centric and abstain on common-noun clusters). A faithful
cue-based common-noun former (ACT-R retrieval extended from pronouns, reusing graded_coref_pick) does NOT
beat surface-head grouping glass-box (LOCATED NEGATIVE, +0.0008 CI-includes-0); the residual is
world-knowledge-bound (head-match recall 0.341; over-merge 91% content-identical). Flag: the affect study's
"+0.43 gold-coref headroom" is partly a gold-LABEL-SPACE artifact (reference built from gold coref labels).

## 7. Adjacent components (evaluated for brain-fidelity + optimization -> next problems)
- `graded_coref_pick` (PRONOUN retrieval): the brain's actual op, PINNED ACT-R activation -- high fidelity,
  landed. Extending it to definite descriptions is faithful but capped (this result).
- `event_centrality_coref` (event structure disambiguates reference): the brain uses the SITUATION MODEL to
  pick WHICH same-gender entity; it is wired for pronouns. OPPORTUNITY: it is the one lever that could touch
  the content-identical over-merge (91% of over-merges) -- but it cannot cross the 66% recall barrier.
  Brain-faithful (genuine HD event memory); a candidate next problem is event-structure-gated common-noun
  binding, though the diagnostic caps its ceiling.
- The character-bound CANONICALIZERS (affect/goal/world-state/`make_canonicalizer`): proper-name-centric
  OUR-INVENTION placeholders -- the actual wiring debt. Not brain-faithful (the brain binds to the entity
  card regardless of name). This is where the +0.27 already-computed recovery is being dropped.
- BRIDGING / role-relational reference ("her father", "the Squire"): needs the relational/world-knowledge
  meaning channel (Phase-1 bottleneck) -- the located-negative residual, shared with the affect and WSD
  located negatives.

## KEY REALIZATIONS
- **Ask whether it could succeed first.** The diagnostic (head-match recall 0.341; over-merge 91%
  content-identical) predicted the negative BEFORE any build -- 19c literary common-noun coreference is
  world-knowledge-bound, not head-match-recoverable. Poesio-Vieira's head-match dominance is a NEWS-genre
  fact; literary prose re-refers by shifting epithet.
- **The brain re-identifies the ENTITY, not the WORD.** The faithful move was to extend the landed ACT-R
  cue-based retrieval op from pronouns to definite descriptions (head lemma a bonus, not a gate) -- which
  found the matching organ instead of reinventing one, and which is the only mechanism that could recover
  name->epithet links. It ties, not beats, surface_head: the accessibility recall gain and over-merge loss
  cancel exactly at the world-knowledge boundary.
- **Audit the ruler.** The "+0.43 gold-coref headroom" is partly a gold-LABEL-SPACE artifact (the affect
  reference is built from gold coref labels), confirmed by the near-ceiling (0.90) experiencer-subpopulation
  clustering. The recoverable clustering signal is much smaller than +0.43, and the reader already has most
  of it (surface_head).
- **The lever is WIRING, not a new algorithm.** Forming a referent for every common noun recovers +0.27
  CoNLL over proper-name-centric, and the reader already computes it; the character-bound registers just do
  not consume common-noun clusters.
- **The RIGHT mechanism is an entity world-model query, and it CROSSES -- given records.** Building the proper
  brain mechanism (query an accumulated file-card model, not weight surface cues) resolves ambiguous reference
  0.255->0.540. The final wall is not the mechanism but IDENTIFIABILITY: you cannot bootstrap correct entity
  records from text alone (consolidation + confidence-gating both cap at +0.006 deployed). The brain breaks it
  with a world-knowledge PRIOR -- which is the precise, generalizable Phase-1 dependency this problem hands off.

## TLDR (plain English)
The task was: when a story calls someone "the man" or "the child" instead of by name, teach the reader to
recognise later mentions as the same person, and check that fixes the downstream understanding. I first
measured whether that is even possible from the words alone, and found it mostly is not: in these
old novels, two-thirds of the time the same person is called by DIFFERENT words each time ("the old man",
"the poor fellow", "her father"), and when the SAME words are reused they usually mean a DIFFERENT person --
so no word-matching rule can tell them apart; you need to understand the story. I then built the method the
brain actually uses (bind a description to the most recently-active compatible person, reusing machinery we
already have), and it does NOT do better than the simple word-grouping the reader already does. But there is
a useful surprise: grouping people by description AT ALL already recovers most of the available signal, and
the reader already does that internally -- it just does not pass those "unnamed people" through to the parts
that track feelings and goals. So the real fix is plumbing (let the feelings/goals trackers see the unnamed
people the reader already found), plus a small tidy-up (don't merge "the old man" with "the young man"), not
a cleverer matching algorithm. The rest genuinely needs world knowledge we have not built yet.

## QUESTIONS
None.

## NEXT STEPS FOR OPTIMIZATION (ranked; verdict-independent)
The optimization space is now fully mapped and every buildable lever measured. In priority order:

1. **LAND the deployable situation-gated former (§5.1) -- the ready, witnessed win.** Head-match-gated +
   modifier-split + wide window + the event-centrality gate (reuse `event_centrality_coref`). +0.0128 CoNLL
   over surface_head (CI-sep), CEAFe 0.469->0.510, twin loses, +0.0000 named-coref regression. Body:
   `exp_commonnoun_situation_gated_binder_v1.situation_predict(headmatch_gate=True, window=16)`. Small but
   real, generalizes (zero fitted params), no-regress. Per no-more-default-off: impact-analyse + turn on if
   net-positive on the live reader.

2. **WIRE the reader's common-noun referents into the character-bound canonicalizers (§5.2) -- the reframe
   lever.** The reader already clusters common nouns (+0.27 CoNLL over proper-name-centric) but the affect /
   goal / world-state registers only NAME proper-name clusters. Expose common-noun clusters with a stable
   head-lemma label. DISK CAVEAT: on the experiencer subpopulation this recovers little (already ~0.90);
   pair with the pronoun graded resolver, because the residual downstream loss is pronoun-experiencer +
   label-consistency, not common-noun clustering. Measure the true downstream lever before over-investing.

3. **The REAL capability = an ENTITY WORLD-MODEL resolver SEEDED BY A WORLD-KNOWLEDGE PRIOR (Phase-1).** The
   ideal architecture is BUILT and PROVEN correct (§4c: entity world-model query resolves 0.255->0.540 GIVEN
   records; generalizes). The ONLY thing blocking it is the bootstrapping wall -- you cannot accumulate
   correct entity records from the text alone (single-pass, 2-pass consolidation, and confidence-gating all
   cap at +0.006). The precise unlock is an EXTERNAL WORLD-KNOWLEDGE PRIOR to seed the records (who plausibly
   holds the "master"/"servant" role in this scenario; kinship priors) -- a static offline foundation asset
   (scenario/frame library + relational schema), NOT an inference-time LLM. FILE this as the Phase-1 program:
   "seed the entity world-model with a scenario/role + kinship KB so the built resolver realizes its 0.54
   ceiling." It lifts this problem AND the affect/WSD located negatives together (shared world-knowledge
   boundary), which is where the leverage is -- NOT another coref/presence heuristic (every one is measured
   and capped).

4. **DO NOT REDO (measured-capped, do not re-attempt as coref heuristics):** WordNet lexical bridging (tags
   7.8%); presence/locality model (~0.26 ceiling even with a gold oracle; ~5-6 co-present regardless of
   presence definition); the possessor-keyed relational binder (+0.0006); 2-pass consolidation (+0.0045);
   confidence-gated accumulation (+0.0056). All are on disk with their specific capping reason.
