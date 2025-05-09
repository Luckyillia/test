import json
import os
import uuid
from src.models.user import User
from src.services.log_services import LogService
from src.services.password_service import PasswordService


class UserService:
    def __init__(self, file_name='data/data.json'):
        self.file_name = file_name
        self.log_service = LogService()
        self.password_service = PasswordService()

    def load_data(self):
        directory = os.path.dirname(self.file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.file_name) or os.stat(self.file_name).st_size == 0:
            return []

        try:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                users = json.load(file).get("users", [])
                return users
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.log_service.add_error_log(
                error_message="Ошибка загрузки данных пользователей",
                metadata={"exception": str(e)}
            )
            return []

    def write_data(self, users):
        try:
            directory = os.path.dirname(self.file_name)
            if not os.path.exists(directory):
                os.makedirs(directory)

            data_to_write = json.dumps(
                {"users": users},
                indent=4,
                ensure_ascii=False
            )

            temp_file_name = f"{self.file_name}.tmp"
            with open(temp_file_name, "w", encoding="utf-8") as temp_file:
                temp_file.write(data_to_write)

            os.replace(temp_file_name, self.file_name)
            return True

        except Exception as e:
            self.log_service.add_error_log(
                error_message="Ошибка записи данных пользователей",
                metadata={"exception": str(e)}
            )
            return False

    def add_user(self, name, surname, username, password, avatar, email=None):
        # Проверяем доступность имени пользователя
        users = self.load_data()
        if not self.is_username_available(username):
            self.log_service.add_error_log(
                error_message="Попытка регистрации с занятым именем пользователя",
                metadata={"username": username}
            )
            return False

        # Проверяем сложность пароля
        password_check = self.password_service.check_password_strength(password)
        if not password_check["valid"]:
            self.log_service.add_error_log(
                error_message="Пароль не соответствует требованиям безопасности",
                metadata={"password_errors": password_check["errors"]}
            )
            return False

        # Хешируем пароль перед сохранением
        hashed_password = self.password_service.hash_password(password)

        user_id = str(uuid.uuid4())
        new_user = User(user_id, name, surname, username, hashed_password, avatar, email).to_dict()
        users.append(new_user)
        success = self.write_data(users)

        if success:
            self.log_service.add_user_action_log(
                user_id=user_id,
                action="USER_REGISTRATION",
                message=f"Пользователь {username} успешно зарегистрирован"
            )
        return success

    def delete_user(self, user_id):
        users = self.load_data()
        updated_users = [user for user in users if user['id'] != user_id]
        if len(updated_users) == len(users):
            return False
        success = self.write_data(updated_users)

        if success:
            self.log_service.add_user_action_log(
                user_id=user_id,
                action="DELETE_USER_ACCOUNT",
                message="Пользовательский аккаунт успешно удалён"
            )
        return success

    def edit_user(self, user_id, new_data):
        users = self.load_data()
        for i, user in enumerate(users):
            if user['id'] == user_id:
                if 'id' in new_data and new_data['id'] != user_id:
                    self.log_service.add_error_log(
                        error_message="Попытка изменения ID пользователя",
                        metadata={"user_id": user_id}
                    )
                    return False

                if 'username' in new_data and new_data['username'] != user['username']:
                    if not self.is_username_available(new_data['username']):
                        self.log_service.add_error_log(
                            error_message="Попытка изменения на уже занятое имя пользователя",
                            metadata={"new_username": new_data['username']}
                        )
                        return False

                # Если меняется пароль, хешируем его
                if 'password' in new_data and new_data['password'] != user['password']:
                    # Проверяем, не является ли пароль уже хешированным
                    if '$' not in new_data['password']:
                        # Проверяем сложность пароля
                        password_check = self.password_service.check_password_strength(new_data['password'])
                        if not password_check["valid"]:
                            self.log_service.add_error_log(
                                error_message="Новый пароль не соответствует требованиям безопасности",
                                metadata={"password_errors": password_check["errors"]}
                            )
                            return False
                        # Хешируем пароль
                        new_data['password'] = self.password_service.hash_password(new_data['password'])

                users[i] = {**user, **new_data}
                success = self.write_data(users)

                if success:
                    self.log_service.add_user_action_log(
                        user_id=user_id,
                        action="EDIT_USER_DATA",
                        message="Данные пользователя успешно изменены"
                    )
                return success
        return False

    def is_username_available(self, username):
        users = self.load_data()
        return not any(user['username'] == username for user in users)

    def get_user_by_username(self, username):
        users = self.load_data()
        for user in users:
            if user['username'] == username:
                return user
        return None

    def get_user_by_id(self, user_id):
        users = self.load_data()
        for user in users:
            if user['id'] == user_id:
                return user
        return None

    def migrate_passwords(self):
        """Мигрирует все пароли из открытого текста в хешированный формат"""
        users = self.load_data()
        updated = 0

        for user in users:
            if '$' not in user['password']:
                # Пароль в открытом виде, хешируем его
                user['password'] = self.password_service.hash_password(user['password'])
                updated += 1

        if updated > 0:
            if self.write_data(users):
                self.log_service.add_system_log(
                    message=f"Миграция паролей: успешно захешировано {updated} паролей",
                    metadata={"migrated_count": updated}
                )
                return updated
            else:
                self.log_service.add_error_log(
                    error_message="Ошибка при миграции паролей",
                    metadata={"attempted_count": updated}
                )
                return 0

        return 0  # Нет паролей для миграции