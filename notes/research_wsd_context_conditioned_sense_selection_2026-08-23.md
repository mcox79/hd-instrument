# Research: how does the brain select the context-appropriate sense of an ambiguous word?

Filed by: research sub-agent, 2026-08-23. Topic: `reader_meaning_channel` — drill for a brain-faithful
CONTEXT-CONDITIONED WORD-SENSE SELECTION mechanism (pick 1 of k senses given a context sentence),
requested directly by a solver working that problem. Companion to
`notes/research_channel_combination_reliability_weighting_2026-08-23.md` (filed same day, adjacent
problem: how to WEIGHT distributional vs sensorimotor channels for concept meaning generally — that
note is about channel fusion; this one is about DISCRETE SENSE CHOICE given context, a different
mechanism question sharing only the hub-and-spoke background).

## HEADLINE

**The brain does NOT select a sense by scoring context-coherence alone.** Every converging account —
the reordered access model (Duffy, Morris & Rayner 1988), the CSC control-network literature, and the
two computational-modeling traditions (Bayesian identification models, attractor/lateral-inhibition
models) — has TWO terms: a **frequency/dominance PRIOR** (pinned via the subordinate bias effect: a
measurable RT cost, ~13-46ms in replication, for a low-frequency sense even under strong disambiguating
context) and a **context-coherence LIKELIHOOD** term. A mechanism using coherence-with-context alone,
with no frequency prior, structurally cannot reproduce the single most robust empirical signature in
this literature (frequency asymmetry surviving disambiguation) and will make a specific, predictable
class of errors: subordinate-sense-favoring context items scored no differently from dominant-sense
items, when human data (and any brain-faithful model) shows a residual bias toward the dominant sense
even there. McClelland (2013, *Frontiers in Psychology*) proves formally that interactive-activation/
lateral-inhibition attractor networks compute EXACTLY a Bayesian posterior when bias terms encode log-
priors and external input encodes log-likelihoods — so "argmax over frequency-prior + context-coherence"
and "attractor settling with frequency-set basin geometry" are the SAME computation, not rival
mechanisms. This substrate should implement the algebraic (argmax-over-sum) form, NOT the recurrent
attractor form — ORGAN_MAP C4 already found, on this exact representation, that attractor/CA3-style
settling would make near-neighbour discrimination WORSE given how fragile the correlational structure
is; the two-term score gets the same brain computation without that cost.

## Mechanism, question by question — PINNED vs MODELER-CHOICE

**1. Controlled Semantic Cognition (Lambon Ralph, Jefferies, Patterson & Rogers 2017, *Nat Rev
Neurosci* 18:42-55).** PINNED: ATL = transmodal hub; LIFG/pMTG = control network that "dynamically
monitors and modulates" retrieval (review's own framing). PINNED, Chiou, Humphreys, Jung & Lambon
Ralph 2018 (*Cortex* 103:100-116), 5-node DCM: the effortful/task-relevant condition selectively
strengthens IFG's connectivity **to the spoke/region holding the task-relevant feature dimension**
(quote: "the control system dynamically heightens its connectivity with relevant components of the
representation system"). PINNED, Hoffman, McClelland & Lambon Ralph 2018 (*Psychol Rev* 125:293-328) —
this is the closest thing to an actual equation in the whole scan: hub input = **a weighted
combination of candidate response options**, weights set by a **context buffer** ("prediction units"
from the previous timestep), reweighted continuously as the network **settles** over iterations. This
is graded, soft biasing of retrieval toward context-relevant candidates — NOT selection from a
discrete list, and NOT a hard gate. MODELER-CHOICE tension worth flagging: Jackson, Rogers & Lambon
Ralph 2020 (*Nat Hum Behav*) found their own best-fitting architectures put control on the SPOKES
(peripheral), not on the hub-input weights as in Hoffman et al 2018 — the same lab has two computational
accounts of WHERE control acts, unresolved. PINNED, Gao, Zheng, Krieger-Redwood, Halai, Margulies,
Smallwood & Jefferies 2022 (*eLife* 11:e80368): weakly-related (controlled) retrieval recruits
measurably HIGHER-dimensional coding in IFG/angular gyrus than strongly-related (automatic) retrieval —
independent confirmation of the same dimensionality-under-control-demand pattern already pinned in
ORGAN_MAP C3.

**2. Time-course (Swinney 1979; Duffy, Morris & Rayner 1988).** PINNED, Swinney 1979 (*J Verbal Learning
& Verbal Behavior* 18:645-659): at word offset, BOTH senses are primed regardless of prior context;
several syllables later only the contextually-appropriate sense remains primed. This is **exhaustive
access, then rapid context-driven suppression** — context does NOT pre-select before both senses ever
activate. PINNED, Duffy/Morris/Rayner 1988 (*J Mem Lang* 27:429-446), corroborated via the direct
replication Binder & Rayner 1998 (*Psychon Bull Rev* 5:271-276): 2x2 design (balanced vs biased
homographs x neutral vs disambiguating context). Neutral context: balanced words read slower than
controls (both senses compete, no frequency edge); biased words read at baseline (dominant sense wins
on frequency alone, free). Disambiguating context favoring the SUBORDINATE sense: still reliably slower
than dominant/control — ~33-46ms under strong context, ~13-24ms under weak context, in the replication's
numbers. **This is the subordinate bias effect: frequency acts as a prior that context must actively
overcome, and even strong context leaves a residual cost.** Best-supported model: the reordered access
model (over pure exhaustive-access and pure selective/context-only access — Simpson 1981/1994's
diagnostic 3-way interaction tested and non-significant). No source states a literal equation, but the
qualitative rule is explicit: resting activation set by frequency (dominant sense has a "head start"),
context adds an activation boost to the contextually-relevant sense, and cost occurs specifically when
frequency and context conflict and the two activations become close enough to compete.

**3. N400 / prediction (Kutas & Federmeier 2011).** PINNED, DeLong, Urbach & Kutas 2005 (*Nat Neurosci*)
+ 9-lab replication Nieuwland et al 2018 (*eLife*): N400 amplitude scales continuously (gradedly) with
cloze probability at the noun — pre-activation is graded, not all-or-none (the finer article/phoneme-
level pre-activation claim did NOT replicate; treat that specific piece as contested). PINNED
computational form, Rabovsky, Hansen & McClelland 2018 (*Nat Hum Behav*): N400 amplitude proportional
to the **magnitude of change forced on an internal "meaning"/situation-model representation** by the
incoming word — an implicit prediction error, not measured against a fixed template but against the
CURRENT discourse state (this matches ORGAN_MAP F5's pinned reference point exactly). Their base model
has **no separate precision multiplier** — error magnitude alone. PLAUSIBLE but not independently
verified against primary text (paywalled): Nour Eddine, Brothers, Wang, Spratling & Kuperberg
(bioRxiv 2023 / *Cognition* 2024) implement N400 as an explicit **precision-weighted** lexico-semantic
prediction error using Spratling's predictive-coding algorithm, precision tied to cue reliability — this
is consistent with, and appears to be the direct source of, ORGAN_MAP F5's "form pinned: precision x
error; precision estimator UNPINNED" line. **No source anywhere explicitly states "the correct sense is
the one that best satisfies the prediction"** for word-sense selection specifically — this is a natural,
unforced extension of the graded-pre-activation + prediction-error framework, not a pinned finding.
Treat it as MODELER-CHOICE with strong indirect support, not as replicated fact.

**4. What representation does coherence get computed over?** Not separately re-scanned this cycle
(covered in depth by the companion note filed the same day): associative/co-occurrence and amodal
experiential-hub representations both measurably contribute (Bruni, Tran & Baroni 2014; Andrews,
Vigliocco & Vinson 2009), with no published formula for their combination weight — see that note's
findings 3-4 for full citations. For sense selection specifically, the CSC literature above answers the
representation question differently: coherence should be computed as a **weighted-toward-relevant-
features** comparison (the IFG-boosted spoke/dimension), not a flat whole-vector similarity — i.e. the
representation the likelihood term reads from is itself supposed to be reshaped by context, and ORGAN_MAP
C3 already found that reshaping (multiplicative per-dimension gain) HARD-FAILS on THIS substrate's
current 256-dim representation for an estimation-noise reason (dims with the largest anchor-difference
are the worst-estimated at ~70 obs/concept), strictly blocked behind B4 (representation capacity). The
frequency-prior fix proposed below does NOT touch that blocked path — it is additive to the existing
flat-coherence score, not a reshaping of it.

**5. The computational synthesis.** Bayesian argmax and attractor/lateral-inhibition settling are the
SAME computation, not competing hypotheses — PINNED as a formal equivalence (not sense-specific) by
McClelland 2013 (*Frontiers in Psychology* 4:503): an interactive-activation network with softmax/
logistic units computes exactly `net_i = log P(sense_i) + sum_j log P(evidence_j | sense_i)`, i.e. a
log-posterior, when its bias terms equal log-priors and its input weights equal log-likelihoods.
Kawamoto 1993 (*J Mem Lang* 32:474-516, PDP attractor model) and Rodd, Gaskell & Marslen-Wilson 2004
(*Cognitive Science* 28:89-104, recurrent attractor over form->semantics) both use frequency-shaped
basin geometry (via training) as the prior and treat context as an external bias vector on the
settling trajectory — consistent with, though not verbatim-quoted confirmation of, the same
prior x likelihood picture. No source stages these as rivals and declares a winner; the honest read is
that attractor settling is HOW the brain implements this decomposition, and the decomposition itself
(prior + likelihood) is the level worth copying per this project's own "copy the computation, not the
implementation particulars" discipline — especially since the recurrent-settling implementation is
explicitly the piece ORGAN_MAP C4 says not to build here.

## The computational rule to implement

```
score(sense_i | context, lemma) = log_prior(sense_i | lemma)  +  coherence(context, sense_i)
decision = argmax_i score(sense_i | context, lemma)
```

- `log_prior(sense_i | lemma)`: log of the sense's relative frequency for that lemma. UNFITTED,
  read-time-computable from a sense-frequency resource (WordNet/SemCor sense-frequency ranks, or a
  cheaper proxy — lemma-sense co-occurrence counts already sitting in the same corpus this substrate
  reads, if a formal tagged resource isn't wired). Zero fitting to task gold — the frequency table is
  built once, off-task, exactly like the Brysbaert concreteness table already used elsewhere.
- `coherence(context, sense_i)`: the EXISTING grounded-similarity-to-context-words score, unchanged.
  This is the current mechanism's only term; it plays the role of a log-likelihood.
- Decision by argmax is licensed (ORGAN_MAP C2): for a top-1/2AFC accuracy metric, argmax is the
  deterministic limit of a softmax/attractor settling and produces the same expected score. Building
  the recurrent settling machinery itself is NOT recommended (C4's fragility finding still applies) —
  the sum-then-argmax form gets the same computation algebraically.

## Arms to test (all UNFITTED, all read-time-computable)

1. **Prior + coherence (primary arm).** As above. Falsifiable, mirroring the actual Duffy/Morris/Rayner
   design: split test items into DOMINANT-CONGRUENT (context supports the higher-frequency sense) and
   SUBORDINATE-CONGRUENT (context supports the lower-frequency sense) buckets using the same frequency
   table the prior reads from.
   - **HARD-PASS**: aggregate accuracy improves over coherence-only by a CI-separated margin, AND the
     gain is asymmetric in the specific direction the mechanism predicts — larger margin/accuracy gain
     on DOMINANT-CONGRUENT items than on SUBORDINATE-CONGRUENT items (the prior helps where it agrees
     with context and costs a little where it disagrees, reproducing the subordinate-bias signature
     rather than a uniform lift). A uniform gain across both buckets is not evidence for this mechanism.
   - **HARD-FAIL**: no CI-separated gain, OR the gain is uniform across buckets, OR SUBORDINATE-CONGRUENT
     items get WORSE by more than the measurement noise floor (the prior should cost a LITTLE there,
     matching human RT cost, but must not flip net accuracy negative — if it does, the prior term is
     too strong relative to coherence and needs reweighting, not abandonment).
   - Per the standing "print reachability numbers before reading the verdict" discipline: report how
     many items actually have coherence and frequency-prior DISAGREEING (if they never disagree, there
     is nothing for the prior to fix and a flat result is a reachability failure, not a refutation).

2. **Precision-weighted coherence (predictive-coding-inspired).** Weight the coherence/likelihood term
   by an unfitted proxy for context reliability (e.g. count of disambiguating content words in the
   local context window, or how peaked the context's own coherence distribution already is across the
   k senses) rather than a fixed weight, per the Nour Eddine/Kuperberg precision x error framing.
   - **HARD-PASS**: further CI-separated gain over arm 1, concentrated in LOW-precision (thin-context)
     items specifically — where the frequency prior should dominate because coherence is unreliable.
   - **HARD-FAIL**: no differential gain by context-richness bucket, or gain is uniform.

3. **Coherence-only (control, current mechanism).** Retained strictly as the baseline being tested
   against — the existing production arm, not a hypothesis under test.

P_deflated for the "prior+coherence beats coherence-only with the predicted asymmetry" (arm 1
HARD-PASS): **0.40** (raw estimate ~0.60-0.65 from four converging independent lines — CSC's own
literature, the reordered access model's robust replication, the Bayesian/attractor equivalence proof,
and this project's own C3 finding that context-as-a-term already produced the largest positive result
in that section of ORGAN_MAP — deflated 0.20-0.25 per the mandatory lit-scan penalty, since no source
tests this exact unfitted formulation on this exact task). Arm 2 (precision-weighting) P_deflated:
**0.30** (more speculative — the precision-weighted N400 model itself could not be independently
verified against primary text this cycle).

## Cross-thread synthesis (this substrate's own prior work)

- **ORGAN_MAP C3** (semantic control): multiplicative per-dimension gain — the literal Chiou/Lambon
  Ralph 2018 mechanism — was already built and tested (`exp_task_local_normalisation_pool_v1`,
  HARD_FAIL_GAIN_HURTS, d=-0.0220 CI[-0.034,-0.0097]) and found to fail for an ESTIMATION-NOISE reason
  (256-dim / ~70 obs-per-concept regime, worst-estimated dimensions are exactly the largest-difference
  ones), not a mechanism-wrong reason — strictly blocked behind B4 (representation capacity). The
  frequency-prior arm proposed here is a DIFFERENT lever (additive scalar term per sense, not a
  per-dimension reweighting) and does not require B4 to resolve first.
- **ORGAN_MAP C4** (attractor settling): explicitly NOT recommended to build on this substrate's current
  representation — distinctive features are weakly correlated, so CA3/attractor-style completion would
  make near-neighbour discrimination WORSE. This scan's finding that attractor settling and Bayesian
  argmax are the SAME computation (McClelland 2013) means the algebraic form captures the brain's
  computation WITHOUT needing the recurrent machinery C4 warns against.
- **ORGAN_MAP C2** (winner selection): argmax already judged fine for a top-1/2AFC metric; no change
  needed there — this scan's contribution is entirely to the SCORE being argmax'd over, not the
  selection rule itself.
- `exp_polysemy_context_bound_cpu_v1` (2026-07-03, HARD_PASS) and `exp_temporal_contextual_
  multiseed_cpu_v1` (2026-07-03, HARD_PASS) — prior landed polysemy work on this substrate; not
  reopened this cycle, worth reading before building the frequency-prior arm to check whether either
  cell already has a frequency signal wired that this proposal would duplicate.
- Companion note `research_channel_combination_reliability_weighting_2026-08-23.md` — adjacent problem
  (channel fusion weight, not sense-prior), shares the hub-and-spoke background citations (Lambon Ralph
  et al.) but is a distinct mechanism question; do not conflate the two combination rules.

## Substrate-product implications

The concrete, low-risk next build is a **lemma-sense frequency table** (WordNet/SemCor-derived or a
corpus co-occurrence proxy) consulted as an ADDITIVE log-prior term beside the existing coherence score
— no change to the representation, no per-dimension reweighting, no recurrent settling, and therefore
none of the failure modes already found in C3/C4. It directly targets the single best-documented gap
between "coherence-only argmax" and the brain's actual behaviour: the complete absence of any variable
that could reproduce the subordinate bias effect. If it clears the HARD-PASS bar with the predicted
asymmetry, that is evidence the mechanism is right, not just that a number moved (per the standing
"score levers on the task, with the qualitative signature the brain predicts" discipline). If it
HARD-FAILs cleanly (uniform gain or no gain), that rules out a naive additive prior and redirects to
precision-weighting (arm 2) as the next test rather than abandoning frequency information altogether.

## Citations (verified count)

18 distinct primary sources, each cross-checked by at least one of the four lit-scan sub-agents via live
WebSearch/WebFetch (not from memory), with explicit PINNED/unverified flags preserved above: Lambon
Ralph, Jefferies, Patterson & Rogers 2017; Chiou, Humphreys, Jung & Lambon Ralph 2018; Hoffman,
McClelland & Lambon Ralph 2018; Jackson, Rogers & Lambon Ralph 2020; Jefferies 2013; Gao, Zheng,
Krieger-Redwood, Halai, Margulies, Smallwood & Jefferies 2022; Swinney 1979; Duffy, Morris & Rayner
1988; Binder & Rayner 1998; Simpson 1981/1994; DeLong, Urbach & Kutas 2005; Nieuwland et al 2018; Kutas
& Federmeier 2011; Rabovsky, Hansen & McClelland 2018; Nour Eddine, Brothers, Wang, Spratling &
Kuperberg 2023/2024; Kuperberg & Jaeger 2016; Kawamoto 1993; Rodd, Gaskell & Marslen-Wilson 2002/2004;
McClelland 2013; Norris 2006 (Bayesian Reader, ruled out as sense-specific); Ferreira & Patson 2007
(good-enough processing, noted as a genuine third position, not adopted). Several primary-text sources
were paywalled/access-blocked this cycle (Jefferies 2013 full text, the 2024 Cognition/bioRxiv precision
N400 equations, Kawamoto 1993 and Rodd et al 2004's literal update equations) — those specific numeric/
equation-level claims are flagged PLAUSIBLE-NOT-VERIFIED above rather than asserted as pinned, per the
"do not invent detail past what was fetched" instruction given to each lit-scan sub-agent.

## Caveats on this note

- Per the mandatory lit-scan calibration penalty, all P estimates above are deflated 0.15-0.25 from the
  raw synthesis estimate and novel-synthesis P is capped at 0.50.
- `research_field_advisor.py` was run at cycle start per the standing ritual; its candidate list
  (free-probability, semiconductor Glauber dynamics, etc.) is built for substrate-physics topics and is
  not adjacent to this cognitive-neuroscience question — noted, not applied, same as the companion note.
- This note does not itself run the cheap decisive test — building the frequency table and re-scoring
  the existing held-out sense-selection set is the next actionable step.
