from nicegui import ui, app
from src.services.user_service import UserService
from src.services.log_services import LogService  # <-- добавляем LogService


class GameRoomManagement:
    def __init__(self, game_state_service):
        self.user_service = UserService()
        self.game_state_service = game_state_service
        self.log_service = LogService()  # <-- создаем экземпляр логов
        pass

    def leave_game(self):
        if not app.storage.user.get('game_state_id'):
            ui.notify('В данный момент ты не находишься в комнате', type='warning')
            self.log_service.add_user_action_log(
                user_id=app.storage.user.get('user_id'),
                action="leave_game_attempt",
                message="Пользователь попытался выйти, но не находился в игре"
            )
            return

        game_state_id = app.storage.user.get('game_state_id')
        app.storage.user.update({'game_state_id': None, 'color': None})
        self.update_user_game_state(app.storage.user.get('user_id'), None)

        self.log_service.add_user_action_log(
            user_id=app.storage.user.get('user_id'),
            action="leave_game",
            message=f"Пользователь покинул игру (game_state_id={game_state_id})",
            metadata={"previous_game_state_id": game_state_id}
        )

        ui.navigate.to('/')

    def show_join_game_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('p-6 w-96'):
            ui.label('Присоединиться к игре').classes('text-xl font-bold mb-4')

            game_id_input = None
            status_label = ui.label('').classes('mt-2')

            def try_join():
                game_id = game_id_input.value.strip()
                if not game_id:
                    status_label.text = 'Пожалуйста, введите ID игры.'
                    status_label.classes('text-red-500 mt-2')
                    self.log_service.add_user_action_log(
                        user_id=app.storage.user.get('user_id'),
                        action="JOIN_GAME_FAILED",
                        message="Пользователь не ввел ID игры"
                    )
                    return

                if self.game_state_service.game_exists(game_id):
                    app.storage.user.update({'game_state_id': game_id})
                    self.update_user_game_state(app.storage.user.get('user_id'), game_id)

                    self.log_service.add_user_action_log(
                        user_id=app.storage.user.get('user_id'),
                        action="JOIN_GAME_SUCCESS",
                        message=f"Пользователь успешно присоединился к игре",
                        metadata={"joined_game_id": game_id}
                    )

                    status_label.text = ''
                    dialog.close()
                    ui.notify('✅ Вы успешно присоединились к игре!', type='positive')
                    ui.navigate.to('/')
                else:
                    status_label.text = '❌ Игры с таким ID не существует.'
                    status_label.classes('text-red-500 mt-2')

                    self.log_service.add_user_action_log(
                        user_id=app.storage.user.get('user_id'),
                        action="JOIN_GAME_FAILED",
                        message=f"Пользователь пытался присоединиться к несуществующей игре",
                        metadata={"attempted_game_id": game_id}
                    )

            game_id_input = ui.input(label='Введите ID места').classes('w-full mb-4').on('keydown.enter', try_join)
            with ui.row().classes('w-full justify-between'):
                ui.button('Отмена', on_click=dialog.close).classes('bg-gray-300 dark:bg-gray-700')
                ui.button('Войти', on_click=lambda: try_join()).classes('bg-blue-500 text-white')

        dialog.open()

    def update_user_game_state(self, user_id, game_state_id):
        users = self.user_service.load_data()
        for user in users:
            if user['id'] == user_id:
                user['gameState'] = game_state_id
                self.user_service.write_data(users)

                self.log_service.add_system_log(
                    user_id=user_id,
                    message=f"Обновлено состояние игры пользователя",
                    metadata={"new_game_state_id": game_state_id, "username": user['username']}
                )

                return True
        self.log_service.add_error_log(
            error_message=f"Не удалось найти пользователя с id {user_id} для обновления состояния игры",
            user_id=user_id,
            metadata={"attempted_game_state_id": game_state_id}
        )
        return False
