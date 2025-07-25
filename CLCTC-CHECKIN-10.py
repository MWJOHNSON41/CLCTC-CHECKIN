import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# --- Config ---
DATA_FILE = "checkin_log.csv"
ADMIN_PIN = "2025"

st.set_page_config(page_title="CTC Staff Check-In / Check-Out", layout="centered")
st.title("📝 CTC Staff Check-In / Check-Out")

# --- Load existing data or create empty DataFrame ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Department", "Location", "Status", "Time", "Notes", "Flight Name"])

# --- Initialize session state variables ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

# --- Staff Check-in/out Form ---
with st.form("checkin_form"):
    name = st.text_input("Enter your name:")
    department = st.text_input("Enter your department:")
    location = st.selectbox("Current Location:", [
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
            st.error("Please enter at least your name and department.")
        elif ("aviation" in department.lower() or "survival" in department.lower()) and not flight_name:
            st.error("Flight Name is required for Aviation or Survival departments.")
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
            # Append new record to dataframe and save CSV
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Submitted!")

st.markdown("---")

# --- Admin Section ---
st.subheader("🔒 Ops Dashboard (Admin Access Only)")

if not st.session_state.admin_logged_in:
    admin_pin = st.text_input("Enter Admin PIN:", type="password")
    if admin_pin == ADMIN_PIN:
        st.session_state.admin_logged_in = True
        st.experimental_rerun()
    elif admin_pin != "":
        st.error("Incorrect PIN.")
else:
    st.success("Access granted. You are logged in as Admin.")

    # Auto-refresh every 10 seconds using Python timer and rerun
    refresh_interval = 10  # seconds
    current_time = time.time()

    if current_time - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = current_time
        st.experimental_rerun()

    # Reload latest data for admin dashboard
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        st.info("No data file found.")
        df = pd.DataFrame(columns=["Name", "Department", "Location", "Status", "Time", "Notes", "Flight Name"])

    # Show grouped check-ins separately for Location and Department
    checked_in = df[df["Status"] == "Check In"]

    st.write("### 📍 Current Check-Ins by Location")
    grouped_location = checked_in.groupby("Location")["Name"].count().reset_index()
    grouped_location.columns = ["Location", "Total Checked In"]
    st.dataframe(grouped_location, use_container_width=True)

    st.write("### 🏢 Current Check-Ins by Department")
    grouped_department = checked_in.groupby("Department")["Name"].count().reset_index()
    grouped_department.columns = ["Department", "Total Checked In"]
    st.dataframe(grouped_department, use_container_width=True)

    st.write("### 📋 Full Check-In/Out Log (most recent first)")
    st.dataframe(df.iloc[::-1], use_container_width=True)

