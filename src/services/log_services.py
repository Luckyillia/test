import os
import json
import time
from datetime import datetime, timedelta
from nicegui import ui


class LogService:
    def __init__(self, logs_directory='data/logs', users_file='data/data.json'):
        self.logs_directory = logs_directory
        self.users_file = users_file
        self.user_filter = None
        self.available_users = []
        self.selected_date = datetime.now().date()
        self.level_filter = 'ALL'
        self.action_filter = 'ALL'
        self.search_query = ''
        self.available_actions = None
        self.logs_table = None
        self.ensure_logs_directory()
        self.load_users()

    def load_users(self):
        """Load users from the specified file."""
        directory = os.path.dirname(self.users_file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.users_file) or os.stat(self.users_file).st_size == 0:
            self.available_users = []
            return []

        try:
            with open(self.users_file, 'r', encoding='utf-8') as file:
                users = json.load(file).get("users", [])
                self.available_users = {user["id"]: user["username"] for user in users}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error loading users: {str(e)}")
            self.available_users = []

    def ensure_logs_directory(self):
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)

    def get_log_filename(self, date=None):
        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y-%m-%d')
        return os.path.join(self.logs_directory, f"log_{date_str}.json")

    def load_logs(self, date=None):
        filename = self.get_log_filename(date)

        if not os.path.exists(filename):
            return []

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"❌ Error: Could not load logs from {filename}")
            return []

    def save_logs(self, logs, date=None):
        self.ensure_logs_directory()
        filename = self.get_log_filename(date)

        try:
            # Convert data to JSON format
            data_to_write = json.dumps(
                logs,
                indent=4,
                ensure_ascii=False
            )

            # Write to a temporary file first
            temp_filename = f"{filename}.tmp"
            with open(temp_filename, 'w', encoding='utf-8') as temp_file:
                temp_file.write(data_to_write)

            # Replace the original file with the temporary one
            os.replace(temp_filename, filename)
            return True
        except Exception as e:
            print(f"❌ Error writing logs to file: {e}")
            return False

    def add_log(self, message, level="INFO", user_id=None, action=None, metadata=None):
        """
        Add a new log entry.

        Args:
            message (str): Log message
            level (str): Log level (INFO, WARNING, ERROR, DEBUG)
            user_id (str, optional): ID of the user related to this log
            action (str, optional): Type of action performed
            metadata (dict, optional): Additional data to store with the log

        Returns:
            bool: True if log was added successfully, False otherwise
        """
        current_time = datetime.now()
        date = current_time.date()

        # Load existing logs for today
        logs = self.load_logs(date)

        # Create new log entry
        log_entry = {
            "timestamp": int(time.time()),
            "datetime": current_time.strftime('%Y-%m-%d %H:%M:%S'),
            "level": level,
            "message": message,
            "user_id": user_id,
            "action": action
        }

        # Add metadata if provided
        if metadata:
            log_entry["metadata"] = metadata

        # Add to logs and save
        logs.append(log_entry)
        return self.save_logs(logs, date)

    def add_error_log(self, error_message, user_id=None, action="ERROR", metadata=None):
        return self.add_log(error_message, level="ERROR", user_id=user_id, action=action, metadata=metadata)

    def add_user_action_log(self, user_id, action, message, metadata=None):
        return self.add_log(message, level="INFO", user_id=user_id, action=action, metadata=metadata)

    def add_system_log(self, message, user_id=None, metadata=None):
        return self.add_log(message, level="SYSTEM", action="SYSTEM",user_id=user_id, metadata=metadata)

    def get_logs_for_date_range(self, start_date, end_date=None):
        if end_date is None:
            end_date = datetime.now().date()
        else:
            end_date = end_date.date()

        start_date = start_date.date()
        current_date = start_date
        result = {}

        # Loop through each date in the range
        while current_date <= end_date:
            logs = self.load_logs(current_date)
            date_str = current_date.strftime('%Y-%m-%d')
            result[date_str] = logs

            # Move to the next day - fixed implementation
            current_date = current_date + timedelta(days=1)

        return result

    def get_logs_for_user(self, user_id, date=None):
        logs = self.load_logs(date)
        return [log for log in logs if log.get("user_id") == user_id]

    def get_logs_by_level(self, level, date=None):
        logs = self.load_logs(date)
        return [log for log in logs if log.get("level") == level]

    def get_logs_by_action(self, action, date=None):
        logs = self.load_logs(date)
        return [log for log in logs if log.get("action") == action]

    def get_available_actions(self, date=None):
        logs = self.load_logs(date)
        actions = set()

        for log in logs:
            action = log.get('action')
            if action:
                actions.add(action)

        return sorted(actions)

    def search_logs(self, query, date=None):
        logs = self.load_logs(date)
        query = query.lower()

        results = []
        for log in logs:
            # Search in message
            if query in log.get("message", "").lower():
                results.append(log)
                continue

            # Search in metadata if it exists
            metadata = log.get("metadata", {})
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if isinstance(value, str) and query in value.lower():
                        results.append(log)
                        break

        return results


    def get_user_username(self, user_id):
        """Get the username for a given user ID."""
        return self.available_users.get(user_id, f"User {user_id}")

    def log_interface(self):
        self.available_actions = ['ALL'] + self.get_available_actions(self.selected_date)

        def update_logs():
            try:
                # Update available actions for the selected date
                self.available_actions = ['ALL'] + self.get_available_actions(self.selected_date)
                action_selector.options = self.available_actions

                if self.action_filter not in self.available_actions:
                    self.action_filter = 'ALL'
                    action_selector.value = 'ALL'

                # Get logs with filters applied
                logs = self.load_logs(self.selected_date)

                if self.level_filter != 'ALL':
                    logs = [log for log in logs if log.get('level') == self.level_filter]

                if self.action_filter != 'ALL':
                    logs = [log for log in logs if log.get('action') == self.action_filter]

                if self.user_filter:
                    logs = self.get_logs_for_user(self.user_filter, self.selected_date)

                if self.search_query:
                    query = self.search_query.lower()
                    logs = [log for log in logs if (
                            query in log.get('message', '').lower() or
                            query in log.get('user_id', '').lower() or
                            query in log.get('action', '').lower() or
                            query in json.dumps(log.get('metadata', {})).lower()
                    )]

                # Clear existing log entries
                log_container.clear()

                # Add log entries to the container
                with log_container:
                    if not logs:
                        ui.label('No logs found matching your criteria').classes('text-grey italic')

                    for log in logs:
                        # Determine card color based on log level
                        level_colors = {
                            'INFO': 'bg-blue-50 dark:bg-blue-800',
                            'ERROR': 'bg-red-50 dark:bg-red-800',
                            'DEBUG': 'bg-green-50 dark:bg-green-800',
                            'SYSTEM': 'bg-purple-50 dark:bg-purple-800'
                        }
                        color_class = level_colors.get(log.get('level', ''), 'bg-gray-50 dark:bg-gray-800')

                        with ui.card().classes(f'w-full mb-2 {color_class}'):
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label(log.get('datetime', '')).classes(
                                    'text-sm text-gray-600 dark:text-gray-300')
                                ui.badge(log.get('level', '')).classes('ml-2 text-sm py-1 px-2 rounded-full')

                                if log.get('action'):
                                    ui.badge(log.get('action')).classes(
                                        'ml-2 bg-green-600 text-sm py-1 px-2 rounded-full')

                                if log.get('user_id'):
                                    username = self.get_user_username(log.get('user_id'))
                                    ui.badge(f"User: {username}").classes(
                                        'ml-2 bg-purple-600 text-sm py-1 px-2 rounded-full')

                            ui.separator()

                            ui.label(log.get('message', '')).classes('font-medium text-gray-800 dark:text-gray-200')

                            if log.get('metadata'):
                                with ui.expansion('Metadata', icon='code').classes('w-full'):
                                    ui.code(json.dumps(log.get('metadata', {}), indent=2, ensure_ascii=False))

            except Exception as e:
                ui.notify(f"Ошибка загрузки логов: {str(e)}", type='negative')

        def set_date(date_str):
            try:
                self.selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                update_logs()
            except Exception:
                ui.notify("Некорректный формат даты", type='warning')

        def set_level(level):
            self.level_filter = level
            update_logs()

        def set_action(action):
            self.action_filter = action
            update_logs()

        def set_user(user_selection):
            if user_selection == 'ALL':
                self.user_filter = None
            else:
                # Извлекаем user_id (UUID) из выбора (формат: "username (user_id)")
                self.user_filter = user_selection.split("(")[-1][:-1]  # Получаем только UUID
            update_logs()

        def set_search(query):
            self.search_query = query.strip()
            update_logs()

        # UI Layout
        with ui.card().classes('w-full p-4 gap-4'):
            # Filter section
            with ui.expansion('Фильтры поиска', icon='filter_alt', group='log_filters').classes(
                    'w-full'):
                with ui.column().classes('w-full items-center').style('gap: 10px'):
                    with ui.row().classes('w-full items-center'):
                        ui.icon('calendar_month').classes('text-xl')
                        ui.date(value=self.selected_date, on_change=lambda e: set_date(e.value)).classes('w-48')

                        ui.separator().props('vertical').classes('mx-2')

                        ui.icon('filter_alt').classes('text-xl')
                        ui.select(
                            ['ALL', 'INFO', 'ERROR', 'DEBUG', 'SYSTEM'],
                            value=self.level_filter,
                            on_change=lambda e: set_level(e.value)
                        ).classes('w-40')

                        ui.separator().props('vertical').classes('mx-2')

                        ui.icon('flag').classes('text-xl')
                        action_selector = ui.select(
                            self.available_actions,
                            value=self.action_filter,
                            on_change=lambda e: set_action(e.value)
                        ).classes('w-48')

                        ui.separator().props('vertical').classes('mx-2')

                        # User Filter: Adding dynamic user filter
                        ui.icon('person').classes('text-xl')
                        user_selector = ui.select(
                            ['ALL'] + [f"{username} ({user_id})" for user_id, username in self.available_users.items()],
                            value='ALL',
                            on_change=lambda e: set_user(e.value)
                        ).classes('w-48')

                        ui.separator().props('vertical').classes('mx-2')

                        ui.icon('search').classes('text-xl')
                        ui.input(
                            placeholder='Поиск...',
                            on_change=lambda e: set_search(e.value)
                        ).classes('flex-grow')

                        ui.button('Обновить', on_click=update_logs).props('icon=refresh')

            # Container for log entries (will be filled dynamically)
            log_container = ui.column().classes('w-full max-h-[610px] overflow-auto')

        # Initial load
        update_logs()