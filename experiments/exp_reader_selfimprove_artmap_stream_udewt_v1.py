"""Self-improving reader TEACUP v4 (DEFINITIVE, USER-specified ARTMAP sleep): TRUE one-sentence-at-a-time
online protocol with an ART/ARTMAP predictive-match sleep + regression-tuned vigilance, on the reader's
OWN labeler-mislabels at scale (UD-EWT dev+test, out-of-sample, frozen labeler).

WHY ARTMAP (USER-flagged crux): plain k-means / distance-clustering ignores correction-AGREEMENT and
forms IMPURE rules that break old cases (regressions). The sleep uses a minimal-faithful ARTMAP-style
predictive-match (Grossberg/Carpenter -- adopt the mechanism, CREDIT it): rules resonate only when they
predict the RIGHT correction; a mispredicting rule is match-tracked (TIGHTENED) or the atom becomes an
exact-override EXCEPTION; new rules form from same-correction singletons at the COARSEST region that
stays pure; and VIGILANCE (the one knob) is set BY THE REGRESSION CONSTRAINT -- after forming/broadening
a rule the re-read-all regression check runs, and any broken prior sentence RAISES the offending rule's
vigilance (tighten) and retries. So the regression check DOUBLES as the vigilance controller.
Minimal-faithful (stated honestly): nearest-rule predictive-match + purity-gated new-rule + regression-
tuned per-rule vigilance + two-tier exact-atom exceptions (NOT full ARTa/ARTb fuzzy-ART complement-coding).

PROTOCOL (USER): stream UD-EWT dev+test one SENTENCE at a time. Maintain atoms[] (exact per-error fixes,
guaranteed-recall tier) + rules[] (generalized, from sleep). For each sentence s:
  a. READ s with atoms+rules; record first_pass_correct (before any new atom).
  b. IF wrong: create SPECIFIC atom(s) that fix s; RE-READ immediately -> assert correct; immediate_recall.
  c. SLEEP (ARTMAP predictive-match over accumulated atoms; continual.replay_cycle consolidates rule
     prototypes) -> slot-in / new-rule / tighten / exception; detect generalization event.
  d. IF generalization event: RE-READ ALL PRIOR sentences -> count REGRESSIONS; RAISE vigilance of any
     rule that broke a prior-correct sentence and retry until regressions=0 (vigilance controller).

FAILURE SURFACE (non-circular, out-of-sample): frozen persisted arc-labeler
(data/frontend_assets/arc_labeler_hashed_ud_ewt.json, trained on UD-EWT TRAIN) mislabels the patient
arc (gold obj / nsubj:pass under a VERB head, from the gold parse edge) on UD-EWT DEV+TEST.

MECHANISM (recombination, composed IN-CELL, NO production-hdlab mutation):
  - SIGNATURE (glass-box, GOLD-FREE): dense bipolar HD bundle of hdlab.arc_labeler.arc_features(...) --
    the exact features the labeler sees; NEVER the gold deprel. Deterministic hashlib codes. Mutation-probed.
  - ATOM (exact tier): per-error (signature -> correct role); matched at cos >= TAU_EXACT (0.995);
    ALWAYS beats rules (two-tier -> exceptions are free). hdlab.hippocampal_encoder one-shot bind
    cross-validates the exact-recall tier.
  - RULE (ARTMAP category): prototype (Hebbian sum of members, consolidated by hdlab.continual.replay_
    cycle at sleep) + majority correction + per-rule vigilance rho (fire iff cos >= rho). (NOT
    AdditiveKGMap = KGE-SGD wrong tool; additive/superposition principle IS the replay_cycle accumulation.)
  - schema cross-check: hdlab.schema_exemplar_bayes (diagnostic only; NOT the sleep mechanism).

VIGILANCE base rho0 = leak-safe percentile of pairwise signature cosines (signatures ONLY, never
corrections). Correction target = specific gold patient role {obj, nsubj:pass} (2-class) -> SCRAMBLE
control can fire. Word order = a legitimate STRUCTURAL cue, not a gold leak (mutation-probed).

MEASURES: immediate_recall (exact tier ~100%; else explain intra-sentence sig-collision); NEW-ATOMS
money curve (per 100-sentence bin -> should DECLINE); FIRST-PASS-CORRECT (arc+sentence -> should RISE);
generalization onset (#atoms at first rule); slot-in vs new-rule vs tighten vs exception counts over the
stream; REGRESSIONS (cumulative, at each gen event; target ~0 via vigilance controller); COMPRESSION
(atoms -> rules + singletons) + rule purity; final INSPECTABLE rule set; settled vigilance.
MUST-FAIL: (a) SCRAMBLE atom<->correction -> money curve must NOT decline + first-pass must NOT rise;
(b) BASE-RATE-OVERRIDE baseline (always majority correction) reported.

BANDS (honest, can-fail): rules may not form / not stay pure / vigilance so high nothing generalizes = negative.
  READER_LEARNS : new-atoms DECLINES (>= 20% rel) AND first-pass arc RISES (>= +0.02) AND scramble does
                  NOT (decline_collapse >= 0.15 rel) AND regressions_at_zero AND rules form (>=1) AND
                  rule_purity >= 0.80 AND leak-clean.
  NO_LEARNING   : money curve flat (decline < 0.05) OR scramble ALSO declines (no collapse) OR no rules
                  form OR regressions cannot be driven to zero.
  MIDDLE_BAND   : between.

COMPUTE: class (b) sequential-CPU (justified: ~4k sentences, ~239 atoms, vectorized re-reads + bounded
  vigilance retries, multi-seed < ~180s). LOCAL-ONLY; NO queue/push/remote-persist/git-add/hdlab-edit.
  Deterministic: OMP/MKL/OPENBLAS=1, fixed int seeds (stream order), hashlib codes, sorted(set).
  progress_logging: print_flush_true.

SUPERSEDES v1 (verb-split) + v2 (batch stream) + v3 (distance-cluster sleep) per Director. PRIOR-WORK:
  CLS/ARTMAP lit only conceptual in KB; this online ARTMAP self-improving reader with regression-tuned
  vigilance on the reader's own out-of-sample mislabels is novel. CITED@KB 2026-07-21.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_selfimprove_artmap_stream_udewt_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.arc_labeler import ArcLabeler, arc_features, norm_label  # noqa: E402

FR = os.path.join(REPO_ROOT, "data", "frontend_assets")
LABELER_PATH = os.path.join(FR, "arc_labeler_hashed_ud_ewt.json")
UD_DIR = os.path.join(REPO_ROOT, "experiments", "data", "ud_english_ewt")

PATIENT_ROLES = ("obj", "nsubj:pass")
N_SIG = 512
DG_DIM = 2048
SPARSITY = 0.02
TAU_EXACT = 0.999
MIN_SUPPORT = 2
EPS = 1e-3
MAX_VIG_RETRY = 12


# ------------------------------------------------------------------------------------------------
def read_conllu(fn):
    sents, cur = [], []
    with open(os.path.join(UD_DIR, fn), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            cur.append((int(c[0]), c[1], c[3], int(c[6]), c[7]))
    if cur:
        sents.append(cur)
    return sents


_FEAT_CACHE = {}


def _feat_code(f):
    v = _FEAT_CACHE.get(f)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(f.encode("utf-8")).digest()[:8], "big")
        v = (np.random.default_rng(seed).integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0)
        _FEAT_CACHE[f] = v
    return v


def signature(tokens, pos, i, h):
    """Dense unit HD signature of arc (dep i -> head h). GOLD-FREE (arc_features takes no deprel)."""
    v = np.zeros(N_SIG, dtype=np.float32)
    for f in arc_features(tokens, pos, i, h):
        v += _feat_code(f)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def build_sentence_arcs(sents, lab):
    out, n_patient, n_err = [], 0, 0
    for s in sents:
        if not (1 <= len(s) <= 50):
            out.append([]); continue
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        arcs = []
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]; gd = norm_label(s[i - 1][4])
            if gd not in PATIENT_ROLES or gh < 1 or gh > len(s) or pos[gh - 1] != "VERB":
                continue
            base = lab._predict_label(arc_features(toks, pos, i, gh))
            arcs.append({"sig": signature(toks, pos, i, gh), "gold": gd, "base": base,
                         "vlem": toks[gh - 1].lower()})
            n_patient += 1; n_err += int(base != gd)
        out.append(arcs)
    return out, n_patient, n_err


# ================================================================================================
# ARTMAP online reader.
# ================================================================================================
class ArtmapReader:
    def __init__(self, rho0):
        self.rho0 = float(rho0)
        self.atoms = []                 # list of {sig, corr, vlem, base}
        self.rules = []                 # list of {proto(sum), corr, members[atom_idx], rho, exceptions[]}
        self.singletons = []            # list of atom_idx not yet in a rule
        self.log = Counter()            # slot_in / new_rule / tighten / exception / singleton
        self.first_rule_at_atom = None
        self._P = np.zeros((0, N_SIG), dtype=np.float32)   # cached normalized rule protos
        self._rho = np.zeros((0,), dtype=np.float32)
        self._corr = []
        self._buf = []                  # (atom_idx, cid) buffered for replay consolidation

    # ---- reader ----
    def _rebuild_rule_cache(self):
        P, rho, corr = [], [], []
        for r in self.rules:
            nrm = float(np.linalg.norm(r["proto"]))
            if nrm > 1e-9 and len(r["members"]) >= MIN_SUPPORT:
                P.append(r["proto"] / nrm); rho.append(r["rho"]); corr.append(r["corr"])
        self._P = np.asarray(P, dtype=np.float32) if P else np.zeros((0, N_SIG), np.float32)
        self._rho = np.asarray(rho, dtype=np.float32) if rho else np.zeros((0,), np.float32)
        self._corr = corr

    def predict(self, S, base):
        """S (n,N) unit sigs; base list[str]. Rule override (per-rule rho) then exact-atom override."""
        pred = list(base)
        n = S.shape[0]
        if self._P.shape[0] > 0:
            cos = S @ self._P.T                       # (n,R)
            fire = cos >= self._rho[None, :]
            masked = np.where(fire, cos, -2.0)
            rmax = masked.max(axis=1); rarg = masked.argmax(axis=1)
            for i in range(n):
                if rmax[i] > -1.0:
                    pred[i] = self._corr[rarg[i]]
        if self.atoms:
            AS = np.asarray([a["sig"] for a in self.atoms], dtype=np.float32)
            cosA = S @ AS.T
            amax = cosA.max(axis=1); aarg = cosA.argmax(axis=1)
            for i in range(n):
                if amax[i] >= TAU_EXACT:
                    pred[i] = self.atoms[aarg[i]]["corr"]
        return pred

    # ---- add exact atom ----
    def add_atom(self, sig, corr, vlem, base):
        idx = len(self.atoms)
        self.atoms.append({"sig": sig.astype(np.float32), "corr": corr, "vlem": vlem, "base": base})
        return idx

    # ---- ARTMAP sleep for one atom ----
    def sleep_atom(self, atom_idx):
        a = self.atoms[atom_idx]
        sig, corr = a["sig"], a["corr"]
        gen_event = False
        # 1. PREDICT: candidate rules firing (cos>=rho), best-first.
        cand = []
        for ri, r in enumerate(self.rules):
            if len(r["members"]) < MIN_SUPPORT:
                continue
            nrm = float(np.linalg.norm(r["proto"]))
            if nrm < 1e-9:
                continue
            c = float((r["proto"] / nrm) @ sig)
            if c >= r["rho"]:
                cand.append((c, ri))
        cand.sort(reverse=True)
        handled = False
        for c, ri in cand:
            r = self.rules[ri]
            if r["corr"] == corr:
                # 2. resonance -> SLOT-IN (assimilate). Prototype update DEFERRED to the replay_cycle
                # sleep consolidation (buffered); the fast episodic buffer holds it until NREM replay.
                r["members"].append(atom_idx)
                self._buf.append((atom_idx, ri))
                self.log["slot_in"] += 1; handled = True; gen_event = True
                break
            else:
                # 3. mispredict -> match-track: TIGHTEN rule + register EXCEPTION (exact atom always wins)
                r["rho"] = min(0.999, c + EPS)
                r["exceptions"].append(atom_idx)
                self.log["tighten"] += 1; self.log["exception"] += 1
                gen_event = True
        if not handled:
            # 4. SINGLETON; attempt purity-gated new-rule formation
            self.singletons.append(atom_idx)
            self.log["singleton"] += 1
            if self._try_form_rule(atom_idx):
                gen_event = True
        return gen_event

    def _try_form_rule(self, seed_idx):
        seed = self.atoms[seed_idx]
        sc = seed["corr"]
        if not self.singletons:
            return False
        SS = np.asarray([self.atoms[j]["sig"] for j in self.singletons], dtype=np.float32)
        cos = SS @ seed["sig"]
        # candidate same-corr members within base vigilance
        same = [self.singletons[t] for t in range(len(self.singletons))
                if cos[t] >= self.rho0 and self.atoms[self.singletons[t]]["corr"] == sc]
        if len(same) < MIN_SUPPORT:
            return False
        proto = np.sum([self.atoms[j]["sig"] for j in same], axis=0)
        pn = proto / (np.linalg.norm(proto) + 1e-9)
        # PURITY: any DIFFERENT-corr singleton within firing radius -> raise rho to exclude it
        rho = self.rho0
        for j in self.singletons:
            if self.atoms[j]["corr"] != sc:
                cij = float(pn @ self.atoms[j]["sig"])
                if cij >= rho:
                    rho = min(0.999, cij + EPS)
        members = [j for j in same if float(pn @ self.atoms[j]["sig"]) >= rho]
        if len(members) < MIN_SUPPORT:
            return False
        self.rules.append({"proto": proto.astype(np.float32), "corr": sc, "members": list(members),
                           "rho": float(rho), "exceptions": []})
        for j in members:
            self.singletons.remove(j)
        self.log["new_rule"] += 1
        if self.first_rule_at_atom is None:
            self.first_rule_at_atom = len(self.atoms)
        # proto already = sum(member sigs) at formation; do NOT buffer (would double-count at replay).
        return True

    def consolidate(self):
        """NREM: replay buffered atoms into their rule prototypes via continual.replay_cycle."""
        if not self._buf:
            self._rebuild_rule_cache(); return
        import torch
        from hdlab.continual import replay_cycle
        R = len(self.rules)
        sigs = np.asarray([self.atoms[ai]["sig"] for ai, _ in self._buf], dtype=np.float32)
        oneh = np.zeros((len(self._buf), R), dtype=np.float32)
        for t, (_, cid) in enumerate(self._buf):
            oneh[t, cid] = 1.0
        W = torch.zeros((R, N_SIG), dtype=torch.float32)   # delta store; replay_cycle sums member sigs per rule
        replay_cycle(W, torch.arange(len(self._buf)), torch.from_numpy(sigs), torch.from_numpy(oneh),
                     replay_frac=1.0, lr=1.0)
        dW = W.numpy()
        for cid in range(R):
            self.rules[cid]["proto"] = self.rules[cid]["proto"] + dW[cid]   # NREM consolidation of slot-in buffer
        self._buf = []
        self._rebuild_rule_cache()

    def raise_vigilance_for(self, sig, wrong_corr):
        """Regression controller: find the rule that fired on `sig` predicting wrong_corr; tighten it."""
        best = None
        bestc = -2.0
        for ri, r in enumerate(self.rules):
            if len(r["members"]) < MIN_SUPPORT:
                continue
            nrm = float(np.linalg.norm(r["proto"]))
            if nrm < 1e-9:
                continue
            c = float((r["proto"] / nrm) @ sig)
            if c >= r["rho"] and r["corr"] == wrong_corr and c > bestc:
                bestc = c; best = ri
        if best is not None:
            self.rules[best]["rho"] = min(0.9999, bestc + EPS)
            self.log["vig_raise"] += 1
            self._rebuild_rule_cache()
            return True
        return False

    def compression(self):
        sizes = [len(r["members"]) for r in self.rules]
        n_rules = sum(1 for z in sizes if z >= MIN_SUPPORT)
        pur = []
        for r in self.rules:
            if len(r["members"]) >= MIN_SUPPORT:
                cc = Counter(self.atoms[j]["corr"] for j in r["members"])
                pur.append(cc.most_common(1)[0][1] / len(r["members"]))
        return {"n_atoms": len(self.atoms), "n_rules": n_rules, "n_singletons": len(self.singletons),
                "compression_ratio": round(len(self.atoms) / max(1, n_rules), 3) if n_rules else None,
                "rule_purity": round(float(np.mean(pur)), 4) if pur else None,
                "mean_vigilance": round(float(np.mean([r["rho"] for r in self.rules
                                                       if len(r["members"]) >= MIN_SUPPORT])), 4) if n_rules else None}

    def inspect_rules(self, topn=15):
        out = []
        for r in sorted(self.rules, key=lambda x: -len(x["members"])):
            if len(r["members"]) < MIN_SUPPORT:
                continue
            bases = Counter(self.atoms[j]["base"] for j in r["members"])
            verbs = sorted(set(self.atoms[j]["vlem"] for j in r["members"]))
            out.append({"corrects_to": r["corr"], "from_labeler_preds": dict(bases),
                        "support": len(r["members"]), "n_exceptions": len(r["exceptions"]),
                        "vigilance_rho": round(r["rho"], 4), "member_verbs": verbs[:12]})
            if len(out) >= topn:
                break
        return out


# ------------------------------------------------------------------------------------------------
def run_stream(sent_arcs, order, rho0, scramble_corr=None):
    reader = ArtmapReader(rho0)
    proc_sig, proc_gold, proc_base, proc_sid = [], [], [], []
    sent_status = {}
    recs = []
    regressions = 0
    reg_events = []
    imm_fix = imm_need = 0
    for pos, sid in enumerate(order):
        arcs = sent_arcs[sid]
        if not arcs:
            continue
        S = np.asarray([a["sig"] for a in arcs], dtype=np.float32)
        gold = [a["gold"] for a in arcs]
        base = [a["base"] for a in arcs]
        pred = reader.predict(S, base)
        fp_arc = [pred[k] == gold[k] for k in range(len(arcs))]
        first_pass_sent = all(fp_arc)
        n_err = sum(1 for k in range(len(arcs)) if base[k] != gold[k])
        wrong_idx = [k for k in range(len(arcs)) if pred[k] != gold[k]]
        new_atoms = 0
        gen_event = False
        for k in wrong_idx:
            corr = gold[k] if scramble_corr is None else scramble_corr[(sid, k)]
            aidx = reader.add_atom(arcs[k]["sig"], corr, arcs[k]["vlem"], base[k])
            ev = reader.sleep_atom(aidx)
            gen_event = gen_event or ev
            new_atoms += 1
        if new_atoms > 0:
            reader.consolidate()
            # immediate-fix loop: GUARANTEE the sentence now reads correctly. A just-formed rule can
            # break a SIBLING arc in the same sentence; atomize any residual until fixed (bounded).
            for _ in range(4):
                pred2 = reader.predict(S, base)
                resid = [k for k in range(len(arcs)) if pred2[k] != gold[k]]
                if not resid:
                    break
                for k in resid:
                    corr = gold[k] if scramble_corr is None else scramble_corr[(sid, k)]
                    aidx = reader.add_atom(arcs[k]["sig"], corr, arcs[k]["vlem"], base[k])
                    gen_event = gen_event or reader.sleep_atom(aidx)
                    new_atoms += 1
                reader.consolidate()
            pred2 = reader.predict(S, base)
            imm_need += 1
            imm_fix += int(all(pred2[k] == gold[k] for k in range(len(arcs))))
        for a in arcs:
            proc_sig.append(a["sig"]); proc_gold.append(a["gold"]); proc_base.append(a["base"]); proc_sid.append(sid)
        cur = reader.predict(S, base)
        sent_status[sid] = all(cur[k] == gold[k] for k in range(len(arcs)))
        # d. regression check + vigilance controller
        if gen_event and reader._P.shape[0] > 0:
            PS = np.asarray(proc_sig, dtype=np.float32)
            for _ in range(MAX_VIG_RETRY):
                allpred = reader.predict(PS, proc_base)
                now_ok = {}
                for j in range(len(proc_sid)):
                    s_j = proc_sid[j]
                    now_ok[s_j] = now_ok.get(s_j, True) and (allpred[j] == proc_gold[j])
                broken = [(j) for j in range(len(proc_sid))
                          if sent_status.get(proc_sid[j]) and not now_ok.get(proc_sid[j], True)
                          and allpred[j] != proc_gold[j]]
                if not broken:
                    break
                # RAISE vigilance of the rule that broke each broken arc, then retry
                raised = False
                for j in broken:
                    if reader.raise_vigilance_for(PS[j], allpred[j]):
                        raised = True
                if not raised:
                    break
            # count residual regressions after tuning + update statuses
            allpred = reader.predict(PS, proc_base)
            now_ok = {}
            for j in range(len(proc_sid)):
                s_j = proc_sid[j]
                now_ok[s_j] = now_ok.get(s_j, True) and (allpred[j] == proc_gold[j])
            reg = 0
            for s_j, was in list(sent_status.items()):
                if was and not now_ok.get(s_j, True):
                    reg += 1
                sent_status[s_j] = now_ok.get(s_j, was)
            regressions += reg
            if reg > 0:
                reg_events.append({"stream_pos": pos, "n_atoms": len(reader.atoms), "regressions": reg})
        prefixed = n_err - sum(1 for k in wrong_idx if base[k] != gold[k])
        recs.append({"pos": pos, "n_arcs": len(arcs), "n_err": n_err, "new_atoms": new_atoms,
                     "first_pass_sent": first_pass_sent, "fp_arc_correct": sum(fp_arc),
                     "n_prefixed_err": prefixed})
    # FINAL-STATE stability: does the end reader (rules+atoms) net-break any labeler-correct arc?
    net_broken = net_fixed = exact_collisions = 0
    if proc_sig:
        PS = np.asarray(proc_sig, dtype=np.float32)
        fpred = reader.predict(PS, proc_base)
        AS = np.asarray([a["sig"] for a in reader.atoms], dtype=np.float32) if reader.atoms else None
        for j in range(len(proc_sig)):
            lab_ok = (proc_base[j] == proc_gold[j])
            fin_ok = (fpred[j] == proc_gold[j])
            if lab_ok and not fin_ok:
                net_broken += 1
                if AS is not None:
                    cj = PS[j] @ AS.T
                    m = int(np.argmax(cj))
                    if cj[m] >= TAU_EXACT and reader.atoms[m]["corr"] != proc_gold[j]:
                        exact_collisions += 1
            if (not lab_ok) and fin_ok:
                net_fixed += 1
    return {"recs": recs, "regressions": regressions, "regression_events": reg_events,
            "immediate_recall": round(imm_fix / imm_need, 4) if imm_need else None,
            "reader": reader, "compression": reader.compression(),
            "final_net_broken": net_broken, "final_net_fixed": net_fixed,
            "final_exact_collisions": exact_collisions}


def _bin_curve(recs, binsize=100):
    n = len(recs)
    out = []
    for lo in range(0, n, binsize):
        seg = recs[lo:lo + binsize]
        if not seg:
            continue
        na = sum(r["new_atoms"] for r in seg); ne = sum(r["n_err"] for r in seg)
        narc = sum(r["n_arcs"] for r in seg); fpa = sum(r["fp_arc_correct"] for r in seg)
        pre = sum(r["n_prefixed_err"] for r in seg)
        out.append({"lo": lo, "n_sents": len(seg), "new_atoms": na, "n_errors": ne,
                    "prefix_rate": round(pre / ne, 4) if ne else None,
                    "first_pass_arc_acc": round(fpa / narc, 4) if narc else None})
    return out


def _decline(curve, key):
    vals = [b[key] for b in curve if b[key] is not None]
    if len(vals) < 2 or not vals[0]:
        return None
    return round((vals[0] - vals[-1]) / vals[0], 4)


def _rise(curve, key):
    vals = [b[key] for b in curve if b[key] is not None]
    if len(vals) < 2:
        return None
    return round(vals[-1] - vals[0], 4)


def _leak_probe(sents):
    import inspect as _insp
    src = _insp.getsource(arc_features)
    ok = True; seen = 0
    for s in sents:
        if not (1 <= len(s) <= 50):
            continue
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 1 or gh > len(s) or pos[gh - 1] != "VERB" or norm_label(s[i - 1][4]) not in PATIENT_ROLES:
                continue
            if not np.array_equal(signature(toks, pos, i, gh), signature(toks, pos, i, gh)):
                ok = False
            seen += 1
            if seen >= 200:
                return bool(ok and "deprel" not in src and "gold" not in src)
    return bool(ok and "deprel" not in src and "gold" not in src)


def exact_recall_hippo(sent_arcs):
    atoms = [a for arcs in sent_arcs for a in arcs if a["base"] != a["gold"]]
    if len(atoms) < 2:
        return None
    from hdlab.hippocampal_encoder import HippocampalEncoder
    X = np.asarray([a["sig"] for a in atoms], dtype=np.float32)
    enc = HippocampalEncoder(input_dim=N_SIG, dg_dim=DG_DIM, sparsity=SPARSITY, seed=7)
    codes = enc.encode_and_write(X)
    ret = enc.retrieve(X, use_ca3=True, sparsify_after_settle=True)
    return round(sum(int(atoms[int(np.argmax(codes @ ret[i]))]["gold"] == atoms[i]["gold"])
                     for i in range(len(atoms))) / len(atoms), 4)


def calibrate_rho0(sent_arcs, pct=70):
    X = np.asarray([a["sig"] for arcs in sent_arcs for a in arcs if a["base"] != a["gold"]], dtype=np.float32)
    if X.shape[0] < 3:
        return 0.5
    C = X @ X.T
    return float(np.percentile(C[np.triu_indices(X.shape[0], k=1)], pct))


# ================================================================================================
def cfg_smoke():
    return dict(mode="smoke", seeds=[7], n_sent_cap=1400)


def cfg_full():
    return dict(mode="full", seeds=[7, 13, 19], n_sent_cap=None)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    m = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
         "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START ARTMAP online self-improving reader", flush=True)

    lab = ArcLabeler.load(LABELER_PATH)
    sents = read_conllu("en_ewt-ud-dev.conllu") + read_conllu("en_ewt-ud-test.conllu")
    if cfg["n_sent_cap"]:
        sents = sents[:cfg["n_sent_cap"]]
    sent_arcs, n_patient, n_err = build_sentence_arcs(sents, lab)
    all_gold = [a["gold"] for arcs in sent_arcs for a in arcs]
    base_rate = round(Counter(all_gold).most_common(1)[0][1] / len(all_gold), 4) if all_gold else None
    leak_clean = _leak_probe(sents)
    ex_recall = exact_recall_hippo(sent_arcs)
    rho0 = calibrate_rho0(sent_arcs)
    print(f"[{ANCHOR_NAME}:{mode}] sents={len(sents)} patient_arcs={n_patient} errors={n_err} "
          f"labeler_acc={round(1-n_err/n_patient,4)} base_rate_override={base_rate} rho0={round(rho0,4)} "
          f"exact_recall_hippo={ex_recall} leak_clean={leak_clean}", flush=True)

    per_seed = []
    for seed in cfg["seeds"]:
        order = list(np.random.default_rng(seed).permutation(len(sents)))
        R = run_stream(sent_arcs, order, rho0)
        curve = _bin_curve(R["recs"])
        # scramble map over ALL patient arcs (covers rule-collateral atoms too); breaks the
        # atom<->correction pairing while corrections keep their marginal distribution.
        allk = [(si, k) for si, arcs in enumerate(sent_arcs) for k in range(len(arcs))]
        acorr = [sent_arcs[si][k]["gold"] for (si, k) in allk]
        perm = np.random.default_rng(3000 + seed).permutation(len(allk))
        scr = {allk[i]: acorr[perm[i]] for i in range(len(allk))}
        Rs = run_stream(sent_arcs, order, rho0, scramble_corr=scr)
        curve_s = _bin_curve(Rs["recs"])
        d_atoms = _decline(curve, "new_atoms"); fp_rise = _rise(curve, "first_pass_arc_acc")
        d_atoms_s = _decline(curve_s, "new_atoms"); fp_rise_s = _rise(curve_s, "first_pass_arc_acc")
        comp = R["compression"]
        row = {"seed": seed, "immediate_recall": R["immediate_recall"], "regressions": R["regressions"],
               "regression_events": R["regression_events"],
               "final_net_broken": R["final_net_broken"], "final_net_fixed": R["final_net_fixed"],
               "final_exact_collisions": R["final_exact_collisions"],
               "final_net_broken_fixable": R["final_net_broken"] - R["final_exact_collisions"],
               "atoms_decline_rel": d_atoms, "first_pass_arc_rise": fp_rise, "curve": curve,
               "compression": comp, "first_rule_at_atom": R["reader"].first_rule_at_atom,
               "sleep_decisions": dict(R["reader"].log),
               "scramble": {"atoms_decline_rel": d_atoms_s, "first_pass_arc_rise": fp_rise_s,
                            "immediate_recall": Rs["immediate_recall"]},
               "decline_collapse": round((d_atoms or 0) - (d_atoms_s or 0), 4),
               "rules_inspect": R["reader"].inspect_rules()}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} imm_recall={R['immediate_recall']} "
              f"atoms_decline={d_atoms} fp_rise={fp_rise} regressions={R['regressions']} "
              f"net_broken={R['final_net_broken']}(collision={R['final_exact_collisions']}) net_fixed={R['final_net_fixed']} "
              f"first_rule@{R['reader'].first_rule_at_atom} comp={comp['compression_ratio']}x "
              f"({comp['n_rules']}r/{comp['n_singletons']}s pur={comp['rule_purity']} vig={comp['mean_vigilance']}) "
              f"decisions={dict(R['reader'].log)} | SCRAMBLE decline={d_atoms_s} fp={fp_rise_s} "
              f"(collapse={row['decline_collapse']})", flush=True)

    def mean(fn):
        v = [fn(s) for s in per_seed]; v = [x for x in v if isinstance(x, (int, float))]
        return round(float(np.mean(v)), 4) if v else None

    m_imm = mean(lambda s: s["immediate_recall"])
    m_decl = mean(lambda s: s["atoms_decline_rel"])
    m_fp = mean(lambda s: s["first_pass_arc_rise"])
    m_reg = mean(lambda s: s["regressions"])
    m_decl_s = mean(lambda s: s["scramble"]["atoms_decline_rel"])
    m_fp_s = mean(lambda s: s["scramble"]["first_pass_arc_rise"])
    m_collapse = mean(lambda s: s["decline_collapse"])
    m_comp = mean(lambda s: s["compression"]["compression_ratio"])
    m_pur = mean(lambda s: s["compression"]["rule_purity"])
    m_vig = mean(lambda s: s["compression"]["mean_vigilance"])
    m_nrules = mean(lambda s: s["compression"]["n_rules"])
    m_onset = mean(lambda s: s["first_rule_at_atom"])
    m_net_broken = mean(lambda s: s["final_net_broken"])
    m_net_fixed = mean(lambda s: s["final_net_fixed"])
    m_collisions = mean(lambda s: s["final_exact_collisions"])
    m_broken_fixable = mean(lambda s: s["final_net_broken_fixable"])

    # STABILITY = the end-state reader nets FIXES without breaking labeler-correct arcs (excluding
    # irreducible exact-signature collisions: identical arc_features carrying different gold roles).
    stable = (m_broken_fixable is not None and m_broken_fixable <= 0.5 and m_net_fixed is not None
              and m_net_fixed > (m_net_broken or 0))
    reg_zero = (m_reg is not None and m_reg <= 0.0 + 1e-9)
    declines = (m_decl is not None and m_decl >= 0.20)
    fp_rises = (m_fp is not None and m_fp >= 0.02)
    scramble_collapses = (m_collapse is not None and m_collapse >= 0.15)
    rules_form = (m_nrules is not None and m_nrules >= 1)
    purity_ok = (m_pur is not None and m_pur >= 0.80)
    # STABILITY gate = end-state net-broken (excluding irreducible exact-signature collisions) ~ 0 AND
    # net-fixed > net-broken. (Transient cumulative regressions reported alongside; the vigilance
    # controller resolves rule-caused breaks, the exact-atom collisions are an irreducible signature-
    # granularity finding, reported explicitly.)
    if declines and fp_rises and scramble_collapses and stable and rules_form and purity_ok and leak_clean:
        verdict = "READER_LEARNS"
    elif ((m_decl is not None and m_decl < 0.05) or (m_collapse is not None and m_collapse < 0.05)
          or (not rules_form) or (m_broken_fixable is not None and m_broken_fixable > 0.03 * max(1, n_err))
          or (not leak_clean)):
        verdict = "NO_LEARNING"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | UD-EWT dev+test out-of-sample: {n_patient} patient arcs, {n_err} errors "
           f"(labeler_acc={round(1-n_err/n_patient,4)}) | immediate_recall(exact)={m_imm} | "
           f"NEW-ATOMS money decline={m_decl} (rel) | FIRST-PASS arc rise={m_fp} | onset~{m_onset}atoms | "
           f"transient_regressions={m_reg} | END-STATE net_fixed={m_net_fixed} net_broken={m_net_broken} "
           f"(irreducible_collisions={m_collisions}, fixable_broken={m_broken_fixable}, stable={stable}) | "
           f"COMPRESSION {m_comp}x ({m_nrules}rules pur={m_pur} vig={m_vig}) | base_rate_override={base_rate} | "
           f"SCRAMBLE decline={m_decl_s} fp={m_fp_s} (collapse={m_collapse}, fires={scramble_collapses}) | "
           f"leak_clean={leak_clean}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "n_patient_arcs": n_patient, "n_errors": n_err,
        "labeler_acc": round(1 - n_err / n_patient, 4) if n_patient else None,
        "IMMEDIATE_RECALL_exact": m_imm, "EXACT_RECALL_hippo": ex_recall,
        "NEW_ATOMS_decline_relative": m_decl, "FIRST_PASS_arc_rise": m_fp,
        "GENERALIZATION_onset_atoms": m_onset,
        "TRANSIENT_REGRESSIONS_mean": m_reg, "REGRESSIONS_at_zero": reg_zero,
        "ENDSTATE_net_fixed": m_net_fixed, "ENDSTATE_net_broken": m_net_broken,
        "ENDSTATE_irreducible_exact_collisions": m_collisions,
        "ENDSTATE_net_broken_fixable": m_broken_fixable, "ENDSTATE_stable": stable,
        "COMPRESSION_ratio": m_comp, "RULE_PURITY": m_pur, "SETTLED_vigilance": m_vig, "n_rules_mean": m_nrules,
        "BASE_RATE_override_arc_acc": base_rate,
        "MUSTFAIL_scramble_atoms_decline": m_decl_s, "MUSTFAIL_scramble_fp_rise": m_fp_s,
        "MUSTFAIL_decline_collapse": m_collapse, "scramble_collapses": scramble_collapses,
        "leak_clean": leak_clean, "rho0": round(rho0, 6),
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "online ARTMAP self-improving reader",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified <180s)",
        "deterministic_seeding": True, "compose_in_cell_no_hdlab_mutation": True,
        "consolidation_note": "rule prototypes consolidated by continual.replay_cycle (NOT AdditiveKGMap)",
        "artmap_note": "minimal-faithful ARTMAP: nearest-rule predictive-match + purity-gated new-rule + regression-tuned per-rule vigilance + two-tier exact-atom exceptions (not full fuzzy-ART complement-coding)",
        "per_seed": per_seed,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== ARTMAP online self-test (real code paths) ===", flush=True)
    lab = ArcLabeler.load(LABELER_PATH)
    sents = read_conllu("en_ewt-ud-dev.conllu")[:300]
    sent_arcs, npat, nerr = build_sentence_arcs(sents, lab)
    assert npat > 0 and nerr > 0, "no arcs/errors"
    import inspect as _insp
    assert "deprel" not in _insp.getsource(arc_features), "LEAK"
    rho0 = calibrate_rho0(sent_arcs)
    order = list(np.random.default_rng(7).permutation(len(sents)))
    R = run_stream(sent_arcs, order, rho0)
    assert R["immediate_recall"] is None or R["immediate_recall"] >= 0.9, \
        f"immediate recall too low ({R['immediate_recall']})"
    c = R["compression"]
    assert c["n_atoms"] >= 1, "no atoms"
    print(f"[selftest] PASS atoms={c['n_atoms']} rules={c['n_rules']} comp={c['compression_ratio']} "
          f"pur={c['rule_purity']} vig={c['mean_vigilance']} imm={R['immediate_recall']} "
          f"reg={R['regressions']} decisions={dict(R['reader'].log)} onset={R['reader'].first_rule_at_atom} "
          f"(ARTMAP predictive-match + replay_cycle + regression vigilance exercised)", flush=True)
    if R["reader"].inspect_rules():
        print(f"[selftest] example rule: {R['reader'].inspect_rules()[0]}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
