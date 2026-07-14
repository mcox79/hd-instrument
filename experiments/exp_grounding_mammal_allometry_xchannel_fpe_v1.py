"""Mammal-allometry CROSS-CHANNEL GROUNDING cell (Track-B grounding build #2).

WHY THIS CELL EXISTS -- the A-INDEPENDENT fair test the periodic result demanded.
  The periodic-table cell (exp_grounding_periodic_xchannel_fpe_v1) was CONFOUNDED:
  its group/period/block relational graph is reverse-engineered FROM the periodic
  law -- group == valence-electron count, which DIRECTLY determines electronegativity,
  ionization energy, atomic radius. So channel A already secretly CONTAINED channel B,
  and the ablation landed MIDDLE_BAND / GROUNDING_REDUNDANT_WITH_RELATIONAL
  (A+B_FPE=0.567 vs A_alone=0.536, d=+0.031 < 0.05 threshold)
  MEASURED@d:/AI/hd-instrument/data/exp_grounding_periodic_xchannel_fpe_v1/metrics.json:agg.
  That could not answer "does grounding ADD" because the domain gave A a free copy of B.

  THIS cell uses a domain where the relation graph is DEMONSTRABLY NOT derived from
  the measured numeric channel:

Channel A (relational, native): species -> (HAS_ORDER o, HAS_FAMILY f, HAS_CLADE c)
  ingested into a REAL hdlab.kg_traversal.KGStore. ORDER / FAMILY / CLADE are
  PHYLOGENETIC classifications established by comparative anatomy + molecular
  systematics. NONE is a function of adult body mass, body length, longevity,
  gestation, or litter size. A_INDEPENDENCE PROOF (the whole point):
    - a 0.02 kg house mouse and a 55 kg capybara are BOTH order Rodentia;
    - a 0.008 kg shrew and a 5000 kg elephant are BOTH placental mammals (clade);
    - a 190 kg lion and a 4 kg domestic cat are BOTH family Felidae.
  Taxonomy partitions by ANCESTRY, not by size -- mass varies 10^6 WITHIN the graph's
  own cells. (Contrast periodic: group IS the property structure.)
Channel B (measured, exterior): adult body mass (kg), head-body length (cm), maximum
  longevity (yr), gestation (days), litter size. REAL database-measured biological
  quantities. CITED@AnAge/PanTHERIA/Walker's-Mammals reference class (approximate
  reference values; a rank/similarity kNN readout on min-max-normalized values is
  robust to modest per-value error -- the test is the A-vs-A+B DELTA, not absolute
  accuracy). Size/time variables are LOG10-transformed before normalization because
  allometric scaling is LINEAR IN LOG SPACE (Kleiber's law; life-history theory).
Encoding: FHRR fractional power encoding (FPE), SMOKED beside a spherical-interp
  LEVEL code, with a resonator CLEANUP decoder arm. (Reused verbatim from the
  proven periodic cell: decode-degradation did not bite, distance-decay Spearman 0.999.)
Oracle: allometric coupling. Predict a held-out species' numeric property from its
  consolidated neighbors (leave-one-out kNN in the consolidated geometry).
Decisive ablation: A alone (taxonomy similarity only) vs A+B (taxonomy fused with
  FPE/level attribute similarity of the OTHER four measured properties).

  EXPECTED here (unlike periodic): B should ADD over A, because allometry couples the
  numerics CONTINUOUSLY across taxa (a 100 kg deer and a 100 kg wolf share gestation/
  longevity scaling despite different ORDERS) -- signal the taxonomy graph cannot carry.
  If A+B beats A on THIS A-independent domain, that is the genuine grounding value-add.

The cell REPORTS which mode fired and does NOT conflate them:
  - ENCODING_BROKEN:      FPE similarity does not decay with numeric distance
  - MACHINERY_INSENSITIVE:the ablation cannot detect a load-bearing exogenous channel
  - GROUNDING_NEGATIVE:   B carries no exogenous info even alone
  - GROUNDING_REDUNDANT:  B grounds but is redundant with A on this domain (MIDDLE_BAND)
  - GROUNDING_ADDS:       B is load-bearing OVER A (HARD_PASS -- the value-add)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (regression-skill cell; no argmax capacity floor)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < A_ALONE skill < 0.95)
# - discriminator survives scale: self-test runs the REAL mechanism on the REAL
#   mammal data at n_dim=2048 (discriminator-preview arm) + FULL at n_dim=8192
# - HARD_PASS strictly above floor + margin (META_RULE_L)
# - HP_SCOPE per-arm declaration (see prereg)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * sum_k n_known(prop_k)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_justification (log10 for power-law size/time vars;
#   Gaussian-freq bandwidth chosen so kernel decays 1.0 -> ~0.1 across [0,1])
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the prereg
# - F.1 real_code_path: self-test CONSTRUCTS the REAL KGStore at n_dim=16 + ingests
# - F.2/F.3 substrate_signature: KGStore bound with BASE/portable kwargs only
#   (n_ent, n_rel, n_dim, generator); NO version-specific init_entities kwarg
# - F.4 guard_baseline_valid: A_ALONE (baseline) validated above RANDOM (floor)
# - progress_logging: print_flush_true (cheap cell; timeout << 1800 anyway)

ASCII-only per feedback_ascii_only_in_scripts. No em-dashes in output.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

# Real substrate objects the FULL run uses (F.1/F.2/F.3).
from hdlab.kg_traversal import KGStore

# Mandated validity-preflight gate (Pattern-5 auto-SCP shared module).
from experiments._validity_preflight import run_validity_preflight

ANCHOR_NAME = "grounding_mammal_allometry_xchannel_fpe_v1"

# --------------------------------------------------------------------------- #
# Arm names                                                                    #
# --------------------------------------------------------------------------- #
MEAN = "MEAN"
DEGREE = "DEGREE"
RANDOM = "RANDOM"
A_ALONE = "A_ALONE"
B_ALONE = "B_ALONE"                 # FPE numeric channel only (no relational) -> does B ground at all
A_PLUS_B_FPE = "A_PLUS_B_FPE"
A_PLUS_B_LEVEL = "A_PLUS_B_LEVEL"
RAW_FEATURE_KNN = "RAW_FEATURE_KNN"  # kNN on raw normalized other-features (informative reference)
ARMS = [MEAN, DEGREE, RANDOM, A_ALONE, B_ALONE, A_PLUS_B_FPE, A_PLUS_B_LEVEL, RAW_FEATURE_KNN]

# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #
FULL_CFG = dict(n_dim=8192, seeds=[7, 13, 19, 23, 29], fpe_freq_std=2.15,
                level_bins=64, weight_exp=6.0, lam=1.0, decode_grid=257,
                decode_cleanup_iters=3)
SELFTEST_CFG = dict(n_dim=2048, seeds=[7, 13], fpe_freq_std=2.15,
                    level_bins=64, weight_exp=6.0, lam=1.0, decode_grid=129,
                    decode_cleanup_iters=3)

# HARD-PASS / HARD-FAIL bands (see prereg for full pre-registration).
HP_B_BEATS_A_MARGIN = 0.05      # A+B_FPE skill must beat A_ALONE by >= this
HP_B_BEATS_FLOOR_MARGIN = 0.10  # A+B_FPE skill must beat RANDOM by >= this
HP_FPE_DECAY_SPEARMAN = 0.90    # |dv| vs -cos monotone decay
HP_DEGREE_INVARIANCE = 0.15     # boundary skill >= interior skill - this (both > 0)
HP_DECODE_CLEANUP_MEDREL = 0.20 # cleanup decode median rel-error must be <= this
HF_ENCODING_SPEARMAN = 0.50     # below this = ENCODING_BROKEN
HF_RAW_DECODE_MEDREL = 0.50     # raw decode above this at bundle-5 = degradation

# Machinery / ship-ability thresholds (self-test). These gate SHIP-ABILITY, NOT the
# science answer: the SYNTH positive control proves the A-vs-A+B ablation DETECTS a
# load-bearing exogenous channel when one exists, so the real-data verdict (whatever
# it is) is trustworthy. The real "does B beat A" question is the FULL science, not a
# ship gate (gating ship on it would refuse to run the very test that answers it).
HP_SYNTH_GAP = 0.30             # A+B - A on a synthetic exogenous channel A cannot predict
HP_B_ALONE_GROUNDS = 0.10       # B_ALONE (numeric only) skill must beat MEAN (==0) by this


# --------------------------------------------------------------------------- #
# Measured mammal reference data (CITED external constants).                    #
#   name, order, family, clade, body_mass(kg), head-body length(cm),           #
#   max longevity(yr), gestation(days), litter size.                           #
# Approximate reference values, CITED@AnAge/PanTHERIA/Walker's-Mammals class.   #
# Zero NaN by construction (all 5 traits present for every species).           #
# --------------------------------------------------------------------------- #
# clade codes: AFR=Afrotheria, XEN=Xenarthra, LAU=Laurasiatheria,
#              EUA=Euarchontoglires, MAR=Marsupialia.
_MAMMALS = [
    # name, order, family, clade, mass_kg, len_cm, life_yr, gest_d, litter
    ("Lion",            "Carnivora",      "Felidae",          "LAU",   190.0, 200.0, 27.0, 110.0, 3.0),
    ("Tiger",           "Carnivora",      "Felidae",          "LAU",   220.0, 250.0, 26.0, 105.0, 3.0),
    ("Domestic_cat",    "Carnivora",      "Felidae",          "LAU",     4.0,  46.0, 30.0,  65.0, 4.0),
    ("Leopard",         "Carnivora",      "Felidae",          "LAU",    60.0, 160.0, 23.0,  96.0, 3.0),
    ("Gray_wolf",       "Carnivora",      "Canidae",          "LAU",    40.0, 105.0, 16.0,  63.0, 5.0),
    ("Red_fox",         "Carnivora",      "Canidae",          "LAU",     6.0,  70.0, 14.0,  52.0, 5.0),
    ("Domestic_dog",    "Carnivora",      "Canidae",          "LAU",    30.0,  90.0, 20.0,  63.0, 6.0),
    ("Brown_bear",      "Carnivora",      "Ursidae",          "LAU",   300.0, 200.0, 33.0, 220.0, 2.0),
    ("Polar_bear",      "Carnivora",      "Ursidae",          "LAU",   450.0, 240.0, 30.0, 240.0, 2.0),
    ("Giant_panda",     "Carnivora",      "Ursidae",          "LAU",   100.0, 150.0, 30.0, 135.0, 1.0),
    ("Raccoon",         "Carnivora",      "Procyonidae",      "LAU",     6.0,  55.0, 20.0,  65.0, 4.0),
    ("Sea_otter",       "Carnivora",      "Mustelidae",       "LAU",    30.0, 120.0, 23.0, 180.0, 1.0),
    ("Spotted_hyena",   "Carnivora",      "Hyaenidae",        "LAU",    60.0, 130.0, 25.0, 110.0, 2.0),
    ("Domestic_cow",    "Artiodactyla",   "Bovidae",          "LAU",   700.0, 250.0, 22.0, 283.0, 1.0),
    ("Domestic_sheep",  "Artiodactyla",   "Bovidae",          "LAU",    70.0, 120.0, 15.0, 150.0, 2.0),
    ("Domestic_goat",   "Artiodactyla",   "Bovidae",          "LAU",    60.0, 130.0, 18.0, 150.0, 2.0),
    ("African_buffalo", "Artiodactyla",   "Bovidae",          "LAU",   600.0, 300.0, 26.0, 340.0, 1.0),
    ("Impala",          "Artiodactyla",   "Bovidae",          "LAU",    55.0, 130.0, 17.0, 200.0, 1.0),
    ("Giraffe",         "Artiodactyla",   "Giraffidae",       "LAU",   900.0, 450.0, 26.0, 450.0, 1.0),
    ("Red_deer",        "Artiodactyla",   "Cervidae",         "LAU",   200.0, 200.0, 20.0, 235.0, 1.0),
    ("Moose",           "Artiodactyla",   "Cervidae",         "LAU",   450.0, 280.0, 22.0, 231.0, 1.0),
    ("Domestic_pig",    "Artiodactyla",   "Suidae",           "LAU",   120.0, 150.0, 20.0, 115.0, 8.0),
    ("Hippopotamus",    "Artiodactyla",   "Hippopotamidae",   "LAU",  1500.0, 350.0, 50.0, 240.0, 1.0),
    ("Dromedary_camel", "Artiodactyla",   "Camelidae",        "LAU",   500.0, 300.0, 40.0, 390.0, 1.0),
    ("Bottlenose_dolphin","Cetacea",      "Delphinidae",      "LAU",   300.0, 280.0, 40.0, 365.0, 1.0),
    ("Killer_whale",    "Cetacea",        "Delphinidae",      "LAU",  4000.0, 700.0, 60.0, 517.0, 1.0),
    ("Blue_whale",      "Cetacea",        "Balaenopteridae",  "LAU",140000.0,2500.0, 90.0, 340.0, 1.0),
    ("Humpback_whale",  "Cetacea",        "Balaenopteridae",  "LAU", 30000.0,1400.0, 80.0, 350.0, 1.0),
    ("Horse",           "Perissodactyla", "Equidae",          "LAU",   500.0, 240.0, 30.0, 340.0, 1.0),
    ("Plains_zebra",    "Perissodactyla", "Equidae",          "LAU",   300.0, 230.0, 25.0, 375.0, 1.0),
    ("White_rhinoceros","Perissodactyla", "Rhinocerotidae",   "LAU",  2300.0, 400.0, 45.0, 490.0, 1.0),
    ("Little_brown_bat","Chiroptera",     "Vespertilionidae", "LAU",   0.008,   8.0, 30.0,  60.0, 1.0),
    ("Vampire_bat",     "Chiroptera",     "Phyllostomidae",   "LAU",   0.040,   9.0, 20.0, 210.0, 1.0),
    ("Flying_fox",      "Chiroptera",     "Pteropodidae",     "LAU",     1.0,  25.0, 30.0, 180.0, 1.0),
    ("European_hedgehog","Eulipotyphla",  "Erinaceidae",      "LAU",     1.0,  25.0, 10.0,  35.0, 4.0),
    ("Common_shrew",    "Eulipotyphla",   "Soricidae",        "LAU",   0.010,   7.0,  2.0,  24.0, 6.0),
    ("Human",           "Primates",       "Hominidae",        "EUA",    70.0, 170.0, 90.0, 267.0, 1.0),
    ("Chimpanzee",      "Primates",       "Hominidae",        "EUA",    50.0, 130.0, 60.0, 230.0, 1.0),
    ("Gorilla",         "Primates",       "Hominidae",        "EUA",   160.0, 170.0, 55.0, 257.0, 1.0),
    ("Orangutan",       "Primates",       "Hominidae",        "EUA",    75.0, 130.0, 60.0, 245.0, 1.0),
    ("Rhesus_macaque",  "Primates",       "Cercopithecidae",  "EUA",     8.0,  50.0, 40.0, 165.0, 1.0),
    ("Olive_baboon",    "Primates",       "Cercopithecidae",  "EUA",    25.0,  75.0, 45.0, 180.0, 1.0),
    ("Ring_tailed_lemur","Primates",      "Lemuridae",        "EUA",     2.2,  42.0, 27.0, 135.0, 1.0),
    ("House_mouse",     "Rodentia",       "Muridae",          "EUA",   0.020,   9.0,  4.0,  20.0, 6.0),
    ("Brown_rat",       "Rodentia",       "Muridae",          "EUA",   0.300,  25.0,  4.0,  22.0, 8.0),
    ("Gray_squirrel",   "Rodentia",       "Sciuridae",        "EUA",   0.500,  25.0, 12.0,  44.0, 3.0),
    ("Capybara",        "Rodentia",       "Caviidae",         "EUA",    55.0, 120.0, 12.0, 150.0, 4.0),
    ("Beaver",          "Rodentia",       "Castoridae",       "EUA",    20.0,  80.0, 24.0, 107.0, 3.0),
    ("Guinea_pig",      "Rodentia",       "Caviidae",         "EUA",     1.0,  25.0,  8.0,  68.0, 3.0),
    ("European_rabbit", "Lagomorpha",     "Leporidae",        "EUA",     2.0,  40.0, 12.0,  31.0, 6.0),
    ("European_hare",   "Lagomorpha",     "Leporidae",        "EUA",     4.0,  60.0, 12.0,  42.0, 3.0),
    ("African_elephant","Proboscidea",    "Elephantidae",     "AFR",  5000.0, 600.0, 70.0, 645.0, 1.0),
    ("Asian_elephant",  "Proboscidea",    "Elephantidae",     "AFR",  4000.0, 550.0, 65.0, 660.0, 1.0),
    ("Rock_hyrax",      "Hyracoidea",     "Procaviidae",      "AFR",     4.0,  50.0, 12.0, 240.0, 2.0),
    ("West_indian_manatee","Sirenia",     "Trichechidae",     "AFR",   500.0, 300.0, 60.0, 365.0, 1.0),
    ("Aardvark",        "Tubulidentata",  "Orycteropodidae",  "AFR",    60.0, 130.0, 23.0, 210.0, 1.0),
    ("Nine_banded_armadillo","Cingulata", "Dasypodidae",      "XEN",     5.0,  50.0, 20.0, 120.0, 4.0),
    ("Giant_anteater",  "Pilosa",         "Myrmecophagidae",  "XEN",    40.0, 120.0, 26.0, 190.0, 1.0),
    ("Three_toed_sloth","Pilosa",         "Bradypodidae",     "XEN",     4.0,  55.0, 30.0, 180.0, 1.0),
    ("Red_kangaroo",    "Diprotodontia",  "Macropodidae",     "MAR",    60.0, 130.0, 22.0,  33.0, 1.0),
    ("Koala",           "Diprotodontia",  "Phascolarctidae",  "MAR",    10.0,  75.0, 18.0,  35.0, 1.0),
    ("Common_wombat",   "Diprotodontia",  "Vombatidae",       "MAR",    30.0, 100.0, 20.0,  21.0, 1.0),
    ("Virginia_opossum","Didelphimorphia","Didelphidae",      "MAR",     3.0,  40.0,  4.0,  13.0, 8.0),
    ("Tasmanian_devil", "Dasyuromorphia", "Dasyuridae",       "MAR",     8.0,  60.0,  6.0,  21.0, 3.0),
]
_PROP_NAMES = ["mass", "length", "lifespan", "gestation", "litter"]
# Power-law-distributed size/time variables -> log10 before min-max (allometry is
# linear in log space; Kleiber's law). Litter size (range 1-8) stays linear.
_PROP_LOG = [True, True, True, True, False]


def load_mammals() -> dict:
    """Return species arrays: props [E,5], order/family/clade ids, degree + boundary mask."""
    name = [r[0] for r in _MAMMALS]
    order = [r[1] for r in _MAMMALS]
    family = [r[2] for r in _MAMMALS]
    clade = [r[3] for r in _MAMMALS]
    props = torch.tensor([[r[4], r[5], r[6], r[7], r[8]] for r in _MAMMALS], dtype=torch.float64)
    n = len(_MAMMALS)
    # graph degree = # OTHER species sharing order OR family OR clade.
    deg = torch.zeros(n, dtype=torch.float64)
    for e in range(n):
        c = 0
        for j in range(n):
            if j == e:
                continue
            if order[j] == order[e] or family[j] == family[e] or clade[j] == clade[e]:
                c += 1
        deg[e] = float(c)
    # boundary = bottom-tertile graph degree (taxonomically isolated; A has few neighbors).
    thresh = float(torch.quantile(deg, 1.0 / 3.0))
    boundary = deg <= thresh
    return dict(name=name, order=order, family=family, clade=clade,
                props=props, degree=deg, boundary=boundary, n=n)


# --------------------------------------------------------------------------- #
# Encodings                                                                    #
# --------------------------------------------------------------------------- #
def _norm_prop(col: torch.Tensor, use_log: bool) -> torch.Tensor:
    """Min-max normalize a property column to [0,1], ignoring NaN. Optional log10 first.

    log10 for power-law-distributed size/time vars (allometry linear in log space).
    """
    x = col
    if use_log:
        pos = torch.where(torch.isnan(col), torch.full_like(col, 1.0), col.clamp_min(1e-9))
        x = torch.where(torch.isnan(col), col, torch.log10(pos))
    mask = ~torch.isnan(x)
    lo = x[mask].min()
    hi = x[mask].max()
    span = (hi - lo).clamp_min(1e-12)
    out = (x - lo) / span
    return out  # NaNs stay NaN


def fpe_encode(vals: torch.Tensor, freqs: torch.Tensor) -> torch.Tensor:
    """FHRR fractional power encoding: enc[e,d] = exp(1j * freqs[d] * vals[e]). [E,D] complex64.

    vals in [0,1] (NaN -> zero vector). freqs Gaussian per-dim base frequencies.
    cos-sim(enc(v1),enc(v2)) = mean_d cos(freqs[d]*(v1-v2)) = exp(-s^2 dv^2/2) (Gaussian kernel).
    """
    E = vals.shape[0]
    D = freqs.shape[0]
    v = torch.nan_to_num(vals, nan=0.0).to(torch.float64).view(E, 1)
    phase = v * freqs.view(1, D).to(torch.float64)
    enc = torch.exp(torch.complex(torch.zeros_like(phase), phase)).to(torch.complex64)
    nan_rows = torch.isnan(vals)
    if nan_rows.any():
        enc[nan_rows] = 0.0
    return enc


def level_encode(vals: torch.Tensor, v_lo: torch.Tensor, v_hi: torch.Tensor) -> torch.Tensor:
    """Spherical-interpolation level code: normalize(cos(t)*v_lo + sin(t)*v_hi), t=v*pi/2. [E,D] float32.

    cos-sim(level(v1),level(v2)) = cos((v1-v2)*pi/2): monotone-decreasing, bundling-robust.
    """
    E = vals.shape[0]
    v = torch.nan_to_num(vals, nan=0.0).to(torch.float64)
    t = v * (math.pi / 2.0)
    out = torch.cos(t).view(E, 1) * v_lo.view(1, -1) + torch.sin(t).view(E, 1) * v_hi.view(1, -1)
    out = out / out.norm(dim=1, keepdim=True).clamp_min(1e-12)
    nan_rows = torch.isnan(vals)
    if nan_rows.any():
        out[nan_rows] = 0.0
    return out.to(torch.float32)


def _cos_sim_real(mat: torch.Tensor) -> torch.Tensor:
    """Pairwise cosine similarity matrix [E,E] (real). Accepts real or complex; complex -> real part."""
    if torch.is_complex(mat):
        norms = mat.abs().pow(2).sum(dim=1).sqrt().clamp_min(1e-12)
        m = mat / norms.view(-1, 1)
        gram = (m @ m.conj().t()).real
        return gram
    norms = mat.norm(dim=1, keepdim=True).clamp_min(1e-12)
    m = mat / norms
    return m @ m.t()


# --------------------------------------------------------------------------- #
# Channel A: REAL KGStore relational signatures                                #
# --------------------------------------------------------------------------- #
def build_relational_store(mm: dict, n_dim: int, gen: torch.Generator):
    """Ingest species->(order,family,clade) triples into a REAL KGStore; return (store, rel_sigs [E,D]).

    Exercises the REAL substrate code path (F.1): KGStore(...) with BASE/portable
    kwargs only (F.2/F.3), + ingest_triples. Species relational signature is built
    from the store's own E/R bipolar codebooks: rel[e] = sum_r R[r]*E[symbol_of(e,r)]
    (bind = elementwise multiply, bundle = sum). Shared order/family/clade -> similar.
    """
    n_sp = mm["n"]
    orders = sorted(set(mm["order"]))
    families = sorted(set(mm["family"]))
    clades = sorted(set(mm["clade"]))
    # Entity index layout: [species | order-symbols | family-symbols | clade-symbols].
    o_off = n_sp
    f_off = o_off + len(orders)
    c_off = f_off + len(families)
    n_ent = c_off + len(clades)
    n_rel = 3  # HAS_ORDER, HAS_FAMILY, HAS_CLADE
    o_idx = {o: o_off + i for i, o in enumerate(orders)}
    f_idx = {f: f_off + i for i, f in enumerate(families)}
    c_idx = {c: c_off + i for i, c in enumerate(clades)}

    # BASE/portable constructor ONLY (portable across KGStore versions per F.3).
    store = KGStore(n_ent, n_rel, n_dim, gen)

    triples = []
    for e in range(n_sp):
        triples.append((e, 0, o_idx[mm["order"][e]]))
        triples.append((e, 1, f_idx[mm["family"][e]]))
        triples.append((e, 2, c_idx[mm["clade"][e]]))
    store.ingest_triples(torch.tensor(triples, dtype=torch.long))

    E = store.E  # [n_ent, D] bipolar float32
    R = store.R  # [n_rel, D]
    rel = torch.zeros(n_sp, n_dim, dtype=torch.float32)
    for e in range(n_sp):
        rel[e] = (R[0] * E[o_idx[mm["order"][e]]]
                  + R[1] * E[f_idx[mm["family"][e]]]
                  + R[2] * E[c_idx[mm["clade"][e]]])
    return store, rel


# --------------------------------------------------------------------------- #
# kNN readout in a consolidated geometry                                       #
# --------------------------------------------------------------------------- #
def _predict_loo(sim: torch.Tensor, target_raw: torch.Tensor, known: torch.Tensor,
                 weight_exp: float) -> torch.Tensor:
    """Leave-one-out similarity-weighted prediction of target_raw for every known species.

    sim [E,E] similarity; target_raw [E] (raw units); known [E] bool mask (has target).
    Returns preds [E] (NaN for unknown). No leakage: a species never weights itself.
    """
    E = sim.shape[0]
    preds = torch.full((E,), float("nan"), dtype=torch.float64)
    idx_known = torch.nonzero(known, as_tuple=False).view(-1).tolist()
    for e in idx_known:
        w = sim[e].clone().to(torch.float64)
        w = torch.clamp(w, min=0.0)
        w[e] = 0.0                       # never use self
        w[~known] = 0.0                  # only neighbors with known target
        w = w.pow(weight_exp)
        wsum = w.sum()
        if wsum <= 1e-12:
            preds[e] = target_raw[known].to(torch.float64).mean()
        else:
            preds[e] = (w * torch.nan_to_num(target_raw.to(torch.float64), nan=0.0)).sum() / wsum
    return preds


def _skill(preds: torch.Tensor, target_raw: torch.Tensor, known: torch.Tensor,
           subset: torch.Tensor | None = None) -> float:
    """R^2-style skill vs the mean baseline over the known (optionally subset) species.

    skill = 1 - SS_res/SS_tot; SS_tot from the mean of the known targets. >0 = beats mean.
    Predictions and targets scored in the SAME (log or linear) space used for encoding.
    """
    m = known.clone()
    if subset is not None:
        m = m & subset
    idx = torch.nonzero(m, as_tuple=False).view(-1)
    if idx.numel() < 3:
        return float("nan")
    y = target_raw[idx].to(torch.float64)
    yhat = preds[idx].to(torch.float64)
    valid = ~torch.isnan(yhat)
    if valid.sum() < 3:
        return float("nan")
    y = y[valid]
    yhat = yhat[valid]
    ss_tot = ((y - y.mean()) ** 2).sum()
    ss_res = ((y - yhat) ** 2).sum()
    if ss_tot <= 1e-12:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def _spearman(a: torch.Tensor, b: torch.Tensor) -> float:
    """Spearman rank correlation (numpy/scipy-free): Pearson of ranks."""
    def rank(x):
        order = torch.argsort(x)
        r = torch.zeros_like(x, dtype=torch.float64)
        r[order] = torch.arange(x.numel(), dtype=torch.float64)
        return r
    ra, rb = rank(a.to(torch.float64)), rank(b.to(torch.float64))
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = (ra.norm() * rb.norm()).clamp_min(1e-12)
    return float((ra * rb).sum() / denom)


# --------------------------------------------------------------------------- #
# FPE distance-decay + decode diagnostics (encoding integrity)                 #
# --------------------------------------------------------------------------- #
def fpe_distance_decay_spearman(freqs_1d: torch.Tensor) -> float:
    """Spearman(|dv|, -cos): does FPE similarity decay monotonically with numeric distance?"""
    grid = torch.linspace(0.0, 1.0, 41, dtype=torch.float64)
    enc = fpe_encode(grid, freqs_1d)              # [41, D]
    sim = _cos_sim_real(enc)                       # [41,41]
    dv = (grid.view(-1, 1) - grid.view(1, -1)).abs()
    iu = torch.triu_indices(grid.numel(), grid.numel(), offset=1)
    dvs = dv[iu[0], iu[1]]
    coss = sim[iu[0], iu[1]]
    return _spearman(dvs, -coss)


def decode_diagnostics(mm: dict, freqs: torch.Tensor, roles: torch.Tensor,
                       grid_n: int, cleanup_iters: int) -> dict:
    """Bundle all 5 FPE-encoded properties per species; decode each RAW vs CLEANUP (resonator).

    Returns median relative decode error (normalized units) for raw and cleanup. This
    distinguishes DECODE_DEGRADATION (raw high, cleanup low) from a real grounding negative.
    """
    n_sp = mm["n"]
    n_dim = freqs.shape[1]
    nprops = len(_PROP_NAMES)
    norm_cols = [_norm_prop(mm["props"][:, k], _PROP_LOG[k]) for k in range(nprops)]
    grid = torch.linspace(0.0, 1.0, grid_n, dtype=torch.float64)
    grid_codes = [fpe_encode(grid, freqs[k]) for k in range(nprops)]  # each [grid_n, D]

    raw_errs, cleanup_errs = [], []
    n_last = 0
    for e in range(n_sp):
        vals = torch.tensor([norm_cols[k][e] for k in range(nprops)], dtype=torch.float64)
        present = [k for k in range(nprops) if not torch.isnan(vals[k])]
        n_last = len(present)
        if len(present) < 2:
            continue
        # Bundle: B = sum_k role_k (*) enc_k(v_k), unit-magnitude FPE bound to role.
        bundle = torch.zeros(n_dim, dtype=torch.complex64)
        for k in present:
            enc_k = fpe_encode(vals[k:k + 1], freqs[k]).view(-1)  # [D]
            bundle = bundle + roles[k] * enc_k

        def decode_slot(residual, k):
            unbound = residual * roles[k].conj()
            scores = (grid_codes[k].conj() * unbound.view(1, -1)).sum(dim=1).real
            gi = int(torch.argmax(scores))
            return grid[gi], gi

        # RAW: single unbind + nearest-grid, no interference removal.
        for k in present:
            dec, _ = decode_slot(bundle, k)
            raw_errs.append(abs(float(dec) - float(vals[k])))

        # CLEANUP: resonator-style iterative interference subtraction (CSim add-on).
        est = {}
        for k in present:
            _, gi = decode_slot(bundle, k)
            est[k] = gi
        for _ in range(cleanup_iters):
            for k in present:
                resid = bundle.clone()
                for m in present:
                    if m == k:
                        continue
                    resid = resid - roles[m] * grid_codes[m][est[m]]
                _, gi = decode_slot(resid, k)
                est[k] = gi
        for k in present:
            cleanup_errs.append(abs(float(grid[est[k]]) - float(vals[k])))

    med = lambda xs: float(torch.tensor(xs, dtype=torch.float64).median()) if xs else float("nan")
    return dict(raw_median_rel_err=med(raw_errs), cleanup_median_rel_err=med(cleanup_errs),
                n_decoded=n_last, bundle_size=len(_PROP_NAMES))


# --------------------------------------------------------------------------- #
# One seed                                                                     #
# --------------------------------------------------------------------------- #
def run_seed(mm: dict, cfg: dict, seed: int) -> dict:
    """Run all arms for one seed. Returns per-arm skill (overall + strata) + diagnostics + preds."""
    n_dim = cfg["n_dim"]
    gen = torch.Generator(device="cpu").manual_seed(seed)
    n_sp = mm["n"]
    nprops = len(_PROP_NAMES)

    # Channel A (REAL KGStore).
    store, rel_sig = build_relational_store(mm, n_dim, gen)
    n_triples = len(store)

    # Random per-property base frequencies (Gaussian) + level endpoints + roles (complex phase).
    freqs = torch.randn(nprops, n_dim, generator=gen, dtype=torch.float32) * cfg["fpe_freq_std"]
    v_lo = (torch.randn(n_dim, generator=gen, dtype=torch.float32))
    v_hi = (torch.randn(n_dim, generator=gen, dtype=torch.float32))
    role_phase = (torch.rand(nprops, n_dim, generator=gen, dtype=torch.float32) * 2 - 1) * math.pi
    roles = torch.exp(torch.complex(torch.zeros_like(role_phase), role_phase)).to(torch.complex64)
    rand_sig = torch.randn(n_sp, n_dim, generator=gen, dtype=torch.float32)

    norm_cols = [_norm_prop(mm["props"][:, k], _PROP_LOG[k]) for k in range(nprops)]
    known = [~torch.isnan(norm_cols[k]) for k in range(nprops)]

    # Relational similarity (Channel A).
    sim_rel = _cos_sim_real(rel_sig)
    sim_rel_n = sim_rel / sim_rel.abs().max().clamp_min(1e-12)
    sim_rand = _cos_sim_real(rand_sig)

    # DEGREE baseline: query-agnostic weighting by graph degree (same-order/family/clade).
    deg = mm["degree"].to(torch.float64)
    sim_deg = deg.view(1, -1).repeat(n_sp, 1)  # every row identical -> query-agnostic

    # Per-target attribute encodings (exclude the target from the bundle -> no leakage).
    per_arm = {a: {} for a in ARMS}
    preds_cat = {a: [] for a in ARMS}
    sim_fpe_by_t = {}                 # per-target normalized FPE similarity (for lam sweep)
    n_units = 0

    for t in range(nprops):
        others = [k for k in range(nprops) if k != t]
        # FPE attribute vector = bundle_{k!=t} role_k (*) FPE_k(v_k).
        attr_fpe = torch.zeros(n_sp, n_dim, dtype=torch.complex64)
        attr_lvl = torch.zeros(n_sp, n_dim, dtype=torch.float32)
        raw_feat = torch.zeros(n_sp, len(others), dtype=torch.float64)
        for j, k in enumerate(others):
            attr_fpe = attr_fpe + roles[k] * fpe_encode(norm_cols[k], freqs[k])
            attr_lvl = attr_lvl + level_encode(norm_cols[k], v_lo, v_hi)
            raw_feat[:, j] = torch.nan_to_num(norm_cols[k], nan=0.0)
        sim_fpe = _cos_sim_real(attr_fpe)
        sim_lvl = _cos_sim_real(attr_lvl)
        sim_fpe_n = sim_fpe / sim_fpe.abs().max().clamp_min(1e-12)
        sim_fpe_by_t[t] = sim_fpe_n
        # RAW_FEATURE_KNN: kNN on the RAW normalized OTHER features (informative reference).
        d2 = torch.cdist(raw_feat, raw_feat) ** 2
        sim_raw = torch.exp(-d2)

        fused_fpe = sim_rel_n + cfg["lam"] * sim_fpe_n
        fused_lvl = sim_rel_n + cfg["lam"] * (sim_lvl / sim_lvl.abs().max().clamp_min(1e-12))

        # Score in the SAME (log/linear) space the encoding uses -> use normalized target.
        target_scored = norm_cols[t]
        kn = known[t]

        arm_sims = {
            RANDOM: sim_rand,
            A_ALONE: sim_rel_n,
            B_ALONE: sim_fpe_n,
            A_PLUS_B_FPE: fused_fpe,
            A_PLUS_B_LEVEL: fused_lvl,
            RAW_FEATURE_KNN: sim_raw,
            DEGREE: sim_deg,
        }
        for a, sim in arm_sims.items():
            preds = _predict_loo(sim, target_scored, kn, cfg["weight_exp"])
            per_arm[a][t] = preds
            preds_cat[a].append(preds[kn])
        # MEAN baseline.
        mean_pred = torch.full((n_sp,), float("nan"), dtype=torch.float64)
        mean_pred[kn] = target_scored[kn].to(torch.float64).mean()
        per_arm[MEAN][t] = mean_pred
        preds_cat[MEAN].append(mean_pred[kn])
        n_units += int(kn.sum())

    # --- SYNTHETIC EXOGENOUS POSITIVE CONTROL (machinery proof) ---
    # An exogenous scalar assigned INDEPENDENTLY of order/family/clade. Channel A
    # (relational) cannot predict it; the FPE numeric channel can. If A+B beats A
    # here, the ablation DETECTS a load-bearing exogenous channel -> the real-data
    # verdict (redundant or not) is trustworthy. This is the ship-ability gate.
    perm = torch.randperm(n_sp, generator=gen).to(torch.float64)
    x_synth = perm / float(n_sp - 1)                 # exogenous, relational-independent, in [0,1]
    all_known = torch.ones(n_sp, dtype=torch.bool)
    attr_synth = roles[0] * fpe_encode(x_synth, freqs[0])
    sim_synth = _cos_sim_real(attr_synth)
    sim_synth_n = sim_synth / sim_synth.abs().max().clamp_min(1e-12)
    p_synth_a = _predict_loo(sim_rel_n, x_synth, all_known, cfg["weight_exp"])
    p_synth_ab = _predict_loo(sim_rel_n + cfg["lam"] * sim_synth_n, x_synth, all_known, cfg["weight_exp"])
    skill_synth_a = _skill(p_synth_a, x_synth, all_known)
    skill_synth_ab = _skill(p_synth_ab, x_synth, all_known)
    synth_gap = skill_synth_ab - skill_synth_a

    # Aggregate skill per arm (overall + strata) + per-property breakdown (weak-point loc).
    interior = ~mm["boundary"]
    boundary = mm["boundary"]
    arm_skill, arm_skill_int, arm_skill_bnd = {}, {}, {}
    per_prop_skill = {A_ALONE: [], B_ALONE: [], A_PLUS_B_FPE: []}
    for a in ARMS:
        sk, ski, skb = [], [], []
        for t in range(nprops):
            kn = known[t]
            s_t = _skill(per_arm[a][t], norm_cols[t], kn)
            sk.append(s_t)
            ski.append(_skill(per_arm[a][t], norm_cols[t], kn, subset=interior))
            skb.append(_skill(per_arm[a][t], norm_cols[t], kn, subset=boundary))
            if a in per_prop_skill:
                per_prop_skill[a].append(s_t)
        arm_skill[a] = float(torch.tensor(sk, dtype=torch.float64).nanmean())
        arm_skill_int[a] = float(torch.tensor(ski, dtype=torch.float64).nanmean())
        arm_skill_bnd[a] = float(torch.tensor(skb, dtype=torch.float64).nanmean())

    # lam-fusion sweep (does B ADD over A under ANY reasonable weight, not just lam=1.0?).
    # Reporting-only diagnostic; headline verdict stays at cfg["lam"] for periodic-comparability.
    lam_grid = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
    lam_sweep = {}
    for lam in lam_grid:
        sk = []
        for t in range(nprops):
            kn = known[t]
            sim_fused = sim_rel_n + lam * sim_fpe_by_t[t]
            preds = _predict_loo(sim_fused, norm_cols[t], kn, cfg["weight_exp"])
            sk.append(_skill(preds, norm_cols[t], kn))
        lam_sweep[lam] = float(torch.tensor(sk, dtype=torch.float64).nanmean())
    best_lam = max(lam_grid, key=lambda L: lam_sweep[L])
    ab_best_lam = lam_sweep[best_lam]

    # Encoding integrity diagnostics.
    decay_spearman = fpe_distance_decay_spearman(freqs[0])
    decode = decode_diagnostics(mm, freqs, roles, cfg["decode_grid"], cfg["decode_cleanup_iters"])

    # ARMS-MUST-DIFFER (META_RULE_AF): per-arm concatenated prediction vectors.
    import hashlib
    digests = {}
    for a in ARMS:
        cat = torch.cat(preds_cat[a]).to(torch.float64)
        digests[a] = hashlib.sha256(torch.nan_to_num(cat, nan=-999.0).numpy().tobytes()).hexdigest()

    return dict(seed=seed, n_dim=n_dim, n_triples=n_triples, n_units=n_units,
                arm_skill=arm_skill, arm_skill_interior=arm_skill_int,
                arm_skill_boundary=arm_skill_bnd, fpe_decay_spearman=decay_spearman,
                decode=decode, arm_digests=digests, per_prop_skill=per_prop_skill,
                lam_sweep={str(k): v for k, v in lam_sweep.items()},
                best_lam=best_lam, ab_best_lam=ab_best_lam,
                synth_skill_a=skill_synth_a, synth_skill_ab=skill_synth_ab, synth_gap=synth_gap)


# --------------------------------------------------------------------------- #
# I/O helpers (start-marker / atomic metrics / crash diagnostic)              #
# --------------------------------------------------------------------------- #
def _out_dir() -> str:
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    return os.path.join("data", "exp_" + name)


def _write_start_marker(out_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(out_dir: str, metrics: dict) -> None:
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: str, exc: Exception) -> None:
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(out_dir, diag)


# --------------------------------------------------------------------------- #
# Verdict logic                                                                #
# --------------------------------------------------------------------------- #
def _agg(seed_results: list, path: str):
    """Mean over seeds of a nested path like 'arm_skill.A_PLUS_B_FPE'."""
    keys = path.split(".")
    vals = []
    for r in seed_results:
        v = r
        for k in keys:
            v = v[k]
        vals.append(v)
    return float(torch.tensor(vals, dtype=torch.float64).nanmean())


def decide_verdict(seed_results: list) -> dict:
    a_alone = _agg(seed_results, "arm_skill." + A_ALONE)
    b_alone = _agg(seed_results, "arm_skill." + B_ALONE)
    ab_fpe = _agg(seed_results, "arm_skill." + A_PLUS_B_FPE)
    ab_lvl = _agg(seed_results, "arm_skill." + A_PLUS_B_LEVEL)
    rand = _agg(seed_results, "arm_skill." + RANDOM)
    mean_arm = _agg(seed_results, "arm_skill." + MEAN)
    degree = _agg(seed_results, "arm_skill." + DEGREE)
    raw_knn = _agg(seed_results, "arm_skill." + RAW_FEATURE_KNN)
    decay = _agg(seed_results, "fpe_decay_spearman")
    raw_dec = _agg(seed_results, "decode.raw_median_rel_err")
    clean_dec = _agg(seed_results, "decode.cleanup_median_rel_err")
    int_fpe = _agg(seed_results, "arm_skill_interior." + A_PLUS_B_FPE)
    bnd_fpe = _agg(seed_results, "arm_skill_boundary." + A_PLUS_B_FPE)
    synth_gap = _agg(seed_results, "synth_gap")
    synth_a = _agg(seed_results, "synth_skill_a")
    synth_ab = _agg(seed_results, "synth_skill_ab")
    ab_best_lam = _agg(seed_results, "ab_best_lam")     # best A+B over lam grid (diagnostic)
    # per-property mean skill (weak-point localization).
    nprops = len(_PROP_NAMES)
    pp = {}
    for arm in (A_ALONE, B_ALONE, A_PLUS_B_FPE):
        pp[arm] = [float(torch.tensor([r["per_prop_skill"][arm][t] for r in seed_results],
                                      dtype=torch.float64).nanmean()) for t in range(nprops)]
    # does B add for ANY single property (even if the 5-property mean is redundant)?
    per_prop_b_adds = [i for i in range(nprops)
                       if (pp[A_PLUS_B_FPE][i] - pp[A_ALONE][i]) >= HP_B_BEATS_A_MARGIN]

    # --- Ship-ability / machinery gates (provable Phase-1 claims) ---
    machinery_ok = synth_gap >= HP_SYNTH_GAP           # ablation detects load-bearing exogenous B
    b_grounds = (b_alone - mean_arm) >= HP_B_ALONE_GROUNDS  # FPE numeric channel carries real info
    encoding_ok = decay >= HP_FPE_DECAY_SPEARMAN
    encoding_broken = decay < HF_ENCODING_SPEARMAN
    decode_degraded = raw_dec > HF_RAW_DECODE_MEDREL
    cleanup_fixes = clean_dec <= HP_DECODE_CLEANUP_MEDREL

    # --- Science headline: is B LOAD-BEARING OVER the native relational channel A ---
    b_beats_a = (ab_fpe - a_alone) >= HP_B_BEATS_A_MARGIN
    b_beats_floor = (ab_fpe - max(rand, 0.0)) >= HP_B_BEATS_FLOOR_MARGIN and ab_fpe > 0.0
    degree_invariant = (bnd_fpe >= int_fpe - HP_DEGREE_INVARIANCE) and (bnd_fpe > 0.0)
    oracle_leak = (int_fpe > 0.0) and (bnd_fpe <= 0.0)

    decode_note = "decode_ok"
    if decode_degraded and cleanup_fixes:
        decode_note = "DECODE_DEGRADATION_NEEDS_CLEANUP_cleanup_recovers"
    elif decode_degraded and not cleanup_fixes:
        decode_note = "DECODE_DEGRADATION_cleanup_insufficient"

    # Failure-mode classification (do NOT conflate the distinct causes).
    failure_mode = "GROUNDING_ADDS"
    if encoding_broken:
        failure_mode = "ENCODING_BROKEN"
    elif not machinery_ok:
        failure_mode = "ABLATION_MACHINERY_INSENSITIVE"
    elif not b_grounds:
        failure_mode = "GROUNDING_NEGATIVE_B_CARRIES_NOTHING"
    elif oracle_leak:
        failure_mode = "ORACLE_LEAK_VIA_SMOOTHNESS"
    elif not b_beats_a:
        # B carries real info + machinery works but B is REDUNDANT with A on THIS domain.
        failure_mode = "GROUNDING_REDUNDANT_WITH_RELATIONAL"
    # else: B beats A on an A-independent domain -> GROUNDING_ADDS (the value-add).

    # HARD_PASS = B is load-bearing OVER A (strong grounding). Requires machinery/
    # encoding/decode valid first, else the comparison is not trustworthy.
    hard_pass = (machinery_ok and encoding_ok and cleanup_fixes and b_grounds
                 and b_beats_a and b_beats_floor and degree_invariant and (ab_fpe > mean_arm))

    if hard_pass:
        verdict = "HARD_PASS"
    elif failure_mode in ("ENCODING_BROKEN", "ABLATION_MACHINERY_INSENSITIVE",
                          "GROUNDING_NEGATIVE_B_CARRIES_NOTHING", "ORACLE_LEAK_VIA_SMOOTHNESS"):
        verdict = "HARD_FAIL"
    else:
        # GROUNDING_REDUNDANT (B grounds but not over A) = pre-registered MIDDLE_BAND.
        verdict = "MIDDLE_BAND"

    msg = ("%s | [science] A+B_FPE=%.3f A_alone=%.3f (d=%+.3f) B_alone=%.3f A+B_lvl=%.3f "
           "RAW_KNN=%.3f RANDOM=%.3f DEGREE=%.3f MEAN=%.3f "
           "| [machinery] synth A=%.3f A+B=%.3f gap=%.3f | [encoding] decay=%.3f "
           "decode raw=%.3f clean=%.3f (%s) | interior_fpe=%.3f boundary_fpe=%.3f "
           "| [diag] A+B_best_lam=%.3f B_adds_props=%s "
           "| failure_mode=%s"
           % (verdict, ab_fpe, a_alone, ab_fpe - a_alone, b_alone, ab_lvl, raw_knn, rand,
              degree, mean_arm, synth_a, synth_ab, synth_gap, decay, raw_dec, clean_dec,
              decode_note, int_fpe, bnd_fpe, ab_best_lam,
              [_PROP_NAMES[i] for i in per_prop_b_adds], failure_mode))
    return dict(verdict=verdict, verdict_msg=msg, failure_mode=failure_mode, decode_note=decode_note,
                b_beats_a=bool(b_beats_a), b_beats_floor=bool(b_beats_floor),
                machinery_ok=bool(machinery_ok), b_grounds=bool(b_grounds),
                encoding_ok=bool(encoding_ok), degree_invariant=bool(degree_invariant),
                cleanup_fixes=bool(cleanup_fixes),
                per_prop_skill={k: list(v) for k, v in pp.items()},
                per_prop_b_adds=[_PROP_NAMES[i] for i in per_prop_b_adds],
                agg=dict(a_alone=a_alone, b_alone=b_alone, ab_fpe=ab_fpe, ab_lvl=ab_lvl,
                         raw_knn=raw_knn, rand=rand, degree=degree, mean=mean_arm,
                         synth_a=synth_a, synth_ab=synth_ab, synth_gap=synth_gap,
                         ab_best_lam=ab_best_lam,
                         fpe_decay_spearman=decay, raw_decode=raw_dec, cleanup_decode=clean_dec,
                         interior_fpe=int_fpe, boundary_fpe=bnd_fpe))


# --------------------------------------------------------------------------- #
# Validity preflight (F.1-F.4 ENFORCE + original 4)                            #
# --------------------------------------------------------------------------- #
def _validity_checks(mm: dict, cfg: dict) -> None:
    """Run the mandated validity-preflight declarations at self-test scale. Raises under enforce."""
    # F.1 / F.2 / F.3: construct + ingest the REAL KGStore at tiny scale.
    exercised = set()
    gsmall = torch.Generator(device="cpu").manual_seed(1)
    store_small = KGStore(6, 2, 16, gsmall)         # BASE/portable kwargs only
    exercised.add("KGStore")
    store_small.ingest_triples(torch.tensor([[0, 0, 4], [1, 1, 5], [2, 0, 4]], dtype=torch.long))
    assert len(store_small) == 3, "ingest_triples did not register triples"
    exercised.add("ingest_triples")

    # Discriminator-preview: run the REAL mechanism on the REAL data (2 seeds).
    seed_results = [run_seed(mm, cfg, s) for s in cfg["seeds"]]
    dv = decide_verdict(seed_results)
    agg = dv["agg"]

    # metric-moves: FPE similarity must MOVE with input (dv=0 vs dv=0.5).
    freqs = torch.randn(1, cfg["n_dim"], generator=torch.Generator().manual_seed(3),
                        dtype=torch.float32) * cfg["fpe_freq_std"]
    enc0 = fpe_encode(torch.tensor([0.0], dtype=torch.float64), freqs[0])
    enc_same = fpe_encode(torch.tensor([0.0], dtype=torch.float64), freqs[0])
    enc_half = fpe_encode(torch.tensor([0.5], dtype=torch.float64), freqs[0])
    cos_same = float((enc0.view(-1) * enc_same.view(-1).conj()).sum().real / cfg["n_dim"])
    cos_half = float((enc0.view(-1) * enc_half.view(-1).conj()).sum().real / cfg["n_dim"])

    # negative-control margin: RANDOM arm skill across seeds must fail "b_beats_a" bar with margin.
    rand_scores = [r["arm_skill"][RANDOM] for r in seed_results]

    # ARMS-MUST-DIFFER exercised at self-test (fail-closed gate).
    d0 = seed_results[0]["arm_digests"]
    pairs = [(x, y) for i, x in enumerate(ARMS) for y in ARMS[i + 1:]]
    arms_differ = all(d0[x] != d0[y] for x, y in pairs)
    assert arms_differ, "META_RULE_AF: two arms produced bit-identical predictions"
    # cardinality exercised at self-test.
    norm_cols = [_norm_prop(mm["props"][:, k], _PROP_LOG[k]) for k in range(len(_PROP_NAMES))]
    expected_units = len(cfg["seeds"]) * sum(int((~torch.isnan(norm_cols[k])).sum())
                                             for k in range(len(_PROP_NAMES)))
    got_units = sum(r["n_units"] for r in seed_results)
    cardinality_ok = (got_units == expected_units)
    assert cardinality_ok, "cardinality breach: got %d expected %d" % (got_units, expected_units)

    run_validity_preflight([
        # F.1: real substrate code path exercised (ENFORCE).
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "ingest_triples"],
         "exercised_entrypoints": sorted(exercised)},
        # F.2/F.3: KGStore call binds the live signature with BASE kwargs (ENFORCE).
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None}},
        # F.4: A_ALONE (the ablation baseline) must be ABOVE the RANDOM floor, so the
        # A-vs-A+B comparison is against a genuine non-floor baseline (not a structural 0).
        {"kind": "guard_baseline_valid", "baseline_score": agg["a_alone"],
         "floor_score": max(agg["rand"], 0.0), "guard_name": "ablation_needs_nonfloor_A",
         "baseline_name": "A_ALONE", "floor_name": "RANDOM", "eps": 0.02},
        # POSITIVE control = the SYNTHETIC exogenous channel machinery. A+B MUST beat A
        # when a genuinely load-bearing exogenous channel is injected -> proves the
        # ablation can detect load-bearing B, so the real-data verdict is trustworthy.
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": agg["synth_gap"] >= HP_SYNTH_GAP,
         "control_name": "SYNTH_exogenous(A+B beats A)", "headline_name": "synth_ablation_gap"},
        {"kind": "metric_moves", "metric_name": "fpe_similarity",
         "before": cos_half, "after": cos_same},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "cardinality"],
         "exercised_gates": ["arms_differ", "cardinality"]},
        # negative control = RANDOM similarity must fail the "grounds above mean" bar.
        {"kind": "negative_control_margin", "control_scores": rand_scores,
         "headline_threshold": HP_B_ALONE_GROUNDS, "higher_is_pass": True, "margin": 0.0,
         "n_repeats_min": 2, "control_name": "RANDOM_similarity"},
    ], run_mode="selftest")

    # Discriminator-fires: the MACHINERY must fire (synth) + the FPE numeric channel must
    # carry real exogenous info (B_alone > MEAN). We do NOT gate ship on the real-data
    # "B beats A" -- that IS the FULL science question this cell exists to answer.
    assert agg["synth_gap"] >= HP_SYNTH_GAP, (
        "ABLATION MACHINERY DID NOT FIRE: synth A+B-A gap=%.3f < %.3f; the test cannot "
        "detect a load-bearing exogenous channel; do NOT ship." % (agg["synth_gap"], HP_SYNTH_GAP))
    assert (agg["b_alone"] - agg["mean"]) >= HP_B_ALONE_GROUNDS, (
        "FPE numeric channel does not ground: B_alone=%.3f <= MEAN+%.3f; wiring carries no "
        "exogenous info; do NOT ship." % (agg["b_alone"], HP_B_ALONE_GROUNDS))
    assert agg["a_alone"] > 0.05, "baseline A_ALONE below band (%.3f); regime too hard" % agg["a_alone"]
    assert agg["a_alone"] < 0.95, "baseline A_ALONE saturated (%.3f); no headroom" % agg["a_alone"]
    print("[self-test] validity + machinery + wiring PASS: %s" % dv["verdict_msg"], flush=True)


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="fast validity + discriminator preview")
    ap.add_argument("--smoke", action="store_true", help="reduced-grid run")
    args, _ = ap.parse_known_args()

    mm = load_mammals()

    if args.self_test:
        _validity_checks(mm, dict(SELFTEST_CFG))
        print("SELFTEST_PASS", flush=True)
        return

    cfg = dict(SELFTEST_CFG) if args.smoke else dict(FULL_CFG)
    run_mode = "smoke" if args.smoke else "full"
    out_dir = _out_dir()
    norm_cols = [_norm_prop(mm["props"][:, k], _PROP_LOG[k]) for k in range(len(_PROP_NAMES))]
    expected_units = len(cfg["seeds"]) * sum(int((~torch.isnan(norm_cols[k])).sum())
                                             for k in range(len(_PROP_NAMES)))
    _write_start_marker(out_dir, run_mode, expected_units)

    t0 = time.perf_counter()
    seed_results = []
    for s in cfg["seeds"]:
        rs = run_seed(mm, cfg, s)
        seed_results.append(rs)
        print("[progress] seed=%d done A+B_FPE=%.3f A_alone=%.3f decay=%.3f elapsed=%.1fs"
              % (s, rs["arm_skill"][A_PLUS_B_FPE], rs["arm_skill"][A_ALONE],
                 rs["fpe_decay_spearman"], time.perf_counter() - t0), flush=True)

    dv = decide_verdict(seed_results)
    elapsed = time.perf_counter() - t0

    got_units = sum(r["n_units"] for r in seed_results)
    cardinality_ok = (got_units == expected_units)
    verdict = dv["verdict"]
    verdict_msg = dv["verdict_msg"]
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = "cardinality breach: got %d expected %d | %s" % (got_units, expected_units, verdict_msg)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg,
        summary=("%s A+B_FPE=%.3f vs A_alone=%.3f decode=%s"
                 % (verdict, dv["agg"]["ab_fpe"], dv["agg"]["a_alone"], dv["decode_note"])),
        elapsed_s=round(elapsed, 3), run_mode=run_mode, anchor_name=ANCHOR_NAME,
        n_dim=cfg["n_dim"], n_seeds=len(cfg["seeds"]), expected_n_units=expected_units,
        got_n_units=got_units, cardinality_ok=cardinality_ok,
        failure_mode=dv["failure_mode"], decode_note=dv["decode_note"],
        agg=dv["agg"], gates=dict(b_beats_a=dv["b_beats_a"], b_beats_floor=dv["b_beats_floor"],
                                  encoding_ok=dv["encoding_ok"], degree_invariant=dv["degree_invariant"],
                                  cleanup_fixes=dv["cleanup_fixes"]),
        prop_names=_PROP_NAMES,
        per_prop_skill=dv["per_prop_skill"], per_prop_b_adds=dv["per_prop_b_adds"],
        per_seed=[dict(seed=r["seed"], n_triples=r["n_triples"], n_units=r["n_units"],
                       arm_skill=r["arm_skill"], arm_skill_interior=r["arm_skill_interior"],
                       arm_skill_boundary=r["arm_skill_boundary"],
                       fpe_decay_spearman=r["fpe_decay_spearman"], decode=r["decode"],
                       per_prop_skill=r["per_prop_skill"], lam_sweep=r["lam_sweep"],
                       best_lam=r["best_lam"], ab_best_lam=r["ab_best_lam"])
                  for r in seed_results],
        ts_iso=datetime.now(timezone.utc).isoformat(), host=platform.node(),
    )
    _write_metrics(out_dir, metrics)
    print("[done] %s" % verdict_msg, flush=True)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
