import streamlit as st
import requests
import random
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="STREAMING-ANOMALY-ENGINE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Cyberpunk Dark CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
    .control-panel {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(8px);
    }
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #00f2fe;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        font-family: 'Courier New', Courier, monospace;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .status-normal { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; }
    .status-anomaly { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
    .status-idle { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid #94a3b8; }
    .terminal-box {
        background-color: #050811;
        border: 1px solid #1e293b;
        border-radius: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        padding: 12px;
        height: 280px;
        overflow-y: auto;
        color: #38bdf8;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Main Title Header
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h1 style="margin:0; background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; letter-spacing: 2px;">
        ⚡ STREAMING-ANOMALY-ENGINE
    </h1>
    <p style="margin:5px 0 0 0; color: #64748b; font-size: 0.95rem;">Real-Time Distributed Event Ingestion & Low-Latency Anomaly Detection Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Main Control Bar
st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.5, 1.5, 1.5, 1.5])

with ctrl_col1:
    total_req_limit = st.number_input("TOTAL REQUEST LIMIT", min_value=10, max_value=5000, value=100, step=10)

with ctrl_col2:
    anomaly_threshold = st.slider("ANOMALY THRESHOLD", min_value=0.1, max_value=1.0, value=0.7, step=0.05)

with ctrl_col3:
    delay_speed = st.slider("STREAM SPEED (SEC)", min_value=0.01, max_value=0.5, value=0.05, step=0.01)

with ctrl_col4:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    start_btn = st.button("🚀 LAUNCH STREAM", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# Main Metrics Row
m1, m2, m3, m4 = st.columns(4)

metric_req_placeholder = m1.empty()
metric_lat_placeholder = m2.empty()
metric_anom_placeholder = m3.empty()
metric_status_placeholder = m4.empty()

metric_req_placeholder.markdown(f"""<div class="metric-card"><div class="metric-title">TOTAL PROCESSED</div><div class="metric-value">0 / {total_req_limit}</div></div>""", unsafe_allow_html=True)
metric_lat_placeholder.markdown("""<div class="metric-card"><div class="metric-title">INTERNAL LATENCY</div><div class="metric-value" style="color: #00f2fe;">0.00 ms</div></div>""", unsafe_allow_html=True)
metric_anom_placeholder.markdown("""<div class="metric-card"><div class="metric-title">ANOMALIES THREATS</div><div class="metric-value" style="color: #ef4444;">0</div></div>""", unsafe_allow_html=True)
metric_status_placeholder.markdown("""<div class="metric-card"><div class="metric-title">ENGINE STATE</div><div class="metric-value"><span class="status-badge status-idle">STANDBY ⚪</span></div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Dual Y-Axis Chart Generator
def create_chart(df=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if df is not None and not df.empty:
        # Trace 1: Anomaly Score (Primary Y-Axis)
        fig.add_trace(
            go.Scatter(
                x=df["Req"], y=df["Score"],
                mode='lines+markers', name='Anomaly Score',
                line=dict(color='#00f2fe', width=2.5),
                marker=dict(size=5, color=df["Is_Anomaly"].map({True: '#ef4444', False: '#00f2fe'}))
            ),
            secondary_y=False,
        )
        # Trace 2: Latency ms (Secondary Y-Axis)
        fig.add_trace(
            go.Scatter(
                x=df["Req"], y=df["Latency"],
                mode='lines', name='Latency (ms)',
                line=dict(color='#a855f7', width=1.5, dash='dot')
            ),
            secondary_y=True,
        )
    else:
        fig.add_trace(
            go.Scatter(x=[0], y=[0], mode='lines', name='Waiting for stream...', line=dict(color='#00f2fe')),
            secondary_y=False
        )

    fig.update_layout(
        paper_bgcolor='rgba(11, 15, 25, 0)',
        plot_bgcolor='rgba(17, 24, 39, 0.5)',
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#94a3b8")),
        xaxis=dict(showgrid=True, gridcolor='#1e293b', tickfont=dict(color="#94a3b8"), title=dict(text="Requests", font=dict(color="#94a3b8")))
    )
    fig.update_yaxes(title_text="Anomaly Score (0-1)", title_font=dict(color="#00f2fe"), tickfont=dict(color="#00f2fe"), showgrid=True, gridcolor='#1e293b', secondary_y=False)
    fig.update_yaxes(title_text="Latency (ms)", title_font=dict(color="#a855f7"), tickfont=dict(color="#a855f7"), showgrid=False, secondary_y=True)
    return fig

col_chart, col_feed = st.columns([2.2, 1])

with col_chart:
    st.markdown("<h3 style='font-size: 1.1rem; color: #cbd5e1;'>📊 LIVE LATENCY & ANOMALY SCORE METRICS</h3>", unsafe_allow_html=True)
    chart_placeholder = st.empty()
    chart_placeholder.plotly_chart(create_chart(), use_container_width=True)

with col_feed:
    st.markdown("<h3 style='font-size: 1.1rem; color: #cbd5e1;'>⚡ REAL-TIME EVENT STREAM FEED</h3>", unsafe_allow_html=True)
    terminal_placeholder = st.empty()
    terminal_placeholder.markdown("<div class='terminal-box'>System Ready. Press 'LAUNCH STREAM' to start...</div>", unsafe_allow_html=True)

st.markdown("<h3 style='font-size: 1.1rem; color: #cbd5e1; margin-top: 25px;'>🚨 THREAT LOGS TABLE</h3>", unsafe_allow_html=True)
logs_placeholder = st.empty()
download_placeholder = st.empty()

URL = "http://localhost:8000/predict"

if start_btn:
    history = []
    anomaly_logs = []
    terminal_logs = []
    anomalies_count = 0
    
    for i in range(1, int(total_req_limit) + 1):
        user_id = f"usr_{random.randint(100, 999)}"
        amount = round(random.uniform(10.0, 2500.0), 2)
        payload = {"user_id": user_id, "amount": amount}
        
        try:
            res = requests.post(URL, json=payload, timeout=2.0).json()
            latency = res.get("latency_ms", 0.0)
            score = res.get("anomaly_score", 0.0)
            is_anomaly = score >= anomaly_threshold
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            if is_anomaly:
                anomalies_count += 1
                anomaly_logs.append({
                    "Timestamp": timestamp,
                    "Req ID": f"#{i:04d}",
                    "User ID": user_id,
                    "Amount ($)": f"${amount:,.2f}",
                    "Anomaly Score": round(score, 4),
                    "Latency": f"{latency:.2f} ms"
                })
                terminal_logs.insert(0, f"<span style='color: #ef4444;'>[{timestamp}] 🔴 ANOMALY DETECTED | Req #{i} | {user_id} | ${amount} | Score: {score:.3f}</span>")
            else:
                terminal_logs.insert(0, f"<span style='color: #10b981;'>[{timestamp}] 🟢 OK | Req #{i} | {user_id} | ${amount} | Score: {score:.3f}</span>")

            history.append({
                "Req": i,
                "Latency": latency,
                "Score": score,
                "Is_Anomaly": is_anomaly
            })

            # Update Metric Cards
            metric_req_placeholder.markdown(f"""<div class="metric-card"><div class="metric-title">TOTAL PROCESSED</div><div class="metric-value">{i} / {total_req_limit}</div></div>""", unsafe_allow_html=True)
            metric_lat_placeholder.markdown(f"""<div class="metric-card"><div class="metric-title">INTERNAL LATENCY</div><div class="metric-value" style="color: #00f2fe;">{latency:.2f} ms</div></div>""", unsafe_allow_html=True)
            metric_anom_placeholder.markdown(f"""<div class="metric-card"><div class="metric-title">ANOMALIES THREATS</div><div class="metric-value" style="color: #ef4444;">{anomalies_count}</div></div>""", unsafe_allow_html=True)
            
            if is_anomaly:
                metric_status_placeholder.markdown("""<div class="metric-card"><div class="metric-title">ENGINE STATE</div><div class="metric-value"><span class="status-badge status-anomaly">THREAT DETECTED 🚨</span></div></div>""", unsafe_allow_html=True)
            else:
                metric_status_placeholder.markdown("""<div class="metric-card"><div class="metric-title">ENGINE STATE</div><div class="metric-value"><span class="status-badge status-normal">STREAMING 🟢</span></div></div>""", unsafe_allow_html=True)

            # Update Chart
            df_chart = pd.DataFrame(history)
            chart_placeholder.plotly_chart(create_chart(df_chart), use_container_width=True)

            # Update Terminal
            term_html = "<div class='terminal-box'>" + "<br>".join(terminal_logs[:12]) + "</div>"
            terminal_placeholder.markdown(term_html, unsafe_allow_html=True)

            # Update Table
            if len(anomaly_logs) > 0:
                logs_placeholder.dataframe(pd.DataFrame(anomaly_logs), use_container_width=True, hide_index=True)

            time.sleep(delay_speed)
            
        except Exception as e:
            st.error("Engine Offline or Connection Refused! Make sure FastAPI Server is running on Port 8000.")
            break

    metric_status_placeholder.markdown("""<div class="metric-card"><div class="metric-title">ENGINE STATE</div><div class="metric-value"><span class="status-badge status-idle">COMPLETED 🏁</span></div></div>""", unsafe_allow_html=True)

    # Export Report CSV Button after completion
    if len(anomaly_logs) > 0:
        df_export = pd.DataFrame(anomaly_logs)
        csv = df_export.to_csv(index=False).encode('utf-8')
        download_placeholder.download_button(
            label="📥 EXPORT THREAT LOGS (CSV)",
            data=csv,
            file_name=f"threat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )