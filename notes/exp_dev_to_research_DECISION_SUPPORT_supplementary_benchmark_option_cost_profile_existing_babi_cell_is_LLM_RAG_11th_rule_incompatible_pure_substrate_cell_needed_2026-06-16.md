# Exp-Dev (Prover) -> Research (Director): DECISION-SUPPORT for the post-Phase-B "supplementary-benchmark tail" option (read-only investigation while standing; NO run requested). Material finding: the existing bAbI substrate cell is a bge+Qwen RAG pipeline -> 11th-rule-INCOMPATIBLE for validating the substrate-internal cardinality capability; a NEW pure-substrate cell would be needed. Steinert-Threlkeld quantifier data not local. This changes the cost profile of that queued option. Intel only -- you prioritize. 218th honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_SUPPORT_supplementary_benchmark_option_cost_profile_existing_babi_cell_is_LLM_RAG_11th_rule_incompatible

## Why this note (14th-rule bounded prep, not a run)
At the Phase-B phase boundary, standing for your next-phase direction. Rather than idle, I ran a read-only
investigation of the one queued option whose cost I was unsure of -- the supplementary-benchmark tail (bAbI-7
counting + Steinert-Threlkeld quantifiers, which I floated to externally-validate the ARM-1 cardinality/quantifier
capabilities). Finding materially changes its cost. NO compute run; intel for your prioritization only.

## Finding: the option is HIGHER-cost than I implied (11th-rule constraint)
```
  bAbI data: fetchable via HF datasets (RMT-team/babilong; network fetch, not local). OK.
  BUT the existing cell experiments/exp_babilong_qa1_substrate_v1.py is a bge+Qwen2.5-1.5B RAG pipeline
     (bare-LLM vs bge-RAG vs whiten+top-k). That is an LLM-in-the-loop retrieval benchmark -- it does NOT
     exercise the substrate-internal cardinality capability, and reusing it would VIOLATE the 11th rule
     (substrate-internal, no LLM) for THIS purpose.
  => To validate the Phase-B cardinality capability (cleanup_distinct_count / CAP_exact_count / CAP_quantifier_most)
     on bAbI-7 (counting) under the 11th rule, a NEW PURE-SUBSTRATE cell is required: encode the story as
     role-filler bindings -> bundle the entities -> apply cleanup_distinct_count -> read the count/quantifier.
     No LLM, no bge. Medium design cost (new encoder + the readout already exists as the ratified operator).
  Steinert-Threlkeld quantifier benchmark data: NOT present locally; would need sourcing. Similar pure-substrate
     cell pattern for CAP_quantifier_most.
  22nd-rule firewall: these are EXTERNAL benchmarks (NOT the held-out gold q54-q65 / 56d), so firewall-compatible
     as long as no benchmark item is ingested into the corpus. OK.
  GPU-batched infra: EXISTS + reusable (experiments/exp_*_gpu_v1.py + tools/gen_gpu_batch_*.py); the pure-substrate
     bAbI-7 encode+count is GPU-perfect (batched role-filler binds + bundle + cleanup matmul).
```

## Honest implication for prioritization
- The supplementary-benchmark tail is a GENUINE external-validation of the Phase-B capabilities (would test
  whether cleanup_distinct_count transfers to an established counting task) -- but it is a NEW pure-substrate
  cell-build (not a quick reuse), gated on 11th-rule purity. Medium cost, real value, GPU-batchable.
- vs the other queued options: bilateral-kappa re-measurement (Skunkworks-lane, pre-stageable, lighter) and the
  ARM-3 principled-gap construction (needs a structural no-gerrymander criterion designed first). Phase-C tier-3
  is USER-gated.
- I have NO preference to push; this is cost intel so you can sequence the post-Phase-B work. I execute whichever
  you GO (heavy -> remote GPU-batched per USER policy; the GPU has been idle ~1300 min and is ready).

## Status / who I'm waiting on (9th rule)
- WAITING ON **Research (Director)**: post-Phase-B next-phase direction (now with sharper cost intel on the
  benchmark option).
- WAITING ON **Testbed**: ARM-3 dual-label finding record file (mechanical; Auditor+Prover endorsed) -> Phase-B
  fully closed.
- USER: architectural decisions (formal-oracle kappa; Phase-C tier-3 timing), no urgency.
- MY active work: COMPLETE; this was read-only decision-support prep. Ready to execute any GO'd next-phase option.
-- Exp-Dev (Prover)
