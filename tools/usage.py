"""Usage & Analytics — Export des métriques du workspace Dust"""
import json
from typing import Optional
from client import DustClient


def register(mcp):

    @mcp.tool()
    async def dust_analytics_export(
        table: str,
        start_date: str,
        end_date: str,
        timezone: str = "Europe/Paris",
    ) -> str:
        """
        Exporter les données analytics du workspace au format CSV.

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
        """
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

        # Validation basique du format date
        import re
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not date_pattern.match(start_date):
            return json.dumps({
                "error": True,
                "message": f"Format de date invalide pour start_date : '{start_date}'",
                "hint": "Format attendu : YYYY-MM-DD (ex: 2026-01-01)"
            }, indent=2, ensure_ascii=False)
        if not date_pattern.match(end_date):
            return json.dumps({
                "error": True,
                "message": f"Format de date invalide pour end_date : '{end_date}'",
                "hint": "Format attendu : YYYY-MM-DD (ex: 2026-03-31)"
            }, indent=2, ensure_ascii=False)

        client = DustClient()

        params = {
            "table": table,
            "startDate": start_date,
            "endDate": end_date,
        }
        if timezone:
            params["timezone"] = timezone

        result = await client.get_raw(
            "/analytics/export",
            params=params,
            accept="text/csv",
        )

        # get_raw retourne le texte brut (CSV) ou un dict erreur
        if isinstance(result, dict) and result.get("error"):
            # Gestion spécifique du 403 (accès non activé)
            status = result.get("status_code", 0)
            if status == 403:
                result["hint"] = (
                    "L'accès à l'API analytics nécessite un rôle 'builder' minimum "
                    "sur l'API key. Vérifiez les permissions de votre clé API dans "
                    "Admin > API Keys."
                )
            return json.dumps(result, indent=2, ensure_ascii=False)

        # Le résultat est du CSV brut
        # Ajouter un header informatif
        lines = result.strip().split("\n") if isinstance(result, str) else []
        row_count = max(0, len(lines) - 1)  # -1 pour le header CSV

        header = (
            f"📊 Analytics Export — {table}\n"
            f"📅 Période : {start_date} → {end_date}\n"
            f"🕐 Timezone : {timezone}\n"
            f"📝 {row_count} ligne(s) de données\n"
            f"{'=' * 50}\n\n"
        )

        return header + result
