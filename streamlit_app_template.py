# streamlit_app_template.py
# Streamlit Control Center for SAP Repricing & Validation
# NOTE: Wire your real SAP / SharePoint / Outlook / Macro code where marked TODO.

import streamlit as st
import pandas as pd
import datetime as dt
import sqlite3
from pathlib import Path
import random

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SAP Repricing Automation",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- GLOBAL STYLE (vibrant + compact + sticky command bar) ----------
CUSTOM_CSS = """
/* --- Layout reset: ensure nothing is clipped at the very top --- */
.block-container { 
  padding-top: 2.25rem !important;   /* safe breathing room */
  padding-bottom: 1rem;
}

/* Keep sidebar consistent on smaller screens (Streamlit classnames are subject to change) */
.css-1d391kg, .css-18ni7ap { padding-top: 0.5rem !important; }

/* --- Command bar as sticky, with safe offset --- */
.command-bar {
  position: sticky;
  top: 0;                 /* sticks to the top of the content area */
  z-index: 100;           /* above tables/cards */
  background: #FFFFFF; 
  padding: 8px 0 6px 0;
  border-bottom: 1px solid #E5E7EB;
}

/* Extra spacing after the command bar to avoid overlap with next section */
.command-spacer { height: 8px; }

/* KPI cards */
.kpi-card {
  background: #ffffff;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid #D8E2EE;
  box-shadow: 0 1px 6px rgba(15, 23, 42, 0.06);
  margin-bottom: 8px;
}
.kpi-title { font-size: 0.85rem; color: #4B5563; font-weight: 600; margin-bottom: 4px; }
.kpi-value { font-size: 1.55rem; font-weight: 700; color: #0F172A; }

.kpi-pill {
  display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem;
  margin-left: 8px; color: #0F172A; border: 1px solid #E5E7EB;
}
.pill-ok { background: #E7F8EE; color: #065F46; border-color: #B7E7C8;}
.pill-warn { background: #FFF7E6; color: #92400E; border-color: #F5D7A1;}
.pill-alert { background: #FFECEF; color: #9B1C1C; border-color: #F7B6BF;}
.pill-info { background: #E8F3FF; color: #1E40AF; border-color: #BFDBFE;}

/* Primary buttons in command bar */
.command-bar button[kind="primary"] {
  background: linear-gradient(90deg, #0EA5E9, #2563EB) !important;
  color: white !important;
  border: none !important;
}

/* Sticky headers for tables */
[data-testid="stTable"] thead tr th {
  position: sticky; top: 0; background: #F8FAFC; z-index: 5;
}

/* Tabs look */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #E5E7EB; }
.stTabs [data-baseweb="tab"] { background: #F3F4F6; border-radius: 999px; padding: 8px 14px; }

/* Reduce form spacing a bit */
.stTextInput, .stSelectbox, .stDateInput, .stFileUploader, .stToggle { margin-bottom: 0.35rem; }

/* Optional shadow for sticky bar (uncomment if desired) */
/* .command-bar { box-shadow: 0 6px 10px -8px rgba(15, 23, 42, 0.25); } */
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# ---------- STORAGE ----------
DATA_DIR = Path("./data"); DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "runs.sqlite"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS runs(ts TEXT, stage TEXT, status TEXT, notes TEXT)"
    )
    return conn

def log(stage, status, notes=""):
    conn = get_db()
    conn.execute(
        "INSERT INTO runs VALUES (?,?,?,?)",
        (dt.datetime.now().isoformat(timespec="seconds"), stage, status, notes),
    )
    conn.commit(); conn.close()

@st.cache_data
def load_recent_runs(n=250):
    conn = get_db()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM runs ORDER BY ts DESC LIMIT ?", conn, params=(n,)
        )
    except Exception:
        df = pd.DataFrame(columns=["ts", "stage", "status", "notes"])
    conn.close()
    return df

# ---------- PLACEHOLDER BACKEND (wire your real code here) ----------
def run_sq00_extracts():
    log("Report Downloads", "Started")
    # TODO: SAP SQ00 / PyRFC / GUI scripting / TPM / Master Price List
    log("Report Downloads", "Success", "Orders, Expected, Discounts, Partners, Master")

def run_repricing_jobs():
    log("Repricing Jobs (Z2CMT3540)", "Triggered", "Background jobs queued")

def run_price_validation_macros():
    log("Price Validation", "Started")
    # TODO: xlwings -> VBA macro call
    log("Price Validation", "Success", "Validation Report.xlsx created")

def split_and_archive_sharepoint():
    log("SharePoint Orchestration", "Started")
    # TODO: MS Graph API calls to split, archive, route by folder
    log("SharePoint Orchestration", "Success")

def send_overview_emails():
    log("Reporting", "Started")
    # TODO: Outlook COM API
    log("Reporting", "Success")

def sap_apply_block(order_ids):
    log("SAP Block (Z1)", "Started", f"{len(order_ids)} orders")
    # TODO: BB Tool / VA02 scripting / BAPI
    log("SAP Block (Z1)", "Success")

def sap_remove_block(order_ids):
    log("SAP Unblock", "Started", f"{len(order_ids)} orders")
    # TODO
    log("SAP Unblock", "Success")

# ---------- SIDEBAR (always visible primary nav) ----------
st.sidebar.image("https://img.icons8.com/color/96/automation.png", width=64)
st.sidebar.title("Control Center")
nav = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "⏬ Report Downloads",
        "🧮 Price Validation",
        "🧷 Block Mgmt (MSO)",
        "🗂️ SharePoint",
        "📧 Reporting",
        "🛠️ Admin / Scheduler",
    ],
    index=0,
)

# Quick filters/search in sidebar (applies on Dashboard & MSO views)
with st.sidebar.expander("🔎 Quick Filters", expanded=False):
    cust_filter = st.text_input("Customer contains")
    order_filter = st.text_input("Order contains")
    status_filter = st.selectbox("Run status", ["All", "Started", "Success", "Error"])

# ---------- TOP: COMMAND BAR (sticky) ----------
st.markdown('<div class="command-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1])
with c1:
    st.markdown("### ⚙️ Streamlit Control Center – SAP Repricing")
    st.caption("All runs, reviews and reporting in one place.")
with c2:
    if st.button("▶️ Full Cycle", use_container_width=True, type="primary"):
        run_sq00_extracts(); run_repricing_jobs(); run_price_validation_macros()
        split_and_archive_sharepoint(); send_overview_emails()
        st.success("Full cycle triggered.")
with c3:
    if st.button("⏬ Extract Reports", use_container_width=True):
        run_sq00_extracts(); st.toast("Report extracts completed.")
with c4:
    if st.button("🧮 Validate Prices", use_container_width=True):
        run_price_validation_macros(); st.toast("Validation complete.")
with c5:
    if st.button("📧 Send Overview", use_container_width=True):
        send_overview_emails(); st.toast("Overview emails sent.")
st.markdown('</div><div class="command-spacer"></div>', unsafe_allow_html=True)

st.divider()

# ---------- KPI RIBBON ----------
def kpi_card(title, value, pill_text=None, pill_class="pill-info"):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}
            {"<span class='kpi-pill "+pill_class+"'>"+pill_text+"</span>" if pill_text else ""}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1: kpi_card("Total Orders", "3,842", "Today", "pill-info")
with k2: kpi_card("Price Mismatches", "271", "7.1%", "pill-alert")
with k3: kpi_card("Blocked (Z1)", "119", "↑ 5 today", "pill-warn")
with k4: kpi_card("Unblocked Today", "46", "✓ cleared", "pill-ok")
with k5: kpi_card("Files Archived", "1,304", "Auto", "pill-info")
with k6: kpi_card("Emails Sent", "8", "Latest run", "pill-ok")

st.divider()

# ---------- PAGE CONTENT ----------
if nav == "🏠 Dashboard":
    st.subheader("📊 Live Status Board")

    runs = load_recent_runs()
    if status_filter != "All":
        runs = runs.query("status == @status_filter")
    if cust_filter:
        runs = runs[runs["notes"].str.contains(cust_filter, case=False, na=False)]
    if order_filter:
        runs = runs[runs["notes"].str.contains(order_filter, case=False, na=False)]

    cA, cB = st.columns([2.2, 1])
    with cA:
        st.dataframe(
            runs,
            use_container_width=True,
            height=420,
        )
    with cB:
        st.markdown("#### 🔔 Recent Alerts")
        alerts = pd.DataFrame(
            {
                "time": [
                    (dt.datetime.now() - dt.timedelta(minutes=i * 7)).strftime(
                        "%H:%M:%S"
                    )
                    for i in range(1, 8)
                ],
                "message": [
                    random.choice(
                        [
                            "High mismatch rate in DE region",
                            "VA02 fallback used for 3 orders",
                            "SharePoint archive completed",
                            "Outlook throttling – retry in 30s",
                            "TPM feed delayed; using cached",
                        ]
                    )
                    for _ in range(7)
                ],
            }
        )
        st.table(alerts)

    st.markdown("#### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1: st.button("🧪 Dry Run (Test Data)", use_container_width=True)
    with qa2: st.button("🔁 Retry Failed Tasks", use_container_width=True)
    with qa3: st.button("🧼 Clean Temp Files", use_container_width=True)
    with qa4: st.button("⬇️ Download Logs", use_container_width=True)

elif nav == "⏬ Report Downloads":
    st.subheader("⏬ Automated Report Downloads")
    g1, g2, g3 = st.columns([1.2, 1, 1])
    with g1:
        st.markdown("**Included:** Orders • Expected Price • Logistics Discount • Partners • Master Price List • TPM")
    with g2:
        st.button("Run All Extracts", type="primary", use_container_width=True, on_click=run_sq00_extracts)
    with g3:
        st.button("Run Repricing Jobs (Z2CMT3540)", use_container_width=True, on_click=run_repricing_jobs)

    st.markdown("##### Recent Downloads")
    st.dataframe(load_recent_runs().query("stage in ['Report Downloads','Repricing Jobs (Z2CMT3540)']"),
                 use_container_width=True, height=420)

elif nav == "🧮 Price Validation":
    st.subheader("🧮 Price Validation Engine (Excel Macros)")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.button("Run Validation Macros", type="primary", use_container_width=True, on_click=run_price_validation_macros)
        st.caption("Runs VBA via xlwings; outputs consolidated mismatch report and category bifurcation.")
    with c2:
        st.selectbox("Report Version", ["Latest", "Yesterday", "Last Week"])
        st.text_input("Filter by Customer/Order")
        st.button("Refresh View", use_container_width=True)

    # Sample validation table with tags (replace with real data frame)
    st.markdown("##### Validation Results (Sample)")
    val = pd.DataFrame(
        {
            "Order": [f"45{100+i}" for i in range(12)],
            "Customer": [f"DE-10{i%4}" for i in range(12)],
            "Issue": [random.choice(["Missing Siebel", "Wrong Value", "X‑mas price taken", "No price found"]) for _ in range(12)],
            "Suggested": [random.choice(["Block", "Unblock", "Investigate"]) for _ in range(12)],
            "Price Δ": [round(random.uniform(-12, 18), 2) for _ in range(12)],
            "Comment": ["" for _ in range(12)],
        }
    )
    st.data_editor(val, use_container_width=True, height=440, num_rows="fixed")

elif nav == "🧷 Block Mgmt (MSO)":
    st.subheader("🧷 MSO Review & Block/Unblock")
    st.caption("Edit comments, choose a decision, and commit changes to SAP (BB Tool / VA02 fallback).")

    df = pd.DataFrame({
        "Order": [f"60{200+i}" for i in range(15)],
        "Customer": [f"DE-{i%4+1}" for i in range(15)],
        "Issue": [random.choice(["Missing Siebel","X‑mas price taken","No price found","Wrong Value"]) for _ in range(15)],
        "Current Block": [random.choice(["", "Z1"]) for _ in range(15)],
        "Decision": [random.choice(["Block","Unblock","Investigate"]) for _ in range(15)],
        "Comments": ["" for _ in range(15)]
    })
    edited = st.data_editor(df, use_container_width=True, height=460, key="mso_table")
    ids_block   = edited.loc[edited["Decision"].str.lower()=="block","Order"].tolist()
    ids_unblock = edited.loc[edited["Decision"].str.lower()=="unblock","Order"].tolist()

    a,b,c = st.columns([1,1,1])
    with a:
        if st.button(f"🔒 Commit Blocks ({len(ids_block)})", type="primary", use_container_width=True):
            sap_apply_block(ids_block); st.success(f"Applied block to {len(ids_block)} orders")
    with b:
        if st.button(f"🔓 Remove Blocks ({len(ids_unblock)})", use_container_width=True):
            sap_remove_block(ids_unblock); st.success(f"Removed block for {len(ids_unblock)} orders")
    with c:
        st.button("📝 Export Review Sheet", use_container_width=True)

elif nav == "🗂️ SharePoint":
    st.subheader("🗂️ SharePoint Orchestration")
    st.caption("Split files by KAM/Customer, archive correct files, route blocked ones back to CD folders.")
    d1, d2 = st.columns([1, 1])
    with d1:
        st.button("Split & Archive", type="primary", use_container_width=True, on_click=split_and_archive_sharepoint)
        st.toggle("Timestamped Save", value=True)
        st.text_input("SharePoint Path", value="/teams/pricing/automation/")
    with d2:
        st.selectbox("Customer Folder", ["All","DE-101","DE-102","DE-103"])
        st.selectbox("Status", ["All","Archived","Blocked","Unblock Ready"])
        st.button("Refresh Folder View", use_container_width=True)
    st.markdown("##### Recent SharePoint Ops")
    st.dataframe(load_recent_runs().query("stage == 'SharePoint Orchestration'"), use_container_width=True, height=420)

elif nav == "📧 Reporting":
    st.subheader("📧 Reporting & Notifications")
    r1, r2, r3 = st.columns([1,1,1])
    with r1:
        st.button("Send Overview Emails", type="primary", use_container_width=True, on_click=send_overview_emails)
        st.multiselect("Recipients", ["pricing@acme.com","kam@acme.com","ops@acme.com"], default=["pricing@acme.com"])
    with r2:
        st.selectbox("Report Type", ["Daily Snapshot","DSR","Evening Summary","Power BI Export"])
        st.date_input("For Date", value=dt.date.today())
    with r3:
        st.file_uploader("Attach Extra File (optional)", type=["xlsx","csv","pdf"])
        st.toggle("Include KPIs image", value=True)
    st.markdown("##### Recent Reports")
    st.dataframe(load_recent_runs().query("stage == 'Reporting'"), use_container_width=True, height=420)

else:  # Admin
    st.subheader("🛠️ Admin & Scheduler")
    st.caption("Configure credentials, schedules, and inspect logs.")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("**Scheduling**")
        c1, c2 = st.columns(2)
        c1.time_input("Extracts", value=dt.time(6,0))
        c1.time_input("Validation", value=dt.time(6,30))
        c2.time_input("Reporting", value=dt.time(7,0))
        st.toggle("Enable Auto-Runs", value=True)
        st.button("Save Schedule", use_container_width=True)

        st.markdown("**Integrations**")
        st.text_input("SAP System", value="PRD")
        st.text_input("SharePoint Site", value="sites/pricing")
        st.text_input("Email From", value="pricing-automation@acme.com")

    with right:
        st.markdown("**Run Log (latest 200)**")
        st.dataframe(load_recent_runs(), use_container_width=True, height=520)