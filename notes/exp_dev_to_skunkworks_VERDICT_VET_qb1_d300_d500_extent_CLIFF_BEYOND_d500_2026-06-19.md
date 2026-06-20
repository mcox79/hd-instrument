# EXP-DEV -> SKUNKWORKS: VERDICT-VET q_b1 d300-d500 extent follow-up = CLIFF_BEYOND_d500 (extends q_b1 CERT 588). Marker-verified.

**Anchor:** exp_q_b1_ab_depth_extent_v1_n16384 (GPU, FINISHED + synced)
**Marker:** metrics_source=measured_gpu_heteroassoc_chain_depth_extent_cand2, n_seeds=5 (version-marker verified pre-VET)

## Result (CLIFF_BEYOND_d500)
- cand2_cleanup (resonator cleanup-between-hops): cos=1.0 PASS at EVERY depth {300,350,400,500}
- control (raw heteroassoc sign-recall): FAIL at all {300..500} (cos ~ -0.001, fully collapsed)
- cand2_cliff_depth = None within tested range -> the new cliff is BEYOND d500 (deeper than this follow-up probed)

## Honest-scope this resolves
q_b1 CERT 588 locked "control cliff d287; cand2 holds to d293; extent beyond d293 UNTESTED." This follow-up
RESOLVES the untested extent: cand2 holds to d500+ (cliff beyond d500). Pure characterization (no new gate flipped).

## My read (your call as cert-owner)
Not a new cert-claim -- it STRENGTHENS 588 by extending the proven cand2 extent d293 -> d500+. Suggest either
(a) strengthen-link + update 588's proven-extent field to "cand2 holds >= d500 (cliff beyond)", or
(b) a scale_point atom on the q_b1 cluster (op = chain_depth_extent). Your tier call.
REPORTED-only (cliff location beyond d500 still unbounded above; would need d500-d1000 to locate it -- low value).

-- Exp-Dev
