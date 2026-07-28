# Research Note: Native VSA Binding for Compositional Generalization (Systematicity)

**Date:** 2026-07-25
**Filed by:** research sub-agent (design-oriented brain drill; biology-first, no child dispatched)
**Trigger:** atom 29556 (`exp_learned_meaning_frontend_differentiation_v1`) VET-confirmed structural
failure -- flat item+relation->property MLP hub acquires fine in-vocab discrimination (learning curve
rises, coarse-before-fine) but held-out same-item/new-relation compositional accuracy decays to the
frozen floor (`ho_lift 0.0`, confirmed structural not init-noise). Roadmap's genuine untested edge =
compositional generalization via NATIVE BINDING, where flat architectures are known to fail.
**Calibration:** P estimates deflated 0.15-0.25 per lit-scan calibration penalty; novel-synthesis P
capped at 0.50.

---

## HEADLINE

The flat MLP hub's failure is not a training-recipe defect -- it is the textbook Fodor-Pylyshyn /
Smolensky systematicity failure mode, independently reproduced inside our own substrate. The literature
(Smolensky tensor-product representations, Hummel-Holyoak LISA temporal-synchrony binding, and the 2022
Neuro-Vector-Symbolic Architecture (NVSA) for Raven's Progressive Matrices, 87.7-88.1% via a *learned
perceptual front-end feeding a FIXED symbolic dictionary/algebra*) converges on one minimal fix: force
item and relation to combine ONLY through a fixed, invertible bilinear algebraic operator (the
substrate's own `bsc_bind`/`bind` -- elementwise multiply / circular convolution), and put the ONLY
learned capacity downstream of that bind, in a SINGLE role-agnostic linear readout. This structurally
forbids the exact failure mode measured in 29556: an MLP hidden layer is free to fit `concat(item,
relation-onehot)` idiosyncratically per (item, relation) pair, so it CAN and DID memorize training
combinations without factoring; a fixed-bind + single-shared-linear-readout CANNOT do that -- the
transformation applied to any item under relation `r` is always the SAME transformation (multiply by
`role_HV_r`, then apply the one shared `M`), so a novel (item, relation) pair inherits the correct
transform as long as the item has been seen under some OTHER relation and the relation has been seen
with some OTHER item. That is precisely the Fodor-Pylyshyn systematicity criterion, and precisely what
29556 never tested cleanly (its held-out pool mixed CATEGORY-CORRELATED relations, which are learnable
from shared structure, with per-item DISTINCTIVE relations, which are unlearnable by construction --
conflating "binding can't generalize" with "there is nothing to generalize").

## KB-check result (what's genuinely new)

`bash tools/substrate_query.sh` on both queries hit strong priors -- nothing here needs re-derivation:

- `notes/wave14e_hierarchical_composition_research.md` (cosine 0.42): full VSA-hierarchy survey
  (Plate 1995 chunking, Kanerva 1996 BSC, Smolensky-Tesar TPR, Eliasmith SPA) + brain mapping
  (cortical hierarchy V1->IT as per-level Hopfield cleanup, Quiroga grandmother cells). This is
  DEPTH/hierarchy (bytes->words->phrases), a different axis from ours (flat item x relation binding).
  Reused: the "cleanup/dictionary is the non-linearity that gives systematic composition, not raw
  binding alone" lesson, and the bio-mapping methodology.
- `notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md` Probe 10 (cosine 0.38-0.40):
  ALREADY states the exact substrate mapping -- "substrate's MAP-I XOR binding is compositional by
  construction... generalizes compositionally in the RETRIEVAL dimension... the GENERATION dimension
  (generating novel compositions as outputs) requires a decoder, which substrate does not natively
  have." P_deflated 0.50 pre-registered there for "substrate outperforms LLM on compositional
  retrieval," HARD-PASS >90% recall / HARD-FAIL <70% recall for novel bound pairs at N=4096. That
  probe is RETRIEVAL of an already-bound composite (compositional storage); ours is COMPLETION --
  given item+relation, predict an unseen property vector -- which requires exactly the missing
  "decoder" Probe 10 flagged as the gap. **This note designs that decoder.**
- `notes/prior_art_scour_synthesis_focus_chaingrade_2026-07-18.md`: names LISA/Hummel-Holyoak,
  Smolensky, TPR, Eliasmith SPA as already-scoured prior art for "binding problem, systematicity,
  structure-content factorization," confirming this drill should NOT re-derive binding theory.

**Genuinely new (not in KB):** (a) the specific NVSA "learned front-end + frozen dictionary/fixed
algebra" split as the concrete engineering pattern to copy; (b) the diagnosis that 29556's `ho_lift 0.0`
held-out pool conflated learnable (category-correlated) with unlearnable-by-design (distinctive)
relations, meaning the prior negative under-tested systematicity rather than refuting it; (c) the
bilinear-factorization argument for WHY fixed-bind + single-linear-readout is structurally immune to
29556's failure mode; (d) the corrected cell design below.

## 1. Systematicity: brain-faithful biology + minimal mechanism

**Fodor & Pylyshyn 1988** (*Cognition* 28:3-71) formalized the challenge: understanding "Ann introduced
Bill to Claire" entails understanding "Bill introduced Claire to Ann" -- human cognition is systematic,
combinatorially structured. They argued pure associative (flat) connectionist nets cannot exhibit this
except by implementing a classical symbol system underneath. **Smolensky's tensor-product
representations (TPR)** (Smolensky 1990; Smolensky-Legendre 2006; Smolensky-Tesar 1995) were the
principled connectionist answer: bind role⊗filler via an outer/tensor product (or circular convolution
in the compressed HRR/VSA variant), so that role and filler remain algebraically separable and any
role can compose with any filler it has never jointly appeared with. **Hummel & Holyoak's LISA**
(Psychological Review 1997; "Learning and Inference with Schemas and Analogies") is the closest
biological-mechanism instantiation: role-filler binding is implemented via TEMPORAL SYNCHRONY of firing
(dynamic binding, not a static tensor slot) across semantic-unit populations, giving the system both
connectionist flexibility (distributed similarity-based retrieval/mapping) and symbolic structure-
sensitivity (systematic relational inference, analogical mapping, schema induction) -- LISA papers
explicitly frame this as answering Fodor-Pylyshyn without full tensor-product blowup. **Why a flat
associative net fails**: a flat hub (our component-1 MLP) receives `item ++ relation` as an
unstructured concatenation and is free to route information through a hidden layer with NO constraint
that the item-transformation must factor identically across relations -- gradient descent then does the
locally-optimal thing (memorize per-(item,relation) idiosyncrasies), which is exactly what 29556 measured
(`ho_lift 0.0`: held-out combinations decay to the frozen floor, i.e., the hub learned nothing that
transfers). **Minimal brain-faithful fix** shared across TPR/LISA/BSC-VSA: force the combination through
a FIXED, invertible algebraic bind (tensor product / circular convolution / elementwise Hadamard for
bipolar codes) so that binding itself carries zero free parameters and is architecturally guaranteed to
apply the SAME transform to a novel item under a role it has seen with other items.

**Caveat (biology-grounded, tempering over-claim):** Lake, Linzen & Baroni's meta-learning work
(*Nature* 2023, "Human-like systematic generalization through a meta-learning neural network," MLC) is
a genuine counter-data-point: it shows systematic/compositional generalization achievable in a purely
distributed (non-explicitly-bound) network via an optimization-FOR-compositionality training regime
(meta-learning over many compositional episodes), not via architectural binding. This means native
binding is A sufficient mechanism, not proven NECESSARY -- if the binding cell below still fails, the
live alternative hypothesis is "the lever is the TRAINING REGIME (meta-learning-for-compositionality),
not the architecture," and that becomes the next-drill candidate rather than "go deeper into binding."

## 2. Does substrate-native VSA bind fix it? NVSA pattern (learned front-end + fixed algebra)

**A neuro-vector-symbolic architecture for solving Raven's Progressive Matrices** (arXiv 2203.04571,
*Nature Machine Intelligence* 2023) is the direct engineering precedent: a LEARNED perceptual front-end
(trainable ResNet-18) produces object/attribute vectors; these are combined with a FROZEN codebook of
d-dimensional vectors via fixed-width vector arithmetic (bind/bundle); reasoning/rule application is
fixed algebra over that frozen dictionary. Result: 87.7% (RAVEN) / 88.1% (I-RAVEN), beating end-to-end
neural and prior neuro-symbolic baselines, with compositional generalization emerging FROM the frozen-
algebra structure, not from more training data. This is the exact split our substrate should copy:

- **FIXED (unlearned):** (i) per-relation role hypervectors `role_HV_r`, one fixed random vector per
  relation drawn once at init (seed-fixed, checked near-orthogonal -- the VSA-native analog of TPR role
  vectors / LISA role units); (ii) the bind algebra itself -- `hdlab.binding.bsc_bind` (bipolar
  elementwise multiply, self-inverse) or `hdlab.binding.bind` (HRR circular convolution via FFT) --
  applied as `bound(i,r) = bind(item_HV_i, role_HV_r)`; (iii) the item embedding pipeline up to and
  including the frozen GloVe/WordnNet `fused()` vector and its existing fixed JL projection into the
  512-d HD space (IDENTICAL to component-1's frozen arm -- this reuses the already-measured meaning axis
  rather than re-litigating it; the ONLY variable under test is the combination mechanism).
- **LEARNED (the only trainable parameters):** a SINGLE linear readout matrix `M` (300-or-512 -> 300,
  matching the property-vector target space) applied identically regardless of relation:
  `predicted_property(i,r) = M @ bound(i,r)`. Because bind is elementwise Hadamard, for a fixed
  `role_HV_r` this is `M @ diag(role_HV_r) @ item_HV_i` -- a bilinear map in (item, role). `M` is fit by
  ordinary least-squares / gradient descent over the SAME training pairs used for the flat-MLP baseline.
  Critically, `M` never sees `r` directly except through its fixed algebraic effect on the vector --
  it cannot learn an item-specific shortcut for a particular relation the way the MLP's hidden layer
  could, because there is no hidden layer with freedom to entangle item-identity and relation-identity
  arbitrarily. This is the structural difference that should (per TPR/LISA/NVSA) restore systematicity.

This IS the direct extension the note is asked to design: swap the MLP hub's `concat(item, onehot(r))
-> hidden -> property` pipeline for `bind(item_HV, role_HV_r) -> linear M -> property`, holding the item
representation, the eval question, and the property targets byte-identical to 29556, so the ONE
variable is the combination mechanism (unconstrained MLP entanglement vs fixed-bind + linear readout).

## 3. Concrete cell design: `exp_native_binding_compositional_generalization_v1`

Extends `experiments/exp_learned_meaning_frontend_differentiation_v1.py` in place (same DOMAINS,
RELATIONS, SemanticHDEncoder, near-degenerate precheck, shuffled must-fail control, exposure-curve
driver). Two structural changes from 29556:

### 3a. THE CRITICAL FIX -- corrected held-out split (isolates binding, not "unlearnable-by-design")

29556's `make_pairs()` held out a fraction of ALL fine (item,relation) pairs indiscriminately, mixing:
- **category-correlated** relations (per domain, already named in 29556's own docstring): `energy:
  byproduct`, `metal: source`, `planet: moons`, `animal: body` -- each is a near-deterministic function
  of the item's coarse category (renewable->clean / precious->nugget / rocky->none / fish->fins, etc.),
  so its value IS inferable from other same-category items' pairs -- a FAIR systematicity test.
- **distinctive** relations (`source/device` for energy, `property/use` for metal, `property/feature`
  for planet, `property/habitat` for animal) -- per-item idiosyncratic (hydroelectric's dam is not
  inferable from wind's turbine) -- UNLEARNABLE by design regardless of mechanism; holding these out
  cannot distinguish "binding failed" from "there was nothing to bind toward."

**Fix:** restrict the held-out (systematicity) pool to ONLY the four category-correlated relations,
1-2 items per domain, subject to the SAME coverage guard 29556 already implements (item must still
appear under a distinctive relation in train; the category-correlated relation must still appear with
other items in train). Report the flat-MLP baseline RE-MEASURED on this corrected split (not the old
29556 number) -- this is a fair one-variable comparison, and it is itself the first falsifiable
prediction below (the note explicitly does not assume 29556's `ho_lift 0.0` transfers to the corrected
split).

### 3b. THE NEW ARM -- native-binding hub

```
role_HV[r]        = fixed unit-norm random vector per relation, seed-fixed, dim = n_dim (512)
                     (checked near-orthogonal: max pairwise cosine < 0.3, else respec seed)
item_HV(c)        = existing frozen fused(c) meaning vector, JL-projected into n_dim exactly as
                     SemanticHDEncoder already does (UNCHANGED from 29546/29556's frozen arm)
bound(c, r)       = hdlab.binding.bsc_bind(item_HV(c), role_HV[r])       [elementwise multiply, bipolar-
                     compatible; if item_HV is real-valued not bipolar, use hdlab.binding.bind (HRR
                     circular convolution) instead -- pick whichever matches the encoder's actual dtype,
                     do NOT introduce a THIRD representation]
predicted_property(c, r) = M @ bound(c, r)          [M: single (n_dim -> 300) linear map, the ONLY
                     learned parameters; trained by full-batch GD / least-squares on train_all pairs,
                     identical loss/target space to 29556's hub]
score(c)          = cos( predicted_property(c, r), probe )         [same argmax-over-contrast-set
                     eval question as 29556, so results are directly comparable]
```

Arms to run, all on the SAME corrected (category-correlated-only) held-out split:
1. **FROZEN** (no learning) -- carried over unchanged, `cos(fused(c), probe)`.
2. **FLAT-MLP hub** (29556's mechanism, re-measured on the corrected split) -- the baseline to beat.
3. **NATIVE-BINDING hub** (this design) -- fixed role vectors + fixed bind + single linear readout.
4. **SHUFFLED-label control** for arm 3 (identical construction to 29556's control: permute
   category-correlated targets across items within domain; train on permuted, eval on TRUE) -- must
   stay flat; if it rises to match arm 3, the "generalization" is leak/artifact.
5. *(diagnostic, not gating)* **bind-then-shallow-MLP readout**: same fixed bind, but replace the
   single linear `M` with a small MLP readout (same H_BOTTLENECK=32 as 29556). If arm 3 (linear) passes
   but this diagnostic arm regresses toward arm 2's failure, that PINS the mechanism precisely on
   "unconstrained nonlinear entanglement AFTER combination is the failure mode," independent of
   concatenation-vs-binding format -- a valuable mechanism-isolation result either way.

### SHAPE / PLACE / METRIC

- **SHAPE:** bilinear factorization via a FIXED elementwise Hadamard (or circular-convolution) bind of
  item and role vectors, decoded by a SINGLE role-agnostic LINEAR map -- vs. the flat MLP's unconstrained
  nonlinear mixing of `concat(item, onehot(r))` in a shared hidden layer free to entangle item-identity
  and relation-identity arbitrarily.
- **PLACE:** generalization capacity moves OUT of the trained weights' coverage of the training
  distribution and INTO the fixed algebra + fixed role vectors -- i.e., systematicity is a property of
  WHERE composition happens (a structural bind operator that is defined for every item/role pair by
  construction, per Probe 10's "algebraically well-defined without having seen the combination"), not of
  how much data the trained weights have seen.
- **METRIC:** held-out compositional accuracy -- argmax-cosine concept recovery among the domain's
  minimal-pair contrast set, evaluated ONLY on category-correlated (item, relation) pairs where item and
  relation have each been separately trained but never jointly (the literal Fodor-Pylyshyn criterion) --
  identical eval shape to 29556's `fine_discrimination`, so `ho_lift` numbers are directly comparable
  across the flat-MLP and native-binding arms.

### Pre-registered bands (a priori; mirrors 29556's REL_LIFT_HP/HF at 0.25/0.10, SHUFFLE_SEP at 0.15)

- **HARD-PASS:** native-binding `ho_lift` (learned-max-exposure minus frozen, on the corrected
  category-correlated-only held-out split) >= 0.25 AND real-vs-shuffled separation >= 0.15 AND shuffled
  arm stays flat (within 0.12 of its exposure-0 value) AND flat-MLP baseline on the SAME corrected split
  stays below 0.10 (confirms this is a real discriminating test, not an artifact of an easier split).
  -> compositional generalization is a genuine binding-conferred edge; native binding is the
  brain-faithful fix for the roadmap's frontier gap.
- **MIDDLE (informative, non-terminal):** native-binding `ho_lift` in [0.10, 0.25) with shuffled control
  holding -> real but modest generalization; OR flat-MLP baseline ALSO clears >= 0.10 on the corrected
  split -> would mean 29556's `ho_lift 0.0` was itself an artifact of the uncorrected split (a genuine,
  important refutation of the prior negative's generality -- report explicitly, do not bury).
- **HARD-FAIL:** native-binding `ho_lift` < 0.10 on the corrected split -> fixed algebraic binding, with
  meaning held fixed, does NOT restore compositional generalization here -> the failure is not (only) in
  the combination mechanism; two live sub-diagnoses to report: (a) the frozen GloVe/WordNet meaning axis
  itself is ALSO the bottleneck for the linear readout (same wall as 29544-46/29555, now shown to survive
  even fixed-algebra binding) -- points back to the richer/grounded-meaning fork already surfaced to
  USER; (b) role vectors are not sufficiently orthogonal / bind interference at this scale -- check the
  near-orthogonality precheck first before accepting (a).
- **INVALID:** shuffled-trained/true-eval control matches or exceeds the real arm (leak); OR near-
  degenerate role-vector precheck fails (max pairwise role cosine >= 0.5, analogous to component-1's
  DEGEN_COS=0.90 guard but for roles instead of items); OR frozen baseline saturates the corrected
  held-out task (>= 0.85, reusing 29556's FROZEN_SAT guard) making the test vacuous.

### Controls / diagnostics carried over unchanged from 29556 (do not re-derive)

Near-degenerate item-vector precheck, coarse-before-fine ordering check, sigmoid-vs-linear AIC shape
diagnostic, glass-box bottleneck/bound-vector separation logging, deterministic seeding
(`numpy.random.default_rng`, sorted iteration, no builtin hash), atomic metrics write, CELL-TEMPLATE
compliance (start-marker, heartbeat, crash-diagnostic, no-BaseException).

## Cheap decisive test

Fully local, CPU-only, foreground (inherits 29544/45/46/29556's contract: GloVe/WordNet data is
git-ignored/large, not remote-portable). Estimated cost: ~1-2 hrs -- this is a small extension of an
already-built and already-smoke-tested cell (new bind step + one linear-regression readout in place of
the existing 2-layer MLP; the DOMAINS/RELATIONS/encoder/precheck/shuffled-control machinery is 100%
reused). The single new piece of infrastructure is the corrected held-out split (3a), which is a pure
function of already-present domain/relation metadata (no new data needed) and should be built FIRST and
unit-checked (assert held pairs are ONLY the four named category-correlated relations, with coverage
guards) before the native-binding arm is run, since a wrong split silently invalidates every downstream
number.

## Falsifiable predictions

**HARD-PASS** (would open compositional generalization as a demonstrated substrate-native capability):
- Native-binding `ho_lift` >= 0.25 over frozen on the corrected category-correlated-only held-out split.
- Flat-MLP baseline, RE-MEASURED on the same corrected split, stays < 0.10 (confirms a real test).
- Shuffled-trained/true-eval control for the native-binding arm stays within 0.12 of its exposure-0
  value (rules out leak/memorization as the source of any lift).
- (secondary) bind-then-MLP-readout diagnostic arm shows LOWER `ho_lift` than the linear-readout arm --
  would confirm the mechanism is specifically "unconstrained nonlinear entanglement after combination,"
  not merely representation format.

**HARD-FAIL** (would mean fixed-algebra binding, alone, does not fix systematicity here):
- Native-binding `ho_lift` < 0.10 on the corrected split.
- Sub-diagnosis required before accepting closure: check role near-orthogonality (max pairwise cosine
  among `role_HV_r` < 0.3) and frozen-baseline-not-saturated (< 0.85) guards both hold; if either guard
  fails, this is a construction bug, not a mechanism refutation -- respec and rerun, do not report as
  HARD-FAIL.
- If HARD-FAIL survives both guards: report the Lake-Linzen-Baroni MLC alternative (meta-learning-for-
  compositionality as a training-regime lever, orthogonal to architecture) as the next-drill candidate,
  per the biology caveat in Section 1.

## Cross-thread synthesis

- **29556 (this drill's trigger):** flat MLP hub, `ho_lift 0.0`, structural. This note's design is the
  direct, pre-planned-in-29556's-own-docstring successor ("genuine compositional differentiation
  belongs to the SEPARATE native-bind component") -- not a new direction, the ALREADY-FLAGGED next step.
- **29544/45/46/29555 (meaning-representation wall):** held fixed and UNCHANGED here by design -- this
  cell isolates the combination-mechanism variable from the meaning-representation variable that those
  cells closed. If HARD-FAIL survives the guards, it re-implicates the SAME meaning wall (sub-diagnosis
  a above), unifying rather than contradicting that prior thread.
- **research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md Probe 10:** pre-registered P_deflated 0.50
  and HARD-PASS/FAIL bands for compositional RETRIEVAL of already-bound composites (>90%/<70% recall).
  This note's task is COMPLETION (predict an unseen property from item+relation), the harder "decoder"
  problem Probe 10 explicitly flagged as unaddressed. The two results, taken together, would fully close
  out the "is native VSA binding compositionally generalizing in THIS substrate" question across both
  storage/retrieval and generation/completion framings.
- **wave14e hierarchical composition:** orthogonal axis (depth/recursion, not held-out role x filler
  novelty), but shares the general lesson "the non-linearity/cleanup, not raw binding alone, is what
  makes composition systematic" -- here the "cleanup" analog is the single shared linear readout acting
  as a structural, not idiosyncratic, decoder.

## Substrate-product implications

If HARD-PASS: the substrate demonstrates a capability no flat associative learner in this comparison
has -- correctly completing NOVEL item x relation combinations from separately-seen parts, the textbook
systematicity capability. Product framing (per no-papers/product-only convention): "customers can ask
about combinations of entities and attributes never jointly observed in training data, and get correct
answers, because the substrate composes them algebraically rather than needing to have seen every
combination" -- directly the medical/legal/financial novel-code-combination pitch already scoped in
Probe 10's synthesis, now extended from retrieval to generative completion.
If HARD-FAIL (post-guards): reinforces that the richer/grounded-meaning investment (already surfaced to
USER as the strategic fork) is the binding constraint across BOTH the flat and the native-binding
mechanism -- strengthens rather than weakens the case for that investment, and narrows the next
architectural lever to training-regime (meta-learning-for-compositionality) rather than architecture.

## Citations (verified: 6)

1. Fodor, J. & Pylyshyn, Z. (1988). "Connectionism and cognitive architecture: A critical analysis."
   *Cognition* 28(1-2):3-71.
2. Hummel, J. E. & Holyoak, K. J. (1997). "Distributed representations of structure: A theory of
   analogical access and mapping." *Psychological Review* 104(3):427-466. (LISA)
3. Smolensky, P. (1990). "Tensor product variable binding and the representation of symbolic
   structures in connectionist systems." *Artificial Intelligence* 46(1-2):159-216.
4. Hersche, M. et al. (2023/2024). "A neuro-vector-symbolic architecture for solving Raven's
   progressive matrices." *Nature Machine Intelligence* / arXiv:2203.04571. (learned front-end + fixed
   algebra pattern; 87.7% RAVEN / 88.1% I-RAVEN)
5. Lake, B. M. & Linzen, T. & Baroni, M. et al. (2023). "Human-like systematic generalization through a
   meta-learning neural network." *Nature*. (counter-data-point: systematicity via training regime,
   not architecture)
6. Lake, B. M. & Baroni, M. (2018). "Generalization without systematicity: On the compositional skills
   of sequence-to-sequence recurrent networks" (SCAN). arXiv:1711.00350. (background; already in KB via
   Probe 10 / wave14e)

Plus 2 in-repo KB citations reused without re-verification (already verified in their originating
notes): `notes/wave14e_hierarchical_composition_research.md`,
`notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md`.

## P_deflated

Naive P (native-binding hub clears HARD-PASS) ~ 0.65, given strong convergent theory (TPR/LISA/NVSA) and
an already-built, structurally-motivated mechanism. Deflated 0.20 for uncharted regime (no published
precedent for this EXACT item-relation-property-completion task via bind+linear-readout; NVSA solves a
different task -- rule execution over Raven's matrices, not property completion) and novel-synthesis cap
applied.

**P_deflated = 0.45** (HARD-PASS band). Flag: biology-grounded (Fodor-Pylyshyn, LISA, Smolensky TPR --
well-established, high confidence as MECHANISM CLASS); the specific cell design and numeric pre-reg
bands are novel synthesis / engineering extrapolation (moderate-to-low confidence, correctly capped).

Next-drill candidate if HARD-FAIL: Lake-Linzen-Baroni meta-learning-for-compositionality (MLC) as a
training-regime-level (not architecture-level) systematicity lever -- orthogonal field, not yet drilled
in this KB.
