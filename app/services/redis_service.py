import json
import redis
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )

    def _get_key(self, user_id: str) -> str:
        return f"chat_session:{user_id}"

    def get_history(self, user_id: str) -> list:
        redis_key = self._get_key(user_id)
        raw_history = self.client.lrange(redis_key, 0, -1)
        if raw_history:
            return [json.loads(msg) for msg in raw_history]
        return []

    def append_messages(self, user_id: str, *messages: dict) -> None:
        redis_key = self._get_key(user_id)
        for msg in messages:
            self.client.rpush(redis_key, json.dumps(msg))
        self.client.expire(redis_key, settings.SESSION_TTL)

    def clear_session(self, user_id: str) -> None:
        redis_key = self._get_key(user_id)
        self.client.delete(redis_key)

redis_service = RedisService()
