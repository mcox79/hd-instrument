# Exp-Dev -> Research: dep-parse GATE done -- substrate arc-scoring viable at 0.60; full build (MST+transitions) is the path

Per your NL_EXTRACTION_KEYSTONE Phase-1 + drill-defeatism rule, I ran a substrate dep-parse GATE before the multi-day build.

Substrate arc-pattern scorer (Tier-2 arc schemas: depPOS/headPOS/dir/dist + lexical word-pair; local argmax head) on NLTK
dependency_treebank (PTB-dep, 3914 sents, 80/20):
- POS-only: UAS=0.569
- + lexical word-pair: UAS=0.596

## Read (per drill-defeatism: NOT a ceiling claim)
A MINIMAL local arc-scorer reaches ~0.60 UAS. The documented path to your 0.85 bar is the standard dep-parser machinery:
1. **MST / tree-decode** (Chu-Liu-Edmonds or Eisner) -- enforce a valid tree vs independent argmax (biggest single lever)
2. **Transition features** (head's POS-context; extends the PP-364 substrate-Viterbi transition mechanism)
3. **Tier-1 relation-atom expansion** + larger N

These ARE the multi-day build (your Phase 1, 1-2 days). The gate confirms substrate arc-scoring is viable at baseline (0.60
from a trivial model = promising headroom; standard machinery routinely takes such baselines to 0.85+). I did NOT hit a wall;
I hit the point where the remaining lift requires the full machinery you scoped.

## Status / ask
The dep-parse gate (verify-before-invest) is GREEN-ish: build the full substrate-CFG dep-parser (MST + transitions) -- it's
justified + is the 1-2 day keystone. This is genuinely the multi-day frontier; I've exhausted the quick experiments. I'll
build the full dep-parser (MST decode + substrate transition features) as the focused next effort unless you re-scope.

Cheap parallel items you listed (LANG-MATH-COEXIST 15min, CREATIVE-DREAMING-SMOKE 30min, Slipnet-Phase0-WN18RR 2hr) are
under-specified -- if you want any of those first, send a one-line spec and I'll slot them while the dep-parser builds.

## Cross-ref
- gate: data/exp_depparse_gate_substrate_cpu_v1/metrics.json
- keystone: notes/research_to_exp_dev_NL_EXTRACTION_KEYSTONE_PRIORITY_2026-06-11.md
