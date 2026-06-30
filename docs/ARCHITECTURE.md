# AI Learning OS - System Architecture

## 1. Vision

AI Learning OS is a long-term personal platform that unifies learning, research,
note-taking, AI assistance, project management, and knowledge management into a single
system. It is meant to be used daily for years, not demoed once and abandoned: so the
architecture is optimized for modularity and long-term maintainability over short-term
build speed.

## 2. Architecture Style

The project follows **Clean Architecture** with strict layering: each layer only
depends on the layer directly beneath it, and business logic never depends on the web
framework or database driver directly. Concretely, every feature (notes, tasks,
flashcards, etc.) is organized as its own module, and each module follows the same
internal layering:

```
Router            → HTTP request/response handling only
   ↓
Service           → business logic, orchestration
   ↓
Repository        → database queries for this module
   ↓
Database          → PostgreSQL
```

At the system level, this looks like:

```
        ┌─────────────────────────────────────────────┐
        │              Frontend (Next.js)             │
        └───────────────────────┬─────────────────────┘
                                │ REST API
        ┌───────────────────────▼──────────────────────────┐
        │           API Gateway / FastAPI App              │
        │   ┌───────────────┐        ┌──────────────────┐  │
        │   │ Authentication│        │ Domain Modules   │  │
        │   └───────────────┘        │ (notes, tasks,   │  │
        │                            │  flashcards...)  │  │
        │                            └────────┬─────────┘  │
        └─────────────────────────────────────┼────────────┘
                                              │
                         ┌────────────────────┼───────────────────────┐
                         │                    │                       │
                 ┌───────▼──────┐   ┌─────────▼─────────┐   ┌─────────▼────────┐
                 │  PostgreSQL  │   │   Vector Store    │   │   File Storage   │
                 │(relational)  │   │ (FAISS → Qdrant)  │   │  (PDFs, images)  │
                 └──────────────┘   └───────────────────┘   └──────────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │  External AI APIs  │
                                    │ (LLMs, embeddings) │
                                    └────────────────────┘
```

Why this shape matters: a request from the frontend always passes through a router,
then a service, then a repository, before it ever touches data. This means business
logic can be unit-tested without a running database, and the database or AI provider
can be swapped without rewriting the modules that use them.

## 3. Major Components

### Frontend

Handles the user-facing experience: dashboard, rich text editor, project boards,
charts, the knowledge graph view, and the AI chat interface.

- **Next.js + React**: application framework
- **Tailwind CSS**: styling
- **TanStack Query**: server state and caching
- **React Flow**: knowledge graph visualization
- **Chart.js**: analytics charts

### Backend

Exposes the REST API, enforces authentication/authorization, runs business logic, and
schedules background work (PDF processing, embedding generation).

- **FastAPI**: async web framework
- **SQLAlchemy 2.0 (async)**: ORM
- **Alembic**: database migrations
- **Pydantic**: request/response validation
- **JWT**: authentication tokens
- **Redis**: caching and Celery broker
- **Celery**: background task queue

### Primary Database: PostgreSQL

Stores all structured, relational data: users, notes, projects, tasks, flashcards,
quizzes, study sessions, categories, and tags. See `ER_DIAGRAM.md` for the full schema.

### Vector Database

Stores document embeddings for semantic search and RAG retrieval.

- **Phase 5 onward:** FAISS (in-process, file-backed no extra infrastructure needed
  for a single-user system)
- **Migration trigger:** once per-user metadata filtering or 100k+ vectors are needed,
  migrate to **Qdrant**

### File Storage

Stores uploaded PDFs, images, videos, and research papers on local disk during early
phases, with a planned migration to S3-compatible storage once the system needs to run
outside a single machine.

## 4. AI Layer

The AI layer is organized as a set of independent services, each with a narrow
responsibility, so any one of them can be upgraded or replaced (e.g. swapping the
embedding model) without touching the rest of the system.

| Service | Responsibility |
|---|---|
| Document Processing | OCR, text extraction, chunking |
| Embedding Service | Generate and store vector embeddings |
| RAG Service | Retrieve relevant chunks, re-rank, generate an answer with citations |
| Quiz Service | Generate quiz questions from document chunks |
| Flashcard Service | Generate spaced-repetition flashcards from content |
| Recommendation Service | Suggest topics or content based on study history |
| Knowledge Graph Service | Detect relationships between concepts, build the graph |
| Analytics Service | Surface study insights and weak topics |

Each service is called by domain modules through a defined interface domain modules
never reach into AI internals directly (see `CODING_STANDARDS.md`, Section 2).

## 5. Folder Structure

```
ai-learning-os/
├── backend/
│   ├── main.py
│   ├── core/              # security, logging, exceptions, shared dependencies
│   ├── config/             # settings (env-driven)
│   ├── database/             # session management, base ORM class
│   ├── shared/                 # pagination, common schemas, utilities
│   ├── modules/                  # one folder per domain feature
│   │   ├── auth/
│   │   ├── notes/
│   │   ├── projects/
│   │   ├── tasks/
│   │   ├── study/
│   │   ├── flashcards/
│   │   ├── research/
│   │   ├── documents/
│   │   ├── search/
│   │   └── experiments/
│   │       # each module: router.py, service.py, repository.py,
│   │       # schemas.py, models.py, tests/
│   ├── ai/                          # independent AI services
│   │   ├── embeddings/
│   │   ├── rag/
│   │   ├── knowledge_graph/
│   │   ├── recommendation/
│   │   ├── analytics/
│   │   ├── quiz/
│   │   └── document_processing/
│   └── tests/                          # cross-module test suites
├── frontend/
├── docs/
├── docker/
└── scripts/
```

This is implemented as real directories under `backend/`, not just a planning diagram
— see the Phase 0 deliverable for the live scaffold.

## 6. Core Modules

Authentication, Notes, Projects, Research Papers, PDF Library, Flashcards, Quiz,
Knowledge Graph, AI Chat, Semantic Search, Learning Planner, Learning Analytics,
Experiment Tracker, Settings, Notifications.

## 7. Data Flow Pipelines

### AI Document Pipeline (Phase 4–6)

```
PDF Upload → Text Extraction → Cleaning → Chunking
   → Embedding → Vector Database → Retrieval → LLM → Answer
```

### Search Pipeline (Phase 5)

```
User Query → Keyword Search ─┐
            → Semantic Search ─┴→ Merge Results → Rank → Return
```

### Learning Pipeline (ongoing)

```
Study Session → Save Session → Generate Statistics
   → Update Weak Topics → Update Planner → Generate Recommendations
```

## 8. Finalized Technical Decisions

The following were left open in earlier planning and are now locked in. Full reasoning
for each is in `ARCHITECTURE_DECISIONS.md`.

| Decision Area | Choice |
|---|---|
| Module layout | Domain-modular (one folder per feature, not one global layer) |
| ORM mode | SQLAlchemy 2.0, async, via `asyncpg` |
| Background jobs | Celery + Redis |
| Vector DB (now) | FAISS |
| Vector DB (later) | Qdrant, once filtering/scale requires it |
| Embedding model | `all-MiniLM-L6-v2` (384-dim) |
| Authentication | JWT access + refresh tokens, multi-tenant-ready schema from day one |
| Migrations | Alembic, single linear history |

## 9. Future AI Modules (not yet built)

Recommendation Engine, Knowledge Graph, Research Assistant, AI Tutor, Experiment
Analysis, Learning Analytics, Voice Assistant, Offline Local LLM, Multimodal Search.

These are deliberately deferred: see `ER_DIAGRAM.md` for why their database schemas
aren't modeled yet.

## 10. Development Rules

- Every new feature must be independent, reusable, documented, tested, and modular.
- AI logic must never be tightly coupled to business logic: domain modules call AI
  services through a defined interface, never the reverse.
- Database queries must never appear inside API routes: always go through a service
  and repository.
- Always use service classes; never put business logic directly in route handlers.

Full enforceable rules (linting, layering, testing, definition of done) are in
`CODING_STANDARDS.md`.

## 11. Design Principles

SOLID · DRY · KISS · Separation of Concerns · Dependency Injection where appropriate ·
Clean Code · Domain-Driven Thinking

## 12. Long-Term Goal

The system should keep evolving for years without requiring a major rewrite. Every new
technology learned should become a new, independent module rather than forcing a
redesign of the existing architecture: this is the test every new feature should be
held to before being added.
