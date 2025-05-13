# AI-Powered Task Planner 🧠✅

This project is an **AI-assisted task planner web application** built with FastAPI and HTML/CSS. Users enter a **topic**, and the app uses the **Google Gemini API** to generate a description and a to-do list, which is then stored in a local database.

## ✨ Features

- 📝 Accepts a simple title input from the user
- 🤖 Generates a relevant description and to-do list using the Gemini API
- 🗂️ Stores tasks in a local database
- 🌐 Web interface built with HTML/CSS
- 🐳 Docker support for easy deployment

## 🧱 Project Structure
─ alembic/ # Alembic migration files
─ frontend/ # HTML / CSS files
─ models/ # SQLAlchemy models
─ routers/ # FastAPI routers
─ db.py # Database connection setup
─ main.py # FastAPI application entry point
─ DockerFile # Docker image definition
─ docker-compose.yaml # Docker service orchestration
─ requirements.txt # Python dependencies

## ⚙️ Installation

### 1. Requirements

- Python 3.9+
- Docker (optional)

### 2. Start with Docker

```bash
docker-compose up --build

```
3. Start Manually (without Docker)
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

# 🧪 Usage
Visit http://localhost:8000 in your browser.
Enter a title and click the "Plan" button.
The AI-generated description and to-do list will appear.
Tasks are saved in the local database.

# 🧠 Technologies Used
- FastAPI
- HTML & CSS
- SQLAlchemy
- Alembic
- Google Gemini API
- Docker & Docker Compose

# 🔐 Notes
It’s recommended to keep your Gemini API key secure using a .env file.

Currently runs locally only. Contributions are welcome to extend functionality.

# 📌 Developer Notes
This project was created to simplify the task planning experience using AI. Feel free to contribute via pull requests or suggestions!
