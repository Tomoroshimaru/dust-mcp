"""Usage & Analytics — Export des métriques du workspace Dust"""
import json
import re
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_analytics_export(
        table: str,
        start_date: str,
        end_date: str,
        timezone: str = "Europe/Paris",
        format: str = "json",
    ) -> str:
        """
        Exporter les données analytics du workspace (CSV ou JSON).

        Endpoint : GET /analytics/export (remplace /workspace-usage, deprecated juin 2026).
        Requiert un rôle builder minimum sur l'API key.

        Tables disponibles :
        - "usage_metrics"  : Messages, conversations et utilisateurs actifs sur la période
        - "active_users"   : Compteurs DAU, WAU, MAU jour par jour
        - "source"         : Volume de messages par source (web, slack, extension, API)
        - "agents"         : Top agents par nombre de messages
        - "users"          : Top utilisateurs par nombre de messages
        - "skill_usage"    : Exécutions de skills et utilisateurs uniques
        - "tool_usage"     : Exécutions d'outils et utilisateurs uniques
        - "messages"       : Logs détaillés message par message

        Args:
            table: Nom de la table analytics à exporter.
                   Valeurs possibles : usage_metrics, active_users, source,
                   agents, users, skill_usage, tool_usage, messages
            start_date: Date de début au format YYYY-MM-DD (ex: "2026-01-01")
            end_date: Date de fin au format YYYY-MM-DD (ex: "2026-03-31")
            timezone: Fuseau horaire IANA (défaut: "Europe/Paris").
                      Exemples : "UTC", "America/New_York", "Asia/Tokyo"
            format: Format de sortie — "json" (défaut) ou "csv".
                    JSON retourne un tableau d'objets, CSV retourne du texte brut.
        """
        # --- Validations ---
        valid_tables = [
            "usage_metrics", "active_users", "source", "agents",
            "users", "skill_usage", "tool_usage", "messages"
        ]
        if table not in valid_tables:
            return json.dumps({
                "error": True,
                "message": f"Table invalide : '{table}'",
                "valid_tables": valid_tables,
                "hint": "Choisissez une table parmi les valeurs ci-dessus."
            }, indent=2, ensure_ascii=False)

        if format not in ("json", "csv"):
            return json.dumps({
                "error": True,
                "message": f"Format invalide : '{format}'",
                "valid_formats": ["json", "csv"],
                "hint": "Choisissez 'json' ou 'csv'."
            }, indent=2, ensure_ascii=False)

        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for label, value in [("start_date", start_date), ("end_date", end_date)]:
            if not date_pattern.match(value):
                return json.dumps({
                    "error": True,
                    "message": f"Format de date invalide pour {label} : '{value}'",
                    "hint": "Format attendu : YYYY-MM-DD (ex: 2026-01-01)"
                }, indent=2, ensure_ascii=False)

        # --- Paramètres communs ---
        client = DustClient()
        params = {
            "table": table,
            "startDate": start_date,
            "endDate": end_date,
            "format": format,
        }
        if timezone:
            params["timezone"] = timezone

        # --- Branchement selon le format ---
        if format == "json":
            # JSON → client.get() retourne un dict/list déjà parsé
            result = await client.get(
                "/analytics/export",
                params=params,
            )

            if isinstance(result, dict) and result.get("error"):
                if result.get("status_code") == 403:
                    result["hint"] = (
                        "L'accès à l'API analytics nécessite un rôle 'builder' minimum "
                        "sur l'API key. Vérifiez les permissions dans Admin > API Keys."
                    )
                return json.dumps(result, indent=2, ensure_ascii=False)

            row_count = len(result) if isinstance(result, list) else "N/A"
            header = (
                f"Analytics Export — {table}\n"
                f"Période : {start_date} → {end_date}\n"
                f"Timezone : {timezone}\n"
                f"{row_count} ligne(s) de données\n"
                f"Format : JSON\n"
                f"{'=' * 50}\n\n"
            )
            return header + json.dumps(result, indent=2, ensure_ascii=False)

        else:
            # CSV → client.get_raw() retourne du texte brut
            result = await client.get_raw(
                "/analytics/export",
                params=params,
                accept="text/csv",
            )

            if isinstance(result, dict) and result.get("error"):
                if result.get("status_code") == 403:
                    result["hint"] = (
                        "L'accès à l'API analytics nécessite un rôle 'builder' minimum "
                        "sur l'API key. Vérifiez les permissions dans Admin > API Keys."
                    )
                return json.dumps(result, indent=2, ensure_ascii=False)

            lines = result.strip().split("\n") if isinstance(result, str) else []
            row_count = max(0, len(lines) - 1)

            header = (
                f"Analytics Export — {table}\n"
                f"Période : {start_date} → {end_date}\n"
                f"Timezone : {timezone}\n"
                f"{row_count} ligne(s) de données\n"
                f"Format : CSV\n"
                f"{'=' * 50}\n\n"
            )
            return header + result
