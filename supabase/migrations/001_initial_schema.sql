-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents (one row per source PDF)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    source_file TEXT NOT NULL UNIQUE,
    topic TEXT,
    summary TEXT,
    key_findings JSONB DEFAULT '[]'::jsonb,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);

-- Document chunks with embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);

-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops);

-- Deliberation sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_slug TEXT NOT NULL,
    scenario_title TEXT NOT NULL,
    stage TEXT NOT NULL DEFAULT 'intro',
    recommendation_status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    action TEXT,
    evidence_used JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);

-- Deduplicated evidence citations per session
CREATE TABLE IF NOT EXISTS session_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    chunk_id UUID REFERENCES document_chunks(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    summary TEXT,
    excerpt TEXT NOT NULL,
    source_file TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, chunk_id)
);

CREATE INDEX IF NOT EXISTS idx_session_evidence_session_id ON session_evidence(session_id);

-- Final recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    recommendation TEXT NOT NULL,
    supporting_arguments JSONB DEFAULT '[]'::jsonb,
    tradeoffs JSONB DEFAULT '[]'::jsonb,
    uncertainties JSONB DEFAULT '[]'::jsonb,
    evidence_cited JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Semantic search RPC
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    filter_category TEXT DEFAULT NULL
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    content TEXT,
    title TEXT,
    summary TEXT,
    source_file TEXT,
    category TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id AS chunk_id,
        dc.document_id,
        dc.content,
        d.title,
        d.summary,
        d.source_file,
        d.category,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    JOIN documents d ON d.id = dc.document_id
    WHERE dc.embedding IS NOT NULL
      AND (filter_category IS NULL OR d.category = filter_category)
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
