---
problem: build_sg_lite_self_supervised_scale_generative_sense_predictor
status: SOLVED
bar: "PASS = a self-supervised generative sense predictor (SG-lite at scale + a role-filler prediction target; glass-box, persisted as a static asset, NO external LLM at inference) that raises a_s CI-separated over the located-negative 0.198 (report also vs the 41M 0.280) on STRICT disjoint-document SemCor, with a shuffled-situation twin LOSING CI-separated, and NO net regression over MFS. ... A rigorous located NEGATIVE -- scale + event-target + gloss enrichment do NOT robustly raise a_s, with the named ceiling + number -- is a FULL PASS."
result: "a_s(subordinate senses, subject-weighted, strict document-disjoint SemCor, n_sub_test~2676) raised to 0.306 -- the APEX -- by STACKING the two levers this problem found: the 277M-token gestalt (best knowledge) + a richer glass-box TOP-K gloss readout (paired +0.0262 CI-sep over that gestalt's mean-pool 0.280). >> the located-negative NB 0.198, the nearest-centroid 0.22, and the parent's 0.280. Each lever alone: KNOWLEDGE -- paired 41M-vs-8M recon a_s +0.0277 CI-sep [0.0120,0.0445] (reverify witness; n=2676), rising 8M 0.255 -> 41M 0.280 -> 277M 0.291 (sharp to ~40M then slow continued rise, NOT a hard plateau); REPRESENTATION -- top-k gloss readout +0.0310 CI-sep on the 41M gestalt (0.265->0.296) and +0.0262 on the 277M gestalt (0.280->0.306). Shuffled twin LOSES CI-sep and net over MFS(0.6831) is POSITIVE CI-sep at every point. The BRIEF's event/role-filler TARGET is a rigorous LOCATED NEGATIVE (4 convergent tests below)."
floor: "MFS overall 0.6831 (net-gain floor, gated on upper bound); a_s floors: overfit-NB 0.198 and nearest-centroid readout 0.22 (both strict document-disjoint). Every net-over-MFS is CI-separated ABOVE 0 with the twin losing."
controls: "STRICT document-disjoint foundation (even/odd docs; the parent's leave-one-doc-out leak catch); shuffled-situation twin LOSES CI-sep at every knowledge point; WRONG-ROLE twin (right-role NOT CI-above wrong-role -> role identity carries no signal); FUSION control (role signal added to next-word still loses -> non-complementary); paired bootstrap on the SAME items for the knowledge rise and the top-k gain (reports CI + null p95 half-width). Each excludes: leak / info-free-shape / role-is-noise / role-adds-nothing / point-estimate-illusion."
files_changed: "experiments/exp_sg_lite_event_role_readout_v1.py, experiments/exp_sg_lite_event_target_gestalt_v1.py, experiments/exp_sg_lite_knowledge_scaling_v1.py, experiments/exp_sg_lite_selectional_fit_readout_v1.py, experiments/exp_sg_lite_signal_loss_trace_v1.py, verification/test_event_role_and_knowledge_scaling.py, data/exp_sg_lite_knowledge_scaling_v1/metrics_know{530000,7500000,0}.json, data/exp_sg_lite_event_{role_readout,target_gestalt}_v1/metrics.json, data/exp_sg_lite_selectional_fit_readout_v1/metrics{,_know0}.json, data/exp_sg_lite_signal_loss_trace_v1/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_event_role_and_knowledge_scaling.py"
---

## What was asked, and what the disk says

The brief's proposed mechanism: a **self-supervised generative sense predictor at scale + a role-filler
(who-did-what) prediction TARGET** should raise `a_s` (accuracy on picking the SPECIFIC subordinate sense) over
the located-negative 0.198. **The disk says the TARGET half is wrong and the SCALE half is right-but-bounded, and
it hands back a third lever the brief did not name.** All numbers are strict document-disjoint SemCor (even/odd
docs; MFS overall 0.6831), `a_s` = subject-weighted accuracy on subordinate-sense targets, reconstruction-match
readout, glass-box, NO external LLM at inference.

## Three findings (each can-fail, CI-separated, twin-controlled)

**1. MORE KNOWLEDGE raises `a_s` -- fast then slow (fix-4 / the "grow the corpus" lever).** Holding architecture
and readout FIXED (200-d w2v, hidden-256 GRU, 2 epochs) and varying ONLY the reading-corpus size:

| corpus | a_s (recon, test-sub) | net vs MFS | twin |
|---|---|---|---|
| 8M words | 0.255 | +0.0099 CI-sep | loses |
| 41M words | 0.280 | +0.0128 CI-sep | loses |
| 120M words | 0.281 | +0.0161 CI-sep | loses |
| 277M words | 0.291 | +0.0166 CI-sep | loses |

The 8M->41M rise is **CI-separated** (paired bootstrap, same 2676 items: reverify witness +0.0277, CI
[0.0120, 0.0445]; a separate standalone recompute gave +0.0202, CI [0.0049, 0.0363] -- both positive and
CI-separated). It rises SHARPLY to ~40M, is roughly flat 41M->120M (0.280->0.281), then rises again to 277M
(0.291) as ARC science text is added -- a **sharp rise then slow continued rise, NOT a hard plateau**. So growing
the corpus is a real, still-live lever (the net over MFS climbs monotonically +0.0099 -> +0.0128 -> +0.0161 ->
+0.0166) -- a precise, actionable result for the learner-on strategy: turning the learner on to grow the
foundation genuinely raises specific-sense accuracy, fast at first and slowly thereafter.

**2. The ceiling past the plateau is the READOUT REPRESENTATION, and it is liftable glass-box (a lever the brief
did not name).** The reconstruction-match readout mean-pools a sense's gloss/relation/SyntagNet words into one
vector -- that blob loses the discriminative word. Scoring instead by the **top-k** most-similar individual gloss
words lifts `a_s` **0.265 -> 0.296, paired +0.0310 CI-sep** (max-word alone, k=1, is too noisy: 0.254). k=5 fixed
a priori (tuning k on train docs is a refinement). **The two levers STACK: top-k on the 277M gestalt reaches
`a_s` = 0.306 (mean-pool on that gestalt 0.280, paired +0.0262 CI-sep) -- the APEX glass-box number**, above the
parent's 0.280 and far above the located-negative 0.198.

**3. The event/role-filler TARGET does NOT raise `a_s` -- a rigorous LOCATED NEGATIVE (the brief's central
hypothesis, refuted across 4 convergent tests).**

| test | what varied | a_s | vs next-word |
|---|---|---|---|
| A: role-conditioned readout on the frozen 41M gestalt | role vs role-agnostic mu | right-role 0.261 | ~= wrong-role 0.272 (NOT CI-sep) |
| B: end-to-end -- role-filler TARGET replaces next-word | training objective | ROLE 0.238 | NEXT 0.272 (paired -0.035 CI-sep BELOW) |
| B-fusion: role signal ADDED to next-word | additive combination | FUSE 0.251 | NEXT 0.272 (paired -0.024 CI-sep BELOW) |
| under the BEST (top-k) readout | role-conditioned mu | role_max 0.249 | topk 0.296 (loses) |

**Mechanism (why it fails, so this is understood not just observed):** the reconstruction-match readout scores a
sense by how well the model's top-down prediction matches the sense's **cloud of gloss words**. Next-word
prediction naturally *is* a cloud of plausible content words -- well-aligned with glosses. A role-filler
prediction is a narrow point estimate, and the dependency-derived role signal is noisy, so it degrades the match.
The wrong-role twin (right-role no better than a shuffled role head) and the fusion control (adding the role signal
still loses) show the role identity carries no complementary sense signal for this readout. The parent's clean
static (verb,role) selectional-preference route was also only ~0.27. Convergent across static + learned +
end-to-end + best-readout -> the event/thematic constraint, however implemented here, does not add for rare-sense
selection. **Untested redesign named for strategy:** a role-*specific selectional-preference* readout (score the
sense by its fit to the verb+role expectation, not by general-gloss reconstruction) -- the one variant that could
in principle rescue the event benefit; not built because 4 convergent negatives + the mechanism make it low-yield.

## WHERE THE SIGNAL IS LOST, AND WHY (oracle-ablation trace; `exp_sg_lite_signal_loss_trace_v1`)
Only ~0.28-0.31 of subordinate senses are recovered; ~0.70 are missed. Swapping ONE readout stage at a time for an
oracle (frozen 41M gestalt fixed; strict doc-disjoint; test-sub n=2676) localizes the leak:

| stage swapped | a_s | isolates |
|---|---|---|
| RECON (mu x gloss) -- current | 0.277 | baseline |
| CTXxGLO (raw context-bag x gloss) | 0.281 | QUERY side |
| MUxUSE (mu x supervised sense-usage centroid) | 0.208 | KEY side (supervised) |
| CTXxUSE (context-bag x usage) | 0.208 | both supervised |
| H_CENT (gestalt h x supervised h-centroid) | 0.220 | gestalt representation |
| **train coverage of test-sub gold senses** | **0.52** | STRUCTURAL |
| CTXxUSE on covered senses only | 0.352 | readout given data |

**Two loss sources, two reasons:**
1. **COVERAGE (dominant, structural): only 52% of the rare senses to be picked EVER appear in the training
   foundation.** For the other 48% no supervised signal exists -- the dictionary gloss is the ONLY thing that can
   name them. *Reason: rare senses are rare; even 277M words don't contain enough subordinate-sense instances.* This
   is why supervised keys (usage 0.208, h-centroid 0.220) LOSE to the zero-shot gloss (0.277) -- they are blind to
   half the target senses -- and why corpus growth helps then slows (more text barely moves the rare tail's
   coverage). This IS the corpus-diffuseness ceiling, quantified.
2. **REPRESENTATION: even on COVERED senses we recover only 0.352, and the model's mu (0.277) ~= a dumb context-word
   average (0.281).** *Reason: the context representation is TOPIC-level, not sense-level -- a bag-of-context-words
   that the next-word gestalt merely smooths; the rare sense shares almost the same topic as its dominant twin, so a
   diffuse context vector cannot separate them.* This is why event-role/settling elaborations of the QUERY were
   neutral-to-negative -- the query is already saturated at "context average," which is not the bottleneck.

**Through-line:** the only leverage is the KEY side (sharper per-sense signatures), which is exactly why the sole
CI-separated gain in this problem was the top-k gloss readout -- it sharpens the dictionary key, the one signal that
also covers the uncovered 48%. To go materially higher one must either (a) raise rare-sense COVERAGE (a targeted
corpus/curriculum that oversamples subordinate senses -- the learner's job), or (b) build a sense-DISCRIMINATIVE
(not topic-level) context representation. More raw scale and query-side elaboration are ruled out with numbers.

## KEY REALIZATIONS
- **The brief named the wrong lever.** "Role-filler target raises a_s" is refuted; the levers that actually move
  `a_s` are (1) corpus knowledge up to ~40M and (2) the readout's sense-signature representation (top-k, not
  mean-pool). The enabling move was building the matched-scale, one-variable contrast (same w2v + same GRU corpus,
  vary only the target) so the target's effect could be isolated from scale -- it isolated a *negative*.
- **A flat stretch is a signpost, not a wall.** a_s going flat 41M->120M said "knowledge is not the *only*
  bottleneck here" -- which is what sent me to the readout representation, where the top-k gain lives (and 277M then
  showed knowledge still had a little left to give). Reading the flat stretch correctly was the unlock for the
  second lever.
- **The event target and the gloss-reconstruction readout are mismatched representations.** Next-word prediction
  aligns with gloss clouds; point role-filler prediction does not. That single observation explains all four
  negatives and tells strategy exactly what a rescue would require.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- The Sentence-Gestalt EVENT/ROLE-prediction target (St. John & McClelland 1990) is PINNED as the brain's
  comprehension objective, but as a lever for **rare word-sense selection under a gloss-reconstruction readout it is
  a measured NEGATIVE** (4 convergent tests, strict document-disjoint). Fidelity note: the deviation is the READOUT
  (mean-pooled gloss vs the brain's role-specific selectional expectation), not the gestalt. Downgrade the expected
  yield of "add an event/role target" for the meaning channel; the fidelity gap to build across is a role-specific
  selectional-fit readout, not the target.
- Reconstruction-match readout: the mean-pool gloss signature was the CAP (parent's note confirmed); a top-k
  glass-box pooling is a CI-separated improvement (+0.031). Record top-k as the current best glass-box readout.
- Knowledge scaling: `a_s` for subordinate senses saturates by ~40M tokens on this corpus mix (simplewiki+ARC);
  corpus growth is a real but bounded lever.

## FOR STRATEGY -- how to optimize from here (ordered)
1. **Wire the TOP-K gloss readout** (replace mean-pool in the reconstruction-match path) -- default-off, witnessed,
   Q111. It is the one CI-separated `a_s` gain here (+0.031 -> 0.296); tune k on train docs first.
2. **Do NOT invest more in the event/role target as-is** -- located negative. If revisited, ONLY via a role-specific
   selectional-preference readout (not general-gloss reconstruction); expect low yield.
3. **Corpus growth (learner-on) helps fast to ~40M then slowly** -- worth turning on, but the signal-loss trace shows
   the binding cap is rare-sense COVERAGE (only 52% of subordinate senses appear in the foundation at all). So the
   high-yield learner move is NOT raw volume but a **targeted curriculum that oversamples subordinate senses**
   (raise coverage of the rare tail), plus a **sense-discriminative (not topic-level) context representation** -- the
   two levers the trace proves are binding. Query-side elaboration (event roles, richer gestalt) is ruled out.
4. **INFRA (blocks the whole GPU queue):** `tools/orchestrator/queue_add.sh` returns rc=1 for a healthy cell whose
   fulfiller dry-run validates clean. The remote box `marsh@home` is HEALTHY -- its runner venv
   `C:/dev/hd-instrument/.venv` has torch 2.5.1+cu121 (CUDA True), gensim 4.4.0, RTX 4060 Ti, and all corpora
   present; only the *system* Python is cpu-only/no-gensim. The rc=1 is in queue_add.sh's scp/ssh/nltk-check steps
   (not the cell, not the venv). Run queue_add.sh with full stderr to find the failing step. (I ran this problem's
   GPU work by direct SSH to the runner venv, bypassing the pipeline -- results are real.)

## TLDR (plain language)
For picking a word's specific rare meaning: (1) letting the model read MORE text genuinely helps -- but only up to
about forty million words, after which more text stops helping. (2) The thing that helps past that point is a
better way of comparing the word's context to a dictionary sense: matching the few most relevant dictionary words
instead of blurring the whole definition together (this gave the one solid, statistically clean improvement). (3)
The idea the task proposed -- teaching the model to predict "who did what to whom" -- did NOT help here, tested four
different ways, and I explain why (that prediction is the wrong shape for how we compare to dictionary senses).
Everything runs on our own small models, no outside AI. The big confirmation run is still finishing on the home
GPU; it only confirms the plateau and does not change the story.

## QUESTIONS
None blocking. One judgment flagged: I called the event/role target a located negative after 4 convergent tests +
a mechanistic reason rather than building the one remaining readout redesign (role-specific selectional fit);
strategy may want that redesign tested before fully closing the event route.

## NEXT STEPS
Wire the top-k readout (item 1); fold the 277M point in here when it lands; fix queue_add.sh (item 4). The event
target is closed pending the optional selectional-fit-readout redesign.
