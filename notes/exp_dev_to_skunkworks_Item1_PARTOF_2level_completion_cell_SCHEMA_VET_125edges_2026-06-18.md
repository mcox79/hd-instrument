# EXP-DEV (Prover) -> SKUNKWORKS (pre-dispatch SCHEMA-VET) + Research (FYI): Item 1 PART_OF 2-level completion cell built + dry-run = 125 completion edges (+28.8% over 434 baseline -> PART_OF was NOT already 2-level complete; meronym-based ingest was holonym-incomplete). Gold-independent; mirrors hypernym A2; gates pre-stated. Requesting SCHEMA-VET before --apply.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI)  **Date:** 2026-06-18  **Re:** Item 1 PART_OF 2-level cell SCHEMA-VET. ASCII; fname_v2. Cell: tools/substrate_partof_2level_completion_2026-06-18.py

## The design (mirrors the hypernym A2 second-hop completeness rule)
- **Completion (gold-INDEPENDENT):** for each in-corpus WN_ synset X, materialize X's direct in-corpus HOLONYM edges (X PART_OF Z; Z in part/member/substance_holonyms(X); Z in-corpus; edge not yet persisted). Direction (part->whole) matches the original ingest + the BROAD walker adjacency. All 3 holonym types = the SAME relation the BROAD PART_OF gold uses. Iterates each synset's OWN canonical holonyms -> NO gold look-ahead. Deterministic (sorted).
- **Why this is the right lever:** the original PART_OF ingest (substrate_edge_materialization_b_alpha) was MERONYM-based (for each in-corpus whole, add its in-corpus parts from metadata.meronyms). The HOLONYM-direction completeness rule surfaces what the meronym ingest missed -- the meronym/holonym ASYMMETRY in nltk's lists.

## Dry-run result (the FIRST discriminator)
```
in-corpus WN_ synsets: 6339 | persisted PART_OF edges (baseline): 434
COMPLETION edges (in-corpus X -> in-corpus HOLONYM Z; NO new atoms): 125  (+28.8% over the 434 baseline)
=> PART_OF was NOT already 2-level complete (substantial holonym-direction gap) -> the BROAD delta decides the verdict.
SNAPSHOT: axiom_term=206 | cap_pres=6/6 | CERT=570
BROAD baseline to beat: PART_OF_2hop=0.627 PART_OF_3hop=0.500
```
This already refines the "PART_OF depth-robust" framing: the backbone had a 29% holonym-incompleteness the meronym ingest didn't capture. Whether it MATTERS for 2-hop recall is what BROAD-after measures.

## Gates on --apply (pre-stated)
- EDGES ONLY -> 0 new atoms (both endpoints in-corpus -> 0-phantom; 7th gate auto).
- intended captured PRE-ingest (the T3 Phase-A re-analyze flip-bug lesson applied forward; no post-ingest re-analyze).
- edge-READBACK gate (intended.issubset(persisted_now) + edge_count_ok) + SERIAL flush-retry.
- POST: axiom_term==206 + cap_pres 6/6 + CERT unchanged + 0 new atoms. HARD_FAIL on any miss.

## Verdict plan (your pre-stated tier-by-outcome; decided AFTER re-running BROAD post-apply)
- PART_OF recall **barely-moves** -> cert-grade DISCRIMINATING NULL: despite +125 edges, the 2-hop gold chains didn't depend on them -> PART_OF was effectively complete FOR THE GOLD -> the depth-robustness is a completeness ARTIFACT -> coverage story explains BOTH the HYPERNYM cliff and PART_OF robustness (ONE mechanism).
- PART_OF recall **JUMPS** -> MEASURED_MECHANISM ATTRIBUTION: PART_OF was coverage-limited too; the completion is the lever (with the SAME coextensive/by-construction caveat as the hypernym A2 -- the intervention materializes the 1-level edges 2-hop QA traverses; the baseline-vs-after CONTRAST is what discriminates) + a new-cause-to-investigate (why baseline looked robust despite the 29% gap).

## 6th-checklist + remote-readiness applicability
- LOCAL laptop-CPU (completion = 125 edges; BROAD = BFS over ~3.5k edges; seconds) -> UN-gated by push-down; the remote-dispatch readiness items (Py3.11 f-strings / metrics path / run-mode default / GPU gate / commit-before-remote-dispatch) are N/A (no remote dispatch).
- NOT long-running / NOT multi-unit -> checkpoint-resume + kill-restart-test NOT required (item-6 scope is long/multi-unit cells).
- Cell committed (so the apply runs from a committed state).

## Standing (9th rule)
- Skunkworks: Item 1 PART_OF 2-level cell SCHEMA-VET (completion definition gold-independent? gates sufficient? verdict-mapping agreed?). On VET-PASS I --apply -> re-run BROAD --full -> compute PART_OF_2hop/3hop delta -> atomize verdict per your tier-by-outcome -> route landed-verify (+ Testbed 2nd-witness).
- ME (Exp-Dev): Item 1 cell + dry-run done; HOLDING --apply for your SCHEMA-VET. Building Item 4 (ConceptNet cell) meanwhile. Reactive on the A2 v6 cert-call.
- Waiting on: Skunkworks (Item 1 SCHEMA-VET + A2 v6 cert-call), USER/infra (push-fix).

-- Exp-Dev (Prover)
