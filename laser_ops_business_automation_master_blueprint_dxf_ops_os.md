# Laser Ops & Business Automation – Master Blueprint (DXF + Ops OS)

> Living document that unifies all laser-cutting work (DXFs, jobs, settings), client acquisition, automations, and AI-assisted DXF generation. This is the **single source of truth**. We’ll paste/import snippets from your other chats here and link them into this structure.

---

## 0) North Star
- **Outcome:** Reliable, recurring production (weekly/monthly) with high-quantity parts; minimal admin; fast quoting; clean cut quality; tight feedback loops.
- **Constraints:** Golden Laser X3; cut capacity up to ~16 mm MS; CypCut; preference for air/N₂/O₂ presets; run-time windows (Mon–Thu 07:00–16:00; Fri 07:00–14:30).
- **Operating Principles:** Single source of truth → structured IDs → automate everything repeatable → measure → iterate.

---

## 1) Information Architecture (Single Source of Truth)
*(Client folders, jobs, DXF library, settings, quoting, production, QA, CRM, automations, reports – see detailed structure from v1 spec)*

---

## 2) Core Data Model (what we track)
*(Clients, jobs, parts, materials, settings, quotes, logs, QA – aligned with CSV schemas)*

---

## 3) End-to-End Pipeline (SOP)
*(Intake → DXF prep → Quoting → Nesting → Cutting → QA → Dispatch → Invoice)*

---

## 4) Automations
*(Email intake, Google Sheets watchdogs, n8n flows, LM Studio agents for DXF cleanup/quoting/client research)*

---

## 5) Daily Cadence & Dashboards
*(Morning/Noon/End routines; KPI dashboard with jobs, runtime vs estimate, utilization, margins, burr rates)*

---

## 6) DXF Library Rules
*(File/folder conventions, versioning, canonical vs WIP)*

---

## 7) Repeat-Business Targeting
*(Industries: Security, HVAC, Electrical, Automotive, Agriculture, etc. with SKU lists + outreach playbooks)*

---

## 8) Quoting & Pricing Framework
*(Material cost, runtime, setup, finishing, margin tiers; self-audit checks)*

---

## 9) Parameters & Presets
*(Matrix of material × gas × thickness, with changelog for burr/quality improvements)*

---

## 10) Maintenance & Machine Health
*(Daily/weekly tasks; log photos; correlate with cut quality KPIs)*

---

## 11) CRM & Outreach Playbooks
*(ICP, list build, first touch, offer, follow-up, retention)*

---

## 12) Dashboards & Reports (from Spec)
- Daily Ops, Weekly Client, Monthly Exec, Employee, Maintenance.
- Templates = Jinja2 → HTML → PDF with checksums/versions.
- Schedule = deterministic with APScheduler + catch-up.
- Email queue with attach/link logic; Outbox UI.

---

## 13) Command Glossary
*(Quick actions: “what is due today”, “add job”, “quote JB…”, “log cut”, etc.)

---

## 14) Technical Spec (from Uploaded Master Spec)
*(Stack, lifecycles, file structure, scheduler, web app pages, backups/security, repo structure)*

---

## 15) DXF Chat-to-Spec Integration (from Upload 2)
*(Critical review, recommendations, canonical JSON, AI chat orchestration, FastAPI endpoints, Dockerization, future extensions)*

---

## 16) DXF AI System — Phased Implementation (from Upload 3)
### 16.1 Quickstart & Requirements
- Local-first system with `ezdxf`, `Flask`, `reportlab`, `opencv-python-headless`, `pytest`.
- Run: create venv, install requirements, run CLI tools (`make_part.py`), execute tests.

### 16.2 Configs
- **kerf_table.json**: kerf per thickness ranges.
- **layers.json**: CUT/BEND/ENGRAVE layers with colors.
- **materials.json**: supported materials + thicknesses.
- **plates.json**: sheet sizes (1220×2440, 1500×3000, 2000×4000).
- **rules.json**: min hole diameter, fillet, bridge, approval requirements, bbox limit.

### 16.3 Schema & LLM
- `ai/spec.schema.json`: contract for part specs (part_name, material, thickness, dims, holes, slots, bends, engrave, notes).
- `ai/llm.py`: wrapper for local LLM (LM Studio or API endpoint).
- Prompt enforcement: hole diameter rules, mm units.

### 16.4 CLI Tools
- `check_config.py`: validate configs.
- `parse_spec.py`: deterministic parser for briefs, enforce rules.
- `build_dxf.py`: DXF builder with racetrack slots, rectangles, circles, bends.
- `validate_dxf.py`: strict DXF validator (units, layers, open polylines, duplicates, hole diameters, bbox).
- `make_pdf.py`: PDF approval drawings with scaled geometry + annotations.
- `make_part.py`: full pipeline (brief → spec → DXF → validation → PDF).

### 16.5 API & UI
- `app/server.py`: Flask API for job creation, DXF/PDF/spec downloads, auto-cleanup.
- `ui/index.html`: simple SPA (“SnapDraft Lite”) for pasting briefs → generate DXF/PDF.

### 16.6 Tests
- `tests/test_pipeline.py`: end-to-end tests ensure DXF + PDF are generated.

### 16.7 SOPs
- Units = mm only; PDF approval required before cutting; all parts must PASS validation.

### 16.8 End Result
- Entire pipeline (configs, schema, CLI, API, UI, tests, SOPs) is self-contained in one .md file.
- Copy-paste into folders → run from Day 1.

---

## 17) SnapDraft Production DXF System (from Upload 4)
### 17.1 Executive Overview & Roadmap
- Two-part platform: **Client Intake Mini‑Site** + **Internal SnapDraft App** that converts images/text to production‑ready DXF (R2010) with layer coding and kerf adjustments.
- Phases 0–8: repo scaffolding → data models → machine/material libraries → client intake → AI outline→DXF → review UI → versioning → nesting → optional 3D viewer.
- Tech stack: FastAPI + Python (Pydantic, ezdxf, OpenCV, Tesseract, SQLModel/Postgres) with React + Vite frontend; ops via Docker‑Compose, Traefik, Redis, MinIO.
- Repo layout includes services for `outline.py`, `dxf_gen.py`, and `nesting.py` plus presets for `machines.json` and `materials.json`.
- Key endpoints: `/projects/{pid}/draft` (outline→DXF), `/projects/{pid}/preview/{dxf_id}` (SVG preview).
- Outline→DXF: Canny edges → contours → LWPolyline export; annotator for notes.
- Docker‑Compose snippet for API, DB, MinIO.

### 17.2 Integration with Our OS
- Map **Client Intake Mini‑Site** → our Intake in §3.1, saving files to canonical folders and creating `JB-…` IDs.
- Use **Preset libraries** to seed §9 Parameters & Presets (machines/materials/kerf).
- Expose `/preview` for inline SVG thumbnails in the Jobs Kanban (§12 Web App pages).
- Adopt versioning & history under `/03_DXFs/...` with diff notes.

---

## 18) Laser Cutting Operations — Master Reference (from Upload 5)
### 18.1 Machine Ops & Settings
- Lens/nozzle selection by job; gas: O₂/N₂; soft‑cut modes for thin stock; strict **no mixed thickness** per job; fail‑resume supported; weekly/monthly maintenance schedule.

### 18.2 File Prep & Drawing Logic
- Inputs accepted: Image/SVG/DXF/Text/Audio; **mm units only**; bend notching and layering by best judgment unless specified; assistant interprets messy inputs and chooses next step; naming keeps client’s original codes.

### 18.3 Approvals, Storage, Roles
- **Kieran** final approval default; payments tracking to be added; current storage is folder‑based → we align to §1 IA; assistant proposes enhancements.

### 18.4 Scheduling & Notifications
- Work hours ~07:00–16:00/17:00; machine provides estimated cut time; notifications: hourly + 30‑min before job; non‑response keeps job at top; rejections require reason log.

### 18.5 Inventory & Nesting Rules
- Scrap allowed for testing; manage sheet lists; **Max 20 units per part per nest**; avoid mixed material/ thickness in nests.

### 18.6 AI/AR Capabilities
- Convert bad inputs to clean DXF; auto‑extract metadata; group lists by client/project/date; prompt for missing info during drawing generation.

**Integration Notes**
- Encode max‑20‑units rule into Nesting Policy; include Kieran approval as a required status gate before `approved` in §3 and §14 validators.
- Add notification cadence to Scheduler (§12) and Outbox logic; extend `tasks.csv` with `rejection_reason`.

---

## 19) Client Acquisition Strategy (from Upload 6)
- **Industries targeted**: Automotive, Construction, Agriculture, Mining/Heavy Industry. Criteria: recurring production, standardized repeatable parts【67†files_uploaded_in_conversation】.
- **Outreach pipeline**: directories, maps, associations → cold email/LinkedIn/phone to factory managers & supervisors. Offer sample cuts (free/discounted). Position: outsourced laser department【67†files_uploaded_in_conversation】.
- **Positioning/offer**: Reliability, flexibility, cost savings, partnership model. Hooks: free DXF cleanup, bundled material sourcing, Kanban supply【67†files_uploaded_in_conversation】.
- **Marketing**: LinkedIn ads, trade shows, Google Ads, word of mouth via welding shops【67†files_uploaded_in_conversation】.
- **Retention**: standard catalog, volume discounts, standing orders. Use CRM tracker【67†files_uploaded_in_conversation】.

---

## 20) Operations Manual – FOT Workflow (from Upload 7)
- **Cut sheet workflow**: Photograph cut sheet → record notes (nesting stage, material batch) → exchange bed & handle material/offcuts → alignment & framing → 5H inspection (Head, Height, Hold-downs, Hardware, Hazards) → restart cycle【68†files_uploaded_in_conversation】.
- **Reminders**: always photo+log every sheet; always 5H inspection; handle offcuts consistently; stay organized across notes/photos/material【68†files_uploaded_in_conversation】.

---

## 21) Scheduler MVP (from Upload 8)
- **Goal**: Local-first web app (Flask, SQLite, HTML/CSS/JS) that mirrors folder structure, enforces naming, routes uploads, tracks approvals/payments, prioritizes jobs, schedules cutting, and produces reports【69†files_uploaded_in_conversation】.
- **Principles**: file system = source of truth; strict naming; gatekeeping (quote+drawing+payment → eligible); SLA T+3 days default; operator-first UX【69†files_uploaded_in_conversation】.
- **Folder/naming conventions**: `[USERCODE]-[part]-[material]-[thickness]-[qty].dxf`; regex provided【69†files_uploaded_in_conversation】.
- **DB schema**: clients, profiles, projects, documents, design_files, approvals, quotes, invoices, tasks, schedule_queue, laser_runs, materials, inventory_events, notifications, users, activity_log【69†files_uploaded_in_conversation】.
- **Status machine**: CREATED → QUOTE_DRAFTED → QUOTE_SENT → AWAITING_APPROVALS → APPROVED → INVOICED → PAID → QUEUED_FOR_CUT → CUTTING → QC → READY_FOR_COLLECTION → COMPLETED【69†files_uploaded_in_conversation】.
- **Scheduling/SLAs**: default 3 days; stale project alerts; priority scoring; drag/drop queue; blockers = tasks【69†files_uploaded_in_conversation】.
- **Reports**: Daily, Weekly, Monthly, Laser Ops. Operator+manager structure with blockers, inventory to order, last 24h laser ops【69†files_uploaded_in_conversation】.
- **UX**: Sidebar nav (Profiles, Client, Employee Progress, Reports), project detail with status/approvals/payments/files, queue views, daily reports【69†files_uploaded_in_conversation】.
- **Automation**: file watcher, morning scripts, notifier, inventory reconciler【69†files_uploaded_in_conversation】.
- **Phases 0–5**: repo scaffold → profiles/projects/parser → status machine → scheduling/queue → reports → inventory+notifications【69†files_uploaded_in_conversation】.
- **API sketch** & CLI utilities provided【69†files_uploaded_in_conversation】.

---

## 22) Business Development & Client Acquisition Plan (from Upload 9)
- **Criteria**: standardized parts, frequent replacement, ongoing demand, outsourcing cheaper/faster【70†files_uploaded_in_conversation】.
- **Industries & parts**: 
  - Mining: screen plates, liners, chute plates, conveyor brackets, guards【70†files_uploaded_in_conversation】.
  - Agriculture: plough blades, seed drill plates, guards, trays【70†files_uploaded_in_conversation】.
  - Automotive: brackets, mudguard supports, trailer stiffeners【70†files_uploaded_in_conversation】.
  - Construction: connection plates, stair treads, gussets【70†files_uploaded_in_conversation】.
  - Retail: shelving brackets, display racks, counter supports【70†files_uploaded_in_conversation】.
  - Renewables: solar brackets, trays, inverter plates【70†files_uploaded_in_conversation】.
- **Shortlists**: Specific companies + contacts per industry (e.g., Multotec, AFGRI, Paramount Trailers, Rubicon, etc.)【70†files_uploaded_in_conversation】.
- **Outreach**: personalized emails, LinkedIn, phone; trial/sample cuts; recurring delivery schedules【70†files_uploaded_in_conversation】.
- **Execution**: pick 2–3 industries; shortlist 10 companies each; send 20–30 intros; follow up; track in CRM【70†files_uploaded_in_conversation】.
- **Next steps**: marketing flyer, CRM tracker, focus initial outreach on mining, transport, retail【70†files_uploaded_in_conversation】.

---

## 23) Next Actions (staging)
- [ ] Merge all additional chat exports.
- [ ] Consolidate acquisition hooks with Scheduler DB (clients/leads table).
- [ ] Integrate FOT workflow into QA + machine ops logging.
- [ ] Wire MVP Scheduler schema into master repo skeleton.
- [ ] Add company shortlists & contacts into CRM module.
- [ ] Generate flyer/pack + catalog templates.
- [ ] On **PROCEED**, build project.zip with repo, CSVs, DXFs, CRM, manuals.

---

### Paste Area
(Use this area to dump content from your other chats. I’ll convert to structured entries above.)
(Use this area to dump content from your other chats. I’ll convert to structured entries above.)
(Use this area to dump content from your other chats. I’ll convert to structured entries above.)

