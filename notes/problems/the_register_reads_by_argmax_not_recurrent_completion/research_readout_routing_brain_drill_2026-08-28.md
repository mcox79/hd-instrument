# Brain drill: when is recurrent completion the correct readout? (2026-08-28)

Finer brain-foundational drill for `the_register_reads_by_argmax_not_recurrent_completion`, launched at
kickoff per the SOLVER OPERATING PROTOCOL + owner's standing "if the brain can do it and we can't,
understand why". Verbatim report archived below. **It CORRECTS the brief's "CA3 recurrent completion"
framing in three load-bearing ways — treat these as the mechanism spec.**

## The three corrections that reshape the build

1. **The register readout is theta-gamma SERIAL decode-and-suppress (Lisman & Idiart 1995), NOT a CA3
   attractor.** CA3 recurrent completion is PINNED as *single-attractor* cue->stored-pattern denoising
   (Marr 1971; Treves & Rolls 1994; Nakazawa 2002). There is **no** classical account of CA3 jointly
   decoding a superposition. The best-grounded biological analogue for reading out several bundled items
   is the theta-gamma phase code: decode the strongest item in a gamma sub-cycle, SUPPRESS it
   (inhibition-of-return), decode the next from the residual — which is exactly successive-interference-
   cancellation / the resonator's iterate. Resonator-network-as-CA3 is an ENGINEERING ANALOGY (Frady et
   al. 2020 claim no neural implementation) — FLAG it. Our SIC decode is faithful *as theta-gamma serial
   readout with inhibition-of-return*, and confidence-ordered (strongest-first) is the faithful schedule.

2. **The hub-bias fix is ARCHITECTURAL, not corrective.** The brain does not de-bias the attractor for
   ranking; it routes ranking to a circuit that never runs recurrent settling to convergence
   (perirhinal/global-match familiarity; MINERVA2/differentiation). Evidence it does NOT self-correct:
   hippocampal replay is *biased toward* frequent/rewarded items, not away. => our reconciliation is
   "DON'T complete on the ranking task", i.e. route by query structure. Matches the cortical-store
   solver's empirical finding (graded population read beats attractor for ranking).

3. **O'Reilly & McClelland 1994 separation/completion tradeoff is the spine.** Completion over
   orthogonal/random (pattern-SEPARATED) codes reduces to nearest-neighbor cleanup — no manifold to
   interpolate; the register's i.i.d. FHRR codes are exactly this regime, so the right op is known-key
   crosstalk cancellation (serial decode), and a codebook ATTRACTOR should NOT help (discriminating
   control: modern-Hopfield ties argmax on the register). Completion over graded/correlated (cortical
   semantic) codes is where settling causes hub collapse — same pathology shows up independently in the
   word-frequency mirror effect and semantic-dementia prototype regularization (Rogers et al. 2004).

## The routing rule (the deliverable — INFERENCE composite, each gate pinned)

Route to **serial completion / iterative unbind-and-suppress** when ALL of: (1) known slot/key structure
("what filler was bound to this known role"); (2) single discrete target on a pattern-SEPARATED substrate;
(3) cue measurably incomplete / high crosstalk (Nakazawa: a full cue does not need CA3); (5) if superposed,
decode SERIALLY with suppression, not settle to one blended attractor.
Route to **graded/direct read** (familiarity-style) when ANY of: (1) task is rank/typicality/similarity
over many candidates; (2) codes are graded/correlated by design (settling -> hub collapse); (3) SNR/margin
already high (full cue -> completing only risks pulling a correct-but-unusual answer toward a generic
neighbor).

**Falsifiable load-bearing claim:** cue completeness / query structure (is there a known key) is the
DOMINANT gate; hub-bias scales with how far you push settling on a graded/correlated code, not with store
size. Predicts: completion helps specifically under partial-cue/high-crosstalk and is INERT at full cue
(matches the audit's low-load inertness); hub-corruption gets WORSE as the query degrades. Both testable.

## What this changes in the experiments
- Exp1 arms: add HOPFIELD_PERSLOT (codebook attractor) as the discriminating control that should TIE
  argmax (no manifold) while SERIAL known-key decode wins — proves the gain is crosstalk-cancellation.
- Serial decode: confidence-ORDER the peel (strongest slot first) + explicit inhibition-of-return
  (gamma-cycle budget is a PARAMETER to sweep, not adopt).
- Exp3 reconciliation: route by recall(known-key, separated)->complete vs rank(correlated)->graded; show
  forcing completion on the correlated ranking store re-promotes hubs (reproduce), and the gate avoids it.
- Test the falsifiable prediction: hub-corruption scales with settling depth on correlated codes;
  completion inert at full cue.

---

## VERBATIM REPORT

**Method note:** verified specific claims/dates/authors against base knowledge of hippocampal systems
neuroscience (CLS, Marr/Treves-Rolls, dual-process recognition are textbook) + pulled less-obvious
mechanistic pieces (theta-gamma readout, CA1 comparator, semantic-dementia attractor collapse). PINNED =
evidence-grounded (still deflate on stretch to our engineering case); INFERENCE = computational-level
synthesis, not a measured brain fact.

**1. Recollection-vs-recognition/ranking is real and anatomically double-dissociated — PINNED.**
CLS (McClelland/McNaughton/O'Reilly 1995; O'Reilly & Rudy 2001): hippocampus = sparse pattern-separated
conjunctive encoding for one-shot binding; neocortex = slow overlapping structured encoding for graded
similarity. Two representational FORMATS for two jobs, not two speeds. Yonelinas 2002/2022 + Aggleton &
Brown 1999: recollection = hippocampal-diencephalic (DG/CA3 completion -> bound, quasi-all-or-none
recovery); familiarity = perirhinal-MD-thalamic (continuous graded strength, largely WITHOUT hippocampal
completion) — a genuine DOUBLE DISSOCIATION in amnesia. High-res fMRI fractionates within HPC (DG/CA3
repetition-suppression/familiarity; behavioral separation more DG, object recognition more CA3). NO single
upstream switch: two parallel channels always computing; what varies = which output is USABLE (a ranking
task has no bound role to recollect) + a physiological gate on when completion DOMINATES. "Routing" = 
arbitration downstream of two continuously-running systems, weighted by task demands + signal quality.

**2. What CA3 completion is for.** Marr 1971 / Treves & Rolls 1994 / Rolls 2013: CA3 recurrent collaterals
= auto-associative (Hopfield-like) attractor, stores patterns as fixed points, completes a degraded cue to
the nearest. Nakazawa 2002 (Science 297:211) = load-bearing causal result: CA3-NMDAR-KO mice retrieve
NORMALLY with full cues, fail ONLY under PARTIAL cue -> the brain does not route through completion when
the cue is sufficient (cue completeness is a measured gate). [Caveat: Nakashiba 2008 / PMC3084823 dispute
whether NMDA-plasticity specifically is required vs recurrent architecture sufficing — a how-dispute, not
a whether.] Norman & O'Reilly 2003: recollection = CA3 pattern completion; familiarity = separate
non-completing cortical/EC match — direct ancestor of the two readout modes. **Does CA3 read a superposed
SET jointly? Real gap.** Classical picture = ONE attractor, one settle; no account of joint factored
decode. Best-pinned neural analogue for successive decode of a superposition = theta-gamma phase code
(Lisman & Idiart 1995, Science 267:1512): items held superposed are read out one per gamma sub-cycle
nested in theta, recently-read items refractory/suppressed -> structurally SIC. Real ephys support
(theta-gamma coupling, phase-coded replay). Resonator networks (Frady/Kent/Olshausen/Sommer 2020) =
explicitly VSA/computational-level, NO claimed neural implementation; resonator-as-CA3 is engineering
analogy. Loose grounding: (i) the cleanup step = CA3 cleaning a noisy vector to a stored codeword (well
grounded); (ii) "known keys" ~ BIC model (Eichenbaum/Yonelinas/Ranganath 2007): item (perirhinal/LEC) and
context (parahippocampal/MEC) on separate channels converging + binding in HPC — brain DOES have "two
known roles, bind then unbind against a known role". N-ary factored decode from that = INFERENCE.

**3. Hub/basin bias — real; brain shows the SAME pathology when it lets completion run over graded codes.**
General attractor theory: more-stored/more-overlapping patterns get larger/deeper basins (spurious/mixture
+ prototype states). Direct behavioral evidence it corrupts fine discrimination: word-frequency MIRROR
EFFECT — high-freq ("hub-like") words -> more false alarms, fewer hits; Word Attractor Space models
(PMC1838560) explain it exactly as your finding. Global-matching models (MINERVA2/SAM/REM) instead use
DIFFERENTIATION (single-pass weighted similarity sum, no settle-to-convergence) -> inherently less
basin-distorted (no positive-feedback pull toward the popular pattern). Cortical semantic system shows the
identical pathology: hub-and-spoke (Rogers/Lambon Ralph 2004) is an attractor over graded overlapping
code with an ATL hub; semantic dementia errors REGULARIZE toward prototypes ("coyote"->"dog") = hub-ward
attractor collapse when signal degrades. **Does the brain counter hub dominance for ranking?** DG pattern
separation is upstream PREVENTION (keeps HPC codes separable) — NOT available for the cortical store which
by design keeps correlated structure. CA1 comparator/novelty (Vinogradova 2001; J Neurosci 2007) = PINNED
match/mismatch — plausible substrate for novelty-weighted gain but its use to counter hub-bias-in-ranking
is INFERENCE. Repetition suppression / divisive normalization (Carandini & Heeger) / k-WTA = plausible
generic counter-pressure, INFERENCE for this role. **Important complicating evidence:** hippocampal replay
is BIASED TOWARD frequent/rewarded experiences (Current Biology 2019) — the brain does NOT correct
hub/frequency bias; if anything reinforces it. => the brain's actual fix looks ARCHITECTURAL ("route
ranking to a circuit that never settles to convergence") not a within-circuit de-bias. Weight this over
the normalization candidates.

**4. Manifold precondition — consistent with the brain; named resolution.** O'Reilly & McClelland 1994
(Hippocampus 4:661, "avoiding a tradeoff"): pattern separation (wants near-orthogonal decorrelated codes,
for capacity) and completion (wants overlapping correlated codes, so "nearby" states exist to fall into)
are in direct architectural TENSION; the trisynaptic solution routes "make separable" -> DG (feedforward
sparse expansion) and "make completable" -> CA3 recurrent matrix -> CA3 completion operates on CA3's own
(already-separated) code, recovering ONE specific trace from a corrupted cue of THAT trace, NOT
interpolating across the raw similarity of many items. Maps exactly onto the finding: completion over
i.i.d./orthogonal keys = nearest-neighbor cleanup of one target (CA3's real job) not manifold
interpolation; completion over correlated cortical code = hub-collapse. Grid-cell continuous attractor
(Nature 2021, toroidal manifold) = positive example of a genuine manifold-constrained attractor (path
integration, drift correction) — completion helps because there IS a real low-D manifold. Brain deploys
attractor dynamics differently by whether the code is structured-correlated (grid: manifold-exploiting) or
separated (CA3: single-target denoising).

**5. THE ROUTING RULE (decision procedure; synthesis = INFERENCE, each gate pinned).**
Route to CA3-style completion / iterative unbind-and-clean when ALL: (1) known slot/key structure ("what
filler bound to this known role"), not "how similar/typical" [BIC; associative-vs-item dissociation]; (2)
single discrete target on a pattern-SEPARATED substrate [O'Reilly & McClelland 94; grid contrast]; (3) cue
measurably incomplete relative to that one trace, gated in proportion to how much is missing [Nakazawa 02];
(4) low-ACh/retrieval mode (CA3-CA3 disinhibited) [Hasselmo]; (5) if superposed, decode SERIALLY with
suppression of already-recovered components, not settle to one blended attractor [Lisman & Idiart 95].
Route to direct/graded (familiarity) when ANY: (1) task is rank/typicality/similarity over many candidates
[dual-process; global-matching beats settling here]; (2) candidate codes graded/correlated by design
(settling -> hub collapse) [Rogers 04; mirror effect]; (3) SNR/margin already high (a full cue only risks
pulling a correct-but-unusual answer toward a generic neighbor) [Nakazawa generalized].
FALSIFIABLE load-bearing claim: cue completeness / query-structure (known key?) is the DOMINANT gate, and
hub-bias scales with how far you push settling on a graded/correlated code, not with store size. Predicts:
CA3-perturbation completion deficits appear specifically under partial-cue known-key retrieval and are
absent for pure similarity ranking; cortical hub-corruption gets WORSE as the query degrades; a real
biological joint-decode should be SERIAL/phase-separated, not simultaneous (else "joint decode" has no CA3
analogue and stays a computational-level device).

**TLDR.** (1) Two parallel systems, not a switch: HPC completion for one bound item via a known key;
cortical/perirhinal graded matching for similarity/familiarity — double-dissociated. (2) CA3 completion
gated ON by cue INCOMPLETENESS (Nakazawa) + ACh/theta phase (Hasselmo). (3) Completion helps with a single
discrete target + a real manifold (grid, CA3's own separated code); over random keys it degenerates to
nearest-neighbor cleanup. (4) Completion HURTS ranking over graded correlated codes (basin/hub bias) —
mirror effect + semantic-dementia collapse. (5) The brain's hub fix is ARCHITECTURAL (route ranking to a
non-settling circuit), not corrective — replay is biased TOWARD hubs. (6) For a superposed read the
grounded analogue is theta-gamma SERIAL decode-then-suppress (Lisman & Idiart 95), not "CA3 attractor";
resonator-as-CA3 stays an engineering analogy.

Sources: Nakazawa 2002 Science; Kumaran & McClelland 2012 REMERGE; Yonelinas 2022; Frady et al. 2020;
Hasselmo theta-phase; Bogacz & Brown perirhinal familiarity; WAS/mirror effect PMC1838560; Vinogradova
comparator; reward-biased replay Curr Biol 2019; grid toroidal attractor Nature 2021; Lisman & Idiart 1995
Science; hub-and-spoke (Rogers et al. 2004); BIC (Eichenbaum et al. 2007).
