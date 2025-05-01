import json
import os
import time

from click import get_app_dir
from nicegui import app


class GameStateService:
    def __init__(self, filepath='data/gameState.json'):
        self.filepath = filepath
        self.ensure_file_exists()

    def ensure_file_exists(self):
        directory = os.path.dirname(self.filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.filepath):
            self.save({})

    def load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            print("❌ Error: Could not load game state data.")
            return {}

    def save(self, data):
        try:
            directory = os.path.dirname(self.filepath)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Convert data to JSON format
            data_to_write = json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            )

            # Write to a temporary file and then replace the original file
            temp_filepath = f"{self.filepath}.tmp"
            with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
                temp_file.write(data_to_write)

            # Replace the original file with the temporary one
            os.replace(temp_filepath, self.filepath)
            return True
        except Exception as e:
            print(f"❌ Error writing game state to file: {e}")
            return False

    def create_game_state(self, game_id):
        data = self.load()
        if game_id not in data:
            data[game_id] = {
                'start': None,
                'gazeta': '',
                'spravochnik': {
                    'people': {},
                    'gosplace': {},
                    'obplace': {}
                },
                '112102': {'text': '', 'delo': ''},
                '440321': {'text': '', 'vskrytie': ''},
                '220123': {'text': '', 'otchet': ''},
                'place': {},
                'isCulprit': {
                    'id': None,
                    'name': None,
                    'endText': None
                },
                "tooltip": {
                    "count": None,
                    "location_id": None
                }
            }
            self.save(data)

    def game_exists(self, game_id):
        data = self.load()
        return game_id in data

    def ensure_game_exists(self, game_id):
        data = self.load()
        if game_id not in data:
            self.create_game_state(game_id)
            return self.load()
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

    def add_people(self, game_id, person_id, person_text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['spravochnik']['people'][person_id] = person_text
        self.save(data)

    def add_gosplace(self, game_id, place_id, place_text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['spravochnik']['gosplace'][place_id] = place_text
        self.save(data)

    def add_obplace(self, game_id, place_id, place_text):
        data = self.ensure_game_exists(game_id)
        data[game_id]['spravochnik']['obplace'][place_id] = place_text
        self.save(data)

    def add_tooltip(self,game_id,count,location_id):
        data = self.load()
        data[game_id]['tooltip']['count'] = int(count)
        data[game_id]['tooltip']['location_id'] = location_id
        self.save(data)

    def get_game_state(self, game_id):
        data = self.load()
        return data.get(game_id, {})

    def edit_gazeta(self, game_id, text):
        data = self.load()
        if game_id in data:
            data[game_id]['gazeta'] = text
            self.save(data)

    def edit_culprit(self, game_id, id_culprit, name_culprit, end_text):
        data = self.load()
        if game_id in data:
            data[game_id]['isCulprit']['id'] = id_culprit
            data[game_id]['isCulprit']['name'] = name_culprit
            data[game_id]['isCulprit']['endText'] = end_text
            self.save(data)

    def edit_game_status(self, game_id, new_status):
        data = self.load()
        if game_id in data:
            data[game_id]['status'] = new_status
            self.save(data)

    def delete_game_state(self, game_id):
        data = self.load()
        if game_id in data:
            del data[game_id]
            self.save(data)