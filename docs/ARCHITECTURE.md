# AI Learning OS - System Architecture

# 1. Vision

AI Learning OS is a long-term personal platform that combines learning, research, note-taking, AI assistance, project management, and knowledge management into one intelligent system.

The architecture must be modular, scalable, maintainable, and easy to extend.

---

# 2. Architecture Style

The project follows **Clean Architecture** with a layered design.

```
                    Frontend (Next.js)

                            │

                    API Gateway (FastAPI)

                            │

                ---------------------------
                |                         |
         Authentication            Application APIs
                |                         |
                ---------------------------
                            │
                    Service Layer
                            │
        ----------------------------------------
        |          |          |                |
    Notes      Projects    Learning       AI Services
                              |
                    Repository Layer
                            │
          PostgreSQL      Vector DB     File Storage
                            │
                    External AI Services
```

---

# 3. Major Components

## Frontend

Responsibilities

* User Interface
* Dashboard
* Rich Text Editor
* Project Management
* Charts
* Knowledge Graph
* AI Chat
* Settings

Technology

* Next.js
* React
* Tailwind CSS
* TanStack Query
* React Flow
* Chart.js

---

## Backend

Responsibilities

* REST APIs
* Authentication
* Authorization
* Business Logic
* Validation
* Background Tasks

Technology

* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* JWT
* Redis

---

## Database

Primary Database

PostgreSQL

Stores

* Users
* Notes
* Projects
* Tasks
* Flashcards
* Analytics
* Study Sessions
* Categories
* Tags

---

## Vector Database

Initially

FAISS

Later

* Qdrant
* Weaviate

Stores

* Embeddings
* Semantic Search Index
* Document Chunks

---

## File Storage

Stores

* PDFs
* Images
* Videos
* Attachments
* Research Papers

Future

S3 Compatible Storage

---

# 4. AI Layer

Contains independent AI modules.

Examples

Document Service

* OCR
* Parsing
* Chunking

Embedding Service

* Generate embeddings
* Store vectors

RAG Service

* Retrieve
* Re-rank
* Generate answer

Quiz Service

* Generate quizzes

Flashcard Service

* Generate flashcards

Recommendation Service

* Recommend topics

Knowledge Graph Service

* Detect relationships
* Build graph

Analytics Service

* Study insights
* Weak topics

Each service should work independently.

---

# 5. Folder Structure

```
ai-learning-os/

app/
frontend/

backend/

api/

core/

config/

database/

models/

schemas/

repositories/

services/

ai/

rag/

embeddings/

knowledge_graph/

recommendation/

analytics/

notes/

projects/

study/

research/

tasks/

flashcards/

experiments/

search/

documents/

storage/

tests/

docs/

docker/

scripts/

```

---

# 6. Core Modules

Authentication

Notes

Projects

Research Papers

PDF Library

Flashcards

Quiz

Knowledge Graph

AI Chat

Semantic Search

Learning Planner

Learning Analytics

Experiment Tracker

Settings

Notifications

---

# 7. Database Modules

User

↓

Study Session

↓

Project

↓

Task

↓

Note

↓

Document

↓

Embedding

↓

Flashcard

↓

Quiz

↓

Analytics

Each module should be loosely coupled.

---

# 8. AI Pipeline

PDF Upload

↓

Text Extraction

↓

Cleaning

↓

Chunking

↓

Embedding

↓

Vector Database

↓

Retrieval

↓

LLM

↓

Answer

---

# 9. Search Pipeline

User Query

↓

Keyword Search

↓

Semantic Search

↓

Merge Results

↓

Rank

↓

Return

---

# 10. Learning Pipeline

Study

↓

Save Session

↓

Generate Statistics

↓

Update Weak Topics

↓

Update Planner

↓

Generate Recommendations

---

# 11. Future AI Modules

Recommendation Engine

Knowledge Graph

Research Assistant

AI Tutor

Experiment Analysis

Learning Analytics

Voice Assistant

Offline Local LLM

Multimodal Search

---

# 12. Development Rules

Every new feature should be:

* Independent
* Reusable
* Documented
* Tested
* Modular

Never tightly couple AI logic with business logic.

Never place database queries inside API routes.

Always use service classes.

---

# 13. Design Principles

* SOLID
* DRY
* KISS
* Separation of Concerns
* Dependency Injection where appropriate
* Clean Code
* Domain Driven Thinking

---

# 14. Long-Term Goal

The project should continue evolving for years.

Every technology learned should become a new module rather than requiring major architectural changes.
