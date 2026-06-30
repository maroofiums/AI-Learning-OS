# Architecture Decision Record (ADR) — Phase 0

This document finalizes the technical decisions that ARCHITECTURE.md leaves open.
Each decision includes the reasoning so it can be revisited later without losing context.

---

## ADR-001: Module Organization — Domain-Modular, Not Layer-Global

**Decision:** Organize the backend by *domain module* (notes, projects, tasks, study,
flashcards, research, documents, search, experiments, auth), where each module owns its
own `router.py`, `service.py`, `repository.py`, `schemas.py`, `models.py`. Shared
infrastructure (`core/`, `config/`, `database/`, `shared/`) sits at the top level.

**Why:** The original folder sketch in ARCHITECTURE.md grouped files by technical layer
globally (one giant `api/`, one giant `services/`, etc.). That works for small projects
but becomes hard to navigate once you have 10+ modules — you end up jumping between five
top-level folders to understand one feature. Domain-modular structure means everything
about "flashcards" lives in one place. This is the standard pattern for FastAPI projects
that are expected to grow for years (your stated goal), and it maps directly onto Clean
Architecture: each module still has the same Presentation → Service → Repository →
Database layering internally.

**Trade-off accepted:** Slightly more boilerplate per module (5 files vs. dropping
everything in one place). Worth it for long-term navigability.

---

## ADR-002: Async SQLAlchemy from Day One

**Decision:** Use SQLAlchemy 2.0 in async mode (`AsyncSession`, `asyncpg` driver) from
Phase 1 onward, not sync SQLAlchemy migrated later.

**Why:** FastAPI is async-first. Phase 4 (Document Library) requires background
processing of large PDFs, and Phase 6 (RAG) involves I/O-bound calls to embedding models
and LLM APIs. Mixing sync DB calls into an async app blocks the event loop unless every
sync call is wrapped in `run_in_threadpool`. Starting async avoids a painful mid-project
migration once you have 8 modules depending on the session pattern.

**Trade-off accepted:** Async SQLAlchemy has a steeper learning curve and async test
fixtures are more fiddly (`pytest-asyncio`). Acceptable since this is a learning project
and async backend skills are part of your stated goals.

---

## ADR-003: Background Jobs — Celery + Redis

**Decision:** Use Celery with Redis as the broker/result backend for background tasks
(PDF OCR, embedding generation, flashcard generation).

**Why:** FastAPI's built-in `BackgroundTasks` runs in-process and dies if the server
restarts mid-job — unacceptable for a multi-minute OCR job on a large PDF. Celery gives
you retries, task status tracking, and scheduled jobs (useful later for spaced-repetition
review reminders in Phase 8 and the AI Planner in Phase 12). Redis is already in your
stack for caching, so it doesn't add a new dependency.

**Alternative considered:** ARQ (async-native, lighter weight). Celery was chosen instead
because its tooling/observability (Flower, retries, chaining) is more mature and better
documented for a solo learner debugging issues without a team.

---

## ADR-004: Vector Database — FAISS for Phase 5, Qdrant Migration in Phase 9+

**Decision:** Start with FAISS (in-process, file-backed) for Phase 5 semantic search.
Plan a migration to Qdrant once per-user metadata filtering becomes necessary
(Knowledge Graph phase or multi-user scenario).

**Why:** FAISS has no native metadata filtering or persistence server — every query
searches the whole index unless you pre-filter manually. That's fine for a single-user
system with a few thousand documents in Phase 5. Qdrant adds operational overhead
(separate service, Docker container) that isn't justified until your vector count or
filtering needs grow. This matches the roadmap's own phasing.

**Concrete trigger for migration:** When you need to filter search results by
project/category at the same time as similarity search, or exceed roughly 100k vectors.

---

## ADR-005: Embedding Model — `sentence-transformers/all-MiniLM-L6-v2` (384-dim)

**Decision:** Use `all-MiniLM-L6-v2` as the default embedding model for Phase 5.

**Why:** It's small enough to run locally on CPU (no GPU dependency, no API cost), has
a well-understood 384-dimension output (fixes your `embeddings.vector` column width
now), and is the standard teaching example for sentence-transformers — useful since
you're learning the underlying theory, not just calling an API. The embedding service is
designed as a swappable module (ADR-001), so upgrading to a larger model (e.g.
`bge-base-en`, 768-dim) later only requires a migration, not an architecture change.

**Schema implication:** `embeddings.vector` is defined as `VECTOR(384)` in the ER
diagram. If you change models later, dimension changes require a migration + re-embed,
documented as a known cost.

---

## ADR-006: Authentication — JWT with Refresh Tokens, Single-User-First

**Decision:** Build standard JWT access/refresh token auth in Phase 1, but design the
`users` table and all foreign keys as if multi-user is possible later, even though you
are the only real user for now.

**Why:** Retrofitting `user_id` foreign keys onto every table after the fact is exactly
the kind of "major schema redesign" your roadmap explicitly wants to avoid. Designing
for multi-tenancy now (every domain table has a `user_id` FK) costs almost nothing today
and avoids a rewrite if you ever add collaborators, share the platform, or open-source it.

---

## ADR-007: Migrations — Alembic, One Linear History

**Decision:** Use Alembic with autogenerate for migrations, one linear revision history
(no branching) since this is a single-developer project.

**Why:** Standard with SQLAlchemy, already listed in your stack. Linear history keeps
things simple — branching migrations only matter with multiple parallel feature branches
merging concurrently, which doesn't apply here.

---

## Summary Table

| Decision Area      | Choice                              |
|---------------------|--------------------------------------|
| Module layout        | Domain-modular (per-feature folders) |
| ORM mode              | SQLAlchemy 2.0 async + asyncpg      |
| Background jobs       | Celery + Redis                      |
| Vector DB (Phase 5)   | FAISS                               |
| Vector DB (Phase 9+)  | Qdrant (migration trigger defined)  |
| Embedding model        | all-MiniLM-L6-v2 (384-dim)         |
| Auth                    | JWT access + refresh, multi-tenant-ready schema |
| Migrations               | Alembic, linear history            |
