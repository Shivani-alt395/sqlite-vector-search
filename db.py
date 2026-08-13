import json
import sqlite3
from pathlib import Path

from vector_engine import DIM, cosine, embed


DB = Path(__file__).parent / "data" / "vector_dbms.sqlite"


def con():
    DB.parent.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init():
    connection = con()
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS document_vectors (
            vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER UNIQUE NOT NULL,
            embedding TEXT NOT NULL,
            dimension INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
        );

        CREATE TABLE IF NOT EXISTS search_history (
            search_id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            top_doc_id INTEGER,
            top_score REAL,
            searched_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (top_doc_id) REFERENCES documents(doc_id)
        );

        CREATE INDEX IF NOT EXISTS idx_doc_user
        ON documents(user_id);

        CREATE INDEX IF NOT EXISTS idx_doc_title
        ON documents(title);
        """
    )

    connection.commit()
    connection.close()


def seed(reset=False):
    if reset and DB.exists():
        DB.unlink()

    init()

    connection = con()
    cursor = connection.cursor()

    document_count = cursor.execute(
        "SELECT COUNT(*) FROM documents"
    ).fetchone()[0]

    if document_count > 0:
        connection.close()
        return

    cursor.execute(
        """
        INSERT INTO users(username, email)
        VALUES (?, ?)
        """,
        ("demo", "demo@example.com"),
    )

    user_id = cursor.lastrowid

    data = [
        (
            "AI in Healthcare",
            "Artificial intelligence helps doctors detect diseases and improve medical diagnosis.",
        ),
        (
            "Online Education",
            "Online learning lets students study remotely using digital courses and virtual classrooms.",
        ),
        (
            "Cybersecurity",
            "Security systems protect computers from hackers, malware, phishing attacks and data breaches.",
        ),
        (
            "Climate Change",
            "Global warming causes rising temperatures, extreme weather and environmental damage.",
        ),
        (
            "Banking Fraud Detection",
            "Algorithms detect suspicious bank transactions and reduce financial fraud risk.",
        ),
        (
            "DBMS Indexing",
            "Database indexes improve SQL query performance by making row lookup faster.",
        ),
    ]

    for title, text in data:
        cursor.execute(
            """
            INSERT INTO documents(user_id, title, content)
            VALUES (?, ?, ?)
            """,
            (user_id, title, text),
        )

        document_id = cursor.lastrowid
        vector = embed(text)

        cursor.execute(
            """
            INSERT INTO document_vectors(
                doc_id,
                embedding,
                dimension,
                model_name
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                document_id,
                json.dumps(vector),
                DIM,
                "local-hash-vector-v1",
            ),
        )

    connection.commit()
    connection.close()


def add(
    title,
    text,
    username="student",
    email="student@example.com",
):
    init()

    connection = con()
    cursor = connection.cursor()

    user = cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if user:
        user_id = user["user_id"]
    else:
        cursor.execute(
            """
            INSERT INTO users(username, email)
            VALUES (?, ?)
            """,
            (username, email),
        )

        user_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO documents(user_id, title, content)
        VALUES (?, ?, ?)
        """,
        (user_id, title, text),
    )

    document_id = cursor.lastrowid
    vector = embed(text)

    cursor.execute(
        """
        INSERT INTO document_vectors(
            doc_id,
            embedding,
            dimension,
            model_name
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            document_id,
            json.dumps(vector),
            DIM,
            "local-hash-vector-v1",
        ),
    )

    connection.commit()
    connection.close()

    return document_id


def search(query, k=5):
    init()

    connection = con()
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT
            d.doc_id,
            d.title,
            d.content,
            v.embedding,
            v.dimension,
            v.model_name
        FROM documents AS d
        JOIN document_vectors AS v
            ON d.doc_id = v.doc_id
        """
    ).fetchall()

    query_vector = embed(query)
    results = []

    for row in rows:
        stored_vector = json.loads(row["embedding"])
        similarity = cosine(query_vector, stored_vector)

        results.append(
            {
                "doc_id": row["doc_id"],
                "title": row["title"],
                "content": row["content"],
                "score": similarity,
                "dimension": row["dimension"],
                "model": row["model_name"],
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    top_results = results[:k]

    top_doc_id = (
        top_results[0]["doc_id"]
        if top_results
        else None
    )

    top_score = (
        top_results[0]["score"]
        if top_results
        else None
    )

    cursor.execute(
        """
        INSERT INTO search_history(
            query,
            top_doc_id,
            top_score
        )
        VALUES (?, ?, ?)
        """,
        (query, top_doc_id, top_score),
    )

    connection.commit()
    connection.close()

    return top_results


def table(name):
    init()

    allowed_tables = {
        "users",
        "documents",
        "document_vectors",
        "search_history",
    }

    if name not in allowed_tables:
        raise ValueError("Invalid table name")

    connection = con()
    cursor = connection.cursor()

    query = f"SELECT * FROM {name} ORDER BY 1 DESC"
    rows = cursor.execute(query).fetchall()

    result = [dict(row) for row in rows]

    connection.close()

    for row in result:
        if "embedding" in row:
            row["embedding"] = row["embedding"][:100] + "..."

    return result
