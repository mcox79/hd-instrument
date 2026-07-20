# DECISIVE DRILL: does an INTEGRATED graded-fit reader escape the post-hoc-contrastive null closure, and is it buildable on 99k words or corpus-gated?

**Date:** 2026-07-19. **Filed by:** research (3 parallel Sonnet lit-scans + director synthesis). **Trigger:** the
Scene-Coherence Verifier (SCV) HARD_FAILed as a trainer — a skunkworks VET found the post-hoc contrastive
coherence-bit gave EXACTLY 0.000 self-supervised training delta across all seeds, even with a gold-perfect
coherence oracle. Separately, brain drills this session established human thematic-fit resolution is graded,
verb-experiential/distributional (not curated-ontology), and INTEGRATED into incremental parsing rather than a
post-hoc filter. This note is the decisive fork-check on the one surviving brain-faithful thread: is "integrated"
actually a different learnable mechanism, or the same null relabeled, and is it buildable on what we have (99k
raw words) or does it require the bigger corpus investment (fork-c) first.

Composes with, does not re-derive: `research_mental_simulation_scene_verifier_error_signal_2026-07-19.md` (SCV
design + Angle B novel-combination flag), `research_prior_art_picturing_sentences_scene_comprehension_2026-07-19.md`
(WordsEye/SPICE prior art, WinoVis/LaViSA negative result on pixel routes), `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`
(two-signal gate: graded N400-style score + discrete P600-style escalation flag — this note supplies the missing
concrete computational form for the graded half that note left as "N400/Sentence-Gestalt-inspired" without an
explicit equation).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement; novel-synthesis
capped P<=0.50 per [[feedback-lit-scan-calibration-penalty]]). Established-lit findings are confidence-flagged per
source, not blanket-deflated.

---

## HEADLINE

**Escapes the post-hoc closure: YES, with high confidence on the GENERAL argument, deflated to P=0.45 on the
SPECIFIC combination needed here (never directly tested in combination). Buildable on 99k words: CONDITIONALLY YES
— but only if scoped as "learn the small number of cue-INTEGRATION weights," NOT "learn new continuous
distributional thematic-fit values from scratch," which IS corpus-gated (needs >=1M words minimum, realistically
100M-1B+). Recommendation: BUILD NOW, narrowly scoped to reuse existing WordNet/VerbNet categorical features as the
graded-fit input and existing LCCP cue-weights as the thing that gets trained, via a per-step error-driven update
integrated into commitment — NOT a post-hoc batch contrast. Defer "learn genuine distributional thematic fit from
raw co-occurrence" to the bigger-corpus fork; that specific sub-piece is honestly corpus-gated and should not be
attempted on 99k words.**

---

## 1. The concrete computational form (what we'd port instead of post-hoc contrastive)

Two established, mathematically explicit architectures exist in the literature for "a running graded expectation
reweights partial parses in real time" — and, importantly, most of the qualitative "constraints are integrated
online" literature (MacDonald, Pearlmutter & Seidenberg 1994; most Altmann & Kamide-style anticipation work through
at least Kukona et al. 2011) turns out to be VERBAL/architectural, not formally specified. That asymmetry is
itself a useful finding: only two lineages actually hand you an equation.

**(A) Competition-Integration Model, normalized recurrence (McRae, Spivey-Knowlton & Tanenhaus 1998, *JML*
38:283-312; algorithm from Spivey-Knowlton 1996).** Verified directly from primary text. Three-step iterative
update per processing cycle:
- normalize each constraint's support across competing structural alternatives: `Sc,a(norm) = Sc,a / sum_a(Sc,a)`
- weighted-sum to interpretation activation: `I_a = sum_c [ w_c * Sc,a(norm) ]` — literally a weighted sum of
  normalized constraint support, `w_c` a fixed per-constraint weight
- feedback boost: `Sc,a = Sc,a(norm) + I_a * w_c * Sc,a(norm)` — a recurrent, attractor-like loop, not one
  feedforward pass
Competition halts at a dynamic, relaxing criterion (`criterion = 1 - delta_crit * cycle`), and reading-time
predictions are a linear function of cycles-to-criterion. This model quantitatively out-predicted a two-stage
garden-path alternative on real self-paced reading data, and its weights transferred from an offline
sentence-completion task to online reading times — real explanatory work, not just curve-fitting. **Caveat, honestly
flagged: in the original paper the `w_c` weights are FIT OFFLINE to human completion-norm data — the paper does
not itself demonstrate an online learning rule for `w_c`. CIM is an explicit, verified mechanism for USE
(real-time structural commitment), not, as published, for LEARNING.**

**(B) Surprisal theory (Hale 2001; Levy 2008), a genuinely different mathematical move.** `S(w_i) = -log P(w_i |
w_1...w_{i-1})`, with Levy's result that surprisal is equivalent (in expectation) to the KL-divergence between the
belief distribution over parses before vs. after the word — i.e., a probability-reallocation account rather than
an activation-competition account. Thematic fit would enter only insofar as it is baked into `P(word | structure)`
via a lexicalized/semantically-augmented grammar. (Confidence: the general shape is well-established field
knowledge; the exact derivation could not be independently re-pulled from primary text this pass — flag as
recalled-not-freshly-verified, not in doubt, just not re-checked word-for-word.)

**Vosse & Kempen's Unification Space** gives a third explicit localist-connectionist activation-update equation
(`a_i(t+1) = alpha*f_forward + beta*a_i(t) - gamma*f_inhibition + delta*f_feedback`) with graded lexical preference
entering as initial activation levels from usage frequency — structurally kin to CIM's weighted-sum-plus-feedback,
but the literature surfaced does not confirm an equally explicit slot for continuous thematic-fit ratings
specifically (a scope gap, flagged not papered over).

**Verdict on Crux 1:** CIM's weighted-sum-with-recurrent-feedback is the concrete architecture to port for the
USE-time half (biasing which structure gets committed, word by word, using a graded score) — and it is
structurally almost identical to what the LCCP already does (a weighted sum over cues, argmax/threshold to commit).
The novelty this project needs to add is not the weighted-sum-integration mechanism itself (CIM already is that,
and the project's own LCCP already approximates it) — it is making the WEIGHTS in that sum LEARNABLE from an
online, per-step error signal, which CIM's own paper does not demonstrate and which is exactly Crux 2 below.

---

## 2. Does it escape the post-hoc closure? Adversarial verdict

**Yes — genuinely different mechanism, not the same thing relabeled, on the general architectural argument
(confidence: high, well-supported by two independent literatures). Deflated to P=0.45 on the SPECIFIC combination
this project needs (an online per-step delta-rule trained wc on top of CIM-style integration), because that exact
combination has not been directly demonstrated anywhere found.**

The reasoning, adversarially stated: in the SCV's null result, two full candidate parses were built end-to-end,
THEN a single scalar coherence-gap was computed and used to nudge weights. This is structurally identical to two
well-documented failure classes: (i) the reinforcement-learning temporal credit-assignment problem — a single
delayed/end-of-trial scalar reward does not, by itself, indicate which of many upstream decisions was responsible,
which is why per-step/process-reward decomposition exists as a known fix; (ii) the self-supervised
contrastive-learning collapse literature (SimCLR/BYOL/SimSiam) — a symmetric, global, end-of-computation
similarity/contrast objective admits degenerate solutions and needs an injected asymmetry (negatives, stop-gradient,
predictor head) to create a LOCAL, structured gradient path back to the parameters responsible. Both literatures
converge on the same general principle: a single global end-of-computation scalar under-specifies credit
assignment; decomposing it into local, per-step errors co-located with the parameters that produced each step
restores a well-posed learning signal.

Concretely, the error-driven syntactic-adaptation literature (Chang, Dell & Bock 2006 — an SRN trained with
backprop-through-time, error computed at EVERY word position, traced back through the specific recurrent weights
that produced that prediction; Fine & Jaeger 2013, Jaeger & Snider 2013 — per-item surprisal scaling a delta-rule-like
belief update) and predictive coding (Rao & Ballard 1999; Friston) both compute error at every level/timestep, not
as one global end-of-sequence judgment — this is definitional to predictive coding, not incidental. This is a
genuinely different shape of learning signal from "build two finished candidates, take one gap."

**The mandatory adversarial caveat (this is the single most decision-critical judgment call in this note):** this
argument only holds if the per-step signal is genuinely tied to identifiable local weights/cues at the moment of
update. If a "per-step" implementation still routes through an aggregated/blended judgment before applying any
update, it silently reintroduces the same aggregation problem one level down — same limitation, just relocated.
**This caveat is directly live for this project, not hypothetical**: re-reading the SCV's own design (companion
note), its training-signal step already claimed to do per-cue attribution ("log which of the LCCP's existing cue
weights favored the coherent candidate vs the incoherent one... apply a margin/perceptron-style update") — which
LOOKS like per-cue credit assignment, yet still gave exactly 0.000 delta. Two honest, distinguishable explanations,
not one: **(a)** the update was computed only on rare "exactly-one-candidate-coherent" trigger EVENTS (a sparse,
gated firing condition), and if that event essentially never fired given corpus/coverage sparsity (this session's
own repeatedly-observed pattern: SCV had only 4-20 usable contrast cases), then 0.000 reflects an EMPTY update set,
not a null mechanism — this is a data/coverage failure wearing a mechanism-failure costume, exactly the trap this
session's own sparsity-ablation discipline exists to catch. **(b)** alternatively, even where the event did fire,
the per-cue attribution step may have been under-specified in a way that still amounts to a blended judgment. The
literature scan cannot adjudicate (a) vs (b) from outside this project's own code — it can only supply the
diagnostic test (Section 4 below) that distinguishes them, and flag that BOTH explanations are literature-consistent,
so neither should be assumed without running that test.

---

## 3. The corpus precondition (decision-critical, answered numerically)

**Pure learned distributional graded thematic fit needs far more than 99k words. A hybrid design (existing
categorical scaffold + small learned integration weights) does not, and is the buildable path now.**

| Source | Corpus | Size | What it's used for |
|---|---|---|---|
| Resnik (1996) | Brown corpus | ~1M words | Selectional association — but WordNet-CLASS-smoothed, not raw noun counts, because raw counts were too sparse even at 1M words |
| Erk (2007); Erk, Padó & Padó (2010) | British National Corpus | ~100M words | Vector-space thematic fit; beat Resnik on error rate but had real coverage gaps even at this scale |
| Padó & Lapata (2007) | BNC (field-convention, not independently re-confirmed this pass) | ~100M words | Dependency-based semantic space models |
| Baroni & Lenci (2010) | ukWaC + BNC + Wikipedia | >1 billion words | Distributional Memory — field's standard large-scale convention |
| Hart & Risley (1995), calibration only | child-directed speech | 13M-45M cumulative words by age 4 (contested, later replications find a smaller gap) | Context for what "enough input to learn graded lexical/semantic regularities" looks like even in the one system (a child) known to succeed at this from scratch |

**99,000 words is ~1/10th of the smallest corpus ever used for this literature's raw-co-occurrence models (Brown,
~1M words) — and that smallest case ALREADY needed taxonomy-class smoothing to be usable — and roughly three orders
of magnitude below the field's actual working scale (BNC/ukWaC, 100M-1B+ words).** Confidence: high on the
qualitative scale conclusion (six convergent sub-findings); medium on the exact Erk/Padó-Lapata corpus-size
attribution specifically (PDF full-text extraction failed for two of the primary sources this pass; BNC-100M
attribution rests on secondary/field-convention corroboration, not a directly pulled sentence — flag, don't treat
as fully independently re-verified).

**The decision-critical nuance, and the thing that resolves the fork:** Resnik's own founding paper, and Clark &
Weir's (2002) explicit class-based-backoff method, exist SPECIFICALLY because raw co-occurrence at small-to-medium
scale is too sparse — the field's own fix is to back a sparse corpus off to a hand-built taxonomy (WordNet classes)
so that thin per-item counts inherit a reliable class-level estimate. **This project already has that hand-built
taxonomy for free** (WordNet supersenses + VerbNet selectional-restriction classes, already assembled for the SCV,
zero additional corpus cost) — meaning the piece the field's own smallest-scale precedent needed a corpus to help
build (the taxonomy) is not something this project needs to learn from 99k words at all; it is already given. What
remains to be learned from the 99k words is only the SMALL, LOW-DIMENSIONAL set of integration weights (how much to
trust each existing cue relative to the others at a commitment point) — a categorically smaller learning problem
than inducing continuous distributional semantics from scratch, and structurally the same scale of parameter as
the LCCP's own existing cue-weight vector. **This is why "buildable on 99k" and "corpus-gated" are BOTH correct,
for different sub-claims — this is not a contradiction, it is a scope distinction that must not be collapsed:**
learning NEW graded distributional fit values = corpus-gated (needs the fork-c bigger-corpus investment). Learning
the integration weights ON TOP OF the already-existing categorical scaffold = plausibly buildable now.

---

## 4. Verdict + must-fail (the decisive design)

**Net verdict: (a) YES, a real, different mechanism worth building — general architectural argument well-supported,
specific combination novel and capped P=0.45. (b) BUILDABLE ON 99K WORDS, narrowly scoped — reuse the existing
WordNet/VerbNet categorical features as the graded-fit INPUT (already built, not learned from corpus), reuse the
LCCP's existing cue-weight vector as the thing that gets trained, and switch the UPDATE RULE from post-hoc batch
contrast to a per-step, per-cue delta-rule fired at every word/commitment point the relevant cues are active — NOT
gated on a rare "exactly-one-candidate-coherent" event.**

**Minimal glass-box design:** at each hard-attachment decision point (reusing the LCCP's existing rival-candidate
generation, no new candidate-gen needed), compute a CIM-style weighted sum over the SAME cues the LCCP already
uses (word-order, animacy, preposition-cue, plus the WordNet-supersense/VerbNet-selectional-restriction type-match
bit from the SCV) to get a graded activation for each candidate structure — this is the "integrated" half, applied
DURING commitment, not after. Commit to the candidate whose activation clears the existing margin-gated threshold
(reuse the coref/animacy margin-gate discipline already built). Immediately after commitment, when the NEXT word
(or the sentence's resolution) confirms or contradicts that commitment, compute a per-cue prediction error
(delta_c = actual_outcome - cue_c's_normalized_support_at_commitment_time) and update `w_c += lr * delta_c *
Sc,a(norm)` for each cue INDIVIDUALLY — a direct delta-rule, not a single blended correction applied uniformly.

**Must-fail control 1 (firing-rate diagnostic — resolves the (a)-vs-(b) ambiguity from Section 2, the single
most important instrumentation addition this note recommends).** Report the RAW COUNT of decision points at which
the update rule fires (has at least one active, non-degenerate cue) on the full 99k-word corpus, not just whether
weights moved. **HARD-PASS:** firing rate is dense — the update fires at a large majority of hard-attachment
decision points (order-of-magnitude more than the SCV's 4-20-sentence event count), because it no longer requires
the rare "exactly-one-VerbNet-type-match" trigger, only "at least one cue is active," which is nearly every word.
**HARD-FAIL:** firing rate remains comparably sparse to the SCV's 4-20 cases — this would mean the sparsity wall is
a genuine WordNet/VerbNet COVERAGE gap on this specific corpus's verbs/nouns (a resource-coverage wall), not fixed
by switching from post-hoc to per-step architecture, and the honest conclusion becomes "resource-gated, not
mechanism-gated" (still distinct from, but adjacent to, the corpus-scale gating in Section 3).

**Must-fail control 2 (the central learning-signal test, mirrors the SCV's own Prediction 2, now run on the
per-step design).** **HARD-PASS:** the per-step delta-rule update, run over the raw 99k-word McGuffey corpus (no
gold used in the update), measurably and reproducibly-across-seeds moves the LCCP's cue weights in a direction that
increases held-out precision on an independent gold slice never touched by the update. **HARD-FAIL:** delta stays
at or near 0.000 despite Control 1 confirming dense firing (this would be a much stronger, cleaner negative than
the SCV's own — it would mean per-step architecture does NOT rescue the mechanism even with a dense, non-sparse
signal, directly refuting the adversarial argument in Section 2 for THIS specific implementation) — OR the delta
is nonzero on the training corpus but does not generalize to held-out gold (overfits the 99k-word corpus's own
idiosyncrasies — a distinct, separately-informative failure mode, not the same as a null signal).

**Must-fail control 3 (degrade-cue control, per the standing "teach a hint, let it learn the weight" discipline).**
Corrupt one specific input cue (e.g., randomly scramble the WordNet-supersense assignment for a held-out subset of
nouns) and confirm the LEARNED weight for that specific cue measurably DROPS relative to the uncorrupted control,
across seeds. **HARD-PASS:** weight drops. **HARD-FAIL:** weight is insensitive to the corruption — indicates the
weight isn't actually tracking that cue's real informativeness, i.e., the "learning" is not doing real
credit-assignment work even if the aggregate precision metric moved for some other reason (a construction-determined
risk explicitly worth ruling out, not assumed away).

**Explicit scope boundary (what NOT to attempt on 99k words):** do not attempt to learn new continuous
distributional thematic-fit VALUES (e.g., a from-scratch verb-noun co-occurrence score) from the 99k-word corpus —
Section 3's numbers make that a near-certain HARD-FAIL by corpus-scale alone, and a failure there would not be
informative (it would just confirm the well-established literature), wasting a test slot that should instead go to
Controls 1-3 above.

---

## Cross-thread synthesis

Directly resolves the open item in `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md`, which flagged the
graded (N400/Sentence-Gestalt) half of its two-signal gate as "needs upgrading" without specifying a concrete
computational form — CIM's normalized-recurrence weighted-sum-plus-feedback (Section 1) is that concrete form, and
this note additionally supplies the missing LEARNING rule (per-step delta-rule) that the original CIM paper itself
does not provide (its `w_c` were fit offline). Directly extends
`research_mental_simulation_scene_verifier_error_signal_2026-07-19.md`'s own Angle B finding (the SCV's central
claim is theoretically grounded but the exact combination untested, P=0.35) — this note narrows that gap further:
the reason the SCV's combination gave exactly 0.000 is now diagnosable as EITHER a sparse-trigger-event coverage
failure (matching this session's own repeatedly-observed sparsity pattern) OR an under-specified per-cue
attribution, and Section 4's Control 1 is the concrete instrument that tells them apart — this was not resolvable
from the companion note alone. Directly answers the open question left in the task brief: "is a real different
mechanism" and "buildable on 99k or corpus-gated" are NOT a single yes/no — they resolve to different verdicts for
different sub-claims (integration mechanism: different, real, buildable now at low-dimensional scope; new
distributional fit values: corpus-gated, defer to fork-c), and collapsing that distinction would have produced a
wrong, over-general answer in either direction.

---

## Substrate-product implications

If Controls 1-3 all pass: this becomes the first result in this arc that both (a) escapes the specific post-hoc
null-training closure with a positive, dense (not sparse-event-gated) learning signal, and (b) does so within the
already-staged 99k-word corpus, meaning it is buildable THIS cycle without waiting on the larger corpus-investment
fork. It would directly convert the "coherence gate" from the schema-fit-gate note's open item into a shipped,
brain-motivated, glass-box mechanism, and would validate the general principle (per-step > post-hoc for
trainability) as something this project can bank going forward for any future self-supervised signal design, not
just this one. If Control 1 hard-fails (sparse firing persists): the honest conclusion is that WordNet/VerbNet
COVERAGE on this specific corpus's vocabulary is the bottleneck, not architecture — worth a scoped, cheap coverage
audit (how many of the corpus's verb/noun types actually have usable VerbNet/WordNet entries) before further
architecture investment. If Control 2 hard-fails despite dense firing (Control 1 passes): this is the strongest,
cleanest negative this whole arc could produce — it would mean per-step credit assignment does not rescue
self-supervised learning from an internal coherence/fit signal in THIS architecture, at THIS data scale, and the
honest recommendation becomes: bank the CIM-style integration as a SELECTOR only (like animacy), park the
self-training ambition, and treat the bigger-corpus investment (fork-c) as the only remaining path to a genuinely
learned graded reader — a real, informative, structural result either way.

---

## Citations (verified count)

McRae, Spivey-Knowlton & Tanenhaus (1998, *JML*, verified from primary text); Spivey-Knowlton (1996, normalized
recurrence algorithm); MacDonald, Pearlmutter & Seidenberg (1994); Pearlmutter, Daugherty, MacDonald & Seidenberg
(1994); McClelland, St. John & Taraban (1989, Sentence Gestalt); Vosse & Kempen (2009, *Cognitive Neurodynamics*);
Hale (2001); Levy (2008); Narayanan & Jurafsky (2002); Jurafsky (1996); Altmann & Kamide (1999); Kukona, Fang,
Aicher, Chen & Magnuson (2011, *Cognition*, explicitly declines to commit to a formal model); a 2025 *JML*
predictive-coding-for-online-sentence-processing paper (abstract only, full text 403-blocked, flagged unverified);
Chang, Dell & Bock (2006, *Psychological Review*, verified — SRN + backprop-through-time, per-word local error);
Fine & Jaeger (2013, *Cognitive Science*); Jaeger & Snider (2013, *Cognition*); Rao & Ballard (1999, *Nature
Neuroscience*, verified — hierarchical per-level per-timestep error); Friston (free-energy principle, general);
Resnik (1996, *Cognition*, verified — Brown corpus ~1M words, WordNet-class-smoothed); Clark & Weir (2002,
class-based probability estimation via semantic hierarchy); Erk (2007, ACL); Erk, Padó & Padó (2010, *Computational
Linguistics*); Padó & Lapata (2007, *Computational Linguistics*, corpus size inferred from field convention, not
independently re-confirmed this pass); Baroni & Lenci (2010, *Computational Linguistics*, Distributional Memory,
ukWaC/BNC/Wikipedia); Hart & Risley (1995, 30-million-word-gap study, contested by later replications, cited as
context not as settled fact); SimCLR/BYOL/SimSiam collapse literature (general ML-theory principle, not a single
paper); classical RL temporal-credit-assignment-problem literature (general principle). **Approximate distinct-source
count: 27.** Two sources (Padó & Lapata's exact corpus figure; the 2025 JML predictive-coding paper's full mechanism)
were explicitly flagged as unverified-from-primary-text this pass and should not be treated as independently
confirmed beyond field-convention corroboration.
