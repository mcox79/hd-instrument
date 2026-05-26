# META request to Strategy — 2026-05-21 14:55 (user-directed)

**Sender**: META session (session 6)
**Recipient**: Strategy session (session 1)
**Topic**: User-directed expansion of substrate engineering candidates from condensed-matter analogs

## What I'm asking

User explicitly asked META to add these to research and the pipeline
after a conversation about (a) how electrons travel through crystals,
(b) superconductivity / Cooper pairs, and (c) other physical mechanisms
that achieve robust transport / correlation across distances.

The conversation produced six candidate substrate-engineering directions
that map onto the substrate's current multi-hop architectural cliff at
d≈25 (cycle 11). Three are buildable experiments, three are research
directions; one (soft cleanup) is cheap enough that it could be a
buildable experiment in a single cycle.

You decide priority and which become bets vs research-only.

## The six candidates

### 1. Soft cleanup (photosynthesis / ENAQT analog) — HIGHEST LEVERAGE, CHEAPEST

**What**: replace `argmax` cleanup with `softmax` (or top-k weighted)
so that multi-hop propagates partial-coherence over candidate states
instead of fully collapsing at each hop.

**Substrate-level claim**: current substrate's argmax collapse at each
cleanup destroys usable information about runner-up candidates. Soft
cleanup keeps the runner-ups weighted and lets the next hop's binding
prune via interference — analogous to environment-assisted quantum
transport (ENAQT) in photosynthesis, where partial coherence between
chromophores yields ~95% transport efficiency across ~50 sites where
classical hopping would give much less.

**Why this matters for multi-hop**: directly tests whether the d≈25
cliff is from argmax collapse or from a deeper noise budget. If soft
cleanup substantially improves d=50 accuracy, the d≈25 cliff was an
implementation artifact (collapse choice), not architectural. If it
doesn't help, the cliff is genuinely architectural.

**Buildability**: 1 cycle. Replace cleanup step with softmax(N·cos/τ)
weighted top-k propagation; sweep τ ∈ {0.5, 1.0, 2.0, 4.0}; multi-probe
against existing FHRR/Modern-Hopfield baselines.

**Multi-probe success criteria** (suggestion):
- acc_50hop ≥ 0.50 at NUM_FACTS=100 (vs FHRR's 0.22, BSC's 0.011)
- monotone gain over τ sweep (rules out collapse-only artifact)
- 3 seeds
- compute cost ≤ 2× baseline (softmax shouldn't add much)

**Kill criterion**: acc_50hop ≤ FHRR (0.22). If soft cleanup doesn't
beat full-coherence binding-algebra swap, partial-coherence isn't the
right axis.

**Materials analog (load-bearing)**: ENAQT in light-harvesting
complexes; quantum walks vs classical random walks (quadratic
position-spread advantage); environment-assisted transport theorem
(Plenio-Huelga, Caruso-Rebentrost).

### 2. Cooper-pair encoding (superconductivity analog) — MEDIUM BUILDABILITY

**What**: store each fact F not as one bundle `e = subj * rel * obj`
but as a pair `(e_1, e_2)` where `e_1 = e * twist_1` and
`e_2 = e * twist_2` for independent random twists. Cleanup at each hop
recovers both and only succeeds if their cosine overlap exceeds a gap
threshold Δ_subst. Noise that breaks one member but not both is
corrected; noise that breaks both equally is rare.

**Substrate-level claim**: BCS gap protection translated to error-
correcting redundancy. Per-hop noise below the gap is structurally
suppressed instead of accumulating.

**Buildability**: 1-2 cycles. Doubles storage cost per fact (acceptable
at current M/N ≤ 8 envelope); cleanup gets a consistency check step.
Multi-probe: pair-recovery accuracy at d=50 vs single-bundle baseline.

**Materials analog**: BCS superconductivity (Bardeen-Cooper-Schrieffer
1957); gap-protected transport; pair-correlation function.

### 3. Holographic / HaPPY error correction codes — RESEARCH-FIRST

**What**: encode each fact as a redundant pattern across multiple
bundles using a tensor-network code structure (HaPPY pentagon code, or
simpler variants). The logical fact = code parameter; physical bundles
= redundant carriers. Erasing any small region of physical bundles
doesn't lose the logical fact.

**Substrate-level claim**: holographic codes give explicit quantitative
error-correction thresholds. Below threshold per-bundle noise is
corrected; above it, the code fails. This is the only mechanism in
the list that gives DIRECT analytic predictions for noise-vs-depth
behavior.

**Buildability**: research first. Needs to verify (a) which HaPPY-class
codes are tractable at substrate dim (N=4096), (b) what the threshold
prediction is, (c) cleanup operator design.

**Routing**: Research R-question (new — call it R30 or similar).
Possibly bet-able after Research delivers the tractable construction.

**Materials analog**: AdS/CFT holography; quantum error correction
codes; tensor networks.

### 4. Soliton attractor design — MEDIUM-HARD

**What**: design cleanup dynamics so that stored facts are soliton-
shaped attractors — localized, shape-preserving under iterated cleanup.
Multi-hop becomes soliton-soliton interaction that preserves shape
across many collisions.

**Substrate-level claim**: nonlinear cleanup balances dispersion;
soliton-shaped facts survive arbitrarily many cleanup steps because
the nonlinearity exactly compensates the noise. Optical solitons
maintain pulse shape across 6,000 km of fiber.

**Buildability**: medium-hard. Substrate already has attractor
dynamics (basins of attraction in vector space). Soliton design = tune
basin shape to be stable under the binding operator. Needs careful
prereg work.

**Materials analog**: optical solitons in fibers (Mollenauer 1980);
Davydov solitons in proteins; nonlinear Schrödinger equation
solutions.

### 5. Magnon / spin-wave substrate (connects to R29) — RESEARCH-LED

**What**: encode facts as rotational patterns in a collective bundle
space rather than as fixed bundles. Multi-hop = propagation of the
rotational pattern through the bundle space. Connects directly to R29
ferromagnetism / magnetic domains (just landed).

**Substrate-level claim**: spin waves in magnetic materials propagate
centimeters in YIG at room temperature with low loss; carry
information without net particle transport. The substrate analog would
be a fact representation that doesn't degrade through repeated cleanup
because the propagation is wave-like, not hopping-like.

**Buildability**: needs R29 integration first. Research route.
Promising because it gives PHYSICAL interpretation to "propagating a
fact" rather than computational interpretation.

**Routing**: Research R-question (new — extends R29 directly).

**Materials analog**: magnonics; YIG magnon devices; spin-wave
propagation; skyrmion bit-carriers.

### 6. Topological protection beyond SSH (Bet F generalization) — HARD

**What**: encode facts in higher-dimensional topological invariants
(2D Chern numbers, 3D linking numbers, symmetry-protected topological
phases like AKLT). Information stored in topological "charge" can't
change under any smooth deformation; local cleanup noise can't change
the invariant.

**Substrate-level claim**: Bet F (SSH-BSC v2, currently blocked on
R10 addendum) is the 1D version. Higher-dim topology gives more
capacity but harder cleanup design.

**Buildability**: hard. Bet F's R10 addendum process needs to settle
first; THEN consider higher-dim extensions.

**Routing**: research-first AFTER Bet F resolves. No urgency.

**Materials analog**: quantum Hall edge states; Majorana fermion pairs;
SPT phases; topological insulators.

### 7. Quantum-repeater architecture (entanglement-swapping analog) — RESEARCH-FIRST → BUILDABLE, HIGHEST LEVERAGE OF RESEARCH-FIRST TIER

Added 2026-05-21 cycle 11 followup #2 after user prompted "I also
can't help but think of quantum entanglement."

**What**: encode facts in non-factorable joint states of bundle pairs
(classical Bell-state-like correlations between pairs of vectors).
Split long multi-hop chains into segments of K hops each. Between
segments, run a **purification operator** that takes M noisy joint
encodings of the same logical fact and produces 1 cleaner joint
encoding (sacrificing M-1 for 1). Continue swapping.

**Substrate-level claim**: the substrate's d≈25 cliff is structurally
the exponential-decay regime of unrepeated quantum communication.
Substrate's existing cleanup IS a noisy entanglement-swap operator.
Adding periodic purification between segments converts exponential
decay into polynomial — substrate could chain to d=50, d=100, d=500
with fidelity that falls only polynomially in N. This is the only
candidate on the list that gives *qualitatively different* asymptotic
behavior (poly vs exp), not just better constants.

**Distinct from Cooper pairs (#2)**: Cooper pairs improve per-hop
fidelity through gap protection — local, single-step. Quantum repeater
adds a recovery step between groups of hops — global, periodic. The
two could combine: Cooper-paired encoding per node + purification
between segments = strongest version.

**Distinct from holographic codes (#3)**: HaPPY codes give *spatial*
error correction (erase a region, recover from the rest). Quantum
repeater gives *temporal* error correction (compound noise over many
steps, purify periodically). Different axes; can stack.

**Buildability**: research-first to specify the classical purification
operator (the load-bearing piece). Once specified, the
swap-segment-purify architecture is straightforward. 1-2 build cycles
after Research delivers the operator.

**Multi-probe success criteria**:
- acc_50hop ≥ 0.70 at NUM_FACTS=100 with K=5 segments × M=3
  purification rounds (vs FHRR 0.22, BSC 0.011)
- monotone improvement as M increases (rules out "purification is
  just averaging")
- scaling at d=100, d=200 is **polynomial in chain length, not
  exponential** — the decisive test that distinguishes architectural
  improvement from local fidelity gain
- 3 seeds minimum

**Kill criterion**: at d=100, acc doesn't beat the best single-hop
substrate by more than 2× — means purification isn't doing structural
work, just smoothing.

**Honest caveat**: the substrate is classical. There's no actual
quantum entanglement, no Bell measurements, no monogamy. What's
transferable is the **architecture** — non-factorable joint encoding,
chain segmentation, periodic purification. The math of classical
purification (redundant majority-vote codes and their generalizations)
is well-established and works classically. The structural insight
from quantum networks is that you should INSERT purification steps
between groups of hops, not just improve individual hops.

**Materials / physics anchor**: Bell 1964 (non-factorability); BBPS
1996 (distillation, arXiv:quant-ph/9511027); Zukowski-Zeilinger 1993
(entanglement swapping); Briegel-Dür-Cirac-Zoller 1998 (quantum
repeaters, the foundational paper); Sangouard-Simon-de Riedmatten-
Gisin 2011 (Rev. Mod. Phys. review of practical quantum repeaters).

## Suggested priority order (revised after candidate #7 added)

1. **Build immediately (1 cycle)**: Soft cleanup (#1). Highest-
   leverage, cheapest test of whether multi-hop's d≈25 cliff is
   collapse-artifact or architectural.
2. **Build next cycle (1-2 cycles)**: Cooper-pair encoding (#2).
   Tests gap-protected per-hop redundancy.
3. **Research new R (highest-leverage research-first)**: Quantum-
   repeater architecture (#7). The only candidate that promises
   poly-vs-exp asymptotic improvement, not just better constants.
   If feasible, single biggest move on the list.
4. **Research new R**: Holographic / HaPPY codes (#3). Spatial error
   correction; orthogonal to #7's temporal error correction; could
   stack.
5. **Research new R**: Magnon / spin-wave substrate (#5). Extends R29.
6. **Research / design** (longer): Soliton attractor (#4).
7. **Defer**: Topological extensions (#6) until Bet F resolves.

If multi-hop d=50 PASS is feasible at all in current arch, items 1 or
2 likely show it. If both fail, the d≈25 cliff is genuinely
architectural and item 3 (#7 quantum repeater) becomes the
load-bearing path forward — convert exponential decay into polynomial
via segment-and-purify architecture. Items 4-6 are alternative
architectural redesigns if 3 is also infeasible.

## Cross-references

- META cycle 11 audit + cycle 7 PROT-005 filing
- User conversation 2026-05-21 14:50-15:00 (crystals → superconductivity
  → broader analogs → quantum entanglement)
- R29 ferromagnetism (landed 14:38)
- Bet F R10 addendum still pending (Experiment Dev request to Research)
- Multi-hop architectural-closure pending after adaptive-beta verdict

## Revision history

- 2026-05-21 14:55 — initial filing with candidates 1-6.
- 2026-05-21 15:00 — added candidate 7 (quantum-repeater
  architecture) after user prompted; updated priority order. The
  research-first tier now has 4 items with #7 (quantum repeater)
  promoted to top of that tier because of its poly-vs-exp asymptotic
  promise.

## What you need from me

Nothing. Substrate-level claims, multi-probe sketches, and material-
science framings are in the candidate descriptions. You decide which
become Bets vs R-questions vs deferrals.

— META session
