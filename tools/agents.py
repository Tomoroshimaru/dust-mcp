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
    async def dust_agents_list(
        view: str = "list",
        with_authors: bool = False
    ) -> str:
        """
        Lister tous les agents du workspace avec leur configuration.

        Retourne pour chaque agent : sId, nom, description, statut, scope,
        modèle, température, nombre d'actions, et optionnellement les derniers éditeurs.

        Args:
            view: Filtre de vue. Options :
                - "list" : agents actifs accessibles à l'utilisateur (défaut)
                - "all" : tous les agents non privés
                - "published" : agents publiés
                - "workspace" : agents workspace uniquement
                - "global" : agents globaux (built-in Dust)
                - "favorites" : agents marqués favoris
            with_authors: Inclure les derniers éditeurs de chaque agent (défaut: false)
        """
        client = DustClient()

        valid_views = ["all", "list", "workspace", "published", "global", "favorites"]
        if view not in valid_views:
            return json.dumps({
                "error": True,
                "message": f"view must be one of: {', '.join(valid_views)}"
            })

        params = {"view": view}
        if with_authors:
            params["withAuthors"] = "true"

        result = await client.get(
            "/assistant/agent_configurations",
            params=params,
        )

        # Si erreur du client, retourner tel quel
        if isinstance(result, dict) and result.get("error"):
            return json.dumps(result, indent=2, ensure_ascii=False)

        agents = result.get("agentConfigurations", [])

        # Construire un résumé lisible
        summary = []
        for agent in agents:
            entry = {
                "sId": agent.get("sId"),
                "name": agent.get("name"),
                "description": agent.get("description"),
                "status": agent.get("status"),
                "scope": agent.get("scope"),
                "model": agent.get("model", {}).get("modelId", "unknown"),
                "provider": agent.get("model", {}).get("providerId", "unknown"),
                "temperature": agent.get("model", {}).get("temperature"),
                "maxStepsPerRun": agent.get("maxStepsPerRun"),
                "actionsCount": len(agent.get("actions", [])),
                "userFavorite": agent.get("userFavorite", False),
            }
            if with_authors and "lastAuthors" in agent:
                entry["lastAuthors"] = agent["lastAuthors"]
            summary.append(entry)

        output = {
            "totalAgents": len(summary),
            "view": view,
            "agents": summary
        }

        return json.dumps(output, indent=2, ensure_ascii=False)
    
    @mcp.tool()
    async def dust_agents_export_yaml(agent_sid: str) -> str:
        """
        Exporter la configuration complète d'un agent au format YAML.

        Retourne le contenu YAML brut prêt à être sauvegardé ou réimporté.
        Utile pour : backup, duplication, migration entre workspaces,
        versioning de config agent.

        ⚠️ Ne fonctionne pas sur les agents archivés ou globaux (built-in).

        Args:
            agent_sid: L'identifiant sId de l'agent (trouvable via dust_agents_search)
        """
        client = DustClient()
        result = await client.get_raw(
            f"/assistant/agent_configurations/{agent_sid}/export/yaml",
            accept="text/yaml",
        )

        # get_raw retourne le texte brut (YAML) ou un dict erreur
        if isinstance(result, dict) and result.get("error"):
            return json.dumps(result, indent=2, ensure_ascii=False)

        return result

    @mcp.tool()
    async def dust_agents_import(config_json: str) -> str:
        """
        Créer un nouvel agent à partir d'une configuration JSON.

        Le body doit contenir TOUS les champs requis :
        - agent: {handle, description, scope, max_steps_per_run, visualization_enabled, avatar_url?}
        - instructions: string (le prompt complet de l'agent)
        - generation_settings: {model_id, provider_id, temperature, reasoning_effort?}
        - tags: [{name, kind}] (peut être vide [])
        - editors: [{email}] (au moins un éditeur requis)
        - toolset: [{name, description, type, configuration}] (peut être vide [])

        Valeurs possibles :
        - scope: "visible" | "hidden"
        - provider_id: "anthropic", "openai", "google_ai_studio", "mistral", "deepseek"
        - model_id: "claude-sonnet-4-6", "gpt-4o", "gemini-2.0-flash", etc.
        - tag kind: "standard" | "protected"
        - toolset type: "MCP"

        ⚠️ ATTENTION : crée réellement un agent dans le workspace.
        Toujours confirmer avec l'utilisateur avant d'appeler.

        Args:
            config_json: Configuration complète de l'agent au format JSON string.
                         Peut être obtenue via dust_agents_export_yaml puis convertie,
                         ou construite manuellement.

        Exemple minimal :
        {
            "agent": {
                "handle": "MonAgent",
                "description": "Un agent de test",
                "scope": "hidden",
                "max_steps_per_run": 10,
                "visualization_enabled": false,
                "avatar_url": "https://dust.tt/static/emojis/bg-blue-500/robot_face/1f916"
            },
            "instructions": "Tu es un assistant utile.",
            "generation_settings": {
                "model_id": "claude-sonnet-4-6",
                "provider_id": "anthropic",
                "temperature": 0.7
            },
            "tags": [],
            "editors": [{"email": "user@example.com"}],
            "toolset": []
        }
        """
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": True,
                "message": f"JSON invalide : {str(e)}",
                "hint": "Vérifiez le format JSON. Utilisez dust_agents_export_yaml pour obtenir un exemple de structure."
            }, indent=2, ensure_ascii=False)

        # Validation des champs requis
        required_fields = ["agent", "instructions", "generation_settings", "tags", "editors", "toolset"]
        missing = [f for f in required_fields if f not in config]
        if missing:
            return json.dumps({
                "error": True,
                "message": f"Champs requis manquants : {', '.join(missing)}",
                "required_fields": required_fields,
                "hint": "Tous les 6 champs sont obligatoires, même si vides (tags: [], toolset: [])."
            }, indent=2, ensure_ascii=False)

        # Validation de l'agent sub-object
        agent_required = ["handle", "description", "scope", "max_steps_per_run", "visualization_enabled"]
        agent_obj = config.get("agent", {})
        agent_missing = [f for f in agent_required if f not in agent_obj]
        if agent_missing:
            return json.dumps({
                "error": True,
                "message": f"Champs requis manquants dans 'agent' : {', '.join(agent_missing)}",
                "hint": "scope doit être 'visible' ou 'hidden'."
            }, indent=2, ensure_ascii=False)

        # Validation editors non vide
        if not config.get("editors") or len(config["editors"]) == 0:
            return json.dumps({
                "error": True,
                "message": "Au moins un éditeur est requis dans 'editors'.",
                "hint": "Format : [{\"email\": \"user@example.com\"}]"
            }, indent=2, ensure_ascii=False)

        client = DustClient()
        result = await client.post(
            "/assistant/agent_configurations/import",
            data=config,
        )

        if isinstance(result, dict) and result.get("error"):
            return json.dumps(result, indent=2, ensure_ascii=False)

        # Résultat : agentConfiguration + skippedActions
        output = {
            "success": True,
            "agentConfiguration": result.get("agentConfiguration", {}),
            "skippedActions": result.get("skippedActions", []),
        }

        # Résumé lisible
        agent_config = output["agentConfiguration"]
        if agent_config:
            output["summary"] = {
                "sId": agent_config.get("sId"),
                "name": agent_config.get("name"),
                "scope": agent_config.get("scope"),
                "status": agent_config.get("status"),
            }

        if output["skippedActions"]:
            output["warning"] = (
                f"{len(output['skippedActions'])} action(s) ignorée(s) lors de l'import. "
                "Vérifiez que les MCP servers et data sources référencés existent dans ce workspace."
            )

        return json.dumps(output, indent=2, ensure_ascii=False)
