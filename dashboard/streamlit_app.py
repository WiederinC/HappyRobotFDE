import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="HappyRobot Freight · Analytics",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"],[class*="st-"]{
    font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter",sans-serif!important;
    background:#F2F2F7!important; color:#1D1D1F!important;
}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2.5rem 3rem!important;max-width:1440px!important;}

/* header */
.app-title{font-size:30px;font-weight:700;letter-spacing:-.8px;color:#1D1D1F;line-height:1.1;}
.app-sub{font-size:14px;color:#8E8E93;margin-top:4px;}
.live-pill{display:inline-flex;align-items:center;gap:6px;background:#F0FFF4;color:#1A7A3C;
    font-size:12px;font-weight:600;padding:6px 14px;border-radius:980px;border:1px solid #C6F6D5;}
.live-dot{width:7px;height:7px;background:#34C759;border-radius:50%;display:inline-block;
    animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px rgba(52,199,89,.3);}
    50%{box-shadow:0 0 0 5px rgba(52,199,89,.1);}}

/* section */
.sec-label{font-size:11px;font-weight:600;color:#8E8E93;text-transform:uppercase;
    letter-spacing:.8px;margin:2rem 0 .75rem 2px;}
.hr{height:1px;background:#C7C7CC;margin:1.75rem 0;}

/* insight cards */
.insight{border-radius:14px;padding:14px 18px;margin-bottom:10px;
    display:flex;align-items:flex-start;gap:12px;}
.insight-success{background:#F0FFF4;border-left:4px solid #34C759;}
.insight-warning{background:#FFFBEB;border-left:4px solid #FF9500;}
.insight-info   {background:#EFF6FF;border-left:4px solid #0071E3;}
.insight-icon{font-size:18px;line-height:1;margin-top:1px;}
.insight-title{font-size:13px;font-weight:600;color:#1D1D1F;margin-bottom:2px;}
.insight-msg{font-size:12px;color:#6E6E73;line-height:1.5;}

/* revenue band */
.rev-band{background:#1D1D1F;border-radius:18px;padding:24px 28px;
    display:flex;justify-content:space-between;align-items:center;margin-bottom:0;}
.rev-item{text-align:center;}
.rev-label{font-size:11px;font-weight:500;color:#8E8E93;text-transform:uppercase;
    letter-spacing:.6px;margin-bottom:6px;}
.rev-value{font-size:28px;font-weight:700;letter-spacing:-1px;color:#FFFFFF;}
.rev-value.green{color:#30D158;}
.rev-value.red  {color:#FF453A;}
.rev-value.blue {color:#64D2FF;}
.rev-divider{width:1px;height:50px;background:#3A3A3C;}

/* kpi card */
.kpi{background:#FFFFFF;border-radius:18px;padding:20px 20px 18px;
    box-shadow:0 1px 3px rgba(0,0,0,.07),0 1px 2px rgba(0,0,0,.04);
    border:1px solid rgba(0,0,0,.05);height:100%;}
.kpi-icon{font-size:20px;margin-bottom:10px;display:block;line-height:1;}
.kpi-label{font-size:11px;font-weight:600;color:#8E8E93;text-transform:uppercase;
    letter-spacing:.6px;margin-bottom:6px;}
.kpi-value{font-size:30px;font-weight:700;letter-spacing:-1px;color:#1D1D1F;line-height:1;}
.kpi-sub{font-size:12px;color:#8E8E93;margin-top:5px;}
.a-blue {border-top:3px solid #0071E3;}
.a-green{border-top:3px solid #34C759;}
.a-teal {border-top:3px solid #5AC8FA;}
.a-indigo{border-top:3px solid #5856D6;}
.a-orange{border-top:3px solid #FF9500;}
.a-purple{border-top:3px solid #AF52DE;}
.a-red  {border-top:3px solid #FF3B30;}
.v-blue {color:#0071E3!important;}
.v-green{color:#1A7A3C!important;}
.v-red  {color:#D70015!important;}

/* chart card */
.cc{background:#FFFFFF;border-radius:18px;padding:22px 22px 8px;
    box-shadow:0 1px 3px rgba(0,0,0,.07),0 1px 2px rgba(0,0,0,.04);
    border:1px solid rgba(0,0,0,.05);}
.ct{font-size:14px;font-weight:600;color:#1D1D1F;margin-bottom:2px;letter-spacing:-.2px;}
.cs{font-size:12px;color:#8E8E93;margin-bottom:14px;}

/* table */
.tw{background:#FFFFFF;border-radius:18px;overflow:hidden;
    box-shadow:0 1px 3px rgba(0,0,0,.07);border:1px solid rgba(0,0,0,.05);}
.tbl{width:100%;border-collapse:collapse;font-size:13px;}
.tbl th{text-align:left;padding:11px 16px;font-size:11px;font-weight:600;color:#8E8E93;
    text-transform:uppercase;letter-spacing:.5px;background:#FAFAFA;
    border-bottom:1px solid #E5E5EA;white-space:nowrap;}
.tbl td{padding:12px 16px;border-bottom:1px solid #F2F2F7;vertical-align:middle;}
.tbl tr:last-child td{border-bottom:none;}
.tbl tr:hover td{background:#F9F9FB;}
.badge{display:inline-flex;align-items:center;padding:3px 10px;border-radius:980px;
    font-size:11px;font-weight:600;white-space:nowrap;}
.b-booked   {background:#E8F9EE;color:#1A7A3C;}
.b-declined {background:#FFF4E5;color:#C15900;}
.b-no_deal  {background:#F2F2F7;color:#6E6E73;}
.b-ineligible{background:#FFF0F0;color:#D70015;}
.b-positive {background:#EFF6FF;color:#1B4F9E;}
.b-neutral  {background:#F2F2F7;color:#6E6E73;}
.b-negative {background:#FFF0F0;color:#D70015;}
.mono{font-family:"SF Mono","Menlo","Fira Code",monospace;font-size:12px;color:#6E6E73;}
.bold{font-weight:600;}

/* button */
div[data-testid="stButton"]>button{
    background:#0071E3!important;color:#fff!important;border:none!important;
    border-radius:980px!important;padding:9px 22px!important;font-size:14px!important;
    font-weight:500!important;box-shadow:0 1px 3px rgba(0,113,227,.4)!important;
    transition:all .15s!important;}
div[data-testid="stButton"]>button:hover{
    background:#0077ED!important;transform:translateY(-1px)!important;}
div[data-testid="stTextInput"] input{border-radius:10px!important;
    border:1px solid #C7C7CC!important;font-size:14px!important;
    padding:8px 14px!important;background:#FFFFFF!important;}
.footer{text-align:center;color:#8E8E93;font-size:12px;margin-top:3rem;
    padding-top:1.25rem;border-top:1px solid #C7C7CC;}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
C = {"blue":"#0071E3","green":"#34C759","red":"#FF3B30","orange":"#FF9500",
     "gray":"#8E8E93","indigo":"#5856D6","purple":"#AF52DE","teal":"#5AC8FA"}

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter'",
              color="#1D1D1F", size=12),
    margin=dict(l=0,r=0,t=8,b=0), showlegend=False,
)

def fmt(v, prefix="$"):
    if v is None: return "—"
    return f"{prefix}{v:,.0f}" if prefix else f"{v:,.0f}"

def fmt_time(ts):
    try: return datetime.fromisoformat(ts).strftime("%-d %b · %-I:%M %p")
    except: return ts or "—"

def badge(text, cls):
    return f'<span class="badge b-{cls}">{text}</span>'

def kpi(icon, label, value, acc, vcls="", sub=""):
    s = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    v = f"kpi-value {vcls}" if vcls else "kpi-value"
    return f"""<div class="kpi a-{acc}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="{v}">{value}</div>{s}</div>"""

def fetch(path, url, key):
    try:
        r = requests.get(f"{url.rstrip('/')}{path}",
                         headers={"X-API-Key":key}, timeout=8)
        r.raise_for_status(); return r.json(), None
    except Exception as e: return None, str(e)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_url = st.text_input("API URL", value=os.getenv("API_URL","http://localhost:8000"))
    api_key = st.text_input("API Key", value=os.getenv("API_KEY","hr-dev-key-change-in-prod"), type="password")
    st.markdown("---"); st.caption("HappyRobot Carrier Analytics · v2.0")

# ── Header ─────────────────────────────────────────────────────────────────────
h1,h2 = st.columns([5,1])
with h1:
    st.markdown("""<div style="margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid #C7C7CC;
        display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
            <div class="app-title">🚛 Carrier Analytics</div>
            <div class="app-sub">HappyRobot Freight · Inbound Sales Operations Dashboard</div>
        </div>
        <div class="live-pill"><span class="live-dot"></span> Live</div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.button("↻  Refresh")

# ── Fetch ──────────────────────────────────────────────────────────────────────
m, e1 = fetch("/metrics/", api_url, api_key)
calls_raw, e2 = fetch("/calls/", api_url, api_key)
if e1 or e2:
    st.error(f"⚠️  Cannot reach API — {e1 or e2}"); st.stop()

# ── Revenue Band ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Revenue Impact</div>', unsafe_allow_html=True)
rev_booked  = m.get("revenue_booked", 0)
rev_risk    = m.get("revenue_at_risk", 0)
rev_per_call= m.get("revenue_per_call", 0)
booking_rate= m.get("booking_rate", 0)
rate_comp   = m.get("rate_compression_pct", 0)

st.markdown(f"""
<div class="rev-band">
    <div class="rev-item">
        <div class="rev-label">Revenue Booked</div>
        <div class="rev-value green">${rev_booked:,.0f}</div>
    </div>
    <div class="rev-divider"></div>
    <div class="rev-item">
        <div class="rev-label">Revenue at Risk</div>
        <div class="rev-value red">${rev_risk:,.0f}</div>
    </div>
    <div class="rev-divider"></div>
    <div class="rev-item">
        <div class="rev-label">Revenue per Call</div>
        <div class="rev-value blue">${rev_per_call:,.0f}</div>
    </div>
    <div class="rev-divider"></div>
    <div class="rev-item">
        <div class="rev-label">Booking Rate</div>
        <div class="rev-value {'green' if booking_rate>=50 else 'red'}">{booking_rate:.1f}%</div>
    </div>
    <div class="rev-divider"></div>
    <div class="rev-item">
        <div class="rev-label">Rate Compression</div>
        <div class="rev-value blue">{rate_comp:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ── Actionable Insights ────────────────────────────────────────────────────────
insights = m.get("insights", [])
if insights:
    st.markdown('<div class="sec-label">Actionable Insights</div>', unsafe_allow_html=True)
    cols_ins = st.columns(min(len(insights), 3))
    type_map = {"success":("✅","insight-success"),
                "warning":("⚠️","insight-warning"),
                "info":   ("💡","insight-info")}
    for i, ins in enumerate(insights[:3]):
        icon, cls = type_map.get(ins["type"], ("💡","insight-info"))
        with cols_ins[i % 3]:
            st.markdown(f"""
            <div class="insight {cls}">
                <span class="insight-icon">{icon}</span>
                <div>
                    <div class="insight-title">{ins['title']}</div>
                    <div class="insight-msg">{ins['message']}</div>
                </div>
            </div>""", unsafe_allow_html=True)

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Activity Metrics</div>', unsafe_allow_html=True)
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
avg_agreed  = m.get("avg_agreed_rate",0)
avg_board   = m.get("avg_loadboard_rate",0)
avg_savings = m.get("avg_savings_per_load",0)
avg_neg     = m.get("avg_negotiations",0)
brc = "v-green" if booking_rate>=50 else ("v-red" if booking_rate<30 else "")
svc = "v-green" if avg_savings>0 else ("v-red" if avg_savings<0 else "")

for col, html in [
    (c1, kpi("📞","Total Calls",     str(m.get("total_calls",0)),   "blue",  "v-blue")),
    (c2, kpi("✅","Booking Rate",    f"{booking_rate:.1f}%",        "green", brc,   "of all calls")),
    (c3, kpi("📦","Loads Booked",    str(m.get("booked",0)),        "teal",  "v-blue")),
    (c4, kpi("💰","Avg Agreed Rate", fmt(avg_agreed),               "indigo","",    "negotiated")),
    (c5, kpi("📋","Avg Board Rate",  fmt(avg_board),                "orange","",    "listed rate")),
    (c6, kpi("📉","Avg Savings",     fmt(abs(avg_savings)),         "purple",svc,   "vs board rate")),
    (c7, kpi("🔄","Avg Rounds",      f"{avg_neg:.1f}",              "red",   "",    "per call")),
]:
    with col: st.markdown(html, unsafe_allow_html=True)

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ── Charts row ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Performance Overview</div>', unsafe_allow_html=True)
col_d, col_s, col_v = st.columns([1.1,1.1,2.2])

with col_d:
    outcomes = m.get("outcomes",{})
    st.markdown('<div class="cc"><div class="ct">Call Outcomes</div><div class="cs">Distribution of all calls</div>', unsafe_allow_html=True)
    if outcomes:
        lbl = list(outcomes.keys()); val = list(outcomes.values())
        cm  = {"booked":C["green"],"declined":C["orange"],"no_deal":C["gray"],"carrier_ineligible":C["red"]}
        fig = go.Figure(go.Pie(
            labels=[l.replace("_"," ").title() for l in lbl], values=val,
            hole=0.64, marker=dict(colors=[cm.get(l,C["gray"]) for l in lbl],
            line=dict(color="#FFF",width=3)), textinfo="none",
            hovertemplate="%{label}: <b>%{value}</b> (%{percent})<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{sum(val)}</b><br><span style='font-size:11px;color:#8E8E93'>total</span>",
            x=0.5,y=0.5,showarrow=False,font=dict(size=20,color="#1D1D1F"))
        fig.update_layout(**BASE, showlegend=True, height=240,
            legend=dict(orientation="h",y=-0.12,x=0.5,xanchor="center",font=dict(size=11,color="#6E6E73")))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_s:
    sentiments = m.get("sentiments",{})
    st.markdown('<div class="cc"><div class="ct">Carrier Sentiment</div><div class="cs">Tone across all calls</div>', unsafe_allow_html=True)
    if sentiments:
        sl = list(sentiments.keys()); sv = list(sentiments.values())
        sc = {"positive":C["blue"],"neutral":C["gray"],"negative":C["red"]}
        fig2 = go.Figure(go.Bar(
            x=[l.title() for l in sl], y=sv,
            marker=dict(color=[sc.get(l,C["gray"]) for l in sl],
                        line=dict(width=0), cornerradius=8),
            text=sv, textposition="outside",
            textfont=dict(size=13,color="#1D1D1F",weight=600),
            hovertemplate="%{x}: <b>%{y}</b><extra></extra>",
        ))
        fig2.update_layout(**BASE, height=240, bargap=0.35,
            xaxis=dict(showgrid=False,showline=False,tickfont=dict(size=13)),
            yaxis=dict(showgrid=False,visible=False))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_v:
    daily = m.get("daily_calls",[])
    st.markdown('<div class="cc"><div class="ct">Daily Call Volume</div><div class="cs">Last 30 days · Agent activity trend</div>', unsafe_allow_html=True)
    if daily:
        df_d = pd.DataFrame(daily)
        df_d["date"] = pd.to_datetime(df_d["date"])
        df_d = df_d.sort_values("date")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_d["date"], y=df_d["count"], mode="lines",
            line=dict(color=C["blue"],width=2.5,shape="spline"),
            fill="tozeroy", fillcolor="rgba(0,113,227,0.07)",
            hovertemplate="%{x|%b %-d}: <b>%{y} calls</b><extra></extra>",
        ))
        mi = df_d["count"].idxmax()
        fig3.add_trace(go.Scatter(
            x=[df_d.loc[mi,"date"]], y=[df_d.loc[mi,"count"]], mode="markers",
            marker=dict(color=C["blue"],size=8,line=dict(color="#fff",width=2)),
            hoverinfo="skip",
        ))
        fig3.update_layout(**BASE, height=240,
            xaxis=dict(showgrid=False,showline=False,tickformat="%b %-d",
                       tickfont=dict(size=11),nticks=10),
            yaxis=dict(showgrid=True,gridcolor="#F2F2F7",showline=False,
                       tickfont=dict(size=11),zeroline=False))
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── Lane & Carrier Intelligence ────────────────────────────────────────────────
st.markdown('<div class="sec-label" style="margin-top:1.5rem">Business Intelligence</div>', unsafe_allow_html=True)
bl, br = st.columns(2)

with bl:
    lane_data = m.get("lane_performance",[])
    rows = ""
    for l in lane_data:
        br_val = l["booking_rate"]
        br_cls = "v-green" if br_val>=60 else ("v-red" if br_val<40 else "")
        rows += f"""<tr>
            <td class="mono bold">{l['load_id']}</td>
            <td style="text-align:center">{l['calls']}</td>
            <td style="text-align:center;font-weight:600" class="{br_cls}">{br_val}%</td>
            <td style="text-align:right">{fmt(l['avg_rate'])}</td>
            <td style="text-align:right;color:#8E8E93">{fmt(l['avg_board'])}</td>
        </tr>"""
    st.markdown(f"""<div class="tw">
        <table class="tbl">
            <thead><tr>
                <th>Load</th><th style="text-align:center">Calls</th>
                <th style="text-align:center">Book Rate</th>
                <th style="text-align:right">Avg Agreed</th>
                <th style="text-align:right">Board Rate</th>
            </tr></thead>
            <tbody>{rows or '<tr><td colspan=5 style="text-align:center;color:#8E8E93;padding:2rem">No data yet</td></tr>'}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)
    st.caption("Lane Performance — focus volume on highest-converting loads")

with br:
    carrier_data = m.get("carrier_value",[])
    rows2 = ""
    for c in carrier_data:
        rows2 += f"""<tr>
            <td class="bold">{c['carrier_name']}</td>
            <td class="mono" style="color:#8E8E93">{c['carrier_mc']}</td>
            <td style="text-align:center">{c['bookings']}/{c['calls']}</td>
            <td style="text-align:center;font-weight:600">{c['booking_rate']}%</td>
            <td style="text-align:right;font-weight:600;color:#1A7A3C">{fmt(c['total_revenue'])}</td>
        </tr>"""
    st.markdown(f"""<div class="tw">
        <table class="tbl">
            <thead><tr>
                <th>Carrier</th><th>MC #</th>
                <th style="text-align:center">Booked/Calls</th>
                <th style="text-align:center">Rate</th>
                <th style="text-align:right">Revenue</th>
            </tr></thead>
            <tbody>{rows2 or '<tr><td colspan=5 style="text-align:center;color:#8E8E93;padding:2rem">No data yet</td></tr>'}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)
    st.caption("Carrier Value — nurture top-revenue relationships")

# ── Negotiations ───────────────────────────────────────────────────────────────
neg_dist = m.get("negotiations_distribution",{})
if neg_dist:
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Negotiation Depth</div>', unsafe_allow_html=True)
    _, nc, _ = st.columns([.05,3.9,.05])
    with nc:
        st.markdown('<div class="cc"><div class="ct">Calls by Negotiation Rounds</div><div class="cs">How many counter-offers before close — more rounds = harder close</div>', unsafe_allow_html=True)
        nl = [f"{k} round{'s' if int(k)!=1 else ''}" for k in neg_dist.keys()]
        nv = list(neg_dist.values())
        fig4 = go.Figure(go.Bar(
            x=nl, y=nv,
            marker=dict(color=[C["blue"],C["indigo"],C["orange"],C["red"]][:len(nl)],
                        line=dict(width=0), cornerradius=8),
            text=nv, textposition="outside",
            textfont=dict(size=14,color="#1D1D1F",weight=600),
            hovertemplate="%{x}: <b>%{y} calls</b><extra></extra>",
        ))
        fig4.update_layout(**BASE, height=190, bargap=0.5,
            xaxis=dict(showgrid=False,showline=False,tickfont=dict(size=13)),
            yaxis=dict(showgrid=False,visible=False))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

# ── Recent Calls ───────────────────────────────────────────────────────────────
st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
st.markdown('<div class="sec-label">Recent Calls · Agent Activity Log</div>', unsafe_allow_html=True)

O = {"booked":("b-booked","✓ Booked"),"declined":("b-declined","✕ Declined"),
     "no_deal":("b-no_deal","— No Deal"),"carrier_ineligible":("b-ineligible","⚠ Ineligible")}
S = {"positive":("b-positive","😊 Positive"),"neutral":("b-neutral","😐 Neutral"),
     "negative":("b-negative","😞 Negative")}

if calls_raw:
    rows3 = ""
    for c in calls_raw[:50]:
        oc,ol = O.get(c.get("outcome",""),("b-no_deal",c.get("outcome","")))
        sc2,sl2 = S.get(c.get("sentiment",""),("b-neutral",c.get("sentiment","")))
        rows3 += f"""<tr>
            <td style="color:#8E8E93;font-size:12px">{fmt_time(c.get('created_at',''))}</td>
            <td class="bold">{c.get('carrier_name') or '—'}</td>
            <td><span class="mono">{c.get('carrier_mc') or '—'}</span></td>
            <td><span class="mono">{c.get('load_id') or '—'}</span></td>
            <td>{fmt(c.get('loadboard_rate'))}</td>
            <td style="color:#8E8E93">{fmt(c.get('initial_offer'))}</td>
            <td class="bold">{fmt(c.get('agreed_rate'))}</td>
            <td style="text-align:center;font-weight:600">{c.get('num_negotiations',0)}</td>
            <td>{badge(ol,oc[2:])}</td>
            <td>{badge(sl2,sc2[2:])}</td>
        </tr>"""
    st.markdown(f"""<div class="tw"><table class="tbl">
        <thead><tr>
            <th>Time</th><th>Carrier</th><th>MC #</th><th>Load</th>
            <th>Board Rate</th><th>Initial Offer</th><th>Agreed Rate</th>
            <th style="text-align:center">Rounds</th><th>Outcome</th><th>Sentiment</th>
        </tr></thead><tbody>{rows3}</tbody>
    </table></div>""", unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center;padding:3rem;color:#8E8E93">No calls recorded yet — make a call to see data here</div>', unsafe_allow_html=True)

st.markdown(f"""<div class="footer">
    HappyRobot Freight Analytics · Built for Acme Logistics ·
    Updated {datetime.now().strftime("%-d %b %Y at %-I:%M %p")}
</div>""", unsafe_allow_html=True)
