# Substrate latent-optimization levers audit (2026-07-13)

AUDIT-ONLY. Read-only sweep of the inductive map-builder stack for BUILT-BUT-UNUSED or
SILENTLY-DISCARDED capabilities that could raise magnitude / native-ceiling / cold-bucket
WITHOUT leaving the glass-box family (closed-form / VSA-native; no learned nets).

Prior-work check: substrate concept-query "latent unused discarded ... reciprocal cold rewire"
returned NONE relevant at cosine>0.30 (top hits were 2026-06 refuse-gate ferry notes, cosine
0.30-0.31, unrelated). This audit is genuinely novel relative to the KB; it is the DIRECT
continuation of the two prior wins named in the task:
  WIN-1 = fit_kge_anchor1 return_inverse (the DISCARDED inverse-relation block D[n_rel:2*n_rel])
          -> harvested by exp_anchor_compose_reciprocal_cold_rescue_cskg_v1 (21x cold lift).
  WIN-2 = unused DGProjection sparsifying front-end in the store.
Both were free discards. This audit finds the NEXT ones. The pattern is now explicit:
**every reciprocal-augmented fit trains an inverse block as a byproduct and throws it away.**

Files audited: hdlab/kg_traversal.py (KGStore), experiments/_kge_anchor1_fit.py,
experiments/_course_c_rotate_core_v1.py, experiments/_course_c_hake_core_v1.py,
hdlab/cleanup_family.py, plus caller map (Select-String over experiments/*.py).

Verdict language throughout: P_deflated = deflated success probability (not ambition).
FREE = a discard-expose / rewire (bit-identical default; the WIN-1 pattern). NEW-CELL = needs a run.

====================================================================================
RANKED CANDIDATES (7 found; 3 FREE-rewire, 4 NEW-CELL)
====================================================================================

------------------------------------------------------------------------------------
C1  [FREE-rewire, TOP]  fit_kge_rotate discards the trained INVERSE-PHASE block
------------------------------------------------------------------------------------
LATENT: _course_c_rotate_core_v1.py::fit_kge_rotate fits THETA over n_rel_eff=2*n_rel rows
  when reciprocal=True (default) -- rows [n_rel:2*n_rel] are the trained inverse-relation phase
  rotations (Lacroix reciprocal augmentation, identical construction to anchor1) -- then at
  return (line 332) SLICES THEM OFF: `return PHI.detach(), THETA.detach()[:n_rel]`. There is NO
  return_inverse flag on the rotate fit (anchor1 grew one for WIN-1; rotate never did).
WHY UNUSED: the forward readout (rotate_direct_scores) only does TAIL prediction (h,r,?); the
  inverse phases would answer HEAD queries (?,r,t) = rotate(X_t by -THETA_inv[r]) at zero new
  training (Kosko BAM: one learned association, either-direction recall). The cold-rescue that
  harvested WIN-1 uses ONLY the ADDITIVE fit's D_inverse; ONESHOT_ROTATE is present there merely
  as a memorize CONTROL -- so the rotation inverse block is fit and discarded in BOTH the map cell
  and the rescue cell. Rotation is the whole arc's thesis-better functional form than additive
  (RotatE>TransE on SYNONYM/IS_A); a rotation-geometry cold-rescue could beat the additive one.
LEVER: COLD bucket (0-tail-support entities currently BELOW random, anchor_mrr~4e-5 vs rand~5e-4).
GLASS-BOX: yes (phase rotation, VSA-native).
COST: FREE rewire -- add return_inverse=True -> 3-tuple (PHI, THETA[:n_rel], THETA[n_rel:2*n_rel]);
  bit-identical 2-tuple default for every existing caller. Exact WIN-1 additive-only-change pattern,
  already shipped once, verified. HARVEST needs one small cell = port the landed additive rescue to
  rotation geometry (add an ANCHOR_RECIP_ROTATE arm).
P_deflated (harvest): 0.40. Mechanism is PROVEN (additive rescue landed); rotation port is the
  lower-risk variety; but P is capped by the same graph-sparsity gate the additive cell hit (do
  cold entities actually HAVE head edges -- construction-fired gate).
CERT: SAFE. Touches experiments/ fit only; does NOT touch hdlab/kg_traversal.py -> no CERT-584/585
  surface.

------------------------------------------------------------------------------------
C2  [FREE-rewire]  fit_kge_hake discards BOTH inverse-phase AND inverse-MODULUS blocks
------------------------------------------------------------------------------------
LATENT: _course_c_hake_core_v1.py::fit_kge_hake (reciprocal=True default) trains THETA AND LMR
  (log-modulus) over 2*n_rel rows, then at return (lines 438-439) slices off BOTH inverse blocks:
  `THETA.detach()[:n_rel] ... LMR.detach()[:n_rel]`. The inverse PHASE and the inverse MODULUS are
  both fit-as-byproduct and both thrown away.
WHY UNUSED: same forward-tail-only readout. The MODULUS term is exactly the radial/hierarchy
  dimension (HAKE, Zhang 2020) that the additive and plain-rotate rescues LACK -- and CSKG's COLD
  population concentrates in the IS_A (1-to-N / hierarchical) stratum where modulus is designed to
  separate parent/child by scale instead of colliding on the unit circle. A bidirectional HAKE cold
  estimate rotates AND rescales X_t back to the held-out head. This is the single RICHEST cold lever
  because it adds the one dimension the two prior rescues cannot express.
LEVER: COLD bucket, specifically the IS_A/hierarchical cold entities.
GLASS-BOX: yes (phase + softplus modulus; closed-form).
COST: FREE rewire (same return_inverse pattern, but 5-tuple). HARVEST = new cell (HAKE bidirectional
  cold rescue), naturally a follow-up to C1's rescue cell.
P_deflated (harvest): 0.30. Higher ceiling than C1 on the IS_A stratum, but same graph-sparsity gate
  AND modulus can re-encode degree (the HAKE core already ships a g_modulus_no_leak guardrail -- must
  be carried into the rescue). Defer BEHIND the additive/rotate rescue verdict: if that HARD-FAILs on
  construction (cold entities lack usable edges either direction), HAKE cannot help either.
CERT: SAFE (experiments/ only).

------------------------------------------------------------------------------------
C3  [FREE-rewire, small]  hard_neg_frac / in-batch hard negatives are default-OFF and
    ABSENT from the primary (rotate) arm
------------------------------------------------------------------------------------
LATENT: fit_kge_anchor1 has a fully-built in-batch-hard-negative path (hard_neg_frac, lever B) gated
  OFF by default (0.0 == bit-identical). fit_kge_rotate and fit_kge_hake do NOT even have the
  parameter -> the PRIMARY arm of the whole map-builder cannot use hard negatives at all.
WHY UNUSED: added for reproducibility-preservation (default 0.0) and never swept; the rotate/hake
  fits were written without porting it.
LEVER: magnitude (MRR / hits@k) on the whole fair arena. Field precedent (MixKG, arXiv:2202.09606 /
  1902.10197): +0.01-0.04 MRR holding architecture fixed.
GLASS-BOX: yes (negative sampling only).
COST: port the param into fit_kge_rotate (free-ish, ~10 lines, same RNG-order-preserving guard) +
  a small hard_neg_frac sweep cell.
P_deflated: 0.30 for a measurable-but-modest lift; deflate because self-adversarial weighting already
  captures much of the hard-negative benefit -- the marginal gain from EXPLICIT hard negatives on top
  of adv_temp is the uncertain part.
CERT: SAFE (experiments/ only).

------------------------------------------------------------------------------------
C4  [NEW-CELL, TOP new-cell]  cleanup_family attractor/peel readout is UNWIRED from the
    map-builder score
------------------------------------------------------------------------------------
LATENT: hdlab/cleanup_family.py exposes CERT'd primitives -- modern_hopfield_continuous (exponential
  capacity), iterative_attractor (CA3/Treves-Rolls), peel_sic_readout (matching-pursuit, CG-certified
  to beat flat top-J at high load) -- and NONE are imported by the map-builder. The rotate/additive
  readouts (rotate_direct_scores / additive_direct_scores -> filtered_hits_from_scores) are ONE-SHOT
  argmax over raw inner products. No cleanup, no attractor iteration, no interference cancellation.
WHY UNUSED: the KGE readout was built as a plain score-and-rank; cleanup_family was built for the
  bundle/WM cells and never cross-wired. The query phase q = PHI_h + THETA_r is a NOISY estimate of
  PHI_t; an attractor step over the entity-phase codebook before argmax can pull a near-tie toward a
  true stored entity, and peel/SIC can resolve the multi-answer (1-to-N) tail set that argmax flattens.
LEVER: magnitude + native-ceiling on the whole arena (not just cold). Genuinely non-redundant with the
  in-flight reciprocal cold work.
GLASS-BOX: yes (Hopfield/attractor/matching-pursuit are all closed-form VSA primitives).
COST: NEW cell -- add a cleanup-readout arm on the rotate map score (swap the final argmax for an
  attractor-cleaned argmax; add a peel_sic arm for the 1-to-N tail strata).
P_deflated: 0.25. Deflated because KGE scores are ALREADY a global inner product against every entity;
  attractor cleanup mainly RERANKS near-ties rather than recovering a lost mode, so expected gain is
  concentrated in the mid stratum and 1-to-N relations. Honest MEDIUM, could-fail-informatively (if it
  doesn't move, that localizes the wall to the FIT, not the READOUT -- a first-class weak-point result).
CERT: CONDITIONAL. SAFE if wired onto the map-builder's rotate_direct_scores path (separate code).
  MUST NOT be wired into hdlab/kg_traversal.py KGStore.score_all / predict_one_hop / predict_n_hop --
  that IS the CERT-585 n8 chain-grade retrieval path (36.49x ratio, refuse=0.999) and CERT-584 FB15k
  ingest path; changing the argmax there would REGRESS both certs. Keep cleanup in the experiment
  readout, prove it, and only then consider a gated KGStore option behind a default-off flag.

------------------------------------------------------------------------------------
C5  [NEW-CELL]  FPE-median secondary readout is COMPUTED then only reported as diagnostic
------------------------------------------------------------------------------------
LATENT: _course_c_rotate_core_v1.py computes fpe_median_scores (bounded FPE kernel with the
  median-heuristic bandwidth fix for the ell=0.55 underflow) for ONESHOT + ORACLE every run, but the
  WIN verdict uses ONLY the direct readout; fpe_median is stored as fpe_median diagnostic and never
  fused into the decision.
WHY UNUSED: added as a "does the bandwidth fix beat the ell underflow?" diagnostic, not a readout.
LEVER: magnitude via rank-fusion (direct + FPE-median) at ZERO new training -- two independent views of
  the same fitted geometry.
GLASS-BOX: yes (FPE kernel is native).
COST: NEW cell (rank-fusion arm + verdict change).
P_deflated: 0.20. The two readouts are monotone-related to the same phases, so fusion gain is limited;
  deflate. Cheap to test because the second view is already materialized.
CERT: SAFE (experiments/ only).

------------------------------------------------------------------------------------
C6  [NEW-CELL]  bidirectional (HEAD-direction) forward readout across ALL entities, not just cold
------------------------------------------------------------------------------------
LATENT: reciprocal augmentation trains a usable inverse operator for EVERY relation, but the map-builder
  only ever queries tails (h,r,?). Head queries (?,r,t) are answerable at zero cost for all entities via
  the C1/C2 inverse blocks (Kosko BAM). This DOUBLES the queryable relational surface, independent of the
  cold bucket.
WHY UNUSED: readout was scoped to tail prediction to match the FB15k/n8 eval convention.
LEVER: native-ceiling (broader relational coverage) + a fairness/weak-point instrument (head-vs-tail
  asymmetry localizes where the fit is directional).
GLASS-BOX: yes. COST: NEW cell (depends on C1/C2 rewire). P_deflated: 0.35 as a coverage/measurement win
  (it MEASURES a capability that provably exists), lower as a headline magnitude win.
CERT: SAFE (experiments/); overlaps C1/C2.

------------------------------------------------------------------------------------
C7  [NEW-CELL, CERT-GATED]  KGStore.W Hebbian retrieval has no cleanup + init_entities path
------------------------------------------------------------------------------------
LATENT: hdlab/kg_traversal.py::KGStore.score_all returns raw E @ (W @ key); predict_n_hop iterates
  argmax with NO cleanup between hops (docstring already flags multi-hop K=3,4 as MIDDLE_BAND). An
  attractor cleanup between hops is the textbook fix for iterated-retrieval noise accumulation.
WHY UNUSED: KGStore is the frozen CERT-585 primitive; nobody touches it.
LEVER: cold/native-ceiling for n-hop (K>=3) chain traversal.
GLASS-BOX: yes.
COST: NEW cell.
P_deflated: 0.25.
CERT: **HIGH REGRESSION RISK -- this IS the CERT-585 path.** Do NOT edit KGStore in place. Any n-hop
  cleanup must be prototyped in a SEPARATE experiment subclass/copy, proven, and only landed behind a
  default-off flag that leaves predict_one_hop / predict_n_hop / refuse_gate_calibrate bit-identical when
  unset. Flagged here as a candidate, NOT a green-light.

====================================================================================
SUMMARY / RANK
====================================================================================
FREE-rewire (discard-expose, bit-identical default, WIN-1 pattern, all CERT-SAFE):
  1. C1  rotate return_inverse           -> COLD    (top free; enables rotation cold-rescue)
  2. C2  hake return_inverse (+modulus)  -> COLD/IS_A (richest cold dim; defer behind additive verdict)
  3. C3  hard_neg_frac port to rotate    -> magnitude (small, modest)
NEW-CELL:
  4. C4  cleanup/peel readout on rotate  -> magnitude/native-ceiling (top new-cell; non-redundant)
  5. C6  bidirectional head readout      -> coverage/native-ceiling
  6. C5  direct+FPE-median rank fusion   -> magnitude (cheap, limited)
  7. C7  n-hop inter-hop cleanup         -> n-hop cold (CERT-585 REGRESSION RISK; separate copy only)

CERT-584/585 REGRESSION FLAGS: C1/C2/C3/C4(experiment-path)/C5/C6 are all CERT-SAFE (they touch only
experiments/ fit + readout code, never hdlab/kg_traversal.py). C4-into-KGStore and C7 WOULD touch the
CERT-585 n8 retrieval path (score_all / predict_one_hop / predict_n_hop / refuse_gate_calibrate) and the
CERT-584 FB15k ingest path -> must be prototyped in a separate copy behind a default-off flag, never
in-place.

RECURRING STRUCTURAL FINDING (the meta-lever): reciprocal=True is the DEFAULT on all three fits
(anchor1 / rotate / hake) and EVERY ONE trains an inverse block then discards it unless a return_inverse
flag is threaded. WIN-1 fixed exactly one of the three (anchor1). C1 + C2 fix the other two. The
one-line audit rule going forward: **any reciprocal-augmented fit that returns [:n_rel] is leaving a
free trained inverse operator on the floor.**
