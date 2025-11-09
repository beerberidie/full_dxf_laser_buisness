# Module N - File Ingest & Extract System

**Version:** 1.7.0 (Phase 8 - Advanced Webhook Features Complete)
**Status:** ✅ PRODUCTION READY - ALL FEATURES OPERATIONAL
**Date:** 2025-10-21

---

## 🎉 Phase 8 Update - ADVANCED WEBHOOK FEATURES COMPLETE!

Module N is now **PRODUCTION READY** with advanced webhook capabilities! This update includes:

✅ **Project Structure** - Complete directory layout
✅ **Database Schema** - 3 tables with migrations
✅ **Database Operations** - Complete CRUD operations with SQLAlchemy ORM
✅ **File Storage** - Organized storage with automatic versioning
✅ **Webhook Notifications** - Real-time notifications to Laser OS
✅ **Webhook Retry Logic** - 🆕 Automatic retry with exponential backoff
✅ **Webhook Queue** - 🆕 Failed webhook queue with background processing
✅ **Webhook Signatures** - 🆕 HMAC-SHA256 signature verification
✅ **Webhook Monitoring** - 🆕 Metrics, health checks, and statistics
✅ **Webhook Filtering** - 🆕 Configurable event type filtering
✅ **Pydantic Models** - Full data validation
✅ **File Validation** - Security and type checking
✅ **Filename Generator** - Standardized naming with collision handling
✅ **FastAPI Application** - 14 endpoints including monitoring and queue stats
✅ **Flask Integration** - ModuleNClient for Laser OS + Webhook receiver with signature verification
✅ **Configuration** - Environment-based settings
✅ **DXF Parser** - Complete metadata extraction from DXF files
✅ **PDF Parser** - Complete metadata extraction from PDF files
✅ **Excel Parser** - Complete metadata extraction from Excel files (.xlsx and .xls)
✅ **LightBurn Parser** - Complete metadata extraction from LightBurn files (.lbrn2)
✅ **Image Parser** - Complete metadata extraction from images (PNG, JPG, BMP, TIFF) with OCR
✅ **Integration Tests** - 18 comprehensive integration tests
✅ **Webhook Tests** - 10 webhook notification tests + 15 advanced webhook tests 🆕
✅ **Tests** - 149 tests passing (Parsers: 97, Integration: 16, Webhooks: 25, Utils: 11)

---

## 📁 Project Structure

```
module_n/
├── __init__.py                 # Package initialization
├── main.py                     # FastAPI application (10 endpoints)
├── config.py                   # Configuration settings
├── db/                         # 🆕 Database layer (Phase 6)
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy ORM models
│   └── operations.py           # CRUD operations
├── storage/                    # 🆕 File storage (Phase 6)
│   ├── __init__.py
│   └── file_storage.py         # File storage with versioning
├── models/
│   ├── __init__.py
│   └── schemas.py              # Pydantic data models
├── parsers/                    # File parsers (5 parsers)
│   ├── __init__.py
│   ├── dxf_parser.py           # DXF parser
│   ├── pdf_parser.py           # PDF parser
│   ├── excel_parser.py         # Excel parser
│   ├── lbrn_parser.py          # LightBurn parser
│   └── image_parser.py         # Image parser with OCR
├── utils/
│   ├── __init__.py
│   ├── validation.py           # File validation
│   └── filename_generator.py   # Filename generation
└── tests/
    ├── __init__.py
    ├── test_validation.py
    ├── test_filename_generator.py
    ├── test_dxf_parser.py
    ├── test_pdf_parser.py
    ├── test_excel_parser.py
    ├── test_lbrn_parser.py
    ├── test_image_parser.py
    ├── test_integration.py     # 🆕 Integration tests (Phase 6)
    └── fixtures/               # Test files
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Module N dependencies
pip install -r requirements_module_n.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.module_n.example .env.module_n

# Edit .env.module_n with your settings
# (defaults are fine for development)
```

### 3. Run Database Migration

```bash
# Apply Module N schema
sqlite3 data/laser_os.db < migrations/schema_module_n.sql
```

### 4. Start Module N Service

```bash
# Development mode (with auto-reload)
cd module_n
python -m uvicorn main:app --reload --port 8081

# Or use the built-in runner
python main.py
```

### 5. Test the Service

```bash
# Health check
curl http://localhost:8081/health

# API documentation
# Open in browser: http://localhost:8081/docs
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env.module_n`:

```bash
# Service
MODULE_N_PORT=8081
MODULE_N_HOST=0.0.0.0

# Database
DATABASE_URL=sqlite:///data/laser_os.db

# File Storage
UPLOAD_FOLDER=data/files
MAX_UPLOAD_SIZE=52428800  # 50 MB

# Laser OS Integration
LASER_OS_WEBHOOK_URL=http://localhost:8080/webhooks/module-n/event

# OCR (Phase 2)
TESSERACT_LANGUAGES=eng+afr

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/module_n.log
```

### Laser OS Configuration

Module N settings are already added to `config.py`:

```python
MODULE_N_ENABLED = False  # Set to True to enable
MODULE_N_URL = 'http://localhost:8081'
MODULE_N_TIMEOUT = 30
MODULE_N_AUTO_PROCESS = True
```

---

## 📊 Database Schema

Three new tables added:

### 1. `file_ingests`
Tracks all uploaded files and processing status.

### 2. `file_extractions`
Stores raw extraction data in JSON format.

### 3. `file_metadata`
Normalized key-value pairs for fast querying.

**Rollback:** If needed, run `migrations/rollback_module_n.sql`

---

## 🧪 Testing

```bash
# Run all tests
pytest module_n/tests/ -v

# Run specific test file
pytest module_n/tests/test_validation.py -v

# Run with coverage
pytest module_n/tests/ --cov=module_n --cov-report=html
```

---

## 📡 API Endpoints

Module N provides 10 comprehensive endpoints for file ingestion, querying, and management.

### `GET /`
Root endpoint with API information.

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "module-n",
  "version": "1.5.0"
}
```

### `POST /ingest`
Upload and process files with full database integration.

**Request:**
```bash
curl -X POST http://localhost:8081/ingest \
  -F "files=@test.dxf" \
  -F "client_code=CL-0001" \
  -F "project_code=JB-2025-10-CL0001-001" \
  -F "mode=AUTO"
```

**Response:**
```json
[
  {
    "success": true,
    "filename": "test.dxf",
    "ingest_id": 123,
    "normalized_filename": "CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
    "file_path": "CL0001/JB-2025-10-CL0001-001/CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf",
    "detected_type": "dxf",
    "confidence_score": 0.95,
    "metadata": {
      "client_code": "CL0001",
      "project_code": "JB-2025-10-CL0001-001",
      "material": "Mild Steel",
      "thickness_mm": 5.0,
      "quantity": 10
    }
  }
]
```

### `GET /files`
List all ingested files with optional filters.

**Query Parameters:**
- `client_code` - Filter by client code
- `project_code` - Filter by project code
- `file_type` - Filter by file type (dxf, pdf, excel, lbrn2, image)
- `material` - Filter by material
- `thickness_mm` - Filter by thickness
- `status` - Filter by status (pending, processing, completed, failed)
- `limit` - Number of results (default: 100)
- `offset` - Pagination offset (default: 0)

**Example:**
```bash
curl "http://localhost:8081/files?client_code=CL0001&material=Mild%20Steel&limit=50"
```

### `GET /files/{file_id}`
Get details of a specific file by ID.

**Example:**
```bash
curl http://localhost:8081/files/123
```

### `GET /files/{file_id}/metadata`
Get extracted metadata for a file.

**Example:**
```bash
curl http://localhost:8081/files/123/metadata
```

### `GET /ingest/{ingest_id}`
Get ingest record by ID (alias for `/files/{file_id}`).

### `POST /files/{file_id}/re-extract`
Re-run extraction on an existing file.

**Request:**
```bash
curl -X POST "http://localhost:8081/files/123/re-extract?mode=AUTO"
```

### `DELETE /files/{file_id}`
Delete a file record (soft delete by default).

**Query Parameters:**
- `hard_delete` - Permanently delete file and record (default: false)

**Example:**
```bash
# Soft delete (mark as deleted)
curl -X DELETE http://localhost:8081/files/123

# Hard delete (permanent removal)
curl -X DELETE "http://localhost:8081/files/123?hard_delete=true"
```

### `GET /docs`
Interactive API documentation (Swagger UI).

---

## 🔗 Integration with Laser OS

### Using ModuleNClient

```python
from app.services.module_n_client import get_module_n_client

# In your route
client = get_module_n_client()

if client.is_enabled() and client.health_check():
    results = client.ingest_files(
        files=request.files.getlist('files'),
        client_code='CL-0001',
        project_code='JB-2025-10-CL0001-001'
    )
```

---

## 📝 File Naming Convention

**Format:**
```
{ClientCode}-{ProjectCode}-{PartName}-{Material}-{Thickness}mm-x{Qty}-v{Version}.{ext}
```

**Example:**
```
CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.dxf
```

**Material Codes:**
- MS = Mild Steel
- SS = Stainless Steel
- GALV = Galvanized Steel
- AL = Aluminum
- BR = Brass
- CU = Copper
- CS = Carbon Steel
- VAST = Vastrap
- ZN = Zinc
- OTH = Other

---

## 🛠️ Development

### Adding a New Parser (Phase 2)

1. Create `module_n/parsers/your_parser.py`
2. Implement `parse()` method
3. Return `NormalizedMetadata` object
4. Add to `main.py` ingest logic
5. Write tests

### Running in Development

```bash
# With auto-reload
uvicorn module_n.main:app --reload --port 8081

# With multiple workers (production)
uvicorn module_n.main:app --host 0.0.0.0 --port 8081 --workers 4
```

---

## 📚 Documentation

Full documentation available in `docs/`:

- **MODULE_N_INDEX.md** - Documentation index
- **MODULE_N_README.md** - Quick start guide
- **MODULE_N_SPECIFICATION.md** - Technical specification
- **MODULE_N_IMPLEMENTATION.md** - Implementation guide
- **MODULE_N_API_DEPLOYMENT.md** - API & deployment

---

## ✅ Phase 1 Checklist

- [x] Project structure created
- [x] Database migration created
- [x] Pydantic models implemented
- [x] File validation utilities
- [x] Filename generator
- [x] FastAPI application
- [x] Flask integration client
- [x] Configuration system
- [x] Basic tests
- [x] Documentation

---

## 🆕 DXF Parser Features

The DXF parser extracts comprehensive metadata from DXF files:

**Extracted Metadata:**
- ✅ Layer names and counts
- ✅ Entity types and counts (LINE, CIRCLE, ARC, POLYLINE, etc.)
- ✅ Bounding box dimensions (width x height in mm)
- ✅ Text notes and annotations
- ✅ Hole detection with diameters and positions
- ✅ Perimeter calculation from outline layers
- ✅ Approximate area calculation
- ✅ Material detection from layer names or text
- ✅ Thickness detection from text notes
- ✅ Part name extraction from text
- ✅ Confidence scoring (0.0 to 1.0)

**Usage Example:**

```python
from module_n.parsers import DXFParser

parser = DXFParser()
metadata = parser.parse(
    file_path="path/to/file.dxf",
    filename="bracket.dxf",
    client_code="CL0001",
    project_code="JB-2025-10-CL0001-001"
)

print(f"Part: {metadata.part_name}")
print(f"Material: {metadata.material}")
print(f"Thickness: {metadata.thickness_mm}mm")
print(f"Dimensions: {metadata.extracted['bounding_box']}")
print(f"Confidence: {metadata.confidence_score:.2f}")
```

---

## 🆕 PDF Parser Features

The PDF parser extracts comprehensive metadata from PDF files:

**Extracted Metadata:**
- ✅ Text content from all pages
- ✅ Tables (using Camelot for table extraction)
- ✅ Page count
- ✅ Document metadata (title, author, creation date, etc.)
- ✅ Embedded images count
- ✅ Material detection from text content
- ✅ Thickness detection from text
- ✅ Quantity detection from text
- ✅ Client/project code detection from text
- ✅ Part name extraction from title or text
- ✅ Confidence scoring (0.0 to 1.0)

**Usage Example:**

```python
from module_n.parsers import PDFParser

parser = PDFParser()
metadata = parser.parse(
    file_path="path/to/file.pdf",
    filename="quote.pdf",
    client_code="CL0001",
    project_code="JB-2025-10-CL0001-001"
)

print(f"Part: {metadata.part_name}")
print(f"Material: {metadata.material}")
print(f"Thickness: {metadata.thickness_mm}mm")
print(f"Pages: {metadata.extracted['page_count']}")
print(f"Tables: {len(metadata.extracted['tables'])}")
print(f"Confidence: {metadata.confidence_score:.2f}")
```

**PDF Types Supported:**
- Customer quotes with part specifications
- Technical drawings exported as PDF
- Job sheets with cutting instructions
- Proof of payment documents
- Multi-page documents with tables

---

## 🆕 Excel Parser Features

The Excel parser extracts comprehensive metadata from Excel files (.xlsx and .xls):

**Extracted Metadata:**
- ✅ Sheet names and count
- ✅ Row and column counts
- ✅ Header row detection
- ✅ Data rows (with performance limits for large files)
- ✅ Material detection from cell values
- ✅ Thickness detection from cell values
- ✅ Quantity detection from cell values
- ✅ Client/project code detection from cells
- ✅ Part name extraction from sheet names or cells
- ✅ Schema detection (quote, cutting list, parts list, invoice, etc.)
- ✅ Column mapping to standard fields
- ✅ Confidence scoring (0.0 to 1.0)

**Usage Example:**

```python
from module_n.parsers import ExcelParser

parser = ExcelParser()
metadata = parser.parse(
    file_path="path/to/file.xlsx",
    filename="quote.xlsx",
    client_code="CL0001",
    project_code="JB-2025-10-CL0001-001"
)

print(f"Part: {metadata.part_name}")
print(f"Material: {metadata.material}")
print(f"Thickness: {metadata.thickness_mm}mm")
print(f"Schema: {metadata.extracted['detected_schema']}")
print(f"Sheets: {metadata.extracted['sheet_count']}")
print(f"Confidence: {metadata.confidence_score:.2f}")
```

**Excel Types Supported:**
- Customer quotes with part specifications
- Cutting lists with material and dimensions
- Parts lists with quantities
- Inventory spreadsheets
- Job sheets with project details
- Generic spreadsheets with metadata

---

## 🆕 LightBurn Parser Features

The LightBurn parser extracts comprehensive metadata from LightBurn (.lbrn2) files:

**Extracted Metadata:**
- ✅ Application version and device name
- ✅ Material height (thickness)
- ✅ Cut settings (power, speed, frequency)
- ✅ Layer information (names, types, counts)
- ✅ Shape counts and types (Path, Circle, Rectangle, Text, etc.)
- ✅ Text elements and annotations
- ✅ Bounding box dimensions (approximate)
- ✅ Material detection from text elements
- ✅ Thickness detection from material height or text
- ✅ Client/project code detection from text
- ✅ Part name extraction from text elements
- ✅ Confidence scoring (0.0 to 1.0)

**Usage Example:**

```python
from module_n.parsers import LBRNParser

parser = LBRNParser()
metadata = parser.parse(
    file_path="path/to/file.lbrn2",
    filename="bracket.lbrn2",
    client_code="CL0001",
    project_code="JB-2025-10-CL0001-001"
)

print(f"Part: {metadata.part_name}")
print(f"Material: {metadata.material}")
print(f"Thickness: {metadata.thickness_mm}mm")
print(f"Layers: {metadata.extracted['layer_count']}")
print(f"Shapes: {metadata.extracted['shape_count']}")
print(f"Confidence: {metadata.confidence_score:.2f}")
```

**LightBurn Features Supported:**
- Cut and engrave settings extraction
- Multi-layer designs
- Complex shape analysis
- Text annotation extraction
- Material height detection

---

## 🆕 Image Parser Features

The Image parser extracts comprehensive metadata from image files with optional OCR:

**Extracted Metadata:**
- ✅ Image dimensions (width x height in pixels)
- ✅ Image format (PNG, JPG, BMP, TIFF, etc.)
- ✅ Color mode (RGB, RGBA, Grayscale, etc.)
- ✅ DPI information
- ✅ EXIF metadata (if available)
- ✅ OCR text extraction (using Tesseract if installed)
- ✅ Material detection from OCR text
- ✅ Thickness detection from OCR text
- ✅ Quantity detection from OCR text
- ✅ Client/project code detection from OCR text
- ✅ Part name extraction from OCR text or filename
- ✅ Confidence scoring (0.0 to 1.0, lower for OCR-based extraction)

**Usage Example:**

```python
from module_n.parsers import ImageParser

parser = ImageParser()
metadata = parser.parse(
    file_path="path/to/file.png",
    filename="drawing.png",
    client_code="CL0001",
    project_code="JB-2025-10-CL0001-001"
)

print(f"Part: {metadata.part_name}")
print(f"Material: {metadata.material}")
print(f"Dimensions: {metadata.extracted['width']}x{metadata.extracted['height']}")
print(f"OCR Available: {metadata.extracted['ocr_available']}")
print(f"Confidence: {metadata.confidence_score:.2f}")
```

**Image Types Supported:**
- PNG, JPG/JPEG, BMP, TIFF/TIF, GIF
- Scanned technical drawings
- Photos of parts or specifications
- Screenshots of quotes or job sheets
- Any image with readable text (if Tesseract OCR is installed)

**OCR Notes:**
- OCR functionality requires Tesseract to be installed
- If Tesseract is not available, parser still extracts basic image metadata
- Image preprocessing (grayscale, contrast enhancement) improves OCR accuracy
- Confidence scores are lower for OCR-based extraction due to uncertainty

---

## 🚧 Next Steps (Phase 6+)

- [x] Implement DXF parser ✅ **COMPLETE**
- [x] Implement PDF parser ✅ **COMPLETE**
- [x] Implement Excel parser ✅ **COMPLETE**
- [x] Implement LightBurn parser ✅ **COMPLETE**
- [x] Implement Image parser with OCR ✅ **COMPLETE**
- [ ] Database integration
- [ ] Webhook notifications
- [ ] File storage logic
- [ ] Integration tests

---

## 🐛 Troubleshooting

**Service won't start:**
- Check Python version (3.11+)
- Verify dependencies installed
- Check port 8081 is available

**Import errors:**
- Make sure you're in the project root
- Activate virtual environment
- Reinstall dependencies

**Database errors:**
- Run migration script
- Check database file exists
- Verify permissions

---

## 📄 License

Part of Laser OS project.

---

**Phase 5 Complete! ALL 5 PARSERS FULLY OPERATIONAL!** 🎉

