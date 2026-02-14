"""Tables & Rows — CRUD complet sur les tables structurées"""
import json
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_tables_list(space_id: str, data_source_id: str) -> str:
        """
        Lister les tables d'une data source.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_get(
        space_id: str, data_source_id: str, table_id: str
    ) -> str:
        """
        Récupérer les détails d'une table (schéma, description, metadata).

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables/{table_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_upsert(
        space_id: str,
        data_source_id: str,
        table_id: str,
        name: str,
        description: str,
    ) -> str:
        """
        Créer ou mettre à jour une table.
        ⚠️ Action d'écriture — Si la table existe, elle sera mise à jour.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table (sera créée si n'existe pas)
            name: Nom de la table
            description: Description de la table
        """
        client = DustClient()
        result = await client.post(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables",
            data={
                "table_id": table_id,
                "name": name,
                "description": description,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_delete(
        space_id: str, data_source_id: str, table_id: str
    ) -> str:
        """
        Supprimer une table et toutes ses rows.
        ⚠️ Action destructive — irréversible.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table à supprimer
        """
        client = DustClient()
        result = await client.delete(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables/{table_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_list_rows(
        space_id: str,
        data_source_id: str,
        table_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """
        Lister les rows d'une table avec pagination.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table
            limit: Nombre max de rows (default 50)
            offset: Décalage pour la pagination (default 0)
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables/{table_id}/rows",
            params={"limit": limit, "offset": offset},
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_upsert_rows(
        space_id: str,
        data_source_id: str,
        table_id: str,
        rows_json: str,
        truncate: bool = False,
    ) -> str:
        """
        Insérer ou mettre à jour des rows dans une table.
        ⚠️ Action d'écriture.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table
            rows_json: JSON array des rows. Chaque row doit avoir "row_id" et "value" (dict des colonnes).
                Exemple: '[{"row_id": "row1", "value": {"name": "Alice", "age": 30}}, {"row_id": "row2", "value": {"name": "Bob", "age": 25}}]'
            truncate: Si True, supprime toutes les rows existantes avant l'upsert (default False)
        """
        client = DustClient()
        try:
            rows = json.loads(rows_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": True, "message": f"JSON invalide: {str(e)}"})

        result = await client.post(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables/{table_id}/rows",
            data={"rows": rows, "truncate": truncate},
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_get_row(
        space_id: str, data_source_id: str, table_id: str, row_id: str
    ) -> str:
        """
        Récupérer une row spécifique d'une table.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table
            row_id: ID de la row
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables/{table_id}/rows/{row_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_tables_delete_row(
        space_id: str, data_source_id: str, table_id: str, row_id: str
    ) -> str:
        """
        Supprimer une row d'une table.
        ⚠️ Action destructive.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            table_id: ID de la table
            row_id: ID de la row à supprimer
        """
        client = DustClient()
        result = await client.delete(
            f"/spaces/{space_id}/data-sources/{data_source_id}/tables/{table_id}/rows/{row_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)