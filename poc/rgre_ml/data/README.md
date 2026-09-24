# Real datasets for RGRE-ML-2

Six small tabular regression datasets, processed by `poc/rgre_ml/prep_data.py`
from public copies reachable over plain HTTPS (the UCI and OpenML hosts were
not reachable from the run environment). Each file is `x0..x{d-1}, y` with a
header naming the columns; rows with a missing value and categorical columns
are dropped, nothing else is changed.

| file | rows | features | target | origin |
|---|---|---|---|---|
| `diabetes.csv` | 442 | 10 | disease progression after one year | Efron et al. 2004, the copy shipped with scikit-learn |
| `mpg.csv` | 392 | 6 | miles per gallon | UCI Auto MPG, the seaborn-data copy |
| `concrete.csv` | 1030 | 8 | compressive strength (MPa) | UCI Concrete Compressive Strength (Yeh 1998) |
| `winered.csv` | 1599 | 11 | quality score | UCI Wine Quality, red (Cortez et al. 2009) |
| `abalone.csv` | 4177 | 7 | rings | UCI Abalone, sex column dropped |
| `california.csv` | 3000 | 8 | median house value | California Housing (Pace and Barry 1997), 3000 rows drawn with seed 2026 |

The UCI datasets are CC BY 4.0; the others are public-domain research data.
