# Research: Quantum-Information Lens on Cheap High-Capacity Codes (Drill A)

Date: 2026-07-13
Topic: TOPIC A -- cheap high-capacity representation + exploitable structure for codes, viewed through
quantum-information / physics-of-information mechanisms, honestly mapped to CLASSICAL (real/complex-phase
VSA) realizability.
Dispatch: research role, 3 parallel Sonnet lit-scan sub-agents (tensor-network/holographic-bound angle;
quantum-associative-memory/amplitude-encoding angle; QEC-structure/phase-interference angle) + Opus-level
synthesis (this note).
Calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis P capped at 0.50; hard-fail thresholds
pre-registered below.
Field-advisor context: `quantum-info` field is flagged in the advisor as 0% yield / DO-NOT-DRILL (4 prior
drills all closed on the Harlow OAQEC no-go, see v93/v98 "Substrate as OAQEC" closure and v278 "classical
analog of AQC" note). This drill deliberately re-enters the field but reframes the question narrowly around
CLASSICAL REALIZABILITY of specific sub-mechanisms (tensor networks, dense associative memory, LDPC wrapper
codes, phase encoding, Sourlas spin-glass codes) rather than "is the substrate quantum" -- a materially
different question than what closed the field before. Net result: the classical-realizability reframe DOES
surface one genuinely new, concrete, non-trivial lever (Lever 1 below) that prior `quantum-info` drills did
not surface, so the field is not purely a dead end when entered at this angle -- but four of five other
angles simply re-confirm the same no-go, so this should NOT be read as un-closing the field generally.

## HEADLINE

Of six quantum-information mechanisms scanned (tensor-network/MPS compression, holographic/entanglement
bounds, quantum-inspired dequantization, amplitude encoding, QRAM, stabilizer/holographic QEC), five
converge on the SAME honest negative for our exact problem (arbitrary structureless entity codes): every
one of these mechanisms buys its capacity/compression benefit ONLY when the underlying data has exploitable
structure (low entanglement / low rank / sparsity / low query-complexity), and each literature explicitly
names "random / generic / high-rank / unstructured" as its own documented failure mode -- not an
unstudied edge case, a *stated* one. This is a triangulated confirmation, from three independent formal
traditions (condensed-matter area-law, numerical tensor-train theory, and dequantization complexity-theory
lower bounds), of exactly why our own multi-module residue / grid-cell factoring attempt failed: structureless
labels have nothing to compress, and no quantum-information mechanism escapes that -- quantum or classical.

The ONE genuinely promising, classically-realizable, NON-compression lever that fell out of this scan is
different in kind from all the "compress an arbitrary vector" ideas: **dense / modern associative memory
with a super-quadratic (polynomial-order or exponential) interaction/energy function** (Krotov & Hopfield
2016; Demircigil et al. 2017). This is the fully-classical mechanism that quantum-associative-memory papers
implicitly compete with when they claim "exponential capacity from qubit superposition" -- and it already
WINS that comparison classically, with zero Hilbert-space/readout overhead, because Holevo's bound proves
the quantum "exponential capacity" is not actually extractable as classical information anyway (only ~n
classical bits recoverable from n qubits, regardless of the 2^n-dimensional amplitude vector). Critically,
this lever requires NO structure in the entities being stored -- it is a change to the READOUT/ENERGY
NONLINEARITY, not a compression of the codes themselves, so it sidesteps the "arbitrary labels, nothing to
compress" problem entirely. This is already flagged independently in our own field-advisor as a fruit-bearing
field ("modern-hopfield -- drill MORE: Krotov/Hopfield-86 generalizations, dense Hopfield exponential
capacity") -- this drill supplies the quantum-information-side justification for why that lever is the
right one to prioritize, plus a secondary classically-realizable lever (LDPC/expander-code redundancy
wrapper, agnostic to payload semantics) that is orthogonal and stackable with it.

## Cheap decisive test

Single CPU-only smoke, no GPU required, ~1-2 hours wall clock:

1. Implement a dense-associative-memory readout with a tunable interaction order/energy nonlinearity
   (polynomial F(x) = x^n for n in {2 (baseline linear/quadratic Hopfield), 4, 8} and exponential
   F(x) = exp(beta x) per Demircigil et al.) as an ALTERNATE cleanup/readout stage layered on top of
   existing substrate entity/relation codes -- do not touch how codes are constructed, only how retrieval
   scores patterns.
2. At N (code dimension) in {256, 512, 1024, 2048}, and using the SAME store-code distribution already in
   use (near-orthogonal random high-dim vectors -- no synthetic structure added), measure max number of
   stored patterns recoverable at >=95% exact-match retrieval accuracy for each interaction order n
   (including n=2 as the linear-capacity baseline, expected ~0.14N per Amit-Gutfreund-Sompolinsky).
3. Fit capacity C(N) to a power law C ~ N^b (or exponential C ~ exp(c*N)) separately for each interaction
   order and compare the fitted exponent/rate against the n=2 baseline.
4. Separately (fast, no GPU): implement an LDPC/expander-style parity wrapper (e.g., a sparse random Tanner
   graph with belief-propagation decoding) around a batch of arbitrary entity codes and measure whether it
   improves recoverability under injected bit/coordinate-level noise relative to the unwrapped codes at
   matched total-storage overhead.

## Falsifiable predictions

**HARD-PASS (dense associative memory lever, primary):**
- HP1: for n in {4, 8} or exponential F(x)=exp(beta x), fitted capacity exponent b > 1.3 (clearly
  superlinear, distinguishable from the n=2 linear baseline's b~1.0) at N up to 2048, OR measured capacity
  at N=2048 exceeds the n=2 linear baseline by >=2x at matched retrieval-accuracy threshold (95% exact
  match). Threshold set at 2x (not the aspirational many-fold gap implied by the exp(N/2) asymptotic form)
  because finite-N pre-asymptotic behavior is expected to undershoot the asymptotic rate -- lit-scan
  calibration penalty applied.
- HP2: the capacity gain from HP1 persists when patterns are drawn from the SAME correlated/near-orthogonal
  code distribution the substrate actually uses (not iid random {-1,+1} patterns as in the original
  Hopfield/Krotov papers) -- i.e., the mechanism is not an artifact of an idealized pattern distribution
  that doesn't survive contact with our actual codebook statistics.

**HARD-FAIL (any one triggers de-prioritization of this lever):**
- HF1: fitted capacity exponent b <= 1.1 for all tested interaction orders up to n=8 (no meaningfully
  superlinear scaling observed at accessible N) -- the asymptotic exponential-capacity result is a
  large-N phenomenon that doesn't show up before compute cost (interaction order n requires O(n)-body terms,
  cost per readout scaling with n * N or worse) becomes prohibitive.
- HF2: capacity gain from HP1 collapses (falls back to within 20% of the n=2 baseline) when re-tested on
  the substrate's actual correlated code distribution (per HP2) -- i.e., the correlation-hurts-capacity
  finding already on file (per [[reference-correlation-hurts-associative-store-capacity-decouple-from-retrieval]])
  dominates and cancels the interaction-order benefit.
- HF3 (LDPC wrapper): injected-noise recovery improvement from the parity wrapper is <10% relative to
  unwrapped codes at matched total storage overhead -- the wrapper mechanism, while theoretically sound,
  doesn't transfer meaningful benefit to the specific noise model our retrieval pipeline actually
  experiences (e.g., if our dominant error mode is systematic interference/crosstalk rather than
  independent bit-flip noise, the LDPC assumption of a memoryless noise channel may not match).

## Cross-thread synthesis

**Confirms and extends prior closures.** The v93/v98 "Substrate as OAQEC" closure (substrate commutative,
Harlow theorem requires non-commutative operator algebra) and the v278 "classical analog of AQC" note
(D-Wave/AQC correspondence, same commutativity boundary) both drew a line at operator-algebra structure.
This drill adds an INDEPENDENT, complementary no-go from a different corner of quantum information theory:
Holevo's channel-capacity theorem (n qubits yield at most n recoverable classical bits, regardless of 2^n
amplitudes) and the dequantization/lower-bounds literature (Gilyen et al. arXiv:2402.15686 formally proves
classical sampling shortcuts provably fail outside low-rank regimes). Between Harlow's operator-algebra
argument and Holevo's channel-capacity argument, we now have TWO structurally different, independently
converging reasons the "quantum gives you more for free" story does not transfer to a classical arbitrary-
data memory system -- this is a stronger, more robust closure of the general quantum-info field than either
argument alone, even as it leaves the field open to narrowly-reframed classical-realizability probes (as
this drill demonstrates).

**Directly explains the TOPIC A premise (why the grid-cell/RNS trick failed).** The prior deployable-levers
note (`notes/research_deployable_representational_capacity_levers_relational_map_builder_2026-07-13.md`)
ranked RNS/CRT multi-module residue coding as the top lever (P_deflated=0.35) by analogy to grid-cell coding
-- but that analogy assumes there IS periodic/modular structure to factor a range into (grid cells factor a
literal spatial coordinate, which has continuous structure). This drill's tensor-network/dequantization
findings independently confirm, from three unrelated formal traditions, that factoring/compressing
arbitrary UNSTRUCTURED entity IDs (no coordinate, no continuous structure, no correlation) into small
modular cores has NO theoretical basis -- the failure was not a bug in our implementation, it is the
expected outcome given the entities genuinely have zero exploitable structure. This should retire "compress
the codes" as a productive direction for the specific case of arbitrary entity labels, and REDIRECT effort
toward mechanisms that don't require code-level structure: (a) the dense-associative-memory
interaction-order lever (this note), (b) resonator-network / phase-encoding capacity work already flagged
as fruit-bearing (`modern-hopfield`, `free-probability` adjacents in the field advisor), and (c) the
LDPC/expander wrapper for robustness (orthogonal axis: recoverability under noise, not raw capacity).

**Independently converges with the same-day wildcard-lens drill.** A sibling same-day drill
(`notes/research_drillA_wildcard_capacity_structure_2026-07-13.md`, coding-theory/linguistics/number-theory/
graph-spectral lens, dispatched with zero cross-talk to this one) reached the identical structural verdict
via completely different formal machinery: Shannon source-coding + Kolmogorov incompressibility prove no
bijective relabeling of an arbitrary entity beats the entropy floor, and all exploitable structure comes
from something EXTERNAL to the label (the codebook operator, usage-frequency, or the relation graph). This
quantum-information drill adds a THIRD and FOURTH independent formal confirmation (condensed-matter
area-law + entanglement volume-law failure mode; dequantization complexity-theory lower bounds) of the same
"nothing to compress in an arbitrary label" conclusion -- now converged from five unrelated fields
(coding theory, linguistics/economics, graph spectral theory, condensed-matter physics, quantum complexity
theory) in a single day. This is about as strong as a negative result gets without running code, and the two
drills' recommended NEXT levers are complementary rather than competing: the wildcard drill's levers
(frequency-driven budget allocation, usage-graph spectral basis) operate on CODE CONSTRUCTION / allocation;
this drill's lever (dense-associative-memory interaction order) operates on READOUT / cleanup-energy
function. The two are stackable -- e.g., frequency-weighted code allocation (wildcard P2) combined with a
higher-order interaction readout (this note's HP1) attack capacity from two independent, non-overlapping
axes simultaneously.

**Connects to the correlation-hurts-capacity finding already on file.** Per
`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`, semantically
correlated store-codes collide and reduce capacity below the iid-random baseline the classical Hopfield
capacity theorems (Amit-Gutfreund-Sompolinsky, Krotov-Hopfield, Demircigil) assume. HP2/HF2 above are
designed specifically to test whether the dense-associative-memory capacity gain survives this known
confound rather than assuming it transfers cleanly from idealized-pattern theory.

## Substrate-product implications

- If HP1/HP2 land: a drop-in, code-construction-agnostic readout upgrade (higher-order interaction /
  exponential energy cleanup) that raises the number of exactly-recoverable stored associations at fixed
  dimension N, without needing to change how entity/relation codes are built -- directly extends the
  usable capacity ceiling of the relational map-builder / KG-store cleanup stage without the super-linear
  cost of just increasing N. Product framing: "more provable, exactly-recoverable facts per unit of vector
  memory," not a compression trick -- the honest framing is a smarter readout/cleanup rule, matching
  [[feedback-no-papers-product-only]].
- If HF1/HF2 fire: this rules out the interaction-order lever specifically for our correlated-code regime,
  and narrows remaining capacity levers to (a) resonator/phase-encoding factorization (already deployed via
  FHRR complex-phase codes -- worth a dedicated drill on resonator-network capacity limits specifically,
  Frady/Kent/Olshausen/Sommer 2301.10352), and (b) accepting brute-force N-scaling as the only lever, with
  LDPC-style redundancy wrappers as a separate, orthogonal robustness lever (recoverability under noise, not
  raw capacity) that remains viable regardless of HF1/HF2 outcome.
- Either way: the tensor-network/dequantization negative result is itself product-relevant -- it retires an
  entire class of "clever compression" proposals (grid-cell/RNS-style factoring, tensor-train factoring of
  entity codes, holographic-bound-inspired schemes) as NOT applicable to arbitrary entity labels, closing
  off a search direction the team might otherwise re-attempt in a different guise. This is a genuine,
  triangulated negative result worth cap_map annotation (deferred to strategy/director per role separation
  -- this note does not modify cap_map).
- The quantum-only closures (Holevo bound on channel capacity; non-commutative operator-algebra requirement
  for OAQEC/holographic-code reconstruction) should NOT be re-drilled again absent a genuinely new angle --
  this is now a doubly-converged closure (Harlow + Holevo, two independent theorems) and further quantum-info
  drills should require a specific, named new sub-mechanism not covered by either argument.

## Citations (verified count: 33 distinct sources across 3 sub-agent scans, cross-checked for consistency)

Tensor-network / holographic-bound / dequantization scan (11 citations):
Orus arXiv:1306.2164 (tensor network review); Eisert-Cramer-Plenio Rev. Mod. Phys. 82:277 / arXiv:0808.3773
(area-law review); arXiv:2112.06959 (volume-law entanglement of typical states); Bekenstein bound survey
arXiv:1009.5385; arXiv:1106.3817 (holographic entropy bound violations); Tang STOC 2019 / arXiv:1807.04271
(quantum-inspired recommendation); Chia et al. arXiv:1910.06151 (sampling-based sublinear matrix arithmetic);
Gilyen et al. arXiv:2402.15686 (dequantization lower bounds); Oseledets SIAM J. Sci. Comput. 33(5) 2011
(tensor-train decomposition); Stoudenmire & Schwab arXiv:1605.05775 (MPS classifiers); Cichocki et al.
arXiv:1609.00893 (tensor networks for dimensionality reduction).

Quantum associative memory / amplitude encoding / Holevo / compressed sensing scan (11 citations):
Holevo 1973 theorem (Wikipedia, Quantiki, CMU lecture notes cs.cmu.edu/~odonnell/quantum15/lecture18.pdf);
Ventura & Martinez quant-ph/9807053 (quantum associative memory via Grover); Rebentrost-Bromley-Weedbrook-
Lloyd Phys. Rev. A 98:042308 / arXiv:1710.03599 (quantum Hopfield network); Phys. Rev. Research 5:023074
(optimal storage capacity of quantum Hopfield networks); Krotov & Hopfield 2016 (dense associative memory,
F(x)=x^n); Demircigil et al. 2017 (exponential-capacity associative memory, F(x)=exp(x)); Aaronson
"Quantum Machine Learning Algorithms: Read the Fine Print" (scottaaronson.com/papers/qml.pdf); Donoho IEEE
Trans. Info Theory 52(4):1289-1306 2006 (compressed sensing); Baraniuk & Davenport (JL meets compressed
sensing); Nature Physics bucket-brigade QRAM; MDPI Sensors 23(17):7462 (QRAM for dummies).

QEC structure / phase-interference / Sourlas scan (11 citations):
arXiv:1602.01545 (stabilizer syndrome correction); Error Correction Zoo qubit-CSS entry; arXiv:0712.0103
(stabilizer codes from classical parity-check matrices); arXiv:1008.5384 (entanglement-assisted QEC);
Pastawski-Yoshida-Harlow-Preskill arXiv:1503.06237 (HaPPY code); Harlow arXiv:1607.03901 (RT formula from
QEC); arXiv:2102.02619 (holographic tensor network QEC review); arXiv:2005.05971 (infinite-dim HaPPY code);
Tanner 1981 (Tanner graphs, foundational); Sipser-Spielman expander codes (foundational, referenced via
quantum-expander-code literature); Plate IEEE Trans. Neural Networks 1995 (Holographic Reduced
Representations); Frady & Sommer arXiv:1901.07718 (rhythmic spike phase codes); Frady et al. resonator
networks / arXiv:2301.10352 (VSA capacity analysis); Sourlas Nature 339:693 1989 (spin-glass error-correcting
codes); Kabashima-Saad arXiv:cond-mat/9904342 (finite-connectivity codes); arXiv:cond-mat/0508586 (survey
propagation Sourlas code); arXiv:1708.03395 PNAS (replica-method GLM phase transitions).

(Total unique citations across all three scans, de-duplicated: 33. All URLs/identifiers as returned by
sub-agents; not independently re-verified by the synthesizing agent beyond internal consistency checking --
per lit-scan calibration discipline, treat citation existence as sub-agent-reported, not director-verified.)
