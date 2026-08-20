"""WHICH ROLE ASSIGNER DOES THE LIVE READING PATH ACTUALLY CALL? Counted, not grepped.

WHY IT MATTERS. Two landed cells measured our role signal as POSITIONAL, not structural
(`structure_used=False`). But a third cell -- `exp_thematic_role_labeler_cue_integration_v1`,
HARD_PASS 2026-08-04 -- scores **0.8666 on NON-CANONICAL held-out against a positional baseline's
0.6032**, +0.2635, five seeds, scramble collapses, no single cue matches. **That is precisely the
capability the other two found missing.** Its registry row reads `VET_PENDING / N_A` while a
DIFFERENT assigner, `frame_primary_role_assigner_v1`, is marked `WIRED_AND_PIPELINE_USED`.

So the question is simply: when the substrate reads, which one runs?

**WHY RUNTIME AND NOT GREP.** CLAUDE.md records that static search gets this wrong in BOTH
directions in this very repo -- `pos_tagger`/`arc_parser`/`arc_labeler` are live but imported inside
a function body and invisible to grep, while two grep "hits" elsewhere are a string constant and a
comment. **And I have twice today stopped at "the module is imported" and treated it as "the code
runs".** `canonicalize_fast` was imported and called ZERO times. Import is not use.

WHAT IS COUNTED, each wrapped so the real function still runs:
  `thematic_role_labeler.label_roles`     the cue-integration entry point
  `thematic_role_labeler.train_perceptron` its weights -- it needs a trained `pred_fn` to work at all
  `thematic_role_labeler.role_feats`      the feature extractor underneath it
  `frame_induction.frame_primary_role`    the assigner the registry says is in-pipeline
  `animacy_lexicon.lookup_animacy`        the cue that distinguishes the two accounts

PRE-COMMITTED READINGS:
  label_roles > 0  -> the cue-integration model IS live, and the positional finding needs a
      different explanation. My "it is built but unused" would be wrong.
  label_roles == 0 AND frame_primary_role > 0 -> **the HARD_PASS capability is unused and a simpler
      assigner is doing the work.** That would explain `structure_used=False` exactly, and wiring an
      already-passing organ is a far smaller job than any new build. **It would still need a VET
      first -- `VET_PENDING` means nobody has independently re-derived that result, and n_test was
      63.**
  BOTH zero -> role assignment is not on the reading path at all, and the composition story needs
      re-framing from the start.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.animacy_lexicon as AL  # noqa: E402
import hdlab.frame_induction as FI  # noqa: E402
import hdlab.thematic_role_labeler as TRL  # noqa: E402

calls = {}


def wrap(mod, name):
    fn = getattr(mod, name, None)
    if fn is None:
        calls[name] = "ABSENT"
        return
    calls[name] = 0

    def w(*a, **k):
        calls[name] += 1
        return fn(*a, **k)

    setattr(mod, name, w)


for m, n in ((TRL, "label_roles"), (TRL, "train_perceptron"), (TRL, "role_feats"),
             (FI, "frame_primary_role"), (AL, "lookup_animacy")):
    wrap(m, n)

# POSITIVE CONTROL: the counter must actually count. Without this, an all-zero result could mean
# "never called" OR "my wrapper was bypassed", and those are opposite conclusions.
_probe = TRL.lemma_word("cities")
assert _probe == "city", "sanity: lemmatiser broken (%r)" % _probe
TRL.role_feats(["the", "dog", "ran"], ["DT", "NN", "VBD"], 2, 1, "rule", False)
assert calls["role_feats"] == 1, "the call counter does not count -- refusing to report zeros"
calls["role_feats"] = 0
print("selftest: wrapper counts a deliberate call, then reset to 0", flush=True)

from hdlab.substrate import Substrate  # noqa: E402

N = int(os.environ.get("DIAG_N_READ", "1200"))
sub = Substrate(seed=7)
sub.read(corpus="simplewiki", n_sentences=N, batch=50, max_patches=1, consolidate_every=200)

print("\nLIVE CALL COUNTS over %d sentences of real reading:" % N)
for k in ("label_roles", "train_perceptron", "role_feats", "frame_primary_role", "lookup_animacy"):
    print("   %-22s %s" % (k, calls.get(k)))

lr = calls.get("label_roles")
fp = calls.get("frame_primary_role")
print()
if isinstance(lr, int) and lr > 0:
    print("VERDICT: **THE CUE-INTEGRATION MODEL IS LIVE.** The positional finding needs a different")
    print("explanation, and my 'built but unused' reading was wrong.")
elif isinstance(fp, int) and fp > 0:
    print("VERDICT: **THE HARD_PASS CAPABILITY IS UNUSED; A SIMPLER ASSIGNER DOES THE WORK.** That")
    print("explains structure_used=False exactly. Wiring an already-passing organ is far smaller")
    print("than any new build -- but it is VET_PENDING (n_test=63), so it needs an independent")
    print("re-derivation BEFORE it is wired, not after.")
else:
    print("VERDICT: **NEITHER RUNS.** Role assignment is not on the reading path at all, and the")
    print("whole composition story needs re-framing from the start. Say so plainly.")
