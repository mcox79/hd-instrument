# Pre-reg: Curry-Howard CHTV-1 substrate-as-verifier (CPU/local, no-heat)
Date 2026-06-12. Cell exp_substrate_curry_howard_type_checker_cpu_v1.py. Local file-IO + set membership (no torch/GPU). NO LLM.
Type-check derivation-chain witnesses over the typed structural-derivation graph (DEPENDS_ON/USES/INSTANCE_OF/SPECIALIZES/DEFINED_OVER/SHARES_MATH).
HARD-PASS CH-P1 well-typed-accept>=0.75 AND CH-P2 ill-typed-reject=1.0 (zero false-accepts). HARD-FAIL CH-P1<0.5 OR any false-accept.
Corpus note: DEPENDS_ON alone is depth-1 (0 depth-2 chains); used full structural-derivation graph (2595 real depth-2 chains).
