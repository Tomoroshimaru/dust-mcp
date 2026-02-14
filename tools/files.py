"""Files — Upload de fichiers"""
import json
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_files_upload(
        content_type: str,
        file_name: str,
        file_size: int,
        use_case: str = "conversation",
    ) -> str:
        """
        Créer une URL d'upload pour un fichier.
        Retourne une URL pré-signée vers laquelle uploader le fichier.

        Args:
            content_type: Type MIME du fichier (ex: "application/pdf", "image/png", "text/csv")
            file_name: Nom du fichier
            file_size: Taille du fichier en bytes
            use_case: Cas d'usage — "conversation" (default) ou "avatar"
        """
        client = DustClient()
        result = await client.post(
            "/files",
            data={
                "contentType": content_type,
                "fileName": file_name,
                "fileSize": file_size,
                "useCase": use_case,
            },
        )
        return json.dumps(result, indent=2, ensure_ascii=False)