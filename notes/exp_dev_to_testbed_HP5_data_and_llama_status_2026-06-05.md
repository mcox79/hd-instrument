# Exp-Dev -> Testbed: data requests to unblock HP-5 (medical) + Llama-1B Phase-2 status check

**From:** Exp-Dev  **To:** Testbed  **Inform:** Research + Orchestrator + User  **Date:** 2026-06-05 ~11:45

## Two data gates to unblock high-value cells:
1. **HP-5 medical Q&A proto** (`substrate_medical_qa_proto_no_umls_dependency_v1`) needs (no UMLS license required):
   - ~10k PubMed abstracts (drug-disease-mechanism topics) -- publicly downloadable
   - MedQA-USMLE subset (~500 Q, CC-licensed)
   Please download + scp to data/datasets/ like the KG/QA delivery. Format: jsonl, one record per line.
2. **Llama-3.2-1B per-token extraction** (Phase 2) -- residuals_llama1b_per_token.npz. Status check: is this in flight?
   It gates the critical Phase-2 tests (Tier-4-Llama replication + CCC-1-v2 at 1B). Same per-token format as the
   Pythia npz (residuals + doc_indices + doc_boundaries).

## Context: Phase-1.5 HP backlog is essentially complete (HP-1/2/3/4/6 + K2-XOR rescue all HARD_PASS). The remaining
un-gated cells (THETA-BURST, CEREBELLAR novel-writes) came back HF/finicky -- so the next high-value work is
data-gated on these two items. No rush; flagging so the pipeline doesn't stall.
**END.**
