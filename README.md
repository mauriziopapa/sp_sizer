# SOLID PROJECT Sizer

Strumento di classificazione dimensionale per progetti di implementazione CRM/integrazione. Parte del metodo SOLID PROJECT di Studioware.

Combina fattori pesati (Business + Tecnici) in un punteggio normalizzato 0-100 che determina la size del progetto (SMALL / PMI / ENTERPRISE), con governance rules e risk flags associati.

## Stack

- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy 2.0 / Alembic / PostgreSQL
- **Frontend**: React 18 / Vite / TailwindCSS / Radix UI
- **Auth**: JWT
- **Deployment**: Railway

## Setup Locale

### Prerequisiti

- Docker e Docker Compose
- Node.js 20+
- Python 3.11+
- PostgreSQL 16+

### Con Docker Compose

```bash
docker-compose up
```

Backend su http://localhost:8000, frontend su http://localhost:5173.

### Sviluppo Manuale

**Backend:**

```bash
cd backend
pip install -r requirements.txt
# Configurare DATABASE_URL in .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Credenziali Default

- Username: `admin`
- Password: `admin`

## Architettura

```
sp_sizer/
├── backend/          # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/      # Route endpoints
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic (scoring, auth, PDF)
│   │   └── seed.py   # Seed data
│   └── alembic/      # DB migrations
├── frontend/         # React + Vite
│   └── src/
│       ├── components/
│       ├── pages/
│       └── lib/
└── docker-compose.yml
```

## API Principali

- `GET /api/health` - Health check
- `POST /api/auth/login` - Login
- `GET /api/sections` - Sezioni con fattori
- `POST /api/sizings` - Esegui sizing
- `GET /api/sizings` - Storico sizing
- `GET /api/sizings/{id}/export/pdf` - Export PDF

## Deploy su Railway

1. Collegare il repository GitHub
2. Aggiungere PostgreSQL plugin
3. Configurare variabili: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
4. Deploy automatico da branch main

## Variabili d'Ambiente

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://... | Connection string PostgreSQL |
| SECRET_KEY | dev-secret-key... | Chiave per JWT |
| CORS_ORIGINS | http://localhost:5173 | Origini CORS (separati da virgola) |
| ENVIRONMENT | development | development / production |
| ADMIN_USERNAME | admin | Username admin iniziale |
| ADMIN_PASSWORD | admin | Password admin iniziale |
