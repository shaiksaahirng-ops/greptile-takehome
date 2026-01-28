
Transforms git commits into user-friendly changelogs using Gemini AI.

# How to Run

### Prerequisites
- Python 3.9+
- Node.js 18+
- Gemini API key (get from https://makersuite.google.com/app/apikey as its free for proof of concept)

### Setup

1. Clone and configure environment:
```bash
cd greptile-takehome
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

2. Start backend:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

3. Start frontend (new terminal):
```bash
cd frontend
npm install
npm run dev
```

4. Install CLI:
```bash
cd cli
pip install -e .
```

### Usage

Generate and publish a changelog from any git repository:
```bash
cd /path/to/your/project
changelog generate --days 7 --publish
```

View changelogs at http://localhost:5173

## Technical Decisions

### Python CLI
GitPython handles repository parsing, Rich provides terminal formatting, and Click simplifies command structure.

### FastAPI Backend
Needed async support ++ FastAPI is fast, modern, and generates /docs endpoint automatically for testing.

### React + Vite Frontend  
Vite has the fastest HMR I've used. Kept dependencies minimal - just React for the UI, no state management library needed since we're just fetching and displaying data.

### SQLite Database
Zero config. The database file gets created automatically on first run. Easy to inspect and migrate to Postgres later if needed.

### Gemini API
Free tier works well for this use case. The model (gemini-flash-latest) handles changelog generation reliably.

## Product Decisions

### CLI Works with Any Repository
Made the tool repository-agnostic rather than hardcoding it to this project. This makes it actually useful and demonstrates generalizability.

### Categorized Output
Automatically groups changes into Features, Bug Fixes, Improvements, and Breaking Changes. AI does the categorization based on commit messages and content.

### Publish Flow
CLI generates changelog locally first, letting developers review before publishing. Separating generation from publishing prevents accidental releases.



## Architecture

```
Developer → CLI (Python) → Git Commits → Gemini AI → Formatted Changelog
                                                              ↓
                                          Backend API (FastAPI + SQLite)
                                                              ↓
                                          Frontend (React) ← End Users
```

## API Endpoints

- GET /api/changelogs - List all changelogs
- POST /api/changelogs - Create new changelog
- GET /api/changelogs/{id} - Get specific changelog
- PUT /api/changelogs/{id} - Update changelog
- DELETE /api/changelogs/{id} - Delete changelog

Full API documentation at http://localhost:8000/docs
