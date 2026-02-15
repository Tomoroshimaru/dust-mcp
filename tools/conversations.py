"""Conversations — Créer, lire, envoyer des messages, gérer les conversations"""
import json
from typing import Optional
from client import DustClient
from config import Config


def _build_message_context(
    username: Optional[str] = None,
    timezone: Optional[str] = None,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
) -> dict:
    """Construit le context requis par l'API Dust."""
    return {
        "username": username or Config.DEFAULT_USERNAME,
        "timezone": timezone or Config.DEFAULT_TIMEZONE,
        "origin": "api",
        **({"fullName": full_name} if full_name else {}),
        **({"email": email} if email else {}),
    }


def register(mcp):

    @mcp.tool()
    async def dust_conv_create(
        message_content: str,
        agent_sid: Optional[str] = None,
        title: Optional[str] = None,
        blocking: bool = True,
        username: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> str:
        """
        Créer une nouvelle conversation et envoyer le premier message.
        Si agent_sid est fourni, l'agent sera mentionné et répondra.

        ⚠️ Si blocking=True ET qu'un agent est mentionné, la requête attend la réponse
        de l'agent (peut prendre 30-120s). Consomme des crédits AI.

        Args:
            message_content: Le contenu du premier message
            agent_sid: sId de l'agent à mentionner (optionnel). Trouvable via dust_agents_search.
            title: Titre de la conversation (optionnel)
            blocking: Si True, attend la réponse de l'agent. Si False, retourne immédiatement
                      l'ID de conversation (utiliser dust_conv_get_events pour récupérer la réponse).
            username: Username de l'expéditeur (optionnel, default: config)
            timezone: Timezone de l'expéditeur (optionnel, default: config)
        """
        client = DustClient()

        message = {
            "content": message_content,
            "mentions": [{"configurationId": agent_sid}] if agent_sid else [],
            "context": _build_message_context(username=username, timezone=timezone),
        }

        body = {"message": message, "blocking": blocking}
        if title:
            body["title"] = title

        result = await client.post(
            "/assistant/conversations",
            data=body,
            timeout=180.0 if blocking else 30.0,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_conv_get(conversation_id: str) -> str:
        """
        Récupérer une conversation complète avec tous ses messages,
        actions, métadonnées et configuration des agents impliqués.

        Args:
            conversation_id: L'identifiant sId de la conversation
        """
        client = DustClient()
        result = await client.get(f"/assistant/conversations/{conversation_id}")
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_conv_send_message(
        conversation_id: str,
        message_content: str,
        agent_sid: Optional[str] = None,
        blocking: bool = True,
        username: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> str:
        """
        Envoyer un message dans une conversation existante.

        ⚠️ Si un agent est mentionné et blocking=True, attend la réponse (consomme des crédits AI).

        Args:
            conversation_id: sId de la conversation
            message_content: Contenu du message à envoyer
            agent_sid: sId de l'agent à mentionner (optionnel)
            blocking: Si True, attend la réponse de l'agent
            username: Username de l'expéditeur (optionnel, default: config)
            timezone: Timezone de l'expéditeur (optionnel, default: config)
        """
        client = DustClient()

        message = {
            "content": message_content,
            "mentions": [{"configurationId": agent_sid}] if agent_sid else [],
            "context": _build_message_context(username=username, timezone=timezone),
        }

        body = {"message": message, "blocking": blocking}

        result = await client.post(
            f"/assistant/conversations/{conversation_id}/messages",
            data=body,
            timeout=180.0 if blocking else 30.0,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_conv_get_events(conversation_id: str) -> str:
        """
        Récupérer les events d'une conversation (réponses agent, actions, tokens).
        Utile après un appel non-blocking pour récupérer la réponse.

        Args:
            conversation_id: sId de la conversation
        """
        client = DustClient()
        result = await client.get(
            f"/assistant/conversations/{conversation_id}/events",
            timeout=180.0,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_conv_edit_message(
        conversation_id: str,
        message_id: str,
        new_content: str,
    ) -> str:
        """
        Éditer un message déjà envoyé dans une conversation.

        Args:
            conversation_id: sId de la conversation
            message_id: sId du message à éditer
            new_content: Nouveau contenu du message
        """
        client = DustClient()
        result = await client.post(
            f"/assistant/conversations/{conversation_id}/messages/{message_id}/edit",
            data={"content": new_content},
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_conv_cancel(conversation_id: str) -> str:
        """
        Annuler la génération en cours d'un agent dans une conversation.
        Utile si l'agent prend trop de temps ou part dans une mauvaise direction.

        Args:
            conversation_id: sId de la conversation
        """
        client = DustClient()
        result = await client.post(
            f"/assistant/conversations/{conversation_id}/cancel"
        )
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def dust_conv_add_content(
        conversation_id: str,
        title: str,
        content: str,
        content_type: str = "text/plain",
        url: Optional[str] = None,
        username: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> str:
        """
        Injecter un content fragment dans une conversation.
        Permet d'ajouter du contexte (fichier, données, texte) que l'agent pourra utiliser.

        Args:
            conversation_id: sId de la conversation
            title: Titre du fragment de contenu
            content: Le contenu textuel à injecter
            content_type: Type MIME (default: text/plain). Autres: text/markdown, application/json
            url: URL source optionnelle
            username: Username de l'expéditeur (optionnel, default: config)
            timezone: Timezone de l'expéditeur (optionnel, default: config)
        """
        client = DustClient()
        body = {
            "title": title,
            "content": content,
            "contentType": content_type,
            "context": _build_message_context(username=username, timezone=timezone),
        }
        if url:
            body["url"] = url

        result = await client.post(
            f"/assistant/conversations/{conversation_id}/content_fragments",
            data=body,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)