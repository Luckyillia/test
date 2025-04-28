# Detective Chronicles Game Platform

A web application for creating text-based quests with game state management, user authentication, and interactive interfaces.

## 🎮 Key Features
- **Game Room Management**: Create/delete games, join via ID
- **Dynamic Guides**: Residents, government institutions, public places
- **Locations**: Travel between locations, visit history, document attachments
- **Content Editor**: Newspapers, police cases, medical reports, registry office
- **Authentication**: Registration, login, user management (admin-only)
- **Dark Theme**: Toggle between light/dark modes

## 🔐 Usage
1. **Registration/Login**:  
   - Login: `/login`
   - Register: `/register` (password ≥8 characters)

2. **Create Game** (admin only):  
   - Navigate to "Create Game" tab
   - Enter unique Game ID

3. **Gameplay**:  
   - Travel between locations using IDs
   - Edit in-game guides
   - View newspapers and documents
   - Track location history

---

## Project Structure
```text
Detektyw/
│
├── 📂 data
│   ├── 📄 data.json
│   └── 📄 gameState.json
├── 📄 README.md
├── 📄 requirements.txt
├── 📂 src
│   ├── 📄 main.py
│   ├── 📂 models
│   │   ├── 📄 user.py
│   │   └── 📄 __init__.py
│   │
│   ├── 📂 services
│   │   ├── 📄 login.py
│   │   ├── 📄 registration.py
│   │   ├── 📄 user_service.py
│   │   └──📄 __init__.py
│   │  
│   ├── 📂 game
│   │   ├── 📄 game_dialog.py
│   │   ├── 📄 game_room_management.py
│   │   ├── 📄 game_state_service.py
│   │   ├── 📄 game_ui.py
│   │   └──📄 __init__.py
│   │
│   ├── 📂 ui
│   │   ├── 📂 components
│   │   │   ├── 📄 user_table.py
│   │   │   └── 📄 __init__.py
│   │   │ 
│   │   ├── 📄 user_ui.py
│   │   └── 📄 __init__.py
│   │   
│   └──📄 __init__.py
│   
└── 📄 test.py
```
---
## Statystyki Kodowania w Projekcie

```text
┌───────────┬───────┬───────┬──────┬───────┬─────────┬─────┐
│ Language  │ Files │     % │ Code │     % │ Comment │   % │
├───────────┼───────┼───────┼──────┼───────┼─────────┼─────┤
│ Python    │    20 │  80.0 │ 1850 │  70.4 │     140 │ 5.3 │
│ JSON      │     3 │  12.0 │  604 │  74.0 │       0 │ 0.0 │
│ Markdown  │     1 │   4.0 │  180 │  68.2 │       0 │ 0.0 │
│ Text only │     1 │   4.0 │   59 │ 100.0 │       0 │ 0.0 │
├───────────┼───────┼───────┼──────┼───────┼─────────┼─────┤
│ Sum       │    25 │ 100.0 │ 2693 │  71.5 │     140 │ 3.7 │
└───────────┴───────┴───────┴──────┴───────┴─────────┴─────┘
```

---

## Installation and Setup

### Prerequisites
- Python 3.12 or later.

### 🛠️  Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Luckyillia/DetectiveGame.git
   cd .\DetectiveGame\
   ```

2. (Optional) Create a virtual environment to isolate dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/MacOS
   .\.venv\Scripts\activate   # Windows
   ```

3. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```

4. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python -m src.main
   ```

6. Open the application in your web browser at:
   ```
   http://localhost:1234
   ```

---

## Usage

### 1. Registration and Login
- Create a new user account via the `/register` page (password must be ≥8 characters)
- Authenticate via `/login` to access game management features
- Session persists with dark/light mode preferences

### 2. Game Management
**For All Players:**
- Join existing games using unique Game IDs
- Travel between locations by entering location IDs
- View in-game newspapers and document attachments
- Access dynamic guides: residents, government offices, public places
- Track movement history with timestamps

**For Admins:**
- Create new game sessions with unique IDs
- Edit starting narrative text for new games
- Manage location descriptions and special venues:
  - Police station (ID 112102)
  - Morgue (ID 440321)
  - Registry office (ID 220123)
- Curate game newspapers and procedural documents

### 3. User Management
**For Players:**
- Update avatar using random generator
- View personal game history

**For Admins (username: lucky_illia):**
- Access special admin tabs for user management
- Add/delete users through interactive table
- Edit user details directly in the UI
- Regenerate user avatars
- Monitor active game sessions

---


## Technologies Used

- **Python** – Core application logic.
- **NiceGUI** – Modern and reactive front-end library for GUIs in Python.
- **JSON** – Storage for user data and game states.
- **FastAPI** – Middleware for authentication and routing requests.

---

## Data Structure

The app stores user information in a JSON file (`data/data.json`).

**Example user data:**
```json
{
    "users": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Jan",
            "surname": "Kowalski",
            "username": "janek",
            "password": "password123",
            "pesel": "12345678901",
            "avatar": "https://robohash.org/ABCDE",
            "gameState": null,
            "color": null
        }
    ]
}
```

The app stores game information in a JSON file (`data/gameState.json`).

**Example user game_state:**
```json
{
    "game_001": {
        "beginText": "",
        "gazeta": "",
        "spravochnik": {
            "people": [
                "1.\tКалинин Артём Сергеевич - ул. Морская, д. 17, кв. 42 - код: 7824"
            ],
            "gosplace": [
                "1.\tПолицейский участок №1 - ул. Советская, д. 25 - код: 112102"
            ],
            "obplace": [
                "1.\tАптека \"ЗдравМир\" - ул. Ленина, д. 15 - код: 2487"
            ]
        },
        "112102": {
            "text": "",
            "delo": ""
        },
        "440321": {
            "text": "",
            "vskrytie": ""
        },
        "220123": {
            "text": "",
            "otchet": ""
        },
        "place": {},
        "location_history": [
            {
                "id": "start",
                "visited_at": 1745536657
            }],
        "current_location": "220123",
        "move": 3
    }
}
```
---

## Contribution Guidelines

We welcome contributions from the community! Feel free to:
- Report bugs.
- Suggest new features or improvements.
- Submit pull requests to enhance functionality or optimize code.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

## Authors

**Authors:**
- **Illia Zaichenko** – *Original creator* – [luckyillia](https://github.com/luckyillia)

If you have any questions or suggestions, feel free to reach out! 🚀 