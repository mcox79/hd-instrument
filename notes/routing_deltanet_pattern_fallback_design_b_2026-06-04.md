# ROUTING -- DeltaNet-pattern hybrid as fallback (substrate-retrieval + gradient-trained readout)

**From:** Research session
**To:** Orchestrator (primary)
**Date:** 2026-06-04
**Type:** Future-cycle LLM probe (Orchestrator routes to Testbed; dispatch ONLY if joint D+H HF)

---

## Capability question

Can a substrate-as-memory-retrieval-layer + gradient-trained-readout hybrid (DeltaNet pattern; Design B from META 3x+ drill) train a tiny LM at rung-1 scale, providing a conservative fallback if the more aggressive joint D+H architecture fails?

## Pre-reg HP/MID/HF bands

**HARD-PASS:**
- >= 4/5 seeds converge to val_loss < 3.5 bits/char by step 500
- Hybrid beats Hebbian-only baseline by >= 10% on val_loss
- Substrate retrieval cache stays within capacity bound at all times
- Gradient-trained readout converges (no instability from substrate-readout interaction)

**MIDDLE:**
- 2-3 / 5 seeds converge
- 5-10% gain over Hebbian baseline
- Some capacity warnings but recoverable

**HARD-FAIL:**
- 0-1 / 5 seeds converge OR
- No gain (or negative gain) vs gradient-only baseline (showing substrate-retrieval adds no value) OR
- Substrate-readout interaction destabilizes training

## Resource

Local CPU runner (rung-1 scale).

## Cost ceiling

$0 (CPU). Wall ~30-60 min per condition; 3 conditions x 5 seeds.

## P_deflated

**Conditional on joint D+H HF:** 0.50 (per META 3x+ drill; DeltaNet 1.3B precedent already exists at NeurIPS 2024; rung-1 success well-supported by published precedent at scale).

If joint D+H HP: this fallback NOT NEEDED; routing parked.

---

## What this is (plain language)

The META 3x+ drill ranked three bypass designs for substrate-as-training-mechanism feasibility:

| Design | Pattern | P_deflated | Precedent |
|---|---|---|---|
| A | Add contrastive phase | 0.50 | RBM (Hinton 1985) |
| B | Substrate retrieval + SGD readout | 0.50 | DeltaNet 1.3B NeurIPS 2024 |
| C | Single-channel aggregation | lower (only fixes 1 of 3) | various MTL |

The joint D+H architecture (multiplicative gating + cf-RPE; shipped separately) is more aggressive but more brain-faithful. P_deflated 0.40-0.50.

This routing pre-stages **Design B (DeltaNet pattern)** as a CONSERVATIVE FALLBACK. It has published precedent at 1.3B LM scale; lower architectural novelty risk. Only dispatched IF joint D+H lands HF.

Architecture:
- Substrate stores patterns as discrete-state memory (no gradient training of substrate)
- Gradient-trained MLP / linear readout reads from substrate via attention
- LM loss back-props through readout only; substrate updated via Hebbian-class rule independently
- Like brain: hippocampus (substrate) stores episodes; cortex (readout) reads and computes

---

## Experiment design (3 conditions, 5 seeds each)

**Anchor name:** `substrate_deltanet_pattern_design_b_rung1_v1_n4096`

### Conditions

- **Arm A (gradient-only baseline):** Tiny char-LM with no substrate; standard SGD. Establishes baseline val_loss.
- **Arm B (substrate-retrieval + SGD readout):** Tiny char-LM with substrate as retrieval layer; gradient-trained readout reads from substrate via attention. Tests Design B core claim.
- **Arm C (Hebbian-only baseline):** Pure Hebbian substrate; no gradient training anywhere (matches the original substrate-trained mini LM HF). Confirms relative gain of Arm B over Hebbian.

### Substrate role in Arm B

- Substrate dimension N=4096 (continuous float32, per Grouped drill mitigation)
- Substrate stored patterns: written via Hebbian rule from training data (no gradient)
- Readout: gradient-trained MLP reads top-k retrieved substrate patterns via attention
- LM final logits computed from readout output
- Cross-entropy loss back-props through readout ONLY (not into substrate)
- Substrate updated via online Hebbian rule (separate from gradient pass)

### Training details

- Model: tiny char-LM, ~10k params (~5k for readout, ~5k for embedding + final layer)
- Substrate: N=4096 continuous float32 retrieval bank
- Corpus: char-level Shakespeare or simple synthetic
- Steps: 500-1000
- Seeds: 5 per condition
- Per-condition wall: ~30-60 min CPU

---

## Sequencing -- IMPORTANT

**This routing dispatches ONLY IF the joint D+H routing lands HF.**

Reason: joint D+H is the more aggressive design with potentially higher capability ceiling. If it works, this fallback is unnecessary. If it fails, this fallback provides a published-precedent-backed path forward at the same scale.

**Orchestrator hold-discipline:**
- If joint D+H lands HP -> park this routing; capability claim secured via the more aggressive design
- If joint D+H lands MIDDLE -> consider both: iterate joint D+H AND dispatch this in parallel
- If joint D+H lands HF -> dispatch this immediately; it's the de-risked path

---

## Strategic outcome

### If dispatched and HP

- Substrate-as-training-mechanism story has a published-precedent path at rung-1 scale
- Cap_map: NEW sub-property founding under substrate-as-training-mechanism row
- Validates the substrate-retrieval-plus-readout pattern (DeltaNet-class)
- Scaling path: rung-2 (4-layer char-LM), rung-3 (~100k subword-LM on laptop GPU), rung-4 (Pythia-160M; cloud-free), rung-5 (GPT-2-small) only if needed

### If dispatched and HF

- Both Design B and joint D+H refuted at rung 1
- Substrate-as-training-mechanism likely requires larger scale (>= 100k params) before any pattern works
- Falls back to Design A (contrastive phase) as next attempt OR concedes substrate-as-training is scale-dependent

---

## Discipline declarations

- Per [[feedback-routings-address-orchestrator-not-testbed]]: orchestrator primary
- Per [[feedback-small-scale-first-methodology]]: rung 1 first; tests Design B at smallest viable scale
- Per [[feedback-rescue-sketch-first-sequencing]]: this is the conservative fallback after the aggressive joint D+H
- Per [[feedback-rehabilitation-after-rejection]]: documented contingency rescue
- Per [[feedback-no-padding-experiments]]: 3 conditions discriminate gradient-only vs substrate-retrieval-hybrid vs Hebbian-only
- ASCII-only output enforced

PROT-018: anchor name `substrate_deltanet_pattern_design_b_rung1_v1_n4096` with _n4096 suffix

---

**END.**

**Orchestrator:** queue this routing as conditional. Dispatch ONLY if joint D+H rung-1 HF lands. Engineering can pre-stage scaffold (~4-6h) since substrate-retrieval + gradient-readout primitives exist; full dispatch held pending joint D+H outcome.

**Research session:** awaits joint D+H verdict; will activate this routing only if joint D+H fails.
