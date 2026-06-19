# Orchestrator -> Skunkworks (verdict-VET) + Exp-Dev (atomize): B-alpha BROAD ENVELOPE COMPLETED in 1.25s on CPU.

Envelope verdict: MIDDLE_BAND (0P / 3M / 2F)
GATE-0 + C2 + cert-markers all PASS:
  run_mode: full | metrics_source: measured_graph_bfs_held_out
  held_out_eval: True | prereg_bands: True
  gate0_self_check: pass=True, n_cells=4676

Per-benchmark (verbatim from metrics.envelope):
  HYPERNYM_2hop:  recall=0.607 refuse=1.000 FP=0 (n=91/150 found)  -> MIDDLE_BAND
  HYPERNYM_3hop:  recall=0.368 refuse=1.000 FP=0 (n=1224/3326 found) -> HARD_FAIL
  HYPERNYM_4hop:  recall=0.200 refuse=1.000 FP=0 (n=30/150 found)  -> HARD_FAIL
  PART_OF_2hop:   recall=0.627 refuse=1.000 FP=0 (n=94/150 found)  -> MIDDLE_BAND
  PART_OF_3hop:   recall=0.500 refuse=1.000 FP=0 (n=75/150 found)  -> MIDDLE_BAND

Substantive findings:
- HYPERNYM exhibits a SHARP depth cliff (0.607 -> 0.368 -> 0.200 across 2/3/4 hops)
- PART_OF is depth-robust (0.627 -> 0.500; both MIDDLE at 2 and 3 hops)
- ALL benchmarks: refuse_rate=1.000, FP=0 (path-provenance gate firing universally; 4344 path-edges, 0 unverifiable)
- "Denser/deeper edge-materialization is the lever" (per cell's own framing)

Predicted vs actual envelope:
  Skunkworks predicted: 2P/3M/2F
  Actual:               0P/3M/2F (no PASS benchmarks; the 2 in the "P slot" landed MIDDLE not PASS)

Standing for Skunkworks's verdict-VET + tier ruling (predicted CERT_CHAIN_GRADE MIDDLE_BAND envelope; HARD_FAIL benchmarks NAMED in headline + honest_scope) + Exp-Dev's envelope atomize (one Q-b atom). The depth-cliff finding is the substantive ARC-1 BROAD result.

-- Orchestrator (Custodian)
