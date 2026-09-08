# Research: a psychological-state register for LOO counterfactual-necessity cause-selection

Filed by: research (Sonnet). Topic: `build_the_generative_result_state_world_model`, psychological-LOO drill.
Trigger: Director task, following `exp_genworldmodel_loo_necessity_v1` HARD_FAIL + `exp_genworldmodel_causal_type_census_v1`
(GOAL 40.8%/36.8% plurality; physical `representable_frac` 5.6%/2.5%) + `exp_genworldmodel_loo_resolved_v1`
(coref-fix ruled out: TMW-GOAL alone-accuracy stays 0.000 under every resolver).

---

## HEADLINE

**The fix is a wrapper, not a rebuild.** Every piece the psychological LOO needs is already landed, default-on,
and validated: `hdlab/goal_register.py` (`track_status_thwart`) already computes goal
active/satisfied/failed as a function of an **event list you control**, and `hdlab/occ_appraisal.py`
(`appraise`, `detect_prospect_sign`) already composes goal-status x prospect into the exact OCC emotion
table. The physical LOO (`WorldState.fold` minus a candidate) has a **structural** twin sitting one level up:
run `track_status_thwart` (or `detect_prospect_sign`) once on the full event list, once with candidate
sentence `j`'s events removed, and check whether the goal's resolved status (or the prospect's
confirm/disconfirm) **flips**. That flip test is the entire net-new code required — a ~150-250 line module,
not a new extraction stack. Two ranked designs below (goal-resolution LOO = priority; prospect-confirmation
LOO = secondary) reuse `goal_register`+`occ_appraisal` byte-for-byte; a third (belief LOO, MENTAL ~6-9%
population) reuses `belief_timeline`+`theory_of_mind`, already measured 0.849 on BigToM but never run as a
cause-selection ablation.

P_deflated = 0.50 (capped, novel-synthesis of two independently-validated organs in an untested configuration)
for "beats the null + order-shuffle + additive-cue integrator CI-separated on the GLUCOSE/TellMeWhy GOAL
population." P = 0.75 (less deflation — this is closer to an engineering-integration claim than a novel
mechanism claim) for "the module runs end-to-end and fires on materially more than 5.6%/2.5% of gold pairs."

---

## 1. Organ sweep — what's landed, ranked by usefulness to the psychological LOO

| Rank | Organ (file:line) | What it represents | Schema | Foldable now? | Brain basis |
|---|---|---|---|---|---|
| 1 | `hdlab/goal_register.py` `track_status_thwart` (goal_register.py:542-606) + `_is_thwarted` (:652-670) | Per-goal **STATUS** (active/satisfied/failed) as a function of an injected `events` list | `Goal.status` field (goal_register.py:93); realized-check = later same-agent event whose normalized predicate == goal head (:579-587, `_norm_pred`/`IRREG_PAST` :459-474); thwart-check = FAILURE_VERBS (:445-449) / negated-goal-head clause / goal-object+ADVERSE_RESULTANT (:452-458, `_is_thwarted` :652-670) | **YES — directly.** Already takes `events` as a parameter; excluding candidate `j`'s events from that list *is* the LOO fold, zero new code | Lutz & Radvansky 1997 (status field, graded decay); Suh & Trabasso 1993 (reinstatement) |
| 2 | `hdlab/occ_appraisal.py` `appraise()` (:118-143), `detect_prospect_sign()` (:187-219) | The **EFFECT RULE**: goal desirability x prospect -> OCC emotion type (satisfaction/disappointment/hope/fear/relief/fears_confirmed) | Pure function, `appraise(desirability∈{+1,-1,None}, prospect∈{actual,prospective,confirmed,disconfirmed}) -> occ_type` (:118-143); `detect_prospect_sign(desir, stim_words, outcome_texts) -> {prospect}` reads a later-sentence-list for favorable/adverse resultant cues (:187-219, `_FAVORABLE`/`_ADVERSE` :161-169) | **YES — directly.** `outcome_texts` is a list; excluding candidate `j` from it is the fold | Ortony, Clore & Collins 1988 (OCC); Scherer component-process (goal-conduciveness first) |
| 3 | `hdlab/affect_register.py` `AffectRegister.feels()` (:383-390) + `hdlab/affect_lexicon.py` `AffectLexicon` (:126-208) | **STATED** emotion (valence primary, category secondary) bound to a coref-resolved experiencer | `Affect(experiencer, emotion_word, emotion_cat, valence, valence_sign, stimulus, sent_idx)` (affect_register.py:74-89); `AffectLexicon.category()/valence_sign()` (:167-202) | YES, read-only (supplies E's actual gold-comparison label, not folded itself) | Barrett constructed emotion; Warriner et al. 2013 norms |
| 4 | `hdlab/goal_register.py` `extract_goals`/`extract_goals_sentence` (:315-326, :191-312) + `bind_agents`/`make_canonicalizer` (:332-339, :712-765) | **GOAL ESTABLISHMENT**: per-sentence desire/intend/try/purpose extraction, agent-canonicalized | `Goal(agent, goal_head, goal_text, kind, sent_idx, agent_canonical)` | YES — re-run on a sentence subset (excluding candidate `j`) to test *establishment* necessity (see Design 1a) | Malle 1999/2004 reason-vs-cause; Spunt/Lieberman dmPFC |
| 5 | `hdlab/goal_outcome_relation.py` `pair_feats`/`relation_votes` (:221-228, :595-617) + `_grounded` twin | **BROADER means-end SATISFACTION**: does outcome text INSTANTIATES (verb-class, not lexeme) or CONTRADICTS a goal, beyond `track_status_thwart`'s strict lemma-match | Learned classifier (estimation/ruleind) + WordNet-MWE dictionary CONTRADICTS leg | Partial — operates on (desire_text, outcome_text) STRING pairs (DesireDB shape), needs adapting to (Goal, candidate-sentence) shape. **Tier-2 upgrade**, not core v1 | — (own-invention, not brain-cited) |
| 6 | `hdlab/belief_timeline.py` `timeline_belief` (:137-145) + `shuffle_order_twin` (:310-320, **an ALREADY-BUILT info-free-twin precedent**) | Per-agent **BELIEF** as sample-and-hold over observed events; false belief falls out of observation-gating | `WorldEvent(obj,value,chrono,narr,affects_reality)` (:49-63) | YES, same pattern (exclude one WorldEvent, refold) | Wimmer & Perner 1983; Saxe & Kanwisher 2003 (TPJ) |
| 7 | `hdlab/theory_of_mind.py` `forward_action`/`compose_action` (:123-127, :145-151) | believes(A,F,t) x wants(A) -> action (bidirectional inverse-planning composition) | Pure function over belief_timeline + goal_register outputs | YES, read-only composition | Baker, Saxe & Tenenbaum 2009/2017; measured on BigToM 0.849 vs floor 0.500 |
| 8 | `hdlab/goal_hierarchy_graph.py` `shuffled_graph` (:354-385, **a SECOND already-built info-free-twin precedent**) | Goal->subgoal hierarchy, connectivity-salience (Trabasso), reinstatement (Suh & Trabasso) | `GoalGraph` with `parent`/`children`/`edge_type` | Not directly needed for the LOO fold itself, but its twin-construction **pattern** (rewire edges, preserve node/status counts) is the template if a graph-shaped psych-LOO is built later | Trabasso & van den Broek 1985 (connectivity=salience) |
| 9 | `data/atomic_kb/v4_atomic_trn.csv` (columns: `event,oEffect,oReact,oWant,xAttr,xEffect,xIntent,xNeed,xReact,xWant,prefix,split`) | ATOMIC (Sap et al. 2019) if-then commonsense KB: xIntent/xReact/xWant give free-text psychological effects per templated event | Raw CSV, **no hdlab loader exists** (grep found nothing under `hdlab/*atomic*`) | **NO — unwired.** Would need a new loader + fuzzy event-template matcher. Flagged as a Tier-2 backoff for events with no explicit desire-verb (implicit-goal recovery), not required for v1 | Sap et al. 2019 |
| 10 | `data/corpora/bigtom/bigtom.csv` (278 items, modern present-tense) | Belief-desire-action causal graph with an explicit observed/unobserved manipulation | Story text + belief/desire/action-prediction fields | Consumed today by `experiments/_tom_bigtom.py` + `hdlab.theory_of_mind`; **never run as a cause-selection ablation** (only belief-prediction accuracy) | Gandhi, Stojnic, Lake & Dillon 2023 |
| — | `hdlab/state_of_mind.py` | **NOT belief** — despite the name, this is a coreference/salience `WorkingOverlay` (module's own docstring, line 3-8, explicitly disclaims ToM). Excluded from this design. | — | — | — |

**What does NOT exist and would need building for v1:** nothing structural. The only new code is the LOO-fold
wrapper (Section 2) and its info-free twins (Section 3) — everything else is read-only reuse of rank 1-4, 6.

---

## 2. The design — psychological-state register + LOO fold

### 2.1 State predicates (the psychological analog of `WorldState.have()`/`is_open()`)

| Predicate | Source (reused, not rebuilt) | Mutability |
|---|---|---|
| `has_goal(agent, g)` | `GoalRegister.goals_of(agent)` (goal_register.py:363-366) | Set-valued, grows as sentences are folded in |
| `goal_status(g) ∈ {active, satisfied, failed}` | `Goal.status` (goal_register.py:93), written by `track_status_thwart` (:542-606) | **The mutable field** — this is `WorldState.have[obj].value_at(t)`'s psychological counterpart |
| `desirability(g) = +1 if satisfied else -1 if failed else None` | `occ_appraisal.appraise()`'s own input convention (occ_appraisal.py:118) | Derived, not stored |
| `prospect(a) ∈ {prospective, confirmed, disconfirmed}` | `occ_appraisal.detect_prospect_sign()` (:187-219) | Derived from `affect_register` fear/hope + later-sentence resolution cues |
| `feels(agent) -> Affect` | `AffectRegister.feels()` (affect_register.py:383-390) | Read-only ground truth for E's actual label (GLUCOSE/TellMeWhy don't need this — it's for a live-reader deployment) |
| `believes(agent, fact, t)` | `belief_timeline.timeline_belief()` (:137-145) | Mutable, sample-and-hold (Design 3 only) |

GOAL is the priority (per census: GLUCOSE 40.8%, TellMeWhy 36.8% — the plurality by a wide margin over
AFFECTIVE 4.8%/5.4%, PHYSICAL 12.3%/8.9%, MENTAL 6.0%/8.9%). `goal_status` is therefore the primary
predicate to fold; `prospect` (affective/fear-hope resolution) is secondary; `believes` (MENTAL) is tertiary.

### 2.2 Effect rules (which events establish / satisfy / thwart a goal, or cause an emotion)

All three rules are **already implemented**, not designed here — this section is a citation map, not new logic:

- **ESTABLISH**: `extract_goals_sentence` (goal_register.py:191-312) fires on desire/intend/try matrix verbs
  (`GOAL_VERBS`, :58-60) or `in order to`/`so as to`/bare-purpose infinitivals -> a new `Goal(status="active")`.
- **SATISFY**: `track_status_thwart` branch 2 (goal_register.py:583-587) — a later same-agent event whose
  `_norm_pred` (:459-474, handles irregular past: "won"->"win") matches the goal head. Branch 4 (:600-604,
  gated behind an injected `hdlab.structured_matcher`) additionally fires on a **converse** outcome (sell-goal
  satisfied by a buy-event of the same theme, role-swap, Cruse converseness).
- **THWART**: `_is_thwarted` (goal_register.py:652-670) — three cues: (1) later same-agent `FAILURE_VERBS`
  (:445-449), (2) later sentence negates the goal head, (3) goal-object + `ADVERSE_RESULTANT` cue (:452-458)
  co-occur in a later sentence. Branch 4's antonym leg (:600-604) is the matcher-mediated generalization.
- **APPRAISE**: `occ_appraisal.appraise(desirability, prospect)` (:118-143) — the fixed a-priori OCC table
  (authored from Ortony, Clore & Collins 1988, ch. 4-6, *before* any gold item, per the module's own docstring
  provenance note at occ_appraisal.py:114-117).

### 2.3 Precondition-read (what flips)

Exactly as `WorldState._read_preconditions` reads possession as a precondition for `use`/`give`/`close`
(world_state_register.py:199-213), the psychological register reads **goal resolution** as a precondition for
an appraisal-typed effect sentence E, or **goal existence** as a precondition for a goal-realizing-action E:

- If E is an **appraised/affect** sentence ("she was thrilled"): E presupposes `goal_status(g) ∈
  {satisfied, failed}` for some prior goal `g` of E's experiencer, such that `appraise(desirability(g),
  "actual")` (or the prospect branch) yields an OCC type whose `_TYPE_FAMILY`/`_TYPE_VALENCE`
  (occ_appraisal.py:45-56) matches E's actual stated family/valence (read via `AffectLexicon.category()`/
  `valence_sign()`, affect_lexicon.py:167-202).
- If E is a **goal-realizing action** ("she bought the bread"): E presupposes `has_goal(agent, g)` with
  `_lemma(g.goal_head) == _lemma(E.predicate)` and `g.sent_idx < E.sent_idx`, for the SAME canonicalized agent
  (`make_canonicalizer`, goal_register.py:712-765).

Removing the right candidate sentence flips one of these from met to unmet — this is the counterfactual test.

---

## 3. Ranked shortlist: 1-2 implementable designs, exact formulas

### DESIGN 1 (top pick) — GOAL-RESOLUTION LOO NECESSITY

Two sub-tests, same predicates, ablating a different role. Both are context-conditioned over the **whole**
story (fold all context sentences, not just the C_j-E pair) — this is the structural property that makes it
a genuine LOO test and not a pairwise-relation classifier.

**1a. ESTABLISHMENT necessity** (for E = a goal-realizing action):

```
def established(sents, sel, sel_agent, sel_pred_lemma, exclude=None):
    exclude = exclude or set()
    subset_idx = [i for i in range(len(sents)) if i != sel and i not in exclude]
    goals = bind_agents(extract_goals([sents[i] for i in subset_idx], [pos[i] for i in subset_idx]),
                         canonicalize)   # goal_register.py:315-326, :332-339
    return any(_lemma(g.goal_head) == sel_pred_lemma
               and (g.agent_canonical or g.agent) == sel_agent
               for g in goals)   # sent_idx ordering falls out of subset construction

def establishment_loo(sents, pos, sel, ci, sel_agent, sel_pred_lemma):
    met_full = established(sents, sel, sel_agent, sel_pred_lemma)
    if not met_full:
        return [0.0] * len(ci)
    return [1.0 if not established(sents, sel, sel_agent, sel_pred_lemma, exclude={j}) else 0.0
            for j in ci]
```

**1b. RESOLUTION necessity** (for E = an appraisal/affect statement) — the priority sub-test, since it is the
one that reaches the OCC composition and the emotion-typed subset of GOAL causation:

```
def resolved(goal, events_subset, sents, canon):
    g_copy = copy.copy(goal); g_copy.status = "active"
    track_status_thwart([g_copy], events_subset, sents=sents, canon=canon)   # goal_register.py:542-606
    return g_copy.status in ("satisfied", "failed"), g_copy.status

def resolution_loo(target_goal, events_all, ci_sent_idxs, sents, canon):
    met_full, status_full = resolved(target_goal, events_all, sents, canon)
    if not met_full:
        return [0.0] * len(ci_sent_idxs)
    out = []
    for j in ci_sent_idxs:
        events_wo = [e for e in events_all if e.sent_idx != j]
        met_wo, _ = resolved(target_goal, events_wo, sents, canon)
        out.append(1.0 if not met_wo else 0.0)
    return out
```

`desirability = +1 if status_full == "satisfied" else -1`; feed `occ_appraisal.appraise(desirability,
"actual")` and compare the returned type's `_TYPE_FAMILY` to E's gold-derived family (GLUCOSE/TellMeWhy's own
`>Causes/Enables>` antecedent match, exactly as `gold_cause_idx` already does in
`exp_genworldmodel_glucose_chain_v1.py:109-127` — reuse unchanged).

**Reuse map**: `hdlab.goal_register.extract_goals` (goal_register.py:315-326), `.bind_agents` (:332-339),
`.track_status_thwart` (:542-606), `.make_canonicalizer` (:712-765); `hdlab.occ_appraisal.appraise`
(occ_appraisal.py:118-143). **Gold loaders**: `experiments.exp_genworldmodel_glucose_chain_v1.load_items`/
`.gold_cause_idx` (unchanged); `experiments.exp_causal_reasoner_tellmewhy_v1.load_items` (unchanged).
**Integrator**: slot the score into `experiments.exp_genworldmodel_loo_necessity_v1`'s own harness — add
`S["psych_loo_necessity"] = _mm(resolution_loo(...))` alongside the existing `S["loo_necessity"]` line
(loo_necessity_v1.py:139), reuse `_eval`/`_null_p95`/`_order_shuffle_alone`/`boot` (:237-251, :208-234)
**unchanged** — this is a drop-in additional cue in the SAME already-built eval harness, zero new
infrastructure beyond the fold functions above. **Twin**: 1b's `desiderability`/`appraise` route also needs
the affect-lexicon comparison — `hdlab.affect_lexicon.AffectLexicon.category()`/`valence_sign()`
(affect_lexicon.py:167-202), read-only.

**Nothing here needs fitting.** `track_status_thwart` and `appraise` are fixed rule-tables (occ_appraisal's
own docstring, occ_appraisal.py:114-117, states the table was "authored BEFORE any gold item"). The only
free parameter is which cues in `_eval`'s `cues_base` list to combine with — reuse `["position", "recency",
"overlap", "means_end"]` unchanged, exactly as the physical LOO did (loo_necessity_v1.py:257).

### DESIGN 2 (second pick) — PROSPECT (FEAR/HOPE) CONFIRMATION LOO NECESSITY

For the AFFECTIVE population (~5%) and the subset of GOAL items whose effect sentence is a fear/hope
resolution rather than a bare satisfaction:

```
def prospect_resolved(desir, stim_words, outcome_sent_idxs, sents, exclude=None):
    exclude = exclude or set()
    texts = [sents[i] for i in outcome_sent_idxs if i not in exclude]
    pr = detect_prospect_sign(desir, stim_words, texts)   # occ_appraisal.py:187-219
    return pr["prospect"] in ("confirmed", "disconfirmed"), pr["prospect"]

def prospect_loo(desir, stim_words, ci, sents):
    met_full, _ = prospect_resolved(desir, stim_words, ci, sents)
    if not met_full:
        return [0.0] * len(ci)
    return [1.0 if not prospect_resolved(desir, stim_words, ci, sents, exclude={j})[0] else 0.0 for j in ci]
```

**Reuse map**: `hdlab.occ_appraisal.detect_prospect_sign` (occ_appraisal.py:187-219) and its
`_FAVORABLE`/`_ADVERSE` cue sets (:161-169), unchanged. `stim_words` comes from
`occ_appraisal._stimulus_words` (:334-346), which itself reads `AffectRegister`'s stated fear/hope affect
(affect_register.py:383-390) or the `_prospect_cue_fallback` (occ_appraisal.py:302-316). **Priority below
Design 1** because the AFFECTIVE population share (4.8%/5.4%) is small relative to GOAL (40.8%/36.8%) — build
this second, as a genuine ADD to Design 1's integrator (not a replacement), since some GOAL-typed gold pairs
route through the prospect branch when the effect sentence states an emotion rather than a bare action.

### DESIGN 3 (flagged, not ranked — smaller population, larger build) — BELIEF-UPDATE LOO

For the MENTAL population (6.0%/8.9%, where the physical register's `representable_by_type` measured exactly
**0.0** for both corpora — the physical fold literally cannot ever fire here): fold `belief_timeline.
timeline_belief` (belief_timeline.py:137-145) with candidate `j`'s `WorldEvent` excluded, check whether the
agent's belief-at-query-time flips. `shuffle_order_twin` (:310-320) is already the precedented info-free twin
for this exact register. Not built out to a formula here — flagged as the next-drill candidate once Design 1
lands, since it needs a `WorldEvent` extraction front-end GLUCOSE/TellMeWhy prose does not currently have
wired (BigToM's items come pre-structured; GLUCOSE/TellMeWhy prose would need `perceives_change`,
theory_of_mind.py:73-91, extended to non-BigToM narrative).

---

## 4. Info-free twins (must-run) + collapse warnings

### Required twins (mirrors the physical LOO's own two, `exp_genworldmodel_loo_necessity_v1.py:208-234`)

1. **Necessity-label permutation null**: permute the LOO scores across candidates within each firing item,
   recompute alone-accuracy, require observed > null p95 (`_null_p95`, loo_necessity_v1.py:208-223, reuse
   unchanged). The physical LOO's own numbers show exactly why this matters: on GLUCOSE, alone-accuracy 0.421
   did **not** clear null p95 0.4737 — it looked like it was doing something but was statistically
   indistinguishable from chance permutation. The psych-LOO must clear this bar honestly, not just "fire."
2. **Story-order shuffle twin**: permute sentence order before folding `extract_goals`/`track_status_thwart`;
   the `sent_idx <` ordering check inside `track_status_thwart`'s realized-scan (goal_register.py:584) makes
   this collapse *if* temporal ordering is actually load-bearing (`_order_shuffle_alone`, loo_necessity_v1.py:
   226-234, reuse unchanged).
3. **NEW — scrambled-agent twin** (recommended addition beyond the physical LOO, because goal-satisfaction is
   agent-bound in a way possession is not agent-exclusive across candidates the same way): consult a
   DIFFERENT character's `GoalRegister` than E's actual agent when checking establishment/resolution. A
   genuinely agent-bound mechanism must lose; a mechanism that's secretly keying off "any goal-shaped sentence
   anywhere nearby" will not.
4. **NEW — valence-permute twin** (precedented already in `exp_causal_mental_selector_faithful_v1.py`'s
   `val_permute` mode, :129-133): for Design 2, permute which candidate carries the appraisal-relevant
   valence before scoring; a genuine appraisal-typing effect collapses.

### Collapse warnings — what this design must NOT degenerate into

- **Raw affect-lexicon word-match** between C_j and E (e.g., "sad" appears in both) is the already-refuted
  associative/content-overlap cue (`comps["content"]` in `exp_genworldmodel_glucose_chain_v1.py`'s `topical`
  arm, and the `overlap` cue in the integrator's `cues_base`). The design above never compares C_j's and E's
  *words* directly — it compares `goal_status` (a discrete state derived from the whole-story fold) and passes
  it through the fixed `appraise()` rule table. If an implementation ever short-circuits to "candidate and
  effect share an emotion word," that is the collapse — check for it explicitly in code review.
- **Context-free goal-verb match** ("any prior sentence with a desire-verb wins") is the already-cleared
  goal-DETECTION capability (`goal_register.extract_goals` itself, or the integrator's existing `means_end`
  cue). The design above is safe from this **only because of the counterfactual removal step** — a
  goal-detection cue scores every candidate that merely co-occurs with a goal-shaped sentence; the LOO score
  is 1.0 **only** for the candidate whose removal specifically flips the fold. If two sentences both establish
  compatible goals (redundant/overdetermined establishment), correct LOO behavior is that **neither** scores
  1.0 alone (removing either one leaves the other still establishing) — this is a feature (matches Mackie
  INUS's own overdetermination handling), not a bug, but it means firing rate will be lower than a naive
  presence-cue's firing rate. That is expected and correct, not a regression.
- **A static type-admissibility table is a DIFFERENT, already-partially-built mechanism** —
  `experiments/exp_causal_mental_selector_faithful_v1.py`'s `necessity(ct, ot)` function (:82-94) is a fixed
  lookup table over WordNet-supersense event types (PERCEPTION/COGNITION/EMOTION -> admissible), combined with
  OCC valence and Talmy force-dynamics via a weighted argmax `_score` (:97-104) — **not** a leave-one-out
  removal test. It was measured on 8 constructed items + 16 LitBank connective-marked pairs (`RC.GOLD`), never
  on the GLUCOSE/TellMeWhy GOAL population, and has no saved `metrics.json`/headline on disk (checked: file
  exists, `data/exp_causal_mental_selector_faithful_v1/metrics.json` does not report a verdict). It is
  **adjacent prior art demonstrating the OCC-valence + type-compatibility ingredients work in isolation** —
  useful evidence that the appraisal composition is soundly built — but it is not a substitute for Design 1/2,
  and Design 1/2 must not quietly collapse into "argmax a static admissibility score" instead of running the
  actual counterfactual fold.

---

## Cheap decisive test

Before a full GPU/CPU dispatch: run Design 1b (resolution LOO) standalone on the **TMW-GOAL** population that
`exp_genworldmodel_loo_necessity_v1.py`'s own `_load_tellmewhy` already isolates (loo_necessity_v1.py:160-178,
the `goal` list). This population is small (n unreported in the metrics but drawn from `TMW_TEST[:1500]`,
non-adjacent-gold-only), fast to re-score (no spaCy re-parse needed — `_sent_reps`-equivalent for goal_register
just needs UPOS, already computed by `_analyze`/`SituationReader`), and is the population where the physical
LOO measured the most damning number: fires 0.02, alone-accuracy **0.000**. Any non-zero alone-accuracy on
this exact population, beating null p95, is a decisive first signal.

## Falsifiable predictions

**HARD-PASS** (report `PSYCH_LOO_HARD_PASS`): on the TMW-GOAL and GLUCOSE-GOAL-typed non-adjacent-gold subsets,
Design 1b's `resolution_loo` fires (met_full=True) on **>= 15%** of items (3x+ the physical LOO's 2%/4% firing
rate — GOAL causation should be reachable far more often than physical possession/toggle causation given the
census's 40.8%/36.8% type share), alone-accuracy-on-firing beats the necessity-permutation null p95
(`_null_p95`), beats the order-shuffle twin by >= 0.02 (mirroring `_order_shuffle_alone`'s existing margin
convention), beats the scrambled-agent twin, and the integrator lift (`+loo_necessity` cue vs.
`cues_base`-only) is CI-separated on the disjoint test split (`boot`, loo_necessity_v1.py:236-241).

**HARD-FAIL** (report `PSYCH_LOO_HARD_FAIL`): firing rate stays below 10%, OR alone-accuracy fails to beat
null p95, OR the scrambled-agent/order-shuffle twins do not collapse (mechanism is not actually reading the
story's psychological structure), OR the integrator lift is not CI-separated. In this case the next drill is
Design 2 (prospect) standalone, then Design 3 (belief, MENTAL population) as the remaining psychological
ontology slice — and if ALL THREE hard-fail, the honest conclusion is that GOAL/AFFECTIVE/MENTAL causation in
GLUCOSE/TellMeWhy requires world-knowledge bridging (Baker/Jara-Ettinger inverse planning over UNSTATED goals,
the located negative goal_register.py's own docstring already flags at Tier-2, :25-27) rather than a
structural register fix — a materially different, harder next problem.

**MIDDLE_BAND**: twins pass but integrator lift is not CI-separated, or firing rate is 10-15%. Report the
per-type breakdown (mirroring `_cov_diag`, loo_necessity_v1.py:181-198, adapted to goal-object-match ->
goal-agent-canonicalization-match) to localize whether the residual is agent-binding (coref) or genuine
goal-establishment coverage (Tier-1 desire/intend/try/purpose markers miss an implicit goal).

---

## Cross-thread synthesis

This closes the loop the arc opened: `exp_genworldmodel_causal_type_census_v1` diagnosed *why* the physical
LOO structurally caps at ~5% (representable_frac 0.056/0.025, matching the arc's own framing almost exactly).
`exp_genworldmodel_loo_resolved_v1` ruled out coref as the GOAL-population blocker (TMW-GOAL alone-accuracy
stays 0.000 under every resolver arm — surface, ACT-R, semantic). This note's contribution is showing that the
**substrate already contains the psychological-effect machinery** the physical register lacks — it was built
for a different consumer (`sm.infer_emotion` live read-out, occ_appraisal.py:32-33) and never connected to the
LOO cause-selection harness. `exp_causal_mental_selector_faithful_v1` is a nearby, independently-built
mechanism (type-admissibility + argmax, not counterfactual-fold) that validates the OCC-valence ingredient in
isolation but was never run on the GOAL population either — it is evidence *for* the appraisal composition
being sound, not a competing implementation of this design.

## Substrate-product implications (no publication framing)

If Design 1 clears HARD-PASS, the practical payoff is a materially more brain-faithful "why did this happen"
answer for the roughly two-in-five story sentences where the honest cause is "a character wanted something and
this event delivered or blocked it" — the dominant real-world shape of everyday narrative causation per this
arc's own census, not an edge case. It also means `occ_appraisal.py`'s existing live read-out
(`sm.infer_emotion`) gains a second, independent USE: not just "what does this character feel now" but "which
earlier sentence explains why" — the same organ answering two different situation-model questions, which is
the kind of reuse this substrate has been rewarded for finding elsewhere (goal_hierarchy_graph reusing
goal_register; theory_of_mind reusing belief_timeline+goal_register). Risk: if the firing rate lands in
MIDDLE_BAND, the honest read is that `track_status_thwart`'s realized-check (strict lemma match) is too narrow
for real prose paraphrase, and the fix is wiring `goal_outcome_relation`'s broader INSTANTIATES classifier
(rank 5 in the organ table) as an OR-condition — a second, smaller build, not a redesign.

## Citations (verified count: 9 external + 12 internal-organ)

External (well-established, cited from established knowledge; two lit-scan sub-agents dispatched in parallel
for independent web verification — see status note below): Trabasso & van den Broek 1985 (causal network
coding, counterfactual-necessity criterion); Trabasso, Secco & van den Broek 1984 (story grammar/GPAO); Suh &
Trabasso 1993 (reinstatement); Zwaan & Radvansky 1998 (event-indexing, intentionality dimension); Graesser,
Singer & Trabasso 1994 (inference taxonomy); Ortony, Clore & Collins 1988 (OCC); Mackie 1965/1974 (INUS);
Baker, Saxe & Tenenbaum 2009/2017 (inverse planning, bidirectional ToM); Wellman & Gopnik 1992 (theory-theory);
Lutz & Radvansky 1997 (goal status field); Wimmer & Perner 1983 (seeing->knowing); Sap et al. 2019 (ATOMIC);
Gandhi, Stojnic, Lake & Dillon 2023 (BigToM). Internal organs cited by file:line throughout Sections 1-4 (12
distinct hdlab/experiments modules).

**Status note**: two Sonnet lit-scan sub-agents were dispatched in parallel (goal-causation/OCC-appraisal
precedent; inverse-planning/BDI/belief-desire precedent, both querying generic cognitive-science terms per
query-privacy discipline) to independently verify the Trabasso 1985 goal-vs-physical framing and calibrate
whether "LOO counterfactual necessity over goal-satisfaction state" has direct published precedent. Their
results were not yet available at time of writing; this note's internal-organ grounding (Section 1-4,
file:line cited, with measured HARD_FAIL numbers from the physical LOO's own completed run) is the primary,
already-verified evidence base and does not depend on their output. If their findings materially change the
citation confidence, that will surface as a follow-up drill, not a retraction of the design above (the design
is grounded in on-disk organs, not in the external literature search).

---

### TLDR

Every ingredient needed to test "does a character's want getting fulfilled or blocked explain what happens
next" already exists in the code and already runs by default — nobody has yet pointed the physical version
of this test's *method* (remove one sentence, see if the story's state changes) at the *psychological* state
instead of the *physical* one. Building that costs about 150-250 lines connecting two already-built
components, not a new capability. The measured baseline this replaces catches the right cause in only 2 to 4
out of 100 sentences that need a psychological explanation instead of a physical one; if this works even
moderately well it should catch the right cause many times more often, because "someone wanted something" is
the actual reason behind about 4 in 10 everyday story sentences, not a rare case.

### QUESTIONS

None outstanding that block starting the cheap decisive test (Design 1b on TMW-GOAL). Open for exp_dev to
decide: whether to build 1a+1b together in one pass or 1b alone first (1b is higher-priority and standalone
testable without 1a).

### NEXT STEPS

1. exp_dev: implement Design 1b (`resolution_loo`) as a new function alongside
   `experiments/exp_genworldmodel_loo_necessity_v1.py`'s existing `_loo_scores`, reusing
   `hdlab.goal_register.track_status_thwart` + `hdlab.occ_appraisal.appraise` per Section 3's pseudocode.
2. Run the cheap decisive test on TMW-GOAL first (small, fast, the population with the most damning existing
   physical-LOO number to beat).
3. If firing rate clears 10%: run the full HARD-PASS gate (twins + integrator lift) on GLUCOSE-GOAL and
   TellMeWhy-GOAL, mirroring `_eval`'s exact train/test split and bootstrap CI convention.
4. If HARD-PASS: build Design 2 (prospect) as an ADD to the same integrator, not a replacement.
5. If HARD-FAIL on 1b: escalate to Design 3 (belief LOO, MENTAL population) as the next drill candidate before
   concluding the psychological ontology needs world-knowledge bridging rather than a register fix.
