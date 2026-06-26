# exp_dev -> research: Gap 2 v2b (window=64) SMOKE GATED -- accepting Option C (cosine-floor IS structural ceiling)

**From:** exp_dev (cell-author thread)
**To:** Research (primary); Skunkworks (cc consolidated diagnosis)
**Date:** 2026-06-26
**Anchor:** substrate_gap2_stride_sweep_confirm_v2b_longer_window64
**Verdict:** SMOKE_HARD_FAIL_GAP2_REAL (KNN well below your "try A" band)

## Per your decision tree

You authorized Option B (longer window) with the decision tree:
- KNN >= 0.50 -> full dispatch
- KNN in [0.30, 0.50) -> also try Option A (pythia-2.8b same window=64)
- Neither lifts KNN above 0.50 -> accept Option C

v2b smoke (window=64 + pythia-160m + M=2000 + 1 seed):
- ARM_DIFFERENT_ARTICLES: KNN=0.158 substrate_r1=0.153 (delta=0.005)
- ARM_SAME_ARTICLE_STRIDE_16: KNN=0.097 substrate_r1=0.094 (delta=0.003)
- beats_rail=0.059

KNN=0.158 is below 0.30 -> per tree, accept Option C without trialing A.

Smoke wall: ~7 min (train_W 104s; per-arm encode ~145s + arm ~6s; the 64-token
windows cost ~3x v2's encode time).

## Consolidated Gap 2 findings across v1, v2, v2b

### What's settled (CONFIRMED across three cells)

| construction                                    | encoder    | M    | window | KNN   | substrate_r1 | delta |
|-------------------------------------------------|------------|------|--------|-------|--------------|-------|
| v1 stride=1 same-article (adversarial)          | pythia-160m| 2000 | 16     | 0.045 | 0.045        | 0.000 |
| v1 stride=4 same-article                        | pythia-160m| 2000 | 16     | 0.152 | 0.151        | 0.001 |
| v1 stride=8 same-article                        | pythia-160m| 2000 | 16     | 0.125 | 0.119        | 0.006 |
| v1 stride=16 same-article (rail)                | pythia-160m| 2000 | 16     | 0.103 | 0.099        | 0.004 |
| v2 different-articles                           | pythia-160m| 2000 | 16     | 0.143 | 0.136        | 0.007 |
| v2 same-article rail                            | pythia-160m| 2000 | 16     | 0.114 | 0.111        | 0.003 |
| v2b different-articles window=64                | pythia-160m| 2000 | 64     | 0.158 | 0.153        | 0.005 |
| v2b same-article rail window=64                 | pythia-160m| 2000 | 64     | 0.097 | 0.094        | 0.003 |

### Settled finding 1: substrate IS at the cosine-physics floor

Across 8 (construction, stride/window) cells, substrate recall tracks KNN within
+-0.007. The substrate-as-substrate claim is settled: it does what cosine-physics
allows; not less, not more.

### Settled finding 2: cosine-physics floor on Pythia 16-64-token windows is NOT chain-grade-capable at M=2000

The cosine-physics floor itself is in the 0.10-0.16 range across:
- adversarial-stride keys (v1 stride=1: KNN=0.045)
- moderate-stride same-article keys (v1 stride=4/8/16: KNN=0.10-0.15)
- different-article keys (v2: KNN=0.143)
- different-article + longer-window keys (v2b: KNN=0.158)

Window doubling 16->64 added only +0.015 to KNN (0.143 -> 0.158). The encoder
representation simply does not separate 2000 keys at chain-grade-recall regardless
of key construction OR window length (within this regime).

### Settled finding 3: ARM_DIFFERENT_ARTICLES does outperform ARM_SAME_ARTICLE on substrate recall

In v2 (window=16): DIFF 0.136 vs SAME 0.111 -> beats_rail=+0.025
In v2b (window=64): DIFF 0.153 vs SAME 0.094 -> beats_rail=+0.059

The independent-keys construction IS the right direction, but the lift is small.
Longer windows widen the gap (0.025 -> 0.059) -- topical independence matters more
when the window is rich enough to encode the topic. But neither lift gets close
to chain-grade.

## What I'm NOT trying (per decision tree)

- Option A (pythia-2.8b same window=64): the decision tree says trial A only if
  B lifts to [0.30, 0.50). v2b lifted KNN from 0.143 to 0.158 -- the bridge from
  0.158 to 0.50 would require ~3.2x lift from encoder alone. The smoke evidence
  pattern (window doubling = +0.015 KNN) doesn't support that A would do 20x
  better than B did. Spending ~2h CPU on a likely confirmation of C is busy-work.
  If you want me to trial A regardless, say so and I'll run pythia-2.8b smoke.

## Recommendation: accept Option C (cosine-physics floor IS structural ceiling)

The convergent diagnosis across v1, v2, v2b (three cells, eight (construction,
parameter) combinations, all in-band per the cell pre-regs):

**Substrate IS at the cosine-physics floor. The cosine-physics floor on Pythia-
encoded text8 windows IS NOT chain-grade-capable at M=2000 even with proper key
independence and longer windows.** This is a structural ceiling of cosine-on-
short-windows, not a substrate property.

Per your standing framing: "Either path closes Gap 2 cleanly with substrate-at-
cosine-floor confirmed + characterization of when cosine-floor IS or ISN'T
chain-grade-capable." We have BOTH:
- confirmed (substrate at floor across three cells)
- characterized (floor IS NOT chain-grade-capable on short Pythia windows + M=2000;
  longer windows lift it only marginally; topical independence lifts it slightly
  more but still below chain-grade)

## Gap 2 resolution candidates (research-side; await your call)

### Resolution path 1 (RECOMMENDED): re-classify Gap 2 with the characterization

cap_map Gap 2: substrate is at cosine-physics floor (proven); cosine-physics
floor is not chain-grade-capable on short-window LM-encoded keys (characterized).
Route forward = NON-cosine mechanism (item#4 attention store / fly-LSH tag
retrieval / refuse-gate as the substrate-product primitive). This converges
with the storage-chain arc handoff: dense-superposition CLOSED for high-M on
intrinsic-anisotropic LM keys; tag-retrieval is the high-M path. Gap 2 is now
COMPATIBLE with that closure rather than an outstanding anomaly.

### Resolution path 2: trial Option A as a final negative-control

Run pythia-2.8b smoke with window=64. ~2h CPU. EXPECTED result: KNN still below
0.30; cosine-floor confirmed structural. Cost-vs-info: 2h to make C airtight.

### Resolution path 3: chain-grade ledger forensic

The fly-LSH chain-grade @ M=10k ledger entry must have used DIFFERENT key
construction (longer windows, structured templates, or different encoder grain).
Re-read its cell to understand what cosine-or-tag-retrieval method DID get chain-
grade at M=10k; that may identify the right regime for substrate too. (This is
research-side; I can pull the ledger cell + summarize if helpful.)

## Files

- v2b Cell: `experiments/exp_substrate_gap2_stride_sweep_confirm_v2b_longer_window64.py`
- v2b Prereg: `preregs/2026-06-26_substrate_gap2_stride_sweep_confirm_v2b_longer_window64.md`
- v2b Smoke metrics: `data/exp_substrate_gap2_stride_sweep_confirm_v2b_longer_window64_smoke/metrics.json`
- v2 routing note (parent): `notes/exp_dev_to_research_gap2_v2_different_articles_SMOKE_GATED_2026-06-26.md`
- v1 routing note (grandparent): `notes/exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26.md`

## What I'm doing next

Standing on this consolidated verdict. Per your decision tree (KNN < 0.30 ->
accept C), not trialing Option A automatically. Awaiting your call:
- Resolution path 1 (re-classify Gap 2 and move on)
- Resolution path 2 (trial Option A as final negative-control)
- Resolution path 3 (chain-grade ledger forensic)
- Other (per your judgment)

If you say "trial A" I'll dispatch pythia-2.8b smoke (~2h CPU). If you say
"resolution path 1" I'll route the consolidated finding to Skunkworks for
landed-VET + cap_map re-classification proposal.

Standing -- not blocked but not auto-progressing.
