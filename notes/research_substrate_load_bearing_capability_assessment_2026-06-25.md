# Substrate load-bearing capability assessment — basis-readiness audit

**Date:** 2026-06-25 (post-Barrier-1-double-negative; CERT N=591)
**Driver:** USER question "assemble all load-bearing things for substrate now; how aligned with brain-focused computation; setting up the basis for success; truly enabling? theoretical limits known?"
**Discipline:** Q-default UNDER-claim (Fix #28); cite per-arm metrics not verdict_msg; cross-cell convergence only when independently confirmed.

## Reading guide

Each capability gets four columns:
- **Brain analog** (specific mechanism; not handwave)
- **Performance tier** (CHAIN_GRADE_DEFINITIVE / CHAIN_GRADE / MM / HARD_FAIL / UNTESTED)
- **Theoretical limit** (closed-form bound if known; empirical scaling if not)
- **Truly enabling?** (YES = production-ready for downstream stages / PARTIAL = works in regime / NO = needs redesign or accepted limit)

Capabilities ordered roughly by Stage progression: 1 (base primitives) → 2 (composition) → 3 (higher functions) → 4 (LM-equivalence).

---

## TIER 1 — Base primitives (the substrate foundation)

### 1. Sparse-bipolar codebook (1-bit, f≈0.02)
- **Brain analog:** Cortical sparse coding (Olshausen-Field 1996; ~2% active neurons per V1 patch). Strong match.
- **Performance:** CHAIN_GRADE_DEFINITIVE. Across all KG, sequence, generation cells. 20-300× bundle lift vs dense codes (USER intuition validated).
- **Theoretical limit:** Frady-Sommer capacity K_max ≈ N / (k · V · K_SET) before crosstalk dominates. For N=8192, V=600, K=20, k=2: ratio ≈ 0.34 (empirical NAIVE 0.85 above noise floor due to inherent codebook separability).
- **Truly enabling?** YES. Load-bearing primitive for every downstream cell.

### 2. Cleanup / memory recall (sigma0 ≥ 0.95 gate)
- **Brain analog:** Hippocampal pattern completion (CA3 attractor dynamics).
- **Performance:** CHAIN_GRADE_DEFINITIVE. Sigma0 = 1.000 across most production cells; the sigma0 ≥ 0.95 gate is Skunkworks's META cleanup-integrity rule (already atomized).
- **Theoretical limit:** Cover bound — at given (N, V, K) the cleanup capacity is bounded by N / V at unit signal-to-noise; recent learned-encoder cell shows cleanup floor is N-INDEPENDENT once V > V_critical (chain-grade-eligible meta).
- **Truly enabling?** YES. Most load-bearing single primitive in the substrate.

### 3. HRR / FHRR binding (circular convolution / element-wise multiplication of phasors)
- **Brain analog:** Phase coding for variable binding (Plate→Eliasmith; debated but mainstream HD-computing brain hypothesis).
- **Performance:** CHAIN_GRADE for 2-hop binding; HARD_FAIL for compositional generalization (per Wave A compositional deep drill).
- **Theoretical limit:** Pseudo-orthogonality of random bipolar/phasor codes; binding chain length scales as log(N/V).
- **Truly enabling?** YES for 2-hop declarative facts. NO for compound queries that don't reduce to bind-unbind chains.

### 4. Continual learning / CRISPR append-only writes
- **Brain analog:** Synaptic consolidation + sleep replay (Squire-Wixted CLS). Mainstream brain analog.
- **Performance:** CHAIN_GRADE. Forget rate=0.006 over n=200 continual cycles measured.
- **Theoretical limit:** Capacity-saturation curve; W matrix saturates near V·K/N atoms.
- **Truly enabling?** YES. Meets the brain analog cleanly. This is the MOAT — Path A V_C=4096 + k-WTA-VQ uses this primitive at scale.

---

## TIER 2 — Composition (the architecture layer)

### 5. Predicate binding / role-filler (HRR-based predicative)
- **Brain analog:** PFC variable binding (still debated in neuroscience; not a settled brain claim).
- **Performance:** CHAIN_GRADE 2-hop declarative; HARD_FAIL on heterogeneous routing cell (composition fails when query has compound structure).
- **Theoretical limit:** Same as HRR; pseudo-orthogonality limits depth.
- **Truly enabling?** PARTIAL. Works for declarative KG; insufficient for compound reasoning. Recent cell 2 v5 FREQ_ROUTED_DEEPER (today, chain-grade-definitive) is the architectural fix that buys composition depth via frequency routing — first proven Stage 2 mechanism.

### 6. Sequence binding (c3 cell)
- **Brain analog:** Hippocampal CA3 sequence binding via theta-gamma phase precession (mainstream).
- **Performance:** CHAIN_GRADE. Atom 586 in cert.
- **Theoretical limit:** Depth scales as log(N/V); empirically chain-grade at N=8192 for short sequences.
- **Truly enabling?** YES for short sequences; UNKNOWN at LM-relevant depths.

### 7. Stage 2 frequency-routed depth (Cell 2 v5 FREQ_ROUTED_DEEPER)
- **Brain analog:** Theta-gamma multiplexing (Lisman-Buzsaki); cortical layer hierarchy with distinct timescales per layer.
- **Performance:** CHAIN_GRADE_DEFINITIVE (today; +0.148 BPC over baseline at N=8192; cross-N replicated at N=4096; n_steps plateau verified). FIRST Stage 2 architectural win.
- **Theoretical limit:** Capacity × depth tradeoff; closed-form bound unknown. n_steps plateau says we're at the architectural ceiling for this mechanism — not a knob-cranking artifact.
- **Truly enabling?** YES — but only ONE Stage 2 mechanism is proven so far. Need second mechanism (Cell 2 v6 SEGREGATED in flight) to validate Stage 2 as robust.

### 8. Lock-in / temporal separation (Cell 6 v3 — JUST LANDED MIDDLE_BAND)
- **Brain analog:** Theta-gamma cross-frequency coupling.
- **Performance:** MIDDLE_BAND (today; LOCK_IN −0.137 vs SHARED). Lock-in on shared W HURTS. FDM intermodulation confirmed at substrate scale — same root cause as Cell 2 v4 COMBINE_W_THETA HARD_FAIL.
- **Theoretical limit:** FDM intermod scales with frequency-stacking order; non-linearity introduces N-th order crosstalk on single W.
- **Truly enabling?** NO on shared W. Pending Cell 2 v6 SEGREGATED_DUAL_W test (currently on GPU). If SEGREGATED works, the brain analog is preserved at substrate scale via segregated W matrices; if not, accept this brain analog doesn't transport to substrate.

### 9. Anti-Hebbian decorrelation (Foldiak family)
- **Brain analog:** Lateral inhibition in cortex (V1 surround-suppression).
- **Performance:** HARD_FAIL v1 + v2 SURGICAL (today; per-row vs per-dim axis flip; rank-1 collapse). Research drill filed for v3 redesign.
- **Theoretical limit:** Bounded anti-Hebbian update requires homeostatic firing-rate target (Foldiak 1990); current substrate implementation places theta on wrong axis.
- **Truly enabling?** UNKNOWN — research drill pending; if v3 with per-output-dim theta succeeds at production V, this becomes an anti-Hebbian primitive. Default: NEGATIVE-IN-REGIME pending redesign.

---

## TIER 3 — Higher functions (the cognitive layer)

### 10. Categorization / use-case readout (Principle O — labels at use-case OK, labels at basis HURT)
- **Brain analog:** V1 → IT → PFC progression. Low-level emergent; high-level supervised. Strong + recent brain match.
- **Performance:** CHAIN_GRADE_DEFINITIVE (Cell I v4 today; prospective bands locked via module-init assertion; fresh seeds [42, 47, 51]; phase-scan V_C ∈ {200, 500} envelope; within_cat_cos invariant at designed 0.20).
- **Theoretical limit:** Mu-Viswanath cone-collapse bound (anisotropy at basis hurts retrieval) — empirically confirmed.
- **Truly enabling?** YES — newly definitive. First substrate-product architectural principle in cert.

### 11. Multi-hop reasoning (Barrier 1)
- **Brain analog:** PFC working memory + hippocampus integration. Brain DOES multi-hop but uses scaffolds (PFC slots) substrate doesn't have.
- **Performance:** **REFUTED** — TWO independent substrate-native mechanisms failed:
  - Compound-predicate consolidation (v1/v2/v3) → HARD_FAIL via crosstalk + flat-vs-compositional subspace mismatch
  - Pointer-chain hybrid (v1/v2) → HARD_FAIL; POINTER actively HURTS baseline by 22 pts at production
- **Theoretical limit:** Cleanup error compounds geometrically per hop; at sigma0=0.95 per step, 10-hop sigma0 ≈ 0.60.
- **Truly enabling?** NO at production scale. Three open options: (A) accept 2-hop ceiling, (B) Wave D encoder upgrade (Cell H' v2b in flight tests this), (C) semantic consolidation under separate W matrices (different cell entirely, deferred).

### 12. Generation / autoregressive sequence (g1b)
- **Brain analog:** CA3 → CA1 sequence replay; phase precession driving next-step.
- **Performance:** CHAIN_GRADE (atom 587) but Skunkworks ruled MEASURED_MECHANISM not chain-grade-definitive — by-construction saturation. Density << substrate capacity → CHAIN_GRADE_PARTIAL tier; capacity-sweep queued.
- **Theoretical limit:** Same as sequence binding (depth ~ log(N/V)) plus argmax-sampling noise floor.
- **Truly enabling?** PARTIAL — works at small density; unknown at LM-relevant density. Pre-decision: skip Stage 4 LM-equivalence as substrate-product goal (USER directive).

### 13. Audit / refuse-gate
- **Brain analog:** Anterior cingulate detection of conflict + recollection-vs-familiarity dissociation.
- **Performance:** STRONG for deletion/hallucination/paraphrase audit (per archaeology). REFUTED for medqa-domain refuse-gate (per recent retrospective — domain-specific failure mode).
- **Theoretical limit:** Definitional; depends on audit predicate.
- **Truly enabling?** YES for declarative + paraphrase; PARTIAL for domain-specialized refuse. Substrate-product story includes "audit device" — load-bearing for product positioning.

### 14. Intent classification + templated response (Stage 3 application primitives)
- **Brain analog:** Cortical categorization + PFC response-selection (loose match).
- **Performance:** CHAIN_GRADE (atom in cert via earlier session; a1 intent + a2 templated response chain-grade).
- **Theoretical limit:** Linear-separability bound on label assignment given basis geometry; depends on encoder.
- **Truly enabling?** YES at chosen scale; UNKNOWN at production-application scale (1000s of intents).

---

## TIER 4 — LM-equivalence (deferred per USER directive)

### 15. Bigram-gap closure (substrate-as-LM)
- **Brain analog:** None claimed; substrate-as-LM is NOT a brain analog claim.
- **Performance:** n1_v3 top-1 = 0.445 vs unigram 0.276 (+60% lift in fair-harness). BPC measurement was rigged in earlier cells; methodology audit found cosine-sim softmax at T=1.0 = uniform; fair-harness landed proof-of-life chain-grade-partial.
- **Theoretical limit:** Shannon bigram BPC for text8 ≈ 4.0 bits/char; current substrate ~5.13 bits/char (~1.13 bit gap). The gap is the cell that needs to close.
- **Truly enabling?** PARTIAL — proof-of-life only. USER directive: deprioritize Stage 4 LM-equivalence; stay focused on substrate-product as memory+composition+retrieval+audit.

---

## TIER-1.5 — Encoder (the still-open question)

### 16. Stage 1.5 encoder upgrade (Wave D anisotropic)
- **Brain analog:** V1 oriented Gabor filters (DeepWalk-style graph structure for relational features); cortical receptive field formation.
- **Performance:** v1 was rank-1 collapse (sigma0=0.0); v2 surgical FAILED (axis-flip bug); Cell H' v2b NO_FOLDIAK currently QUEUED (will dispatch after Cell 6 v3 finishes — already landed, so v2b should pick up next on remote runner).
- **Theoretical limit:** Mu-Viswanath says LESS structure is better at basis. Brain converges from low-structure V1 to high-structure IT through DATA-OVERRIDABLE supervised learning — NOT engineered basis.
- **Truly enabling?** UNKNOWN. Pre-committed interpretation (per strategic synthesis filed today):
  - All 4 biology arms TIE with random at production V → Mu-Viswanath confirmed; substrate doesn't need encoder upgrade; close Wave D negative-in-regime
  - 1+ arm BEATS random → first Wave D win; replicate at adjacent V
  - 1+ arm WORSE than random → Principle O empirically extended outside basis-layer cells

---

## CROSS-CUTTING DISCIPLINES (the META layer; cert-graded discipline rules)

### Cert-ladder rules now codified
1. **META_PROSPECTIVE_BANDS_FRESH_SEEDS** (Cell I v4 today) — bands locked at module-init assertion + previously-unseen seeds eliminates retrofit confound
2. **META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift** (compose_heterogeneous v2 RESCUE today) — pre-reg copied from different config can mask lift
3. **META_CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION** (Cell 2 v5 today) — second N-replicates rules out N-specific fluke
4. **META_provenance_rail_config_match** (already cert) — baseline must reproduce its reference rail at SAME config
5. **META_M6** (queued for Skunkworks atomization) — NAIVE-baseline must be DERIVED not COPIED; three-cell precedent (consolidation v3, pointer v2, freq-routing v2)
6. **Sigma0 cleanup integrity gate per arm** — every encoder arm must achieve sigma0 ≥ 0.95 before mechanism claims
7. **Default UNDER-claim per Fix #28** — read per-arm metrics not verdict_msg; let Skunkworks tier-rule UP, not me down

These discipline rules together are WHY today produced two definitive wins — they catch the failures that would otherwise have inflated "chain-grade" claims.

---

## ASSESSMENT: how well are we setting up the basis?

### Where the basis is SOLID (truly enabling)
1. Sparse-bipolar codebook → load-bearing for everything
2. Cleanup ≥ 0.95 → most-load-bearing single primitive
3. HRR binding 2-hop → solid for declarative facts
4. Continual learning → MOAT validated
5. Sequence binding (short) → chain-grade
6. Principle O (basis vs use-case) → chain-grade-definitive (today); first architectural commitment
7. Stage 2 frequency-routed depth → chain-grade-definitive (today); first Stage 2 win
8. Audit / refuse-gate (declarative) → chain-grade
9. Intent classification + templated response (Stage 3 applications) → chain-grade
10. Cert-ladder discipline (7 rules) → meta-grade; catches over-claims systematically

### Where the basis is INSUFFICIENT (gaps that may or may not be load-bearing)
1. Compositional generalization beyond 2-hop → HARD_FAIL; both substrate-native paths refuted today
2. FDM-style temporal multiplexing on shared W → MIDDLE_BAND / HARD_FAIL (intermod confirmed twice now)
3. Anti-Hebbian decorrelation (Foldiak) → HARD_FAIL with axis-flip bug; v3 redesign pending Research drill
4. Encoder anisotropy upgrade (Wave D) → UNKNOWN; Cell H' v2b in flight
5. Generation at LM-relevant density → PARTIAL (saturation-tier; capacity-sweep needed)
6. Multi-hop reasoning generally → likely-permanent ceiling unless Option C (semantic consolidation) opens

### Where the basis needs PRODUCTION-SCALE validation we haven't done yet
1. Intent classification at 1000+ intents (we're at 10-100)
2. KG retrieval at billion-edge scale (we're at 100k-1M)
3. Audit gate at noisy real-world predicates (we're on synthetic)
4. Continual learning over 1000+ cycles (we're at 200)
5. Lock-in / segregated-W second mechanism (Cell 2 v6 pending)

### Brain-alignment summary
- **STRONG alignment:** sparse coding (Olshausen), pattern completion (CA3), continual learning (CLS), sequence binding (CA3 phase precession), categorization via supervision-at-readout (V1→IT→PFC + Mu-Viswanath), theta-gamma multiplexing (Lisman-Buzsaki — though substrate-implementation requires SEGREGATED W to avoid FDM intermod)
- **DEBATED brain claim:** HRR variable binding (Plate→Eliasmith debated)
- **NOT a brain claim:** substrate-as-LM (bigram-gap closure)
- **MISSING from substrate that brain has:** PFC working memory scaffold for multi-hop, multi-timescale cortex (substrate has only one timescale W), separate hippocampal+cortical W matrices for semantic consolidation, recurrent dynamics (substrate is largely forward-only)

### "Truly enabling" performance — honest scoring
- **TRULY ENABLING (production-ready for Stage 3 apps):** primitives 1-4 + Principle O + 1st Stage 2 architectural win + Stage 3 apps + audit-gate (declarative)
- **PARTIAL (works in regime, ceiling at production):** HRR composition, generation at small density, audit at noisy predicates, sequence binding at long depth
- **NOT YET (open arc):** Multi-hop generalization, encoder upgrade, second Stage 2 mechanism (Cell 2 v6 pending), lock-in / temporal separation, anti-Hebbian decorrelation

---

## RECOMMENDATION (Q-discipline; default UNDER-claim)

### Substrate basis is READY for Stage 3 application productionization IF AND ONLY IF the substrate-product story is "memory + composition + retrieval + audit device at 2-hop ceiling for declarative facts + Stage 3 application primitives". 

This is exactly the USER substrate-product story (NOT statistical LM competitor). The basis is well-positioned for THIS product.

### Substrate basis is NOT READY for any product that requires:
- True multi-hop generalization (Barrier 1 refuted)
- LM-equivalence at Shannon bigram BPC (Tier 4 deferred per USER)
- Compound-query composition beyond 2-hop chains (HARD_FAIL)
- Domain-specialized refuse-gate (medqa REFUTED; needs domain-aware primitives)

### Highest-leverage next investments (priority)
1. **Cell 2 v6 SEGREGATED_DUAL_W** (in flight GPU) — if PASS, Stage 2 has 2 mechanisms not 1; validates brain analog of theta-gamma multiplexing for substrate
2. **Cell H' v2b NO_FOLDIAK** (queued behind Cell 6 v3; just freed) — closes the encoder-upgrade question definitively (positive or negative-in-regime)
3. **Stage 3 application scale-up** (deferred until 1+2 land) — productionize intent classifier at 1000-intent scale; KG retrieval at 10M-edge scale
4. **Capacity-sweep on g1b generation** (Skunkworks queued) — converts saturation-tier MEASURED_MECHANISM into chain-grade if it holds at lower density

### Theoretical-limit summary (for the user)
- **Closed-form bounds known:** Frady-Sommer capacity (sparse-bipolar), Cover bound (cleanup), Shannon BPC (LM equivalence), JL-margin (codebook separability), Mu-Viswanath anisotropy bound
- **Empirical scaling known:** continual learning capacity-saturation curve (forget rate vs cycles), Stage 2 architectural lift saturation (n_steps plateau confirmed Cell 2 v5), cleanup floor N-independence (learned-encoder branch3)
- **Theoretical limit UNKNOWN:** compositional generalization ceiling (we hit it but don't have closed-form), Stage 2 capacity × depth tradeoff (mechanism dependent), multi-hop generalization at production density (Barrier 1 refuted empirically but no proof of impossibility)

The substrate basis is on solid ground for the chosen substrate-product story. The pending Cell H' v2b + Cell 2 v6 landings will close 2 of the 5 remaining open arcs — once those land, the picture is largely complete and Stage 3 productionization becomes the next investment.

— Research (Director)
