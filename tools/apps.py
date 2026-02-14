"""Apps — Lister et exécuter des Dust Apps"""
import json
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_apps_list(space_id: str) -> str:
        """
        Lister toutes les Dust Apps d'un space.

        Args:
            space_id: ID du space
        """
        client = DustClient()
        result = await client.get(f"/spaces/{space_id}/apps")
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_apps_run(
        space_id: str,
        app_id: str,
        config_json: str,
        inputs_json: Optional[str] = None,
    ) -> str:
        """
        Lancer l'exécution d'une Dust App.
        ⚠️ Peut consommer des crédits AI selon l'app.

        Args:
            space_id: ID du space
            app_id: ID de l'app (sId)
            config_json: JSON de configuration des blocs de l'app.
                Exemple: '{"block_name": {"provider_id": "openai", "model_id": "gpt-4"}}'
            inputs_json: JSON des inputs de l'app (optionnel).
                Exemple: '[{"key": "value"}]'
        """
        client = DustClient()
        try:
            config = json.loads(config_json)
            inputs = json.loads(inputs_json) if inputs_json else []
        except json.JSONDecodeError as e:
            return json.dumps({"error": True, "message": f"JSON invalide: {str(e)}"})

        result = await client.post(
            f"/spaces/{space_id}/apps/{app_id}/runs",
            data={"config": config, "inputs": inputs},
            timeout=180.0,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_apps_get_run(
        space_id: str, app_id: str, run_id: str
    ) -> str:
        """
        Récupérer le résultat d'un run d'app.

        Args:
            space_id: ID du space
            app_id: ID de l'app
            run_id: ID du run
        """
        client = DustClient()
        result = await client.get(
            f"/spaces/{space_id}/apps/{app_id}/runs/{run_id}"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)