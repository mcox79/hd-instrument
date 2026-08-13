# Encoder path -- CORRECTION to `encoder_lineage_final_2026-08-13.md` (2026-08-13, later same day)

**This note SUPERSEDES two load-bearing claims** in `notes/encoder_lineage_final_2026-08-13.md`
(that note stays on disk; a superseded-by line has been added to its top):

1. "No final landed encoder exists -- the line was abandoned, not won." **FALSE.**
2. "The trained encoder does not beat its own random-init twin on synonym-vs-sibling
   (0.7064 vs 0.7452), so the pooling interface separates them." **NO EVIDENCE BEHIND IT** --
   the cell that produced those numbers loaded the WRONG CHECKPOINT, and was superseded 43
   minutes later by a confound-removed cell that reverses the sign.

Read-only investigation. No code in `hdlab/` or `experiments/` was modified.

---

## A. A learned encoder DID land, is clean at HEAD, and is registry-WIRED

| item | evidence |
|---|---|
| module | `hdlab/encoder_retrain_persist.py`, commit `367a42729` (2026-07-31), `git status --porcelain` clean at HEAD |
| registry | row `encoder_retrain_persist_generalizing_lever_reusable_v1`, `gate_decision: WIRE`, `integration_status: WIRED`, paths = the module + its wiring cell + its loader verifier |
| assets | `data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt`, 3 x ~109 MB, mtime 2026-07-31, **untracked by design** (too large for git) |
| runtime | all 3 seeds load OK (`d_model=512`); `experiments/verify_encoder_retrain_persist_loader_v1.py` returns OVERALL PASS |
| what it is | v2 TinyTransformer + **minimal top-1-layer unfreeze**, 3,153,408 trainable params, 220 steps. State-dict diff: exactly **14 of 76 tensors differ** from v2; `tok_emb` byte-identical |

**Why the earlier audit missed it.** Its runtime trace ("40 hdlab modules load, 0 encoders") was
CORRECT but measured the **DEFAULT path**. This module is **OPT-IN BY DESIGN**: its own docstring
states it "does NOT change any existing cell's default encoder -- nothing else imports this module
automatically. Any harness that wants the improved encoder calls `load_improved_encoder(...)`."
Absence from a default-path trace is therefore the module working as specified, not an island. The
plug point is already in the live loop: `hdlab/reading_grounding_loop.py` `process_sentence(...)`
(def at `:1006`) takes `encoder: Optional[StructuralEncoder] = None` at `:1011`, and
`_selftest_structured_encoder_is_off_by_default` at `:1945` asserts `encoder=None` is the shipped
path byte-for-byte.

## B. It HAS accuracy floors (the prior note said it had none)

All four are on disk with their control arms:

- `exp_encoder_alltype_transfer_v1` -- HARD_PASS 2026-08-01T01:04Z. 3/3 types:
  `a_name_maintenance` +0.192 (0.492 -> 0.683), `b_competitive_coref` +0.150 (0.492 -> 0.642),
  `c_overwrite` +0.320 (0.403 -> 0.723). Shortcut controls `global_last` 0.007-0.011 and
  `most_frequent` 0.057-0.070. Band: UNIVERSAL_LEVER, not coref-specific.
- `exp_encoder_alltype_transfer_stress_v1` -- HARD_PASS 2026-08-01T01:27Z. +0.050 to +0.231 across
  three stress conditions: harder difficulty, held-out eval draw, and an **INDEPENDENT entity-file
  harness** (so the win is not a `base_loop`-harness artifact).
- `exp_coref_encoder_transfer_v1` -- HARD_PASS 2026-08-01T00:29Z. `stage_ENT` 0.724 -> 0.858
  (+0.134); Tier-1 absolute 0.507 -> 0.652; delta 0.188 -> 0.239, all 3 seeds > 0.05.
- Recipe cert `exp_situation_model_assembly_encoder_retrain_scale_v1` -- CLEAN_PASS 2026-07-31.
  Chance 0.05; frozen wall 0.47-0.52 -> **0.830**; the must-fail **full-unfreeze control craters to
  0.2916** (the collapse guard fires as designed on degenerate config d6).

**SCOPE CAVEAT -- must travel with EVERY citation of these numbers.** The base is real ARC text,
but the DELTA and all transfer evals are the **SYNTHETIC situation-model harness**. Naturalistic
validation is PENDING. Coref absolute is **0.652, below the 0.70 bar**. This is a proven
representation-quality **LEVER for entity-addressed comprehension**, NOT solved comprehension --
which is exactly what the module's own docstring says ("HONEST SCOPE: a proven LEVER ... NOT solved
comprehension"). Do not upgrade it in transit.

## C. `..._heldout_v2` is NOT superseded by `..._v3_relobj`

The v3 cell **CHANGED THE TASK**. Its own prereg
(`preregs/2026-07-27_scale_meaning_learn_arc_heldout_v3_relobj.md:76-83`) states that the one
variable is the **training OBJECTIVE** (adding `L_rel` to `L_mlm`), and that v2's checkpoint is
**RELOADED, never retrained**, serving as the same-architecture zero-retrain BASELINE. v3's
`HARD_FAIL_ARCHITECTURE_BOUND` (margin -0.0046, `rel_loss` visibly decreasing) therefore means
*the added objective did not beat v2* -- it is a negative about the objective, not a retraction of
v2.

**v2 stands** (`exp_scale_meaning_learn_arc_heldout_v2`, HARD_PASS_CLEAN_WIN, 2026-07-27):
semantic AUC text 0.6356 vs raw 0.5968, random-init 0.5322, collapse-shuffle 0.4964, popularity
0.4968.

---

## D. The synonym-vs-sibling "wall" -- two independent defects

### D1. WRONG ARM: the diagnostic loaded the HARD_FAIL checkpoint

`experiments/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105`:

```python
CKPT_PATH = os.path.join(REPO_ROOT, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj",
                         "ckpt_seed_7.pt")
```

That is the **v3_relobj** checkpoint -- the `HARD_FAIL_ARCHITECTURE_BOUND` weights. Distinctness is
proven, not assumed: its sha256 differs from v2's, **all 76 of 76 tensors differ**, max |delta|
0.539. So "trained 0.7064 vs random-init 0.7452" tested **neither** the v2 HARD_PASS encoder
**nor** the landed asset in `data/exp_encoder_retrain_persist_v1/`. It is a measurement of a third,
failed artifact.

### D2. SUPERSEDED ANYWAY: the confound-removed cell reverses the sign

`data/exp_diag_synonym_sibling_confound_removed_v1/metrics.json`, run 2026-08-12T03:54:01Z -- **43
minutes after** the cell it supersedes. It balances concreteness (the confound the first cell had
itself flagged: `conc_z_gap_sibling_minus_synonym` **1.6022**, reduced to **0.0406**, `balanced:
true`). On the MAIN set at n_syn=26 / n_sib=26:

| arm | AUC | d' |
|---|---|---|
| `main_trained` | **0.5888** | +0.292 |
| `main_randinit` | **0.4615** | -0.350 |
| `main_scramble` | 0.5074 | +0.193 |

**The trained model DOES beat its random-init twin** (+0.127) and its scramble (+0.081) once
concreteness is balanced. The 0.71-0.75 separation in the earlier cell was the concreteness
confound, on top of the wrong checkpoint.

**Caveat this note refuses to drop** (checked against the cell's own verdict, not just its
numbers): the cell's headline verdict is `MIDDLE_BAND_HELDOUT_UNDERPOWERED`. Its **DECISIVE**
(concreteness-balanced AND held-out) set is n=5/5 against a declared floor of 8, so it does not
gate; the cell explicitly labels the MAIN set "secondary, non-gating context isolating whether
concreteness alone ... explains the original 0.71". For the record the decisive set runs the same
direction (`decisive_trained` 0.72 vs `decisive_randinit` 0.60 vs `decisive_scramble` 0.64) but is
underpowered and licenses nothing.

**What this licenses, precisely.** It does NOT license "synonym-vs-sibling is solved". It DOES
remove the evidentiary basis for the claim that the trained encoder *loses* to a random-init twin,
and therefore for the "the pooling interface separates them" framing built on top of it. The
correct status of the synonym/sibling question is **OPEN and unmeasured at power**, not WALLED.

---

## E. Consequences for the steering docs

- `notes/STATUS.md` "ENCODER PATH -- NO FINAL LANDED ENCODER" heading and body: rewritten.
- `notes/STATUS_LESSONS.md` "ENCODER LINEAGE" section: refuted paragraphs replaced in place, per
  `STATUS_SPEC.md` sec 7 ("the superseding pointer replaces it in place").
- STANDING DISCIPLINE 4 ("establish the final landed version before evaluating a subsystem") gains
  instances 4-6 and a new sub-rule: **an absence claim requires an ENUMERATION, not a search.**
  The generative cause of both defects here is a search that could not have found its target: this
  note's assets are untracked 105 MB `.pt` files, its module is absent from a default-path trace by
  design, and a `grep` of `encoder_lineage_final_2026-08-13.md` for `alltype`,
  `coref_encoder_transfer` and `load_improved_encoder` returns **zero matches** -- the 2026-08-01
  cells were never enumerated at all.
