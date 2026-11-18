# Finding and reading ECB series keys (SDMX)

The ECB Data Portal follows the **SDMX** standard. Every series is identified by a **dataflow** and a **key**.

## 1. Concepts

| Concept | What it is | Example |
|---|---|---|
| Dataflow | A table of related series | `FM` financial markets, `MIR` bank interest rates, `HICP` consumer prices |
| Dimension | A field that describes a series | frequency, reference area, currency... |
| Key | One code per dimension, joined by dots | `M.ES.B.A2C.AM.R.A.2250.EUR.N` |

## 2. Workflow

```python
import sdmx
ecb = sdmx.Client("ECB")

# 1. Catalogue: list all dataflows
catalogue = sdmx.to_pandas(ecb.dataflow().dataflow)

# 2. Structure: which dimensions make up a key
structure = ecb.dataflow("MIR", params={"references": "all"}).dataflow["MIR"].structure
[d.id for d in structure.dimensions.components]

# 3. Data: download one series
msg = ecb.data("MIR", key="M.ES.B.A2C.AM.R.A.2250.EUR.N", params={"startPeriod": "2014-01"})
series = sdmx.to_pandas(msg)
```

The ECB portal's search (https://data.ecb.europa.eu/) is useful to find candidate keys; the structure confirms what each code means.

## 3. Keys used in this project

### `FM` — `FREQ . REF_AREA . CURRENCY . PROVIDER_FM . INSTRUMENT_FM . PROVIDER_FM_ID . DATA_TYPE_FM`

| Key | Decoded |
|---|---|
| `B.U2.EUR.4F.KR.DFR.LEV` | Daily (business week) · euro area · EUR · ECB · key interest rate · deposit facility, dates of changes · level |
| `M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA` | Monthly · euro area · EUR · Refinitiv · money market · Euribor 1-year · historical close, average of observations through period |

### `MIR` — `FREQ . REF_AREA . BS_REP_SECTOR . BS_ITEM . MATURITY_NOT_IRATE . DATA_TYPE_MIR . AMOUNT_CAT . BS_COUNT_SECTOR . CURRENCY_TRANS . IR_BUS_COV`

| Key | Decoded |
|---|---|
| `M.ES.B.A2C.AM.R.A.2250.EUR.N` | Monthly · Spain · deposit-taking corporations · lending for house purchase · total (volume-weighted) maturity · annualised agreed rate · all amounts · households and NPISH · EUR · new business |

### `HICP` — `FREQ . REF_AREA . ADJUSTMENT . ICP_ITEM . DATA_PROVIDER . ICP_SUFFIX`

| Key | Decoded |
|---|---|
| `M.ES.N.000000.4D0.ANR` | Monthly · Spain · not seasonally adjusted · HICP total · Eurostat · annual rate of change |

## 4. Adapting the project

- **Another euro-area country:** change `ES` in the `MIR` and `HICP` keys (e.g. `DE`, `FR`, `IT`).
- **Another frequency:** change the first code (`M` monthly, `Q` quarterly), after checking it exists in the structure.
