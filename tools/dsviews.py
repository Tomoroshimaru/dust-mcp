"""DataSource Views — Vues filtrées sur les data sources"""
import json
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_dsv_list(space_id: str) -> str:
        """
        Lister les Data Source Views d'un space.
        Une DSV est une vue filtrée sur une data source.

        Args:
            space_id: ID du space
        """
        client = DustClient()
        result = await client.get(f"/spaces/{space_id}/data_source_views")
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_dsv_search(
        space_id: str,
        dsv_id: str,
        query: str,
        top_k: int = 10,
        full_text: bool = False,
        timestamp_gt: Optional[int] = None,
        timestamp_lt: Optional[int] = None,
    ) -> str:
        """
        Recherche sémantique dans une Data Source View.
        Plus ciblé que dust_search_nodes car limité à une DSV spécifique.

        Args:
            space_id: ID du space
            dsv_id: ID de la data source view
            query: Requête de recherche
            top_k: Nombre de résultats (default 10)
            full_text: Retourner le contenu complet (default False)
            timestamp_gt: Filtrer après ce timestamp Unix ms
            timestamp_lt: Filtrer avant ce timestamp Unix ms
        """
        client = DustClient()
        params = {
            "query": query,
            "top_k": top_k,
            "full_text": str(full_text).lower(),
        }
        if timestamp_gt:
            params["timestamp_gt"] = timestamp_gt
        if timestamp_lt:
            params["timestamp_lt"] = timestamp_lt

        result = await client.get(
            f"/spaces/{space_id}/data_source_views/{dsv_id}/search",
            params=params,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)