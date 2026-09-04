"""Scaffold-free witness for upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior.

Recomputes the located-negative core + the deployable win from source (CPU; NO GPU, NO external LLM at inference;
spaCy used ONLY as an offline diagnostic oracle, and that check is SKIPPED if spaCy is absent).

  W1  DEPENDENCY RESOLVED: the calibrated CRF posterior is a GLASS-BOX, pure-numpy linear-chain CRF -- its P(VERB)
      marginals reproduce sklearn_crfsuite.predict_marginals to < 1e-4 (ships as a dependency-free static asset).
  W2  THE LEVER IS THE CALIBRATED POSTERIOR (axis-1), and it separates 19c dropped verbs strongly on its own
      (AUROC(CRF P(VERB)) >= 0.85 over the false-candidate population).
  W3  THE JOINT PARSE-COHERENCE (axis-3) DOES NOT ADD: augmenting the CRF posterior with the force-VERB
      parse-coherence cue (register-robust DELEX parser) lifts AUROC by < 0.02 (negligible -- the located negative).
  W4  THE PARSER'S REGISTER-BRITTLENESS IS REAL BUT IMMATERIAL: the DELEX (register-robust) coherence cue is a
      better separator than the LEXICAL (modern) coherence cue (AUROC_delex >= AUROC_lex), yet neither matters
      because the calibrated posterior already captures the signal.
  W5  (oracle, skipped if spaCy absent) THE RESIDUAL IS A PARSER-FIDELITY GAP, NOT A MEANING CEILING: a competent
      statistical reader (spaCy, offline) recovers most in-vocab drops.

Run: .venv/Scripts/python.exe verification/test_joint_decode_register_robust.py
"""
import os
# core-headroom cap (USER 2026-09-04: constrain local runs below all cores; concurrent sessions share the box)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_crf_glassbox_marginals_v1 as GB
import experiments.exp_joint_decode_residual_decomposition_v1 as DEC

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    if ok:
        PASS += 1
    else:
        FAIL += 1


def main():
    print("[witness] recomputing from source (CRF + arc-eager parsers; a few minutes) ...", flush=True)

    # W1 -- glass-box CRF == crfsuite marginals
    gbres = GB.verify(n_sents=40, rebuild=False)
    chk("W1 glass-box CRF reproduces crfsuite P(VERB) to <1e-4 (dependency-free static asset)",
        gbres["max_abs_vpost_error"] < 1e-4,
        "max|dP(VERB)|=%.2e viterbi-agree=%.4f" % (gbres["max_abs_vpost_error"], gbres["viterbi_tag_agreement"]))

    # W2-W5 -- residual decomposition on the 19c dropped-verb population (moderate cap for a witness)
    sys.argv = ["dec", "--cap", "1200"]
    DEC.main()
    import json
    res = json.load(open(os.path.join(_REPO, "data/exp_joint_decode_residual_decomposition_v1/metrics.json")))["results"]

    a_crf = res["auroc_crf_post"]; a_lex = res["auroc_coh_lex"]; a_delex = res["auroc_coh_delex"]
    a_crf_delex = res["auroc_crf_plus_cohdelex"]
    chk("W2 the calibrated posterior separates 19c dropped verbs strongly on its own (AUROC(CRF)>=0.85)",
        a_crf >= 0.85, "AUROC(CRF P(VERB))=%.4f n_drops=%d" % (a_crf, res["n_drops"]))
    chk("W3 joint parse-coherence (DELEX) does NOT add: AUROC(CRF+cohDELEX) - AUROC(CRF) < 0.02 (the located negative)",
        (a_crf_delex - a_crf) < 0.02, "CRF=%.4f -> CRF+cohDELEX=%.4f (delta %+.4f)" % (a_crf, a_crf_delex, a_crf_delex - a_crf))
    chk("W4 register-robustness is REAL but immaterial: DELEX coherence separates better than LEXICAL (AUROC_delex>=AUROC_lex)",
        a_delex >= a_lex - 1e-9, "AUROC coh: delex=%.4f >= lex=%.4f" % (a_delex, a_lex))

    if "oracle_spacy_recovers_frac" in res:
        chk("W5 residual is a PARSER-FIDELITY gap, not a meaning ceiling (spaCy oracle recovers >0.5 of in-vocab drops)",
            res["oracle_recovers_invocab_frac"] > 0.5,
            "spaCy recovers %.3f of drops, %.3f of in-vocab" % (res["oracle_spacy_recovers_frac"], res["oracle_recovers_invocab_frac"]))
    else:
        print("  SKIP W5 (spaCy unavailable -- offline oracle only)", flush=True)

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
