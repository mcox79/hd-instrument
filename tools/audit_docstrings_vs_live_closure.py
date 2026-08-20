"""Which LIVE modules describe themselves as NOT being on the live path?

WHY. `_make_definitional_gate`'s rationale said *"it is NOT on the live reading path"* while the gate
was firing on 212 of 402 facts, and in the same paragraph described a route (`Definition.head`) that
is not the one shipping (`d.definiens`). **A future reader deciding whether to invest in that wire
would have read a rationale for the arm today's blind audit says is worth nothing, and applied it to
the arm that is worth a lot.** That is invisible until someone acts on it, so the question is whether
there are others.

METHOD -- RUNTIME, because CLAUDE.md says the live closure is knowable only by importing and
inspecting `sys.modules`, and that grep gets this wrong in BOTH directions in the same file (lazy
imports inside function bodies are invisible to it; a module named only in a string constant or a
comment reads as an import).

  1. Actually READ with the substrate, so lazily-imported organs load.
  2. Snapshot `sys.modules` for `hdlab.*` -- that IS the live closure.
  3. For each live module, scan its MODULE DOCSTRING REGION (the head of the file) for a
     NON-REACHABILITY claim about itself.
  4. Report the intersection: LIVE, but says it is not.

WHAT IS DELIBERATELY *NOT* FLAGGED. "NOT wired into `<function>`'s precedence" and "default OFF" are
legitimate design statements about an OPT-IN LEVER, not claims of unreachability, and there are
dozens of them. Flagging those would bury the real cases -- the same cry-wolf failure that gets a
guard ignored. Only self-descriptions of the MODULE's own reachability count.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import re  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.substrate import Substrate  # noqa: E402

N_READ = int(os.environ.get("DIAG_N_READ", "1200"))

sub = Substrate(seed=7)
total = 0
while total < N_READ:
    r = sub.read(corpus="simplewiki", n_sentences=min(400, N_READ - total), batch=50,
                 max_patches=1, consolidate_every=200)
    if r.n_sentences == 0:
        break
    total += r.n_sentences
# exercise the read side too, so retrieval-only organs load
try:
    s0 = sub.state.sentence_pool[0] if sub.state.sentence_pool else ""
    if s0:
        sub.recall_sentence(s0, top_k=5)
        sub.recall_cortical(s0, top_k=5)
        sub.query("water")
except Exception as exc:                                   # a probe must not mask the audit
    print("note: read-side probe raised %r (continuing; closure below is still valid)" % exc)

live = sorted(m for m in sys.modules if m.startswith("hdlab."))
print("read %d sentences | LIVE hdlab modules in sys.modules: %d" % (total, len(live)))

# Claims about THE MODULE'S OWN REACHABILITY. Not "not wired into <fn>'s precedence" (an opt-in
# lever), not "default OFF" (a parameter default) -- those are design statements and are legion.
CLAIMS = [
    (re.compile(r"not\s+on\s+the\s+live\s+(reading\s+)?path", re.I), "says NOT ON THE LIVE PATH"),
    (re.compile(r"absent\s+from\s+the\s+[^.\n]{0,40}closure", re.I), "says ABSENT FROM THE CLOSURE"),
    (re.compile(r"zero\s+consumers?\b", re.I), "says ZERO CONSUMERS"),
    (re.compile(r"\bno\s+consumers?\b", re.I), "says NO CONSUMERS"),
    (re.compile(r"is\s+not\s+reachable", re.I), "says NOT REACHABLE"),
    (re.compile(r"never\s+imported", re.I), "says NEVER IMPORTED"),
]
HEAD_LINES = 80          # the module-docstring region, not the whole file

flagged = []
for mod in live:
    path = getattr(sys.modules[mod], "__file__", None)
    if not path or not os.path.exists(path):
        continue
    try:
        with open(path, encoding="utf-8") as fh:
            head = "".join(fh.readlines()[:HEAD_LINES])
    except OSError:
        continue
    for rx, label in CLAIMS:
        m = rx.search(head)
        if m:
            line_no = head[:m.start()].count("\n") + 1
            ctx = head[max(0, m.start() - 90):m.start() + 110].replace("\n", " ")
            flagged.append((mod, label, line_no, " ".join(ctx.split())))
            break

print()
print("=" * 90)
print("LIVE MODULES THAT DESCRIBE THEMSELVES AS NOT REACHABLE")
print("=" * 90)
if not flagged:
    print("NONE. Every live module's self-description is consistent with it being live.")
    print("(The definitional-gate case found earlier today was a FUNCTION docstring, not a module")
    print(" one, so a module-level scan would not have caught it -- stated so this clean result is")
    print(" not over-read. See the note below.)")
else:
    for mod, label, ln, ctx in flagged:
        print("\n  %-46s %s (head line ~%d)" % (mod, label, ln))
        print("      ...%s..." % ctx[:150])

print()
print("SCOPE, STATED SO A CLEAN RESULT IS NOT OVER-READ:")
print("  * this checks MODULE docstrings only. Today's real defect was in a FUNCTION docstring")
print("    (`_make_definitional_gate`), inside a module that never claimed to be unreachable.")
print("    A clean run here does NOT mean no stale reachability claims exist.")
print("  * it checks REACHABILITY claims only -- not whether a docstring describes the arm that")
print("    actually ships, which is the OTHER half of today's defect and is not machine-checkable.")
print("  * the closure is from ONE read path (read + recall + query). An organ reached only by a")
print("    different entry point would not appear as live here.")
