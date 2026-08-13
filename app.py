import pandas as pd
import streamlit as st

from db import add, con, init, search, seed, table
from vector_engine import DIM, embed


st.set_page_config(
    page_title="Vector DBMS",
    page_icon="🧠",
    layout="wide",
)

init()
seed()

st.title("🧠 Mini Vector Database")
st.caption(
    "DBMS mini project: SQLite database with vector storage and semantic search"
)

page = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Add Document",
        "Semantic Search",
        "Database Explorer",
    ],
)


if page == "Dashboard":
    st.header("Database Dashboard")

    connection = con()

    table_names = [
        "users",
        "documents",
        "document_vectors",
        "search_history",
    ]

    counts = {}

    for table_name in table_names:
        counts[table_name] = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

    connection.close()

    columns = st.columns(4)

    for column, (name, value) in zip(
        columns,
        counts.items(),
    ):
        column.metric(
            name.replace("_", " ").title(),
            value,
        )

    st.subheader("How the Vector Database Works")

    st.code(
        """
Document
    |
    v
Text converted into vector
    |
    v
Vector stored in document_vectors table
    |
    v
User enters search query
    |
    v
Query converted into vector
    |
    v
Cosine similarity calculated
    |
    v
Most similar documents displayed
        """.strip()
    )

    st.subheader("Stored Documents")

    documents = pd.DataFrame(
        table("documents")
    )

    st.dataframe(
        documents,
        use_container_width=True,
    )


elif page == "Add Document":
    st.header("Add Document")

    title = st.text_input(
        "Document Title"
    )

    text = st.text_area(
        "Document Content",
        height=150,
    )

    if st.button(
        "Save Document",
        type="primary",
    ):
        if title.strip() and text.strip():
            document_id = add(
                title.strip(),
                text.strip(),
            )

            vector_preview = embed(text)[:8]

            st.success(
                f"Document added successfully. Document ID: {document_id}"
            )

            st.write(
                "Vector dimension:",
                DIM,
            )

            st.write(
                "Vector preview:",
                vector_preview,
                "...",
            )
        else:
            st.error(
                "Please enter both title and content."
            )


elif page == "Semantic Search":
    st.header("Semantic Search")

    query = st.text_input(
        "Enter your search query",
        "How can technology help doctors?",
    )

    if st.button(
        "Search",
        type="primary",
    ):
        query_vector = embed(query)
        results = search(query)

        st.write(
            "Query vector preview:",
            query_vector[:8],
            "...",
        )

        st.write(
            f"Vector dimension: {DIM}"
        )

        if not results:
            st.warning(
                "No documents found."
            )
        else:
            for rank, result in enumerate(
                results,
                start=1,
            ):
                with st.container(
                    border=True
                ):
                    st.subheader(
                        f"#{rank} {result['title']}"
                    )

                    st.metric(
                        "Cosine Similarity",
                        f"{result['score']:.4f}",
                    )

                    st.write(
                        result["content"]
                    )

                    st.caption(
                        f"Document ID: {result['doc_id']} | "
                        f"Dimension: {result['dimension']} | "
                        f"Model: {result['model']}"
                    )

        st.latex(
            r"cosine(A,B)=\frac{A\cdot B}{||A||||B||}"
        )


elif page == "Database Explorer":
    st.header("Database Explorer")

    st.write(
        "The following sections show the actual SQLite tables used by the project."
    )

    for table_name in [
        "users",
        "documents",
        "document_vectors",
        "search_history",
    ]:
        with st.expander(
            f"Table: {table_name}",
            expanded=table_name == "documents",
        ):
            dataframe = pd.DataFrame(
                table(table_name)
            )

            st.dataframe(
                dataframe,
                use_container_width=True,
            )

    st.subheader("Database Schema")

    st.code(
        """
users
    user_id (Primary Key)
    username
    email

documents
    doc_id (Primary Key)
    user_id (Foreign Key)
    title
    content
    created_at

document_vectors
    vector_id (Primary Key)
    doc_id (Foreign Key)
    embedding
    dimension
    model_name

search_history
    search_id (Primary Key)
    query
    top_doc_id (Foreign Key)
    top_score
    searched_at
        """.strip()
    )

    st.subheader("Read-only SQL Console")

    sql = st.text_area(
        "Enter a SELECT query",
        "SELECT doc_id, title, content FROM documents;",
    )

    if st.button("Run SQL"):
        if sql.strip().lower().startswith("select"):
            try:
                connection = con()
                rows = connection.execute(sql).fetchall()
                dataframe = pd.DataFrame(
                    [dict(row) for row in rows]
                )
                connection.close()

                st.dataframe(
                    dataframe,
                    use_container_width=True,
                )

            except Exception as error:
                st.error(str(error))
        else:
            st.error(
                "Only SELECT queries are allowed."
            )
