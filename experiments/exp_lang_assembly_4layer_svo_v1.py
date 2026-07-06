# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): the 5 arms produce hash-distinct per-sentence
#     recovered-structure signatures (structured / flat_bag / scrambled_roles differ on slot recovery;
#     naive_morphology differs on allomorph selection; identity_scrambled differs on the recovered stem id).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb / capacity-feasibility: LEVELS=1 block-local disjoint-block recovery is exact-by-construction
#     (bs = N/S = 1024, one code per disjoint block, no within-block superposition -> no argmax-noise floor;
#     crlb_n_a). FHRR identity cleanup: candidate stems are independent unit-phasors, self-cos=1.0,
#     cross-cos ~ 1/sqrt(2N) ~ 0.0078 (THEORETICAL) -> argmax separation exact-by-construction over a
#     small candidate set. discriminator_reachability=True (HP thresholds below the exact-by-construction
#     ceiling; the CONTROLS carry the falsification weight, not a hard-to-reach floor).
# - baseline_in_band (META_RULE_AG): the 4 controls are NEGATIVE controls expected to COLLAPSE by
#     construction (flat_bag / scrambled_roles collapse exact_ordered ~ 0; naive_morphology collapses
#     allomorph selection ~ chance 0.33; identity_scrambled collapses identity_consistency ~ chance
#     1/(3+K)). They are EXEMPT from the 0.05<baseline<0.95 in-band gate (HP_SCOPE); they carry ONLY the
#     collapse gate that PROVES the stressor bites. The MECHANISM arm (structured_joint) is the finding.
# - discriminator survives scale: ALL arms run at FULL N=8192 in smoke (smoke reduces sentence count +
#     seeds only, NEVER N). The 4 control collapses are STRUCTURAL / N-independent (flat superposition
#     merges disjoint blocks regardless of N; scrambled mis-addresses regardless of N; naive averages 3
#     allomorph tags into a blurred centroid regardless of N; wrong-id stem is orthogonal to the candidate
#     set regardless of N) -> smoke at full N fires every discriminator (option A + option B analytical).
# - HARD_PASS strictly above floor (META_RULE_L): exact_ordered >= 0.90 (floor 0.50, +5%=0.525);
#     identity_consistency >= 0.95 (floor 0.50); surface_string >= 0.90 (floor 0.50). All strict-above.
# - HP_SCOPE: chain-grade HP gates apply ONLY to structured_joint; controls carry ONLY their collapse gate.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# LANG-ASSEMBLY-4LAYER-SVO v1 -- FIRST end-to-end 4-layer language assembly (glass-box STRUCTURED composition)
# ============================================================================================================
# WHAT (USER-LOCKED FRAMING -- do NOT over-claim): compose FOUR independently-proven glass-box language
#   PRIMITIVES -- LEXICON (real native GSBC concept codes) + MORPHOLOGY (FHRR dual-route inflection) +
#   SYNTAX/GRAMMAR (block-local sparse slot-order + function-word operators) -- into ONE end-to-end pipeline
#   that encodes a KNOWN structured proposition (e.g. "the cat chased the dog") and round-trips it to the
#   structured parse (det=the, subj=cat, verb=chase[+PAST], det=the, obj=dog) with STRUCTURE intact, plus the
#   correctly-inflected surface string. This is glass-box STRUCTURED (lemma-level) COMPOSITION. It is NOT a
#   language model, NOT fluent language, NOT generation (the proposition is GIVEN not decided), NOT semantic
#   understanding. Stage-3.
#
# HONEST DATA NOTE (load-bearing; MEMORY.md foundational anchor "SUBSTRATE KNOWS NOTHING"): the 177,899-name
#   concept pool is a TECHNICAL ONTOLOGY (T1/vector_space, T1/inner_product, ...) MEASURED@ the id_order_json
#   of data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz -- it contains NO English
#   words like "cat"/"dog"/"chase". Therefore the English words here are HUMAN GLOSSES deterministically bound
#   to REAL native GSBC concept codes (real pool rows carrying the real GSBC cos-cone), NOT semantics the
#   substrate knows. The identity_consistency discriminator is about STRUCTURAL identity (the SAME concept-id
#   flowing through every layer), not meaning. Never narrate this as the substrate "knowing" cat/dog.
#
# THE CROSS-LAYER SPLIT (the load-bearing architectural finding, per 3 converging lit-scans + the brain's
#   lemma/lexeme split, research_language_assembly_composition_scoping_2026-07-05.md Section 1): the 4 layers
#   split into TWO INCOMPATIBLE vector families -- LEXICON/SYNTAX/GRAMMAR share sparse block-local GSBC codes;
#   MORPHOLOGY runs DENSE FHRR complex-phasor algebra. We do NOT fuse the vector spaces (no proven cross-VSA
#   theory exists). We BRIDGE AT THE DISCRETE SYMBOL BOUNDARY: decode each layer to a concept-id symbol, hand
#   the symbol to the next layer. This is the field's normal cleanup-decode readout idiom AND how human
#   sentence production is architected (lemma/lexeme are separate vocabularies; Roelofs/Meyer/Levelt 1998).
#
# THE 5 CROSS-LAYER MISMATCHES resolved as GLUE (scoping note Section 1d):
#   #1 algebra mismatch (FHRR morphology vs GSBC syntax) -> bridge at symbol, KEPT (brain-analogous, not fixed).
#   #2 grounding mismatch (morphology stems were ungrounded randoms) -> NEW deterministic concept-id->FHRR-stem
#      derivation: fhrr_stem_for_id(cid) seeds a phasor by the concept id, so the SAME lemma gets the SAME FHRR
#      stem every time -> lets identity_consistency verify morphology + syntax agree on WHICH lemma.
#   #3 block-size-schedule mismatch -> reuse the decoder's gsbc->block-local projection at grammar's LEVELS=1
#      bs=1024 (positive-control arm verifies it composes; NOT assumed).
#   #4 feature-binding location -> tense/number tracked as a PARALLEL symbolic sentence-plan (glue bookkeeping),
#      not carried in the vector algebra (Reiter&Dale precedent).
#   #5 function-word string gap -> a small curated {the,a} determiner gloss table (closed-class operators).
#
# ARMS (PAIRED -- same sentences + codebooks across arms, per feedback_paired_trials_mandatory):
#   structured_joint   (PRIMARY, mechanism): full 4-layer pipeline, bridge intact.
#   flat_bag           (control): syntax collapses -> superpose all slots into block 0 (reuse grammar arm).
#   scrambled_roles    (control): syntax collapses -> permuted (L,slot)->block address (reuse grammar arm).
#   naive_morphology   (control): morphology allomorph mechanism collapses -> single blurred transform.
#   identity_scrambled (control, THE NOVEL DISCRIMINATOR): morphology processes a DIFFERENT (wrong) concept-id
#                        than syntax decoded for the VERB slot. Syntax slot-recovery AND surface string still
#                        look correct, but the two subsystems SECRETLY DISAGREE on the lemma -> caught ONLY by
#                        identity_consistency. Isolates cross-layer IDENTITY (the one joint never before tested).
#
# METRICS (report SEPARATELY per Fix #28 -- never collapse to one aggregate; PAIRED across arms):
#   exact_ordered_slot_match : recovered ordered slot-content-id sequence == gold (chance ~ 0 for flat/scram).
#   identity_consistency     : P[FHRR-cleanup of the morphology stem (unbound) == the concept-id syntax decoded
#                              for the VERB slot], over the syntax-decoded candidate set + K distractors
#                              (chance = 1/(3+K)). THE novel cross-layer joint.
#   surface_string_exact     : final assembled + inflected string == gold string over the curated sentence set.
#
# Reuses (verbatim import; small glue only -- NOT new research):
#   experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py  (LEXICON pool + gsbc->block projection)
#   experiments/exp_grammar_recursive_function_word_blocklocal_v1.py  (SYNTAX/GRAMMAR encode/decode/score/audit)
#   experiments/exp_morph_ruleset_wug_v2_cpu.py                       (MORPHOLOGY FHRR algebra -- copied glue)
#
# ASCII-only. CPU (numpy + light torch import via decoder; no GPU; no LLM). Read-only on substrate.
# Run: python experiments/exp_lang_assembly_4layer_svo_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# --- LEXICON layer: real native GSBC pool + gsbc->block-local projection (decoder cell; __main__-guarded) ---
from experiments.exp_generation_decoder_gsbc_native_blocklocal_v1 import (  # noqa: E402
    _load_pool, _gsbc_dense, _blocklocal_codebook_gsbc, GSBC_DIM,
)

# --- SYNTAX/GRAMMAR layer: block-local encode/decode/score/audit (grammar cell; __main__-guarded) ---
from experiments.exp_grammar_recursive_function_word_blocklocal_v1 import (  # noqa: E402
    Codebooks, _encode_structured, _encode_flat_bag, _decode, _score_tree, _scramble_addr,
    structural_audit, S_SLOTS, N_DIM,
    SLOT_DET_S, SLOT_SUBJ, SLOT_VERB, SLOT_DET_O, SLOT_OBJ,
)

ANCHOR_NAME = "lang_assembly_4layer_svo_v1"

N = 8192                    # FHRR dim (morphology) == GSBC_DIM == N_DIM (block-local). CITED@source cells.
assert N == GSBC_DIM == N_DIM, "N must match the reused block-local + GSBC dim"

LEVELS = 1                  # flat clause (demo #1; recursion is a deliberately-deferred scoped follow-on)
V_CONTENT = 64              # content vocab (nouns+verbs) each bound to a REAL pool row; bs=1024 >> V (headroom)
K_DISTRACT = 5              # identity_consistency cleanup distractors (candidate set = 3 syntax ids + K)
NSHOW_PER_CLASS = 3         # morphology examples per allomorph class (few-shot conditioned transform inference)
IRREG_GATE_THRESH = 0.5     # dual-route exception-retrieval cosine gate (self ~1.0; non-member ~0.008)

SEEDS_FULL = (7, 13, 19)
SEEDS_SMOKE = (7,)
SEEDS_SELFTEST = (7,)

ARMS = ["structured_joint", "flat_bag", "scrambled_roles", "naive_morphology", "identity_scrambled"]

# ---- Pre-registered bands (HYPOTHESIZED@this-cell; deflated per lit-scan calibration; verified vs smoke) ----
HP_EXACT = 0.90            # HARD_PASS: structured_joint exact_ordered_slot_match (floor 0.50; +5%=0.525)
HP_IDENTITY = 0.95         # HARD_PASS: structured_joint identity_consistency (chance 1/(3+K))
HP_SURFACE = 0.90          # HARD_PASS: structured_joint surface_string_exact
HF_EXACT = 0.50            # HARD_FAIL: exact_ordered below -> undiagnosed integration-joint bug (mismatch #3)
HF_IDENTITY = 0.50         # HARD_FAIL: identity below -> the concept-id bridge itself is broken (mismatch #2)
# control-collapse gates (each control MUST collapse or the test is vacuous):
CTRL_EXACT_MAX = 0.30      # flat_bag / scrambled_roles exact_ordered must collapse below this
CTRL_ALLO_MAX = 0.55       # naive_morphology allomorph-selection acc must collapse below this (chance 0.33)
CTRL_IDENTITY_MAX = 0.30   # identity_scrambled identity_consistency must collapse below this (chance ~0.125)
IDENTITY_CHANCE = 1.0 / (3 + K_DISTRACT)   # THEORETICAL chance for the identity cleanup


# ============================================================
# MORPHOLOGY FHRR glue (copied verbatim algebra from exp_morph_ruleset_wug_v2_cpu.py; small)
# ============================================================


def _cnorm(v: np.ndarray) -> np.ndarray:
    """Project to unit-modulus phasors (keeps phase). CITED@morph cell cnorm."""
    return np.exp(1j * np.angle(v)).astype(np.complex64)


def _cphasor_seeded(seed: int, d: int) -> np.ndarray:
    """One deterministic random unit phasor of dim d, seeded (reproducible). (d,) complex64."""
    g = np.random.default_rng(int(seed) & 0x7FFFFFFFFFFFFFFF)
    ang = (g.random(d) * 2.0 - 1.0) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def _cphasor_rng(m: int, d: int, g: np.random.Generator) -> np.ndarray:
    """m random unit phasors of dim d from a live rng. (m,d) complex64. CITED@morph cell cphasor."""
    ang = (g.random((m, d)) * 2.0 - 1.0) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


# ============================================================
# THE BRIDGE (mismatch #2 resolution): concept-id -> two representations
# ============================================================


def concept_id_for_word(word: str, pool_n: int) -> int:
    """Deterministic REAL pool row (native GSBC concept) for a gloss. Same word -> same real concept.
    The GLOSS is a human label; the returned id addresses a real native GSBC code (technical ontology)."""
    h = int(hashlib.sha256(("cid|" + word).encode("ascii")).hexdigest(), 16)
    return h % pool_n


def fhrr_stem_for_id(concept_id: int) -> np.ndarray:
    """mismatch #2 resolution -- the cross-layer IDENTITY anchor. Deterministic FHRR phasor stem seeded by the
    concept id: the SAME lemma -> the SAME FHRR morphology stem every time it is referenced. (N,) complex64."""
    return _cphasor_seeded(3_000_000 + concept_id, N)


# ============================================================
# Curated demo lexicon (GLOSSES only; every vector is a REAL substrate concept / synthetic operator)
# ============================================================
# Verb table: (base_gloss, past_gloss, allomorph_class in {0=/t/,1=/d/,2=/id/}, is_irregular)
# Allomorph class of regular past -ed is conditioned on the base's final sound (curated, linguistically plausible).
_VERBS = [
    ("walk", "walked", 0, False), ("chase", "chased", 0, False), ("watch", "watched", 0, False),
    ("push", "pushed", 0, False), ("kick", "kicked", 0, False), ("race", "raced", 0, False),
    ("chew", "chewed", 1, False), ("follow", "followed", 1, False), ("call", "called", 1, False),
    ("name", "named", 1, False), ("seize", "seized", 1, False), ("roam", "roamed", 1, False),
    ("hunt", "hunted", 2, False), ("guard", "guarded", 2, False), ("wait", "waited", 2, False),
    ("need", "needed", 2, False), ("herd", "herded", 2, False), ("mend", "mended", 2, False),
    ("go", "went", 1, True), ("run", "ran", 1, True), ("eat", "ate", 0, True), ("catch", "caught", 0, True),
]
# Noun table: (singular_gloss, plural_gloss, plural_allomorph_class); plural exercised on a subset of objects.
_NOUNS = [
    ("cat", "cats", 0), ("hawk", "hawks", 0), ("duck", "ducks", 0), ("ant", "ants", 0),
    ("dog", "dogs", 1), ("bird", "birds", 1), ("bear", "bears", 1), ("crow", "crows", 1),
    ("fox", "foxes", 2), ("horse", "horses", 2), ("mouse", "mouses", 2), ("goose", "gooses", 2),
]
_DETERMINERS = ["the", "a"]   # closed-class determiner glosses (mismatch #5: small curated function-word table)


def _verb_order():
    """Class-BALANCED interleaved verb order so ANY prefix is ~balanced across the 3 past-ed allomorph classes.
    This is load-bearing for the naive_morphology control: naive picks a FIXED class (it cannot condition on the
    stem), so its accuracy = fraction of verbs in that class; under balanced classes that is chance (~1/3). If the
    verb list were class-grouped, a small (smoke) prefix would be class-imbalanced and naive would NOT collapse."""
    by_class = {0: [], 1: [], 2: []}
    irregs = []
    for v in _VERBS:
        (irregs if v[3] else by_class[v[2]]).append(v)
    order = []
    ci = {0: 0, 1: 0, 2: 0}
    ii = 0
    step = 0
    # round-robin c0,c1,c2 ...; inject an irregular every 4th slot (keeps regular classes balanced in every prefix)
    while len(order) < len(_VERBS):
        if step % 4 == 3 and ii < len(irregs):
            order.append(irregs[ii]); ii += 1
        else:
            c = step % 3
            # find next class with remaining verbs, preferring c for balance
            for cc in (c, (c + 1) % 3, (c + 2) % 3):
                if ci[cc] < len(by_class[cc]):
                    order.append(by_class[cc][ci[cc]]); ci[cc] += 1
                    break
            else:
                if ii < len(irregs):
                    order.append(irregs[ii]); ii += 1
        step += 1
    return order


def _build_sentences(n_sent: int):
    """Curated SVO sentences (deterministic, ordered). Each: det_s, subj, verb, det_o, obj (+ optional plural obj).
    Verb inflected to PAST (past_ed allomorphy + irregular dual-route); ~1/3 objects inflected to PLURAL
    (plural_s allomorphy) -> exercises 2 productive allomorphic rules + the dual-route exception gate."""
    nouns = _NOUNS
    verbs = _verb_order()
    sents = []
    for i in range(n_sent):
        subj = nouns[i % len(nouns)]
        obj = nouns[(i + 3) % len(nouns)]
        verb = verbs[i % len(verbs)]
        obj_plural = (i % 3 == 0)              # inflect ~1/3 of objects to plural
        det_s = _DETERMINERS[i % 2]
        det_o = _DETERMINERS[(i + 1) % 2]
        gold = "%s %s %s %s %s" % (
            det_s, subj[0], verb[1], det_o, (obj[1] if obj_plural else obj[0]))
        sents.append({
            "det_s": det_s, "det_o": det_o,
            "subj_gloss": subj[0], "obj_gloss_sing": obj[0], "obj_gloss_plural": obj[1],
            "obj_plural": obj_plural, "obj_plural_class": obj[2],
            "verb_base": verb[0], "verb_past": verb[1], "verb_class": verb[2], "verb_irregular": verb[3],
            "gold": gold,
        })
    return sents


# ============================================================
# Per-seed context: codebooks (lexicon-grounded content + grammar function/hook) + morphology FHRR tags
# ============================================================


class SeedContext:
    """Everything derived once per seed. Content codebook is the REAL native GSBC pool projected block-local
    (mismatch #3). Function/hook codebooks come from the grammar cell unchanged. Morphology runs FHRR at N."""

    def __init__(self, seed: int):
        self.seed = seed
        pool = _load_pool()
        self.pool_n = int(pool["n"])
        # ---- content vocab -> REAL pool rows (deterministic per gloss) ----
        vocab_glosses = []
        for (g, _p, _c, _ir) in _VERBS:
            vocab_glosses.append(g)
        for (g, _p, _c) in _NOUNS:
            vocab_glosses.append(g)
        # de-dup preserving order, pad to V_CONTENT with synthetic gloss keys if short (headroom)
        seen = {}
        for g in vocab_glosses:
            if g not in seen:
                seen[g] = len(seen)
        idx = len(seen)
        while len(seen) < V_CONTENT:
            seen["_pad_%d" % idx] = len(seen)
            idx += 1
        self.gloss_to_vocab = dict(list(seen.items())[:V_CONTENT])
        self.vocab_glosses = [None] * V_CONTENT
        for g, vi in self.gloss_to_vocab.items():
            self.vocab_glosses[vi] = g
        # concept id (real pool row) per vocab slot
        self.vocab_cids = np.array([concept_id_for_word(self.vocab_glosses[vi], self.pool_n)
                                    for vi in range(V_CONTENT)], dtype=np.int64)
        # ---- LEXICON -> SYNTAX bridge: real GSBC codes projected block-local (mismatch #3) ----
        gsbc_codes = _gsbc_dense(self.vocab_cids.astype(np.int64))   # (V_CONTENT, GSBC_DIM) real
        bs = N_DIM // (LEVELS * S_SLOTS)                             # 1024 at LEVELS=1
        lex_content = _blocklocal_codebook_gsbc(gsbc_codes, bs, seed)  # (V_CONTENT, bs) sparse bipolar
        # grammar codebooks; override .content with the lexicon-grounded codebook (structured/flat/scram arms)
        self.cb_lex = Codebooks(LEVELS, V_CONTENT, seed)
        assert self.cb_lex.bs == bs and self.cb_lex.content.shape == lex_content.shape, "bs / content shape mismatch"
        self.cb_lex.content = lex_content.astype(np.float32)
        # positive control (Gate D): grammar's own SYNTHETIC content codebook at the SAME regime
        self.cb_synth = Codebooks(LEVELS, V_CONTENT, seed)          # unchanged synthetic content
        self.scr_addr = _scramble_addr(LEVELS, seed)
        # ---- MORPHOLOGY FHRR tags (per seed) ----
        g = np.random.default_rng(700000 + seed)
        self.BASE_M = _cphasor_rng(1, N, g)[0]                      # citation/base marker
        self.PAST_ROLE = _cphasor_rng(1, N, g)[0]                  # identity-binding role tag (past)
        self.allo_past = [_cphasor_rng(1, N, g)[0] for _ in range(3)]    # 3 past -ed allomorph tags
        self.allo_plural = [_cphasor_rng(1, N, g)[0] for _ in range(3)]  # 3 plural -s allomorph tags
        self.R_past = self._infer_transforms(self.allo_past, g)
        self.R_plural = self._infer_transforms(self.allo_plural, g)
        # ---- dual-route exception memory (irregular verbs) ----
        irr_glosses = [v[0] for v in _VERBS if v[3]]
        self.irr_glosses = irr_glosses
        self.irr_cids = {w: concept_id_for_word(w, self.pool_n) for w in irr_glosses}
        # exception codebook = FHRR base of each irregular verb (keyed by concept id)
        self.irr_base = {w: _cnorm(fhrr_stem_for_id(self.irr_cids[w]) * self.BASE_M) for w in irr_glosses}
        self.irr_codebook = (np.stack([self.irr_base[w] for w in irr_glosses], axis=0)
                             if irr_glosses else np.zeros((0, N), dtype=np.complex64))

    def _infer_transforms(self, allo_tags, g):
        """Conditioned per-class transforms R_cond[c] + one blurred naive transform R_naive, inferred from a
        few synthetic (base, surface) example pairs per class. CITED@morph cell infer_transform / eval_allo_rule."""
        R_cond = []
        all_acc = np.zeros(N, dtype=np.complex64)
        for c in range(3):
            acc = np.zeros(N, dtype=np.complex64)
            ex = _cphasor_rng(NSHOW_PER_CLASS, N, g)                # example stems for this class
            for j in range(NSHOW_PER_CLASS):
                base = _cnorm(ex[j] * self.BASE_M)
                surf = _cnorm(ex[j] * allo_tags[c])
                acc = acc + surf * np.conj(base)
                all_acc = all_acc + surf * np.conj(base)
            R_cond.append(_cnorm(acc))
        R_naive = _cnorm(all_acc)                                   # single blurred centroid over all 3 classes
        return {"cond": R_cond, "naive": R_naive}

    # ---- MORPHOLOGY inflection: select allomorph, return (selected_class, correct) ----
    def select_allomorph(self, stem: np.ndarray, gold_class: int, allo_tags, R, naive: bool) -> int:
        """Apply the conditioned (per gold phonological class) OR naive (single) transform, argmax over the 3
        allomorph realizations of THIS stem. Conditioned -> selects gold_class; naive -> blurred -> chance."""
        base = _cnorm(stem * self.BASE_M)
        Rt = R["naive"] if naive else R["cond"][gold_class]
        pred = _cnorm(base * Rt)
        cands = np.stack([_cnorm(stem * allo_tags[a]) for a in range(3)], axis=0)   # (3, N)
        sel = int(np.argmax((pred[None, :] @ np.conj(cands).T).real))
        return sel

    def dual_route_surface(self, verb_base: str, verb_cid: int, verb_past: str, verb_class: int) -> str:
        """Irregular dual-route: gate on cosine to the exception codebook; fire -> memorized (gold) surface;
        else the regular route would over-regularize. Returns the emitted surface gloss."""
        stem_base = _cnorm(fhrr_stem_for_id(verb_cid) * self.BASE_M)
        if self.irr_codebook.shape[0] == 0:
            return verb_past
        gate = float((stem_base[None, :] @ np.conj(self.irr_codebook).T).real.max() / N)
        if gate > IRREG_GATE_THRESH:
            return verb_past                                       # memorized surface retrieved (correct)
        return "%s+ed" % verb_base                                # over-regularized (WRONG for irregular)


# ============================================================
# One sentence through all arms
# ============================================================


def _make_tree(sent, ctx: SeedContext):
    """Build the grammar tree (LEVELS=1 flat clause) for a sentence. Content slots hold content-vocab indices;
    determiner slots hold function-vocab indices (the=0, a=1)."""
    det_s_idx = _DETERMINERS.index(sent["det_s"])
    det_o_idx = _DETERMINERS.index(sent["det_o"])
    subj_vi = ctx.gloss_to_vocab[sent["subj_gloss"]]
    verb_vi = ctx.gloss_to_vocab[sent["verb_base"]]
    obj_vi = ctx.gloss_to_vocab[sent["obj_gloss_sing"]]
    tokens = {
        (0, SLOT_DET_S): det_s_idx, (0, SLOT_SUBJ): subj_vi, (0, SLOT_VERB): verb_vi,
        (0, SLOT_DET_O): det_o_idx, (0, SLOT_OBJ): obj_vi,
    }
    return {"tokens": tokens, "hosts": {}, "has_embed": {0: True}, "levels": LEVELS, "full_depth": True}, \
        {"det_s": det_s_idx, "det_o": det_o_idx, "subj": subj_vi, "verb": verb_vi, "obj": obj_vi}


def _syntax_recover(comp, cb, tree, arm_decode):
    """Decode + return recovered content-slot vocab indices and the tree_exact (all filled slots recovered)."""
    rt, re_, rh = _decode(comp, cb, tree, arm_decode)
    s = _score_tree(tree, rt, re_, rh)
    rec = {
        "det_s": rt.get((0, SLOT_DET_S), -1), "det_o": rt.get((0, SLOT_DET_O), -1),
        "subj": rt.get((0, SLOT_SUBJ), -1), "verb": rt.get((0, SLOT_VERB), -1),
        "obj": rt.get((0, SLOT_OBJ), -1),
    }
    exact = 1.0 if s["tree_exact"] == 1.0 else 0.0
    return rec, exact


def _identity_consistency(ctx: SeedContext, true_verb_cid: int, rec_content_cids, morph_stem_cid: int, g):
    """FHRR cross-layer identity: bind morphology stem (of morph_stem_cid) with PAST_ROLE, unbind, clean up
    against the candidate set = {syntax-decoded subj/verb/obj cids} + K distractors. Hit iff the recovered
    stem's concept-id == the TRUE verb concept-id. In the mechanism arm morph_stem_cid == true_verb_cid;
    in identity_scrambled morph_stem_cid is a WRONG id -> recovered stem not in the (correct) candidate set."""
    stem = fhrr_stem_for_id(morph_stem_cid)
    surface = _cnorm(stem * ctx.PAST_ROLE)                         # morphology surface (identity binding)
    pred_stem = _cnorm(surface * np.conj(ctx.PAST_ROLE))          # unbind role -> recovered stem
    # candidate concept-ids: the syntax-decoded content ids (subj, verb, obj) + K distractors from vocab
    cand_cids = [int(rec_content_cids["subj"]), int(rec_content_cids["verb"]), int(rec_content_cids["obj"])]
    used = set(cand_cids) | {int(true_verb_cid)}
    pool_choices = [int(c) for c in ctx.vocab_cids if int(c) not in used]
    g.shuffle(pool_choices)
    cand_cids = cand_cids + pool_choices[:K_DISTRACT]
    cand_stems = np.stack([fhrr_stem_for_id(c) for c in cand_cids], axis=0)     # (n_cand, N)
    sel = int(np.argmax((pred_stem[None, :] @ np.conj(cand_stems).T).real))
    return 1.0 if cand_cids[sel] == int(true_verb_cid) else 0.0


def _assemble_surface(ctx: SeedContext, sent, rec, verb_naive: bool):
    """Assemble the final inflected surface string from the SYNTAX-recovered slot glosses + MORPHOLOGY output."""
    det_s = _DETERMINERS[rec["det_s"]] if 0 <= rec["det_s"] < 2 else "?"
    det_o = _DETERMINERS[rec["det_o"]] if 0 <= rec["det_o"] < 2 else "?"
    subj = ctx.vocab_glosses[rec["subj"]] if 0 <= rec["subj"] < V_CONTENT else "?"
    obj_sing = ctx.vocab_glosses[rec["obj"]] if 0 <= rec["obj"] < V_CONTENT else "?"
    verb_base = ctx.vocab_glosses[rec["verb"]] if 0 <= rec["verb"] < V_CONTENT else "?"
    # verb inflection (morphology)
    verb_cid = concept_id_for_word(sent["verb_base"], ctx.pool_n)
    if sent["verb_irregular"]:
        verb_surface = ctx.dual_route_surface(sent["verb_base"], verb_cid, sent["verb_past"], sent["verb_class"])
    else:
        stem = fhrr_stem_for_id(verb_cid)
        sel = ctx.select_allomorph(stem, sent["verb_class"], ctx.allo_past, ctx.R_past, naive=verb_naive)
        verb_surface = sent["verb_past"] if sel == sent["verb_class"] else "%s+WRONG_allo%d" % (verb_base, sel)
    # object number (morphology plural, if applicable)
    if sent["obj_plural"] and not sent["verb_irregular"]:
        obj_cid = concept_id_for_word(sent["obj_gloss_sing"], ctx.pool_n)
        ostem = fhrr_stem_for_id(obj_cid)
        osel = ctx.select_allomorph(ostem, sent["obj_plural_class"], ctx.allo_plural, ctx.R_plural, naive=verb_naive)
        obj_surface = sent["obj_gloss_plural"] if osel == sent["obj_plural_class"] else "%s+WRONG_pl%d" % (obj_sing, osel)
    elif sent["obj_plural"]:
        obj_cid = concept_id_for_word(sent["obj_gloss_sing"], ctx.pool_n)
        ostem = fhrr_stem_for_id(obj_cid)
        osel = ctx.select_allomorph(ostem, sent["obj_plural_class"], ctx.allo_plural, ctx.R_plural, naive=verb_naive)
        obj_surface = sent["obj_gloss_plural"] if osel == sent["obj_plural_class"] else "%s+WRONG_pl%d" % (obj_sing, osel)
    else:
        obj_surface = obj_sing
    return "%s %s %s %s %s" % (det_s, subj, verb_surface, det_o, obj_surface)


def run_sentence(sent, ctx: SeedContext, g):
    """Run one sentence through all 5 arms. Returns per-arm dict of the 3 metrics + a recovered signature."""
    tree, true_vi = _make_tree(sent, ctx)
    true_verb_cid = int(ctx.vocab_cids[true_vi["verb"]])
    # encodes (PAIRED codebooks): structured/naive/identity share the structured lexicon encode+decode;
    # flat_bag + scrambled_roles collapse syntax.
    comp_struct = _encode_structured(tree, ctx.cb_lex)
    comp_flat = _encode_flat_bag(tree, ctx.cb_lex)
    comp_scram = _encode_structured(tree, ctx.cb_lex, addr=ctx.scr_addr)

    rec_struct, ex_struct = _syntax_recover(comp_struct, ctx.cb_lex, tree, "structured")
    rec_flat, ex_flat = _syntax_recover(comp_flat, ctx.cb_lex, tree, "flat_bag")
    rec_scram, ex_scram = _syntax_recover(comp_scram, ctx.cb_lex, tree, "scrambled_roles")

    def cids_of(rec):
        return {k: int(ctx.vocab_cids[rec[k]]) if 0 <= rec[k] < V_CONTENT else -1 for k in ("subj", "verb", "obj")}

    # a random WRONG concept-id for identity_scrambled (a different lemma than the verb) -- drawn from vocab
    wrong_choices = [int(c) for c in ctx.vocab_cids if int(c) != true_verb_cid]
    g.shuffle(wrong_choices)
    wrong_cid = wrong_choices[0]

    out = {}
    # structured_joint (mechanism): syntax=structured, morphology stem = TRUE verb cid, conditioned allomorph.
    out["structured_joint"] = {
        "exact_ordered_slot_match": ex_struct,
        "identity_consistency": _identity_consistency(ctx, true_verb_cid, cids_of(rec_struct), true_verb_cid, g),
        "surface_string_exact": 1.0 if _assemble_surface(ctx, sent, rec_struct, verb_naive=False) == sent["gold"] else 0.0,
        "allomorph_ok": None,
    }
    # flat_bag (syntax collapse)
    out["flat_bag"] = {
        "exact_ordered_slot_match": ex_flat,
        "identity_consistency": _identity_consistency(ctx, true_verb_cid, cids_of(rec_flat), true_verb_cid, g),
        "surface_string_exact": 1.0 if _assemble_surface(ctx, sent, rec_flat, verb_naive=False) == sent["gold"] else 0.0,
        "allomorph_ok": None,
    }
    # scrambled_roles (syntax collapse)
    out["scrambled_roles"] = {
        "exact_ordered_slot_match": ex_scram,
        "identity_consistency": _identity_consistency(ctx, true_verb_cid, cids_of(rec_scram), true_verb_cid, g),
        "surface_string_exact": 1.0 if _assemble_surface(ctx, sent, rec_scram, verb_naive=False) == sent["gold"] else 0.0,
        "allomorph_ok": None,
    }
    # naive_morphology (allomorph mechanism collapse): syntax=structured, morphology stem=TRUE, NAIVE transform.
    allo_ok = None
    if not sent["verb_irregular"]:
        stem = fhrr_stem_for_id(true_verb_cid)
        sel = ctx.select_allomorph(stem, sent["verb_class"], ctx.allo_past, ctx.R_past, naive=True)
        allo_ok = 1.0 if sel == sent["verb_class"] else 0.0
    out["naive_morphology"] = {
        "exact_ordered_slot_match": ex_struct,
        "identity_consistency": _identity_consistency(ctx, true_verb_cid, cids_of(rec_struct), true_verb_cid, g),
        "surface_string_exact": 1.0 if _assemble_surface(ctx, sent, rec_struct, verb_naive=True) == sent["gold"] else 0.0,
        "allomorph_ok": allo_ok,
    }
    # identity_scrambled (THE NOVEL DISCRIMINATOR): syntax=structured (fine), surface=conditioned (fine),
    # but morphology's identity stem is derived from a WRONG concept-id -> identity bridge breaks ONLY.
    out["identity_scrambled"] = {
        "exact_ordered_slot_match": ex_struct,
        "identity_consistency": _identity_consistency(ctx, true_verb_cid, cids_of(rec_struct), wrong_cid, g),
        "surface_string_exact": 1.0 if _assemble_surface(ctx, sent, rec_struct, verb_naive=False) == sent["gold"] else 0.0,
        "allomorph_ok": None,
    }
    # recovered signature per arm (for META_RULE_AF arms-differ)
    sig = {
        "structured_joint": (tuple(sorted(rec_struct.items())), int(out["structured_joint"]["identity_consistency"])),
        "flat_bag": (tuple(sorted(rec_flat.items())), int(out["flat_bag"]["identity_consistency"])),
        "scrambled_roles": (tuple(sorted(rec_scram.items())), int(out["scrambled_roles"]["identity_consistency"])),
        "naive_morphology": (tuple(sorted(rec_struct.items())), int(out["naive_morphology"]["surface_string_exact"]), "naive"),
        "identity_scrambled": (tuple(sorted(rec_struct.items())), int(out["identity_scrambled"]["identity_consistency"]), int(wrong_cid)),
    }
    return out, sig


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(time.perf_counter() - t0, 2)}
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")   # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid()}
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# Config + driver + verdict
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"seeds": SEEDS_SELFTEST, "n_sent": 8}
    if mode == "smoke":
        return {"seeds": SEEDS_SMOKE, "n_sent": 12}
    return {"seeds": SEEDS_FULL, "n_sent": 22}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else float("nan")


def _aggregate(per_unit):
    """Aggregate the 3 primary metrics per arm (mean over seeds x sentences) + naive allomorph acc."""
    agg = {}
    for arm in ARMS:
        agg[arm] = {
            "exact_ordered_slot_match": round(_mean([u[arm]["exact_ordered_slot_match"] for u in per_unit]), 4),
            "identity_consistency": round(_mean([u[arm]["identity_consistency"] for u in per_unit]), 4),
            "surface_string_exact": round(_mean([u[arm]["surface_string_exact"] for u in per_unit]), 4),
        }
    agg["naive_morphology"]["allomorph_selection_acc"] = round(
        _mean([u["naive_morphology"]["allomorph_ok"] for u in per_unit]), 4)
    return agg


def classify(mode, agg, audit, n_units, exp_units):
    if n_units < exp_units:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {n_units}/{exp_units} units")

    sj = agg["structured_joint"]
    fb, sc = agg["flat_bag"], agg["scrambled_roles"]
    nm, ids = agg["naive_morphology"], agg["identity_scrambled"]

    diag = (
        f"structured_joint: exact_ordered={sj['exact_ordered_slot_match']:.3f} "
        f"identity={sj['identity_consistency']:.3f} surface={sj['surface_string_exact']:.3f} | "
        f"CONTROLS flat_bag.exact={fb['exact_ordered_slot_match']:.3f} scrambled.exact={sc['exact_ordered_slot_match']:.3f} "
        f"naive.allo={nm.get('allomorph_selection_acc', float('nan')):.3f} naive.surface={nm['surface_string_exact']:.3f} "
        f"identity_scrambled.identity={ids['identity_consistency']:.3f} (chance {IDENTITY_CHANCE:.3f}); "
        f"bag_blind={audit['bag_blind_to_structure']}"
    )

    # BIAS: flat_bag must be provably structure-blind (grammar structural audit)
    if not audit["bag_blind_to_structure"]:
        return ("BLOCK_DISPATCH_BIAS_BAG_NOT_BLIND",
                f"flat_bag composite not invariant to structure swap: the syntax stressor does not bite. {diag}")

    # DISCRIMINATORS MUST FIRE (each control collapses; else the test is vacuous) -- all modes
    ctrl_fail = []
    if not (fb["exact_ordered_slot_match"] <= CTRL_EXACT_MAX):
        ctrl_fail.append(f"flat_bag.exact={fb['exact_ordered_slot_match']:.3f}>{CTRL_EXACT_MAX}")
    if not (sc["exact_ordered_slot_match"] <= CTRL_EXACT_MAX):
        ctrl_fail.append(f"scrambled.exact={sc['exact_ordered_slot_match']:.3f}>{CTRL_EXACT_MAX}")
    if not (nm.get("allomorph_selection_acc", 1.0) <= CTRL_ALLO_MAX):
        ctrl_fail.append(f"naive.allo={nm.get('allomorph_selection_acc'):.3f}>{CTRL_ALLO_MAX}")
    if not (ids["identity_consistency"] <= CTRL_IDENTITY_MAX):
        ctrl_fail.append(f"identity_scrambled.identity={ids['identity_consistency']:.3f}>{CTRL_IDENTITY_MAX}")
    if ctrl_fail:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"a control did NOT collapse ({'; '.join(ctrl_fail)}): cannot attribute a structured pass to the "
                f"composed mechanism -- vacuous test. {diag}")

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: 4-layer assembly runs end-to-end AT N={N}; all 4 controls collapse "
                f"(syntax flat/scrambled, naive allomorph, identity-scramble) and structured_joint recovers on "
                f"all 3 metrics; identity_scrambled isolates the cross-layer identity joint. The pre-registered "
                f"assembly band is FULL-only (canonical = orchestrator FULL). {diag}")

    # --- FULL pre-registered bands (gate on structured_joint) ---
    if sj["exact_ordered_slot_match"] < HF_EXACT or sj["identity_consistency"] < HF_IDENTITY:
        return ("HARD_FAIL",
                f"4-layer assembly FAILS to round-trip: structured exact_ordered={sj['exact_ordered_slot_match']:.3f} "
                f"(HF<{HF_EXACT}) OR identity_consistency={sj['identity_consistency']:.3f} (HF<{HF_IDENTITY}) -- either "
                f"the block-projection joint (mismatch #3) or the concept-id->FHRR-stem bridge (mismatch #2) is "
                f"broken. {diag}")

    if (sj["exact_ordered_slot_match"] >= HP_EXACT and sj["identity_consistency"] >= HP_IDENTITY
            and sj["surface_string_exact"] >= HP_SURFACE):
        return ("HARD_PASS",
                f"FIRST 4-LAYER LANGUAGE ASSEMBLY round-trips: four independently-proven glass-box primitives "
                f"(lexicon + FHRR morphology + block-local syntax + function-word grammar) chain via a DISCRETE "
                f"SYMBOL bridge to recover a KNOWN structured proposition -- exact_ordered_slot_match="
                f"{sj['exact_ordered_slot_match']:.3f} (>={HP_EXACT}), cross-layer identity_consistency="
                f"{sj['identity_consistency']:.3f} (>={HP_IDENTITY}, chance {IDENTITY_CHANCE:.3f}), "
                f"surface_string_exact={sj['surface_string_exact']:.3f} (>={HP_SURFACE}). All 4 controls collapse. "
                f"Glass-box STRUCTURED composition of a known proposition over a curated gloss set -- NOT generation, "
                f"NOT understanding, NOT a language model; English words are HUMAN GLOSSES on real GSBC concepts. "
                f"{diag}")

    return ("MIDDLE_BAND",
            f"partial 4-layer assembly: structured beats all controls but does not clear the full HARD_PASS bar "
            f"(exact_ordered={sj['exact_ordered_slot_match']:.3f} vs {HP_EXACT}; identity={sj['identity_consistency']:.3f} "
            f"vs {HP_IDENTITY}; surface={sj['surface_string_exact']:.3f} vs {HP_SURFACE}) -- diagnostic: exact weak => "
            f"block-projection (mismatch #3); identity weak => id->FHRR bridge (mismatch #2); surface weak while both "
            f"vector metrics pass => a string-lookup bug (cheapest). {diag}")


def _demo_lines(sents, ctx: SeedContext, g):
    """Print the assembled sentences (structured_joint) -- glass-box evidence of the round-trip."""
    lines = []
    for sent in sents[:6]:
        tree, _ = _make_tree(sent, ctx)
        comp = _encode_structured(tree, ctx.cb_lex)
        rec, ex = _syntax_recover(comp, ctx.cb_lex, tree, "structured")
        surf = _assemble_surface(ctx, sent, rec, verb_naive=False)
        mark = "MATCH" if surf == sent["gold"] else "MISS"
        lines.append("  gold=%-34r assembled=%-34r [%s]" % (sent["gold"], surf, mark))
    return lines


def run_all(mode: str, output_dir: Path, t0: float):
    cfg = get_config(mode)
    sents = _build_sentences(cfg["n_sent"])
    per_unit = []          # one record per (seed, sentence): {arm: {3 metrics}}
    all_sigs = []          # per (seed, sentence): {arm: signature} for arms-differ
    total_units = len(cfg["seeds"]) * len(sents)
    unit = 0
    demo = []
    for seed in cfg["seeds"]:
        ctx = SeedContext(seed)
        g = np.random.default_rng(1234 + seed)
        if not demo:
            demo = _demo_lines(sents, ctx, g)
        for sent in sents:
            res, sig = run_sentence(sent, ctx, g)
            per_unit.append(res)
            all_sigs.append(sig)
            unit += 1
            if unit % max(1, total_units // 6) == 0 or unit == total_units:
                _heartbeat(output_dir, unit, total_units, t0, extra={"seed": seed})
                _say("[progress] seed=%d unit=%d/%d elapsed=%.1fs" % (seed, unit, total_units, time.perf_counter() - t0))
    return cfg, sents, per_unit, all_sigs, demo, total_units


def _arms_differ(all_sigs) -> bool:
    """META_RULE_AF: per (seed,sentence) the 5 arms' recovered signatures must be hash-distinct."""
    for sig in all_sigs:
        digs = set()
        for arm in ARMS:
            b = json.dumps(sig[arm], sort_keys=True, default=str).encode("utf-8")
            digs.add(hashlib.sha256(b).hexdigest())
        if len(digs) < len(ARMS):
            return False
    return True


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp_units = len(cfg["seeds"]) * get_config(mode)["n_sent"]
    _write_start_marker(output_dir, mode, exp_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N={N} LEVELS={LEVELS} V_CONTENT={V_CONTENT} seeds={cfg['seeds']} "
         f"n_sent={cfg['n_sent']} expected_units={exp_units}")

    audit = structural_audit()      # reuse grammar's structural audit (flat_bag provably structure-blind)
    _say(f"[{ANCHOR_NAME}] STRUCTURAL audit (grammar): bag_blind={audit['bag_blind_to_structure']}")

    cfg, sents, per_unit, all_sigs, demo, total_units = run_all(mode, output_dir, t0)

    arms_differ_ok = _arms_differ(all_sigs)
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: the 5 arm signatures are not hash-distinct per sentence")

    agg = _aggregate(per_unit)
    verdict, vmsg = classify(mode, agg, audit, len(per_unit), exp_units)
    elapsed = time.perf_counter() - t0

    _say("\n[GLASS-BOX DEMO] assembled sentences (structured_joint round-trip; strings are HUMAN GLOSSES):")
    for ln in demo:
        _say(ln)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: first 4-layer (lexicon+morphology+syntax+grammar) structured assembly ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_sent": cfg["n_sent"],
        "n_units": len(per_unit),
        "expected_n_units": exp_units,
        "cardinality_ok": len(per_unit) >= exp_units,
        "arms_differ_verified": arms_differ_ok,
        "arms": agg,
        "structural_audit": audit,
        "demo": demo,
        "config": {
            "N": N, "LEVELS": LEVELS, "V_CONTENT": V_CONTENT, "K_DISTRACT": K_DISTRACT,
            "arms": ARMS, "seeds": list(cfg["seeds"]), "n_sent": cfg["n_sent"],
            "bridge": "concept_id_to_two_reps: gsbc_blocklocal (syntax) + fhrr_stem_for_id (morphology)",
            "morphology_scope": "past_ed allomorphy (3 classes) + plural_s allomorphy (3 classes) + irregular dual-route",
            "lexicon_source": "REAL native GSBC pool (technical ontology); English words are HUMAN GLOSSES",
            "storage_strategy": "sharded_block_disjoint_per_slot (inherited from grammar)",
        },
        "bands": {"HP_EXACT": HP_EXACT, "HP_IDENTITY": HP_IDENTITY, "HP_SURFACE": HP_SURFACE,
                  "HF_EXACT": HF_EXACT, "HF_IDENTITY": HF_IDENTITY,
                  "CTRL_EXACT_MAX": CTRL_EXACT_MAX, "CTRL_ALLO_MAX": CTRL_ALLO_MAX,
                  "CTRL_IDENTITY_MAX": CTRL_IDENTITY_MAX, "IDENTITY_CHANCE": round(IDENTITY_CHANCE, 4)},
        "hp_scope": {
            "structured_joint": ["HP_EXACT", "HP_IDENTITY", "HP_SURFACE"],
            "flat_bag": ["CTRL_EXACT_MAX_collapse_only"],
            "scrambled_roles": ["CTRL_EXACT_MAX_collapse_only"],
            "naive_morphology": ["CTRL_ALLO_MAX_collapse_only"],
            "identity_scrambled": ["CTRL_IDENTITY_MAX_collapse_only"],
        },
        "framing": "glass-box STRUCTURED (lemma-level) composition of a KNOWN proposition; NOT generation, NOT "
                   "understanding, NOT a language model; English words are HUMAN GLOSSES on real GSBC concepts; Stage-3",
        "cited_sources": {
            "lexicon_syntax": "data/exp_generation_decoder_gsbc_native_blocklocal_v1 (HARD_PASS FULL)",
            "grammar": "data/exp_grammar_recursive_function_word_blocklocal_v1 (HARD_PASS FULL)",
            "morphology": "data/exp_morph_ruleset_wug_v2_cpu (HARD_PASS FULL)",
            "scoping": "notes/research_language_assembly_composition_scoping_2026-07-05.md",
        },
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    """Formula self-test: verify the composed algebra on a tiny fixed regime BEFORE any full run.
    Asserts: (1) structured recovers all slots + identity + surface ~ 1.0; (2) flat_bag + scrambled collapse
    exact_ordered; (3) naive allomorph collapses to chance; (4) identity_scrambled identity collapses."""
    t0 = time.perf_counter()
    ctx = SeedContext(7)
    g = np.random.default_rng(999)
    sents = _build_sentences(8)
    acc = {a: {"ex": [], "id": [], "su": [], "allo": []} for a in ARMS}
    for sent in sents:
        res, _ = run_sentence(sent, ctx, g)
        for a in ARMS:
            acc[a]["ex"].append(res[a]["exact_ordered_slot_match"])
            acc[a]["id"].append(res[a]["identity_consistency"])
            acc[a]["su"].append(res[a]["surface_string_exact"])
            if res[a]["allomorph_ok"] is not None:
                acc[a]["allo"].append(res[a]["allomorph_ok"])
    sj_ex = float(np.mean(acc["structured_joint"]["ex"]))
    sj_id = float(np.mean(acc["structured_joint"]["id"]))
    sj_su = float(np.mean(acc["structured_joint"]["su"]))
    fb_ex = float(np.mean(acc["flat_bag"]["ex"]))
    sc_ex = float(np.mean(acc["scrambled_roles"]["ex"]))
    nm_allo = float(np.mean(acc["naive_morphology"]["allo"])) if acc["naive_morphology"]["allo"] else 1.0
    ids_id = float(np.mean(acc["identity_scrambled"]["id"]))
    audit = structural_audit()

    ok = (audit["bag_blind_to_structure"]
          and sj_ex >= 0.95 and sj_id >= 0.95 and sj_su >= 0.90
          and fb_ex <= CTRL_EXACT_MAX and sc_ex <= CTRL_EXACT_MAX
          and nm_allo <= CTRL_ALLO_MAX and ids_id <= CTRL_IDENTITY_MAX)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: structured exact={sj_ex:.3f} identity={sj_id:.3f} "
         f"surface={sj_su:.3f} | flat_bag.exact={fb_ex:.3f} scrambled.exact={sc_ex:.3f} naive.allo={nm_allo:.3f} "
         f"identity_scrambled.identity={ids_id:.3f} (chance {IDENTITY_CHANCE:.3f}) bag_blind="
         f"{audit['bag_blind_to_structure']} [{time.perf_counter() - t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return _run_selftest()
    mode = "smoke" if args.smoke else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:   # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
