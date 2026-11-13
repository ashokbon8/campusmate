-- CampusMate — PostgreSQL + pgvector schema
--
-- This is the production schema used by docker-compose. The FastAPI app also
-- creates these tables automatically on first start (SQLAlchemy metadata), so
-- this file documents the shape and can be applied directly if preferred:
--
--   psql "$DATABASE_URL" -f database/schema.sql
--
-- The application runs on SQLite with a JSON embedding fallback for zero-setup
-- local development; pgvector is used only against PostgreSQL.

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------------
-- Staff accounts (admin workspace)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    full_name       VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(32)  NOT NULL DEFAULT 'admin',  -- admin | publisher | viewer
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------------
-- Student accounts (public sign-up / sign-in)
-- Students create their own account before using the chatbot. Only the bcrypt
-- password hash is stored; the plain password is never persisted.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    full_name       VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    programme       VARCHAR(64),
    semester        VARCHAR(16),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_students_email ON students (email);

-- ---------------------------------------------------------------------------
-- Knowledge versions
-- A version is a snapshot of the approved knowledge base. Only one row has
-- is_active = TRUE at a time, so answers are always served from a single
-- consistent snapshot and cache invalidation is well defined.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_versions (
    id         SERIAL PRIMARY KEY,
    label      VARCHAR(64) NOT NULL UNIQUE,   -- e.g. kv-0001
    is_active  BOOLEAN     NOT NULL DEFAULT FALSE,
    notes      TEXT        NOT NULL DEFAULT '',
    created_at TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_knowledge_versions_active ON knowledge_versions (is_active);

-- ---------------------------------------------------------------------------
-- Documents (approved notices / FAQs)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id                    SERIAL PRIMARY KEY,
    doc_uid               VARCHAR(64) NOT NULL UNIQUE,
    title                 VARCHAR(255) NOT NULL,
    category              VARCHAR(64)  NOT NULL,   -- the five official categories
    doc_type              VARCHAR(32)  NOT NULL DEFAULT 'pdf',  -- pdf | faq

    programme             VARCHAR(64),
    academic_year         VARCHAR(32),
    semester              VARCHAR(16),
    subject               VARCHAR(128),
    publication_date      VARCHAR(32),
    effective_date        VARCHAR(32),
    expiry_date           VARCHAR(32),
    version               INTEGER      NOT NULL DEFAULT 1,
    source_page           INTEGER,

    status                VARCHAR(32)  NOT NULL DEFAULT 'draft', -- draft|published|replaced|retired
    replaces_document_id  INTEGER REFERENCES documents (id),
    retired_at            TIMESTAMP,

    stored_path           VARCHAR(512),
    content_hash          VARCHAR(64),

    knowledge_version_id  INTEGER REFERENCES knowledge_versions (id),
    uploaded_by_id        INTEGER REFERENCES admins (id),
    created_at            TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at          TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_documents_category ON documents (category);
CREATE INDEX IF NOT EXISTS ix_documents_status   ON documents (status);
CREATE INDEX IF NOT EXISTS ix_documents_programme ON documents (programme);
CREATE INDEX IF NOT EXISTS ix_documents_semester  ON documents (semester);
CREATE INDEX IF NOT EXISTS ix_documents_subject   ON documents (subject);
CREATE INDEX IF NOT EXISTS ix_documents_kv        ON documents (knowledge_version_id);

-- ---------------------------------------------------------------------------
-- Passages (extracted, sanitised, embedded chunks)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS passages (
    id          SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL DEFAULT 1,
    ordinal     INTEGER NOT NULL DEFAULT 0,
    content     TEXT    NOT NULL,
    embedding   vector(384)   -- must match EMBEDDING_DIM
);
CREATE INDEX IF NOT EXISTS ix_passages_document ON passages (document_id);
-- Approximate nearest-neighbour index for vector search.
CREATE INDEX IF NOT EXISTS ix_passages_embedding
    ON passages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ---------------------------------------------------------------------------
-- Helpdesk tickets
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
    id                  SERIAL PRIMARY KEY,
    reference           VARCHAR(32) NOT NULL UNIQUE,
    student_name        VARCHAR(255),
    contact             VARCHAR(255),
    category            VARCHAR(64) NOT NULL,
    programme           VARCHAR(64),
    semester            VARCHAR(16),
    subject             VARCHAR(128),
    description         TEXT NOT NULL,
    related_document_id INTEGER REFERENCES documents (id),
    status              VARCHAR(32) NOT NULL DEFAULT 'open', -- open|pending|in_progress|resolved|closed
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_tickets_status   ON tickets (status);
CREATE INDEX IF NOT EXISTS ix_tickets_category ON tickets (category);

CREATE TABLE IF NOT EXISTS ticket_messages (
    id          SERIAL PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    author      VARCHAR(32) NOT NULL,   -- student | staff
    body        TEXT NOT NULL,
    is_internal BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_ticket_messages_ticket ON ticket_messages (ticket_id);

-- ---------------------------------------------------------------------------
-- Chat logs (feeds the "unanswered question categories" admin metric)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_logs (
    id                SERIAL PRIMARY KEY,
    question          TEXT NOT NULL,
    category          VARCHAR(64),
    answer_state      VARCHAR(32) NOT NULL,   -- answered | needs_context | escalated
    knowledge_version VARCHAR(64),
    created_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_chat_logs_state    ON chat_logs (answer_state);
CREATE INDEX IF NOT EXISTS ix_chat_logs_category ON chat_logs (category);
