# Brain-fidelity VET of the semantic-organ plan (component-by-component, adversarial)

AUDIT-ONLY (Skunkworks). Reference standard = `notes/brain_audit_affective_comprehension_mechanism.md`
(the brain-faithful drill: 9 subsystems 1.1-1.9, Section 2 answers, Section 4 recurrent pipeline).
Plan under audit = `notes/PLAN_grounded_semantic_organ_build.md` (v2). Prior design-VET =
`notes/design_vet_semantic_organ_plan.md`. Triggering evidence = C-A's two failures.

Every code/number claim below was read off disk THIS pass (READ THE CODE not the label):
`experiments/exp_sense_structured_hub_ca_v2.py` (full), the three metrics.json
(`data/exp_sense_collapse_floor_v1`, `..._ca_v1`, `..._ca_v2`), `hdlab/situation_reader.py`
(EventRecord L111-124), `experiments/exp_grounded_appraisal_sim_earned_v1.py` (CONG L74, codebooks
L114-119). Reuse-organ reads for ToM / frame_induction / predictive_coding are carried from the
design-VET's line-cited on-disk reads (consistent with what I re-verified here).
Cross-arc overlap check (carried from design-VET, same components): C-A overlaps HIGH with
`hdlab_encoder_cluster_vwfa_ppmi_composed_v3` + `concept_encoder` (same ATL-hub concept).

MEASURED vs claimed is flagged throughout.

---

## PART A — THE C-A CENTRAL QUESTION (decisive; gates the build)

**Question:** Is C-A as formulated — STANDALONE, UNSUPERVISED, DISCRETE-sense induction from LEXICAL
CO-OCCURRENCE, evaluated by isolated 2AFC sense-discrimination — brain-faithful?

**Decisive answer: NO. It is un-brain-faithful on THREE independent axes (shape, position, metric),
and the two failures are the predicted symptom, not bad luck.** Held against the drill:

### (a) Do the two fails confirm raw co-occurrence lacks the sense signal? — YES, strongly (MEASURED).

The drill (§1.4, §2.2, §4) says sense selection is done by the semantic-control network via biased
competition keyed to the running situation model, and concepts are differentiated by grounding to
spokes (valuation/interoception). The signal that separates "studied hard" from "hit hard" is
grounding + syntax + situation, NOT bag-of-words co-occurrence. The disk confirms co-occurrence
carries almost none of it:

- **Floor cell** (`sense_collapse_floor_v1`): all four existing encoders at/near chance —
  random_indexing 0.375, concept_encoder 0.5625, composed_encoder_v3 0.531, ppmi_sparse 0.625.
  Crucially the two *context-sensitive-by-construction* encoders (composed_v3, ppmi) show
  same-sense-vs-diff-sense cosine SEPARATION ~0.005 / ~0.003 — i.e. the rep DOES vary with context
  but the variation is essentially orthogonal to the sense distinction. `any_positive_surprise=False`,
  `best_starting_encoder=none`.
- **v1** (`ca_v1`): mean_fit_same_sense_residual 0.436 vs mean_fit_diff_sense_residual 0.447 —
  featureless (0.011 gap). held_out 0.567 ~= floor 0.5625.
- **v2** (`ca_v2`, 3000-sentence real corpus): count_ppmi 0.55, error_driven_pc 0.517 — BOTH BELOW
  the 0.5625 floor. count residuals same 0.235 / diff 0.244; error-driven residuals same 0.619 /
  diff 0.617 — again featureless in BOTH arms.
- **The kill-shot for the "signal is there, induction is weak" hypothesis:** the SUPERVISED
  single-prototype control in v2 (ref_A = FIT-A[0], ref_B = FIT-B[0], nearest-centroid WITH the gold
  sense handed to it) scores 0.5167 — chance. When even a supervised 1-shot-per-sense nearest-centroid
  on the same bag-of-words rep is at chance, the failure is REPRESENTATIONAL (signal absent), not a
  clustering/induction defect. Confirmed: the brain's sense signal is not in masked bag-of-words.

### (b) Is "induce N DISCRETE sense-prototypes" itself un-brain-faithful? — YES (FRAMING error).

The drill's hub (§1.2) is an **amodal, graded** concept representation; §1.1 says all senses are
transiently **co-active**, and §2.1 (Barrett constructionist) says meaning is **constructed
per-instance, graded, not a fixed inventory of stored senses**. C-A instead induces a discrete
prototype set per form (greedy spawn/merge k-means over context vectors, `_induce_senses`
L581-622) and does hard nearest-prototype 2AFC. That is a discrete-symbol WSD formulation, which the
constructionist view the drill adopts explicitly rejects. **Reformulation: C-A should be a
CONTEXT-MODULATED graded concept representation — one concept vector per form that context SHIFTS
toward a reading — not a discrete sense inventory.** The "reading" is a point in a graded space
selected by control+situation, not a cluster id.

### (c) Are C-A and C-B inseparable (the split is an artifact)? — YES (POSITION error).

The drill is unambiguous (§1.4, §4 "which components dominate"): the hub ALONE yields only the
**default/dominant** reading; the contextually-correct sense is produced BY the control network
(1.4) under top-down bias from the situation model (1.5) and prediction (1.6), in a **recurrent
1.4/1.5/1.6 loop** (§4 "Recurrence"). So a form's senses only become separable WHEN control +
situation + grounding weigh in. "Sense structure that exists and is testable BEFORE control" is not
a thing the brain has — the plan's C-A (sense structure) / C-B (control) split cuts the pipeline at
a seam the brain does not have. This is exactly why C-A fails in isolation: it is being asked to
produce, feedforward and unaided, the very thing the drill says is only produced by the recurrent
loop. **C-A and C-B must be ONE component: a context-conditioned concept read (biased competition
keyed to context), tested together.**

### (d) Is the METRIC wrong? — YES (METRIC error).

The drill's objective for sense selection (§1.4) is **contextual relevance / coherence with the
situation model**, and the decisive brain-referenced test (§2.2, §6) is **downstream differential
grounding/valence on collision items** — does "studied hard" ground to non-harm while "hit hard"
grounds to harm. Isolated 2AFC clustering of masked bag-of-words tests neither: it strips the target
word (removing the thing being grounded), strips syntax and word order (`_bundle_sign` is an
order-free sign-of-sum bundle, L508-514), and provides no situation/prior-sentence context. The
metric measures a quantity the brain does not optimize. **The test should be the differential
downstream grounding on collision pairs given context, not standalone sense-cluster accuracy.**

### C-A REFORMULATION (the corrected component)

Merge C-A+C-B into one **context-conditioned concept-read** organ:
- ONE graded concept vector per form (keep the existing ATL-hub encoder as the default activation).
- A control step (biased competition / top-down bias vector from the running context) that SHIFTS
  the read, using grounding spokes and syntax (verb frame / argument structure) as the bias source —
  NOT bag-of-words co-occurrence, which the disk proves is signal-free here.
- Judged by DOWNSTREAM differential grounding on collision pairs given a disambiguating prior clause,
  not by isolated 2AFC. This is the §6 cheap decisive test, restricted to subset (a).

---

## PART B — RANKED DIAGNOSIS OF THE TWO C-A FAILS

Four candidate causes, ranked by how much of the failure each explains (all MEASURED off disk):

1. **SIGNAL (dominant).** Masked bag-of-words co-occurrence context does not linearly separate these
   senses at this scale. Evidence: context-sensitive encoders separate at ~0.003-0.005; supervised
   nearest-centroid control at chance (0.5167). No induction method can recover a signal that is not
   in the representation. This is the primary cause and it VALIDATES the drill: the sense signal is
   grounding/syntax/situation, not co-occurrence.

2. **FRAMING (large, load-bearing).** Discrete standalone induction + isolated 2AFC is the wrong
   shape (b) at the wrong pipeline position (c) judged on the wrong objective (d). Even with a
   perfect co-occurrence signal this formulation would not be the brain's mechanism. Ranked above
   MECHANISM because it is the reason the experiment cannot succeed regardless of the gate details.

3. **MECHANISM (real but secondary).** The "error-driven" arm never engaged its error gate:
   `applied_frac=0.9996` (18669/18676 writes applied) — the `threshold_gate` skipped essentially
   nothing, so the Rao-Ballard residual selectivity did NOTHING and the arm degenerated to plain
   Hebbian outer-product accumulation. The induction-trace residuals are bimodal (1.0 on spawn /
   ~0.01 on merge), not graded — a saturating associative memory, not predictive coding. So "error-
   driven differentiation" was never actually tested. Secondary because the honest count_ppmi arm
   AND the supervised control are also at chance — fixing the gate cannot rescue an absent signal.

4. **EVAL (minor).** 60 trials/arm is small (binomial SE ~0.06), but the effect size is ~0, not
   merely noisy — underpowering is not the story. The masked-target + order-free bundle also removes
   real signal, but that is a FRAMING/metric issue (d), not sampling.

**Read:** SIGNAL and FRAMING together account for the failure; MECHANISM is a genuine but non-
rescuing defect; EVAL is minor. The correct conclusion is NOT "count caps beat error-driven" (the
plan's `COUNT_BEATS_ERROR_DRIVEN` read is an artifact of comparing two at-chance arms, delta 0.033,
inside noise) — it is "bag-of-words is the wrong signal AND standalone discrete 2AFC is the wrong
test." Do NOT iterate C-A v3 on the same formulation.

---

## PART C — PER-COMPONENT FIDELITY TABLE

Verdict key: SHAPE = does our mechanism reproduce the subsystem's computation; POSITION = right
pipeline place WITH the right feedback/recurrence; METRIC = judged on the brain's objective.
Easy-proxy flag = where we do a cheap substitute for what the brain actually does.

| Component | Brain subsystem | SHAPE | POSITION | METRIC | Easy-proxy flag | Brain-faithful correction |
|---|---|---|---|---|---|---|
| **C-A sense hub** | 1.1/1.2 (wordform+ATL hub), but the *task* it is set is 1.4's | WRONG-SHAPE (discrete inventory vs graded co-active; §1.2/§2.1) | WRONG (tested standalone/feedforward; brain resolves sense only in the 1.4/1.5/1.6 loop, §4) | WRONG (isolated 2AFC vs contextual-coherence/downstream-grounding, §1.4/§2.2) | **YES** — bag-of-words co-occurrence as a proxy for grounding+syntax+situation | Merge with C-B; graded context-modulated read; judge by downstream differential grounding |
| **C-B semantic control** | 1.4 (IFG/pMTG biased competition) | WEAK (plan wording admits an argmax-over-cues heuristic; not Desimone-Duncan mutual inhibition) | WRONG as sequenced (placed AFTER a standalone C-A; must BE the thing that makes sense separable, with situation-model top-down bias) | WEAK (local-window shortcut saturates it unless disambiguator is prior-sentence-only) | YES — local-window cue argmax as a proxy for situation-model-keyed biased competition | This IS the real C-A; implement mutual-inhibition under a top-down situation bias vector; prior-sentence-only can-fail |
| **BRIDGE-1 text->appraisal** | feeds 1.3 (OFC/insula spokes) | MISSING (does not exist; the sim's congruence/coping are HAND-mapped, `CONG` L74) | n/a (unbuilt) | n/a | YES — inheriting the synthetic no-text 1.000 as if it were a text number | Build+gate a real appraisal-from-text encoder (itself a hub+control job); never inherit 1.000 |
| **C-C sense-resolved valence** | 1.3 grounding spokes | BLOCKED on BRIDGE-1 (WRONG-SHAPE until the bridge exists); appraisal-sim theta is a discrete-world codebook, type-incompatible with text (L114-119) | right in principle (downstream of the read) | WEAK (scramble discriminator is good but a per-sense hand table also beats it; doesn't prove the sim drove the value) | YES — "route concept into the sim" hand-waves the entire text->appraisal organ | Value witness (sim theta drove it) + generalization-to-unseen-concept floor over a hand table |
| **C-D situation-model affect + prediction** | 1.5 event-model + 1.6 predictive coding | PARTIAL — EventRecord (predicate/agent/patient/tense/subj_role/obj_role, L111-124) is the correct EMPTY home but has NO affect dim; prediction not isolated from integration | POSITION right (above sentence-level, feeds control) | WRONG as written — "beat per-token pooling" proves INTEGRATION not PREDICTION; a static Bayesian aggregator passes it too | YES — static cue-aggregation as a proxy for forward-projection-to-an-unstated-outcome (§2.3: dread = predicted future negative) | Add affect dim bound to coref index; add a can-fail that ISOLATES forward prediction (static-no-projection arm must fail); reuse `predictive_coding` |
| **C-E-DETECT ACC incongruity** | 1.8 (dorsal ACC conflict monitor) | ASSUMED — not built as its own component; folded into C-E | MISSING as a first-class trigger between 1.6 and 1.7 | ungated | YES — assuming the detector rather than building/gating it | Build as its own gated component (predicted-vs-surface mismatch magnitude, ROC vs no-conflict); CARRY the drill's MODERATE-confidence flag (§1.8/§3: ACC-for-irony is inference-from-adjacent-lit, not established) |
| **BRIDGE-2 text->belief** | feeds 1.7 (TPJ nested-HRR) | MISSING (ToM takes structured agent-partitioned belief bundles, not a text mismatch signal) | n/a (unbuilt) | n/a | YES — "route through ToM" hand-waves the belief-from-text extractor | Build+gate the belief-from-text bridge separately, or declare C-E blocked on it |
| **C-E irony (byproduct)** | 1.7 mentalizing reattribution | CONDITIONAL — faithful ONLY if C-D prediction is genuine AND no surface classifier smuggled via BRIDGE-2 | right (downstream consumer of 1.5/1.6, gated by 1.8) | GOOD design (bans explicit-marker leak; requires byproduct) but validity is downstream of the C-D prediction gate | LOW (best-designed gate) but risk: relabeled surface classifier | Keep, but strictly conditional on the C-D prediction-isolation gate and a charged/adequately-sized sincere FP set |
| **C-F goal-owner** | 1.7 content bound via 1.5 intentionality dim, persisted via 1.9 | DIRECTION right (frame-conditioned + persisted; matches verified `frame_primary_role` frame-primary win) | POSITION right but UNSEQUENCED — `frame_primary_role` falls OOV subj->AGENT in production; OOV induction is offline-only | WEAK — "beat 0.32 e2e" is aggregate-permissive; coref alone could move it | YES — positional/coref fallback masquerading as sense-resolved role typing | WIRE OOV frame-induction into the reader FIRST; ablation isolating the TYPING_MISS delta to sense-resolved roles |
| coref (persistence spoke) | 1.9 hippocampal relational | SOUND (verified faithful/HARD_PASS/WIRED) | SOUND | SOUND | none | reuse as-is (bind affect to coref-resolved protagonist index) |
| predictive_coding (reused) | 1.6 substrate | SOUND organ, UNDER-REUSED | should feed C-D/C-E forward-valence | n/a | YES (missed-reuse -> islanding risk) | reuse for forward-valence expectation + predicted-vs-surface mismatch |

---

## PART D — WHICH FORMULATIONS (not just implementations) MUST CHANGE

1. **C-A + C-B: MERGE and REFORMULATE.** The single biggest correction. Discrete standalone sense
   induction from co-occurrence, isolated-2AFC-scored, is wrong on shape (b), position (c) and
   metric (d), and the disk proves the signal is absent (a). Replace with ONE context-conditioned
   graded concept-read organ whose bias source is grounding+syntax, judged by downstream differential
   grounding. This is a FORMULATION change, not a gate tweak — do not run C-A v3 on the old design.

2. **C-D: REFORMULATE the gate to isolate PREDICTION from integration.** Highest-priority gate
   rewrite (C-E depends on it). Add a forward-projection-to-unstated-outcome can-fail with a
   static-no-projection arm that MUST fail.

3. **C-E-DETECT (ACC): PROMOTE from assumed to a first-class gated component**, carrying the
   moderate-confidence flag. It is currently a formulation gap (an assumed sub-signal), not an
   implementation gap.

4. **BRIDGE-1 and BRIDGE-2: PROMOTE from hand-waves to first-class gated build steps.** Both are
   instances of the missing organ (text->structured extraction is itself a hub+control job); C-C and
   C-E are blocked on them. Never inherit the synthetic appraisal-sim 1.000 or the ToM HARD_PASS as
   a text number.

Components whose DIRECTION is fine and need only implementation/sequencing (not reformulation):
C-F (wire OOV first + ablation), coref (reuse), predictive_coding (reuse, stop under-reusing).

---

## PART E — CORRECTED NEXT STEP FOR C-A

Do NOT dispatch C-A v3 as more discrete-induction-from-co-occurrence. The next step is the drill's
Section-6 cheap decisive test, restricted to the (a) sense-override subset, run as ONE merged
context-conditioned read:

1. Build minimal collision pairs ("studied hard"/"hit hard", "a trick"=deception/skill) where the
   disambiguator lives in a PRIOR clause (not the local window, not the masked target).
2. Read = ATL-hub default vector SHIFTED by a control step whose bias comes from the verb frame /
   argument structure + grounding spokes (reuse `frame_induction` roles + the appraisal spoke via a
   real BRIDGE-1), NOT from bag-of-words co-occurrence.
3. Judge by DOWNSTREAM differential grounding: does the shifted read of "hard" ground to non-harm in
   the study frame and to harm in the strike frame. Floor = the single-prototype hub (which the disk
   shows is at chance); HARD-PASS = a real grounding gap on collision pairs, prior-sentence-forced.
4. Keep the honest-floor and disjoint-vocab disciplines; drop the isolated-2AFC metric.

If BRIDGE-1 is not yet built, the correct next step is BRIDGE-1 (appraisal-from-text), because C-A's
corrected metric depends on it. That is the true blocking foundation — not another sense-induction
arm.

---

## DISK PATHS + DRILL SECTIONS CITED
- Drill: `notes/brain_audit_affective_comprehension_mechanism.md` §1.1-1.9, §2.1-2.5, §4, §5, §6.
- Plan: `notes/PLAN_grounded_semantic_organ_build.md`; prior VET: `notes/design_vet_semantic_organ_plan.md`.
- C-A code: `experiments/exp_sense_structured_hub_ca_v2.py` (`_bundle_sign` L508, `_fit_error_driven_arm`
  L517, `_induce_senses` L581, control L727-741).
- Metrics: `data/exp_sense_collapse_floor_v1/metrics.json` (floor 0.5625, all-encoder collapse),
  `data/exp_sense_structured_hub_ca_v1/metrics.json` (0.567; residual 0.436/0.447),
  `data/exp_sense_structured_hub_ca_v2/metrics.json` (count 0.55 / error-driven 0.517;
  applied_frac 0.9996; supervised control 0.5167).
- Reuse organs: `hdlab/situation_reader.py` EventRecord L111-124 (no affect dim);
  `experiments/exp_grounded_appraisal_sim_earned_v1.py` CONG L74, codebooks L114-119 (hand-mapped);
  `hdlab/predictive_coding.py` (wired, under-reused); `hdlab/frame_induction.py` frame_primary_role
  (OOV->AGENT in prod); coref (verified faithful/WIRED).
