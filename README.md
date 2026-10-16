# 🏥 Healthcare Application Backend

A robust, secure, and production-ready backend system for a healthcare application built using **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT Authentication** (`djangorestframework-simplejwt`).

The system enables secure user registration, token-based authentication, management of patient and doctor records, and assignment mappings between patients and doctors.

---

## 📋 Features

- **JWT Authentication**: Secure user registration and login with JSON Web Tokens (`access` and `refresh` tokens) via SimpleJWT.
- **Custom User Model**: Authentication via unique email address and name.
- **Patient Management**: Full CRUD capabilities with multi-tenant privacy—authenticated users can only list and manage their own created patient records.
- **Doctor Management**: Full CRUD capabilities for medical professionals with specialized fields (specialization, experience, hospital affiliation, contact info).
- **Patient-Doctor Mapping**: Assign doctors to patients with duplicate-assignment prevention, retrieve all doctors assigned to any patient, and remove mappings.
- **PostgreSQL Database**: Configured with Django ORM for enterprise-grade relational integrity.
- **Interactive OpenAPI 3.0 & Swagger UI**: Built-in interactive API documentation at `/api/docs/` and `/api/redoc/` powered by `drf-spectacular`.
- **Dockerized Deployment**: Complete `Dockerfile` and `docker-compose.yml` for instant 1-command startup.
- **Production-Ready**: `whitenoise` for compressed static assets, `gunicorn` WSGI server, and strict environment configuration.
- **Standardized Error Handling**: Custom exception handler delivering clear, unified JSON error responses across all endpoints.
- **Testing & Verification**: 24 automated unit tests + end-to-end verification script + importable Postman collection.

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.10+
- **Framework**: Django 5.x
- **API Framework**: Django REST Framework (DRF) 3.18+
- **Authentication**: `djangorestframework-simplejwt`
- **Documentation**: `drf-spectacular` (OpenAPI 3.0 / Swagger UI / ReDoc)
- **Database**: PostgreSQL 16+
- **Database Driver**: `psycopg2-binary`
- **WSGI Production Server**: `gunicorn`
- **Static Assets Handler**: `whitenoise`
- **Environment Management**: `python-dotenv`
- **CORS Support**: `django-cors-headers`
- **Containerization**: Docker & Docker Compose

---

## 📁 Project Structure

```
Django_Assignment/
├── .env                              # Environment variables (DB credentials, secret key)
├── .env.example                      # Example template for environment configuration
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── manage.py                         # Django management entry point
├── verify_api.py                     # E2E live API verification script
├── postman_collection.json           # Importable Postman collection
│
├── healthcare_project/               # Project configuration
│   ├── __init__.py
│   ├── settings.py                   # DRF, SimpleJWT, Database, CORS settings
│   ├── urls.py                       # Root URL routing & API discovery
│   ├── wsgi.py
│   └── asgi.py
│
├── authentication/                   # User authentication & JWT
│   ├── models.py                     # Custom User model (email-based)
│   ├── serializers.py                # Register & Login serializers
│   ├── views.py                      # RegisterView, LoginView, ProfileView
│   ├── urls.py                       # /api/auth/ routes
│   └── tests.py                      # Auth test suite
│
├── patients/                         # Patient management
│   ├── models.py                     # Patient entity
│   ├── permissions.py                # Creator/Staff permissions
│   ├── serializers.py                # Validated patient serializer
│   ├── views.py                      # PatientListCreateView, PatientDetailView
│   ├── urls.py                       # /api/patients/ routes
│   └── tests.py                      # Patient test suite
│
├── doctors/                          # Doctor management
│   ├── models.py                     # Doctor entity
│   ├── serializers.py                # Validated doctor serializer
│   ├── views.py                      # DoctorListCreateView, DoctorDetailView
│   ├── urls.py                       # /api/doctors/ routes
│   └── tests.py                      # Doctor test suite
│
├── mappings/                         # Patient-Doctor relationships
│   ├── models.py                     # PatientDoctorMapping entity
│   ├── serializers.py                # Mapping & nested representation serializers
│   ├── views.py                      # Mapping list/create, detail/delete views
│   ├── urls.py                       # /api/mappings/ routes
│   └── tests.py                      # Mapping test suite
│
└── common/                           # Shared utilities
    ├── exceptions.py                 # Unified custom DRF exception handler
    └── management/commands/
        └── seed_data.py              # Sample data generator command
```

---

## 🚀 Setup & Installation

### 1. Clone & Navigate to Repository
```bash
cd c:\Users\yachn\Documents\Django_Assignment
```

### 2. Activate Virtual Environment
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat

# Linux / macOS
source venv/bin/activate
```

*(If creating a new virtual environment: `python -m venv venv`)*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (based on `.env.example`):
```ini
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# PostgreSQL Database Configuration
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# JWT Settings
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

### 5. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed Sample Data (Optional but Recommended)
Populates realistic users, doctors, patients, and mappings:
```bash
python manage.py seed_data
```

**Pre-seeded Test Accounts:**
- **Admin**: `admin@healthcare.test` / `Admin@12345`
- **Staff User**: `staff@healthcare.test` / `Staff@12345`

### 7. Run the Development Server
```bash
python manage.py runserver
```
Server runs at `http://127.0.0.1:8000/`.

---

## 📡 API Endpoints Reference

All requests requiring authentication must include the JWT token in the `Authorization` header:
```http
Authorization: Bearer <your_access_token>
```

### 1. Authentication APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user with name, email, and password | No |
| `POST` | `/api/auth/login/` | Log in with email & password, return JWT tokens | No |
| `POST` | `/api/auth/token/refresh/` | Refresh expired access token | No |
| `GET` | `/api/auth/profile/` | Get current user's profile | **Yes** |

#### Register User
`POST /api/auth/register/`
```json
{
  "name": "Dr. House",
  "email": "house@hospital.test",
  "password": "Password123!"
}
```
**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "name": "Dr. House",
    "email": "house@hospital.test"
  },
  "tokens": {
    "refresh": "eyJhbGciOi...",
    "access": "eyJhbGciOi..."
  }
}
```

#### Login User
`POST /api/auth/login/`
```json
{
  "email": "house@hospital.test",
  "password": "Password123!"
}
```
**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful.",
  "user": {
    "id": 1,
    "name": "Dr. House",
    "email": "house@hospital.test"
  },
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi..."
}
```

---

### 2. Patient Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/patients/` | Add a new patient | **Yes** |
| `GET` | `/api/patients/` | Retrieve all patients created by authenticated user | **Yes** |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient | **Yes** |
| `PUT` | `/api/patients/<id>/` | Update patient details | **Yes** (Owner/Admin) |
| `DELETE` | `/api/patients/<id>/` | Delete a patient record | **Yes** (Owner/Admin) |

#### Add Patient
`POST /api/patients/`
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "contact_number": "+1-555-0199",
  "email": "john.doe@example.com",
  "address": "123 Health Ave, Metropolis",
  "medical_history": "Hypertension diagnosed in 2020."
}
```

---

### 3. Doctor Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor | **Yes** |
| `GET` | `/api/doctors/` | Retrieve all doctors | **Yes** |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | **Yes** |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | **Yes** |
| `DELETE` | `/api/doctors/<id>/` | Delete a doctor record | **Yes** |

#### Add Doctor
`POST /api/doctors/`
```json
{
  "name": "Dr. Sarah Johnson",
  "specialization": "Cardiology",
  "contact_number": "+1-555-0101",
  "email": "sarah.johnson@hospital.test",
  "experience_years": 12,
  "hospital_affiliation": "Heart & Vascular Institute"
}
```

---

### 4. Patient-Doctor Mapping APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/mappings/` | Assign a doctor to a patient | **Yes** |
| `GET` | `/api/mappings/` | Retrieve all patient-doctor mappings | **Yes** |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient | **Yes** |
| `DELETE` | `/api/mappings/<id>/` | Remove a doctor from a patient (by mapping id) | **Yes** |
| `GET` | `/api/mappings/patient/<patient_id>/` | Explicit endpoint to get doctors for a patient | **Yes** |
| `DELETE` | `/api/mappings/remove/<patient_id>/<doctor_id>/` | Explicit remove by patient_id & doctor_id | **Yes** |

#### Assign Doctor to Patient
`POST /api/mappings/`
```json
{
  "patient_id": 1,
  "doctor_id": 2,
  "notes": "Assigned for cardiovascular assessment and follow-up."
}
```

#### Get Doctors Assigned to Patient
`GET /api/mappings/1/`
```json
{
  "success": true,
  "patient_id": 1,
  "patient_name": "Robert Miller",
  "total_assigned_doctors": 2,
  "assigned_doctors": [
    {
      "mapping_id": 1,
      "doctor_id": 1,
      "doctor_name": "Dr. Sarah Johnson",
      "specialization": "Cardiology",
      "contact_number": "+1-555-0101",
      "email": "sarah.johnson@hospital.test",
      "experience_years": 12,
      "hospital_affiliation": "Heart & Vascular Institute",
      "notes": "Cardiovascular review and monitoring",
      "assigned_at": "2026-10-16T12:00:00Z"
    }
  ]
}
```

---

## 🧪 Testing

### Run Automated Django Unit Tests
The test suite covers models, serializers, validation logic, permission checks, and API endpoints across all 4 apps:
```bash
python manage.py test
```
**Result**: 24 tests run and passed (`OK`).

### Run Live End-to-End Verification Script
Runs a comprehensive live flow against PostgreSQL:
```bash
python verify_api.py
```
**Result**: 17 sequential verification steps verified and passed.

---

## 📮 Postman Collection

An importable Postman collection is included in the root directory: [`postman_collection.json`](./postman_collection.json).

### How to use:
1. Open **Postman** (or Thunder Client / Insomnia).
2. Click **Import** and select `postman_collection.json`.
3. The collection is organized into 4 folders:
   - `1. Authentication`
   - `2. Patient Management`
   - `3. Doctor Management`
   - `4. Patient-Doctor Mappings`
4. Run `Register User` or `Login User` first: the collection automatically saves the returned JWT token to the `{{jwt_token}}` variable and includes it in all subsequent requests!

---

## 📖 Interactive Swagger & ReDoc Documentation

The backend includes auto-generated OpenAPI 3.0 documentation. You can test and inspect every API endpoint directly in your browser:

- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
  *(Allows you to authenticate via the **Authorize** button with `Bearer <token>` and execute requests live!)*
- **ReDoc Documentation**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI 3.0 Raw Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 🐳 Docker Deployment (1-Command Run)

To spin up both PostgreSQL and the Django backend without installing PostgreSQL or Python locally:

```bash
docker compose up --build
```

This will automatically:
1. Start the PostgreSQL 16 database container.
2. Build the Django container.
3. Apply all database migrations.
4. Seed the database with sample healthcare data.
5. Launch the Gunicorn production WSGI server on port `8000`.

---

## 🔒 Production Readiness Checklist

When deploying to production environments (AWS, Render, Heroku, DigitalOcean):
- Set `DEBUG=False` in `.env`.
- Provide a strong, randomly generated `SECRET_KEY`.
- Set specific allowed domains in `ALLOWED_HOSTS`.
- Use `gunicorn healthcare_project.wsgi:application` (included in `Dockerfile` and `requirements.txt`).
- Static assets are automatically compressed and cached using `WhiteNoise`.

