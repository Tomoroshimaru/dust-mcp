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
                      "search", "spaces", "datasources", "documents", "tables", "files"
        """
        catalog = {
            "agents": {
                "description": "Consulter les agents Dust (configuration, recherche)",
                "tools": {
                    "dust_agents_search": "Chercher un agent par nom → retourne sId + description",
                    "dust_agents_get": "Récupérer la config complète d'un agent (modèle, instructions, actions, skills)",
                    "dust_agents_update": "Modifier la configuration d'un agent (⚠️ écriture — vérifier les champs acceptés)",
                },
            },
            "conversations": {
                "description": "Créer et gérer des conversations avec les agents Dust",
                "notes": (
                    "Le context (username, timezone) est automatiquement injecté. "
                    "Origin est toujours 'api'. "
                    "send_message utilise du polling pour le mode blocking (pas de SSE)."
                ),
                "tools": {
                    "dust_conv_create": "Créer une conversation + premier message (blocking natif côté API)",
                    "dust_conv_get": "Récupérer une conversation complète avec tous ses messages et actions",
                    "dust_conv_send_message": "Envoyer un message dans une conversation existante (blocking via polling)",
                    "dust_conv_edit_message": "Éditer un message déjà envoyé dans une conversation",
                    "dust_conv_cancel": "Annuler la génération en cours d'un agent",
                    "dust_conv_add_content": "Injecter un content fragment (fichier, texte, contexte additionnel)",
                    "dust_conv_get_feedbacks": "Récupérer tous les feedbacks (thumbs up/down) d'une conversation",
                    "dust_conv_submit_feedback": "Soumettre un feedback sur un message agent (up/down + commentaire)",
                    "dust_conv_delete_feedback": "Supprimer un feedback sur un message",
                },
            },
            "search": {
                "description": "Recherche sémantique dans le workspace",
                "notes": (
                    "Si space_ids n'est pas fourni, la recherche s'effectue automatiquement "
                    "sur tous les spaces du workspace (fallback auto)."
                ),
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
                    "dust_data_search": "Recherche sémantique dans une data source spécifique",
                },
            },
            "documents": {
                "description": "CRUD sur les documents dans les data sources",
                "notes": (
                    "Body en snake_case (mime_type, source_url, light_document_output). "
                    "update_parents peut être rejeté si API key non-système."
                ),
                "tools": {
                    "dust_docs_list": "Lister les documents d'une data source (avec pagination limit/offset)",
                    "dust_docs_get": "Récupérer un document spécifique avec son contenu complet",
                    "dust_docs_upsert": "Créer ou mettre à jour un document (⚠️ écrase si document_id existe)",
                    "dust_docs_delete": "Supprimer un document (⚠️ irréversible)",
                    "dust_docs_update_parents": "Modifier la hiérarchie parent d'un document",
                },
            },
            "tables": {
                "description": "CRUD complet sur les tables et rows",
                "notes": (
                    "tables_upsert utilise 'title' (le champ 'name' est deprecated). "
                    "upsert_rows requiert un JSON array avec 'row_id' et 'value' par row."
                ),
                "tools": {
                    "dust_tables_list": "Lister les tables d'une data source",
                    "dust_tables_get": "Récupérer les détails d'une table (schéma, colonnes, metadata)",
                    "dust_tables_upsert": "Créer ou modifier une table (title, description, tags, timestamp)",
                    "dust_tables_delete": "Supprimer une table et toutes ses rows (⚠️ irréversible)",
                    "dust_tables_list_rows": "Lister les rows d'une table (pagination: limit/offset)",
                    "dust_tables_upsert_rows": "Insérer ou modifier des rows (truncate=True pour vider avant)",
                    "dust_tables_get_row": "Récupérer une row spécifique par row_id",
                    "dust_tables_delete_row": "Supprimer une row (⚠️ irréversible)",
                },
            },
            "files": {
                "description": "Upload de fichiers vers Dust",
                "tools": {
                    "dust_files_upload": "Créer une URL d'upload pré-signée pour un fichier",
                },
            },
        }

        if category != "all" and category in catalog:
            result = {category: catalog[category]}
        elif category == "all":
            result = catalog
        else:
            result = {
                "error": f"Catégorie '{category}' inconnue.",
                "categories_disponibles": list(catalog.keys()),
            }

        return json.dumps(result, indent=2, ensure_ascii=False)