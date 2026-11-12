"""Turn the raw downloads into the six small CSVs the real-data experiment reads.

Each output is `x0..x{d-1},y` with a header naming the original columns. Rows with a missing
value are dropped; categorical columns are dropped; California is subsampled to 3000 rows with a
fixed seed because the full 20640 would make the oracle the slow part of the run. Run once, from
the raw files in a scratch directory; the outputs are committed so the run is reproducible without
network access. Sources are in data/README.md.
"""
from __future__ import annotations
import csv, gzip, sys
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent / "data"


def write(name, X, y, feats, target):
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(list(feats) + [target])
        for xr, yy in zip(X, y):
            w.writerow([f"{v:.6g}" for v in xr] + [f"{yy:.6g}"])
    print(f"{name:<11} n={len(y):<5} d={X.shape[1]}  features={list(feats)} target={target}")


def read_csv(path, skip_header=True):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    return (rows[0], rows[1:]) if skip_header else (None, rows)


def numeric(rows, cols):
    keep, out = [], []
    for r in rows:
        try:
            out.append([float(r[c]) for c in cols]); keep.append(True)
        except ValueError:
            keep.append(False)
    return np.array(out, float), np.array(keep)


def main(raw):
    raw = Path(raw)
    # diabetes: sklearn's raw copy (10 features, space separated, no header) and the target file
    with gzip.open(raw / "diabetes_raw.csv.gz", "rt") as f:
        X = np.array([[float(v) for v in ln.split()] for ln in f if ln.strip()])
    with gzip.open(raw / "diabetes_target.csv.gz", "rt") as f:
        y = np.array([float(ln) for ln in f if ln.strip()])
    write("diabetes", X, y, ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"], "progression")

    # auto mpg: six numeric features, rows with a missing horsepower dropped
    hdr, rows = read_csv(raw / "mpg.csv")
    cols = [hdr.index(c) for c in ["cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year"]]
    A, keep = numeric(rows, cols + [hdr.index("mpg")])
    write("mpg", A[:, :-1], A[:, -1], ["cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year"], "mpg")

    # concrete compressive strength: eight features, last column the target
    hdr, rows = read_csv(raw / "concrete.csv")
    A, keep = numeric(rows, list(range(9)))
    write("concrete", A[:, :8], A[:, 8], ["cement", "slag", "flyash", "water", "superplast", "coarse", "fine", "age"], "strength")

    # red wine quality: eleven features, target quality
    hdr, rows = read_csv(raw / "winered.csv")
    A, keep = numeric(rows, list(range(12)))
    feats = [h.strip().replace(" ", "_") for h in hdr[:11]]
    write("winered", A[:, :11], A[:, 11], feats, "quality")

    # abalone: sex dropped, seven numeric features, target rings
    _, rows = read_csv(raw / "abalone.csv", skip_header=False)
    A, keep = numeric(rows, list(range(1, 9)))
    write("abalone", A[:, :7], A[:, 7], ["length", "diameter", "height", "whole", "shucked", "viscera", "shell"], "rings")

    # california housing: eight numeric features, rows with a missing total_bedrooms dropped,
    # 3000 rows drawn with a fixed seed
    hdr, rows = read_csv(raw / "california.csv")
    cols = [hdr.index(c) for c in ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
                                   "population", "households", "median_income", "median_house_value"]]
    A, keep = numeric(rows, cols)
    rng = np.random.default_rng(2026)
    pick = rng.permutation(len(A))[:3000]
    A = A[np.sort(pick)]
    write("california", A[:, :8], A[:, 8], ["longitude", "latitude", "age", "rooms", "bedrooms", "population",
                                            "households", "income"], "value")


if __name__ == "__main__":
    main(sys.argv[1])
