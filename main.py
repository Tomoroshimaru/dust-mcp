"""
Dust MCP Server — Full API
Serveur MCP exposant l'API Dust complète via FastMCP.
"""
import os
import logging
from fastmcp import FastMCP
from starlette.types import ASGIApp, Receive, Scope, Send

from config import Config

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Validate config
Config.validate()

# Initialize MCP server
mcp = FastMCP("Dust MCP")

# === Register all tools ===
from tools.agents import register as register_agents
from tools.conversations import register as register_conversations
from tools.search import register as register_search
from tools.spaces import register as register_spaces
from tools.datasources import register as register_datasources
from tools.documents import register as register_documents
from tools.tables import register as register_tables
from tools.files import register as register_files
from tools.usage import register as register_usage

register_agents(mcp)
register_conversations(mcp)
register_search(mcp)
register_spaces(mcp)
register_datasources(mcp)
register_documents(mcp)
register_tables(mcp)
register_files(mcp)
register_usage(mcp)

logger.info("✅ All tools registered")


# === NoHostCheckWrapper (bypass TrustedHostMiddleware derrière proxy) ===
class NoHostCheckWrapper:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = []
            for name, value in scope.get("headers", []):
                if name.lower() == b"host":
                    headers.append((name, b"localhost:8080"))
                else:
                    headers.append((name, value))
            scope["headers"] = headers
        await self.app(scope, receive, send)


# === Main ===
if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", "8000"))

    app = mcp.http_app()
    final_app = NoHostCheckWrapper(app)

    logger.info("=" * 60)
    logger.info("🚀 Dust MCP Server")
    logger.info(f"📍 http://0.0.0.0:{PORT}")
    logger.info("=" * 60)

    uvicorn.run(final_app, host="0.0.0.0", port=PORT)