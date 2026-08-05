# Adversarial re-VET: thematic_role_labeler_cue_integration_v1

**Auditor:** hdi_skunkworks (AUDIT-ONLY; independent off-disk recompute, no writes to cell/data/module)
**Anchor:** thematic_role_labeler_cue_integration_v1 (commit d71da0858)
**Reported:** HARD_PASS, full_acc=0.8666 vs positional=0.6032 (lift +0.2635), scramble collapse, frame_only@0.6984, n_test=63, resolve_rate=0.62
**Verdict:** **DOWNGRADE -> MIDDLE_BAND** (axis-masked; earned mechanism net-harmful on the load-bearing axis; in-vocab-only; end-to-end ~0.43-0.54)
**Wire decision:** **SHELVE / needs-more-work** -- do NOT wire as the Component-3 goal-owner organ.

Recompute reproduced the headline EXACTLY (my full_acc=0.8667 across the same 5 seeds), so the aggregate number is real. Every finding below is off my own re-derivation from the cell logic + data, not metrics.json.

---

## The one-line headline is masking the axis that matters

Aggregate 0.867 is carried by **41 easy ditransitives** (0.951). The load-bearing goal-owner axis (experiencer / psych-verb subject) is **0.614**, and on the *literal* goal-owner subjects (gold=EXPERIENCER, n=7) it is **0.657**.

| slice | n (test) | full (earned) acc |
|---|---|---|
| **aggregate (headline)** | 63 | **0.867** |
| ditrans axis | 41 (29 supplement + 12 auto) | **0.951** |
| passive axis | 8 (supplement) | 0.875 |
| **experiencer axis** | 14 (10 auto + 4 supplement) | **0.614** |
| gold=EXPERIENCER subjects only | 7 | **0.657** |
| auto-real (all) | 22 | 0.891 |
| auto-experiencer only | 10 | **0.70** |
| supplement-experiencer only | 4 | **0.25** |

The "auto-real is weak" hypothesis is FALSE (auto-real=0.891) -- but only because auto = 10 experiencer + 12 *perfect* ditrans; the auto-experiencer slice alone is 0.70. Ditransitives (46% of the test set) inflate every aggregate they touch.

## Check 4 (earned vs supplied) -- THE decisive finding: earned integration is NET-HARMFUL on the goal-owner axis

The earned averaged-perceptron (the actual deliverable) does NOT deliver goal-owner attribution -- supplied knowledge does, and the earned part **degrades** it:

| experiencer axis | full (earned) | frame_only (supplied) | positional |
|---|---|---|---|
| all 14 exp-axis | **0.614** | **0.857** | 0.429 |
| gold=EXPERIENCER only (7) | **0.657** | **0.857** | 0.000 |

Earned lift on the experiencer axis = **-0.24** (frame_only 0.857 -> full 0.614). The +0.17 aggregate "earned lift" (0.698 frame -> 0.867 full) lands ENTIRELY on ditransitives. Mechanism: the perceptron learned `order:pre -> AGENT` from the canonical-dominated train set and overrides the correct verb-frame signal for pre-verbal experiencer subjects -- a textbook Competition-Model cue-conflict failure. **earned-helps-experiencer = NO (it hurts).** The goal-owner capability is entirely a property of the SUPPLIED psych-verb frame dict.

## Check 6 (OOV) -- experiencer result is IN-VOCAB-ONLY; OOV structurally fails to AGENT

- Auto-experiencer axis is 100% in-vocab **by construction**: cell line 160 tags `experiencer` iff `v_lemma in PSYCH_VERBS`, so every auto psych verb is in the supplied dict.
- Supplement experiencer verbs: fear/hate/want/remember all in dict.
- `frame_slot_role` does `VERB_FRAMES.get(lemma, DEFAULT_FRAME)` -> an OOV psych verb gets subj=**AGENT**. Demoed: cherish/loathe/crave/resent/covet/begrudge ALL -> AGENT. No frame-learning exists; verb-frame knowledge is static.

So even the frame_only=0.857 experiencer number is in-vocab-only; long-tail psych verbs are structurally mislabeled AGENT -- the exact goal-owner failure the organ was built to fix. The experiencer win = supplied-dict recognition of specific verbs, not earned generalization.

(Incidental bug found: `lemma_verb("likes") -> "lik"` (suffix-strip), which is NOT in VERB_FRAMES -> falls to DEFAULT_FRAME -> subj=AGENT. This is why supplement-experiencer acc=0.25. A real lemmatizer defect, but a side issue.)

## Check 2 (protocol) -- deviation SOUND & disclosed, BUT coarse-feature leakage is severe

- The 50/50 train-exposure/held-out split IS legitimate and honestly disclosed: I confirmed a linear perceptron structurally cannot predict a zero-exposure class (argmax over classes with zero training mass). The rationale is TRUE.
- The split is by SENTENCE/RECORD (`_split_units`); no within-sentence leak, deterministic. Sentence-level protocol is clean.
- **BUT the feature representation is so coarse that 58/63 (92%) test examples have an EXACT feature-vector duplicate in train** (all 29 supplement + all 12 auto ditransitives; 7/7 supplement passives; etc.). "Held-out sentences" are featurally identical to trained ones. For the 0.95 ditrans axis this is near-memorization of a feature pattern reproduced on the same pattern -- NOT generalization to unseen constructions. This is the aggregate-inflation mechanism, orthogonal to (and more damaging than) the disclosed split deviation.

## Check 3 (supplement integrity) -- CLEAN labels, but templatic/easy on the easy axis

The 36 hand-authored records are naturalistic McGuffey-register and CORRECTLY thematic-role labeled (spot-checked all 36); not cherry-picked-tricky, not mislabeled. But 20/36 are near-templatic ditransitives ("X gave/told/sold Y Z") -> 29/63 test items (46%) all in the easy 0.95 axis. Honest data, but its composition structurally tilts the aggregate toward the axis that didn't need the earned mechanism.

## Check 5 (resolve_rate) -- labeler scored only on the easy-to-parse 62%

Confirmed 62/100 gold triples resolved (agent+patient both found); 38% failed upstream (candidate-gen) and are excluded from scoring. Honest end-to-end on real text:
- aggregate: ~0.62 x 0.87 ~= **0.54** effective (if unresolved=wrong)
- **goal-owner (auto-experiencer): ~0.62 x 0.70 ~= 0.43** end-to-end.

---

## Scope of what was actually proven
- Mechanism-class (averaged-perceptron cue-integration) fits ditransitive/RECIPIENT structure at 0.95 -- but featurally near-memorized + on templatic supplement, so this is a weak generalization claim.
- Scramble-collapse and no-single-cue-match controls DO pass (verified) -- the weights aren't decorative in aggregate; but that aggregate is dominated by ditrans.
- The organ does NOT prove the load-bearing capability: earned goal-owner (experiencer) attribution. On that axis it is (a) below the supplied-frame baseline, (b) in-vocab-only, (c) ~0.43 end-to-end.

## Residual risks (ranked)
1. **Earned mechanism is net-harmful on the goal-owner axis (-0.24 vs supplied frame).** The deliverable degrades the capability it targets. TOP risk.
2. **In-vocab-only; OOV psych verbs -> AGENT.** No frame induction; static dict. Real-world long-tail fails exactly where goal-owner matters.
3. **92% feature-level train/test overlap** -- "held-out generalization" is largely reproduction of seen feature patterns.
4. **End-to-end ~0.43 (goal-owner) / ~0.54 (aggregate)** once 38% unresolved counted.
5. Aggregate dominated by 46% templatic ditransitives; lemmatizer `likes->lik` defect.

## Recommendation: SHELVE (needs-more-data + rebuild), do NOT wire
Revival criteria before this can be the Component-3 organ:
1. Earned integration must BEAT frame_only ON the experiencer axis (currently -0.24) -- fix the order-cue-overrides-frame conflict (per-verb-class cue weighting / lexical gating).
2. OOV psych-verb handling: learned frame induction/bootstrapping, not a static ~150-lemma dict; report OOV-verb accuracy explicitly.
3. Finer features so held-out items are featurally novel (kill the 92% overlap), then re-measure generalization.
4. Report end-to-end (incl. the 38% unresolved), not on-resolved-only.
5. Fix lemma_verb("likes")->"lik".

---
### One-line report
`skunkworks_reVET_thematic_role_labeler_cue_integration_v1.md | experiencer-axis-acc=0.614 (goal-owner-subj-only=0.657) | auto-real-acc=0.891 (auto-exp-only=0.70) | protocol-sound=Y (split ok; 92% feature-level leakage=N) | supplement-clean=Y (labels correct; templatic/easy) | earned-helps-experiencer=N (-0.24, HURTS) | end-to-end-effective=~0.54 agg / ~0.43 goal-owner | verdict=DOWNGRADE_MIDDLE | wire=SHELVE`
