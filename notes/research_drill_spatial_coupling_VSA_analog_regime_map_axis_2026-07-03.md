# Research drill — spatial-coupling as candidate VSA regime-map axis (2026-07-03)

## (a) HEADLINE
**MAYBE — ONE_PROBE_ONLY, not axis promotion.** P_deflated = **0.20**. Analogy is FORMAL (BP-MAP gap ↔ argmax-listwise corridor, both are area-integrals of an informativeness curve) but the LDPC saturation mechanism is intrinsically ITERATIVE (traveling-wave propagation from seeded boundary through coupled DE); VSA one-shot argmax has no wave-propagation surface, and no prior VSA/HRR paper implements a cross-item structural coupling with a proven capacity-corridor widening. Recommendation: one probe cell to test if coupled-storage + iterative retry (NOT plain argmax) widens the dominance corridor at flip=0.35-0.45.

## (b) Lit-scan (3 sub-agent breadth pass)
- **Kudekar/Richardson/Urbanke 1001.1826 (BEC) + 1004.3742 (BMS):** SC-LDPC construction = chain of L identical component ensembles + coupling window w>=2 + boundary termination seed. Coupled-DE recursion x_i^(t+1) = f((1/w) sum_j x_j^(t)) admits a traveling-wave solution: correct decoding nucleates at pinned boundary and propagates inward each iteration. BP threshold saturates to MAP threshold.
- **Yedla/Jian/Nguyen/Pfister 1204.5703 (scalar) + 1208.4080 (vector):** Potential-function proof — saturation is a property of any MONOTONE COUPLED RECURSION with spatial window + boundary pinning + well-behaved potential. Decouples result from LDPC-specific graph structure. Endpoint threshold characterizable STATICALLY (variational problem), but REACHING it requires the iterative wave.
- **Krzakala et al. 1109.4424 + Donoho-Javanmard-Montanari 1112.0708 (coupled compressed sensing):** Block-structured measurement matrix + seed block + AMP state evolution collapses algorithmic phase transition α_AMP(ρ) down to information-theoretic Wu-Verdu limit. Mechanism = 1D wave of decreasing MSE propagating from seed. NO one-shot / plain-L1 analog found.
- **Salavati-Karbasi-Vetterli 1302.1156 (expander AM) + follow-ups:** Exponential capacity from linear-algebraic subspace structure + iterative bit-flipping / GDBF localized correction on expander graph. Capacity gain tied to iterative decoder, not static readout.
- **Applicability boundary:** In all four frameworks, capacity/threshold widening is tied to a decoder that carries LOCAL extrinsic information across the coupling window through multiple rounds. No one-shot / matched-filter / argmax analog was located.

## (c) Formalization of "structural cross-item context" for VSA/HRR
Concrete definition: a coupling tensor C_{ij} on stored items such that retrieval of item i uses evidence from items j in a neighborhood N(i) with |N(i)| = w. Candidates evaluated:
- **Co-occurrence graph** (items frequently co-bundled share a coupling edge). Closest to LDPC protograph — structured, monotone, admits potential function.
- **KG relations** (items linked by explicit relation r couple through r's inverse). Richer but heterogeneous; monotonicity NOT guaranteed.
- **Temporal proximity** (sequence-adjacent items couple with window w). Analogous to Yedla's 1D spatial recursion; monotone; boundary = sequence endpoints.
- **Semantic clusters** (items in cluster c share a coupling matrix). Discrete-block structure, analogous to protograph blocks.
Most analogous to LDPC coupled protograph: **temporal proximity** (1D, monotone, natural boundary) or **co-occurrence graph** (protograph-like). LDPC bind/unbind interaction: coupling would enter as a shared-role-slot vector v_r added at bind time; unbind of item i would sum contributions from N(i) weighted by C_{ij}.

## (d) Prior VSA structured-storage work
Convergent NEGATIVE finding across resonator networks (1906.11684), sequential HDC / SDM sequences (partial, treated as noise not exploited), structured VSA (Kleyko survey 2111.06077; capacity analysis 2301.10352), graph/KG-VSA (HolE 1510.04935; ComplEx), modern Hopfield / DAM (Ramsauer 2008.02217, structured-Hopfield 2402.13725, structured-knowledge AM PMC9759586). **NO surveyed paper implements LDPC-style cross-item spatial coupling with a proven capacity-corridor widening.** Structured-knowledge AM has the mechanism SHAPE (shared tensor across items) but explicitly disclaims capacity gain. Sequential HDC has soft coupling from Hamming-ball overlap but treats it as noise.

## (e) Candidate cell design — coupling-strength sweep as ONE-PROBE
Cell name: `probe17_coupling_strength_corridor_widening`. Parameterization: coupling strength `c` in {0.0, 0.25, 0.5, 0.75, 1.0}; retrieval mode in {ARGMAX, LISTWISE_TAM}; base regime at n = d^2 = midpoint of dominance corridor (n log n / 2 point). Structure: temporal coupling (Yedla-1D) with window w=3, boundary seed = perfect first/last item. Factors: c, mode, seed (3 seeds). Predicted phase transitions per regime:
- c=0, ARGMAX: below corridor (per AM 2605.05189) -> baseline fail
- c=0, LISTWISE: baseline pass (in corridor)
- c=1, ARGMAX: **if coupling widens corridor for one-shot, ARGMAX now passes**; if not, still fails
- c=1, LISTWISE: pass (no worse)
**HARD-PASS threshold:** delta_acc (c=1, ARGMAX) - (c=0, ARGMAX) >= 0.15 at midpoint AND monotone-in-c AND consistent across 3 seeds. **HARD-FAIL threshold:** delta_acc <= 0.03 OR non-monotone OR seed-dependent sign.

## (f) Cheap decisive test
The ONE cell above. Discriminator: **argmax-mode delta at c=1 vs c=0 at the midpoint of the dominance corridor** (single scalar effect size). Cost: 15 cells (5c x 2 modes x 3 seeds; ~15 min local CPU at n~1024, d~40). Distinguishes "coupling widens corridor for one-shot" from "coupling helps only iterative/listwise retry" (control arm) from "coupling irrelevant" (no delta anywhere).

## (g) Anti-drift discriminator
Three confound-checks:
1. **Dimensionality confound:** effective dimension of coupled bundle >= dim of uncoupled bundle. Report d_eff = trace(cov)^2 / trace(cov^2). Reject if delta_acc tracks delta_d_eff (mislabeled higher-dim substrate effect).
2. **Bundling confound:** replicate at fixed BUDGET (energy / total norm held constant across c). Rejects "coupling = more storage capacity trivially".
3. **Axis-aliasing check:** vary M (item count) at c=0.5 fixed. If coupling delta scales identically with M as bundle noise scales with M, alias detected.

## (h) Cross-thread synthesis
- **Probe 16 SHARDED-cliff #56:** sharded storage's own cliff is a load-factor phase transition (M/N ratio, Kanerva sphere-packing). Coupling would introduce a THIRD covariate — but note SHARDED already has cross-slot structure via hash function; SHARDED with additional temporal coupling is over-parameterized. Recommend testing coupling on BUNDLED regime first (cleaner baseline).
- **axis-aliasing #48:** coupling axis vs F (fan-out) — coupling with w-window and F fan-out could alias since both introduce cross-item overlap. Discriminator (g.3) directly addresses.
- **sharded_capacity atom:** if coupling doesn't help SHARDED (which is already near cuckoo-hashing cliff), the negative result would not close the general coupling question; test BUNDLED first.
- **cortex CG v1+v2:** cortex composition = an iterative-retry surface with soft evidence carrying (per LDPC-Maxwell drill 2026-07-04 note). Coupling analog most naturally lives INSIDE cortex composition — coupled-storage + soft-evidence carrying is the LDPC-Maxwell-EXACT analog. That is where P is HIGHEST.
- **M-sweep CG_META regime cross-term (session 2026-07-03):** the CG_META cross-term result already probes a coupling-like effect (regime cross-term = shared context between M and other axis). Coupling axis proposed here is subordinate: test whether explicit coupling ADDS to CG_META cross-term or is REDUNDANT with it.

## (i) Composition with Regime Map arc — does this become a NEW axis?
**NO — collapses onto existing axes.** Argument: (1) if coupling requires iterative retrieval to have effect (per lit convergence), then coupling is a MODIFIER of the retrieval-mode axis, not a new axis. (2) if coupling has effect only with soft-evidence carrying, it collapses onto the "cortex composition" axis (LDPC-Maxwell drill 2026-07-04 already flagged this). (3) if coupling has effect with argmax alone, it would still likely alias with F (fan-out) or M (item count) per (g.3). **Recommendation: treat coupling as a MODIFIER of cortex-composition regime, not a Regime Map axis.**

## (j) Substrate-product implications
IF probe17 HARD-PASSES: retrieval-capacity uplift under coupled-storage = argmax dominance corridor widens by area-theorem-bounded factor, historically 0.02-0.10 acc units in comparable AM sweeps (per LDPC-Maxwell drill). Cost: coupling matrix C_{ij} is O(n * w) storage; O(w) additional bind ops per item. Negligible at w=3. IF HARD-FAILS: closes the "structural context widens corridor for one-shot" question NEGATIVELY; concentrates future effort on soft-evidence carrying inside cortex composition (already the LDPC-Maxwell primary target).

## (k) Citations (verified count = 12)
- arxiv 1001.1826 (KRU BEC saturation)
- arxiv 1004.3742 (KRU BMS saturation)
- arxiv 1204.5703 (Yedla scalar potential proof)
- arxiv 1208.4080 (Yedla vector potential proof)
- arxiv 1109.4424 (KMSSZ coupled compressed sensing)
- arxiv 1112.0708 (Donoho-Javanmard-Montanari optimal CS via coupling+AMP)
- arxiv 1302.1156 (Salavati-Karbasi-Vetterli expander AM)
- arxiv 1906.11684 (Frady/Kent/Olshausen/Sommer Resonator Networks 2)
- arxiv 2111.06077 (Kleyko HDC survey)
- arxiv 2301.10352 (VSA capacity analysis)
- arxiv 2008.02217 (Ramsauer modern Hopfield)
- arxiv 2605.05189 (Sharp Capacity Thresholds Linear AM — corridor result, primary anchor)
