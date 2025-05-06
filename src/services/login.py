from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.user_service import UserService
from src.services.registration import Registration
from src.services.log_services import LogService  # Добавил импорт логирования

from nicegui import app, ui

UNRESTRICTED_PAGE_ROUTES = {'/login', '/register'}

log_service = LogService()  # Инициализация логирования


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in UNRESTRICTED_PAGE_ROUTES:
                return RedirectResponse(f'/login?redirect_to={request.url.path}')
        return await call_next(request)


@ui.page('/register')
def register() -> None:
    Registration()
    # Логируем попытку открытия страницы регистрации
    log_service.add_system_log('Открыта страница регистрации')


@ui.page('/login')
def login(redirect_to: str = '/') -> Optional[RedirectResponse]:
    def try_login() -> None:
        users = UserService().load_data()
        for user in users:
            if user['username'] == username.value and user['password'] == password.value:
                game_state_id = user['gameState']
                app.storage.user.update({
                    'username': username.value,
                    'user_id': user['id'],
                    'authenticated': True,
                    'game_state_id': game_state_id,
                    'dark_mode': True
                })
                # Логируем успешный вход
                log_service.add_user_action_log(
                    user_id=user['id'],
                    action='LOGIN_SUCCESS',
                    message=f"Пользователь {username.value} успешно вошёл в систему"
                )
                ui.navigate.to(redirect_to)
                return
        # Логируем неудачную попытку входа
        log_service.add_error_log(
            error_message=f"Неудачная попытка входа для логина: {username.value}",
            action="LOGIN_FAILED",
            metadata={"entered_username": username.value, "entered_password": password.value}
        )
        ui.notify('Неправильный пароль или логин', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')

    with ui.card().classes('absolute-center'):
        username = ui.input('Логин').on('keydown.enter', try_login)
        password = ui.input('Пароль', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Войти', on_click=try_login)
        ui.button('Регистрация', on_click=lambda: ui.navigate.to('/register'))

    # Логируем открытие страницы входа
    log_service.add_system_log('Открыта страница входа')

    return None
