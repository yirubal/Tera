# Tera
# 🚖 Tera Project

**Tera** is a backend system (built with Django + Django REST Framework) for managing Bajaj (three-wheel taxi) operations across terminals.  
It coordinates protectors, drivers, routes, shifts, and turns (waiting → departure → incoming), while tracking earnings and analytics.

---

---

## 🔑 Features

- **User & Protector Management**
  - Protectors have one-to-one User accounts.
  - Drivers have profiles with plate number & optional User account.
- **Shift System**
  - Only one active shift per protector.
  - Only one active shift per terminal.
  - Protectors can start, end, or transfer shifts.
- **Turns & Departures**
  - Drivers join the waiting list at a terminal (FIFO enforced).
  - Protectors can mark drivers as departed → departure record created.
  - Departures propagate as incoming to destination terminal.
- **Routes**
  - Unique route per terminal pair (A→B).
  - Validation: route must start at shift’s terminal.
- **Earnings**
  - Earnings logic tracked separately from departures.
- **Constraints & Safety**
  - DB constraints prevent duplicates.
  - Transactions + row locking ensure fairness in queues.

---

## ⚙️ Tech Stack

- **Backend:** Django 5, Django REST Framework
- **Database:** SQLite (dev)
- **Auth:** Django auth + DRF JWT (planned)
- **Others:** Pillow (images), DRF browsable API

---

## 📌 API Endpoints (Core)

### Protector
- `POST /api/protector/register` → Create protector profile  
- `GET /api/protector/me` → View own profile  
- `PATCH /api/protector/me` → Update phone/profile picture  

### Shift
- `POST /api/shift/start` → Start shift  
- `GET /api/shift/me` → Get active shift  
- `PATCH /api/shift/me` → Update route in current shift  
- `POST /api/shift/end` → End current shift  
- `POST /api/shift/transfer` → Transfer shift to another protector  

### Turns
- `POST /api/turns` → Add driver to waiting list (by plate number)  
- `PUT /api/turns/{id}` → Mark waiting driver as departed  
- `GET /api/turns/waiting` → Current waiting list  
- `GET /api/turns/departed` → Departures from my terminal  
- `GET /api/turns/incoming` → Incoming to my terminal  

---

## 🚀 Getting Started

### 1) Clone the repo
```bash
git clone https://github.com/<your-username>/Tera.git
cd Tera
