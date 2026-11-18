# Data

## `ecb_spain_monthly.csv`

Monthly dataset built by [`notebooks/ecb_interest_rates_spain.ipynb`](../notebooks/ecb_interest_rates_spain.ipynb). One row per month, from January 2014 to the last complete month at the time of the run (October 2026 in this version).

| Column | Type | Unit | Source (dataflow · key) | Description |
|---|---|---|---|---|
| `month` | period | YYYY-MM | — | Month (index) |
| `ecb_rate` | float | % | `FM` · `B.U2.EUR.4F.KR.DFR.LEV` | ECB deposit facility rate in force at month end |
| `euribor_12m` | float | % | `FM` · `M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA` | 12-month Euribor, monthly average |
| `mortgage_rate_es` | float | % | `MIR` · `M.ES.B.A2C.AM.R.A.2250.EUR.N` | Annualised agreed rate on new loans for house purchase to households, Spain |
| `inflation_es` | float | % | `HICP` · `M.ES.N.000000.4D0.ANR` | HICP all items, annual rate of change, Spain |
| `payment_150k` | float | € | calculated | Monthly payment of a €150,000, 25-year loan at `euribor_12m` + 1 % (floored at 0 %) |

**Missing values:** the latest month of `mortgage_rate_es` can be empty, because bank interest-rate statistics are published 1–2 months after market data. It is not imputed.

**Source:** European Central Bank, [ECB Data Portal](https://data.ecb.europa.eu/). Re-running the notebook overwrites this file with the latest data.
