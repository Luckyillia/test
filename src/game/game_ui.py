from nicegui import ui, app

from src.game.game_state_service import GameStateService
from src.game.game_dialog import GameDialog
from src.game.game_room_management import GameRoomManagement


class GameUI:
    def __init__(self):
        self.game_state_service = GameStateService(self)
        self.game_dialog = GameDialog(self)
        self.game_room_management = GameRoomManagement(self.game_state_service)
        self.available_games = {}
        self.load_available_games()
        self.last_update = 0
        ui.timer(interval=1.0, callback=self.game_state_service.check_for_updates)

    def load_available_games(self):
        try:
            self.available_games = self.game_state_service.load()
        except Exception as e:
            ui.notify(f'Ошибка загрузки игр: {str(e)}', color='negative')
            self.available_games = {}

    @ui.refreshable
    def display_games_list(self):
        """Динамически обновляемый список игр"""
        if self.available_games:
            for game_id in self.available_games.keys():  # Изменено: итерируем по ключам
                current_game_data = self.game_state_service.get_game_state(game_id)  # Получаем данные для каждой игры

                with ui.card().classes('w-full p-4'):
                    with ui.expansion(f'Айди игры: {game_id}', icon='description').classes('w-full'):
                        with ui.column().classes('w-full'):
                            with ui.row().classes('w-full items-center mb-4'):
                                # Кнопка обновления данных
                                ui.button('Обновить данные', icon='refresh', on_click=lambda gid=game_id: [
                                    self.load_available_games(),
                                    self.display_games_list.refresh(),
                                    ui.notify('Данные обновлены')
                                ]).classes('ml-auto')

                                # Кнопка удаления игры
                                ui.button('Удалить игру', icon='delete', color='red', on_click=lambda gid=game_id: [
                                    self.game_state_service.delete_game_state(gid),
                                    app.storage.user.update({'game_state_id': None}),
                                    self.load_available_games(),
                                    self.display_games_list.refresh(),
                                    ui.notify('Игра удалена'),
                                ])

                                # Газета
                                with ui.expansion('Газета', icon='description').classes('w-full'):
                                    def refresh_gazeta(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid)
                                        content_container.clear()
                                        with content_container:
                                            if current_data.get('gazeta'):
                                                ui.markdown(current_data['gazeta']).classes('whitespace-pre-wrap')
                                            gazeta_input = ui.textarea('Редактировать газету').classes('w-full')
                                            gazeta_input.value = ''
                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.edit_gazeta(gid, gazeta_input.value),
                                                    refresh_gazeta(),
                                                    ui.notify('Газета обновлена')
                                                ]
                                            )

                                    content_container = ui.column().classes('w-full')
                                    refresh_gazeta()

                                # Справочник: Люди
                                with ui.expansion('Справочник: Люди', icon='people').classes('w-full'):
                                    def refresh_people(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid)
                                        people_container.clear()
                                        with people_container:
                                            for person in current_data.get('spravochnik', {}).get('people', []):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label(person).classes('whitespace-pre-wrap')
                                            new_person_input = ui.textarea('Добавить человека').classes('w-full')
                                            ui.button(
                                                'Добавить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_people(gid, new_person_input.value),
                                                    refresh_people(),
                                                    new_person_input.set_value(''),
                                                    ui.notify('Добавлено в справочник')
                                                ]
                                            )

                                    people_container = ui.column().classes('w-full')
                                    refresh_people()

                                # Справочник: Гос. места
                                with ui.expansion('Справочник: Гос. места', icon='account_balance').classes('w-full'):
                                    def refresh_gosplaces(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid)
                                        gosplaces_container.clear()
                                        with gosplaces_container:
                                            for place in current_data.get('spravochnik', {}).get('gosplace', []):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label(place).classes('whitespace-pre-wrap')
                                            new_gosplace_input = ui.textarea('Добавить гос. место').classes('w-full')
                                            ui.button(
                                                'Добавить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_gosplace(gid, new_gosplace_input.value),
                                                    refresh_gosplaces(),
                                                    new_gosplace_input.set_value(''),
                                                    ui.notify('Добавлено в справочник')
                                                ]
                                            )

                                    gosplaces_container = ui.column().classes('w-full')
                                    refresh_gosplaces()

                                # Справочник: Общественные места
                                with ui.expansion('Справочник: Общественные места', icon='store').classes('w-full'):
                                    def refresh_obplaces(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid)
                                        obplaces_container.clear()
                                        with obplaces_container:
                                            for place in current_data.get('spravochnik', {}).get('obplace', []):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label(place).classes('whitespace-pre-wrap')
                                            new_obplace_input = ui.textarea('Добавить общественное место').classes(
                                                'w-full')
                                            ui.button(
                                                'Добавить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_obplace(gid, new_obplace_input.value),
                                                    refresh_obplaces(),
                                                    new_obplace_input.set_value(''),
                                                    ui.notify('Добавлено в справочник')
                                                ]
                                            )

                                    obplaces_container = ui.column().classes('w-full')
                                    refresh_obplaces()

                                # Полиция
                                with ui.expansion('Полиция (112102)', icon='local_police').classes('w-full'):
                                    def refresh_police(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid).get('112102', {})
                                        police_container.clear()
                                        with police_container:
                                            # Показываем текущие данные как markdown
                                            if current_data.get('text'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label('Текст:').classes('font-bold')
                                                    ui.markdown(current_data.get('text', '')).classes(
                                                        'whitespace-pre-wrap')

                                            if current_data.get('delo'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label('Дело:').classes('font-bold')
                                                    ui.markdown(current_data.get('delo', '')).classes(
                                                        'whitespace-pre-wrap')

                                            # Поля для редактирования
                                            police_text_input = ui.textarea('Редактировать текст').classes('w-full')
                                            police_text_input.value = ''
                                            police_delo_input = ui.textarea('Редактировать дело').classes('w-full mt-2')
                                            police_delo_input.value = ''
                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_police(
                                                        gid,
                                                        text=police_text_input.value,
                                                        delo=police_delo_input.value
                                                    ),
                                                    refresh_police(),
                                                    ui.notify('Полиция обновлена')
                                                ]
                                            ).classes('mt-2')

                                    police_container = ui.column().classes('w-full')
                                    refresh_police()

                                # Морг
                                with ui.expansion('Морг (440321)', icon='sick').classes('w-full'):
                                    def refresh_morg(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid).get('440321', {})
                                        morg_container.clear()
                                        with morg_container:
                                            # Показываем текущие данные как markdown
                                            if current_data.get('text'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label('Текст:').classes('font-bold')
                                                    ui.markdown(current_data.get('text', '')).classes(
                                                        'whitespace-pre-wrap')

                                            if current_data.get('vskrytie'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label('Вскрытие:').classes('font-bold')
                                                    ui.markdown(current_data.get('vskrytie', '')).classes(
                                                        'whitespace-pre-wrap')

                                            # Поля для редактирования
                                            morg_text_input = ui.textarea('Редактировать текст').classes('w-full')
                                            morg_text_input.value = current_data.get('text', '')
                                            morg_vskrytie_input = ui.textarea('Редактировать вскрытие').classes(
                                                'w-full mt-2')
                                            morg_vskrytie_input.value = ''
                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_morg(
                                                        gid,
                                                        text=morg_text_input.value,
                                                        vskrytie=morg_vskrytie_input.value
                                                    ),
                                                    refresh_morg(),
                                                    ui.notify('Морг обновлен')
                                                ]
                                            ).classes('mt-2')

                                    morg_container = ui.column().classes('w-full')
                                    refresh_morg()

                                # ЗАГС
                                with ui.expansion('ЗАГС (220123)', icon='assignment').classes('w-full'):
                                    def refresh_zags(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid).get('220123', {})
                                        zags_container.clear()
                                        with zags_container:
                                            # Показываем текущие данные как markdown
                                            if current_data.get('text'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label('Текст:').classes('font-bold')
                                                    ui.markdown(current_data.get('text', '')).classes(
                                                        'whitespace-pre-wrap')

                                            if current_data.get('otchet'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label('Отчет:').classes('font-bold')
                                                    ui.markdown(current_data.get('otchet', '')).classes(
                                                        'whitespace-pre-wrap')

                                            # Поля для редактирования
                                            zags_text_input = ui.textarea('Редактировать текст').classes('w-full')
                                            zags_text_input.value = ''
                                            zags_otchet_input = ui.textarea('Редактировать отчет').classes(
                                                'w-full mt-2')
                                            zags_otchet_input.value = ''
                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_zags(
                                                        gid,
                                                        text=zags_text_input.value,
                                                        otchet=zags_otchet_input.value
                                                    ),
                                                    refresh_zags(),
                                                    ui.notify('ЗАГС обновлен')
                                                ]
                                            ).classes('mt-2')

                                    zags_container = ui.column().classes('w-full')
                                    refresh_zags()

                                # Другие места
                                with ui.expansion('Другие места', icon='place').classes('w-full'):
                                    def refresh_places(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid).get('place', {})
                                        places_container.clear()
                                        with places_container:
                                            for place_id, place_text in current_data.items():
                                                with ui.card().classes('w-full mb-4 p-3'):
                                                    ui.label(f'ID: {place_id}').classes('font-bold')
                                                    ui.markdown(place_text).classes('whitespace-pre-wrap')
                                            with ui.card().classes('w-full p-4 bg-blue-50 dark:bg-blue-900'):
                                                place_id_input = ui.input('ID места').classes('w-full')
                                                place_text_input = ui.textarea('Описание места').classes('w-full mt-2')
                                                ui.button(
                                                    'Добавить',
                                                    on_click=lambda: [
                                                        self.game_state_service.add_place(
                                                            gid,
                                                            place_id_input.value,
                                                            place_text_input.value
                                                        ),
                                                        refresh_places(),
                                                        place_id_input.set_value(''),
                                                        place_text_input.set_value(''),
                                                        ui.notify('Место добавлено')
                                                    ]
                                                ).classes('mt-2')

                                    places_container = ui.column().classes('w-full')
                                    refresh_places()

                                # Начальный текст
                                with ui.expansion('Начальный текст', icon='text_format').classes('w-full'):
                                    def refresh_begin_text(gid=game_id):
                                        current_data = self.game_state_service.get_game_state(gid)
                                        begin_text_container.clear()
                                        with begin_text_container:
                                            # Показываем текущий текст как markdown
                                            if current_data.get('beginText'):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.markdown(current_data.get('beginText', '')).classes(
                                                        'whitespace-pre-wrap')

                                            # Поле для редактирования
                                            begin_text_input = ui.textarea('Редактировать начальный текст').classes(
                                                'w-full')
                                            begin_text_input.value = ''
                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.ensure_game_exists(gid),
                                                    data := self.game_state_service.load(),
                                                    data.__setitem__(gid, {**data[gid],
                                                                           'beginText': begin_text_input.value}),
                                                    self.game_state_service.save(data),
                                                    refresh_begin_text(),
                                                    ui.notify('Начальный текст сохранен')
                                                ]
                                            ).classes('mt-2')

                                    begin_text_container = ui.column().classes('w-full')
                                    refresh_begin_text()
        else:
            ui.label('Выберите игру из списка выше или создайте новую').classes(
                'text-center w-full p-8 text-gray-500 italic')

    def refresh_game_data(self, game_id):
        self.game_data = self.game_state_service.get_game_state(game_id)
        ui.update()
        return self.game_data

    def table_game(self):
        with ui.card().classes('w-full p-4 bg-blue-50 dark:bg-blue-900'):
            ui.label('Создать новую игру').classes('font-bold mb-2')
            game_id_input = ui.input('Айди игры')

            def create_game():
                game_id = game_id_input.value.strip()

                # Проверка на пустое значение
                if not game_id:
                    ui.notify('ID игры не может быть пустым', color='negative')
                    return

                # Проверка на существование игры с таким же ID
                if game_id in self.available_games:
                    ui.notify(f'Игра с ID "{game_id}" уже существует', color='negative')
                    return

                # Создание новой игры
                try:
                    self.game_state_service.create_game_state(game_id)
                    app.storage.user.update({'game_state_id': game_id})
                    self.refresh_game_data(game_id)
                    self.load_available_games()
                    self.display_games_list.refresh()
                    ui.notify('Игра успешно создана', color='positive')
                    game_id_input.set_value('')  # Очистка поля после создания
                except Exception as e:
                    ui.notify(f'Ошибка при создании игры: {str(e)}', color='negative')

            ui.button('Создать Игру', on_click=create_game).classes('mt-2')

        self.display_games_list()

    def show_game_interface(self):
        """Отображает игровой интерфейс для пользователя, если у него выбрана игра"""
        # Создаем или получаем контейнер для игрового интерфейса
        if hasattr(self, 'game_container'):
            self.game_container.clear()
        else:
            self.game_container = ui.element('div').classes('w-full')

        current_game_id = app.storage.user.get('game_state_id')

        if not current_game_id:
            with self.game_container:
                with ui.card().classes('w-full max-w-lg mx-auto mt-6 p-6 shadow-lg bg-gray-100 rounded-2xl'):
                    ui.label('У вас нет активной игры').classes('text-xl font-semibold text-center text-gray-800 mb-2')
                    ui.label('Пожалуйста, войдите в существующую игру или создайте новую.').classes(
                        'text-center text-gray-600 mb-4')
                    ui.button('Войти в игру', on_click=self.game_room_management.show_join_game_dialog).classes(
                        'bg-blue-500 text-white text-lg w-full')
            return

        if current_game_id not in self.available_games:
            with self.game_container:
                with ui.card().classes('p-6 max-w-xl mx-auto mt-10 shadow-lg rounded-xl bg-white'):
                    ui.label(f'⚠️ Игра с ID "{current_game_id}" не найдена.').classes('text-center text-red-600 text-lg font-semibold')

                    ui.label('Проверьте правильность ID или выберите другую игру.').classes('text-center text-gray-500 mt-2')

                    self.game_room_management.update_user_game_state(app.storage.user.get('user_id'), None)
                    app.storage.user.update({'game_state_id': None})

                    ui.button("Вернуться назад", on_click=lambda: ui.navigate.to('/')).classes(
                        'mt-6 bg-blue-600 hover:bg-blue-700 text-white text-lg w-full rounded-lg py-2')
            return

        game_data = self.refresh_game_data(current_game_id)

        with self.game_container:
            with ui.card().classes('w-full p-6 bg-gray-50 dark:bg-gray-800'):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Игровой интерфейс').classes('text-xl font-bold')
                    ui.label(f'Ходов: {game_data.get("move", 0)}').classes('text-right text-sm text-gray-600')

                # Получаем историю локаций
                location_history = self.game_state_service.get_location_history(current_game_id)
                current_location = self.game_state_service.get_current_location(current_game_id)

                # Если есть история локаций, показываем последнюю
                if location_history:
                    for i, location in enumerate(location_history):
                        with ui.card().classes('w-full mb-4 p-3'):
                            ui.label(f'Шаг {i + 1}: Локация {location["id"]}').classes('font-bold mb-2')
                            ui.markdown(location['text']).classes('whitespace-pre-wrap')
                            if location.get('additional_document'):
                                # Создаем функцию, которая захватывает текущее значение документа
                                def create_click_handler(doc):
                                    return lambda: self.game_dialog.show_document(doc)

                                # Используем эту функцию для создания обработчика для каждой кнопки
                                ui.button('Посмотреть вложение', icon='folder_open',
                                          on_click=create_click_handler(location['additional_document'])).classes(
                                    'mt-2')
                # Иначе показываем начальный текст
                elif game_data.get('beginText'):
                    # При первом запуске игры добавляем начальный текст как первую локацию
                    if not location_history:
                        self.game_state_service.add_location_to_history(
                            current_game_id,
                            'start',
                            game_data['beginText']
                        )
                    ui.markdown(game_data['beginText']).classes('whitespace-pre-wrap mb-6 text-lg')
                else:
                    ui.label('Для этой игры не задан начальный текст.').classes('italic text-gray-500 mb-6')

                with ui.row().classes('w-full justify-between items-center gap-2 mt-4'):
                    # Кнопка перемещения
                    ui.button('Куда хотите пойти?', icon='directions_walk',
                              on_click=self.game_dialog.show_travel_dialog).classes('text-lg bg-blue-500 text-white')

                    # Кнопка открытия газеты
                    ui.button('Открыть Газету', icon='description',
                              on_click=lambda: self.game_dialog.show_newspaper_dialog(game_data)).classes(
                        'text-lg bg-yellow-500 text-white')

                    # Кнопка: Справочник жителей
                    ui.button('Справочник жителей', icon='people',
                              on_click=lambda: self.game_dialog.show_spravochnik_dialog(game_data, 'people')).classes(
                        'text-lg bg-blue-500 text-white')

                    # Кнопка: Справочник госструктур
                    ui.button('Справочник госструктур', icon='gavel',
                              on_click=lambda: self.game_dialog.show_spravochnik_dialog(game_data, 'gosplace')).classes(
                        'text-lg bg-blue-500 text-white')

                    # Кнопка: Справочник общественных мест
                    ui.button('Справочник общественных мест', icon='map',
                              on_click=lambda: self.game_dialog.show_spravochnik_dialog(game_data, 'obplace')).classes(
                        'text-lg bg-blue-500 text-white')

                    # Кнопка выхода из игры (красная)
                    ui.button('Выйти из игры', icon='exit_to_app',
                              on_click=self.game_room_management.leave_game).classes(
                        'text-lg bg-red-500 text-white')

    def travel_to_location(self, game_id, location_id):
        """Логика перемещения в новую локацию"""
        if not location_id:
            ui.notify('Укажите ID места', color='warning')
            return

        # Получаем данные о месте
        game_data = self.game_state_service.get_game_state(game_id)
        location_text = None
        additional_document = None

        # Проверяем специальные места
        if location_id == '112102':  # Полиция
            location_text = game_data.get('112102', {}).get('text', 'Информация о полиции отсутствует')
            additional_document = game_data.get('112102', {}).get('delo', None)
        elif location_id == '440321':  # Морг
            location_text = game_data.get('440321', {}).get('text', 'Информация о морге отсутствует')
            additional_document = game_data.get('440321', {}).get('vskrytie', None)
        elif location_id == '220123':  # ЗАГС
            location_text = game_data.get('220123', {}).get('text', 'Информация о ЗАГСе отсутствует')
            additional_document = game_data.get('220123', {}).get('otchet', None)
        else:
            # Проверяем обычные места
            locations = game_data.get('place', {})
            if location_id in locations:
                location_text = locations[location_id]
            else:
                ui.notify(f'Место с ID {location_id} не найдено', color='negative')
                return

        # Добавляем в историю перемещений
        success = self.game_state_service.add_location_to_history(game_id, location_id, location_text, additional_document)

        if success:
            ui.notify(f'Вы переместились в локацию {location_id}', color='positive')
            # Обновляем данные игры
            self.refresh_game_data(game_id)
            # Обновляем только игровой интерфейс
            self.show_game_interface()
        else:
            ui.notify('Ошибка при перемещении', color='negative')