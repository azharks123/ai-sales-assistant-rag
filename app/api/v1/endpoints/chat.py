from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatPayload, ChatResponse
from app.services.redis_service import redis_service
from app.services.llm_service import llm_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, summary="Send message to AI sales manager")
async def ai_chat(payload: ChatPayload):
    try:
        history = redis_service.get_history(payload.user_id)
        
        ai_response_content = await llm_service.process_chat(history, payload.message)

        user_message = {"role": "user", "content": payload.message}
        assistant_message = {"role": "assistant", "content": ai_response_content}
        redis_service.append_messages(payload.user_id, user_message, assistant_message)

        return ChatResponse(user_id=payload.user_id, message=ai_response_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", summary="Clear user chat session memory")
async def clear_chat_memory(user_id: str):
    redis_service.clear_session(user_id)
    return {"message": f"Chat memory cleared for user {user_id}."}
