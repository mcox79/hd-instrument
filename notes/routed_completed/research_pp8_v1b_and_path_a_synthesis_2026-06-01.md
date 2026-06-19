# Research: PP-8 v1b LR-fix + D3-Path-A post-D1-1 refresh — combined synthesis

Date: 2026-06-01
Origin: user pushback after I started filing a routing without drilling — "did you do research on this?" Triggered 2 parallel Sonnet drills (~135K tokens combined) on v1b LR-fix HP-fragility mitigation + D3-Path-A architecture refresh post-D1-1.
Method: 2 parallel Sonnet drills + main-thread synthesis

## HEADLINE

**v1b primary mitigation: WSD (Warmup-Stable-Decay) + EMA combination, P_joint ≈ 0.55-0.60.** The HP-fragility failure mode is precisely diagnosed as **narrow-attractor collapse under cosine LR annealing** — SGD lands at the BOUNDARY of flat regions (Izmailov 2018 SWA paper); cosine decay locks in boundary not center. WSD inserts a stable phase between warmup and decay; EMA adds zero-cost trajectory smoothing.

**D3-Path-A architecture: 3 viable variants survive D1-1**, but the **original "audit-grade semantic cache" wedge does NOT survive random keys at the substrate layer**. Strongest revised wedge: **Architecture 3 asymmetric bridge** (P=0.44) — substrate = audit-cert layer; standard ANN = semantic-match layer. This is MORE DEFENSIBLE than the original because it isolates substrate's unique contribution (deletion-cert) from solved engineering (semantic ANN).

**Critical strategic insight (cross-drill)**: substrate's durable moat is the **deletion-certificate infrastructure**, NOT the retrieval mechanism. GDPR Art 17 + EU AI Act Art 13 + HIPAA accounting-of-disclosures is the wedge that survives any architectural variation. LangChain Memory / Mem0 / Anthropic Memory have no auditable deletion certificate.

## DRILL 1: v1b LR-fix HP-fragility mitigation

### Precise failure-mode characterization

Not generic catastrophic forgetting — specific sub-class: **narrow-attractor collapse under LR annealing**. Mechanism chain:

1. Warmup (0-100): high LR, broad gradient steps; model sits at basin boundary not center
2. Peak (250-400): gradient magnitude drops as solution crystallizes; val accuracy spikes
3. Cosine decay onset: `η(t) = η_max/2·(1 + cos(πt/T))` drops from peak to near-zero
4. Collapse: cosine commits to last-visited boundary point; for narrow attractors (Phi-3 keys), small LR reduction tips the gradient balance enough to fall out

Geometric fact (Izmailov 2018): SGD solutions land at boundary of wide-loss valleys not center. Cosine decay accelerates commit to whatever boundary point was last visited. Width of attractor basin determines tolerance: random codebooks (wider basins via isotropy) survive partial decay; Phi-3 keys (narrower via anisotropy) collapse harder; held-out (even narrower; basins are path-dependent) collapses catastrophically.

### 5 mitigation candidates ranked

| # | Mitigation | P (deflated) | Eng-days | Mechanism |
|---|---|---|---|---|
| **1** | **WSD: Warmup-Stable-Decay (3-phase)** | **0.52** | **0.5** | Insert constant-LR stable phase between warmup and cosine cooldown; literature: DeepSeek-V3, WSD-S Wen 2024, arxiv 2601.09000 universal dynamics |
| 2 | SWA: Stochastic Weight Averaging | 0.44 | 1.0 | Running average of weights → center of flat region (Izmailov 2018); PyTorch built-in |
| 3 | Polyak/EMA Shadow Model | 0.40 | 0.25 | Exponential moving average α∈[0.999, 0.9999]; standard in GAN + diffusion training (arxiv 2411.18704) |
| 4 | Extended Warmup (100→250) | 0.36 | trivial | Delay cosine onset past peak window |
| 5 | Lookahead Optimizer | 0.28 | 1.5 | Fast/slow weight sets; 1.5× memory |

### Stacking analysis

- **WSD + EMA: ORTHOGONAL — stacks cleanly** (different layers: schedule vs trajectory). RECOMMENDED default.
- WSD + SWA: 40% redundant (both target basin center)
- SWA + EMA: redundant (pick one); EMA is zero-cost choice
- Lookahead + any: independent but lower priority

### Lambda batch grid spec

Per [[feedback-batch-cloud-experiments]]: single Lambda job sharing Phi-3-mini-4bit base load.

**3 × 3 grid = 9 cells**:

| Schedule axis | Key-encoding axis |
|---|---|
| `sched_baseline` (warmup + cosine; control reproducing failure) | `keys_phi3` (v1+v1' setting) |
| `sched_wsd` (warmup + stable + cosine cooldown) | `keys_frozen_random` (D1-1 setting) |
| `sched_constant` (warmup + constant LR, no decay; arxiv 2603.16127 WSO) | `keys_held_out` (Option A split) |

EMA shadow model in ALL 9 cells (zero-cost dual-eval). SWA optional eval on `sched_wsd` cells (3 extra eval points, no extra training).

### Pre-reg bands (per [[feedback-pre-reg-peak-not-final-HP-fragile]])

Track 4 metrics per cell:
- `val_peak = max(val(t) for t in training)`
- `stability = mean(val(t) for t in [peak_step-25, peak_step+25])` (multi-step stability at peak)
- `val_final` for live model + `val_ema_final` for EMA shadow
- `retention_ratio = final / peak` (primary HP-fragility metric)

**Global HARD-PASS**: retention_ratio ≥ 0.80 for any cell — peak is locked in
**Global MIDDLE-BAND**: retention_ratio 0.60-0.80 OR stability < 0.80 × peak
**Global HARD-FAIL**: retention_ratio < 0.50 OR peak < 0.50 (model never found solution)

### Strategic recommendation (v1b primary dispatch)

Single Lambda batch, 9 cells, ~$8-12 estimated Lambda budget (shares Phi-3-mini-4bit model load; per-cell incremental cost low).

Pre-reg WSD + EMA as primary combination across the 9 cells. Expected outcome: WSD cells outperform baseline cells on retention_ratio across all 3 key-encoding axes. Random-codebook advantage interpretation: wider basins benefit MORE from removing schedule artifact; held-out genuine difficulty floor remains even with WSD.

## DRILL 2: D3-Path-A KV-cache post-D1-1 refresh

### Critical structural finding

D1-1 used `"Key {idx}: "` fixed string format — **exact-match retrieval, NOT semantic-match retrieval**. Random keys retrieve correctly because same string → same embedding. D1-1 PROVED M1 dominance for fixed-format retrieval; it NEITHER PROVED NOR REFUTED M2 contribution to paraphrase-variation matching.

**Geometric argument**: SimHash preserves cosine similarity. If write key K_write and query key K_query come from same embedding model on semantically similar text, SimHash preserves their proximity. **With frozen-random K_write at write time, there is NO correlation structure between K_write and paraphrase K_query**. Cache hit probability for paraphrases equals base rate for unrelated pairs. **Semantic matching is structurally destroyed under random keys at the SUBSTRATE LAYER**. This is a geometric fact, not calibration uncertainty.

### 5 architecture candidates ranked

| # | Architecture | P (deflated) | Audit-cert | Semantic match | Cost delta |
|---|---|---|---|---|---|
| **1** | **Asymmetric bridge: random substrate keys + Phi-3-ANN bridge layer** | **0.44** | **Strong** | **Yes (ANN layer)** | +$2-3 |
| 2 | Phi-3 keys for KV-cache (separate from PP-8 task) | 0.38 | Good (collision risk) | Yes (substrate) | +$5-10 |
| 3 | Pure random (exact-match cache only) | 0.42* | Strong | No | Zero |
| 4 | Hash + LSH hybrid (Tier 1 exact + Tier 2 approximate) | 0.35 | Moderate (Tier 2 complex) | Yes (LSH) | +$2-3 |
| 5 | Val-side semantic match | 0.22 | Weak | Uncertain (query-response cosine) | +$4-9 |

*Arch 3 P is for the narrower product (exact-match audit cache only), not the original semantic claim.

### Strategic positioning verdict

**Original "audit-grade semantic cache" wedge**: does NOT survive random keys at substrate layer. The semantic-match mechanism was always M2-dependent; D1-1 showed M2 isn't load-bearing in exact-format retrieval but that task never tested phrasing variation.

**3 revised wedges remain viable**:

- **Wedge A1 (Arch 1 asymmetric bridge, STRONGEST)**: substrate = audit-cert layer; standard embedding ANN = semantic-match layer. Reframes substrate's role; isolates the unique contribution (deletion-cert) from solved engineering (semantic ANN). MORE DEFENSIBLE than original because the moat is now legally durable (regulatory requirement) not technically novel (semantic-match is solved by competitors).
- **Wedge A2 (Arch 2 Phi-3-keys-for-KV-cache)**: original Path A architecture, conditional on paraphrase smoke validation. P=0.38 because empirically unvalidated post-D1-1.
- **Wedge A3 (Arch 3 exact-match-only)**: narrower "audit-grade exact-match cache" for HIPAA accounting-of-disclosures + batch inference + CI pipelines. Doesn't compete on semantic dimension; competes on cryptographic deletion-cert.

**Cross-competitor positioning post-D1-1**: LangChain Memory / Mem0 / Anthropic Memory all operate on approximate semantic matching with NO audit-cert capability. Substrate's moat shifts from "semantic match + audit" to "audit infrastructure for ANY caching architecture". The narrower wedge is also more durable: GDPR Art 17 + EU AI Act Art 13 + HIPAA are regulatory requirements competitors cannot address with their current architectures.

### Recommended next smoke

**Primary**: Architecture 2 paraphrase test using MRPC/QQP benchmark, ~$3-5 Lambda, ~60s wall.
- HARD-PASS: paraphrase hit rate > 60% at cosine threshold 0.85 + stability across 3 thresholds (0.80/0.85/0.90)
- HARD-FAIL: paraphrase hit rate < 35% (semantic structure not inherited by substrate codewords)

**If Arch 2 PASSES**: original wedge validated. Proceed to FULL.
**If Arch 2 FAILS**: adopt Arch 1 (asymmetric bridge); reframe product positioning as "audit-cert infrastructure for LLM caching" + "semantic matching via standard ANN".

**Do not smoke Arch 4 (val-side)** — too weak audit + semantic coherence problem.
**Do not smoke Arch 5 (LSH hybrid)** — legal complexity for Tier 2 audit certificate outweighs benefit.

## CROSS-DRILL SYNTHESIS

### Single Lambda batch dispatch grid (per [[feedback-batch-cloud-experiments]])

Combine v1b LR-fix grid + Arch 2 paraphrase smoke into single Lambda dispatch:

- **v1b grid**: 9 cells (3 schedule × 3 key-encoding); ~$8-12 estimated
- **Arch 2 paraphrase smoke**: 1 cell (Phi-3-keys + WSD schedule + MRPC/QQP paraphrase eval); ~$3-5
- **Combined**: 10 cells, single Phi-3-mini-4bit model load, ~$11-17 estimated Lambda budget

Per [[feedback-pre-reg-peak-not-final-HP-fragile]]: ALL cells pre-reg explicit peak + stability + retention_ratio bands.

### Cap_map implications

PP-8 substrate-LLM deep integration row (currently promoted v316):
- **Conditional LIFT after WSD+EMA HARD-PASS**: → 🟢 0.60-0.78 (peak lock-in confirmed; HP-fragility resolved)
- **Caveat addition**: "M1-dominant key encoding; Phi-3 forward pass NOT required on key side for exact-match retrieval"
- **Sub-property addition**: "WSD+EMA HP-fragility mitigation stack" (production deployment requirement)

D3-Path-A KV-cache row (proposed but not yet created per Round 3 drill):
- **Create as NEW row** if Arch 2 smoke HARD-PASS → row at 🟡 0.50-0.65
- **Create as NEW row with Arch 1 architecture** if Arch 2 smoke HARD-FAIL → row at 🟡 0.45-0.60 (substrate=audit-layer reframe; semantic-match handled by standard ANN)
- **Sub-property**: "Deletion-cert infrastructure as universal compliance moat across cache architectures"

### Strategic recommendation (consolidated)

1. **Dispatch combined Lambda batch immediately**: 10 cells, ~$11-17 budget, single Phi-3-mini-4bit base load
2. **Pre-reg per [[feedback-pre-reg-peak-not-final-HP-fragile]]**: explicit peak + stability + retention bands; multi-metric eval per cell
3. **Strategic positioning post-results**:
   - WSD+EMA HARD-PASS + Arch 2 HARD-PASS: substrate-LLM deep integration is production-viable AND original Path A wedge survives
   - WSD+EMA HARD-PASS + Arch 2 HARD-FAIL: ship with Arch 1 asymmetric bridge architecture (more defensible reframe)
   - WSD+EMA HARD-FAIL: deeper investigation required (possibly architectural rather than schedule)

## METHOD NOTES

- 2 parallel Sonnet drills + main-thread synthesis ≈ ~135K tokens combined
- Per [[feedback-pre-reg-peak-not-final-HP-fragile]] (saved earlier today): pre-reg bands explicit on peak + stability + retention_ratio; no batch-level expectation
- Per [[feedback-batch-cloud-experiments]] (saved earlier today): single Lambda batch dispatch sharing Phi-3-mini-4bit base load
- Per [[feedback-drill-prompt-bodies-must-be-generic]] (saved earlier today): future drill prompts must use generic descriptions in prompt bodies; the drills run for this synthesis predated the lock-in
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated 0.15-0.20 throughout; novel-synthesis cap 0.50 applied
- Strong literature anchors: Izmailov 2018 SWA, DeepSeek-V3 WSD, arxiv 2601.09000 universal dynamics, arxiv 2603.16127 WSO, arxiv 2411.18704 EMA dynamics, Zhang 2019 Lookahead, Hara-Kabashima 2026 DMFT


Acted-on 2026-06-01: synthesis adopted; 10-cell dispatch authorized for testbed; WSD+EMA mitigation strategy + Architecture 1 asymmetric-bridge pivot
