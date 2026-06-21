# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: continual-write lever de-risk RAN (heat-safe CPU) -> GREEN (genuine cost) + the DISTINCTIVE-AXIS sharpening. 2nd storage-chain make-or-break de-risked. Substantive.

**Context:** continuing the de-risk series (USER "surely something to work on"). Same heat-safe CPU-synthetic pattern as the flagship probe. tools/skunkworks_probe_continual_write_genuine_cost_v1.py. Hopfield store W=sum v_i k_i^T + codebook-cleanup; incremental writes; important-old set re-queried throughout (my C1).

## SELF-CATCH first (verify-the-referent on my own probe)
v1 (N=512/M=1500) showed write-all recall=1.0 -> I did NOT report "lever->MM" off it: write-all NOT forgetting at 3x nominal capacity is implausible = the probe hadn't CROWDED (N=512 has too much capacity; cleanup too forgiving). Failed the can-fail check -> fixed the regime (N=256, M-sweep) to LOCATE genuine crowding. (Symmetric-verify: the flagship probe discriminated; this one needed a harder regime first.)

## RESULT v2: GREEN -- genuine cost LOCATED + cap-aware beats BOTH
M-sweep at N=256 (write-all all-active recall = the forgetting onset):
| M | write-all all-active | FIFO imp-old | cap-aware imp-old | write-all imp-old |
|---|---|---|---|---|
| 1200 | 0.975 | 0.000 | 1.000 | 0.956 |
| 2400 | **0.644** | 0.000 | 1.000 | 0.622 |
| 4800 | 0.188 | 0.000 | 1.000 | 0.256 |
At M=2400 (crowding): **write-all FORGETS (0.62, crosstalk corrupts) + FIFO FAILS (0.00, drops important-old) + cap-aware HOLDS (1.00).** cap-aware beats BOTH naive in a regime where EACH genuinely fails = exactly my SCHEMA-VET C1 + lever-design 99392cca bar. The genuine cost EXISTS (write-all forgetting is real past capacity; it's NOT a LEVER-1.5-style no-cost).

## THE DISTINCTIVE-AXIS SHARPENING (the honest caveat -> changes the cell design)
My probe's cap-aware PROTECTS-BY-LABEL (it's TOLD which facts are important-old, never evicts them). That's circular -- it proves "IF you can identify important-old, protecting-them beats FIFO," which is almost by-construction. **The REAL lever's distinctive challenge is INFERRING importance WITHOUT a label** -- the policy must infer which facts are still-needed (recall-error / access-frequency / age-weighted proxy) and protect THOSE. So the cell's chain-grade bar isn't "does protect-important beat FIFO" (yes, trivially) but **"does a LABEL-FREE importance-inference policy (recall-error/access proxy) beat FIFO + write-all?"** That's the genuine selection problem. Design the cell's cap-aware arm to INFER importance, and compare vs an oracle-protect upper bound.

## Net (both storage-chain make-or-breaks now de-risked on CPU)
- Flagship (sparse-projected-KV): decrowding SURVIVES sparse = GREEN (764c16be).
- Continual-write: genuine forgetting-cost EXISTS + cap-aware-with-importance beats both = GREEN, **chain-grade-eligible** -- with the distinctive axis = label-free importance-inference (not protect-by-label). Build the inference policy + oracle upper-bound.
Honest limits: synthetic Hopfield+cleanup (not the real substrate-KV + a3f473dd envelope); the real crowding onset + the importance-inference efficacy need the actual cell. De-risks the make-or-break (genuine cost = YES); not a substitute for the cell.
