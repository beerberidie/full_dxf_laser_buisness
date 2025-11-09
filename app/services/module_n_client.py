"""
Laser OS - Module N Client
Client for communicating with Module N file ingestion service
"""

import requests
from typing import List, Dict, Any, Optional
from flask import current_app
from werkzeug.datastructures import FileStorage
import logging

logger = logging.getLogger(__name__)


class ModuleNClient:
    """Client for communicating with Module N service."""
    
    def __init__(self):
        """Initialize Module N client with configuration from Flask app"""
        self.base_url = current_app.config.get('MODULE_N_URL', 'http://localhost:8081')
        self.timeout = current_app.config.get('MODULE_N_TIMEOUT', 30)
        self.enabled = current_app.config.get('MODULE_N_ENABLED', False)
    
    def is_enabled(self) -> bool:
        """Check if Module N is enabled"""
        return self.enabled
    
    def health_check(self) -> bool:
        """
        Check if Module N service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        if not self.enabled:
            logger.debug("Module N is disabled")
            return False
        
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, timeout=5)
            is_healthy = response.status_code == 200
            logger.info(f"Module N health check: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
        except Exception as e:
            logger.error(f"Module N health check failed: {str(e)}")
            return False
    
    def ingest_files(
        self,
        files: List[FileStorage],
        client_code: Optional[str] = None,
        project_code: Optional[str] = None,
        mode: str = "AUTO"
    ) -> List[Dict[str, Any]]:
        """
        Send files to Module N for ingestion.
        
        Args:
            files: List of FileStorage objects
            client_code: Optional client code (e.g., "CL-0001")
            project_code: Optional project code (e.g., "JB-2025-10-CL0001-001")
            mode: Processing mode (AUTO, dxf, pdf, excel, etc.)
        
        Returns:
            List of ingestion results
        
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        if not self.enabled:
            raise RuntimeError("Module N is not enabled")
        
        url = f"{self.base_url}/ingest"
        
        # Prepare files for upload
        files_data = []
        for file in files:
            # Reset file pointer to beginning
            file.seek(0)
            files_data.append(
                ('files', (file.filename, file.stream, file.content_type))
            )
        
        # Prepare form data
        data = {
            'mode': mode
        }
        if client_code:
            data['client_code'] = client_code
        if project_code:
            data['project_code'] = project_code
        
        try:
            logger.info(f"Sending {len(files)} file(s) to Module N")
            logger.debug(f"Client: {client_code}, Project: {project_code}, Mode: {mode}")
            
            response = requests.post(
                url,
                files=files_data,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            results = response.json()
            logger.info(f"Module N processed {len(results)} file(s)")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Module N request failed: {str(e)}")
            raise
    
    def get_ingest_status(self, ingest_id: int) -> Dict[str, Any]:
        """
        Get status of a file ingestion.
        
        Args:
            ingest_id: ID of the ingestion record
        
        Returns:
            Ingestion status dictionary
        
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        if not self.enabled:
            raise RuntimeError("Module N is not enabled")
        
        url = f"{self.base_url}/ingest/{ingest_id}"
        
        try:
            logger.info(f"Getting status for ingest ID: {ingest_id}")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Module N status check failed: {str(e)}")
            raise
    
    def re_extract(self, ingest_id: int, mode: str = "AUTO") -> Dict[str, Any]:
        """
        Re-run extraction on an existing file.
        
        Args:
            ingest_id: ID of the ingestion record
            mode: Processing mode
        
        Returns:
            Re-extraction result dictionary
        
        Raises:
            requests.exceptions.RequestException: If request fails
        """
        if not self.enabled:
            raise RuntimeError("Module N is not enabled")
        
        url = f"{self.base_url}/extract/{ingest_id}"
        
        try:
            logger.info(f"Re-extracting ingest ID: {ingest_id} with mode: {mode}")
            response = requests.post(
                url,
                data={'mode': mode},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Module N re-extraction failed: {str(e)}")
            raise


# Convenience function for use in routes
def get_module_n_client() -> ModuleNClient:
    """
    Get Module N client instance.
    
    Returns:
        ModuleNClient instance
    """
    return ModuleNClient()

