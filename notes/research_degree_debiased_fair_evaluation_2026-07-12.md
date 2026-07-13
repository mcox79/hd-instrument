# Research: is the g_backdoor leak (r=0.31) real, or is our EVAL PROTOCOL itself degree-biased? A debiased fair-evaluation design (2026-07-12)

Synthesis drill, 3 parallel Sonnet lit-scan sub-agents (debiasing protocols / degree-corrected negative sampling;
embedding-norm-vs-popularity correlation interpretation / hubness; filtered-ranking-protocol degree-bias mechanics)
+ director on-disk re-derivation of exactly what `cross_channel_geom_vs_poprank_r` and the fair-stratum hits@10
computation actually measure in `experiments/_course_c_rotate_core_v1.py` and
`experiments/exp_course_c_map_builder_cskg_l2_genuine_v1.py`. Design-only cycle, no local compute, per the
no-local-smokes lock — the deliverable is a pre-registered, REMOTE-runnable re-scoring cell spec, not new numbers.

Trigger: `data/exp_course_c_rotate_cskg_l2_seed_{7,17,23}_gpu1024_v1/metrics.json` (multi-seed FULL, verdict
`MIDDLE_BAND_PARTIAL`) shows the fair (low+mid degree tertile) WIN margin holding 3/3 seeds
(oneshot_fair=0.0772 vs POP_fair=0.0442, margin=+0.033, seed17; consistent sign/magnitude across seed7/23 —
confirmed by reading all three metrics.json) while `g_backdoor` FAILS: `backdoor_r=0.3118` (seed17, and
comparable on the other two seeds) against the pre-registered `R_BACKDOOR=0.15` threshold. This note answers:
is that 0.31 a real shortcut, or a measurement artifact of an eval protocol that is itself degree-biased —
exactly the failure mode the KG/RecSys popularity-bias literature (Aiyappa et al. ICML2025; Shomer et al.
WWW2023; Mohamed et al. UAI2020) has independently converged on.

---

## HEADLINE

**The r=0.31 "backdoor" correlation is very likely dominated by a THIRD-VARIABLE CONFOUND (gold-tail degree),
not a genuine frequency shortcut — but the fair-stratum WIN margin has a DIFFERENT, real gap: it stratifies the
POSITIVE (gold) side by degree but never degree-matches the NEGATIVE (candidate) side, which is exactly the
mechanism the field's newest papers (Aiyappa et al. 2025; Shomer et al. 2023) identify as the dominant residual
bias in link-prediction evaluation even after gold-side stratification.** Both problems are fixable with one
cheap re-scoring pass over a reproduced (not re-designed) fit — no new experiment, no new cell logic, ~30-40 min
GPU wall-time across 3 seeds.

1. **What `backdoor_r` (`cross_channel_geom_vs_poprank_r`) actually computes** (verified by reading
   `_course_c_rotate_core_v1.py` lines 582-596): for every held-out L2-genuine query (pooled across ALL THREE
   degree tertiles, ~6000 queries, NOT restricted to the fair low+mid arena), it is
   `Pearson(gold_geo_i, -pop_rank_i)` where `gold_geo_i` = ONESHOT_ROTATE's raw chordal-cosine score on the
   TRUE gold tail, and `pop_rank_i` = the gold tail's filtered rank under per-relation tail-frequency (POP).
   Because this correlation is computed **pooled across strata**, and both `gold_geo` (via hubness — see below)
   and `pop_rank` (by definition) are driven by the SAME underlying variable — the gold tail's own degree — a
   substantial positive correlation is the textbook signature of a shared-confound Pearson correlation, not
   necessarily evidence the rotation geometry is "reading off" frequency. arm_hits already shows this dependency
   directly: ONESHOT's own hits@10 goes 0.0307 (low) -> 0.1244 (mid) -> 0.3955 (high) and POP's goes 0.0129 ->
   0.0761 -> 0.4155 — both arms track gold-degree in the SAME direction, which is exactly what would produce a
   pooled cross-channel r near +0.3 even if the WITHIN-stratum relationship were much weaker or absent.

2. **Hubness calibration point (sub-agent 2, high confidence on direction, medium on magnitude-comparability):**
   in the embedding literature, higher-degree/higher-frequency entities systematically get larger-norm /
   better-conditioned embeddings purely from MORE gradient exposure (Radovanovic et al. 2010 hubness; Schakel &
   Wilson 2015 word2vec norm-vs-frequency) with NO explicit frequency feature ever given to the model — this is
   treated as expected background, not a leak. Reported embedding-norm-vs-popularity correlations in comparable
   settings run **r ~ 0.42-0.84**. Our measured r=0.31 sits BELOW the low end of that typical benign range —
   directionally consistent with "this is ambient hubness, not an injected shortcut," though the measurement
   isn't apples-to-apples (embedding-norm-vs-frequency vs. our raw-score-on-gold-vs-pop-rank), so treat this as
   a supporting calibration point, not proof.

3. **The field's actual verdict mechanism is not a correlation threshold at all** (sub-agent 2): no paper found
   specifies a numeric "acceptable r" cutoff for embedding-vs-degree correlation. The diagnostic the field
   actually uses is **"does a degree/popularity-only baseline reproduce most of the model's accuracy on the
   SAME eval set"** (Zhou/Aiyappa et al. 2025's own methodology) — which is EXACTLY what our `win_pop` /
   `fair_hits_at_k` gate already tests (ONESHOT vs POP, fair stratum). In other words: **the fair-stratum hits@10
   margin, not the pooled correlation, is the field-validated diagnostic.** The `g_backdoor` gate as currently
   built is a stricter, non-standard, additional paranoia check that is measuring something else (pooled
   cross-channel correlation) and is *more* likely than the WIN gate to be swamped by the degree confound
   described in point 1. This reframes the MIDDLE_BAND verdict: `win_pop=True` may already be the more
   trustworthy signal; `g_backdoor=False` may be an artifact of computing the wrong statistic (pooled r instead
   of partial/within-stratum r), not evidence the win itself is fake.

4. **But the WIN gate has its own, more mainstream, exposure: the negative/candidate side is never
   degree-matched.** `filtered_hits_from_scores` (verified by reading
   `exp_course_c_map_builder_cskg_l2_genuine_v1.py` lines 332-357) ranks the gold tail against **ALL N=25,752
   entities** regardless of which stratum the QUERY's gold tail falls in — `fair_hits_from_scores` only
   subsets which ROWS (queries) are scored, never which COLUMNS (candidates) compete. This is precisely the
   mechanism Aiyappa et al. (ICML 2025, arXiv:2405.14985) formalize for homogeneous-graph link prediction:
   positive edges are drawn with a degree-skewed distribution (`p_pos(k) = (k/<k>)*p(k)`) while the negative
   pool is degree-uniform (`p_neg(k) = p(k)`), so a model exploiting raw degree/popularity separates positives
   from negatives "for free," independent of any real structural learning; their degree-matched null (draw
   negatives from a degree-weighted node list matching the positive distribution) collapsed a strong
   preferential-attachment baseline from AUC 0.83 (13th/26, beating 54% of real methods) to 0.54 (dead last),
   while sophisticated GNNs correspondingly IMPROVED rank (GCN 14th->2nd, node2vec 17th->5th) once the
   candidate pool was corrected. Shomer et al. (WWW 2023, arXiv:2302.05044) independently show the SAME
   mechanism specifically inside KGE (TransE/RotatE/ComplEx-class) filtered ranking, and argue gold-side
   stratification is necessary-but-not-sufficient without also correcting the candidate side. Our fair-stratum
   design controls the gold/positive side (restricts evaluated queries to low+mid gold-degree) but leaves the
   negative/candidate side uncorrected (all 25,752 entities, spanning every degree, compete regardless of
   stratum) — this is the textbook incompletely-corrected setup both papers warn about.

5. **Which direction does the missing correction cut?** Not obvious a priori, and genuinely the open empirical
   question (see falsifiable predictions). Two considerations pull in OPPOSITE directions: (a) leaving
   high-degree entities in the candidate pool for a low/mid-degree QUERY is, if anything, already a HANDICAP
   for POP (POP's absolute low-stratum score is only 0.0129 — it loses badly to high-degree "hub" distractors
   it would otherwise favor) — this cuts AGAINST "POP is artificially inflated in the fair arena," and suggests
   our fair-stratum design is already MORE degree-corrected on this axis than Aiyappa's default homogeneous
   protocol was before their fix; (b) but per Aiyappa's own before/after result, properly degree-matching the
   candidate pool generally makes SOPHISTICATED methods look relatively BETTER, not worse, once the naive
   degree-driven "free wins/free losses" are removed from the comparison — which would predict the ROTATE-vs-POP
   margin GROWS or holds under debiasing, not shrinks.

---

## Cheap decisive test (remote-runnable, ~30-40 min GPU across 3 seeds, no new cell logic)

**Constraint discovered while designing this (must be stated plainly, not glossed over): the mission's framing
("reuse the EXISTING gpu1024 fit codes... pure re-eval, no re-training") is not literally available as stated.**
`experiments/_fit_checkpoint.py:cleanup_seed_checkpoints` deletes the per-arm `_fitckpt_*.pt` files from the
anchor output dir immediately after a FULL run completes successfully (line 1087 of `_course_c_rotate_core_v1.py`)
— by design, for disk hygiene, not for post-hoc reuse. Confirmed: `ls data/exp_course_c_rotate_cskg_l2_seed_*_gpu1024_v1/`
shows only `metrics.json` in all three seed dirs; no PHI/THETA tensors survive.

**The workaround is cheap and already validated on this exact cell:** the FULL run's own self-test already
proved bit-identical resume-equivalence (`"resume_equiv_rotate_maxdev": 0.0`, tol `1e-5`, all three seeds) —
the fit is deterministic given (seed, config, split-hash, code). A re-run of `fit_kge_rotate` with the SAME
seed + `FULL_CFG` reproduces the exact same PHI/THETA the archived run used. Each seed's `arm_sigs` in the
existing metrics.json (e.g. seed17: `ONESHOT_ROTATE="7a8e196906e99b7b"`, `BASELINE_POP="f7fe67bfd8c3af18"`)
give a ready-made VERIFICATION checksum: the re-scoring cell should recompute these two sigs first and hard-fail
if they don't match the archived value, proving the recompute is a faithful reproduction and not a new fit.

**Design (a small new anchor, reusing `_course_c_rotate_core_v1` functions directly, not a new design):**

1. For each seed in {7, 17, 23}: rebuild the identical split (`build_cskg_core_triples` / `extract_l2_genuine`
   / `stratify_by_tail_degree`, same `k_core=12`, `n_eval=6000`, same seed) and refit ONLY `ONESHOT_ROTATE`
   (skip ADDITIVE/SCRAMBLE/RANDOM/ORACLE/DISCRETE — not needed for this diagnostic, cuts GPU cost to roughly
   1/6th of the original 7-arm FULL run's 3412s, since POP needs no fitting at all — just a frequency count).
2. **Verification gate (must pass before trusting anything below):** recompute `arm_sig` for ONESHOT_ROTATE and
   BASELINE_POP; hard-fail the cell if either sig differs from the archived metrics.json value for that seed.
3. **Debiased diagnostic A (fixes the pooled-correlation confound, point 1/3 above):** recompute
   `cross_channel_geom_vs_poprank_r` THREE ways: (i) as-is pooled (should reproduce 0.3118 exactly, sanity
   check); (ii) WITHIN each of the existing low/mid/high tertiles separately (reuses `strat` array already
   computed, zero new code); (iii) as a genuine partial correlation controlling continuously for
   `log(node_degree+1)` (residualize `gold_geo` and `pop_rank` each against `log(degree+1)` via one-line OLS,
   correlate residuals). (ii) and (iii) are the field-standard fix for exactly this confound.
4. **Debiased diagnostic B (fixes the candidate-side gap, point 4 above):** for the fair (low+mid) queries
   only, recompute `filtered_hits_from_scores` / `pop_hits` with the CANDIDATE POOL (columns) restricted to
   entities whose `node_degree` also falls in the low+mid tertile range (`tert_bounds` already stored per
   seed) — i.e., mask out all high-degree columns before ranking, for BOTH ONESHOT_ROTATE and POP, same
   `all_true_by_hr` filtering otherwise unchanged. Report the new fair margin
   `oneshot_fair_degmatched - POP_fair_degmatched`.
5. Report all four numbers (pooled r, within-stratum r's, partial r, degree-matched margin) per seed + 3-seed
   mean/cv, same JSON schema conventions as the existing gates block.

This is the FAIR YARDSTICK the mission asks for — reusable verbatim for the future map-builder eval and any
subsequent course-C cell, not a one-off patch.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered BEFORE the re-eval runs)

Deflated per lit-scan calibration penalty (novel-synthesis cap 0.50; no direct precedent for this EXACT
combination of glass-box phase-rotation + CSKG + this specific debiasing recipe).

**P1 — the pooled backdoor correlation is a confound, not a leak (redeems the g_backdoor gate).**
- HARD-PASS: within-stratum r (each of low/mid/high individually) AND the degree-partialed r all fall below
  `R_BACKDOOR=0.15` (or comfortably closer to it than the pooled 0.31).
- HARD-FAIL: within-stratum / partial r stays >= 0.25 — i.e. the correlation survives controlling for degree,
  meaning there IS a genuine within-degree-band relationship between rotation geometry and popularity (a real,
  if modest, leak).
- P(HARD-PASS) = **0.45** (deflated from an un-deflated instinct of ~0.60-0.65, per calibration cap and because
  this is the first time this EXACT diagnostic has been computed on this substrate — no prior measurement to
  anchor on beyond the general-literature calibration point in headline #2).

**P2 — the fair-stratum WIN margin under degree-matched candidates: GROWS, HOLDS, or SHRINKS/vanishes.**
- (a) GROWS (margin_degmatched > 0.033 + noise, i.e. >= 0.045): P = **0.25**. Consistent with Aiyappa's
  before/after pattern (sophisticated methods rank relatively BETTER once naive-degree free-wins are removed
  from the comparison).
- (b) HOLDS (margin_degmatched in [0.015, 0.045], same qualitative WIN): P = **0.40** (highest-probability
  outcome — our fair-stratum design already partially corrects the positive side, so the INCREMENTAL effect of
  also degree-matching candidates should be smaller than Aiyappa's dramatic homogeneous-graph swing).
- (c) SHRINKS/vanishes (margin_degmatched <= 0.01, i.e. the original 0.033 margin was itself substantially a
  candidate-pool degree artifact): P = **0.20**.
- (Remaining ~0.15 mass: POP itself collapses to near-chance under degree-matched candidates — a genuinely
  different regime, would need its own follow-up.)
- HARD-PASS (redeemed/cleaner result): margin_degmatched >= 0.02 (relaxed from POP_GAP=0.03 since this is
  measurably a HARDER, stricter test than the original) AND P1 HARD-PASS.
- HARD-FAIL (the leak was real): margin_degmatched <= 0.00 (ties or reverses) — i.e. once candidates are
  degree-matched, ROTATE no longer beats POP in the fair arena. This would mean the ORIGINAL 3-seed WIN was
  itself an artifact of asymmetric candidate composition, not real relational reasoning.
- MIDDLE (ambiguous, most likely outcome given P(b) dominance): margin shrinks to (0.00, 0.02] — positive but
  below the stricter bar; escalate to a 4th/5th seed or a k/epoch sweep before either closing or claiming WIN.

**P3 — arm_sig verification passes (recompute reproduces archived sigs exactly).**
- HARD-PASS: both sigs match exactly (proves faithful re-derivation, not a new experiment).
- HARD-FAIL: sigs differ -> STOP, do not trust any downstream number; investigate nondeterminism (unlikely
  given the self-test's own resume-equivalence proof, but must be checked, not assumed).
- P(HARD-PASS) = **0.90** (high confidence; this is a mechanical determinism check, not a novel-synthesis
  claim, so NOT subject to the 0.50 novel-synthesis cap).

---

## Cross-thread synthesis with prior entries

- Extends `notes/research_kg_degree_community_diagnostic_2026-07-12.md` (same k-core=12, N=25752, avg-deg
  39.7 graph) — that note characterized the GRAPH's degree distribution (Gini, power-law exponent) as a
  prerequisite diagnostic; this note characterizes the EVALUATION PROTOCOL's degree-sensitivity as the
  complementary prerequisite. Together they argue: before trusting ANY geometry-vs-frequency margin on a
  CSKG-scale multi-relational graph, BOTH the graph's degree skew AND the eval protocol's degree-sensitivity
  need to be measured, not assumed benign.
- Directly operationalizes the `g_backdoor` gate that FAILED in
  `data/exp_course_c_rotate_cskg_l2_seed_{7,17,23}_gpu1024_v1/metrics.json` — this is the first research pass
  that opens up WHAT that gate is actually computing (pooled cross-stratum correlation) rather than treating
  its failure as a flat verdict.
- Consistent with the standing discipline `[[feedback-fairness-plus-weak-point-localization-first-class]]`
  (USER 2026-07-10): this design adds BOTH a fairness fix (degree-matched candidates) AND a localization tool
  (within-stratum / partial correlation pinpoints WHERE the pooled correlation comes from) in one cheap pass —
  exactly the "metric-can-it-move + localize-the-break" pattern the user asked to be first-class per cell.
- Consistent with `[[feedback-dont-over-correct-on-raw-full-either]]` (2026-07-10): this note explicitly argues
  AGAINST over-correcting on the g_backdoor FAIL alone (point 3 above — the pooled r may itself be the
  mismeasured artifact) while ALSO not dismissing the real, literature-grounded candidate-pool gap (point 4) —
  holding both readings open until the cheap re-eval actually runs, rather than swinging to either "the win is
  fake" or "the win is proven" prematurely.

---

## Substrate-product implications

- If P1 HARD-PASS + P2 (a)/(b): the glass-box rotation-vs-frequency result becomes a CLEANER, field-validated
  win — not just multi-seed-stable but shown to survive the specific debiasing protocol the KG-eval literature
  considers decisive. This upgrades confidence in “the substrate can do real relational composition beyond
  frequency-guessing” from MIDDLE_BAND to a genuine WIN candidate, unblocking the map-builder direction without
  needing a new experimental design — just a corrected yardstick.
- If P2 HARD-FAIL: this is equally valuable as a NEGATIVE result — it means the current fair-stratum apparatus
  (used across the whole course-C family, not just this cell) has a shared, fixable evaluation blind spot
  (candidate-pool degree composition), and every prior course-C WIN/MIDDLE_BAND verdict computed with the same
  `filtered_hits_from_scores` machinery should be re-audited with degree-matched candidates before being trusted
  at face value. That would be a structural fix applicable across the whole family, not a one-cell fix.
- Either way, the debiased re-scoring machinery designed here (within-stratum/partial correlation +
  degree-matched candidate pool) becomes the FAIR YARDSTICK for the next map-builder eval cycle, as the mission
  requested — a reusable diagnostic, not a one-off patch.
- Cost discipline: because POP needs no fitting and only 1 of 7 arms needs refitting, this yardstick is cheap
  enough to run as a STANDARD add-on gate on every future course-C-family cell, not a special one-time audit.

---

## Citations (verified count: 9 primary sources fetched/confirmed via WebSearch+WebFetch or cross-corroborated by 2+ independent sub-agent searches; several additional secondary/survey citations reported by sub-agents but not independently re-verified by the director are listed as "reported, not independently verified")

Verified (director independently fetched or cross-confirmed across >=2 sub-agents):
1. Aiyappa, Wang, Kim, Seckin, Yoon, Ahn & Kojaku, "Implicit Degree Bias in the Link Prediction Task," ICML 2025
   (PMLR v267), arXiv:2405.14985. Director-fetched abstract + HTML full text directly (mechanism, Algorithm 1
   degree-matched negative sampling, AUC 0.83->0.54 / rank 13->26 for preferential-attachment, GCN 14->2,
   node2vec 17->5 numbers pulled from full-text fetch, not summary).
2. Shomer, Jin, Wang, Zhao, Wu & Tang, "Toward Degree Bias in Embedding-Based Knowledge Graph Completion,"
   WWW 2023, arXiv:2302.05044. Reported convergently by 2 sub-agents (debiasing-protocols scan + correlation
   scan).
3. Mohamed, [Novacek/Vandenbussche co-authorship reported inconsistently across sub-agents — venue confirmed
   UAI 2020, PMLR v124], "Popularity-Agnostic Evaluation of Knowledge Graph Embeddings." Venue/PMLR-volume
   cross-checked (v124 = UAI 2020) to resolve a sub-agent venue conflict (one reported UAI, one reported
   AISTATS); treat exact co-author list as unverified.
4. Radovanovic, Nanopoulos & Ivanovic, "Hubs in Space: Popular Nearest Neighbors in High-Dimensional Data,"
   JMLR 2010. Foundational hubness result, standard citation.
5. Sun, Deng, Nie & Tang, "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space," ICLR
   2019, arXiv:1902.10197 — self-adversarial negative sampling (already the recipe reused in our
   `_course_c_rotate_core_v1.py`, cross-referenced not newly discovered).
6. Krichene & Rendle, "On Sampled Metrics for Item Recommendation," KDD 2020 / CACM 2022 — sampled-vs-full
   ranking metric inconsistency, RecSys precedent for the KG-eval-protocol critique.
7. Steck, "Item Popularity and Recommendation Accuracy," RecSys 2011 — earliest clean statement of the
   popularity-inflates-accuracy mechanism in the adjacent RecSys literature.
8. Zhang, Feng, He, Wei, Song, Ling & Zhang, "Causal Intervention for Leveraging Popularity Bias in
   Recommendation" (PDA), SIGIR 2021, arXiv:2105.06067 — causal/counterfactual popularity-debiasing approach,
   noted as NOT yet operationalized for KGE training (transfer gap flagged as sub-agent's own synthesis, not
   a sourced claim).
9. Saito et al., "Unbiased Recommender Learning from Missing-Not-At-Random Implicit Feedback," WSDM 2020 — IPS
   propensity-reweighting precedent.

Reported by sub-agents, not independently re-verified by director (lower confidence, flagged per-item above):
Sun et al. "Theoretical and Empirical Insights into the Origins of Degree Bias in GNNs" (arXiv:2404.03139);
Schakel & Wilson / Wilson & Schakel word2vec norm-vs-frequency papers (2015); "How Graph Convolutions Amplify
Popularity Bias for Recommendation?" (arXiv:2305.14886); "Are Knowledge Graph Embedding Models Biased, or Is
it the Data?" (CEUR-WS); Rossi et al. KGE comparative-analysis survey.

---

## Intuitive summary

We had a worry: our result that "geometric reasoning beats simple frequency-counting" on the fair, non-obvious
part of the knowledge graph might secretly be cheating — the geometry might be quietly re-deriving popularity
instead of doing real reasoning, flagged by a suspicious 0.31 correlation between how confident the geometry
model is and how popular the correct answer is. I went and checked what the wider AI research field has learned
about exactly this kind of trap in the last two years. The good news: there's a well-known, boring reason two
unrelated models would BOTH correlate with an answer's popularity even with zero cheating — popular things
simply get more "practice" during training, so any reasonable model gets a little more confident about them,
the same way a student who's seen a word a thousand times writes it more fluently regardless of whether they
"know" what it means. Our correlation (0.31) is actually on the LOW side of what's normally seen in totally
innocent cases (0.4-0.8 is typical), which is reassuring. BUT the field also found a real, separate problem
that DOES apply to us: when you test a model, you should make sure the WRONG answers it's rejecting are just
as "obscure or popular" as the right answer — otherwise the model gets an easy freebie by just noticing "this
candidate is famous, that one isn't," without doing any real reasoning. We check this for the CORRECT answer
already (we test separately on obscure vs. popular correct answers) but we never checked it for the WRONG
answers it's being compared against. So I designed a cheap follow-up test (a few tens of minutes on the GPU,
reusing work already done, not a new experiment) that fixes both things at once and will tell us, honestly,
whether our win is real, gets even stronger once we remove the easy freebies, or was itself partly a freebie.
Either answer is useful: if it holds up, we have a cleaner, field-tested win; if it doesn't, we've found a
general blind spot worth fixing across this whole family of tests, which is valuable in its own right.
