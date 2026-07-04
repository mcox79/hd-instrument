# Brain 5x-drill angle 4/5 — is dense-retrieval / sparse-storage a REAL biological regime-switch?

**Date:** 2026-07-04
**Author:** Research (Director / Opus 4.8 1M)
**Angle:** Does the BRAIN use a DIFFERENT representation for RETRIEVAL/QUERY vs sparse STORAGE — a biological regime-switch? (a) is recall denser than the sparse engram? (b) does the query carry more info than the stored trace, then settle to the sparse attractor? (c) is asymmetric coding (dense query -> sparse store) a real biological principle?
**Calibration:** lit-scan penalty applied (deflate raw P 0.20; novel-synthesis cap 0.50).
**Substrate prior-work check:** RUN (`substrate_query.sh`, cosine top-5) — NOT none; three directly relevant priors reconciled below.

---

## HEADLINE — one sentence

**YES, strongly brain-grounded: the hippocampal-neocortical memory system is fundamentally a KEY-VALUE store with ASYMMETRIC representations — a SPARSE, pattern-separated addressing/binding code (DG ~1-2% active -> CA3 recurrent attractor) that is a DIFFERENT object from the DENSE, distributed content it reinstates (neocortex, driven back from a dense entorhinal cue) — and retrieval REINSTATES a stored dense value via the sparse index rather than RECONSTRUCTING content from the sparse code; so a regime-switch (2% sparse for STORAGE+ALGEBRA, dense readout for RETRIEVAL) is the biological factorization, NOT a hack — provided we LINK a stored dense value to the sparse key rather than trying to COMPOSE/decode the dense readout out of the sparse code (which is exactly what our prior READOUT_DEGENERATE attempt did).**

---

## The three sub-questions — mechanism verdicts

### (a) Is the retrieval/recall pathway denser / graded relative to the sparse stored engram? — YES

- **Dentate gyrus (DG)** is the sparsifier: ~1-2% granule cells active (some estimates <1%), expansion recoding of a smaller EC input onto many more granule cells for pattern SEPARATION. This is the biological analog of our 2% sparse code — and it is the STORAGE/orthogonalization stage, not the readout stage.
- **CA3** is sparse-but-denser (~2-4%), an auto-associative recurrent attractor that stores the engram.
- **Entorhinal cortex (EC) II/III -> perforant path** carries the RETRIEVAL CUE: a DENSER, distributed grid/place cortical pattern. The query that drives recall is denser than the sparse hippocampal trace it addresses.
- **Neocortex** holds the CONTENT densely; the recalled percept is a DENSE reinstated cortical pattern.
- Net: query (dense EC) -> sparse index (DG/CA3) -> dense reinstated content (cortex). Both ENDS are denser than the sparse MIDDLE. The sparse code is the addressing waypoint, not the retrieval output.

### (b) Does the query carry MORE info than the stored trace, then settle to the sparse attractor? — YES on FORMAT, with a key nuance

- **Format:** the cue's representational format (dense EC/cortical) is richer/denser than the sparse stored code — confirmed.
- **Nuance on information content:** classic auto-association is completion of a PARTIAL cue (cue carries LESS semantic content, network fills in). But the cue is delivered in a dense format and CA3 settles to the sparse stored attractor via recurrent pattern completion (Neunuebel & Knierim 2014: degraded DG->CA3 input restored to the stored representation; CA3 change < EC/DG change = error-correction/completion signature).
- **Critical:** retrieval does NOT terminate at the sparse attractor. CA3 completion -> CA1 -> EC deep layers -> neocortex REINSTATES the dense cortical pattern (hippocampal reinstatement precedes and predicts neocortical reinstatement; gamma phase-synchrony gates it). The sparse settle is an intermediate ADDRESSING event; the RETRIEVAL OUTPUT is the dense reinstated value. This is exactly the regime-switch: address in the sparse space, read out in the dense space.

### (c) Is asymmetric coding (dense query -> sparse store) a real biological PRINCIPLE? — YES, it is arguably THE central principle of episodic memory

Three convergent, well-established frameworks — this is textbook, not speculative:

1. **Hippocampal Memory Indexing Theory** (Teyler & DiScenna 1986; Teyler & Rudy 2007). The hippocampus stores a SPARSE INDEX/pointer to neocortical activity; the rich content lives DISTRIBUTED in neocortex. Retrieval = the sparse index reactivates and reinstates the dense cortical ensemble. Explicit trade-off in the literature: "a SPARSER index is better for avoiding interference between memories" — i.e. the index is optimized for orthogonality/addressing, the value for fidelity of readout. These are DIFFERENT optimization targets carried by DIFFERENT representations.
2. **Complementary Learning Systems** (McClelland/McNaughton/O'Reilly 1995; Kumaran et al. 2016). Hippocampus = sparse, fast, pattern-separated; neocortex = dense, slow, overlapping. The two coexist and interact by design — a literal dense/sparse dual-representation architecture.
3. **Encoding-vs-retrieval REGIME-SWITCH gated at the substrate level** (Hasselmo SPEAR; Treves-Rolls). Distinct input regimes DOMINATE storage vs recall: mossy-fiber DG->CA3 ("detonator", sparse) dominates ENCODING; perforant-path + CA3 recurrent collaterals dominate RETRIEVAL — gated by acetylcholine (high ACh = encode, suppresses recurrent; low ACh = retrieve, restores recurrent) and separated across theta phase. The brain LITERALLY switches representational/dynamical regime between store and recall.

**Modern synthesis (load-bearing, recent):** "Key-value memory in the brain" (arXiv:2501.02950, 2025) argues the brain implements key-value memory in which KEYS and VALUES are DELIBERATELY DIFFERENT representations: keys are optimized for DISCRIMINATION (sparse, pattern-separated, low-interference addressing) and values for FIDELITY (dense content readout). This is the exact statement of our regime-switch: the sparse 2% code is the KEY (addressing + bind/unbind algebra = hippocampal relational binding); the dense BGE-derived readout is the VALUE (cosine retrieval). Optimizing one representation to do both jobs is fighting the biology.

---

## Prior-work reconciliation (substrate KB)

- **`exp_substrate_two_codebook_sparse_storage_dense_compose_v1` -> verdict READOUT_DEGENERATE (run_mode=full).** This IS a prior regime-switch attempt (sparse storage / dense compose). BUT the verdict_msg is explicit: "two-codebook architecture NOT evaluated; needs recalibration; raw_bpc near vocab entropy." This is a MISCALIBRATED / INCONCLUSIVE cell (the dense readout came out degenerate so the arm could not be assessed), NOT a clean falsification of the concept. Crucially, it tried to COMPOSE/decode a dense readout — which the brain says is the WRONG operation. The brain LINKS a stored dense value to the sparse key (reinstatement), it does not reconstruct content from the index. The prior failure INFORMS the fix; it does not close the direction. (Note: that cell was in the LM/bpc predict-next-token regime, not the retrieval@2%-sparse regime the current target lives in.)
- **`research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md`** — CA3 cue-clamped attractor drill. Relevant boundary: that drill's H2 called theta/ACh modulation a "red herring" but ONLY for the WITHIN-retrieval multi-iter question. For THIS (encoding-vs-retrieval REGIME) question, the theta/ACh encoding-retrieval SWITCH is exactly on-point — it is the biological regime-switch itself. Its cue-clamping finding also applies: the dense cue must be persistently available during the sparse settle (perforant path continuously drives CA3), so our dense query should clamp the sparse addressing step, not be discarded after step 1.
- **`research_to_exp_dev_DIMSPARSE2_sparse_substrate_state_2026-06-06.md`** — "retrieval is bottlenecked by KEY-COLLISION, not value-density." This is the sharpest constraint on the design: the sparse code's job in a regime-switch is to be a COLLISION-FREE index at the required item count; retrieval fidelity then rides on the dense value store, NOT on the sparse code's own reconstruction ability. Matches indexing theory's "sparser index = less interference."

---

## Design implication (concrete)

**Ship the regime-switch, but wire it as LINK-not-RECONSTRUCT (biological reinstatement), not as compose-dense-from-sparse.**

- STORE: sparse 2% bipolar code as the KEY. Do bind/unbind SBC algebra ON THE KEY (this is hippocampal relational binding — the sparse code is the right substrate for orthogonal, low-interference binding).
- ALONGSIDE each key, store the DENSE readout vector as the linked VALUE (the annealed encoder's dense embedding that already retrieves at 0.65 — the neocortical content).
- RETRIEVE: (1) address by pattern-completing / cleaning the query in the SPARSE key space (cue-clamped attractor per the CA3 drill so the dense query keeps driving the settle), (2) return the LINKED dense value, (3) do cosine retrieval in the DENSE space. Sparse code never has to reconstruct content; it only has to ADDRESS uniquely.
- This decouples the two objectives that were fighting inside one code: sparse handles ALGEBRA + collision-free ADDRESSING; dense handles high-fidelity COSINE READOUT. The USER's "should be EASIER" is brain-confirmed — you stop asking the 2% code to do a job the brain assigns to a separate dense system.

**The one real open risk (what would drop P):** does the sparse-key -> dense-value LINK survive the bind/unbind algebra? If you bind position/role onto the sparse key, you must still recover the correct dense value after unbind. The brain's binding (hippocampal, on the index) and content reinstatement (cortical, separate store) are architecturally separate, so this is coherent in principle — but our implementation must preserve the (key -> value) association THROUGH the algebra. Smoke that specifically: bind N items, unbind, verify the recovered dense value still retrieves >= 0.35 cosine. Second risk: key-collision at the target item count (DIMSPARSE2) — set sparsity for collision-avoidance, verify at full N per the batch/N-ratio rule.

---

## Calibration

- **Mechanism brain-grounded:** ~certain (indexing theory + CLS + key-value-in-brain are convergent and textbook). This part is not the uncertainty.
- **P_deflated that regime-switch (link-not-reconstruct) is the RIGHT ANSWER for retrieval >= 0.35 @ 2% sparse + algebra + cosine = 0.50.** Raw ~0.70 (dense readout component ALREADY works at 0.65; architecture is canonical biology; prior "failure" was a miscalibrated compose-attempt that the brain framework says was wired wrong), deflated 0.20 for: (i) one prior degenerate attempt on this exact direction, (ii) the UNVALIDATED link-survival-through-algebra risk, (iii) novel-synthesis for our pipeline. Capped at 0.50 (novel-synthesis cap engaged; the number rides on the untested link-through-algebra step, not on the well-grounded mechanism).

---

## Citations

External (verified via WebSearch this cycle + inherited-verified from CA3 drill):
1. Teyler & Rudy (2007) "The hippocampal indexing theory and episodic memory: updating the index." Hippocampus. (indexing theory; sparse index -> dense neocortical reinstatement; sparser index = less interference)
2. Goode, Tanaka et al. / "An Integrated Index: Engrams, Place Cells, and Hippocampal Memory" (2020) Neuron PMC7486247.
3. Gershman et al. (2025) "Key-value memory in the brain." arXiv:2501.02950. (LOAD-BEARING: keys optimized for discrimination / sparse addressing, values for fidelity / dense readout = the regime-switch principle)
4. McClelland, McNaughton, O'Reilly (1995) Complementary Learning Systems; Kumaran, Hassabis, McClelland (2016) update.
5. Neunuebel & Knierim (2014) "CA3 retrieves coherent representations from degraded input." Neuron. (CA3 pattern completion; change < input change)
6. Hasselmo (2013) encoding-vs-retrieval scheduling by theta phase + ACh; Treves & Rolls (1994) DG/CA3 storage-vs-retrieval pathway asymmetry. (the biological regime-switch)
7. "Dentate gyrus circuits for encoding, retrieval and discrimination" PMC7115869; Rolls (2015) pattern separation/completion.

Substrate-internal:
- `data/exp_substrate_two_codebook_sparse_storage_dense_compose_v1/metrics.json` (READOUT_DEGENERATE = inconclusive/miscalibrated compose-attempt, not falsification)
- `notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md` (cue-clamped CA3; theta/ACh regime boundary)
- `notes/research_to_exp_dev_DIMSPARSE2_sparse_substrate_state_2026-06-06.md` (key-collision is the retrieval bottleneck, not value-density)

Sources (web): [Teyler & Rudy indexing theory (PubMed)](https://pubmed.ncbi.nlm.nih.gov/17696170/) · [An Integrated Index (PMC7486247)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7486247/) · [Key-value memory in the brain (arXiv:2501.02950)](https://arxiv.org/pdf/2501.02950) · [DG circuits encoding/retrieval (PMC7115869)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7115869/) · [Pattern completion/separation mechanisms (PMC3812781)](https://ncbi.nlm.nih.gov/pmc/articles/PMC3812781)
