"""Re-teach the attachment validities under the CURRENT decode with the re-keyed (dual-route) typed-plausibility assets, into a
SEPARATE file (A/B against the live asset). usage: python experiments/_reteach_validities_v2dr.py [extra builder args]"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
AA.BF_TSP_ASSET = os.path.join(REPO, "data", "frontend_assets", "typed_selectional_preference_bf_v2dr.json")
AA.BF_TSP_SUBJ_ASSET = os.path.join(REPO, "data", "frontend_assets", "typed_selectional_preference_bf_subj_v2dr.json")
from tools.build_attachment_validities import main
out = os.path.join(REPO, "data", "frontend_assets", "attachment_validities_reteach_v2dr.json")
sys.exit(main(["--out", out, "--eval"] + sys.argv[1:]))
