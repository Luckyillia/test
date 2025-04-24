import json
import os

class GameStateService:
    def __init__(self, filepath='data/gameState.json'):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        directory = os.path.dirname(self.filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump({}, file)

    def load(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _save(self, data):
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
                'place': {}
            }
            self._save(data)

    def _ensure_game_exists(self, game_id):
        data = self.load()
        if game_id not in data:
            self.create_game_state(game_id)
        return data

    def add_place(self, game_id, place_id, text):
        data = self._ensure_game_exists(game_id)
        data[game_id]['place'][place_id] = text
        self._save(data)

    def add_gazeta(self, game_id, text):
        data = self._ensure_game_exists(game_id)
        data[game_id]['gazeta'] = text
        self._save(data)

    def add_police(self, game_id, text=None, delo=None):
        data = self._ensure_game_exists(game_id)
        if text is not None:
            data[game_id]['112102']['text'] = text
        if delo is not None:
            data[game_id]['112102']['delo'] = delo
        self._save(data)

    def add_morg(self, game_id, text=None, vskrytie=None):
        data = self._ensure_game_exists(game_id)
        if text is not None:
            data[game_id]['440321']['text'] = text
        if vskrytie is not None:
            data[game_id]['440321']['vskrytie'] = vskrytie
        self._save(data)

    def add_zags(self, game_id, text=None, otchet=None):
        data = self._ensure_game_exists(game_id)
        if text is not None:
            data[game_id]['220123']['text'] = text
        if otchet is not None:
            data[game_id]['220123']['otchet'] = otchet
        self._save(data)

    def add_people(self, game_id, person_text):
        data = self._ensure_game_exists(game_id)
        data[game_id]['spravochnik']['people'].append(person_text)
        self._save(data)

    def add_gosplace(self, game_id, place_text):
        data = self._ensure_game_exists(game_id)
        data[game_id]['spravochnik']['gosplace'].append(place_text)
        self._save(data)

    def add_obplace(self, game_id, place_text):
        data = self._ensure_game_exists(game_id)
        data[game_id]['spravochnik']['obplace'].append(place_text)
        self._save(data)

    def get_game_state(self, game_id):
        data = self.load()
        return data.get(game_id, {})

    def edit_gazeta(self, game_id, text):
        data = self.load()
        if game_id in data:
            data[game_id]['gazeta'] = text
            self._save(data)

    def delete_game_state(self, game_id):
        data = self.load()
        if game_id in data:
            del data[game_id]
            self._save(data)