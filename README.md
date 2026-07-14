# MediBook - Clinic Appointment Management System

MediBook is a production-style, role-based Clinic Appointment Management System. It allows clinic administrators, receptionists, and doctors to coordinate patient registrations, appointment bookings, consultation medical records, and document attachments (X-Rays, PDFs) under secure, role-based controls. It also includes an administrative analytics dashboard built with Streamlit.

---

## Features

- **Authentication & Security**: Argon2 password hashing and JWT signatures for role-based authorization.
- **Clinic Registry**: Manage departments and doctor profiles.
- **Patient Registry**: 중앙화된 환자 관리(Centralized patient registry) with search parameters.
- **Appointment Scheduling**: Smart slot reservation preventing double bookings or overlapping schedules within a 30-minute window for doctors and patients.
- **Medical Records**: One-to-One appointment diagnosis, prescription logs, and follow-up entries.
- **File Uploads**: Attach attachments (PDFs, X-Rays, reports) directly to patient profiles with secure unique UUID file naming and disk removal cascading.
- **Advanced Querying**: Search engines utilizing subqueries, inner joins, date ranges, and experience thresholds.
- **Interactive Analytics**: Administrative dashboard rendering total stats and Plotly charts showing appointment trends, workloads, and distributions.

---

## Role-Based Access Matrix

| Feature | Admin | Doctor | Receptionist |
|---|---|---|---|
| Manage Departments & Doctors | Write / Read | Read Only | Read Only |
| Manage Patients | Write / Read | Read Only | Write / Read |
| Book & Reschedule Appointments | Write / Read | Read Only | Write / Read |
| Manage Medical Records | Write / Read | Write / Read (Assigned Only) | Read Only |
| Upload Patient Documents | Write / Read | Write / Read | Write / Read |
| View Analytics Dashboard | Full Access | Full Access | Full Access |

---

## Installation & Setup

### Option 1: Local Development

1. **Clone the Repository** and navigate to the project directory:
   ```bash
   cd medibook
   ```

2. **Setup Virtual Environment** (Python 3.9 recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables**:
   Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
   Fill in your configuration credentials (default settings will work out-of-the-box for local dev).

5. **Run the Backend API Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The interactive Swagger documentation will be accessible at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

6. **Run the Analytics Dashboard**:
   In a separate terminal window, with the virtual environment activated, run:
   ```bash
   streamlit run dashboard/streamlit_app.py
   ```
   The dashboard will open automatically in your browser at: [http://localhost:8501](http://localhost:8501)

---

### Option 2: Docker Compose (Production Readiness)

Deploy both the backend and dashboard containers instantly:

1. **Build and Run Containers**:
   ```bash
   docker compose up --build
   ```

2. **Access Links**:
   - **FastAPI Backend Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Streamlit Analytics Dashboard**: [http://localhost:8501](http://localhost:8501)

3. **Data Persistence**:
   - SQLite database is saved to `./data/medibook.db` on your local host.
   - Uploaded documents are persistent under `./uploads` on your local host.

---

## API Endpoint Reference

### 🔐 Authentication
- `POST /auth/register` - Create user (Admin, Doctor, Receptionist roles)
- `POST /auth/login` - Obtain JWT token
- `GET /users/me` - Retrieve current user profile

### 🏢 Clinic Management
- `GET /departments` - List departments
- `POST /departments` - Create department (Admin only)
- `GET /doctors` - Search doctors (Filters: `department_id`, `experience_min`, `available_at`)
- `POST /doctors` - Create doctor profile (Admin only)

### 👥 Patient Management
- `GET /patients` - Search patients (Filters: `name`, `phone`, `blood_group`, `gender`)
- `POST /patients` - Register patient (Admin/Receptionist only)
- `GET /patients/{id}` - View patient details

### 📅 Appointment Scheduling
- `POST /appointments` - Book appointment
- `GET /appointments` - List/filter appointments (Filters: `doctor_id`, `patient_id`, `status_val`, `start_date`, `end_date`, `department_id`)
- `PUT /appointments/{id}/reschedule` - Reschedule appointment
- `PUT /appointments/{id}/status` - Modify status (`Scheduled`, `Completed`, `Cancelled`, `Rescheduled`)

### 📋 Medical Records
- `POST /medical-records` - Record consultation outcome (Doctor/Admin only, automatically completes appointment)
- `GET /medical-records` - List medical records
- `GET /medical-records/{id}` - Retrieve details
- `PUT /medical-records/{id}` - Update record (Doctor/Admin only)

### 📁 Document Uploads
- `POST /patients/{patient_id}/documents` - Upload patient file (PDF, X-Ray, etc.)
- `GET /patients/{patient_id}/documents` - List patient attachments
- `GET /patients/{patient_id}/documents/{document_id}/download` - Download file
- `DELETE /patients/{patient_id}/documents/{document_id}` - Delete file
