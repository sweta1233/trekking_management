# Trekking Management Application (TMA)

A simple full-stack trekking management system for adventure organizations, built with Flask, Vue.js, SQLite, Redis, and Celery. Three roles: **Admin**, **Trek Staff**, and **User (Trekker)**.

## Tech Stack

| Layer     | Technology                       |
|-----------|-----------------------------------|
| Backend   | Flask (REST API), SQLAlchemy ORM |
| Database  | SQLite, stored in `backend/instances/` |
| Frontend  | Vue.js 3, plain custom CSS (no UI framework) |
| Entry page| Jinja2 (backend `/` route only)  |
| Caching   | Redis (via Flask-Caching)        |
| Background jobs | Celery + Redis (worker + beat)  |
| Email (dev)| MailHog (local SMTP catcher, UI at :8025) |
| Auth      | JWT (Flask-JWT-Extended)         |

## Project Structure 

```
TMA/
├── backend/                  # only 5 python files
│   ├── app.py                # Flask app factory + auto DB init + auto admin seed
│   ├── config.py             # settings, incl. instances/ folder path
│   ├── models.py             # all 4 models: User, Trek, Booking, StaffProfile
│   ├── routes.py             # every API endpoint, in one file
│   ├── tasks.py              # Celery app + all 3 background jobs
│   ├── requirements.txt
│   ├── templates/index.html  # Jinja2 entry page only (not the app UI)
│   └── instances/            # auto-created: tma.db + exports/ (gitignored)
│
└── frontend/
    ├── package.json          # vue, vue-router, axios only
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js, App.vue
        ├── router/index.js   # role-based route guards
        ├── services/api.js, auth.js
        ├── assets/main.css   # one small custom design system (no Bootstrap)
        └── components/       # organized into subfolders; every screen is still its own .vue file
            ├── shared/
            │   ├── AppLayout.vue        (page shell: sidebar + topbar)
            │   ├── NavBar.vue           (sidebar links per role)
            │   ├── TrekCard.vue         (shared trek card, shows price)
            │   ├── ToastNotification.vue
            │   └── PaymentModal.vue     (payment gateway UI)
            ├── auth/
            │   ├── LoginPage.vue
            │   └── RegisterPage.vue
            ├── admin/
            │   ├── AdminDashboard.vue / ManageTreks.vue / CreateStaff.vue
            │   └── ManageStaff.vue / ManageUsers.vue / Bookings.vue / Search.vue / Reports.vue / Settings.vue
            ├── staff/
            │   └── StaffDashboard.vue / MyTreks.vue / ManageTrek.vue / Participants.vue / Profile.vue
            └── user/
                └── UserDashboard.vue / BrowseTreks.vue / MyBookings.vue / TrekkingHistory.vue / Profile.vue
```

Every `.vue` file is still fully separate — grouping them into `shared/`, `auth/`, `admin/`, `staff/`, `user/` just makes a 24-file flat folder easier to navigate. Imports were updated accordingly (role pages import shared components via `../shared/...`).

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server (optional locally — the app degrades gracefully without it, see note below)
- MailHog (optional locally — used to catch/view emails sent by the Celery jobs instead of a real SMTP provider)

## Running Everything — 6 Terminals

Each piece runs as its own process. Open 6 terminals (all but the first two just stay open running a long-lived process):

### Terminal 1 — Redis

```bash
redis-server
```

Needed for both Flask-Caching and as the Celery broker/result backend (`redis://localhost:6379/0` and `/1`).

### Terminal 2 — MailHog

MailHog is a standalone binary (not a pip package), so install it once, then just run it:

```bash
# macOS
brew install mailhog
mailhog

# Linux (download the release binary once)
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64 -O mailhog
chmod +x mailhog
./mailhog

# Or via Docker (any OS, no install needed)
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

- SMTP catcher listens on **localhost:1025** (this is what the Celery jobs send to).
- Web UI to view caught emails: **http://localhost:8025**

### Terminal 3 — Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env            # already defaults MAIL_SERVER to localhost:1025 (MailHog)

python app.py
```

Backend runs at **http://localhost:5000**. On first run it creates `backend/instances/tma.db` automatically and seeds the default Admin:
- Email: `admin@tma.com`
- Password: `Admin@123`

### Terminal 4 — Celery worker

```bash
cd backend
source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info
```

This is the process that actually **executes** background jobs (sends the emails, generates the CSV, etc.) when they're triggered — either by the beat schedule or on-demand (e.g. "Export History" in the UI).

### Terminal 5 — Celery beat

```bash
cd backend
source venv/bin/activate
celery -A tasks.celery_app beat --loglevel=info
```

This is the **cron scheduler** — it doesn't run the jobs itself, it just fires them into the queue on schedule, and the worker (Terminal 4) picks them up:
- `send_daily_reminders` — every day at 07:00 UTC
- `generate_monthly_report` — 1st of every month at 06:00 UTC

Worker and beat are two separate processes from the same `tasks.celery_app`, so both terminals must be running for scheduled jobs to actually fire and execute.

### Terminal 6 — Frontend (Vue)

```bash
cd frontend
npm install
npm run dev
```

Runs at **http://localhost:5173**, proxying `/api/*` to the backend on port 5000.

### Verifying it all works

1. Trigger something that sends an email (e.g. book a trek starting tomorrow, then let the daily reminder fire, or use "Export History" for the CSV-ready email).
2. Watch Terminal 4 (worker) log the task being received and completed.
3. Open **http://localhost:8025** — the email should be sitting in MailHog's inbox, fully rendered (HTML included), with nothing actually sent over the real internet.

If you don't want to wait for the cron schedule, you can manually trigger a task to test the pipeline end-to-end:

```bash
cd backend
source venv/bin/activate
python -c "from tasks import send_daily_reminders; send_daily_reminders.delay()"
```

Then check Terminal 4 for execution logs and MailHog's UI for the resulting email(s).

## Pricing & Payments

- Every trek has a **price per person**, set by Admin when creating/editing a trek.
- When a trekker books a trek, they pick a payment method (Card / UPI / Cash) — the booking captures the amount (`trek.price`) and simulates payment (`payment_status: Paid`).
- Cancelling a booking simulates a refund (`payment_status: Refunded`) and frees the slot.
- Admin Dashboard and Reports show **Total Revenue** (sum of paid, non-cancelled bookings).



## Deployment Guide (Render + Vercel)

### 1. Deploying Backend & PostgreSQL Database on Render

#### Option A: Automatic Deployment using Render Blueprint (`render.yaml`) - Recommended
1. Log in to [Render](https://render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository (`sweta1233/Trekking-management-app`).
4. Render will automatically detect `render.yaml` and configure:
   - A free **PostgreSQL Database** (`tma-postgres`)
   - A **Python Web Service** (`tma-backend`) with all necessary environment variables and database connections.
5. Click **Apply**.
6. Once deployed, copy your backend URL (e.g., `https://tma-backend-xxxx.onrender.com`).

#### Option B: Manual Setup on Render
1. **Create PostgreSQL Database**:
   - Go to Render Dashboard -> **New +** -> **PostgreSQL**.
   - Name: `tma-postgres`, Database: `tmadb`, User: `tma_user`.
   - Click **Create Database** and copy the **Internal Database URL** (or External Database URL).

2. **Create Web Service**:
   - Go to Render Dashboard -> **New +** -> **Web Service**.
   - Connect your GitHub repository.
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --workers 2 --threads 4 --timeout 120`
   - **Environment Variables**:
     - `DATABASE_URL`: *(Paste your Render PostgreSQL connection string)*
     - `SECRET_KEY`: *(Set a strong secret key)*
     - `JWT_SECRET_KEY`: *(Set a strong JWT secret key)*
     - `CACHE_TYPE`: `SimpleCache`
     - `ADMIN_EMAIL`: `admin@tma.com` (optional, default)
     - `ADMIN_PASSWORD`: `Admin@123` (optional, default)
   - Click **Deploy Web Service**.
   - Copy the deployed service URL (e.g. `https://tma-backend.onrender.com`).

---

### 2. Deploying Frontend on Vercel

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository (`sweta1233/Trekking-management-app`).
4. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click `Edit` and select `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. **Environment Variables**:
   - Name: `VITE_API_BASE_URL`
   - Value: `https://<YOUR-RENDER-BACKEND-URL>.onrender.com/api`
6. Click **Deploy**.

---

### 3. Verification & Default Admin Credentials

- Open your Vercel URL (e.g. `https://trekking-management-app.vercel.app`).
- Log in with the default admin account:
  - **Email**: `admin@tma.com`
  - **Password**: `Admin@123`
  - **Role**: `admin`
- As Admin, create staff accounts or manage treks, users, and bookings.

---

## Role Permissions 

**Admin** (pre-existing superuser, auto-seeded)
- Create, update, delete treks
- Add and manage trek staff (edit details, deactivate/blacklist/reactivate, delete)
- Assign staff to treks
- View and manage all users, staff, and treks
- Search users, staff, or treks
- Deactivate or blacklist users or staff (three states: active / inactive / blacklisted)
- View reports and trekking statistics

**Trek Staff** (no self-registration — only created by Admin)
- Log in only once created by Admin
- View treks assigned to them by Admin
- Manage only: **available slots** and **trek status (Open/Closed)** — cannot edit trek name, location, dates, price, or difficulty; those stay Admin-only. Enforced server-side, not just hidden in the UI.
- View the list of registered users for their treks (view-only — cannot cancel/remove a participant's booking)
- Update trek completion status ("Mark Completed")

**User (Trekker)**
- Register, log in, update their own profile
- View approved/open treks
- Search and filter treks by **difficulty, location, and duration**
- Book treks (with simulated payment)
- View booking status and trekking history

## Business Rules

- Booking blocked when slots are full, trek isn't `Open`, trek has already started, or the user already has an active booking for that trek.
- Slots decrement on booking, increment on cancellation.
- Blacklisted/inactive accounts of any role are blocked at login.
