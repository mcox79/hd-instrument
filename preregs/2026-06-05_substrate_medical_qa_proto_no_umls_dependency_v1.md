# Prereg: substrate_medical_qa_proto_no_umls_dependency_v1
## Anchor
substrate_medical_qa_proto_no_umls_dependency_v1
## Routing
HP-5: medical Q&A proto (MedQA-USMLE) substrate-retrieval-aug vs Pythia-raw + deletion-cert on medical facts. GPU $0.
## Bands
HARD-PASS MedQA-aug>=1.5x Pythia AND deletion-cert. MIDDLE one. HARD-FAIL neither.
Smoke: deletion-cert 0.97->0.00 operational (medical wedge); MedQA aug 0.125/raw 0.175 below-random (Pythia-160M ceiling -> revisit Llama-1B) -> MIDDLE.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
