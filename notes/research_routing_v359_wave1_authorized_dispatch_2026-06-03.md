# RESEARCH ROUTING — Wave 1 AUTHORIZED dispatch (3 probes)

**From:** Research session
**To:** Orchestrator / Testbed / exp_dev
**Date:** 2026-06-03
**Trigger:** User explicit GO authorization for Wave 1 of substrate-influenced context+training probe dossier (`research_routing_v359_substrate_context_training_probe_dossier_2026-06-03.md`).
**Status:** AUTHORIZED. Total $15-35 cloud + ~2 days wall.
**Discipline:** per-probe specs locked; testbed picks up per integration checklist. Per-PROT compliance.

---

## 0. AUTHORIZED PROBES

| Anchor name | Resource | Cost | Wall | Eng | Authorization status |
|---|---|---|---|---|---|
| **`phase_d_pre_ablation_antihebbian_failure_signatures_v1_n128`** (NEW pre-flight gate) | local CPU | $0 | <2h | 0.5 day | AUTHORIZED (pre-flight; gates Probe 11+ dispatch) |
| `phase_d_tier6_full_pipeline_4_core_char_lm_v1` (DEFENSIVE UPDATE) | A100 cloud | $5-10 | ~2-4h | 3-4 days | AUTHORIZED (dispatch GATED on pre-ablation NOT triggering watchlist signatures) |
| `substrate_curriculum_learning_small_lm_v1` | Pythia-160M cloud | $5-15 | ~6-12h | 2-3 days | AUTHORIZED |
| `tier2_substrate_preloaded_icl_pythia410m_v1` | local GPU or cheap cloud | $5-10 | ~6h | 2 days | AUTHORIZED |

**Full specs at:** `research_routing_v359_substrate_context_training_probe_dossier_2026-06-03.md` §§1-2 (now updated with Probe 11+ upgraded spec).

---

## 1. DISPATCH SEQUENCING

```
T-0 (NOW)
├── Testbed picks up Probe 11+ spec; starts engineering (anti-Hebbian + HRC wiring is the longest path; ~3-4 days)
├── Testbed picks up Probe 2 + Probe 8 specs; engineering in parallel (~2-3 days each; smaller scope)
└── Engineering proceeds in parallel; cheap A100 cloud bootstrap shared across all 3 probes if possible

T+2-4 days (engineering complete)
├── Probe 2 dispatches (cheapest engineering; smallest scale)
├── Probe 8 dispatches (Pythia-160M; cheap cloud)
└── Probe 11+ dispatches (4-core substrate-native LM; A100)

T+4-6 days (verdicts land)
├── 3 verdicts processed via verdict_handler
└── Wave 2 / Phase E decision gates evaluated

If Probe 11+ HARD-PASS:
├── Strong empirical signal for substrate-native LM training viability
├── Trigger Phase E candidate (Pythia-160M with FULL 12-primitive surface; $25-50; 1-2 weeks)
└── Surface to user for Phase E GO

If Probe 11+ MIDDLE or HARD-FAIL:
└── Synthesize per dossier §11+ discriminator outcomes; refine for next-cycle design
```

---

## 2. INTEGRATION CHECKLIST (for testbed)

### Pre-Flight: anti-Hebbian failure-signature ablation (NEW per cascade drill)

**Anchor:** `phase_d_pre_ablation_antihebbian_failure_signatures_v1_n128`
**Resource:** local CPU
**Wall:** <2h
**Cost:** $0

Per cascade drill: P=0.55 that anti-Hebbian primitive becomes load-bearing failure mode at LM-class scale. Cheap CPU ablation tests 3 watchlist signatures BEFORE A100 cloud spend on Probe 11+.

- [ ] 2-layer minimal substrate-native loop at N=128 (small for CPU; tests dynamics not scale)
- [ ] Apply 4 core primitives jointly: outer-product write + anti-Hebbian contrastive + hierarchical recurrent retrieval + stacked independent-W
- [ ] Train on synthetic micro-corpus (~1000 chars; sparse-coding regime per Tsodyks-Sejnowski)
- [ ] Monitor 3 failure signatures:
  - (i) BPC plateau within 100-500 steps with positive-only control continuing to improve
  - (ii) ||W||_2 exponential growth within 200 steps
  - (iii) Retrieval accuracy on held-out probe drops toward chance
- [ ] **Gate rule:** if ANY signature triggers → ABORT Probe 11+ cloud dispatch; pivot to defensive variant OR hybrid path
- [ ] **Gate rule:** if NO signatures trigger → Probe 11+ dispatches to A100 cloud as planned

### Probe 11+ (FULL-PIPELINE 4-CORE substrate-native LM) — DEFENSIVE UPDATE per cascade drill

- [ ] 4-layer character-LM scaffolding
- [ ] **Outer-product Hopfield write** per layer (standard Hebbian rule)
- [ ] **Anti-Hebbian bipartite contrastive** wiring — **DEFENSIVE: use Tsodyks-Sejnowski sparse coding** (activity ~5% per pattern per cascade drill best-mitigation finding; gives 25× α_c lift over dense coding); **DEFENSIVE: binary activations only** (no continuous; per cascade drill gradient-degeneration risk for soft activations)
- [ ] **Hierarchical recurrent retrieval** per layer (multi-step pattern lookup; binary activations throughout)
- [ ] **Stacked independent-W composition** (Error-Correction-Chain criterion; max_k(α_k) < α_c with α_c lifted to ~3.45 via sparse coding)
- [ ] **NEW: α budget accounting** — positive patterns P + anti-Hebbian patterns Q must satisfy (P+Q)/N < α_c_sparse (per cascade drill highest-severity failure mode)
- [ ] NO gradient descent at ANY layer
- [ ] Loss measurement via final-layer retrieval cosine
- [ ] Baseline: identical 4-layer char-LM gradient-trained
- [ ] Corpus: Wikitext-2 character-level (~10MB)
- [ ] 5 seeds each
- [ ] Pre-registered bands: HP BPC ≤ 2× baseline + wall ≤ 0.5× baseline + all 4 primitives operational throughout; HF BPC > 4× baseline OR primitive collapse OR ANY of the 3 cascade-drill watchlist signatures triggered
- [ ] **NEW: auto-abort on watchlist signature trigger** (saves cloud spend mid-run if anti-Hebbian collapses)
- [ ] Per-cell partial JSON output per `feedback_testbed_progress_logging_and_restart`
- [ ] Cost tracker $5-10 ceiling
- [ ] **GATE: Probe 11+ dispatches ONLY if pre-ablation NO-SIGNATURE pass**

### Probe 8 (substrate-curriculum-learning)

- [ ] Pythia-160M small LM training scaffolding
- [ ] 4 curriculum policies wired:
  - (i) Random ordering (baseline)
  - (ii) Difficulty-graded
  - (iii) Loss-based active learning
  - (iv) Substrate-curriculum (substrate scores next training example via lowest-cosine to current substrate state)
- [ ] Wikitext-2 character-level corpus for 1 epoch
- [ ] Measure convergence rate (loss vs training step) + final BPC on held-out test set
- [ ] Pre-registered bands: HP substrate reaches ≤ best baseline BPC in ≤ 50% of steps; HF substrate-curriculum BPC > random baseline
- [ ] 5 seeds
- [ ] Cost tracker $5-15 ceiling

### Probe 2 (substrate-pre-loaded ICL)

- [ ] Pythia-410M (or Llama-3.2-3B if cloud budget allows) LM
- [ ] 3 conditions per problem: (i) standard ICL with K=10 examples in prompt + query; (ii) substrate-loaded with K=10 examples Hebbian-written + only query in prompt + substrate residual-stream injection at layer 0.7L; (iii) zero-shot baseline
- [ ] Task suite: 200 problems × 3 task types (analogy completion + arithmetic-with-format + sentiment classification)
- [ ] 5 seeds
- [ ] Pre-registered bands: HP substrate-loaded within ±5pp of standard ICL AND substrate input tokens < 10% of standard ICL AND wall-time per "learning instance" ≥ 50× faster; HF substrate-loaded < zero-shot baseline
- [ ] Cost tracker $5-10 ceiling

---

## 3. SHARED INFRASTRUCTURE NOTES

- All 3 probes can ride a single cheap A100 cloud bootstrap if scheduled together (substrate's bipolar primitives are GPU-compute-light; the dominant cost is small-LM inference + training)
- Local GPU (RTX-4060-Ti) viable for Probe 2 at smaller LM scale (Pythia-410M); use cheap T4 cloud only if local capacity is in use
- Probe 11+ requires A100 for the 4-layer char-LM training with full-pipeline 4-core wiring
- Cost tracker monitoring: $15-35 ceiling; alert at $25; cap at $40 incremental

---

## 4. CAP_MAP IMPACT (if Wave 1 all-HP)

If Probe 11+ HP: **NEW substrate-novel finding** — substrate's 4-primitive white-space combination empirically validated as a training+inference loop at small scale. Founds candidate PP-59 row (substrate-native LM training; band 0.55-0.70 EXPLORATORY).

If Probe 8 HP: NEW substrate sub-property — training-orchestration intelligence via substrate scoring. Cross-references PP-52 training-speedup framework. Could lift PP-52 band.

If Probe 2 HP: NEW substrate sub-property — ICL persistent memory at ~0 context cost. Adds to Phase 0.5b sub-cell H expected outcome.

**Triple-HP would empirically anchor 3 substrate-novel capability claims:** substrate-native LM training viability + substrate-as-training-orchestrator + substrate-as-persistent-ICL-memory.

---

## 5. NEXT-CYCLE DECISION GATES

Post-Wave-1 verdicts:

- Probe 11+ HP → **Phase E candidate trigger:** Pythia-160M-scale substrate-native LM with FULL 12-primitive surface active during training+inference ($25-50; 1-2 weeks engineering); user GO required at Phase E gate
- Probe 8 HP → Phase B Cluster B1 design extended with substrate-curriculum-learning variant cell
- Probe 2 HP → Phase 0.5b sub-cell H pre-reg gate strengthened (substrate-loaded ICL empirically anchored at small scale before Llama-3.1-8B test)
- Any HF → synthesize discriminator outcomes per dossier; refine for next-cycle

---

## 6. OPTIONAL CASCADE DRILL

Per Drill 4 next-drill candidate: **anti-Hebbian contrastive at transformer scale** — Tier-1 field-advisor match for the riskiest of the 4 core primitives at LM scale. ~30 min sonnet, $0.

**Could dispatch in parallel to Probe 11+ engineering** to provide theoretical de-risking on whether the anti-Hebbian primitive scales cleanly at LM-class scales BEFORE Probe 11+ empirical results land. Surfaces failure modes Probe 11+ should design for.

**Status: NOT DISPATCHED** — pending user nod (separate from Wave 1 authorization).

---

## 7. DISCIPLINE DECLARATIONS

- **Per `feedback_obey_user_pause_explicitly`:** Wave 1 ($15-35) within user authorization received 2026-06-03.
- **Per `feedback_capabilities_not_product_positioning`:** each probe framed as substrate-capability-add question.
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** all HARD-FAIL trip-wires explicit; verdict_handler honest re-read.
- **Per `feedback_batch_cloud_experiments`:** all 3 probes share cloud bootstrap if scheduled together.
- **Per `feedback_testbed_progress_logging_and_restart`:** per-cell partial JSON for restart capability.
- **Per `feedback_short_cloud_runs_preferred`:** each probe under per-case threshold; cumulative within standing envelope.
- **PROT-018:** anchor names per dossier §§1-2 (compliant with tier-prefix + _v1 family).
- **PROT-022:** Probe 11+ tests 4-primitive joint operation; pre-reg HP/HF bands per Drill 4 closed-form predictions.

---

**END.**

**Testbed:** Wave 1 authorized; pick up integration checklist (§2); dispatch on engineering completion (estimated ~3-4 days for Probe 11+ which is the longest path).

**Orchestrator:** queue management — when verdicts land, dispatch verdict_handler per usual flow; trigger Phase E surface to user IF Probe 11+ HARD-PASSes.

**User:** Wave 1 dispatched on engineering ready. Phase E ($25-50 Pythia-160M scale-up with FULL 12-primitive surface) decision-gate surfaces post-Wave-1 verdicts. Cascade drill (anti-Hebbian contrastive at transformer scale) available for $0 sonnet de-risking — say the word.
