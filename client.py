"""Dust API Client — async httpx"""
import logging
from typing import Any, Dict, Optional, Union
import httpx

from config import Config

logger = logging.getLogger(__name__)


class DustClient:
    """Client HTTP async pour l'API Dust."""

    def __init__(self):
        self.base_url = Config.workspace_url()
        self.api_key = Config.DUST_API_KEY

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: float = 120.0,
    ) -> Dict[str, Any]:
        """Requête générique avec gestion d'erreurs."""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._headers(),
                    params=params,
                    json=json_data,
                )

                if response.status_code == 401:
                    return {
                        "error": True,
                        "message": "API Key invalide ou expirée. Vérifiez DUST_API_KEY.",
                    }
                if response.status_code == 403:
                    return {"error": True, "message": "Accès interdit. Vérifiez les permissions de la clé API."}
                if response.status_code == 404:
                    return {"error": True, "message": f"Ressource non trouvée: {endpoint}"}
                if response.status_code == 429:
                    return {"error": True, "message": "Rate limit atteint. Réessayez dans quelques secondes."}
                if response.status_code == 204 or not response.text:
                    return {"success": True, "message": "Opération réussie (pas de contenu retourné)."}

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                return {"error": True, "message": f"Timeout sur {method} {endpoint}"}
            except httpx.HTTPStatusError as e:
                detail = e.response.text[:500] if e.response else str(e)
                return {"error": True, "message": f"HTTP {e.response.status_code}: {detail}"}
            except Exception as e:
                logger.exception(f"Request failed: {e}")
                return {"error": True, "message": f"Erreur inattendue: {str(e)}"}

    # === Raccourcis ===
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, **kwargs) -> Dict:
        return await self._request("POST", endpoint, json_data=data, params=params, **kwargs)

    async def patch(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        return await self._request("PATCH", endpoint, json_data=data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict:
        return await self._request("DELETE", endpoint, **kwargs)

    # === Réponses non-JSON (YAML, CSV, texte brut) ===
    async def get_raw(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        accept: str = "text/plain",
        timeout: float = 120.0,
    ) -> Union[str, Dict[str, Any]]:
        """
        GET qui retourne le body brut (texte) au lieu de parser du JSON.
        Utilisé pour les endpoints qui retournent du YAML, CSV, etc.

        Retourne :
        - str : le contenu texte brut si succès (2xx)
        - dict : {"error": True, ...} si erreur
        """
        url = f"{self.base_url}{endpoint}"
        headers = {**self._headers(), "Accept": accept}

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    return response.text

                # Réutilise la même logique d'erreur que _request
                if response.status_code == 401:
                    return {"error": True, "status_code": 401, "message": "API Key invalide ou expirée."}
                if response.status_code == 403:
                    return {"error": True, "status_code": 403, "message": "Accès interdit. Vérifiez les permissions."}
                if response.status_code == 404:
                    return {"error": True, "status_code": 404, "message": f"Ressource non trouvée: {endpoint}"}
                if response.status_code == 429:
                    return {"error": True, "status_code": 429, "message": "Rate limit atteint."}

                # Tenter de parser le body d'erreur en JSON
                try:
                    error_body = response.json()
                    msg = error_body.get("error", {}).get("message", response.text[:500])
                except Exception:
                    msg = response.text[:500]

                return {"error": True, "status_code": response.status_code, "message": msg}

            except httpx.TimeoutException:
                return {"error": True, "status_code": 408, "message": f"Timeout sur GET {endpoint}"}
            except Exception as e:
                logger.exception(f"get_raw failed: {e}")
                return {"error": True, "status_code": 500, "message": f"Erreur inattendue: {str(e)}"}
