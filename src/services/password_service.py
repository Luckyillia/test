import hashlib
import os
import binascii
import re
import random
import string


class PasswordService:
    def __init__(self):
        self.min_length = 8
        self.min_complexity = 2  # Минимальное количество различных типов символов

    def hash_password(self, password: str) -> str:
        """Хеширует пароль с солью с использованием PBKDF2"""
        # Генерируем соль
        salt = os.urandom(16)
        # Хешируем пароль
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        # Возвращаем хеш в формате, удобном для хранения
        return f"{binascii.hexlify(salt).decode('utf-8')}${binascii.hexlify(key).decode('utf-8')}"

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Проверяет, совпадает ли предоставленный пароль с хешированным"""
        # Обработка случая, когда пароли хранятся в открытом виде (для обратной совместимости)
        if '$' not in stored_password:
            return stored_password == provided_password

        # Разделяем соль и хеш
        try:
            salt_hex, key_hex = stored_password.split('$')
            salt = binascii.unhexlify(salt_hex)
            stored_key = binascii.unhexlify(key_hex)

            # Хешируем предоставленный пароль с той же солью
            key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)

            # Сравниваем хеши
            return key == stored_key
        except:
            # При любых ошибках парсинга возвращаем False
            return False

    def check_password_strength(self, password: str) -> dict:
        """Проверяет сложность пароля и возвращает результат проверки"""
        result = {
            "valid": True,
            "errors": [],
            "strength": 0  # От 0 до 5
        }

        # Проверка длины
        if len(password) < self.min_length:
            result["valid"] = False
            result["errors"].append(f"Пароль должен быть не менее {self.min_length} символов")

        # Проверка наличия разных типов символов
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digits = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

        complexity_count = sum([has_lowercase, has_uppercase, has_digits, has_special])

        if complexity_count < self.min_complexity:
            result["valid"] = False
            result["errors"].append(
                f"Пароль должен содержать минимум {self.min_complexity} из следующих типов символов: строчные буквы, заглавные буквы, цифры, специальные символы")

        # Оценка сложности пароля
        result["strength"] = min(5, complexity_count + (1 if len(password) >= 12 else 0))

        return result

    def generate_reset_code(self, length: int = 6) -> str:
        """Генерирует код восстановления пароля"""
        return ''.join(random.choices(string.digits, k=length))