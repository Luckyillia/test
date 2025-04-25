from nicegui import ui, app

from src.game.game_state_service import GameStateService
from src.services.user_service import UserService


class GameRoomManagement:
    def __init__(self):
        self.user_service = UserService()
        self.game_state_service = GameStateService()
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
        self.dialog = ui.dialog().classes('w-full max-w-md')

        with self.dialog:
            with ui.card().classes('p-6 rounded-xl bg-white shadow-xl'):
                with ui.row().classes('justify-between items-center'):
                    ui.label('Присоединиться к игре').classes('text-xl font-semibold')
                    ui.button(icon='close', on_click=self.dialog.close).props('flat dense')

                ui.label('Введите ID игры').classes('text-gray-700 mb-2')
                game_id_input = ui.input(label='ID Игры').classes('w-full')

                status_label = ui.label('').classes('mt-2')

                def try_join():
                    game_id = game_id_input.value.strip()
                    if not game_id:
                        status_label.text = 'Пожалуйста, введите ID игры.'
                        status_label.classes('text-red-500 mt-2')
                        return

                    if self.game_state_service.game_exists(game_id):
                        app.storage.user.update({'game_state_id': game_id})

                        # Сохраняем в user_data.json
                        self.update_user_game_state(app.storage.user.get('user_id'), game_id)

                        status_label.text = ''
                        self.dialog.close()
                        ui.notify('Вы успешно присоединились к игре!', type='positive')
                        ui.navigate.to('/')
                    else:
                        status_label.text = 'Игры с таким ID не существует.'
                        status_label.classes('text-red-500 mt-2')

                ui.button('Присоединиться', on_click=try_join).classes('mt-4 bg-blue-600 text-white w-full')

        self.dialog.open()

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