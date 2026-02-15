"""Documents — CRUD sur les documents des data sources"""
import json
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_docs_list(
        space_id: str,
        data_source_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> str:
        """
        Lister les documents d'une data source.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            limit: Nombre max de documents (default 20)
            offset: Décalage pour la pagination (default 0)
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data_sources/{data_source_id}/documents",
            params={"limit": limit, "offset": offset},
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_docs_get(
        space_id: str,
        data_source_id: str,
        document_id: str,
    ) -> str:
        """
        Récupérer un document spécifique avec son contenu complet.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            document_id: ID du document
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/data_sources/{data_source_id}/documents/{document_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_docs_upsert(
        space_id: str,
        data_source_id: str,
        document_id: str,
        title: str,
        text: str,
        mime_type: str = "text/plain",
        source_url: Optional[str] = None,
        tags: Optional[str] = None,
        timestamp: Optional[int] = None,
        light_document_output: bool = True,
    ) -> str:
        """
        Créer ou mettre à jour un document dans une data source.
        ⚠️ Action d'écriture — Si le document_id existe déjà, il sera écrasé.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            document_id: ID du document (sera créé s'il n'existe pas)
            title: Titre du document
            text: Contenu textuel du document
            mime_type: Type MIME (default: text/plain). Autres: text/markdown, text/html
            source_url: URL source optionnelle
            tags: Tags séparés par des virgules (optionnel). Ex: "tag1,tag2"
            timestamp: Timestamp Unix ms du document (optionnel)
            light_document_output: Si True, retourne une version légère (default True)
        """
        client = DustClient()

        # Body en snake_case (confirmé par le code source Dust)
        body = {
            "title": title,
            "text": text,
            "mime_type": mime_type,
            "light_document_output": light_document_output,
        }
        if source_url:
            body["source_url"] = source_url
        if tags:
            body["tags"] = [t.strip() for t in tags.split(",")]
        if timestamp:
            body["timestamp"] = timestamp

        result = await client.post(
            f"/spaces/{space_id}/data_sources/{data_source_id}/documents/{document_id}",
            data=body,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_docs_delete(
        space_id: str,
        data_source_id: str,
        document_id: str,
    ) -> str:
        """
        Supprimer un document d'une data source.
        ⚠️ Action destructive — irréversible.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            document_id: ID du document à supprimer
        """
        client = DustClient()
        result = await client.delete(
            f"/spaces/{space_id}/data_sources/{data_source_id}/documents/{document_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_docs_update_parents(
        space_id: str,
        data_source_id: str,
        document_id: str,
        parents_json: str,
    ) -> str:
        """
        Modifier la hiérarchie parent d'un document.
        Permet de réorganiser les documents dans l'arborescence.

        ⚠️ Cette opération peut être rejetée si la clé API n'a pas les permissions système.

        Args:
            space_id: ID du space
            data_source_id: ID de la data source
            document_id: ID du document
            parents_json: JSON array des IDs parents. Ex: '["parent_id_1", "parent_id_2"]'
        """
        client = DustClient()
        try:
            parents = json.loads(parents_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": True, "message": f"JSON invalide: {str(e)}"})

        result = await client.post(
            f"/spaces/{space_id}/data_sources/{data_source_id}/documents/{document_id}/parents",
            data={"parents": parents},
        )
        return json.dumps(result, indent=2, ensure_ascii=False)