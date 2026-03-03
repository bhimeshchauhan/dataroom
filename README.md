# Data Room MVP

A virtual data room for secure document storage and organization - built for Acme Corp's multi-billion dollar acquisition due diligence.

React + TypeScript + Tailwind (frontend) · Flask + PostgreSQL (backend)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ and Python 3.11+ (for local dev without Docker)

### Run with Docker Compose
```bash
docker-compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:5000
# Postgres: localhost:5432
```

### Run Locally (Development)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start Postgres (via Docker or local install)
docker run -d --name dataroom-db \
  -e POSTGRES_DB=dataroom -e POSTGRES_USER=dataroom -e POSTGRES_PASSWORD=dataroom \
  -p 5432:5432 postgres:15-alpine

python wsgi.py  # runs on http://localhost:5000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # runs on http://localhost:5173
```

**Run Tests:**
```bash
cd backend
python -m pytest tests/ -v
```

## Cloud Demo Deployment

For a zero/low-cost demo setup with GitHub Actions deployments:
- Frontend: GitHub Pages
- Backend: Render
- Database: Neon
- File storage: Cloudflare R2

See the full guide: [`docs/deployment/cloud-demo.md`](docs/deployment/cloud-demo.md)

## Design Decisions

### Architecture
- **Separate frontend/backend** - Clean separation of concerns. SPA communicates via REST API. Easy to deploy independently and scale horizontally.
- **Flask over Django** - Lighter weight for an MVP. No ORM magic, explicit routing. SQLAlchemy provides just enough abstraction without being heavyweight.
- **Multiple data rooms** - Each data room is an independent top-level container (like separate Google Drives). Users can create, browse, and manage multiple data rooms.

### Database
- **Three tables: datarooms + folders + files** - Data rooms are first-class entities. Folders and files are scoped to a data room via foreign keys. Files can live at the data room root (nullable folder_id) or inside any folder.
- **Materialized path for nesting** - Each folder stores its full ancestor path (e.g., `/uuid1/uuid2/uuid3`). This enables efficient subtree queries (`WHERE path LIKE '/uuid1/%'`) without recursive CTEs or Postgres extensions (vs ltree). Tradeoff: path updates on folder moves are O(descendants), but moves are not in MVP scope.
- **Soft delete with deleted_at** - Data rooms hold critical legal/financial documents. Accidental deletions must be recoverable. A background job could hard-delete items older than 30 days.
- **Partial unique indexes** - Enforce name uniqueness only among active (non-deleted) items, scoped to the parent context. Allows recreating items with previously-used names after deletion.

### File Storage
- **Storage abstraction (local or S3-compatible)** - Files are stored with UUID keys and can use local disk (`STORAGE_BACKEND=local`) or object storage (`STORAGE_BACKEND=s3`, e.g. Cloudflare R2). No user input ever touches the filesystem key/path.
- **Triple PDF validation** - Extension check + Content-Type header + magic bytes (`%PDF`). Defense in depth against malicious uploads.
- **50MB file size limit** - Configurable via environment variable. Checked before writing to disk.

### Frontend
- **Two-view SPA** - Landing page (data room grid) and detail view (sidebar tree + content panel). State managed in App.tsx with hash-based deep linking.
- **shadcn/ui components** - Professional, accessible UI primitives with consistent styling.
- **react-pdf** - In-app PDF viewing with page navigation, keyboard shortcuts, and fallback to browser tab.
- **Optimistic refresh** - After every mutation, both the folder tree and content panel refresh to stay in sync.

### Scalability Considerations
- **Pagination-ready endpoints** - All list endpoints accept page/per_page parameters.
- **Partial indexes** - Only index active items, keeping index size proportional to live data even with millions of soft-deleted records.
- **Materialized path index** - `text_pattern_ops` btree index enables fast prefix scans for subtree queries.
- **Storage abstraction** - Backend storage service can be swapped from disk to object storage (S3) without schema changes.
- **Stateless backend** - No server-side sessions. Ready for horizontal scaling behind a load balancer.

### What I'd Add With More Time
- **Authentication** - JWT tokens with Flask-Login or Auth0. Add `user_id` to datarooms for ownership. Row-level access control.
- **Full-text search** - Extract PDF text with PyPDF2, index with Postgres tsvector. Search bar in header.
- **Drag-and-drop moving** - Move files/folders between folders via drag in the sidebar or a "Move to..." dialog.
- **File versioning** - Track upload history, allow rollback.
- **Real-time updates** - WebSocket notifications when other users modify the data room.
- **Comprehensive test suite** - Integration tests, E2E with Playwright, frontend component tests.
- **Background jobs** - Celery for hard-delete cleanup, PDF text extraction, thumbnail generation.

## API Reference

Base URL: `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/datarooms` | Create a data room |
| GET | `/datarooms` | List all data rooms |
| GET | `/datarooms/:id` | Get a data room |
| PATCH | `/datarooms/:id` | Rename/update a data room |
| DELETE | `/datarooms/:id` | Soft-delete a data room + all contents |
| GET | `/datarooms/:id/contents` | List root-level folders + files |
| GET | `/datarooms/:id/tree` | Get folder tree for sidebar |
| POST | `/datarooms/:id/folders` | Create a folder |
| GET | `/folders/:id/contents` | List folder contents |
| PATCH | `/folders/:id` | Rename a folder |
| DELETE | `/folders/:id` | Soft-delete folder + all descendants |
| POST | `/datarooms/:id/files` | Upload a PDF file |
| GET | `/files/:id` | Get file metadata |
| GET | `/files/:id/content` | Stream PDF for viewing |
| PATCH | `/files/:id` | Rename a file |
| DELETE | `/files/:id` | Soft-delete a file |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4, shadcn/ui, react-pdf, lucide-react |
| Backend | Flask 3.1, SQLAlchemy, Flask-Migrate, Gunicorn, boto3 |
| Database | PostgreSQL 15 |
| Testing | Pytest (20 tests) |
| Containerization | Docker, Docker Compose |

## Edge Cases Handled

- **Same filename in folder** - Unique index rejects; API returns 409 with descriptive message
- **Delete non-empty folder** - Cascading soft-delete of all descendants in a single transaction
- **Invalid file upload** - Triple validation (extension + content-type + magic bytes)
- **Path traversal** - UUID-only filenames on disk; no user input in filesystem paths
- **Deep folder nesting** - Materialized path handles efficiently; breadcrumbs show full chain
- **Refresh persistence** - All state in Postgres; URL hash restores exact view on refresh
- **Large files** - Rejected before saving; configurable size limit (default 50MB)
- **Concurrent name conflicts** - Database-level unique constraints prevent race conditions
