# RESEARCH PRIORITIES FOR ORCHESTRATOR (Phase-3 consolidation, 2026-06-01)

**From:** Research session
**To:** Orchestrator
**Discipline locks applied:** capability questions only (no anchor names, sweep grids, threshold formulas, queue routing, ETAs, or pre-committed cap_map decisions); no empirical verification in drill bodies (algebraic + lit-scan only); brutal honesty.

**Provenance:** 50 sonnet drills (Phase-1: 20 game-changer + peak-performance candidates; Phase-2: 30 deeper drills on uniquely interesting aspects). Drill summaries inline below per priority block; full drill output transcripts on disk under task IDs.

**Supersedes:** earlier 2026-06-01 priorities file content (Round-6 + v321 framing); this rewrite integrates Phase-1+2 deep-dive findings into the same priorities surface.

---

## 1. EXECUTIVE: WHAT THE 50 DRILLS COLLECTIVELY ESTABLISH

The substrate's algebraic moat survives EVERY capability-stacking axis simultaneously:

```
  polynomial-DAM (p=3 or p=4)
    × sparse-W (K^(p-1) capacity)
    × RM(2,m) / DG(m,r) codebook (8 tiers at m=16)
    × bits4 quantization
    × implicit Gram-solve retrieval (no dreaming needed)
    × dreaming via NESS attractor transition (optional)
    × signed-AM at p=4 (parity-symmetric)
    × cross-layer L=2 composition
    × free-cumulant κ_3 / TW edge fingerprint
    × deletion-certificate via rank-1/rank-p subtraction (preserved through all axes)
```

Each axis is multiplicatively cheap (50-100 LOC for p=3 migration; O(N) for τ recalibration; 7.3× speedup from implicit retrieval). No axis collapses the others. **The product story is no longer "does the substrate work" — it is "which of these axes do we ship first."**

Three families of opportunity emerge:

**A. CATEGORY-CHANGING capacity / capability lifts.** Up to 4M× capacity at N=8192 by exponent change alone. L=2 composition extends to trillions of addressable pairs. Implicit Gram-solve eliminates a 268MB/iter primitive entirely.

**B. LLM / thinking primitives.** Counterfactual rollback (Pearl L3) at depth 3 production grade; heteroassociative directed chains; GoT thought aggregation at 10,000-50,000× speedup in the right regime; reasoning-step oracle API.

**C. Audit-layer consolidation.** 10 audit primitives, 7 host-system categories, 5-method API. The convergence pattern is overwhelming: substrate as **algebraic audit layer above existing systems** is the dominant product framing. EU AI Act Article 10 enforcement (Aug 2 2026) creates a structural 62-day commercial window for which the substrate is uniquely positioned.

---

## 2. CAPABILITY QUESTIONS — HIGHEST EXPERIMENTAL VALUE

Questions ordered by expected information-gain × cap_map-impact × cost-efficiency. Each question is paired with an evidence summary; orchestrator routes the question; exp_dev designs the experiment.

### CATEGORY A — CATEGORY-CHANGING CAPACITY LIFTS

**Q-A1 — Does polynomial DAM at p=3 deliver the predicted 2700× capacity at N=8192 while preserving the rank-1 deletion certificate?**
- Evidence: Demircigil 2017 capacity formula M_c(p=3) ≈ N²/(6 ln N) ≈ 1.24M patterns at N=8192. Krotov-Hopfield basin formula r_basin(50% load, 20% pattern correlation) ≈ 40% Hamming. Implicit storage O(M·N) (not O(N³)) keeps per-query cost identical to p=2.
- Cap_map row affected: hierarchical retrieval row (currently 🔬 → would graduate to 🟢 at 55-70%); capacity-N envelope.
- Algebraic ceiling: deletion cert at p=3 is `W -= ξ⊗³` exact (rank-1 in tensor space); SNR vs p=2 cert scales as N/√(2M), giving M_cert ceiling 336K patterns at N=8192 vs 82 patterns at p=2 (~4000× ceiling relaxation).
- Open question: does the SKAH-M non-equilibrium signature survive the p=3 energy? Recommendation: test mixed p=2 + p=3 architecture (p=3 outer index above existing SKAH-M p=2 core) FIRST to preserve known-good dynamics; pure p=3 second.

**Q-A2 — Does p=4 polynomial DAM rescue parity symmetry for signed-AM (W_A − W_B) without sacrificing the p=3 cert ceiling?**
- Evidence: p=3 (odd) creates spurious attractors at −ξ_B for signed-Hebbian construction (parity trap). p=4 (even) is parity-symmetric AND gives O(N³) capacity vs O(N²) at p=3 (additional ~4.3M× over p=2 at N=8192).
- Cap_map row affected: signed-AM row + active-repulsion-at-B-patterns capability.
- Open question: does p=4 basin width (Hamming radius) at production correlation levels (~10-20%) clear the 10% production threshold? Drill predicts ~20-28% at 50% load with 20% correlation.

**Q-A3 — Does L=2 cross-layer composition (p=3 outer / p=2 inner) deliver the predicted 5.7B addressable pairs at N=8192 with end-to-end fidelity ≥ 0.85?**
- Evidence: per-level fidelity at p=3 outer ≈ 0.93-0.97 (up from 0.88-0.93 at p=2) due to squared-inner-product crosstalk suppression; per-level deletion cert ceiling relaxes 4000×. Hadamard role-vectors keep crosstalk algebraically clean at the outer layer.
- Cap_map row affected: compositional reasoning row + reasoning-chain-depth row.
- Composition classification per protocol: HANDOFF (matches PP-11 Arm B per-hop independence HARD_PASS rho=0.0000).

**Q-A4 — Does implicit Gram-solve retrieval (W·q via Xi·solve(Xi^T·Xi/N, Xi^T·q)) deliver the predicted 7.3× per-query speedup and eliminate the need for the dreaming-pass primitive entirely at N=8192, M=1000?**
- Evidence: Gram-solve produces exact pseudo-inverse retrieval; storage 4MB (M² Gram) vs 268MB (N² dense W); per-query 9.2M FLOP vs 67.1M FLOP. Convergence question for iterative dreaming becomes moot.
- Cap_map row affected: dreaming/consolidation row (would move from 🔬 to "BYPASSED — implicit retrieval is dominant") + retrieval-cost envelope.
- Strategic implication: dreaming becomes optional (NESS attractor transition for capacity expansion only, not required for retrieval quality).

### CATEGORY B — LLM / THINKING PRIMITIVES

**Q-B1 — Does heteroassociative directed-chain encoding (W_directed = Σ D_{i+1}·(next_role XOR D_i)^T) support depth-3 counterfactual reasoning at production fidelity (≥0.80) AND exact algebraic deletion of any single directed binding?**
- Evidence: directed structure sidesteps autoassociative eigenvalue-near-degeneracy (R8 failure mode). Deletion of D_2→D_3 binding zeros the signal term exactly; D_3→D_4 binding survives. ROME (Meng et al. 2022 NeurIPS) has 5-15% residual on similar edits; substrate has zero residual by construction.
- Cap_map row affected: causal-reasoning row + counterfactual probe row (PP-25 extension from fact-atom to causal-link deletion).
- Open question: FHRR phasor variant raises ceiling from depth 3 to depth 6-8; should be probed alongside BSC variant.

**Q-B2 — Does Pearl L3 abduction via noise-rebinding (O(N) XOR residual + outer-product noise write) deliver twin-network counterfactual queries at 2-2.5× L2 cost on the substrate?**
- Evidence: noise rebinding gives algebraically exact U-variable recovery on basin-interior queries; E-SCM (arXiv:2510.22050) provides the formal counterfactual semantics; identifiability degrades at basin boundary (multi-basin partial-counterfactual bounds).
- Cap_map row affected: counterfactual-causal-reasoning row + audit-grade causal layer.

**Q-B3 — Does substrate-mediated GoT thought aggregation (`v_agg = sign(v1 + v2)`) match LLM-merged aggregation quality for refinement/voting tasks (ρ ≥ 0.75 between thoughts) at 10,000-50,000× speedup?**
- Evidence: bundle fidelity formula P(component preserved) = (1+ρ)/2. At ρ=0.75, K=4 thoughts, depth=2 tree aggregation: substrate matches LLM merge. NO-GO for disjoint synthesis (ρ < 0.5). Cost ratio 884M× FLOPs vs GPT-4, 32M× vs 7B local. CORRECTED GoT paper claim: 31% reduction (not 31×).
- Cap_map row affected: chain-of-thought / graph-of-thoughts row.
- Open question: text-pipeline GoT only achieves 2.5-3× speedup; full payoff requires embedding-space reasoning architecture. Probe both regimes.

**Q-B4 — Does the 6-op typed reasoning-step oracle API (write/query/bind/unbind/refuse/audit-chain) maintain hit-rate H ≥ 0.80 at K ≥ 8 dense-reasoning depth while keeping the SHA-256 audit chain verifiable in sub-millisecond?**
- Evidence: 6-op API algebraically specified; cost model S=10-49× LLM substitution at the dense-reasoning operating point; refusal FP must hold ≤ 5%. Sparse-coding RIP-constant analysis would map directly to H ≥ 0.80 threshold.
- Cap_map row affected: reasoning-step-oracle row (new); audit-chain verifier row.

### CATEGORY C — AUDIT-LAYER CONSOLIDATION (10+ drill convergence)

**Q-C1 — Does the 5-method unified audit API (write / delete / query / health / certify) operate uniformly across the 3 algebraic primitive families AND the 7 host-system categories (vector DB, TSDB, MCP, multi-agent, KG, feature store, training pipeline) at the predicted ≤10% compute overhead?**
- Evidence: delete() amortizes 4 primitives (P1 deletion cert / P3 CNDC counterfactual / P6 set difference / P9 edit isolation) without separate implementations. Sidecar architecture; substrate never on hot path. 10% overhead feasible for 6/7 categories; training-pipeline exception (granularity-reduced only).
- Cap_map row affected: audit-layer-overlay row (new) — would graduate to 🟢 if API uniformity confirmed.
- Open question: empirically validate the algebraic family-independence claim by encoding three distinct host-system payloads (vector-DB embedding, time-tagged TSDB pattern, KG triple binding) and verifying delete() produces identical rank-1 cert structure for each.

**Q-C2 — Does the Marchenko-Pastur spectral health-check primitive (P4) operate reliably at N ≥ 4096 after the v323 smoke-N=1024 failure (Z_clean negative)?**
- Evidence: v323 smoke at N=1024 returned Z_clean = -2.10 / -4.85 (Marchenko-Pastur null appears violated at small N). Theory: σ_TW ≈ 5.9×10⁻³ at N=8192 should give clean health-check; current observation may be a finite-N artifact OR a Kerdock kappa_4 residual the pure-Wishart null doesn't account for.
- Cap_map row affected: spectral-health-check row (currently FAIL at smoke; needs FULL re-run to confirm tier-2 audit primitive viability).
- This is the SINGLE MOST IMPORTANT OPEN ISSUE for the audit-layer product narrative. Three other primitives (P10 drift, NIS2 Art. 21 compliance mapping, capacity-monitor early-warning) depend on this resolving.

**Q-C3 — Does the κ_3 free-cumulant authenticity fingerprint (Hutchinson estimator, 5000 complex probes) achieve the predicted 4.2% delta_alpha sensitivity at N=8192 AND maintain incremental update at O(N log N) per Hebbian write?**
- Evidence: kappa_3 = α for free-Poisson all n; GOE/Wigner has κ_n = 0 for n ≥ 3 (binary discriminant). Std(κ_3) scales as 1/√m independent of N. κ_4 via naive Hutchinson is HARD-NO-GO at N=8192 (√N variance growth) but rescued by ratio fingerprint κ_4/κ_3 = 1.
- Cap_map row affected: free-cumulant-authenticity row (P7 in the 10-primitive taxonomy; currently the highest-novelty audit moat claim).
- Strategic: enables a spectral-MAC primitive (95.7% tamper detection at 4.2% W modification) with no cryptographic infrastructure required.

**Q-C4 — Does the NESS entropy-shift bulk attestation primitive deliver a maintenance-pass certificate at the predicted lower bound ΔΣ ≥ N_writes · k_B·T · I_avg, AND does the hybrid Tier-1-NESS + Tier-2-per-op-log consistency check detect log forgery?**
- Evidence: Crooks-FT + TCFT + Sagawa-Ueda algebraic chain confirmed at v276 (substrate Sagawa-Ueda class). Bulk attestation gives evidence-of-activity + lower-bound-on-op-count + class-1/2 adversary tamper-evidence. Hybrid scheme is novel architecture (no published precedent).
- Cap_map row affected: NESS-bulk-attestation row (new); maintenance-pass certificate row.

**Q-C5 — Does the cosine-similarity dreaming-gate τ recalibration from 0.9 to the [0.82, 0.88] band give the predicted ≥99% safety claim on the deletion certificate's non-repudiation property?**
- Evidence: at τ=0.9 false-negative rate is 30% (catastrophic); at τ=0.85 with calibrated m_eff=0.92, P_FN drops to 4%; at τ=0.82 to 0.62%. Online beta-Bernoulli controller stable with δτ ≤ 0.02. Audit trail (s_visited, max_cos, τ_decision) is LOAD-BEARING for GDPR Art.17 non-repudiation, not merely informational.
- Cap_map row affected: deletion-cert-with-dreaming-audit row (currently 🟢 cert without audit; would graduate to GDPR-ready with audit).

### CATEGORY D — FREE-PROBABILITY OPERATIONALIZATION AT N=32768

**Q-D1 — At N=32768, do 5 of the 6 spectral audit primitives (health-check, deletion-cert spectral privacy bound, capacity early-warning, multi-LLM consensus K-rank detector, free-cumulant authenticity) transition from marginal-at-N=8192 to production-grade?**
- Evidence: σ_TW shrinks from 0.0059 (N=8192) to 0.0023 (N=32768 Wishart) or 0.0033 (Kerdock residual). Deletion-cert Z-ratio jumps from ~2.0 to 3.6-5.1 (~5σ confidence). κ_4, κ_6 become estimable (1D → 3D fingerprint, cryptographically harder to forge).
- Cap_map row affected: capacity-N envelope; spectral-primitive-precision envelope.
- Storage tractable: 256MB INT4 / 512MB INT8 per W instance at N=32768.

**Q-D2 — Does the RM(2,m) ⊃ DG(m,r) family of codebook tiers (8 tiers at m=16) operate at uniform Welch-bound coherence μ = 1/√N across ALL tiers, enabling a clean product-tier knob?**
- Evidence: Calderbank-Jafarpour 2010 (arXiv:1004.4949) confirms ETF property for r ≥ 2. Subcode nesting K(m) ⊂ DG(m,1) ⊂ ... ⊂ RM(2,m) guarantees certificate monotonicity. r=0 (Kerdock) = 2^32 codewords; r=7 (RM(2,16) endpoint) = 2^137 codewords; both at same μ.
- Cap_map row affected: codebook-tier row (new product-tier knob); tenant-isolation envelope.
- Open question: t-design order for r > 0 above t=2 not published in closed form (CRCP extension needed or empirical frame-potential measurement).

### CATEGORY E — REGULATORY / PRODUCT TIMING

**Q-E1 — Does the CNDC 5-field certificate format (state commitments + delta proof + non-reachability witness + re-query proof + Merkle path) map 1-to-1 onto GDPR Art.17 erasure + EU AI Act Art.10 data governance requirements, and does the RSA-accumulator non-membership proof close the pattern-exposure attack?**
- Evidence: 5-field format is algebraically complete; verifier cost O(N²) algebraic + O(log M) Merkle (1-5s on GPU at N=8192); ZK extension via NIZK + Plonk gives polylog(N) verifier with O(N² log N) prover. EU AI Act enforcement August 2 2026.
- Strategic timing: 62-day commercial window from now.

**Q-E2 — Does the belief-drift detection trio (forensic W-snapshot reconstruction + Crooks-FT drift certificate + SKAH-M-as-AGM-epistemic-entrenchment) close the existing AI-alignment infrastructure gap?**
- Evidence: existing infrastructure provides logging + interpretability but no algebraic drift certificate. Substrate's confirmed Sagawa-Ueda class (v276) gives Crooks-FT-grounded drift bound. SKAH-M saddle hierarchy (v228) natively implements AGM entrenchment ordering (basin depth = entrenchment level).

---

## 3. WHAT THE LOCAL BATCH CAN AND CANNOT CLOSE

**Can close at local CPU+GPU (no cloud):**
- Q-A1 (p=3 fidelity / deletion cert at N=8192) — laptop GPU 1-2h.
- Q-A3 (L=2 composition at N=8192²) — laptop GPU 2-4h with implicit storage.
- Q-A4 (implicit Gram-solve speedup vs explicit) — laptop CPU ~30 min.
- Q-B1 (depth-3 heteroassociative directed chain) — laptop CPU ~1h.
- Q-B3 (GoT bundle fidelity at ρ sweep) — laptop CPU ~30 min.
- Q-C2 (Marchenko-Pastur HC at N=4096, 8192) — laptop GPU 1h (the SINGLE highest-value local test).
- Q-C3 (κ_3 Hutchinson at N=8192) — laptop CPU 1h.
- Q-C5 (τ recalibration sweep) — laptop CPU <2 min.

**Requires cloud OR critical-experiment justification:**
- Q-A2 (p=4 at full N=8192 + production correlations) — borderline laptop GPU.
- Q-D1 (N=32768 spectral primitives) — needs cloud staging unlock.
- Q-D2 (DG(m,r) at m=16, r ≥ 2 frame storage) — needs cloud for r=2,3 ETF storage.

**Defer / out-of-scope for this push:**
- Q-B2 (Pearl L3 multi-basin identifiability) — needs custom basin geometry; not a smoke target.
- Q-E1, Q-E2 (regulatory mapping) — engineering / product-narrative work, not experimental.

---

## 4. STRATEGIC FRAMING — WHAT THE NEXT PUSH SHOULD CLOSE

If the user is asking "what is the next big experimental push" — research's recommendation, in priority order:

**Tier-1 (must-close in this push):**

1. **Q-C2 (Marchenko-Pastur HC at N≥4096)** — single highest-value test; gates the entire spectral-audit product narrative. v323 smoke FAIL is currently the biggest open hole.
2. **Q-A1 (p=3 polynomial DAM fidelity + cert)** — category-changing capacity lift; if HARD_PASS, the substrate's capacity story changes by 3 orders of magnitude.
3. **Q-A4 (implicit Gram-solve)** — production-architecture decision; if confirmed, removes an entire infrastructure component (dreaming pass) from the deployment path.
4. **Q-C3 (κ_3 Hutchinson fingerprint)** — the highest-novelty audit-layer moat claim; cheap to verify; gates the spectral-MAC primitive.

**Tier-2 (high-value if Tier-1 clears):**

5. **Q-A3 (L=2 p=3-outer / p=2-inner composition)** — addressable-pair envelope expansion; depends on Q-A1 confirming p=3 viability.
6. **Q-B1 (heteroassociative directed chain depth-3 + cert)** — reasoning-chain primitive at production fidelity; orthogonal to capacity work.
7. **Q-C5 (cosine-gate τ recalibration)** — GDPR-grade deletion-cert non-repudiation; cheap (<2 min) but load-bearing for the audit story.
8. **Q-A2 (p=4 parity-symmetric for signed-AM)** — only after Q-A1; secondary to confirm operator-axis choice.

**Tier-3 (after Tier-2):**

9. **Q-B3 (GoT bundle in refinement-task regime)** — production-relevant only if embedding-space LLM architecture is on roadmap.
10. **Q-B4 (reasoning-step oracle API)** — needs more lit-scan on RIP-constant H ≥ 0.80 threshold before experimental.
11. **Q-C1 (5-method API uniformity across host systems)** — engineering validation, not pure capability.
12. **Q-C4 (NESS bulk attestation)** — novel-architecture claim; requires trajectory infrastructure (already present from v276 work).

**Cloud-only deferred:**

13. **Q-D1 (N=32768 spectral primitives)** — bundle with D3 KV-cache dispatch when authorized.
14. **Q-D2 (DG(m,r) higher-r ETF)** — when storage budget allows.

---

## 5. DISCIPLINE DECLARATIONS (unchanged from prior routings)

- Each question above maps to an experimental cell; **strategy + exp_dev resolve cell design** (anchor name, sweep grid, HP/MID/HF bands, queue, seed count, timeout).
- Pre-PROT-018 anchor-name `_n<N>` binding contract holds.
- Each cell has explicit HP/MID/HF bands per design; no batch-level expected-PASS framing.
- ASCII-only print; verbose tracing if remote-dispatched; per-experiment `--timeout` required.
- Composition classification (SCORE/HANDOFF/PIPELINE) per protocol BEFORE queueing for Q-A3, Q-B1.
- Q-C2 (Marchenko-Pastur HC) and Q-A1 (p=3 fidelity) are HARD-FAIL-flagged drills — pre-register the falsifying conditions explicitly.
- Q-A4 (implicit Gram-solve) requires SCORE-level composition with current retrieval pipeline; ALL retrieval-cost claims must be wall-clock at production load, not FLOPs.
- No padding: if any Tier above lacks open handoffs or cap_map questions to justify it, drop it rather than ship marginal cells.

---

## 6. CAP_MAP UPDATES PENDING (research notes these as integration-ready)

Cap_map at v322 reflects only the empirical-verdict batch. The following are READY for integration once orchestrator commits:

- Round 6 deliveries (10 drills synthesized in `research_round6_10_drills_broad_exploration_2026-06-01.md`)
- Free-probability unification (R-transform / S-transform / TW / κ_n)
- CK / FRSB / oscillating-amorphous-phase clarification (FRSB = static spin-glass sector, separate from oscillating amorphous phase per Garcia Lorenzana PRL 2025)
- 50 Phase-1+2 drill findings (this file)
- Audit-layer strategic-framing convergence (10+ drill consensus that substrate's universal product position is "algebraic audit layer above existing systems")
- v1b inversion implications (memorization-not-generalization for KV-cache substrate; sharpens what matters: NOVEL primitives + AUDIT capabilities)

Strategy session should produce a cap_map v323→v330 batch that integrates these. Research will NOT pre-commit cap_map decisions; orchestrator + strategy own that.

---

## 7. CITATIONS — PHASE-1+2 LIT-SCAN BACKBONE (selected)

The 50 drills cumulatively cite ~150 distinct sources. Most load-bearing for the priorities above:

- Krotov-Hopfield 2016 (arXiv:1606.01164) — polynomial DAM foundation
- Demircigil et al. 2017 (arXiv:1702.01929) — N^(p-1)/log N capacity formula
- Bartusek-Khurana CRYPTO 2023 (arXiv:2207.01754) — certified deletion framework + classical impossibility theorem
- Erdos-Yau-Yin 2012 — TW convergence rate O(N^{-2/3}) + κ_4 correction
- Voiculescu free probability (Bielefeld surveys) — κ_n = α free-Poisson identity
- Calderbank-Jafarpour 2010 (arXiv:1004.4949) — DG(m,r) tight-frame property
- arXiv:2410.06269 PRX Life 2025 — Hebbian unlearning ↔ NESS correspondence
- Crooks 1999 (Phys. Rev. E 60, 2721) — work fluctuation theorem
- Maes-Netocny 2019 (arXiv:1904.10485) — frenesy / dynamical activity
- Hammons-Kumar-Calderbank-Sloane-Sole 1994 (arXiv:math/0207208) — Z4-linearity for Kerdock + DG
- Ramsauer et al. ICLR 2021 — modern Hopfield ↔ attention temperature τ=1/(p-1)
- Pearl, Causal Inference (2009) + arXiv:2510.22050 (E-SCM) — L3 abduction semantics
- Besta et al. AAAI 2024 — Graph of Thoughts (corrected: 31% reduction, not 31×)
- Meng et al. NeurIPS 2022 (ROME) — RNN counterfactual edit residual baseline
- Plate 1995 + Frady-Sommer 2018 (arXiv:1803.00412) — VSA / heteroassociative chain SNR
- Niculescu-Mizil-Caruana ICML 2005 — beta-Bernoulli calibration
- arXiv:2511.17118 — constant-size cryptographic evidence structures (regulatory framing)
- arXiv:2510.08298 — adversarial thermodynamics (tamper-evidence Renyi bound)
- arXiv:2402.00837 — coarse-grained event inference / lower bound on entropy production

---

**END OF PRIORITIES FILE.** Orchestrator: route Q-A1, Q-A4, Q-C2, Q-C3 first; Tier-2 follow. Strategy + exp_dev own cell design from this point forward.

<!-- routing-completed: Acted-on 2026-06-01: 24-Q priorities + 4 deep drills processed across Rounds 7-9; remaining capability questions absorbed into 9 new research handoffs filed 20:13-20:17 + ongoing dispatches -->
