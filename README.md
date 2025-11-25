# Jarvis — Desktop Voice Assistant

**Jarvis** is a lightweight, voice-powered desktop assistant for Windows that performs common tasks (play music, control brightness/volume, take screenshots, get weather & news, run background downloads/tasks, reminders and more) using local tools, a small LLM routing layer, and simple persistence.

---

## Key features
- Voice interaction (speech → intent → action) with a small LLM routing layer.
- Core program loop & command routing in `main.py`.
- System controls: brightness, mute/unmute, shutdown/restart, screenshots.
- Music control (local playback + YouTube search/play/download).
- Background task manager with persistent task state and resume for interrupted downloads.
- Weather & news fetchers with local caching.
- Reminders with system toast notifications.

---

## Repo / File layout (important files)
- `main.py` — application entrypoint and routing loop.
- `utils.py` — helper utilities: TTS (SAPI), take_screenshot, music controls, brightness, volume controls, etc.
- `llm_handler.py` — wraps the LLM system prompt & parsing.
- `tasks.py` — maps LLM actions to application functions and triggers background tasks.
- `task_manager.py` — background task runner + persistence + recover logic.
- `youtube_downloader.py` — yt-dlp based downloader with progress hooks and resume.
- `news.py` — fetch headlines using NewsAPI with caching fallback.
- `weather.py` — get coordinates via Nominatim + Open-Meteo client + caching.
- `reminders.py` — interactive reminder setting and check loop.
- `config.env` — environment variables (API keys, credentials). See **Configuration** below.

---

## Requirements
> Tested on Windows11 (desktop). Python 3.12.5 recommended.

Install dependencies (example):

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

---

## Configuration
Create a `config.env` in the project root (copy `config.env.example`) with values like:

```
NEWS_API=your_newsapi_key
EMAIL_ID=your_email@example.com
EMAIL_PASSWORD=your_email_app_password
GEMINI_API_KEY=your_gemini_api_key
```

The code reads env variables with `python-dotenv`.

---

## Usage
Run the assistant:

```bash
python main.py
```

On first run the assistant will announce itself and read the top headlines (if configured). The LLM interprets spoken commands and returns structured JSON actions (see `llm_handler.py` for the system prompt & rules).

### Example voice commands
- “Play music” — plays local or asks for source.
- “Set reminder at 5:30 pm to call mom” — sets reminder.
- “Get weather in Hyderabad” — returns cached or live weather.
- “Download Sanchaari from globetrotter from YouTube” — starts background download with resume.

---

## Persistence & Resilience
- Tasks and downloads persist to `task_state.json` and are resumed on next startup by `task_manager.py`.
- Weather and news use JSON cache fallbacks when API requests fail (offline mode).

---

## Development notes & TODOs
- Improve media playback error handling (current implementation uses `os.startfile` and can be fragile).
- Consider local parsers for offline resilience or add retry/backoff for LLM calls.
- Add `requirements.txt` pins and unit tests for `task_manager` and `youtube_downloader`.
- Test across additional Windows versions.

---

