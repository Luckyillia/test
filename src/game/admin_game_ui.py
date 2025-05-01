from nicegui import ui, app

from src.game.game_state_service import GameStateService
from src.game.game_room_management import GameRoomManagement
from src.services.log_services import LogService


class AdminGameUI:
    def __init__(self):
        self.game_state_service = GameStateService()
        self.game_room_management = GameRoomManagement()
        self.log_service = LogService()
        self.available_games = {}
        self.load_available_games()
        # Данные о комнатах и играх
        self.display_container = None

    def load_available_games(self):
        try:
            self.available_games = self.game_state_service.load()
        except Exception as e:
            error_message = f'Ошибка загрузки игр: {str(e)}'
            ui.notify(error_message, color='negative')
            self.log_service.add_log(
                level='ADMIN_GAME',
                action='ERROR',
                message=error_message,
                user_id=app.storage.user.get('user_id', None),
                metadata={"action": "load_available_games"}
            )
            self.available_games = {}

    def validate_fields(self, *fields, field_names=None):
        if field_names is None:
            field_names = ["Поле"] * len(fields)

        for i, field in enumerate(fields):
            if not field.value or (isinstance(field.value, str) and field.value.strip() == ""):
                error_message = f'Поле "{field_names[i]}" не заполнено!'
                ui.notify(error_message, color='negative')
                self.log_service.add_log(
                    level='ADMIN_GAME',
                    action='ERROR',
                    message=error_message,
                    user_id=app.storage.user.get('user_id', None),
                    metadata={"field_name": field_names[i], "action": "validate_fields"}
                )
                return False
        return True

    def create_game_cards(self):
        """Динамически обновляемый список игр"""
        if self.available_games:
            with self.display_container:
                for game_id in self.available_games.keys():
                    with ui.card().classes('w-full p-4'):
                        with ui.expansion(f'Айди игры: {game_id}', icon='description', group='ADMIN_GAME').classes('w-full'):
                            with ui.column().classes('w-full'):
                                with ui.row().classes('w-full items-center mb-4'):
                                    # Кнопка обновления данных
                                    ui.button('Обновить данные', icon='refresh', on_click=lambda gid=game_id: [
                                        self.load_available_games(),
                                        self.refresh_ui(),
                                        ui.notify('Данные обновлены'),
                                        self.log_service.add_log(
                                            level='ADMIN_GAME',
                                            user_id=app.storage.user.get('user_id', None),
                                            action="ADMIN_GAME_REFRESH_GAME",
                                            message=f"Администратор обновил данные игры {gid}",
                                            metadata={"game_id": gid}
                                        )
                                    ]).classes('ml-auto')

                                    # Кнопка удаления игры
                                    ui.button('Удалить игру', icon='delete', color='red', on_click=lambda gid=game_id: [
                                        self.game_state_service.delete_game_state(gid),
                                        app.storage.user.update({'game_state_id': None}),
                                        self.load_available_games(),
                                        self.refresh_ui(),
                                        ui.notify('Игра удалена'),
                                        self.log_service.add_log(
                                            level='ADMIN_GAME',
                                            user_id=app.storage.user.get('user_id', None),
                                            action="ADMIN_GAME_DELETE_GAME",
                                            message=f"Администратор удалил игру {gid}",
                                            metadata={"game_id": gid}
                                        )
                                    ])
                                    # Начальный текст
                                    with ui.expansion('Начальный текст', icon='text_format', group='element').classes(
                                            'w-full'):
                                        def refresh_begin_text(gid=game_id):
                                            current_data = self.game_state_service.get_game_state(gid)
                                            begin_text_container.clear()
                                            with begin_text_container:
                                                # Показываем текущий текст как markdown
                                                if current_data and current_data.get('start'):
                                                    with ui.card().classes('w-full mb-2 p-3'):
                                                        ui.markdown(current_data.get('start', '')).classes(
                                                            'whitespace-pre-wrap')

                                                # Поле для редактирования
                                                begin_text_input = ui.textarea('Редактировать начальный текст').classes(
                                                    'w-full')
                                                begin_text_input.value = current_data.get('start', '')

                                                def save_begin_text():
                                                    if not self.validate_fields(begin_text_input,
                                                                                field_names=["Начальный текст"]):
                                                        return

                                                    self.game_state_service.ensure_game_exists(gid)
                                                    data = self.game_state_service.load()
                                                    data[gid] = {**data[gid], 'start': begin_text_input.value}
                                                    self.game_state_service.save(data)
                                                    begin_text_input.set_value('')
                                                    self.load_available_games()
                                                    refresh_begin_text()
                                                    ui.notify('Начальный текст сохранен')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_EDIT_START_TEXT",
                                                        message=f"Администратор изменил начальный текст игры {gid}",
                                                        metadata={"game_id": gid}
                                                    )

                                                ui.button(
                                                    'Сохранить',
                                                    on_click=save_begin_text
                                                ).classes('mt-2')

                                        begin_text_container = ui.column().classes('w-full')
                                        refresh_begin_text()

                                    # Газета
                                    with ui.expansion('Газета', icon='description', group='element').classes('w-full'):
                                        def refresh_gazeta(gid=game_id):
                                            current_data = self.game_state_service.get_game_state(gid)
                                            content_container.clear()
                                            with content_container:
                                                if current_data.get('gazeta'):
                                                    ui.markdown(current_data['gazeta']).classes('whitespace-pre-wrap')
                                                gazeta_input = ui.textarea('Редактировать газету').classes('w-full')
                                                gazeta_input.value = current_data.get('gazeta', '')

                                                def save_gazeta():
                                                    if not self.validate_fields(gazeta_input, field_names=["Текст газеты"]):
                                                        return

                                                    self.game_state_service.edit_gazeta(gid, gazeta_input.value)
                                                    gazeta_input.set_value('')
                                                    self.load_available_games()
                                                    refresh_gazeta()
                                                    ui.notify('Газета обновлена')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_EDIT_GAZETA",
                                                        message=f"Администратор изменил текст газеты в игре {gid}",
                                                        metadata={"game_id": gid}
                                                    )

                                                ui.button(
                                                    'Сохранить',
                                                    on_click=save_gazeta
                                                )

                                        content_container = ui.column().classes('w-full')
                                        refresh_gazeta()

                                    # Справочник: Люди
                                    with ui.expansion('Справочник: Люди', icon='people', group='element').classes('w-full'):
                                        def refresh_people(gid=game_id):
                                            current_data = self.game_state_service.get_game_state(gid)
                                            people_container.clear()
                                            with people_container:
                                                for person_id, person_text in current_data.get('spravochnik', {}).get(
                                                        'people', {}).items():
                                                    with ui.card().classes('w-full mb-2 p-3'):
                                                        ui.label(f'**{person_id}**: {person_text}').classes(
                                                            'whitespace-pre-wrap')
                                                new_person_input_id = ui.input('ID человека').classes('w-full')
                                                new_person_input_text = ui.textarea('Добавить человека').classes('w-full')

                                                def add_person():
                                                    if not self.validate_fields(
                                                            new_person_input_id, new_person_input_text,
                                                            field_names=["ID человека", "Описание человека"]
                                                    ):
                                                        return

                                                    person_id = new_person_input_id.value
                                                    self.game_state_service.add_people(
                                                        gid, person_id, new_person_input_text.value
                                                    )
                                                    new_person_input_id.set_value('')
                                                    new_person_input_text.set_value('')
                                                    self.load_available_games()
                                                    refresh_people()
                                                    ui.notify('Добавлено в справочник')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_ADD_PERSON",
                                                        message=f"Администратор добавил человека '{person_id}' в игру {gid}",
                                                        metadata={"game_id": gid, "person_id": person_id}
                                                    )

                                                ui.button(
                                                    'Добавить',
                                                    on_click=add_person
                                                )

                                        people_container = ui.column().classes('w-full')
                                        refresh_people()

                                    # Справочник: Гос. места
                                    with ui.expansion('Справочник: Гос. места', icon='account_balance',
                                                      group='element').classes('w-full'):
                                        def refresh_gosplaces(gid=game_id):
                                            current_data = self.game_state_service.get_game_state(gid)
                                            gosplaces_container.clear()
                                            with gosplaces_container:
                                                for place_id, place_text in current_data.get('spravochnik', {}).get(
                                                        'gosplace', {}).items():
                                                    with ui.card().classes('w-full mb-2 p-3'):
                                                        ui.label(f'**{place_id}**: {place_text}').classes(
                                                            'whitespace-pre-wrap')
                                                new_gosplace_input_id = ui.input('ID гос. места').classes('w-full')
                                                new_gosplace_input_text = ui.textarea('Добавить гос. место').classes(
                                                    'w-full')

                                                def add_gosplace():
                                                    if not self.validate_fields(
                                                            new_gosplace_input_id, new_gosplace_input_text,
                                                            field_names=["ID гос. места", "Описание гос. места"]
                                                    ):
                                                        return

                                                    place_id = new_gosplace_input_id.value
                                                    self.game_state_service.add_gosplace(
                                                        gid, place_id, new_gosplace_input_text.value
                                                    )
                                                    new_gosplace_input_id.set_value('')
                                                    new_gosplace_input_text.set_value('')
                                                    self.load_available_games()
                                                    refresh_gosplaces()
                                                    ui.notify('Добавлено в справочник')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_ADD_GOSPLACE",
                                                        message=f"Администратор добавил гос. место '{place_id}' в игру {gid}",
                                                        metadata={"game_id": gid, "place_id": place_id}
                                                    )

                                                ui.button(
                                                    'Добавить',
                                                    on_click=add_gosplace
                                                )

                                        gosplaces_container = ui.column().classes('w-full')
                                        refresh_gosplaces()

                                    # Справочник: Общественные места
                                    with ui.expansion('Справочник: Общественные места', icon='store',
                                                      group='element').classes('w-full'):
                                        def refresh_obplaces(gid=game_id):
                                            current_data = self.game_state_service.get_game_state(gid)
                                            obplaces_container.clear()
                                            with obplaces_container:
                                                for place_id, place_text in current_data.get('spravochnik', {}).get(
                                                        'obplace', {}).items():
                                                    with ui.card().classes('w-full mb-2 p-3'):
                                                        ui.label(f'**{place_id}**: {place_text}').classes(
                                                            'whitespace-pre-wrap')
                                                new_obplace_input_id = ui.input('ID общественного места').classes('w-full')
                                                new_obplace_input_text = ui.textarea('Добавить общественное место').classes(
                                                    'w-full')

                                                def add_obplace():
                                                    if not self.validate_fields(
                                                            new_obplace_input_id, new_obplace_input_text,
                                                            field_names=["ID общественного места",
                                                                         "Описание общественного места"]
                                                    ):
                                                        return

                                                    place_id = new_obplace_input_id.value
                                                    self.game_state_service.add_obplace(
                                                        gid, place_id, new_obplace_input_text.value
                                                    )
                                                    new_obplace_input_id.set_value('')
                                                    new_obplace_input_text.set_value('')
                                                    self.load_available_games()
                                                    refresh_obplaces()
                                                    ui.notify('Добавлено в справочник')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_ADD_OBPLACE",
                                                        message=f"Администратор добавил общественное место '{place_id}' в игру {gid}",
                                                        metadata={"game_id": gid, "place_id": place_id}
                                                    )

                                                ui.button(
                                                    'Добавить',
                                                    on_click=add_obplace
                                                )

                                        obplaces_container = ui.column().classes('w-full')
                                        refresh_obplaces()

                                    # Полиция
                                    with ui.expansion('Полиция (112102)', icon='local_police', group='element').classes(
                                            'w-full'):
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
                                                police_text_input.value = current_data.get('text', '')
                                                police_delo_input = ui.textarea('Редактировать дело').classes('w-full mt-2')
                                                police_delo_input.value = current_data.get('delo', '')

                                                def save_police():
                                                    # Здесь можно оставить необязательным поле "дело"
                                                    if not self.validate_fields(
                                                            police_text_input,
                                                            field_names=["Текст полиции"]
                                                    ):
                                                        return

                                                    self.game_state_service.add_police(
                                                        gid,
                                                        text=police_text_input.value,
                                                        delo=police_delo_input.value
                                                    )
                                                    police_text_input.set_value('')
                                                    police_delo_input.set_value('')
                                                    self.load_available_games()
                                                    refresh_police()
                                                    ui.notify('Полиция обновлена')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_UPDATE_POLICE",
                                                        message=f"Администратор обновил данные полиции в игре {gid}",
                                                        metadata={"game_id": gid, "has_delo": bool(police_delo_input.value)}
                                                    )

                                                ui.button(
                                                    'Сохранить',
                                                    on_click=save_police
                                                ).classes('mt-2')

                                        police_container = ui.column().classes('w-full')
                                        refresh_police()

                                    # Морг
                                    with ui.expansion('Морг (440321)', icon='sick', group='element').classes('w-full'):
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
                                                morg_vskrytie_input.value = current_data.get('vskrytie', '')

                                                def save_morg():
                                                    # Здесь текст обязателен, вскрытие - опционально
                                                    if not self.validate_fields(
                                                            morg_text_input,
                                                            field_names=["Текст морга"]
                                                    ):
                                                        return

                                                    self.game_state_service.add_morg(
                                                        gid,
                                                        text=morg_text_input.value,
                                                        vskrytie=morg_vskrytie_input.value
                                                    )
                                                    morg_text_input.set_value('')
                                                    morg_vskrytie_input.set_value('')
                                                    self.load_available_games()
                                                    refresh_morg()
                                                    ui.notify('Морг обновлен')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_UPDATE_MORG",
                                                        message=f"Администратор обновил данные морга в игре {gid}",
                                                        metadata={"game_id": gid, "has_vskrytie": bool(morg_vskrytie_input.value)}
                                                    )

                                                ui.button(
                                                    'Сохранить',
                                                    on_click=save_morg
                                                ).classes('mt-2')

                                        morg_container = ui.column().classes('w-full')
                                        refresh_morg()

                                    # ЗАГС
                                    with ui.expansion('ЗАГС (220123)', icon='assignment', group='element').classes(
                                            'w-full'):
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
                                                zags_text_input.value = current_data.get('text', '')
                                                zags_otchet_input = ui.textarea('Редактировать отчет').classes(
                                                    'w-full mt-2')
                                                zags_otchet_input.value = current_data.get('otchet', '')

                                                def save_zags():
                                                    # Текст обязательный, отчет - опциональный
                                                    if not self.validate_fields(
                                                            zags_text_input,
                                                            field_names=["Текст ЗАГСа"]
                                                    ):
                                                        return

                                                    self.game_state_service.add_zags(
                                                        gid,
                                                        text=zags_text_input.value,
                                                        otchet=zags_otchet_input.value
                                                    )
                                                    zags_text_input.set_value('')
                                                    zags_otchet_input.set_value('')
                                                    self.load_available_games()
                                                    refresh_zags()
                                                    ui.notify('ЗАГС обновлен')
                                                    self.log_service.add_log(
                                                        level='ADMIN_GAME',
                                                        user_id=app.storage.user.get('user_id', None),
                                                        action="ADMIN_GAME_UPDATE_ZAGS",
                                                        message=f"Администратор обновил данные ЗАГСа в игре {gid}",
                                                        metadata={"game_id": gid, "has_otchet": bool(zags_otchet_input.value)}
                                                    )

                                                ui.button(
                                                    'Сохранить',
                                                    on_click=save_zags
                                                ).classes('mt-2')

                                        zags_container = ui.column().classes('w-full')
                                        refresh_zags()

                                    # Другие места
                                    with ui.expansion('Другие места', icon='place', group='element').classes('w-full'):
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

                                                    def add_place():
                                                        if not self.validate_fields(
                                                                place_id_input, place_text_input,
                                                                field_names=["ID места", "Описание места"]
                                                        ):
                                                            return

                                                        place_id = place_id_input.value
                                                        self.game_state_service.add_place(
                                                            gid,
                                                            place_id,
                                                            place_text_input.value
                                                        )
                                                        place_id_input.set_value('')
                                                        place_text_input.set_value('')
                                                        self.load_available_games()
                                                        refresh_places()
                                                        ui.notify('Место добавлено')
                                                        self.log_service.add_log(
                                                            level='ADMIN_GAME',
                                                            user_id=app.storage.user.get('user_id', None),
                                                            action="ADMIN_GAME_ADD_PLACE",
                                                            message=f"Администратор добавил место '{place_id}' в игру {gid}",
                                                            metadata={"game_id": gid, "place_id": place_id}
                                                        )

                                                    ui.button(
                                                        'Добавить',
                                                        on_click=add_place
                                                    ).classes('mt-2')

                                        places_container = ui.column().classes('w-full')
                                        refresh_places()

                                    with ui.expansion('Виновный', icon='report_problem', group='element').classes('w-full'):
                                        def refresh_culprit(gid=game_id):
                                            current_data = self.game_state_service.get_game_state(gid).get('isCulprit', {})
                                            culprit_container.clear()
                                            with culprit_container:
                                                if current_data.get('id') and current_data.get('name') and current_data.get(
                                                        'endText'):
                                                    with ui.card().classes('w-full mb-4 p-3'):
                                                        ui.label(f'ID: {current_data["id"]}').classes('font-bold')
                                                        ui.label(current_data['name']).classes('whitespace-pre-wrap')
                                                    with ui.card().classes('w-full mb-4 p-3'):
                                                        ui.markdown(current_data.get('endText', '')).classes(
                                                            'whitespace-pre-wrap')
                                                with ui.card().classes('w-full p-4 bg-blue-50 dark:bg-blue-900'):
                                                    culprit_id_input = ui.input('ID виновного').classes('w-full')
                                                    culprit_text_input = ui.textarea('Название виновного').classes(
                                                        'w-full mt-2')
                                                    culprit_endtext_input = ui.textarea('Финальный текст').classes(
                                                        'w-full mt-2')

                                                    def add_culprit():
                                                        if not self.validate_fields(
                                                                culprit_id_input, culprit_text_input, culprit_endtext_input,
                                                                field_names=["ID виновного", "Название виновного",
                                                                             "Финальный текст"]
                                                        ):
                                                            return

                                                        culprit_id = culprit_id_input.value
                                                        self.game_state_service.edit_culprit(
                                                            gid,
                                                            culprit_id,
                                                            culprit_text_input.value,
                                                            culprit_endtext_input.value
                                                        )
                                                        culprit_id_input.set_value('')
                                                        culprit_text_input.set_value('')
                                                        culprit_endtext_input.set_value('')
                                                        self.load_available_games()
                                                        refresh_culprit()
                                                        ui.notify('Виновный обновлен')
                                                        self.log_service.add_log(
                                                            level='ADMIN_GAME',
                                                            user_id=app.storage.user.get('user_id', None),
                                                            action="ADMIN_GAME_SET_CULPRIT",
                                                            message=f"Администратор установил виновного '{culprit_id}' в игре {gid}",
                                                            metadata={
                                                                "game_id": gid,
                                                                "culprit_id": culprit_id,
                                                                "culprit_name": culprit_text_input.value
                                                            }
                                                        )

                                                    ui.button(
                                                        'Добавить',
                                                        on_click=add_culprit
                                                    ).classes('mt-2')

                                        culprit_container = ui.column().classes('w-full')
                                        refresh_culprit()

        else:
            ui.label('Выберите игру из списка выше или создайте новую').classes(
                'text-center w-full p-8 text-gray-500 italic')

    def show_create_game_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('w-full p-4 bg-blue-50 dark:bg-blue-900'):
            ui.label('Создать новую игру').classes('font-bold mb-2')
            game_id_input = ui.input('Айди игры')

            def create_game():
                game_id = game_id_input.value.strip()

                if not self.validate_fields(game_id_input, field_names=["ID игры"]):
                    return

                if game_id in self.available_games:
                    ui.notify(f'Игра с ID "{game_id}" уже существует', color='negative')
                    return

                try:
                    self.game_state_service.create_game_state(game_id)
                    self.load_available_games()
                    self.refresh_ui()
                    ui.notify('Игра успешно создана', color='positive')
                    self.log_service.add_log(
                        level='ADMIN_GAME',
                        action='ADMIN_GAME_CREATE_GAME',
                        message=f'Игра {game_id} успешно создана',
                        user_id=app.storage.user.get('user_id', None),
                        metadata={'game_id': game_id}
                    )
                    dialog.close()
                except Exception as e:
                    ui.notify(f'Ошибка при создании игры: {str(e)}', color='negative')
                    self.log_service.add_log(
                        level='ADMIN_GAME',
                        action='ERROR',
                        message=f'Ошибка при создании игры: {str(e)}',
                        user_id=app.storage.user.get('user_id', None),
                        metadata={'game_id': game_id}
                    )

            with ui.row().classes('justify-end mt-4'):
                ui.button('Отмена', on_click=dialog.close).classes('bg-gray-300 text-white')
                ui.button('Создать', on_click=create_game).classes('bg-green-500 text-white')

        dialog.open()

    def refresh_ui(self):
        self.load_available_games()
        if self.display_container:
            self.display_container.clear()
            self.create_game_cards()

    def create_ui(self):
        """Создает интерфейс управления игровыми комнатами"""
        self.load_available_games()

        with ui.card().classes('w-full p-4'):
            ui.label('Управление игровыми комнатами').classes('text-xl font-bold mb-4')

            # Кнопки верхнего уровня
            with ui.row().classes('w-full justify-between mb-4'):
                ui.button('Обновить список игр', icon='refresh', on_click=lambda: self.refresh_ui()) \
                    .classes('bg-blue-500 text-white')

                ui.button('Создать новую игру', icon='add', on_click=lambda: self.show_create_game_dialog()) \
                    .classes('bg-green-500 text-white')
            # Контейнер для карточек игр
            self.display_container = ui.column().classes('w-full')
            self.create_game_cards()