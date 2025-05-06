import time
from collections import defaultdict
from typing import Dict, List, Union, Optional


class LoginSecurity:
    def __init__(self):
        self.login_attempts = defaultdict(list)
        self.ip_attempts = defaultdict(list)
        self.lock_duration = 30 * 60  # 30 минут блокировки (в секундах)
        self.max_user_attempts = 5  # Максимальное количество попыток для пользователя
        self.max_ip_attempts = 10  # Максимальное количество попыток с одного IP

    def record_attempt(self, username: str, ip_address: str, success: bool) -> None:
        """Записывает попытку входа"""
        current_time = time.time()

        # Очищаем устаревшие попытки для пользователя (старше lock_duration)
        self.login_attempts[username] = [
            attempt for attempt in self.login_attempts[username]
            if current_time - attempt["timestamp"] < self.lock_duration
        ]

        # Очищаем устаревшие попытки для IP (старше lock_duration)
        self.ip_attempts[ip_address] = [
            attempt for attempt in self.ip_attempts[ip_address]
            if current_time - attempt["timestamp"] < self.lock_duration
        ]

        # Записываем новую попытку для пользователя
        self.login_attempts[username].append({
            "timestamp": current_time,
            "ip_address": ip_address,
            "success": success
        })

        # Записываем новую попытку для IP
        self.ip_attempts[ip_address].append({
            "timestamp": current_time,
            "username": username,
            "success": success
        })

    def is_account_locked(self, username: str) -> bool:
        """Проверяет, заблокирован ли аккаунт"""
        current_time = time.time()
        recent_attempts = [
            attempt for attempt in self.login_attempts.get(username, [])
            if current_time - attempt["timestamp"] < self.lock_duration
        ]

        # Считаем неудачные попытки
        failed_attempts = sum(1 for attempt in recent_attempts if not attempt["success"])

        return failed_attempts >= self.max_user_attempts

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Проверяет, заблокирован ли IP-адрес"""
        current_time = time.time()
        recent_attempts = [
            attempt for attempt in self.ip_attempts.get(ip_address, [])
            if current_time - attempt["timestamp"] < self.lock_duration
        ]

        # Считаем неудачные попытки
        failed_attempts = sum(1 for attempt in recent_attempts if not attempt["success"])

        return failed_attempts >= self.max_ip_attempts

    def get_remaining_attempts(self, username: str) -> int:
        """Возвращает оставшееся количество попыток для аккаунта"""
        if self.is_account_locked(username):
            return 0

        failed_attempts = sum(
            1 for attempt in self.login_attempts.get(username, [])
            if not attempt["success"]
        )

        return max(0, self.max_user_attempts - failed_attempts)

    def get_unlock_time(self, username: str) -> Optional[int]:
        """Возвращает время (в секундах), через которое аккаунт будет разблокирован"""
        if not self.is_account_locked(username):
            return None

        current_time = time.time()
        oldest_failed_attempt = float('inf')

        for attempt in self.login_attempts.get(username, []):
            if not attempt["success"]:
                oldest_failed_attempt = min(oldest_failed_attempt, attempt["timestamp"])

        if oldest_failed_attempt == float('inf'):
            return None

        unlock_time = oldest_failed_attempt + self.lock_duration - current_time
        return max(0, int(unlock_time))

    def reset_attempts(self, username: str) -> None:
        """Сбрасывает счетчик неудачных попыток для пользователя"""
        if username in self.login_attempts:
            del self.login_attempts[username]