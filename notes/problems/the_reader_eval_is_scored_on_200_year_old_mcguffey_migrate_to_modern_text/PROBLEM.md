---
priority: 1
review:
review_text:
---

# PROBLEM: the reader's comprehension EVAL is still scored on ~200-year-old McGuffey graded readers (1830s prose), a standing corpus-age confound the OWNER has asked to fix REPEATEDLY. The LEARNING corpus is already modern (Simple Wikipedia + textbooks), and the WHO-DID-WHAT eval already runs on LitBank (19c literary prose), but the ROLE-labeling / situation-model eval (the "57 McGuffey passages", McGuffey-as-CoNLL) and several organs (situation_reader, coreference_resolver, candidate_generator, animacy_lexicon, verb_lexical_similarity, ...) still lean on McGuffey. Archaic vocabulary/syntax scored against modern instruments is a mismatch, and — separately — it is simply not what a reader of MODERN text would face. MODERN annotated corpora are ALREADY ON THE SHELF (`data/corpora/`): `litbank_coref_conll` (real literary narrative, coref+entity gold, already in CoNLL), `ud_english_ewt` (modern web text, gold parse), `race` / `mcscript2` / `social_iqa` (modern narrative + QA), `onestop` (modern GRADED news at 3 levels). MIGRATE the reader-comprehension eval off McGuffey onto modern annotated text, revalidate the reader organs on it, and QUANTIFY the corpus-age delta (how much McGuffey was inflating or deflating each result). A rigorous result either way — "the organ results HOLD on modern text" or "here is exactly what changes and why" — is a full pass; the point is to stop reporting reader numbers on 1830s prose.

**slug:** `the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text` — **opened:** 2026-08-30 by the strategy session at the OWNER'S REPEATED, EXPLICIT request ("we keep using this 200 year old text ... I've asked for this like 10 times"). **status:** OPEN — a DATA-PREP (build a modern annotated eval) + REVALIDATION (re-run the reader organs on it, report the delta) problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant); an LLM may NOT be used to fabricate gold labels either — use EXISTING gold (LitBank/UD-EWT/RACE) or a transparent, auditable derivation.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1` — TOP priority. This is an owner-requested fix asked ~10 times, and it is a STANDING CONFOUND on EVERY reader result (each is currently caveated "McGuffey is 200 years old"). Fixing it makes every downstream number trustworthy and modern. Ranked above the reasoning-frontier problems (they can be re-scored on the modern eval once it exists). **Dependency web:** touches `situation_reader` + the eval harnesses (the assembly's McGuffey-as-CoNLL loader, `exp_wire_organs_endtoend_v1.load_gold`); consumes the on-shelf modern corpora. **⚠️ COORDINATE:** BUILD the modern eval + revalidate in `experiments/` (reader-independent); strategy sequences any hdlab default swap. **Re-rank per the owner** (but the owner explicitly wants this prioritized).

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
We keep testing the reader on 1830s schoolbook text (McGuffey). That's a double problem: the old words and grammar don't
match the modern dictionaries we score against, and it's just not the kind of text we actually want the reader to handle.
The owner has asked to fix this many times. The learning material is already modern (Wikipedia), and one of our tests (who
did what) already runs on more recent literary text — but the main "what role did each phrase play / who is who" test still
uses the old readers. Modern, properly-labelled text is already sitting in our data folder. Move the reader's tests onto
modern text, re-run the reader's components on it, and report clearly how much the old text was helping or hurting each
number. If everything holds up on modern text, great — that's a stronger claim. If some numbers change, that's exactly the
finding we want.

## 2. WHY THIS ONE
It is a standing, owner-priority confound on EVERY reader result. Right now each reader number carries an asterisk ("scored
on 200-year-old prose"); after this, they don't. It also directly de-risks the reasoning frontier (belief-timeline,
causation, QA capstone) — they can all be scored on the modern eval instead of inheriting the confound. And it is ENABLED,
not blocked: the modern annotated corpora are already downloaded and, in LitBank's case, already in the exact CoNLL format
the reader eats.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the framing):** a reader generalises to the text distribution it will actually face; validating comprehension on
  archaic prose and reporting it as general comprehension is a MEASUREMENT-fidelity error, not a brain-mechanism question.
  The brain's mechanisms (role assignment, coref, situation model) are the SAME; what must change is the EVAL DISTRIBUTION.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** WHICH modern corpus + WHICH gold. **Copy nothing new** — REUSE the
  existing reader organs unchanged; only the EVAL corpus + its gold change. **REUSE** on-shelf gold: LitBank coref/entity
  (`data/corpora/litbank_coref_conll`), UD-EWT gold parse/roles (`data/corpora/ud_english_ewt`), and, if you build a role
  gold, do it by a TRANSPARENT rule over existing annotations (e.g. UD dependency → thematic role), never an LLM.
- **NOT brain-faithful / NOT allowed:** fabricating gold labels with an LLM; cherry-picking a modern corpus where the organ
  happens to win; changing the ORGAN to fit the corpus (this problem changes the CORPUS, not the mechanism).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE):** the reader organs + their McGuffey results (the assembly's 57-passage role eval 0.517→0.742;
  who-did-what already on LitBank; the archaic-prose parse study `role_assignment_is_untested_on_archaic_literary_prose`,
  which found the parser survives 19c prose — so the parse is NOT the confound, MEANING/eval-distribution is). The on-shelf
  modern corpora (litbank_coref_conll, ud_english_ewt, race, mcscript2, onestop, simplewiki).
- **INFERRED (to prove):** that the reader's key results (role-labeling, coref, situation-model) REPRODUCE on a MODERN
  annotated eval CI-comparably to the strongest real floor recomputed on that modern population — OR, if they shift, a
  quantified per-organ McGuffey-vs-modern delta with the reason (which is the valuable rigorous result). The info-free twin
  must still LOSE on the modern eval (the organ's signal is real on modern text, not a McGuffey artifact).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT change any reader organ to fit the corpus (change the EVAL, not the mechanism). Do NOT use an LLM to label gold.
- Do NOT re-derive that the parser handles 19c prose (`role_assignment_is_untested_on_archaic_literary_prose` already did —
  the parse is fine; the confound is the eval DISTRIBUTION + archaic meaning scored on modern gold). Do NOT keep McGuffey as
  the PRIMARY eval "because the gold exists" — that is exactly the status quo the owner is rejecting.
- The learning/grounding corpus is ALREADY modern (simplewiki + textbooks) — this problem is about the EVAL, not learning.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- `python -c "import hdlab.corpus_registry as C; print([s for s in C.enumerate_corpora()])"` to see the enumerated shelf +
  which entries are READABLE_PROSE. Inspect `data/corpora/litbank_coref_conll` (CoNLL coref/entity gold — the readiest
  drop-in), `data/corpora/ud_english_ewt` (gold parse → derive roles), `data/corpora/race` + `mcscript2` + `onestop`
  (modern narrative; check what gold each ships). Read the assembly's McGuffey-as-CoNLL loader
  (`experiments/exp_wire_organs_endtoend_v1.load_gold` / `_passage_aliases`) and `situation_reader.read()` (the CoNLL it
  eats) — the modern eval must produce the SAME shape. Grep `mcguffey` across hdlab to see every organ that leans on it.
  **The corpus-age confound is the THING BEING MEASURED here — quantify it, do not hand-wave it.**

## 7. THE BAR
PASSES only with ALL of:
1. **A MODERN annotated reader-comprehension eval** (built in `experiments/`, in the reader's CoNLL shape): real modern (or
   at minimum 20c/21c, NOT 1830s) narrative/prose with EXISTING or transparently-derived gold for the reader's dimensions
   (role/who-did-what AND coref/entity at least). Name the corpus + the gold provenance. NO LLM-fabricated gold.
2. **The reader organs REVALIDATED on it** — re-run role-labeling + coref + (where gold exists) the situation-model readouts
   on the modern eval; each key result must beat its strongest floor recomputed ON THE MODERN POPULATION, with the info-free
   twin LOSING CI-separated; report CI half-width + null p95. NO number crosses populations (McGuffey and modern are
   separate populations — report both, never average).
3. **The McGuffey-vs-modern DELTA, per organ** — quantify how much the corpus-age confound moved each number (a controlled
   comparison: same organ, McGuffey population vs modern population). This is the deliverable that retires the confound: it
   says, with numbers, whether McGuffey was inflating, deflating, or neutral for each reader result.
4. **One-screen summary:** modern corpus + gold provenance → per-organ modern result vs floor vs twin → McGuffey-vs-modern
   delta → the recommendation (make the modern eval the default; which McGuffey uses can be retired). Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the role organ holds on modern LitBank/UD-EWT +0.20 CI-sep, coref holds, but the
situation-model timeline has no modern gold on the shelf so that dimension stays McGuffey-scored until a modern gold is
built — here is the one to build next").

## 8. FILES AND ENTRY POINTS
- **Reuse (do not modify the organs):** `hdlab/situation_reader.py`; the assembly eval loader
  `experiments/exp_wire_organs_endtoend_v1.py` (`load_gold`, `_passage_aliases`); `hdlab/corpus_registry.py` (the shelf).
  **Modern corpora (on disk):** `data/corpora/{litbank_coref_conll, ud_english_ewt, race, mcscript2, social_iqa, onestop,
  simplewiki}`. Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The reader organs are the INGREDIENTS (unchanged) — the deliverable is a MODERN annotated eval + the reader revalidated on
it + the quantified McGuffey-vs-modern delta. Do NOT change the mechanism to fit the corpus, do NOT LLM-label gold, do NOT
keep McGuffey as primary. Strategy lands the default-eval swap once the modern eval is validated.
