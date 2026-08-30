---
priority: 4
review:
review_text:
---

# PROBLEM: the substrate's knowledge base accepts whatever is extracted from a trusted source and NEVER checks whether a stored fact is CORRECT or CONSISTENT with the rest of the knowledge — so the foundation stays noisy no matter how clean the extraction gets. The component scan of `hd_fact_store` (BRAIN_FOUNDATIONAL_AUDIT §2b, 2026-08-30) found this in the organ's own words: "INGEST-VET is SOURCE-TRUST vetting, NOT correctness vetting… a clean (non-conflicting) fact simply STORES — there is no internal uncertainty gate." It detects same-(subject,relation) CONFLICTS and resolves them by SOURCE RANK (REPLACE/COMBINE/FLAG/DROP), but it has NO mechanism to notice that a fact CONTRADICTS the coherent majority of what is already known, or is internally inconsistent, regardless of its source. This is the North Star's downstream CLEAN-FOUNDATION half: the extraction front-end (`the_extraction_front_end…`, p1) reduces noise going IN; this reduces noise ALREADY IN — and both must hold before the learner can safely grow on the foundation ([[learner-on-organizing-frame]]: the learner is OFF because the foundation is too noisy; the cleaned store is the disconnected missing link). Build the consistency/correctness cleanup — a glass-box organ that scores each stored fact for CONSISTENCY with the surrounding knowledge and downweights/flags the ones that contradict the coherent majority — and validate it removes injected errors without removing correct facts.

**slug:** `the_knowledge_store_has_no_correctness_or_consistency_cleanup` — **opened:** 2026-08-30 by the strategy session (the
`hd_fact_store` component-scan finding; the North Star's downstream clean-foundation link). **status:** OPEN — a MECHANISM +
BUILD problem. You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the
invariant); NO external correctness oracle at inference (consistency must come from WITHIN the knowledge, not a looked-up truth).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — HIGH and North-Star-central. It is the DOWNSTREAM half
> of the clean-foundation chain the whole learner-on program hinges on (p1 is the upstream half); the two together are the gate
> to flipping the learner on. Ranked below the in-flight foundation/reader work (p1/p2/p3) and above the two successor builds
> (p5/p6) because a noisy stored foundation caps the learner regardless of those. **Re-rank per the owner.** ⚠️ This is NOT the
> consolidation READ-OUT (written-but-never-read) nor the replay MECHANISM (single-average vs selective — tested, doesn't
> generalize) — it is CONSISTENCY-vs-the-knowledge, a fresh angle; do not re-tread those.

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
Our knowledge store is a gullible note-taker: if a source it trusts says something, it writes it down, and it never asks "wait,
does this even fit with everything else I know?" So if the reader mis-extracts a fact — or a source is simply wrong about one
thing — that wrong fact sits in memory forever, and later reasoning trusts it. The brain doesn't work that way: when a new
claim clashes with a coherent web of things you already believe, you feel the friction and discount the outlier. Build that
"does this fit?" check: score each stored fact against the surrounding knowledge and quietly down-weight the ones that
contradict the coherent majority — using only what's inside the store, no external fact-checker. Then prove it actually
removes wrong facts we plant, without throwing out the good ones.

## 2. WHY THIS ONE
It is the missing downstream half of the clean foundation. We are already fixing what goes IN (the extraction front-end, p1);
this fixes what is ALREADY in. The learner is deliberately OFF because the foundation is too noisy — and "too noisy" means
exactly "the store holds facts no one ever checked for correctness." Without this, cleaner extraction still leaves a store
that accumulates every past error. It is the concrete organ the learner-on roadmap named as the disconnected missing link.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** the brain monitors for CONFLICT/CONTRADICTION between incoming information and existing knowledge
  (ACC/mPFC conflict + error monitoring) and assimilates or CORRECTS new memory against a SCHEMA — a coherent structure of
  related knowledge (mPFC; van Kesteren schema-congruence; Ghosh & Gilboa; Gilboa & Marlatte). Coherent, mutually-supporting
  facts reinforce; an outlier that contradicts the schema is flagged/down-weighted. Systems consolidation over-writes toward
  the gist/schema, discarding inconsistent detail (Winocur & Moscovitch).
- **OUR-INVENTION (flag + sweep):** the CONSISTENCY/coherence score (a within-store agreement measure — how much a fact is
  supported vs contradicted by its neighbours in the (subject,relation,object) graph), the schema/neighbourhood definition,
  the down-weight/flag thresholds. Glass-box, no external LLM, NO external truth oracle at inference.

## 4. MEASURED vs INFERRED
- **MEASURED (the gap):** `hd_fact_store` INGEST-VET vets SOURCE-TRUST only; a clean fact stores unconditionally; there is no
  correctness/consistency gate (its own docstring). The foundation's noise enters here.
- **INFERRED (you must measure):** whether a within-store consistency-scoring cleanup identifies and down-weights INJECTED
  wrong/contradictory facts (that clash with the coherent majority) CI-separated over a random-drop twin, WITHOUT down-weighting
  correct/consistent facts — and only where the store has enough related facts for a consistency signal to exist (report the
  coverage honestly; a sparse store has no signal — an honest bound, not a failure).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The consolidation READ-OUT (`the_consolidated_cortical_store_is_written_but_never_read`) — a read-path problem, NOT this.
- The consolidation MECHANISM as selective replay (`one_store_does_two_jobs…`; the generalization stress-test found selective
  replay DOES NOT beat uniform on real cross-domain interference) — do NOT reframe this as replay; it is a within-store
  CONSISTENCY check, a different operation.
- SOURCE reliability (`no_automatic_reliability_signal_reaches_the_source_oracle`, integrated) — that is SOURCE trust; this is
  consistency-with-the-knowledge, independent of source. Compose, don't duplicate.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/hd_fact_store.py` (the store + INGEST-VET REPLACE/COMBINE/FLAG/DROP + the same-(s,r) conflict key) and the
  BRAIN_FOUNDATIONAL_AUDIT §2b `hd_fact_store` entry — confirm the correctness gate is genuinely absent.
- Build a REAL extracted fact store from the reading corpus (SimpleWiki/LitBank) so the consistency signal is measured on a real
  (s,r,o) graph, not a synthetic one — MIND THE CORPUS-AGE CONFOUND.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a REAL extracted fact store (SimpleWiki/LitBank), with a CONTROLLED-CORRUPTION protocol (inject a known fraction of
contradictory/wrong facts that clash with the coherent majority — a gold-free ground truth, since you know which you injected):
- **PASS =** the consistency-cleanup organ DETECTS/down-weights the injected errors — precision AND recall on the injected set —
  CI-separated over BOTH the strongest floors (source-trust-only INGEST-VET, and a frequency/degree prior) AND the info-free
  twin (random-drop matched to the same removal rate must LOSE), WITHOUT a CI-separated loss of correct/consistent facts. Report
  CI half-width + null p95; report the COVERAGE (fraction of facts with a real consistency signal) as an honest bound.
- **A rigorous NEGATIVE is a full PASS:** if within-store consistency cannot separate injected errors from correct facts on a
  real extracted store (e.g. the store is too sparse/disconnected for a consistency signal), name why, enumerated — that tells
  the learner-on program the cleanup must wait on a denser foundation (and re-points to p1/coverage).

## 8. FILES AND ENTRY POINTS
- `hdlab/hd_fact_store.py` (the store to add the consistency-cleanup to). Build a real extracted store in `experiments/`; witness
  recomputes the injected-error detection from source. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the
  correctness/consistency gate; the coverage bound). This is the North Star clean-foundation DOWNSTREAM half — coordinate with
  p1 (upstream extraction) and the learner-on roadmap ([[learner-on-organizing-frame]] / `notes/LEARNER_ON_ROADMAP.md`).
