# Prereg: substrate_cognitive_core_architectural_advantage_v1
## Anchor
substrate_cognitive_core_architectural_advantage_v1
## Routing
CCC-1-v2 architectural-advantage trio (the decisive Phase-1 benchmarks): long-conversation memory, cross-session persistence, multi-doc synthesis. Substrate vs Pythia-160M. torch+transformers GPU $0.
## Bands
HARD-PASS all 3 (LONGCONV sub>=0.80 @d & Pythia<=0.30; CROSS-SESSION sub>=0.70 & Pythia<=0.10; MULTIDOC sub>=3x Pythia). MIDDLE 2/3. HARD-FAIL <2.
Smoke: LONGCONV 1.00/0.00, CROSS 1.00/0.00, MULTIDOC@300 1.00/0.08 -> HARD_PASS (substrate categorically wins).
## Queue
overnight_queue timeout 7200s. PROT-022 PASS.
