---
problem: the_core_binding_operator_may_not_be_brain_faithful
status: SOLVED
bar: "On a binding-STRESS task -- multi-relation slot-filling recovered under interference AND relational retrieval under a PARTIAL role cue, on a held-out population with floors recomputed on it -- a brain-motivated binding operator (theta-gamma phase / conjunctive-mixed-selectivity / tensor-product, built as faithfully as the literature allows) must beat FHRR bind CI-separated over the strongest floor's UPPER bound, info-free twin LOSING, with CI half-width + null p95 reported."
result: "ThetaGamma (content-addressable temporal separation, Lisman-Jensen), EQUAL storage footprint, beats FHRR_percomp CI-separated on the partial-cue binding-stress task. Headline cell D=64(complex)/N=16 pairs/p=0.9 dropout: theta hit@1 = 0.1281 [0.1164, 0.1408] vs FHRR_percomp 0.0247 [0.0196, 0.0310]; scorer = FHRR cleanup-argmax hit@1; n = 2880 queries (3 seeds x 60 trials x 16 pairs); population = synthetic random-codebook key-value binding, |V|=256. Generalises: theta beats FHRR_percomp CI-separated in 29/54 grid cells = EVERY partial-cue (p=0.5, 0.9) cell at all D in {64,128,256}, plus all low-D interference cells."
floor: "Strongest info-free twin upper-95%CI = 0.0077 (random_memory/shuffled_key/bag_no_binding; chance = 1/256 = 0.0039). Theta headline 0.1164 (lower CI) clears it. Theta ALSO clears its own separation-specific floor (theta_blind_slot twin, ~1/N): REAL_ABOVE_BLIND in all tested cells, so the role->slot MATCHING carries information, not just clean storage."
controls: "(1) 3 info-free twins each EXCLUDE a leak: random_memory (excludes 'the memory carries value info without binding' -> <0.006), shuffled_key (excludes 'an unbound key still recovers' -> <0.008), bag_no_binding (excludes 'superposed values alone answer a role query' -> <0.008). (2) theta_blind_slot twin EXCLUDES 'clean per-slot storage is trivially correct' by replacing role-matching with a random slot pick (~1/N); real theta is CI-separated above it. (3) EQUAL storage footprint (2*D reals) EXCLUDES 'theta just has more memory'; the win holds at equal footprint. (4) FHRR_ca3_cleanup arm EXCLUDES 'a fancier terminal cleanup does it' -- routing the readback through the brain's real CA3 attractor (hdlab.iterative_attractor alpha=0.5) TIES argmax (0.0236 vs 0.0247). (5) GUARD: FHRR_percomp arm's superposition is asserted bit-equal to hdlab.bundling.bundle and single-pair unbind exact, so the baseline IS the live op."
files_changed: "experiments/exp_binding_operator_stress_v1.py, verification/verify_binding_operator_stress.py, notes/problems/the_core_binding_operator_may_not_be_brain_faithful/DESIGN_brain_analysis.md, notes/problems/the_core_binding_operator_may_not_be_brain_faithful/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/verify_binding_operator_stress.py"
---

# The bind OPERATOR is validated; the deviation is the RETRIEVAL ARCHITECTURE built on it

## Headline in plain language

Our most central operation ties a role to a filler ("agent -> dog") with a specific piece of vector
math (FHRR complex multiply). The worry was that this piece of math might be subtly wrong because the
brain's binding equation is unknown. **The math itself is fine** -- when I hold storage equal and pit
it against the two brain theories that CAN be written as an equation (tensor-product and conjunctive
product), our compressed version WINS. It is an efficient choice, not a lazy one.

**The real problem is one level up.** Our substrate crams many role-filler pairs into ONE vector and
"un-mixes" them on demand. The brain does not do this. It keeps things SEPARATE (a small set of
slots) and finds the one you asked for by MATCHING your cue against what is stored -- so a partial or
noisy cue still works. When I built that brain mechanism and stressed both with a degraded cue, the
brain-style mechanism recovered the right filler **five times more often** than our current math, and
the gap is statistically clean. Crucially, the substrate ALREADY has the parts for this (a banked
store, a pattern-completer) -- but it wires them in a way that throws the advantage away.

## What I built

`experiments/exp_binding_operator_stress_v1.py` -- a binding-STRESS instrument: a key-value
associative memory (the canonical role-filler binding). N distinct random role-keys, N filler values
from a |V|=256 codebook, all superposed into one memory; query a role (EXACT or a component-dropout
PARTIAL cue) and recover its filler by cleanup-argmax. Swept: dimensionality D in {64,128,256}
(footprint 2*D reals, matched across arms), interference N in {2..64} pairs, partial-cue dropout p in
{0, 0.5, 0.9}, 3 seeds x 80 trials. The FHRR arm IMPORTS the real hdlab ops (binding.bind/unbind,
bundling.bundle) and a guard asserts it is bit-equal to the live op.

**Arms (all at EQUAL storage footprint):** FHRR_percomp (the live op), FHRR_L2 / FHRR_rawsum
(normaliser ablations of the SAME operator), HRR (real circular convolution), TPR (Smolensky /
Whittington TEM outer product), TPR_sparse (Rigotti-Fusi mixed-selectivity), ThetaGamma (Lisman-Jensen
temporal slot separation), MultiBankHash8 (a faithful model of the LIVE hdlab.situation_model_multibank),
FHRR_ca3_cleanup (FHRR readback settled by the brain's real CA3 attractor). Info-free twins:
random_memory, shuffled_key, bag_no_binding, theta_blind_slot.

## What I measured (all CI'd; reverify = the witness above)

1. **The bind OPERATOR is validated at equal storage.** At exact cue, no uncompressed brain operator
   beats FHRR. D=256/N=32/p0: FHRR 0.754, HRR 0.853, TPR 0.740, theta 0.219. TPR (tensor-product /
   conjunctive product) LOSES to FHRR in every exact-cue cell -- compression is more storage-efficient
   than the full outer product. (HRR, a real-valued VSA sibling, edges FHRR in several cells -- a
   VSA-internal note, not a brain-motivated win.)

2. **HEADLINE -- a brain-motivated operator beats FHRR under the PARTIAL cue, CI-separated, at equal
   storage.** ThetaGamma (content-addressable temporal separation) beats FHRR_percomp in 29/54 cells:
   EVERY partial-cue cell (p=0.5, 0.9) at all three D, plus all low-D interference cells. Headline
   D=64/N=16/p=0.9: theta 0.1281 [0.1164, 0.1408] vs FHRR 0.0247 [0.0196, 0.0310] (CI half-widths
   0.0122 / 0.0057; null p95 = strongest twin upper CI 0.0077). At the tempbonus storage regime the
   gap is larger (0.379 vs 0.025). Info-free twins all < 0.008. The mechanism is brain-faithful and
   PRECISELY predicted: a partial cue only has to SELECT the slot (1-of-7), not RECONSTRUCT the filler
   from a dense superposition -- which is exactly the CA3 partial-cue dissociation (CA3-NMDAR knockouts
   retrieve from full cues, fail selectively from partial ones; Nakazawa 2002).

3. **The per-component normaliser is the wrong op for binding too.** FHRR_L2 and FHRR_rawsum each beat
   FHRR_percomp in 32 grid cells; FHRR_percomp beats them in ZERO. E.g. D=64/N=16/p0: percomp 0.400
   [0.376,0.420] vs L2 0.533. This extends audit E1's "the additive SUM is faithful, only the
   per-component normaliser is not" (measured there as 20-32% of d' on feature bundling) to a NEW,
   directly-relevant task: role-filler recovery under interference.

4. **The gain is ARCHITECTURAL, not a fancier terminal cleanup (informative negative).** Routing the
   FHRR readback through the brain's own CA3 attractor completion (hdlab.iterative_attractor,
   alpha=0.5 = brain-canonical) TIES one-shot argmax (0.0236 vs 0.0247). For a single noisy readback
   vs a near-orthogonal codebook, argmax is already the MAP estimate. **You cannot clean your way out
   of superposition crosstalk; you have to not superpose.** This is a load-bearing negative: it says
   the fix is the storage architecture, NOT bolting an attractor onto the flat read.

5. **The LIVE substrate sits between flat-FHRR and the brain, and its exact weakness is identifiable.**
   MultiBankHash8 (a faithful model of hdlab.situation_model_multibank) HUGELY beats flat FHRR at
   exact cue (D=64/N=16/p0: 1.000 vs 0.397) -- **banking/separation is the right instinct and it is
   already in the substrate.** But under the partial cue, content-addressable theta beats hash-routed
   multibank CI-separated (0.379 [0.357,0.401] vs 0.199 [0.182,0.217]) EVEN THOUGH the hash router is
   generously handed exact-identity routing. The multibank's own docstring states the flaw: routing is
   "a deterministic hash lookup ... routing accuracy is 1.0 by construction" -- it assumes the key is
   known EXACTLY, so it has no graceful-degradation path for a partial cue. The brain routes by
   content-addressable matching (Lewis & Vasishth 2005; audit E3 pins this for coreference).

## What would change in hdlab (proposed; the strategy session lands it, Q111)

Ranked by evidence strength and safety. **I am NOT proposing to replace the bind operator** -- it is
validated. The changes are to the superposition normaliser and the retrieval architecture.

- **A (small, safe, strongly evidenced): the superposition normaliser.** `hdlab/bundling.py:36-39`
  renormalises each complex component to the unit torus (`out = s / s.abs()`). L2 / raw-sum beat it in
  32/32 decisive cells and it wins none. PROPOSED: add a `norm="l2"` option to `bundle()` for the
  complex branch (whole-vector L2). **COUPLING TO FLAG (do not miss):** `hdlab/atoms.py:similarity`
  computes FHRR similarity as `(a*conj(b)).sum().real / n`, which assumes per-component unit magnitude
  (`||v||=sqrt(n)`). If the bundle is L2-normalised (`||v||=1`), the readout must divide by the actual
  norms (a true cosine), or the cleanup scores are miscalibrated. So this is a two-line change in TWO
  files, landed together -- exactly why it needs the owner's care, not a solo edit. Default-OFF flag
  first; measure on the live reading task before flipping (an isolation win is not a capability).

- **B (the real lever, architectural): give the separated store a CONTENT-ADDRESSABLE retrieval path.**
  `hdlab/situation_model_multibank.py` separates (good) but routes by `stable_bank_id(hash(event_idx))`,
  which requires the exact key and dies on a partial cue. The brain-faithful retrieval is
  content-addressable (match the -- possibly partial -- cue against stored slot tags, then complete).
  The substrate ALREADY OWNS this: `hdlab/ca3_completer.py` (`complete_addressed`: unbind by key ->
  settle each spoke via `iterative_attractor` -> rebuild) is exactly it, and is DEFAULT-OFF. PROPOSED
  DIRECTION: on `decode()` with a degraded/partial cue, route through `ca3_completer` /
  content-addressable slot matching instead of the hash lookup. This is a capability addition, not a
  one-liner, and it is where the 5x partial-cue gain lives. Pair it with DG pattern separation
  (`hdlab/dg_pattern_separation.py`, also owned) for overlapping cues -- the DG->CA3 matched pair.

- **C (a guard, from the negative in finding 4): do NOT expect a terminal attractor cleanup on the
  flat readback to help.** It ties argmax. Any future "add Hopfield/attractor cleanup to the read"
  proposal should be gated on operating over a SEPARATED store, or it will move nothing.

## KEY REALIZATIONS (the enabling moves)

- **Reframed the question from the OPERATOR to the ARCHITECTURE.** The brief asked "is the bind
  operator wrong". The disk's own reframe (audit E1: "the additive SUM is faithful, only the
  normaliser is not") plus the fact that FHRR is a compressed tensor product told me the multiply is
  fine; the deviation had to be downstream. That is what let separation win where operator-swaps could
  not.
- **Stressed the RIGHT regime.** At D=1024 every scheme scores 1.000 and nothing is learnable (the
  brief's explicit warning). Dropping to low D + heavy interference + a degraded cue -- which is ALSO
  the more brain-faithful regime (cortex is low-dim) -- is what made the operators diverge.
- **Let the biology name the discriminating variable.** Lisman-Jensen and Nakazawa's CA3 dissociation
  both say the payoff of separation + content-addressing is specifically PARTIAL-cue robustness. So I
  built the partial cue, and that is exactly the cell where the brain mechanism wins. The win was
  predicted by the neuroscience, not found by sweeping.
- **The informative negative (CA3 cleanup ties argmax) was as valuable as the win.** It killed the
  tempting-but-wrong fix ("clean up harder") and pointed all the way back to the storage architecture.
- **Building the info-free twin for the WINNING arm (theta_blind_slot) defended the win** against the
  obvious "clean slots make cleanup trivial" objection -- the role->slot match is CI-separated above a
  random-slot pick, so the binding is doing the work.

## What I did NOT establish (and would withdraw first if wrong)

- **This is a synthetic-algebra construction proof, not a downstream comprehension win.** It shows the
  binding OPERATION recovers better under stress with a brain-faithful architecture; it does NOT show
  that wiring this lifts the real reading/QA numbers. This project's standing lesson is that an
  isolation win is not a capability -- so the FIRST thing I would withdraw is any implication that
  changes A/B move a downstream metric. They must be measured on the live task before that is claimed.
- **The theta win is regime-specific.** Under an EXACT cue with adequate D, FHRR (and especially the
  banked multibank) WINS -- theta has a hard ~7-item capacity cliff. So "theta beats FHRR" is true
  ONLY in the partial-cue / low-D-interference regime, which is the stress regime the task targets. I
  present it as a regime result, not a blanket replacement.
- **My roles are random and near-orthogonal.** The brain's retrieval interference (the fan effect)
  needs FEATURE-OVERLAPPING cues to show, which I did not build; DG pattern separation would matter
  there and I did not test it (it is a no-op on orthogonal keys). So the "DG->CA3 pairing" in
  recommendation B is motivated but not yet measured here -- a clean next experiment.
- **Partial cue = component dropout.** Other partial-cue models (additive noise, candidate-role
  superposition) may behave differently; I tested dropout.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, E1 / TIER 3)

E1's verdict UNSCORABLE is correct for the algebraic bind, but the entry can be SHARPENED, and one
line should move:

1. **The E1 deviation is mis-located.** The entry frames binding as "the deepest deviation ... our
   central operation has no settled brain equation." Measured: at equal storage the bind OPERATOR
   (compressed TPR) BEATS the two writable brain hypotheses (tensor-product, conjunctive) -- it is
   efficient, not a liability. The real E1/E2 deviation is the **superposition-and-unbind RETRIEVAL**:
   the brain SEPARATES and retrieves CONTENT-ADDRESSABLY, and a faithful version of that beats FHRR
   CI-separated under a partial cue (5x). Suggest re-tagging E1 from "UNSCORABLE, deepest deviation"
   to "operator VALIDATED at equal storage; deviation is the flat-superposition retrieval, shared with
   E2/E3."
2. **E1's normaliser note now has a second, task-relevant datapoint.** The "additive SUM faithful,
   per-component normaliser not" claim (20-32% d' on feature bundling) reproduces on binding recovery:
   L2/raw-sum beat per-component in 32/32 decisive cells, percomp wins none.
3. **E2 confirmed and made actionable.** "multibank routes by deterministic hash, not a noisy-cue
   argmax" is exactly the flaw: it has no partial-cue path. Content-addressable routing (ca3_completer,
   DEFAULT-OFF) is the owned fix; its value is realised only over the SEPARATED store (CA3 cleanup on a
   flat readback ties argmax).
4. **This unifies E1/E2/E3 under one brain mechanism:** cue-based content-addressable retrieval with
   similarity interference (Lewis & Vasishth 2005; McElree; Nakazawa 2002). E3 already pins it for
   coreference; it is the SAME mechanism binding-recovery needs.

---

## TLDR
Our core "tie a role to a filler" math is fine -- when storage is held equal it beats the brain
theories you can actually write as an equation. The thing that is NOT brain-like is that we mix many
ties into one vector and un-mix them on demand; the brain keeps them separate and finds the one you
asked for by matching your cue, so a partial or noisy cue still works. Built the brain version and
stressed both with a degraded cue: the brain version got the right answer ~5x more often, cleanly. We
already own the parts for this (a banked store, a pattern-completer) but wire them so the advantage is
lost. Also: one normalisation step we apply after mixing only ever hurt, never helped. And a tempting
"just clean up the answer harder" fix does nothing -- the win has to come from not mixing in the first
place.

## QUESTIONS
None -- the result is decisive and the recommendations are scoped. One judgement call for the owner:
recommendation A (the normaliser) is small and safe but touches the shared similarity/cleanup path in
two files at once, so it wants the owner's hand, not a solo land.

## NEXT STEPS
1. Land recommendation A behind a default-OFF flag (bundling L2 + the coupled cosine readout) and
   measure it on the LIVE reading task, not in isolation.
2. Prototype recommendation B: a content-addressable (ca3_completer) retrieval path for the multibank
   register under partial/unknown cues; measure vs the hash route on the real situation-model task
   (E2's LOCALIZED_WALL cell is the natural harness).
3. Run the missing finer experiment: overlapping (feature-correlated) role cues to elicit the fan
   effect, and test whether the owned DG->CA3 pair mitigates the interference as the brain predicts.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT. Re-verified scaffold-free (verify_binding_operator_stress.py PASS: guard FHRR==live bundle; twins <0.008; theta 0.1281 vs FHRR 0.0247 CI-sep; CA3 cleanup TIES argmax; percomp 0.4003 < L2 0.5330; content-addr theta 0.3865 > hash multibank 0.1965). A model of the strengthened protocol: refuted the surface question (the bind OPERATOR is validated -- beats the writable brain theories TPR/conjunctive at equal storage), went deeper, and located the REAL deviation = flat-superposition RETRIEVAL (brain separates + retrieves content-addressably; ~5x under partial cue). Load-bearing negative: CA3 cleanup on a flat read ties argmax (fix is storage architecture, not terminal cleanup). Honestly scoped as a synthetic construction proof, not a downstream win. Review in PROBLEM.md; priority cleared. AUDIT UPDATE folded into BRAIN_FOUNDATIONAL_AUDIT.md (E1 re-located: operator validated, deviation is retrieval; unifies E1/E2/E3). hdlab Rec A (bundling L2 + coupled cosine, default-off) to land carefully; Rec B (content-addressable retrieval, the real lever) recorded as the proven-ready direction. Committed (no push).
