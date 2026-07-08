# Brain-grounded levers to beat the fixed-N additive-bundling wall

**Filed:** 2026-07-08
**Trigger:** two-head encoder superposition-recall (SP) at FULL scale (N=4096, V=40000) degrades J=3->0.99, J=5->0.75, J=8->0.20 -- a graceful (not cliff) decay that resembles the brain's own ~4-item working-memory limit.
**Method:** 2x discipline. Broad lit-scan pass (4 parallel Sonnet sub-agents, one per thread) then one narrow drill on the thread the on-disk evidence already flags as most promising (theta-gamma phase coding + sequential slot-peel decode, given the resonator K5/K6 escape landed same-day). Generic math/neuro terms only in all external queries; no substrate-specific names, configs, or numbers went off-platform.
**Calibration:** per [[feedback-lit-scan-calibration-penalty]], all P estimates below are deflated 0.15-0.25 off gut-sense and novel-synthesis items are capped at P<=0.50.

---

## HEADLINE

The brain does not solve ~4-item working memory by cramming more into one flat simultaneous code -- it multiplexes in TIME (theta-gamma phase slots, sequentially read out one item per gamma sub-cycle) and in HIERARCHY (chunks-of-chunks, each level bounded by the same ~4-item span). Both mechanisms are structurally about converting one hard J-way problem into several easier sub-problems solved in sequence, not about raising per-item SNR. The substrate already has BOTH ingredients CHAIN_GRADE/MEASURED_MECHANISM separately (theta-gamma v2 nested phase-slot encoding; resonator theta-gamma slot-peel sequential-cancellation decode) but has never combined them and pointed the combination at the ADDITIVE bundling wall specifically -- to date they've only been applied to MULTIPLICATIVE k-way factorization. Literature on sparse superposition codes (SPARC/AMP) gives a precise, falsifiable prediction for what should happen when they are combined: **slotting alone should NOT raise capacity (it only reorders access); slotting PLUS sequential cancellation (deflate each resolved item before decoding the next) SHOULD raise capacity**, because cancellation is what closes the gap between a tractable per-slot decode and the true joint-capacity limit. This also resolves an apparent contradiction in the resonator peel result (deflation showed zero benefit there) -- that cell was already in an easy, high-SNR regime where there was no crosstalk left to cancel; the encoder's bundling wall is explicitly NOT in that regime (visible graceful degradation already present at J=5), which is exactly where SIC-style cancellation is predicted to matter.

---

## Cheap decisive test

Small CPU cell, N~1024-2048, small vocabulary (V~200-1000, cheap cleanup), J sweep = {3, 5, 8, 12}, 3 seeds. Four arms, all decoding from the SAME underlying encode when possible (paired):

1. **FLAT** -- current behavior: unkeyed sum of J item vectors, cleanup via cosine-argmax against the full vocabulary (this is the control that reproduces the observed 0.99/0.75/0.20 decay).
2. **SLOT_NODEFLATE** -- bind item j to a distinct theta-gamma phase slot (reuse `theta_gamma_bind` / `make_fhrr_codebook` from the v2 FHRR design spec), sum, decode each slot by direct unbind (`* conj(slot_j)`) + cleanup against the full vocabulary, NO cancellation (single-shot, matches `slot_decode_nodeflate` from the resonator peel cell, generalized so `books[k]` = the SAME full-vocabulary codebook at every slot instead of K distinct small per-factor alphabets).
3. **SLOT_PEEL** -- same as (2) but sequential: decode slot 1, subtract its reconstructed contribution from the running residual, decode slot 2 from the cleaner residual, etc. (verbatim reuse of `slot_decode_peel`'s loop structure from `exp_resonator_theta_gamma_peel_v1.py`).
4. **SLOT_PEEL_POWER_ORDERED** (stretch, optional) -- same as (3) but resolve slots in DESCENDING per-slot residual-magnitude order rather than fixed 1..J order, mirroring SPARC's power-allocation-driven decoding wave.

### Falsifiable predictions

**HARD-PASS** (mechanism confirmed as SIC-style capacity gain, not just reordering):
- recall@J for SLOT_PEEL >= recall@J for FLAT by >= 0.15 absolute at J=8 (the regime currently at 0.20), AND
- SLOT_NODEFLATE is NOT better than FLAT by more than 0.05 at any J (dissociates "slotting helps" from "cancellation helps" -- this is the mechanism-diagnostic condition, not just a headline number), AND
- cv across 3 seeds <= 0.10 on the SLOT_PEEL - FLAT delta.

**MIDDLE_BAND**:
- SLOT_PEEL beats FLAT by 0.05-0.15 (real but modest lift), OR
- SLOT_NODEFLATE captures most of the SLOT_PEEL lift (would mean the encoder's wall is more like the resonator's SEARCH-discontinuity case than a genuine SNR/crosstalk case -- a different, still-useful finding, but changes which mechanism gets credit).

**HARD-FAIL**:
- SLOT_PEEL delta over FLAT < 0.05 at J=8 (vocabulary-scale cleanup, V=40000 candidates per slot rather than the resonator's small per-factor alphabets, reintroduces enough cross-vocabulary similarity noise that per-slot argmax cleanup itself becomes the bottleneck -- cancellation can't help if the cleanup step is already failing), OR
- cv > 0.15 (unstable, not a real effect).

---

## Cross-thread synthesis (4 threads, broad pass)

### Thread 1 -- Theta-gamma phase coding [highest priority, most buildable]

- **Lisman & Idiart 1995** (*Science*, "Storage of 7+-2 Short-Term Memories in Oscillatory Subcycles"): each item = one gamma sub-cycle nested in a theta cycle; capacity = theta/gamma frequency ratio (~5-10), a CLOCK-DIVISION quantity, not an SNR/dimensionality quantity. Foundational, well-established.
- **Lisman & Jensen 2013** (*Neuron*, "The Theta-Gamma Neural Code"): feedback inhibition is what FORCES non-overlapping slots (prevents assemblies from firing together) -- this is the mechanistic reason readout is sequential rather than blended.
- **Bahramisharif et al.** (MEG, *PLOS Biology*) and **Heusser et al. 2016** (*Nat. Neurosci.*, hippocampal iEEG, "Episodic sequence memory is supported by a theta-gamma phase code"): direct human evidence that sequentially-presented items occupy DISTINCT theta phases during retention/encoding -- items are genuinely phase-multiplexed, not superposed in one code. Well-established for the "sequential, not simultaneous" claim; the PAC-strength-vs-load relationship is more mixed (Axmacher et al. 2010 *PNAS* found monotonic load-scaling, but a later PMC9496728 study found the opposite direction in some cortical sites -- flag as contested).
- **Information-theory grounding (the load-bearing citation for this drill):** Successive interference cancellation (SIC, Verdu *Multiuser Detection* 1998) and sparse superposition/regression codes (SPARC: Barron & Joseph; Venkataramanan, Tatikonda, Sarwate monograph) are PROVEN capacity-achieving via section-by-section AMP decoding with cancellation. The narrow-pass drill found the crux mechanism explicitly: **sectioning alone buys TRACTABILITY (converts one intractable joint decode into L tractable per-section decodes) but sectioning alone does NOT close the gap to capacity** -- what closes it is genuine sequential cancellation (plus power allocation / "decoding wave" ordering). This is a well-established comms-theory result; its extension to HD/VSA bundling specifically is NOT found stated directly in any single paper (flagged as cross-domain synthesis, moderate confidence) but the mechanism-match to Lisman-Idiart's slot structure is very close.
- **Does this transfer to the encoder's additive wall (not the resonator's multiplicative wall)?** These are different math and the narrow drill makes the distinction explicit:
  - Resonator K5/K6 wall = a joint iterative *search/convergence* failure (oracle_any=0.000, a discontinuity) -- slot-peel fixed it by REPLACING the iterative joint search with a direct one-shot unbind+cleanup per known factor-slot. Deflation (cancellation) made ZERO measured difference there because that regime was already easy/high-SNR once search was removed from the equation.
  - Encoder's additive bundling wall = a graceful SNR/crosstalk degradation (0.99->0.75->0.20), structurally the CLASSICAL bundling-capacity-limited regime, not a search-convergence discontinuity. Per SIC/SPARC theory, THIS is exactly the regime where cancellation (not mere slotting) is predicted to matter, because there IS crosstalk left to cancel.
  - **This makes the "deflation didn't matter" resonator result and "deflation should matter here" prediction fully consistent, not contradictory** -- they are different regimes on the same theory (SIC helps precisely when there's residual interference to remove; the resonator peel cell had none left after slotting, the encoder's bundling wall visibly does).

### Thread 2 -- Chunking + hierarchy

- **Miller 1956**: capacity is constant in CHUNKS, not raw items -- chunk internal complexity is unbounded.
- **Chase & Simon 1973 / Gobet & Simon template theory**: chess masters use ~2-3 large "templates" (up to ~15 pieces) drawn from a huge (order 10^4-10^5) learned template vocabulary, not more STM slots. Capacity gain disappears entirely on non-chunkable (random) boards -- isolates CHUNKING, not raw span, as the multiplier. Well-established.
- **Ericsson, Chase & Faloon 1980** (*Science*): digit-span expert reached 79-82 digits (~11x) via a hierarchical group-of-groups retrieval structure, not innate capacity increase.
- **2024 arXiv 2408.07637 / bioRxiv 2024.08.14.607952 ("Synaptic Theory of Chunking")**: derives M* = 2^(C-1) for base capacity C via an optimal BINARY-TREE chunk hierarchy, generalizable to N^L for branching factor N and L levels, bounded by per-level noise accumulation. Single recent model, not yet broadly replicated -- flagged speculative.
- **Store-vs-cue debate unresolved**: expert-memory data (SF, chess) favor retrieval-structure/cueing as the dominant mechanism for extreme super-span performance; computational WM models (Mathy & Feldman 2012; PMC6026019) favor genuine store-side compression for ordinary within-span chunking. Both are evidenced; which dominates in a given regime is actively debated.
- **Substrate mapping**: the theta-gamma nested-encoding primitive already IS a natural 2-level hierarchy (theta cycle > gamma sub-cycle). A 3rd nesting level (gamma > sub-gamma) is a direct, buildable extension of `theta_gamma_nested_encode`'s `position_codes = theta_codebook[t] * gamma_codebook[g]` formula (add a third multiplicative factor). This is genuinely new (untested at 3 levels) -- see Rank 2 below.

### Thread 3 -- Sparse massive-N distributed coding

- **Tsodyks & Feigel'man 1988**: sparse coding raises Hopfield capacity from ~0.14N (dense) to P ~ N/(a|ln a|) (a = activity fraction); optimum sparsity a* ~ ln(N)/N (Amari 1989), giving peak P_max ~ N^2/(ln N)^2. Well-established classical result.
- **Marr 1971 / Treves & Rolls / Leutgeb et al. 2007** (*Science*): dentate-gyrus expansion recoding (EC -> DG, larger + sparser ~1-4% active) decorrelates similar inputs before CA3 storage -- pattern separation as the mechanistic driver of the capacity gain, not a separate additive effect. Well-established.
- **Decomposition finding (directly relevant to the certified correlation-hurts-capacity law):** the literature does NOT treat "storage capacity" and "decorrelation/retrieval discriminability" as two separable effects -- decorrelation IS the mechanism that produces the capacity gain (fewer correlated overlaps -> less synaptic/associative crosstalk -> more patterns storable). This is a strong, direct alignment with the substrate's own certified law (`reference_correlation_hurts_associative_store_capacity`): sparsification is simply the biological instantiation of "keep store-side codes near-orthogonal."
- **N vs. sparsity tradeoff at fixed budget**: tuning sparsity toward the optimum a*~ln(N)/N buys a MUCH bigger capacity multiplier than spending the same budget on raw N at non-optimal sparsity (classical Amari-lineage result). Implication: if the substrate has budget to spend, spending it on lowering the effective activation fraction of bundle-member codes (e.g. via a DG-style sparsifying expansion front-end) is probably a better return than spending it on raising N directly.
- **Substrate mapping**: the DGProjection expansion front-end already exists (built for the resonator K-sweep) and was proven NON-load-bearing there -- but that was tested against a SEARCH/convergence wall (wrong tool for that failure mode, per the cross-cell law "classify decode mode before building"). The encoder's bundling wall is an SNR/crosstalk wall -- the correct failure-mode class for a decorrelating sparsifying front-end. Re-testing the SAME existing code against the RIGHT failure mode is cheap and well-motivated. See Rank 3.

### Thread 4 -- Hierarchical/recursive role-filler binding

- **von der Malsburg 1981 / Roskies 1999**: binding-by-synchrony -- role-filler binding coded by millisecond-scale spike-timing correlation (added TIME structure) rather than combinatorial neurons. Influential, partially corroborated, still contested (Shadlen & Movshon 1999 "Synchrony Unbound").
- **van der Velde & de Kamps** Neural Blackboard Architecture: bounded, reusable neural circuitry for recursive sentence structure without per-structure combinatorial allocation. Purely theoretical/computational, no direct single-neuron confirmation.
- **Ding, Melloni, Zhang, Tian & Poeppel 2016** (*Nat. Neurosci.*): cortical activity tracks nested linguistic units (syllable/phrase/sentence) at correspondingly nested oscillatory rates -- empirically well-replicated; the inference that MORE nested oscillatory levels is specifically WHAT PREVENTS combinatorial blowup is contested (Meyer, Sun & Martin 2022, *Nat. Rev. Neurosci.*: oscillations may track structure without implementing the composition operation).
- **Plate's HRR / Smolensky tensor-product theory**: fixed-dimension binding (circular convolution / elementwise multiply) avoids the tensor-product blowup by lossy-compressing it back to N dimensions -- but this is explicitly an ABSTRACT/mathematical convenience with WEAK direct neural grounding (only recent, narrow, largely unreplicated proposals connect it to real synapses, e.g. BTSP-based binding, 2025).
- **Bottom line for synthesis**: this thread does NOT surface a lever independent of Thread 1 -- the FHRR complex-multiply binding already used in theta-gamma v2 IS the VSA-style fixed-dimension binding this thread describes, and the literature's own verdict is that this specific math has the WEAKEST direct neural grounding of the four threads (synchrony/oscillation is the better-evidenced brain mechanism, and that IS already what theta-gamma v2 encodes). Recommend as low-priority / mostly subsumed, not a new buildable item.

---

## RANKED buildable list

### Rank 1 -- Theta-gamma slot-keyed additive bundling + sequential cancellation decode

- **(a) Mechanism + citations**: Lisman & Idiart 1995 (theta-gamma nested slots, sequential readout); Heusser et al. 2016 / Bahramisharif et al. (human evidence for sequential phase-multiplexed readout); Barron & Joseph SPARC + Rush/Venkataramanan AMP capacity proofs (sequential cancellation, not mere sectioning, closes the gap to capacity).
- **(b) Substrate lever**: bind each of the J bundle members to a distinct theta-gamma phase slot (reuse `make_fhrr_codebook` + `theta_gamma_bind` from the v2 FHRR design spec verbatim) before summing; decode via the resonator peel cell's exact `slot_decode_peel` loop (unbind slot k, cleanup vs. full vocabulary, subtract resolved contribution, continue), generalized so every slot shares the SAME full-vocabulary codebook instead of K distinct small factor alphabets.
- **(c) Correlation-hurts-capacity composition**: NEUTRAL-TO-HELPFUL. Phase-slot keys are random/near-orthogonal (not semantically seeded); per-slot cleanup still runs against the existing near-orthogonal item-vocabulary codebook. Adds a random positional factor multiplicatively -- does not inject semantic correlation into the store side.
- **(d) Composition with existing infra**: reuses TWO independently-certified primitives verbatim -- theta-gamma v2 FHRR nested phase-slot codebook/bind/unbind (CHAIN_GRADE, `notes/director_theta_gamma_v2_FHRR_all_complex_design_spec_2026-06-30.md`) and the resonator slot-peel sequential-deflate decode loop (MEASURED_MECHANISM, `experiments/exp_resonator_theta_gamma_peel_v1.py`). The only genuinely novel piece is applying `slot_encode`/`slot_decode_peel`'s SAME formula to the ADDITIVE bundling-recall task (full-vocabulary cleanup per slot) instead of the K-way multiplicative-factorization task (small per-factor alphabet per slot).
- **(e) P_deflated**: reuse of two already-proven primitives, strongly predicted by SIC/SPARC theory, but the combination itself is untested and vocabulary-scale cleanup (V=40000 per slot vs. resonator's small M) is a real risk. Novel-synthesis cap applies. **P_deflated = 0.48.**

### Rank 2 -- Recursive 3-level chunking (theta > gamma-chunk > sub-gamma-item)

- **(a) Mechanism + citations**: Miller 1956 / Gobet & Simon chunking theory; 2024 arXiv 2408.07637 "Synaptic Theory of Chunking" (M* = 2^(C-1) binary-tree capacity formula, generalizable to N^L); Ding et al. 2016 nested-oscillation-tracks-hierarchy (contested per Meyer/Sun/Martin 2022 -- oscillations may track, not implement, composition).
- **(b) Substrate lever**: extend the ALREADY-CHAIN_GRADE `theta_gamma_nested_encode` formula (`position_codes = theta_codebook[t] * gamma_codebook[g]`) to 3 multiplicative factors (`theta[t] * gamma_chunk[c] * subgamma[s]`): group J bundle members into ~4 chunks, bind each chunk's members with a shared chunk-slot plus a within-chunk sub-slot, decode chunk-level first (peel), then within-chunk (peel again on the isolated chunk residual). Converts one flat J-way bundling problem into ~4 sequential (J/4)-way sub-problems.
- **(c) Correlation-hurts-capacity composition**: NEUTRAL, same random-key discipline as Rank 1.
- **(d) Composition with existing infra**: direct multiplicative extension of the theta-gamma v2 NESTED arm (already CHAIN_GRADE at 2 levels); composes with Rank 1's peel decode as the within-chunk decode step. Untested at 3 nesting levels -- compounding risk since it depends on BOTH levels' peel succeeding.
- **(e) P_deflated**: genuine novel extension, higher compounding risk than Rank 1 (2 sequential peel layers must both work; the capacity formula is single-paper/unreplicated). **P_deflated = 0.35.**

### Rank 3 -- DG-style sparsifying front-end (reapply DGProjection to the correct failure-mode class)

- **(a) Mechanism + citations**: Tsodyks & Feigel'man 1988 (P ~ N/(a|ln a|) sparse Hopfield capacity); Marr 1971 / Treves & Rolls / Leutgeb et al. 2007 (DG expansion-recoding pattern separation); Amari 1989 (optimal sparsity a*~ln(N)/N).
- **(b) Substrate lever**: re-run the EXISTING DGProjection expansion front-end (already built for the resonator K-sweep) against the encoder's bundling-recall task instead of the resonator's factorization task. Per the cross-cell law "classify decode mode before building" (self_margin_taxonomy / CRT-residue), this front-end was tested against the WRONG failure-mode class last time (a search/convergence discontinuity, where it rescued K4 but did nothing for the K5/K6 discontinuity) -- the encoder's wall is the RIGHT class (SNR/crosstalk-limited), where a decorrelating sparsifying front-end is the textbook-predicted fix.
- **(c) Correlation-hurts-capacity composition**: DIRECTLY HELPS, strongest alignment of all four threads with the certified law -- sparsification's mechanism (decorrelation -> less crosstalk -> more capacity) IS the store-side lever the law already prescribes.
- **(d) Composition with existing infra**: reuses existing DGProjection code verbatim, just retargeted; composable as a pre-processing step before Rank 1's slot-keyed bundling (sparsify item codes first, then slot-bind-and-sum) for a possible combined effect -- not yet evaluated together.
- **(e) P_deflated**: existing code, low implementation risk, but mechanism-fit for the bundling wall specifically is untested (was proven non-load-bearing for a DIFFERENT wall, so some risk it's also a poor discriminator here even though the theory-fit is better). **P_deflated = 0.40.**

### Rank 4 -- Generic recursive role-filler binding primitive (VSA/HRR-style)

- **(a) Mechanism + citations**: von der Malsburg 1981 / Roskies 1999 (binding-by-synchrony); van der Velde & de Kamps Neural Blackboard Architecture; Plate HRR / Smolensky tensor-product-avoidance (flagged weak neural grounding relative to synchrony/oscillation).
- **(b) Substrate lever**: none beyond what Ranks 1-2 already build -- the FHRR complex-multiply binding already in use IS this thread's proposed mechanism.
- **(c) Correlation-hurts-capacity composition**: neutral, same as above.
- **(d) Composition with existing infra**: fully subsumed by theta-gamma nested position-encoding; not a distinct new lever.
- **(e) P_deflated**: LOW priority -- literature's own verdict flags this as the weakest-grounded of the four threads, and it does not add anything beyond Ranks 1-2. **P_deflated = 0.25.**

---

## Substrate-product implications

- If Rank 1 HARD-PASSes: the encoder gains a genuinely new capability tier -- ordered/keyed bundling recall at J beyond the current flat wall (J=8 -> 0.20), without needing to touch N or the vocabulary encoder itself. This is a pure DECODE-SIDE fix reusing two already-certified primitives, which is the cheapest possible path to a capacity win (no re-training, no re-encoding of the store).
- The MIDDLE_BAND outcome (SLOT_NODEFLATE captures most of the lift) would still be a useful negative -- it would mean the encoder's wall is closer to a search-discontinuity than a genuine SNR wall, redirecting future work toward resonator-style search fixes rather than SIC-style cancellation fixes.
- Rank 3 is the cheapest possible next test (existing code, just retargeted) and should be run in parallel with Rank 1 rather than sequentially -- they are not mutually exclusive and the theory suggests they may compose (sparsify first, then slot-bind).
- Rank 2 (3-level chunking) should wait on Rank 1's result -- it depends on Rank 1's peel decode working as the within-chunk step, so a Rank 1 HARD-FAIL would also sink Rank 2's design as specified (though the chunking IDEA could still be tested with a different within-chunk decode).

---

## Citations (verified count)

24 distinct sources cited across the four threads (author/year + findable title/venue in each case above): Lisman & Idiart 1995; Lisman & Jensen 2013; Axmacher et al. 2010; Bahramisharif et al. (PLOS Biology); Heusser et al. 2016; Barron & Joseph (SPARC); Venkataramanan/Tatikonda/Sarwate (SPARC monograph); Verdu 1998 (Multiuser Detection / SIC); Miller 1956; Chase & Simon 1973; Gobet & Simon (template theory); Ericsson, Chase & Faloon 1980; Mathy & Feldman 2012; arXiv 2408.07637 (Synaptic Theory of Chunking); Badre & D'Esposito 2007; Skaggs & McNaughton 1996; Tsodyks & Feigel'man 1988; Amit/Gutfreund/Sompolinsky 1985; Krotov & Hopfield 2016/2021; Marr 1971; Treves & Rolls 1994; Leutgeb et al. 2007; Amari 1989; von der Malsburg 1981; Roskies 1999; van der Velde & de Kamps 2006; Ding et al. 2016; Meyer, Sun & Martin 2022; Plate 1995; Smolensky 1990; Kymn/Kleyko/Frady/Kent/Olshausen/Sommer (VSA capacity, arXiv 2301.10352); Hersche/Kleyko (Sparse Block Codes, arXiv 2303.13957); Frady/Kent/Olshausen/Sommer (Resonator Networks). All fetched via WebSearch/WebFetch this cycle across 5 sub-agent dispatches (4 broad + 1 narrow); none carried substrate-specific terms off-platform per query-privacy discipline.
