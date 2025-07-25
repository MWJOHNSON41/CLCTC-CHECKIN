import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# --- Configuration ---
DATA_FILE = "checkin_log.csv"
ADMIN_PIN = "2025"

st.set_page_config(page_title="CTC Staff Check-In / Check-Out", layout="centered")
st.title("📝 CTC Staff Check-In / Check-Out")

# --- Load CSV or create empty ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Department", "Location", "Status", "Time", "Notes", "Flight Name"])

# --- Session state initialization ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = time.time()

# --- Check-In / Check-Out Form ---
with st.form("checkin_form"):
    name = st.text_input("Enter your name:")
    department = st.text_input("Enter your department:")
    location = st.selectbox("Select your location:", [
        "Main Training Site", "Survival FTA", "LegoLand", "City of Cold Lake", "Other"
    ])
    status = st.radio("Status:", ["Check In", "Check Out"])
    notes = st.text_input("Optional notes (e.g. ETA 1600):")

    flight_name = ""
    if "aviation" in department.lower() or "survival" in department.lower():
        flight_name = st.text_input("Flight Name (required for Aviation/Survival):")

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not name or not department:
            st.error("Please enter your name and department.")
        elif ("aviation" in department.lower() or "survival" in department.lower()) and not flight_name:
            st.error("Flight Name is required for Aviation/Survival.")
        else:
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record = {
                "Name": name,
                "Department": department,
                "Location": location,
                "Status": status,
                "Time": time_now,
                "Notes": notes,
                "Flight Name": flight_name if flight_name else ""
            }

            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Check-In/Out submitted!")

# --- Divider ---
st.markdown("---")

# --- Admin Panel ---
st.subheader("🔒 Admin Dashboard")

if not st.session_state.admin_logged_in:
    admin_pin = st.text_input("Enter Admin PIN:", type="password")
    if admin_pin == ADMIN_PIN:
        st.session_state.admin_logged_in = True
        st.rerun()
    elif admin_pin != "":
        st.error("Incorrect PIN.")
else:
    st.success("Access granted. Admin mode active.")

    # Refresh admin section every 10 seconds
    refresh_interval = 10  # seconds
    if time.time() - st.session_state.last_refresh_time > refresh_interval:
        st.session_state.last_refresh_time = time.time()
        st.rerun()

    # Load updated data
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # Display current check-ins by Location
        checked_in_df = df[df["Status"] == "Check In"]
        location_summary = checked_in_df.groupby("Location")["Name"].count().reset_index()
        location_summary.columns = ["Location", "Total Checked In"]
        st.write("### 📍 Check-Ins by Location")
        st.dataframe(location_summary, use_container_width=True)

        # Display current check-ins by Department
        department_summary = checked_in_df.groupby("Department")["Name"].count().reset_index()
        department_summary.columns = ["Department", "Total Checked In"]
        st.write("### 🏢 Check-Ins by Department")
        st.dataframe(department_summary, use_container_width=True)

        # Full log
        st.write("### 📋 Full Check-In/Out Log (most recent first)")
        st.dataframe(df.iloc[::-1], use_container_width=True)
    else:
        st.info("No data file found.")

