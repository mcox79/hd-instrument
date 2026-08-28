---
priority: 3
review:
review_text:
---

# PROBLEM: the coreference NAME/NOMINAL branch clusters mentions by single-head-token overlap, so it SHATTERS one character's different names ("Elizabeth" / "Bennet" / "Lizzy" / "Miss Bennet") into SEPARATE entities — 65.6% of multi-name characters split, name-mention purity 0.819 — and THIS (not the now-solved pronoun link) is the measured bottleneck capping the whole who-did-what / entity-tracking stack (oracle-coref 0.62 vs the live binder 0.17). Build the brain-faithful cross-mention entity resolution (a new mention COMPLETES to an existing person-entity or SEPARATES into a new one), validate cluster quality CI-separated over the token-overlap floor on real narrative with the info-free twin losing, and SERVE the who-did-what lift toward the oracle ceiling

**slug:** `the_name_branch_shatters_one_character_into_many_entities` — **opened:** 2026-08-28 by the strategy session
(surfaced + MEASURED as the #1 highest-leverage adjacency by the integrated `coreference_is_capped_at_065_on_real_narrative`,
owner-DONE/EXCELLENT: its adjacency 2). **status:** OPEN — a MECHANISM + INSTRUMENT problem. You build + validate in
`experiments/`; strategy lands any hdlab change (Q111). This is the UNTOUCHED half of coreference — the pronoun-antecedent
half was just solved (graded cue-based retrieval); the name/nominal ENTITY-CLUSTERING half is now the binding constraint.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGHEST-leverage of the open builds: name
> clustering caps the ENTIRE downstream stack (who-did-what, entity tracking, the situation model, the SPACE register, the
> ToM cue all need a character's mentions unified). The just-integrated coref work proved the pronoun LINK is NOT the
> who-did-what bottleneck — this clustering is (oracle-coref 0.62 vs binder 0.17). A correctly-bound pronoun cannot
> retrieve its referent's events when the referent's identity is scattered across many entities. **Re-rank per the owner.**

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When you read a novel, "Elizabeth", "Miss Bennet", "Lizzy", "Elizabeth Bennet" and "her" are ALL one person — you keep a
single mental file for that character and file every mention under it. Our reader does not. The coreference NAME/NOMINAL
branch (`hdlab/coreference_resolver._resolve_name_branch`) decides whether two name mentions are the same entity by
TOKEN-OVERLAP (Jaccard) — and because the mention store gives it only a single HEAD TOKEN per mention, "Elizabeth"
{elizabeth} and "Bennet" {bennet} share ZERO tokens, so they become TWO separate people. Measured on real narrative
(LitBank, 100 novels): **65.6% of multi-name gold characters are SHATTERED** (their name mentions split across ≥2
predicted entities), 19.5% of predicted clusters wrongly MERGE ≥2 gold characters, name-mention purity 0.819. The damage
is downstream and large: a pronoun that was resolved CORRECTLY still cannot retrieve its referent's actions when that
referent's identity is scattered — the who-did-what decode sits at **0.17 (COMMIT/ABSTAIN/RANDOM alike) vs ORACLE-coref
0.62**. The just-integrated pronoun solver PROVED the pronoun LINK is not the bottleneck; THIS clustering is. The task:
build the brain-faithful cross-mention entity resolution (unify a character's aliases into ONE entity), validate the
cluster quality beats the token-overlap floor CI-separated on real narrative (info-free twin losing), and SERVE the
who-did-what lift toward the oracle ceiling — so it is WIRED, not islanded.

## 2. WHY THIS ONE
Highest leverage of the open builds: name/entity clustering is the SHARED foundation under who-did-what, entity tracking,
the situation model, the SPACE location register, and the ToM observation cue — every one of them needs a character's
mentions unified before it can bind anything to that character. It is the measured cap (oracle-coref 0.62 vs 0.17), it is
a genuinely MISSING competence (the pronoun half is solved; the name half is single-token string overlap), and fixing it
unblocks a whole line at once. It is the natural successor to the coref integration, which named + measured it precisely.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** cross-mention entity identity is CONTENT-ADDRESSABLE resolution — different surface forms
  of one person CONVERGE on a single **person-identity node** (Bruce & Young 1986 PINs; the anterior temporal lobe as the
  semantic hub for unique/person-specific knowledge — Patterson, Nestor & Rogers 2007). The decision "is this new mention
  the same person or a new one?" is exactly **hippocampal pattern SEPARATION vs COMPLETION** (DG separates distinct
  entities; CA3 completes a partial cue to an existing one — the substrate ALREADY has `dg_pattern_separation` and CA3
  organs). At the discourse level this is the file-card / discourse-referent update (Heim 1982 file-change semantics; Kamp
  DRT): each entity is a card, and a mention either updates the matching card (completion) or opens a new one (separation).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the FEATURE set that cues completion — full name SPAN (not a single
  head token), surname/given-name structure, honorific/title, inferred gender, and the local discourse context — and the
  merge-vs-separate THRESHOLD. Copy the COMPUTATION (content-addressable complete-or-separate onto a person node); SWEEP
  the features + threshold. A partial cue ("Elizabeth") should COMPLETE to the "Elizabeth Bennet" node; an incompatible
  one ("Mr. Darcy") should SEPARATE.
- **NOT brain-faithful:** single-head-token exact/Jaccard match (the measured trap that shatters aliases), a fixed
  alias dictionary, or an external neural coref system / LLM at inference (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the coref SOLVED (`coreference_is_capped_at_065_on_real_narrative`,
  adjacency 2 + 4) measured the shatter (65.6% of multi-name gold entities), the merge (19.5% of clusters), name-mention
  purity 0.819, and the downstream cap (who-did-what 0.17 vs oracle-coref 0.62) on LitBank 100 novels; it named the ROOT
  CAUSE — the LitBank mention cache (`data/litbank/who_did_what_events.json`) stores only a single HEAD TOKEN per mention,
  which starves any full-span feature. The substrate already has the content-addressable machinery
  (`dg_pattern_separation`, the CA3 completion organs) and its own gender/number agreement + name-gender inference.
- **INFERRED (to prove):** that a full-span, feature-cued content-addressable name-unification (complete-or-separate onto
  a person node) beats the single-token-overlap floor on real-narrative cluster quality, and that unifying the aliases
  lifts the who-did-what decode toward the oracle-coref ceiling.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The single-head-token Jaccard branch (`_resolve_name_branch`) IS the floor — do NOT reproduce it as your result;
  recompute it in-place on the same population as the baseline. Do NOT redo the PRONOUN branch (solved: graded cue-based
  retrieval). Do NOT use an external coref/LLM at inference (the invariant). REUSE `dg_pattern_separation` + the CA3
  completion organs (the content-addressable currency) and the substrate's gender/number agreement rather than
  hand-rolling. The masculine surname-bridge gender inference already in the resolver is DATA/gazetteer-level — extend the
  loader/features, not with a bespoke lookup table masquerading as a mechanism.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/coreference_resolver.py` (`_resolve_name_branch`, the token-overlap floor) and the coref SOLVED
  (`notes/problems/coreference_is_capped_at_065_on_real_narrative/SOLVED.md`, adjacencies 2 & 4 — the measurements + root
  cause). Read `hdlab/dg_pattern_separation.py` + the CA3 completion organ(s) — the content-addressable complete/separate
  currency. **The LitBank mention cache stores single head tokens** — you will likely need to extend the loader to carry
  full mention SPANS + the LitBank entity TYPE (PER/FAC/GPE/...) before any full-span feature can help (state how you built
  it + verify it). Gold clusters: LitBank coref (`data/corpora/litbank_coref_conll` / the cache's gold entity keys).
- `tools/experiment_index.py query "coref"` / `"cluster"` / `"entity"` / `"name"`. Audit: the COREFERENCE / ENTITY
  TRACKING entry + the newest §2b coref entry (which names this NAME/NOMINAL branch as the new open case).

## 7. THE BAR
PASSES only with ALL of:
1. **A cross-mention name/nominal ENTITY-CLUSTERING organ** (built in `experiments/`): content-addressable
   complete-or-separate onto a person-identity node over FULL-SPAN features (span, surname/given, honorific, gender,
   context). Copy the computation (pattern separation/completion); SWEEP the features + threshold.
2. **Cluster quality beats the token-overlap floor CI-separated on REAL narrative** (LitBank held-out). Use a standard
   coref clustering metric (B-cubed F, or homogeneity+completeness / name-mention purity+inverse-purity) recomputed on the
   SAME population as the current `_resolve_name_branch` floor. **The info-free twin (shuffled name features / random
   merge decisions) LOSES CI-separated.** Report CI half-width + null p95; no number crosses populations/scorers.
3. **A POSITIVE control the metric can move:** a re-entry alias case the merger gets and the single-token-overlap baseline
   cannot (e.g. "Elizabeth" ↔ "Miss Bennet"), so a null is interpretable.
4. **SERVES a downstream capability (wire-don't-island):** unifying the aliases LIFTS the who-did-what decode toward the
   oracle-coref ceiling (from ~0.17 measurably UP toward 0.62), CI-separated vs the current clustering on the same task —
   i.e. it is the shared foundation, not a second island.
5. **A one-screen summary:** features chosen → floor → twin → cluster metric → verdict → who-did-what lift. Route any
   heavy LitBank-scale runs to REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).
A rigorous NEGATIVE is a FULL PASS (e.g. "full-span content-addressable clustering does NOT beat token-overlap once the
cache is fixed — the real cap is X" — with the positive control confirming the metric can move — closes the question).

## 8. FILES AND ENTRY POINTS
- Floor + seam: `hdlab/coreference_resolver.py` (`_resolve_name_branch`). Content-addressable currency:
  `hdlab/dg_pattern_separation.py` + the CA3 completion organ(s). Data + root-cause fix:
  `data/litbank/who_did_what_events.json` (single-head-token — extend the loader to full spans + entity TYPE), LitBank
  coref gold. Prior measurement: `coreference_is_capped_at_065_on_real_narrative/SOLVED.md` (adjacencies 2 & 4). Audit:
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (COREFERENCE entry + §2b). Heavy runs → REMOTE.

## DO NOT QUOTE / DO NOT REDO
The 65.6%-shatter / purity-0.819 / 0.17-vs-0.62 measurements are the MOTIVATING evidence (from the coref integration), not
your result — recompute your own floor + headline on your own population. Do NOT rebuild the pronoun branch (solved). Do
NOT rebuild the (entity, role, event) binding. Strategy owns any hdlab landing — you propose the clustering organ (and any
loader extension), you do not write `hdlab/`.
