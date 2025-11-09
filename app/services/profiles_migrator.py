"""
Profiles Migration Service for Laser OS.

This service handles the complete migration of client projects from the
profiles_import directory structure into the database.

Phase 3 of Profiles Migration System.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

from app import db
from app.models import Client, Project, DesignFile, ProjectDocument
from app.services.profiles_parser import ProfilesParser


class ProfilesMigrator:
    """
    Service class for migrating profiles from file system to database.
    
    Handles scanning, parsing, validation, and import of projects and files.
    """
    
    def __init__(self, base_path: str = "profiles_import", upload_folder: str = "data/files", documents_folder: str = "data/documents", default_status: str = None):
        """
        Initialize the migrator.

        Args:
            base_path: Base path to profiles_import directory
            upload_folder: Path to upload folder for design files
            documents_folder: Path to documents folder
            default_status: Default status for migrated projects (defaults to 'Quote')
        """
        self.base_path = Path(base_path)
        self.upload_folder = Path(upload_folder)
        self.documents_folder = Path(documents_folder)
        self.default_status = default_status or Project.STATUS_QUOTE

        # Statistics
        self.stats = {
            'projects_scanned': 0,
            'projects_created': 0,
            'design_files_uploaded': 0,
            'documents_uploaded': 0,
            'errors': [],
            'warnings': []
        }
    
    def verify_client(self, client_code: str) -> Optional[Client]:
        """
        Verify that a client exists in the database.
        
        Args:
            client_code: Client code (e.g., 'CL-0002')
        
        Returns:
            Client object if found, None otherwise
        """
        return Client.query.filter_by(client_code=client_code).first()
    
    def scan_client_projects(self, client_code: str) -> List[Dict[str, Any]]:
        """
        Scan all projects for a client.
        
        Args:
            client_code: Client code (e.g., 'CL-0002')
        
        Returns:
            List of project dictionaries with folder and file information
        """
        client_path = self.base_path / client_code / "1.Projects"
        
        if not client_path.exists():
            self.stats['errors'].append(f"Client path not found: {client_path}")
            return []
        
        projects = []
        
        for project_folder in sorted(client_path.iterdir()):
            if not project_folder.is_dir():
                continue
            
            # Parse folder name
            folder_data = ProfilesParser.parse_project_folder(project_folder.name)
            
            if not folder_data:
                self.stats['warnings'].append(f"Could not parse folder: {project_folder.name}")
                continue
            
            # Scan files in project
            design_files = []
            documents = []
            
            for file_path in sorted(project_folder.iterdir()):
                if not file_path.is_file():
                    continue
                
                file_ext = file_path.suffix.lower()
                
                # Check if it's a design file
                if file_ext in ['.dxf', '.lbrn2']:
                    file_data = ProfilesParser.parse_file_name(file_path.name)
                    
                    if file_data:
                        file_data['file_path'] = file_path
                        file_data['file_size'] = file_path.stat().st_size
                        file_data['file_extension'] = file_ext
                        design_files.append(file_data)
                    else:
                        self.stats['warnings'].append(f"Could not parse design file: {file_path.name}")
                
                # Check if it's a document
                elif file_ext in ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']:
                    documents.append({
                        'file_name': file_path.name,
                        'file_path': file_path,
                        'file_size': file_path.stat().st_size,
                        'file_extension': file_ext
                    })
            
            projects.append({
                'folder_name': project_folder.name,
                'folder_path': project_folder,
                'parsed_data': folder_data,
                'design_files': design_files,
                'documents': documents
            })
            
            self.stats['projects_scanned'] += 1
        
        return projects
    
    def generate_stored_filename(self, original_filename: str) -> str:
        """
        Generate a unique stored filename.
        
        Args:
            original_filename: Original filename
        
        Returns:
            Unique stored filename with timestamp
        """
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        ext = Path(original_filename).suffix
        return f"{timestamp}_{unique_id}{ext}"
    
    def create_project(self, client: Client, project_data: Dict[str, Any]) -> Optional[Project]:
        """
        Create a project record in the database.
        
        Args:
            client: Client object
            project_data: Project data dictionary from scan
        
        Returns:
            Created Project object or None on failure
        """
        try:
            parsed = project_data['parsed_data']
            design_files = project_data['design_files']
            
            # Get material info from first design file
            material_type = None
            material_thickness = None
            parts_quantity = 0
            
            if design_files:
                first_file = design_files[0]
                material_type = first_file['material_type']
                material_thickness = first_file['thickness']
                
                # Sum quantities from all design files
                parts_quantity = sum(f['quantity'] for f in design_files)
            
            # Create project
            project = Project(
                client_id=client.id,
                name=parsed['description'],
                description=f"Imported from {project_data['folder_name']}",
                status=self.default_status,
                created_at=parsed['date_created'],
                material_type=material_type,
                material_thickness=material_thickness,
                parts_quantity=parts_quantity
            )
            
            # project_code will be auto-generated by the event listener
            
            db.session.add(project)
            db.session.flush()  # Get the project ID without committing
            
            self.stats['projects_created'] += 1
            
            return project
        
        except Exception as e:
            self.stats['errors'].append(f"Error creating project {project_data['folder_name']}: {str(e)}")
            return None
    
    def upload_design_file(self, project: Project, file_data: Dict[str, Any]) -> Optional[DesignFile]:
        """
        Upload a design file and create database record.
        
        Args:
            project: Project object
            file_data: File data dictionary from scan
        
        Returns:
            Created DesignFile object or None on failure
        """
        try:
            source_path = file_data['file_path']
            original_filename = source_path.name
            stored_filename = self.generate_stored_filename(original_filename)
            
            # Create project folder
            project_folder = self.upload_folder / str(project.id)
            project_folder.mkdir(parents=True, exist_ok=True)
            
            # Destination path
            dest_path = project_folder / stored_filename
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Relative path for database (format: {project_id}/{stored_filename})
            relative_path = f"{project.id}/{stored_filename}"
            
            # Detect file type
            file_ext = file_data['file_extension']
            file_type = 'lbrn2' if file_ext == '.lbrn2' else 'dxf'
            
            # Create database record
            design_file = DesignFile(
                project_id=project.id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=relative_path,
                file_size=file_data['file_size'],
                file_type=file_type,
                uploaded_by='profiles_migrator'
            )
            
            db.session.add(design_file)
            
            self.stats['design_files_uploaded'] += 1
            
            return design_file
        
        except Exception as e:
            self.stats['errors'].append(f"Error uploading design file {file_data.get('file_name', 'unknown')}: {str(e)}")
            return None
    
    def upload_document(self, project: Project, file_data: Dict[str, Any]) -> Optional[ProjectDocument]:
        """
        Upload a document and create database record.
        
        Args:
            project: Project object
            file_data: File data dictionary from scan
        
        Returns:
            Created ProjectDocument object or None on failure
        """
        try:
            source_path = file_data['file_path']
            original_filename = source_path.name
            stored_filename = self.generate_stored_filename(original_filename)
            
            # Determine document type from filename
            # Valid types: Quote, Invoice, Proof of Payment, Delivery Note
            filename_lower = original_filename.lower()
            if 'quote' in filename_lower or 'quotation' in filename_lower or 'quo' in filename_lower:
                document_type = 'Quote'
                doc_folder = 'quotes'
            elif 'invoice' in filename_lower or 'inv' in filename_lower:
                document_type = 'Invoice'
                doc_folder = 'invoices'
            elif 'pop' in filename_lower or 'proof' in filename_lower or 'payment' in filename_lower:
                document_type = 'Proof of Payment'
                doc_folder = 'pops'
            elif 'delivery' in filename_lower:
                document_type = 'Delivery Note'
                doc_folder = 'delivery_notes'
            else:
                # Default to Quote for unknown document types
                document_type = 'Quote'
                doc_folder = 'quotes'
            
            # Create document folder
            dest_folder = self.documents_folder / doc_folder
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Destination path
            dest_path = dest_folder / stored_filename
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Create database record
            document = ProjectDocument(
                project_id=project.id,
                document_type=document_type,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_path=str(dest_path),
                file_size=file_data['file_size'],
                uploaded_by='profiles_migrator'
            )
            
            db.session.add(document)
            
            self.stats['documents_uploaded'] += 1
            
            return document

        except Exception as e:
            self.stats['errors'].append(f"Error uploading document {file_data.get('file_name', 'unknown')}: {str(e)}")
            return None

    def migrate_client(self, client_code: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate all projects for a client.

        Args:
            client_code: Client code (e.g., 'CL-0002')
            dry_run: If True, only scan and preview without database writes

        Returns:
            Dictionary with migration results and statistics
        """
        # Reset statistics
        self.stats = {
            'projects_scanned': 0,
            'projects_created': 0,
            'design_files_uploaded': 0,
            'documents_uploaded': 0,
            'errors': [],
            'warnings': []
        }

        # Step 1: Verify client exists
        client = self.verify_client(client_code)

        if not client:
            return {
                'success': False,
                'message': f"Client {client_code} not found in database",
                'stats': self.stats
            }

        # Step 2: Scan projects
        projects = self.scan_client_projects(client_code)

        if not projects:
            return {
                'success': False,
                'message': f"No projects found for client {client_code}",
                'stats': self.stats
            }

        # Step 3: Preview mode - return scan results
        if dry_run:
            return {
                'success': True,
                'message': 'Scan completed successfully (dry run)',
                'client': {
                    'code': client.client_code,
                    'name': client.name,
                    'id': client.id
                },
                'projects': projects,
                'stats': self.stats
            }

        # Step 4: Actual migration - create projects and upload files
        try:
            for project_data in projects:
                # Create project
                project = self.create_project(client, project_data)

                if not project:
                    continue

                # Upload design files
                for file_data in project_data['design_files']:
                    self.upload_design_file(project, file_data)

                # Upload documents
                for file_data in project_data['documents']:
                    self.upload_document(project, file_data)

            # Commit all changes
            db.session.commit()

            return {
                'success': True,
                'message': f'Successfully migrated {self.stats["projects_created"]} projects for {client.name}',
                'client': {
                    'code': client.client_code,
                    'name': client.name,
                    'id': client.id
                },
                'stats': self.stats
            }

        except Exception as e:
            # Rollback on error
            db.session.rollback()
            self.stats['errors'].append(f"Migration failed: {str(e)}")

            return {
                'success': False,
                'message': f'Migration failed: {str(e)}',
                'stats': self.stats
            }

    def get_migration_preview(self, client_code: str) -> str:
        """
        Get a formatted preview of what will be migrated.

        Args:
            client_code: Client code (e.g., 'CL-0002')

        Returns:
            Formatted string with migration preview
        """
        result = self.migrate_client(client_code, dry_run=True)

        if not result['success']:
            return f"❌ {result['message']}"

        client = result['client']
        projects = result['projects']
        stats = result['stats']

        output = []
        output.append("=" * 70)
        output.append("MIGRATION PREVIEW")
        output.append("=" * 70)
        output.append(f"\nClient: {client['name']} ({client['code']})")
        output.append(f"Client ID: {client['id']}")
        output.append(f"\nProjects to Import: {len(projects)}")

        total_design_files = sum(len(p['design_files']) for p in projects)
        total_documents = sum(len(p['documents']) for p in projects)

        output.append(f"Design Files: {total_design_files}")
        output.append(f"Documents: {total_documents}")

        output.append("\n" + "=" * 70)
        output.append("PROJECT DETAILS")
        output.append("=" * 70)

        for i, project in enumerate(projects, 1):
            parsed = project['parsed_data']
            output.append(f"\n{i}. {parsed['description']}")
            output.append(f"   Folder: {project['folder_name']}")
            output.append(f"   Date: {parsed['date_created'].strftime('%Y-%m-%d')}")
            output.append(f"   Design Files: {len(project['design_files'])}")
            output.append(f"   Documents: {len(project['documents'])}")

            if project['design_files']:
                first_file = project['design_files'][0]
                output.append(f"   Material: {first_file['material_type']}")
                output.append(f"   Thickness: {first_file['thickness']} mm")
                total_qty = sum(f['quantity'] for f in project['design_files'])
                output.append(f"   Total Parts: {total_qty}")

        if stats['warnings']:
            output.append("\n" + "=" * 70)
            output.append("WARNINGS")
            output.append("=" * 70)
            for warning in stats['warnings']:
                output.append(f"⚠️  {warning}")

        if stats['errors']:
            output.append("\n" + "=" * 70)
            output.append("ERRORS")
            output.append("=" * 70)
            for error in stats['errors']:
                output.append(f"❌ {error}")

        return "\n".join(output)

