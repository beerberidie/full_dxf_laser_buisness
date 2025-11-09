
# Laser OS Multi-Tier Project — Summary & Migration Blueprint

## 1. Consolidation Phase
- Integrated all uploaded blueprints, manuals, specs, and strategy docs into a **Master Blueprint**.
- Covered: scheduling, quoting, DXF pipeline, materials/presets, comms automation, reporting, client strategy.

## 2. Clarification Phase
- Identified 43 critical decision points (DBs, stacks, auth, SLA, file naming, presets, quoting, reporting, AI).
- Chose to define **3 distinct versions** instead of one rigid answer.

## 3. Packaging Phase
- Built **3 repo skeletons + blueprints**, bundled into a ZIP:

### Tier 1 — Local / Quickest
- Flask + SQLite + CSV
- Local folders for DXF storage
- R12 DXF only; LightBurn manual
- Roles: admin/operator/manager
- Reports: daily/weekly/monthly via Flask jobs
- Simple PWA cut list

### Tier 2 — Halfway / Dockerized
- FastAPI + React + Tailwind + Docker Compose
- Postgres + MinIO
- JWT auth, role-based
- DXF R2010 + R12 fallback; optional .lbrn2
- Operator PWA with photos/notes
- Optional WhatsApp Cloud API for client updates

### Tier 3 — Full Industry Standard
- Next.js (frontend) + FastAPI (backend) + Redis/Workers
- Postgres + MinIO/S3 + Traefik
- JWT + SSO (Google/Microsoft)
- DXF R2010/R12, + .cyp + .lbrn2 exporters
- Multi-role (admin/manager/operator/sales/finance/viewer)
- Client portal, audit logs, advanced quoting
- CI/CD, backups, audit trails

## 4. Deliverable
- **laser_os_multi_tier_project.zip** with all 3 tiers, each containing:
  - `Blueprint.md`
  - `README.md`
  - Minimal code/API/UI skeletons
  - Seed CSVs for clients, jobs, projects, materials, logs, presets, email queue

---

# Migration Path

## A. Tier 1 → Tier 2 (local → dockerized modular)
- **Data**: SQLite/CSV → Postgres (same schema)
- **Files**: local folders → MinIO (S3-compatible)
- **API**: Flask routes → FastAPI endpoints
- **Auth**: Flask sessions → JWT
- **Reports**: Flask jobs → FastAPI background tasks
- **Acceptance tests**: row counts match, DXFs upload & retrieve, daily report sent

## B. Tier 2 → Tier 3 (dockerized → enterprise)
- **Workers**: add Redis + RQ/Celery for DXF generation, OCR, heavy reports
- **Auth**: add Google/Microsoft SSO + RBAC matrix
- **Files**: immutable DXF versioning, diff thumbnails
- **Exports**: .lbrn2 + .cyp generation
- **Quoting**: full cost model (runtime, pierce, bending, handling, delivery)
- **Invoicing**: Xero/Sage CSV export
- **Notifications**: operator + manager cadence; client portal
- **Ops**: Traefik reverse proxy, HTTPS, audit hash chain
- **Acceptance tests**: jobs queue & finish, client portal live, invoices match, backups restorable

---

# Cross-Tier Compatibility Rules
1. Stable IDs (`CL-xxxx`, `JB-yyyy-mm-client-###`)
2. Filenames: `[USERCODE]-[DESC]-[MAT]-[THK]-[QTY].dxf` (no spaces, underscores only)
3. Units: mm everywhere
4. Versioning: monotonic `v001...`; keep checksums
5. Timezones: UTC stored, SA displayed
6. Schema versions tracked (`schema_version` table)

---

# Migration Scripts (examples)

## SQLite → Postgres
```bash
sqlite3 laser_os.db ".headers on" ".mode csv" "SELECT * FROM clients;" > export/clients.csv
psql $PG_URL -f ddl.sql
psql $PG_URL -c "\copy clients FROM 'export/clients.csv' CSV HEADER;"
```

## Folder → MinIO
```bash
mc alias set local http://127.0.0.1:9000 minio minio123
mc mb local/laser
mc mirror /path/to/Laser_OS/03_DXFs local/laser/dxf
```

## .env Example
```
POSTGRES_URL=postgresql://snapdraft:changeme@db:5432/snapdraft
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
SMTP_HOST=smtp.gmail.com
SMTP_USER=...
SMTP_PASS=...
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change-me
```

---

# Suggested Timeline
- Day 1–2: DB + API + object storage
- Day 3: Reports & auth roles
- Day 4–5: WhatsApp + cutover
- Later: Tier 3 enterprise migration

