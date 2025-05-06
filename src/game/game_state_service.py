import json
import os
import time
import shutil
from click import get_app_dir
from nicegui import app


class GameStateService:
    def __init__(self, directory='data/games'):
        self.directory = directory
        self.ensure_directory_exists()

    def ensure_directory_exists(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def get_game_filepath(self, game_id):
        """Return the filepath for a specific game's state file."""
        return os.path.join(self.directory, f"{game_id}.json")

    def load(self, game_id):
        """Load a specific game's state from its file."""
        filepath = self.get_game_filepath(game_id)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                return None
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"❌ Error: Could not load game state data for game {game_id}.")
            return None

    def save(self, game_id, data):
        """Save a specific game's state to its file."""
        try:
            # Ensure the directory exists
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)

            filepath = self.get_game_filepath(game_id)

            # Convert data to JSON format
            data_to_write = json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            )

            # Write to a temporary file and then replace the original file
            temp_filepath = f"{filepath}.tmp"
            with open(temp_filepath, 'w', encoding='utf-8') as temp_file:
                temp_file.write(data_to_write)

            # Replace the original file with the temporary one
            os.replace(temp_filepath, filepath)
            return True
        except Exception as e:
            print(f"❌ Error writing game state to file for game {game_id}: {e}")
            return False

    def create_game_state(self, game_id):
        """Create a new game state file for the given game ID."""
        game_state = {
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
            "tooltip": {}
        }
        self.save(game_id, game_state)

    def game_exists(self, game_id):
        """Check if a game state file exists for the given game ID."""
        filepath = self.get_game_filepath(game_id)
        return os.path.exists(filepath)

    def ensure_game_exists(self, game_id):
        """Ensure a game state file exists for the given game ID, creating it if necessary."""
        if not self.game_exists(game_id):
            self.create_game_state(game_id)
            return self.load(game_id)
        return self.load(game_id)

    def add_place(self, game_id, place_id, text):
        """Add place information to a game's state."""
        game_data = self.ensure_game_exists(game_id)
        game_data['place'][place_id] = text
        self.save(game_id, game_data)

    def add_gazeta(self, game_id, text):
        """Add gazeta text to a game's state."""
        game_data = self.ensure_game_exists(game_id)
        game_data['gazeta'] = text
        self.save(game_id, game_data)

    def add_police(self, game_id, text=None, delo=None):
        """Add police information to a game's state."""
        game_data = self.ensure_game_exists(game_id)
        if text is not None:
            game_data['112102']['text'] = text
        if delo is not None:
            game_data['112102']['delo'] = delo
        self.save(game_id, game_data)

    def add_morg(self, game_id, text=None, vskrytie=None):
        """Add morgue information to a game's state."""
        game_data = self.ensure_game_exists(game_id)
        if text is not None:
            game_data['440321']['text'] = text
        if vskrytie is not None:
            game_data['440321']['vskrytie'] = vskrytie
        self.save(game_id, game_data)

    def add_zags(self, game_id, text=None, otchet=None):
        """Add ZAGS information to a game's state."""
        game_data = self.ensure_game_exists(game_id)
        if text is not None:
            game_data['220123']['text'] = text
        if otchet is not None:
            game_data['220123']['otchet'] = otchet
        self.save(game_id, game_data)

    def add_people(self, game_id, person_id, person_text):
        """Add person information to a game's spravochnik."""
        game_data = self.ensure_game_exists(game_id)
        game_data['spravochnik']['people'][person_id] = person_text
        self.save(game_id, game_data)

    def add_gosplace(self, game_id, place_id, place_text):
        """Add government place information to a game's spravochnik."""
        game_data = self.ensure_game_exists(game_id)
        game_data['spravochnik']['gosplace'][place_id] = place_text
        self.save(game_id, game_data)

    def add_obplace(self, game_id, place_id, place_text):
        """Add public place information to a game's spravochnik."""
        game_data = self.ensure_game_exists(game_id)
        game_data['spravochnik']['obplace'][place_id] = place_text
        self.save(game_id, game_data)

    def add_tooltip(self, game_id, count, location_id):
        """Add tooltip information to a game's state."""
        game_data = self.load(game_id)
        game_data['tooltip'][count] = location_id
        self.save(game_id, game_data)

    def get_game_state(self, game_id):
        """Get the entire state of a game."""
        return self.load(game_id) or {}

    def edit_gazeta(self, game_id, text):
        """Edit gazeta text in a game's state."""
        game_data = self.load(game_id)
        if game_data:
            game_data['gazeta'] = text
            self.save(game_id, game_data)

    def edit_culprit(self, game_id, id_culprit, name_culprit, end_text):
        """Edit culprit information in a game's state."""
        game_data = self.load(game_id)
        if game_data:
            game_data['isCulprit']['id'] = id_culprit
            game_data['isCulprit']['name'] = name_culprit
            game_data['isCulprit']['endText'] = end_text
            self.save(game_id, game_data)

    def edit_game_status(self, game_id, new_status):
        """Edit game status in a game's state."""
        game_data = self.load(game_id)
        if game_data:
            game_data['status'] = new_status
            self.save(game_id, game_data)

    def delete_game_state(self, game_id):
        """Delete a game's state file."""
        filepath = self.get_game_filepath(game_id)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def list_all_games(self):
        """List all game IDs by scanning the games directory."""
        if not os.path.exists(self.directory):
            return []

        game_files = [f for f in os.listdir(self.directory) if f.endswith('.json')]
        return [os.path.splitext(f)[0] for f in game_files]

    def migrate_from_single_file(self, old_filepath='data/gameState.json'):
        """
        Мигрирует все игры из старого формата (один JSON файл) в новый (файл на игру)

        :param old_filepath: Путь к старому файлу JSON со всеми играми
        :return: Количество мигрированных игр или None в случае ошибки
        """
        try:
            # Проверяем существование старого файла
            if not os.path.exists(old_filepath):
                print(f"❌ Ошибка: Исходный файл {old_filepath} не найден.")
                return None

            # Загружаем данные из старого файла
            with open(old_filepath, 'r', encoding='utf-8') as file:
                old_data = json.load(file)

            # Проверяем, есть ли данные для миграции
            if not old_data:
                print("⚠️ Предупреждение: В исходном файле нет данных для миграции.")
                return 0

            # Создаем директорию для игр, если она не существует
            self.ensure_directory_exists()

            migrated_count = 0

            # Перебираем все игры в старом файле
            for game_id, game_data in old_data.items():
                # Проверяем, существует ли уже файл для этой игры
                game_filepath = self.get_game_filepath(game_id)
                if os.path.exists(game_filepath):
                    print(f"⚠️ Предупреждение: Файл для игры {game_id} уже существует. Пропускаем.")
                    continue

                # Сохраняем данные игры в отдельный файл
                self.save(game_id, game_data)
                migrated_count += 1
                print(f"✅ Игра {game_id} успешно мигрирована.")

            # Создаем резервную копию старого файла, если миграция успешна
            if migrated_count > 0:
                backup_filepath = f"{old_filepath}.backup.{int(time.time())}"
                shutil.copy2(old_filepath, backup_filepath)
                print(f"✅ Создана резервная копия старого файла: {backup_filepath}")

            return migrated_count

        except json.JSONDecodeError:
            print(f"❌ Ошибка: Не удалось декодировать JSON из файла {old_filepath}")
            return None
        except Exception as e:
            print(f"❌ Ошибка при миграции данных: {str(e)}")
            return None