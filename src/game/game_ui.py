from nicegui import ui, app
from src.game.game_state_service import GameStateService
from src.game.game_dialog import GameDialog
from src.game.game_room_management import GameRoomManagement
from src.services.log_services import LogService


class GameUI:
    def __init__(self):
        self.last_update = 0
        self.log_service = LogService()
        self.timer = None
        self.game_state_service = GameStateService()
        self.game_dialog = GameDialog(self)
        self.game_room_management = GameRoomManagement(game_ui=self)

    def check_updates_safely(self):
        """Безопасная проверка обновлений с учетом состояния клиента"""
        # Проверяем подключен ли клиент перед выполнением
        if hasattr(ui, 'client_connected') and not ui.client_connected():
            return  # Просто выходим, если клиент не подключен

        self.game_room_management.check_for_updates()

    def refresh_game_data(self, room_id):
        self.log_service.add_log(
            level='GAME',
            message=f"Обновление данных игры для игры: {room_id}",
            action="REFRESH_GAME",
            metadata={"game_id": room_id}
        )

        # Используем метод get_game_state из game_room_management
        room_data = self.game_room_management.get_game_state(room_id)
        game_data = self.game_state_service.get_game_state(room_data['game_id'])
        ui.update()
        return room_data, game_data

    @property
    def show_game_interface(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
        current_room_id = app.storage.user.get('game_state_id')
        user_id = app.storage.user.get('user_id')

        # Создаем или получаем контейнер для игрового интерфейса
        if hasattr(self, 'game_container'):
            self.game_container.clear()
        else:
            self.game_container = ui.element('div').classes('w-full')

        if not current_room_id:
            with self.game_container:
                with ui.card().classes(
                        'w-full max-w-lg mx-auto mt-6 p-6 shadow-lg bg-gray-100 dark:bg-gray-800 rounded-2xl'):
                    ui.label('У вас нет активной игры').classes(
                        'text-xl font-semibold text-center text-gray-800 dark:text-gray-100 mb-2')

                    ui.label('Пожалуйста, войдите в существующую игру или создайте новую.').classes(
                        'text-center text-gray-600 dark:text-gray-300 mb-4')

                    ui.button('Войти в игру',
                              on_click=lambda: self.game_room_management.show_join_game_dialog(self)).classes(
                        'bg-blue-500 hover:bg-blue-600 text-white text-lg w-full rounded-lg py-2 transition')

            self.log_service.add_log(
                level='GAME',
                message="Показывание интерфейса без игры",
                user_id=user_id,
                action="NO_GAME"
            )
            return

        # Проверяем существование игры через game_room_management
        if not self.game_id_exists(current_room_id):
            self.log_service.add_log(
                level='GAME',
                action='ERROR',
                message=f"Игра не найдена: {current_room_id}",
                user_id=user_id,
                metadata={"game_id": current_room_id}
            )

            with self.game_container:
                with ui.card().classes(
                        'w-full max-w-lg mx-auto mt-6 p-6 shadow-lg bg-gray-100 dark:bg-gray-800 rounded-2xl'):
                    ui.label(f'⚠️ Игра с ID "{current_room_id}" не найдена.').classes(
                        'text-xl font-semibold text-center text-gray-800 dark:text-gray-100 mb-2')

                    ui.label('Проверьте правильность ID или выберите другую игру.').classes(
                        'text-center text-gray-600 dark:text-gray-300 mb-4')

                    self.game_room_management.update_user_game_state(app.storage.user.get('user_id'), None)
                    app.storage.user.update({'game_state_id': None})

                    ui.button("Вернуться назад", on_click=lambda: ui.navigate.to('/')).classes(
                        'mt-6 bg-blue-600 hover:bg-blue-700 text-white text-lg w-full rounded-lg py-2')
            return

        room_data, game_data = self.refresh_game_data(current_room_id)
        if room_data['status'] != 'finished':
            self.log_service.add_log(
                level='GAME',
                message=f"Показывание активной игры для пользователя",
                user_id=user_id,
                action="SHOW_GAME",
                metadata={"game_id": current_room_id, "move": game_data.get("move", 0)}
            )
            self.timer = ui.timer(interval=1.0, callback=self.check_updates_safely)
            with self.game_container:
                with ui.card().classes('w-full p-6 bg-gray-50 dark:bg-gray-800'):
                    with ui.row().classes('w-full justify-between items-center mb-4'):
                        ui.label('Игровой интерфейс').classes('text-xl font-bold')
                        ui.label(f'Ходов: {room_data.get("move", 0)}').classes('text-right text-sm text-gray-600')

                    # Получаем историю локаций через game_room_management
                    location_history = self.game_room_management.get_location_history(current_room_id)
                    current_location = self.game_room_management.get_current_location(current_room_id, self)

                    # Если есть история локаций, показываем последнюю
                    if location_history:
                        for i, location in enumerate(location_history):
                            location_id = location["id"]
                            visited_at = location["visited_at"]

                            spravochnik = game_data.get('spravochnik', {})
                            gosplace = spravochnik.get('gosplace', {})
                            people = spravochnik.get('people', {})
                            obplace = spravochnik.get('obplace', {})

                            # Определяем название локации
                            if location_id in gosplace:
                                location_name = gosplace[location_id]
                            elif location_id in people:
                                location_name = people[location_id]
                            elif location_id in obplace:
                                location_name = obplace[location_id]
                            elif location_id == "start":
                                location_name = 'Вводные данные'
                            elif location_id == game_data['tooltip']['location_id']:
                                location_name = "Подсказка"
                            else:
                                location_name = 'Неизвестная локация'

                            location_text = None
                            additional_document = None

                            if location_id == '112102':  # Полиция
                                location_text = game_data.get('112102', {}).get('text',
                                                                                'Информация о полиции отсутствует')
                                additional_document = game_data.get('112102', {}).get('delo', None)
                            elif location_id == '440321':  # Морг
                                location_text = game_data.get('440321', {}).get('text',
                                                                                'Информация о морге отсутствует')
                                additional_document = game_data.get('440321', {}).get('vskrytie', None)
                            elif location_id == '220123':  # ЗАГС
                                location_text = game_data.get('220123', {}).get('text',
                                                                                'Информация о ЗАГСе отсутствует')
                                additional_document = game_data.get('220123', {}).get('otchet', None)
                            elif location_id == 'start':
                                location_text = game_data.get('start', 'Для этой игры не задан начальный текст.')
                            elif location_id in game_data.get('place', {}):
                                location_text = game_data.get('place', {}).get(location_id,
                                                                               'Информация о месте отсутствует')
                            else:
                                location_text = 'По данному делу информации нет'

                            with ui.expansion(f'Шаг {i + 1}: {location_name}', icon='ads_click',
                                              group='location').classes('w-full'):
                                ui.markdown(location_text).classes('whitespace-pre-wrap')
                                if additional_document:
                                    def create_click_handler(doc):
                                        return lambda: self.game_dialog.show_document(doc)

                                    ui.button('Посмотреть вложение', icon='folder_open',
                                              on_click=create_click_handler(additional_document)).classes('mt-2')

                    # Иначе показываем начальный текст
                    elif game_data.get('start'):
                        # При первом запуске игры добавляем начальный текст как первую локацию
                        if not location_history:
                            self.log_service.add_log(
                                level='GAME',
                                message=f"Первый запуск игры для айди {current_room_id}, добавление начальной локации",
                                user_id=user_id,
                                action="ADD_START_LOCATION",
                                metadata={"game_id": current_room_id}
                            )
                            # Используем метод из game_room_management
                            self.game_room_management.add_location_to_history(current_room_id, 'start')
                        ui.markdown(game_data['start']).classes('whitespace-pre-wrap mb-6 text-lg')
                    else:
                        ui.label('Для этой игры не задан начальный текст.').classes('italic text-gray-500 mb-6')

                    with ui.row().classes('w-full justify-between items-center gap-2 mt-4'):
                        # Кнопка перемещения
                        ui.button('Куда хотите пойти?', icon='directions_walk',
                                  on_click=self.game_dialog.show_travel_dialog).classes(
                            'text-lg bg-blue-500 text-white')

                        # Кнопка открытия газеты
                        ui.button('Открыть Газету', icon='description',
                                  on_click=lambda: self.game_dialog.show_newspaper_dialog(game_data)).classes(
                            'text-lg bg-yellow-500 text-white')

                        # Кнопка: Справочник жителей
                        ui.button('Справочник жителей', icon='people',
                                  on_click=lambda: self.game_dialog.show_spravochnik_dialog(game_data, 'people',
                                                                                            game_ui=self,
                                                                                            game_id=current_room_id)).classes(
                            'text-lg bg-blue-500 text-white')

                        # Кнопка: Справочник госструктур
                        ui.button('Справочник госструктур', icon='gavel',
                                  on_click=lambda: self.game_dialog.show_spravochnik_dialog(game_data,
                                                                                            'gosplace', game_ui=self,
                                                                                            game_id=current_room_id)).classes(
                            'text-lg bg-blue-500 text-white')

                        # Кнопка: Справочник общественных мест
                        ui.button('Справочник общественных мест', icon='map',
                                  on_click=lambda: self.game_dialog.show_spravochnik_dialog(game_data,
                                                                                            'obplace', game_ui=self,
                                                                                            game_id=current_room_id)).classes(
                            'text-lg bg-blue-500 text-white')

                        # Кнопка: Обвинить жителя
                        ui.button('Обвинить жителя', icon='report_problem',
                                  on_click=self.game_dialog.show_accuse_dialog).classes(
                            'text-lg bg-purple-600 text-white')

                        # Кнопка выхода из игры (красная)
                        ui.button('Выйти из игры', icon='exit_to_app',
                                  on_click=lambda: self.game_room_management.leave_game(self)).classes(
                            'text-lg bg-red-500 text-white')
        else:
            if self.timer:
                self.timer.cancel()
                self.timer = None

            self.log_service.add_log(
                level='GAME',
                message=f"Показывание интерфейса для законченной игры",
                user_id=user_id,
                action="SHOW_FINISHED_GAME",
                metadata={
                    "game_id": current_room_id,
                    "culprit": game_data['isCulprit']['name'],
                    "moves": room_data['move']
                }
            )

            with self.game_container:
                with ui.card().classes(
                        'w-full max-w-lg mx-auto mt-6 p-6 shadow-lg bg-gray-100 dark:bg-gray-800 rounded-2xl'):
                    ui.label(f'🎉 Игра с ID "{current_room_id}" завершена!').classes(
                        'text-center text-green-600 dark:text-green-400 text-lg font-semibold')

                    # Предполагается, что ты заранее определяешь имя виновного и число ходов
                    culprit_name = game_data['isCulprit']['name']
                    turns_taken = room_data['move']
                    endText = game_data['isCulprit']['endText']

                    ui.label(f'🔍 Виновный: {culprit_name}').classes(
                        'text-center text-gray-800 dark:text-white text-base font-medium mt-4')

                    ui.markdown(endText).classes(
                        'whitespace-pre-wrap text-center text-gray-600 dark:text-gray-300 mb-6'
                    )

                    ui.label(f'⏱ Количество ходов: {turns_taken}').classes(
                        'text-center text-gray-700 dark:text-gray-300 text-base mt-1')

                    self.game_room_management.update_user_game_state(app.storage.user.get('user_id'), None)
                    self.game_room_management.remove_user_from_room(app.storage.user.get('user_id'), current_room_id)
                    app.storage.user.update({'game_state_id': None})

                    ui.button("Вернуться назад", on_click=lambda: ui.navigate.to('/')).classes(
                        'mt-6 bg-blue-600 hover:bg-blue-700 text-white text-lg w-full rounded-lg py-2')
            return

    def check_tooltip(self,room_id):
        room_data = self.game_room_management.get_game_state(room_id)
        game_data = self.game_state_service.get_game_state(room_data['game_id'])
        if game_data['tooltip']['count'] <= room_data['move'] and room_data['tooltip'] == False:
            self.game_room_management.add_location_to_history(room_id, game_data['tooltip']['location_id'], tooltip=True)
            self.log_service.add_debug_log(
                message="Подсказка была добавлена",
                user_id=app.storage.user.get('user_id'),
                action="TOOLTIP",
                metadata={"room_id": room_id}
            )


    def travel_to_location(self, room_id, location_id):
        """Логика перемещения в новую локацию"""
        user_id = app.storage.user.get('user_id')

        if not location_id:
            ui.notify('Укажите ID места', color='warning')
            self.log_service.add_log(
                level='GAME',
                action='ERROR',
                message="Попытка поездки с пустым Айди места",
                user_id=user_id,
                metadata={"room_id": room_id}
            )
            return

        room_data = self.game_room_management.get_game_state(room_id)
        game_data = self.game_state_service.get_game_state(room_data['game_id'])
        spravochnik = game_data.get('spravochnik', {})

        # Проверяем, существует ли место
        if (location_id not in game_data.get('place', {})
                and location_id not in ['112102', '440321', '220123']
                and location_id not in spravochnik.get('obplace', {})
                and location_id not in spravochnik.get('gosplace', {})
                and location_id not in spravochnik.get('people', {})):
            # Используем increment_move из game_room_management вместо прямого обновления
            ui.notify(f'Место с ID {location_id} не найдено', color='negative')

            self.log_service.add_log(
                level='GAME',
                action='ERROR',
                message=f"Локация не найдена: {location_id}",
                user_id=user_id,
                metadata={"room_id": room_id}
            )
            return

        # Используем метод из game_room_management
        success = self.game_room_management.add_location_to_history(room_id, location_id)

        if success:
            ui.notify(f'Вы переместились в локацию {location_id}', color='positive')
            self.log_service.add_log(
                level='GAME',
                message=f"Пользователь успешно переместился в локацию: {location_id}",
                user_id=user_id,
                action="TRAVEL_SUCCESS",
                metadata={"game_id": room_id, "location_id": location_id}
            )

            # Обновляем данные игры
            self.refresh_game_data(room_id)
            # Обновляем только игровой интерфейс
            self.show_game_interface
        else:
            ui.notify('Ошибка при перемещении', color='negative')

            self.log_service.add_error_log(
                error_message="Ошибка при перемещении",
                user_id=user_id,
                metadata={"room_id": room_id, "location_id": location_id}
            )
        self.check_tooltip(room_id)

    def accuse_suspect(self, room_id, suspect_id):
        """Обвинить подозреваемого"""
        user_id = app.storage.user.get('user_id')

        room_data = self.game_room_management.get_game_state(room_id)
        game_data = self.game_state_service.get_game_state(room_data['game_id'])
        culprit = game_data.get('isCulprit', {})

        # Используем метод из game_room_management
        if self.game_room_management.accuse_suspect(room_id, suspect_id):
            # Используем метод из game_room_management для завершения игры
            self.game_room_management.finishing_game(room_id)
            ui.notify('✅ Отличная работа! Вы раскрыли дело и нашли виновного!', color='emerald')

            self.log_service.add_log(
                level='GAME',
                message=f"Пользователь раскрыл дело и нашел виновного: {culprit['name']}",
                user_id=user_id,
                action="ACCUSE_CORRECT",
                metadata={
                    "room_id": room_id,
                    "game_id": room_data['game_id'],
                    "suspect_id": suspect_id,
                    "moves": game_data.get('move', 0) + 1
                }
            )
        else:
            ui.notify('❌ Увы, это был не тот человек! Попробуйте ещё раз.', color='rose')

            self.log_service.add_log(
                level='GAME',
                message=f"Пользователь не правильно предположил {suspect_id}",
                user_id=user_id,
                action="ACCUSE_INCORRECT",
                metadata={
                    "room_id": room_id,
                    "game_id": room_data['game_id'],
                    "suspect_id": suspect_id,
                    "actual_culprit": culprit['id']
                }
            )

        # Используем метод из game_room_management
        self.game_room_management.increment_move(room_id)
        self.show_game_interface


    # Вспомогательная функция для проверки существования игры
    def game_id_exists(self, room_id):
        """Проверяет существование игры по ID через game_state_service"""
        if not room_id:
            return False

        # Здесь предполагается, что в реальном коде будет использоваться
        # game_state_service.game_exists() из класса GameStateService
        # или аналогичная функция из GameRoomManagement
        return self.game_room_management.room_exists(room_id)