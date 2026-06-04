"""
Kenya Fiscal Intelligence — Data Pipeline
Fetches fiscal indicators from:
  - IMF DataMapper API: debt (% GDP), revenue, expenditure, fiscal balance
  - World Bank REST API v2: external debt stocks, debt service, ODA, GDP
Covers Kenya and EAC peers (UG, TZ, ET, RW) for 2000-2024.
"""

import requests
import pandas as pd
import time
from pathlib import Path

# ─── Country mappings ────────────────────────────────────────────────────────
COUNTRIES_WB  = ['KE', 'UG', 'TZ', 'ET', 'RW']   # ISO-2 for WB
COUNTRIES_IMF = ['KEN', 'UGA', 'TZA', 'ETH', 'RWA']  # ISO-3 for IMF

ISO3_TO_ISO2 = {
    'KEN': 'KE', 'UGA': 'UG', 'TZA': 'TZ', 'ETH': 'ET', 'RWA': 'RW',
}

COUNTRY_NAMES = {
    'KE': 'Kenya', 'UG': 'Uganda', 'TZ': 'Tanzania',
    'ET': 'Ethiopia', 'RW': 'Rwanda',
}

YEAR_RANGE = range(2000, 2025)

# ─── IMF DataMapper indicators ────────────────────────────────────────────────
IMF_INDICATORS = {
    'GGXWDG_GDP':        'Gross govt debt (% GDP)',
    'GGR_G01_GDP_PT':    'Revenue (% GDP)',
    'GGX_GDP':           'Expenditure (% GDP)',
    'GGXCNL_G01_GDP_PT': 'Fiscal balance (% GDP)',
}

# ─── World Bank REST API v2 indicators ───────────────────────────────────────
WB_INDICATORS = {
    'GC.XPN.INTP.ZS':    'Interest payments (% expense)',
    'DT.DOD.DECT.CD':    'External debt stocks (USD)',
    'DT.DOD.DECT.GN.ZS': 'External debt (% GNI)',
    'DT.TDS.DECT.GN.ZS': 'Total debt service (% GNI)',
    'DT.ODA.ALLD.CD':    'Net ODA received (USD)',
    'NY.GDP.MKTP.CD':    'GDP (USD)',
}

IMF_BASE = 'https://www.imf.org/external/datamapper/api/v1'
WB_BASE  = 'https://api.worldbank.org/v2'


# ─── Fetch helpers ────────────────────────────────────────────────────────────

def fetch_imf_indicator(code: str, countries: list, retries: int = 3, timeout: int = 30) -> pd.DataFrame:
    """Fetch one IMF DataMapper indicator for multiple countries (ISO-3)."""
    country_str = ','.join(countries)
    url = f'{IMF_BASE}/{code}/{country_str}'
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            values = data.get('values', {}).get(code, {})
            rows = []
            for iso3, yearly in values.items():
                iso2 = ISO3_TO_ISO2.get(iso3)
                if iso2 is None:
                    continue
                for yr_str, val in yearly.items():
                    try:
                        yr = int(yr_str)
                    except ValueError:
                        continue
                    if yr not in YEAR_RANGE:
                        continue
                    rows.append({'economy': iso2, 'year': yr, code: val})
            return pd.DataFrame(rows)
        except requests.exceptions.Timeout:
            print(f"    IMF timeout attempt {attempt+1}/{retries} for {code}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"    IMF error attempt {attempt+1}/{retries} for {code}: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return pd.DataFrame()


def fetch_wb_indicator(code: str, countries: list, date_range: str = '2000:2024',
                       per_page: int = 500, retries: int = 3, timeout: int = 60) -> pd.DataFrame:
    """Fetch one WB indicator for multiple ISO-2 countries via REST API v2."""
    country_str = ';'.join(countries)
    url = (f'{WB_BASE}/country/{country_str}/indicator/{code}'
           f'?format=json&per_page={per_page}&date={date_range}')
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            if len(data) < 2 or not data[1]:
                return pd.DataFrame()
            records = list(data[1])
            # Pagination
            for page in range(2, data[0].get('pages', 1) + 1):
                r2 = requests.get(url + f'&page={page}', timeout=timeout)
                r2.raise_for_status()
                d2 = r2.json()
                if len(d2) > 1 and d2[1]:
                    records.extend(d2[1])
            rows = []
            for rec in records:
                iso3 = rec.get('countryiso3code', '')
                iso2 = ISO3_TO_ISO2.get(iso3)
                if iso2 is None:
                    continue
                try:
                    yr = int(rec.get('date', 0))
                except ValueError:
                    continue
                if yr not in YEAR_RANGE:
                    continue
                rows.append({'economy': iso2, 'year': yr, code: rec.get('value')})
            return pd.DataFrame(rows)
        except requests.exceptions.Timeout:
            print(f"    WB timeout attempt {attempt+1}/{retries} for {code}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"    WB error attempt {attempt+1}/{retries} for {code}: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return pd.DataFrame()


# ─── Main fetch ───────────────────────────────────────────────────────────────

def fetch_all():
    Path('data/processed').mkdir(parents=True, exist_ok=True)

    # Scaffold: all (economy, year) combinations
    scaffold = pd.DataFrame(
        [(c, y) for c in COUNTRIES_WB for y in YEAR_RANGE],
        columns=['economy', 'year']
    )

    print("\n--- IMF indicators ---")
    for code, label in IMF_INDICATORS.items():
        print(f"  Fetching {code} — {label}...", end=' ', flush=True)
        df = fetch_imf_indicator(code, COUNTRIES_IMF)
        if df.empty:
            print("EMPTY / FAILED")
            continue
        df = df.rename(columns={code: label})
        n = df[label].notna().sum()
        print(f"OK ({n} non-null across all countries)")
        scaffold = scaffold.merge(df[['economy', 'year', label]], on=['economy', 'year'], how='left')

    print("\n--- World Bank indicators ---")
    for code, label in WB_INDICATORS.items():
        print(f"  Fetching {code} — {label}...", end=' ', flush=True)
        df = fetch_wb_indicator(code, COUNTRIES_WB)
        if df.empty:
            print("EMPTY / FAILED")
            continue
        df = df.rename(columns={code: label})
        n = df[label].notna().sum()
        print(f"OK ({n} non-null across all countries)")
        scaffold = scaffold.merge(df[['economy', 'year', label]], on=['economy', 'year'], how='left')

    result = scaffold.copy()
    result['country'] = result['economy'].map(COUNTRY_NAMES)
    result = result.sort_values(['economy', 'year']).reset_index(drop=True)

    # Derived columns
    if 'External debt stocks (USD)' in result.columns:
        result['External debt stocks (USD bn)'] = result['External debt stocks (USD)'] / 1e9
    if 'GDP (USD)' in result.columns:
        result['GDP (USD bn)'] = result['GDP (USD)'] / 1e9
    if 'Net ODA received (USD)' in result.columns:
        result['Net ODA received (USD bn)'] = result['Net ODA received (USD)'] / 1e9
    if 'Expenditure (% GDP)' in result.columns and 'Revenue (% GDP)' in result.columns:
        result['Fiscal gap (% GDP)'] = result['Expenditure (% GDP)'] - result['Revenue (% GDP)']

    out_path = 'data/processed/fiscal.parquet'
    result.to_parquet(out_path, index=False)

    # ─── Summary ─────────────────────────────────────────────────────────────
    ke = result[result['economy'] == 'KE']
    all_indicator_cols = (list(IMF_INDICATORS.values()) + list(WB_INDICATORS.values())
                          + ['Fiscal gap (% GDP)', 'External debt stocks (USD bn)'])

    print(f"\n{'='*70}")
    print(f"Saved {len(result)} rows to {out_path}")
    print(f"Countries : {sorted(result['economy'].unique().tolist())}")
    print(f"Years     : {int(result['year'].min())} – {int(result['year'].max())}")
    print(f"\nKenya coverage per indicator:")
    for col in all_indicator_cols:
        if col in ke.columns:
            yrs = sorted(ke[ke[col].notna()]['year'].tolist())
            n = len(yrs)
            yr_str = f"{yrs[0]}–{yrs[-1]}" if yrs else "none"
            print(f"  {col:<50} {n:>3} years  ({yr_str})")
    print(f"{'='*70}")
    return result


if __name__ == '__main__':
    print("Fetching fiscal indicators (IMF + World Bank)...")
    print(f"Countries: {COUNTRIES_WB}")
    fetch_all()
