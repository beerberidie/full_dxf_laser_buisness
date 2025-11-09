# Module N - File Ingest, Extract & Naming System
## Complete Technical Specification for Laser OS Integration

**Version:** 1.0  
**Date:** 2025-10-21  
**Status:** Design Phase  
**Author:** AI Assistant + User Collaboration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack](#technology-stack)
4. [Configuration Answers](#configuration-answers)
5. [Database Schema](#database-schema)
6. [Data Models](#data-models)
7. [File Processing Engines](#file-processing-engines)
8. [API Endpoints](#api-endpoints)
9. [File Naming Convention](#file-naming-convention)
10. [Integration with Laser OS](#integration-with-laser-os)
11. [Security & Validation](#security--validation)
12. [Deployment Guide](#deployment-guide)
13. [Testing Strategy](#testing-strategy)
14. [Future Enhancements](#future-enhancements)

---

## Executive Summary

**Module N** is a comprehensive file ingestion, metadata extraction, and intelligent file naming system designed to integrate seamlessly with **Laser OS** (Flask-based laser cutting business automation system).

### Purpose

- **Ingest** multiple file formats (Excel, PDF, DXF, LBRN2, images, text, Google Docs/Sheets)
- **Extract** structured metadata using format-specific parsers
- **Normalize** data into consistent schema
- **Apply** intelligent file naming conventions
- **Route** files to correct project directories
- **Notify** Laser OS of processed files via webhooks

### Key Features

✅ **Multi-format support:** Excel, PDF, DXF, LBRN2, images, text, Google Docs/Sheets  
✅ **Intelligent parsing:** Format-specific extractors with confidence scoring  
✅ **Auto-detection:** Automatic file type detection with manual override  
✅ **OCR capability:** Tesseract-based text extraction from images/scanned PDFs  
✅ **Table extraction:** Camelot/Tabula for structured data from PDFs  
✅ **DXF analysis:** Layer detection, entity counting, dimension extraction  
✅ **LightBurn support:** Metadata extraction from .lbrn2 files  
✅ **Collision handling:** Smart versioning for duplicate filenames  
✅ **Audit trail:** Complete tracking of all file operations  

---

## Architecture Overview

### Deployment Options

**Option A: Microservice Architecture (Recommended)**
```
┌─────────────────┐         ┌──────────────────┐
│   Laser OS      │         │    Module N      │
│   (Flask)       │◄───────►│   (FastAPI)      │
│   Port 8080     │  HTTP   │   Port 8081      │
└─────────────────┘         └──────────────────┘
        │                            │
        └────────────┬───────────────┘
                     ▼
              ┌─────────────┐
              │  SQLite DB  │
              │  (Shared)   │
              └─────────────┘
```

**Option B: Monolithic Architecture**
```
┌─────────────────────────────────┐
│        Laser OS (Flask)         │
│  ┌───────────────────────────┐  │
│  │  Module N Blueprint       │  │
│  │  /ingest routes           │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
                │
                ▼
         ┌─────────────┐
         │  SQLite DB  │
         └─────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Module N Core                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Validator  │  │   Detector   │  │   Router     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                    Parser Engines                        │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │Excel │ │ PDF  │ │ DXF  │ │LBRN2 │ │Image │ │ Text ││
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘│
├─────────────────────────────────────────────────────────┤
│                   Normalizer Layer                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Pydantic Models → Unified Metadata Schema       │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                  Storage & Naming                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ File Naming  │  │  Collision   │  │   Storage    │  │
│  │  Generator   │  │   Handler    │  │   Manager    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                Database & Events                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Ingest     │  │ Extractions  │  │  Webhooks    │  │
│  │   Records    │  │   Storage    │  │  /Callbacks  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Runtime & Framework

**Backend Service:**
- **FastAPI** 0.104.1 (async, high-performance REST API)
- **Python** 3.11+ (matches Laser OS)
- **Uvicorn** 0.24.0 (ASGI server)
- **Pydantic** 2.5.0 (data validation)

**Integration with Laser OS:**
- **Flask** 3.0.0 (existing Laser OS framework)
- **SQLAlchemy** 3.1.1 (ORM - shared with Laser OS)
- **Requests** 2.31.0 (HTTP client for microservice calls)

### File Processing Libraries

```python
# Excel Processing
pandas==2.1.3              # Data manipulation
openpyxl==3.1.2            # .xlsx files
xlrd==2.0.1                # .xls files (legacy)

# PDF Processing
PyMuPDF==1.23.8            # PDF parsing (fitz) - fast & reliable
camelot-py[cv]==0.11.0     # Table extraction from PDFs
tabula-py==2.9.0           # Alternative table extraction
pdf2image==1.16.3          # PDF to image conversion

# DXF Processing
ezdxf==1.1.0               # DXF parsing (already in Laser OS)

# Image Processing
Pillow==10.1.0             # Image manipulation (already in Laser OS)
pytesseract==0.3.10        # OCR wrapper
opencv-python==4.8.1       # Computer vision (optional)

# Document Processing
python-docx==1.1.0         # Word documents
python-pptx==0.6.23        # PowerPoint (optional)

# Utilities
python-magic==0.4.27       # MIME type detection
chardet==5.2.0             # Character encoding detection
python-dotenv==1.0.0       # Environment configuration
```

### Google APIs (Phase 2 - Future)

```python
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-api-python-client==2.110.0
```

### Database

- **SQLite** (development & small deployments)
- **PostgreSQL** (production - already planned for Laser OS)

---

## Configuration Answers

Based on analysis of the Laser OS codebase, here are the confirmed configuration decisions:

### 1. Runtime & Stack

**Answer:** Python FastAPI service + Flask frontend (NOT React)

- **Backend Service:** FastAPI (Module N)
- **Frontend:** Jinja2 templates (existing Laser OS)
- **Integration:** REST API calls or Flask Blueprint

### 2. Storage

**Answer:** A) Filesystem + D) Postgres metadata

**Current Structure:**
```
data/files/
├── clients/{ClientCode}/
│   └── projects/{ProjectCode}/
│       ├── inputs/          # Raw uploaded files
│       ├── dxf/             # Parsed DXF files
│       ├── lbrn2/           # LightBurn files
│       ├── drawings/        # Technical drawings
│       ├── documents/       # Quotes, invoices, POPs
│       ├── exports/         # Generated cut files
│       └── images/          # Photos, scans

data/documents/
├── quotes/
├── invoices/
├── pops/
└── delivery_notes/
```

**File Path Format:**
- Stored: `data/files/clients/{ClientCode}/projects/{ProjectCode}/inputs/{filename}`
- Database: Relative path `clients/{ClientCode}/projects/{ProjectCode}/inputs/{filename}`

### 3. Database

**Answer:** SQLite (current) → PostgreSQL (production)

- **Current:** SQLite at `data/laser_os.db`
- **ORM:** SQLAlchemy 3.1.1
- **Schema Version:** v10
- **Tables:** 32 existing tables
- **Production Plan:** PostgreSQL migration ready

### 4. File Naming Convention

**Answer:** Hybrid format with hard-enforced fields

**Format:**
```
{ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}
```

**Example:**
```
CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.dxf
```

**Hard-Enforced Fields:**
- ✅ `ClientCode` (format: `CL-\d{4}` or `CL\d{4}`)
- ✅ `ProjectCode` (format: `JB-yyyy-mm-CLxxxx-###`)
- ✅ `Material` (from MATERIAL_TYPES list)
- ✅ `Thickness` (numeric with 'mm' suffix)

**Optional Fields:**
- ⚠️ `Qty` (default: 1)
- ⚠️ `Version` (default: v1)

**Material Types (from Laser OS config):**
```python
MATERIAL_TYPES = [
    'Aluminum',
    'Brass',
    'Carbon Steel',
    'Copper',
    'Galvanized Steel',
    'Mild Steel',
    'Stainless Steel',
    'Vastrap',
    'Zinc',
    'Other'
]
```

**Material Code Mapping:**
```python
MATERIAL_MAP = {
    'Galv': 'Galvanized Steel',
    'SS': 'Stainless Steel',
    'MS': 'Mild Steel',
    'Al': 'Aluminum',
    'Brass': 'Brass',
    'Copper': 'Copper',
    'CS': 'Carbon Steel',
    'Vastrap': 'Vastrap',
    'Zinc': 'Zinc',
    'Other': 'Other'
}
```

### 5. Project Hierarchy

**Answer:** Use current Laser OS structure with enhancements

**Confirmed Structure:**
```
data/files/clients/{ClientCode}/projects/{ProjectCode}/
├── inputs/          # NEW: Raw uploaded files (Module N target)
├── dxf/             # Existing: DXF files
├── lbrn2/           # Existing: LightBurn files
├── drawings/        # NEW: Technical drawings (PDF, images)
├── documents/       # Existing: Quotes, invoices, POPs
├── exports/         # NEW: Generated cut files, reports
└── images/          # NEW: Photos, scans
```

**Helper Functions (already exist in Laser OS):**
```python
from app.utils.helpers import (
    get_client_directory,
    get_project_directory,
    get_dxf_directory
)
```

### 6. Google APIs

**Answer:** No (Phase 1), Yes (Phase 2 - future)

**Phase 1 (MVP):**
- ❌ No Google OAuth integration
- ✅ Direct file uploads only
- ✅ Focus on local file processing

**Phase 2 (Future):**
- ✅ Google OAuth credentials
- ✅ Read Google Sheets → JSON rows
- ✅ Export Google Docs to HTML/text
- ✅ Store credentials in `.env`

### 7. OCR

**Answer:** Tesseract + Camelot, English + Afrikaans

**OCR Stack:**
```python
pytesseract==0.3.10        # Tesseract wrapper
pdf2image==1.16.3          # PDF to image conversion
camelot-py[cv]==0.11.0     # Table extraction
Pillow==10.1.0             # Image processing
```

**Languages:**
- ✅ English (primary)
- ✅ Afrikaans (secondary - timezone is Africa/Johannesburg)

**Configuration:**
```python
TESSERACT_LANGUAGES = 'eng+afr'
TESSERACT_CONFIG = '--oem 3 --psm 6'  # LSTM OCR, assume uniform block of text
```

**Layout-Aware Parsing:**
- ✅ **Camelot** for digital PDFs with tables
- ✅ **Tabula** as fallback
- ✅ **LayoutParser** for complex layouts (optional Phase 2)

### 8. PDF Engine

**Answer:** PyMuPDF (fitz) - Approved ✅

**Why PyMuPDF:**
- Fast and reliable
- Extracts text, images, page dimensions
- Handles both digital and scanned PDFs
- Already familiar (Laser OS uses WeasyPrint for generation)

**Capabilities:**
```python
import fitz  # PyMuPDF

# Extract text
text = page.get_text()

# Extract images
images = page.get_images()

# Get page dimensions
bbox = page.bound()

# Extract tables (with Camelot)
import camelot
tables = camelot.read_pdf('file.pdf', pages='all')
```

### 9. DXF

**Answer:** ezdxf (already in use) - Approved ✅

**Current Usage:** Laser OS already uses `ezdxf==1.1.0`

**Fields to Extract:**

**Required:**
- ✅ Overall dimensions (bounding box)
- ✅ Layer names (e.g., "CUT", "ENGRAVE", "ETCH", "OUTLINE", "HOLES")
- ✅ Entities summary (lines, circles, arcs, polylines, splines)
- ✅ Text notes (all text entities)
- ✅ Block list (reusable components)
- ✅ Color (layer colors for operations)
- ✅ Linetype (solid, dashed, etc.)

**Optional (nice-to-have):**
- ⚠️ Material thickness (from title block or attributes)
- ⚠️ Part name (from title block or filename)
- ⚠️ Hole count and sizes (for drilling)
- ⚠️ Perimeter length (for cut time estimation)
- ⚠️ Area (for material usage)

**DXF Layer Standards (from Laser OS DXF library):**
```
- OUTLINE (color 7) — outer profiles
- HOLES (color 1) — cut-outs, holes
- CENTERLINES (color 3) — center marks/crosses
- NOTES (color 2) — minimal text titles
```

### 10. LightBurn .lbrn2

**Answer:** Metadata + thumbnail extraction; geometry via export ✅

**.lbrn2 Format:** XML-based (not fully proprietary)

**Phase 1: Metadata Extraction**
```python
import xml.etree.ElementTree as ET

# Parse XML
tree = ET.parse('file.lbrn2')
root = tree.getroot()

# Extract metadata
job_name = root.find('.//JobName').text
material = root.find('.//Material').text
layers = root.findall('.//Layer')

# Extract cut settings
for layer in layers:
    power = layer.get('Power')
    speed = layer.get('Speed')
    passes = layer.get('Passes')
```

**Phase 2: Geometry Extraction**
- **Option A:** Parse XML for basic shapes (lines, circles, paths)
- **Option B:** User exports to DXF/SVG from LightBurn (more reliable)

**Acceptable Workflow:**
1. Upload .lbrn2 file
2. Extract metadata (job name, material, cut settings)
3. Extract preview image (if embedded)
4. For geometry: User exports to DXF/SVG and re-uploads

---

## Database Schema

### New Tables for Module N

Module N requires 3 new tables to track file ingestion, extractions, and metadata.

#### Table 1: `file_ingests`

Tracks all uploaded files and their processing status.

```sql
CREATE TABLE IF NOT EXISTS file_ingests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Relationships
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,

    -- File metadata
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,  -- bytes
    file_type VARCHAR(50) NOT NULL,  -- 'excel', 'pdf', 'dxf', 'lbrn2', 'image', 'txt'
    mime_type VARCHAR(100),

    -- Processing status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    processing_mode VARCHAR(20),  -- 'AUTO', 'excel', 'pdf', 'dxf', etc.

    -- Extracted metadata (normalized)
    client_code VARCHAR(10),
    project_code VARCHAR(30),
    part_name VARCHAR(200),
    material VARCHAR(50),
    thickness_mm DECIMAL(10, 2),
    quantity INTEGER,
    version INTEGER DEFAULT 1,

    -- Processing details
    error_message TEXT,
    processing_started_at DATETIME,
    processing_completed_at DATETIME,

    -- Audit
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),

    -- Constraints
    CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Indexes
CREATE INDEX idx_file_ingests_project ON file_ingests(project_id);
CREATE INDEX idx_file_ingests_client ON file_ingests(client_id);
CREATE INDEX idx_file_ingests_status ON file_ingests(status);
CREATE INDEX idx_file_ingests_type ON file_ingests(file_type);
CREATE INDEX idx_file_ingests_created ON file_ingests(created_at);
```

#### Table 2: `file_extractions`

Stores extracted data in JSON format for flexibility.

```sql
CREATE TABLE IF NOT EXISTS file_extractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_ingest_id INTEGER NOT NULL REFERENCES file_ingests(id) ON DELETE CASCADE,

    -- Extraction metadata
    extraction_type VARCHAR(50) NOT NULL,
    extracted_data TEXT NOT NULL,  -- JSON format
    confidence_score DECIMAL(3, 2),  -- 0.00 to 1.00

    -- Audit
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_file_extractions_ingest ON file_extractions(file_ingest_id);
CREATE INDEX idx_file_extractions_type ON file_extractions(extraction_type);
```

#### Table 3: `file_metadata`

Normalized key-value pairs for quick queries.

```sql
CREATE TABLE IF NOT EXISTS file_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_ingest_id INTEGER NOT NULL REFERENCES file_ingests(id) ON DELETE CASCADE,

    -- Metadata key-value pairs
    key VARCHAR(100) NOT NULL,
    value TEXT,
    data_type VARCHAR(20),  -- 'string', 'number', 'date', 'boolean', 'json'

    -- Audit
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_file_metadata_ingest ON file_metadata(file_ingest_id);
CREATE INDEX idx_file_metadata_key ON file_metadata(key);
CREATE INDEX idx_file_metadata_key_value ON file_metadata(key, value(100));
```

### Migration Script

```sql
-- migrations/schema_module_n.sql

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Create tables (include all CREATE TABLE statements from above)

-- Insert schema version
INSERT INTO schema_version (version) VALUES ('module_n_v1');

-- Insert settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('module_n_enabled', 'true', 'Enable Module N file ingestion'),
    ('module_n_url', 'http://localhost:8081', 'Module N service URL'),
    ('module_n_auto_process', 'true', 'Automatically process uploaded files'),
    ('module_n_ocr_languages', 'eng+afr', 'Tesseract OCR languages'),
    ('module_n_confidence_threshold', '0.70', 'Minimum confidence score');
```

---

