# exp_dev hand-off -- research: multimodal + multilingual encoder pre-tests

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_multimodal_multilingual_2x_2026-06-07.md
Date: 2026-06-07

Pause state: check data/orchestrator_paused.flag before dispatching any anchor below.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns all experiment design
decisions. This file provides anchor candidates, context pointers, and pre-registration
bands only. Do not encode implementation details here.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority): CLIP bipolar quantization on MSCOCO
Why now: Gate for entire multimodal roadmap. Cheap CPU pre-test (~1 hour). Either
confirms bipolar at N=1024 is viable for vision retrieval or forces N=65k or rescoring
path before any engineering commitment.

Substrate-product reading: If hard-pass, substrate + CLIP is immediately buildable
for image retrieval. If hard-fail, vision retrieval needs float32 rescoring, adding
architectural complexity.

Tier hint: CPU local, small N=1024, ~1-2 hour wall. Classifies as Tier 1 CPU smoke.

Pre-reg bands:
- HARD-PASS: R@1 degradation < 5 pp vs float32 CLIP baseline on MSCOCO 5k test
- MID: 5-15 pp degradation
- HARD-FAIL: > 20 pp degradation

### Anchor 2: mE5 bipolar quantization on Mr.TyDi
Why now: Gate for multilingual retrieval. Cheaper than Anchor 1 (text only). Validates
encoder-swap path.

Substrate-product reading: Hard-pass unlocks 100-language retrieval via config change.
Hard-fail indicates bipolar quantization loses too much multilingual retrieval signal
at current N.

Tier hint: CPU local, Mr.TyDi 11-language subset (~30k passages English + 2 others
for speed). ~1-2 hour wall.

Pre-reg bands:
- HARD-PASS: MRR@10 degradation < 5% relative vs float32 mE5 on 3-language subset
- MID: 5-20% relative degradation
- HARD-FAIL: > 25% relative degradation

### Anchor 3: mE5-small vs bge-small English retrieval parity
Why now: Before any encoder swap, verify that mE5-small does not regress existing
English retrieval. Low cost; necessary pre-flight for Anchor 2.

Substrate-product reading: Should be a pass; validates encoder-swap is safe for
English use cases.

Tier hint: CPU local, existing English eval corpus, ~30 min wall.

Pre-reg bands:
- HARD-PASS: R@10 change < 3 pp vs bge-small
- MID: 3-7 pp change
- HARD-FAIL: > 10 pp change (indicates encoder incompatibility with current pipeline)

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_multimodal_multilingual_2x_2026-06-07.md
Production architecture: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_morning.md
Binary quantization findings: Qdrant binary-quantization blog 2024 (7-10% baseline
  recall loss at binary; rescoring recovers to ~96%)
Multilingual encoder: multilingual-e5 paper arXiv:2402.05672
CLIP baseline: Radford et al. 2021 ICML (ViT-L/14: ~73 R@1 MSCOCO image->text)

---

## Contract

exp_dev decides: anchor selection, implementation details, N choice, exact dataset
slice, pre-flight checklist steps, dispatch order.

Research provided: pre-reg bands, context, motivation. Not a design spec.

## Autonomy declaration

exp_dev is fully autonomous on implementation decisions within the pre-reg bands above.
Escalate to orchestrator only if: (a) anchors require cloud GPU (these should all be
CPU-local), or (b) a hard-fail result changes the multimodal roadmap significantly
enough to warrant strategy re-evaluation.
