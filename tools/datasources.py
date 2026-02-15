"""DataSources — Lister et chercher dans les data sources"""
import json
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_data_list(space_id: str) -> str:
        """
        Lister toutes les data sources d'un space.
        Retourne: nom, description, provider, connecteur pour chaque data source.

        Args:
            space_id: ID du space (trouvable via dust_list_spaces)
        """
        client = DustClient()
        result = await client.get(f"/spaces/{space_id}/data_sources")
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_data_search(
        space_id: str,
        data_source_id: str,
        query: str,
        top_k: int = 10,
        full_text: bool = False,
    ) -> str:
        """
        Recherche sémantique dans une data source spécifique.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            query: Requête de recherche
            top_k: Nombre de résultats (default 10)
            full_text: Si True, retourne le texte complet des documents
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data_sources/{data_source_id}/search",
            params={
                "query": query,
                "top_k": top_k,
                "full_text": str(full_text).lower(),
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)