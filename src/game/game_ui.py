from nicegui import ui, app
import json
import os


class GameUI:
    def __init__(self, game_state_service):
        self.game_state_service = game_state_service
        self.game_data = {}
        self.available_games = {}
        self.load_available_games()

    def load_available_games(self):
        try:
            self.available_games = self.game_state_service.load()
        except Exception as e:
            ui.notify(f'Ошибка загрузки игр: {str(e)}', color='negative')
            self.available_games = {}

    def refresh_game_data(self, game_id):
        self.game_data = self.game_state_service.get_game_state(game_id)
        ui.update()
        return self.game_data

    @ui.refreshable
    def display_games_list(self):
        """Динамически обновляемый список игр"""
        if self.available_games:
            for game_id, game_data in self.available_games.items():
                with ui.card().classes('w-full p-4'):
                    with ui.expansion(f'Айди игры: {game_id}', icon='description').classes('w-full'):
                        with ui.column().classes('w-full'):
                            with ui.row().classes('w-full items-center mb-4'):
                                ui.label().classes('text-lg font-bold')
                                ui.button('Обновить данные', icon='refresh', on_click=lambda game_id=game_id: [
                                    self.refresh_game_data(game_id),
                                    self.load_available_games(),
                                    ui.notify('Данные обновлены'),
                                    ui.update()
                                ]).classes('ml-auto')

                                ui.button('Удалить игру', icon='delete', color='red', on_click=lambda game_id=game_id: [
                                    self.game_state_service.delete_game_state(game_id),
                                    app.storage.user.update({'game_state_id': None}),
                                    self.load_available_games(),
                                    self.display_games_list.refresh(),
                                    ui.notify('Игра удалена'),
                                ])

                                # Газета (Newspaper)
                                with ui.expansion('Газета', icon='description').classes('w-full'):
                                    content_container = ui.column().classes('w-full')

                                    def refresh_gazeta_content():
                                        content_container.clear()
                                        if self.game_data.get('gazeta'):
                                            with content_container:
                                                ui.markdown(self.game_data['gazeta']).classes('whitespace-pre-wrap')

                                        with content_container:
                                            gazeta_input = ui.textarea('Редактировать газету').classes('w-full')
                                            gazeta_input.value = self.game_data.get('gazeta', '')
                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.edit_gazeta(game_id, gazeta_input.value),
                                                    ui.notify('Газета обновлена'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_gazeta_content()
                                                ]
                                            )

                                    refresh_gazeta_content()

                                # Справочник: Люди (Reference: People)
                                with ui.expansion('Справочник: Люди', icon='people').classes('w-full'):
                                    people_container = ui.column().classes('w-full')

                                    def refresh_people_content():
                                        people_container.clear()
                                        with people_container:
                                            for person in self.game_data.get('spravochnik', {}).get('people', []):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label(person).classes('whitespace-pre-wrap')

                                            new_person_input = ui.textarea('Добавить человека').classes('w-full')
                                            ui.button(
                                                'Добавить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_people(game_id, new_person_input.value),
                                                    ui.notify('Добавлено в справочник'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_people_content(),
                                                    new_person_input.set_value('')
                                                ]
                                            )

                                    refresh_people_content()

                                # Справочник: Государственные места (Reference: Government places)
                                with ui.expansion('Справочник: Гос. места', icon='account_balance').classes('w-full'):
                                    gosplaces_container = ui.column().classes('w-full')

                                    def refresh_gosplaces_content():
                                        gosplaces_container.clear()
                                        with gosplaces_container:
                                            for place in self.game_data.get('spravochnik', {}).get('gosplace', []):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label(place).classes('whitespace-pre-wrap')

                                            new_gosplace_input = ui.textarea('Добавить гос. место').classes('w-full')
                                            ui.button(
                                                'Добавить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_gosplace(game_id,
                                                                                         new_gosplace_input.value),
                                                    ui.notify('Добавлено в справочник'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_gosplaces_content(),
                                                    new_gosplace_input.set_value('')
                                                ]
                                            )

                                    refresh_gosplaces_content()

                                # Справочник: Общественные места (Reference: Public places)
                                with ui.expansion('Справочник: Общественные места', icon='store').classes('w-full'):
                                    obplaces_container = ui.column().classes('w-full')

                                    def refresh_obplaces_content():
                                        obplaces_container.clear()
                                        with obplaces_container:
                                            for place in self.game_data.get('spravochnik', {}).get('obplace', []):
                                                with ui.card().classes('w-full mb-2 p-3'):
                                                    ui.label(place).classes('whitespace-pre-wrap')

                                            new_obplace_input = ui.textarea('Добавить общественное место').classes(
                                                'w-full')
                                            ui.button(
                                                'Добавить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_obplace(game_id,
                                                                                        new_obplace_input.value),
                                                    ui.notify('Добавлено в справочник'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_obplaces_content(),
                                                    new_obplace_input.set_value('')
                                                ]
                                            )

                                    refresh_obplaces_content()

                                # Полиция (Police station - 112102)
                                with ui.expansion('Полиция (112102)', icon='local_police').classes('w-full'):
                                    police_container = ui.column().classes('w-full')

                                    def refresh_police_content():
                                        police_container.clear()
                                        police_data = self.game_data.get('112102', {})

                                        with police_container:
                                            # Display existing data if available
                                            if police_data.get('text'):
                                                ui.label('Текст:').classes('font-bold')
                                                ui.label(police_data['text']).classes('whitespace-pre-wrap mb-3')

                                            if police_data.get('delo'):
                                                ui.label('Дело:').classes('font-bold')
                                                ui.markdown(police_data['delo']).classes('whitespace-pre-wrap mb-3')

                                            # Input fields for updating
                                            police_text_input = ui.textarea('Текст').classes('w-full')
                                            police_text_input.value = police_data.get('text', '')

                                            police_delo_input = ui.textarea('Дело').classes('w-full mt-2')
                                            police_delo_input.value = police_data.get('delo', '')

                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_police(
                                                        game_id,
                                                        text=police_text_input.value,
                                                        delo=police_delo_input.value
                                                    ),
                                                    ui.notify('Полиция обновлена'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_police_content()
                                                ]
                                            ).classes('mt-2')

                                    refresh_police_content()

                                # Морг (Morgue - 440321)
                                with ui.expansion('Морг (440321)', icon='sick').classes('w-full'):
                                    morg_container = ui.column().classes('w-full')

                                    def refresh_morg_content():
                                        morg_container.clear()
                                        morg_data = self.game_data.get('440321', {})

                                        with morg_container:
                                            # Display existing data if available
                                            if morg_data.get('text'):
                                                ui.label('Текст:').classes('font-bold')
                                                ui.label(morg_data['text']).classes('whitespace-pre-wrap mb-3')

                                            if morg_data.get('vskrytie'):
                                                ui.label('Вскрытие:').classes('font-bold')
                                                ui.markdown(morg_data['vskrytie']).classes('whitespace-pre-wrap mb-3')

                                            # Input fields for updating
                                            morg_text_input = ui.textarea('Текст').classes('w-full')
                                            morg_text_input.value = morg_data.get('text', '')

                                            morg_vskrytie_input = ui.textarea('Вскрытие').classes('w-full mt-2')
                                            morg_vskrytie_input.value = morg_data.get('vskrytie', '')

                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_morg(
                                                        game_id,
                                                        text=morg_text_input.value,
                                                        vskrytie=morg_vskrytie_input.value
                                                    ),
                                                    ui.notify('Морг обновлен'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_morg_content()
                                                ]
                                            ).classes('mt-2')

                                    refresh_morg_content()

                                # ЗАГС (Registry office - 220123)
                                with ui.expansion('ЗАГС (220123)', icon='assignment').classes('w-full'):
                                    zags_container = ui.column().classes('w-full')

                                    def refresh_zags_content():
                                        zags_container.clear()
                                        zags_data = self.game_data.get('220123', {})

                                        with zags_container:
                                            # Display existing data if available
                                            if zags_data.get('text'):
                                                ui.label('Текст:').classes('font-bold')
                                                ui.label(zags_data['text']).classes('whitespace-pre-wrap mb-3')

                                            if zags_data.get('otchet'):
                                                ui.label('Отчет:').classes('font-bold')
                                                ui.markdown(zags_data['otchet']).classes('whitespace-pre-wrap mb-3')

                                            # Input fields for updating
                                            zags_text_input = ui.textarea('Текст').classes('w-full')
                                            zags_text_input.value = zags_data.get('text', '')

                                            zags_otchet_input = ui.textarea('Отчет').classes('w-full mt-2')
                                            zags_otchet_input.value = zags_data.get('otchet', '')

                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service.add_zags(
                                                        game_id,
                                                        text=zags_text_input.value,
                                                        otchet=zags_otchet_input.value
                                                    ),
                                                    ui.notify('ЗАГС обновлен'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_zags_content()
                                                ]
                                            ).classes('mt-2')

                                    refresh_zags_content()

                                # Другие места (Other places)
                                with ui.expansion('Другие места', icon='place').classes('w-full'):
                                    places_container = ui.column().classes('w-full')

                                    def refresh_places_content():
                                        places_container.clear()
                                        places = self.game_data.get('place', {})

                                        with places_container:
                                            # Display existing places
                                            if places:
                                                for place_id, place_text in places.items():
                                                    with ui.card().classes('w-full mb-4 p-3'):
                                                        ui.label(f'ID: {place_id}').classes('font-bold')
                                                        ui.label(place_text).classes('whitespace-pre-wrap')

                                            # Add new place
                                            with ui.card().classes('w-full p-4 bg-blue-50 dark:bg-blue-900'):
                                                ui.label('Добавить новое место').classes('font-bold')
                                                place_id_input = ui.input('ID места').classes('w-full')
                                                place_text_input = ui.textarea('Описание места').classes('w-full mt-2')

                                                ui.button(
                                                    'Добавить',
                                                    on_click=lambda: [
                                                        self.game_state_service.add_place(
                                                            game_id,
                                                            place_id_input.value,
                                                            place_text_input.value
                                                        ),
                                                        ui.notify('Место добавлено'),
                                                        self.refresh_game_data(game_id),
                                                        refresh_places_content(),
                                                        place_id_input.set_value(''),
                                                        place_text_input.set_value('')
                                                    ]
                                                ).classes('mt-2')

                                    refresh_places_content()

                                # Начальный текст (Begin text)
                                with ui.expansion('Начальный текст', icon='text_format').classes('w-full'):
                                    begin_text_container = ui.column().classes('w-full')

                                    def refresh_begin_text_content():
                                        begin_text_container.clear()

                                        with begin_text_container:
                                            if self.game_data.get('beginText'):
                                                ui.label(self.game_data['beginText']).classes(
                                                    'whitespace-pre-wrap mb-3')

                                            begin_text_input = ui.textarea('Начальный текст').classes('w-full')
                                            begin_text_input.value = self.game_data.get('beginText', '')

                                            ui.button(
                                                'Сохранить',
                                                on_click=lambda: [
                                                    self.game_state_service._ensure_game_exists(game_id),
                                                    data := self.game_state_service._load(),
                                                    data.__setitem__(game_id, {**data[game_id],
                                                                               'beginText': begin_text_input.value}),
                                                    self.game_state_service._save(data),
                                                    ui.notify('Начальный текст сохранен'),
                                                    self.refresh_game_data(game_id),
                                                    refresh_begin_text_content()
                                                ]
                                            ).classes('mt-2')

                                    refresh_begin_text_content()
            else:
                ui.label('Выберите игру из списка выше или создайте новую').classes('text-center w-full p-8 text-gray-500 italic')

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