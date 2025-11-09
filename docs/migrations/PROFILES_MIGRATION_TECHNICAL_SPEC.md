# Profiles Migration - Technical Specification

## 📐 Module Specifications

### Module 1: Filename Parser (`app/services/profiles_parser.py`)

#### Class: `ProfilesParser`

**Purpose**: Extract structured metadata from folder and file names

**Methods:**

```python
class ProfilesParser:
    """Parse project folder and file names to extract metadata."""
    
    # Material code mapping
    MATERIAL_MAP = {
        'Galv': 'Galvanized Steel',
        'Galvanized': 'Galvanized Steel',
        'SS': 'Stainless Steel',
        'Stainless': 'Stainless Steel',
        'MS': 'Mild Steel',
        'Mild': 'Mild Steel',
        'AL': 'Aluminum',
        'Alu': 'Aluminum',
        'Aluminum': 'Aluminum',
        'Brass': 'Brass',
        'Copper': 'Copper',
    }
    
    @staticmethod
    def parse_project_folder(folder_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse project folder name.
        
        Pattern: {project_number}-{description}-{date}
        Example: "0001-Gas Cover box 1 to 1 ratio-10.15.2025"
        
        Returns:
            {
                'project_number': '0001',
                'description': 'Gas Cover box 1 to 1 ratio',
                'date_created': date(2025, 10, 15),
                'raw_date': '10.15.2025'
            }
        """
        
    @staticmethod
    def parse_file_name(file_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse file name to extract metadata.
        
        Pattern: {project_number}-{part_description}-{material}-{thickness}-{quantity}.{ext}
        Example: "0001-Full Gas Box Version1-Galv-1mm-x1.dxf"
        
        Returns:
            {
                'project_number': '0001',
                'part_description': 'Full Gas Box Version1',
                'material_code': 'Galv',
                'material_type': 'Galvanized Steel',
                'thickness': 1.0,
                'thickness_raw': '1mm',
                'quantity': 1,
                'quantity_raw': 'x1',
                'extension': 'dxf',
                'file_type': 'dxf'
            }
        """
    
    @staticmethod
    def map_material(material_code: str) -> str:
        """
        Map material code to full material name.
        
        Args:
            material_code: Short code like 'Galv', 'SS', 'MS'
            
        Returns:
            Full material name or 'Other' if not found
        """
    
    @staticmethod
    def parse_thickness(thickness_str: str) -> Optional[float]:
        """
        Parse thickness string to float.
        
        Examples:
            '1mm' -> 1.0
            '1.5mm' -> 1.5
            '2' -> 2.0
            
        Returns:
            Thickness in mm as float
        """
    
    @staticmethod
    def parse_quantity(quantity_str: str) -> Optional[int]:
        """
        Parse quantity string to integer.
        
        Examples:
            'x1' -> 1
            'x10' -> 10
            '5' -> 5
            
        Returns:
            Quantity as integer
        """
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """
        Parse date string in various formats.
        
        Supported formats:
            - MM.DD.YYYY (10.15.2025)
            - DD-MM-YYYY (15-10-2025)
            - YYYY-MM-DD (2025-10-15)
            - MM/DD/YYYY (10/15/2025)
            
        Returns:
            date object or None if parsing fails
        """
```

#### Regex Patterns

```python
# Project folder pattern
PROJECT_FOLDER_PATTERN = r'^(\d{4})-(.+?)-(\d{1,2}[\./-]\d{1,2}[\./-]\d{4})$'

# File name pattern (flexible)
FILE_NAME_PATTERN = r'^(\d{4})-(.+?)-([A-Za-z0-9]+)-(\d+(?:\.\d+)?mm?)-x?(\d+)\.([^.]+)$'

# Alternative file name pattern (more lenient)
FILE_NAME_PATTERN_ALT = r'^(\d{4})-(.+?)\.([^.]+)$'
```

---

### Module 2: Directory Scanner (`app/services/profiles_scanner.py`)

#### Class: `ProfilesScanner`

**Purpose**: Traverse directory structure and collect project data

**Data Structures:**

```python
@dataclass
class ProjectData:
    """Container for project data from file system."""
    client_code: str
    project_number: str
    project_description: str
    date_created: Optional[date]
    folder_path: Path
    design_files: List[Path]  # .dxf, .lbrn2
    document_files: List[Path]  # .pdf, .jpg, etc.
    metadata: Dict[str, Any]
    errors: List[str]

@dataclass
class ScanResult:
    """Results from directory scan."""
    projects: List[ProjectData]
    total_clients: int
    total_projects: int
    total_files: int
    missing_clients: List[str]
    errors: List[str]
```

**Methods:**

```python
class ProfilesScanner:
    """Scan profiles_import directory structure."""
    
    def __init__(self, base_path: Path, db_session):
        self.base_path = base_path
        self.db_session = db_session
        self.parser = ProfilesParser()
        
    def scan(self) -> ScanResult:
        """
        Scan entire profiles_import directory.
        
        Returns:
            ScanResult with all discovered projects
        """
        
    def scan_client_folder(self, client_code: str, client_path: Path) -> List[ProjectData]:
        """
        Scan a single client's folder.
        
        Args:
            client_code: Client code (e.g., 'CL-0001')
            client_path: Path to client folder
            
        Returns:
            List of ProjectData for this client
        """
        
    def scan_project_folder(self, client_code: str, project_path: Path) -> Optional[ProjectData]:
        """
        Scan a single project folder.
        
        Args:
            client_code: Client code
            project_path: Path to project folder
            
        Returns:
            ProjectData or None if invalid
        """
        
    def classify_file(self, file_path: Path) -> Tuple[str, str]:
        """
        Classify file by type.
        
        Returns:
            Tuple of (category, file_type)
            - category: 'design' or 'document'
            - file_type: 'dxf', 'lbrn2', 'pdf', 'image', 'other'
        """
        
    def validate_client_exists(self, client_code: str) -> bool:
        """
        Check if client exists in database.
        
        Args:
            client_code: Client code to check
            
        Returns:
            True if client exists
        """
```

---

### Module 3: Project Importer (`app/services/profiles_importer.py`)

#### Class: `ProfilesImporter`

**Purpose**: Create project records and upload files

**Methods:**

```python
class ProfilesImporter:
    """Import projects from ProfilesScanner data."""
    
    def __init__(self, app, db_session):
        self.app = app
        self.db = db_session
        self.parser = ProfilesParser()
        self.stats = ImportStats()
        
    def import_project(self, project_data: ProjectData) -> Optional[Project]:
        """
        Import a single project.
        
        Args:
            project_data: ProjectData from scanner
            
        Returns:
            Created Project or None if failed
            
        Process:
            1. Get client from database
            2. Check for duplicates
            3. Create project record
            4. Upload design files
            5. Upload document files
            6. Commit transaction
        """
        
    def create_project_record(self, client: Client, project_data: ProjectData) -> Project:
        """
        Create Project model instance.
        
        Args:
            client: Client model instance
            project_data: Parsed project data
            
        Returns:
            Project instance (not yet committed)
        """
        
    def upload_design_files(self, project: Project, file_paths: List[Path]) -> List[DesignFile]:
        """
        Upload DXF and LBRN2 files.
        
        Args:
            project: Project instance
            file_paths: List of file paths to upload
            
        Returns:
            List of created DesignFile records
        """
        
    def upload_documents(self, project: Project, file_paths: List[Path]) -> List[ProjectDocument]:
        """
        Upload document files.
        
        Args:
            project: Project instance
            file_paths: List of file paths to upload
            
        Returns:
            List of created ProjectDocument records
        """
        
    def detect_document_type(self, file_path: Path) -> str:
        """
        Detect document type from filename.
        
        Patterns:
            - 'quote' in name -> 'Quote'
            - 'invoice' in name -> 'Invoice'
            - 'pop' or 'payment' in name -> 'Proof of Payment'
            - 'delivery' in name -> 'Delivery Note'
            - default -> 'Other'
            
        Returns:
            Document type string
        """
        
    def check_duplicate(self, client_id: int, project_number: str) -> Optional[Project]:
        """
        Check if project already exists.
        
        Args:
            client_id: Client ID
            project_number: Project number from folder
            
        Returns:
            Existing Project or None
        """
```

---

### Module 4: Migration Script (`migrate_profiles.py`)

#### Main Script Structure

```python
#!/usr/bin/env python3
"""
Profiles Migration Script

Migrate client projects from profiles_import directory structure
into Laser OS database.

Usage:
    python migrate_profiles.py --source ./profiles_import --validate-only
    python migrate_profiles.py --source ./profiles_import --client CL-0001
    python migrate_profiles.py --source ./profiles_import --all
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from app import create_app, db
from app.services.profiles_scanner import ProfilesScanner
from app.services.profiles_importer import ProfilesImporter


class MigrationOrchestrator:
    """Orchestrate the migration process."""
    
    def __init__(self, app, source_path: Path, options: Dict):
        self.app = app
        self.source_path = source_path
        self.options = options
        self.scanner = ProfilesScanner(source_path, db.session)
        self.importer = ProfilesImporter(app, db.session)
        
    def run(self) -> bool:
        """
        Execute migration.
        
        Returns:
            True if successful
        """
        
    def validate_only(self) -> bool:
        """Run validation without importing."""
        
    def import_all(self) -> bool:
        """Import all projects."""
        
    def import_client(self, client_code: str) -> bool:
        """Import projects for specific client."""
        
    def generate_report(self) -> str:
        """Generate migration report."""


def main():
    parser = argparse.ArgumentParser(description='Migrate profiles to database')
    parser.add_argument('--source', required=True, help='Path to profiles_import directory')
    parser.add_argument('--validate-only', action='store_true', help='Validate without importing')
    parser.add_argument('--client', help='Import specific client only')
    parser.add_argument('--all', action='store_true', help='Import all clients')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (same as validate-only)')
    
    args = parser.parse_args()
    
    # Create app
    app = create_app('development')
    
    # Run migration
    with app.app_context():
        orchestrator = MigrationOrchestrator(
            app,
            Path(args.source),
            vars(args)
        )
        
        success = orchestrator.run()
        
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     MIGRATION PROCESS FLOW                       │
└─────────────────────────────────────────────────────────────────┘

1. SCAN PHASE
   ┌──────────────────┐
   │ profiles_import/ │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ ProfilesScanner  │──┐
   │ - Find clients   │  │
   │ - Find projects  │  │
   │ - Catalog files  │  │
   └────────┬─────────┘  │
            │            │
            ▼            │
   ┌──────────────────┐  │
   │ ProfilesParser   │◀─┘
   │ - Parse folders  │
   │ - Parse files    │
   │ - Extract meta   │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  ProjectData[]   │
   │  (in memory)     │
   └────────┬─────────┘

2. VALIDATION PHASE
            │
            ▼
   ┌──────────────────┐
   │ Validate Clients │──→ Missing clients? → Report & Exit
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Validate Data    │──→ Invalid data? → Report & Continue
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Check Duplicates │──→ Duplicates? → Skip or Update
   └────────┬─────────┘

3. IMPORT PHASE
            │
            ▼
   ┌──────────────────┐
   │ For each project │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ BEGIN TRANSACTION│
   └────────┬─────────┘
            │
            ├──→ Create Project Record
            │
            ├──→ Upload Design Files (DXF/LBRN2)
            │    └──→ Copy to data/files/projects/{id}/
            │         └──→ Create DesignFile records
            │
            ├──→ Upload Documents (PDF/Images)
            │    └──→ Copy to data/documents/{type}/
            │         └──→ Create ProjectDocument records
            │
            ▼
   ┌──────────────────┐
   │ COMMIT or ROLLBACK│
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Log Progress     │
   └────────┬─────────┘

4. REPORTING PHASE
            │
            ▼
   ┌──────────────────┐
   │ Generate Report  │
   │ - Stats          │
   │ - Errors         │
   │ - Warnings       │
   └──────────────────┘
```

---

## 📊 Database Transaction Strategy

### Per-Project Transactions

```python
def import_project(self, project_data: ProjectData) -> Optional[Project]:
    """Import with transaction safety."""
    
    try:
        # Start transaction
        db.session.begin_nested()
        
        # Create project
        project = self.create_project_record(client, project_data)
        db.session.add(project)
        db.session.flush()  # Get project.id
        
        # Upload files
        design_files = self.upload_design_files(project, project_data.design_files)
        documents = self.upload_documents(project, project_data.document_files)
        
        # Commit transaction
        db.session.commit()
        
        self.log_success(project)
        return project
        
    except Exception as e:
        # Rollback transaction
        db.session.rollback()
        
        # Clean up any copied files
        self.cleanup_files(project)
        
        self.log_error(project_data, e)
        return None
```

---

## 🎯 Success Criteria

### Validation Success
- ✅ All client codes found in database
- ✅ All folder names parse successfully
- ✅ All file names parse successfully
- ✅ No critical errors detected

### Import Success
- ✅ All projects created in database
- ✅ All files uploaded successfully
- ✅ All relationships established
- ✅ No orphaned records
- ✅ File counts match source

### Data Integrity
- ✅ Project codes unique and valid
- ✅ Client relationships correct
- ✅ File paths accessible
- ✅ Metadata accurately extracted
- ✅ No data loss

---

**Document Version**: 1.0  
**Created**: 2025-10-16  
**Status**: Ready for Implementation

