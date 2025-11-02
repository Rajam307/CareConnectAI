# Single-file Streamlit demo for CareConnectAI (Patient chat, Nurse, Doctor, Admin)
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime

# ---------- DB connection (Neon) ----------
USERNAME = "neondb_owner"
PASSWORD = "npg_hNu4bqHo5EPQ"
HOST = "ep-aged-bread-a1xghr1f-pooler.ap-southeast-1.aws.neon.tech"
DATABASE = "Raaji"

ENGINE_URL = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"
engine = create_engine(ENGINE_URL, future=True)


# ---------- Symptom -> Department map (Final Updated Version) ----------
SYMPTOM_TO_DEPT = {
    # 🩺 General health
    "fever": "General Physician",
    "cough": "General Physician",
    "cold": "General Physician",
    "running nose": "General Physician",
    "sore throat": "ENT",
    "throat": "ENT",
    "food infection": "Gastroenterology",
    "dysentery": "Gastroenterology",
    "gas": "Gastroenterology",
    "acidity": "Gastroenterology",
    "vomit": "Gastroenterology",
    "vomiting": "Gastroenterology",

    # 💪 Pain & musculoskeletal
    "headache": "Neurology",
    "back pain": "Orthopedics",
    "leg pain": "Orthopedics",
    "leg swelling": "Orthopedics",
    "neck pain": "Orthopedics",
    "sprain": "Orthopedics",
    "fracture": "Orthopedics",

    # 👁️ Eye, 👂 Ear, 🦷 Dental
    "eye pain": "Ophthalmology",
    "eyes": "Ophthalmology",
    "vision": "Ophthalmology",
    "tooth ache": "Dentistry",
    "tooth pain": "Dentistry",
    "dental": "Dentistry",
    "ear pain": "ENT",
    "ear infection": "ENT",

    # 💆 Skin & hair
    "rash": "Dermatology",
    "skin": "Dermatology",
    "hair fall": "Dermatology",
    "itching": "Dermatology",

    # ❤️ Chronic / systemic
    "diabetes": "Endocrinology",
    "chest pain": "Cardiology",
    "chest": "Cardiology",

    # 🧠 Mental health
    "anxiety": "Psychiatry",
    "mental depression": "Psychiatry",
    "depression": "Psychiatry",
}




# ---------- Helper functions ----------
def read_df(sql, params=None):
    # Accept sqlalchemy.text or plain SQL string
    return pd.read_sql(text(sql) if not isinstance(sql, str) or sql.strip().upper().startswith("SELECT") else sql, engine, params=params)

def find_user_by_email(email: str):
    q = text("SELECT * FROM users WHERE email = :email LIMIT 1")
    return pd.read_sql(q, engine, params={"email": email})

def find_patient_by_user_id(user_id: str):
    q = text("SELECT * FROM patients WHERE user_id = :uid LIMIT 1")
    return pd.read_sql(q, engine, params={"uid": user_id})

def get_random_doctor_in_dept(department: str):
    # For demo we ignore department matching in users table (unless you have specialty column)
    q = text("SELECT user_id, name FROM users WHERE role = 'Doctor' ORDER BY random() LIMIT 1")
    df = pd.read_sql(q, engine)
    if df.empty:
        return None, None
    return df.iloc[0]["user_id"], df.iloc[0]["name"]

def infer_department_from_text(text):
    t = (text or "").lower()
    for k, v in SYMPTOM_TO_DEPT.items():
        if k in t:
            return v
    return "General Physician"

def create_user_and_patient_if_not_exists(name, email, phone, age, gender):
    # Check user exists
    user_df = find_user_by_email(email)
    if not user_df.empty:
        user_id = user_df.iloc[0]["user_id"]
    else:
        user_id = f"USR-{str(uuid.uuid4())[:6]}"
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO users (user_id, name, email, phone, role, created_at)
                    VALUES (:user_id, :name, :email, :phone, 'Patient', NOW())
                """),
                {"user_id": user_id, "name": name, "email": email, "phone": phone},
            )
    # Check patient exists
    pat_df = find_patient_by_user_id(user_id)
    if not pat_df.empty:
        patient_id = pat_df.iloc[0]["patient_id"]
    else:
        patient_id = f"PAT-{str(uuid.uuid4())[:6]}"
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO patients (patient_id, user_id, age, gender, blood_group)
                    VALUES (:pid, :uid, :age, :gender, 'Unknown')
                """),
                {"pid": patient_id, "uid": user_id, "age": int(age), "gender": gender},
            )
    return user_id, patient_id

def book_appointment(patient_id, department):
    doctor_id, doctor_name = get_random_doctor_in_dept(department)
    if not doctor_id:
        return None, "No doctors available"
    appointment_id = f"APT-{str(uuid.uuid4())[:6]}"
    # schedule default demo slot: today 15:00
    timeslot = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO appointments (appointment_id, patient_id, doctor_id, department, scheduled_time, status, created_at)
                VALUES (:aid, :pid, :did, :dept, :stime, 'Scheduled', NOW())
            """),
            {"aid": appointment_id, "pid": patient_id, "did": doctor_id, "dept": department, "stime": timeslot},
        )
    return appointment_id, f"Appointment booked with Dr. {doctor_name} ({department}) at {timeslot.strftime('%Y-%m-%d %H:%M')}"

# ---------- Streamlit UI ----------
st.set_page_config(page_title="CareConnectAI - demo", layout="wide")
st.title("🏥 CareConnectAI — Live Demo (Patient / Nurse / Doctor / Admin)")

role = st.sidebar.selectbox("Choose role for demo", ["Patient (Chat)", "Nurse", "Doctor", "Admin"])

# -------------------------
# PATIENT: Chat-driven registration & booking (IMPROVED)
# -------------------------
if role == "Patient (Chat)":
    st.header("💬 Patient Chat Assistant — Registration & Appointment Booking")
    st.markdown("The assistant will ask for details step-by-step, then book an appointment based on symptoms.")

    # ---------- Initialize Chat State ----------
    if "chat_initialized" not in st.session_state:
        st.session_state.chat_step = "greet"
        st.session_state.patient_info = {}
        st.session_state.chat_history = []
        st.session_state.chat_history.append(
            ("ai", "Hi, welcome to CareConnect AI - Doctor Consultation Booking Portal. Please tell me your name.")
        )
        st.session_state.chat_initialized = True

    # ---------- Display Chat History ----------
    for who, msg in st.session_state.chat_history:
        if who == "ai":
            st.info(f"🤖 {msg}")
        else:
            st.success(f"🧑 {msg}")

    # ---------- End state handling ----------
    if st.session_state.chat_step == "end":
        st.info("✅ Chat session completed. Thank you for using CareConnect AI!")
        if st.button("🔄 Restart Chat"):
            for key in ["chat_step", "patient_info", "chat_history", "chat_initialized"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.stop()

    # ---------- placeholder map for clarity ----------
    placeholder_map = {
        "greet": "Enter full name (e.g., Arjun Kumar)",
        "ask_age": "Enter age (numbers only)",
        "ask_gender": "Enter gender (Male / Female / Other)",
        "ask_email": "Enter email (e.g., you@example.com)",
        "ask_phone": "Enter phone number (digits only)",
        "await_symptoms": "Describe symptoms (e.g., 'fever and cough')",
        "ask_rebook": "Reply Yes or No",
    }

    # current step
    step = st.session_state.get("chat_step", "greet")
    ph = placeholder_map.get(step, "Type your reply here...")

    # ---------- Chat Input (step-aware placeholder) ----------
    user_text = st.chat_input(ph)


    # ---------- Chat Logic ----------
    if user_text:
        user_input = user_text.strip()
        st.session_state.chat_history.append(("user", user_input))
        step = st.session_state.chat_step

        # -------------- Step 1: Name --------------
        if step == "greet":
            st.session_state.patient_info["name"] = user_input
            st.session_state.chat_step = "ask_age"
            st.session_state.chat_history.append(("ai", f"Thanks {user_input}! Please enter your age."))

        # -------------- Step 2: Age --------------
        elif step == "ask_age":
            try:
                age_val = int(user_input)
                st.session_state.patient_info["age"] = age_val
                st.session_state.chat_step = "ask_gender"
                st.session_state.chat_history.append(("ai", "Great! What is your gender? (Male / Female / Other)"))
            except ValueError:
                st.session_state.chat_history.append(("ai", "Please enter a valid numeric age."))
                st.stop()

        # -------------- Step 3: Gender --------------
        elif step == "ask_gender":
            st.session_state.patient_info["gender"] = user_input.capitalize()
            st.session_state.chat_step = "ask_email"
            st.session_state.chat_history.append(("ai", "Please provide your email."))

        # -------------- Step 4: Email --------------
        elif step == "ask_email":
            st.session_state.patient_info["email"] = user_input
            st.session_state.chat_step = "ask_phone"
            st.session_state.chat_history.append(("ai", "And your phone number?"))

        # -------------- Step 5: Phone --------------
        elif step == "ask_phone":
            st.session_state.patient_info["phone"] = user_input
            st.session_state.chat_step = "await_symptoms"
            st.session_state.chat_history.append(("ai", "✅ Registration completed. Please tell me your symptoms."))

        # -------------- Step 6: Symptoms --------------
        elif step == "await_symptoms":
            symptoms = user_input
            department = infer_department_from_text(symptoms)
            st.session_state.patient_info["symptoms"] = symptoms

            st.session_state.chat_history.append(("ai", "⏳ Please wait while we process your appointment..."))
            st.session_state.chat_step = "processing"
            st.rerun()

        # -------------- Step 7: Processing Appointment --------------
        elif step == "processing":
            info = st.session_state.patient_info
            try:
                _, patient_id = create_user_and_patient_if_not_exists(
                    info["name"], info["email"], info["phone"], info["age"], info["gender"]
                )
                apt_id, msg = book_appointment(patient_id, infer_department_from_text(info["symptoms"]))
                if apt_id:
                    st.session_state.chat_history.append(("ai", f"I detected your symptoms → {infer_department_from_text(info['symptoms'])}. {msg} (Appointment ID: {apt_id})"))
                    st.session_state.chat_history.append(("ai", "Would you like to book another appointment? (Yes / No)"))
                    st.session_state.chat_step = "rebook"
                else:
                    st.session_state.chat_history.append(("ai", "⚠️ Sorry, could not book your appointment."))
                    st.session_state.chat_step = "end"
            except Exception as e:
                st.session_state.chat_history.append(("ai", f"Error while saving to DB: {e}"))
                st.session_state.chat_step = "end"
            st.rerun()

        # -------------- Step 8: Rebooking Option --------------
        elif step == "rebook":
            if user_input.lower() in ["yes", "y"]:
                for key in ["chat_step", "patient_info", "chat_history", "chat_initialized"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            else:
                st.session_state.chat_history.append(("ai", "🙏 Thank you and get well soon! ❤️"))
                st.session_state.chat_step = "end"

        st.rerun()

# ---------- Auto-run booking if waiting to process ----------
    if st.session_state.chat_step == "processing":
        info = st.session_state.patient_info
        try:
            _, patient_id = create_user_and_patient_if_not_exists(
                info["name"], info["email"], info["phone"], info["age"], info["gender"]
            )
            apt_id, msg = book_appointment(patient_id, infer_department_from_text(info["symptoms"]))
            if apt_id:
                st.session_state.chat_history.append(("ai", f"I detected your symptoms → {infer_department_from_text(info['symptoms'])}. {msg} (Appointment ID: {apt_id})"))
                st.session_state.chat_history.append(("ai", "Would you like to book another appointment? (Yes / No)"))
                st.session_state.chat_step = "rebook"
            else:
                st.session_state.chat_history.append(("ai", "⚠️ Sorry, could not book your appointment."))
                st.session_state.chat_step = "end"
        except Exception as e:
            st.session_state.chat_history.append(("ai", f"Error while saving to DB: {e}"))
            st.session_state.chat_step = "end"
        st.rerun()
  


# -------------------------
# NURSE: Select appointment & log vitals
# -------------------------
elif role == "Nurse":
    st.header("🩺 Nurse — Log Vitals")
    st.markdown("Select a scheduled appointment (shows appointment_id, patient_id, patient name). Then record vitals.")

    appts = pd.read_sql(
        text("""
            SELECT a.appointment_id, a.patient_id, u.name AS patient_name, a.department, a.scheduled_time
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.status = 'Scheduled'
            ORDER BY a.scheduled_time ASC
            LIMIT 200
        """),
        engine
    )

    if appts.empty:
        st.info("No scheduled appointments found.")
    else:
        appts["label"] = appts.apply(lambda r: f"{r['appointment_id']} — {r['patient_name']} ({r['patient_id']}) — {r['department']}", axis=1)
        choice = st.selectbox("Choose appointment to log vitals for", appts["label"].tolist())
        if choice:
            selected_pid = choice.split("(")[-1].replace(")","").strip()
            st.write("Selected Patient ID:", selected_pid)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                temp = st.number_input("Temperature °C", min_value=30.0, max_value=45.0, value=37.0, step=0.1)
            with col2:
                bp = st.text_input("Blood Pressure", value="120/80")
            with col3:
                pulse = st.number_input("Pulse (bpm)", min_value=30, max_value=200, value=80)
            with col4:
                spo2 = st.number_input("SpO2 (%)", min_value=50, max_value=100, value=97)

            notes = st.text_input("Notes", value="Logged by nurse")

            if st.button("💾 Save Vitals"):
                vital_id = f"VTL-{str(uuid.uuid4())[:6]}"
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO vitals (vital_id, patient_id, nurse_id, temperature, blood_pressure, pulse, spo2, notes, recorded_at)
                            VALUES (:vid, :pid, :nid, :temp, :bp, :pulse, :spo2, :notes, NOW())
                        """),
                        {"vid": vital_id, "pid": selected_pid, "nid": "USR-00004", "temp": float(temp), "bp": bp, "pulse": int(pulse), "spo2": int(spo2), "notes": notes},
                    )
                st.success(f"✅ Vitals saved (ID: {vital_id}) for patient {selected_pid}")

# -------------------------
# DOCTOR: view vitals/reports, prescribe, discharge
# -------------------------
elif role == "Doctor":
    st.header("🧑‍⚕️ Doctor Console — View patients, prescribe, discharge")
    st.markdown("Select a patient to view vitals and reports. You can add a prescription or sign a discharge summary.")

    recent = pd.read_sql(
        text("""
            SELECT DISTINCT p.patient_id, u.name AS patient_name, u.email
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            ORDER BY a.created_at DESC
            LIMIT 200
        """),
        engine
    )

    if recent.empty:
        st.info("No recent patients found.")
    else:
        selected = st.selectbox("Select patient", recent.apply(lambda r: f"{r['patient_id']} — {r['patient_name']}", axis=1))
        if selected:
            sel_pid = selected.split("—")[0].strip()
            st.subheader("Recent vitals")
            vit = pd.read_sql(text("SELECT vital_id, temperature, blood_pressure, pulse, spo2, notes, recorded_at FROM vitals WHERE patient_id=:pid ORDER BY recorded_at DESC LIMIT 10"), engine, params={"pid": sel_pid})
            st.dataframe(vit, use_container_width=True)

            st.subheader("Medical reports")
            reps = pd.read_sql(text("SELECT report_id, report_type, file_url, extracted_text, uploaded_at FROM medical_reports WHERE patient_id=:pid ORDER BY uploaded_at DESC LIMIT 10"), engine, params={"pid": sel_pid})
            st.dataframe(reps, use_container_width=True)

            st.subheader("Add prescription")
            med = st.text_input("Medication (e.g., Paracetamol 500mg)")
            dosage = st.text_input("Dosage (e.g., 1 tablet x 3/day)")
            instr = st.text_area("Instructions")
            if st.button("💊 Save Prescription"):
                rx = f"RX-{str(uuid.uuid4())[:6]}"
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO prescriptions (prescription_id, patient_id, doctor_id, medication, dosage, instructions, prescribed_at, fulfilled)
                            VALUES (:rx, :pid, :doc, :med, :dos, :ins, NOW(), False)
                        """),
                        {"rx": rx, "pid": sel_pid, "doc": "USR-00003", "med": med, "dos": dosage, "ins": instr},
                    )
                st.success(f"✅ Prescription saved (ID: {rx})")

            st.subheader("Add & Sign Discharge Summary")
            dtext = st.text_area("Discharge summary text", value="Patient stable. Follow-up in 7 days.")
            if st.button("📝 Sign & Save Discharge"):
                dsc = f"DSC-{str(uuid.uuid4())[:6]}"
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO discharge_summaries (discharge_id, patient_id, doctor_id, summary_text, created_at, signed_at)
                            VALUES (:did, :pid, :doc, :txt, NOW(), NOW())
                        """),
                        {"did": dsc, "pid": sel_pid, "doc": "USR-00003", "txt": dtext},
                    )
                st.success(f"✅ Discharge summary saved (ID: {dsc})")

# -------------------------
# ADMIN: KPIs & quick tables
# -------------------------
elif role == "Admin":
    st.header("🧑‍💼 Admin Dashboard — KPIs & Quick Ops")

    # KPIs
    total_patients = pd.read_sql(text("SELECT COUNT(*) as n FROM patients"), engine).iloc[0]["n"]
    total_doctors = pd.read_sql(text("SELECT COUNT(*) as n FROM users WHERE role='Doctor'"), engine).iloc[0]["n"]
    total_nurses = pd.read_sql(text("SELECT COUNT(*) as n FROM users WHERE role='Nurse'"), engine).iloc[0]["n"]
    appts_today = pd.read_sql(text("SELECT COUNT(*) as n FROM appointments WHERE DATE(created_at) = CURRENT_DATE"), engine).iloc[0]["n"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total patients", total_patients)
    c2.metric("Doctors", total_doctors)
    c3.metric("Nurses", total_nurses)
    c4.metric("Appts today", appts_today)

    st.markdown("### Appointments by department")
    dept = pd.read_sql(text("SELECT department, COUNT(*) as total FROM appointments GROUP BY department ORDER BY total DESC LIMIT 20"), engine)
    if not dept.empty:
        st.bar_chart(dept.set_index("department"))

    st.markdown("### Quick tables (today)")
    t1, t2, t3 = st.tabs(["Appointments (today)", "Reports (today)", "Discharges (today)"])
    with t1:
        df_ap = pd.read_sql(text("""
            SELECT a.appointment_id, p.patient_id, u.name AS patient_name, d.name AS doctor_name, a.department, a.scheduled_time, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            JOIN users d ON a.doctor_id = d.user_id
            WHERE DATE(a.created_at) = CURRENT_DATE
            ORDER BY a.created_at DESC
            LIMIT 50
        """), engine)
        st.dataframe(df_ap, use_container_width=True)
    with t2:
        df_r = pd.read_sql(text("""
            SELECT r.report_id, p.patient_id, u.name AS patient_name, r.report_type, r.file_url, r.uploaded_at
            FROM medical_reports r
            JOIN patients p ON r.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE DATE(r.uploaded_at) = CURRENT_DATE
            ORDER BY r.uploaded_at DESC
            LIMIT 50
        """), engine)
        st.dataframe(df_r, use_container_width=True)
    with t3:
        df_d = pd.read_sql(text("""
            SELECT d.discharge_id, p.patient_id, u.name AS patient_name, d.summary_text, d.created_at
            FROM discharge_summaries d
            JOIN patients p ON d.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE DATE(d.created_at) = CURRENT_DATE
            ORDER BY d.created_at DESC
            LIMIT 50
        """), engine)
        st.dataframe(df_d, use_container_width=True)


