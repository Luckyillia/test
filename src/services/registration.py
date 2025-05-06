from nicegui import ui
from src.services.user_service import UserService
from src.services.log_services import LogService
import random
import string


class Registration:
    def __init__(self, user_table=None):
        # Initialize services
        self.user_service = UserService()
        self.log_service = LogService()  # Инициализация логирования
        self.user_table = user_table
        self.avatar_url = self.generate_avatar()

        # Initialize input fields and their UI components
        self.name_input = ui.input('Имя').classes('m-auto w-64')
        self.surname_input = ui.input('Фамилия').classes('m-auto w-64')
        self.username_input = ui.input('Логин').classes('m-auto w-64')
        self.password_input = ui.input('Пароль', password=True, password_toggle_button=True).classes('m-auto w-64')

        # Initialize avatar image UI
        self.avatar_image = ui.image(self.avatar_url).classes('w-32 h-32 m-auto')

        # UI buttons
        ui.button('Сгенерировать новую аватарку', on_click=self.refresh_avatar).classes('m-auto w-64')

        # Navigation buttons
        if not self.user_table:
            ui.button('Зарегестрироваться', on_click=self.add_user).classes('m-auto w-64')
            ui.button('Вернуться', on_click=lambda: ui.navigate.to('/login')).classes('m-auto w-64')
        else:
            ui.button('Добавить пользователя', on_click=self.add_user).classes('m-auto w-64')

    def generate_avatar(self):
        # Generate a random avatar URL
        chars = string.ascii_uppercase + string.digits
        avatar_url = f'https://robohash.org/{"".join(random.choice(chars) for _ in range(5))}'
        return avatar_url

    def refresh_avatar(self):
        # Refresh the avatar image
        old_avatar = self.avatar_url
        self.avatar_url = self.generate_avatar()
        self.avatar_image.set_source(self.avatar_url)
        self.log_service.add_system_log(f'Аватар обновлен: {old_avatar} → {self.avatar_url}')

    def add_user(self, redirect_to: str = '/'):
        # Validate input fields
        if self.name_input.value and self.surname_input.value and self.username_input.value and self.password_input.value:
            if len(self.password_input.value) >= 8:
                # Try to add the user
                if not self.user_service.add_user(
                    self.name_input.value.strip(),
                    self.surname_input.value.strip(),
                    self.username_input.value.strip(),
                    self.password_input.value.strip(),
                    self.avatar_url.strip()
                ):
                    ui.notify('Такой пользователь уже есть', color='red')
                    self.log_service.add_log(
                        message=f"Попытка регистрации с существующим логином: {self.username_input.value}",
                        level="WARNING",
                        action="USER_REGISTRATION",
                        metadata={"username": self.username_input.value}
                    )
                    return

                # Clear inputs and reset avatar
                self.name_input.value = ''
                self.surname_input.value = ''
                self.username_input.value = ''
                self.password_input.value = ''
                self.avatar_url = self.generate_avatar()
                self.avatar_image.set_source(self.avatar_url)

                # Update table or redirect
                if self.user_table:
                    self.user_table.update_table()
                else:
                    ui.navigate.to(redirect_to)

            else:
                ui.notify('Пароль должен быть не меньше 8 символов', color='red')
                self.log_service.add_log(
                    message=f"Ошибка регистрации: короткий пароль для пользователя {self.username_input.value}",
                    level="ERROR",
                    action="USER_REGISTRATION",
                    metadata={"username": self.username_input.value, "password_length": len(self.password_input.value)}
                )
        else:
            ui.notify('Все поля должны быть заполненые', color='red')
            self.log_service.add_log(
                message="Ошибка регистрации: незаполненные поля",
                level="ERROR",
                action="USER_REGISTRATION"
            )
