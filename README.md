# Mini Vector Database - DBMS Project

A simple educational Vector Database implemented with Python, SQLite and Streamlit.

## Features

- SQLite relational database
- Users table
- Documents table
- Document vectors table
- Search history table
- Primary keys and foreign keys
- Database indexes
- Vector embedding generation
- Cosine similarity search
- Database Explorer
- Read-only SQL console
- Add new documents through the interface

## Technologies

- Python
- SQLite
- Streamlit
- Pandas

## Run on Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python seed_data.py
python -m streamlit run app.py
```

If PowerShell blocks virtual-environment activation:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Project Structure

- `app.py` - Streamlit user interface
- `db.py` - Database operations
- `vector_engine.py` - Vector generation and cosine similarity
- `seed_data.py` - Creates sample database data
- `schema.sql` - SQL database schema
- `requirements.txt` - Python dependencies

The project is intended for academic demonstration and uses a simple local vector-generation method rather than a production vector database engine.
