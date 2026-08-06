# FORMALIZE-drill: the continuous LEARN-WORD-VALENCE-FROM-CONSEQUENCE loop (2026-08-06)

Research role, spec-only cycle (deliverable = design + pre-reg, NOT a build/run). Direct continuation
of `notes/SYNTHESIS_grounding_wall_definitive_2026-08-06.md` and
`notes/research_anchor_propagate_oov_outcome_verb_valence_2026-08-06.md` (P_deflated=0.42, delivered
this session) -- USER explicitly chose the EARNED continuous-consequence version over that WordNet
static-propagate design ("WordNet drops to AT MOST an optional bootstrap accelerator... assess
honestly whether WordNet is needed at all"). This note supersedes the WordNet-anchor-propagate
PROPOSE-mechanism as the primary direction; the anchor_propagate pre-reg is left on disk as a
standing alternative, not deleted.

Every code claim below is a direct read of the file/line on disk this session (files read in full or
targeted-section: `experiments/exp_self_extension_loop_v1.py`,
`experiments/exp_self_extension_grounded_realprose_v1.py`,
`experiments/exp_grounded_appraisal_sim_earned_v1.py`, `hdlab/context_grounded_valence.py`,
`hdlab/goal_typing.py` (all 1259 lines), `hdlab/verb_lexical_similarity.py` (full),
`hdlab/self_improving_loop.py` (`decide_keep_or_revert`/`ABSTAIN_BAND_DEFAULT`),
`experiments/exp_bridge1_governor_grounding_v1.py` (`GOVERNOR_VERB_CLASS` definition),
`experiments/exp_pfc_gate_cfrpe_trained_v2.py` (header/contract), plus a live diagnostic corpus scan
(see Section 7) over `data/corpora/{little_women,anne_of_green_gables,tom_sawyer,wizard_of_oz}` and a
direct re-derivation of `experiments/data/goal_bearing_modern_eval_v1.jsonl`'s corpus provenance.

---

## HEADLINE

**A non-circular, WordNet-free consequence-learning design exists and is buildable by reusing four
already-validated owned organs (`hdlab.goal_typing.find_desired_state`/`congruence_decision`/
`lexicon_predict`, `hdlab.verb_lexical_similarity.register_acquired_outcome`,
`hdlab.self_improving_loop.decide_keep_or_revert`, and the self-extension loop's multi-pass
read-mint-reread CONTROL STRUCTURE) plus three small, honestly-flagged new generalizations (a
window-scoped extension of `congruence_decision`/`lexicon_predict` from one sentence to a multi-
sentence outcome window, a referent-linked OOV-credit-target scan, and a 3-way POS/NEG/NEUTRAL
vote-margin consolidation rule). The reward-earned RL appraisal family (`exp_grounded_appraisal_
sim_earned_v1` / `pfc_gate_cfrpe_trained_v2` / `context_grounded_valence`) is NOT the right wire for
this increment and should NOT be used -- Section 3 shows why with a direct code-read, not an
assumption. The teacher signal instead comes directly from `congruence_decision`'s own existing,
already-production, purely-structural MET/UNMET verdict, corroborated by the independent flat-lexicon
`lexicon_predict` -- this is genuinely the "minimal alternative" the task itself flagged as plausible,
and the code confirms it is not only plausible but preferable. WordNet is NOT needed anywhere in this
design (Section 8). A live corpus scan (Section 7, not a guess) over the 4 real novels finds 1,641
goal-clear sentences (6.6% of 24,831), of which 848 (51.7%) already have a computable teacher signal
using ONLY today's ~90-word seed lexicon -- a genuine, disk-measured bootstrap floor. The lit-scan
this session (Section 9) found NO existing literature that combines cross-situational word learning
with goal-outcome-polarity credit assignment as one account -- this design is a genuine cross-
component SYNTHESIS of independently-established pieces (cross-situational statistical learning,
"propose-but-verify" single-hypothesis-per-exposure credit assignment, Behrend's 1990 result-verb
bias, Tomasello's intention-reading account, light-verb theory), not an instantiation of a settled
paradigm -- flagged honestly, not overclaimed, and pushes the P_deflated estimate down accordingly
(Section 11).

---

## 1. Brain -> organ -> engine map (FORMALIZE discipline: SHAPE / POSITION / METRIC)

| Component | Brain (from the prior 2 drills this session) | Owned organ / engine piece | Reused verbatim / new |
|---|---|---|---|
| Goal representation | PFC goal-maintenance (DMN/mPFC agent-goal rep, Trabasso goal-plan analysis) | `hdlab.goal_typing.find_desired_state` (GOAL_GOVERNING_PASS-governed purpose-infinitival extraction) | **VERBATIM, unchanged.** Already production; this design adds zero new goal-detection logic. |
| Consequence / outcome evaluation | Not a felt reward per se for THIS increment -- see Section 3's verdict that the RL-appraisal family is the WRONG brain analogy here; the better analogy is symbolic PLAN-MONITORING (does the observed world-state satisfy the maintained goal-representation? -- Miller/Cohen 2001 PFC cognitive-control monitoring, NOT OFC/vmPFC valuation) | `hdlab.goal_typing.congruence_decision` (Signal A, class-relation + referent-linking) + `lexicon_predict` (Signal B, flat bag-of-words) | **VERBATIM logic, NEW scope.** Both functions exist and are production; this design generalizes their SCOPE from one outcome sentence to a multi-sentence window (Section 4) -- the class-relation/referent-linking/lexicon-membership MECHANISMS themselves are unchanged. |
| Novelty / mint trigger ("is this word new to me?") | Hippocampal novelty detection is graded (prediction-error-based) for STRUCTURE, but for a single LEXICAL ITEM the relevant signal is simply "have I mapped a meaning to this phonological form yet" -- a binary lexical-access gate (Levelt 1989 lexical access; not a graded residual) | `in_lexicon(lemma, "outcome")` (existing, `hdlab/verb_lexical_similarity.py`) | **NOT `predictive_coding.threshold_gate`/`residual_magnitude`.** Deliberately NOT reused (see Section 2) -- the self-extension loop needed a graded residual because "novelty of a causal-structure signature" has no natural discrete membership test; "novelty of a WORD" does (OOV-of-lexicon), so the residual apparatus would be unnecessary machinery here. |
| Cross-situational accumulation / anti one-shot-drift | Not single-trial; verb-island / propose-but-verify accounts (Section 9) both require MULTIPLE exposures before a form-meaning mapping is trusted | `hdlab.self_improving_loop.decide_keep_or_revert` / `ABSTAIN_BAND_DEFAULT` ARCHITECTURE (best-candidate-must-clear-a-margin-above-alternative, pure function of aggregated deltas) + `exp_self_extension_loop_v1.MIN_CONFIRM` PATTERN (>=N independent confirmations before consolidation) | **PATTERN reused, not the literal function call.** `decide_keep_or_revert` is a 2-way (adopt-best-or-abstain) rule; this design needs a 3-way split (POS/NEG/**NEUTRAL as an explicit, not merely absent, outcome** -- Section 4.4). A new small function implements the SAME abstain-band architecture generalized to 3 outcomes; flagged as new code, not silently claimed as a reused call. |
| Multi-pass "read -> update -> re-read" | Neocortical slow interleaved consolidation across sleep/replay cycles; NELL's CPL "promotion requires re-scanning with the grown vocabulary" | `exp_self_extension_loop_v1`/`exp_self_extension_grounded_realprose_v1`'s overall loop CONTROL STRUCTURE (read -> gate -> mint -> consolidate -> **re-read**) | **VERBATIM structural reuse of the CONTROL FLOW, new per-pass mechanism.** This is the single most direct engine-reuse point (Section 5) -- newly-grounded words feed back into Signal A automatically (existing Tier-3 wiring, zero new code), so a second corpus pass computes MORE teacher verdicts than the first. This is the design's actual "loop." |
| Write-back / consolidated long-term store | Hippocampal-to-neocortical systems consolidation (the word's meaning becomes part of stable semantic memory) | `hdlab.verb_lexical_similarity.register_acquired_outcome` / `ACQUIRED_OUTCOME_VERB_FEATURES` | **VERBATIM, unchanged.** Same write-back target the anchor_propagate design also planned to use -- this is the one piece both candidate designs agree on. |
| Consumer (does the grounded word matter for comprehension) | PFC goal-outcome congruence evaluation | `hdlab.goal_typing._verb_classes`'s Tier-3 `_acquired_pole_sentinel` + `_class_relation`'s pole-comparison branch (built in increment 1b, confirmed by direct code read, lines 559-616 of `goal_typing.py`) | **No gap, already built and wired.** This is why the design needs ZERO new consumer-side plumbing -- increment 1b already built the exact overlay-consumption path this design populates. |

---

## 2. Why the self-extension loop's NOVELTY-RESIDUAL apparatus is deliberately NOT reused

`exp_self_extension_loop_v1.py`'s mint trigger is `pc.threshold_gate(pc.predict(W_seed, obs), ...,
threshold=RESIDUAL_THRESHOLD)` -- a graded prediction-error residual against a Hebbian-written schema
library, needed because the space of possible NEW CAUSAL-STRUCTURE SIGNATURES has no natural discrete
membership test (a signature is a set of feature atoms, and "is this signature novel" is inherently a
distance-from-known-templates question). Word-level novelty has a much crisper, already-built test:
`hdlab.verb_lexical_similarity.in_lexicon(lemma, "outcome")` returns `False` for any lemma absent from
`OUTCOME_VERB_FEATURES` (Tier-1/2) and `ACQUIRED_OUTCOME_VERB_FEATURES` (Tier-3) -- a deterministic,
zero-threshold-tuning binary gate. Reusing the residual machinery here would add an unnecessary
threshold-calibration risk (as the self-extension loop's own `RESIDUAL_THRESHOLD=0.25` required
explicit pre-registered calibration against a harm/goal_block/noise residual spread) for no benefit.
This is an intentional simplification, named explicitly so it does not read as an oversight.

---

## 3. THE REWARD/CONSEQUENCE WIRE -- verdict on the make-or-break question

**Verdict: use `congruence_decision`'s own structural MET/UNMET verdict directly as the consequence
label. Do NOT wire `exp_grounded_appraisal_sim_earned_v1` / `pfc_gate_cfrpe_trained_v2` /
`hdlab.context_grounded_valence` into this increment.** Three independent, disk-grounded reasons:

1. **The prior session's own increment-1b finding already proved the RL-theta path is redundant for
   this exact payload.** `hdlab/goal_typing.py`'s own module docstring (`goal_congruence_appraisal_
   type`, lines 1064-1097) states plainly: "unlike increment 1's downstream caller) NO reward-theta
   lookup: the caller maps RECIPROCITY->POS / BLOCK_HIGH->NEG directly (increment 1b, Section 1: the
   reward-theta was a fixed 2-value sign constant, dropped as proven-redundant, not a capability
   loss)." This is not a re-interpretation of a prior finding -- it is the SAME code path this design
   would otherwise re-wire, and it was already measured to contribute zero word-specific bits.
2. **`pfc_gate_cfrpe_trained_v2` is a structurally unrelated mechanism.** Direct read of its header
   (`experiments/exp_pfc_gate_cfrpe_trained_v2.py:1-80`): this is a Go/NoGo ACTION-SELECTION gate for
   PLANNING (successor-representation/TD-trained reach-toward-goal scoring over a substrate codeword
   space), unrelated to lexical outcome-verb valence. It is part of this substrate's `pfc_gate_*`
   basal-ganglia-gating family, not part of the goal-outcome-congruence lineage. The prior session's
   own docs used "`pfc_gate_cfrpe_trained_v2` / `grounded_appraisal_sim_earned`" as loose shorthand for
   "the substrate's RL-earned-appraisal family" generically -- a direct code read shows these are two
   genuinely different mechanisms (planning-gate vs. situation-appraisal), and NEITHER is the right
   wire for word-valence credit assignment.
3. **`context_grounded_valence`'s governing mechanism is gated by its OWN separate closed lexicon,
   not word-identity-independent.** Direct read of `experiments/exp_bridge1_governor_grounding_v1.py`
   (lines 82-90): `GOVERNOR_VERB_CLASS` is built from `TRAIN_HARM_VERBS + TEST_HARM_VERBS` /
   `..._HELP_VERBS` / `..._NEUTRAL_VERBS` -- a hand-labeled physical-harm/help governor-verb list,
   structurally identical in kind (a closed hand lexicon) to `hdlab.goal_typing.CLASS_REGISTRY`, just
   scoped to a DIFFERENT semantic domain (physical harm/help events, not abstract goal-attainment). If
   the OOV outcome verb this design wants to ground (e.g. "waste") is also OOV of `GOVERNOR_VERB_
   CLASS`, `context_grounded_valence.score_item`'s governor stage returns `gclass="UNK"` and falls
   through to the animacy-driven event-assembly stage, whose own force-verb list
   (`FORCE_CLASS_HARM_REAL`) is explicitly documented in `hdlab/context_grounded_valence.py`'s module
   docstring as "a closed, test-fitted hand list." So this pipeline does NOT solve the general-OOV-verb
   problem either -- it is a differently-scoped niche (physical harm/help with WordNet-animacy
   generality on the PATIENT noun, not the verb), not a lexically-general teacher signal.

**This is a genuine negative finding worth stating plainly, per the task's own instruction:** the
RL-earned appraisal family, while real and validated on its own terms (Section headline of the prior
SYNTHESIS doc), is the WRONG brain analogy for this specific increment. The better brain analogy for
"does the observed outcome satisfy the maintained goal" is symbolic PFC plan-monitoring/goal-outcome
comparison (Miller & Cohen 2001 cognitive control; MEDIUM confidence, canonical, not independently
re-verified this cycle), which is exactly what `congruence_decision`'s class-relation + referent-
linking machinery already IS -- a structural comparison, not a felt valuation. Using it directly is
not a downgrade from "true reward learning" to "mere heuristic" -- it is choosing the brain-analogous
mechanism that actually matches this sub-problem, per the standing discipline of picking the right
brain STRUCTURE for the job (not defaulting to whichever earned-reward organ is already on the shelf).

---

## 4. CREDIT ASSIGNMENT -- the design, precisely

### 4.1 Two independent teacher signals (the self-extension loop's "two independent views" PRINCIPLE, reused architecturally)

`hdlab/goal_typing.py` already contains two mechanically DIFFERENT ways to compute an outcome
sentence's MET/UNMET verdict, already composed as PRIMARY+fallback in `congruence_with_lexicon_
fallback` (lines 888-898):

- **Signal A = `congruence_decision`** (class-relation via `CLASS_REGISTRY`/`OPPOSED_PAIRS` +
  discourse-entity referent-linking via `_referent_links` -- pronoun-coref and shared-feature-cosine
  tiers). Structural, referent-aware, precise but narrow (abstains whenever no class-related,
  referent-linked candidate exists).
- **Signal B = `lexicon_predict`** (flat token-set membership against `V2_OUTCOME_UNMET`/`_MET`, no
  referent-linking, no class relation -- a cruder, sentence-wide bag-of-words scan).

These are genuinely different failure modes (A can mis-link referents or be silent when no
class-registry verb is present; B can be confused by ANY V2-lexicon word appearing anywhere in the
sentence, referent-linked or not). This design reuses this EXISTING pair, not as
PRIMARY-then-fallback (its production role today) but as an **AND-gate cross-check** for training-
signal purposes: an episode's teacher verdict is trusted only when Signal A and Signal B *agree*.
This is the direct structural analog of `exp_self_extension_grounded_realprose_v1`'s two-independent-
grounded-views architecture (residual-proposes / discourse-cue-disposes) -- same PRINCIPLE (require
agreement of two disjoint mechanisms before trusting a signal), different concrete instantiation
(two already-existing goal-congruence signal sources instead of a residual + a discourse-connective
lexicon).

### 4.2 Window generalization (new, small, honestly flagged)

Both `congruence_decision` and `lexicon_predict` are currently scoped to a SINGLE outcome sentence
(`congruence_outcome_valence` splits a passage into `sents[:-1]` / `sents[-1]`). The credit-assignment
design needs a WINDOW (goal sentence + next `W` sentences, `W` pre-registered = 3, matching the
diagnostic scan in Section 7) because a real narrative's outcome is often stated across more than one
sentence (a vivid/rare verb followed by a plain restatement, or vice versa) -- this is the design's
own answer to "how does an OOV verb's episode ever get a teacher label when it's the ONLY relevant
verb in its own sentence." Concretely: `find_actual_state_candidates` and `lexicon_predict`'s
tokenization are called across the CONCATENATED window text rather than one sentence; this is a small,
mechanical generalization of an EXISTING function's scope, not a new mechanism. Flagged as **NEW code
(small)**, not literal reuse, for FORMALIZE-discipline honesty.

### 4.3 The credit-assignment rule itself (answers the task's central question directly)

For a goal-clear sentence `g` (`find_desired_state(g)` returns `desired = {referent, classes,
verb_lemma}`) and its window `W_g` = `g` + next `W` sentences:

1. Compute `teacher_verdict = Signal_A(W_g)` if `Signal_A(W_g) in {MET, UNMET}` **and**
   `Signal_A(W_g) == Signal_B(W_g)`; else `ABSTAIN_EPISODE` (no training signal this window). Two
   agreement conventions are distinguished and pre-registered separately (Section on non-circularity
   below): Signal-B-SILENT (returns `NONE`) while Signal-A fires counts as agreement (B simply lacked
   the vocabulary to detect it, not a contradiction); Signal-B firing the OPPOSITE polarity from Signal
   A is always a hard disagreement -> abstain.
2. Scan `W_g` for CREDIT-TARGET candidates: tokens OOV of the FULL lexicon (`in_lexicon` false for
   Tier-1/2/3 all) whose LOCAL CLAUSE referent -- extracted with the SAME `_np_last_content` NP-head
   logic `find_desired_state`/`find_actual_state_candidates` already use, tried at BOTH the
   pre-verb-subject position and the post-verb-object position (since an OOV verb's `SUBJECT_IS_
   REFERENT_CLASSES`/`OBJECT_IS_REFERENT_CLASSES` membership is, by definition, unknown) -- **LINKS**
   (via `_referent_links`, the SAME literal/pronoun-coref/shared-feature-cosine tiers) to `desired[
   "referent"]` (the GOAL's own referent, not necessarily the SAME clause as whichever known verb
   produced the teacher verdict in step 1). **This is the direct, disk-grounded answer to "how is the
   negative signal attributed to the outcome verb specifically, not savings/buy/bystanders": credit
   requires STRUCTURAL referent-linkage to the goal's own theme, using the identical machinery that
   already prevents `congruence_decision` from over-linking unrelated nouns (its own
   `D-unmet`/`M-unmet` precision-guard cases, cited in the prior session's promotion docstring) --
   "savings" and "buy" are excluded not by a hand-written stopword list but because they do not
   independently satisfy the SAME referent-linking test a real candidate must clear.**
3. If a `teacher_verdict` exists (step 1) AND >=1 credit-target lemma is found (step 2): record one
   `(lemma, teacher_verdict)` exposure per credited lemma for this window. (Rare multi-candidate
   windows credit ALL qualifying lemmas -- a conservative choice that risks occasional bystander
   mis-credit, mitigated by cross-situational accumulation below, not eliminated at the single-window
   level; named as a known imprecision, not hidden.)

### 4.4 Cross-situational accumulation + 3-way consolidation (POS / NEG / **explicit NEUTRAL**)

Per-lemma exposure counts (`pos_votes`, `neg_votes`) accumulate across the ENTIRE non-excluded corpus
pass (exclusion defined in Section 6). Consolidation (new function, ARCHITECTURE reused from
`decide_keep_or_revert`'s "best-candidate-must-clear-a-band" pattern, not the literal 2-way call):

```
total = pos_votes + neg_votes
if total < MIN_CONFIRM:            -> PENDING (insufficient data, correctly stays OOV/abstaining)
margin = (pos_votes - neg_votes) / total
if margin >= NEUTRAL_BAND:         -> register_acquired_outcome(lemma, "POS")
elif margin <= -NEUTRAL_BAND:      -> register_acquired_outcome(lemma, "NEG")
else:                              -> GROUNDED_NEUTRAL (do NOT register -- correctly stays OOV)
```

`GROUNDED_NEUTRAL` and `PENDING` are downstream-BEHAVIORALLY IDENTICAL (neither ever calls
`register_acquired_outcome`, so both leave the lemma correctly non-contributing to any pole decision
-- exactly the safe behavior a light/support verb should have). They are tracked as SEPARATE
bookkeeping categories ONLY so the pre-reg's light-verb-neutral-correctness claim (Section 6, task's
"crucial payoff") can be MEASURED as "the mechanism actively recognized balance with enough data," not
conflated with "the mechanism never got enough data to say anything." This directly targets the task's
explicit ask: light/support verbs (`be, go, make, give, take, carry, ...`) that co-occur with BOTH MET
and UNMET episodes roughly equally should land in `GROUNDED_NEUTRAL`, not merely `PENDING`.

`MIN_CONFIRM` and `NEUTRAL_BAND` are pre-registered in the companion pre-reg (Section: config),
fixed BEFORE any run, per this module family's own standing "not tuned post-hoc" discipline.

---

## 5. BOOTSTRAP -- does learning expand outward, and how small can the seed be?

**Confirmed by direct code read, zero new plumbing required:** `_verb_classes` (the function
`find_actual_state_candidates`/Signal A depend on) already consults the Tier-3 `ACQUIRED_OUTCOME_
VERB_FEATURES` overlay via `_acquired_pole_sentinel` (`hdlab/goal_typing.py:559-587`, built in
increment 1b). This means a lemma grounded by THIS design's consolidation step automatically becomes
"known" to Signal A for every SUBSEQUENT window scanned -- the bootstrap loop requires no new wiring
on the consumption side.

Order-dependence matters, though: a single linear pass cannot let a LATER-discovered word help an
EARLIER-scanned window. This is exactly why the self-extension loop's **multi-pass read -> mint ->
re-read control structure** (Section 1's most direct reuse point) is the right engine to borrow: run
`N_PASSES` (pre-registered cap, e.g. 3) full corpus passes; each pass's newly-consolidated words feed
Signal A for the NEXT pass, so the computable-window rate should rise monotonically and plateau (a
concrete, MEASURABLE prediction, not just an assertion -- see the pre-reg's bootstrap-curve reporting
requirement). `lexicon_predict` (Signal B) does NOT automatically pick up Tier-3 words (it only checks
the flat, hardcoded `V2_OUTCOME_UNMET`/`_MET` sets) -- this is a deliberate, honestly-flagged asymmetry:
the AND-gate (Signal A and Signal B agree) is the bar for MINTING a genuinely NEW word; once a word is
minted, it joins the "known" pool for Signal A alone in later passes/consumption, exactly as any other
Tier-1/2 word already does. This is not a loophole -- Tier-1/2 words were never required to pass a
Signal-B check either; the two-signal AND-gate is specifically the entry bar for TRUSTING A NOVEL
CROSS-SITUATIONAL SIGNAL, not a permanent double-check every consumption must repeat.

---

## 6. Anti-drift / non-circularity (load-bearing controls)

1. **EVAL-PASSAGE EXCLUSION (critical, concrete, disk-verified necessity).** Directly re-derived this
   session: 34 of the 44 items in `experiments/data/goal_bearing_modern_eval_v1.jsonl` are drawn from
   EXACTLY the 4 novels this design's corpus scan uses (`little_women` 12, `anne_of_green_gables` 12,
   `tom_sawyer` 5, `wizard_of_oz` 5). The learning pass MUST exclude the exact source line-ranges the
   eval file's own `line_citation` field identifies (e.g. `"little_women.clean.txt:~1945-1981"`),
   expanded by a safety margin (`+/- 50` lines, since citations are `~`-approximate) -- built directly
   from data already on disk, not invented. Any sentence whose originating line falls inside an
   excluded range is dropped from the learning pass, for ALL 4 corpora. This is a MANDATORY gate, not
   an optional nicety -- without it, "held-out" scoring against the 36-item eval would be trivially
   contaminated by direct training-passage overlap.
2. **LABEL-SCRAMBLE control.** After computing all `(lemma, window, teacher_verdict)` triples,
   permute `teacher_verdict` labels across windows (fixed seed) BEFORE consolidation; re-run
   consolidation on the scrambled labels. Score the resulting `ACQUIRED_OUTCOME_VERB_FEATURES` against
   the (excluded, held-out) 36-item eval's gold polarities -- must collapse toward chance. This is the
   single most important control: if scrambling the teacher labels does NOT collapse accuracy, the
   mechanism is not actually learning from the consequence signal (genuinely circular/artifactual).
3. **RANDOM-CREDIT ablation.** Replace step 4.3's referent-linked credit-target selection with a
   RANDOM OOV-token choice from the same window (fixed seed) -- must perform WORSE than the real
   referent-linked design. Isolates that STRUCTURAL referent-linkage (not mere window co-occurrence)
   is load-bearing for credit assignment, directly testing the task's "not savings/buy/bystanders"
   concern empirically, not just by design argument.
4. **SIGNAL-A-ONLY / SIGNAL-B-ONLY ablations.** Drop the AND-gate; run consolidation off each signal
   alone. Report each arm's noise/precision relative to the AND-gated design -- isolates that DUAL-
   SIGNAL AGREEMENT (not either mechanism alone) drives precision.
5. **LIGHT-VERB-NEUTRAL canary (the task's "crucial payoff," pre-registered as a named success
   criterion).** A fixed list of light/support verbs, drawn directly from this session's own corpus
   scan's top co-occurring OOV candidates (Section 7) intersected with the anchor_propagate note's own
   light-verb list: `be, have, do, say, try, look, feel, want, think, make, come, go, find, ask, seem,
   begin, mean, know, see, tell, get, put, take, give, carry, buy`. Measure the fraction of this canary
   set that reaches `MIN_CONFIRM` exposures AND lands in `GROUNDED_NEUTRAL` (not spuriously POS/NEG-
   locked, not merely stuck PENDING). This is a DIRECT test of the credit-assignment design's central
   structural claim (light verbs co-occur with both MET and UNMET episodes roughly equally, so a
   genuinely-working cross-situational tally should wash them out, not lock them).

---

## 7. DATA SUFFICIENCY -- measured, not guessed

A read-only diagnostic scan (this session, using ONLY existing `hdlab.goal_typing` primitives --
`find_desired_state`, `_verb_classes`/`CLASS_REGISTRY` membership, `lemma_verb` -- no new mechanism)
over the 4 real novels (`little_women` 186,112 words, `anne_of_green_gables` 102,263,
`tom_sawyer` 70,800, `wizard_of_oz` 39,648; ~399K words combined), window `W=3`:

| Metric | Value |
|---|---|
| Total sentences (4 novels) | 24,831 |
| Sentences firing `find_desired_state` (goal-clear anchors) | 1,641 (6.6%) |
| Goal-windows with >=1 ALREADY-KNOWN (Tier-1/2) outcome-class verb present | 848 / 1,641 (**51.7%**) |
| Unique OOV-candidate lemmas found in these windows (crude token-shape heuristic, see caveat) | 2,513 |
| ...with >=2 window co-occurrences | 1,501 |
| ...with >=3 | 1,050 |
| ...with >=5 | 638 |

**Honest caveat on this scan's precision:** the OOV-candidate detector uses a crude token-shape
heuristic (`lemma_verb(tok) != tok or tok.endswith(("ed","ing"))`), not a POS tagger, so the raw
2,513-lemma figure includes real lemmatizer noise (non-verb tokens like "thing"/"something"/"eyes"/
"always"/"nothing"/"anything"/"girl" appear in the top-30 exposure list alongside genuine verbs). The
TRUE learnable-content-verb count after (a) proper POS filtering, (b) the Signal-A/Signal-B agreement
gate, (c) the referent-linking credit-target filter, and (d) `MIN_CONFIRM` will be substantially
smaller than 638 -- this scan establishes the ORDER OF MAGNITUDE and the bootstrap-floor number
(51.7%), not a final learnable-verb count; the pre-reg's actual run will report the real, filtered
number.

**A striking, disk-grounded confirmation, not an artifact of the crude heuristic:** the top-30
most-exposed OOV candidates combined across all 4 novels are DOMINATED by exactly the light/support
verbs both this design and the prior anchor_propagate note independently flagged as unlearnable-at-
the-verb-level: `be`(2163), `have`(639), `say`(616), `try`(330), `do`(285), `look`(206), `feel`(184),
`want`(179), `think`(177), `make`(168), `come`(166), `go`(155), `find`(135), `ask`(132), `seem`(130),
`begin`(129), `mean`(114), `know`(109), `see`(105), `tell`(102). This is exactly the traffic the
`GROUNDED_NEUTRAL` mechanism (Section 4.4) must correctly absorb -- real narrative text's most
frequent goal-window co-occurrences ARE the light verbs, so the neutral-convergence gate is not a
minor edge case, it is the DOMINANT case this design must get right to avoid being swamped by noise.

---

## 8. WordNet -- honest necessity verdict

**Not needed anywhere in this design.** Every mechanism above (`find_desired_state`, `congruence_
decision`, `lexicon_predict`, the referent-linking tiers, the credit-assignment scan, the consolidation
rule, the multi-pass bootstrap) is built entirely from already-owned, WordNet-free organs (`hdlab.
coreference_resolver`, `hdlab.lexical_similarity` -- a McRae-style hand+corpus feature lexicon, NOT
WordNet-sourced, confirmed by direct prior-session code read -- `hdlab.thematic_role_labeler`,
`hdlab.verb_lexical_similarity`). The ONE place WordNet (or, more precisely, ANY part-of-speech
tagger) could serve as an OPTIONAL accelerator is candidate-quality filtering in step 4.2's OOV-token
scan (Section 7's own crude heuristic produces non-verb noise) -- but a plain POS tagger already used
elsewhere in this substrate (`hdlab/context_grounded_valence.py`'s `_tokenize_and_tag`, `nltk.pos_tag`
with the universal tagset) accomplishes the SAME filtering without WordNet specifically, and is already
an adopted dependency with zero additional install/scope risk. **Recommendation: do not add a WordNet
dependency to this design at all; if candidate-filtering quality becomes a measured problem in the
actual run, reach for `nltk.pos_tag` (already used, simpler, no polarity-relevant baggage), not
WordNet.** This directly answers the task's explicit request to assess WordNet necessity honestly --
the anchor_propagate design (P_deflated=0.42) genuinely needs WordNet as its core relatedness channel;
this design does not need it for anything load-bearing.

---

## 9. Cross-thread synthesis + literature calibration (lit-scan this session, Sonnet sub-agent, generic terms)

A targeted lit-scan (this session, query-privacy-compliant generic terms) was run specifically because
this design's "learn verb valence from cross-situational goal-outcome consequence" framing is NOT
covered by the prior 3 lit-scans this session (which covered valuation content-blindness, the
but-connective ceiling, and the developmental origin of loss-grounding -- adjacent but not this
specific mechanism). Findings, confidence-flagged per the lit-scan-calibration discipline:

- **Cross-situational statistical word learning** (Yu & Smith 2007, *Psychological Science*; Smith &
  Yu 2008, *Cognition* 106) -- HIGH confidence this is a real, established paradigm, but it is
  overwhelmingly NOUN/object-reference work; verb extensions (Scott & Fisher 2012) exist but are a
  smaller, later offshoot (MEDIUM confidence). The credit-assignment mechanism this literature
  actually proposes -- **"propose-but-verify"** (Trueswell et al. 2013; Stevens et al. 2017): the
  learner stores only ONE hypothesis per exposure and confirms/rejects it against later evidence,
  rather than accumulating soft associative weight over all co-occurring candidates -- is a striking,
  independently-arrived-at structural match to THIS design's own per-window single-credit-target
  scan + cross-episode consolidation (Section 4.3-4.4), even though the lit-scan did not find this
  design's specific goal-outcome-polarity framing described anywhere. HIGH confidence on
  propose-but-verify as the closest developmental analog to this design's credit-assignment shape.
- **Behrend (1990)** -- 3-year-olds show a "result-verb bias," expecting distinct RESULT STATES to
  license distinct verb labels. This is the most directly on-point citation found: it establishes that
  children's verb learning is genuinely sensitive to outcome/result state, not just argument
  structure. MEDIUM-HIGH confidence (a real, specific finding, not independently re-verified beyond
  this cycle's search).
- **Tomasello's verb-island hypothesis** (*First Verbs* 1992, *Constructing a Language* 2003) is about
  SYNTACTIC argument-structure generalization, NOT result/outcome semantics -- HIGH confidence this
  citation is real and well-established, but it does not directly support this design's outcome-
  polarity framing; noted honestly rather than stretched to fit (Ninio's "No Verb Is an Island" is a
  live contestation of the strict verb-island claim, flagged for completeness).
- **Tomasello's intention-reading account / Bloom (2000)** -- social-pragmatic word learning via
  inferring communicative/goal intent, plus the infant goal-reasoning literature (Woodward,
  Hamlin/Kuhlmeier helper-hinderer paradigms establishing pre-verbal success/failure representation)
  -- MEDIUM-HIGH confidence on the components, but **the lit-scan explicitly could NOT find literature
  that combines goal-satisfaction detection with cross-situational VERB-POLARITY learning as one
  account** -- flagged as a genuine gap this design bridges, not a citation this design instantiates.
- **RL/credit-assignment framing specifically** -- Siskind (1996, *Cognition* 61) and Fazly, Alishahi
  & Stevenson (2010, *Cognitive Science* 34) are real computational cross-situational verb-meaning
  alignment models (EM/alignment-based), but **the lit-scan found NO credible citation framing this as
  a reward/RL credit-assignment problem over goal-outcome polarity specifically** -- this reinforces
  Section 3's verdict that reaching for this substrate's own RL-appraisal family would have been
  importing a framing the literature itself does not support for this sub-problem, not just a
  substrate-internal wiring mismatch.
- **Light-verb theory** (Jespersen; Grimshaw & Mester 1988; Butt 1995/2010) -- HIGH confidence,
  well-established; light verbs are semantically bleached/general-purpose, drawing meaning from a
  complement rather than lexically encoding result -- directly supports Section 4.4's `GROUNDED_
  NEUTRAL` design requirement as linguistically well-motivated, not an ad-hoc patch.

**Honest overall read:** this design is a genuine cross-component SYNTHESIS (cross-situational
learning's propose-but-verify credit-assignment shape + Behrend's result-verb-bias sensitivity +
Tomasello/Bloom's goal-intent grounding + light-verb theory's neutral-convergence prediction), not an
instantiation of an existing unified account -- the lit-scan explicitly flagged the specific
combination as absent from the literature it searched. This is valuable calibration information (a
negative-but-informative finding per the role's own standing discipline) and is the primary reason
Section 11's P_deflated lands below the anchor_propagate design's 0.42, despite this design's cleaner
non-circularity story and its avoidance of a wrong-mechanism risk (Section 3).

Also directly supersedes/redirects `notes/research_anchor_propagate_oov_outcome_verb_valence_
2026-08-06.md`'s PRIMARY direction (WordNet-relatedness propagation) per explicit USER instruction --
that pre-reg remains a standing, buildable ALTERNATIVE (not deleted, not falsified), should this
consequence-learning design's real-corpus yield (Section 7's honest uncertainty) prove too sparse in
practice.

---

## 10. Cheap decisive test / falsifiable predictions (summary -- full bands + exact procedure in the companion pre-reg)

Full pre-reg: `preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md`. Summary:

- **Primary metric:** live `congruence_with_lexicon_fallback` MET/UNMET accuracy on the 36-item OOV
  subset of `experiments/data/goal_bearing_modern_eval_v1.jsonl` (`outcome_in_lexicon: false`), AFTER
  the (non-circular, eval-passage-excluded) corpus learning pass populates `ACQUIRED_OUTCOME_VERB_
  FEATURES`.
- **HARD-PASS (summary; full gates in pre-reg):** learnable-subset accuracy >=0.75 (items whose
  outcome verb actually got grounded with a decisive margin); full-36 >=0.60 (beats majority floor
  0.6389... **note the full-36 gate is capped by construction below the majority floor unless enough
  items' verbs get grounded -- see pre-reg's honest-ceiling discussion**, actually gated on beating
  0.6389 by a real margin where coverage allows) and decisively beats increment-1b's 0.4444;
  light-verb-canary `GROUNDED_NEUTRAL` rate >=0.70; scramble control collapses to within the
  pre-registered chance band; referent-linked credit beats random-credit ablation by >=0.15 accuracy.
- **HARD-FAIL (summary):** full-36 fails to beat 0.6389 (repeats increment-1b's failure mode), OR the
  scramble control does NOT collapse (proves circularity), OR light-verb-canary `GROUNDED_NEUTRAL`
  rate <0.30 (verbs spuriously POS/NEG-locked from noise instead of correctly washing out).

---

## 11. Substrate-product implications

- **Do not wire `exp_grounded_appraisal_sim_earned_v1`/`pfc_gate_cfrpe_trained_v2`/`context_grounded_
  valence` into outcome-verb valence learning.** This is a real, disk-grounded, negative finding
  (Section 3) that should prevent a future increment from re-attempting this wire under the assumption
  that "the RL-earned component must be the missing piece" -- it is a differently-scoped mechanism
  (planning-gate / physical-harm-governor-verb niche), not a general consequence-computer for the
  goal-outcome-verb domain, and the prior session's own increment-1b measurement already proved the
  reward-theta path is redundant for this exact payload.
- **The `congruence_decision`/`lexicon_predict` dual-signal pair is a genuinely reusable "two
  independent teacher signals" primitive** beyond this one increment -- any future consequence-driven
  learning task in this substrate's goal/outcome domain can reuse this AND-gate pattern rather than
  re-deriving a novel two-view architecture from scratch (as the self-extension loop family did per-
  cell). Worth naming as a candidate for its own small promotion if a second consumer appears.
- **WordNet stays scoped to the anchor_propagate design only; do not add it here.** Keeping this
  design WordNet-free is a real architectural simplicity win, not just an incidental honesty finding
  -- it means this design has one fewer external-dependency risk surface than the alternative already
  on file.
- **The light-verb-neutral-convergence requirement is not a minor edge case -- it is the DOMINANT
  real-corpus traffic pattern (Section 7).** Any future consequence-learning increment in this domain
  must treat "correctly recognizing balanced/uninformative co-occurrence" as a first-class, heavily-
  weighted success criterion, not an afterthought -- the corpus scan shows light verbs are the
  MAJORITY of what a naive learner would see.
- **If this design's real yield proves too sparse** (Section 7's honest uncertainty about the
  filtered, real learnable-verb count), the anchor_propagate WordNet design remains a standing,
  already-pre-registered fallback (P_deflated=0.42) -- the two designs are not mutually exclusive;
  WordNet-relatedness propagation could in principle serve as a genuine "optional bootstrap
  accelerator" for words that never accumulate enough cross-situational exposure under this design,
  exactly the framing the task itself proposed. This is left as an explicit, named follow-up
  combination, not built here.

---

## Citations (verified count)

**This session's direct code reads (primary evidence, 9 files/sections, cited inline throughout):**
`experiments/exp_self_extension_loop_v1.py` (full), `experiments/exp_self_extension_grounded_
realprose_v1.py` (full), `experiments/exp_grounded_appraisal_sim_earned_v1.py` (full), `hdlab/context_
grounded_valence.py` (full), `hdlab/goal_typing.py` (full, 1259 lines), `hdlab/verb_lexical_
similarity.py` (full), `hdlab/self_improving_loop.py` (`decide_keep_or_revert`/`ABSTAIN_BAND_DEFAULT`
section), `experiments/exp_bridge1_governor_grounding_v1.py` (`GOVERNOR_VERB_CLASS` section),
`experiments/exp_pfc_gate_cfrpe_trained_v2.py` (header/contract), plus `experiments/data/goal_bearing_
modern_eval_v1.jsonl` (re-derived corpus-provenance breakdown, not assumed) and a live diagnostic
corpus scan over `data/corpora/{little_women,anne_of_green_gables,tom_sawyer,wizard_of_oz}/cleaned/
*.clean.txt` (Section 7 numbers, script not retained as a permanent artifact -- read-only measurement,
no new mechanism).

**Reused, previously verified in this session's prior notes (not re-fetched this cycle):**
`notes/SYNTHESIS_grounding_wall_definitive_2026-08-06.md`; `notes/research_anchor_propagate_oov_
outcome_verb_valence_2026-08-06.md` (P_deflated=0.42); `notes/drill_brain_grounding_wall_definitive_
2026-08-06.md`; `notes/drill_our_components_grounding_wall_definitive_2026-08-06.md`.

**New this session (Sonnet lit-scan sub-agent, generic academic terms, query-privacy discipline,
confidence-flagged per point, see Section 9 for the full per-citation calibration):** Yu & Smith
(2007, *Psychological Science*, cross-situational statistics, HIGH); Smith & Yu (2008, *Cognition*
106, infant CSWL, HIGH); Scott & Fisher (2012, cross-situational verb learning at 2.5y, MEDIUM);
Trueswell, Medina, Hafri & Gleitman (2013) / Stevens, Yang, Trueswell & Gleitman (2017,
"propose-but-verify," MEDIUM-HIGH); Tomasello (1992 *First Verbs*, 2003 *Constructing a Language*,
verb-island, HIGH but syntax-scoped); Ninio (contestation, "No Verb Is an Island," LOW/unverified
exact citation); Pinker (1984 *Language Learnability*, 1989 *Learnability and Cognition*, semantic
bootstrapping/structure-mapping, MEDIUM, causative-alternation-adjacent not outcome-polarity-direct);
Behrend (1990, result-verb bias in 3-year-olds, MEDIUM-HIGH, most directly on point); Tomasello
(intention-reading account) / Bloom (2000, *How Children Learn the Meanings of Words*, MEDIUM-HIGH);
Woodward / Hamlin & Kuhlmeier (infant goal-reasoning/helper-hinderer paradigms, HIGH on the components,
not on this design's specific synthesis); Siskind (1996, *Cognition* 61) / Fazly, Alishahi & Stevenson
(2010, *Cognitive Science* 34, computational cross-situational verb-meaning alignment, MEDIUM-HIGH
existence, explicitly NOT RL-framed); Jespersen (light verb, exact 1965 edition date LOW-confidence,
concept HIGH); Grimshaw & Mester (1988) / Butt (1995/2010, light-verb constructions, HIGH); Miller &
Cohen (2001, PFC cognitive-control/plan-monitoring, MEDIUM, canonical, not independently re-verified
this cycle).

**P_deflated:** raw ~0.50 (clean non-circularity design, direct reuse of 5 already-validated organs,
a correctly-identified wrong-mechanism-avoidance finding in Section 3, and a real disk-measured
bootstrap floor of 51.7%) deflated 0.20 (genuine novel cross-component synthesis per Section 9's
lit-scan -- no existing literature combines this design's specific mechanism, three new small
generalizations are unproven, and the real filtered learnable-verb yield is honestly uncertain until
run, likely well below the crude 638-lemma upper bound) -> **P_deflated = 0.30** (below the anchor_
propagate design's 0.42 and below the 0.50 novel-synthesis cap, reflecting that this design's
ARCHITECTURE is more defensible/non-circular than the WordNet alternative but its measured real-corpus
YIELD is the greater open question -- the biggest empirical risk is that the dual-signal AND-gate,
applied to real narrative windows, may simply not fire often enough per lemma to clear `MIN_CONFIRM`
for a useful number of genuinely content-bearing verbs).
