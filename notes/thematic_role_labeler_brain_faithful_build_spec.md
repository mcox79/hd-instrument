# Thematic-role labeler — brain-faithful build spec (Component 3, goal-owner pipeline)

**Status:** design drill, no cell run. Ready to build. Supersedes nothing; extends
`notes/goal_owner_attribution_pipeline_brain_fidelity_audit.md` (Component 3 finding: MISSING-ENTIRELY,
load-bearing). All organs/data below are disk-verified this session (paths, functions, actual metrics
read from `metrics.json`, not names/docstrings trusted at face value).

---

## 1. BIOLOGY (lead)

**Mechanism:** verb argument-structure processing in posterior/mid temporal cortex (pMTG/STS) + IFG
(Broca's-area homolog), formalized by MacWhinney's **Competition Model**: a role label (AGENT / PATIENT
/ EXPERIENCER / GOAL / RECIPIENT / INSTRUMENT) is assigned by **integrating multiple probabilistic
surface cues** — word order, animacy, case/voice marking — **weighted by each cue's CUE VALIDITY**
(how reliable that cue is in the language), combined with the **verb's lexical-semantic selectional
frame** (which roles this specific verb licenses: experiencer-subject "fear/like" vs agent-subject
"kick"; ditransitive "give" licensing AGENT/RECIPIENT/THEME).

**Why cue-integration, not position, is the correct SHAPE.** Agrammatic-aphasia evidence
(Grodzinsky; Caramazza & Zurif) shows role assignment fails specifically when **word-order cues are
stripped by passivization** — patients with intact single-cue (animacy) processing but damaged
syntactic-cue integration mis-assign roles on passive/reversible sentences while doing fine on
active canonical ones. This is the direct falsifier of a positional heuristic: **a system whose SHAPE
is "position=role" cannot, by construction, pass the passive/non-canonical generalization test** — it
will get every canonical sentence right (position and role correlate there) and collapse exactly where
the brain's cue-integration degrades gracefully instead of collapsing (other cues, e.g. animacy and
verb-frame, still fire and partially compensate).

**SHAPE:** verb-frame retrieval (lexical-semantic knowledge) + multi-cue probabilistic integration
(word order, animacy, voice) → a role label per (verb, argument) pair, generalizing across active /
passive / ditransitive / experiencer-subject constructions.

**POSITION:** mid-level; consumes lexical-semantic verb knowledge + a syntactic parse; is the DIRECT
upstream input to situation-model binding (Component 4, `AccumulateRegister`) and to coherence-based
role-fit selection (Component 5). Confirmed by the pipeline audit: both downstream components are
correctly built and FAITHFUL but currently starved by this missing upstream stage.

**METRIC:** role-assignment accuracy stratified by construction type. The diagnostic is specifically
**generalization to passive / non-canonical word order** — a positional heuristic is definitionally
unable to pass it; a genuine cue-integration mechanism degrades gracefully rather than collapsing.

---

## 2. REUSE MAP (disk-verified this session — do not trust names, code was read)

| Asset | What it actually is (verified) | Role in the new labeler |
|---|---|---|
| `hdlab/animacy_lexicon.py` | WordNet-hypernym-closure lookup, `lookup_animacy(word, pos_tag) -> {animacy, category, agent_capable}`. Guards two named collision modes (pronoun/symbol, proper-noun/homograph). **Already ships `scrambled_lookup_factory()`** — a deterministic permuted-control generator built for exactly this kind of can-fail ablation. Registry: `animacy_lexicon_wordnet_glassbox`, WIRED but `WIRED_BUT_NOT_PIPELINE_REACHABLE` (used only by `exp_extraction_commit_then_revise_v4_animacy.py` today). | ANIMACY CUE + its own negative control, reused verbatim. |
| `hdlab/candidate_generator.py` | `CandidateGenerator` composes a persisted UPOS tagger + an **unlabeled** arc-factored perceptron parser (UAS ~0.79, margins exposed). `candidates_from_parse()` emits `(verb_idx, arg_idx)` pairs tagged by which rule fired (`core_dep` / `relcl_gap` / `coord` / `conj_obj`) — explicitly documented as unable to tell subject from object. | WORD-ORDER / DEPENDENCY-ARC CUE source: (pre/post-verb position, arc-rule tag, token distance from predicate). Does **not** currently detect voice — see gap below. |
| `hdlab/coref.py::parse_litbank_conll` | `is_subject` field (line 234) is **NOT syntactic** — it's `rank == 0` where rank orders a sentence's referring mentions by raw token position (first-mention-in-sentence heuristic, the same class of signal as `_assign_roles`). Confirms the audit's SHAPE-mismatch finding independently. | One more WORD-ORDER-class cue, not a syntactic-subject cue — folded into the word-order feature, not treated as a separate authoritative signal. |
| `hdlab/situation_reader.py::_assign_roles` | AGENT = subject-mention-if-before-predicate-else-nearest-preceding; PATIENT = nearest-following. Purely positional. Independently re-derived here (matches the audit's 0.231-vs-1.0-oracle figure — this is the organ that figure was measured on). | The organ this build **replaces**, not extends (its SHAPE is the defect). Its I/O contract (consumes nominal-mention dicts, emits AGENT/PATIENT strings) is kept — new labeler is a drop-in with the same call signature, extended to emit EXPERIENCER/RECIPIENT/GOAL too. |
| `hdlab/event_bundle.py` | `DEFAULT_ROLES: Tuple[str,...] = ("PRED","AGENT","PATIENT","TENSE")` is a **configurable constructor parameter** (`roles: Sequence[str] = DEFAULT_ROLES`), not a hardcoded enum — verified by reading `EventBundleCodec.__init__`. | Output vocabulary target. Extending to `(PRED, AGENT, PATIENT, EXPERIENCER, RECIPIENT, TENSE)` requires **zero changes to `event_bundle.py`** — pass the extended `roles` tuple at construction. No new organ needed here. |
| `experiments/exp_path1_srl_mwp_cpu_v1.py::_train_role` | An **averaged-perceptron per-argument-feature → role-label classifier** (`_role_feats` builds `[prev-token, next-token, next-next-token, position-bucket, context-cue-words]`; standard averaged-perceptron training loop). Disk-verified metrics: `HARD_FAIL` (acc 0.3268 vs 0.39 baseline), but the cell's own verdict attributes this to **corpus size** (n_srl_train=30, a hand-authored 30-example set) and a wrong domain (math-word-problem `ARG1_qty` roles, not narrative AGENT/PATIENT/EXPERIENCER) — not a mechanism failure. | **Reuse the training-loop pattern verbatim** (averaged perceptron, feature-dict → per-role score, argmax) for the new labeler's cue-integration learner. This is disk-proof the architecture class is buildable in this codebase; do not re-derive it from scratch. Do NOT reuse its corpus or role vocabulary. |
| `experiments/exp_read_events_fix_role_reader_litbank_v1.py` (the `D.ORC/D.M/D.E` chain) | A **second, separate** real-text role-reading effort, distinct from `situation_reader.py`. Measured (disk-verified `metrics.json`): `gate1_mcguffey.reader_f1 = 0.592` vs `naive_f1 = 0.341` (HARD_PASS margin 0.251) on McGuffey gold; `gate2_litbank` noise-rate reduction is MIDDLE_BAND (rel_reduction 0.120). Its "reader" is still positional-agent + a WordNet-animacy **post-hoc noise filter** (`is_inanimate_agent`), not verb-frame/multi-cue integration at the assignment step — animacy here GATES/reports, it does not vote. | **This is the stronger real baseline to beat**, not the 0.231 figure alone — see Section 5. Also: `situation_reader.py`'s docstring cites an uncorroborated "F1~0.64 on McGuffey LCCP gold, atom 29502" that no file on disk substantiates (searched; zero hits beyond the self-citation) — **flagged, not propagated**, same discrepancy class the pipeline audit already caught once in Component 2. Use the disk-verified 0.592 number instead. |
| `experiments/exp_read_events_supply_parse_nsubj_litbank_v1.py` | **Directly informs the make-or-break design constraint.** Supplied spaCy's dependency parse (`nsubj`/`nsubjpass`, ascending the head chain through participles) as a **hard override** for agent selection. Disk-verified verdict: `CLEAN_NEGATIVE`, `net_fix = -182` (fixed 68 real errors, matches the pre-registered 70-92 estimate, but **250 over-attribution breaks dominated** — spaCy's own parser errs on 19th-century prose enough that a single-cue hard override nets negative). | **Direct evidence for cue-INTEGRATION over cue-SUBSTITUTION.** A deterministic single-cue swap catastrophically fails when that cue is noisy on this genre. A weighted-integration mechanism is structurally robust to exactly this failure mode: a noisy voice/parse cue gets outvoted by animacy + verb-frame + other cues instead of unilaterally overriding. This is the strongest argument in this spec for the earned-integration requirement, not just a biology appeal — it is a **measured, on-this-corpus demonstration of why the naive alternative fails.** |
| `hdlab/pos_tagger.py`, `hdlab/arc_parser.py` | Checked directly for voice/passive detection: **none exists.** No `passive`/`voice` string anywhere in either file. | Gap — see Section 3, item (i). A new glass-box passive-voice **cue detector** (not a mechanism) is needed; built as a hand pattern (BE-aux + past-participle POS sequence, optional trailing "by"-PP), same KNOWLEDGE-class status as `animacy_lexicon.py`, explicitly NOT a repeat of the spaCy-supply failure — see below. |

No HIGH-tier island (`ToM`, `grounded-appraisal`, `VAMP-EP`, `action_selection`, `slot_attention_wm`) contains
a thematic-role extractor — re-checked against `notes/capability_reconciliation_invisible_islands_audit.md`.
Confirmed **BUILD NEW**, composed from the reusable pieces above.

---

## 3. THE EARNED CUE-INTEGRATION MECHANISM

### Supplied (glass-box knowledge — acceptable per project convention; the MECHANISM must be earned, not the vocabulary)

- **(a) Verb selectional-frame table.** A small hand-authored dict `verb_lemma -> frame`, e.g.:
  `"kick": {"subj":"AGENT","obj":"PATIENT"}`, `"fear": {"subj":"EXPERIENCER","obj":"STIMULUS"}`,
  `"give": {"subj":"AGENT","iobj":"RECIPIENT","obj":"THEME"}`. Same status as `animacy_lexicon.py` /
  CSKG (supplying knowledge, not the reading mechanism). Seed it from the existing McGuffey/LitBank verb
  vocabulary (frequency-ranked, ~150-300 lemmas covers the bulk of narrative-prose tokens per Zipf) plus
  a small closed class of experiencer-subject/psych verbs (fear, like, hate, want, know, believe, see,
  hear, feel...) since these are the constructions where positional heuristics are known to fail hardest.
- **(b) Animacy lookup** — reuse `hdlab/animacy_lexicon.py::lookup_animacy` verbatim (already WIRED).
- **(c) Dependency-arc structure** — reuse `hdlab/candidate_generator.py::candidates_from_parse` verbatim
  (already WIRED, UAS ~0.79) for word-order/arc-rule features.
- **(d) NEW: passive-voice surface detector** (to be built, ~30 lines, symbolic pattern-match, no learning):
  `is_passive_clause(tokens, pos_tags) -> bool` — BE-auxiliary (`is/was/were/be/been/being`) immediately or
  near-adjacent to a past-participle-tagged verb, optionally followed by a `by`-headed PP. This is a
  KNOWLEDGE/DETECTION-class rule (like the animacy lookup), not the role-ASSIGNMENT mechanism — it emits
  one boolean CUE VALUE per clause, fed into the integration step below as one more feature, never as an
  override. This explicitly avoids repeating the `exp_read_events_supply_parse_nsubj_litbank_v1` failure
  mode (a hard override on a noisy external-parser signal); the passive detector here is intentionally
  self-contained regex/POS-pattern (glass-box, in-repo, no spaCy dependency) precisely because the prior
  cell showed borrowed-parser noise on 19c prose is real and must be integration-absorbed, not trusted.

### Earned (learned from data, glass-box inspectable — this is the actual deliverable)

For each candidate `(verb_idx, arg_idx)` pair from `candidate_generator.py`, build a feature vector:

```
feats = [
    "order:pre" | "order:post",              # word order relative to predicate
    "dist_bucket:0" | "dist_bucket:1" | ...,  # token distance from predicate, bucketed
    "arc_rule:core_dep" | "arc_rule:relcl_gap" | ...,   # candidate_generator's rule tag
    "animacy:animate" | "animacy:inanimate" | "animacy:unk",   # animacy_lexicon lookup
    "frame_slot:AGENT" | "frame_slot:PATIENT" | "frame_slot:EXPERIENCER" | "frame_slot:none",
        # what the verb's selectional frame licenses for a nominal in THIS syntactic position
        # (subj-position -> frame["subj"], obj-position -> frame["obj"], etc.)
    "voice:active" | "voice:passive",         # the new passive-voice detector
    "voice_x_order",                          # interaction feature: voice AND order combined
                                               # (this is the feature that must carry passive-sentence
                                               # AGENT-in-object-position, PATIENT-in-subject-position)
]
```

Train an **averaged perceptron** (reuse the exact training loop from `exp_path1_srl_mwp_cpu_v1.py::_train_role`
— same feature-dict-in, weighted-vote-out, argmax pattern, disk-proven to run in this codebase) mapping
`feats -> role label` (AGENT / PATIENT / EXPERIENCER / RECIPIENT / GOAL / none) on a role-labeled TRAIN
split. The learned per-`(feature, role)` weight **is** the cue validity (MacWhinney's term, operationalized
directly): a large `|weight|` on `voice_x_order` for the AGENT class after training means the mechanism has
learned that word order alone is unreliable once voice flips it — that is the earned integration, not a
hand-set rule.

**Per-decision glass-box inspection:** for any single prediction, the sorted list of
`(feature, weight, contribution)` is directly printable — satisfies the inspectability requirement without
any additional instrumentation (the averaged-perceptron score IS a sum of interpretable per-feature terms).

---

## 4. DATA

**What exists:**
- `data/litbank/{entities,coref,events,quotations,tagger}` — confirmed by directory listing: **no SRL /
  thematic-role layer** in LitBank natively. `events/` is event-mention detection (is-this-token-an-event),
  not argument-role annotation.
- McGuffey gold used by `exp_read_events_fix_role_reader_litbank_v1.py::gate1_mcguffey` — real predicate/
  agent/patient gold exists and is scored (F1 0.592 disk-verified), but the underlying gold file's
  construction-type distribution (active vs passive vs ditransitive) has **not been checked or stratified**
  by any cell found on disk.
- `experiments/data/srl_corpus_mwp_minimal_v1.jsonl` — 30 hand-authored examples, but wrong domain (math
  word problems) and wrong role vocabulary (`ARG1_qty` etc., not AGENT/PATIENT/EXPERIENCER). Not directly
  reusable, but its **existence proves the "hand-author ~30 construction-labeled examples" pattern is
  precedented in this codebase** (same file format, same effort scale) if the auto-stratification route
  (below) comes up short.

**CRITICAL GAP — flagged explicitly, not hand-waved:** no construction-VARIED (passive / ditransitive /
experiencer-subject) role-labeled gold set is confirmed to exist anywhere on disk. This is exactly the
data the generalization test requires and it is a genuine **data sub-task**, not a detail to defer silently.

**Recommended two-track resolution (do both, in this order):**
1. **Auto-stratify existing real gold first (cheap, real-distribution, no new annotation).** Run the new
   passive-voice detector (Section 3d) + the verb-frame table over the McGuffey gold sentences already
   scored by `gate1_mcguffey` and over LitBank sentences with events-layer predicates; bucket into
   canonical-active / passive / ditransitive / experiencer-subject by surface pattern. This is nearly free
   (the detector is ~30 lines) and yields a REAL-TEXT non-canonical test set if 19th-century narrative
   prose contains enough passives (plausible but unverified — literary prose does use passive for scene-
   setting, e.g. "the letter was written by...", but agent-first active dominates the genre, so the yield
   could be thin).
2. **If (1) yields too few non-canonical examples** (a real risk — flag this now rather than discovering it
   mid-build): hand-author a small construction-diversity probe set, same effort/format as
   `srl_corpus_mwp_minimal_v1.jsonl` (~30-50 examples), explicitly covering active/passive/ditransitive/
   experiencer-subject in the AGENT/PATIENT/EXPERIENCER/RECIPIENT vocabulary. This is a bounded, precedented
   task (the MWP corpus is the existing template), not new methodology.

Do not skip straight to (2) without attempting (1) — a hand-authored set alone risks the same
corpus-size failure that sank `exp_path1_srl_mwp_cpu_v1.py` (HARD_FAIL attributed to n=30 being too small
to learn stable cue weights); real-distribution data from (1) should be the backbone, with (2) as a
targeted supplement specifically for the constructions (1) under-samples.

---

## 5. PRE-REGISTERED GENERALIZATION TEST (the falsifier)

**Protocol:** train/tune cue weights on the CANONICAL (active-voice, natural-distribution) subset of the
combined McGuffey+LitBank gold. Test, held out, on the auto-stratified (or supplemented) PASSIVE /
ditransitive / experiencer-subject subset.

**Baselines (both, not one — they measure different things, keep them separate):**
- **Positional baseline A** (`situation_reader.py::_assign_roles`): 0.231 acc vs 1.0 oracle (audit-cited,
  re-derived here).
- **Positional baseline B** (`exp_read_events_fix_role_reader_litbank_v1.py` reader chain): 0.592 F1 vs
  0.341 naive (disk-verified, the currently-deployed stronger baseline). **The new labeler must beat
  whichever baseline is measured on the SAME corpus/metric it is compared against — do not cherry-pick the
  weaker one.**

**Controls (mandatory, anti-tautology):**
- **Validity-scramble control:** after training, randomly permute the learned `(feature, role)` weight
  vector (same permutation-control pattern as `animacy_lexicon.py::scrambled_lookup_factory` — reuse that
  exact discipline). If scrambled-weight performance does not collapse toward chance/floor, the "learned"
  weights are not actually doing the discriminating work.
- **Single-cue ablation:** re-run integration using ONLY word-order, ONLY animacy, ONLY verb-frame, ONLY
  voice, each in isolation. If any single-cue ablation reproduces the full-integration result within
  noise, the "integration" is a disguised single-cue rule (this is the check `decode_coherence_margins`'s
  history warned about — a signal that LOOKS structural but is positional-in-disguise, per the
  `exp_coherence_role_conflict_crosstalk_v1` `HARD_FAIL_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL` precedent).

**HARD-PASS:** full cue-integration model beats the matched positional baseline **specifically on the
non-canonical (passive/ditransitive/experiencer-subject) held-out subset** by a pre-registered margin
(recommend >= 0.15 absolute over positional-baseline accuracy on that subset, since positional is
expected to be near-floor there by construction) AND the validity-scramble control collapses (>= 0.10
absolute drop) AND no single-cue ablation matches the full model within 0.05 absolute on the non-canonical
subset.

**HARD-FAIL:** any of — (i) matches baseline on canonical but stays at-or-below baseline on non-canonical
(positional-in-disguise, the exact failure mode `_assign_roles` was built to have); (ii) a single-cue
ablation (most likely animacy-only, since it is the highest-coverage supplied cue) reproduces the full
model within 0.05 on non-canonical (not genuine integration); (iii) validity-scramble does not collapse
performance (weights are decorative).

**MIDDLE-BAND:** beats positional baseline on non-canonical but by less than the HARD-PASS margin, or one
control (not both) shows partial degradation — right mechanism class, underpowered (the same honest
classification `coherence_selector_v3` used for its 1-hop 0.87 result).

---

## 6. P_deflated + biggest risks

**P_deflated = 0.40.** (This is a design-synthesis over disk-verified internal evidence, not an external
lit-scan — no lit-scan calibration penalty formula literally applies, but the same discipline is used:
deflated from a naive ~0.60 because of three concrete, disk-grounded risk factors below, capped conservatively
since this is a novel-synthesis build, not a replication.)

**Biggest risks, ranked:**
1. **Data risk (highest): the auto-stratified non-canonical subset may be too thin to power a real
   generalization test on 19th-century narrative prose**, which is heavily agent-first/active by genre
   convention. If passive/ditransitive/experiencer-subject sentences are rare, the held-out test set could
   be single-digit-N, making HARD-PASS/HARD-FAIL classification unreliable regardless of mechanism
   quality. Mitigation is already specced (Section 4, track 2) but adds hand-authoring effort.
2. **Earned-integration collapsing to a single dominant cue** — animacy is the highest-coverage, most
   reliable supplied cue in this genre (per `exp_read_events_fix_role_reader_litbank_v1`'s F1 0.592 win
   coming substantially from an animacy-adjacent gate already); a real risk is the perceptron learns to
   weight animacy so heavily that voice/verb-frame become vestigial, which the single-cue-ablation control
   is specifically built to catch — but if it fires, the fallback is not "abandon integration," it's
   "the corpus doesn't have enough voice-conditioned signal to teach the voice cue's validity," which
   folds back into risk (1).
3. **The new passive-voice detector inherits some of the same 19c-prose-noise risk** that sank the spaCy-
   nsubj supply experiment, though at much smaller surface area (a boolean voice flag is far cheaper to get
   wrong than a full dependency-parse subject substitution, and it enters as ONE feature among ~7 rather
   than a hard override — this is exactly the structural mitigation Section 3 argues for, but it is not a
   guarantee; if the detector's false-positive rate on 19c "was + adjective" constructions (e.g. "was
   happy" mistaggable near past-participle patterns) is high, it adds noise to the integration rather than
   signal, which the ablation control will also surface).

---

## Reference to prior audit

Full component-by-component brain-fidelity ranking (Components 1-6, this component's context) lives in
`notes/goal_owner_attribution_pipeline_brain_fidelity_audit.md`. This spec extends only Component 3;
Components 2, 4, 6 are independently confirmed FAITHFUL and should not be re-touched without new evidence.
Component 5 (coherence scoring) is the natural next build once this labeler ships real (non-tautological)
role labels for it to score over.
