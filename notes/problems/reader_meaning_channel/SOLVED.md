---
problem: reader_meaning_channel
status: REFUTED
bar: "An UNFITTED read-time mechanism -- no model trained on the gold -- that uses the sensorimotor channel to choose a word's meaning ... AND IT MUST NOT BE A SOLE-CHANNEL DECIDER ... Combine it; do not substitute it ... Scored on held-out text, CI-separated over the strongest floor actually run, gated on the floor's upper bound ... The three controls that bound the existing result must be rebuilt and must still bind: candidate-only, shuffled-query, and an information-free version of your own winning arm which must LOSE ... Report coverage."
result: "On context-conditioned word-sense selection (subject-weighted accuracy; 287 multi-sense words, 841 trials; the reused, pre-registered instrument exp_context_conditioned_sense_selection_v1), the grounded multi-spoke hub (sensory+motor+AFFECT, concreteness-gated) combined with the sense-frequency prior (brain-faithful Bayesian score) does NOT clear the strongest floor. BAYES_HUB 0.4702 vs strongest floor MFS_PRIOR 0.4778, paired-word delta -0.0075 CI[-0.033,+0.019] (NOT separated). The brain control-gated arm BAYES_HUB_GATED 0.4844, delta +0.0066 CI[-0.017,+0.031] (NOT separated). Grounded coherence ALONE 0.4171 -- below the uniform floor 0.4316."
floor: "STRONGEST FLOOR ACTUALLY RUN = most-frequent-sense (MFS) prior = 0.4778 subject-weighted. It REPLACES the instrument's shipped uniform mean(1/k)=0.4316 floor, which was too weak: adding the sense-frequency prior (the brain's other half, omitted by every prior grounded-WSD cell) beats the grounded coherence CI-separated (+0.060 [+0.007,+0.115])."
controls: "candidate-only = context-lesion (C2): with no context BAYES reduces to the prior (0.4778) -- excludes context-cheating. shuffled-query = cross-item context swap (C1): grounded coherence drops 0.4171->0.3968 -- excludes query-independent scoring. info-free twin = spoke tables permuted: BAYES_HUB_INFOFREE 0.4563 < BAYES_HUB 0.4702, and coherence-only-info-free 0.3710 -- excludes a machinery-not-norms artifact. All three bind."
files_changed: "experiments/exp_reader_sense_selection_bayesian_hub_v1.py, experiments/grounding_channels.py, verification/test_reader_sense_selection_bayesian_hub.py, notes/problems/reader_meaning_channel/SOLVED.md (superseded exploratory cells: experiments/exp_reader_meaning_channel_combined_v1.py, experiments/exp_reader_meaning_channel_multispoke_v1.py)"
reverify: ".venv/Scripts/python.exe verification/test_reader_sense_selection_bayesian_hub.py"
---

# REFUTED -- the diagnosis is wrong: the reader's meaning gap is ARCHITECTURAL, not MODAL

## THE REFRAME (the aggressive, load-bearing claim -- read this first)

The brief's title and operative premise are *"the reader's meaning channel is the WRONG MODALITY --
supply the grounded/sensory channel and the reader will get meaning."* **On the evidence, that is the
wrong diagnosis, and it is refuted at read time.**

**The convergent fact.** Supplying a better MODALITY has now been tried as an unfitted read-time
mechanism on **SIX** meaning-USE instruments -- word-sense selection (this cell), pick-one-of-50
(`exp_discrimination_ceiling_v1`), cortical read (`exp_cortical_read_consolidated_v1`, sensorimotor
was the WORST arm), the on-path readout vs human similarity (`exp_meaning_asset_ctx_readout_variants_v1`),
end-to-end readout (`exp_substrate_end_to_end_readout_v1`, grounding never consulted), and the
multi-attribute fusion (`exp_grounding_multiattribute_fusion_v1`, +0.02 over the best single channel).
**Every one floored or failed.** The grounded modality's *only* demonstrated win is an OFFLINE
similarity TABLE -- a known literature result -- which never touched the reading path.

**What actually moved the number was ARCHITECTURE, not modality.** The single lever that beat the
grounded channel CI-separated was the **sense-frequency prior** (`log P(sense)`) -- and the brain
drill names the rest of the missing machinery precisely: Controlled Semantic Cognition
(Lambon Ralph/Jefferies/Rogers) says meaning USE = a **representation** (the ATL hub + spokes) plus a
**control network** (LIFG/pMTG) that biases retrieval to context and overrides the default only when
context conflicts with it. McClelland (2013) proves that settling computes exactly
`log P(sense) + Sum log P(evidence|sense)`. **The reader has spokes-worth of representation and NONE
of the control architecture.** You cannot fix a control deficit by adding more spokes -- which is why
six modality-supply attempts floored and the one architectural lever did not.

**So the problem is mis-framed:** it is not that the reader has the wrong KIND of information; it is
that it lacks the ARCHITECTURE that USES information -- a frequency prior and a conflict-gated control
network. That redirects the whole flagship from "wire in a better modality" to "build the controlled-
retrieval architecture."

**Scope of the refutation, stated exactly so it does not over-travel:**
- ✅ Refuted: *supplying the grounded modality improves the reader's read-time meaning USE.* Six
  instruments, one direct + five cited, all floored; the prior beats grounding CI-separated.
- ❌ NOT claimed: *grounding is useless.* It carries real meaning (offline similarity rho 0.27-0.37,
  established) and shows the exact brain-predicted flicker on the hard (subordinate) items. Its likely
  correct home is **graded inference/generalization**, not discrimination -- untested, and the
  strongest next experiment (a positive dissociation) is named in NEXT STEPS.
- ❌ NOT tested: the live `read()` adapter. A bench refutation of the *diagnosis*, not of an
  unbuilt mechanism.

## The one-paragraph version

The brief's actionable premise is "the reader's meaning channel is the wrong modality; wire in the
grounded (sensory/emotional) channel instead/as-well, it is 2-7x better." I built the **strongest,
most brain-faithful version of that channel** -- a multi-spoke hub (sensory + motor + **the emotional
VAD database**), concreteness-gated, combined with the incumbent the brain-correct way (a Bayesian
`log P(sense) + coherence(context, sense)`, with a control gate) -- and tested it on a **behavioral**
reading task (pick the right sense of a word in context), reusing a landed, pre-registered instrument
with a real floor and a full control battery. **It does not clear the floor.** The grounded coherence
adds nothing measurable over knowing how frequent each sense is (delta -0.0075, CI includes 0; even
the control-gated form +0.0066, CI includes 0). What *did* move the number is the piece every prior
attempt omitted: the **sense-frequency prior**, the brain's default that context must overcome. That
reframes the problem -- the reader's disambiguation gap is not, on this evidence, a missing-modality
problem; it is a missing-frequency-prior problem.

## Why this and not the experiment the brief describes (the honest journey)

The brief points at a read-time similarity/retrieval test. I built one first
(`exp_reader_meaning_channel_multispoke_v1`), then the owner halted me to check we were doing "what is
right, not what is easy." Two things came out of that check and a deep prior-work survey:

1. **The obvious experiment was contaminated.** A pick-one-of-N test draws its candidate pool *from
   co-occurrence*, so it cannot show an answer co-occurrence missed and cannot answer "is
   co-occurrence worth keeping"; and its ConceptNet oracle scores a *relational* structure against an
   *experiential* channel -- my own "a benchmark selected by a resource cannot fairly score that
   resource" trap.
2. **The clean similarity test was already done.** The grounded channel already beats co-occurrence on
   human similarity as an *offline table* (rho ~0.27-0.37; a known literature result), and the
   *on-path* co-occurrence readout vs human similarity already floored
   (`exp_meaning_asset_ctx_readout_variants_v1`). The grounded channel had also already floored or
   failed as an unfitted read-time mechanism on **five** instruments (WSD, pick-one-of-50, cortical
   read, on-path readout, end-to-end). Building another similarity arm would have re-measured a known
   result; the honest move was a *behavioral* test with the two things never tried: the **emotional
   database + gating**, and the **frequency prior**.

## What I built

- `experiments/grounding_channels.py` -- the multi-database grounded hub the owner asked for: four
  experiential norm sets exposed as separate spokes -- SENSORY (6 Lancaster perceptual dims), MOTOR
  (5 action/effector dims), **AFFECT (Warriner valence/arousal/dominance -- the emotional database)**,
  plus concreteness (Brysbaert) and age-of-acquisition (Kuperman) as gating signals. Each spoke votes
  only where it covers the word (no cross-database zero-fill). All SUPPLIED human ratings.
- `experiments/exp_reader_sense_selection_bayesian_hub_v1.py` -- reuses the landed, pre-registered
  sense-selection instrument (`exp_context_conditioned_sense_selection_v1`: eval-set, answer-masking,
  RI encoder, perceptual selector, the 0.4316 floor, and the C1/C2/C3 leakage controls) verbatim, and
  adds only: the multi-spoke gated **hub coherence** selector, the **sense-frequency prior**
  (leave-nothing-out corpus attestation, unfitted, never the eval label), the **Bayesian**
  combination, an **entropy control gate** (deploy coherence in proportion to the prior's uncertainty
  -- the brain's "use context when the default is uncertain," unfitted, no tuned threshold), and the
  dominant/subordinate and concreteness strata.
- `verification/test_reader_sense_selection_bayesian_hub.py` -- scaffold-free witness, recomputes
  every headline independently from the saved 841-trial population with its own bootstrap. All 5
  checks pass.

The mechanism is **brain-pinned**, not convenient: McClelland (2013) proves attractor/lateral-
inhibition settling computes exactly `log P(sense) + Sum log P(evidence|sense)`, so the argmax is the
licensed deterministic limit; the frequency prior is the subordinate-bias effect (Duffy/Rayner 1988);
concreteness-gating over POS-gating is forced by Vigliocco (2006). Two research drills are persisted:
`notes/research_wsd_context_conditioned_sense_selection_2026-08-23.md`,
`notes/research_channel_combination_reliability_weighting_2026-08-23.md`.

## What I measured (subject-weighted accuracy; 287 words, 841 trials; unfitted)

| arm | acc | vs strongest floor (MFS 0.4778) |
|---|---|---|
| uniform floor mean(1/k) | 0.4316 | (the instrument's shipped floor) |
| grounded coherence ALONE (COH_HUB) | **0.4171** | below even the uniform floor |
| **MFS_PRIOR (frequency prior)** | **0.4778** | **the strongest floor; +0.046 over uniform** |
| BAYES_HUB (prior + grounded, uniform) | 0.4702 | **-0.0075, CI[-0.033,+0.019] NOT separated** |
| BAYES_HUB_GATED (prior + control-gated grounded) | 0.4844 | **+0.0066, CI[-0.017,+0.031] NOT separated** |
| BAYES_HUB_INFOFREE (twin) | 0.4563 | loses to BAYES_HUB |

**The positive, and it is real:** the sense-frequency prior -- omitted by every prior grounded-WSD
cell, which all used the uniform floor -- beats the grounded coherence **CI-separated** (+0.060
[+0.007,+0.115]). Adding the brain's missing half lifts disambiguation above chance.

**The brain-fidelity signature IS present** (this is the interesting part of the negative): split the
items by whether the true sense is the *frequent* one (dominant, n=708) or the *rare* one
(subordinate, n=133). MFS scores **0.0** on subordinate items by construction (it always picks the
frequent sense); the grounded hub **rescues some to 0.083** -- coherence helps *exactly* where the
prior fails, the pre-registered subordinate-bias prediction. But subordinate items are only 16% of the
set, and on the 84% dominant items uniform blending *hurts* (adds noise), so the net is a wash. The
control gate protects the dominant items (0.544 vs MFS 0.551) and is the best arm (0.4844) -- yet
still not CI-separated. Also brain-consistent, not established: grounded coherence is best on
**concrete** words (0.475 vs 0.393 abstract), matching "concrete concepts grounded in the senses."

## What I did NOT establish

- **Nothing on the live `read()` path.** This is a standalone behavioral instrument. The adapter that
  would make `read()` consult the asset does not exist (the brief's other half), so no live-path claim
  is made or possible here. A standalone-harness result is a construction proof, not a capability on
  the reading path -- the long-term plan's own warning, and I am honoring it.
- **Not a refutation of the grounded channel in general.** It wins on offline human-similarity (known
  result), and it carries a faint, real, brain-located signal on subordinate senses. I tested ONE
  behavioral task. "Adds nothing to *disambiguation* over a frequency prior" is the claim; "useless"
  is not.
- **The subordinate/concreteness gains are hypotheses, not results** -- they are strata, small n, and
  the pre-registered overall gate is null. Do not quote them as wins.
- **The prior's lift is modest here** (+0.046) because this eval set's senses are near-equifrequent;
  on ordinary skewed text the MFS baseline is far higher, so the grounded channel's bar would be
  *harder*, not easier.

## What I would withdraw first if wrong

The positive sub-finding -- "the frequency prior is the lever" -- rests on MFS beating grounded
coherence CI-separated (+0.060 [+0.007,+0.115]); the lower bound is close to 0, so if I had to drop
one claim it is this one first. The **negative** (grounded adds nothing CI-separated over the prior,
uniform or gated) is the robust result and I would defend it last: it survives three controls, the
info-free twin, and an independent witness.

## PROPOSED hdlab CHANGE (a proposal, not a landed diff -- board Q111)

**The change the brief asked for is NOT justified by this evidence, and that is the finding.** Do not
wire the grounded channel in as a disambiguation decider or contributor to sense selection: even its
richest multi-spoke+emotion+gated+control-gated form does not beat a frequency prior CI-separated.

The change that IS justified, and it is small:

1. **Wherever the reader selects among competing senses/meanings, add a sense-frequency prior
   (most-frequent-sense) as the default**, and treat any meaning-channel evidence as a *contribution
   that must overcome it*, not as the decider. This is the brain's actual computation
   (`log P(sense) + coherence`) and the half currently missing. Concretely this is a change to the
   sense/meaning read-out selection, not to `grounded_similarity.py`.
2. **Keep `GROUNDED_CAP` and the contributor-only stance exactly as they are** -- this result
   independently confirms the cap's premise (the grounded channel must not decide).
3. If the grounded channel is ever deployed for meaning selection, deploy it **only via the entropy
   control gate** (weight by the prior's uncertainty) -- it is the only form that does not *hurt* the
   easy items, though it still does not measurably help overall.

Strongest-floor / control artifacts to reuse, not re-derive: MFS as the WSD floor (0.4778, replaces
uniform); the saved 841-trial population `data/exp_reader_sense_selection_bayesian_hub_v1/_scored_population.json`.

---

## TLDR (plain language)

We wanted to know if giving the reader human sensory-and-emotional ratings for words helps it work out
which meaning of an ambiguous word is intended in a sentence. I built the richest version of that idea
-- sight, sound, touch, action, *and* emotion, combined the way the brain does -- and tested it on a
real "pick the right meaning in context" task. **It didn't help.** Once you also give the system the
single most powerful ordinary clue -- *how common each meaning is* -- the sensory/emotional ratings
add essentially nothing on top. And that common-ness clue, which every past attempt here left out, is
actually the thing that helps. So the reader's trouble understanding word meanings looks less like "it
has the wrong kind of information" and more like "it wasn't using how-common-each-meaning-is." The
sensory/emotional channel does show a faint, real flicker in exactly the hard cases (rare meanings),
matching what the brain does, but it is too weak to count. **The deeper read, and the reason this is
filed REFUTED:** the reader's trouble is not the KIND of information it has -- it is that it is missing
the brain machinery that USES information (knowing which meaning is common, plus a control step that
decides when a sentence should overrule that default). More sensory or emotional data cannot fix a
missing control step. We spent this brief looking for a better ingredient; the evidence says the
recipe is what's missing.

## QUESTIONS

None blocking. One worth your steer, framed in NEXT STEPS.

## NEXT STEPS (reordered around the reframe)

1. **STOP supplying modalities to fix disambiguation/selection.** Six read-time attempts, all floored.
   The seventh will floor too. This is the "don't keep trying fancy available tools" discipline: the
   modality is not the binding constraint.
2. **Build the control architecture, which is the actual missing brain piece.** (a) Wire a
   most-frequent-sense prior into the reader's sense/meaning selection -- unfitted, the only lever that
   moved the number, and half of the brain's computation. (b) Then a conflict-gated control mechanism
   that overrides the prior only when context confidently disagrees (the LIFG gate; the entropy gate
   here is a crude first cut that already protects the easy items). NOTE the drill's catch: the
   multiplicative-gain form of control already failed here (`exp_task_local_normalisation_pool_v1`),
   blocked behind representation capacity -- the ADDITIVE prior + conflict gate is the untried,
   unblocked form.
3. **The strongest next EXPERIMENT -- a positive dissociation (file as a new problem, do not balloon
   this one).** The reframe predicts a double dissociation: the frequency prior wins on DISCRIMINATION
   (which sense) and loses on GENERALIZATION; the grounded channel wins on GRADED INFERENCE ("I know X;
   is Y similar enough to transfer?") and loses on discrimination. Proving grounding helps where the
   thesis says it should would turn this refutation into a positive theory of what each channel is FOR.
   This is the maximally aggressive empirical form; it is a real build and a genuinely different task.
4. The live-path adapter is still unbuilt and is the only way any of this becomes a *reading* result
   rather than a bench result -- this brief's other, still-open half.
