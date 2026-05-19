from database import conn, cursor
from rag_pipeline import vectordb

def save_memory(title, content):

    # Save into SQLite
    cursor.execute(
        """
        INSERT INTO memories(title, content)
        VALUES (?, ?)
        """,
        (title, content)
    )

    conn.commit()

    # Save into Vector DB
    vectordb.add_texts(
        texts=[content],
        metadatas=[{"title": title}]
    )