import jwt
import time
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class AuthService:
    def __init__(self, user_service):
        self.user_service = user_service
        self.token_storage = {}  # В продакшне заменить на БД

        # Генерируем или загружаем секретный ключ
        self.secret_key = os.getenv("AUTH_SECRET_KEY") or "natka.zajk79_secure_key"

    def generate_token(self, user_id: str, remember_me: bool = False) -> str:
        """Генерирует JWT-токен для пользователя"""
        # Устанавливаем срок действия токена
        expiration = datetime.now() + timedelta(days=30 if remember_me else 1)

        # Создаем уникальный идентификатор для токена
        token_id = str(uuid.uuid4())

        # Записываем токен в хранилище для возможности его отзыва
        self.token_storage[token_id] = {
            "user_id": user_id,
            "expires": expiration,
            "created": datetime.now()
        }

        # Создаем JWT-токен
        payload = {
            "user_id": user_id,
            "exp": int(expiration.timestamp()),
            "iat": int(datetime.now().timestamp()),
            "jti": token_id
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def validate_token(self, token: str) -> Optional[str]:
        """Проверяет валидность токена и возвращает ID пользователя"""
        try:
            # Декодируем токен
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            token_id = payload.get("jti")

            # Проверяем, не был ли токен отозван
            if token_id not in self.token_storage:
                return None

            # Проверяем срок действия
            if datetime.now().timestamp() > payload["exp"]:
                return None

            return payload["user_id"]
        except:
            return None

    def revoke_token(self, token: str) -> bool:
        """Отзывает токен (выход из системы)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            token_id = payload.get("jti")
            if token_id in self.token_storage:
                del self.token_storage[token_id]
                return True
        except:
            pass
        return False

    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Отзывает все токены пользователя (выход со всех устройств)
        Возвращает количество отозванных токенов"""
        tokens_to_remove = []
        for token_id, data in self.token_storage.items():
            if data["user_id"] == user_id:
                tokens_to_remove.append(token_id)

        for token_id in tokens_to_remove:
            del self.token_storage[token_id]

        return len(tokens_to_remove)

    def cleanup_expired_tokens(self) -> int:
        """Очищает истекшие токены из хранилища
        Возвращает количество удаленных токенов"""
        current_time = datetime.now()
        tokens_to_remove = []

        for token_id, data in self.token_storage.items():
            if data["expires"] < current_time:
                tokens_to_remove.append(token_id)

        for token_id in tokens_to_remove:
            del self.token_storage[token_id]

        return len(tokens_to_remove)