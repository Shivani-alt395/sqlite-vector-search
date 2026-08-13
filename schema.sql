CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE documents (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE document_vectors (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER UNIQUE NOT NULL,
    embedding TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
);

CREATE TABLE search_history (
    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    top_doc_id INTEGER,
    top_score REAL,
    searched_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (top_doc_id) REFERENCES documents(doc_id)
);

CREATE INDEX idx_doc_user
ON documents(user_id);

CREATE INDEX idx_doc_title
ON documents(title);
