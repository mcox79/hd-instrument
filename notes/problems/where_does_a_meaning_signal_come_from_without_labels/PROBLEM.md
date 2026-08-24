---
priority: 1
review:
review_text:
---

> # 🥇 **PRIORITY 1 — FILED ON OWNER INSTRUCTION (board Q118, 2026-08-24): *"this should be a problem to give to a solver."***
> **This is the hardest open question in the project and it is filed as a problem rather than worked
> incrementally.** Three independent instruments agree: an ORACLE clears, and NOTHING unsupervised
> reaches it. **You are being asked where the supervision comes from when nobody hands over answers.**

# PROBLEM: EVERY ORACLE WE BUILD CLEARS THE BAR. NOTHING UNSUPERVISED REACHES IT. A CHILD IS NOT GIVEN THE ANSWERS.

**slug:** `where_does_a_meaning_signal_come_from_without_labels` · **opened:** 2026-08-24 by the
strategy session on owner instruction · **status:** OPEN

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

The test that matters: can the system tell that two words are **interchangeable** (*car / automobile*)
rather than merely that they **turn up together** (*car / drive*)? The second is easy. The first is
what meaning is.

On one test, one set of 242 word pairs, where guessing scores `0.486` and a right answer scores `0.960`:

- **Every method that counts which words appear near each other scores `0.02`–`0.13`.** That is not
  merely bad, it is **backwards** — they confidently rank words-that-co-occur as the interchangeable
  ones. Our own machinery is in that group at `0.0710`. Four tuning families moved it to `0.114` and
  no further.
- **The grounded sensory channel is the only thing pointing the right way at `0.599`** — but a
  control that gives **every word the same vector** scores `0.6195` and beats it. So it is not
  learning about individual words at all.
- 🔑 **And a model ALLOWED TO SEE THE ANSWERS reaches `0.9606` on data it has never seen.**

**So the information IS in the text. We cannot get at it without being told the answers.** A child is
not told the answers.

---

## 2. WHY THIS ONE

- **IT IS THE SAME MISSING PIECE THREE OTHER PROBLEMS FOUND SEPARATELY.** Each has an oracle that
  clears a floor nothing unsupervised reaches (§3). **Four routes, one hole.**
- **TWO PRE-REGISTERED `STOP_IF`s HAVE ALREADY FIRED** on the obvious family of fixes, so this cannot
  be answered by another transform of a co-occurrence matrix (§4).
- 🧠 **IT IS THE BRAIN QUESTION IN ITS SHARPEST FORM.** A child acquires substitutability without a
  labelled list. Whatever they use, we do not have it, and naming it is the whole task.

---

## 3. MEASURED vs INFERRED

### MEASURED — THE CONVERGENCE, THREE INSTRUMENTS, EACH AGAINST ITS OWN FLOOR

| instrument | ORACLE | best unsupervised | source |
|---|---|---|---|
| **substitutability** (242 pairs) | fitted, **HELD-OUT `0.9606`** | every transform `0.02`–`0.13`; ours `0.0710`; grounded `0.599` under a `0.6195` no-information floor | `exp_corpus_capacity_ppmi_svd_ceiling_v1` |
| **partial-cue identity** (5,490 lemmas) | `ORACLE_UNION` **`0.4082`** (`+0.0840` CI `[+0.0769,+0.0914]`) | counting `0.3242`; best store `0.2461` | `exp_recognition_store_calibrated_familiarity_recollection_v1` |
| **write rule** | `BEST_SINGLE_ORACLE` **`0.3033`** | `SUM_ALL` `0.0100`; `RANDOM_SINGLE` `0.0367` | `exp_writerule_step_ladder_v1` |

**Chance on the first instrument is `0.4862` and the known-answer arm reads `0.9599`, so the
instrument works and the failures are real.** *Info-free controls bind on all three.*

### ⚠️ AND ONE PLACE WHERE UNSUPERVISED COMBINATION *DOES* WORK — DO NOT IGNORE THIS
`exp_c3_grounded_fusion_v1`, on morphology-stripped gold: **fusing the distributional channel with
the grounded spoke reaches `0.0790` `[0.0707,0.0875]`, beating BOTH its own components
CI-separated** (grounded alone `0.0607`, bag alone `0.0459`), with `FUSE_RANDOM_GROUNDED 0.0291` as a
binding control. **That is unsupervised and it works.** *It is a different task from the 242-pair
instrument and the numbers may NOT be compared — but it means "unsupervised combination is hopeless"
is FALSE, and the honest question is narrower: it works when two channels are COMPARABLE and fails
when one is a DOMINATING PRIOR (the same grounded channel goes `0.4811` -> `0.1415` under a
frequency prior).*

---

### INFERRED — OVERTURNING ANY OF THIS IS A RESULT, AND ONE OF THEM IS LOAD-BEARING

- 🔻 **That the three instruments are showing the SAME missing piece.** *They are different tasks
  with different scorers, and I am the one who grouped them.* The shared shape is "an oracle clears,
  nothing unsupervised does" — **but that shape is also what you would see if each task simply had a
  different, unrelated hard part.** *This is my reading, not a measurement, and it is the premise the
  whole brief rests on. Overturning it is a full result.*
- 🔻 **That a non-label signal EXISTS at all for substitutability from this corpus.** The fitted
  oracle proves the INFORMATION is present. It does not prove any unsupervised procedure can reach
  it. **A rigorous demonstration that none can, on this corpus, is also a full result** — it would
  redirect the project to supplied knowledge with evidence instead of by fatigue.
- 🔻 **That "being corrected" is the biggest gap.** That was my recommendation on the board and the
  owner did not endorse it — they asked for the problem to be handed over instead. **Treat it as one
  candidate among several, not the answer.**
- 🔻 That the grounded fusion's success transfers to this instrument. **It has not been tried there,
  and the two tasks' numbers may not be compared.** *It is a reason for hope and nothing more.*

---

## 4. ALREADY TRIED — DO NOT REDO

- 🛑 **`exp_corpus_capacity_ppmi_svd_ceiling_v1`: `STOP_IF_iii_INFO_PRESENT_NO_UNSUPERVISED_FIRST_
  ORDER_TRANSFORM_REACHES_IT`.** PPMI `0.0249`, PPMI+SVD at k=50/100/300/500 `0.023`–`0.052`,
  second-order cosine `0.0510`. **Do not propose another unsupervised first-order transform of the
  co-occurrence matrix. That class is closed.**
- 🛑 **`exp_tuned_count_unsupervised_dissociation_v1`: `TUNING_IMPROVES_ON_VANILLA_BUT_STAYS_BELOW_
  0.5__SUPERVISION_CONCLUSION_SURVIVES_A_FAIRER_TEST`.** Four tuning families; best `0.1144`.
- 🔻 **The grounded channel alone does NOT clear its own floor on this instrument**
  (`exp_sensorimotor_channel_discrimination_v1`: `SM11_RAW_COSINE 0.599` vs its own
  `F_CONSTANT_PROTOTYPE 0.6195`). **Wiring the sensory norms in is not the answer here.**
- 🔻 **Reliability-weighted combination has a HARD_PASS and two HARD_FAILs already**
  (`exp_attention_salience_reliability_gate_*`): it works with an INDEPENDENT reliability estimate
  (`+0.0634`), is INERT when the estimate is DERIVED from the same evidence (**even at `auc 0.8303`**),
  and INVERTS under correlated/systematic error (`auc 0.3198`, below chance).
- 🔻 Max-pool and top-k-mean over occurrences are WORSE than summing (`0.0299` / `0.0217`–`0.0264`).

---

## 5. THE BAR

**PRODUCE A LEARNING SIGNAL THAT IS NOT A LABEL, AND SHOW IT MOVES A HELD-OUT TASK.**

1. **Name the signal and where it comes from.** It must be available to a system that is only
   reading, or acting, or being corrected by an environment — **not to one handed a gold list.**
2. **Score on a held-out task with its floor recomputed on that task's own population**, CI
   half-width and null p95 beside every margin.
3. 🚨 **THE DISQUALIFYING TEST, AND IT IS THE WHOLE POINT: if your signal is derived from the same
   resource the evaluation uses, you have rebuilt the oracle in disguise.** State explicitly what
   your signal would still know if WordNet, the gold, and the benchmark did not exist. *A control
   trained on the oracle's own labels must be shown to be a DIFFERENT thing from what you built.*
4. **An info-free twin of your signal must LOSE**, and — given the derived-reliability HARD_FAIL —
   **report your signal's predictive AUC and its task delta SEPARATELY.** A good AUC with a null
   delta is the documented failure mode, not a partial success.
5. **A clear negative is a full result** *if* it names what was tested and what the stronger version
   would be.

**REFUTING THIS IS THE HALFWAY POINT.** If the route you try fails, you have earned the right to
solve the underlying problem another way. **The underlying problem is: *a system that only reads has
no teacher, and we need one that is not a lookup table.*** Prediction error, environmental
consequence, agreement between independent channels, being corrected by another agent, curiosity
about its own uncertainty — all fair game. **Come back with "refuted" alone only if you have also
established that no route you could test supplies such a signal, and say which you tried.**

---

## 6. HOW THE BRAIN DOES THIS — **THE OPENING MOVE, NOT AN AFTERTHOUGHT**

**Ask which structure supplies the training signal when nobody labels anything.** Candidates worth
taking seriously, and you must label each PINNED-BY-EVIDENCE or OUR-INVENTION-UNDER-TEST:

- **Prediction error as a self-supervised teacher.** The brain predicts constantly and learns from
  the mismatch; no external label is required. *Note this repo has a landed dissociation
  (`exp_predictive_coding_write_gate_dissociation_v1`) where the gain was the GATING RATE and not the
  prediction error — read it before proposing this.*
- **Cross-modal agreement.** Two channels that see the same world and must agree can supervise each
  other. *This is the one with a live positive: the grounded fusion above.*
- **Social correction.** A child hears the right word used in the same situation. **We have NOTHING
  of this in any form** — which makes it the biggest gap and the easiest to fake. *If corrections are
  generated from a lexical resource, you have smuggled the answers back in.*
- **Consequence.** A word used wrongly produces a worse outcome in the world.

**Copy the COMPUTATION; sweep any PARAMETER.** Inventing is encouraged; mislabelling is the only
thing barred.

---

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the 242-pair instrument + the fitted oracle | `data/exp_corpus_capacity_ppmi_svd_ceiling_v1/metrics.json` |
| the tuned-count STOP_IF | `data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json` |
| the grounded channel on the same instrument | `data/exp_sensorimotor_channel_discrimination_v1/metrics.json` |
| **the unsupervised fusion that DOES work** | `data/exp_c3_grounded_fusion_v1/metrics.json` (`strip_bootstrap`) |
| the oracle-union ceiling | `data/exp_recognition_store_calibrated_familiarity_recollection_v1/` |
| the reliability-gate family | `data/exp_attention_salience_reliability_gate_*/` |
| the morphology strip (shared) | `hdlab/morphology_leakage.py` |

**WRITE:** `experiments/`, `verification/`, this folder. **NOT** `hdlab/`, **NOT** `preregs/**`,
**NOT** any `arm_key*`. `data/foundation/` is READ-ONLY.

---

## 8. DO NOT QUOTE

- 🚫 **`A5_STRINGCTRL` / `A6_TRIGRAM_ONLY` `0.0870` as a floor.** ~`78%` was morphological leakage;
  the honest value re-measured in its own harness is `0.0195`. **Score against morphology-stripped
  gold** (`hdlab/morphology_leakage.py`).
- 🚫 **`0.1125` as "the fusion clears the floor".** That arm includes the spelling channel on LEAKY
  gold; on fair gold it collapses to `0.0431`, **below the bag alone**.
- 🚫 **Any number from the 242-pair instrument against any number from the c3 task.** Different
  tasks, different scorers, different populations.
- 🚫 **The fitted oracle's `0.9606` as a capability.** It is a CEILING measured with the answers in
  hand. It says the information exists; it says nothing about reaching it.

---

## 9. VERIFY BEFORE YOU START — THE DISK OUTRANKS THIS BRIEF

1. `python tools/before_you_start.py "learn word meaning without labels"` — read **every** row.
2. `python tools/experiment_index.py query "substitutability"` — 7 cells. Read all seven.
3. `python tools/organ_map_cite.py A6_TRIGRAM_ONLY` — the floor is under correction.
4. `.venv/Scripts/python.exe verification/test_grounding_loses_to_counting_cooccurrence_at_power.py`
