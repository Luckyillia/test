import json
import os
import time

from nicegui import app


class GameStateService:
    def __init__(self, game_ui ,filepath='data/gameState.json'):
        self.game_ui = game_ui
        self.filepath = filepath
        self.ensure_file_exists()

    def ensure_file_exists(self):
        directory = os.path.dirname(self.filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump({}, file)

    def load(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save(self, data):
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def create_game_state(self, game_id):
        data = self.load()
        if game_id not in data:
            data[game_id] = {
                'beginText': None,
                'gazeta': '',
                'spravochnik': {
                    'people': [],
                    'gosplace': [],
                    'obplace': []
                },
                '112102': {'text': '', 'delo': ''},
                '440321': {'text': '', 'vskrytie': ''},
                '220123': {'text': '', 'otchet': ''},
                'place': {},
                'move': 0
            }
            self.save(data)

    def game_exists(self, game_id):
        data = self.load()
        if game_id in data:
            return True
        return False

    def ensure_game_exists(self, game_id):
        data = self.load()
        if game_id not in data:
            self.create_game_state(game_id)
        return data

    def add_place(self, game_id, place_id, text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['place'][place_id] = text
        self.save(data)

    def add_gazeta(self, game_id, text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['gazeta'] = text
        self.save(data)

    def add_police(self, game_id, text=None, delo=None):
        data = self.ensure_game_exists(game_id)
        if text is not None:
            data[game_id]['112102']['text'] = text
        if delo is not None:
            data[game_id]['112102']['delo'] = delo
        self.save(data)

    def add_morg(self, game_id, text=None, vskrytie=None):
        data = self.ensure_game_exists(game_id)
        if text is not None:
            data[game_id]['440321']['text'] = text
        if vskrytie is not None:
            data[game_id]['440321']['vskrytie'] = vskrytie
        self.save(data)

    def add_zags(self, game_id, text=None, otchet=None):
        data = self.ensure_game_exists(game_id)
        if text is not None:
            data[game_id]['220123']['text'] = text
        if otchet is not None:
            data[game_id]['220123']['otchet'] = otchet
        self.save(data)

    def add_people(self, game_id, person_text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['spravochnik']['people'].append(person_text)
        self.save(data)

    def add_gosplace(self, game_id, place_text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['spravochnik']['gosplace'].append(place_text)
        self.save(data)

    def add_obplace(self, game_id, place_text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['spravochnik']['obplace'].append(place_text)
        self.save(data)

    def get_game_state(self, game_id):
        data = self.load()
        return data.get(game_id, {})

    def edit_gazeta(self, game_id, text):
        data = self.load()
        if game_id in data:
            data[game_id]['gazeta'] = text
            self.save(data)

    def delete_game_state(self, game_id):
        data = self.load()
        if game_id in data:
            del data[game_id]
            self.save(data)

    def add_location_to_history(self, game_id, location_id, location_text, additional_document=''):
        """Добавляет локацию в историю перемещений игрока"""
        data = self.load()
        if game_id not in data:
            return False

        if 'location_history' not in data[game_id]:
            data[game_id]['location_history'] = []

        location_entry = {
            'id': location_id,
            'text': location_text,
            'additional_document': additional_document,
            'visited_at': int(time.time())  # Время посещения
        }

        data[game_id]['location_history'].append(location_entry)
        data[game_id]['current_location'] = location_id
        data[game_id]['last_visited_at'] = int(time.time())
        data[game_id]['move'] = data[game_id].get('move', 0) + 1  # Увеличиваем счетчик ходов

        self.save(data)
        return True

    def get_location_history(self, game_id):
        """Возвращает историю перемещений игрока"""
        data = self.load()
        if game_id not in data:
            return []

        return data[game_id].get('location_history', [])

    def get_current_location(self, game_id):
        """Возвращает текущую локацию игрока"""
        data = self.load()
        if game_id not in data:
            return None

        return data[game_id].get('current_location', None)

    def check_for_updates(self):
        data = self.load()
        game_id = app.storage.user.get('game_state_id')
        if game_id not in data:
            return
        last_move_time = data[game_id].get('last_visited_at', 0)
        if last_move_time > self.game_ui.last_update:
            self.game_ui.show_game_interface()
            self.game_ui.last_update = last_move_time