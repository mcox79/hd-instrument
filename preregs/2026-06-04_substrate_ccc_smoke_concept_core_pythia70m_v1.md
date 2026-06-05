# Prereg: substrate_ccc_smoke_concept_core_pythia70m_v1
## Anchor
substrate_ccc_smoke_concept_core_pythia70m_v1
## Routing
CCC-smoke cognitive-core first gate (drill Sub-Q6). Pythia-70M inline encode -> VQ V_c=64 -> cf-RPE substrate
concept-transition write (context-bound keys) -> retrieval. torch+transformers GPU, $0. overnight_queue.
## Pre-registered bands
HARD-PASS >=70% transitions retrieved (cos>=0.7). MIDDLE 40-70%. HARD-FAIL <40%.
## Smoke gate (pipeline check)
Tiny config (N=1024,V_c=16): 30% (collision-limited; cf-RPE fixed raw-Hebbian 0%). Full mode V_c=64/N=4096 is the
actual drill gate (4x concepts + 4x N -> far fewer context collisions). diagnostic: concepts non-degenerate (16/16), ctx_conflict 0.14.
## Queue
overnight_queue timeout 14400s. PROT-022 self-tests PASS.
