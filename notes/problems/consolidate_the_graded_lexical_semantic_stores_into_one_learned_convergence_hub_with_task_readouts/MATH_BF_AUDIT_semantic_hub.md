# MATHEMATICAL BF AUDIT -- the convergence semantic hub, rung by rung (2026-09-13)

Owner ask: "make sure we're brain foundational, mathematically as well." Every mathematical operation in
`experiments/exp_semantic_hub_convergence_v1.py::ConsensusHub` enumerated with: the computation, the brain
computation it realizes, citation, and status. PINNED = brain's mechanism fixed, we copy it. COMPUTATIONAL-LEVEL
= implementation unpinned but a defensible published brain model. OUR-INVENTION = a labeled choice. PARAMETER =
a constraint we do not share, SWEPT never adopted.

| # | rung | computation | brain-exact realization | citation | status |
|---|---|---|---|---|---|
| 1 | per-spoke input norm | L2-normalize each spoke block | divisive normalization | Carandini-Heeger 2012 | BF |
| 2 | convergence layer | h = tanh(W.s + b), ALL spokes through ONE shared hidden layer | hub-and-spoke convergence principle; error-driven cortical learning of a shared deep layer | Rogers-McClelland 2004; Jackson-Rogers-Lambon Ralph 2021 | BF (op PINNED; tanh = COMPUTATIONAL-LEVEL sigmoidal unit) |
| 3 | reconstruction | s_hat = V.h + c, reproduce every spoke from the hub | auto-associative "reproduce every modality from every other" | Rogers-McClelland 2004 | BF (offline consolidation objective) |
| 4 | spoke-dropout denoising | zero whole spokes, reconstruct the CLEAN present spokes | partial-input training = missing-modality robustness + forces cross-spoke prediction; CA3 pattern completion | Vincent 2008 (denoising AE, comp-level); McClelland 1995 (completion) | BF_SPIRIT; dropout rate = PARAMETER (swept) |
| 5 | recon loss | spoke-balanced (1/dim) squared error over present dims | prediction-error minimization; per-modality error normalized so none dominates by dimensionality | error-driven learning; divisive norm | BF_SPIRIT; the 1/dim balance = OUR-INVENTION (labeled) |
| 6 | **consensus target** | **T_ij = mean over covering spokes of cos_k(i,j)** | optimal multi-cue integration -- reliability-weighted agreement across cues | Ma-Beck-Latham-Pouget 2006; Ernst-Banks 2002 | **DEVIATION (see below): EQUAL-weight mean is only optimal if all spokes have EQUAL precision. Ma-Pouget is INVERSE-VARIANCE weighted. -> FIX = precision-weighted consensus.** |
| 7 | similarity readout loss | (cos(u_i,u_j) - T_ij)^2 on unit-normed hub codes | representational-similarity learning: shape the hub's similarity geometry to a target RDM | Cox-Fernandino et al. 2024; Kriegeskorte RSA | BF_SPIRIT (comp-level) |
| 8 | cosine readout | u_i . u_j | population-vector readout | Georgopoulos 1986 | BF |
| 9 | online update | dW = eta_slow * error * input, SMALL lr, INTERLEAVED replay of old+new | CLS neocortical SLOW system; interleaving prevents catastrophic interference | McClelland-McNaughton-O'Reilly 1995; Kumaran 2016 | BF (PINNED comp-level); eta_slow = PARAMETER |
| 10 | asset between consolidations | checkpoint, re-consolidated online (NOT frozen) | neocortical weights change slowly + continuously, never frozen | CLS; owner 2026-09-13 | BF (plastic) |

## The one mathematical DEVIATION and its fix (rung 6)
- **As-built:** the consensus teacher weights every covering spoke EQUALLY: `T_ij = (1/K) Sum_k cos_k(i,j)`.
- **Brain-exact (Ma-Pouget / Ernst-Banks optimal cue integration):** cues combine by INVERSE VARIANCE (precision):
  `T_ij = Sum_k w_k cos_k(i,j) / Sum_k w_k`, `w_k = 1/sigma_k^2` = spoke k's precision (reliability). This is
  the SAME rule the landed `FusedSenseRanker` uses (earned-gain precision weighting) -- so equal-weighting is a
  mathematical INFIDELITY that also makes the hub inconsistent with the incumbent it must beat.
- **Precision, gold-free and available:** per-spoke reliability signals already exist -- DINOv2 exemplar count /
  inverse dispersion (visual), Lancaster rater SD -> `grounded_reliability` (grounded), token frequency / count
  (distributional, w2v), Warriner SD (valence). Where a per-word precision is not cached, a gold-free DATA-DRIVEN
  precision proxy is each spoke's agreement with the leave-one-out consensus of the others (a reliable cue is one
  whose signal is consistent with the rest -- inverse-variance estimated from the data itself).
- **FIX (implemented as the mathematically-BF PRIMARY; equal-weight kept as an ABLATION control):** precision-
  weighted consensus target. Test: does Ma-Pouget precision weighting beat equal weighting? (If yes, the brain's
  inverse-variance rule is load-bearing here; if no, report it -- either way it is now the faithful default.)

## Not a deviation (checked): converging spokes into ONE hub h does NOT violate the separate-pool /
double-dissociation principle. The separate-pool rule (Ma-Pouget; semantic-dementia x amnesia) governs the
READ-TIME fusion of the ATL hub vs the HIPPOCAMPAL episodic store (convergent_cue_reader) -- two DIFFERENT
memory systems. The modality SPOKES converging into the ONE amodal ATL hub is exactly Patterson-Rogers hub-and-
spoke; that IS one pool by design. So: spokes -> one hub (correct); hub vs hippocampus -> separate pools (correct,
and unchanged -- the hub becomes one of the pools the convergent_cue_reader/FusedSenseRanker weights at read).

## VERDICT
Every rung is BF or BF_SPIRIT once rung 6 is precision-weighted. Parameters (hub width, dropout, eta_slow,
sim_w) are SWEPT, never adopted. The convergence operation (2), the consolidation objective (3-4), the RSA
readout (7), and the online CLS update (9) are the brain's computations; the equal-weight consensus was the one
math infidelity and is replaced by Ma-Pouget inverse-variance weighting.
