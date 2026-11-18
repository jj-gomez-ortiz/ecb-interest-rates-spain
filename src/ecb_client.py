"""Collect ECB series through the SDMX API and build a monthly dataset for Spain.

Usage
-----
>>> from src.ecb_client import build_dataset
>>> df = build_dataset()          # downloads the latest data from the ECB
"""

import time

import pandas as pd
import requests
import sdmx

# name : (dataflow, series key)
SERIES = {
    "ecb_rate":         ("FM",   "B.U2.EUR.4F.KR.DFR.LEV"),           # ECB deposit facility rate
    "euribor_12m":      ("FM",   "M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA"),  # 12-month Euribor
    "mortgage_rate_es": ("MIR",  "M.ES.B.A2C.AM.R.A.2250.EUR.N"),     # Spain, new house-purchase loans
    "inflation_es":     ("HICP", "M.ES.N.000000.4D0.ANR"),            # Spain, HICP annual rate of change
}

# Series that only have a value on the days they change (ECB policy decisions)
EVENT_SERIES = {"ecb_rate"}


class ECBClient(sdmx.Client):
    """sdmx.Client for the ECB that retries on temporary server errors (5xx)."""

    def __init__(self, retries=5, wait=10, **kwargs):
        super().__init__("ECB", **kwargs)
        self.retries, self.wait = retries, wait

    def get(self, *args, **kwargs):
        """Same as sdmx.Client.get, with automatic retries on 5xx errors.
        """
        for attempt in range(1, self.retries + 1):
            try:
                return super().get(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                if status is not None and status >= 500 and attempt < self.retries:
                    time.sleep(self.wait * attempt)      # 10 s, 20 s, 30 s...
                else:
                    raise


def download(client, dataflow, key, start="2008-01"):
    """Download one series and return it as a pandas Series indexed by date only."""
    message = client.data(dataflow, key=key, params={"startPeriod": start})
    series = sdmx.to_pandas(message)
    # sdmx1 returns a MultiIndex (country, currency...); keep only the time dimension
    return series.droplevel([n for n in series.index.names if n != "TIME_PERIOD"])


def to_monthly(series, event_based=False):
    """Convert a series to a monthly PeriodIndex.

    Event-based series (e.g. the ECB rate, which only has a value on decision days)
    are carried forward day by day and the value in force at month end is kept.
    """
    series = series.copy()
    series.index = pd.to_datetime(series.index)
    if event_based:
        days = pd.date_range(series.index[0], pd.Timestamp.today(), freq="D")
        series = series.reindex(days).ffill().resample("ME").last()
    series.index = series.index.to_period("M")
    return series


def monthly_payment(annual_rate, amount=150_000, years=25):
    """Fixed monthly payment of a loan (French amortisation). Negative rates count as 0 %."""
    r = max(annual_rate, 0) / 100 / 12
    n = years * 12
    return amount / n if r == 0 else amount * r / (1 - (1 + r) ** -n)


def build_dataset(start="2014-01", spread=1.0, client=None):
    """Download all series and return the monthly DataFrame (up to the last complete month)."""
    client = client or ECBClient()
    raw = {name: download(client, flow, key) for name, (flow, key) in SERIES.items()}
    df = pd.concat({name: to_monthly(s, event_based=name in EVENT_SERIES)
                    for name, s in raw.items()}, axis=1)
    last_complete_month = pd.Timestamp.today().to_period("M") - 1
    df = df.loc[start:last_complete_month]
    df.index.name = "month"
    df["payment_150k"] = (df["euribor_12m"] + spread).apply(monthly_payment).round(0)
    return df
