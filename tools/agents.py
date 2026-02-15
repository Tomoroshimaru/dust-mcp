"""Agents — Recherche, détails et mise à jour des agents Dust"""
import json
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_agents_search(query: str) -> str:
        """
        Chercher un agent par nom dans le workspace.
        Utile pour trouver le sId d'un agent avant de l'utiliser.

        Args:
            query: Nom ou partie du nom de l'agent à chercher
        """
        client = DustClient()
        result = await client.get(
            "/assistant/agent_configurations/search",
            params={"q": query},
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_agents_get(agent_sid: str) -> str:
        """
        Récupérer la configuration complète d'un agent : modèle, instructions,
        actions, temperature, maxSteps, etc.

        Args:
            agent_sid: L'identifiant sId de l'agent (trouvable via dust_agents_search)
        """
        client = DustClient()
        result = await client.get(f"/assistant/agent_configurations/{agent_sid}")
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_agents_update(agent_sid: str, updates_json: str) -> str:
        """
        Mettre à jour la configuration d'un agent.
        ⚠️ Action d'écriture — utiliser avec précaution.

        Args:
            agent_sid: L'identifiant sId de l'agent
            updates_json: JSON string des champs à modifier.
                Exemple: '{"name": "Nouveau nom", "model": {"providerId": "anthropic", "modelId": "claude-sonnet-4-20250514", "temperature": 0.7}}'
                Champs modifiables: name, description, instructions, model, maxStepsPerRun, pictureUrl, userFavorite
        """
        client = DustClient()
        try:
            updates = json.loads(updates_json)
        except json.JSONDecodeError as e:
            return json.dumps({"error": True, "message": f"JSON invalide: {str(e)}"})

        result = await client.patch(
            f"/assistant/agent_configurations/{agent_sid}",
            data=updates,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)