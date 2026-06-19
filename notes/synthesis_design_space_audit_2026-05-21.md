# Design-space audit — what's been dug into, what hasn't, what to spin up

**Author**: Strategy session (Session 1)
**Date**: 2026-05-21 cycle 27 followup
**User prompt**: "summarize the design space and where we've focused. Are
there other relevant big bets that we haven't dug into yet? Anything that
holographic / materials science / crystallography uncovers that we
haven't flagged? Let's spin up some research. Spin glass should surface
some too."

Purpose: ground forward direction in honest accounting of what the
substrate has and hasn't characterized, with materials-physics framing
per [[feedback-materials-science-probe]].

---

## What we've dug into deeply (validated ✅ rows by cluster)

**Memory editing primitives** (deepest characterization):
- decompose, edit, recompose; CPU retrieval; pool retrieval
- ACF rescue (K/N up to 3.0 at 100%)
- **Structured-codebook erase** (Bet 2/C): Hadamard M/N≤0.78,
  Kerdock m=12 standard M/N≤8.0, Kerdock 32-coset variant M/N≤4.0
- **Continual sequential editing** 30→100→200→500→1000→2000→5000 ✅
  (past AlphaEdit 3000 ceiling)
- Iterative re-editing same fact (both arms hold)
- Edit reversibility (500 cycles both arms)
- Order-invariance (Kerdock commutes; Frob drift < 0.05)
- Noisy edit keys, batch=sequential equivalent, alpha-flat insensitive
- **Edit-then-query pipeline ✅** (Bet A) at M < N / M = N / M = 2N

**Concept / generation**:
- R10 K-scaling (full curve), M1 bundle-SNR, generation at K=16
  strict baseline, multi-step generation beats trigram (Bet H rescued
  via T=0.5 sampling and rep penalty p≥1)

**Continual learning**: R7 random replay; pre-shift replay free;
Hebbian-only confirmed.

**Robustness/scaling**: K-cliff K/N=0.56 (B=2), K/N=0.31 (B=3),
N-dependent correction at N=8192. **Substrate noise tolerance σ≤16
(break at σ=32)**.

**Spin-glass / topological**: RSB structurally ✅ at α=0.153 (Parisi P(q)
multi-peaked, ultrametricity 0.357). α_c AGS-like (rising 0.082 →
0.107 → 0.153 across N).

**Compound**: multihop+edit composes ✅; **real-time learning via
continual pool** ✅ (static 6.50 → continual 3.78 bpc).

**Forensics**: WHT for structured (Hadamard) keys 100% recall through
K/N=0.98; SVD partial for random keys; **random-key iterative
chargeflip ❌** PROVISIONAL.

**Calibration**: ❌ → ✅ via TEMPSCALE β=32 (Bet G).

**ICL**: log-linear at low/mid ICTX (slope +0.14); soft-saturating
high ICTX (slope +0.05); monotone positive through ICTX=65536.

---

## Where we've focused most (4-hour pattern)

Cycles 9-25 ran HEAVY on:
- **Memory-editing × composition matrix** (edit × overcapacity,
  edit × calibration, edit × multihop, edit × noise, etc.) — 20+ smoke
  results, mostly all positive
- **Continual-editing capacity ladder** (M/N from <1 to 16N; edit count
  from 30 to 5000)
- **Bet G/H rescues** (TEMPSCALE β=32; T=0.5 sampling)

Pattern: substrate composes well; extensions confirm rather than
falsify. Experiment Dev pivoted to break-point hunting at cycle 24,
located σ=32 noise break + Kerdock v8 32-coset M/N=8 break.

---

## What we've NOT dug into (big bets piling up)

### Tier-1 KILLER still unresolved
- **Bet B multi-task continual learning** A→B→C→D — Tier-1 KILLER ⚪;
  R5 landed cycle 8; Experiment Dev hasn't built (PROT-005 may unblock
  on next cycle)
- **GPT-quality generation bar** — generation ✅ at single-pos + multi-
  step-beats-trigram, but not GPT-class. Bet D K-curve analyzer pass
  pending.

### Tier-2 KILLERs barely touched
- **Cross-modal binding (vision-language)** — never tested. Was on v1
  KILLER Tier-2 list.
- **Compositional generalization** — R3 research landed (cycle 15) but
  no experiment designed yet.
- **Hierarchical concepts / concepts-of-concepts** — never tested.
- **Multi-hop reasoning extended past d=25** — R8 FHRR/hybrid candidates
  ready but unbuilt.
- **Bet F SSH-BSC v2 topological** — R10 landed; unbuilt.
- **Sleep-style memory consolidation** — never tested. Offline replay
  during quiescence.
- **Principled forgetting / robust GDPR-erase under attack** — Bet 2/C
  validated multi-probe Mirage but not adversarial.

### Open research backlog (forward-routed)
- R7 random-key chargeflip rehab — landed
- R13 Drinfeld double — landed honest-negative; deferred
- R14 Tomita-Takesaki — landed honest-negative (wrong tool)
- **R15 Steenrod** — pending
- **R16 Free probability quantitative predictions** — active (Bet I)

---

## Materials-science angles NOT YET flagged

Per user direction: "what does holographic / materials science /
crystallography uncover that we haven't flagged?"

### Crystallography beyond WHT-peak forensics

WHT-peak diffraction for structured keys: ✅ done (cycle 12+).
**What hasn't been touched:**

- **Diffuse scattering** vs Bragg peaks — substrate behavior under
  partial-order codebooks (between full Hadamard and random ±1).
  Diffuse scattering carries information about local disorder; could
  give a forensics primitive for "how structured is this substrate?"
- **Anomalous diffraction** (phase retrieval beyond intensities only)
  — substrate analog of MAD / SAD phasing from biological X-ray
  crystallography. Different probe than Walsh peaks.
- **Quasicrystals** — non-periodic but ordered codebooks (Penrose-tiling-
  like). Would have aperiodic diffraction patterns; might give
  intermediate capacity between random and Hadamard.
- **Charge density wave (CDW)** — periodic modulation in W matrix;
  substrate analog of incommensurate density modulations.

### Spin-glass directions beyond what we have

We have: α_c AGS-like, P(q) multi-peaked, ultrametricity 0.357,
RSB phase confirmed structurally. **Untouched:**

- **Continuous RSB (full Parisi)** vs 1RSB — our P(q) result was
  multi-peaked (1RSB); is the substrate at higher α / different
  codebook in continuous RSB? Different physics.
- **de Almeida-Thouless (AT) line** — phase boundary between replica-
  symmetric and RSB. Where exactly is the substrate? Crossing the AT
  line corresponds to different substrate operating regimes.
- **Aging / FDT violation** — `wave14j_aging_kovacs` ran cycle 12-13
  inconclusive. Glassy substrates show fluctuation-dissipation
  violation; quantifying it would diagnose glassiness.
- **Mode-coupling theory (MCT)** — predicts supercooled-liquid-to-glass
  transition; might describe substrate training dynamics (W spectrum
  during delta-rule updates).
- **Two-temperature dynamics** — substrate has effective T from
  softmax (β=32 from Bet G ✅). Two-temperature systems (T_quench ≠ T_obs)
  show specific signatures connecting to FDT violation.
- **Random First-Order Transition (RFOT)** — connects spin-glass to
  glass-forming liquids; gives an additional capacity-scaling
  framework distinct from M-P.
- **Replica-symmetric crossover at small α** — substrate at α=0.001
  would be RS; what's the operating-mode change at AT line?

### Holographic / AdS-CFT directions

The substrate has a bulk/boundary structure (W matrix internal state vs
queried output). Holographic principle has substrate connections:

- **Ryu-Takayanagi formula** — entanglement entropy ~ minimal surface
  area. For substrate: could provide alternative capacity bound
  (substrate bundle = "bulk region"; accessible atoms = "boundary";
  RT formula bounds information content). Distinct theoretical
  framework from M-P.
- **Bekenstein bound** — max information in a region scales as area not
  volume. Substrate analog: max info in W scales as dim^2 not deeper.
  Where does substrate hit this bound?
- **Tensor networks (MERA, TNS, holographic codes)** — hierarchical
  state representation matching RSB tree structure. Wave 9 MPS exists
  but unexplored. HaPPY codes / perfect tensors might give
  fault-tolerant substrate primitives.
- **Bulk reconstruction from boundary** — given the substrate's
  observable behavior, can we reconstruct W's internal state? Substrate
  forensics from a different angle.

### Topological order beyond domain walls

Bet F SSH-BSC tests Z-quantized winding (chiral class AIII). **Untouched:**

- **Anyons / fractional statistics** — substrate analog of fractional
  quantum Hall. Different topological invariant than winding number.
- **Skyrmions / instantons** — topological objects beyond domain walls;
  more robust noise protection (different defect class).
- **Higher Chern numbers** — beyond Z-quantization, into Z^n.
- **Topological order parameters from K-theory** — full 10-fold-way
  classification.

### Other physics frameworks worth scoping

- **Eigenstate thermalization hypothesis (ETH)** — when does substrate
  "know it's at equilibrium"? Connects to calibration + RSB.
- **Many-body localization (MBL)** — substrate state-trapping; relevant
  for continual-learning catastrophic-forgetting boundaries.
- **Hydrodynamic modes** — collective behavior of bundle population
  during continual editing.
- **Color glass condensate** (QCD) — high-density limit; might describe
  substrate at M/N≫1.

---

## Recommended new research requests (R17-R22)

Per [[feedback-unbiased-research]]: each framed "what does X do?"
not "X for substrate?" Per [[feedback-no-papers-product-only]]:
substrate-physics characterization, not paper-worthy. All forward-
research backlog; slot in after top-priority queue (Bet B / multi-hop
FHRR / Bet F) drains.

**R17 — Holographic principle for substrate**
Pass 1 broad: Ryu-Takayanagi, Bekenstein, tensor networks (MERA, TNS),
HaPPY codes, bulk reconstruction. Pass 2: substrate-compatible drill —
does RT give an alternative capacity bound? Tensor-network
representation of substrate's RSB tree? Holographic-code analog for
fault-tolerant substrate? Connects to: Bet C capacity claims,
hierarchical retrieval RSB row.

**R18 — RFOT / glassy-dynamics for substrate**
Pass 1 broad: Random First-Order Transition, supercooled liquids,
mode-coupling theory, aging dynamics, two-temperature systems, FDT
violation, eigenstate thermalization. Pass 2: substrate-compatible
drill — substrate training dynamics analogous to glass transition?
Two-temperature picture grounds TEMPSCALE β=32? Aging signatures
distinguishable from M-P spectral predictions? Connects to: Bet G
calibration ✅, Bet I free probability, RSB row.

**R19 — Topological order beyond winding**
Pass 1 broad: anyons, fractional statistics, skyrmions, instantons,
higher Chern numbers, full 10-fold-way K-theory classification.
Pass 2: substrate-compatible drill — does substrate carry a
fractional topological invariant beyond Z-quantized winding? Skyrmion
analog for robust memory protection? Connects to: Bet F SSH-BSC v2
(currently AIII class only).

**R20 — Compositional generalization experiment design** (reactivate R3)
R3 (compositional generalization research) landed cycle 15 but no
experiment was designed. Pass 2 (already had broad lit scan): design
substrate-compatible compositional eval — novel combinations of
learned concepts that aren't in training. Output: experiment spec
for Experiment Dev. Connects to: Tier-2 KILLER (Compositional
generalization untested).

**R21 — Cross-modal substrate binding** (vision-language)
Pass 1 broad: multimodal embeddings, CLIP-style joint spaces, image-
text bound representations, cross-modal retrieval. Pass 2: substrate-
compatible drill — substrate binds text-codebook with image-embedding
codebook? Cross-modal queries retrieve correctly? Tier-2 KILLER
untouched since v1.

**R22 — Sleep-style memory consolidation**
Pass 1 broad: sleep-replay neuroscience, hippocampal replay during
quiescence, consolidation timescales, off-line learning. Pass 2:
substrate-compatible drill — does offline replay during quiescence
(no new inputs) improve substrate retention beyond what online R7
replay gives? Connects to: continual learning ✅ but only online
variant tested.

### NEW spin-glass-specific routings (per user "spin glass should surface some too")

**R23 — Continuous RSB / AT line for substrate**
We have 1RSB structural at α=0.153. Pass 1 broad: full Parisi
solution, continuous RSB, de Almeida-Thouless line, AT instability,
phase boundary diagnostics. Pass 2: substrate-compatible drill — is
substrate in 1RSB or continuous RSB at α=0.153? Where is the AT
line? What operating-mode changes at AT? Connects to: Bet E Parisi
P(q), RSB row.

**R24 — FDT violation + two-temperature substrate dynamics**
Substrate has effective T from softmax (β=32). Pass 1 broad:
Fluctuation-Dissipation theorem, FDT violation in glasses, two-
temperature out-of-equilibrium systems, T_eff measurements.
Pass 2: substrate-compatible drill — measure FDT violation in
substrate; does it correspond to β=32 calibration finding? Two-
temperature picture grounds calibration? Connects to: Bet G ✅, Bet I,
RFOT (R18).

**R25 — Aging / memory rejuvenation in substrate**
`wave14j_aging_kovacs` (cycle 12-13) ran inconclusive. Pass 1 broad:
Kovacs effect, aging protocols, memory and rejuvenation in spin
glasses. Pass 2: substrate-compatible drill — design proper aging
protocol; does substrate show Kovacs memory? Substrate-relevant for
long-running deployments. Connects to: continual learning ✅, RFOT.

---

## Priority ordering for these new R-requests

Strategy ranks by (a) substrate-actionable-output probability,
(b) connection to active bets, (c) cost.

| Rank | R-request | Substrate link | Cost (lit scan) |
|---|---|---|---|
| 1 | **R20 compositional gen experiment design** | Closes Tier-2 KILLER directly | 1 cycle |
| 2 | **R23 continuous RSB / AT line** | Strengthens Bet E + R16 Bet I | 1 cycle |
| 3 | **R24 FDT violation + two-T** | Grounds Bet G β=32 theoretically | 1 cycle |
| 4 | **R17 holographic principle** | Alt capacity bound vs Bet I M-P | 1-2 cycles |
| 5 | **R18 RFOT / glassy dynamics** | Extends spin-glass framing | 1 cycle |
| 6 | **R21 cross-modal binding** | Tier-2 KILLER + product-relevant | 1 cycle |
| 7 | **R22 sleep-replay consolidation** | Extends continual learning ✅ | 1 cycle |
| 8 | **R19 topological order beyond winding** | Extends Bet F | 1 cycle |
| 9 | **R25 aging / Kovacs in substrate** | Diagnostic; lower priority | 1 cycle |

R20 / R23 / R24 are highest-leverage: they close or strengthen
existing active work.

## Bet promotions if research lands positive

If R20 produces experiment spec → **Bet J** (compositional generalization).
If R23 + R24 land with strong substrate-actionable predictions →
**Bet K** (substrate dynamics from spin-glass theory).
If R17 produces RT-style capacity bound → folds into Bet I (free probability).

---

## Recommended cap_map updates after R-batch lands

- Compound section: add cross-modal, compositional, sleep-replay rows
  (initial state: ⚪ until tested)
- Topological row: extend beyond winding (anyons, skyrmions)
- Spin-glass row: explicit AT-line position, continuous vs 1RSB
- Calibration row: theoretical grounding from FDT/two-T

---

## Cycle 27 followup #3 — Learning deep-dive, light-matter, ferromagnetism (user)

User added three more directions: "have we done a deep dive on learning?
... light frequency, vibrational frequency, dislocation physics ... whole
world of interactions ... ferromagnetism ... magnetic domains and
interactions should be highly actionable."

Honest assessment: **no, we have NOT done a deep dive on learning**.
Substrate has Hebbian-only confirmed + R7 random replay + real-time
learning via pool, but **the learning theory itself** (optimization
landscape, generalization, neural tangent kernel, scaling laws,
implicit bias of the delta rule) hasn't been systematically explored.

Light-matter and ferromagnetism are unflagged framing axes.

### Learning deep-dive (R26)

**Untouched**:
- **Implicit bias of delta rule**: what does the delta-rule prefer in
  the high-dimensional W landscape? Compare to gradient-descent
  implicit bias on overparameterized networks.
- **Neural tangent kernel (NTK)** for substrate: lazy-training regime
  analogs. Substrate Hebbian-only may sit in a non-NTK regime.
- **Double descent** in substrate generalization: empirical curve as
  M_stored / N scales past 1.
- **Scaling laws**: bpc vs N, K, M_stored, sample count — is there a
  substrate analog of LLM scaling laws (Chinchilla-style optimal
  compute allocation)?
- **Convergence rate** of delta-rule on W: how fast does W stabilize?
- **Catastrophic forgetting curves**: empirical forgetting curve for
  random replay (R7) is ✅ at A→B; never characterized as a curve.
- **Generalization gap**: substrate train-vs-test gap as function of
  M_stored / N.
- **Sample efficiency**: bpc improvement per sample seen.

### Light-matter / nano-scale interactions (R27)

**Substrate analogs unflagged**:
- **Photonic crystals** — periodic dielectric → photonic band gaps;
  substrate analog: structured-codebook frequency-domain forbidden
  zones. Could give ALT capacity / forensics framework than Walsh.
- **Plasmonics** — collective electron oscillations; substrate analog:
  collective atom modes / soft modes during retrieval.
- **Cavity polaritons** — coupled photon-phonon modes; substrate analog:
  coupled codebook-context modes.
- **Optical frequency combs** — discrete frequency lattice; substrate
  analog: discrete atom basis spacing.
- **Metamaterials / negative-index** — subwavelength structured response
  beyond bulk material. Substrate analog: emergent retrieval behavior
  beyond per-atom response.
- **Topological photonics** — protected modes in photonic structures;
  complements Bet F SSH topology.
- **Stimulated Raman scattering** — nonlinear cascade between
  frequencies; substrate analog could be cascaded multi-hop binding
  through different W modes.

### Dislocation physics (R28)

**Substrate analogs**:
- **Edge dislocations** — line defects; substrate analog: line-defect
  in codebook lattice.
- **Screw dislocations** — helical defects; substrate analog: phase
  shift in periodic codebook structure.
- **Burgers vector** — topological invariant of dislocations; substrate
  analog: an invariant beyond Bet F winding.
- **Dislocation motion** under stress — substrate analog: edit
  trajectories through W as defect motion.
- **Frank-Read sources** — dislocation multiplication; substrate analog:
  one edit spawning correlated changes.
- Complements Bet F SSH-BSC topology with a different defect class.

### Ferromagnetism / magnetic domains (R29) — user specifically called out

**Substrate analogs**:
- **Magnetic domains** — regions of aligned spins; substrate analog:
  clusters of correlated atoms in stored bundles. Domain SIZE
  distribution would be a substrate fingerprint.
- **Domain walls** — already in Bet F SSH-BSC (chiral AIII).
- **Hysteresis** — substrate training-dependent state; substrate
  analog: order-of-edits matters under specific protocols (we showed
  Kerdock commutes per cycle 19, but with what hysteretic protocol
  does substrate show memory?).
- **Curie temperature** — order-disorder transition; substrate has α_c
  AGS-like (cycle 8 evening update). Same physics, different framing.
- **Exchange interactions** (Heisenberg / Ising / XY) — substrate W is
  exactly this; ferromagnetic vs antiferromagnetic interactions.
- **Spin waves / magnons** — collective excitations; substrate analog:
  collective excitation of stored atoms under perturbation. Connects
  to phonon framing.
- **Magnetocrystalline anisotropy** — preferred directions in spin
  alignment; substrate analog: codebook anisotropy (Kerdock has it;
  random keys don't).
- **Anti-ferromagnetism / frustration** — geometric frustration leading
  to spin liquids. Connects directly to RSB (geometric frustration is
  the prototypical RSB cause).
- **Information storage in magnetic media** — substrate IS a magnetic-
  memory analog at the atom level.

---

## Updated R-request priority ordering (post cycle 27 followup #3)

| Rank | R-request | Substrate link | Why |
|---|---|---|---|
| 1 | **R26 Learning theory deep-dive** | Foundational — covers ALL bets | Surprising gap; central to substrate as ML object |
| 2 | **R29 Ferromagnetism / magnetic domains** | Connects spin-glass + Bet F + RSB | User explicitly called out as highly actionable |
| 3 | **R20 Compositional gen experiment design** | Closes Tier-2 KILLER | Prior priority 1 |
| 4 | **R23 Continuous RSB / AT line** | Bet E + Bet I | Prior priority 2 |
| 5 | **R24 FDT violation / two-T** | Bet G theoretical grounding | Prior priority 3 |
| 6 | **R27 Light-matter / photonics / metamaterials** | Alt framing for capacity / topology | New framing axis |
| 7 | **R28 Dislocation physics** | Extends Bet F topology | Different defect class |
| 8 | **R17 Holographic principle** | Alt capacity vs Bet I M-P | Prior medium |
| 9 | **R18 RFOT / glassy dynamics** | Extends spin-glass | Prior medium |
| 10 | **R19 Topological order beyond winding** | Extends Bet F | Prior lower |
| 11 | **R21 Cross-modal binding** | Tier-2 KILLER untouched | Prior lower |
| 12 | **R22 Sleep-replay consolidation** | Extends continual learning ✅ | Prior lower |
| 13 | **R25 Aging / Kovacs** | Diagnostic | Prior lower |

R26 + R29 jump to top per user direction. Learning theory is genuinely
the biggest gap in our characterization — the substrate has been studied
as a memory primitive but not as a learning system in its own right.

---

## Honest assessment

The substrate is heavily characterized on **edit / continual / capacity**
axes. The gaps are on **multi-modal / compositional / sleep / theoretical
grounding**. The spin-glass material has been touched at α_c + P(q) but
not drilled into the continuous-RSB / AT-line / FDT structure where the
real theoretical leverage lives. The materials-science framing has been
applied to crystallography (WHT) but not to the rich phenomenology
beyond Bragg peaks. Holographic-principle hooks (RT, tensor networks)
are completely unflagged.

Spin up R20/R23/R24 first (highest leverage, lowest cost). R17/R18 next
(broader frameworks, longer payback). R21/R22 if there's research
bandwidth left.
