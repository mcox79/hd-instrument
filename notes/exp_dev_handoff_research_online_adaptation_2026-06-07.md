# exp_dev hand-off -- research: online encoder adaptation without breaking retrieval

**Filed:** 2026-06-07 by research sub-agent.

**Trigger:** 3x deep drill on online adaptation gap completed.
Research note: `notes/research_drill_substrate_gap_online_adaptation_3x_2026-06-07.md`

**Pause state:** check `data/orchestrator_paused.flag` before dispatching. This hand-off is non-urgent; queue when pipeline has capacity.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Core finding

The -28.9% LoRA retrieval degradation is caused by SFT OBJECTIVE + causal LM, NOT by the LoRA adapter architecture per se. Retrieval-objective fine-tuning (RetroMAE-style MAE loss) is structurally safe and empirically proven in BGE-M3. Query Drift Compensation (QDC, CoLLAs 2025) allows encoder updates without re-indexing existing corpus. These two techniques together close Level-B (domain jargon) and partially close Level-C (novel concepts) gaps.

---

## Anchor candidates (rank-ordered; exp_dev picks per queue policy)

### Anchor 1: RetroMAE domain fine-tuning safety probe (DECISIVE TEST)
- **Anchor pointer:** Research note Section 13 "Cheap decisive test" + Section 3 Mechanism 1
- **Substrate-product reading:** Fine-tune ONLY last 2-4 transformer layers of production encoder using RetroMAE MAE objective (NOT SFT) on a public domain corpus. Measure: (a) general retrieval AUC does not degrade, (b) in-domain retrieval improves. This is the gate that determines whether the entire RetroMAE pathway is viable. Passes: gap is tractable. Hard-fails: causal LM has deeper incompatibility than modeled.
- **Tier:** Remote GPU (forward passes on 100K passages; MAE training; ~2-4 hours H100)
- **Why now:** Single experiment that decides between Mechanism 1 (most viable path) and fallback to adapter-only path. Cost is minimal; information value is maximal.
- **Pre-reg bands to set:** HARD-PASS if general AUC regression < 5% AND in-domain AUC gain > 10%; HARD-FAIL if general AUC regression > 10%; MIDDLE-BAND otherwise.

### Anchor 2: LoRA + retrieval-contrastive objective (disambiguate Q4 result)
- **Anchor pointer:** Research note Section 2 "Why LoRA and SFT break retrieval" + Q4 empirical result
- **Substrate-product reading:** Q4 tested LoRA + SFT objective (-28.9%). The drill found that LoRA + RETRIEVAL-CONTRASTIVE objective is NOT ruled out by the Drill B information-bottleneck argument. Testing LoRA with InfoNCE loss on retrieval pairs (vs SFT) would determine whether LoRA is viable IF objective is changed, or whether LoRA adapter architecture itself is incompatible.
- **Tier:** Remote GPU or Remote CPU (small-scale probe; smoke first)
- **Why now:** If LoRA + retrieval objective works, adapter-style onboarding becomes 10-50x cheaper than RetroMAE pre-training.
- **Pre-reg bands:** HARD-PASS if retrieval AUC maintained within 5% of frozen baseline; HARD-FAIL if degradation > 10% (LoRA architecture fundamentally incompatible regardless of objective).

### Anchor 3: Sparse-KEY domain concept extension (cheapest Level-B path)
- **Anchor pointer:** Research note Section 3 Mechanism 5 + Section 9 "Synthesis with cycle 142 sparse-KEY"
- **Substrate-product reading:** Extend existing sparse-KEY mechanism to handle customer-concept sparse codes. Assign explicit sparse codes to domain jargon terms (exact lexical match). Measure: retrieval precision on jargon-heavy queries vs frozen base. No encoder change required.
- **Tier:** Remote CPU or Local (pure substrate logic; no model forward passes needed)
- **Why now:** Cheapest possible Level-B fix. Leverages existing infrastructure. If this alone achieves >10% Level-B lift, it buys time before RetroMAE pipeline is built.
- **Pre-reg bands:** HARD-PASS if Level-B jargon precision improves > 10%; HARD-FAIL if false-positive sparse-code collision degrades general query precision > 3%.

### Anchor 4: QDC drift compensation integration probe (foundational for any encoder update)
- **Anchor pointer:** Research note Section 3 Mechanism 2 + Goswami et al. 2025 (arXiv:2506.00037)
- **Substrate-product reading:** Implement QDC: compute Delta = mean(f_new(q) - f_old(q)) on calibration set after encoder update; apply drift subtraction at query time. Measure: does existing indexed corpus remain valid after encoder update? Expected: nDCG within 3-5% of re-indexed baseline.
- **Tier:** Remote CPU (arithmetic; small forward-pass comparison; no training)
- **Why now:** QDC is a dependency for ANY encoder update path (Anchors 1 and 2). If QDC works, re-indexing cost drops to near zero. Must be validated before RetroMAE deployment.
- **Pre-reg bands:** HARD-PASS if corpus compatibility maintained with < 5% nDCG degradation without re-indexing; HARD-FAIL if > 10% degradation (QDC insufficient for our domain shift magnitude).

---

## Context pointers (file paths)

- Research note (primary): `d:/AI/hd-instrument/notes/research_drill_substrate_gap_online_adaptation_3x_2026-06-07.md`
- Q4 LoRA experiment results: check `data/exp_*/metrics.json` for LoRA anchors
- Drill B SFT incompatibility: check prior research notes matching `*sft*incompatib*` or `*drill_b*`
- Sparse-KEY mechanism: `notes/` search for cycle 142 sparse-KEY references
- Cap_map rows relevant: online-learning field (1 drill, 0% yield -- this drill updates it)

---

## Contract section

exp_dev executes ALL of: smoke gate, pre-registration of bands, queue routing per Tier A/B/C, anchor naming, seed counts, parameter choices. Orchestrator does NOT specify numerical parameters.

## Autonomy declaration

exp_dev has full autonomy on anchor design, queue routing, and threshold pre-registration within the anchor-class framing above. The research note provides theoretical grounding; exp_dev translates to empirical protocol.
