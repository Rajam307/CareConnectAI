# ==============================
# CareConnectAI - Dashboard (Step 6 + Step 7)
# File: dashboard_app.py
# ==============================

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime

# ------------------------------
# Database Connection
# ------------------------------
username = "neondb_owner"
password = "npg_hNu4bqHo5EPQ"
host = "ep-aged-bread-a1xghr1f-pooler.ap-southeast-1.aws.neon.tech"
database = "Raaji"

engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}/{database}")

st.set_page_config(page_title="CareConnectAI Dashboard", layout="wide")

st.title("📊 CareConnectAI - Hospital Dashboard")

# ------------------------------
# Load Data Function
# ------------------------------
def load_data(query):
    return pd.read_sql(query, engine)

# ------------------------------
# Tabs for Dashboard Sections
# ------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Appointments", "Vitals", "Prescriptions", "Reports"])

# ---- Appointments ----
with tab1:
    st.subheader("📅 Appointments Overview")
    query = """
        SELECT a.appointment_id, u.name AS patient_name, d.name AS doctor_name, 
               a.department, a.scheduled_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        JOIN users d ON a.doctor_id = d.user_id
        ORDER BY a.created_at DESC LIMIT 20;
    """
    df = load_data(query)
    st.dataframe(df, use_container_width=True)

# ---- Vitals ----
with tab2:
    st.subheader("🩺 Latest Vitals Records")
    query = """
        SELECT v.vital_id, u.name AS patient_name, v.temperature, v.blood_pressure, 
               v.pulse, v.spo2, v.recorded_at
        FROM vitals v
        JOIN patients p ON v.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        ORDER BY v.recorded_at DESC LIMIT 20;
    """
    df = load_data(query)
    st.dataframe(df, use_container_width=True)

# ---- Prescriptions ----
with tab3:
    st.subheader("💊 Prescriptions")
    query = """
        SELECT pr.prescription_id, u.name AS patient_name, d.name AS doctor_name, 
               pr.medication, pr.dosage, pr.instructions, pr.prescribed_at
        FROM prescriptions pr
        JOIN patients p ON pr.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        JOIN users d ON pr.doctor_id = d.user_id
        ORDER BY pr.prescribed_at DESC LIMIT 20;
    """
    df = load_data(query)
    st.dataframe(df, use_container_width=True)

# ---- Reports ----
with tab4:
    st.subheader("📄 Medical Reports")
    query = """
        SELECT r.report_id, u.name AS patient_name, r.report_type, r.file_url, r.uploaded_at
        FROM medical_reports r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        ORDER BY r.uploaded_at DESC LIMIT 20;
    """
    df = load_data(query)
    st.dataframe(df, use_container_width=True)

st.success("✅ Dashboard loaded successfully!")

# ------------------------------
# 🔔 Step 7: Dummy Notifications / Alerts
# ------------------------------
st.markdown("---")
st.subheader("🔔 Notifications & Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚨 Abnormal Vitals Alert"):
        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO admin_logs (log_id, user_id, action, target_entity, timestamp, details)
                VALUES ('LOG-{uuid.uuid4().hex[:5]}', 'USR-00004', 'Vitals Alert',
                        'Vitals', NOW(), 'High BP/Low SpO2 detected for a patient');
            """))
        st.warning("⚠️ Alert generated: Abnormal vitals flagged to doctors.")

with col2:
    if st.button("📄 New Report Uploaded"):
        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO admin_logs (log_id, user_id, action, target_entity, timestamp, details)
                VALUES ('LOG-{uuid.uuid4().hex[:5]}', 'USR-00001', 'Report Upload',
                        'MedicalReports', NOW(), 'New X-Ray report uploaded.');
            """))
        st.info("📄 Notification: New medical report uploaded and logged.")

with col3:
    if st.button("✅ Discharge Summary Ready"):
        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO admin_logs (log_id, user_id, action, target_entity, timestamp, details)
                VALUES ('LOG-{uuid.uuid4().hex[:5]}', 'USR-00012', 'Discharge Summary',
                        'DischargeSummaries', NOW(), 'Auto-generated summary signed by doctor.');
            """))
        st.success("✅ Notification: Discharge summary created and signed.")
# ==============================
# Step 9: Notifications & Quick Actions (with demo buttons)
# ==============================
import uuid
from sqlalchemy import text

st.markdown("---")
st.header("🔔 Notifications & Quick Actions")

# Create 3 sub-tabs inside Notifications
notif1, notif2, notif3 = st.tabs(["🚨 Abnormal Vitals", "📄 New Reports", "📃 Discharge Summaries"])

# ---- Abnormal Vitals Alert ----
with notif1:
    st.subheader("🚨 Abnormal Vital Alerts")

    # Quick Action Button to insert a dummy abnormal vital
    if st.button("⚡ Simulate Abnormal Vital Entry"):
        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO vitals (vital_id, patient_id, nurse_id, temperature, blood_pressure, pulse, spo2, notes, recorded_at)
                VALUES ('VTL-{str(uuid.uuid4())[:5]}', 'PAT-2a114', 'USR-00004', 39.5, '160/100', 120, 90, 'Demo abnormal vitals', NOW());
            """))
        st.success("✅ Dummy abnormal vital inserted!")

    query = """
        SELECT v.vital_id, u.name AS patient_name, v.temperature, v.blood_pressure, v.pulse, v.spo2, v.recorded_at
        FROM vitals v
        JOIN patients p ON v.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        WHERE v.temperature > 38.0 OR v.spo2 < 95 OR v.pulse > 100
        ORDER BY v.recorded_at DESC
        LIMIT 10;
    """
    df = load_data(query)
    if df.empty:
        st.info("✅ No abnormal vitals detected today.")
    else:
        st.warning("⚠️ Abnormal vitals flagged to doctors!")
        st.dataframe(df, use_container_width=True)

# ---- New Report Uploaded ----
with notif2:
    st.subheader("📄 Newly Uploaded Reports")

    if st.button("⚡ Simulate Report Upload"):
        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO medical_reports (report_id, patient_id, uploaded_by, report_type, file_url, uploaded_at)
                VALUES ('RPT-{str(uuid.uuid4())[:5]}', 'PAT-2a114', 'USR-00003', 'Lab', 's3://demo/new_report.pdf', NOW());
            """))
        st.success("✅ Dummy medical report inserted!")

    query = """
        SELECT r.report_id, u.name AS patient_name, r.report_type, r.file_url, r.uploaded_at
        FROM medical_reports r
        JOIN patients p ON r.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        WHERE DATE(r.uploaded_at) = CURRENT_DATE
        ORDER BY r.uploaded_at DESC
        LIMIT 10;
    """
    df = load_data(query)
    if df.empty:
        st.info("ℹ️ No new reports uploaded today.")
    else:
        st.success("📢 New reports available for doctor review.")
        st.dataframe(df, use_container_width=True)

# ---- Discharge Summaries Ready ----
with notif3:
    st.subheader("📃 Discharge Summaries Ready")

    if st.button("⚡ Simulate Discharge Summary"):
        with engine.begin() as conn:
            conn.execute(text(f"""
                INSERT INTO discharge_summaries (discharge_id, patient_id, doctor_id, summary_text, created_at, signed_at)
                VALUES ('DSC-{str(uuid.uuid4())[:5]}', 'PAT-2a114', 'USR-00003', 'Demo: Patient stable, follow-up in 5 days.', NOW(), NOW());
            """))
        st.success("✅ Dummy discharge summary inserted!")

    query = """
        SELECT d.discharge_id, u.name AS patient_name, d.summary_text, d.created_at
        FROM discharge_summaries d
        JOIN patients p ON d.patient_id = p.patient_id
        JOIN users u ON p.user_id = u.user_id
        WHERE DATE(d.created_at) = CURRENT_DATE
        ORDER BY d.created_at DESC
        LIMIT 10;
    """
    df = load_data(query)
    if df.empty:
        st.info("✅ No discharge summaries generated today.")
    else:
        st.success("📢 New discharge summaries ready for patient handover.")
        st.dataframe(df, use_container_width=True)

