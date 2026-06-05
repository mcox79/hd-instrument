# Prereg: substrate_multimodal_binding_text_kg_v1
## Anchor
substrate_multimodal_binding_text_kg_v1
## Routing
HP-9: multi-modal VSA binding (text<->KG modality-agnostic) + cross-modal evidence combine. CPU $0 (no faiss).
## Bands
HARD-PASS cross-modal recovery>=0.90 both directions AND combine>=single. MIDDLE>=0.70. HARD-FAIL<0.70.
Smoke: text->KG 1.0, KG->text 1.0, combine 1.0 -> HARD_PASS (modality-agnostic binding).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
