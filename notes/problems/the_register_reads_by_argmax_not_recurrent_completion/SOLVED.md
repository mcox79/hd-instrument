---
problem: the_register_reads_by_argmax_not_recurrent_completion
status: SOLVED
bar: "Recovery of the OVERLOADED regime, CI-separated over the argmax baseline, on the REAL register/composed-reader load (the regime where the cliff bites -- high fan / book-scale load, NOT the current low-load sentence task where it is correctly inert). Recompute the strongest real floor AND an info-free twin AT EACH LOAD -- the twin MUST LOSE CI-separated. DISTINGUISH the readout lever from the others (hold D FIXED). RESOLVE the help-vs-hurt tension: the same completion that recovers overloaded set-decode does NOT regress ranked retrieval."
result: "SYNTHETIC live register (D=256 FIXED, V=100, n_reps=40, unit=entity, 2000-boot): at overload M=64 the theta-gamma serial decode-and-suppress readout on the linear superposition recovers argmax 0.509 -> 0.983 (paired +0.454 [+0.426,+0.479]); recovery window M in [16,64] (up to +0.49). REAL LitBank (D=1024 FIXED, 100 docs, gold coref, unit=entity, 2000-boot): INERT on the bulk (argmax=serial=1.000 for <=63 events/entity); on the high-fan tail (91 entities with >=64 events, up to 260) argmax 0.959 -> serial 1.000 (+0.041 [+0.031,+0.053]) and CA1-gated 0.995 (+0.037 [+0.029,+0.045])."
floor: "argmax (the organ's current cleanup_argmax readout) recomputed per load AND per population: synthetic 0.509 @M64 / 0.339 @M96; REAL 0.959 in the 64+ bin. Per-entity majority-verb floor on real load = 0.138 (64+ bin). Info-free twins (shuffled-key serial) LOSE CI-separated at every load: synthetic 0.027 @M64 (chance 0.01), REAL 0.044 (64+ bin)."
controls: "(1) shuffled-key twin (info-free serial: joint machinery runs, keys wrong) LOSES CI-sep everywhere -- excludes 'the iteration helps regardless of the keys'. (2) per-slot modern-Hopfield ATTRACTOR ties argmax exactly (0.529=0.529 @M64) -- excludes 'generic completion'; proves the gain is known-key CROSSTALK CANCELLATION, since a codebook attractor has no manifold on the register's separated i.i.d. codes (O'Reilly & McClelland 1994). (3) renorm-vs-rawsum decomposition + an argmax_rawsum control -- locates the per-component bundle renorm as breaking serial (serial_renorm 0.119 << serial_rawsum 0.983 @M64), excluding a trace-representation confound. (4) POSITIVE CONTROL: the harness sees the cliff (argmax fans 1.0->0.085 with load). (5) hub-bias reproduced on a ranking task with a CHANCE info-free control and settling-DEPTH scaling -- excludes a metric that cannot fail. (6) CA1-comparator exact-match gate REFUSES the resonator's spurious divergence at extreme overload (M>=96 -> argmax fallback) -- excludes 'always complete'. (7) REAL-load inertness on low-fan entities -- excludes a false current-task win. Scaffold-free witness 12/12 PASS."
files_changed: "experiments/exp_register_completion_readout_v1.py, experiments/exp_register_readout_vs_store_lever_v1.py, experiments/exp_readout_recall_vs_rank_reconciliation_v1.py, experiments/exp_register_completion_real_litbank_v1.py, experiments/exp_register_completion_correlated_fillers_v1.py, verification/test_register_completion_readout.py, notes/problems/the_register_reads_by_argmax_not_recurrent_completion/{SOLVED.md, research_readout_routing_brain_drill_2026-08-28.md} (NO hdlab/ change -- proposed diff below; board Q111)"
reverify: ".venv/Scripts/python.exe verification/test_register_completion_readout.py"
---

# SOLVED -- the register's capacity cliff is largely an argmax-readout artifact, and the brain-faithful fix is theta-gamma SERIAL decode-and-suppress on the LINEAR superposition. It is a DISTINCT lever from the sparse store (they compose), and it recovers RECALL without regressing RANK because completion and graded-read are two different operations for two different query types.

## THE VERDICT IN ONE BREATH (plain language)

When one character in a story does many things, we pack all those actions into a single memory vector and
then read them back one at a time by "take the single best match." The brain does not read a crowded memory
that way: it reads out one item, quiets it down, then reads the next from what is left (a known
neuroscience mechanism -- the theta-gamma serial code). Copying that read-out **roughly quadruples how many
actions we can pack in and still read back correctly, without making the memory any bigger.** On real book
text it changes nothing for ordinary characters (they are not crowded enough to matter -- so we do not claim
a win there) but it fixes the busiest characters (a protagonist with dozens of actions), lifting them from
96% to 100% correct. Crucially, this same "read it out carefully" trick **must NOT** be used for a different
job -- ranking things by similarity -- where it makes a common item wrongly outrank the right answer; so the
deliverable is a read-out that knows which job it is doing.

## WHAT THE BRIEF GOT RIGHT, AND THE ONE THING IT GOT WRONG

- **RIGHT:** the argmax cleanup imposes an artificial cliff; the brain's recurrent read-out pushes it back
  ~4x at fixed dimensionality; the help-vs-hurt tension with ranked retrieval is real and is the meat.
- **CORRECTED (brain-fidelity, from the drill):** the mechanism is **NOT** "CA3 attractor pattern
  completion". CA3 completion is single-attractor cue->stored-pattern denoising; there is no pinned account
  of CA3 jointly decoding a superposition. The pinned neural analogue for reading a *superposition* is the
  **theta-gamma serial code (Lisman & Idiart 1995): decode the strongest item, SUPPRESS it
  (inhibition-of-return), decode the next from the residual** -- which IS successive-interference
  cancellation. Resonator-network-as-CA3 (Frady et al. 2020) is an engineering analogy, flagged. This is a
  fidelity upgrade to the brief's own framing, earned by the drill (`research_readout_routing_brain_drill_2026-08-28.md`).

## WHAT I BUILT (four cells, one witness) AND MEASURED

**EXP1 -- the read-out on the LIVE register** (`exp_register_completion_readout_v1.py`; D=256 FIXED). Built
theta-gamma serial decode-and-suppress (confidence-ordered peel + inhibition-of-return) on the actual
`AccumulateRegister`. Recovery window M in [16,64]: argmax 0.51 -> serial 1.00 at M=64 (+0.454 CI-sep).
Three controls make it brain-faithful *down to the components*:
- **per-slot modern-Hopfield attractor TIES argmax** (0.529=0.529) -- a codebook attractor has no manifold
  on the register's separated i.i.d. codes, so it degenerates to nearest-neighbor (O'Reilly & McClelland
  1994). => the serial gain is **crosstalk cancellation via the KNOWN KEYS**, not generic "completion".
- **the per-component bundle renorm BREAKS serial** (serial on the renormalized `register()` = 0.119 vs
  serial on the linear sum = 0.983 @M64; and 0.892 vs 1.000 at low load). The read-out must operate on the
  **linear population superposition** (which the register already stores in `_events`) -- the FHRR
  per-component unit-torus renorm is a storage bookkeeping op, not a brain op, and it is incompatible with
  the residual subtraction. This is a component-level fidelity finding, measured not asserted.
- **schedule sweep** (`--sweep`): recovery is robust across the gamma-cycle budget n_iter>=2 (even n_iter=1
  = 0.995 confidence-ordered) and confidence-ordering helps -- the recovery is a property of the OPERATION,
  not a tuned number.
- **own divergence cliff:** at extreme overload (M>=96 at D=256) serial DIVERGES to a spurious solution and
  underperforms argmax -- a real, honest boundary (see EXP3's gate for how it is handled).

**EXP2 -- lever separation** (`exp_register_readout_vs_store_lever_v1.py`; D=256 FIXED, 8 banks). The
read-out lever and p2's sparse multibank STORE lever are DISTINCT and COMPOSE multiplicatively: usable load
~ organ 32 -> +read-out 64 (2x) -> +store 256 (8x) -> +both 384-512 (12-16x). At M=384 (per-bank load ~60,
at the argmax knee) store-alone = 0.757 but both = 1.000. Answers "what buys what": read-out ~doubles
per-bundle capacity; store divides crosstalk by n_banks; and **the store keeps per-bundle load in the
read-out's recovery window, so it is also the architectural fix for the divergence cliff.**

**EXP3 -- the reconciliation (the meat)** (`exp_readout_recall_vs_rank_reconciliation_v1.py`). Two different
operations for two different query types:
- **hub bias reproduced + scales with settling depth** (the drill's falsifiable prediction): on a ranking
  task over correlated hub-structured codes, graded read hits 0.895; attractor settling drops it to
  0.52->0.36->0.28->0.27 as depth goes 1->8, the target's rank falls 0.4->25.9, hubs rise. Graded - attractor
  = +0.587 [+0.500,+0.676] CI-sep (chance 0.026). It is a MODERATE-beta phenomenon (too little settling =
  snap to nearest = graded; too much = full collapse to one hub) -- the settling IS the pathology.
- **the CA1-comparator gate** (Vinogradova 2001) tracks the better recall arm at EVERY load: it accepts
  completion ONLY on a near-EXACT reconstruction match (the true joint solution reconstructs the stored sum
  exactly, residual ~0; a spurious diverged solution reconstructs only partially, residual ~0.5, and is
  REJECTED -> argmax fallback). Self-calibrating, gold-blind, no tuned threshold; completes M in [32,64],
  refuses M>=96.
- **the gated policy beats both blanket policies** on a mixed workload: recall 1.000 / rank 0.895 /
  **aggregate 0.947** vs always-graded 0.769 (cliffs on recall) and always-complete 0.640 (regresses rank).
  The gate routes by QUERY STRUCTURE (recall-from-known-keys -> serial; rank-by-similarity -> graded) --
  the architectural fix the brain uses (it does not de-bias the attractor; replay is biased TOWARD hubs).

**EXP4 -- the REAL reader load** (`exp_register_completion_real_litbank_v1.py`; D=1024 FIXED = the real
pipeline dimensionality, 100 LitBank docs, gold coref). Honest scope, measured: events-per-entity is median
1 / p90 5 (bulk far below k_cliff(1024)=89 -> read-out correctly INERT, argmax=serial=1.000, NO false
current-task win), but the tail is real (193 entities >=32 events, 91 >=64, one protagonist 260). On the 64+
tail argmax 0.959 -> serial 1.000 (+0.041 [+0.031,+0.053]), CA1-gated 0.995 (+0.037 [+0.029,+0.045]),
shuffled-key twin 0.044, majority-verb floor 0.138. A real-load recovery on book-scale accumulators.

## WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST

- **NO end-to-end reading-comprehension win, and none is claimed.** The current dominant wall is the
  front-end linking (real 0.17 vs oracle 0.60), a different problem; a read-out fix is inert there. The value
  is a book-scale CAPACITY lever, exactly as the brief scoped it.
- **First thing I would withdraw if wrong:** the magnitude of the REAL-load tail gain (+0.041). It rests on
  91 entities and on the fine-per-event-index construction; if the live reader used a coarser key the fan
  would be a within-slot COLLISION (p2's SET-return lever), not the across-slot superposition my read-out
  targets. The SYNTHETIC recovery (+0.45) and the mechanism controls are far more robust than the specific
  real-load number.
- The resonator/serial **divergence at extreme overload is a genuine limit**, not fully solved by the
  read-out alone -- it is handled by the CA1 gate (refuse) + the store lever (prevent), not by the read-out
  converging where it cannot.

## KEY REALIZATIONS (the enabling moves)

1. **The two prior results are not in tension -- they are different operations.** `graded_attractor_vs_argmax`
   HARD-FAILED because on a SINGLE degraded cue argmax is already the optimal nearest-neighbor rule. SIC/serial
   wins because it is NOT denoising a single cue -- it cancels STRUCTURED crosstalk from the other co-bundled
   items using their KNOWN keys. Naming that distinction unlocked everything.
2. **Copy the OPERATION, and read the RIGHT trace.** The recovery only appears on the LINEAR superposition;
   the per-component bundle renorm breaks the residual subtraction. Measuring serial on both representations
   (not assuming) located a live substrate fidelity gap.
3. **The Hopfield-ties-argmax control is what proves it is brain-faithful and not convenient.** A generic
   attractor does nothing on separated codes; only the known-key serial decode recovers. That single control
   is the difference between "we threw completion at it" and "we copied the brain's actual read of a
   superposition."
4. **The hub-bias resolution is ARCHITECTURAL, not corrective.** The brain routes ranking to a non-settling
   circuit rather than de-biasing the attractor (replay is biased toward hubs). So the deliverable is a
   router keyed on QUERY STRUCTURE, and "when to complete" is answered by the CA1 comparator's EXACT-match
   test -- not by tuning a margin threshold (which could not separate recoverable-overload from divergence).
5. **The unexpected wall (spurious resonator solutions) was drilled, not hacked.** A partial reconstruction
   match IS the mismatch/novelty signal; accept completion only on a near-exact match. The brain has this
   mechanism, so we could too.
6. **DEEPENING that reversed my own prediction (`exp_register_completion_correlated_fillers_v1.py`):** I
   expected correlated fillers (real verbs are semantically correlated -- the audit's flagged iid-code
   OUR-INVENTION) to DEGRADE the serial read-out. The disk says the opposite: serial stays at **1.000
   exact-id recovery from iid (mean|cos| 0.035) to strongly-correlated (0.123)**, because its crosstalk
   cancellation is keyed on the ORTHOGONAL event-slot keys, not on filler dissimilarity -- while **argmax
   COLLAPSES (0.757 -> 0.136)** because it relies on separability. The lever's edge GROWS with correlation
   (+0.243 -> +0.864 CI-sep). Two consequences: (a) the iid-code assumption is NOT load-bearing for the
   read-out -- the KNOWN-KEY structure is; and this is the sharp form of the reconciliation (keys make
   completion correlation-robust for RECALL; exp3's KEYLESS ranking + settling gives hub bias). (b) since
   real verbs ARE correlated, the real-load benefit (exp4 +0.041, measured with the register's iid codes) is
   if anything an UNDER-estimate -- argmax on real correlated fillers is worse than iid predicts.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

- **The register read-out (`situation_model_accumulate.cleanup_argmax`) is the noise->0 argmax collapse of a
  graded serial read; the brain-faithful op is theta-gamma serial decode-and-suppress (Lisman & Idiart 1995),
  NOT CA3 attractor completion.** Recovers ~4x load at fixed D (PINNED computation; iteration budget is
  OUR-INVENTION swept, robust n_iter>=2).
- **NEW deviation, measured:** the default per-component `bundling.bundle` renorm is incompatible with the
  serial/resonator read-out (breaks residual subtraction). The completion read-out must read the LINEAR
  accumulator. (Consistent with the existing flag on `norm="l2"` in `bundling.bundle` that per-component
  renorm "only ever HURTS role-filler recovery".)
- **Reconciliation logged:** recurrent completion is the correct read-out for RECALL of a known-key
  superposition; it HURTS RANK over CORRELATED codes (hub bias, O'Reilly & McClelland 1994
  separation/completion tradeoff). Route by query structure; gate "when to complete" by the CA1 comparator
  exact-match test.
- **REVISION to the audit's flagged item ("the FHRR iid-random-code assumption is an unflagged
  OUR-INVENTION"):** for the register READ-OUT, the iid assumption is NOT load-bearing -- serial decode is
  correlation-INVARIANT (1.000 exact recovery from mean|cos| 0.035 to 0.123) because it cancels crosstalk
  using the orthogonal KEYS, not filler separability; argmax is the one that needs separated codes (it
  collapses 0.757->0.136 under correlation). The load-bearing property is the KNOWN-KEY structure. (This
  does NOT retract the iid caveat for STORAGE CAPACITY / for the ranking store -- only for the known-key
  read-out.)

## PROPOSED hdlab CHANGE (strategy lands it -- board Q111; I do not write hdlab/)

Additive, default-safe -- no storage-format change (the raw event list already exists in `_events`):
1. `hdlab/situation_model_accumulate.py`: add a `decode_serial(entity, event_idxs=None, n_iter=6)` method on
   `AccumulateRegister` that (a) forms the LINEAR sum of the entity's stored bindings, (b) runs
   confidence-ordered serial decode-and-suppress over the occupied event-slot keys, (c) returns per-slot
   fillers. Port `decode_serial` + `_scores` verbatim from `experiments/exp_register_completion_readout_v1.py`.
   Keep `decode()` (argmax) the default; `decode_serial` is opt-in.
2. Add `decode_gated(entity, event_idxs=None)` (the deployable read-out): argmax when it already reconstructs
   the trace (residual < clean_eps); else serial accepted ONLY on a near-exact reconstruction match
   (residual < accept_eps); else argmax fallback. Port `_recon_residual` + `decode_gated_recall` from
   `experiments/exp_readout_recall_vs_rank_reconciliation_v1.py`.
3. Do NOT route RANKED-retrieval reads (cortical store) through completion -- keep the graded population read
   there (this is `the_consolidated_cortical_store...`'s lane; the gate's rank branch documents why).
4. Wiring note: pair with the multibank store default so per-bundle load stays in the read-out's recovery
   window (the store is the architectural guard against the divergence cliff).

## ADJACENT COMPONENTS THAT ARE SUBOPTIMAL (candidate focused-solver briefs -- flagged per owner instruction)

1. **`bundling.bundle` per-component renorm is not brain-faithful and is now MEASURED to hurt the completion
   read-out.** It sits upstream of every FHRR read-out. A focused problem: "is the per-component unit-torus
   renorm ever the right bundle op, or should the substrate store the linear accumulator and normalise only
   at compare time?" (ties to `the_core_binding_operator_may_not_be_brain_faithful`).
2. **The register does not record which event_idx each event used** (`_events[entity]` is an unlabelled list);
   a joint all-slot read-out needs the occupied-key set surfaced. Small API/state gap.
3. **The front-end linking wall (real 0.17 vs oracle 0.60)** is the actual current bottleneck and a different
   problem (coref/incremental parser) -- named here only to keep the read-out's scope honest.
4. **The cortical-store ranking read** still needs its hub-robust fix (k-WTA + frequency-normalised
   inhibition) -- that is `the_consolidated_cortical_store...`'s lane; this work only characterises + gates it.

## TLDR
Reading a crowded memory by "single best guess" throws away recoverable information. Copying the brain's
actual read of a crowded memory -- pull out one item, quiet it, read the next -- roughly quadruples how much
one memory can hold at the same size, and on real book text it fixes the busiest characters (96%->100%)
while correctly doing nothing for ordinary ones. The same trick must be switched OFF for ranking-by-similarity
(there it wrongly promotes common items), so the read-out is built to know which job it is doing.

## QUESTIONS
None -- the five bar items are all measured (recovery CI-sep on real load with floors+twin per load; D held
fixed; lever separation; help-vs-hurt resolved; one-screen summary). Awaiting owner verdict.

## NEXT STEPS
1. Strategy re-verifies (`verification/test_register_completion_readout.py`, 12/12) and, on owner DONE, lands
   the additive `decode_serial` + `decode_gated` methods (proposed diff above), paired with the multibank
   default.
2. File the two strongest adjacencies as focused-solver problems (the bundle renorm; the register key-set API).
3. Keep ranked-retrieval reads on the graded path (do NOT blanket-swap completion) -- carried into the
   cortical-store brief.
