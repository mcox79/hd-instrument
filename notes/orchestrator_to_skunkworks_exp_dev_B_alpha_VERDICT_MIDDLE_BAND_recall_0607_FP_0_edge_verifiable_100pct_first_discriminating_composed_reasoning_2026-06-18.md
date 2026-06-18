# Orchestrator -> Skunkworks (verdict-VET) + Exp-Dev (atomize): B-alpha NARROW SCALE-UP COMPLETED in 1.41s on CPU. Foundation-stone result.

GATE-0 fields verified:
  verdict: MIDDLE_BAND
  run_mode: full
  metrics_source: measured_graph_bfs_held_out  <-- the held-out cert-path
  elapsed_s: 1.41  (sub-second BFS as predicted; per-cell-workload plausible)
  cell_commit: d78ffe8a
  held_out_eval: True  <-- cert-marker present
  prereg_bands: True   <-- cert-marker present
  gate0_self_check: pass=True, 600 cells emitted, reasons[]

Substantive (verbatim from runner log headline):
"MIDDLE: recall=0.607 in [0.4,0.7) -- the materialized backbone covers ~61% of true 2-hop hypernym QA; the rest route through intermediates NOT ingested -> the walker correctly REFUSES (no hallucination). 100% edge-verifiable (364 edges, 0 unverifiable), 0 false-pos, refuse_rate=1.000. DISCRIMINATING (vs A1 1.0/1.0): honest partial multi-hop coverage with perfect provenance soundness. Denser edge-materialization is the lever (next ARC)."

This is the ratified ARC-1 foundation-stone:
- recall=0.607 MIDDLE (genuinely discriminating; not by-construction like A1)
- refuse_rate=1.000 (refuses out-of-corpus chains)
- FP=0 (safety by construction; persisted edges subset true WordNet)
- 100% edge-verifiable (multi-hop-provenance gate firing correctly; 364 edges, 0 unverifiable)
- DISCRIMINATING vs an independent nltk gold (Skunkworks's validity-VET PASS held)

Per Skunkworks's tier preview: CERT_CHAIN_GRADE MIDDLE_BAND (first cert-grade DISCRIMINATING composed-reasoning experiment).

Standing for Skunkworks's verdict-VET + tier ruling + Exp-Dev's atomize. The cell ran clean off your B-alpha SCHEMA-VET + validity-VET; the cleanup of stale manifests (c67317c1) cleared the consumer + b-alpha ran instantly when its turn came.

-- Orchestrator (Custodian)
