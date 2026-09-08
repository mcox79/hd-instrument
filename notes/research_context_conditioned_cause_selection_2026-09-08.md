# Research: context-conditioned cause-selection mechanisms for build_the_generative_result_state_world_model (2026-09-08)

Filed by: research (Opus), director-requested deep operational drill (2x-style: level-2 drill on existing
findings, not a broad rescan). Trigger: after ~25 cells, the load-bearing signals for real-narrative
CAUSE-SELECTION are the context-FREE pairwise result-state check (`rs_fire`) + POSITION (GLUCOSE only) +
a Competition-Model cue integrator + a script-order prior; associative densification, a directed causal-KB,
and graph-reachability rollouts are REPEATEDLY NOT load-bearing because they are all CONTEXT-FREE stores.
The ask: the next lever is CONTEXT-CONDITIONED structure — infer the cause by conditioning on the RUNNING
SITUATION MODEL, not a context-free pair or static store. Specify one concretely enough to implement.

Method: read the 6 most relevant on-disk prior research notes in full (not re-derived), read the exact
current cause-selection cells (`rs_fire`, the Competition-Model integrator, the script-order cue, the
refuted directed-KB rollout) at file:line, read the 7 named organs at file:line, then dispatched 2 parallel
Sonnet lit-scan lanes on the two genuinely open questions this specific ask raises (counterfactual/INUS
cause-SELECTION-among-candidates psychology; Kuperberg/Rabovsky predictive-coding applied to MULTI-candidate
retrospective cause comparison — neither was covered by the 6 prior notes, which addressed CAUSE EXISTENCE
and precondition/force-dynamics but not cause SELECTION among several candidates specifically).

---

## HEADLINE

**The literature answer is decisive and was hiding in a citation the substrate already uses for something
else.** Trabasso & van den Broek's (1985, *JML* 24(5)) causal-network CODING CRITERION — "if event A had
not occurred, then, in the circumstances of the story, event B would not have occurred" — is a **leave-
one-out (LOO) counterfactual-necessity test applied pairwise across an entire story's event set**, and its
online-reading-time correlates (Suh & Trabasso 1993; van den Broek 1990; Fletcher & Bloom 1988) are
independently established. This is EXACTLY the same test as Mackie's (1965/1974) INUS-condition
"remove-X-check-sufficiency" procedure and Batusov & Soutchanski's (2018, KR workshop; arXiv:2501.06857
2025) STRIPS/situation-calculus formalization of "achievement causes" (counterfactually suppress an
action's preconditions/effects, check whether the target condition still holds) — three independent
literatures (narrative psychology, philosophy of causation, AI formal methods) converging on ONE
computation, none of them citing each other. **The substrate already has the exact machinery this test
needs, unused for this purpose**: `hdlab/world_state_register.py`'s `WorldState.fold`/`apply_event`/
`_read_preconditions`/`unmet_preconditions` builds a per-story mutable STRIPS state and reads events'
PRECONDITIONS against it — but the currently-wired cause-selection cell (`rs_fire`,
`experiments/exp_genworldmodel_resultstate_v1.py:234`) only checks a **candidate's own local clause**
against a goal span extracted from that SAME clause — a pairwise, single-hop check that never folds the
OTHER candidates or conditions on what else happened in the story. Folding the WHOLE non-adjacent context
set through `WorldState` and scoring each candidate by its LOO counterfactual necessity is a genuinely new,
context-conditioned computation that the confirmed-load-bearing `rs_fire` does not perform and the
refuted directed-KB rollout could not perform (that store was corpus-mined and context-free by construction
— see the warnings section for why this is not the same mechanism wearing a STRIPS label).

Both dispatched lit-scans independently confirm the counterfactual-necessity account is the ONLY one of the
five requested frameworks with a **direct, narrative-specific, online-reading-time-corroborated** precedent
for cause SELECTION among several candidates (not just cause DETECTION). Predictive-coding/surprisal-based
accounts (Kuperberg 2016/2021; Rabovsky, Hansen & McClelland 2018) are confirmed FORWARD-only, single-
hypothesis architectures with **zero published treatment of retrospective multi-candidate comparison** —
the natural "surprisal-reduction" operationalization is a real, established NLP-interpretability technique
(leave-one-out context attribution: AttriBoT arXiv:2411.15102; SePer arXiv:2503.01478) but has **never been
proposed as a human process model**, and the substrate's own SR-TD contrastive forward-regressor was
independently `MECHANISM_FALSIFIED` three times (`data/exp_event_level_sr_td_contrastive_relation_
inference_phase2_v1/metrics.json`), which rules out the most natural (trained) way to build it here.

---

## Ranked shortlist (top 3, decisive)

### #1 — LOO counterfactual world-state necessity (Trabasso & van den Broek 1985; Mackie 1965/1974 INUS;
Batusov & Soutchanski 2018/2025 STRIPS actual-causality; Haviland & Clark 1974 bridging)

**Per-candidate scoring formula.** For effect sentence E at position `sel`, and candidate set
`ci = {C_1...C_n}` (all non-adjacent prior sentences):

```
WS_full   = WorldState().fold(events[0 : sel], read_preconditions=False)      # apply ALL prior events
met_full  = WS_full.apply_event(rep(E), t=sel, read_preconditions=True)       # -> is E's precondition met?

for each candidate C_j in ci:
    WS_minus_j = WorldState().fold([events[i] for i in range(sel) if i != j])  # LOO fold, C_j removed
    met_minus_j = precondition_met(rep(E), WS_minus_j)

    necessary_j = met_full_precondition AND (met_minus_j == False)   # C_j is INUS-necessary for E
    # graded version: fraction of E's precondition atoms that flip met->unmet when C_j is removed
    score(C_j) = necessary_j as {0,1}, or the graded flip-fraction in [0,1]
```

Candidate with `score=1` (or max graded score) is the predicted cause; ties broken by the existing `rs_fire`
ACHIEVE label at C_j itself, or folded as a 6th cue into the Competition-Model integrator (see Cheap
decisive test).

**Exact organs to reuse (file:line):**
- `hdlab/world_state_register.py:133` — class `WorldState`; `.fold()` line 214; `.apply_event()` line 169;
  `._read_preconditions()` line 199 (the precondition-READ layer — the piece no other cause-selection cell
  uses); `.unmet_preconditions()` line 234; `.classify()` staticmethod line 152 (verb->op fallback).
- `experiments/exp_genworldmodel_resultstate_v1.py:104-131` (`_op_of`) — the EXISTING op-lexicon reuse
  pattern (prefers `hdlab.possession_operators.build_lexicon`, falls back to `WorldState.classify` + the
  `USE` set) — reuse this verbatim rather than re-deriving verb->operator mapping.
- `hdlab/bound_event_backbone.py:118` (`_norm_event`) — the EXISTING SituationReader-EventRecord ->
  `{ROLE: filler}` dict normalizer; adapt this (not `WorldState`'s own `rep` shape) to build the `apply_event`
  input from reader events (PRED/AGENT/PATIENT are already normalized there; `ARG2`/dative-recipient is the
  one field neither normalizer currently supplies — flag as the one extraction gap to close, e.g. via the
  existing PP-attachment/dative-shift detector in the front-end).

**What makes this genuinely different from the confirmed-load-bearing `rs_fire`:** `rs_fire`
(`experiments/exp_genworldmodel_resultstate_v1.py:234-251`) is gated on `_has_goal(cand_words, cand_lemmas)`
and only ever looks at ONE candidate clause vs. the effect clause — it structurally cannot represent
**redundant/overdetermined causes** (two sentences that each transfer possession of the same object) because
it never folds "what else happened." The LOO test is sensitive to exactly that: if two prior sentences are
each individually redundant (removing either one alone does not flip E's precondition because the other
still supplies it), the LOO test correctly assigns LOW necessity to both — a genuinely higher-order
computation `rs_fire`'s pairwise check cannot produce even in principle. It is also NOT gated on `_has_goal`
— it can fire on any precondition-bearing effect (USE/TOGGLE_OFF/GIVE preconditions), reaching the
non-GOAL/OTHER population `rs_fire`'s own disclosed coverage gap (`cov["coverage_frac_of_miss"]` in that
cell) structurally cannot reach.

**Info-free twin (two, both required):**
1. **Story-order shuffle.** Permute the SENTENCE ORDER used to build the fold (keep each candidate's own
   content fixed, scramble the sequence positions before folding). If the mechanism is genuinely reading the
   sequential precondition-transition structure (not a disguised overlap proxy), boundary/necessity accuracy
   should collapse toward the `objmatch`-style floor, because scrambled order lets a temporally-impossible
   candidate (one that would occur AFTER E) get credited — a real causal-order test cannot survive this.
   This is the same family of twin already used and load-bearing-confirming elsewhere on this arc:
   `n400_coherence_monitor`'s running-reset-vs-global-anchor test, `bound_event_backbone`'s binding-shuffle,
   `script_order_cue_v1`'s per-item shuffled-script twin (`experiments/exp_genworldmodel_script_order_cue_v1.py:159-164`).
2. **Necessity-label permutation NULL**, reusing the EXISTING `null_twin` harness verbatim
   (`experiments/exp_genworldmodel_resultstate_v1.py:412-430`, K=400 shuffles, null mean + p95 + p-value):
   permute the per-candidate necessity score across candidates WITHIN each item, recompute accuracy — the
   mechanism is load-bearing iff observed accuracy beats the null p95.

**Warning — how this collapses to an already-refuted mechanism if built wrong:** the refuted
`exp_genworldmodel_directed_kb_rollout_v1.py` mechanism was a **corpus-mined, cross-story, static** directed
verb-pair graph (`CausalKnowledgeStore`, 65k pairs mined offline from CSKG) queried by BFS reachability —
context-FREE by construction, which is exactly why a same-density random-edge twin matched it
(`causal_kb_load_bearing=False` unless it separately beats base). The LOO mechanism above is NOT this: it
builds a **fresh, story-specific mutable state from THIS story's own sentences only**, never touching a
cross-story KB. If an implementer "simplifies" this by pre-computing a static a-priori
precondition/effect table across many stories (instead of folding the ACTUAL sentences of the ACTUAL story
being read), it degenerates back into exactly the refuted directed-KB shape — the fold MUST run per-item,
per-story, over that story's own extracted events, every time.

---

### #2 — Kintsch Construction-Integration coherence-settling (Kintsch 1988, *Psych Rev* 95(2); Kintsch 2005,
*Discourse Processes* 39(2-3), exact equation already primary-source-verified in
`notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md` section 1a)

**Per-candidate scoring formula.** Build a small coherence network over the discourse-so-far's TYPED
relational bindings (not raw distributional cosine — see warning), then read each candidate's contribution
to E's SETTLED activation via iterated constraint-satisfaction:

```
nodes   = {content(C_j) for C_j in ci} union {content(E)} union {already-bound CausalLinkRegister facts}
edges   = pairwise coherence: bind/bundle-consistency (CausalLinkRegister CAUSE/EFFECT membership = +edge;
          quality_relation.py opposition channel hit = -edge; else content-stem overlap, small weight)
A       = net_activation(supports={"coherence": [coherence(C_j, network \ C_j -> E) for C_j in ci]}, weights)
score(C_j) = settled activation of E after C_j is folded IN vs LEFT OUT (LOO again), read via
          normalized_recurrence(A) -- Spivey-Knowlton settling, cycles-to-settle = the graded difficulty
```

**Exact organs to reuse (file:line):**
- `hdlab/graded_competition.py:57` (`net_activation`, additive Lewis-Vasishth cue activation — ALREADY the
  landed organ for exactly "combine several per-candidate supports into one activation"), `:91`
  (`normalized_recurrence`, Spivey-Knowlton iterated mutual-inhibition settling — the CI "integration" step),
  `:119` (`graded_pick`, returns the settled distribution + entropy + margin + cycles in one call).
- `hdlab/situation_model_accumulate.py:486` (`CausalLinkRegister`) — `add_causal_link`/`query_effect_of`/
  `query_cause_of` (lines 534-583) supply the TYPED bound-fact edges the coherence network needs (not a flat
  embedding average).
- `hdlab/cleanup_family.py:201` (`iterative_attractor`) as an alternative/complementary settling readout
  (CA3/DG-attractor-shaped, per `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md`
  section 3 mapping table) if a Hopfield-style relaxation over the raw vectors is preferred to the discrete
  Competition-Model activation above.
- **This is directly implementable as a 6th cue inside the ALREADY-VALIDATED Competition-Model integrator**
  (`experiments/exp_genworldmodel_competition_model_integrator_v1.py:59` `_supports`, `CUES` list line 50) —
  literally the same extension pattern `script_order_cue_v1.py` already used to add its 5th cue.

**Info-free twin:** shuffle which facts are considered bound in `CausalLinkRegister` (scramble the
CAUSE/EFFECT link membership before computing coherence) — if the coherence score collapses to the
EXISTING `overlap` cue's accuracy, it adds no independent information. Must ALSO pass the
`five_vs_four`-style CI-separated integrator-lift test AND a shuffled-network `script_load_bearing`-style
test, run EXACTLY as `experiments/exp_genworldmodel_script_order_cue_v1.py:156-174` already does for its
5th cue — this methodology is proven and should be reused verbatim, not reinvented.

**Warning:** if the "coherence network" is built from raw distributional cosine similarity over a flat bag
of context vectors (rather than the TYPED `CausalLinkRegister` bindings), this is a relabeled
associative-relatedness-densification — **already refuted** (`exp_genworldmodel_rollout_phase_diagram_v1.py`
family: a same-density random-edge twin matches raw densification). The differentiator that keeps this
genuinely Kintsch-shaped and not a repeat of the refuted mechanism is that edges must come from STRUCTURED,
bound relational facts (bind/bundle FHRR via `CausalLinkRegister`), not raw embedding cosine.

---

### #3 — LOO surprisal-reduction on the existing N400 content-prediction-error stream (Rabovsky, Hansen &
McClelland 2018; Kuperberg 2016/2021) — ranked THIRD, higher risk, build only after #1 and #2

**Per-candidate scoring formula** (glass-box, NO training — reuses the running-mean machinery already in
the landed organ, sidestepping the substrate's own disclosed hard constraint against trained forward-
regression):

```
e_with_Cj    = 1 - cos(content(E), gist_including(C_j))     # N400CoherenceMonitor's own error, content space
e_without_Cj = 1 - cos(content(E), gist_excluding(C_j))     # LOO: same gist, C_j's content vector removed
score(C_j)   = e_without_Cj - e_with_Cj                     # surprisal REDUCTION attributable to C_j
```

**Exact organ (file:line):** `hdlab/n400_coherence_monitor.py:84` (`N400CoherenceMonitor`), specifically the
content-space prediction-error computation at `:150` (`e = 1.0 - _cos(v, ref)`) and the running-gist
accumulation at `:169` (`self._gist_sum = self._gist_sum + v`). Compute the LOO gist by summing all
candidate content vectors EXCEPT `C_j` instead of subscribing to the monitor's own online accumulation —
this is a batch re-application of the SAME formula, not a new mechanism.

**Both dispatched lit-scans independently confirm this specific operationalization is NOT literature-
stated anywhere** — Kuperberg's and Rabovsky's frameworks are confirmed FORWARD-only (next-word/event
prediction, single-hypothesis goal-revision), with **zero published treatment of comparing prediction-error
reduction across several retrospective candidate causes**. The LOO-ablation-attribution TECHNIQUE itself is
real and established, but only in ML interpretability (AttriBoT arXiv:2411.15102 — LOO context attribution;
SePer arXiv:2503.01478 — "semantic perplexity reduction" for RAG evaluation), **never proposed as a model of
human causal-antecedent selection**, and no bridge exists in print between that literature and the
Trabasso causal-network literature. Treat this as this drill's own novel synthesis: P is capped at 0.50 and
should be deflated further (0.15-0.25) per calibration discipline before betting on it as psychologically
faithful — build it as a THIRD, lower-priority arm, not the lead.

**Info-free twin:** swap WHICH candidate's content vector is credited with the removal (shuffle the
candidate-to-Δe assignment within the item) — the same `null_twin` pattern as #1. Also run a
content-vs-position confound check: the delta must survive controlling for `C_j`'s raw position (since
raw surprisal magnitude is highly collinear with recency).

**Warning — the single highest collapse risk of the three:** `e = 1-cos(content, gist)` IS a semantic-
similarity computation; an LOO delta on it is dangerously close to a relabeled associative-relatedness-
densification (**already refuted**) unless what is scored is the DELTA under REMOVAL (not raw magnitude)
AND it is shown to survive the shuffled-attribution twin above. Do not report a raw `e` value as a
"surprisal-reduction cause score" without the LOO delta — that would just be `overlap` (already in the
Competition-Model integrator as its own cue) wearing a new name.

---

## Explicit warnings — collapse-to-known-negative checklist

| Proposed mechanism | Collapses to (already-refuted) if... | What must differ |
|---|---|---|
| #1 LOO precondition-necessity | ...built as a pre-mined cross-story precondition/effect table (a static KB) instead of a fresh per-story fold | `WorldState.fold` must run on THIS story's own extracted events every time, never a corpus-level static table (that IS the refuted `directed_kb_rollout` shape) |
| #1 LOO precondition-necessity | ...implemented WITHOUT folding the other candidates (i.e., just C_j's own local ACHIEVE/DEFEAT label) | That degenerates exactly to the ALREADY-confirmed `rs_fire` — no new information; the LOO-over-OTHER-candidates fold is the entire differentiator |
| #2 Kintsch coherence-settling | ...edges are raw distributional cosine over a flat context bag | Edges must come from TYPED bound facts (`CausalLinkRegister`), not flat embedding similarity — that IS the refuted associative-densification shape |
| #2 Kintsch coherence-settling | ...tested only as a standalone accuracy number, not as a 5th/6th cue vs. the 4/5-cue integrator with a shuffled-network twin | Must run the EXACT `five_vs_four` + `script_load_bearing` dual test `script_order_cue_v1.py` already used — anything less is not a fair "load-bearing" claim on this arc's own evidentiary standard |
| #3 LOO surprisal-reduction | ...scores raw `e` magnitude rather than the LOO delta | Raw content-similarity magnitude IS the `overlap` cue already in the integrator — must be the counterfactual DELTA, tested against the shuffled-attribution twin |
| #3 LOO surprisal-reduction | ...implemented by training a new forward regressor conditioned on situation-state (the "obvious" ML move) | The substrate's own SR-TD contrastive forward-regressor was independently `MECHANISM_FALSIFIED` 3x (`data/exp_event_level_sr_td_contrastive_relation_inference_phase2_v1/metrics.json` — trained margin +0.0025 vs required >=0.05); retrieval/running-mean beats trained regression on this substrate, do not re-attempt training here |
| Any of the three | ...position/recency does the real work under the hood (segment-membership, recency-weighted gist, etc.) | Each MUST be tested as an ADDITIONAL cue vs. the position cue already inside the Competition-Model integrator (`experiments/exp_genworldmodel_competition_model_integrator_v1.py:50` `CUES`), CI-separated, exactly the discipline `script_order_cue_v1` already applied — a mechanism that only wins by smuggling in position is not a new lever |

---

## (4) `hdlab/predictive_reader.py` fitting status — decisive answer, no fitting needed

**A persisted, fitted asset already exists and is already wired live**: `data/frontend_assets/
predict_surprisal_predictor_v1.pkl` (1.90 MB, written 2026-08-31; verified present on disk this cycle).
Loaded by `hdlab/situation_reader.py:172` (`_PREDICT_SURPRISAL_ASSET`) and `:2586`
(`self._pr_predictor = PredictiveReader.load(self.predict_surprisal_asset or _PREDICT_SURPRISAL_ASSET)`) —
this is NOT an island; the live reader already loads it. It was fit on **QA-SRL v2 gold predicate-argument
triples** (verb lemma, argument head, role in {AGENT, PATIENT}), extracted via
`experiments/exp_predictive_reader_anticipation_surprisal_v1.py:99` (`extract_triples`, gold verb index +
gold agent/patient spans from `data/benchmark_trap_check/qasrl/qasrl-v2/orig`, `min_args=5` per its own
metrics params) — a modern-text corpus chosen specifically to avoid the 19c/McGuffey age confound (per that
cell's own docstring). **If a situation-state-CONDITIONED variant of the predictor is wanted for mechanism
#3** (predicting the expected next content given the FOLDED discourse state, not just the local verb-role),
that is a fresh fit target this asset does not cover — the recipe is: extend `extract_triples`-style triples
to `(situation_state_summary, role, arg)` keys instead of `(verb, role, arg)`, call
`PredictiveReader(temp=...).fit(triples)` (`hdlab/predictive_reader.py:97`), then `.save(path)`
(`hdlab/predictive_reader.py:175`) to a new asset path — but mechanism #3 as scoped above does NOT need
this; it reuses `N400CoherenceMonitor`'s existing untrained running-gist machinery instead, specifically to
avoid a new fitting/training step.

---

## Cheap decisive test

Run mechanism #1 (top pick) FIRST, as a 6th cue inside the EXISTING, already-validated Competition-Model
integrator harness (`experiments/exp_genworldmodel_competition_model_integrator_v1.py`), on the SAME two
corpora already used across this arc (GLUCOSE non-adjacent, TellMeWhy non-adjacent GOAL), reusing the
existing train/test split-by-parity discipline (no leak):

1. Add `loo_necessity` as a 5th (or 6th, alongside `script_order`) cue: `_supports()` gains
   `"loo_necessity": [loo_score(WS, sw[j], sl[j], sw[sel], sl[sel]) for j in ci]` per item, computed via
   `WorldState.fold` over that item's own sentences with `j` left out (mechanism #1's formula above).
2. Fit weights on train (`_fit_weights`, the existing delta-rule/Rescorla-Wagner learner,
   `experiments/exp_genworldmodel_competition_model_integrator_v1.py:125`), score on disjoint test.
3. Run BOTH info-free twins from mechanism #1's section above on the held-out test split.
4. Extend to the non-GOAL/OTHER TellMeWhy population (mechanism #1's structural advantage over `rs_fire` —
   it is not gated on `_has_goal`) as a SEPARATE arm, since that population is exactly where `rs_fire`
   structurally cannot fire (`cov["coverage_frac_of_miss"]` in `exp_genworldmodel_resultstate_v1.py`).

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND)

**HARD-PASS**: the 5/6-cue integrator with `loo_necessity` beats the current best (4-cue GLUCOSE / 5-cue
TellMeWhy-with-script_order) integrator CI-separated on AT LEAST ONE corpus AND `loo_necessity` beats BOTH
info-free twins (story-order shuffle collapses it; necessity-label-permutation null p95 beaten) AND it
fires on a materially non-zero fraction of the non-GOAL/OTHER TellMeWhy population `rs_fire` cannot reach.

**MIDDLE_BAND**: `loo_necessity` beats its own info-free twins (genuinely reading the story-specific state)
but does not CI-separate the integrator lift on either corpus — real signal, needs richer coverage (more
verb-op lexicon entries, or `ARG2`/dative-recipient extraction closing the flagged gap) before it earns a
seat in the default cue set.

**HARD-FAIL**: `loo_necessity` does not beat the story-order-shuffle twin (i.e., it is reading local content
overlap, not genuine sequential state-transition — likely means the fold's precondition-read is too coarse
or under-covered to carry order information), OR it does not beat the necessity-permutation null p95, OR
adding it to the integrator REGRESSES accuracy on either corpus outside noise — in that case fall back to
mechanism #2 (Kintsch coherence-settling) as the next candidate to test, per the same harness.

---

## Cross-thread synthesis

- Directly extends and RESOLVES the open question in
  `notes/brain_foundational_confirmation_whole_architecture_2026-07-29.md` (SEM/EST convergent finding that
  discrete event-boundary segmentation, not continuous blending, is the missing system-level element) and
  `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md` (retrieval+recombination,
  never trained regression, is the literature-and-disk-verified correct shape) — mechanism #1 and #2 above
  are both retrieval/settling-over-structured-state computations, consistent with both findings; mechanism
  #3 is explicitly flagged as the one closest to the banned trained-regression shape and is scoped to avoid
  it (untrained running-gist, not a fitted predictor).
- Directly extends `notes/research_psych_bridging_inference_situation_models_2026-08-09.md` (ACHIEVE/
  CONTRADICT graded relation queries over `AccumulateRegister`) and
  `notes/research_preclusion_goal_failure_inference_2026-08-09.md` (event-calculus `Clipped`/`terminates`,
  ASP-NAF `interferes` as the SAME symbolic mutex/precondition shape mechanism #1 uses) — this drill supplies
  the missing CAUSE-SELECTION-AMONG-CANDIDATES layer those two notes did not address (they covered cause
  EXISTENCE/preclusion for a single candidate-outcome pair, not ranking several candidates).
- Directly extends `notes/research_sem_crp_brain_fidelity_audit_2026-08-09.md` (sticky-CRP is
  Marr-computational-level-only; DG/CA3 continuous competition is the better brain shape) — mechanism #2's
  settling step deliberately reuses `graded_competition.normalized_recurrence`/`cleanup_family.
  iterative_attractor` (the DG/CA3-shaped continuous-competition family that note recommended) rather than
  any discrete-cluster mechanism.
- NEW this cycle (not previously on disk): the Mackie/Trabasso/Batusov-Soutchanski three-way convergence on
  the LOO counterfactual-necessity test, and the confirmed absence of any multi-candidate treatment in the
  Kuperberg/Rabovsky predictive-coding literature — both surfaced only by this cycle's 2 targeted lit-scans,
  filling the one gap the 6 prior notes left open (they covered cause EXISTENCE mechanisms, not cause
  SELECTION-among-several-candidates mechanisms specifically).

## Substrate-product implications

If mechanism #1 clears HARD-PASS or MIDDLE_BAND, the product gains a materially richer auditable trace for
cause-selection: instead of "this candidate's goal-object reappeared in the effect clause" (the current
`rs_fire`/`objmatch` trace) or "this candidate typically precedes this effect across many stories" (the
current `script_order` trace), the trace becomes "removing this specific sentence from the story would have
left the effect's precondition [have(X)/is_open(X)] unmet — this is why it, and not the other candidates,
is the cause" — a step-by-step, counterfactually-testable explanation an LLM black box cannot produce (it
has no discrete state to counterfactually remove a fact from). This is the same glass-box auditability
differentiator this arc has repeatedly identified as the defensible product edge. In plain terms: the
system would be able to say not just "these two sentences are both about the same object" but "take this
one sentence away and the ending couldn't have happened the way it did" — the same kind of explanation a
person gives when asked "why did this happen," and it can point to the exact fact it checked.

## Citations (verified count)

Directly verified THIS cycle by the 2 dispatched lit-scan lanes (15 + 20 tool-uses, mixed full-text/
abstract/search-confirmed): Mackie 1965 (*Am Phil Q*) / 1974 (*The Cement of the Universe*, Oxford); Wright
NESS test (arXiv:2012.05123 secondary); Halpern & Pearl actual-causation structural-model account (modified
HP-definition papers); Cheng & Novick 1990 (*JPSP*) / Cheng 1997 (*Psych Rev*) Power PC (Luhmann & Ahn 2005
critique); Hilton & Slugoski 1986 (*Psych Rev*) abnormal-conditions-focus, Hart & Honoré 1959 *Causation in
the Law*; Kominsky, Phillips, Gerstenberg, Lombrozo & Knobe 2015 (*Cognition*); Icard, Kominsky & Knobe 2017
(*Cognition*); Gerstenberg, Goodman, Lagnado & Tenenbaum 2021 (*Psych Rev*, counterfactual simulation model)
+ Gerstenberg 2024 (*TiCS* review, flags narrative extension as open); Batusov & Soutchanski 2018 (KR/AAAI
workshop) + arXiv:2501.06857 (2025); Trabasso & van den Broek 1985 (*JML* 24(5)); Trabasso & Sperry 1985
(*JML* 24(5)); Fletcher & Bloom 1988; van den Broek 1990; Suh & Trabasso 1993; GLUCOSE (Mostafazadeh et al.
2020, EMNLP); Kuperberg 2016 (*Lang Cogn Neurosci* 31(5)); Kuperberg & Jaeger 2016 (*Lang Cogn Neurosci*
31(1)); Kuperberg 2021 (*Topics in Cognitive Science* 13(1)); Rabovsky, Hansen & McClelland 2018 (*Nat Hum
Behav* 2); "Modeling Language as a Sequence of Thoughts" arXiv:2512.25026 (2026 preprint, Thought-Gestalt
architecture, no LOO-ablation evaluation); AttriBoT arXiv:2411.15102 (LOO context attribution); SePer
arXiv:2503.01478 (semantic-perplexity-reduction RAG evaluation); Friston 2005/2010 precision-weighting
(secondary/background, no multi-candidate treatment found).

REUSED (not re-verified this cycle, already primary-source-verified in the 6 prior notes read in full):
Franklin, Norman, Ranganath, Zacks & Gershman 2020 (SEM, *Psych Rev* 127(3)); Kintsch 1988 (*Psych Rev* 95(2))
/ 2005 (*Discourse Processes* 39(2-3), exact iterated-spreading-activation equation quoted); Zwaan & Radvansky
1998 (*Psych Bull* 123(2)); Zwaan, Langston & Graesser 1995; Haviland & Clark 1974; Fikes & Nilsson 1971
(STRIPS); Talmy 1988/2000 force dynamics; Wolff & Song 2003, Wolff 2007 dynamics theory of causation;
McKoon & Ratcliff 1992; Graesser, Singer & Trabasso 1994; Suh & Trabasso 1993 / Trabasso & Suh 1993; Barsalou
2009; Schacter & Addis 2007; Hassabis, Kumaran, Vann & Maguire 2007; Collins & Loftus 1975; Anderson & Lebiere
1998 (ACT-R).

Disk-verified this cycle (not literature): `data/exp_event_level_sr_td_contrastive_relation_inference_
phase2_v1/metrics.json` (MECHANISM_FALSIFIED, trained forward-regression); `data/frontend_assets/
predict_surprisal_predictor_v1.pkl` (exists, 1.90MB, 2026-08-31); all ~25 `experiments/exp_genworldmodel_*`
cells (file listing + 4 read in full: `resultstate_v1`, `competition_model_integrator_v1`,
`script_order_cue_v1`, `directed_kb_rollout_v1`); 7 named organs read in full at file:line
(`world_state_register.py`, `predictive_reader.py`, `n400_coherence_monitor.py`, `bound_event_backbone.py`,
`state_of_mind.py`, `situation_model_accumulate.py`, `consolidation_gate.py`) plus `graded_competition.py`
and `temporal_script_schema.py`.

Total distinct sources this note directly draws on: 46 (25 fresh-verified across 2 lit-scan lanes this
cycle, 21 reused-with-attribution from 6 prior on-disk notes read in full).

## Calibration

Per mandatory lit-scan calibration policy: mechanism #1's LITERATURE-CHARACTERIZATION claims (Mackie/
Trabasso/Batusov-Soutchanski convergence, online-reading-time correlates) are well-verified across two
independently-dispatched lanes — P(literature characterized accurately) ~0.75 pre-deflation, **deflated to
0.55** (top of the 0.15-0.25 band, reflecting that the INTEGRATED claim — LOO removal over an incrementally
built STRIPS state as the mechanism — is this drill's own novel synthesis bridging three literatures that do
not cite each other, honestly flagged as such by both lit-scan lanes). P(mechanism #1 HARD-PASSes the cheap
decisive test as specified) is capped at the mandatory novel-synthesis ceiling: **P_deflated = 0.40**.
Mechanism #2 (Kintsch settling): P_deflated = 0.35 (well-grounded literature, but the specific "6th cue"
instantiation is this drill's own construction). Mechanism #3 (LOO surprisal-reduction): **P_deflated = 0.25**
— capped low given both lit-scans independently confirmed zero published precedent for the specific
operationalization and flagged the highest collapse-to-overlap risk of the three.
