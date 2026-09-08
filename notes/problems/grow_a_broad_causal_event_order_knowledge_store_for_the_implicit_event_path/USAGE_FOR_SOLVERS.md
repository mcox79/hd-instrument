# USAGE — the broader causal/event-order store (ready to test with, 2026-09-08)

The broader glass-box implicit-event **order** store is built and on disk — no rebuild needed. It re-mines
98,161 ROCStories through the tense-agnostic detector into **454,129 ordered verb-pairs** (seed had 177,800) and
lifts TRACIE implicit-event ordering **0.5296 → 0.5655 (+0.036 CI-sep)**, coverage 0.29 → 0.607 (validated 8/8;
shuffled-order twin loses).

## Load + query (drop-in for the seed store, via the landed hdlab organ)
```python
from hdlab.temporal_script_schema import TemporalScriptSchema as TSS
S = TSS.load("data/exp_broaden_causal_order_store_v1/chains_broad.json")   # 454,129 pairs
# WordNet-lemmatized variant: data/exp_broaden_causal_order_store_v1/chains_broad_wn.json
S.order("hold", "hand")     # -> 'before'  (hold the paper before handing it)
S.order("wake", "sleep")    # -> 'after'   (wake after sleep)
S.p_before("buy", "pay")    # -> 0.67      (directional prob in [0,1]; None if uncovered)
```
- `order(a,b)` → `"before"` / `"after"` / `None` (abstains when uncovered). `p_before(a,b)` → the directional
  probability — threshold it for a strength-gated override on the iconicity default. Keys are **verb lemmas**
  (the organ lemmatizes the token you pass).
- Richer store with the consolidation-gate admission + a confidence/SAT operating-point dial:
  `experiments/_causal_order_store.OrderStore` (same `.order(a,b)` interface). The raw `chains_broad.json` counts
  above reproduce the headline.

## Honest scope — do NOT over-read it
- This is the **context-free SCRIPT PRIOR** (Schank-Abelson canonical order): right (~0.61–0.68 per covered pair)
  when a story follows its script, wrong on story-specific **deviations** (falls *then* stands). Closing that gap
  needs reading the specific story's context — a categorically deeper mechanism, not a store fix.
- **Located negatives (do not redo):** transitive closure (coverage up, tail-accuracy → chance); a causal-cue
  directional blend (+0.001; ROCStories is connective-sparse).
- The reasoner's `SCRIPT_M_MIN` is the confidence/coverage dial (higher margin → higher per-pair accuracy, lower
  coverage).

## Remote runs
The asset is under `data/` (gitignored) — present on the shared repo machine. For a **remote** dispatch, declare
`# KB_REFERENT: data/exp_broaden_causal_order_store_v1/chains_broad.json` so it ships.

*(Rebuild from source if ever needed: `experiments/exp_broaden_causal_order_store_v1.py` — re-mines ROCStories
through the tense-agnostic front-end + the consolidation gate.)*
