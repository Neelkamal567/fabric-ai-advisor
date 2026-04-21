"""
Chat Service — Google Gemini API integration for conversational AI.
Falls back to template-based responses if API key is unavailable.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Try to import Gemini SDK
gemini_available = False
genai = None

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai_module
        genai = genai_module
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_available = True
        print("✅ Gemini API configured successfully")
    except ImportError:
        print("⚠️ google-generativeai package not installed. Using fallback mode.")
    except Exception as e:
        print(f"⚠️ Gemini API configuration failed: {e}. Using fallback mode.")
else:
    print("⚠️ GEMINI_API_KEY not set. Chatbot will use fallback mode.")


SYSTEM_PROMPT = """You are an expert textile and fabric advisor. Your role is to recommend fabrics and materials based on:
- Weather conditions (summer, winter, rainy, humid, autumn)
- Festivals and occasions (weddings, Diwali, Eid, office events, etc.)
- Purpose and usage (daily wear, sports, formal, travel, etc.)

When recommending fabrics, always explain:
1. WHY the fabric is suitable for the given conditions
2. Key properties: comfort, breathability, durability, sustainability
3. Cost considerations
4. Care instructions when relevant
5. Cultural significance for festival-specific recommendations

Be conversational, helpful, and provide clear reasoning. Use Indian and global context.
When the user provides specific requirements, give your top 3 fabric recommendations with detailed explanations.

If recommendation data is provided in the context, incorporate it into your response naturally."""


class ChatService:
    """Handles chat interactions using Gemini API or fallback templates."""

    def __init__(self):
        self.model = None
        if gemini_available and genai:
            try:
                self.model = genai.GenerativeModel(
                    model_name="gemini-flash-latest",
                    system_instruction=SYSTEM_PROMPT,
                )
                print("✅ Gemini model initialized (gemini-flash-latest)")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini model: {e}")

    async def chat(self, message: str, history: list = None, recommendation_context: str = "", ui_context: dict = None):
        """
        Process a chat message and return a response.

        Args:
            message: User's message
            history: Conversation history [{"role": "user"/"assistant", "content": "..."}]
            recommendation_context: Optional ML recommendation data to include
            ui_context: Active UI state (dropdowns, history)

        Returns:
            dict with 'reply' and 'history'
        """
        if history is None:
            history = []
        if ui_context is None:
            ui_context = {}

        if self.model and gemini_available:
            return await self._gemini_chat(message, history, recommendation_context, ui_context)
        else:
            return self._fallback_chat(message, history, recommendation_context)

    async def _gemini_chat(self, message: str, history: list, context: str, ui_context: dict):
        """Chat using Gemini API."""
        try:
            # Build conversation history for Gemini
            gemini_history = []
            for h in history[-10:]:  # Keep last 10 messages for context
                role = "user" if h.get("role") == "user" else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [{"text": h.get("content", "")}]
                })

            # Enrich message with UI context
            enriched_message = message
            ui_state = ""
            if ui_context:
                w = ui_context.get("weather", "Not selected")
                f = ui_context.get("festival", "Not selected")
                p = ui_context.get("purpose", "Not selected")
                ui_state = f"[Current UI Selections: Weather={w}, Occasion={f}, Purpose={p}]"

            if context or ui_state:
                enriched_message = (
                    f"{message}\n\n"
                    f"{ui_state}\n"
                    f"[Context from recommendation engine: {context}]\n\n"
                    f"Please factor in these UI selections and engine context in your answer if relevant. "
                    f"Also, ALWAYS finish your response with a 'You may also like:' section suggesting 2 alternative trending fabrics."
                )

            chat = self.model.start_chat(history=gemini_history)
            response = chat.send_message(enriched_message)

            reply = response.text

            # Update history
            new_history = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply},
            ]

            return {"reply": reply, "history": new_history}

        except Exception as e:
            print(f"⚠️ Gemini API error: {e}")
            return self._fallback_chat(message, history, context)

    def _fallback_chat(self, message: str, history: list, context: str):
        """Generate template-based responses when Gemini is unavailable."""
        message_lower = message.lower()

        # Parse intent from message
        reply = ""

        if any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
            reply = (
                "👋 Hello! I'm your AI Fabric & Material Advisor. I can help you choose "
                "the perfect fabric based on:\n\n"
                "🌤️ **Weather** — summer, winter, rainy, humid, autumn\n"
                "🎉 **Festival/Occasion** — wedding, Diwali, office, party, etc.\n"
                "🎯 **Purpose** — daily wear, sports, formal, travel, etc.\n\n"
                "Just tell me what you need! For example:\n"
                "*\"What fabric should I wear for a summer wedding?\"*\n"
                "*\"Suggest something comfortable for office in humid weather\"*"
            )

        elif any(word in message_lower for word in ["summer", "hot", "heat"]):
            reply = (
                "☀️ For **summer** weather, I recommend:\n\n"
                "1. **Cotton** — Excellent breathability (9/10), very comfortable, affordable\n"
                "2. **Linen** — Maximum breathability (10/10), lightweight, eco-friendly\n"
                "3. **Bamboo** — Great moisture-wicking, sustainable, soft on skin\n\n"
                "💡 Avoid wool, velvet, and fleece in summer — they trap heat!"
            )

        elif any(word in message_lower for word in ["winter", "cold", "cool"]):
            reply = (
                "❄️ For **winter** weather, I recommend:\n\n"
                "1. **Wool** — Excellent warmth, durable (8/10), naturally insulating\n"
                "2. **Cashmere** — Premium comfort (10/10), luxuriously soft\n"
                "3. **Fleece** — Affordable warmth, moisture-wicking, lightweight\n\n"
                "💡 Layer with cotton underneath for maximum comfort!"
            )

        elif any(word in message_lower for word in ["rain", "monsoon", "wet"]):
            reply = (
                "🌧️ For **rainy/monsoon** weather, I recommend:\n\n"
                "1. **Polyester** — Water-resistant, quick-drying, very durable (9/10)\n"
                "2. **Nylon** — Lightweight, water-repellent, durable (9/10)\n"
                "3. **Denim** — Sturdy, handles moisture well, versatile\n\n"
                "💡 Avoid silk, velvet, and cashmere — they get damaged by water!"
            )

        elif any(word in message_lower for word in ["wedding", "marry", "bridal"]):
            reply = (
                "💍 For a **wedding**, I recommend:\n\n"
                "1. **Silk** — Classic elegance, beautiful drape, cultural significance\n"
                "2. **Velvet** — Rich, luxurious texture, perfect for evening ceremonies\n"
                "3. **Brocade** — Traditional opulence, intricate patterns, premium feel\n\n"
                "💡 Consider the season too — Silk works year-round, "
                "Velvet is better for winter weddings!"
            )

        elif any(word in message_lower for word in ["office", "work", "professional", "formal"]):
            reply = (
                "💼 For **office/formal** wear, I recommend:\n\n"
                "1. **Cotton** — All-day comfort (9/10), breathable, easy to maintain\n"
                "2. **Linen** — Premium professional look, excellent breathability\n"
                "3. **Polyester blend** — Wrinkle-resistant, durable, affordable\n\n"
                "💡 Cotton-polyester blends offer the best of both worlds — "
                "comfort with low maintenance!"
            )

        elif any(word in message_lower for word in ["sport", "exercise", "gym", "athletic"]):
            reply = (
                "🏃 For **sports/athletic** activities, I recommend:\n\n"
                "1. **Polyester** — Moisture-wicking, quick-drying, durable (9/10)\n"
                "2. **Nylon** — Lightweight, stretchy, abrasion-resistant\n"
                "3. **Lycra/Spandex** — Maximum stretch, comfortable fit, flexibility\n\n"
                "💡 Look for moisture-wicking blends for intense workouts!"
            )

        elif any(word in message_lower for word in ["sustain", "eco", "green", "environment"]):
            reply = (
                "🌿 For **sustainable/eco-friendly** choices, I recommend:\n\n"
                "1. **Khadi** — Sustainability: 10/10, handwoven, zero carbon footprint\n"
                "2. **Hemp** — Sustainability: 10/10, requires minimal water to grow\n"
                "3. **Bamboo** — Sustainability: 10/10, biodegradable, naturally antibacterial\n\n"
                "💡 Tencel and Modal are also great semi-synthetic eco options!"
            )

        elif context:
            reply = (
                f"Based on my recommendation engine, here's what I found:\n\n{context}\n\n"
                "Would you like to know more about any specific fabric? "
                "I can explain its properties, care instructions, and best use cases!"
            )

        else:
            reply = (
                "I'd be happy to help you find the perfect fabric! Could you tell me:\n\n"
                "1. 🌤️ What's the **weather** like? (summer/winter/rainy/humid/autumn)\n"
                "2. 🎉 Any **special occasion**? (wedding/Diwali/office/party/none)\n"
                "3. 🎯 What's the **purpose**? (daily wear/sports/formal/travel)\n\n"
                "The more details you provide, the better I can recommend!"
            )

        # Update history
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]

        return {"reply": reply, "history": new_history}

    @property
    def is_available(self):
        """Check if Gemini API is available."""
        return gemini_available and self.model is not None


# Singleton
_chat_service = None


def get_chat_service():
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
