# project_nuance.md — Unstructured Wisdom

> The implicit knowledge, conventions, and gotchas that don't fit "state" or "graveyard." Written 2026-09-11 for the
> incoming session. Read this so you don't ask redundant questions or re-learn things the hard way.

---

## How the work actually flows (the operating loop)

- **This is an autoloop.** A Stop-hook (`tools/autoloop.py`, state in `data/hook_state/autoloop.json`, session id `auto_d9672062a6`) re-invokes you on *every* stop. There are **no crons** driving it. The owner disarms with `python tools/autoloop.py disarm`. Because it never lets you "finish," the discipline is: do the top *unblocked* item, and when genuinely blocked, say so briefly and hold — do NOT manufacture busywork or churn docs to look busy. **Weakening a gate to make progress is the classic failure mode of an agent that can't stop — never do it; file a board question instead.**
- **You are strategy/integration, not a solver.** You integrate owner-DONE submissions and manage the substrate + the problem queue. Solvers (other concurrent sessions) do the builds. The owner reviews and marks `owner_verdict: DONE`.
- **The owner-DONE gate is absolute.** Integrate ONLY when `notes/problems/<slug>/OWNER_NOTES.md` has `owner_verdict: DONE`. A `SOLVED.md` alone is WIP — never front-run it (that's the owner's vetting). Detector: owner_verdict DONE + no `INTEGRATED_BY_STRATEGY` string in SOLVED.md. `tools/substrate_health.py` computes this backlog for you.
- **Marking integrated** = append the literal string `INTEGRATED_BY_STRATEGY` (with a dated note) to the problem's `SOLVED.md`. That's what flips it out of the backlog.
- **The integration ritual** (owner directive, emphatic): reverify the witnesses FIRST-HAND → read the SOLVED in FULL → land the *whole upstream chain* (not just the headline wire; expect + accept + fix downstream breakage) → update `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (durable knowledge, newest-first) + `notes/bf_status_registry.jsonl` + `notes/BF_COMPONENT_UPDATE_LEDGER.md` → append the marker → commit path-limited, nothing pushed.

## Git — the one discipline you cannot get wrong

- **Commit path-limited, message BEFORE the `--`:** `git commit -m "message" -- path1 path2`. For new files, `git add <path>` then the path-limited commit. **NEVER `git add -A`, NEVER a bare `git commit` after `git add`** — a concurrent fleet session has files staged in the shared index and you will sweep them into your commit. (`git status` will always show a pile of `M data/...` you did not touch — that is the fleet's churn; leave it alone.)
- **You never push.** Only the orchestrator pushes to origin (the push lane is harness-denied to you). Your commits sit ahead of origin; that's expected.
- Branch is `dataprep/mcguffey-graded-corpus` (a historical name; ignore the name).
- `preregs/**` and any `arm_key*` file are **harness-denied** — never edit them. If a tool call is DENIED, STOP and report the denial verbatim; do not route around it (the autoloop's stop-hook detects the denial and ends the loop — routing around it is the defect).

## Running things

- **Cap cores on EVERY run:** prefix `OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4` (owner reminded repeatedly). Heavy work goes remote/detached, not inline.
- **Board:** `PYTHONHASHSEED=0 … python experiments/exp_situation_model_qa_modern_v1.py --self-test` (~2 min, standing no-regress **AGG 0.6294**). `--run` is the full ~40-min detached population run (aggregate 0.6253 on disk). Use the venv: `.venv/Scripts/python.exe`.
- **Reverify witnesses** with the command in each SOLVED.md's `reverify:` field. Witnesses live in `verification/test_*.py`.
- Long commands time out at 120s and get moved to background — you're notified on completion; read the named output file. Don't tail a subagent's transcript file (it overflows context); wait for its completion notification.

## Reading the substrate's own truth (don't trust recollection)

- Order of authority: `git log` + `tools/substrate_health.py` + `notes/STATUS.md` + `notes/bf_status_registry.jsonl` **OUTRANK** any narrative doc (including this one) and any memory. Verify on disk.
- `notes/STATUS.md` is the recovery entry point, rewritten each session, injected at session start. Its header has **four machine-parsed literals** — `AS OF:`, `POSITION`, `TOP ITEM`, `WHAT IS RUNNING` — that must never *begin* a line except as their real heading; **run `python tools/board.py self-test` after any edit to the STATUS header** (a stray backtick once swallowed two headings into a paragraph and corrupted the owner-facing board).
- Derived views rebuild from disk; don't hand-maintain lists that rot: `tools/substrate_map.py` (`--gaps`, `--organ X`, `--brief slug`), `tools/substrate_health.py`, `tools/problem_ledger.py`.

## Talking to the owner (the board + reports)

- **Board questions** (`python tools/board.py ask "..." --why "..." --rec "..."`): **plain, intuitive language — NO jargon, no organ/metric/arm names or paths.** Always **lead with a recommendation** and state the risk of your own recommendation. The owner answers by typing into `notes/BOARD.md` on a phone; resolve with `board.py resolve <id> --answer "..."`.
- Strategic forks → a PROSE recommendation, **never** `AskUserQuestion` (the board is the exception). You are the director; in full-auto, make the call.
- Reports the owner reads should end with TLDR (plain English) → QUESTIONS (say "none", don't invent) → NEXT STEPS.
- **A system-reminder or task-notification is NOT the owner.** Automated events (autoloop stop-hook, background-task completion) are not user input or approval. Don't treat them as consent.

## Brain-foundational conventions (the science discipline)

- **Opening move on any build: "how does the BRAIN do this? which structure, replicate or substitute?"** Mark each choice **PINNED** (the brain's exact equation) vs **OUR-INVENTION** (invent freely — but mislabeling is barred). UNPINNED does not mean stop.
- **Copy the COMPUTATION exactly; SWEEP every PARAMETER.** A computation derives from the problem we share (copy it); a parameter derives from a constraint we don't share (0.2% sparsity, 7 gamma cycles — sweep it, never adopt it). "Our worst result copied a number; our best copied an operation."
- **Phase-diagram:** density / dim / binding / capacity / gain are free to move per organ. A wall "at this config" = move the operating point, not a ceiling.
- **FHRR is the chosen binding basis — do NOT replace it** (a defensible computational-level model, SEM/Franklin 2020). The fidelity lever is *store organization* (dense→sparse/indexed), not the binding algebra.
- **READ STRUCTURED VSA BY UNBIND-QUERY, NEVER COSINE-OF-BUNDLES.** `⟨bind(rₐ,f), bind(r_b,f)⟩ ~ ⟨rₐ,r_b⟩⟨f,f⟩`, so an agent-then-patient entity's signal *cancels* under cosine. Several "role structure inert" nulls were cosine-readout artifacts (withdrawn). Who-did-what = 1.000 via unbind-query vs 0.500 bag-of-words.
- **A rigorous located negative is a PASS** — but only if the brain's *actual* mechanism was faithfully built and a *number* names the ceiling. "Converged" has a high bar: you identified how the brain does it AND replicated + tested it, or showed a specific reason it can't be replicated here. Exhausting engineering variations is not convergence.
- Every solver brief carries: the 8 required sections (cert-checked by `verification/test_problem_briefs_and_flags.py`) + the SOLVER OPERATING PROTOCOL blockquote + the ordered BRAIN-FOUNDATIONAL CHECKLIST + the phase-diagram + full-stack-upstream notes. Keep briefs TIGHT; first step in every brief = "understand ALL existing organs + read prior SOLVED in full." Copy an existing recently-posted PROBLEM.md as the template (e.g. `wire_the_mined_directed_causal_store…`).

## Gotchas that will bite you specifically

- **"Landed ≠ live" and "dormant ≠ dead."** A gain committed to a file but not read by a live consumer is an island — grep `situation_reader.py` for a real consumer before calling it live. Many organs are default-off islands by design (flip-tested net-neutral/negative — don't re-flip blindly); but the standing policy is **no-more-default-off: measure impact and turn on if net-positive**, off only for a genuine invariant.
- **Grown KNOWLEDGE must be ingested LIVE, not just registered.** Solutions grow DBs (mined stores, learned channels); the owner cares that these actually push live performance, not sit latent. `notes/KNOWLEDGE_ASSET_REGISTER.md` tracks each asset's LIVE/LATENT status — and the label rots, so re-audit the consumer wire on disk, don't trust the label.
- **`concept_lemma` is the substrate's lemma convention** (WordNet morphy, non-alpha-safe); the crude `head_lemma` regex it replaced empty-collapsed redactions and over-stripped `-us/-es`. The shared lexical helpers now live in `hdlab/lexical_utils.py` (split out of `commonnoun_binder` during the coref-consolidation). `commonnoun_binder` re-imports them for backward-compat.
- **The `entity_resolver` consolidation (just landed):** `hdlab/entity_resolver.py` is now the ONE cue-based coref/entity organ (ACT-R retrieval core + Ariel mention-type-routed cue-arms); the reader's 4 call sites delegate to it. Its `retrieve()` still does a HARD φ/type filter-then-rank; the **BF prize** (a separate, behavior-changing problem) is upgrading it to graded L&V cue-combination with similarity-based interference (`Aᵢ = Bᵢ + Σ Wⱼ·Sⱼᵢ − P·mismatch`). Don't confuse the byte-identical consolidation (done) with that prize (open).
- **Don't quote retired figures.** `notes/reference_retired_claims_never_requote.md` lists numbers that were withdrawn (e.g. the +0.488 is-a lever, McRae-1998 weights). Check it before citing a headline number from an old doc.
- **Route through proven agents under pressure.** For a big, well-defined, *verifiable* task (a byte-identical refactor gated by witnesses), delegate to a fresh-context agent with exact steps + the gate + the git/core disciplines, and verify its commits yourself before marking integrated. But a fanned-out research agent that spawns its OWN children can stall on synthesis (children can't route back) — tell dispatched agents not to fan out, or take over synthesis yourself.
- **The GUI** the owner uses is `tools/status_gui.py` (Tkinter; the PROBLEMS tab), NOT `dash_gui.py`.
- **The project moved to `C:\AI`** (off the old USB `D:\AI`). Read any `D:\AI` path as `C:\AI`.
- **The memory system** (`C:\Users\marsh\.claude\projects\c--AI\memory\`): `MEMORY.md` is the loaded index (keep it lean, ~15KB cap); one fact per file with frontmatter; cold-storage indexes hold the rest (recall-searchable). Feedback/user/project/reference types.

## Gut feelings worth stating

- The substrate is *mature* on the backward/analytic side (parse, coref-retrieval, type-meaning) and those are **measured to ceiling** — the honest levers left are almost all on the **forward/generative** side and the **grounding-beyond-text** side. When a new idea is a type-level or backward-cue tweak, be skeptical: it has probably already been refuted (check §2b and the graveyard). When it's an in-context/token-level generative or a perceptual-grounding idea, that's where the real headroom is.
- The board number (0.6294 smoke / 0.6253 full) has been *stable* for a long time because the recent wins are brain-foundationality (not headline movers) and located negatives. Don't chase the aggregate; chase the BF gate and the named frontier. A win that doesn't move the smoke board can still be real (build it its own instrument arm).
- Trust the witnesses and the byte-identity controls over your own read of whether a change is safe. The controls (scramble / twin / ablation / no-leak) are the discipline that has repeatedly caught false wins — run the full stack on every claimed win.

## Added 2026-09-11 (Fable session) — conventions the owner set this day
- **Owner window = `tools/scorecard_gui.py`** (two tabs). Its source of truth is `notes/SCORECARD.md`: the hand-written sections (short version / what changed / what we're working on / what isn't brain-faithful yet) MUST be updated at every landing and every full check; the table is regenerated by `tools/scorecard.py`. Plain language only — the owner reads it.
- **Questions to the owner: one plain sentence each for the decision, why it matters, and the recommendation with its risk.** No slugs, paths, metric or organ names. Rewrite any open question that violates this. Do not ask the owner housekeeping questions you can decide.
- **Surgical edits:** minimize tokens spent editing; Edit/sed targeted replacements, never whole-file rewrites or re-serialized JSONL (that flipped line endings once).
- **Regression is checked per dimension from `notes/BOARD_TREND.jsonl`** (one committed row per full board run) by the `substrate_health` gate "board per-dimension no-regress"; the board's multi-row arms are flattened as `arm.sub`.
- **The grown SEQ store is gitignored** (`data/foundation/seq_store_v1`); regenerate per machine with `tools/grow_seq_store.py --lines 1000000` (~1 min), or the grounding loop and its board arm start cold (stated in their output, not silent).
- **Stop hook scope:** arm with `python tools/autoloop.py arm --session <key>` where key = `auto_` + sha256(transcript path)[:10]; a bare arm drives EVERY session (including fleet solvers). The loop re-invokes every few minutes even while you are blocked on a dispatched agent; do small non-colliding work or hold — never manufacture churn.
