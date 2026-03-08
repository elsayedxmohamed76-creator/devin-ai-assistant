# Devin AI Assistant

An AI-powered coding assistant inspired by Devin - modular, extensible, and built to help developers. Cross-platform: Web, Desktop, and Mobile.

## Features

- **Interactive Chat** - Natural language conversation with an AI coding assistant
- **Tool System** - File reading/writing, shell execution, code search, and more
- **Task Planning** - Break down complex tasks into manageable steps
- **Conversation Memory** - Token-aware memory with sliding window
- **Cross-Platform** - Runs on Web, Desktop (Electron), and Mobile (Capacitor)
- **Beautiful UI** - Modern dark theme with responsive design

## Architecture

```
devin-ai-assistant/
├── backend/              # Python FastAPI backend (AI engine)
│   ├── app/
│   │   ├── main.py       # FastAPI app with CORS
│   │   ├── models.py     # Pydantic data models
│   │   ├── engine.py     # AI assistant engine (conversations, tools, planner)
│   │   └── routes.py     # API endpoints
│   └── pyproject.toml    # Python dependencies (Poetry)
├── frontend/             # React + TypeScript frontend (shared UI)
│   ├── src/
│   │   ├── App.tsx       # Main application component
│   │   ├── components/   # Chat UI components
│   │   ├── hooks/        # Custom React hooks
│   │   └── services/     # API client
│   ├── electron/         # Desktop app (Electron)
│   │   ├── main.js       # Electron main process
│   │   └── preload.js    # Preload script
│   └── capacitor.config.ts  # Mobile app (Capacitor)
├── README.md
└── LICENSE
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (for Python backend)

### Backend Setup

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend Setup (Web)

```bash
cd frontend
npm install
npm run dev
```

The web app will be available at `http://localhost:5173`.

### Desktop App (Electron)

```bash
cd frontend
npm install
npm install --save-dev electron electron-builder

# Development
npm run dev
# In another terminal:
npx electron electron/main.js

# Production build
npm run build
npx electron-builder
```

### Mobile App (Capacitor)

```bash
cd frontend
npm install
npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android
npx cap init

# Build web assets first
npm run build

# Add platforms
npx cap add ios
npx cap add android

# Open in native IDE
npx cap open ios
npx cap open android
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send a message and get AI response |
| `GET` | `/api/conversations` | List all conversations |
| `GET` | `/api/conversations/:id` | Get conversation details |
| `DELETE` | `/api/conversations/:id` | Delete a conversation |
| `GET` | `/api/tools` | List available tools |
| `POST` | `/api/tools/execute` | Execute a tool |
| `POST` | `/api/tasks` | Create a task plan |
| `GET` | `/api/tasks` | List all tasks |
| `PATCH` | `/api/tasks/:id` | Update task status |
| `GET` | `/api/agent` | Get agent info |
| `GET` | `/healthz` | Health check |

## Available Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents from the workspace |
| `write_file` | Write content to files |
| `run_shell` | Execute shell commands safely |
| `search_code` | Search code with regex patterns |
| `list_files` | List and filter files by glob pattern |
| `web_search` | Search the web for documentation |

## Tech Stack

- **Backend**: Python, FastAPI, Pydantic, httpx
- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Desktop**: Electron
- **Mobile**: Capacitor (iOS & Android)
- **Icons**: Lucide React

## License

MIT License - see [LICENSE](LICENSE) for details.
