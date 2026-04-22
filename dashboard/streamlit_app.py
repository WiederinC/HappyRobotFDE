"""
Acme Logistics · HappyRobot Agent Dashboard
Analytics + Operations · Streamlit
"""
import os
import html as html_lib
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Acme Logistics · Agent Dashboard",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = os.getenv("API_URL", "https://happyrobot-carrier-production.up.railway.app")
API_KEY = os.getenv("API_KEY", "hr-dev-key-change-in-prod")
HEADERS = {"X-API-Key": API_KEY}

# ── Palette ────────────────────────────────────────────────────────────────────
C = dict(
    blue="#2563EB", blue_light="#DBEAFE",
    green="#16A34A", green_light="#DCFCE7",
    red="#DC2626", red_light="#FEE2E2",
    amber="#D97706", amber_light="#FEF3C7",
    gray="#6B7280", gray_light="#F3F4F6",
    text="#111827", subtext="#6B7280",
    bg="#F9FAFB", card="#FFFFFF",
    border="#E5E7EB",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Page */
  [data-testid="stAppViewContainer"] {{background:{C['bg']};}}
  [data-testid="stHeader"] {{background:{C['bg']};}}
  section[data-testid="stSidebar"] {{display:none;}}
  .block-container {{padding:2rem 2.5rem 4rem;max-width:1400px;}}

  /* Typography */
  .page-title {{font-size:24px;font-weight:700;color:{C['text']};margin:0;}}
  .page-sub   {{font-size:14px;color:{C['subtext']};margin:0 0 1.5rem;}}
  .sec-label  {{font-size:11px;font-weight:700;letter-spacing:.08em;
                text-transform:uppercase;color:{C['subtext']};margin:1.4rem 0 .6rem;}}

  /* KPI cards */
  .kpi-grid   {{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:1rem;}}
  .kpi        {{background:{C['card']};border:1px solid {C['border']};border-radius:14px;
                padding:18px 20px;}}
  .kpi-label  {{font-size:12px;color:{C['subtext']};font-weight:500;margin-bottom:4px;}}
  .kpi-val    {{font-size:28px;font-weight:700;color:{C['text']};line-height:1;}}
  .kpi-sub    {{font-size:12px;color:{C['subtext']};margin-top:4px;}}
  .kpi-val.green{{color:{C['green']};}} .kpi-val.blue{{color:{C['blue']};}}
  .kpi-val.red  {{color:{C['red']};}}  .kpi-val.amber{{color:{C['amber']};}}

  /* Chart cards */
  .cc  {{background:{C['card']};border:1px solid {C['border']};border-radius:14px;
         padding:18px 20px 8px;height:100%;}}
  .ct  {{font-size:14px;font-weight:600;color:{C['text']};margin-bottom:2px;}}
  .cs  {{font-size:12px;color:{C['subtext']};margin-bottom:10px;}}

  /* Table */
  .tw  {{overflow-x:auto;border-radius:14px;border:1px solid {C['border']};}}
  .tbl {{border-collapse:collapse;width:100%;font-size:13px;}}
  .tbl thead tr {{background:{C['gray_light']};}}
  .tbl th {{padding:10px 14px;text-align:left;font-size:11px;font-weight:700;
            letter-spacing:.05em;text-transform:uppercase;color:{C['subtext']};
            white-space:nowrap;border-bottom:1px solid {C['border']};}}
  .tbl td {{padding:10px 14px;color:{C['text']};border-bottom:1px solid {C['border']};
            white-space:nowrap;vertical-align:middle;}}
  .tbl tr:last-child td {{border-bottom:none;}}
  .tbl tr:hover td {{background:#F8FAFF;}}
  .bold {{font-weight:600;}}
  .mono {{font-family:monospace;font-size:12px;}}

  /* Badges */
  .badge {{display:inline-block;border-radius:999px;padding:2px 10px;
           font-size:11px;font-weight:600;white-space:nowrap;}}
  .booked    {{background:{C['green_light']};color:{C['green']};}}
  .no_deal   {{background:{C['gray_light']};color:{C['gray']};}}
  .declined  {{background:{C['red_light']};color:{C['red']};}}
  .ineligible{{background:{C['amber_light']};color:{C['amber']};}}
  .positive  {{background:{C['green_light']};color:{C['green']};}}
  .neutral   {{background:{C['gray_light']};color:{C['gray']};}}
  .negative  {{background:{C['red_light']};color:{C['red']};}}
  .rate-hold {{background:{C['red_light']};color:{C['red']};}}
  .waitlist  {{background:{C['amber_light']};color:{C['amber']};}}
  .available {{background:{C['green_light']};color:{C['green']};}}
  .booked-load{{background:{C['gray_light']};color:{C['gray']};}}

  /* Insight cards */
  .insight {{border-radius:12px;padding:14px 16px;margin-bottom:6px;display:flex;gap:10px;align-items:flex-start;}}
  .insight-success{{background:{C['green_light']};border-left:3px solid {C['green']};}}
  .insight-warning{{background:{C['amber_light']};border-left:3px solid {C['amber']};}}
  .insight-info   {{background:{C['blue_light']};border-left:3px solid {C['blue']};}}
  .insight-icon   {{font-size:18px;}}
  .insight-title  {{font-weight:600;font-size:13px;color:{C['text']};}}
  .insight-msg    {{font-size:12px;color:{C['subtext']};margin-top:2px;}}

  /* Ops cards */
  .ops-card {{background:{C['card']};border:1px solid {C['border']};border-radius:14px;
              padding:16px 20px;margin-bottom:10px;}}
  .ops-header {{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}}
  .ops-title  {{font-weight:700;font-size:15px;color:{C['text']};}}
  .ops-meta   {{font-size:12px;color:{C['subtext']};}}
  .ops-detail {{font-size:13px;color:{C['text']};}}
  .ops-sub    {{font-size:12px;color:{C['subtext']};margin-top:3px;}}

  /* Divider */
  .hr {{border:none;border-top:1px solid {C['border']};margin:1.2rem 0;}}

  /* Tabs */
  [data-testid="stTabs"] button {{font-size:14px;font-weight:500;}}
  [data-testid="stTabs"] button[aria-selected="true"] {{font-weight:700;}}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch(path):
    try:
        r = requests.get(f"{API_URL}{path}", headers=HEADERS, timeout=8)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def badge(label, cls):
    return f'<span class="badge {cls}">{html_lib.escape(str(label))}</span>'

def fmt_money(v):
    if v is None: return "—"
    try: return f"${float(v):,.0f}"
    except: return "—"

def fmt_time(s):
    if not s: return "—"
    try:
        dt = datetime.fromisoformat(s.replace("Z",""))
        return dt.strftime("%-m/%-d %H:%M")
    except: return s[:16]

def esc(v):
    return html_lib.escape(str(v)) if v else "—"

BASE_CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color=C["text"]),
    margin=dict(l=0, r=0, t=10, b=0),
)

# ── Header ─────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([6, 1])
with h1:
    st.markdown('<div class="page-title">🚛 Acme Logistics · Agent Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">HappyRobot AI · Live data · Refreshes every 30s</div>', unsafe_allow_html=True)
with h2:
    if st.button("↻  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Fetch all data ─────────────────────────────────────────────────────────────
m, err_m         = fetch("/metrics/")
calls,  err_c    = fetch("/calls/")
loads,  _        = fetch("/loads/")
waitlist, _      = fetch("/waitlist/")
matches, _       = fetch("/matches/")

if err_m or err_c:
    st.error(f"⚠️  Cannot reach API — {err_m or err_c}")
    st.stop()

calls    = calls    or []
loads    = loads    or []
waitlist = (waitlist or {}).get("entries", [])
matches  = (matches  or {}).get("matches", [])

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_analytics, tab_operations = st.tabs(["📊  Analytics", "⚙️  Operations"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab_analytics:

    # KPI row
    total   = m.get("total_calls", 0)
    booked  = m.get("booked", 0)
    br      = m.get("booking_rate", 0)
    rev     = m.get("revenue_booked", 0)
    rpc     = m.get("revenue_per_call", 0)
    rc      = m.get("rate_compression_pct", 0)
    risk    = m.get("revenue_at_risk", 0)
    avg_neg = m.get("avg_negotiations", 0)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-label">Total Calls</div>
        <div class="kpi-val blue">{total}</div>
        <div class="kpi-sub">{booked} booked</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Booking Rate</div>
        <div class="kpi-val {'green' if br>=50 else 'red'}">{br:.1f}%</div>
        <div class="kpi-sub">Target ≥ 50%</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Revenue Booked</div>
        <div class="kpi-val green">${rev:,.0f}</div>
        <div class="kpi-sub">${rpc:,.0f} per call</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Revenue at Risk</div>
        <div class="kpi-val {'amber' if risk>0 else 'green'}">${risk:,.0f}</div>
        <div class="kpi-sub">Unconverted loads</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Rate Compression</div>
        <div class="kpi-val blue">{rc:.1f}%</div>
        <div class="kpi-sub">Avg {avg_neg:.1f} negotiation rounds</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts row 1: Outcomes | Sentiment | Daily volume
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="cc"><div class="ct">Call Outcomes</div><div class="cs">Distribution across all calls</div>', unsafe_allow_html=True)
        outcomes = m.get("outcomes", {})
        if outcomes:
            labels = [k.replace("_"," ").title() for k in outcomes]
            values = list(outcomes.values())
            colors = [C["green"] if "booked" in k else C["red"] if "declined" in k
                      else C["amber"] if "ineligible" in k else C["gray"]
                      for k in outcomes]
            fig = go.Figure(go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors, line=dict(color="#fff", width=2)),
                hole=0.6, textinfo="none",
                hovertemplate="%{label}: <b>%{value}</b><extra></extra>",
            ))
            fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:11px'>calls</span>",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(size=20, color=C["text"]))
            fig.update_layout(**BASE_CHART, showlegend=True, height=230,
                              legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                                          font=dict(size=11)))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="cc"><div class="ct">Carrier Sentiment</div><div class="cs">Tone across all calls</div>', unsafe_allow_html=True)
        sentiments = m.get("sentiments", {})
        if sentiments:
            sl = list(sentiments.keys())
            sv = list(sentiments.values())
            sc = {"positive": C["green"], "neutral": C["gray"], "negative": C["red"]}
            fig2 = go.Figure(go.Bar(
                x=[l.title() for l in sl], y=sv,
                marker=dict(color=[sc.get(l, C["gray"]) for l in sl],
                            line=dict(width=0), cornerradius=8),
                text=sv, textposition="outside",
                textfont=dict(size=13, color=C["text"], weight=600),
                hovertemplate="%{x}: <b>%{y}</b><extra></extra>",
            ))
            fig2.update_layout(**BASE_CHART, showlegend=False, height=230, bargap=0.35,
                               xaxis=dict(showgrid=False, showline=False, tickfont=dict(size=13)),
                               yaxis=dict(showgrid=False, visible=False))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="cc"><div class="ct">Daily Call Volume</div><div class="cs">Agent activity trend</div>', unsafe_allow_html=True)
        daily = m.get("daily_calls", [])
        if daily:
            df_d = pd.DataFrame(daily)
            df_d["date"] = pd.to_datetime(df_d["date"])
            fig3 = go.Figure(go.Scatter(
                x=df_d["date"], y=df_d["count"], mode="lines",
                line=dict(color=C["blue"], width=2.5, shape="spline"),
                fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
                hovertemplate="%{x|%b %-d}: <b>%{y} calls</b><extra></extra>",
            ))
            fig3.update_layout(**BASE_CHART, height=230,
                               xaxis=dict(showgrid=False, showline=False,
                                          tickfont=dict(size=11), tickformat="%b %-d"),
                               yaxis=dict(showgrid=True, gridcolor=C["border"],
                                          tickfont=dict(size=11)))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Charts row 2: Negotiation rounds | Lane performance
    c4, c5 = st.columns([1, 2])

    with c4:
        st.markdown('<div class="cc"><div class="ct">Negotiation Rounds</div><div class="cs">How many rounds to close</div>', unsafe_allow_html=True)
        neg_dist = m.get("negotiations_distribution", {})
        if neg_dist:
            nx = [f"{k} round{'s' if k!='1' else ''}" for k in neg_dist]
            ny = list(neg_dist.values())
            fig4 = go.Figure(go.Bar(
                x=nx, y=ny,
                marker=dict(color=C["blue"], line=dict(width=0), cornerradius=8),
                text=ny, textposition="outside",
                textfont=dict(size=12, color=C["text"], weight=600),
                hovertemplate="%{x}: <b>%{y} calls</b><extra></extra>",
            ))
            fig4.update_layout(**BASE_CHART, showlegend=False, height=220, bargap=0.4,
                               xaxis=dict(showgrid=False, showline=False, tickfont=dict(size=11)),
                               yaxis=dict(showgrid=False, visible=False))
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="cc"><div class="ct">Lane Performance</div><div class="cs">Booking rate and avg rate by route</div>', unsafe_allow_html=True)
        lanes = m.get("lane_performance", [])
        if lanes:
            df_l = pd.DataFrame(lanes)
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(
                name="Booking Rate %",
                x=df_l["route"], y=df_l["booking_rate"],
                marker=dict(color=C["blue"], cornerradius=6, line=dict(width=0)),
                yaxis="y", hovertemplate="%{x}<br>Booking rate: <b>%{y:.0f}%</b><extra></extra>",
            ))
            fig5.add_trace(go.Scatter(
                name="Avg Rate $",
                x=df_l["route"], y=df_l["avg_rate"],
                mode="markers", marker=dict(color=C["green"], size=10, symbol="diamond"),
                yaxis="y2", hovertemplate="%{x}<br>Avg rate: <b>$%{y:,.0f}</b><extra></extra>",
            ))
            fig5.update_layout(
                **BASE_CHART, height=220, bargap=0.35,
                showlegend=True,
                legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(size=11)),
                xaxis=dict(showgrid=False, tickfont=dict(size=9), tickangle=-20),
                yaxis=dict(showgrid=True, gridcolor=C["border"], tickfont=dict(size=10),
                           title="Booking %", titlefont=dict(size=10)),
                yaxis2=dict(overlaying="y", side="right", tickfont=dict(size=10),
                            title="Avg Rate $", titlefont=dict(size=10), showgrid=False,
                            tickprefix="$"),
            )
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Insights
    insights = m.get("insights", [])
    if insights:
        st.markdown('<div class="sec-label">Actionable Insights</div>', unsafe_allow_html=True)
        type_map = {
            "success": ("✅", "insight-success"),
            "warning": ("⚠️", "insight-warning"),
            "info":    ("💡", "insight-info"),
        }
        cols_ins = st.columns(min(len(insights), 3))
        for i, ins in enumerate(insights[:3]):
            icon, cls = type_map.get(ins["type"], ("💡", "insight-info"))
            with cols_ins[i % 3]:
                st.markdown(f"""
                <div class="insight {cls}">
                  <span class="insight-icon">{icon}</span>
                  <div>
                    <div class="insight-title">{esc(ins['title'])}</div>
                    <div class="insight-msg">{esc(ins['message'])}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Call log table
    st.markdown('<div class="sec-label">Call Log · Agent Activity</div>', unsafe_allow_html=True)
    OUTCOME_MAP = {
        "booked":             ("booked",     "✓ Booked"),
        "declined":           ("declined",   "✕ Declined"),
        "no_deal":            ("no_deal",    "— No Deal"),
        "carrier_ineligible": ("ineligible", "⚠ Ineligible"),
        "rate_hold":          ("rate-hold",  "⏸ Rate Hold"),
        "waitlisted":         ("waitlist",   "📋 Waitlist"),
    }
    SENT_MAP = {
        "positive": ("positive", "😊 Positive"),
        "neutral":  ("neutral",  "😐 Neutral"),
        "negative": ("negative", "😞 Negative"),
    }
    if calls:
        rows = ""
        for c in calls[:100]:
            oc, ol = OUTCOME_MAP.get(c.get("outcome",""), ("no_deal", c.get("outcome","")))
            sc, sl = SENT_MAP.get(c.get("sentiment",""), ("neutral", c.get("sentiment","")))
            rows += f"""<tr>
              <td style="color:{C['subtext']};font-size:12px">{fmt_time(c.get('created_at',''))}</td>
              <td class="bold">{esc(c.get('carrier_name') or '—')}</td>
              <td><span class="mono">{esc(c.get('carrier_mc') or '—')}</span></td>
              <td><span class="mono">{esc(c.get('load_id') or '—')}</span></td>
              <td>{fmt_money(c.get('loadboard_rate'))}</td>
              <td style="color:{C['subtext']}">{fmt_money(c.get('initial_offer'))}</td>
              <td class="bold">{fmt_money(c.get('agreed_rate'))}</td>
              <td style="text-align:center;font-weight:600">{c.get('num_negotiations',0)}</td>
              <td>{badge(ol, oc)}</td>
              <td>{badge(sl, sc)}</td>
            </tr>"""
        st.markdown(f"""
        <div class="tw"><table class="tbl"><thead><tr>
          <th>Time</th><th>Carrier</th><th>MC #</th><th>Load</th>
          <th>Board Rate</th><th>1st Offer</th><th>Agreed Rate</th>
          <th style="text-align:center">Rounds</th><th>Outcome</th><th>Sentiment</th>
        </tr></thead><tbody>{rows}</tbody></table></div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;padding:3rem;color:{C["subtext"]}">No calls recorded yet</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_operations:

    ops_c1, ops_c2 = st.columns([1, 1])

    # ── Left column: Available Loads ──────────────────────────────────────────
    with ops_c1:
        available = [l for l in loads if l.get("status") == "available"]
        booked_loads = [l for l in loads if l.get("status") != "available"]

        st.markdown(f'<div class="sec-label">Available Loads ({len(available)})</div>', unsafe_allow_html=True)

        if available:
            for ld in sorted(available, key=lambda x: x.get("pickup_datetime","")):
                rpm = round(ld["loadboard_rate"] / ld["miles"], 2) if ld.get("miles") else 0
                pickup = ld.get("pickup_datetime","")[:16]
                st.markdown(f"""
                <div class="ops-card" style="border-left:3px solid {C['green']};">
                  <div class="ops-header">
                    <div>
                      <span class="ops-title">{esc(ld['origin'])} → {esc(ld['destination'])}</span>
                      <span style="margin-left:8px;">{badge('Available','available')}</span>
                    </div>
                    <div style="text-align:right;">
                      <div style="font-size:16px;font-weight:700;color:{C['green']};">{fmt_money(ld['loadboard_rate'])}</div>
                      <div style="font-size:11px;color:{C['subtext']};">${rpm}/mi</div>
                    </div>
                  </div>
                  <div class="ops-detail">
                    <span style="color:{C['subtext']}">{esc(ld.get('equipment_type',''))} · {esc(ld.get('commodity_type',''))} · {esc(str(int(ld['miles']))) if ld.get('miles') else '—'} mi</span>
                  </div>
                  <div class="ops-sub">📅 Pickup {pickup} &nbsp;·&nbsp; <span class="mono">{esc(ld['load_id'])}</span></div>
                  {f'<div class="ops-sub" style="margin-top:4px;color:{C["subtext"]}">{esc(ld["notes"])}</div>' if ld.get("notes") else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="padding:2rem;text-align:center;color:{C["subtext"]}">No available loads</div>', unsafe_allow_html=True)

        if booked_loads:
            st.markdown(f'<div class="sec-label" style="margin-top:1rem;">Booked / Unavailable ({len(booked_loads)})</div>', unsafe_allow_html=True)
            for ld in booked_loads[:5]:
                st.markdown(f"""
                <div class="ops-card" style="border-left:3px solid {C['border']};opacity:0.7;">
                  <div class="ops-header">
                    <div>
                      <span style="font-weight:600;font-size:14px;color:{C['subtext']}">{esc(ld['origin'])} → {esc(ld['destination'])}</span>
                      <span style="margin-left:8px;">{badge('Booked','booked-load')}</span>
                    </div>
                    <div style="font-size:14px;font-weight:600;color:{C['subtext']}">{fmt_money(ld['loadboard_rate'])}</div>
                  </div>
                  <div style="font-size:12px;color:{C['subtext']}">{esc(ld.get('equipment_type',''))} · <span class="mono">{esc(ld['load_id'])}</span></div>
                </div>
                """, unsafe_allow_html=True)

    # ── Right column: Waitlist + Callback Opportunities ───────────────────────
    with ops_c2:

        # Callback opportunities (waitlist matched to loads)
        st.markdown(f'<div class="sec-label">🔥 Callback Opportunities ({len(matches)})</div>', unsafe_allow_html=True)
        if matches:
            for mx in matches:
                for wc in mx["waiting_carriers"]:
                    is_rate_hold = wc["entry_type"] == "rate_hold"
                    tag_cls   = "rate-hold" if is_rate_hold else "waitlist"
                    tag_label = "Rate Hold"  if is_rate_hold else "Waitlist"
                    border_c  = C["red"]     if is_rate_hold else C["amber"]

                    carrier_ask = wc.get("carrier_ask_rate","")
                    try:
                        rate_line = f'Carrier asked {fmt_money(float(carrier_ask))} · Board {fmt_money(mx["loadboard_rate"])}' if carrier_ask else f'Board {fmt_money(mx["loadboard_rate"])}'
                    except:
                        rate_line = f'Board {fmt_money(mx["loadboard_rate"])}'

                    avail = esc(wc.get("availability_window","")) if wc.get("availability_window") else ""

                    st.markdown(f"""
                    <div class="ops-card" style="border-left:4px solid {border_c};">
                      <div class="ops-header">
                        <div>
                          <span class="ops-title">{esc(mx['origin'])} → {esc(mx['destination'])}</span>
                          <span style="margin-left:8px;">{badge(tag_label, tag_cls)}</span>
                        </div>
                        <div style="font-size:12px;color:{C['subtext']}">{esc(mx['equipment_type'])} · {mx['pickup_datetime'][:10]}</div>
                      </div>
                      <div class="ops-detail">MC <strong>{esc(wc['carrier_mc'])}</strong> · {rate_line}</div>
                      {f'<div class="ops-sub">Available: {avail}</div>' if avail else ""}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="padding:1.5rem;text-align:center;color:{C["subtext"]}">No callback opportunities right now</div>', unsafe_allow_html=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        # Full waitlist
        rate_holds  = [e for e in waitlist if e["entry_type"] == "rate_hold"]
        lane_waits  = [e for e in waitlist if e["entry_type"] == "lane_unavailable"]

        st.markdown(f'<div class="sec-label">Rate Holds ({len(rate_holds)})</div>', unsafe_allow_html=True)
        if rate_holds:
            rows_rh = ""
            for e in rate_holds:
                rows_rh += f"""<tr>
                  <td>{esc(e.get('origin',''))} → {esc(e.get('destination',''))}</td>
                  <td><span class="mono">{esc(e.get('carrier_mc',''))}</span></td>
                  <td style="font-weight:600">{fmt_money(e.get('carrier_ask_rate'))}</td>
                  <td style="color:{C['subtext']};font-size:12px">{fmt_time(e.get('created_at',''))}</td>
                </tr>"""
            st.markdown(f"""
            <div class="tw"><table class="tbl"><thead><tr>
              <th>Lane</th><th>MC #</th><th>Carrier Ask</th><th>Added</th>
            </tr></thead><tbody>{rows_rh}</tbody></table></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="padding:1rem;color:{C["subtext"]};font-size:13px">No rate holds</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sec-label" style="margin-top:1rem;">Lane Waitlist ({len(lane_waits)})</div>', unsafe_allow_html=True)
        if lane_waits:
            rows_lw = ""
            for e in lane_waits:
                rows_lw += f"""<tr>
                  <td>{esc(e.get('origin',''))} → {esc(e.get('destination',''))}</td>
                  <td><span class="mono">{esc(e.get('carrier_mc',''))}</span></td>
                  <td style="color:{C['subtext']};font-size:12px">{esc(e.get('availability_window',''))}</td>
                  <td style="color:{C['subtext']};font-size:12px">{fmt_time(e.get('created_at',''))}</td>
                </tr>"""
            st.markdown(f"""
            <div class="tw"><table class="tbl"><thead><tr>
              <th>Lane</th><th>MC #</th><th>Availability</th><th>Added</th>
            </tr></thead><tbody>{rows_lw}</tbody></table></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="padding:1rem;color:{C["subtext"]};font-size:13px">No lane waitlist entries</div>', unsafe_allow_html=True)

        # Carrier value table
        carrier_value = m.get("carrier_value", [])
        if carrier_value:
            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-label">Top Carriers by Revenue</div>', unsafe_allow_html=True)
            rows_cv = ""
            for cv in carrier_value[:8]:
                rows_cv += f"""<tr>
                  <td class="bold">{esc(cv.get('carrier_name',''))}</td>
                  <td><span class="mono">{esc(cv.get('carrier_mc',''))}</span></td>
                  <td style="text-align:center">{cv.get('calls',0)}</td>
                  <td style="text-align:center">{cv.get('bookings',0)}</td>
                  <td style="text-align:center;font-weight:600;color:{C['blue']}">{cv.get('booking_rate',0):.0f}%</td>
                  <td style="font-weight:700;color:{C['green']}">{fmt_money(cv.get('total_revenue'))}</td>
                </tr>"""
            st.markdown(f"""
            <div class="tw"><table class="tbl"><thead><tr>
              <th>Carrier</th><th>MC #</th>
              <th style="text-align:center">Calls</th>
              <th style="text-align:center">Booked</th>
              <th style="text-align:center">Rate</th>
              <th>Revenue</th>
            </tr></thead><tbody>{rows_cv}</tbody></table></div>
            """, unsafe_allow_html=True)
