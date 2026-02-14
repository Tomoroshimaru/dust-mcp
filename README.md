# Dust MCP Server

Serveur MCP (Model Context Protocol) exposant l'API Dust complète. Permet à un agent Dust d'interagir programmatiquement avec son propre workspace : agents, conversations, documents, tables, search, apps.

## Architecture

```
dust_mcp/
├── config.py              # Variables d'environnement, URLs API
├── client.py              # Client HTTP async (httpx) pour l'API Dust
├── main.py                # Serveur FastMCP + wiring
├── tools/
│   ├── helper.py          # dust_help — catalogue des outils
│   ├── agents.py          # Recherche, détails, mise à jour d'agents
│   ├── conversations.py   # Créer, lire, envoyer des messages
│   ├── search.py          # Recherche sémantique workspace
│   ├── datasources.py     # Lister et chercher dans les data sources
│   ├── documents.py       # CRUD documents
│   ├── dsviews.py         # Data Source Views
│   ├── tables.py          # CRUD tables et rows
│   ├── apps.py            # Lister et exécuter des Dust Apps
│   └── files.py           # Upload de fichiers
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Tools disponibles (33)

| Domaine | Tools | Type |
|---------|-------|------|
| **Help** | `dust_help` | Guide l'agent vers le bon outil |
| **Agents** | `dust_agents_search`, `dust_agents_get`, `dust_agents_update` | Read + Write |
| **Conversations** | `dust_conv_create`, `dust_conv_get`, `dust_conv_send_message`, `dust_conv_get_events`, `dust_conv_edit_message`, `dust_conv_cancel`, `dust_conv_add_content` | Read + Write |
| **Search** | `dust_search_nodes` | Read |
| **DataSources** | `dust_data_list`, `dust_data_search` | Read |
| **Documents** | `dust_docs_list`, `dust_docs_get`, `dust_docs_upsert`, `dust_docs_delete`, `dust_docs_update_parents` | Read + Write + Delete |
| **DSViews** | `dust_dsv_list`, `dust_dsv_search` | Read |
| **Tables** | `dust_tables_list`, `dust_tables_get`, `dust_tables_upsert`, `dust_tables_delete`, `dust_tables_list_rows`, `dust_tables_upsert_rows`, `dust_tables_get_row`, `dust_tables_delete_row` | Read + Write + Delete |
| **Apps** | `dust_apps_list`, `dust_apps_run`, `dust_apps_get_run` | Read + Write |
| **Files** | `dust_files_upload` | Write |

## Authentification

Ce MCP utilise une **API Key Dust** (workspace-level). Pas d'OAuth — la clé est stockée en variable d'environnement et donne accès au workspace entier avec les permissions associées à la clé.

Endpoints qui **consomment des crédits AI** : uniquement ceux qui déclenchent une réponse d'agent (`dust_conv_create` et `dust_conv_send_message` avec un `agent_sid`). Tous les autres endpoints (CRUD data, search, agents config) sont gratuits hors rate limits.

### Rate limits API Dust

| Domaine | Limite |
|---------|--------|
| Conversations (messages) | `100 × nb users` /jour, `10 × nb users` /min |
| DataSources (upserts) | `120 upserts` /min |
| Apps (runs) | `10 000` /jour/app |

## Setup

### Prérequis

- Python 3.11+
- Une API Key Dust (Settings > API Keys dans le workspace)

### Installation locale

```bash
# Cloner le repo
git clone <repo-url>
cd dust-mcp-2.0

# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer
cp .env.example .env
# Éditer .env avec ta clé API et ton workspace ID

# Lancer
python main.py
```

### Docker

```bash
docker build -t dust-mcp .
docker run -p 8000:8000 --env-file .env dust-mcp
```

### Variables d'environnement

| Variable | Obligatoire | Description |
|----------|-------------|-------------|
| `DUST_API_KEY` | ✅ | Clé API Dust (commence par `sk-`) |
| `DUST_WORKSPACE_ID` | ✅ | ID du workspace (visible dans l'URL Dust) |
| `PORT` | Non | Port du serveur (default: `8000`) |
| `HOST` | Non | Host du serveur (default: `0.0.0.0`) |


## Stack

- **FastMCP** — Framework MCP Python
- **httpx** — Client HTTP async
- **uvicorn** — Serveur ASGI
- **python-dotenv** — Gestion des variables d'environnement