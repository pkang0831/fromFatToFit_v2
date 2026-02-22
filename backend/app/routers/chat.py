"""
Chat Router — RAG-based diet coaching chatbot endpoints
Free to use with a daily message limit (no credit cost).
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request
from pydantic import BaseModel, Field
from typing import Optional, List
from ..middleware.auth_middleware import get_current_user
from ..services.rag_chat_service import generate_answer, save_message, get_chat_history, clear_chat_history
from ..database import get_supabase
from ..rate_limit import limiter

router = APIRouter()

FREE_DAILY_LIMIT = 15
PRO_DAILY_LIMIT = 200


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    answer: str
    sources: List[str] = []
    messages_today: int = 0
    daily_limit: int = FREE_DAILY_LIMIT


class ChatHistoryItem(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    sources: List[str] = []
    created_at: Optional[str] = None


async def _count_today_messages(user_id: str) -> int:
    """Count how many user messages were sent today."""
    supabase = get_supabase()
    today = date.today().isoformat()
    result = supabase.table("chat_messages")\
        .select("id", count="exact")\
        .eq("user_id", user_id)\
        .eq("role", "user")\
        .gte("created_at", f"{today}T00:00:00")\
        .execute()
    return result.count or 0


@router.get("/status")
async def get_chat_status(current_user: dict = Depends(get_current_user)):
    """Get current chat usage status (messages today, daily limit)."""
    user_id = current_user["id"]
    is_premium = current_user.get("premium_status", False)
    limit = PRO_DAILY_LIMIT if is_premium else FREE_DAILY_LIMIT
    count = await _count_today_messages(user_id)
    return {
        "messages_today": count,
        "daily_limit": limit,
        "remaining": max(0, limit - count),
    }


@router.post("/message", response_model=ChatMessageResponse)
@limiter.limit("20/minute")
async def send_message(
    request: Request,
    chat_request: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to the AI diet coach and get a response. Free with daily limit."""
    user_id = current_user["id"]
    is_premium = current_user.get("premium_status", False)
    daily_limit = PRO_DAILY_LIMIT if is_premium else FREE_DAILY_LIMIT

    today_count = await _count_today_messages(user_id)
    if today_count >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily message limit reached ({daily_limit}/day). Come back tomorrow!"
        )

    history = await get_chat_history(user_id, limit=10)
    chat_history = [{"role": m["role"], "content": m["content"]} for m in history]

    user_context = {
        "weight_kg": current_user.get("weight_kg"),
        "target_weight_kg": current_user.get("target_weight_kg"),
        "height_cm": current_user.get("height_cm"),
        "gender": current_user.get("gender"),
        "age": current_user.get("age"),
    }

    try:
        result = await generate_answer(
            query=chat_request.message,
            user_context=user_context,
            chat_history=chat_history,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

    await save_message(user_id, "user", chat_request.message)
    await save_message(user_id, "assistant", result["answer"], result["sources"])

    return ChatMessageResponse(
        answer=result["answer"],
        sources=result["sources"],
        messages_today=today_count + 1,
        daily_limit=daily_limit,
    )


@router.get("/history", response_model=List[ChatHistoryItem])
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for the current user."""
    messages = await get_chat_history(current_user["id"], limit=limit)
    return [
        ChatHistoryItem(
            id=m.get("id"),
            role=m["role"],
            content=m["content"],
            sources=m.get("sources", []),
            created_at=m.get("created_at"),
        )
        for m in messages
    ]


@router.delete("/history")
async def delete_history(current_user: dict = Depends(get_current_user)):
    """Clear all chat history for the current user."""
    await clear_chat_history(current_user["id"])
    return {"message": "Chat history cleared"}
