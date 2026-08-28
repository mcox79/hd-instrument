---
problem: compose_the_reader_by_convergent_cue_not_independent_conjunction
status: SOLVED
bar: "A convergent-cue composition PASSES only with ALL of: 1. Beats the independent-AND baseline (0.119) CI-separated on the SAME gold/harness (paraphrased pronoun who-did-what, the STEP-18 items), scored identically. Recompute the baseline in-harness -- no number crosses harnesses. 2. Mechanism is convergent-cue, not fusion: meaning + entity cues JOINTLY address ONE content-addressable read (pattern completion / top-down bias), NOT a re-weighted AND of two independent readouts. State the operation explicitly. 3. The DOUBLE DISSOCIATION is PRESERVED (the fidelity gate): a FUSED-pool control (meaning and entity in one undifferentiated store) must be REFUTED -- either it loses to convergent-cue, or it destroys the dissociation (lesioning one system no longer degrades gracefully). Report the lesion-each-system test. 4. Info-free twin LOSES: a shuffled/irrelevant meaning cue provides NO facilitation (score falls back toward the independent baseline). This proves the gain is TOP-DOWN SEMANTIC support, not a free-parameter artifact. 5. The gain is LOCALISED to the predicted subset: show the lift concentrates on entity-solo-WRONG cases (where top-down support should rescue), not a uniform shift (which would suggest a scoring artifact). A rigorous NEGATIVE (faithfully-built convergent-cue does NOT beat independence here, root-caused) is a PASS."
result: "CONVERGENT read (reliability-weighted product of the episodic + semantic posteriors; learned weight w=12 calibrated on train docs, evaluated strictly HELD-OUT 5-fold) = 0.7438 [0.7246,0.7626] on the STEP-18 gold/harness (LitBank paraphrased pronoun who-did-what, 60 docs, n=3681 pronoun queries). Beats meaning-solo 0.6998 [0.6791,0.7222] -- the STRONGEST floor actually run -- by +0.044 paired CI[0.031,0.058], hw 0.014 (and the brief's independent-AND floor 0.1282 by +0.6156, entity-solo 0.1785 by +0.5653). All 7 bar checks PASS; robust across 3 combination forms (log-Bayes 0.744, z-norm-lambda 0.750, activation-space top-down-reinstatement 0.723)."
floor: "STRONGEST floor = meaning-solo 0.6998 [0.6791,0.7222] (the pure-semantic special case of the convergent read; the brief's named independent-AND baseline 0.1282 is a STRAW floor -- it is LOWER than either single system, so beating it is trivial; disk-outranks-brief, stated in prose). Also run: entity-solo 0.1785; independent-AND (recomputed in-harness) 0.1282."
controls: "(1) info-free MEANING twin (shuffled semantic cue) 0.0407 -> collapses, HEADLINE beats it +0.7031 CI-sep, null p95 vs meaning-solo delta -0.6355 (twin loses) -> the gain is top-down semantic support, not a free parameter. (2) info-free EPISODIC twin (shuffled episodic cue) 0.6669 -> FALLS BELOW meaning-solo (-0.0329 CI-sep) and HEADLINE beats it +0.0769 CI-sep -> the win over meaning-solo genuinely requires the REAL episodic evidence (it is convergence, not meaning-solo relabeled). (3) FUSED one-undifferentiated-pool control 0.3602 -> LOSES to convergent +0.3836 CI-sep, and its lesion-meaning read 0.1342 is BELOW the separated entity-solo 0.1785 (fusion adds interference) -> refuted as a fidelity regression. (4) DOUBLE DISSOCIATION preserved: lesion meaning -> entity-solo 0.1785 (spared, nonzero); lesion entity -> meaning-solo 0.6998 (spared, nonzero). (5) LOCALISATION: keeps 97.6% of meaning-solo-RIGHT (n=2576), rescues 20.5% of meaning-solo-WRONG (n=1105) via episodic support and 70.1% of entity-solo-WRONG (n=3024) via meaning support -> targeted lift, not a uniform shift. (6) equal-reliability product (w=1) 0.6387 -> BELOW meaning-solo -> reliability weighting is load-bearing (Ernst-Banks)."
files_changed: "experiments/exp_convergent_cue_composed_reader_v1.py (the convergent-cue reader + all arms/controls; deployable), experiments/exp_convergent_cue_probe_v1.py (lambda-sweep probe), experiments/exp_convergent_cue_reliability_drill_v1.py (ceiling + per-query-reliability + reliability-tracking drill), verification/test_convergent_cue_composed_reader.py (scaffold-free witness, 7/7 PASS), data/exp_convergent_cue_composed_reader_v1/{metrics.json,records_60.json,records_8.json,run60.log}. NO hdlab/ (Q111 -- strategy lands; proposed diff below)."
reverify: ".venv/Scripts/python.exe verification/test_convergent_cue_composed_reader.py"
---

# Convergent-cue composition beats the independent-AND -- and beats the true strongest floor, faithfully

## What the brief asked, and the one place the disk outranks it
STEP-18 composed the two landed organs -- the episodic entity binder (`salience_binder`, ACT-R + Centering)
and the ATL conceptual channel (`conceptual_meaning`) -- by an INDEPENDENT post-hoc AND: score correct iff the
entity read's argmax verb == v AND the meaning read's argmax verb == v. That product (0.119) is what the brief
names as the baseline to beat.

**But the AND (recomputed in-harness: 0.1282) is a STRAW floor: it is LOWER than EITHER system alone**
(entity-solo 0.1785, meaning-solo 0.6998). Beating it is trivial -- either solo already does. Per the standing
measurement discipline ("a gate is a CI-separated margin over the STRONGEST floor actually run"), the real floor
is **meaning-solo 0.6998** -- which is exactly the pure-semantic special case of the convergent read (episodic
weight -> 0). So the honest bar I held myself to is: **beat meaning-solo CI-separated**, and I do (+0.044). This is
the disk-outranks-brief nuance the kickoff asks for; the brief's own §4 already flags entity-solo/meaning-solo as
the context numbers, so this is a sharpening, not a contradiction.

## The mechanism (bar #2: ONE read, jointly driven -- stated explicitly)
Opening move -- how does the brain do this? Episodic recall is **CONVERGENT-CUE PATTERN COMPLETION**: a partial
multi-cue probe reinstates the full conjunctive trace via CA3 attractor dynamics (McClelland/McNaughton/O'Reilly
1995; Norman & O'Reilly 2003 -- PINNED). Optimal combination of two cues about the same target = the **PRODUCT of
their evidence distributions = the SUM of log-evidence**, each cue weighted by its **RELIABILITY** (Ernst & Banks
2002 -- PINNED normative rule); and in a probabilistic population code that weighting is **automatic** -- you
literally ADD the two population codes and the more confident (higher-gain) one dominates (Ma/Beck/Latham/Pouget
2006 -- PINNED mechanism). Hemmer & Steyvers 2009 is the closest whole-operation precedent (episodic trace x
semantic prior, Bayesian, reliability-graded).

**The operation** (per pronoun query: entity E, slot s, true verb v; paraphrase cue q = a WordNet synonym of v
that is NOT a doc candidate string; candidates = the doc's verbs):

```
epi_raw(c) = FHRR cleanup score of candidate verb c from the LANDED per-entity register decode
             (unbind(entity E's multibank register, slot s) then Re<conj(verb_c), readback>/d)   [BOTTOM-UP episodic]
sem_raw(c) = conceptual_meaning.similarity(q, c)                                                  [TOP-DOWN semantic]
p_epi = softmax(epi_raw / tau_e),  p_sem = softmax(sem_raw / tau_s)     (tau = each cue's OWN gold-blind global
        scale = the population's fixed gain; per-query PEAKEDNESS then carries reliability automatically)
answer = argmax_c [ log p_epi(c) + w * log p_sem(c) ]                   (product of posteriors = ONE competition
        jointly driven by both cues; w = the learned average reliability ratio)
```

This is a top-down bias on **ONE content-addressable read** (the cleanup competition), NOT an AND of two
independent argmaxes. Its activation-space equivalent (arm `CONVERGENT_REINSTATE`, also wins, 0.723) makes this
literal: adding the semantic-predicted vector `sum_c p_sem(c)*verb_vec_c` to the FHRR readback and re-running one
cleanup reduces -- because the verb atoms are ~orthonormal -- to `softmax(epi)(c) + w*p_sem(c)`, i.e. top-down
predictive-coding reinstatement into the hippocampal read. Bayes-form and activation-form are the same mechanism.

**Two SEPARATE pools combined at read (never fused):** hippocampal lesion (no register) -> p_epi uniform ->
answer = meaning-solo; semantic lesion (drop sem) -> answer = entity-solo. The double dissociation is preserved
by construction (see controls).

## What I measured (60 docs, n=3681 -- the exact STEP-18 population)
- HEADLINE convergent (learned w, held-out) **0.7438** vs meaning-solo **0.6998** -> **+0.044 CI[0.031,0.058]**,
  the strongest floor beaten CI-separated. (vs AND 0.1282: +0.6156; vs entity-solo 0.1785: +0.5653.)
- **Reliability weighting is load-bearing:** the equal-weight product (w=1) scores 0.6387, BELOW meaning-solo --
  the two cues are NOT equally reliable (Ernst-Banks), so combining them requires reliability weighting; the
  learned w (=12 median across folds; the DENSE episodic store is weak, so semantic is trusted more) fixes it.
- **Robust across 3 combination forms:** log-Bayes 0.744, z-normalised-lambda (CV) 0.750, activation-space
  reinstatement 0.723 -- all beat meaning-solo. The probe shows a broad winning band (lambda in [3,100]); this is
  not a knife-edge tuned knob.
- **Controls (each excludes something):** shuffled-MEANING twin 0.041 (collapses -> gain is top-down semantic);
  shuffled-EPISODIC twin 0.667 (falls BELOW meaning-solo -> the win needs the REAL episodic cue = genuine
  convergence); FUSED one-pool 0.360 (loses; its episodic read 0.134 < separated entity-solo 0.178 = interference);
  lesion-each -> entity-solo 0.178 and meaning-solo 0.700 both nonzero (dissociation preserved); lift localised
  (keeps 97.6% of meaning-solo-right, rescues 20.5% of meaning-solo-wrong).
- Witness `verification/test_convergent_cue_composed_reader.py`: **7/7 PASS** on n=3681.

## Further-optimization drill (is the RULE at its ceiling, and is the weighting really reliability-driven?)
Asked to keep pushing and stay brain-foundational, I drilled two questions (`exp_convergent_cue_reliability_drill_v1.py`):

1. **Is the combination RULE near-optimal, or is there headroom?** ORACLE_UNION = correct iff EITHER cue's
   argmax is v = the tightest ceiling for any one-answer selector between these two cues = **0.7501**. The
   headline convergent read is **0.7438** -- the gap to the oracle is **+0.0062, CI-separation NOT_SEP** (the
   read is statistically AT the ceiling). A fuller PER-QUERY precision-weighted form (each cue's z-normalised
   shape weighted by its own per-query confidence = the explicit Ernst-Banks form) scores 0.6767 -- it does NOT
   beat the global-weight product (-0.067 CI-sep). So the simple log-Bayes product ALREADY performs optimal
   per-observation reliability weighting (Ma et al.: multiplying posteriors IS per-observation weighting); the
   "more elaborate" variant is a fidelity/accuracy regression. **The rule cannot be improved with these inputs.**
   Notably, on the meaning-solo-WRONG subset convergent achieves 0.2045, EXCEEDING even the episodic argmax rate
   there (0.1674) -- it lands on v when v is 2nd in BOTH cues, i.e. it integrates GRADED evidence rather than
   selecting an argmax. That is the defining signature of genuine convergent-cue pattern completion, and it is why
   the read can sit above the argmax-union oracle on the hard cases while being at the union ceiling overall.
2. **Does the weighting genuinely track episodic reliability (the compounding prediction)?** Binning queries by
   episodic-read confidence (peakedness of p_epi) into quartiles, the convergent gain over meaning-solo rises
   MONOTONICALLY with reliability: Q1 (no episodic info) **+0.000** (graceful fallback to meaning-solo) -> Q2
   +0.010 -> Q3 +0.052 -> Q4 (high episodic confidence; entity-solo there 0.525) **+0.117**. The weighting is
   genuinely reliability-driven, and this VALIDATES the compounding prediction WITHIN the current store: p2's
   sparse DG+CA3 store globally raises episodic reliability, which -- by this very curve -- grows the convergent
   gain. **The wall is the dense episodic store's quality, not the combination rule.**

## What I did NOT establish (and would withdraw first if wrong)
1. **The magnitude of the gain is bounded by the DENSE episodic store, not by the mechanism.** entity-solo is only
   0.178 (the STEP-18 dense-bundle ceiling that p2's sparse DG+CA3 targets), so top-down support can only rescue a
   fraction (20.5%) of meaning-solo-wrong cases, giving +0.044. **Testable forward prediction:** when p2 lands the
   sparse store, entity-solo rises, the learned reliability weight w drops toward 1, and the convergence gain
   GROWS -- re-run is one swap (the harness reads whatever register `make_situation_register` returns). If that
   prediction fails, the first thing I withdraw is "the gain is store-limited, not mechanism-limited."
2. **The learned weight w is calibrated, not automatic.** Ma et al.'s "add the population codes, gain does the
   weighting for free" requires the two cues to be ONE commensurate population (Poisson, shared basis). Our two
   evidence codes (FHRR complex cleanup vs sparse-cosine) are heterogeneous, so the automatic gain is not
   available; the reliability ratio must be CALIBRATED (w, learned on train / evaluated held-out). Calibration is
   itself PINNED (Ernst-Banks: organisms learn cue reliability from experience), but "reliability-weighting is
   fully emergent here" would be the over-claim -- I withdraw it explicitly. This is an OUR-INVENTION boundary.
3. **The paraphrase gold keeps STEP-14's mild WordNet circularity** (WordNet synonyms scored by a WordNet channel).
   This inflates the absolute meaning-solo (0.70) but is IDENTICAL across all arms, so the CI-separated DELTA is
   unaffected; a non-WordNet paraphrase set is the clean follow-on. I do not quote the absolute as a capability.
4. **Single-shot vs REMERGE recurrence.** Kumaran & McClelland 2012 (REMERGE, big-loop recurrent settling) is the
   closest neural precedent for multi-cue mutual constraint, but its recurrence earns its keep only when cues
   reactivate DIFFERENT traces that must chain (transitive inference A-B, B-C -> A-C). Here both cues address the
   SAME target (the verb), so the one-step product IS the settled fixed point; building the full loop would be
   unfaithful over-engineering for this task. If a future task needs episodic-episodic chaining, REMERGE is the
   build. (Reasoned scope decision, not a shortcut.)

## KEY REALIZATIONS (the enabling moves)
- **The brief's floor was a straw; the real floor is the winning arm's own pure-semantic special case.** Recomputing
  the floors in-harness revealed the AND (0.13) is below BOTH solos -- so I re-aimed at meaning-solo (0.70), the
  strongest floor, which is `w->0`... no, `episodic weight -> 0` of the convergent read itself. Beating your own
  degenerate case is the honest bar.
- **The equal-weight product FAILING was the signal, not a bug.** `log p_epi + log p_sem` (w=1) scores BELOW
  meaning-solo. That is exactly Ernst-Banks: unequal-reliability cues MUST be reliability-weighted. Adding the
  learned weight is the mechanism, and the failure of the un-weighted version is the evidence FOR it. (Also: my
  first "parameter-free" instinct -- z-score both cues to unit scale -- was the mistake; it EQUALISES the gains and
  destroys the very reliability signal Ma et al. says does the weighting. Global-scale tau preserves it.)
- **The shuffled-EPISODIC twin is the control that proves CONVERGENCE, not the shuffled-meaning one.** Meaning is
  the dominant cue, so shuffling it obviously collapses the score -- that only proves meaning matters. Shuffling
  the EPISODIC cue and watching the score fall BELOW meaning-solo is what proves the win is real two-cue
  convergence and not meaning-solo with extra steps. A control has to be able to remove the thing you are claiming.

## AUDIT UPDATE (notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b -- the composition-fidelity entry, 2026-08-27)
The sec-2b deviation "composition-by-independent-conjunction where the brain composes by convergent-cue retrieval"
is now **TESTED and RESOLVED at the READ side**: the convergent-cue read (reliability-weighted product of the two
posteriors = one CA3-style cleanup competition jointly driven by episodic + top-down semantic evidence) BEATS the
strongest floor (meaning-solo 0.70 -> 0.74, +0.044 CI-sep, held-out), with the fused-pool control refuted and the
double dissociation preserved. Update the deviation from "under-test" to "READ-side mechanism validated;
magnitude gated by the dense episodic store (p2)". New PINNED-vs-INVENTED line for the composition: the COMBINATION
RULE (product of posteriors / sum of log-evidence) is PINNED (Ernst-Banks/Ma et al.); the RELIABILITY WEIGHT being
CALIBRATED rather than emergent is OUR-INVENTION-UNDER-TEST (heterogeneous cue codes, not one PPC population).
Forward hook: convergent + p2's sparse store should compound (predicted w -> 1, gain grows).

## PROPOSED hdlab CHANGE (Q111 -- strategy lands it; I did NOT write hdlab/)
1. **New `hdlab/convergent_cue_reader.py`** (or a method on the situation-model read path): given a query
   (entity register, slot, a semantic cue distribution over candidate verbs), return `argmax_c [ log softmax(
   cleanup_scores/tau_e)(c) + w * log softmax(sem_scores/tau_s)(c) ]`. Reuse the LANDED
   `situation_model_accumulate` decode for `cleanup_scores` (it already returns the full score dict) and
   `conceptual_meaning.similarity` for `sem_scores`. `tau_e, tau_s` = gold-blind global cue scales (static,
   offline-computed = admissible per the pivot); `w` = a single reliability scalar CALIBRATED offline (a static
   asset, ~12 on the current dense store) -- NOT fit at inference. Graceful degradation is free: empty register ->
   meaning-solo; no semantic cue -> entity-solo.
2. **Wire it as the composition step** wherever STEP-18's independent-AND currently composes entity+meaning; keep
   the two organs and their separate stores UNCHANGED (the dissociation gate forbids fusing them).
3. **Re-run on p2's sparse store when it lands** (one swap of the register backend) and RE-CALIBRATE w; the
   predicted effect is a larger convergence gain with a smaller w.
4. **Do NOT:** fuse the two into one undifferentiated pool (loses + destroys the dissociation, measured); use the
   equal-weight product (below meaning-solo, measured); quote the absolute convergent number as a capability (the
   claim is the CI-separated beat over meaning-solo + the controls); build the REMERGE recurrent loop for this
   co-referential task (single-shot is the settled state).

## TLDR (plain language)
To answer "what did she chase?" a reader must both track who "she" is (an episodic/memory skill) and know the
paraphrase (a meaning skill). The old way ran the two skills separately and demanded both be right -- which scores
worse than either skill alone, because it multiplies two chances of failure. The brain does not do that: it feeds
both clues into ONE memory lookup at once, where the meaning clue helps steer the memory read (and each clue counts
more when it is more reliable). I built exactly that, grounded in textbook results (CA3 pattern completion; optimal
cue-combination = multiply the two evidence distributions, weight by reliability). It beats the best single skill
(from about 70% to about 74% on the hard paraphrased-pronoun test, a real CI-separated gain), and every check that
it is the RIGHT mechanism passes: scramble the meaning clue and it collapses; scramble the memory clue and the
extra gain disappears (so the memory is genuinely contributing); merge the two memories into one pool and it gets
WORSE and loses the ability to fail gracefully (which the brain's separate-systems design predicts). The gain is
modest because the memory store it reads is still the weak "dense" one; the same mechanism should gain MORE once
the sharper "sparse" store (a separate in-flight fix) lands.

## QUESTIONS
None blocking. One judgment call made visible: I re-aimed the bar from the brief's independent-AND (0.13) to the
true strongest floor meaning-solo (0.70) and beat THAT -- because beating a floor that sits below both single
systems would not have been evidence of anything. I flagged this as disk-outranks-brief rather than silently
using the easier target.

## NEXT STEPS
1. Land `convergent_cue_reader` (default-safe) and swap it in for the STEP-18 independent-AND composition.
2. Re-run + re-calibrate w on p2's sparse DG+CA3 store when it lands (predicted: bigger gain, smaller w).
3. Clean-up follow-on: a non-WordNet paraphrase gold to remove the mild circularity from the absolute numbers.

---
INTEGRATED_BY_STRATEGY: 2026-08-27 (grade EXCELLENT). Re-verified FIRST-HAND (test_convergent_cue_composed_reader.py
7/7 PASS). Convergent-cue read beats the strongest floor meaning-solo 0.700->0.744 (+0.044 CI-sep); all controls pass
(shuffled-meaning collapses, shuffled-episodic falls below meaning-solo = genuine convergence, fused loses + kills the
dissociation, double dissociation preserved, lift localised, equal-weight below meaning-solo). Brain-faithful (PINNED
product-of-posteriors; OUR-INVENTION calibrated w labelled). Solver correctly caught the brief's straw floor (0.119) and
re-aimed at meaning-solo. hdlab LANDED: hdlab/convergent_cue_reader.py (convergent_pick, ports pick_convergent_rw +
tau calibration verbatim, DEFAULT_W=12 dense-store calibration, graceful degradation); witness
test_convergent_cue_reader_organ.py PASS; registered convergent_cue_reader_v1 (BUILT/ISLAND, default-safe). Review +
SOLVER REVIEW block written to PROBLEM.md; priority cleared. AUDIT UPDATE folded (§2b). NEXT: recalibrate w on p2's
sparse store when it lands (predicted w->1, larger gain -- gain compounds with episodic reliability).
