# Research analysis: 6 R-PRIME directions + 5 new fields

**Filed:** 2026-05-24 by orchestrator (verbatim from user analysis).
**Status:** Active research agenda. Week 1 priority = R-PRIME-2 + R-PRIME-1.

---

## R-PRIME directions (6)

### R-PRIME-1 — PAC-Bayes KL-accumulation floor
**Premise:** Multi-task retention has an information-theoretic floor set by KL divergence accumulation across task switches. Each new task's posterior must remain close (in KL) to the joint over all prior tasks; the rate of KL growth bounds retention from below.
**Falsifier:** Measured retention drops faster than the KL-floor predicts (substrate is below the information-theoretic limit and the floor isn't binding).
**Promotion gate:** Bet B retention vs. predicted KL-floor across phase-A norm regimes; if measured floor tracks predicted within +/- 20% across 3+ regimes, promote PAC-Bayes row 🔬 -> 🟡.
**Why it matters:** Gives a *non-substrate-specific* lower bound the substrate must respect; if substrate beats it, we've discovered something. If it tracks it, we have a closed-form retention predictor.

### R-PRIME-2 — MoE M_c falsifier
**Premise:** If retention is governed by per-expert capacity M_c (not global M), then K-sweep at fixed M_total should show retention scaling with M/K, not M. The model "Mixture-of-Experts on substrate" makes this a sharp, falsifiable claim.
**Falsifier:** K-sweep at fixed M_total = 64, K in {2,4,6,8,10,12,14,16}. If retention is flat in K, MoE-on-substrate REJECTED. If retention scales with M/K (concretely: retention(K) = f(M_total/K) within 10%), MoE row -> 🟢.
**Promotion gate:** PASS = scaling matches MoE prediction within 10% on 4+ K values; KILL = retention flat or non-monotone in K.
**Why it matters:** Directly probes whether substrate is doing implicit expert allocation. Cheap (1 GPU-day). High signal/noise.

### R-PRIME-3 — task-pair geometry
**Premise:** Bet B retention depends on representational distance between task pairs. Closer task pairs (in HD-space inner product) should interfere more.
**Falsifier:** Retention vs. mean(<v_taskA, v_taskB>) shows no correlation (r < 0.3 across 8+ task-pair instances).
**Promotion gate:** Correlation r > 0.6 with monotone sign promotes task-geometry row 🔬 -> 🟡.
**Why it matters:** Already partially supported by Bet B retention variance across corpus pairs (variance is large; geometry is the leading explanation).

### R-PRIME-4 — Allen-Cahn t^(1/2) [REJECTED 2026-05-24]
**Premise:** Phase-field theory predicts retention decay as t^(1/2) under Allen-Cahn dynamics.
**Falsifier (now triggered):** `wave14_betB_allen_cahn_tsweep_v1` slope = 0.069, outside the predicted [0.3, 0.7] band.
**Outcome:** REJECTED. Decay is monotone (retA 0.860 -> 0.829 over t=1..21) but functional form is NOT t^(1/2). Bet M needs reframing — see roadmap note.

### R-PRIME-5 — SSM / HiPPO connection
**Premise:** Substrate dynamics may be equivalent to a structured state-space model with HiPPO measure. If so, retention is set by the HiPPO basis projection.
**Falsifier:** Measure substrate retention against HiPPO-LegS / LegT closed-form decay; if no fit within 15% across t in {1..50}, REJECTED.
**Promotion gate:** Closed-form fit within 15% promotes SSM row 🔬 -> 🟡.
**Why it matters:** Would give an O(N log N) algorithmic accelerator for the substrate via SSM-style state recurrence.

### R-PRIME-6 — Clifford / TN R5 narrowing
**Premise:** Clifford-algebra and tensor-network framings should narrow toward a specific R5-style rank/order regime where substrate operations factor cleanly.
**Falsifier:** No R5 sub-structure appears in measured operator-spectra; substrate has full-rank dense behavior at all scales.
**Promotion gate:** Spectral analysis reveals consistent R5 / low-rank-tensor block structure across 3+ operations.
**Why it matters:** Would unlock efficient sparse / structured-algebra implementations.

---

## 5 new fields worth deep inspiration

### Field-A — Reservoir computing
**Why:** Substrate dynamics look like an echo-state reservoir with HD readout. Lyapunov spectrum + memory-capacity curves are mature literature.
**Key probe:** Measure substrate Lyapunov spectrum at the edge-of-chaos operating point. If sub-substrate matches reservoir-computing edge-of-chaos signatures, opens echo-state mapping.

### Field-B — List decoding (coding theory)
**Why:** Multi-hop recall == list-decoding the bundle. Johnson bound, Guruswami-Sudan algorithms are precisely the tools for "decode multiple superimposed codewords."
**Key probe:** Map substrate multi-hop accuracy curves to Johnson-radius prediction.

### Field-C — Statistical physics of inference (cavity / replica method)
**Why:** Bet B retention is a free-energy minimization over a disordered system. Replica-symmetric and 1-RSB calculations give closed-form retention predictors.
**Key probe:** Replica-symmetric ansatz on substrate's retention landscape; compare to measured retention curves.

### Field-D — Differential privacy
**Why:** Bet B retention with replay == DP-SGD with privacy budget. Renyi-DP composition theorems give retention floors.
**Key probe:** Treat each replay batch as a DP mechanism; compute Renyi-DP composition; compare to measured retention.

### Field-E — Neuroscience replay (hippocampal)
**Why:** Replay-prioritization-by-norm we just tested has direct analogs in hippocampal replay literature (Foster & Wilson, Pfeiffer & Foster). Norm-weighting maps to value-weighted replay.
**Key probe:** Operationalize "value-weighted replay" mechanisms (TD-error-weighted, novelty-weighted) on substrate; compare retention vs. uniform.
