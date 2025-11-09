"""
Module N - Excel Parser
Extracts metadata from Excel files (.xlsx and .xls) using pandas
"""

import pandas as pd
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from decimal import Decimal

from ..models.schemas import (
    ExcelMetadata,
    NormalizedMetadata,
    FileType,
    MATERIAL_MAP,
    MATERIAL_CODE_MAP
)

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parser for Excel files (.xlsx and .xls) using pandas."""
    
    # Material detection patterns (reuse from DXF/PDF parsers)
    MATERIAL_PATTERNS = {
        'Galvanized Steel': ['galv', 'galvanized'],
        'Stainless Steel': ['stainless', 'inox', 'ss '],
        'Mild Steel': ['mild steel', 'mild', 'ms '],
        'Aluminum': ['aluminum', 'aluminium', 'alu', 'al '],
        'Brass': ['brass'],
        'Copper': ['copper'],
        'Carbon Steel': ['carbon steel', 'carbon'],
    }
    
    # Thickness detection patterns
    THICKNESS_PATTERN = re.compile(
        r't[=:\s]*(\d+\.?\d*)\s*mm|(\d+\.?\d*)\s*mm|thickness[:\s]*(\d+\.?\d*)',
        re.IGNORECASE
    )
    
    # Quantity detection patterns
    QUANTITY_PATTERN = re.compile(
        r'qty[:\s]*(\d+)|quantity[:\s]*(\d+)|x\s*(\d+)|(\d+)\s*pcs?',
        re.IGNORECASE
    )
    
    # Client/Project code patterns
    CLIENT_CODE_PATTERN = re.compile(r'CL[-\s]?(\d{4})', re.IGNORECASE)
    PROJECT_CODE_PATTERN = re.compile(
        r'(JB|PR|PO)[-\s]?(\d{4}[-\s]\d{2}[-\s]\w+[-\s]\d{3})',
        re.IGNORECASE
    )
    
    # Common column header patterns for schema detection
    COLUMN_PATTERNS = {
        'part_name': ['part', 'part name', 'part_name', 'item', 'description', 'component'],
        'material': ['material', 'mat', 'steel type', 'metal'],
        'thickness': ['thickness', 'thick', 't', 'gauge'],
        'quantity': ['qty', 'quantity', 'amount', 'count', 'pcs'],
        'client': ['client', 'customer', 'client code', 'customer code'],
        'project': ['project', 'job', 'project code', 'job code', 'po'],
        'price': ['price', 'unit price', 'cost', 'rate'],
        'total': ['total', 'amount', 'subtotal'],
        'width': ['width', 'w', 'x'],
        'height': ['height', 'h', 'y', 'length'],
    }
    
    # Maximum rows to extract (performance limit)
    MAX_DATA_ROWS = 100
    
    def parse(self, file_path: str, filename: str, client_code: Optional[str] = None,
              project_code: Optional[str] = None) -> NormalizedMetadata:
        """
        Parse Excel file and extract comprehensive metadata.
        
        Args:
            file_path: Path to the Excel file
            filename: Original filename
            client_code: Optional client code override
            project_code: Optional project code override
            
        Returns:
            NormalizedMetadata object with extracted data
        """
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            
            # Extract Excel-specific metadata
            excel_meta = self._extract_excel_metadata(excel_file, file_path)
            
            # Parse filename for metadata
            filename_meta = self._parse_filename(filename)
            
            # Enhance metadata from Excel content
            enhanced_meta = self._enhance_from_excel(excel_meta, filename_meta)
            
            # Override with provided codes
            if client_code:
                enhanced_meta.client_code = client_code
            if project_code:
                enhanced_meta.project_code = project_code
            
            # Add Excel metadata to extracted field
            enhanced_meta.extracted = {
                'sheet_names': excel_meta.get('sheet_names', []),
                'sheet_count': excel_meta.get('sheet_count', 0),
                'row_count': excel_meta.get('row_count', 0),
                'column_count': excel_meta.get('column_count', 0),
                'headers': excel_meta.get('headers', []),
                'data_rows': excel_meta.get('data_rows', []),
                'detected_schema': excel_meta.get('detected_schema', 'unknown'),
                'column_mapping': excel_meta.get('column_mapping', {}),
            }
            
            # Calculate confidence score
            enhanced_meta.confidence_score = self._calculate_confidence(enhanced_meta)
            
            # Set file type
            enhanced_meta.detected_type = FileType.EXCEL
            enhanced_meta.source_file = filename
            
            # Get file size
            enhanced_meta.file_size = Path(file_path).stat().st_size
            enhanced_meta.mime_type = self._get_mime_type(filename)
            
            excel_file.close()
            
            logger.info(f"Excel parsed successfully: {filename} (confidence: {enhanced_meta.confidence_score:.2f})")
            return enhanced_meta
            
        except Exception as e:
            logger.error(f"Failed to parse Excel {filename}: {str(e)}")
            raise ValueError(f"Failed to parse Excel: {str(e)}")
    
    def _extract_excel_metadata(self, excel_file: pd.ExcelFile, file_path: str) -> Dict[str, Any]:
        """Extract Excel-specific metadata from workbook."""
        metadata = {}
        
        try:
            # Get sheet names
            sheet_names = excel_file.sheet_names
            metadata['sheet_names'] = sheet_names
            metadata['sheet_count'] = len(sheet_names)
            
            # Read first sheet (or first non-empty sheet)
            df = None
            for sheet_name in sheet_names:
                try:
                    temp_df = excel_file.parse(sheet_name)
                    if not temp_df.empty:
                        df = temp_df
                        metadata['active_sheet'] = sheet_name
                        break
                except Exception as e:
                    logger.warning(f"Could not read sheet '{sheet_name}': {str(e)}")
                    continue
            
            if df is None or df.empty:
                logger.warning("No readable data found in Excel file")
                metadata['row_count'] = 0
                metadata['column_count'] = 0
                metadata['headers'] = []
                metadata['data_rows'] = []
                metadata['detected_schema'] = 'empty'
                return metadata
            
            # Get dimensions
            metadata['row_count'] = len(df)
            metadata['column_count'] = len(df.columns)
            
            # Get headers (column names)
            headers = [str(col) for col in df.columns]
            metadata['headers'] = headers
            
            # Extract data rows (limited for performance)
            data_rows = []
            for idx, row in df.head(self.MAX_DATA_ROWS).iterrows():
                row_dict = {}
                for col in df.columns:
                    value = row[col]
                    # Convert to string, handle NaN
                    if pd.isna(value):
                        row_dict[str(col)] = None
                    else:
                        row_dict[str(col)] = str(value)
                data_rows.append(row_dict)
            
            metadata['data_rows'] = data_rows
            
            # Detect schema/structure
            schema_info = self._detect_schema(headers, data_rows)
            metadata['detected_schema'] = schema_info['schema_type']
            metadata['column_mapping'] = schema_info['column_mapping']
            
            # Collect all cell values as text for pattern matching
            all_text = []
            all_text.extend(headers)
            all_text.extend(sheet_names)
            for row in data_rows[:20]:  # First 20 rows for text analysis
                all_text.extend([str(v) for v in row.values() if v is not None])
            
            metadata['all_text'] = ' '.join(all_text)
            
        except Exception as e:
            logger.warning(f"Error extracting Excel metadata: {str(e)}")
        
        return metadata
    
    def _detect_schema(self, headers: List[str], data_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect the schema/structure of the spreadsheet."""
        schema_info = {
            'schema_type': 'unknown',
            'column_mapping': {}
        }
        
        if not headers:
            return schema_info
        
        # Normalize headers for matching
        headers_lower = [h.lower().strip() for h in headers]
        
        # Map columns to known fields
        for field, patterns in self.COLUMN_PATTERNS.items():
            for i, header in enumerate(headers_lower):
                for pattern in patterns:
                    if pattern in header:
                        schema_info['column_mapping'][field] = headers[i]
                        break
        
        # Detect schema type based on column combinations
        mapping = schema_info['column_mapping']
        
        if 'part_name' in mapping and 'material' in mapping and 'thickness' in mapping:
            if 'price' in mapping or 'total' in mapping:
                schema_info['schema_type'] = 'quote'
            else:
                schema_info['schema_type'] = 'cutting_list'
        elif 'part_name' in mapping and 'quantity' in mapping:
            schema_info['schema_type'] = 'parts_list'
        elif 'price' in mapping and 'total' in mapping:
            schema_info['schema_type'] = 'invoice'
        elif 'material' in mapping and 'quantity' in mapping:
            schema_info['schema_type'] = 'inventory'
        else:
            schema_info['schema_type'] = 'generic'
        
        return schema_info
    
    def _parse_filename(self, filename: str) -> NormalizedMetadata:
        """Parse metadata from filename."""
        # Remove extension
        name_without_ext = Path(filename).stem
        
        # Try new format: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1.xlsx
        pattern1 = r'^(CL\d{4})-([\w-]+)-([\w-]+)-([A-Z]+)-(\d+\.?\d*)mm-x(\d+)-v(\d+)$'
        match = re.match(pattern1, name_without_ext, re.IGNORECASE)
        
        if match:
            material_code = match.group(4)
            material = None
            for full_name, code in MATERIAL_CODE_MAP.items():
                if material_code.upper() == code.upper():
                    material = full_name
                    break
            
            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.EXCEL,
                client_code=match.group(1),
                project_code=match.group(2),
                part_name=match.group(3),
                material=material,
                thickness_mm=float(match.group(5)),
                quantity=int(match.group(6)),
                version=int(match.group(7)),
                extracted={}
            )
        
        # Try old format: 0001-Full Gas Box-Galv-1mm-x1.xlsx
        pattern2 = r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*)mm-x(\d+)$'
        match = re.match(pattern2, name_without_ext, re.IGNORECASE)
        
        if match:
            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.EXCEL,
                part_name=match.group(2),
                material=MATERIAL_MAP.get(match.group(3), 'Other'),
                thickness_mm=float(match.group(4)),
                quantity=int(match.group(5)),
                extracted={}
            )
        
        # Fallback: minimal metadata
        return NormalizedMetadata(
            source_file=filename,
            detected_type=FileType.EXCEL,
            extracted={}
        )

    def _enhance_from_excel(self, excel_meta: Dict[str, Any],
                            filename_meta: NormalizedMetadata) -> NormalizedMetadata:
        """Enhance metadata using Excel content."""
        # Start with filename metadata
        enhanced = filename_meta

        # Get column mapping and data
        column_mapping = excel_meta.get('column_mapping', {})
        data_rows = excel_meta.get('data_rows', [])
        all_text = excel_meta.get('all_text', '')

        # Extract from first data row if available
        if data_rows and len(data_rows) > 0:
            first_row = data_rows[0]

            # Extract part name from mapped column
            if not enhanced.part_name and 'part_name' in column_mapping:
                col_name = column_mapping['part_name']
                part_value = first_row.get(col_name)
                if part_value and part_value != 'None':
                    enhanced.part_name = part_value

            # Extract material from mapped column
            if not enhanced.material and 'material' in column_mapping:
                col_name = column_mapping['material']
                mat_value = first_row.get(col_name)
                if mat_value and mat_value != 'None':
                    # Try to map material code or name
                    enhanced.material = self._normalize_material(mat_value)

            # Extract thickness from mapped column
            if not enhanced.thickness_mm and 'thickness' in column_mapping:
                col_name = column_mapping['thickness']
                thick_value = first_row.get(col_name)
                if thick_value and thick_value != 'None':
                    thickness = self._extract_number(thick_value)
                    if thickness:
                        enhanced.thickness_mm = thickness

            # Extract quantity from mapped column
            if enhanced.quantity == 1 and 'quantity' in column_mapping:
                col_name = column_mapping['quantity']
                qty_value = first_row.get(col_name)
                if qty_value and qty_value != 'None':
                    quantity = self._extract_number(qty_value)
                    if quantity and 1 <= quantity <= 10000:
                        enhanced.quantity = int(quantity)

            # Extract client code from mapped column
            if not enhanced.client_code and 'client' in column_mapping:
                col_name = column_mapping['client']
                client_value = first_row.get(col_name)
                if client_value and client_value != 'None':
                    client_code = self._detect_client_code(client_value)
                    if client_code:
                        enhanced.client_code = client_code

            # Extract project code from mapped column
            if not enhanced.project_code and 'project' in column_mapping:
                col_name = column_mapping['project']
                project_value = first_row.get(col_name)
                if project_value and project_value != 'None':
                    project_code = self._detect_project_code(project_value)
                    if project_code:
                        enhanced.project_code = project_code

        # Detect from all text if not found in columns
        if not enhanced.material:
            material = self._detect_material_from_text(all_text)
            if material:
                enhanced.material = material

        if not enhanced.thickness_mm:
            thickness = self._detect_thickness_from_text(all_text)
            if thickness:
                enhanced.thickness_mm = thickness

        if enhanced.quantity == 1:
            quantity = self._detect_quantity_from_text(all_text)
            if quantity:
                enhanced.quantity = quantity

        if not enhanced.client_code:
            client_code = self._detect_client_code(all_text)
            if client_code:
                enhanced.client_code = client_code

        if not enhanced.project_code:
            project_code = self._detect_project_code(all_text)
            if project_code:
                enhanced.project_code = project_code

        # Try to extract part name from sheet name if not found
        if not enhanced.part_name:
            sheet_names = excel_meta.get('sheet_names', [])
            if sheet_names:
                # Use first sheet name that's not generic
                for sheet_name in sheet_names:
                    if sheet_name.lower() not in ['sheet1', 'sheet2', 'sheet3', 'data', 'main']:
                        enhanced.part_name = sheet_name
                        break

        return enhanced

    def _normalize_material(self, material_str: str) -> Optional[str]:
        """Normalize material string to standard material name."""
        material_str = material_str.strip()

        # Check if it's a material code
        for full_name, code in MATERIAL_CODE_MAP.items():
            if material_str.upper() == code.upper():
                return full_name

        # Check if it matches a material pattern
        material = self._detect_material_from_text(material_str)
        if material:
            return material

        # Check if it's already a full name
        if material_str in MATERIAL_CODE_MAP:
            return material_str

        return None

    def _extract_number(self, value_str: str) -> Optional[float]:
        """Extract numeric value from string."""
        try:
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.]', '', str(value_str))
            if cleaned:
                return float(cleaned)
        except (ValueError, TypeError):
            pass
        return None

    def _detect_material_from_text(self, text: str) -> Optional[str]:
        """Detect material from text content."""
        text_lower = text.lower()

        # Check patterns in order (more specific first)
        for material, patterns in self.MATERIAL_PATTERNS.items():
            for pattern in patterns:
                # For short codes like 'ss ', 'ms ', check word boundaries
                if pattern.endswith(' '):
                    if text_lower.startswith(pattern.strip() + ' ') or ' ' + pattern in text_lower:
                        return material
                else:
                    if pattern in text_lower:
                        return material

        return None

    def _detect_thickness_from_text(self, text: str) -> Optional[float]:
        """Detect thickness from text content."""
        match = self.THICKNESS_PATTERN.search(text)
        if match:
            for group in match.groups():
                if group:
                    try:
                        return float(group)
                    except ValueError:
                        continue
        return None

    def _detect_quantity_from_text(self, text: str) -> Optional[int]:
        """Detect quantity from text content."""
        match = self.QUANTITY_PATTERN.search(text)
        if match:
            for group in match.groups():
                if group:
                    try:
                        qty = int(group)
                        if 1 <= qty <= 10000:
                            return qty
                    except ValueError:
                        continue
        return None

    def _detect_client_code(self, text: str) -> Optional[str]:
        """Detect client code from text content."""
        match = self.CLIENT_CODE_PATTERN.search(text)
        if match:
            return f"CL{match.group(1)}"
        return None

    def _detect_project_code(self, text: str) -> Optional[str]:
        """Detect project code from text content."""
        match = self.PROJECT_CODE_PATTERN.search(text)
        if match:
            prefix = match.group(1).upper()
            code = match.group(2).replace(' ', '-')
            return f"{prefix}-{code}"
        return None

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension."""
        ext = Path(filename).suffix.lower()
        if ext == '.xlsx':
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif ext == '.xls':
            return 'application/vnd.ms-excel'
        else:
            return 'application/octet-stream'

    def _calculate_confidence(self, metadata: NormalizedMetadata) -> float:
        """Calculate confidence score based on extracted metadata completeness."""
        score = 0.0

        # Base score for successful parsing
        score += 0.2

        # Add points for each field
        if metadata.client_code:
            score += 0.1
        if metadata.project_code:
            score += 0.1
        if metadata.part_name:
            score += 0.15
        if metadata.material:
            score += 0.15
        if metadata.thickness_mm:
            score += 0.15
        if metadata.quantity and metadata.quantity > 1:
            score += 0.05

        # Add points for Excel-specific data
        extracted = metadata.extracted or {}
        if extracted.get('sheet_count', 0) > 0:
            score += 0.05
        if extracted.get('detected_schema') in ['quote', 'cutting_list', 'parts_list']:
            score += 0.05

        return min(score, 1.0)

