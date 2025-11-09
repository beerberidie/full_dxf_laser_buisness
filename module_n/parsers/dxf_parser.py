"""
Module N - DXF Parser
Extracts metadata from DXF files using ezdxf
"""

import ezdxf
from ezdxf.math import Vec3
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from decimal import Decimal

from ..models.schemas import (
    DXFMetadata,
    NormalizedMetadata,
    FileType,
    MATERIAL_MAP,
    MATERIAL_CODE_MAP
)

logger = logging.getLogger(__name__)


class DXFParser:
    """Parser for DXF files using ezdxf library."""
    
    # Common layer name patterns for detecting features
    OUTLINE_LAYERS = ['OUTLINE', 'CUT', 'PERIMETER', 'BORDER', 'EDGE']
    HOLE_LAYERS = ['HOLES', 'HOLE', 'DRILL', 'BORE']
    TEXT_LAYERS = ['NOTES', 'TEXT', 'ANNOTATION', 'LABEL']
    
    # Material detection patterns in layer names or text
    # Order matters - more specific patterns first to avoid false matches
    MATERIAL_PATTERNS = {
        'Galvanized Steel': ['galv', 'galvanized'],
        'Stainless Steel': ['stainless', 'inox', 'ss '],  # 'ss ' with space to avoid matching 'brass'
        'Mild Steel': ['mild steel', 'mild', 'ms '],  # 'ms ' with space
        'Aluminum': ['aluminum', 'aluminium', 'alu', 'al '],  # 'al ' with space
        'Brass': ['brass'],
        'Copper': ['copper'],
        'Carbon Steel': ['carbon steel', 'carbon'],
    }
    
    # Thickness detection patterns (e.g., "3mm", "5.0mm", "t=3", "thickness 5")
    THICKNESS_PATTERN = re.compile(r't[=:\s]*(\d+\.?\d*)\s*mm|(\d+\.?\d*)\s*mm|thickness[:\s]*(\d+\.?\d*)', re.IGNORECASE)
    
    def parse(self, file_path: str, filename: str, client_code: Optional[str] = None, 
              project_code: Optional[str] = None) -> NormalizedMetadata:
        """
        Parse DXF file and extract comprehensive metadata.
        
        Args:
            file_path: Full path to DXF file
            filename: Original filename
            client_code: Optional client code
            project_code: Optional project code
        
        Returns:
            NormalizedMetadata object with extracted data
        """
        logger.info(f"Parsing DXF file: {filename}")
        
        try:
            # Read DXF file
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            
            # Extract DXF-specific metadata
            dxf_meta = self._extract_dxf_metadata(doc, msp)
            
            # Parse filename for metadata hints
            filename_meta = self._parse_filename(filename)
            
            # Enhance metadata from DXF content
            enhanced_meta = self._enhance_from_dxf(filename_meta, dxf_meta)
            
            # Set client and project codes if provided
            if client_code:
                enhanced_meta.client_code = client_code
            if project_code:
                enhanced_meta.project_code = project_code
            
            # Add DXF metadata to extracted field
            enhanced_meta.extracted = dxf_meta.model_dump()
            enhanced_meta.detected_type = FileType.DXF
            enhanced_meta.source_file = filename
            
            # Calculate confidence score
            enhanced_meta.confidence_score = self._calculate_confidence(enhanced_meta, dxf_meta)
            
            logger.info(f"DXF parsing complete. Confidence: {enhanced_meta.confidence_score:.2f}")
            return enhanced_meta
            
        except ezdxf.DXFStructureError as e:
            logger.error(f"DXF structure error: {str(e)}")
            raise ValueError(f"Invalid DXF file structure: {str(e)}")
        except Exception as e:
            logger.error(f"DXF parsing error: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to parse DXF: {str(e)}")
    
    def _extract_dxf_metadata(self, doc, msp) -> DXFMetadata:
        """Extract DXF-specific metadata from document."""
        metadata = DXFMetadata()
        
        try:
            # Extract DXF version
            metadata.dxf_version = doc.dxfversion
            
            # Extract layers
            metadata.layers = [layer.dxf.name for layer in doc.layers]
            logger.debug(f"Found {len(metadata.layers)} layers: {metadata.layers}")
            
            # Count entities by type
            entity_counts = {}
            text_notes = []
            holes = []
            
            for entity in msp:
                entity_type = entity.dxftype()
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                
                # Extract text notes
                if entity_type in ['TEXT', 'MTEXT']:
                    try:
                        text = entity.dxf.text if hasattr(entity.dxf, 'text') else ''
                        if text and text.strip():
                            text_notes.append(text.strip())
                    except:
                        pass
                
                # Detect holes (circles on hole layers)
                if entity_type == 'CIRCLE':
                    try:
                        layer_name = entity.dxf.layer.upper() if hasattr(entity.dxf, 'layer') else ''
                        is_hole_layer = any(hole_layer in layer_name for hole_layer in self.HOLE_LAYERS)
                        
                        radius = entity.dxf.radius
                        diameter = radius * 2
                        center = entity.dxf.center
                        
                        holes.append({
                            'diameter': round(diameter, 2),
                            'center_x': round(center.x, 2),
                            'center_y': round(center.y, 2),
                            'layer': entity.dxf.layer,
                            'is_hole_layer': is_hole_layer
                        })
                    except:
                        pass
            
            metadata.entity_counts = entity_counts
            metadata.text_notes = text_notes
            metadata.holes = holes
            
            logger.debug(f"Entity counts: {entity_counts}")
            logger.debug(f"Found {len(text_notes)} text notes")
            logger.debug(f"Found {len(holes)} circles (potential holes)")
            
            # Calculate bounding box and dimensions
            try:
                extents = msp.extents()
                if extents:
                    min_x, min_y = extents.extmin.x, extents.extmin.y
                    max_x, max_y = extents.extmax.x, extents.extmax.y
                    
                    metadata.bounding_box = {
                        'min_x': round(min_x, 2),
                        'min_y': round(min_y, 2),
                        'max_x': round(max_x, 2),
                        'max_y': round(max_y, 2),
                        'width': round(max_x - min_x, 2),
                        'height': round(max_y - min_y, 2)
                    }
                    
                    logger.debug(f"Bounding box: {metadata.bounding_box['width']}mm x {metadata.bounding_box['height']}mm")
            except Exception as e:
                logger.warning(f"Could not calculate bounding box: {str(e)}")
            
            # Calculate perimeter (from outline layers)
            perimeter = self._calculate_perimeter(msp)
            if perimeter > 0:
                metadata.perimeter_mm = round(perimeter, 2)
                logger.debug(f"Perimeter: {metadata.perimeter_mm}mm")
            
            # Calculate approximate area
            if metadata.bounding_box:
                metadata.area_mm2 = round(
                    metadata.bounding_box['width'] * metadata.bounding_box['height'], 2
                )
            
        except Exception as e:
            logger.error(f"Error extracting DXF metadata: {str(e)}", exc_info=True)
        
        return metadata
    
    def _calculate_perimeter(self, msp) -> float:
        """Calculate perimeter from outline entities."""
        perimeter = 0.0
        
        try:
            for entity in msp:
                layer_name = entity.dxf.layer.upper() if hasattr(entity.dxf, 'layer') else ''
                is_outline = any(outline in layer_name for outline in self.OUTLINE_LAYERS)
                
                if not is_outline:
                    continue
                
                entity_type = entity.dxftype()
                
                if entity_type == 'LINE':
                    start = Vec3(entity.dxf.start)
                    end = Vec3(entity.dxf.end)
                    perimeter += start.distance(end)
                
                elif entity_type == 'CIRCLE':
                    radius = entity.dxf.radius
                    perimeter += 2 * 3.14159 * radius
                
                elif entity_type == 'ARC':
                    radius = entity.dxf.radius
                    start_angle = entity.dxf.start_angle
                    end_angle = entity.dxf.end_angle
                    angle_diff = abs(end_angle - start_angle)
                    perimeter += (angle_diff / 360.0) * 2 * 3.14159 * radius
                
                elif entity_type in ['LWPOLYLINE', 'POLYLINE']:
                    try:
                        points = list(entity.get_points())
                        for i in range(len(points) - 1):
                            p1 = Vec3(points[i][:2])
                            p2 = Vec3(points[i+1][:2])
                            perimeter += p1.distance(p2)
                        
                        # Close the polyline if needed
                        if entity.is_closed:
                            p1 = Vec3(points[-1][:2])
                            p2 = Vec3(points[0][:2])
                            perimeter += p1.distance(p2)
                    except:
                        pass
        
        except Exception as e:
            logger.warning(f"Error calculating perimeter: {str(e)}")

        return perimeter

    def _parse_filename(self, filename: str) -> NormalizedMetadata:
        """
        Parse filename to extract metadata hints.
        Supports multiple filename formats.
        """
        # Remove extension
        name_without_ext = Path(filename).stem

        # Try new format: CL0001-JB-2025-10-CL0001-001-BracketLeft-MS-5mm-x14-v1
        pattern1 = re.compile(
            r'^([A-Z]{2}\d{4})-(.+?)-([A-Za-z]+)-([A-Za-z]+)-(\d+\.?\d*)mm(?:-x(\d+))?(?:-v(\d+))?$',
            re.IGNORECASE
        )
        match = pattern1.match(name_without_ext)

        if match:
            client_code = match.group(1)
            project_code = match.group(2)
            part_name = match.group(3)
            material_code = match.group(4)
            thickness = float(match.group(5))
            quantity = int(match.group(6)) if match.group(6) else 1
            version = int(match.group(7)) if match.group(7) else 1

            # Map material code to full name
            material = None
            # Reverse lookup: MATERIAL_CODE_MAP has full_name -> code, we need code -> full_name
            for full_name, code in MATERIAL_CODE_MAP.items():
                if material_code.upper() == code.upper():
                    material = full_name
                    break

            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.DXF,
                client_code=client_code,
                project_code=project_code,
                part_name=part_name,
                material=material,
                thickness_mm=thickness,
                quantity=quantity,
                version=version,
                extracted={}
            )

        # Try old format: 0001-Full Gas Box Version1-Galv-1mm-x1
        pattern2 = re.compile(
            r'^(\d{4})-(.+?)-([A-Za-z]+)-(\d+\.?\d*)mm-x(\d+)$',
            re.IGNORECASE
        )
        match = pattern2.match(name_without_ext)

        if match:
            part_name = match.group(2)
            material_code = match.group(3)
            thickness = float(match.group(4))
            quantity = int(match.group(5))

            # Map material code
            material = MATERIAL_MAP.get(material_code, 'Other')

            return NormalizedMetadata(
                source_file=filename,
                detected_type=FileType.DXF,
                part_name=part_name,
                material=material,
                thickness_mm=thickness,
                quantity=quantity,
                extracted={}
            )

        # Fallback: minimal metadata
        return NormalizedMetadata(
            source_file=filename,
            detected_type=FileType.DXF,
            extracted={}
        )

    def _enhance_from_dxf(self, metadata: NormalizedMetadata, dxf_meta: DXFMetadata) -> NormalizedMetadata:
        """Enhance metadata using information extracted from DXF content."""

        # Try to detect material from layers or text
        if not metadata.material:
            detected_material = self._detect_material_from_text(dxf_meta.text_notes + dxf_meta.layers)
            if detected_material:
                metadata.material = detected_material
                logger.debug(f"Detected material from DXF: {detected_material}")

        # Try to detect thickness from text
        if not metadata.thickness_mm:
            detected_thickness = self._detect_thickness_from_text(dxf_meta.text_notes + dxf_meta.layers)
            if detected_thickness:
                metadata.thickness_mm = detected_thickness
                logger.debug(f"Detected thickness from DXF: {detected_thickness}mm")

        # Try to extract part name from text notes
        if not metadata.part_name and dxf_meta.text_notes:
            # Use the first substantial text note as part name
            for note in dxf_meta.text_notes:
                if len(note) > 3 and len(note) < 100:
                    # Clean up the note
                    part_name = re.sub(r'[^a-zA-Z0-9\s-]', '', note)
                    part_name = part_name.strip()
                    if part_name:
                        metadata.part_name = part_name
                        logger.debug(f"Extracted part name from text: {part_name}")
                        break

        return metadata

    def _detect_material_from_text(self, text_list: List[str]) -> Optional[str]:
        """Detect material from text notes or layer names."""
        combined_text = ' '.join(text_list).lower()

        # Check patterns in order (more specific first)
        for material, patterns in self.MATERIAL_PATTERNS.items():
            for pattern in patterns:
                # For short codes like 'ss ', 'ms ', check word boundaries
                if pattern.endswith(' '):
                    # Check if pattern appears at start or after a space
                    if combined_text.startswith(pattern.strip() + ' ') or ' ' + pattern in combined_text:
                        return material
                else:
                    # For longer patterns, simple substring match
                    if pattern in combined_text:
                        return material

        return None

    def _detect_thickness_from_text(self, text_list: List[str]) -> Optional[float]:
        """Detect thickness from text notes or layer names."""
        combined_text = ' '.join(text_list)

        match = self.THICKNESS_PATTERN.search(combined_text)
        if match:
            # Extract the first non-None group
            for group in match.groups():
                if group:
                    try:
                        return float(group)
                    except:
                        pass

        return None

    def _calculate_confidence(self, metadata: NormalizedMetadata, dxf_meta: DXFMetadata) -> float:
        """
        Calculate confidence score based on how much metadata was extracted.
        Score ranges from 0.0 to 1.0.
        """
        score = 0.0

        # Base score for successful DXF parsing
        score += 0.2

        # Client code (10%)
        if metadata.client_code:
            score += 0.1

        # Project code (10%)
        if metadata.project_code:
            score += 0.1

        # Part name (15%)
        if metadata.part_name:
            score += 0.15

        # Material (15%)
        if metadata.material:
            score += 0.15

        # Thickness (15%)
        if metadata.thickness_mm:
            score += 0.15

        # DXF has valid bounding box (10%)
        if dxf_meta.bounding_box:
            score += 0.1

        # DXF has entities (5%)
        if dxf_meta.entity_counts:
            score += 0.05

        # DXF has layers (5%)
        if dxf_meta.layers and len(dxf_meta.layers) > 0:
            score += 0.05

        # Cap at 1.0
        return min(score, 1.0)

