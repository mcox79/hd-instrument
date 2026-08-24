---
problem: the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by
status: REFUTED
bar: A CI-SEPARATED MARGIN OVER THE STRONGEST FLOOR YOU ACTUALLY RUN, ON THE LICENSED SUBSTITUTABILITY INSTRUMENT, MEASURED THROUGH THE LIVE PATH RATHER THAN IN A CELL.
result: at realistic accumulation (>=256 distinct context words) rare-count decode r=0.135 CI[0.121,0.163] hw=0.021 and count-1-vs-absent separation 0.326 sigma CI[0.286,0.359] hw=0.037; n=125 anchor-size rows over 204 real anchors, 34,169-sentence corpus, the real bit-exact store field. The per-word counts PPMI needs are NOT recoverable from the live _sums bundle.
floor: the info-free shuffled-code twin + absent-word noise floor, recomputed per anchor on this population -- twin median 0.033 sigma, p95 0.447, max 2.663. The realistic count-1 separation 0.326 sigma sits BELOW the null p95, i.e. at noise.
controls: POSITIVE small-k separation 3.73 sigma CI[3.61,3.82] clears null max 2.663 (decoder works when it can, so the collapse is real); NOISE MODEL measured/predicted 0.9984 pearson 0.9986 (the failure IS the random-projection crosstalk norm(P)/sqrt(d), excludes a bug); ORACLE-SUPPORT least-squares (strongest linear decoder) recovers EXACTLY r=1.0 for support<=d and collapses to r=0.245 for support>d, decoy false-positive std jumps 1e-15 to ~1 across the cliff (excludes a weak-decoder explanation); SHUFFLED-CODE info-free twin ~0 at every size (excludes estimator artifact); ENCODER IDENTITY bit-exact max_err 0.0 (excludes "not the live field"); 3 independent anchor samples reproduce.
files_changed: experiments/exp_decode_snr_real_store_field_v1.py, verification/test_decode_snr_shows_counts_are_not_recoverable.py, data/exp_decode_snr_real_store_field_v1/metrics.json, data/exp_decode_snr_real_store_field_v1/scored_population.json
reverify: .venv/Scripts/python.exe verification/test_decode_snr_shows_counts_are_not_recoverable.py
---

# What is refuted, and what is upheld

The brief's title claims the fix's data "is already being stored and then thrown away" -- i.e. the
substrate accumulates the co-occurrence counts a text-statistics (PPMI+SVD) channel needs, and the
job is just to DECODE them from the stored bundle. **That is refuted.** The counts are thrown away at
a deeper level than the brief identified: not at read-out by the sign quantiser, but at STORE time by
a 256-dimensional random projection, and no decoder recovers them at realistic accumulation.

Upheld, and not in dispute: the substrate really does accumulate word-context evidence while reading
(`ConceptSpace._sums[lemma] += context_vector(window, graded=True)`), and `anchor_matrix()` really
does discard magnitude with `np.sign`. Those two brief facts are true. What is false is the inference
that keeping the un-signed version (`freeze_graded`) hands back the counts. It does not, because the
graded sum IS the lossy projection.

# What I built

- `experiments/exp_decode_snr_real_store_field_v1.py` -- decodes co-occurrence counts from the REAL
  stored field and measures recovery vs ground truth, as accumulation grows, split frequent/rare.
- `verification/test_decode_snr_shows_counts_are_not_recoverable.py` -- scaffold-free witness, 7/7
  PASS, exit 0; prints CI half-widths and the info-free null p95/max beside every margin.

The store field is not synthetic here. The brief's own worry was that its feasibility test used the
documented sha256->bipolar draw, not the live encoder. I closed that: with `GRADED_COMPARATOR=True`
(confirmed live) and `context_vector(text, graded=True) == H^T p` (H's row for surface word w is
`symbol_vector(w)`, d=256), the store row is exactly `_sums[a] == H^T P_a`, where P_a is a's total
co-occurrence count vector. The cell asserts `reconstruct_bipolar(counts) == context_vector_masked`
BYTE-FOR-BYTE on real sentences as a precondition (max_err 0.0), reproducing rather than importing
exp_cue_information_audit_v1's 5491-anchor identity. So the field I decode IS the live field.

# What I measured

The naive decode the brief proposes, `decode(a,c) = dot(_sums[a], symbol_vector(c)) / d`, is a
matched filter: `= P_a[c] + SUM_{w!=c} P_a[w] * (dot(code(w),code(c))/d)`. The true count PLUS
Gaussian crosstalk with std `norm(P_a)/sqrt(d)`. Recovering the count of a RARE (count-1) context
word means reading a signal of 1 against that noise.

Degradation vs number of distinct context words (median; count-1 separation from absent, in sigmas;
rare-word decode correlation r):

| distinct context words | count-1 sep (sigma) | rare-word r | noise pred | noise meas |
|---|---|---|---|---|
| 1-8    | 6.89 | 0.892 | 0.140 | 0.143 |
| 8-32   | 3.52 | 0.700 | 0.286 | 0.285 |
| 32-64  | 1.93 | 0.519 | 0.519 | 0.525 |
| 64-128 | 1.25 | 0.390 | 0.824 | 0.811 |
| 128-256| 0.79 | 0.274 | 1.333 | 1.337 |
| 256-512| 0.41 | 0.180 | 2.469 | 2.368 |
| 512-1024| 0.21 | 0.116 | 4.657 | 4.680 |
| 1024-4096| 0.08 | 0.057 | 8.538 | 8.881 |

This reproduces and extends the brief's own ladder (13.8 -> 5.8 -> 3.1 -> 1.6 sigma). The five load-
bearing facts:

1. **POSITIVE CONTROL.** At tiny accumulation the decoder recovers count-1 words at 3.73 sigma
   (CI[3.61,3.82]), clearing the info-free null MAX of 2.663. The instrument works; the collapse at
   scale is real, not a broken decoder.
2. **REALISTIC REGIME (>=256 distinct).** Count-1 separation 0.326 sigma (CI[0.286,0.359]) -- BELOW
   the info-free null p95 of 0.447 -- and rare-word decode r=0.135 (CI[0.121,0.163]). Rare entries
   are at noise. PPMI weights rare co-occurrences hardest, so the entries the transform leans on are
   exactly the ones that drown.
3. **IT IS THE PROJECTION, NOT A BUG.** The measured absent-word noise std equals the analytic
   crosstalk `norm(P_a)/sqrt(d)` to 0.2% (median ratio 0.9984, pearson 0.9986). This is a
   deterministic property of a 256-wide random projection; it would be identical for any random H of
   this width.
4. **NO DECODER BEATS IT.** Oracle-support least-squares -- the optimal linear decoder, TOLD exactly
   which words co-occur -- recovers counts EXACTLY (r=1.0, decoy false-positive std ~1e-15) while the
   support is <= d, then falls off a cliff the instant support exceeds d: r=0.34 (support 1.1-2x d),
   0.16 (2-4x), 0.06 (>4x), with decoy false-positive std jumping to ~1.0. The naive matched filter
   and the optimum share one information limit at support == d = 256.
5. **THE WORDS YOU NEED ARE THE UNRECOVERABLE ONES.** Real anchors reach a median of 130 distinct
   context words, p90 543, max 3737 in this 34k corpus; 24% already exceed d=256. And distinct-
   context-word count tracks corpus frequency at Spearman 0.909 -- so the frequent words that appear
   in running text and most need a distributional vector are precisely the ones over the recovery
   limit. The recoverable regime (few distinct words) is the rare words you least need.

The shuffled-code info-free twin sits at ~0 sigma at every size (median 0.033), so the small-
accumulation signal is real information and the estimator invents nothing.

# Brain structure (labelled, none fabricated)

PINNED-BY-EVIDENCE: the hub-and-spoke architecture (Lambon Ralph; Patterson 2007) -- a distributional
spoke feeding the ATL hub is what SHOULD be stored. This finding does not touch that; it is about
whether OUR storage format can give it back.

OUR-INVENTION: the 256-dim random projection H is an engineering capacity choice, not a neural
structure. Inventing an anatomy for it would be the laundering the fidelity gate bans. The result is
a property of that invention: a random projection of this width cannot serve the pinned function once
an anchor co-occurs with more than ~d distinct words -- which real anchors do almost immediately.

# The strongest version of the idea, tested and also refuted

The brief asks: do not stop at "refuted"; name the strongest brain-faithful version and test THAT.
The strongest form of "use what is already stored" is "keep the GRADED sum instead of the sign"
(`freeze_graded`). I tested exactly that: the graded sum IS `H^T P_a`, and it is what the whole cell
decodes. Dropping the sign does not help, because the sign was never the binding loss -- the random
projection is. The strongest version of the brief's own idea fails for the same reason.

# What would have to change in hdlab (PROPOSED, not landed -- strategy session owns integration)

The distributional channel is genuinely missing and must be SUPPLIED, not decoded. Two admissible
routes; neither is "read freeze_graded and decode", which is refuted:

- **A (smallest, offline, admissible per owner 08-16).** Promote the distillation cell's own PPMI+SVD
  word-context space -- built offline from the corpus via `Pstore` (`raw_counts_for_window`) + `svds`
  -- into a STATIC labelled asset, and have `read()` / `grounded_similarity` consult it (with the
  taught direction) for pairs the hand lexicon does not cover. This is the space that already carried
  the 0.8388 substitutability result, using TRUE offline counts. Label it OFFLINE-BUILT; it is not
  something the substrate learned.
- **B (if it must be learned online).** Add an explicit sparse per-lemma context-count store to
  `ConceptSpace.observe` (a `Dict[lemma, Counter]` written ALONGSIDE `_sums`), so the counts are KEPT
  rather than projected away. Then PPMI+SVD on those at inference. Cost: memory grows with distinct
  co-occurrences -- the very quantity that breaks the projection -- but the counts are exact. This is
  the honest "store the data instead of throwing it away", and it requires ADDING storage, because
  the existing store does not contain the counts in recoverable form.

Either way the taught direction (distillation) is unchanged; only the SOURCE of the distributional
vector changes. The reason it "is not plugged in" is not that the wiring is missing -- it is that the
thing it would plug into (recoverable counts in the live store) does not exist.

# What I did NOT establish, and what I would withdraw first

- I did NOT run PPMI+SVD or substitutability THROUGH THE LIVE PATH. That is moot under this finding
  and is the brief's own sanctioned stopping point (bar item 1). The cell's 0.8388 substitutability
  number is untouched: it is an OFFLINE-COUNTS result and I neither reproduced nor challenged it; I
  showed only that its input cannot come from the live store.
- I tested the matched filter (brief-specified) and the L2-optimal oracle-support least-squares. A
  non-linear L1/sparse-recovery decoder could in principle reach slightly further IF P_a were sparse
  enough (k << d/log V ~ 25 nonzeros); real P_a at realistic sizes has hundreds-to-thousands of
  nonzeros, far past that budget, so L1 cannot rescue it either. This last step is REASONED from the
  oracle-support cliff, not exhaustively measured -- it is what I would withdraw first if challenged.
- The realistic sizes here (34k-sentence corpus, max 3737 distinct) are a LOWER BOUND on the full
  live read (12k-40k+ sentences); the real system is strictly worse, not better.

If the noise-floor definition (absent words) were disputed, the three definition-free facts still
carry the refutation on their own: the encoder identity (bundle == H^T P_a, bit-exact), the oracle-
support LSQ cliff at support==d (r=1.0 -> 0.06, no floor choice involved), and the accumulation
distribution (24% of anchors already past d=256, frequency-accumulation Spearman 0.909).

---

## TLDR (plain language)

The system was said to be quietly saving the word-neighbourhood tallies it needs to tell "sofa/couch"
from "apple/orange", and just needing them read back out. It is not saving them in a form you can read
back. As it reads, it adds each word's neighbourhood into a fixed-size 256-number summary. That
summary is like adding many transparent photos onto one sheet: a word seen next to hundreds of
different others turns into a blur. We measured the blur on the real saved summaries. When a word has
only a handful of distinct neighbours the tally reads back cleanly (about 4-7 times clearer than
chance). By the time it has a few hundred -- which the common words reach almost at once -- a
neighbour that occurred once is indistinguishable from one that never occurred (0.33 vs a 0.45 noise
level). Even a perfect reader that is told exactly which words are neighbours cannot undo it once
there are more than 256 of them; that is a hard limit of the 256-number format, not a weak method, and
we confirmed the blur matches the exact math to within a fifth of a percent. The cruel part: the
common words you most want to describe are the blurriest. So the fix cannot be "read what is stored".
The neighbourhood description has to be built separately (offline from the text, which already works
and gave the good result) or the tallies have to be saved explicitly as they are read -- both of which
mean ADDING the data, not recovering it.

## QUESTIONS

None. The measurement is complete and the brief's bar item 1 pre-authorised stopping here.

## NEXT STEPS (for the strategy session, which owns integration)

1. Re-verify on the artifact: `.venv/Scripts/python.exe verification/test_decode_snr_shows_counts_are_not_recoverable.py` (7/7, exit 0; ~15s, writes nothing).
2. Decide route A (promote the offline PPMI+SVD space as a labelled static asset) vs route B (add an explicit sparse context-count store to ConceptSpace). A is smaller and already validated at 0.8388; B is the "learned online" version and costs memory. My recommendation is A first, labelled OFFLINE-BUILT, because it is the shortest path to a live-path substitutability number and it does not pretend the substrate learned the channel. Risk of A: it is a static asset, so it does not grow with new reading; if the vision requires an online-learned channel, B is unavoidable and should be scoped now rather than after A ships.
3. Retire the framing "the data is already stored, just decode it" wherever it appears in the plan/board; the accurate framing is "the distributional channel must be supplied, because the live store keeps a projection that cannot return the counts."
