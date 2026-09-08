# Research: the resolution wall and what the gold labels actually encode (2026-09-08)

Filed by: research (Opus), director-requested deep operational drill (level-2, past-surface-diagnosis) on
`build_the_generative_result_state_world_model`. Trigger: owner says "we clearly don't understand this fully
yet" after 29 cells / cycles 1-15 of SOLVED.md. Method: read SOLVED.md in full (both halves), read
`exp_genworldmodel_psych_loo_v1.py`, `exp_genworldmodel_causal_type_census_v1.py`,
`exp_genworldmodel_competition_model_integrator_v1.py` and their `metrics.json` in full; read
`hdlab/goal_register.py` (542-670), `hdlab/goal_outcome_relation.py`, `hdlab/structured_matcher.py`,
`hdlab/quality_relation.py` in full; sampled `data/corpora/glucose/train.jsonl` and inspected
`data/corpora/tellmewhy/` loader code; dispatched 3 parallel Sonnet lit-scan lanes (Q1 semantic
goal-satisfaction NLP literature, Q2 GLUCOSE/TellMeWhy primary-source annotation-protocol fetch +
norm/counterfactual/explanatory-virtue causal-selection literature, Q4 XAIP/normality-weighted
actual-causation literature), each independently WebFetch-verified against primary sources where possible.

---

## HEADLINE

**Q2 is the crux, and it reframes the whole arc.** Both GLUCOSE (Mostafazadeh et al. 2020, EMNLP) and
TellMeWhy (Lal et al. 2021, ACL-IJCNLP Findings) instruct annotators to produce a **best, plausible,
relevant** explanation ("just give your intuition"; "any plausible explanation you can come up with";
an answer is invalid only if it "does not give a plausible reason... and states an irrelevant piece of
information") — **neither protocol ever asks annotators to test removal/negation of a candidate** (the
operational signature of counterfactual necessity is structurally absent from both instruction sets). GLUCOSE
goes further and **self-cites its own theoretical grounding**: Miller 2019 ("people... choose which of an
event's many causes to cite based on its **relevance** to the context") and Lombrozo 2006 ("people explain by
appealing to broader theories that enable **generalization**") — i.e. GLUCOSE was designed, by its authors'
own stated theory, as a best-explanation/relevance dataset, not a counterfactual-necessity dataset. This means
the LOO counterfactual-necessity mechanism (Trabasso/Mackie/Batusov-Soutchanski) — while a real, well-cited,
mathematically correct computation, and the mechanism that **excels at oracle binding** (cycle-3, +0.035
CI-sep) — is being scored against gold labels that were elicited by a **different theoretical construct**
(best/simple/broad/relevant explanation, per Lombrozo 2016; Hilton 1990). This is not a contradiction of the
earlier "LOO is the right mechanism" finding — it is one level deeper: **LOO is correctly built and correctly
excels when tested on its own construct (oracle necessity); it keeps losing on real narrative gold because the
gold is not primarily measuring necessity.** Topical connectivity, position/script order, and result-state
achievement are not "cheap heuristics that happen to win" — they are the three cheapest available **proxies
for the actual reward signal** (a broad, simple, script-typical, intuitively-satisfying explanation), which is
why every generated/typed/structured LOO-shaped signal has tied-or-lost to them across ~15 cycles.

Q4 supplies the literature's own fix for exactly this mismatch: **Icard, Kominsky & Knobe 2017** (*Cognition*
161) give a computable **necessity-sufficiency-typicality** blend, φ(X,Y) = P(X abnormal)·necessity(X,Y) +
P(X normal)·sufficiency(X,Y) — abnormal (atypical) candidates get judged mostly by counterfactual necessity,
typical/on-script candidates get judged mostly by sufficiency. This is a genuinely different, well-supported
computation from both topical association and flat-additive cue integration, and every ingredient it needs is
**already built on this substrate**: necessity = `loo_necessity`/`psych_loo` (built, cycle-13/15), sufficiency
= `rs_fire`/means-end (built, cycle-1-10), typicality = the `temporal_script_schema` p_before store (built,
cycle-11/12). Q1 gives a concrete, mostly-zero-cost partial fix for the goal-**resolution** sub-wall
(`track_status_thwart`'s strict-lemma realized-check): `hdlab/structured_matcher.py`'s converse/antonym store
is **already wired as an optional parameter** (`goal_register.py:600-604`, `_matcher_converse_antonym` at
:614-649) but the psych-LOO cell never passes it (`exp_genworldmodel_psych_loo_v1.py:92`,
`track_status_thwart(gg, evs, sents=toks, canon=None)` — no `matcher=`). Passing it is a **strict superset,
zero build cost, zero risk** — but the estimated recovery is small (Section 1). `hdlab/goal_outcome_relation.py`'s
INSTANTIATES classifier is a genuine but narrow Tier-2 upgrade (3 hand-authored pools tuned to DesireDB's
vocabulary, not GLUCOSE/TellMeWhy's) that would need pool re-authoring, not a drop-in.

P_deflated for the Q2 reframing claim (protocol instructions favor best-explanation over necessity-elicitation):
**0.55** (direct primary-source quotes from both papers, both independently corroborating; deflated from ~0.75
because the *inference* that this explains 15 cycles of LOO-vs-topical results is this drill's own synthesis).
P_deflated for the Icard-Kominsky-Knobe cue as a load-bearing integrator arm: **capped at 0.40** (novel
synthesis, mandatory ceiling). P_deflated for structured_matcher wiring recovering >=3pp resolution: **0.35**.

---

## Q1 — the resolution wall: which organ, how much, at what cost

**`track_status_thwart` (`hdlab/goal_register.py:542-606`)** resolves a goal in two baseline branches: negation
(:576) and **strict lemma-normalized match** (:583-587, `pl == ah` after `_norm_pred`/`IRREG_PAST`, :459-474,
:484-487) — this is the measured bottleneck (psych_loo research note + this cycle's own funnel numbers, Section
below). Two extension points already exist in the function signature and are **unused by the LOO cell**:

| Organ | Exact hook | What it adds | Fitting needed? | Estimated recovery |
|---|---|---|---|---|
| `hdlab/structured_matcher.py` `StructuredMatcher` (class :61), `.converse()` (:220-230), `.antonym()` (:190-202) | `goal_register.py:600-604` branch 4, `_matcher_converse_antonym` (:614-649) — **already implemented, gated behind an optional `matcher=` param `track_status_thwart` already accepts** (:542, :551-557 docstring). `exp_genworldmodel_psych_loo_v1.py:92`'s `_statuses()` calls `track_status_thwart(gg, evs, sents=toks, canon=None)` with **no `matcher=`** — branch 4 never fires today. | A later same-agent event that is a **converse** of the goal head (role-swap, e.g. wanted-to-SELL satisfied by a BUY of the same theme) -> satisfied; a pure **antonym** (goal-holder's own opposite, win/lose) -> failed. THEME-gated (:630-637), not agent-only. | **No.** `StructuredMatcher` is read-only over static WordNet/FrameNet/ConceptNet assets; no eval-fit. | **Small, ~+2-5pp absolute resolution rate.** Converse/antonym is a narrow, precise relation class (role-swaps and pure opposites), not the dominant "wanted to relax"->"took a nap" (topic-shift/instantiation) shape. Zero cost, zero risk (strict superset per the module's own byte-identity guarantee when abstaining) — **wire it regardless**, independent of whether it clears a HARD-PASS bar alone. |
| `hdlab/goal_outcome_relation.py` `relation_votes` (:595-617), `pair_feats`/`goal_atoms`/`outcome_atoms` (:221-228, :183-218) | Needs an adapter: `track_status_thwart` operates on (Goal, later-event) with sentence-indexed predicates; `goal_outcome_relation` operates on (desire_text, outcome_text) STRING pairs (DesireDB's own shape). A new branch 5 would call `relation_votes(g.goal_text, sent_text)` for later sentences and treat an `INSTANTIATES`-POS vote as satisfied. | The genuinely-needed **semantic-instantiation** bridge ("wanted to know why" satisfied by "we talked about it" — no shared lemma) via a small **learned classifier** over 3 hand-authored construction-cue pools (`INFO_EXCHANGE_POOL`, `ERRAND_POOL`, `SKILL_TRAIN_POOL`, goal-atoms `goal_cognition`/`goal_activity_engagement`/`goal_skill_practice`, :158-168) plus a WordNet-MWE dictionary lookup for the CONTRADICTS/disengagement half (:391-469, floor coverage 26/29=0.897 on its own representative bank). | **The classifier itself is pre-trained (cached, `get_induced_hypothesis`, :373-385) — no new fitting.** But its 3 pools were hand-authored FOR DesireDB's blog-narrative desire vocabulary (M1/M2/M3-inc1 build history, module docstring lines 1-107), not GLUCOSE/TellMeWhy's. Re-authoring pools that actually cover this corpus's goal vocabulary (physical needs, social goals, safety, etc. — not just cognition/activity/skill) **is a real build step**, not a drop-in. | **Larger IF rebuilt for this domain (+5-15pp plausible), near-zero AS-IS** (its 3 pools are a narrow slice of the GOAL types the causal-type census found — cognition/errand/skill-practice is not the dominant shape of GLUCOSE/TellMeWhy goals). Flag as Tier-2, do not treat as a drop-in. |
| `hdlab/quality_relation.py` `quality_relation` (:287-322), `AXIS_WORDS["engagement"]` (:215-221) | Same shape as `structured_matcher.antonym` — a signed FPE axis for adjective/phrasal-verb opposition. | **Not independently useful here.** Its own docstring (lines 176-221) states the `engagement` axis was seeded **from `goal_outcome_relation.REPRESENTATIVE_DISENGAGEMENT_PHRASES`** — it is a parallel continuous-cosine encoding of the SAME CONTRADICTS/disengagement vocabulary `goal_outcome_relation.mwe_disengage_scan` already covers at 89.7% floor coverage. It does not touch INSTANTIATES/satisfy (the actual gap; see funnel below). | N/A | **~0.** Redundant with an already-well-covered sub-piece; does not address the dominant satisfy-side gap. Do not prioritize for Q1. |

**The measured funnel this fix must move (this cycle's own numbers, `data/exp_genworldmodel_psych_loo_v1/metrics.json`):**
`has_goal` 0.636 (GLUCOSE) / 0.783 (TellMeWhy-GOAL) -> `has_resolved_goal` **0.156 / 0.163** -> `loo_fires`
(LOO-necessary given resolved) **0.025 / 0.022**. Note the LAST step is itself a ~16% multiplicative filter
(0.025/0.156 ≈ 0.16) — **even a perfect resolution detector does not by itself clear the psych-LOO research
note's own pre-registered HARD-PASS bar (>=15% firing)** unless the LOO-necessity-given-resolved ratio also
rises under semantically-correct resolution (untested — flagged as an open sub-question, see Q3's oracle
stage). Honest arithmetic with the estimates above: wiring `structured_matcher` (+2-5pp resolution) moves
0.156->~0.18-0.21; even a generously-rebuilt `goal_outcome_relation` (+5-15pp) moves it to ~0.25-0.35 at best.
Neither, alone or combined, plausibly reaches the resolution rate needed to cross 15% LOO-firing given the
observed 16% multiplicative filter — **this is consistent with, not contradicted by, the literature**: the
external lit-scan's closest precedent task (Chaturvedi, Goldwasser & Daumé 2016, "Ask, and shall you receive?
Understanding Desire Fulfillment in Natural Language Text," AAAI, arXiv:1511.09460 — literally this exact
task, non-lexical desire/evidence fulfillment classification) reports **F1 56.9-74.4 (MCTest) but only
14.3-27.1 (SimpleWiki, the harder open-domain set)** even with a **trained** Latent Structure Narrative Model;
Rahimtoroghi et al. 2017's DesireDB (SIGDIAL, arXiv:1708.09040) needs an LSTM sentence-embedding model to reach
F1 0.70. **A hand-built, untrained glass-box classifier performing in a comparable-or-lower band should be read
as being near the literature's own ceiling for non-neural methods on this exact problem, not as an
under-built organ** — this is the calibration-honest read, not a reason to stop building (structured_matcher
wiring is free and should still land).

---

## Q2 — what the gold labels actually encode (the crux)

**GLUCOSE** (Mostafazadeh, Kalyanpur, Moon, Buchanan, Berkowitz, Biran & Chu-Carroll, EMNLP 2020,
aclanthology.org/2020.emnlp-main.370; on-disk `data/corpora/glucose/PROVENANCE.json`, sampled
`train.jsonl` this cycle — confirms the schema: one worker per row fills 1-3 of 10 dimension slots, each with
a `specificNL`/`generalNL` (Someone_A-schema) pair and a `>Causes/Enables>` or `>Enables>` relation string).
The worker-facing prompt (paper Fig. 5, quoted verbatim by the lit-scan): *"Consider the events that happen
before X (or are likely to happen). Does any of them directly cause X, or simply make it possible (i.e.,
enable it)? Whenever possible, you are encouraged to find the answer from the other sentences in the story.
Remember, there are often no right or wrong answers; just give your intuition."* Cause and Enable were
**collapsed on measured worker disagreement** (§4.1 fn.5) — an inter-annotator-reliability operationalization,
not a philosophical distinction; **Talmy force dynamics and Mackie's INUS condition are cited nowhere in the
paper.** GLUCOSE's own theoretical grounding (§3.3) is explicit: *"Research in cognitive psychology suggests
that humans typically choose which of an event's many causes to cite based on its relevance to the context
(Miller, 2019)"* and *"people explain by appealing to broader theories that enable generalization (Lombrozo,
2006)"* — GLUCOSE is, by its authors' own stated design lineage, a **relevance/best-explanation** dataset.

**TellMeWhy** (Lal et al. 2021, ACL-IJCNLP Findings; on-disk `data/corpora/tellmewhy/PROVENANCE.md`;
`experiments/exp_causal_reasoner_tellmewhy_v1.py:3-4,51-85` confirms the schema: template-generated "Why did
X happen?" questions via spaCy dependency parse of subject/verb/object, answered by crowdworkers who mark
`helpful_sentences` + an `is_ques_answerable` flag). The answer-writer instruction (paper Appendix C.1, quoted
verbatim by the lit-scan): *"You are encouraged to answer in your own words... Answer such a question with
any plausible explanation you can come up with."* The validity bar for the companion rating task: *"An answer
is considered invalid if it does not give a plausible reason for the question asked and states an irrelevant
piece of information instead"* — **plausibility/relevance, not necessity.** Sentence-selection is described as
workers picking *"the sentences from the narrative which influenced their answer"* — **"influenced" is an
associative/relevance term**, never "without which the event could not have happened." No guidance anywhere
addresses excluding the adjacent sentence or preferring the most-specific-vs-most-general cause.

**Adjudication.** Neither protocol's own wording contains the operational signature of counterfactual-necessity
elicitation (no removal/negation test is ever posed to annotators). Both instead instruct **plausible, relevant,
intuitive** explanation — GLUCOSE additionally self-cites Miller 2019 (whose own AI-facing synthesis surveys
Hilton & Slugoski's **abnormal-conditions-focus** model and Hitchcock & Knobe's 2009 "Cause and Norm," *J.
Phil.* 106(11) — a **norm-restricted counterfactual-selection filter**, i.e., you don't test all antecedents
counterfactually, you preferentially test the ones that violate a default/script) and Lombrozo 2006/2007
(*Cognitive Psychology*, simplicity+breadth over raw probability or strict necessity). This gives three
theories, each with a distinct falsifiable prediction the lit-scan formalized:
- **(a) Necessity** (Lewis 1973; Trabasso & van den Broek 1985; Mackie 1965/1974): predicts high agreement only
  when one candidate is uniquely necessary; predicts elevated abstention/disagreement under overdetermination.
- **(b) Norm/abnormality** (Hart & Honoré 1959; Hilton & Slugoski 1986; Kominsky, Phillips, Gerstenberg,
  Lagnado & Knobe 2015, *Cognition*, "Causal superseding"; Hitchcock & Knobe 2009): predicts annotators pick
  the statistically-rare or script-violating candidate over an equally-or-more-necessary but normal background
  condition, and the effect **persists or increases** exactly in overdetermination cases where (a) cannot
  discriminate.
- **(c) Explanatory virtue** (Lombrozo 2006/2007/2016): predicts selection correlates with how much a candidate
  explains (breadth) and how few additional causes it needs (simplicity), independent of raw necessity.

Given the confirmed protocol wording, **(c) is the closer match by explicit design citation, with (b) present
by inheritance** (Miller 2019's synthesis folds Hilton-style abnormality into its relevance account). **(a) is
not what either protocol elicits.** This is the reframing: the arc's own repeated finding — every
generated/typed/structured causal signal (LOO necessity, directed force/psych typing, the ECHO coalition
decision, the SOT-conditioning organ) ties or loses to topical connectivity, position, and result-state
achievement (SOLVED.md cycles 6-13) — now has a **protocol-level mechanistic explanation**, not just an
empirical pattern: topical connectivity approximates breadth/relevance, position approximates script-typicality
(Lombrozo's "broader theories"), and result-state achievement approximates a simple, complete, intuitively
satisfying story-continuation — all three are cheap proxies for the actual (b)/(c)-flavored reward signal,
while LOO-necessity targets a formally different, narrower construct that the annotation instructions never
elicited. (Minor citation correction: the Director's brief cited "Henne et al. 2021" for the action-effect
asymmetry paper; the lit-scan located it as **Henne, Niemi, Pinillos, De Brigard & Knobe 2019**, *Cognition* —
the 2021 date appears to be a mix-up with a related follow-on; flagged, not load-bearing for this note's claims.)

**Concrete measurement to adjudicate the fractions** (per the task's ask, "design a measurement that would
decide what fraction of gold causes each theory predicts"): sample ~150-200 GLUCOSE/TellMeWhy gold
cause-effect pairs; for each, compute (i) LOO-necessity under ORACLE world/goal-state (does removing the
candidate's content, under a hand-verified semantic fold, flip the effect's reachability?), (ii) a
**typicality/abnormality score** for the candidate (reuse `temporal_script_schema`'s p_before frequency as a
script-typicality proxy — a LOW p_before is a script-violation/abnormal event), (iii) a **breadth score**
(how many OTHER effect-relevant facts the candidate's content also supports, reusing `CausalLinkRegister`
query_effect_of counts). Cross-tabulate: if gold selection correlates most strongly with LOW p_before
(abnormality) independent of oracle-necessity, that is direct evidence for (b); if it correlates with breadth
independent of necessity, that is evidence for (c); if oracle-necessity alone predicts selection best, (a)
survives after all and the wall really is pure extraction/coref (the Q111 story). This is a cheap, reusable
diagnostic (no new mechanism, just cross-tabulating already-built organs' outputs against gold) and should be
the FIRST cell built from this note, since it decides which of Q1/Q3/Q4's follow-ons are worth prioritizing.

---

## Q3 — the signal-loss ladder (design, not yet run)

Reuse `experiments/exp_genworldmodel_competition_model_integrator_v1.py` verbatim: `_supports()` (:59-66),
`_fit_weights()` (:125-148, the delta-rule cue-validity learner), `_integrator_hits()`/`boot()` (:151-170) —
each ladder stage is a **CUES-list prefix**, re-fit and re-scored with no other code changes. Population:
TellMeWhy GOAL non-adjacent, **pooled train+validation+test** (n=935, the cycle-12 `script_order_power`
population — already the correctly-powered choice; GLUCOSE non-adjacent as a second population, since Q2's
adjudication may be dataset-dependent).

| Stage | CUES added | Reuse (file:line) | Already-measured marginal (TellMeWhy GOAL) |
|---|---|---|---|
| base | none (majority/random floor) | — | — |
| +topical | `overlap` | `competition_model_integrator_v1.py:64` | SOLVED.md: topical (content-only argmax) 0.2500 vs base 0.2773 (topical is WEAKER than base here — TellMeWhy's topical floor undershoots the multi-cue base) |
| +position | `position` | `:63` | **~0 on TellMeWhy** (cycle-9: earliest/nearest/before_nearest = 0.000, position-USELESS here — a genuine null, report it, don't hide it; this is why the ladder must ALSO run on GLUCOSE where position dominates at 0.694) |
| +result-state | `means_end` (`rs_fire`) | `:65`, `exp_genworldmodel_resultstate_v1.py` | GOAL-subset base 0.2935 -> rollout 0.3804, **+0.0870 CI[0.0217,0.1522]** (already measured, SOLVED.md) |
| +script-order | `script_order` (`temporal_script_schema` p_before) | `exp_genworldmodel_script_order_cue_v1.py` (5th-cue pattern already precedented) | 4cue->5cue **0.499->0.559, +0.060 CI[0.024,0.096]**, load-bearing vs shuffled-script twin (cycle-12, already measured) |
| +goal-resolution STRUCTURAL | `psych_loo` (strict-lemma track_status_thwart) | `exp_genworldmodel_psych_loo_v1.py:100-122` | **~0 (HARD-FAIL, already measured)**: fires 0.022-0.026, does not beat null p95, `+int` delta = 0.0000 exactly (metrics.json above) — CONFIRMS this specific sub-stage contributes nothing today |
| +goal-resolution ORACLE (semantic) | **new, not yet built** | see below | **unmeasured — this cell** |
| gold | — | — | ceiling = 1.0, or (more honest) the datasets' own inter-annotator agreement, which neither this note nor the on-disk PROVENANCE files report a number for — **flag as an unverified ceiling, do not assume 1.0 is achievable even in principle** |

**Cheapest way to get an ORACLE goal-resolution signal (the task's explicit ask):** do **not** build a new
automatic semantic classifier first. `exp_genworldmodel_signal_loss_ladder_v1.py` already established the
right pattern for this exact purpose — it granted the PHYSICAL result-state stage a "PERFECT goal simulator"
by hand-verification (SOLVED.md: "base 0.277 -> +our surface means-end 0.293 -> **+PERFECT goal simulator
0.441**"). Do the same for the psychological register: draw a small sample (n≈100-150) from exactly the
population `psych_loo`'s own diagnostic isolated as the loss point (`has_goal=True AND has_resolved_goal=False`
— the 0.64-0.78 -> 0.16 gap), and **hand-label** (a single annotator pass, a few hours, no model training) for
each item whether ANY later sentence semantically satisfies/thwarts the stated goal, and which one. This is a
gold micro-annotation, not a new mechanism — it upper-bounds what ANY future automatic detector (Q1's
candidates, or a future build) could possibly buy, cheaply and honestly, before investing in the detector
itself. Score it as a 6th cue exactly like the other stages (an oracle-lookup dict keyed by item id, `0.0`
default for un-annotated items so the ladder stays well-defined on the full population).

**Pre-registered prediction for the oracle stage (deflated per calibration):** the marginal on the
**GOAL-subset** should be real and probably sizeable (this is exactly the population psych_loo's own funnel
isolated). The marginal on the **FULL non-adjacent population** is capped by GOAL-type share (40.8%/36.8%,
causal-type census) x the resolution-recovery fraction x whatever fraction of newly-resolved goals are ALSO
LOO-necessary (historically ~16% of resolved goals, though this ratio is untested under oracle-quality
resolution and could differ). Rough estimate: **+0.03 to +0.08 accuracy points on the full population** — a
real, plausibly CI-separable but modest lift, not a wall-closing result. P_deflated = 0.35 for "CI-separated
on the full population"; MIDDLE_BAND (real GOAL-subset marginal, not CI-sep on full population) is the more
likely honest outcome per this estimate.

---

## Q4 — is there a different, better-matched mechanism? Yes: necessity-sufficiency weighted by typicality

The XAIP "why-not"/contrastive-explanation literature (Fox, Long & Magazzeni 2017; Krarup, Cashmore,
Magazzeni & Miller 2019, ICAPS-19 XAIP workshop, "Model-Based Contrastive Explanations for Explainable
Planning") formalizes contrastive explanation as **minimally-different-plan counterfactual comparison** — this
is the SAME leave-one-out/constraint-removal machinery already built and already HARD-FAILing here, wearing a
different name; it does not offer a new mechanism. **It genuinely does exist one level deeper**, in the
norm/normality-weighted actual-causation literature Miller 2019 itself points to:

**Icard, Kominsky & Knobe 2017** (*Cognition* 161, "Normality and actual causal strength") propose a
computable causal-strength measure combining a **necessity** term and a **sufficiency** term, weighted by each
candidate's own **base-rate/typicality**:
```
phi_P(X, Y) = P(X=0) * P^m_{X=0}(Y=0)     [abnormal-candidate weight * necessity: does Y fail when X is removed]
            + P(X=1) * P^r_{X=1}(Y=1)     [normal-candidate weight * sufficiency: does Y occur when X is present]
```
(Formula shape corroborated by two independent secondary descriptions after primary-PDF extraction failed;
symbol-level detail is medium-confidence, structure is high-confidence — flagged per the lit-scan's own
honesty check.) This is independently cross-corroborated by the **Necessity-Sufficiency Model**'s replication
in **Gill, Kominsky, Icard & Knobe 2022** (*Cognition*, "An interaction effect of norm violations on causal
judgment"): abnormal (low base-rate) causes get judged mostly on necessity, normal (high base-rate/on-script)
causes get judged mostly on sufficiency. **Halpern & Hitchcock 2015** ("Graded Causation and Defaults," *BJPS*
66(2)) independently formalizes the same idea inside the structural-model actual-causation framework: add a
normality ordering over possible worlds/contingencies, and grade causal strength by how large a departure from
normality the counterfactual witness requires.

**Why this is the mechanism Q2's finding predicts should matter, and why it is cheap to try:** every ingredient
already exists on this substrate. **Necessity** = `loo_necessity`/`psych_loo` (built, HARD-FAILing alone).
**Sufficiency** = `rs_fire`/means-end achievement (built, the CI-sep GOAL-subset winner) — sufficiency
("does the effect occur given this candidate") is structurally closer to a forward achievement-check than a
removal-check, which is exactly what `rs_fire` already computes. **Typicality/base-rate** = the
`temporal_script_schema` p_before frequency (built, already used as the script-order cue, cycle-11/12) — a
LOW p_before IS a low base-rate/abnormal event in Icard-Kominsky-Knobe's sense. The proposed new cue for the
Competition-Model integrator (`experiments/exp_genworldmodel_competition_model_integrator_v1.py:50`, `CUES`
list) is therefore: `ikn_blend(C_j) = (1 - p_before(C_j)) * loo_necessity(C_j) + p_before(C_j) * rs_fire(C_j)`
— a **typicality-GATED mixture**, not a flat additive term like the other 5 cues. This is a materially
different combination rule from the integrator's current flat additive Competition-Model activation (which
already achieves "synergy" per cycle-10's own finding — this proposal asks whether a literature-motivated
NON-flat combination beats that flat baseline, isolating whether the existing synergy is already capturing
this structure by accident or whether a genuine further lift is available).

**Verdict on Q4 directly:** yes, a genuinely different, well-supported computation exists (necessity-
sufficiency blend weighted by typicality, Icard/Kominsky/Knobe 2017 + Halpern/Hitchcock 2015), distinct from
both topical association and flat LOO-necessity, buildable entirely from already-landed organs. The XAIP
contrastive-explanation literature does NOT offer anything beyond the already-tried LOO shape. Norm theory
(Kahneman & Miller 1986) has **no implemented/algorithmic narrative-text version** in the literature (the
lit-scan found none) — the Icard-Kominsky-Knobe formula is the one genuinely computable bridge. A pure
LM-surprisal proxy for "abnormality" is explicitly flagged by the literature itself as confounded (Bear & Knobe
2016, *Cognition*, "Normality: part descriptive, part prescriptive" — statistical rarity and prescriptive-norm
violation are **dissociable**) — use the script-store's p_before (a descriptive/statistical typicality signal,
already disclosed as such) rather than inventing a surprisal-based "norm violation" score, and do not
over-claim it captures prescriptive norms.

---

## Cheap decisive test

Build, in this priority order (cheapest/most-informative first):
1. **The Q2 adjudication cross-tab** (oracle-necessity vs p_before-typicality vs breadth, against gold
   selection, n≈150-200) — decides which of Q1/Q3/Q4 is worth the next build cycle. No new mechanism, pure
   diagnostic over already-built organ outputs.
2. **Wire `structured_matcher` into `track_status_thwart`'s calls in `exp_genworldmodel_psych_loo_v1.py`**
   (pass `matcher=StructuredMatcher(hub=<landed bridging_inference instance>)` at line 92) — zero cost,
   strict superset, re-run the existing psych_loo eval unchanged to get the exact recovered resolution rate.
3. **The Icard-Kominsky-Knobe typicality-gated cue** in the Competition-Model integrator, on the SAME
   TellMeWhy-GOAL pooled population (n=935) used in cycle-12, with two required info-free twins: (a) shuffle
   which candidate gets the necessity-weight vs sufficiency-weight (breaks the typicality-gating specifically);
   (b) the existing necessity-permutation null (reuse `_fires_null_shuf`, `psych_loo_v1.py:155-177`).

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND)

**1. `structured_matcher` wiring.** HARD-PASS: `has_resolved_goal` rises >=0.03 absolute on either corpus AND
`loo_fires` rises >=0.01 absolute, AND the scrambled-agent/order-shuffle twins still collapse (the new
converse/antonym branch stays agent-bound and order-sensitive — verify it doesn't leak). HARD-FAIL: resolved-rate
rise <0.01 (this cycle's own estimate, most likely outcome) — report as "correct-but-negligible," land it anyway
(it is free and strictly cannot regress by construction), do not re-file as a fix.

**2. Q2 cross-tab diagnostic.** HARD-PASS-for-(b)/(c): gold-selection rate correlates more strongly with LOW
p_before (typicality-violation) or high breadth than with oracle-necessity (report the three correlations/AUCs
side by side). HARD-PASS-for-(a): oracle-necessity dominates the other two predictors — in this case, reverse
this note's recommended priority and re-focus on closing extraction/coref (the Q111 story) instead of trying
Q4's blend. MIDDLE_BAND: no predictor dominates (all three carry partial, overlapping signal) — the honest
read is that real annotators mix theories, and the Q4 blend (which explicitly mixes necessity and sufficiency)
is still the best-motivated next build regardless.

**3. Icard-Kominsky-Knobe typicality-gated cue.** HARD-PASS: CI-beats the current best flat-additive
integrator (cycle-12's 5-cue 0.559 on TellMeWhy, or GLUCOSE's equivalent) on at least one corpus AND beats
BOTH required twins. MIDDLE_BAND: beats its twins (genuinely reading typicality-gated structure) but not
CI-separated over the flat integrator — meaning the existing flat Competition-Model blend already captures
most of this structure via its own learned weights (a real, interesting finding in itself — Bates-MacWhinney
cue-validity learning may already be approximating the typicality-gate). HARD-FAIL: ties or loses to a
same-mean random-mixing-weight twin — the typicality signal (p_before) is not actually informative for WHICH
combination rule to apply, only for direct scoring (already captured by the existing script_order cue).

---

## Cross-thread synthesis

Directly extends and re-answers the open question `research_context_conditioned_cause_selection_2026-09-08.md`
raised (LOO necessity is the 3-literature-convergent mechanism) by adding the piece that note could not have
had without reading the datasets' own annotation protocols: **the mechanism is correct; the target it was
built to hit (necessity) is not what the gold measures (relevance/best-explanation).** Directly extends
`research_psychological_state_register_for_loo_2026-09-08.md`'s organ sweep (ranked `goal_outcome_relation` at
#5, `structured_matcher` not even listed there — this cycle found `structured_matcher` is the **cheaper, already-
wired** option, a correction worth propagating) and its own measured funnel (has_goal/has_resolved/loo_fires),
now given a numeric ceiling estimate for what closing the resolution sub-wall alone can buy (Section Q1). Adds
a genuinely NEW field to this arc's citation base not covered by either prior note: **norm-based/normality-
weighted causal judgment** (Hitchcock & Knobe 2009; Icard, Kominsky & Knobe 2017; Halpern & Hitchcock 2015;
Gill, Kominsky, Icard & Knobe 2022) — Trigger-C adjacency-cascade territory, since Icard/Kominsky/Knobe 2017
appeared only as a passing citation in the prior context-conditioned note and is now the load-bearing formula
for Q4's recommended next build. Confirms (does not contradict) SOLVED.md's cycle-9-through-13 finding that
topical/position/result-state repeatedly beat generated/typed/structured signals — this note supplies the
protocol-level WHY, not a new empirical result.

## Substrate-product implications

If the Q2 adjudication and the Icard-Kominsky-Knobe blend both land as designed, the practical payoff is a
cause-selection engine whose scoring logic matches what everyday causal explanations actually reward — not
"the one strictly-indispensable fact" (which real narrative rarely isolates cleanly) but "the fact that best
explains, in a normal-feeling and complete way, why this happened" — the same standard a person uses when
asked "why did this happen?" In plain terms: right now the system sometimes insists on a narrow, technically-
correct-but-alien notion of "cause" (would this specific fact's absence have literally changed the outcome?)
when real explanations more often reward "what's the most natural, relevant story-fact that accounts for
this?" — and this note found, by reading the exact instructions the human annotators who built our answer key
were given, that the answer key itself was built to reward the second kind of explanation, not the first. The
risk of proceeding: the necessity-sufficiency-typicality blend is this drill's own synthesis of published
formulas (not a pre-built, tested system), so it may still underperform the current flat blend once actually
run — that would still be valuable information (Section Q4's HARD-FAIL case), not wasted effort, because it
would show the existing learned cue-integrator already captures what a hand-derived typicality gate would add.

## Citations (verified count)

Directly verified THIS cycle by 3 dispatched lit-scan lanes (19+25+29 tool-uses, primary-source WebFetch where
possible, search-corroborated where PDF extraction failed — each lane's own honesty-disclosures preserved
above): Mostafazadeh, Kalyanpur, Moon, Buchanan, Berkowitz, Biran & Chu-Carroll 2020 (EMNLP, GLUCOSE, direct
protocol quotes); Lal et al. 2021 (ACL-IJCNLP Findings, TellMeWhy, direct protocol quotes; on-disk
`PROVENANCE.md` author list: Lal, Tang, Ghosh, Chambers, Balasubramanian — the lit-scan's own author-list
summary varied slightly, flagged as a minor citation-transcription uncertainty, not load-bearing); Miller 2019
(*Artificial Intelligence* 267, GLUCOSE-self-cited); Lombrozo 2006 (*TiCS*, GLUCOSE-self-cited) / 2007
(*Cognitive Psychology*) / 2016; Lewis 1973 (*J. Phil.*); Hart & Honoré 1959 (*Causation in the Law*); Hilton
& Slugoski 1986 (*Psych Review*); Kominsky, Phillips, Gerstenberg, Lagnado & Knobe 2015 (*Cognition*); Hitchcock
& Knobe 2009 (*J. Phil.* 106(11), "Cause and Norm"); Henne, Niemi, Pinillos, De Brigard & Knobe 2019
(*Cognition* — corrects the brief's "2021" citation); Lehnert 1981 (*Cognitive Science*, plot units); Goyal,
Riloff & Daumé 2010 (EMNLP/W10-0203, AESOP, patient-polarity verbs); Rashkin, Bosselut, Farra & Choi 2016 (ACL,
Connotation Frames); Ding & Riloff 2018 (NAACL, human-needs categorization); Chaturvedi, Goldwasser & Daumé
2016 (AAAI, arXiv:1511.09460, Desire Fulfillment / LSNM); Rahimtoroghi, Wu, Wang, Anand & Walker 2017 (SIGDIAL,
arXiv:1708.09040, DesireDB); Sap et al. 2019 (ATOMIC, reused); Bosselut et al. 2019 (COMET); Hwang et al. 2020
(COMET-ATOMIC-2020); Fox, Long & Magazzeni 2017 (Explainable Planning); Krarup, Cashmore, Magazzeni & Miller
2019 (ICAPS-19 XAIP workshop); Halpern & Hitchcock 2015 (*BJPS* 66(2), "Graded Causation and Defaults",
formula-medium-confidence per lit-scan's own disclosure); Icard, Kominsky & Knobe 2017 (*Cognition* 161,
"Normality and actual causal strength" — formula shape corroborated by 2 independent secondary sources, not
primary-PDF-verified, disclosed); Gill, Kominsky, Icard & Knobe 2022 (*Cognition*); Kahneman & Miller 1986
(norm theory); Bear & Knobe 2016 (*Cognition*, descriptive/prescriptive normality dissociation); Jahn, Hühn &
Förster 2024 (abnormality-biased counterfactual XAI, tabular-only, paywalled/unverified detail).

Reused-with-attribution from prior on-disk notes (already primary-source-verified there, not re-verified this
cycle): Trabasso & van den Broek 1985; Mackie 1965/1974; Batusov & Soutchanski 2018/2025; Icard, Kominsky &
Knobe 2017 (first surfaced there as a passing citation; now load-bearing here).

Total distinct sources this note directly draws on: **~30** (26 fresh-verified across 3 lit-scan lanes this
cycle, 4 reused-with-attribution). Disk-verified this cycle (not literature): `hdlab/goal_register.py`,
`hdlab/goal_outcome_relation.py`, `hdlab/structured_matcher.py`, `hdlab/quality_relation.py` (full reads);
`data/exp_genworldmodel_psych_loo_v1/metrics.json`, `data/exp_genworldmodel_causal_type_census_v1/metrics.json`
(full reads); `data/corpora/glucose/train.jsonl` (sampled), `data/corpora/tellmewhy/PROVENANCE.md`,
`experiments/exp_causal_reasoner_tellmewhy_v1.py` (schema-verified).

## Calibration

Per mandatory lit-scan calibration policy: Q2's protocol-characterization claims are directly quote-verified
from both primary papers by an independent lit-scan lane — P(protocol characterization accurate) ~0.80
pre-deflation, **deflated to 0.55** (top of band; the INTEGRATED claim — that this explains 15 cycles of
LOO-vs-topical results — is this drill's own synthesis, not stated by either paper). Q4's Icard-Kominsky-Knobe
formula: literature well-established in shape, **P_deflated=0.40, capped** (the specific mapping of
substrate organs onto necessity/sufficiency/typicality terms is this drill's own novel synthesis, and the
formula's own symbol-level detail is only secondary-source-corroborated). Q1's structured_matcher-wiring
recovery estimate: **P_deflated=0.35** for >=3pp; the wiring action itself (zero-cost, strict superset) is
near-certain to be safe to land (P~0.90) independent of whether it clears any accuracy bar.

---

### TLDR

We built a detector that asks "would this exact fact's absence have changed what happened" — a very precise,
narrow kind of cause. We went and read the actual instructions given to the people who wrote our answer key,
and found they were never asked that question. They were told: "just give your intuition" about what plausibly
explains this, and to prefer plausible, relevant, complete-feeling answers. That is a different, more everyday
notion of "cause" — closer to "what's the story-typical, satisfying explanation" than "what's the one
irreplaceable fact." This explains, for the first time with a real reason instead of just repeated results, why
our precise mechanism keeps losing to simpler signals (what's topically connected, what came first, whether the
goal got achieved) on real stories: those simpler signals happen to be cheap stand-ins for the everyday notion
of cause, while our precise mechanism is answering a harder, different question nobody asked for. We also found
a small, free fix (reusing a store we already built) that should recover a little bit of the goal-tracking gap
at zero cost and zero risk, and a genuinely new, published formula (blend "was it necessary" with "was it
enough," weighted by "was it unusual") that fits the everyday notion of cause better than either of our current
approaches — buildable entirely from parts we already have.

### QUESTIONS

None outstanding that block the next build. Open for the Director/owner to decide priority: whether to run the
Q2 cross-tab diagnostic first (decides whether Q1/Q4 are worth building at all, cheapest, ~1 cell) or go
straight to the two concrete builds (structured_matcher wiring, near-zero cost; the typicality-gated integrator
cue, medium cost) in parallel, since the wiring is safe regardless of what the diagnostic finds.

### NEXT STEPS

1. exp_dev: run the Q2 cross-tab diagnostic (oracle-necessity vs p_before-typicality vs breadth against gold
   selection, n≈150-200, reusing `temporal_script_schema` and `CausalLinkRegister` query counts — no new
   mechanism, pure measurement). Decides Q1/Q4 priority.
2. exp_dev: wire `hdlab.structured_matcher.StructuredMatcher` into `exp_genworldmodel_psych_loo_v1.py`'s
   `track_status_thwart` calls (line 92, add `matcher=`), re-run the existing eval unchanged, report the exact
   `has_resolved_goal`/`loo_fires` delta. Zero cost, land regardless of outcome.
3. exp_dev: build the oracle goal-resolution micro-annotation (n≈100-150, hand-labeled, ~1-2 hours), add as a
   6th ladder stage in the Competition-Model integrator, report the isolated marginal on GOAL-subset and full
   population separately (per this note's pre-registered +0.03-0.08 full-population estimate).
4. exp_dev: build the Icard-Kominsky-Knobe typicality-gated necessity/sufficiency cue
   (`ikn_blend = (1-p_before)*loo_necessity + p_before*rs_fire`) as a new arm in
   `exp_genworldmodel_competition_model_integrator_v1.py`, with the two required info-free twins, on the
   pooled TellMeWhy-GOAL (n=935) and GLUCOSE non-adjacent populations.
5. Do NOT prioritize `goal_outcome_relation.py` pool re-authoring or `quality_relation.py` for Q1 until step 1's
   diagnostic and steps 2-3's results are in — both are real but smaller/costlier levers than the wiring +
   oracle-ladder + typicality-blend sequence above.
