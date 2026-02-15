"""dust_help — Guide l'agent sur les outils disponibles"""
import json


def register(mcp):
    @mcp.tool()
    async def dust_help(category: str = "all") -> str:
        """
        Affiche les outils disponibles dans ce MCP, groupés par catégorie.
        Appeler cet outil EN PREMIER pour savoir quel outil utiliser.

        Args:
            category: Catégorie à afficher. Valeurs: "all", "agents", "conversations",
                      "search", "spaces", "datasources", "documents", "dsviews", "tables", "apps", "files"
        """
        catalog = {
            "agents": {
                "description": "Gérer les agents Dust (configuration, recherche, mise à jour)",
                "tools": {
                    "dust_agents_search": "Chercher un agent par nom",
                    "dust_agents_get": "Récupérer la config complète d'un agent (modèle, instructions, actions)",
                    "dust_agents_update": "Modifier la configuration d'un agent (⚠️ vérifier les champs acceptés par l'API)",
                },
            },
            "conversations": {
                "description": "Créer et gérer des conversations avec les agents Dust",
                "notes": "Le context (username, timezone) est automatiquement injecté. Origin est toujours 'api'.",
                "tools": {
                    "dust_conv_create": "Créer une conversation + premier message (peut mentionner un agent)",
                    "dust_conv_get": "Récupérer une conversation complète avec tous ses messages",
                    "dust_conv_send_message": "Envoyer un message dans une conversation existante",
                    "dust_conv_get_events": "Récupérer les events SSE d'une conversation (réponse agent)",
                    "dust_conv_edit_message": "Éditer un message déjà envoyé",
                    "dust_conv_cancel": "Annuler la génération en cours d'un agent",
                    "dust_conv_add_content": "Injecter un content fragment (fichier, contexte additionnel)",
                },
            },
            "search": {
                "description": "Recherche sémantique dans le workspace",
                "tools": {
                    "dust_search_nodes": "Rechercher des documents/nodes (query min 3 chars, viewType: all/document/table)",
                },
            },
            "spaces": {
                "description": "Découvrir les spaces du workspace",
                "notes": "Utiliser dust_list_spaces EN PREMIER pour obtenir les space_ids nécessaires aux autres outils.",
                "tools": {
                    "dust_list_spaces": "Lister tous les spaces disponibles et leurs IDs",
                },
            },
            "datasources": {
                "description": "Explorer les data sources du workspace",
                "tools": {
                    "dust_data_list": "Lister les data sources d'un space",
                    "dust_data_search": "Rechercher dans une data source spécifique",
                },
            },
            "documents": {
                "description": "CRUD sur les documents dans les data sources",
                "notes": "Body en snake_case (mime_type, source_url, light_document_output). parents peut être rejeté si API key non-système.",
                "tools": {
                    "dust_docs_list": "Lister les documents d'une data source",
                    "dust_docs_get": "Récupérer un document spécifique",
                    "dust_docs_upsert": "Créer ou mettre à jour un document",
                    "dust_docs_delete": "Supprimer un document",
                    "dust_docs_update_parents": "Modifier la hiérarchie parent d'un document",
                },
            },
            "dsviews": {
                "description": "Data Source Views — vues filtrées sur les data sources",
                "tools": {
                    "dust_dsv_list": "Lister les data source views d'un space",
                    "dust_dsv_search": "Recherche sémantique dans une data source view",
                },
            },
            "tables": {
                "description": "CRUD complet sur les tables et rows",
                "tools": {
                    "dust_tables_list": "Lister les tables d'une data source",
                    "dust_tables_get": "Récupérer les détails d'une table",
                    "dust_tables_upsert": "Créer ou modifier une table",
                    "dust_tables_delete": "Supprimer une table",
                    "dust_tables_list_rows": "Lister les rows d'une table",
                    "dust_tables_upsert_rows": "Insérer ou mettre à jour des rows (validation row_id + value)",
                    "dust_tables_get_row": "Récupérer une row spécifique",
                    "dust_tables_delete_row": "Supprimer une row",
                },
            },
            "apps": {
                "description": "Dust Apps — lister et exécuter des apps",
                "tools": {
                    "dust_apps_list": "Lister les apps d'un space",
                    "dust_apps_run": "Lancer l'exécution d'une app",
                    "dust_apps_get_run": "Récupérer le résultat d'un run",
                },
            },
            "files": {
                "description": "Upload de fichiers",
                "tools": {
                    "dust_files_upload": "Créer une URL d'upload pour un fichier",
                },
            },
        }

        if category != "all" and category in catalog:
            result = {category: catalog[category]}
        else:
            result = catalog

        return json.dumps(result, indent=2, ensure_ascii=False)