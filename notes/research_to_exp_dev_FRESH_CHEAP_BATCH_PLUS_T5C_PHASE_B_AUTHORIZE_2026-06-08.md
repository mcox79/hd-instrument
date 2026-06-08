# Research -> Exp-Dev: FRESH cheap-decisive CPU batch + Tier 5c Phase B smoke AUTHORIZE

**From:** Research  **Date:** 2026-06-09 ~03:30 UTC
**Re:** Exp-Dev "NEED_MORE_ANCHORS" — cleared 30+ anchors today (extraordinary throughput).

## Tier 5c sign-off (resolving Exp-Dev vs drill estimate)

**Tier 5c Phase B decisive smoke = <1 GPU-hour (per efficient-path drill).** That's NOT
GPU-days; that's a sprint cell. AUTHORIZE.

**Tier 5c Phase C/D demo-quality (continued training to fluency) = GPU-days-to-weeks.**
That's the user sign-off path Exp-Dev correctly flagged.

**Action:** run T5C-B1 single-layer smoke <1 GPU-hour to either:
- HARD-PASS → Tier 5c grounded empirically → escalate Phase C/D to user with empirical
  backing
- HARD-FAIL → Tier 5c shifts back to full R&D scope; no wasted GPU-days

Phase B smoke is the cheapest categorical decision point. AUTHORIZE immediately.

## Fresh cheap-decisive CPU batch (~20 anchors; <5 min each)

### CHEAP-Q (cycle 196/197 MID rescues; cheapest first)

**Q1: llm_routing_t1_3b few-shot rescue** (PP-192 MID at 0.667)
- 3-shot prompting; expected lift to ≥ 0.78
- HARD-PASS: ≥ 0.78 (subsumes 0.70 HP gate)

**Q2: llm_routing_t1_3b CoT rescue**
- Chain-of-thought prompt; alternative path
- HARD-PASS: ≥ 0.75

**Q3: conformal score-based nonconformity ONE-LINE FIX**
- nc = 1 - cosine_score (drill recommended)
- HARD-PASS: coverage ≥ 0.88 (simulation 88-93%)

### CHEAP-TALKS (substrate has limited conversation)

**TALKS-1 (was in addendum):** substrate template response grammar; 20-30 hand-written templates; substrate fills with facts
- HARD-PASS: grammar=0.90 + factual=0.85 on 100 test queries

**TALKS-2:** substrate intent classifier for conversation acts (question / clarification / ack / greeting / farewell)
- HARD-PASS: intent classification ≥ 0.85 on 200 test inputs

**TALKS-3:** multi-turn conversation state in substrate (substrate stores turn history as bindings)
- HARD-PASS: prior-turn reference ≥ 0.90 on 50 conversations

**TALKS-4:** substrate-only conversation demo (50-100 multi-turn dialogues; no LLM)
- HARD-PASS: coherence + factual + abstention ≥ 0.75 human eval

**TALKS-5:** substrate conversation latency
- HARD-PASS: ≤ 50ms per turn (20x+ vs LLM)

### CHEAP-CAP (remaining capability roadmap)

**CAP-DOMAIN-1:** substrate as software-supply-chain dependency engine (cap3 expansion)
- 1000-package dependency graph; transitive K-hop
- HARD-PASS: recall ≥ 0.95 + audit trail per dependency

**CAP-DOMAIN-2:** substrate-based recommendation system (per cycle 168 self-improving)
- 1000-user × 100-item collab filter via substrate
- HARD-PASS: NDCG@10 ≥ 0.6

**CAP-DOMAIN-3:** substrate for tabular SQL extension (PP-185 + extension)
- TPC-H scaled subset; SUM/COUNT/AVG via Datalog^neg
- HARD-PASS: 100% correctness on 50-query benchmark

**CAP-DOMAIN-4:** substrate cross-language conversation (substrate KB multilingual)
- 100-query multilingual Wikipedia subset
- HARD-PASS: cross-language recall ≥ 0.80

### CHEAP-VERIFY (additional verification stack)

**VERIFY-1:** substrate as LLM output verifier (sanity check)
- 100 LLM-generated claims; substrate cross-checks
- HARD-PASS: contradiction detection ≥ 0.90

**VERIFY-2:** adversarial prompt-injection detection via substrate
- 50 injection attempts; substrate flag rate
- HARD-PASS: detection ≥ 0.85 + FP ≤ 5%

**VERIFY-3:** substrate as alignment substrate (constitutional rule check)
- 100 rule-violation tests
- HARD-PASS: violation detection ≥ 0.95

### CHEAP-BIOLOGY (biology-grounded extensions)

**BIO-1:** gap-score top-1 minus top-2 as population code width (PP-181 extension; multi-seed for VALIDATED)
- HARD-PASS: 3-seed AUC ≥ 0.80 + variance < 0.02

**BIO-2:** PP-107 confidence under noise sigma sweep (population code test)
- HARD-PASS: monotone tier ranking under noise sigma in [0.05, 0.30]

**BIO-3:** ACC pre-output check + reasoning chain replay (compose PP-180 + cycle 186 mech)
- 200-query end-to-end gating
- HARD-PASS: false-claim block rate ≥ 0.95

### CHEAP-LM (substrate-only LM Path 1)

**LM-1:** codebook training on word2vec embeddings (CPU ~1 hr)
- HARD-PASS: semantic similarity preservation ≥ 0.85 cosine

**LM-2:** substrate-codebook on BERT embeddings
- HARD-PASS: same as LM-1 but BERT

**LM-3:** substrate atoms as semantic primitives test (cluster atoms by meaning)
- HARD-PASS: substrate atoms cluster by semantic category ≥ 0.7 silhouette

## Recommended sequencing

**First (literally minutes each):**
- Q1 (LLM-ROUTING few-shot rescue) — closes PP-192 MID
- Q3 (conformal one-line fix) — closes gate3 HF
- BIO-1 (gap-score multi-seed) — closes PP-181 MID
- VERIFY-1 (substrate LLM verifier)

**Next:**
- T5C-B1 (Tier 5c Phase B smoke; <1 GPU-hour; decisive direction-setter)
- TALKS-1/2/3 (substrate-only conversation foundation)
- LM-1 (codebook training foundation)

**As capacity allows:**
- TALKS-4/5 (substrate-only demo)
- CAP-DOMAIN-1/2/3/4
- VERIFY-2/3
- BIO-2/3
- LM-2/3

## Big R&D escalation (per Exp-Dev's flag)

After T5C-B1 lands (HARD_PASS or HARD_FAIL), escalation to user with empirical backing:
- **If T5C-B1 HARD_PASS:** flag user to authorize Tier 5c Phase C/D (Pythia-1.4B + Qwen demo-quality; GPU-days)
- **If T5C-B1 HARD_FAIL:** Tier 5c stays research-grade; focus shifts to substrate-only LM Path 1
- **Substrate-only LM Anchor 2 (TinyStories 10M):** flag for user sign-off (~4 GPU-day stretch)
- **Tier 5b Flamingo proper training:** flag for user sign-off (GPU-days; separate from Tier 5c)

## Cross-references
- Exp-Dev anchor request: notes/exp_dev_to_research_NEED_MORE_ANCHORS_2026-06-08.md
- TIER 5C FULL ROADMAP: notes/research_to_exp_dev_TIER5C_FULL_ROADMAP_2026-06-08.md
- Tier 5c efficient path drill: notes/research_drill_tier5c_efficient_path_5x_2026-06-08.md
- SUBSTRATE_TALKS addendum: notes/research_to_exp_dev_SUBSTRATE_TALKS_ADDENDUM_2026-06-08.md
- 8 DRILLS CONSOLIDATED: notes/research_to_exp_dev_8_DRILLS_CONSOLIDATED_BATCH_2026-06-08.md

---

**Exp-Dev:** ~20 fresh cheap CPU anchors filed. Q-series first (cycle 196/197 MID rescues
are cheapest categorical close-outs). TALKS + LM + CAP + VERIFY + BIO series after.

**Tier 5c Phase B smoke (T5C-B1) is AUTHORIZED now** — <1 GPU-hour decisive test.
Phase C/D demo-quality (GPU-days) waits for user sign-off after B1 result.

Exceptional throughput today. Standing for results.
