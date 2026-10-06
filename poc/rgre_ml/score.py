"""Score RGRE-ML-1 by its frozen bars. Written and committed before the fresh seeds ran."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from poc.rgre_ml.run import summarise
from poc.rgre_ml.dictionary import CLASSES


def main(paths):
    recs, per_seed = [], {}
    for p in paths:
        d = json.load(open(p)); recs += d["cases"]; per_seed[d["seed"]] = d["summary"]
    S = summarise(recs)
    known = [r for r in recs if r["kind"] in ("isolated", "two")]
    oov = [r for r in recs if r["kind"] == "oov"]
    n_cand = float(np.median([len(CLASSES) - len(r["missing"]) - 1 for r in recs]))  # rough candidate count
    print(f"{len(recs)} cases pooled from seeds {sorted(per_seed)}\n")
    rows = []
    b1 = S["q_perp_value_auc"]; rows.append(("B1 abstention AUC (field)", ">= 0.90", f"{b1:.3f}", b1 >= 0.90))
    b2 = S["two_step_recovery_field"]; rows.append(("B2 two-step recovery (field)", ">= 0.85", f"{b2:.3f}", b2 >= 0.85))
    b3 = S["identity_value"] > S["identity_nogate"] and S["q_perp_value_auc"] > S["q_perp_auc"]
    rows.append(("B3 field beats consumer", "identity and AUC both higher",
                 f"identity {S['identity_value']:.2f} vs {S['identity_nogate']:.2f}; AUC {S['q_perp_value_auc']:.2f} vs {S['q_perp_auc']:.2f}", b3))
    means = {k: float(np.mean([r["value"][k] for r in known])) for k in ("rgre_value", "random", "cheapest", "gradnorm", "mp_value")}
    b4 = S["value_rgre_value"] >= 0.90 and all(S["value_rgre_value"] >= S[f"value_{b}"] and means["rgre_value"] >= means[b]
                                               for b in ("random", "cheapest", "gradnorm"))
    rows.append(("B4 selection value (field = MP)", ">= 0.90 and above baselines",
                 f"median {S['value_rgre_value']:.2f} mean {means['rgre_value']:.2f} | random {S['value_random']:.2f}/{means['random']:.2f} cheapest {S['value_cheapest']:.2f}/{means['cheapest']:.2f} gradnorm {S['value_gradnorm']:.2f}/{means['gradnorm']:.2f}", b4))
    b5 = S["oov_abstain"] >= 0.80 and S["known_false_abstain"] <= 0.10
    rows.append(("B5 tau transfers (predicted fail)", "oov >= 80%, known <= 10%", f"{100*S['oov_abstain']:.0f}%, {100*S['known_false_abstain']:.0f}%", b5))
    b6 = S["ctrl_declined_or_abstained"] >= 0.75
    rows.append(("B6 controls decline", ">= 75%", f"{100*S['ctrl_declined_or_abstained']:.0f}%", b6))
    b7 = S["defer_oov_orthg_wins"] >= 0.60
    rows.append(("B7 orthogonal deferral (predicted fail)", ">= 60% of oov cases", f"{100*S['defer_oov_orthg_wins']:.0f}%", b7))
    b8 = S["search_fraction"] <= 1 / 3
    rows.append(("B8 search fraction", "<= 1/3", f"{S['search_fraction']:.2f}", b8))
    print("| bar | target | result | |\n|---|---|---|---|")
    for name, tgt, res, ok in rows:
        print(f"| {name} | {tgt} | {res} | {'pass' if ok else 'FAIL'} |")
    letter = {(True, True): "A", (True, False): "B", (False, True): "C", (False, False): "D"}[(b1 >= 0.90, b2 >= 0.85)]
    print(f"\nOutcome by the frozen tree (B1 x B2): **{letter}**")
    print("\nper seed:")
    for sd, s in sorted(per_seed.items()):
        print(f"  seed {sd}: AUC field {s['q_perp_value_auc']:.2f} consumer {s['q_perp_auc']:.2f} | two-step field {s['two_step_recovery_field']:.2f} consumer {s['two_step_recovery_consumer']:.2f} | identity field {s['identity_value']:.2f} consumer {s['identity_nogate']:.2f} | value field {s['value_rgre_value']:.2f}")
    print("\nother reported quantities:")
    for k in ("value_rgre", "value_rgre_notabstained", "identity", "oracle_identity", "two_step_found_field",
              "q_perp_known", "q_perp_oov", "defer_oov_mag", "defer_oov_orth_global", "defer_oov_random",
              "defer_iso_orthg_wins", "ctrl_abstain"):
        print(f"  {k:<26} {S[k]:.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
