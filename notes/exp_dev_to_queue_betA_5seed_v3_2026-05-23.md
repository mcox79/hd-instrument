# Exp Dev -> Queue: Bet A 5-seed v3 (N=32768 OOM-safe respec)

**Filed**: 2026-05-23
**Trigger**: GPU idle >10 min; betA_continual_edit_5seed_v2 remote FULL FAILED
  (cycle 175 Sweep A: N=65536 OOM on 8GB GPU even at M_init=1024)

## What was built

name=wave14_betA_continual_edit_5seed_v3
script=experiments/exp_wave14_betA_continual_edit_5seed_v3.py
prereg=preregs/2026-05-23_wave14_betA_continual_edit_5seed_v3.md
timeout=3600

## Why v3 is new work (not re-pick)

v2 FAILED on remote = OOM at N=65536 (W alone is 8.6 GB bf16 > 8 GB VRAM).
v3 re-specs to N=32768: W=2.15 GB bf16; fp32 edit peak ~4.3 GB; total <5 GB.
M_init=4096, M/N=0.125 -- same operating ratio as cycle 172 v2 RESCUED point.
This is a genuinely new measurement (8x scale vs smoke N=4096; not a v2 re-run).

## Smoke result

BETA_5SEED_PASS: edit_acc=1.000 kept_acc=1.000 sd=0.000 at N=4096 M_init=512
M/N=0.125 (2 seeds). Metrics validated. ASCII-only confirmed.

## Substrate axis probed

Bet A editable memory (capability class 2): does 5-seed statistical confirmation
of edit_acc >= 0.95 AND kept_acc >= 0.95 hold at N=32768 with M/N=0.125?
This is a FULL-scale confirmation at 8x the standard substrate operating N,
using the same anti-Hebbian erase + insert protocol as all prior Bet A work.

## Decision rationale (option 1 of 4)

Option 1 (betA v3): chosen because:
- Bet A's capability class 2 status is CONTESTED (v2 smoke PASS vs remote FULL FAIL)
- The v3 OOM-safe re-spec resolves the ambiguity at a validated N
- Substrate-product capability class 2 is highest-priority unresolved item
- v3 design is minimal change (N re-spec only; same protocol, same seeds)
- Smoke passed locally in 12s; FULL expected ~25-40 GPU-min at N=32768

Options 2-4 (cross-application, scope expansion, envelope expansion) deferred:
the contested cap-2 status is higher urgency than forward expansion. Per
[[feedback-strategy-shore-up-capabilities]]: shore up contested capabilities
before expanding scope.
