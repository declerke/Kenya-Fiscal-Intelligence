"""
Kenya Fiscal Intelligence Dashboard
Are we living beyond our means? Kenya's budget, debt, and fiscal trajectory 2000-2024.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import io

# ─── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Kenya Fiscal Intelligence",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ──────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background-color: #060b17;
}
[data-testid="stSidebar"] {
    background: #080d1a !important;
    border-right: 1px solid rgba(0,210,106,0.12);
}
/* Hide all sidebar toggle buttons (Material Icons font not loading from CDN) */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
    display: none !important;
}
/* Prevent raw icon text from bleeding through anywhere */
span.material-symbols-rounded,
span.material-symbols-outlined,
span.material-icons {
    visibility: hidden !important;
    font-size: 0 !important;
}
[data-testid="stSidebar"] * { color: #a0aec0 !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1729 0%, #131f38 100%);
    border: 1px solid rgba(0,210,106,0.15);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    border-left: 3px solid #00d26a;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
[data-testid="metric-container"] label {
    color: #718096 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
    font-size: 1.9rem !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0c1428;
    border-radius: 10px;
    padding: 4px 6px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    color: #718096;
    border-radius: 7px;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 0.45rem 1rem;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00d26a, #00b35c) !important;
    color: #000 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.2rem;
}

/* Typography */
h1 { color: #f7fafc !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h2 { color: #e2e8f0 !important; font-weight: 600 !important; }
h3 { color: #a0aec0 !important; font-weight: 500 !important; }
p, li { color: #cbd5e0 !important; }
hr { border: none !important; border-top: 1px solid rgba(0,210,106,0.1) !important; margin: 0.8rem 0 !important; }

/* Insight boxes */
.insight-box {
    background: linear-gradient(135deg, #0d1527 0%, #141f38 100%);
    border-left: 4px solid #f5a623;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin: 0.8rem 0 1.2rem 0;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.insight-box strong { color: #f5a623; }
.insight-box .icon { font-size: 1.1rem; margin-right: 0.4rem; }

.warning-box {
    background: linear-gradient(135deg, #1a0f0f 0%, #2a1010 100%);
    border-left: 4px solid #ce1126;
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin: 0.8rem 0 1.2rem 0;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
}
.warning-box strong { color: #ce1126; }

.hero-kpi {
    background: linear-gradient(135deg, #0d1a2d 0%, #0f2040 100%);
    border: 1px solid rgba(0,210,106,0.2);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}
.hero-num { font-size: 2.8rem; font-weight: 800; color: #00d26a; line-height: 1.1; }
.hero-num.red { color: #ce1126; }
.hero-num.gold { color: #f5a623; }
.hero-label { font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.3rem; }
.hero-sub { font-size: 0.82rem; color: #a0aec0; margin-top: 0.2rem; }

.section-divider {
    height: 2px;
    background: linear-gradient(90deg, rgba(0,210,106,0.4), rgba(0,210,106,0.05), transparent);
    margin: 1.5rem 0 1rem 0;
    border-radius: 2px;
}

/* Dataframe styling */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Sidebar caption */
[data-testid="stSidebar"] .stCaption { color: #4a5568 !important; font-size: 0.75rem !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── Design tokens ───────────────────────────────────────────────────────────
KENYA_GREEN = '#00d26a'
KENYA_RED   = '#ce1126'
GOLD        = '#f5a623'
BLUE        = '#4299e1'
PURPLE      = '#9f7aea'
TEAL        = '#38b2ac'

CHART_COLORS = [KENYA_GREEN, GOLD, KENYA_RED, BLUE, PURPLE, TEAL]

COUNTRY_COLORS = {
    'KE': KENYA_GREEN,
    'UG': GOLD,
    'TZ': BLUE,
    'ET': PURPLE,
    'RW': TEAL,
}

COUNTRY_NAMES = {
    'KE': 'Kenya', 'UG': 'Uganda', 'TZ': 'Tanzania',
    'ET': 'Ethiopia', 'RW': 'Rwanda',
}

BG_PAPER = 'rgba(0,0,0,0)'
BG_PLOT  = 'rgba(0,0,0,0)'
GRID_COLOR = 'rgba(255,255,255,0.05)'
AXIS_COLOR = 'rgba(255,255,255,0.12)'
FONT_COLOR = '#e2e8f0'
AXIS_FONT  = '#8a9ab8'


def base_layout(title: str = '', height: int = 420, x_title: str = '',
                y_title: str = '', legend: bool = True) -> dict:
    layout = dict(
        title=dict(
            text=title,
            font=dict(color='#d0daf0', size=15, family='Inter'),
            x=0.01, y=0.97,
        ),
        paper_bgcolor=BG_PAPER,
        plot_bgcolor=BG_PLOT,
        font=dict(color=FONT_COLOR, family='Inter', size=12),
        height=height,
        margin=dict(l=12, r=20, t=55, b=30),
        xaxis=dict(
            title=x_title,
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            zeroline=False,
            tickfont=dict(color=AXIS_FONT),
            title_font=dict(color=AXIS_FONT),
        ),
        yaxis=dict(
            title=y_title,
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            zeroline=False,
            tickfont=dict(color=AXIS_FONT),
            title_font=dict(color=AXIS_FONT),
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#0d1830',
            bordercolor='rgba(0,210,106,0.3)',
            font=dict(color='#e2e8f0', family='Inter'),
        ),
    )
    if legend:
        layout['legend'] = dict(
            bgcolor='rgba(10,15,35,0.7)',
            bordercolor='rgba(255,255,255,0.07)',
            borderwidth=1,
            font=dict(color='#a0aec0'),
        )
    return layout


# ─── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = Path('data/processed/fiscal.parquet')
    if not path.exists():
        st.error("data/processed/fiscal.parquet not found. Run data_pipeline.py first.")
        st.stop()
    df = pd.read_parquet(path)
    return df


df = load_data()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇰🇪 Kenya Fiscal Intel")
    st.markdown("*Government finances, debt trajectory & fiscal sustainability*")
    st.markdown("---")

    year_min = int(df['year'].min())
    year_max = int(df['year'].max())
    year_range = st.slider(
        "Year Range", year_min, year_max,
        (max(year_min, 2004), year_max),
        help="Filter the analysis period"
    )

    st.markdown("---")
    st.markdown("### EAC Peer Comparison")
    peer_options = {'Uganda': 'UG', 'Tanzania': 'TZ', 'Ethiopia': 'ET', 'Rwanda': 'RW'}
    selected_peers = st.multiselect(
        "Select peers",
        list(peer_options.keys()),
        default=['Uganda', 'Tanzania', 'Rwanda'],
    )
    selected_codes = ['KE'] + [peer_options[p] for p in selected_peers]

    st.markdown("---")
    st.markdown("### About")
    st.caption("**Data sources:**")
    st.caption("- IMF DataMapper API (fiscal aggregates)")
    st.caption("- World Bank Open Data API (external debt, GDP)")
    st.caption("")
    st.caption("**Coverage:** 2000–2024, 5 EAC countries")
    st.caption("**Built with:** Streamlit · Plotly · pandas")


# ─── Filter helpers ───────────────────────────────────────────────────────────
def get_ke(yr=None):
    base = df[df['economy'] == 'KE'].copy()
    if yr:
        base = base[(base['year'] >= yr[0]) & (base['year'] <= yr[1])]
    return base.sort_values('year')

def get_peers(codes, yr=None):
    base = df[df['economy'].isin(codes)].copy()
    if yr:
        base = base[(base['year'] >= yr[0]) & (base['year'] <= yr[1])]
    return base.sort_values(['economy', 'year'])


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 0.5rem 0 1rem 0;">
  <h1 style="font-size:2rem; margin-bottom:0.2rem;">
    🇰🇪 Kenya Fiscal Intelligence
  </h1>
  <p style="color:#718096; font-size:0.95rem; margin-top:0;">
    Are we living beyond our means? · Budget, debt & fiscal trajectory 2000–2024
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ─── Hero KPIs ────────────────────────────────────────────────────────────────
ke_all = get_ke()

def latest_val(series, col):
    s = series.dropna(subset=[col]).sort_values('year')
    return s.iloc[-1] if len(s) > 0 else None

def prev_val(series, col):
    s = series.dropna(subset=[col]).sort_values('year')
    return s.iloc[-2] if len(s) > 1 else None

latest_debt  = latest_val(ke_all, 'Gross govt debt (% GDP)')
prev_debt    = prev_val(ke_all, 'Gross govt debt (% GDP)')
latest_bal   = latest_val(ke_all, 'Fiscal balance (% GDP)')
latest_rev   = latest_val(ke_all, 'Revenue (% GDP)')
latest_exp   = latest_val(ke_all, 'Expenditure (% GDP)')
latest_ext   = latest_val(ke_all, 'External debt (% GNI)')
latest_svc   = latest_val(ke_all, 'Total debt service (% GNI)')
latest_int   = latest_val(ke_all, 'Interest payments (% expense)')

def fmt(row, col, suffix='%', dp=1):
    if row is None or pd.isna(row.get(col, np.nan)):
        return 'N/A'
    return f"{row[col]:.{dp}f}{suffix}"

def delta_fmt(cur, prv, col):
    if cur is None or prv is None:
        return None
    d = cur.get(col, np.nan) - prv.get(col, np.nan)
    if pd.isna(d):
        return None
    return f"{d:+.1f} pp"

col1, col2, col3, col4, col5 = st.columns(5)

debt_val = fmt(latest_debt, 'Gross govt debt (% GDP)')
debt_yr  = int(latest_debt['year']) if latest_debt is not None else ''
with col1:
    debt_num_class = 'hero-num red' if latest_debt is not None and latest_debt['Gross govt debt (% GDP)'] > 60 else 'hero-num gold'
    st.markdown(f"""
    <div class="hero-kpi">
      <div class="{debt_num_class}">{debt_val}</div>
      <div class="hero-label">Govt Debt / GDP</div>
      <div class="hero-sub">{debt_yr}</div>
    </div>""", unsafe_allow_html=True)

bal_val = fmt(latest_bal, 'Fiscal balance (% GDP)')
bal_yr  = int(latest_bal['year']) if latest_bal is not None else ''
with col2:
    bal_class = 'hero-num red' if latest_bal is not None and latest_bal['Fiscal balance (% GDP)'] < -3 else 'hero-num gold'
    st.markdown(f"""
    <div class="hero-kpi">
      <div class="{bal_class}">{bal_val}</div>
      <div class="hero-label">Fiscal Balance / GDP</div>
      <div class="hero-sub">{bal_yr}</div>
    </div>""", unsafe_allow_html=True)

rev_val = fmt(latest_rev, 'Revenue (% GDP)')
rev_yr  = int(latest_rev['year']) if latest_rev is not None else ''
with col3:
    st.markdown(f"""
    <div class="hero-kpi">
      <div class="hero-num">{rev_val}</div>
      <div class="hero-label">Revenue / GDP</div>
      <div class="hero-sub">{rev_yr}</div>
    </div>""", unsafe_allow_html=True)

ext_val = fmt(latest_ext, 'External debt (% GNI)')
ext_yr  = int(latest_ext['year']) if latest_ext is not None else ''
with col4:
    ext_class = 'hero-num red' if latest_ext is not None and latest_ext['External debt (% GNI)'] > 50 else 'hero-num gold'
    st.markdown(f"""
    <div class="hero-kpi">
      <div class="{ext_class}">{ext_val}</div>
      <div class="hero-label">External Debt / GNI</div>
      <div class="hero-sub">{ext_yr}</div>
    </div>""", unsafe_allow_html=True)

svc_val = fmt(latest_svc, 'Total debt service (% GNI)')
svc_yr  = int(latest_svc['year']) if latest_svc is not None else ''
with col5:
    svc_class = 'hero-num red' if latest_svc is not None and latest_svc['Total debt service (% GNI)'] > 15 else 'hero-num gold'
    st.markdown(f"""
    <div class="hero-kpi">
      <div class="{svc_class}">{svc_val}</div>
      <div class="hero-label">Debt Service / GNI</div>
      <div class="hero-sub">{svc_yr}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ─── Executive Summary Banner ─────────────────────────────────────────────────
ke_latest_debt_row = ke_all[ke_all['Gross govt debt (% GDP)'].notna()].sort_values('year').iloc[-1]
ke_latest_balance_row = ke_all[ke_all['Fiscal balance (% GDP)'].notna()].sort_values('year').iloc[-1]
ke_latest_ds_row = ke_all[ke_all['Total debt service (% GNI)'].notna()].sort_values('year').iloc[-1]
ke_latest_int_row = ke_all[ke_all['Interest payments (% expense)'].notna()].sort_values('year').iloc[-1]

exec_text = f"""
<div style="background:linear-gradient(135deg,#0f1729,#1a2744);border-radius:12px;padding:1.2rem 1.5rem;border:1px solid rgba(0,210,106,0.2);margin-bottom:1.5rem">
<div style="color:#00d26a;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:0.6rem">&#x1F4CB; KEY FINDINGS</div>
<ul style="color:#cbd5e0;margin:0;padding-left:1.2rem;line-height:1.8">
<li>Kenya's gross government debt reached <strong style="color:#f5a623">{ke_latest_debt_row['Gross govt debt (% GDP)']:.1f}% of GDP</strong> in {int(ke_latest_debt_row['year'])} — exceeding the IMF's 60% sustainability benchmark.</li>
<li>The fiscal balance stood at <strong style="color:#ce1126">{ke_latest_balance_row['Fiscal balance (% GDP)']:.1f}% of GDP</strong> in {int(ke_latest_balance_row['year'])} — Kenya has run continuous deficits for over a decade.</li>
<li>Total external debt service costs <strong style="color:#f5a623">{ke_latest_ds_row['Total debt service (% GNI)']:.1f}%</strong> of GNI annually, crowding out spending on public services.</li>
<li>Interest payments consumed <strong style="color:#ce1126">{ke_latest_int_row['Interest payments (% expense)']:.1f}%</strong> of government expenditure in {int(ke_latest_int_row['year'])} — signalling a <strong style="color:#ce1126">fiscal trap</strong> where servicing old debt limits investment in new priorities.</li>
</ul>
</div>
"""
st.markdown(exec_text, unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Debt Trajectory",
    "💰  Revenue & Expenditure",
    "🌍  Peer Comparison",
    "📥  Export Data",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — DEBT TRAJECTORY
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    ke = get_ke(year_range)
    ke_debt = ke.dropna(subset=['Gross govt debt (% GDP)']).sort_values('year')
    ke_ext  = ke.dropna(subset=['External debt stocks (USD bn)']).sort_values('year')

    # --- Insight callout ---
    if len(ke_debt) >= 2:
        d_start = ke_debt.iloc[0]
        d_end   = ke_debt.iloc[-1]
        d_chg   = d_end['Gross govt debt (% GDP)'] - d_start['Gross govt debt (% GDP)']
        d_dir   = "surged" if d_chg > 10 else ("risen" if d_chg > 0 else "fallen")
        yr_peak_row = ke_debt.loc[ke_debt['Gross govt debt (% GDP)'].idxmax()]
        peak_yr  = int(yr_peak_row['year'])
        peak_val = yr_peak_row['Gross govt debt (% GDP)']
        st.markdown(f"""
        <div class="insight-box">
          <span class="icon">📊</span>
          Kenya's general government debt has <strong>{d_dir}</strong> from
          <strong>{d_start['Gross govt debt (% GDP)']:.1f}%</strong> of GDP
          in {int(d_start['year'])} to <strong>{d_end['Gross govt debt (% GDP)']:.1f}%</strong>
          in {int(d_end['year'])} — a change of <strong>{d_chg:+.1f} percentage points</strong>.
          Peak recorded: <strong>{peak_val:.1f}% in {peak_yr}</strong>.
          Kenya's debt/GDP ratio exceeds the IMF's 60% benchmark for emerging economies.
        </div>
        """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    # Chart 1: Debt/GDP area + annotations
    with col_a:
        st.markdown("#### General Government Debt (% of GDP)")
        fig1 = go.Figure()

        if not ke_debt.empty:
            # Gradient fill area
            fig1.add_trace(go.Scatter(
                x=ke_debt['year'], y=ke_debt['Gross govt debt (% GDP)'],
                mode='lines',
                line=dict(color=KENYA_GREEN, width=2.5),
                fill='tozeroy',
                fillcolor='rgba(0,210,106,0.08)',
                name='Debt / GDP',
                hovertemplate='%{y:.1f}%<extra>Debt/GDP</extra>',
            ))

            # 60% IMF threshold — horizontal reference line
            fig1.add_hline(
                y=60, line_dash='dash', line_color='rgba(245,166,35,0.5)',
                line_width=1.5,
                annotation_text='IMF 60% Benchmark',
                annotation_position='top right',
                annotation_font_color='#f5a623',
            )

            # Key event vertical lines
            vline_events = {
                2008: ('Global Financial Crisis', 'rgba(160,160,180,0.45)', 'rgba(160,160,180,0.9)'),
                2014: ('Eurobond Era',             'rgba(0,210,106,0.45)',   'rgba(0,210,106,0.9)'),
                2020: ('COVID-19 Shock',           'rgba(206,17,38,0.55)',   'rgba(206,17,38,0.9)'),
                2023: ('IMF Program',              'rgba(245,166,35,0.55)',  'rgba(245,166,35,0.9)'),
            }
            for yr, (label, line_color, ann_color) in vline_events.items():
                if ke_debt['year'].between(yr, yr).any():
                    fig1.add_vline(
                        x=yr,
                        line_dash='dash',
                        line_color=line_color,
                        line_width=1.2,
                        annotation_text=label,
                        annotation_position='top left',
                        annotation_font=dict(color=ann_color, size=9),
                    )

        layout1 = base_layout('', 400, y_title='% of GDP')
        layout1['yaxis']['range'] = [0, max(90, ke_debt['Gross govt debt (% GDP)'].max() * 1.15) if not ke_debt.empty else 90]
        fig1.update_layout(**layout1)
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Dual-axis — External debt stocks (USD bn) + debt service (% GNI)
    with col_b:
        st.markdown("#### External Debt: Stocks vs Debt Service")
        fig2 = go.Figure()

        ke_svc = ke.dropna(subset=['Total debt service (% GNI)']).sort_values('year')

        if not ke_ext.empty:
            fig2.add_trace(go.Bar(
                x=ke_ext['year'],
                y=ke_ext['External debt stocks (USD bn)'],
                name='Ext debt (USD bn)',
                marker_color='rgba(0,210,106,0.3)',
                marker_line=dict(color=KENYA_GREEN, width=1.2),
                yaxis='y1',
                hovertemplate='USD %{y:.1f}bn<extra>External debt</extra>',
            ))

        if not ke_svc.empty:
            fig2.add_trace(go.Scatter(
                x=ke_svc['year'],
                y=ke_svc['Total debt service (% GNI)'],
                name='Debt service (% GNI)',
                mode='lines+markers',
                line=dict(color=GOLD, width=2.5),
                marker=dict(size=5, color=GOLD),
                yaxis='y2',
                hovertemplate='%{y:.1f}%<extra>Debt service/GNI</extra>',
            ))

        layout2 = base_layout('', 400)
        layout2.update(dict(
            yaxis=dict(
                title='External debt (USD bn)',
                gridcolor=GRID_COLOR,
                linecolor=AXIS_COLOR,
                zeroline=False,
                tickfont=dict(color=AXIS_FONT),
                title_font=dict(color=KENYA_GREEN),
            ),
            yaxis2=dict(
                title='Debt service (% GNI)',
                overlaying='y',
                side='right',
                gridcolor='rgba(0,0,0,0)',
                zeroline=False,
                tickfont=dict(color=AXIS_FONT),
                title_font=dict(color=GOLD),
            ),
        ))
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3 (full width): External debt (% GNI) trend
    st.markdown("#### External Debt Burden (% of GNI) — Full Timeline")
    ke_gni = ke_all.dropna(subset=['External debt (% GNI)']).sort_values('year')
    fig3 = go.Figure()
    if not ke_gni.empty:
        fig3.add_trace(go.Scatter(
            x=ke_gni['year'], y=ke_gni['External debt (% GNI)'],
            mode='lines+markers',
            line=dict(color=KENYA_RED, width=2.5),
            marker=dict(size=6, color=KENYA_RED),
            fill='tozeroy',
            fillcolor='rgba(206,17,38,0.07)',
            name='Ext debt / GNI',
            hovertemplate='%{y:.1f}%<extra>External debt/GNI</extra>',
        ))
        fig3.add_hline(
            y=50, line_dash='dot', line_color='rgba(245,166,35,0.5)',
            annotation_text='50% caution threshold',
            annotation_position='top right',
            annotation_font=dict(color='#f5a623', size=10),
        )
    fig3.update_layout(**base_layout('', 300, y_title='% of GNI'))
    st.plotly_chart(fig3, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — REVENUE & EXPENDITURE
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    ke = get_ke(year_range)
    ke_rev = ke.dropna(subset=['Revenue (% GDP)', 'Expenditure (% GDP)']).sort_values('year')
    ke_bal = ke.dropna(subset=['Fiscal balance (% GDP)']).sort_values('year')
    ke_int = ke.dropna(subset=['Interest payments (% expense)']).sort_values('year')

    # ── Insight callout ──
    if latest_int is not None and latest_rev is not None:
        int_pct = latest_int.get('Interest payments (% expense)', np.nan)
        rev_pct_exp = 100 - int_pct if pd.notna(int_pct) else np.nan
        int_yr = int(latest_int['year'])
        rev_yr2 = int(latest_rev['year'])
        if pd.notna(int_pct):
            st.markdown(f"""
            <div class="warning-box">
              <span>⚠️</span>
              In <strong>{int_yr}</strong>, Kenya spent <strong>{int_pct:.1f}%</strong>
              of government expenditure on interest payments alone — leaving only
              <strong>{rev_pct_exp:.1f}%</strong> for services, infrastructure, and social spending.
              This "fiscal trap" — high interest crowding out productive spending — is a key
              risk indicator. The IMF 25% warning threshold was
              {'<strong style="color:#ce1126">breached</strong>' if int_pct > 25 else 'approached'}.
            </div>
            """, unsafe_allow_html=True)
    elif latest_bal is not None:
        bal_yr2 = int(latest_bal['year'])
        bal_v   = latest_bal['Fiscal balance (% GDP)']
        st.markdown(f"""
        <div class="warning-box">
          <span>⚠️</span>
          Kenya's fiscal balance stood at <strong>{bal_v:.1f}% of GDP</strong>
          in <strong>{bal_yr2}</strong>, indicating a persistent deficit.
          Every year of deficit adds to the debt stock, compounding future interest costs.
        </div>
        """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    # Chart: Revenue vs Expenditure grouped bars
    with col_a:
        st.markdown("#### Revenue vs Expenditure (% of GDP)")
        fig4 = go.Figure()
        if not ke_rev.empty:
            fig4.add_trace(go.Bar(
                x=ke_rev['year'], y=ke_rev['Revenue (% GDP)'],
                name='Revenue',
                marker_color='rgba(0,210,106,0.75)',
                marker_line=dict(color=KENYA_GREEN, width=0.8),
                hovertemplate='%{y:.1f}%<extra>Revenue</extra>',
            ))
            fig4.add_trace(go.Bar(
                x=ke_rev['year'], y=ke_rev['Expenditure (% GDP)'],
                name='Expenditure',
                marker_color='rgba(245,166,35,0.7)',
                marker_line=dict(color=GOLD, width=0.8),
                hovertemplate='%{y:.1f}%<extra>Expenditure</extra>',
            ))
        layout4 = base_layout('', 400, y_title='% of GDP')
        layout4['barmode'] = 'group'
        fig4.update_layout(**layout4)
        st.plotly_chart(fig4, use_container_width=True)

    # Chart: Fiscal balance waterfall-style
    with col_b:
        st.markdown("#### Fiscal Balance (% of GDP) — Deficit/Surplus")
        fig5 = go.Figure()
        if not ke_bal.empty:
            colors = [KENYA_GREEN if v >= 0 else KENYA_RED
                      for v in ke_bal['Fiscal balance (% GDP)']]
            fig5.add_trace(go.Bar(
                x=ke_bal['year'],
                y=ke_bal['Fiscal balance (% GDP)'],
                name='Fiscal balance',
                marker_color=colors,
                marker_line=dict(color='rgba(255,255,255,0.1)', width=0.5),
                hovertemplate='%{y:.2f}%<extra>Fiscal balance</extra>',
            ))
            fig5.add_hline(y=0, line_color='rgba(255,255,255,0.2)', line_width=1)
            fig5.add_hline(
                y=-3, line_dash='dash', line_color='rgba(245,166,35,0.5)',
                annotation_text='-3% Maastricht threshold',
                annotation_position='bottom right',
                annotation_font=dict(color='#f5a623', size=9),
            )
        layout5 = base_layout('', 400, y_title='% of GDP')
        fig5.update_layout(**layout5)
        st.plotly_chart(fig5, use_container_width=True)

    # Chart: Interest payments % expense (full width)
    st.markdown("#### Interest Payments as % of Government Expenditure — The Fiscal Trap (2014–2023, latest available)")
    st.caption("⚠️ World Bank data available from 2014 onwards for this indicator.")
    fig6 = go.Figure()
    ke_int_full = ke_all.dropna(subset=['Interest payments (% expense)']).sort_values('year')
    if not ke_int_full.empty:
        bar_colors = ['rgba(206,17,38,0.8)' if v > 25 else 'rgba(0,210,106,0.7)'
                      for v in ke_int_full['Interest payments (% expense)']]
        fig6.add_trace(go.Bar(
            x=ke_int_full['year'],
            y=ke_int_full['Interest payments (% expense)'],
            name='Interest / expense',
            marker_color=bar_colors,
            hovertemplate='%{y:.1f}%<extra>Interest/Expense</extra>',
        ))
        fig6.add_hline(
            y=25, line_dash='dash', line_color='rgba(245,166,35,0.7)',
            line_width=2,
            annotation_text='⚠️ 25% warning threshold',
            annotation_position='top left',
            annotation_font=dict(color='#f5a623', size=11, family='Inter'),
        )
        # Add trend line
        x_vals = ke_int_full['year'].values
        y_vals = ke_int_full['Interest payments (% expense)'].values
        mask = ~np.isnan(y_vals)
        if mask.sum() > 2:
            z = np.polyfit(x_vals[mask], y_vals[mask], 1)
            p = np.poly1d(z)
            fig6.add_trace(go.Scatter(
                x=x_vals, y=p(x_vals),
                mode='lines',
                line=dict(color='rgba(255,255,255,0.25)', dash='dot', width=1.5),
                name='Trend',
                hoverinfo='skip',
            ))
    fig6.update_layout(**base_layout('', 350, y_title='% of expenditure'))
    st.plotly_chart(fig6, use_container_width=True)

    # ── Revenue vs Expenditure gap insight (dynamically computed) ──
    _latest_rev = ke_all[ke_all['Revenue (% GDP)'].notna()].sort_values('year').iloc[-1]
    _latest_exp = ke_all[ke_all['Expenditure (% GDP)'].notna()].sort_values('year').iloc[-1]
    _gap = _latest_exp['Expenditure (% GDP)'] - _latest_rev['Revenue (% GDP)']
    insight_text = (
        f"In {int(_latest_rev['year'])}, Kenya collected revenue worth "
        f"<strong>{_latest_rev['Revenue (% GDP)']:.1f}%</strong> of GDP but spent "
        f"<strong>{_latest_exp['Expenditure (% GDP)']:.1f}%</strong> — a spending gap of "
        f"<strong style='color:#ce1126'>{_gap:.1f} percentage points</strong>. "
        f"This gap must be financed through borrowing, adding to the debt stock. "
        f"Every deficit year compounds future interest obligations, deepening the fiscal trap."
    )
    if not ke_int_full.empty:
        latest_int_r = ke_int_full.iloc[-1]
        earliest_int_r = ke_int_full.iloc[0]
        chg = latest_int_r['Interest payments (% expense)'] - earliest_int_r['Interest payments (% expense)']
        interest_text = (
            f" Between <strong>{int(earliest_int_r['year'])}</strong> and "
            f"<strong>{int(latest_int_r['year'])}</strong>, the share of government spending "
            f"consumed by interest payments "
            f"{'<strong>increased</strong>' if chg > 0 else '<strong>decreased</strong>'} "
            f"by <strong>{abs(chg):.1f} pp</strong> "
            f"(from <strong>{earliest_int_r['Interest payments (% expense)']:.1f}%</strong> "
            f"to <strong>{latest_int_r['Interest payments (% expense)']:.1f}%</strong>)."
        )
    else:
        interest_text = ""

    st.markdown(f"""
    <div class="insight-box">
      <span class="icon">&#x1F4B0;</span>
      {insight_text}{interest_text}
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — PEER COMPARISON
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    peers_df = get_peers(selected_codes, year_range)

    col_a, col_b = st.columns(2)

    # Chart 6: Multi-country debt/GDP line chart
    with col_a:
        st.markdown("#### Govt Debt / GDP — EAC Country Comparison")
        fig7 = go.Figure()
        for code in selected_codes:
            cdf = peers_df[(peers_df['economy'] == code)].dropna(
                subset=['Gross govt debt (% GDP)']).sort_values('year')
            if cdf.empty:
                continue
            lw = 3 if code == 'KE' else 1.8
            dash = 'solid' if code == 'KE' else 'dot'
            fig7.add_trace(go.Scatter(
                x=cdf['year'],
                y=cdf['Gross govt debt (% GDP)'],
                name=COUNTRY_NAMES.get(code, code),
                mode='lines+markers',
                line=dict(color=COUNTRY_COLORS.get(code, '#888'), width=lw, dash=dash),
                marker=dict(size=5 if code == 'KE' else 3),
                hovertemplate='%{y:.1f}%<extra>' + COUNTRY_NAMES.get(code, code) + '</extra>',
            ))
        fig7.add_hline(
            y=60, line_dash='dash', line_color='rgba(245,166,35,0.4)',
            annotation_text='60% benchmark', annotation_position='top right',
            annotation_font=dict(color='#f5a623', size=9),
        )
        fig7.update_layout(**base_layout('', 420, y_title='% of GDP'))
        st.plotly_chart(fig7, use_container_width=True)

    # Chart 7: Horizontal bar — latest debt/GDP ranking
    with col_b:
        st.markdown("#### Latest Debt / GDP Ranking")
        # Get most recent value per country
        ranking_rows = []
        for code in selected_codes:
            cdf = df[df['economy'] == code].dropna(subset=['Gross govt debt (% GDP)'])
            if not cdf.empty:
                r = cdf.sort_values('year').iloc[-1]
                ranking_rows.append({
                    'economy': code,
                    'country': COUNTRY_NAMES.get(code, code),
                    'Gross govt debt (% GDP)': r['Gross govt debt (% GDP)'],
                    'year': int(r['year']),
                })
        rank_df = pd.DataFrame(ranking_rows).sort_values('Gross govt debt (% GDP)', ascending=True)

        fig8 = go.Figure()
        if not rank_df.empty:
            bar_colors = [KENYA_GREEN if c == 'KE' else 'rgba(66,153,225,0.6)'
                          for c in rank_df['economy']]
            fig8.add_trace(go.Bar(
                x=rank_df['Gross govt debt (% GDP)'],
                y=rank_df['country'],
                orientation='h',
                marker_color=bar_colors,
                marker_line=dict(color='rgba(255,255,255,0.1)', width=0.8),
                text=[f"{v:.1f}% ({y})" for v, y in
                      zip(rank_df['Gross govt debt (% GDP)'], rank_df['year'])],
                textposition='outside',
                textfont=dict(color='#a0aec0', size=11),
                hovertemplate='%{x:.1f}%<extra>%{y}</extra>',
            ))
            fig8.add_vline(
                x=60, line_dash='dash', line_color='rgba(245,166,35,0.5)',
            )
        layout8 = base_layout('', 420, x_title='% of GDP')
        layout8['xaxis']['range'] = [0, rank_df['Gross govt debt (% GDP)'].max() * 1.3 if not rank_df.empty else 100]
        layout8['margin']['r'] = 80
        fig8.update_layout(**layout8)
        st.plotly_chart(fig8, use_container_width=True)

    # Chart 8: Scatter — Revenue vs Expenditure latest year
    st.markdown("#### Revenue vs Expenditure (% GDP) — Latest Available Year per Country")
    scatter_rows = []
    for code in selected_codes:
        cdf = df[df['economy'] == code].dropna(
            subset=['Revenue (% GDP)', 'Expenditure (% GDP)'])
        if not cdf.empty:
            r = cdf.sort_values('year').iloc[-1]
            scatter_rows.append({
                'economy': code,
                'country': COUNTRY_NAMES.get(code, code),
                'Revenue (% GDP)': r['Revenue (% GDP)'],
                'Expenditure (% GDP)': r['Expenditure (% GDP)'],
                'year': int(r['year']),
            })
    scatter_df = pd.DataFrame(scatter_rows)

    fig9 = go.Figure()
    if not scatter_df.empty:
        # Diagonal balance line
        axis_max = max(scatter_df['Revenue (% GDP)'].max(),
                       scatter_df['Expenditure (% GDP)'].max()) * 1.15
        axis_min = min(scatter_df['Revenue (% GDP)'].min(),
                       scatter_df['Expenditure (% GDP)'].min()) * 0.85
        fig9.add_trace(go.Scatter(
            x=[axis_min, axis_max], y=[axis_min, axis_max],
            mode='lines',
            line=dict(color='rgba(255,255,255,0.15)', dash='dot', width=1.5),
            name='Balance line',
            hoverinfo='skip',
        ))
        # Shaded "deficit zone" annotation
        fig9.add_annotation(
            x=(axis_min + axis_max) / 2 + 1.5,
            y=(axis_min + axis_max) / 2 - 1.5,
            text='← Deficit zone',
            showarrow=False,
            font=dict(color='rgba(206,17,38,0.6)', size=10),
            textangle=-35,
        )

        for _, row in scatter_df.iterrows():
            code = row['economy']
            color = COUNTRY_COLORS.get(code, '#888')
            size = 20 if code == 'KE' else 14
            fig9.add_trace(go.Scatter(
                x=[row['Revenue (% GDP)']],
                y=[row['Expenditure (% GDP)']],
                mode='markers+text',
                name=row['country'],
                marker=dict(color=color, size=size,
                            line=dict(color='rgba(255,255,255,0.3)', width=1.5)),
                text=[f"  {row['country']} ({row['year']})"],
                textposition='middle right',
                textfont=dict(color=color, size=11),
                hovertemplate=(
                    f"<b>{row['country']}</b><br>"
                    f"Revenue: {row['Revenue (% GDP)']:.1f}%<br>"
                    f"Expenditure: {row['Expenditure (% GDP)']:.1f}%<br>"
                    f"Gap: {row['Expenditure (% GDP)'] - row['Revenue (% GDP)']:.1f} pp"
                    "<extra></extra>"
                ),
            ))

    layout9 = base_layout('', 420,
                           x_title='Revenue (% GDP)',
                           y_title='Expenditure (% GDP)')
    layout9['showlegend'] = False
    fig9.update_layout(**layout9)
    st.plotly_chart(fig9, use_container_width=True)

    # Insight: fiscal gap comparison
    if not scatter_df.empty and 'KE' in scatter_df['economy'].values:
        ke_row = scatter_df[scatter_df['economy'] == 'KE'].iloc[0]
        gap = ke_row['Expenditure (% GDP)'] - ke_row['Revenue (% GDP)']
        n_worse = sum(
            (r['Expenditure (% GDP)'] - r['Revenue (% GDP)']) > gap
            for _, r in scatter_df.iterrows() if r['economy'] != 'KE'
        )
        n_peers = len(scatter_df) - 1
        st.markdown(f"""
        <div class="insight-box">
          <span class="icon">🌍</span>
          In its most recent year ({int(ke_row['year'])}), Kenya's fiscal gap
          (expenditure minus revenue) was <strong>{gap:.1f} percentage points</strong> of GDP.
          Of the {n_peers} comparison peers shown, <strong>{n_worse}</strong> had a larger gap.
          Countries above the diagonal line are running deficits; countries below are in surplus.
        </div>
        """, unsafe_allow_html=True)

    # Multi-country Revenue trend
    st.markdown("#### Revenue (% GDP) — Cross-Country Trend")
    fig10 = go.Figure()
    for code in selected_codes:
        cdf = peers_df[(peers_df['economy'] == code)].dropna(
            subset=['Revenue (% GDP)']).sort_values('year')
        if cdf.empty:
            continue
        fig10.add_trace(go.Scatter(
            x=cdf['year'], y=cdf['Revenue (% GDP)'],
            name=COUNTRY_NAMES.get(code, code),
            mode='lines+markers',
            line=dict(
                color=COUNTRY_COLORS.get(code, '#888'),
                width=2.5 if code == 'KE' else 1.5,
                dash='solid' if code == 'KE' else 'dot',
            ),
            marker=dict(size=5 if code == 'KE' else 3),
            hovertemplate='%{y:.1f}%<extra>' + COUNTRY_NAMES.get(code, code) + '</extra>',
        ))
    fig10.update_layout(**base_layout('', 320, y_title='% of GDP'))
    st.plotly_chart(fig10, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — EXPORT DATA
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Kenya Data — Full Dataset")

    ke_export = ke_all.copy()

    # Display columns (excluding raw USD to reduce clutter)
    display_cols = [
        'year', 'economy', 'country',
        'Gross govt debt (% GDP)', 'Revenue (% GDP)', 'Expenditure (% GDP)',
        'Fiscal balance (% GDP)', 'Fiscal gap (% GDP)',
        'Interest payments (% expense)',
        'External debt (% GNI)', 'External debt stocks (USD bn)',
        'Total debt service (% GNI)',
        'Net ODA received (USD bn)', 'GDP (USD bn)',
    ]
    display_cols = [c for c in display_cols if c in ke_export.columns]
    ke_display = ke_export[display_cols].sort_values('year', ascending=False)

    st.dataframe(
        ke_display.style.format({
            col: '{:.1f}' for col in ke_display.select_dtypes('float').columns
        }),
        use_container_width=True,
        height=420,
    )

    st.markdown("### Full Dataset (All Countries)")
    all_display_cols = [
        'year', 'economy', 'country',
        'Gross govt debt (% GDP)', 'Revenue (% GDP)', 'Expenditure (% GDP)',
        'Fiscal balance (% GDP)', 'External debt (% GNI)',
        'Total debt service (% GNI)', 'GDP (USD bn)',
    ]
    all_display_cols = [c for c in all_display_cols if c in df.columns]
    all_display = df[all_display_cols].sort_values(['economy', 'year'], ascending=[True, False])
    st.dataframe(
        all_display.style.format({
            col: '{:.1f}' for col in all_display.select_dtypes('float').columns
        }),
        use_container_width=True,
        height=350,
    )

    # Excel download
    st.markdown("### Download")
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        buf_ke = io.BytesIO()
        with pd.ExcelWriter(buf_ke, engine='openpyxl') as writer:
            ke_display.to_excel(writer, sheet_name='Kenya', index=False)
        buf_ke.seek(0)
        st.download_button(
            label="📥 Download Kenya Data (Excel)",
            data=buf_ke,
            file_name="kenya_fiscal_intelligence.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col_dl2:
        buf_all = io.BytesIO()
        with pd.ExcelWriter(buf_all, engine='openpyxl') as writer:
            ke_display.to_excel(writer, sheet_name='Kenya', index=False)
            for code in ['UG', 'TZ', 'ET', 'RW']:
                cname = COUNTRY_NAMES.get(code, code)
                c_df = df[df['economy'] == code][all_display_cols].sort_values('year', ascending=False)
                c_df.to_excel(writer, sheet_name=cname, index=False)
        buf_all.seek(0)
        st.download_button(
            label="📥 Download All Countries (Excel)",
            data=buf_all,
            file_name="eac_fiscal_intelligence.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.markdown("---")
    st.caption("**Data sources:** IMF DataMapper API (fiscal aggregates) · World Bank Open Data API (external debt, GDP, ODA)")
    st.caption("**Indicators:** General govt gross debt, Revenue, Expenditure, Fiscal balance (IMF WEO) · External debt, Debt service, ODA, GDP (WB)")
    st.caption("**Coverage:** 2000–2024 · Kenya, Uganda, Tanzania, Ethiopia, Rwanda")
