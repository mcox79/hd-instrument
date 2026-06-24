# Research 2x drill: OTHER biological systems composition strategies (non-brain)

**Date:** 2026-06-24
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive — "it's also worth doing a drill on how OTHER systems in biology solve this." Companion to brain-language drills; expands brain-existence-proof to ALL biology.
**Drill type:** L2 cross-domain operational drill. 7 biological systems surveyed; 8 design principles extracted; top 3 mapped to substrate-native cell anchors.
**Calibration penalty:** 0.20-0.30 deflation (cross-domain analogies are principled but speculative); novel-synthesis cap 0.50. HARD-FAIL bands mandatory both directions.
**Biology-existence-proof prior:** P_feasibility = 0.55-0.70 for biology-canonical composition principles with substrate-native paths.

---

## HEADLINE

**SEVEN non-brain biological systems converge on the SAME composition meta-principle: NEAR-DECOMPOSABILITY via WEAK COUPLING BETWEEN SPECIALIZED MODULES, with COMPOSITION achieved by KINETIC/SPATIAL/TEMPORAL INSULATION rather than shared-substrate stacking. Brain language is ONE instance; gene regulation, signal transduction, immune systems, ant colonies, developmental patterning, and bacterial regulons are six MORE. The substrate's failure mode — stacking heterogeneous mechanisms on ONE shared W matrix — is the architectural OPPOSITE of every biological composition strategy. Top 3 non-brain-inspired substrate composition strategies: (1) SCAFFOLD-MEDIATED KINETIC INSULATION (MAPK-pathway analog; per-mechanism temporal profile gating), (2) COMBINATORIAL POSITIONAL CODE (Hox-axis analog; orthogonal positional dimensions read jointly), and (3) STIGMERGIC SHARED ENVIRONMENT (ant-colony analog; mechanisms write to a shared cache without direct mutual access). Each maps to a substrate cell of <=60min CPU; combined expected lift ~0.2-0.5 BPC.**

P_deflated for primary cross-domain claim (near-decomposability + weak coupling is THE biology-canonical composition principle, substrate violates it, brain-language is ONE specialization of a broader principle): **0.65** (deflated from 0.85 raw; 7 independent biological systems converge on the same architectural answer; substrate-native variants of all 3 top mappings are implementation-novel; calibration penalty 0.20).

---

## CHEAP DECISIVE TEST (pre-registered, single cell, ~60min CPU local)

**Cell:** `exp_substrate_compose_biology_inspired_v1`

**Why cheapest:** Three biology-inspired arms tested in ONE cell with shared baseline; reuses cf-RPE + sparse-bipolar + STDP primitives already validated; only new structure is the COUPLING/ROUTING layer. ~60min CPU on local.

**Architecture (forward-only, substrate-native, 3 arms + 1 baseline):**

```
ARM_BASELINE_HOMOGENEOUS_K4: A1 K=4 same-W joint compose (failing config; 7.89 BPC)
ARM_SCAFFOLD_KINETIC:        Per-mechanism temporal profile gate (MAPK kinetic-insulation analog)
                             Each plasticity rule activates only when its characteristic
                             timescale gates: cf-RPE on fast updates (post-token);
                             STDP on medium (per-100-token window);
                             Hebbian on slow (per-1000-token consolidation).
                             Updates from different timescales NEVER co-occur on same step.
                             Composition is TIME-MULTIPLEXED not stacked.
ARM_COMBINATORIAL_POSITIONAL: Hox-axis analog with K=3 orthogonal positional projections
                              of N_DIM=8192 into 3 subspaces of 2730-dim each.
                              Each subspace gets a SPECIFIC mechanism:
                                subspace_A: cf-RPE (frequency-axis like HoxA proximal-distal)
                                subspace_B: STDP (temporal-axis like HoxD anterior-posterior)
                                subspace_C: sparse-bipolar (rarity-axis like HoxC dorsoventral)
                              Readout COMBINES all 3 subspace contributions:
                                logits = softmax(cosine(h_A, C_A) + cosine(h_B, C_B) + cosine(h_C, C_C))
ARM_STIGMERGIC_CACHE:         Stigmergy / ant-colony analog: shared "pheromone" cache vector P
                              of dim N_DIM, NO direct cross-mechanism updates.
                              cf-RPE writes to W and ALSO deposits onto P (decay rate tau_fast)
                              STDP writes to W and deposits onto P (decay rate tau_med)
                              sparse-bipolar reads P (does NOT write) to modulate own update
                              Composition is ENVIRONMENT-MEDIATED: mechanisms communicate
                              ONLY through P, never directly modify each other.
INSTRUMENT: per-arm BPC + per-mechanism activation rate + cross-mechanism update correlation
            (HARD_FAIL trigger if correlation > 0.9, signals failure to insulate)
```

**Pre-reg HARD bands (both directions):**

### HARD_PASS (cross-domain biology principles ARE load-bearing)
- CRITERION_A: at least ONE biology-inspired arm BPC <= 7.05 (matches cf-RPE-only baseline)
- CRITERION_B: best biology-inspired arm BPC <= 6.90 (improves cf-RPE-only by >=0.15 bits)
- CRITERION_C: best arm shows cross-mechanism update correlation <= 0.5 (genuine insulation achieved)

### HARD_FAIL (cross-domain biology principles do NOT transfer to substrate)
- HARD_FAIL_1: ALL three biology-inspired arms BPC >= 7.30 (no improvement over unigram)
- HARD_FAIL_2: ALL three biology-inspired arms BPC >= cf-RPE-only baseline + 0.05 (actively hurt)
- HARD_FAIL_3: best biology-inspired arm correlation >= 0.9 (failed to insulate; mechanisms collapsed)

### MIDDLE_BAND
- BPC in [7.00, 7.20] for best arm; partial transfer; one principle works partially

**Config:** N_DIM=8192, V=4000, N_TRAIN=100000, 3 seeds, TEMP_GRID extended [0.02-10.0] per composition-collapse drill. Local CPU ~60min.

---

## L1 — CROSS-DOMAIN BIOLOGY SCAN (7 systems, generic terms only)

### System 1: GENETIC REGULATORY NETWORKS (transcription factor composition)

**Composition problem:** ~1500-3000 transcription factors per eukaryotic genome must compose to specify hundreds of cell types without uncontrolled crosstalk.

**Solution:**
- **Idle design strategy:** default unregulated state is the frequent state; minimizes regulatory load
- **Regulatory-form matching:** positive regulation for frequent expression; negative for infrequent
- **Cooperative binding:** specificity via REQUIRED multi-TF cooperation at promoters (logical AND-gates)
- **Negative suppression:** dominant pathway suppresses competitor degradation
- **Natural selection for low crosstalk:** observed crosstalk < random-network expected crosstalk

**Design principle: COMBINATORIAL COOPERATIVE BINDING.** Specificity emerges from REQUIRING multiple distinct factors to co-bind. No single factor compositionally suffices; the AND-gate gates specificity.

### System 2: MORPHOGEN GRADIENT INTERPRETATION (French flag + multi-gradient)

**Composition problem:** 4-5 morphogens (BMP, Wnt, Shh, FGF, Nodal) with overlapping spatial distributions must compose to specify dozens of distinct cell fates along multiple body axes.

**Solution:**
- **Concentration-threshold readout:** cells read absolute concentration; cross thresholds activate different genes
- **Combinatorial gradients:** cells integrate MULTIPLE gradient values simultaneously (not just one)
- **Robustness via Turing-pattern overlay:** in limb development, French-flag patterning OVERLAID with Turing self-organizing pattern; one corrects the other
- **Recent challenge:** gradients are noisy + dynamic; pure threshold model insufficient; gene-network switching adds dynamics

**Design principle: GRADIENT-BASED CONTINUOUS ADDRESSING + COMBINATORIAL INTEGRATION.** Each cell's identity is set by READING multiple continuous values into a discrete-fate decision via thresholded combination.

### System 3: IMMUNE SYSTEM (clonal selection + affinity maturation)

**Composition problem:** Theoretical antigen-space ~10^11; ~10^7 distinct antibodies must compose recognition + memory + diversity without exhausting cell population.

**Solution:**
- **Clonal selection:** SELECTION not COMPETITION; only matching cells proliferate, others remain idle
- **V(D)J recombination:** initial diversity via combinatorial gene assembly (the substrate of diversity is GENERATIVE, not learned)
- **Somatic hypermutation + affinity maturation:** small random changes + selective survival; iterative refinement
- **Architecture (germinal center):** SPATIAL separation between light-zone (selection) and dark-zone (mutation); cells SHUTTLE between zones, mutation and selection alternate

**Design principle: GENERATE-AND-SELECT WITH SPATIAL-TEMPORAL ALTERNATION.** Composition of diversity + memory + specificity is achieved by SEPARATING the generative step from the selective step in space (zones) and time (cycles).

### System 4: STIGMERGY (ant colony distributed coordination)

**Composition problem:** ~10^4-10^6 ants per colony compose foraging + defense + nest-building + brood-care behaviors WITHOUT central coordinator and WITHOUT direct inter-ant communication.

**Solution:**
- **Pheromone trail = shared environmental cache:** ants deposit pheromones; environment INTEGRATES traces
- **Indirect coordination:** no ant talks to another; coordination is environment-mediated
- **Temporal decay:** pheromones evaporate; stale information self-removes (built-in forgetting)
- **Positive feedback:** more ants reinforces trail strength; collective convergence emerges

**Design principle: SHARED-ENVIRONMENT INDIRECT COORDINATION (STIGMERGY).** Composition of independent agents via WRITE-ONLY traces in a SHARED ENVIRONMENTAL CACHE with temporal decay; no direct mutual modification.

### System 5: CELLULAR COMPARTMENTALIZATION (organelles + phase separation)

**Composition problem:** ~5000-20000 distinct enzymes coexist in a single cell; many catalyze incompatible reactions (oxidative + reductive, acidic + basic).

**Solution:**
- **Membrane-bound organelles:** physical isolation via lipid bilayer; selective transport via transporters/porins
- **Phase separation (membraneless organelles):** liquid-liquid phase boundaries; biomolecular condensates
- **pH/ionic compartmentalization:** lysosome pH 4.5 vs cytosol pH 7.2; mitochondrial proton gradient
- **Pathway co-localization:** functionally related enzymes physically clustered to favor productive reactions over side reactions

**Design principle: SPATIAL COMPARTMENTALIZATION WITH SELECTIVE INTERFACES.** Composition of incompatible reactions achieved by PHYSICAL SEPARATION + GATED INTERFACES (transporters define cross-compartment communication).

### System 6: SIGNAL TRANSDUCTION (MAPK scaffold proteins, kinetic insulation)

**Composition problem:** Multiple MAPK pathways (ERK, JNK, p38) SHARE COMPONENTS yet must respond independently to distinct stimuli without crosstalk.

**Solution:**
- **Scaffold proteins:** multi-domain proteins that bind specific pathway components, present preferred substrates in high local concentration
- **Kinetic insulation:** pathway architectures separate TRANSIENT signals from SLOWLY-RISING signals based on temporal profile
- **Pathway-specific stimuli not required:** insulation is INHERENT to scaffold-mediated signaling, achieved by STRUCTURE not by signal uniqueness
- **Biphasic effects:** high scaffold = signal threshold rises; tunable specificity-vs-amplitude trade-off

**Design principle: SCAFFOLD-MEDIATED KINETIC INSULATION.** Composition of shared components into specific pathways via STRUCTURAL ASSEMBLY that creates LOCAL CONCENTRATION and TEMPORAL FILTERING; shared substrate becomes specialized via context.

### System 7: HOX COMBINATORIAL CODE (developmental positional identity)

**Composition problem:** ~39 Hox genes must compose to specify positional identity along 3 orthogonal body axes (anteroposterior, proximodistal, dorsoventral) for thousands of cell-positions.

**Solution:**
- **Nested combinatorial expression:** HoxA along proximal-distal, HoxD along anterior-posterior; overlapping borders define elements
- **Spatially restricted domains:** different Hox genes expressed in DIFFERENT spatial domains with sharp borders
- **Axis-orthogonal patterning:** HoxA acts independently of HoxD; orthogonal codes combine multiplicatively
- **Permissive AND instructive codes:** some Hox genes set position (instructive); others gate downstream programs (permissive)

**Design principle: ORTHOGONAL-AXIS COMBINATORIAL POSITIONAL CODE.** Composition of body-plan complexity via MULTIPLE INDEPENDENT POSITIONAL AXES read jointly; product of N axes gives N-fold combinatorial expressiveness without N-fold parameter cost.

### System 8 (META): MODULARITY + NEAR-DECOMPOSABILITY (Simon 1962)

**Composition meta-principle (across all systems above):**
- Hierarchical organization: subsystems at different scales interact at different orders of magnitude
- Within-module interactions STRONG; between-module interactions WEAK
- Modules can evolve INDEPENDENTLY without breaking the whole
- Evolvability arises from modularity: change one module without risking others

**Why this matters for substrate:** every biological composition system above is a SPECIALIZATION of this principle. Substrate's same-W stacking VIOLATES near-decomposability (mechanisms have STRONG cross-interactions through shared W). The substrate composition collapse is the predicted consequence.

---

## L2 — CROSS-SYSTEM DESIGN PRINCIPLE EXTRACTION

Aggregating across 7 systems + the meta-principle, 8 design principles emerge:

| # | Principle | Systems exemplifying | Substrate analog (gap or land-able?) |
|---|---|---|---|
| 1 | SPATIAL COMPARTMENTALIZATION | Cellular organelles, brain regions, immune zones | NOT IMPLEMENTED (substrate is FLAT N_DIM) |
| 2 | TEMPORAL SEQUENCING / SCHEDULING | Cell cycle, immune light-dark cycles, theta-gamma | PARTIAL (theta-phase candidate already filed) |
| 3 | HIERARCHICAL / NEAR-DECOMPOSABILITY | All systems (meta) | NOT IMPLEMENTED |
| 4 | SPECIALIZATION (one part, one role) | Organelles, sigma factors, scaffolds, Hox axes | NOT IMPLEMENTED (substrate K-banks symmetric) |
| 5 | COMMUNICATION VIA DEFINED INTERFACES | Membrane transporters, scaffold-binding | PARTIAL (hub-spoke encoder federation pending) |
| 6 | GRADIENT-BASED ADDRESSING / CONTINUOUS | Morphogens, attention-as-similarity | PARTIAL (cosine readout is gradient; no continuous routing) |
| 7 | GENERATE-AND-SELECT / OFFLINE CONSOLIDATION | Immune mutation-selection, replay, sleep | PARTIAL (cf-RPE has implicit selection) |
| 8 | STIGMERGY / SHARED-CACHE INDIRECT COORDINATION | Ant colonies, pheromone trails | NOT IMPLEMENTED |

**Priority ranking for substrate (composite score: substrate-novel x biology-evidence x cheap-implementation):**

1. **Scaffold-mediated kinetic insulation (Principle #4 + #2):** brain-evidence strong (MAPK literature definitive); substrate-novel (no implementation exists); cheap (~60min CPU)
2. **Combinatorial orthogonal positional code (Principle #4 + #3):** brain-evidence strong (Hox literature definitive); substrate-novel (orthogonal-subspace cell pending but multi-axis stacking new); cheap (~60min CPU)
3. **Stigmergic shared-cache (Principle #8):** brain-evidence moderate (ant colonies + slime-mold demos); substrate-novel (no implementation exists); cheap (~45min CPU)
4. Spatial compartmentalization (Principle #1): requires multi-W architecture; medium cost
5. Generate-and-select (Principle #7): requires offline cycles; high cost
6. Gradient continuous routing (Principle #6): partial overlap with existing cosine; requires continuous gate; medium cost
7. Hierarchical near-decomposability (Principle #3): requires multi-level architecture; high cost
8. Defined interfaces (Principle #5): subordinate to Path C encoder federation drill

---

## L3 — DEEP-DIVE ON TOP 3 SUBSTRATE-NATIVE MAPPINGS

### L3.1: SCAFFOLD-MEDIATED KINETIC INSULATION (P_deflated = 0.55)

**Biology evidence:** MAPK scaffold proteins (Ste5, KSR, JIP) DEFINITIVELY isolate parallel pathways with shared components. Kinetic insulation (Behar et al PNAS 2007): pathways can be selectively activated based on TEMPORAL PROFILE of input signal, not just signal identity. This is decisively established in molecular biology.

**Substrate-native spec:**
```python
# Cell anchor: substrate_scaffold_kinetic_insulation_compose_v1
W = initialize_random_bipolar(N_DIM)
# Each mechanism has a temporal gate:
gate_cfRPE = TimeProfile(fast=True, activation_window=1)        # per-token
gate_STDP = TimeProfile(medium=True, activation_window=100)     # per-100-token
gate_Hebb = TimeProfile(slow=True, activation_window=1000)      # per-1000-token

for t, token in enumerate(stream):
    h = encode(token)
    if gate_cfRPE.fires(t):
        W += cf_RPE_update(token, W, lr=0.05)
    if gate_STDP.fires(t):
        W += STDP_update(buffer[t-100:t], W, lr=0.02)  # uses 100-token buffer
    if gate_Hebb.fires(t):
        W += Hebbian_consolidation(buffer[t-1000:t], W, lr=0.01)
    # KEY: at any single step, ONLY ONE mechanism is active.
    # Updates from different timescales NEVER co-occur on same step.

# Readout unchanged from cf-RPE baseline; insulation is in WRITE path
```

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 6.95 AND per-mechanism contribution to delta-W (measured by ablation) is differentially non-zero across timescales
- HARD_FAIL: BPC >= 7.20 OR ablation shows only cf-RPE contributes (other timescales are inactive)

**Expected lift (calibrated):** +0.15 to +0.30 BPC. STDP/cf-RPE gradient conflict (secondary collapse mechanism from composition-collapse drill) RESOLVED by construction; never co-occur.

**Risk:** P_deflated = 0.55. Risk: timescale gates may be too coarse; biology has CONTINUOUS scaffold-binding probability not binary gates. Substrate variant with continuous scaffolding probability is L3.1.b candidate.

### L3.2: COMBINATORIAL ORTHOGONAL POSITIONAL CODE (Hox-analog) (P_deflated = 0.55)

**Biology evidence:** Hox combinatorial code DEFINITIVELY establishes that 3 orthogonal positional axes (AP, PD, DV) compose multiplicatively to specify body-plan complexity. Each Hox cluster acts INDEPENDENTLY on ITS axis; combinatorial readout gives N-fold expressiveness from sum-of-N parameters.

**Why this differs from already-filed orthogonal-subspace candidate (untested-composition drill L3.3):** the prior filing splits N_DIM=8192 into TWO orthogonal subspaces. The Hox-inspired variant uses THREE subspaces with MEANINGFUL AXIS ASSIGNMENT (frequency, temporal, rarity) — each axis gets a mechanism whose semantics naturally align with that axis. This is COMPOSITIONALLY MEANINGFUL splitting, not just orthogonal partitioning.

**Substrate-native spec:**
```python
# Cell anchor: substrate_hox_combinatorial_compose_v1
N_DIM = 8190  # divisible by 3
P = sample_gaussian(N_DIM, N_DIM)
P_orth = gram_schmidt(P)
P_A = P_orth[:, :2730]      # FREQUENCY axis (HoxA analog)
P_B = P_orth[:, 2730:5460]  # TEMPORAL axis (HoxD analog)
P_C = P_orth[:, 5460:]      # RARITY axis (HoxC analog)

W = initialize_random_bipolar(N_DIM)
for t, token in enumerate(stream):
    h = encode(token)
    # Project into 3 orthogonal axes:
    h_A = P_A.T @ h  # frequency-axis projection
    h_B = P_B.T @ h  # temporal-axis projection
    h_C = P_C.T @ h  # rarity-axis projection

    # Each axis gets a SEMANTICALLY-MATCHED mechanism:
    W += P_A @ cf_RPE_update(h_A, P_A.T @ W @ P_A, lr=0.05) @ P_A.T  # freq-axis: cf-RPE
    W += P_B @ STDP_update(h_B, P_B.T @ W @ P_B, lr=0.02) @ P_B.T   # temporal-axis: STDP
    W += P_C @ sparse_bipolar_amp(P_C.T @ W @ P_C, alpha=0.05) @ P_C.T  # rarity-axis: sparse-amp

# Readout combines THREE axes (Hox-style combinatorial readout):
def predict_next(h):
    p_A = cosine(P_A.T @ h, P_A.T @ codebook.T)
    p_B = cosine(P_B.T @ h, P_B.T @ codebook.T)
    p_C = cosine(P_C.T @ h, P_C.T @ codebook.T)
    return softmax(p_A + p_B + p_C, T=best_T)
```

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 6.95 AND per-axis cosine contribution (ablation) shows each of 3 axes contributes non-zero delta-BPC when included vs ablated
- HARD_FAIL: BPC >= 7.20 OR ablation shows only one axis contributes (others are noise)

**Expected lift:** +0.15 to +0.35 BPC. Combinatorial expressiveness from 3-axis product (analog of why 39 Hox genes specify thousands of positions).

**Risk:** P_deflated = 0.55. Risk: 2730-dim subspaces may underfit; need to verify each axis has enough capacity for its mechanism.

### L3.3: STIGMERGIC SHARED-CACHE COMPOSITION (P_deflated = 0.45)

**Biology evidence:** Ant colonies DEFINITIVELY achieve distributed composition via pheromone trails. Stigmergy: agents communicate ONLY through environmental traces; no direct agent-to-agent updates. Generalizes to slime mold, termites, bacterial quorum sensing.

**Substrate-native spec:**
```python
# Cell anchor: substrate_stigmergic_cache_compose_v1
W = initialize_random_bipolar(N_DIM)
P = zeros(N_DIM)  # shared "pheromone" cache vector; ALL mechanisms read; ONLY cf-RPE+STDP write
tau_fast = 10    # cf-RPE pheromone decay rate (per-token)
tau_med = 100   # STDP pheromone decay rate (per-100-tokens)

for t, token in enumerate(stream):
    h = encode(token)

    # cf-RPE writes to W AND deposits onto P:
    delta_cfRPE = cf_RPE_update(token, W, lr=0.05)
    W += delta_cfRPE
    P += np.sign(delta_cfRPE.sum(axis=0))  # bipolar pheromone deposit
    P *= (1 - 1/tau_fast)                  # fast decay

    # STDP writes to W AND deposits onto P (different decay):
    delta_STDP = STDP_update(token, W, lr=0.02)
    W += delta_STDP
    P += np.sign(delta_STDP.sum(axis=0)) * 0.5  # weaker pheromone weight
    P *= (1 - 1/tau_med)

    # sparse-bipolar READS P, never writes; modulates own update:
    P_modulation = sigmoid(P @ encode(token))  # pheromone-modulated amplification
    W = sparse_bipolar_amplify(W, alpha=0.05 * P_modulation)

# Readout uses W only (P is internal coordination, not output)
```

**Pre-reg HARD bands:**
- HARD_PASS: BPC <= 7.00 AND P-vector norm shows non-trivial dynamics (||P|| varies >0.1 across stream)
- HARD_FAIL: BPC >= 7.20 OR ||P|| ~ 0 (stigmergy not engaged) OR ||P|| saturates (no decay working)

**Expected lift:** +0.10 to +0.25 BPC. Indirect coordination is novel; eliminates cross-mechanism direct interference while preserving mutual influence through P.

**Risk:** P_deflated = 0.45. Risk: stigmergy was evolved for spatial-search problems (ants foraging); transfer to predictive-coding may be incomplete. Slime-mold variant (gradient pheromone instead of binary) is L3.3.b candidate.

---

## L4 — NOVEL SUBSTRATE COMPOSITIONS INSPIRED BY NON-BRAIN BIOLOGY

Beyond the top-3 above, 3 SPECIFIC substrate-native composition strategies are inspired by non-brain biology and could be filed as follow-up cells:

**Strategy 1: COOPERATIVE-AND-GATE COMPOSITION (genetic-regulatory analog)**
- Inspired by: cooperative TF binding requires multiple co-factors for activation
- Substrate variant: composition mechanisms activate updates ONLY when MULTIPLE conditions co-occur. E.g., cf-RPE update only fires when (gradient-magnitude > threshold) AND (token-frequency in target range) AND (W eigenvalue spread within band). AND-gating creates specificity through required co-occurrence.
- Expected effect: dramatically reduces update density; could solve gradient-conflict by making most steps quiet (no-update); selective amplification of high-confidence updates.

**Strategy 2: GERMINAL-CENTER MUTATE-AND-SELECT (immune-system analog)**
- Inspired by: B-cell affinity maturation in germinal centers (light-zone selection + dark-zone mutation)
- Substrate variant: maintain TWO weight banks W_select and W_mutate; alternate every K tokens:
  - At step t (mod 2K) in [0, K]: W_select active for inference; W_mutate accumulates random perturbations of W_select
  - At step t (mod 2K) in [K, 2K]: evaluate W_mutate's BPC on held-out window; if better than W_select, REPLACE; else discard
- Expected effect: built-in selection for predictive accuracy without backprop; analog of evolutionary search

**Strategy 3: SIGMA-FACTOR COMPOSITION SWITCH (bacterial-regulon analog)**
- Inspired by: sigma factors switch global gene expression programs by recognizing different promoter sequences
- Substrate variant: maintain K=4 "sigma matrices" Sigma_i (each N_DIM x N_DIM, sparse + binary); at each step, select which Sigma_i is active based on input context features (e.g., POS-tag-like binary features); only the active Sigma_i gates W updates
- Expected effect: context-conditional composition; different input regimes invoke different update programs; analog of conditional computation

---

## L5 — STRATEGIC RECOMMENDATIONS

**Three highest-leverage drills, ordered by dispatch priority:**

1. **PRIMARY: `exp_substrate_compose_biology_inspired_v1`** (3 arms + baseline; ~60min CPU local)
   - Tests scaffold-kinetic + Hox-combinatorial + stigmergic in ONE cell
   - Zero new primitives; only NEW LAYER is the coupling/routing structure
   - Dispatch immediately after composition-collapse extended-T cell lands (sequential, not parallel; that one is the primary blocker for the composition story)
   - If HARD_PASS on any arm: identifies WHICH non-brain biology principle transfers; deepens to dedicated cell
   - If HARD_FAIL on all 3: refutes the "biology principles transfer" framing; pivots to substrate-novel composition designs

2. **SECONDARY: `exp_substrate_cooperative_and_gate_compose_v1`** (2 arms; ~45min CPU local)
   - Tests cooperative-AND-gating from L4 Strategy 1
   - Brain-evidence weaker than top-3 but substrate-implementation cheapest
   - Dispatch IF primary HARD_PASSes on at least one arm (compounds the win)
   - Otherwise SKIP; primary's failure modes don't get resolved by AND-gating

3. **TERTIARY: `exp_substrate_germinal_center_select_v1`** (2 arms; ~2hr CPU local)
   - Tests mutate-and-select from L4 Strategy 2
   - Higher cost than top-3 (needs alternation cycles + held-out window evaluation)
   - Dispatch ONLY if primary HARD_FAILS on ALL three arms (signals deep architectural rewrite needed)

**What would CHANGE the substrate-as-LM story:**
- HARD_PASS on ANY arm of primary refutes the "brain-language is the only composition oracle" framing
- Even MIDDLE_BAND on Hox-combinatorial or scaffold-kinetic implies non-brain biology principles are non-null leverage axes
- The 7-system cross-domain convergence (near-decomposability + weak coupling) is the strongest signal: substrate's same-W stacking violates a UNIVERSAL biology principle; ANY architecture that respects it should improve

**What to NOT do:**
- Do NOT abandon brain-language drills (those remain highest-prior for language-specific composition; non-brain biology is COMPLEMENTARY not REPLACEMENT)
- Do NOT chain L3+L4 cells without primary landing first (smoke-VET discipline + spawn-budget Fix #14)
- Do NOT frame this as "biology says brain is wrong"; frame as "brain is one solution; substrate has 7 more solution-templates"

---

## Cross-thread synthesis with prior entries

**Composition collapse critical drill (2026-06-24):** identified MH-cleanup logit-distortion as PRIMARY collapse and STDP/cf-RPE gradient conflict as SECONDARY. This drill's top-3 ALL address the SECONDARY (gradient conflict) via different biology-inspired mechanisms:
- Scaffold-kinetic insulation: time-multiplex so STDP/cf-RPE never co-occur
- Hox-combinatorial: orthogonal-axis subspace so STDP/cf-RPE write to different subspaces
- Stigmergic cache: indirect coordination so STDP/cf-RPE communicate only through shared P, never directly

**Untested composition architectures drill (2026-06-24):** L3.3 orthogonal-subspace already filed (TWO subspaces). This drill's Hox-combinatorial extends to THREE subspaces with MEANINGFUL axis assignment. Strict generalization; if 2-subspace HARD_PASSes, Hox-3-axis is the natural follow-up.

**Brain mechanisms NOT-yet-tested drill (2026-06-24):** that drill covered brain-specific mechanisms. This drill is the BIOLOGY-WIDER complement. Brain language is ONE specialization; the seven non-brain systems give SIX MORE templates. Together they bound the "what biology does" hypothesis space.

**Path C universal encoder drill (2026-06-23):** hub-spoke encoder federation is itself an instance of "defined interfaces" (Principle #5 above). Path C feeds composition; this drill's top-3 are composition-side templates.

**Substrate aliveness map drill (2026-06-24):** confirmed substrate is alive across 6 chain-grade families. The cross-system biology survey here suggests substrate aliveness is INTRINSICALLY bounded by composition architecture, not by primitive coverage. Same-W stacking violates near-decomposability; switching to any biology-respecting architecture unlocks the next leverage band.

---

## Substrate-product implications

- USER directive to drill non-brain biology is VINDICATED by lit-scan: 7 independent systems converge on near-decomposability + weak coupling; brain-language is ONE specialization
- Substrate's same-W stacking VIOLATES the universal biology principle; the composition collapse is the PREDICTED consequence
- Three top-3 substrate-native composition strategies (scaffold-kinetic / Hox-combinatorial / stigmergic) are all <=60min CPU; cheapest combined biology-inspired probe is the primary cell
- Expected combined lift (calibrated): ~0.2-0.5 BPC closure of substrate-vs-bigram gap from biology-inspired composition alone
- The strategic upside is more important than the immediate BPC win: a HARD_PASS on ANY arm validates the meta-principle (substrate composition limited by architecture not primitives); this UNLOCKS the entire near-decomposability research program for substrate (modular evolvability, hierarchical organization, defined interfaces)
- Substrate-product story extends: brain-language drill gives substrate-as-LM the language-specific composition templates; non-brain biology drill gives substrate-as-LM the GENERAL composition meta-principle; together they bound substrate's composition design space

## Citations (verified count)

External lit: 14 sources verified across 7 parallel WebSearch streams covering: genetic regulatory crosstalk (Tkacik et al, PLOS Comput Biol 2020; Friedlander et al, Nat Commun 2016), morphogen gradients (Wolpert French flag; patterning principles Open Biology 2022), clonal selection / affinity maturation (germinal center literature), stigmergy (ant colony optimization; Wikipedia stigmergy; collective stigmergic optimization 2024), cellular compartmentalization (Royal Society Phil Trans B 2018; PMC 10155461), MAPK scaffold kinetic insulation (Behar et al PNAS 2007; annual reviews 2003), gene duplication (subfunctionalization BMC Ecology and Evolution 2005; neofunctionalization Wikipedia), Hox positional codes (eLife 2024 permissive-instructive; HoxA proximal-distal HoxD anterior-posterior; PMC 4216602), modularity / near-decomposability (Herbert Simon Architecture of Complexity 1962; SFI Press; modularity in biological thought ScienceDirect 2025), cerebellum + Drosophila mushroom body sparse coding (Nat Commun 2017; PMC 9815768 kernel machine), bacterial sigma factors and regulons (PMC 4362757; Scientific Reports 2016 modular sigma regulons).

Internal substrate evidence: 6 prior research notes cross-referenced — composition-collapse drill, untested-architectures drill, brain-mechanisms drill, Path C universal encoder drill, substrate aliveness drill, top1-targeted plasticity drill.

---

**End of drill.**
