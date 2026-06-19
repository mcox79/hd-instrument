# exp_dev hand-off -- research: charLM HD hybrid recapture (3x drill)

**Filed:** 2026-06-17 by research sub-agent (post 3x deep lit-scan).

**Trigger:** Tier-6 charLM Shakespeare FULL run produced hybrid_BPC ~3.62 (MIDDLE_BAND; NOT VALIDATED). Research 3x drill across HDC/VSA hybrids + char-level LM stacks + BPC-improvement techniques delivered at notes/research_charLM_HD_hybrid_recapture_3x_2026-06-17.md.

**Pause state:** read data/orchestrator_paused.flag at dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile.

---

## Headline finding (research note)

- Published char-LM SOTA on Shakespeare/enwik8 scale sits at BPC ~0.94-1.06 for dense small models with the canonical stack (depth + segment-recurrence + RoPE/ALiBi + AdamW-cosine + tied embeddings + length-curriculum).
- ZERO published autoregressive char-LM uses VSA binding or resonator decoding (so no direct comparator; we are in an under-explored regime).
- Substrate hybrid_BPC ~3.62 is ~2.5+ BPC above what dense baselines achieve. Gap is too large to be the HD seam alone; trunk-stack basics likely dominate.
- Best architectural precedent for HD-as-LM-component is hierarchical chunk-pooling (Charformer GBST, CANINE, MEGABYTE), NOT self-attention substitution.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- Vanilla char-transformer baseline recapture (TRUNK STACK)
- Anchor pointer: research note section (b) STAGE 1; section (e) Tier-1 item 1.
- Substrate-product reading: train a NO-HD vanilla 6-layer char-transformer on Shakespeare with the canonical small-LM stack (AdamW + cosine warmup + RoPE + tied embeddings + length-curriculum + dropout 0.1-0.2 + weight decay 0.1). Establish the BPC floor that the hybrid must approach. This is the cheap decisive test for whether the recapture gap is trunk-stack or HD-seam.
- Tier hint: cheap (laptop CPU < 2hr likely, per USER policy super-fast on laptop, heavier remote).
- Why now: HEADLINE is "gap likely dominated by trunk-stack basics"; this is the load-bearing measurement that distinguishes trunk-stack failure from HD-seam failure.

### Anchor 2 -- Length-curriculum recapture variant
- Anchor pointer: research note section (e) Tier-1 item 2.
- Substrate-product reading: same as Anchor 1 but with explicit length-curriculum stages (short ctx -> long ctx). Empirically the highest-leverage single trick for char-level small models.
- Tier hint: cheap; rerun of Anchor 1 with curriculum schedule applied.
- Why now: if Anchor 1 alone falls short of HARD-PASS, Anchor 2 is the next-cheapest single-knob escalation.

### Anchor 3 -- HD-as-chunk-pooler hybrid (architectural reposition)
- Anchor pointer: research note section (b) STAGE 2; section (e) Tier-2 item 3.
- Substrate-product reading: take the trained Anchor 1 backbone and inject HD/FHRR binding as a chunk-pooler between layers 2 and 3 (replace 1 transformer block with circular-convolution bind-and-bundle of k characters -> 1 chunk hypervector; attend at chunk level). Architectural precedent: Kim 2016 CharCNN, Charformer GBST, CANINE down-sample, MEGABYTE patch.
- Tier hint: medium (architectural change requires fresh training run).
- Why now: if Anchor 1 establishes a healthy trunk-stack baseline, this is the cleanest test of "does HD wire-in degrade or preserve BPC."

### Anchor 4 -- Resonator-decoder auxiliary loss
- Anchor pointer: research note section (e) Tier-2 item 4.
- Substrate-product reading: add resonator-decoder auxiliary loss aligned to character n-gram bundles; supplies symbolic-recovery training signal. Precedent: Hersche 2023 NVSA back-end; Frady-Sommer 2020 factorization.
- Tier hint: medium (training-loop modification).
- Why now: addresses "HD decoder is not extractable bottleneck" HARD-FAIL prediction; auxiliary loss is the cleanest way to test that.

### Anchor 5 -- N-sweep / binding-variant rescue (CONDITIONAL on 1-4 underperforming)
- Anchor pointer: research note section (e) Tier-3 item 5.
- Substrate-product reading: if HD seam remains lossy after Anchors 1-4, raise N from 1024 -> 4096 OR switch binding from FHRR to MAP/BSC. Per USER-LOCKED rule [[feedback-measured-bounds-are-method-config-contingent-not-fundamental]] the capacity envelope is method/config-contingent; the rescue is to widen the config envelope.
- Tier hint: heavy (multi-config sweep, remote desktop per USER compute policy).
- Why now: structural rescue; only fire if 1-4 do not close the gap.

---

## Pre-registered HARD-PASS / HARD-FAIL bands (research-side, exp_dev refines)

HARD-PASS (any ONE triggers escalation):
- Anchor 1 vanilla baseline BPC <= 1.50 on Shakespeare (<100K params).
- Anchor 3 hybrid hybrid_BPC <= 1.70 (within +0.20 of Anchor 1 baseline) -- proves HD seam non-pathological.
- Anchor 3 replaces self-attention block at >25% parameter savings without raising BPC by >0.10.

HARD-FAIL (any ONE refutes that-line architectural choice):
- Anchor 1 vanilla baseline BPC > 2.50 on Shakespeare: trunk hyperparameters mis-specified; HD discussion premature.
- Anchor 3 hybrid_BPC > 3.00 even AFTER healthy Anchor 1: HD seam fundamentally lossy at N=1024; trigger Anchor 5.
- Anchor 4 resonator-decoder auxiliary loss does NOT improve hybrid_BPC after 10 epochs joint training: HD output decoder is not extractable bottleneck.

Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: P(Anchor 1 HARD-PASS) deflated 0.70 -> 0.50; P(Anchor 3 HARD-PASS) deflated to 0.35; novel-synthesis HD-as-bottleneck capped at 0.45.

---

## Context pointers (paths, not summaries)

- notes/research_charLM_HD_hybrid_recapture_3x_2026-06-17.md -- this drill's source research note.
- notes/substrate_capability_map.md -- current cap_map; check Tier-6 charLM row.
- hdlab/ -- substrate implementation directory; HD binding primitives.
- verification/ -- baseline test harness; charLM Tier-6 Shakespeare verifier.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke.
- Smoke gate per exp_dev role contract.
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance.
- Queue routing per USER compute policy: super-fast on laptop, heavy on remote desktop.
- Ship via tools/orchestrator/queue_add.sh.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code (5 = post-ship verification failed).
- status_log entry per anchor with plain_language + importance.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, exact HARD-PASS / HARD-FAIL band tightening, queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, ordering of Anchors 1-5. Research provides anchor POINTERS + cheap decisive test + initial HARD bands only. If exp_dev wants to start with Anchor 2 (curriculum) instead of Anchor 1 (no-curriculum) as the cheaper kill-switch, that is exp_dev's call.

---

## Filed by

Research sub-agent, 2026-06-17, post 3x deep drill (24 verified citations across 3 angles). Hand-off ready for /exp_dev notes/exp_dev_handoff_research_charLM_HD_hybrid_recapture_2026-06-17.md dispatch when pause flag clears.
