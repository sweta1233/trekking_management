import json
import logging
import re
import time
from typing import List, Dict, Any, Optional

from config import Config

logger = logging.getLogger("TMA.LLMProvider")


class BaseLLMProvider:
    """Abstract base interface for TrekMate AI LLM providers."""

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def classify_intent(self, user_query: str) -> str:
        raise NotImplementedError


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.available = True
        except Exception as e:
            logger.warning(f"OpenAI client init failed: {e}")
            self.available = False

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("OpenAI client is not available")

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency_ms = int((time.time() - start_time) * 1000)

        content = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0

        return {
            "content": content,
            "model": self.model_name,
            "provider": "openai",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": latency_ms,
        }


class AnthropicLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model_name = model_name
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            self.available = True
        except Exception as e:
            logger.warning(f"Anthropic client init failed: {e}")
            self.available = False

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Anthropic client is not available")

        formatted_messages = []
        for m in messages:
            formatted_messages.append({
                "role": "user" if m.get("role") in ["user", "system"] else "assistant",
                "content": m.get("content", "")
            })

        start_time = time.time()
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=formatted_messages,
        )
        latency_ms = int((time.time() - start_time) * 1000)

        content = response.content[0].text if response.content else ""
        prompt_tokens = response.usage.input_tokens if response.usage else 0
        completion_tokens = response.usage.output_tokens if response.usage else 0

        return {
            "content": content,
            "model": self.model_name,
            "provider": "anthropic",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_ms": latency_ms,
        }


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.available = True
        except Exception as e:
            logger.warning(f"Gemini client init failed: {e}")
            self.available = False

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Gemini client is not available")

        start_time = time.time()
        conversation_text = ""
        if system_prompt:
            conversation_text += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
        for m in messages:
            conversation_text += f"{m['role'].upper()}: {m['content']}\n"
        conversation_text += "ASSISTANT: "

        response = self.model.generate_content(
            conversation_text,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
        )
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "content": response.text,
            "model": self.model_name,
            "provider": "gemini",
            "prompt_tokens": len(conversation_text) // 4,
            "completion_tokens": len(response.text) // 4,
            "latency_ms": latency_ms,
        }


class MockRulesEngineLLMProvider(BaseLLMProvider):
    """
    High-fidelity offline fallback LLM provider.
    Ensures that the entire TrekMate AI platform (RAG, agent workflow, trip planning,
    fitness readiness, packing, intent routing, and tool calling) runs 100% reliably
    even when running completely offline or without paid third-party API keys.
    """

    def __init__(self):
        self.model_name = "trekmate-rules-engine-v1"

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        start_time = time.time()
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        query = last_user_msg.lower()

        # Check if RAG context was injected in system_prompt
        has_verified_context = False
        context_body = ""
        if system_prompt and "VERIFIED CONTEXT:" in system_prompt:
            ctx_split = system_prompt.split("VERIFIED CONTEXT:\n")
            if len(ctx_split) > 1 and "No external documents found" not in ctx_split[1]:
                context_body = ctx_split[1].strip()
                if len(context_body) > 30:
                    has_verified_context = True

        if has_verified_context:
            # Synthesize answer directly grounded in the verified RAG context
            # Extract citation headers like [Document Title (p. 1, § Section)]
            citations = re.findall(r"\[(.*?)\]", context_body)
            main_citation = citations[0] if citations else "Official Trekking Manual"

            # Extract key paragraphs or bullet points from context
            paragraphs = [p.strip() for p in context_body.split("\n\n") if p.strip() and not p.strip().startswith("[") and not p.strip().startswith("---")]

            # Select most relevant sentences from context matching query keywords
            query_words = set(re.findall(r"\b\w{3,}\b", query))
            scored_sentences = []
            for p in paragraphs:
                sents = [s.strip() for s in re.split(r"[.\n]", p) if len(s.strip()) > 15]
                for s in sents:
                    s_words = set(re.findall(r"\b\w{3,}\b", s.lower()))
                    match_score = len(query_words.intersection(s_words))
                    scored_sentences.append((match_score, s))

            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            top_sents = [s for score, s in scored_sentences[:6] if score > 0]
            if not top_sents and paragraphs:
                top_sents = [paragraphs[0][:300]]

            synthesized_body = "\n\n".join(f"• {s}." if not s.endswith(".") else f"• {s}" for s in top_sents)

            content = (
                f"Based on the verified expedition documentation in **[{main_citation}]**:\n\n"
                f"{synthesized_body}\n\n"
                f"**Key Safety & Field Guidelines**:\n"
                f"- Maintain active hydration (3-4L/day) and monitor Lake Louise AMS symptoms daily.\n"
                f"- Strictly adhere to the golden rule: *Climb high, sleep low*.\n"
                f"- For full emergency evacuation protocols, reference [{main_citation}]."
            )

        elif "recommend" in query or "suggest" in query or "beginner" in query or "which trek" in query:
            content = (
                "Based on trail difficulty, altitude, and current availability, here are top recommendations:\n\n"
                "1. **Kedarkantha Trek (3,810m)** - *Easy to Moderate* | 5 Days | ₹9,500\n"
                "   - Perfect for beginners with panoramic 360-degree summit views of the Garhwal Himalayas.\n"
                "2. **Hampta Pass & Chandratal (4,270m)** - *Moderate* | 5 Days | ₹11,200\n"
                "   - Dynamic landscape transition from lush Kullu valley to dramatic desert mountains of Spiti.\n"
                "3. **Valley of Flowers (4,390m)** - *Easy to Moderate* | 6 Days | ₹10,800\n"
                "   - UNESCO World Heritage site carpeted with endemic alpine flora and serene Hemkund Sahib lake.\n\n"
                "Would you like to review day-by-day itineraries, check gear requirements, or check fitness readiness?"
            )
        elif "packing" in query or "gear" in query or "pack" in query or "clothes" in query:
            content = (
                "Here is your altitude-adapted **Trekking Packing Checklist**:\n\n"
                "• **Clothing & Layers**: Moisture-wicking base layer (x3), fleece mid-layer, 700+ fill down jacket, waterproof windcheater.\n"
                "• **Footwear**: Ankle-support trekking boots (broken-in), 4 pairs synthetic/wool socks, microspikes (if snow).\n"
                "• **Gear & Hardware**: 50-60L rucksack with rain cover, UV400 polarized sunglasses, headlamp with extra batteries, adjustable trekking poles.\n"
                "• **Medical & Safety**: Personal first-aid kit, Diamox (consult doctor for AMS), hydration bladder + water purification tablets.\n\n"
                "*Tip: Always pack light and use dry-bags to protect thermal layers from unexpected alpine rains.*"
            )
        elif "fitness" in query or "readiness" in query or "prepare" in query or "training" in query:
            content = (
                "**Trek Readiness & Fitness Assessment**:\n\n"
                "For high-altitude treks exceeding 3,500m, target the following benchmarks:\n"
                "1. **Aerobic Endurance**: Ability to run 5 km in under 32-35 minutes without stopping.\n"
                "2. **Cardiovascular Conditioning**: 45 minutes of stair climbing or cycling 3 times weekly.\n"
                "3. **Leg Strength**: Squats, lunges, and calf raises (3 sets of 20 reps each).\n"
                "4. **Acclimatization Golden Rule**: Climb high, sleep low, drink 4 liters of water daily, and avoid alcohol at altitude.\n\n"
                "⚠️ *Safety Disclaimer: This is general conditioning guidance. Consult a licensed medical practitioner before attempting high-altitude expeditions.*"
            )
        elif "book" in query or "reservation" in query or "reserve" in query:
            content = (
                "To confirm your trek reservation on TrekMate AI:\n\n"
                "1. Select your desired trek and preferred expedition start date.\n"
                "2. Ensure all participants meet the minimum fitness and medical requirements.\n"
                "3. Complete the reservation checkout with emergency contact details.\n\n"
                "You can manage your confirmed slots in the **My Bookings** dashboard anytime."
            )
        elif "itinerary" in query or "day" in query or "plan" in query:
            content = (
                "**Sample Expedition Itinerary Structure**:\n\n"
                "• **Day 1**: Base Camp arrival, briefing, gear check & initial acclimatization walk.\n"
                "• **Day 2**: Ascent to intermediate alpine camp (gain 600m elevation, active hydration).\n"
                "• **Day 3**: Acclimatization hike to ridge viewpoint, safety training on microspikes and gaiters.\n"
                "• **Day 4**: Early morning summit push (3:00 AM start), enjoy sunrise at the peak, descent to basecamp.\n"
                "• **Day 5**: Debriefing, certificate distribution, and departure.\n\n"
                "Would you like an itinerary tailored for a specific trek or altitude goal?"
            )
        else:
            content = (
                "Welcome to **TrekMate AI**! I am your intelligent adventure assistant. "
                "I can help you explore curated Himalayan treks, synthesize official trail guides using RAG, "
                "generate custom day-by-day itineraries, evaluate fitness readiness, and adapt your packing checklist. "
                "How may I assist your next mountain journey today?"
            )

        latency_ms = int((time.time() - start_time) * 1000) + 8
        return {
            "content": content,
            "model": self.model_name,
            "provider": "mock",
            "prompt_tokens": len(query) // 4 + 20,
            "completion_tokens": len(content) // 4,
            "latency_ms": latency_ms,
        }


def get_llm_provider() -> BaseLLMProvider:
    """Factory function returning the configured LLM provider with graceful fallback."""
    provider_name = Config.LLM_PROVIDER.lower()

    if provider_name == "openai" and Config.OPENAI_API_KEY:
        try:
            return OpenAILLMProvider(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        except Exception as e:
            logger.warning(f"Falling back to Mock provider due to OpenAI error: {e}")

    elif provider_name == "anthropic" and Config.ANTHROPIC_API_KEY:
        try:
            return AnthropicLLMProvider(Config.ANTHROPIC_API_KEY, Config.ANTHROPIC_MODEL)
        except Exception as e:
            logger.warning(f"Falling back to Mock provider due to Anthropic error: {e}")

    elif (provider_name == "gemini" or provider_name == "google") and Config.GOOGLE_API_KEY:
        try:
            return GeminiLLMProvider(Config.GOOGLE_API_KEY, Config.GEMINI_MODEL)
        except Exception as e:
            logger.warning(f"Falling back to Mock provider due to Gemini error: {e}")

    # Default offline robust fallback
    return MockRulesEngineLLMProvider()
