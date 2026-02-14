"""Search — Recherche sémantique dans le workspace"""
import json
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_search_nodes(
        query: str,
        top_k: int = 10,
        space_ids: Optional[str] = None,
        data_source_view_ids: Optional[str] = None,
        timestamp_gt: Optional[int] = None,
        timestamp_lt: Optional[int] = None,
    ) -> str:
        """
        Recherche sémantique dans le workspace Dust.
        Retourne les documents/nodes les plus pertinents.

        Args:
            query: Requête de recherche en langage naturel
            top_k: Nombre de résultats (default 10, max 100)
            space_ids: Filtrer par IDs de spaces (séparés par des virgules, optionnel)
            data_source_view_ids: Filtrer par IDs de data source views (séparés par des virgules, optionnel)
            timestamp_gt: Filtrer docs après ce timestamp Unix ms (optionnel)
            timestamp_lt: Filtrer docs avant ce timestamp Unix ms (optionnel)
        """
        client = DustClient()

        body = {"query": query, "top_k": min(top_k, 100)}
        if space_ids:
            body["spaceIds"] = [s.strip() for s in space_ids.split(",")]
        if data_source_view_ids:
            body["dataSourceViewIds"] = [d.strip() for d in data_source_view_ids.split(",")]
        if timestamp_gt:
            body["timestampGt"] = timestamp_gt
        if timestamp_lt:
            body["timestampLt"] = timestamp_lt

        result = await client.post("/search", data=body)
        return json.dumps(result, indent=2, ensure_ascii=False)