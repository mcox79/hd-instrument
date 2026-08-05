# Adversarial re-VET: frame_primary_role_assigner_v1

**Auditor:** hdi_skunkworks (AUDIT-ONLY; independent off-disk recompute + fresh re-run, no writes to cell/data/module)
**Anchor:** frame_primary_role_assigner_v1 (commit 7d41ca28d). Fix = hdlab/frame_induction.py::frame_primary_role()
**Reported:** HARD_PASS, subj-exp axis acc=0.8769 (N=65), beats perceptron-0.614 + default-0.0, frame-ablation->0.0, no-override=1.0, obj-exp deferred=0.396
**Verdict:** **DOWNGRADE -> MIDDLE_BAND** (headline conflates trivial dict-lookup with a coarse animacy proxy; two load-bearing controls near-vacuous on this axis; cross-dataset baseline; the genuine frame-beats-position hard case is DEFERRED)
**Wire decision:** **WIRE the ARCHITECTURE (frame-primary, known-verb-unconditional) as the Component-3 subject-experiencer organ, WITH corrected numbers + documented caveats** -- the fix is real and strictly better than the shelved perceptron; do NOT propagate 0.877 as a capability figure.

I re-ran the cell fresh in .venv (reproduced exactly: HARD_PASS, 0.8769, plugin=ruleind, oov=0.7667, known=1.0, partial_ablation=0.796875) and re-derived every slice from raw per-record + a same-data baseline the cell never computed. All findings below are off my own recompute, not metrics.json.

---

## Director's 4 concerns -- all CONFIRMED

**1. Aggregate inflation -- CONFIRMED.** 0.877 = 34 KNOWN-lemma cases at acc 1.0 (a deterministic `VERB_FRAMES[lemma]['subj']` dict lookup -- trivially correct, zero learning) + 23/30 OOV. The honest EARNED number is **0.767 (N=30)**. Worse, the cell reports NO same-data frame baseline: I computed **frame_only same-data = 0.523** (34 known correct, all 31 OOV -> AGENT). So the real same-data lift from the earned component is 0.523 -> 0.877, and the honest earned capability is 0.767 on 30 cases. Reporting 0.877 as "the capability" is misleading. **aggregate-misleading = Y.**

**2. OOV is a position+animacy proxy -- CONFIRMED CONCLUSIVELY.** The induced ruleind hypothesis's load-bearing rule is `['order_pre','arg_animate'] -> EXPERIENCER` (coverage 37, precision 0.838). Behavioral probe: EXPERIENCER fires ONLY when `arg_animate` is present (order_pre alone -> OTHER; order_pre+has_scomp -> OTHER; order_pre+degree_mod -> OTHER). On the subject axis order_pre is universal, so the effective rule reduces to **`arg_animate -> EXPERIENCER`**. Decisive recompute: across all 30 resolved OOV cases, `arg_animate == correct` in **30/30**. Every OOV miss (her heart craved / Wickham cherished the hope / Emma grieved for her / Rawdon marvelled / Dick marveled that / esteem him dearly / women revere men) lacks `arg_animate`; every OOV hit has it. scomp/degree/passive do NOT drive the subject-axis result. The "earned construction-frame induction" is a one-feature animacy heuristic, not genuine syntactic bootstrapping. **is-OOV-a-position-proxy = Y.**

**3. Override control near-vacuous -- CONFIRMED.** no-position-override=1.0 over N=51 pre-verbal-animate records -- but on the SUBJECT-experiencer axis subjects ARE pre-verbal and animate, so position and frame AGREE (frame says EXPERIENCER; the induced animacy rule ALSO says EXPERIENCER). Nothing is actually overridden. The genuine frame-must-beat-position case is the POST-verbal experiencer = object-experiencer, which is **DEFERRED (0.396, near chance-of-the-wrong-class)**. The control does not demonstrate frame-beats-position in the hard case. **override-control-vacuous = Y.**

**4. Cross-dataset baseline -- CONFIRMED apples-to-oranges.** 0.614 is the shelved perceptron on the OLD McGuffey-gold set (n=14), cited absolute, NOT re-run head-to-head. On THIS data the honest same-data baselines are default-AGENT=0.0 (degenerate: every subj gold is EXPERIENCER, so all-AGENT is all-wrong by construction) and frame_only=0.523 (not reported). "beats 0.614" is not a fair comparison. **baseline-fair = N.**

## Also-checks
- **LEAK -- CLEAN.** `build_train_corpus(exclude_lemmas=set(oov_subj_lemmas))` drops every record whose verb lemma is one of the 18 OOV subj lemmas, entirely (not just the split-flagged half). Lemma is never a feature (verified in `real_construction_feats`); the induced rule is surface-cue-only. No OOV test lemma appears in training. **leak-clean = Y.**
- **frame-ablation=0.0 -- real but WEAK.** Forcing all preds to AGENT trivially yields 0 because the axis gold is a degenerate constant (all EXPERIENCER). It proves "some frame signal carries the result" only in the weak sense that removing it leaves you predicting the wrong constant class. Not a strong discriminator.
- **Architectural fix -- REAL and non-trivial.** `frame_primary_role` returns `frame_slot_role(lemma,'subj')` UNCONDITIONALLY for known verbs -- no position/animacy re-ranking layer exists. This genuinely removes the shelved perceptron's blanket `order:pre -> AGENT` override that caused the prior -0.24 earned-harm regression (known-lemma acc 1.0 here vs perceptron experiencer 0.614). The fix IS verb-class-conditioned (via the supplied VERB_FRAMES dict) and frame-primary. **is-architectural-fix-real = Y.**

## Adjudication
Unlike the prior lineage version (earned mechanism NET-HARMFUL, -0.24), this is NOT harmful: the architecture is correct-by-construction for known psych verbs and the OOV path is net-positive (lifts OOV 0.0 -> 0.767). The DESIGN is the right one and unblocks the goal-owner pipeline. But the CELL does not earn a HARD_PASS as a capability: the headline 0.877 is 52% trivial dict-lookup, the "earned" remainder is a coarse animacy proxy, both gating controls are weak on this degenerate axis, and the one case that would prove frame-primary (post-verbal experiencer) is deferred at 0.396.

## Residual risks (ranked)
1. **Object-experiencer (the real frame-beats-position hard case) is unsolved (0.396).** Component-3 goal-owner needs it; deferring it means the load-bearing capability is not demonstrated. TOP risk.
2. **OOV "induction" is a single-feature animacy heuristic**, not construction-frame semantics -- long-tail psych verbs with inanimate/oblique subjects (her heart craved, women revere men) mislabel AGENT. scomp/degree/passive contribute nothing on this axis.
3. **Headline 0.877 will propagate as a capability number if wired uncaveated** -- it is 34/65 deterministic dict-lookup; honest earned = 0.767 (N=30).
4. **No same-data baseline reported** (frame_only=0.523); the cited 0.614 is cross-dataset (n=14).
5. Degenerate axis gold (all EXPERIENCER) makes default-AGENT and frame-ablation trivially 0 -- weak discriminators.

## Recommendation: WIRE the architecture, at MIDDLE_BAND, with corrected numbers
- WIRE `frame_primary_role` (known-verb-unconditional, no re-ranking) as the Component-3 subject-experiencer organ -- it is the correct design and strictly better than the shelved perceptron; refusing would leave a worse state.
- Record it in the capability registry at its HONEST tier **MIDDLE_BAND**, with: known-verb subj = 1.0 (supplied dict), OOV subj = 0.767 (coarse animacy heuristic, flag as such -- NOT "learned construction-frame induction"), object-experiencer = 0.396 OPEN GAP. Do NOT bank 0.877 as the capability figure.
- Revival-to-HARD_PASS criteria: (1) object-experiencer axis solved (post-verbal experiencer where frame must beat position); (2) OOV path shows a cue BEYOND animacy is load-bearing (scomp/degree/passive currently inert); (3) report same-data frame_only baseline, not the cross-dataset 0.614.

---
### One-line report
`skunkworks_reVET_frame_primary_role_assigner_v1.md | earned-OOV-acc=0.767(N=30) | is-OOV-a-position-proxy=Y (rule=order_pre&arg_animate; 30/30 animate==correct) | is-architectural-fix-real=Y | aggregate-misleading=Y (0.877=34 dict-lookup+23/30 earned; same-data frame_only=0.523) | override-control-vacuous=Y (pos==frame on subj axis; hard case=obj-exp deferred 0.396) | baseline-fair=N (0.614 cross-dataset n=14) | leak-clean=Y | verdict=DOWNGRADE_MIDDLE | wire=WIRE (architecture only, corrected numbers + caveats)`
