"""Search — Recherche sémantique dans le workspace"""
import json
import logging
from typing import Optional
from client import DustClient

logger = logging.getLogger(__name__)


def register(mcp):

    @mcp.tool()
    async def dust_search_nodes(
        query: str,
        limit: int = 10,
        view_type: str = "all",
        include_data_sources: bool = True,
        space_ids: Optional[str] = None,
        data_source_view_ids: Optional[str] = None,
        timestamp_gt: Optional[int] = None,
        timestamp_lt: Optional[int] = None,
    ) -> str:
        """
        Recherche sémantique dans le workspace Dust.
        Retourne les documents/nodes les plus pertinents.

        Si space_ids n'est pas fourni, recherche automatiquement dans tous les spaces.

        Args:
            query: Requête de recherche en langage naturel (minimum 3 caractères)
            limit: Nombre de résultats (default 10, max 100)
            view_type: Type de vue — "all" (default), "document", "table"
            include_data_sources: Inclure les data sources dans les résultats (default True)
            space_ids: Filtrer par IDs de spaces (séparés par des virgules, optionnel — si omis, tous les spaces)
            data_source_view_ids: Filtrer par IDs de data source views (séparés par des virgules, optionnel)
            timestamp_gt: Filtrer docs après ce timestamp Unix ms (optionnel)
            timestamp_lt: Filtrer docs avant ce timestamp Unix ms (optionnel)
        """
        client = DustClient()

        # Validation minimale
        if len(query.strip()) < 3:
            return json.dumps({"error": True, "message": "La requête doit contenir au moins 3 caractères."})

        body = {
            "query": query,
            "limit": min(max(limit, 1), 100),
            "viewType": view_type,
            "includeDataSources": include_data_sources,
        }

        # Résolution des spaceIds
        if space_ids:
            body["spaceIds"] = [s.strip() for s in space_ids.split(",")]
        else:
            # Fallback : récupérer tous les spaces du workspace
            try:
                spaces_result = await client.get("/spaces")
                if "spaces" in spaces_result:
                    body["spaceIds"] = [s["sId"] for s in spaces_result["spaces"]]
                    logger.info(f"Search fallback: using {len(body['spaceIds'])} spaces")
                else:
                    return json.dumps({
                        "error": True,
                        "message": "Impossible de récupérer les spaces. Fournissez space_ids manuellement."
                    })
            except Exception as e:
                return json.dumps({
                    "error": True,
                    "message": f"Erreur lors de la récupération des spaces: {str(e)}"
                })

        if data_source_view_ids:
            body["dataSourceViewIds"] = [d.strip() for d in data_source_view_ids.split(",")]
        if timestamp_gt:
            body["timestampGt"] = timestamp_gt
        if timestamp_lt:
            body["timestampLt"] = timestamp_lt

        result = await client.post("/search", data=body)
        return json.dumps(result, indent=2, ensure_ascii=False)