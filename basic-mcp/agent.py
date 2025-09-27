import os
import logging
from pathlib import Path
from dotenv import load_dotenv
# from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool, ChatChunk
from livekit.agents.voice import Agent, AgentSession
# from livekit.plugins import deepgram, openai, silero
from livekit.agents import JobContext, WorkerOptions, cli, Agent, AgentSession
from livekit.plugins import deepgram, openai, silero, bithuman
from livekit.api.access_token import AccessToken, VideoGrants

from mcp_client import MCPServerSse
from mcp_client.agent_tools import MCPToolsIntegration

load_dotenv()

# Manual JWT workaround: Lösung für Pickle-Probleme (Python 3.13)
def generate_livekit_jwt(room: str, identity: str, name: str | None = None) -> str:
    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError("LIVEKIT_API_KEY/LIVEKIT_API_SECRET nicht gesetzt")

    token = AccessToken(api_key=api_key, api_secret=api_secret)
    token.with_identity(identity)
    if name:
        token.with_name(name)
    token.with_grants(VideoGrants(
        room=room,
        room_join=True,
        can_publish=True,
        can_subscribe=True,
    ))
    return token.to_jwt()

class FunctionAgent(Agent):
    """A LiveKit agent that uses MCP tools from one or more MCP servers."""

    def __init__(self):
        super().__init__(
            instructions=
    """You are a friendly customer service representative for GymFit Apparel. You help customers find products and answer questions about policies.

    **CRITICAL: You can ONLY answer questions using the available tools. NEVER make up information or use embedded knowledge.**

    **Available Tools:**
    - **shopify_find_products_by_title_or_handle**: Use this to search for products in our store
    - **add_tools**: Use this to add new tools if needed
    - **edit_tools**: Use this to modify existing tools if needed

    **MCP Server Integration:**
    You have access to a Zapier MCP server that can search for products in our online store. When customers ask about specific products, use this tool to find real-time information.

    **Product Search Flow:**
    1. Customer asks: "Do you have blue t-shirts?" or "Find me workout leggings"
    2. You respond: "One moment while I check our online shop."
    3. Use the shopify_find_products_by_title_or_handle tool to search for products
    4. Present results: "We have [Product Name] for $[Price]. [Description if available]."

    **Customer Service Guidelines:**
    - Speak warmly and professionally
    - Use natural, conversational language
    - Always prioritize customer satisfaction
    - Keep responses concise and factual
    - NEVER provide store links - customers are already on your site
    - **PRONUNCIATION**: Always say "Jim-Fit" (not "Jyme-Fit") when referring to the brand

    **IMPORTANT RULES:**
    - If a customer asks about policies (shipping, returns, etc.), tell them you don't have access to that information and suggest they contact customer support
    - If a customer asks about products, use the shopify tool to search
    - NEVER make up information about policies, shipping times, or company details
    - If you don't have a tool to answer a question, be honest and say you don't know

    **Example Responses:**
    - "What's your return policy?" → "I don't have access to our return policy information. Please contact our customer support team for details."
    - "Do you have blue hats?" → "One moment while I check our online shop." [use tool]
    - "How long does shipping take?" → "I don't have access to our shipping information. Please contact customer support for details." """,

            stt=deepgram.STT(),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=openai.TTS(voice="alloy", model="tts-1"),
            vad=silero.VAD.load(),
            allow_interruptions=True
        )

    async def llm_node(self, chat_ctx, tools, model_settings):
        """Override the llm_node to handle tool calls."""

        # Get the original response from the parent class
        async for chunk in super().llm_node(chat_ctx, tools, model_settings):


            yield chunk

async def entrypoint(ctx: JobContext):
    """Main entrypoint for the LiveKit agent application."""
    mcp_server = MCPServerSse(
        params={"url": os.environ.get("ZAPIER_MCP_URL")},
        cache_tools_list=True,
        name="SSE MCP Server"
    )

    from PIL import Image
    from livekit.plugins import bithuman

    avatar = bithuman.AvatarSession(
        avatar_image=Image.open(os.path.join(os.path.dirname(__file__), "assets", "hans_avatar.jpeg")),
    )
    # avatar = bithuman.AvatarSession(
    #     model_path="/Users/jimmybradford/Downloads/hacker.imx", # This example uses a demo model installed in the current directory
    # )

    agent = await MCPToolsIntegration.create_agent_with_tools(
        agent_class=FunctionAgent,
        mcp_servers=[mcp_server]
    )

    await ctx.connect()

    session = AgentSession()

    # Manual JWT workaround: Erzeuge JWT und übergebe es an avatar.start()
    try:
        try:
            room_name = ctx.room.name if hasattr(ctx.room, 'name') else str(ctx.room)
        except Exception:
            room_name = os.environ.get("DEV_ROOM", "quickstart-room")
        
        manual_jwt = generate_livekit_jwt(room_name, "bithuman-avatar", "BitHuman Avatar Agent")
        print("🔑 Manual JWT workaround aktiv - umgeht Python 3.13 Pickle-Fehler")
        
        # Übergabe des manuellen JWT an avatar.start()
        await avatar.start(session, room=ctx.room, token=manual_jwt)
    except Exception as e:
        print(f"⚠️ Manual JWT workaround fehlgeschlagen: {e}")
        print("🔄 Fallback: Avatar-Start ohne JWT...")
        try:
            await avatar.start(session, room=ctx.room)
        except Exception as e2:
            print(f"❌ Avatar-Start komplett fehlgeschlagen: {e2}")
    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
