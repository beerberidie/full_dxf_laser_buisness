import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Dict, Any, Optional
from config import settings

class WhatsAppGraphClient:
    def __init__(self, access_token: Optional[str] = None, phone_number_id: Optional[str] = None, version: Optional[str] = None):
        self.access_token = access_token or settings.access_token
        self.phone_number_id = phone_number_id or settings.phone_number_id
        self.version = version or settings.graph_api_version
        self.base_url = f"https://graph.facebook.com/{self.version}"

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if resp.status_code >= 400:
            raise requests.exceptions.RequestException(f"{resp.status_code}: {resp.text}")
        return resp.json()
