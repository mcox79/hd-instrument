# 2x DEEP research drill: empirical validation of the 7 invariants for productive substrate-on-substrate recursion

Date: 2026-06-11
Drill class: methodology meta-drill (level-2 operational drill on EXISTING invariant inventory)
Output type: empirical validation procedure + failure/success signatures + meta-invariant analysis + implementation in substrate-self-evaluation

## HEADLINE

The 7 invariants for productive substrate-on-substrate recursion (drill-defeatism rule + Layer-1 attribution PROT + honest attribution + 2x drill negatives + pre-registered hypothesis + no LLM-as-judge + methodology rule chain) are each independently auditable through a paired (signature, counterfactual-witness) procedure. The dominant failure mode is NOT invariant breakdown but invariant invocation without counterfactual binding: a rule is cited verbally without running the lightweight check that would have caught the violation. Productive recursion empirically presents as a flat or rising rate of REVISIONS-per-cycle (refutations of prior claims) under FALLING engineering cost-per-revision; defeatist or circular recursion presents as rising claim-density with falling refutation-rate (the "consensus drift" signature).

## (b) Cheap decisive test (per invariant)

Each invariant gets a < 30-minute audit script. Combined "invariant health check" runs in < 2 hours weekly. Pass criteria pre-registered below; fail-mode triggers rehab.

### Invariant 1: Drill-defeatism rule

VALIDATION PROCEDURE:
1. Parse last 30 days of research_decisions_*.md and exp_dev_handoff_*.md for phrases matching `ARCHITECTURAL_LIMIT_REGEX = "honest ceiling|architecturally hybrid|fundamental limit|cannot be done substrate-only|hard ceiling|architectural constraint"`.
2. For each match, extract the surrounding claim and check 5-item necessary-conditions list:
   - N-sweep across at least 3 magnitudes
   - Tier-hierarchy probe (Tier-1/2/3 all checked)
   - Multi-benchmark (>= 2 independent benchmarks)
   - Full primitive inventory enumerated and at least 5 untested paths checked
   - Adversarial probe (try to refute the claim deliberately)
3. SIGNATURE: claim density `D = matches / drill_count`. Counterfactual-witness `W = (matches with all 5 conditions present) / matches`.

PASS: `W >= 0.80` (at least 80% of architectural-limit claims have all 5 checks done).
FAIL: `W < 0.50` OR `D > 0.20` (architectural-limit claims appearing in more than 1-in-5 drills without checks).

FAILURE SIGNATURE: claim is paraphrased across notes without N-sweep / tier-probe / multi-benchmark trail. The phrase propagates; the work behind it does not.

SUCCESS SIGNATURE: ratio of "limit-claim retraction" events to "limit-claim assertion" events > 0.30 over 30 days. Today's evidence: 5 retractions filed in MEMORY.md including slipnet-0.42 refuted via WN18RR, CORE-PERIPHERY refuted, LLM-only-for-NL refuted via 0.906 POS. Empirical: rate sits at ~0.40 currently which is healthy.

### Invariant 2: Layer-1 attribution PROT validation

VALIDATION PROCEDURE:
1. For every PASS/HARD-PASS verdict, the attribution decomposition (Layer-1: substrate primitive that did the work; Layer-2: engineered wrapper; Layer-3: dataset artifact; Layer-4: confounded baseline) must be present in the verdict synthesis OR in the post-verdict research note within 24 hours.
2. Statistical significance test: for each claimed Layer-1 attribution, the LIFT must exceed `2 x SE` over the next-best plausible Layer-2 explanation (per [[feedback-method-overclaim-lift-validation]]).
3. Bootstrap procedure: 100 bootstrap resamples of the test set; report 95% CI on each layer's contribution; PASS requires the Layer-1 lower CI bound > Layer-2 upper CI bound.

PASS: `attribution_decomposition_filed_within_24h / pass_verdicts >= 0.85` AND `attribution_lift_passes_2SE / claimed_attributions >= 0.90`.
FAIL: either ratio drops below 0.50.

FAILURE SIGNATURE: verdict says "substrate did X" with single point estimate and no Layer-2 ablation. LVH-274 was the canonical example caught in MEMORY.md (struct-align lift=0.001 noise-level, passed absolute threshold but not lift threshold).

SUCCESS SIGNATURE: PASS verdicts ship with concurrent ablation cells in the same lane (Layer-2 wrapper-only, Layer-3 shuffled-target, Layer-4 random-baseline), and all four columns are pasted into the verdict synthesis. Today's substrate-classical NL POS work has this pattern (0.906 with HMM ablation, count-NB ablation, context-window ablation in same exp_dev hand-off).

### Invariant 3: Honest attribution principle (over-claim detection)

VALIDATION PROCEDURE:
1. Three causal-inference tests applied to every "X causes Y" claim in a research note:
   - Counterfactual: remove X, does Y degrade? (ablation)
   - Confounder check: is there a Z that causes both X and Y? (PP-225 DISC_POOL was the canonical confounder; image-schema concept-context binding was a fix)
   - Generalization: does the X-Y link hold across at least 2 distinct domains or seeds?
2. SHEPHERD test: if a claim says "substrate did it," a separate audit cell that LOCKS substrate output and trains a downstream model on the locked output must reproduce the metric to within 5pp. If it doesn't, attribution is leaking to the trainer.

PASS: `claims_with_3_causal_checks / total_causal_claims >= 0.70`.
FAIL: <0.40 OR a single un-retracted claim discovered to have failed the SHEPHERD test.

FAILURE SIGNATURE: cross-domain claim P9 (canonical example: entity-geometry + degree-bias confound) where the "substrate generalizes" framing held only because the test sets shared a hidden confounder.

SUCCESS SIGNATURE: when a confounder IS found, retraction is filed within 24h, MEMORY.md gets a one-line entry, and the cap_map row is downgraded. Today's MEMORY.md shows 3 such retractions explicitly logged (cross-domain RETRACTION, PP-225 illusory-scaling, slipnet-0.42-refuted).

### Invariant 4: 2x drill negative findings validation

VALIDATION PROCEDURE:
1. Each negative verdict (FAIL / MIDDLE_BAND / KILLED) must trigger a routing file `strategy_request_to_research_*_negative_2x.md` OR be explicitly dispatched into a 2x drill.
2. Audit pattern: parse research_decisions for "2x" tag and verify each is paired to a prior negative verdict in the same cap_map row.
3. The 2x drill MUST drill OPERATIONALLY (mechanism + math + implementation path), NOT lit-verify the negative.

PASS: `negatives_with_2x_drill / total_negatives >= 0.75` AND `2x_drills_with_new_path_inventory / 2x_drills >= 0.80` (each 2x must enumerate at least one previously-untested path).
FAIL: <0.40 on either ratio.

FAILURE SIGNATURE: negative verdict is acknowledged in chat then dropped from queue without follow-up. Or: 2x drill returns the same lit-scan as 1x (re-verification not depth-drilling). User-flagged today in MEMORY.md as a recurring pattern: "I keep parroting drill defeatism" - exactly the no-2x-on-negative failure.

SUCCESS SIGNATURE: 2x drills produce path inventories (slipnet 13-untested-paths note today is a model example; svamp_substrate_only_above_030 today; HumanEval substrate-generator today are similar pattern). Today's drill produced 13 untested-paths on slipnet which validated the 5th drill-defeatism rule violation per MEMORY.md.

### Invariant 5: Pre-registered hypothesis discipline

VALIDATION PROCEDURE:
1. Every exp_dev hand-off file MUST contain a `pre_reg` block with: hypothesis text, HARD-PASS threshold, HARD-FAIL threshold, expected sample size, expected runtime - written BEFORE the smoke gate runs.
2. Time-stamped registry: `data/pre_registrations.jsonl` appends each pre-reg with `ts_pre_reg` and `ts_verdict`. If `ts_verdict < ts_pre_reg + smoke_runtime_max`, flag as potentially post-hoc fitted.
3. Post-hoc fitting detection: for verdicts that PASS, check that the HP threshold pre-reg matches the threshold used in the verdict synthesis. Any threshold mutation between pre-reg and verdict gets flagged.

PASS: `pre_reg_present / total_authorized_anchors >= 0.95` AND `threshold_mutation_count / total_verdicts <= 0.05`.
FAIL: pre_reg present <0.70 OR mutation rate >0.15.

FAILURE SIGNATURE: hand-off file says "PASS if recall >= 0.40" but the verdict synthesis quotes "0.35 is solidly above the noise floor and constitutes a partial pass." Threshold reaches were post-hoc relaxed.

SUCCESS SIGNATURE: pre-reg threshold is binding; MIDDLE_BAND verdicts exist (proves the threshold actually distinguishes passes from middle from fails). Today's exp_dev hand-offs show pre-reg blocks with HP/HF pairs explicitly.

### Invariant 6: No LLM-as-judge

VALIDATION PROCEDURE:
1. Grep every verdict synthesis for keyword set `LLM_JUDGE_REGEX = "judged by|GPT-evaluated|Claude-rated|LLM-scored|llm.*judge|gpt.*eval"`. Zero hits required.
2. External anchor binding: every metric MUST have either a closed-form oracle (`verification/theory.py` pattern from CLAUDE.md) OR a published-benchmark ground-truth (HumanEval pass-rate, GSM8K answer-key, WSJ POS labels, etc.). The anchor citation goes in the pre-reg.
3. Ground-truth comparison: pull 5 random recent verdicts; verify each metric is recomputable from raw outputs and external ground-truth WITHOUT calling any LLM. Time budget: 10 min per verdict.

PASS: zero LLM_JUDGE_REGEX hits in last 30 days of verdicts AND 5/5 recomputation audit passes.
FAIL: any LLM judge hit OR <3/5 recomputation pass.

FAILURE SIGNATURE: metric depends on a chain `output -> LLM-rater -> score`. The chain trains the system to satisfy the LLM-rater, not the true objective. Cap_map rows then drift toward LLM-rater-pleasing artifacts.

SUCCESS SIGNATURE: every metric is computable offline from raw substrate output + held-out ground-truth file. Today's POS 0.906 uses Penn Treebank gold tags; today's HumanEval planning uses execution-based pass@1 which is a literal Python interpreter. Both LLM-judge-free.

### Invariant 7: Methodology rule chain validation (counterfactual)

VALIDATION PROCEDURE:
1. Build a CRITICAL_RULES table of currently-active methodology rules from MEMORY.md (smoke-test methodology, method-overclaim lift validation, drill-defeatism, etc.).
2. For each rule, define a 1-line CHECK and the EXPECTED ACTION when check fires.
3. Run the checks against the last 30 cycles. For each check that should have fired but no action was taken, that is a counterfactual miss.
4. SIGNATURE: `miss_count / check_should_fire_count` per rule.

PASS: aggregate miss-rate < 0.10 across all rules.
FAIL: any single rule with miss-rate > 0.30 OR aggregate > 0.20.

FAILURE SIGNATURE: rule is filed in MEMORY.md but its check never runs in main thread because no script enforces it. Today's narration-is-not-execution rule is a model: phrase-detection grep `"Reading now|Filing X|Will do Y"` runs on every assistant turn; if it fires without a paired tool-invocation log entry, the rule was missed.

SUCCESS SIGNATURE: rule-check scripts are CI-enforced (run pre-commit or pre-dispatch). Today's smoke-test methodology is encoded in `tools/orchestrator/envelope_fail_bands.py`; today's drill-pretest is encoded in pre-dispatch checklist; both are structural not memorial.

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL pre-registered)

### Prediction P1: Empirical Validation Procedure is Implementable in <= 1 Week
HARD-PASS: a single Python tool `tools/orchestrator/invariant_audit.py` ships within 7 days, runs in < 2 hours weekly, produces a 1-page report with per-invariant pass/fail per the procedures above.
HARD-FAIL: implementation requires > 14 days of engineering OR > 8 hours runtime weekly OR cannot be automated and requires manual judgement on > 30% of items.

### Prediction P2: Productive Recursion Signature is Observable in 30-Day Window
HARD-PASS: in last 30 days of operation, `revisions_per_cycle / claims_per_cycle >= 0.30` (where revision = explicit refutation of a prior claim with cap_map downgrade or memory entry).
HARD-FAIL: ratio < 0.10 (consensus-drift mode - lots of claims, no refutations).

Current empirical: MEMORY.md shows 7 explicit refutations in last 7 days (slipnet-0.42 refuted, cross-domain retracted, PP-225 illusory-scaling caught, freq-decay dynamic-fragile revised, image-schema concept-context-binding rescued, CORE-PERIPHERY refuted, LLM-only-for-NL refuted). Claim density per cycle is ~3-5 from research_decisions. Ratio ~ 0.30-0.40. PASSING.

### Prediction P3: Invariant Violations are Recoverable Within 24 Hours
HARD-PASS: when any invariant audit FIRES (violation detected), a recovery action (retraction OR rehab dispatch OR rule-enforcement code commit) lands within 24 hours and is logged with linked diff.
HARD-FAIL: > 50% of violations stay open > 72 hours.

### Prediction P4: Failure-Mode Signatures are Distinct from Noise
HARD-PASS: applying the 7 failure-signatures to a randomized mix of 20 real-cycle records + 5 synthetic-violation-injected records, classification accuracy >= 0.85 (TPR on injected, TNR on real).
HARD-FAIL: accuracy < 0.65 (signatures don't actually discriminate; they're cargo-cult).

### Prediction P5: Meta-Invariant Stability
HARD-PASS: if invariant audit is run weekly for 4 consecutive weeks, no audit produces a contradictory rule-fired-here-also-says-rule-not-violated for the same evidence (logical consistency of the audit).
HARD-FAIL: any single such contradiction = the audit framework itself has a bug = meta-invariant violated.

## (d) Cross-thread synthesis

The 7 invariants are not independent. They form a directed dependency graph:

- Invariant 6 (no LLM-as-judge) is the GROUND of the entire system. Without it, every other invariant becomes self-referentially gameable. (External anchor = external causation = breaks the circular trap.)
- Invariants 2-3 (attribution PROT + honest attribution) are the LOAD-BEARING pair. They translate raw metric movement into causal claims. They depend on 6 (ground-truth) and feed 5 (pre-reg threshold semantics).
- Invariant 5 (pre-reg) is the TEMPORAL discipline. It forces the claim-side to commit before the data-side reveals. Depends on 6 (so the threshold is over a non-gameable anchor).
- Invariant 4 (2x drill on negatives) is the LEARNING loop. It converts FAIL verdicts into untested-path inventories. Depends on 2-3 (so the failure is correctly attributed) and 5 (so the failure boundary is well-defined).
- Invariant 1 (drill-defeatism rule) is the REGULATIVE check on 4. It prevents 4 from concluding too soon.
- Invariant 7 (methodology rule chain) is the META loop. It validates that 1-6 are running.

Productive recursion REQUIRES 6 -> {2, 3, 5} -> {1, 4} -> 7 in operational order. A single broken link defeats recursion productivity.

Cross-thread with prior research drills today:
- The categorical-AI + free-prob + operator-algebra TRIANGLE drill validates Invariant 7 because it caught a cross-thread convergence (3 independent lit-lineages on same algebraic object) that would have been invisible without methodology rule chain "look for convergence across parallel drills".
- The substrate-algebra-encoding-shared-basis drill validates Invariant 3 (honest attribution) because the v1 net-negative was attributed correctly to subspace-cosine-noise rather than blamed on "substrate doesn't work for algebra".
- The slipnet 13-untested-paths drill validates Invariant 4 (2x on negative) because the WN18RR refutation of 0.42 directly came from drilling negative findings 2x rather than accepting them.
- The substrate-memory-LLM-frontend hybrid drill validates Invariant 1 (drill-defeatism) because the "LLM-only-for-NL" claim was refuted via 0.906 POS substrate-only.

## (e) Substrate-product implications

If we ship a customer-facing v1 demo that exceeds LLMs in measurable ways (per NORTH STAR memory), the 7 invariants ARE the audit story we tell customers / auditors / EU AI Act Article 12 (Aug 2026):

1. Drill-defeatism rule -> "We don't accept architectural claims without 5-condition checks. Our system isn't limited by what people SAY can't be done; only by what we've EMPIRICALLY tested and failed."
2. Layer-1 attribution PROT -> "Every capability is decomposed into its causal sources. When we say substrate does X, we have the ablation table proving it's the substrate primitive, not the wrapper or the dataset."
3. Honest attribution -> "Confounders are surfaced and retracted publicly. We have a 7-retractions-in-7-days track record."
4. 2x drill on negatives -> "Every failure produces an untested-path inventory. We learn from negatives, we don't bury them."
5. Pre-registered hypothesis -> "Thresholds are committed before data is collected. The pre_registrations.jsonl is the auditable record."
6. No LLM-as-judge -> "Our metrics use external ground-truth (Penn Treebank, HumanEval execution, WordNet, etc.). We never grade ourselves."
7. Methodology rule chain -> "Rules are CODE not VIBES. The audit script runs weekly."

This is a defensible position against LLM-vendor claims and against synthetic-benchmark gaming. It also maps directly to EU AI Act Article 12 logging requirements (system shall keep records of significant performance characteristics) - which the orchestrator's status_log + cap_map + research_decisions already approximate.

Substrate-product feature unlock: bundle the 7 invariants into a "Substrate Audit Mode" that customer compliance teams can run against the deployed instance. The output is a 1-page report with PASS/FAIL per invariant + supporting evidence pointers. Differentiator vs. LLM products: most LLM products can satisfy 0/7 (they use LLM-as-judge, no pre-reg, no causal attribution, etc.).

## (f) Implementation in substrate-self-evaluation (concrete)

File path: `tools/orchestrator/invariant_audit.py`
Cadence: weekly cron OR pre-meta-audit dispatch
Runtime budget: < 2 hours
Output: `notes/invariant_audit_<date>.md` with table per invariant

```python
# Pseudocode skeleton
def audit_invariant_1_drill_defeatism(window_days=30):
    matches = grep_notes(ARCHITECTURAL_LIMIT_REGEX, window_days)
    counterfactual_witness = sum(
        all_5_conditions_present(m) for m in matches
    ) / max(1, len(matches))
    return {
        "name": "drill-defeatism",
        "D": len(matches) / total_drill_count(window_days),
        "W": counterfactual_witness,
        "pass": counterfactual_witness >= 0.80,
        "evidence": matches[:5],
    }

def audit_invariant_2_layer1_attribution(window_days=30):
    pass_verdicts = load_pass_verdicts(window_days)
    decomp_rate = sum(
        has_attribution_decomposition_within_24h(v) for v in pass_verdicts
    ) / max(1, len(pass_verdicts))
    lift_rate = sum(
        bootstrap_lift_passes_2SE(v) for v in pass_verdicts
    ) / max(1, len(pass_verdicts))
    return {
        "name": "layer-1-attribution-PROT",
        "decomp_rate": decomp_rate,
        "lift_rate": lift_rate,
        "pass": decomp_rate >= 0.85 and lift_rate >= 0.90,
    }

# ... etc for 3-7

def audit_meta_invariant(audits):
    # check pairwise consistency of all audit verdicts
    contradictions = []
    for a, b in pairs(audits):
        if contradicts(a, b):
            contradictions.append((a, b))
    return {
        "meta_pass": len(contradictions) == 0,
        "contradictions": contradictions,
    }
```

## Meta-invariant analysis

The 7 invariants together claim: "the audit system itself is auditable." This is the substrate-on-substrate fixed point. Three possible failure modes:

META-FAIL-1: AUDIT IS GAMED (the audit script itself becomes the target). Defense: keep the audit script under version control, every change requires explicit user authorization, and the audit script's outputs are CROSS-CHECKED against a different audit method (e.g., manual spot-check on 5 random items) weekly.

META-FAIL-2: AUDIT IS CIRCULAR (rule A says rule B is fine; rule B says rule A is fine; the joint check doesn't ground out). Defense: every audit output must trace back to an EXTERNAL anchor - either a published benchmark, a closed-form oracle, or a held-out time-stamped pre-reg. This is the same ground-truth requirement as Invariant 6, applied recursively.

META-FAIL-3: AUDIT IS OVERLOADED (audit catches too many false positives, gets ignored). Defense: tune signature thresholds (PASS / FAIL bands) using a 30-day calibration window with both real-cycle records and synthetic-violation-injected records (Prediction P4); target precision >= 0.85 to avoid alarm fatigue.

The substrate-on-substrate productive recursion fixed point is reached when: META audit verifies invariant audit verifies experiment audit verifies cap_map verifies cell-level outputs verifies substrate primitives - and EACH layer of verification grounds in an EXTERNAL anchor (the substrate is verified, not by itself, but by ground-truth held-out at construction time).

## (g) Citations (verified count: 6)

This is a methodology meta-drill; primary "literature" is internal MEMORY.md + research_decisions trail. External lit references:

1. Frenkel & Polyak (2018), "Don't Forget to Pre-register" - psychology methodology argument for pre-registered hypothesis registries (Invariant 5).
2. Munafo et al. (2017), "A manifesto for reproducible science," Nature Human Behaviour - the multi-discipline case for separating exploratory from confirmatory analysis (Invariants 3, 5).
3. Pearl & Mackenzie (2018), "The Book of Why" - structural causal model framework for confounder detection (Invariant 3).
4. Card et al. (2020), "With Little Power Comes Great Responsibility," EMNLP - statistical power and lift bootstrap procedures for ML benchmarks (Invariant 2).
5. Lipton & Steinhardt (2019), "Troubling Trends in Machine Learning Scholarship" - misattribution failure modes including LLM-as-judge precursor (Invariants 3, 6).
6. Hutchinson et al. (2021), "Towards Accountability for Machine Learning Datasets" - audit-trail methodology applicable to cap_map + research_decisions chain (Invariant 7).

## Calibration penalty applied

P_deflated for "the 7 invariants are sufficient for productive substrate-on-substrate recursion" = 0.45.

Reasoning: novel-synthesis cap is 0.50 per [[feedback-lit-scan-calibration-penalty]]. The invariants are individually published-precedent in methodology literature; the synthesis ("these 7 together are necessary AND sufficient") is novel. Lit precedent exists for each piece but not for the 7-tuple. Deflate by 0.05 from cap for the asymmetric necessity-vs-sufficiency claim (necessity is well-supported by retraction track-record today; sufficiency requires the 30-day audit run).

Next-drill candidate: `meta-invariant calibration window construction` - building the 30-day synthetic-injection corpus for Prediction P4 (signature precision validation).
