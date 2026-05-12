from __future__ import annotations

import json
import os
from datetime import date
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


def _read_url(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as response:
        return response.read()


def _json_get(url: str) -> Any:
    return json.loads(_read_url(url).decode("utf-8"))


def requested_close_from_today(today: date) -> str:
    d = today
    while d.weekday() >= 5:
        d = d.fromordinal(d.toordinal() - 1)
    return d.isoformat()


def _select_history_row(rows: list[dict[str, Any]], requested_close_date: str | None = None) -> dict[str, Any]:
    if not rows:
        raise RuntimeError("No usable history rows were available")
    rows = sorted(rows, key=lambda row: row["date"])
    selected = rows[-1]
    if requested_close_date:
        eligible = [row for row in rows if row["date"] <= requested_close_date]
        if eligible:
            selected = eligible[-1]
    return selected


def _normalize_row(row: dict[str, Any], *, source: str, currency: str = "USD") -> dict[str, Any]:
    close = row.get("close")
    if close is None:
        raise RuntimeError(f"Missing close in {source} row")
    return {
        "date": str(row.get("date") or row.get("datetime") or row.get("label") or "")[:10],
        "open": _safe_float(row.get("open")),
        "high": _safe_float(row.get("high")),
        "low": _safe_float(row.get("low")),
        "close": float(close),
        "volume": row.get("volume"),
        "currency": row.get("currency") or currency or "USD",
        "source": source,
    }


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_yahoo_history(
    symbol: str,
    *,
    requested_close_date: str | None = None,
    range_period: str = "6mo",
    interval: str = "1d",
) -> dict[str, Any]:
    encoded = quote(symbol, safe="")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?interval={interval}&range={range_period}&includePrePost=false&events=div%2Csplits"
    )
    payload = _json_get(url)
    result = payload.get("chart", {}).get("result", [])
    if not result:
        raise RuntimeError(f"No Yahoo chart result for symbol: {symbol}")

    block = result[0]
    timestamps = block.get("timestamp") or []
    quote_block = (block.get("indicators", {}).get("quote") or [{}])[0]
    closes = quote_block.get("close") or []
    opens = quote_block.get("open") or []
    highs = quote_block.get("high") or []
    lows = quote_block.get("low") or []
    volumes = quote_block.get("volume") or []
    currency = block.get("meta", {}).get("currency") or "USD"

    rows: list[dict[str, Any]] = []
    for idx, ts in enumerate(timestamps):
        if idx >= len(closes):
            continue
        close_value = closes[idx]
        if close_value is None:
            continue
        row_date = date.fromtimestamp(ts).isoformat()
        rows.append(
            {
                "date": row_date,
                "open": opens[idx] if idx < len(opens) else None,
                "high": highs[idx] if idx < len(highs) else None,
                "low": lows[idx] if idx < len(lows) else None,
                "close": float(close_value),
                "volume": volumes[idx] if idx < len(volumes) else None,
                "currency": currency,
                "source": "yahoo_chart",
            }
        )

    if not rows:
        raise RuntimeError(f"No usable Yahoo history rows for symbol: {symbol}")

    selected = _select_history_row(rows, requested_close_date)
    return {
        "symbol": symbol,
        "selected": selected,
        "rows": sorted(rows, key=lambda row: row["date"]),
        "currency": currency,
        "source": "yahoo_chart",
        "range": range_period,
        "interval": interval,
    }


def fetch_yahoo_close(symbol: str, requested_close_date: str | None = None) -> dict[str, Any]:
    history = fetch_yahoo_history(symbol, requested_close_date=requested_close_date, range_period="3mo", interval="1d")
    selected = history["selected"]
    return {
        "symbol": symbol,
        "date": selected["date"],
        "open": selected["open"],
        "high": selected["high"],
        "low": selected["low"],
        "close": float(selected["close"]),
        "currency": selected["currency"],
        "source": history["source"],
        "provider_rank": 1,
    }


def fetch_twelve_data_history(symbol: str, *, requested_close_date: str | None = None, outputsize: int = 140) -> dict[str, Any]:
    api_key = os.getenv("TWELVE_DATA_API_KEY") or os.getenv("TWELVEDATA_API_KEY")
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY not configured")
    params = urlencode({"symbol": symbol, "interval": "1day", "outputsize": outputsize, "apikey": api_key, "format": "JSON"})
    payload = _json_get(f"https://api.twelvedata.com/time_series?{params}")
    if payload.get("status") == "error":
        raise RuntimeError(str(payload.get("message") or f"Twelve Data error for {symbol}"))
    rows: list[dict[str, Any]] = []
    for item in payload.get("values") or []:
        if item.get("close") is None:
            continue
        rows.append(
            {
                "date": str(item.get("datetime"))[:10],
                "open": _safe_float(item.get("open")),
                "high": _safe_float(item.get("high")),
                "low": _safe_float(item.get("low")),
                "close": float(item.get("close")),
                "volume": item.get("volume"),
                "currency": "USD",
                "source": "twelve_data_time_series",
            }
        )
    if not rows:
        raise RuntimeError(f"No usable Twelve Data rows for symbol: {symbol}")
    rows = sorted(rows, key=lambda row: row["date"])
    selected = _select_history_row(rows, requested_close_date)
    return {"symbol": symbol, "selected": selected, "rows": rows, "currency": selected.get("currency") or "USD", "source": "twelve_data_time_series"}


def fetch_fmp_history(symbol: str, *, requested_close_date: str | None = None, timeseries: int = 160) -> dict[str, Any]:
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise RuntimeError("FMP_API_KEY not configured")
    encoded = quote(symbol, safe="")
    payload = _json_get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{encoded}?timeseries={timeseries}&apikey={api_key}")
    rows: list[dict[str, Any]] = []
    for item in payload.get("historical") or []:
        if item.get("close") is None:
            continue
        rows.append(
            {
                "date": str(item.get("date"))[:10],
                "open": _safe_float(item.get("open")),
                "high": _safe_float(item.get("high")),
                "low": _safe_float(item.get("low")),
                "close": float(item.get("close")),
                "volume": item.get("volume"),
                "currency": "USD",
                "source": "fmp_historical_price_full",
            }
        )
    if not rows:
        raise RuntimeError(f"No usable FMP rows for symbol: {symbol}")
    rows = sorted(rows, key=lambda row: row["date"])
    selected = _select_history_row(rows, requested_close_date)
    return {"symbol": symbol, "selected": selected, "rows": rows, "currency": selected.get("currency") or "USD", "source": "fmp_historical_price_full"}


def fetch_alpha_vantage_history(symbol: str, *, requested_close_date: str | None = None) -> dict[str, Any]:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY") or os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY not configured")
    params = urlencode({"function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": symbol, "outputsize": "compact", "apikey": api_key})
    payload = _json_get(f"https://www.alphavantage.co/query?{params}")
    series = payload.get("Time Series (Daily)") or {}
    if not series:
        message = payload.get("Note") or payload.get("Information") or payload.get("Error Message") or f"No Alpha Vantage rows for {symbol}"
        raise RuntimeError(str(message))
    rows: list[dict[str, Any]] = []
    for row_date, item in series.items():
        close = item.get("5. adjusted close") or item.get("4. close")
        if close is None:
            continue
        rows.append(
            {
                "date": str(row_date)[:10],
                "open": _safe_float(item.get("1. open")),
                "high": _safe_float(item.get("2. high")),
                "low": _safe_float(item.get("3. low")),
                "close": float(close),
                "volume": item.get("6. volume") or item.get("5. volume"),
                "currency": "USD",
                "source": "alpha_vantage_daily_adjusted",
            }
        )
    if not rows:
        raise RuntimeError(f"No usable Alpha Vantage rows for symbol: {symbol}")
    rows = sorted(rows, key=lambda row: row["date"])
    selected = _select_history_row(rows, requested_close_date)
    return {"symbol": symbol, "selected": selected, "rows": rows, "currency": selected.get("currency") or "USD", "source": "alpha_vantage_daily_adjusted"}


def fetch_layered_history(symbol: str, *, requested_close_date: str | None = None, range_period: str = "1y") -> dict[str, Any]:
    """ETF-style layered close discovery for index proxies/benchmarks.

    Provider order is intentionally explicit and persisted by callers:
    Yahoo → Twelve Data → FMP → Alpha Vantage. Missing provider keys are
    recorded as skipped attempts by the raised messages and do not stop fallback.
    """
    attempts: list[dict[str, Any]] = []
    providers = [
        ("yahoo_chart", lambda: fetch_yahoo_history(symbol, requested_close_date=requested_close_date, range_period=range_period, interval="1d")),
        ("twelve_data_time_series", lambda: fetch_twelve_data_history(symbol, requested_close_date=requested_close_date)),
        ("fmp_historical_price_full", lambda: fetch_fmp_history(symbol, requested_close_date=requested_close_date)),
        ("alpha_vantage_daily_adjusted", lambda: fetch_alpha_vantage_history(symbol, requested_close_date=requested_close_date)),
    ]
    for rank, (provider, fn) in enumerate(providers, start=1):
        try:
            result = fn()
            selected = result["selected"]
            result["source"] = result.get("source") or provider
            result["provider_rank"] = rank
            result["attempts"] = attempts + [{"provider": provider, "status": "ok", "selected_date": selected.get("date")}]
            return result
        except Exception as exc:  # noqa: BLE001
            attempts.append({"provider": provider, "status": "failed", "error": str(exc)[:240]})
    raise RuntimeError(f"Layered close discovery failed for {symbol}: {attempts}")


def fetch_layered_close(symbol: str, requested_close_date: str | None = None) -> dict[str, Any]:
    history = fetch_layered_history(symbol, requested_close_date=requested_close_date, range_period="1y")
    selected = history["selected"]
    return {
        "symbol": symbol,
        "date": selected["date"],
        "open": selected.get("open"),
        "high": selected.get("high"),
        "low": selected.get("low"),
        "close": float(selected["close"]),
        "currency": selected.get("currency") or history.get("currency") or "USD",
        "source": history.get("source"),
        "provider_rank": history.get("provider_rank"),
        "attempts": history.get("attempts", []),
        "rows": history.get("rows", []),
    }


def fetch_ecb_usd_per_eur(requested_close_date: str | None = None) -> dict[str, Any]:
    xml_bytes = _read_url("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml")
    root = ET.fromstring(xml_bytes)
    ns = {"gesmes": "http://www.gesmes.org/xml/2002-08-01", "def": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}

    observations: list[dict[str, Any]] = []
    for cube in root.findall(".//def:Cube[@time]", ns):
        obs_date = cube.attrib.get("time")
        if not obs_date:
            continue
        usd_rate = None
        for child in cube.findall("def:Cube", ns):
            if child.attrib.get("currency") == "USD":
                usd_rate = child.attrib.get("rate")
                break
        if usd_rate is not None:
            observations.append({"date": obs_date, "usd_per_eur": float(usd_rate)})

    if not observations:
        raise RuntimeError("ECB EUR/USD reference data was not available")

    observations = sorted(observations, key=lambda row: row["date"])
    selected = observations[-1]
    if requested_close_date:
        eligible = [row for row in observations if row["date"] <= requested_close_date]
        if eligible:
            selected = eligible[-1]

        requested = date.fromisoformat(requested_close_date)
        selected_date = date.fromisoformat(selected["date"])
        max_lag_days = 7
        if (requested - selected_date).days > max_lag_days:
            raise RuntimeError(
                "ECB EUR/USD reference data is stale for requested close date: "
                f"requested_close_date={requested_close_date} fx_date={selected['date']} max_lag_days={max_lag_days}"
            )

    return {
        "date": selected["date"],
        "usd_per_eur": float(selected["usd_per_eur"]),
        "source": "ecb_reference",
    }
