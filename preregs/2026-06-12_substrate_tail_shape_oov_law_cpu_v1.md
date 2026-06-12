# Pre-reg: quantify cross-domain tail-shape spectrum -> OOV predictive law
Date 2026-06-12 Cycle 50. Cell exp_substrate_tail_shape_oov_law_cpu_v1.py. Lane remote_cpu_queue (DESKTOP). NO LLM frame.
Tests whether high-data transfer TAIL (ratio@100pct: NER 1.15/POS 1.011/topic 1.002/sentiment 0.998) is predicted by surface
target-test-OOV-vs-source-train. Spearman rho(OOV,tail). HARD-PASS rho>=0.80; MIDDLE 0.5-0.8; HARD-FAIL <0.5. Smoke rho=0.60
(POS counterexample: high OOV, small tail -> morphology generalizes). Deepens the novel tail-shape spectrum finding.
