"""
RAG Chat Service — vector search + GPT-4o-mini generation
Uses Supabase pgvector for retrieval and OpenAI for answer generation.
"""
import logging
from typing import List, Dict, Any, Optional
import openai
from ..database import get_supabase
from ..config import settings

logger = logging.getLogger(__name__)

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

SYSTEM_PROMPT = """You are pkang, a knowledgeable diet and fitness coach. You answer questions about weight loss, nutrition, exercise, body composition, and healthy lifestyle habits.

Rules:
- Base your answers on the provided knowledge context below. If the context doesn't cover the question, say so honestly and give general best-practice advice.
- Be practical, encouraging, and evidence-based.
- Keep answers concise but thorough (2-4 paragraphs max).
- If the user shares personal stats (weight, height, goals), incorporate them into your advice.
- Answer in the same language the user writes in (Korean or English).

Feature Awareness (mention naturally when relevant, never force):
- When the user asks about food/calories → suggest they try the **Food Camera** ("You can snap a photo of your meal and I'll analyze the macros instantly — check out the Food Camera feature!")
- When the user asks about body fat or physique → mention **Body Scan** ("Want an AI estimate of your current body fat %? Try our Body Scan feature!")
- When the user discusses motivation or goals → mention **Transformation Preview** ("Curious what you'd look like at your target body fat? Try the Transformation Preview!")
- When the user asks about workout form → mention **Form Check** ("Upload a video of your exercise form and get instant AI feedback with Form Check!")
- When the user tracks weight/progress → mention **Goal Projection** ("Your weight trend and projected goal date are on the Dashboard — check it out!")
- Do NOT upsell in every message. Only mention features when they are genuinely relevant to the conversation.
- Never mention credits, pricing, or cost. Just describe the feature as helpful.

Knowledge Context:
{context}"""


def _get_openai_client() -> openai.OpenAI:
    return openai.OpenAI(api_key=settings.openai_api_key)


async def embed_query(query: str) -> List[float]:
    """Embed a user query using OpenAI text-embedding-3-small."""
    client = _get_openai_client()
    resp = client.embeddings.create(model=EMBED_MODEL, input=query)
    return resp.data[0].embedding


async def search_similar_chunks(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """Embed the query and find the most similar transcript chunks via pgvector."""
    query_embedding = await embed_query(query)
    supabase = get_supabase()

    # Use Supabase RPC for vector similarity search
    result = supabase.rpc("match_transcript_chunks", {
        "query_embedding": query_embedding,
        "match_count": top_k,
    }).execute()

    return result.data if result.data else []


async def search_similar_chunks_direct(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """Fallback: fetch all and sort in Python (for when the RPC isn't set up yet)."""
    query_embedding = await embed_query(query)
    supabase = get_supabase()

    result = supabase.rpc("match_transcript_chunks", {
        "query_embedding": query_embedding,
        "match_count": top_k,
    }).execute()

    if result.data:
        return result.data

    logger.warning("RPC match_transcript_chunks not found, returning empty results")
    return []


async def generate_answer(
    query: str,
    user_context: Optional[Dict[str, Any]] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Full RAG pipeline: retrieve relevant chunks, build prompt, generate answer.
    Returns the answer text and source files used.
    """
    chunks = await search_similar_chunks(query)

    context_parts = []
    sources = []
    for chunk in chunks:
        context_parts.append(chunk.get("content", ""))
        src = chunk.get("source_file", "")
        if src and src not in sources:
            sources.append(src)

    context_text = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

    system_msg = SYSTEM_PROMPT.format(context=context_text)

    if user_context:
        profile_lines = []
        if user_context.get("weight_kg"):
            profile_lines.append(f"Current weight: {user_context['weight_kg']}kg")
        if user_context.get("target_weight_kg"):
            profile_lines.append(f"Target weight: {user_context['target_weight_kg']}kg")
        if user_context.get("height_cm"):
            profile_lines.append(f"Height: {user_context['height_cm']}cm")
        if user_context.get("gender"):
            profile_lines.append(f"Gender: {user_context['gender']}")
        if user_context.get("age"):
            profile_lines.append(f"Age: {user_context['age']}")
        if profile_lines:
            system_msg += "\n\nUser Profile:\n" + "\n".join(profile_lines)

    messages = [{"role": "system", "content": system_msg}]

    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": query})

    client = _get_openai_client()
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=800,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks),
    }


async def save_message(user_id: str, role: str, content: str, sources: List[str] = None) -> Dict[str, Any]:
    """Save a chat message to the database."""
    supabase = get_supabase()
    data = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "sources": sources or [],
    }
    result = supabase.table("chat_messages").insert(data).execute()
    return result.data[0] if result.data else data


async def get_chat_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent chat history for a user."""
    supabase = get_supabase()
    result = supabase.table("chat_messages")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()

    messages = result.data if result.data else []
    messages.reverse()
    return messages


async def clear_chat_history(user_id: str) -> bool:
    """Clear all chat history for a user."""
    supabase = get_supabase()
    supabase.table("chat_messages")\
        .delete()\
        .eq("user_id", user_id)\
        .execute()
    return True
