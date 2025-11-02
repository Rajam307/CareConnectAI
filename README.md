🏥 CareConnect AI — “Talk It. Track It. Treat It.”

CareConnect AI is an AI-powered hospital assistant that connects Patients, Nurses, Doctors, and Admins in one unified platform.
It automates appointment booking, vitals logging, prescriptions, discharge summaries, and hospital analytics using Conversational AI, OCR, and RAG (Retrieval-Augmented Generation).

🚀 Project Overview

Hospitals often struggle with disconnected systems and paperwork.
CareConnect AI provides one intelligent interface to:

🧑‍⚕️ Help patients book appointments and upload reports

👩‍⚕️ Assist nurses in logging vitals and generating summaries

👨‍⚕️ Give doctors instant access to patient history and e-prescriptions

🏥 Support admins with dashboards and analytics

⚙️ Key Features

🤖 Chat-based AI assistant for patients and staff

🩺 Smart nurse vitals logging with alerts

👨‍⚕️ Doctor 360° view of patient data

📊 Admin dashboard for operations and reports

🔒 Role-Based Access (Patient, Nurse, Doctor, Admin)

🧠 NLP + OCR + TF-IDF embeddings for intelligent retrieval

🧰 Tech Stack

Frontend: Streamlit

Backend: Python (FastAPI / Flask)

AI/NLP: Hugging Face, scikit-learn, LangChain

Database: PostgreSQL / Neon / AWS RDS

Cloud: AWS S3 (for file storage)

Deployment: Docker

Security: RBAC, JWT, Data Encryption

📂 Project Structure
CARECONNECTAI/
│
├── CareConnectAI_DataPrep.ipynb   # Data preprocessing & model training
├── demo.py                        # Core logic (roles & workflows)
├── dashboard_app.py               # Streamlit main app
├── dashboard_charts.py            # Admin charts & analytics
├── db_connect.py                  # Database connection helper
├── scripts/migrate_db.sql         # Database schema
├── data/, data_cleaned/           # Datasets
├── tfidf_model.pkl                # TF-IDF model (not uploaded)
├── tfidf_embeddings.pkl           # Embeddings (not uploaded)
└── README.md                      # Project documentation

🧠 Model Files (TF-IDF & Embeddings)

To keep the repository lightweight, .pkl files are not uploaded.
You can recreate them locally:

Open the notebook:

CareConnectAI_DataPrep.ipynb


Run all cells — this will:

Train the TF-IDF model

Generate embeddings

Save two files:

tfidf_model.pkl
tfidf_embeddings.pkl


These files are automatically loaded by the app when present.

💡 You can also download pretrained models from your shared Google Drive link (optional).

⚙️ Installation
git clone <repo-url>
cd CARECONNECTAI
python -m venv venv
venv\Scripts\activate      # (Windows)
# or source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
streamlit run dashboard_app.py


Create a .env file in the root directory:

DB_HOST=your-db-host
DB_NAME=careconnect
DB_USER=your-user
DB_PASS=your-password

💻 How to Use
Role	Functionality
Patient	Book appointments, upload reports, view status
Nurse	Log vitals, generate discharge summaries
Doctor	View patient records, issue e-prescriptions
Admin	Monitor hospital load, staff, and analytics

Run the app locally:

streamlit run dashboard_app.py

📊 Database Tables

Main tables used in the project:

users

patients

appointments

vitals

medical_reports

prescriptions

discharge_summaries

admin_logs

🧪 Evaluation Focus

✅ AI accuracy for query understanding

✅ Appointment & vitals workflow performance

✅ OCR extraction precision

✅ Dashboard analytics correctness

✅ Role-based access and security

👩‍💻 Author

Developed by Rajalakshmi
📧 Email: raji.rajam@gmail.com

🔗 GitHub: https://github.com/Rajam307

✅ Quick Checklist

 Code organized & documented

 .env file added (not committed)

 .pkl files regenerated locally

 App runs with streamlit run dashboard_app.py
