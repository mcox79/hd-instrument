# Research: the DYNAMICS/algorithm of pronoun antecedent selection -- activation, reinstatement, settling

**Date:** 2026-08-27. **Filed by:** research (Opus synthesis + 4x Sonnet lit-scan lanes, all fetched
primary/near-primary sources, not abstract-only). **Trigger:** direct topic request -- deep
Marr-algorithmic-level drill on the DYNAMICS of antecedent selection, explicitly NOT re-deriving
which cues matter (settled: grammatical role >> recency; Bayesian prior x likelihood; LV05
cue-based-activation refuted for the BINDING/choice decision).

**Grounding in prior work (not re-derived):**
`notes/problems/entity_binding_needs_a_modern_pronoun_corpus/SOLVED.md` (the live salience binder:
grammatical-prominence-dominant, 0.6988 [0.677,0.719] on GAP test n=1773, recency/frequency
ablate to +0.0000 marginal, CI-separated over string-identity/most-recent-mention/shuffled-twin
floors -- **this IS the "computational-level-correct" binder the topic statement refers to**),
`notes/research_pronoun_anaphora_brain_computation_2026-08-27.md` (established the prior x
likelihood shape, LV05 HARD_FAIL for binding, Jager/Engelmann/Vasishth 2017 interference-absent
finding), `notes/research_ic_coherence_gap_pronoun_2026-08-27.md` (IC/coherence likelihood term,
measured null on GAP). This drill's job is strictly the ALGORITHM/DYNAMICS layer these left open.

---

## (a) HEADLINE

**The literature does not support building an iterative settling/attractor mechanism for the
antecedent PICK itself -- two independent lines of evidence (a naturalistic-pronoun brain-fit
study and an interference-timing study) say the winning computation is fast and effectively
one-shot, convergent with the substrate's own on-disk HARD_FAIL of the nearest iterative cousin.
But the CURRENT feed-forward formula is fixable in a way the literature DOES pin down precisely:
replace the count-plus-capped-exponential-tiebreak salience score (proven mathematically unable to
let recency ever overturn a 1-mention frequency lead, per `T2c` on disk) with an ACT-R-style
base-level activation sum over ALL prior mentions,
`B_i = ln(sum_k w_role(k) . dt_k^-d)`, which is a genuine frequency/recency TRADE-OFF (a very
recent single mention CAN outscore several old ones, and several moderately-recent mentions CAN
outscore one very-recent one) rather than the current frequency-always-wins arithmetic. This is
not a new algorithm class -- it is still a feed-forward score-and-argmax -- but it is the
literature-correct FORM of that score, and no prior drill or build has tested it. GAP could not
have shown this defect (its snippets are too short for repeated-mention decay to matter, which is
exactly why the SOLVED.md ablation found recency/frequency marginal at +0.0000 even under the OLD,
provably-broken formula); a running-narrative corpus (LitBank / GUM) is required to exercise it.**

---

## (b) The six questions, answered, Marr-algorithmic level, PINNED / CONTESTED / UNKNOWN

### 1. Discourse-entity activation: quantitative form and update

**No framework in the literature offers a validated, empirically-fit CONTINUOUS scalar for
discourse-referent activation.** This negative is itself the most load-bearing finding of this
lane -- confirm before building on any of the four candidates as if it were settled:

- **(a) ACT-R base-level activation, `B_i = ln(sum_k t_k^-d)` (d~0.5), applied to referents:
  CONTESTED/mostly UNKNOWN.** The canonical form is Lewis & Vasishth (2005, *Cognitive Science*
  29:375-419, PDF fetched): total activation `A_i = B_i + sum_j W_j . S_ji` (fan-adjusted
  associative boost), latency `T_i = F . e^-A_i`. This machinery is validated for
  **sentence-internal syntactic dependencies** (reflexive/filler-gap binding), NOT for
  multi-sentence discourse-referent tracking. Lewis & Vasishth themselves flag the extension as
  future work and an untested assumption: *"one possibility is to simply assume that nominals have
  base activations that reflect their referential type... it would simply be an assumption about
  how certain linguistic distinctions are manifest in processing"* (p.410). Nobody has fit this
  equation to inter-sentential coreference competition. **This absence is the gap this drill's
  recommendation (below) proposes to fill, not a finding to build on as already-proven.**
- **(b) Centering Theory Cf/Cb update: PINNED as ordinal, UNKNOWN/absent as numeric.** Grosz,
  Joshi & Weinstein (1995): Cf(U_i) ranked by grammatical role, Cb(U_i) = highest-ranked Cf(U_i-1)
  element realized in U_i, Rule 2 prefers CONTINUE > RETAIN > SHIFT transitions. Confirmed via
  Poesio, Stevenson, Di Eugenio & Hitzeman (2004, *Comp. Ling.* 30(3), fetched): every published
  parametrization (grammatical-function, linear-order, Strube & Hahn 1999's
  HEARER-OLD/MEDIATED/HEARER-NEW) stays ORDINAL. Kibble (2001, *Comp. Ling.* 27(4)) explicitly
  **considered and rejected** numeric weighting in favor of ranked constraints. No paper found
  assigning Cf entities a real-valued score with an update equation.
- **(c) Givenness/Accessibility as graded activation: PINNED categorical, CONTESTED any numeric
  form.** Gundel/Hedberg/Zacharski (1993) is explicitly NOT graded ("encodes manner, not degree,
  of accessibility"); confirmed via a 2025 CRAC corpus re-evaluation (Chiarcos, fetched) still
  using categorical alignment. Ariel's Accessibility Marking Scale is ordinal (low/mid/high). The
  field's actual **working numeric proxy** is a different, less-famous paper: **Lappin & Leass
  (1994, *Comp. Ling.* 20(4))** -- explicit weighted salience factors (recency=100, subject=80,
  existential=70, direct-object=50, indirect-object=40, head-noun=80), summed per candidate, and
  **halved at every sentence boundary** (a discrete geometric decay, structurally the discrete
  cousin of ACT-R's continuous power-law decay), argmax picks the antecedent. This is corpus-tuned
  engineering, not derived from Ariel/Gundel/Chafe by its authors, but it is the closest thing to a
  validated numeric accessibility score that exists.
- **(d) Grosz & Sidner (1986) focus-space stack: PINNED, and does NOT supply a per-entity
  scalar.** Fetched directly. Focus spaces push/pop at discourse-SEGMENT boundaries; a focus space
  is a SET of salient entities plus the discourse-segment-purpose, membership-based not scalar.
  The paper itself states the division of labor: Centering is "a more local phenomenon" than the
  segment-level discourse-segment-purpose (DSP) Grosz & Sidner track; Poesio et al. (2004)
  independently confirm Centering is "the component... concerned with local coherence and
  salience... within a discourse segment." **Use Grosz & Sidner only for segment-boundary
  detection (e.g. resetting/discounting activation across a scene break), never as the per-entity
  activation mechanism itself.**
- **Unification (my judgment, not a literature result):** Centering supplies the correct FEATURE
  (grammatical role as a strength multiplier, matching what the live binder already validated at
  CI-separated +0.0344 marginal) but refuses to be numeric. ACT-R supplies the correct
  MATHEMATICAL FORM (decay-over-presentations) but has never been pointed at referents. Lappin &
  Leass show the two combine without contradiction: role sets a per-mention WEIGHT, and a decay
  term (continuous ACT-R power-law, or the coarser discrete Lappin & Leass halving) accumulates
  weighted mentions over time. **Recommended unification: `B_i(t) = ln( sum_{mentions k of i before
  t} w_role(k) . dt_k^-d )`** -- role sets each presentation's strength (reusing the SOLVED.md
  role-prominence hierarchy, not new), `dt_k` is sentence-distance (matching Lappin & Leass's
  granularity, not raw token distance), `d` is swept not adopted per standing discipline. A
  concrete discriminating test case for where Centering's ordinal Rule 2 and this scalar would
  diverge: two SHIFT transitions Centering treats as equally non-preferred, but one has 1
  intervening mention and the other has 8 -- the scalar predicts different antecedent strength,
  ordinal Centering predicts none.

### 2. The reinstatement operation (Dijksterhuis 2024) and its computational class

**Citation correction first (verify before quoting further):** the full, verified citation is
**Dijksterhuis, D.E., Self, M.W., Possel, J.K., et al. (18 authors), Dehaene, S., & Roelfsema, P.R.
(2024). "Pronouns reactivate conceptual representations in human hippocampal neurons." *Science*,
385(6716), 1478-1484.** DOI 10.1126/science.adr2813 (also bioRxiv 2024.06.23.600044). Fetched
directly. **Important calibration the topic statement should register: the verified abstract
establishes that pronoun-reading reactivates the hippocampal neuron selective for its referent --
it does NOT explicitly report a COMPETITIVE-SELECTION test among multiple simultaneously-active
candidate referents.** "Reinstates the peak-activation concept cell among competitors" is this
project's reasonable EXTRAPOLATION from the finding, not a claim the paper itself tested. Mark this
piece **CONTESTED-by-extrapolation**, not fully PINNED as stated in the topic statement.

**Is there a formal model of "pronoun as cue -> reinstates peak-activation referent"? PINNED, and
it already exists under a different name: this IS the ACT-R cue-based-retrieval machinery
(Lewis & Vasishth 2005; McElree, Foraker & Dyer 2003 speed-accuracy-tradeoff evidence for
direct-access, distance-independent retrieval; Parker 2019, *Cognitive Science* 43(3), "Cue
Combinatorics in Memory Retrieval for Anaphora" -- cues combine MULTIPLICATIVELY/nonlinearly, not
additively, a genuine departure from a plain weighted sum).** No SAM (Raaijmakers & Shiffrin 1981)
or classical-Hopfield-attractor model applied specifically to pronoun resolution was found -- the
ACT-R lineage is the field's actual working formalization of "cue -> content-addressable retrieval
-> highest-activation match," under different branding than the topic statement used.

**How does this differ from weighted-feature-sum argmax? THE CRUX FINDING, PINNED: it mostly
doesn't, mathematically.** ACT-R's own activation equation IS a weighted linear sum
(`sum_j W_j . S_ji`). And **Ramsauer et al. (2020/ICLR2021, "Hopfield Networks is All You Need,"
arXiv:2008.02217, fetched)** rigorously PROVES that one-step continuous-Hopfield content-addressable
retrieval (`s_{t+1} = X^T . softmax(beta . X . s_t)`) is mathematically IDENTICAL to one
transformer-attention step -- i.e. to a similarity-weighted softmax sum. **Under one-shot, linear/
softmax conditions, "cue-triggered pattern completion" and "weighted-sum argmax" provably coincide.**
The three places they genuinely diverge, and the only places worth building difference into:
(i) a stochastic race-to-threshold that can FAIL to retrieve (unlike argmax, which always answers)
-- relevant for a future "no confident antecedent" abstention signal, not for accuracy per se;
(ii) MULTIPLICATIVE/nonlinear cue combination (Parker 2019) instead of additive weighting -- a
genuinely different, cheap, testable change to the scoring function itself; (iii) genuine ITERATIVE
multi-step attractor relaxation with a partial cue reconstructing full stored patterns in the SAME
representational space -- this is the true "different algorithm class," and is addressed in Q3.

### 3. Settling vs. feed-forward

**Kintsch's Construction-Integration (1988, *Psych. Review* 95:163-182; 1998 book): PINNED
mechanism, CONTESTED exact cycle count.** Update: `a(t+1) = clip_>=0( normalize_L1( W . a(t) ) )`
-- W built from proposition argument-overlap (extendable with coreference/elaboration links),
negative values clipped to zero, remaining mass L1-normalized, iterated to stabilization. **Guha &
Rossi (2001, *J. Math. Psych.* 45(2):355-369, fetched)** formally prove this nonlinear dynamical
system's convergence/equilibrium properties -- the convergence guarantee is itself a citable,
PINNED result, even though the typical cycle count quoted in secondary literature (~6) could not be
independently re-verified against Kintsch's own primary text here (PDF access failed repeatedly;
report as CONTESTED, not adopted as a parameter).

**Spivey-Knowlton "normalized recurrence" (1996 dissertation; McRae, Spivey-Knowlton & Tanenhaus
1998, *JML* 38(3)): PINNED as a DISTINCT mathematical family from Kintsch's CI, not a variant of
it.** Per McClelland, Mirman, Bolger & Khaitan (2014, *Cognitive Science*, fetched): a 3-step cycle
-- raw per-constraint support -> normalized probabilistic support across the SMALL competitor set
-> weighted-summed and recurrently combined with existing activation, renormalized, iterated to a
criterion. This is multiplicative/probabilistic competition among a handful of interpretations, not
linear propagation over a large sparse graph. **The project's own existing
`experiments/exp_frontend_normalized_recurrence_v1.py` already implements essentially this exact
form** (`a = a * exp(gain*net); a = a / a.sum()`, iterate to a criterion) -- for THEMATIC-ROLE
assignment, not coreference. It is the right SUBSTRATE (same math family), wrong TARGET currently.

**Does settling predict something argmax cannot? CONFIRMED for thematic-role ambiguity, GENUINE
GAP for anaphora specifically.** McRae et al. (1998) reproduce graded self-paced-reading-time
patterns (cycles-to-criterion tracks difficulty) for reduced-relative-clause ambiguity -- a
difficulty gradient a single-shot argmax cannot naturally produce. **No paper was found applying
either CI or normalized recurrence BY NAME to anaphora/pronoun resolution with an RT/ERP
correlation.** The anaphora-specific settling-adjacent literature is a SEPARATE tradition --
memory-resonance models (O'Brien, Duffy & Myers 1986; Dell, McKoon & Ratcliff 1983) showing passive
antecedent reactivation correlating with RT, a different formalism (resonance, not
connectivity-matrix or normalized-recurrence). **The generalization "settling helps anaphora the
way it helps thematic roles" is UNTESTED in the literature, not confirmed.**

### 4. Structured-memory readout (FHRR/VSA) and attractor models of discourse activation

**Reading activation out of a bundled/superposed vector memory: PINNED qualitatively, CONTESTED on
exact equations.** Standard cleanup-memory readout is dot-product/cosine similarity between a
(possibly partial/noisy) cue and each stored item; highest-similarity item wins (Plate,
*Holographic Reduced Representations*, 1995/2003 -- primary PDF access failed, summary corroborated
via secondary source). Eliasmith's Semantic Pointer Architecture (2013, *How to Build a Brain*)
retrieves a bound item from superposed working memory by unbinding-then-cleanup (qualitative
mechanism confirmed via the lab's own SPA overview page; an explicit numbered retrieval-strength
equation could not be pulled from primary text -- access-limited, mark CONTESTED on the exact form
only). Kanerva's Sparse Distributed Memory gives a threshold-summed analog of the same idea
(NASA/NTRS technical report, fetched).

**Franklin, Norman, Ranganath, Zacks & Gershman (2020), "Structured Event Memory," *Psych. Review*
127(3):327-361 (SEM): UNKNOWN, not confirmed either way.** Citation verified (PubMed, Gershman lab
PDF located) but full-text extraction failed during this scan -- could not confirm or deny an
explicit entity-activation equation, HRR-style bind/bundle machinery, or any anaphora/pronoun
application inside SEM specifically. Report as a genuine open item requiring a follow-up fetch, not
a confirmed absence.

**A formal attractor-network model of REFERENT reinstatement, specifically for language/coreference:
NOT FOUND -- appears to be a genuine, currently-unfilled gap in the published literature.** Searched
multiple term combinations (attractor network + coreference/anaphora/pattern-completion + discourse
referent). Found only generic hippocampal CA3 pattern-completion literature with no language
application, and Ding et al. (2023, bioRxiv 2023.04.16.537082) -- a pure EEG/MEG correlational
"delta-band reinstatement" study for pronoun resolution with **no formal attractor-network
equation**. **If this project ever built and published such a model it would be a genuinely novel
contribution, not a replication of existing work -- flag as high-novelty/high-risk, not a
near-term build item.**

### 5. Test instrument: running-narrative corpus

GAP is confirmed structurally unable to test activation-accumulation (isolated 2-candidate
snippets, no accumulating discourse). Four candidates checked for live download + license + fit:

| corpus | downloadable | license | size / genre | fit |
|---|---|---|---|---|
| **LitBank** | YES, github.com/dbamman/litbank (verified) | CC-BY 4.0 | 100 novel excerpts, 210,532 tokens, 29,103 mentions, ~2,105 words/doc, continuous narrative, 1719-1922 fiction | **BEST FIT** -- long continuous spans, dense per-entity mention chains, exactly what an accumulation/decay mechanism needs to be exercised |
| **GUM** | YES, github.com/amir-zeldes/gum + gucorpling.org/gum/download.html (verified) | CC-BY | 168 docs, 150K+ tokens, 12 genres incl. fiction, CoNLL format | **SECOND CHOICE / cross-validation** -- open, well-formatted, but fiction subset shorter/thinner than LitBank |
| OntoNotes/CoNLL-2012 | official LDC-paywalled; unofficial HF mirror of disputed provenance | LDC / murky | ~1.6M words, news/broadcast, avg 464 words/doc | poor fit -- wrong genre, short docs, licensing unclear on the free route |
| ARRAU | LDC-paywalled | LDC | small, dialogue + Pear Stories narrative + news, mixed | selling point (long-distance anaphora) real but inaccessible + mostly non-narrative |
| PreCo | YES but weak fit | CC-BY | 38K docs, 12.5M words, exam-style short passages | large but shallow -- not accumulating discourse |
| WikiCoref | download link could not be verified live (bot-blocked host) | presumed CC-BY | ~30 full articles | plausible but **unconfirmed**, needs manual follow-up before relying on it |

**Recommendation: LitBank first, GUM second.** Both verified live and open-licensed today.

### 6. Honest disconfirming evidence

Two independent findings argue AGAINST needing iterative settling for the antecedent-CHOICE
decision specifically -- report both as real, not softened:

- **Li, Luh, Pylkkänen, Yang & Hale (2020), bioRxiv 10.1101/2020.11.24.396598, "Modeling pronoun
  resolution in the brain": PINNED, and it cuts AGAINST settling, not for it.** (Citation
  correction: the topic statement's "Li et al. 2020, ACT-R best-fit" is this paper; the authors are
  NOT "Li & Vasishth" -- that appears to be a conflation with the Lewis & Vasishth ACT-R lineage the
  model is built on.) Four models compared (Hobbs, Centering, ACT-R, NeuralCoref) against fMRI+MEG
  during naturalistic listening; **ACT-R's base-level DECAY equation plus associative/subjecthood
  spreading activation best-fit the neural signal, with MEG effects at 320-350ms post-pronoun-onset
  -- fast, consistent with a single retrieval-strength SCORE per candidate, not multi-cycle
  relaxation.** This supports base-level ACTIVATION (recommendation in Q1/HEADLINE) while arguing
  against iterative SETTLING as the pick mechanism -- these are separable claims and the paper
  supports one, not the other.
- **Chow, Lewis & Phillips (2014), *Frontiers in Psychology* 5:630: PINNED, evidence for fast,
  non-iterative, deterministic pick.** Across five experiments, absence of "facilitative
  interference" argues structural constraints (e.g. Principle B) apply deterministically at initial
  retrieval, explicitly contrasted against gradual/probabilistic constraint-satisfaction accounts.
- **Consistent with the substrate's own on-disk result:** LV05 full cue-based-activation binder
  HARD_FAILED for the binding decision (-0.1348, per prior notes), and
  Jager/Engelmann/Vasishth (2017) found the interference SIGNATURE absent for
  reflexive/reciprocal-antecedent dependencies specifically -- the structural case closest to
  pronoun binding. **Three independent sources now converge on the same negative: iterative/
  competitive retrieval dynamics are not the mechanism for the antecedent PICK.**
- Direct settling-vs-heuristic comparison SPECIFICALLY for anaphora (as opposed to thematic-role
  assignment, where settling's advantage is confirmed): **UNKNOWN, not found in the literature
  searched.** The generalization from thematic roles to anaphora is untested, not confirmed either
  direction.

---

## (c) Cheap decisive test (pre-registered)

**Step 1 (no training, ~1 day, uses LitBank -- already verified downloadable):** Download LitBank,
parse into per-document mention streams (role via spaCy, same tooling class as the GAP binder).
Implement the ACT-R-decay activation scalar `B_i(t) = ln(sum_k w_role(k) . dt_k^-d)` as a drop-in
replacement for the current `count + beta*exp(-lambda*dist)` salience score, holding the
grammatical-role weighting and agreement pre-filter IDENTICAL to the validated GAP binder (isolate
the decay-form change as the only variable). Sweep `d` in {0.3, 0.5, 0.7, 1.0} (ACT-R's own
literature range) -- do not adopt 0.5 by default per standing discipline.

**Step 2 (paired accuracy test, same population):** On LitBank pronoun instances restricted to
entities with >=3 prior mentions (the subset where decay-form differences are structurally able to
matter -- report this subset size explicitly, it may be small):
- Arm 1: current substrate formula (count + capped exp tiebreak).
- Arm 2: ACT-R-decay activation scalar (role-weighted, best-swept `d`).
- Arm 3 (mandatory, per the T2b/T2c lesson): Arm 2 recomputed with mention TIMESTAMPS shuffled
  within each entity's own mention list (destroys the decay structure, keeps the count and role
  weights) -- Arm 2 must beat this info-free twin CI-separated or the "decay carries information"
  claim is unsupported.
- Arm 4 (control from the analytic proof): construct a case where Arm 1 is PROVABLY wrong by its
  own math (entity A: 1 old mention far away; entity B: 0 mentions until now, 1 very recent mention
  -- A wins under Arm 1's count-dominant rule; B should win under a true recency/salience account if
  B is more discourse-topical) and confirm Arm 2 resolves it the way Arm 1 structurally cannot.

**Step 3 (settling, confirmatory not exploratory -- run only if Step 2 lands):** Re-point
`exp_frontend_normalized_recurrence_v1`'s normalized-recurrence machinery at antecedent-candidate
activation scores (role-weighted ACT-R-decay from Step 2) instead of thematic-role interpretation
scores. Test whether cycles-to-settle correlates with a DIFFICULTY proxy (e.g. top1-top2 activation
margin, already flagged in ORGAN_MAP E3 as a brain-faithful abstention signal) on LitBank. This is
NOT expected to change accuracy (per Q3/Q6 -- settling is not predicted to beat one-shot argmax on
accuracy); it is testing whether it adds a USEFUL difficulty/confidence signal cheaply, reusing
already-built code. Skip entirely if the top1-top2-margin signal already serves this role at lower
cost -- check before building.

---

## (d) Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction A -- ACT-R-decay activation beats the current count+capped-tiebreak formula on
LitBank, isolated to the multi-mention subset, and beats a shuffled-timestamp info-free twin.**
P estimate: raw prior HIGH (this is an analytic fix to a mathematically PROVEN defect -- T2c's
proof that a 1-mention count lead is unbeatable by the current recency term transfers directly:
the new form does not have that property by construction). Deflated 0.20 for uncharted
corpus/implementation risk (LitBank's fiction register, spaCy role-parse accuracy on 18th/19th-
century prose, and the possibility the multi-mention subset is too small to power a CI-separated
result) per the calibration discipline: **P_deflated = 0.45** (near the 0.50 novel-synthesis cap;
this is closer to "pinned math, unproven empirical transfer" than genuine novel synthesis).
HARD-PASS: CI-separated margin over Arm 1 AND over the shuffled-twin Arm 3, on the multi-mention
subset, n reported with CI half-width.
HARD-FAIL: no separation from Arm 1, or the shuffled twin ties/beats Arm 2 (would mean the decay
FORM doesn't carry information at this scale even where GAP could not test it -- a real, useful
negative, and would mean the SOLVED.md ablation's "recency/frequency near-zero marginal" finding
generalizes beyond GAP's short-snippet limitation rather than being an artifact of it).

**Prediction B -- combined role-weighted ACT-R-decay activation beats role-alone (recomputing the
SOLVED.md's 0.694-equivalent grammatical-prominence cue on LitBank).**
P estimate: **P_deflated = 0.40** (real risk the fiction-register parser or LitBank's own role
distribution swamps any decay-term contribution, consistent with the possibility flagged in
Prediction A's HARD-FAIL).
HARD-PASS: CI-separated lift over role-alone on the same population.
HARD-FAIL: ties/loses to role-alone -- would mean grammatical prominence so dominates that the
decay refinement, while mathematically correct, is not decision-relevant even on long narrative;
a legitimate, reportable negative (and consistent with SOLVED.md's own ablation direction).

**Prediction C (near-confirmatory, testing convergent literature) -- iterative settling over the
SAME activation scores does NOT beat one-shot argmax on accuracy, on the antecedent-CHOICE task
specifically.**
P estimate: **P = 0.65** (two independent lit sources, Li et al. 2020 and Chow/Lewis/Phillips
2014, plus the substrate's own on-disk HARD_FAIL of the nearest cousin mechanism, all point the
same direction -- this is close to a literature-confirmed claim, not synthesis).
HARD-PASS (confirms): settling accuracy does not CI-separate above one-shot argmax on the same
scores; settling MAY still show a genuine cycles-to-settle / difficulty correlation (a different,
compatible claim -- track separately, do not conflate).
HARD-FAIL (genuinely interesting if it happens): settling wins CI-separated on accuracy -- would
suggest the prior LV05-cousin failure was representation-specific (coarse features), not
settling-specific, and would warrant a dedicated re-test with better-resourced representations
before generalizing further.

---

## (e) Cross-thread synthesis

1. **Directly extends `notes/problems/entity_binding_needs_a_modern_pronoun_corpus/SOLVED.md`**
   rather than restarting it: SOLVED.md validated WHICH cue wins (grammatical prominence) and
   proved recency/frequency marginal at +0.0000 UNDER THE OLD FORMULA on GAP. This drill supplies
   the missing piece -- WHY that formula is the wrong FORM (T2c's proof: count is integer,
   exp-tiebreak is capped at 0.5, so recency can never overturn a 1-mention lead) and the
   literature-correct replacement form (ACT-R decay), plus the corpus (LitBank) GAP structurally
   cannot substitute for in testing it.
2. **Reconciles with `notes/research_pronoun_anaphora_brain_computation_2026-08-27.md`'s
   Prediction C** (LV05 cue-based-activation does not outperform salience for BINDING) --
   this drill's Q3/Q6 findings are the DYNAMICS-layer version of the same conclusion: not just "the
   specific LV05 implementation lost," but "the literature's OWN naturalistic-pronoun brain-fit
   study (Li et al. 2020) independently found a fast, one-shot activation SCORE wins, not
   iterative retrieval-with-settling." Two different lit-scans, run on different days with
   different search strategies, converge on the same negative -- this raises confidence in the
   negative beyond what either alone would support.
3. **Corrects a citation before it propagates further:** the topic statement's "Li et al. 2020" is
   Li, Luh, Pylkkänen, Yang & Hale (bioRxiv), not "Li & Vasishth" -- flagging this now per the
   project's own cite_check discipline (a wrong author attribution is exactly the kind of detail
   that survives silently once quoted a few times).
4. **`experiments/exp_frontend_normalized_recurrence_v1.py` is confirmed the right EXISTING
   substrate for any future settling exploration** (same normalized-recurrence mathematical family
   as Spivey-Knowlton/McRae et al.), but Q3/Q6's findings say do NOT repoint it at the antecedent
   PICK for accuracy purposes -- only as an optional, lower-priority difficulty/confidence-signal
   probe (Step 3), and only after checking whether the already-flagged top1-top2-margin abstention
   signal (ORGAN_MAP E3) already serves that purpose more cheaply.
5. **No existing note or organ addresses ACT-R-style multi-presentation decay for discourse
   referents** -- this is a genuinely new, specific, implementable proposal, not a re-run of
   anything on disk. `experiment_index.py query "activation decay"` / `query "act-r"` should be
   run by whoever builds this, as a final prior-work check before dispatch (not run here -- this
   note is research, not build).

---

## (f) Substrate-product implications

1. **The highest-value near-term build is a FORM fix, not a new mechanism class**: replace the
   count+capped-tiebreak salience score with the ACT-R-decay scalar, keeping the existing
   feed-forward score-and-argmax architecture, the existing role-prominence weighting, and the
   existing agreement pre-filter completely unchanged. This is a small, glass-box, swept-not-adopted
   change with a specific, falsifiable, pre-registered test (Section c/d above) -- not a rebuild.
2. **Do NOT build an iterative settling/attractor mechanism for the antecedent-pick decision.**
   This is now supported by three converging sources (two literature, one on-disk) and should be
   treated as a standing design constraint the way the prior LV05 finding already is -- flag so a
   future solver does not silently re-attempt it having only seen the accuracy metric.
3. **A genuinely novel, unfilled research niche exists** (formal attractor-network model of
   referent reinstatement for language) but is correctly OUT OF SCOPE for near-term product work --
   high novelty/high risk, no existing template to adapt, better filed as a standing "if we ever
   want a publishable/differentiating mechanism" note than pursued now.
4. **LitBank is a reusable foundation asset regardless of this specific drill's outcome** -- CC-BY
   4.0, verified live, and the only free running-narrative coreference corpus with dense enough
   per-entity mention chains to test ANY accumulation-based mechanism (not just this one). Loading
   it once serves every future discourse-accumulation test, not just pronoun binding.
5. **The FHRR-native readout (Q4, activation = cosine similarity to a stored/bundled mention
   vector rather than a hand-set role weight) is a real refinement path but should NOT gate the
   near-term build** -- the hand-set role-weight version is lower-risk, already partially validated
   (SOLVED.md's role-prominence result), and separable; test it first, refine to the register-native
   version only if it lands.

---

## (g) Citations (verified count)

**~31 sources directly fetched or independently corroborated across 4 parallel Sonnet lit-scan
lanes** (a few marked access-limited/partial, noted inline above rather than silently treated as
fully verified):

**Lane A (activation formalisms):** Lewis & Vasishth 2005 (PDF fetched); Grosz, Joshi & Weinstein
1995 (cited via secondary); Poesio, Stevenson, Di Eugenio & Hitzeman 2004 (fetched); Kibble 2001;
Chiarcos 2025 CRAC (PDF fetched); Lappin & Leass 1994; Grosz & Sidner 1986 (PDF fetched).

**Lane B (reinstatement + VSA):** Dijksterhuis et al. 2024 *Science* (DOI + bioRxiv preprint
fetched, full author list verified); Lewis & Vasishth 2005; McElree, Foraker & Dyer 2003
(ScienceDirect abstract fetched); Parker 2019 (Wiley abstract fetched); Van Dyke CBRT overview
(fetched); Ramsauer et al. 2020 "Hopfield Networks is All You Need" (arXiv PDF fetched); Plate HRR
1995/2003 (secondary summary only, primary access failed); Eliasmith 2013 SPA (lab overview page
fetched, primary equation not extracted); Kanerva SDM (NASA/NTRS report fetched); Franklin, Norman,
Ranganath, Zacks & Gershman 2020 SEM (citation verified via PubMed + Gershman lab PDF located, full
text not extracted -- UNKNOWN not negative); Ding et al. 2023 bioRxiv (fetched).

**Lane C (settling + disconfirming):** Kintsch 1988/1998 (secondary sources + ACM overview fetched,
primary PDF access failed); Guha & Rossi 2001 (formal convergence proof, cited); McRae,
Spivey-Knowlton & Tanenhaus 1998; McClelland, Mirman, Bolger & Khaitan 2014 (fetched, gives the
normalized-recurrence 3-equation form); Li, Luh, Pylkkänen, Yang & Hale 2020 bioRxiv (fetched,
citation corrected from topic statement's "Li & Vasishth"); Chow, Lewis & Phillips 2014 *Frontiers*
(fetched); Lago, Namyst, Jager & Lau 2019 (access-blocked, secondary snippets only).

**Lane D (corpus):** LitBank github.com/dbamman/litbank (fetched, live); GUM github.com/amir-zeldes/
gum + gucorpling.org (fetched, live); OntoNotes/CoNLL-2012 LDC + HuggingFace mirror (checked);
ARRAU LDC (checked); PreCo (checked, weak); WikiCoref (checked, link dead/bot-blocked -- flagged
unconfirmed, not usable as stated).

---

## TLDR

We already built and confirmed WHICH clue matters for figuring out who "he" or "she" refers to
(the grammatical subject of the sentence, not how recently someone was mentioned) -- this drill
was about HOW the brain actually computes the pick, not which clues it uses. Two things came out
clearly. First, the honest answer to "does the brain run some elaborate back-and-forth settling
process to make the pick" is NO, for this specific decision -- three separate pieces of evidence
(two from the literature, one already measured in our own system) all say the real mechanism is
fast and one-shot, so we should NOT build that. Second, we found a real, fixable flaw in how our
current formula weighs "how recently was this person mentioned": right now, mentioning someone
even one extra time can never be out-voted by recency, no matter how long ago that mention was.
The brain's actual math (from a well-established memory model) does NOT have that flaw -- a single
very recent mention CAN beat several old ones, and several medium-recent mentions CAN beat one very
recent one, which is a much more realistic trade-off. Our test corpus so far (short Wikipedia
snippets) was too short to ever expose this flaw, so we found a free, licensed collection of full
novel excerpts (LitBank) that actually has long enough stretches of text to test it properly. We
also caught and corrected a wrong citation before it could spread, and confirmed the 2024 brain-
scanning study that inspired this drill shows something slightly narrower than we assumed (it shows
reactivation, not literally a head-to-head competition test).

## QUESTIONS

None.

## NEXT STEPS

1. Dispatch a build cycle against the pre-registered test in Section (c): implement the ACT-R-decay
   activation scalar as a drop-in replacement for the current salience formula, on LitBank
   (download link verified live in this note), with the exact HARD-PASS/HARD-FAIL bands from
   Section (d) -- no further experiment design should be needed before shipping.
2. Do NOT build settling/attractor machinery for the antecedent-pick step itself; if a
   difficulty/confidence signal is wanted later, check whether the existing top1-top2-margin
   abstention feature already covers it before repointing
   `exp_frontend_normalized_recurrence_v1.py` at this problem.
3. File the "formal attractor-network model of referent reinstatement" gap as a standing, low-
   priority, high-novelty research note (not a near-term build item) -- it is a genuinely unfilled
   spot in the published literature, worth knowing about even though it is not this cycle's target.
4. Whoever builds this should run `experiment_index.py query "activation decay"` and
   `query "act-r"` as the final prior-work check immediately before dispatch (not run here, since
   this note is research not build, per role separation).
