"""hdlab/structural_do.py -- STRUCTURAL DIRECT-OBJECT evidence (is_bare_do), promoted VERBATIM (2026-09-03) from
experiments/exp_whodidwhat_coverage_transitivity_control_v1.is_bare_do (the owner-DONE coverage-gap §0g wire).

WHY. The reader's `verb_subcat` gate vetoes a bound patient on a low-transitivity verb to PROTECT precision
("the man SAT" must not bind a spurious patient). But that blanket veto also DROPS genuinely-transitive uses of
the same verbs on 19c prose (ambitransitive / context-transitive: "he WALKED the horse", "she SAT the exam") --
47 mis-vetoed clauses in the coverage-gap diagnosis. The brain-faithful fix (Competition Model, Bates &
MacWhinney): STRUCTURAL evidence overrides a weak lexical prior. A post-verbal nominal is a DIRECT OBJECT iff no
preposition intervenes between the verb and the candidate (a preposition-governed nominal is an OBLIQUE). So a
low-transitivity verb WITH a bare post-verbal DO keeps the patient (recovers the 47); WITHOUT one it still
abstains (intransitive precision preserved). Glass-box, NO LLM.

CLEAN_PREPS is the FROZEN modern + archaic/literary preposition set from the validated cell (REG.PREPS | the
literary extension: amongst/unto/upon/betwixt/whilst-of-place...), used TOGETHER with the UPOS ADP tag so a word
the modern tagger misses on old prose (amongst/unto) is still caught. OUR-INVENTION (a wordlist) -- a more
complete list can only PURIFY the direct-object set. 59 entries, byte-frozen from the cell at promotion time.
"""
from __future__ import annotations

from typing import Sequence

# byte-frozen from experiments.exp_19c_composed_cleaned_gold_v1.CLEAN_PREPS (REG.PREPS | the literary extension).
CLEAN_PREPS = {
    "aboard", "about", "above", "across", "after", "against", "along", "amid",
    "amidst", "among", "amongst", "around", "as", "at", "before", "behind",
    "below", "beneath", "beside", "besides", "between", "betwixt", "beyond", "by",
    "concerning", "despite", "down", "during", "for", "from", "in", "into",
    "near", "of", "off", "on", "onto", "out", "over", "past",
    "regarding", "round", "since", "than", "through", "throughout", "till", "to",
    "toward", "towards", "under", "until", "unto", "up", "upon", "via",
    "with", "within", "without",
}


def is_bare_do(toks: Sequence[str], pos: Sequence[str], vi: int, ix: int) -> bool:
    """Structural direct-object evidence: no preposition (UPOS ADP, or a CLEAN_PREPS token the modern tagger may
    miss) between the verb (0-based index `vi`) and the candidate nominal (0-based index `ix`). A bare adjacent
    nominal is a direct object; a preposition-governed one is an oblique. VERBATIM the validated cell's is_bare_do.
    Expects ix > vi (a post-verbal candidate); returns True on an empty span (adjacent DO)."""
    for j in range(vi + 1, ix):
        if pos[j] == "ADP" or str(toks[j]).lower() in CLEAN_PREPS:
            return False
    return True
