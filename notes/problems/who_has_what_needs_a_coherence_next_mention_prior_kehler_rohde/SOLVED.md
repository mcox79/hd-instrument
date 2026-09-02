---
problem: who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde
status: REFUTED
bar: "PASS = a glass-box coherence/next-mention PRIOR (predicting the likely next referent from the discourse-coherence relation, multiplied into the graded-retrieval posterior before argmax) that: 1. recovers the STRUCTURALLY-DOMINATED error bucket CI-separated -- the bucket reachable by NO recency/subject/frequency cue (currently 0.481, n~445) -- over the entity-maintenance floor (recompute the floor on the held-out population, gate on its UPPER bound), on HELD-OUT LitBank gold coref (doc-split); 2. the lift is ATTRIBUTED to the coherence prior -- it must appear on the structurally-dominated bucket (which no backward cue can reach), with the backward graded pick held at its near-optimal setting; 3. a shuffled-coherence twin LOSES CI-separated (same mentions, wrong coherence relation -> the forward signal, not the machinery, does the work); 4. does NO net harm to the near / non-dominated cases (report the per-bucket effect; a bucket recovery bought with a non-dominated regression is not a pass). Report CI half-width + null p95 on every margin. A rigorous located NEGATIVE is a FULL PASS if a faithfully-built coherence prior does not recover the bucket AND it names why (the coherence-relation signal is too weak glass-box / the prior is dominance-reinforcing / a genuine irreducible ambiguity floor) with the number."
result: "RIGOROUS LOCATED NEGATIVE (a full pass per the bar) -- AND this brief's mechanism is a near-DUPLICATE of the owner-DONE 2026-08-29 problem `the_reader_has_no_coherence_next_mention_prior` (REFUTED / EXCELLENT / owner_verdict DONE), which already built this exact coherence prior and measured it dead. On the HELD-OUT (50 test docs) CHAIN (entity-maintenance) STRUCTURALLY-DOMINATED bucket -- the brief's exact population, nochain-defined struct-dom scored under the chain, n=695 -- the faithful coherence next-mention PRIOR (selectional grounded-centroid + thematic connective, reused VERBATIM from the 2026-08-29 cell, fused as a Bayesian product, weight tuned on the DEV bucket = its best shot, wp=0.3) does NOT recover the bucket: chain floor 0.4230 [0.3080,0.5433] -> +prior 0.4187 [0.3000,0.5365], prior-minus-floor -0.0043 [-0.0223,+0.0119] (NOT_SEP); and it does NOT beat its own 20-shuffle INFO-FREE TWIN: prior-minus-twin +0.0009 [-0.0138,+0.0148], half-width 0.0143, null p95 0.0144, band NOT_SEP. ORACLE ceilings on the bucket are near-chance (best-case argmax, no fusion): selectional 5.1%, thematic 14.7%, combined 6.9% (when applicable). The DEEPER specific-discourse EVENT-STATE situation-model channel the prior negative NAMED but never built (accumulate each entity's who-did-what-to-whom grounded event profile from the reading; predict re-mention by grounded event-coherence) is ALSO near-chance: oracle 7.8% (53/683). POSITIVE CONTROL: the SAME coherence mechanism flips constructed coherence-decisive minimal pairs (selectional 8/8, implicit-causality 8/8) where structural likelihood + info-free shuffle are at chance -> the mechanism WORKS; the structurally-dominated bucket lacks the cases (the anti-typical Winograd core). Premise reproduced EXACTLY via the parent's own harness: on the nochain-defined struct-dominated bucket the chain scores 0.4809 (the brief's 0.481), 0.294 of errors are struct-dominated (n=445), 0.995 of wrong picks are confident. Scorer = argmax==gold he/she who-has-what pick accuracy on the fixed held-out bucket, doc-bootstrap 95% CI. Deterministic across PYTHONHASHSEED 0/1/42."
floor: "Strongest floor actually run = the info-free 20-shuffle coherence-prior TWIN on the SAME held-out bucket = 0.4178 [0.3027,0.5229]; the real prior 0.4187 does NOT clear it (prior-minus-twin +0.0009, NOT_SEP, null p95 0.0144). The entity-maintenance CHAIN floor (the bar's named floor) = 0.4230 [0.3080,0.5433] (gate on the UPPER bound 0.5433); the prior does not beat it either (-0.0043, NOT_SEP). Premise floor faithfully reproduced via the parent harness: chain acc on the struct-dominated bucket 0.4809 (= the brief's 0.481), n=445. ORACLE ceilings (reachability, not floors): selectional 5.1% / thematic 14.7% / combined 6.9% / event-state 7.8% -- all near-chance, so no fusion weight can rescue any channel."
controls: "(1) INFO-FREE 20-shuffle TWIN on the same bucket: the prior (0.4187) does NOT beat it (0.4178); prior-minus-twin +0.0009 NOT_SEP -- excludes 'the coherence prior carries usable residual signal' (it does not beat its own noise). (2) ORACLE-ceiling decomposition per channel (best-case argmax, no fusion): selectional 5.1% / thematic 14.7% / combined 6.9% / EVENT-STATE 7.8% -- all near-chance -> excludes 'a better fusion weight rescues it' (even the oracle is near-chance). (3) NO-REGRESSION on non-dominated (structure-decisive) held-out cases at wp_best: 0.7521 -> 0.7246, broke 75/2731 -> the prior is DOMINANCE-REINFORCING (it regresses the cases it must not touch; bar item 4 fails for it). (4) POSITIVE CONTROL: the reused coherence mechanism flips 8/8 selectional + 8/8 implicit-causality constructed pairs where structural likelihood + info-free shuffle sit at chance (~5/8) -> excludes 'the mechanism is broken / the metric cannot move' (it can; the population lacks the cases). (5) DEV/TEST doc-split; fusion weight tuned on the DEV bucket (best shot); all headlines on the disjoint TEST bucket -> excludes tuning-to-gold. (6) PREMISE reproduced two ways: faithfully via the parent harness (EXACT 0.481/0.294/0.995/445) and via a cache-representation analog (0.499/0.391/0.979). (7) determinism verified across PYTHONHASHSEED 0/1/42 (identical)."
files_changed: "experiments/exp_coref_coherence_prior_on_chain_bucket_v1.py (the chain re-expressed in the who-did-what cache representation + the reused coherence-prior channels + the NEW event-state situation-model channel + oracle/fusion/twin on the held-out chain bucket + faithful parent-harness premise reproduction); verification/test_coref_coherence_prior_on_chain_bucket.py (4/4 scaffold-free witness); data/exp_coref_coherence_prior_on_chain_bucket_v1/metrics.json. NO hdlab/ written (Q111 -- proposed direction below)."
reverify: ".venv/Scripts/python.exe verification/test_coref_coherence_prior_on_chain_bucket.py   # 4/4: self-test + premise reproduces EXACT via parent harness (0.481/0.294/0.995) + coherence prior dead on the composed held-out bucket (oracle 6.9%, prior does NOT beat its info-free twin) + event-state lever near-chance + positive control fires"
---

# REFUTED (a rigorous located negative = full pass) -- AND this problem is a near-DUPLICATE of an owner-DONE negative.

## The headline, in one line
The coherence next-mention PRIOR this brief proposes was ALREADY built and measured dead -- owner_verdict DONE,
grade EXCELLENT -- four days ago (`the_reader_has_no_coherence_next_mention_prior`, 2026-08-29, REFUTED). I
reproduced the brief's premise EXACTLY, confirmed the negative SURVIVES composition with the just-integrated
entity-maintenance loop (the coherence prior still does not beat its own info-free twin on the post-chain
bucket), and went one step DEEPER than the prior negative -- the specific-discourse EVENT-STATE situation-model
lever it named but never built is ALSO near-chance. The residual is the anti-typical Winograd core; its real
fix is the (separately-filed, priority-1) north-star situation model + richer distributional semantics, NOT a
coherence prior. **My recommendation to strategy: consolidate this problem into priority-1; do not spend a
solver on re-deriving it, and do NOT land a coherence prior into hdlab.**

## THE DISK OUTRANKS THE BRIEF -- this brief missed prior work (the documented failure mode)
The brief (filed 2026-09-02) frames the coherence next-mention prior as "the located residual's real fix" and
cites the parent (`incremental_entity_maintenance_...`) and `coreference_is_capped_at_065...`. It does NOT cite
`the_reader_has_no_coherence_next_mention_prior` (2026-08-29), which is the SAME mechanism on the SAME kind of
population and was REFUTED. I found it on disk two ways before writing any code:
- the module comment at `hdlab/graded_coref_pick.py:125` ("Landed 2026-08-29 from the integrated
  `the_reader_has_no_coherence_next_mention_prior` (the coherence prior was a RIGOROUS NEGATIVE / EXCELLENT,
  owner-DONE: measured dead on the residual)"), and
- its `SOLVED.md` + `OWNER_NOTES.md` (`owner_verdict: DONE`).
That prior negative built the faithful coherence prior (selectional grounded centroid + thematic/coherence
relation, Bayesian-product fusion), and measured SIX independent glass-box channels dead/anti-predictive on the
structurally-dominated residual: coherence prior oracle 2.9% (beaten by its info-free twin), fine-distance 37.6%
oracle but ungateable, Kush structural-proxy 0/205, clean-parse GAP below chance, WordNet 2.0%, ConceptNet 2.8%
(despite 86.8% coverage). Its unifying insight -- the reason all six fail identically -- is that the
structurally-dominated bucket is BY CONSTRUCTION the ANTI-TYPICAL cases (gold is NOT most-recent, NOT
max-subjecthood, NOT most-frequent), so every typicality-tracking cue is anti-predictive on it.

**Per the protocol ("refuting the brief is the halfway point; do not re-run a landed negative"), I did not
blindly re-run. I did the three things that are NOT redundant:** reproduce the premise, test whether the negative
survives the NEW composition (entity-maintenance), and go deeper on the one lever the prior negative named but
never built.

## THE OPENING MOVE -- how does the brain do this? (PINNED vs OUR-INVENTION)
PINNED (Kehler & Rohde 2013): reference resolution is a two-term Bayesian product, `P(referent|pronoun) prop
P(pronoun|referent) x P(referent)` -- a Centering/ACT-R LIKELIHOOD (the graded pick, near-optimal by the
MAP-optimality theorem, held FIXED here) times a coherence-driven forward NEXT-MENTION PRIOR. The prior is
forward pre-activation of the likely referent (Rohde & Kehler 2014; the substrate's `predictive_reader`). This
is faithful and it is exactly what the 2026-08-29 problem and this one both build. The OUR-INVENTION-UNDER-TEST
parts (the coherence-relation inventory; how the prior is estimated glass-box; the fusion weight) were swept, not
adopted. **What the brief gets wrong is not the mechanism but its APPLICABILITY**: the structurally-dominated
bucket is precisely the set where the forward coherence prior has nothing to grip, because the disambiguating
fact is a SPECIFIC-DISCOURSE world-fact ("the rider is the parson, not the mare"), not a coherence relation.

## WHAT WAS BUILT AND MEASURED

### 1. The premise reproduces EXACTLY (my own recompute, faithful via the parent harness)
Calling the parent's own harness (`exp_entity_maintenance_chaining_v1`, the `hdlab.coref` loader with nominal
gender/animacy) in-memory, on the NOCHAIN-defined structurally-dominated bucket scored under the CHAIN arm:
chain acc 0.4809 (the brief's 0.481), 0.294 of errors struct-dominated (n=445), 0.995 of wrong picks confident.
Every premise number the brief states is reproduced to 3 decimals. (A cache-representation analog on all 100
docs gives 0.499 / 0.391 / 0.979 -- consistent; it is a fair-but-dirtier bucket because the who-did-what cache
lacks nominal gender/animacy, so it over-admits inanimate candidates. The coherence-prior verdict is robust
across both bucket constructions.)

### 2. The coherence prior is DEAD on the composed (entity-maintenance) held-out bucket (n=695)
The brief's exact test: multiply the faithful coherence prior into the graded-retrieval posterior before argmax,
recover the bucket over the entity-maintenance floor, twin must lose, no harm to non-dominated.

| arm (held-out chain struct-dominated bucket, n=695) | acc [95% CI] | vs floor / vs twin |
|---|---|---|
| entity-maintenance CHAIN floor | 0.4230 [0.3080, 0.5433] | -- |
| + faithful coherence prior (wp=0.3, DEV-tuned) | 0.4187 [0.3000, 0.5365] | prior-minus-floor **-0.0043 [-0.0223,+0.0119] NOT_SEP** |
| + INFO-FREE 20-shuffle twin | 0.4178 [0.3027, 0.5229] | prior-minus-twin **+0.0009 [-0.0138,+0.0148] NOT_SEP** (hw 0.0143, null p95 0.0144) |

The coherence prior does not beat the entity-maintenance floor, and -- the decisive test -- it does not beat its
own info-free noise. ORACLE ceilings (best-case argmax, no fusion) confirm no fusion weight could rescue it:
selectional 5.1%, thematic 14.7%, combined 6.9% (when applicable). This reproduces the 2026-08-29 negative
(oracle 2.9%, prior < twin) on the NEW post-entity-maintenance population -- so the just-integrated chaining
loop does not resurrect the coherence prior.

### 3. GOING DEEPER -- the specific-discourse EVENT-STATE situation-model lever is ALSO near-chance
The prior negative NAMED the real lever ("the SITUATION MODEL accumulating specific-discourse entity facts +
reasoning over them") but did not build it. I built the glass-box version at this representation: accumulate each
entity's who-did-what-to-whom EVENT PROFILE across the reading (grounded `gov_verb` + `obj_head` from the cache),
and predict re-mention by grounded event-coherence between the pronoun's clause event and each candidate's
accumulated profile. Its ORACLE ceiling on the bucket is **7.8% (53/683 when applicable)** -- near-chance. So the
event-coherence situation-model channel, at the current 12-dim grounded space, cannot discriminate the
anti-typical gold either. This is the measured reason (not asserted): the channel is starved by the COARSE
grounded space (two people have near-identical event profiles -- the p1 representation coupling) on top of the
anti-typical property. It confirms the prior negative's diagnosis with a channel the prior negative did not test.

### 4. NO net harm fails, and the positive control shows the mechanism works
- NO-REGRESSION (bar item 4): on the non-dominated (structure-decisive) held-out cases the prior REGRESSES,
  0.7521 -> 0.7246 (broke 75/2731) -- it is DOMINANCE-REINFORCING, exactly the prior negative's tradeoff-curve
  finding. A bucket recovery bought with a non-dominated regression is not a pass (and here there is no bucket
  recovery to buy it with).
- POSITIVE CONTROL (bar item 3, passes): the SAME coherence mechanism flips constructed coherence-decisive
  minimal pairs -- selectional 8/8, implicit-causality 8/8 -- where the structural likelihood and an info-free
  shuffle sit at chance (~5/8). The mechanism is faithful and works; the real bucket simply does not contain
  these cases (LitBank's implicit-causality-decisive frame is ~n=0 in ~200K tokens, the parent's + coref-cap's
  reconfirmed finding).

## WHAT I DID NOT ESTABLISH / would withdraw first
1. **I did NOT prove the residual is irreducible in principle.** The prior negative's fine-distance oracle
   (37.6%, ungateable without a reliable parse) already shows a large slice is reachable by a DIFFERENT organ
   (a parse-based syntactic-locality binder), not by a coherence prior. My claim is specifically that the
   coherence next-mention prior -- and the grounded event-coherence situation channel at the current
   representation -- do not reach it. Withdraw first any implication that the bucket is unrecoverable by ANY route.
2. **The event-state channel is ceiling'd by the coarse 12-dim grounded space (p1), not proven impossible with
   richer semantics.** A richer distributional representation might lift its oracle above 7.8% -- untested here
   (no-LLM invariant + coarse space). What holds: at the substrate's CURRENT representation it is near-chance.
3. **The bucket floor (~0.42) is not 0**, so "beat the floor" is not definitionally trivial here (unlike the
   prior negative's 0/205 residual) -- which makes the info-free twin the meaningful comparator, and the prior
   fails to beat it. The negative rests on the prior-vs-twin NOT_SEP (half-width 0.014, well-powered n=695) +
   the near-chance oracle ceilings, not on a point estimate.
4. **OOD caveat (shared with the parent):** LitBank is the reader coref's home corpus; the blind-vs-prior DELTA
   holds regardless (same corpus both arms), the absolute levels may be optimistic OOD.

## KEY REALIZATIONS (the enabling moves)
1. **Check the disk for the exact mechanism BEFORE building, by SHAPE not keyword.** `before_you_start.py` on
   the brief's terms did not surface `the_reader_has_no_coherence_next_mention_prior` (different slug wording),
   but the `hdlab/graded_coref_pick.py` module comment did -- the landed organ carries the provenance of the
   negative that spared it. Reading the organ I was told to reuse is what caught the duplicate. (An absence
   claim requires an enumeration: I enumerated the coherence/prior/predictive problem folders on disk, not just
   a keyword search.)
2. **The struct-dominated bucket is defined on the NOCHAIN history and scored under the CHAIN.** My first
   recompute defined struct-domination on the CHAINED candidate priors and got acc 0.13/0.20, not 0.481 --
   because chaining ADDS pronoun mentions that change recency/frequency. The parent defines the bucket on the
   nominal-only (nochain) history and measures the chain's accuracy on it -- which is why chaining recovers it
   to 0.48 (long-distance re-instatement). Matching the exact bucket definition (two-pass, join by mention
   identity) is what reproduced 0.481 precisely. The bucket is the population; get it wrong and the whole test
   is on a different set.
3. **The info-free twin is the meaningful floor even when the floor is not 0.** The chain floor here is ~0.42
   (not the prior negative's 0/205), but the coherence-SIGNAL question is still "does the prior beat its own
   shuffled self?" -- and it does not. The twin isolates the SIGNAL from the machinery.
4. **Measure the ORACLE ceiling first.** The selectional/thematic/combined/event-state oracles are all
   near-chance, so no fusion weight, no better twin, no clever gate could rescue them -- which is why the
   negative is airtight without an elaborate fusion sweep. Asking "could this even succeed?" (the highest-yield
   habit) is answered by the oracle before any effort on the fusion.
5. **The deeper lever, built and measured, is dead for a NAMED reason.** The one channel the prior negative
   left un-built -- specific-discourse event-coherence -- is near-chance at the current grounded space, which
   pins the real bottleneck to the p1 representation + the full situation model, not to "a better coherence prior."

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
The who-has-what structurally-dominated residual, AFTER the entity-maintenance wire, is STILL not
coherence-prior-decisive -- reconfirming the 2026-08-29 audit entry on the NEW composed population. A faithful
coherence next-mention prior (selectional + thematic, Bayesian-product fusion, DEV-tuned) does not beat its
info-free twin on the held-out chain bucket (prior-minus-twin +0.0009, NOT_SEP; oracle 6.9%), and it regresses
the non-dominated cases (dominance-reinforcing). NEW: the specific-discourse EVENT-STATE situation-model channel
(grounded who-did-what-to-whom event coherence) -- the lever previously named but never built -- has an oracle
ceiling of 7.8% on the bucket, ceiling'd by the coarse 12-dim grounded space (the p1 coupling) on top of the
anti-typical-by-construction property. NET: the ~0.48-on-the-struct-dominated-bucket ceiling is a REAL bound for
BOTH a glass-box coherence prior AND a glass-box grounded event-coherence situation channel; the two-system
boundary is SPECIFIC-DISCOURSE world knowledge x rich DISTRIBUTIONAL semantics (p1) + a reliable parse for the
intra-sentential slice, not LIKELIHOOD x coherence-PRIOR. Cross-link: this residual and the coref-cap's ~19%
residual and the 2026-08-29 residual are ONE boundary; the fix is the priority-1 north-star situation model + p1.

## PROPOSED hdlab DIRECTION (strategy lands; Q111 -- NOT a coherence prior)
Do **NOT** land a coherence next-mention prior, a grounded event-coherence prior, a fine-distance override, a
structural-proxy binder, or a static-KG plausibility cue into `hdlab/coreference_resolver.py` -- every one is now
measured dead/anti-predictive on this bucket (six channels on 2026-08-29 + the event-state channel here). The
graded pick + entropy-abstain (the parent's Track B) is the right OUTPUT on this bucket: the errors are
CONFIDENT structural mistakes (0.995 low-entropy), so the brain-faithful response to the irreducible slice is to
DEFER/flag, not to resolve. The real accuracy lever is the priority-1 north-star SITUATION MODEL (accumulate
this-discourse facts + reason over them, Garrod-Sanford resolution) + richer DISTRIBUTIONAL semantics (p1), which
this cell's event-state oracle localizes precisely (near-chance at the current 12-dim space).

## ADJACENT COMPONENTS (brain-fidelity + optimization -> the next problems)
- **The north-star SITUATION MODEL (priority-1, `optimize_and_validate_the_learner...` / the generative meaning
  model).** THE lever. Brain-foundational (Garrod-Sanford slow resolution). This cell shows the event-coherence
  proxy for it is starved by the grounded space -> the situation model needs richer entity-fact representation,
  not just event roles. Highest leverage; already filed above this at priority 1.
- **The 12-dim GROUNDED SEMANTIC SPACE (p1 representation lane).** MEASURED here as the binding constraint on
  the event-state channel (oracle 7.8%; two people are near-identical). Brain status: the ATL PDP hub is
  distributional; our coarse space is the gap. Optimization: richer distributional semantics would lift the
  selectional + event-state oracles. Standing lane.
- **`hdlab/predictive_reader` as a coref prior.** PINNED for anticipation; MIS-APPLIED as the coref prior for
  this person-heavy anti-typical bucket (oracle near-chance) -- the brief's (and 2026-08-29's) shared error.
- **The parse-based syntactic-locality binder (a DIFFERENT organ).** The prior negative's fine-distance oracle
  (37.6%, ungateable without a reliable parse) points here for the intra-sentential slice; blocked by
  archaic-prose parse noise. A register-robust parser is the follow-on for THAT slice (not this bucket's main mass).

## TLDR (plain language)
As you read a story, the hardest "who is she?" cases are the ones where grammar points at the wrong person and
only knowing what is actually happening in the story tells you the truth. This task asked me to add a "guess who
gets talked about next" step to fix those. Two important facts: **first, we already tried exactly this four days
ago and proved it does not help** -- I found that earlier result on disk (the brief did not mention it), so this
task is essentially a repeat of a finished one. To be sure, I re-checked the exact hard cases the brief points
at, and confirmed the "guess who's next" step still does no better than a scrambled version of itself, even after
the recent memory-tracking improvement. **Second, I went one step further than the earlier attempt** and built
the deeper "keep track of who did what to whom in this exact story" version it had suggested but never tested --
and that is also no better than chance here, because our meaning space is too coarse to tell two people apart by
what they have been doing. The upshot: the leftover mistakes need the big "understand the story" model we already
have queued as the number-one priority, plus a richer meaning representation -- not a "guess who's next" rule. My
recommendation is to fold this task into that number-one project rather than have someone rebuild it, and to NOT
add a "guess who's next" rule to the reader (it is measured to slightly hurt). The mechanism itself works on
clean textbook examples (8 out of 8 both times), which is exactly why it is worth knowing that the real hard
cases do not contain those examples.

## QUESTIONS
One judgement call for you at integration, the same one the 2026-08-29 solver raised: I marked this **REFUTED**
(the brief's coherence-prior mechanism is the wrong fix for this bucket, and it is a near-duplicate of an
owner-DONE negative) rather than SOLVED. A rigorous located negative is a full pass either way per the bar; the
content is identical. If you would rather it read SOLVED, only the label changes. Beyond that: none.

## NEXT STEPS
1. (Strategy) CONSOLIDATE: this priority-3 problem is a near-duplicate of the owner-DONE
   `the_reader_has_no_coherence_next_mention_prior` (2026-08-29). Recommend closing/merging it into the
   priority-1 north-star situation-model problem rather than assigning another solver to re-derive it. Re-verify
   the witness (4/4) first.
2. (Strategy) Do NOT land a coherence prior / event-coherence prior / static-KG cue into the reader -- all
   measured dead on this bucket. The graded pick + entropy-abstain is the right output (defer the confident
   structural residual).
3. (Fold) The AUDIT UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` 2b (the residual survives entity-maintenance
   composition; the event-state situation channel is p1-ceiling'd).
4. (Priority-1 follow-on) The north-star situation model + richer distributional semantics (p1) -- the real
   lever this cell localizes (the event-state oracle is near-chance at the current 12-dim grounded space).
