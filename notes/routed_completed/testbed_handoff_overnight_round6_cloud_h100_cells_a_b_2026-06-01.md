# Testbed handoff: overnight Round 6 cloud H100 cells A + B

**Filed:** 2026-06-01
**From:** exp_dev (Sonnet)
**To:** testbed session (cloud H100)
**Authorization:** User authorized this turn (2026-06-01 overnight 16h batch)

---

## Cell A: Multi-tenancy depth scaling at N=32768

**Anchor name (proposed):** mt_depth_n32768_v1
**Queue:** cloud H100 (N=32768 multi-tenant)
**Source:** notes/strategy_request_to_strategy_overnight_16h_batch_2026-06-01.md (Tier 1)

### Scientific question

Does the multi-tenant zero-leakage property hold at N=32768? Prior result:
5/5 zero-leakage at N=16384 (multi_tenant_arch1_full_v1_n16384). N=32768 is the
next staging step. Theory predicts ~2x depth (more concurrent tenants) at double N.

### Pre-registered bands (exp_dev to testbed)

- HARD-PASS: contamination_rate=0 in ALL 5 seeds AND zero cross-tenant retrievals
  in codebook-collision attack in ALL 5 seeds (replicates N=16384 result at N=32768).
- MIDDLE: Pattern-1 isolation holds (contamination=0) but Pattern-2 attack partially
  succeeds in 1-2 seeds.
- HARD-FAIL: contamination_rate > 0 in any seed.

### Design

N=32768, 2 tenants (A and B), M_per_tenant=256 (alpha~0.0078).
Architecture 1: per-tenant W matrices (W_A, W_B, no shared memory).
Same codebook-collision attack as N=16384 anchor.
5 seeds: [7, 17, 23, 31, 41].

### Memory estimate

W at N=32768: 32768^2 * 4 = 4 GB per tenant. Two tenants = 8 GB.
Requires H100 (80 GB HBM) or A100 (40/80 GB). NOT feasible on local 4060 Ti (8 GB).

### Implementation note

Based on exp_multi_tenant_arch1_full_v1_n16384.py. Increase N_FULL from 16384 to 32768.
Adjust W dtype to float16 or bfloat16 if memory is tight (preserves isolation guarantee).
Include PROT-018 binding: anchor name mt_depth_n32768_v1 -- no _n suffix needed per
PROT-018 rule 3 since this is a depth test at N=32768 (N is in the name but as a
descriptor, not a binding -- OR use mt_depth_n32768_v1 with explicit N_FULL=32768 assertion).

### Timeout estimate

N=32768 vs N=16384 = 4x in N^2 ops. N=16384 anchor used timeout=21600s.
N=32768 estimate: 21600 * 4 = 86400s = 24h (exceeds 14400s threshold).
REVIEW: testbed session should benchmark before queueing. Consider float16 to reduce
memory and compute by 2x. Alternative: reduce M_per_tenant from 256 to 128 (reduces
W construction cost by 50%, isolation guarantee unchanged).

---

## Cell B: PP-33 framework-class lift via N-scaling collapse

**Anchor name (proposed):** pp33_fdt_4pt_collapse_v1
**Queue:** cloud H100 (N up to 32768, 4-point fit)
**Source:** notes/strategy_request_to_strategy_overnight_16h_batch_2026-06-01.md (Tier 1)

### Scientific question

Does the FDT-violation order parameter X(t,t') for the substrate show a 4-point
N-scaling collapse? Fitting exponent x: x=2/3 -> DMFT-TW class; x<0.5 -> Levy-DMFT class.

### Pre-registered bands

- HARD-PASS: clean N-scaling collapse (R^2 > 0.90 on the collapse fit), exponent x
  measured to within +/-0.1, distinguishing x=2/3 (DMFT-TW) from x<0.5 (Levy-DMFT).
- MIDDLE: collapse visible but noisy R^2 in [0.70, 0.90], exponent x uncertain +/-0.2.
- HARD-FAIL: no collapse (R^2 < 0.70) OR x outside [0.1, 1.0] (unphysical).

### Design

N_grid = [4096, 8192, 16384, 32768]. alpha=0.15 (above alpha_c=0.138).
FDT-violation order parameter: X(t,t') = chi(t,t') / C(t,t') where:
  C(t,t') = two-time correlator (as in CK discriminator Cell C)
  chi(t,t') = integral response (susceptibility)
N-scaling collapse: for each t,t': X(N,t,t') should collapse onto a scaling function
when plotted vs N^x * (t-t') or N^x * log(t/t').
4 N values are needed to fit x. N=32768 drives the H100 requirement.

### Dependency

Cell C (ck_seb_discriminator_v1) results will be informative for the chi-C measurement
protocol. But Cell B is independent and can run in parallel with Cell C results.
The 4-point N-scaling collapse requires all 4 N values -- cells at N in {4096, 8192,
16384} can run on local GPU; only N=32768 requires H100.

### Alternative: staged approach

If cloud H100 is not immediately available, testbed can run N in {4096, 8192, 16384}
on local GPU to establish the collapse trend, then add N=32768 to confirm.
This is recommended: partial collapse (3 points) is already valuable.

### Timeout estimate

Per N point: similar to CK discriminator (N=2048 ~ 150s). At N=32768: 150 * (32768/2048)^1.5 ~ 150 * 181 ~ 27000s. Borderline 14400s threshold.
Testbed to benchmark at N=8192 and extrapolate.

---

## Cloud-launch protocol

Per [[feedback-cloud-launch-snapshot-reconcile]]:
1. Snapshot current cloud instance state BEFORE any launch command.
2. Check capacity availability before committing to N=32768 config.
3. If instance launch fails or 502 errors: record any orphan instance ID from error response.
4. Post-launch: reconcile by listing all instances and verifying the launched instance
   is in the expected state before shipping queue entry.

Lambda Cloud API context: on-demand only (no spot/preemptible per feedback_lambda_no_spot_api.md).
Fast-fail: 300s stuck-boot threshold.

---

## Handoff contract

Testbed session is authorized to:
- Launch and configure cloud H100 instance for Cells A + B.
- Design final N=32768 scripts based on existing N=16384 templates.
- Queue to overnight_queue (the remote runner IS the GPU runner; cloud H100 may
  be a separate runner -- testbed confirms the target queue).
- Drop either cell if cost/timeout is prohibitive and inform orchestrator.
- Reduce M_per_tenant (Cell A) or reduce N_max (Cell B) for budget if needed.

Testbed is NOT authorized to:
- Modify cap_map (orchestrator only after verdict).
- Ship more than 2 additional anchors beyond A + B without orchestrator approval.
