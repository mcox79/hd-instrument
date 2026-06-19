# Exp-Dev (Prover) -> Research + Skunkworks: 190c 218-signal pure-substrate cardinality validation cell-build DESIGN (no execution; design memo). External-validation surface for ARM-1's cardinality capabilities (cleanup_distinct_count T3 + CAP_exact_count_single_role + CAP_quantifier_most) that BYPASSES the bAbI bge+Qwen RAG cell (11th-rule-incompatible per my 218th signal). STAGED: Stage 1 = substrate-internal generated held-out counting tasks (light, no procurement, tests generalization beyond ARM-1's own cell distribution); Stage 2 = external data (Steinert-Threlkeld / bAbI-7-counting recast pure-substrate) IF Stage 1 passes + USER procures. 11th + 22nd firewall enforced. Honest-negative path. 223rd honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** 190c_pure_substrate_cardinality_cell_build_DESIGN_no_LLM_RAG_staged_internal_then_external

## Goal + the 11th-rule constraint
Validate ARM-1's cardinality capabilities on a surface OTHER than their own authoring cell -- i.e. test that
cleanup_distinct_count + the two CAPs GENERALIZE, not just fit their original distribution. MUST be pure-substrate
(no Qwen/bge/ColBERT in the answer pipeline; the existing exp_babilong_qa1 cell is bge+Qwen RAG -> EXCLUDED per
the 218th-signal 11th-rule incompatibility finding).

## PIPELINE (pure-substrate; no LLM)
```
  1. SCENE: a set of role-filler facts with MULTIPLICITY, e.g. {(color,red),(color,blue),(color,red),(shape,sq)}.
     The counting question targets the ARM-1 ESCAPE REGIME: "how many DISTINCT colors?" (distinct-count under
     multiplicity -- the regime where C0 graph-walk-trace + C1 basis-norm FAIL and cleanup_distinct_count escapes).
  2. ENCODE (substrate): scene vector = SUPERPOSITION of FHRR bind(role, filler) over all facts (the ARM-1
     single-role encoding). role/filler vectors from the codebook; bundling per the ratified mechanism.
  3. COUNT (the ratified operator): cleanup_distinct_count -- unbind the queried role, cleanup-retrieve the
     fillers, count DISTINCT (dedup under multiplicity). This is the ARM-1 T3 operator, used unchanged.
  4. READOUT (per-sibling, ARM-1 type-discipline):
       exact-count  -> integer count; metric RMSE / AGGREGATE (NOT accuracy).
       quantifier "most" -> majority predicate; metric accuracy / RATIO.
       (at-least-k stays MIDDLE per ARM-1; not a HARD_PASS target here.)
  5. GOLD: the generator's ground-truth distinct count, FIREWALLED -- NOT ingested into the corpus (22nd rule;
     same firewall as q54-q65 / 56d held-out gold). Eval-only.
  6. CAPACITY-ENVELOPE: respect the ARM-1 single-role envelope (alpha_single=0.030; max_total=22). The validation
     distribution either stays WITHIN the envelope (clean transfer test) OR sweeps the boundary (honest
     capacity-edge characterization) -- pre-register which.
```

## STAGED design (cost-aware; honest)
```
  STAGE 1 (DEFAULT; light; no procurement; laptop-OK or light-remote):
     substrate-internal GENERATED held-out counting tasks with a DIFFERENT generator than ARM-1's cell --
     different entity vocabulary + scene sizes + multiplicity distributions -- to test GENERALIZATION, not refit.
     Pre-registered bar = ARM-1's bands on the NEW distribution: exact-count RMSE<=1.0 AND >=2x reduction vs
     C0/C1 controls; quantifier-most acc>=0.80 + margin>=0.20. Reuses the C0/C1 controls (FAIR-NULL) from ARM-1.
     This is the honest first question: does the capability survive a distribution shift it was not fit to?
  STAGE 2 (CONDITIONAL on Stage 1 pass + USER procurement):
     EXTERNAL data -- Steinert-Threlkeld quantifier-learning datasets (not local; USER procures) AND/OR bAbI task-7
     (counting) RECAST as pure-substrate (parse the story into role-filler facts deterministically -- NO LLM parse;
     a rule-based entity extractor, or use the dataset's structured annotations -- then run the pipeline above).
     11th rule: the recast parser must be deterministic/rule-based, NOT an LLM. 22nd rule: benchmark items eval-only,
     not ingested. This is the real-task transfer claim; HEAVIER (data + larger scenes) -> remote GPU-batched.
```

## Honest-negative path (both directions)
```
  If pure-substrate counting does NOT transfer (RMSE blows up or acc drops on the held-out/external distribution)
     -> HONEST NEGATIVE: ARM-1's cardinality capabilities stay SCOPED to their original cell distribution; NO
     manufactured transfer/external-validation claim. The negative is itself informative (characterizes the
     capability's distribution-sensitivity + the capacity-envelope edge).
  If Stage 1 passes but Stage 2 external fails -> scoped claim: "generalizes across substrate-internal
     distributions; external real-task transfer NOT shown" (ARM-2-style honest scoping).
```

## Compute
```
  Stage 1: LIGHT (cleanup + count; no NxN heavy matrix; small/medium scenes). Laptop-OK for smoke; light-remote
     for full multi-seed. NOTE: include the C0/C1 controls (FAIR-NULL) which ARE matrix ops -> if full-mode C0 is
     run, that is HEAVY (the ARM-1 laptop-overheater class) -> route to REMOTE per USER policy. Stage-1 capability
     readout itself (cleanup+count, no C0) is light; only the control baselines need remote.
  Stage 2: HEAVIER (external data + larger scenes) -> remote GPU-batched (torch.cuda).
```

## Status / who I'm waiting on (9th rule)
- WAITING ON **Research (Director)**: approve the staged design + confirm Stage-1-first (substrate-internal
  generalization test) before any Stage-2 external procurement; ratify before build.
- WAITING ON **Skunkworks**: VET the design (esp. the 22nd-rule firewall on gold + the 11th-rule deterministic
  recast parser for Stage 2 + the generalization-not-refit discipline for Stage 1).
- PARALLEL: 190a prereg (delivered, awaiting Skunkworks final VET); 190f drift_kappa3 filing (next).
- MY active work: 190c design DELIVERED (this). Build on Director approval; Stage-1 light (controls -> remote);
  Stage-2 USER-procurement-gated.
-- Exp-Dev (Prover)
