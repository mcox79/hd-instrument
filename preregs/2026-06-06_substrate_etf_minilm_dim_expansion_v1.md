# Prereg: substrate_etf_minilm_dim_expansion_v1
## Anchor
substrate_etf_minilm_dim_expansion_v1
## Routing
GPU follow-on to Slot 9 (MIDDLE 2.75x): does dimensional expansion recover ETF capacity headroom for real encoders? D-sweep {384,1024,4096}, raw vs whitened. GPU $0.
## Bands
HARD-PASS whitened cap scales >=3x from D384 to D4096. MIDDLE 1.5-3x. Smoke ~2.67x (D1024 censored) -> expansion scales ~linearly with D.
## Queue
overnight_queue 14400s.
