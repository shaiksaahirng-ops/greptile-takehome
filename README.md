# 📋 Changelog AI

> AI-powered changelog generator that transforms git commits into beautiful, user-friendly release notes.

![Demo](https://via.placeholder.com/800x400?text=Changelog+AI+Demo)

## ✨ Features

- **🤖 AI-Powered Generation** - Uses Gemini AI to transform technical commits into user-friendly changelog entries
- **📊 Smart Categorization** - Automatically groups changes into Features, Bug Fixes, Improvements, and Breaking Changes
- **🖥️ Developer CLI** - Simple command-line tool that works with any git repository
- **🌐 Beautiful Public Website** - Modern, responsive changelog page for end-users
- **⚡ Fast & Free** - Runs locally, uses free Gemini API tier

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- [Gemini API Key](https://makersuite.google.com/app/apikey) (free)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd greptile-takehome

# Copy environment template
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Install the CLI

```bash
cd cli
pip install -e .
```

### 5. Generate a Changelog!

```bash
# Navigate to ANY git repository
cd /path/to/your/project

# Generate a changelog from the last 7 days
changelog generate --days 7

# Or publish immediately
changelog generate --days 7 --publish
```

Visit **http://localhost:5173** to see your changelog! 🎉

---

## 📖 CLI Usage

```bash
# Generate changelog from last 7 days
changelog generate --days 7

# Generate from specific date range
changelog generate --since 2024-01-01 --until 2024-01-15

# Generate and publish in one command
changelog generate --days 7 --publish

# Dry run (see commits without calling AI)
changelog generate --days 7 --dry-run

# Save to file
changelog generate --days 7 --output changelog.json

# List published changelogs
changelog list

# See all options
changelog generate --help
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--days, -d` | Number of days to look back (default: 7) |
| `--since, -s` | Start date (YYYY-MM-DD) |
| `--until, -u` | End date (YYYY-MM-DD) |
| `--branch, -b` | Branch to analyze |
| `--version, -v` | Version for this changelog |
| `--project, -p` | Project name |
| `--publish` | Publish immediately |
| `--dry-run` | Preview without AI call |
| `--output, -o` | Save to JSON file |

---

## 🐳 Docker Setup (Alternative)

Run everything with one command:

```bash
docker-compose up --build
```

Then install the CLI locally and point it to the Docker backend:

```bash
cd cli
pip install -e .
export CHANGELOG_API_URL=http://localhost:8000
changelog generate --days 7 --publish
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Developer     │     │    Backend      │     │   End Users     │
│   (CLI Tool)    │────▶│   (FastAPI)     │◀────│   (Website)     │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Git Repo      │     │    SQLite       │
│   (commits)     │     │   (storage)     │
└─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Gemini AI     │
│   (generation)  │
└─────────────────┘
```

---

## 🎨 Design Decisions

### Why Python CLI?
- Most developers already have Python installed
- Excellent libraries for git parsing (GitPython) and terminal UI (Rich, Click)
- Easy to install with `pip install -e .`

### Why FastAPI Backend?
- Modern, fast, and async-first
- Auto-generates OpenAPI documentation at `/docs`
- Clean and readable code with Pydantic validation

### Why React + Vite Frontend?
- Fast development with hot module replacement
- Modern build tooling, optimized production builds
- Simple, focused codebase without unnecessary dependencies

### Why SQLite?
- Zero configuration, works out of the box
- Perfect for local development and demos
- Easy to migrate to PostgreSQL for production

### Why Gemini AI?
- Free tier available
- Good quality for changelog generation
- Fast response times

---

## 📁 Project Structure

```
greptile-takehome/
├── cli/                    # Python CLI tool
│   ├── changelog_cli/
│   │   ├── main.py        # CLI commands
│   │   ├── git_parser.py  # Git commit extraction
│   │   ├── ai_generator.py # Gemini integration
│   │   └── api_client.py  # Backend API client
│   └── pyproject.toml
│
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI app
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Request/response schemas
│   │   ├── routes.py      # API endpoints
│   │   └── database.py    # DB connection
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── App.jsx        # Main component
│   │   └── index.css      # Styling
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/changelogs` | List all changelogs |
| GET | `/api/changelogs/{id}` | Get single changelog |
| POST | `/api/changelogs` | Create changelog |
| PUT | `/api/changelogs/{id}` | Update changelog |
| DELETE | `/api/changelogs/{id}` | Delete changelog |

Full API documentation available at **http://localhost:8000/docs**

---

## 🎯 User Experience

### For Developers

1. **Simple Installation** - One `pip install` command
2. **Works Everywhere** - Run from any git repository
3. **Beautiful Terminal Output** - Rich formatting with colors and emojis
4. **Flexible Options** - Date ranges, branches, versions
5. **Dry Run Mode** - Preview before sending to AI

### For End Users

1. **Clean Design** - Modern dark theme with vibrant accents
2. **Timeline View** - Easy to scan through updates
3. **Color-Coded Categories** - Quickly identify features vs fixes
4. **Responsive** - Works on desktop and mobile
5. **Fast Loading** - Lightweight, no heavy frameworks

---

## 🤝 Contributing

Feel free to open issues or submit PRs!

---

## 📄 License

MIT

---

Built with ❤️ for the Greptile Take-Home Challenge
