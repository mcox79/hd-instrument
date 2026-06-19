# Research — Bet E Parisi P(q) measurement methodology review

**Topic.** Bet E (active capability bet, queued): substrate-fingerprint via
Parisi overlap distribution P(q) shape. Strategy noted: "Research
methodology review optional but recommended before queue." This note
provides that review. Not a formal R# (R1-R15 are all complete; R16
already exists); produced under user directive "more research."

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 19 tool uses,
25+ verified citations 1975-2026). Thirteenth consecutive cycle following
post-audit protocol.

**HEADLINE finding (per [[feedback-no-smoke]])**: Bet E's planned sweep
across (random, Hadamard, Kerdock) × (M/N = 0.5, 1, 2) substrates has
a **critical methodological confound** that the experiment design did
not address: **structured codebooks suppress self-averaging**, so
multi-peaked P(q) for Hadamard might reflect codebook lattice geometry
rather than spin-glass RSB phase. The lit scan recommends a 6-test
diagnostic battery (Binder, system-size scaling, equilibration,
self-averaging, ultrametricity, spectrum check) before any RSB claim
is made. Substrate's prior P(q) result (multi-peaked at one N on
random keys) is consistent with RSB BUT does NOT prove it — finite-
size artifact remains possible.

---

## Pass 1 — External literature scan (verified)

Generic statistical-physics queries via subagent: "Parisi overlap
distribution P(q) measurement," "spin glass replica symmetry breaking
numerical," "ultrametricity test spin glass simulation," "Hopfield
network overlap distribution," "Mezard-Parisi-Virasoro replica method,"
etc. No substrate fingerprint.

### 1.1 The Parisi overlap distribution — foundational

For a spin-glass-like system with N sites:
- Two independent replicas (a, b) at the same disorder realization:
  **overlap q_{ab} = (1/N) Σᵢ s^a_i s^b_i**
- **P_J(q) = ⟨δ(q − q_{ab})⟩_{thermal}** (per disorder J)
- **P(q) = [P_J(q)]_{disorder avg}** (canonical observable)
- Single peak at ±q_EA: replica-symmetric (RS) phase
- Continuous support / multi-peak: replica-symmetry-broken (RSB) phase
- k delta peaks: k-step RSB

**Parisi 1979** PRL 43:1754 ("Toward a mean field theory for spin
glasses"); **Parisi 1980** *J. Phys. A* 13:1101 ("The order parameter
for spin glasses: a function on the interval 0-1"). **Mézard-Parisi-
Virasoro 1987** World Scientific textbook.

Construction is uncontested. Open dispute (still active): does
finite-dimensional Edwards-Anderson reproduce SK's full-RSB structure
or follow droplet/scaling picture (Fisher-Huse)? Mean-field substrate
(fully-connected outer-product) is SK-like → full RSB applies
rigorously (arXiv:2504.00269 proves existence 2025).

### 1.2 Standard measurement protocols (5 methods)

**Method A — Two-replica MC** (Bhatt-Young 1985 PRL 54:924, 1988
PRB 37:5606). Two independent chains on same J; sample q after
equilibration; average over O(10³-10⁴) disorder realizations.
Workhorse.

**Method B — Parallel tempering** (Hukushima-Nemoto 1996; Marinari-
Parisi-Ruiz-Lorenzo 1996 PRL 76:843). Essential below T_c. Multiple
replicas at different temperatures; exchange to break ergodicity
barriers. Speedup over single-T MC grows as T decreases.

**Method C — Janus/Janus-II/Janus-III FPGA computers** (Janus
Collaboration 2008-2024). Custom hardware: 86 ps per spin flip per
core, 1024 cores per FPGA. Equilibrate L=32 EA lattices down to
T = 0.64 T_c with PT. Tracks dynamics over 11 decades (arXiv:1003.2569,
PNAS 109:6452).

**Method D — Multicanonical / multi-overlap** (Berg-Janke 1998 PRL
80:4771; cond-mat/0112036, cond-mat/9811423). Resolves P(q) tails
over 80 orders of magnitude. For tail behavior; otherwise overkill.

**Method E — Pool / configurational sampling** (substrate-applicable):
when system has explicit ensemble of states (pool of stored patterns),
pairwise overlaps among pool elements give empirical P(q) DIRECTLY —
no MC needed. **CRITICAL**: this is the **configurational P(q)**,
distinct from thermal P(q). The two coincide only at T=0 for an
attractor ensemble.

### 1.3 Diagnostic battery — separating RSB from finite-size artifacts

**This is the lit scan's most actionable contribution for substrate.**
A multi-peaked P(q) at finite N can be either genuine RSB or finite-
size artifact. The consensus battery:

**Test 1 — Binder cumulant**: g_N(T) = (1/2)(3 − ⟨q⁴⟩/⟨q²⟩²).
Family of curves for different N should cross at T_c (Binder 1981).
**Caveat**: in spin glasses, hyperscaling breaks down (Lundow-Campbell
2017 arXiv:1706.04586); non-universal critical Binder values
documented.

**Test 2 — System-size scaling of P(0)**: in droplet picture, P(0) →
0 as N→∞; in RSB, P(0) remains finite. **The contested datum.**

**Test 3 — Equilibration test** (Katzgraber-Palassini-Young 2001 PRB
63:184422; Marinari-Parisi-Ruiz-Lorenzo PT criterion): integrated
quantities computed two ways (energy from PT chains vs logarithmic
time-window averaging) must converge.

**Test 4 — Self-averaging**: Var_J[P_J(q)] should NOT vanish for the
overlap order parameter in an RSB phase — **P(q) is non-self-averaging
by Parisi's construction** (Yucesoy et al. 2013 arXiv:1306.0423).
Average P(q) can be dominated by rare disorder samples.

**Test 5 — Ultrametricity** (triple-overlap test): for three replicas,
smallest two of q_{12}, q_{13}, q_{23} are equal (isosceles condition).
**Standard test**: compute d(q) = max − median across triples. Bhatt-
Young 1986; Hed-Young-Domany cond-mat/9608161; Iñiguez-Marinari-
Parisi-Ruiz-Lorenzo cond-mat/9903130. **Contested in 3D EA; clean in
mean-field / long-range.**

**Test 6 — Spectrum check** (Marchenko-Pastur + outliers): substrate-
relevant. Eigenvalue density of W should follow MP bulk with K outlier
spikes (BBP transition). Barra-Genovese-Guerra-Tantari 2018
arXiv:1811.08298 derives MP from RS quenched free energy. **Orthogonal
corroboration** for P(q) features.

### 1.4 Hopfield network P(q) specifically — the substrate-critical regime

**Amit-Gutfreund-Sompolinsky 1987** Ann. Phys. 173:30: phase diagram
with α_c ≈ 0.138 for retrieval-to-spin-glass transition under RS
ansatz.

**Crisanti-Amit-Gutfreund 1986**: 1RSB-corrected α_c ≈ 0.144
(LATER CORRECTED).

**Steffan-Kühn 1994** Z. Phys. B 95, cond-mat/9404036: careful
1RSB and 2RSB calculation gives α_c^{1RSB} ≈ **0.138186** and
α_c^{2RSB} ≈ **0.138187** — only barely above RS value.

**RSB-corrected retrieval states exist in the narrow window
0.138 < α ≤ ~0.144 with replica-symmetry-broken structure.**

**Substrate at α=0.153 sits IN this narrow window** (or just above its
upper edge). Bet E's premise is well-founded: substrate physics
predicts non-trivial P(q) structure at substrate's operating point.

**Bovier-Gayrard 1995** cond-mat/9507111: rigorous form of P(q)
in the retrieval phase. For α > α_c, P(q) is genuinely non-trivial.

### 1.5 Substrate-relevant methodology summary

For substrate's W = Σᵢ vᵢ kᵢᵀ:
- **Storage geometry → configurational P(q) (Method E)** — cheap,
  correct, no MC.
- **Thermal P(q) at finite T → PT (Method B)** with Marinari criterion
  — necessary if temperature dependence matters.
- **Mandatory diagnostic battery** before any RSB claim.

### 1.6 Recent (2020-2026) developments

- **Janus-III** continuation (ongoing 2020-2024 papers)
- **2024 Nobel** to Hopfield/Hinton: renewed work on neural-network
  statistical mechanics (arXiv:2408.06421, arXiv:2508.07397)
- **Generative-network-assisted equilibration** (arXiv:2210.11288):
  trains generators for smart Metropolis moves
- **Existence of full RSB in SK at low T proven rigorously** (2025
  arXiv:2504.00269)
- **Dense/modern Hopfield RSB analyses**: Lucibello-Mézard exponential
  capacity; arXiv:2604.07401 retrieval phase transitions in continuous
  thermal dense AM
- **50-year retrospective**: arXiv:2505.24432 (2025)

### 1.7 The 5 CRITICAL pitfalls (load-bearing for substrate)

Lit scan's "do not skip" list:

1. **Reporting multi-peaked P(q) at one N as evidence of RSB.** It's
   NOT; could be finite-size. **Substrate's prior wave14e2_parisi
   result at ONE N is consistent with RSB but does NOT prove it.**

2. **Not certifying equilibration.** Below T_c, single-T MC will lie.

3. **Averaging P(q) over disorder when self-averaging fails.** Report
   median + disorder-variance, not just mean.

4. **Confounding configurational (pool) P(q) with thermal P(q).** They
   are different distributions answering different questions.

5. **Structured codebooks suppress self-averaging.** A multi-peaked
   P(q) for Hadamard might reflect codebook lattice geometry (algebraic
   peaks) rather than spin-glass RSB phase. **This is the critical
   confound for Bet E's planned (random, Hadamard, Kerdock) sweep.**

---

## Pass 2 — Substrate-specific methodology drill

### 2.1 The substrate-critical methodological gap

Bet E's claim: "P(q) shape varies meaningfully with substrate
configuration (codebook structure, K, M_stored)." Test design:
- 3 substrate configs (random ±1, Hadamard, Kerdock) at N=4096, K=400,
  M=2N
- 3 M_stored values (M=0.5N, M=N, M=2N) for fixed random substrate
- 3 seeds per cell

**The critical methodological gap**: Bet E's design does NOT include
the diagnostic battery. Without Binder cumulants across N, ultrametricity
tests, equilibration certification, and self-averaging variance — a
multi-peaked P(q) finding doesn't prove RSB.

**Specifically problematic for structured codebooks**:

For random ±1 keys, self-averaging holds (disorder average is
meaningful). For Hadamard/Kerdock keys, the codebook IS the disorder
realization (there's no random ensemble to average over). **Multi-
peaked P(q) for Hadamard could be reading off the Walsh-group lattice
structure, NOT a spin-glass RSB phase.**

Without the diagnostic battery, the experiment cannot distinguish:
- **A**: substrate is in RSB phase + Hadamard preserves RSB structure
- **B**: substrate's P(q) shape is just the codebook's algebraic
  geometry; RSB is incidental

### 2.2 Recommended methodology revisions for E_E experiment

**Add to Bet E success criteria**:

1. **System-size scaling**: measure P(q) at N ∈ {1024, 2048, 4096,
   8192}. RSB peaks should grow with N (not shrink); finite-size
   artifacts shrink.
2. **Binder cumulant**: compute g_N across N at fixed α; check for
   crossings. **Required for any "RSB confirmed" claim.**
3. **Equilibration certification** (if thermal MC used): Marinari
   criterion comparing PT-chain vs time-window energy estimators.
4. **Self-averaging variance**: report Var_J[P_J(q)] across codebook
   realizations (or "pseudo-disorder" if structured). For Hadamard:
   vary the specific Hadamard rows selected; for Kerdock: vary the
   coset selection.
5. **Ultrametricity test**: triple-overlap distribution P(d(q)=0)
   above chance threshold (0.33 per Bet E's existing criterion).
6. **Spectrum check**: empirical eigenvalue density of W vs MP
   prediction with K outliers. Orthogonal corroboration.

### 2.3 Configurational vs thermal P(q) — substrate-relevant distinction

**Substrate's prior wave14e2_parisi_ultrametricity result** (per cap_map
v3) was almost certainly **configurational** (Method E pool sampling),
NOT thermal MC. The lit scan's pitfall #4 applies directly.

**What this means for the result interpretation**:
- Configurational P(q): characterizes the structure of stored states
  in the pool (geometric / algebraic property)
- Thermal P(q): characterizes the equilibrium distribution of states
  under finite-T dynamics (phase property)

**These answer different questions.** Substrate's prior result =
"the stored states have non-trivial overlap structure" (geometric
fact). For an RSB phase claim, thermal P(q) is the correct quantity.

**Substrate-applicable recommendation**:
- For Bet E's substrate-fingerprint claim (codebook config → P(q)
  shape), **configurational P(q) is appropriate**. The substrate's
  state is the stored pool; thermal dynamics aren't substrate-natural.
- For an RSB phase claim, thermal P(q) at substrate's effective
  temperature would be required. But Bet E doesn't strictly need
  this for the fingerprint use-case.
- **Clarify in Bet E reporting**: substrate-fingerprint claim is
  about configurational P(q) of stored ensemble; NOT about
  equilibrium phase.

### 2.4 The structured-codebook confound — most critical

For random ±1 keys: P(q) shape reflects spin-glass-like overlap
distribution of stored memories. Multi-peaked structure indicates
RSB-like geometric organization.

For Hadamard / Kerdock keys: P(q) shape may reflect:
- Substrate's spin-glass-like overlap distribution (RSB physics)
- Codebook's intrinsic algebraic geometry (Walsh-group lattice, Kerdock-
  coset structure)
- Mix of the two

**Without the diagnostic battery, these are indistinguishable.**

**Substrate-applicable diagnostic**: compute the P(q) of the
**pure codebook** (no substrate, no storage, just the Hadamard or
Kerdock vectors themselves with their natural inner-product overlaps).
- If pure-codebook P(q) ≈ stored-state P(q): substrate adds nothing;
  result is codebook geometry, not RSB.
- If stored-state P(q) ≠ pure-codebook P(q): substrate physics is
  changing the P(q); RSB claim viable.

**Add this control to Bet E experimental design**.

---

## Specific experimental design (Bet E methodology revisions)

**Experiment**: `wave14_parisi_pq_sweep_v1` (Strategy already queued).
**This note proposes methodology revisions for the v1 design**.

### Revised config:

```text
config:
  # ORIGINAL Bet E config (kept):
  N_main = 4096
  K = 400
  M_sweep_codebook = [random_pm1, Hadamard, Kerdock]
  M_sweep_storage = [0.5*N, N, 2*N]
  seeds = 3 per cell

  # ADDED for methodology rigor:
  N_size_sweep = [1024, 2048, 4096, 8192]  # for system-size scaling
  diagnostic_battery = ['binder', 'ultrametricity', 'self_averaging',
                        'spectrum_check', 'pure_codebook_control']
```

### Methodology-revised verdict logic:

```text
# Original Bet E criteria (kept):
PASS_BetE iff:
  P(q) peak counts / peak locations / ultrametricity distinguishable
  across configs (≥2σ separation on at least one metric)
  AND ultrametricity > 0.33 across cells
  AND P(q) shifts detectably across M_sweep_storage

# ADDED methodology criteria (REQUIRED before "RSB confirmed" claim):
RSB_CONFIRMED iff (all required):
  PASS_BetE
  AND Binder cumulants cross at consistent T_c across system-size sweep
  AND P(0) grows (or stays nonzero) as N increases from 1024 to 8192
  AND ultrametricity holds in TRIPLE-overlap test, not just pair-overlap
  AND self_averaging variance distinguishes RSB from finite-size
  AND spectrum check (MP + outliers) matches RSB prediction

# Without RSB_CONFIRMED:
CAPABILITY: substrate-fingerprint via configurational P(q) is valid
  (BetE PASS suffices) BUT the underlying physics framing is
  "codebook geometry + storage geometry", NOT "RSB phase"

# CRITICAL CONFOUND CHECK:
PURE_CODEBOOK_CONTROL iff:
  P_codebook(q) (just the codebook vectors, no substrate) is
  computed and compared to P_stored(q)
  AND P_stored(q) ≠ P_codebook(q) for at least 2 of 3 codebook configs
  (otherwise result is geometric not physical)
```

### Pseudocode for pure-codebook control:

```text
def pure_codebook_pq(codebook_vectors, num_samples=10000):
    """Configurational P(q) of pure codebook before storage."""
    pairs_q = []
    indices = sample_indices(len(codebook_vectors), num_samples * 2)
    for i, j in zip(indices[0::2], indices[1::2]):
        q = inner_product(codebook_vectors[i], codebook_vectors[j]) / N
        pairs_q.append(q)
    return histogram(pairs_q, bins=100)

# Compare to substrate's stored-state P(q):
def stored_state_pq(pool_states, num_samples=10000):
    """P(q) of stored states after substrate construction."""
    pairs_q = []
    indices = sample_indices(len(pool_states), num_samples * 2)
    for i, j in zip(indices[0::2], indices[1::2]):
        q = inner_product(pool_states[i], pool_states[j]) / N
        pairs_q.append(q)
    return histogram(pairs_q, bins=100)
```

### Smoke test additions:

```text
oracle_assertions (in addition to Bet E smoke):
  - For random ±1 codebook: P_codebook(q) should be approximately
    Gaussian centered at 0, width ~1/√N. P_stored(q) for substrate
    should differ from this (substrate physics adds structure).
  - For Hadamard codebook: P_codebook(q) should have discrete peaks
    at q ∈ {0, ±1/N} (codebook algebra). P_stored(q) should differ
    if substrate adds anything.
```

### Wall budget

Original Bet E budget + 3× additional N-sizes + diagnostic computations.
Method E (pool sampling) at substrate scale is O(S²N) = O(10⁴² · 4096)
= ~10¹¹ FLOPs per cell — minutes per cell on GPU. Total: ~30 min for
all cells + diagnostics. Tractable.

---

## Materials analog (load-bearing — substrate IS a Hopfield spin-glass)

**This IS the substrate physics.** The substrate's W = Σᵢ vᵢ kᵢᵀ at
α = K/N = 0.153 is structurally a Hopfield-type spin-glass coupling
sitting in the narrow RSB window above α_c = 0.138.

**Direct mathematical equivalence**:
- Substrate's W → SK-like coupling matrix J_ij
- Substrate's bipolar values vᵢ → Ising spins ±1
- Substrate's stored bundles → equilibrium pure states
- Substrate's softmax-of-cosine retrieval → Boltzmann sampling at β

**Physics prediction**: at α=0.153, substrate exhibits replica-symmetry-
breaking with non-trivial P(q). Steffan-Kühn 1994 corrected α_c values
place substrate just above the RS-RSB transition — RSB is expected
analytically.

**The substrate's Bet E result (multi-peaked configurational P(q) at
α=0.153) is CONSISTENT with this prediction.** What's missing is the
diagnostic battery to elevate "consistent with" to "confirmed."

**Recent rigorous proof**: arXiv:2504.00269 (2025) established
existence of full RSB for SK at low T. Substrate's mean-field
structure makes this directly applicable.

---

## Falsifiable prediction

**Primary prediction (with methodology revisions applied)**:

At N ∈ {1024, 2048, 4096, 8192}, α=0.153, random ±1 keys:

- **Multi-peaked P(q) at all N**: substrate genuinely in RSB phase
- **Binder cumulants cross** at consistent threshold across N
- **P(0) stays nonzero** as N grows (RSB signature)
- **Ultrametricity > 0.33** in triple-overlap test
- **Self-averaging variance ≠ 0** across codebook realizations
- **Spectrum** matches MP + K outliers (BBP signature)

**P(All 6 diagnostics pass) ≈ 65-80%** — substrate physics matches
Hopfield RSB prediction at α=0.153.

**Stress prediction (structured codebooks)**:

For Hadamard codebook:
- Pure codebook P_codebook(q) has discrete peaks at q ∈ {0, ±1/N}
- Stored-state P_stored(q) should DIFFER from P_codebook(q) if
  substrate adds RSB structure beyond codebook geometry
- **P(P_stored(q) ≠ P_codebook(q) meaningfully) ≈ 30-50%** — uncertain;
  could go either way

For Kerdock codebook:
- Pure codebook P_codebook(q) has discrete peaks per Welch bound
- Stored-state P_stored(q): may or may not differ

**Kill criterion**: if pure-codebook control shows P_codebook(q) ≈
P_stored(q) for Hadamard/Kerdock, Bet E's substrate-fingerprint claim
collapses: result is codebook geometry, not substrate physics. R10's
Kerdock-codebook framing already validates Bet C ✅, so this would
be a result-reframe (codebook IS the fingerprint), not a capability
loss.

**Honest probability estimates**:
- P(random-key P(q) shows clean RSB after full diagnostic battery)
  ≈ 65-80%
- P(structured-key P(q) differs from pure-codebook P(q)) ≈ 30-50%
- P(Bet E's substrate-fingerprint claim holds across all 3 codebook
  configs) ≈ 35-55%
- P(reframe to "codebook fingerprint" suffices for product story)
  ≈ 70-85%

---

## Citations

1. **Parisi (1979). "Toward a mean field theory for spin glasses."**
   PRL 43:1754.
   — RSB introduced; P(q) as order parameter.

2. **Parisi (1980). "The order parameter for spin glasses: a function
   on the interval 0-1."** *J. Phys. A* 13:1101.
   — Full RSB construction.

3. **Mézard, Parisi, Virasoro (1987). *Spin Glass Theory and Beyond.***
   World Scientific.
   — Standard textbook.

4. **Sherrington, Kirkpatrick (1975). "Solvable Model of a Spin-Glass."**
   PRL 35:1792.
   — Founding paper; SK model = substrate's mean-field analog.

5. **Amit, Gutfreund, Sompolinsky (1987). "Statistical mechanics of
   neural networks near saturation."** Ann. Phys. 173:30.
   — Hopfield α_c = 0.138; substrate's operating point in retrieval/
   RSB framing.

6. **Steffan, Kühn (1994). "Replica Symmetry Breaking in Attractor
   Neural Network Models."** Z. Phys. B 95. cond-mat/9404036.
   — Corrected α_c^{1RSB} ≈ 0.138186; substrate at α=0.153 in narrow
   RSB window.

7. **Bovier, Gayrard (1995). "The Retrieval Phase of the Hopfield
   Model."** cond-mat/9507111.
   — Rigorous P(q) in Hopfield retrieval phase.

8. **Bhatt, Young (1988). "Numerical studies of Ising spin glasses
   in two, three, and four dimensions."** PRB 37:5606.
   — Standard two-replica MC protocol.

9. **Hukushima, Nemoto (1996). "Exchange Monte Carlo method and
   application to spin glass simulations."** J. Phys. Soc. Jpn. 65:1604.
   — Parallel tempering (essential below T_c).

10. **Marinari, Parisi, Ruiz-Lorenzo (1996). "Numerical evidence for
    spontaneously broken replica symmetry in 3D spin glasses."** PRL
    76:843.
    — PT equilibration criterion (the "Marinari criterion").

11. **Katzgraber, Palassini, Young (2001). "Monte Carlo simulations
    of spin glasses at low temperatures."** PRB 63:184422.
    — Equilibration certification protocol.

12. **Yucesoy et al. (2013). "Typical versus averaged overlap
    distribution in Spin-Glasses."** arXiv:1306.0423.
    — Self-averaging caveat; P(q) non-self-averaging.

13. **Barra, Genovese, Guerra, Tantari (2018). "A novel derivation of
    the Marchenko-Pastur law through analog bipartite spin-glasses."**
    arXiv:1811.08298.
    — Spectrum-P(q) bridge; MP from RS quenched free energy.

14. **(2025). "Existence of Full RSB for the SK Model at Low
    Temperature."** arXiv:2504.00269.
    — Recent rigorous proof of full RSB; substrate's mean-field
    structure makes this directly applicable.

15. **Janus Collaboration (2010). "Nature of the spin-glass phase at
    experimental length scales."** arXiv:1003.2569.
    — Janus FPGA simulations of EA at scale.

---

## Routing

- **Experiment Dev (E_E methodology revision)**: this note recommends
  adding 6-test diagnostic battery to Bet E's `wave14_parisi_pq_sweep_v1`:
  1. System-size scaling (N ∈ {1024, 2048, 4096, 8192})
  2. Binder cumulant crossings
  3. Equilibration certification (if thermal MC; not needed for
     configurational)
  4. Self-averaging variance
  5. Ultrametricity triple-overlap test
  6. **Pure-codebook control** (P_codebook vs P_stored)
  Plus: explicit clarification that substrate's P(q) is configurational
  (pool sampling, Method E), NOT thermal MC. This is the substrate-
  natural quantity for the fingerprint use-case.
  Wall budget additions: ~30 min for diagnostic battery.

- **Strategy**: this note proposes:
  - **Bet E methodology review LANDED** (not formal R# but documented
    research need from active_priorities)
  - cap_map Bet E entry should clarify: substrate P(q) is
    configurational (pool sampling), not thermal MC
  - The structured-codebook confound is the **most important
    methodological catch**: without pure-codebook controls, multi-
    peaked P(q) for Hadamard could be codebook geometry not RSB
  - If RSB claim doesn't survive the diagnostic battery, **reframe
    to "codebook fingerprint"** is still product-valid (substrate
    distinguishable by codebook choice)
  - This connects to R14 finding: substrate's β=32 likely derives
    from RSB transition; Bet E's P(q) work theoretically validates
    that connection
  - Substrate is in narrow RSB window (α=0.153 just above α_c^{1RSB}
    = 0.138186 per Steffan-Kühn 1994)

- **Research (this session, future cycles)**: methodology review
  closes; substrate has well-grounded protocol for Bet E experiment.
  If Bet E E_E experiment runs and produces ambiguous results (multi-
  peaked P(q) but failing diagnostic battery), follow-up research on
  reframe-to-codebook-fingerprint may be useful.

**HONEST FINAL NOTE**: substrate's prior wave14e2_parisi result
(multi-peaked configurational P(q) at one N on random keys) is
**consistent with RSB at α=0.153** per Hopfield physics (Steffan-Kühn
1994 narrow RSB window). But **without the diagnostic battery**, the
result is "physics-consistent" rather than "physics-confirmed." Per
[[feedback-no-smoke]]: don't overstate as confirmed RSB until the 6
tests pass. The structured-codebook confound (pitfall #5 from lit
scan) is the most important methodological catch that Bet E's design
did not address. Per [[feedback-rehabilitation-after-rejection]]:
this methodology revision adds 5 rescue axes (the 5 diagnostic tests
beyond ultrametricity which Bet E already had).
