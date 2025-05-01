from nicegui import app, ui

from src.game.game_room_management import GameRoomManagement
from src.game.admin_game_ui import AdminGameUI
from src.game.game_room_management_ui import GameRoomManagementUI
from src.game.game_ui import GameUI
from src.services.log_services import LogService
from src.services.user_profile import UserProfile
from src.ui.components.user_table import UserTable
from src.services.registration import Registration
from src.services.user_service import UserService


class UserUI:
    def __init__(self):
        # Initialize user service and user table
        self.user_service = UserService()
        self.user_table = UserTable(self.user_service)
        self.user_profile = UserProfile()
        self.admin_game_ui = AdminGameUI()
        self.game_ui = GameUI()
        self.log_services = LogService()
        self.game_room_management = GameRoomManagement(game_ui=self.game_ui)
        self.game_room_management_ui = GameRoomManagementUI()
        self.game_data = {}  # Store game data at class level
        self.switch_dark_mode(app.storage.user.get('dark_mode'))
        self.setup_ui()

    def setup_ui(self):

        # Create UI tabs
        with ui.tabs().classes('w-full') as tabs:
            if (app.storage.user.get('username') == 'lucky_illia'):
                one = ui.tab('Добавить пользователя')
                two = ui.tab('Список пользователей')
                three = ui.tab('Логи')
                four = ui.tab('Управление играми')
                five = ui.tab('Управление комнатами')
            six = ui.tab('Игра')
            seven = ui.tab('Профиль')

        # User info and logout button
        with ui.row().classes('w-full items-center px-4 py-2 rounded-lg flex justify-center'):
            self.dark_mode = ui.switch('Dark mode', value=app.storage.user.get('dark_mode'), on_change=lambda e: self.switch_dark_mode(e.value)).classes('flex-grow')
            ui.label(f'Привет, {app.storage.user.get("username", "")}').classes('text-xl font-semibold text-primary text-center')
            ui.button(on_click=self.logout, icon='logout').props('outline round')

        # Define content for each tab
        with ui.tab_panels(tabs, value=six).classes('w-full flex justify-center items-center'):
            if app.storage.user.get('username') == 'lucky_illia':
                with ui.tab_panel(one):
                    reg = Registration(self.user_table)
                with ui.tab_panel(two):
                    self.user_table.init_table()
                with ui.tab_panel(three):
                    self.log_services.log_interface()
                with ui.tab_panel(four):
                    self.admin_game_ui.table_game()
                with ui.tab_panel(five):
                    self.game_room_management_ui.create_ui()

            with ui.tab_panel(six):
                self.game_ui.show_game_interface
            with ui.tab_panel(seven):
                self.user_profile.show_profile_ui(app.storage.user.get('user_id'))


    def switch_dark_mode(self, arg):
        app.storage.user.update({'dark_mode': arg})
        if arg:
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()

    def logout(self) -> None:
        app.storage.user.clear()
        ui.navigate.to('/login')