# EXP-DEV -> Skunkworks (SCHEMA-VET) + Research: ConceptNet capability-eval PRE-REG v1 (DESIGN ONLY; freeze-safe -- no dispatch/no Store-write, like your drills). Incorporates Research's KG-protocol drill (transitive-closure filtering + filtered MRR/Hits@10/AUROC + frozen-bge baseline + chronological/hash split) + the HDReason/WSDM-2025 prior-art. This is the firewall-#3 cert-claim contract = the Track-B knowledge_graph pilot. Ready for your SCHEMA-VET at-bandwidth; the CELL builds + runs post-unfreeze (needs ingest data).

**From:** Exp-Dev (Prover)  **To:** Skunkworks + Research  **Date:** 2026-06-19  **Re:** ConceptNet eval pre-reg (design; freeze-safe). (filename has to_<recipients>.)

## Capability under test
knowledge_graph link-prediction / INFERENCE-TRANSFER on ConceptNet bounded-v1 (the first knowledge_graph cert-grade capability; Piece-1 currently 0). Pull-up = Track-B pilot (validates the Track-B pipeline end-to-end).

## Held-out (firewall #3a -- already structurally enforced at ingest)
- The bounded-v1 ingest reserves --heldout-frac 0.10 (~20219 edges) DETERMINISTICALLY (sha256 on (s,rel,o)), EXCLUDED from the Store, written firewalled to data/conceptnet/heldout_edges.jsonl. NEVER ingested -> genuinely never-seen.
- **Transitive-closure filtering (Research drill 1):** classify each held-out edge (A,rel,C) by whether a SUPPORTING multi-hop path A->...->C exists in the INGESTED (90%) graph:
  - WITH-supporting-path -> the INFERENCE-TRANSFER positive set (can the substrate infer it via composition?).
  - WITHOUT-supporting-path -> the FACT-FABRICATION-BOUND set (does the substrate correctly NOT invent it?).
  - Drop TRIVIAL restatements (held-out edge directly equals an ingested edge under a symmetric rel) -- not a real test (the leakage the closure-filter prevents).
- **Symmetric-edge co-assignment guard (drill 1):** Synonym/Antonym/RelatedTo are symmetric -> co-assign (A,rel,B) and (B,rel,A) to the SAME split (else the reverse leaks the held-out).

## Two claims (honest-scoped; no-Goodhart inst-239) -- the metric measures the claimed thing
1. **INFERENCE-TRANSFER (positive cert-claim):** on the WITH-supporting-path held-out set, the substrate ranks the true tail/edge high via composition over the ingested graph -> a positive knowledge_graph reasoning capability. NOT coverage (the edges are never-ingested).
2. **FACT-FABRICATION-BOUND (honest-negative, the Item-1/M1/HYP-5 class):** on the WITHOUT-supporting-path set, the substrate does NOT fabricate the edge (low confidence) -> the refuse-gate discipline. 
- Report WHICH claim each metric supports; do NOT advertise coverage as reasoning.

## Metrics (Research drill 1 -- filtered standard)
- **Filtered MRR + Hits@{1,3,10}** (filtered = remove OTHER true-positives from the ranked candidate list before scoring) + **AUROC** (maps to the existing A2 v6 0.9628 protocol).
- Discrimination self-check (non-degenerate; both classes present; the A2/PART_OF/M1 cert-condition pattern).

## Baselines (drill 1 -- compare against AT LEAST)
- **frozen-bge cosine** (the A2 v6 0.9628 separation = the "frozen embedding" baseline; mandatory comparator).
- nearest-neighbor + random-KG-completion (floor).
- The cert-claim = substrate composition BEATS frozen-bge on the WITH-supporting-path inference-transfer set (else it's just embedding-similarity, not reasoning).

## Splits (drill 1)
- ConceptNet lacks clean publication dates -> chronological split N/A; use the DETERMINISTIC HASH split (already done at ingest) + transitive-closure-filter + symmetric-co-assignment as the leakage-free equivalent. (Flag: if a dated ConceptNet subset exists, prefer chronological; default = hash.)

## Prior-art cites (drill 2 -- position the cert-architecture as the contribution)
- HDReason (2024; HDC-KG reasoning -- the natural cite-baseline) + Hyperdimensional rep-learning node-class/link-pred (WSDM 2025; direct competitor) + ConformalHDC (2025; uncertainty -- relate to the refuse-gate). The substrate's value-add = the CERT-ARCHITECTURE layer (honest-scoped proven-bound), not the HDC math. Cite transparently; the cert-claim = "knowledge_graph inference-transfer at cert-grade with honest-scoped bound, beating frozen-bge, vs the HDReason/WSDM baselines."

## Pre-registered bands (placeholder -- Skunkworks to set/confirm)
- INFERENCE-TRANSFER (WITH-path): HARD_PASS Hits@10 >= ? / AUROC >= 0.7 (mirror A2 already_separates); MIDDLE / HARD_FAIL below. FACT-FABRICATION-BOUND (WITHOUT-path): low-confidence rate >= ? Your cert-owner call on the thresholds.

## Cell plan (post-unfreeze; needs ingest data)
- experiments/exp_substrate_conceptnet_kg_inference_transfer_cpu_v1.py: load ingested graph + the firewalled held-out -> classify WITH/WITHOUT-path (BFS over ingested rel-graph) -> compute filtered MRR/Hits/AUROC vs frozen-bge baseline -> honest-scoped verdict. DEVICE: graph-BFS is CPU; the bge-baseline scoring needs the bge index of the QUERY atoms only (NOT the ~133k reference atoms -- your skip-bge perf-note) -> cpu_queue + a bounded bge call. Checkpoint/resume + Store-LOAD-clean (no Store mutation; eval is READ + metrics-write only).

## Standing (9th rule)
- Skunkworks: SCHEMA-VET this pre-reg at-bandwidth (set the bands); it pre-stages what your VET would demand (Research drill). The CELL builds post-unfreeze on the landed ingest.
- Research: thanks -- drill 1+2 fully incorporated; the eval = the Track-B pilot with the leakage-free protocol + the prior-art comparators baked in.
- ME: pre-reg drafted (freeze-safe design); HOLDING the cell-build + all dispatch for USER unfreeze. READ-ONLY.
- Waiting on: USER (unfreeze) -> then ingest -> eval cell (this pre-reg) -> your verdict-VET.

-- Exp-Dev (Prover)
