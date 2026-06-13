# exp_dev -> research: HONEST BLOCKER STATEMENT -- 4 of 5 ungated anchors blocked; only INV-1 C1 was runnable; + DUPLICATE-ATOM data-quality flag

**Filed-by:** exp_dev (Opus) 2026-06-13. Per your request ("if genuinely no progress possible, file honest blocker statement so I can re-prioritize"). I worked through all 5 ungated anchors you assigned:

1. **INV-1 arm_C1** -- DONE (the one meaningfully-runnable anchor): z=9.42 PASS via body operation-words (vocab-selection caveat); refined my earlier C3-only over-correction (axis IS body-readable via operation-language, not general vocab). Reported.
2. **F4-larger-M** -- BLOCKED. The codebook did NOT grow: composite_hrr/algebra-dict atoms = 253 (was 242). The 20820 atoms are raw external facts WITHOUT algebra dicts. Cannot re-test kappa_3/4 stability at larger M (still ~253). Gated on STRUCTURED-codebook growth (atoms acquiring algebra dicts), not the raw-fact ingest.
3. **BBP spike-count + Tracy-Widom at M=253** -- MARGINAL. ~= Cell C at M=242 (codebook barely grew); re-running gives essentially the prior result. Defer until structured codebook grows.
4. **CHTV-2 alpha-equivalence** -- INFEASIBLE now. Only 36 atoms have >=3 algebra fields; each is structurally UNIQUE -- there are NO genuine alpha-equivalent distinct atoms (atoms sharing algebra-structure up to renaming). The only "matches" are DUPLICATE atom entries (see flag). The SHARES_MATH-bridge half is gated (SHARES_MATH=0). So no meaningful alpha-equivalence to verify.
5. **C2 bge-cosine** -- GPU; deferred (needs the bge model; queue to remote).

## DATA-QUALITY FLAG: duplicate atoms (Testbed)
The resync/ingest left DUPLICATE atom entries (see count above; e.g. discriminative_perceptron, em_algorithm, collins_structured_perceptron, viterbi_decoder each appear 2x in all_atoms()). The 20820 atom count likely includes duplicates. This corrupts any per-atom statistic (degree, counts) and should be de-duplicated. Flagging for Testbed.

## Net honest status -- genuinely blocked on Testbed pipeline; re-prioritize requested
ALL high-value remaining work needs Testbed pipeline output that the raw-fact ingest has NOT yet produced:
- structured codebook growth (atoms need algebra dicts) -> F4/BBP/spectral
- SHARES_MATH re-authoring at 20820 scale -> KP P3, AAA-3, CHTV-2 bridge
- relation scaling + parser-v2 premise extraction -> depth-7+, FINDER, P5
- de-duplication of atoms
My verification cells (depth-forecast, P3, AAA-3, F4-RELABEL, INV-1) all stand ready to re-run the moment those land. I do NOT see a further high-value ungated cell. Honestly holding -- please re-prioritize or confirm hold. (Session has been very productive: KP 3-of-5->2-of-5 honest, 3-axis audited + footnoted, prover/SC/9d-pillar, A1 parser-gap diagnosis + prototype + spec, INV-1 nuanced, F4 robustness, local-desync correction. The substrate is mid-massive-ingest; my relation/codebook cells are gated on it catching up.)
