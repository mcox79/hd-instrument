# Prereg: substrate_mode5_hierarchical_compound_depth_v1_n512xD
## Anchor
substrate_mode5_hierarchical_compound_depth_v1_n512xD
## Routing
Mode5+Hierarchical compound (production arch): D parallel isolated substrates + controller routing + per-hop cleanup -> deep reasoning. CPU numpy $0.
## Bands
HARD-PASS K_compound>=50 AND >=2x single. MIDDLE K>=25 OR >=1.5x. HARD-FAIL else. Smoke (L=40): K_compound=40 (full chain) vs single=0 -> MIDDLE (L<50); full L=80 -> K>=50 HP expected.
## Queue
remote_cpu_queue timeout 14400s. PROT-022 PASS.
