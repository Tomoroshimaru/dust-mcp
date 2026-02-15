"""Spaces — Lister les spaces du workspace"""
import json
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_list_spaces() -> str:
        """
        Lister tous les spaces disponibles dans le workspace.
        Utile pour découvrir les space_ids nécessaires aux autres outils
        (data sources, documents, tables, apps, etc.).

        Returns:
            Liste des spaces avec leurs IDs, noms et types.
        """
        client = DustClient()
        result = await client.get("/spaces")
        return json.dumps(result, indent=2, ensure_ascii=False)