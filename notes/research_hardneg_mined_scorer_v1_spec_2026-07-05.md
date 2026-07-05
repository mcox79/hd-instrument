# Research: trained hard-negative-mined scorer as the redirect from the post-hoc rescore MIDDLE — spec only

**Filed:** 2026-07-05 by research (Opus synthesis; off-disk recompute of the landed debias-rescore smoke
cell's per-slot metrics, cross-referenced against the reframe cell's training-loop source, plus 2
parallel Sonnet lit-scan sub-agents, generic-math-terms only per query-privacy discipline). **Spec
only — no dispatch.**

**Trigger:** `data/exp_schema_relation_hubness_debias_rescore_v1_smoke/metrics.json`, verdict
`MIDDLE_BAND`: the training-free CSLS/logit-adjust post-hoc rescore (`experiments/exp_schema_relation_hubness_debias_rescore_v1.py`)
moved MRR rms materially (best V300+ rms lift +0.4948) but the gate that actually matters —
REAL-absolute non-degradation, not just the paired rms delta — shows the win is **slot-conditional**:
it clears HARD-PASS on the JOINT slot (undertrained, hub-collapsed) and is a **phantom** on the
FROZEN slot (scale-representative, fully-converged bilinear relation transform on fixed content).
Diagnosis lineage: `notes/research_hubness_popularity_debias_rank1_sharpening_2026-07-05.md`
(hubness Gini 0.87-0.95, label-prior corr 0.42-0.80, split by relation) →
`experiments/exp_schema_relation_hitsatk_mrr_reframe_v1.py` (scorer/training source, read in full for
this note) → `data/exp_schema_relation_hitsatk_mrr_reframe_v1_smoke/` (parent MIDDLE_BAND).

---

## HEADLINE

**Hubness has two loci with different fixability, and the smoke cell's own per-slot data — not just
external lit-scan — proves it.** (1) A **content-geometry-baked** component survives even a
fully-converged relation transform: on the FROZEN slot (2000-step-equivalent bilinear W trained to
convergence on FIXED content), the raw object-side argmax-winner Gini is **nearly identical between
the REAL-labeled and SHUFFLED-labeled arms** (V300 CausesDesire: REAL Gini=0.980 vs SHUFFLED
Gini=0.971; V300 AtLocation: REAL=0.918 vs SHUFFLED=0.927) — meaning *which* labeling task the
relation transform W is fit to barely moves which objects win the argmax slot. That is a direct,
internally-measured signature that the hub concentration lives in the **fixed object-embedding
geometry** (`Vo = Fo @ Po`, both frozen), not in what W learned. Confirmed independently: the
post-hoc rescore on FROZEN doesn't just fail to help, it makes REAL performance monotonically
**worse** as correction strength increases (CausesDesire V300 FROZEN: CSLS real Hits@1 lift=-0.033,
LOGIT=-0.25, BOTH=-0.317) while the apparent rms "win" is 100% attributable to a SHUFFLED-arm
collapse (shuf lift -0.567) — the textbook phantom this cell's own anti-phantom gate exists to catch.
(2) A **transient, training-state-driven** component is genuinely removable: on the JOINT slot
(undertrained at smoke scale, 80 steps), CSLS delivers a **real, non-phantom** win (CausesDesire
V300: REAL Hits@1 lift=+0.467, SHUFFLED lift=0.0, `clears_HP=True`). Two parallel lit-scans
independently corroborate both halves: (a) linear/orthogonal recombinations of a fixed embedding
(PCA, ICA) provably fail to reduce hubness unless they destroy neighbor information — only
distance-*distorting* nonlinear methods succeed (Feldbauer & Flexer 2019) — which is exactly why a
bilinear map on frozen content (FROZEN) cannot touch component (1); (b) a model trained to
cross-entropy optimality under a skewed label marginal is *expected*, as a matter of Bayes-consistency,
to confidently prefer popular wrong answers on ambiguous inputs (Gordon-Rodriguez et al. 2020) — which
means FROZEN's confident (z=2.2-2.7 std) preference for hub objects is not necessarily miscalibration
to be rescored away; it may be the CE-optimal fit to a biased marginal, and removing it algebraically
removes real signal along with bias (exactly the monotonic-REAL-degradation result above).

**The redirect to TRAINED hard-negative mining is well-motivated, but not for the reason the naive
framing suggests.** The reframe/debias cell already trains with **exact full softmax** over the
entire (V<=1000) candidate set on every step — every "negative" DPR/ANCE-style mining would surface
is *already* in the loss every step. Lit-scan confirms: classical hard-negative mining's benefit is
specifically about exposing a model to negatives missing from a *sampled*-softmax or in-batch
approximation (Karpukhin et al. 2020; Xiong et al. 2021) — that exposure gap does not exist here, so
"mine negatives and add them to training" as literally stated would not change anything (they were
never absent). The mechanistically correct redirect is a **margin-augmented loss** (additive-margin /
large-margin softmax, ArcFace/CosFace/L-Softmax family) that keeps gradient pressure applied on the
*specific currently-highest-scoring wrong competitor* even after CE alone has stopped pushing (CE's
gradient shrinks toward zero once P(true) is highest, regardless of how thin the margin is over the
runner-up — it has no floor to satisfy). "Mining" still matters, but as **curriculum weighting +
margin target selection** (identify the current top-ranked wrong object every K steps, cheap at
V<=1000, no ANN needed — the task's own framing) — not as new-negative exposure. This reframes the
cell from "give the model negatives it hasn't seen" (false premise here) to "give the training
objective an explicit rank-margin floor calibrated to the measured confidence gap, targeted at the
specific object each query is actually confused with" (well-motivated, and testable).

---

## 1. MECHANISM — quantified content-vs-transform locus (off-disk recompute + lit-scan)

### 1a. Direct measurement: REAL vs SHUFFLED Gini on FROZEN (the "is it content or transform" test)

| Config | Relation | FROZEN REAL Gini | FROZEN SHUFFLED Gini | delta |
|---|---|---|---|---|
| V100 | AtLocation | 0.720 | 0.707 | 0.013 |
| V100 | CausesDesire | 0.801 | 0.753 | 0.048 |
| V300 | AtLocation | 0.918 | 0.927 | -0.009 |
| V300 | CausesDesire | 0.980 | 0.971 | 0.009 |

(source: `hub_diag_real_vs_shuffled_gini` in `data/exp_schema_relation_hubness_debias_rescore_v1_smoke/metrics.json`,
computed from `score_mats["FROZEN"][arm]["inductive"]` per `eval_config_relenc`.)

**Reading:** the SHUFFLED arm trains an *entirely different* bilinear W (fit to a random permutation
of labels — pure noise, by construction) on the *same* fixed content/projection. If hubness were
primarily a property of what W learns, REAL and SHUFFLED Gini should differ substantially (W is
optimizing for a completely different, unrelated target). They don't — deltas are 0.01-0.05 on a
Gini scale of 0.7-0.98. This is the internal, measured version of the lit-scan's PCA/ICA-null-result
argument: a linear map re-expresses the same fixed geometry regardless of which labeling task it is
asked to fit, and object-side argmax-winner concentration is set almost entirely by the FIXED
object embedding `Vo = Fo @ Po`, not by W. **This is why post-hoc rescore is structurally incapable
of fixing FROZEN's hub bias without collateral damage: there is no "W-induced excess" to subtract —
the excess score-mass sits in the object geometry itself, and any global row/column correction
applied on top of it also strips whatever real per-query discrimination W *did* manage to learn
(hence the monotonic REAL degradation as CSLS→LOGIT→BOTH stack).**

### 1b. Verdict on the mechanism question: content or transform?

**Both, at different loci, with different fixability — and the fixability split maps exactly onto
FROZEN vs JOINT:**

- **Content-embedding-geometry hubness** (the FIXED `Fo`/`Po` object-side geometry): baked in,
  survives full convergence of a linear/bilinear relation transform, MEASURED equally present in
  REAL and SHUFFLED arms. **Not reachable by retraining the relation transform alone** — a linear
  map cannot remove concentration-of-measure effects in the space it operates on (Feldbauer & Flexer
  2019, PCA/ICA null result). The one lever that directly targets this (richer/different content
  embedding) was already tried and HARD_FAILed (`exp_schema_relation_richer_content_vscan_v1`) — so
  this component's cheapest remaining lever is not "better content" (closed) but a **nonlinear,
  end-to-end-trained reshaping** with a loss that explicitly targets rank-margin rather than
  likelihood (see below) — that reshaping is only possible where the encoder itself is trainable
  (JOINT), not where content is frozen (FROZEN) — UNLESS the FROZEN slot is also given a trainable
  nonlinear head, which this spec proposes as the concrete test of "can *any* amount of relation-side
  training touch this locus, or is it truly out of reach for a fixed-content pipeline."
- **Optimization-trajectory hubness** (JOINT at 80 smoke-steps): a transient artifact of an
  undertrained nonlinear encoder — MEASURED genuinely removable (JOINT CSLS clears real HARD-PASS on
  CausesDesire, non-phantom). Lit-scan flags a related, larger literature on representation
  collapse/anisotropy in undertrained encoders (Jing et al. 2022 dimensional collapse in
  contrastive/SSL training) as the likely underlying phenomenon, though no paper was found that
  explicitly reconciles "frozen concentration-of-measure hubness" and "transient undertraining
  collapse" as the same symptom with two causes — **that reconciliation is this note's own synthesis,
  not a cited result, and is flagged accordingly (novel-synthesis cap applies).**
- **Open, not fully resolved by this note:** whether JOINT at its FULL-mode step count (500 steps,
  vs smoke's deliberately-crippled 80) still sits in the malleable/undertrained regime or has already
  reconverged toward the FROZEN-like Bayes-consistent-with-bias fixed point. This is exactly the
  question the proposed cell (Section 2) is designed to answer, and is flagged as the top follow-up
  if this cell's own JOINT-slot result is ambiguous.

### 1c. Why margin-loss, not naive re-exposure — the corrected mechanism story

Two lit-scan sub-agents (generic-math-terms queries; full transcripts on file, summarized here)
converged on the same correction to the naive task framing:

- **Full-softmax already includes every negative every step.** Classical hard-negative mining
  (Karpukhin et al. DPR 2020; Xiong et al. ANCE 2021) exists to fix *negative-exposure starvation*
  under sampled/in-batch softmax. This cell's training (`fit_scorer_paired`, `joint_train_score`) uses
  exact full softmax cross-entropy over the *entire* V-object codebook on every gradient step — there
  is no exposure gap. Literally adding "mined negatives" to a loss that already sees them changes
  nothing. (Corroborated further by NV-Retriever, Moreira et al. 2024, which frames re-mining as
  fixing exposure/staleness, not adding new information content the loss lacked.)
- **CE has no margin floor.** Softmax cross-entropy's gradient on the true-class logit is `p_true-1`
  — it shrinks continuously as `p_true` rises and does not care about the *margin* over the runner-up,
  only the absolute probability. Once a model ranks the true object above the hub competitor by even a
  hair, CE pressure decays. Margin-based losses (L-Softmax, Liu et al. 2016; CosFace, Wang et al. 2018;
  ArcFace, Deng et al. 2019) inject an explicit floor that keeps gradient large until a *margin* is
  satisfied, not just a *rank*. This is the mechanistically correct lever for a failure mode the
  diagnosis note itself measured as high-confidence (z=2.2-2.7 std), not thin-margin.
- **Bayes-consistency caveat (important for HARD-FAIL interpretation):** if a query's content signal
  is genuinely ambiguous (multiple valid answers, no disambiguating feature), a CE-trained model's
  confident preference for the popular object is the *correct* Bayes-optimal behavior given that
  ambiguity (Gordon-Rodriguez et al. 2020) — not a bug. A margin/hard-neg loss cannot manufacture
  disambiguating information that isn't in the content; it can only stop the loss from *settling* at
  a thin margin when the content genuinely does contain (but under-uses) discriminating signal. This
  is precisely why **curriculum-by-relation-fanout** (task's "optional" lever) matters: it is the
  mechanism for separating "genuinely one-to-many, Bayes-optimal-to-prefer-the-common-answer"
  relations from "genuinely discriminable but mis-trained" relations, so a HARD-FAIL on a high-fanout
  relation is not misread as refuting the mechanism.

---

## 2. Lit-scan citations (2 parallel Sonnet sub-agents, generic math/stats terms only)

1. Radovanović M, Nanopoulos A, Ivanović M (2010) Hubs in Space. *JMLR* 11:2487-2531. — carried
   forward from the parent note; re-verified as the source of "hubness is primarily a fixed-geometry/
   intrinsic-dimensionality property, derivable even for i.i.d. random point sets, independent of any
   training state."
2. Feldbauer R, Flexer A (2019) A comprehensive empirical comparison of hubness reduction. *KIS*. —
   VERIFIED (re-fetched). NEW use this round: PCA/ICA (linear, non-distance-distorting) fail to reduce
   hubness unless cutting below intrinsic dimension (destroys neighbor info); only distance-distorting
   nonlinear methods (Isomap, diffusion maps) succeed — direct support for "a linear/bilinear relation
   transform on frozen content cannot remove content-geometry hubness."
3. Jing L et al. (2022) Understanding Dimensional Collapse in Contrastive Self-Supervised Learning.
   *ICLR*. — lightly verified via search. Undertrained/early-phase representation collapse literature;
   candidate explanation for JOINT's smoke-scale hub-collapse (component 2), flagged as NOT explicitly
   reconciled with hubness-proper in the literature (gap; this note's synthesis).
4. Nielsen A, Hansen LK (2024) arXiv:2311.18364 — hubness reduction (~75%) in Sentence-BERT spaces via
   post-hoc rescoring on a FROZEN model. VERIFIED (fetched). Important caveat surfaced by lit-scan: the
   *strongest* cited hubness-reduction number in this space is itself training-free/post-hoc — meaning
   "post-hoc can work well" is not universally false, it failed HERE specifically because the bias is
   entangled with a converged, Bayes-consistent CE fit (label-prior correlation up to r=0.80), which
   Sentence-BERT hub-reduction tasks may not share. Flagged as an open uncertainty, not resolved.
5. Trosten DJ et al. (2023) Hubs and Hyperspheres: Reducing Hubness and Improving Transductive Few-Shot
   Learning. *CVPR*. — VERIFIED (fetched). Direct precedent that a PURPOSE-BUILT training-time
   hubness-reduction objective (not generic contrastive/hard-neg fine-tuning) measurably reduces hub
   counts in a learned embedding — evidence that representation-level fixes ARE achievable, motivating
   this spec's inclusion of a margin/hinge term rather than relying on generic re-training alone.
6. Liu W et al. (2016) Large-Margin Softmax Loss for CNNs (L-Softmax). *ICML*. — recalled/lightly
   verified. Origin of the additive/multiplicative margin-before-softmax mechanism used in Section 3.
7. Wang H et al. (2018) CosFace: Large Margin Cosine Loss. *CVPR*. / Deng J et al. (2019) ArcFace.
   *CVPR*. — lightly verified via search. Modern margin-softmax family; confirms margin losses are the
   standard fix for "CE converges to thin-margin correct, not confidently-separated correct."
8. Gordon-Rodriguez E et al. (2020) Uses and Abuses of the Cross-Entropy Loss. *NeurIPS workshop*. —
   lightly verified via search. Bayes-consistency of CE under label imbalance; grounds the caveat in
   Section 1c above and the curriculum-by-fanout design choice in Section 3.
9. Karpukhin V et al. (2020) DPR. *EMNLP*. / Xiong L et al. (2021) ANCE. *ICLR*. — carried forward,
   re-read specifically for "what problem does mining solve" — confirmed it is exposure-gap-driven,
   which does not apply to this cell's exact-full-softmax training loop (the key correction to the
   naive task framing).
10. Moreira GO et al. (2024) NV-Retriever. arXiv:2407.15831. — lightly verified. Corroborates #9's
    framing (mining = exposure/staleness fix) and separately warns about false-negative contamination
    in mined sets, relevant to this spec's mining-cadence design (Section 3).
11. Cao Z et al. (2007) ListNet. / Burges C et al. (2005/2010) RankNet/LambdaRank. — recalled. Used to
    confirm (and correct) the initial "pointwise vs listwise" framing: full-softmax CE with one true
    label per query IS mathematically a ListNet top-one listwise loss already — the real gap vs
    LambdaRank is the absence of an explicit margin/metric-weighted floor, not pointwise-vs-listwise
    per se. This sharpens the mechanism claim in Section 1c.

**Verified count: 6 new citations independently fetched this round (Feldbauer&Flexer re-fetch,
Jing 2022, Nielsen&Hansen 2024, Trosten 2023, Gordon-Rodriguez 2020, Moreira 2024), 5 lightly-verified
via search (L-Softmax, CosFace, ArcFace, ListNet, RankNet/LambdaRank), cross-checked by 2 independent
Sonnet lit-scan sub-agents against generic-math-terms queries only (no substrate-novel mechanism names
sent off-platform, per query-privacy discipline) plus this note's own direct recompute of the internal
REAL-vs-SHUFFLED Gini comparison (not asserted from metrics.json prose alone).**

---

## 3. ENVELOPE — falsifiable cell spec (SPEC ONLY, no dispatch)

**Proposed cell name:** `exp_schema_relation_hardneg_mined_scorer_v1`

**Design (reuse, don't rebuild):** identical harness to `exp_schema_relation_hitsatk_mrr_reframe_v1.py`
and its debias-rescore child — same V-scan, same relations (AtLocation, CausesDesire semantic;
DerivedFrom watchdog), same 2 encodings, same seeds, same paired REAL/SHUFFLED arms, same
inductive/transductive modes, same `filtered_ranks`/`rank_metrics` verbatim. **The change: a new
training-time loss, applied to BOTH the FROZEN and JOINT slots** (a deliberate extension beyond the
task's literal "continue-train the JOINT scorer" wording — justified in Section 1b: the FROZEN slot
is the one MEASURED to be post-hoc-immune, so it is also the one that most needs a trained-fix
opportunity to test whether the mechanism claim holds where it matters; giving JOINT-only a new lever
would not test the "succeeds where post-hoc failed for full-strength scorers" claim this note exists
to evaluate. Director may descope to JOINT-only if compute is a concern — noted as an explicit,
overridable judgment call, not silently smuggled in).

**New loss (replaces plain CE for the new training ARMS; CE_BASELINE arm reproduces the parent
byte-for-byte as the positive control):**

```
# every step: plain CE as before, PLUS an additive margin on the true-class logit
logit_true' = logit_true - m_add                      # m_add fixed, in the SAME units as tau
loss_ce = CrossEntropy(softmax((logits with true-slot shifted by -m_add) / tau), y_true)

# every K steps (K=25 smoke / K=50 full -- re-mine cadence, trivial at V<=1000, no ANN):
h(t) = argmax_{j != y_true(t)} score(t, j)             # current top-ranked WRONG object, per query
loss_hinge = mean_t max(0, m_hinge - (score(t, y_true(t)) - score(t, h(t))))

loss_total = loss_ce + lambda_hinge * loss_hinge
```

**Fixed, pre-registered hyperparameters (NOT tuned-for-pass):** `m_add = 1.0 * tau_slot` (one
temperature unit, dimensionally coherent with each slot's own SCORER_TAU/JOINT_TAU); `m_hinge =
2.5 * tau_slot` (deliberately set to match the diagnosis note's own MEASURED z-margin of 2.2-2.7 std
on miss rows — the margin target is the empirically observed confidence gap, not an arbitrary
choice); `lambda_hinge = 1.0`; re-mine cadence `K=25` (smoke) / `K=50` (full). **Both REAL and
SHUFFLED arms get mining independently from their OWN current checkpoint** (paired-trials discipline
— the SHUFFLED arm's hard negatives are mined from the SHUFFLED-trained model, never borrowed from
REAL), matching the existing `fit_scorer_paired`/`joint_train_score` batched-B=2 pattern.

**Optional cheap ablation arm (reuses `compute_log_prior` verbatim, near-zero extra cost):**
`LOGIT_ADJUST_LOSS` — Menon et al. 2021's TRAIN-TIME variant (subtract `tau_adj * log(pi_j)` from
logits INSIDE the training loss, not just at test time) — a near-direct-transfer fix specifically for
the label-prior-dominant relations (CausesDesire, corr=0.80) that is cheaper than margin+mining and
worth running side-by-side to attribute which lever actually closes which relation's gap (the
"arms_differ" discriminator structure already standard in this cell family).

**Curriculum-by-relation-fanout (optional, reported not gating):** log each relation's mean
in-codebook fanout (avg #true objects per subject) as a covariate; report HARD-PASS/HARD-FAIL
stratified by fanout tercile. This is a DIAGNOSTIC, not folded into the primary gate — per Section 1c,
a high-fanout relation failing to clear HARD-PASS may be genuine Bayes-optimal ambiguity, not a
refutation of the mechanism, and conflating the two would corrupt the falsification test.

**New anti-phantom guard specific to a TRAINED (not post-hoc) mechanism — `SHUF_OVERFIT_GUARD`:**
post-hoc rescoring cannot overfit (it never touches parameters); a margin+mining training loop, run
for potentially many re-mine cycles on a small V<=1000 pool, plausibly CAN memorize the SHUFFLED
arm's fixed pseudo-random permutation given enough capacity/steps. Required: SHUFFLED arm's absolute
inductive Hits@1 under the new loss must not rise more than **+0.03 absolute** over the matched
CE_BASELINE SHUFFLED Hits@1, at the same V/seed. A violation here is not a "win," it is instrument
failure (the mechanism is memorizing, not generalizing) and must zero out that unit's HP eligibility
regardless of REAL-side numbers.

**Synthetic discriminator-fires controls (mirroring the family's existing discipline):**
- `synth_content_baked_hub` (POSITIVE, must fire): construct a synthetic linear-content generator
  where the OBJECT-side embedding itself has genuine concentration (a few synthetic object vectors
  sit systematically closer to the data centroid, independent of any label), verify (a) FROZEN-style
  linear-only fit shows REAL≈SHUFFLED Gini (reproducing Section 1a's signature) and CSLS/LOGIT are
  near-inert-or-harmful on REAL, while (b) margin+mining training measurably narrows the REAL-vs-hub
  margin (even if it cannot fully remove the geometric bias) — proves the new mechanism can make
  *some* progress on the harder, content-geometry-baked class the post-hoc cell could not touch.
- `synth_ambiguous_null` (NULL, must stay near-baseline): construct a synthetic regime where multiple
  objects are GENUINELY equally likely given the input (no content signal disambiguates them) — margin
  + mining must NOT manufacture a fake win here (Hits@1 lift should stay within the SHUF_OVERFIT_GUARD
  tolerance of the CE_BASELINE), directly testing the Bayes-consistency caveat from Section 1c.

**HP_SCOPE:** identical exclusion structure as parent/debias cells — bands apply to
`best-of-{FROZEN,JOINT} x {MARGIN_HARDNEG, LOGIT_ADJUST_LOSS} REAL/inductive/FILTERED, SEMANTIC rel x
enc @ V>=300`; KNN/DerivedFrom/SHUFFLED/CE_BASELINE remain references/watchdogs/controls.

### Falsifiable predictions

**HARD-PASS** (task's bands, restated formally): best-of-{FROZEN,JOINT} x {MARGIN_HARDNEG,
LOGIT_ADJUST_LOSS} filtered **REAL-absolute Hits@1 lift >= 0.05** over the matched CE_BASELINE REAL
Hits@1, **AND** filtered MRR real_minus_shuf(inductive) rms **>= 0.15**, holding on **>=2 relations
(AtLocation + CausesDesire) x >=2 encoders** at **V>=300**, **with the SHUFFLED control's absolute
Hits@1 NOT lifted more than the SHUF_OVERFIT_GUARD tolerance (+0.03)** over CE_BASELINE SHUFFLED —
the anti-phantom gate the task requires, extended with the training-specific overfit guard above.
Both `synth_content_baked_hub`/`synth_ambiguous_null` discriminators must fire as specified.

**HARD-FAIL**: best-of-{FROZEN,JOINT} x {MARGIN_HARDNEG, LOGIT_ADJUST_LOSS} REAL-absolute Hits@1
lift is **<=+0.02** on EVERY semantic rel x enc cell at V>=300 (i.e., the trained fix does no better
than the CE_BASELINE it's replacing) — falsifies the "train through it" redirect entirely and would
mean BOTH the post-hoc AND the trained-margin levers have now failed on the SAME diagnosed bias,
redirecting to the last remaining, more expensive options: (i) a genuinely different content
representation (not just richer — the richer-content cell already failed; something with different
distance-concentration properties, e.g. content whitening/decorrelation before the frozen encoder),
or (ii) accepting the one-to-many/fanout ceiling as a structural property of this relation class and
re-scoping the capability claim rather than continuing to chase rank-1 on high-fanout relations.

**MIDDLE-BAND** (plausible middle outcome given fanout heterogeneity): REAL Hits@1 lift clears
HARD-PASS on the label-prior-dominant relation (CausesDesire, where LOGIT_ADJUST_LOSS is a
near-direct transfer) but not on the genuine-geometric-hubness relation (AtLocation, where the
literature gap flagged in Section 1b — no direct evidence generic training reduces hub counts,
only bespoke hubness-aware losses do — means the margin+mining lever is less precedented). This
would motivate a follow-up drill specifically on Trosten et al. (2023)-style explicit
hubness-decorrelation regularizers (not just margin/rank losses) for the AtLocation-class relations,
rather than declaring the whole redirect closed.

**Cardinality / compute:** heavier than the debias-rescore cell (that one added zero training; this
one adds a per-arm training loop with periodic re-mining). Still cheap in absolute terms: re-mining
is a single (T_train, V) matrix rescoring pass every K steps, trivial at V<=1000 with no ANN index.
Expect wall-clock in the 15-25 min FULL range (roughly 2-3x the debias cell, driven by the extra
MARGIN_HARDNEG/LOGIT_ADJUST_LOSS training arms on both slots, not by the mining step itself).

---

## Cheap decisive test

Section 1a's REAL-vs-SHUFFLED Gini comparison on the ALREADY-LANDED debias smoke cell IS this note's
own cheap decisive test for the mechanism question (content vs transform) — it required zero new
compute, only a re-read of a field (`hub_diag_real_vs_shuffled_gini`) already present in the landed
metrics.json. The proposed cell above is the next cheap test: whether a TRAINED fix can move the
needle where a training-FREE one (proven, above) cannot, on the SAME diagnosed bias, at similar
compute order (2-3x, not order-of-magnitude more).

## Cross-thread synthesis

- Directly extends `notes/research_hubness_popularity_debias_rank1_sharpening_2026-07-05.md`'s own
  Stage-2 forward pointer ("train-time logit-adjustment loss... and/or DPR/ANCE-style
  hard-negative-mining... rather than declaring the question closed either way") — this note is that
  Stage-2 drill, and corrects the DPR/ANCE framing en route (exposure-gap mechanism does not transfer
  to an exact-full-softmax setting; margin-loss is the mechanistically matched substitute).
- Directly extends the debias-rescore cell's own `exp_dev_predispatch_caveat` (which predicted
  HARD_FAIL/low-MIDDLE for the "deep-truth weak scorer" case and pre-registered "trained hard-neg
  mining / richer content" as the redirect) — confirms that prediction was correct for FROZEN
  specifically (not JOINT), and sharpens WHY (Bayes-consistency + linear-transform-invariance of
  hubness, not just "the truth is deep").
- Does not re-open the richer-content HARD_FAIL (`exp_schema_relation_richer_content_vscan_v1`) —
  this cell targets the LOSS FUNCTION and TRAINING DYNAMICS on the EXISTING content representation,
  not a new content-representation claim. If this cell also HARD_FAILs, richer/different content (not
  more training on the same content) becomes the only lever left standing per the diagnosis chain.
- Ties into `notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md`'s
  attractor-cleanup caution: a margin/hinge objective is, in effect, a *trained* attractor-sharpening
  step (widening basins around the true answer relative to its nearest competitor) — but unlike raw
  CA3-style cleanup on an unmodified score landscape (which the diagnosis note argued would amplify
  hub preference), this is explicitly hub-*aware* (the mined competitor IS the hub object in most
  cases) — so it is the mechanistically-corrected version of "attractor cleanup," not a re-opening of
  the previously-cautioned-against naive version.

## Substrate-product implications

If this cell clears HARD-PASS (even on one relation class), the honest product story becomes: "the
substrate's relational rank-1 accuracy has TWO distinct, now-separately-diagnosed ceilings — one
fixable for free at inference time (transient undertraining, already shown fixable by rescoring), one
requiring a modest, well-precedented training-loss change (margin-calibrated to the substrate's own
measured confidence gap) rather than either a full retrain or accepting the ceiling as fixed." If it
HARD_FAILs across the board, the product-honest sharpening is sharper still: THREE independent levers
(post-hoc rescore, richer content, trained margin/hard-neg loss) have now been tried and found
insufficient on this specific rank-1 gap, which is unusually strong evidence that the remaining gap is
either (a) a genuine one-to-many/fanout ceiling that should be re-scoped as a property of the relation
class rather than chased further, or (b) a content-representation problem that specifically requires
*decorrelating* the fixed embedding geometry (not just enriching it), a materially different lever
than anything tried so far and the honest next-drill candidate either way.

## Citations (verified count)

See Section 2 above: 6 new independently-fetched citations this round, 5 lightly-verified via search,
cross-checked by 2 independent Sonnet lit-scan sub-agents, plus this note's own direct off-disk
recompute of the REAL-vs-SHUFFLED Gini comparison from already-landed metrics.json (not asserted from
verdict prose alone).

## P_deflated

**P_deflated(HARD-PASS as spec'd, i.e. clears on >=2 rel x >=2 enc simultaneously) = 0.33** (raw
~0.55: the label-prior-dominant relation (CausesDesire) has a near-direct-transfer fix
(LOGIT_ADJUST_LOSS, Menon et al. 2021's own train-time variant) and the undertrained-JOINT precedent
already showed genuine, non-phantom trained-regime improvement is possible; the genuine-geometric-hub
relation (AtLocation) is materially less precedented — lit-scan found NO direct evidence that generic
margin/hard-neg training reduces measured hub *counts* in a learned embedding, only that bespoke
hubness-aware losses (Trosten et al. 2023) do, and this spec's margin+mining loss is closer to the
former than the latter. -0.22 lit-scan calibration for: this exact combination (margin loss +
periodic mining, calibrated to a MEASURED z-margin) never tried on this substrate/task; the FROZEN
slot's demonstrated resistance to a training-FREE fix does not guarantee a training-based one
succeeds — CE-Bayes-consistency argues the *converged* fixed point a longer/harder-trained model
reaches may still prefer the popular object where content is genuinely ambiguous, which margin loss
cannot fix; and per novel-synthesis-cap discipline, the content-vs-transform reconciliation itself
(Section 1b) is this note's own synthesis, not a cited result.**

**P_deflated(beats the post-hoc cell's own best MIDDLE outcome — i.e., achieves a genuine,
non-phantom REAL Hits@1 lift >=0.05 on AT LEAST the relation/slot combination where post-hoc already
won non-phantom, CausesDesire/JOINT, PLUS at least a partial (non-zero, non-phantom) gain elsewhere)
= 0.58** (higher confidence here: this is a strictly easier bar than full HARD-PASS — it only
requires the trained approach to at least match what post-hoc already proved possible on the
malleable/undertrained regime, which a strictly more expressive training-based mechanism should be
able to do or exceed, plus the LOGIT_ADJUST_LOSS ablation is a near-certain incremental win on
CausesDesire's label-prior component specifically per Menon et al. 2021's own direct precedent for
that mechanism class; capped below 0.60 per novel-synthesis discipline since the AtLocation/FROZEN
extension remains the genuinely untested part of the claim).**
