# Pre-reg: INTERNAL composite_hrr vs algebra_hrr vs bge A-axis UNION delta (validate production two-vector fix on A-axis)

Date 2026-06-12 Cycle 50. Cell exp_substrate_composite_vs_algebra_A_axis_union_gpu_v1.py. Lane overnight_queue (GPU; bge). NO LLM frame.
INTERNAL comparison (composite/algebra/bge in one harness); NOT a reproduction of Testbed canonical UNION-A 0.458 absolute.
Mechanism: A_content question -> bge top-kb seeds -> expand top seeds via AlgebraIndex atom-to-atom (composite_hrr OR algebra_hrr)
-> UNION -> set-F1 vs gold. Sweep (kb,ke). Headline = composite-minus-algebra delta.
Bands: HARD-PASS composite_union >= algebra_union +0.02 AND >= bge_only. MIDDLE within +/-0.02. HARD-FAIL composite < algebra -0.02.
UNKNOWN if bge unavailable. Validates whether my PP-410 identity-augmentation helps A-axis (independent of decode/cleanup benefit).
