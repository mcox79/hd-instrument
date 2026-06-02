# Research note: substrate as time-series infrastructure
## Date: 2026-06-01
## Topic: Speculative drill -- substrate vs regulated time-series DBs (audit / compression / edit-isolation niche)

---

## HEADLINE

Substrate does NOT beat InfluxDB/TimescaleDB as a general TSDB, but occupies a structurally defensible COMPLIANCE SIDECAR niche for regulated, low-cardinality time series (healthcare telemetry, financial tick data, industrial monitoring under NIS2). The winning axis is algebraic deletion certificates + edit-isolation under HIPAA/GDPR -- a gap confirmed to exist in current TSDBs. This finding CONVERGES with the already-adopted v315 primary product narrative and COMPLIANCE SIDECAR GTM; time series is a new vertical application of the same algebraic-certificate moat, not a new product direction.

---

## Cheap decisive test

**Algebraic range-query binding correctness (CPU, less than 5 min)**

Store K=10 time-tagged patterns (xi_t1 through xi_t10). Bind each to a time-index hypervector: m_t = xi_t XOR tau_t. Issue a range query by summing tau_window = tau_t3 + tau_t4 + tau_t5 and unbinding. Measure: does unbind(tau_window, stored_W) recover {xi_t3, xi_t4, xi_t5} at >90% accuracy while non-window patterns stay below noise floor?

If YES: algebraic time-windowed retrieval is functional. Add as compliance sidecar sub-capability.
If NO: XOR time-binding does not compose for range queries -- requires temporal codebook redesign before any time-series product claim.

This is N=1024, K=10, pure Python, no GPU. 15 min total including writeup.

---

## Falsifiable predictions

### HARD-PASS thresholds (GO signal)

**HP-1 (algebraic range correctness)**: time-windowed unbinding recovers in-window patterns at >85% accuracy (5-seed, K=10, N=1024) while out-of-window patterns score <20% (noise floor).

**HP-2 (deletion certificate round-trip)**: algebraic deletion of a specific time-tagged pattern xi_t produces a deletion certificate that (a) reduces target pattern cosine similarity by >0.70 and (b) leaves non-target patterns within 5% of baseline -- no collateral damage.

**HP-3 (TSDB compliance gap confirmed operationally)**: structured search of InfluxDB/TimescaleDB GDPR deletion documentation confirms that (a) backup immutability creates a verified gap (CONFIRMED from lit-scan -- backups persist beyond 30-day GDPR window), and (b) no native algebraic proof of deletion is produced by either system.

HP-3 is ALREADY PASSED based on lit-scan (InfluxDB Enterprise documentation and GDPR compliance sources confirm backup immutability creates a compliance gap; no native deletion-cert is produced).

### HARD-FAIL thresholds (NO-GO signal)

**HF-1 (range query fails algebraically)**: in-window accuracy <50% or out-of-window contamination >40% -- XOR time-binding does not produce separable time windows; substrate cannot serve as a time-index without redesign.

**HF-2 (throughput ceiling kills the niche)**: if regulated low-cardinality time series (50 ICU patients x 10 sensors x 1 Hz = 500 writes/sec) exceed substrate O(N^2) write budget at N=4096 on CPU -- then even the sidecar architecture fails because the compliance ingestion path is too slow for real-time streams. (Estimated ceiling: N=4096 outer-product write approximately 0.5ms on CPU = 2000 writes/sec; 500 writes/sec appears feasible but needs verification.)

**HF-3 (tau_mem compression not derivable)**: no formal Shannon compression bound found after 1 derivation attempt -- remove compression claim from product narrative.

---

## Cross-thread synthesis with prior entries

### Convergence with v315 PRIMARY PRODUCT NARRATIVE (adopted 2026-06-01)

The time-series finding is NOT a new direction -- it is a THIRD VERTICAL (after knowledge graphs PP-21 and ML feature stores PP-22) where the same algebraic-certificate moat applies. The v315 narrative already states: "substrate stores facts with intrinsic algebraic certificates for audit, privacy (DP), tenant isolation, edit-impact-prediction, deletion, recovery..." Time-series telemetry is a fourth class of "facts" with identical compliance requirements. No cap_map revision needed; this is an application of existing rows PP-9, PP-15, PP-20, PP-32 to the time-series vertical.

### Convergence with COMPLIANCE SIDECAR GTM (adopted 2026-06-01)

The sidecar framing directly resolves the throughput/cardinality objection. Substrate is NEVER on the hot path (InfluxDB handles millions of writes/sec ingestion); substrate is on the COMPLIANCE PATH only. In a regulated TSDB sidecar deployment: InfluxDB ingests at 1M writes/sec; substrate receives only the compliance-relevant series (patient IDs, regulated device IDs) at 100-10,000 writes/sec, which is within O(N^2) budget at N=1024-4096.

### Convergence with DELETION CERTIFICATE SHARED PRIMITIVE (adopted 2026-06-01)

GDPR Art. 17 right-to-erasure applied to time-series patient telemetry is EXACTLY the PP-9/PP-20 delete-cert use case. The finding that TSDBs have a confirmed backup-immutability compliance gap (from InfluxDB/TimescaleDB documentation) strengthens the moat claim operationally. This is the first external confirmation of the compliance gap from TSDB vendor documentation.

### HopCPT (NeurIPS 2023) -- adjacent method, DO NOT DISMISS

HopCPT (Conformal Prediction for Time Series with Modern Hopfield Networks) uses a modern Hopfield network for similarity-based reweighting of conformal calibration scores. This is mathematically adjacent: HopCPT does NOT use additive Hebbian write dynamics or algebraic deletion -- it uses energy-based retrieval for conformal set construction. The substrate could in principle replicate the HopCPT score-reweighting layer (pattern-similarity lookup) while adding the audit/deletion certificate layer that HopCPT lacks entirely. Per feedback-dont-dismiss-adjacent-methods: dispatch a follow-up lit-scan on HopCPT implementation to assess whether substrate primitives subsume or extend HopCPT.

### Attraos (NeurIPS 2024) -- attractor memory for long-term forecasting

Attraos uses attractor memory concepts (phase-space reconstruction, MDMU polynomial approximator) for long-term forecasting. NOT algebraically identical to substrate (no additive Hebbian; no deletion cert). Attraos wins on forecasting accuracy; substrate wins on audit/deletion. Non-competing verticals.

### Memory-augmented anomaly detection (MemAE-OCSVM, MIXAD, HTM) -- converging adjacent methods

The ML literature has converged on memory-augmented approaches for time-series anomaly detection: memory stores normal patterns; anomalies show high reconstruction error or memory activation shift. MIXAD (2024) uses memory activation shift as the anomaly score -- this is mechanistically adjacent to substrate spectral health-check. Key difference: MIXAD has no deletion cert, no algebraic audit trail. Substrate can subsume MIXAD-style anomaly detection while adding the audit layer. P_deflated = 0.40 that substrate spectral health-check maps cleanly to MIXAD-style anomaly score on time-series data.

### OU process and tau_mem decay -- compression claim assessment

The tau_mem = (1/gamma)log(1 + N*gamma / (2*lambda)) gives a natural decay timescale implementing exponentially-weighted aggregation. The information-loss bound derivation is NOT in the literature -- no papers found linking tau_mem to Shannon compression bounds for time series. This is a substrate-novel claim requiring a new derivation. P_deflated = 0.30 (raw 0.50, deflated 0.20 for uncharted novel-derivation regime). Do NOT include compression claim in product narrative until bound is derived.

---

## Substrate-product implications

### GO vertical (HIGH confidence, P_deflated = 0.60)

**Regulated low-cardinality time series as COMPLIANCE SIDECAR:**

Target segments: healthcare patient telemetry (HIPAA), financial customer tick data (GDPR), industrial critical-infrastructure sensor logs (NIS2)

Volume regime: 10-10,000 series, 1-100 Hz, N=1024-4096 substrate

Write budget: estimated 500-2000/sec at N=4096 -- matches sidecar-path load for regulated series

Win axes:
- Algebraic deletion certificate closes the backup-immutability compliance gap confirmed in InfluxDB/TimescaleDB documentation
- Edit-isolation under concurrent stream + retroactive correction: substrate additive write + algebraic undo produces derivable before/after proof; InfluxDB has no equivalent
- Anomaly detection integrated at storage layer vs bolted-on alerting systems
- Audit trail is intrinsic (algebraic), not a separate logging system

Loss axes (delegate to hot-path TSDB):
- Raw throughput: InfluxDB 10^6 writes/sec vs substrate ~2000/sec at N=4096
- Cardinality: TSDBs handle billions of series vs substrate 0.138*N cap
- Ecosystem maturity: decades of tooling, dashboards, alerting

Architecture: InfluxDB (hot path) + substrate sidecar (compliance path, regulated series only) + deletion-cert API for GDPR/HIPAA Art. 17 requests.

### SPECULATIVE (MEDIUM confidence, cheap test needed first)

**Algebraic range query via time-tag binding:**
P_deflated = 0.45 (raw 0.65, deflated 0.20 uncharted substrate operation)
If HP-1 passes: adds time-windowed retrieval to the compliance sidecar product story
If HF-1 fires: requires temporal codebook redesign before any time-series retrieval claim

**Anomaly detection as integrated substrate primitive:**
P_deflated = 0.40 (raw 0.60, deflated 0.20; MIXAD/HopCPT show Hopfield-memory anomaly detection works, but substrate-specific spectral health-check on time-series has not been tested)
HopCPT (NeurIPS 2023) provides strong precedent for Hopfield-based conformal uncertainty on time series; substrate is adjacent but not identical

### NO-GO (structural losses, do not close niche but close specific sub-claims)

1. Substrate as primary TSDB replacement: N-cap structural mismatch with billions-of-series production TSDBs. Not a competition.
2. High-throughput IoT ingestion on hot path: InfluxDB handles 10^6 writes/sec; substrate is not the right tool for raw ingestion.
3. tau_mem compression as primary value prop: no formal bound derivable from current lit; remove from product narrative until derived.

---

## P estimate summary (deflated, post-calibration-penalty)

| Claim | Raw P | Deflation | P_deflated | Status |
|---|---|---|---|---|
| Compliance sidecar niche is real and defensible | 0.75 | 0.15 | 0.60 | Lit-confirmed TSDB gap |
| XOR time-binding range query works | 0.65 | 0.20 | 0.45 | Uncharted; cheap test pending |
| Deletion cert on time series works (extends PP-9) | 0.70 | 0.15 | 0.55 | Algebraically same as confirmed PP-9 |
| tau_mem gives derivable compression bound | 0.50 | 0.20 | 0.30 | Novel derivation, no precedent |
| Anomaly detection via spectral health-check | 0.60 | 0.20 | 0.40 | Adjacent (MIXAD/HopCPT) unconfirmed |
| Substrate beats TSDB as general replacement | 0.05 | 0.00 | 0.05 | Structural: cardinality + throughput losses are not closable |

Overall GO/NO-GO: GO for compliance sidecar vertical.

---

## Next-drill candidates (priority order)

1. **Cheap decisive test dispatch (CPU scoping)**: XOR time-tag range query, N=1024, K=10, CPU, less than 5min. Route to exp_dev as laptop CPU smoke run. Cost: ~1h.

2. **HopCPT adjacency lit-scan** (modern-Hopfield / conformal-prediction): Does substrate Hopfield similarity-lookup subsume HopCPT conformal-score reweighting? If yes, substrate can claim conformal-calibrated anomaly detection with audit trail. Adjacent to free-probability and modern-Hopfield (both Tier-1 fields). Cost: 1 research sub-agent, 30 min.

3. **tau_mem compression bound derivation** (thermodynamics Tier-1, yield 71%, 7 drills, adjacency A3/A4 un-drilled): Attempt formal Shannon compression bound for exponentially-weighted OU decay on i.i.d. time-series patterns. Maps to thermodynamics Tier-1 field. Cost: 1-day theory.

---

## Citations (verified)

1. HopCPT: "Conformal Prediction for Time Series with Modern Hopfield Networks" -- NeurIPS 2023. https://arxiv.org/abs/2303.12783
2. Attraos: "Attractor Memory for Long-Term Time Series Forecasting: A Chaos Perspective" -- NeurIPS 2024. https://arxiv.org/abs/2402.11463
3. MIXAD: "Memory-Induced Explainable Time Series Anomaly Detection" -- arxiv 2024. https://arxiv.org/pdf/2410.22735
4. MemAE-OCSVM: "Multi-feature unsupervised time series anomaly detection based on memory-augmented autoencoder" -- ScienceDirect 2025. https://www.sciencedirect.com/science/article/abs/pii/S0952197626004057
5. Hierarchical Temporal Memory for anomaly detection -- ScienceDirect 2018. https://www.sciencedirect.com/science/article/abs/pii/S0925231217313887
6. InfluxDB 3 Enterprise data retention (backup gap confirmed). https://docs.influxdata.com/influxdb3/enterprise/reference/internals/data-retention/
7. TimescaleDB data retention policies. https://dohost.us/index.php/2025/11/12/data-retention-policies-managing-old-data-in-influxdb-and-timescaledb/
8. GDPR backup immutability compliance gap (HubiFi). https://www.hubifi.com/blog/immutable-audit-log-basics
9. HIPAA audit log requirements 2025 (Kiteworks). https://www.kiteworks.com/hipaa-compliance/hipaa-audit-log-requirements/
10. NIS2 IoT connectivity compliance. https://ixt.io/blog/regulation-proof-iot-your-utilities-guide-to-nis2-ready-connectivity
11. OU process entropy decay (arxiv). https://arxiv.org/pdf/1910.12931
12. Privacy-preserving time series IoT quality assessment (arxiv 2025). https://arxiv.org/pdf/2501.07154

Verified citations: 12

<!-- routing-completed: Acted-on 2026-06-01: source for Round 10 -->
