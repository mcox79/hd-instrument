# PROBE: loop-autonomy self-signal feasibility (2026-08-02)

Task: probe-to-aim (cheap, no big build) whether a GOLD-FREE self-signal can separate
fix-induced coref decision CHANGES that were actually correct ("keep") from ones that
were actually wrong ("revert"), BEFORE building an autonomous fix-router. The
self-improving loop (FLAG -> apply candidate fix -> measure) is engine-certified
(atom 29624) but every keep/revert call so far has been DIRECTOR-dispatched (gold-read).

Probe script (new, not dispatched, single local run):
`d:/AI/hd-instrument/experiments/probe_loop_autonomy_self_signal_v1.py`
Metrics: `d:/AI/hd-instrument/data/exp_probe_loop_autonomy_self_signal_v1/metrics.json`

Prior-work check (substrate_query.sh, per SUBSTRATE-KB discipline): queried "gold-free
self-signal fix keep revert autonomy coreference confidence margin coherence" ->
top hits are generic WordNet-level concept entries (coherence 0.4287, coreference
0.417, confidence 0.3955) from the concept KB, not prior EXPERIMENT CELLS on this
question at cosine>0.30. No prior arc cell duplicates this specific self-signal-for-
autonomy probe; genuinely new, building directly on cycle 2-3 (commits 4cc041fcd,
0c4285f52, 7bef6f740).

## The labeled set (reconstructed from disk, not hand-curated)

Reran the three cycle-2/3 fixes with traced, byte-for-byte replays of the committed
pick logic (`run_learnable_strict_cb`, `run_loop_principle_b`, `run_loop_discourse`),
each VET'd in `self_test()` to reproduce IDENTICAL predicted-id sequences to the
imported originals before trusting any signal (same discipline as the calibration
cell's instrumented-copy VET). Caught and fixed one tie-break bug in the first draft
of the decay-window replay (`_pick_decay_window`'s tie-break favors the candidate with
the LARGER `last_pos` on a score tie, not list order) via the fidelity assertion --
exactly the kind of drift this VET step exists to catch.

For every pronoun decision where the fix CHANGED the pick (pre-fix strict_cb pick !=
post-fix pick), labeled via the clean MUC-style link label (`mention_link_wrong`):
corrected (pre wrong -> post right), broken (pre right -> post wrong), or neutral
(both same truth value -- excluded from the labeled set).

Recovered exactly the counts already visible in the landed metrics:
- principle_b: 2 changed -> 1 corrected, 0 broken, 1 neutral.
- speaker_deixis: 3 changed -> 2 corrected, 0 broken, 1 neutral.
- decay_window: 26 changed -> 3 corrected, 6 broken, 17 neutral.

**N = 12 labeled instances (6 corrected, 6 broken).** Small-N aim-probe, not a powered
result -- exactly as scoped by the task.

## The three gold-free self-signals (computed pre-fix vs post-fix, delta = post - pre)

(a) **n_compatible delta**: candidate-pool size before vs after the fix's own filter.
    Only non-degenerate for filter-based fixes (principle_b, speaker_deixis exclude
    candidates); decay_window never shrinks the pool (it only re-ranks), so this
    signal is IDENTICALLY ZERO for all 6 decay_window instances -- structurally unable
    to discriminate decay_window's breaks. AUC = 0.75 (driven entirely by the
    principle_b/speaker_deixis instances).

(b) **decay-margin delta**: recency-decayed salience margin (top candidate score minus
    runner-up, `DECAY=0.7`/`WINDOW=4` from the cross-clause-discourse cell) computed
    generically over whichever candidate pool each arm actually used for its pick.
    AUC = 0.472 -- indistinguishable from chance. This is the mechanism decay_window
    ITSELF uses to pick, so its own margin does not know when it is wrong (unsurprising
    in hindsight -- an internal score being self-referential to the mechanism that
    produced it is not evidence the mechanism was right).

(c) **coherence-margin delta**: `hdlab.situation_model_accumulate.AccumulateRegister`
    role-decode margin (top1 vs runner-up over `ROLE_VOCAB`) for the picked entity's
    accumulated register at the mention's own event slot, built from that arm's FULL
    passage-level cluster assignment (same FHRR generator seed pre/post so only the
    cluster assignment moves, not the random role/idx vocab). **AUC = 0.917** -- the
    standout signal. At a threshold of 0 (post-fix coherence margin higher than
    pre-fix): rejects 5/6 of decay_window's breaks and keeps 5/6 of all 6 known-good
    corrections (the one miss is a near-zero borderline case, delta=-0.0051, on a
    speaker_deixis correction).

Combined signal (arithmetic sum of (b)+(c)) has a slightly higher RANK AUC (0.944,
because decay-margin still contributes weak-but-real ordering information across the
FULL 12-instance ranking) but a WORSE hard threshold-at-0 rule (rejects only 3/6 decay
breaks) because decay-margin's near-chance noise flips the sign of the sum on several
borderline cases. **Honest read: do not naively sum signals of very different
reliability -- (c) alone is the load-bearing, actionable signal; (b) is not currently
pulling its weight as a standalone keep/revert gate.**

## Key question: would a keep/revert rule have kept the good fixes and rejected the bad ones?

Using coherence-margin delta (signal c) alone, threshold at 0:
- decay_window's 6 breaks: 5/6 correctly REJECTED (would have prevented 5 of the 6
  regressions the decay-window arm actually shipped as a NULL/negative finding).
- All 6 known corrections (principle_b x1, speaker_deixis x2, decay_window x3): 5/6
  correctly KEPT.
- Net: 10/12 correct keep/revert calls from ONE gold-free signal with a trivial
  threshold, on the exact adversarial case (decay_window) the task singled out as
  the crucial negative to reject.

## Verdict: AUTONOMY FEASIBLE (probe-grade)

Per the pre-declared bars (AUC >= 0.70 OR clean reject of >=5/6 decay breaks while
keeping corrections): the coherence-margin-delta signal clears AUC 0.917, comfortably
above 0.70, and independently clears the reject-fraction bar (5/6) on its own hard
threshold. **Recommend: build the self-gated router around the coherence-margin-delta
signal specifically** (AccumulateRegister role-decode margin, pre-fix vs post-fix,
threshold near 0 or a small positive margin for extra conservatism) -- NOT around
n_compatible (mechanism-specific, doesn't apply to non-filtering fixes) or decay-margin
(self-referential to the mechanism, near-chance).

Caveats (report honestly, do not over-claim from N=12):
- This is 12 instances from 2 fix cycles on short/simple McGuffey content -- an
  aim-probe, not a powered result. The prior self-correct-null finding (McGuffey too
  simple for coherence signal to discriminate reader-internal errors) was about
  SELF-detection of errors pre-fix, not about JUDGING a fix's effect on the situation
  model post-fix -- a related but distinct question; this probe suggests the
  post-fix-effect version of the question is more tractable on the same content,
  plausibly because a fix event directly perturbs the accumulated register's
  consistency in a way a single ambient error does not.
- 1/6 corrections and 1/6 breaks are misclassified by the coherence signal alone --
  a real router needs either a confidence-weighted abstain zone (do not act right
  at the margin=0 boundary) or a second corroborating signal before genuinely
  autonomous (no-human) deployment.
- decay_margin_delta (signal b) being near-chance is itself a real, useful negative:
  it says the SPECIFIC mechanism that made a change is not a trustworthy judge of
  its own change (introspection != a mechanism reporting its own uncertainty
  correctly) -- the router needs an INDEPENDENT signal (the situation-model coherence
  organ), not the deciding mechanism's own score, which is the more brain-faithful
  reading anyway (a downstream consistency check, not first-person confidence).

## Recommendation

FEASIBLE -- proceed to a focused build of the self-gated router keyed on
coherence-margin-delta (AccumulateRegister decode-margin, pre vs post), with an
abstain band near the decision boundary rather than a hard 0 threshold, and treat
n_compatible / decay-margin as auxiliary (not primary) signals. Before wiring this
into the live loop for genuinely unsupervised operation, widen the labeled set (more
fix cycles, and per the standing content caveat, richer/longer content than short
McGuffey passages) to move this from an N=12 aim-probe to a powered validation.

## Reproducibility

- Probe script: `experiments/probe_loop_autonomy_self_signal_v1.py`
  (`--self-test` VETs the 3 traced replays byte-identical to their committed
  originals on a 6-passage slice before the full run trusts any signal).
- Full run: `python experiments/probe_loop_autonomy_self_signal_v1.py`
  (elapsed 0.53s, all 36 combined-gold passages, no GPU/remote needed).
- Metrics: `data/exp_probe_loop_autonomy_self_signal_v1/metrics.json`
  (`result.instances` has the full per-decision signal dump; `result.aucs`,
  `result.keep_revert_confusion`, `result.decay_window_reject_fraction_per_signal`,
  `result.all_corrections_keep_fraction_per_signal` have the aggregate numbers
  cited above).
- Reused verbatim / traced-and-VET'd, never mutated: `run_learnable_strict_cb`
  (5b266248f), `run_loop_principle_b` (4cc041fcd), `run_loop_discourse` (0c4285f52),
  `mention_link_wrong` + `auc_from_scores` (coref self-confidence calibration cell),
  `hdlab.situation_model_accumulate.AccumulateRegister` (wired capability).
