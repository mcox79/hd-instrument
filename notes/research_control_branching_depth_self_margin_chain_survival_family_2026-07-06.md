# Prep-drill: control-branching-depth self-margin -- it IS the chain-survival order-statistic family (buildable MM; CG needs the SR-SNR derivation)

Date: 2026-07-06. Director main-thread drill (zero new trials, verified off exp_pfc_gate_branching_depth_entropy_grid_v1
structure + its landed FULL metrics). Resolves the frontier-map's last self-predictable-capability candidate
(research_capability_self_margin_frontier_map_2026-07-06 row: "control branching-depth, HARDER, needs horizon-SNR
derivation first, P0.35"). Verdict: it does NOT need a NEW horizon family -- it is the SAME chain-survival
order-statistic as the reasoning-depth CG self-margin, but the per-gate SNR lacks a closed form -> semi-empirical MM.

## What the cell is (verified off-disk)
exp_pfc_gate_branching_depth_entropy_grid_v1 (FULL = HARD_PASS): a FLAT Go/NoGo control gate collapses at high
DECISION-ENTROPY = log2(n_ops)*depth over an n_ops in {2,3,4} x depth in {4,6,8} grid; a HIERARCHICAL-OPTIONS gate
(decompose the depth-d chain into low-horizon segments) recovers the collapse. spearman(flat, -depth) = -0.79.
gamma / SR-horizon is INERT (smoke-proven) -- collapse is a BRANCHING-FACTOR story (Hick 1952 accuracy~log2(N);
Usher-McClelland 2001 LCA), NOT a temporal-discount story. Per-gate decision = rank/argmax over n_ops options
(gate fires on reach_rank > 1/n_ops + margin).

## The mapping (this is the drill's core insight)
A depth-d control chain SURVIVES only if ALL d gating decisions are correct. Each gate = an extreme-value
order-statistic over n_ops competitors with per-gate margin mu. If gates are ~independent:
   P_chain_survive(n_ops, d) = P_gate(n_ops, mu)^d,   P_gate = E_z[ Phi(mu+z)^(n_ops-1) ]  (GH64, the SAME kernel
   already CHAIN_GRADE for RNS decode / FHRR capacity / reasoning-depth).
Consistency check with the landed result: -log(survival) ~ d * (-log P_gate). Under Hick (error ~ log2(n_ops)) this
is ~ d*log2(n_ops) = the DECISION-ENTROPY the cell already found predictive. So the entropy predictor is the
first-order shadow of the exact chain-survival order-statistic. => control-branching-depth is the SAME FAMILY as the
reasoning-depth CG self-margin, with competitor count = BRANCHING FACTOR n_ops (small, 2-4) and chain length = depth.

## Why it is MM not CG (the honest bound)
The cell explicitly flags crlb_n/a: the accuracy-closure discriminator "has no single closed-form noise floor". The
per-gate margin mu is a LEARNED successor-representation (SR) reachability, not a clean codebook decode -- so mu is
not available in closed form (unlike RNS/FHRR/reasoning-depth where mu came from an exact decode margin). Therefore:
- BUILDABLE self-margin = SEMI-EMPIRICAL: MEASURE the per-gate margin mu at SHALLOW depth (d=1 or the segment length),
  then PROJECT the deep collapse via P_gate(n_ops, mu_hat)^d and check it predicts the flat depth-collapse across the
  (n_ops, depth) grid. This is exactly the reasoning-depth v1 pattern (empirical sigma -> order-statistic) which was
  MEASURED_MECHANISM before the exact v2. Expected tier here: MM (P_deflated ~0.5 for MM, the mechanism is sound and
  the grid already exists to test against).
- CG path (the P0.35 hard part) = DERIVE the horizon-dependent SR-reachability SNR mu(h) from the SR structure so the
  projection is parameter-free. Separate, harder theory step; do NOT gate the MM build on it.

## Dispatch recipe (ready; hold until an agent slot frees -- currently 5 in flight)
- NEW cell: fit the per-gate order-statistic margin mu_hat from the SHALLOW-depth flat-gate accuracy (per n_ops),
  then predict flat_gonogo(n_ops, depth) = P_gate(n_ops, mu_hat)^depth across the FULL grid; compare predicted-vs-
  observed collapse. Firing control: shuffle the gate scores (destroys the margin) -> prediction should break.
- Pre-reg bands: predicted-vs-observed survival within tolerance ACROSS the (n_ops,depth) grid, and BEAT the Hick-
  entropy first-order predictor (the order-statistic should be tighter than log2(n_ops)*depth). Multi-seed >=5.
- Reuse the reasoning-depth GH64 order-statistic kernel. Score against the LANDED branching-depth grid (no new control
  training needed if the per-(n_ops,depth) flat accuracies are persisted -- verify they are before dispatch).
- FRAMING: monitor-not-control (predicts its own usable control depth; never edits the gate). Narrow glass-box step.

## Where this sits
Self-margin family = 3 CG INTERIOR (RNS/FHRR/reasoning-depth) + comprehension MIDDLE (PR-revived, language frontier) +
generation (dispatched this session) + NOW control-branching-depth mapped as a 6th capability = chain-survival family,
buildable SEMI-EMPIRICALLY (MM). => the self-margin generalization spans DECODE (RNS/FHRR), REASONING (depth),
LANGUAGE (comprehension/generation), and CONTROL (branching-depth) -- a systematic capability-frontier, monitor-not-
control, honestly tiered (CG where decode is clean/closed-form, MM where the margin is learned/no-closed-form).
Composes with research_reasoning_depth_self_margin_closed_form and research_capability_self_margin_frontier_map (2026-07-06).
