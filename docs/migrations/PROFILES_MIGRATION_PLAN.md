# Profiles Import Migration - Implementation Plan

## 📋 Executive Summary

This document outlines the comprehensive implementation plan for migrating client projects and files from the existing file structure (`profiles_import`) into the Laser OS application database.

### Migration Scope
- **Source**: File system structure at `profiles_import/{client_code}/1.Projects/`
- **Target**: Laser OS database (clients, projects, design_files, project_documents)
- **Data**: Project folders, DXF files, LBRN2 files, and supporting documents

---

## 🎯 Objectives

1. **Preserve Data Integrity**: Ensure all project metadata is accurately extracted and stored
2. **Maintain Relationships**: Link projects to existing clients via client_code
3. **Organize Files**: Categorize and store files in appropriate database tables
4. **Enable Traceability**: Track migration progress and provide detailed reporting
5. **Ensure Safety**: Implement validation, error handling, and rollback capabilities

---

## 📁 Source Data Structure

### File Pattern Analysis

**Folder Structure:**
```
\profiles_import\{client_code}\1.Projects\{project_folder}\{files}
```

**Project Folder Pattern:**
```
{project_number}-{project_description}-{date_created}
```
Example: `0001-Gas Cover box 1 to 1 ratio-10.15.2025`

**File Naming Pattern:**
```
{project_number}-{part_description}-{material}-{thickness}-{quantity}.{extension}
```
Example: `0001-Full Gas Box Version1-Galv-1mm-x1.dxf`

### Extracted Metadata

From **Project Folder Name**:
- `project_number`: e.g., "0001"
- `project_description`: e.g., "Gas Cover box 1 to 1 ratio"
- `date_created`: e.g., "10.15.2025" → parsed to date

From **File Name**:
- `project_number`: e.g., "0001" (validation check)
- `part_description`: e.g., "Full Gas Box Version1"
- `material`: e.g., "Galv" → mapped to "Galvanized Steel"
- `thickness`: e.g., "1mm" → parsed to 1.0
- `quantity`: e.g., "x1" → parsed to 1

---

## 🗄️ Target Database Schema

### Existing Tables

#### **clients** (Already Populated)
- `id`, `client_code`, `name`, `contact_person`, `email`, `phone`, `address`, `notes`
- **Migration**: Match by `client_code` (e.g., CL-0001)

#### **projects** (Target for Import)
Key fields to populate:
- `project_code`: Auto-generated (JB-yyyy-mm-CLxxxx-###)
- `client_id`: Foreign key from clients table
- `name`: From project folder description
- `description`: Combination of project and part descriptions
- `status`: Default to 'Request' (Phase 9 workflow)
- `material_type`: Parsed from filename
- `material_thickness`: Parsed from filename (in mm)
- `parts_quantity`: Parsed from filename
- `created_at`: Parsed from folder date

#### **design_files** (DXF/LBRN2 Files)
- `project_id`: Foreign key to projects
- `original_filename`: Original file name
- `stored_filename`: Generated unique name
- `file_path`: Relative path in storage
- `file_size`: File size in bytes
- `file_type`: 'dxf' or 'lbrn2'
- `uploaded_by`: 'profiles_migration'

#### **project_documents** (Other Files)
- `project_id`: Foreign key to projects
- `document_type`: 'Quote', 'Invoice', 'Proof of Payment', 'Delivery Note', 'Other'
- `original_filename`: Original file name
- `stored_filename`: Generated unique name
- `file_path`: Full path in storage
- `file_size`: File size in bytes
- `uploaded_by`: 'profiles_migration'

---

## 🏗️ Architecture Design

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Profiles Migration System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  File Scanner    │─────▶│  Filename Parser │            │
│  │  - Traverse dirs │      │  - Extract meta  │            │
│  │  - Find projects │      │  - Validate data │            │
│  └──────────────────┘      └──────────────────┘            │
│           │                          │                       │
│           ▼                          ▼                       │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Client Matcher  │      │  Project Builder │            │
│  │  - Lookup codes  │      │  - Create records│            │
│  │  - Validate      │      │  - Generate codes│            │
│  └──────────────────┘      └──────────────────┘            │
│           │                          │                       │
│           └──────────┬───────────────┘                       │
│                      ▼                                       │
│           ┌──────────────────┐                              │
│           │  File Uploader   │                              │
│           │  - Copy files    │                              │
│           │  - Create records│                              │
│           └──────────────────┘                              │
│                      │                                       │
│                      ▼                                       │
│           ┌──────────────────┐                              │
│           │  Transaction Mgr │                              │
│           │  - Commit/Rollback│                             │
│           │  - Error handling│                              │
│           └──────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Scan**: Traverse `profiles_import` directory structure
2. **Parse**: Extract metadata from folder/file names
3. **Validate**: Check client codes, file formats, data completeness
4. **Match**: Link to existing clients in database
5. **Import**: Create project records with metadata
6. **Upload**: Copy files to appropriate storage locations
7. **Record**: Create database entries for all files
8. **Verify**: Validate successful migration
9. **Report**: Generate detailed migration summary

---

## 🔧 Implementation Phases

### Phase 1: Analysis & Planning ✓

**Deliverables:**
- [x] File structure pattern analysis
- [x] Database schema mapping
- [x] Architecture design
- [x] Implementation plan document

### Phase 2: Core Parsing Module

**File**: `app/services/profiles_parser.py`

**Components:**
1. **FolderNameParser**
   - Parse project folder names
   - Extract: project_number, description, date
   - Handle variations and edge cases

2. **FileNameParser**
   - Parse file names
   - Extract: part_description, material, thickness, quantity
   - Validate against project number

3. **MaterialMapper**
   - Map short codes to full material names
   - Examples: "Galv" → "Galvanized Steel", "SS" → "Stainless Steel"

4. **DateParser**
   - Parse various date formats
   - Handle: MM.DD.YYYY, DD-MM-YYYY, YYYY-MM-DD

**Key Functions:**
```python
def parse_project_folder(folder_name: str) -> Dict[str, Any]
def parse_file_name(file_name: str) -> Dict[str, Any]
def map_material_code(code: str) -> str
def parse_project_date(date_str: str) -> Optional[date]
```

### Phase 3: File Scanner & Validator

**File**: `app/services/profiles_scanner.py`

**Components:**
1. **DirectoryScanner**
   - Traverse profiles_import structure
   - Identify client folders
   - Find project folders
   - Catalog all files

2. **ClientValidator**
   - Check client_code exists in database
   - Report missing clients
   - Suggest corrections

3. **FileClassifier**
   - Categorize files by extension
   - DXF/LBRN2 → design_files
   - PDF → documents (type detection)
   - Images → documents (type: Other)

**Key Functions:**
```python
def scan_profiles_directory(base_path: Path) -> List[ProjectData]
def validate_client_exists(client_code: str) -> bool
def classify_file(file_path: Path) -> Tuple[str, str]
```

### Phase 4: Project Importer

**File**: `app/services/profiles_importer.py`

**Components:**
1. **ProjectBuilder**
   - Create Project model instances
   - Generate project codes
   - Set default values
   - Handle metadata mapping

2. **DuplicateDetector**
   - Check for existing projects
   - Match by client + project number
   - Provide skip/update options

3. **MetadataMapper**
   - Map parsed data to Project fields
   - Handle missing/optional fields
   - Apply business rules

**Key Functions:**
```python
def create_project_from_metadata(client_id: int, metadata: Dict) -> Project
def check_duplicate_project(client_id: int, project_num: str) -> Optional[Project]
def map_metadata_to_project(metadata: Dict) -> Dict
```

### Phase 5: File Upload Handler

**File**: `app/services/profiles_file_handler.py`

**Components:**
1. **DesignFileUploader**
   - Copy DXF/LBRN2 files
   - Generate stored filenames
   - Create DesignFile records
   - Store in: `data/files/projects/{project_id}/`

2. **DocumentUploader**
   - Copy document files
   - Detect document type
   - Create ProjectDocument records
   - Store in: `data/documents/{type}/`

3. **FileValidator**
   - Check file exists
   - Validate file size
   - Check file integrity

**Key Functions:**
```python
def upload_design_file(project: Project, source_path: Path) -> DesignFile
def upload_document(project: Project, source_path: Path, doc_type: str) -> ProjectDocument
def detect_document_type(file_path: Path) -> str
```

### Phase 6: Migration Script

**File**: `migrate_profiles.py`

**Components:**
1. **MigrationOrchestrator**
   - Coordinate all phases
   - Manage transactions
   - Track progress
   - Handle errors

2. **ProgressTracker**
   - Count total items
   - Report progress percentage
   - Estimate time remaining
   - Log milestones

3. **ErrorHandler**
   - Catch and log errors
   - Continue on non-critical errors
   - Rollback on critical failures
   - Generate error report

**Command-Line Interface:**
```bash
# Dry run (validation only)
python migrate_profiles.py --source ./profiles_import --validate-only

# Import specific client
python migrate_profiles.py --source ./profiles_import --client CL-0001

# Import all with progress
python migrate_profiles.py --source ./profiles_import --all --verbose

# Resume from checkpoint
python migrate_profiles.py --source ./profiles_import --resume checkpoint.json
```

### Phase 7: Validation & Testing

**Files**: 
- `tests/test_profiles_migration.py`
- `validate_profiles_migration.py`

**Test Coverage:**
1. **Unit Tests**
   - Parser functions
   - Material mapping
   - Date parsing
   - File classification

2. **Integration Tests**
   - End-to-end migration
   - Database transactions
   - File operations
   - Error scenarios

3. **Validation Tools**
   - Compare source vs database
   - Check file counts
   - Verify relationships
   - Data integrity checks

### Phase 8: Documentation

**Files**:
- `PROFILES_MIGRATION_GUIDE.md` - User guide
- `PROFILES_MIGRATION_TROUBLESHOOTING.md` - Common issues
- `PROFILES_MIGRATION_REPORT_TEMPLATE.md` - Report format

---

## 🔍 Detailed Technical Specifications

### Filename Parsing Regex Patterns

**Project Folder:**
```regex
^(\d{4})-(.+?)-(\d{1,2}\.\d{1,2}\.\d{4})$
Groups: (project_number, description, date)
```

**File Name:**
```regex
^(\d{4})-(.+?)-([A-Za-z]+)-(\d+(?:\.\d+)?mm?)-x(\d+)\.([^.]+)$
Groups: (project_number, part_desc, material, thickness, quantity, extension)
```

### Material Code Mapping

```python
MATERIAL_MAP = {
    'Galv': 'Galvanized Steel',
    'SS': 'Stainless Steel',
    'MS': 'Mild Steel',
    'AL': 'Aluminum',
    'Alu': 'Aluminum',
    'Brass': 'Brass',
    'Copper': 'Copper',
}
```

### Document Type Detection

```python
DOCUMENT_TYPE_PATTERNS = {
    'Quote': ['quote', 'quotation', 'estimate'],
    'Invoice': ['invoice', 'bill'],
    'Proof of Payment': ['pop', 'proof', 'payment'],
    'Delivery Note': ['delivery', 'dispatch', 'shipping'],
}
```

---

## ⚠️ Error Handling Strategy

### Error Categories

1. **Critical Errors** (Stop migration)
   - Database connection failure
   - Source directory not found
   - Permission denied on target directories

2. **Project-Level Errors** (Skip project, continue)
   - Client code not found
   - Invalid folder name format
   - No files in project folder

3. **File-Level Errors** (Skip file, continue)
   - File not readable
   - Invalid file format
   - File size exceeds limit

### Rollback Strategy

- Use database transactions per project
- Keep checkpoint file for resume capability
- Don't delete source files
- Log all operations for manual rollback if needed

---

## ✅ Validation Checklist

### Pre-Migration
- [ ] Database backup created
- [ ] Source directory accessible
- [ ] All clients imported and verified
- [ ] Sufficient disk space available
- [ ] Test migration completed successfully

### During Migration
- [ ] Progress logging active
- [ ] Error logging functional
- [ ] Checkpoint saving enabled
- [ ] Transaction management working

### Post-Migration
- [ ] All projects imported
- [ ] All files uploaded
- [ ] Relationships verified
- [ ] File counts match
- [ ] No orphaned records
- [ ] Migration report generated

---

## 📊 Expected Outcomes

### Database Records
- **Projects**: One per project folder
- **Design Files**: One per DXF/LBRN2 file
- **Documents**: One per PDF/image/other file

### File Organization
```
data/
├── files/
│   └── projects/
│       ├── {project_id_1}/
│       │   ├── 20251016_123456_abc123.dxf
│       │   └── 20251016_123457_def456.lbrn2
│       └── {project_id_2}/
│           └── ...
└── documents/
    ├── quotes/
    ├── invoices/
    ├── pops/
    ├── delivery_notes/
    └── other/
```

### Migration Report
- Total clients processed
- Total projects created
- Total files uploaded
- Errors encountered
- Skipped items
- Execution time
- Recommendations

---

## 🚀 Next Steps

1. **Review and Approve Plan** - Stakeholder sign-off
2. **Create Test Data** - Sample profiles_import structure
3. **Implement Phase 2** - Core parsing module
4. **Unit Test Parsers** - Validate extraction logic
5. **Implement Phases 3-5** - Scanner, importer, uploader
6. **Integration Testing** - End-to-end test
7. **Implement Phase 6** - Main migration script
8. **Dry Run** - Validate-only mode on real data
9. **Production Migration** - Execute full import
10. **Verification** - Validate results and generate report

---

**Document Version**: 1.0  
**Created**: 2025-10-16  
**Status**: Ready for Implementation

