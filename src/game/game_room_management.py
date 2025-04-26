from nicegui import ui, app

from src.services.user_service import UserService


class GameRoomManagement:
    def __init__(self , game_state_service):
        self.user_service = UserService()
        self.game_state_service = game_state_service
        pass
    def leave_game(self):
        if not app.storage.user.get('game_state_id'):
            ui.notify('Nie jestes w zadnym pokoju!', type='warning')
            return
        game_state_id = app.storage.user.get('game_state_id')
        app.storage.user.update({'game_state_id': None, 'color': None})
        self.update_user_game_state(app.storage.user.get('user_id'), None)
        ui.navigate.to('/')

    def show_join_game_dialog(self):
        # Создаем диалоговое окно
        with ui.dialog() as dialog, ui.card().classes('p-6 w-96'):
            ui.label('Присоединиться к игре').classes('text-xl font-bold mb-4')

            game_id_input = ui.input(label='Введите ID места').classes('w-full mb-4')

            status_label = ui.label('').classes('mt-2')

            def try_join():
                game_id = game_id_input.value.strip()
                if not game_id:
                    status_label.text = 'Пожалуйста, введите ID игры.'
                    status_label.classes('text-red-500 mt-2')
                    return

                if self.game_state_service.game_exists(game_id):
                    app.storage.user.update({'game_state_id': game_id})
                    self.update_user_game_state(app.storage.user.get('user_id'), game_id)

                    status_label.text = ''
                    dialog.close()
                    ui.notify('✅ Вы успешно присоединились к игре!', type='positive')
                    ui.navigate.to('/')
                else:
                    status_label.text = '❌ Игры с таким ID не существует.'
                    status_label.classes('text-red-500 mt-2')

            with ui.row().classes('w-full justify-between'):
                ui.button('Отмена', on_click=dialog.close).classes('bg-gray-300 dark:bg-gray-700')
                ui.button('Войти', on_click=lambda: try_join()).classes('bg-blue-500 text-white')
        dialog.open()

    def update_user_game_state(self, user_id, game_state_id):
        """Update a user's game state ID in the user data"""
        from src.services.user_service import UserService
        users = self.user_service.load_data()
        for user in users:
            if user['id'] == user_id:
                user['gameState'] = game_state_id
                self.user_service.write_data(users)
                return True
        return False