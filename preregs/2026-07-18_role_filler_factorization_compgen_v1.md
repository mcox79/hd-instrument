# Pre-reg: role_filler_factorization_compgen_v1 (COMPONENT-1 of the learned reader)

Filed 2026-07-18 (exp_dev, local foreground mechanism-proof). Cell:
`experiments/exp_role_filler_factorization_compgen_v1.py`. NO queue dispatch (glass-box CPU,
seconds). CLAIM-VET-pending (skunkworks landed-VET before treating as fact).

## Question
Does a brain-faithful STRUCTURE-CONTENT FACTORIZATION -- a content-blind structural role-scaffold
g (TEM-style, LEARNED here via Hebbian averaging, NOT hand-assigned) bound to grounded content x
via native FHRR conjunctive binding -- generalize to HELD-OUT (role, filler) combinations where a
flat / memorization baseline FAILS?

## Prior-work check (substrate_query "compositional generalization held out combination structure
content factorization role binding TEM")
Top hits at cosine>0.30 are all NOTES/research-drills, NOT prior CELLS: `Compositional
generalization` (0.533, wave14e note), `3.2 TEM structural-sensory factorization` (0.483, brain
drill 3 note). NO prior experiment cell tests held-out-combination role-binding with native bind
vs flat. This cell is GENUINELY NOVEL as a cell (first role-binding compositional-generalization
discriminator); it builds on the 07-18 brain-drill design (credited) and the arc's prior TEM
notes. Not a rediscovery.

## Honest scoping (load-bearing)
SYNTHETIC MECHANISM-PROOF (like k-parity atom 29329), NOT a real-text capability and NOT
chain-grade. A PASS proves the mechanism (native structure-binding + learned content-blind g gives
compositional generalization IN PRINCIPLE) and justifies the real-text build. Do NOT over-read a
synthetic pass as capability. Random content codes; enumerable roles; supervised generative model.

## Design gate (pre-registered; verified at smoke BEFORE full)
- REAL baseline = ARM_FLAT: per-role content-prototype associative memory over bag-of-content
  (no role-filler binding). Canonical flat/memorization baseline; failure is STRUCTURAL (no
  binding), matching COGS flat-architecture failure. Not abstain-all, not artificially weakened.
- CAN-FAIL-BOTH-WAYS: FACTORED can GENERALIZE (held-out ~ in-dist, >> flat) OR TIE flat (crosstalk
  at the regime kills the learned-g readout, or learned g leaks filler identity). The D=2 low-data
  point (FACTORED vocab held-out 0.738, NOT saturated) and the m=32 capacity cliff both show
  FACTORED CAN underperform -> not by-construction pass.
- DIFFICULTY ON: held-out (role,filler) pairs are provably unseen in training (asserted in
  build_split: every held-out filler stays trainable in >=1 OTHER role = grounded; every role has
  trainable + held-out fillers). COGS "primitive seen, combination novel" condition.
- ONE VARIABLE: FACTORED (learn role-key g_hat, bind role(x)filler, readout by unbind) vs FLAT
  (bag-of-content, readout by role-prototype). Same task / data / split / content codes / seeds.

## Metric + bands (present-candidate readout; m=3 -> chance 1/3 = 0.333)
Primary discriminator = per-arm GENERALIZATION DROP (COGS metric = in-dist minus held-out).
- MUST-FAIL CONTROL (smoke gate, MUST fire): FLAT held-out <= 0.45 AND FLAT gen-drop
  (in-dist - held-out) >= 0.20. VOID if FLAT held-out > 0.60 (flat generalizes -> split does not
  isolate compositional generalization).
- HARD_PASS: FACTORED held-out >= 0.80 AND (FACTORED - FLAT) held-out gap >= 0.30 AND FACTORED
  gen-drop <= 0.10 (generalizes, no drop) AND FLAT gen-drop >= 0.20 AND must-fail fired AND
  learning signal present (FACTORED vocab held-out learning-curve delta >= 0.15 OR g_hat->g_true
  cosine delta >= 0.02).
- HARD_FAIL: held-out gap <= 0.05 (tie -> factorization confers no edge) OR FACTORED held-out
  <= chance + 0.05.
- MIDDLE_BAND: otherwise.

## Learning curve (USER-load-bearing "flexible / improving-as-it-reads")
Sweep training diversity D in {2,4,8,32,128,512}. g_hat is crosstalk-corrupted at low D and
content-blind at high D (2025 diversity-threshold mechanism). Reported on the HARDER full-vocab
readout (where accuracy is not saturated) + the mechanistic g_hat->g_true cosine.

## Brain-check (outcome NOT pre-assumed)
Conjunctive coding = FHRR bind = the brain's binding (compressed). TEM content-blind g = existence
proof zero-shot transfer CAN be done. OUR substrate's real bound = FHRR superposition crosstalk vs
number of simultaneous bindings m (three convergent derivations: SHRUTI ~10-binding ceiling,
tensor-coding blowup, VSA superposition noise). Capacity-stress probe (dedicated) LOCATES it.
Same-limit -> ACCEPT (keep m small = brain-faithful).

## Discipline gates satisfied
arms_differ (hash test on FACTORED vs FLAT predictions), scaffold-free witness exercises REAL
hdlab.binding.bind/unbind + hdlab.atoms (hand-built held-out GLASS-as-AGENT: FACTORED recovers,
FLAT fails), except SystemExit before Exception, no bare/BaseException, tmp+os.replace atomic
metrics, deterministic (fixed int seeds + random.Random + sorted; OMP=1; verified bit-repro on
re-run), all comment numbers tagged. compute_class = sequential-CPU (validates the primitive;
wall ~20s).

## RESULT (MEASURED@data/exp_role_filler_factorization_compgen_v1/metrics.json)
HARD_PASS. 5 seeds, N=8192, F=24, m=3. FACTORED held-out=1.000 vs FLAT held-out=0.003 (gap 0.997);
FACTORED gen-drop 0.000 (generalizes) vs FLAT gen-drop 0.382 (fails on novel combos). Learning
curve: D=2 FACTORED vocab held-out 0.738 / g_cos 0.432 -> D=512 vocab 1.000 / g_cos 0.998
(vocab delta 0.262, g_cos delta 0.566, both monotonic). Capacity cliff at N=256: robust through
m=24, degrades at m=32 (0.927) -- same crosstalk phenomenon as SHRUTI ~10-binding brain ceiling,
far beyond brain-faithful m=2-6. Determinism: identical verdict on re-run.
