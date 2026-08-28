---
problem: the_register_bundle_renorm_breaks_the_serial_readout
status: SOLVED
bar: "A brain-faithful normalization for the superposition register (copy divisive/homeostatic normalization; sweep the pool/gain) that PRESERVES the serial-readable linear structure: the theta-gamma serial readout on the normalized register recovers the overloaded regime CI-separated over the current per-component renorm (serial_renorm ~0.12 -> target ~raw-sum), recompute per load; an info-free twin LOSES CI-separated; report CI half-width + null p95; a positive control that the harness sees the renorm break the readout; NO REGRESSION on the argmax cleanup + write stability."
result: "Pooled DIVISIVE normalization (Carandini-Heeger / homeostatic) of the register bundle + a gain-matched serial readout RECOVERS the overloaded register to the raw-sum ceiling: per-slot filler-recovery accuracy @M=64 (D=256 FIXED, V=100, n=30 entities/load, synthetic controlled-load AccumulateRegister) serial:per-component 0.325 -> serial:divisive 1.000, headline +0.675 CI-sep [+0.646,+0.703] hw 0.028; recovery window M={48,64,96,128}; divisive TIES raw-sum at every load (delta<0.001)."
floor: "Strongest floor actually run = the LIVE organ's own per-component renorm store read by the SAME gain-matched readout, serial 0.325 @M64 (and the current organ end-to-end argmax-on-per-component 0.512 @M64, worst-arm); info-free shuffled-key twin 0.029 @M64 (twin_null_p95 per load); chance 0.01."
controls: "(1) POSITIVE CONTROL -- per-component store under the BEST (gain-matched) readout still cannot recover (0.325 vs 1.000): isolates the STORE norm, not the readout, as the constraint, and the harness sees the renorm break at M>=48 while M=8 is fine. (2) SCALE-INVARIANCE -- scalar-norm argmax bit-identical to raw-sum argmax (diff<1e-6): excludes an argmax regression. (3) INFO-FREE TWIN -- shuffled-key serial 0.029 LOSES CI-sep (excludes machinery-without-keys). (4) NAIVE-vs-GAIN-MATCHED -- naive serial on an L2 store 0.117 << gain-matched 0.988 (excludes 'any readout works'; store & readout normalization must MATCH). (5) PARAMETER SWEEP -- serial flat (=1.000) across C-H sigma {0..64} and homeostatic target {0.1..100}: excludes a tuned constant."
files_changed: "experiments/exp_register_divisive_norm_v1.py, verification/test_register_divisive_norm.py, notes/problems/the_register_bundle_renorm_breaks_the_serial_readout/SOLVED.md, notes/problems/the_register_bundle_renorm_breaks_the_serial_readout/ADJACENT_COMPONENTS_brain_fidelity_map.md"
reverify: ".venv/Scripts/python.exe verification/test_register_divisive_norm.py"
---

# SOLVED: the per-component bundle renorm is the non-brain-faithful choice; a POOLED divisive normalization serves BOTH readouts

## The one-screen summary

```
normalization (of the SAME stored bindings)  ->  serial recovery  ->  argmax no-regression  ->  verdict
  per-component  S_i/|S_i|   (INCUMBENT organ)     BREAKS  (0.325 @M64, best readout)   0.512 (organ)     the OUR-INVENTION outlier
  divisive/pooled S/(sigma+mean|S|) (Carandini-Heeger)  RECOVERS (1.000 @M64, ties raw)  0.644 (+0.096)   BRAIN-FAITHFUL, serves both
  homeostatic     S*target/RMS(S)   (Turrigiano)         RECOVERS (1.000, param-flat)     0.644            BRAIN-FAITHFUL, serves both
  L2 / RMS        S/||S||  /  S/RMS(S)                    RECOVERS (1.000)                 0.644            pooled-scalar members
  raw-sum         S  (ceiling, but UNBOUNDED in M)        RECOVERS (1.000)                 0.644            reference, not a legit stored state
```
**One divisive normalization serves both readouts; NO raw-sum shadow copy is needed.** The per-component renorm is the
single member of the normalization family that is NOT a pooled/scalar gain, and it is the one that breaks the serial readout.

## What the brain does (PINNED) vs what we built (OUR-INVENTION)

- **PINNED (the computation):** a cortical/hippocampal population SUMS its inputs (linear superposition on the
  dendrite) and controls magnitude by **DIVISIVE NORMALIZATION** -- dividing the summed response by a **POOLED gain**,
  one scalar over the normalization pool (Carandini & Heeger 2012, the canonical cortical computation) -- and by
  **homeostatic synaptic SCALING**, a slow global multiplicative rescale toward a target activity level (Turrigiano
  2008). Both are **pooled / scalar** gains. A scalar divisor is a global rescaling: it preserves the relative/linear
  structure exactly, so the strongest component stays largest and suppress-and-repeat still decodes. VSA/HDC theory
  agrees (Plate 1995; Kanerva 2009): bundling is addition; normalization is a scalar/divisive step.
- **OUR-INVENTION-UNDER-TEST (the suspect, now confirmed):** the register's **per-component renorm** `S_i/|S_i|`
  (`hdlab/bundling.py` default, the FHRR unit-torus projection). It divides each dimension by *its own* magnitude --
  a nonlinear, **non-invertible** per-component distortion. Its only legitimate role is torus-closure so an atom can be
  **re-bound**; a register trace is a **terminal readout, never re-bound**, so per-component renorm is unjustified here.
- **The fidelity question the brief posed -- answered POSITIVELY:** a divisive/homeostatic (pooled) normalization
  serves **BOTH** the argmax cleanup path AND the theta-gamma serial readout. Per-component renorm is *not* required for
  either; it is strictly worse for both. No principled either/or -- the same normalization does both jobs.

## RESEARCH VERIFICATION (two adversarial literature drills, 2026-08-28 -- "use research liberally to verify")

I did not rest on cited-from-memory claims; two drills were tasked to REFUTE the mechanism. Result: the claim survives,
with the labeling SHARPENED (this is the PINNED-vs-OUR-INVENTION discipline done properly):
- **Pooled divisive normalization is DIRECTLY CONFIRMED** in sensory + decision/value cortex (Carandini & Heeger 2012;
  Louie & Glimcher 2011/2017, LIP/OFC) -- the divisor is genuinely a POOLED quantity (shared scalar, preserves relative
  ratios). Its application to a hippocampal/WM *memory register* is a **STRUCTURALLY-MOTIVATED EXTENSION BY ANALOGY**,
  not a recorded hippocampal circuit -> labeled **OUR-EXTENSION-UNDER-TEST**, not PINNED. The closest direct precedent
  for a *pooled bundle renormalization* is Eliasmith's NEF/SPA near-unit-radius semantic pointers and Frady/Kleyko/
  Sommer 2018 (bundle capacity ~4, normalization/thresholding sets retrieval SNR) -- both a POOLED/global constraint.
- **The per-component objection is REFUTED, strengthening the negative half:** Turrigiano homeostatic scaling is slow
  (hours), weight-level, and uniform-multiplicative (PRESERVES relative ratios) -- it argues *for* structure-preservation,
  not for per-component renorm. The nearest per-cell divisive mechanism (photoreceptor/olfactory adaptation) is
  history-based and structure-preserving. **No fast biological mechanism performs instantaneous per-component magnitude
  erasure (`S_i/|S_i|`)** -> "don't renormalize per-component" is well-grounded; "use pooled divisive normalization" is
  the faithful analogy, labeled as such.
- **The per-component-vs-pooled distinction itself is NOT a term of art in the VSA/HDC primary literature** (Plate,
  Kanerva, Eliasmith, Frady) -> OUR-INVENTION-UNDER-TEST as a *framing*, even though each side's biology is as above.

## What I built (experiments/ only -- no hdlab write, per Q111)

Two **matched** pooled-normalization steps (the brain applies divisive normalization at BOTH store and readout):
1. **STORE** (`apply_norm` in the cell): `bundle -> S / g_pooled` where `g` is a scalar -- L2 / RMS / Carandini-Heeger
   `sigma+mean|S|` / homeostatic `target/RMS` -- instead of the per-component `S_i/|S_i|`.
2. **READOUT** (`decode_serial_pooled`): the theta-gamma serial decode-and-suppress made **scale-equivariant** by a
   single least-squares **pooled gain** `g = <trace,total>/<trace,trace>` per iteration (itself a divisive-normalization
   step -- one scalar over the whole vector). On the raw sum g~=1, so it reduces to the landed `decode_serial` exactly.

## What I measured (D=256 FIXED, V=100, per-slot filler-recovery accuracy, bootstrap CI over entities)

| M | argmax:percomp (organ) | argmax:divnorm | serial:percomp | serial:divnorm | serial:rawsum | twin | divnorm-percomp serial |
|---|---|---|---|---|---|---|---|
| 8  | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.117 | +0.000 |
| 32 | 0.824 | 0.923 | 1.000 | 1.000 | 1.000 | 0.046 | +0.000 |
| 48 | 0.648 | 0.775 | 0.740 | 1.000 | 1.000 | 0.031 | **+0.260** [+0.185,+0.331] |
| 64 | 0.512 | 0.643 | 0.325 | **1.000** | 1.000 | 0.029 | **+0.675** [+0.646,+0.703] hw0.028 |
| 96 | 0.338 | 0.429 | 0.182 | 0.296 | 0.296 | 0.016 | +0.114 [+0.083,+0.144] |
| 128| 0.245 | 0.320 | 0.128 | 0.187 | 0.187 | 0.011 | +0.059 [+0.047,+0.073] |

- **Serial recovers CI-separated over the per-component store** in the window M={48,64,96,128}; at M=64 the readout goes
  0.325 -> 1.000 (the store is the ONLY variable changed).
- **Divisive TIES the raw-sum ceiling at every load** (delta<0.001): a pooled/scalar norm loses nothing vs the unbounded
  raw sum -- and unlike raw-sum it is a *bounded, legitimate stored state* (its homeostatic purpose).
- **Argmax NO-REGRESSION at every load** -- in fact **improves** (0.512 -> 0.644 @M64, +0.096 CI-sep lo): a scalar norm
  gives argmax the raw-sum's decisions (scale-invariant, bit-identical), which the prior
  `the_core_binding_operator_may_not_be_brain_faithful` already showed beat per-component 32/32.
- **Info-free twin loses** (0.029 vs 1.000 @M64). **Parameter-flat**: serial=1.000 across C-H sigma and homeostatic
  target -- the recovery is a property of the OPERATION, not a tuned number.
- **MEASURED ON THE DEFAULT BACKEND, IN THE COMPOSE REGIME (witness N8).** `make_situation_register` defaults to
  `MultiBankAccumulateRegister`, whose `decode()` reads a per-BANK bundle (same `bundling.bundle` per-component renorm)
  at a smaller per-bank load. Distributing M=384 events across 8 banks (k_per_bank~60, an overloaded bank), the norm fix
  recovers the per-bank serial readout **0.733 -> 1.000 (+0.293 CI-sep, hw~0.02)** and improves argmax **0.654 -> 0.765**.
  So the p2 store lever (distribute load) and this norm fix **COMPOSE**: the store makes per-bank load tractable, the norm
  fix makes each bank serial-readable. This is the 12-16x compose the brief names -- now measured with the norm fix in
  place, not inferred from "same code path."

## What I did NOT establish (and would withdraw first if wrong)

- **The M>=96 regime is a TRUE capacity bound, not a normalization win.** At M={96,128} divisive serial = raw-sum serial
  = 0.296/0.187 -- the resonator's own DIVERGENCE (the parent problem's finding: extreme overload exceeds the readout's
  capacity; that is the p2 STORE-distribution lever, not this problem). There, `argmax:divnorm` (0.429/0.320) actually
  *beats* serial. So the honest claim is: **the store-norm fix recovers the register wherever the serial readout is
  viable (the M=48-64 window: 0.512 -> 1.000), and is a strict argmax win at ALL loads incl. M>=96.** It does not defeat
  the resonator's intrinsic capacity limit -- nothing about normalization could. **First thing I'd withdraw** is any
  reading that divisive normalization "fixes overload at M>=96"; it fixes the *readability of the linear structure*, and
  distributing load past the resonator's capacity is the sparse-store's job.
  **Research drill B located this precisely in the brain's subsystem architecture, and it is a stronger frame than
  "capacity bound":** whether normalizing a dense bundle is brain-faithful DEPENDS on the subsystem. Under a WORKING-
  MEMORY reading (bounded, few items -- the register's operating regime; theta-gamma holds ~7+-2, Frady bundle capacity
  ~4) normalization IS the load-bearing lever (Eliasmith near-unit-radius; Frady capacity-SNR). Under an EPISODIC/LTM
  reading (many items) the brain does NOT hold a dense normalized bundle at all -- it PATTERN-SEPARATES (sparse DG ~2-4%)
  before combining (Marr 1971; Treves & Rolls 1994 capacity ~N/(a ln 1/a) collapses as a->dense; O'Reilly & McClelland
  1994; Yassa & Stark 2011; Norman & O'Reilly 2003 CLS). **My measured M-transition IS that subsystem boundary:**
  normalization recovers the register in the WM regime (M<=64), and the M>=96 divergence is exactly where the faithful
  answer switches to sparse separation (p2). So the fix is brain-faithful *for the WM register it operates on*, and it
  does not -- and should not -- try to be the episodic-storage mechanism.
- **Real-narrative (LitBank) load is inherited, not re-measured here.** The effect is a pure algebraic property
  (a scalar rescale preserves the linear sum; a per-component one does not), demonstrated on controlled load. The parent
  `the_register_reads_by_argmax_not_recurrent_completion` already showed serial on the raw linear sum recovers the real
  high-fan tail (D=1024, 91 entities >=64 events: 0.959->1.000). Since divisive serial == raw-sum serial (proven here),
  the real-load recovery transfers. I did **not** re-run the D=1024 LitBank arm (it would re-derive a landed parent
  result); a strategy re-verify could add it cheaply if wanted.
- **"Write stability" is moot for this architecture, not proven robust under a different one.** `AccumulateRegister`
  is stateless: `add_event` appends to a Python list and `register()` re-bundles the whole list *fresh* every read, so
  no normalized state is ever stored-and-compounded -- there is no in-place write that could drift. The load sweep IS
  the stability evidence (decode quality vs accumulated events). If a future variant caches a normalized register
  incrementally, stability would need re-checking there.

## KEY REALIZATIONS (the enabling moves)

1. **The distinction that unlocked it: POOLED (scalar) vs PER-COMPONENT normalization.** Carandini-Heeger divisive
   normalization divides by a *pooled* quantity -- **one scalar shared across the population** -- which is a global
   rescaling that preserves linear structure. The register's renorm divides each component by *its own* magnitude. Same
   word ("normalize"), opposite effect on serial decodability. Naming that split made the fix obvious and the control
   sharp.
2. **A scalar norm makes the readout invariance FREE.** Argmax is scale-invariant, so a scalar-normalized store gives
   *bit-identical* argmax to the raw sum -- I could prove no-regression by identity, not just by CI. The serial readout
   needed only a one-line pooled-gain estimate to become scale-equivariant.
3. **The best readout as a positive control.** Giving the per-component store the *gain-matched* readout (not the naive
   one) took its serial from 0.119 -> 0.325 and it STILL failed (vs 1.000). That is stronger evidence than the brief's
   0.119: even the best possible readout can't rescue a per-component-distorted store -> the constraint is the STORE norm.
4. **Store and readout normalization must MATCH.** Naive serial on an L2 store scores 0.117 (the trace's scale != the
   reconstruction's scale) -> 0.988 once gain-matched. The brain gets this for free: divisive normalization is applied at
   *both* stages, so they are consistent by construction. The bug was a per-component store feeding a linear-structure
   readout.
5. **Sweep proved the OPERATION, not the number.** Serial = 1.000 flat across every sigma and target because
   gain-matching removes any global scalar. Copy the computation (pooled division); the parameter is irrelevant.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- strategy folds in)

- The §2b **register-readout** entry's "New fidelity wall: the register's per-component BUNDLE RENORM is
  non-brain-faithful -- it breaks the serial readout" is **RESOLVED, not just flagged**: the brain-faithful
  normalization is **pooled divisive normalization** (Carandini-Heeger 2012) / homeostatic synaptic scaling (Turrigiano
  2008) -- a scalar gain that preserves the linear structure -- and it recovers the serial readout to the raw-sum ceiling
  while *improving* the argmax path (no raw-sum shadow copy needed). Promote the wall from OPEN to
  **MECHANISM-IDENTIFIED-AND-BUILT (proposed hdlab diff pending strategy landing)**.
- Sharpen the standing **per-component-normaliser** verdict (audit line ~1089, "L2/raw-sum beat per-component 32/32"):
  the per-component renorm is now shown to break not only argmax-cleanup fidelity but the **linear/serial** structure --
  its correct scope is **torus-closure for RE-BINDING an atom only**; a *terminal superposition register* should use a
  pooled divisive norm. This is a general substrate rule: **every bundle store that is READ (not re-bound) should
  normalize by a pooled scalar, never per-component.**
- **LABELING (from research verification):** record the register-normalization mechanism as
  **OUR-EXTENSION-UNDER-TEST**, not PINNED -- pooled divisive normalization is confirmed in sensory/decision cortex and
  extended by analogy to the WM register (direct pooled precedent: Eliasmith NEF/SPA near-unit-radius; Frady/Kleyko/
  Sommer 2018). The NEGATIVE (per-component instantaneous renorm has no fast biological analogue) is well-grounded.
- **SUBSYSTEM BOUNDARY (a durable framing the audit should carry):** dense-bundle normalization is brain-faithful under
  the **working-memory** reading (bounded items, the register regime); under an **episodic/LTM** reading the brain
  pattern-separates (sparse DG) rather than normalizing a dense trace. The register's measured M-transition (norm
  recovers at M<=64; resonator diverges at M>=96) IS that WM->episodic boundary -- so the norm lever (this problem) and
  the sparse-store lever (p2) are the SAME dichotomy the CLS literature draws (Norman & O'Reilly 2003), and they compose.
- **ADJACENCY MAP:** a general substrate audit -- `bundling.bundle`'s per-component default is sub-optimal for its ENTIRE
  measured read-terminal consumer set, and the `sign()`-on-a-bundle sites are the same wrong-op -- is written up in
  `ADJACENT_COMPONENTS_brain_fidelity_map.md` (this folder). Fold its candidate follow-ons into the audit's gap list.

## Proposed hdlab diff (strategy lands it -- Q111; I do NOT write hdlab/)

1. **`hdlab/bundling.py::bundle`** -- add a pooled divisive-normalization option (default-off, byte-identical when off).
   The `norm="l2"` branch already exists; add `norm="divnorm"` (Carandini-Heeger pooled) and keep the per-component path
   as the default for **re-bound atoms**:
   ```python
   # in the complex branch, alongside the existing norm=="l2":
   elif norm == "divnorm":                     # pooled divisive normalization (Carandini-Heeger 2012); scalar gain
       pooled = s.abs().mean()                 # one scalar over the pool
       out = s / (DIVNORM_SIGMA + pooled).to(s.dtype)   # DIVNORM_SIGMA default 0.0 -> RMS-like; swept, not adopted
   ```
2. **`hdlab/situation_model_accumulate.py::AccumulateRegister`** (and `situation_model_multibank.py`, which also calls
   `bundling.bundle` at lines 114/145) -- thread a `bundle_norm="percomp"` constructor arg into the `register()` /
   `_bank_register()` bundle calls. Default `"percomp"` keeps every current caller bit-identical; `"divnorm"` opts a
   register into the serial-readable, argmax-improving, bounded normalization.
3. **`hdlab/situation_model_accumulate.py`** -- add `decode_serial_pooled` (the gain-matched serial readout from the
   cell) as an additive method, so a `bundle_norm="divnorm"` register can be read by the theta-gamma serial path. Pairs
   with the parent problem's queued `decode_serial`/`decode_gated`; the gain-matching makes them store-norm-agnostic.
   `cleanup_argmax` / `decode()` stay the default readout and are unaffected (scale-invariant).

**Landing risk (stated against myself):** `norm="divnorm"` requires the coupled readout to be gain-aware (bar N6) --
landing the store option WITHOUT the gain-matched readout would *break* any serial caller that assumed raw scale. Land
them together, and keep `bundle_norm` default `"percomp"` so no existing caller changes until explicitly opted in.

## Adjacent components flagged to strategy (candidate follow-ons, with on-disk leverage)

- **The M>=96 resonator DIVERGENCE = the sparse-store lever (p2).** The store-norm fix takes serial to the raw-sum
  ceiling but that ceiling itself falls at extreme overload (0.296 @M96) -- a *true* capacity bound. Distributing load
  (multibank / sparse DG) is what raises it; this problem and p2 COMPOSE (parent measured 12-16x). Not mine to build,
  but the norm fix is a prerequisite for the compose to be serial-readable.
- **Every OTHER bundle store that is READ, not re-bound, inherits this bug -- NOW MAPPED (owner asked to evaluate
  adjacent components).** I enumerated `bundling.bundle`'s callers and classified them by consumption in
  `ADJACENT_COMPONENTS_brain_fidelity_map.md`: **all enumerated callers are READ-terminal** (`situation_model_multibank`,
  `selection_weighted_sharded_typer`, `script_grain_acquisition_loop`, `goal_achievement` via unbind+cleanup;
  `lexical_similarity`/`verb_lexical_similarity`/`quality_relation` via cosine) -- I found NO caller that re-binds the
  bundle, so the per-component default is sub-optimal for its whole consumer set. My witness N3 (argmax:divnorm >=
  argmax:percomp at every load) is the general evidence for the cleanup_argmax family; the cosine-readout consumers need
  their own probe (a distinct readout). The `sign()`-on-a-bundle sites (`grounding_acquisition_loop`, `situation_focus`,
  `role_slot_summarizer`, `event_bundle`; audit lines ~1001/1176) are the SAME wrong-op in a bipolar code -- one "pooled
  divisive normalization at read-terminal bundles" principle covers both families. Ranked candidate follow-ons are in the map.

## TLDR (plain language)

The memory that holds "who did what" in a scene stacks many facts into one signal, then rescales it. It was rescaling
each channel of the signal on its own -- which quietly destroys the ability to peel the facts back apart one at a time.
The brain rescales the *whole* signal by a single shared amount (this is one of the most established things cortex does).
When I switch to the brain's way, the peel-apart read of an overloaded memory jumps from failing (about a third right) to
essentially perfect, and the simpler read gets a bit better too -- no downside, and it needs no special "shadow" copy.
The exact rescaling amount doesn't matter at all; only *sharing one amount across the whole signal* matters. It stops
helping only once the memory is stuffed so full that no read could untangle it -- and fixing *that* is a different,
already-known job (spreading the load across more sub-memories).

## QUESTIONS

None. The mechanism is identified, built, and CI-separated with the info-free twin losing and a positive control that
the harness sees the break; the one honest limit (extreme-overload capacity) is a different, already-owned lever.

## NEXT STEPS

1. Strategy re-verifies `verification/test_register_divisive_norm.py` (7/7) and lands the proposed diff -- the two
   normalization steps TOGETHER, `bundle_norm` default `"percomp"` (opt-in), per the landing-risk note.
2. Fold the AUDIT UPDATE into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (wall RESOLVED) and the per-component-normaliser
   line (scope = re-bound atoms only).
3. Consider filing the "read-terminal bundle-store norm audit" as a small follow-on (map every `bundling.bundle` caller;
   switch the read-terminal ones to pooled divisive norm) -- a general substrate hygiene win the register result generalizes to.
