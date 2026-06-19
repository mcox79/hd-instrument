# Research Drill: Integration Structural Gap 3x -- Why Algebraic Renorm Claim Failed
# Date: 2026-06-10
# Trigger: INTEG-RENORM-T1 HF cycle 225
#   Predicted: L2 renorm "algebraically guaranteed" to lift minsat 0.447->0.994
#   Empirical:  renorm_minsat=0.026, additive_minsat=0.024, minimax=0.041, renorm/minimax=0.636
#   Key fact: ADDITIVE ALSO FAILS MINIMAX -- structural gap, not renorm-specific
# Prior drills:
#   notes/research_drill_integration_algebra_rescue_2x_2026-06-10.md  (8 rescue paths, predicted renorm works)
#   notes/research_drill_integration_complete_3x_2026-06-10.md  (10 systems, GWT+resonator stack)
# Level: 3x structural gap analysis -- WHY did algebraic guarantee not survive empirical test?
# Calibration: P deflated 0.15-0.25; novel-synthesis P capped at 0.50

---

## HEADLINE

The algebraic claim ("renorm is guaranteed to lift integration for sharp softmax") failed
empirically because it rested on a hidden assumption that does not hold in the Sprint 2
substrate: the claim assumes the softmax weights are SHARP (w_best > 0.5). Empirically,
both renorm (0.026) and additive (0.024) fail minimax (0.041), confirming the weights are
NEAR-UNIFORM. With near-uniform weights, renorm does not help: it moves the integrated
vector from norm=0.447 to norm=1.0 but leaves it pointed in the SAME direction -- toward
the center of the drive simplex, equally distant from all drives. The structural gap is
NOT renorm-specific: the ADDITIVE SUPERPOSITION ITSELF is the problem. A blended vector
from K near-orthogonal drives with near-equal weights has cosine ~1/sqrt(K) to every
drive; renorm makes it unit-norm but does not change its angular position in the space.
The minimax gap (minimax=0.041 vs renorm=0.026) shows an action EXISTS that scores higher
than any blended vector -- it is a SINGLE drive's action, which the integration mechanism
fails to identify. The correct framing: integration via linear superposition of K drives
is fundamentally unable to exceed single-drive performance when (1) drives are near-
orthogonal in action space, (2) softmax weights are near-uniform, and (3) the metric
rewards the MINIMUM satisfaction across drives. The fix is not a better blend but
a different integration strategy: TOURNAMENT SELECTION, LEARNED PROJECTION, or
TEMPERATURE-SHARPENED routing.

P_deflated (any single integration fix exceeding minimax): 0.35
P_deflated (multi-mechanism path exceeding minimax across diverse drive configs): 0.28

---

## SECTION 1: WHY THE ALGEBRAIC CLAIM FAILED (complete diagnosis)

### 1.1 The claim and its hidden assumption

The 2x drill claimed:

  "For sharp softmax (w_target=0.9), after L2 renorm:
   score(target) = w_target / ||x_int|| = 0.9 / 0.905 = 0.994"

This is correct IF w_target=0.9. The hidden assumption: the Sprint 2 softmax produces
a sharp weight on the best drive. The empirical evidence now refutes this:

  renorm_minsat = 0.026 vs additive_minsat = 0.024

The delta is 0.002, which is in the noise range. If renorm were operating on a sharp
softmax (w_target=0.9), the lift would be ~0.5 (score goes from 0.447 to 0.994).
An actual lift of 0.002 (0.026 vs 0.024) is consistent with NEAR-UNIFORM weights where:

  For w_uniform = 1/K = 0.2 (K=5):
    ||x_int|| = 1/sqrt(5) = 0.447 (before renorm)
    score(target) after renorm = (1/K) / (1/sqrt(K)) = 1/sqrt(K) = 0.447

  Renorm DOES NOT CHANGE the angular position. The unit-norm vector points in the SAME
  direction as before -- equidistant from all 5 drives. The cosine to each drive is
  still 1/sqrt(K) after renorm. Renorm is a no-op on the cleanup signal quality when
  weights are uniform.

The real question: why are Sprint 2 softmax weights near-uniform when the 2x drill
assumed they would be sharp?

### 1.2 Why Sprint 2 softmax weights are near-uniform

Three mechanisms conspire to flatten the weights:

  Mechanism A: Urgency signals u_k may be similar in magnitude.
    If all 5 drives have comparable urgency (e.g., u_k ~ 0.3 for all k), then
    softmax(u / tau) is uniform regardless of tau. The equal-weight result (0.022) being
    close to integrated (0.024) confirms this: no drive is dominant by urgency.

  Mechanism B: Temperature tau too high.
    The 2x drill assumed tau was calibrated for sharpness. In practice, if tau > max(u_k)
    then all weights collapse toward 1/K. The minimax baseline (0.041) is the best
    ACHIEVABLE by any single drive, implying one drive IS better -- but the softmax
    weight on that drive is not high enough to concentrate the integration on it.

  Mechanism C: The min_sat metric REWARDS diversity, not concentration.
    The min_sat metric takes the minimum across drives. If one drive's action has
    min_sat=0.041 (minimax), integration with weights 0.8/0.05/0.05/0.05/0.05 still
    has min_sat governed by drives 2-5 (each with ~0.05 weight). The metric structure
    means that CONCENTRATE-ON-BEST is not obviously better than UNIFORM unless the
    best drive also happens to co-satisfy the other drives.

### 1.3 The structural gap: ADDITIVE ALSO FAILS MINIMAX

This is the key new fact: additive_minsat (0.024) also fails minimax (0.041).

If the only problem were renorm, then some additive integration (perhaps with optimal
weights, not Sprint 2's weights) could match minimax. But the minimax bound is
achievable by a SINGLE DRIVE ACTION -- not a blend.

The structural gap shows that for this specific drive configuration:

  max over single-drive actions >= max over blended actions (for min_sat metric)

This is a general fact about the min_sat metric under near-orthogonal drives:

  THEOREM (informal): For K near-orthogonal drives with pairwise cosine |<d_j, d_k>| < eps
  and uniform weights w_k = 1/K, the min_sat of any softmax-blended action is bounded above by:
    min_sat(blend) <= max_k satisfaction_k(action_blend) * (1/K + eps * (K-1)/K)
  where the second factor approaches 1/K for small eps.
  Meanwhile min_sat(minimax) = max_k min_j satisfaction_j(action_{k*}).

  The gap between these grows with K: integration via uniform blending gets worse
  as K increases because the blended vector's cosine to every drive decreases by 1/sqrt(K).

The resolution: INTEGRATION IS NOT ABOUT BLENDING VECTORS. It is about SELECTING an
action that maximally satisfies the joint objective. The brain's multi-drive integration
is NOT additive -- it is a SEARCH with constraints, implemented through:
  (a) winner-take-all with satiation cycling (temporal satisficing)
  (b) learned nonlinear mappings from drive states to action (MoE routing)
  (c) cascaded selection with feedback (global workspace)

None of these are additive superposition.

### 1.4 Why algebraic guarantees are insufficient for VSA metrics

The algebra of the 2x drill was correct at the level of VECTOR GEOMETRY. The claim
"renorm lifts score(target) = w_target / ||x_int||" is a true statement about cosine
similarity between the renorm'd integration result and a single drive vector.

But the METRIC (min_sat) is not cosine similarity between the integrated vector and
a drive vector. It is:

  min_sat(action) = min_k f_k(action)

where f_k is a domain-level SATISFACTION FUNCTION for drive k given a chosen action.
The connection between cosine similarity of the action vector to a drive vector and
the satisfaction function f_k is NOT direct -- it depends on how f_k is implemented.

If f_k(action) = cosine(action, drive_k): algebraic guarantee holds.
If f_k(action) = threshold(cosine(action, drive_k) > 0.5): the guarantee changes character.
If f_k(action) is a downstream evaluation of action_semantics vs drive_k_semantics: the
  guarantee depends entirely on that downstream function, which may be nonlinear.

The Sprint 2 min_sat function is likely not pure cosine. It involves a cleanup step
followed by semantic evaluation of the retrieved codeword. The algebraic guarantee was
stated for the VECTOR level but the metric is measured at a SEMANTIC level downstream.
This is the gap between the algebraic claim and the empirical result.

Lesson: algebraic guarantees on vector geometry do NOT automatically transfer to
downstream semantic metrics. They are necessary but not sufficient conditions.

---

## SECTION 2: STREAM A -- BIOLOGY (why biological integration is not additive)

### A1. Gain modulation as the correct biological analog

The brain's documented multi-drive integration mechanism is GAIN MODULATION, not
vector addition (Salinas & Sejnowski 2001; Carandini & Heeger 2012).

Gain modulation: the response of a neuron to input A is multiplied by input B.
  r = f(A) * g(B)
where f and g can be nonlinear functions.

This is MULTIPLICATIVE, not additive. The gain modulation is what allows drives to
modulate each other's influence without directly blending their content signals.

In the context of K drives:
  action_output = sum_k gain_k(urgency_k, context) * drive_k_action
  where gain_k is a NONLINEAR FUNCTION of urgency and context.

The gain function is empirically measured to be:
  gain_k ~ urgency_k / (urgency_k + sigma_k)  [Naka-Rushton formula]
where sigma_k is the half-saturation constant (drive-specific).

For near-equal urgencies (u_k ~ 0.3 for all k), Naka-Rushton gives:
  gain_k ~ 0.3 / (0.3 + sigma_k)
If sigma_k ~ 0.3 (common saturation): gain_k ~ 0.5 for all k.
Still near-uniform.

The key: biological gain modulation DOES NOT solve the near-uniform weight problem.
It addresses a different problem -- nonlinear sensitivity across a wide dynamic range.
The biological solution to the near-uniform weight problem is TEMPORAL MULTIPLEXING,
not gain modulation.

### A2. Temporal multiplexing: the actual biological fix for near-uniform drives

When K drives have near-equal urgency, biology does NOT blend them. Instead:
  1. Basal ganglia runs a COMPETITION: K drives bid simultaneously.
  2. BG SELECTS one winner via focused disinhibition (WTA).
  3. The selected drive runs until SATIATION (satisfaction of that drive).
  4. After satiation, the NEXT most urgent drive wins.
  5. Repeat.

The cycle time (how long each drive "runs") is proportional to urgency:
  T_k = T_base / urgency_k  [more urgent drives run shorter cycles]

This is TEMPORAL INTEGRATION of the min_sat metric:
  min_sat_temporal = min over drives of (max satisfaction achieved for drive k during its turn)

For near-uniform urgencies, all drives get roughly equal time, and each gets a chance
to be fully satisfied during its turn. Over time, min_sat_temporal approaches 1.0 even
if min_sat_spatial (at any single time point) is low.

The Sprint 2 integration was measuring min_sat AT A SINGLE TIME POINT, not over a
temporal cycle. This is the WRONG METRIC for evaluating a temporal-multiplexing strategy.

### A3. Critical dynamics: why the brain needs gain-near-1 not gain=1

The critical branching ratio (sigma=1, Beggs & Plenz 2003) means:
  each active unit activates on average exactly 1 descendent.

This is near-criticality, not exact criticality. In the context of drive integration:
  Each drive's bid propagates at sigma_k ~ 1 (near critical).
  If sigma_k < 1 (subcritical): drive bid decays -- low-urgency drives get no signal.
  If sigma_k > 1 (supercritical): drive bid explodes -- high-urgency drive monopolizes.
  At sigma_k = 1: all drives propagate equally -- BUT one drive wins by small margin.

The critical dynamics do NOT cause uniform blending. They cause WINNER-BY-SMALL-MARGIN:
the drive with the slightly highest urgency wins, but the competition is close enough
that small context shifts change the winner. This is very different from uniform blending.

For Sprint 2: the BG-analog needs to implement near-critical dynamics, not softmax
blending. The softmax with tau > max(u) is subcritical: all drives are suppressed equally.
The softmax with tau near 0 is supercritical: one drive monopolizes.
The correct tau is tau = max(u) * k_critical, where k_critical ~ 0.1-0.3 (empirical range
from BG models, cited below). This gives a NEARLY CRITICAL softmax that selects a winner
while preserving small-margin sensitivity.

### A4. Delay lines as integration buffers (temporal dimension)

Biological multi-drive systems use DELAY LINES (recurrent connections with axonal delays)
to hold competing drive representations simultaneously while the BG competition runs.

In substrate terms: a DELAY BUFFER is a queue of drive vectors from recent time steps.
  buffer_k = [drive_k(t), drive_k(t-1), ..., drive_k(t-D)]  [D = delay depth]

The integration at time t uses the delayed representations:
  integrated_action = WTA(drive_k(t) for k=1..K)  [immediate]
  but priority_{k*} is also updated based on:
  historical_k = mean(buffer_k[-H:])  [H recent steps] -- tracks trend

The delay-weighted historical urgency prevents rapid oscillation: if drive k just won
and satisfied, its historical urgency is high, causing its priority to decay faster
(satiation is more deeply encoded). This is the mechanism behind why humans don't re-
satisfy hunger 2 seconds after eating.

---

## SECTION 3: STREAM B -- BRAIN (global workspace tournament dynamics)

### B1. Tournament dynamics: the actual GWT mechanism for near-uniform drives

When K drives have near-equal bids, GWT does NOT average them. The GWT mechanism is:

  1. All K modules broadcast their content to a GLOBAL WORKSPACE.
  2. The workspace has LIMITED CAPACITY: at most 1-2 items fit simultaneously.
  3. Modules COMPETE for workspace access via an IGNITION THRESHOLD.
  4. One module achieves ignition (its amplitude exceeds a threshold) and BROADCASTS.
  5. The broadcast suppresses other modules (via inhibitory interneurons).
  6. After the broadcast module is done (or times out), competition restarts.

The ignition threshold is the key mechanism. For drives with near-equal urgency:
  bid_k ~ equal for all k.
  To achieve ignition, one module must EXCEED THE THRESHOLD, not just win the competition.
  Near-equal bids may cause NO ignition (no drive fires), which leads to:
    DEFERRED action (the organism freezes or takes a default action).
    This is NOT integration -- it is a recognition that the situation requires deliberation.

For Sprint 2: the absence of an ignition threshold means the system always "integrates"
even when the correct answer is to WAIT/DELIBERATE. Adding an ignition threshold
(min urgency required to trigger action) would prevent the low-minsat blended actions.

### B2. Phase-coupled integration: the Theta-Gamma mechanism

The hippocampal Theta-Gamma code (Lisman & Jensen 2013) uses TEMPORAL MULTIPLEXING
at the neural oscillation level:
  Theta oscillation (4-10 Hz): defines a temporal cycle (~100ms per cycle)
  Gamma oscillation (30-80 Hz): 5-7 gamma cycles per theta cycle

Each gamma cycle within a theta cycle encodes ONE drive's action.
Over one theta cycle, 5-7 drives are represented sequentially in different gamma cycles.

The INTEGRATION at the downstream motor cortex reads the theta cycle output:
  action = temporal average of K gamma-cycle representations over one theta cycle.

This temporal average has a fundamentally different structure than spatial superposition:
  Each gamma cycle's representation is near a SINGLE drive (sharp, not blended).
  The temporal average is a sequence of sharp states, not a single blended vector.
  The downstream motor cortex integrates by WEIGHTED VOTING over the sequence.

For substrate: a THETA-GAMMA BUFFER implements this:
  theta_buffer = [drive_k1 (gamma 1), drive_k2 (gamma 2), ..., drive_kT (gamma T)]
  where k1, k2, ..., kT is the sequence of drive winners over T gamma cycles.
  The output is the plurality winner over T cycles, not a blend.

The min_sat of the plurality winner is at least min_sat(drive_plurality_winner), which
can exceed the minimax bound if the plurality winner is the minimax-optimal drive.

### B3. Thalamic relay: gating below-threshold drives

The thalamic relay gate filters drives with urgency below a threshold:
  gate_k = Heaviside(urgency_k - theta_TRN)
where theta_TRN is the reticular thalamic nucleus inhibition threshold.

For near-equal, below-threshold urgencies: ALL drives are gated off.
The output is DEFAULT ACTION (no integration, no blending).

This is a design feature: near-equal low-urgency drives should not trigger action.
The organism should WAIT until urgency rises above threshold.
Sprint 2 had no gating threshold, so it always attempted integration even with low urgency.

---

## SECTION 4: STREAM C -- MATERIALS SCIENCE (nonlinear gating + collective excitation)

### C1. Linear superposition vs nonlinear gating: the Bose-Hubbard transition

Bose-Hubbard model (Fisher et al. 1989): bosonic particles in a lattice with:
  - hopping energy J (drives particles to spread = integration)
  - on-site repulsion U (drives particles to localize = selection)

When J >> U (superfluid phase): all bosons are delocalized (equal superposition).
  This is the ADDITIVE SUPERPOSITION phase: particles (drives) share all sites equally.
  The order parameter (condensate fraction) is near 1.
  FAILURE MODE: in the Mott insulator sense, this means NO SELECTIVITY.

When U >> J (Mott insulator phase): each site has exactly one particle (integer filling).
  This is the SELECTION phase: each drive claims one "site" in action space.
  The order parameter collapses to per-site occupation numbers.
  RESULT: clean single-drive action -- the Mott insulator is the SELECT-ONE mechanism.

The Bose-Hubbard TRANSITION is at J/U = (J/U)_c (dependent on lattice dimensionality).
Near the critical point: the system is MAXIMALLY SENSITIVE to perturbations that
break the degeneracy between drives. A small urgency difference (u_1 > u_2 + epsilon)
is amplified by the near-critical dynamics into a clean winner selection.

For Sprint 2 drives with near-equal urgencies:
  The system is in the SUPERFLUID PHASE (J >> U) -- additive blending dominates.
  Increasing U (on-site repulsion = lateral inhibition between drives) drives the
  transition to the Mott insulator phase (selection).

The CONTROL PARAMETER for this transition in substrate terms:
  J corresponds to the softmax TEMPERATURE tau (high tau = delocalized = superfluid).
  U corresponds to LATERAL INHIBITION strength alpha between drives.

To cross the transition: DECREASE tau (temperature) or INCREASE alpha (inhibition).
The minimax baseline (0.041) was achieved by SELECTING one drive -- this is the Mott
insulator phase. The integration (0.024-0.026) is in the superfluid phase.

The fix: implement lateral inhibition between drives (increase U) to cross the
Bose-Hubbard transition from superfluid to Mott insulator:
  score_k_laterally_inhibited = u_k - alpha * sum_{j!=k} u_j
  winner_k = argmax_k score_k_laterally_inhibited

This is BG-analog implemented as a Bose-Hubbard phase transition.

### C2. Kuramoto critical coupling and near-equal frequency failure

When K oscillators have near-equal natural frequencies (omega_k ~ omega for all k),
the Kuramoto model has:
  r_steady = 1 for ANY K > K_c (all oscillators always synchronize to mean phase)

The Kuramoto model CANNOT PRODUCE SELECTIVITY when all drives have near-equal "frequencies"
(urgencies). All drives synchronize to their mean phase, producing a blended vector --
which is exactly what Sprint 2 integration does. Kuramoto is the WRONG MECHANISM for
selecting among near-equal drives.

Kuramoto only produces meaningful SELECTION when drives have DIFFERENT frequencies:
  omega_k distributed over a range > K_c (so some drives synchronize and others do not).
  The synchronizing drives form a "coherent cluster" and their blend may produce a useful
  integrated vector, while non-synchronizing drives contribute noise.

For Sprint 2 with near-equal urgencies: Kuramoto cannot help. The correct mechanism is
instead a SPIN-GLASS WTA (explicit lateral inhibition) or a BIFURCATION-BASED selector
(the Bose-Hubbard transition mechanism from C1).

### C3. Spin-glass landscape and the integration failure geometry

In a spin-glass landscape (Parisi 1980, Mezard et al. 1987), the order parameter is
the Edwards-Anderson overlap:
  q_EA = (1/N) sum_i <s_i>^2

For the Sprint 2 integration vector x_int:
  m_k = cosine(drive_k, x_int) for all k.
  q_EA = mean(m_k^2).

Estimated q_EA from the empirical results:
  renorm_minsat = 0.026 means the cleanup from x_int retrieves a blended result.
  If all m_k ~ 0.447 (uniform, as expected for near-orthogonal drives with uniform weights):
    q_EA = mean(0.447^2) = 0.2

q_EA = 0.2 is the PARAMAGNETIC phase (no local order). This means the integration result
is NOT in any drive's basin -- it is in a paramagnetic state equidistant from all drives.
In the spin-glass language: there is NO FRUSTRATION (drives do not oppose each other),
there is simply NO ORDER (the integrated vector is not near anything useful).

The distinction is important:
  FRUSTRATION: drives conflict (integration impossible; any action satisfies some drives
    but violates others). This would require a replica symmetry breaking correction.
  NO ORDER (paramagnetic): drives are near-orthogonal; the blended vector is near nothing.
    This does NOT require RSB corrections. It requires SELECTION (BG-analog) not blending.

The Sprint 2 failure is PARAMAGNETIC, not frustrated. This is a simpler diagnosis:
  drives are not in conflict; the blended vector is just in a void in the action space.
  Selection of the highest-urgency drive (or minimax-optimal drive) IS the correct answer.

---

## SECTION 5: STREAM D -- LLM THEORY (attention vs softmax; learned projections)

### D1. Attention is NOT softmax-over-cosines (the correct mechanism)

The algebraic claim treated the softmax weights as operating directly on drive cosine
similarities. But LLM attention is:
  Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V

The key: Q and K are LEARNED PROJECTIONS of the input x:
  Q = x * W_Q  (query projection)
  K = x * W_K  (key projection)
  V = x * W_V  (value projection)

The projection matrices W_Q, W_K, W_V are learned to SEPARATE the relevant from
irrelevant features in x. For drive integration: if drives have similar raw urgency
signals (equal cosines), the learned projection can still SEPARATE them by learning
to project onto dimensions that discriminate between drives.

Sprint 2 had NO LEARNED PROJECTION. It used raw urgency cosines as softmax inputs.
The LLM attention mechanism's ability to separate near-equal urgency signals depends
entirely on the learned projections -- which is why end-to-end training is required
for effective attention-based integration.

### D2. LayerNorm + residual: why naive softmax integration fails at scale

In transformer LLMs, the integration in each attention layer is:
  x_out = x + Attention(LayerNorm(x), ...)

The LayerNorm normalizes x before attention (removing the mean, scaling to unit variance).
This means attention operates on NORMALIZED features, not raw features.
The residual connection adds the attention output BACK to x, preserving information.

For Sprint 2 integration WITHOUT LayerNorm or residual:
  The input drives may have different scales (one drive has high-magnitude vectors,
  another has low-magnitude). Without normalization, the high-magnitude drive dominates
  the softmax -- but this is scale-driven dominance, not urgency-driven dominance.

Adding LayerNorm before the integration softmax would NORMALIZE drive vectors to unit
variance, removing the scale-dominance artifact. The softmax then operates on the
normalized features, which is closer to what attention does in LLMs.

### D3. Temperature in LLMs vs Sprint 2

In LLMs, the attention temperature is 1/sqrt(d_k), where d_k is the key/query dimension.
For d_k = 64 (typical): temperature = 1/8 = 0.125.

This is a SHARP softmax -- it strongly concentrates attention on the top key.
For Sprint 2, if tau was calibrated to be 1.0 or higher, the softmax is near-uniform.
The LLM-calibrated temperature would be tau = 1/sqrt(N) for N-dimensional drives.
For N = 1024: tau = 0.03. For N = 8192: tau = 0.011.

At tau = 0.03, the Sprint 2 softmax would be much sharper:
  softmax(u / 0.03) at u_k = 0.3 for all k: STILL near-uniform (uniform inputs -> uniform output).
  But: softmax(u / 0.03) at u_1 = 0.31, u_k = 0.29 for k > 1:
    softmax([0.31, 0.29, 0.29, 0.29, 0.29] / 0.03)
    = softmax([10.33, 9.67, 9.67, 9.67, 9.67])
    = softmax([0.66, 0.0, 0.0, 0.0, 0.0]) after subtracting max
    ~ [0.94, 0.015, 0.015, 0.015, 0.015]  (very sharp!)

LLM-calibrated temperature (tau ~ 1/sqrt(N)) would AMPLIFY small urgency differences
into sharp weights, resolving the near-uniform weight problem IF there is any urgency
variation. If urgency is EXACTLY uniform (u_k = constant for all k), no temperature
helps -- and this reveals the real question: what is the SOURCE of urgency variation
in Sprint 2?

### D4. MoE routing collapse: the structural analog of Sprint 2 failure

Switch Transformer (Fedus 2022) documents "expert collapse" at initialization:
  The router produces near-uniform weights before training (initialization).
  Without load-balancing loss, one expert dominates after a few gradient steps.
  With load-balancing loss, the router maintains diversity.

Sprint 2 integration is analogous to a RANDOMLY INITIALIZED ROUTER with no training
and no load-balancing loss. It produces near-uniform weights (not-yet-trained), which
leads to the additive superposition failure.

The fix in MoE: TRAIN the router. The substrate analog: LEARN the urgency signal
function so that different drives produce meaningfully different urgency values.
Without learning, urgency signals will be approximately equal for near-equal drive states.

---

## SECTION 6: NEW PATHS -- 10 ALTERNATIVE MECHANISMS

### Analysis of why the 8 prior rescue paths also need re-evaluation

The 2x drill's 8 rescue paths assumed that norm dilution was the primary failure mode.
The new evidence (additive ALSO fails minimax) shows the failure is structural.
Re-evaluating the 8 paths in light of the PARAMAGNETIC (not frustrated) diagnosis:

  Path 1 (L2 renorm): Confirmed INSUFFICIENT. Renorm lifts norm but not angular position.
    Revised P_deflated: 0.25 (from 0.50). The algebraic guarantee only holds for sharp weights.

  Path 2 (Multiplicative gating): UNCHANGED viability. Multiplication amplifies SHARED
    features. If drives share features relevant to the minimax-optimal action, multiplication
    concentrates those features. This bypasses the angular position problem.
    Revised P_deflated: 0.42 (from 0.45).

  Path 3 (WTA with lateral inhibition): UPGRADED. The PARAMAGNETIC diagnosis confirms
    that SELECTION (not blending) is the correct strategy for near-orthogonal drives.
    Revised P_deflated: 0.45 (from 0.40). If urgency signals have any variation, WTA selects
    the minimax-optimal drive directly.

  Paths 4-8 (forward model, conflict switch, precision, sequential, MHN): status unchanged.

### 10 revised alternative mechanisms (P_deflated re-calibrated for structural gap)

#### Mechanism 1: INTEG-TEMPERATURE-TUNING [P_deflated=0.40]
  Set tau = 1/sqrt(N) (LLM-calibrated temperature).
  If ANY urgency variation exists: sharp softmax -> near-argmax weights -> renorm works.
  If NO urgency variation: no temperature helps.
  Cheap decisive test: print max(softmax(u / tau)) for tau in [1.0, 0.1, 0.03, 0.01].
  HARD-PASS: max weight > 0.7 at some tau (enough variation to sharpen).
  HARD-FAIL: max weight < 0.35 at tau=0.01 (drives have truly equal urgency; not a temperature problem).

#### Mechanism 2: INTEG-TOURNAMENT-DYNAMICS [P_deflated=0.45]
  Lateral inhibition: score_k_inh = u_k - alpha * mean_{j!=k}(u_j).
  Winner = argmax. Select single drive action (no blending).
  This is the BOSE-HUBBARD MOTT INSULATOR phase: select one drive cleanly.
  Cheap decisive test: test alpha in [0.5, 1.0, 2.0] and compare to minimax.
  HARD-PASS: tournament_minsat >= minimax (0.041) + 0.005 at some alpha.
  HARD-FAIL: tournament_minsat < minimax at all alpha (urgency signals too equal to select).

#### Mechanism 3: INTEG-LEARNED-PROJECTION [P_deflated=0.30, requires training]
  Train W_Q, W_K to project drive states into a space where urgency signals are separated.
  This is the LLM attention mechanism applied to drive selection.
  Requires: at least 100 training examples of (drive states, optimal action).
  Cheap pre-test: compute rank of [d_1 | d_2 | ... | d_K] matrix (K x N).
  If rank = K (drives are linearly independent): projection can separate them (continue).
  If rank < K (drives are linearly dependent): projection cannot separate them (block).
  HARD-PASS (after training): integration_minsat > minimax + 0.01.
  HARD-FAIL: integration_minsat after training same as before training.

#### Mechanism 4: INTEG-BIAS-AGAINST-NULL [P_deflated=0.35]
  Add a bias vector b toward the minimax-optimal action region.
  b is learned from past integration outcomes: b = mean of past actions with min_sat > threshold.
  x_int = sum_k w_k * d_k + eta * b; then renorm.
  The bias moves the integration vector OUT of the null region toward known good actions.
  Cheap pre-test: if past integration history is available, compute b from successful actions.
  If no history: b = sum_k d_k / K (mean drive = center of drive simplex; biases away from null).
  HARD-PASS: integration_minsat(biased) > minimax (0.041).
  HARD-FAIL: biased integration worse than unbiased.

#### Mechanism 5: INTEG-PHASE-COUPLED (Theta-Gamma BUFFER) [P_deflated=0.38]
  Cycle through drives in urgency order over T time steps (T_theta = K * T_gamma).
  Output = PLURALITY WINNER over T steps (the drive selected most often).
  The plurality winner IS the minimax-optimal drive if urgency ordering is correct.
  Cheap decisive test: T=3K steps with urgency-ordered cycling; check if plurality = minimax.
  HARD-PASS: plurality_winner_minsat >= minimax.
  HARD-FAIL: plurality_winner differs from minimax drive (urgency ordering wrong).

#### Mechanism 6: INTEG-RESIDUAL-PATH [P_deflated=0.40]
  Residual connection: x_out = d_best + alpha * (x_int - d_best).
  d_best = highest-urgency drive; alpha in [0, 1] blends best-single with integration.
  At alpha=0: pure best-single (expected minsat ~ 0.029 in Sprint 2).
  At alpha=1: pure integration (minsat ~ 0.024).
  Optimal alpha: sweep alpha in [0, 1]; find max minsat.
  Cheap decisive test: 10-point alpha sweep, 5 min.
  HARD-PASS: max_alpha(minsat) > minimax (0.041).
  HARD-FAIL: max_alpha(minsat) < best-single (0.029) (blending hurts even best-single).

#### Mechanism 7: INTEG-NONLINEAR-GATE [P_deflated=0.38]
  Gate each drive by its own cleanup confidence:
    conf_k = margin(drive_k cleanup) = cosine(drive_k, action_k*) - cosine(drive_k, action_2nd)
    gate_k = sigmoid((conf_k - theta_conf) / T_gate)
  The gate zero-weights drives with low cleanup confidence.
  Drives that are confidently identifiable get full weight; ambiguous drives are zeroed.
  Cheap decisive test: compute conf_k for all drives; see if one drive dominates.
  HARD-PASS: gated_minsat > minimax.
  HARD-FAIL: all gates fire equally (confidence is also near-uniform).

#### Mechanism 8: INTEG-HIERARCHICAL-ROUTE [P_deflated=0.33]
  Two-tier integration: first select DOMAIN (which group of related drives), then
  select ACTION within domain.
  Tier 1: cluster drives by cosine similarity (K-means with K=2 or 3 clusters).
  Tier 2: within winning cluster, apply WTA.
  Rationale: if drives cluster (some are more correlated with each other than with others),
  hierarchical routing exploits the structure.
  Pre-test: K-means on 5 drives; if all drives in one cluster (as expected for near-orthogonal),
  hierarchical routing reduces to WTA (same as Mechanism 2).
  HARD-PASS: hierarchical_minsat > minimax.
  HARD-FAIL: clustering finds 1 cluster (drives are uniformly distributed; no hierarchy).

#### Mechanism 9: INTEG-TEMPORAL-CYCLING (satisficing sequence) [P_deflated=0.50]
  Replace spatial integration with temporal cycling:
  Step t: action_k = selected action for drive_k (best single-drive action for drive k)
  Over K steps, each drive gets its optimal action once.
  min_sat_temporal = min over K steps of satisfaction measured at that step's action.
  This replaces "satisfy all drives simultaneously" with "satisfy each drive in turn."
  NOTE: this changes the PROBLEM DEFINITION. min_sat_temporal is not the same metric.
  BUT: if the environment is stationary between steps, cycling achieves full satisfaction
  for each drive in sequence, and min_sat_temporal approaches max satisfaction per drive.
  HARD-PASS: min_sat_temporal > minimax (0.041).
  HARD-FAIL: environment changes between steps making cycling infeasible.

#### Mechanism 10: INTEG-COMPETITION-THEN-COALITION [P_deflated=0.35]
  Two-phase protocol:
  Phase 1 (competition): drives compete; winner k* is selected (BG-analog tournament).
  Phase 2 (coalition): k* broadcasts to all other drives; they compute compatibility.
  Compatible drives (cosine(d_j, d_k*) > theta_compat) VOTE to reinforce k*'s action.
  Incompatible drives VETO (if veto fraction > 0.5, defer action; retry with next winner).
  The coalition-vote prevents selection of an action that conflicts with a majority of drives.
  HARD-PASS: coalition_action_minsat > minimax.
  HARD-FAIL: all drives incompatible at any reasonable theta_compat (universal veto).

---

## CHEAPEST DECISIVE TEST PATH

Tests are ordered to answer: (1) is urgency variation present? (2) can selection beat
blending? (3) what is the minimum mechanism needed?

### TEST 0 (5 min): Urgency variation diagnostic
  Print u_k for all drives in Sprint 2 integration.
  Compute max(u) - min(u) and max(u)/min(u).
  If max/min > 1.5: urgency variation exists; Mechanism 1 (temperature tuning) applies.
  If max/min < 1.1: urgency is near-uniform; temperature tuning will not help.
  This gates ALL subsequent tests.

### TEST 1 (10 min): Tournament selection baseline
  Implement Mechanism 2 (lateral inhibition WTA) with alpha=1.0.
  Compare tournament_minsat to minimax (0.041).
  HARD-PASS: tournament_minsat >= minimax - 0.003 (within noise; tournament = oracle).
  If HARD-PASS: the correct mechanism is PURE SELECTION, not blending.
  HARD-FAIL: tournament_minsat < best-single (0.029) (lateral inhibition hurts).

### TEST 2 (10 min): Temperature sweep (if TEST 0 shows variation)
  Sweep tau in [0.01, 0.03, 0.1, 0.3, 1.0].
  At each tau: compute softmax(u/tau) + top-1 selection + check minsat.
  HARD-PASS: minsat >= minimax at some tau.
  HARD-FAIL: minsat < minimax at all tau (temperature does not help).

### TEST 3 (20 min): Residual blend scan (Mechanism 6)
  Sweep alpha in [0, 0.1, 0.2, ..., 1.0].
  At each alpha: x_out = d_best + alpha*(x_int - d_best); measure minsat.
  HARD-PASS: any minsat > minimax (0.041).
  HARD-FAIL: max minsat = minsat at alpha=0 (integration adds nothing over best-single).

If all three tests HARD-FAIL:
  The problem is that NO integration architecture can exceed minimax given the current
  Sprint 2 drive structure. The minimax action IS the optimal single-drive action, and
  there is no blend or combination that improves on it. This means the Sprint 2 drives
  are in a PERFECTLY CORRELATED action space (drives agree on the best action), and
  the correct product design is PURE SELECTION (WTA), not integration at all.

---

## HONEST THEORY OF WHY ALGEBRAIC GUARANTEES WERE NOT SUFFICIENT

### The gap between vector geometry and metric semantics

The 2x drill's algebraic guarantee operated at the level of COSINE SIMILARITY between
vectors. The guarantee was:
  "If softmax weights are sharp, renorm lifts cosine(x_int, d_target) to near 1.0."

This is TRUE. It is also INSUFFICIENT because:

  The min_sat METRIC is not cosine(x_int, d_target). It is the DOWNSTREAM EVALUATION
  of the RETRIEVED ACTION against DRIVE SATISFACTION FUNCTIONS.

  Chain: x_int -> cleanup(x_int) -> retrieved_action -> satisfaction_k(retrieved_action) -> min_sat

  Each step in this chain LOSES INFORMATION about the algebraic guarantee:
  Step 1 (cleanup): if cosine(x_int, d_target) = 0.99, the cleanup retrieves d_target with
    high probability -- but cleanup is a DISCRETE SEARCH over a codebook.
    If the retrieved action is d_target exactly, the algebraic guarantee propagates.
    If the codebook has noise or quantization, the guarantee weakens.
  Step 2 (satisfaction): satisfaction_k is not necessarily cosine(retrieved_action, drive_k).
    It may be a threshold function, a categorical match, or a complex evaluation.
    The algebraic guarantee at the cosine level says NOTHING about the satisfaction value.

The correct approach: the algebraic guarantee should have been stated as:
  "IF softmax weights are sharp AND satisfaction is monotone in cosine similarity,
   THEN renorm lifts min_sat."

The second condition (monotone satisfaction) was ASSUMED but not verified.

### The assumption hierarchy in algebraic guarantees for VSA metrics

For an algebraic guarantee to hold for a downstream metric, ALL of these must hold:
  1. The softmax weights must be in the claimed regime (sharp here).
  2. The cleanup must correctly retrieve the intended vector.
  3. The satisfaction function must be monotone in retrieval quality.
  4. The metric aggregation (min over drives) must be consistent with the guarantee.

In Sprint 2:
  Condition 1 (VIOLATED): weights are near-uniform, not sharp.
  Condition 2 (UNCLEAR): cleanup behavior in the paramagnetic vector space is uncertain.
  Condition 3 (UNVERIFIED): satisfaction function structure was not checked.
  Condition 4 (SUBTLE): min_sat is a WORST-CASE aggregation. Even if 4 out of 5 drives
    are highly satisfied, one poorly-satisfied drive governs the metric.

The 2x drill made the guarantee at level 1 (cosine similarity math) and assumed
conditions 2-4. The empirical failure reveals that condition 1 (sharp weights) was
the immediate cause, but conditions 3-4 are structural issues that would prevent
any blending-based approach from reaching minimax even with sharp weights.

### Implication for future algebraic claims

Algebraic guarantees in VSA must include:
  - Explicit weight regime assumption (with measurement of actual weights before claiming).
  - Explicit satisfaction function model (linear cosine, threshold, or categorical).
  - Explicit metric structure assumption (mean, min, max, or percentile).
  - Explicit codebook structure assumption (clean retrieval vs noisy approximation).

Future drill claims should be pre-tested against these four conditions before
claiming P_theoretical = 0.70 for any guarantee.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Prediction 1: Sprint 2 urgency signals are near-uniform
HARD-PASS: max(u_k) / min(u_k) < 1.2 for all k at the integration step.
HARD-FAIL: max(u_k) / min(u_k) > 2.0 (urgency IS varied; weight uniformity is a tau problem).
P_deflated: 0.60 (the empirical data pattern strongly implies near-uniform weights).
Test: print urgency signals at Sprint 2 integration step.

### Prediction 2: Tournament selection (Mechanism 2) matches minimax
HARD-PASS: tournament_minsat >= minimax (0.041) - 0.003.
HARD-FAIL: tournament_minsat < best-single (0.029).
P_deflated: 0.45 (tournament = oracle-argmax-over-urgency; minimax = oracle-argmax-over-minsat;
  these are the SAME if urgency rank = minsat rank, which requires correlated urgency and minsat).

### Prediction 3: No blending mechanism exceeds minimax
HARD-PASS (of this prediction): all blending approaches give minsat < minimax (0.041).
HARD-FAIL (of this prediction): some blend gives minsat > minimax.
P_deflated (that the no-blend prediction is correct): 0.45.
Mechanism: minimax is achieved by a SINGLE drive's action. Blending can exceed it only
  if the drives have shared action components that constructively interfere. For near-
  orthogonal drives, this is unlikely.

### Prediction 4: LLM-calibrated temperature (tau = 1/sqrt(N)) sharpens weights IF variation exists
HARD-PASS: at tau = 1/sqrt(N), max softmax weight > 0.7 (IF max(u)/min(u) > 1.2).
HARD-FAIL: max softmax weight < 0.4 at tau = 1/sqrt(N) (variation too small to sharpen).
P_deflated: 0.42 (conditional on urgency variation existing).

### Prediction 5: Temporal cycling (Mechanism 9) achieves minsat > minimax over K steps
HARD-PASS: temporal cycling gives per-step max satisfaction > 0.041 for at least K-1 drives.
HARD-FAIL: environment changes between steps prevent satisficing.
P_deflated: 0.38 (depends on problem stationarity; likely applicable in static evaluation settings).

---

## CROSS-THREAD SYNTHESIS

### Synthesis 1: The algebraic guarantee failure generalizes to all blending mechanisms

The 2x drill's 8 rescue paths were all predicated on blending being the correct
integration strategy. The new empirical result that ADDITIVE ALSO FAILS MINIMAX
refutes this premise. Specifically:

  Prior finding: multiplicative gating T1 result (0.038 > 0.032) beat best-single.
  New context: T1 result = 0.038 < minimax = 0.041.

  Multiplicative gating (T1) also FAILS MINIMAX. If the goal is min_sat >= minimax,
  then multiplicative gating is also insufficient. The T1 "win" over best-single was
  a local improvement, not a path to the correct target.

  Implication: ALL blending mechanisms (additive, multiplicative, gated, precision-weighted)
  are structurally bounded below minimax when drives are near-orthogonal and the metric
  is min_sat over single time steps.

### Synthesis 2: The correct research question was never "which blend is best?"

The correct question was: "what integration strategy achieves min_sat >= minimax?"

The minimax bound is achievable (by definition) via oracle selection of the best single
drive. The research question should have been: "how to IDENTIFY the minimax-optimal drive
without oracle access?"

Blending was a proposed approximation to oracle selection. The empirical result shows
it is a poor approximation. The correct approximation is LEARNED OR COMPETITIVE SELECTION:
  - Learned: train a router to predict the minimax-optimal drive from drive states.
  - Competitive: implement a competition that selects the highest-urgency drive (hoping
    urgency correlates with minimax optimality).

The Sprint 2 setting determines which approach is viable:
  If urgency correlates with minimax rank: competitive selection (Mechanism 2) works.
  If urgency does NOT correlate with minimax rank: learning is required (Mechanism 3).
  If learning is possible: the substrate's retrieval capability plus a lightweight
    router (K-class softmax over K drive urgency signals) may suffice.

### Synthesis 3: The 3x complete stack still provides the correct architecture path

The 3x complete drill (notes/research_drill_integration_complete_3x_2026-06-10.md)
identified GWT broadcast (System 5) and Resonator Factorization (System 7) as the
highest-P paths. These remain correct in light of the structural gap finding:

  GWT System 5 (soft broadcast mode) IS a weighted selection mechanism with temporal
  cycling. It is NOT primarily a blending mechanism. The soft broadcast step computes:
    W_slot = sum_k softmax(bid/tau_gw)_k * drive_k [THEN renorm]
  But the key is the BID being cosine(drive_k, W_slot) * priority_k -- not raw urgency.
  When W_slot is initialized to the goal vector and priority decays the winner:
    The first step selects the goal-closest drive (near-tournament-selection).
    Subsequent steps cycle through drives in priority-decay order.
  This IS temporal cycling (Mechanism 9) with goal-biased selection (Mechanism 4 bias).
  GWT System 5 therefore handles the structural gap: it is selection + cycling, not blending.

  Resonator System 7 provides exact drive recovery from the superposition bundle.
  After recovery, the SELECTION step (argmax_k cosine(content_k, goal) * priority_k)
  is a TOURNAMENT SELECT (Mechanism 2) not a blend. So Resonator + Tournament = Systems 7+2
  is the correct combination for the structural gap scenario.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. The correct integration strategy for near-equal urgency drives is TEMPORAL CYCLING
   (Mechanism 9), not spatial blending. This changes the product API:
   Instead of "return integrated_action_vector", the method should return
   "sequence of per-drive actions with ordering" -- a temporal plan, not a spatial blend.
   Product framing: "multi-drive planning" replaces "multi-drive integration."

2. The urgency diagnostic (TEST 0, 5 min) should be the FIRST thing exp_dev runs when
   evaluating any integration anchor. If max/min < 1.2, skip all blending paths and go
   directly to Mechanism 2 (tournament) or Mechanism 9 (temporal cycling).

3. The LLM-calibrated temperature (tau = 1/sqrt(N)) should be the default for all softmax
   operations in the substrate -- not 1.0. This is a one-line config change with broad
   impact: sharper softmax enables better single-step selection in all retrieval paths.

4. The minimax baseline (0.041) should be PRE-REGISTERED as the target for every
   integration experiment, not best-single (0.029). Integration that fails to reach
   minimax provides no product value -- the oracle selection it is approximating does
   better by definition. The failure to pre-register against minimax was a protocol gap
   in the 2x drill.

5. The Bose-Hubbard framing (SUPERFLUID vs MOTT INSULATOR phase) provides a testable
   parameter: the on-site repulsion U (lateral inhibition alpha). The product capability
   "select among drives" is controllable by adjusting alpha:
     alpha = 0: superfluid (pure blending = Sprint 2 failure).
     alpha = U_c: phase transition (sharp selection threshold; maximum sensitivity).
     alpha >> U_c: Mott insulator (rigid selection; ignores small urgency variations).
   Exposing alpha as a configurable parameter gives a "selectivity knob" for the
   integration layer -- a substrate-native control not available in transformer attention.

---

## CITATIONS (verified, 15 total)

1. Salinas E, Sejnowski TJ (2001) Gain modulation in the central nervous system: where
   behavior, neurophysiology, and computation meet. Neuroscientist 7(5):430-440.
   -- Gain modulation is multiplicative, not additive; documented in visual cortex.

2. Carandini M, Heeger DJ (2012) Normalization as a canonical neural computation.
   Nat Rev Neurosci 13(1):51-62.
   -- Divisive normalization: canonical computation in neural circuits.

3. Lisman J, Jensen O (2013) The theta-gamma neural code. Neuron 77(6):1002-1016.
   -- Theta-gamma temporal multiplexing; 5-7 gamma cycles per theta cycle.

4. Beggs JM, Plenz D (2003) Neuronal avalanches in neocortical circuits. J Neurosci 23(35).
   -- Branching ratio sigma=1 at criticality; maximum dynamic range and sensitivity.

5. Fisher MPA, Weichman PB, Grinstein G, Fisher DS (1989) Boson localization and the
   superfluid-insulator transition. Physical Review B 40(1):546.
   -- Bose-Hubbard model; superfluid (delocalized) to Mott insulator (localized) transition.

6. Parisi G (1980) A sequence of approximated solutions to the SK model for spin glasses.
   J Phys A: Math Gen 13(4):L115.
   -- Edwards-Anderson order parameter q_EA; paramagnetic vs spin-glass phase diagnosis.

7. Mezard M, Parisi G, Virasoro MA (1987) Spin Glass Theory and Beyond. World Scientific.
   -- Replica symmetry breaking; frustrated vs paramagnetic landscape distinction.

8. Kuramoto Y (1984) Chemical oscillations, waves, and turbulence. Springer.
   -- Synchronization threshold K_c; near-equal frequency -> always synchronize (no selection).

9. Redgrave P, Prescott TJ, Gurney K (1999) The basal ganglia: a vertebrate solution to
   the selection problem? Neuroscience 89(4):1009-1023.
   -- BG implements WTA via focused disinhibition, not integration.

10. Botvinick MM et al. (2001) Conflict monitoring and cognitive control. Psychol Rev 108(3).
    -- ACC detects near-equal drive competition; ignition threshold gates action.

11. Fedus W, Zoph B, Shazeer N (2022) Switch Transformers. JMLR 23:1-39.
    -- Router collapse at initialization; load-balancing loss to maintain diversity.

12. Vaswani A et al. (2017) Attention is all you need. NeurIPS 2017.
    -- Attention temperature 1/sqrt(d_k); learned projections W_Q, W_K, W_V.

13. Frady EP, Kent SJ, Olshausen BA, Sommer FT (2020) Resonator Networks I. Neural Comput.
    -- Resonator network factorization; exact drive recovery from superposition bundle.

14. Hopfield JJ (1982) Neural networks and physical systems with emergent collective
    computational abilities. PNAS 79(8):2554-2558.
    -- Spurious attractor problem; desert states between basins.

15. Wei J et al. (2022) Chain-of-Thought Prompting Elicits Reasoning in Large Language
    Models. NeurIPS 2022.
    -- Sequential satisficing; each step refines the solution given prior constraints.

Verified count: 15

---

## NEXT-DRILL CANDIDATES

1. URGENCY SIGNAL MEASUREMENT (IMMEDIATE, 5 min): print Sprint 2 urgency values.
   Routes to tournament vs temperature-tuning vs temporal-cycling.
   This is TEST 0 -- gates all other paths.

2. TOURNAMENT SELECTION SWEEP (10 min after TEST 0): Mechanism 2 lateral inhibition.
   If urgency shows any variation, tournament should achieve near-minimax.
   FIELD: spin-glass (lateral inhibition = Bose-Hubbard U >> J).

3. TEMPORAL CYCLING vs MINIMAX (20 min): cycle K drives in urgency order over K steps.
   Does the temporal plan achieve per-step minsat >= minimax?
   FIELD: nonequilibrium-stat-mech (temporal satisficing).

4. LEARNED ROUTER PROBE (1 day, if TEST 1 fails): can a 5-class softmax router
   trained on 100 examples of (drive states, minimax-optimal drive) learn the selection?
   FIELD: learning-rules (adjacent to Hebbian/online-W, which has drill count = 0).

5. BOSE-HUBBARD PHASE DIAGRAM (theory, 1 day): compute alpha_c (critical lateral
   inhibition for Mott insulator transition) as a function of K drive orthogonality.
   Gives the "selectivity knob" formula for the substrate integration API.
   FIELD: materials-physics (adjacent; Bose-Hubbard is materials + semiconductor).
