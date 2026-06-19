# exp_dev hand-off -- MoE learned-router discriminating probe

**Filed:** 2026-05-27 by Research sub-agent.
**Source drill:** `notes/research_moe_learned_router_2026-05-27.md`
**Trigger:** v220 K_perarm M2_DOMINANT: LSH gating entropy sole K-scaling degradation source.
**Pause-gated:** YES. Honor `data/orchestrator_paused.flag` per [[feedback-obey-user-pause-explicitly]].

---

## TASK

Replace LSH gating with cosine-dot gating in the MoE SHIFT architecture. Sweep K = {4, 8, 16, 32}. Compare retention and routing entropy vs v220 K_perarm LSH baseline.

## WHY

v220 diagnosed M2_DOMINANT: LSH gating entropy (0.78b at K=2 -> 5.32b at K=64) is the SOLE source of K-scaling degradation (IEC ~0 all K; m_cap constant all K). The research drill (`notes/research_moe_learned_router_2026-05-27.md`) identified Expert-Choice cosine-dot routing as the most substrate-compatible router replacement. Cosine-dot eliminates entropy by design and uses the substrate's native retrieval operation (dot(query, anchor)/N). This is a ~5-10 line code change -- the cheapest possible rescue probe.

## CONTRACT

### Core implementation

Per-expert anchor: random BSC vector (N=4096 bipolar +/-1, one anchor per expert). Init: `anchor_k = torch.sign(torch.randn(N))`.

Routing: `scores = [dot(query, anchor_k)/N for k in K_experts]; expert_assigned = argmax(scores)`.

Optional Expert-Choice variant (preferred if batch processing is available): each expert selects its top ceil(batch_size/K) items by cosine score rather than items selecting their expert. Both variants acceptable; report which was used.

### Metrics to report per cell

1. `routing_entropy_bits` -- Shannon entropy of routing assignment distribution over K experts.
2. `retention_mean` -- mean retention at the standard M-load (same as v220 baseline).
3. `retention_vs_lsh_delta` -- difference from v220 LSH baseline at same K.
4. `k_eff_cosine` -- effective number of distinct experts used (non-empty).
5. `anchor_cosine_spread` -- mean pairwise cosine similarity among anchors (diagnostic: if close to 1/sqrt(N), anchors are mutually orthogonal as expected).

### Pre-registered bands (research note section b)

- **HARD-PASS:** routing entropy at K=16 < 2.0b AND retention at K=16 >= K=4 retention minus 0.005.
- **HARD-FAIL:** routing entropy at K=16 > 3.0b (same as LSH) OR retention at K=16 < K=4 retention minus 0.015.
- **MIDDLE BAND:** entropy [2.0, 3.0b] or retention delta [0.005, 0.015]. INCONCLUSIVE; escalate to Hebbian-anchor follow-up.

### Minimum experiment

3 seeds at K = {4, 8, 16, 32}. N=4096 (substrate default). M at standard operating load (same as K_perarm_v1). Estimated runtime: ~2500s CPU (same as K_perarm_v1 at 2288.9s plus overhead).

## AUTONOMY

- Choose anchor initialization (random BSC vs Hebbian-bundle of first M/K items per expert). Report which was used.
- Choose Expert-Choice vs token-choice based on substrate implementation availability.
- Choose smoke (K={4,16}) vs full (K={4,8,16,32}) based on queue state.
- Set numerical M-load and seed count within standard substrate defaults.
- If routing entropy at K=16 > 3.0b with random anchors, optionally retry with Hebbian anchors in same run.

## NOT IN SCOPE

- Do NOT modify the MoE SHIFT capacity computation or expert dimensionality.
- Do NOT add gradient-based anchor training (this probe uses fixed anchors only).
- Do NOT sweep N or M systematically -- standard operating point only.

## CROSS-REFS

- `notes/research_moe_learned_router_2026-05-27.md` -- full pre-reg + caveats + P estimates
- `notes/strategy_decisions_2026-05-27.md` v220 -- mechanism diagnosis source
- `data/exp_wave14_moe_shift_K_perarm_v1/` -- LSH baseline to compare against

---

**End hand-off.**
