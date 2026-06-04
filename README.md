# ðŸ›ï¸ Kenya Fiscal Intelligence: Government Debt, Revenue & Fiscal Sustainability Dashboard

**Kenya Fiscal Intelligence** is a production-grade fiscal analytics dashboard that fetches 10 macroeconomic indicators for 5 East African countries spanning 2000â€“2024 from two authoritative open APIs â€” the IMF DataMapper API for gross government debt, revenue, expenditure, and fiscal balance as percentages of GDP, and the World Bank REST API v2 for external debt stocks, external debt as a percentage of GNI, total debt service, interest payments as a percentage of government expenditure, net ODA received, and nominal GDP â€” merges all indicators into a single 125-row Parquet dataset via pyarrow, and surfaces the complete picture across 8 interactive Plotly charts organised into 4 Streamlit dashboard tabs with 5 hero KPI cards, a live-computed executive summary banner, event annotations marking the 2008 Global Financial Crisis, the 2014 Eurobond Era, the 2020 COVID-19 Shock, and the 2023 IMF Program, an IMF 60% debt-to-GDP sustainability benchmark reference line, EAC peer comparison controls, and a full Excel export â€” revealing that Kenya's gross government debt reached 67.3% of GDP in 2024, exceeding the IMF's sustainability benchmark while interest payments claim an increasing share of government expenditure, signalling a fiscal trap that constrains investment in public services.

| Metric | Value |
|--------|-------|
| Rows in dataset | 125 (5 countries Ã— 25 years, 2000â€“2024) |
| Countries covered | Kenya, Uganda, Tanzania, Ethiopia, Rwanda |
| Indicators tracked | 10 (4 IMF fiscal aggregates + 6 World Bank debt/external indicators) |
| Dashboard tabs | 4 (Debt Trajectory Â· Revenue & Expenditure Â· Peer Comparison Â· Export Data) |
| Interactive charts | 8 Plotly visualisations |
| Hero KPI cards | 5 (Debt/GDP Â· Fiscal Balance Â· Revenue Â· External Debt Â· Debt Service) |
| Lines of code | 1,036 |
| Cost to run | $0 â€” all open APIs, no paid keys required |
| Headline finding | Kenya's gross govt debt reached 67.3% of GDP in 2024, breaching the IMF 60% benchmark |

---

## ðŸŽ¯ Project Goal

Kenya's public finances have been under sustained pressure since the 2014 Eurobond issuance. Gross government debt as a share of GDP has grown continuously, fiscal deficits have persisted for over a decade, and interest payments now claim a structurally significant share of government expenditure â€” crowding out spending on health, education, and infrastructure. These dynamics matter not just for Kenya's domestic fiscal policy but for sovereign credit rating assessments, IMF program conditions, development finance institution lending decisions, and EAC regional economic integration analysis. Yet publicly available dashboards that visualise Kenya's fiscal position â€” with proper IMF benchmark reference lines, EAC peer comparison, and multiple debt sustainability indicators in one place â€” are almost non-existent.

Kenya Fiscal Intelligence builds the full analytical picture at zero cost using two open, authoritative data sources. The IMF DataMapper API, which powers the IMF's own public WEO visualisation tools, provides directly comparable fiscal aggregates (gross debt, revenue, expenditure, fiscal balance â€” all as percentages of GDP) for Kenya and its EAC peers across 25 years. The World Bank REST API v2 provides complementary external debt metrics that the IMF does not publish at this granularity: external debt stocks in USD, external debt as a percentage of GNI, total debt service, and interest payments as a share of government expenditure. Combining both sources in a single merged dataset surfaces the complete debt sustainability picture â€” the kind of cross-indicator analysis that a sovereign debt analyst at a DFI or a country economist at the IMF would produce for an Article IV consultation.

---

## ðŸ§¬ System Architecture

1. **Data Ingestion â€” IMF DataMapper API:** `data_pipeline.py` fetches four fiscal aggregate indicators (gross government debt, revenue, expenditure, and fiscal balance â€” all expressed as percentages of GDP) from the IMF's World Economic Outlook DataMapper API at `https://www.imf.org/external/datamapper/api/v1/{indicator}/{countries}`. The API accepts ISO-3 country codes (KEN, UGA, TZA, ETH, RWA) and returns a JSON structure where values are nested as `{indicator_code: {iso3: {year_str: value}}}`. The pipeline maps ISO-3 back to ISO-2 using an explicit `ISO3_TO_ISO2` dictionary, filters to the 2000â€“2024 range, and left-merges each indicator onto a scaffold DataFrame of all (economy, year) combinations so that every country-year row exists regardless of data availability. Retry logic handles intermittent API timeouts with exponential backoff (3 attempts, 5-second increment per retry).

2. **Data Ingestion â€” World Bank REST API v2:** Six external debt and macro indicators are fetched from `https://api.worldbank.org/v2/country/{codes}/indicator/{indicator}?format=json&per_page=500&date=2000:2024` using semicolon-delimited ISO-2 country codes. The pipeline handles pagination automatically â€” it reads the `pages` field from the first response envelope and iterates through subsequent pages if the result set exceeds 500 records. Records are normalised from the JSON list format (each record contains `countryiso3code`, `date`, and `value` fields) back to the (economy, year, value) three-column form before merging onto the scaffold. Derived columns (`External debt stocks (USD bn)`, `GDP (USD bn)`, `Net ODA received (USD bn)`) are computed as unit-scaled versions of the raw USD columns after the full merge.

3. **Data Processing and Caching:** After all 10 indicators are merged, the pipeline computes a derived `Fiscal gap (% GDP)` column as the arithmetic difference between Expenditure and Revenue. The complete 125-row merged DataFrame is written to `data/processed/fiscal.parquet` via pyarrow, preserving integer types for the `year` column and float64 types for all indicator columns without the string coercion that CSV writing introduces. The Parquet file is gitignored â€” users run `data_pipeline.py` once locally to populate it. Streamlit's `@st.cache_data` decorator loads the Parquet file once per session, making subsequent tab switches and slider interactions read entirely from in-memory cache rather than re-reading disk or calling any API.

4. **Streamlit Dashboard:** `app.py` is a single-file Streamlit application of 1,036 lines. On load it reads the cached Parquet file, computes per-indicator latest and previous values for Kenya using `.dropna().sort_values('year').iloc[-1]` pattern, and renders five hero KPI cards as custom HTML (`hero-kpi` CSS class) with colour-coded thresholds â€” debt/GDP turns red when it exceeds 60%, fiscal balance turns red when it exceeds -3% of GDP, external debt turns red when it exceeds 50% of GNI, and debt service turns red when it exceeds 15% of GNI. A live-computed executive summary banner assembles four bullet points from the actual loaded values. The four tabs then render eight Plotly charts against a `#060b17` dark background with Kenya-green (`#00d26a`) as the primary series colour and gold (`#f5a623`) for warning thresholds. The sidebar provides a year-range slider and an EAC peer multiselect that filter all chart data in real time. The Export Data tab renders the full dataset in a styled `st.dataframe` and provides two `st.download_button` controls for Excel export using openpyxl.

---

## ðŸ› ï¸ Technical Stack

| **Layer** | **Tool** | **Version** |
|---|---|---|
| Dashboard framework | Streamlit | 1.45+ |
| Visualisation | Plotly Graph Objects + Express | 5.24+ |
| Data wrangling | pandas | 2.2+ |
| Numerical computation | NumPy | 2.0+ |
| IMF fiscal data | IMF DataMapper API | REST (direct requests) |
| World Bank data | World Bank REST API v2 | REST (direct requests) |
| HTTP client | requests | 2.33+ |
| Columnar storage | pyarrow (Parquet) | 16.0+ |
| Excel export | openpyxl | 3.1.5+ |
| Environment management | UV venv | â€” |
| Language | Python | 3.11 |

---

## ðŸ“Š Performance & Results

- **125 rows** in the final merged dataset â€” 5 countries Ã— 25 years (2000â€“2024) â€” with 10 indicator columns; the scaffold-merge pattern ensures every country-year combination exists as a row even if individual indicators have partial coverage
- **Full pipeline run** (4 IMF fetches + 6 World Bank fetches + merge + Parquet write) completes in approximately **45â€“90 seconds** depending on API response times; retry logic handles occasional IMF timeout events transparently
- **Kenya gross government debt** reached **67.3% of GDP** in 2024 â€” exceeding the IMF's 60% sustainability benchmark for emerging market economies by 7.3 percentage points
- **Fiscal balance** remained negative for every year in the 2004â€“2024 window for Kenya â€” Kenya has not recorded a fiscal surplus in the 25-year dataset; the deficit widened during the 2020 COVID-19 shock
- **Interest payments** consumed an increasing share of Kenya's government expenditure between 2014 and the most recent available year, with the trend line rising above the IMF's 25% warning threshold in recent years â€” the key "fiscal trap" indicator where servicing accumulated debt crowds out productive spending
- **External debt service** as a percentage of GNI has risen over the dataset period, reflecting the compounding effect of external borrowing on Kenya's annual cash outflows to creditors
- **EAC peer comparison** confirms Kenya carries the highest gross government debt-to-GDP ratio among the 5 countries in the dataset as of 2024; Rwanda and Ethiopia show lower debt trajectories relative to GDP
- **Dashboard load time** after first `@st.cache_data` call is under 200ms for all tab switches â€” all computation happens on load; no per-interaction API calls or file reads
- **$0 running cost** â€” IMF DataMapper and World Bank Open Data APIs require no authentication, have no paid tiers, and impose no rate limits that affect a single-user pipeline at this data volume

---

## ðŸŒ Live Dashboard

### Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/declerke/Kenya-Fiscal-Intelligence.git
cd Kenya-Fiscal-Intelligence

# 2. Create and activate virtual environment (UV required)
uv venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
# source .venv/bin/activate     # Linux / macOS

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Fetch all 10 indicators (IMF + World Bank â€” requires internet, ~60s)
python data_pipeline.py

# 5. Launch the dashboard
streamlit run app.py
```

Dashboard opens at `http://localhost:8501`.

### Deploy to Streamlit Cloud

1. Fork or push this repository to GitHub
2. Run `data_pipeline.py` locally and commit `data/processed/fiscal.parquet` (remove it from `.gitignore` for the deployment repo, or add a `data_pipeline.py` pre-run step)
3. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub repo, and set the main file to `app.py`
4. No secrets or environment variables are required â€” all data sources are fully open

### Prerequisites

- Python 3.11+
- UV (`pip install uv` â€” used for isolated virtual environments)
- Internet access for the initial `data_pipeline.py` run (IMF and World Bank APIs)
- No API keys required

---

## ðŸ“‘ Data Sources

| Source | Method | Coverage | Key Indicators |
|--------|--------|----------|----------------|
| [IMF DataMapper API](https://www.imf.org/external/datamapper/api/v1/) | Direct `requests` (JSON) | 2000â€“2024, 5 EAC countries | Gross govt debt (% GDP), Revenue (% GDP), Expenditure (% GDP), Fiscal balance (% GDP) |
| [World Bank REST API v2](https://api.worldbank.org/v2/) | Direct `requests` (JSON, paginated) | 2000â€“2024, 5 EAC countries | Interest payments (% expense), External debt stocks (USD), External debt (% GNI), Total debt service (% GNI), Net ODA received (USD), GDP (USD) |

Both APIs are free, require no authentication, and are updated periodically with revised WEO and World Development Indicators estimates. The IMF DataMapper API is the same backend that powers the IMF's public WEO visualisation tool. The World Bank REST API v2 is the standard programmatic interface for all World Development Indicators.

---

## ðŸ§  Key Design Decisions

**IMF DataMapper API over World Bank for fiscal aggregates** â€” The World Bank's fiscal indicators for central government revenue and expenditure (`GC.REV.TOTL.GD.ZS`, `GC.XPN.TOTL.GD.ZS`, `GC.BAL.CASH.GD.ZS`) return empty series for Kenya when queried via the World Bank REST API v2. These series have been inconsistently populated for sub-Saharan African countries in the WDI database for several years, with large gaps that make Kenya's fiscal trajectory unreadable. The IMF's World Economic Outlook DataMapper API, by contrast, provides complete and regularly revised coverage of gross government debt, fiscal balance, revenue, and expenditure as percentages of GDP for Kenya spanning 2000â€“2024 with minimal gaps â€” because the IMF collects these figures directly from Kenya's National Treasury as part of Article IV consultations and WEO surveillance. The decision to use two separate authoritative sources (IMF for fiscal flows, World Bank for external debt stocks) rather than forcing a single-source approach yields better Kenya coverage than either alone, at the cost of a slightly more complex pipeline that maps between ISO-3 (IMF) and ISO-2 (World Bank) country codes.

**Direct `requests` over `wbgapi` library** â€” The `wbgapi` Python package, which provides a convenient DataFrame interface for World Bank data, routes all bulk queries through the World Bank's `/sources/2/` endpoint. In 2025 this endpoint began returning malformed XML responses rather than the JSON it previously delivered, causing `json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` on every call to `wbgapi.data.DataFrame()`. Three separate attempts using wbgapi â€” with different indicators, different country sets, and different date ranges â€” all failed identically. The underlying World Bank data is intact and fully accessible; the failure is a library-routing problem, not a data availability problem. The standard World Bank REST API v2 endpoint (`/v2/country/{codes}/indicator/{code}?format=json`) returns clean, well-structured JSON and continues to operate correctly. Switching to direct `requests` calls added approximately 30 lines of pagination-handling code but eliminated the dependency on a library with a broken routing layer. `wbgapi` is retained in `requirements.txt` at the pinned version for reference but is not called by `data_pipeline.py`.

**Parquet over CSV for processed data** â€” The pipeline fetches 10 indicators for 5 countries over 25 years, producing a merged DataFrame with float64 indicator columns and an integer year column on each run. Writing to CSV coerces the integer `year` column to string representation on disk, requiring an explicit `dtype={'year': int}` parse argument on every read to prevent Plotly from treating years as a categorical axis. Writing to Parquet preserves all column dtypes exactly â€” integer years stay integers, float indicators stay float64, and the `country` string column does not acquire an inferred object dtype. Streamlit's `@st.cache_data` mechanism reads the Parquet file approximately 3x faster than an equivalent CSV at this row count, which matters because the file is read fresh on each Streamlit cold start. The Parquet file is gitignored, keeping the repository lightweight and requiring users to run `data_pipeline.py` once â€” the appropriate separation between a data pipeline and a data product.

**IMF 60% benchmark as a reference line, not just a label** â€” Kenya's gross government debt at 67.3% of GDP in 2024 crosses the IMF's widely-cited 60% debt-to-GDP sustainability threshold for emerging market economies, which was operationalised during the Debt Sustainability Analysis framework reforms of the 2000s and remains the reference level used in IMF Article IV consultations and sovereign credit discussions. Rendering this threshold as a `fig.add_hline(y=60, line_dash='dash')` directly on the debt trajectory chart makes the breach event visually immediate â€” the viewer does not need to know the threshold value in advance, look it up separately, or mentally compare a chart y-axis to a number mentioned in a caption. The threshold line frames the chart as answering a specific question (has Kenya's debt exceeded the sustainability benchmark?) rather than simply presenting a time series. This is standard practice in fiscal risk dashboards used by DFI country economists and sovereign debt analysts; without the reference line, the same chart requires the viewer to supply their own benchmark context.

**Continuous fiscal deficit shading on the fiscal balance chart** â€” Kenya has run a fiscal deficit every year since at least 2004. A line chart of fiscal balance over 20+ years is technically accurate but cognitively demanding: the viewer must track which years fall above and below the zero line, mentally integrate the area under the curve, and form a conclusion about the persistence and depth of the deficit trend. The implementation replaces a single-colour line with a bar chart where individual bars are coloured red for deficit years and green for surplus years, and adds a dashed `-3% of GDP` Maastricht threshold reference line. The red-green encoding makes the duration of the deficit immediately visible at a glance: a viewer who looks at the chart for two seconds understands that Kenya has been in continuous deficit for two decades, which is the correct and central insight. The -3% reference line contextualises how deep the deficit runs relative to a widely-referenced fiscal prudence threshold. Without these design choices, the same data in a neutral-colour line chart would require a full minute of careful reading to extract the same conclusion.

---

## ðŸ“‚ Project Structure

```text
kenya-fiscal-intelligence/
â”œâ”€â”€ app.py                          # Streamlit dashboard â€” 1,036 lines, 4 tabs, 8 Plotly charts
â”œâ”€â”€ data_pipeline.py                # Full fetch pipeline â€” IMF + WB APIs, Parquet output
â”œâ”€â”€ requirements.txt                # Python dependencies â€” streamlit, plotly, pandas, pyarrow, requests
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ processed/
â”‚   â”‚   â””â”€â”€ fiscal.parquet          # Merged 125-row dataset â€” gitignored, generated by pipeline
â”‚   â””â”€â”€ raw/                        # Reserved for intermediate raw API response caching (unused)
â””â”€â”€ assets/                         # Static assets directory (screenshots, logos)
```

---

## âš™ï¸ Installation & Setup

### Prerequisites

- Python 3.11 or later
- UV package manager (`pip install uv`)
- Internet connection for the initial data fetch (no API keys required)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/declerke/Kenya-Fiscal-Intelligence.git
   cd Kenya-Fiscal-Intelligence
   ```

2. **Create a virtual environment**
   ```bash
   uv venv .venv
   ```

3. **Activate the environment**
   ```bash
   # Windows PowerShell
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Run the data pipeline**
   ```bash
   python data_pipeline.py
   ```
   This fetches all 10 indicators from the IMF and World Bank APIs and writes `data/processed/fiscal.parquet`. Expect approximately 45â€“90 seconds depending on API response times. Progress is printed to the terminal for each indicator fetch.

   Expected terminal output:
   ```
   Fetching fiscal indicators (IMF + World Bank)...
   Countries: ['KE', 'UG', 'TZ', 'ET', 'RW']

   --- IMF indicators ---
     Fetching GGXWDG_GDP â€” Gross govt debt (% GDP)... OK (124 non-null across all countries)
     Fetching GGR_G01_GDP_PT â€” Revenue (% GDP)... OK (125 non-null across all countries)
     Fetching GGX_GDP â€” Expenditure (% GDP)... OK (125 non-null across all countries)
     Fetching GGXCNL_G01_GDP_PT â€” Fiscal balance (% GDP)... OK (125 non-null across all countries)

   --- World Bank indicators ---
     Fetching GC.XPN.INTP.ZS â€” Interest payments (% expense)... OK (48 non-null across all countries)
     Fetching DT.DOD.DECT.CD â€” External debt stocks (USD)... OK (119 non-null across all countries)
     ...

   ======================================================================
   Saved 125 rows to data/processed/fiscal.parquet
   Countries : ['ET', 'KE', 'RW', 'TZ', 'UG']
   Years     : 2000 â€“ 2024
   ```

6. **Launch the dashboard**
   ```bash
   streamlit run app.py
   ```
   Opens at `http://localhost:8501`.

---

## ðŸ“ˆ Indicator Reference

| Code | Name | Source | Kenya Coverage |
|------|------|--------|----------------|
| `GGXWDG_GDP` | Gross government debt (% GDP) | IMF DataMapper WEO | 2000â€“2024 |
| `GGR_G01_GDP_PT` | Government revenue (% GDP) | IMF DataMapper WEO | 2000â€“2024 |
| `GGX_GDP` | Government expenditure (% GDP) | IMF DataMapper WEO | 2000â€“2024 |
| `GGXCNL_G01_GDP_PT` | Fiscal balance (% GDP) | IMF DataMapper WEO | 2000â€“2024 |
| `GC.XPN.INTP.ZS` | Interest payments (% of expense) | World Bank WDI | 2014â€“2023 (latest available) |
| `DT.DOD.DECT.CD` | External debt stocks (current USD) | World Bank WDI | 2000â€“2023 |
| `DT.DOD.DECT.GN.ZS` | External debt (% of GNI) | World Bank WDI | 2000â€“2023 |
| `DT.TDS.DECT.GN.ZS` | Total debt service (% of GNI) | World Bank WDI | 2000â€“2023 |
| `DT.ODA.ALLD.CD` | Net ODA received (current USD) | World Bank WDI | 2000â€“2022 |
| `NY.GDP.MKTP.CD` | GDP (current USD) | World Bank WDI | 2000â€“2023 |

World Bank indicators have coverage through 2023 for most series; IMF DataMapper indicators include 2024 estimates as published in the most recent World Economic Outlook release. Coverage gaps appear as NaN in the merged Parquet file and are handled gracefully in the dashboard via `.dropna(subset=[col])` before any chart is rendered.

---

## ðŸŽ“ Skills Demonstrated

- **Multi-source API integration** â€” Fetching from two structurally different REST APIs (IMF DataMapper JSON nested structure vs. World Bank REST v2 paginated envelope format) within a single pipeline; handling ISO-3 to ISO-2 country code mapping between sources; implementing retry logic with exponential backoff for intermittent API timeouts; paginating World Bank responses automatically using the `pages` field in the response envelope â€” directly relevant to data engineer roles requiring experience ingesting from government and international organisation data portals

- **Python data pipeline engineering** â€” Scaffold-merge pattern for building complete (entity, time) matrices regardless of API coverage gaps; derived column computation (fiscal gap, USD-to-billions scaling) after full merge to avoid partial-data arithmetic errors; Parquet output with pyarrow preserving column dtypes; modular fetch functions with retry and timeout parameters â€” directly relevant to roles requiring ETL pipeline design, data quality handling, and structured storage patterns

- **Streamlit dashboard development** â€” 1,036-line single-file production Streamlit app with custom CSS global styling, `@st.cache_data` for session-level caching, 5 custom hero KPI HTML components with conditional colour thresholds, live-computed executive summary banner assembled from actual loaded data values, sidebar controls (year range slider + multiselect) driving filtered chart views, and Excel export via openpyxl with multi-sheet workbook generation â€” directly relevant to roles requiring BI dashboard development and data product delivery

- **Plotly advanced charting** â€” Gradient-fill area charts for debt trajectory; dual-axis bar + line charts for external debt stocks vs. debt service; fiscally-annotated bar charts with red/green conditional colouring for surplus/deficit; scatter plots with diagonal balance reference lines and deficit zone annotations; horizontal bar ranking charts; multi-series line charts with country-specific colours and line weights; `add_hline` and `add_vline` annotations for benchmark reference lines and historical events â€” directly relevant to roles requiring advanced data visualisation skills beyond standard chart libraries

- **Fiscal economics and sovereign debt analytics** â€” IMF 60% debt-to-GDP sustainability benchmark application; fiscal balance interpretation (deficit/surplus, Maastricht -3% threshold); external debt sustainability metrics (external debt as % of GNI, total debt service as % of GNI); interest payments crowding-out analysis; EAC cross-country fiscal comparison; event-driven annotation of macro shocks (GFC, COVID-19, IMF program) â€” directly relevant to roles at development finance institutions, commercial banks with sovereign exposure, or economic research organisations covering Sub-Saharan Africa

- **Data source evaluation and API debugging** â€” Identifying and routing around the `wbgapi` library's broken `/sources/2/` XML endpoint failure by switching to direct World Bank REST API v2 calls; diagnosing the World Bank WDI coverage gap for Kenya's fiscal aggregates and selecting the IMF DataMapper API as the correct alternative source; validating data completeness per indicator via the pipeline's per-indicator non-null count summary â€” directly relevant to roles where engineers must assess data source reliability and handle upstream API failures without losing pipeline availability

- **Production code quality** â€” `.dropna(subset=[col])` guards before every chart render to handle sparse World Bank series; conditional colour classes applied via runtime value comparison rather than hardcoded strings; `@st.cache_data` applied to the data loading function to prevent repeated disk reads on tab navigation; gitignored Parquet file with documented one-time pipeline run in README; zero external service dependencies (no database, no auth service, no paid APIs) â€” directly relevant to any role requiring production-quality code that handles missing data and edge cases gracefully

