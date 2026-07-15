# Research: three brain mechanisms for asymmetric/directed-relation encoding — head-to-head vs role-keying

**Filed by:** research sub-agent. **Trigger:** `exp_interaction_bilinear_wall_break_v1` (commit 29b53e63b) landed
`HARD_FAIL_BILINEAR_IS_ANOTHER_SPECIALIST_PARITY_ONLY` (confirmed off-disk, `data/exp_interaction_bilinear_wall_break_v1/metrics.json`):
PARITY solved (HERO_R1=0.978 vs SYM specialist=0.992, parity_ok=True) but DOMINANCE not solved (HERO_R1=0.485 vs
role-keyed specialist=1.000, vs SYM=0.477 — **HERO_R1 and SYM differ by only +0.008, i.e. the learned bilinear op
converged back to the symmetric specialist and gained nothing on dominance**, `hero_minus_sym_dom=0.008`,
`ties_elementwise=True`). Mechanistic reason (below) is structural, not a tuning failure: a per-role LOW-RANK
correction to each factor still gets folded by a **commutative Hadamard product across all K factors** — no matter
how the individual factors are transformed beforehand, `a⊙b⊙c⊙d` is order-blind by construction. Relabeling factors
before an order-blind combination cannot inject order-sensitivity. Per standing rule (negative -> brain-check -> if
the brain solves it differently, the brain's mechanism is the fix), this note brain-grounds and head-to-head designs
THREE theorized brain mechanisms for directed relations, each mapped to a distinct substrate operator that changes
**where** order-sensitivity is injected (not just re-parameterizing the same order-blind fold).

**Method:** 3 parallel Sonnet lit-scan sub-agents (transition/successor dynamics; heteroassociative Hebbian
outer-product asymmetry; theta-gamma phase-order coding), generic neuro/math search terms only, no substrate-novel
framing sent off-platform. Synthesized against 2 same-week prior drills already on file
(`drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md`,
`drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md`) which had already surfaced TEM
non-commutative transition matrices, TPR/outer-product binding, and oscillatory phase coding as contested,
non-reconciled accounts of "where asymmetry lives" — this note is the targeted follow-up that actually builds and
head-to-head tests the three candidates rather than leaving them as a ranked shortlist.

---

## HEADLINE

**Mechanistic diagnosis of the bilinear negative:** the failed op's final composition step is a commutative
Hadamard product over K factors; per-factor low-rank corrections cannot make a commutative combination
order-sensitive. The three brain mechanisms differ in **where** they'd inject order-sensitivity relative to this
failure point:

1. **Transition/successor dynamics** injects order-sensitivity **in the composition operator itself**
   (sequential non-commutative matrix application, `M_i @ (...)`, chained — `AB != BA` by construction). This is
   the mechanistically closest fix to the diagnosed flaw and the **best-grounded candidate** (direct, well-replicated
   biology: TEM's `W_a` matrices, PubMed-verified grid-cell path-integration group-representation theorem).
2. **Heteroassociative Hebbian asymmetry** injects order-sensitivity **in the memory-write step** (`W = sum b_i
   a_i^T`, forward `Wa~b` vs backward `W^T b` genuinely different maps) — well-grounded for the *mechanism* of
   asymmetry, but the literature is unusually explicit and convergent that this specific mechanism is a
   **lookup/storage** device, not a relation-generalization device: it is expected to memorize seen pairs and
   **not** transfer to novel pairs, which is the arena's core discriminator (SEEN vs NOVEL).
3. **Theta phase precession** injects order-sensitivity **in the readout of relative phase** — this is the
   **weakest-grounded candidate**, and this cycle's lit-scan surfaced a direct, recent (2025), well-powered
   refutation (Liebe et al., *Nat Neurosci*, human single-unit) of the core claim that phase order tracks item
   order at the population level. There is also a hard structural objection: FHRR's complex-multiply bind is
   itself **commutative** (`z1*z2 = z2*z1` for complex numbers), so any order-sensitivity from a phase-tagged
   design must come from a *fixed per-role phase offset acting as a role-tag*, not from the bind becoming
   non-commutative — i.e. if it works at all, the honest interpretation is "phase dressing of a role-tag," not
   "phase precession discovered order from an otherwise-symmetric bind." Flagged as the highest mis-mapping-risk
   candidate; still worth a cheap test with a control ablation to attribute any win correctly.

**Bottom line:** the three mechanisms are NOT equally promising. Transition/successor dynamics is favored to beat
role-keying or at minimum match it while pointing at a real architectural fix; heteroassociative asymmetry is
expected to reproduce the ROLE_KEY-vs-BILINEAR tension in a *new, cleanly diagnostic* form (a hard SEEN/NOVEL split,
not a soft failure); phase-order is the long shot, run mainly to close the loop and because it is cheap given the
substrate's native FHRR complex path.

---

## (1) Transition / successor dynamics

### (a) Biology (lead)

- **Tolman-Eichenbaum Machine** (Whittington, Muller, Mark, Chen, Barry, Burgess & Behrens, 2020, *Cell* 183:1249-1263
  — secondary-sourced this cycle, paywalled primary PDF, but corroborated via abstract + independent secondary
  summaries across two research cycles now): each relation/action `a` has its **own learned matrix operator**
  `W_a`, applied to a structural/grid-like code `g`: `g_{t+1} = f(W_a, g_t)`. Composing different relations in
  different orders yields genuinely different codes — non-commutativity is a **designed requirement** for correct
  relational generalization (the "uncle = father-then-brother, not brother-then-father" example), not an incidental
  property.
- **Hippocampal successor representation** (Dayan 1993, *Neural Computation*; Stachenfeld, Botvinick & Gershman
  2017, *Nat. Neurosci.* — both independently verified via abstract/PDF): `M = (I - gamma*T)^-1` is a resolvent over
  the transition matrix `T`, giving expected discounted future occupancy. **Important negative finding from this
  cycle's lit-scan: no paper frames the SR matrix (or single-step `T`) as a general single-relation bind operator
  ("bind(A, relation) -> B") analogous to a rotation/permutation** — SR's published role is multi-step occupancy
  prediction, not pairwise relation encoding. This is a genuine literature gap, not a confirmed transfer; treat SR
  itself as a *weaker* direct precedent for THIS use (single relation-instance encoding) than TEM's `W_a`, even
  though the two are adjacent (both non-commutative operators on a structural code) and were the substrate of a
  prior research note in a *different* use case (`research_successor_representation_reachability_autonomous_traversal_2026-07-09.md`,
  goal-conditioned multi-hop traversal — not directly transferable to this note's single-pair-relation-encoding
  question, flagged so the two are not conflated).
- **Grid-cell path integration as a rotation/matrix-group operator** — the cleanest, most rigorously confirmed
  math bridge found this cycle: Burak & Fiete (2009, *PLoS Comp. Biol.*, verified via arXiv/lab PDF) show
  velocity/heading inputs act as rotation-like transforms on the attractor manifold; Gao, Xie, Zhu et al. (NeurIPS
  2021, arXiv:2006.10259, verified via abstract) **prove** a group-representation condition is necessary for path
  integration and that the simplest solution is literally a matrix Lie group of rotations. This is a name-brand,
  proven (not just observed) non-commutative-by-construction result — the strongest single citation in this whole
  note.
- **Existing substrate precedent** (per the July 14 drills' cross-thread synthesis): GHRR matrix-vector bind
  (non-commutative, `M_R . a` is directed) is **already validated on this substrate** (June 2026 pilot). This
  candidate is therefore closer to a **direct precedent transfer** of an already-proven mechanism into this specific
  dominance/parity arena than a from-scratch novel synthesis.

### (b) Best substrate operator + why

**`TRANSITION_OP`**: shared per-value embedding table `e[l]` (same style as `LEARN_SYM`'s shared code — NOT
role-keyed at the embedding level), plus **K learned full-rank D×D matrices `M_0..M_{K-1}`** (one per slot/role,
NOT regularized toward identity, NOT low-rank — genuinely free parameters; a small weight-decay for numerical
stability only). Composition is **sequential, not a simultaneous product-fold**:

```
s_0 = e[x_0]
s_i = M_i @ (s_{i-1} (*) e[x_i])   for i = 1..K-1     ((*) = elementwise Hadamard)
z = s_{K-1}
```

then a learned linear readout head on `z`, same capacity class as every other learned arm. This directly generalizes
TEM's `g_{t+1} = f(W_a, g_t)` (state carried forward, transformed by a per-step matrix) and is the mechanistically
correct fix for the diagnosed bilinear flaw: **the composition step itself is now non-commutative** (`M_1(M_2(...))
!= M_2(M_1(...))` in general), not just the per-factor content.

### (c) Prediction

Expect `TRANSITION_OP` to **beat** `LEARN_BILINEAR_RANK1` on dominance by a wide margin (the mechanism directly
targets the diagnosed flaw) and to be **competitive with or exceed role-keying** (`ROLE_KEYED = max(LEARN_INT,
LEARN_ADD)`) on NOVEL dominance, since it is not restricted to per-role additive/multiplicative composition the way
role-keyed embeddings are — it can in principle express strictly richer order-sensitive functions. Whether it
**beats** role-keying (not just matches) would be a genuine surprise worth extra scrutiny (role-keying is already at
the ceiling on this arena, 1.000). The more likely, still-valuable outcome is TRANSITION_OP matches role-keying
within tolerance while ALSO being close to LEARN_SYM on parity (the "does it also preserve parity" bonus) — no
strong guarantee here since the mechanism is now explicitly order-sensitive by construction; parity would require
the learned `M_i` to converge toward mutually-commuting (near-identity-like) matrices specifically for the
parity-family data, which is possible but not guaranteed by the architecture.

### (d) Failure modes / non-result conditions

- If `M_i` converge to near-identity anyway (Occam-collapse to the elementwise case despite no explicit
  regularization pushing that way, e.g. because the small weight-decay still favors small-norm solutions) —
  would reproduce the bilinear result for a *different, informative* reason: even an unconstrained non-commutative
  composition operator doesn't get used non-commutatively unless the readout task forces it to.
- **Sequencing-order diagnostic (built into the design, see cell spec below):** a `TRANSITION_OP_SHUFFLED_ORDER`
  ablation (apply the same learned `M_i` but in a randomly PERMUTED slot-processing order at test time only) should
  degrade performance if the mechanism genuinely uses sequence-order non-commutativity; if it does NOT degrade,
  the "order" being read is coming from somewhere else (e.g. slot-identity tagging leaking through some other path)
  and the mechanism-attribution claim is void even if the raw accuracy numbers look good.
- Would NOT be a non-result if it merely ties role-keying — TEM/grid-cell literature does not predict it strictly
  dominates a hand-designed role-key, only that it is a brain-grounded alternative that doesn't require external
  role assignment.

---

## (2) Heteroassociative synaptic asymmetry

### (a) Biology (lead)

- **Classical outer-product/correlation-matrix formalism** (Kohonen 1972, *IEEE Trans. Computers*; Anderson 1972,
  *Math. Biosciences*; both secondary-sourced this cycle via search summaries, not primary-fetched): `W = sum_i
  (b_i a_i^T)`. Confirmed core asymmetry claim: `W @ a_i ~ b_i` (forward) is built in by construction, but `W` is
  generally **not symmetric**, and there is **no automatic backward mapping** — `W^T @ b_i` is a separate,
  independently-defined operation, not guaranteed to recover `a_i` unless `W` was built symmetrically.
- **Willshaw, Buneman & Longuet-Higgins** (1969, *Nature* 222:960-962, secondary-sourced) — the original
  binary-correlogram associative net. **Marr** (1971, *Phil. Trans. R. Soc. B*, secondary-sourced via 2015
  commemorative special issue) — archicortex/hippocampus as a simple associative-memory device.
- **Hippocampal circuit grounding is weaker than expected, and contains an important honest correction surfaced
  this cycle**: McNaughton & Morris (1987, *Trends in Neurosciences*) proposed CA3 recurrent-collateral LTP as a
  Kohonen/Marr-style correlation-matrix memory, but a direct, more recent modeling result (Christie et al.,
  PMC4869174, "Symmetric STDP at CA3-CA3 synapses optimizes storage and recall in autoassociative networks") found
  storage/recall in CA3's own recurrent collaterals is **more robust with SYMMETRIC, not asymmetric, plasticity** —
  i.e. genuine forward != backward directional asymmetry is **not** the dominant framing for CA3-CA3 recurrence
  itself. The heteroassociative-asymmetry story fits **cross-region pathways** (EC->DG->CA3, or CA3->CA1) far
  better than CA3's own recurrent loop. Treat "hippocampus IS an asymmetric heteroassociative memory" as
  region-specific, not a blanket claim.
- **Asymmetric Hebbian plasticity as the directionality mechanism**: Abbott & Blum (1996, *Cerebral Cortex*,
  "Functional Significance of LTP for Sequence Learning and Prediction") is the clearest primary link found this
  cycle — temporal asymmetry in NMDA-mediated LTP induction directly converts a population code into a
  forward-shifted/predictive code, i.e. `W != W^T` emerges from STDP's causal (pre-before-post) timing window.
- **Modern Hopfield / dense associative memory** (Krotov & Hopfield 2016; Ramsauer et al. 2020, arXiv:2008.02217)
  — exponential-in-dimension capacity vs. classical Hopfield's well-known **~0.14N hard capacity limit**, beyond
  which spurious attractors proliferate. **Load-bearing failure-mode finding, directly convergent and unusually
  explicit**: a 2025 synthesis (arXiv:2505.21777, "Memorization to Generalization: Emergence of Diffusion Models
  from Associative Memory") states that near-capacity "generalization" in outer-product/Hopfield memories is really
  **interpolation among stored patterns**, not synthesis of a relation for a genuinely unseen pair. **The literature
  is consistent that outer-product/Hopfield-style memory is fundamentally a lookup/storage mechanism** — it recalls
  previously-bound pairs (or noisy/partial versions), with no demonstrated mechanism for representing an arbitrary
  relation between two never-before-seen items outside the stored set.

### (b) Best substrate operator + why

**`HETEROASSOC_OP`**: a literal **one-shot Hebbian write, zero gradient descent** — the one CONSTRUCT-class arm in
this cell (all other candidates are SGD-learned). Build `W = sum_{train rows} onehot(y_row) (x) feature(x_0, x_1)`
(outer product of the training label's one-hot target with a feature vector built from the two dominance-relevant
slots' shared embeddings, e.g. their FHRR bind or concatenation). At query time, score candidates via `W @
feature(query)`, argmax. Zero training epochs, zero learned readout — this is the literal brain mechanism (a
correlation-matrix write), not a differentiable relaxation of it, which keeps the comparison honest: it is a
genuinely different mechanism CLASS from every other arm in this cell, not just a different parameterization.

### (c) Prediction

**This is the one candidate this note predicts will fail the primary HARD-PASS bar (beat role-keying on NOVEL),
and says so up front, per the honest-negative discipline** — but its predicted failure MODE is itself the useful,
falsifiable result: expect `HETEROASSOC_OP` to perform **well on SEEN** (near-`MEMORIZE`-arm levels) and to
**degrade sharply on NOVEL** (the literature's own predicted lookup-not-relation failure). A large, pre-registered
SEEN-minus-NOVEL gap on `HETEROASSOC_OP` specifically (see band below) would be a *clean, literature-predicted,
positive confirmation of a negative* — informative even though it does not clear the primary asymmetric-generalization
bar. If it unexpectedly does NOT show this gap (i.e. generalizes to novel pairs about as well as it does to seen
ones), that would be the more surprising and higher-value finding, worth its own follow-up.

### (d) Failure modes / non-result conditions

- Predicted primary failure mode (lookup-not-relation) is not itself a non-result if the pre-registered
  SEEN/NOVEL-gap diagnostic fires as predicted — that is a positive, mechanism-confirming result, just not a
  HARD-PASS on the primary axis.
- Would be a genuine non-result / uninformative if `HETEROASSOC_OP`'s SEEN performance is ALSO poor (would mean the
  construction itself is broken, not that the mechanism's known limitation was exercised) — guarded by requiring
  SEEN accuracy well above chance as a construction-sanity floor (see cell spec).
- Crosstalk/capacity ceiling (~0.14N classical Hopfield analog) is a live risk if `N_ENT=220` training rows produce
  more distinct patterns than the embedding dimension comfortably separates — report degradation with training-set
  size as a diagnostic, not gated.

---

## (3) Temporal-order via theta phase precession

### (a) Biology (lead) — two distinct phenomena, often conflated; disambiguated this cycle

- **(A) Strict phase precession** (O'Keefe & Recce 1993, *Hippocampus*): a **single** place cell's firing phase
  advances as the animal crosses that cell's OWN place field — encodes within-field POSITION for one cell, NOT
  directly a two-item order code.
- **The bridge from (A) to a population-level order code**: Skaggs, McNaughton, Wilson & Barnes (1996, *Hippocampus*,
  verified via PubMed/Wiley/lab PDF) shows that **across a population** of place cells with sequential/overlapping
  fields, phase precession compresses the real behavioral-timescale traversal sequence into a single theta cycle
  (compression ratios up to ~10:1), with relative firing-phase order across cells mirroring real-world spatial
  order. Important scope limit: this is demonstrated for **spatially contiguous, correlated cells** (place fields
  along a path), not for an arbitrary, unrelated pair of items.
- **(B) Discrete gamma-subcycle-per-item model** (Lisman & Idiart 1995, *Science*; Lisman & Jensen 2013, *Neuron*,
  "The Theta-Gamma Neural Code"): each theta cycle subdivided into ~7 gamma subcycles, one memory item per
  subcycle — order = which subcycle an item fires in, giving the classic "7+/-2" capacity link. Heusser, Poeppel,
  Ezzyat & Davachi (2016, *Nat. Neurosci.*, verified PMC5039104) is the key human intracranial/MEG evidence:
  different sequence positions show gamma power concentrated at distinct theta phases, phase precision predicts
  order-memory success. **Scope limit confirmed by the lit-scan: this evidence is specifically for
  temporally-experienced sequences, not semantic role-asymmetry (subject/object, cause/effect)** — no source
  generalizes it to non-temporal semantic order.
- **Load-bearing, recent, direct counter-finding surfaced this cycle**: Liebe et al. (2025, *Nat. Neurosci.*,
  PMC11976290) directly tested and **refuted** the Lisman phase-order claim using human MTL single-unit recordings
  (1,420 neurons, 16 patients) plus matched RNN modeling — **phase order did NOT match item order**; phase was
  better explained by a confound between oscillation frequency and stimulus timing. This is a serious, recent,
  well-powered challenge to mechanism (B) as literally implemented in the brain, and must be weighted heavily in
  this candidate's calibration.
- **No evidence found for isolated-pair, context-free "does A precede B" queries.** Every version of (A)/(B)
  requires a shared, ongoing oscillatory reference (a "carrier" theta) plus an active sequence-encoding episode —
  none of the sources found support a phase code answering a one-shot relational query pulled from memory without
  that context, which is closer to how this arena's DOMINANCE relation would need to be read.

### (b) Best substrate operator + why (with an explicit mechanistic caveat)

**`PHASE_ORDER_OP`**: fixed, evenly-spaced per-role phase offsets `theta_i = i * (2*pi/K)` (direct analog of
gamma-subcycle slot assignment), each ordinal value gets a LEARNED complex phasor code `c[l]` (shared table, same
style as other shared-embedding arms), per-slot phasor `p_i(x_i) = c[x_i] * exp(i*theta_i)`, bound across slots via
the substrate's **real FHRR complex elementwise multiply** (`hd_bind`, the existing production bind — no new
primitive), `z = product_i p_i(x_i)`. Readout: learned linear head on `[z.real, z.imag]`, same capacity class as
every other learned arm.

**Mechanistic honesty flag, pre-registered before running (do not skip this in the writeup of results):** complex
elementwise multiplication is **commutative** (`z1*z2 = z2*z1`) — the FHRR bind itself cannot become
order-sensitive from this construction alone. Any order-sensitivity `PHASE_ORDER_OP` shows must come from the
FIXED, role-differentiated `theta_i` acting as a role-tag (structurally a permutation/role-key dressed in phase),
**not** from the bind operator becoming non-commutative. This must be stated in the results writeup regardless of
outcome, to prevent overclaiming "phase precession discovered order" when the honest mechanism is "role-tagging via
phase, exactly like role-keying but relabeled."

### (c) Prediction

**Weakest-grounded candidate of the three.** Two outcomes are plausible and both are informative:

- If `PHASE_ORDER_OP` clears dominance_ok, expect it to land **close to `ROLE_KEYED`**, not clearly above it — per
  the mechanistic caveat, a win here is expected to be attributable to the role-offset tag, confirmed via the
  `PHASE_NO_OFFSET` ablation (below) collapsing to near-chance. A pass that is NOT confirmed by that ablation
  (i.e. `PHASE_NO_OFFSET` ALSO passes) would falsify the "it's just a role-tag" account and require a genuinely new
  explanation — flag as the single most surprising possible outcome in this whole note.
- More likely per the Liebe et al. 2025 refutation and the missing context-free-query precedent: `PHASE_ORDER_OP`
  fails to clear dominance_ok, or clears only marginally / inconsistently across seeds — this would be consistent
  with (not contradicting) the current state of the biology, which itself just took a direct hit against the phase
  claim in 2025.

### (d) Failure modes / non-result conditions

- **`PHASE_NO_OFFSET` diagnostic (all `theta_i = 0`, i.e. plain symmetric complex-phase fold, no role-tag)**:
  reported, not gated. If `PHASE_ORDER_OP` and `PHASE_NO_OFFSET` perform similarly, the phase-offset mechanism is
  doing nothing and any apparent signal is coming from elsewhere (construction bug or the learned complex table
  itself leaking role information some other way) — treat as a REFUTE-adjacent finding for this specific candidate.
- Would be a clean non-result (not informative either way) if `INT_MATCH`-style sanity floor is not met for the
  arena itself — already guarded by the existing `REFUTE_INT_FLOOR` gate carried over from the prior cell.
- Mis-mapping risk (explicitly named in the task): conflating strict single-cell phase precession (A) with a
  population two-item order code (B) — this note's design uses (B)'s mechanism (per-role fixed offset, discrete
  slot assignment), not (A), and that choice should be stated explicitly in the cell docstring so a future reader
  does not assume (A) was tested.

---

## Ready-to-build head-to-head cell design

### Arena (REUSE verbatim — no re-hunt)

Exact arena from `experiments/exp_interaction_bilinear_wall_break_v1.py` / `exp_interaction_nonadditive_discovery_v1.py`
(commits 29b53e63b / 59056b6d4): `K=4` constituents, `L=4` ordinal levels, `N_ENT=220` sampled entities (combo space
`L^K=256`), `QUERY_FRAC=0.45`, families `{PARITY, AND2, MULT, DOMINANCE, ADD}`, regimes `{CLEAN, ARBITRARY, SHUFFLE}`,
`split_novel` (SEEN vs NOVEL by combo membership in train), deterministic seeding from integer indices only (never
salted hashing — the prior VET-fixed root cause). Reuse `make_X`, `target`, `plant_regime`, `split_novel`,
`nonadditivity`, `arm_int_match` (INT_MATCH sanity), `arm_mono` (MONO additive contrast), `arm_homophily`/
`arm_memorize`/`FREQ_NULL`/`POP`/`ORACLE` baselines verbatim.

### Arms

| Arm | Class | Mechanism |
|---|---|---|
| `INT_MATCH`, `MONO` | construction-proof | reused verbatim, arena sanity |
| `LEARN_SYM` | learned | shared code + product, swap-symmetric (parity specialist / symmetric reference) |
| `ROLE_KEYED` | learned | `max(LEARN_INT, LEARN_ADD)`, reused verbatim (**incumbent asymmetric baseline**) |
| `BILINEAR_REF` | learned | `LEARN_BILINEAR_RANK1`, reused verbatim (**failed reference — re-run in the SAME seeds/units for a controlled comparison, not just cross-cited from the prior cell**) |
| `TRANSITION_OP` | learned, NEW | sequential non-commutative matrix chain (mechanism (1) above) |
| `TRANSITION_OP_SHUFFLED_ORDER` | diagnostic, NEW | same learned `M_i`, slot-processing order randomly permuted at TEST time only — reported, not gated |
| `HETEROASSOC_OP` | one-shot Hebbian CONSTRUCT, NEW | `W = sum onehot(y) (x) feature(x0,x1)`, zero SGD (mechanism (2) above) |
| `PHASE_ORDER_OP` | learned, NEW | FHRR complex bind + fixed per-role phase offsets (mechanism (3) above) |
| `PHASE_NO_OFFSET` | diagnostic, NEW | same but `theta_i=0` for all `i` — reported, not gated, attribution check |
| `FREQ_NULL`, `MEMORIZE`, `POP`, `ORACLE` | baselines | reused verbatim |

Same `EMB_D=48`, same Adam/SGD hyperparameters where applicable, same `EPOCHS=500`, `LR=0.05` for every learned arm
(fairness — no arm gets an unfair capacity/training-budget advantage). Same 5 seeds `(7,13,17,23,29)` as the
existing `run_measurement` default, for direct comparability with the already-landed bilinear cell's numbers.

### Must-fails

Same `ARBITRARY` + `SHUFFLE` regimes, same `MUSTFAIL_TOL=0.10`, applied to all three NEW candidate operators
(`TRANSITION_OP`, `HETEROASSOC_OP`, `PHASE_ORDER_OP`) over `CLAIM_FAMILIES = {PARITY, AND2, MULT, DOMINANCE}` (ADD
excluded from must-fail scope, per existing convention). Each candidate's gap over `FREQ_NULL` on NOVEL
ARBITRARY/SHUFFLE must be `<= 0.10`, else that candidate is fitting noise, not structure — invalidates its result
independent of the other two.

### Pre-registered bands (fix before running; TOL_SPEC=0.10, same constants as the landed bilinear cell for continuity)

For each candidate `OP` in `{TRANSITION_OP, HETEROASSOC_OP, PHASE_ORDER_OP}`, on NOVEL CLEAN:

```
dominance_ok(OP) = OP_dom >= ROLE_KEYED_dom - 0.10        (within tolerance of the incumbent asymmetric specialist)
                   AND OP_dom - FREQ_dom      >= 0.10     (clearly beats the honest antisymmetric FREQ_NULL)
                   AND OP_dom - LEARN_SYM_dom >= 0.15     (clearly beats the symmetric/elementwise reference)

parity_ok(OP)     = OP_par >= LEARN_SYM_par - 0.10
                    AND OP_par >= chance_p + 0.20
                    AND OP_par - LEARN_ADD_par >= 0.15
                    AND OP_par - FREQ_par      >= 0.15

mustfail_ok(OP)   = arb_gap(OP) <= 0.10 AND shuf_gap(OP) <= 0.10, all CLAIM_FAMILIES
```

**HARD-PASS (overall) = at least one of `{TRANSITION_OP, HETEROASSOC_OP, PHASE_ORDER_OP}` clears
`dominance_ok(OP) AND mustfail_ok(OP)`** — a brain-grounded asymmetric operator that reads dominance on NOVEL
combos at/above the role-keyed specialist and clearly above `FREQ_NULL`, with must-fails firing. Report which
candidate(s) cleared it. **Bonus (reported separately, not required for HARD-PASS): does that same candidate ALSO
clear `parity_ok`** — a step toward one code doing both, extending the July 14 unification drill's Rank-1/Rank-2
proposals with a THIRD, brain-mechanism-grounded candidate.

**HARD-FAIL (overall) = none of the three clears `dominance_ok AND mustfail_ok`** — role-keying remains the best
asymmetric construct on this arena; the three brain mechanisms, as directly transferred here, do not beat it.
(Per the honest per-candidate predictions above, this is the single MOST LIKELY overall outcome if `HETEROASSOC_OP`
and `PHASE_ORDER_OP` behave as their own literature predicts — the interesting open question is whether
`TRANSITION_OP` alone is enough to flip the overall verdict to HARD-PASS.)

**Diagnostic bands (reported, not gating the overall verdict):**

```
heteroassoc_lookup_confirmed = HETEROASSOC_seen_dom - HETEROASSOC_novel_dom >= 0.30
    (confirms the literature-predicted lookup-not-relation failure mode; a POSITIVE finding even if HETEROASSOC
    hard-fails dominance_ok)

phase_attribution_to_role_tag = (PHASE_ORDER_OP_dom - PHASE_NO_OFFSET_dom) >= 0.20
    AND |PHASE_ORDER_OP_dom - ROLE_KEYED_dom| <= 0.15
    (if PHASE_ORDER_OP passes, confirms the win is the role-offset tag, not bind non-commutativity, per the
    mechanistic honesty flag in section 3b)

transition_order_confirmed = TRANSITION_OP_dom - TRANSITION_OP_SHUFFLED_ORDER_dom >= 0.20
    (confirms TRANSITION_OP's win, if any, genuinely depends on sequence-order non-commutativity rather than
    some other leak)
```

**MIDDLE_BAND** = any candidate clears dominance_ok on SEEN but not on NOVEL without meeting the
`heteroassoc_lookup_confirmed` threshold cleanly (an under-diagnosed partial), or a candidate clears the raw
threshold but fails its own mechanism-attribution diagnostic (e.g. `PHASE_ORDER_OP` passes `dominance_ok` but
`phase_attribution_to_role_tag` is false, meaning the win is unexplained rather than cleanly attributed) — report
per-candidate, do not average into one global verdict.

**REFUTE_IMPL** = reused verbatim (`INT_MATCH` must solve parity and dominance, floor 0.90) — arena/impl sanity.

---

## Falsifiable predictions summary

| Candidate | HARD-PASS threshold | HARD-FAIL threshold | Predicted outcome (this note's honest call) |
|---|---|---|---|
| `TRANSITION_OP` | dominance_ok AND mustfail_ok | `<=0.20` on dominance OR ties `LEARN_SYM` (`\|OP_dom-SYM_dom\|<0.05`) like the bilinear op did | Most likely to pass; strongest brain + existing-substrate (GHRR) grounding |
| `HETEROASSOC_OP` | dominance_ok AND mustfail_ok on NOVEL | large SEEN-NOVEL gap (`heteroassoc_lookup_confirmed`) with NOVEL `<=0.20` | Most likely to hard-fail dominance_ok on NOVEL, but confirm the diagnostic gap — an informative negative |
| `PHASE_ORDER_OP` | dominance_ok AND mustfail_ok AND (if passing) confirmed via `phase_attribution_to_role_tag` | `<=0.20` OR fails to separate from `PHASE_NO_OFFSET` | Weakest-grounded; most likely to hard-fail or produce an unattributable pass requiring a MIDDLE_BAND call |

---

## Cheap decisive test

Run all three candidates plus the two diagnostic ablations (`TRANSITION_OP_SHUFFLED_ORDER`, `PHASE_NO_OFFSET`) plus
`HETEROASSOC_OP`'s SEEN-stratum accuracy, in the SAME cell, SAME seeds, alongside re-run `ROLE_KEYED`/`BILINEAR_REF`/
`LEARN_SYM` for a fully controlled comparison. One CPU cell, ~5 arms x 5 families x 3 regimes x 5 seeds — same order
of magnitude as the already-landed bilinear cell (775 lines, ran to completion on CPU). No new external data, no
LLM at measurement, glass-box throughout.

## Substrate-product implications

- If `TRANSITION_OP` clears HARD-PASS: converts "role-keying is our only working asymmetric construct" into
  "role-keying AND a brain-grounded, order-sensitive-by-construction sequential operator both work" — reduces
  reliance on hand-designed role vectors, reuses the already-validated GHRR non-commutative-bind machinery in a new
  composition pattern, and gives a second, mechanistically-explained path to asymmetric relation encoding for future
  KG-relation work (directly relevant to the currently-active AdditiveKGMap improvement thread).
- If `HETEROASSOC_OP` confirms the lookup-not-relation diagnostic: this is a clean, literature-predicted negative
  that closes off one-shot Hebbian memory as a *generalization* mechanism for novel relation instances (it remains
  useful for what it is actually good at — fast, cheap recall of previously-seen pairs, i.e. a genuine complementary
  role alongside a generalizing mechanism like TRANSITION_OP, not a competitor to it).
- If `PHASE_ORDER_OP` fails or is unattributable: closes the phase-precession angle for this substrate-product with
  a specific, mechanistically-explained reason (bind commutativity + the 2025 Liebe et al. refutation), rather than
  leaving it as an untested "maybe" in the shortlist — frees future research cycles from re-visiting phase-coding
  as a live candidate for asymmetric bind design absent new bio evidence.
- Either way, all three results feed back into the still-open "does ANY single operator preserve BOTH parity and
  dominance" unification question from the July 14 drill — a `TRANSITION_OP` clearing both bars would be a
  materially stronger unification candidate than that drill's Rank 1/2 (role-keyed-bundle, tied/untied bilinear
  heads) since it would do so via ONE mechanism class rather than an explicit two-channel composition recipe.

## Cross-thread synthesis

- Directly follows `drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md` (established the
  SEPARATE-mechanisms shortlist, ranked bilinear pooling #1 — since HARD-FAILed on dominance) and
  `drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md` (established that "where asymmetry
  lives" is contested across TEM transition matrices / CA3-CA1 plasticity-rule split / Lippl additive-geometry
  accounts — this note operationalizes the first of those three contested accounts as a buildable, testable
  operator, and adds two more mechanism classes (heteroassociative outer-product, phase-order) not covered by
  either July 14 drill's shortlist).
- `research_successor_representation_reachability_autonomous_traversal_2026-07-09.md` used the SR/PPR resolvent for
  a DIFFERENT problem (multi-hop goal-conditioned traversal signal, not single-relation-instance bind) — this note
  explicitly does NOT reuse that note's design; TEM's `W_a` (not the SR resolvent) is the operator transferred here,
  flagged to avoid conflating two adjacent-but-distinct successor/transition concepts.
- Extends the June 2026 GHRR non-commutative-bind pilot: `TRANSITION_OP` is a genuinely new COMPOSITION PATTERN
  (sequential chaining across K slots with content-folding at each step) built on that already-validated primitive,
  not a new operator class — lowest-novelty, highest-precedent candidate of the three.

## Citations (verified count)

**~24 distinct sources across 3 parallel Sonnet lit-scan sub-agents this cycle**, plus carried-over citations from
the two July 14 drills (not re-counted here, see those notes for their own ~30+34 citation lists).

Transition/successor angle (~8): Dayan (1993, *Neural Computation*, verified via abstract); Stachenfeld, Botvinick &
Gershman (2017, *Nat. Neurosci.*, verified); Whittington et al. (2020, *Cell*, secondary-sourced, corroborated
across two cycles); Burak & Fiete (2009, *PLoS Comp. Biol.*, verified via arXiv/lab PDF); Gao, Xie, Zhu et al.
(NeurIPS 2021, arXiv:2006.10259, verified via abstract); Gosmann & Eliasmith (2019, VTB, verified via PubMed/lab
PDF); Momennejad SR review (bioRxiv, secondary); Gershman "SR computational logic" (2018, secondary).

Heteroassociative angle (~9): Kohonen (1972, secondary); Anderson (1972, secondary); Willshaw, Buneman &
Longuet-Higgins (1969, *Nature*, secondary); Marr (1971, secondary via 2015 commemorative issue); McNaughton &
Morris (1987, secondary); Christie et al. (PMC4869174, symmetric-STDP-in-CA3 correction, verified via PMC); Levy &
Steward (1983, secondary); Abbott & Blum (1996, *Cerebral Cortex*, secondary abstract, PDF located not fully
fetched); Ramsauer et al. (2020, arXiv:2008.02217, verified); arXiv:2505.21777 "Memorization to Generalization"
(verified via HTML fetch).

Phase-order angle (~7): O'Keefe & Recce (1993, secondary); Skaggs, McNaughton, Wilson & Barnes (1996, verified via
PubMed/Wiley/lab PDF); Lisman & Idiart (1995, *Science*, verified); Lisman & Jensen (2013, *Neuron*, verified);
Heusser, Poeppel, Ezzyat & Davachi (2016, *Nat. Neurosci.*, verified PMC5039104); **Liebe et al. (2025, *Nat.
Neurosci.*, PMC11976290, verified via PMC — the single most load-bearing NEW citation this cycle, a direct
refutation)**; Dragoi & Buzsaki (2006, *Neuron*, secondary).

Substrate/verdict grounding: `data/exp_interaction_bilinear_wall_break_v1/metrics.json` (read directly off disk,
commit 29b53e63b) — exact numbers quoted above, not recalled from memory.

## P_deflated

**Per-candidate (lit-scan calibration penalty applied, 0.15-0.25 deflation, novel-synthesis capped at 0.50):**

- `TRANSITION_OP` clears HARD-PASS (dominance_ok + mustfail_ok): base intuition ~0.65 (strongest, most directly
  transferable precedent — TEM's non-commutative matrices, a proven grid-cell group-representation theorem, AND an
  already-validated substrate primitive (GHRR) to build on) — deflated to **0.48** (below the 0.50 cap; this exact
  composition pattern on this exact arena has not been tested, and the parity-preservation bonus is explicitly
  uncertain).
- `HETEROASSOC_OP` clears HARD-PASS: base intuition ~0.20 (literature convergently and explicitly predicts the
  opposite outcome) — deflated to **0.12**. The `heteroassoc_lookup_confirmed` diagnostic passing (the informative
  negative) is separately estimated at **~0.55** — more likely than not, given how convergent and explicit the
  lookup-not-relation literature is this cycle.
- `PHASE_ORDER_OP` clears HARD-PASS: base intuition ~0.25 (weakest grounding, a direct 2025 refutation of the core
  claim, no context-free-query precedent) — deflated to **0.15**. Conditional on passing, `phase_attribution_to_role_tag`
  confirming (i.e. the win is "just" a role-tag) is estimated at **~0.70** given the hard commutativity objection.

**Overall (at least one candidate clears HARD-PASS): P_deflated = 0.42** (capped below the 0.50 novel-synthesis
ceiling; driven almost entirely by `TRANSITION_OP`'s individual estimate, with `HETEROASSOC_OP` and `PHASE_ORDER_OP`
contributing negligible marginal probability of their own per their own literatures' honest predictions).

## Next-drill candidate

If `TRANSITION_OP` HARD-PASSes and also clears the parity bonus: the natural follow-up is testing whether this same
sequential-matrix-chain composition pattern can be extended to K>4 constituents / deeper relation chains (the
"uncle = father-then-brother" multi-hop composition case TEM was originally built for), which would connect this
result directly to the currently-active AdditiveKGMap improvement thread (`hdlab/additive_map.py`) rather than
remaining confined to this synthetic arena. Per the field advisor, this also sits on the
`network-science-graph-theory` adjacency (Tier-1-equivalent per the 07-15 advisor run) if it needs a graph-scale
follow-up cell.
