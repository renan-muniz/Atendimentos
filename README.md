# Atendimento Manager – Backend-Focused Web Application

A lightweight backend-oriented web application built to help a psychology practice register daily sessions, track payment status, and generate monthly summaries of unpaid sessions.

This project was developed with a **backend-first and data-centric approach**, focusing on relational data modeling, SQL queries, backend business logic, and real-world cloud deployment. The frontend is intentionally minimal and functional.

---

![imagem](images/image_1.png)
![imagem](images/image_2.png)
![imagem](images/image_3.png)


---
## Project Motivation

The application was created to replace a manual workflow based on paper notes and monthly calculations.

The main goals were:

- Allow daily session registration  
- Keep a reliable historical record of payments  
- Automatically identify unpaid sessions from the previous month  
- Generate structured billing messages per client  
- Support manual reconciliation after payment  

This is a **real production system** designed to be used daily.

---

## Architecture Overview

```text
Client (Browser)
        ↓
Flask Web Application (server-rendered templates)
        ↓
Business Logic and SQL Queries (Python)
        ↓
PostgreSQL Database (Neon)
```


The system follows a **single-admin architecture**, suitable for individual professionals and small practices.

---

## Database Design

The database uses **PostgreSQL** and consists of a single main table.

### ENUM: `status_atendimento`

- `pago`
- `pendente`

### Table: `atendimentos`

| Column           | Description                                  |
|------------------|----------------------------------------------|
| `id`             | Primary key                                  |
| `nome_cliente`   | Client name                                  |
| `data_sessao`    | Session date                                 |
| `valor`          | Session value                                |
| `status`         | Payment status (`pago` / `pendente`)         |
| `data_pagamento` | Payment date (nullable)                      |
| `criado_em`      | Record creation timestamp                    |

Indexes are applied on:

- `data_sessao`
- `nome_cliente`
- `status`

---

## Backend Logic and Data Flow

### Daily Workflow

- Each attended session is inserted as a new row.
- Default payment status is set to `pendente`.

### Monthly Reconciliation

At the beginning of each month, the system:

- Queries sessions from the previous month  
- Filters only pending payments  
- Groups sessions by client name  
- Computes total amount due per client  
- Generates a ready-to-send billing message  

### Payment Confirmation

After payment is received, selected sessions are updated in batch:

- `status` is set to `pago`
- `data_pagamento` is recorded

---

## Authentication Model

The application uses a **single-admin authentication model**.

Credentials are stored securely via environment variables:

- `ADMIN_USER`
- `ADMIN_PASS_HASH`

Passwords are **never stored in plain text**.

---

## Tech Stack

### Backend
- Python
- Flask
- psycopg2
- SQL (PostgreSQL)

### Frontend
- HTML
- Jinja templates

### Infrastructure
- Neon (managed PostgreSQL)
- Render (web hosting)
- Gunicorn (WSGI server)

---

## Deployment

The application is deployed as a **Render Web Service** using Gunicorn.

## Why This Project Matters

This project demonstrates:

- Real-world backend problem solving  
- Relational data modeling  
- SQL-first time-based querying  
- Payment state management  
- Secure configuration handling  
- Cloud deployment under free-tier constraints  

It was built to be used daily, **not as a demo or toy project**.

---

## Future Improvements

- Client normalization with a separate clients table  
- WhatsApp integration for billing messages  
- CSV export for accounting  
- Automated backups  
- API-first refactor  
- Basic analytics dashboards  

---

## Author

**Renan Muniz**  
Data Scientist | Data Engineer  
Madrid, Spain

---

## Disclaimer

The user interface is intentionally simple.  
The main focus of this project is backend logic, data handling, database design, and system deployment.




