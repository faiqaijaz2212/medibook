import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, date, timedelta

st.set_page_config(
    page_title="MediBook Admin Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://127.0.0.1:8000"

# CSS for styling metric cards
st.markdown(
    """
<style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-val {
        font-size: 32px;
        font-weight: 700;
        color: #2b6cb0;
        margin-bottom: 5px;
    }
    .metric-lbl {
        font-size: 12px;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Authentication Session State Init
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None


# Helper to call REST API
def api_request(endpoint, method="GET", json_data=None, params=None):
    headers = {}
    if st.session_state["token"]:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"

    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            res = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=json_data)
        return res
    except Exception as e:
        st.error(f"Failed to connect to backend server: {e}")
        return None


# 1. LOGIN SCREEN
if not st.session_state["token"]:
    st.title("🔐 MediBook Clinic Login")
    st.write(
        "Welcome to the administrative analytics portal. Please log in using your clinic credentials."
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Log In", use_container_width=True)

        if login_btn:
            if not username or not password:
                st.warning("Please fill in both fields.")
            else:
                res = api_request(
                    "/auth/login",
                    method="POST",
                    json_data={"username": username, "password": password},
                )
                if res and res.status_code == 200:
                    token_data = res.json()
                    st.session_state["token"] = token_data["access_token"]
                    st.session_state["username"] = username

                    # Get user profile info
                    me_res = api_request("/users/me")
                    if me_res and me_res.status_code == 200:
                        st.session_state["role"] = me_res.json()["role"]
                        st.success("Logged in successfully!")
                        st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
    st.stop()

# 2. MAIN DASHBOARD CONTENT
st.title("📊 MediBook Clinic Analytics")
st.write(
    f"Logged in as **{st.session_state['username']}** ({st.session_state['role'].capitalize()})"
)

# Fetch baseline data
depts_res = api_request("/departments")
docs_res = api_request("/doctors")
pats_res = api_request("/patients")

if not (depts_res and docs_res and pats_res):
    st.error("Could not fetch baseline data from backend. Is uvicorn running?")
    st.stop()

departments = depts_res.json()
doctors = docs_res.json()
patients = pats_res.json()

# Get today's date and calculate date boundaries
today_val = date.today()
default_start = today_val - timedelta(days=30)
default_end = today_val + timedelta(days=30)

# SIDEBAR FILTERS
st.sidebar.header("🎯 Interactive Filters")

# Date range filter
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", default_end)

# Department filter
dept_names = {d["id"]: d["name"] for d in departments}
dept_options = ["All Departments"] + list(dept_names.values())
selected_dept_name = st.sidebar.selectbox("Filter by Department", dept_options)
selected_dept_id = None
if selected_dept_name != "All Departments":
    selected_dept_id = [
        k for k, v in dept_names.items() if v == selected_dept_name
    ][0]

# Doctor filter
doc_names = {doc["id"]: doc["name"] for doc in doctors}
selected_doc_names = st.sidebar.multiselect(
    "Filter by Doctor(s)", list(doc_names.values())
)
selected_doc_ids = []
if selected_doc_names:
    selected_doc_ids = [
        k for k, v in doc_names.items() if v in selected_doc_names
    ]

# Fetch filtered appointments
app_params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
if selected_dept_id:
    app_params["department_id"] = selected_dept_id

apps_res = api_request("/appointments", params=app_params)
if not apps_res or apps_res.status_code != 200:
    st.error("Failed to load appointments.")
    st.stop()

all_appointments = apps_res.json()

# Apply Doctor filtering locally (if selected)
if selected_doc_ids:
    all_appointments = [
        a for a in all_appointments if a["doctor_id"] in selected_doc_ids
    ]

# Convert appointments list to DataFrame for charting
df_apps = pd.DataFrame(all_appointments)
if not df_apps.empty:
    df_apps["appointment_date"] = pd.to_datetime(df_apps["appointment_date"])
    df_apps["date_only"] = df_apps["appointment_date"].dt.date
    df_apps["hour_only"] = df_apps["appointment_date"].dt.hour

# Calculate top-level stats
total_pats = len(patients)
total_docs = len(doctors)
total_depts = len(departments)

# Calculate status stats
scheduled_count = 0
completed_count = 0
cancelled_count = 0
today_count = 0

if not df_apps.empty:
    scheduled_count = len(df_apps[df_apps["status"].isin(["Scheduled", "Rescheduled"])])
    completed_count = len(df_apps[df_apps["status"] == "Completed"])
    cancelled_count = len(df_apps[df_apps["status"] == "Cancelled"])
    today_count = len(df_apps[df_apps["date_only"] == today_val])

# RENDER METRIC CARDS
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{total_pats}</div><div class="metric-lbl">Total Patients</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{total_docs}</div><div class="metric-lbl">Total Doctors</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{total_depts}</div><div class="metric-lbl">Departments</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{today_count}</div><div class="metric-lbl">Today\'s Appts</div></div>',
        unsafe_allow_html=True,
    )
with col5:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val" style="color: #2f855a;">{completed_count}</div><div class="metric-lbl">Completed</div></div>',
        unsafe_allow_html=True,
    )
with col6:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val" style="color: #c53030;">{cancelled_count}</div><div class="metric-lbl">Cancelled</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# RENDER VISUALIZATIONS
if df_apps.empty:
    st.info("No appointments found matching the selected filters.")
else:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # 1. Appointment Trend Over Time
        st.subheader("📈 Appointment Trend")
        df_trend = (
            df_apps.groupby("date_only")
            .size()
            .reset_index(name="Appointments count")
        )
        df_trend.rename(columns={"date_only": "Date"}, inplace=True)
        fig_trend = px.line(
            df_trend,
            x="Date",
            y="Appointments count",
            markers=True,
            color_discrete_sequence=["#2b6cb0"],
        )
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="No. of Bookings")
        st.plotly_chart(fig_trend, use_container_width=True)

        # 2. Patient Gender Distribution
        st.subheader("🧬 Patient Gender Distribution")
        df_pats = pd.DataFrame(patients)
        if not df_pats.empty and "gender" in df_pats.columns:
            df_gender = df_pats.groupby("gender").size().reset_index(name="count")
            fig_gender = px.pie(
                df_gender,
                names="gender",
                values="count",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.write("No patient gender data available.")

        # 3. Daily Patient Visits (Area Chart)
        st.subheader("👥 Daily Unique Patient Visits")
        df_visits = (
            df_apps.groupby("date_only")["patient_id"]
            .nunique()
            .reset_index(name="Unique Patients")
        )
        df_visits.rename(columns={"date_only": "Date"}, inplace=True)
        fig_visits = px.area(
            df_visits,
            x="Date",
            y="Unique Patients",
            color_discrete_sequence=["#4299e1"],
        )
        fig_visits.update_layout(xaxis_title="Date", yaxis_title="Patients Visited")
        st.plotly_chart(fig_visits, use_container_width=True)

    with chart_col2:
        # 4. Doctor Workload
        st.subheader("👨‍⚕️ Doctor Workload")
        df_workload = (
            df_apps.groupby("doctor_id").size().reset_index(name="Appointments")
        )
        df_workload["Doctor Name"] = df_workload["doctor_id"].map(doc_names)
        fig_workload = px.bar(
            df_workload.sort_values(by="Appointments", ascending=True),
            x="Appointments",
            y="Doctor Name",
            orientation="h",
            color="Appointments",
            color_continuous_scale="Blues",
        )
        fig_workload.update_layout(xaxis_title="Appointments Count", yaxis_title="")
        st.plotly_chart(fig_workload, use_container_width=True)

        # 5. Department Doctor Distribution
        st.subheader("🏢 Doctors per Department")
        df_docs = pd.DataFrame(doctors)
        if not df_docs.empty and "department_id" in df_docs.columns:
            df_docs["Department"] = df_docs["department_id"].map(dept_names)
            df_dept_dist = (
                df_docs.groupby("Department").size().reset_index(name="Doctors")
            )
            fig_dept = px.bar(
                df_dept_dist.sort_values(by="Doctors", ascending=False),
                x="Department",
                y="Doctors",
                color="Doctors",
                color_continuous_scale="Teal",
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.write("No department doctor data available.")

        # 6. Appointment Status Distribution
        st.subheader("📋 Appointment Status Distribution")
        df_status = df_apps.groupby("status").size().reset_index(name="count")
        fig_status = px.pie(
            df_status,
            names="status",
            values="count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        st.plotly_chart(fig_status, use_container_width=True)

# Add logout option in sidebar
if st.sidebar.button("Log Out"):
    st.session_state["token"] = None
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.rerun()
